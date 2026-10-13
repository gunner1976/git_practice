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
from casingdesign.design import (
    Section,
    StringDesign,
    evaluate_design,
    optimize_string,
    optimize_tapered,
)
from casingdesign.design.evaluate import _axial_for
from casingdesign.examples import onshore_horizontal_well
from casingdesign.loads.cases import standard_load_cases
from casingdesign.web.serialize import design_dict, result_dict, spec_dict
from casingdesign.well import Well

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="casingdesign", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
catalog = Catalog.default()


class SectionChoice(BaseModel):
    top_md: float
    bottom_md: float
    weight: float
    grade: str
    connection: str = "BTC"


class SpecChoice(BaseModel):
    """A uniform pipe (weight/grade) or an explicit list of sections for a string."""

    string: str
    od: float
    weight: float | None = None
    grade: str | None = None
    connection: str = "BTC"
    sections: list[SectionChoice] | None = None


class EvaluateRequest(BaseModel):
    well: Well
    specs: list[SpecChoice]


class OptimizeRequest(BaseModel):
    well: Well
    strings: list[str] | None = None
    connection: str = "BTC"
    top: int = 5
    tapered: bool = True
    max_sections: int = 3
    min_section_length: float = 500.0


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
            if ch.sections:
                design = StringDesign(tuple(
                    Section(sec.top_md, sec.bottom_md,
                            catalog.spec(ch.od, sec.weight, sec.grade, sec.connection))
                    for sec in ch.sections))
            else:
                if ch.weight is None or ch.grade is None:
                    raise HTTPException(400, f"{ch.string}: give weight/grade or sections")
                design = StringDesign.uniform(
                    s.hanger_md, s.shoe_md, catalog.spec(ch.od, ch.weight, ch.grade, ch.connection))
        except KeyError as e:
            raise HTTPException(400, f"unknown string or pipe: {e}") from e
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
        cases = standard_load_cases(req.well, s, inner_diameter=design.sections[0].spec.pipe.id)
        r = evaluate_design(req.well, s, design, cases)
        axial = {c.name: _axial_for(c, req.well, s, design) for c in cases}
        out.append(result_dict(r, cases, axial, req.well))
    return {"well": req.well.name, "results": out}


@app.post("/api/optimize")
def optimize(req: OptimizeRequest) -> dict:
    targets = ([req.well.string(n) for n in req.strings] if req.strings else req.well.strings)
    out = {}
    for s in targets:
        cands = optimize_string(req.well, s, catalog, connection=req.connection,
                                max_results=req.top)
        out[s.name] = [{"spec": spec_dict(c.spec), "design": design_dict(c.design),
                        "cost_per_ft": c.cost_per_ft, "summary": c.result.summary}
                       for c in cands]
        if req.tapered:
            t = optimize_tapered(req.well, s, catalog, connection=req.connection,
                                 max_sections=req.max_sections,
                                 min_section_length=req.min_section_length)
            if t is not None and not t.design.is_uniform:
                out[s.name].insert(0, {"spec": spec_dict(t.spec), "design": design_dict(t.design),
                                       "cost_per_ft": t.cost_per_ft, "summary": t.result.summary,
                                       "tapered": True})
    return {"well": req.well.name, "candidates": out}
