"""Task 4: tidy Tecolutla production database.
Usage: python src/production_db.py
Outputs (data/processed/):
  tecolutla_production.parquet / .csv   tidy monthly records, one row per well-month-source
  tecolutla_field_monthly.csv           one 'best available' field oil series with the basis named per month
  tecolutla_production_allocations.csv  block volumes that exist only as totals (wellfile summaries), never spread to months
  tecolutla_tec10_daily.csv             TEC-10 daily test/production data Sep 2018 - Nov 2019
  tecolutla_production_gaps.csv         months with no record inside each well's producing life, plus documented pre-record gaps
  tecolutla_gor_flags.csv               well-months whose GOR is outside the solution-GOR band
  production_summary.json
  figures/04_production_history.png
Nothing is interpolated. Every row carries source_file/source_sheet and a source_kind.
"""
import json, re
import numpy as np, pandas as pd, openpyxl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

A = "data/raw/appraisal_plan/Production (Tecolutla).xlsx"
B = "data/raw/appraisal_plan/Tecolutla Production to Dec 2018.xlsx"
C = "data/raw/appraisal_plan/Tecolutla Production History (Possible Solution GOR).xlsx"
D = "data/raw/appraisal_plan/Tecolutla Production Summary (by well by perf interval).xlsx"
E = "data/raw/staff_production/Tecolutla Production Tracking.xlsx"
M23 = "data/raw/tec12_drill/2023-09-29 Tec-12 Economics.xlsm"
OUT = "data/processed/"
SOL_GOR_IFR = 552      # scf/bbl, IFR PVT Calculator (Tecolutla).xlsx Oil!C7 (assumed input, "possible solution GOR")
SOL_GOR_PEMEX = 59.9 * 5.6146  # scf/bbl from RGA 59.9 m3/m3, PEMEX '6 -Resumen Campo Tecolutla.docx' table 5
WELLMAP = {"TECOLUTLA-2": "TEC-2", "TECOLUTLA-6": "TEC-6", "TECOLUTLA-7": "TEC-7", "TECOLUTLA-9": "TEC-9",
           "TECOLUTLA-10": "TEC-10", "TEC-10": "TEC-10", "TEC-2": "TEC-2", "TEC-7": "TEC-7", "TEC-11": "TEC-11",
           "CAMPO": "FIELD", "CAMPO TECO": "FIELD"}

def sheet(f, name, hdr=0):
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True); ws = wb[name]
    rows = list(ws.iter_rows(values_only=True)); wb.close()
    h = [str(c).strip() if c is not None else f"c{i}" for i, c in enumerate(rows[hdr])]
    return pd.DataFrame(rows[hdr + 1:], columns=h)

def num(s): return pd.to_numeric(s, errors="coerce")

recs = []
# ------------------------------------------------------------------ 1. CNH/PEMEX monthly per well, 1966-2016
a = sheet(A, "Production"); a["Date"] = pd.to_datetime(a["Date"], errors="coerce"); a = a.dropna(subset=["Date"])
c = sheet(C, "Production"); c["Date"] = pd.to_datetime(c["Date"], errors="coerce"); c = c.dropna(subset=["Date"])
for col in ["Oil (bbl)", "Wat (bbl)", "Gas (mcf)", "DOM", "Prod Days", "From (mkb)", "To (mkb)"]:
    a[col] = num(a[col]); 
    if col in c: c[col] = num(c[col])
# cross-check A vs C on common well-months
m = a.merge(c[["WELL", "Date", "Oil (bbl)", "Gas (mcf)", "Wat (bbl)"]], on=["WELL", "Date"], suffixes=("", "_C"))
xcheck = {"common_rows": len(m), "oil_max_abs_diff_bbl": float((m["Oil (bbl)"] - m["Oil (bbl)_C"]).abs().max()),
          "gas_max_abs_diff_mcf": float((m["Gas (mcf)"] - m["Gas (mcf)_C"]).abs().max()),
          "rows_only_in_A": int(len(a) - len(m)), "rows_only_in_C": int(len(c) - len(m))}
