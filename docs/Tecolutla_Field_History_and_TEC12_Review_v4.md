# Tecolutla Field History Review & TEC-12 Opportunity Analysis

**Version:** 4 — rebuilt on the reconciled data in this repository (tasks 1–10). Version 3 is kept unchanged as `Tecolutla_Field_History_and_TEC12_Review.md`; every number below traces to a file, sheet and cell through the task notes in `docs/0*_*.md`, the processed tables in `data/processed/` and the gap register `docs/gaps.md` (G-01 to G-51).
**Prepared for:** the incoming operator's technical team. **Author of record:** Kevin Gunning, P.Eng. **Units:** depths in mMD or mSS as stated; volumes in bbl; money in USD unless labelled CAD; pressures in MPa at 2,300 mSS.

---

## 1. Executive summary

**What changed from version 3.** Nine of the ten open questions in v3 §8 are now closed on primary data, and two findings reverse the emphasis of the TEC-12 case:

1. **The 2.0 MMbbl field cumulative is 1.72 MMbbl recorded plus 0.43 MMbbl of PEMEX wellfile allocations** for 1956–1972 (task 4). The v3 per-well table simply omitted TEC-7 (267 kbbl); there was never a missing 0.33 MMbbl.
2. **Pressure has fallen 0.5 MPa (2 %) in 62 years**, from 24.65 MPa (24 May 1956, a 2 h 45 min reading) to 24.14–24.16 MPa in three wells in 2018 at 2,300 mSS (task 5). Expansion alone would have supported 11 kbbl; the aquifer replaced more than 99 % of voidage. "At original pressure" becomes "within 2 % of initial after ~2 MMbbl", which is the stronger statement because it is measurable.
3. **The 345 kbbl type curve embeds PEMEX-era recompletions.** The four wells it is fitted to were each re-perforated two or three times over 30–50 years. TEC-10, the only single-completion modern well, declines with b = 0.49 and points to ~100 kbbl. The recommended TEC-12 range is **65 / 218 / 366 kbbl (P90 / P50 / P10)** with a 180 bbl/d base (task 6). GLJ's YE2020 1P/2P/3P were 203 / 343 / 502 kbbl; Petrel Robertson's 100 bbl/d base and 200 bbl/d upside bracket the low and base.
4. **The TEC-12 target window (2,294–2,311 mSS) reads 4–5 ohm·m in both wells that have resistivity** (TEC-9 1973, TEC-10 2018), with neutron-density separation and a PE of 3.8 at TEC-10; a book-parameter Archie pass returns Sw ≈ 1. Resistivity rises to 15–50 ohm·m below ~2,310 mSS, and every barrel the field has produced came from 2,303–2,332 mSS (task 9). The window is either water-bearing or an argillaceous, poorer reservoir; the logs alone cannot say which. This is the decisive open item (G-47) and it was invisible in v3 because no one had hung the logs on one datum.
5. **The 11.2 vs 7.8 MMbbl OOIP difference is petrophysics, not geometry.** 7.8 is PEMEX's CNH-booked volume; 11.2 is IFR's with TEC-10 log parameters; the independent Petrel Robertson model gives 7.6 with TEC-2/9 vintage-log petrophysics and 12.0 with TEC-10's on the same rock volume. Monte Carlo on the source ranges: **8.1 / 10.0 / 12.2 MMbbl**; remaining at trend-average recovery about 0.9 (0.3–1.6) MMbbl (task 7).
6. **The AFE is USD 1,572,724, not 1,567,724**; the difference is a deleted formula in the September 2021 copy. It is priced on 2018 TEC-11 contract rates. Escalated to September 2026: USD 1.81 / 1.97 / 2.20 MM, CAD 2.52 / 2.74 / 3.06 MM at 1.3915 (task 8). The currency is USD by evidence, still to be confirmed by the author.
7. **Every IFR economic model since 2020 carries TEC-12 as a USD 1.55–1.8 MM horizontal re-entry of TEC-10**, not the S-shape new drill in the AFE and work program (task 2). The eleven models differ in price, price factor (0.95 → 0.801 → 0.90, unsourced), well count and window placement, never in the TEC-12 curve.
8. **Rebuilt single-well economics** (2023 fiscal and cost structure, base profile, escalated AFE, flat WTI): stand-alone NPV10 before tax is −0.09 MM at WTI 70 and +0.46 MM at 80; **incremental to a producing TEC-10** (battery and disposal already carried) it is +0.76 MM at 70 and +1.41 MM at 80, payout under two years. The low profile never pays out; the high profile pays out at WTI 60 (task 10). WTI is about USD 100 in mid-September 2026 on a supply disruption, against long-term decks of 70–80.

