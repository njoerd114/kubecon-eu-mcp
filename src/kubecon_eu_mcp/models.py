"""Data models for KubeCon EU schedule, parties, venue, and travel."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Session:
    """A conference session (talk, keynote, tutorial, break, etc.)."""

    uid: str
    title: str
    start: str  # ISO 8601
    end: str  # ISO 8601
    day: str  # e.g. "monday", "tuesday"
    location: str
    description: str
    category: str  # e.g. "Keynote", "Breakout", "Tutorial"
    url: str
    speakers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Party:
    """A conference party or social event."""

    name: str
    day: str  # e.g. "monday", "tuesday"
    date: str  # e.g. "March 23, 2026"
    time: str  # e.g. "6-9PM"
    sponsor: str
    location: str
    address: str
    rsvp_url: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Hotel:
    """A conference hotel block."""

    name: str
    address: str
    distance_to_venue: str
    rate_from: str
    rating: str
    url: str
    availability: str  # "Available" | "Sold Out" | "Room Block Closed"
    breakfast_included: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VenueInfo:
    """Conference venue details."""

    name: str
    address: str
    description: str
    rooms: list[str]
    transit: dict[str, str]
    parking: str
    maps: dict[str, str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ColocatedEvent:
    """A co-located event on Monday."""

    name: str
    duration: str  # "Half-Day" | "Full-Day"
    location: str
    requires: str  # "ALL ACCESS PASS" | "SEPARATE REGISTRATION"
    url: str
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def day_from_date(dt: datetime) -> str:
    """Convert a datetime to a day name key."""
    return dt.strftime("%A").lower()