for r in a.itertuples():
    flag = ""
    if r.WELL == "TECOLUTLA-2" and r.Date >= pd.Timestamp("2015-01-01"):
        flag = "hand-entered: integer bbl/d oil and water rising exactly 390 bbl/month; not in the CNH-sourced copy (C)"
    recs.append(dict(well=WELLMAP[r.WELL], date=r.Date, source_kind="cnh_monthly_pemex_era", oil_bbl=r._13, water_bbl=r._14, gas_mcf=r._15,
                     days_on=r._7, days_in_month=r.DOM, perf_top_mkb=r._8, perf_base_mkb=r._9, zone=None,
                     source_file="appraisal_plan/Production (Tecolutla).xlsx", source_sheet="Production", quality_flag=flag))
# ------------------------------------------------------------------ 2. field-level 1960-1965 and Tonalli early monthly (B)
b = sheet(B, "DATA"); b["Date"] = pd.to_datetime(b["Date"], errors="coerce")
for col in ["Oil (bbl/d)", "Wat (bbl/d)", "Gas (mcf/d)", "DOM"]: b[col] = num(b[col])
b = b[(b.TYPE == "ACTUAL")].dropna(subset=["Date"])
campo = b[(b.WELL == "CAMPO") & (b["Oil (bbl/d)"] > 0)]
for r in campo.itertuples():
    recs.append(dict(well="FIELD", date=r.Date, source_kind="cnh_monthly_field_level", oil_bbl=r._10 * r.DOM, water_bbl=r._11 * r.DOM if pd.notna(r._11) else np.nan,
                     gas_mcf=r._12 * r.DOM if pd.notna(r._12) else np.nan, days_on=np.nan, days_in_month=r.DOM, perf_top_mkb=np.nan, perf_base_mkb=np.nan, zone=r.Zone,
                     source_file="appraisal_plan/Tecolutla Production to Dec 2018.xlsx", source_sheet="DATA (WELL=CAMPO)",
                     quality_flag="field total, no well split; rate x days-in-month"))
ton = b[b.WELL.isin(["TECOLUTLA-10", "TECOLUTLA-2"]) & (b.Date >= "2016-02-01")]
for r in ton.itertuples():
    recs.append(dict(well=WELLMAP[r.WELL], date=r.Date, source_kind="tonalli_monthly_test_2018", oil_bbl=r._10 * r.DOM, water_bbl=r._11 * r.DOM,
                     gas_mcf=np.nan, days_on=np.nan, days_in_month=r.DOM, perf_top_mkb=num(pd.Series([r._8]))[0], perf_base_mkb=num(pd.Series([r._9]))[0], zone=r.Zone,
                     source_file="appraisal_plan/Tecolutla Production to Dec 2018.xlsx", source_sheet="DATA", quality_flag=str(r.Comment)))
# ------------------------------------------------------------------ 3. TEC-10 daily Sep 2018 - Nov 2019 (2023 econ workbook, sheet Tec-10 Prod)
wb = openpyxl.load_workbook(M23, read_only=True, data_only=True); ws = wb["Tec-10 Prod"]
rows = list(ws.iter_rows(min_row=4, max_col=8, values_only=True)); wb.close()
t10 = pd.DataFrame(rows, columns=["date", "ptbg_psi", "oil_bpd", "gas_mcfd", "water_bpd", "gor_scf_bbl", "oil_cut", "total_fluid_bpd"])
t10["date"] = pd.to_datetime(t10.date, errors="coerce"); t10 = t10.dropna(subset=["date"])
for col in t10.columns[1:]: t10[col] = num(t10[col])
t10["source_file"] = "tec12_drill/2023-09-29 Tec-12 Economics.xlsm"; t10["source_sheet"] = "Tec-10 Prod"
t10.to_csv(OUT + "tecolutla_tec10_daily.csv", index=False)
mon = t10.set_index("date").resample("MS").agg(oil_bbl=("oil_bpd", "sum"), water_bbl=("water_bpd", "sum"), gas_mcf=("gas_mcfd", "sum"),
                                              days_on=("oil_bpd", "count"), ptbg=("ptbg_psi", "mean"))
