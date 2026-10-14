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


def test_round_thread_not_offered_where_api_makes_none():
    c = Catalog.default()
    assert c.candidates(13.375, connection="LTC") == []  # no LTC coupling for 13-3/8 in 5CT
    assert c.candidates(13.375, connection="STC")
    assert c.candidates(20.0, connection="LTC")


def test_btc_small_pipe_uses_regular_coupling():
    """4-1/2 11.6# L-80 BTC: the pipe thread governs (~291 klbf). The regular 5CT coupling
    (W = 5.25 in) is stronger than the special-clearance one (5.0 in) that was wrongly
    tabulated before; a thin enough coupling would govern instead."""
    import math
    c = Catalog.default()
    s = c.spec(4.5, 11.6, "L-80", "BTC")
    g = s.geometry
    pipe_thread = 0.95 * g.area * 95_000 * (1.008 - 0.0396 * (1.083 - 80 / 95) * 4.5)
    assert s.joint_strength == pytest.approx(pipe_thread, rel=1e-6)
    regular = 0.95 * math.pi / 4 * (5.25**2 - 4.5**2) * 95_000
    special = 0.95 * math.pi / 4 * (5.0**2 - 4.5**2) * 95_000
    assert special < regular and pipe_thread < special
    assert buttress_joint_strength(g, 80_000, 95_000, coupling_od=4.8) < pipe_thread
