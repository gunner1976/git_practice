"""Well description: trajectory, pressure environment, fluids and casing program.

Pydantic models so a well can be written as JSON/YAML by hand, imported from a
planning tool, or built from a UI, and validated before any calculation runs.
"""
from __future__ import annotations

import math
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field, model_validator

PSI_PER_FT_PER_PPG = 0.052


def ppg_to_gradient(ppg: float) -> float:
    """Fluid density (ppg) to pressure gradient (psi/ft)."""
    return PSI_PER_FT_PER_PPG * ppg


def gradient_to_ppg(psi_per_ft: float) -> float:
    return psi_per_ft / PSI_PER_FT_PER_PPG


# ---------------------------------------------------------------------------
# Trajectory
# ---------------------------------------------------------------------------
class SurveyStation(BaseModel):
    md: float = Field(ge=0, description="measured depth, ft")
    inclination: float = Field(ge=0, le=180, description="deg from vertical")
    azimuth: float = Field(ge=0, lt=360, description="deg")


class Trajectory(BaseModel):
    """Survey stations; TVD and dogleg severity computed by minimum curvature."""

    stations: list[SurveyStation]

    @model_validator(mode="after")
    def _check(self):
        if len(self.stations) < 1:
            raise ValueError("trajectory needs at least one station")
        mds = [s.md for s in self.stations]
        if mds != sorted(mds) or len(set(mds)) != len(mds):
            raise ValueError("stations must be strictly increasing in MD")
        if self.stations[0].md != 0.0:
            # prepend a surface station to anchor TVD = 0 at MD = 0
            self.stations.insert(0, SurveyStation(md=0.0, inclination=0.0, azimuth=0.0))
        return self

    @classmethod
    def vertical(cls, td: float) -> Trajectory:
        return cls(stations=[SurveyStation(md=0, inclination=0, azimuth=0),
                             SurveyStation(md=td, inclination=0, azimuth=0)])

    def _compute(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Returns arrays md, tvd, inclination, dls (deg/100ft) at each station."""
        md = np.array([s.md for s in self.stations])
        inc = np.radians([s.inclination for s in self.stations])
        azi = np.radians([s.azimuth for s in self.stations])
        tvd = np.zeros_like(md)
        dls = np.zeros_like(md)
        for i in range(1, len(md)):
            dmd = md[i] - md[i - 1]
            i1, i2, a1, a2 = inc[i - 1], inc[i], azi[i - 1], azi[i]
            cos_dl = math.cos(i2 - i1) - math.sin(i1) * math.sin(i2) * (1 - math.cos(a2 - a1))
            dl = math.acos(max(-1.0, min(1.0, cos_dl)))
            rf = 1.0 if dl < 1e-9 else 2.0 / dl * math.tan(dl / 2.0)
            tvd[i] = tvd[i - 1] + dmd / 2.0 * (math.cos(i1) + math.cos(i2)) * rf
            dls[i] = math.degrees(dl) / dmd * 100.0 if dmd > 0 else 0.0
        return md, tvd, np.degrees(inc), dls

    @property
    def td(self) -> float:
        return self.stations[-1].md

    def tvd(self, md) -> np.ndarray | float:
        m, t, _, _ = self._compute()
        return np.interp(md, m, t)

    def inclination(self, md) -> np.ndarray | float:
        m, _, inc, _ = self._compute()
        return np.interp(md, m, inc)

    def dls(self, md) -> np.ndarray | float:
        """Dogleg severity of the interval containing md (step function), deg/100 ft."""
        m, _, _, d = self._compute()
        idx = np.clip(np.searchsorted(m, md, side="right"), 1, len(m) - 1)
        return d[idx]


# ---------------------------------------------------------------------------
# Pressure environment
# ---------------------------------------------------------------------------
class DepthValue(BaseModel):
    tvd: float = Field(ge=0)
    value: float


class Profile(BaseModel):
    """Piecewise-linear property versus TVD (e.g. pore pressure in ppg EMW)."""

    points: list[DepthValue]
    unit: str = "ppg"

    @model_validator(mode="after")
    def _sorted(self):
        tvds = [p.tvd for p in self.points]
        if tvds != sorted(tvds):
            raise ValueError("profile points must be sorted by TVD")
        return self

    @classmethod
    def constant(cls, value: float, unit: str = "ppg") -> Profile:
        return cls(points=[DepthValue(tvd=0, value=value)], unit=unit)

    def at(self, tvd) -> np.ndarray | float:
        xs = [p.tvd for p in self.points]
        ys = [p.value for p in self.points]
        return np.interp(tvd, xs, ys)

    def pressure(self, tvd) -> np.ndarray | float:
        """Pressure (psi) at TVD if this profile is an EMW gradient in ppg."""
        if self.unit != "ppg":
            raise ValueError("pressure() requires a ppg EMW profile")
        return ppg_to_gradient(self.at(tvd)) * np.asarray(tvd, dtype=float)


class Formation(BaseModel):
    pore_pressure: Profile = Field(description="pore pressure EMW, ppg vs TVD")
    fracture_gradient: Profile = Field(description="fracture gradient EMW, ppg vs TVD")
    surface_temperature_f: float = 70.0
    geothermal_gradient_f_per_100ft: float = 1.2
    sour: bool = False

    def temperature(self, tvd) -> np.ndarray | float:
        """Static (geothermal) temperature, deg F, at TVD."""
        return self.surface_temperature_f + self.geothermal_gradient_f_per_100ft * np.asarray(
            tvd, dtype=float) / 100.0


class YieldDerating(BaseModel):
    """Linear reduction of yield strength with temperature above a reference.

    factor = max(floor, 1 - slope (T - T_ref)). Default 0.03 % per deg F above 70 F is
    a conservative envelope for carbon/low-alloy casing grades (manufacturer data
    typically 0.02-0.03 %/F); replace with grade-specific data when available. All
    ratings scale with yield (joint strength approximately, since it also depends on
    tensile strength).
    """

    enabled: bool = True
    slope_per_f: float = Field(default=0.0003, ge=0)
    reference_f: float = 70.0
    floor: float = Field(default=0.80, gt=0, le=1)

    def factor(self, temperature_f) -> np.ndarray:
        t = np.asarray(temperature_f, dtype=float)
        if not self.enabled:
            return np.ones_like(t)
        return np.maximum(self.floor, 1.0 - self.slope_per_f * np.maximum(t - self.reference_f, 0.0))


# ---------------------------------------------------------------------------
# Casing program
# ---------------------------------------------------------------------------
StringType = Literal["conductor", "surface", "intermediate", "production", "liner"]


class CasingString(BaseModel):
    name: str
    type: StringType
    od: float = Field(gt=0, description="casing OD, in")
    hole_size: float = Field(gt=0, description="open hole size drilled for this string, in")
    hanger_md: float = Field(ge=0, default=0.0, description="top of string (0 for surface)")
    shoe_md: float = Field(gt=0)
    toc_md: float = Field(ge=0, description="top of cement, MD")
    mud_weight: float = Field(gt=0, description="mud weight string is run/cemented in, ppg")
    cement_lead_ppg: float = Field(gt=0, default=12.5)
    cement_tail_ppg: float = Field(gt=0, default=15.8)
    tail_length: float = Field(ge=0, default=500.0, description="length of tail slurry above shoe")
    next_hole_mud_weight: float | None = Field(
        default=None, description="max mud weight drilled below this shoe, ppg")
    next_section_td_md: float | None = Field(default=None, description="TD of next hole section")
    overpull: float = Field(ge=0, default=100_000.0, description="running overpull, lbf")
    pressure_test: float | None = Field(default=None, description="surface test pressure, psi")

    # Well-control burst case for strings drilled ahead below (surface / intermediate).
    # kick_volume_bbl = None -> conservative gas-to-surface case; a volume -> kick
    # tolerance case with that influx. include_gas_to_surface keeps both.
    kick_volume_bbl: float | None = Field(default=None, gt=0, description="influx volume, bbl")
    kick_intensity_ppg: float = Field(
        default=0.5, ge=0, description="formation pressure in excess of next mud weight, ppg")
    max_surface_pressure: float | None = Field(
        default=None, gt=0, description="BOP / wellhead working pressure cap, psi")
    include_gas_to_surface: bool = False

    # Production-string specific
    packer_md: float | None = None
    packer_fluid_ppg: float | None = None
    shut_in_tubing_pressure: float | None = Field(default=None, description="SITP, psi")
    frac_surface_pressure: float | None = Field(
        default=None, description="max surface treating pressure for stimulation, psi")
    frac_fluid_ppg: float | None = None

    @model_validator(mode="after")
    def _depths(self):
        if self.toc_md > self.shoe_md:
            raise ValueError("TOC must be above the shoe")
        if self.hanger_md >= self.shoe_md:
            raise ValueError("hanger must be above shoe")
        if self.type == "liner" and self.hanger_md <= 0:
            raise ValueError("a liner must hang below surface (hanger_md > 0)")
        if self.type != "liner" and self.hanger_md > 0:
            raise ValueError("only liners may have hanger_md > 0 (use type='liner')")
        return self

    @property
    def is_liner(self) -> bool:
        return self.type == "liner"

    @property
    def length(self) -> float:
        return self.shoe_md - self.hanger_md


class DesignFactors(BaseModel):
    """Minimum acceptable design factors (rating / load). Typical onshore defaults."""

    burst: float = 1.10
    collapse: float = 1.00
    tension: float = 1.60
    triaxial: float = 1.25


class Well(BaseModel):
    name: str
    trajectory: Trajectory
    formation: Formation
    strings: list[CasingString]
    design_factors: DesignFactors = DesignFactors()
    yield_derating: YieldDerating = YieldDerating()
    gas_gradient_psi_ft: float = 0.1  # dry gas column assumption for kick cases
    seawater_or_fresh_gradient_psi_ft: float = 0.433  # backup fluid for degraded cement/mud

    def string(self, name: str) -> CasingString:
        for s in self.strings:
            if s.name == name:
                return s
        raise KeyError(name)

    def parent_of(self, liner: CasingString) -> CasingString | None:
        """The string a liner hangs in: the smallest-OD string larger than the liner
        whose interval covers the liner hanger."""
        if not liner.is_liner:
            return None
        hosts = [s for s in self.strings if s is not liner and s.od > liner.od
                 and s.hanger_md <= liner.hanger_md < s.shoe_md]
        return min(hosts, key=lambda s: s.od) if hosts else None

    def liners_of(self, parent: CasingString) -> list[CasingString]:
        """Liners hung (directly) in this string, shallowest first."""
        return sorted((s for s in self.strings if s.is_liner and self.parent_of(s) is parent),
                      key=lambda s: s.hanger_md)

    def warnings(self) -> list[str]:
        """Non-fatal design checks a reviewer should see."""
        out: list[str] = []
        for s in self.strings:
            if s.shoe_md > self.trajectory.td:
                out.append(f"{s.name}: shoe {s.shoe_md:.0f} ft is below the surveyed TD "
                           f"{self.trajectory.td:.0f} ft")
            if s.is_liner:
                parent = self.parent_of(s)
                if parent is None:
                    out.append(f"{s.name}: no parent casing found covering the hanger at "
                               f"{s.hanger_md:.0f} ft")
                else:
                    if s.toc_md > s.hanger_md:
                        out.append(f"{s.name}: TOC {s.toc_md:.0f} ft is below the liner top "
                                   f"{s.hanger_md:.0f} ft (uncemented lap)")
                    if parent.shoe_md - s.hanger_md < 200:
                        out.append(f"{s.name}: only {parent.shoe_md - s.hanger_md:.0f} ft overlap "
                                   f"inside {parent.name}")
        return out
