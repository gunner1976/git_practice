"""opex_monthly.csv, opex_annual.csv, opex_breakdown.json. Every number transcribed from a repo file named in its source field."""
import pandas as pd, numpy as np, json
REPO = "/home/user/git_practice/"
OUT = "data/processed/presentation/"
PROD = "data/processed/tecolutla_production.csv"
CNHF = "data/processed/cnh/cnh_production_filings_2020_2022.csv"
APPX = "data/processed/deck_notes/accounting_notes.md Appendix A (TONALLI BUDGET Actual 2019 Forecast 2020 > Monthly Summary, row 'Operating Costs', USD cash basis)"
ACCF = "data/processed/database_review/acc_findings.md s.1-2"
ACCR = "data/processed/database_review/acc_review.csv"

d = pd.read_csv(REPO + PROD); d["month"] = d.date.str[:7]
cnh = pd.read_csv(REPO + CNHF).drop_duplicates("month", keep="first").set_index("month")

months = pd.period_range("2018-07", "2025-12", freq="M").astype(str)
rows = []
# monthly opex Sep-18..Dec-19 (Appendix A) and sales bbl (same sheet)
appx_opex = dict(zip(["2018-09", "2018-10", "2018-11", "2018-12", "2019-01", "2019-02", "2019-03", "2019-04", "2019-05", "2019-06", "2019-07", "2019-08", "2019-09", "2019-10", "2019-11", "2019-12"],
                     [67530, 80000, 72000, 68604, 68145, 59365, 62812, 53596, 69117, 83409, 81906, 80736, 73034, 61291, 70097, 75544]))
appx_sales = dict(zip(list(appx_opex), [1719.93, 5053.92, 4440.82, 4200.00, 3924.90, 2291.93, 1810.17, 2199.88, 2400.00, 3756.77, 4136.05, 2819.27, 2588.48, 2300.48, 2140.65, 2378.84]))
los22 = {"2022-01": 920.78, "2022-02": 183.03, "2022-03": 0, "2022-04": 0, "2022-05": 0, "2022-06": 0, "2022-07": 0, "2022-08": 0, "2022-09": 0, "2022-10": 0, "2022-11": 919.12, "2022-12": 733.09}
# annual LOS totals for the period-average column (not a monthly actual)
annual = {2018: (291365, 4, "LOS 2018 TEC-10 statement (Sep-Dec), Drive 1yElwLBJ, via acc_findings.md s.1"),
          2019: (839052, 12, "LOS 2019 Total Company, Drive 1FCUF9Pp, via acc_findings.md s.1"),
          2020: (336244, 12, "LOS 2020, Drive 1MUDIBfZ, via acc_findings.md s.1 / acc_review.csv"),
          2021: (349282, 12, "LOS 2021 final (2022 workbook), Drive 1l_gSKHt, via acc_findings.md s.1"),
          2022: (168283, 12, "LOS 2022, Drive 1l_gSKHt, via acc_findings.md s.1"),
          2023: (627273, 12, "LOS 2023 summary sheet, Drive 1Co9-h-R, via acc_findings.md s.1 (no split)"),
          2024: (289000, 12, "Tonalli P&L 2024 (Drive 1QOiCRJv/1kPVuMAR) via data/processed/database_review/res_findings.md item 5 ('USD 289 k')"),
          2025: (248000, 12, "Tonalli P&L 2025 via res_findings.md item 5 ('USD 248 k')")}

