"""Task 5: tidy pressure dataset at a common datum and the depletion picture.
Usage: python src/pressure_db.py
Outputs: data/processed/pressure/tecolutla_pressures.csv (one row per survey, with datum-corrected pressure at 2,300 mSS),
         data/processed/pressure/pressure_summary.json, figures/05_pressure_depletion.png
Datum: 2,300 m subsea (mSS). The IFR summary workbook uses 2,300 m below KB; the difference is the KB elevation (3.8-7.1 m).
Gradient used between gauge depth and datum: 10.5 kPa/m (the reservoir gradient IHS derived from the 2018 build-ups); sensitivity
with an oil gradient of 8.7 kPa/m is reported per row. Nothing is interpolated between surveys.
"""
import json, numpy as np, pandas as pd, openpyxl
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

SUM = "data/raw/geology/Tecolutla Pressure Summary.xlsx"
OUT = "data/processed/pressure/"
KPA_PER_KGCM2 = 98.0665
GRAD = 10.5; GRAD_OIL = 8.7   # kPa/m
KB = {"TEC-2": 3.8, "TEC-6": 6.0, "TEC-7": 4.8, "TEC-10": 7.1}   # m; TEC-2/7 from the PEMEX survey forms, TEC-6 from Tecolutla Well Header Information.csv (ELEV_KB), TEC-10 from the IHS report

wb = openpyxl.load_workbook(SUM, read_only=True, data_only=True); rows = list(wb["all"].iter_rows(values_only=True, max_col=14)); wb.close()
hi = next(i for i, r in enumerate(rows) if r[0] == "Date"); hdr = rows[hi]; s = pd.DataFrame(rows[hi + 1:], columns=[str(h) for h in hdr]).dropna(subset=["Date"])
s["well"] = s.Well.str.replace("Tecolutla-", "TEC-")
recs = []
for r in s.itertuples():
    run = float(r._8); p_run_mpa = float(r._10)
    shut = r._4
    kind = "static gradient" if r.Type == "SG" else "flowing survey"
    flag = []
    if isinstance(shut, (int, float)) and shut < 1: flag.append(f"shut-in only {shut*24:.1f} h")
    if r.Type == "Flow": flag.append("flowing, not static")
    if isinstance(r.Comments, str) and "Pflowing" in r.Comments: flag.append("flowing pressure before shut-in"); kind = "flowing survey"
    if r.well == "TEC-2" and r.Date.year == 2018: flag.append("gauge stopped at 2,250 mKB above the perforations; extrapolated by IFR at a water gradient")
    tvd_kb = run  # vertical wells; TEC-2 2018 survey is vertical
    recs.append(dict(date=pd.Timestamp(r.Date), well=r.well, kind=kind, shut_in_days=shut if isinstance(shut, (int, float)) else np.nan,
                     gauge_depth_mkb=run, gauge_depth_mss=tvd_kb - KB[r.well], p_gauge_kpa=p_run_mpa * 1000, p_gauge_source="IFR summary transcription of PEMEX scan",
                     ifr_datum_2300mkb_kpa=float(r._13) * 1000 if isinstance(r._13, (int, float)) else np.nan, comment=r.Comments,
                     source="geology/Tecolutla Pressure Summary.xlsx!all; scans in pressures/ folder", quality_flag="; ".join(flag)))
# corrections to the transcription verified against the scans
for x in recs:
    if x["well"] == "TEC-2" and x["date"] == pd.Timestamp("1956-05-24"):
        x["p_gauge_kpa"] = 252.0 * KPA_PER_KGCM2; x["gauge_depth_mkb"] = 2310; x["gauge_depth_mss"] = 2310 - 3.8
        x["p_gauge_source"] = "scan read: 252.0 kg/cm2 at 2310 m, 2 h 45 min shut-in, oil level 2210 m, water gradient 0.070 kg/cm2/m below 2260 m"
    if x["well"] == "TEC-7" and x["date"] == pd.Timestamp("1998-10-06"):
        x["p_gauge_kpa"] = 252.232 * KPA_PER_KGCM2; x["gauge_depth_mkb"] = 2325; x["gauge_depth_mss"] = 2325 - 4.8
        x["p_gauge_source"] = "scan read: 252.232 kg/cm2 at 2325 m (below perfs), 250.634 at 2311.5 m; gradient 0.1028-0.1049 kg/cm2/m (water)"
