"""End-user CLI: add / list / pause / resume / remove, prompt-once auth."""

import argparse

import pytest

from skillwise import user_cli, userstate
from skillwise.ingest import publish


@pytest.fixture()
def user_home(tmp_path, monkeypatch):
    """Isolated ~/.skillwise and install dir per test."""
    monkeypatch.setenv("SKILLWISE_USER_DIR", str(tmp_path / "userdir"))
    userstate.save_config({"install_dir": str(tmp_path / "agent-skills")})
    return tmp_path


def _seeded(make_skill):
    publish(make_skill(name="Invoice Generator",
                       description="Generate professional PDF invoices from plain-text order details."))


def _args(**kw):
    return argparse.Namespace(**kw)


def _install(monkeypatch, answers):
    it = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))
    user_cli.cmd_add(_args(skill_id="invoice-generator", yes=False))


def test_add_prompts_once_and_installs(sw_home, user_home, make_skill, monkeypatch, capsys):
    _seeded(make_skill)
    _install(monkeypatch, answers=["y", "xin"])  # confirm install, then register name
    cfg = userstate.load_config()
    assert cfg["token"].startswith("swk_")
    assert (userstate.install_dir(cfg) / "invoice-generator" / "SKILL.md").exists()
    assert userstate.load_manifest()["invoice-generator"]["paused"] is False

    # second add of another skill must NOT prompt for registration again
    publish(make_skill(name="Second Skill"))
    answers = iter(["y"])  # only the install confirmation
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    user_cli.cmd_add(_args(skill_id="second-skill", yes=False))
    assert (userstate.install_dir(cfg) / "second-skill").exists()


def test_search_needs_no_registration(sw_home, user_home, make_skill, capsys):
    _seeded(make_skill)
    user_cli.cmd_search(_args(query="invoice", limit=10))
    out = capsys.readouterr().out
    assert "invoice-generator" in out
    assert "token" not in userstate.load_config()


def test_pause_resume_moves_folder(sw_home, user_home, make_skill, monkeypatch):
    _seeded(make_skill)
    _install(monkeypatch, answers=["y", "xin"])
    cfg = userstate.load_config()
    active = userstate.install_dir(cfg) / "invoice-generator"
    paused = userstate.paused_dir(cfg) / "invoice-generator"

    user_cli.cmd_pause(_args(skill_id="invoice-generator"))
    assert paused.exists() and not active.exists()
    assert userstate.load_manifest()["invoice-generator"]["paused"] is True

    user_cli.cmd_resume(_args(skill_id="invoice-generator"))
    assert active.exists() and not paused.exists()
    assert userstate.load_manifest()["invoice-generator"]["paused"] is False


def test_remove_deletes_even_when_paused(sw_home, user_home, make_skill, monkeypatch):
    _seeded(make_skill)
    _install(monkeypatch, answers=["y", "xin"])
    user_cli.cmd_pause(_args(skill_id="invoice-generator"))
    user_cli.cmd_remove(_args(skill_id="invoice-generator"))
    cfg = userstate.load_config()
    assert not (userstate.install_dir(cfg) / "invoice-generator").exists()
    assert not (userstate.paused_dir(cfg) / "invoice-generator").exists()
    assert "invoice-generator" not in userstate.load_manifest()


def test_pause_unknown_skill_fails(sw_home, user_home):
    with pytest.raises(SystemExit):
        user_cli.cmd_pause(_args(skill_id="never-installed"))


def test_add_without_tty_fails_cleanly_with_hint(sw_home, user_home, make_skill, monkeypatch, capsys):
    _seeded(make_skill)

    def _eof(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", _eof)
    with pytest.raises(SystemExit):
        user_cli.cmd_add(_args(skill_id="invoice-generator", yes=False))
    err = capsys.readouterr().err
    assert "-y" in err  # actionable hint, not a traceback


def test_registration_without_tty_fails_cleanly(sw_home, user_home, make_skill, monkeypatch, capsys):
    _seeded(make_skill)

    def _eof(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", _eof)
    with pytest.raises(SystemExit):
        user_cli.cmd_add(_args(skill_id="invoice-generator", yes=True))
    assert "skillwise login" in capsys.readouterr().err
