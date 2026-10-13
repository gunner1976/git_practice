"""Pick the lightest / cheapest pipe that passes every check for a string.

Cost model: $/ft = nominal weight * price per lb for the grade (defaults are relative
indices, not quotes). Replace with a real price list via `price_per_lb`.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from casingdesign.catalog import Catalog, PipeSpec
from casingdesign.design.evaluate import StringResult, evaluate_design, evaluate_string
from casingdesign.design.sections import Section, StringDesign
from casingdesign.loads import LoadCase
from casingdesign.loads.cases import depth_grid, standard_load_cases
from casingdesign.well import CasingString, Well

# Relative price index per lb by grade (carbon grades ~1.0, higher grades cost more).
DEFAULT_PRICE_INDEX = {
    "H-40": 0.95, "J-55": 1.00, "K-55": 1.00, "M-65": 1.05, "N-80": 1.10, "L-80": 1.15,
    "C-90": 1.35, "R-95": 1.25, "T-95": 1.40, "C-110": 1.60, "P-110": 1.35, "Q-125": 1.60,
}


@dataclass
class Candidate:
    result: StringResult
    cost_per_ft: float  # for a tapered design: length-weighted average

    @property
    def spec(self) -> PipeSpec:
        return self.result.spec

    @property
    def design(self) -> StringDesign:
        return self.result.design

    @property
    def total_cost(self) -> float:
        return self.cost_per_ft * (self.design.bottom_md - self.design.top_md)


def cost_per_ft(spec: PipeSpec, price_per_lb: dict[str, float] | None = None) -> float:
    idx = (price_per_lb or DEFAULT_PRICE_INDEX).get(spec.grade.name, 1.5)
    return spec.pipe.nominal_weight * idx


def design_cost(design: StringDesign, price_per_lb: dict[str, float] | None = None) -> float:
    """Total cost index of a design (cost index x ft)."""
    return sum(cost_per_ft(sec.spec, price_per_lb) * sec.length for sec in design.sections)


def optimize_string(well: Well, s: CasingString, catalog: Catalog,
                    grades: list[str] | None = None, connection: str = "BTC",
                    price_per_lb: dict[str, float] | None = None,
                    max_results: int = 5) -> list[Candidate]:
    """Evaluate every catalog candidate for the string's OD; return passing uniform
    designs sorted by cost per foot (cheapest first)."""
    passing: list[Candidate] = []
    for spec in catalog.candidates(s.od, grades, connection, sour=well.formation.sour):
        r = evaluate_string(well, s, spec)
        if r.passes:
            passing.append(Candidate(r, cost_per_ft(spec, price_per_lb)))
    passing.sort(key=lambda c: (c.cost_per_ft, c.spec.pipe.nominal_weight))
    return passing[:max_results]


# ---------------------------------------------------------------------------
# Tapered strings
# ---------------------------------------------------------------------------
def _runs(idx: np.ndarray) -> list[tuple[int, int, int]]:
    """Contiguous runs of equal values as (start, end_exclusive, value)."""
    out, start = [], 0
    for i in range(1, len(idx) + 1):
        if i == len(idx) or idx[i] != idx[start]:
            out.append((start, i, int(idx[start])))
            start = i
    return out


def _design_from_choice(md: np.ndarray, choice: np.ndarray, specs: list[PipeSpec],
                        top: float, bottom: float) -> StringDesign:
    runs = _runs(choice)
    secs = []
    for k, (a, b, v) in enumerate(runs):
        t = top if k == 0 else 0.5 * (md[a - 1] + md[a])
        btm = bottom if k == len(runs) - 1 else 0.5 * (md[b - 1] + md[b])
        secs.append(Section(t, btm, specs[v]))
    return StringDesign(tuple(secs))


def _merge_plan(i: int, runs: list[tuple[int, int, int]], lengths: list[float],
                costs: np.ndarray) -> tuple[float, int, int]:
    """How to eliminate run i without weakening any depth: returns (extra cost,
    run index to overwrite, candidate index to write). Either run i is upgraded to a
    stronger (dearer) neighbour, or a cheaper neighbour is upgraded to run i's pipe."""
    _, _, v = runs[i]
    nb = [j for j in (i - 1, i + 1) if 0 <= j < len(runs)]
    stronger = [j for j in nb if runs[j][2] >= v]
    if stronger:
        j = min(stronger, key=lambda j: costs[runs[j][2]])
        return (costs[runs[j][2]] - costs[v]) * lengths[i], i, runs[j][2]
    j = min(nb, key=lambda j: (costs[v] - costs[runs[j][2]]) * lengths[j])
    return (costs[v] - costs[runs[j][2]]) * lengths[j], j, v


