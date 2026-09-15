# Task 6 — Type curve and TEC-12 forecast reconciliation

Script: `src/forecast_reconcile.py`. Outputs: `data/processed/forecast/type_curve_month_on_prod.csv` (per-well rate by month on production, four PEMEX wells + TEC-10, with the IFR workbook columns alongside), `cases.csv` (19 cases), `tec12_profiles_monthly.csv` (recommended low/base/high, 360 months, plus the IFR 2020 curve), `summary.json`, `figures/06_type_curve_forecast.png`.

Sources: task-4 database; `tec12_drill/Tecolutla Type Curve.xlsx` (3 Mar 2021 copy; the 15 Mar 2022 copy in `appraisal_plan` differs only in header cells and row labels, no data differ; G-04 closed); `ye2020_reserves/Gross Oil Monthly Forecast by Well (Kevin).xlsx` (GLJ YE2020 profiles); `tec12_drill/Simmons Scenarios - Tec 12 and Tec 13.xlsx`; `tec12_drill/Petrel Robertson Tec-12 Assessment.pdf`; the 2023 economics (task 1).

Arps hyperbolic throughout: q = qi / (1 + b·Di·t)^(1/b), t in months. Volumes at 30.42 d/month. Economic cut-off 10 bbl/d unless the source applied its own.

## 1. What the "vertical well type curve" is

The IFR workbook (updated 17 Sep 2020, "data to Oct 2020") stacks the four PEMEX wells by month on production, averages them, and fits a curve. The task-4 database reproduces the workbook's per-well columns and its average to within 25 bbl/d in every month after the first (the first-month difference is the partial-month calendar-day rate). The fitted TEC-12 curve is qi 342 bbl/d, b 1.7, Di 3.5/yr (first-month average 300 bbl/d), 401 kbbl over 417 months, 315 kbbl over 20 years; "345 kbbl" is a pasted cumulative at an unrecorded cut-off (task 2, G-18).

Two things about that data matter for what the curve means:

1. **The PEMEX wells were recompleted.** TEC-6 produced from three intervals (1956–72, 1972–76, 1976–2006), TEC-2 from two, TEC-7 from two (task 4). The month-on-production average rises again at months 100–130 and 250–300 because wells were re-perforated or restarted after long shut-ins. A b of 1.7 with a 35-year tail is the signature of a multi-completion, multi-restart history, not of one completion draining one interval. Re-fitting the four-well average over 240 months gives qi 279 bbl/d, Di 1.9/yr, b 1.34: 259 bbl/d in month 1 and 315 kbbl to 10 bbl/d, close to the IFR curve.
2. **TEC-10 is the only single-completion, continuously produced, daily-measured well.** Fifteen months of daily data (Sep 2018 to Nov 2019) plus the 2020–22 commingled field sales (of which TEC-10 is ~90 %) fit qi 152 bbl/d, Di 0.79/yr, **b 0.49**: 181 bbl/d in the first full month, 78 bbl/d at 12 months, ~45 bbl/d at 33 months, ~21 bbl/d at 45 months. EUR to 10 bbl/d about 104 kbbl. Water cut went from 42 % to 67 % in the first year. TEC-10 is decaying three to four times faster than the type curve.

## 2. Every TEC-12 number in circulation, on one basis

| Case | First month bbl/d | Month 12 | Month 36 | 1-yr cum | 5-yr cum | 20-yr cum | EUR (kbbl) | Note |
|---|---|---|---|---|---|---|---|---|
| IFR 2020 type curve, no limit | 300 | 112 | 61 | 62.1 | 157.6 | 314.5 | 407 | 417 months |
| IFR 2020 curve to 10 bbl/d | 300 | 112 | 61 | 62.1 | 157.6 | 314.5 | 380 | |
| IFR 2023 economics, incremental TEC-12 | 300 | 112 | 61 | 62.1 | 157.6 | — | 235 | economic limit Nov 2034 (task 1) |
| GLJ YE2020 1P TEC-12 Dir | 196 | 129 | 65 | 58.1 | 160.1 | 203.0 | 203 | GLJ economic life, 116 months |
| GLJ YE2020 2P TEC-12 Dir | 221 | 157 | 89 | 68.0 | 204.6 | 340.3 | 343 | the "343/345 kbbl" |
| GLJ YE2020 3P TEC-12 Dir | 270 | 194 | 113 | 83.5 | 257.7 | 452.9 | 502 | |
| Petrel Robertson base | 100 | (37) | (20) | (20.7) | (52.5) | (76.1) | >100 stated | PR gives rate and EUR only; profile shape assumed |
| Petrel Robertson upside | 200 | (74) | (41) | (41.4) | (105.0) | (209.5) | ~200 stated | as above |
| Simmons low / most likely / upper / high | 120 / 170 / 235 / 300 | | | | | | 390 / 504 / 652 / 799 | **8-year sales of TEC-12 plus TEC-13 together**, not a single-well EUR |
| TEC-10 actual, Arps fit (15 months + sales) | 147 | 80 | 32 | 39.7 | 92.8 | 103.5 | 104 | b 0.49 |
| Four PEMEX wells, average, Arps fit | 259 | 111 | 56 | 59.5 | 148.0 | 270.0 | 315 | b 1.34, includes recompletions |
| **Recommended low (P90)** | 100 | 54 | 22 | 27.0 | 63.2 | 65.5 | **65** | TEC-10 shape at the PR base rate |
| **Recommended base (P50)** | 180 | 104 | 53 | 49.8 | 133.2 | 217.6 | **218** | b 0.9, Di 0.79/yr |
| **Recommended high (P10)** | 300 | 128 | 65 | 69.0 | 171.7 | 313.1 | **366** | PEMEX-average shape at the IFR rate |

