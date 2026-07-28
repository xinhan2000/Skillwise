"""Creator draft store — the owner-bound lifecycle behind the create-skill pipeline.

States: created → distilled → interviewed → drafted → evaluated → published.
The server validates every transition; the agent orchestrates but cannot skip
stages. Rules carry origin tags (article / interview / compiler-default) per
Protocol v3, and eval reports must be segmented.

Layout: <SKILLWISE_HOME>/drafts/<draft-id>/
  draft.json      meta: owner, state, source hash, timestamps
  source.txt      raw source snapshot (hashed at creation)
  ir.json         knowledge inventory (origin-tagged rules + ranked gaps)
  interview.json  questions + creator answers (mandatory stage)
  SKILL.md        the drafted skill
  eval_report.json  segmented self-eval (article/interview/holistic + fabrication)
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import time
from pathlib import Path

from . import config

STATES = ["created", "distilled", "interviewed", "drafted", "evaluated", "published"]
_ORDER = {s: i for i, s in enumerate(STATES)}
VALID_ORIGINS = {"article", "interview", "compiler-default"}

EVAL_REQUIRED_KEYS = ("status", "article_rules", "interview_rules", "holistic",
                      "fabrication_check")


class DraftError(Exception):
    """Raised on ownership, lifecycle, or validation violations."""


def drafts_dir() -> Path:
    return config.home() / "drafts"


def _dir(draft_id: str) -> Path:
    return drafts_dir() / draft_id


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_meta(draft_id: str) -> dict:
    p = _dir(draft_id) / "draft.json"
    if not p.exists():
        raise DraftError(f"No draft {draft_id!r}.")
    return json.loads(p.read_text(encoding="utf-8"))


def _save_meta(meta: dict) -> None:
    meta["updated_at"] = _now()
    (_dir(meta["id"]) / "draft.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")


def check_owner(meta: dict, user_id: str) -> None:
    if meta["owner"] != user_id:
        raise DraftError("This draft belongs to another account; only its owner "
                         "can view, modify, or publish it.")


def list_for(user_id: str) -> list[dict]:
    out = []
    if drafts_dir().is_dir():
        for d in sorted(drafts_dir().iterdir()):
            p = d / "draft.json"
            if p.exists():
                meta = json.loads(p.read_text(encoding="utf-8"))
                if meta.get("owner") == user_id:
                    out.append({"id": meta["id"], "state": meta["state"],
                                "source_url": meta["source"].get("url"),
                                "updated_at": meta["updated_at"]})
    return out


def create(owner: str, source_text: str, source_url: str | None = None) -> dict:
    if not source_text or len(source_text.strip()) < 200:
        raise DraftError("Source is too thin to compile (need at least ~200 chars "
                         "of substantive content).")
    config.ensure_dirs()
    draft_id = f"draft-{secrets.token_hex(4)}"
    d = _dir(draft_id)
    d.mkdir(parents=True)
    (d / "source.txt").write_text(source_text, encoding="utf-8")
    meta = {
        "id": draft_id,
        "owner": owner,
        "state": "created",
        "source": {
            "url": source_url,
            "sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "chars": len(source_text),
            "fetched_at": _now(),
        },
        "created_at": _now(),
        "updated_at": _now(),
    }
    _save_meta(meta)
    return meta


# ---------- artifact validation ----------

def _validate_ir(ir: dict) -> None:
    if not isinstance(ir, dict):
        raise DraftError("IR must be an object.")
    for key in ("task", "when_to_use", "procedure", "rules", "gaps"):
        if key not in ir:
            raise DraftError(f"IR missing required key {key!r}.")
    if not isinstance(ir["rules"], list) or not ir["rules"]:
        raise DraftError("IR 'rules' must be a non-empty list.")
    for r in ir["rules"]:
        if not isinstance(r, dict) or not r.get("text") or r.get("origin") not in VALID_ORIGINS:
            raise DraftError(
                "Every IR rule must be {'text': ..., 'origin': 'article' | "
                "'interview' | 'compiler-default'} — origin tags are mandatory "
                "(Protocol v3).")


def _validate_interview(iv: dict) -> None:
    qs = iv.get("questions") if isinstance(iv, dict) else None
    if not isinstance(qs, list) or not qs:
        raise DraftError("Interview must contain a non-empty 'questions' list.")
    answered = [q for q in qs
                if isinstance(q, dict) and str(q.get("answer", "")).strip()]
    if not answered:
        raise DraftError("The interview stage is mandatory: at least one question "
                         "must carry a creator answer ('no opinion, source stands' "
                         "is a valid answer; empty is not).")


def _validate_skill_md(text: str) -> None:
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text or "", re.DOTALL)
    if not m:
        raise DraftError("SKILL.md must start with YAML frontmatter (--- ... ---).")
    fm = m.group(1)
    if "name:" not in fm or "description:" not in fm:
        raise DraftError("SKILL.md frontmatter needs 'name' and 'description'.")


def _validate_eval(rep: dict) -> None:
    if not isinstance(rep, dict):
        raise DraftError("eval_report must be an object.")
    for key in EVAL_REQUIRED_KEYS:
        if key not in rep:
            raise DraftError(f"eval_report missing {key!r} — segmented reporting "
                             "(article_rules / interview_rules / holistic / "
                             "fabrication_check) is required by Protocol v3.")


# ---------- stage saves ----------

def save(draft_id: str, user_id: str, *, ir: dict | None = None,
         interview: dict | None = None, skill_md: str | None = None,
         eval_report: dict | None = None) -> dict:
    meta = load_meta(draft_id)
    check_owner(meta, user_id)
    if meta["state"] == "published":
        raise DraftError("Draft already published; start a new draft to revise.")
    if not any(x is not None for x in (ir, interview, skill_md, eval_report)):
        raise DraftError("Nothing to save: provide ir, interview, skill_md, or "
                         "eval_report.")

    d = _dir(draft_id)
    saved: list[str] = []

    def _advance(to_state: str) -> None:
        if _ORDER[meta["state"]] < _ORDER[to_state]:
            meta["state"] = to_state

    def _require_at_least(state: str, what: str) -> None:
        if _ORDER[meta["state"]] < _ORDER[state]:
            raise DraftError(f"Out of order: cannot save {what} while the draft "
                             f"is {meta['state']!r} — complete the earlier stages "
                             "first (the pipeline cannot skip steps).")

    if ir is not None:
        _validate_ir(ir)
        (d / "ir.json").write_text(json.dumps(ir, indent=2), encoding="utf-8")
        _advance("distilled")
        saved.append("ir")
    if interview is not None:
        _require_at_least("distilled", "the interview")
        _validate_interview(interview)
        (d / "interview.json").write_text(json.dumps(interview, indent=2),
                                          encoding="utf-8")
        _advance("interviewed")
        saved.append("interview")
    if skill_md is not None:
        _require_at_least("interviewed", "SKILL.md")
        _validate_skill_md(skill_md)
        (d / "SKILL.md").write_text(skill_md, encoding="utf-8")
        _advance("drafted")
        saved.append("skill_md")
    if eval_report is not None:
        _require_at_least("drafted", "the eval report")
        _validate_eval(eval_report)
        (d / "eval_report.json").write_text(json.dumps(eval_report, indent=2),
                                            encoding="utf-8")
        _advance("evaluated")
        saved.append("eval_report")

    _save_meta(meta)
    return {"state": meta["state"], "saved": saved}


# ---------- publish ----------

def prepare_publish(draft_id: str, user_id: str) -> tuple[dict, str, dict]:
    """Validate the full lifecycle and return (meta, skill_md, extra_entry_fields).

    The caller (server) hands the package to ingest.publish() — the single
    door into the catalog stays single.
    """
    meta = load_meta(draft_id)
    check_owner(meta, user_id)
    if meta["state"] == "published":
        raise DraftError("Draft already published.")
    if meta["state"] != "evaluated":
        raise DraftError(f"Draft is {meta['state']!r}; it must complete the full "
                         "lifecycle (distill → interview → draft → evaluate) "
                         "before publishing.")
    d = _dir(draft_id)
    rep = json.loads((d / "eval_report.json").read_text(encoding="utf-8"))
    if rep.get("status") != "pass":
        raise DraftError("The eval report status is not 'pass' — a failed or "
                         "pending eval cannot be published. Improve the skill "
                         "and re-run the eval.")
    if rep.get("fabrication_check") != "pass":
        raise DraftError("Fabrication check did not pass — outputs containing "
                         "invented facts cannot be published (Protocol v3 §3).")
    skill_md = (d / "SKILL.md").read_text(encoding="utf-8")
    extra = {
        "provenance": {
            "draft_id": draft_id,
            "source_url": meta["source"].get("url"),
            "source_sha256": meta["source"]["sha256"],
            "compiler": "skillwise-create/0.1",
            "interviewed": True,
            "owner": meta["owner"],
        },
        "eval": {
            "status": rep["status"],
            "article_rules": rep["article_rules"],
            "interview_rules": rep["interview_rules"],
            "holistic": rep["holistic"],
            "fabrication_check": rep["fabrication_check"],
            "method": rep.get("method", "self-eval v0 (in-session); independent "
                                        "server-side eval arrives in Phase 1"),
            "evaluated_at": meta["updated_at"],
        },
    }
    return meta, skill_md, extra


def mark_published(draft_id: str, skill_id: str, version: str) -> None:
    meta = load_meta(draft_id)
    meta["state"] = "published"
    meta["published"] = {"skill_id": skill_id, "version": version, "at": _now()}
    _save_meta(meta)
