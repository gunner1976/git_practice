"""Figures and tables for the block and development history deck (task 16).

Outputs:
  data/processed/wells/casing_strings.csv   casing / liner / plug / perforation table with provenance
  figures/18_wellbore_schematics.png        nine wellbore schematics, depth mMD below KB
  figures/19_well_histories.png             per-well monthly oil and water rate, six producers
  figures/20_block_timeline.png             1956-2024 block chronology
  figures/21_funding_and_cash.png           partner funding, revenue and cash by year (accounting notes)
Sources: data/raw/geology CSVs (well header, perforations), PEMEX estados mecanicos and Halliburton
post-operative reports read from the Drive (ids in data/processed/deck_notes/drive_reads_notes.md),
data/processed/tecolutla_production.csv (task 4).
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"; OUT = ROOT / "data/processed/wells"; OUT.mkdir(parents=True, exist_ok=True)
SURF = "#fcfcfb"; INK = "#0b0b0b"; INK2 = "#52514e"; GRID = "#e6e5e1"
PAL = {"TEC-2": "#2a78d6", "TEC-6": "#eb6834", "TEC-7": "#1baf7a", "TEC-9": "#eda100", "TEC-10": "#e87ba4", "TEC-11": "#008300",
       "TEC-3": "#9a9a95", "TEC-5": "#9a9a95", "TEC-101": "#9a9a95"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2})

# ---------------- casing / completion table -----------------
# columns: well, item (conductor|surface|intermediate|production|liner|open_hole|tubing|packer|plug|perf), od_in, weight_lbft, grade,
#          top_mmd, base_mmd, status, source
rows = [
 # TEC-2 (1956 discovery well). Casing strings not stated in any package source (Tonalli 2019 estado mecanico is a drawing only).
 ("TEC-2","perf",None,None,None,2307.4,2311,"active 2019","Tecolutla Perforations Information.csv"),
 ("TEC-2","plug",None,None,None,2330,2331,"bridge plug","Tecolutla Perforations Information.csv"),
 ("TEC-2","perf",None,None,None,2335,2339,"squeezed","Tecolutla Perforations Information.csv"),
 ("TEC-2","plug",None,None,None,2341,2342,"bridge plug","Tecolutla Perforations Information.csv"),
 ("TEC-2","perf",None,None,None,2345,2349,"squeezed","Tecolutla Perforations Information.csv"),
 ("TEC-2","perf",None,None,None,2353,2354,"squeezed","Tecolutla Perforations Information.csv"),
 ("TEC-2","perf",None,None,None,2019,2020,"2019 RTG 1 11/16 in shallow shot (interval per Tonalli 2019 estado mecanico text)","TON_estado_mecanico_tec_2_20190219.pdf (1RxpD0jw)"),
 ("TEC-2","td",None,None,None,0,2375,"TD","Tecolutla Well Header Information.csv"),
 ("TEC-2","casing_unknown",None,None,None,0,2375,"casing strings not in the package (G-54)","-"),
 # TEC-3 (1956, salt water, plugged)
 ("TEC-3","open_hole",None,None,None,2376.8,2380.8,"open hole","Tecolutla Perforations Information.csv"),
 ("TEC-3","td",None,None,None,0,2381,"TD; plugged 1956 (salt water)","Well header CSV; TEC-6 informe final"),
 ("TEC-3","casing_unknown",None,None,None,0,2381,"casing strings not in the package (G-54)","-"),
 # TEC-5 (1956, structurally low, plugged)
 ("TEC-5","surface",9.625,36,"J-55",0,501.35,"cemented","BLOQUE_TECOLUTLA_5_ESTADO_MECANICO.pdf (1VCktsVx)"),
 ("TEC-5","open_hole",8.625,None,None,501.35,2562.1,"open hole 8 5/8 in, plugged 28 Jul 1956","BLOQUE_TECOLUTLA_5_ESTADO_MECANICO.pdf"),
 ("TEC-5","plug",None,None,None,477.8,525,"cement plug","BLOQUE_TECOLUTLA_5_ESTADO_MECANICO.pdf"),
 ("TEC-5","plug",None,None,None,2505.3,2562.1,"cement plug","BLOQUE_TECOLUTLA_5_ESTADO_MECANICO.pdf"),
 ("TEC-5","td",None,None,None,0,2562.1,"TD","BLOQUE_TECOLUTLA_5_INFORME_FINAL.PDF"),
 # TEC-6 (1956)
 ("TEC-6","surface",9.625,None,None,0,499.5,"cemented","TECOLUTLA_6_INFORME_FINAL.pdf (1c2-WKxk)"),
 ("TEC-6","production",6.625,None,None,0,2280,"cemented","TECOLUTLA_6_INFORME_FINAL.pdf"),
 ("TEC-6","liner",4.5,None,None,2302,2336,"liner","TECOLUTLA_6_INFORME_FINAL.pdf"),
 ("TEC-6","tubing",2.875,None,None,0,2280,"2 3/8 and 2 7/8 in (1956)","TECOLUTLA_6_INFORME_FINAL.pdf"),
 ("TEC-6","plug",None,None,None,2303,2304,"bridge plug","Tecolutla Perforations Information.csv"),
 ("TEC-6","perf",None,None,None,2314,2316,"squeezed","Tecolutla Perforations Information.csv"),
 ("TEC-6","perf",None,None,None,2320,2321,"squeezed","Tecolutla Perforations Information.csv"),
 ("TEC-6","perf",None,None,None,2324,2327,"squeezed","Tecolutla Perforations Information.csv"),
 ("TEC-6","perf",None,None,None,2336,2338,"open hole (1956 initial interval)","Perforations CSV; TEC-6 informe final"),
 ("TEC-6","td",None,None,None,0,2338.9,"TD","TECOLUTLA_6_INFORME_FINAL.pdf"),
 # TEC-7 (1957)
 ("TEC-7","surface",9.625,36,"J-55",0,600.48,"cemented","Anexo 3 estado mecanico final tec-7.pdf (11Wasndd)"),
 ("TEC-7","production",6.625,20,"J-55/N-80 20-24",0,2306.5,"cemented","Anexo 3 estado mecanico final tec-7.pdf"),
 ("TEC-7","liner",4.5,11.6,"J-55",2281,2340,"liner","Anexo 3 estado mecanico final tec-7.pdf"),
 ("TEC-7","tubing",2.375,None,"EUE",0,2300,"2 3/8 in tubing + 4.5 in mechanical packer at ~2,300 m (2019 water-injection string)","Anexo 3 estado mecanico final tec-7.pdf"),
 ("TEC-7","perf",None,None,None,2310,2313,"active (last interval)","Perforations CSV; estado mecanico 2019"),
 ("TEC-7","plug",None,None,None,2325,2325.5,"permanent plug","Anexo 3 estado mecanico final tec-7.pdf"),
 ("TEC-7","plug",None,None,None,2330,2330.5,"mechanical plug","BLOQUE_TECOLUTLA_7_ESTADO_MECANICO.pdf (1UZlBMHq)"),
 ("TEC-7","perf",None,None,None,2335,2337,"squeezed / below plug","Perforations CSV; estado mecanico"),
 ("TEC-7","td",None,None,None,0,2340,"TD","Well header CSV"),
 # TEC-9 (1973)
 ("TEC-9","surface",9.625,36,"J-55",0,502,"cemented","BLOQUE_TECOLUTLA_9_ESTADO_MECANICO.PDF (1ys9wOiU)"),
 ("TEC-9","production",6.625,28,"P-110",0,2340,"cemented","BLOQUE_TECOLUTLA_9_ESTADO_MECANICO.PDF"),
 ("TEC-9","tubing",2.875,None,None,0,2318,"2 7/8 in to 2,318 m + 2 3/8 in","BLOQUE_TECOLUTLA_9_ESTADO_MECANICO.PDF"),
 ("TEC-9","perf",None,None,None,2328,2333,"squeezed (closed Jan 1999; monument)","Perforations CSV; estado mecanico"),
 ("TEC-9","td",None,None,None,0,2340,"TD; deviated from 296 m, 11 deg, 112 m displacement","BLOQUE_TECOLUTLA_9_ESTADO_MECANICO.PDF"),
 # TEC-101 (1972)
 ("TEC-101","surface",9.625,40,"N-80",0,807.19,"cemented","BLOQUE_TECOLUTLA_101_ESTADO_MECANICO.pdf (1a00morB)"),
 ("TEC-101","open_hole",8.625,None,None,807.19,2804,"open hole; fish at 926 m; water-invaded, plugged 31 Mar 1972","BLOQUE_TECOLUTLA_101_ESTADO_MECANICO.pdf"),
 ("TEC-101","perf",None,None,None,2718,2804,"open-hole interval, squeezed","Tecolutla Perforations Information.csv"),
 ("TEC-101","td",None,None,None,0,2804,"TD","BLOQUE_TECOLUTLA_101_ESTADO_MECANICO.pdf"),
 # TEC-10DES (2018)
 ("TEC-10","conductor",13.375,None,None,0,30,"cemented 11 Apr 2018","POST OPERATIVO TEC-10 13 3/8 @ 30 m (1EV-1L__)"),
 ("TEC-10","surface",9.625,32.3,"H-40 STC",0,470,"cemented to surface 16 Apr 2018","POST OPERATIVO TEC-10 TR 9 5/8 @ 470 m (1_5UzGZI)"),
 ("TEC-10","production",7.0,26,"L-80",0,2285,"cemented to surface 27 Apr 2018","POSTOPERATIVO TEC-10 TR 7 (16_dQsnw)"),
 ("TEC-10","liner",4.5,11.6,"L-80 (test report: 13.5 P-110)",2133.42,2489.33,"cemented 4 May 2018","POST OPERATIVO TEC-10 LN 4 1/2 @ 2489 m (10f2RlOT)"),
 ("TEC-10","tubing",2.375,None,"L-80 EUE",0,2057,"2 3/8 in tubing, packer at 2,057 m (ESTADO MECANICO FINAL Jul 2019, well unnamed)","ESTADO MECANICO FINAL.pdf (1HUjuDEt)"),
 ("TEC-10","perf",None,None,None,2349.5,2350.5,"active","Tecolutla Perforations Information.csv"),
 ("TEC-10","perf",None,None,None,2351.5,2353,"active","Tecolutla Perforations Information.csv"),
 ("TEC-10","perf",None,None,None,2394.5,2398.5,"inactive","Tecolutla Perforations Information.csv"),
 ("TEC-10","perf",None,None,None,2404,2406,"inactive","Tecolutla Perforations Information.csv"),
 ("TEC-10","perf",None,None,None,2410,2414,"inactive","Tecolutla Perforations Information.csv"),
 ("TEC-10","perf",None,None,None,2433.5,2442.5,"active per CSV; injectivity test Jun 2018 admitted at 2,120 psi","Perforations CSV; Prueba de Admision (1XyZ35a9)"),
 ("TEC-10","td",None,None,None,0,2490,"TD (J-shape, ~20 deg at TD)","Well header CSV; QMAX mud report"),
 # TEC-11DES (2018)
 ("TEC-11","surface",9.625,None,None,0,472,"proposal depth 472/500 m; post-operative report not read","PROPUESTA VF TEC-11 TR 9 5/8 @ 472 m (1o4iHKGh)"),
 ("TEC-11","production",7.0,26,None,0,2354.44,"cemented 24-25 Nov 2018, returns to surface","TEC-11 DES TR 7 Reporte Post Operativo (1CL89Fst)"),
 ("TEC-11","liner",4.5,13.5,None,2354.44,3283,"4 1/2 in liner in the lateral (liner run design 1Fk1BJgP); tubing-less","Tecolutla 11_Corrida_V1_Liner 4.5.xlsm; Fideicomiso 2024"),
 ("TEC-11","plug",None,None,None,2400,2401,"Boss composite plug set Aug 2019; 100 % water","Anexo 4 aviso abandono temporal (18kU9Zb7)"),
 ("TEC-11","perf",None,None,None,2624,2806,"ten proposed 2 m intervals 2,624-2,806 mMD (never produced oil)","Tecolutla Perforations Information.csv"),
 ("TEC-11","td",None,None,None,0,3283,"TD mMD (2,331 mTVD)","Well header CSV; Fideicomiso 2024"),
]
cas = pd.DataFrame(rows, columns=["well","item","od_in","weight_lbft","grade","top_mmd","base_mmd","status","source"])
kb = {"TEC-2":4.0,"TEC-3":6.0,"TEC-5":4.0,"TEC-6":5.67,"TEC-7":5.0,"TEC-9":5.07,"TEC-101":8.0,"TEC-10":6.13,"TEC-11":4.70}
cas["kb_m"] = cas.well.map(kb)
cas.to_csv(OUT / "casing_strings.csv", index=False)

# ---------------- figure 18: schematics -----------------
order = ["TEC-2","TEC-3","TEC-5","TEC-6","TEC-7","TEC-9","TEC-101","TEC-10","TEC-11"]
fig, axes = plt.subplots(1, 9, figsize=(16, 7.2), sharey=True, facecolor=SURF)
for ax, w in zip(axes, order):
    ax.set_facecolor(SURF); d = cas[cas.well == w]
    td = float(d[d["item"] == "td"].base_mmd.iloc[0])
    for _, r in d.iterrows():
        it = r["item"]
        if it in ("conductor","surface","intermediate","production"):
            hw = r.od_in / 2 * 0.09
            ax.add_patch(Rectangle((-hw, r.top_mmd), 2 * hw, r.base_mmd - r.top_mmd, fill=False, lw=1.4, ec=INK))
            ax.text(hw + 0.03, r.base_mmd, f'{r.od_in:g}"', va="center", fontsize=6.5, color=INK2)
        elif it == "liner":
            hw = r.od_in / 2 * 0.09
            ax.add_patch(Rectangle((-hw, r.top_mmd), 2 * hw, r.base_mmd - r.top_mmd, fill=False, lw=1.4, ec=INK, ls="-"))
            ax.text(hw + 0.03, r.top_mmd, f'{r.od_in:g}" liner', va="center", fontsize=6.5, color=INK2)
        elif it == "open_hole":
            hw = (r.od_in or 8.5) / 2 * 0.09
            ax.add_patch(Rectangle((-hw, r.top_mmd), 2 * hw, r.base_mmd - r.top_mmd, fill=False, lw=1, ec=INK2, ls=(0, (2, 2))))
        elif it == "casing_unknown":
            ax.add_patch(Rectangle((-0.3, 0), 0.6, r.base_mmd, fill=False, lw=1, ec=INK2, ls=(0, (1, 3))))
            ax.text(0, r.base_mmd * 0.45, "casing\nnot in\npackage", ha="center", fontsize=6.5, color=INK2)
        elif it == "tubing":
            ax.plot([0, 0], [0, r.base_mmd], color=INK2, lw=0.8)
        elif it == "perf":
            c = PAL[w] if "active" in r.status and "inactive" not in r.status else "#9a9a95"
            ax.add_patch(Rectangle((-0.42, r.top_mmd), 0.84, max(r.base_mmd - r.top_mmd, 1.0), color=c, alpha=0.9, lw=0))
        elif it == "plug":
            ax.add_patch(Rectangle((-0.28, r.top_mmd), 0.56, max(r.base_mmd - r.top_mmd, 4), color=INK, lw=0))
    ax.set_xlim(-0.75, 0.9); ax.set_ylim(td + 120, -60)
    ax.set_xticks([]); ax.set_title(f"{w}\nKB {kb[w]:.2f} m, TD {td:,.0f} mMD", fontsize=8)
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
axes[0].set_ylabel("Depth, m MD below KB")
fig.suptitle("Wellbore schematics, Tecolutla field (colour = active perforations; grey = squeezed/inactive; black = plugs; dotted = open hole or unknown casing). Depth to scale, diameters not.", fontsize=9, color=INK)
fig.tight_layout(); fig.savefig(FIG / "18_wellbore_schematics.png", dpi=170, facecolor=SURF); plt.close(fig)

# ---------------- figure 19: per-well histories -----------------
p = pd.read_csv(ROOT / "data/processed/tecolutla_production.csv", parse_dates=["date"])
p = p[p.well != "FIELD"]
wells = ["TEC-6","TEC-2","TEC-7","TEC-9","TEC-10","FIELD"]
pf = pd.read_csv(ROOT / "data/processed/tecolutla_production.csv", parse_dates=["date"])
fig, axes = plt.subplots(3, 2, figsize=(14, 8.4), facecolor=SURF, sharex=False)
for ax, w in zip(axes.ravel(), wells):
    ax.set_facecolor(SURF)
    src = pf[(pf.well == "FIELD") & (pf.date >= "2020-01-01")] if w == "FIELD" else p[p.well == w]
    d = src.groupby("date")[["oil_bbl","water_bbl","days_in_month"]].sum().sort_index()
    idx = pd.date_range(d.index.min(), d.index.max(), freq="MS"); d = d.reindex(idx)
    dim = d.index.days_in_month
    ax.plot(d.index, d.oil_bbl / dim, color="#2a78d6", lw=1.4, label="oil, bbl/d (calendar-day)")
    ax.plot(d.index, d.water_bbl / dim, color="#eb6834", lw=1.2, label="water, bbl/d")
    cum = d.oil_bbl.fillna(0).cumsum().iloc[-1]
    lab = "Field, commingled sales (trucking tickets and PEMEX statements)" if w == "FIELD" else w
    ax.set_title(f"{lab}: {d.index.min():%b %Y} to {d.index.max():%b %Y}, {cum/1e3:,.0f} kbbl oil in the monthly record", fontsize=8.5, loc="left")
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.set_ylim(bottom=0)
axes[0,0].legend(frameon=False, fontsize=7, loc="upper right")
axes[1,0].set_ylabel("Monthly-average rate, bbl/d"); 
fig.suptitle("Per-well production histories from the reconciled database (task 4): CNH monthly 1966-2016, Tonalli 2018-19. Gaps are missing months, not zeros. TEC-6 wellfile allocation of 388 kbbl (pre-1966) not shown; TEC-11 produced water only (May-Aug 2019).", fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "19_well_histories.png", dpi=170, facecolor=SURF); plt.close(fig)

# ---------------- figure 20: timeline -----------------
events = [
 ("1956-05", "TEC-2 discovery, 1956; TEC-3 (salt water) and TEC-5 (low) dry", "drilling"),
 ("1956-10", "TEC-6 completed, El Abra top 2,296 mSS", "drilling"),
 ("1957-01", "TEC-7 completed", "drilling"),
 ("1964-12", "Static surveys TEC-2/7: 24.4-24.7 MPa", "reservoir"),
 ("1966-01", "CNH monthly record begins (TEC-2, 6, 7)", "production"),
 ("1972-03", "TEC-101 water-invaded, plugged", "drilling"),
 ("1973-05", "TEC-9 completed, 2,328-2,333 m", "drilling"),
 ("1999-01", "TEC-9 closed", "production"),
 ("2006-12", "TEC-6 last production", "production"),
 ("2012-07", "TEC-9 last record", "production"),
 ("2016-01", "PEMEX era ends: TEC-2 last CNH month; field shut in", "production"),
 ("2016-03", "CNH-R01-L03-A24/2016 licence to Tonalli Energia (IFR / Grupo Idesa)", "regulatory"),
 ("2017-05", "Plan de Evaluacion filed; 3D reprocessing (PSTM/PSDM)", "regulatory"),
 ("2018-03", "TEC-2 static gradient after 2 yr shut-in: 24.16 MPa", "reservoir"),
 ("2018-04", "TEC-10DES drilled (11 Apr-4 May), cored, logged, tested", "drilling"),
 ("2018-08", "TEC-10 build-up p* 24.14 MPa at 2,300 mSS", "reservoir"),
 ("2018-11", "TEC-11DES horizontal drilled (11 Nov-18 Dec); 100 % water", "drilling"),
 ("2019-08", "TEC-11 plugged (composite plug 2,400 m); TEC-2 shut in Sep 2019", "production"),
 ("2019-09", "PEMEX factoring stalls; cash shortfall USD 1.55 MM", "corporate"),
 ("2020-07", "PEP early-production sales contract (21 Jul); Programa de Transicion rejected (7 Aug)", "regulatory"),
 ("2022-02", "Informe de Evaluacion rejected; field shut in 4 Feb 2022", "regulatory"),
 ("2022-07", "CNH approves Programa de Transicion (18 Jul)", "regulatory"),
 ("2022-08", "Idesa exits; Jaguar buys 50 % for USD 850 k (25 Aug)", "corporate"),
 ("2024-03", "Abandonment trust reserve USD 411 k; cash calls 2024", "corporate"),
]
lanes = {"drilling": 0, "production": 1, "reservoir": 2, "regulatory": 3, "corporate": 4}
lane_col = {"drilling": "#2a78d6", "production": "#eb6834", "reservoir": "#1baf7a", "regulatory": "#eda100", "corporate": "#e87ba4"}
fig = plt.figure(figsize=(16, 7.6), facecolor=SURF)
ax = fig.add_axes([0.05, 0.56, 0.93, 0.40]); ax.set_facecolor(SURF)
for i, (dt, txt, cat) in enumerate(events, 1):
    x = pd.Timestamp(dt + "-01"); y = lanes[cat]
    ax.plot([x], [y], "o", color=lane_col[cat], ms=13, mec=SURF, mew=1.5)
    ax.text(x, y, str(i), ha="center", va="center", fontsize=6.5, color="white", fontweight="bold")
for cat, y in lanes.items():
    ax.axhline(y, color=GRID, lw=0.8, zorder=0); ax.text(pd.Timestamp("1954-06-01"), y, cat, va="center", ha="right", fontsize=8, color=INK2)
ax.set_yticks([]); ax.set_ylim(-0.7, 4.7); ax.set_xlim(pd.Timestamp("1950-01-01"), pd.Timestamp("2026-06-01"))
for s in ("top","right","left"): ax.spines[s].set_visible(False)
ax.set_title("Block chronology 1956-2024 (sources: PEMEX well reports, CNH database, Tonalli regulatory and corporate files; details in the deck notes)", fontsize=9, loc="left")
half = (len(events) + 1) // 2
for col, chunk in enumerate((events[:half], events[half:])):
    for j, (dt, txt, cat) in enumerate(chunk):
        n = j + 1 + col * half
        fig.text(0.05 + col * 0.48, 0.50 - j * 0.038, f"{n:>2}. {dt}  {txt}", fontsize=7.2, color=INK, family="DejaVu Sans")
fig.savefig(FIG / "20_block_timeline.png", dpi=170, facecolor=SURF); plt.close(fig)

# ---------------- figure 21: funding, revenue and cash (accounting_notes.md §3, §6, §8) -----------------
yrs = ["2016-17", "2018", "2019", "2020", "2021", "2022", "2023", "2024 (to Sep)"]
fund = [3.25, 6.9985, 2.25, np.nan, np.nan, 0.419, 1.731, 2.071]
rev = [0, 0.921, 1.732, 0.682, 0.939, 0.178, 0, 0]
cash = [0.856, 0.327, 0.422, np.nan, 0.079, 0.0063, 0.0088, 0.0176]
fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=SURF); ax.set_facecolor(SURF)
x = np.arange(len(yrs)); w = 0.38
ax.bar(x - w/2, fund, w, color="#2a78d6", label="partner contributions / loans, USD MM")
ax.bar(x + w/2, rev, w, color="#eb6834", label="gross oil revenue, USD MM")
for i, v in enumerate(fund):
    if np.isnan(v): ax.text(x[i] - w/2, 0.15, "not in\nsheets", ha="center", fontsize=7, color=INK2)
ax.plot(x, cash, "o-", color=INK, lw=1.5, ms=5, label="cash at period end, USD MM")
for i, v in enumerate(cash):
    if not np.isnan(v): ax.annotate(f"{v:.2f}" if v >= 0.05 else f"{v*1000:.0f} k", (x[i], v), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=7, color=INK)
ax.set_xticks(x); ax.set_xticklabels(yrs, fontsize=8); ax.set_ylabel("USD MM"); ax.set_ylim(0, 7.8)
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.set_title("Tonalli funding, revenue and cash, 2016-2024 (cash basis; 2020-21 contributions and 2020 cash not in the workbooks read)", fontsize=9, loc="left")
fig.tight_layout(); fig.savefig(FIG / "21_funding_and_cash.png", dpi=170, facecolor=SURF); plt.close(fig)
print("figures 18-21 written;", len(cas), "casing rows")
