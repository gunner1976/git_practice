import pytest

from casingdesign.well import DepthValue, Profile, SurveyStation, Trajectory


def test_vertical_tvd_equals_md():
    t = Trajectory.vertical(10_000)
    assert t.tvd(5_000) == pytest.approx(5_000)
    assert t.dls(5_000) == 0


def test_minimum_curvature_build_section():
    # Build from 0 to 90 deg over 3000 ft MD at constant 3 deg/100ft.
    t = Trajectory(stations=[
        SurveyStation(md=0, inclination=0, azimuth=0),
        SurveyStation(md=5000, inclination=0, azimuth=0),
        SurveyStation(md=8000, inclination=90, azimuth=0),
        SurveyStation(md=12000, inclination=90, azimuth=0),
    ])
    r = 3000 / (3.14159 / 2)  # radius of curvature
    assert t.tvd(8000) == pytest.approx(5000 + r, rel=1e-4)
    assert t.tvd(12000) == pytest.approx(5000 + r, rel=1e-4)
    assert t.dls(6000) == pytest.approx(3.0)
    assert t.dls(10000) == pytest.approx(0.0)


def test_profile_pressure():
    p = Profile(points=[DepthValue(tvd=0, value=8.6), DepthValue(tvd=10_000, value=10.0)])
    assert p.at(5000) == pytest.approx(9.3)
    assert p.pressure(10_000) == pytest.approx(0.052 * 10.0 * 10_000)


def test_unsorted_stations_rejected():
    with pytest.raises(ValueError):
        Trajectory(stations=[SurveyStation(md=100, inclination=0, azimuth=0),
                             SurveyStation(md=50, inclination=0, azimuth=0)])
