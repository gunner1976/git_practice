"""Convert engine results into JSON-friendly dicts for the API and plots."""
from __future__ import annotations

import math

import numpy as np

from casingdesign.catalog import PipeSpec
from casingdesign.design.evaluate import StringResult
from casingdesign.design.sections import StringDesign
from casingdesign.loads import LoadCase


def _list(a: np.ndarray) -> list[float | None]:
    return [None if (math.isinf(x) or math.isnan(x)) else float(x) for x in a.tolist()]


def spec_dict(spec: PipeSpec) -> dict:
    return {
        "label": spec.label, "od": spec.pipe.od, "weight": spec.pipe.nominal_weight,
        "wall": spec.pipe.wall, "id": spec.pipe.id, "grade": spec.grade.name,
        "connection": spec.connection.name, "yield": spec.grade.min_yield,
        "burst": spec.burst, "collapse": spec.collapse, "body_yield": spec.body_yield,
        "joint_strength": spec.joint_strength, "tension_rating": spec.tension_rating,
    }


def design_dict(design: StringDesign) -> dict:
    return {"label": design.label, "uniform": design.is_uniform,
            "sections": [{"top_md": sec.top_md, "bottom_md": sec.bottom_md,
                          "spec": spec_dict(sec.spec)} for sec in design.sections]}


def case_dict(case: LoadCase) -> dict:
    return {
        "name": case.name, "kind": case.kind.value, "description": case.description,
        "md": _list(case.profile.md), "internal": _list(case.profile.internal),
        "external": _list(case.profile.external),
    }


def result_dict(result: StringResult, cases: list[LoadCase], axial_by_case: dict[str, np.ndarray],
                well=None) -> dict:
    temp = None
    if well is not None:
        md = cases[0].profile.md
        t = well.formation.temperature(well.trajectory.tvd(md))
        temp = {"md": _list(md), "temperature_f": _list(t),
                "yield_factor": _list(well.yield_derating.factor(t))}
    return {
        "temperature": temp,
        "string": result.string,
        "spec": spec_dict(result.spec),
        "design": design_dict(result.design),
        "pass": result.passes,
        "summary": result.summary,
        "cases": [case_dict(c) | {"axial": _list(axial_by_case[c.name])} for c in cases],
        "checks": [
            {"case": c.case, "check": c.check, "md": _list(c.md), "load": _list(c.load),
             "rating": _list(c.rating), "design_factor": _list(c.design_factor),
             "min_df": None if math.isinf(c.min_df) else c.min_df, "md_at_min": c.md_at_min}
            for c in result.checks
        ],
    }
