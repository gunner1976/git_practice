"""Task 19 support: structure at TEC-12 from the PSDM (DMI 2019) and PEMEX PSTM (554702) field windows extracted in Colab
(colab/tecolutla_seismic_extract.ipynb -> data/raw/colab_out/).
Usage: .venv/bin/python src/seismic_colab_analysis.py
Outputs: data/processed/seismic/{seismic_ties.csv, seismic_loo.csv, seismic_summary.json, pstm_reef_top.csv, psdm_reef_top.csv},
         figures/26_seismic_sections.png, figures/27_seismic_structure_maps.png

Method
- PSDM: int16-requantised sub-cube, 25 m bins, z read as metres below sea level (zstart -280 m, 2 m; no unit in the file).
- PSTM 554702 (raw, 2 ms, Petrel 2013 export, UTM 14N WGS84): traces gridded by inline (bytes 189) / crossline (bytes 21).
- In both volumes the reef-top trough-peak pair is auto-tracked from a seed at the TEC-12 bottom hole (flood fill, best peak within
  +-4 ms / +-2 m of the neighbour, amplitude > 25 % of the seed), restricted to the field (Jan 2019 grid shallower than -2,345 m).
  PSTM pair: trough ~1,548 ms, peak ~1,566 ms at TEC-12. PSDM pair: trough ~2,275 m, peak ~2,298 m at TEC-12.
- Ties: well tops (formation-tops table / GLJ map, data/processed/seismic/el_abra_grid_ties.csv) against the tracked events.
- PSTM depth at TEC-12: well top / (peak time / 2) gives an average velocity per well; the velocity at TEC-12 is the inverse-distance
  mean of the wells; leave-one-out over the wells measures the prediction error.
Polarity is not stated in the files; "peak" and "trough" refer to sample sign only.
"""
import glob, heapq, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "data/processed/seismic/"; RAW = "data/raw/colab_out/"
INK = "#0b0b0b"; INK2 = "#52514e"; SURF = "#fcfcfb"
T12 = (707754.0, 2262460.0); NCREST = (707350.58, 2263168.54)


def grid_sampler():
    g = pd.read_csv("data/raw/seismic/ElAbraXYZJan2019_GRE.csv")
    xs, ys = np.sort(g.X.unique()), np.sort(g.Y.unique())
    Zg = g.pivot_table(index="Y", columns="X", values="Depth").reindex(index=ys, columns=xs).values
    def s(x, y):
        i = np.searchsorted(xs, x) - 1; j = np.searchsorted(ys, y) - 1
        if i < 0 or j < 0 or i >= len(xs) - 1 or j >= len(ys) - 1: return np.nan
        tx = (x - xs[i]) / (xs[i + 1] - xs[i]); ty = (y - ys[j]) / (ys[j + 1] - ys[j]); z = Zg[j:j + 2, i:i + 2]
        return -float(z[0, 0] * (1 - tx) * (1 - ty) + z[0, 1] * tx * (1 - ty) + z[1, 0] * (1 - tx) * ty + z[1, 1] * tx * ty)
    return s


def peaks(tr, z):
    m = np.where((tr[1:-1] > tr[:-2]) & (tr[1:-1] >= tr[2:]))[0] + 1
    d = tr[m - 1] - 2 * tr[m] + tr[m + 1]; off = np.where(d != 0, 0.5 * (tr[m - 1] - tr[m + 1]) / d, 0)
    return z[m] + off * (z[1] - z[0]), tr[m]


