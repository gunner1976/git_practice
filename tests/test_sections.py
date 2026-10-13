import numpy as np
import pytest

from casingdesign.catalog import Catalog
from casingdesign.design import (
    Section,
    StringDesign,
    design_cost,
    evaluate_design,
    evaluate_string,
    optimize_string,
    optimize_tapered,
)
from casingdesign.loads import running_axial
from casingdesign.loads.cases import depth_grid


@pytest.fixture
def cat():
    return Catalog.default()


def test_uniform_design_matches_evaluate_string(onshore_well, cat):
    s = onshore_well.string("Production")
    spec = cat.spec(5.5, 20.0, "P-110")
    a = evaluate_string(onshore_well, s, spec)
    b = evaluate_design(onshore_well, s, StringDesign.uniform(s.hanger_md, s.shoe_md, spec))
    assert a.summary == b.summary


def test_section_lookup_and_contiguity(cat):
    hi, lo = cat.spec(5.5, 20.0, "P-110"), cat.spec(5.5, 17.0, "P-110")
    d = StringDesign((Section(0, 8000, hi), Section(8000, 18000, lo)))
    md = np.array([0, 7999, 8000, 8001, 18000])
    assert d.section_index(md).tolist() == [0, 0, 0, 1, 1]
    assert d.per_depth(md, "burst")[0] == pytest.approx(hi.burst)
    assert d.per_depth(md, "burst")[-1] == pytest.approx(lo.burst)
    with pytest.raises(ValueError):
        StringDesign((Section(0, 8000, hi), Section(9000, 18000, lo)))


def test_lighter_pipe_below_reduces_surface_tension(cat):
    """Vertical well: lighter pipe in the bottom half removes hanging weight; the
    smaller shoe area reduces the buoyant end force slightly but weight dominates."""
    from casingdesign.well import CasingString, Trajectory
    traj = Trajectory.vertical(10_000)
    s = CasingString(name="P", type="production", od=5.5, hole_size=8.5, shoe_md=10_000,
                     toc_md=5_000, mud_weight=12.0)
    hi, lo = cat.spec(5.5, 20.0, "P-110"), cat.spec(5.5, 17.0, "P-110")
    md = depth_grid(s)
    f_hi = running_axial(md, s, hi, traj)
    f_lo = running_axial(md, s, lo, traj)
    tapered = running_axial(md, s, StringDesign((Section(0, 5000, hi), Section(5000, 10000, lo))),
                            traj)
    assert f_lo[0] < tapered[0] < f_hi[0]
    assert tapered[-1] == pytest.approx(f_lo[-1])  # same bottom pipe -> same end force
    # Removing (20-17) lb/ft nominal over 5000 ft ~ 15 klbf less at surface, minus the
    # smaller buoyant end force (~5 klbf) -> ~10 klbf lighter.
    assert f_hi[0] - tapered[0] == pytest.approx(10_000, rel=0.3)


def test_tapered_is_no_dearer_than_best_uniform(onshore_well, cat):
    s = onshore_well.string("Production")
    best_uniform = optimize_string(onshore_well, s, cat, max_results=1)[0]
    tapered = optimize_tapered(onshore_well, s, cat, max_sections=3)
    assert tapered is not None and tapered.result.passes
    assert tapered.cost_per_ft <= best_uniform.cost_per_ft + 1e-9
    assert len(tapered.design.sections) <= 3
    assert all(sec.length >= 500 for sec in tapered.design.sections)
    assert design_cost(tapered.design) == pytest.approx(tapered.total_cost)


def test_tapered_intermediate_saves_money(onshore_well, cat):
    """Burst governs at surface and collapse at the shoe for the intermediate, so a
    tapered design should beat the 47# uniform string."""
    s = onshore_well.string("Intermediate")
    best_uniform = optimize_string(onshore_well, s, cat, max_results=1)[0]
    tapered = optimize_tapered(onshore_well, s, cat, max_sections=3)
    assert tapered is not None and tapered.result.passes
    assert tapered.cost_per_ft < best_uniform.cost_per_ft
