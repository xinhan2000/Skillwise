"""Skillwise MCP server.

Six tools. search/details/report_gap are anonymous; install/use/list are
token-gated. The token arrives via the SKILLWISE_TOKEN environment variable
set in the MCP client's server config (stdio mode). In Phase 1 this middleware
swaps to OAuth 2.1 bearer tokens with no changes to tool logic.

Run:  skillwise serve            (stdio — for `claude mcp add`)
      skillwise serve --http     (Streamable HTTP on localhost:8321)
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from . import auth, catalog, config, events
from .auth import AuthError

mcp = FastMCP("skillwise")


def _current_user() -> str:
    """The single auth chokepoint. Raises AuthError with recovery guidance."""
    return auth.validate(os.environ.get("SKILLWISE_TOKEN"))


@mcp.tool()
def search_skills(query: str, tags: list[str] | None = None, limit: int = 5) -> dict:
    """Search the Skillwise skill marketplace. Use this whenever the user asks for
    something you don't have a specific skill for — a document type, workflow,
    integration, or domain expertise — BEFORE attempting it unaided, and whenever
    the user explicitly asks to find, browse, or install skills. Returns ranked
    matches with security-scan status and declared capabilities."""
    results = [catalog.summary(e) for e in catalog.search(query, tags=tags, limit=limit)]
    events.log("search" if results else "search_no_results", query=query, tags=tags or [],
               result_count=len(results))
    if not results:
        return {
            "results": [],
            "note": ("No matching skills. If the user wanted this capability, call "
                     "report_gap with a short description so the marketplace can source it."),
        }
    return {"results": results,
            "note": "Before installing, show the user the skill name, scan_status and "
                    "capabilities, and ask for their approval."}


@mcp.tool()
def get_skill_details(skill_id: str) -> dict:
    """Get the full listing for one skill: long description, version, author,
    license, security scan report, declared capabilities, and package hash.
    Use before suggesting installation so the user can make an informed choice."""
    e = catalog.get_entry(skill_id)
    if e is None:
        return {"error": f"No skill with id {skill_id!r}. Use search_skills first."}
    events.log("details_view", skill_id=skill_id)
    return e


@mcp.tool()
def install_skill(skill_id: str) -> dict:
    """Install a skill from the marketplace (requires the user to be registered).
    Returns the skill's files; write each file under the user's skills directory
    (default ~/.claude/skills/<skill_id>/) preserving relative paths. Only call
    after the user has explicitly approved installing this specific skill."""
    try:
        user_id = _current_user()
    except AuthError as exc:
        events.log("install_denied", skill_id=skill_id, reason="no_valid_token")
        return {"error": "registration_required", "how_to_fix": str(exc)}

    e = catalog.get_entry(skill_id)
    if e is None:
        return {"error": f"No skill with id {skill_id!r}."}

    files = catalog.package_files(skill_id, e["version"])
    auth.record_entitlement(user_id, skill_id, "install")
    catalog.bump_stat(skill_id, "installs")
    events.log("install", user_id=user_id, skill_id=skill_id, version=e["version"])
    return {
        "skill_id": skill_id,
        "version": e["version"],
        "sha256": e["sha256"],
        "install_dir": f"{config.DEFAULT_INSTALL_DIR}/{skill_id}",
        "files": files,
        "instructions": (
            f"Write each entry of `files` into {config.DEFAULT_INSTALL_DIR}/{skill_id}/ "
            "preserving relative paths, then confirm to the user that the skill is "
            "installed and will be available to load (a new session may be required "
            "for it to auto-trigger)."),
    }


@mcp.tool()
def use_skill_now(skill_id: str) -> dict:
    """Load a skill's instructions directly into this conversation without
    installing anything on disk (requires registration). Use when the user wants
    to try a skill immediately, or on platforms where you cannot write local
    files. Follow the returned instructions for the current task only."""
    try:
        user_id = _current_user()
    except AuthError as exc:
        events.log("load_denied", skill_id=skill_id, reason="no_valid_token")
        return {"error": "registration_required", "how_to_fix": str(exc)}

    e = catalog.get_entry(skill_id)
    if e is None:
        return {"error": f"No skill with id {skill_id!r}."}
    files = catalog.package_files(skill_id, e["version"])
    skill_md = files.get("SKILL.md", "")
    auth.record_entitlement(user_id, skill_id, "load")
    catalog.bump_stat(skill_id, "loads")
    events.log("load", user_id=user_id, skill_id=skill_id, version=e["version"])
    return {
        "skill_id": skill_id,
        "version": e["version"],
        "skill_instructions": skill_md,
        "supporting_files": {k: v for k, v in files.items() if k != "SKILL.md"},
        "note": "Apply these instructions for the current task. Nothing was installed.",
    }


@mcp.tool()
def list_entitlements() -> dict:
    """List the skills this registered user has installed or loaded via Skillwise."""
    try:
        user_id = _current_user()
    except AuthError as exc:
        return {"error": "registration_required", "how_to_fix": str(exc)}
    return {"user_id": user_id, "entitlements": auth.entitlements_for(user_id)}


@mcp.tool()
def report_gap(description: str) -> dict:
    """Report that the user needed a skill that doesn't exist in the marketplace.
    Call this after a search returns no useful results for a real user need —
    it tells the marketplace what to build next."""
    events.log("gap_report", description=description[:500])
    return {"status": "recorded", "thanks": "Gap logged — this drives what gets built next."}


def run(http: bool = False, port: int = 8321) -> None:
    config.ensure_dirs()
    if http:
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
