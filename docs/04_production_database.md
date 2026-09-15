# Task 4 — Tecolutla production database

Script: `src/production_db.py`. Outputs in `data/processed/`:

| File | Content |
|---|---|
| `tecolutla_production.parquet` / `.csv` | 1,341 tidy rows, one per well × month × source: `well, date, source_kind, oil_bbl, water_bbl, gas_mcf, days_on, days_in_month, oil_bpd_cd, water_cut, gor_scf_bbl, perf_top_mkb, perf_base_mkb, zone, source_file, source_sheet, quality_flag` |
| `tecolutla_field_monthly.csv` | one "best available" field oil series 1960-01 to 2022-12 with the `basis` named for every month, 163 months carrying `no record` |
| `tecolutla_production_allocations.csv` | the 12 block totals of the March 2020 "By Zone" summary, with how much of each is covered by monthly records |
| `tecolutla_tec10_daily.csv` | 431 daily TEC-10 records, 20 Sep 2018 to 24 Nov 2019 (oil, gas, water, tubing pressure) |
| `tecolutla_production_gaps.csv` | 76 gaps: 66 runs of missing months inside the CNH record plus 10 documented pre-record or post-record gaps |
| `tecolutla_gor_flags.csv` | 174 well-months with GOR above 1,500 or below 150 scf/bbl |
| `production_summary.json` | totals, cross-checks, cumulative GORs |
| `figures/04_production_history.png` | rate, water cut, GOR and cumulative, plotted with line breaks at every missing month |

Nothing has been interpolated. Depths are mMD (perforation `From/To (mkb)` as reported by CNH) and mSS where the source gives them.

## 1. Sources and what each covers

| `source_kind` | Source (file → sheet) | Wells | Period | Rows | Notes |
|---|---|---|---|---|---|
| `cnh_monthly_pemex_era` | `appraisal_plan/Production (Tecolutla).xlsx` → `Production` | TEC-2, 6, 7, 9 | 1966-01 to 2016-01 | 1,174 | CNH monthly volumes (oil, water, gas, producing days, perforation interval). Identical to `Tecolutla Production History (Possible Solution GOR).xlsx` on all 1,161 common rows (max difference 0); the 13 extra rows are TEC-2 2015-01 to 2016-01 |
| `cnh_monthly_field_level` | `appraisal_plan/Tecolutla Production to Dec 2018.xlsx` → `DATA`, WELL = CAMPO | field | 1960-01 to 1965-12 | 68 | field total only, no well split; rate × days |
| `tonalli_monthly_test_2018` | same file → `DATA` | TEC-10, TEC-2 | 2018-07 to 2018-12 | 7 | Tonalli test months ("Testing; PEMEX #") |
| `tonalli_daily_sum` | `tec12_drill/2023-09-29 Tec-12 Economics.xlsm` → `Tec-10 Prod` | TEC-10 | 2018-09 to 2019-11 | 15 | sums of the daily sheet; `days_on` = days with a record |
| `tonalli_trucking_sales` | `staff_production/Tecolutla Production Tracking.xlsx` → `TRUCKING` | TEC-10, TEC-2 (to 2019-08); TEC-7, TEC-11 (water hauls only); CAMPO TECO (commingled field, 2019-07 to 2022-12) | 2018-07 to 2022-12 | 54 | PEMEX-measured oil per truck ticket; loads to MOZUTLA-1/-7 are water disposal |
| `pemex_statement_sales` | same file → `Reconciliation` | field | 2018-09 to 2020-11 | 23 | monthly PEMEX statement volumes (the invoiced basis) |

Forecast rows in the same workbooks (`TYPE = FORECAST`, the GLJ forecast tables, the transition-plan table) are excluded; they belong to task 6.

## 2. Field cumulative: the 2.0 MMbbl and the 1.67 MMbbl reconciled (closes G-11)

The March 2020 "By Zone" summary (`Tecolutla Production Summary (by well by perf interval).xlsx`) totals **1,936,255 bbl**. That is the "2.0 MMbbl" in the review and the work program. It is built from:

| Well | Interval mMD (mSS) | Period | bbl | Of which in monthly records | Basis of the rest |
|---|---|---|---|---|---|
| TEC-6 | 2336–2338 (2330–2332) | 1956-10 to 1972-02 | 509,993 | 122,004 | "derived from wellfile summary"; the sheet's own note says 117,394 bbl is in CNH data |
| TEC-6 | 2324–2327 | 1972-02 to 1976-01 | 84,293 | 84,293 | |
| TEC-6 | 2314–2316 (2308–2310) | 1976-03 to 2006-12 | 305,499 | 305,499 | |
| TEC-2 | 2335–2339 (2331–2335) | 1956-06 to 1972-01 | 40,885 | 2,730 | wellfile |
| TEC-2 | 2307–2311 (2303–2307) | 1972-01 to 2016-01 | 320,334 | 320,334 | |
| TEC-2 | 2307–2311 | 2019-06 to 2020-03 | 7,812 | 0 (commingled sales) | Tonalli |
| TEC-7 | 2335–2337 | 1957-01 to 1957-03 | ? | 0 | "no data" |
| TEC-7 | 2335–2337 | 1968-06 | 40 | 40 | |
| TEC-7 | 2310–2313 (2305–2308) | 1971-10 to 2006-12 | 266,988 | 266,988 | |
| TEC-9 | 2328–2333 (2314–2319) | 1973-05 to 2012-07 | 352,601 | 352,601 | |
| TEC-10 | 2349.5–2353 (2311.5–2315) | 2018-07 to 2020-03 | 47,811 | 0 (see below) | Tonalli |
| **Total** | | | **1,936,255** | 1,454,489 | **481,767 bbl are block totals with no monthly record** |