**The honest framing for the incoming team.** The field is a small, thin, strongly aquifer-supported El Abra accumulation whose wells are water-limited from their first year. TEC-12 is a sound well only as an incremental well on a producing pad, at a base rate about half of what the internal case assumed, and only if the target interval is shown to hold oil. The v3 conclusion that "the well economics were never the problem" survives for the incremental case at WTI ≥ 65; the v3 rate and volume assumptions do not. The cheapest high-value step remains the one v3 recommended: a long shut-in static gradient on TEC-10 (four years of build-up for free), now paired with a core-calibrated petrophysical evaluation of the TEC-10 upper zone.

---

## 2. Field history on reconciled data

### 2.1 Chronology (unchanged from v3 except dates now verified)

The economic-model file dates in v3 ("Sept 2023 — final work program, Petrel Robertson assessment and economics") are Drive copy dates. The nine "Feb 2022" models were saved between 11 April and 21 June 2022, in an order that runs backwards against their suffixes; the 2023 economics is stamped "Updated 2023-10-24" (G-08, G-20, G-21).

### 2.2 Production (task 4, `data/processed/tecolutla_production.parquet`)

| Well | Interval mMD (mSS) | Period | Oil, bbl | Basis |
|---|---|---|---|---|
| TEC-6 | 2336–2338 (2330–2332) | Oct 1956 – Feb 1972 | 509,993 | 122 kbbl monthly records; 388 kbbl PEMEX wellfile allocation |
| TEC-6 | 2324–2327 | Feb 1972 – Jan 1976 | 84,293 | CNH monthly |
| TEC-6 | 2314–2316 (2308–2310) | Mar 1976 – Dec 2006 | 305,499 | CNH monthly |
| TEC-9 | 2328–2333 (2323–2328) | May 1973 – Jul 2012 | 352,601 | CNH monthly |
| TEC-7 | 2310–2313 (2305–2308) | Oct 1971 – Dec 2006 | 266,988 | CNH monthly; 1957–68 no data |
| TEC-2 | 2335–2339 | 1956 – 1972 | 40,885 | wellfile allocation |
| TEC-2 | 2307–2311 (2303–2307) | Jan 1972 – Jan 2016; Jun 2019 – | 328,146 | CNH monthly to 2016 (2015–16 rows hand-entered); Tonalli |
| TEC-10 | 2349.5–2353 (2314–2318) | Jul 2018 – | ~48 kbbl to Mar 2020, ~80 kbbl to 2022 | daily sheet to Nov 2019; commingled sales after |
| **Field** | | | **1.72 MMbbl recorded; 1.94 MMbbl with allocations (Mar 2020); ~1.98 MMbbl to end-2022** | |

Field-level CNH data exist for 1960–65 (182 kbbl); nothing monthly exists before 1960 or for TEC-2 and TEC-7 before 1972 (G-30, G-34). After November 2019 no per-well volumes exist in the pulled files; the CNH annual filings give the field 16.1 kbbl net in 2020 (both wells, April–June shut in) and 17.4 kbbl in 2021 with TEC-10 named as the only origin, and the 2022 monthly reports show the field effectively shut in from July 2022 (238 bbl net in four months) (G-32, `docs/13_cnh_filings_gis_cmi.md`).

