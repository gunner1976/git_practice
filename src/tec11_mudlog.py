"""Task 3: parse the Rise Energy TEC-11DES mud log (cuttings, 5 m) and post it against the
directional survey. Usage: python src/tec11_mudlog.py
Outputs: data/processed/tec11/mudlog_intervals.csv, facies_along_hole.csv, facies_summary.csv,
         figures/03_tec11_lateral_facies.png
"""
import re, sys, json
import numpy as np, pandas as pd
import pymupdf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PDF = "data/raw/geology/Tec-11 DES Sample Descriptions/Tecolutla-11Des Columna Litologica 40-3283 MD.pdf"
SURVEY = "data/raw/geology/Directional Survey/TECOLUTLA DIRECTIONAL SURVEY DATA.CSV"
OUT = "data/processed/tec11/"

# ---------------------------------------------------------------- 1. text -> intervals
doc = pymupdf.open(PDF)
lines = []
for p in doc:
    lines += p.get_text().split("\n")
skip = re.compile(r"^(Page \d+ of|RIG:|SE-836|MUD LOGGING|WELL NAME|LOCATION:|TECOLUTLA-2$|DRILL CUTTINGS|DATE:|DEC 4|INTERVAL:|INTERV:|%$|DESCRIPCION|LITHOLOGIC DESC|\s*RISE ENERGY|SURFACE LOGGING|www\.)")
lines = [l.rstrip() for l in lines if l.strip() and not skip.match(l.strip())]
ivl = re.compile(r"^(\d{2,4})(?:\s*-\s*(\d{2,4}))?$")
pct = re.compile(r"^[\d\s,\-]+$")
recs, i, last_top = [], 0, 0
def is_interval(line):
    m = ivl.match(line.strip())
    if not m:
        return None
    top = int(m.group(1)); base = int(m.group(2)) if m.group(2) else None
    if top < last_top or (base is not None and base < top):
        return None  # a percentage line such as "90-10" or "100", not a depth
    return top, base
while i < len(lines):
    iv = is_interval(lines[i])
    if not iv:
        i += 1; continue
    top, base = iv; last_top = top
    i += 1
    p = []
    # the line(s) right after an interval are percentages, even when they look like depths ("100", "90-10")
    while i < len(lines) and pct.match(lines[i].strip()):
        p += [int(x) for x in re.findall(r"\d+", lines[i])]
        i += 1
    desc = []
    while i < len(lines) and not is_interval(lines[i]):
        desc.append(lines[i].strip()); i += 1
    text = " ".join(desc)
    # Spanish half runs up to the first English lithology keyword
    cut = re.search(r"\b(SHALE|MUDSTONE ?- ?WACKE?STONE ?,? ?WHITE|MUDSTONE AND WACK|MUDSTONE IN PART|WACKE?STONE IN PART|WACKE?STONE ?-? ?GRAINSTONE OF|GRAINSTONE ?-? ?WACKE?STONE (WHITE|LIGHT|CREAM|BROWN)|GRAINSTONE (WHITE|LIGHT|CREAM|BROWN|OF)|WACKE?STONE,? (WHITE|LIGHT|CREAM|BROWN)|BENTONITE (WHITE|LIGHT|GREEN)|GRAVLE|SANDSTONE LIGHT|MUDSTONE, WHITE|MUDSTONE WHITE|PACKSTONE LIGHT|LIMESTONE)\b", text)
    es = text[:cut.start()] if cut else text
    en = text[cut.start():] if cut else ""
    recs.append({"top_mMD": top, "base_mMD": base, "pcts": p, "es": es.strip(), "en": en.strip()})

# make intervals contiguous: single-depth samples run to the next top
for k, r in enumerate(recs):
    if r["base_mMD"] is None:
        r["base_mMD"] = recs[k + 1]["top_mMD"] if k + 1 < len(recs) else r["top_mMD"] + 5
    if r["base_mMD"] <= r["top_mMD"]:
        r["base_mMD"] = recs[k + 1]["top_mMD"] if k + 1 < len(recs) else r["top_mMD"] + 1
    # close gaps between successive samples (cuttings every 5 m; description applies until next sample)
    if k + 1 < len(recs) and recs[k + 1]["top_mMD"] > r["base_mMD"]:
        r["base_mMD"] = recs[k + 1]["top_mMD"]

# ---------------------------------------------------------------- 2. classify
CARB = re.compile(r"GRAINSTONE|PACKSTONE|WACKE?STONE|MUDSTON")
OTHER = [(r"LUTITA", "shale"), (r"ARENISCA", "sandstone"), (r"BENTONITA", "bentonite"), (r"PEDERNAL", "chert"),
         (r"GRAVILLA", "gravel"), (r"CEMENTO", "cement")]
