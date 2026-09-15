"""Parse the Weatherford slickline report for TEC-2 (May 2018): the 30-May static
gradient stations and the 10-30 May gauge time series (flowing + build-up).

Source: data/processed/drive_text/REPORT_TECOLUTLA_2.xlsx.txt, the Drive-connector
text rendering of `REPORT TECOLUTLA 2.xlsx` (Drive id 1EdJ8tOM5QEtOPUHjPHucg_7Exj8G3v9k,
9,968,484 bytes). Perforated interval 2307-2311 m; gauges 78446 and 79284.

Outputs (data/processed/pressure/tec2_2018/):
  stations_2018-05-30.csv   MD, TVD, psi, kg/cm2, gradient kg/cm2/m, temp
  gauge_series.csv          line, datetime, minutes, psi, degC
  summary.json
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/processed/drive_text/REPORT_TECOLUTLA_2.xlsx.txt"
OUT = ROOT / "data/processed/pressure/tec2_2018"
PSI_KPA = 6.894757
KGCM2_KPA = 98.0665


def main():
    text = SRC.read_text()
    rows = re.split(r" (?=,)", text)
    OUT.mkdir(parents=True, exist_ok=True)

    # --- station table: cells after "(Kg/cm2),,,,,,, " pattern: MD,TVD,psi,kg/cm2,grad,degC,degF,WHPpsi,WHPkg
    st_row = next(r for r in rows if "CÁLCULO PROFUNDIDAD VERTICAL" in r)
    cells = [c.strip() for c in st_row.split(",")]
    recs = []
    i = 0
    while i < len(cells) - 8:
        if re.match(r"^\d+(\.\d+)?$", cells[i]) and re.match(r"^\d+(\.\d+)?$", cells[i + 1]) and re.match(r"^\d+(\.\d+)?$", cells[i + 2]):
            try:
                recs.append({
                    "md_m": float(cells[i]), "tvd_m": float(cells[i + 1]), "p_psi": float(cells[i + 2]),
                    "p_kgcm2": float(cells[i + 3]),
                    "grad_kgcm2_m": float(cells[i + 4]) if re.match(r"^[\d.]+$", cells[i + 4]) else None,
                    "t_degC": float(cells[i + 5]), "t_degF": float(cells[i + 6]),
                    "whp_psi": float(cells[i + 7]), "whp_kgcm2": float(cells[i + 8]),
                })
                i += 9
                continue
            except ValueError:
                pass
        i += 1
    st = pd.DataFrame(recs)
    st["p_kpa"] = st["p_psi"] * PSI_KPA
    st.to_csv(OUT / "stations_2018-05-30.csv", index=False)

    # --- gauge series
    g_row = next(r for r in rows if "Line No.,Date Time,Time,Pressure,Temperature" in r or "dd/mm/aaaa HH:mm:ss" in r)
    series = re.findall(r"(\d+),(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} [ap]\.m\.),(\d+),([-\d.]+),([-\d.]+),([-\d.]+)", text)
    gs = pd.DataFrame(series, columns=["line", "datetime", "minutes", "p_psi", "t_degC", "dp_psi"])
    for c in ["line", "minutes"]:
        gs[c] = gs[c].astype(int)
    for c in ["p_psi", "t_degC", "dp_psi"]:
        gs[c] = gs[c].astype(float)
    gs["datetime"] = pd.to_datetime(gs["datetime"].str.replace(" p.m.", " PM").str.replace(" a.m.", " AM"), format="%d/%m/%Y %I:%M:%S %p")
    gs = gs.drop_duplicates("line").sort_values("line").reset_index(drop=True)
    gs["p_kpa"] = gs["p_psi"] * PSI_KPA
    gs.to_csv(OUT / "gauge_series.csv", index=False)

    # header summary values
    m = re.search(r"Inicial,([\d.]+),,([\d.]+),([\d.]+),([\d.]+),+ Final,([\d.]+),,([\d.]+),([\d.]+),([\d.]+)", text)
    hdr = {}
    if m:
        hdr = {"initial_whp_psi": float(m.group(1)), "initial_wht_degC": float(m.group(2)),
               "initial_bhp_psi": float(m.group(3)), "initial_bht_degC": float(m.group(4)),
               "final_whp_psi": float(m.group(5)), "final_wht_degC": float(m.group(6)),
               "final_bhp_psi": float(m.group(7)), "final_bht_degC": float(m.group(8))}
    summ = {
        "source": "REPORT TECOLUTLA 2.xlsx (Weatherford slickline, unit SL-424, eng. Miguel Mar Santiago)",
        "perforations_m": "2307-2311",
        "kb_m_assumed": 3.8,
        "header": hdr,
        "gauge_series": {"n": int(len(gs)), "start": str(gs["datetime"].min()), "end": str(gs["datetime"].max()),
                         "p_max_psi": float(gs["p_psi"].max()), "p_max_kpa": float(gs["p_kpa"].max()),
                         "p_last_psi": float(gs["p_psi"].iloc[-1]), "t_last_degC": float(gs["t_degC"].iloc[-1])},
        "stations_2018_05_30": st.to_dict("records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summ, indent=2, default=str))
    pd.set_option("display.width", 200)
    print(st.to_string())
    print(gs.head(3).to_string()); print(gs.tail(3).to_string())
    print(json.dumps({k: v for k, v in summ.items() if k != "stations_2018_05_30"}, indent=1, default=str))
    # daily max pressure during the series
    d = gs.set_index("datetime")["p_psi"].resample("D").agg(["min", "max", "last"])
    print(d.to_string())


if __name__ == "__main__":
    main()
