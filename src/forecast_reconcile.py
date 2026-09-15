"""Task 6: type curve and TEC-12 forecast reconciliation -> one base case with a range.
Usage: python src/forecast_reconcile.py
Inputs: task-4 production database, Tecolutla Type Curve.xlsx (Mar 2021 copy), GLJ YE2020 forecast workbook,
        Simmons scenarios, Petrel Robertson assessment (numbers quoted in docs/06_forecast.md), 2023 economics profile.
Outputs: data/processed/forecast/{type_curve_month_on_prod.csv, cases.csv, tec12_profiles_monthly.csv, summary.json}, figures/06_type_curve_forecast.png
Arps hyperbolic: q(t) = qi / (1 + b Di t)^(1/b), t in months, Di per month. Monthly volumes = 30.42 x rate.
"""
import json, numpy as np, pandas as pd, openpyxl
from scipy.optimize import curve_fit
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "data/processed/forecast/"; DPM = 30.42
def arps(t, qi, di, b): return qi / (1 + b * di * t) ** (1 / b)
def profile(qi, di, b, months=360, qmin=10.0):
    t = np.arange(1, months + 1) - 0.5
    q = arps(t, qi, di, b); q[q < qmin] = 0
    return q
def stats(q):
    c = np.cumsum(q * DPM)
    return dict(ip_first_month_bpd=round(float(q[0]), 1), month12_bpd=round(float(q[11]), 1), month36_bpd=round(float(q[35]), 1),
                cum_1yr_bbl=int(c[11]), cum_5yr_bbl=int(c[59]), cum_10yr_bbl=int(c[119]), cum_20yr_bbl=int(c[239]),
                eur_bbl_at_10bpd=int(c[-1]), months_above_10bpd=int((q > 0).sum()))

# ---------------------------------------------------------------- 1. month-on-production series from the task-4 database
db = pd.read_parquet("data/processed/tecolutla_production.parquet")
pem = db[db.source_kind == "cnh_monthly_pemex_era"].copy()
mop = {}
for w, g in pem.groupby("well"):
    g = g.sort_values("date"); g = g[g.oil_bbl > 0]
    if w == "TEC-7": g = g[g.date >= "1971-10-01"]  # the single 1968-06 test month (1.3 bbl/d) is not month 1 in the IFR workbook either
    g["mop"] = range(1, len(g) + 1)  # months with production, in order (the IFR workbook indexes producing months the same way)
    mop[w] = g.set_index("mop").oil_bpd_cd
t10 = db[(db.well == "TEC-10") & (db.source_kind == "tonalli_daily_sum")].sort_values("date")
t10r = (t10.oil_bbl / t10.days_on).values          # producing-day average
mop["TEC-10"] = pd.Series(t10r, index=range(1, len(t10r) + 1))
tc = pd.DataFrame(mop); tc.index.name = "month_on_production"
tc["avg_4_pemex_wells"] = tc[["TEC-2", "TEC-6", "TEC-7", "TEC-9"]].mean(axis=1)
# cross-check against the IFR workbook's Average column
wb = openpyxl.load_workbook("data/raw/tec12_drill/Tecolutla Type Curve.xlsx", read_only=True, data_only=True)
rows = list(wb["Updated 20200917"].iter_rows(values_only=True, min_row=3, max_col=9)); wb.close()
ifr = pd.DataFrame([r for r in rows if isinstance(r[0], (int, float))], columns=["mop", "TEC-2", "TEC-6", "TEC-7", "TEC-9", "Tec-10", "Average", "Fit", "Tec-12"]).set_index("mop")
tc["ifr_workbook_average"] = ifr["Average"]; tc["ifr_workbook_fit"] = ifr["Fit"]; tc["ifr_tec12_curve"] = ifr["Tec-12"]
chk = (tc["avg_4_pemex_wells"] - tc["ifr_workbook_average"]).abs()
tc.to_csv(OUT + "type_curve_month_on_prod.csv")
# late TEC-10 constraint from commingled field sales (task 4): field 2021 ~50 bbl/d, 2022 (Jan-Feb, Nov) ~30 bbl/d; TEC-2 share ~10 % (By Zone 7.8 kbbl vs TEC-10 47.8 kbbl to Mar 2020)
field = pd.read_csv("data/processed/tecolutla_field_monthly.csv", parse_dates=["date"])
late = []
for yr in [2020, 2021, 2022]:
    f = field[(field.date.dt.year == yr) & field.oil_bbl.notna() & (field.oil_bbl > 0)]
    bpd = f.oil_bbl.sum() / (f.date.dt.days_in_month.sum())
    m = (pd.Timestamp(f"{yr}-07-01") - pd.Timestamp("2018-09-20")).days / DPM
    late.append(dict(year=yr, field_bpd=round(bpd, 1), tec10_est_bpd=round(bpd * 0.9, 1), month_on_prod=round(m, 1)))
