"""Task 10 support: TEC-12 single-well economics rebuilt in Python on the 2023 IFR model's fiscal and cost structure,
with the task-6 production range, the task-8 escalated AFE and a flat WTI grid.
Usage: python src/econ_rebuild.py
Outputs: data/processed/econ_rebuild/{cases.csv, cashflow_base.csv, summary.json}, figures/10_econ_rebuild.png
Every fiscal and cost parameter is taken from the 2023 workbook (task 1, docs/01_econ_2023.md) unless stated; nothing here is a
substitute for a fiscal-regime check after the 2025 reform.
"""
import json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "data/processed/econ_rebuild/"; DPM = 30.42
prof = pd.read_csv("data/processed/forecast/tec12_profiles_monthly.csv")
afe = pd.read_csv("data/processed/afe/afe_escalated.csv").set_index("case")
P = dict(  # 2023 workbook Model (Tec-10 & Tec-12)
    field_price_factor=0.90, bid_royalty=0.3122, basic_b0=0.00125, basic_add=0.015, basic_a0=48.0, surface=0.01,
    hc_tax_peso_km2_m=(1150.0, 2750.0), block_km2=7.2, mxn_usd=18.0, battery_fixed=10000.0, well_fixed=2500.0, disposal_fixed=1500.0,
    oil_var=7.25, water_var=3.25, tax=0.30, depr=0.25, disc=0.10, abandon=150000.0, start="2027-01-01")
def water_cut(m):  # TEC-10 trajectory: 0.42 first year -> 0.67 at 12 months -> ~0.85 by year 10 (task 4); explicit assumption
    return np.clip(0.40 + 0.45 * (1 - np.exp(-m / 24.0)), 0.40, 0.85)
def run(profile, wti, capex, price_factor=P["field_price_factor"], months=360, label="", incremental=False):
    q = prof[profile].values[:months]; m = np.arange(1, months + 1)
    oil = q * DPM; wc = water_cut(m); water = oil * wc / (1 - wc)
    fp = wti * price_factor
    rev = oil * fp
    basic = np.where(fp < P["basic_a0"], 0.075, np.minimum(0.15, P["basic_b0"] * fp + P["basic_add"])) if False else (P["basic_b0"] * fp + P["basic_add"])  # 2023 model formula, capped at G460 (not reached)
    roy = rev * (P["bid_royalty"] + basic) + P["surface"] * rev * (1 - P["bid_royalty"])
    hc = np.where(m <= 60, P["hc_tax_peso_km2_m"][0], P["hc_tax_peso_km2_m"][1]) * P["block_km2"] / P["mxn_usd"]
    fixed = P["well_fixed"] if incremental else (P["battery_fixed"] + P["well_fixed"] + P["disposal_fixed"])  # incremental: battery and disposal already carried by TEC-10
    opex = fixed + oil * P["oil_var"] + water * P["water_var"]
    netback = rev - roy - hc - opex
    # economic limit: first month after which the trailing 12-month netback is negative
    trailing = pd.Series(netback).rolling(12, min_periods=1).sum().values
    live = np.ones(months, bool)
    bad = np.where((trailing < 0) & (m > 12))[0]
    if len(bad): live[bad[0]:] = False
    live &= q > 0
    cf = np.where(live, netback, 0.0); cap = np.zeros(months); cap[0] = -capex
    last = np.where(live)[0].max() if live.any() else 0; cap[last] -= P["abandon"]
    btax = cf + cap
    # tax: 25 % declining-balance depreciation of capex, 30 % on positive taxable income with loss carry-forward
    dep = np.zeros(months); pool = capex
    for i in range(months):
        d = pool * P["depr"] / 12; dep[i] = d; pool -= d
    taxable = np.where(live, netback, 0.0) - dep; carry = 0.0; tax = np.zeros(months)
    for i in range(months):
        ti = taxable[i] + carry
        if ti > 0: tax[i] = -ti * P["tax"]; carry = 0.0
        else: carry = ti
    atax = btax + tax
    df = (1 + P["disc"]) ** (-(m - 0.5) / 12)
    cum = np.cumsum(btax); payout = int(np.argmax(cum > 0)) + 1 if (cum > 0).any() else None
    irr = None
    try:
        lo, hi = -0.99, 10.0
        f = lambda r: np.sum(btax / (1 + r) ** ((m - 0.5) / 12))
        if f(lo) > 0 and f(hi) < 0:
            for _ in range(80):
                mid = (lo + hi) / 2; (lo, hi) = (mid, hi) if f(mid) > 0 else (lo, mid)
            irr = round(lo, 3)
    except Exception: pass
    out = dict(profile=profile, wti=wti, field_price=fp, capex=capex, price_factor=price_factor, incremental=incremental, econ_months=int(live.sum()), oil_econ_bbl=int(oil[live].sum()),
               revenue=int(rev[live].sum()), royalties=int((roy + hc)[live].sum()), opex=int(opex[live].sum()), noi_btax=int(btax.sum()),
               npv10_btax=int(np.sum(btax * df)), npv10_atax=int(np.sum(atax * df)), tax=int(tax.sum()), payout_months=payout, irr_btax=irr,
               royalty_share=round(float((roy + hc)[live].sum() / rev[live].sum()), 3), opex_per_bbl=round(float(opex[live].sum() / oil[live].sum()), 2))
    cfd = pd.DataFrame(dict(month=m, oil_bpd=q, oil_bbl=oil, water_bbl=water, field_price=fp, revenue=rev, royalties=roy + hc, opex=opex, netback=netback, live=live, capital=cap, cf_btax=btax, tax=tax, cf_atax=atax, disc_factor=df))
    return out, cfd
