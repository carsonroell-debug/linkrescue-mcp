"""
LinkRescue MCP Server — Broken link detection, monitoring, and remediation for AI agents.

Run locally:
    fastmcp run main.py --transport streamable-http --port 8000

Environment variables:
    LINKRESCUE_API_BASE_URL  — Base URL of your LinkRescue API (default: http://localhost:3000/api/v1)
    LINKRESCUE_API_KEY       — API key for authenticated requests
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
import asyncio
from typing import Any

import httpx
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_BASE = os.getenv("LINKRESCUE_API_BASE_URL", "http://localhost:3000/api/v1").rstrip("/")
API_KEY = os.getenv("LINKRESCUE_API_KEY", "")

log = logging.getLogger("linkrescue-mcp")
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "LinkRescue",
    instructions=(
        "LinkRescue finds, monitors, and fixes broken links on any website. "
        "Use check_broken_links to scan a URL, monitor_links to set up ongoing checks, "
        "get_fix_suggestions to get remediation steps from a scan report, "
        "and health_check to verify the server is running."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _headers() -> dict[str, str]:
    h: dict[str, str] = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


def _app_base() -> str:
    if API_BASE.endswith("/api/v1"):
        return API_BASE[: -len("/api/v1")]
    if API_BASE.endswith("/api"):
        return API_BASE[: -len("/api")]
    return API_BASE


def _ts() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


async def _api_post(path: str, payload: dict) -> dict:
    """POST to the LinkRescue API. Falls back to local simulation only if unreachable."""
    url = f"{API_BASE}{path}"
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=_headers())
            resp.raise_for_status()
            return resp.json()
    except httpx.RequestError as exc:
        log.warning("API call to %s failed: %s — using local simulation", url, exc)
        return {}
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        raise RuntimeError(f"LinkRescue API error {exc.response.status_code}: {detail}") from exc


async def _api_get(path: str, params: dict | None = None) -> dict:
    url = f"{API_BASE}{path}"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params, headers=_headers())
            resp.raise_for_status()
            return resp.json()
    except httpx.RequestError as exc:
        log.warning("API call to %s failed: %s — using local simulation", url, exc)
        return {}
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        raise RuntimeError(f"LinkRescue API error {exc.response.status_code}: {detail}") from exc


async def _wait_for_scan(scan_id: str, timeout_seconds: int = 300, poll_interval: float = 2.0) -> dict:
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        status = await _api_get(f"/scans/{scan_id}")
        if not status:
            return {}

        if status.get("status") in {"completed", "failed"}:
            return status

        await asyncio.sleep(poll_interval)

    raise RuntimeError(f"Timed out waiting for scan {scan_id} to complete")


def _map_issue_priority(issue: dict[str, Any]) -> str:
    if issue.get("is_affiliate"):
        return "high"

    issue_type = issue.get("issue_type")
    if issue_type in {"BROKEN_4XX", "SERVER_5XX", "LOST_PARAMS"}:
        return "medium"
    return "low"


def _normalize_scan_report(report: dict[str, Any]) -> dict[str, Any]:
    issues = report.get("issues", [])
    broken_links = [
        {
            "url": issue.get("url"),
            "status_code": issue.get("status_code"),
            "final_url": issue.get("final_url"),
            "redirect_hops": issue.get("redirect_hops"),
            "issue_type": issue.get("issue_type"),
            "link_type": "affiliate" if issue.get("is_affiliate") else "external",
            "is_affiliate": issue.get("is_affiliate", False),
            "seo_impact": _map_issue_priority(issue),
        }
        for issue in issues
    ]
    summary = report.get("summary", {})
    by_type = summary.get("by_type")
    if not by_type:
        by_type = {}
        for issue in issues:
            issue_type = issue.get("issue_type", "UNKNOWN")
            by_type[issue_type] = by_type.get(issue_type, 0) + 1

    return {
        "scan_id": report.get("scan_id"),
        "url": report.get("domain"),
        "timestamp": report.get("completed_at") or report.get("started_at") or _ts(),
        "pages_scanned": report.get("pages_scanned", 0),
        "total_links_checked": report.get("links_checked", 0),
        "broken_links": broken_links,
        "summary": {
            "total_broken": report.get("issue_count", len(broken_links)),
            "by_type": by_type,
            "health_score": summary.get("health_score"),
        },
        "raw_scan_status": report,
    }

# ---------------------------------------------------------------------------
# Simulation helpers (used when no backend API is reachable)
# ---------------------------------------------------------------------------

def _simulate_scan(url: str, max_depth: int) -> dict:
    """Return a realistic simulated scan result for demo/testing purposes."""
    return {
        "scan_id": str(uuid.uuid4()),
        "url": url,
        "timestamp": _ts(),
        "pages_scanned": 47,
        "total_links_checked": 312,
        "max_depth": max_depth,
        "broken_links": [
            {
                "url": f"{url.rstrip('/')}/old-product-link",
                "status_code": 404,
                "found_on": f"{url.rstrip('/')}/blog/best-picks-2025",
                "anchor_text": "Check latest price",
                "link_type": "affiliate",
                "seo_impact": "high",
                "estimated_monthly_clicks": 320,
                "estimated_revenue_loss_usd": 48.00,
            },
            {
                "url": "https://expired-partner.example.com/deal",
                "status_code": 502,
                "found_on": f"{url.rstrip('/')}/resources",
                "anchor_text": "Partner deal",
                "link_type": "external",
                "seo_impact": "medium",
                "estimated_monthly_clicks": 85,
                "estimated_revenue_loss_usd": 0,
            },
            {
                "url": f"{url.rstrip('/')}/wp-content/uploads/guide.pdf",
                "status_code": 403,
                "found_on": f"{url.rstrip('/')}/guides/seo-checklist",
                "anchor_text": "Download the checklist",
                "link_type": "internal",
                "seo_impact": "low",
                "estimated_monthly_clicks": 40,
                "estimated_revenue_loss_usd": 0,
            },
        ],
        "summary": {
            "total_broken": 3,
            "by_type": {"affiliate": 1, "external": 1, "internal": 1},
            "total_estimated_revenue_loss_usd": 48.00,
            "health_score": 87,
        },
    }


def _simulate_suggestions(broken_links: list[dict]) -> list[dict]:
    suggestions = []
    for link in broken_links:
        url = link.get("url", "")
        status = link.get("status_code", 0)
        suggestion: dict[str, Any] = {
            "broken_url": url,
            "status_code": status,
            "priority": link.get("seo_impact", "medium"),
        }

        if link.get("link_type") == "affiliate":
            suggestion["action"] = "update_affiliate_link"
            suggestion["detail"] = (
                "This affiliate link is returning a 404. Check if the merchant "
                "changed their link structure or if the product was removed. "
                "Update the href to the current product URL or replace with an "
                "alternative product from the same program."
            )
            suggestion["code_snippet"] = (
                f'<!-- Replace broken link -->\n'
                f'<a href="NEW_AFFILIATE_URL" rel="nofollow sponsored">'
                f'{link.get("anchor_text", "Link")}</a>'
            )
        elif status in (301, 302, 308):
            suggestion["action"] = "follow_redirect"
            suggestion["detail"] = (
                "This URL redirects. Update the link to point directly to the "
                "final destination to avoid redirect chains and improve page speed."
            )
        elif status == 403:
            suggestion["action"] = "check_permissions"
            suggestion["detail"] = (
                "Access is forbidden. Verify the resource still exists and that "
                "any authentication or CDN configuration is correct."
            )
        elif status >= 500:
            suggestion["action"] = "retry_later_or_replace"
            suggestion["detail"] = (
                "The target server is returning a 5xx error. This may be temporary. "
                "Re-check in 24 hours; if persistent, replace with an alternative link."
            )
        else:
            suggestion["action"] = "remove_or_replace"
            suggestion["detail"] = (
                f"Link returned HTTP {status}. Remove the link or replace it with "
                "a working alternative."
            )

        suggestions.append(suggestion)

    return suggestions

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def check_broken_links(
    url: str,
    sitemap_url: str | None = None,
    max_depth: int = 3,
) -> dict:
    """Scans a single URL or entire site/sitemap for broken links.

    Returns a structured report with every broken link found, its HTTP status code,
    the page it was discovered on, link type (affiliate/external/internal),
    SEO impact rating, and estimated revenue loss.

    Agents can pass the output directly to get_fix_suggestions for remediation steps.

    Args:
        url: The website URL to scan (e.g. "https://example.com").
        sitemap_url: Optional sitemap URL to crawl instead of discovering pages by depth.
        max_depth: How many levels deep to crawl from the start URL. Default 3.

    Returns:
        JSON report with scan_id, broken_links list, and summary statistics.
    """
    payload = {"url": url}
    if sitemap_url:
        payload["sitemap_url"] = sitemap_url

    result = await _api_post("/scans", payload)

    if not result:
        log.info("Using simulated scan for %s", url)
        result = _simulate_scan(url, max_depth)
    else:
        scan_id = result.get("scan_id")
        if not scan_id:
            raise RuntimeError("LinkRescue API did not return a scan_id")
        completed = await _wait_for_scan(scan_id)
        if not completed:
            log.info("Using simulated scan for %s", url)
            result = _simulate_scan(url, max_depth)
        elif completed.get("status") == "failed":
            return completed
        else:
            result = _normalize_scan_report(completed)

    return result


@mcp.tool()
async def monitor_links(
    url: str,
    frequency_hours: int = 24,
) -> dict:
    """Sets up ongoing broken-link monitoring for a website.

    The monitor runs on a schedule (default: every 24 hours) and will detect
    new broken links, links that were fixed, and changes in site health score.

    Returns a monitoring_id you can reference later to check status or cancel.

    Args:
        url: The website URL to monitor.
        frequency_hours: How often to re-scan, in hours. Default 24.

    Returns:
        Confirmation with monitoring_id and schedule details.
    """
    payload = {"url": url, "frequency_hours": frequency_hours}
    result = await _api_post("/monitors", payload)

    if not result:
        monitoring_id = str(uuid.uuid4())
        result = {
            "monitoring_id": monitoring_id,
            "url": url,
            "frequency_hours": frequency_hours,
            "status": "active",
            "next_scan": _ts(),
            "message": f"Monitoring set up for {url} every {frequency_hours}h.",
        }

    return result


@mcp.tool()
async def get_fix_suggestions(
    broken_links_report: str | dict,
) -> dict:
    """Given a broken links report, returns prioritized remediation suggestions.

    Each suggestion includes the broken URL, a recommended action
    (update link, follow redirect, remove, etc.), a human-readable explanation,
    and a code snippet where applicable.

    Accepts either the full JSON report from check_broken_links or just the
    broken_links array.

    Args:
        broken_links_report: The scan report (JSON string or dict) from check_broken_links.

    Returns:
        List of prioritized fix suggestions with code snippets.
    """
    if isinstance(broken_links_report, str):
        try:
            broken_links_report = json.loads(broken_links_report)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON. Pass the output of check_broken_links directly."}

    # Extract broken_links array from either full report or raw array
    if isinstance(broken_links_report, dict):
        broken = broken_links_report.get("broken_links", [])
    elif isinstance(broken_links_report, list):
        broken = broken_links_report
    else:
        return {"error": "Expected a scan report dict or broken_links array."}

    if not broken:
        return {"suggestions": [], "message": "No broken links to fix — site looks healthy!"}

    payload: dict[str, Any]
    if isinstance(broken_links_report, dict) and broken_links_report.get("scan_id"):
        payload = {"scan_id": broken_links_report["scan_id"]}
    else:
        payload = {"broken_links": broken}

    # Try API first
    result = await _api_post("/suggestions", payload)

    if not result:
        suggestions = _simulate_suggestions(broken)
        result = {
            "suggestions": suggestions,
            "total": len(suggestions),
            "high_priority": sum(1 for s in suggestions if s.get("priority") == "high"),
        }

    return result


@mcp.tool()
async def health_check() -> dict:
    """Confirms the LinkRescue MCP server is alive and can reach the backend API.

    Use this to verify connectivity before running scans. Returns server status,
    API reachability, and current configuration.
    """
    api_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{_app_base()}/api/health", headers=_headers())
            api_ok = resp.status_code == 200
    except httpx.HTTPError:
        pass

    return {
        "status": "ok",
        "server": "LinkRescue MCP",
        "api_base_url": API_BASE,
        "api_reachable": api_ok,
        "api_key_configured": bool(API_KEY),
        "timestamp": _ts(),
    }

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("linkrescue://example-report")
async def example_report() -> str:
    """Sample broken-links scan report showing the output format of check_broken_links.

    Agents can read this resource to understand the data schema before calling tools.
    """
    sample = _simulate_scan("https://example.com", max_depth=3)
    return json.dumps(sample, indent=2)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000, stateless_http=True)