late = pd.DataFrame(late)

# ---------------------------------------------------------------- 2. fits
def fit(series, tmax=None, p0=(200, 0.1, 1.0), bounds=([1, 1e-4, 0.01], [2000, 5, 3])):
    s = series.dropna(); s = s[s > 0]
    if tmax: s = s[s.index <= tmax]
    t = s.index.values.astype(float) - 0.5; y = s.values
    p, _ = curve_fit(lambda t, qi, di, b: np.log(arps(t, qi, di, b)), t, np.log(y), p0=p0, bounds=bounds, maxfev=20000)
    return dict(qi=float(p[0]), di_per_month=float(p[1]), b=float(p[2]), n=len(s))
f_avg = fit(tc["avg_4_pemex_wells"], tmax=240)
f_t10 = fit(tc["TEC-10"])
# TEC-10 with the late field-sales points added (weighted equally)
s = tc["TEC-10"].dropna().copy()
for r in late.itertuples(): s.loc[r.month_on_prod] = r.tec10_est_bpd
f_t10_late = fit(s.sort_index())
# IFR 2020 curve parameters (Model!I28:L28): qi 342, Di 3.507/yr nominal, b 1.7 -> first-month average 300.15
ifr_p = dict(qi=342.0, di=3.507302612853693 / 12, b=1.7)
# GLJ YE2020 TEC-12 Dir profiles (Gross Oil Monthly Forecast by Well (Kevin).xlsx, sheet daily: cols D=1P, F=2P, I=3P)
wb = openpyxl.load_workbook("data/raw/ye2020_reserves/Gross Oil Monthly Forecast by Well (Kevin).xlsx", read_only=True, data_only=True)
rows = [r for r in wb["daily"].iter_rows(values_only=True, min_row=5, max_col=10) if r[0] is not None]; wb.close()
glj = pd.DataFrame(rows, columns=["date", "days", "t10_1p", "t12_1p", "t10_2p", "t12_2p", "t13_2p", "t10_3p", "t12_3p", "t13_3p"])
glj["date"] = pd.to_datetime(glj.date)
def glj_profile(col):
    g = glj[glj[col] > 0]; q = g[col].values.astype(float); return q, g.days.values.astype(float)
cases = []
def add_case(name, source, q, days=None, note=""):
    if days is None: days = np.full(len(q), DPM)
    c = np.cumsum(q * days); qq = np.array(q, dtype=float)
    def at(m): return int(c[min(m, len(c)) - 1]) if len(c) else 0
    cases.append(dict(case=name, source=source, ip_first_month_bpd=round(float(qq[0]), 1), month12_bpd=round(float(qq[11]) if len(qq) > 11 else 0, 1),
                      month36_bpd=round(float(qq[35]) if len(qq) > 35 else 0, 1), cum_1yr_bbl=at(12), cum_5yr_bbl=at(60), cum_10yr_bbl=at(120),
                      cum_20yr_bbl=at(240), eur_bbl=int(c[-1]), months=len(qq), note=note))
add_case("IFR 2020 type curve (qi 342, b 1.7, Di 3.5/yr)", "Tecolutla Type Curve.xlsx / Model!I28:L28", profile(**ifr_p, months=417, qmin=0), note="no economic limit; 401 kbbl over 417 months in the workbook")
add_case("IFR 2020 curve to a 10 bbl/d limit", "same", profile(**ifr_p, qmin=10))
add_case("IFR 2023 economics, TEC-12 incremental to economic limit", "2023 Tec-12 Economics.xlsm", profile(**ifr_p, months=131, qmin=0), note="235 kbbl incremental in the 2024 model (task 1); 131 months to Nov 2034")
for lab, col in [("GLJ YE2020 1P", "t12_1p"), ("GLJ YE2020 2P", "t12_2p"), ("GLJ YE2020 3P", "t12_3p")]:
    q, d = glj_profile(col); add_case(lab + " TEC-12 Dir", "Gross Oil Monthly Forecast by Well (Kevin).xlsx daily", q, d, note="GLJ economic life applied; on stream May 2021")
