"""Catalog store: the index, package files, hashing, search, provenance log."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

from . import config


# ---------- index ----------

def load_index() -> list[dict]:
    if config.catalog_index().exists():
        return json.loads(config.catalog_index().read_text(encoding="utf-8"))
    return []


def save_index(entries: list[dict]) -> None:
    config.ensure_dirs()
    config.catalog_index().write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def get_entry(skill_id: str) -> dict | None:
    for e in load_index():
        if e["id"] == skill_id:
            return e
    return None


def upsert_entry(entry: dict) -> None:
    entries = load_index()
    for i, e in enumerate(entries):
        if e["id"] == entry["id"]:
            entries[i] = entry
            break
    else:
        entries.append(entry)
    save_index(entries)


def bump_stat(skill_id: str, stat: str) -> None:
    entries = load_index()
    for e in entries:
        if e["id"] == skill_id:
            e.setdefault("stats", {})
            e["stats"][stat] = e["stats"].get(stat, 0) + 1
            save_index(entries)
            return


# ---------- packages ----------

def version_dir(skill_id: str, version: str) -> Path:
    return config.skills_dir() / skill_id / version


def package_files(skill_id: str, version: str) -> dict[str, str]:
    """Return {relative_path: content} for a published package (text files, excluding _meta)."""
    root = version_dir(skill_id, version)
    files: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and "_meta" not in p.parts:
            files[str(p.relative_to(root))] = p.read_text(encoding="utf-8", errors="replace")
    return files


def canonical_hash(package_dir: Path) -> str:
    """Deterministic sha256 over sorted relative paths + contents."""
    h = hashlib.sha256()
    for p in sorted(package_dir.rglob("*")):
        if p.is_file() and "_meta" not in p.parts:
            h.update(str(p.relative_to(package_dir)).encode())
            h.update(b"\x00")
            h.update(p.read_bytes())
            h.update(b"\x00")
    return h.hexdigest()


def append_publish_log(skill_id: str, version: str, sha256: str) -> None:
    """Append-only provenance record — the seed of the transparency log."""
    config.ensure_dirs()
    line = json.dumps({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "id": skill_id,
        "version": version,
        "sha256": sha256,
    })
    with config.publish_log().open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------- search ----------

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def search(query: str, tags: list[str] | None = None, limit: int = 5) -> list[dict]:
    """Weighted keyword search: name×3, tags×2, one-liner/description×1.

    An empty query means browse mode: the whole catalog (optionally filtered
    by tags), most-installed first.
    """
    entries = load_index()
    if tags:
        wanted = {t.lower() for t in tags}
        entries = [e for e in entries
                   if wanted & {t.lower() for t in e.get("tags", [])}]

    q_tokens = set(_tokens(query or ""))
    if not q_tokens:  # browse mode
        entries.sort(key=lambda e: (-e.get("stats", {}).get("installs", 0), e["id"]))
        return entries[:limit]

    results = []
    for e in entries:
        score = 0
        name_t = set(_tokens(e["name"] + " " + e["id"]))
        tag_t = set(_tokens(" ".join(e.get("tags", []))))
        desc_t = set(_tokens(e.get("one_liner", "") + " " + e.get("description", "")))
        score += 3 * len(q_tokens & name_t)
        score += 2 * len(q_tokens & tag_t)
        score += 1 * len(q_tokens & desc_t)
        if score > 0:
            results.append((score, e))
    results.sort(key=lambda r: (-r[0], r[1]["id"]))
    return [e for _, e in results[:limit]]


def summary(e: dict) -> dict:
    """Compact listing view used by search results."""
    return {
        "id": e["id"],
        "name": e["name"],
        "one_liner": e.get("one_liner", ""),
        "version": e["version"],
        "author": e.get("author", {}).get("name", "unknown"),
        "tags": e.get("tags", []),
        "price_usd": e.get("price_usd", 0),
        "scan_status": e.get("scan", {}).get("status", "unscanned"),
        "capabilities": e.get("capabilities", {}),
        "installs": e.get("stats", {}).get("installs", 0),
    }
