# 18 — Technical overview and question prep: Kinjal (John Tominey)

Companion deck: `docs/Tecolutla_Technical_Overview.pptx` (23 slides, built by `src/build_overview_deck.py`). Each slide's speaker notes carry the questions expected on that slide, with answers and sources.

Prepared for Kevin Gunning ahead of a technical presentation of Tecolutla to John Tominey (Kinjal, kinjalgas.com). This is a prep document, not a handout. Part C lists the weak spots John is likely to find, so do not send this file on as is.

**Who Kinjal is** (kinjalgas.com and its Newsfile releases, read 24 Oct 2026):
- Kinjal Corporation (Toronto; CEO Warren Levy, who was on the Jaguar side of the Sep 2022 Tecolutla review) is completing a reverse takeover of IFR.
- **3 Sep 2026:** Petro Frontera (IFR) signed a definitive agreement to buy Jaguar's 57.37 % of Tonalli. IFR already holds 42.63 %, so the resulting issuer would own 100 % of Tonalli and the Tecolutla block. The deal is subject to TSXV, shareholder and Mexican approvals, including SENER.
- **25 May 2026 release:** all Tonalli indebtedness is to be eliminated at closing, and a company-wide third-party reserve report covering Tecolutla is planned after closing.
- Kinjal's portfolio is gas-weighted: the Misión field (Burgos), the Kinkan discovery on block CS.06, and A10.CS (Macuspana farm-in).
- So John is likely assessing Tecolutla as an asset his company is about to own outright. Expect questions on reserves classification, the development plan and operating cost, more than on the sale itself.

Every number below comes from the repository or the Drive files it cites. Where your outline differs from the records, Part A says so.

---

## Part A — Your storyline, checked

### A1. Where it fits in the El Abra trend
- **Setting:** southeastern end of the Faja de Oro (Golden Lane) El Abra reef rim, on the margin of the Tuxpan platform atoll, in the Tampico–Misantla basin. It sits about 60 km ESE of Poza Rica, between the Miguel Hidalgo block (NW) and the Ignacio Allende block (SE).
- **Trap:** an NW–SE elongated anticline on the reef rim, with normal faults on both flanks parallel to the axis. Tertiary rocks (Tantoyuca, Upper Eocene) rest directly on the El Abra over the crest. Upper Cretaceous is eroded on the culmination; TEC-5 on the flank has 58 m of San Felipe.
- **Reservoir:** Middle Cretaceous El Abra reef-margin grainstone and packstone, recrystallised miliolid facies. Porosity runs from 2 to 11 %, and the TEC-10 core plugs measured 0.04–1.2 mD matrix permeability.
- **Flow:** productivity comes from fractures and vugs, not matrix. IHS fitted 18 mD to the TEC-10 2018 build-up.
- **Sources:** `data/processed/deck_notes/geology_geophysics_notes.md` §2, §10; `docs/03_tec11_facies.md`; TEC-10 core report (G-47 update).

### A2. Limited size
- **Area:** 2.5–3.1 km².
- **OOIP:** PEMEX/CNH booked volume 7.8 MMbbl; IFR's volumetric 11.2 MMbbl; probabilistic P90/P50/P10 8.1 / 10.0 / 12.2 MMbbl. That is 2.5 MMbbl/km², against a median of 8.3 for reef-rim fields.
- **Produced:** 1.98 MMbbl to end-2022 (1.72 MMbbl in the monthly record plus the PEMEX wellfile allocations), so about 20–25 % recovered.
- **Peak rate:** 932 bbl/d in March 1972.
- **Remaining recoverable:** 0.3–1.6 MMbbl, most likely about 0.9 MMbbl at trend-average recovery.
- **Sources:** `docs/07_volumetrics.md`, `data/processed/production_summary.json`.

### A3. Strong aquifer drive
This is the best-supported claim in the story. Pressures are corrected to 2,300 mSS:

| Year | Well | Pressure |
|---|---|---|
| 1956 | TEC-2 | 24.65 MPa |
| 1964 | TEC-2, TEC-7 | 24.36–24.66 MPa |
| 1998 | TEC-7 | 24.52 MPa |
| 2018 | TEC-2 | 24.14–24.16 MPa |

