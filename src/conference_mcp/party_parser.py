"""Parse party data from conferenceparties.com HTML."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from conference_mcp.models import Party

# Default day map for KubeCon-style conferenceparties.com
_DEFAULT_DAY_MAP = {
    "monday": ("monday", "March 23, 2026"),
    "tuesday": ("tuesday", "March 24, 2026"),
    "wednesday": ("wednesday", "March 25, 2026"),
    "thursday": ("thursday", "March 26, 2026"),
}


def _clean_text(text: str) -> str:
    """Clean up whitespace in scraped text."""
    return re.sub(r"\s+", " ", text).strip()


def _detect_day(text: str, day_map: dict | None = None) -> tuple[str, str] | None:
    """Detect which day a text refers to."""
    mapping = day_map or _DEFAULT_DAY_MAP
    lower = text.lower().strip()
    for key, (day, date) in mapping.items():
        if key in lower:
            return day, date
    return None


def parse_parties_html(
    html: str, day_map: dict | None = None
) -> list[Party]:
    """Parse party listings from conferenceparties.com HTML.

    The page uses a single table containing ALL days. Day headings appear as
    rows with a single cell (or cells with colspan). Data rows have 5 cells:
    Time | Sponsor | Event & RSVP Link | Location | Listed

    Args:
        html: Raw HTML from conferenceparties.com
        day_map: Optional day name → (day_key, date_str) mapping.

    Returns:
        List of Party objects.
    """
    mapping = day_map or _DEFAULT_DAY_MAP

    soup = BeautifulSoup(html, "html.parser")
    parties: list[Party] = []
    current_day = ""
    current_date = ""

    table = soup.find("table")
    if not table:
        return _parse_from_headings(soup, mapping)

    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        row_text = _clean_text(row.get_text())

        if len(cells) <= 2:
            detected = _detect_day(row_text, mapping)
            if detected:
                current_day, current_date = detected
            continue

        if len(cells) < 4:
            continue

        first_text = _clean_text(cells[0].get_text())
        if first_text.lower() in ("time", "") or not first_text:
            continue

        time_text = first_text
        sponsor = _clean_text(cells[1].get_text())
        event_cell = cells[2]
        location_cell = cells[3]

        link = event_cell.find("a")
        event_name = _clean_text(event_cell.get_text())
        rsvp_url = link["href"] if link and link.get("href") else ""

        location_text = _clean_text(location_cell.get_text())

        if not event_name or not time_text:
            continue

        party = Party(
            name=event_name,
            day=current_day,
            date=current_date,
            time=time_text,
            sponsor=sponsor,
            location=location_text,
            address=location_text,
            rsvp_url=rsvp_url,
        )
        parties.append(party)

    return parties


def _parse_from_headings(
    soup: BeautifulSoup, day_map: dict
) -> list[Party]:
    """Fallback parser using H2 headings and sibling elements."""
    parties: list[Party] = []
    current_day = ""
    current_date = ""

    for h2 in soup.find_all("h2"):
        detected = _detect_day(h2.get_text(), day_map)
        if not detected:
            continue
        current_day, current_date = detected

        sibling = h2.find_next_sibling()
        while sibling and sibling.name != "h2":
            text = sibling.get_text() if isinstance(sibling, Tag) else ""
            links = sibling.find_all("a") if isinstance(sibling, Tag) else []

            time_match = re.search(
                r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM)\s*[-\u2013]\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM))",
                text,
                re.IGNORECASE,
            )
            if time_match and links:
                link = links[0]
                party = Party(
                    name=_clean_text(link.get_text()),
                    day=current_day,
                    date=current_date,
                    time=time_match.group(1),
                    sponsor="",
                    location="",
                    address="",
                    rsvp_url=link.get("href", ""),
                )
                parties.append(party)

            sibling = sibling.find_next_sibling()

    return parties
