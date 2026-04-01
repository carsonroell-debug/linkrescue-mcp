"""
LinkRescue MCP Server — Broken link detection, monitoring, and remediation for AI agents.

Run locally:
    fastmcp run main.py --transport streamable-http --port 8000

Environment variables:
    LINKRESCUE_API_BASE_URL  — Base URL of your LinkRescue API (default: http://localhost:3000/api)
    LINKRESCUE_API_KEY       — API key for authenticated requests
"""

# Re-export from the package so both `fastmcp run main.py` and `pip install .` work.
from linkrescue_mcp.server import mcp  # noqa: F401

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000, stateless_http=True)
