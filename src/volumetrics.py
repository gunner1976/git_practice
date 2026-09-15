"""Task 7: reconcile the 11.2 vs 7.8 MMbbl OOIP figures and give a probabilistic range.
Usage: python src/volumetrics.py
Outputs: data/processed/volumetrics/{ooip_by_source.csv, analogue_rf.csv, monte_carlo.csv, summary.json}, figures/07_volumetrics.png
"""
import json, numpy as np, pandas as pd, openpyxl
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "data/processed/volumetrics/"; BBL_PER_M3 = 6.28981; ACRE_M2 = 4046.8564224
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- 1. every OOIP in the files, with its inputs
src = [
    dict(source="IFR Summary (GLJ) sheet (all economic models 2020-2023)", file="2023-09-29 Tec-12 Economics.xlsm!Summary (GLJ) D6:D19", area_km2=630 * ACRE_M2 / 1e6, gross_m=42.269, ntg=0.40, phi=0.07, sw=0.30, bo=1.19, ooip_mmbbl=11.164, note="630 acres; the '11.2 MMbbl'"),
    dict(source="Petrel Robertson, deep contact -2374 mSS, all wells", file="Petrel Robertson Volumetrics.xlsx!B", area_km2=2.5464, gross_m=46.781, ntg=0.4271, phi=0.05558, sw=0.2000, bo=1.19, ooip_mmbbl=11.956, note="Petrel geomodel; bulk 119.1 MMm3"),
    dict(source="Petrel Robertson, TEC-10 new logs only", file="Petrel Robertson Volumetrics.xlsx!D", area_km2=2.5464, gross_m=46.781, ntg=0.4176, phi=0.06164, sw=0.1888, bo=1.299, ooip_mmbbl=12.044, note="Rsi 552 scf/bbl"),
    dict(source="Petrel Robertson, TEC-2, 9 and 10 logs", file="Petrel Robertson Volumetrics.xlsx!F", area_km2=2.5464, gross_m=46.781, ntg=0.3517, phi=0.04736, sw=0.2103, bo=1.299, ooip_mmbbl=7.589, note="same bulk rock volume, vintage-log petrophysics"),
    dict(source="CNH / PEMEX official (El Abra trend table)", file="El Abra Trend Field Analogies.xlsx row Tecolutla, cols VO_Crudo, Superficie; PEMEX Resumen table 'Volumen Original'", area_km2=3.115, gross_m=np.nan, ntg=np.nan, phi=np.nan, sw=np.nan, bo=np.nan, ooip_mmbbl=7.818, note="the '7.8 MMbbl'; 1P=2P=3P original volume 7.8; produced 1.913 to Apr 2015; RF 24.5 %; 3P EUR 2.129 (27.2 %)"),
]
for s in src:
    if not np.isnan(s["gross_m"]):
        s["ooip_recalc_mmbbl"] = s["area_km2"] * 1e6 * s["gross_m"] * s["ntg"] * s["phi"] * (1 - s["sw"]) / s["bo"] * BBL_PER_M3 / 1e6
        s["hcpv_m_per_km2"] = s["gross_m"] * s["ntg"] * s["phi"] * (1 - s["sw"])  # net oil column, m
by_source = pd.DataFrame(src); by_source.to_csv(OUT + "ooip_by_source.csv", index=False)

