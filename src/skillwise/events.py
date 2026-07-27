"""Append-only event telemetry (data/events.jsonl).

Even in single-user Phase 0 this matters: searches with no results are
a purchase-intent list for skills that don't exist yet.
"""

from __future__ import annotations

import json
import time

from . import config


def log(event: str, user_id: str | None = None, **payload) -> None:
    config.ensure_dirs()
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "user_id": user_id or "anon",
        "payload": payload,
    }
    with config.events_file().open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
