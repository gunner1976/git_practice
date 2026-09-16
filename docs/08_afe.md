# Task 8 — TEC-12 AFE: rebuild, the $5,000, the currency, and escalation to 2026

Script: `src/afe_rebuild.py`. Outputs: `data/processed/afe/afe_lines.csv` (38 lines, both workbook versions side by side), `afe_by_day.csv`, `afe_categories.csv`, `afe_escalated.csv`, `summary.json`, `figures/08_afe.png`.

Sources: `ye2020_reserves/TEC-12 Drilling & Completion Cost Estimate.xlsx` (Drive 7 Apr 2021, 43,581 B) and `tec12_drill/TEC-12 Rough Drilling & Completion Cost Estimate (2).xlsx` (14 Sep 2021, 43,103 B; same file also in `tec12_budget_2021`). Both are a 20-column daily schedule (PS1–PS6 pre-spud 9–14 Nov 2020, days 1–14 drilling and completion to 8 Dec 2020) with a SUB column per line. TEC-11 actuals from `development_plan/Tec 11 Summary of Costs (Actual and Budgeted).xlsx` and `drilling_costs/TEC-11 Drilling Cost Tracker 26Dec2018.xlsx`; TEC-10 AFE cover from `drilling_costs/TEC-10 Updated Drilling Cost Summary 15Jun2018.xlsx`; FX from `appraisal_plan/GLJ jan22.xlsx` and the 15 Sep 2026 spot.

## 1. The $5,000 discrepancy is resolved

| | Apr 2021 workbook | Sep 2021 "(2)" workbook |
|---|---|---|
| Sum of every daily cell | 1,572,723.52 | 1,572,723.52 |
| Cumulative row, last day | 1,572,723.52 | 1,572,723.52 |
| SUB column total (the "AFE total") | **1,572,723.52** | **1,567,723.52** |

In the September copy the SUB formula in cell AB12, Drilling Pad Maintenance (5,000, Kefren), was deleted, so the SUB column is short by exactly that line while the daily totals still carry it. Two other SUB formulas in that copy (Conductor Hammering, Rig move) start at column I or J instead of H, which loses nothing because column H is empty on those rows. **The AFE is USD 1,572,724, not 1,567,724**; the review quoted the broken column. Every other cell is identical between the two versions.

## 2. What the AFE contains (Nov 2020 pricing)

| Category | USD | Share | Largest lines |
|---|---|---|---|
| Rig and rig move | 424,163 | 27 % | Simmons rig 15,950/day × 13.75 days = 203,363; rig move 190,000 (35,000 × 3 in, 85,000 out); camp 28,000 |
| Tubulars and wellhead | 365,233 | 23 % | 7" intermediate casing 79.40 USD/m × 2,360 m = 187,384; 2⅞" tubing 27.71 × 2,200 m = 60,962; wellhead 42,000; 9⅝" surface 81.79 × 500 m = 40,895; conductor 166.4 × 30 m = 4,992 |
| Mud, fluids and disposal | 277,823 | 18 % | mud and chemicals 74,984 (12¼") + 177,915 (8½") = 260,323 |
| Downhole tools and directional | 141,500 | 9 % | directional 10,000/day × 7 = 70,000; special tools 3,000/day × 11; bits 23,500 |
| Logging, perforating, completion | 118,000 | 8 % | wireline 50,000; perforating 40,000; swab/test 20,000; stimulation 8,000 |
| Supervision, engineering, HSE | 96,725 | 6 % | engineering 39,500; supervision 2,700/day; geologist 1,000/day |
| Cementing | 94,280 | 6 % | production 58,825; surface 35,455 |
| Site and civil | 55,000 | 3 % | conductor hammering 30,000; survey, pad, cellar, cleanup |
| **Total** | **1,572,724** | | 20 operational days |

Unit rates are consistent with TEC-11's December 2018 tracker (rig 15,950/day, supervision 2,700/day, camp, geologist 1,000/day, engineering 250–500/day are identical), so the 2020 AFE is priced on 2018 contracts. Notably absent: contingency, production casing (the design runs 7" intermediate to TD and completes with tubing), a cement bond log, and any owner's cost or insurance.

