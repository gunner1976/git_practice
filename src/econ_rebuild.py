"""Task 10 support: TEC-12 single-well economics rebuilt in Python on the 2023 IFR model's fiscal and cost structure,
with the task-6 production range and the task-8 escalated AFE.
Usage: python src/econ_rebuild.py
Outputs: data/processed/econ_rebuild/{cases.csv, cashflow_base.csv, summary.json}, figures/10_econ_rebuild.png

Primary case (Oct 2026 update): GLJ Ltd. price forecast effective 1 Oct 2026 (WTI then-current, Table 1, gljpc.com Oct26.pdf),
costs inflated at GLJ's 2 %/yr from 2026, realised price 0.81 x WTI (PEMEX settlements, task 15), AFE indexed to Sep 2026 on the
US drilling PPI (G-45), and the area-based fiscal charges as actually paid in 2024-25 (G-60) charged to the stand-alone case only: they
are field-level and paid with or without TEC-12, so the incremental case (TEC-10 producing) carries none. A flat real-WTI grid is kept
as a sensitivity. A bridge from this case to GLJ's YE2025 TEC-12 1P entity (Kinjal report 25269) is written to bridge.csv and figure 24.
Royalty, tax and opex terms are the 2023 workbook's (task 1, docs/01_econ_2023.md); the 2025 reform leaves the contract terms
unchanged (LSH transitorio Décimo, G-49).
"""
import json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "data/processed/econ_rebuild/"; DPM = 30.42
prof = pd.read_csv("data/processed/forecast/tec12_profiles_monthly.csv")
afe = pd.read_csv("data/processed/afe/afe_escalated.csv").set_index("case")
P = dict(  # 2023 workbook Model (Tec-10 & Tec-12) unless noted
    bid_royalty=0.3122, basic_b0=0.00125, basic_add=0.015, surface=0.01,
    battery_fixed=10000.0, well_fixed=2500.0, disposal_fixed=1500.0, oil_var=7.25, water_var=3.25,
    tax=0.30, depr=0.25, disc=0.10, abandon=150000.0, start="2027-01-01",
    # area-based fiscal charges (G-60). As paid: LIH art. 23 contractual quota paid to the FMP in 2024 (MXN 29,829/month, at 18 MXN/USD)
    # plus the IEEH (LIH art. 55 activity tax) booked in the Tonalli P&L at USD 42.8 k (2024) and 42.7 k (2025). Statutory sensitivity:
    # quota plus the art. 55 exploration-phase rate 2,464.84 MXN/km2/month (RMF DOF 28-12-2025) on 7.16 km2. Extraction phase: art. 55
    # extraction rate 9,859.56 MXN/km2/month and no quota (art. 23 applies in the exploration phase only).
    cuota_mxn_m=29829.0, ieeh_usd_yr=42800.0, act_tax_mxn_km2_m=2464.84, act_tax_extraction_mxn_km2_m=9859.56, block_km2=7.16, mxn_usd=18.0,
    inflation=0.02, cost_base_year=2026, price_factor=0.81)
P["area_fees_usd_m"] = P["cuota_mxn_m"] / P["mxn_usd"] + P["ieeh_usd_yr"] / 12
P["area_fees_statutory_usd_m"] = (P["cuota_mxn_m"] + P["act_tax_mxn_km2_m"] * P["block_km2"]) / P["mxn_usd"]
P["area_fees_extraction_usd_m"] = P["act_tax_extraction_mxn_km2_m"] * P["block_km2"] / P["mxn_usd"]
FEES = {"as_paid": "area_fees_usd_m", "statutory": "area_fees_statutory_usd_m", "extraction": "area_fees_extraction_usd_m"}
# GLJ 1 Oct 2026, WTI Cushing, then-current USD/bbl; +2.0 %/yr after 2035
GLJ_OCT26 = {2026: 91.00, 2027: 81.00, 2028: 75.00, 2029: 73.22, 2030: 74.68, 2031: 76.18, 2032: 77.70, 2033: 79.26, 2034: 80.84, 2035: 82.46}
# GLJ 1 Jan 2026 (the deck behind GLJ's YE2025 report for Kinjal), WTI Cushing, then-current USD/bbl, Table 1, gljpc.com Jan26.pdf
GLJ_JAN26 = {2026: 59.25, 2027: 66.00, 2028: 70.00, 2029: 72.16, 2030: 73.60, 2031: 75.08, 2032: 76.58, 2033: 78.11, 2034: 79.67, 2035: 81.27}
DECKS = {"glj_oct26": GLJ_OCT26, "glj_jan26": GLJ_JAN26}
def glj_wti(year, deck="glj_oct26"):
    d = DECKS[deck]
    return d[year] if year in d else d[2035] * 1.02 ** (year - 2035)