TRACE = re.compile(r"^(TRAZAS?|ESPORADIC[OA]S?|ESCAS[OA]S?|NOTA)", re.I)

def carbonate_class(ph):
    """Dunham texture of one cuttings phrase. Mixed textures keep the mud logger's word order:
    the first-named texture is taken as dominant ('WACKESTONE EN PARTE GRAINSTONE' -> wackestone-grainstone)."""
    g = re.search(r"GRAINSTONE", ph); mw = re.search(r"WACKE?STONE|MUDSTON", ph); pk = re.search(r"PACKSTONE", ph)
    if g and mw:
        return "grainstone-wackestone" if g.start() < mw.start() else "wackestone-grainstone"
    if g:
        return "grainstone"
    if pk:
        return "packstone"
    if mw:
        return "mudstone-wackestone"
    return None

def components(es):
    """Lithology classes in order of first mention in the Spanish description, trace phrases dropped.
    Within a phrase the class is the keyword that appears first."""
    phrases = re.split(r"(?<=[\.\;])\s+|\s+(?=TRAZAS DE|ESPORADICOS FRAGMENTOS|ESPORADICAS|NOTA:)", es)
    out = []
    for ph in phrases:
        ph = ph.strip()
        if not ph or TRACE.match(ph):
            continue
        hits = [(m.start(), cls) for rx, cls in OTHER for m in [re.search(rx, ph)] if m]
        c = CARB.search(ph)
        if c:
            hits.append((c.start(), carbonate_class(ph)))
        if hits:
            cls = min(hits)[1]
            if cls not in out:
                out.append(cls)
    return out

GRAIN = ["grainstone", "grainstone-wackestone", "wackestone-grainstone"]
rows = []
for r in recs:
    comps = components(r["es"])
    p = r["pcts"]
    # normalise percentage list: "90-95-5-10" style ranges -> midpoints
    if len(p) == 2 * len(comps) and len(comps) > 1 and sum(p) > 110:
        p = [(p[2 * j] + p[2 * j + 1]) / 2 for j in range(len(comps))]
    if not comps:
        comps = ["unclassified"]
    if not p:
        p = [100]  # percentage line missing in the PDF text; dominant = first-named lithology (flagged in pct_raw)
    if len(p) < len(comps):
        p = p + [0] * (len(comps) - len(p))
    if len(p) > len(comps):
        p = p[:len(comps)]
    tot = sum(p) or 100
    share = {c: 100 * v / tot for c, v in zip(comps, p)}
    dom = max(share, key=share.get)
    es_up = r["es"].upper()
    show = ("good" if re.search(r"BUENA IMPREGNACION|REGULAR IMPREGNACION|MODERADA IMPREGNACION", es_up)
            else "poor" if re.search(r"POBRE IMPREGNACION", es_up)
            else "scarce" if re.search(r"ESCASA IMPREGNACION", es_up)
            else "none")
    rows.append({"top_mMD": r["top_mMD"], "base_mMD": r["base_mMD"], "thickness_m": r["base_mMD"] - r["top_mMD"],
                 "pct_raw": " ".join(str(x) for x in r["pcts"]) or "MISSING", "components": "|".join(comps),
                 "dominant": dom, "dominant_pct": round(share[dom], 1),
                 "grainstone_pct": round(sum(share.get(c, 0) for c in GRAIN), 1),
                 "mudwack_pct": round(share.get("mudstone-wackestone", 0), 1),
                 "oil_show": show, "fluorescence": bool(re.search("FLUORESCENCIA", es_up)),
                 "vuggy": bool(re.search("VUGULAR|CAVERN", es_up)), "cement_contaminated": bool(re.search("CEMENTO", es_up)),
                 "description_es": r["es"], "description_en": r["en"]})
mud = pd.DataFrame(rows)
mud.to_csv(OUT + "mudlog_intervals.csv", index=False)

# ---------------------------------------------------------------- 3. survey
sv = pd.read_csv(SURVEY)
sv = sv[sv.UWI == "TEC-11DES"].sort_values("MD").reset_index(drop=True)
md = sv.MD.values; tvd = sv.TVD.values; tvdss = sv.TVDSS.values; inc = sv.DIP.values
ns = sv.NSOFFSET.values; ew = sv.EWOFFSET.values
def at(x, arr): return np.interp(x, md, arr)

# 1 m along-hole sampling
grid = np.arange(40, 3283, 1.0) + 0.5
g = pd.DataFrame({"mMD": grid, "mTVD": at(grid, tvd), "mSS": -at(grid, tvdss), "inclination_deg": at(grid, inc),
                  "north_m": at(grid, ns), "east_m": at(grid, ew)})