# 2018 build-ups (IHS PTA reports)
recs += [
    dict(date=pd.Timestamp("2018-05-30"), well="TEC-2", kind="build-up, extrapolated p*", shut_in_days=311 / 24, gauge_depth_mkb=2309.0, gauge_depth_mss=2305.2,
         p_gauge_kpa=24190, p_gauge_source="IHS PTA final report p.5/14: pR 24190 kPa(a) at 2309 mKB (final measured 24187 after 311 h)", ifr_datum_2300mkb_kpa=np.nan,
         comment="k 50 mD, h 8 m, skin +196, constant-pressure boundary at 700 m; last flow 50 bbl/d oil, 453 bbl/d water", source="development_plan/Tecolutla 2 Final Report (IHS PTA) Spanish.pdf", quality_flag="model-extrapolated; 13-day build-up still rising 3 kPa"),
    dict(date=pd.Timestamp("2018-08-31"), well="TEC-10", kind="build-up, extrapolated p*", shut_in_days=598 / 24, gauge_depth_mkb=2322.1, gauge_depth_mss=2315.0,
         p_gauge_kpa=24304, p_gauge_source="IHS PTA final report p.5/15: pR 24304 kPa(a) at 2322.1 mTVD KB (final measured 24283 after 598 h)", ifr_datum_2300mkb_kpa=np.nan,
         comment="k 18 mD, h 13.2 m, skin +4.9, constant-pressure boundary at 195 m, no-flow at 125 m; last flow 196 bbl/d oil, 114 bbl/d water", source="development_plan/Tecolutla 10 Final Report (IHS PTA) Spanish.pdf", quality_flag="model-extrapolated; 25-day build-up"),
]
p = pd.DataFrame(recs).sort_values("date").reset_index(drop=True)
p["p_2300mss_kpa"] = p.p_gauge_kpa + GRAD * (2300 - p.gauge_depth_mss)
p["p_2300mss_oilgrad_kpa"] = p.p_gauge_kpa + GRAD_OIL * (2300 - p.gauge_depth_mss)
p["p_2300mss_mpa"] = p.p_2300mss_kpa / 1000; p["p_2300mss_psia"] = p.p_2300mss_kpa * 0.1450377
p["usable_static"] = ~p.kind.str.contains("flowing") & ~p.quality_flag.str.contains("shut-in only")
# cumulative oil at each survey date from the task-4 field series
f = pd.read_csv("data/processed/tecolutla_field_monthly.csv", parse_dates=["date"])
alloc = pd.read_csv("data/processed/tecolutla_production_allocations.csv")
pre = 429_000  # wellfile block totals before the 1960 field series (TEC-6 388 kbbl + TEC-2 38 kbbl, task 4)
def cum_at(d):
    rec = f[f.date < d].oil_bbl.sum()
    return rec, rec + (pre if d >= pd.Timestamp("1960-01-01") else 0)
p["np_recorded_bbl"] = [cum_at(d)[0] for d in p.date]; p["np_with_allocations_bbl"] = [cum_at(d)[1] for d in p.date]
p.to_csv(OUT + "tecolutla_pressures.csv", index=False)

