# Tecolutla (CA-24, El Abra) — fluid, rock and core notes for the handover deck

Compiled 17 Sep 2026 from the files listed in §0. Every number carries its source (file, page/sheet/cell). Values read by OCR from scanned forms are marked *(OCR)*; where the two OCR engines disagree or a field is illegible this is said. Nothing in §1–§7 is interpreted; my own reading is confined to the final "Reader's notes".

Abbreviations: SG = specific gravity; BS&W = basic sediment and water; SSU = Saybolt Universal seconds; PV = pore volume; NCS = net confining stress; mKB = metres below rotary table.

## 0. Sources and what could be read

| Source | Readable? | How read |
|---|---|---|
| `fluid_analyses/20180606 Tecolutla-2 Oil Analysis1.pdf` (SGS Deer Park) | text | pdfplumber |
| `fluid_analyses/201808 Tecolutla-10 Oil Analysis Report - SGS.pdf` | text | pdfplumber |
| `fluid_analyses/201808 Tecolutla-10 Oil Analysis (Distillation) - Corelab.pdf` (Saybolt) | scan, 6 pp | OCR (`data/processed/fluids/ocr/*Corelab.p1–6.*`), both engines agree on all numbers |
| `fluid_analyses/20181126 / 20181214 / 20190118 Tecolutla-10 Oil Analysis Report - Intertek.pdf` | scans, 1 / 7 / 7 pp | OCR; the results page is p.1 (Nov) and p.7 (Dec, Jan); pp.1–6 of Dec/Jan are cover letter and terms |
| `fluid_analyses/20190824 Tecolutla-11 Oil Analysis Tantoyuca.pdf` (Química Apollo) | text | pdfplumber |
| `fluid_analyses/Tecolutla-10DES Zona AB / Zona B / Zona C AnalisisCrudo V603-18.pdf` (SGS Coatzacoalcos) | text | pdfplumber |
| `fluid_analyses/Tecolutla-10 Gas Comps V603-18.pdf`, `Tecolutla-2 Gas Comps V613-18.pdf` (Stratascan/SGS) | text | pdfplumber |
| `fluid_analyses/Tecolutla-2 Gas Comps V613-18 (JT Liquids Recovery).xlsx` | xlsx | openpyxl |
| `fluid_analyses/Tecolutla10 Water Analisis Stiff V603-18.pdf`, `Tecolutla-2 Water Analisis Stiff V613-18.pdf` | text | pdfplumber |
| `fluid_analyses/Tecolutla-2 Muestreo V613-18.pdf` (SGS field sampling report) | text | pdfplumber |
| `fluid_analyses/Tecolutla-6 Gas Analysis Aug28, 1970.pdf` (PEMEX) | scan | OCR, both engines |
| `fluid_analyses/Tecolutla-{2,6,7} Oil Distillation *.pdf` (9 PEMEX Engler forms 1956–75) | scans, handwritten fields | OCR; RapidOCR recovered most numeric fields, Tesseract few; transcribed in §1.3 with flags |
| `fluid_analyses/Historical_Oil_Analysis_Tecolutla_Field.pdf` (9 pp) | scan | OCR; pp.1–9 are the same nine PEMEX forms in the order TEC-2 Jul-74, TEC-2 May-74, TEC-6 Jan-59, TEC-6 Jun-74, TEC-6 May-75, TEC-6 Oct-56, TEC-7 Jan-57, TEC-7 Jul-71, TEC-7 May-75 (checked page by page against the single-form OCR). No additional analyses. |
| `appraisal_plan/PVT Calculator (Tecolutla).xlsx` | xlsx | openpyxl, formulas and cached values |
| `development_plan/pvtdoc.pdf` (manual of the PVTProps.XLA add-in the calculator calls) | text | pdfplumber |
| `development_plan/Tecolutla 10 / Tecolutla 2 Final Report (IHS PTA) Spanish.pdf` | text (154 / 151 pp) | pdfplumber |
| `appraisal_plan/6 -Resumen Campo Tecolutla.docx` (PEMEX Ronda-1 field summary) | docx | python-docx |
| `data/processed/drive_text/Tecolutla10_ReporteFinal_V603-18.pdf.txt` (Stratascan core report, text rendering) | text | read in full |
| `geology/…/Core/Tecolutla10N1(3)PetrofBasicaV603-18 (1).xlsx` (plug workbook, 27 sheets) | xlsx | openpyxl |
| `geology/…/Core/Tecolutla1N1Petrog1(6LD)2352.15-2352.83 V603-18 EngVr.pdf` (petrography, English) | text, 22 pp | pdfplumber |
| `geology/…/Sample Descriptions/REPORTE FINAL TECOLUTLA-10_020518.pdf` | text, 79 pp | pdfplumber. **What it is:** the Weatherford mud-logging (Registro de Hidrocarburos, Unidad Móvil 20) final report for TEC-10, 17 Apr–1 May 2018, 470–2,490 m: operations summary, BHA and bit records, surveys, cuttings lithology every 2–5 m, mud data, gas shows, well sketch and recommendations. Not a core report. |
| `petrophysics/LAS/TECOLUTLA 10_CXD PROPIEDADES MECANICAS_2487.00m-2280.5m_02MAY2018.las` | LAS | lasio; data actually 2,301.7–2,491.7 mMD |
| `docs/04 §5, 09, 12 §5, 14`, `data/processed/petrophysics/summary.json`, `data/processed/welltest/*.csv` | text/csv | read |

Nothing in the list was unreadable. Two files carry no usable numbers beyond what is tabulated: the Historical compilation (duplicates) and the TEC-2 Jul-1974 form (mostly illegible, see §1.3).

## 1. Oil properties

### 1.1 Tonalli-era laboratory analyses (2018–2019), stock-tank / separator oil

