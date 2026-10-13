"""FastAPI application: JSON API plus a single-page UI.

    uvicorn casingdesign.web.app:app --reload
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from casingdesign.catalog import Catalog
from casingdesign.design import evaluate_string, optimize_string
from casingdesign.design.evaluate import _axial_for
from casingdesign.examples import onshore_horizontal_well
from casingdesign.loads.cases import standard_load_cases
from casingdesign.web.serialize import result_dict, spec_dict
from casingdesign.well import Well

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="casingdesign", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
catalog = Catalog.default()


class SpecChoice(BaseModel):
    string: str
    od: float
    weight: float
    grade: str
    connection: str = "BTC"


class EvaluateRequest(BaseModel):
    well: Well
    specs: list[SpecChoice]


class OptimizeRequest(BaseModel):
    well: Well
    strings: list[str] | None = None
    connection: str = "BTC"
    top: int = 5


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/example")
def example() -> dict:
    return onshore_horizontal_well().model_dump()


@app.get("/api/catalog")
def get_catalog() -> dict:
    return {
        "grades": [g.name for g in catalog.grades.values()],
        "connections": [c.name for c in catalog.connections.values()],
        "pipes": [{"od": p.od, "weight": p.nominal_weight, "wall": p.wall, "id": p.id}
                  for p in catalog.pipes],
    }


@app.post("/api/evaluate")
def evaluate(req: EvaluateRequest) -> dict:
    out = []
    for ch in req.specs:
        try:
            s = req.well.string(ch.string)
            spec = catalog.spec(ch.od, ch.weight, ch.grade, ch.connection)
        except KeyError as e:
            raise HTTPException(400, f"unknown string or pipe: {e}") from e
        cases = standard_load_cases(req.well, s)
        r = evaluate_string(req.well, s, spec, cases)
        axial = {c.name: _axial_for(c, req.well, s, spec) for c in cases}
        out.append(result_dict(r, cases, axial))
    return {"well": req.well.name, "results": out}


@app.post("/api/optimize")
def optimize(req: OptimizeRequest) -> dict:
    targets = ([req.well.string(n) for n in req.strings] if req.strings else req.well.strings)
    out = {}
    for s in targets:
        cands = optimize_string(req.well, s, catalog, connection=req.connection,
                                max_results=req.top)
        out[s.name] = [{"spec": spec_dict(c.spec), "cost_per_ft": c.cost_per_ft,
                        "summary": c.result.summary} for c in cands]
    return {"well": req.well.name, "candidates": out}