- About 0.5 MPa (70 psi) of depletion after roughly 1.9 MMbbl and 62 years.
- Both 2018 build-ups (TEC-2, TEC-10) needed a constant-pressure boundary, at 700 m and 195 m, to match late time. That is the aquifer showing up in the transient.
- **Sources:** `docs/05_pressure.md`, `figures/05_pressure_depletion.png`.

### A4. Vertical wells, perforating higher and higher
The records support this, with one exception you should name before John does: **TEC-9 never moved up.** Depths are mSS:

| Well | First interval | Later intervals |
|---|---|---|
| TEC-6 | 2,330–2,332 (1956–72) | 2,318–2,321 (1972–76), then 2,308–2,310 (1976–2006) |
| TEC-2 | 2,331–2,335 (1956–57) | shut in for salt water 1957–71; 2,303–2,307 (1972–2016) |
| TEC-7 | 2,330–2,332 (1957) | shut in for salt water 1957–71; 2,305–2,308 (1971–2006) |
| TEC-9 | 2,323–2,328 (1973–2012) | none; produced 353 kbbl from this one interval, deeper than everyone else's last interval |

- The PEMEX expedientes show the 1957–71 TEC-2/TEC-7 shut-ins were for "alto contenido de agua salada" (G-34 update).
- So the water did not rise as a flat plane. It coned or fingered around producers, probably along fractures. That actually helps the remaining-oil argument; say it that way.
- **Sources:** `docs/09_log_panel.md` §3; `data/processed/tecolutla_production_gaps_pemex.csv`; Tonalli to Jaguar, Sep 2022 (`1974i04rU2wMb73auSql8T3JiHZGznv_O`).

### A5. IFR/Tonalli programme, 2018–2019

**TEC-10DES (Apr–May 2018).** J-shape, cored and logged with a modern suite.
- Found producible oil at **2,314–2,318 mSS**, which is 7–11 m below the last producing intervals of TEC-2 (2,303–2,307) and TEC-7 (2,305–2,308). Your "oil deeper than last producing" point holds against those two wells.
- **Expect this pushback:** TEC-9 produced from 2,323–2,328 mSS until 2012. The finding is "the oil column is still there between the old producers", not "the oil is deeper than anyone produced".
- The lower zones A/B (2,394–2,442 mMD) were tight and did not flow.
- **Test history:** 182 bbl/d oil at 39 % water cut and about 880 psi flowing (Jul 2018); 131 bbl/d at 49 % (Sep 2018). First full month 181 bbl/d, peak daily test 232 bbl/d. 75.8 kbbl to Dec 2021, last rate 34 bbl/d at 86 % water cut, then shut in with "stim required during restart". Restarted Nov 2022 (678 bbl net in 15 days).
- **Sources:** Sep 2022 Jaguar deck; `docs/04_production_database.md`; `docs/13_cnh_filings_gis_cmi.md`.

**TEC-2 restart.**
- 2018 workover found paraffin in the tubing. The 7-day test made 50 bbl/d oil at 90 % water cut, then the well was shut in for lack of water disposal.
- Feb 2019: add-perf at 2,319–2,320 mKB. The repository had this wrongly at 2,019 m; corrected, G-59.
- May 2019: a permanent plug at 2,322.5 m shut off the wet deeper perforations. The 69-day test made 47 bbl/d oil at 75 % water cut and about 250 psi.
- 10.0 kbbl since 2018. Last reported rate 18 bbl/d at 72 % water cut (Sep 2020).
- **Sources:** `Activities performed in Tecolutla.xlsx` (`1PawcesNTey9NYEkRvJHdybIETY8vaTGQ`); Jaguar deck.

**TEC-7 test and conversion (Jun–Aug 2019).**
- Wellhead repair and acid job; the 2,305–2,308 mSS interval made 182 bbl/d water, 100 % water cut.
- Tonalli suspected bad cement or a leaking plug giving access to the lower perforations.
- Converted to produced-water disposal: triplex pump injection since 7 Aug 2019, under ASEA authorisation 1712/2019.
- **Source:** activities log; Jaguar deck; G-57.