| Well, sample | Date sampled | Lab, report | °API | SG / density | S % m/m | Viscosity | Pour point | BS&W / water | Salt | Other | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TEC-2, whole crude, well sample, test separator | 17 May 2018 | SGS Deer Park DP18-06236.001 | **28.4** (D5002) | SG 60/60 0.8847; 884.2 kg/m³ at 15 °C | 1.66 | 13.67 cSt at 40 °C; 3.911 cSt at 98.9 °C | −18 °C | 38.0 % v/v by distillation (D4006); 36.0 % by centrifuge (D4007), on the original sample | 95 lb/1000 bbl | RVP (VPCR4, 100 °F) 2.10 psi; acid no. 0.33 mg KOH/g; organic Cl 2 mg/kg; Si 460 ppb; colour D8.0; sample treated with demulsifier before all tests except water | `20180606 Tecolutla-2 Oil Analysis1.pdf` pp.1–2 |
| TEC-10, Zone C, well sample | 27 Jul 2018 | SGS Deer Park DP18-09329.001 | **26.5** | SG 0.8956; 895.1 kg/m³ | 1.67 | 18.73 cSt at 40 °C; 9.369 cSt at 60 °C | −24 °C | 44.5 % by distillation; 40.0 % by centrifuge (as received) | 138 lb/1000 bbl | RVP 1.24 psi; acid no. 0.11; org. Cl <1; Si 4,040 ppb; H2S in liquid 38 ppm, mercaptan S 218 ppm (UOP 163); H2S in vapour 1,000 ppm v/v (D5705); colour D8.0 | `201808 … SGS.pdf` pp.1–2 |
| TEC-10, Zone C | rec'd 10 Aug 2018 | Saybolt/Corelab 13071-14273, sample 6994578 | — | density 0.8863 and 0.8916 (two lines, basis not stated) *(OCR)* | — | — | — | — | — | Mol wt 136.54, C6+ 138.48; PIONA of identified light ends (wt %): paraffin 3.13, isoparaffin 3.28, naphthene 1.82, aromatic 0.49, unidentified 91.29 | `…Corelab.pdf` p.5 *(OCR)* |
| TEC-10DES, Zone A+B, "muestreo de fondo" | 12 Jul 2018 | SGS Coatzacoalcos C537-18 (LC-2749-18) | — | SG 60/60 **0.9577** (D1298) | 2.56 | 776 SUS at 100 °F | — | — | — | — | `…Zona AB AnalisisCrudo V603-18.pdf` p.2 |
| TEC-10DES, Zone B, "muestreo de fondo" | 12 Jul 2018 | SGS Coatzacoalcos C536-18 (LC-2746-18) | — | SG **0.9223** | 2.33 | 396 SUS at 100 °F | — | — | — | — | `…Zona B AnalisisCrudo V603-18.pdf` p.2 |
| TEC-10, Zone C, "condensado" | 3 Aug 2018 | SGS Coatzacoalcos C799-18 (LC-3019-18) | — | SG **0.9334** | 0.71 | 231 SUS at 100 °F | — | — | — | — | `Tecolutltla-10DES Zona C … 3-ago-18.pdf` p.2 |
| TEC-10, shore tank TC-10 | 21 Nov 2018 | Intertek Coatzacoalcos LAC-1771/18 | **30.42** (D4052) | 0.8734 g/cm³ at 60 °F | 1.66 | — | — | 0.025 % v/v (D4007) | 10.0 lb/1000 bbl | RVP 5.70 psi; acid no. 1.26 mg KOH/g (RapidOCR; Tesseract "12"); org. Cl <1 µg/g; Si <10 (actual 1.16), Al <5 mg/kg | `20181126 … Intertek.pdf` p.1 *(OCR)* |
| TEC-10, shore tank TC-10 | 11 Dec 2018 | Intertek LAC-1851/18 | **30.78** | 0.8717 g/cm³ | 1.08 | — | — | 4.0 % v/v | 15.0 lb/1000 bbl | RVP 7.30 psi; acid <0.1; org. Cl <1; Si 7.11 mg/kg; Al n.d. | `20181214 … Intertek.pdf` p.7 *(OCR)* |
| TEC-10, "Tanque 10" | 15 Jan 2019 | Intertek 3302548 / 2019-COTZ-000027 | **30.1** | SG 20/4 °C 0.8681 | 1.57 | — | — | 0.30 % v/v | 71.9 lb/1000 bbl | RVP 7.00 psi; acid <0.10; org. Cl <1 (actual 0); Si <10 (actual 2); Al <5 | `20190118 … Intertek.pdf` p.7 *(OCR)* |
| TEC-11, 2,361–2,364 m, **Tantoyuca** (not El Abra) | 22 Aug 2019 | Química Apollo, Poza Rica | **17.0** (D287 hydrometer) | 0.9295 g/cc | — | — | — | water 31.8 % v (18 % as emulsion); oil 67 % v; org. sediment 0.5 %, inorg. 0.7 % | water phase: Cl 31,550 mg/l, salinity 52,058 mg/l, pH 7.0 | asphaltenes 9.84 % w, paraffins 2.70 % w, asphaltic resins 21.53 % w | `20190824 Tecolutla-11 … Tantoyuca.pdf` p.4 |