So 25 % of the quoted field cumulative rests on a PEMEX wellfile summary for TEC-6 1956–1965 and TEC-2 1956–1972 rather than on monthly records. The "Table" sheet in the same workbook states the method: *"missing ~500 Mbbl (compared to executive summary from dataroom); Allocated to Tec-6 based on wellfile reporting."* The number is an allocation, not a measurement.

The review's per-well table (TEC-6 ~899 kbbl, TEC-9 353, TEC-2 361, TEC-10 ~55) sums to 1.67 MMbbl because it omits TEC-7 (267 kbbl). With TEC-7 it is 1.94 MMbbl, the same figure. G-11 is closed: there is no missing 0.33 MMbbl, only an omitted well.

The database's own best-available monthly series sums to **1,715 kbbl** from 1960 to Dec 2022 (records only). Adding the 429 kbbl of wellfile block totals for 1956–1965 that fall before the field-level series (the TEC-6 388 kbbl and TEC-2 38 kbbl not covered by any monthly record) gives about 2.14 MMbbl. The overlap between the CNH field-level 1960–65 series (182 kbbl) and the TEC-6 wellfile block is unknown, so the honest statement is: **field cumulative to end-2022 is between 1.72 MMbbl (recorded) and about 2.1 MMbbl (with wellfile allocations), and the 2.0 MMbbl in circulation is the March 2020 allocation figure plus nothing after March 2020.** Post-March-2020 sales add 39 kbbl (Apr 2020 to Dec 2022) to whichever basis is used.

## 3. Gaps (the kickoff's "pre-1960" and "1965–1972")

| Gap | What exists | What does not |
|---|---|---|
| 1956-06 to 1959-12 | initial tests (TEC-2 453 bbl/d, TEC-6 579 bbl/d, TEC-7 352 bbl/d); wellfile block totals | any monthly volume, field or well |
| 1960-01 to 1965-12 | CNH field-level monthly, 182 kbbl, 75–115 bbl/d | any well split |
| 1966-01 to 1971-12 | TEC-6 monthly only (TEC-7 one month, 1968-06) | TEC-2 and TEC-7 monthly (TEC-2 was on the 2335–2339 m interval; TEC-7 "no data") |
| 1972 onward | all four wells monthly, with 66 runs of missing months (1978-06 to 1979-09 across all wells; TEC-6/9 1999-02 to 2003; TEC-7 1990-02 to 2006-09; TEC-2 1999-02 to 2006-08) | whether the missing months are shut-in or unreported; the CNH table has no zero rows |
| 2016-02 to 2018-06 | nothing (field shut in at handover) | |
| 2019-12 to 2022-12 | commingled field sales only (CAMPO TECO tickets; PEMEX statements to 2020-11) | any per-well volume for TEC-10 or TEC-2 after Nov 2019 |
| 2020-04 to 2020-06 and 2022-03 to 2022-10 | nothing | sales tickets or statements |

TEC-2 2015-01 to 2016-01 (13 rows present only in the later copy of the CNH table) are flagged: oil is integer bbl/d and water rises by exactly 390.01 bbl every month, which is hand entry, not measurement.

## 4. Modern era (Tonalli, 2018–2022)

- **TEC-10**: daily sheet gives 44,468 bbl over 431 recorded days (20 Sep 2018 to 24 Nov 2019); peak month Oct 2018 at 181 bbl/d producing-day average, 77 bbl/d by mid-2019, water cut 42 % rising to 67 %, tubing pressure falling from 875 to 450 psi. Trucking tickets attribute 29,399 bbl of PEMEX-measured oil to TEC-10 up to Aug 2019, after which sales are commingled. The By Zone summary's 47,811 bbl to Mar 2020 is consistent with the daily sheet plus four further months at ~70 bbl/d.
- **TEC-2**: 2,456 bbl sold Sep 2018 to Aug 2019 per tickets; By Zone gives 7,812 bbl Jun 2019 to Mar 2020.
- **TEC-7 and TEC-11**: water hauls only (3,252 and 4,397 bbl to Mozutla disposal, 2019); no oil sold from either. TEC-11's 26 loads in May–Aug 2019 are the only production record of the well.
- **Field sales**: PEMEX statements total 63,146 bbl Sep 2018 to Nov 2020; tickets total 54,104 bbl for the commingled CAMPO TECO stream Jul 2019 to Dec 2022. Field rate fell from ~130 bbl/d (Oct 2018) to ~70 bbl/d (2019–2020), ~50 bbl/d (2021) and ~30 bbl/d (2022).
- Tonalli's own measurements and PEMEX's differ by −1,301 bbl over Sep 2018 to Nov 2020 (−2 %), per the Reconciliation sheet.