**GOR and fluid.** Cumulative produced GOR 1966–1992 was 565 scf/bbl, which is where IFR's "solution GOR 552" comes from, PEMEX measured 685 scf/bbl on TEC-6 in December 1964, and the TEC-10 flowback of Jul–Aug 2018 metered a median 767 scf/bbl (Weatherford daily reports, `docs/12_drive_large_files.md` §7); PEMEX's PVT table (336 scf/bbl, Pb 1,877 psi, 20 °API) does not describe this fluid. OCR of the Intertek 2018–19 reports gives the measured stock-tank oil as 30.1–30.8 °API, 1.6 % sulphur; no laboratory Rs or bubble point exists in the files (G-31). The anomalies are field-allocated gas in 24 months, a 1993–99 allocation artefact at low rates, TEC-2's 2013–16 tail (8 bbl/d oil against the field's gas), and a real but local rise on TEC-10 to 1,800–2,500 scf/bbl as tubing pressure fell below 500 psi. None indicates a gas cap or reservoir-wide gas liberation.

### 2.3 Reservoir, facies and volumetrics (tasks 7 and 9)

The GR trap in v3 is confirmed quantitatively: GR rises with porosity in every well (Spearman +0.28 to +0.49; `gr_polarity.csv`). Clean-GR intervals are the tight miliolid facies.

| OOIP source | MMbbl | Area km² | N/G | φ | Sw |
|---|---|---|---|---|---|
| CNH / PEMEX booked | 7.8 | 3.1 | — | — | — |
| Petrel Robertson, TEC-2/9/10 vintage-log petrophysics | 7.6 | 2.55 | 0.35 | 0.047 | 0.21 |
| IFR Summary (GLJ) sheet | 11.2 | 2.55 | 0.40 | 0.070 | 0.30 |
| CNH field polygon, 2015 data room (G-43) | — | 3.14 (all nine wells inside; administrative outline) | — | — | — |
| Petrel Robertson, TEC-10 logs | 12.0 | 2.55 | 0.42 | 0.062 | 0.19 |
| **Monte Carlo P90 / P50 / P10** | **8.1 / 10.0 / 12.2** | | | | |

Tecolutla holds 2.5 MMbbl/km² against a reef-rim median of 8.3. On the CNH volume it has recovered 25 %, the trend median (30 %) is close; on the P50 volume, 20 %. Remaining recoverable at 29 %: 0.3 MMbbl (CNH), 0.9 (P50), 1.3 (IFR).

### 2.4 Pressure and drive (task 5, `data/processed/pressure/tecolutla_pressures.csv`)

