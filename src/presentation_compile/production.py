"""Build production_by_well.csv, field_annual.csv, producing_wells.csv from the repo production database.
Read-only on the repo. Output to the compile folder."""
import pandas as pd, numpy as np, json
REPO = "/home/user/git_practice/"
OUT = "data/processed/presentation/"
SRC = "data/processed/tecolutla_production.csv"
d = pd.read_csv(REPO + SRC)
d["month"] = d.date.str[:7]

rows = []
def add(r, well, rule, oil=None, water=None, gas=None, oil_src=None, water_src=None, gas_src=None, flag=None, attributed=None):
    rows.append(dict(month=r["month"], well=well,
                     oil_bbl=r["oil_bbl"] if oil is None else oil,
                     water_bbl=r["water_bbl"] if water is None else water,
                     gas_mcf=r["gas_mcf"] if gas is None else gas,
                     days_on=r["days_on"],
                     oil_source=oil_src or f"{SRC} source_kind={r['source_kind']} ({r['source_file']} > {r['source_sheet']})",
                     water_source=water_src or f"{SRC} source_kind={r['source_kind']}",
                     gas_source=gas_src or (f"{SRC} source_kind={r['source_kind']}" if pd.notna(r["gas_mcf"]) else ""),
                     selection_rule=rule, attributed_to=attributed or "", quality_flag=(flag if flag is not None else (r["quality_flag"] if pd.notna(r["quality_flag"]) else ""))))

# R1: 1960-01..1965-12 field-level CNH (no well split)
for _, r in d[d.source_kind == "cnh_monthly_field_level"].iterrows():
    add(r, "FIELD (no well split)", "R1 CNH field-level monthly 1960-65; only source for those months", gas=np.nan, gas_src="")
# R2: PEMEX era per well
for _, r in d[d.source_kind == "cnh_monthly_pemex_era"].iterrows():
    add(r, r["well"], "R2 CNH monthly per well 1966-2016 (only per-well source)")

tk = d[d.source_kind == "tonalli_trucking_sales"]
ds = d[d.source_kind == "tonalli_daily_sum"]
# R3: TEC-10 test months Jul-Aug 2018 (water only) from trucking
for _, r in tk[(tk.well == "TEC-10") & (tk.month <= "2018-08")].iterrows():
    add(r, "TEC-10", "R3 TEC-10 pre-production test hauls (trucking); daily sheet starts Sep-2018")
# R4: TEC-10 Sep-2018..Nov-2019 from the daily sheet (wellhead, per-well measured, has gas)
for _, r in ds.iterrows():
    add(r, "TEC-10", "R4 TEC-10 daily-sheet monthly sum (wellhead basis, only per-well oil+water+gas series); trucking TEC-10 rows not used to avoid double count")
# R5: TEC-2 trucking (Sep-2018, Jun-2019); Jul/Aug-2019 trucking oil=0 because TEC-2 oil was sold commingled in CAMPO TECO;
# oil for those two months taken from the 2019 TEC-2 lease operating statement (acc_review.csv), water from trucking.
LOS = "data/processed/database_review/acc_review.csv row 1FCUF9Ppm_JjaOqnXVaJohTKmRR1IfE0R (Tonalli 2019 Operations Statements, TEC-2 sheet: Jul 1,746.6 bbl, Aug 1,043.9 bbl sold)"
los_tec2 = {"2019-07": 1746.6, "2019-08": 1043.9}
for _, r in tk[tk.well == "TEC-2"].iterrows():
    if r["month"] in los_tec2:
        add(r, "TEC-2", "R5 TEC-2: water from trucking; oil from TEC-2 LOS because trucking books TEC-2 oil in the commingled CAMPO TECO stream", oil=los_tec2[r["month"]], oil_src=LOS,
            flag="oil sold commingled (CAMPO TECO); LOS per-well sales volume")
    else:
        add(r, "TEC-2", "R5 TEC-2 trucking sales (PEMEX-measured oil per ticket)")