def _enforce_sections(choice: np.ndarray, md: np.ndarray, costs: np.ndarray,
                      min_length: float, max_sections: int) -> np.ndarray:
    """Merge runs shorter than min_length, then reduce to max_sections, choosing the
    cheapest merge each time. Candidates are sorted by cost so a higher index is never
    weaker in cost terms, and merges only ever upgrade a depth."""
    choice = choice.copy()
    step = md[1] - md[0]
    while True:
        runs = _runs(choice)
        if len(runs) == 1:
            return choice
        lengths = [md[b - 1] - md[a] + step for a, b, _ in runs]
        short = [i for i, L in enumerate(lengths) if L < min_length]
        if short:
            i = min(short, key=lambda k: lengths[k])
        elif len(runs) > max_sections:
            i = min(range(len(runs)), key=lambda k: _merge_plan(k, runs, lengths, costs)[0])
        else:
            return choice
        _, target_run, value = _merge_plan(i, runs, lengths, costs)
        a, b, _ = runs[target_run]
        choice[a:b] = value


def optimize_tapered(well: Well, s: CasingString, catalog: Catalog,
                     grades: list[str] | None = None, connection: str = "BTC",
                     price_per_lb: dict[str, float] | None = None,
                     min_section_length: float = 500.0, max_sections: int = 3,
                     step: float = 50.0, max_iter: int = 10) -> Candidate | None:
    """Cheapest tapered design.

    1. Rank candidates by cost; evaluate each as a uniform string to get a per-depth
       pass mask (an approximation, since axial load depends on the pipe below).
    2. At each depth choose the cheapest candidate that passes there.
    3. Enforce minimum section length and section count, only ever upgrading.
    4. Re-evaluate the composite design exactly; where it fails, upgrade that depth
       to the next candidate and repeat until it passes (or no candidate remains).
    """
    cands = catalog.candidates(s.od, grades, connection, sour=well.formation.sour)
    costs_list = [cost_per_ft(c, price_per_lb) for c in cands]
    order = sorted(range(len(cands)), key=lambda i: (costs_list[i], cands[i].pipe.nominal_weight))
    specs = [cands[i] for i in order]
    costs = np.array([costs_list[i] for i in order])
    # Load cases depend (weakly) on the pipe ID through the gas kick case, so they are
    # built per candidate; the MD grid is common.
    masks = np.array([evaluate_design(well, s, StringDesign.uniform(s.hanger_md, s.shoe_md, sp),
                                      standard_load_cases(well, s, step, sp.pipe.id)).pass_mask()
                      for sp in specs])
    md = depth_grid(s, step)
    if not masks.any(axis=0).all():
        return None  # some depth has no passing candidate even uniformly
    choice = np.argmax(masks, axis=0)  # first (cheapest) passing index per depth

    for _ in range(max_iter):
        choice = _enforce_sections(choice, md, costs, min_section_length, max_sections)
        design = _design_from_choice(md, choice, specs, s.hanger_md, s.shoe_md)
        cases: list[LoadCase] = standard_load_cases(well, s, step, design.sections[0].spec.pipe.id)
        result = evaluate_design(well, s, design, cases)
        ok = result.pass_mask()
        if ok.all():
            return Candidate(result, design_cost(design, price_per_lb) / (s.shoe_md - s.hanger_md))
        # Upgrade failing depths to the next candidate that passes there (uniformly).
        for i in np.where(~ok)[0]:
            nxt = np.where(masks[choice[i] + 1:, i])[0]
            if len(nxt) == 0:
                return None
            choice[i] = choice[i] + 1 + nxt[0]
    return None