def water_cut(m):  # TEC-10 trajectory: 0.42 first year -> 0.67 at 12 months -> ~0.85 by year 10 (task 4); explicit assumption
    return np.clip(0.40 + 0.45 * (1 - np.exp(-m / 24.0)), 0.40, 0.85)

def run(profile, capex, wti=None, deck=None, price_factor=P["price_factor"], months=360, incremental=False, fees="as_paid", q=None, over=None, npv_date=None):
    """wti: flat real price (no cost inflation); deck='glj_oct26' or 'glj_jan26': GLJ then-current prices with 2 %/yr cost inflation.
    q: custom monthly oil rate (bbl/d) in place of a named profile; over: overrides of P (costs, start); npv_date: discount to this date
    instead of the first production month."""
    P_ = {**P, **(over or {})}
    if q is None: q = prof[profile].values[:months]
    q = np.asarray(q, float)[:months]; m = np.arange(1, months + 1)
    t0 = pd.Timestamp(P_["start"]); mdate = pd.DatetimeIndex([t0 + pd.DateOffset(months=int(i)) for i in m - 1])
    year = mdate.year.values
    if deck in DECKS:
        w = np.array([glj_wti(int(y), deck) for y in year]); infl = (1 + P_["inflation"]) ** (year - P_["cost_base_year"])
    else:
        w = np.full(months, float(wti)); infl = np.ones(months)
    oil = q * DPM; wc = water_cut(m); water = oil * wc / (1 - wc)
    fp = w * price_factor
    rev = oil * fp
    basic = P_["basic_b0"] * fp + P_["basic_add"]  # 2023 model formula, cap at G460 not reached
    roy = rev * (P_["bid_royalty"] + basic) + P_["surface"] * rev * (1 - P_["bid_royalty"])
    fee_m = 0.0 if incremental else P_[FEES[fees]]
    hc = fee_m * infl
    fixed = (P_["well_fixed"] if incremental else (P_["battery_fixed"] + P_["well_fixed"] + P_["disposal_fixed"])) * infl  # incremental: battery and disposal carried by TEC-10
    opex = fixed + (oil * P_["oil_var"] + water * P_["water_var"]) * infl
    netback = rev - roy - hc - opex
    # economic limit: first month after which the trailing 12-month netback is negative
    trailing = pd.Series(netback).rolling(12, min_periods=1).sum().values
    live = np.ones(months, bool)
    bad = np.where((trailing < 0) & (m > 12))[0]
    if len(bad): live[bad[0]:] = False
    live &= q > 0
    capex_spent = capex * infl[0]
    cf = np.where(live, netback, 0.0); cap = np.zeros(months); cap[0] = -capex_spent
    last = np.where(live)[0].max() if live.any() else 0; cap[last] -= P_["abandon"] * infl[last]
    btax = cf + cap
    # tax: 25 % declining-balance depreciation of capex, 30 % on positive taxable income with loss carry-forward
    dep = np.zeros(months); pool = capex_spent
    for i in range(months):
        d = pool * P_["depr"] / 12; dep[i] = d; pool -= d
    taxable = np.where(live, netback, 0.0) - dep; carry = 0.0; tax = np.zeros(months)
    for i in range(months):
        ti = taxable[i] + carry
        if ti > 0: tax[i] = -ti * P_["tax"]; carry = 0.0
        else: carry = ti
    atax = btax + tax
    lag = 0.0 if npv_date is None else (t0 - pd.Timestamp(npv_date)).days / 365.25
    df = (1 + P_["disc"]) ** (-((m - 0.5) / 12 + lag))
    cum = np.cumsum(btax); payout = int(np.argmax(cum > 0)) + 1 if (cum > 0).any() else None
    irr = None
    lo, hi = 0.0, 10.0  # IRR reported only when positive (a late abandonment cost makes negative-rate roots ill-posed)
    f = lambda r: np.sum(btax / (1 + r) ** ((m - 0.5) / 12))
    if f(lo) > 0 and f(hi) < 0:
        for _ in range(80):
            mid = (lo + hi) / 2; (lo, hi) = (mid, hi) if f(mid) > 0 else (lo, mid)
        irr = round(lo, 3)
    out = dict(profile=profile if isinstance(profile, str) else "custom", deck=deck or "flat", wti=wti if deck is None else None, price_factor=price_factor, capex=round(capex_spent), incremental=incremental, fees=("none" if incremental else fees),
               econ_months=int(live.sum()), oil_econ_bbl=int(oil[live].sum()), revenue=int(rev[live].sum()), royalties=int((roy + hc)[live].sum()), opex=int(opex[live].sum()),
               noi_btax=int(btax.sum()), npv10_btax=int(np.sum(btax * df)), npv10_atax=int(np.sum(atax * df)), tax=int(tax.sum()), payout_months=payout, irr_btax=irr,
               royalty_share=round(float((roy + hc)[live].sum() / rev[live].sum()), 3), opex_per_bbl=round(float(opex[live].sum() / oil[live].sum()), 2))
    cfd = pd.DataFrame(dict(month=m, year=year, wti=w, oil_bpd=q, oil_bbl=oil, water_bbl=water, field_price=fp, revenue=rev, royalties=roy + hc, opex=opex, netback=netback,
                            live=live, capital=cap, cf_btax=btax, tax=tax, cf_atax=atax, disc_factor=df))
    return out, cfd

