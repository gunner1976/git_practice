# 18 — Technical overview and question prep: Kinjal (John Tominey)

Companion deck: `docs/Tecolutla_Technical_Overview.pptx` (built built by `src/build_overview_deck.py`). Each slide's speaker notes carry the questions expected on that slide, with answers and sources.

Prepared for Kevin Gunning ahead of a technical presentation of Tecolutla to John Tominey (Kinjal, kinjalgas.com). This is a prep document, not a handout. Part C lists the weak spots John is likely to find, so do not send this file on as is.

**Who Kinjal is** (kinjalgas.com and its Newsfile releases, read 24 Oct 2026):
- Kinjal Corporation (Toronto; CEO Warren Levy, who was on the Jaguar side of the Sep 2022 Tecolutla review) is completing a reverse takeover of IFR.
- **3 Sep 2026:** Petro Frontera (IFR) signed a definitive agreement to buy Jaguar's 57.37 % of Tonalli. IFR already holds 42.63 %, so the resulting issuer would own 100 % of Tonalli and the Tecolutla block. The deal is subject to TSXV, shareholder and Mexican approvals, including SENER.
- **25 May 2026 release:** all Tonalli indebtedness is to be eliminated at closing, and a company-wide third-party reserve report covering Tecolutla is planned after closing.
- Kinjal's portfolio is gas-weighted: the Misión field (Burgos), the Kinkan discovery on block CS.06, and A10.CS (Macuspana farm-in).
- So John is likely assessing Tecolutla as an asset his company is about to own outright. Expect questions on reserves classification, the development plan and operating cost, more than on the sale itself.

Every number below comes from the repository or the Drive files it cites. Where your outline differs from the records, Part A says so.

**Database review (25 Oct 2026).** Every file in the TECOLUTLA DATAROOM, plus all Tecolutla LAS and seismic on the Drive, has now been reviewed (`docs/19_database_review.md`). The changes it forces are folded in below and marked *(review)*.

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
- **OOIP:** PEMEX/CNH booked volume 7.8 MMbbl; IFR's 2018 pre-drill figure 26 MMbbl (TM-01 deck; it may surface) *(review)*; IFR's volumetric 11.2 MMbbl; probabilistic P90/P50/P10 8.1 / 10.0 / 12.2 MMbbl. That is 2.5 MMbbl/km², against a median of 8.3 for reef-rim fields.
- **Produced:** 1.98 MMbbl to end-2022 (1.72 MMbbl in the monthly record plus the PEMEX wellfile allocations), so about 20–25 % recovered.
- **Peak rate:** 932 bbl/d in March 1972.
- **Remaining recoverable:** 0.3–1.6 MMbbl, most likely about 0.9 MMbbl at trend-average recovery.
- **Official baseline:** PEMEX/CNH at 1 Jan 2015 booked **1P 0.0, 2P 0.0, 3P 0.1 MMbbl** (cumulative 1.9 MMbbl) *(review)*. GLJ YE2025 for Kinjal: 348 / 903 / 1,383 kbbl, all non-producing or undeveloped (B5).
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
- The lower zones: A (2,433–2,442 mMD) gave no inflow after acid; B (2,394.5–2,413.5 mMD) gave weak water inflow (16.9 m³ recovered, less than the 19.6 m³ injected), so it was not tight but not conclusive *(review)*.
- **Test history:** 182 bbl/d oil at 39 % water cut and about 880 psi flowing (Jul 2018); 131 bbl/d at 49 % (19–21 Jan 2019 in the daily data; the Jaguar deck labels it Sep 2018, when the average was 101 bbl/d at 63 % during clean-up, G-78). First full month 181 bbl/d, peak daily test 232 bbl/d. 75.8 kbbl to Dec 2021, last rate 34 bbl/d at 86 % water cut, then shut in with "stim required during restart". Restarted Nov 2022 (678 bbl net in 15 days).
- **Sources:** Sep 2022 Jaguar deck; `docs/04_production_database.md`; `docs/13_cnh_filings_gis_cmi.md`.

