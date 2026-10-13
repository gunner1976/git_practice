"""Evaluate a pipe specification against every load case for a string.

For each load case and depth we compute uniaxial design factors (rating / load) and the
triaxial VME design factor, then report the minimum of each over depth and which load
case governs. A string passes when every minimum meets the well's design factors.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from casingdesign.catalog import PipeSpec
from casingdesign.design.sections import StringDesign
from casingdesign.loads import LoadCase, as_cemented_axial, running_axial
from casingdesign.loads.cases import standard_load_cases
from casingdesign.ratings import collapse_rating_with_axial
from casingdesign.ratings.triaxial import bending_stress, max_vme
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
    design: StringDesign
    checks: list[CheckResult] = field(default_factory=list)
    required: dict[str, float] = field(default_factory=dict)

    @property
    def spec(self) -> PipeSpec:
        """The pipe spec for a uniform design (top section for a tapered one)."""
        return self.design.sections[0].spec

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

    def pass_mask(self) -> np.ndarray:
        """True at each depth of the grid where every check meets its design factor."""
        md = self.checks[0].md
        ok = np.ones_like(md, dtype=bool)
        for c in self.checks:
            ok &= c.design_factor >= self.required[c.check] - 1e-9
        return ok


def _axial_for(case: LoadCase, well: Well, s: CasingString, design) -> np.ndarray:
    md = case.profile.md
    if case.axial_state == "running":
        return running_axial(md, s, design, well.trajectory)
    return as_cemented_axial(md, s, design, well.trajectory)


def _safe_df(rating: np.ndarray, load: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        df = np.where(load > 0.0, rating / np.where(load > 0.0, load, 1.0), INF)
    return df


def evaluate_string(well: Well, s: CasingString, spec: PipeSpec,
                    cases: list[LoadCase] | None = None, step: float = 50.0) -> StringResult:
    """Evaluate a single pipe spec over the whole string."""
    return evaluate_design(well, s, StringDesign.uniform(s.hanger_md, s.shoe_md, spec),
                           cases, step)


def evaluate_design(well: Well, s: CasingString, design: StringDesign,
                    cases: list[LoadCase] | None = None, step: float = 50.0) -> StringResult:
    """Evaluate a (possibly tapered) design: at each depth the section in effect
    supplies the geometry, yield and ratings; the axial profile uses the composite
    weight of all sections below."""
    if cases is None:
        cases = standard_load_cases(well, s, step, design.sections[0].spec.pipe.id)
    dfs = well.design_factors
    result = StringResult(s.name, design, required={
        "burst": dfs.burst, "collapse": dfs.collapse, "tension": dfs.tension,
        "triaxial": dfs.triaxial})

    for case in cases:
        md = case.profile.md
        pi, pe = case.profile.internal, case.profile.external
        specs = design.spec_at(md)
        axial = _axial_for(case, well, s, design)
        area = np.array([sp.geometry.area for sp in specs])
        yp = np.array([sp.grade.min_yield for sp in specs])
        sigma_a = axial / area
        dls = np.asarray(well.trajectory.dls(md), dtype=float)

        # Burst: body/connection internal yield vs differential pressure.
        burst_rating = design.per_depth(md, "burst")
        burst_load = case.profile.burst_load
        result.checks.append(CheckResult(case.name, "burst", md,
                                         _safe_df(burst_rating, burst_load), burst_load,
                                         burst_rating))

        # Collapse: rating reduced for axial tension at each depth (API 5C3 biaxial).
        coll_rating = np.array([
            collapse_rating_with_axial(sp.geometry, sp.grade.min_yield, float(sa))
            * sp.connection.collapse_efficiency for sp, sa in zip(specs, sigma_a)])
        coll_load = case.profile.collapse_load
        result.checks.append(CheckResult(case.name, "collapse", md,
                                         _safe_df(coll_rating, coll_load), coll_load,
                                         coll_rating))

        # Tension: joint/body rating vs axial force; bending added as equivalent force.
        bend_force = np.array([bending_stress(sp.geometry, float(d)) for sp, d in
                               zip(specs, dls)]) * area
        tension_load = np.maximum(axial, 0.0) + bend_force
        tension_rating = design.per_depth(md, "tension_rating")
        result.checks.append(CheckResult(case.name, "tension", md,
                                         _safe_df(tension_rating, tension_load),
                                         tension_load, tension_rating))

        # Triaxial: VME at inner/outer fibre with bending.
        vme = np.array([max_vme(sp.geometry, float(a), float(b), float(f), float(d))
                        for sp, a, b, f, d in zip(specs, pi, pe, axial, dls)])
        result.checks.append(CheckResult(case.name, "triaxial", md, _safe_df(yp, vme),
                                         vme, yp))
    return result
