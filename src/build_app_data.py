"""Assemble the data file for the presentation app (Tecolutla Field Story artifact).
Usage: .venv/bin/python src/build_app_data.py <out_dir>    -> <out_dir>/app_data.json
Inputs (all in the repository):
  data/processed/presentation/{wells.json, events.json, production_by_well.csv, opex_monthly.csv, drilling_costs.json, opex_breakdown.json,
                               technical_tables.json, coast_golden_lane.json}  (compiled 26 Oct 2026 from the docs and processed tables; sources inside)
  data/processed/pressure/tecolutla_pressures.csv, data/processed/econ_rebuild/{summary.json, bridge.csv, cashflow_base.csv},
  data/processed/petrophysics/{TEC10_logs_mss.csv, TEC9_logs_mss.csv, TEC11_logs_mss.csv}, data/processed/seismic/tec11_vs_grid.csv,
  data/processed/volumetrics/{summary.json, ooip_by_source.csv, monte_carlo.csv, analogue_rf.csv}, data/processed/tecolutla_production.csv.
Nothing is interpolated: months without a record are absent, except documented non-producing months (explicit zeros, flagged z=1; see below). Pre-1966 PEMEX wellfile allocations (TEC-6 388 kbbl, TEC-2 38 kbbl) are carried
as a single lump per well at the end of the allocation period, flagged, never spread over months.
"""
import json, math, sys
import numpy as np, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "data/processed"; PR = P / "presentation"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
J = lambda p: json.loads(Path(p).read_text())
def clean(o):
    if isinstance(o, float): return None if (math.isnan(o) or math.isinf(o)) else round(o, 4)
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.floating,)): return clean(float(o))
    if isinstance(o, (np.integer,)): return int(o)
    return o
def dec(d):  # date -> decimal year at the start of the month
    d = pd.Timestamp(d); return round(d.year + (d.month - 1) / 12, 4)

A = {}
# ---------------- wells and events
wj = J(PR / "wells.json"); A["wells"] = wj["wells"] if isinstance(wj, dict) else wj; ev = J(PR / "events.json"); A["events"] = ev["events"] if isinstance(ev, dict) else ev
# ---------------- monthly production by well (one best source per well-month, see production_notes.md)
pb = pd.read_csv(PR / "production_by_well.csv"); pb = pb[pb.month.str.match(r"^\d{4}-\d{2}$", na=False)].copy(); pb["month"] = pd.to_datetime(pb.month + "-01")
# 1960-65 field-level rows are TEC-6 (the only producer: TEC-2 and TEC-7 were shut in for salt water 1957-71); the 2019-22 commingled
# CAMPO TECO stream is shown as TEC-10, its main or sole source per the CNH filings (TEC-2 contributed in 2020). Display attribution only.
pb["well"] = pb.well.replace({"FIELD (no well split)": "TEC-6", "FIELD commingled (CAMPO TECO)": "TEC-10"})
pb = pb[pb.well.isin(["TEC-2", "TEC-6", "TEC-7", "TEC-9", "TEC-10", "TEC-11"])]
A["prod"] = [dict(w=r.well, t=dec(r.month), o=round(float(r.oil_bbl or 0), 1), wt=round(float(r.water_bbl), 1) if pd.notna(r.water_bbl) else None,
                  g=round(float(r.gas_mcf), 1) if pd.notna(r.gas_mcf) else None) for r in pb.itertuples() if pd.notna(r.oil_bbl) or pd.notna(r.water_bbl)]
