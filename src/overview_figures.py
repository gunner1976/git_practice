"""Task 19: figures for the technical overview deck.
Usage: .venv/bin/python src/overview_figures.py -> figures/22_interval_ladder.png, figures/23_field_opex.png
Sources: perforation depths on one datum (docs/09_log_panel.md §3), top El Abra picks (GLJ YE2019 map and the
cross-section panels, data/processed/deck_notes/geology_geophysics_notes.md), 2019 test results (Tonalli operations
log 1PawcesN and the Sep 2022 Jaguar deck 1974i04r), monthly field opex (accounting_notes.md Appendix A) and the
Sep 2020 cost sheet (Tonalli Op Cost 290920.xlsx, FX 21 MXN/USD).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; FIG = ROOT / "figures"
INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#9a9a95"; GRID = "#e4e3df"; SURF = "#fcfcfb"
PAL = {"TEC-2": "#2a78d6", "TEC-6": "#eb6834", "TEC-7": "#1baf7a", "TEC-9": "#eda100", "TEC-10": "#e87ba4"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2})

# ---------------- figure 22: producing intervals by well, on one datum -----------------
# (well, top_mss, base_mss, label, kind) ; kind: prod (produced oil), last (last/current interval), wet (tested water), lateral
iv = [
    ("TEC-6", 2330, 2332, "1956-72", "prod"), ("TEC-6", 2318, 2321, "1972-76", "prod"), ("TEC-6", 2308, 2310, "1976-2006", "last"),
    ("TEC-2", 2341, 2345, "1956 test only", "prod"), ("TEC-2", 2331, 2335, "1956-57", "prod"), ("TEC-2", 2303, 2307, "1972-2016\n2018-20", "last"),
    ("TEC-2", 2315, 2316, "add-perf 2019", "last"),
    ("TEC-7", 2330, 2332, "1957", "prod"), ("TEC-7", 2305, 2308, "1971-2006; 100 % water 2019", "last"),
    ("TEC-9", 2323, 2328, "1973-2012, 353 kbbl", "last"),
    ("TEC-10", 2314.3, 2318, "2018-22, oil cut 30-60 %", "last"),
]
tops = {"TEC-6": 2294, "TEC-9": 2296, "TEC-2": 2301, "TEC-7": 2304, "TEC-10": 2308.5}
order = ["TEC-6", "TEC-9", "TEC-2", "TEC-7", "TEC-10", "TEC-11", "TEC-12"]
x = {w: i for i, w in enumerate(order)}
fig, ax = plt.subplots(figsize=(11.5, 6.2), facecolor=SURF); ax.set_facecolor(SURF)
ax.axhspan(2294, 2311, color="#e9eef7", zorder=0)
ax.text(x["TEC-11"], 2294.6, "TEC-12 target window 2,294-2,311 mSS\n(never produced except the top 4 m\nof TEC-2's interval)", ha="center", va="top", fontsize=8, color=INK2)
for w, t, b, lab, k in iv:
    c = PAL[w]; a = 1.0 if k == "last" else 0.45
    ax.add_patch(Rectangle((x[w] - 0.16, t), 0.32, b - t, color=c, alpha=a, lw=0, zorder=3))
    ax.text(x[w] + 0.21, (t + b) / 2, lab, va="center", fontsize=7.5, color=INK2, zorder=4)
for w, t in tops.items():
    ax.plot([x[w] - 0.24, x[w] + 0.24], [t, t], color=INK, lw=2, zorder=4)
# TEC-11 lateral: 2,305-2,331 mSS, mostly 2,322-2,324; 100 % water
ax.add_patch(Rectangle((x["TEC-11"] - 0.08, 2305), 0.16, 26, fill=False, ec=MUTED, lw=1, ls=(0, (2, 2)), zorder=3))
ax.add_patch(Rectangle((x["TEC-11"] - 0.16, 2322), 0.32, 2, color=MUTED, lw=0, zorder=3))
ax.text(x["TEC-11"], 2333, "720 m lateral 2,305-2,331 mSS\n(mostly 2,322-2,324);\n100 % water, 2019", ha="center", va="top", fontsize=7.5, color=INK2)
# TEC-12 plan
ax.annotate("", xy=(x["TEC-12"], 2311), xytext=(x["TEC-12"], 2294), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
ax.text(x["TEC-12"], 2314, "TEC-12 (planned)\ncrest, 3-17 m above TEC-10;\nlog, test, then perforate;\nfallback 2,311-2,332 mSS", ha="center", va="top", fontsize=7.5, color=INK)
ax.set_xticks(range(len(order))); ax.set_xticklabels(order, fontsize=9.5, color=INK)
ax.set_xlim(-0.6, len(order) - 0.25); ax.set_ylim(2350, 2288)
ax.set_ylabel("Depth, m subsea (mSS)")
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_title("Producing intervals by well on one datum. Black bar = top El Abra; solid = last/current interval; faded = earlier intervals; wells ordered crest to flank", fontsize=9, color=INK, loc="left")
fig.tight_layout(); fig.savefig(FIG / "22_interval_ladder.png", dpi=170, facecolor=SURF); plt.close(fig)

# ---------------- figure 23: monthly field opex -----------------
months = ["Sep-18", "Oct-18", "Nov-18", "Dec-18", "Jan-19", "Feb-19", "Mar-19", "Apr-19", "May-19", "Jun-19", "Jul-19", "Aug-19", "Sep-19", "Oct-19", "Nov-19", "Dec-19"]
opex = [67530, 80000, 72000, 68604, 68145, 59365, 62812, 53596, 69117, 83409, 81906, 80736, 73034, 61291, 70097, 75544]
fig, ax = plt.subplots(figsize=(11.5, 4.6), facecolor=SURF); ax.set_facecolor(SURF)
xs = list(range(len(months)))
ax.bar(xs, [v / 1e3 for v in opex], width=0.7, color=PAL["TEC-2"], lw=0)
gx = len(months) + 1
ax.bar([gx], [28.155], width=0.7, color=PAL["TEC-2"], lw=0, hatch="///", edgecolor=SURF)
ax.text(gx, 28.155 + 2, "28", ha="center", fontsize=8.5, color=INK)
ax.text(xs[9], 83.4 + 2, "83", ha="center", fontsize=8.5, color=INK)
for xi, y, lab in [(11, 84, "TEC-7 disposal on;\nwater trucking ends"), (12, 100, "TEC-2\nshut in"), (14, 73, "TEC-10 to TEC-2\nflowline"), (15, 90, "separator bought;\nrental ends Mar-20")]:
    ax.text(xi, y, lab, ha="center", va="bottom", fontsize=7.5, color=INK2)
ax.set_xticks(xs + [gx]); ax.set_xticklabels(months + ["Sep-20\nrun-rate"], fontsize=8, rotation=0)
ax.set_ylim(0, 115); ax.set_ylabel("Field operating cost, USD thousand per month")
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_title("Field opex, monthly actuals Sep 2018 - Dec 2019 and the Sep 2020 cost sheet (excludes G&A and regulatory costs)", fontsize=9, color=INK, loc="left")
fig.tight_layout(); fig.savefig(FIG / "23_field_opex.png", dpi=170, facecolor=SURF); plt.close(fig)
print("figures 22-23 written")
