"""Triaxial (von Mises equivalent) stress analysis of a thick-walled cylinder.

Lame equations give radial and tangential (hoop) stress at any radius for internal
pressure pi and external pressure po. Axial stress is uniform over the section and
bending adds +/- M c / I at the outer fibre. The VME stress is compared to the
yield strength to give the triaxial design factor (API TR 5C3 Annex / ISO 10400).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .api5c3 import PipeGeometry


@dataclass(frozen=True)
class StressState:
    radial: float
    tangential: float
    axial: float

    @property
    def vme(self) -> float:
        return vme_stress(self.radial, self.tangential, self.axial)


def lame_stresses(
    geom: PipeGeometry, p_internal: float, p_external: float, radius: float
) -> tuple[float, float]:
    """Radial and tangential stress (psi) at `radius` (in). Compression negative."""
    ri = geom.id / 2.0
    ro = geom.od / 2.0
    k = (p_internal * ri**2 - p_external * ro**2) / (ro**2 - ri**2)
    m = (p_internal - p_external) * ri**2 * ro**2 / (ro**2 - ri**2)
    sigma_r = k - m / radius**2
    sigma_t = k + m / radius**2
    return sigma_r, sigma_t


def vme_stress(sigma_r: float, sigma_t: float, sigma_a: float) -> float:
    """Von Mises equivalent stress for principal stresses (no shear)."""
    return math.sqrt(
        0.5 * ((sigma_a - sigma_t) ** 2 + (sigma_t - sigma_r) ** 2 + (sigma_r - sigma_a) ** 2)
    )


def axial_stress_from_load(geom: PipeGeometry, axial_force: float) -> float:
    """Uniform axial stress, psi, from axial force in lbf (tension positive)."""
    return axial_force / geom.area


def bending_stress(geom: PipeGeometry, dogleg_deg_per_100ft: float) -> float:
    """Outer-fibre bending stress, psi, from a dogleg severity in deg/100 ft.

    sigma_b = E * (D/2) / R, with R = 180*100*12 / (pi * DLS) inches.
    Equivalent to the common field form 218 * D * DLS (psi, D in inches).
    """
    if dogleg_deg_per_100ft == 0.0:
        return 0.0
    from .api5c3 import E_STEEL

    radius_in = (180.0 * 100.0 * 12.0) / (math.pi * dogleg_deg_per_100ft)
    return E_STEEL * (geom.od / 2.0) / radius_in


def max_vme(
    geom: PipeGeometry,
    p_internal: float,
    p_external: float,
    axial_force: float,
    dogleg_deg_per_100ft: float = 0.0,
) -> float:
    """Maximum VME stress over the wall (inner and outer fibre, +/- bending), psi.

    Bending is only applied at the outer fibre where it is maximal; it is combined
    with the Lame stresses at that radius. Checks the inner wall without bending
    as well, since pressure-driven VME peaks there.
    """
    sa = axial_stress_from_load(geom, axial_force)
    sb = bending_stress(geom, dogleg_deg_per_100ft)
    ri, ro = geom.id / 2.0, geom.od / 2.0
    candidates = []
    sr, st = lame_stresses(geom, p_internal, p_external, ri)
    candidates.append(vme_stress(sr, st, sa))
    sr, st = lame_stresses(geom, p_internal, p_external, ro)
    for sign in (1.0, -1.0):
        candidates.append(vme_stress(sr, st, sa + sign * sb))
    # Bending also acts at the inner fibre scaled by ri/ro.
    sr, st = lame_stresses(geom, p_internal, p_external, ri)
    for sign in (1.0, -1.0):
        candidates.append(vme_stress(sr, st, sa + sign * sb * ri / ro))
    return max(candidates)


def triaxial_design_factor(
    geom: PipeGeometry,
    yield_strength: float,
    p_internal: float,
    p_external: float,
    axial_force: float,
    dogleg_deg_per_100ft: float = 0.0,
) -> float:
    """Yp / max VME. Returns inf if the pipe is unstressed."""
    vme = max_vme(geom, p_internal, p_external, axial_force, dogleg_deg_per_100ft)
    return math.inf if vme == 0.0 else yield_strength / vme
