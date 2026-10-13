import numpy as np
import pytest

from casingdesign.catalog import Catalog
from casingdesign.design import evaluate_string, optimize_string
from casingdesign.loads.cases import standard_load_cases


def _names(well, s, cid=8.681):
    return [c.name for c in standard_load_cases(well, s, inner_diameter=cid)]


def test_kick_replaces_gas_to_surface_when_volume_given(onshore_well):
    s = onshore_well.string("Intermediate")
    assert "Gas to surface" in _names(onshore_well, s) and "Gas kick" not in _names(onshore_well, s)
    s.kick_volume_bbl = 50.0
    assert "Gas kick" in _names(onshore_well, s) and "Gas to surface" not in _names(onshore_well, s)
    s.include_gas_to_surface = True
    assert {"Gas kick", "Gas to surface"} <= set(_names(onshore_well, s))


def test_kick_profile_physics(onshore_well):
    s = onshore_well.string("Intermediate")
    s.kick_volume_bbl = 50.0
    cid = 8.681
    kick = next(c for c in standard_load_cases(onshore_well, s, inner_diameter=cid)
                if c.name == "Gas kick")
    pi, md = kick.profile.internal, kick.profile.md
    traj = onshore_well.trajectory
    h = 50.0 / (cid**2 / 1029.4)
    td_tvd = traj.tvd(s.next_section_td_md)
    p_form = 0.052 * (12.0 + 0.5) * td_tvd
    expected_surface = p_form - 0.052 * 12.0 * (td_tvd - h) - 0.1 * h
    assert pi[0] == pytest.approx(expected_surface, rel=1e-6)
    assert expected_surface == pytest.approx(0.052 * 0.5 * td_tvd + (0.052 * 12.0 - 0.1) * h)
    # Gas gradient in the bubble, mud gradient below it (per ft of TVD).
    grad = np.diff(pi) / np.diff(traj.tvd(md))
    assert grad[0] == pytest.approx(0.1, abs=1e-6)
    assert grad[-1] == pytest.approx(0.052 * 12.0, abs=1e-6)
    # Shoe pressure stays at or below fracture pressure.
    p_frac = onshore_well.formation.fracture_gradient.pressure(traj.tvd(s.shoe_md))
    assert pi[-1] <= p_frac + 1e-6
    assert "bbl" in kick.description


def test_kick_is_less_severe_than_gas_to_surface(onshore_well):
    s = onshore_well.string("Intermediate")
    gts = next(c for c in standard_load_cases(onshore_well, s) if c.name == "Gas to surface")
    s.kick_volume_bbl = 50.0
    kick = next(c for c in standard_load_cases(onshore_well, s, inner_diameter=8.681)
                if c.name == "Gas kick")
    assert kick.profile.burst_load[0] < gts.profile.burst_load[0]


def test_bop_cap_shifts_profile(onshore_well):
    s = onshore_well.string("Intermediate")
    s.kick_volume_bbl = 50.0
    s.max_surface_pressure = 300.0
    kick = next(c for c in standard_load_cases(onshore_well, s, inner_diameter=8.681)
                if c.name == "Gas kick")
    assert kick.profile.internal[0] == pytest.approx(300.0)
    assert "BOP" in kick.description


def test_kick_tolerance_changes_governing_burst_case(onshore_well):
    """For this well collapse at the shoe still forces 47#, but the kick case should
    relieve burst substantially compared with gas-to-surface."""
    cat = Catalog.default()
    s = onshore_well.string("Intermediate")
    spec = cat.spec(9.625, 47.0, "N-80")
    before = evaluate_string(onshore_well, s, spec).summary["burst"]
    s.kick_volume_bbl = 50.0
    after = evaluate_string(onshore_well, s, spec).summary["burst"]
    assert before["case"] == "Gas to surface" and after["case"] != "Gas to surface"
    assert after["min_df"] > before["min_df"] * 1.5
    assert optimize_string(onshore_well, s, cat, max_results=1)[0].result.passes