PROFILES = ["low_bpd", "base_bpd", "high_bpd"]
cases = []
for inc in [False, True]:
    for profile in PROFILES:
        for capcase in ["low", "base", "high"]:
            o, _ = run(profile, afe.loc[capcase, "usd"], deck="glj_oct26", incremental=inc); o["capex_case"] = capcase; cases.append(o)
            for wti in [50, 60, 70, 80, 90, 100]:
                o, _ = run(profile, afe.loc[capcase, "usd"], wti=wti, incremental=inc); o["capex_case"] = capcase; cases.append(o)
for fz in ["statutory", "extraction"]:  # stand-alone with statutory exploration-phase fees, and with extraction-phase fees (after a Development Plan)
    for profile in PROFILES:
        o, _ = run(profile, afe.loc["base", "usd"], deck="glj_oct26", fees=fz); o["capex_case"] = "base"; cases.append(o)
for pf in [0.75, 0.85, 0.90]:
    for inc in [False, True]:
        o, _ = run("base_bpd", afe.loc["base", "usd"], deck="glj_oct26", price_factor=pf, incremental=inc); o["capex_case"] = "base"; cases.append(o)
cases = pd.DataFrame(cases); cases.to_csv(OUT + "cases.csv", index=False)
base, cfd = run("base_bpd", afe.loc["base", "usd"], deck="glj_oct26", incremental=True); cfd.to_csv(OUT + "cashflow_base.csv", index=False)

pf0 = P["price_factor"]
main_fee = cases.fees.isin(["as_paid", "none"])
sel = cases[(cases.capex_case == "base") & (cases.price_factor == pf0) & main_fee]
glj = sel[sel.deck == "glj_oct26"].assign(view=lambda d: np.where(d.incremental, "incremental", "stand-alone"))
glj_tab = glj.pivot_table(index="profile", columns="view", values=["npv10_btax", "npv10_atax", "payout_months", "oil_econ_bbl"], aggfunc="first")
flat = sel[sel.deck == "flat"]
def breakeven(g):
    g = g.sort_values("wti"); x, y = g.wti.values, g.npv10_btax.values
    for i in range(1, len(x)):
        if y[i - 1] < 0 <= y[i]: return round(float(x[i - 1] + (x[i] - x[i - 1]) * (-y[i - 1]) / (y[i] - y[i - 1])), 1)
    return None