g["vs_m"] = np.hypot(g.north_m, g.east_m)  # horizontal displacement from surface location
cls = np.full(len(grid), "unclassified", dtype=object); gpct = np.zeros(len(grid)); mwpct = np.zeros(len(grid)); shw = np.full(len(grid), "none", dtype=object)
for r in mud.itertuples():
    m = (grid >= r.top_mMD) & (grid < r.base_mMD)
    cls[m] = r.dominant; gpct[m] = r.grainstone_pct; mwpct[m] = r.mudwack_pct; shw[m] = r.oil_show
g["dominant"] = cls; g["grainstone_pct"] = gpct; g["mudwack_pct"] = mwpct; g["oil_show"] = shw
g.to_csv(OUT + "facies_along_hole.csv", index=False)

# ---------------------------------------------------------------- 4. summaries
carb_top = mud[(mud.grainstone_pct + mud.mudwack_pct) >= 50].top_mMD.min()
lat_top = float(md[np.argmax(inc >= 80)])  # first station at >= 80 deg
segs = {"whole carbonate section (dominant carbonate, from %d mMD)" % carb_top: g.mMD >= carb_top,
        "build section in carbonate (< 80 deg)": (g.mMD >= carb_top) & (g.inclination_deg < 80),
        "lateral (>= 80 deg, from %.0f mMD)" % lat_top: g.mMD >= lat_top}
summ = []
for name, m in segs.items():
    sub = g[m]
    d = {"segment": name, "length_m": len(sub)}
    for c in ["grainstone", "grainstone-wackestone", "wackestone-grainstone", "packstone", "mudstone-wackestone", "shale", "sandstone", "bentonite", "unclassified"]:
        d[f"{c}_m_dominant"] = int((sub.dominant == c).sum())
    d["grainstone_bearing_m_dominant"] = int(sub.dominant.isin(GRAIN).sum())
    d["grainstone_m_pct_weighted"] = round(float(sub.grainstone_pct.sum() / 100), 1)
    d["mudwack_m_pct_weighted"] = round(float(sub.mudwack_pct.sum() / 100), 1)
    for s in ["good", "poor", "scarce", "none"]:
        d[f"show_{s}_m"] = int((sub.oil_show == s).sum())
    d["mSS_min"] = round(sub.mSS.min(), 1); d["mSS_max"] = round(sub.mSS.max(), 1)
    summ.append(d)
summ = pd.DataFrame(summ); summ.to_csv(OUT + "facies_summary.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(summ.T.to_string())
print("\ncarbonate top (dominant) mMD", carb_top, "at", round(at(carb_top, tvd), 1), "mTVD,", round(-at(carb_top, tvdss), 1), "mSS; lateral from", lat_top, "mMD")
print(mud[mud.top_mMD >= 2330][["top_mMD", "base_mMD", "pct_raw", "components", "dominant", "dominant_pct", "oil_show"]].to_string())
json.dump({"carb_top_mMD": float(carb_top), "carb_top_mSS": float(-at(carb_top, tvdss)), "lateral_top_mMD": lat_top,
           "td_mMD": float(md.max()), "td_mSS": float(-tvdss[-1]), "max_inc": float(inc.max()),
           "lateral_mSS_range": [float(g[g.mMD >= lat_top].mSS.min()), float(g[g.mMD >= lat_top].mSS.max())]}, open(OUT + "summary.json", "w"), indent=1)

# ---------------------------------------------------------------- 5. figure
COL = {"grainstone": "#f1c40f", "grainstone-wackestone": "#f7dc6f", "wackestone-grainstone": "#a9cce3", "packstone": "#f5b041", "mudstone-wackestone": "#2e86c1", "shale": "#7f8c8d",
       "sandstone": "#d7bde2", "bentonite": "#a9dfbf", "chert": "#333", "gravel": "#ccc", "cement": "#eee", "unclassified": "white"}
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 1, height_ratios=[1.6, 1.0, 0.9], hspace=0.35)
# (a) vertical section coloured by facies
ax = fig.add_subplot(gs[0])
sub = g[g.mMD >= 2100]
for c in COL:
    m = sub.dominant == c
    if m.any():
        ax.scatter(sub.vs_m[m], sub.mSS[m], s=14, color=COL[c], edgecolor="none", label=c, zorder=3)
ax.plot(sub.vs_m, sub.mSS, color="k", lw=0.6, zorder=2)
ax.set_xlabel("Horizontal displacement from TEC-2 surface location (m), azimuth ~316-330°")
ax.set_ylabel("Depth (m subsea, TVDSS)"); ax.set_ylim(2345, 2060)
ax.set_title("TEC-11DES: mud-log dominant lithology posted on the directional survey (Rise Energy cuttings at 5 m, 4 Dec 2018; survey CSV 27 Jan 2019)")
for perf, lab in [(2308, "TEC-6/TEC-9 highest perforations -2,308 to -2,319 mSS (review v3 §5)"), (2319, None)]:
    ax.axhline(perf, color="red", lw=0.8, ls="--")
    if lab: ax.text(sub.vs_m.min() + 5, perf - 3, lab, color="red", fontsize=8)