for d, r in mon.iterrows():
    recs.append(dict(well="TEC-10", date=d, source_kind="tonalli_daily_sum", oil_bbl=r.oil_bbl, water_bbl=r.water_bbl, gas_mcf=r.gas_mcf, days_on=r.days_on,
                     days_in_month=d.days_in_month, perf_top_mkb=2349.5, perf_base_mkb=2353.0, zone=3,
                     source_file="tec12_drill/2023-09-29 Tec-12 Economics.xlsm", source_sheet="Tec-10 Prod",
                     quality_flag=f"sum of {int(r.days_on)} daily records; mean Ptbg {r.ptbg:.0f} psi" + ("" if r.days_on >= d.days_in_month - 1 else "; partial month")))
# ------------------------------------------------------------------ 4. Tonalli trucking: sales per well per month, water hauled
tr = sheet(E, "TRUCKING"); tr["Date"] = pd.to_datetime(tr["Date"], errors="coerce"); tr = tr.dropna(subset=["Date"])
vc = {"ship_bbl": "Volume Shipped (bbls) from Site", "ton_oil": "TONALLI - Oil (bbls)", "ton_wat": "TONALLI - Water (bbl)", "pem_oil": "PEMEX - Oil (bbls)", "pem_wat": "PEMEX - Water (bbl)"}
for k, v in vc.items(): tr[k] = num(tr[v])
tr["oil_dest"] = tr.Destination.isin(["EZOR", "ESA", "Santa Agueda 49", "Santa Agueda"])
tr = tr[tr.Well != "CANCELADA"]
tr["month"] = tr.Date.dt.to_period("M").dt.to_timestamp()
g = tr.groupby(["Well", "month"]).agg(loads=("Date", "size"), ship_bbl=("ship_bbl", "sum"), ton_oil=("ton_oil", "sum"), ton_wat=("ton_wat", "sum"),
                                     pem_oil=("pem_oil", "sum"), pem_wat=("pem_wat", "sum"), oil_loads=("oil_dest", "sum")).reset_index()
for r in g.itertuples():
    recs.append(dict(well=WELLMAP[r.Well], date=r.month, source_kind="tonalli_trucking_sales", oil_bbl=r.pem_oil if r.pem_oil > 0 else r.ton_oil,
                     water_bbl=r.ton_wat, gas_mcf=np.nan, days_on=np.nan, days_in_month=r.month.days_in_month, perf_top_mkb=np.nan, perf_base_mkb=np.nan, zone=None,
                     source_file="staff_production/Tecolutla Production Tracking.xlsx", source_sheet="TRUCKING",
                     quality_flag=f"{r.loads} loads ({int(r.oil_loads)} to oil terminals); oil = PEMEX-measured where >0 else Tonalli; Tonalli oil {r.ton_oil:.0f}, shipped {r.ship_bbl:.0f} bbl"))
# ------------------------------------------------------------------ 5. PEMEX statement reconciliation (field sales)
rc = sheet(E, "Reconciliation"); rc["Month"] = pd.to_datetime(rc["Month"], errors="coerce"); rc["PEMEX Oil (bbl)"] = num(rc["PEMEX Oil (bbl)"])
rc = rc[(rc.Source.astype(str).str.contains("pemex statement")) & rc["PEMEX Oil (bbl)"].notna()]
for r in rc.itertuples():
    recs.append(dict(well="FIELD", date=r.Month, source_kind="pemex_statement_sales", oil_bbl=r._5, water_bbl=np.nan, gas_mcf=np.nan, days_on=np.nan,
                     days_in_month=r.Month.days_in_month, perf_top_mkb=np.nan, perf_base_mkb=np.nan, zone=None,
                     source_file="staff_production/Tecolutla Production Tracking.xlsx", source_sheet="Reconciliation", quality_flag=f"{r.From:%Y-%m-%d} to {r.To:%Y-%m-%d}; {r.Status}"))
