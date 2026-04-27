<!-- mcp-name: io.github.carsonroell-debug/linkrescue-mcp -->

# LinkRescue MCP Server

[![PyPI](https://img.shields.io/pypi/v/linkrescue-mcp)](https://pypi.org/project/linkrescue-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCPize](https://img.shields.io/badge/MCPize-Install-22c55e)](https://mcpize.com/mcp/linkrescue-mcp?ref=YHCCR&utm_source=github&utm_medium=readme)

Find broken affiliate links fast, prioritize by impact, and generate fix suggestions your AI agent can act on.

**One call. 38+ affiliate networks checked. Revenue loss estimated.**

> **One-click install:** [Install on MCPize](https://mcpize.com/mcp/linkrescue-mcp?ref=YHCCR&utm_source=github&utm_medium=readme) | `pip install linkrescue-mcp`

LinkRescue MCP exposes broken-link scanning, monitoring, and remediation workflows through the Model Context Protocol (MCP), so tools like Claude and Cursor can run link-health operations directly.

## What You Get

- `check_broken_links`: scan a URL (or sitemap) and return a structured broken-link report
- `monitor_links`: set up recurring monitoring for a website
- `get_fix_suggestions`: generate prioritized remediation recommendations
- `health_check`: verify MCP server and backend API connectivity

If the LinkRescue backend API is unreachable, the server falls back to realistic simulated data so local testing and demos keep working.

## Quick Start

```json
{
  "mcpServers": {
    "linkrescue": {
      "command": "linkrescue-mcp"
    }
  }
}
```

Then ask your AI agent:

> "Scan example.com for broken affiliate links"

## Free vs Pro

| Tool | Free | Pro ($19/mo) | Agency ($29/mo) |
|------|------|--------------|-----------------|
| `health_check` | Yes | Yes | Yes |
| `check_broken_links` (up to 50 pages) | Yes | Yes | Yes |
| `check_broken_links` (up to 2,000 pages) | - | Yes | Yes |
| `check_broken_links` (unlimited + sitemap crawl) | - | - | Yes |
| `get_fix_suggestions` | - | Yes | Yes |
| `monitor_links` (daily) | - | Yes | Yes |
| `monitor_links` (hourly + webhooks) | - | - | Yes |
| Revenue loss estimates | - | Yes | Yes |
| Multi-site monitoring | - | 5 sites | 25 sites |

Free tier gives you single-page broken-link checks. Pro unlocks the full crawler + fix suggestions + recurring monitoring. Agency adds hourly checks, webhooks, and unlimited site count.

**[Upgrade to Pro on MCPize](https://mcpize.com/mcp/linkrescue-mcp?ref=YHCCR&utm_source=github&utm_medium=readme)** — $19/mo or $190/yr. Agency $29/mo or $290/yr.

## Install

### MCPize (Recommended)

One-click install with managed hosting: **[Install on MCPize](https://mcpize.com/mcp/linkrescue-mcp?ref=YHCCR&utm_source=github&utm_medium=readme)**

### PyPI

```bash
pip install linkrescue-mcp
linkrescue-mcp
```

### From source

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
export LINKRESCUE_API_BASE_URL="https://www.linkrescue.io/api/v1"
export LINKRESCUE_API_KEY="your-api-key"
linkrescue-mcp
```

Get an API key at [linkrescue.io/settings/api](https://www.linkrescue.io/settings/api) (Pro and Agency tiers only).

## Running Options

Run via the installed entry point:

```bash
linkrescue-mcp
```

Run directly from source:

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
      "command": "linkrescue-mcp"
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
- `sitemap_url` (optional, Agency tier): crawl from sitemap
- `max_depth` (optional, default `3`): crawl depth

Returns scan metadata, broken-link details, and summary statistics. Pro and Agency tiers include estimated monthly revenue loss for broken affiliate links.

### `monitor_links`

Inputs:

- `url` (required)
- `frequency_hours` (optional, default `24`; Agency tier supports `1`)

Returns monitoring ID, schedule details, and status. Free tier returns a simulated monitor (no persistence).

### `get_fix_suggestions`

Input:

- full report from `check_broken_links`, or
- raw `broken_links` array, or
- JSON string of either format

Returns prioritized actions and suggested remediation steps. Pro and Agency tiers only.

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
LinkRescue Backend API (linkrescue.io)
```

This server is a translation layer between MCP tool calls and LinkRescue API operations.

## License

MIT — Built by [Freedom Engineers](https://freedomengineers.tech)

## Related

- [SelfHeal MCP](https://mcpize.com/mcp/selfheal-mcp?ref=YHCCR&utm_source=github&utm_medium=readme) — Self-healing proxy for MCP servers
- [SiteHealth MCP](https://mcpize.com/mcp/sitehealth-mcp?ref=YHCCR&utm_source=github&utm_medium=readme) — Full website health audit
- [LeadEnrich MCP](https://mcpize.com/mcp/leadenrich-mcp?ref=YHCCR&utm_source=github&utm_medium=readme) — Waterfall lead enrichment

## Additional README Variants

- Developer-focused version: `README.dev.md`
- Marketplace-focused version: `README.marketplace.md`