**TEC-2 restart.**
- 2018 workover found paraffin in the tubing. The 7-day test made 50 bbl/d oil at 90 % water cut, then the well was shut in for lack of water disposal.
- Feb 2019: add-perf at 2,319–2,320 mKB per the operations log (the repository had 2,019 m, G-59). *(review)* The May 2019 Tonalli schematic does not show this interval, so get the perforating ticket before it goes on a slide.
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
- Final state (Tonalli, 25 Sep 2019) *(review)*: 4½" liner from a tie-back at 1,869.18 to 2,863 mMD, a 5.9 m fish at 2,866–2,872, open hole 2,872–3,283. Five 3 m perforations at 2,643.5–2,745.5 mMD flowed 286 bbl/d water, 100 % water cut.
- The operator's July 2019 deck adds that TEC-11 was drilled at 320° to cut natural fractures predicted from TEC-10 and was acidised without isolation: "faults and fractures connect aquifer to oil column". On the Jan 2019 grid the lateral ran down the north-west plunge, mostly 4–10 m above the mapped El Abra top (G-75).
- A Tantoyuca recompletion made trace 17 °API oil and 96 bbl/d water. A composite plug was set at 2,400 m in Aug 2019.
- **How to tell it:** "the concept was tested by a well that missed the target." Do not present it as a test of the reservoir. Add the lesson the operator drew: the azimuth and an unisolated acid job targeted the aquifer conduits.
- **Source:** `docs/03_tec11_facies.md`; activities log; Jaguar deck.

**TEC-9 testing — no Tonalli record found.**
- *(review)* What the records do show is PEMEX's 2012 job: at 10–11 bopd, solvent + 3 m³ 15 % HCl lifted TEC-9 to 101.6 bopd, then 33–46 bopd for four months, before PEMEX squeezed it (Nov 2012) and plugged it (4 Jan 2013). If you meant this, cite it as PEMEX 2012.
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
- The location is on the crest, 175 m from TEC-10 and 118 m from TEC-9. *(review)* On the Jan 2019 depth grid, which ties all eight vertical-well tops within ±2.1 m, the bottom hole maps at −2,289.4 mSS, 6.6 m above the −2,296 prognosis and 20 m above TEC-10's El Abra top (`figures/25_el_abra_structure.png`).
- Nothing in the field has ever been produced from 2,294–2,311 mSS except the top 4 m of TEC-2's interval. It is genuinely untested.
- TEC-10 found oil 7–11 m below the last TEC-2/TEC-7 intervals, so the water front is not a flat plane, and attic oil between and above the old producers is plausible.
- **TEC-9 (1973 logs):** on the sonic porosity, the window's water saturation is at parity with the interval that made 353 kbbl (window ÷ produced Sw 0.85–1.03 as logged). *(review)* That parity rests on the top 8 m of El Abra (2,296–2,304 mSS: ILD 8, SPHI 15 %); the 6 m below is tight (SPHI 5 %). PEMEX cemented this interval without perforating it.
- *(review)* **TEC-10 never sampled the El Abra window.** XRD on the cuttings puts all of 2,294–2,311 mSS in the Tantoyuca (quartz 31 %, clay 9 %, calcite 50 %); El Abra starts at −2,312.9 mSS. The low resistivity there is a marl, and TEC-101 shows the same signature above its El Abra top. So the TEC-10 logs below are not evidence against TEC-12's target, which is the top ~8 m of El Abra where the reef is 14–20 m higher.

