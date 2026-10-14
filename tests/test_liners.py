import pytest

from casingdesign.catalog import Catalog
from casingdesign.design import evaluate_string, optimize_string
from casingdesign.examples import onshore_liner_well
from casingdesign.loads.cases import standard_load_cases
from casingdesign.well import CasingString


@pytest.fixture
def liner_well():
    return onshore_liner_well()


def test_parent_and_liner_relationships(liner_well):
    liner = liner_well.string("Liner")
    prod = liner_well.string("Production")
    assert liner_well.parent_of(liner) is prod
    assert liner_well.liners_of(prod) == [liner]
    assert liner_well.liners_of(liner_well.string("Intermediate")) == []
    assert liner_well.warnings() == []


def test_liner_validation():
    bad = CasingString(name="L", type="liner", od=4.5, hole_size=6.125, hanger_md=0,
                       shoe_md=18_000, toc_md=0, mud_weight=12)
    assert any("liner must hang" in e for e in bad.errors())
    bad2 = CasingString(name="P", type="production", od=7.0, hole_size=8.5, hanger_md=500,
                        shoe_md=18_000, toc_md=0, mud_weight=12)
    assert any("only liners" in e for e in bad2.errors())
    good = CasingString(name="L", type="liner", od=4.5, hole_size=6.125, hanger_md=10_500,
                        shoe_md=18_000, toc_md=10_500, mud_weight=12)
    assert good.errors() == []


def test_warnings_for_bad_lap(liner_well):
    liner = liner_well.string("Liner")
    liner.hanger_md = 11_400  # 100 ft lap
    liner.toc_md = 12_000     # TOC below liner top
    w = liner_well.warnings()
    assert any("overlap" in x for x in w) and any("uncemented lap" in x for x in w)


def test_parent_inherits_liner_stimulation(liner_well):
    prod = liner_well.string("Production")
    names = [c.name for c in standard_load_cases(liner_well, prod, inner_diameter=6.276)]
    assert "Stimulation (via Liner)" in names
    assert "Tubing leak" in names  # the casing's own case
    liner_names = [c.name for c in standard_load_cases(liner_well, liner_well.string("Liner"))]
    assert "Stimulation" in liner_names and "Gas to surface" not in liner_names


def test_inherited_profile_matches_liner_at_shared_depth(liner_well):
    prod, liner = liner_well.string("Production"), liner_well.string("Liner")
    own = next(c for c in standard_load_cases(liner_well, liner) if c.name == "Stimulation")
    inh = next(c for c in standard_load_cases(liner_well, prod, inner_diameter=6.276)
               if c.name == "Stimulation (via Liner)")
    # Internal pressure at 11,000 ft MD (inside the lap) is the same frac column.
    import numpy as np
    assert np.interp(11_000, inh.profile.md, inh.profile.internal) == pytest.approx(
        np.interp(11_000, own.profile.md, own.profile.internal), rel=1e-6)


def test_liner_axial_starts_at_hanger(liner_well):
    cat = Catalog.default()
    liner = liner_well.string("Liner")
    r = evaluate_string(liner_well, liner, cat.spec(4.5, 11.6, "P-110"))
    run = next(c for c in r.checks if c.check == "tension" and c.case == "Running + overpull")
    assert run.md[0] == 10_500
    # Buoyed liner weight (~7,500 ft, mostly horizontal) plus 60 klbf overpull is small.
    assert run.load[0] < 150_000


def test_drilling_liner_kick_propagates_to_parent(liner_well):
    inter = liner_well.string("Intermediate")
    drill_liner = CasingString(name="Drilling liner", type="liner", od=7.0, hole_size=8.5,
                               hanger_md=8_000, shoe_md=12_000, toc_md=8_000, mud_weight=12.0,
                               next_hole_mud_weight=13.0, next_section_td_md=18_000,
                               kick_volume_bbl=30.0)
    liner_well.strings.insert(2, drill_liner)
    assert liner_well.parent_of(drill_liner) is inter
    names = [c.name for c in standard_load_cases(liner_well, inter, inner_diameter=8.681)]
    assert "Gas kick (via Drilling liner)" in names


def test_optimizer_handles_liner_and_parent(liner_well):
    cat = Catalog.default()
    for name in ("Production", "Liner"):
        best = optimize_string(liner_well, liner_well.string(name), cat, max_results=1)
        assert best and best[0].result.passes, name
