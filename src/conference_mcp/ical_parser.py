"""Parse iCal feeds from sched.com into Session models."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from icalendar import Calendar

from conference_mcp.models import Session, day_from_date

# Pattern to extract speakers from session titles like:
# "Talk Title - Speaker Name, Company & Speaker2, Company2"
_SPEAKER_PATTERN = re.compile(r"^(.+?)\s+-\s+(.+)$")

# Categories/tracks to skip (non-session events)
_SKIP_CATEGORIES = {"badge pick-up", "cloakroom", "lunch", "coffee break", "break"}


def _extract_speakers(title: str) -> tuple[str, list[str]]:
    """Try to extract speaker names from a session title.

    Returns (clean_title, [speaker_names]).
    Many sched.com titles follow: "Session Title - Speaker, Org [& Speaker2, Org2]"
    """
    match = _SPEAKER_PATTERN.match(title)
    if not match:
        return title, []

    clean_title = match.group(1).strip()
    speaker_part = match.group(2).strip()

    raw_speakers = re.split(r"\s*[&;]\s*", speaker_part)

    speakers = []
    for s in raw_speakers:
        name = s.split(",")[0].strip()
        if name and len(name) > 1:
            speakers.append(name)

    return clean_title, speakers


def _to_iso(dt_val) -> str:
    """Convert an icalendar datetime to ISO 8601 string."""
    if dt_val is None:
        return ""
    dt = dt_val.dt if hasattr(dt_val, "dt") else dt_val
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    return dt.isoformat()


def _to_datetime(dt_val) -> datetime | None:
    """Convert an icalendar datetime to a Python datetime."""
    if dt_val is None:
        return None
    dt = dt_val.dt if hasattr(dt_val, "dt") else dt_val
    if isinstance(dt, datetime):
        return dt
    return datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)


def parse_ical(ical_text: str) -> list[Session]:
    """Parse an iCal string into a list of Session objects."""
    cal = Calendar.from_ical(ical_text)
    sessions: list[Session] = []

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        raw_title = str(component.get("SUMMARY", ""))
        description = str(component.get("DESCRIPTION", ""))
        location = str(component.get("LOCATION", ""))
        uid = str(component.get("UID", ""))
        url = str(component.get("URL", ""))

        categories_prop = component.get("CATEGORIES")
        if categories_prop:
            if hasattr(categories_prop, "to_ical"):
                category = (
                    str(categories_prop.to_ical(), "utf-8")
                    if isinstance(categories_prop.to_ical(), bytes)
                    else str(categories_prop.to_ical())
                )
            else:
                category = str(categories_prop)
        else:
            category = ""

        dtstart = component.get("DTSTART")
        dtend = component.get("DTEND")

        start_dt = _to_datetime(dtstart)
        if start_dt is None:
            continue

        clean_title, speakers = _extract_speakers(raw_title)

        session = Session(
            uid=uid,
            title=clean_title if speakers else raw_title,
            start=_to_iso(dtstart),
            end=_to_iso(dtend),
            day=day_from_date(start_dt),
            location=location,
            description=description[:2000],
            category=category,
            url=url,
            speakers=speakers,
        )
        sessions.append(session)

    sessions.sort(key=lambda s: s.start)
    return sessions
