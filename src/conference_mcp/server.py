"""Conference MCP Server — parameterized for any conference.

Exposes tools, resources, and prompts for conference guidance via the
Model Context Protocol. All branding, data sources, and static data
are driven by the active ConferenceConfig.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from conference_mcp.conferences import ConferenceConfig
from conference_mcp.data_service import DataService


def _day_list(cfg: ConferenceConfig) -> str:
    """Human-readable day list (e.g. "monday, tuesday, wednesday, or thursday")."""
    *rest, last = cfg.day_names
    if rest:
        return f"{', '.join(rest)}, or {last}"
    return last


def _short_day(cfg: ConferenceConfig, day: str) -> str:
    """Get a short description for a day."""
    overview = cfg.schedule_overview.get("schedule_at_a_glance", {})
    return overview.get(day.lower(), "")


def create_server(config: ConferenceConfig) -> FastMCP:
    """Build a FastMCP server for a specific conference.

    Args:
        config: ConferenceConfig with all event-specific settings.

    Returns:
        A fully configured FastMCP server instance.
    """
    data_service = DataService(config)

    days = _day_list(config)
    key = config.key
    short_name = config.short_name

    mcp = FastMCP(
        f"{config.name} Guide",
        stateless_http=True,
        json_response=True,
        instructions=f"""
# {config.name} — Conference Guide

You are a helpful conference assistant for {config.name}, held {config.dates}
at {config.location}.

## Tool Selection Guide

- Use `search_sessions` to find talks by topic, speaker, or keyword.
- Use `get_schedule` to see the full schedule for a specific day.
- Use `find_speaker` to look up what a specific person is presenting.
- Use `find_parties` to discover social events and parties.
- Use `plan_party_route` to optimize an evening of party-hopping.
- Use `get_venue_info` to answer questions about the venue, rooms, or maps.
- Use `get_hotel_info` for hotel details and distances to venue.
- Use `get_travel_info` for transit, airport, and airline discount info.
- Use `get_colocated_events` for co-located events and workshops.
- Use `get_conference_overview` for a high-level event summary.
- Use `score_sessions` to get sessions with a scoring rubric for personalized ranking.
- Use `detect_conflicts` to check if selected sessions overlap in time.

## Important Context