def track(C, z, mask, seed, z0, sign, step, minfrac=0.25):
    S = sign * C; ni, nj, _ = S.shape; H = np.full((ni, nj), np.nan)
    pz, pa = peaks(S[seed], z); k = np.argmin(abs(pz - z0)); H[seed] = pz[k]; a0 = pa[k]; hp = [(-pa[k], seed)]
    while hp:
        _, (i, j) = heapq.heappop(hp)
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            a, b = i + di, j + dj
            if not (0 <= a < ni and 0 <= b < nj) or not mask[a, b] or np.isfinite(H[a, b]): continue
            pz, pa = peaks(S[a, b], z); ok = (abs(pz - H[i, j]) <= step) & (pa > minfrac * a0)
            if not ok.any(): continue
            c = np.argmax(np.where(ok, pa, -np.inf)); H[a, b] = pz[c]; heapq.heappush(hp, (-pa[c], (a, b)))
    return H


def nearest(X, Y, x, y):
    d = np.where(np.isfinite(X), (X - x) ** 2 + (Y - y) ** 2, np.inf); i, j = np.unravel_index(np.argmin(d), d.shape)
    return (i, j), float(np.sqrt(d[i, j]))


def med3(H, ij):  # 3 x 3 median around a trace, for robustness to single-trace picks
    i, j = ij; return float(np.nanmedian(H[max(i - 1, 0):i + 2, max(j - 1, 0):j + 2]))


gs = grid_sampler()
# ---------------- PSDM
D = [np.load(p) for p in sorted(glob.glob(RAW + "psdm2019_cube_part*.npz"))]
A = np.concatenate([d["data"].astype(np.float32) * float(d["scale"]) for d in D], 0)
AX = np.concatenate([d["x"] for d in D]); AY = np.concatenate([d["y"] for d in D]); Zd = D[0]["z"].astype(float)
AG = np.vectorize(gs)(AX, AY); amask = np.isfinite(AG) & (AG < 2345)
s = nearest(AX, AY, *T12)[0]
dP = track(A, Zd, amask, s, 2298, 1, 2.0); dT = track(A, Zd, amask, s, 2275, -1, 2.0)
# ---------------- PSTM 554702
W = [np.load(p) for p in sorted(glob.glob(RAW + "pstm554702_window_part*.npz"))]
tr = np.concatenate([w["data"].astype(np.float32) * float(w["scale"]) for w in W]); t = W[0]["t"].astype(float)
il = np.concatenate([w["inline_189"] for w in W]); xl = np.concatenate([w["ensemble_21"] for w in W])
x = np.concatenate([w["x"] for w in W]); y = np.concatenate([w["y"] for w in W])
i0, j0 = il.min(), xl.min(); ni, nj = il.max() - i0 + 1, xl.max() - j0 + 1
C = np.zeros((ni, nj, len(t)), np.float32); TX = np.full((ni, nj), np.nan); TY = np.full((ni, nj), np.nan)
C[il - i0, xl - j0] = tr; TX[il - i0, xl - j0] = x; TY[il - i0, xl - j0] = y
TG = np.full((ni, nj), np.nan); have = np.isfinite(TX); TG[have] = [gs(a, b) for a, b in zip(TX[have], TY[have])]
tmask = have & np.isfinite(TG) & (TG < 2345)
s = nearest(TX, TY, *T12)[0]
tP = track(C, t, tmask, s, 1566, 1, 4.0); tT = track(C, t, tmask, s, 1548, -1, 4.0)

# ---------------- ties
ties = pd.read_csv(OUT + "el_abra_grid_ties.csv")
pts = [(r.well, r.x, r.y, -r.top_mss) for r in ties.itertuples()] + [("north grid crest", *NCREST, np.nan)]
rows = []
for n, xx, yy, top in pts:
    a, da = nearest(AX, AY, xx, yy); b, db = nearest(TX, TY, xx, yy)
    rows.append(dict(well=n, x=xx, y=yy, top_mss=top, grid_mss=round(gs(xx, yy), 1),
                     pstm_trough_ms=round(med3(tT, b), 1), pstm_peak_ms=round(med3(tP, b), 1),
                     psdm_trough_m=round(med3(dT, a), 1), psdm_peak_m=round(med3(dP, a), 1), psdm_trace_m=round(da, 1), pstm_trace_m=round(db, 1)))
