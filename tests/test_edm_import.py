from pathlib import Path

import pytest

from casingdesign.catalog import Catalog
from casingdesign.design import evaluate_string
from casingdesign.io import import_edm, list_wellbores

FIX = Path(__file__).parent / "fixtures" / "sample_edm.xml"


def test_list_wellbores():
    wbs = list_wellbores(FIX)
    assert ("WB1", "Demo 1H Original Hole", "Demo 1H") in wbs
    assert len(wbs) == 2


def test_import_picks_deepest_wellbore_and_maps_trajectory():
    r = import_edm(FIX)
    w = r.well
    assert w.name == "Demo 1H Original Hole"
    assert w.trajectory.td == 18_000
    assert w.trajectory.tvd(18_000) == pytest.approx(8955, abs=5)


def test_pressures_and_temperature():
    w = import_edm(FIX).well
    f = w.formation
    assert f.pore_pressure.at(6000) == pytest.approx(9.0, abs=0.01)
    assert f.pore_pressure.at(0) == pytest.approx(8.6, abs=0.01)  # extended to surface
    assert f.fracture_gradient.at(9000) == pytest.approx(16.5, abs=0.01)
    assert f.surface_temperature_f == pytest.approx(70, abs=0.5)
    assert f.geothermal_gradient_f_per_100ft == pytest.approx(1.2, abs=0.01)


def test_strings_and_specs():
    r = import_edm(FIX)
    names = [s.name for s in r.well.strings]
    assert names == ["13-3/8 Surface", "9-5/8 Intermediate", "5-1/2 Production"]
    assert [s.type for s in r.well.strings] == ["surface", "intermediate", "production"]
    inter = r.well.string("9-5/8 Intermediate")
    assert inter.shoe_md == 8500 and inter.next_section_td_md == 18_000
    # Heaviest component represents the string; grade names normalised.
    assert r.specs["9-5/8 Intermediate"].label == '9.625" 47# L-80 BTC'
    assert r.specs["13-3/8 Surface"].label == '13.375" 54.5# J-55 BTC'
    prod = r.specs["5-1/2 Production"]
    assert prod.grade.name == "P-110" and prod.connection.name == "PREMIUM"
    assert any("mud weight assumed" in w for w in r.warnings)


def test_stored_ratings_match_ours():
    r = import_edm(FIX)
    cmp = {c["string"]: c for c in r.rating_comparison()}
    c = cmp["9-5/8 Intermediate"]
    assert c["burst_ours"] == pytest.approx(c["burst_stored"], abs=10)
    assert c["collapse_ours"] == pytest.approx(c["collapse_stored"], abs=15)
    assert c["axial_ours_klbf"] == pytest.approx(c["axial_stored_klbf"], rel=0.005)


def test_imported_well_evaluates():
    r = import_edm(FIX)
    for s in r.well.strings:
        res = evaluate_string(r.well, s, r.specs[s.name])
        assert res.summary  # runs end to end


def test_select_wellbore_by_name_and_units():
    r = import_edm(FIX, wellbore="Demo 1H Pilot")
    assert r.well.trajectory.td == 9000
    rm = import_edm(FIX, wellbore="WB2", source_units="meters")
    assert rm.well.trajectory.td == pytest.approx(9000 * 3.280839895)
    with pytest.raises(KeyError):
        import_edm(FIX, wellbore="nope")


def test_catalog_kwarg():
    r = import_edm(FIX, catalog=Catalog.default())
    assert r.specs
