"""Task 1 — parse `2023-09-29 Tec-12 Economics.xlsm`.

Reads cached values (openpyxl data_only=True) and formulas from the workbook,
extracts assumptions, price/fiscal terms, capital, opex, the production profile
and the outputs for both model sheets, and re-derives the key lines in pandas
as the recalculation cross-check (LibreOffice cannot load files in this
container — see docs/gaps.md G-16). Every output row carries a sheet!cell ref.

Outputs in data/processed/econ_2023/:
  assumptions.csv, capital_items.csv, annual_<case>.csv, monthly_<case>.parquet,
  tec12_profile_2020.csv, summary.json, crosscheck.csv
"""
import json, warnings, datetime as dt
from pathlib import Path
import numpy as np, pandas as pd, openpyxl
from openpyxl.utils import get_column_letter as L

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/raw/tec12_drill/2023-09-29 Tec-12 Economics.xlsm"
OUT = ROOT / "data/processed/econ_2023"; OUT.mkdir(parents=True, exist_ok=True)
wbv = openpyxl.load_workbook(SRC, data_only=True, keep_vba=True)
wbf = openpyxl.load_workbook(SRC, data_only=False, keep_vba=True)
CASES = {"tec10": "Model (Tec-10)", "tec10_tec12": "Model (Tec-10 & Tec-12)"}
FIRST_COL = 11  # column K = first month

def cell(ws, ref):  # value + formula
    return wbv[ws][ref].value, wbf[ws][ref].value

# ---------- 1. assumptions (input block, rows 1-21 of the combined model) ----------
M = CASES["tec10_tec12"]
A = [  # label, value cell, unit, note
    ("Evaluation start date", "B8", "date", ""), ("Economic start date", "B9", "date", ""),
    ("Depreciation rate", "B10", "fraction/yr", ""), ("Income tax rate", "B11", "fraction", ""),
    ("Inflation", "B12", "fraction", "0 => flat real pricing"), ("Discount rate", "B13", "fraction", ""),
    ("Contract duration", "B14", "years", ""),
    ("Oil offset (legacy)", "B16", "USD/bbl", "superseded by the 90% of WTI field-price factor in K428"),
    ("Gas offset", "B17", "USD/mmbtu", ""), ("Abandonment fund", "B21", "USD", ""),
    ("Block area", "B4", "km2", ""), ("API gravity (model)", "B5", "deg", "note in C5: set to 40 only so the price formula avoids a discount; true 28-30"),
    ("Bid round royalty", "E9", "fraction of revenue", ""), ("Surface land royalty", "H9", "fraction of revenue", ""),
    ("Community royalty", "H10", "fraction", ""), ("GORR", "H11", "fraction", ""),
    ("Battery fixed cost", "E15", "USD/month", ""), ("Oil well fixed cost", "E16", "USD/well/month", ""),
    ("Gas well fixed cost", "E17", "USD/well/month", ""), ("Disposal well fixed cost", "E18", "USD/month", ""),
    ("Block fee <=60 months", "E19", "peso/km2/month", ""), ("Block fee >60 months", "E20", "peso/km2/month", ""),
    ("Oil variable cost", "H15", "USD/bbl", "trucking/handling"), ("Water disposal", "H16", "USD/bbl", ""),
    ("Sales gas processing", "H17", "USD/mcf", ""), ("Extraction area share", "H21", "fraction of block", ""),
    ("WTI price (flat)", "K412", "USD/bbl", "row 412 'Oil (US$/bbl) LLS flat'"),
    ("Field price factor", "D428", "fraction of WTI", "PEMEX price at Ezequiel Ordonez"),
    ("Field price", "K428", "USD/bbl", "= WTI x factor"),
    ("Gas contractual price", "K414", "USD/mmbtu", ""),
    ("FX CAD/USD", "K74", "CAD per USD", "labelled 'Not Used'"), ("FX MXN/USD", "K75", "peso per USD", "block fees only"),
    ("Basic royalty A0 threshold", "E458", "USD/bbl", "Mexican basic royalty, oil"),
    ("Basic royalty B0 slope", "E459", "fraction per USD", ""),
    ("Basic oil royalty rate at model price", "K460", "fraction", "= B0 x price + 1.5%"),
    ("Economic life (check3)", "I505", "years", "months with positive trailing netback"),
    ("TEC-10 forecast start", "E26", "date", "well #2, chance of success G26"),
    ("TEC-12 forecast start", "E28", "date", "well #4 'Tecolutla 12 HZ', chance of success G28"),
    ("TEC-12 chance of success", "G28", "fraction", ""),
]
rows = []
for lab, ref, unit, note in A:
    val, frm = cell(M, ref)
    if isinstance(val, dt.datetime): val = val.date().isoformat()
    rows.append({"item": lab, "value": val, "unit": unit, "source": f"{M}!{ref}", "formula": frm if isinstance(frm, str) and frm.startswith("=") else "", "note": note})
pd.DataFrame(rows).to_csv(OUT / "assumptions.csv", index=False)

