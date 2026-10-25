"""Task 19: Top El Abra structure map from the Jan 2019 depth grid, with well tops and the TEC-12 target.
Usage: .venv/bin/python src/structure_map.py -> figures/25_el_abra_structure.png, data/processed/seismic/el_abra_grid_ties.csv
Sources: ElAbraXYZJan2019_GRE.csv (Drive 1cgN5-M1EkKNBWUhGHpNSxzG3aA4pyC4p; 2,863 nodes, 50 m, UTM 14N WGS84, depth mSS negative down);
well surface coordinates from the well header CSV (wells_ops_reserves_notes.md §1.1); TEC-10 target X 707,589.60 Y 2,262,253.10 (masterlog);
top El Abra from the formation-tops table / GLJ YE2019 map; TEC-12 surface and bottom-hole from the Feb 2021 completion programme
(seismic_findings.md §5), prognosed top -2,296 mSS. Vertical wells are tied at their surface location. TEC-11 is posted from its directional
survey (data/processed/tec11/facies_along_hole.csv, offsets from the TEC-11 surface location) and compared with the grid along hole
(data/processed/seismic/tec11_vs_grid.csv).
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INK = "#0b0b0b"; INK2 = "#52514e"; GRID = "#e4e3df"; SURF = "#fcfcfb"
g = pd.read_csv(ROOT / "data/raw/seismic/ElAbraXYZJan2019_GRE.csv")
xs, ys = np.sort(g.X.unique()), np.sort(g.Y.unique())
Z = g.pivot_table(index="Y", columns="X", values="Depth").reindex(index=ys, columns=xs).values
def sample(x, y):  # bilinear on the 50 m lattice
    i = np.searchsorted(xs, x) - 1; j = np.searchsorted(ys, y) - 1
    tx = (x - xs[i]) / (xs[i + 1] - xs[i]); ty = (y - ys[j]) / (ys[j + 1] - ys[j])
    z = Z[j:j + 2, i:i + 2]
    return float(z[0, 0] * (1 - tx) * (1 - ty) + z[0, 1] * tx * (1 - ty) + z[1, 0] * (1 - tx) * ty + z[1, 1] * tx * ty)
# well, x, y, top El Abra mSS (negative), basis
wells = [("TEC-6", 707493.99, 2262529.05, -2294.1, "tops table"), ("TEC-9", 707833.50, 2262336.31, -2295.9, "GLJ map"),
         ("TEC-2", 707586.77, 2262986.35, -2301.6, "tops table"), ("TEC-7", 707945.70, 2262705.90, -2304.0, "tops table"),
         ("TEC-10", 707589.60, 2262253.10, -2309.7, "tops table, at target"), ("TEC-101", 707336.30, 2262779.00, -2334.0, "GLJ map; logs -2,334"),
         ("TEC-3", 707858.90, 2263433.11, -2372.6, "tops table"), ("TEC-5", 706443.52, 2263588.88, -2551.0, "GLJ map")]
rows = []
for w, x, y, top, basis in wells:
    gz = sample(x, y); rows.append(dict(well=w, x=x, y=y, top_mss=top, grid_mss=round(gz, 1), mistie_m=round(top - gz, 1), basis=basis))
t12 = dict(sx=707582.0, sy=2262425.0, bx=707754.0, by=2262460.0, prog=-2296.0)
rows.append(dict(well="TEC-12 BHL (plan)", x=t12["bx"], y=t12["by"], top_mss=t12["prog"], grid_mss=round(sample(t12["bx"], t12["by"]), 1),
                 mistie_m=round(t12["prog"] - sample(t12["bx"], t12["by"]), 1), basis="completion programme Feb 2021"))
f11 = pd.read_csv(ROOT / "data/processed/tec11/facies_along_hole.csv")
t11 = f11.assign(x=707605.0 + f11.east_m, y=2263031.17 + f11.north_m)[["mMD", "mSS", "x", "y", "dominant"]]
t11 = t11[t11.mMD >= 1000].iloc[::5].copy()
t11["grid_mss"] = [-sample(a, b) for a, b in zip(t11.x, t11.y)]; t11["well_minus_grid_m"] = (t11.mSS - t11.grid_mss).round(1)
ties = pd.DataFrame(rows); out = ROOT / "data/processed/seismic"; out.mkdir(parents=True, exist_ok=True); ties.to_csv(out / "el_abra_grid_ties.csv", index=False)
t11.round(1).to_csv(out / "tec11_vs_grid.csv", index=False)
lt = t11[t11.mMD >= 2563]; print(f"TEC-11 lateral: well minus grid {lt.well_minus_grid_m.min()} to {lt.well_minus_grid_m.max()} m (negative = above grid top)")
print(ties.to_string(index=False))
k = np.nanargmax(Z); jy, ix = np.unravel_index(k, Z.shape); print("grid crest", xs[ix], ys[jy], Z[jy, ix])

fig, ax = plt.subplots(figsize=(10.5, 7.6), facecolor=SURF); ax.set_facecolor(SURF)
lv = np.arange(-2400, -2279, 5)
cf = ax.contourf(xs, ys, np.clip(Z, -2400, None), levels=lv, cmap="YlGnBu", extend="min")
cs = ax.contour(xs, ys, Z, levels=np.arange(-2400, -2279, 10), colors=INK2, linewidths=0.5, linestyles="solid")
ax.clabel(cs, fmt=lambda v: f"{-v:,.0f}", fontsize=7)
for lvl, c, lab in [(-2311, "#d03b3b", "-2,311 (window base / TEC-10 El Abra top)"), (-2374.2, "#2a78d6", "-2,374 lowest known oil (TEC-3)")]:
    ax.contour(xs, ys, Z, levels=[lvl], colors=c, linewidths=1.6, linestyles="solid")
    ax.plot([], [], color=c, lw=1.6, label=lab)
for r in ties.itertuples():
    if r.well.startswith("TEC-12"): continue
    ax.plot(r.x, r.y, "o", ms=6, color=INK, zorder=5)
    off = {"TEC-2": (6, -22), "TEC-9": (8, -4)}.get(r.well, (6, 5))
    ax.annotate(f"{r.well}\n{-r.top_mss:,.1f} (grid {-r.grid_mss:,.1f})", (r.x, r.y), xytext=off, textcoords="offset points", fontsize=7.5, color=INK, zorder=6)
ax.plot([707574.96, 707589.60], [2262437.07, 2262253.10], color=INK, lw=1)
ax.plot(t11.x, t11.y, color="#7a5cc4", lw=1.8, zorder=5); ax.plot(707605.0, 2263031.17, "^", ms=6, color="#7a5cc4", zorder=5)
lat = t11[t11.mMD >= 2563]; ax.plot(lat.x, lat.y, color="#7a5cc4", lw=3.2, zorder=5)
ax.annotate("TEC-11DES lateral (2,563-3,283 mMD,\n2,305-2,331 mSS: mostly 4-10 m above the grid top)", (lat.x.iloc[len(lat) // 2], lat.y.iloc[len(lat) // 2]), xytext=(14, 2), textcoords="offset points", fontsize=7.5, color="#5b3fa6", zorder=6,
            bbox=dict(boxstyle="round,pad=0.2", fc=SURF, ec="none", alpha=0.85))
ax.plot([t12["sx"], t12["bx"]], [t12["sy"], t12["by"]], color="#eb6834", lw=2.2, zorder=6)
ax.plot(t12["bx"], t12["by"], "*", ms=15, color="#eb6834", mec=INK, zorder=7)
ax.annotate(f"TEC-12 BHL (plan)\nprognosis {-t12['prog']:,.0f}, grid {-sample(t12['bx'], t12['by']):,.1f}", (t12["bx"], t12["by"]), xytext=(-150, -78), textcoords="offset points", arrowprops=dict(arrowstyle="-", color="#b5461d", lw=0.8), bbox=dict(boxstyle="round,pad=0.2", fc=SURF, ec="none", alpha=0.85), fontsize=8, color="#b5461d", weight="bold", zorder=7)
ax.plot(xs[ix], ys[jy], "+", ms=12, mew=2, color=INK); ax.annotate(f"grid crest {-Z[jy, ix]:,.1f}\n(northern culmination)", (xs[ix], ys[jy]), xytext=(-110, -6), textcoords="offset points", fontsize=7.5)
ax.set_xlim(706300, 708500); ax.set_ylim(2261700, 2264000); ax.set_aspect("equal")
ax.set_xlabel("UTM 14N X, m (WGS84)"); ax.set_ylabel("UTM 14N Y, m")
ax.ticklabel_format(useOffset=False, style="plain"); ax.tick_params(labelsize=7.5)
cb = fig.colorbar(cf, ax=ax, shrink=0.8, pad=0.02); cb.set_label("Top El Abra, m below sea level (Jan 2019 grid)"); cb.set_ticks(np.arange(-2400, -2279, 20)); cb.set_ticklabels([f"{-v:,}" for v in np.arange(-2400, -2279, 20)])
ax.legend(fontsize=7.5, loc="lower left", frameon=True, facecolor=SURF)
ax.set_title("Top El Abra depth (Jan 2019 seismic grid, 50 m): labels give well top and grid value, mSS", fontsize=10, color=INK, loc="left")
plt.tight_layout(); plt.savefig(ROOT / "figures/25_el_abra_structure.png", dpi=150, facecolor=SURF); print("figure 25 written")