**TEC-11DES horizontal (Nov–Dec 2018).** Intent as you describe: place a lateral in the top of the zone, open hole, low drawdown to delay water.
- **What the records say happened:** the 720 m lateral sat at 2,305–2,331 mSS, mostly 2,322–2,324, which is 4–12 m *below* the TEC-6/TEC-9 high. It ran through 923 m of mostly mudstone–wackestone.
- The operations log lists "wrong navigation", "well collapse (horizontal section)", "lack of logs" and "lack of pilot hole". The 4 1/2" tie-back and liner cementing failed, and the open-hole section could not be re-entered.
- Liner perforations at 2,674–2,745 mMD flowed 286 bbl/d water, 100 % water cut.
- A Tantoyuca recompletion made trace 17 °API oil and 96 bbl/d water. A composite plug was set at 2,400 m in Aug 2019.
- **How to tell it:** "the concept was tested by a well that missed the target." Do not present it as a test of the reservoir.
- **Source:** `docs/03_tec11_facies.md`; activities log; Jaguar deck.

**TEC-9 testing — no record found.**
- Nothing on the Drive or in the repository shows a Tonalli test of TEC-9. The 2018–2019 activities log, the Sep 2022 Jaguar deck and the CNH filings read do not mention one.
- The 2024 Work Program describes the TEC-9 wellhead as a safety and environmental hazard.
- If there was a test (a pressure survey, swab or wellhead check), find the date and the report before you cite it, or leave it out.

### A6. Operations
- **TEC-10 flowing:** confirmed. Flowing tubing pressure was about 880 psi in Jul 2018 and about 520 psi in Sep 2018.
- **TEC-2 cycling:** the rates above support on/off operation (tested, shut in, restarted). The day-by-day cycling pattern you describe is not documented in any file read, and per-well volumes after Nov 2019 are not separable (G-32). Describe it as operating practice, not as a data series.
- **TEC-7 disposal:** confirmed (above). The June 2019 job indicates roughly 700–1,400 bbl/d injectivity at under 450 psi, from a short test, not a sustained rate.
- **Solvent squeezes:** the log records six jobs in 2019 with **APSOL-AP "organic system"**, 2–3 m³ each, from Química Apollo or TPM.
  - TEC-10: 21 Jun, 13 Aug, 1 Nov and 23 Dec 2019.
  - TEC-2: 13 Aug and 23 Dec 2019.
  - The files name the product, not xylene. Check what APSOL-AP is before calling them xylene squeezes.
  - Jobs after 2019 are not in the files.
  - Paraffin is documented in TEC-2 (2018). The TEC-10 Zone C stock-tank oil has a −24 °C pour point and is 28.9 % C10–C20 and 16.7 % C20–C30, which is consistent with wax dropping out in cool tubing rather than a high-pour crude.
  - The relative-permeability benefit you mention is plausible, but nothing in the files measures it. Present it as an observation (oil cut improved for a period after jobs) only if the daily data show it.

### A7. TEC-12 — your "biggest remaining opportunity"
Your framing: TEC-12 at the peak of the reef, perforating the highest, under-exploited top of the zone. **This is where John will spend his time, and where the repository's own analysis is most cautious (G-47).** Bring both sides.

**Supports the case:**
- The location is on the crest, structurally 3–17 m above TEC-10, 175 m from TEC-10 and 118 m from TEC-9.
- Nothing in the field has ever been produced from 2,294–2,311 mSS except the top 4 m of TEC-2's interval. It is genuinely untested.
- TEC-10 found oil 7–11 m below the last TEC-2/TEC-7 intervals, so the water front is not a flat plane, and attic oil between and above the old producers is plausible.
- **TEC-9 (1973 logs):** on the sonic porosity, the window's water saturation is at parity with the interval that made 353 kbbl (window ÷ produced Sw 0.85–1.03 as logged).

**Argues against it:**
- **TEC-10 logs:** the window (2,294–2,311 mSS) has 9–11 % porosity but reads only 4–5 ohm·m, with neutron–density separation and PE 3.8. That is a clay-bearing or water-bearing response.
- **TEC-10 saturation sensitivity:** on the density porosity, which the core plugs support, the window is water-saturated in every case tested (Sw ≥ 1.1), against 0.6–1.0 in the perforated interval.
- The TEC-10 mud log over the window shows 70 % compact mudstone–wackestone, 30 % soft calcareous shale, 2–3 gas units and no show.
- PEMEX never perforated it in TEC-6 (bridge plug at 2,297 mSS instead), TEC-9 or TEC-2. Tonalli logged it at TEC-10 and chose not to perforate it.
- TEC-7 at 2,305–2,308 mSS tested 100 % water in 2019 (possibly via bad cement). TEC-11 at 2,305–2,331 mSS made 100 % water (but it was in tight mudstone with mechanical problems).
- **There was gas at the top in 1956.** TEC-2's first open-hole test (2,307.4–2,321.7 mKB) made 41 m³/d oil with 47,702 m³/d gas (GOR 1,163 m³/m³, about 6,500 scf/bbl). PEMEX's 1971 TEC-2 schematic marks a gas–oil level at 2,319 mKB (about 2,315 mSS). The neutron–density crossover in TEC-10 below 2,311 mSS is a light-hydrocarbon (gas) effect. **The very top of the structure may be or have been gas, not oil.**

