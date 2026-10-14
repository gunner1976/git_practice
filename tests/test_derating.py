import numpy as np
import pytest

from casingdesign.catalog import Catalog
from casingdesign.design import evaluate_string
from casingdesign.well import YieldDerating


def test_factor_formula():
    d = YieldDerating(slope_per_f=0.0003, reference_f=70, floor=0.8)
    assert d.factor(70) == 1.0
    assert d.factor(50) == 1.0  # no credit below reference
    assert d.factor(270) == pytest.approx(1 - 0.0003 * 200)
    assert d.factor(2000) == 0.8
    assert YieldDerating(enabled=False).factor(np.array([70, 400])).tolist() == [1.0, 1.0]


def test_example_temperature_profile(onshore_well):
    f = onshore_well.formation
    assert f.temperature(0) == 70.0
    assert f.temperature(9000) == pytest.approx(70 + 1.2 * 90)


def test_derating_lowers_design_factors_at_depth(onshore_well):
    cat = Catalog.default()
    s = onshore_well.string("Intermediate")
    spec = cat.spec(9.625, 47.0, "P-110")
    hot = evaluate_string(onshore_well, s, spec)
    onshore_well.yield_derating.enabled = False
    cool = evaluate_string(onshore_well, s, spec)
    for chk in ("burst", "collapse", "tension", "triaxial"):
        assert hot.summary[chk]["min_df"] <= cool.summary[chk]["min_df"] + 1e-9
    # Burst and tension ratings scale exactly with the yield factor at each depth.
    md = hot.checks[0].md
    f = onshore_well.yield_derating.model_copy(update={"enabled": True}).factor(
        onshore_well.formation.temperature(onshore_well.trajectory.tvd(md)))
    assert f[0] == 1.0 and f[-1] < 0.975
    for chk in ("burst", "tension"):
        h = next(c for c in hot.checks if c.check == chk).rating
        c_ = next(c for c in cool.checks if c.check == chk).rating
        assert np.allclose(h / c_, f)
    # Plastic-regime collapse falls less than proportionally (API constants shift with Yp).
    hc = next(c for c in hot.checks if c.check == "collapse").rating[-1]
    cc = next(c for c in cool.checks if c.check == "collapse").rating[-1]
    assert f[-1] < hc / cc < 1.0


def test_hot_well_can_fail_where_cool_passes(onshore_well):
    cat = Catalog.default()
    s = onshore_well.string("Intermediate")
    spec = cat.spec(9.625, 47.0, "P-110")
    assert evaluate_string(onshore_well, s, spec).passes
    onshore_well.formation.geothermal_gradient_f_per_100ft = 3.0  # ~325 F at the shoe
    onshore_well.yield_derating.slope_per_f = 0.002  # a grade with steep hot-yield loss
    onshore_well.yield_derating.floor = 0.6
    assert not evaluate_string(onshore_well, s, spec).passes
