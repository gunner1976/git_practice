import math

import pytest

from casingdesign.ratings import PipeGeometry, lame_stresses, triaxial_design_factor, vme_stress
from casingdesign.ratings.triaxial import bending_stress, max_vme


def test_lame_boundary_conditions():
    g = PipeGeometry(9.625, 0.472)
    sr_i, _ = lame_stresses(g, 5000, 1000, g.id / 2)
    sr_o, _ = lame_stresses(g, 5000, 1000, g.od / 2)
    assert sr_i == pytest.approx(-5000)
    assert sr_o == pytest.approx(-1000)


def test_vme_pure_uniaxial():
    assert vme_stress(0, 0, 50_000) == pytest.approx(50_000)
    assert vme_stress(0, 0, -50_000) == pytest.approx(50_000)


def test_bending_stress_matches_field_rule():
    g = PipeGeometry(7.0, 0.362)
    # Field rule of thumb: sigma_b ~ 218 * OD * DLS
    assert bending_stress(g, 10.0) == pytest.approx(218 * 7.0 * 10.0, rel=0.01)


def test_triaxial_df_vs_uniaxial_burst_on_thin_wall():
    """With no axial load the VME check at the inner wall is close to Barlow burst
    (without the 0.875 wall factor) for thin pipe, so DF should be ~Yp/hoop."""
    g = PipeGeometry(9.625, 0.472)
    yp = 80_000
    pi = 3000.0
    df = triaxial_design_factor(g, yp, pi, 0.0, 0.0)
    hoop_approx = pi * (g.id / (2 * g.wall))
    assert df == pytest.approx(yp / hoop_approx, rel=0.15)


def test_unstressed_gives_inf():
    g = PipeGeometry(7.0, 0.362)
    assert math.isinf(triaxial_design_factor(g, 80_000, 0, 0, 0))


def test_dogleg_increases_vme():
    g = PipeGeometry(7.0, 0.362)
    assert max_vme(g, 3000, 1000, 200_000, 8.0) > max_vme(g, 3000, 1000, 200_000, 0.0)