**Argues against it:**
- **TEC-10 logs:** the window (2,294–2,311 mSS) has 9–11 % porosity but reads only 4–5 ohm·m, with neutron–density separation and PE 3.8. *(review)* That is the Tantoyuca marl (dolomite ≤ 2 %, so not "dolomitic"); IFR's own evaluation finds no pay above 2,314 mSS.
- **TEC-10 saturation sensitivity:** on the density porosity, which the core plugs support, the window is water-saturated in every case tested (Sw ≥ 1.1), against 0.6–1.0 in the perforated interval.
- The TEC-10 mud log over the window shows 70 % compact mudstone–wackestone, 30 % soft calcareous shale, 2–3 gas units and no show.
- PEMEX never perforated it in TEC-6 (bridge plug at 2,297 mSS instead), TEC-9 or TEC-2. Tonalli logged it at TEC-10 and chose not to perforate it.
- TEC-7 at 2,305–2,308 mSS tested 100 % water in 2019 (possibly via bad cement). TEC-11 at 2,305–2,331 mSS made 100 % water (but it was in tight mudstone with mechanical problems).
- *(review)* The operator wrote in July 2019: "either the regional free water level has risen from 2,380 mTVDss to approx 2,316 mTVDss, with a transition zone above it, or the water is coming up through fractures". Under the first reading the window is in a transition zone.
- **There was gas at the top in 1956.** TEC-2's first open-hole test (2,307.4–2,321.7 mKB) made 41 m³/d oil with 47,702 m³/d gas (GOR 1,163 m³/m³, about 6,500 scf/bbl). PEMEX's 1971 TEC-2 schematic marks a gas–oil level at 2,319 mKB (about 2,315 mSS). The neutron–density crossover in TEC-10 below 2,311 mSS is a light-hydrocarbon (gas) effect. **The very top of the structure may be or have been gas, not oil.**

**Suggested framing:**
- Present TEC-12 as an **appraisal-producer**: a full modern suite across 2,290–2,335 mSS (density–neutron–PE, resistivity, ideally dielectric or NMR), formation pressures and a fluid sample.
- Perforate on the data. The fallback is the 2,311–2,332 mSS interval that produced in every well.
- That turns John's hardest question into the well's stated objective.
- The repository has not run a separate economic case for the fallback alone. Say so if asked.

**Economics** (updated 25 Oct 2026; area charges as paid, G-60). GLJ's 1 Oct 2026 price deck, costs +2 %/yr, 0.81 × WTI, NPV10 before tax, contract fiscal terms (`docs/10_econ_rebuild.md`):
- AFE USD 2.04 MM for an S-shape from the TEC-10 pad (USD 1.57 MM at Nov 2020 prices, PPI-indexed ×1.297).
- Base profile: 50 / 133 / 178 kbbl at 1 / 5 / 10 years, EUR 218 kbbl.
- **Incremental to a producing TEC-10:** NPV10 +0.47 MM (+0.11 after tax), payout 27 months, IRR 29 %; high profile +1.44, low −1.02.
- **Stand-alone:** −0.57 MM; high +0.20. It carries the area fiscal charges as paid in 2024–25, USD 5.2 k/month (FMP quota MXN 29,829 plus IEEH USD 42.8 k/yr).
- **Flat-WTI break-evens:** about 66 incremental and 86 stand-alone.
- **Against GLJ** *(review)*: GLJ's YE2025 TEC-12 1P entity is NPV10 BT 2.08 MM. `figures/24_glj_bridge.png` rebuilds it within 2 % from our case: deck −0.39, timing +0.04, capex +0.07, **costs +1.46** (GLJ has 1,670 $/well-month and 5.85 $/bbl and no water-handling charge), type well +0.49. If John asks why we are below GLJ: our costs include water at 40–85 % water cut, and our type well is calibrated on TEC-10.

### A8. Commercial and regulatory
- **Sales:** trucked to PEMEX at CAB Poza Rica. Realised price 0.81 × WTI (volume-weighted 2020–22), with 2.7–3.3 USD/bbl fixed tariffs.
- **Fiscal:** 31.22 % bid royalty plus the basic royalty under licence contract CNH-R01-L03-A24/2016.
- **Regulatory status:** a Plan de Desarrollo has never been approved. The field produced under the evaluation period and the 2022 transition programme. The CNH's functions passed to the CNE in 2025; per secondary sources, pre-reform contracts keep their terms (G-49).
- **Gas:** flared under the evaluation-period approval. *(review)* The 2017 plan justified flaring with a GOR of 337 scf/bbl against 742–859 measured, under a 98 % utilisation norm (G-67).
- *(review)* **Contract:** change of control needs CNH consent (cl. 23.2); term to 2041-08-25 plus two conditional 5-year extensions; guarantee USD 1,764,100; minimum work 4,600 units (4,978 offered). A Jan 2018 amendment moved the committed workover from TEC-2 to TEC-7 (G-66).
- *(review)* **Shut-in:** GLJ says TEC-2 and TEC-10 were shut in early 2023 for an environmental permit; the CNH filings give July 2022; IFR's representation letters say all permits are in place (G-65). Settle this with counsel before the meeting.
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

