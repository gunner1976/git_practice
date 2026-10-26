"""Export the field's seismic windows, El Abra surfaces and well paths for the 3-D field viewer in the presentation app.
Usage: .venv/bin/python src/export_viewer_data.py <out_dir>
Inputs: data/raw/colab_out/{pstm554702_window_part*.npz, psdm2019_cube_part*.npz} (Colab extracts, see colab/),
        data/raw/seismic/ElAbraXYZJan2019_GRE.csv (Jan 2019 depth grid), data/processed/seismic/{seismic_ties.csv, pstm_reef_top.csv},
        data/raw/geology/Directional Survey/TECOLUTLA DIRECTIONAL SURVEY DATA.CSV (TEC-9, TEC-10, TEC-11DES),
        data/processed/petrophysics/perforations_mss.csv.
Outputs (<out_dir>): pstm.png / psdm.png (8-bit atlases, one tile per time or depth slice, 128 = zero amplitude),
        viewer_meta.json (grid geometry, axes, surfaces, wells).
Lossy by design: amplitudes are clipped at the 99.5th percentile and quantised to 8 bits; the PSTM is cut to 1,350-1,850 ms and the PSDM
to 2,150-2,550 m. For display and orientation only; interpretation stays on src/seismic_colab_analysis.py.
Depth display of the PSTM: z = v t / 2 with v interpolated (inverse distance) from the per-well average velocities to the reef-top peak
(seismic_ties.csv, 2,914-2,951 m/s); correct at the reef top by construction, approximate above and below it.
"""
import glob, json, sys
import numpy as np, pandas as pd
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT / "data/raw/colab_out"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)


def affine(I, J, X, Y):
    """Least-squares (i, j) -> (x, y) affine; returns origin and the two step vectors."""
    A = np.c_[np.ones(I.size), I.ravel(), J.ravel()]
    cx, *_ = np.linalg.lstsq(A, X.ravel(), rcond=None); cy, *_ = np.linalg.lstsq(A, Y.ravel(), rcond=None)
    res = np.hypot(A @ cx - X.ravel(), A @ cy - Y.ravel())
    return dict(origin=[cx[0], cy[0]], di=[cx[1], cy[1]], dj=[cx[2], cy[2]], fit_rms_m=float(np.sqrt(np.mean(res ** 2))))


def to_u8(V):
    c = float(np.nanpercentile(np.abs(V), 99.5)); q = np.clip(np.nan_to_num(V) / c, -1, 1)
    return np.round(127.5 + 127 * q).astype(np.uint8), c


def atlas(U, path):
    """U (ni, nj, nk) -> PNG with nk tiles of (nj wide, ni tall), cols chosen to keep the image near-square."""
    ni, nj, nk = U.shape; cols = int(np.ceil(np.sqrt(nk * ni / nj))); rows = int(np.ceil(nk / cols))
    img = np.full((rows * ni, cols * nj), 128, np.uint8)
    for k in range(nk):
        r, c = divmod(k, cols); img[r * ni:(r + 1) * ni, c * nj:(c + 1) * nj] = U[:, :, k]
    Image.fromarray(img, "L").save(path, optimize=True)
    return dict(file=path.name, cols=cols, rows=rows, tile=[nj, ni])


meta = {"crs": "UTM 14N WGS84, metres; depth metres below sea level, positive down"}
# ---------------- PSTM 554702 (raw SFSG, Petrel 2013 export)
W = [np.load(p) for p in sorted(glob.glob(str(RAW / "pstm554702_window_part*.npz")))]
tr = np.concatenate([w["data"].astype(np.float32) * float(w["scale"]) for w in W]); t = W[0]["t"].astype(float)
il = np.concatenate([w["inline_189"] for w in W]); xl = np.concatenate([w["ensemble_21"] for w in W])
x = np.concatenate([w["x"] for w in W]); y = np.concatenate([w["y"] for w in W])
i0, j0 = il.min(), xl.min(); ni, nj = il.max() - i0 + 1, xl.max() - j0 + 1
kt = (t >= 1350) & (t <= 1850)
C = np.full((ni, nj, kt.sum()), np.nan, np.float32); C[il - i0, xl - j0] = tr[:, kt]
U, clip = to_u8(C)
geo = affine(il - i0, xl - j0, x, y)
ties = pd.read_csv(ROOT / "data/processed/seismic/seismic_ties.csv").dropna(subset=["vavg_peak_mps"])
ties = ties[~ties.well.str.startswith("TEC-12")]
def v_idw(px, py):
    d2 = (ties.x.values - px) ** 2 + (ties.y.values - py) ** 2 + 1.0; w = 1 / d2
    return float((w * ties.vavg_peak_mps.values).sum() / w.sum())
meta["pstm"] = dict(name="PEMEX PSTM 554702 (raw SFSG), time", ni=int(ni), nj=int(nj), nk=int(kt.sum()), axis="time_ms",
                    k0=float(t[kt][0]), dk=float(t[1] - t[0]), clip=clip, inline0=int(i0), crossline0=int(j0), **geo,
                    atlas=atlas(U, OUT / "pstm.png"), v_field_mps=round(v_idw(707700, 2262600), 1),
                    note="displayed in depth with z = v t / 2, v from the well ties (2,914-2,951 m/s)")