## 3. Currency

Neither workbook carries a currency label. The evidence that the figures are USD:

- The sister documents from the same Tonalli cost system are labelled: the TEC-11 cost format (`Formato_costo_pozos`) is headed "Costos totales — Dólares", and the TEC-11 actual-versus-budget summary is in the same units (drilling 3,105,308 actual vs 2,853,870 budget).
- The same line items and vendors (Simmons rig at 15,950/day, Tenaris tubulars per metre) carry the same numbers in the TEC-11 tracker, which is in the USD format above.
- Every IFR economic model carries TEC-12 capital as "(US$)" 1.55–1.8 MM, consistent only with a USD AFE.

Conclusion: **USD**, confirmed by Kevin Gunning on 16 Sep 2026 (G-44 resolved). No conversion of any source figure was made until this point; the CAD figures below are conversions of the USD total at stated rates.

## 4. Escalation from Nov 2020 to Sep 2026

No cost index could be pulled inside this environment (FRED, BLS, ycharts and tradingeconomics are blocked by the egress proxy; G-45). The three factors below are explicit assumptions, chosen from what could be sourced:

| Case | Factor | Basis |
|---|---|---|
| Low | ×1.15 | GLJ's own cost-inflation deck in the files (0 % 2022, 3 % 2023, 2 %/yr after: ×1.12 to 2026) plus the TEC-11 drilling overrun of 8.8 % against its AFE |
| Base | ×1.25 | S&P Global UCCI: +7 % in H1 2022 alone, US Lower-48 onshore +15–20 % in 2022, +3 % in 2025 and "elevated" into 2026; a US drilling PPI near 396–403 (Dec 1985 = 100) through 2025–26 against a 2020 trough |
| High | ×1.40 | the same, with the AFE re-priced from 2018 contract rates and a contingency that the AFE does not carry |

| | USD | CAD at 1.3915 (15 Sep 2026 spot) | CAD at 1.266 (GLJ Jan-2022 long-term 0.79) |
|---|---|---|---|
| AFE as written (Nov 2020) | 1,572,724 | 2,188,445 | 1,990,789 |
| Escalated low | 1,808,632 | 2,516,711 | 2,289,408 |
| **Escalated base** | **1,965,904** | **2,735,556** | **2,488,487** |
| Escalated high | 2,201,813 | 3,063,823 | 2,787,105 |

For comparison, IFR's own 2023 economics carried TEC-12 at USD 1.8 MM (as a TEC-10 re-entry, task 1), which sits at the low case, and the TEC-11 horizontal came in at USD 4.40 MM actual against 3.93 MM budget (+12 % overall, +8.8 % on drilling). The base escalated AFE of about **USD 2.0 MM / CAD 2.7 MM** is the number to carry into the economics rebuild, with 1.8–2.2 MM as the range.

## 5. Checks

- Both workbooks re-summed cell by cell; 38 lines; every daily total and the cumulative row reproduce.
- Category totals sum to the line total.
- FX: spot 1.3915 USD/CAD on 15 Sep 2026 (tradingeconomics, Bank of Canada series); GLJ long-term CAD/USD 0.79 from the Jan-2022 deck in the files.

Sources for the escalation and FX statements: [S&P Global UCCI update](https://www.spglobal.com/energy/en/research-analytics/upward-price-pressures-will-make-cost-savings-difficult-this-y), [Wood Mackenzie, upstream cost inflation](https://www.woodmac.com/blogs/energy-pulse/upstream-cost-inflation-is-back/), [S&P Global 2026 cost outlook](https://energy.spglobal.com/rs/325-KYL-599/images/2026-Cost-And-Supply-EMEA-Growth-Marketo-Form-Aberdeen-NS-Dialogue-Digital-Page-Top-5-trends.pdf), [FRED PCU213111213111 (blocked here)](https://fred.stlouisfed.org/series/PCU213111213111), [tradingeconomics USD/CAD](https://tradingeconomics.com/canada/currency), [Bank of Canada monthly rates](https://www.bankofcanada.ca/rates/exchange/monthly-exchange-rates/).