q, d = glj_profile("t10_2p"); add_case("GLJ YE2020 2P TEC-10 remaining (for comparison)", "same", q, d, note="from Jan 2021")
add_case("Petrel Robertson base (100 bbl/d, >100 kbbl)", "Petrel Robertson Tec-12 Assessment.pdf p.2", profile(100 / (arps(0.5, 1, ifr_p["di"], 1.7)), ifr_p["di"], 1.7, qmin=10), note="shape assumed = IFR curve scaled to 100 bbl/d first month; PR gives rate and EUR only")
add_case("Petrel Robertson upside (200 bbl/d, ~200 kbbl)", "same", profile(200 / (arps(0.5, 1, ifr_p["di"], 1.7)), ifr_p["di"], 1.7, qmin=10), note="shape assumed as above")
for lab, rate, sales in [("Simmons low", 120, 390420), ("Simmons most likely", 170, 504274), ("Simmons upper likely", 235, 651664), ("Simmons high", 300, 799323)]:
    cases.append(dict(case=f"{lab} ({rate} bbl/d)", source="Simmons Scenarios - Tec 12 and Tec 13.xlsx", ip_first_month_bpd=rate, month12_bpd=np.nan, month36_bpd=np.nan,
                      cum_1yr_bbl=np.nan, cum_5yr_bbl=np.nan, cum_10yr_bbl=np.nan, cum_20yr_bbl=np.nan, eur_bbl=sales, months=96,
                      note="8-year sales for TEC-12 AND TEC-13 together (Tec-13 on stream Jan 2022); not a single-well EUR"))
add_case("TEC-10 actual, Arps fit to 15 months", "task 4 daily sheet", profile(f_t10["qi"], f_t10["di_per_month"], f_t10["b"], qmin=10), note=f"fit qi {f_t10['qi']:.0f}, Di {f_t10['di_per_month']*12:.2f}/yr, b {f_t10['b']:.2f}")
add_case("TEC-10 actual + 2020-22 field-sales constraint", "task 4", profile(f_t10_late["qi"], f_t10_late["di_per_month"], f_t10_late["b"], qmin=10), note=f"fit qi {f_t10_late['qi']:.0f}, Di {f_t10_late['di_per_month']*12:.2f}/yr, b {f_t10_late['b']:.2f}; TEC-10 taken as 90 % of commingled field sales")
add_case("Four PEMEX wells, average, Arps fit (240 months)", "task 4 CNH monthly", profile(f_avg["qi"], f_avg["di_per_month"], f_avg["b"], qmin=10), note=f"fit qi {f_avg['qi']:.0f}, Di {f_avg['di_per_month']*12:.2f}/yr, b {f_avg['b']:.2f}")
# ---------------------------------------------------------------- 3. recommended range
# low: TEC-10's own single-completion decline (b 0.49) at Petrel Robertson's 100 bbl/d
# base: 180 bbl/d first month (between GLJ 1P 196 and TEC-10 actual 181) with b 0.9, midway between the single-completion
#       TEC-10 shape (0.49) and the multi-completion PEMEX-average shape (1.26), for a well higher on structure with more pay
# high: PEMEX-average shape (b 1.26, Di 1.22/yr) at 300 bbl/d, i.e. the IFR curve's outcome, which needs a PEMEX-style 30-year life with recompletions
shapes = {"low (P90)": (100.0, f_t10_late["di_per_month"], f_t10_late["b"]),
          "base (P50)": (180.0, f_t10_late["di_per_month"], 0.9),
          "high (P10)": (300.0, f_avg["di_per_month"], f_avg["b"])}
def scaled(lab): q1, di, b = shapes[lab]; return profile(q1 / arps(0.5, 1, di, b), di, b, qmin=10)
rec = {k: v[0] for k, v in shapes.items()}
for lab, (q1, di, b) in shapes.items():
    add_case(f"Recommended {lab}: first month {q1:.0f} bbl/d, Di {di*12:.2f}/yr, b {b:.2f}", "this study", scaled(lab), note="10 bbl/d economic cut-off")
cases = pd.DataFrame(cases); cases.to_csv(OUT + "cases.csv", index=False)
prof = pd.DataFrame({"month": np.arange(1, 361)})
for lab in shapes: prof[lab.split(" ")[0] + "_bpd"] = scaled(lab)
prof["ifr_2020_bpd"] = profile(**ifr_p, qmin=0)[:360]
prof.to_csv(OUT + "tec12_profiles_monthly.csv", index=False)
summary = dict(avg_check_max_abs_diff_bpd=round(float(chk.max()), 3), fits=dict(pemex_avg=f_avg, tec10=f_t10, tec10_with_late=f_t10_late, ifr_2020=dict(qi=ifr_p["qi"], di_per_month=ifr_p["di"], b=ifr_p["b"])),
               late_constraint=late.to_dict("records"), glj_tec12_totals_mbbl=dict(p1=float(np.nansum(glj.t12_1p * glj.days) / 1e3), p2=float(np.nansum(glj.t12_2p * glj.days) / 1e3), p3=float(np.nansum(glj.t12_3p * glj.days) / 1e3)),
               recommended={k: dict(first_month_bpd=v[0], di_per_yr=v[1]*12, b=v[2], **stats(scaled(k))) for k, v in shapes.items()})
