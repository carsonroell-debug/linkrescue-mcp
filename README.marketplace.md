# LinkRescue MCP Server

Fix broken links with AI agents in minutes.

LinkRescue MCP connects your agent to broken-link scanning, impact-aware prioritization, and fix suggestions through MCP.

## Best For

- SEO teams maintaining content-heavy sites
- affiliate publishers losing revenue from dead links
- engineering teams automating website quality checks

## What It Does

- scans URLs or sitemaps for broken links
- labels issues by impact
- suggests practical remediation actions
- supports recurring link monitoring

## Tools Included

- `check_broken_links`
- `monitor_links`
- `get_fix_suggestions`
- `health_check`

## Quick Setup

```bash
pip install linkrescue-mcp
python main.py
```

Endpoint:

- `http://localhost:8000/mcp`

## MCP Client Snippet

```json
{
  "mcpServers": {
    "linkrescue": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Configuration

- `LINKRESCUE_API_BASE_URL` (default: `http://localhost:3000/api/v1`)
- `LINKRESCUE_API_KEY` (optional)

## Reliability

If the backend API is unreachable, LinkRescue MCP returns realistic simulated responses for demos and local development.

## Repository

[carsonroell-debug/linkrescue-mcp](https://github.com/carsonroell-debug/linkrescue-mcp)
