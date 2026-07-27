"""End-user local state: ~/.skillwise/ config and installed-skill manifest.

Override the location with SKILLWISE_USER_DIR (used by tests).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


def user_dir() -> Path:
    return Path(os.environ.get("SKILLWISE_USER_DIR", str(Path.home() / ".skillwise")))


def _config_path() -> Path:
    return user_dir() / "config.json"


def _manifest_path() -> Path:
    return user_dir() / "installed.json"


def load_config() -> dict:
    p = _config_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_config(cfg: dict) -> None:
    user_dir().mkdir(parents=True, exist_ok=True)
    _config_path().write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def install_dir(cfg: dict | None = None) -> Path:
    cfg = cfg if cfg is not None else load_config()
    return Path(cfg.get("install_dir", str(Path.home() / ".claude" / "skills"))).expanduser()


def paused_dir(cfg: dict | None = None) -> Path:
    d = install_dir(cfg)
    return d.parent / (d.name + "-paused")


def load_manifest() -> dict:
    p = _manifest_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest: dict) -> None:
    user_dir().mkdir(parents=True, exist_ok=True)
    _manifest_path().write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def record_install(skill_id: str, version: str, sha256: str) -> None:
    m = load_manifest()
    m[skill_id] = {
        "version": version,
        "sha256": sha256,
        "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "paused": False,
    }
    save_manifest(m)


def set_paused(skill_id: str, paused: bool) -> None:
    m = load_manifest()
    if skill_id in m:
        m[skill_id]["paused"] = paused
        save_manifest(m)


def remove_record(skill_id: str) -> None:
    m = load_manifest()
    m.pop(skill_id, None)
    save_manifest(m)
