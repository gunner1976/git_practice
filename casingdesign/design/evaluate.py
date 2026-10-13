"""Evaluate a pipe specification against every load case for a string.

For each load case and depth we compute uniaxial design factors (rating / load) and the
triaxial VME design factor, then report the minimum of each over depth and which load
case governs. A string passes when every minimum meets the well's design factors.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from casingdesign.catalog import PipeSpec
from casingdesign.loads import LoadCase, as_cemented_axial, running_axial
from casingdesign.loads.cases import standard_load_cases
from casingdesign.ratings import collapse_rating_with_axial
from casingdesign.ratings.triaxial import max_vme
from casingdesign.well import CasingString, Well

INF = float("inf")


@dataclass
class CheckResult:
    """Design factor profile for one check (burst/collapse/tension/triaxial) of one case."""

    case: str
    check: str
    md: np.ndarray
    design_factor: np.ndarray  # inf where the load is zero
    load: np.ndarray
    rating: np.ndarray

    @property
    def min_df(self) -> float:
        return float(np.min(self.design_factor))

    @property
    def md_at_min(self) -> float:
        return float(self.md[int(np.argmin(self.design_factor))])


@dataclass
class StringResult:
    string: str
    spec: PipeSpec
    checks: list[CheckResult] = field(default_factory=list)
    required: dict[str, float] = field(default_factory=dict)

    def governing(self, check: str) -> CheckResult:
        return min((c for c in self.checks if c.check == check), key=lambda c: c.min_df)

    @property
    def summary(self) -> dict[str, dict]:
        out = {}
        for chk in ("burst", "collapse", "tension", "triaxial"):
            g = self.governing(chk)
            out[chk] = {
                "min_df": g.min_df,
                "required": self.required[chk],
                "case": g.case,
                "md": g.md_at_min,
                "pass": g.min_df >= self.required[chk],
            }
        return out

    @property
    def passes(self) -> bool:
        return all(v["pass"] for v in self.summary.values())


def _axial_for(case: LoadCase, well: Well, s: CasingString, spec: PipeSpec) -> np.ndarray:
    md = case.profile.md
    if case.axial_state == "running":
        return running_axial(md, s, spec, well.trajectory)
    return as_cemented_axial(md, s, spec, well.trajectory)


def _safe_df(rating: np.ndarray, load: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        df = np.where(load > 0.0, rating / np.where(load > 0.0, load, 1.0), INF)
    return df


def evaluate_string(well: Well, s: CasingString, spec: PipeSpec,
                    cases: list[LoadCase] | None = None, step: float = 50.0) -> StringResult:
    cases = cases if cases is not None else standard_load_cases(well, s, step)
    geom = spec.geometry
    yp = spec.grade.min_yield
    dfs = well.design_factors
    result = StringResult(s.name, spec, required={
        "burst": dfs.burst, "collapse": dfs.collapse, "tension": dfs.tension,
        "triaxial": dfs.triaxial})

    for case in cases:
        md = case.profile.md
        pi, pe = case.profile.internal, case.profile.external
        axial = _axial_for(case, well, s, spec)
        sigma_a = axial / geom.area
        dls = np.asarray(well.trajectory.dls(md), dtype=float)

        # Burst: body/connection internal yield vs differential pressure.
        burst_load = case.profile.burst_load
        result.checks.append(CheckResult(case.name, "burst", md,
                                         _safe_df(np.full_like(md, spec.burst), burst_load),
                                         burst_load, np.full_like(md, spec.burst)))

        # Collapse: rating reduced for axial tension at each depth (API 5C3 biaxial).
        coll_rating = np.array([collapse_rating_with_axial(geom, yp, float(sa)) for sa in sigma_a])
        coll_rating *= spec.connection.collapse_efficiency
        coll_load = case.profile.collapse_load
        result.checks.append(CheckResult(case.name, "collapse", md,
                                         _safe_df(coll_rating, coll_load), coll_load,
                                         coll_rating))

        # Tension: joint/body rating vs axial force; bending added as equivalent force.
        from casingdesign.ratings.triaxial import bending_stress
        bend_force = np.array([bending_stress(geom, float(d)) for d in dls]) * geom.area
        tension_load = np.maximum(axial, 0.0) + bend_force
        result.checks.append(CheckResult(case.name, "tension", md,
                                         _safe_df(np.full_like(md, spec.tension_rating),
                                                  tension_load),
                                         tension_load, np.full_like(md, spec.tension_rating)))

        # Triaxial: VME at inner/outer fibre with bending.
        vme = np.array([max_vme(geom, float(a), float(b), float(f), float(d))
                        for a, b, f, d in zip(pi, pe, axial, dls)])
        result.checks.append(CheckResult(case.name, "triaxial", md, _safe_df(np.full_like(md, yp), vme),
                                         vme, np.full_like(md, yp)))
    return result
