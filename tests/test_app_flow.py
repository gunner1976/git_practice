"""Project store and the one-click design endpoint."""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    tmp = tempfile.mkdtemp()
    monkeypatch.setenv("CASINGDESIGN_DB", os.path.join(tmp, "t.db"))
    import importlib

    import casingdesign.web.app as appmod
    importlib.reload(appmod)
    return TestClient(appmod.app)


def test_project_crud_and_report(client):
    assert client.get("/api/projects").json() == []
    p = client.post("/api/projects", json={}).json()
    assert p["name"] and len(p["well"]["strings"]) == 3
    lst = client.get("/api/projects").json()
    assert lst[0]["id"] == p["id"] and lst[0]["strings"] == 3
    p2 = client.put(f"/api/projects/{p['id']}", json={"name": "Renamed",
                                                     "design": {"Production": {"weight": 20.0, "grade": "P-110"}}}).json()
    assert p2["name"] == "Renamed" and p2["design"]["Production"]["grade"] == "P-110"
    rep = client.get(f"/report/{p['id']}")
    assert rep.status_code == 200 and "Casing design report" in rep.text and "PASS" in rep.text
    assert client.delete(f"/api/projects/{p['id']}").json()["deleted"] == p["id"]
    assert client.get(f"/api/projects/{p['id']}").status_code == 404
    assert client.get("/report/nope").status_code == 404


def test_design_endpoint_recommends_and_respects_overrides(client):
    well = client.get("/api/example").json()
    d = client.post("/api/design", json={"well": well}).json()
    assert [s["string"] for s in d["strings"]] == ["Surface", "Intermediate", "Production"]
    inter = next(s for s in d["strings"] if s["string"] == "Intermediate")
    assert inter["recommended"]["kind"] == "tapered" and inter["result"]["pass"]
    assert not inter["overridden"] and len(inter["alternatives"]) == 3
    d2 = client.post("/api/design", json={"well": well, "choices": {
        "Intermediate": {"weight": 40.0, "grade": "L-80"}}}).json()
    inter2 = next(s for s in d2["strings"] if s["string"] == "Intermediate")
    assert inter2["overridden"] and not inter2["result"]["pass"]
    bad = client.post("/api/design", json={"well": well, "choices": {"Intermediate": {"weight": 99, "grade": "L-80"}}})
    assert bad.status_code == 400


def test_index_serves_app_and_legacy(client):
    assert "app.js" in client.get("/").text
    assert client.get("/legacy").status_code == 200


def test_design_respects_grade_preferences(client):
    well = client.get("/api/example").json()
    d = client.post("/api/design", json={"well": well}).json()
    assert "H-40" in d["strings"][0]["recommended"]["design"]["label"]
    d2 = client.post("/api/design", json={"well": well, "grades": ["J-55", "L-80", "P-110"]}).json()
    assert "H-40" not in d2["strings"][0]["recommended"]["design"]["label"]
    well["prefs"] = {"grades": ["P-110"]}
    d3 = client.post("/api/design", json={"well": well}).json()
    assert all("P-110" in sec["spec"]["grade"] for s in d3["strings"] for sec in s["result"]["design"]["sections"])


def test_drafts_save_but_design_refuses_invalid(client):
    well = client.get("/api/example").json()
    well["strings"][1]["toc_md"] = 9000  # below the 8500 ft shoe
    p = client.post("/api/projects", json={"name": "draft", "well": well})
    assert p.status_code == 200  # a draft always saves
    r = client.post("/api/design", json={"well": well})
    assert r.status_code == 400 and "top of cement" in r.json()["detail"]
    assert client.get(f"/report/{p.json()['id']}").status_code == 400
