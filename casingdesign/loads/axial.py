"""Axial force profiles along a casing string (tension positive, lbf).

Pressure-area method: the only axial end force on an open-ended string at the shoe is
the hydrostatic pressure acting on the steel cross-section, F_shoe = -P * A_steel
(compression). Self-weight is added above the shoe. This is exact for a vertical well
and conservative for inclined wells (ignores wall friction and the cos(inc) reduction
in weight, both of which reduce hanging tension in a static check).
"""
from __future__ import annotations

from collections.abc import Callable

import numpy as np

from casingdesign.catalog import PipeSpec
from casingdesign.well import CasingString, Trajectory, ppg_to_gradient

STEEL_DENSITY_LB_PER_IN3 = 0.2833


def weight_per_ft(spec: PipeSpec) -> float:
    """Plain-end weight from steel area (lb/ft). Nominal weight is used for cost only."""
    return spec.geometry.area * STEEL_DENSITY_LB_PER_IN3 * 12.0


WeightProfile = Callable[[np.ndarray], np.ndarray]  # lb/ft as a function of MD


def _weight_profile(spec_or_design) -> WeightProfile:
    if hasattr(spec_or_design, "weight_per_ft"):
        return spec_or_design.weight_per_ft
    w = weight_per_ft(spec_or_design)
    return lambda md: np.full_like(np.asarray(md, dtype=float), w)


def _end_area(spec_or_design) -> float:
    """Steel area at the shoe (bottom section for a tapered design), in^2."""
    if hasattr(spec_or_design, "sections"):
        return spec_or_design.sections[-1].spec.geometry.area
    return spec_or_design.geometry.area


def _hanging_weight(md: np.ndarray, string: CasingString, traj: Trajectory,
                    weight: WeightProfile) -> np.ndarray:
    """Air weight hanging below each MD. Uses cos(inc) component so highly deviated
    sections contribute their vertical weight only (friction ignored). `weight` may
    vary with MD for tapered strings."""
    grid = np.linspace(string.hanger_md, string.shoe_md, 801)
    inc = np.radians(traj.inclination(grid))
    mid = 0.5 * (grid[1:] + grid[:-1])
    seg = np.diff(grid) * np.cos(0.5 * (inc[1:] + inc[:-1])) * weight(mid)
    cum = np.concatenate([[0.0], np.cumsum(seg)])  # lbf of vertical weight from hanger
    total = cum[-1]
    return total - np.interp(md, grid, cum)


def running_axial(md: np.ndarray, string: CasingString, spec, traj: Trajectory,
                  overpull: float | None = None) -> np.ndarray:
    """Axial force while running in mud, at the moment of maximum overpull at surface.
    `spec` is a PipeSpec or a StringDesign."""
    p_shoe = ppg_to_gradient(string.mud_weight) * traj.tvd(string.shoe_md)
    f_end = -p_shoe * _end_area(spec)
    f = _hanging_weight(md, string, traj, _weight_profile(spec)) + f_end
    op = string.overpull if overpull is None else overpull
    return f + op


def as_cemented_axial(md: np.ndarray, string: CasingString, spec,
                      traj: Trajectory) -> np.ndarray:
    """Axial force locked in when cement sets: mud inside, cement outside at the shoe.

    The open-ended shoe sees the annular (cement) pressure on the steel area. This
    is the base state onto which service pressure changes act (ballooning), which the
    MVP neglects; the resulting profile is used for the triaxial and biaxial checks.
    """
    shoe_tvd = traj.tvd(string.shoe_md)
    toc_tvd = traj.tvd(string.toc_md)
    tail_top_tvd = traj.tvd(max(string.toc_md, string.shoe_md - string.tail_length))
    p_shoe = (ppg_to_gradient(string.mud_weight) * toc_tvd
              + ppg_to_gradient(string.cement_lead_ppg) * (tail_top_tvd - toc_tvd)
              + ppg_to_gradient(string.cement_tail_ppg) * (shoe_tvd - tail_top_tvd))
    f_end = -p_shoe * _end_area(spec)
    return _hanging_weight(md, string, traj, _weight_profile(spec)) + f_end