# ---------- 2. capital items ----------
cap = []
for r in range(509, 561):
    d = wbv[M][f"C{r}"].value; tot = wbv[M][f"F{r}"].value; t0 = wbv[M][f"G{r}"].value
    if d and tot not in (None, 0):
        cap.append({"row": r, "description": d, "group": wbv[M][f"D{r}"].value, "location": wbv[M][f"E{r}"].value,
                    "total_usd": tot, "start": t0.date().isoformat() if isinstance(t0, dt.datetime) else t0,
                    "in_2024_model": isinstance(t0, dt.datetime) and t0.year >= 2024, "source": f"{M}!C{r}:G{r}"})
pd.DataFrame(cap).to_csv(OUT / "capital_items.csv", index=False)

# ---------- 3. monthly & annual tables per case ----------
ROWS = {"date": 67, "year": 69, "days": 71, "discount": 73, "oil_bbl": 386, "water_bbl": 388, "wcut": 387,
        "field_price": 428, "revenue": 454, "roy_basic": 471, "roy_bid": 478, "roy_surface": 480, "roy_hc_tax": 482,
        "royalties": 483, "opex_fixed": 493, "opex_var": 498, "opex": 500, "netback": 502, "econ_flag": 505,
        "capital": 571, "abandon": 573, "capital_total": 574, "noi_btax": 577, "noi_btax_adj": 578, "cum_noi": 579,
        "disc_noi": 580, "tax": 587, "noi_atax": 588, "disc_noi_atax": 590, "tec10_oil_bpd": 91, "tec10_wat_bpd": 96,
        "tec12_oil_bpd": 107, "tec12_wat_bpd": 112, "tec12_wells": 106, "tec10_wells": 90}
summary = {}
for key, sheet in CASES.items():
    ws = wbv[sheet]; last = ws.max_column
    data = {k: [ws.cell(r, c).value for c in range(FIRST_COL, last + 1)] for k, r in ROWS.items()}
    m = pd.DataFrame(data)
    m = m[m["date"].notna()].copy(); m["date"] = pd.to_datetime(m["date"])
    num = [c for c in m.columns if c != "date"]
    m[num] = m[num].apply(pd.to_numeric, errors="coerce")
    m.to_parquet(OUT / f"monthly_{key}.parquet", index=False)
    # cross-check: re-derive lines from primitives
    chk = pd.DataFrame({"date": m["date"]})
    chk["revenue_calc"] = m["oil_bbl"] * m["field_price"]
    chk["royalties_calc"] = m[["roy_basic", "roy_bid", "roy_surface", "roy_hc_tax"]].sum(axis=1)
    chk["opex_calc"] = m["opex_fixed"] + m["opex_var"]
    chk["netback_calc"] = chk["revenue_calc"] + chk["royalties_calc"] + chk["opex_calc"]
    chk["noi_calc"] = chk["netback_calc"] + m["capital_total"]
    econ = m["econ_flag"].fillna(0) > 0
    npv_calc = float((m["noi_btax"] * m["discount"])[econ].sum())
    a = (m.assign(econ=econ).groupby("year")
         .agg(days=("days", "sum"), oil_bbl=("oil_bbl", "sum"), water_bbl=("water_bbl", "sum"), revenue_usd=("revenue", "sum"),
              royalties_usd=("royalties", "sum"), opex_usd=("opex", "sum"), netback_usd=("netback", "sum"),
              capital_usd=("capital_total", "sum"), noi_btax_usd=("noi_btax", "sum"), tax_usd=("tax", "sum"),
              noi_atax_usd=("noi_atax", "sum"), disc_noi_btax_usd=("disc_noi", "sum"), econ_months=("econ", "sum"),
              tec10_oil_bpd=("tec10_oil_bpd", "mean"), tec12_oil_bpd=("tec12_oil_bpd", "mean")))
    a["oil_bpd"] = a["oil_bbl"] / a["days"]; a["wcut"] = a["water_bbl"] / (a["water_bbl"] + a["oil_bbl"])
    a["royalty_pct_rev"] = -a["royalties_usd"] / a["revenue_usd"]; a["opex_per_bbl"] = -a["opex_usd"] / a["oil_bbl"]
    a.reset_index().to_csv(OUT / f"annual_{key}.csv", index=False)
    I = lambda r: ws[f"I{r}"].value; J = lambda r: ws[f"J{r}"].value
    summary[key] = {
        "sheet": sheet, "econ_life_years": I(505), "oil_econ_bbl": I(403), "oil_total_bbl": J(403), "water_econ_bbl": I(409),
        "revenue_econ_usd": I(454), "royalties_econ_usd": I(483), "opex_econ_usd": I(500), "netback_econ_usd": I(502),
        "capital_total_usd": J(574), "noi_btax_adj_usd": J(578), "irr_btax": I(578), "payout_months": I(579), "npv10_btax_usd": J(580),
        "tax_usd": J(587), "noi_atax_usd": J(588), "irr_atax": I(588), "npv10_atax_usd": J(590),
        "tec10_oil_total_bbl": J(91), "tec12_oil_econ_bbl": I(107), "tec12_oil_total_bbl": J(107), "tec12_water_total_bbl": J(112),
        "crosscheck": {"npv10_btax_recalc_usd": npv_calc,
                       "revenue_max_abs_diff_usd": float((chk["revenue_calc"] - m["revenue"]).abs().max()),
                       "royalties_max_abs_diff_usd": float((chk["royalties_calc"] - m["royalties"]).abs().max()),
                       "opex_max_abs_diff_usd": float((chk["opex_calc"] - m["opex"]).abs().max()),
                       "netback_max_abs_diff_usd": float((chk["netback_calc"] - m["netback"]).abs().max()),
                       "noi_max_abs_diff_usd": float((chk["noi_calc"] - m["noi_btax"]).abs().max())}}
    chk.to_csv(OUT / f"crosscheck_{key}.csv", index=False)
