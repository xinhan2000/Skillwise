import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


@pytest.fixture()
def sw_home(tmp_path, monkeypatch):
    """Isolated SKILLWISE_HOME per test."""
    monkeypatch.setenv("SKILLWISE_HOME", str(tmp_path))
    return tmp_path


@pytest.fixture()
def make_skill(tmp_path):
    """Factory: create a skill source folder."""
    def _make(name="Test Skill", description=None, extra_files=None, body="# Test\nDo the thing well."):
        description = description or "A test skill that does a very specific useful thing for testing."
        src = tmp_path / "src-skills" / name.lower().replace(" ", "-")
        src.mkdir(parents=True, exist_ok=True)
        (src / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\ntags: test, sample\n---\n\n{body}\n",
            encoding="utf-8")
        for rel, content in (extra_files or {}).items():
            p = src / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                p.write_bytes(content)
            else:
                p.write_text(content, encoding="utf-8")
        return src
    return _make
