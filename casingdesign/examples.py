"""Example wells used by the tests, docs and CLI demo."""
from casingdesign.well import (
    CasingString,
    DepthValue,
    DesignFactors,
    Formation,
    Profile,
    SurveyStation,
    Trajectory,
    Well,
)


def onshore_horizontal_well() -> Well:
    """A representative onshore 3-string well: 13-3/8 surface, 9-5/8 intermediate,
    5-1/2 production with a horizontal lateral that is fracture stimulated."""
    traj = Trajectory(stations=[
        SurveyStation(md=0, inclination=0, azimuth=0),
        SurveyStation(md=8_000, inclination=0, azimuth=0),
        SurveyStation(md=9_500, inclination=90, azimuth=90),   # 6 deg/100 ft build
        SurveyStation(md=18_000, inclination=90, azimuth=90),
    ])
    formation = Formation(
        pore_pressure=Profile(points=[DepthValue(tvd=0, value=8.6),
                                      DepthValue(tvd=6_000, value=9.0),
                                      DepthValue(tvd=9_000, value=11.0)]),
        fracture_gradient=Profile(points=[DepthValue(tvd=0, value=12.0),
                                          DepthValue(tvd=2_000, value=13.5),
                                          DepthValue(tvd=9_000, value=16.5)]),
    )
    strings = [
        CasingString(name="Surface", type="surface", od=13.375, hole_size=17.5,
                     shoe_md=2_000, toc_md=0, mud_weight=9.0, cement_lead_ppg=12.5,
                     cement_tail_ppg=15.6, tail_length=500, next_hole_mud_weight=11.0,
                     next_section_td_md=8_500, pressure_test=1_500),
        CasingString(name="Intermediate", type="intermediate", od=9.625, hole_size=12.25,
                     shoe_md=8_500, toc_md=1_500, mud_weight=11.0, cement_lead_ppg=12.5,
                     cement_tail_ppg=15.8, tail_length=1_000, next_hole_mud_weight=12.0,
                     next_section_td_md=18_000, pressure_test=3_500, overpull=150_000),
        CasingString(name="Production", type="production", od=5.5, hole_size=8.5,
                     shoe_md=18_000, toc_md=7_000, mud_weight=12.0, cement_lead_ppg=13.5,
                     cement_tail_ppg=15.8, tail_length=9_500, pressure_test=8_000,
                     overpull=150_000, packer_md=8_000, packer_fluid_ppg=9.0,
                     shut_in_tubing_pressure=4_500, frac_surface_pressure=9_500,
                     frac_fluid_ppg=8.6),
    ]
    return Well(name="Example Onshore Horizontal Well", trajectory=traj, formation=formation,
                strings=strings, design_factors=DesignFactors())


def onshore_liner_well() -> Well:
    """Same well as above but completed with a 7" production casing to 11,500 ft and a
    4-1/2" frac'd liner from 10,500 ft to TD (1,000 ft lap)."""
    base = onshore_horizontal_well()
    strings = base.strings[:2] + [
        CasingString(name="Production", type="production", od=7.0, hole_size=8.5,
                     shoe_md=11_500, toc_md=7_000, mud_weight=12.0, cement_lead_ppg=13.5,
                     cement_tail_ppg=15.8, tail_length=3_000, pressure_test=6_000,
                     overpull=150_000, packer_md=8_000, packer_fluid_ppg=9.0,
                     shut_in_tubing_pressure=4_500),
        CasingString(name="Liner", type="liner", od=4.5, hole_size=6.125,
                     hanger_md=10_500, shoe_md=18_000, toc_md=10_500, mud_weight=12.0,
                     cement_lead_ppg=15.8, cement_tail_ppg=15.8, tail_length=7_500,
                     pressure_test=8_000, overpull=60_000, frac_surface_pressure=9_500,
                     frac_fluid_ppg=8.6),
    ]
    return Well(name="Example Onshore Well with Frac Liner", trajectory=base.trajectory,
                formation=base.formation, strings=strings, design_factors=base.design_factors)
