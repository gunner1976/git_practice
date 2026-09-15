"""Parse the Weatherford daily testing reports for TEC-10 (29 Jun - 6 Aug 2018).

Source: data/processed/drive_text/201807_Tecolutla-10_Welltest_Data.xlsx.txt, the
Drive-connector text rendering of `201807 Tecolutla-10 Welltest Data.xlsx`
(Drive id 1xVMk3sM2k8bP6SJ37SXxNvnGv-DcYChA, 9,594,784 bytes). The workbook is
one sheet per day ("REPORTE DIARIO DE LECTURAS, CALCULOS Y ACTIVIDADES TESTING");
the rendering is a single line with cells comma-separated and rows separated by a
space before a leading comma. Hourly rows carry: choke, WHP, gas rate, GOR (RGA),
liquid rate, BSW, oil rate, cumulative oil, API, water rate, salinity.

Outputs:
  data/processed/welltest/tec10_welltest_2018_hourly.csv
  data/processed/welltest/tec10_welltest_2018_daily.csv
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/processed/drive_text/201807_Tecolutla-10_Welltest_Data.xlsx.txt"
OUT = ROOT / "data/processed/welltest"

COLS = {  # index in the comma-split row -> name (header row of the form)
    1: "hora", 2: "choke_in", 3: "whp_psig", 4: "wht_degF", 5: "p_choke_psig", 6: "t_choke_degF",
    7: "p_abs_psia", 8: "dp_inH2O", 9: "t_gas_degF", 10: "orifice_in", 11: "gas_sg",
    12: "gas_mmscfd", 13: "gor_scf_bbl", 14: "liq_bbl_h", 15: "liq_cum_bbl", 16: "bsw_pct",
    17: "oil_sg", 18: "oil_bbl_h", 19: "oil_bopd", 20: "oil_cum_bbl", 21: "t_oil_degF",
    22: "api", 23: "wat_bbl_h", 24: "wat_bwpd", 25: "wat_cum_bbl", 26: "ph", 27: "salinity_ppm",
}
NUM = re.compile(r"^-?\d+(\.\d+)?$")


def num(s: str):
    s = s.strip().replace('"', "")
    if NUM.match(s):
        return float(s)
    return None


def main():
    text = SRC.read_text()
    rows = re.split(r" (?=,)", text)
    date = None
    recs = []
    for r in rows:
        m = re.search(r"Fecha:,+(\d{2}/\d{2}/\d{4})", r)
        if m:
            date = m.group(1)
            continue
        c = r.split(",")
        if len(c) < 26 or date is None or not re.match(r"^\d{1,2}:00$", c[1].strip()):
            continue
        rec = {"date": pd.to_datetime(date, format="%d/%m/%Y"), "hora": c[1].strip()}
        vals = {name: num(c[i]) for i, name in COLS.items() if i > 1 and i < len(c)}
        if all(v is None for v in vals.values()):
            continue
        rec.update(vals)
        rec["choke_in"] = c[2].strip()
        recs.append(rec)
    df = pd.DataFrame(recs)
    df["hour"] = df["hora"].str.split(":").str[0].astype(int)
    df = df.sort_values(["date", "hour"]).reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "tec10_welltest_2018_hourly.csv", index=False)

    flow = df[df["oil_bopd"].notna() & (df["oil_bopd"] > 0)]
    daily = flow.groupby("date").agg(
        hours_flowing=("hour", "count"),
        oil_bopd_mean=("oil_bopd", "mean"),
        oil_bbl_h_sum=("oil_bbl_h", "sum"),
        oil_cum_bbl_max=("oil_cum_bbl", "max"),
        wat_bwpd_mean=("wat_bwpd", "mean"),
        bsw_pct_mean=("bsw_pct", "mean"),
        gas_mmscfd_mean=("gas_mmscfd", "mean"),
        gor_scf_bbl_mean=("gor_scf_bbl", "mean"),
        gor_scf_bbl_median=("gor_scf_bbl", "median"),
        api_mean=("api", "mean"),
        whp_psig_mean=("whp_psig", "mean"),
        choke=("choke_in", lambda s: "/".join(sorted(set(x for x in s if x)))),
    ).reset_index()
    daily.to_csv(OUT / "tec10_welltest_2018_daily.csv", index=False)
    pd.set_option("display.width", 250)
    print(len(df), "hourly rows;", len(flow), "flowing rows")
    print(daily.round(1).to_string())
    g = flow[flow["gor_scf_bbl"].notna() & (flow["gor_scf_bbl"] > 0)]
    print("GOR: n", len(g), "median", g["gor_scf_bbl"].median(), "p10/p90",
          g["gor_scf_bbl"].quantile([0.1, 0.9]).round(0).tolist())
    print("oil-weighted GOR:", (g["gas_mmscfd"] * 1e6).sum() / g["oil_bopd"].sum() if g["oil_bopd"].sum() else None)
    a = flow[flow["api"].notna() & (flow["api"] > 0)]
    print("API: n", len(a), "median", a["api"].median(), "range", a["api"].min(), a["api"].max())
    print("total oil (max cum):", df["oil_cum_bbl"].max())


if __name__ == "__main__":
    main()