- All times are in {config.timezone}.
- Acceptable day values: {days}.
- Session seating is first-come, first-served.
""",
    )

    # =====================================================================
    # Tools
    # =====================================================================

    @mcp.tool()
    async def search_sessions(
        query: str,
        day: str = "",
        track: str = "",
        limit: int = 20,
    ) -> str:
        """Search conference sessions by keyword, topic, speaker name, or technology.

        Args:
            query: Search query (e.g., "eBPF", "security", "AI agents", "platform engineering").
            day: Optional day filter ({days}).
            track: Optional track filter (e.g., "Keynote", "Tutorial", "Breakout").
            limit: Maximum number of results to return (default 20).

        Returns:
            JSON array of matching sessions with title, speakers, time, room, and URL.
        """  # noqa: E501
        results = await data_service.search_sessions(
            query=query,
            day=day or None,
            track=track or None,
            limit=limit,
        )
        if not results:
            return json.dumps(
                {
                    "message": f"No sessions found for '{query}'.",
                    "suggestion": "Try broader terms or remove day/track filters.",
                }
            )
        return json.dumps([s.to_dict() for s in results], indent=2)

    @mcp.tool()
    async def get_schedule(day: str) -> str:
        """Get the full conference schedule for a specific day.

        Args:
            day: Day name — {days}.

        Returns:
            JSON array of all sessions for that day, sorted by start time.
        """  # noqa: E501
        sessions = await data_service.get_schedule_for_day(day)
        if not sessions:
            return json.dumps(
                {
                    "message": f"No sessions found for {day}.",
                    "hint": f"Valid days: {days}",
                }
            )
        return json.dumps([s.to_dict() for s in sessions], indent=2)

    @mcp.tool()
    async def find_speaker(name: str) -> str:
        """Find sessions by a specific speaker.

        Args:
            name: Speaker name or partial name (e.g., "Lin Sun", "Bryce").

        Returns:
            JSON array of sessions featuring the speaker.
        """
        results = await data_service.find_speakers(name)
        if not results:
            return json.dumps(
                {
                    "message": f"No sessions found for speaker '{name}'.",
                    "suggestion": "Try a partial name or check spelling.",
                }
            )
        return json.dumps([s.to_dict() for s in results], indent=2)

    @mcp.tool()
    async def find_parties(day: str = "", after: str = "", before: str = "") -> str:
        """Find conference parties, happy hours, and social events.

        Args:
            day: Optional day filter ({days}).
            after: Optional time filter — only show events starting after this time (e.g., "6PM").
            before: Optional time filter — only show events starting before this time (e.g., "10PM").

        Returns:
            JSON array of parties with name, time, sponsor, location, and RSVP link.
        """  # noqa: E501
        if day:
            parties = await data_service.get_parties_for_day(day)
        else:
            parties = await data_service.get_parties()

        if not parties:
            return json.dumps(
                {"message": "No party data available. Check the conference website for social events."}
            )

        return json.dumps([p.to_dict() for p in parties], indent=2)

    @mcp.tool()
    async def plan_party_route(day: str, preferences: str = "") -> str:
        """Plan an optimized party-hopping route for an evening.

        Returns parties for the requested day sorted by time, with location details
        to help plan an efficient route.

        Args:
            day: Day name — {days}.
            preferences: Optional preferences like "networking", "food", "near venue", "open bar".

        Returns:
            JSON with sorted party timeline and location context for route planning.
        """  # noqa: E501
        parties = await data_service.get_parties_for_day(day)
        if not parties:
            return json.dumps({"message": f"No parties found for {day}."})

        route = {
            "day": day,
            "total_parties": len(parties),
            "tip": config.party_venue_tips,
            "parties": [p.to_dict() for p in parties],
            "key_venues": config.party_key_venues,
        }

        return json.dumps(route, indent=2)

    @mcp.tool()
    async def get_venue_info() -> str:
        """Get venue details: address, rooms, maps, and transit information.

        Returns:
            JSON with venue name, address, room list, map links, transit info, and parking.
        """
        venue = config.venue
        return json.dumps(venue.to_dict(), indent=2)

    @mcp.tool()
    async def get_hotel_info() -> str:
        """Get conference hotel block information with rates and distances.

        Returns:
            JSON array of hotels with name, address, rate, distance to venue, and availability.
        """
        return json.dumps([h.to_dict() for h in config.hotels], indent=2)

    @mcp.tool()
    async def get_travel_info() -> str:
        """Get travel information: airport, transit, parking, and airline discounts.

        Returns:
            JSON with airport details, public transport info, parking, and airline discount codes.
        """
        venue = config.venue
        return json.dumps(
            {
                "airport": venue.transit.get("from_airport", "See venue transit info"),
                "public_transport": venue.transit,
                "parking": venue.parking,
                "airline_discounts": config.airline_discounts,
            },
            indent=2,
        )

    @mcp.tool()
    async def get_colocated_events() -> str:
        """Get co-located events and workshops for this conference.

        Returns:
            JSON array of co-located events with name, duration, room, and requirements.
        """
        events = config.colocated_events
        return json.dumps([e.to_dict() for e in events], indent=2)

    @mcp.tool()
    async def get_conference_overview() -> str:
        """Get a high-level overview of the entire conference.

        Returns:
            JSON with event name, dates, schedule at a glance, and useful links.
        """
        return json.dumps(config.schedule_overview, indent=2)

    # =====================================================================
    # Scoring & Conflict Tools
    # =====================================================================

    @mcp.tool()
    async def score_sessions(
        role: str,
        interests: str,
        day: str = "",
        experience_level: str = "intermediate",
        priorities: str = "",
        prefer_hands_on: bool = False,
        prefer_deep_dives: bool = False,
        avoid_vendor_pitches: bool = False,
        limit: int = 30,
    ) -> str:
        """Get sessions ready for personalized scoring, with a scoring rubric.

        Returns scorable sessions (logistics events filtered out) along with a
        structured scoring rubric. You (the AI agent) should apply the rubric to
        rank sessions for the attendee.

        Args:
            role: Attendee's job title (e.g., "Platform Engineer", "SRE", "Developer").
            interests: Comma-separated interests (e.g., "eBPF, security, AI on Kubernetes").
            day: Optional day filter ({days}).
            experience_level: "beginner", "intermediate", "advanced", or "expert".
            priorities: Comma-separated goals (e.g., "evaluate service mesh tools, learn GitOps").
            prefer_hands_on: Boost hands-on workshops and labs.
            prefer_deep_dives: Boost deep technical talks over intros.
            avoid_vendor_pitches: Penalize vendor-heavy marketing sessions.
            limit: Max sessions to return (default 30).

        Returns:
            JSON with attendee profile, scoring rubric, and session list to score.
        """  # noqa: E501
        sessions = await data_service.get_scorable_sessions(
            day=day or None, limit=limit
        )
        if not sessions:
            return json.dumps({"message": "No scorable sessions found."})

        prefs = []
        if prefer_hands_on:
            prefs.append("Prefers hands-on workshops and demos")
        if prefer_deep_dives:
            prefs.append("Prefers deep technical dives over introductory content")
        if avoid_vendor_pitches:
            prefs.append("Penalize vendor-heavy marketing talks")

        result = {
            "attendee_profile": {
                "role": role,
                "interests": [i.strip() for i in interests.split(",")],
                "experience_level": experience_level,
                "priorities": [p.strip() for p in priorities.split(",") if p.strip()]
                if priorities
                else [],
                "preferences": prefs,
            },
            "scoring_rubric": {
                "description": "Score each session 0-100 across three dimensions.",
                "dimensions": {
                    "role_relevance": {
                        "max": 35,
                        "description": "How relevant is this session to the attendee's role?",
                        "scale": {
                            "30-35": "Directly addresses core job functions",
                            "20-29": "Strongly related to role",
                            "10-19": "Tangentially related",
                            "0-9": "Not relevant to role",
                        },
                    },
                    "topic_alignment": {
                        "max": 35,
                        "description": "How well does the topic match the attendee's interests?",
                        "scale": {
                            "30-35": "Directly matches primary interests",
                            "20-29": "Matches secondary interests",
                            "10-19": "Loosely related",
                            "0-9": "No alignment",
                        },
                    },
                    "strategic_value": {
                        "max": 30,
                        "description": "What unique strategic value does this session offer?",
                        "scale": {
                            "25-30": "Unique insights, actionable takeaways",
                            "15-24": "Good learning opportunity",
                            "5-14": "Standard content, available elsewhere",
                            "0-4": "Low strategic value",
                        },
                    },
                },
                "score_tiers": {
                    "85-100": "Must-attend",
                    "70-84": "Recommended",
                    "50-69": "Consider",
                    "30-49": "Low priority",
                    "0-29": "Skip",
                },
                "calibration": [
                    "A perfect 100 should be extremely rare (1-2 sessions max).",
                    "Aim for natural distribution: most sessions between 30-70.",
                    "Introductory talks should score lower for advanced/expert attendees.",
                    "Vendor-specific talks score lower unless the tool is directly relevant.",
                ],
            },
            "sessions": [s.to_dict() for s in sessions],
            "total_sessions": len(sessions),
            "attribution": "Scoring rubric from github.com/FredrikCarlssn/kubecon-event-scorer",
        }

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def detect_conflicts(session_uids: str) -> str:
        """Detect scheduling conflicts among selected sessions.

        Checks whether any of the provided sessions overlap in time, helping
        attendees resolve conflicts in their planned schedule.

        Args:
            session_uids: Comma-separated session UIDs to check for conflicts.

        Returns:
            JSON with conflict pairs, overlap duration, and session details.
        """
        uids = [uid.strip() for uid in session_uids.split(",") if uid.strip()]
        if len(uids) < 2:
            return json.dumps(
                {"message": "Need at least 2 session UIDs to check for conflicts."}
            )

        conflicts = await data_service.detect_conflicts(uids)

        return json.dumps(
            {
                "sessions_checked": len(uids),
                "conflicts_found": len(conflicts),
                "conflicts": conflicts,
                "tip": "Use `search_sessions` to find alternative sessions on the same topic."
                if conflicts
                else "No conflicts — your schedule is clear!",
            },
            indent=2,
        )

    # =====================================================================
    # Resources
    # =====================================================================

    @mcp.resource(f"conference://{key}/overview")
    async def resource_overview() -> str:
        """Full conference overview with dates, venue, and schedule at a glance."""
        return json.dumps(config.schedule_overview, indent=2)

    @mcp.resource(f"conference://{key}/venue")
    async def resource_venue() -> str:
        """Venue details including rooms, maps, and transit."""
        return json.dumps(config.venue.to_dict(), indent=2)

    @mcp.resource(f"conference://{key}/hotels")
    async def resource_hotels() -> str:
        """Conference hotel block information."""
        return json.dumps([h.to_dict() for h in config.hotels], indent=2)

    @mcp.resource(f"conference://{key}/colocated-events")
    async def resource_colocated() -> str:
        """Co-located events and workshops."""
        return json.dumps(
            [e.to_dict() for e in config.colocated_events], indent=2
        )

    # =====================================================================
    # Prompts
    # =====================================================================

    @mcp.prompt()
    async def plan_my_conference(
        interests: str,
        role: str = "developer",
        experience: str = "intermediate",
    ) -> str:
        """Build a personalized conference itinerary.

        Args:
            interests: Comma-separated topics (e.g., "security, platform engineering, eBPF").
            role: Your role (e.g., "developer", "SRE", "platform engineer", "architect").
            experience: Experience level — "beginner", "intermediate", or "advanced".
        """
        return f"""You are a {config.name} conference planning assistant.

