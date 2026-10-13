import pytest

from casingdesign.catalog import Catalog


def test_default_catalog_loads():
    c = Catalog.default()
    assert "L-80" in c.grades
    assert len(c.pipes) > 40
    s = c.spec(9.625, 47.0, "L-80", "BTC")
    assert s.burst == pytest.approx(6870, abs=10)
    assert s.collapse == pytest.approx(4760, abs=15)
    assert s.tension_rating == pytest.approx(1_086_000, rel=0.002)
    assert s.label == '9.625" 47# L-80 BTC'


def test_candidates_filter_sour():
    c = Catalog.default()
    all_ = c.candidates(7.0)
    sour = c.candidates(7.0, sour=True)
    assert len(sour) < len(all_)
    assert all(s.grade.sour_service for s in sour)


def test_missing_pipe_raises():
    with pytest.raises(KeyError):
        Catalog.default().pipe(7.0, 99.0)
