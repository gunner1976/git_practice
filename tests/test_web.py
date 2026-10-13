from fastapi.testclient import TestClient

from casingdesign.web.app import app

client = TestClient(app)


def test_index_and_catalog():
    assert client.get("/").status_code == 200
    cat = client.get("/api/catalog").json()
    assert "L-80" in cat["grades"] and cat["pipes"]


def test_evaluate_roundtrip():
    well = client.get("/api/example").json()
    body = {"well": well, "specs": [
        {"string": "Production", "od": 5.5, "weight": 20.0, "grade": "P-110"}]}
    r = client.post("/api/evaluate", json=body)
    assert r.status_code == 200, r.text
    res = r.json()["results"][0]
    assert res["pass"] is True
    assert {c["check"] for c in res["checks"]} == {"burst", "collapse", "tension", "triaxial"}
    assert len(res["cases"]) >= 5 and len(res["cases"][0]["axial"]) == len(res["cases"][0]["md"])


def test_optimize_and_bad_spec():
    well = client.get("/api/example").json()
    r = client.post("/api/optimize", json={"well": well, "strings": ["Surface"], "top": 2})
    assert r.status_code == 200 and len(r.json()["candidates"]["Surface"]) == 2
    bad = client.post("/api/evaluate", json={"well": well, "specs": [
        {"string": "Nope", "od": 5.5, "weight": 20.0, "grade": "P-110"}]})
    assert bad.status_code == 400


def test_evaluate_with_sections_and_tapered_optimize():
    well = client.get("/api/example").json()
    body = {"well": well, "specs": [{"string": "Production", "od": 5.5, "sections": [
        {"top_md": 0, "bottom_md": 9000, "weight": 17.0, "grade": "P-110"},
        {"top_md": 9000, "bottom_md": 18000, "weight": 15.5, "grade": "P-110"}]}]}
    r = client.post("/api/evaluate", json=body)
    assert r.status_code == 200, r.text
    res = r.json()["results"][0]
    assert res["design"]["uniform"] is False and len(res["design"]["sections"]) == 2
    o = client.post("/api/optimize", json={"well": well, "strings": ["Intermediate"], "top": 1})
    c = o.json()["candidates"]["Intermediate"]
    assert c[0].get("tapered") is True and c[0]["cost_per_ft"] < c[1]["cost_per_ft"]