# incremental TEC-12 = combined - Tec-10 only
c, b = summary["tec10_tec12"], summary["tec10"]
summary["tec12_incremental"] = {k: (c[k] - b[k]) for k in ("npv10_btax_usd", "npv10_atax_usd", "noi_btax_adj_usd", "oil_econ_bbl", "capital_total_usd")}
# ---------- 4. the 2020-vintage TEC-12 profile & case table (sheet 'Tec-12 (1)') ----------
t = wbv["Tec-12 (1)"]; last = t.max_column
dates = [t.cell(4, c).value for c in range(FIRST_COL, last + 1)]
prof = pd.DataFrame({"date": pd.to_datetime([d for d in dates if isinstance(d, dt.datetime)]),
                     "tec12_oil_bpd": [t.cell(21, c).value for c in range(FIRST_COL, last + 1) if isinstance(t.cell(4, c).value, dt.datetime)]})
prof["days"] = prof["date"].dt.days_in_month; prof["cum_bbl"] = (prof["tec12_oil_bpd"].fillna(0) * prof["days"]).cumsum()
prof.to_csv(OUT / "tec12_profile_2020.csv", index=False)
cases2020 = [{"case": t[f"A{r}"].value, "wti_usd_bbl": t[f"B{r}"].value, "ip_bpd": t[f"C{r}"].value, "reserves_bbl": t[f"D{r}"].value,
              "npv10_usd": t[f"E{r}"].value, "irr": t[f"F{r}"].value, "payout_months": t[f"G{r}"].value, "capex_mmusd": t["C15"].value,
              "source": f"Tec-12 (1)!A{r}:G{r}"} for r in range(31, 35)]
pd.DataFrame(cases2020).to_csv(OUT / "tec12_cases_2020.csv", index=False)
summary["tec12_2020_profile"] = {"first_month": str(prof.loc[prof.tec12_oil_bpd > 0, "date"].min().date()), "ip_bpd": float(prof.tec12_oil_bpd.max()),
                                 "cum_at_row_J21_bbl": t["J21"].value, "cum_to_end_of_sheet_bbl": float(prof.cum_bbl.iloc[-1]),
                                 "months_in_sheet": int((prof.tec12_oil_bpd > 0).sum())}
# ---------- 5. GLJ summary / volumetrics sheet ----------
g = wbv["Summary (GLJ)"]; gf = wbf["Summary (GLJ)"]
summary["volumetrics_sheet"] = {
    "field": {"area_km2": g["D6"].value, "area_formula": gf["D6"].value, "gross_m": g["D7"].value, "ntg": g["D8"].value, "phi": g["D10"].value, "sw": g["D11"].value, "bo": g["D12"].value, "ooip_mmbbl": g["D19"].value},
    "tec12_drainage": {"area_km2": g["I6"].value, "ntg": g["I8"].value, "net_pay_m": g["I9"].value, "phi": g["I10"].value, "sw": g["I11"].value, "ooip_mmbbl": g["I19"].value, "rf": g["I21"].value, "reserves_bbl": g["I22"].value, "target_reserves_bbl": g["I24"].value},
    "alt1": {"area_km2": g["P6"].value, "net_pay_m": g["P9"].value, "phi": g["P10"].value, "sw": g["P11"].value, "rf": g["P21"].value, "reserves_bbl": g["P22"].value},
    "alt2": {"area_km2": g["T6"].value, "net_pay_m": g["T9"].value, "phi": g["T10"].value, "sw": g["T11"].value, "rf": g["T21"].value, "reserves_bbl": g["T22"].value}}
o = wbv["OUTPUT"]
summary["output_sheet"] = {"updated": o["N7"].value, "cases": {"wti80": {"tec10_noi_per_month": o["O20"].value, "combined_noi_per_month": o["P20"].value, "royalty_share": o["P16"].value, "opex_per_bbl": o["P14"].value},
                                                                  "wti85": {"tec10_noi_per_month": o["S20"].value, "combined_noi_per_month": o["T20"].value, "royalty_share": o["T16"].value, "opex_per_bbl": o["T14"].value}}}
json.dump(summary, open(OUT / "summary.json", "w"), indent=2, default=str)
print(json.dumps(summary, indent=1, default=str))
