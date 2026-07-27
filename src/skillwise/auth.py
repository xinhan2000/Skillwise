"""Dev-token auth (Phase 0 stub for OAuth 2.1).

Structure mirrors production: one middleware chokepoint, anonymous reads,
authenticated writes/installs, every authed call attributed to a user_id.
Swap `validate()` for real OAuth token introspection in Phase 1.
"""

from __future__ import annotations

import json
import secrets
import time

from . import config


class AuthError(Exception):
    """Raised when a gated tool is called without a valid token."""

    HELP = (
        "This action requires a Skillwise account token. "
        "Ask the user to run `skillwise token create <name>` in the Skillwise "
        "folder, then add the token to this MCP server's config as the "
        "SKILLWISE_TOKEN environment variable and reconnect."
    )


def _load() -> dict:
    if config.tokens_file().exists():
        return json.loads(config.tokens_file().read_text(encoding="utf-8"))
    return {}


def _save(tokens: dict) -> None:
    config.ensure_dirs()
    config.tokens_file().write_text(json.dumps(tokens, indent=2), encoding="utf-8")


def create_token(user_id: str) -> str:
    tokens = _load()
    token = "swk_" + secrets.token_urlsafe(24)
    tokens[token] = {
        "user_id": user_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _save(tokens)
    return token


def validate(token: str | None) -> str:
    """Return user_id for a valid token; raise AuthError otherwise."""
    if not token:
        raise AuthError("No token provided. " + AuthError.HELP)
    entry = _load().get(token)
    if entry is None:
        raise AuthError("Invalid or revoked token. " + AuthError.HELP)
    return entry["user_id"]


# --- entitlement records (which user installed/loaded which skill) ---

def _load_entitlements() -> dict:
    if config.entitlements_file().exists():
        return json.loads(config.entitlements_file().read_text(encoding="utf-8"))
    return {}


def record_entitlement(user_id: str, skill_id: str, kind: str) -> None:
    ents = _load_entitlements()
    user = ents.setdefault(user_id, [])
    if not any(e["skill_id"] == skill_id and e["kind"] == kind for e in user):
        user.append({
            "skill_id": skill_id,
            "kind": kind,  # "install" | "load"
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        config.entitlements_file().write_text(json.dumps(ents, indent=2), encoding="utf-8")


def entitlements_for(user_id: str) -> list[dict]:
    return _load_entitlements().get(user_id, [])