json.dump(summary, open(OUT + "summary.json", "w"), indent=1, default=float)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(cases[["case", "ip_first_month_bpd", "month12_bpd", "month36_bpd", "cum_1yr_bbl", "cum_5yr_bbl", "cum_20yr_bbl", "eur_bbl"]].to_string())
print(json.dumps(summary, indent=1, default=float))

# ---------------------------------------------------------------- 4. figure
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(17, 8))
t = np.arange(1, 361)
for w, col in [("TEC-2", "#bbb"), ("TEC-6", "#999"), ("TEC-7", "#777"), ("TEC-9", "#555")]:
    ax.plot(tc.index, tc[w], color=col, lw=0.7, label=f"{w} (CNH monthly, producing months)")
ax.plot(tc.index, tc["avg_4_pemex_wells"], color="k", lw=1.5, label="four-well average")
ax.plot(tc.index, tc["TEC-10"], color="#ff7f0e", lw=2.5, label="TEC-10 actual 2018-19 (15 months)")
ax.scatter(late.month_on_prod, late.tec10_est_bpd, color="#ff7f0e", marker="x", s=80, label="TEC-10 implied by 2020-22 field sales (90 %)")
ax.plot(t, profile(**ifr_p, qmin=0)[:360], color="red", lw=1.5, ls="--", label="IFR 2020 TEC-12 curve (qi 342, b 1.7): 401 kbbl")
for lab, col, c in [("GLJ 1P", "#2ca02c", "t12_1p"), ("GLJ 2P", "#1f77b4", "t12_2p"), ("GLJ 3P", "#9467bd", "t12_3p")]:
    q, d = glj_profile(c); ax.plot(np.arange(1, len(q) + 1), q, color=col, lw=1, ls=":", label=f"{lab} TEC-12 Dir ({(q*d).sum()/1e3:.0f} kbbl)")
for lab in shapes:
    q = scaled(lab); ax.plot(t, np.where(q > 0, q, np.nan), lw=2, label=f"recommended {lab}: {shapes[lab][0]:.0f} bbl/d, b {shapes[lab][2]:.2f}, EUR {(q*DPM).sum()/1e3:.0f} kbbl")
ax.set_yscale("log"); ax.set_ylim(5, 600); ax.set_xlim(0, 300); ax.set_xlabel("month on production"); ax.set_ylabel("oil rate (bbl/d)")
ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=7.5, loc="upper right"); ax.set_title("Tecolutla vertical-well type curve: data, existing forecasts and the recommended TEC-12 range")
labels = ["IFR 2020 curve", "IFR 2023 econ (to limit)", "GLJ 1P", "GLJ 2P", "GLJ 3P", "PR base", "PR upside", "Simmons low*", "Simmons most likely*", "Simmons upper*", "Simmons high*", "TEC-10 fit (15 mo)", "TEC-10 fit + sales", "PEMEX avg fit", "Rec. low", "Rec. base", "Rec. high"]
vals = [cases.eur_bbl.iloc[0], cases.eur_bbl.iloc[2], cases.eur_bbl.iloc[3], cases.eur_bbl.iloc[4], cases.eur_bbl.iloc[5], cases.eur_bbl.iloc[7], cases.eur_bbl.iloc[8]] + list(cases.eur_bbl.iloc[9:13]) + list(cases.eur_bbl.iloc[13:16]) + list(cases.eur_bbl.iloc[16:19])
colors = ["red", "red", "#2ca02c", "#1f77b4", "#9467bd", "grey", "grey", "#ccc", "#ccc", "#ccc", "#ccc", "#ff7f0e", "#ff7f0e", "k", "tab:olive", "tab:olive", "tab:olive"]
ax2.barh(labels, np.array(vals) / 1e3, color=colors); ax2.invert_yaxis(); ax2.set_xlabel("EUR or sales volume (kbbl)"); ax2.grid(axis="x", alpha=0.3)
for i, v in enumerate(vals): ax2.text(v / 1e3 + 5, i, f"{v/1e3:.0f}", va="center", fontsize=8)
ax2.set_title("TEC-12 volumes in circulation (* Simmons = TEC-12 + TEC-13, 8-year sales)")
plt.tight_layout(); plt.savefig("figures/06_type_curve_forecast.png", dpi=140); print("figure written")