*(review)* **Actuals now in hand** (field LOS, `acc_findings.md`):

| Year | Sales bbl | Revenue | Royalties, taxes, fees | Field opex | Opex USD/bbl |
|---|---|---|---|---|---|
| 2018 (Sep–Dec) | 15,209 | 917 k | 382 k (42 %) | 291 k | 19.2 |
| 2019 | 32,702 | 1,732 k | 706 k (41 %) | 839 k | 25.7 |
| 2020 | 19,041 | 682 k | 283 k (42 %) | 336 k | 17.7 |
| 2021 | 17,546 | 939 k | 394 k (42 %) | 349 k | 19.9 |
| 2022 | 2,756 | 178 k | 89 k (50 %) | 168 k | 61 |
| 2023 | 530 | 30 k | 17 k (56 %) | 627 k | — |

- Jul–Nov 2020 ran 24.3–25.4 k/month and 2021 averaged 29.1 k/month, which confirms the logistics point.
- **Cumulative field netback 2018–23 is about zero** (revenue 4.48 MM, royalties and fees 1.87 MM, opex 2.61 MM), before G&A and ~7.6 MM of capital. John will compute this; say it first.
- 2023 care and maintenance averaged ~52 k/month with no breakdown (G-70); 2024–25 holding opex was 289 k and 248 k with no sales.

**Caveats John may raise:**
- The 28 k/month is a September 2020 cost sheet; the 2020–21 LOS actuals above confirm it (G-56).
- G&A was USD 674 k in 2019, and corporate administration was USD 39 k/month in the 2022 CNH report. All-in cost per barrel was much higher than field opex at 50–150 bbl/d.
- The 2023 economics assume 7.25 USD/bbl oil + 3.25 USD/bbl water + 2,500 USD/well/month + 10 k battery + 1.5 k disposal per month. At TEC-10's water cuts that sits close to the 2020 run-rate.

---

## Part B — Questions to expect, with short answers

### B1. Reservoir and geology
1. **What is the drive mechanism, and how do you know?** Aquifer. About 70 psi of depletion in 62 years, constant-pressure boundaries in both 2018 build-ups, and every well watered out (A3).
2. **Where is the OWC today?** There is no single number. *(review)* In circulation: original FWL 2,380 mTVDss (2019 operator deck); PEMEX 1956 oil–salt-water ≈ −2,373 and GLJ's lowest known oil −2,374.2, both from the TEC-3 DST (980 m of ~24 °API oil and 80 m of salt water); a possible current FWL ~−2,316 (2019 deck); an untested TEC-10 pick at −2,402.8; "water at 2,350 m" (2017 plan); wet TEC-2 perforations at 2,331–2,345 mSS (G-76). The producing record says oil-cut-bearing rock at 2,303–2,328 mSS and coning around wells.
3. **Is there a gas cap? Where is the GOC?** 1956 TEC-2 top test at GOR about 6,500 scf/bbl, and a PEMEX 1971 gas–oil level at about 2,315 mSS. The field GOR was 560 scf/bbl (1966–92 cumulative), 1,073 (1993–99) and 762 (TEC-10 test 2018). There is no PVT and no modern gas-cap mapping. *Honest answer: probably a small gas cap at the crest originally; current extent unknown.*
4. **Matrix or fracture flow?** Matrix 0.04–1.2 mD from core; 18 mD from the well test. Fractures and vugs carry the flow. The TEC-10 CMI image log shows 0–7 fractures per metre, but it has not been interpreted here (G-09).
5. **How good is the structure map?** PEMEX 3D, reprocessed by Earth Signal (PSTM, 2017–18) and DMI (PSDM, 2018), interpreted in Petrel. *(review)* The PSDM volume (710 MB ZGY) and the Petrel project are on the Drive but too large to open through the connector; the Earth Signal and DMI gathers, angle stacks and velocity models are not on the Drive (G-55). The Jan 2019 depth grid ties all vertical-well tops within ±2.1 m (`figures/25_el_abra_structure.png`). TEC-10 came in low against prognosis. AVO work in 2018 was judged inconclusive.
6. **OOIP range and recovery factor?** See A2. The reef-rim analogue median recovery is 31 % (3P EUR), against about 20–25 % to date.

