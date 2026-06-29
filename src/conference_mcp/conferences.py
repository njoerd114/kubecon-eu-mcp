"""Conference configuration registry.

Each conference is defined as a ConferenceConfig that drives all tools,
resources, prompts, and data fetching for that event.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from conference_mcp.models import ColocatedEvent, Hotel, VenueInfo

# ---------------------------------------------------------------------------
# Conference Config
# ---------------------------------------------------------------------------


@dataclass
class ConferenceConfig:
    """All configuration for a single conference."""

    key: str
    name: str
    short_name: str
    dates: str
    location: str
    timezone: str
    hashtags: list[str]

    # Data sources
    schedule_ical_url: str
    colocated_ical_url: str = ""
    parties_url: str = ""

    # Static data
    venue: VenueInfo = field(default_factory=lambda: VenueInfo.empty())
    hotels: list[Hotel] = field(default_factory=list)
    colocated_events: list[ColocatedEvent] = field(default_factory=list)
    schedule_overview: dict = field(default_factory=dict)
    airline_discounts: list[dict] = field(default_factory=list)

    # Day mapping: day keys used by the schedule (lowercase)
    day_names: list[str] = field(default_factory=list)

    # Messaging / party planning tips
    party_venue_tips: str = ""
    party_key_venues: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def _kubecon_eu_2026() -> ConferenceConfig:
    from conference_mcp.static_data import (
        KUBECON_VENUE,
        KUBECON_HOTELS,
        KUBECON_COLOCATED_EVENTS,
        KUBECON_SCHEDULE_OVERVIEW,
        KUBECON_AIRLINE_DISCOUNTS,
    )

    return ConferenceConfig(
        key="kubecon-eu-2026",
        name="KubeCon + CloudNativeCon Europe 2026",
        short_name="KubeCon EU 2026",
        dates="March 23-26, 2026",
        location="RAI Amsterdam, Netherlands",
        timezone="CET (Central European Time, UTC+1)",
        hashtags=["#KubeCon", "#CloudNativeCon"],
        schedule_ical_url="https://kccnceu2026.sched.com/all.ics",
        colocated_ical_url="https://colocatedeventseu2026.sched.com/all.ics",
        parties_url="https://conferenceparties.com/kubeconeu26/",
        venue=KUBECON_VENUE,
        hotels=KUBECON_HOTELS,
        colocated_events=KUBECON_COLOCATED_EVENTS,
        schedule_overview=KUBECON_SCHEDULE_OVERVIEW,
        airline_discounts=KUBECON_AIRLINE_DISCOUNTS,
        day_names=["monday", "tuesday", "wednesday", "thursday"],
        party_venue_tips=(
            "Most parties near RAI Amsterdam are in the Europaplein/Zuidas area "
            "(walking distance). Parties in central Amsterdam (Keizersgracht, Amstel) "
            "are 15-25 min by tram/metro from RAI. The last metro runs around 00:30."
        ),
        party_key_venues={
            "near_rai": "Strandzuid, Amstel Boathouse, nhow Hotel, Nela Restaurant — all within 10 min walk of RAI",
            "central": "Heineken Experience, Escape DeLux, Oche — 20-25 min by tram from RAI",
            "canal_area": "Elasticsearch office (Keizersgracht) — 25 min by tram",
        },
    )


def _containerdays_hamburg_2026() -> ConferenceConfig:
    from conference_mcp.static_data import (
        CDS_VENUE,
        CDS_HOTELS,
        CDS_WORKSHOPS,
        CDS_SCHEDULE_OVERVIEW,
    )

    return ConferenceConfig(
        key="containerdays-hamburg-2026",
        name="ContainerDays Hamburg 2026",
        short_name="ContainerDays Hamburg",
        dates="September 2-4, 2026",
        location="Hamburg, Germany",
        timezone="CEST (Central European Summer Time, UTC+2)",
        hashtags=["#ContainerDays", "#CDS2026", "#AIContext"],
        schedule_ical_url="https://sessionize.com/api/v2/mss5egyq/view/GridSmart?under=True",
        colocated_ical_url="",
        parties_url="",
        venue=CDS_VENUE,
        hotels=CDS_HOTELS,
        colocated_events=CDS_WORKSHOPS,
        schedule_overview=CDS_SCHEDULE_OVERVIEW,
        day_names=["wednesday", "thursday", "friday"],
        party_venue_tips=(
            "The evening event on Wednesday is held at the venue. "
            "Hamburg's Sternschanze and St. Pauli districts offer great bars "
            "and restaurants within 15 min by S-Bahn."
        ),
        party_key_venues={
            "venue": "MS Bleichen event ship — the main venue",
            "sternschanze": "Bars and restaurants in Sternschanze — 10-15 min by S-Bahn",
            "st_pauli": "St. Pauli / Reeperbahn area — 15-20 min by S-Bahn",
        },
    )


# Registry of all supported conferences (key → factory)
_REGISTRY: dict[str, ConferenceConfig] = {
    "kubecon-eu-2026": _kubecon_eu_2026(),
    "containerdays-hamburg-2026": _containerdays_hamburg_2026(),
}

_DEFAULT = "kubecon-eu-2026"


def get_conference(key: str | None = None) -> ConferenceConfig:
    """Get a conference config by key.

    Args:
        key: Conference key (e.g. "kubecon-eu-2026"). Defaults to KubeCon EU 2026.

    Returns:
        ConferenceConfig for the requested conference.

    Raises:
        ValueError: If the conference key is not found.
    """
    if key is None:
        key = _DEFAULT

    try:
        return _REGISTRY[key]
    except KeyError:
        available = ", ".join(sorted(_REGISTRY))
        raise ValueError(
            f"Unknown conference '{key}'. Available: {available}"
        ) from None


def list_conferences() -> list[str]:
    """Return sorted list of available conference keys."""
    return sorted(_REGISTRY)


def default_conference() -> str:
    """Return the default conference key."""
    return _DEFAULT
