"""Bounded water-saturation sensitivity for the TEC-12 target window at TEC-10 (G-47).

The window (2,294-2,311 mSS at TEC-10) reads 4-8 ohm.m with 7-10 % porosity; the
perforated interval below (2,311-2,320 mSS) reads 20-40 ohm.m with 1-6 % porosity and
produced at ~30 % oil cut. No core electrical properties or water analysis exist, so Rw,
m and the clay correction are unknown. Instead of book values this script anchors the
model three ways and reports the window relative to the produced interval:

  A. aquifer-anchored:  Sw = 1 in the zone below GLJ's LKO (-2,374.2 mSS) -> Rw_app
  B. produced-anchored: Sw = 0.55 in the perforated interval (IHS 2018 test model) -> Rw_app
  C. book values:       Rw 0.054 ohm.m (PEMEX 45,000 ppm at 98.6 C), a = 1

For each anchor: m in {1.8, 2.0, 2.2}, n = 2, porosity = mean(N,D) or density-only, and a
clay correction (Simandoux) with Vsh from the neutron-density separation against an
assumed shale point (separation 25 pu; 20 and 30 pu as sensitivity) and Rsh 4 ohm.m.

Inputs : data/processed/petrophysics/TEC10_logs_mss.csv (task 9; casing above 2,245 mSS excluded)
Outputs: data/processed/petrophysics/tec10_sw_sensitivity_zones.csv, tec10_sw_sensitivity_curves.csv,
         figures/15_sw_sensitivity.png
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
SRC = ROOT / "data/processed/petrophysics/TEC10_logs_mss.csv"
OUT = ROOT / "data/processed/petrophysics"
ZONES = {"upper El Abra 2270-2294": (2270, 2294), "TEC-12 window 2294-2311": (2294, 2311),
         "perforated 2311-2320": (2311, 2320), "lower produced 2320-2332": (2320, 2332),
         "tight 2332-2374": (2332, 2374.2), "below LKO 2374-2447": (2374.2, 2447)}
RW_BOOK, RSH, N = 0.054, 4.0, 2.0


def simandoux_sw(rt, phi, vsh, rw, rsh, m, n=2.0):
    """Sw from 1/Rt = phi^m Sw^n / Rw + Vsh Sw / Rsh, n = 2 (quadratic)."""
    a = phi ** m / rw
    b = vsh / rsh
    c = -1.0 / rt
    with np.errstate(invalid="ignore", divide="ignore"):
        sw = (-b + np.sqrt(b * b - 4 * a * c)) / (2 * a)
    return sw


def main():
    d = pd.read_csv(SRC)
    d = d[(d.mss >= 2245) & (d.res_ild < 1e5)].copy()
    d["phi_mean"] = ((d.NPOR + d.DPOR) / 2).clip(lower=0.005)
    d["phi_den"] = d.DPOR.clip(lower=0.005)
    d["sep_pu"] = (d.NPOR - d.DPOR) * 100
    zone_of = np.full(len(d), "", dtype=object)
    for k, (a, b) in ZONES.items():
        zone_of[(d.mss.values >= a) & (d.mss.values < b)] = k
    d["zone"] = zone_of
    zmed = d[d.zone != ""].groupby("zone").agg(rt=("res_ild", "median"), phi_mean=("phi_mean", "median"),
                                                phi_den=("phi_den", "median"), sep_pu=("sep_pu", "median"),
                                                gr=("GRGM", "median"), pe=("pe", "median"))
    rows = []
    curves = {}
    for phi_name, m, sep_sh in itertools.product(["phi_mean", "phi_den"], [1.8, 2.0, 2.2], [None, 20, 25, 30]):
        phi = d[phi_name].values
        vsh = np.zeros_like(phi) if sep_sh is None else np.clip(d.sep_pu.values / sep_sh, 0, 0.6)
        phie = phi * (1 - vsh)
        rt = d.res_ild.values
        aq = zmed.loc["below LKO 2374-2447"]
        pf = zmed.loc["perforated 2311-2320"]
        anchors = {
            "A aquifer Sw=1": aq.rt * aq[phi_name] ** m,
            "B produced Sw=0.55": 0.55 ** N * pf.rt * pf[phi_name] ** m,
            "C book Rw 0.054": RW_BOOK,
        }
        for anc, rw in anchors.items():
            if sep_sh is None:
                sw = np.sqrt(rw / (rt * phie ** m))
            else:
                sw = simandoux_sw(rt, phie, vsh, rw, RSH, m, N)
            sw = np.clip(sw, 0, 1.5)
            key = (phi_name, m, sep_sh, anc)
            curves[key] = sw
            for z in ZONES:
                sel = d.zone.values == z
                rows.append({"porosity": phi_name, "m": m, "clay_sep_pu": sep_sh or 0, "anchor": anc,
                             "rw_app_ohmm": round(float(rw), 4), "zone": z,
                             "sw_median": round(float(np.median(sw[sel])), 3),
                             "sw_p25": round(float(np.percentile(sw[sel], 25)), 3),
                             "vsh_median": round(float(np.median(vsh[sel])), 3),
                             "phie_median": round(float(np.median(phie[sel])), 3)})
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "tec10_sw_sensitivity_zones.csv", index=False)
    cdf = pd.DataFrame({"mss": d.mss.values, "rt": d.res_ild.values, "phi_mean": d.phi_mean.values, "phi_den": d.phi_den.values, "sep_pu": d.sep_pu.values})
    for key, sw in curves.items():
        cdf[f"sw|{key[0]}|m{key[1]}|clay{key[2] or 0}|{key[3][0]}"] = sw
    cdf.to_csv(OUT / "tec10_sw_sensitivity_curves.csv", index=False)

    piv = res[res.zone.isin(["TEC-12 window 2294-2311", "perforated 2311-2320", "lower produced 2320-2332"])]
    piv = piv.pivot_table(index=["porosity", "m", "clay_sep_pu", "anchor"], columns="zone", values="sw_median")
    piv["window/perforated"] = (piv["TEC-12 window 2294-2311"] / piv["perforated 2311-2320"]).round(2)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
    print(zmed.round(3).to_string()); print(piv.round(2).to_string())
    w = res[res.zone == "TEC-12 window 2294-2311"]
    print("\nWindow Sw median across all 72 cases: min %.2f  p25 %.2f  median %.2f  p75 %.2f  max %.2f" % tuple(w.sw_median.quantile([0, .25, .5, .75, 1])))
    print("cases with window Sw < 0.6:", int((w.sw_median < 0.6).sum()), "of", len(w))
    print("window/perforated ratio: min %.2f median %.2f max %.2f" % (piv["window/perforated"].min(), piv["window/perforated"].median(), piv["window/perforated"].max()))

    # figure: three anchors, m = 2, phi_mean vs phi_den, with and without clay
    fig, axes = plt.subplots(1, 4, figsize=(13, 8), sharey=True)
    y = d.mss.values
    axes[0].semilogx(d.res_ild, y, color="#333", lw=0.8); axes[0].set_xlabel("ILD, ohm·m"); axes[0].set_xlim(1, 200)
    axes[1].plot(d.phi_mean * 100, y, color="#1f77b4", lw=0.8, label="mean N-D"); axes[1].plot(d.phi_den * 100, y, color="#d62728", lw=0.8, label="density")
    axes[1].plot(d.sep_pu, y, color="#2ca02c", lw=0.6, label="N-D separation, pu"); axes[1].set_xlabel("porosity, %"); axes[1].set_xlim(-5, 20); axes[1].legend(fontsize=7)
    cols = {"A aquifer Sw=1": "#1f77b4", "B produced Sw=0.55": "#ff7f0e", "C book Rw 0.054": "#2ca02c"}
    for anc, c in cols.items():
        axes[2].plot(curves[("phi_mean", 2.0, None, anc)], y, color=c, lw=0.8, label=anc)
        axes[3].plot(curves[("phi_den", 2.0, 25, anc)], y, color=c, lw=0.8, label=anc)
    axes[2].set_xlabel("Sw, Archie, mean N-D porosity, m 2"); axes[3].set_xlabel("Sw, Simandoux, density porosity,\nVsh from N-D (25 pu), m 2")
    for ax in axes[2:]:
        ax.set_xlim(0, 1.5); ax.axvline(1, color="k", lw=0.5, ls="--"); ax.legend(fontsize=7, loc="lower right")
    for ax in axes:
        ax.axhspan(2294, 2311, color="gold", alpha=0.25); ax.axhspan(2314.3, 2317.8, color="#b22222", alpha=0.2)
        ax.axhline(2374.2, color="#1f77b4", lw=0.8, ls=":"); ax.grid(alpha=0.3)
    axes[0].set_ylabel("depth, mSS"); axes[0].set_ylim(2440, 2250)
    fig.suptitle("TEC-10 water-saturation sensitivity for the TEC-12 window (gold) vs the perforations (red)\nanchors: A aquifer below LKO (dotted) = water; B perforated interval Sw 0.55 (IHS); C book Rw 0.054 ohm·m")
    fig.tight_layout(); fig.savefig(ROOT / "figures/15_sw_sensitivity.png", dpi=150)


if __name__ == "__main__":
    main()
