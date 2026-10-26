# 19 — Tecolutla database review: file-by-file pass and what it changes

Date: 2026-10-25. Scope: every file in the IFR Team Folder `TECOLUTLA DATAROOM` (CNH Dataroom, Engineering, Geology, Geophysics, Reserves, Accounting, Regulatory, Presentations), plus the Tecolutla LAS and seismic files wherever they sit on the shared drive, and the YE2024–YE2025 reserve folders outside the dataroom. Read through the Google Drive connector on the gunninginc@gmail.com account. Per-file inventories, reviews and per-folder findings are in `data/processed/database_review/` (`<key>_inventory.csv`, `<key>_review.csv`, `<key>_findings.md`; `las_findings.md`, `seismic_inventory.csv`, `seismic_findings.md`). Nothing in `data/raw` was edited; new raw files have manifest rows.

## 1. Coverage

| Folder (key) | Files inventoried | Unique files reviewed | Not read, and why |
|---|---|---|---|
| CNH Dataroom (cnh) | 190 | 121 | 17 binary, 15 vector drawings/images unreadable, 16 photos skipped, 5 not read |
| Engineering (eng) | 35 | 26 | none (4 partial: truncated renderings) |
| Geology (geo) | 98 | 14 new (84 already covered) | 4 DLIS binaries, 1 TIFF, 1 PDF with no text layer |
| Geophysics (gph) | 5 | 5 | Petrel.zip and the PSDM ZGY are binaries (see §5) |
| Reserves (res), incl. YE2024–25 folders | 61 | 46 | none (4 GLJ reports partial: text stops before the end) |
| Accounting (acc) | 9 | 9 | none |
| Regulatory (reg) | 604 | 307 groups | 116 binary groups (shapefiles, CAD), 41 not read (MSDS, ID documents, superseded copies) |
| Presentations (pres) | 33 (2 in folder + related versions) | 6 | IFR Nov 2023 deck and its two versions unreadable (G-69) |
| LAS, drive-wide | 523 records → 115 unique | 106 on disk, parsed | 9 not downloadable (G-71) |
| Seismic, drive-wide | 74 | all classified | volumes too large for the connector (G-55) |

## 2. Findings that change the presentation, ranked

1. **The TEC-12 window has to be argued stratigraphically, with TEC-9 as the only analogue (G-47).** TEC-10's 2,294–2,311 mSS window is Tantoyuca on XRD (quartz 31 %, clay 9 %, calcite 50 %, dolomite ≤ 2 %); El Abra starts at 2,348 mMD (−2,312.9 mSS). IFR's own TEC-10 evaluation finds no pay above 2,314 mSS. TEC-101's logs show the same low-resistivity signature above a sharp El Abra top at −2,334. At TEC-9, the only well where El Abra is at window depth, the top 8 m of El Abra (2,296–2,304 mSS) has SPHI ~15 % and ILD ~8 ohm·m, and the 6 m below is tight. So the case is: TEC-12 reaches the top ~8 m of El Abra 14–20 m higher than TEC-10, in rock like TEC-9's top unit, which PEMEX cemented without ever perforating. The operator itself wrote in July 2019 that the FWL may have risen to ~2,316 mTVDss with a transition zone above. Drop "dolomitic" and "high GR = porosity" at TEC-10.
2. **The structure supports the location; the grid is well tied (figure 25).** The Jan 2019 Top El Abra grid ties all eight vertical-well tops within ±2.1 m. TEC-12's bottom hole maps at −2,289.4 mSS against the −2,296 prognosis (prognosis 6.6 m conservative), next to the southern high (~−2,285.7). A northern culmination at −2,284.4 mSS has no El Abra penetration: TEC-11 passed ~170 m from it while building, still above the mapped El Abra, and its lateral ran down the north-west plunge mostly 4–10 m above the grid top (G-75). The grid and the ZGY behind it are unverified until the seismic is opened. *Update 26 Oct (docs/20):* the seismic was opened. The PEMEX PSTM confirms TEC-12 on the southern crest (−2,293 mSS estimated) but not the northern culmination (30–60 m deeper); the DMI PSDM does not map the El Abra top (G-79).
3. **GLJ's booking for Kinjal is the number John will have, and it now reconciles (G-68, figure 24).** GLJ YE2025 for Kinjal Gas (report 25269, 100 %): 348 / 903 / 1,383 kbbl, NPV10 BT 2.87 / 8.11 / 12.11 MM USD, no producing reserves, TEC-12 in Jul 2028 at 1.9 MM capex, EUR 250 / 399 / 578 kbbl. GLJ's TEC-12 1P entity is 2.08 MM USD; our incremental base is 0.47 MM. The bridge rebuilds GLJ within 2 % (2.13 MM): deck −0.39, timing +0.04, capex +0.07, **costs +1.46** (GLJ 1,670 $/well-month and 5.85 $/bbl with no water charge, against our 2,500 $/well-month, 7.25 $/bbl oil and 3.25 $/bbl water at 40–85 % water cut), type well +0.49. The answer to "GLJ says 400, you say 218" is the TEC-10 analogue: GLJ still carries TEC-10 at 300 kbbl 2P against 77 kbbl produced.
4. **The field's commercial history: cumulative field netback ≈ 0 (G-56).** 2018–23 LOS: revenue 4.48 MM, royalties and fees 1.87 MM (41–56 % of revenue), opex 2.61 MM, before G&A and ~7.6 MM capital. Opex ran 24–29 k USD/month in 2020–21 (supports the logistics story), but 2023 care and maintenance averaged ~52 k/month with no breakdown (G-70), and 2024–25 holding costs were 289 k / 248 k USD with no sales.
5. **Area charges are higher than modelled (G-60).** As paid in 2024–25: FMP quota MXN 29,829/month plus IEEH USD 42.8 k/yr ≈ USD 5.2 k/month. Stand-alone TEC-12 NPV10 BT moves from −0.45 to −0.57 MM; the incremental case is unaffected.
6. **Regulatory items for the Kinjal deal (G-65, G-66, G-67).** Change of control needs CNH consent (cl. 23.2); base term to 2041-08-25 plus two conditional 5-year extensions; guarantee USD 1,764,100; 4,600 work-unit minimum (4,978 offered). GLJ says the wells were shut in early 2023 for an environmental permit, while IFR representation letters say all permits are in place. Flaring economics used GOR 337 scf/bbl against 742–859 measured, against a 98 % utilisation norm.
7. **PEMEX booked nothing proved: 1P 0.0 / 2P 0.0 / 3P 0.1 MMbbl at 1 Jan 2015** (CNH table; OOIP 7.8 MMbbl, cumulative 1.9 MMbbl). This is the pre-Tonalli baseline for any reserves-classification question. IFR's 2018 OOIP of 26 MMbbl (TM-01 deck) is the high end of the OOIP history (G-41).
8. **Cheap remedial upside is documented.** TEC-9 in 2012: solvent + 3 m³ 15 % HCl took it from 10 to 101.6 bopd, then 33–46 bopd for four months: near-wellbore damage, not depletion. TEC-2 1956 build-up gave 263–410 mD, against IHS's 50 mD with skin +196 in 2018.
9. **Contacts: five numbers, one tested.** Original FWL 2,380 mTVDss (2019 operator deck); PEMEX 1956 oil–salt-water ≈ −2,373 and GLJ LKO −2,374.2, both from the TEC-3 DST (980 m oil + 80 m salt water, ~24 °API); possible current FWL ~−2,316 (2019 deck); TEC-10 pick −2,402.8 (untested, base of zone A). Present them together (G-76).
10. **Well-record corrections.** TEC-101's chronology belonged to Cuesta Blanca-2 (G-61). TEC-9 produced to 2012 and was plugged 4 Jan 2013 (G-62). TEC-6 was abandoned in 2007 with casing parted at 352 m, beside the TEC-12 pad (G-63). TEC-3 surface shoe 601.7 m (G-54). TEC-11's final state: 4½" liner 1,869.18–2,863 mMD, fish 2,866–2,872, open hole 2,872–3,283, five water-invaded perforations 2,643.5–2,745.5 mMD. TEC-10 zone B was weak water inflow, not tight. All carried into `casing_strings.csv` and figure 18.

