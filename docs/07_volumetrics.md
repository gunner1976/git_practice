# Task 7 — Volumetrics: 11.2 versus 7.8 MMbbl, and a probabilistic range

Script: `src/volumetrics.py`. Outputs: `data/processed/volumetrics/ooip_by_source.csv`, `analogue_rf.csv` (45 El Abra fields from the CNH table), `monte_carlo.csv` (20,000 draws), `summary.json`, `figures/07_volumetrics.png`.

## 1. Where the two numbers come from

| Source | Area km² | Gross m | N/G | φ | Sw | Bo | OOIP MMbbl | File |
|---|---|---|---|---|---|---|---|---|
| IFR `Summary (GLJ)` sheet, identical in all eleven economic models 2020–2023 | 2.55 (630 ac) | 42.3 | 0.40 | 0.070 | 0.30 | 1.19 | **11.16** | `2023-09-29 Tec-12 Economics.xlsm!Summary (GLJ)` D6:D19 |
| Petrel Robertson geomodel, deep contact −2,374 mSS, all wells | 2.55 | 46.8 | 0.427 | 0.056 | 0.20 | 1.19 | 11.96 | `Petrel Robertson Volumetrics.xlsx` col B |
| Petrel Robertson, TEC-10 new logs only | 2.55 | 46.8 | 0.418 | 0.062 | 0.19 | 1.30 | 12.04 | col D |
| Petrel Robertson, TEC-2, 9 and 10 vintage logs | 2.55 | 46.8 | 0.352 | 0.047 | 0.21 | 1.30 | **7.59** | col F |
| CNH / PEMEX official | 3.12 | — | — | — | — | — | **7.82** | `El Abra Trend Field Analogies.xlsx` row Tecolutla (VO_Crudo); PEMEX field summary, "Volumen Original 7.8 mmb" for 1P, 2P and 3P |

All five recompute exactly from their own inputs. The "7.8 MMbbl in the analogue table" is not an internal inconsistency: it is PEMEX's booked original volume as filed with CNH (with 1.91 MMbbl produced to April 2015, 24.5 % recovered, 3P EUR 2.13 MMbbl at 27.2 %). The "11.2" is IFR's own volumetric on the same rock volume with 40 % net-to-gross and 7 % porosity. Petrel Robertson's third case shows what closes the gap: with the vintage-log petrophysics of TEC-2 and TEC-9 (N/G 0.35, φ 4.7 %) the same geomodel gives 7.6 MMbbl; with TEC-10's modern logs (N/G 0.42, φ 6.2 %) it gives 12.0. **The 11.2 versus 7.8 difference is a petrophysics question, porosity and net-to-gross, not an area or structure question.** Task 9 (the LAS correlation panel) is where it gets settled; until then both are legitimate.

## 2. Probabilistic field OOIP

Triangular distributions spanning the sources (area 2.40–2.55–3.12 km², gross 40–44–47 m, N/G 0.30–0.40–0.45, φ 4.5–6.0–7.5 %, Sw 18–25–35 %, Bo 1.19–1.25–1.30), 20,000 draws:

| | P90 | P50 | P10 |
|---|---|---|---|
| Field OOIP | **8.1 MMbbl** | **10.0 MMbbl** | **12.2 MMbbl** |

Porosity and net-to-gross each swing the answer by ±2.5 MMbbl; area by −0.6/+2.3 (the 3.1 km² CNH surface versus the 630-acre IFR polygon); Sw ±1.2; gross ±0.8; Bo ±0.5. Both quoted figures sit inside the range: 7.8 is close to P90, 11.2 between P50 and P10.

## 3. Recovery factor context (CNH data, 45 El Abra fields to April 2015)

