import pytest

from casingdesign.catalog import Catalog
from casingdesign.ratings import PipeGeometry
from casingdesign.ratings.joints import buttress_joint_strength, round_thread_joint_strength


def test_btc_matches_published_9625_47_l80():
    # Published API BTC joint strength for 9-5/8 47# L-80: 1,122,000 lbf.
    g = PipeGeometry(9.625, 0.472)
    assert buttress_joint_strength(g, 80_000, 95_000) == pytest.approx(1_122_000, rel=0.01)


def test_round_thread_fracture_bounds_jumpout():
    g = PipeGeometry(9.625, 0.472)
    long = round_thread_joint_strength(g, 80_000, 95_000, engaged_length=50.0)
    short = round_thread_joint_strength(g, 80_000, 95_000, engaged_length=2.33)
    assert long == pytest.approx(0.95 * 11.434 * 95_000, rel=0.01)  # fracture-limited
    assert short < long


def test_catalog_ordering_stc_lt_ltc_lt_btc():
    c = Catalog.default()
    for od, wt in [(5.5, 17.0), (7.0, 26.0), (9.625, 47.0)]:
        stc = c.spec(od, wt, "L-80", "STC").joint_strength
        ltc = c.spec(od, wt, "L-80", "LTC").joint_strength
        btc = c.spec(od, wt, "L-80", "BTC").joint_strength
        body = c.spec(od, wt, "L-80", "BTC").body_yield
        assert stc < ltc < btc
        assert body < btc <= body * 1.10  # BTC is tensile-based: a little above body yield


def test_calibrated_ltc_values():
    c = Catalog.default()
    assert c.spec(9.625, 47.0, "L-80", "LTC").joint_strength == pytest.approx(905_000, rel=0.01)
    assert c.spec(7.0, 26.0, "L-80", "LTC").joint_strength == pytest.approx(519_000, rel=0.01)


def test_round_thread_not_offered_where_no_thread_data():
    c = Catalog.default()
    assert c.candidates(20.0, connection="LTC") == []
    assert c.candidates(20.0, connection="STC")