# ---------------------------------------------------------------- 2. El Abra trend recovery factors (CNH data to Apr 2015)
wb = openpyxl.load_workbook("data/raw/appraisal_plan/El Abra Trend Field Analogies.xlsx", read_only=True, data_only=True); rows = list(wb["Sheet1"].iter_rows(values_only=True)); wb.close()
h = [str(x) for x in rows[1]]
an = pd.DataFrame([r for r in rows[2:] if r[2] and r[0]], columns=h)
an = an.rename(columns={"CAMPO": "field", "Play2": "play", "Superficie (Km²)": "area_km2", "VO_Crudo (MMbbl)": "ooip_mmbbl", "Prod Oil (MMbbl)": "prod_mmbbl", "Oil Curr RF (%)": "rf_current", "3P EUR Oil RF (%)": "rf_3p_eur", "Oil (Vo MMbbl / km2)": "ooip_per_km2", " °API": "api", "Max of Oil Wells": "max_wells"})
an = an[["field", "play", "area_km2", "ooip_mmbbl", "prod_mmbbl", "rf_current", "rf_3p_eur", "ooip_per_km2", "api", "max_wells"]]
for c in an.columns[2:]: an[c] = pd.to_numeric(an[c], errors="coerce")
an.to_csv(OUT + "analogue_rf.csv", index=False)
rim = an[(an.play == "Reef Rim") & (an.ooip_mmbbl > 0)]
rf_stats = dict(n_fields=int(len(an)), n_reef_rim=int(len(rim)),
                rf_current_all_median=float(an.rf_current.median()), rf_current_all_mean=float(an.rf_current.mean()),
                rf_current_all_weighted=float(an.prod_mmbbl.sum() / an.ooip_mmbbl.sum()),
                rf_current_rim_median=float(rim.rf_current.median()), rf_current_rim_weighted=float(rim.prod_mmbbl.sum() / rim.ooip_mmbbl.sum()),
                rf_3p_rim_median=float(rim.rf_3p_eur.median()), rf_3p_rim_p10_p90=[float(rim.rf_3p_eur.quantile(0.9)), float(rim.rf_3p_eur.quantile(0.1))],
                rf_3p_rim_max=float(rim.rf_3p_eur.max()), ooip_per_km2_rim_median=float(rim.ooip_per_km2.median()), tecolutla_ooip_per_km2=2.51)

# ---------------------------------------------------------------- 3. Monte Carlo on the field OOIP
N = 20000
tri = lambda lo, mode, hi: rng.triangular(lo, mode, hi, N)
area = tri(2.40, 2.55, 3.12)          # km2: IFR/PR 2.55 (630 ac), CNH surface 3.1
gross = tri(40.0, 44.0, 47.0)          # m: 42.3 (IFR) to 46.8 (PR)
ntg = tri(0.30, 0.40, 0.45)            # PR 0.35-0.43, IFR 0.40
phi = tri(0.045, 0.060, 0.075)         # PR 0.047-0.062, IFR 0.07
sw = tri(0.18, 0.25, 0.35)             # PR 0.19-0.21, IFR 0.30, PEMEX logs 35-65 % in poorer zones
bo = tri(1.19, 1.25, 1.30)             # PEMEX 1.19, PR/IHS 1.28-1.30
ooip = area * 1e6 * gross * ntg * phi * (1 - sw) / bo * BBL_PER_M3 / 1e6
mc = pd.DataFrame(dict(area_km2=area, gross_m=gross, ntg=ntg, phi=phi, sw=sw, bo=bo, ooip_mmbbl=ooip)); mc.to_csv(OUT + "monte_carlo.csv", index=False)
p90, p50, p10 = np.percentile(ooip, [10, 50, 90])
# sensitivity (swing of P50 when each input runs its low/high with the rest at mode)
mode = dict(area=2.55, gross=44.0, ntg=0.40, phi=0.060, sw=0.25, bo=1.25)
def ooip_of(**k):
    d = {**mode, **k}; return d["area"] * 1e6 * d["gross"] * d["ntg"] * d["phi"] * (1 - d["sw"]) / d["bo"] * BBL_PER_M3 / 1e6
base = ooip_of()
swing = {k: (ooip_of(**{k: lo}), ooip_of(**{k: hi})) for k, (lo, hi) in dict(area=(2.40, 3.12), gross=(40, 47), ntg=(0.30, 0.45), phi=(0.045, 0.075), sw=(0.35, 0.18), bo=(1.30, 1.19)).items()}

# ---------------------------------------------------------------- 4. produced and remaining
np_rec = 1.715; np_alloc = 1.936 + 0.039   # MMbbl: task 4 recorded to Dec 2022; By Zone Mar 2020 + sales after
rem = {}
for lab, N_ in [("CNH 7.8", 7.818), ("MC P90", p90), ("MC P50", p50), ("MC P10", p10), ("IFR 11.2", 11.164), ("PR 12.0", 11.956)]:
    rem[lab] = {f"RF {int(rf*100)}%": round(N_ * rf - np_alloc, 2) for rf in (0.25, 0.29, 0.33, 0.38)}
    rem[lab]["RF to date (alloc basis)"] = round(np_alloc / N_, 3)