# Commingled 2019-22 months (shown as TEC-10): the ticket stream has no water, and the shut-in months of 2022 have no ticket row. Take the
# CNH-filed / LOS values from opex_monthly.csv for those months (sourced there, row by row); flag f=1.
ox = pd.read_csv(PR / "opex_monthly.csv"); have = {(r["w"], r["t"]): r for r in A["prod"]}
for r in ox[(ox.month >= "2019-12") & (ox.month <= "2022-12")].itertuples():
    k = ("TEC-10", dec(r.month + "-01"))
    if k in have:
        if have[k]["wt"] is None and pd.notna(r.water_bbl): have[k]["wt"] = round(float(r.water_bbl), 1); have[k]["f"] = 1
        if have[k]["o"] == 0 and pd.notna(r.oil_bbl) and r.oil_bbl > 0: have[k]["o"] = round(float(r.oil_bbl), 1); have[k]["f"] = 1   # Dec-2022: ticket books 0, LOS 733 bbl sold
    elif pd.notna(r.oil_bbl):
        A["prod"].append(dict(w="TEC-10", t=k[1], o=round(float(r.oil_bbl), 1), wt=round(float(r.water_bbl), 1) if pd.notna(r.water_bbl) else None, g=None, f=1))
# Reported-zero and shut-in months: a month with no record inside a non-producing segment of the well's status timeline (wells.json, each
# segment sourced; PEMEX-era internal gaps are CNH-reported zero months, G-34) is an explicit zero, flagged z=1. A month with no record inside
# a producing segment (1956-59, TEC-2 1956-57, TEC-7 early 1957, the 2019-22 TEC-2 months inside the commingled stream, Jan 2023) stays
# absent: no monthly record exists. Plugged wells stop at the plugging month. See production_notes.md "Zero months".
NOW_M = "2026-10"; have = {(r["w"], r["t"]) for r in A["prod"]}
months = pd.period_range("1956-01", NOW_M, freq="M")
for w in A["wells"]:
    if w["well"] not in ("TEC-2", "TEC-6", "TEC-7", "TEC-9", "TEC-10"): continue
    segs = []
    for s in w.get("status_timeline") or []:
        f = pd.Timestamp(str(s["from"]) + ("-01" if len(str(s["from"])) == 7 else ""))
        u = pd.Timestamp(str(s["to"]) + ("-28" if len(str(s["to"])) == 7 else "")) if s.get("to") else pd.Timestamp(NOW_M + "-28")
        segs.append((f, u, s["status"]))
    for m in months:
        mid = m.to_timestamp() + pd.Timedelta(days=14); st = next((x[2] for x in segs if x[0] <= mid <= x[1]), None)
        if st == "plugged": break
        if st in ("shut_in", "workover", "injector") and (w["well"], dec(m.to_timestamp())) not in have:
            A["prod"].append(dict(w=w["well"], t=dec(m.to_timestamp()), o=0.0, wt=0.0, g=None, z=1))
A["prod"].sort(key=lambda r: (r["w"], r["t"]))
# annual table
an = pd.read_csv(PR / "field_annual.csv")
A["annual"] = an.to_dict("records"); A["annualCols"] = list(an.columns)
# ---------------- pressure
p = pd.read_csv(P / "pressure/tecolutla_pressures.csv")
A["pressure"] = [dict(date=r.date, well=r.well, type=r.kind, depth_mss=r.gauge_depth_mss, p_mpa=round(r.p_2300mss_mpa, 3), p_psi=round(r.p_2300mss_psia),
                      p_kgcm2=round(r.p_2300mss_mpa * 10.197, 1), usable=bool(r.usable_static), np_bbl=r.np_with_allocations_bbl,
                      note=r.quality_flag if isinstance(r.quality_flag, str) else "", source=r.source) for r in p.itertuples()]
A["pressure_summary"] = J(P / "pressure/pressure_summary.json")
# ---------------- economics
es = J(P / "econ_rebuild/summary.json"); A["econ"] = dict(cases=es["glj_oct26_base_capex"], pf=es.get("glj_oct26_price_factor_sensitivity"),
    breakeven=es.get("flat_wti_breakeven"), params=es["parameters"], wti=es["glj_oct26_wti"], capex=es["capex_usd_2026"],
    bridge=pd.read_csv(P / "econ_rebuild/bridge.csv").to_dict("records"))
