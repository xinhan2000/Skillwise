"""Marketplace client layer with two interchangeable backends.

LocalBackend  — calls core functions in-process against the local catalog
                (SKILLWISE_HOME). No server process needed. Phase-0 default.
HttpBackend   — talks to a Skillwise server's REST API (/api/*). Becomes the
                default in Phase 1 by setting `server_url` in ~/.skillwise/config.

Both enforce the same rule: reads are anonymous, install requires a token.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod

from . import auth, catalog, config, events


class ClientError(Exception):
    pass


class RegistrationRequired(ClientError):
    pass


class Backend(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 20) -> list[dict]: ...

    @abstractmethod
    def get(self, skill_id: str) -> dict | None: ...

    @abstractmethod
    def register(self, name: str) -> str: ...

    @abstractmethod
    def install(self, skill_id: str, token: str | None) -> dict: ...


class LocalBackend(Backend):
    """In-process access to the local catalog. Mirrors server.py's gating."""

    def search(self, query: str, limit: int = 20) -> list[dict]:
        results = [catalog.summary(e) for e in catalog.search(query, limit=limit)]
        events.log("cli_search" if results else "cli_search_no_results",
                   query=query, result_count=len(results))
        return results

    def get(self, skill_id: str) -> dict | None:
        return catalog.get_entry(skill_id)

    def register(self, name: str) -> str:
        return auth.create_token(name)

    def install(self, skill_id: str, token: str | None) -> dict:
        try:
            user_id = auth.validate(token)
        except auth.AuthError as exc:
            raise RegistrationRequired(str(exc)) from exc
        entry = catalog.get_entry(skill_id)
        if entry is None:
            raise ClientError(f"No skill with id {skill_id!r}.")
        files = catalog.package_files(skill_id, entry["version"])
        auth.record_entitlement(user_id, skill_id, "install")
        catalog.bump_stat(skill_id, "installs")
        events.log("install", user_id=user_id, skill_id=skill_id,
                   version=entry["version"], via="cli")
        return {"skill_id": skill_id, "version": entry["version"],
                "sha256": entry["sha256"], "files": files}


class HttpBackend(Backend):
    """Thin REST client for a (local or hosted) Skillwise server."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, body: dict | None = None,
                 token: str | None = None) -> dict:
        url = self.base_url + path
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                raise RegistrationRequired(exc.read().decode()[:300]) from exc
            raise ClientError(f"Server error {exc.code}: {exc.read().decode()[:300]}") from exc
        except urllib.error.URLError as exc:
            raise ClientError(f"Cannot reach Skillwise server at {self.base_url}: {exc.reason}") from exc

    def search(self, query: str, limit: int = 20) -> list[dict]:
        qs = urllib.parse.urlencode({"q": query, "limit": limit})
        return self._request("GET", f"/api/skills?{qs}")["results"]

    def get(self, skill_id: str) -> dict | None:
        try:
            return self._request("GET", f"/api/skills/{urllib.parse.quote(skill_id)}")
        except ClientError as exc:
            if "404" in str(exc):
                return None
            raise

    def register(self, name: str) -> str:
        return self._request("POST", "/api/register", {"name": name})["token"]

    def install(self, skill_id: str, token: str | None) -> dict:
        if not token:
            raise RegistrationRequired("This server requires registration to install skills.")
        return self._request("POST", f"/api/skills/{urllib.parse.quote(skill_id)}/install",
                             {}, token=token)


def get_backend(cfg: dict) -> Backend:
    """Pick the backend: server_url configured → HTTP; otherwise in-process local."""
    if cfg.get("server_url"):
        return HttpBackend(cfg["server_url"])
    if cfg.get("skillwise_home"):
        os.environ["SKILLWISE_HOME"] = cfg["skillwise_home"]
    if not config.catalog_index().exists():
        raise ClientError(
            "No local catalog found and no server_url configured.\n"
            f"Looked in: {config.catalog_dir()}\n"
            "Fix: run from your Skillwise folder, set skillwise_home in "
            "~/.skillwise/config.json, or set server_url to a Skillwise server.")
    return LocalBackend()
