"""Ingest pipeline: validate -> lint -> hash -> publish.

Single path into the catalog, shared by the web upload form and the CLI.
"""

from __future__ import annotations

import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from . import catalog, config
from .lint import scan_package

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_ID_OK = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")


class IngestError(Exception):
    pass


@dataclass
class IngestResult:
    skill_id: str
    version: str
    sha256: str
    scan: dict
    published: bool
    message: str


def _parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = _FRONTMATTER.match(text)
    if not m:
        raise IngestError("SKILL.md must start with YAML frontmatter (--- ... ---).")
    meta: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("'\"")
    if not meta.get("name"):
        raise IngestError("Frontmatter must include a `name` field.")
    if not meta.get("description") or len(meta["description"]) < 20:
        raise IngestError("Frontmatter must include a `description` of at least 20 characters "
                          "(it is how agents decide when to use the skill).")
    return meta


def _validate_structure(package_dir: Path) -> Path:
    skill_md = package_dir / "SKILL.md"
    if not skill_md.exists():
        raise IngestError("Package must contain a SKILL.md at its root.")
    total = 0
    for p in package_dir.rglob("*"):
        if p.is_file():
            size = p.stat().st_size
            if size > config.MAX_FILE_BYTES:
                raise IngestError(f"File too large (> {config.MAX_FILE_BYTES // 1024 // 1024} MB): {p.name}")
            total += size
    if total > config.MAX_PACKAGE_BYTES:
        raise IngestError(f"Package too large (> {config.MAX_PACKAGE_BYTES // 1024 // 1024} MB total).")
    return skill_md


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:64]
    if not _ID_OK.match(slug or ""):
        raise IngestError(f"Cannot derive a valid skill id from name {name!r}.")
    return slug


def publish(package_dir: Path, *, author_name: str = "local", version: str | None = None,
            tags: list[str] | None = None, price_usd: float = 0.0,
            license_name: str = "Skillwise-Open-v0",
            extra: dict | None = None) -> IngestResult:
    """Run the full pipeline. Raises IngestError on validation/scan hard-fail."""
    package_dir = Path(package_dir)
    if not package_dir.is_dir():
        raise IngestError(f"Not a directory: {package_dir}")

    # 1. validate
    skill_md = _validate_structure(package_dir)
    meta = _parse_frontmatter(skill_md)
    skill_id = _slug(meta["name"])

    # 2. lint
    report, caps = scan_package(package_dir)
    if report.status == "fail":
        fails = [f for f in report.findings if f.level == "fail"]
        detail = "; ".join(f"[{f.check}] {f.file}:{f.line} {f.reason}" for f in fails[:5])
        raise IngestError(f"Security scan failed ({len(fails)} blocking finding(s)): {detail}")

    # 3. version + hash
    existing = catalog.get_entry(skill_id)
    if version is None:
        if existing:
            major, minor, patch = (existing["version"].split(".") + ["0", "0"])[:3]
            version = f"{major}.{int(minor) + 1}.0"
        else:
            version = "1.0.0"
    dest = catalog.version_dir(skill_id, version)
    if dest.exists():
        raise IngestError(f"Version {version} of {skill_id} already exists (versions are immutable).")

    # 4. copy package
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_dir, dest, ignore=shutil.ignore_patterns("_meta", "__pycache__", ".git"))
    sha256 = catalog.canonical_hash(dest)

    # 5. write metadata
    meta_dir = dest / "_meta"
    meta_dir.mkdir(exist_ok=True)
    import json
    (meta_dir / "scan.json").write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    (meta_dir / "package.sha256").write_text(sha256 + "\n", encoding="utf-8")

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    body = skill_md.read_text(encoding="utf-8", errors="replace")
    description_md = _FRONTMATTER.sub("", body).strip()

    entry = {
        "id": skill_id,
        "name": meta["name"],
        "one_liner": meta["description"][:160],
        "description": description_md[:4000],
        "version": version,
        "author": {"id": _slug(author_name), "name": author_name, "verified": False},
        "license": license_name,
        "tags": tags or [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "price_usd": price_usd,
        "sha256": sha256,
        "scan": report.to_dict(),
        "capabilities": caps,
        "created_at": existing["created_at"] if existing else now,
        "updated_at": now,
        "stats": existing.get("stats", {}) if existing else {"installs": 0, "loads": 0},
    }
    if extra:
        # Only whitelisted blocks may ride along (provenance/eval from the
        # creator draft pipeline); everything else stays ingest-controlled.
        entry.update({k: v for k, v in extra.items() if k in ("provenance", "eval")})

    catalog.upsert_entry(entry)
    catalog.append_publish_log(skill_id, version, sha256)

    status_note = "clean" if report.status == "pass" else f"published with {len(report.findings)} warning(s)"
    return IngestResult(skill_id, version, sha256, report.to_dict(), True,
                        f"Published {skill_id} v{version} ({status_note}).")
