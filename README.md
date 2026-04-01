<!-- mcp-name: io.github.carsonroell-debug/linkrescue-mcp -->

# LinkRescue MCP Server

[![PyPI](https://img.shields.io/pypi/v/linkrescue-mcp)](https://pypi.org/project/linkrescue-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Find broken links fast, prioritize by impact, and generate fix suggestions your AI agent can act on.

LinkRescue MCP exposes broken-link scanning, monitoring, and remediation workflows through the Model Context Protocol (MCP), so tools like Claude and Cursor can run link-health operations directly.

## What You Get

- `check_broken_links`: scan a URL (or sitemap) and return a structured broken-link report
- `monitor_links`: set up recurring monitoring for a website
- `get_fix_suggestions`: generate prioritized remediation recommendations
- `health_check`: verify MCP server and backend API connectivity

If the LinkRescue backend API is unreachable, the server falls back to realistic simulated data so local testing and demos keep working.

## Requirements

- Python 3.11+
- `pip`

## Quick Start

```bash
git clone https://github.com/carsonroell-debug/linkrescue-mcp.git
cd linkrescue-mcp
pip install -r requirements.txt
python main.py
```

MCP endpoint:

- `http://localhost:8000/mcp`

## Configuration

| Variable | Description | Default |
|---|---|---|
| `LINKRESCUE_API_BASE_URL` | Base URL for LinkRescue API | `http://localhost:3000/api/v1` |
| `LINKRESCUE_API_KEY` | API key for authenticated requests | empty |

Example:

```bash
export LINKRESCUE_API_BASE_URL="https://your-api.example.com/api/v1"
export LINKRESCUE_API_KEY="your-api-key"
python main.py
```

## Running Options

Run directly:

```bash
python main.py
```

Run via FastMCP CLI:

```bash
fastmcp run main.py --transport streamable-http --port 8000
```

## Connect an MCP Client

### Claude Desktop

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "linkrescue": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add linkrescue --transport http http://localhost:8000/mcp
```

## Try It

```bash
fastmcp list-tools main.py
fastmcp call-tool main.py health_check '{}'
fastmcp call-tool main.py check_broken_links '{"url":"https://example.com"}'
```

## Tool Inputs and Outputs

### `check_broken_links`

Inputs:

- `url` (required): site URL to scan
- `sitemap_url` (optional): crawl from sitemap
- `max_depth` (optional, default `3`): crawl depth

Returns scan metadata, broken-link details, and summary statistics.

### `monitor_links`

Inputs:

- `url` (required)
- `frequency_hours` (optional, default `24`)

Returns monitoring ID, schedule details, and status.

### `get_fix_suggestions`

Input:

- full report from `check_broken_links`, or
- raw `broken_links` array, or
- JSON string of either format

Returns prioritized actions and suggested remediation steps.

### `health_check`

No input. Returns server status and backend API reachability.

## Deployment

### Smithery

This repo includes `smithery.yaml` and `smithery.json`.

1. Push repository to GitHub
2. Create/add server in [Smithery](https://smithery.ai/)
3. Point Smithery to this repository

### Docker / Hosting Platforms

A `Dockerfile` is included for Railway, Fly.io, and other container hosts.

```bash
# Railway
railway up

# Fly.io
fly launch
fly deploy
```

Set `LINKRESCUE_API_BASE_URL` and `LINKRESCUE_API_KEY` in your host environment.

## Architecture

```text
Agent (Claude, Cursor, etc.)
  -> MCP
LinkRescue MCP Server (this repo)
  -> HTTP API
LinkRescue Backend API
```

This server is a translation layer between MCP tool calls and LinkRescue API operations.

## Additional README Variants

- Developer-focused version: `README.dev.md`
- Marketplace-focused version: `README.marketplace.md`
