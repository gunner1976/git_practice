"""Standard onshore load cases.

Each load case yields internal and external pressure profiles (psi) along the string
on a common MD grid. The external profile is the "backup" pressure that offsets the
internal load. Conventions follow common operator practice for onshore wells and are
documented per case so they can be reviewed and tightened for a given basin.

Sign conventions: burst load = Pi - Pe (>0 governs burst), collapse load = Pe - Pi.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from casingdesign.well import CasingString, Well, ppg_to_gradient


class LoadKind(str, Enum):
    BURST = "burst"
    COLLAPSE = "collapse"
    AXIAL = "axial"


@dataclass(frozen=True)
class LoadProfile:
    md: np.ndarray
    internal: np.ndarray
    external: np.ndarray

    @property
    def burst_load(self) -> np.ndarray:
        return np.maximum(self.internal - self.external, 0.0)

    @property
    def collapse_load(self) -> np.ndarray:
        return np.maximum(self.external - self.internal, 0.0)


@dataclass(frozen=True)
class LoadCase:
    name: str
    kind: LoadKind
    profile: LoadProfile
    axial_state: str  # "running" or "as_cemented" - which axial profile accompanies it
    description: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def depth_grid(string: CasingString, step: float = 50.0) -> np.ndarray:
    n = max(2, round(string.length / step) + 1)
    return np.linspace(string.hanger_md, string.shoe_md, n)


def mud_hydrostatic(well: Well, md: np.ndarray, ppg: float) -> np.ndarray:
    return ppg_to_gradient(ppg) * well.trajectory.tvd(md)


def annulus_as_cemented(well: Well, string: CasingString, md: np.ndarray) -> np.ndarray:
    """External pressure with wet cement in place: mud above TOC, lead then tail below."""
    tvd = well.trajectory.tvd(md)
    toc_tvd = well.trajectory.tvd(string.toc_md)
    tail_top_md = max(string.toc_md, string.shoe_md - string.tail_length)
    tail_top_tvd = well.trajectory.tvd(tail_top_md)
    g_mud = ppg_to_gradient(string.mud_weight)
    g_lead = ppg_to_gradient(string.cement_lead_ppg)
    g_tail = ppg_to_gradient(string.cement_tail_ppg)
    p = g_mud * np.minimum(tvd, toc_tvd)
    p += g_lead * np.clip(tvd - toc_tvd, 0.0, tail_top_tvd - toc_tvd)
    p += g_tail * np.clip(tvd - tail_top_tvd, 0.0, None)
    return p


def burst_backup(well: Well, string: CasingString, md: np.ndarray) -> np.ndarray:
    """External pressure credited against burst after cement has set.

    Above TOC: mud hydrostatic (mud is assumed to remain, but degraded to no better than
    its original density). Below TOC: the lesser of pore pressure and mud hydrostatic;
    set cement is not credited with transmitting more than formation pressure.
    """
    tvd = well.trajectory.tvd(md)
    mud = mud_hydrostatic(well, md, string.mud_weight)
    pore = well.formation.pore_pressure.pressure(tvd)
    below_toc = md >= string.toc_md
    return np.where(below_toc, np.minimum(mud, pore), mud)


def collapse_external(well: Well, string: CasingString, md: np.ndarray) -> np.ndarray:
    """External pressure for collapse after cementing: mud hydrostatic over the full
    length (set cement and the cement sheath are not credited - conservative)."""
    return mud_hydrostatic(well, md, string.mud_weight)


# ---------------------------------------------------------------------------
# Load cases
# ---------------------------------------------------------------------------
def _via(src: CasingString, s: CasingString) -> str:
    return "" if src is s else f" (via {src.name})"


def pressure_test(well: Well, s: CasingString, md: np.ndarray) -> LoadCase | None:
    if s.pressure_test is None:
        return None
    internal = s.pressure_test + mud_hydrostatic(well, md, s.mud_weight)
    # Test is performed with cement still wet (green cement test) -> backup is the
    # as-cemented annulus; this is usually the more severe of wet/set conditions.
    external = annulus_as_cemented(well, s, md)
    return LoadCase("Pressure test", LoadKind.BURST, LoadProfile(md, internal, external),
                    "as_cemented", f"{s.pressure_test:.0f} psi on {s.mud_weight} ppg mud, "
                    "green cement backup")


def _cap_profile(well: Well, s: CasingString, md: np.ndarray, internal: np.ndarray,
                 notes: list[str]) -> np.ndarray:
    """Shift a well-control profile down so the shoe never exceeds fracture pressure
    (the formation breaks down first) and surface pressure never exceeds the BOP cap.
    `s` is the string whose shoe is open to formation (a liner's, when inherited)."""
    shoe_tvd = well.trajectory.tvd(s.shoe_md)
    p_frac = well.formation.fracture_gradient.pressure(shoe_tvd)
    if s.shoe_md <= md[-1]:
        p_shoe = float(np.interp(s.shoe_md, md, internal))
    else:  # shoe below this grid: continue the last gradient (in TVD) down to it
        tvd = well.trajectory.tvd(md)
        grad = (internal[-1] - internal[-2]) / max(tvd[-1] - tvd[-2], 1e-9)
        p_shoe = float(internal[-1] + grad * (shoe_tvd - tvd[-1]))
    if p_shoe > p_frac:
        internal = internal - (p_shoe - p_frac)
        notes.append(f"limited by frac at shoe ({p_frac:.0f} psi)")
    if s.max_surface_pressure is not None and internal[0] > s.max_surface_pressure:
        internal = internal - (internal[0] - s.max_surface_pressure)
        notes.append(f"capped at {s.max_surface_pressure:.0f} psi BOP rating")
    return np.maximum(internal, 0.0)


def gas_kick(well: Well, s: CasingString, md: np.ndarray,
             inner_diameter: float | None, src: CasingString | None = None) -> LoadCase | None:
    """Kick tolerance: an influx of `kick_volume_bbl` gas sits at the top of the casing
    (worst case for burst) with next-section mud below it, the whole column anchored
    at formation pressure at the next section TD. Kick intensity is defined, as is
    conventional, as the formation pressure in excess of the mud weight in use:
    P_formation = 0.052 (MW_next + intensity) TD_tvd.

    Surface pressure = P_formation - g_mud (TD_tvd - h_tvd) - g_gas h_tvd, where the
    bubble height h is the influx volume over the casing capacity. Capped by fracture
    pressure at the shoe and by the BOP rating if given.
    """
    src = src or s
    if src.type not in ("surface", "intermediate", "liner") or src.kick_volume_bbl is None:
        return None
    if src.next_hole_mud_weight is None or src.next_section_td_md is None:
        return None
    traj = well.trajectory
    cid = inner_diameter if inner_diameter is not None else s.od - 0.9  # typical wall
    capacity_bbl_per_ft = cid**2 / 1029.4
    h_md = src.kick_volume_bbl / capacity_bbl_per_ft
    h_md = min(h_md, s.shoe_md - s.hanger_md)
    h_tvd = traj.tvd(s.hanger_md + h_md) - traj.tvd(s.hanger_md)
    td_tvd = traj.tvd(src.next_section_td_md)
    g_mud = ppg_to_gradient(src.next_hole_mud_weight)
    p_form = (g_mud + ppg_to_gradient(src.kick_intensity_ppg)) * td_tvd
    g_gas = well.gas_gradient_psi_ft
    tvd = traj.tvd(md)
    tvd0 = traj.tvd(s.hanger_md)
    p_surface = p_form - g_mud * (td_tvd - tvd0 - h_tvd) - g_gas * h_tvd
    depth = tvd - tvd0
    internal = p_surface + np.where(depth <= h_tvd, g_gas * depth,
                                    g_gas * h_tvd + g_mud * (depth - h_tvd))
    notes = [(f"{src.kick_volume_bbl:g} bbl gas at top of casing (ID {cid:.2f} in, "
              f"{h_md:.0f} ft), {src.kick_intensity_ppg} ppg intensity, "
              f"formation {p_form:.0f} psi at {src.next_section_td_md:.0f} ft MD")]
    internal = _cap_profile(well, src, md, internal, notes)
    external = burst_backup(well, s, md)
    return LoadCase("Gas kick" + _via(src, s), LoadKind.BURST,
                    LoadProfile(md, internal, external), "as_cemented", "; ".join(notes))


def gas_to_surface(well: Well, s: CasingString, md: np.ndarray,
                   src: CasingString | None = None) -> LoadCase | None:
    """Displacement to gas: shoe at fracture pressure, dry gas gradient to surface.

    Applies to strings that will have a BOP on them while drilling ahead
    (surface and intermediate). Capped at the fracture pressure at the shoe because
    the formation will break down before the casing sees more. Used when no kick
    volume is given, or when include_gas_to_surface is set.
    """
    src = src or s
    if src.type not in ("surface", "intermediate", "liner"):
        return None
    if src.is_liner and src.next_section_td_md is None:
        return None  # a production liner is not drilled ahead below
    if src.kick_volume_bbl is not None and not src.include_gas_to_surface:
        return None
    traj = well.trajectory
    tvd = traj.tvd(md)
    shoe_tvd = traj.tvd(src.shoe_md)
    p_frac_shoe = well.formation.fracture_gradient.pressure(shoe_tvd)
    internal = p_frac_shoe - well.gas_gradient_psi_ft * (shoe_tvd - tvd)
    notes = [(f"frac at shoe {p_frac_shoe:.0f} psi, gas gradient "
              f"{well.gas_gradient_psi_ft} psi/ft, pore/mud backup")]
    internal = _cap_profile(well, src, md, internal, notes)
    external = burst_backup(well, s, md)
    return LoadCase("Gas to surface" + _via(src, s), LoadKind.BURST,
                    LoadProfile(md, internal, external), "as_cemented", "; ".join(notes))


def tubing_leak(well: Well, s: CasingString, md: np.ndarray,
                src: CasingString | None = None) -> LoadCase | None:
    """Tubing leak near surface: SITP applied on top of packer fluid down to the packer."""
    src = src or s
    if src.type not in ("production", "liner") or src.shut_in_tubing_pressure is None:
        return None
    pf = src.packer_fluid_ppg if src.packer_fluid_ppg is not None else src.mud_weight
    packer_md = src.packer_md if src.packer_md is not None else src.shoe_md
    tvd = well.trajectory.tvd(md)
    packer_tvd = well.trajectory.tvd(packer_md)
    internal = src.shut_in_tubing_pressure + ppg_to_gradient(pf) * np.minimum(tvd, packer_tvd)
    # Below the packer the casing sees the pore (reservoir) pressure continuation; we
    # conservatively continue the packer-fluid gradient.
    internal = np.where(tvd > packer_tvd,
                        internal + ppg_to_gradient(pf) * (tvd - packer_tvd), internal)
    external = burst_backup(well, s, md)
    return LoadCase("Tubing leak" + _via(src, s), LoadKind.BURST,
                    LoadProfile(md, internal, external), "as_cemented",
                    f"SITP {src.shut_in_tubing_pressure:.0f} psi on {pf} ppg packer fluid")


def stimulation(well: Well, s: CasingString, md: np.ndarray,
                src: CasingString | None = None) -> LoadCase | None:
    """Fracturing down casing: surface treating pressure + frac fluid hydrostatic."""
    src = src or s
    if src.frac_surface_pressure is None:
        return None
    ff = src.frac_fluid_ppg if src.frac_fluid_ppg is not None else 8.5
    internal = src.frac_surface_pressure + mud_hydrostatic(well, md, ff)
    external = burst_backup(well, s, md)
    return LoadCase("Stimulation" + _via(src, s), LoadKind.BURST,
                    LoadProfile(md, internal, external), "as_cemented",
                    f"{src.frac_surface_pressure:.0f} psi surface treating pressure on "
                    f"{ff} ppg frac fluid")


def full_evacuation(well: Well, s: CasingString, md: np.ndarray) -> LoadCase:
    """Casing fully evacuated to atmospheric (lost circulation / depletion / gas lift)."""
    internal = np.zeros_like(md)
    external = collapse_external(well, s, md)
    return LoadCase("Full evacuation", LoadKind.COLLAPSE, LoadProfile(md, internal, external),
                    "as_cemented", f"empty casing, {s.mud_weight} ppg mud backup outside")


def cementing(well: Well, s: CasingString, md: np.ndarray) -> LoadCase:
    """End of displacement, before plug bump: mud inside, full cement column outside."""
    internal = mud_hydrostatic(well, md, s.mud_weight)
    external = annulus_as_cemented(well, s, md)
    return LoadCase("Cementing", LoadKind.COLLAPSE, LoadProfile(md, internal, external),
                    "running", f"lead {s.cement_lead_ppg} / tail {s.cement_tail_ppg} ppg "
                    f"outside, {s.mud_weight} ppg displacement fluid inside")


def lost_returns(well: Well, s: CasingString, md: np.ndarray) -> LoadCase | None:
    """Partial evacuation while drilling the next section: the mud column falls until it
    balances the lowest pore pressure in the next section with the next mud weight."""
    if s.next_hole_mud_weight is None or s.next_section_td_md is None:
        return None
    traj = well.trajectory
    td_tvd = traj.tvd(s.next_section_td_md)
    # Minimum pore pressure gradient in the next hole section (worst-case thief zone):
    probe = np.linspace(traj.tvd(s.shoe_md), td_tvd, 50)
    p_pore_min = float(np.min(well.formation.pore_pressure.pressure(probe) /
                              np.maximum(probe, 1.0)) * td_tvd)
    g_next = ppg_to_gradient(s.next_hole_mud_weight)
    level_tvd = max(0.0, td_tvd - p_pore_min / g_next)  # TVD of fluid level
    tvd = traj.tvd(md)
    internal = g_next * np.clip(tvd - level_tvd, 0.0, None)
    external = collapse_external(well, s, md)
    return LoadCase("Lost returns", LoadKind.COLLAPSE, LoadProfile(md, internal, external),
                    "as_cemented", f"{s.next_hole_mud_weight} ppg mud level drops to "
                    f"{level_tvd:.0f} ft TVD")


def running_case(well: Well, s: CasingString, md: np.ndarray) -> LoadCase:
    """Running in hole with overpull; pressures balanced (mud inside and out)."""
    p = mud_hydrostatic(well, md, s.mud_weight)
    return LoadCase("Running + overpull", LoadKind.AXIAL, LoadProfile(md, p, p), "running",
                    f"{s.overpull:.0f} lbf overpull in {s.mud_weight} ppg mud")


def standard_load_cases(well: Well, s: CasingString, step: float = 50.0,
                        inner_diameter: float | None = None) -> list[LoadCase]:
    """All applicable load cases on a common MD grid. `inner_diameter` (top of string)
    is only needed by the gas kick case for the influx height."""
    md = depth_grid(s, step)
    builders = [pressure_test, gas_to_surface, tubing_leak, stimulation,
                full_evacuation, cementing, lost_returns, running_case]
    cases = [lc for b in builders if (lc := b(well, s, md)) is not None]
    kick = gas_kick(well, s, md, inner_diameter)
    if kick is not None:
        cases.insert(1, kick)
    # Loads a liner hung in this string imposes on it: its well-control cases while
    # drilling ahead below the liner, and its production cases (the parent casing
    # carries the same tubing-leak / stimulation pressure down to the liner top).
    for liner in well.liners_of(s):
        for b in (gas_to_surface, tubing_leak, stimulation):
            lc = b(well, s, md, src=liner)
            if lc is not None:
                cases.append(lc)
        lc = gas_kick(well, s, md, inner_diameter, src=liner)
        if lc is not None:
            cases.append(lc)
    return cases