**Suggested framing:**
- Present TEC-12 as an **appraisal-producer**: a full modern suite across 2,290–2,335 mSS (density–neutron–PE, resistivity, ideally dielectric or NMR), formation pressures and a fluid sample.
- Perforate on the data. The fallback is the 2,311–2,332 mSS interval that produced in every well.
- That turns John's hardest question into the well's stated objective.
- The repository has not run a separate economic case for the fallback alone. Say so if asked.

**Economics** (updated 25 Oct 2026). GLJ's 1 Oct 2026 price deck, costs +2 %/yr, 0.81 × WTI, NPV10 before tax, contract fiscal terms (`docs/10_econ_rebuild.md`):
- AFE USD 2.04 MM for an S-shape from the TEC-10 pad (USD 1.57 MM at Nov 2020 prices, PPI-indexed ×1.297).
- Base profile: 50 / 133 / 178 kbbl at 1 / 5 / 10 years, EUR 218 kbbl.
- **Incremental to a producing TEC-10:** NPV10 +0.47 MM (+0.11 after tax), payout 27 months, IRR 29 %; high profile +1.44, low −1.02.
- **Stand-alone:** −0.45 MM; high +0.33. It carries the area fiscal charges of USD 2.6 k/month.
- **Flat-WTI break-evens:** about 66 incremental and 83 stand-alone.

### A8. Commercial and regulatory
- **Sales:** trucked to PEMEX at CAB Poza Rica. Realised price 0.81 × WTI (volume-weighted 2020–22), with 2.7–3.3 USD/bbl fixed tariffs.
- **Fiscal:** 31.22 % bid royalty plus the basic royalty under licence contract CNH-R01-L03-A24/2016.
- **Regulatory status:** a Plan de Desarrollo has never been approved. The field produced under the evaluation period and the 2022 transition programme. The CNH's functions passed to the CNE in 2025; per secondary sources, pre-reform contracts keep their terms (G-49).
- **Gas:** flared under the evaluation-period approval.
- **Sources:** `docs/15_pemex_settlements.md`; `docs/01_econ_2023.md`; G-49.

### A9. Opex and logistics
The records support your point, and the trend is the evidence. All figures are field operating costs only; G&A and regulatory costs are separate. Sources: `data/processed/deck_notes/accounting_notes.md` §4 and Appendix A; `Tonalli Op Cost 290920.xlsx`; the 2019 activity table in the operations log.

| Period | Field opex | Per barrel | What drove it |
|---|---|---|---|
| Sep–Dec 2018 | USD 67–80 k/month (288 k total) | 18.7 USD/bbl | start-up; TEC-10 on test with rented Weatherford separator |
| 2019 | USD 54–83 k/month (839 k total) | 25.6 USD/bbl | two wells on test; water trucked out until Aug; separator rental MXN 216 k/month (about USD 10 k) |
| 2020 forecast (Jan 2020) | USD 461 k/year | 15.9 USD/bbl | after the 2019 changes below |
| Sep 2020 run-rate | **about USD 28 k/month** (about 338 k/year) | roughly 13–16 USD/bbl at 2020 volumes | crew MXN 280 k, vacuum truck MXN 108 k, diesel MXN 60 k, frac tank MXN 32 k, consumables, lab |

**What changed in 2019:**
- **TEC-7 converted to disposal (Aug 2019).** This ended trucking of produced water; the log calls it "opex reduction".
- **TEC-10 to TEC-2 flowline (Nov 2019).** It consolidated tankage and testing at one battery.
- **Own separator procured (Dec 2019)** for Q1-2020 install, replacing the rental, which was invoiced to Mar 2020.
- **TEC-2 shut in when uneconomic (Sep 2019),** with an USD 8 k demobilisation.