for m in months:
    y = int(m[:4]); r = dict(month=m)
    tm = d[(d.month == m) & (d.source_kind == "tonalli_trucking_sales")]
    st = d[(d.month == m) & (d.source_kind == "pemex_statement_sales")]
    ds = d[(d.month == m) & (d.source_kind == "tonalli_daily_sum")]
    r["oil_sales_pemex_statement_bbl"] = st.oil_bbl.sum() if len(st) else np.nan
    r["oil_trucking_tickets_bbl"] = tm.oil_bbl.sum() if len(tm) else np.nan
    r["oil_tec10_wellhead_daily_bbl"] = ds.oil_bbl.sum() if len(ds) else np.nan
    # chosen oil: PEMEX statement (invoiced) where present, else trucking tickets (all wells + commingled)
    if len(st): r["oil_bbl"], r["oil_source"] = st.oil_bbl.sum(), f"{PROD} source_kind=pemex_statement_sales"
    elif m == "2022-12": r["oil_bbl"], r["oil_source"] = 733.09, f"{ACCR} row 1l_gSKHt (LOS 2022: Dec sales 733.09 bbl); trucking row for Dec-2022 books 0 PEMEX-measured oil although 740 bbl were shipped"
    elif len(tm): r["oil_bbl"], r["oil_source"] = tm.oil_bbl.sum(), f"{PROD} source_kind=tonalli_trucking_sales (sum of all trucking rows)"
    elif m in cnh.index: r["oil_bbl"], r["oil_source"] = cnh.loc[m, "oil_bbl"], f"{CNHF} (filed production; no sales that month)"
    elif m in los22: r["oil_bbl"], r["oil_source"] = los22[m], f"{ACCR} row 1l_gSKHt (LOS 2022 monthly sales = 0; field shut in)"
    else: r["oil_bbl"], r["oil_source"] = np.nan, ("no record (shut in Apr-Jun 2020, CNH filing reports 0)" if m in ("2020-04", "2020-05", "2020-06") else "no record")
    # water hauled by truck (cost driver until TEC-7 disposal, Aug-2019)
    r["water_trucked_bbl"] = tm.water_bbl.sum() if len(tm) else np.nan
    # produced water, best available
    if m <= "2018-08" and len(tm):
        r["water_bbl"], r["water_source"] = tm[tm.well == "TEC-10"].water_bbl.sum(), f"{PROD} tonalli_trucking_sales TEC-10 test water"
    elif "2018-09" <= m <= "2019-11":
        t2 = tm[tm.well == "TEC-2"].water_bbl.sum() if len(tm[tm.well == "TEC-2"]) else 0.0
        r["water_bbl"] = (ds.water_bbl.sum() if len(ds) else 0.0) + t2
        r["water_source"] = f"{PROD} tonalli_daily_sum TEC-10 wellhead water" + (" + tonalli_trucking_sales TEC-2 water" if t2 else "")
    elif m in cnh.index:
        r["water_bbl"], r["water_source"] = cnh.loc[m, "water_bbl"], f"{CNHF} ({cnh.loc[m, 'source'][:60]}...)"
    else:
        r["water_bbl"], r["water_source"] = np.nan, "no record"
    r["gas_mcf"] = ds.gas_mcf.sum() if len(ds) else (cnh.loc[m, "gas_mmcf"] * 1000 if m in cnh.index else np.nan)
    r["gas_source"] = f"{PROD} tonalli_daily_sum (TEC-10)" if len(ds) else (f"{CNHF} gas_mmcf x 1000" if m in cnh.index else "")
    r["sales_bbl_accounting"] = appx_sales.get(m, los22.get(m, np.nan))
    r["sales_source"] = APPX.replace("'Operating Costs'", "'Total Sales Volumes (BBL)'") if m in appx_sales else (f"{ACCR} row 1l_gSKHt (LOS 2022 monthly oil sales)" if m in los22 else "")
    r["opex_usd"] = appx_opex.get(m, 0.0 if m in ("2018-07", "2018-08") else np.nan)
    r["opex_source"] = APPX if m in appx_opex else (APPX + ": '-' (nil) before first sales; test costs sat in capital" if m in ("2018-07", "2018-08") else "")
    if y in annual and m not in appx_opex and m not in ("2018-07", "2018-08"):
        tot, n, src = annual[y]
        r["opex_period_avg_usd_per_month"] = round(tot / n, 0)
        r["opex_period_avg_note"] = f"NOT a monthly actual: {y} annual total {tot:,} / {n} months ({src})"
    else:
        r["opex_period_avg_usd_per_month"] = np.nan; r["opex_period_avg_note"] = ""
    r["currency"] = "USD (as booked; no conversion)"
    rows.append(r)
mo = pd.DataFrame(rows)
mo.to_csv(OUT + "opex_monthly.csv", index=False, float_format="%.1f")
print(mo[["month", "oil_bbl", "water_bbl", "opex_usd", "opex_period_avg_usd_per_month"]].to_string())
print("2019 monthly sum", sum(v for k, v in appx_opex.items() if k.startswith("2019")), "2018", sum(v for k, v in appx_opex.items() if k.startswith("2018")))

