"""Parse Sessionize GridSmart HTML into Session models.

Sessionize renders conference agendas as CSS grid HTML with structured data
attributes. This parser extracts sessions from the server-rendered HTML
returned by the ``?under=True`` API parameter.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta

from bs4 import BeautifulSoup

from conference_mcp.models import Session

# Timezone for ContainerDays Hamburg: CEST (UTC+2)
_EVENT_TZ = timezone(timedelta(hours=2))

# Day name mapping from month-day
_DAY_NAMES = {
    2: "wednesday",
    3: "thursday",
    4: "friday",
}

# Tab ID to date mapping
_TAB_DATES: dict[str, str] = {}


def _parse_sztz(sztz: str) -> tuple[datetime, datetime] | None:
    """Parse Sessionize data-sztz time attribute.

    Format: ``TimeWithDuration|en-US|2026-09-02T07:45:00.0000000Z|2026-09-02T08:20:00.0000000Z``

    Returns (start_utc, end_utc) or None on parse failure.
    """
    parts = sztz.split("|")
    if len(parts) < 4:
        return None
    try:
        start = datetime.fromisoformat(parts[2].replace("Z", "+00:00"))
        end = datetime.fromisoformat(parts[3].replace("Z", "+00:00"))
        return start, end
    except (ValueError, IndexError):
        return None


def _build_tab_map(soup: BeautifulSoup) -> None:
    """Build mapping of tab container IDs to ISO dates."""
    for tab in soup.select(".sz-tabs__item"):
        link = tab.select_one("a")
        if not link:
            continue
        tab_id = link.get("href", "").replace("#sz-tab-", "")
        sztz = link.get("data-sztz", "")
        parts = sztz.split("|")
        if len(parts) >= 3:
            try:
                dt = datetime.fromisoformat(parts[2].replace("Z", "+00:00"))
                _TAB_DATES[tab_id] = dt.strftime("%Y-%m-%d")
            except ValueError:
                pass


def parse_sessionize_html(html: str) -> list[Session]:
    """Parse Sessionize GridSmart HTML into Session objects.

    Args:
        html: Raw HTML from Sessionize's GridSmart view (with ``?under=True``).

    Returns:
        List of Session objects sorted by start time.
    """
    soup = BeautifulSoup(html, "html.parser")
    _build_tab_map(soup)

    sessions: list[Session] = []
    seen_ids: set[str] = set()

    for tab_container in soup.select('[id^="sz-tab-"]'):
        tab_id = tab_container.get("id", "").replace("sz-tab-", "")
        date_str = _TAB_DATES.get(tab_id, "")

        for el in tab_container.select(".sz-session"):
            session_id = el.get("data-sessionid", "")
            if not session_id or session_id in seen_ids:
                continue
            seen_ids.add(session_id)

            title_el = el.select_one(".sz-session__title a")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title or title == "-":
                continue

            time_el = el.select_one(".sz-session__time")
            room_el = el.select_one(".sz-session__room")

            sztz = time_el.get("data-sztz", "") if time_el else ""
            parsed = _parse_sztz(sztz)

            if parsed:
                start_utc, end_utc = parsed
                # Convert to event local time (CEST = UTC+2)
                start_local = start_utc.astimezone(_EVENT_TZ)
                end_local = end_utc.astimezone(_EVENT_TZ)
            else:
                continue

            day = start_local.strftime("%A").lower()
            start_iso = start_local.isoformat()
            end_iso = end_local.isoformat()
            room = room_el.get_text(strip=True) if room_el else ""

            # Extract speakers
            speakers: list[str] = []
            for sp in el.select(".sz-session__speakers li a"):
                name = sp.get_text(strip=True)
                if name:
                    speakers.append(name)

            # Extract tags (category + level)
            category = ""
            for tag in el.select(".sz-session__tags li.sz-tag"):
                tag_name = tag.get("data-categoryname", "")
                tag_text = tag.get_text(strip=True)
                if tag_name == "track":
                    category = tag_text
                # level tag can be appended to category or used separately

            # Build URL
            url = f"https://sessionize.com/s/{session_id}"

            session = Session(
                uid=session_id,
                title=title,
                start=start_iso,
                end=end_iso,
                day=day,
                location=room,
                description="",
                category=category,
                url=url,
                speakers=speakers,
            )
            sessions.append(session)

    sessions.sort(key=lambda s: s.start)
    return sessions
