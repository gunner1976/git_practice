"""FastAPI application: JSON API plus a single-page UI.

    uvicorn casingdesign.web.app:app --reload
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
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
from casingdesign.examples import onshore_horizontal_well, onshore_liner_well
from casingdesign.loads.cases import standard_load_cases
from casingdesign.web.serialize import design_dict, result_dict, spec_dict
from casingdesign.web.store import ProjectStore
from casingdesign.well import Well

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="casingdesign", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
catalog = Catalog.default()
store = ProjectStore()


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


@app.get("/legacy")
def legacy():
    return FileResponse(STATIC / "legacy.html")


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
class ProjectIn(BaseModel):
    name: str | None = None
    well: Well | None = None
    design: dict | None = None  # string name -> SpecChoice-like dict (uniform or sections)


@app.get("/api/projects")
def list_projects() -> list[dict]:
    return store.list()


@app.post("/api/projects")
def create_project(body: ProjectIn) -> dict:
    well = body.well or onshore_horizontal_well()
    return store.create(body.name or well.name, well.model_dump(), body.design)


@app.get("/api/projects/{pid}")
def get_project(pid: str) -> dict:
    p = store.get(pid)
    if p is None:
        raise HTTPException(404, "no such project")
    return p


@app.put("/api/projects/{pid}")
def update_project(pid: str, body: ProjectIn) -> dict:
    p = store.update(pid, body.name, body.well.model_dump() if body.well else None, body.design)
    if p is None:
        raise HTTPException(404, "no such project")
    return p


@app.delete("/api/projects/{pid}")
def delete_project(pid: str) -> dict:
    if not store.delete(pid):
        raise HTTPException(404, "no such project")
    return {"deleted": pid}


# ---------------------------------------------------------------------------
# One-shot design: optimise every string, evaluate the chosen/recommended pipe
# ---------------------------------------------------------------------------
class DesignRequest(BaseModel):
    well: Well
    choices: dict[str, dict] | None = None  # overrides per string (SpecChoice fields)
    connection: str = "BTC"
    tapered: bool = True
    max_sections: int = 3


def _design_from_choice(s, ch: dict) -> StringDesign:
    if ch.get("sections"):
        return StringDesign(tuple(
            Section(sec["top_md"], sec["bottom_md"],
                    catalog.spec(s.od, sec["weight"], sec["grade"], sec.get("connection", "BTC")))
            for sec in ch["sections"]))
    return StringDesign.uniform(s.hanger_md, s.shoe_md,
                                catalog.spec(s.od, ch["weight"], ch["grade"],
                                             ch.get("connection", "BTC")))


@app.post("/api/design")
def design(req: DesignRequest) -> dict:
    """For each string: the cheapest passing uniform pipe, the cheapest tapered design,
    and a full evaluation of the chosen pipe (user override, else recommendation)."""
    out = []
    choices = req.choices or {}
    for s in req.well.strings:
        uniform = optimize_string(req.well, s, catalog, connection=req.connection, max_results=3)
        tapered = (optimize_tapered(req.well, s, catalog, connection=req.connection,
                                    max_sections=req.max_sections) if req.tapered else None)
        rec = None
        if tapered is not None and (not uniform or tapered.cost_per_ft < uniform[0].cost_per_ft - 1e-9):
            rec = {"kind": "tapered", "design": design_dict(tapered.design),
                   "cost_per_ft": tapered.cost_per_ft, "summary": tapered.result.summary}
        elif uniform:
            rec = {"kind": "uniform", "design": design_dict(uniform[0].design),
                   "cost_per_ft": uniform[0].cost_per_ft, "summary": uniform[0].result.summary}
        # What to evaluate in full: the user's choice if given, else the recommendation.
        ch = choices.get(s.name)
        try:
            if ch:
                dsg = _design_from_choice(s, ch)
            elif tapered is not None and rec and rec["kind"] == "tapered":
                dsg = tapered.design
            elif uniform:
                dsg = uniform[0].design
            else:
                dsg = None
        except (KeyError, ValueError) as e:
            raise HTTPException(400, f"{s.name}: {e}") from e
        result = None
        if dsg is not None:
            cases = standard_load_cases(req.well, s, inner_diameter=dsg.sections[0].spec.pipe.id)
            r = evaluate_design(req.well, s, dsg, cases)
            axial = {c.name: _axial_for(c, req.well, s, dsg) for c in cases}
            result = result_dict(r, cases, axial, req.well)
        out.append({
            "string": s.name, "od": s.od, "top_md": s.hanger_md, "shoe_md": s.shoe_md,
            "recommended": rec, "overridden": bool(ch),
            "alternatives": [{"design": design_dict(c.design), "cost_per_ft": c.cost_per_ft,
                              "summary": c.result.summary} for c in uniform],
            "result": result,
        })
    return {"well": req.well.name, "strings": out, "warnings": req.well.warnings()}


# ---------------------------------------------------------------------------
# Printable report
# ---------------------------------------------------------------------------
@app.get("/report/{pid}", response_class=HTMLResponse)
def report(pid: str) -> str:
    from casingdesign.web.report import render_report
    p = store.get(pid)
    if p is None:
        raise HTTPException(404, "no such project")
    well = Well.model_validate(p["well"])
    data = design(DesignRequest(well=well, choices=p.get("design") or None))
    return render_report(p, well, data)


EXAMPLES = {"horizontal": onshore_horizontal_well, "liner": onshore_liner_well}


@app.get("/api/example")
def example(name: str = "horizontal") -> dict:
    if name not in EXAMPLES:
        raise HTTPException(404, f"unknown example; choose from {list(EXAMPLES)}")
    return EXAMPLES[name]().model_dump()


@app.get("/api/examples")
def examples() -> list[str]:
    return list(EXAMPLES)


@app.get("/api/catalog")
def get_catalog() -> dict:
    return {
        "grades": [g.name for g in catalog.grades.values()],
        "connections": [c.name for c in catalog.connections.values()],
        "pipes": [{"od": p.od, "weight": p.nominal_weight, "wall": p.wall, "id": p.id}
                  for p in catalog.pipes],
    }


@app.post("/api/import")
async def import_edm_file(file: UploadFile = File(...), wellbore: str | None = None,
                          units: str = "feet") -> dict:
    """Import a Landmark EDM export. Returns the well, the resolved pipe specs per
    string, warnings, and the stored-vs-computed rating comparison."""
    import tempfile

    from casingdesign.io import import_edm, list_wellbores
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        wellbores = list_wellbores(path)
        r = import_edm(path, wellbore=wellbore, source_units=units, catalog=catalog)
    except (ValueError, KeyError) as e:
        raise HTTPException(400, f"import failed: {e}") from e
    except Exception as e:  # malformed XML etc.
        raise HTTPException(400, f"could not parse EDM file: {e}") from e
    return {"well": r.well.model_dump(),
            "specs": {n: {"od": sp.pipe.od, "weight": sp.pipe.nominal_weight,
                          "grade": sp.grade.name, "connection": sp.connection.name}
                      for n, sp in r.specs.items()},
            "warnings": r.warnings, "rating_comparison": r.rating_comparison(),
            "wellbores": [{"id": i, "name": n, "well": w} for i, n, w in wellbores]}


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
    return {"well": req.well.name, "results": out, "warnings": req.well.warnings()}


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