# annual by category (grouped), with raw lines
lines = [  # (year, line as in source, usd, group)
    (2018, "Separator rental (SIPOMEGA three-phase)", 89334, "Separator rental"), (2018, "Sampling and measurement", 46733, "Sampling & lab"),
    (2018, "Trucking emulsion", 36365, "Oil trucking"), (2018, "Trucking water", 30719, "Water trucking & disposal"),
    (2018, "Site engineers (PIURZA, 2 supervisors)", 33732, "Supervision & crew"), (2018, "Tanks", 26295, "Tanks"),
    (2018, "Transfer pump", 20562, "Other"), (2018, "ASSA housing", 3474, "Other"), (2018, "SSQ chemicals", 4150, "Inj. pump, chemicals & stims"),
    (2019, "Separator", 186456, "Separator rental"), (2019, "Site engineers", 173474, "Supervision & crew"), (2019, "Tanks", 112290, "Tanks"),
    (2019, "Trucking emulsion", 91583, "Oil trucking"), (2019, "Water trucking", 83944, "Water trucking & disposal"),
    (2019, "Water disposal fee 1.33 USD/bbl (Feb-Aug)", 32534, "Water trucking & disposal"), (2019, "Sampling", 36139, "Sampling & lab"),
    (2019, "Chem/stim", 46952, "Inj. pump, chemicals & stims"), (2019, "Rental equipment for water-injection well (Aug-Dec)", 75680, "Inj. pump, chemicals & stims"),
    (2020, "Trucking", 67891, "Oil trucking"), (2020, "Sampling", 20715, "Sampling & lab"), (2020, "Separator rental (Jan-Mar only)", 22494, "Separator rental"),
    (2020, "Tanks", 54199, "Tanks"), (2020, "Field supervision", 109287, "Supervision & crew"), (2020, "Demulsifier", 7400, "Inj. pump, chemicals & stims"),
    (2020, "Injection pump diesel (Dec)", 3255, "Inj. pump, chemicals & stims"), (2020, "Injection pump rental (Jan-Mar)", 46778, "Inj. pump, chemicals & stims"),
    (2020, "Stimulation (Dec)", 4225, "Inj. pump, chemicals & stims"),
    (2021, "Trucking", 102720, "Oil trucking"), (2021, "Sampling", 25624, "Sampling & lab"), (2021, "Tanks", 24639, "Tanks"),
    (2021, "Field supervision", 159745, "Supervision & crew"), (2021, "Demulsifier", 7400, "Inj. pump, chemicals & stims"),
    (2021, "Injection pump and stims", 29154, "Inj. pump, chemicals & stims"),
    (2022, "Trucking", 39573, "Oil trucking"), (2022, "Sampling", 10241, "Sampling & lab"), (2022, "Tanks", 25582, "Tanks"),
    (2022, "Field supervision", 68172, "Supervision & crew"), (2022, "Injection pump (Sep)", 4713, "Inj. pump, chemicals & stims"),
    (2022, "Stimulation (Nov)", 20003, "Inj. pump, chemicals & stims")]
srcmap = {2018: f"{ACCR} row 1yElwLBJ (Tonalli Operations Statement - TEC 10 2018.xlsx)", 2019: f"{ACCR} row 1FCUF9Pp (Tonalli 2019 Operations Statements, Total Company)",
          2020: f"{ACCR} row 1MUDIBfZ (Tecolutla 2020 Lease Operations Statements.xlsx)", 2021: f"{ACCR} row 1l_gSKHt (final 2021 sheet in the Dec-2022 LOS workbook)",
          2022: f"{ACCR} row 1l_gSKHt (Tonalli Operations Statements Dec 31 2022.xlsx)"}
L = pd.DataFrame(lines, columns=["year", "line_item_as_in_source", "usd", "group"]); L["source"] = L.year.map(srcmap)
L.to_csv(OUT + "opex_annual_lines.csv", index=False)
groups = ["Separator rental", "Supervision & crew", "Tanks", "Oil trucking", "Water trucking & disposal", "Inj. pump, chemicals & stims", "Sampling & lab", "Other"]
fin = {2018: (15209, 917237, 382127, 243745, 19.16, "Sep-Dec only (first sales Sep-2018)"), 2019: (32702, 1731700, 706221, 186428, 25.66, ""),
       2020: (19041, 681883, 283429, 62210, 17.66, "no sales Apr-Jun (COVID shut-in)"), 2021: (17546, 939437, 393544, 196611, 19.91, ""),
       2022: (2756, 177705, 88773, -79350, 61.06, "field shut in Mar-Oct; restarted Nov after USD 20 k stimulation"),
       2023: (530, 30387, 16945, -613831, 1183.53, "one producing month (Jan); care and maintenance; no category split"),
       2024: (0, np.nan, np.nan, np.nan, np.nan, "no sales; holding cost (Tonalli P&L)"), 2025: (0, np.nan, np.nan, np.nan, np.nan, "no sales; holding cost (Tonalli P&L)")}
ar = []
for y in range(2018, 2026):
    tot, n, src = annual[y]; sb, rev, rtf, nb, perbbl, note = fin[y]
    row = dict(year=y, months_in_period=n, sales_bbl=sb, revenue_usd=rev, royalties_taxes_fees_usd=rtf, field_netback_usd=nb, opex_usd=tot, opex_usd_per_bbl=perbbl,
               opex_avg_usd_per_month=round(tot / n, 0))
    for g in groups:
        row[g] = int(L[(L.year == y) & (L.group == g)].usd.sum()) if y <= 2022 else np.nan
    row["categories_sum_usd"] = int(L[L.year == y].usd.sum()) if y <= 2022 else np.nan
    row["note"] = note; row["source_totals"] = src if y >= 2024 else f"{ACCF} table 'Year | Sales bbl | ... | Field opex' ({src})"
    row["source_categories"] = srcmap.get(y, "no split in source")
    row["currency"] = "USD"
    ar.append(row)
A = pd.DataFrame(ar); A.to_csv(OUT + "opex_annual.csv", index=False)
print(A[["year", "opex_usd", "categories_sum_usd", "opex_avg_usd_per_month"] + groups].to_string())
