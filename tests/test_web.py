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