### B2. Petrophysics and TEC-12
7. **Show me the logs over the TEC-12 window in TEC-10 and TEC-9.** `figures/09_log_panel.png` and `figures/15_sw_sensitivity.png`. *(review)* Lead with stratigraphy: at TEC-10 the window is Tantoyuca on XRD, so TEC-9 is the only log of El Abra at window depth. Within El Abra, high GR marks porosity at TEC-9 and TEC-2; at TEC-10 the published GR–porosity polarity is the Tantoyuca/El Abra contrast, so do not cite TEC-10 for it.
8. **Why didn't Tonalli perforate the upper zone in TEC-10?** Low resistivity and no mud-log show. *(review)* And it is not El Abra there: the XRD puts it in the Tantoyuca. Answer it straight.
9. **What is Rw, and do you have core electrical properties?** Rw 0.054–0.075 ohm·m from the PEMEX 45,000 ppm water analysis. There are no m/n measurements and no 2018 water analysis in the files.
10. **What makes you think TEC-12 sees something different?** TEC-12 reaches El Abra 14–20 m higher than TEC-10, where TEC-10 had no El Abra at all; TEC-9's top 8 m of El Abra is porous and at parity with its 353 kbbl producer; and water moved by coning, not a flat rise. TEC-12 will log and test before perforating.
11. **What is the downside case?** The window is wet or tight; complete in 2,311–2,332 mSS between producers. No separate case has been run; if the window adds nothing, the outcome leans toward the low profile (65 kbbl EUR), which is negative at every price tested.

### B3. Wells and operations
- **What does it cost to run the field?** See A9: field opex about USD 28 k/month by Sep 2020, down from 70–80 k in mid-2019, after in-field disposal, the flowline, the owned separator and the TEC-2 shut-in. Have the G&A number ready too.
12. **Why did TEC-11 fail?** See A5: navigation below target in mudstone, mechanical failures, no pilot hole or logs. A failed execution, not a negative reservoir test.
13. **What is TEC-10 doing now?** Last full data: 34 bbl/d at 86 % water cut (Dec 2021), shut in Feb 2022, restarted Nov 2022 on TEC-10 alone. *(review)* Last production Jan 2023 (GLJ); shut in since. GLJ YE2025 carries it as PDNP with a 15 k$ paraffin workover in Aug 2026.
14. **Water handling capacity?** TEC-7 disposal by triplex pump. Indicative injectivity about 700–1,400 bbl/d from a short 2019 test. Injected volumes and pressures since 2019 are not in the files (G-57).
15. **What about the solvent jobs?** See A6.
16. **Artificial lift?** None to date. TEC-10 flowed, and the 2023 economics carry a pump jack for TEC-12. With water cuts of 75–90 %, lift is likely needed later in life.
17. **Casing and wellbore integrity of the old wells?** Casing is known for all nine wells now (G-54 closed). TEC-2 and TEC-7 were accepted in 2017 without integrity tests. *(review)* TEC-6, beside the TEC-12 pad, was abandoned in 2007 with its 6 5/8" casing parted at 352 m (G-63). TEC-9 has breaches at ~70 m (repaired 2010) and 530–833 m and was plugged 4 Jan 2013; its wellhead is flagged as a hazard. TEC-11 has a composite plug at 2,400 m and a fish at 2,866–2,872 m.

### B4. Fluids, gas and H2S
18. **Oil quality?** 26.5–31 °API, 1.6–1.9 % S; dead-oil viscosity 13.7–18.7 cSt at 40 °C; pour point −24 °C (TEC-10).
19. **PVT?** None measured (G-31). All PVT is correlation or a PEMEX analogue. A bottom-hole sample from TEC-12 should be on the programme.
20. **Gas composition and H2S?** H2S was also present at TEC-9 in 2012 *(review)*. Separator gas H2S 0.66–1.75 mol % across three analyses (the TEC-10 completion report states 17,500 ppm) and about 11 % CO2. Plan sour service and H2S safety. Gas is flared: about 0.9 MMcf in 15 days in Nov 2022, roughly 60 Mcf/d. There is no gas sales outlet.
21. **Gas monetisation?** Volumes are small, roughly 0.1–0.2 MMcf/d at field rates and GORs of 500–900 scf/bbl, and sour. Flaring was approved only for the evaluation period, so a gas-handling solution may be a condition of a Development Plan. *This is a likely topic if Kinjal is gas-focused.*

