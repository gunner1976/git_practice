"""Task 2 (part 2): curated diff matrix and lineage chart from the econ_lineage extraction.
Usage: python src/econ_lineage_matrix.py
Reads data/processed/econ_lineage/*.csv, writes diff_matrix.csv, diff_matrix.md and
figures/02_econ_model_lineage.png. All money USD as labelled in the workbooks.
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

D = "data/processed/econ_lineage/"
models = pd.read_csv(D + "models.csv").set_index("tag")
res = pd.read_csv(D + "results.csv").set_index("tag")
prices = pd.read_csv(D + "prices.csv").set_index("tag")
wells = pd.read_csv(D + "wells.csv")
hdr = pd.read_csv(D + "diff_matrix_header.csv").set_index("key")
TAGS = list(models.index)

def hv(label, tag):
    v = hdr.loc[label, tag] if label in hdr.index else None
    return None if (v is None or (isinstance(v, float) and np.isnan(v))) else v

def active_wells(tag):
    w = wells[(wells.tag == tag) & (wells.cos > 0)]
    return "; ".join(f"{r.well.replace('Tecolutla', 'Tec').strip()} {r.forecast_start[:7]} qi{r.qi_bpd:g}" for r in w.itertuples())

rows = []
def add(param, unit, fn, source):
    rows.append({"parameter": param, "unit": unit, **{t: fn(t) for t in TAGS}, "source": source})

add("File (internal last-modified, UTC)", "", lambda t: str(models.loc[t, "modified"])[:16] if isinstance(models.loc[t, "modified"], str) else "not stored", "docProps/core.xml")
add("Sheets", "", lambda t: models.loc[t, "sheets"].count("|") + 1, "workbook")
add("Evaluation / economic start", "date", lambda t: hv("Evaluation Start Date", t), "Model!B8:B9")
add("Inflation", "fraction/yr", lambda t: hv("Inflation Rate (%)", t), "Model!B12")
add("WTI deck", "USD/bbl", lambda t: f"{prices.loc[t,'wti_m1']:g} {prices.loc[t,'price_deck_note']}" if prices.loc[t, "price_deck_note"] == "flat" else f"{prices.loc[t,'price_deck_note']}: {prices.loc[t,'wti_m1']:g}, {prices.loc[t,'wti_m13']:g}, {prices.loc[t,'wti_m25']:g}, {prices.loc[t,'wti_m37']:g} ...", "Model!row 412")
add("Field price factor (PEMEX/WTI)", "fraction", lambda t: prices.loc[t, "field_price_factor"], "Model!D428")
add("Field price, month 1", "USD/bbl", lambda t: round(prices.loc[t, "field_m1"], 2), "Model!K428")
add("Bid-round royalty", "fraction", lambda t: 0.3122, "outputs!B3")
add("Battery fixed cost", "USD/month", lambda t: hv("Battery Costs (US$/mth)", t), "Model!E15")
add("Oil well fixed cost", "USD/well/month", lambda t: hv("Oil Well Costs (US$/well/mth)", t), "Model!E16")
add("Well intervention cost", "USD/well/month", lambda t: hv("Well Intervention Costs (US$/well/mth)", t), "Model!E17 (v6+)")
add("Oil variable cost", "USD/bbl", lambda t: -7.25, "Model!H15")
add("Water disposal", "USD/bbl", lambda t: -3.25, "Model!H16")
add("Active wells (COS>0): start, qi", "", active_wells, "Model!A25:L44")
add("TEC-12 slot: IP in window", "bbl/d", lambda t: round(res.loc[t, "slot4_ip_bpd"], 1), "Model!row 107")
add("TEC-12 slot: oil in window (economic)", "bbl", lambda t: int(res.loc[t, "slot4_oil_econ_bbl"]), "Model!row 107 x flag")
add("Capital inside evaluation window", "USD", lambda t: int(res.loc[t, "capital_in_window_usd"]), "Model!rows 509-568")
add("Capital lines in window", "", lambda t: res.loc[t, "capital_lines_in_window"], "Model!rows 509-568")
add("Dated capital excluded (before window)", "", lambda t: res.loc[t, "capital_lines_dated_before_window"] if isinstance(res.loc[t, "capital_lines_dated_before_window"], str) else "", "Model!rows 509-568")
add("Economic life", "years", lambda t: round(res.loc[t, "econ_life_yr_econ"], 2), "Model!I505 (check3)")
add("Oil, economic", "bbl", lambda t: int(res.loc[t, "oil_bbl_econ"]), "Model!I403")
add("Sales gas, economic", "mcf", lambda t: int(res.loc[t, "gas_mcf_econ"]), "Model!I404")
add("Water, economic", "bbl", lambda t: int(res.loc[t, "water_bbl_econ"]), "Model!I409")
add("Revenue, economic", "USD", lambda t: int(res.loc[t, "revenue_econ"]), "Model!I454")
add("Royalties, economic", "USD", lambda t: int(res.loc[t, "royalties_econ"]), "Model!I483")
add("Opex, economic", "USD", lambda t: int(res.loc[t, "opex_econ"]), "Model!I500")
add("Total capital incl. abandonment", "USD", lambda t: int(res.loc[t, "capital_total"]), "Model!J574")
add("NOI before tax", "USD", lambda t: int(res.loc[t, "noi_btax_total"]), "Model!J578")
add("IRR before tax (cached)", "fraction/yr", lambda t: res.loc[t, "irr_btax"], "Model!I578")
add("NPV10 before tax", "USD", lambda t: int(res.loc[t, "npv10_btax_total"]), "Model!J580")
add("NPV10 after tax", "USD", lambda t: int(res.loc[t, "npv10_atax_total"]), "Model!J590")
add("outputs 'Active' NPV10", "kUSD", lambda t: round(res.loc[t, "outputs_active_npv10_musd"], 1), "outputs!F13")
add("outputs 'Active' capital", "kUSD", lambda t: res.loc[t, "outputs_active_capital_musd"], "outputs!H13")

mat = pd.DataFrame(rows)
mat.to_csv(D + "diff_matrix.csv", index=False)
with open(D + "diff_matrix.md", "w") as f:
    f.write("| Parameter | Unit | " + " | ".join(TAGS) + " | Source |\n|" + "---|" * (len(TAGS) + 3) + "\n")
    for r in rows:
        f.write(f"| {r['parameter']} | {r['unit']} | " + " | ".join(str(r[t]) if r[t] is not None else "" for t in TAGS) + f" | {r['source']} |\n")
print(mat[["parameter"] + TAGS].to_string())

# ---------------- lineage chart -------------------------------------------------------
# Lineage edges are inferred from (a) internal last-modified order, (b) shared content
# (identical results / profiles) — documented in docs/02_econ_lineage.md.
nodes = {
    "2020-08": ("Aug 2020\nTrans. plan", "2020-08-15", 0),
    "2022-v3": ("v3\nApr 11 18:08", "2022-04-11", 1),
    "2022-v2": ("v2\nApr 11 18:10", "2022-04-11", 2),
    "2022-v1": ("v1\nApr 11 18:11", "2022-04-11", 3),
    "2022-v5": ("v5 (HZ)\nApr 12", "2022-04-12", 4),
    "2022-v4": ("v4 (Tec12&13)\nJun 17 00:37", "2022-06-17", 5),
    "2022-v6": ("v6 (12-15)\nJun 17 21:26", "2022-06-17", 6),
    "2022-v7": ("v7 (12-15)\nJun 20", "2022-06-20", 7),
    "2022-v8": ("v8 (Tec14 HZ)\nJun 21 14:45", "2022-06-21", 8),
    "2022-v9": ("v9 (Tec14 HZ)\nJun 21 18:17", "2022-06-21", 9),
    "2023-10": ("Sep/Oct 2023\nTEC-12 econ", "2023-10-24", 10),
}
edges = [("2020-08", "2022-v3"), ("2022-v3", "2022-v2"), ("2022-v2", "2022-v1"), ("2022-v3", "2022-v5"),
         ("2022-v3", "2022-v4"), ("2022-v4", "2022-v6"), ("2022-v6", "2022-v7"), ("2022-v7", "2022-v8"),
         ("2022-v8", "2022-v9"), ("2020-08", "2023-10")]
labels = {("2020-08", "2022-v3"): "start Apr 2022; WTI 30→90; factor 0.95→0.801;\nTEC-12 + TEC-13 on (1.55 MM each)",
          ("2022-v3", "2022-v2"): "gas sales removed", ("2022-v2", "2022-v1"): "TEC-13 Feb→Jun 2023",
          ("2022-v3", "2022-v5"): "one 684 bbl/d HZ at 3.0 MM\ninstead of TEC-12 + TEC-13", ("2022-v3", "2022-v4"): "HZ→VT labels;\nDecline sheet (CNH plan)",
          ("2022-v4", "2022-v6"): "start Jul 2023; GLJ Apr-22 deck; 2%/yr infl.;\nTEC-12/13 capital now sunk; +TEC-14/15, TEC-2, power",
          ("2022-v6", "2022-v7"): "opex split only\n(NPV unchanged)", ("2022-v7", "2022-v8"): "TEC-14/15 VT → one\n547 bbl/d HZ at 3.0 MM",
          ("2022-v8", "2022-v9"): "HZ gas fixed", ("2020-08", "2023-10"): "start Jan 2024; WTI 85 flat; factor 0.90;\nTEC-10 qi 80; TEC-12 re-entry 1.8 MM; profile sheet unchanged"}

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(16, 11), gridspec_kw={"height_ratios": [1.4, 1]})
pos = {"2020-08": (0, 1), "2022-v3": (1, 1), "2022-v2": (2, 1), "2022-v1": (3, 1), "2022-v5": (2, -0.1),
       "2022-v4": (2, 2.2), "2022-v6": (3, 2.2), "2022-v7": (4, 2.2), "2022-v8": (5, 2.2), "2022-v9": (6, 2.2),
       "2023-10": (6, 0)}
stamp = {t: (str(models.loc[t, "modified"])[:16].replace("T", " ") if isinstance(models.loc[t, "modified"], str) else "no internal stamp") for t in TAGS}
short = {"2020-08": "Aug 2020 transition-plan model", "2022-v3": "Feb 2022 (3)", "2022-v2": "Feb 2022 (2)", "2022-v1": "Feb 2022 (no suffix)",
         "2022-v5": "Feb 2022 (5) HZ", "2022-v4": "Feb 2022 (4) Tec12 & Tec13", "2022-v6": "Feb 2022 (6) Tec12-15",
         "2022-v7": "Feb 2022 (7) Tec12-15", "2022-v8": "Feb 2022 (8) Tec14 HZ", "2022-v9": "Feb 2022 (9) Tec14 HZ", "2023-10": "2023-09-29 Tec-12 Economics"}
for t, (xx, yy) in pos.items():
    col = "#d62728" if not t.startswith("2022") else "#1f77b4"
    ax.add_patch(plt.Rectangle((xx - 0.42, yy - 0.28), 0.84, 0.56, fc="white", ec=col, lw=2, zorder=3))
    ax.text(xx, yy + 0.1, short[t], ha="center", va="center", fontsize=8.5, weight="bold", zorder=4)
    ax.text(xx, yy - 0.1, f"saved {stamp[t]}\nNPV10 {res.loc[t,'npv10_btax_total']/1e6:.1f} MM", ha="center", va="center", fontsize=7.5, zorder=4)
offs = {("2020-08", "2022-v3"): (0.3, 0.48), ("2022-v3", "2022-v2"): (0, -0.32), ("2022-v2", "2022-v1"): (0, -0.32),
        ("2022-v3", "2022-v5"): (0.1, -0.28), ("2022-v3", "2022-v4"): (-0.45, 0.05), ("2022-v4", "2022-v6"): (0, 0.44),
        ("2022-v6", "2022-v7"): (0, -0.32), ("2022-v7", "2022-v8"): (0, 0.44), ("2022-v8", "2022-v9"): (0, -0.32),
        ("2020-08", "2023-10"): (1.0, 0.18)}
for a_, b_ in edges:
    (x1, y1), (x2, y2) = pos[a_], pos[b_]
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, color="grey", lw=1.2, zorder=2,
                                 shrinkA=28, shrinkB=28))
    dx, dy = offs[(a_, b_)]
    ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, labels[(a_, b_)], fontsize=7, color="dimgrey", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9), zorder=5)
ax.set_xlim(-0.6, 6.6); ax.set_ylim(-0.7, 3.0); ax.axis("off")
ax.set_title("Tecolutla IFR economic model lineage, Aug 2020 to Oct 2023. Edges inferred from internal save stamps and shared content; "
             "file suffixes 3, 2, (none) run backwards in time. Blue: Feb 2022 series. Red: TEC-12 workbooks.", fontsize=10)
# bottom: NPV10 BTAX and TEC-12 economic oil per version
npv = res.loc[TAGS, "npv10_btax_total"] / 1e6
t12 = res.loc[TAGS, "slot4_oil_econ_bbl"] / 1e3
xx = np.arange(len(TAGS))
b1 = ax2.bar(xx - 0.2, npv, 0.4, label="NPV10 before tax, whole model (MM USD, left)", color="#1f77b4")
ax2b = ax2.twinx()
b2 = ax2b.bar(xx + 0.2, t12, 0.4, label="TEC-12 slot oil inside window (kbbl, right)", color="#ff7f0e")
ax2.set_xticks(xx); ax2.set_xticklabels(TAGS, rotation=0, fontsize=9)
ax2.set_ylabel("NPV10 before tax (MM USD)"); ax2b.set_ylabel("TEC-12 economic oil (kbbl)")
for i, t in enumerate(TAGS):
    ax2.text(i - 0.2, npv[t] + 0.2, f"{npv[t]:.1f}", ha="center", fontsize=8)
    ax2b.text(i + 0.2, t12[t] + 8, f"{t12[t]:.0f}", ha="center", fontsize=8, color="#b35900")
ax2.legend(handles=[b1, b2], loc="upper left", fontsize=8); ax2.set_ylim(-1.5, 23); ax2b.set_ylim(-35, 520)
ax2.set_title("Headline results as saved (cached values). NPV covers the whole well programme of each version, not TEC-12 alone; v6-v9 exclude sunk TEC-12/13 capital.", fontsize=9)
ax2.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("figures/02_econ_model_lineage.png", dpi=150)
print("figure written")
