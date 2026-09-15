"""Task 9: LAS correlation panel TEC-6 / TEC-2 / TEC-9 / TEC-10 / TEC-11 on a subsea datum, GR-polarity test,
and an Archie pass on TEC-10 (the only well with modern resistivity + porosity).
Usage: python src/log_panel.py
Outputs: data/processed/petrophysics/{<well>_logs_mss.csv, gr_polarity.csv, tec10_archie.csv, summary.json}, figures/09_log_panel.png
Depth: mSS = TVD below KB minus KB elevation (Tecolutla Well Header Information.csv; TEC-10 6.13 m per the survey CSV, TEC-11 4.70).
TEC-10 and TEC-11 MD->TVD from TECOLUTLA DIRECTIONAL SURVEY DATA.CSV (TEC-11 LWD file carries its own TVD). Other wells vertical.
"""
import json, warnings, numpy as np, pandas as pd, lasio
from scipy.stats import spearmanr
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
D = "data/raw/petrophysics/LAS/"; OUT = "data/processed/petrophysics/"
KB = {"TEC-2": 4.0, "TEC-6": 6.0, "TEC-9": 5.0, "TEC-10": 6.13, "TEC-11": 4.70}
L = lambda f: lasio.read(D + f, ignore_header_errors=True, engine="normal").df()
sv = pd.read_csv("data/raw/geology/Directional Survey/TECOLUTLA DIRECTIONAL SURVEY DATA.CSV")
t10s = sv[sv.UWI == "TEC_10"].sort_values("MD"); t11s = sv[sv.UWI == "TEC-11DES"].sort_values("MD")
def tvdss10(md): return -np.interp(md, t10s.MD, t10s.TVDSS)   # positive down, subsea
perf = pd.read_csv("data/raw/geology/Tecolutla Perforations/Tecolutla Perforations  Informaiton.csv").ffill()
perf["well"] = perf.LABEL.str.replace("TECOLUTLA-", "TEC-").str.replace("TEC_10", "TEC-10").str.replace("TEC-11DES", "TEC-11")
def perf_mss(w):
    p = perf[(perf.well == w) & perf.PERFTOP.notna()].copy()
    if w == "TEC-10": p["top_mss"] = tvdss10(p.PERFTOP); p["base_mss"] = tvdss10(p.PERFBASE)
    elif w == "TEC-11": p["top_mss"] = -np.interp(p.PERFTOP, t11s.MD, t11s.TVDSS); p["base_mss"] = -np.interp(p.PERFBASE, t11s.MD, t11s.TVDSS)
    else: p["top_mss"] = p.PERFTOP - KB[w]; p["base_mss"] = p.PERFBASE - KB[w]
    return p[["well", "PERFTOP", "PERFBASE", "top_mss", "base_mss", "Type and Status"]]
perfs = pd.concat([perf_mss(w) for w in ["TEC-2", "TEC-6", "TEC-9", "TEC-10", "TEC-11"]]); perfs.to_csv(OUT + "perforations_mss.csv", index=False)

wells = {}
# TEC-6, 1956 GR-neutron (count-type curves in old units)
d = L("BLOQUE_TECOLUTLA_6_GR_NEUT_100_2335.LAS"); d = d[d.index > 2200]; d["mss"] = d.index - KB["TEC-6"]
wells["TEC-6"] = dict(df=d.rename(columns={"GR": "gr", "NEUT": "neut_counts"}), gr="gr", por=None, por_is_counts="neut_counts", res=None, note="1956 GR (old scale 1-8) and neutron counts; no resistivity; high counts = low porosity")
# TEC-2: 1956 open-hole (digitised 2018) + 2019 cased-hole GR + 2018 neutron
o = L("Tecolutla 2_Original_OH_Logs.LAS"); o["mss"] = o.index - KB["TEC-2"]
g19 = L("TECOLUTLA-2_GR_CCL_2325.0m-2120m_10-FEBRERO-2019.las"); g19["mss"] = g19.index - KB["TEC-2"]
n18 = L("TECOLUTLA-2_NEUTRON_05-04-2018.las"); n18 = n18[n18.index > 2150]; n18["mss"] = n18.index - KB["TEC-2"]
wells["TEC-2"] = dict(df=o.rename(columns={"GR": "gr", "NPHI": "nphi", "LN": "res_ln", "SN": "res_sn"}), gr="gr", por="nphi", por_is_counts=None, res="res_ln", extra=dict(gr2019=g19.rename(columns={"GRCG": "gr_cps"}), n2018=n18.rename(columns={"GRGC": "gr", "NPRL": "nprl"})),
                   note="1956 open-hole GR/SP/normals + neutron porosity (digitised 2018, 2290-2372 mMD); 2019 cased-hole GR (cps) 2120-2327 mMD; 2018 neutron stops at 2286 mMD above the reservoir")
