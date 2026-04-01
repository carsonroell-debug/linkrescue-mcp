# LinkRescue MCP Server (Developer README)

Technical reference for local development, integration, and deployment.

## Project Overview

This repository exposes LinkRescue functionality over MCP using FastMCP.

Core capabilities:

- broken-link scanning (`check_broken_links`)
- scheduled monitoring (`monitor_links`)
- remediation guidance (`get_fix_suggestions`)
- connectivity checks (`health_check`)

## Requirements

- Python 3.11+
- pip

## Install

```bash
pip install -r requirements.txt
```

## Run

Direct:

```bash
python main.py
```

FastMCP CLI:

```bash
fastmcp run main.py --transport streamable-http --port 8000
```

Endpoint:

- `http://localhost:8000/mcp`

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `LINKRESCUE_API_BASE_URL` | LinkRescue API base URL | `http://localhost:3000/api/v1` |
| `LINKRESCUE_API_KEY` | Bearer token for API auth | empty |

## Tool Contracts

### `check_broken_links`

Input:

- `url: str`
- `sitemap_url: str | None = None`
- `max_depth: int = 3`

Output includes:

- `scan_id`, `url`, `timestamp`
- crawl counts (`pages_scanned`, `total_links_checked`)
- `broken_links[]`
- `summary`

Behavior:

- Calls backend `/scans`, then polls `/scans/{scan_id}` until complete.
- Falls back to local simulation on request/connectivity failure.

### `monitor_links`

Input:

- `url: str`
- `frequency_hours: int = 24`

Behavior:

- Calls `/monitors`
- Simulates monitor creation if backend unavailable

### `get_fix_suggestions`

Input:

- dict report from `check_broken_links`
- or raw `broken_links` list
- or JSON string of either

Behavior:

- Calls `/suggestions`
- Simulates suggestions when backend unavailable

### `health_check`

Behavior:

- Returns server status
- Checks backend reachability via `GET {_app_base()}/api/health`

## MCP Resource

- `linkrescue://example-report`: JSON example report schema for agents.

## Local Validation

```bash
fastmcp list-tools main.py
fastmcp call-tool main.py health_check '{}'
fastmcp call-tool main.py check_broken_links '{"url":"https://example.com"}'
```

## Repository Structure

- `main.py`: entrypoint and re-export
- `linkrescue_mcp/server.py`: MCP server, tools, API client logic, simulation logic
- `server.json`: MCP registry metadata
- `smithery.yaml`: Smithery deployment config
- `pyproject.toml`: packaging and script metadata

## Deployment

### Smithery

Repo includes first-class Smithery config.

### Container

Use included `Dockerfile` for Railway, Fly.io, or other container hosts.

## Notes

- API HTTP status failures raise explicit runtime errors.
- Network/request failures trigger simulation fallback.
- Defaults are optimized for local development.
