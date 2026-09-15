"""Relative water-saturation test for the TEC-12 window at TEC-9 (1973 logs), the direct
offset 118 m from the proposed TEC-12 location (G-47).

TEC-9 has ILD, SN, GR, neutron counts and a sonic (DT:2 in us/m, DT:1 sparse, SPHI sparse)
but no density and no logged aquifer (the log stops at 2,345 mSS, above the -2,374 mSS LKO).
Porosity therefore comes from the sonic (Wyllie, limestone matrix 47.5 us/ft, fluid 189
us/ft), which in an argillaceous or vuggy carbonate is biased: shale raises it, vugs are
missed. The window is compared with the interval TEC-9 produced 353 kbbl from
(2,323-2,328 mSS, squeezed later) using the apparent water resistivity Rwa = Rt * phi^m
and anchors B (produced interval Sw 0.55 and 0.70) and C (book Rw 0.054). A shale-effect
sensitivity reduces the window's sonic porosity by 0-40 %.

Outputs: data/processed/petrophysics/tec9_sw_sensitivity_zones.csv, figures/16_tec9_rwa.png
"""
from __future__ import annotations
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/processed/petrophysics/TEC9_logs_mss.csv"
OUT = ROOT / "data/processed/petrophysics"
DT_MA, DT_F = 47.5, 189.0
ZONES = {"upper 2270-2294": (2270, 2294), "TEC-12 window 2294-2311": (2294, 2311), "tight 2311-2320": (2311, 2320),
         "produced 2323-2328": (2323, 2328), "lower 2328-2340": (2328, 2340)}


def main():
    d = pd.read_csv(SRC)
    d = d[(d.mss >= 2260) & d.res_ild.notna() & (d.res_ild > 0)].copy()
    d["dt_usft"] = d["DT:2"] / 3.28084
    d["phi_sonic"] = ((d.dt_usft - DT_MA) / (DT_F - DT_MA)).clip(lower=0.005, upper=0.35)
    d["phi_sonic"] = d.phi_sonic.interpolate(limit=8)
    zone = np.full(len(d), "", dtype=object)
    for k, (a, b) in ZONES.items():
        zone[(d.mss.values >= a) & (d.mss.values < b)] = k
    d["zone"] = zone
    zmed = d[d.zone != ""].groupby("zone").agg(rt=("res_ild", "median"), sn=("SN", "median"), dt=("dt_usft", "median"),
                                                phi_sonic=("phi_sonic", "median"), sphi=("sphi", "median"),
                                                gr=("gr", "median"), neut=("neut_counts", "median"), sp=("SP", "median"))
    zmed["rwa_m2"] = zmed.rt * zmed.phi_sonic ** 2
    pd.set_option("display.width", 250)
    print(zmed.round(3).to_string())
    rows = []
    pr = zmed.loc["produced 2323-2328"]
    for m, shale_cut, (anc, sw_anchor) in itertools.product([1.8, 2.0, 2.2], [0.0, 0.2, 0.4],
                                                            [("B produced Sw=0.55", 0.55), ("B' produced Sw=0.70", 0.70), ("C book Rw 0.054", None)]):
        rw = 0.054 if sw_anchor is None else sw_anchor ** 2 * pr.rt * pr.phi_sonic ** m
        for z, r in zmed.iterrows():
            phi = r.phi_sonic * (1 - shale_cut) if z in ("TEC-12 window 2294-2311", "upper 2270-2294") else r.phi_sonic
            sw = min(np.sqrt(rw / (r.rt * phi ** m)), 1.5)
            rows.append({"m": m, "window_shale_cut": shale_cut, "anchor": anc, "rw_app": round(rw, 4), "zone": z,
                         "phi_used": round(phi, 3), "sw": round(sw, 3)})
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "tec9_sw_sensitivity_zones.csv", index=False)
    piv = res[res.zone.isin(["TEC-12 window 2294-2311", "produced 2323-2328", "tight 2311-2320"])].pivot_table(
        index=["m", "window_shale_cut", "anchor"], columns="zone", values="sw")
    piv["window/produced"] = (piv["TEC-12 window 2294-2311"] / piv["produced 2323-2328"]).round(2)
    print(piv.round(2).to_string())
    w = res[res.zone == "TEC-12 window 2294-2311"]
    print("window Sw: min %.2f median %.2f max %.2f; ratio window/produced min %.2f median %.2f max %.2f" % (
        w.sw.min(), w.sw.median(), w.sw.max(), piv["window/produced"].min(), piv["window/produced"].median(), piv["window/produced"].max()))

    fig, axes = plt.subplots(1, 4, figsize=(12, 7), sharey=True)
    y = d.mss.values
    axes[0].semilogx(d.res_ild, y, color="#333", lw=0.8, label="ILD"); axes[0].semilogx(d.SN, y, color="#999", lw=0.6, label="SN")
    axes[0].set_xlabel("ohm·m"); axes[0].set_xlim(1, 300); axes[0].legend(fontsize=7)
    axes[1].plot(d.phi_sonic * 100, y, color="#d62728", lw=0.8, label="sonic (Wyllie)"); axes[1].plot(d.sphi * 100, y, "o", ms=2, color="#1f77b4", label="SPHI (1973)")
    axes[1].set_xlabel("porosity, %"); axes[1].set_xlim(0, 25); axes[1].legend(fontsize=7)
    axes[2].plot(d.gr, y, color="#2ca02c", lw=0.8); axes[2].set_xlabel("GR, API"); axes[2].set_xlim(0, 80)
    axes[3].semilogx(d.res_ild * d.phi_sonic ** 2, y, color="#9467bd", lw=0.8); axes[3].set_xlabel("Rwa = Rt·φ², ohm·m"); axes[3].set_xlim(0.005, 1)
    axes[3].axvline(0.054, color="k", lw=0.5, ls="--")
    for ax in axes:
        ax.axhspan(2294, 2311, color="gold", alpha=0.25); ax.axhspan(2323, 2328, color="#b22222", alpha=0.2); ax.grid(alpha=0.3)
    axes[0].set_ylabel("depth, mSS"); axes[0].set_ylim(2345, 2260)
    fig.suptitle("TEC-9 (1973): resistivity, sonic porosity and apparent water resistivity\ngold = TEC-12 window; red = TEC-9 produced interval 2,323–2,328 mSS (353 kbbl); dashed = book Rw")
    fig.tight_layout(); fig.savefig(ROOT / "figures/16_tec9_rwa.png", dpi=150)


if __name__ == "__main__":
    main()