Field measurements of oil density during the 2018 TEC-2 test (Weatherford tables reproduced in the IHS TEC-2 report, pp. with "Se realiza analisis de densidad observada"): observed 0.866–0.892 at 85–105 °F, corrected 0.885 SG at 60 °F = 28.38 °API (`Tecolutla 2 Final Report (IHS PTA) Spanish.pdf`, hourly test table, 20/64" choke period). The TEC-10 2018 flowback tables carry a blank API column (`data/processed/welltest/tec10_welltest_2018_hourly.csv`, column `api`). CNH monthly filings give 28.4–30.4 °API through 2020–21 and 30.9 °API, 1.6 % S, 48.8 lb/Mbbl salt in Nov 2022 (`docs/gaps.md` G-31 update of 15 Sep 2026).

### 1.2 Distillation / boiling-range data, 2018

| Sample | Method | IBP | 5 % | 10 % | 20 % | 30 % | 40 % | 50 % | 60 % | 70 % | 80 % | 90 % | 95 % | FBP | Recovery | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TEC-2, May 2018 | ASTM D7169 HT-GC, °F | 106 | 236 | 296 | 389 | 488 | 584 | 688 | 801 | 921 | 1068 | 1261 | >1328 | >1328 | 92.99 % m/m | SGS DP18-06236 p.1 |
| TEC-10 Zone C, Jul 2018 | ASTM D7169, °F | 158 | 247 | 314 | 425 | 530 | 632 | 745 | 860 | 994 | 1162 | >1328 | >1328 | >1328 | 88.55 % | SGS DP18-09329 p.1 |
| TEC-10 Zone C, Aug 2018 | ASTM D7169, °F | 42 | 221 | 263 | 378 | 485 | 587 | 695 | 808 | 933 | 1087 | 1255 | — | — | 94.6 % at 1328 °F, residue 5.4 % | Corelab p.1–2 *(OCR)*; also 15 % 320, 25 % 431, 35 % 536, 45 % 638, 55 % 753, 65 % 867, 75 % 1006, 85 % 1174 |

Corelab carbon-number distribution, TEC-10 Zone C (% off, cumulative): C5–C10 17.2 (17.2); C10–C20 28.9 (46.1); C20–C30 16.7 (62.8); C30–C40 9.9 (72.7); C40–C50 6.1 (78.8); C50–C60 4.2 (83.0); C60–C70 3.4 (86.4); C70–C80 3.1 (89.5); C80–C90 2.3 (91.8); C90–C100 2.8 (94.6); C100+ 5.4 (100) (Corelab p.6 *(OCR)*). Light-ends by ASTM D7900 (Corelab pp.3–5): ethane 0.01, propane 0.08, iC4 0.11, nC4 0.27, iC5 0.33, nC5 0.43, n-hexane 0.55, n-heptane 0.61, n-octane 0.72, n-nonane 0.54 wt %; benzene 0.04, toluene 0.13, xylenes 0.27 wt %; unidentified 91.20 wt %. The SGS TEC-2 report refers to a D7900 light-ends attachment that is not in the PDF.

### 1.3 PEMEX Engler distillations 1956–1975 (Poza Rica laboratory forms, handwritten entries, OCR)

Form layout: P.I.E. (initial boiling point), % distilled vs °C, temperatura máxima, total destilado %, residuo %, pérdida %, corte a 175 °C %, corte a 205 °C %, densidad a 20/4 °C, viscosidad SSU at three temperatures. Values below are RapidOCR readings cross-checked against Tesseract; "?" = one engine only or doubtful; "—" = not legible.

| Well, date (file) | Interval / formation | IBP °C | 5 / 10 / 20 / 30 / 40 / 50 / 60 % at °C | T max °C | Total dist. / residue / loss % | Cut ≤175 °C / ≤205 °C % | Density 20/4 | Viscosity SSU | Source page |
|---|---|---|---|---|---|---|---|---|---|
| TEC-6, 19 Oct 1956 | 2,336–2,338 m | 119 | 144 / 165 / 214 / 270 / 308 / 328? / — | 318 | 54? / — / — | 17.5 / 24 | **0.874** | 113 / 70 / 56 (temperatures not read; form order is ~30, 50, 70 °C) | `Tecolutla-6 Oil Distillation Oct 19, 1956.pdf` p.1 |
| TEC-7, 21 Jan 1957 | 2,335.0–2,337.0 m | 55 | 115 / 142 / 190 / 250 / 302 / 340 / — | 340 | 52 / — / — | 17.0 / 22.0 | **0.871** | 109 at 26 °C / 64 at 50 °C / 55 at 70 °C | `Tecolutla-7 Oil Distillation Jan 21, 1957.pdf` |
| TEC-6, 22 Jan 1959 | not read | 113? | 131 / 153 / 172 (15 %?) / 225 / 269 / — / — | 275 | 40.5 / 56.0 / 3.5 | 20.5 / 26.5 | **0.881** | 115 / 78 at 50 °C / 68 at 70 °C | `Tecolutla-6 Oil Distillation Jan 22, 1959.pdf` |
| TEC-7, "7-X-71" on form (file says Jul 1971) | 2,310–2,313 m, El Abra | 47 | 96? / 119 / 165 / 223 / 285 / 308 / — | 327 | 58.5 / 40.5 / 1.0 | 21.5 / 27.0 | **0.868** | 80 at 29–30 °C / 57 at 50 °C / 47 at 70 °C | `Tecolutla-7 Oil Distillation Jul 1971.pdf` |
| TEC-2, 9 May 1974 | 2,307–2,311 m, El Abra | 79 | 112 / 135 / 178 / 244 / 281 / 298 / 322 (65 % 331, 70 % 340, 75 % 348) | 348 | 75? / — / — | 19.0 / 24.0 | **0.857** | 101.2 at 35 °C / 84.1 at 50 °C / 59.1 at 70 °C | `Tecolutla-2 Oil Distillation May 9, 1974.pdf` |
| TEC-6, 19 Jun 1974 | 2,324–2,327 m, El Abra | 57 | 102 / 128 / 186 / 242 / — / — / — | 290 | 47.0 / 52.0 / 1.0 | 18.0 / 23.0 | **0.868** | 88 / 58 at 50 °C / — | `Tecolutla-6 Oil Distillation Jun 19, 1974.pdf` |
| TEC-2, 9 Jul 1974 | 2,307–2,311? | — | mostly illegible: 40 % 250?, 55 % 325? | — | 43.0? / — / — | — | — | 39 at 50 °C? | `Tecolutla-2 Oil Distillation Jul 9, 1974.pdf` (both engines fail on the handwriting) |
| TEC-6, 9 May 1975 | El Abra (interval not read) | 54 | 102 / 126 / 180 / 240 / 290 / 310 / 330 | 330 | 60.0 / 39.0 / 1.0 | 19.0 / 24.5 | **0.867** | 83 at 30 °C / 59 at 50 °C / 44 at 70 °C | `Tecolutla-6 Oil Distillation May 9, 1975.pdf` |
| TEC-7, 9 May 1975 | El Abra | 54 | 94 / 118 / 166 / 228 / 280 / 306 / 330 | 330 | 60.0 / 39.0 / 1.0 | 21.0 / 26.0 | **0.863** | 76 at 30 °C / 55 at 50 °C / 49 at 70 °C | `Tecolutla-7 Oil Distillation May 9, 1975.pdf` |

## 2. Gas compositions

| Component, mol % | TEC-6, 28 Aug 1970, casing gas ("gas toma por TR"), PEMEX lab report 105/70 *(OCR)* | TEC-2, 17 May 2018, separator gas, 6.3 kg/cm²(a), 38.8 °C | TEC-10 Zone C, 27 Jul 2018, three-phase test separator TP-18, 8.8 kg/cm²(a), 32.6 °C |
|---|---|---|---|
| N2 | not listed on form | 0.920 | 0.812 |
| CO2 | 4.78 | 10.572 | 11.142 |
| H2S | 0.66 | 1.746 | 0.989 |
| C1 | 79.81 | 70.442 | 70.321 |
| C2 | 7.91 | 6.665 | 7.707 |
| C3 | 4.24 | 4.252 | 4.701 |
| iC4 | 0.51 | 1.159 | 1.119 |
| nC4 | 1.18 (Tesseract "1418", RapidOCR 2.15; 1.18 closes the sum to 100.0) | 1.697 | 1.545 |
| iC5 | 0.25 | 0.681 | 0.505 |
| nC5 | 0.27 | 0.731 | 0.490 |
| C6 | 0.42 ("hexanos y más pesados") | 0.677 | 0.372 |
| C7 | — | 0.321 | 0.193 |
| C8 | — | 0.113 | 0.081 |
| C9 | — | 0.019 | 0.018 |
| C10 | — | 0.005 | 0.004 |
| C11+ | — | 0.000 | 0.001 (C11), 0 above |
| C6+ / C7+ (mol %, MW g/mol) | — | 1.135 (90.06) / 0.458 (97.55) | 0.669 (90.91) / 0.297 (98.28) |
| Gas gravity (air = 1) | 0.730 | 0.842 | 0.829 |
| Molecular weight | 21.139 | 24.4 | 24.0 |
| Gross heating value, BTU/ft³ dry | 1,152 (net 1,043) | 1,155 (net 1,045) | 1,133 (net 1,024) |
| GPM C3+ / C2+ | 2.064 (C3+?); 0.0491 bbl/Mcf | 3.065 / 4.846 | 2.787 / 4.846 |
| H2S, grains/100 scf | 420 | — | — |
| Z at sampling / STP | — | 0.9847 / 0.9975 | 0.9782 / 0.9975 |
| Pseudo-critical T, K / P, kg/cm²(a) | — | 234.2 / 49.9 | 232.6 / 49.9 |
| Air contamination, mol % | — | 0.137 | 0.101 |
| Note on form | "PTR = 76 kg/cm²" (casing pressure) | 3 cylinders taken (SGS-031, -098, -039 at 75 psi), one analysed (SGS-031) | 1 cylinder SGS-027 |
| Source | `Tecolutla-6 Gas Analysis Aug28, 1970.pdf` p.1 | `Tecolutla-2 Gas Comps V613-18.pdf` pp.2–5; `Tecolutla-2 Muestreo V613-18.pdf` pp.4, 8–9 | `Tecolutla-10 Gas Comps V603-18.pdf` pp.2–5 |

Method for both 2018 analyses: extended GC, GPA 2286, standard conditions 1.036 kg/cm²(a) and 15.6 °C. Both 2018 reports list reservoir temperature, reservoir pressure and completion data as "datos no transmitidos".

JT liquids screening on the TEC-2 gas (`Tecolutla-2 Gas Comps V613-18 (JT Liquids Recovery).xlsx`, Sheet1): yields from GPM (E10:E24, bbl/MMcf) 44.5 C2, 29.3 C3, 9.5 iC4, 13.4 nC4, 6.2 iC5, 6.6 nC5, 6.6 C6, 3.6 C7, 1.3 C8, total 121.2; with assumed JT recovery efficiencies (F10:F24: 0 C2, 25 % C3/iC4, 50 % nC4, 90 % C5, 95 % C6+) the JT yield is 39.0 bbl/MMcf (G25); JT range −18 to −27 °C, 800–1,000 psi (K7:L8). Assumed inputs, not measurements.

Mud-gas chromatography while drilling TEC-10 (`REPORTE FINAL TECOLUTLA-10_020518.pdf` p.76): at 2,429 m total gas 5,172 ppm with C1 2,083, C2 1,293, C3 178, iC4 180, nC4 144, iC5 121, nC5 73 ppm, CO2 2,169 ppm; through the El Abra 2,288–2,360 m the gas was 1–3 units, C1 100 % (pp.62–68).

## 3. Water analyses

| Item | TEC-2, 17 May 2018, separator outlet (report STIFFPVT019, 24 May 2018) | TEC-10, 27 Jul 2018, three-phase separator TP-18 (STIFFPVT021, 1 Aug 2018) |
|---|---|---|
| Na+ (calc.), mg/l (meq/l) | 16,627.4 (723.25) | 13,352.3 (580.79) |
| Ca2+ | 2,000.0 (99.8) | 480.0 (24.0) |
| Mg2+ | 510.3 (42.0) | 170.1 (14.0) |
| Ba2+ | 100.0 (1.5) | 130.0 (1.9) |
| Fe2+ | 0.1 | 0.5 |
| Cl− | 30,250.0 (853.24) | 20,850.0 (588.10) |
| SO4 2− | 560.0 (11.66) | 670.0 (13.95) |
| HCO3− | 97.6 (1.60) | 1,134.6 (18.60) |
| CO3 2−, OH− | 0 | 0 |
| Total cations / anions, mg/l | 19,237.8 / 30,907.6 | 14,132.9 / 22,654.6 |
| **TDS, mg/l** | **50,145.4** | **36,787.5** |
| NaCl-equivalent salinity, ppm | 49,912.5 | 34,402.5 |
| Suspended / settleable solids, mg/l | 6.0 / traces | 62.0 / 0 |
| pH at 73 °F | 6.68 | 6.98 |
| SG 60/60 °F | 1.0326 | 1.0239 |
| Resistivity at 75 °F, ohm·m | **0.128** | **0.196** |
| Conductivity at 75 °F, mS/cm | 78.408 | 50.896 |
| Alkalinity P / M (total) | 0 / 80 | 0 / 930 |
| Hardness Ca / Mg / total | 5,000 / 2,100 / 7,100 | 1,200 / 700 / 1,900 |
| Turbidity, FTU; colour Pt/Co | 9.16; 14 | 19.40; 327 |
| Water type (lab) | CONNATA | CONNATA |
| Ryznar / Langelier | 6.57 corrosive / 0.05 scaling (CaCO3 precipitates) | 5.15 scaling / 0.92 scaling |
| Stiff pattern | Na–Cl dominant; Ca 100 meq/l is the second cation; HCO3 negligible | Na–Cl dominant; HCO3 18.6 meq/l exceeds SO4 and Ca |
| Source | `Tecolutla-2 Water Analisis Stiff V613-18.pdf` p.1 | `Tecolutla10 Water Analisis Stiff V603-18.pdf` p.1 |

Both Stiff sheets leave "Formación" blank ("SIN INFORMACION"). The TEC-2 sampling report notes that the well was making roughly 90 % water on 17 May 2018 and that the water sample was taken from the separator sight-glass (`Tecolutla-2 Muestreo V613-18.pdf` pp.3, 5).

Other water salinity figures in the set:

| Where | Value | Source |
|---|---|---|
| PEMEX petrophysical parameters, El Abra | formation-water salinity 45,000 ppm; Rw 0.075 ohm·m at 65 °C; a = 1, m = 1.8–2, n = 2, Archie | `6 -Resumen Campo Tecolutla.docx` Table v.1 (docx table 4) |
| TEC-2 2018 test, field titration "Salinidad" column | 69,000–90,750 ppm during 8–17 May 2018 | IHS TEC-2 report, Weatherford hourly tables |
| TEC-10 2018 flowback, field "Salinidad" column | 19,000–22,000 ppm, 23 Jul–6 Aug 2018 | `data/processed/welltest/tec10_welltest_2018_hourly.csv` `salinity_ppm` |
| TEC-11 Tantoyuca oil, water phase | Cl 31,550 mg/l; salinity 52,058 mg/l | `20190824 Tecolutla-11 … Tantoyuca.pdf` p.4 |
| Rw used in the repo Archie pass | 0.054 ohm·m at 98.6 °C (PEMEX 0.075 at 65 °C corrected) | `data/processed/petrophysics/summary.json` `archie` |

## 4. PVT: measured vs correlated vs PEMEX

**No laboratory PVT study exists in the pulled set.** No file contains a measured bubble point, solution GOR, formation volume factor, live-oil viscosity or compressibility for Tecolutla. The three sets of numbers in circulation are (a) the PEMEX Ronda-1 summary, which quotes the PVT of a different well (Ezequiel Ordóñez-41) as representative, (b) IFR's PVT calculator, which is the HP Petroleum Fluids Pack correlations in an Excel add-in with assumed inputs, and (c) the IHS well-test models, which use the same Vasquez-Beggs / Beggs-Robinson correlations. Measured items are the stock-tank oil properties (§1), the separator-gas compositions (§2) and the produced GOR.

| Property | PEMEX (EO-41 PVT, "representative") | IFR PVT calculator (correlation) | IHS TEC-2 model (correlation) | IHS TEC-10 model (correlation) | Measured at Tecolutla |
|---|---|---|---|---|---|
| Oil gravity | 20 °API; density 0.8415 g/cm³ in the table, 0.9365 in the text | 28.4 °API (Oil!C8, from the TEC-2 SGS report, cell I16) | 28.0 °API | 28.2 °API | 26.5–30.8 °API stock tank (§1.1); 28.38 °API field density on TEC-2 test |
| Rs / RGA | 59.9 m³/m³ (= 336 scf/bbl) | 552 scf/stb assumed (C9), "slope of initial cum gas vs cum oil plot" (L12) | 96.37 m³/m³ (541 scf/bbl) | 101.55 m³/m³ (570 scf/bbl) | never measured; produced GOR: 565 cum. 1966–92, 685 on TEC-6 1964 survey, TEC-10 2018 flowback median 767 (P10–P90 597–942), IHS "~130 m³/m³ (750 scf/bbl) nearly constant"; TEC-2 May-2018 test 500 rising to 800 m³/m³ (`docs/04` §5; IHS TEC-10 p.13; IHS TEC-2 p.12) |
| Bubble point | 132 kg/cm² (1,877 psi, 12.9 MPa) | 2,849.2 psia hard-coded (Oil!F13); the sheet note (B33) says the correlation gave a Pb above discovery pressure and the author "chose to lower PBP to the highest level" that still gives rising GOR and Bo | 20,000 kPa(a) (2,901 psia) used in the Vogel IPR (p.23) | 23,800 kPa(a) (3,452 psia) in the Vogel IPR (p.24); text says drainage area is undersaturated with Rs "≈100 m³/m³ estimated through correlations" (p.13) | never measured |
| Bo | 1.1923 | 1.299 rb/stb at Pb; 1.290 at 3,400 psia (Oil!D24, D30) | 1.283 m³/m³ | 1.296 m³/m³ | never measured |
| Oil viscosity | 11.2 cp | 0.624 cp at Pb, 0.657 at 3,400 psia (Oil!E24, E30); dead-oil input 13.67 cSt at 40 °C (K18) | 0.7387 mPa·s | 0.7176 mPa·s | dead oil only: 13.67 cSt at 40 °C (TEC-2), 18.73 cSt at 40 °C (TEC-10 Zone C) |
| Oil compressibility | — | 1.61e-5 psi⁻¹ at Pb to 1.35e-5 at 3,400 psia (Oil!F24:F30) | 1.79e-6 kPa⁻¹ (1.23e-5 psi⁻¹) | 1.82e-6 kPa⁻¹ (1.25e-5 psi⁻¹) | never measured |
| Formation / total compressibility | — | — | cf 6.78e-7 kPa⁻¹; ct 1.98e-6 kPa⁻¹ (1.37e-5 psi⁻¹) | cf 6.86e-7 kPa⁻¹; ct 6.13e-6 kPa⁻¹ (4.23e-5 psi⁻¹) | never measured |
| Reservoir temperature | 65 °C (docx Table v.1, for Rw) | 95 °C entered (J11), converted to 228.6 °F (K11 → C11) | 101.0 °C | 98.6 °C | gradient surveys: TEC-2 99.3 °C at 2,250 m, 26 Mar 2018 (IHS TEC-2 pp.102–104); TEC-10 97.5 °C static / 97.8 °C flowing at 2,120 m, 3 Aug 2018 (IHS TEC-10 pp.93–94); Weatherford log header TMAX 96 °C (CXD LAS) |
| Reservoir pressure | initial 252 kg/cm² (docx §vi) | 25.4 MPa = 3,684 psia (Oil!J13:K13) | pi 24,190 kPa(a) at 2,309 m | pi 24,304 kPa(a) at 2,322.1 mTVD | see `docs/05` |
| Gas properties | — | Gas!C8:C11 from the TEC-10 analysis (SG 0.829, N2 0.812, CO2 11.142, H2S 0.989 %); Z 0.871 at Pb, 0.888 at 3,400 psia; µg 0.021–0.023 cp; Bg 0.0060–0.0051 rcf/scf (Gas!C22:J28) | — | — | separator-gas composition measured (§2) |
| Water properties | — | Water!C8 salt 3.68 wt % from TEC-10 TDS 36,787.5 (J9); Bw 1.046, µw 0.28 cp, Rsw 13 scf/stb, cw 3.35e-6 psi⁻¹ at Pb (Water!C19:F19) | — | — | Stiff analyses (§3) |
| Correlations | PEMEX Poza Rica lab, bottom-hole sample of EO-41 | PVTProps.XLA: Pb, Rs, Bo, co Vasquez-Beggs (1980) with Ramey (1964) for co; µo Beggs-Robinson (1975)/Vasquez-Beggs; Z Dranchuk-Purvis-Robinson with Standing's N2/CO2/H2S pseudo-criticals; µg Lee-Gonzalez-Eakin; water from Numbere-Brigham-Standing/Meehan (`pvtdoc.pdf` pp.3–7) | Vasquez-Beggs; Beggs & Robinson (p.21) | Vasquez-Beggs; Beggs & Robinson (p.22) | — |
| Separator conditions in correlation | — | 80 °F, 100 psia assumed (C12:C13) | — | — | TEC-2 sample 6.3 kg/cm²(a), 38.8 °C; TEC-10 8.8 kg/cm²(a), 32.6 °C (§2) |
| Source | `6 -Resumen Campo Tecolutla.docx` Table v.2 and §v text | `PVT Calculator (Tecolutla).xlsx` sheets Oil, Gas, Water (external link `PVTPROPS.XLA`) | `Tecolutla 2 Final Report (IHS PTA) Spanish.pdf` pp.21, 23 | `Tecolutla 10 Final Report (IHS PTA) Spanish.pdf` pp.13, 22, 24 | as cited |

PEMEX Ronda-1 test results quoted in the same docx (Table vi.1): 2,307.4–2,321.7 m: 258 bd oil, 1.7 MMcfd gas, RGA 1,163 m³/m³, PTP 174 kg/cm², 6 mm choke; 2,345–2,349 m: 352 bd, 0.153 MMcfd, RGA 77; 2,335–2,339 m: 453 bd, 0.244 MMcfd, RGA 96 m³/m³.

## 5. Core summary: TEC-10 core 1

| Item | Value | Source |
|---|---|---|
| Interval cut | 2,352–2,362 mMD attempted (10 m), 6 1/8" hole, water-based polymer mud 1.11 g/cm³ | `REPORTE FINAL TECOLUTLA-10_020518.pdf` pp.9–10, 73 |
| Recovery | 1.20 m (mud-log operations, p.10); 1.32 m (mud-log recommendations, p.79); 1.30 m and 14.44 % (Stratascan inventory, core state "regular a malo") | as stated; `Tecolutla10_ReporteFinal_V603-18.pdf.txt` inventory sheet |
| Core diameter | 2.5 in | Stratascan inventory |
| Coring conditions | ROP 2.5 m/h with a drill-pipe connection in mid-cut; Weatherford recommends ≤1 m/h in future because "El Abra es un Mudstone-Wackstone muy fracturado" | mud-log report p.79 |
| Handling | so fractured it could not be removed from the aluminium sleeve; photographed in white and UV light in the sleeve; one 1.00 m tube | Stratascan §1.1–1.2 |
| Subsea depth | about 2,317 mSS (KB 6.13 m, survey), inside the perforated interval 2,349.5–2,353.0 mMD | `docs/12` §5, `summary.json` |
| Age given by the lab | "Cretácico Superior" | Stratascan §2.1 |

Megascopic description (Stratascan §1.2; the report writes the depths as 5352–5353, a typo for 2352–2353):
- Upper 2,352.00–2,352.38 m: grainstone of benthic foraminifera and bioclasts, very light brown, strongly recrystallised, good intercrystalline microporosity from recrystallisation, fair vuggy microporosity and rare microfractures, **"con posibles trazas de aceite"**.
- Middle 2,352.38–2,352.61 m: wackestone to packstone of benthic foraminifera, greenish grey, argillaceous, finely recrystallised, no visible porosity in the matrix.
- Lower 2,352.61–2,353.30 m: as the upper part, with possible traces of oil.

Spectral gamma on the core (`…PetrofBasicaV603-18 (1).xlsx` sheet `spc1`, 27 readings at 5 cm from 2,352.00 to 2,353.30 m): total GR 9.7–33.8 API (mean 19.7), K 0.03–0.24 %, U 0.35–1.78 ppm, Th 0.59–1.98 ppm; the highest total GR (27–32 API) is at 2,352.3–2,352.5 m, the argillaceous middle part. The lab notes the log is too short to depth-match to wireline (§1.3).

### 5.1 Routine core analysis, three horizontal plugs (Stratascan §3.1; workbook sheets `PlugSum`, `Plug@500`, `Plug@NCS`)

| Plug | Depth mMD | Length × dia, cm | NCS psi | Pore vol cm³ | He porosity, frac | k air, mD | k Klinkenberg, mD | b (He) | Grain density g/cm³ | Lithology (sheet `LithoDesc`) |
|---|---|---|---|---|---|---|---|---|---|---|
| N1H1 | 2,352.25 | 3.553 × 2.544 | ambient | 0.543 | 0.030 | — | — | — | 2.696 | grainstone of benthic forams and bioclasts, cream, highly recrystallised, secondary dissolution porosity partly filled with calcite, intercrystalline porosity |
| | | | 500 | 0.419 | 0.0234 | 0.037 | 0.020 | 45.6 | | |
| | | | 3,400 | 0.308 | 0.0173 | 0.009 | 0.004 | 70.0 | | |
| N1H2 | 2,352.70 | 4.379 × 2.539 | ambient | 1.677 | 0.076 | — | — | — | 2.709 | same |
| | | | 500 | 1.461 | 0.0665 | 1.158 | 0.956 | 11.0 | | |
| | | | 3,400 | 1.385 | 0.0633 | 0.467 | 0.356 | 16.2 | | |
| N1H3 | 2,352.89 | 2.944 × 2.541 | ambient | 1.185 | 0.079 | — | — | — | 2.713 | same |
| | | | 500 | 1.123 | 0.0755 | 0.245 | 0.174 | 21.3 | | |
| | | | 3,400 | 1.058 | 0.0715 | 0.128 | 0.084 | 27.7 | | |

3,400 psi (239 kg/cm²) was the maximum overburden "de acuerdo a instrucciones de Tonalli Energía". Lab fits: k_air = 0.0138·e^(50.06 φ) at 500 psi and 0.0036·e^(61.56 φ) at 3,400 psi; k_Klink = 0.8228·k_air^1.1237 (500 psi), 0.8568·k_air^1.1381 (3,400 psi); Winland R35 rock types 3–4 (N1H2 TR3, N1H1/N1H3 TR4 at 3,400 psi, `Plug@NCS` K15:U17). The lab attributes the stress sensitivity to fracturing of the plugs (§3.1).

### 5.2 Dean-Stark fluid saturations (toluene extraction, before cleaning; `Plug@500` J15:K17, Stratascan RCA sheet)

| Plug | Oil, % PV | Water, % PV | Gas by difference, % PV |
|---|---|---|---|
| N1H1 (2,352.25) | 58.8 | 23.9 | 17.3 |
| N1H2 (2,352.70) | 19.7 | 20.5 | 59.8 |
| N1H3 (2,352.89) | 13.8 | 17.8 | 68.4 |

Pore volume basis is the 500 psi helium porosity. Core cut with water-based mud (mud-log p.73); no tracer analysis reported.

### 5.3 Petrography (six thin sections, unwashed to preserve hydrocarbon evidence; `Tecolutla1N1Petrog1(6LD)… EngVr.pdf` pp.1–22 and Stratascan §2.1)

| Sample | Depth m | Dunham | Main components | Diagenesis | Visual porosity (point count) | Hydrocarbons | Quality (lab tick) |
|---|---|---|---|---|---|---|---|
| N1PS | 2,352.15 | grainstone | miliolids, textulariids, bioclasts, few rudists, peloids C, intraclasts C; microsparite E | compaction, recrystallisation, calcite cement, calcitisation | intercrystalline, moldic, intrafossil; dissolution 3 %; "good to fair" in photos B–D | none | none |
| N1H1 | 2,352.25 | grainstone (packstone in photos A–B) | miliolids, bioclasts, intraclasts, peloids | same | little intercrystalline; dissolution 2 % | none | none |
| N1PM | 2,352.38 | wackestone (to packstone) | benthic forams; **planktonic foraminifera C (Globotruncana sp.)**, micrite C, scattered pyrite; in contact with a planktonic-foram wackestone | same | none visible | none | none |
| N1H2 | 2,352.70 | grainstone | miliolids, textulariids, bioclasts, intraclasts A, microsparite A | same | intercrystalline microporosity, dissolution 3 % | none | none |
| N1H3 | 2,352.83 | grainstone | miliolids, textulariids, calcitised bioclasts; fine fractures sealed with calcite | same | micro-dissolution, dissolution 4 %; "good intercrystalline" in photos B, D; moldic in C | none | none |
| N1PI | 2,353.24 | grainstone | miliolids, textulariids, bioclasts, peloids; sealed fractures; possible micrite-filled cavity | same | dissolution 2 %; pyrite-filled microporosity | none | none |

Per-sample visual porosity totals read from the summary row of the point-count table: 5, 2, 1, 3, 4, 3 % (N1PS … N1PI; column assignment from text extraction, treat as indicative). Rows "Intergranular 1 1" and "Intercrystalline 1 1" are present for two of the grainstones. Depositional environment: outer shelf ("plataforma media a externa"). Dolomite, anhydrite, quartz, glauconite and organic matter: none recorded. Impregnation: "None" ticked for all six; the lab's overall text nonetheless calls the grainstone porosity "de buena a regular calidad".

### 5.4 Workbook caveat

Sheets `DCAmbTab`, `DCSCTab` and `TodasSCDC` in the plug workbook contain full-diameter samples N1F95DC2 … N1F9DC21 at 5,998–6,005 m with a "Pemex Exploración y Producción" header, grain density 2.80–2.84 g/cm³ and a "Microfractura" comment; `PlugSum` AS19:AT47 lists N1H2…N1H9 at 5,684–5,689 m. These are template residue from another job, not Tecolutla-10 data (TEC-10 TD is 2,490 m). Only N1H1–N1H3 at 2,352.25–2,352.89 m belong to this well.

## 6. Rock properties from logs, mud log and well tests

### 6.1 Well tests (IHS Markit, 2018)

| | TEC-2, 10–30 May 2018, 2,307–2,311 mKB | TEC-10, 21 Jul–31 Aug 2018, 2,349.5–2,350.5 + 2,351.5–2,353.0 mKB MD |
|---|---|---|
| Model | skin & boundaries, one constant-pressure boundary | skin & boundaries, one constant-pressure boundary |
| kh/µ | 5,838 mD·m/mPa·s (846 md·ft/cP) | 519 mD·m/mPa·s (1,730 md·ft/cP) |
| k (oil) | 50 mD (63 mD from the radial-flow derivative; 140 mD on h = 25 m from the 1956 DST) | 18 mD (18.5 mD first radial flow; 8.9 mD second pseudo-radial flow) |
| h (supplied by IFR) | 8 m | 13.2 m |
| φ, Sw (supplied by IFR) | 11 %, 33 % | 10.7 %, 55 % |
| Skin | +196 (+254 from derivative); flow efficiency 0.054; Δp skin 6,991 kPa | +4.9; flow efficiency 0.629; Δp skin 1,100 kPa |
| Boundaries | constant-pressure boundary 700 m, no-flow boundary 150 m; min. drainage area 890 acres (1,900 × 1,900 m) | no-flow boundary 125 m, constant-pressure boundary 195 m; 640 acres assumed, min. 327 acres (1,150 × 1,150 m) |
| Wellbore radius / storage | 0.107 m; wellbore volume 1,955 m³ | 0.107 m; 145 m³ |
| Pressures | pi = pR 24,190 kPa(a) at 2,309 m (10.5 kPa/m); last pwf 16,799 kPa(a) | pi = pR 24,304 kPa(a) at 2,322.1 mTVD (10.5 kPa/m); last pwf 21,342 kPa(a) |
| Last rates | 8.0 m³/d oil, 72.1 m³/d water, 6.2 10³m³/d gas | 31.1 m³/d oil, 18.1 m³/d water, 4.06 10³m³/d gas; max 178 m³/d oil |
| Source | `Tecolutla 2 Final Report (IHS PTA) Spanish.pdf` pp.5–6, 8, 12–14, 21 | `Tecolutla 10 Final Report (IHS PTA) Spanish.pdf` pp.5–6, 13–14, 18–22 |

Both reports say the 8 m and 13.2 m thicknesses were provided by IFR; k scales inversely with them.

### 6.2 TEC-10 wireline (Weatherford, 2 May 2018) zoned in the repo (`summary.json` `tec10_zones`; Archie a = 1, m = 2, n = 2, Rw 0.054 ohm·m at 98.6 °C, φ = mean of limestone neutron and density porosity, uncalibrated to core)

| mSS | mMD | GR mean | φ mean | ILD median ohm·m | Archie Sw | m with φ ≥ 6 % | m with φ ≥ 6 % and Sw ≤ 50 % |
|---|---|---|---|---|---|---|---|
| 2,270–2,294 | 2,302.6–2,328.0 | 91 | 0.107 | 4.1 | 0.99 | 25.2 | 0.0 |
| 2,294–2,311 (TEC-12 window) | 2,328.0–2,346.0 | 83 | 0.089 | 5.2 | 0.99 | 16.5 | 0.0 |
| 2,311–2,320 (perforations) | 2,346.0–2,355.5 | 44 | 0.054 | 30.1 | 0.79 | 4.1 | 2.2 |
| 2,320–2,340 | 2,355.5–2,376.6 | 65 | 0.053 | 17.1 | 0.91 | 6.6 | 1.0 |
| 2,340–2,360 | 2,376.6–2,397.8 | 71 | 0.026 | 51.4 | 0.96 | 0.2 | 0.0 |
| 2,360–2,400 | 2,397.8–2,440.0 | 84 | 0.025 | 53.9 | 0.94 | 0.7 | 0.6 |
| 2,400–2,450 | 2,440.0–2,490.0 | 84 | 0.031 | 39.9 | 0.95 | 2.5 | 0.3 |

Zone medians in `docs/14` §1: window Rt 5.2, φN 10.0 %, φD 6.7 %, GR 134, PE 3.86; perforated interval Rt 30, φN 1.4 %, φD 5.8 %, PE 5.09; below the LKO (2,374–2,447 mSS) Rt 45, φD 4.2 %. The density porosity through the cored interval (5.8 %) matches the plugs (2.3/6.7/7.6 %); the neutron (1.4 %) does not (`docs/14` §2). GR rises with porosity in every well with a porosity curve (`docs/09` §2). CMI fracture density 0–7 fractures/m over 2,296–2,488 mMD, not yet examined (`docs/09` §5). PEMEX log-derived values for the 1956 TEC-2 tests: φ 10–12 % / Sw 35–40 % at 2,307.4–2,321.7 m; 6–8 % / 55–60 % at 2,345–2,349 m; 5–6 % / 60–65 % at 2,335–2,339 m; field-wide "porosidad del orden de 5 a 12 % y Sw 24 a 38 %" (docx Table vi.1 and §v).

### 6.3 Mud-log lithology at TEC-10 (`REPORTE FINAL TECOLUTLA-10_020518.pdf` pp.62–68)

2,288–2,298 m: 50–60 % soft grey calcareous shale, 20–30 % white-cream compact mudstone / brown mudstone-wackestone, 20 % fine-medium grey sandstone; 1–3 gas units, C1 100 %. 2,328–2,346 m (the TEC-12 window): 70 % compact mudstone / mudstone-wackestone partly recrystallised, 30 % soft calcareous shale, traces of sandstone; 1–3 gas units, calcimetry 78 %. 2,346–2,360 m (perforated and cored interval): 100 % mudstone / mudstone-wackestone, calcimetry 86–90 %, 2.1–3.0 gas units. No oil show is recorded in the El Abra; the two "intervalos de interés" are clastic (850–880 m, 22,941 ppm; 1,775–1,815 m, 29,072 ppm) and the recommendation interval 2,429–2,490 m (5,172 ppm with C2–C5 present).

### 6.4 Mechanical properties, TEC-10 (Weatherford CXD dipole-sonic product; `TECOLUTLA 10_CXD PROPIEDADES MECANICAS…las`, 2,301.7–2,491.7 mMD, 0.025 m step, 6,383 valid samples)

| Curve | Unit | 2,302–2,330 m | 2,330–2,380 m | 2,380–2,430 m | 2,430–2,487 m | Whole log mean (min–max) |
|---|---|---|---|---|---|---|
| YME_DYN, dynamic Young's modulus | Mpsi | 4.69 (3.94–5.36) | 6.62 (3.58–10.44) | 9.27 (7.83–10.24) | 9.12 (7.31–10.71) | 8.02 (3.58–10.71) |
| PR_DYN, dynamic Poisson ratio | — | 0.316 (0.301–0.332) | 0.332 (0.283–0.416) | 0.311 (0.280–0.346) | 0.318 (0.289–0.354) | 0.320 (0.280–0.416) |
| SMG_DYN, shear modulus | Mpsi | 1.78 | 2.49 | 3.54 | 3.46 | 3.04 (1.28–4.03) |
| BMK_DYN, bulk modulus | Mpsi | 4.23 | 6.71 | 8.19 | 8.40 | 7.47 (3.65–11.04) |
| BRIT, brittleness | % | 43 | 51 | 76 | 73 | 65 (8–92) |
| CSG, closure-stress gradient (quick look) | psi/ft | 0.698 | 0.720 | 0.693 | 0.702 | 0.705 (0.658–0.838) |
| PP_NORMAL, normal pore pressure | psi | 1,007 | 1,023 | 1,044 | 1,066 | 1,001–1,078 |
| DTC / DTS | µs/ft | 72.9 / 140.3 | 60.6 / 122.4 | 52.6 / 100.4 | 52.6 / 102.4 | 56.6 / 110.7 |
| DEN bulk density | g/cm³ | 2.576 | 2.596 | 2.639 | 2.629 | 2.615 |

No UCS or static-modulus curve exists in the file. Header: mud "E. INVERSA" 1.36 g/cm³, Rm 0.12, Rmf 0.09 at 29 °C, TMAX 96 °C, KB 5.13 m, matrix "arenisca 2.65 g/cm³" for the CXD run; over-pulls during logging "pudo haber afectado la calidad de las lecturas" (remark 13). The interval above 2,301.7 m is cased (7" at 2,285 m).

## 7. Gaps

1. **No PVT study.** No bubble point, Rs, Bo, live viscosity or compressibility has ever been measured on Tecolutla oil. Every value in §4 is a correlation or a PEMEX analogue (EO-41). Closing G-31 requires a bottom-hole or recombined separator sample; the 2018 separator gas and stock-tank oil (§1–§2) with the metered separator GOR would allow a recombination if the separator oil rate and shrinkage were recorded.
2. **Two TEC-10DES "muestreo de fondo" oils (SG 0.9577 and 0.9223, 2.3–2.6 % S, 12 Jul 2018) do not match the stock-tank oil (SG 0.87–0.90, 1.1–1.7 % S).** Which zones A and B are, and whether these were swabbed or completion-fluid-contaminated samples, is not stated in the reports.
3. **The Corelab densities (0.8863, 0.8916) have no stated basis or temperature** and only OCR text exists.
4. **PEMEX distillation forms**: the TEC-2 Jul-1974 form is illegible; on the other eight, the interval and some percentages are uncertain (§1.3). Original scans should be checked by eye before any of the 1956–75 densities are quoted.
5. **No water analysis is tied to a formation**, and the two 2018 analyses differ by 13,000 mg/l TDS. TEC-10's field-titration salinity (19–22 kppm) is lower than its lab TDS (36.8 kppm); TEC-2's (69–91 kppm) is higher than its lab TDS (50.1 kppm). No Rw has been measured at reservoir temperature.
6. **Reservoir temperature** is 97.5–99.3 °C from the 2018 gradient surveys; the PEMEX 65 °C in the docx and the 95 °C entered in the PVT calculator are both lower; the calculator converts 95 °C to 228.6 °F.
7. **Core**: one 1.3 m core, three plugs at one depth, no vertical plug, no electrical properties (a, m, n), no capillary pressure, no relative permeability, no grain-density/mineralogy (XRD), no tracer on the Dean-Stark water, no depth match to wireline; recovery 12–14 % of the 10 m attempted. The TEC-12 window (2,328–2,346 mMD at TEC-10) was not cored.
8. **Petrography vs hand specimen**: hand specimen "posibles trazas de aceite", thin sections "sin presencia de hidrocarburos" in all six, Dean-Stark 14–59 % PV oil. The UV photographs in the report would settle which is right; only the text rendering has been read.
9. **Mechanical**: dynamic moduli only; no static correlation, no UCS, no calibration to the plugs; the sonic was run with a sandstone matrix setting.
10. **Well tests**: h, φ and Sw were inputs from IFR, not outputs; TEC-2's k rests on h = 8 m, TEC-10's on 13.2 m. Neither report gives a measured Pb; each IPR assumes one (20,000 and 23,800 kPa(a)).
11. **Gas**: the 2018 flowback orifice calculations used a gas SG of 0.952 (`tec10_welltest_2018_hourly.csv` `gas_sg`), whereas the laboratory gas gravity is 0.829; gas rates and GOR from the test tables carry that assumption. The TEC-6 1970 form lists no N2.
12. **Missing attachments**: the SGS TEC-2 D7900 light-ends table ("See Attached"); the Weatherford TEC-10 daily-test API values (blank column).

## Reader's notes (interpretation, not source data)

- Stock-tank gravity is consistently 28–31 °API across TEC-2 (2018), TEC-10 (2018–19), the 2018 field density (28.4) and the 1956–75 PEMEX densities (0.857–0.881 at 20/4 °C, i.e. roughly 29–33 °API after the ~0.004 shift from 20 °C to 60 °F). The PEMEX EO-41 table (20 °API, 0.9365 g/cm³, 11.2 cp) is a different oil and its 0.8415 g/cm³ table entry is internally inconsistent with 20 °API. The TEC-10 Zone C SGS sample (26.5 °API, 40–44 % water, Si 4 ppm) and the three Coatzacoalcos "fondo/condensado" samples (SG 0.92–0.96) look like early clean-up or emulsion samples rather than reservoir oil; the Intertek tank samples four to six months later are the cleaner measurement.
- Two input errors in `PVT Calculator (Tecolutla).xlsx` deserve a fix before its outputs are quoted: (1) Oil!K11 converts 95 °C with `=(J11+32)*9/5` = 228.6 °F; the correct conversion is 203 °F (and the 2018 surveys say 98–99 °C = 209–210 °F). (2) Oil!C10 (`=141.5/(C8+131.5)` = 0.885, the oil SG) is passed as the *gas* gravity argument to BP, Rs, Bo and Co, whose manual defines SG as "gas specific gravity relative to air"; the measured gas gravities are 0.829–0.842, so the effect is modest but the cell is mislabelled. With the 2,849 psia Pb hard-coded, the calculator's Bo 1.30 and µo 0.62 cp are close to IHS's 1.28–1.30 and 0.72–0.74 cp because all three runs use the same Vasquez-Beggs / Beggs-Robinson equations with nearly the same inputs; agreement between them is not corroboration.
- The produced GOR (565 cumulative 1966–92; 685 in 1964; 740–770 on TEC-10 in 2018; 500–800 m³/m³ ≈ 2,800–4,500 scf/bbl on TEC-2 in 2018 with 90 % water cut) puts solution GOR at or above 550 scf/bbl, which is what IFR assumed. The PEMEX 336 scf/bbl and Pb 132 kg/cm² do not describe this fluid. On the Vasquez-Beggs basis with the measured gas gravity and 28–30 °API, an Rs of 550–750 scf/bbl gives a Pb of roughly 2,900–3,800 psia at 98 °C (my calculation, no separator correction), so the reservoir (3,500 psia initial) is at most a few hundred psi undersaturated and may be saturated at the upper end, and TEC-10's GOR rise at low tubing pressure (`docs/04` §5) is the expected behaviour. A single bottom-hole sample from TEC-10 would resolve this for a few thousand dollars and is the highest-value fluid measurement left in the field.
- IHS's TEC-10 total compressibility (6.13e-6 kPa⁻¹) is three times TEC-2's (1.98e-6 kPa⁻¹) although co and cf are the same; with So 0.45 and Sw 0.55 it implies a water compressibility of ~8e-6 kPa⁻¹, twenty times the usual value, so either a gas saturation or a different cw was set in that model. It affects the TEC-10 boundary distances, not k or skin.
- Rw: converting the 2018 laboratory resistivities to 98.6 °C with the Arps relation gives 0.074 ohm·m for the TEC-10 water and 0.048 ohm·m for the TEC-2 water, bracketing the 0.054 used in `summary.json`. The TEC-10 water (higher HCO3, lower Ca, lower TDS) is the fresher of the two; neither sheet says whether it is formation water or a mix with completion brine, and TEC-10 had been swabbed and acidised in July 2018.
- The three plugs come from a 0.65 m span at one depth; their 0.1–0.5 mD Klinkenberg permeability at stress is two orders of magnitude below the 18 mD the well test attributes to 13.2 m of pay, so flow at TEC-10 is through fractures or vugs the plugs do not sample (the core "could not be removed from the sleeve" because of fracturing; Weatherford calls the El Abra "muy fracturado"). The core supports matrix porosity of 6–8 % in the grainstone and near zero in the argillaceous wackestone, which is the neutron–density story in `docs/14`.
- The lab's "Cretácico Superior" and the Globotruncana in the middle wackestone are worth a geologist's look: if the planktonic-foram wackestone is a real Upper Cretaceous (Agua Nueva/San Felipe-type) intercalation rather than El Abra lagoonal facies, the "El Abra" top pick at TEC-10 and the TEC-12 window correlation should be revisited.
- Mechanical data are dynamic only. For a fracture-stimulation or wellbore-stability design at TEC-12 the 2,302–2,330 m interval (E 4–5 Mpsi, ν 0.32, brittleness 43 %) is markedly softer than the 2,380–2,487 m section (E 9–10 Mpsi, brittleness 73–76 %); that contrast, not the absolute values, is the usable information.