| | Value |
|---|---|
| Reef-rim fields, median RF to date | 30 % |
| Reef-rim fields, production-weighted RF to date | 29 % (the "29 % trend average") |
| Reef-rim 3P EUR RF, P90 / median / P10 | 12 % / 31 % / 40 % |
| Best reef-rim field (3P EUR) | 53 % |
| Tecolutla on the CNH basis | 24.5 % to Apr 2015; 25 % with production to 2022 on 7.8 MMbbl |
| Tecolutla on the IFR basis | 18 % on 11.2 MMbbl |
| Tecolutla OOIP density | 2.5 MMbbl/km² versus a reef-rim median of 8.3 MMbbl/km² |

Tecolutla is a small, thin accumulation for the trend. On the CNH volume it has already recovered what a typical reef-rim field has; on the IFR volume it is below the trend and has a third of its trend-average recovery still ahead.

## 4. Remaining recoverable oil

Produced to end-2022: 1.72 MMbbl recorded, 1.98 MMbbl with the PEMEX wellfile allocations (task 4). Remaining = OOIP × RF − 1.98:

| OOIP basis | RF 25 % | RF 29 % | RF 33 % | RF 38 % |
|---|---|---|---|---|
| CNH 7.8 | 0.0 | 0.3 | 0.6 | 1.0 |
| P90 8.1 | 0.1 | 0.4 | 0.7 | 1.1 |
| **P50 10.0** | 0.5 | **0.9** | 1.3 | 1.8 |
| P10 12.2 | 1.1 | 1.6 | 2.1 | 2.7 |
| IFR 11.2 | 0.8 | 1.3 | 1.7 | 2.3 |

The review's "roughly 1.2 MMbbl remains recoverable" is the IFR OOIP at the trend-average RF. On the P50 OOIP and the same RF it is 0.9 MMbbl; on the CNH volume it is 0.3 MMbbl. The number to carry into the handover is **0.3 to 1.6 MMbbl, most likely about 0.9 MMbbl at trend-average recovery**, with the upper half of that range contingent on TEC-10-quality petrophysics applying across the field.

## 5. TEC-12 drainage volumetrics in the files

| Source | Area | Net m | φ | Sw | Bo | OOIP | RF | Recoverable | Comment |
|---|---|---|---|---|---|---|---|---|---|
| `Summary (GLJ)` TEC-12 block | 0.921 km² | 4.99 (N/G 0.118 of 42.3) | 0.07 | 0.30 | 1.19 | 1.19 MMbbl | 0.29 | 345,000 bbl | back-solved to hit 345,000 (G-18) |
| `Tecolutla Type Curve.xlsx!Volumetrics`, likely | 50 ha (r = 399 m) | 9 (N/G 0.6 of 15) | 0.06 | 0.20 | 1.299 | 1.05 MMbbl | 0.30 | 314 kbbl | Mar 2021 |
| same, low / high | 50 ha | 4.8 / 12 | 0.03 / 0.09 | 0.45 / 0.45 | 1.299 / 1.19 | 0.19 / 1.57 MMbbl | 0.18 / 0.45 | 35 / 706 kbbl | |

The task-6 production-based range (65 / 218 / 366 kbbl) sits inside the type-curve workbook's own low–high volumetric range and below its "likely" case, which assumes 9 m of net pay at 6 % porosity over 50 ha. Whether 9 m of net pay exists at the TEC-12 location is a task-9 question.

## 6. What to say in the handover

1. Quote both OOIP figures with their provenance: 7.8 MMbbl is PEMEX/CNH's booked volume; 11.2 MMbbl is IFR's with modern-log petrophysics. The independent Petrel Robertson model gives either, depending on which logs it is fed.
2. Use 8–10–12 MMbbl (P90–P50–P10) as the range and 10 MMbbl as the reference.
3. Remaining recoverable at trend-average recovery: about 0.9 MMbbl (0.3–1.6).
4. The lever is petrophysics, which is exactly what TEC-12's modern logs would measure. Frame the well as much as an appraisal of the 4 MMbbl of OOIP uncertainty as a producer.
