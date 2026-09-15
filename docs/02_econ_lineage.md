# Task 2 — Reconciliation of the IFR economic models (Aug 2020, Feb 2022 ×9, Sept/Oct 2023)

Sources: eleven `.xlsm` workbooks in `data/raw/appraisal_plan`, `data/raw/development_plan`, `data/raw/tec12_drill` and `data/raw/tec12_drill/OLD` (SHA256 in `data/manifest.csv`, file table in `data/processed/econ_lineage/models.csv`).
Scripts: `src/econ_lineage.py` (extraction, cached values only) and `src/econ_lineage_matrix.py` (diff matrix, chart).
Outputs: `data/processed/econ_lineage/` (`models.csv`, `header_cells.csv`, `diff_matrix_header.csv`, `wells.csv`, `prices.csv`, `capital.csv`, `results.csv`, `profiles.csv`, `diff_matrix.csv`, `diff_matrix.md`) and `figures/02_econ_model_lineage.png`.
All money is USD as labelled in the workbooks. No recalculation was possible (G-16); values are as last saved by Excel.

## 1. What the eleven files are

All eleven descend from one IFR template (docProps created 2015-07-23, same `EDITS` change log, which stops at 15 May 2020). The `Summary (GLJ)` volumetrics sheet is byte-for-byte the same in all eleven, so the 11.16 MMbbl field OOIP and the 345,000 bbl TEC-12 back-solve (G-18) date from at least August 2020.

| Tag | File | Internal save stamp (UTC) | Sheets | Purpose read from content |
|---|---|---|---|---|
| 2020-08 | `Economic Model (Tecolutla August 2020) - FOR TRANS PLAN (TEC-12 Drill Econ).xlsm` | none stored (Drive 2025-08-18) | 10 | CNH transition plan; TEC-12 cases live in `Tec-12 (1)` |
| 2022-v3 | `Economic Model (Tecolutla Feb 2022)3.xlsm` | 2022-04-11 18:08 | 7 | Appraisal plan: TEC-10 + TEC-12 + TEC-13, gas sales |
| 2022-v2 | `... Feb 2022)2.xlsm` | 2022-04-11 18:10 | 7 | as v3 without gas |
| 2022-v1 | `... Feb 2022).xlsm` | 2022-04-11 18:11 | 7 | as v2, TEC-13 moved to Jun 2023 |
| 2022-v5 | `... Feb 2022)5 (HZ).xlsm` | 2022-04-12 01:35 | 7 | one 684 bbl/d horizontal at 3.0 MM instead of TEC-12/13 |
| 2022-v4 | `... Feb 2022)4 (Tec12 & Tec13).xlsm` | 2022-06-17 00:37 | 8 | v3 re-saved with "VT" labels and a `Decline` sheet "FOR CNH TRANSITION PLAN" |
| 2022-v6 | `... Feb 2022)6 (Tec12, 13, 14 & 15).xlsm` | 2022-06-17 21:26 | 10 | Development plan from Jul 2023: TEC-12/13 sunk, TEC-14/15, TEC-2 reactivation, power generation |
| 2022-v7 | `... Feb 2022)7 (Tec12, 13, 14 & 15).xlsm` | 2022-06-20 17:13 | 10 | v6 with fixed opex re-split (results identical) |
| 2022-v8 | `... Feb 2022)8 (Tec14 HZ).xlsm` | 2022-06-21 14:45 | 10 | TEC-14/15 verticals replaced by one 547 bbl/d horizontal at 3.0 MM |
| 2022-v9 | `... Feb 2022)9 (Tec14 HZ).xlsm` | 2022-06-21 18:17 | 10 | v8 with the horizontal's gas volumes corrected |
| 2023-10 | `2023-09-29 Tec-12 Economics.xlsm` | none stored (`OUTPUT` stamp 2023-10-24) | 12 | TEC-12 stand-alone decision from Jan 2024 (task 1) |

Two things the file names hide:

- **The suffix order is not the save order.** "3" was saved first, then "2", then the un-suffixed file, three minutes apart on 11 April 2022. "4" was saved on 17 June, after "5". The names are Save-As copies, not a sequence (G-21).
- **"Feb 2022" is the plan month, not the model date.** The `Model Production Profiles` sheet in v3–v5 is stamped 2022-03-08 and in v6–v9 2022-06-16; nothing in the series was saved in February 2022.