## 3. Corrections applied in the repository

| Item | Was | Now | Where |
|---|---|---|---|
| TEC-101 dates, objective | 15 Apr–31 Oct 1972, Jurassic objective | drilled 28 Jan–16 Mar 1972, plugged 31 Mar 1972 | deck notes (G-61) |
| TEC-9 status | closed Jan 1999 | produced 2003–12; plugged 4 Jan 2013; casing breaches | deck notes, casing register (G-62) |
| TEC-3 surface shoe | 501.35 m | 601.7 m; KB 5.78 | casing register (G-54) |
| TEC-6 | 1956 completion | 2007 abandonment, casing parted 352 m | casing register (G-63) |
| TEC-11 mechanical state | liner to TD; ten proposed perfs | liner to 2,863, fish, open hole, five perfs | casing register, deck |
| CNH missing months | unknown | reported zero months | G-34 closed |
| Stand-alone area charges | USD 2,638/month | USD 5,224/month as paid | `src/econ_rebuild.py` (G-60) |
| GLJ vs repository NPV | unexplained 4× gap | bridged within 2 % | `bridge.csv`, figure 24 (G-68) |
| "131 bbl/d at 49 %" | Sep 2018 | Jan 2019 | briefing (G-78) |
| TEC-12 window | 17 m depth band, "dolomitic" | top ~8 m of El Abra; Tantoyuca at TEC-10 | briefing, deck (G-47) |

## 4. Files to obtain natively (connector cannot read them)

- Seismic: `Tec_PSDM2019.zgy` (710 MB, `1qdKlGUK5l9hETyrwmcy1FSbZDwmrBf7I`), `Petrel.zip` (17 MB, `1cxtvuC5-2RkldobWZcCS4B2eN_blSKJy`), PEMEX PSTM cuts 554702/554703 (1.07 GB each); from Tonalli/Earth Signal/DMI: PSTM, gathers, angle stacks, velocity models, EBCDIC headers (G-55).
- LAS: `TEC-10 Logs.LAS`, TEC-11 GAM_SST, TEC-10 CXD and intermediate runs, TEC-6 2007 IDWD, two RAR archives; TEC-7 expediente zip (G-71, G-14).
- IFR November 2023 presentation, KPG version (G-69).
- Feb 2019 TEC-2 perforating ticket (G-59); PEMEX TEC-6 2007 abandonment report (G-63).
- 2023 opex breakdown (G-70); Workstrings invoice status (G-64); permit correspondence (G-65); CNH approvals and guarantee status (G-66).
- GLJ export workbooks with monthly profiles (YE2019, YE2022–25) and the RockWise XRD report PDF.

## 5. How the seismic was handled

The Drive holds about 2.85 GB of Tecolutla seismic (one PSDM ZGY, two legacy PSTM SEG-Y). These exceed the connector's download limit, so they were inventoried, not opened; `src/pull_drive.py` reads them once a service-account key is supplied in `GDRIVE_SA_JSON`. The Jan 2019 Top El Abra depth grid (88 KB) was ingested and mapped (`src/structure_map.py`, figure 25, `data/processed/seismic/`). The large `TC-SB` SEG-Y files on the Drive are Burgos blocks, not Tecolutla.
