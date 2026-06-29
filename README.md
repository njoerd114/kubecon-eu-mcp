# conference-mcp

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License MIT](https://img.shields.io/badge/license-MIT-green.svg)

An MCP server for tech conferences — agentic schedule planner, party optimizer, and conference guide. Connect AI agents to live conference data for personalized itineraries, session scoring, and logistics.

## Supported Conferences

| Conference | Dates | Location | Flag |
|---|---|---|---|
| KubeCon + CloudNativeCon Europe 2026 | March 23-26, 2026 | RAI Amsterdam | `--conference kubecon-eu-2026` |
| ContainerDays Hamburg 2026 | September 2-4, 2026 | MS Bleichen, Hamburg | `--conference containerdays-hamburg-2026` |

Data sources include:
- Official Sched.com iCal feeds (KubeCon)
- Sessionize.com grid views (ContainerDays)
- ConferenceParties.com (KubeCon)
- Conference websites

## Features

- **Smart Scheduling**: Search talks by topic, speaker, or technology.
- **Party Optimizer**: Find evening social events and plan routes.
- **Logistics Guide**: Venue details, hotel blocks, transit, and maps.
- **Agentic Planning**: Built-in prompts for itineraries and first-timer guides.
- **Session Scoring**: Personalized ranking using a 3-dimension rubric.
- **Conflict Detection**: Check selected sessions for time overlaps.
- **Multi-Conference**: One server, multiple events — switch via `--conference`.

## Quick Start

### Zero Install (uvx)
```bash
uvx conference-mcp --conference kubecon-eu-2026
uvx conference-mcp --conference containerdays-hamburg-2026
```

### Standard Install (pip)
```bash
pip install .
conference-mcp --conference kubecon-eu-2026
```

### Docker
```bash
docker build -t conference-mcp .
docker run -it conference-mcp

# For ContainerDays:
docker run -e CONFERENCE_MCP_EVENT=containerdays-hamburg-2026 -it conference-mcp
```

## Configuration

### Claude Desktop
```json
{
  "mcpServers": {
    "conference-mcp": {
      "command": "uvx",
      "args": ["conference-mcp", "--conference", "kubecon-eu-2026"]
    }
  }
}
```

### Environment Variable
Set `CONFERENCE_MCP_EVENT` to select the default conference (overridden by `--conference` flag):
```bash
export CONFERENCE_MCP_EVENT=containerdays-hamburg-2026
```

## Tools Reference (12 tools)

| Tool | Description |
|---|---|
| `search_sessions` | Search talks by keyword, topic, or speaker. |
| `get_schedule` | Get the full schedule for a specific day. |
| `find_speaker` | Look up sessions for a specific person. |
| `find_parties` | Discover social events and happy hours. |
| `plan_party_route` | Get an optimized route for evening events. |
| `get_venue_info` | Details on rooms, maps, and venue address. |
| `get_hotel_info` | Hotel block rates and distances to venue. |
| `get_travel_info` | Airport, transit, and airline discount codes. |
| `get_colocated_events`| Co-located events and workshops. |
| `get_conference_overview`| High-level event summary and key dates. |
| `score_sessions` | Sessions with a personalized scoring rubric for AI-powered ranking. |
| `detect_conflicts` | Check if selected sessions overlap in time. |

## Resources Reference

Access structured data directly via these URIs (per conference):

- `conference://{key}/overview`: Full conference summary
- `conference://{key}/venue`: Venue layout and transit details
- `conference://{key}/hotels`: Accommodation options
- `conference://{key}/colocated-events`: Co-located events and workshops

## Prompts Reference

- `plan_my_conference`: Builds a personalized itinerary.
- `party_tonight`: Plans an evening of networking and social events.
- `first_timer_guide`: Essential tips for new attendees.
- `whats_happening_now`: Finds sessions starting soon.
- `create_profile`: Interactive profile builder for session scoring.

## Adding a New Conference

1. Add a `ConferenceConfig` factory in `src/conference_mcp/conferences.py`
2. Add static data (venue, hotels, events) in `src/conference_mcp/static_data.py`
3. Register it in the `_REGISTRY` dict
4. Optionally add upstream data source URLs (iCal, Sessionize, parties)

## Contributing

1. Clone the repository.
2. Install dependencies: `uv sync`
3. Run the server: `uv run conference-mcp --conference kubecon-eu-2026`
4. Run tests: `uv run pytest tests/`

License: MIT