**Crude logistics:** trucked by contractor to PEMEX at CAB Poza Rica, with demulsifier treatment (Apollo, about USD 925/month). Monthly Intertek crude analyses support quality. PEMEX's fixed tariffs are 2.7–3.3 USD/bbl.

So field opex fell by about two-thirds, from about USD 70–80 k/month in mid-2019 to about 28 k/month by Sep 2020.

**Caveats John may raise:**
- The 2020–21 actuals are not in the files (G-56). The 28 k/month is a September 2020 cost sheet, not an audited figure.
- G&A was USD 674 k in 2019, and corporate administration was USD 39 k/month in the 2022 CNH report. All-in cost per barrel was much higher than field opex at 50–150 bbl/d.
- The 2023 economics assume 7.25 USD/bbl oil + 3.25 USD/bbl water + 2,500 USD/well/month + 10 k battery + 1.5 k disposal per month. At TEC-10's water cuts that sits close to the 2020 run-rate.

---

## Part B — Questions to expect, with short answers

### B1. Reservoir and geology
1. **What is the drive mechanism, and how do you know?** Aquifer. About 70 psi of depletion in 62 years, constant-pressure boundaries in both 2018 build-ups, and every well watered out (A3).
2. **Where is the OWC today?** There is no single number. Three are in circulation: "water at 2,350 m" (2017 plan); wet TEC-2 perforations at 2,331–2,345 mSS; GLJ's lowest known oil at −2,374 mSS used for OOIP. The producing record says oil-cut-bearing rock at 2,303–2,328 mSS and coning around wells.
3. **Is there a gas cap? Where is the GOC?** 1956 TEC-2 top test at GOR about 6,500 scf/bbl, and a PEMEX 1971 gas–oil level at about 2,315 mSS. The field GOR was 560 scf/bbl (1966–92 cumulative), 1,073 (1993–99) and 762 (TEC-10 test 2018). There is no PVT and no modern gas-cap mapping. *Honest answer: probably a small gas cap at the crest originally; current extent unknown.*
4. **Matrix or fracture flow?** Matrix 0.04–1.2 mD from core; 18 mD from the well test. Fractures and vugs carry the flow. The TEC-10 CMI image log shows 0–7 fractures per metre, but it has not been interpreted here (G-09).
5. **How good is the structure map?** PEMEX 2011 PSTM, reprocessed by Earth Signal in 2018, interpreted in Petrel. **We do not hold the SEG-Y, the Petrel project or the velocity model (G-55).** TEC-10 came in low against prognosis.
6. **OOIP range and recovery factor?** See A2. The reef-rim analogue median recovery is 31 % (3P EUR), against about 20–25 % to date.

### B2. Petrophysics and TEC-12
7. **Show me the logs over the TEC-12 window in TEC-10 and TEC-9.** `figures/09_log_panel.png` and `figures/15_sw_sensitivity.png`. Lead with the GR polarity: at Tecolutla, high GR marks porosity, so a standard GR cut-off discards the reservoir.
8. **Why didn't Tonalli perforate the upper zone in TEC-10?** Low resistivity and no mud-log show. The window was judged wet or poor. Answer it straight.
9. **What is Rw, and do you have core electrical properties?** Rw 0.054–0.075 ohm·m from the PEMEX 45,000 ppm water analysis. There are no m/n measurements and no 2018 water analysis in the files.
10. **What makes you think TEC-12 sees something different?** TEC-9's parity result, the crestal position, and the TEC-10 evidence that water moved by coning, not a flat rise. And TEC-12 will log and test before perforating.
11. **What is the downside case?** The window is wet or tight; complete in 2,311–2,332 mSS between producers. No separate case has been run; if the window adds nothing, the outcome leans toward the low profile (65 kbbl EUR), which is negative at every price tested.