cases = []
for inc in [False, True]:
    for profile in ["low_bpd", "base_bpd", "high_bpd"]:
        for wti in [50, 60, 70, 80, 90, 100]:
            for capcase in ["low", "base", "high"]:
                o, _ = run(profile, wti, afe.loc[capcase, "usd"], incremental=inc); o["capex_case"] = capcase; cases.append(o)
for pf in [0.80, 0.85]:
    o, _ = run("base_bpd", 70, afe.loc["base", "usd"], price_factor=pf); o["capex_case"] = "base"; cases.append(o)
# measured realised price: 0.81 x WTI volume-weighted over the 2020-2022 PEMEX settlements (src/pemex_settlements.py, G-24)
for inc in [False, True]:
    for profile in ["low_bpd", "base_bpd", "high_bpd"]:
        for wti in [50, 60, 70, 80, 90, 100]:
            o, _ = run(profile, wti, afe.loc["base", "usd"], price_factor=0.81, incremental=inc); o["capex_case"] = "base"; cases.append(o)
cases = pd.DataFrame(cases); cases.to_csv(OUT + "cases.csv", index=False)
base, cfd = run("base_bpd", 70, afe.loc["base", "usd"]); cfd.to_csv(OUT + "cashflow_base.csv", index=False)
sa = cases[(cases.capex_case == "base") & (cases.price_factor == 0.9)]
grid = sa[~sa.incremental].pivot_table(index="profile", columns="wti", values="npv10_btax")
grid_at = sa[~sa.incremental].pivot_table(index="profile", columns="wti", values="npv10_atax")
grid_inc = sa[sa.incremental].pivot_table(index="profile", columns="wti", values="npv10_btax")
grid_inc_at = sa[sa.incremental].pivot_table(index="profile", columns="wti", values="npv10_atax")
summary = dict(parameters=P, capex_usd=afe.usd.to_dict(), base_case=base, npv10_btax_grid_base_capex=grid.round(0).to_dict(), npv10_atax_grid_base_capex=grid_at.round(0).to_dict(), npv10_btax_grid_incremental=grid_inc.round(0).to_dict(), npv10_atax_grid_incremental=grid_inc_at.round(0).to_dict(),
               notes=["fiscal terms and opex from the 2023 IFR workbook; no corporate G&A, no Simmons carry, 100 % WI", "water cut assumed to follow TEC-10 (0.40 -> 0.85)", "flat real prices, no inflation, 10 % discount, start Jan 2027", "post-2025 fiscal reform not checked (G-49)"])