## 5. The GOR anomaly

Reference values:

| Basis | GOR scf/bbl | Source |
|---|---|---|
| PEMEX PVT, RGA 59.9 m³/m³, Pb 132 kg/cm² (1,877 psi) | 336 | `6 -Resumen Campo Tecolutla.docx` table 5 |
| Initial well tests 1956–1973 | 431–765 | By Zone "Test Info" |
| TEC-6 flowing survey, 2 Dec 1964 (OCR of the PEMEX form) | 685 (RGA 122 m³/m³ at 9 m³/d oil) | `pressures/Tecolutla-6 Static Gradient Dec 2, 1964.pdf` |
| Cumulative produced GOR 1966–1992 | 565 | this database |
| IFR "possible solution GOR" | 552 | `PVT Calculator (Tecolutla).xlsx` Oil!C7, an assumed input, which gives Pb 2,849 psi |
| TEC-10 initial test Oct 2018 | 762 | By Zone |

What the monthly data show (`tecolutla_gor_flags.csv`, figure panel 3):

1. **1966–1992 the field produced at 400–800 scf/bbl**, cumulative 565, i.e. at or a little above solution GOR. The reservoir was undersaturated and there is no gas cap signal. IFR's 552 is evidently this cumulative figure, not a laboratory value, and the PEMEX 336 is inconsistent with 27 years of production; one of the two PVT bases is wrong (G-31).
2. **24 months carry an identical GOR in every producing well** (1973-01, 1982, 1988-05 to -08, 1990, 1992-03 to 1993-01, 2008-02, 2011-04). Gas was allocated by a field ratio in those months, so per-well GOR is not measured data.
3. **1993–1999 GOR rose to 1,000–3,000 scf/bbl** in all wells at once (cumulative 1,073 for the period) while oil fell below 30 bbl/d per well. A simultaneous rise in every well at low rate is an allocation or metering effect (gas measured at the battery against small, poorly measured oil volumes), not a reservoir change; reservoir pressure at the time (task 5) will confirm.
4. **TEC-2 2013–2016: 2,000–20,000 scf/bbl** on 6–12 bbl/d of oil and 60–100 bbl/d of water. Gas volumes of 20–180 mcf/d against 8 bbl/d of oil; the well was effectively a water producer with the field's gas metered to it. These 37 months account for 87 mmcf of the 965 mmcf recorded and should be excluded from any material-balance GOR.
5. **TEC-10 2018–2019: 640–2,470 scf/bbl**, high during clean-up (Sep 2018), 650–950 through the first year, then rising above 1,800 from Aug 2019 as tubing pressure fell to 450–500 psi. This is the only per-well, daily-measured GOR in the field. A rise at low flowing pressure in a single well next to the aquifer is most simply near-wellbore gas breakout below bubble point, which requires Pb above ~500 psi at the sandface; it is consistent with the IFR Pb of 2,849 psi and not with the PEMEX Pb of 1,877 psi if the flowing pressure stayed above 1,877 psi, which it did not.

Resolution for the review: the field's solution GOR is about 550–570 scf/bbl on the evidence of 27 years of production; the anomalies are (a) field-allocated gas in specific months, (b) a late-life allocation artefact on TEC-2, and (c) a genuine but local GOR rise on TEC-10 at low tubing pressure. None of them indicates a gas cap or reservoir-wide depletion below bubble point. The PEMEX PVT table (336 scf/bbl, 20 °API) does not describe this fluid and should not be used; the Intertek 2018–2019 TEC-10 oil analyses in `fluid_analyses/` need to be read for a measured Rs and Pb (task 5).

## 6. Cross-checks

- The two CNH monthly workbooks agree exactly on 1,161 common rows.
- Per-well CNH totals reproduce the By Zone summary to the barrel for every interval with monthly coverage (TEC-6 305,499 and 84,293; TEC-7 266,988; TEC-9 352,601; TEC-2 320,334).
- Field-level 1960–65 rates (75–115 bbl/d) are consistent with TEC-6 alone producing 80–100 bbl/d in 1966–67 when its monthly record begins.
- TEC-10: monthly sums of the daily sheet (Oct–Dec 2018: 5,607 / 4,929 / 4,524 bbl) exceed the Tonalli test-month figures in the Dec 2018 workbook (4,349 / 4,693 / 3,980 bbl) by 5–15 %, and the ticketed PEMEX oil (4,340 / 4,666 / 3,980) matches the test-month figures. The daily sheet is wellhead production; the tickets are sales after BS&W and shrinkage. Both are kept, with different `source_kind`.
