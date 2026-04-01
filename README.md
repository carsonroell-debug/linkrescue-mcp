# LinkRescue MCP Server

MCP server that exposes LinkRescue's broken link scanning, monitoring, and fix suggestion capabilities to AI agents (Claude, Cursor, etc.).

Built with [FastMCP 3.x](https://github.com/jlowin/fastmcp) for the [Model Context Protocol](https://modelcontextprotocol.io/).

## Run Locally

```bash
# Install deps
pip install -r requirements.txt

# Run with FastMCP (streamable HTTP for agent access)
fastmcp run main.py --transport streamable-http --port 8000

# Or run directly
python main.py
```

The server starts on `http://localhost:8000/mcp`.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `LINKRESCUE_API_BASE_URL` | Your LinkRescue API base URL | `http://localhost:3000/api` |
| `LINKRESCUE_API_KEY` | API key for authenticated requests | (empty) |

Without a running LinkRescue API backend, the server returns realistic simulated data — useful for testing and demos.

## Connect to Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "linkrescue": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Connect to Claude Code

```bash
claude mcp add linkrescue --transport http http://localhost:8000/mcp
```

## Test with FastMCP CLI

```bash
# List tools
fastmcp list-tools main.py

# Call a tool
fastmcp call-tool main.py health_check '{}'
fastmcp call-tool main.py check_broken_links '{"url": "https://example.com"}'
```

## Deploy to Smithery

1. Push this repo to GitHub
2. Go to [smithery.ai](https://smithery.ai)
3. Click "Add Server" → paste your GitHub repo URL
4. Smithery reads `smithery.yaml` and deploys automatically

One-liner after pushing to GitHub:

```bash
npx @anthropic-ai/claude-code mcp add linkrescue --smithery freedomengineers/linkrescue-mcp
```

## Deploy to Railway / Fly.io

Use the included `Dockerfile`:

```bash
# Railway
railway up

# Fly.io
fly launch
fly deploy
```

Set env vars in the platform dashboard.

## Tools

| Tool | Description |
|---|---|
| `check_broken_links` | Scan a URL/sitemap for broken links with SEO impact estimates |
| `monitor_links` | Set up scheduled broken link monitoring |
| `get_fix_suggestions` | Get prioritized remediation steps from a scan report |
| `health_check` | Verify server and API connectivity |

## Architecture

```
Agent (Claude/Cursor)
  ↓ MCP protocol
LinkRescue MCP Server (this repo)
  ↓ HTTP API calls
LinkRescue API Backend (your existing app)
```

The MCP server is a thin translation layer. It converts MCP tool calls into LinkRescue API requests and returns structured results agents can act on. If the backend is unreachable, it falls back to simulated data for demo purposes.