json.dump(summary, open(OUT + "summary.json", "w"), indent=1, default=float)
pd.set_option("display.width", 220)
print("STANDALONE BTAX"); print(grid.round(0).to_string()); print("STANDALONE ATAX"); print(grid_at.round(0).to_string()); print("INCREMENTAL BTAX"); print(grid_inc.round(0).to_string()); print("INCREMENTAL ATAX"); print(grid_inc_at.round(0).to_string()); print(json.dumps(base, indent=1, default=float))
print(cases[cases.profile == "base_bpd"][["wti", "capex_case", "price_factor", "npv10_btax", "npv10_atax", "payout_months", "irr_btax", "econ_months", "oil_econ_bbl"]].to_string())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5))
for profile, col, lab in [("low_bpd", "tab:blue", "low (P90): 100 bbl/d, 65 kbbl"), ("base_bpd", "tab:orange", "base (P50): 180 bbl/d, 218 kbbl"), ("high_bpd", "tab:green", "high (P10): 300 bbl/d, 366 kbbl")]:
    g = sa[(sa.profile == profile) & ~sa.incremental]; gi = sa[(sa.profile == profile) & sa.incremental]
    ax1.plot(g.wti, g.npv10_btax / 1e6, "-o", color=col, label=lab + ", stand-alone BTAX")
    ax1.plot(gi.wti, gi.npv10_btax / 1e6, "--s", color=col, alpha=0.7, label=lab + ", incremental to TEC-10 BTAX")
ax1.axhline(0, color="k", lw=0.8); ax1.set_xlabel("WTI, flat real (USD/bbl); field price = 90 %"); ax1.set_ylabel("NPV10 (USD MM), 100 % WI, well level")
ax1.set_title(f"TEC-12 NPV10 vs price, capex USD {afe.loc['base','usd']/1e6:.2f} MM (escalated AFE base)", fontsize=10); ax1.grid(alpha=0.3); ax1.legend(fontsize=7)
# tornado around base/70
b = base["npv10_btax"]
items = []
for lab, lo, hi in [("production profile (P90 / P10)", sa[(sa.profile == "low_bpd") & (sa.wti == 70) & ~sa.incremental].npv10_btax.iloc[0], sa[(sa.profile == "high_bpd") & (sa.wti == 70) & ~sa.incremental].npv10_btax.iloc[0]),
                    ("WTI 60 / 80", sa[(sa.profile == "base_bpd") & (sa.wti == 60) & ~sa.incremental].npv10_btax.iloc[0], sa[(sa.profile == "base_bpd") & (sa.wti == 80) & ~sa.incremental].npv10_btax.iloc[0]),
                    ("capex high / low", cases[(cases.profile == "base_bpd") & (cases.wti == 70) & (cases.capex_case == "high") & ~cases.incremental & (cases.price_factor == 0.9)].npv10_btax.iloc[0], cases[(cases.profile == "base_bpd") & (cases.wti == 70) & (cases.capex_case == "low") & ~cases.incremental & (cases.price_factor == 0.9)].npv10_btax.iloc[0]),
                    ("PEMEX price factor 0.80 / 0.90", cases[(cases.profile == "base_bpd") & (cases.wti == 70) & (cases.price_factor == 0.80)].npv10_btax.iloc[0], b),
                    ("incremental to TEC-10 (shared battery) / stand-alone", sa[(sa.profile == "base_bpd") & (sa.wti == 70) & sa.incremental].npv10_btax.iloc[0], b)]:
    items.append((lab, lo - b, hi - b))
items.sort(key=lambda x: abs(x[1]) + abs(x[2]))
for i, (lab, lo, hi) in enumerate(items):
    ax2.barh(lab, lo / 1e6, color="#e6550d"); ax2.barh(lab, hi / 1e6, color="#31a354")
ax2.axvline(0, color="k", lw=0.8); ax2.set_xlabel(f"change in NPV10 before tax from the base case (USD {b/1e6:.2f} MM at WTI 70)"); ax2.set_title("Tornado, before tax", fontsize=10); ax2.grid(axis="x", alpha=0.3)
plt.tight_layout(); plt.savefig("figures/10_econ_rebuild.png", dpi=140); print("figure written")
