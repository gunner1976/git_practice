"""Import a well from a Landmark EDM / COMPASS / StressCheck XML export.

An EDM export is one flat XML document whose child elements are table rows
(``CD_WELL``, ``CD_WELLBORE``, ``CD_SURVEY_STATION``, ``CD_PORE_PRESSURE``,
``CD_ASSEMBLY``, ``CD_ASSEMBLY_COMP`` ...) with all data in attributes. Files are
large, so this reader streams with ``iterparse`` and keeps only what the design
needs. Table and attribute names follow the schema documented by the Apache-2.0
``welleng`` project (``welleng.exchange.edm_stream``); the mapping onto our well
model, and the assumptions it has to make, are ours and are reported as warnings.

What is imported
- trajectory: the longest survey (definitive if present) for the wellbore
- pore / fracture pressure: psi vs TVD -> EMW ppg (PLAN phase preferred)
- temperature: surface temperature and geothermal gradient by least squares
- strings: Casing / Liner assemblies and their casing components -> CasingString
  plus the catalog pipe spec (OD, weight, grade, connection) for each
- Landmark's stored burst / collapse / axial ratings per component, returned as an
  oracle so they can be compared with our API 5C3 values

What EDM does not carry for us (mud weights, TOC, cement, test pressures, kick
parameters) is filled with conservative defaults and flagged.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import numpy as np

from casingdesign.catalog import Catalog, PipeSpec
from casingdesign.well import (
    CasingString,
    DepthValue,
    Formation,
    Profile,
    SurveyStation,
    Trajectory,
    Well,
    gradient_to_ppg,
)

FEET_PER_METER = 3.280839895


def _f(a: dict, key: str) -> float | None:
    v = a.get(key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


@dataclass
class StoredRating:
    """Landmark's stored component ratings (verbatim; units as stored: psi, klbf)."""

    string: str
    description: str
    burst_psi: float | None
    collapse_psi: float | None
    axial_klbf: float | None


@dataclass
class EDMImportResult:
    well: Well
    specs: dict[str, PipeSpec]  # string name -> catalog spec resolved from the components
    stored_ratings: list[StoredRating]
    warnings: list[str] = field(default_factory=list)

    def rating_comparison(self) -> list[dict]:
        """Our API 5C3 ratings next to Landmark's stored ones, per string."""
        out = []
        for r in self.stored_ratings:
            spec = self.specs.get(r.string)
            if spec is None:
                continue
            out.append({
                "string": r.string, "pipe": spec.label,
                "burst_ours": spec.burst, "burst_stored": r.burst_psi,
                "collapse_ours": spec.collapse, "collapse_stored": r.collapse_psi,
                "axial_ours_klbf": spec.tension_rating / 1000.0,
                "axial_stored_klbf": r.axial_klbf,
            })
        return out


class _Tables:
    """The subset of EDM tables we keep, indexed for lookup."""

    WANTED: ClassVar[frozenset[str]] = frozenset({
        "CD_WELL", "CD_WELLBORE", "CD_SURVEY_HEADER", "CD_SURVEY_STATION",
        "CD_DEFINITIVE_SURVEY_HEADER", "CD_DEFINITIVE_SURVEY_STATION",
        "CD_PORE_PRESSURE_GROUP", "CD_PORE_PRESSURE", "CD_FRAC_GRADIENT_GROUP",
        "CD_FRAC_GRADIENT", "CD_TEMP_GRADIENT_GROUP", "CD_TEMP_GRADIENT",
        "CD_ASSEMBLY", "CD_ASSEMBLY_COMP", "CD_CASE",
    })

    def __init__(self, path: str | Path):
        self.rows: dict[str, list[dict]] = {t: [] for t in self.WANTED}
        for _, el in ET.iterparse(str(path), events=("end",)):
            tag = el.tag.split("}")[-1]
            if tag in self.WANTED:
                self.rows[tag].append(dict(el.attrib))
            el.clear()

    def __getitem__(self, tag: str) -> list[dict]:
        return self.rows[tag]


