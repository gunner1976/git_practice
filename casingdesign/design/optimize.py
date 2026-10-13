"""Pick the lightest / cheapest pipe that passes every check for a string.

Cost model: $/ft = nominal weight * price per lb for the grade (defaults are relative
indices, not quotes). Replace with a real price list via `price_per_lb`.
"""
from __future__ import annotations

from dataclasses import dataclass

from casingdesign.catalog import Catalog, PipeSpec
from casingdesign.design.evaluate import StringResult, evaluate_string
from casingdesign.well import CasingString, Well

# Relative price index per lb by grade (carbon grades ~1.0, higher grades cost more).
DEFAULT_PRICE_INDEX = {
    "H-40": 0.95, "J-55": 1.00, "K-55": 1.00, "M-65": 1.05, "N-80": 1.10, "L-80": 1.15,
    "C-90": 1.35, "R-95": 1.25, "T-95": 1.40, "C-110": 1.60, "P-110": 1.35, "Q-125": 1.60,
}


@dataclass
class Candidate:
    result: StringResult
    cost_per_ft: float

    @property
    def spec(self) -> PipeSpec:
        return self.result.spec


def cost_per_ft(spec: PipeSpec, price_per_lb: dict[str, float] | None = None) -> float:
    idx = (price_per_lb or DEFAULT_PRICE_INDEX).get(spec.grade.name, 1.5)
    return spec.pipe.nominal_weight * idx


def optimize_string(well: Well, s: CasingString, catalog: Catalog,
                    grades: list[str] | None = None, connection: str = "BTC",
                    price_per_lb: dict[str, float] | None = None,
                    max_results: int = 5) -> list[Candidate]:
    """Evaluate every catalog candidate for the string's OD; return passing designs
    sorted by cost per foot (cheapest first)."""
    passing: list[Candidate] = []
    for spec in catalog.candidates(s.od, grades, connection, sour=well.formation.sour):
        r = evaluate_string(well, s, spec)
        if r.passes:
            passing.append(Candidate(r, cost_per_ft(spec, price_per_lb)))
    passing.sort(key=lambda c: (c.cost_per_ft, c.spec.pipe.nominal_weight))
    return passing[:max_results]
