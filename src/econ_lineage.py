"""Task 2: extract comparable parameters from every IFR Tecolutla economic model
(Aug 2020, nine Feb 2022 versions, Sept/Oct 2023) and build a diff matrix.

Usage: python src/econ_lineage.py
Outputs: data/processed/econ_lineage/<tag>_{header,wells,capital,results,profiles}.csv,
         data/processed/econ_lineage/diff_matrix.csv, models.csv
Values are the cached (last Excel-calculated) values; no recalculation is done here.
"""
from __future__ import annotations
import csv, glob, hashlib, json, os, re, sys, zipfile
from datetime import datetime, date
import openpyxl
import pandas as pd

OUT = "data/processed/econ_lineage"
os.makedirs(OUT, exist_ok=True)

MODELS = [  # tag, path, primary model sheet
    ("2020-08", "data/raw/tec12_drill/OLD/Economic Model (Tecolutla August 2020) - FOR TRANS PLAN (TEC-12 Drill Econ).xlsm", "Model"),
    ("2022-v1", "data/raw/appraisal_plan/Economic Model (Tecolutla Feb 2022).xlsm", "Model"),
    ("2022-v2", "data/raw/appraisal_plan/Economic Model (Tecolutla Feb 2022)2.xlsm", "Model"),
    ("2022-v3", "data/raw/appraisal_plan/Economic Model (Tecolutla Feb 2022)3.xlsm", "Model"),
    ("2022-v4", "data/raw/appraisal_plan/Economic Model (Tecolutla Feb 2022)4 (Tec12 & Tec13).xlsm", "Model"),
    ("2022-v5", "data/raw/appraisal_plan/Economic Model (Tecolutla Feb 2022)5 (HZ).xlsm", "Model"),
    ("2022-v6", "data/raw/development_plan/Economic Model (Tecolutla Feb 2022)6 (Tec12, 13, 14 & 15).xlsm", "Model"),
    ("2022-v7", "data/raw/development_plan/Economic Model (Tecolutla Feb 2022)7 (Tec12, 13, 14 & 15).xlsm", "Model"),
    ("2022-v8", "data/raw/development_plan/Economic Model (Tecolutla Feb 2022)8 (Tec14 HZ).xlsm", "Model"),
    ("2022-v9", "data/raw/development_plan/Economic Model (Tecolutla Feb 2022)9 (Tec14 HZ).xlsm", "Model"),
    ("2023-10", "data/raw/tec12_drill/2023-09-29 Tec-12 Economics.xlsm", "Model (Tec-10 & Tec-12)"),
]