The attendee has the following profile:
- **Role**: {role}
- **Interests**: {interests}
- **Experience level**: {experience}

Please create a personalized itinerary for {config.name} ({config.dates}, {config.location}).

Instructions:
1. Use `search_sessions` to find relevant sessions matching their interests.
2. Use `get_colocated_events` to check for co-located events or workshops.
3. Use `find_parties` to suggest evening social events for networking.
4. Flag any scheduling conflicts and suggest alternatives.
5. Include practical tips (arrive early for popular sessions, best rooms for networking, etc.).
6. Consider their experience level — skip 101 talks for advanced users, recommend tutorials for beginners.
7. Check `get_conference_overview` for the schedule at a glance.

Format the itinerary by day with time blocks."""

    @mcp.prompt()
    async def party_tonight(day: str, constraints: str = "") -> str:
        """Plan the perfect evening of conference parties.

        Args:
            day: Which evening — {days}.
            constraints: Optional constraints like "must be back by 11pm", "near venue", "with food".
        """  # noqa: E501
        return f"""You are a {config.name} party planning assistant.

The attendee wants to maximize their evening on **{day}**.
Constraints: {constraints if constraints else "None specified"}

Instructions:
1. Use `find_parties` with day="{day}" to get all parties for this evening.
2. Use `plan_party_route` with day="{day}" to get location context.
3. Create an optimized party-hopping route considering:
   - Party start/end times and overlaps
   - Walking/transit distances between venues
   - RSVP requirements (note which ones need advance registration)
   - Mix of networking and social events
