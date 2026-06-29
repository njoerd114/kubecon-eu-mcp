"""Data service: live upstream fetch -> in-memory cache -> static fallback.

This module owns all data access. The MCP server tools call methods here
instead of touching parsers or static data directly.

All upstream URLs and static data are driven by the active ConferenceConfig.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

import httpx

from conference_mcp.conferences import ConferenceConfig
from conference_mcp.ical_parser import parse_ical
from conference_mcp.models import Session, Party
from conference_mcp.party_parser import parse_parties_html
from conference_mcp.sessionize_parser import parse_sessionize_html

logger = logging.getLogger(__name__)

# Cache TTLs (seconds)
SCHEDULE_TTL = 3600  # 1 hour
PARTIES_TTL = 7200  # 2 hours

_http_timeout = httpx.Timeout(15.0, connect=10.0)


class _Cache:
    """Simple TTL cache for a single value."""

    def __init__(self, ttl: int):
        self.ttl = ttl
        self._data: Any = None
        self._fetched_at: float = 0.0

    @property
    def valid(self) -> bool:
        return self._data is not None and (time.time() - self._fetched_at) < self.ttl

    @property
    def stale(self) -> bool:
        return self._data is not None and not self.valid

    def get(self) -> Any:
        return self._data

    def set(self, data: Any) -> None:
        self._data = data
        self._fetched_at = time.time()


class DataService:
    """Central data service with upstream fetching, caching, and fallback."""

    def __init__(self, config: ConferenceConfig) -> None:
        self._config = config
        self._sessions_cache = _Cache(SCHEDULE_TTL)
        self._colocated_sessions_cache = _Cache(SCHEDULE_TTL)
        self._parties_cache = _Cache(PARTIES_TTL)

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    async def get_sessions(self, force_refresh: bool = False) -> list[Session]:
        """Get all main conference sessions.

        Priority: live iCal feed -> cached data -> empty list.
        """
        if self._sessions_cache.valid and not force_refresh:
            return self._sessions_cache.get()

        url = self._config.schedule_ical_url
        if not url:
            return []

        try:
            sessions = await self._fetch_sessions(url)
            self._sessions_cache.set(sessions)
            logger.info("Fetched %d sessions from upstream", len(sessions))
            return sessions
        except Exception:
            logger.warning("Failed to fetch upstream schedule, using cache/fallback")
            if self._sessions_cache.stale:
                return self._sessions_cache.get()
            return []

    async def get_colocated_sessions(
        self, force_refresh: bool = False
    ) -> list[Session]:
        """Get co-located event / workshop day sessions."""
        if self._colocated_sessions_cache.valid and not force_refresh:
            return self._colocated_sessions_cache.get()

        url = self._config.colocated_ical_url
        if not url:
            return []

        try:
            sessions = await self._fetch_sessions(url)
            self._colocated_sessions_cache.set(sessions)
            logger.info("Fetched %d co-located sessions from upstream", len(sessions))
            return sessions
        except Exception:
            logger.warning("Failed to fetch co-located schedule")
            if self._colocated_sessions_cache.stale:
                return self._colocated_sessions_cache.get()
            return []

    async def search_sessions(
        self,
        query: str,
        day: str | None = None,
        track: str | None = None,
        limit: int = 20,
    ) -> list[Session]:
        """Search sessions by keyword, optionally filtered by day and track."""
        sessions = await self.get_sessions()
        colocated = await self.get_colocated_sessions()

        if day and day == self._config.day_names[0]:
            all_sessions = colocated + sessions
        elif day:
            all_sessions = sessions + colocated
        else:
            all_sessions = sessions + colocated

        query_lower = query.lower()
        results = []

        for s in all_sessions:
            if day and s.day != day.lower():
                continue
            if track and track.lower() not in s.category.lower():
                continue

            searchable = (
                f"{s.title} {s.description} {' '.join(s.speakers)} {s.category}".lower()
            )
            if query_lower in searchable:
                results.append(s)

        return results[:limit]

    async def get_schedule_for_day(self, day: str) -> list[Session]:
        """Get all sessions for a specific day."""
        if day.lower() == self._config.day_names[0]:
            colocated = await self.get_colocated_sessions()
            if colocated:
                return colocated

        sessions = await self.get_sessions()
        return [s for s in sessions if s.day == day.lower()]

    async def find_speakers(self, name: str, limit: int = 10) -> list[Session]:
        """Find sessions by speaker name."""
        all_sessions = await self.get_sessions()
        name_lower = name.lower()
        results = []

        for s in all_sessions:
            for speaker in s.speakers:
                if name_lower in speaker.lower():
                    results.append(s)
                    break
            else:
                if name_lower in s.title.lower():
                    results.append(s)

        return results[:limit]

    # ------------------------------------------------------------------
    # Parties
    # ------------------------------------------------------------------

    async def get_parties(self, force_refresh: bool = False) -> list[Party]:
        """Get all conference parties.

        Priority: live scrape -> cached data -> empty list.
        """
        if self._parties_cache.valid and not force_refresh:
            return self._parties_cache.get()

        url = self._config.parties_url
        if not url:
            return []

        try:
            parties = await self._fetch_parties()
            if parties:
                self._parties_cache.set(parties)
                logger.info("Fetched %d parties from upstream", len(parties))
                return parties
        except Exception:
            logger.warning("Failed to fetch upstream party data")

        if self._parties_cache.stale:
            return self._parties_cache.get()
        return []

    async def get_parties_for_day(self, day: str) -> list[Party]:
        """Get parties for a specific day."""
        parties = await self.get_parties()
        return [p for p in parties if p.day == day.lower()]

    # ------------------------------------------------------------------
    # Scoring support (inspired by kubecon-event-scorer)
    # ------------------------------------------------------------------

    async def get_scorable_sessions(
        self,
        day: str | None = None,
        limit: int = 50,
    ) -> list[Session]:
        """Get sessions suitable for scoring (filters out logistics events)."""
        skip_keywords = {
            "registration",
            "breakfast",
            "lunch",
            "coffee break",
            "badge pick",
            "networking break",
            "shuttle",
            "cloakroom",
            "break",
            "solutions showcase",
            "exhibition",
        }
        skip_categories = {"REGISTRATION", "BREAKS", "BREAK", "MEAL", "LUNCH"}

        if day and day.lower() == self._config.day_names[0]:
            sessions = await self.get_colocated_sessions()
        elif day:
            sessions = await self.get_schedule_for_day(day)
        else:
            sessions = await self.get_sessions()

        scorable = []
        for s in sessions:
            title_lower = s.title.lower().strip()
            cat_upper = s.category.upper()
            if cat_upper in skip_categories:
                continue
            if any(kw in title_lower for kw in skip_keywords):
                continue
            scorable.append(s)

        return scorable[:limit]

    async def detect_conflicts(self, session_uids: list[str]) -> list[dict]:
        """Detect scheduling conflicts among selected sessions."""
        all_sessions = await self.get_sessions()
        colocated = await self.get_colocated_sessions()
        session_map = {s.uid: s for s in all_sessions + colocated}

        selected = [session_map[uid] for uid in session_uids if uid in session_map]
        conflicts: list[dict] = []

        for i, a in enumerate(selected):
            for b in selected[i + 1 :]:
                if a.day != b.day:
                    continue
                try:
                    a_start = datetime.fromisoformat(a.start)
                    a_end = datetime.fromisoformat(a.end)
                    b_start = datetime.fromisoformat(b.start)
                    b_end = datetime.fromisoformat(b.end)
                except (ValueError, TypeError):
                    continue

                if a_start < b_end and b_start < a_end:
                    overlap_start = max(a_start, b_start)
                    overlap_end = min(a_end, b_end)
                    overlap_min = int(
                        (overlap_end - overlap_start).total_seconds() / 60
                    )
                    conflicts.append(
                        {
                            "session_a": {
                                "uid": a.uid,
                                "title": a.title,
                                "time": f"{a.start} - {a.end}",
                                "location": a.location,
                            },
                            "session_b": {
                                "uid": b.uid,
                                "title": b.title,
                                "time": f"{b.start} - {b.end}",
                                "location": b.location,
                            },
                            "overlap_minutes": overlap_min,
                        }
                    )

        return conflicts

    # ------------------------------------------------------------------
    # Static data accessors
    # ------------------------------------------------------------------

    @property
    def config(self) -> ConferenceConfig:
        return self._config

    # ------------------------------------------------------------------
    # Internal fetch methods
    # ------------------------------------------------------------------

    async def _fetch_sessions(self, url: str) -> list[Session]:
        async with httpx.AsyncClient(
            timeout=_http_timeout, follow_redirects=True
        ) as client:
            resp = await client.get(
                url, headers={"User-Agent": "conference-mcp/0.1"}
            )
            resp.raise_for_status()
            if "sessionize.com" in url:
                return parse_sessionize_html(resp.text)
            return parse_ical(resp.text)

    async def _fetch_parties(self) -> list[Party]:
        async with httpx.AsyncClient(
            timeout=_http_timeout, follow_redirects=True
        ) as client:
            resp = await client.get(
                self._config.parties_url,
                headers={"User-Agent": "conference-mcp/0.1"},
            )
            resp.raise_for_status()
            return parse_parties_html(resp.text)