summary = dict(by_source={s["source"]: round(s["ooip_mmbbl"], 2) for s in src}, monte_carlo=dict(p90=round(p90, 2), p50=round(p50, 2), p10=round(p10, 2), mean=round(float(ooip.mean()), 2)),
               mode_case=round(base, 2), swing={k: [round(a, 2), round(b, 2)] for k, (a, b) in swing.items()}, trend_rf=rf_stats,
               produced_mmbbl=dict(recorded_to_2022=np_rec, with_allocations=np_alloc), remaining_mmbbl=rem)
json.dump(summary, open(OUT + "summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1)); print(by_source[["source", "area_km2", "gross_m", "ntg", "phi", "sw", "bo", "ooip_mmbbl", "ooip_recalc_mmbbl"]].to_string())

# ---------------------------------------------------------------- 5. figure
fig, axes = plt.subplots(1, 3, figsize=(19, 6.5))
ax = axes[0]
ax.hist(ooip, bins=60, color="#9ecae1", edgecolor="none"); ax.set_xlabel("field OOIP (MMbbl)"); ax.set_ylabel("Monte Carlo count (n = 20,000)")
for v, lab, col in [(p90, f"P90 {p90:.1f}", "k"), (p50, f"P50 {p50:.1f}", "k"), (p10, f"P10 {p10:.1f}", "k")]:
    ax.axvline(v, color=col, ls="--", lw=1); ax.text(v, ax.get_ylim()[1] * 0.95, lab, rotation=90, va="top", fontsize=8)
for s, col in zip(src, ["red", "green", "green", "green", "blue"]):
    ax.axvline(s["ooip_mmbbl"], color=col, lw=1.5); ax.text(s["ooip_mmbbl"], ax.get_ylim()[1] * 0.6, f"{s['ooip_mmbbl']:.1f}", rotation=90, va="top", fontsize=8, color=col)
ax.set_title("Field OOIP, Monte Carlo (blue CNH 7.8; red IFR 11.2; green Petrel Robertson)", fontsize=9)
ax = axes[1]
labs = list(swing.keys()); lo = [swing[k][0] - base for k in labs]; hi = [swing[k][1] - base for k in labs]
order = np.argsort([abs(a) + abs(b) for a, b in zip(lo, hi)])
ax.barh([labs[i] for i in order], [lo[i] for i in order], color="#e6550d", label="input at low end"); ax.barh([labs[i] for i in order], [hi[i] for i in order], color="#31a354", label="input at high end")
ax.axvline(0, color="k", lw=0.8); ax.set_xlabel(f"change in OOIP from the mode case ({base:.1f} MMbbl)"); ax.legend(fontsize=8); ax.set_title("Which inputs move the answer", fontsize=9)
ax = axes[2]
ax.scatter(rim.ooip_mmbbl, rim.rf_current * 100, s=25, color="grey", label="El Abra reef-rim fields, RF to Apr 2015 (CNH)")
ax.scatter(rim.ooip_mmbbl, rim.rf_3p_eur * 100, s=25, marker="^", color="#756bb1", label="same fields, 3P EUR RF")
t = an[an.field == "Tecolutla"].iloc[0]
ax.scatter([t.ooip_mmbbl], [t.rf_current * 100], s=120, color="blue", zorder=5, label=f"Tecolutla, CNH basis: 7.8 MMbbl, {t.rf_current*100:.0f} %")
ax.scatter([11.164], [np_alloc / 11.164 * 100], s=120, color="red", zorder=5, label=f"Tecolutla, IFR basis: 11.2 MMbbl, {np_alloc/11.164*100:.0f} %")
ax.set_xscale("log"); ax.set_xlabel("field OOIP (MMbbl, CNH)"); ax.set_ylabel("oil recovery factor (%)"); ax.set_ylim(0, 60); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=7.5, loc="upper left")
ax.axhline(rf_stats["rf_current_rim_median"] * 100, color="grey", ls=":", lw=1); ax.text(0.02, rf_stats["rf_current_rim_median"] * 100 + 1, f"reef-rim median RF to date {rf_stats['rf_current_rim_median']*100:.0f} %", fontsize=8, color="grey")
ax.set_title("Recovery factors on the El Abra trend (45 fields)", fontsize=9)
plt.tight_layout(); plt.savefig("figures/07_volumetrics.png", dpi=140); print("figure written")