# R6: TEC-7 and TEC-11 water hauls only
for _, r in tk[tk.well.isin(["TEC-7", "TEC-11"])].iterrows():
    add(r, r["well"], "R6 water hauled to disposal (no oil sold); TEC-11 = test water, TEC-7 = workover/clean-out water")
# R7: commingled field stream Dec-2019..Dec-2022 (CAMPO TECO). Jul-Nov 2019 CAMPO TECO rows dropped: they duplicate TEC-10 (R4) + TEC-2 (R5).
fld = tk[(tk.well == "FIELD") & (tk.month >= "2019-12")]
for _, r in fld.iterrows():
    att = "TEC-10 (CNH 2021 annual filing names TEC-10 sole origin)" if r["month"].startswith("2021") else (
          "TEC-10 (Nov-2022 CNH VHP: TEC-10DES only)" if r["month"] >= "2022-11" else "TEC-10 + TEC-2 commingled (CNH 2020 filing: 'Pozos Tecolutla 2 y Tecolutla 10')")
    add(r, "FIELD commingled (CAMPO TECO)", "R7 commingled field sales tickets Dec-2019 to Dec-2022; water column is BS&W in oil loads only (produced water went to TEC-7 injection), so water left blank",
        water=np.nan, water_src="not recorded per month in tecolutla_production.csv after Aug-2019 (see cnh_production_filings_2020_2022.csv for filed water)", attributed=att)

p = pd.DataFrame(rows).sort_values(["month", "well"]).reset_index(drop=True)
p["year"] = p.month.str[:4].astype(int)
p.to_csv(OUT + "production_by_well.csv", index=False, float_format="%.1f")

# field annual by well
wells = ["FIELD (no well split)", "TEC-2", "TEC-6", "TEC-7", "TEC-9", "TEC-10", "TEC-11", "FIELD commingled (CAMPO TECO)"]
short = {"FIELD (no well split)": "field_1960_65_unsplit", "FIELD commingled (CAMPO TECO)": "commingled_2019_22"}
def col(w): return short.get(w, w.replace("-", "").lower())
years = range(1960, 2023)
out = []
for y in years:
    py = p[p.year == y]
    row = dict(year=y)
    for w in wells:
        q = py[py.well == w]
        row[f"oil_{col(w)}"] = round(q.oil_bbl.sum(), 0) if len(q) else np.nan
        row[f"water_{col(w)}"] = round(q.water_bbl.sum(min_count=1), 0) if len(q) else np.nan
    row["oil_field"] = round(py.oil_bbl.sum(), 0) if len(py) else np.nan
    row["water_field_recorded"] = round(py.water_bbl.sum(min_count=1), 0) if py.water_bbl.notna().any() else np.nan
    row["gas_field_mcf_recorded"] = round(py.gas_mcf.sum(min_count=1), 0) if py.gas_mcf.notna().any() else np.nan
    row["months_with_record"] = int(py.month.nunique())
    row["oil_producing_wells"] = int(py[(py.oil_bbl > 0) & py.well.str.startswith("TEC")].well.nunique())
    out.append(row)
fa = pd.DataFrame(out)
fa["cum_oil_field_recorded"] = fa.oil_field.fillna(0).cumsum().round(0)
fa.loc[fa.oil_field.isna(), "oil_field"] = np.nan
fa["producing_wells_basis"] = "count of wells with oil > 0 in the per-well monthly records"
fa.loc[fa.year.between(1960, 1965), "oil_producing_wells"] = np.nan
fa.loc[fa.year.between(1960, 1965), "producing_wells_basis"] = "no well split (TEC-6 and probably TEC-2 per By Zone wellfile blocks)"
for y, n, b in [(2019, 2, "TEC-10 and TEC-2 (TEC-2 shut in Sep-2019)"), (2020, 2, "CNH 2020 annual filing origin 'Pozos Tecolutla 2 y Tecolutla 10' (commingled; GLJ last TEC-2 production 2020-09)"),
                (2021, 1, "CNH 2021 annual filing: TEC-10 sole origin"), (2022, 1, "TEC-10 (Nov-2022 CNH VHP: TEC-10DES only); TEC-2 not reported")]:
    fa.loc[fa.year == y, "oil_producing_wells"] = n; fa.loc[fa.year == y, "producing_wells_basis"] = b