# TEC-9, 1973 resistivity/sonic/neutron
n = L("TECOLUTLA-9_RESISTIVO_SONICO_NEUTRON_2345_2000_08MAY1973P.LAS"); n = n[n.index > 2200]; n["mss"] = n.index - KB["TEC-9"]
wells["TEC-9"] = dict(df=n.rename(columns={"GR": "gr", "NEUT": "neut_counts", "ILD": "res_ild", "SPHI": "sphi"}), gr="gr", por="sphi", por_is_counts="neut_counts", res="res_ild", note="1973 GR, neutron counts, ILD, sonic porosity (sparse)")
# TEC-10, 2018 Weatherford compact triple combo
a = L("TECOLUTLA-10_LAS_2280.50m-2487.00m_02MAY2018.las"); a["mss"] = tvdss10(a.index.values)
a = a.rename(columns={"GRGC": "gr", "NPRL": "nprl", "DPRL": "dprl", "DEN": "den", "PDPE": "pe", "RILD": "res_ild", "RILM": "res_ilm"})
wells["TEC-10"] = dict(df=a, gr="gr", por="nprl", por_is_counts=None, res="res_ild", note="2018 MCG/MDN/MPD/MAI: GR, limestone neutron and density porosity, PE, deep induction; MD->TVDSS from survey")
# TEC-11, 2018 LWD (GR, sonic) in a deviated/horizontal hole
e = L("Tecolutla 11_LAS_GR_SST_3283 mMD.las"); e["mss"] = e.TVD - KB["TEC-11"]
e = e.rename(columns={"HAGRT": "gr", "DTC": "dtc"}); e["sphi_wyllie"] = ((e.dtc - 47.5) / (189 - 47.5)).clip(0, 0.4)
wells["TEC-11"] = dict(df=e, gr="gr", por="sphi_wyllie", por_is_counts=None, res=None, note="2018 LWD GR and compressional sonic (Wyllie limestone porosity here, uncalibrated); the hole is 61-90 deg so the TVDSS axis compresses 900 m of lateral into 90 m")
for w, v in wells.items():
    v["df"].to_csv(OUT + f"{w.replace('-', '')}_logs_mss.csv")
    for k, x in v.get("extra", {}).items(): x.to_csv(OUT + f"{w.replace('-', '')}_{k}_mss.csv")

# ---------------------------------------------------------------- GR polarity in the reservoir window (2,280-2,380 mSS)
pol = []
def rho(x, y):
    m = np.isfinite(x) & np.isfinite(y); return (spearmanr(x[m], y[m])[0], int(m.sum())) if m.sum() > 20 else (np.nan, int(m.sum()))
for w, v in wells.items():
    d = v["df"]; d = d[(d.mss > 2280) & (d.mss < 2380)]
    rec = dict(well=w, n=len(d))
    if v["por"]: r, k = rho(d[v["gr"]].values, d[v["por"]].values); rec["rho_gr_vs_porosity"] = round(r, 2); rec["porosity_curve"] = v["por"]
    if v["por_is_counts"]: r, k = rho(d[v["gr"]].values, -d[v["por_is_counts"]].values); rec["rho_gr_vs_minus_neutron_counts"] = round(r, 2)
    if v["res"]: r, k = rho(d[v["gr"]].values, np.log10(d[v["res"]].clip(lower=0.1)).values); rec["rho_gr_vs_log_resistivity"] = round(r, 2)
    pol.append(rec)
if "extra" in wells["TEC-2"]:
    x = wells["TEC-2"]["extra"]["n2018"]; x = x[x.mss > 2150]; r, k = rho(x.gr.values, x.nprl.values); pol.append(dict(well="TEC-2 (2018 cased-hole, 2150-2282 mSS)", n=k, rho_gr_vs_porosity=round(r, 2), porosity_curve="nprl"))
pol = pd.DataFrame(pol); pol.to_csv(OUT + "gr_polarity.csv", index=False)

