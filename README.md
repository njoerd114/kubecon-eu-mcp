# kubecon-eu-mcp

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License MIT](https://img.shields.io/badge/license-MIT-green.svg)
![KubeCon EU 2026](https://img.shields.io/badge/KubeCon%20EU-2026-orange.svg)

An MCP server for KubeCon + CloudNativeCon Europe 2026. This tool serves as an agentic schedule planner, party optimizer, and conference guide for the event held March 23-26 at RAI Amsterdam.

## Overview

kubecon-eu-mcp connects AI agents to live conference data, enabling them to help attendees navigate the schedule, discover social events, and plan their trip. It fetches data live from upstream sources with efficient in-memory caching to ensure accuracy throughout the week.

Data sources include:
- [Official Sched.com iCal feed](https://kccnceu2026.sched.com/)
- [ConferenceParties.com](https://conferenceparties.com/kubeconeu26/)
- CNCF / LF events website

As a meta tie-in, this project highlights the **Agentics Day: MCP + Agents** co-located event on Monday, March 23.

## Features

- **Smart Scheduling**: Search talks by topic, speaker, or technology (eBPF, AI, WASM, etc.).
- **Party Optimizer**: Find evening social events and plan the best route through Amsterdam.
- **Logistics Guide**: Access hotel block info, airline discounts, and venue transit details.
- **Agentic Planning**: Built-in prompts to help users build 4-day itineraries or first-timer guides.
- **Session Scoring**: Personalized session ranking using the scoring rubric from [kubecon-event-scorer](https://github.com/FredrikCarlssn/kubecon-event-scorer) by Fredrik Carlsson — scores across role relevance, topic alignment, and strategic value.
- **Live Updates**: Data is pulled directly from official sources to reflect last-minute room changes.

## Quick Start

### 1. Zero Install (uvx)
If you have `uv` installed, you can run the server without manual installation:
```bash
uvx kubecon-eu-mcp
```

### 2. Standard Install (pip)
Install the package from your local clone or repository:
```bash
pip install .
# Then run the server
kubecon-eu-mcp
```

### 3. Docker
Build and run the containerized server:
```bash
docker build -t kubecon-eu-mcp .
docker run -it kubecon-eu-mcp
```

## Usage Examples

Once connected to an MCP client like Claude Desktop, you can ask questions like:

- "What AI talks are on Wednesday?"
- "Find all sessions featuring Lin Sun."
- "What's the best way to get to RAI Amsterdam from Schiphol airport?"
- "Are there any parties near the venue on Tuesday night?"
- "Plan a 4-day itinerary for a platform engineer interested in security."

### Example Interaction
**User:** What AI talks are on Tuesday?
**Assistant:** (Calls `search_sessions(query="AI", day="tuesday")`)
The agent searches the live schedule and returns matching sessions with titles,
speakers, rooms, and times. It can then help you compare options, flag conflicts
with other sessions you want to attend, and suggest alternatives.

## Tools Reference

The server exposes 12 specialized tools:

| Tool | Description |
|------|-------------|
| `search_sessions` | Search talks by keyword, topic, or speaker. |
| `get_schedule` | Get the full schedule for a specific day. |
| `find_speaker` | Look up sessions for a specific person. |
| `find_parties` | Discover social events and happy hours. |
| `plan_party_route` | Get an optimized route for evening events. |
| `get_venue_info` | Details on rooms, maps, and venue address. |
| `get_hotel_info` | Hotel block rates and distances to RAI. |
| `get_travel_info` | Airport, transit, and airline discount codes. |
| `get_colocated_events`| Monday's specialized events (ArgoCon, Agentics Day, etc.). |
| `get_conference_overview`| High-level event summary and key dates. |
| `score_sessions` | Get sessions with a personalized scoring rubric for AI-powered ranking. |
| `detect_conflicts` | Check if selected sessions overlap in time. |

## Resources Reference

Access structured data directly via these URIs:

- `kubecon://overview`: Full conference summary.
- `kubecon://venue`: Venue layout and transit details.
- `kubecon://hotels`: Accommodation options.
- `kubecon://colocated-events`: Monday's co-located event list.

## Prompts Reference

Pre-configured workflows for common tasks:

- `plan_my_kubecon`: Builds a personalized 4-day itinerary based on interests.
- `party_tonight`: Plans an evening of networking and social events.
- `first_timer_guide`: Provides essential tips for new attendees.
- `whats_happening_now`: Finds sessions starting soon based on current time.
- `create_profile`: Interactive profile builder that scores and ranks sessions using the [kubecon-event-scorer](https://github.com/FredrikCarlssn/kubecon-event-scorer) rubric.

## Configuration

### Claude Desktop
Add this to your `claude_desktop_config.json`:

**Standard (stdio) Mode:**
```json
{
  "mcpServers": {
    "kubecon-eu-mcp": {
      "command": "uvx",
      "args": ["kubecon-eu-mcp"]
    }
  }
}
```

**Hosted (HTTP) Mode:**
If running the server with the `--http` flag:
```json
{
  "mcpServers": {
    "kubecon-eu-mcp": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Contributing

1. Clone the repository.
2. Install dependencies with `uv sync` or `pip install -e .`.
3. Run the server in development mode: `python -m kubecon_eu_mcp`.
4. Submit a Pull Request with your improvements.

License: MIT