# ---------------- PSDM 2019 (DMI)
D = [np.load(p) for p in sorted(glob.glob(str(RAW / "psdm2019_cube_part*.npz")))]
A = np.concatenate([d["data"].astype(np.float32) * float(d["scale"]) for d in D], 0)
AX = np.concatenate([d["x"] for d in D]); AY = np.concatenate([d["y"] for d in D]); z = D[0]["z"].astype(float)
kz = (z >= 2150) & (z <= 2550)
Ua, clipa = to_u8(A[:, :, kz])
I, J = np.meshgrid(np.arange(A.shape[0]), np.arange(A.shape[1]), indexing="ij")
meta["psdm"] = dict(name="PSDM 2019 (DMI), depth", ni=int(A.shape[0]), nj=int(A.shape[1]), nk=int(kz.sum()), axis="depth_m",
                    k0=float(z[kz][0]), dk=float(z[1] - z[0]), clip=clipa, **affine(I, J, AX, AY), atlas=atlas(Ua, OUT / "psdm.png"),
                    note="z read as metres below sea level (no unit in the file)")
# ---------------- surfaces
g = pd.read_csv(ROOT / "data/raw/seismic/ElAbraXYZJan2019_GRE.csv")
xs, ys = np.sort(g.X.unique()), np.sort(g.Y.unique())
Z = -g.pivot_table(index="Y", columns="X", values="Depth").reindex(index=ys, columns=xs).values
meta["grid2019"] = dict(name="Top El Abra, Jan 2019 depth grid", x0=float(xs[0]), y0=float(ys[0]), dx=float(xs[1] - xs[0]), dy=float(ys[1] - ys[0]),
                        nx=len(xs), ny=len(ys), z=[[None if np.isnan(v) else round(float(v), 1) for v in row] for row in Z])
p = pd.read_csv(ROOT / "data/processed/seismic/pstm_reef_top.csv")
p["i"] = (p.inline - i0).astype(int); p["j"] = (p.crossline - j0).astype(int)
H = np.full((ni, nj), np.nan); ok = p.peak_ms.notna()
H[p.i[ok], p.j[ok]] = [pk / 2000 * v_idw(a, b) for pk, a, b in zip(p.peak_ms[ok], p.x[ok], p.y[ok])]
meta["pstm_top"] = dict(name="Reef-top peak tracked on the PSTM, depth-converted with the well velocities", ni=int(ni), nj=int(nj),
                        z=[[None if np.isnan(v) else round(float(v), 1) for v in row] for row in H])
# ---------------- wells
sv = pd.read_csv(ROOT / "data/raw/geology/Directional Survey/TECOLUTLA DIRECTIONAL SURVEY DATA.CSV")
sv["NAME"] = sv.NAME.str.replace("TECOLUTLA-9", "TEC-9").str.replace("TEC_10", "TEC-10").str.replace("TEC-11DES", "TEC-11")
perfs = pd.read_csv(ROOT / "data/processed/petrophysics/perforations_mss.csv")
tops = pd.read_csv(ROOT / "data/processed/seismic/el_abra_grid_ties.csv").set_index("well")
vert = {"TEC-2": (4.0, 2375), "TEC-3": (6.0, 2380.5), "TEC-5": (4.0, 2562.1), "TEC-6": (5.67, 2338.9), "TEC-7": (4.8, 2340), "TEC-101": (8.0, 2364)}
wells = []
for w, (kb, td) in vert.items():
    x0, y0 = tops.loc[w, "x"], tops.loc[w, "y"]
    wells.append(dict(well=w, kb=kb, path=[[x0, y0, -kb], [x0, y0, td - kb]], top_mss=float(-tops.loc[w, "top_mss"]), survey="vertical (no survey; PEMEX records)"))
for w in ["TEC-9", "TEC-10", "TEC-11"]:
    s = sv[sv.NAME == w].sort_values("MD")
    wells.append(dict(well=w, kb=float(s.TVDSS.iloc[0]), path=[[round(a, 2), round(b, 2), round(-c, 2)] for a, b, c in zip(s.XPATH, s.YPATH, s.TVDSS)],
                      md=[round(m, 1) for m in s.MD], survey="TECOLUTLA DIRECTIONAL SURVEY DATA.CSV",
                      top_mss=float(-tops.loc[w, "top_mss"]) if w in tops.index else None))
# TEC-12: programme surface and bottom-hole locations (completion programme Feb 2021); the path between them is schematic
sx, sy, bx, by = 707582.0, 2262425.0, 707754.0, 2262460.0
pts = [[sx, sy, -6.0], [sx, sy, 1500.0]]
for f in np.linspace(0, 1, 9)[1:]:
    pts.append([sx + (bx - sx) * f, sy + (by - sy) * f, 1500 + (2310 - 1500) * f])
wells.append(dict(well="TEC-12", kb=6.0, path=[[round(a, 1), round(b, 1), round(c, 1)] for a, b, c in pts], top_mss=2296.0, planned=True,
                  survey="schematic: programme surface and bottom-hole locations, prognosed El Abra top -2,296 mSS"))
for w in wells:
    pp = perfs[perfs.well == w["well"]]
    w["perfs"] = [dict(top=round(float(a), 1), base=round(float(b), 1), status=str(s)) for a, b, s in zip(pp.top_mss, pp.base_mss, pp["Type and Status"])]
meta["wells"] = wells
(OUT / "viewer_meta.json").write_text(json.dumps(meta, separators=(",", ":")))
print("PSTM", ni, nj, kt.sum(), "fit", round(meta["pstm"]["fit_rms_m"], 2), "m; PSDM", A.shape, kz.sum(), "fit", round(meta["psdm"]["fit_rms_m"], 2))
for f in OUT.iterdir(): print(f.name, f.stat().st_size)
