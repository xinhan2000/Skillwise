"""REST API used by HttpBackend (and future hosted clients)."""

import pytest
from fastapi.testclient import TestClient

from skillwise.ingest import publish
from skillwise.site.app import app


@pytest.fixture()
def api(sw_home, make_skill):
    publish(make_skill(name="Invoice Generator",
                       description="Generate professional PDF invoices from plain-text order details."))
    return TestClient(app)


def test_api_search_anonymous(api):
    r = api.get("/api/skills", params={"q": "invoice"})
    assert r.status_code == 200
    assert r.json()["results"][0]["id"] == "invoice-generator"


def test_api_get_and_404(api):
    assert api.get("/api/skills/invoice-generator").json()["version"] == "1.0.0"
    assert api.get("/api/skills/nope").status_code == 404


def test_api_install_requires_token(api):
    r = api.post("/api/skills/invoice-generator/install")
    assert r.status_code == 401


def test_api_register_then_install(api):
    token = api.post("/api/register", json={"name": "xin"}).json()["token"]
    r = api.post("/api/skills/invoice-generator/install",
                 headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert "SKILL.md" in body["files"] and body["version"] == "1.0.0"
