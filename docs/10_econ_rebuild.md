# Task 10 — Economics rebuild, review v4 and the deck

Outputs: `docs/Tecolutla_Field_History_and_TEC12_Review_v4.md` (the extended review), `docs/Tecolutla_TEC12_Handover.pptx` (13 slides, built by `src/build_deck.py`), `src/econ_rebuild.py` with `data/processed/econ_rebuild/{cases.csv, cashflow_base.csv, summary.json}` and `figures/10_econ_rebuild.png`.

## Economics rebuild

Structure: the 2023 IFR workbook's fiscal and cost terms (task 1): bid royalty 31.22 %, basic royalty B0 0.00125 × field price + 1.5 %, surface 1 %, hydrocarbon tax 1,150 then 2,750 peso/km²/month on 7.2 km² at 18 MXN/USD, field price 90 % of WTI, opex 7.25 USD/bbl oil + 3.25 USD/bbl water + 2,500 USD/well/month, battery 10,000 and disposal 1,500 USD/month, 30 % tax on netback less 25 % declining-balance depreciation with loss carry-forward, 10 % discount, 150 k abandonment, economic limit when the trailing 12-month netback turns negative. Inputs from this repository: task-6 profiles (low/base/high), task-8 escalated AFE (1.81 / 1.97 / 2.20 MM USD), water cut following TEC-10 (0.40 rising to 0.85), start January 2027, flat real WTI 50–100.

Two views are reported: **stand-alone** (all fixed costs on TEC-12) and **incremental** to a producing TEC-10 (battery and disposal fixed costs already carried), which is the relevant one for an operator that keeps the field on production. NPV10 grids are in `summary.json` and the review §6.5.

| Base profile, base capex, price factor 0.90 (as first run) | Stand-alone NPV10 BTAX | Incremental NPV10 BTAX | Payout (incremental) |
|---|---|---|---|
| WTI 60 | −0.62 MM | +0.06 MM | — |
| WTI 70 | −0.09 MM | +0.76 MM | < 2 yr |
| WTI 80 | +0.46 MM | +1.41 MM | < 2 yr |

**Addendum (task 15).** The PEMEX delivery-reception settlements measure the realised price at 0.81 × WTI volume-weighted over 2020–22 (`docs/15_pemex_settlements.md`), not the 0.90 the 2023 workbook assumed. `econ_rebuild.py` now also sweeps every profile and both views at 0.81; these are the numbers carried into the review v4 §6.5 and the deck:

| Base profile, base capex, price factor 0.81 (measured) | Stand-alone NPV10 BTAX | Incremental NPV10 BTAX | Payout (incremental) |
|---|---|---|---|
| WTI 60 | −0.92 MM | −0.34 MM | — |
| WTI 70 | −0.46 MM | +0.27 MM | 32 months |
| WTI 80 | +0.02 MM | +0.89 MM | 23 months |

Break-even moves from WTI ≈ 72 to ≈ 80 stand-alone and from ≈ 59 to ≈ 65 incremental. The high profile stays positive incremental from WTI 60 and stand-alone from 70; the low profile is negative everywhere.

Not covered: the March 2025 fiscal reform (G-49), corporate G&A, the Simmons carry, inflation, and any TEC-13 follow-on.

## Review v4 and deck

The v4 review keeps the v3 structure and replaces each section's numbers with the reconciled ones, marking what changed. The deck has one figure per task with the reading of it, and closes with the decisions list and the gap register.

## Update, 25 Oct 2026: GLJ October 2026 prices, indexed AFE and actual area charges

These changes were agreed with Kevin Gunning on 24 Oct 2026. `src/econ_rebuild.py` was rewritten; the outputs and `figures/10_econ_rebuild.png` were regenerated.

**What changed:**

1. **Primary price case: GLJ Ltd. forecast effective 1 Oct 2026** (gljpc.com `Oct26.pdf`, Table 1). WTI then-current, USD/bbl:

   | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | after 2035 |
   |---|---|---|---|---|---|---|---|---|---|
   | 81.00 | 75.00 | 73.22 | 74.68 | 76.18 | 77.70 | 79.26 | 80.84 | 82.46 | +2 %/yr |

   - Costs are inflated at GLJ's 2 %/yr from 2026, and NPV10 is nominal.
   - The realised price stays at 0.81 × WTI.
   - The flat real-WTI grid is kept as a sensitivity.
2. **AFE indexed on the US drilling PPI (G-45).** The factor is 401.286 / 309.400 = ×1.297, Nov 2020 to Sep 2026, giving USD 2.04 MM in 2026 dollars (previously ×1.25, USD 1.97 MM). It is spent in Jan 2027 at USD 2.08 MM. Low and high capex remain ×1.15 and ×1.40.
3. **Area-based fiscal charges (G-60).**
   - **Stand-alone case:** USD 2,638/month in 2026 dollars, inflated. This is the LIH art. 23 contract quota as paid in 2024 (MXN 29,829/month) plus the art. 55 exploration-phase activity tax (2,464.84 MXN/km²/month on 7.16 km²), at 18 MXN/USD. An extraction-phase sensitivity uses USD 3,922/month.
   - **Incremental case:** no area charges. They are field-level costs that TEC-10 carries whether or not TEC-12 is drilled, as with the battery and disposal.
   - Before this update, the model charged 1,150 then 2,750 peso/km²/month (the unindexed 2014 quota) in both cases.

**Results.** Base capex, 0.81 × WTI, NPV10 in USD MM:

| GLJ 1 Oct 2026 | Before tax | After tax | Payout | IRR before tax | Oil to economic limit |
|---|---|---|---|---|---|
| Incremental, low | −1.02 | −1.10 | — | — | 65 kbbl |
| **Incremental, base** | **+0.47** | **+0.11** | 27 months | 29 % | 203 kbbl |
| Incremental, high | +1.44 | +0.83 | 15 months | 78 % | 331 kbbl |
| Stand-alone, low | −1.57 | −1.60 | — | — | 49 kbbl |
| **Stand-alone, base** | **−0.45** | **−0.69** | — | — | 127 kbbl |
| Stand-alone, high | +0.33 | −0.10 | 19 months | 36 % | 177 kbbl |

**Sensitivities:**
- Stand-alone base with extraction-phase fees: −0.51.
- Incremental base by price factor: 0.75 → +0.12; 0.85 → +0.70; 0.90 → +0.99.
- Incremental base by capex: low (×1.15) +0.70; high (×1.40) +0.30.

**Flat real-WTI sensitivity** (NPV10 before tax, base profile):

| WTI | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|
| Stand-alone | −1.50 | −1.08 | −0.63 | −0.16 | +0.32 | +0.80 |
| Incremental | −0.95 | −0.36 | +0.29 | +0.90 | +1.49 | +2.05 |

**Break-evens:**
- Base: WTI ≈ 66 incremental, ≈ 83 stand-alone.
- High: WTI ≈ 57 incremental, ≈ 69 stand-alone.
- Low: never breaks even.

**Reading:**
- The GLJ deck averages about USD 78/bbl over 2027–35, with USD 81 in the first year when the well's rate is highest. That lifts the incremental base case from +0.27 (flat 70) to +0.47.
- Removing the area fees from the incremental view, about +0.1, roughly offsets the higher indexed capex, about −0.07.
- The conclusion is unchanged: TEC-12 works as an add-on to a producing TEC-10 and does not stand alone at the base profile.
