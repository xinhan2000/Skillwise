"""Exercise the MCP tool functions directly (no client needed)."""

from skillwise import auth, server
from skillwise.ingest import publish


def _seed(make_skill):
    publish(make_skill(name="Invoice Generator",
                       description="Generate professional PDF invoices from plain-text order details."),
            author_name="Tester")


def test_search_anonymous(sw_home, make_skill):
    _seed(make_skill)
    out = server.search_skills("invoice")
    assert out["results"] and out["results"][0]["id"] == "invoice-generator"


def test_search_no_results_suggests_gap_report(sw_home):
    out = server.search_skills("quantum basket weaving")
    assert out["results"] == []
    assert "report_gap" in out["note"]


def test_install_requires_token(sw_home, make_skill, monkeypatch):
    _seed(make_skill)
    monkeypatch.delenv("SKILLWISE_TOKEN", raising=False)
    out = server.install_skill("invoice-generator")
    assert out["error"] == "registration_required"
    assert "skillwise token create" in out["how_to_fix"]


def test_install_with_token(sw_home, make_skill, monkeypatch):
    _seed(make_skill)
    token = auth.create_token("xin")
    monkeypatch.setenv("SKILLWISE_TOKEN", token)
    out = server.install_skill("invoice-generator")
    assert "files" in out and "SKILL.md" in out["files"]
    assert out["install_dir"].endswith("/invoice-generator")

    ents = server.list_entitlements()
    assert ents["user_id"] == "xin"
    assert any(e["skill_id"] == "invoice-generator" for e in ents["entitlements"])


def test_use_skill_now_streams_content(sw_home, make_skill, monkeypatch):
    _seed(make_skill)
    token = auth.create_token("xin")
    monkeypatch.setenv("SKILLWISE_TOKEN", token)
    out = server.use_skill_now("invoice-generator")
    assert "skill_instructions" in out and "Invoice" in out["skill_instructions"]