### B5. Commercial and regulatory
22. **Realised price and offtake terms?** See A8; PEMEX formula from the settlements. *(review)* CNH net oil is a prorated balance of the CAB Poza Rica fiscal meter; field gauging only sets the daily split (G-53).
- **What are the reserves?** *(review)* GLJ YE2025 for Kinjal Gas (report 25269, 100 %): 348 / 903 / 1,383 kbbl, NPV10 BT 2.87 / 8.11 / 12.11 MM USD (Jan-2026 deck), no producing reserves; TEC-12 in Jul 2028, capex 1.9 MM, EUR 250 / 399 / 578 kbbl. GLJ's TEC-12 type well has not changed since YE2019. Our base EUR (218 kbbl) is below GLJ's 1P (250) because ours is calibrated on TEC-10, which GLJ still carries at 300 kbbl 2P after 77 kbbl produced.
23. **Government take?** 31.22 % bid royalty plus the basic royalty; there is a hydrocarbon surface tax; 30 % income tax. See `docs/01_econ_2023.md`.
24. **Contract status after the 2025 reform?** Pre-reform contracts reportedly keep their terms; the regulator is now the CNE; counsel to confirm (G-49).
25. **Abandonment liability?** USD 411 k reserve (four wells plus line, separator and dam) against a MXN 6.94 MM trust balance (2024–25).

---

## Part C — Weak spots to handle before or in the meeting
1. **TEC-12 window (G-47).** Lead with it rather than let John find it. See A7. The review turns it from "the window logs wet" into "only TEC-9 samples El Abra at that depth".
2. **TEC-9 "testing".** No record. Verify it or drop it.
3. **"Xylene" squeezes.** The records say APSOL-AP organic system. Check the product before naming it.
4. **TEC-2 cycling and post-2019 per-well data.** Not separable in the files (G-32). Say "field sales 2020–22, roughly 90 % TEC-10".
5. **No PVT, and the seismic volumes are located but not opened** (G-31, G-55).
8. **Commercial history** *(review)*: cumulative field netback ≈ 0 for 2018–23; 2023 care and maintenance ~52 k/month unexplained; ~0.96 MM of TEC-11 Workstrings invoices of unknown status (G-64).
9. **Regulatory** *(review)*: CNH consent to the change of control; shut-in cause and date vs representation letters; flaring basis (G-65 to G-67).
6. **TEC-11** must be framed as an execution failure with its lessons: pilot hole, logs while drilling, geosteering.
7. **Data inconsistencies he may spot:**
   - TEC-10 top perforation is 2,314.3 mSS on the directional survey against 2,311.5 in the By Zone sheet and the Jaguar deck (G-46, survey adopted).
   - TEC-10 cumulative figures depend on the basis (daily file vs tickets vs Tonalli's 75.8 kbbl).
   - TEC-2 KB is 3.80 m (PEMEX 1971) against 4.00 m in the repository (G-58).

## Part D — What to have on hand
- **Figures:** `figures/25_el_abra_structure.png`, `figures/24_glj_bridge.png`, `figures/18_wellbore_schematics.png`, `figures/19_well_histories.png`, `figures/05_pressure_depletion.png`, `figures/09_log_panel.png`, `figures/15_sw_sensitivity.png`, `figures/07_volumetrics.png`, `figures/10_econ_rebuild.png`.
- **Decks:** `docs/Tecolutla_Block_and_Development_History.pptx` (52 slides, full backup) and `docs/Tecolutla_TEC12_Handover.pptx` (13 slides).
- **Registers:** `docs/gaps.md` (open items), `docs/19_database_review.md` (database review) and `data/processed/wells/casing_strings.csv`.
