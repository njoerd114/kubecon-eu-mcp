"""Conference MCP Server — Agentic conference guide via Model Context Protocol.

Supports multiple conferences via the --conference flag (e.g.
--conference kubecon-eu-2026, --conference containerdays-hamburg-2026).
"""

import os
import sys

from conference_mcp.conferences import get_conference, default_conference


def main() -> None:
    """Entry point for the CLI."""
    transport = "stdio"
    args = sys.argv[1:]

    # Conference selection: CLI arg > env var > default
    conf_key = os.environ.get("CONFERENCE_MCP_EVENT", default_conference())
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == "--conference" and i + 1 < len(args):
            conf_key = args[i + 1]
            i += 2
        elif args[i].startswith("--conference="):
            conf_key = args[i].split("=", 1)[1]
            i += 1
        elif args[i] == "--http":
            transport = "streamable-http"
            i += 1
        elif args[i] == "--list-conferences":
            from conference_mcp.conferences import list_conferences

            for c in list_conferences():
                print(c)
            return
        else:
            remaining.append(args[i])
            i += 1

    config = get_conference(conf_key)
    from conference_mcp.server import create_server

    mcp = create_server(config)
    mcp.run(transport=transport)