Values in brackets are derived from an assumed shape, not from the source.

## 3. Why the sources disagree by a factor of four

- **Rate assumption**: 100 (Petrel Robertson) to 300 bbl/d (IFR). GLJ 1P at 196 and TEC-10's own first full month at 181 sit in the middle. The IFR 300 is the four-well average of 1956–73 initial rates from wells that tested 350–580 bbl/d on their first perforations; nothing drilled since 2018 has started above 200.
- **Decline shape**: the type curve (b 1.7) and GLJ (b about 1.2 to reach 343 kbbl from 221 bbl/d) assume a PEMEX-style tail. TEC-10 (b 0.49) does not show one. GLJ's YE2020 forecast for TEC-10 itself (80 bbl/d through 2021, 212 kbbl remaining 2P) was overtaken within a year: the field sold 49 bbl/d in 2021 and 23 bbl/d in 2022 with TEC-2 included (G-39).
- **What is being counted**: Simmons' 390–799 kbbl are eight-year sales of two wells (TEC-12 from March 2021, TEC-13 from January 2022); the review's table presents them next to single-well EURs (G-40). The 2023 economics' 235 kbbl is the IFR curve cut at an economic limit driven by USD 10,000/month battery cost and 44 % royalty.

## 4. Recommendation: one base case with a range

| | Low (P90) | **Base (P50)** | High (P10) |
|---|---|---|---|
| First-month rate | 100 bbl/d | **180 bbl/d** | 300 bbl/d |
| Di (nominal) / b | 0.79/yr / 0.49 | **0.79/yr / 0.90** | 1.91/yr / 1.34 |
| Month 12 / 36 | 54 / 22 | **104 / 53** | 128 / 65 |
| Cum 1 yr / 5 yr / 10 yr | 27 / 63 / 65 kbbl | **50 / 133 / 178 kbbl** | 69 / 172 / 236 kbbl |
| EUR at 10 bbl/d | 65 kbbl (5.6 yr) | **218 kbbl (18 yr)** | 366 kbbl (30 yr) |
| Basis | TEC-10's own decline at Petrel Robertson's base rate | TEC-10 rate class, decline eased for a well 16.5 m higher with ~15 m of pay against TEC-10's 2.5 m perforated | the IFR / PEMEX-average curve: requires a 30-year life with recompletions |

The base case is deliberately anchored on the one modern well rather than on 1956 initial rates. It sits at GLJ 1P on volume (218 vs 203 kbbl) with a lower first-year rate and a longer tail, which is what the pressure history (task 5: 2 % depletion, strong aquifer) and TEC-10's water-cut trajectory together imply: rate is water-limited from the first year, but the reservoir does not run out of energy. The IFR 345–400 kbbl curve should be presented as the upside that a PEMEX-style recompletion programme could reach, not as the expected case, and Petrel Robertson's 100 bbl/d as the downside.

For the economics rebuild (tasks 8 and 10): use the base profile in `tec12_profiles_monthly.csv`, the 2023 workbook structure with the AFE new-drill cost, and run low and high as sensitivities.

## 5. Checks

- Four-well average reproduced from the tidy database against the IFR workbook: max difference 25 bbl/d after month 1, 88 bbl/d in month 1 (partial-month convention).
- GLJ TEC-12 profile sums (203.0 / 342.9 / 501.8 Mbbl) equal the totals in the workbook header.
- TEC-10 fit with and without the 2020–22 sales points gives the same EUR within 2 kbbl; the late points are consistent with the 15-month decline.
- The base case at 180 bbl/d reproduces TEC-10's first-year cumulative (50 vs 40–44 kbbl actual) within the rate scaling.
