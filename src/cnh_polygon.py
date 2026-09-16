"""CNH field polygon for Tecolutla (G-43).

Source: CNH_R01_L03_2015-campos.shp (Drive id 16p3LwvhAzqztuCkbz6zcW6f-AL2HKhiD, 145,992 B,
WGS84; .prj id 1Y0cIXkyFup_qxAYVHQtCfBs_m59jQJG1), the field outlines published with the
Ronda 1 tercera convocatoria (2015) data room. The .dbf (id 1CPYUpHX598g6cKTljdd1USNf2ioDI-4q)
lists 13 fields in this order: Mareógrafo, Duna, Benavides, San Bernardo, Peña Blanca,
Carretas, La Laja, Paso de Oro, Tecolutla, Calibrador, Barcodón, Ricos, Pontón; the
Tecolutla record is index 8 and is confirmed here by the well coordinates falling inside it.

Outputs: data/processed/cnh/tecolutla_cnh_polygon.csv (WGS84 + UTM 14N vertices),
         data/processed/cnh/cnh_polygon_summary.json, figures/13_cnh_polygon.png
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pyproj
import shapefile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SHP = ROOT / "data/raw/cnh_gis/CNH_R01_L03_2015-campos.shp"
HDR = ROOT / "data/raw/geology/Tecolutla Well header Information/Tecolutla Well Header Information.csv"
OUT = ROOT / "data/processed/cnh"
TR = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32614", always_xy=True)
IDX = 8


def ring_area_km2(xy):
    x, y = xy[:, 0], xy[:, 1]
    return abs(np.dot(x[:-1], y[1:]) - np.dot(x[1:], y[:-1])) / 2 / 1e6


def inside(pts, px, py):
    ins = False
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
            ins = not ins
    return ins


def main():
    r = shapefile.Reader(shp=open(SHP, "rb"))
    s = r.shapes()[IDX]
    ll = np.array(s.points)
    xy = np.array([TR.transform(x, y) for x, y in ll])
    area = ring_area_km2(xy)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"lon": ll[:, 0], "lat": ll[:, 1], "x_utm14n_m": xy[:, 0], "y_utm14n_m": xy[:, 1]}).to_csv(OUT / "tecolutla_cnh_polygon.csv", index=False)

    hdr = pd.read_csv(HDR)
    lonc = [c for c in hdr.columns if "lon" in c.lower()][0]
    latc = [c for c in hdr.columns if "lat" in c.lower()][0]
    namec = hdr.columns[0]
    wells = hdr[[namec, lonc, latc]].dropna()
    wells["inside"] = [inside(ll, x, y) for x, y in zip(wells[lonc], wells[latc])]
    ifr_km2 = 630 * 0.00404686
    summ = {"cnh_polygon_area_km2": round(area, 3), "ifr_630ac_km2": round(ifr_km2, 3),
            "ratio_cnh_over_ifr": round(area / ifr_km2, 3), "bbox_lon": [float(ll[:, 0].min()), float(ll[:, 0].max())],
            "bbox_lat": [float(ll[:, 1].min()), float(ll[:, 1].max())],
            "wells": wells.rename(columns={namec: "well", lonc: "lon", latc: "lat"}).to_dict("records")}
    (OUT / "cnh_polygon_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=1))

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(xy[:, 0] / 1000, xy[:, 1] / 1000, "-", color="#1f4e79", lw=2, label=f"CNH field polygon, {area:.2f} km² (2015 data room)")
    for _, w in wells.iterrows():
        x, y = TR.transform(w[lonc], w[latc])
        ax.plot(x / 1000, y / 1000, "o", color="#b22222" if w["inside"] else "#888888", ms=6)
        ax.annotate(str(w[namec]).replace("TECOLUTLA", "TEC"), (x / 1000, y / 1000), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.set_xlabel("UTM 14N easting, km"); ax.set_ylabel("UTM 14N northing, km")
    ax.set_title("Tecolutla: CNH field polygon vs well locations\n(IFR volumetrics use 630 ac = 2.55 km²; GLJ 1P/2P/3P 401/515/630 ac)")
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout(); fig.savefig(ROOT / "figures/13_cnh_polygon.png", dpi=150)


if __name__ == "__main__":
    main()