| Date | Well | Shut-in | p at 2,300 mSS, MPa |
|---|---|---|---|
| 24 May 1956 | TEC-2 | 2 h 45 min | 24.65 (PEMEX "initial", 252 kg/cm²) |
| Dec 1964 | TEC-2 / TEC-7 | 75–95 d | 24.36–24.66 |
| Aug–Oct 1971 | TEC-6 | 4 → 74 d | 23.24 → 24.35 (a 74-day build-up; short shut-ins understate by up to 1 MPa; all 16 PEMEX scans OCR-verified, one transcription error corrected) |
| Oct 1998 | TEC-7 | — | 24.52 |
| Mar–Aug 2018 | TEC-2 (SG), TEC-2 (build-up), TEC-10 (build-up) | 2 y, 13 d, 25 d | 24.16, 24.14, 24.15 (the TEC-2 build-up end, 3,441 psi at the 2,263 m gauge in the Weatherford report, reproduces IHS's 24.19 MPa at the perforations within 0.01 MPa) |

Both 2018 build-ups needed a constant-pressure boundary (TEC-2 at 700 m, TEC-10 at 195 m) to match late-time data; TEC-10 also needed a no-flow boundary at 125 m, consistent with the facies edge TEC-11 found. TEC-2's skin is +196 (a workover candidate); TEC-10's is +4.9 with kh/μ 519 mD·m/mPa·s over an assumed 13.2 m.

### 2.5 Type curve (task 6)

The IFR curve (qi 342, b 1.7, Di 3.5/yr; 401 kbbl over 417 months; "345 kbbl" is a pasted cumulative at an unrecorded cut-off) is unchanged in every model from August 2020 to October 2023. Re-fitting the four-well average gives b 1.34 and 315 kbbl, but the average rises again at months 100–130 and 250–300 as wells were re-perforated. TEC-10's own 15 months plus the 2020–22 sales fit qi 152 bbl/d, Di 0.79/yr, b 0.49, ~104 kbbl.

---

## 3. TEC-10 — the direct analogue, re-read

- Perforations 2,349.5–2,353 mMD = **2,314–2,318 mSS on the survey** (2,311.5 in the By Zone sheet; G-46). 2.5 m perforated in a 5–6 % porosity, 15–50 ohm·m interval.
- 181 bbl/d in the first full month, 78 bbl/d at 12 months, ~45 at 33 months, ~21 at 45 months; water cut 42 % → 67 % in year one; 44.5 kbbl in the first 431 days.
- The 41 m of 9–11 % porosity above the perforations (2,270–2,311 mSS) reads 4–5 ohm·m with neutron > density porosity and PE 3.8. The CMI sees no open fracture in it (3 mixed, 6 cemented picks over 17 m) and none in the perforated 10 m; open fractures start below 2,320 mSS, in the produced and water-bearing interval (`docs/13_cnh_filings_gis_cmi.md` §4). A 72-case saturation sensitivity anchored to the well's own aquifer and its own producing interval puts the window at Sw ≥ 1.1 on the core-supported density porosity while the perforations sit at 0.6–1.0; only if the neutron porosity is trusted in the tight zones does the window look as good as the perforations, and the neutron-density crossover flips sign exactly at 2,311 mSS. At TEC-9, 118 m from the TEC-12 location, the same test on the 1973 sonic gives the opposite: the window's 12.7 % porosity at 8.7 ohm·m is at parity with the 2,323–2,328 mSS interval that produced 353 kbbl, unless a fifth or more of that porosity is shale effect (`docs/14_sw_sensitivity.md`). Tonalli logged it with a modern suite and did not perforate it. The Weatherford image log is a CMI, not an FMI (G-09).
- GLJ's YE2020 forecast for TEC-10 (80 bbl/d through 2021) was overtaken within a year (G-39). GLJ's TEC-12 parameters are now read from the detail report: 200/225/275 bbl/d, b 0.5/0.6/0.7, EUR 250/400/600 kbbl, NPV10 2.2/4.1/6.0 MM at 42 $/bbl. The Work Program itself files 345,000 bbl as the vertical type-curve volume and 75 ac as the TEC-12 drainage polygon at the 2,315 mSS contour.

## 4. Modern drilling performance (unchanged from v3; costs verified)

TEC-11 actual USD 4.40 MM against a 3.93 MM budget (+12 %; drilling +8.8 %). The TEC-12 AFE uses the same day rates (rig 15,950/day, supervision 2,700/day) as the TEC-11 December 2018 tracker.

## 5. TEC-11 failure — quantified (task 3, `figures/03_tec11_lateral_facies.png`)

Carbonate section 923 m from 2,360 mMD (2,245 mSS); lateral (≥ 80°) 720 m at 2,305–2,331 mSS, mostly 2,322–2,324 mSS, i.e. 4–12 m **below** the TEC-6/9 highest perforations, not "roughly 2,311+". Of the 720 m: 419 m mudstone–wackestone, 240 m grainstone-bearing (all as "wackestone en parte grainstone" or "grainstone-wackestone", compact, partly recrystallised; no sample logged as pure grainstone), 31 m shale at 2,584–2,615 mMD, 30 m bentonite-dominant, with 30–40 % bentonite over the last 180 m to TD. Shows: 20 m moderate (2,920–2,945 mMD), 259 m poor, 125 m scarce, 519 m none. The v3 conclusion stands: facies, not depth. The v3 wording "intermittent miliolid grainstone" should read "wackestone to grainstone, compact" (G-27, G-28).

## 6. TEC-12 opportunity analysis

### 6.1 Concept and target

v3's premise, "un-perforated crestal El Abra pay that PEMEX logged", is where the new evidence bites. On the survey basis the target window (2,294–2,311 mSS) is about 20 m above TEC-10's top perforation. In TEC-10 that window has 16.5 m of φ ≥ 6 % and 0 m of Archie pay; in TEC-9 the same depths read 3–5 ohm·m; PEMEX set a bridge plug at 2,297 mSS in TEC-6 rather than perforate it. Two readings remain open (free water; or clay-bound water in an argillaceous carbonate with lower effective porosity). If the first holds, the target must move to the 2,311–2,332 mSS interval that has produced in every well and the argument becomes "between two producers in the same interval" rather than "higher on structure".

### 6.2 Well design (unchanged from v3)

S-shape from the TEC-10 pad, TD 2,370 mMD / 2,352.6 mTVD, max 15°, 1°/30 m; vertical through the El Abra. A CMI (or equivalent) and a full triple-combo with a proper Rw sample are the minimum logging programme, because the well's value as an appraisal of the OOIP uncertainty (4 MMbbl between the P90 and P10) is at least as large as its value as a producer.

### 6.3 Cost (task 8, `docs/08_afe.md`)

| | USD | CAD at 1.3915 |
|---|---|---|
| AFE as written, Nov 2020 pricing | 1,572,724 | 2,188,445 |
| Escalated low / **base** / high, Sep 2026 | 1,808,632 / **1,965,904** / 2,201,813 | 2,516,711 / **2,735,556** / 3,063,823 |

Composition: rig and move 27 %, tubulars and wellhead 23 %, mud and disposal 18 %. No contingency, no production casing, no owner's costs. Escalation factors are stated assumptions because no cost index could be downloaded (G-45).

### 6.4 Production forecast — resolved into a range

| | Low (P90) | **Base (P50)** | High (P10) |
|---|---|---|---|
| First month | 100 bbl/d | **180 bbl/d** | 300 bbl/d |
| Month 12 / 36 | 54 / 22 | **104 / 53** | 128 / 65 |
| EUR to 10 bbl/d | 65 kbbl | **218 kbbl** | 366 kbbl |
| Basis | TEC-10's decline at Petrel Robertson's rate | TEC-10 rate class, b 0.9 | PEMEX-average shape at the IFR rate |

Simmons' 390–799 kbbl "8-year sales" are TEC-12 plus TEC-13 (G-40) and the 2023 economics' 235 kbbl is the IFR curve at an economic limit; neither is a single-well EUR.

### 6.5 Economics — rebuilt (task 10, `data/processed/econ_rebuild/`, `figures/10_econ_rebuild.png`)

2023 IFR fiscal and cost structure (bid royalty 31.22 %, basic royalty B0 × price + 1.5 %, surface 1 %, hydrocarbon tax on 7.2 km², field price 90 % of WTI, opex 7.25 USD/bbl oil + 3.25 USD/bbl water + 2,500 USD/well/month, battery 10,000 and disposal 1,500 USD/month, 30 % tax, 25 % depreciation, 10 % discount), start January 2027, water cut following TEC-10 (40 % → 85 %), escalated base AFE, 100 % WI, no corporate G&A, no carry. NPV10 before tax, USD MM:

| WTI flat | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|
| Stand-alone, low profile | −1.77 | −1.57 | −1.36 | −1.15 | −0.94 | −0.73 |
| Stand-alone, **base** | −1.12 | −0.62 | **−0.09** | **0.46** | 1.00 | 1.54 |
| Stand-alone, high | −0.66 | 0.03 | 0.77 | 1.53 | 2.32 | 3.10 |
| Incremental to producing TEC-10, low | −1.41 | −1.14 | −0.88 | −0.63 | −0.39 | −0.16 |
| Incremental, **base** | −0.60 | 0.06 | **0.76** | **1.41** | 2.04 | 2.64 |
| Incremental, high | −0.08 | 0.85 | 1.81 | 2.72 | 3.59 | 4.42 |

Base case at WTI 70, stand-alone: 142 kbbl produced in 69 months before the fixed costs and 44 % royalty end it; payout 35 months. Incremental to a producing TEC-10: payout under two years at WTI 70. A 0.80 PEMEX price factor instead of 0.90 costs 0.4 MM. After-tax values are 0.3–0.5 MM lower.

The v3 overhead finding is unchanged: USD 1.05 MM/yr of corporate and regulatory cost consumed 97 % of the Simmons most-likely NOI. It is also now clear that the well-level case at the base profile only works as an add-on to an existing operation, which is the incoming operator's situation and not IFR's.

### 6.6 Risks (revised)

| Risk | Assessment |
|---|---|
| **Target interval water-bearing or argillaceous** (G-47) | High: at TEC-10 the window is water on the core-supported porosity under every anchor tested; at TEC-9 it is at parity with the producer on an uncorrected 1973 sonic and water with a 20–40 % shale correction (`docs/14_sw_sensitivity.md`). TEC-12 sits between the two wells and must log the window with a density-neutron pair and PE, and test it, before the completion is designed. The single item that can stop the well. The only core (TEC-10, 2,352–2,353 mMD, in the produced interval 17 m below the window) is a recrystallised grainstone at 2–8 % porosity and 0.01–0.5 mD at stress with 14–59 % PV residual oil and no electrical measurements; the mud log over the window at TEC-10 is 70 % compact mudstone-wackestone with 30 % shale and no show |
| Rate below base | TEC-10 itself started at 181 bbl/d and halved in a year; the low case never pays out |
| Facies | Low relative to TEC-11 (bracketed by TEC-6 and TEC-9), but the TEC-10 build-up needed a no-flow boundary at 125 m |
| Water | Every well water-limited within a year; the aquifer that holds pressure also delivers the water |
| Cost | AFE on 2018 rates, no contingency; 25 % escalation assumed |
| Price and fiscal | 44 % royalty burden at WTI 70; the March 2025 Ley del Sector Hidrocarburos leaves existing contract terms under the LISH per secondary sources, but its Reglamento allows substitution of contracts by assignments and the regulator is now the Comisión Nacional de Energía; counsel to confirm (G-49) |
| Depth control | TEC-10 came in low against prognosis; 3 m offset between survey and By Zone depths (G-46) |

## 7. Beyond TEC-12 (unchanged from v3)

TEC-2 skin +196 (workover), TEC-13 now structurally lower on the reprocessed 3D, the CNH 500 kbbl-per-well figure in the Decline sheet, which the filed forecast tables do not use: they carry the IFR 2020 curve for TEC-12 and TEC-13 (G-22 resolved).

## 8. Verification list — status

| v3 item | Status |
|---|---|
| 1 Reconcile OOIP 11.2 vs 7.8 | Done, task 7: petrophysics, not geometry; 8.1/10.0/12.2 |
| 2 TEC-11 mechanism | Done, task 3: metres by facies quantified |
| 3 Forecast basis | Done, task 6: 65/218/366 kbbl |
| 4 Economics rebuild | Done, task 10, on the 2023 structure; fiscal reform pending (G-49) |
| 5 AFE $5,000 and currency | Done, task 8 |
| 6 GLJ YE2020 | Included, task 6 |
| 7 Current reservoir pressure | Done, task 5: 24.15 MPa in 2018, 2 % below initial |
| 8 Static gradient at reopening | Still the highest-value cheap measurement; add the TEC-10 petrophysical evaluation |
| New | Resolve G-47 before sanction; confirm the AFE currency (G-44) and which well the 2023 model priced (G-17); pull the ten large-file binaries into `data/raw/` (G-52). 15 of 53 logged gaps remain open |

## 9. What the presentation says

Thirteen slides in `docs/Tecolutla_TEC12_Handover.pptx`: the reconciled field history; the eleven economic models on one basis; TEC-11 metres by facies; the production database; pressure at one datum; the type curve and the range; OOIP by source; the AFE; the log panel and the target window; the rebuilt economics; the second-pass sources (CNH polygon, CMI fractures, core, CNH filings); and the gap register.

## 10. Sources

Every file is listed with its SHA256 in `data/manifest.csv` (150 binaries plus 10 text renderings). The ten files above the connector's download limit, including the Work Program PDF and the GLJ YE2020 corporate summary detail, were read through the connector's text rendering (G-13 resolved, `docs/12_drive_large_files.md`); their figures and the two gauge-series workbooks beyond about 1 MB are still unread (G-52). Task notes: `docs/01_econ_2023.md` … `docs/09_log_panel.md`; gap register `docs/gaps.md`.