4. Note transportation constraints (last metro/train times).
5. Recommend 3-4 parties as the optimal route with travel times between them."""

    @mcp.prompt()
    async def first_timer_guide() -> str:
        """Get a first-timer's guide to the conference."""
        return f"""You are a {config.name} guide for first-time attendees.

Create a comprehensive first-timer guide covering:

1. **Before You Go**:
   - Use `get_travel_info` for airport/transit info.
   - Use `get_hotel_info` for accommodation options.
   - Recommend building a personal schedule before arriving.

2. **Conference Overview**:
   - Use `get_conference_overview` for the schedule at a glance.
   - Explain the conference format and what to expect each day.

3. **At the Conference**:
   - Use `get_venue_info` for venue layout and room locations.
   - Tip: Sessions are first-come, first-served — arrive early for popular ones.
   - The hallway track (networking between sessions) is where magic happens.

4. **Evening Events**:
   - Use `find_parties` to show what social events are happening.
   - Many parties require advance RSVP — register early.
   - Recommend at least one party per evening for networking.

5. **Practical Tips**:
   - Wear comfortable shoes (lots of walking).
   - Bring a laptop charger.
   - Check `get_venue_info` for venue maps and transit.

Format as a friendly, actionable guide."""

    @mcp.prompt()
    async def whats_happening_now(current_time: str = "", location: str = "") -> str:
        """Find out what's happening right now or next at the conference.

        Args:
            current_time: Current time in the conference timezone ({config.timezone}).
            location: Optional — your current location at the venue.
        """  # noqa: E501
        return f"""You are a real-time {config.name} assistant.

The attendee is at the conference right now.
Current time ({config.timezone}): {current_time if current_time else "Ask the attendee"}
Current location: {location if location else "Unknown"}

Instructions:
1. Determine the current day and time.
2. Use `get_schedule` for today's schedule.
3. Find sessions that are:
   - Currently in progress (started before now, ending after now)
   - Starting within the next 30 minutes
   - Starting within the next 1-2 hours
4. If location is known, prioritize sessions in nearby rooms.
5. Also check `find_parties` if it's after 5 PM — evening events may be starting.
6. Suggest 2-3 options with room locations and brief descriptions.

Be concise — the attendee is on the move."""

    @mcp.prompt()
    async def create_profile(background: str = "") -> str:
        """Create a personalized attendee profile for session scoring.

        Generates a profile, then uses it to score and rank sessions.

        Args:
            background: Any background info (e.g., "I'm an SRE at Acme Corp, we run 50 clusters").
        """
        return f"""You are a {config.name} profile builder and session scorer.

The attendee provided this background: {background if background else "Not yet provided — ask them."}

## Step 1: Build the Profile

Ask the attendee (or infer from their background) about:
- **Role**: Job title (e.g., Platform Engineer, SRE, Developer Advocate)
- **Interests**: Primary topics (e.g., eBPF, service mesh, platform engineering)
  and secondary topics (e.g., observability, security)
- **Experience level**: beginner, intermediate, advanced, or expert
- **Priorities**: What they want to accomplish at this conference (e.g., evaluate GitOps tools)
- **Preferences**: Do they prefer hands-on workshops? Deep dives? Want to avoid vendor pitches?
- **Context**: Anything relevant about their work environment

## Step 2: Score Sessions

Once you have the profile, use `score_sessions` with the profile parameters to get
sessions and the scoring rubric. Then:

1. Score each session using the 3-dimension rubric (role_relevance, topic_alignment, strategic_value).
2. Sort by total score descending.
3. Present the top 15-20 sessions grouped by score tier:
   - **Must-attend (85+)**: These are your highest-priority sessions.
   - **Recommended (70-84)**: Strong matches worth attending.
   - **Consider (50-69)**: Good options if you have time.
4. Flag any conflicts among the top-scoring sessions.
5. Suggest a daily schedule based on the scored results.

## Step 3: Check for Conflicts

Use `detect_conflicts` with the UIDs of the top-scoring sessions to find overlaps.
For each conflict, suggest which session to prioritize based on scores."""

    return mcp