# ------------------------------------------------------------------ assemble
df = pd.DataFrame(recs)
df["date"] = pd.to_datetime(df.date)
df["oil_bpd_cd"] = df.oil_bbl / df.days_in_month
df["water_cut"] = df.water_bbl / (df.water_bbl + df.oil_bbl)
df["gor_scf_bbl"] = df.gas_mcf * 1000 / df.oil_bbl.where(df.oil_bbl > 0)
df = df.sort_values(["well", "date", "source_kind"]).reset_index(drop=True)
cols = ["well", "date", "source_kind", "oil_bbl", "water_bbl", "gas_mcf", "days_on", "days_in_month", "oil_bpd_cd", "water_cut", "gor_scf_bbl",
        "perf_top_mkb", "perf_base_mkb", "zone", "source_file", "source_sheet", "quality_flag"]
df = df[cols]; df["zone"] = df.zone.astype(str).where(df.zone.notna(), None); df["quality_flag"] = df.quality_flag.astype(str)
df.to_parquet(OUT + "tecolutla_production.parquet", index=False)
df.to_csv(OUT + "tecolutla_production.csv", index=False)

# ------------------------------------------------------------------ allocations (block totals, never spread)
wb = openpyxl.load_workbook(D, read_only=True, data_only=True); zrows = list(wb["By Zone"].iter_rows(values_only=True, max_col=8)); wb.close()
alloc = []; well = None
for r in zrows[2:]:
    first, second, start, end, oil, zone, comment, test = (list(r) + [None] * 8)[:8]
    if isinstance(first, str) and first.startswith("TECOLUTLA"): well = first; continue
    if isinstance(second, str) and second.startswith("TECOLUTLA"): well = second; continue
    if hasattr(start, "year"):
        alloc.append(dict(well=WELLMAP.get(well, well), interval_mss=first, interval_mmd=second, start=pd.Timestamp(start), end=pd.Timestamp(end), oil_bbl=oil, zone=zone,
                          comment=comment, test_info=test, source_file="appraisal_plan/Tecolutla Production Summary (by well by perf interval).xlsx", source_sheet="By Zone (last updated 2020-03-01)"))
alloc = pd.DataFrame(alloc)
alloc["oil_bbl"] = num(alloc.oil_bbl)
# which block totals are NOT covered by monthly records
def monthly_cov(w, s, e):
    sub = df[(df.well == w) & (df.source_kind == "cnh_monthly_pemex_era") & (df.date >= s) & (df.date <= e)]
    return float(sub.oil_bbl.sum())
alloc["monthly_records_bbl"] = [monthly_cov(w, s, e) for w, s, e in zip(alloc.well, alloc.start, alloc.end)]
alloc["not_in_monthly_bbl"] = (alloc.oil_bbl - alloc.monthly_records_bbl).round(0)
alloc.to_csv(OUT + "tecolutla_production_allocations.csv", index=False)

# ------------------------------------------------------------------ field 'best available' monthly series
def pick(dfm):
    order = ["cnh_monthly_pemex_era", "cnh_monthly_field_level", "tonalli_daily_sum", "pemex_statement_sales", "tonalli_trucking_sales", "tonalli_monthly_test_2018"]
    out = []
    months = pd.period_range(dfm.date.min(), dfm.date.max(), freq="M")
    for p in months:
        d = p.to_timestamp(); sub = dfm[dfm.date == d]
        if sub.empty:
            out.append(dict(date=d, oil_bbl=np.nan, basis="no record")); continue
        if (sub.source_kind == "cnh_monthly_pemex_era").any():
            s = sub[sub.source_kind == "cnh_monthly_pemex_era"]; out.append(dict(date=d, oil_bbl=s.oil_bbl.sum(), basis="sum of CNH monthly well records")); continue
        if (sub.source_kind == "cnh_monthly_field_level").any():
            s = sub[sub.source_kind == "cnh_monthly_field_level"]; out.append(dict(date=d, oil_bbl=s.oil_bbl.sum(), basis="CNH field-level monthly")); continue
        if (sub.source_kind == "pemex_statement_sales").any():
            s = sub[sub.source_kind == "pemex_statement_sales"]; out.append(dict(date=d, oil_bbl=s.oil_bbl.sum(), basis="PEMEX statement sales (field)")); continue
        if (sub.source_kind == "tonalli_trucking_sales").any():
            s = sub[sub.source_kind == "tonalli_trucking_sales"]; out.append(dict(date=d, oil_bbl=s.oil_bbl.sum(), basis="trucking tickets, PEMEX-measured oil (field)")); continue
        s = sub; out.append(dict(date=d, oil_bbl=s.oil_bbl.sum(), basis="/".join(sorted(set(s.source_kind)))))
    return pd.DataFrame(out)
