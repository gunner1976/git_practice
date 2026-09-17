# Tecolutla (AC-24) — wells, wellbore schematics, operations and reserves: source notes for the handover deck

Compiled 17 Sep 2026 from the files under `data/raw/`, `data/processed/` and the Drive renderings listed in `data/processed/deck_notes/drive_reads_notes.md`. Every fact carries its source (file → sheet/cell, page or slide; Drive id where the file is not in the repo). Nothing is inferred except under "Reader's notes" (section 5). Depths are mMD below KB unless marked mSS (subsea) or mTVD. Spanish source text is translated; original wording kept where a term matters.

Conventions: `WP` = `data/processed/drive_text/Tecolutla_Work_Program_Tec-12_Drill.pdf.txt` (Tonalli Work Program deck, Feb 2021 / Sep 2023 copy); `Resumen` = `data/raw/appraisal_plan/6 -Resumen Campo Tecolutla.docx` (PEMEX/CNH data-room field summary, 2014 basis); `ByZone` = `data/raw/appraisal_plan/Tecolutla Production Summary (by well by perf interval).xlsx`; `Tracking` = `data/raw/staff_production/Tecolutla Production Tracking.xlsx`; `GLJ20` = `data/processed/drive_text/YE2020_Reserves_Corporate_Summary_Detail_Final.pdf.txt` (GLJ, effective 31 Dec 2020, run 26 Feb 2021 / printed 17 Mar 2021); `GLJ21` = Drive 1cILp0-IlG0Km_H_CArRWF4XkI8R1GsqX "Tecolutla (Tonalli) - December 31, 2021 Reserve Report (Draft 1)" (GLJ project 1223410, run 1 Apr 2022), rendered text; `DRN` = `drive_reads_notes.md`; `Prog12` = `data/raw/tec12_regulatory/Programa de perforación Tecolutla 12.pdf` (Tonalli, Sept 2020, 73 pp); `Term12` = `data/raw/tec12_regulatory/PROGRAMA DE TERMINACIÓN TECOLUTLA-12DES VER1.0.pdf` (22 pp); `PE2017` = Drive 1P7EHEf7_Kx0d3Q1ggtlNiN1mOJBudD1q "Plan de Evaluación (Tecolutla) 0517" (May 2017, machine-translated rendering).

---

## 0. Source register

| Source | What it contributes | Readability |
|---|---|---|
| `data/raw/geology/Tecolutla Well header Information/Tecolutla Well Header Information.csv` | UWI, KB, TD, lat/long, UTM for 9 wells | clean |
| `data/raw/geology/Tecolutla Perforations/Tecolutla Perforations  Informaiton.csv` | perforation top/base and status for 8 wells (TEC-11 "PROPOSED") | clean |
| `Resumen` (docx) | PEMEX 2014 field summary: history, OOIP/reserves 2014, RF, well status count, petrophysics, PVT, tests, type-well completion, HSE/permits text | clean; it has no per-well history section beyond TEC-2 tests and the 4-well status count |
| `data/raw/appraisal_plan/Transition plan-Production chapter.docx` | 2022 transition-programme forecast (TEC-10/12/13), decline method, TEC-10 test rates, tubing design note | clean |
| `ByZone` | cumulative oil by well and interval to Mar 2020, rig-release dates, test rates | clean |
| `data/processed/tecolutla_production.csv`, `production_summary.json`, `tecolutla_production_allocations.csv` | reconciled monthly database (task 4) | clean |
| `data/processed/drive_text/Masterlog_Tecolutla_10_470_a_2490m.pdf.txt` | TEC-10 header: casing, hole sizes, mud, spud/TD | text rendering of a graphic log; lithology columns not captured |
| `data/raw/petrophysics/LAS/TECOLULTA-10_CBL-VDL-GR-CCL_CASING 7IN.las` | CBL header (KB 5.13, GL 1.00, TD 2,490, logger TD 2,428; 31 May 2018); casing block in the header lists only the 13 3/8" 54.5# string | clean header |
| `data/raw/tec11/Tecolutla 11_Tieback 4 12_Graficas_181218.pptx` | 5 slides, images only: Halliburton iCem charts of the TEC-11 4 1/2" tie-back cementation, 18 Dec 2018 | images read (see 2.5 TEC-11) |
| `data/raw/drilling_costs/TEC-11 Drilling Cost Tracker 26Dec2018.xlsx`, `TEC-10 Updated Drilling Cost Summary 15Jun2018.xlsx` | day-by-day TEC-11 cost (9 Nov–26 Dec 2018), TEC-10 AFE programme text and actuals | clean |
| `data/raw/development_plan/Tec 11 Summary of Costs (Actual and Budgeted).xlsx` | TEC-11 actual vs budget by phase | clean |
| `Prog12`, `data/raw/ye2020_reserves/PROGRAMA DE PERFORACIÓN TECOLUTLA-12DES VER1.1.pdf`, `Term12`, `data/raw/tec12_regulatory/Tecolutla-12DES Perforacion.pdf` | TEC-12 planned design; VER1.1 (74 pp) and "Tecolutla-12DES Perforacion" (73 pp) are the same Sept-2020 programme (same casing table, TD, dates) | text; figures (mechanical sketch, trajectory plots) not captured |
| `data/raw/tec12_drill/TEC-12 Build&Hold Well Design.pdf`, `TEC-12 S-Shape Deviation Plan.pdf`, `Tec-12 Time vs Depth.pdf`, `Petrel Robertson Tec-12 Assessment.pdf` | sketch casing/tubing; S-shape survey; TEC-11 lessons; PR reservoir opinion | clean |
| `data/raw/appraisal_plan/20180726 Tec-10 Quick IPR2.xlsx` | TEC-10 IPR from the 6 Aug 2018 test | clean |
| `data/raw/appraisal_plan/HWrates (TEC-11).xls` | Babu–Odeh horizontal-well productivity model (pre-drill screening), not test rates | clean |
| `data/processed/welltest/tec10_welltest_2018_daily.csv`, `data/processed/tec10/tec10_mudlog_intervals.csv` | TEC-10 flowback 23 Jul–6 Aug 2018; mud-log intervals | clean |
| `data/raw/development_plan/Tecolutla 10 Final Report (IHS PTA) Spanish.pdf`, `Tecolutla 2 Final Report (IHS PTA) Spanish.pdf` | IHS build-up analyses (Jul–Aug 2018 TEC-10; May 2018 TEC-2) | first 7 pages read |
| `Tracking` | Reconciliation, TRUCKING (885 tickets Jul 2018–Dec 2022), PIVOT, Acronyms. **No daily-ops, tank, downtime or personnel sheets exist in this workbook** | clean |
| `data/processed/drive_text/Tabla_Informe_Mensual_CNH_Nov2022.xlsx.txt`, `Anexo_III.8.III_Consolidado_Anual_Produccion_2020/2021.pdf.txt`, `Tabla_Produccion_2021_and_2022_CNH_forecast.xlsx.txt` | CNH filings | clean renderings |
| `data/raw/cnh_reports/Nov-22/*.xlsx` (= contents of `Anexo I. Formatos mensuales Tonalli Nov-22.zip`) | CNH DGM monthly measurement formats, Nov 2022 | clean |
| `data/raw/tec12_drill/Tonalli Contractual Fee and Exploration Tax.xlsx` | LISH art. 45/55 fees per km² | clean |
| `GLJ20`, `data/raw/ye2020_reserves/2021-02-19 Tecolutla YE Reserve Report - Draft (100 ).xlsx`, `Gross Oil Monthly Forecast by Well (Kevin).xlsx` | YE2020 reserves (final and 19 Feb 2021 draft) | text; plots garbled |
| `GLJ21` (Drive rendering) | YE2021 draft reserves | text; summary-of-values page partly garbled, reconstructed below |
| `data/raw/appraisal_plan/GLJ jan22.xlsx`, `Petrel Robertson Volumetrics.xlsx` | GLJ Jan-2022 price deck; PR OOIP cases | clean |
| `docs/03_tec11_facies.md`, `04_production_database.md`, `06_forecast.md`, `07_volumetrics.md`, `13_cnh_filings_gis_cmi.md`, `15_pemex_settlements.md`, `gaps.md` | repo results | clean |
| `data/raw/ye2020_reserves/Tonalli - Management Reservoir Engineer Questions 2020.pdf` | **not read** (not opened in this pass) | — |
| Drive `Inventarios Tonalli Energía SASISOPA.xlsx` (1Kc7j1UecnAlj6lfjQotqkkwDiaqFUEGc, Apr 2020) | 107-line materials inventory (two identical sheets) | rendered as flat CSV; parsed at 29 columns/row |

---

## 1. Field frame

- Location: municipality of Tecolutla, Veracruz, ~60 km ESE of Poza Rica; Tampico–Misantla basin; Faja de Oro terrestre; formerly PEMEX asignación AR-0463; field area 2.5 km² (Resumen §i). Contract CNH-R01-L03-A24/2016 (all CNH formats). Contract area stated as 7 km² in Prog12 p.6 and 7.162 km² in the fee workbook (`Tonalli Contractual Fee and Exploration Tax.xlsx!H13`).
- Discovery: TEC-2 completed 9 Jun 1956 in El Abra, 453 bpd initial; peak field rate 932 bpd in Mar 1972; cumulative to 1 Jan 2014 1.9 MMbbl oil, 1.7 Bcf gas (Resumen §i, §vi).
- PEMEX-era handling: production to the "Estación de recolección Vicente Guerrero" (gathering for Gutiérrez Zamora, Tecolutla and Vicente Guerrero fields), trucked to Batería de Separación Ezequiel Ordóñez (Resumen §i). PE2017 line 306/320: all four producers flowed to a single collection battery, gas vented or burned; "from February 2016 all wells have been suspended or abandoned".
- PEMEX 2014 well status: 4 wells drilled, 1 producer, 1 closed, 2 plugged "sin posibilidades" (Resumen Tabla ii.4). Reader's note: this counts only the AR-0463 development wells (TEC-2, 6, 7, 9); TEC-3, 5 and 101 are the exploratory/plugged wells.
- Operator chain: PEMEX (1956–2016) → Tonalli Energía S.A.P.I. de C.V. (IFR 50 % / Grupo IDESA 50 %), licence awarded 2018 per GLJ20 p.6 (contract dated 2016 per the CNH id) → 25 Aug 2022 Petro Frontera (IFR) bought IDESA's 50 %, then sold 50 % to Jaguar Exploración y Producción for USD 850,000, Jaguar to become operator (DRN, Drive 1ffaRgawITP0SXxh-eCjETW54mTkkie6J).

### 1.1 Well header table (`Tecolutla Well Header Information.csv`, rows 3–11)

| Well | UWI | KB m | TD m | Lat | Long | UTM X | UTM Y |
|---|---|---|---|---|---|---|---|
| TEC-2 | 1030022460 | 4.00 | 2,375 | 20.454036 | −97.010058 | 707,586.77 | 2,262,986.35 |
| TEC-3 | 1030022461 | 6.00 | 2,381 | 20.458041 | −97.007398 | 707,858.90 | 2,263,433.11 |
| TEC-5 | 1030022462 | 4.00 | 2,562 | 20.459603 | −97.020943 | 706,443.52 | 2,263,588.88 |
| TEC-6 | 1030022463 | 6.00 | 2,339 | 20.449917 | −97.011000 | 707,493.99 | 2,262,529.05 |
| TEC-7 | 1030022466 | 5.00 | 2,340 | 20.451464 | −97.006651 | 707,945.70 | 2,262,705.90 |
| TEC-9 | 1030022465 | 5.00 | 2,340 | 20.448139 | −97.007769 | 707,833.50 | 2,262,336.31 |
| TEC-101 | 1030022464 | 8.00 | 2,363 | 20.452191 | −97.012482 | 707,336.30 | 2,262,779.00 |
| TEC-10 | TEC_10 | 6.13 | 2,490 | 20.449077 | −97.010235 | 707,574.96 | 2,262,437.07 |
| TEC-11DES | TEC-11DES | 4.70 | 3,283 | 20.454439 | −97.009878 | 707,605.00 | 2,263,031.17 |

Other KB/TD sources that differ: TEC-6 KB 5.67 m, PT 2,338.9 m (PEMEX 1956 final report, DRN 1c2-WKxk…); TEC-5 KB 4.00, PT 2,562.1 (DRN 19i5buDs…); TEC-9 KB 5.07, GL 1.24, TD 2,340 mMD / 2,331.2 mTVD (PEMEX estado mecánico, DRN 1ys9wOiU…); TEC-10 KB 5.13 / GL 1.00 (masterlog header and CBL LAS) vs 6.13 (header CSV, survey) — resolved by decision to 6.13 (`docs/gaps.md` G-46); TEC-101 TD 2,804 m (PE2017 well table line 608 and PEMEX estado mecánico) vs 2,363 in the header CSV (the CSV value is unexplained — flag). Top El Abra per GLJ YE2019 map (DRN 1xGo-WvPj…): TEC-6 −2,294; TEC-9 −2,295.87; TEC-2 −2,302; TEC-7 −2,304.2; TEC-10 −2,309.93; TEC-11 −2,311.88; TEC-101 −2,334; TEC-5 −2,551 mSS.

---

## 2. Wells

### 2.0 One-line well summary