# ---------------------------------------------------------------- Archie on TEC-10
RW65 = 0.075; T65 = 65.0; TRES = 98.6           # PEMEX field summary: 45,000 ppm, Rw 0.075 ohm.m at 65 C; IHS: 98.6 C at TEC-10
rw = RW65 * (T65 + 21.5) / (TRES + 21.5)         # Arps temperature correction
A_, M_, N_ = 1.0, 2.0, 2.0
t = wells["TEC-10"]["df"].copy()
t["phi"] = t[["nprl", "dprl"]].mean(axis=1).clip(lower=0.001)  # simple average of limestone neutron and density porosity
t["sw"] = np.sqrt(A_ * rw / (t.phi ** M_ * t.res_ild.clip(lower=0.1))).clip(upper=1.0)
t["sw_m1p8"] = np.sqrt(A_ * rw / (t.phi ** 1.8 * t.res_ild.clip(lower=0.1))).clip(upper=1.0)
t["pay_6_50"] = (t.phi >= 0.06) & (t.sw <= 0.5); t["pay_4_60"] = (t.phi >= 0.04) & (t.sw <= 0.6); t["por_6"] = t.phi >= 0.06
step = 0.025
t[["mss", "gr", "nprl", "dprl", "den", "pe", "res_ild", "phi", "sw", "sw_m1p8", "pay_6_50", "pay_4_60"]].to_csv(OUT + "tec10_archie.csv")
def window(top, base):
    x = t[(t.mss >= top) & (t.mss < base)]
    return dict(mss=f"{top}-{base}", md=f"{np.interp(top, -t10s.TVDSS, t10s.MD):.1f}-{np.interp(base, -t10s.TVDSS, t10s.MD):.1f}", gr_mean=round(float(x.gr.mean()), 1), phi_mean=round(float(x.phi.mean()), 3),
                res_median=round(float(x.res_ild.median()), 1), sw_mean=round(float(x.sw.mean()), 2), m_phi_ge_6pct=round(float(x.por_6.sum() * step), 1), m_pay_6_50=round(float(x.pay_6_50.sum() * step), 1), m_pay_4_60=round(float(x.pay_4_60.sum() * step), 1), thickness_m=round(base - top, 1))
zones = [window(2270, 2294), window(2294, 2311), window(2311, 2320), window(2320, 2340), window(2340, 2360), window(2360, 2400), window(2400, 2450)]
summary = dict(kb=KB, rw_ohmm_at_res_temp=round(rw, 4), archie=dict(a=A_, m=M_, n=N_, rw65=RW65, tres=TRES, note="Rw from PEMEX 45,000 ppm at 65 C corrected to 98.6 C; phi = mean of limestone neutron and density porosity; uncalibrated to core"),
               tec10_zones=zones, gr_polarity=pol.to_dict("records"), perforations=perfs.round(1).to_dict("records"),
               tec10_top_perf_mss_survey=round(float(tvdss10(2349.5)), 1), tec12_target_window_mss=[2294, 2311], by_zone_top_perf_mss=2311.5)
json.dump(summary, open(OUT + "summary.json", "w"), indent=1, default=float)
print(json.dumps(summary, indent=1, default=float)[:4500])

# ---------------------------------------------------------------- figure
ymin, ymax = 2240, 2400
fig, axes = plt.subplots(1, 11, figsize=(22, 13), sharey=True, gridspec_kw={"width_ratios": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.2]})
def norm(s, lo=5, hi=95):
    a, b = np.nanpercentile(s, lo), np.nanpercentile(s, hi); return (s - a) / (b - a)
def track(ax, x, y, label, color="k", lw=0.7, xlim=None, log=False):
    ax.plot(x, y, color=color, lw=lw); ax.set_xlabel(label, fontsize=8)
    if xlim: ax.set_xlim(*xlim)
    if log: ax.set_xscale("log")
    ax.grid(alpha=0.3); ax.tick_params(labelsize=7)
def perfbars(ax, w):
    for r in perfs[perfs.well == w].itertuples():
        col = {"ACTIVE": "red", "SQUEEZED": "grey", "OPEN HOLE": "orange", "PROPOSED": "blue", "INACTIVE": "grey", "Bridge PLUG": "black"}.get(str(r._6).strip(), "grey")
        ax.axhspan(r.top_mss, r.base_mss, xmin=0.0, xmax=0.08, color=col, alpha=0.9)
def target(ax):
    ax.axhspan(2294, 2311, color="gold", alpha=0.18)