be = {f"{p}|{'incremental' if inc else 'stand-alone'}": breakeven(flat[(flat.profile == p) & (flat.incremental == inc)]) for p in PROFILES for inc in [False, True]}
grid = {("incremental" if inc else "stand-alone"): flat[flat.incremental == inc].pivot_table(index="profile", columns="wti", values="npv10_btax").round(0).to_dict() for inc in [False, True]}
ext = cases[cases.fees == "extraction"].set_index("profile").npv10_btax.to_dict()
stat = cases[cases.fees == "statutory"].set_index("profile").npv10_btax.to_dict()
pfs = cases[(cases.deck == "glj_oct26") & (cases.profile == "base_bpd") & (cases.capex_case == "base") & main_fee][["price_factor", "incremental", "npv10_btax"]].to_dict("records")
capx = cases[(cases.deck == "glj_oct26") & (cases.profile == "base_bpd") & (cases.price_factor == pf0) & main_fee][["capex_case", "incremental", "capex", "npv10_btax"]].to_dict("records")

# ---------------- bridge to GLJ YE2025 (Kinjal report 25269, TEC-12 1P entity: 205 kbbl remaining, NPV10 BT USD 2.08 MM at 2026-01-01) ----
# GLJ inputs from res_findings.md: Jan-2026 deck, first production Jul 2028, capex 1.9-1.96 MM$, fixed 1,670 $/well-month, variable 5.85 $/bbl,
# no water-handling charge, abandonment 75 k$/well, 1P type well qi 200 bbl/d, Di 36.6 %/yr, b 0.5. Di is read as GLJ's usual effective
# (secant) annual decline, converted to the nominal hyperbolic rate; over 30 years this gives 252 kbbl against GLJ's 1P EUR of 250 kbbl.
# That reading is an interpretation, not a GLJ statement; the nominal reading (Di = 0.366) would give 337 kbbl.
def arps(qi, de, b, months=360):
    di = ((1 - de) ** (-b) - 1) / b
    t = (np.arange(months) + 0.5) / 12
    return qi / (1 + b * di * t) ** (1 / b)
GLJ_1P = arps(200.0, 0.366, 0.5)
steps = [("Repository incremental base (Oct-2026 deck, Jan 2027 start, NPV at start)", {}),
         ("Price deck to GLJ Jan 2026", dict(deck="glj_jan26")),
         ("First oil Jul 2028, NPV dated 1 Jan 2026", dict(over=dict(start="2028-07-01"), npv_date="2026-01-01")),
         ("Capex 1.96 MM$ (GLJ) for the indexed AFE", dict(capex=1.96e6)),
         ("Costs to GLJ: 1,670 $/well-month, 5.85 $/bbl, no water charge, 75 k$ abandonment",
          dict(over=dict(well_fixed=1670.0, oil_var=5.85, water_var=0.0, abandon=75000.0))),
         ("Profile to GLJ 1P type well (qi 200, Di 36.6 %, b 0.5)", dict(q=GLJ_1P))]
kw = dict(profile="base_bpd", capex=afe.loc["base", "usd"], deck="glj_oct26", incremental=True, over={}); bridge = []
for name, ch in steps:
    ch = dict(ch)
    if "over" in ch: kw["over"] = {**kw["over"], **ch.pop("over")}
    kw.update(ch)
    o, _ = run(**kw)
    bridge.append(dict(step=name, npv10_btax=o["npv10_btax"], oil_econ_bbl=o["oil_econ_bbl"], econ_months=o["econ_months"], opex_per_bbl=o["opex_per_bbl"]))