fa["note"] = ""
fa.loc[fa.year.between(1960, 1965), "note"] = "field total only (no well split); TEC-6 and TEC-2 wellfile block totals 1956-65 not in monthly records"
fa.loc[fa.year.between(2017, 2017), "note"] = "no production record (field shut in at handover 2016-02 to 2018-06)"
fa.loc[fa.year == 2016, "note"] = "TEC-2 Jan-2016 only (hand-entered row)"
fa.loc[fa.year == 2019, "note"] = "Jul-Nov 2019: TEC-10 wellhead (daily sheet) + TEC-2 LOS; CAMPO TECO commingled rows excluded to avoid double count"
fa.loc[fa.year >= 2020, "note"] = "commingled sales tickets (TEC-10 + TEC-2 in 2020; TEC-10 only in 2021 and Nov-22); produced water not in database"
fa.loc[fa.year == 2018, "note"] = "TEC-10 Jul-Aug test water; Sep-Dec TEC-10 wellhead (daily sheet) + TEC-2 Sep test month"
fa.to_csv(OUT + "field_annual.csv", index=False)

# producing wells list
alloc = pd.read_csv(REPO + "data/processed/tecolutla_production_allocations.csv")
lst = []
for w in ["TEC-2", "TEC-6", "TEC-7", "TEC-9", "TEC-10", "TEC-11"]:
    q = p[p.well == w]
    qo = q[q.oil_bbl > 0]
    a = alloc[alloc.well == w]
    lst.append(dict(well=w, operator="PEMEX" if w in ("TEC-2", "TEC-6", "TEC-7", "TEC-9") else "Tonalli",
                    produced_oil=bool(qo.oil_bbl.sum() > 0),
                    first_oil_month_in_records=qo.month.min() if len(qo) else "", last_oil_month_in_records=qo.month.max() if len(qo) else "",
                    years_with_oil_records=int(qo.year.nunique()),
                    cum_oil_bbl_monthly_records=round(q.oil_bbl.sum(), 0), cum_water_bbl_monthly_records=round(q.water_bbl.sum(), 0),
                    cum_gas_mcf_monthly_records=round(q.gas_mcf.sum(), 0) if q.gas_mcf.notna().any() else np.nan,
                    by_zone_allocation_total_bbl=round(a.oil_bbl.sum(), 0) if len(a) else np.nan,
                    by_zone_periods="; ".join(f"{r.start[:7]}..{r.end[:7]} {r.interval_mss} {r.oil_bbl:,.0f}" for r in a.itertuples() if pd.notna(r.oil_bbl)),
                    source=f"{SRC} (rules in production_notes.md); data/processed/tecolutla_production_allocations.csv (By Zone, Mar-2020)"))
def yrs(q):
    ys = sorted(q[q.oil_bbl > 0].year.unique()); runs = []; 
    for y in ys:
        if runs and y == runs[-1][1] + 1: runs[-1][1] = y
        else: runs.append([y, y])
    return ", ".join(f"{a}-{b}" if a != b else f"{a}" for a, b in runs)
for e in lst: e["oil_years_in_monthly_records"] = yrs(p[p.well == e["well"]])
pre = {"TEC-2": "1956-1972 on 2331-2335 mSS (By Zone wellfile block, 38,155 bbl not in monthly records)", "TEC-6": "1956-1965 (By Zone wellfile block, 387,989 bbl not in monthly records)",
       "TEC-7": "1957 Jan-Mar test production, no data", "TEC-10": "Dec-2019 to Dec-2022 inside the commingled CAMPO TECO stream (TEC-10 sole origin in 2021 and Nov-2022 per CNH filings)",
       "TEC-2_": ""}