def list_wellbores(path: str | Path) -> list[tuple[str, str, str]]:
    """(wellbore_id, wellbore_name, well_name) for every wellbore in the file."""
    t = _Tables(path)
    wells = {w.get("well_id"): w.get("well_common_name", "") for w in t["CD_WELL"]}
    return [(wb["wellbore_id"], wb.get("wellbore_name", ""), wells.get(wb.get("well_id"), ""))
            for wb in t["CD_WELLBORE"]]


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------
def _trajectory(t: _Tables, wellbore_id: str, k: float, warnings: list[str]) -> Trajectory:
    """Longest survey for the wellbore; definitive survey preferred."""
    for hdr_tag, st_tag, key in (
        ("CD_DEFINITIVE_SURVEY_HEADER", "CD_DEFINITIVE_SURVEY_STATION", "def_survey_header_id"),
        ("CD_SURVEY_HEADER", "CD_SURVEY_STATION", "survey_header_id"),
    ):
        headers = [h for h in t[hdr_tag] if h.get("wellbore_id") == wellbore_id]
        if not headers:
            continue
        best = max(headers, key=lambda h: _f(h, "md_max") or 0.0)
        hid = best.get(key) or best.get("survey_header_id")
        rows = [r for r in t[st_tag] if (r.get(key) or r.get("survey_header_id")) == hid]
        rows.sort(key=lambda r: _f(r, "md") or 0.0)
        stations, seen = [], set()
        for r in rows:
            md = _f(r, "md")
            if md is None or md in seen:
                continue
            seen.add(md)
            stations.append(SurveyStation(md=md * k, inclination=_f(r, "inclination") or 0.0,
                                          azimuth=(_f(r, "azimuth") or 0.0) % 360.0))
        if len(stations) >= 2:
            if hdr_tag.startswith("CD_SURVEY"):
                warnings.append("trajectory: no definitive survey; used survey header "
                                f"'{best.get('survey_name', hid)}'")
            return Trajectory(stations=stations)
    raise ValueError(f"no survey stations found for wellbore {wellbore_id}")


def _pressure_profile(t: _Tables, group_tag: str, row_tag: str, gid_key: str, value_key: str,
                      emw_key: str, wellbore_id: str, k: float, warnings: list[str],
                      label: str) -> Profile | None:
    groups = [g for g in t[group_tag] if g.get("wellbore_id") == wellbore_id]
    if not groups:
        return None
    # Prefer PLAN phase, then the group with the most points.
    rows_by = {}
    for g in groups:
        rows_by[g[gid_key]] = [r for r in t[row_tag] if r.get(gid_key) == g[gid_key]]
    groups.sort(key=lambda g: (g.get("phase") == "PLAN", len(rows_by[g[gid_key]])), reverse=True)
    g = groups[0]
    pts = []
    for r in sorted(rows_by[g[gid_key]], key=lambda r: _f(r, "tvd") or 0.0):
        tvd = _f(r, "tvd")
        if tvd is None:
            continue
        tvd_ft = tvd * k
        p = _f(r, value_key)
        emw = _f(r, emw_key)
        if p is not None and tvd_ft > 0:
            ppg = gradient_to_ppg(p / tvd_ft)
        elif emw is not None:
            ppg = emw
        else:
            continue
        if pts and abs(pts[-1].tvd - tvd_ft) < 1e-6:
            continue
        pts.append(DepthValue(tvd=tvd_ft, value=ppg))
    if not pts:
        return None
    if pts[0].tvd > 0:
        pts.insert(0, DepthValue(tvd=0.0, value=pts[0].value))
    warnings.append(f"{label}: used group '{g.get('name', g[gid_key])}' "
                    f"({g.get('phase') or 'no phase'}, {len(pts)} points)")
    return Profile(points=pts)


def _temperature(t: _Tables, wellbore_id: str, k: float,
                 warnings: list[str]) -> tuple[float, float] | None:
    groups = [g for g in t["CD_TEMP_GRADIENT_GROUP"] if g.get("wellbore_id") == wellbore_id]
    if not groups:
        return None
    g = max(groups, key=lambda g: g.get("phase") == "PLAN")
    gid = g["temp_gradient_group_id"]
    rows = [r for r in t["CD_TEMP_GRADIENT"] if r.get("temp_gradient_group_id") == gid]
    tvd = np.array([(_f(r, "tvd") or 0.0) * k for r in rows])
    temp = np.array([_f(r, "temperature") for r in rows], dtype=float)
    ok = ~np.isnan(temp)
    if ok.sum() >= 2:
        slope, intercept = np.polyfit(tvd[ok], temp[ok], 1)
        warnings.append(f"temperature: linear fit to {int(ok.sum())} points, "
                        f"{intercept:.0f} F + {slope * 100:.2f} F/100 ft")
        return float(intercept), float(slope * 100.0)
    grad = _f(g, "grad_tvd")
    surf = _f(g, "surface_ambient_temp")
    if grad is not None and surf is not None:
        return surf, grad * 100.0 / k
    return None