u = p[p.usable_static]
init = p[(p.well == "TEC-2") & (p.date.dt.year == 1956)].iloc[0]
first_static = u.iloc[0]; last = u[u.date.dt.year == 2018]
summary = dict(
    datum="2300 mSS", gradient_kpa_per_m=GRAD, kb_m=KB,
    p_1956_tec2_2300mss_mpa=round(float(init.p_2300mss_mpa), 2), p_1956_note="2 h 45 min shut-in on a new well; taken as initial by PEMEX (252 kg/cm2)",
    p_1964_mpa={w: round(float(v), 2) for w, v in u[u.date.dt.year == 1964].set_index("well").p_2300mss_mpa.items()},
    p_1971_tec6_final_74d_mpa=round(float(u[(u.well == "TEC-6") & (u.date == "1971-10-18")].p_2300mss_mpa.iloc[0]), 2),
    p_1998_tec7_mpa=round(float(u[u.date.dt.year == 1998].p_2300mss_mpa.iloc[0]), 2),
    p_2018_mpa={f"{r.well} {r.date.date()}": round(float(r.p_2300mss_mpa), 2) for r in last.itertuples()},
    depletion_1956_to_2018_mpa=round(float(init.p_2300mss_mpa - last.p_2300mss_mpa.mean()), 2),
    depletion_pct=round(float(100 * (init.p_2300mss_mpa - last.p_2300mss_mpa.mean()) / init.p_2300mss_mpa), 1),
    np_at_2018_recorded_bbl=int(last.np_recorded_bbl.iloc[0]), np_at_2018_with_allocations_bbl=int(last.np_with_allocations_bbl.iloc[0]),
    expansion_only_check="N x ct x dp with N 11.2 MMbbl (IFR volumetrics), ct 1.98e-6/kPa (IHS TEC-2), dp 500 kPa = %.0f bbl vs ~1.9 MMbbl produced: >99%% of voidage replaced by water influx" % (11.2e6 * 1.98e-6 * 500),
    tec6_1971_buildup="23.20 -> 24.31 MPa (datum, IFR basis) between 4 and 74 days shut-in: short shut-ins understate reservoir pressure by up to 1 MPa",
)
json.dump(summary, open(OUT + "pressure_summary.json", "w"), indent=1, default=str)
print(p[["date", "well", "kind", "shut_in_days", "gauge_depth_mss", "p_gauge_kpa", "p_2300mss_mpa", "p_2300mss_oilgrad_kpa", "usable_static", "np_with_allocations_bbl", "quality_flag"]].to_string())
print(json.dumps(summary, indent=1))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 11))
mk = {"TEC-2": "o", "TEC-6": "s", "TEC-7": "^", "TEC-10": "D"}
for w, g in p.groupby("well"):
    gu = g[g.usable_static]; gf = g[~g.usable_static]
    ax1.scatter(gu.date, gu.p_2300mss_mpa, marker=mk[w], s=70, label=f"{w} static / build-up", zorder=3)
    ax1.scatter(gf.date, gf.p_2300mss_mpa, marker=mk[w], s=70, facecolors="none", edgecolors="grey", zorder=3, label=f"{w} flowing or <1 day shut-in")
    ax2.scatter(gu.np_with_allocations_bbl / 1e6, gu.p_2300mss_mpa, marker=mk[w], s=70, label=w, zorder=3)
    ax2.scatter(gf.np_with_allocations_bbl / 1e6, gf.p_2300mss_mpa, marker=mk[w], s=70, facecolors="none", edgecolors="grey", zorder=3)
b = p[(p.well == "TEC-6") & (p.date.dt.year == 1971)]
ax1.plot(b.date, b.p_2300mss_mpa, color="tab:orange", lw=0.8, ls=":", label="TEC-6 Aug-Oct 1971 build-up (4 to 74 days)")
for ax in (ax1, ax2):
    ax.axhline(init.p_2300mss_mpa, color="red", ls="--", lw=1, label=f"TEC-2 24 May 1956, 2 h 45 min shut-in: {init.p_2300mss_mpa:.2f} MPa (PEMEX 'initial' 252 kg/cm2)")
    ax.set_ylim(18, 26); ax.grid(alpha=0.3); ax.set_ylabel("pressure at 2,300 mSS (MPa)")
ax1.set_title("Tecolutla static pressures corrected to 2,300 mSS at 10.5 kPa/m (PEMEX surveys 1956-1998 from the IFR summary and scans; IHS build-ups 2018)")
ax1.legend(fontsize=7.5, ncol=3, loc="lower right")
ax2.set_xlabel("cumulative field oil at survey date (MMbbl, recorded + 0.43 MMbbl wellfile block totals; task 4)")
ax2.set_title("Pressure versus cumulative oil: 0.5 MPa (2 %) decline over ~1.9 MMbbl; expansion alone would support ~11 kbbl, so >99 % of voidage is water influx")
ax2.legend(fontsize=8, loc="lower right")
ax2b = ax2.twinx(); ax2b.set_ylim(18 * 145.0377, 26 * 145.0377); ax2b.set_ylabel("psia")
ax1b = ax1.twinx(); ax1b.set_ylim(18 * 145.0377, 26 * 145.0377); ax1b.set_ylabel("psia")
plt.tight_layout(); plt.savefig("figures/05_pressure_depletion.png", dpi=140); print("figure written")