for mmd in [2360, 2500, 2727, 3000, 3283]:
    x, y = at(mmd, np.hypot(ns, ew)), -at(mmd, tvdss)
    ax.annotate(f"{mmd} mMD", (x, y), xytext=(0, 10 if mmd in (2500, 2727) else -14), textcoords="offset points", fontsize=7.5, ha="center")
ax.legend(loc="upper right", fontsize=8, ncol=2, title="dominant lithology of cuttings sample")
ax.grid(alpha=0.3)
ax.text(0.01, 0.03, "vertical exaggeration ~3x; TVD interpolated linearly between survey stations", transform=ax.transAxes, fontsize=7.5, color="dimgrey")
# (b) along-hole strip: facies with percentages, inclination, shows
ax2 = fig.add_subplot(gs[1])
lat = g[g.mMD >= 2100]
for c in COL:
    m = lat.dominant == c
    if m.any():
        ax2.bar(lat.mMD[m], 100, width=1.0, color=COL[c], edgecolor="none")
ax2.plot(lat.mMD, lat.grainstone_pct, color="#b7950b", lw=1.2, label="grainstone-bearing % of sample")
ax2.plot(lat.mMD, lat.mudwack_pct, color="#1f618d", lw=1.2, label="mudstone-wackestone % of sample")
ax2.set_ylim(0, 100); ax2.set_ylabel("% of cuttings sample")
ax2b = ax2.twinx(); ax2b.plot(lat.mMD, lat.inclination_deg, color="k", lw=1, ls="-.", label="inclination (deg)")
ax2b.set_ylim(0, 100); ax2b.set_ylabel("inclination (deg)")
for s, col in [("poor", "orange"), ("scarce", "grey"), ("good", "green")]:
    m = lat.oil_show == s
    if m.any():
        ax2.scatter(lat.mMD[m], np.full(m.sum(), 96), s=6, color=col, marker="|", label=f"oil impregnation: {s}")
ax2.set_xlabel("Measured depth (mMD)"); ax2.set_xlim(2100, 3290)
ax2.axvline(lat_top, color="k", lw=0.8); ax2.text(lat_top + 5, 50, f"lateral (>=80°) from {lat_top:.0f} mMD", fontsize=8, rotation=90, va="center")
ax2.axvline(carb_top, color="k", lw=0.8); ax2.text(carb_top + 5, 50, f"carbonate dominant from {carb_top} mMD", fontsize=8, rotation=90, va="center")
h1, l1 = ax2.get_legend_handles_labels(); h2, l2 = ax2b.get_legend_handles_labels()
ax2.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7, ncol=3)
ax2.set_title("Along-hole: dominant lithology (colour), grainstone and mudstone-wackestone share of each 5 m cuttings sample, inclination, oil shows", fontsize=10)
# (c) bar summary
ax3 = fig.add_subplot(gs[2])
cats = ["grainstone", "grainstone-wackestone", "wackestone-grainstone", "mudstone-wackestone", "shale", "bentonite", "unclassified"]
xx = np.arange(len(cats)); w = 0.38
lat_row = summ.iloc[2]; carb_row = summ.iloc[0]
ax3.bar(xx - w / 2, [carb_row[f"{c}_m_dominant"] for c in cats], w, label=f"{carb_row.segment} ({carb_row.length_m} m)", color="#aaa")
ax3.bar(xx + w / 2, [lat_row[f"{c}_m_dominant"] for c in cats], w, label=f"{lat_row.segment} ({lat_row.length_m} m)", color="#444")
for i, c in enumerate(cats):
    ax3.text(i - w / 2, carb_row[f"{c}_m_dominant"] + 5, f"{carb_row[f'{c}_m_dominant']}", ha="center", fontsize=8)
    ax3.text(i + w / 2, lat_row[f"{c}_m_dominant"] + 5, f"{lat_row[f'{c}_m_dominant']}", ha="center", fontsize=8)
ax3.set_xticks(xx); ax3.set_xticklabels([c.replace("-", "-\n") for c in cats], fontsize=8); ax3.set_ylabel("metres along hole (dominant lithology)")
ax3.legend(fontsize=8); ax3.grid(axis="y", alpha=0.3)
ax3.set_title(f"Metres by dominant lithology. Percentage-weighted: lateral grainstone-bearing {lat_row.grainstone_m_pct_weighted} m, mudstone-wackestone {lat_row.mudwack_m_pct_weighted} m of {lat_row.length_m} m", fontsize=10)
plt.savefig("figures/03_tec11_lateral_facies.png", dpi=150, bbox_inches="tight")
print("figure written")