_GRADE_RE = re.compile(r"^([A-Z]+)-?(\d+)")


def _normalise_grade(name: str) -> str | None:
    m = _GRADE_RE.match(name.strip().upper())
    return f"{m.group(1)}-{m.group(2)}" if m else None


def _connection(name: str) -> str:
    n = name.upper()
    for key in ("BTC", "BUTT", "LTC", "STC"):
        if key in n:
            return {"BUTT": "BTC"}.get(key, key)
    return "PREMIUM"


def _classify(assemblies: list[dict]) -> list[str]:
    """String types from Landmark string_type and OD order."""
    types = []
    casings = [a for a in assemblies if a.get("string_type", "").lower() != "liner"]
    casings_sorted = sorted(casings, key=lambda a: -(_f(a, "assembly_size") or 0.0))
    for a in assemblies:
        st = a.get("string_type", "").lower()
        if st == "liner":
            types.append("liner")
        elif st == "conductor":
            types.append("conductor")
        else:
            i = casings_sorted.index(a)
            if i == 0 and len(casings_sorted) > 1:
                types.append("surface")
            elif i == len(casings_sorted) - 1:
                types.append("production")
            else:
                types.append("intermediate")
    return types


def import_edm(path: str | Path, wellbore: str | None = None, source_units: str = "feet",
               catalog: Catalog | None = None) -> EDMImportResult:
    """Build a Well from an EDM export. `wellbore` is a name or id (default: the one
    with the deepest survey). `source_units` is 'feet' or 'meters' for stored depths."""
    k = 1.0 if source_units == "feet" else FEET_PER_METER
    t = _Tables(path)
    cat = catalog or Catalog.default()
    warnings: list[str] = []

    wbs = t["CD_WELLBORE"]
    if not wbs:
        raise ValueError("no CD_WELLBORE rows in file")
    if wellbore is None:
        depth = {}
        for h in t["CD_SURVEY_HEADER"] + t["CD_DEFINITIVE_SURVEY_HEADER"]:
            depth[h.get("wellbore_id")] = max(depth.get(h.get("wellbore_id"), 0.0),
                                              _f(h, "md_max") or 0.0)
        wb = max(wbs, key=lambda w: depth.get(w["wellbore_id"], 0.0))
    else:
        match = [w for w in wbs if wellbore in (w.get("wellbore_id"), w.get("wellbore_name"))]
        if not match:
            raise KeyError(f"wellbore {wellbore!r} not found; have "
                           f"{[w.get('wellbore_name') for w in wbs]}")
        wb = match[0]
    wbid = wb["wellbore_id"]
    wells = {w.get("well_id"): w.get("well_common_name", "") for w in t["CD_WELL"]}
    well_name, wb_name = wells.get(wb.get("well_id"), ""), wb.get("wellbore_name", "")
    name = wb_name if wb_name.startswith(well_name) else f"{well_name} {wb_name}".strip()
    name = name or wbid

    traj = _trajectory(t, wbid, k, warnings)
    pore = _pressure_profile(t, "CD_PORE_PRESSURE_GROUP", "CD_PORE_PRESSURE",
                             "pore_pressure_group_id", "pore_pressure", "pore_pressure_emw",
                             wbid, k, warnings, "pore pressure")
    frac = _pressure_profile(t, "CD_FRAC_GRADIENT_GROUP", "CD_FRAC_GRADIENT",
                             "frac_gradient_group_id", "frac_gradient_pressure",
                             "frac_gradient_emw", wbid, k, warnings, "fracture gradient")
    if pore is None:
        pore = Profile.constant(8.6)
        warnings.append("pore pressure: none in file; assumed 8.6 ppg (normal)")
    if frac is None:
        frac = Profile.constant(14.0)
        warnings.append("fracture gradient: none in file; assumed 14.0 ppg - REVIEW")
    temp = _temperature(t, wbid, k, warnings)
    formation = Formation(pore_pressure=pore, fracture_gradient=frac,
                          surface_temperature_f=temp[0] if temp else 70.0,
                          geothermal_gradient_f_per_100ft=temp[1] if temp else 1.2)
    if temp is None:
        warnings.append("temperature: none in file; assumed 70 F + 1.2 F/100 ft")

    # Strings -----------------------------------------------------------------
    asm = [a for a in t["CD_ASSEMBLY"] if a.get("wellbore_id") == wbid
           and a.get("string_type", "").lower() in ("casing", "liner", "conductor")
           and _f(a, "md_assembly_base")]
    asm.sort(key=lambda a: _f(a, "md_assembly_base") or 0.0)
    if not asm:
        warnings.append("strings: no casing/liner assemblies found")
    types = _classify(asm)
    comps_by = {}
    for c in t["CD_ASSEMBLY_COMP"]:
        comps_by.setdefault(c.get("assembly_id"), []).append(c)

    strings: list[CasingString] = []
    specs: dict[str, PipeSpec] = {}
    stored: list[StoredRating] = []
    for a, stype in zip(asm, types):
        aname = a.get("assembly_name") or f"{a.get('string_type')} {a.get('assembly_size')}"
        shoe = (_f(a, "md_assembly_base") or 0.0) * k
        top = (_f(a, "md_assembly_top") or 0.0) * k if stype == "liner" else 0.0
        od = _f(a, "assembly_size") or 0.0
        comps = [c for c in comps_by.get(a["assembly_id"], [])
                 if c.get("sect_type_code", "").upper() in ("CAS", "CASING", "LIN", "TUB", "")]
        comps.sort(key=lambda c: int(_f(c, "sequence_no") or 0))
        # Pick the heaviest casing component as the representative pipe (conservative
        # for the design check; tapered strings can be rebuilt by hand afterwards).
        best = None
        for c in comps:
            od_c, id_c = _f(c, "od_body"), _f(c, "id_body")
            if od_c is None or id_c is None:
                continue
            if best is None or (od_c - id_c) > (_f(best, "od_body") - _f(best, "id_body")):
                best = c
        if od == 0.0 and best is not None:
            od = _f(best, "od_body")
        hole = _f(a, "hole_size") or od + 1.5
        shoe_tvd = float(traj.tvd(min(shoe, traj.td)))
        mw = float(pore.at(shoe_tvd)) + 0.5
        s = CasingString(name=aname, type=stype, od=od, hole_size=hole, hanger_md=top,
                         shoe_md=shoe, toc_md=top, mud_weight=round(mw, 1))
        strings.append(s)
        if best is not None:
            grade = _normalise_grade(best.get("grade", "")) or ""
            wall = (_f(best, "od_body") - _f(best, "id_body")) / 2.0
            cands = [p for p in cat.pipes_for_od(od)]
            pipe = min(cands, key=lambda p: abs(p.wall - wall)) if cands else None
            if pipe is None or abs(pipe.wall - wall) > 0.01:
                warnings.append(f"{aname}: no catalog pipe for OD {od} wall {wall:.3f}; "
                                "spec not resolved")
            elif grade not in cat.grades:
                warnings.append(f"{aname}: grade {best.get('grade')!r} not in catalog; "
                                "spec not resolved")
            else:
                conn = _connection(best.get("connection_name", ""))
                try:
                    specs[aname] = cat.spec(od, pipe.nominal_weight, grade, conn)
                except (KeyError, ValueError):
                    specs[aname] = cat.spec(od, pipe.nominal_weight, grade, "BTC")
                    warnings.append(f"{aname}: connection {best.get('connection_name')!r} "
                                    "mapped to BTC")
            stored.append(StoredRating(aname, best.get("catalog_key_desc", ""),
                                       _f(best, "pipe_pressure_burst"),
                                       _f(best, "pressure_collapse"), _f(best, "axial_rating")))
        else:
            warnings.append(f"{aname}: no casing components; pipe not resolved")
        warnings.append(f"{aname}: mud weight assumed {s.mud_weight} ppg (pore + 0.5), TOC at "
                        f"string top, cement 12.5/15.8 ppg - REVIEW")

    # Link drilling-ahead parameters from the next string down.
    for i, s in enumerate(strings[:-1]):
        nxt = strings[i + 1]
        if s.type in ("surface", "intermediate", "liner") and nxt.shoe_md > s.shoe_md:
            s.next_hole_mud_weight = nxt.mud_weight
            s.next_section_td_md = nxt.shoe_md

    if traj.td < max((s.shoe_md for s in strings), default=0.0):
        warnings.append("trajectory ends above the deepest shoe; TVD is extrapolated vertically")

    well = Well(name=name, trajectory=traj, formation=formation, strings=strings)
    return EDMImportResult(well=well, specs=specs, stored_ratings=stored, warnings=warnings)
