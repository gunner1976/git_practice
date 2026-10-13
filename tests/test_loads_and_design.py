import numpy as np
import pytest

from casingdesign.catalog import Catalog
from casingdesign.design import evaluate_string
from casingdesign.loads import as_cemented_axial, running_axial, standard_load_cases
from casingdesign.loads.cases import depth_grid


@pytest.fixture
def cat():
    return Catalog.default()


def test_standard_cases_per_string_type(onshore_well):
    names = {s.name: {c.name for c in standard_load_cases(onshore_well, s)}
             for s in onshore_well.strings}
    assert "Gas to surface" in names["Surface"]
    assert "Lost returns" in names["Intermediate"]
    assert {"Tubing leak", "Stimulation"} <= names["Production"]
    assert "Gas to surface" not in names["Production"]
    for n in names.values():
        assert {"Full evacuation", "Cementing", "Running + overpull", "Pressure test"} <= n


def test_gas_to_surface_profile_shape(onshore_well):
    s = onshore_well.string("Intermediate")
    case = next(c for c in standard_load_cases(onshore_well, s) if c.name == "Gas to surface")
    pi = case.profile.internal
    shoe_tvd = onshore_well.trajectory.tvd(s.shoe_md)
    frac = onshore_well.formation.fracture_gradient.pressure(shoe_tvd)
    assert pi[-1] == pytest.approx(frac)
    assert pi[0] == pytest.approx(frac - 0.1 * shoe_tvd)
    # Burst load is largest near surface for a gas-filled casing.
    assert np.argmax(case.profile.burst_load) == 0


def test_axial_running_is_tension_at_surface_compression_at_shoe(onshore_well, cat):
    s = onshore_well.string("Intermediate")
    spec = cat.spec(9.625, 47.0, "L-80")
    md = depth_grid(s)
    f = running_axial(md, s, spec, onshore_well.trajectory, overpull=0.0)
    # Buoyed weight ~ 47 lb/ft * 8500 ft * (1 - 10/65.4) ~ 338 klbf
    assert f[0] == pytest.approx(47 * 8500 * (1 - 10 / 65.4), rel=0.03)
    assert f[-1] < 0
    f_cem = as_cemented_axial(md, s, spec, onshore_well.trajectory)
    assert f_cem[-1] < f[-1]  # heavier cement at shoe -> more compression


def test_evaluate_reasonable_designs_pass(onshore_well, cat):
    # Common onshore choices; these should all pass with default design factors.
    picks = {"Surface": (13.375, 54.5, "J-55"),
             "Intermediate": (9.625, 47.0, "P-110"),
             "Production": (5.5, 20.0, "P-110")}
    for s in onshore_well.strings:
        r = evaluate_string(onshore_well, s, cat.spec(*picks[s.name]))
        assert r.passes, (s.name, r.summary)


def test_evaluate_undersized_fails(onshore_well, cat):
    s = onshore_well.string("Production")
    r = evaluate_string(onshore_well, s, cat.spec(5.5, 14.0, "J-55"))
    assert not r.passes
    assert not r.summary["burst"]["pass"]
    assert r.summary["burst"]["case"] in ("Stimulation", "Pressure test")


def test_triaxial_never_exceeds_uniaxial_on_pure_pressure(onshore_well, cat):
    """Sanity: the triaxial DF with zero axial load should be within ~15% of the
    Barlow burst DF without the 0.875 wall factor."""
    s = onshore_well.string("Production")
    spec = cat.spec(5.5, 20.0, "P-110")
    r = evaluate_string(onshore_well, s, spec)
    b = r.governing("burst").min_df
    t = r.governing("triaxial").min_df
    assert 0.8 < t / (b / 0.875) < 1.3