for e in lst: e["other_production_periods"] = pre.get(e["well"], "")
lst[1 if False else 0]["other_production_periods"] = pre["TEC-2"] + "; Dec-2019 to ~2020 inside the commingled CAMPO TECO stream (CNH 2020 filing names TEC-2 and TEC-10)"
q = p[p.well == "FIELD commingled (CAMPO TECO)"]
lst.append(dict(well="FIELD commingled (CAMPO TECO): TEC-10 + TEC-2", operator="Tonalli", produced_oil=True, first_oil_month_in_records=q[q.oil_bbl>0].month.min(), last_oil_month_in_records=q[q.oil_bbl>0].month.max(),
                years_with_oil_records=int(q[q.oil_bbl>0].year.nunique()), cum_oil_bbl_monthly_records=round(q.oil_bbl.sum(),0), cum_water_bbl_monthly_records=np.nan, cum_gas_mcf_monthly_records=np.nan,
                by_zone_allocation_total_bbl=np.nan, by_zone_periods="", source=f"{SRC} source_kind=tonalli_trucking_sales well=FIELD", oil_years_in_monthly_records=yrs(q), other_production_periods="no per-well split in the database"))
q = p[p.well == "FIELD (no well split)"]
lst.append(dict(well="FIELD 1960-65 (no well split; TEC-6 and TEC-2)", operator="PEMEX", produced_oil=True, first_oil_month_in_records=q.month.min(), last_oil_month_in_records=q.month.max(),
                years_with_oil_records=int(q.year.nunique()), cum_oil_bbl_monthly_records=round(q.oil_bbl.sum(),0), cum_water_bbl_monthly_records=round(q.water_bbl.sum(),0), cum_gas_mcf_monthly_records=np.nan,
                by_zone_allocation_total_bbl=np.nan, by_zone_periods="", source=f"{SRC} source_kind=cnh_monthly_field_level", oil_years_in_monthly_records="1960-1965", other_production_periods="overlap with the TEC-6/TEC-2 wellfile blocks unknown (docs/04 s.2)"))
pw = pd.DataFrame(lst)
pw.to_csv(OUT + "producing_wells.csv", index=False)

# peak
fm = p[p.well != "FIELD (no well split)"].groupby("month").agg(oil=("oil_bbl", "sum")).reset_index()
fm_all = p.groupby("month").agg(oil=("oil_bbl", "sum")).reset_index()
nw = p[(p.oil_bbl > 0) & p.well.str.startswith("TEC")].groupby("month").well.apply(lambda s: ",".join(sorted(s))).rename("wells")
fm_all = fm_all.merge(nw, on="month", how="left")
fm_all["days"] = pd.to_datetime(fm_all.month + "-01").dt.days_in_month
fm_all["bpd"] = fm_all.oil / fm_all.days
pk = fm_all.loc[fm_all.oil.idxmax()]
print("PEAK month", pk.to_dict())
print(fm_all.sort_values("oil", ascending=False).head(8).to_string())
ann = fa[["year", "oil_field", "oil_producing_wells"]]
print(ann.sort_values("oil_field", ascending=False).head(6))
print(pw.to_string())
print("total recorded", p.oil_bbl.sum())
# max number of wells producing simultaneously
cnt = p[(p.oil_bbl > 0) & p.well.str.startswith("TEC")].groupby("month").well.nunique()
print("max simultaneous wells", cnt.max(), cnt[cnt == cnt.max()].index.min(), cnt[cnt == cnt.max()].index.max(), (cnt == cnt.max()).sum())
json.dump(dict(peak_month=pk.month, peak_month_oil_bbl=float(pk.oil), peak_bpd=float(pk.bpd), peak_wells=pk.wells,
               max_simultaneous=int(cnt.max())), open(OUT + "_peak.json", "w"), indent=1)