i = 0
# TEC-6
d = wells["TEC-6"]["df"]; track(axes[i], norm(d.gr), d.mss, "TEC-6 GR\n(1956, normalised)", "g", xlim=(-0.2, 1.4)); perfbars(axes[i], "TEC-6"); target(axes[i]); i += 1
track(axes[i], norm(-d.neut_counts), d.mss, "TEC-6 neutron\n(counts, inverted = porosity)", "b", xlim=(-0.2, 1.4)); target(axes[i]); i += 1
# TEC-2
d = wells["TEC-2"]["df"]; g = wells["TEC-2"]["extra"]["gr2019"]
track(axes[i], norm(d.gr), d.mss, "TEC-2 GR 1956 OH (green)\n2019 cased GR cps (grey)", "g", xlim=(-0.2, 1.4)); axes[i].plot(norm(g.gr_cps), g.mss, color="grey", lw=0.5); perfbars(axes[i], "TEC-2"); target(axes[i]); i += 1
track(axes[i], d.nphi, d.mss, "TEC-2 NPHI 1956 (v/v)\nblue; LN ohm.m red (log)", "b", xlim=(0, 0.3)); ax2 = axes[i].twiny(); ax2.plot(d.res_ln, d.mss, color="r", lw=0.6); ax2.set_xscale("log"); ax2.set_xlim(10, 2000); ax2.tick_params(labelsize=6); target(axes[i]); i += 1
# TEC-9
d = wells["TEC-9"]["df"]; track(axes[i], d.gr, d.mss, "TEC-9 GR 1973 (API)", "g", xlim=(0, 80)); perfbars(axes[i], "TEC-9"); target(axes[i]); i += 1
track(axes[i], norm(-d.neut_counts), d.mss, "TEC-9 neutron (inv. counts,\nblue); ILD ohm.m red (log)", "b", xlim=(-0.2, 1.4)); ax2 = axes[i].twiny(); ax2.plot(d.res_ild, d.mss, color="r", lw=0.6); ax2.set_xscale("log"); ax2.set_xlim(1, 200); ax2.tick_params(labelsize=6); target(axes[i]); i += 1
# TEC-10
d = wells["TEC-10"]["df"]; track(axes[i], d.gr, d.mss, "TEC-10 GR 2018 (GAPI)", "g", xlim=(0, 300)); perfbars(axes[i], "TEC-10"); target(axes[i]); i += 1
track(axes[i], d.nprl, d.mss, "TEC-10 NPHI ls (blue), DPHI ls\n(cyan); ILD ohm.m red (log)", "b", xlim=(0, 0.3)); axes[i].plot(d.dprl, d.mss, color="c", lw=0.5); ax2 = axes[i].twiny(); ax2.plot(d.res_ild, d.mss, color="r", lw=0.6); ax2.set_xscale("log"); ax2.set_xlim(1, 1000); ax2.tick_params(labelsize=6); target(axes[i]); i += 1
track(axes[i], t.sw, t.mss, "TEC-10 Archie Sw\n(a1 m2 n2, Rw %.3f)" % rw, "k", xlim=(0, 1)); axes[i].fill_betweenx(t.mss, 0, 1, where=t.pay_6_50, color="lime", alpha=0.5); axes[i].text(0.05, 2245, "green = phi>=6%, Sw<=50%", fontsize=7); target(axes[i]); i += 1
# TEC-11
d = wells["TEC-11"]["df"]; track(axes[i], d.gr, d.mss, "TEC-11 LWD GR (API)\nvs TVDSS (deviated!)", "g", xlim=(0, 100)); perfbars(axes[i], "TEC-11"); target(axes[i]); i += 1
track(axes[i], d.sphi_wyllie, d.mss, "TEC-11 sonic porosity\n(Wyllie, uncalibrated)", "b", xlim=(0, 0.3)); target(axes[i]); i += 1
axes[0].set_ylim(ymax, ymin); axes[0].set_ylabel("depth (m subsea)")
fig.suptitle("Tecolutla El Abra correlation panel on a subsea datum. Gold band = TEC-12 target window 2,294-2,311 mSS (review v3). Left-edge bars = perforations (red active, grey squeezed/inactive, orange open hole, blue proposed). "
             "GR increases with porosity in every well (GR-polarity test, gr_polarity.csv): clean-GR intervals are the tight ones.", fontsize=9.5)
plt.tight_layout(rect=[0, 0, 1, 0.97]); plt.savefig("figures/09_log_panel.png", dpi=130); print("figure written")
