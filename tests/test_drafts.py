"""Creator draft pipeline: lifecycle, ownership, gating, provenance."""

import pytest

from skillwise import auth, catalog, drafts, server

SOURCE = ("How to write great release notes. Step one: lead with user impact, "
          "never with ticket numbers. Step two: group changes by outcome. "
          "Step three: every breaking change gets a migration note. Never use "
          "internal jargon. Example: 'Exports now finish 3x faster' beats "
          "'Optimized the export pipeline worker pool.' Keep it under a page.")

IR = {
    "task": "Write user-facing release notes",
    "when_to_use": ["release notes", "changelog requests"],
    "procedure": ["lead with user impact", "group by outcome", "flag breaking changes"],
    "rules": [
        {"text": "Lead with user impact, never ticket numbers", "origin": "article"},
        {"text": "Every breaking change gets a migration note", "origin": "article"},
        {"text": "Ask for the audience before drafting", "origin": "interview"},
        {"text": "Default length: one page", "origin": "compiler-default"},
    ],
    "gaps": [{"gap": "audience calibration", "impact": "high"}],
}

INTERVIEW = {"questions": [
    {"question": "Who is the audience?", "gap": "audience calibration",
     "answer": "Default to end users; engineers get a separate appendix."},
]}

SKILL_MD = ("---\nname: Release Notes Pro\ndescription: Write user-facing release "
            "notes that lead with impact, group by outcome, and flag breaking "
            "changes with migration notes. Use when the user asks for release "
            "notes or a changelog.\ntags: writing, releases\n---\n\n# Release "
            "Notes Pro\n\nLead with user impact. [origin: article]\n")

EVAL_PASS = {"status": "pass", "article_rules": "4/4", "interview_rules": "2/2",
             "holistic": "preferred in 3/3 cases", "fabrication_check": "pass",
             "cases": 4}


@pytest.fixture()
def creator(sw_home, monkeypatch):
    token = auth.create_token("casey")
    monkeypatch.setenv("SKILLWISE_TOKEN", token)
    return "casey"


def _run_to(state, draft_id):
    if state in ("distilled", "interviewed", "drafted", "evaluated"):
        server.save_draft(draft_id, ir=IR)
    if state in ("interviewed", "drafted", "evaluated"):
        server.save_draft(draft_id, interview=INTERVIEW)
    if state in ("drafted", "evaluated"):
        server.save_draft(draft_id, skill_md=SKILL_MD)
    if state == "evaluated":
        server.save_draft(draft_id, eval_report=EVAL_PASS)


def test_full_lifecycle_publishes_with_provenance_and_eval(creator):
    out = server.start_skill_draft(source_text=SOURCE)
    draft_id = out["draft_id"]
    assert out["state"] == "created" and len(out["source_sha256"]) == 64

    _run_to("evaluated", draft_id)
    result = server.publish_draft(draft_id)
    assert result.get("error") is None
    entry = catalog.get_entry(result["skill_id"])
    assert entry["provenance"]["source_sha256"] == out["source_sha256"]
    assert entry["provenance"]["owner"] == "casey"
    assert entry["eval"]["status"] == "pass"
    assert entry["eval"]["interview_rules"] == "2/2"
    assert drafts.load_meta(draft_id)["state"] == "published"


def test_draft_requires_registration(sw_home, monkeypatch):
    monkeypatch.delenv("SKILLWISE_TOKEN", raising=False)
    out = server.start_skill_draft(source_text=SOURCE)
    assert out["error"] == "registration_required"


def test_only_owner_can_save_and_publish(creator, monkeypatch):
    draft_id = server.start_skill_draft(source_text=SOURCE)["draft_id"]
    other = auth.create_token("mallory")
    monkeypatch.setenv("SKILLWISE_TOKEN", other)
    assert "another account" in server.save_draft(draft_id, ir=IR)["error"]
    assert "another account" in server.publish_draft(draft_id)["error"]


def test_stages_cannot_be_skipped(creator):
    draft_id = server.start_skill_draft(source_text=SOURCE)["draft_id"]
    out = server.save_draft(draft_id, skill_md=SKILL_MD)
    assert "Out of order" in out["error"]
    out = server.publish_draft(draft_id)
    assert "lifecycle" in out["error"]


def test_interview_is_mandatory_and_must_be_answered(creator):
    draft_id = server.start_skill_draft(source_text=SOURCE)["draft_id"]
    server.save_draft(draft_id, ir=IR)
    out = server.save_draft(draft_id, interview={"questions": [
        {"question": "Audience?", "answer": "   "}]})
    assert "mandatory" in out["error"]


def test_origin_tags_are_enforced(creator):
    draft_id = server.start_skill_draft(source_text=SOURCE)["draft_id"]
    bad_ir = dict(IR, rules=[{"text": "untagged rule", "origin": "vibes"}])
    out = server.save_draft(draft_id, ir=bad_ir)
    assert "origin" in out["error"]


def test_failed_eval_blocks_publish(creator):
    draft_id = server.start_skill_draft(source_text=SOURCE)["draft_id"]
    _run_to("drafted", draft_id)
    server.save_draft(draft_id, eval_report=dict(EVAL_PASS, status="fail"))
    out = server.publish_draft(draft_id)
    assert "not 'pass'" in out["error"]


def test_fabrication_failure_blocks_publish(creator):
    draft_id = server.start_skill_draft(source_text=SOURCE)["draft_id"]
    _run_to("drafted", draft_id)
    server.save_draft(draft_id, eval_report=dict(EVAL_PASS, fabrication_check="fail"))
    out = server.publish_draft(draft_id)
    assert "Fabrication" in out["error"]


def test_list_drafts_shows_only_own(creator, monkeypatch):
    mine = server.start_skill_draft(source_text=SOURCE)["draft_id"]
    other_token = auth.create_token("mallory")
    monkeypatch.setenv("SKILLWISE_TOKEN", other_token)
    server.start_skill_draft(source_text=SOURCE)
    theirs = server.list_drafts()["drafts"]
    assert all(d["id"] != mine for d in theirs) and len(theirs) == 1
