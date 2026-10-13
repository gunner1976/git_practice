"""Benchmarks against published API 5CT/5C3 performance property tables.

Values are rounded as published (burst/collapse to nearest 10 psi, yield to 1000 lbf).
Each case: (OD, nominal weight, wall, grade yield psi, burst, collapse, body yield).
"""
import math

import pytest

from casingdesign.ratings import (
    PipeGeometry,
    burst_rating,
    collapse_rating,
    collapse_rating_with_axial,
    collapse_regime,
    pipe_body_yield,
)
from casingdesign.ratings.api5c3 import CollapseRegime

# Published API minimum performance properties.
TABLE = [
    # OD, wt, wall, Yp, burst, collapse, body yield (lbf), regime
    (9.625, 47.0, 0.472, 80_000, 6_870, 4_760, 1_086_000, CollapseRegime.PLASTIC),
    (9.625, 40.0, 0.395, 55_000, 3_950, 2_570, 630_000, CollapseRegime.PLASTIC),
    (7.0, 26.0, 0.362, 80_000, 7_240, 5_410, 604_000, CollapseRegime.PLASTIC),
    (7.0, 29.0, 0.408, 110_000, 11_220, 8_530, 929_000, CollapseRegime.PLASTIC),
    (5.5, 17.0, 0.304, 80_000, 7_740, 6_290, 397_000, CollapseRegime.PLASTIC),
    (5.5, 20.0, 0.361, 110_000, 12_640, 11_100, 641_000, CollapseRegime.PLASTIC),
    (13.375, 68.0, 0.480, 55_000, 3_450, 1_950, 1_069_000, CollapseRegime.TRANSITION),
    (13.375, 54.5, 0.380, 55_000, 2_730, 1_130, 853_000, CollapseRegime.TRANSITION),
    (4.5, 11.6, 0.250, 80_000, 7_780, 6_350, 267_000, CollapseRegime.PLASTIC),
]


@pytest.mark.parametrize("od,wt,wall,yp,burst,collapse,body_yield,regime", TABLE)
def test_published_table(od, wt, wall, yp, burst, collapse, body_yield, regime):
    g = PipeGeometry(od, wall)
    assert burst_rating(g, yp) == pytest.approx(burst, abs=10)
    assert collapse_rating(g, yp) == pytest.approx(collapse, abs=15)
    assert pipe_body_yield(g, yp) == pytest.approx(body_yield, rel=0.002)
    assert collapse_regime(g, yp) is regime


def test_geometry_basics():
    g = PipeGeometry(9.625, 0.472)
    assert g.id == pytest.approx(8.681)
    assert g.area == pytest.approx(13.572, rel=1e-3)


def test_axial_tension_reduces_collapse():
    g = PipeGeometry(9.625, 0.472)
    yp = 80_000
    base = collapse_rating(g, yp)
    reduced = collapse_rating_with_axial(g, yp, axial_stress=20_000)
    assert reduced < base
    # Hand calculation: Ypa = 68,102 psi -> A=3.031 B=0.0607 C=1599 (plastic) -> 4,390 psi.
    assert reduced == pytest.approx(4_390, abs=15)
    # Compression is not credited.
    assert collapse_rating_with_axial(g, yp, axial_stress=-20_000) == base


def test_collapse_is_continuous_at_regime_boundaries():
    """The four API formulas should meet (within rounding) at the D/t boundaries."""
    from casingdesign.ratings.api5c3 import _collapse_boundaries

    yp = 80_000
    for dt in _collapse_boundaries(yp):
        lo = collapse_rating(PipeGeometry(dt * 0.5 - 1e-6, 0.5), yp)
        hi = collapse_rating(PipeGeometry(dt * 0.5 + 1e-6, 0.5), yp)
        assert math.isclose(lo, hi, rel_tol=5e-3)


def test_collapse_with_near_yield_axial_stress_is_finite_and_small():
    g = PipeGeometry(5.5, 0.244)
    yp = 55_000
    low = collapse_rating_with_axial(g, yp, axial_stress=0.95 * yp)
    assert 0.0 <= low < collapse_rating(g, yp) * 0.25
    assert collapse_rating_with_axial(g, yp, axial_stress=yp) == 0.0