field = pick(df)
field["cum_oil_bbl_records_only"] = field.oil_bbl.fillna(0).cumsum()
field.to_csv(OUT + "tecolutla_field_monthly.csv", index=False)

# ------------------------------------------------------------------ gaps
gaps = []
pem = df[df.source_kind == "cnh_monthly_pemex_era"]
for w, sub in pem.groupby("well"):
    have = set(sub.date.dt.to_period("M"))
    rng = pd.period_range(sub.date.min(), sub.date.max(), freq="M")
    missing = [p for p in rng if p not in have]
    # group consecutive months
    if missing:
        start = prev = missing[0]
        for p in missing[1:] + [None]:
            if p is None or p != prev + 1:
                gaps.append(dict(well=w, gap_start=str(start), gap_end=str(prev), months=(prev - start).n + 1, kind="no monthly record inside producing life", source="derived from CNH monthly table"))
                if p is not None: start = p
            if p is not None: prev = p
documented = [
    ("TEC-2", "1956-06", "1971-12", "no monthly record; wellfile summary gives 40,885 bbl for interval 2335-2339 mMD (zone 2), and the 2345-2349 mMD test only", "By Zone / Table sheets"),
    ("TEC-6", "1956-10", "1965-12", "no monthly record; wellfile summary gives 509,993 bbl for 1956-10 to 1972-02 of which 117,394 bbl is in CNH monthly data, i.e. 392,599 bbl unrecorded monthly", "By Zone sheet comment"),
    ("TEC-7", "1957-01", "1968-05", "no data ('?'); initial test 352 bbl/d", "By Zone sheet"),
    ("FIELD", "1956-06", "1959-12", "no field-level record; CNH field series starts 1960-01", "Tecolutla Production to Dec 2018.xlsx DATA"),
    ("FIELD", "2016-02", "2018-06", "field shut in between PEMEX handover and Tonalli restart; no production", "context"),
    ("TEC-10", "2019-12", "2022-12", "no well-level record after the daily sheet ends 2019-11-24; only commingled field sales (CAMPO TECO) exist", "Tracking workbook"),
    ("TEC-2", "2019-09", "2022-12", "no well-level record; By Zone gives 7,812 bbl for 2019-06 to 2020-03; commingled thereafter", "By Zone / Tracking"),
    ("FIELD", "2020-04", "2020-06", "no sales tickets or PEMEX statements (COVID shut-in?)", "Tracking workbook"),
    ("FIELD", "2022-03", "2022-10", "no sales tickets", "Tracking workbook"),
]
for w, s, e, k, src in documented:
    gaps.append(dict(well=w, gap_start=s, gap_end=e, months=(pd.Period(e, "M") - pd.Period(s, "M")).n + 1, kind=k, source=src))
gaps = pd.DataFrame(gaps).sort_values(["well", "gap_start"]); gaps.to_csv(OUT + "tecolutla_production_gaps.csv", index=False)

# ------------------------------------------------------------------ GOR analysis
pem = pem.copy(); pem["gor"] = pem.gas_mcf * 1000 / pem.oil_bbl.where(pem.oil_bbl > 0)
cum_gor = {}
for lbl, (s, e) in {"1966-1992": ("1966-01-01", "1992-12-31"), "1993-1999": ("1993-01-01", "1999-12-31"), "2003-2012": ("2003-01-01", "2012-12-31"), "2013-2016": ("2013-01-01", "2016-12-31"), "all 1966-2016": ("1966-01-01", "2016-12-31")}.items():
    sub = pem[(pem.date >= s) & (pem.date <= e)]
    cum_gor[lbl] = dict(oil_bbl=float(sub.oil_bbl.sum()), gas_mcf=float(sub.gas_mcf.sum()), gor=float(sub.gas_mcf.sum() * 1000 / sub.oil_bbl.sum()))