tt = pd.DataFrame(rows)
tt["vavg_peak_mps"] = tt.top_mss / (tt.pstm_peak_ms / 2000.0)
tt["vavg_trough_mps"] = tt.top_mss / (tt.pstm_trough_ms / 2000.0)
wells = tt[tt.top_mss.notna() & ~tt.well.str.startswith("TEC-12") & tt.vavg_peak_mps.notna()].copy()

def idw_v(xx, yy, df, col):
    d = np.hypot(df.x - xx, df.y - yy).clip(lower=25.0); w = 1 / d ** 2; return float((df[col] * w).sum() / w.sum())

loo = []
for r in wells.itertuples():
    rest = wells[wells.well != r.well]
    v = idw_v(r.x, r.y, rest, "vavg_peak_mps"); pred = v * r.pstm_peak_ms / 2000.0
    loo.append(dict(well=r.well, top_mss=r.top_mss, predicted_mss=round(pred, 1), error_m=round(pred - r.top_mss, 1)))
loo = pd.DataFrame(loo)
row12 = tt[tt.well.str.startswith("TEC-12")].iloc[0]
v12 = idw_v(*T12, wells, "vavg_peak_mps"); z12 = v12 * row12.pstm_peak_ms / 2000.0
near2 = wells[wells.well.isin(["TEC-9", "TEC-10"])]
z12_rng = [float(near2.vavg_peak_mps.min() * row12.pstm_peak_ms / 2000.0), float(near2.vavg_peak_mps.max() * row12.pstm_peak_ms / 2000.0)]
tt["pstm_depth_est_mss"] = np.nan
for k in tt.index:
    if np.isfinite(tt.at[k, "pstm_peak_ms"]):
        tt.at[k, "pstm_depth_est_mss"] = idw_v(tt.at[k, "x"], tt.at[k, "y"], wells, "vavg_peak_mps") * tt.at[k, "pstm_peak_ms"] / 2000.0
tt = tt.round({"vavg_peak_mps": 0, "vavg_trough_mps": 0, "pstm_depth_est_mss": 1})
tt.to_csv(OUT + "seismic_ties.csv", index=False); loo.to_csv(OUT + "seismic_loo.csv", index=False)
corr = lambda a, b: float(np.corrcoef(a, b)[0, 1])
w5 = wells.dropna(subset=["psdm_peak_m"])
# rank of the TEC-12 location among all tracked field traces (fraction of traces with an earlier PSTM peak)
frac_earlier = float(np.mean(tP[np.isfinite(tP)] < row12.pstm_peak_ms))
summary = dict(
    psdm=dict(cube=list(A.shape), bin_m=25, z_axis="m below sea level (read; no unit in file)", dominant_wavelength_m=67,
              tracked_fraction=[float(np.isfinite(dP)[amask].mean()), float(np.isfinite(dT)[amask].mean())],
              corr_peak_vs_tops=corr(w5.psdm_peak_m, w5.top_mss),
              note="reef-level reflectors are highest along the west (TEC-101, TEC-2, north) and lower at TEC-9/TEC-12: the reverse of the log tops"),
    pstm=dict(volume="554702 SFSG (raw)", cube=[int(ni), int(nj), len(t)], sample_ms=2.0,
              tracked_fraction=[float(np.isfinite(tP)[tmask].mean()), float(np.isfinite(tT)[tmask].mean())],
              corr_peak_time_vs_tops=corr(wells.pstm_peak_ms, wells.top_mss),
              vavg_peak_mps=dict(zip(wells.well, wells.vavg_peak_mps.round(0))),
              loo_error_m=dict(mean=float(loo.error_m.mean()), rms=float(np.sqrt((loo.error_m ** 2).mean())), max_abs=float(loo.error_m.abs().max())),
              tec12=dict(peak_ms=float(row12.pstm_peak_ms), trough_ms=float(row12.pstm_trough_ms), v_idw_mps=v12, depth_est_mss=z12,
                         depth_range_tec9_tec10_velocity=z12_rng, grid_mss=float(row12.grid_mss), prognosis_mss=2296.0,
                         fraction_of_field_traces_with_earlier_peak=frac_earlier),
              north_grid_crest=dict(peak_ms=float(tt[tt.well == "north grid crest"].pstm_peak_ms.iloc[0]),
                                    trough_ms=float(tt[tt.well == "north grid crest"].pstm_trough_ms.iloc[0]))))