| Well | Type | Operator | Spud | Completed / rig release | TD mMD (mTVD) | KB m | Formation at TD | Current status | Sources |
|---|---|---|---|---|---|---|---|---|---|
| TEC-3 | exploration, vertical | PEMEX | 10 Feb 1956 | 7 Mar 1956 (abandoned) | 2,380.5 | 6.00 | El Abra (top; open-hole test 2,376.8–2,380.8) | plugged 1956; LKO −2,374.2 mSS used by GLJ | PE2017 l.288, l.600; header CSV; GLJ20 p.8 |
| TEC-2 | discovery, vertical | PEMEX → Tonalli | 16 Apr 1956 | 31 May 1956; producer 9 Jun 1956 | 2,375 (2,379 in PE2017) | 4.00 (3.8 in the 1956 survey) | El Abra | shut in (Sep 2019; commingled test Jan 2020); abandonment reserve USD 102,893 | ByZone Table; Resumen §i; DRN |
| TEC-5 | exploration, vertical | PEMEX | 25 Jun 1956 | 28 Jul 1956 (plugged) | 2,562.1 | 4.00 | El Abra (5 m penetrated, 248 m low to TEC-2) | plugged 1956 | DRN 19i5buDs…, 1VCktsVx… |
| TEC-6 | development, vertical | PEMEX | 8 Sep 1956 | 15/16 Oct 1956 | 2,338.9 | 5.67 (6.00 CSV) | El Abra (36 m penetrated) | abandoned by PEMEX after Dec 2006 | DRN 1c2-WKxk…; ByZone; PE2017 l.604 |
| TEC-7 | development, vertical | PEMEX → Tonalli | 21 Nov 1956 | 22–25 Jan 1957 | 2,340 | 5.00 | El Abra | shut in; converted to water injector Aug 2019; abandonment reserve USD 101,376 | DRN 1UZlBMHq…, 11Wasndd… |
| TEC-101 | deep exploration, vertical | PEMEX | 15 Apr 1972 | 31 May 1972 (ByZone) / 31 Oct 1972 (PE2017) | 2,804 (CSV says 2,363 — flag) | 8.00 | El Abra (deep); Lower Cretaceous/Jurassic objective not reached | plugged 1972, water-invaded | PE2017 l.302, l.608; DRN 1a00morB… |
| TEC-9 | development, slightly deviated ("S") | PEMEX | 1 Apr 1973 | 7 May 1973 TD; 19 May 1973 completed | 2,340 (2,331.2) | 5.07 (5.00 CSV) | El Abra (30 m below top at 2,310) | closed Jan 1999 (CNH record to Jul 2012); casing damaged 544–718 m; returned to CNH/SENER | DRN 1ys9wOiU…; WP |
| TEC-10DES | development, directional (J) | Tonalli | 11 Apr 2018 (QMAX) / 16 Apr 2018 (masterlog) | TD 1 May 2018; on production Oct 2018 | 2,490 (2,488 mMD = ~2,446 mSS per the CMI zone table in docs/13) | 6.13 (5.13 masterlog/CBL) | El Abra (~180 m below top) | shut-in producer (last produced Nov–Dec 2022); abandonment reserve USD 99,124 | Masterlog; DRN; docs/gaps G-46 |
| TEC-11DES | development, horizontal | Tonalli | 11 Nov 2018 | 18 Dec 2018 TD; rig release 26 Dec 2018; completion finished 6 Sep 2019 | 3,283 (2,331 mSS, 82°) | 4.70 | El Abra lateral, 2,305–2,331 mSS | 100 % water; composite plug ±2,400 mMD Aug 2019; temporary abandonment notice Apr 2022; candidate injector | tracker; docs/03; DRN 18kU9Zb7… |
| TEC-12DES | planned development, directional | Tonalli (Jaguar operator-designate from Aug 2022) | not drilled | — | 2,360 (2,341) planned | 8.2 planned | El Abra (target −2,296 mSS) | Programa de Transición approved 18 Jul 2022; not drilled | Prog12; Term12; DRN |

### 2.1 Wellbore schematic data (all wells)