The chart `figures/02_econ_model_lineage.png` shows the inferred tree. Edges follow the save stamps and shared content: v5 keeps v3's gas sales and TEC-13 timing; v4 carries v3's results to the last dollar; v6 inherits v4's `Decline` sheet; v7's results equal v6's; v9 differs from v8 only in gas. The 2023 workbook descends from the Aug 2020 file, not from the 2022 series: it has the 2020 sheet set (`Tec-12 (1)`, `Tec-10 Prod`, `Sensitivity`), the 2020 profile sheet unchanged, and the 2020 capital labels.

## 2. Diff matrix

Full matrix with cell references: `data/processed/econ_lineage/diff_matrix.md` (33 parameters × 11 versions). The rows that matter:

| Parameter | 2020-08 | v3 / v2 / v1 | v5 | v4 | v6 / v7 | v8 / v9 | 2023-10 |
|---|---|---|---|---|---|---|---|
| Evaluation start | 2020-09 | 2022-04 | 2022-04 | 2022-04 | 2023-07 | 2023-07 | 2024-01 |
| WTI | 30 flat | 90 flat | 90 flat | 90 flat | GLJ Apr-2022 deck: 90, 85, 75.64, 77.15 … 90.4 (2033) | same | 85 flat |
| Inflation | 0 | 0 | 0 | 0 | 2 %/yr | 2 %/yr | 0 |
| Field price factor (PEMEX/WTI), `D428` | 0.95 | 0.801 | 0.801 | 0.801 | 0.801 | 0.801 | 0.90 |
| Field price month 1, USD/bbl | 28.50 | 72.09 | 72.09 | 72.09 | 72.09 (60.59 in year 2) | same | 76.50 |
| Battery fixed, USD/month | 15,000 | 15,000 | 15,000 | 15,000 | 15,000 | 15,000 | 10,000 |
| Well fixed, USD/well/month | 2,500 | 2,500 | 2,500 | 2,500 | 1,000 + 1,500 intervention (v7+: 812.5 + 1,687.5) | same | 2,500 |
| Active wells | TEC-2 25, TEC-10 50 bbl/d; TEC-12 off (COS 0) | TEC-10 50; TEC-12 Sep-22; TEC-13 Feb-23 (v1: Jun-23); qi 342 each | TEC-10; one HZ 684 bbl/d Sep-22 | as v3, "VT" labels | TEC-10 (Jul-22 start, 42 bbl/d by Jul-23); TEC-12 Dec-22; TEC-13 May-23; TEC-14 Jul-24; TEC-15 Jul-25 (qi 273.6); TEC-2 back Jun-25 at 20 | TEC-14/15 off; one HZ 547 bbl/d Jul-24 | TEC-10 80 bbl/d; TEC-12 HZ 342 Jan-24 |
| TEC-12 IP in window, bbl/d | 0 | 300.15 | 0 | 300.15 | 137.2 (already 7 months on) | 137.2 | 300.15 |
| TEC-12 oil in window, bbl | 0 | 401,440 | 0 | 401,440 | 261,551 | 261,551 | 234,629 econ / 403,217 full |
| Capital inside window, USD | 65,000 | 3,350,000 (TEC-12 1.25 + 0.25 + 0.05; battery 0.25; TEC-13 1.55) | 3,000,000 | 3,350,000 | 4,021,623 (TEC-14 1.55, TEC-15 1.55, TEC-2 0.15, power 0.5, TEC-11 conversion 0.15; inflated) | 3,887,911 (HZ 3.0 …) | 1,800,000 |
| Capital dated **before** window (excluded) | TEC-12 HZ re-entry 1.55 MM @ Jan-21 | none | TEC-12/13 lines switched off | none | TEC-12 1.55 @ Nov-22, TEC-13 1.55 @ Apr-23, battery 0.10, skid 0.25 | same | — |
| Economic life, yr | 4.0 | 35.5 | 35.5 | 35.5 | 18.1 | 18.1 | 10.9 |
| Oil, economic, bbl | 82,350 | 899,614 / 901,077 / 901,077 | 898,558 | 901,077 | 1,115,376 | 1,285,097 | 335,024 |
| Sales gas, mcf | 0 | 848,319 (v3) / 0 / 0 | 845,947 | 848,319 | 930,694 | 546,255 / 1,072,313 | 0 |
| NPV10 before tax, USD | −88,228 | 9,710,469 / 9,881,934 / 9,719,455 | 10,554,478 | 9,710,469 | 14,042,836 | 17,796,505 / 17,724,121 | 4,192,547 |
| NPV10 after tax, USD | −107,817 | 6,609,472 / 6,729,498 / 6,618,705 | 7,213,535 | 6,609,472 | 9,506,954 | 12,132,297 / 12,082,168 | 2,983,952 |
| IRR before tax (cached) | −44 % | 343 % / 357 % / 370 % | 447 % | 343 % | `#DIV/0!` | `#NUM!` / `#DIV/0!` | 415 % |