flags = pem[(pem.gor > 1500) | (pem.gor < 150)][["well", "date", "oil_bbl", "gas_mcf", "gor", "days_on"]].copy()
flags["flag"] = np.where(flags.gor > 1500, "GOR > 1500 scf/bbl", "GOR < 150 scf/bbl")
# same-month identical GOR across wells = field-allocated gas
piv = pem.pivot_table(index="date", columns="well", values="gor")
same = piv[(piv.round(0).nunique(axis=1) == 1) & (piv.notna().sum(axis=1) >= 2)]
flags.to_csv(OUT + "tecolutla_gor_flags.csv", index=False)
t10m = mon.copy(); t10m["gor"] = t10m.gas_mcf * 1000 / t10m.oil_bbl
summary = dict(
    cross_check_A_vs_C=xcheck,
    pemex_era_totals_bbl={w: float(v) for w, v in pem.groupby("well").oil_bbl.sum().items()},
    pemex_era_total_bbl=float(pem.oil_bbl.sum()),
    field_level_1960_1965_bbl=float(df[df.source_kind == "cnh_monthly_field_level"].oil_bbl.sum()),
    tec10_daily_range=[str(t10.date.min().date()), str(t10.date.max().date())], tec10_daily_oil_bbl=float(t10.oil_bpd.sum()),
    trucking_pemex_oil_by_well=g.groupby("Well").pem_oil.sum().round(0).to_dict(), trucking_water_by_well=g.groupby("Well").ton_wat.sum().round(0).to_dict(),
    pemex_statement_sales_total_bbl=float(rc["PEMEX Oil (bbl)"].sum()), pemex_statement_range=[str(rc.Month.min().date()), str(rc.Month.max().date())],
    allocations_total_bbl=float(alloc.oil_bbl.sum()), allocations_not_in_monthly_bbl=float(alloc.not_in_monthly_bbl.sum()),
    cumulative_gor=cum_gor, gor_flag_count=int(len(flags)), months_identical_gor_across_wells=int(len(same)),
    identical_gor_years=sorted(set(same.index.year.tolist())),
    tec10_monthly_gor=t10m.gor.round(0).to_dict().__class__.__name__ and {str(k.date()): float(round(v, 0)) for k, v in t10m.gor.items()},
    solution_gor_refs={"IFR PVT calculator input": SOL_GOR_IFR, "PEMEX Resumen RGA 59.9 m3/m3": round(SOL_GOR_PEMEX, 0),
                       "initial tests 1956-73 (By Zone)": [431, 541, 576, 532, 437, 521, 765], "TEC-10 initial test 2018": 762},
)
json.dump(summary, open(OUT + "production_summary.json", "w"), indent=1, default=str)
print(json.dumps(summary, indent=1, default=str)[:6000])
print(alloc[["well", "interval_mmd", "start", "end", "oil_bbl", "monthly_records_bbl", "not_in_monthly_bbl"]].to_string())
print(gaps.to_string())
print(same.round(0).to_string())

# ------------------------------------------------------------------ figure
fig, axes = plt.subplots(4, 1, figsize=(16, 15), sharex=True, gridspec_kw={"height_ratios": [1.4, 1, 1, 1]})
ax = axes[0]
for w, col in [("TEC-6", "#1f77b4"), ("TEC-7", "#2ca02c"), ("TEC-2", "#d62728"), ("TEC-9", "#9467bd")]:
    s = pem[pem.well == w].set_index("date").oil_bpd_cd.asfreq("MS")  # NaN months break the line: no interpolation drawn
    ax.plot(s.index, s.values, lw=0.9, color=col, label=f"{w} (CNH monthly)")