RESULT_KEYS = [  # (col A label, col B label) -> short key
    (("Total Oil", "(bbl)"), "oil_bbl"),
    (("Total Sales Gas", "(mcf)"), "gas_mcf"),
    (("Total Water", "(bbl)"), "water_bbl"),
    (("Total Revenue", "(US$)"), "revenue"),
    (("Total Royalties", "(US$)"), "royalties"),
    (("Total Operating Costs", "(US$)"), "opex"),
    (("Operating Netback", "(US$)"), "netback"),
    (("Operating Netback", "check3"), "econ_life_yr"),
    (("Total Capital", "(US$)"), "capital"),
    (("Net Operating Income*", "(US$)"), "noi_btax"),
    (("Cumulative Net Operating Income*", "(US$)"), "payout_months"),
    (("Discounted Net Operating Income*", "(US$)"), "npv10_btax"),
    (("Tax", "(US$)"), "tax"),
    (("Net Operating Income (ATAX)", "(US$)"), "noi_atax"),
    (("Discounted Net Operating Income", "(US$)"), "npv10_atax"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def core_props(path):
    z = zipfile.ZipFile(path)
    out = {"created": None, "modified": None, "last_modified_by": None}
    if "docProps/core.xml" in z.namelist():
        x = z.read("docProps/core.xml").decode()
        for k, pat in [("created", r"created[^>]*>([^<]+)"), ("modified", r"modified[^>]*>([^<]+)"), ("last_modified_by", r"lastModifiedBy>([^<]+)")]:
            m = re.search(pat, x)
            out[k] = m.group(1) if m else None
    return out


def s(v):
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    return v


def extract(tag, path, model_sheet):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[model_sheet]
    rows = list(ws.iter_rows(min_row=1, max_row=ws.max_row or 700, max_col=440, values_only=True))
    wb.close()

    def cell(r, c):  # 1-based
        try:
            return rows[r - 1][c - 1]
        except IndexError:
            return None

    # --- header block A1:L22 as label->value pairs ------------------------------------
    header = []
    for r in range(1, 23):
        for c in range(1, 12):
            lab = cell(r, c)
            if isinstance(lab, str) and lab.strip() and not lab.startswith("<") and not lab.startswith("*"):
                val = cell(r, c + 1)
                if val is not None and not (isinstance(val, str) and val.startswith("<")):
                    header.append({"tag": tag, "row": r, "col": c, "label": lab.strip(), "value": s(val),
                                   "value2": s(cell(r, c + 2)) if not isinstance(cell(r, c + 2), str) else None})
    # --- well table ---------------------------------------------------------------------
    wells = []
    for r in range(25, 46):
        if cell(r, 2) == "Oil" and cell(r, 3):
            wells.append({"tag": tag, "slot": cell(r, 1), "well": cell(r, 3), "forecast_start": s(cell(r, 5)),
                          "cos": cell(r, 7), "qi_bpd": cell(r, 9), "qi_adj_bpd": cell(r, 10), "n_b": cell(r, 11), "di_per_yr": cell(r, 12)})
    # --- date row and price row ----------------------------------------------------------
    date_row = next(r for r in range(60, 80) if isinstance(cell(r, 11), (datetime, date)) and isinstance(cell(r, 12), (datetime, date)))
    dates = [s(cell(date_row, c)) for c in range(11, 440)]
    price_row = next((r for r in range(400, 440) if cell(r, 1) == "Oil" and cell(r, 2) == "(US$/bbl)" and cell(r, 3) == "LLS"), None)
    fp_row = next((r for r in range(400, 440) if isinstance(cell(r, 1), str) and cell(r, 1).startswith("Oil Field Price")), None)
    prices = {"tag": tag, "price_row": price_row, "price_deck_note": cell(price_row, 4) if price_row else None,
              "field_price_row": fp_row, "field_price_note": cell(fp_row, 3) if fp_row else None,
              "field_price_factor": cell(fp_row, 4) if fp_row else None}
    for c in (11, 23, 35, 47, 59, 71, 131):  # month 1 and the same month in years 2..6 and 11
        prices[f"wti_m{c-10}"] = cell(price_row, c) if price_row else None
        prices[f"field_m{c-10}"] = cell(fp_row, c) if fp_row else None
    prices["first_month"] = dates[0]
    # --- capital table ------------------------------------------------------------------
    cap_hdr = next((r for r in range(480, 600) if cell(r, 3) == "Description" or cell(r, 2) == "Description"), None)
    capital = []
    if cap_hdr:
        hdr = [cell(cap_hdr, c) for c in range(1, 12)]
        r = cap_hdr + 1
        while r < cap_hdr + 80 and not (isinstance(cell(r, 1), str) and cell(r, 1).startswith("Total Type")):
            desc = cell(r, 3) if cell(cap_hdr, 3) == "Description" else cell(r, 2)
            if desc:
                rec = {"tag": tag, "row": r, "type": cell(r, 2) if cell(cap_hdr, 3) == "Description" else None, "description": desc}
                for c in range(4, 12):
                    h = hdr[c - 1]
                    if h:
                        rec[str(h).strip()] = s(cell(r, c))
                # monthly sum within the model window
                rec["sum_in_model"] = sum(v for v in rows[r - 1][10:440] if isinstance(v, (int, float)))
                capital.append(rec)
            r += 1
    # --- results ------------------------------------------------------------------------
    results = {"tag": tag}
    for (a, b), key in RESULT_KEYS:
        r = next((r for r in range(380, 620) if cell(r, 1) == a and cell(r, 2) == b), None)
        if r:
            results[key + "_econ"] = cell(r, 9)
            results[key + "_total"] = cell(r, 10)
            results[key + "_row"] = r
    irr_row = results.get("noi_btax_row")
    if irr_row:
        results["irr_btax"] = cell(irr_row, 9)
    if results.get("noi_atax_row"):
        results["irr_atax"] = cell(results["noi_atax_row"], 9)
    results["date_row"] = date_row
    results["first_month"] = dates[0]
    results["last_month"] = next(d for d in reversed(dates) if d)
    # per-slot oil volumes: slot k oil row = 83 + 8*(k-1), water = +5; econ flag from the check3 row
    flag_r = results.get("econ_life_yr_row")
    flag = [v if isinstance(v, (int, float)) else 0 for v in rows[flag_r - 1][10:440]] if flag_r else [1] * 430
    for k in range(1, 9):
        r = 83 + 8 * (k - 1)
        oil = [v if isinstance(v, (int, float)) and v < 50000 else 0 for v in rows[r - 1][10:440]]
        results[f"slot{k}_oil_total_bbl"] = round(sum(o * 30.42 for o in oil))
        results[f"slot{k}_oil_econ_bbl"] = round(sum(o * 30.42 * f for o, f in zip(oil, flag)))
        results[f"slot{k}_ip_bpd"] = next((o for o in oil if o > 0), 0)
    results["capital_in_window_usd"] = sum(c["sum_in_model"] for c in capital)
    results["capital_lines_in_window"] = "; ".join(f"{c['description'].splitlines()[0]} {c['sum_in_model']:.0f}" for c in capital if c["sum_in_model"])
    results["capital_lines_dated_before_window"] = "; ".join(
        f"{c['description'].splitlines()[0]} {c['total']:.0f} @{c.get('Start Timing')}" for c in capital
        if not c["sum_in_model"] and c.get("total") and isinstance(c.get("Start Timing"), str) and c["Start Timing"] >= "2020-01-01")
    return header, wells, prices, capital, results


def profiles(tag, path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    if "Model Production Profiles" not in wb.sheetnames:
        return []
    ws = wb["Model Production Profiles"]
    rows = list(ws.iter_rows(min_row=1, max_row=800, max_col=40, values_only=True))
    wb.close()
    hdr_r = next((i for i, r in enumerate(rows) if r and r[0] == "Econ Model Date"), None)
    if hdr_r is None:
        return []
    hdr = rows[hdr_r]
    out = []
    data = [r for r in rows[hdr_r + 1:] if r and isinstance(r[0], (datetime, date))]
    for c, h in enumerate(hdr):
        if isinstance(h, str) and ": Oil" in h:
            vals = [(r[0], r[c]) for r in data if isinstance(r[c], (int, float))]
            nz = [(d, v) for d, v in vals if v and v > 0]
            cum = sum(v * 30.42 for d, v in vals)
            out.append({"tag": tag, "series": h, "updated": s(rows[0][1]) if rows[0][0] and "UPDATED" in str(rows[0][0]) else None,
                        "first_nonzero_month": s(nz[0][0]) if nz else None, "ip_bpd": nz[0][1] if nz else 0,
                        "months_nonzero": len(nz), "cum_bbl_30p42": cum, "rate_m12": nz[11][1] if len(nz) > 11 else None,
                        "rate_m36": nz[35][1] if len(nz) > 35 else None})
    return out


def main():
    models, H, W, P, C, R, PR = [], [], [], [], [], [], []
    for tag, path, sheet in MODELS:
        cp = core_props(path)
        wb = openpyxl.load_workbook(path, read_only=True)
        sheets = wb.sheetnames
        wb.close()
        models.append({"tag": tag, "file": os.path.basename(path), "dir": os.path.dirname(path).replace("data/raw/", ""),
                       "size_bytes": os.path.getsize(path), "sha256": sha256(path), "model_sheet": sheet, "sheets": "|".join(sheets), **cp})
        h, w, p, c, r = extract(tag, path, sheet)
        wo = openpyxl.load_workbook(path, read_only=True, data_only=True)
        orow = [row for row in wo["outputs"].iter_rows(min_row=12, max_row=20, max_col=8, values_only=True) if row[0] == "Active"]
        wo.close()
        if orow:
            for name, val in zip(["oil_mbbl", "gas_mmcf", "ngl_cond_mbbl", "res_mboe", "npv10_musd", "ror", "capital_musd"], orow[0][1:8]):
                r[f"outputs_active_{name}"] = val
        H += h; W += w; P.append(p); C += c; R.append(r); PR += profiles(tag, path)
        print(tag, "ok", len(h), "header cells", len(w), "wells", len(c), "capital lines")
    pd.DataFrame(models).to_csv(f"{OUT}/models.csv", index=False)
    pd.DataFrame(H).to_csv(f"{OUT}/header_cells.csv", index=False)
    pd.DataFrame(W).to_csv(f"{OUT}/wells.csv", index=False)
    pd.DataFrame(P).to_csv(f"{OUT}/prices.csv", index=False)
    pd.DataFrame(C).to_csv(f"{OUT}/capital.csv", index=False)
    pd.DataFrame(R).to_csv(f"{OUT}/results.csv", index=False)
    pd.DataFrame(PR).to_csv(f"{OUT}/profiles.csv", index=False)
    # diff matrix on header labels (label -> value per tag)
    hd = pd.DataFrame(H)
    hd["key"] = hd["label"].str.replace(r"\s+", " ", regex=True)
    mat = hd.pivot_table(index="key", columns="tag", values="value", aggfunc="first")
    mat = mat[[m[0] for m in MODELS]]
    mat["n_distinct"] = mat.apply(lambda r: r.dropna().astype(str).nunique(), axis=1)
    mat.to_csv(f"{OUT}/diff_matrix_header.csv")
    print(mat[mat.n_distinct > 1].to_string())


if __name__ == "__main__":
    main()
