"""Central paths and configuration.

Everything lives under SKILLWISE_HOME (default: current working directory).
This keeps Phase 0 fully local and makes the store relocatable — point
SKILLWISE_HOME at any folder (or later, swap this module for a remote client).
"""

from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    return Path(os.environ.get("SKILLWISE_HOME", ".")).resolve()


def catalog_dir() -> Path:
    return home() / "catalog"


def skills_dir() -> Path:
    return catalog_dir() / "skills"


def catalog_index() -> Path:
    return catalog_dir() / "catalog.json"


def publish_log() -> Path:
    return catalog_dir() / "publish_log.jsonl"


def data_dir() -> Path:
    return home() / "data"


def tokens_file() -> Path:
    return data_dir() / "tokens.json"


def entitlements_file() -> Path:
    return data_dir() / "entitlements.json"


def events_file() -> Path:
    return data_dir() / "events.jsonl"


def ensure_dirs() -> None:
    for d in (catalog_dir(), skills_dir(), data_dir()):
        d.mkdir(parents=True, exist_ok=True)


# Files larger than this are rejected at ingest (bytes).
MAX_FILE_BYTES = 5 * 1024 * 1024
# Total package size limit (bytes).
MAX_PACKAGE_BYTES = 20 * 1024 * 1024
# Default install location suggested to the agent.
DEFAULT_INSTALL_DIR = "~/.claude/skills"