### B3. Wells and operations
- **What does it cost to run the field?** See A9: field opex about USD 28 k/month by Sep 2020, down from 70–80 k in mid-2019, after in-field disposal, the flowline, the owned separator and the TEC-2 shut-in. Have the G&A number ready too.
12. **Why did TEC-11 fail?** See A5: navigation below target in mudstone, mechanical failures, no pilot hole or logs. A failed execution, not a negative reservoir test.
13. **What is TEC-10 doing now?** Last full data: 34 bbl/d at 86 % water cut (Dec 2021), shut in Feb 2022, restarted Nov 2022 on TEC-10 alone. Current status since then is not in the files.
14. **Water handling capacity?** TEC-7 disposal by triplex pump. Indicative injectivity about 700–1,400 bbl/d from a short 2019 test. Injected volumes and pressures since 2019 are not in the files (G-57).
15. **What about the solvent jobs?** See A6.
16. **Artificial lift?** None to date. TEC-10 flowed, and the 2023 economics carry a pump jack for TEC-12. With water cuts of 75–90 %, lift is likely needed later in life.
17. **Casing and wellbore integrity of the old wells?** Casing is known for all nine wells now (G-54 closed). TEC-2 and TEC-7 were accepted in 2017 without integrity tests. The TEC-9 wellhead is flagged as a hazard. TEC-11 has only a composite plug.

### B4. Fluids, gas and H2S
18. **Oil quality?** 26.5–31 °API, 1.6–1.9 % S; dead-oil viscosity 13.7–18.7 cSt at 40 °C; pour point −24 °C (TEC-10).
19. **PVT?** None measured (G-31). All PVT is correlation or a PEMEX analogue. A bottom-hole sample from TEC-12 should be on the programme.
20. **Gas composition and H2S?** Separator gas H2S 0.66–1.75 mol % across three analyses (the TEC-10 completion report states 17,500 ppm) and about 11 % CO2. Plan sour service and H2S safety. Gas is flared: about 0.9 MMcf in 15 days in Nov 2022, roughly 60 Mcf/d. There is no gas sales outlet.
21. **Gas monetisation?** Volumes are small, roughly 0.1–0.2 MMcf/d at field rates and GORs of 500–900 scf/bbl, and sour. Flaring was approved only for the evaluation period, so a gas-handling solution may be a condition of a Development Plan. *This is a likely topic if Kinjal is gas-focused.*

### B5. Commercial and regulatory
22. **Realised price and offtake terms?** See A8; PEMEX formula from the settlements.
23. **Government take?** 31.22 % bid royalty plus the basic royalty; there is a hydrocarbon surface tax; 30 % income tax. See `docs/01_econ_2023.md`.
24. **Contract status after the 2025 reform?** Pre-reform contracts reportedly keep their terms; the regulator is now the CNE; counsel to confirm (G-49).
25. **Abandonment liability?** USD 411 k reserve (four wells plus line, separator and dam) against a MXN 6.94 MM trust balance (2024–25).

---

## Part C — Weak spots to handle before or in the meeting
1. **TEC-12 window (G-47).** Lead with it rather than let John find it. See A7.
2. **TEC-9 "testing".** No record. Verify it or drop it.
3. **"Xylene" squeezes.** The records say APSOL-AP organic system. Check the product before naming it.
4. **TEC-2 cycling and post-2019 per-well data.** Not separable in the files (G-32). Say "field sales 2020–22, roughly 90 % TEC-10".
5. **No PVT and no seismic package in hand** (G-31, G-55).
6. **TEC-11** must be framed as an execution failure with its lessons: pilot hole, logs while drilling, geosteering.
7. **Data inconsistencies he may spot:**
   - TEC-10 top perforation is 2,314.3 mSS on the directional survey against 2,311.5 in the By Zone sheet and the Jaguar deck (G-46, survey adopted).
   - TEC-10 cumulative figures depend on the basis (daily file vs tickets vs Tonalli's 75.8 kbbl).
   - TEC-2 KB is 3.80 m (PEMEX 1971) against 4.00 m in the repository (G-58).

## Part D — What to have on hand
- **Figures:** `figures/18_wellbore_schematics.png`, `figures/19_well_histories.png`, `figures/05_pressure_depletion.png`, `figures/09_log_panel.png`, `figures/15_sw_sensitivity.png`, `figures/07_volumetrics.png`, `figures/10_econ_rebuild.png`.
- **Decks:** `docs/Tecolutla_Block_and_Development_History.pptx` (52 slides, full backup) and `docs/Tecolutla_TEC12_Handover.pptx` (13 slides).
- **Registers:** `docs/gaps.md` (open items) and `data/processed/wells/casing_strings.csv`.
