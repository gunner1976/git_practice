# Task 10 — Economics rebuild, review v4 and the deck

Outputs: `docs/Tecolutla_Field_History_and_TEC12_Review_v4.md` (the extended review), `docs/Tecolutla_TEC12_Handover.pptx` (12 slides, built by `src/build_deck.py`), `src/econ_rebuild.py` with `data/processed/econ_rebuild/{cases.csv, cashflow_base.csv, summary.json}` and `figures/10_econ_rebuild.png`.

## Economics rebuild

Structure: the 2023 IFR workbook's fiscal and cost terms (task 1): bid royalty 31.22 %, basic royalty B0 0.00125 × field price + 1.5 %, surface 1 %, hydrocarbon tax 1,150 then 2,750 peso/km²/month on 7.2 km² at 18 MXN/USD, field price 90 % of WTI, opex 7.25 USD/bbl oil + 3.25 USD/bbl water + 2,500 USD/well/month, battery 10,000 and disposal 1,500 USD/month, 30 % tax on netback less 25 % declining-balance depreciation with loss carry-forward, 10 % discount, 150 k abandonment, economic limit when the trailing 12-month netback turns negative. Inputs from this repository: task-6 profiles (low/base/high), task-8 escalated AFE (1.81 / 1.97 / 2.20 MM USD), water cut following TEC-10 (0.40 rising to 0.85), start January 2027, flat real WTI 50–100.

Two views are reported: **stand-alone** (all fixed costs on TEC-12) and **incremental** to a producing TEC-10 (battery and disposal fixed costs already carried), which is the relevant one for an operator that keeps the field on production. NPV10 grids are in `summary.json` and the review §6.5.

| Base profile, base capex | Stand-alone NPV10 BTAX | Incremental NPV10 BTAX | Payout (incremental) |
|---|---|---|---|
| WTI 60 | −0.62 MM | +0.06 MM | — |
| WTI 70 | −0.09 MM | +0.76 MM | < 2 yr |
| WTI 80 | +0.46 MM | +1.41 MM | < 2 yr |

Not covered: the March 2025 fiscal reform (G-49), corporate G&A, the Simmons carry, inflation, and any TEC-13 follow-on.

## Review v4 and deck

The v4 review keeps the v3 structure and replaces each section's numbers with the reconciled ones, marking what changed. The deck has one figure per task with the reading of it, and closes with the decisions list and the gap register.