bridge = pd.DataFrame(bridge); bridge["delta"] = bridge.npv10_btax.diff().fillna(bridge.npv10_btax)
bridge.to_csv(OUT + "bridge.csv", index=False)
print(bridge.to_string(index=False))
summary = dict(parameters={k: v for k, v in P.items()}, glj_oct26_wti=GLJ_OCT26, capex_usd_2026=afe.usd.to_dict(),
               glj_oct26_base_capex={f"{r.profile}|{r.view}": dict(npv10_btax=int(r.npv10_btax), npv10_atax=int(r.npv10_atax), payout_months=r.payout_months, irr_btax=r.irr_btax, oil_econ_bbl=int(r.oil_econ_bbl), econ_months=int(r.econ_months)) for r in glj.itertuples()},
               glj_oct26_standalone_extraction_fees=ext, glj_oct26_standalone_statutory_fees=stat, glj_oct26_price_factor_sensitivity=pfs, glj_oct26_capex_sensitivity=capx,
               bridge_to_glj_ye2025=bridge.to_dict("records"), glj_ye2025_tec12_1p=dict(remaining_kbbl=205, npv10_btax_usd=2.08e6, ref="Kinjal report 25269, 1pj5nvDi"),
               flat_wti_npv10_btax=grid, flat_wti_breakeven=be, base_case_incremental=base,
               notes=["GLJ 1 Oct 2026 then-current WTI, costs +2 %/yr from 2026, NPV10 nominal, mid-month discounting, start Jan 2027",
                      "flat-WTI grid: constant prices and costs (real), same fees/capex",
                      "area fees in stand-alone only, as paid 2024-25 (FMP quota + IEEH); incremental assumes TEC-10 producing and carrying battery, disposal and area fees",
                      "no corporate G&A, no carry, 100 % WI; fiscal terms per contract (unchanged by the 2025 reform, G-49)"])
json.dump(summary, open(OUT + "summary.json", "w"), indent=1, default=float)
pd.set_option("display.width", 220)
print("GLJ OCT 2026, base capex, 0.81:"); print(glj[["profile", "view", "npv10_btax", "npv10_atax", "payout_months", "irr_btax", "oil_econ_bbl", "econ_months"]].to_string(index=False))
print("stand-alone, extraction-phase fees:", ext); print("breakeven flat WTI:", be)
print(pd.DataFrame(pfs).to_string(index=False)); print(pd.DataFrame(capx).to_string(index=False))

