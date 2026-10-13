"""Pipe body performance properties per API TR 5C3 / ISO 10400 (historical API formulas).

All inputs and outputs in US oilfield units: inches, psi, lbf.
Every function is pure and documented with the clause it implements so a reviewer can
trace any number back to the standard.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

# Below this yield strength the empirical A..G constants leave their fitted range
# (API grades span 40-125 ksi) and the regime boundaries stop being monotonic. Only
# reached via the biaxial reduced yield Ypa when axial stress approaches yield.
MIN_YIELD_FOR_API_COLLAPSE_FIT = 15_000.0
# API 5C3 wall-thickness tolerance used for burst (minimum wall = 87.5% nominal).
WALL_TOLERANCE_FACTOR = 0.875
# Young's modulus for steel, psi. The elastic-collapse constant 46.95e6 = 2E/(1-nu^2)
# with E = 30e6 psi and nu = 0.3.
E_STEEL = 30.0e6
POISSON = 0.3
ELASTIC_COLLAPSE_CONST = 46.95e6


@dataclass(frozen=True)
class PipeGeometry:
    """Nominal pipe body geometry."""

    od: float  # in
    wall: float  # in

    @property
    def id(self) -> float:
        return self.od - 2.0 * self.wall

    @property
    def d_over_t(self) -> float:
        return self.od / self.wall

    @property
    def area(self) -> float:
        """Steel cross-sectional area, in^2."""
        return math.pi / 4.0 * (self.od**2 - self.id**2)

    @property
    def moment_of_inertia(self) -> float:
        """Second moment of area, in^4."""
        return math.pi / 64.0 * (self.od**4 - self.id**4)


class CollapseRegime(str, Enum):
    YIELD = "yield"
    PLASTIC = "plastic"
    TRANSITION = "transition"
    ELASTIC = "elastic"


# ---------------------------------------------------------------------------
# Burst (API 5C3 §4.3 internal yield pressure, Barlow with 87.5% wall)
# ---------------------------------------------------------------------------
def burst_rating(geom: PipeGeometry, yield_strength: float) -> float:
    """Internal yield pressure of the pipe body, psi.

    P = 0.875 * 2 * Yp * t / D
    """
    return WALL_TOLERANCE_FACTOR * 2.0 * yield_strength * geom.wall / geom.od


# ---------------------------------------------------------------------------
# Pipe body yield strength (API 5C3 §4.1)
# ---------------------------------------------------------------------------
def pipe_body_yield(geom: PipeGeometry, yield_strength: float) -> float:
    """Axial load to yield the pipe body, lbf. F = Yp * A."""
    return yield_strength * geom.area


# ---------------------------------------------------------------------------
# Collapse (API 5C3 §4.2, four regimes with empirical constants A, B, C, F, G)
# ---------------------------------------------------------------------------
def _collapse_constants(yp: float) -> tuple[float, float, float, float, float]:
    """Empirical collapse constants A, B, C, F, G as functions of yield strength (psi)."""
    a = 2.8762 + 0.10679e-5 * yp + 0.21301e-10 * yp**2 - 0.53132e-16 * yp**3
    b = 0.026233 + 0.50609e-6 * yp
    c = -465.93 + 0.030867 * yp - 0.10483e-7 * yp**2 + 0.36989e-13 * yp**3
    ba = b / a
    x = 3.0 * ba / (2.0 + ba)
    f = ELASTIC_COLLAPSE_CONST * x**3 / (yp * (x - ba) * (1.0 - x) ** 2)
    g = f * ba
    return a, b, c, f, g


def _collapse_boundaries(yp: float) -> tuple[float, float, float]:
    """D/t boundaries between yield/plastic, plastic/transition and transition/elastic."""
    a, b, c, f, g = _collapse_constants(yp)
    bc = b + c / yp
    dt_yp = (math.sqrt((a - 2.0) ** 2 + 8.0 * bc) + (a - 2.0)) / (2.0 * bc)
    dt_pt = yp * (a - f) / (c + yp * (b - g))
    dt_te = (2.0 + b / a) / (3.0 * b / a)
    return dt_yp, dt_pt, dt_te


def collapse_regime(geom: PipeGeometry, yield_strength: float) -> CollapseRegime:
    dt = geom.d_over_t
    dt_yp, dt_pt, dt_te = _collapse_boundaries(yield_strength)
    if dt <= dt_yp:
        return CollapseRegime.YIELD
    if dt <= dt_pt:
        return CollapseRegime.PLASTIC
    if dt <= dt_te:
        return CollapseRegime.TRANSITION
    return CollapseRegime.ELASTIC


def collapse_rating(geom: PipeGeometry, yield_strength: float) -> float:
    """External pressure collapse resistance of the pipe body, psi (no axial load).

    Yield:      Pyp = 2 Yp (D/t - 1) / (D/t)^2
    Plastic:    Pp  = Yp (A/(D/t) - B) - C
    Transition: Pt  = Yp (F/(D/t) - G)
    Elastic:    Pe  = 46.95e6 / ((D/t) (D/t - 1)^2)
    """
    dt = geom.d_over_t
    yp = yield_strength
    if yp < MIN_YIELD_FOR_API_COLLAPSE_FIT:
        # Outside the empirical fit: bound by yield collapse and elastic collapse.
        return min(2.0 * yp * (dt - 1.0) / dt**2,
                   ELASTIC_COLLAPSE_CONST / (dt * (dt - 1.0) ** 2))
    regime = collapse_regime(geom, yp)
    a, b, c, f, g = _collapse_constants(yp)
    if regime is CollapseRegime.YIELD:
        return 2.0 * yp * (dt - 1.0) / dt**2
    if regime is CollapseRegime.PLASTIC:
        return yp * (a / dt - b) - c
    if regime is CollapseRegime.TRANSITION:
        return yp * (f / dt - g)
    return ELASTIC_COLLAPSE_CONST / (dt * (dt - 1.0) ** 2)


# ---------------------------------------------------------------------------
# Collapse under axial stress (API 5C3 §4.2.6, biaxial reduced yield)
# ---------------------------------------------------------------------------
def axial_adjusted_yield(yield_strength: float, axial_stress: float) -> float:
    """Yield strength reduced for axial tension (positive) per API 5C3.

    Ypa = Yp * [ sqrt(1 - 0.75 (Sa/Yp)^2) - 0.5 (Sa/Yp) ]

    Axial compression (negative Sa) raises Ypa; API caps the correction at Sa = Yp.
    """
    ratio = axial_stress / yield_strength
    if abs(ratio) >= 1.0:
        raise ValueError("axial stress magnitude must be below yield strength")
    return yield_strength * (math.sqrt(1.0 - 0.75 * ratio**2) - 0.5 * ratio)


def collapse_rating_with_axial(
    geom: PipeGeometry, yield_strength: float, axial_stress: float
) -> float:
    """Collapse resistance with axial stress, psi.

    Recomputes the collapse constants and regime with the reduced yield strength Ypa.
    Tension reduces collapse resistance; API 5C3 does not credit compression, so we
    use Ypa = Yp when Sa <= 0 (conservative, matches common practice).
    """
    if axial_stress <= 0.0:
        return collapse_rating(geom, yield_strength)
    if axial_stress >= yield_strength:
        return 0.0  # pipe body has yielded axially; no collapse capacity remains
    ypa = axial_adjusted_yield(yield_strength, axial_stress)
    return collapse_rating(geom, ypa)