fl = df[df.source_kind == "cnh_monthly_field_level"].set_index("date").oil_bpd_cd.asfreq("MS")
ax.plot(fl.index, fl.values, lw=1.2, color="k", ls="--", label="field level 1960-65 (CNH)")
t = df[(df.well == "TEC-10") & (df.source_kind == "tonalli_daily_sum")].set_index("date")
ax.plot(t.index, t.oil_bbl / t.days_on, lw=1.5, color="#ff7f0e", label="TEC-10 (daily sheet, producing-day avg)")
ps = df[df.source_kind == "pemex_statement_sales"].set_index("date").oil_bpd_cd.asfreq("MS")
ax.plot(ps.index, ps.values, lw=1.2, color="grey", label="field sales, PEMEX statements (calendar-day)")
tk = df[(df.well == "FIELD") & (df.source_kind == "tonalli_trucking_sales")].set_index("date").oil_bpd_cd.asfreq("MS")
ax.plot(tk.index, tk.values, lw=1.0, color="grey", ls=":", label="field sales, trucking tickets (calendar-day)")
ax.set_yscale("log"); ax.set_ylim(1, 1000); ax.set_ylabel("oil rate (bbl/d, calendar-day unless noted)"); ax.legend(fontsize=8, ncol=3, loc="upper right"); ax.grid(alpha=0.3, which="both")
ax.set_title("Tecolutla oil production by well, 1960-2022, as recorded (no interpolation). Pre-1960 and TEC-6 1956-65 exist only as block totals (see allocations table).")
for s_, e_, lab in [("1956-06-01", "1959-12-31", "no record"), ("2016-02-01", "2018-06-30", "shut in"), ("2020-04-01", "2020-06-30", ""), ("2022-03-01", "2022-10-31", "")]:
    ax.axvspan(pd.Timestamp(s_), pd.Timestamp(e_), color="grey", alpha=0.12)
    if lab: ax.text(pd.Timestamp(s_), 600, lab, fontsize=8, color="dimgrey")
ax = axes[1]
for w, col in [("TEC-6", "#1f77b4"), ("TEC-7", "#2ca02c"), ("TEC-2", "#d62728"), ("TEC-9", "#9467bd")]:
    s = pem[pem.well == w].set_index("date").water_cut.asfreq("MS")
    ax.plot(s.index, s.values * 100, lw=0.9, color=col, label=w)
ax.plot(t.index, t.water_cut * 100, lw=1.5, color="#ff7f0e", label="TEC-10")
ax.set_ylabel("water cut (%)"); ax.set_ylim(0, 100); ax.legend(fontsize=8, ncol=5); ax.grid(alpha=0.3)
ax = axes[2]
for w, col in [("TEC-6", "#1f77b4"), ("TEC-7", "#2ca02c"), ("TEC-2", "#d62728"), ("TEC-9", "#9467bd")]:
    s = pem[pem.well == w].set_index("date").gor.asfreq("MS")
    ax.plot(s.index, s.values, lw=0.8, color=col, label=w)
ax.plot(t10m.index, t10m.gor, lw=1.5, color="#ff7f0e", label="TEC-10")
ax.axhline(SOL_GOR_IFR, color="k", ls="--", lw=1, label=f"IFR PVT input Rs = {SOL_GOR_IFR} scf/bbl")
ax.axhline(SOL_GOR_PEMEX, color="k", ls=":", lw=1, label=f"PEMEX PVT RGA 59.9 m3/m3 = {SOL_GOR_PEMEX:.0f} scf/bbl")
ax.set_yscale("log"); ax.set_ylim(50, 30000); ax.set_ylabel("producing GOR (scf/bbl), monthly"); ax.legend(fontsize=8, ncol=4); ax.grid(alpha=0.3, which="both")
for y_ in [1993, 1998, 2008, 2013]:
    ax.axvline(pd.Timestamp(f"{y_}-01-01"), color="grey", lw=0.5)
ax = axes[3]
cum = field.set_index("date").cum_oil_bbl_records_only.asfreq("MS") / 1e3
ax.plot(cum.index, cum.values, color="k", lw=1.5, label="cumulative of monthly records (field best-available series)")
extra = alloc[alloc.not_in_monthly_bbl > 1000]
tot = float(alloc.oil_bbl.sum())
ax.axhline(tot / 1e3, color="red", ls="--", lw=1, label=f"By Zone summary total (Mar 2020) {tot/1e3:,.0f} kbbl, includes {alloc.not_in_monthly_bbl.sum()/1e3:,.0f} kbbl wellfile block totals")
ax.set_ylabel("cumulative oil (kbbl)"); ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.3)
ax.set_xlim(pd.Timestamp("1955-01-01"), pd.Timestamp("2023-06-01"))
plt.tight_layout(); plt.savefig("figures/04_production_history.png", dpi=140)
print("figure written")