# ---------------- figure -----------------
INK = "#0b0b0b"; INK2 = "#52514e"; GRID = "#e4e3df"; SURF = "#fcfcfb"
COL = {"low_bpd": "#2a78d6", "base_bpd": "#eb6834", "high_bpd": "#1baf7a"}
LAB = {"low_bpd": "low (P90): 100 bbl/d, 65 kbbl", "base_bpd": "base (P50): 180 bbl/d, 218 kbbl", "high_bpd": "high (P10): 300 bbl/d, 366 kbbl"}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw={"width_ratios": [1.15, 1]}, facecolor=SURF)
for ax in (ax1, ax2): ax.set_facecolor(SURF)
views = ["stand-alone", "incremental"]; xb = np.arange(len(views)); wdt = 0.26
for i, p in enumerate(PROFILES):
    vals = [glj[(glj.profile == p) & (glj.view == v)].npv10_btax.iloc[0] / 1e6 for v in views]
    bars = ax1.bar(xb + (i - 1) * wdt, vals, width=wdt - 0.02, color=COL[p], label=LAB[p])
    for bx, v in zip(xb + (i - 1) * wdt, vals):
        ax1.text(bx, v + (0.04 if v >= 0 else -0.04), f"{v:+.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=9, color=INK)
ax1.axhline(0, color=INK2, lw=0.8); ax1.set_xticks(xb); ax1.set_xticklabels(["stand-alone\n(all field costs and area fees on TEC-12)", "incremental to a producing TEC-10\n(battery, disposal, area fees already carried)"], fontsize=9)
ax1.set_ylabel("NPV10 before tax, USD MM (100 % WI)"); ax1.grid(axis="y", color=GRID, lw=0.6); ax1.set_axisbelow(True); ax1.legend(fontsize=8, loc="upper left", frameon=False)
ax1.set_title(f"GLJ 1 Oct 2026 price deck, 0.81 x WTI, costs +2 %/yr, AFE USD {afe.loc['base','usd']/1e6:.2f} MM (2026)", fontsize=10, color=INK, loc="left")
for p in PROFILES:
    for inc, ls, mk in [(False, "-", "o"), (True, "--", "s")]:
        g = flat[(flat.profile == p) & (flat.incremental == inc)].sort_values("wti")
        ax2.plot(g.wti, g.npv10_btax / 1e6, ls=ls, marker=mk, ms=4, lw=2, color=COL[p], label=f"{p.split('_')[0]}, {'incremental' if inc else 'stand-alone'}")
ax2.axhline(0, color=INK2, lw=0.8); ax2.set_xlabel("WTI, flat real USD/bbl (sensitivity; field price 0.81 x WTI)"); ax2.set_ylabel("NPV10 before tax, USD MM")
ax2.grid(color=GRID, lw=0.6); ax2.set_axisbelow(True); ax2.legend(fontsize=7.5, ncol=2, frameon=False)
ax2.set_title("Flat-price sensitivity (GLJ Oct 2026 averages ~USD 78/bbl over 2027-35)", fontsize=10, color=INK, loc="left")
for s in ("top", "right"):
    ax1.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("figures/10_econ_rebuild.png", dpi=150, facecolor=SURF); print("figure written")

# ---------------- figure 24: bridge to GLJ YE2025 -----------------
lab = ["Repository\nincremental base\n(Oct-26 deck)", "GLJ Jan-26\nprice deck", "First oil Jul 2028,\nNPV at 1 Jan 2026", "Capex\n1.96 MM$",
       "GLJ costs: 1,670 $/well-mo,\n5.85 $/bbl, no water\ncharge, 75 k$ ABEX", "GLJ 1P type well\nqi 200, Di 36.6 %, b 0.5\n(252 kbbl)", "GLJ YE2025\nTEC-12 1P\n(report 25269)"]
fig, ax = plt.subplots(figsize=(13, 5.6), facecolor=SURF); ax.set_facecolor(SURF)
v = bridge.npv10_btax.values / 1e6; d = bridge.delta.values / 1e6; xs = np.arange(len(lab))
ax.bar(0, v[0], color="#eb6834", width=0.6)
for i in range(1, len(v)):
    lo_, hi_ = sorted([v[i - 1], v[i]])
    ax.bar(i, hi_ - lo_, bottom=lo_, color="#1baf7a" if d[i] >= 0 else "#d03b3b", width=0.6)
    ax.plot([i - 1 + 0.3, i - 0.3], [v[i - 1], v[i - 1]], color=INK2, lw=0.7)
    ax.text(i, hi_ + 0.05, f"{d[i]:+.2f}", ha="center", va="bottom", fontsize=9, color=INK)
ax.text(0, v[0] + 0.05, f"{v[0]:+.2f}", ha="center", va="bottom", fontsize=9, color=INK)
ax.bar(len(v), 2.08, color="#2a78d6", width=0.6); ax.text(len(v), 2.13, "2.08", ha="center", va="bottom", fontsize=9, color=INK)
ax.plot([len(v) - 1 + 0.3, len(v) - 0.3], [v[-1], v[-1]], color=INK2, lw=0.7)
ax.set_xticks(xs); ax.set_xticklabels(lab, fontsize=8); ax.axhline(0, color=INK2, lw=0.8)
ax.set_ylabel("TEC-12 NPV10 before tax, USD MM (100 % WI)"); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
ax.set_title(f"From the repository case to GLJ's booking: rebuilt GLJ case USD {v[-1]:.2f} MM vs GLJ USD 2.08 MM; the cost basis is the largest single step", fontsize=10, color=INK, loc="left")
plt.tight_layout(); plt.savefig("figures/24_glj_bridge.png", dpi=150, facecolor=SURF); print("figure 24 written")
