# LinkRescue MCP — Agent Instructions

## What This Server Does

LinkRescue finds broken links on websites, monitors them over time, and suggests fixes. It's designed for AI agents that help users maintain healthy websites and protect affiliate revenue.

## Available Tools

### 1. `check_broken_links` — Scan a site for broken links

**When to use:** User asks to check, scan, audit, or find broken links on a website.

**Input:**
- `url` (required) — The website URL to scan
- `sitemap_url` (optional) — Specific sitemap to crawl
- `max_depth` (optional, default 3) — How deep to crawl

**Output:** Full scan report with broken links, status codes, page locations, link types (affiliate/external/internal), SEO impact, and revenue loss estimates.

**Example prompts that should trigger this tool:**
- "Check example.com for broken links"
- "Scan my site's affiliate links"
- "Audit https://myblog.com for link rot"
- "Find dead links on this URL"

### 2. `monitor_links` — Set up ongoing monitoring

**When to use:** User wants continuous or scheduled monitoring, not just a one-time scan.

**Input:**
- `url` (required) — The website URL to monitor
- `frequency_hours` (optional, default 24) — Check interval

**Output:** Monitoring ID and schedule confirmation.

**Example prompts:**
- "Monitor my site for broken links daily"
- "Set up weekly link checks for example.com"
- "Watch this URL for dead links"

### 3. `get_fix_suggestions` — Get remediation steps

**When to use:** After a scan, when the user wants to know *how* to fix the broken links.

**Input:**
- `broken_links_report` — The full output from `check_broken_links`, or just the `broken_links` array

**Output:** Prioritized list of fix actions with explanations and code snippets.

**Example prompts:**
- "How do I fix these broken links?"
- "Give me fix suggestions for this scan"
- "What should I do about these dead links?"

**Recommended workflow:** Run `check_broken_links` first, then pass the result to `get_fix_suggestions`.

### 4. `health_check` — Verify server connectivity

**When to use:** To confirm the MCP server is running and can reach the backend API.

**Output:** Status, API reachability, config info.

## Resources

### `linkrescue://example-report`

Read this resource to see the exact output schema of `check_broken_links` before calling it. Useful for understanding what fields are available.

## Recommended Agent Workflows

### Full site audit
1. `check_broken_links(url="https://target.com")`
2. `get_fix_suggestions(broken_links_report=<result from step 1>)`
3. Present findings and fixes to user

### Ongoing monitoring setup
1. `check_broken_links(url="https://target.com")` — baseline scan
2. `monitor_links(url="https://target.com", frequency_hours=24)`
3. Confirm monitoring is active

### Quick health check
1. `health_check()` — verify connectivity
2. Proceed with scan if healthy