json.dump(summary, open(OUT + "seismic_summary.json", "w"), indent=1, default=float)
pd.DataFrame(dict(x=TX.ravel(), y=TY.ravel(), inline=(np.arange(ni)[:, None] + i0 + 0 * TX).ravel(), crossline=(np.arange(nj)[None, :] + j0 + 0 * TX).ravel(),
                  trough_ms=tT.ravel(), peak_ms=tP.ravel())).dropna(subset=["x"]).round(2).to_csv(OUT + "pstm_reef_top.csv", index=False)
pd.DataFrame(dict(x=AX.ravel(), y=AY.ravel(), trough_m=dT.ravel(), peak_m=dP.ravel())).round(2).to_csv(OUT + "psdm_reef_top.csv", index=False)
print(tt.drop(columns=["x", "y"]).to_string(index=False)); print(loo.to_string(index=False)); print(json.dumps(summary["pstm"]["tec12"], indent=1))

# ---------------- figure 26: sections
def polyline(names, step=12.5):
    tl = ties.set_index("well"); P = [(tl.loc[n].x, tl.loc[n].y) if isinstance(n, str) else n for n in names]; L = []
    for (x0, y0), (x1, y1) in zip(P[:-1], P[1:]):
        n = max(int(np.hypot(x1 - x0, y1 - y0) / step), 1); L += [(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u) for u in np.linspace(0, 1, n, endpoint=False)]
    L.append(P[-1]); L = np.array(L); return P, L, np.r_[0, np.cumsum(np.hypot(*np.diff(L, axis=0).T))]

def section(ax, cube, X, Y, zax, names, title, depth=True, H=None):
    P, L, d = polyline(names); S = []
    for xx, yy in L:
        (i, j), _ = nearest(X, Y, xx, yy); S.append(cube[i, j])
    S = np.array(S).T; v = np.percentile(np.abs(S), 98)
    ax.imshow(S, cmap="gray_r", vmin=-v, vmax=v, aspect="auto", extent=[0, d[-1], zax[-1], zax[0]])
    if H is not None:
        hv = [H[nearest(X, Y, xx, yy)[0]] for xx, yy in L]; ax.plot(d, hv, color="#eb6834", lw=1.4, label="tracked reef-top peak")
    if depth: ax.plot(d, [gs(xx, yy) for xx, yy in L], color="#1baf7a", lw=1.6, label="Jan 2019 Top El Abra grid")
    tl = ties.set_index("well")
    for n, p in zip(names, P):
        if not isinstance(n, str): continue
        k = np.argmin(np.hypot(L[:, 0] - p[0], L[:, 1] - p[1])); ax.axvline(d[k], color="#2a78d6", lw=0.8)
        ax.text(d[k], (zax[0] if depth else zax[0]) + (8 if depth else 6), n.replace(" (plan)", ""), ha="center", va="top", fontsize=8, color="#2a78d6",
                bbox=dict(fc=SURF, ec="none", alpha=0.8, pad=1))
        if depth and np.isfinite(tl.loc[n].top_mss): ax.plot(d[k], -tl.loc[n].top_mss, "o", color="#eda100", mec=INK, ms=6)
    ax.set_title(title, fontsize=9.5, loc="left", color=INK); ax.set_xlabel("distance along line, m", fontsize=8)
    ax.set_ylabel("depth, m below sea level" if depth else "two-way time, ms", fontsize=8); ax.tick_params(labelsize=7.5)