cf = pd.read_csv(P / "econ_rebuild/cashflow_base.csv")
A["econ"]["cf"] = cf[["month", "year", "oil_bpd", "cf_btax"]].iloc[::3].round(1).to_dict("records")
# ---------------- logs
def logs(f, cols, lo, hi, step):
    d = pd.read_csv(P / "petrophysics" / f); d = d[(d.mss >= lo) & (d.mss <= hi)].copy()
    d["b"] = (d.mss / step).round() * step; g = d.groupby("b")[[c for c in cols if c in d]].median().reset_index().rename(columns={"b": "mss"})
    for c in g.columns:
        if c.startswith("res"): g.loc[g[c] > 5000, c] = np.nan
    return g.round(4).to_dict("records")
A["logs"] = dict(tec10=logs("TEC10_logs_mss.csv", ["gr", "res_ild", "nprl", "dprl", "den", "pe"], 2262, 2420, 0.5),
                 tec9=logs("TEC9_logs_mss.csv", ["gr", "res_ild", "sphi"], 2262, 2340, 0.5))
t11 = pd.read_csv(P / "petrophysics/TEC11_logs_mss.csv").dropna(subset=["dtc"])
t11["b"] = (t11.DEPT / 5).round() * 5
A["tec11_logs"] = t11.groupby("b")[["mss", "gr", "dtc"]].median().reset_index().rename(columns={"b": "md"}).round(2).to_dict("records")
g11 = pd.read_csv(P / "seismic/tec11_vs_grid.csv"); g11 = g11[g11.mMD >= 2200]
A["tec11_grid"] = g11[["mMD", "mSS", "x", "y", "grid_mss", "dominant"]].round(1).to_dict("records")
# ---------------- volumetrics
vs = J(P / "volumetrics/summary.json")
A["ooip"] = dict(sources=pd.read_csv(P / "volumetrics/ooip_by_source.csv").drop(columns=["file"]).to_dict("records"), mc=vs["monte_carlo"], swing=vs["swing"],
                 rf=vs["trend_rf"], produced=vs["produced_mmbbl"], remaining=vs["remaining_mmbbl"])
mc = pd.read_csv(P / "volumetrics/monte_carlo.csv").ooip_mmbbl
hist, edges = np.histogram(mc, bins=np.arange(5.0, 16.01, 0.25))
A["ooip"]["hist"] = [dict(x0=float(a), x1=float(b), n=int(n)) for a, b, n in zip(edges[:-1], edges[1:], hist)]
# El Abra analogue recovery (CNH trend table, 45 fields to Apr 2015; docs/07 §3)
an_rf = pd.read_csv(P / "volumetrics/analogue_rf.csv")
A["ooip"]["analogues"] = an_rf[["field", "play", "area_km2", "ooip_mmbbl", "prod_mmbbl", "rf_current", "rf_3p_eur", "api", "max_wells"]].round(4).to_dict("records")
# ---------------- compiled tables (opex, costs, fluids, core, marl) and the coastline
for k, f in [("opex", "opex_monthly.csv")]:
    if (PR / f).exists(): A[k] = pd.read_csv(PR / f).to_dict("records")
for k, f in [("costs", "drilling_costs.json"), ("opex_breakdown", "opex_breakdown.json"), ("tech", "technical_tables.json"), ("coast", "coast_golden_lane.json")]:
    if (PR / f).exists(): A[k] = J(PR / f)
A["sources"] = J(PR / "sources.json") if (PR / "sources.json").exists() else []
(OUT / "app_data.json").write_text(json.dumps(clean(A), separators=(",", ":"), ensure_ascii=False))
print("app_data.json", (OUT / "app_data.json").stat().st_size, "bytes;", {k: (len(v) if hasattr(v, "__len__") else 1) for k, v in A.items()})