## 3. What actually changed, in order

1. **Aug 2020 → Apr 2022 (v3).** Start moved from Sep 2020 to Apr 2022. WTI 30 → 90 flat. The PEMEX field-price factor fell from 0.95 to 0.801 with no note of source. TEC-12 and TEC-13 switched on at qi 342 bbl/d each (the same hyperbolic: b 1.7, Di 3.507/yr, giving 300 bbl/d first-month average and 400 kbbl full life). Capital labels changed from "Tec-12 HZ Drill *Tec-10 Re-Entry" to "Tec-12 Drill", but the numbers did not: 1.25 + 0.25 + 0.05 = 1.55 MM in both. A 0.25 MM battery upgrade was added (comment dated 2022-04-11: "incl Tec-11 WO"). TEC-2 dropped to COS 0.
2. **v3 → v2 → v1 (same evening).** v2 removed the associated-gas sales that v3 had added (848 mmcf; gas revenue is flagged "NOT INCL IN TOT" in `outputs`, so v3's gas only added royalty and opex, lowering NPV by 0.17 MM). v1 slipped TEC-13 from Feb to Jun 2023. NPV10 9.71 → 9.88 → 9.72 MM.
3. **v3 → v5 (next morning).** Replaced TEC-12 + TEC-13 with one "Tecolutla Horizontal" at 684 bbl/d (two type curves stacked) for 3.0 MM, keeping v3's gas sales and Feb 2023 timing. NPV10 10.55 MM against v3's 9.71 MM. This is the horizontal-versus-two-verticals comparison; the horizontal wins by 0.84 MM on the same reserves because it saves 0.35 MM of capital and brings the second curve forward.
4. **v3 → v4 (17 June).** Renamed TEC-12/13 from "HZ" to "VT" and added the `Decline` sheet, which carries a block headed "FOR CNH TRANSITION PLAN": Q 500,000 bbl per well, 50 % hyperbolic (250,000 bbl at b 1.7, ai 0.2925/month) plus a 250,000 bbl exponential tail at 0.3 %/month to 2 bbl/d. Results identical to v3. So the CNH plan quoted 500 kbbl per vertical well while the economics ran on 400 kbbl (G-22).
5. **v4 → v6 (same day).** Start moved to Jul 2023, so TEC-12 (Nov 2022) and TEC-13 (Apr 2023) capital, the battery upgrade and the measurement skid, 3.45 MM in total, fall **before the window and are excluded from NPV**. Their production is included. GLJ April 2022 price deck with 2 %/yr inflation replaced flat 90. TEC-14 and TEC-15 added at 80 % of the TEC-12 curve (qi 273.6), TEC-2 reactivated in 2025 at 20 bbl/d, TEC-11 converted (0.15 MM) and a 0.5 MM gas-conservation power plant added. Fixed well cost split into 1,000 + 1,500 intervention. NPV10 14.04 MM, 7.35 MM programme capital in `outputs` (G-23).
6. **v6 → v7.** Fixed well cost re-split 812.5 + 1,687.5 (sum unchanged). Results identical.
7. **v7 → v8 → v9.** TEC-14/15 verticals replaced by one 547 bbl/d horizontal (1.6 × the vertical curve) at 3.0 MM from Jul 2024. v8's horizontal carried half the gas of the rest; v9 corrected it (1,072 mmcf). NPV10 17.72 MM. v9 is the last of the series and the basis of the Development Plan numbers.
8. **Aug 2020 → Oct 2023.** The 2023 TEC-12 workbook was built from the 2020 file, not from v9: start Jan 2024, WTI 85 flat, factor 0.90, battery 10 k/month, TEC-10 restarted at 80 bbl/d (v6–v9 had it at 42 bbl/d by mid-2023), TEC-12 capital raised to 1.5 + 0.25 + 0.05 = 1.8 MM but still labelled "Tec-10 Re-Entry". The `Model Production Profiles` sheet still shows TEC-12 first oil in March 2021.

## 4. What never changed

- **The TEC-12 type curve.** qi 342 bbl/d, b 1.7, Di 3.507/yr, first-month 300.15 bbl/d, 111.6 bbl/d at month 12, 61.2 at month 36, 400 kbbl over the full curve, in every version from Aug 2020 to Oct 2023 (`Model!I28:L28`, `profiles.csv`). Three years of TEC-10 history and the TEC-11 result changed nothing about it.
- **Fiscal terms.** Bid royalty 31.22 %, basic royalty B0 = 0.00125, surface 1 %, block fees 1,150/2,750 peso/km²/month, 30 % tax, 25 % depreciation, 10 % discount, 35-year contract, 150 k abandonment (v6–v9 carry abandonment in the capital table instead of `B21`).
- **Variable opex.** 7.25 USD/bbl oil, 3.25 USD/bbl water throughout.
- **Volumetrics sheet.** Identical in all eleven.

## 5. Why the headline numbers differ by a factor of four

None of the differences is a reserves revision. NPV10 before tax runs from 4.2 MM (2023) to 17.7 MM (v9) because:

| Driver | Effect |
|---|---|
| Number of wells in the programme | 1 (2023) vs 2 (v1–v4) vs 4–5 plus TEC-2 (v6–v9) |
| Sunk-capital convention | v6–v9 exclude 3.45 MM of TEC-12/13 capital that v1–v4 include |
| Field price | 72.09 (2022 flat) vs 60.6–65.6 (GLJ deck years 2–6) vs 76.5 (2023) |
| PEMEX factor | 0.95 → 0.801 → 0.90, unsourced in every file (G-24) |
| Economic limit | 35.5 yr (v1–v5 never reach the limit test) vs 18.1 yr vs 10.9 yr |

The incremental TEC-12 value that the review quotes (NPV10 2.84 MM before tax, 2.09 MM after tax) exists only in the 2023 workbook and prices a 1.8 MM re-entry, not the AFE well (G-17).

## 6. Recommendation

1. **Use the 2023 workbook structure as the single TEC-12 base case**, because it is the only version that isolates the TEC-12 decision from a multi-well programme and starts after the TEC-11 result. Before it is used, three inputs must be replaced: the capital line (AFE new-drill cost from task 8, in USD, with the CAD view alongside), the price basis (a dated WTI deck and a sourced PEMEX factor), and the TEC-12 profile (re-fitted in task 6 to TEC-10's 2018–2025 history rather than the 2020 curve).
2. **Retire the Feb 2022 series as an economic reference.** Keep v9 only as the record of what the Development Plan submitted to CNH assumed (5-well programme, 1.29 MMbbl, 17.7 MM NPV10 with 3.45 MM of capital treated as sunk), and v4's `Decline` sheet as the record of the 500 kbbl-per-well figure given to CNH.
3. **Quote versions by save stamp, not suffix**, in the review and deck: "Feb 2022 (3), saved 11 Apr 2022" etc.
4. **Do not quote the cached IRRs from v6–v9**; they are error cells.

## 7. Cross-checks performed

- Per-well oil volumes were recomputed from the monthly rate rows (rate × 30.42 days) and reconcile to the `outputs` "Active" oil totals within 0.2 % in every version (`results.csv` slot columns vs `outputs_active_oil_mbbl`).
- The `outputs` NPV10 equals `Model!J580` in all versions except 2023-10, where `outputs` is linked to the TEC-10-only sheet (1,355.7 k) rather than the combined sheet (4,192.5 k).
- Capital inside the window was recomputed by summing the monthly capital rows and matches `outputs` "Capital" for v1–v5 (3.35 / 3.0 MM); for v6–v9 `outputs` reports the whole programme (7.35 / 7.25 MM) while only 4.02 / 3.89 MM (inflated) falls inside the window.
