"""Shared fixtures for MCP server tests.

Provides mock session/party data and patches the data service so tools
never hit the network during tests.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from kubecon_eu_mcp.models import Session, Party


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_SESSIONS: list[Session] = [
    Session(
        uid="sess-1",
        title="Intro to eBPF on Kubernetes",
        start="2026-03-24T10:00:00+01:00",
        end="2026-03-24T10:35:00+01:00",
        day="tuesday",
        location="Hall 7 | Room A",
        description="Learn how eBPF enables powerful observability and networking.",
        category="Breakout",
        url="https://kccnceu2026.sched.com/event/ebpf-intro",
        speakers=["Liz Rice"],
    ),
    Session(
        uid="sess-2",
        title="Building AI Agents with MCP",
        start="2026-03-24T11:00:00+01:00",
        end="2026-03-24T11:35:00+01:00",
        day="tuesday",
        location="Hall 7 | Room B",
        description="How to build cloud-native AI agents using the Model Context Protocol.",
        category="Breakout",
        url="https://kccnceu2026.sched.com/event/mcp-agents",
        speakers=["David Aronchick"],
    ),
    Session(
        uid="sess-3",
        title="Platform Engineering Best Practices",
        start="2026-03-25T14:00:00+01:00",
        end="2026-03-25T14:35:00+01:00",
        day="wednesday",
        location="Hall 8 | Room D",
        description="Patterns for building a golden path for developers.",
        category="Breakout",
        url="https://kccnceu2026.sched.com/event/platform-eng",
        speakers=["Kaslin Fields"],
    ),
    Session(
        uid="sess-overlap",
        title="Service Mesh Deep Dive",
        start="2026-03-24T10:00:00+01:00",
        end="2026-03-24T10:35:00+01:00",
        day="tuesday",
        location="Hall 8 | Room E",
        description="Deep dive into service mesh internals.",
        category="Breakout",
        url="https://kccnceu2026.sched.com/event/mesh-deep",
        speakers=["Lin Sun"],
    ),
    Session(
        uid="sess-lunch",
        title="Lunch Break",
        start="2026-03-24T12:00:00+01:00",
        end="2026-03-24T13:00:00+01:00",
        day="tuesday",
        location="Halls 1-5",
        description="",
        category="LUNCH",
        url="",
        speakers=[],
    ),
]

MOCK_COLOCATED_SESSIONS: list[Session] = [
    Session(
        uid="colo-1",
        title="Agentics Day Opening Keynote",
        start="2026-03-23T13:00:00+01:00",
        end="2026-03-23T13:30:00+01:00",
        day="monday",
        location="Hall 7 | Room A",
        description="Welcome to Agentics Day.",
        category="Keynote",
        url="https://colocatedeventseu2026.sched.com/event/agentics-keynote",
        speakers=["Sam Altman"],
    ),
]

MOCK_PARTIES: list[Party] = [
    Party(
        name="Cloud Native Happy Hour",
        day="tuesday",
        date="March 24, 2026",
        time="6-9PM",
        sponsor="Isovalent",
        location="Strandzuid",
        address="Europaplein 22, Amsterdam",
        rsvp_url="https://example.com/rsvp/happy-hour",
    ),
    Party(
        name="Kubernetes Birthday Bash",
        day="wednesday",
        date="March 25, 2026",
        time="7PM-1AM",
        sponsor="CNCF",
        location="Heineken Experience",
        address="Stadhouderskade 78, Amsterdam",
        rsvp_url="https://example.com/rsvp/k8s-birthday",
    ),
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_data_service(monkeypatch):
    """Patch all data_service network methods so tests never hit the internet."""
    from kubecon_eu_mcp.data_service import data_service

    monkeypatch.setattr(
        data_service, "get_sessions", AsyncMock(return_value=MOCK_SESSIONS)
    )
    monkeypatch.setattr(
        data_service,
        "get_colocated_sessions",
        AsyncMock(return_value=MOCK_COLOCATED_SESSIONS),
    )
    monkeypatch.setattr(
        data_service, "get_parties", AsyncMock(return_value=MOCK_PARTIES)
    )
