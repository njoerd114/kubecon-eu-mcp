"""Data service: live upstream fetch -> in-memory cache -> static fallback.

This module owns all data access. The MCP server tools call methods here
instead of touching parsers or static data directly.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

import httpx

from kubecon_eu_mcp.ical_parser import parse_ical
from kubecon_eu_mcp.models import Session, Party, Hotel, VenueInfo, ColocatedEvent
from kubecon_eu_mcp.party_parser import parse_parties_html
from kubecon_eu_mcp.static_data import (
    VENUE,
    HOTELS,
    COLOCATED_EVENTS,
    SCHEDULE_OVERVIEW,
    AIRLINE_DISCOUNTS,
)

logger = logging.getLogger(__name__)

# Upstream URLs
SCHEDULE_ICAL_URL = "https://kccnceu2026.sched.com/all.ics"
COLOCATED_ICAL_URL = "https://colocatedeventseu2026.sched.com/all.ics"
PARTIES_URL = "https://conferenceparties.com/kubeconeu26/"

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
        """Data exists but is expired."""
        return self._data is not None and not self.valid

    def get(self) -> Any:
        return self._data

    def set(self, data: Any) -> None:
        self._data = data
        self._fetched_at = time.time()


class DataService:
    """Central data service with upstream fetching, caching, and fallback."""

    def __init__(self) -> None:
        self._sessions_cache = _Cache(SCHEDULE_TTL)
        self._colocated_sessions_cache = _Cache(SCHEDULE_TTL)
        self._parties_cache = _Cache(PARTIES_TTL)

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    async def get_sessions(self, force_refresh: bool = False) -> list[Session]:
        """Get all conference sessions (Tue-Thu).

        Priority: live iCal feed -> cached data -> empty list.
        """
        if self._sessions_cache.valid and not force_refresh:
            return self._sessions_cache.get()

        try:
            sessions = await self._fetch_sessions(SCHEDULE_ICAL_URL)
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
        """Get Monday co-located event sessions."""
        if self._colocated_sessions_cache.valid and not force_refresh:
            return self._colocated_sessions_cache.get()

        try:
            sessions = await self._fetch_sessions(COLOCATED_ICAL_URL)
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
        if day:
            all_sessions = sessions + (
                await self.get_colocated_sessions() if day == "monday" else []
            )
        else:
            all_sessions = sessions + await self.get_colocated_sessions()

        query_lower = query.lower()
        results = []

        for s in all_sessions:
            if day and s.day != day.lower():
                continue
            if track and track.lower() not in s.category.lower():
                continue

            # Search across title, description, speakers, category
            searchable = (
                f"{s.title} {s.description} {' '.join(s.speakers)} {s.category}".lower()
            )
            if query_lower in searchable:
                results.append(s)

        return results[:limit]

    async def get_schedule_for_day(self, day: str) -> list[Session]:
        """Get all sessions for a specific day."""
        if day.lower() == "monday":
            return await self.get_colocated_sessions()

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
                # Also check the title (speaker names often in title)
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
        """Get sessions suitable for scoring (filters out logistics events).

        Removes registration, breaks, badge pickup, cloakroom, lunch, and
        other non-session events — same logic as kubecon-event-scorer's
        filter_scorable().
        """
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
        }
        skip_categories = {"REGISTRATION", "BREAKS", "BREAK", "MEAL", "LUNCH"}

        if day and day.lower() == "monday":
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
        """Detect scheduling conflicts among selected sessions.

        Inspired by kubecon-event-scorer's conflicts_with() method.

        Args:
            session_uids: List of session UIDs to check for conflicts.

        Returns:
            List of conflict pairs with details.
        """
        all_sessions = await self.get_sessions()
        colocated = await self.get_colocated_sessions()
        session_map = {s.uid: s for s in all_sessions + colocated}

        selected = [session_map[uid] for uid in session_uids if uid in session_map]
        conflicts: list[dict] = []

        for i, a in enumerate(selected):
            for b in selected[i + 1 :]:
                if a.day != b.day:
                    continue
                # Parse ISO times and check overlap
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
    # Static data (venue, hotels, travel)
    # ------------------------------------------------------------------

    def get_venue(self) -> VenueInfo:
        return VENUE

    def get_hotels(self) -> list[Hotel]:
        return HOTELS

    def get_colocated_events(self) -> list[ColocatedEvent]:
        return COLOCATED_EVENTS

    def get_schedule_overview(self) -> dict:
        return SCHEDULE_OVERVIEW

    def get_airline_discounts(self) -> list[dict]:
        return AIRLINE_DISCOUNTS

    # ------------------------------------------------------------------
    # Internal fetch methods
    # ------------------------------------------------------------------

    async def _fetch_sessions(self, url: str) -> list[Session]:
        """Fetch and parse an iCal feed."""
        async with httpx.AsyncClient(
            timeout=_http_timeout, follow_redirects=True
        ) as client:
            resp = await client.get(url, headers={"User-Agent": "kubecon-eu-mcp/0.1"})
            resp.raise_for_status()
            return parse_ical(resp.text)

    async def _fetch_parties(self) -> list[Party]:
        """Fetch and parse party listings."""
        async with httpx.AsyncClient(
            timeout=_http_timeout, follow_redirects=True
        ) as client:
            resp = await client.get(
                PARTIES_URL, headers={"User-Agent": "kubecon-eu-mcp/0.1"}
            )
            resp.raise_for_status()
            return parse_parties_html(resp.text)


# Module-level singleton
data_service = DataService()
