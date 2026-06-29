"""Tests for the Conference MCP server tools, resources, and prompts.

Uses FastMCP's direct call_tool / read_resource / get_prompt methods with
monkeypatched data_service (see conftest.py) so no network calls are made.
"""

from __future__ import annotations

import json

import pytest


# =========================================================================
# Helpers
# =========================================================================


def _tool_text(result: tuple) -> str:
    content_blocks = result[0]
    assert len(content_blocks) >= 1
    return content_blocks[0].text


def _tool_json(result: tuple) -> dict | list:
    return json.loads(_tool_text(result))


# =========================================================================
# Tool registration
# =========================================================================


async def test_list_tools_count(mcp):
    tools = await mcp.list_tools()
    assert len(tools) == 12


async def test_list_tools_names(mcp):
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    expected = {
        "search_sessions",
        "get_schedule",
        "find_speaker",
        "find_parties",
        "plan_party_route",
        "get_venue_info",
        "get_hotel_info",
        "get_travel_info",
        "get_colocated_events",
        "get_conference_overview",
        "score_sessions",
        "detect_conflicts",
    }
    assert names == expected


# =========================================================================
# Tools — static data (no network)
# =========================================================================


async def test_get_venue_info(mcp):
    result = _tool_json(await mcp.call_tool("get_venue_info", {}))
    assert result["name"] == "RAI Amsterdam"
    assert "Europaplein" in result["address"]
    assert len(result["rooms"]) > 0
    assert "transit" in result
    assert "maps" in result


async def test_get_hotel_info(mcp):
    result = _tool_json(await mcp.call_tool("get_hotel_info", {}))
    assert isinstance(result, list)
    assert len(result) >= 1
    hotel = result[0]
    assert "name" in hotel
    assert "rate_from" in hotel
    assert "distance_to_venue" in hotel


async def test_get_travel_info(mcp):
    result = _tool_json(await mcp.call_tool("get_travel_info", {}))
    assert "airport" in result
    assert "Amsterdam" in str(result["airport"])
    assert "public_transport" in result
    assert "airline_discounts" in result
    assert len(result["airline_discounts"]) >= 1


async def test_get_colocated_events(mcp):
    result = _tool_json(await mcp.call_tool("get_colocated_events", {}))
    assert isinstance(result, list)
    assert len(result) >= 1
    names = [e["name"] for e in result]
    assert "Agentics Day: MCP + Agents" in names


async def test_get_conference_overview(mcp):
    result = _tool_json(await mcp.call_tool("get_conference_overview", {}))
    assert result["event"] == "KubeCon + CloudNativeCon Europe 2026"
    assert "schedule_at_a_glance" in result
    assert "useful_links" in result


# =========================================================================
# Tools — session search (uses mocked data_service)
# =========================================================================


async def test_search_sessions_by_keyword(mcp):
    result = _tool_json(await mcp.call_tool("search_sessions", {"query": "eBPF"}))
    assert isinstance(result, list)
    assert len(result) >= 1
    assert any("eBPF" in s["title"] for s in result)


async def test_search_sessions_by_day(mcp):
    result = _tool_json(
        await mcp.call_tool(
            "search_sessions", {"query": "Platform", "day": "wednesday"}
        )
    )
    assert isinstance(result, list)
    assert all(s["day"] == "wednesday" for s in result)


async def test_search_sessions_no_results(mcp):
    result = _tool_json(
        await mcp.call_tool("search_sessions", {"query": "nonexistent-xyz-topic"})
    )
    assert isinstance(result, dict)
    assert "message" in result


async def test_get_schedule_tuesday(mcp):
    result = _tool_json(await mcp.call_tool("get_schedule", {"day": "tuesday"}))
    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(s["day"] == "tuesday" for s in result)


async def test_get_schedule_monday_colocated(mcp):
    result = _tool_json(await mcp.call_tool("get_schedule", {"day": "monday"}))
    assert isinstance(result, list)
    assert len(result) >= 1
    assert any(s["day"] == "monday" for s in result)


async def test_find_speaker(mcp):
    result = _tool_json(await mcp.call_tool("find_speaker", {"name": "Liz Rice"}))
    assert isinstance(result, list)
    assert len(result) >= 1
    assert any("Liz Rice" in s["speakers"] for s in result)


async def test_find_speaker_partial(mcp):
    result = _tool_json(await mcp.call_tool("find_speaker", {"name": "Liz"}))
    assert isinstance(result, list)
    assert len(result) >= 1


async def test_find_speaker_not_found(mcp):
    result = _tool_json(await mcp.call_tool("find_speaker", {"name": "Nobody Here"}))
    assert isinstance(result, dict)
    assert "message" in result


# =========================================================================
# Tools — parties (uses mocked data_service)
# =========================================================================


async def test_find_parties_all(mcp):
    result = _tool_json(await mcp.call_tool("find_parties", {}))
    assert isinstance(result, list)
    assert len(result) == 2


async def test_find_parties_by_day(mcp):
    result = _tool_json(await mcp.call_tool("find_parties", {"day": "tuesday"}))
    assert isinstance(result, list)
    assert all(p["day"] == "tuesday" for p in result)


async def test_plan_party_route(mcp):
    result = _tool_json(await mcp.call_tool("plan_party_route", {"day": "tuesday"}))
    assert result["day"] == "tuesday"
    assert "parties" in result
    assert "tip" in result
    assert "key_venues" in result