| Well | String | OD | Weight / grade | Shoe or interval mMD | Cement / notes | Source |
|---|---|---|---|---|---|---|
| TEC-2 | surface | 9 5/8" | — | 607.87 | drilled 13 1/4" to 610 m | Prog12 p.66 §21.1 |
| TEC-2 | production | 6 5/8" | J-55 / N-80 | 2,307.38 | 8 5/8" hole to 2,321.7 m; cement drilled out to 2,321.7 | Prog12 p.66 |
| TEC-2 | liner | 4 1/2" | — | to 2,375 (set with running tool, cemented) after deepening with 5 5/8" bit | top of liner ~2,280 mSS ("ToL@2,280mSS / 7" CSG shoe @2,303mSS" on the TEC-2 sketch: `Tantoyuca TEC-2,6,9.pptx` slide 1 text — note the slide says 7", Prog12 says 6 5/8") | Prog12 p.66; pptx |
| TEC-2 | tubing | 2 7/8" + 2 3/8" (type well: "TR 4 1/2" y aparejo de producción de 2 7/8"") | — | — | Resumen §vii; Transition plan docx ("tramos de 2-3/8" en el fondo" in the old wells) | |
| TEC-2 | Tonalli 2019 work | — | — | "2019–2020 m IV. Disparo con pistolas RTG 1 11/16"" (shallow perforation, purpose not stated) | Tonalli estado mecánico 18 Feb 2019, DRN 1RxpD0jw… (diagram only) | |
| TEC-3 | — | — | — | open hole 2,376.8–2,380.8 tested (980 m oil + 80 m water recovered in pipe) | no casing data in any file | PE2017 line 288; Perforations CSV |
| TEC-5 | surface | 9 5/8" | J-55 36# | 501.35 (501.3) | open hole 8 5/8" to 2,562.1; cement plugs/labels at 477.8, 525 and 2,505.3 m; plugged 28 Jul 1956 | PEMEX estado mecánico 2006, DRN 1VCktsVx…; PEMEX 1956 report DRN 19i5buDs… |
| TEC-6 | surface | 9 5/8" | — | 499.5 | 13 1/4" hole to 510 m | PEMEX 1956 report DRN 1c2-WKxk…; Prog12 p.67 |
| TEC-6 | production | 6 5/8" | J-55 / N-80 | 2,302.0 (2,280 in the 1956 report) | 8 5/8" hole to 2,310.8 | Prog12 p.67; DRN |
| TEC-6 | liner | 4 1/2" | — | 2,336; liner top 2,280 | 5 5/8" hole to 2,336; then 3 7/8" hole 2,336–2,338 (open-hole producing interval) | Prog12 p.67; DRN |
| TEC-6 | tubing | 2 3/8" and 2 7/8" | — | — | | DRN 1c2-WKxk… |
| TEC-6 | plugs | bridge plug 2,303–2,304 | | | Perforations CSV | |
| TEC-7 | surface | 9 5/8" | J-55 36# (ID 8.921") | 600.48 | | PEMEX estado mecánico 2006 DRN 1UZlBMHq…; Tonalli final Aug 2019 DRN 11Wasndd… |
| TEC-7 | production | 6 5/8" | J-55 20# (ID 6.049") / N-80 24# (ID 5.921") | 2,306.50 | | same |
| TEC-7 | liner | 4 1/2" | J-55 11.6# (ID 4.0") | top 2,281, shoe 2,340 (PT) | | same |
| TEC-7 | plugs | permanent plug 2,325; mechanical plug 2,330; markers 2,315 / 2,338 | | old perfs 2,335–2,337 below the plug | same |
| TEC-7 | 2019 completion | 2 3/8" 8RD EUE tubing + 4 1/2" 11.6# mechanical packer at ±2,300 m | | **water-injection string** (Tonalli, 26 Aug 2019); wellhead 9 5/8" × 6 5/8" × 2 3/8" | DRN 11Wasndd… |
| TEC-9 | surface | 9 5/8" | J-55 36# | 502.0 | 12 1/4" hole to 505 m; fish (4 1/2" slips) at 388 m in first hole, cemented | PEMEX estado mecánico DRN 1ys9wOiU…; Prog12 p.67 |
| TEC-9 | production | 6 5/8" | P-110 28# | 2,340 (PT 2,340 mMD / 2,331.2 mTVD); **no liner** | 8 1/2" hole | same; WP ("Tec-9 did not [run a liner]") |
| TEC-9 | tubing | 2 7/8" to 2,318 m + 2 3/8" | | | DRN 1ys9wOiU… |
| TEC-9 | damage | casing "very large damage" 544–718 m after milling during a failed PEMEX workover; prospect interval cemented without being perforated; well closed, not properly abandoned; tree in bad condition; returned to CNH/SENER by Tonalli; wellhead now a monument with plate | | | WP; DRN |
| TEC-101 | surface | 9 5/8" | N-80 40# | 807.19 | fish at 926 m; open hole 8 5/8" 2,718–2,804 (PT 2,804); markers 55, 590, 829, 2,335 m; plugged 31 Mar 1972, water-invaded, structurally low | PEMEX estado mecánico DRN 1a00morB… |
| TEC-10 | conductor | 13 3/8" | 54.5# (CBL header) | 30–40 m (masterlog "0–40"; Halliburton conductor report "at 30 m"; QMAX table "to 40 m") | 17 1/2" hole (masterlog) / 16" conductor to 30 m in the AFE programme | Masterlog header; CBL LAS; DRN 1_5UzGZII…; AFE Cover row 17 |
| TEC-10 | surface | 9 5/8" | 32.3# H-40 STC | 470 (masterlog) / 471 (QMAX, Prog12 p.67) | 12 1/4" hole; Halliburton 16 Apr 2018: ExtendaCem 1.50 92.8 bbl + GasStop 1.90 29.6 bbl, 21 bbl returns to surface; WBM 1.26 | Masterlog; DRN 1_5UzGZII… |
| TEC-10 | production | 7" | 26# L-80 | 2,282.72 (masterlog) / 2,285 (Halliburton post-op) / 2,288 (QMAX, programme) | 8 3/4" hole to 2,288 (masterlog; QMAX says 8 1/2"); Halliburton 27 Apr 2018: OBM 1.36, 60 bbl Tuned Spacer III 1.45, lead ExtendaCem 1.50 163.5 bbl to surface, tail GasStop 1.90 75.5 bbl (top 370 m), displaced with 1.10 brine, **cement to surface observed**, casing tested 500 psi | Masterlog; DRN 16_dQsnwO… |
| TEC-10 | liner | 4 1/2" | 11.6# L-80 (Halliburton) — the injectivity-test header says P-110 13.5# STC | shoe 2,489.33, top 2,133.42 (Weatherford hanger) | 6 1/8" hole 2,288–2,490 (bit 2 was 8 1/8"? masterlog text ambiguous; QMAX: 6 1/8" PDC); 27 bbl GasStop/Tuned Light 1.45, brine 1.13; 4 May 2018 | DRN 10f2RlOT…; Masterlog |
| TEC-10 | tubing | 2 7/8" (2,319.95 m) + 2 3/8" (122.83 + 352.29 m) + 4 1/2" 109.65 m "producción" | API 5CT | run May–Jun 2018 | SASISOPA inventory rows 11–14, 19 (see 3.1.4); packer "Empacador mecánico 6 5/8"" row 50; AFE programme step 18: 4 1/2" 20.09 kg/m L-80 liner with permanent packer, step 20: retrievable bridge plug at 500 m | inventory; AFE Cover rows 33–35 |
| TEC-10 | wellhead | 9 5/8" × 7" × 2 7/8" 5M; tree 7 1/16" × 2 9/16" × 2 1/16" 5K | | | inventory rows 1–10, 48; Prog12 p.59 (TEC-12 uses the same) |
| TEC-10 | perforations | C1 2,349.5–2,350.5; C2 2,351.5–2,353.0 (active); B 2,394.5–2,398.5, 2,404–2,406, 2,410–2,414 (inactive, "no inflow"); A 2,433.5–2,442.5 (active per CSV, "no inflow" per ByZone; injectivity test 30 Jun–1 Jul 2018: admission at 2,120 psi, 0.5 bpm at 3,000–3,500 psi, 48 bbl, tight) | | | Perforations CSV; ByZone rows 30–32; IHS PTA p.1; DRN 1XyZ35a9… |
| TEC-11DES | conductor | 13 3/8" | — | (hammered, "as in TEC-11" per WP) | inventory row 67: 57.03 m of 13 3/8" delivered 30 Nov 2018 | WP; inventory |
| TEC-11DES | surface | 9 5/8" | — | proposals 472/500 m (DRN); inventory 320.37 m delivered | | DRN (1o4iHKGh…, 1db5Xfhc…) |
| TEC-11DES | intermediate/production | 7" | 26# | shoe 2,354.44 (open hole 2,357 mMD, 61° inclination) | Halliburton 25 Nov 2018, rig SE 836: 51 centralisers, OBM 1.36, ExtendaCem 1.50 166 bbl + HalCem 1.90 43 bbl, 306 bbl brine, returns to surface, 3,200 psi final | DRN 1CL89Fst… |
| TEC-11DES | liner + tie-back | 4 1/2" | 11.6# (3,829.99 m delivered) + 56.39 m 4 1/2" N-80 | liner to TD 3,283 mMD (survey); tie-back to surface cemented 18 Dec 2018 (iCem chart: spacer 1.45 g/cc at 13:07, TunedLight slurry 1.24 g/cc at 13:27, displacement from 13:48–13:51, ~130 bbl total; line test 4,500 psi) | liner-hanger damaged; "tie-back string faulty and then damaged, fishing lost tie-back pieces; two cement jobs for liner" | inventory rows 70–71; tieback pptx images 1–2; WP; `Tec-12 Time vs Depth.pdf` |
| TEC-11DES | tubing | 2 3/8" J-55 2,155.37 m; 2 3/8" L-80 151.93 + 2,156.72 m; 2 3/8" N-80 253.44 m; FIP hanger 7 1/16" × 2 7/8"; ASI-X HP packer for 4 1/2" 11.6# (12 Aug 2019) | | run Jun–Aug 2019 (completion); Tonalli "ESTADO MECANICO FINAL" Jul 2019 (well unnamed): 220 joints 2 3/8" EUE L-80, XO 2 7/8" × 2 3/4", ASIX packer at 2,057.28 m | inventory rows 83–88; DRN 1HUjuDEt… |
| TEC-11DES | plug | composite blind plug (TCI, 10,000 psi; "Tapón 4 1/2" 13.5 Boss @ 2400 md") set in the 4 1/2" liner at ±2,400 mMD, 11–12 Aug 2019; killed with 1.06 brine; no cement; tubing-less per 2024 abandonment sheet | | | DRN 18kU9Zb7…, 1-Zlu4S3E…, 1XSHXSKe… |
| TEC-12DES (planned) | conductor | 13 3/8" | J-55 54.5# BCN, ID 12.615" | ±30 m, hammered | | Prog12 p.18, p.27; Term12 p.9 |
| TEC-12DES | surface | 9 5/8" | H-40 32.3# STC, ID 9.001" | 500 mMD/TVD, 12 1/4" hole, polymer WBM 1.10–1.26 | lead 1.5 g/cc 0–350 m, tail 1.9 g/cc 350–500 m; 13 centralisers; TOC surface | Prog12 p.27–31 |
| TEC-12DES | production | 7" | L-80 26# BCN, ID 6.276" | 2,360 mMD / 2,341 mTVD (TD), 8 1/2" hole, invert-emulsion OBM 1.32–1.36 | lead 1.5 g/cc 0–1,696 m, tail 1.9 g/cc 1,696–2,360 m; 61 centralisers; TOC surface; FIT 5 m below each shoe | Prog12 p.27, p.34–35, p.50 |
| TEC-12DES | tubing | 2 7/8" | TSH511 6.5# L-80, ID 2.441" | 238 joints to 2,201.8 m, no packer ("sin empacador mecánico") in Term12; the earlier sketch shows 2 7/8" with hydraulic packer at 2,200 m | integral hanger 7 1/16" | Term12 p.12; `TEC-12 Build&Hold Well Design.pdf`; `TEC-12 Proposed S-Shaped Well Design.pptx` |
| TEC-12DES | wellhead | 9 5/8" × 7" × 2 7/8" 5K SBU (Weatherford), tree 7 1/16" 5M × 2 9/16" × 2 1/16"; PSL2, class EE (H2S 1.75 %, CO2 4.78 %) | | | Prog12 p.59, p.64; Term12 p.13 |
| TEC-12DES | perforations | to be selected from logs; 2 1/8" exposed guns, 20 spf, 60° phase, HMX DP; matrix acid 3 m³ xylene + 3 m³ 15 % HCl per interval, bullhead ≤4,000 psi | | | Term12 p.13, p.17 |

Casing data **missing or contradictory** (flagged): TEC-3 (no strings anywhere); TEC-2 production string quoted as 6 5/8" (PEMEX operations summary in Prog12) and 7" (Tonalli sketch); TEC-2 liner shoe 2,375 vs TD 2,379 in PE2017; TEC-6 6 5/8" shoe 2,280 (1956 report) vs 2,302 (Prog12); TEC-10 7" shoe 2,282.72 / 2,285 / 2,288 in three sources; TEC-10 liner grade 11.6# L-80 vs P-110 13.5#; TEC-11 9 5/8" setting depth not confirmed by a post-job report in the repo (proposals 472/500 m only); TEC-11 liner top / tie-back depths not in text (the iCem charts have no depth annotations); TEC-101 header CSV TD 2,363 vs 2,804 elsewhere; TEC-10 KB 5.13 vs 6.13.

### 2.2 Perforation and interval status (`Tecolutla Perforations  Informaiton.csv` unless stated)

| Well | Interval mMD | Status (CSV) | Interval mSS (ByZone) | Dates / cumulative (ByZone, database) |
|---|---|---|---|---|
| TEC-2 | 2,307.4–2,311 | ACTIVE | 2,303–2,307 | Jan 1972–Jan 2016: 320,334 bbl (peak monthly 269 bbl/d Mar-72); Jun 2019–Mar 2020: 7,812 bbl (Tonalli) |
| TEC-2 | 2,311–2,320 | PROPOSED | | |
| TEC-2 | 2,330–2,331; 2,341–2,342 | Bridge PLUG | | |
| TEC-2 | 2,335–2,339 | SQUEEZED | 2,331–2,335 | Jun 1956–Jan 1972: 40,885 bbl; initial test 453 bbl/d, 541 scf/bbl, up to 9.4 % wcut |
| TEC-2 | 2,345–2,349; 2,353–2,354 | SQUEEZED | 2,341–2,345 | Jun 1956 test 353 bbl/d (0.881 SG), 431 scf/bbl, 9.6 % wcut at 580 psi Ptbg; 0 bbl produced |
| TEC-3 | 2,376.8–2,380.8 | OPEN HOLE | | 1956 test, oil and water in pipe; plugged 7 Mar 1956 |
| TEC-5 | — | No perforations | | plugged |
| TEC-6 | 2,303–2,304 | Bridge PLUG | | |
| TEC-6 | 2,314–2,316 | SQUEEZED | 2,308–2,310 | Mar 1976–Dec 2006: 305,499 bbl (peak monthly 293 bbl/d Aug-77) |
| TEC-6 | 2,320–2,321 | SQUEEZED | | |
| TEC-6 | 2,324–2,327 | SQUEEZED | 2,318–2,321 | Feb 1972–Jan 1976: 84,293 bbl; test 264 bbl/d, 532 scf/bbl, 2 % wcut |
| TEC-6 | 2,336–2,338 | OPEN HOLE | 2,330–2,332 | Oct 1956–Feb 1972: 509,993 bbl (of which only 117,394 in CNH monthly data; rest "derived from wellfile summary"); test 579 bbl/d, 576 scf/bbl, 3.4 % wcut (elsewhere 484 bbl/d, 543 scf/bbl) |
| TEC-7 | 2,310–2,313 | ACTIVE | 2,305–2,308 | Oct 1971–Dec 2006: 266,988 bbl; test 478 bbl/d, 437 scf/bbl, 0.2 % wcut |
| TEC-7 | 2,335–2,337 | SQUEEZED | 2,330–2,332 | Jan–Mar 1957 "no data"; Jun 1968 40 bbl; test 352 bbl/d, 521 scf/bbl, 7.5 % wcut |
| TEC-9 | 2,328–2,333 | SQUEEZED | 2,314–2,319 | May 1973–Jul 2012: 352,601 bbl; test 189 bbl/d, 765 scf/bbl, 0.6 % wcut. Prog12 p.10: "3 intervalos potencialmente productores" never exploited |
| TEC-101 | 2,718–2,804 | SQUEEZED | | open hole, never produced |
| TEC-10 | 2,349.5–2,350.5; 2,351.5–2,353 | ACTIVE | 2,311.5–2,315 | Jul 2018–Mar 2020: 47,811 bbl; peak daily test 232 bbl/d oil, 762 scf/bbl, 25.3 % wcut at 772 psi Ptbg (20 Oct 2018) |
| TEC-10 | 2,394.5–2,398.5; 2,404–2,406; 2,410–2,414 | INACTIVE | | "no inflow" (ByZone zone 2, 2,394.5–2,413.5) |
| TEC-10 | 2,433.5–2,442.5 | ACTIVE (CSV) / "no inflow" (ByZone zone 1) | | injectivity test Jun–Jul 2018, tight |
| TEC-11DES | ten 2-m intervals 2,624–2,806 mMD (2,624–26, 2,658–60, 2,674–76, 2,688–90, 2,701–03, 2,727–29, 2,743–45, 2,756–58, 2,783–85, 2,804–06) | PROPOSED | lateral 2,305–2,331 mSS (survey, `docs/03_tec11_facies.md`) | actual completion: acid bullheaded without isolation (selective tool could not pass the damaged liner hanger); some oil then 100 % water (WP) |

ByZone "Table" sheet rig-release dates: TEC-3 7 Mar 1956; TEC-2 31 May 1956; TEC-5 28 Jul 1956; TEC-6 15 Oct 1956; TEC-7 22 Jan 1957; TEC-101 31 May 1972; TEC-9 7 May 1973. Note there: "missing ~500 Mbbl (compared to executive summary from dataroom); allocated to Tec-6 based on wellfile reporting".

### 2.3 Cumulative production by well

Two bases exist. (a) ByZone allocation (Mar 2020): 1,936,255 bbl. (b) Reconciled monthly database (`data/processed/tecolutla_production.csv`, computed with pandas, records only):

| Well | First record | Last record | Oil bbl | Water bbl | Gas Mcf | Source kind |
|---|---|---|---|---|---|---|
| FIELD 1960–65 | 1960-01 | 1965-12 | 181,800 | 159,675 | 0 | CNH field-level monthly |
| TEC-2 | 1972-01 | 2016-01 (+ 2018-09 test month 411 bbl) | 320,334 (+411) | 262,788 | 337,483 | CNH monthly |
| TEC-6 | 1966-01 | 2006-12 | 507,185 | 149,645 | 272,916 | CNH monthly |
| TEC-7 | 1968-06 | 2006-12 | 267,028 | 41,151 | 130,067 | CNH monthly |
| TEC-9 | 1973-05 | 2012-07 | 352,601 | 266,478 | 224,918 | CNH monthly |
| TEC-10 | 2018-09 | 2019-11 | 44,468 (daily sheet) | 56,789 | 52,165 | Tonalli daily sums |
| TEC-10 | 2018-07 | 2018-12 | 13,956 | 18,118 | — | Tonalli test months |
| TEC-11 | 2019-05 | 2019-08 | 0 | 4,397 hauled | — | trucking (water only) |
| TEC-7 (2019) | 2019-06 | 2019-07 | 0 | 3,252 hauled | — | trucking (water only) |
| CAMPO TECO (commingled sales) | 2019-07 | 2022-12 | 55,598 tickets / 63,146 PEMEX statements Sep 2018–Nov 2020 | | | trucking / statements |

PEMEX-era per-well total 1,447,147 bbl (`production_summary.json`). GLJ cumulative basis (GLJ20 Table 1, to Dec 2020): TEC-10 58 Mbbl / 69 MMcf / 111 Mbbl water; TEC-2 329 / 347 / 254; TEC-6 507 / 273 / 150; TEC-7 267 / 130 / 41; TEC-9 353 / 225 / 266; total 1,514 Mbbl oil, 1,043 MMcf, 821 Mbbl water. GLJ21 Table 1 (to Dec 2021): TEC-10 76 / 84 / 184; field 1,531 Mbbl oil, 1,058 MMcf, 895 Mbbl water; TEC-10 last quarter 2021: 35 bbl/d oil, 40 Mcf/d, 210 bbl/d water, WC 86 %, GOR 1,127.

### 2.4 Per-well histories

**TEC-3** (exploratory, 1956). Spud 10 Feb 1956, TD 2,380.5 m on 7 Mar 1956 (PE2017 line 288, table line 600). Drilled to top El Abra; open-hole test 2,376.8–2,380.8 m recovered 980 m of oil and 80 m of water in the pipe; abandoned 7 Mar 1956 (PE2017). PEMEX 1956 TEC-6 report: "TEC-3 (plugged, salt water) limits the NE flank" (DRN 1c2-WKxk…). GLJ used its lowest known oil, −2,374.2 mSS, as the field OWC (GLJ20 p.8). Status: plugged ("corky" = taponado in the machine translation). Casing: none recorded.

**TEC-2** (discovery well). Spud 16 Apr 1956, rig release 31 May 1956, TD 2,375 m (PE2017 table; ByZone Table). Completed 9 Jun 1956 as oil/gas producer in El Abra, 453 bpd initial (Resumen §i). Three 1956 tests (Resumen Tabla vi.1): 2,307.4–2,321.7 m: 258 bpd oil, 1.7 MMcfd gas, RGA 1,163 m³/m³, PTP 174 kg/cm², 6 mm choke; 2,345–2,349 m: 352 bpd, 0.153 MMcfd, RGA 77, PTP 40; 2,335–2,339 m: 453 bpd, 0.244 MMcfd, RGA 96, PTP 64. PEMEX operations (Prog12 p.66): 13 1/4" hole to 610 m, 9 5/8" at 607.87; 8 5/8" hole to 2,321.7, 6 5/8" J-55/N-80 at 2,307.38; packer Lane-Wells BOCL 6 5/8" at 2,275.8; interval 2,307.4–2,321.7 acidised with 1,900 L; flowed water then gas and some oil; on 6 mm choke 41 m³/d oil, 47,702 m³/d gas, RGA 1,163, TP 174 kg/cm²; Pwf 234 kg/cm² at 2,310 m, Ps 252 kg/cm² (the field "initial pressure", 24.7 MPa; a 2 h 45 min reading per `docs/gaps.md` G-36); well killed, deepened with 5 5/8" bit to 2,375 m, logged, 4 1/2" liner run and cemented to 2,375 m. Produced 2,335–2,339 m 1956–72 (40,885 bbl), then 2,307–2,311 m from Jan 1972 (320,334 bbl to Jan 2016; peak month 269 bbl/d Mar 1972) (ByZone). PEMEX table: last production Dec 2014, "Closed" (PE2017 line 600). Late-life GOR 2,000–20,000 scf/bbl 2013–16 on 6–12 bbl/d oil, an allocation artefact (`docs/04_production_database.md` §5). Tonalli: static gradient 27 Mar 2018 (23.6 MPa at 2,250 m, 24.1 MPa at datum; WP pressure table); IHS build-up 10–30 May 2018 on 2,307–2,311 m: pi 3,508 psia, k 50 mD, h 8 m, skin +196, final flow 50 bbl/d oil, 453 bbl/d water, Pwf 2,436 psia, WHP 515 psia (IHS TEC-2 report p.5–6); cumulative 320.30 Mbbl oil, 337.79 MMcf, 190.87 Mbbl water at 17 May 2018. Tonalli 2019 estado mecánico shows a perforation "2019–2020 m" with RTG 1 11/16" guns (DRN 1RxpD0jw…; purpose unknown). Tonalli production: Sep 2018 test month 411 bbl; tickets 2,456 bbl Sep 2018–Aug 2019; ByZone 7,812 bbl Jun 2019–Mar 2020 "currently producing". Directors' memo 6 Sep 2019: TEC-2 uneconomic, shut in Sep 2019 (USD 8 k demobilisation) (DRN 1DvcwTMU…). GLJ note: "2020-Jan-31 commingled for testing with Tecolutla-10" (GLJ20 Table 2.2 note 2); GLJ Table 1 last production 2020-09; CNH 2020 filing origin "Pozos Tecolutla 2 y Tecolutla 10", 2021 filing TEC-10 only. 2024 abandonment reserve: TEC-2 vertical 2,375 m, shut-in, USD 102,893 (DRN 1XSHXSKe…). Status: shut in since 2020 at the latest; casing per Prog12; a 2" flowline runs 0.52 km from TEC-10DES to the "TEC-2DES platform" (abandonment sheet).

**TEC-5** (exploratory, 1956). Spud 25 Jun 1956, TD 28 Jul 1956, PT 2,562.1 m; 1,290 m NW of TEC-2; GL 0.30, KB 4.00; 9 5/8" at 501.3 m only; El Abra at 2,555 m (2,551 mSS), 248 m lower than TEC-2; full Tertiary–Upper Cretaceous column (San Felipe 58 m, Chicontepec Inferior 55 m) — marks the separation from Miguel Hidalgo; structurally low, water; plugged, no tests (PEMEX 1956 report DRN 19i5buDs…; estado mecánico 2006 DRN 1VCktsVx…: cement plugs 477.8, 525, 2,505.3 m). Never produced.

**TEC-6** (development, 1956). Spud 8 Sep 1956, TD 16 Oct 1956 (rig release 15 Oct per ByZone), PT 2,338.9 m; GL 2.19, KB 5.67; 9 5/8" at 499.5, 6 5/8" at 2,280 (1956 report) / 2,302.0 (Prog12), 4 1/2" liner 2,302–2,336 (liner top 2,280), tubing 2 3/8" + 2 7/8"; open hole 2,336–2,338 drilled with a 3 7/8" bit; 6 bbl acid (960 L); initial 77 m³/d (484 bbl/d) oil, 7,485 m³/d gas, RGA 97, 3.4 % water, 0.876 g/cm³, TP 40 / TR 7 kg/cm²; salinity 5,200 ppm; El Abra 2,302 mMD / 2,296 mSS, 7 m higher than TEC-2; Tantoyuca directly on El Abra (DRN 1c2-WKxk…; Prog12 p.67). Three completions: 2,336–2,338 (Oct 1956–Feb 1972, 509,993 bbl allocated), 2,324–2,327 (Feb 1972–Jan 1976, 84,293 bbl), 2,314–2,316 (Mar 1976–Dec 2006, 305,499 bbl, peak 293 bbl/d Aug 1977) (ByZone; Prog12 p.12 uses 509,490). Static gradients 1964, 1971 (14 surveys Aug–Oct 1971, 23.2–24.4 MPa at datum), 4 Jun 1973 (22.8 MPa, Pflowing 16.6 MPa before shut-in) (WP pressure table; `data/raw/pressures/`). Petrel Robertson: "definite water breakthrough each time the well is restarted; GOR steady" (PR assessment p.2). Last production Dec 2006; PEMEX table status plugged ("corky") (PE2017 line 604). WP: "Tec-6 was abandoned before the upper section was perfed. We do not know the reason"; un-perforated pay 2,294–2,307 mSS. Bridge plug 2,303–2,304 mMD (Perforations CSV). Not in the 2024 abandonment reserve (already abandoned by PEMEX). Status: abandoned.

**TEC-7** (development, 1956–57). Spud 21 Nov 1956, completed 22–25 Jan 1957, TD 2,340 m (PE2017; PEMEX estado mecánico). Casing 9 5/8" J-55 36# at 600.48; 6 5/8" J-55 20# / N-80 24# at 2,306.50; 4 1/2" J-55 11.6# liner 2,281–2,340; tubing 2 7/8" (PEMEX 2006 estado mecánico DRN 1UZlBMHq…). Initial 352 bpd from 2,335–2,337 m (PE2017; ByZone test 352 bbl/d, 521 scf/bbl, 7.5 % wcut); Jan–Mar 1957 "no data"; recompleted 2,310–2,313 m Oct 1971 (test 478 bbl/d, 437 scf/bbl, 0.2 % wcut), 266,988 bbl to Dec 2006 (ByZone). Static gradients 8 Dec 1964 (24.6 MPa datum) and 6 Oct 1998 (24.5 MPa) (WP table). Last production Dec 2006, "Closed" (PE2017 line 604). Logs lost by PEMEX (`docs/gaps.md` G-14). Tonalli 2019: 19 water loads (3,252 bbl) hauled from TEC-7 in Jun–Jul 2019 (Tracking); 26 Aug 2019 final estado mecánico: permanent plug 2,325 m, mechanical plug 2,330 m, last interval 2,310–2,313 m, 2 3/8" EUE tubing with 4 1/2" mechanical packer at ±2,300 m — a **water-injection string**; wellhead 9 5/8" × 6 5/8" × 2 3/8" (DRN 11Wasndd…). Directors' memo Sep 2019: "water-injection rental at TEC-7" among shared costs (DRN 1DvcwTMU…). 2024 abandonment reserve: TEC-7 vertical 2,340 m, shut-in, USD 101,376. Status: shut-in, equipped as injector; injected volumes not recorded in any file read.

**TEC-101** (deep exploratory, 1972). Spud 15 Apr 1972, rig release 31 May 1972 (ByZone) / 31 Oct 1972 (PE2017 table), objective Lower Cretaceous / Jurassic syn-rift; drilling problems at 2,678 m, "the drilling rig was left in the well" (PE2017 line 302 — machine translation; the estado mecánico records a fish at 926 m); PT 2,804 m; 9 5/8" N-80 40# at 807.19; open hole 8 5/8" 2,718–2,804; plugged 31 Mar 1972 [sic in the PEMEX card], water-invaded, structurally low (DRN 1a00morB…). Petrel Robertson: karst "sinkhole" access to the aquifer, "e.g. TEC-101" (PR assessment p.1). Top El Abra −2,334 mSS (GLJ YE2019 map). Never produced. Header CSV TD 2,363 is inconsistent with 2,804 — flag.

**TEC-9** (development, 1973). Spud 1 Apr 1973, TD 7 May 1973, completed 19 May 1973; GL 1.24, KB 5.07; UTM 707,873.67 / 2,262,243.38; 12 1/4" hole, 9 5/8" J-55 36# at 502 m; 8 1/2" hole, 6 5/8" P-110 28# at 2,340 m, no liner; tubing 2 7/8" to 2,318 + 2 3/8"; top El Abra 2,310 mMD / 2,296 mSS; deviated from 296 m (a dropped piece of equipment changed the plan — WP), max 11°15' N6°15'W, 112–118 m displacement, back to vertical from 1,192 m, PT 2,340 mMD / 2,331.2 mTVD; gas shows at 2,071, 2,194, 2,330 (slight) and 2,340 (strong); perforations 2,328–2,333 mMD (2,319–2,324 mTVD; 2,314–2,319 mSS); logs induction, sonic, microlog, dipmeter, GR, CBL; initial May 1973 on 3.5 mm choke 91.6 m³/d oil (ByZone: 189 bbl/d, 765 scf/bbl, 0.6 % wcut), RGA 230; final Sep 1998 30 m³/d oil, 4 % water, RGA 155, TP 86 / TR 50 kg/cm²; closed Jan 1999 (PEMEX estado mecánico DRN 1ys9wOiU…; Prog12 p.67). CNH monthly record continues to Jul 2012, cumulative 352,601 bbl, 266,478 bbl water, 224,918 Mcf (database). Failed PEMEX workover: restriction encountered and milled, casing damage 544–718 m, prospect interval (2,296–2,311 mSS = 2,310–2,325 mMD, 3–11 % porosity) cemented without being perforated; well closed, not properly abandoned; tree a safety and environmental hazard; returned to CNH & SENER by Tonalli; repair or sidetrack not recommended (6 5/8" casing, cemented) (WP; `Tec-12 Drill.pptx` slide 3). Status: closed/returned; wellhead a monument with plate.

**TEC-10DES** (Tonalli, 2018). AFE ST028 "Perforación del pozo TEC-10 pozo direccional" from a new 120 m × 110 m multi-well pad beside TEC-6; AFE USD 2,924,760 (1 Jan 2018 basis), actual USD 2,039,002 at 15 Jun 2018 (`TEC-10 Updated Drilling Cost Summary 15Jun2018.xlsx!AFE Cover O39, Drilling_Cost_Summary G73:H73`); programme: 16" conductor 30 m, 12 1/4" to 620 m with 9 5/8" 53.57 kg/m J-55, 8 3/4" (222.2 mm) vertical to 2,100 m with 7" 34.23 kg/m J-55 LT&C, 6 1/8" (156 mm) directional from 2,150 m, core in El Abra, TD ~2,500 m, 4 1/2" 20.09 kg/m L-80 liner with permanent packer, retrievable 7" bridge plug at 500 m (AFE Cover rows 15–36). As drilled: rig Diavaz DTM-638; spud 11 Apr 2018 (QMAX) / 16 Apr 2018 (masterlog header; mud logging from 470 m on 17 Apr); 13 3/8" 0–40 m, 9 5/8" 0–470 m, 7" 0–2,282.72 m; holes 17 1/2" / 12 1/4" / 8 3/4"; mud 1.05–1.10, 1.10–1.26, 1.32–1.36, then 1.05–1.15 g/cm³ in El Abra; connection gas 1,367–8,984 units 1,850–2,080 m; bit 1 8 3/4" Ulterra CF515 1,817 m in 98 h; core #1 28–30 Apr 2018 at ~2,352 m; formation gas at 2,422 m TG 5,172 ppm; TD 2,490 mMD on 1 May 2018 (Masterlog text). Surface 707,554.956 / 2,262,437.068; target 707,589.60 / 2,262,253.10 (masterlog); displacement 192.59 m S, 16.56 m E, 193.3 m total (WP); inclination ~19–20° at 2,208–2,317 mMD, azimuth ~S 8–10° E (QMAX). Cementing: 9 5/8" 16 Apr, 7" 27 Apr (cement to surface), 4 1/2" liner 4 May (top 2,133.42, shoe 2,489.33) (DRN). Logs: full open-hole suite 2,280.5–2,487 m 2 May 2018 (induction, porosity, dipole sonic, Stoneley, CMI image) (`data/raw/petrophysics/LAS/`); CBL 31 May 2018 (LAS). Core: Stratascan V603-18, six thin sections 2,352.15–2,353.24 m, 1–4 % visual porosity, no impregnation (DRN 1OG5lzvl…). Completion: zone A 2,433–2,443 m injectivity test 30 Jun–1 Jul 2018, tight (DRN 1XyZ35a9…); zones B no inflow; zone C 2,349.5–2,350.5 + 2,351.5–2,353.0 m produced; 2 7/8" tubing 2,319.95 m + 2 3/8" 475 m + 6 5/8" mechanical packer (SASISOPA inventory). Flowback 23 Jul–6 Aug 2018 on 12/64": oil 41→194 bbl/d, water 337→124 bbl/d, BS&W 89→39 %, GOR ~700–1,000, WHP 328→863 psig; 1,475 bbl oil cumulative (`tec10_welltest_2018_daily.csv`; IHS TEC-10 report p.5); "post-stim flow back yielded 1,475 bbl" (WP). IHS build-up 21 Jul–31 Aug 2018: pi 3,525 psia, k 18 mD, h 13.2 m, kh/µ 1,730 md·ft/cP, skin +4.9, constant-pressure boundary at 195 m (IHS p.5–6). IPR (6 Aug 2018): Ps 3,510 psi, Pwf 3,118, PI 0.78 bbl/d/psi, 306 bbl/d total at 58 % oil; Vogel suggested >1,000 bpd open-flow (`20180726 Tec-10 Quick IPR2.xlsx!Quick C6:C13`; Transition plan docx). On production 7–8 Oct 2018: 313 bbl/d liquid, 158 oil, 156 water, 292 Mcfd, 900 psi WHP (Transition plan docx); test peak 232 bbl/d oil 20 Oct 2018 (ByZone). Daily record 20 Sep 2018–24 Nov 2019: 44,468 bbl; Oct 2018 181 bbl/d, mid-2019 77 bbl/d, WC 42→67 %, Ptbg 875→450 psi (`docs/04_production_database.md` §4). GLJ: choke increased 25 Feb 2021, ~100 bbl/d in Jan 2021 (GLJ20 Table 2.2 note 1); 2021 average 47.9 bbl/d, WC 80.9 % (GLJ21). Only producing well in 2021; shut in 4 Feb 2022 with the field (DRN 1Z5EAMWG…); restarted late Nov 2022: 15 days, 2,260 bbl gross / 678 net, 1,582 bbl water, 0.9 MMcf flared, 30.9 °API, 1.6 % S, 48.8 lb/Mbbl salt; 916 bbl delivered at CAB Poza Rica (`CNH_DGM_VHP.xlsx!CNH_DGM_01_PM row 10`; `CNH_DGM_VHPM.xlsx!CNH_DGM_04_PIM row 10`). 2024 abandonment reserve: TEC-10DES J-shape 2,262 mTVD / 2,288 mMD [sic; these are the 7" shoe depths], shut-in, USD 99,124 (DRN 1XSHXSKe…). Status: shut-in producer (2023 status per the abandonment sheet).

**TEC-11DES** (Tonalli horizontal, 2018–19). AFE TON2018DR002 USD 2,250,000 (`TEC-11 Drilling Cost Tracker 26Dec2018.xlsx!N3:N4`); surface location on the TEC-2 pad (mud log header "LOCATION: TECOLUTLA-2"); pre-spud 9–13 Nov 2018, drilling days 1–38 = 11 Nov–18 Dec 2018, rig release 26 Dec 2018 (tracker row 7); drilling cost to 26 Dec 2018 USD 3,025,996 (tracker AZ54). Drilled 11 Nov–18 Dec 2018 (CNH abandonment notice, DRN 18kU9Zb7…). Rig SE 836 (Halliburton 7" report). Trajectory: kick-off below 1,000 mMD, 47° at 2,209 mMD, 60° at 2,318 mMD (2,225 mSS), 80° at 2,563 mMD (2,305 mSS), 90° at 2,727 mMD (2,323 mSS), TD 3,283 mMD at 2,331 mSS and 82°, azimuth 316→331°, 1,190 m displacement (`docs/03_tec11_facies.md` §2). Problems (`Tec-12 Time vs Depth.pdf`; WP): pump failure on surface hole; auto-driller not functioning while building to 61°; last 24 h only 25 m (2,332–2,357 mMD); hydraulic-arm failure running the 7" (51.5 h from casing point 2,357 to cemented); liner hanger damaged; tie-back string faulty, fishing, two cement jobs. 7" 26# shoe 2,354.44 m cemented 25 Nov 2018 with returns to surface (DRN 1CL89Fst…); 4 1/2" liner and tie-back (3,830 + 56 m of 4 1/2" delivered 30 Nov/18 Dec 2018, inventory rows 70–71); tie-back cemented 18 Dec 2018 (iCem charts: line test to ~4,500 psi 11:52–12:01; job 13:07–14:40, spacer 1.45 g/cc, TunedLight 1.24 g/cc, ~130 bbl pumped; the pptx has no depth annotations). Mud log: carbonate dominant from 2,360 mMD; 923 m of carbonate section, 622 m mudstone–wackestone-dominant, 240 m with grainstone named (never pure), one moderate show 2,920–2,945 mMD; 31 m shale at 2,584–2,615 mMD; 30–40 % bentonite over the last 180 m (`docs/03_tec11_facies.md`). Costs: drilling USD 3,105,308 (budget 2,853,870), CBL/clean-up 129,360, completion May–Jun 2019 962,850 (budget 831,000), "Tantoyuca" Aug 2019 206,225 (incl. testing); total 4,403,743 vs 3,934,870 budget (`Tec 11 Summary of Costs (Actual and Budgeted).xlsx!Actual E7:G11`). Completion plan (same workbook, `TEC-11 Completion`): 20 perforated intervals, 20 stimulations, 14-day flow test, 30 days. Actual: the selective acid tool could not be run through the damaged liner hanger; acid pumped from surface without isolation; pressure broke down quickly, acid entered at low pressure and high rate; some oil on flowback then 100 % water ("acid likely entered a fracture and induced an overwhelming flow of water from the aquifer") (WP). Test 11 Jul 2019: 260 bpd water, 12/64", 195 psi WHP; completion finished 6 Sep 2019; composite blind plug at ±2,400 mMD 11–12 Aug 2019, killed with 1.06 brine, no cement; 18 Oct 2019 reclassified producer → injector with CNH; "Tantoyuca" test Aug 2019 (cost line; `20190824 Tecolutla-11 Oil Analysis Tantoyuca.pdf` exists in `fluid_analyses/`, not read) (DRN 18kU9Zb7…). Water hauled from TEC-11: 26 loads, 4,397 bbl, May–Aug 2019 (Tracking). Tubing string 2 3/8" J-55/L-80/N-80 with ASI-X packer run Jun–Aug 2019 (inventory rows 83–88); the 2024 sheet calls the well tubing-less, "water invaded", horizontal 2,331 mTVD / 3,246 mMD, USD 99,233 to abandon. GLJ: "TECOLUTLA-11 HZ" carried with no reserves in every category (GLJ20 Table 2.2). Status: temporarily abandoned (aviso art. 54, Apr 2022), possible future water injector.

**TEC-12DES** (planned; not drilled). Location on the TEC-10 pad ("Macropera Tecolutla-10"); conductor 707,582 / 2,262,425; target 707,753 / 2,262,460; GL 4.5 m, KB 8.2 m (3.7 m table); rig 836 Single 1,000 HP; directional, azimuth 78.433°, 174.5 m displacement; target El Abra at −2,296 mSS = 2,304.2 mTVD = 2,323.2 mMD; TD 2,341 mTVD / 2,360 mMD (−2,332.8 mSS) (Prog12 p.7–8; Term12 p.4 gives "3,341 md", a typo). Build-and-hold (14–15°) or S-shape (build to 13.5–15°, drop to vertical by 1,560 mMD, 175.2 m departure) plans (`TEC-12 S-Shape Deviation Plan.pdf`; Term12 p.10). Prognosis tops mTVD KB: Tuxpan 40.2; Escolín 734.2; Coatzintla 1,125.2; Palma Real Sup 1,751.2; Inf 2,011.2; Tantoyuca 2,218.2; El Abra 2,304.2 (Prog12 p.8). Casing: 13 3/8" J-55 54.5# hammered 30 m; 9 5/8" H-40 32.3# STC 500 m (12 1/4", polymer WBM 1.10–1.26); 7" L-80 26# BCN 2,360 mMD (8 1/2", invert emulsion 1.32–1.36 g/cm³, 230–270 kppm CaCl₂) (Prog12 p.27, p.38); cementing lead 1.5 / tail 1.9 g/cc, TOC surface both strings (p.30–35); design factors burst 1.10, collapse 1.0, tension 1.6, triaxial 1.25; kick tolerance MAASP 292 psi (9 5/8") and 1,808 psi (7") (p.29). Bits: 12 1/4" U519SS (ROP 25 m/h), 8 1/2" U616M (ROP 20 m/h) (p.46). Logging: MWD; open-hole litho-density, neutron, induction, GR 500–2,360 m; cuttings every 5 m, gas detector and chromatograph (p.49–50). Time: 12 1/4" phase 3.54 d, 8 1/2" phase 9.55 d, total 13.09 d (p.58); the time-analysis table drills vertical to 1,880, builds to 45° by 2,220 and 75° by 2,394 mMD — inconsistent with the 14–15° plans (p.56; flag). Cost in the programme: USD 289,674 + 515,076 = 804,750 (p.58) — this is the rig-phase cost only; the Work Program quotes "Total cost $1,500,000" and GLJ carries DCET 1,500 M$ (1,125 development + 375 tangible) (WP; GLJ20 Table 4). Completion (Term12): 2 7/8" TSH511 6.5# L-80 to 2,201.8 m without packer, integral hanger; perforate on wireline through tubing with 2 1/8" guns (20 spf, 60°, HMX); matrix acid 3 m³ xylene + 3 m³ 15 % HCl per interval, 0.8–2 bpm, ≤4,000 psi; 12 h soak; flow 7–60 days on 10–12/64" through test equipment, gas flared (p.12–18). Expected: 300 bpd liquid, 250 oil, 50 water (16.67 % WC), 0.51 MMcfd, reservoir pressure 3,597 psi; fluid 28.6 °API, 11.2 cP, GOR 2,041 scf/bbl [sic; "363.6 m³/m³"], H₂S 1.75 %; TEC-6 gas analysis CO₂ 4.78 %, H₂S 0.66 %, C1 79.81 % (Prog12 p.9). Regulatory: Programa de Transición request 2 Jul 2020 dismissed 7 Aug 2020; refiled 19 Nov 2021; Informe de Evaluación resolved unfavourably 3 Feb 2022; withdrawn 4 Feb 2022; Programa de Transición approved 18 Jul 2022 (CNH.E.56.001/2022) (DRN 1Z5EAMWG…, 1BJf7OGI…). GLJ schedule: on stream May 2021 (YE2020), May 2022 (YE2021); CNH forecast tables: month 3 of 2021, month 5 of 2022 (`Tabla_Produccion_2021_and_2022_CNH_forecast.xlsx.txt`); transition-plan forecast: Dec 2022 (Transition plan docx Tabla 1). Not drilled as of the 2024 abandonment sheet.

### 2.5 Pressure history (WP pressure table; datum 2,300 m below KB — see `docs/gaps.md` G-35)

| Date | Well | Type | Datum P MPa | Comment |
|---|---|---|---|---|
| 24 May 1956 | TEC-2 | static | 24.7 | oil at 2,210 m; the "original" pressure |
| 2 Dec 1964 | TEC-6 | flowing | 18.7 | 9 m³/d oil, 3 % water |
| 5–8 Dec 1964 | TEC-2 / TEC-7 | static | 24.3–24.6 | water level 1,151–2,045 m |
| Aug–Oct 1971 | TEC-6 | static (14) | 23.2–24.4 | |
| 4 Jun 1973 | TEC-6 | static | 22.8 | Pflowing 16.6 MPa pre shut-in |
| 6 Oct 1998 | TEC-7 | static | 24.5 | |
| 27 Mar 2018 | TEC-2 | static (extended) | 24.1 | |
| May 2018 / Aug 2018 | TEC-2 / TEC-10 | build-up (IHS) | 3,508 / 3,525 psia | 24.19 / 24.30 MPa at the gauge |

Reader's note: 2 % depletion in 62 years with 1.5–2.0 MMbbl produced: strong aquifer (also GLJ20 p.9 "strong aquifer support"; WP "reservoir pressure is currently at original pressure").

---

## 3. Operations

### 3.1 Facilities

**3.1.1 PEMEX era.** Single-well batteries per producer, gas vented, no separation or measurement inside the block; a gas-pipeline compression station lies just outside (PE2017 lines 306, 320, 702; Feb 2017 base-map captions DRN 1hSasL3U…). Oil to Estación de Recolección Vicente Guerrero, then trucked to Batería Ezequiel Ordóñez (Resumen §i).

**3.1.2 Tonalli 2017 plan (PE2017 lines 1760–1808, 2248–2390).** "Batería de recolección TEC-10" on the TEC-10 pad: two 36" × 120" horizontal three-phase separators with turbine meters (design 600 m³/d liquid, 180,000 m³/d gas), two 750-bbl API-650 tanks (1,500 bbl, expandable to six tanks / 4,500 bbl), separate water tank, fuel-gas system and generator (up to two 1.5 MW), dual-burner flare per API-521, discharge lines from TEC-2 and TEC-10, truck-loading meter (TOM tickets), trucks to PEMEX Ezequiel Ordóñez (EORD) pumping station, then PEMEX 12" line; injection-pump space for up to 2,000 m³/d at <14,000 kPag. Cost line "ST014 A24 Battery collection TEC-10" and "ST070 battery TEC-2" (Annex E).

**3.1.3 As built / as operated (2018–2022).**
- Production was handled at the wellsite through test equipment and hauled by truck; a 2" sch 80 A106 Gr B sour-service flowline spec from a 2" ANSI 300 wellhead take-off with hi/lo ESD to a metering manifold was issued Feb 2020 (TONALLI-INFRA-002, DRN 1LawOYRR…). Inventory row 89: 514 m of 2" A-106 Gr B pipe, 2" class 300 plug/check/safety valves, flanges, installed 17 Dec 2019. Abandonment sheet: 0.52 km 2" line TEC-10DES → "TEC-2DES platform".
- Separator: three-phase separator (ASME, RT1, NACE, PWHT, 0.125" CA) and an ecological burner (quemador ecológico) in operation from 8 Mar 2020 (inventory rows 106–107); abandonment sheet: separator 20" OD × 10 ft, 1,440 psi. Before that, separator rental at MXN 216,000/month (Sept 2019–Mar 2020 invoices) (DRN 1K3fXnOe…).
- Tanks: rented frac tanks (Oro Negro, MXN 32,000/month, invoices Jun 2019–Sept 2020) (DRN 1K3fXnOe…); a 60 m³ "presa" (pit/dam) in the abandonment list; no API-650 tank farm appears in any inventory read.
- Pumps: two motor-pumps (8.3 HP, 1,210 L/min, Oct 2018; solids-handling pump Jan 2019) (inventory rows 54, 72).
- Water disposal: hauled to third-party disposal 2018–Aug 2019 (see 3.4); from Aug 2019 TEC-7 equipped with a 2 3/8" injection string and packer at ±2,300 m (DRN 11Wasndd…) and "water-injection rental at TEC-7" is in the Sept 2019 cost base (DRN 1DvcwTMU…). CNH gas balance Nov 2022: 0.9 MMcf flared, "quema aprobada durante el programa de evaluación" (`CNH_DGM_BALANCES.xlsx!CNH_DGM_07_BG row 11`).
- Metering: Tonalli truck tickets with top/mid/bottom BS&W samples and API, PEMEX agreed BS&W, monthly reconciliation meetings (Tracking!TRUCKING columns 17–36; !Reconciliation). Nov 2022 CNH format: measurement point "CAB Poza Rica", fiscal turbine meter, delivery at Estación de Bombeo Ezequiel Ordóñez, La Guasima, Papantla; sale point CAB Poza Rica 100 % (`Tabla_Informe_Mensual_CNH_Nov2022.xlsx.txt`; `CNH_DGM_VHPM.xlsx!CNH_DGM_04_PIM`).

**3.1.4 SASISOPA inventory (Drive 1Kc7j1UecnAlj6lfjQotqkkwDiaqFUEGc, "Inventarios Tonalli Energía SASISOPA.xlsx", Apr 2020; 107 numbered lines, all Sistema "Pozo", Localización "Tecolutla"; the file does not name the well per line — dates separate TEC-10 (Mar–Jun 2018) from TEC-11 (Nov 2018–Aug 2019) and the surface line (Dec 2019)).**

| Group | Items (qty) | In-service date | Condition |
|---|---|---|---|
| Wellhead / trees | 7 1/16" × 2 1/16" and 2 9/16" 5,000 psi tree valves (master, wing), flow crosses 2 9/16" × 2 1/16" (rows 1–10); wellhead 9 5/8" × 7" × 2 7/8" 5M (row 48, 11 Apr 2018); wellhead SBU 9 5/8" × 7" × 4 1/2" × 2 7/8" 5K incl. tree (row 73, 25 Jan 2019); FIP hanger 7 1/16" × 2 7/8" 5K (row 86, Jul 2019); tapered hanger 2 7/8" × 7 1/16" (row 34) | Mar 2018–Jul 2019 | mostly "Operando"; several tree valves "F/O Temporal" |
| Casing (TEC-10) | 13 3/8" 41.21 m; 9 5/8" 656.05 m; 7" 2,412.87 m; 4 1/2" 286.82 m (rows 15–18) | 8–22 Apr, 2 May 2018 | Operando |
| Casing (TEC-11) | 13 3/8" 57.03 m; 9 5/8" 320.37 m; 7" 2,357.93 m; 4 1/2" 3,829.99 m; 4 1/2" N-80 56.39 m (rows 67–71; mis-labelled "tubería de producción") | 30 Nov, 18 Dec 2018 | Operando |
| Tubing (TEC-10) | 2 7/8" 2,319.95 m + 2,173.66 m; 2 3/8" 122.83 + 352.29 m; 4 1/2" 109.65 m; 6 5/8" mechanical packer; 2 7/8" × 2 3/8" crossover (rows 11–14, 19, 50–53) | Mar–Jun 2018 | Operando |
| Tubing (TEC-11) | 2 3/8" J-55 2,155.37 m; 2 3/8" L-80 151.93 + 2,156.72 m; 2 3/8" N-80 253.44 m; ASI-X HP packer for 4 1/2" 11.6# (rows 83–88) | Jun–Aug 2019 | Operando |
| Stimulation tools (TEC-11) | selective acid cup tool 114.3 × 60.3 mm, drag block, rotary diverter valve, L-80 pup joints, locator seal, swivel (rows 75–82); 3 3/4" PDC bit (row 74) | May 2019 | F/O Temporal |
| Surface | motor-pumps (rows 54, 72); 3" hose and quick connections (55–57); 2" flowline 514 m + valves/fittings (89–105); ecological burner and three-phase separator (106–107, 8 Mar 2020); SCBA sets (65–66); calibration rabbits 9 5/8", 7", 4 1/2" (20–22) | Oct 2018–Mar 2020 | Operando |

### 3.2 Delivery point, trucking and reconciliation (Tracking!TRUCKING, 885 rows, 23 Jul 2018–9 Dec 2022; !Acronyms; !Reconciliation)

- Destinations: EZOR = Ezequiel Ordóñez pump station (PEMEX, oil sales; 519 loads); MOZUTLA-1 (149) and MOZUTLA-7 (177) = water disposal 2018–19; ESA = Ecología y Servicios Ambientales (21 loads, Jul–Aug 2018 flowback water); Santa Agueda 49 (4 loads, oil, 2018–20); 12 cancelled.
- Trucking companies: Transportes Especializados PHC 258 loads, Transportes Nuevo Amanecer 197, TDH 175 (2021–22; TDH's rented 30 m³ pressure-vacuum unit and its two operators are named in the 1 Jul 2020 letter, DRN 1zM6upX2…), Carga Sedimentaria 153, CBG 61, XOXOCOTLA 21, ROMAGA 4, ASSA 2.
- Ticket volumes by year (Volume shipped bbl; PEMEX-agreed oil bbl):

| Year | EZOR loads | Shipped bbl | PEMEX oil bbl | Water-disposal loads (Mozutla/ESA) | Water bbl |
|---|---|---|---|---|---|
| 2018 (Jul–Dec) | 90 | 17,300 | 14,385 | 90 | 15,586 |
| 2019 | 202 | 35,422 | 33,795 | 257 | 43,998 |
| 2020 | 101 | 18,773 | 17,224 | 0 | 0 |
| 2021 | 98 | 18,075 | 17,971 | 0 | 0 |
| 2022 | 15 | 2,780 | 2,036 (Dec loads unsettled) | 0 | 0 |

- PEMEX statements (Reconciliation sheet, "final adjusted"): 2018 15,159 bbl (Tonalli 14,685); 2019 32,701 (33,975); 2020 Jan–Nov excl. Mar 15,286 (15,787); total Sep 2018–Nov 2020 63,146 vs 64,447 Tonalli, −2.0 % (rows 15, 42, 63, 66). Conciliation meetings monthly (e.g. 31 Oct 2018: 4,357 bbl October agreed; comments column). Gaps: no statements Apr–Jun 2020 (shut-in) and Mar 2020 unfilled.
- Realised price (docs/15_pemex_settlements.md, from PEMEX comprobantes 2020–22): 0.81 × WTI volume-weighted; 28–31 °API, 1.5–1.9 % S; delivery-programme penalties for loads outside ±10 % of 175–180 bbl/d.
- Sept 2019 directors' memo: PEMEX had not loaded the Jul 2019 invoice (USD 263,173 incl. VAT) into the NAFIN factoring portal; revenue assumed 60 days after COPADE (DRN 1DvcwTMU…). PEMEX early-production sales contract signed 21 Jul 2020 (DRN 1Z5EAMWG…).

### 3.3 Operating mode 2018–2023

| Period | Wells producing | Events | Source |
|---|---|---|---|
| Mar–May 2018 | — | TEC-2 static gradient 27 Mar; TEC-2 test and build-up 8–30 May (50 bbl/d oil, 453 bbl/d water) | WP table; IHS TEC-2 |
| Apr–May 2018 | — | TEC-10 drilled 11/16 Apr–1 May; logged; cased; liner 4 May | Masterlog; DRN |
| Jul–Aug 2018 | TEC-10 flowback | 23 Jul–6 Aug; 21 loads of flowback water to ESA; build-up to 31 Aug | welltest csv; Tracking |
| Sep–Dec 2018 | TEC-10 (+ TEC-2 Sep test month 411 bbl) | first EZOR sales 5 loads Sep 2018; Oct 2018 peak ~181 bbl/d TEC-10; TEC-11 drilled 11 Nov–18 Dec | Tracking; database; tracker |
| Jan–Aug 2019 | TEC-10, TEC-2 | TEC-2 tickets to Aug 2019; TEC-11 completion May–Sep 2019, water only, 26 water loads; TEC-7 19 water loads Jun–Jul; last Mozutla disposal Aug 2019; TEC-7 converted to injector 26 Aug 2019 | Tracking; DRN |
| Sep 2019 | TEC-10 (TEC-2 shut in) | TEC-2 uneconomic, shut in; forecast TEC-10 only at −1.2 %/month, uneconomic by Feb 2020 at USD 54/bbl; scenario 3 = shut in TEC-10 from Oct 2019 (not executed) | DRN 1DvcwTMU… |
| Oct 2019–Mar 2020 | TEC-10 (+ TEC-2 "commingled for testing" from 31 Jan 2020) | commingled "CAMPO TECO" tickets; separator and burner installed 8 Mar 2020; Mar 2020 last load 20 Mar | GLJ20 note; inventory; Reconciliation |
| Apr–Jun 2020 | none | shut in (price collapse); CNH 2020 filing zeros; no tickets | Anexo 2020; docs/13 |
| Jul 2020–Jan 2022 | TEC-10 (2021 filing: TEC-10 only every month) | sales 1,300–2,600 bbl/month 2020, 730–2,335 bbl/month 2021; Programa de Transición request dismissed 7 Aug 2020; Plan de Evaluación extended to 24 Nov 2021; TEC-10 choke opened Feb 2021 | Tracking; Anexo 2021; DRN |
| 4 Feb 2022–Nov 2022 | none | Informe de Evaluación resolved unfavourably 3 Feb 2022; production stopped 4 Feb 2022 (last EZOR loads Feb 2022); Programa de Transición approved 18 Jul 2022; Jul–Oct 2022 CNH monthly: 0/189/49/0 bbl; 25 Aug 2022 Jaguar buys 50 % | DRN; Tabla Informe Mensual; Tracking |
| 24 Nov–Dec 2022 | TEC-10 | restarted: 15 producing days in Nov, 678 bbl net, 916 bbl delivered on 24, 25, 29, 30 Nov; 4 loads Dec 2022 (740 bbl, unsettled) | CNH DGM Nov-22; Tracking |
| 2023 | not recorded in the files read | 2024 abandonment sheet lists all four Tonalli-era wells (TEC-2, 7, 10, 11) as shut-in | DRN 1XSHXSKe… |

Field sales by year (PEMEX-measured tickets / CNH filings): 2018 14.4 kbbl; 2019 33.8; 2020 17.2 (CNH: 18,973 gross monthly column, 16,132 "net" total line — G-53); 2021 18.0 (CNH 17,402); 2022 2.0 (CNH Jul–Oct 238 bbl + Nov 678). Field rate ~130 bbl/d Oct 2018 → ~70 (2019–20) → ~50 (2021) → ~30 (H1 2022) (`docs/04_production_database.md` §4).

### 3.4 Water handling

| Period | Water bbl | Route | Source |
|---|---|---|---|
| Jul–Aug 2018 | 3,654 (21 loads) | ESA disposal (flowback, assumed 100 % BS&W) | Tracking |
| Sep 2018–Dec 2018 | 11,932 + 182 | Mozutla-1 (69 loads), Santa Agueda | Tracking |
| 2019 | 13,569 (Mozutla-1) + 30,429 (Mozutla-7) | last loads Aug 2019; includes TEC-11 4,397 and TEC-7 3,252 | Tracking |
| Sep 2019 → | — | TEC-7 injection string + packer (Aug 2019); no water hauls after Aug 2019 in the tickets; water carried in the sales stream 0–0.4 % BS&W | DRN; Tracking |
| 2020 | 47,732 (CNH filing, Jan–Mar, Jul–Dec) | field-produced water; WC 72–75 % | Anexo 2020 |
| 2021 | 73,827 (CNH filing), 81 % WC | TEC-10 only | Anexo 2021 |
| Jul–Oct 2022 | 0 / 2,218 / 511 / 0 | | Informe mensual |
| Nov 2022 | 1,582 (15 days) | TEC-10 | CNH DGM VHP |
| TEC-10 well tests | 2018 daily: water 337→124 bbl/d; Jul 2019 WC 67 % | | welltest csv; docs/04 |

Ticket comments record produced water being sucked from the TEC-2/TEC-11 cellars and the TEC-11 work pit and "filled at TEC-10 with congenital water" (Tracking!TRUCKING Comment1, 2019). Water disposal well: none in the block other than the TEC-7 injector conversion; TEC-11 reclassified as a possible injector (Oct 2019).

### 3.5 Staffing (as far as stated)

- Field: crew contracted through "Servicio de Ingeniería, Instrumentación y Conexos" at MXN 280,000/month (Sept 2020 op-cost sheet, DRN 1K3fXnOe…). Ticket signatories for Tonalli at site: Bernardo Leandro López (462 tickets, 2020–22), José G. Briviesca Ramos (~380, 2019–22), Francisco Ramírez and Roberto Maldonado (2018), Iván Torres Frías, Marco A. Cortés (Tracking!TRUCKING col K); data entered by Eduardo Navarrete (2018), José Briviesca, Bernardo Leandro. SISOPA coordinator José Mario Guillermo Berman (TDH letter, DRN 1zM6upX2…). Vacuum-truck operators: two TDH operators (same letter).
- Corporate: 2022 monthly CNH report budget lines "Personal de administración del proyecto" USD 11,000 + 7,870/month, information administration 6,101, office rent 6,101, contract administration fee 8,104; total actual USD 39,177/month against USD 190,595 approved (`Tabla_Informe_Mensual_CNH_Nov2022.xlsx.txt`). Sept 2019 G&A + regulatory USD 820 k for 2019 (DRN 1DvcwTMU…).
- No headcount table exists in any file read.

### 3.6 Regulatory filings and cadence

| Filing | Cadence | Content | Source |
|---|---|---|---|
| CNH_DGM_01_PM "Reporte de producción de petróleo, gas natural y condensados" | monthly, per well | days on, gross/net oil, API, S, salt, water, gas, composition | `CNH_DGM_VHP.xlsx` |
| CNH_DGM_02_AF "Reporte mensual de aforos" | monthly, per well test | WHP, choke, line P, T, rates, GOR | same (Nov 2022 row blank) |
| CNH_DGM_03_PID "Reporte diario de producción por instalación" | daily rows, monthly file | net oil per day at the measurement point, API 30.9, S 1.6, salt 48.8 | `CNH_DGM_VHPM.xlsx` (Nov 2022: production on 24, 25, 29, 30 Nov: 179, 183, 369, 184 bbl) |
| CNH_DGM_04_PIM "Reporte mensual de producción por instalación" | monthly | 915.8 bbl at CAB Poza Rica, turbine, fiscal, "se entrega producción a venta con PEMEX" | same |
| CNH_DGM_05_BP / 06_BC / 07_BG oil / condensate / gas balances | monthly | Nov 2022: opening inventory 238 bbl, extracted 678, delivered 915.8, impurity shrink factor 0.19; gas 0.9 MMcf flared under approved evaluation-programme burn | `CNH_DGM_BALANCES.xlsx` |
| Informe mensual de actividades e inversiones (contract obligation 4.1) | monthly | LISH budget vs actual, production vs approved, measurement point | `Tabla_Informe_Mensual_CNH_Nov2022.xlsx.txt` (Jul–Oct 2022) |
| Anexo III.8.III Consolidado anual de producción | annual | monthly oil/water/API/gas, origin wells, destination BSB Ezequiel Ordóñez, transport "terrestre UPV" | 2020, 2021 renderings |
| Tabla Producción (Plan de Desarrollo forecast) | annual | per-well base/incremental profiles; TEC-12DES from month 3 of 2021 / month 5 of 2022, TEC-13DES month 8 of 2022 | `Tabla_Produccion_2021_and_2022_CNH_forecast.xlsx.txt` |
| CRE-17-054-C semi-annual sales report | semi-annual | acknowledgements only on the Drive | docs/15 |
| Plan de Evaluación (May 2017), Informe de Evaluación (2 Jul 2020, 19 Nov 2021), Programa de Transición (approved 18 Jul 2022), aviso de abandono temporal art. 54 (TEC-11, Apr 2022), reclassification TEC-11 to injector (18 Oct 2019), TEC-9 returned to CNH/SENER, Fideicomiso de abandono (USD 411,032; MXN 6,943,765 balance; contract term 25 years) | event | | DRN |
| PEMEX conciliation | monthly meeting + monthly statement | | Tracking!Reconciliation |
| Fees (LISH art. 45/55, from 1 Feb 2020): exploration fee 1,396.09 MXN/km²/month (first 60 months) then 3,348.47; activity tax 1,820.44 (exploration) / 7,281.76 (extraction) MXN/km²/month on 7.162 km² → USD 1,128/month now, 3,561 in extraction phase (FX 21) | monthly | | `Tonalli Contractual Fee and Exploration Tax.xlsx!D13:J29` |

### 3.7 HSE and regulatory framework (as stated)

- PEMEX era: MIA-R Proyecto Integral Poza Rica 2001–2016, SEMARNAT resolution SGPA-DGIRA-DIA-0659/02 of 7 Aug 2002; installations "intrínsecamente seguras" per NOM, ASME, API, NFPA, ASTM, ANSI, NACE; municipality of Tecolutla classified "mediana intensidad" for insecurity (CISEN) (Resumen §viii, §x).
- Tonalli: SASISOPA in place (inventory Apr 2020; element 13 procedures PRO-HSE-019, FOR-HSE-004/005 for emergency drills; drills for well control, fire, evacuation, first aid, heat stroke; PPE list; DCS extinguishers 30 lb, 150 lb wheeled, CO₂, SCBA, fixed/portable gas detection, fire pump; H₂S training; API-RP2D cranes; weekly kick drills) (Prog12 p.70–72; Term12 p.21–22). Flowline to NOM-009-ASEA-2017, NOM-006-ASEA-2017, NACE MR0175 (DRN 1LawOYRR…). H₂S 1.75 % mol basis for wellhead spec (Prog12 p.64). Gas flaring approved under the evaluation programme (CNH gas balance). TEC-9 wellhead flagged as "Safety & Environmental Hazard" (WP). Abandonment per NMX-L-169-SCFI-2004 (Prog12 p.70). No incident statistics in any file read.

### 3.8 Operating cost snapshot

- Sept 2020 monthly payments ≈ USD 28,155: crew MXN 280,000; TDH vacuum truck MXN 108,000; diesel 60,000; consumables 40,000; frac-tank rental 32,000; Mensuranda water analysis 21,000; Intertek crude analysis USD 1,468; Apollo demulsifier USD 925 (DRN 1K3fXnOe…). GLJ opex assumptions: fixed 1,400 $/well/month + 276 M$/yr field (YE2020); 1,670 $/well/month + 227 M$/yr (YE2021); variable 3.75 → 5.85 $/bbl; transport 2.79 → 2.73 $/bbl (GLJ20/21 Table 4).
- Sept 2019 memo: break-even 60 bbl/d at USD 54/bbl; shared costs ≈ USD 14 k/month; capital payables USD 2.3 MM (30 Jun 2019); VAT recoverable ≈ USD 1.2 MM (DRN 1DvcwTMU…).

---

## 4. Reserves

### 4.1 Reserves by evaluator and category (gross lease, Mbbl oil unless stated)

| Evaluator / date | Basis | 1P (PDP / total) | 2P (PDP / total) | 3P (PDP / total) | Notes | Source |
|---|---|---|---|---|---|---|
| PEMEX (CNH data room), 1 Jan 2014 | remaining reserves | 6 (0.006 MMbbl) oil, 0.012 Bcf gas, 9 PCE | 6 / 0.012 / 9 | 156 / 0.185 / 196 | OOIP 7.8 MMbbl all categories | Resumen Tabla ii.1–ii.2 |
| PEMEX/CNH El Abra table (to Apr 2015) | | | | 3P EUR 2,129 (2.13 MMbbl) | produced 1,913; RF 24.5 %; 3.1 km² | `docs/07_volumetrics.md` §1 |
| GLJ, effective 31 Dec 2019 | map only on Drive (project s1202432) | — | — | — | top-structure map read; report not in repo | DRN 1xGo-WvPj… |
| GLJ draft, 19 Feb 2021 (IFR 100 % WI sensitivity, project 1212824) | YE2020, GLJ (2021-01) | 99 / 326 | 125 / 862 | 164 / 1,238 | TEC-12 labelled "HZ location" (renamed DIR in the final); same volumes and PV10 as final | draft xlsx `Table 1` rows 71–79, 133–227 |
| **GLJ final, effective 31 Dec 2020** (Tonalli, project 1212851, run 26 Feb 2021) | GLJ (2021-01), USD | **99 / 326** (NAR 60 / 198) | **125 / 862** (NAR 76 / 522) | **164 / 1,238** (NAR 100 / 745) | by entity: TEC-10 99 / 130 / 125 / 205 / 164 / 284; TEC-12 DIR 197 (1P) / 335 (2P) / 493 (3P); TEC-13 HZ 322 (2P) / 460 (3P) | GLJ20 p.3, p.5 |
| **GLJ Draft 1, effective 31 Dec 2021** (project 1223410, run 1 Apr 2022) | GLJ (2022-01), USD | **92 / 329** (NAR 55 / 198) | **125 / 885** (NAR 75 / 534) | **170 / 1,279** (NAR 103 / 773) | TEC-10 92 / 121 / 125 / 196 / 170 / 277; TEC-12 DIR 209 / 350 / 516; TEC-13 HZ 339 / 486 | GLJ21 "Daily Production, Reserves and PV summary" |
| Tonalli to CNH, Tabla Producción 2021/2022 | forecast, must be consistent with 2P/3P | TEC-2 + TEC-10 base ~71 bbl/d start 2021; TEC-12DES 300.2 bbl/d incremental | | | IFR type curve month averages (345/400 kbbl) | `Tabla_Produccion…txt`; docs/13 §1 |
| Jaguar transaction valuation, 25 Aug 2022 | GLJ 31 Dec 2021, April price sensitivity | | 2P PV15 USD 9.134 MM less development 3.972 MM, abandonment 0.388 MM, payables 2.141 MM = 2.633 MM | | | DRN 1ffaRgaw… |

GLJ YE2020 → YE2021 reconciliation (GLJ21 REC-1/REC-2, company interest, Mbbl): PDP 99.2 + 10.1 technical − 17.4 production = 91.8; Total proved 326.1 + 20.8 − 17.4 = 329.4 (TEC-10 129.6→120.8, TEC-12 196.5→208.6); P+P producing 124.8 + 18.0 − 17.4 = 125.4; Total P+P 862.2 + 40.2 − 17.4 = 885.0 (TEC-10 205.5→196.2, TEC-12 334.6→350.2, TEC-13 322.1→338.6); PPP producing 164.1 + 23.7 − 17.4 = 170.3; Total PPP 1,237.6 + 59.0 − 17.4 = 1,279.2. 2021 production 17.4 Mbbl (vs 17,402 bbl in the CNH filing).

### 4.2 Before-tax present values (M$ USD)

| Category | YE2020 0 % | 5 % | 8 % | 10 % | 12 % | 15 % | 20 % | YE2021 0 % | 5 % | 8 % | 10 % | 12 % | 15 % | 20 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Proved producing | 839 | 806 | 784 | 770 | 755 | 733 | 698 | 1,175 | 1,108 | 1,068 | 1,042 | 1,017 | 981 | 924 |
| Total proved | 3,673 | 3,187 | 2,933 | 2,778 | 2,634 | 2,437 | 2,153 | 5,392 | 4,676 | 4,311 | 4,091 | 3,888 | 3,613 | 3,222 |
| P+P producing | 1,216 | 1,131 | 1,082 | 1,051 | 1,021 | 979 | 914 | 1,683 | 1,531 | 1,448 | 1,397 | 1,348 | 1,281 | 1,182 |
| Total P+P | 12,381 | 9,486 | 8,187 | 7,460 | 6,824 | 6,011 | 4,945 | 16,840 | 12,653 | 10,859 | 9,875 | 9,027 | 7,959 | 6,581 |
| PPP producing | 1,668 | 1,502 | 1,414 | 1,359 | 1,308 | 1,237 | 1,134 | 2,294 | 2,005 | 1,858 | 1,771 | 1,690 | 1,581 | 1,427 |
| Total PPP | 20,049 | 14,404 | 12,116 | 10,896 | 9,863 | 8,587 | 6,984 | 27,149 | 18,703 | 15,546 | 13,921 | 12,573 | 10,939 | 8,929 |

YE2020 from GLJ20 p.3; YE2021 from GLJ21 p.5–6 (the rendering of the summary page is column-scrambled; the YE2021 Total-proved row is reconstructed as PDP + PUD (PUD 4,216 / 3,568 / 3,242 / 3,048 / 2,871 / 2,633 / 2,297) and agrees with the clean PV10 4,091 and the visible 5,392 / 4,676 / 4,311 / 3,888 / 3,613 / 3,222 fragments). YE2020 entity PV10 (M$): TEC-10 PDP 1,899, TP 2,334, P+P 2,359/3,208, PPP 2,986/3,903; TEC-12 DIR 2,213 (1P), 4,057 (2P), 5,953 (3P); TEC-13 HZ 2,927 (2P), 4,193 (3P); field expenses −1,129 to −3,153 (GLJ20 p.5). YE2021 entity PV10: TEC-10 2,133 / 2,540 / 2,754 / 3,417 / 3,460 / 4,127; TEC-12 3,241 / 5,327 / 7,569; TEC-13 3,599 / 4,991; field expenses −1,090 to −2,766 (GLJ21). First-six-year BTAX cash flow YE2020 (PDP / TP / P+P prod / TP+P / PPP prod / TPPP): 2021 371 / −231 / 392 / −67 / 407 / 186; 2022 276 / 1,305 / 331 / 212 / 373 / 589; 2023 173 / 937 / 249 / 2,523 / 308 / 2,957 (GLJ20 p.3).

### 4.3 OOIP by source and recovery factors

| Source | Area | Gross m | N/G | φ | Sw | Bo | OOIP MMbbl | RF / EUR | Source file |
|---|---|---|---|---|---|---|---|---|---|
| PEMEX 2014 (CNH data room) | 2.5 km² | — | — | 5–12 % | 24–38 % | 1.1923 | 7.8 (1P=2P=3P) | actual 24.35 % oil / 19.31 % gas; final 24.43 / 19.45 (1P–2P), 26.35 / 21.54 (3P) | Resumen Tablas ii.1, ii.3, v.2 |
| CNH El Abra trend table (Apr 2015) | 3.1 km² | | | | | | 7.82 | 24.5 % to date; 3P EUR 2.13 (27.2 %) | `El Abra Trend Field Analogies.xlsx` via docs/07; WP table "Tecolutla 3.1 7.8 2.0 25 %" |
| IFR "Summary (GLJ)" sheet / WP volumetrics | 2.5 km² (630 ac) | 42.3 | 0.40 | 7.0 % | 30 % | 1.19 | 11.2 (1.8 e6 m³; GRV 107.8, NRV 43.1, PV 3.0, HCPV 2.1 e6 m³) | cum 2 MMbbl = 18 %; 1.2 MMbbl remaining at "conservative 29 %"; up to 45 % in other El Abra pools | WP; docs/07 |
| GLJ YE2020/YE2021 1P (A/C) | 401 ac | 59,610 ac·ft GRV | 0.40 | 5.0 % | 30 % | 1.19 | 5.441 | EUR 1,680 (30.9 %) PDP / 1,930 (35.5 %) TP | GLJ20 Table 2.1; GLJ21 Table 2.1 identical |
| GLJ 2P (G / G+E1) | 515 ac | 74,071 | 0.40 | 6.0 % | 30 % | 1.19 | 8.302 | 1,755 (21.1 %) / 2,555 (30.8 %) | same |
| GLJ 3P (P / P+E1N1) | 630 ac | 87,368 | 0.40 | 7.0 % | 30 % | 1.19 | 11.164 | 1,855 (16.6 %) / 3,055 (27.4 %) | same |
| Petrel Robertson geomodel, deep OWC −2,374, all wells | 2.546 km² | 46.8 | 0.427 | 5.56 % | 20 % | 1.19 | 11.96 | | `Petrel Robertson Volumetrics.xlsx!B` |
| PR, TEC-10 new logs only | 2.546 | 46.8 | 0.418 | 6.16 % | 18.9 % | 1.299 | 12.04 (Rsi 552 scf/bbl; OGIP 6.65 Bcf) | | col D |
| PR, TEC-2/9/10 vintage logs | 2.546 | 46.8 | 0.352 | 4.74 % | 21.0 % | 1.299 | 7.59 | | col F |
| Repo Monte Carlo (task 7) | | | | | | | P90 8.1 / P50 10.0 / P10 12.2 | remaining at trend 29 %: 0.3–1.6, ~0.9 MMbbl | `data/processed/volumetrics/summary.json` |

GLJ method (GLJ20 p.8): Petrel model from Tonalli; porosity from TEC-9 and TEC-10 only (low 5 %, high 7 %, best = average); Sw 30 % from TEC-9 by Simandoux (a 1, m 2, n 2, Rw 0.135 at 25 °C); N/G 40 % from petrophysics plus microlog/neutron counts in old wells; OWC −2,374.2 mSS = LKO in TEC-3; high case whole property; low case only south of TEC-11 "due to the poor results from the Tecolutla-11 well and the uncertainty to the source of the water"; best = average of the two gross volumes. PEMEX petrophysics: Archie, Rw 0.075 at 65 °C, 45,000 ppm, m 1.8–2, n 2, a 1 (Resumen Tabla v.1). PEMEX PVT (Ezequiel Ordóñez-41 sample used as representative): 20 °API [sic, text says 28], Bo 1.1923, RGA 59.9 m³/m³, 0.8415 g/cm³, 11.2 cP, Pb 132 kg/cm² (Resumen Tabla v.2) — incompatible with produced GOR 565–860 scf/bbl and measured 30–31 °API (docs/04 §5, docs/gaps G-31).

### 4.4 GLJ decline parameters (Table 2.2)

| Entity / class | Analysis date | Di %/yr | qi bbl/d | qf | b | Life yr | EUR Mbbl | Cum | Remaining | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| TEC-10 1P (A) YE2020 | 2021-01-01 | 26.04 | 100 | 3 | 0.40 | 23.9 | 225 | 58.4 | 166.6 | GLJ20 |
| TEC-10 2P (G) | | 20.98 | 100 | 3 | 0.50 | 38.2 | 300 | 58.4 | 241.6 | |
| TEC-10 3P (P) | | 17.32 | 100 | 3 | 0.60 | 59.5 | 400 | 58.4 | 341.6 | |
| TEC-12 DIR 1P (B2) | | 36.63 | 200 | 3 | 0.50 | 27.9 | 250 | 0 | 250 | |
| TEC-12 DIR 2P (H2) | | 31.35 | 225 | 3 | 0.60 | 48.7 | 400 | 0 | 400 | |
| TEC-12 DIR 3P (Q2) | | 30.47 | 275 | 3 | 0.70 | 78.1 | 600 | 0 | 600 | |
| TEC-13 HZ 2P (E2) | | 28.48 | 200 | 3 | 0.60 | 51.3 | 400 | 0 | 400 | |
| TEC-13 HZ 3P (E2N2) | | 23.24 | 200 | 3 | 0.70 | 88.0 | 600 | 0 | 600 | |
| TEC-10 1P / 2P / 3P YE2021 | 2022-01-01 | 23.36 / 18.11 / 14.53 | 80 | 3 | 0.40 / 0.50 / 0.60 | 24.2 / 39.6 / 62.4 | 225 / 300 / 400 | 75.8 | 149.2 / 224.2 / 324.2 | GLJ21 |
| TEC-12, TEC-13 YE2021 | | unchanged from YE2020 | | | | | | | | GLJ21 |
| TEC-2, 6, 7, 9 | | no forecast; cum 328.5 / 507.2 / 267.0 / 352.6 | | | | | | | | both |

Economic-limit volumes (GLJ20 Table 2, "remaining reserves are less than the estimate due to economic limit"): TEC-10 99 / 130 / 125 / 205 / 164 / 284; TEC-12 197 / 335 / 493; TEC-13 322 / 460. Kevin's export workbook (26 Feb run) sums 1P 108.9 (TEC-10) + 203.0 (TEC-12); 2P 211.5 + 342.9 + 331.7; 3P 289.8 + 501.8 + 470.0 Mbbl (`Gross Oil Monthly Forecast by Well (Kevin).xlsx!monthly B3:I3`); TEC-12 1P starts May 2021 at 6.07 Mbbl/month (~196 bbl/d) (!original row 25). Daily production forecast, total P+P (GLJ20 Table 3): 219 (2021, 2 wells), 338 (2022, 3 wells), 304, 238, 191, 158, 133, 115, 99, 87, 77, 69 bbl/d … to 36 bbl/d in 2039; 862 Mbbl total. YE2021 total P+P: 193 (2022), 272, 313, 242, 194, 160, 135 … (GLJ21 p.27).

### 4.5 Economic parameters and price decks

| Item | GLJ YE2020 (GLJ 2021-01) | GLJ YE2021 (GLJ 2022-01) | Source |
|---|---|---|---|
| Oil reference | 88.4 % of Brent (US$) | 87.9 % of Brent; GOR 900 scf/bbl, gas reference Henry Hub, surface loss 100 % | Table 4 A |
| Transport | 2.79 $/bbl | 2.73 $/bbl | |
| Realised price by year ($/bbl, 2P total) | 2021 42.05; 2022 45.78; 2023 48.82; 2024 51.67; 2025 52.63; 2026 53.62; 2027 54.61; 2028 55.64; 2029 56.68; 2030 57.81; 2031 58.97; 2032 60.15 … 2039 69.09 | 2022 64.10; 2023 60.95; 2024 59.78; 2025 60.97; 2026 62.20; 2027 63.43; 2028 64.71; 2029 66.00; 2030 67.32; 2031 68.67; 2032 70.04 … 2044 88.83 | GLJ20 p.30; GLJ21 p.27 |
| GLJ Jan-2022 Brent deck ($/bbl) | | 2022 76.00; 2023 72.51; 2024 71.24; 2025 72.66; 2026 74.12; 2027 75.59; 2028 77.11; 2029 78.66; 2030 80.22; 2031 81.83; +2 %/yr after (WTI 73.00, 69.01, 67.24 …; Maya 68.4 …) | `GLJ jan22.xlsx!International Oil` rows 17–27 |
| Royalty | fixed + sliding scale on reference price; "Crown" 7.5 %, "non-crown" 31.8 % of revenue on the P+P producing case; ~39.3 % total burden in the P+P total case | same structure | GLJ20 p.29; draft xlsx Sheet2 col Q |
| Opex | fixed 1,400 $/well/month; variable 3.75 $/bbl; field 276 M$/yr | 1,670 $/well/month; 5.85 $/bbl; 227 M$/yr | Table 4 B |
| Abandonment | 75 M$/well | 75 M$/well | Table 4 C |
| Capital | TEC-12 DIR 1,500 M$ (1,125 + 375) May 2021; TEC-13 HZ 2,400 M$ (1,800 + 600) May 2022 | TEC-12 May 2022; TEC-13 Sep 2023; same amounts | Table 4 D |
| Measured realised price | | 0.81 × WTI (2020–22 comprobantes) | docs/15 |

### 4.6 Forecast assumptions in circulation (for the "which forecast" slide)

| Case | First month bbl/d | EUR kbbl | Basis | Source |
|---|---|---|---|---|
| IFR vertical type curve (Aug/Sep 2020) | 300 (qi 342, b 1.7, Di 29 %/yr) | 345 quoted; 401 over 417 months; 380 to 10 bbl/d | average of TEC-2/6/7/9 by month on production, "data since 1960"; 12/64" choke, 2 7/8" tubing to surface | WP; Transition plan docx; `docs/06_forecast.md` |
| Tonalli Programa de Transición 2022 | TEC-12 300.2 bbl/d Dec 2022, 0 % water first month; TEC-13 May 2023; TEC-10 47.9→41.7 bbl/d, 147→153 bbl/d water | 2–3 %/month field decline | new wells 2 7/8" tubing to surface, expected interval 2,296–2,303 mSS | Transition plan docx Tabla 1, Tabla 23 |
| GLJ YE2020/21 TEC-12 | 196 / 221 / 270 (1P/2P/3P) | 203 / 343 / 502 (250 / 400 / 600 technical) | offset production + pad synergy; TEC-13 400/600 | GLJ20 p.9, Table 2.2 |
| Petrel Robertson | 100 base, up to 200 | >100 base, ~200 upside | TEC-10 as downside; ~15 m net pay vs 3 m at TEC-10 | PR assessment p.2–3 |
| TEC-10 actual fit | 152 (181 first full month) | ~104 | b 0.49, Di 0.79/yr | docs/06 |
| Repo recommendation | 100 / 180 / 300 | 65 / 218 / 366 | P90 / P50 / P10 | docs/06 §4 |
| Prog12 / Term12 expected initial | 250 oil + 50 water, 0.51 MMcfd | | | Prog12 p.9; Term12 p.6 |

---

## 5. Reader's notes (interpretation, not source)

1. The only Tonalli-era water disposal well is TEC-7 (converted Aug 2019); the ticket record shows disposal hauling stopping in Aug 2019, which is consistent, but no injected volumes or injection pressures are in any file read. The 2024 abandonment sheet does not mention the injection string, so its current state is unknown.
2. The TEC-11 tie-back pptx is Halliburton job-monitoring output only; it confirms the date (18 Dec 2018), slurry density (1.24 g/cc TunedLight), spacer (1.45) and a ~130-bbl job, nothing about depths. Depth of the liner top and tie-back should be taken from the Halliburton/Weatherford post-job reports on the Drive (DRN lists TR 7 @ 2,396/2,425 m proposals) — not confirmed here.
3. TEC-10 7" shoe: 2,282.72 (masterlog), 2,285 (Halliburton post-op), 2,288 (QMAX and Prog12 hole depth). For a schematic, 2,285 m (cementer's report) is the most direct measurement; the 2024 abandonment sheet's "2,262 mTVD / 2,288 mMD" refers to this shoe, not the well TD (2,490 mMD).
4. The Prog12 casing-design pages carry two mutually inconsistent trajectories (14–15° build-and-hold vs 45–75° in the time analysis); the S-shape plan (Term12 p.10) is the version filed with the completion programme. The deck should show the S-shape and the 13 3/8" / 9 5/8" 500 m / 7" 2,360 m strings.
5. GLJ's volumetric parameters are identical at YE2020 and YE2021; only TEC-10's initial rate (100→80 bbl/d) and cumulative changed. GLJ's TEC-10 2P profile was overtaken by actual performance within a year (docs/gaps G-39).
6. PEMEX's 2014 reserves (6 Mbbl 2P remaining, 156 Mbbl 3P) reflect the field at 9 bpd in 2014 and are the baseline the CNH "Volumen Original 7.8 MMbbl" belongs to; GLJ's 1P OOIP (5.4 MMbbl) is below it because of the 401-acre low-case area.
7. The SASISOPA inventory is a materials list, not a facilities register: no tank, pit or pump-station capacity is in it beyond the separator and two pumps, which supports the picture of a rented, minimal battery (rented separator until Mar 2020, rented frac tanks throughout).

## 6. Files not read or not readable in this pass

- `data/raw/ye2020_reserves/Tonalli - Management Reservoir Engineer Questions 2020.pdf` — not opened.
- `data/raw/ye2020_reserves/YE 2020 Reserves (Tecolutla) - Corporate Summary.pdf` — not opened (the text rendering of the "Detail (Final)" version was used).
- `data/raw/tec11/Tecolutla 11_Tieback 4 12_Graficas_181218.pptx` — images only; two of six read.
- `data/raw/petrophysics/TEC-9 SS Logs.pptx`, `Tantoyuca TEC-2,6,9.pptx` — mostly images; slide text used.
- `data/raw/tec12_regulatory/PROGRAMA DE TERMINACIαN TECOLUTLA-12DES VER1.0.pdf` — duplicate filename with an encoding artefact; not opened separately (assumed identical to the ÓN copy).
- `data/processed/drive_text/201807_Tecolutla-10_Welltest_Data.xlsx.txt` and `REPORT_TECOLUTLA_2.xlsx.txt` — empty files (0 lines).
- `data/raw/appraisal_plan/HWrates (TEC-11).xls` — read; it is a Babu–Odeh model, not test data.
- Drive files listed in DRN as "not yet read" or "too large": PEMEX survey scans 1957/1972/1991, TEC-11 casing proposals, `CONTRATO_CNH-R01-L03-A24.2016 TECOLUTLA.pdf`, `Tonalli G&A Expenses- December 31, 2021.xlsx`.
- The GLJ YE2021 "Summary of Reserves and Values" page rendered column-scrambled; PV table above reconstructed as described in 4.2. The GLJ YE2020/YE2021 plot pages are garbled (axis text only).
- IHS PTA reports: only the summary pages (1–7) read; the discussion, plots and gauge data were not.
