"""TEC-10 CMI fracture density and dip picks by depth zone (G-09).

Sources (data/raw/petrophysics/LAS and data/raw/geology/tec10_image_log, Weatherford, 2 May 2018):
  TECOLUTLA 10_CMI FRACTURE DENSITY_2487.00m-2280.5m_02MAY2018.las  (1-m counts and P10/P21/P32)
  TECOLUTLA 10_CMI IMAGE DIPS_2487.00m-2280.5m_02MAY2018.las         (individual dip picks with class)
  TECOLUTLA 10_CXD ANISOTROPIA_2487.00m-2280.5m_02MAY2018.las        (dipole sonic shear anisotropy)
Depths are mMD; mSS uses the survey-based offset from data/processed/petrophysics/TEC10_logs_mss.csv.

Outputs: data/processed/petrophysics/tec10_cmi_zones.csv, tec10_cmi_dips.csv, figures/14_cmi_fractures.png
"""
from __future__ import annotations
from pathlib import Path
import lasio
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
LAS = ROOT / "data/raw/petrophysics/LAS"
FD = LAS / "TECOLUTLA 10_CMI FRACTURE DENSITY_2487.00m-2280.5m_02MAY2018.las"
DIPS = ROOT / "data/raw/geology/tec10_image_log/TECOLUTLA 10_CMI IMAGE DIPS_2487.00m-2280.5m_02MAY2018.las"
ANI = LAS / "TECOLUTLA 10_CXD ANISOTROPIA_2487.00m-2280.5m_02MAY2018.las"
MSS = ROOT / "data/processed/petrophysics/TEC10_logs_mss.csv"
OUT = ROOT / "data/processed/petrophysics"
ZONES = [("above window", 2296, 2329), ("TEC-12 window", 2329, 2346), ("perforated", 2346, 2356),
         ("below perforations", 2356, 2400), ("deep El Abra", 2400, 2488)]


def main():
    fd = lasio.read(FD).df().reset_index()
    fd = fd.mask(fd == -9999)
    dips = lasio.read(DIPS).df().reset_index()
    for c in ["DEPTH", "AZIMUTH", "DIP_TRU"]:
        dips[c] = pd.to_numeric(dips[c], errors="coerce")
    ani = lasio.read(ANI).df().reset_index().rename(columns={"MD": "DEPTH"})
    ani = ani.mask(ani == -9999)
    mss = pd.read_csv(MSS)
    md_col = [c for c in mss.columns if c.lower() in ("dept", "depth", "md", "depth_mmd")][0]
    ss_col = [c for c in mss.columns if "mss" in c.lower() or "tvdss" in c.lower()][0]
    ss = np.interp(fd["DEPTH"], mss[md_col], mss[ss_col])
    fd["DEPTH_MSS"] = ss

    rows = []
    for name, a, b in ZONES:
        z = fd[(fd.DEPTH >= a) & (fd.DEPTH < b)]
        d = dips[(dips.DEPTH >= a) & (dips.DEPTH < b)]
        an = ani[(ani.DEPTH >= a) & (ani.DEPTH < b)]
        rows.append({
            "zone": name, "top_mmd": a, "base_mmd": b,
            "top_mss": round(float(np.interp(a, mss[md_col], mss[ss_col])), 1),
            "base_mss": round(float(np.interp(b, mss[md_col], mss[ss_col])), 1),
            "metres": len(z),
            "frac_conductive": int(z["FRACTURE__CONDUCTIVE_COUNT"].sum()),
            "frac_mixed": int(z["FRACTURE__MIXED_COUNT"].sum()),
            "frac_resistive": int(z["FRACTURE__RESISTIVE_COUNT"].sum()),
            "p10_sum_per_m": round(float(z["P10_SUM"].mean()), 3),
            "p32_sum_per_m": round(float(z["P32_SUM"].mean()), 3),
            "bedding_picks": int(d["TYPE"].str.startswith("Bedding").sum()),
            "bedding_dip_median_deg": round(float(d.loc[d["TYPE"].str.startswith("Bedding"), "DIP_TRU"].median()), 1) if (d["TYPE"].str.startswith("Bedding")).any() else None,
            "fracture_picks": int(d["TYPE"].str.startswith("Fracture").sum()),
            "fracture_dip_median_deg": round(float(d.loc[d["TYPE"].str.startswith("Fracture"), "DIP_TRU"].median()), 1) if (d["TYPE"].str.startswith("Fracture")).any() else None,
            "shear_anisotropy_pct_median": round(float(an["ANIS"].median()), 2) if len(an) else None,
        })
    zones = pd.DataFrame(rows)
    zones.to_csv(OUT / "tec10_cmi_zones.csv", index=False)
    dips["DEPTH_MSS"] = np.interp(dips["DEPTH"], mss[md_col], mss[ss_col])
    dips.to_csv(OUT / "tec10_cmi_dips.csv", index=False)
    pd.set_option("display.width", 250)
    print(zones.to_string())

    fig, axes = plt.subplots(1, 4, figsize=(12, 8), sharey=True)
    y = fd["DEPTH_MSS"]
    axes[0].barh(y, fd["FRACTURE__CONDUCTIVE_COUNT"].fillna(0), height=1, color="#1f77b4", label="conductive (open)")
    axes[0].barh(y, fd["FRACTURE__MIXED_COUNT"].fillna(0), left=fd["FRACTURE__CONDUCTIVE_COUNT"].fillna(0), height=1, color="#ff7f0e", label="mixed")
    axes[0].barh(y, fd["FRACTURE__RESISTIVE_COUNT"].fillna(0), left=(fd["FRACTURE__CONDUCTIVE_COUNT"].fillna(0) + fd["FRACTURE__MIXED_COUNT"].fillna(0)), height=1, color="#7f7f7f", label="resistive (cemented)")
    axes[0].set_xlabel("fractures per metre (count)"); axes[0].legend(fontsize=7, loc="lower right")
    axes[1].plot(fd["P32_SUM"], y, color="#2ca02c"); axes[1].set_xlabel("P32 fracture intensity, 1/m")
    bed = dips[dips["TYPE"].str.startswith("Bedding")]
    frc = dips[dips["TYPE"].str.startswith("Fracture")]
    axes[2].plot(bed["DIP_TRU"], bed["DEPTH_MSS"], "o", ms=3, color="#333333", label="bedding")
    axes[2].plot(frc["DIP_TRU"], frc["DEPTH_MSS"], "^", ms=4, color="#d62728", label="fracture")
    axes[2].set_xlabel("true dip, deg"); axes[2].set_xlim(0, 90); axes[2].legend(fontsize=7)
    axes[3].plot(ani["ANIS"], np.interp(ani["DEPTH"], mss[md_col], mss[ss_col]), color="#9467bd", lw=0.8)
    axes[3].set_xlabel("shear anisotropy, %")
    for ax in axes:
        ax.axhspan(2294, 2311, color="gold", alpha=0.25)
        ax.axhspan(2314.3, 2317.8, color="#b22222", alpha=0.2)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("depth, mSS"); axes[0].invert_yaxis(); axes[0].set_ylim(2440, 2290)
    fig.suptitle("TEC-10 Weatherford CMI (2 May 2018): fracture counts, intensity, dips and dipole-sonic anisotropy\ngold = TEC-12 target window 2,294–2,311 mSS; red = TEC-10 perforations 2,314–2,318 mSS")
    fig.tight_layout(); fig.savefig(ROOT / "figures/14_cmi_fractures.png", dpi=150)


if __name__ == "__main__":
    main()