async def test_plan_party_route_no_parties(mcp):
    result = _tool_json(await mcp.call_tool("plan_party_route", {"day": "thursday"}))
    assert "message" in result


# =========================================================================
# Tools — scoring & conflicts (uses mocked data_service)
# =========================================================================


async def test_score_sessions(mcp):
    result = _tool_json(
        await mcp.call_tool(
            "score_sessions",
            {"role": "SRE", "interests": "eBPF, observability"},
        )
    )
    assert "attendee_profile" in result
    assert result["attendee_profile"]["role"] == "SRE"
    assert "scoring_rubric" in result
    assert "sessions" in result
    titles = [s["title"] for s in result["sessions"]]
    assert "Lunch Break" not in titles


async def test_score_sessions_preferences(mcp):
    result = _tool_json(
        await mcp.call_tool(
            "score_sessions",
            {
                "role": "Developer",
                "interests": "AI",
                "prefer_hands_on": True,
                "avoid_vendor_pitches": True,
            },
        )
    )
    prefs = result["attendee_profile"]["preferences"]
    assert any("hands-on" in p for p in prefs)
    assert any("vendor" in p.lower() for p in prefs)


async def test_detect_conflicts_found(mcp):
    result = _tool_json(
        await mcp.call_tool(
            "detect_conflicts", {"session_uids": "sess-1,sess-overlap"}
        )
    )
    assert result["conflicts_found"] >= 1
    conflict = result["conflicts"][0]
    assert conflict["overlap_minutes"] > 0


async def test_detect_conflicts_none(mcp):
    result = _tool_json(
        await mcp.call_tool("detect_conflicts", {"session_uids": "sess-1,sess-3"})
    )
    assert result["conflicts_found"] == 0


async def test_detect_conflicts_too_few(mcp):
    result = _tool_json(
        await mcp.call_tool("detect_conflicts", {"session_uids": "sess-1"})
    )
    assert "message" in result


# =========================================================================
# Resources
# =========================================================================


async def test_list_resources_count(mcp):
    resources = await mcp.list_resources()
    assert len(resources) == 4


async def test_list_resources_uris(mcp):
    resources = await mcp.list_resources()
    uris = {str(r.uri) for r in resources}
    expected = {
        "conference://kubecon-eu-2026/overview",
        "conference://kubecon-eu-2026/venue",
        "conference://kubecon-eu-2026/hotels",
        "conference://kubecon-eu-2026/colocated-events",
    }
    assert uris == expected


async def test_resource_overview(mcp):
    contents = await mcp.read_resource("conference://kubecon-eu-2026/overview")
    data = json.loads(contents[0].content)
    assert data["event"] == "KubeCon + CloudNativeCon Europe 2026"


async def test_resource_venue(mcp):
    contents = await mcp.read_resource("conference://kubecon-eu-2026/venue")
    data = json.loads(contents[0].content)
    assert data["name"] == "RAI Amsterdam"


async def test_resource_hotels(mcp):
    contents = await mcp.read_resource("conference://kubecon-eu-2026/hotels")
    data = json.loads(contents[0].content)
    assert isinstance(data, list)
    assert len(data) >= 1


async def test_resource_colocated(mcp):
    contents = await mcp.read_resource("conference://kubecon-eu-2026/colocated-events")
    data = json.loads(contents[0].content)
    assert isinstance(data, list)
    assert any(e["name"] == "Agentics Day: MCP + Agents" for e in data)


# =========================================================================
# Prompts
# =========================================================================


async def test_list_prompts_count(mcp):
    prompts = await mcp.list_prompts()
    assert len(prompts) == 5


async def test_list_prompts_names(mcp):
    prompts = await mcp.list_prompts()
    names = {p.name for p in prompts}
    expected = {
        "plan_my_conference",
        "party_tonight",
        "first_timer_guide",
        "whats_happening_now",
        "create_profile",
    }
    assert names == expected


async def test_prompt_plan_my_conference(mcp):
    result = await mcp.get_prompt(
        "plan_my_conference",
        {"interests": "security, eBPF", "role": "SRE", "experience": "advanced"},
    )
    assert len(result.messages) >= 1
    text = result.messages[0].content.text
    assert "SRE" in text
    assert "security" in text
    assert "KubeCon" in text


async def test_prompt_party_tonight(mcp):
    result = await mcp.get_prompt(
        "party_tonight", {"day": "tuesday", "constraints": "near venue"}
    )
    assert len(result.messages) >= 1
    text = result.messages[0].content.text
    assert "tuesday" in text


async def test_prompt_first_timer_guide(mcp):
    result = await mcp.get_prompt("first_timer_guide", {})
    assert len(result.messages) >= 1
    text = result.messages[0].content.text
    assert "first-time" in text.lower() or "first timer" in text.lower()


async def test_prompt_whats_happening_now(mcp):
    result = await mcp.get_prompt(
        "whats_happening_now", {"current_time": "2:30 PM", "location": "Hall 7"}
    )
    assert len(result.messages) >= 1
    text = result.messages[0].content.text
    assert "2:30 PM" in text


async def test_prompt_create_profile(mcp):
    result = await mcp.get_prompt(
        "create_profile", {"background": "SRE at Acme Corp"}
    )
    assert len(result.messages) >= 1
    text = result.messages[0].content.text
    assert "SRE at Acme Corp" in text