kd = (Zd >= 2150) & (Zd <= 2500); kt = (t >= 1450) & (t <= 1750)
fig, axs = plt.subplots(2, 2, figsize=(15, 9), facecolor=SURF)
line1 = ["TEC-10", "TEC-12 BHL (plan)", "TEC-9"]; line2 = ["TEC-101", "TEC-6", "TEC-12 BHL (plan)", "TEC-9"]
section(axs[0, 0], A[:, :, kd], AX, AY, Zd[kd], line1, "PSDM (DMI 2019): TEC-10 - TEC-12 - TEC-9 (dots = well tops)", True, dP)
section(axs[0, 1], C[:, :, kt], TX, TY, t[kt], line1, "PEMEX PSTM 554702: TEC-10 - TEC-12 - TEC-9", False, tP)
section(axs[1, 0], A[:, :, kd], AX, AY, Zd[kd], line2, "PSDM: TEC-101 - TEC-6 - TEC-12 - TEC-9", True, dP)
section(axs[1, 1], C[:, :, kt], TX, TY, t[kt], line2, "PSTM: TEC-101 - TEC-6 - TEC-12 - TEC-9", False, tP)
axs[0, 0].legend(fontsize=7.5, loc="lower left", frameon=True); axs[0, 1].legend(fontsize=7.5, loc="lower left", frameon=True)
plt.tight_layout(); plt.savefig("figures/26_seismic_sections.png", dpi=140, facecolor=SURF); plt.close()

# ---------------- figure 27: maps
fig, axs = plt.subplots(1, 3, figsize=(16, 6.2), facecolor=SURF)
gsel = (AG < 2345)
panels = [(AX, AY, np.where(gsel, AG, np.nan), "Jan 2019 Top El Abra grid (m below sea level)"),
          (TX, TY, tP, "PEMEX PSTM: reef-top peak time (ms), tracked"),
          (AX, AY, dP, "DMI PSDM: reef-top peak depth (m), tracked")]
for ax, (XX, YY, V, lab) in zip(axs, panels):
    ax.set_facecolor(SURF); ok = np.isfinite(V) & np.isfinite(XX)
    m = ax.scatter(XX[ok], YY[ok], c=V[ok], s=9, marker="s", cmap="viridis_r", vmin=np.nanpercentile(V[ok], 3), vmax=np.nanpercentile(V[ok], 97))
    cb = plt.colorbar(m, ax=ax, shrink=0.8); cb.ax.tick_params(labelsize=7); cb.ax.invert_yaxis()
    for r in ties.itertuples():
        if r.well in ("TEC-5", "TEC-3"): continue
        is12 = r.well.startswith("TEC-12"); ax.plot(r.x, r.y, "*" if is12 else "o", color="#eb6834" if is12 else INK, ms=12 if is12 else 4, mec=INK)
        ax.annotate(r.well.replace(" BHL (plan)", ""), (r.x, r.y), xytext=(4, 3), textcoords="offset points", fontsize=7)
    ax.plot(*NCREST, "+", color="#d03b3b", ms=10, mew=2); ax.annotate("grid north crest", NCREST, xytext=(4, -10), textcoords="offset points", fontsize=7, color="#d03b3b")
    ax.set_xlim(706900, 708350); ax.set_ylim(2261850, 2263750); ax.set_aspect("equal"); ax.set_title(lab, fontsize=9, loc="left")
    ax.tick_params(labelsize=6.5); ax.ticklabel_format(useOffset=False, style="plain")
fig.suptitle("Shallow = yellow. PSTM time high is on TEC-6 / TEC-12 / TEC-9 / TEC-10, as the well tops are; the grid's north crest is not high on the PSTM",
             fontsize=10, x=0.01, ha="left", color=INK)
plt.tight_layout(); plt.savefig("figures/27_seismic_structure_maps.png", dpi=140, facecolor=SURF); plt.close()
print("figures 26, 27 written")
