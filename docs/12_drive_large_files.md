# 12. The ten large Drive files, read through the connector's text rendering

**Why this exists.** Gap G-13 recorded that the session's Drive connector refused raw downloads over about 7–10 MB, so ten files stayed unread and the task queue said "await API credentials". That was the wrong route: the files are shared with Kevin and the same connector's `read_file_content` call returns a text rendering of any size without downloading the binary. All ten were read on 15 Sep 2026 and the renderings are kept in `data/processed/drive_text/` (SHA256 in `data/manifest.csv`, `source_kind = drive-connector-text`). What the rendering does **not** carry: figures, maps, log images, embedded charts and, for the two gauge workbooks, anything past about 1 MB of text (G-52). The binaries are still not in `data/raw/`.

| Drive file | Size | Rendering | What it contains | Used for |
|---|---|---|---|---|
| `Tecolutla Work Program - Tec-12 Drill.pdf` (1FY4O…; Feb-2021 copy 1lICyY… byte-identical) | 14.5 MB | 15 KB, slide text | The IFR/Tonalli Tec-12 planning deck: merits, volumetrics table, Tec-9 status, un-perforated intervals, inter-well distances, well design, cost, pressure history table, El Abra analogue table, TEC-11 lessons | §1–§3 below |
| `YE 2020 Reserves (Tecolutla) - Corporate Summary Detail (Final).pdf` (14zn5S…) | 15.9 MB | 70 KB, full text | GLJ Ltd. evaluation effective 31 Dec 2020, 43 pages: reserves, volumetrics (Table 2.1), decline parameters (Table 2.2), economic parameters (Table 4), cash-flow forecasts by class | §4 |
| `Tecolutla10 ReporteFinal V603-18.pdf` (1OKibA…) | 7.7 MB | 58 KB, full text | Stratascan core report, TEC-10 core 1 (2,352–2,353 m, 1.30 m recovered): plug porosity/permeability at ambient, 500 and 3,400 psi, Dean-Stark saturations, thin sections, spectral GR | §5 (G-47) |
| `Litologia_Tecolutla_10.pdf` (1UTXD3…) | 7.3 MB | 93 KB, full text | Weatherford mud-log lithology report, 470–2,490 mMD, 2-m/5-m intervals with percentages, description, total gas, calcimetry | §6, `src/tec10_mudlog.py` |
| `Masterlog_Tecolutla 10_470 a 2490 m.pdf` (1duCrO…) | 7.0 MB | 3 KB, annotations | Header (KB 5.13, coordinates, casing, mud), drilling parameters, gas notes, core point | §6 |
| `201807 Tecolutla-10 Welltest Data.xlsx` (1xVMk3…) | 9.6 MB | 1.0 MB, truncated | Weatherford daily testing reports 29 Jun–6 Aug 2018, hourly rows: choke, WHP, gas rate, GOR, liquid, BSW, oil, cumulative, water, salinity | §7, `src/welltest_2018_extract.py` |
| `REPORT TECOLUTLA 2.xlsx` (1EdJ8t…) | 10.0 MB | 1.0 MB, truncated | Weatherford slickline report, TEC-2, 10–30 May 2018: operations log, 30-May static gradient stations, gauge series (only 10–12 May survives the truncation) | §8, `src/tec2_2018_survey.py` |
| `TECOLUTLA 10_CMI INTERPRETED IMAGE__2487.00m-2280.5m_02MAY2018.pdf` (12qxiA…) | 14.1 MB | 1 KB, track headers | Weatherford CMI interpreted image with dip classification (bedding, conductive/resistive fractures); the picks are graphical only | G-09 stays as is |
| `Tec 12.pptx` Sept 2021 (1Rt-cR…) | 8.1 MB | 2 KB | Well-design and TEC-11 lessons slides, identical text to the Work Program's design section; the budget tables are images | §3 |
| `Tec-12 Back-up Slides.pptx` Aug 2020 (1ayn5d…) | 14.5 MB | 0.4 KB | Maps: "Contour at 2315 mSS, Tec 12, 75.3 ac / 30.5 ha, based on known Tec-2 to Tec-7 distance of 456 m", PSDM 3D, Miguel Hidalgo spacing | §2 |

## 1. Work Program: what it says and what it settles

- **Type curve volume filed in the Work Program is 345,000 bbl** ("Vertical well type curve cumulative oil forecast is 345,000 bbl", data since 1960). The 500 kbbl "FOR CNH TRANSITION PLAN" block in the 2022 model `Decline` sheet is not in this deck; G-22 stays open only for what was filed with CNH.
- **Volumetrics table** is the IFR case already reconciled in task 7: 2.5 km², 42.3 m gross, N/G 40 %, 16.9 m net, φ 7 %, Sw 30 %, Bo 1.19, OOIP 1.8 e6 m³ = 11.2 MMbbl, "approximately 2 MMbbl recovered, 18 %", "1.2 MMbbl remaining at a conservative 29 %".
- **Pressure history table** is the same table as the IFR Pressure Summary transcribed in task 5, including the 9 Aug 1971 TEC-6 row at 24.3 MPa (248 kg/cm²) that the scan reads as 244.6 (G-51). The error therefore predates the summary workbook.
- **The TEC-12 claim in metres.** Un-perforated pay is stated as TEC-9 −2,296 to −2,311 mSS ("3 % – 11 % porosity", cuttings "cream miliolid grainstone" 2,308–2,329 mMD) and TEC-6 −2,294 to −2,307 mSS; TEC-6 top El Abra −2,294 mSS. "Top of prospective Tec-9 area (−2,296 mSS) is 16.5 metres higher than the top of the Tec-10 perfs" uses the 2,311.5 mSS By-Zone depth, not the survey depth (G-46). A log panel is labelled "Sw = 0.05 % Never Perforated" for TEC-6; the value is not reproducible from the vintage logs (task 9, G-48).
- **TEC-9 condition**: casing damaged 544–718 m during PEMEX milling, prospect interval cemented un-perforated, well returned to CNH/SENER; "not recommended to repair nor sidetrack (6-5/8" casing, cemented)".
- **Inter-well distances**: TEC-10 bottom-hole displacement 193.3 m (192.6 S, 16.6 E); TEC-9 117.9 m (117.2 N, 12.5 W); proposed TEC-12 174.6 m (171 E, 35 N) from the TEC-10 pad.
- **Well design and cost**: TD ~2,352 mTVD (2,370 mMD), 8½" hole to TD, 7" casing, 5" liner contingency, WBM 1.20–1.25 g/cc or invert, 14-day drill-and-complete target, "Total Cost: $1,500,000 … rough pricing based on 2018–2019 pricing". This is the 1.5 MM that persists in every economic model (task 2, G-26); the AFE's 1,572,724 (task 8) is the later line-item build.
- **Netback slides** are at WTI 42 and 50 with "Tec-12 @ 250 bbls/day", excluding Tonalli office G&A, HSE and regulatory cost (the v3 overhead point).
- **TEC-11 mechanism**, in Tonalli's own words: the selective-stimulation tool could not pass the damaged liner hanger, acid was bull-headed from surface, pressure broke down quickly, "acid likely entered a fracture and induced an overwhelming flow of water from the aquifer". Consistent with task 3.
- **El Abra analogue table**: 45 fields, 509 km², 6,126 MMbbl OOIP, 1,796 MMbbl 1P EUR, 29 % (Tecolutla row: 3.1 km², 7.8 MMbbl, 2.0 MMbbl, 25 %). Same table as `data/processed/volumetrics/` (task 7).

## 2. Aug 2020 back-up slides

Only one text fragment survives: the TEC-12 drainage polygon is drawn at the 2,315 mSS contour as 75.3 ac (30.5 ha) "based on known Tec-2 to Tec-7 distance of 456 m". That is the areal basis behind the 345 kbbl per-well claim (task 6): 75 ac × 16.9 m net × 7 % × 0.7 / 1.19 ≈ 1.6 MMbbl OOIP per drainage area, so 345 kbbl is a 21 % recovery of that polygon.

## 3. Sept 2021 `Tec 12.pptx`

The text is the Work Program's well-design section verbatim (TD 2,352 mTVD / 2,370 mMD, similar design to TEC-9, liner contingency, TEC-11 depth-time lessons). The September 2021 budget tables are images; the AFE workbook (task 8) is the numeric source.

## 4. GLJ YE2020 Corporate Summary Detail (effective 31 Dec 2020, run 26 Feb / 17 Mar 2021, US$)

Evaluators Hirschmiller, Virginillo, Olenick. Price deck GLJ (2021-01): Tecolutla oil at 88.4 % of Brent, 42.05 $/bbl in 2021 rising to 56.68 in 2029; transport 2.79 $/bbl; opex 1,400 $/well/month + 3.75 $/bbl variable + 276 M$/yr field fixed; abandonment 75 M$/well; royalty 7.5 % crown + 31.83 % non-crown (sliding). Capital: TEC-12 DIR 1,500 M$ (1,125 drill/complete + 375 tangible) in May 2021; TEC-13 HZ 2,400 M$ in May 2022.

| Item | Proved (1P) | Proved + probable (2P) | Proved + probable + possible (3P) |
|---|---|---|---|
| Area, acres | 401 | 515 | 630 |
| Porosity | 5 % | 6 % | 7 % |
| OOIP, Mbbl (N/G 0.40, Sw 30 %, Bo 1.19, LKO −2,374.2 mSS from TEC-3) | 5,441 | 8,302 | 11,164 |
| Ultimate RF, whole field | 35.5 % | 30.8 % | 27.4 % |
| TEC-12 decline: qi bbl/d, Di %/yr, b, final 3 bbl/d | 200, 36.6, 0.50 | 225, 31.4, 0.60 | 275, 30.5, 0.70 |
| TEC-12 EUR (Table 2.2), Mbbl | 250 | 400 | 600 |
| TEC-12 reserves at economic limit, Mbbl | 197 | 335 | 493 |
| TEC-12 NPV10 before tax, M$ | 2,213 | 4,057 | 5,953 |
| Property NPV10 before tax, M$ (incl. TEC-13 in 2P/3P) | 2,778 | 7,460 | 10,896 |
| TEC-10 remaining, Mbbl (b 0.4/0.5/0.6) | 167 | 242 | 342 |

Notes. (i) GLJ's low-case gross rock volume excludes everything north of TEC-11 "due to the poor results from the Tecolutla-11 well and the uncertainty to the source of the water"; only TEC-9 and TEC-10 were used for porosity. (ii) The 203/343/502 Mbbl quoted in `docs/06_forecast.md` are the monthly-profile sums in GLJ's export workbook (26 Feb run); the detail PDF's entity reserves are 197/335/493 (17 Mar run). Same forecast, 3 % apart on economic-limit treatment. (iii) GLJ's TEC-12 1P rate of 200 bbl/d with Di 37 %/yr and b 0.5 is close to this review's base case in shape (task 6: 180 bbl/d, b 0.9) but assigns 250 kbbl to it, versus 218 here, because of the flatter tail. (iv) The property-level 1P RF of 35.5 % on a 401-acre / 5 % porosity volume is the highest recovery in the analogue table; the 3P case is the IFR volume at 27 %.

## 5. TEC-10 core 1 (Stratascan V603-18): the only rock measurement in the field

Core 1 cut 2,352–2,353 mMD (about 2,317 mSS, inside the perforated interval 2,349.5–2,353 mMD), 1.30 m recovered, so fractured it could not be removed from the aluminium sleeve. Three horizontal plugs:

| Plug | Depth mMD | φ (He) ambient / 500 psi / 3,400 psi | k air, mD, ambient / 500 / 3,400 psi | k Klinkenberg at 3,400 psi | Grain density | Dean-Stark oil / water, % PV |
|---|---|---|---|---|---|---|
| N1H1 | 2,352.25 | 0.030 / 0.023 / 0.017 | – / 0.037 / 0.009 | 0.004 | 2.696 | 58.8 / 23.9 |
| N1H2 | 2,352.70 | 0.076 / 0.067 / 0.063 | – / 1.158 / 0.467 | 0.356 | 2.709 | 19.7 / 20.5 |
| N1H3 | 2,352.89 | 0.079 / 0.076 / 0.071 | – / 0.245 / 0.128 | 0.084 | 2.713 | 13.8 / 17.8 |

Petrography: benthic-foraminifera (miliolid, textulariid) and bioclast grainstone, strongly recrystallised, intercrystalline, mouldic and intrafossil porosity "good to fair", partial calcite fill, "with possible traces of oil" in hand specimen but "no hydrocarbons" in thin section; a 23-cm greenish-grey argillaceous wackestone-packstone in the middle with no visible porosity. Fit reported by the lab: k = 0.0036·e^(61.6·φ) at 3,400 psi.

What this settles for G-47: (a) the good rock in TEC-10 is a recrystallised grainstone with 6–8 % porosity and 0.1–0.5 mD at stress, not the 9–11 % log porosity at the TEC-12 window; (b) no electrical properties (m, n, Rw) were measured, so the Archie Sw ≈ 1 in the window cannot be checked against core; (c) the plugs kept 14–59 % oil in a water-based-mud flushed core at the produced depth, which is the only direct evidence of oil saturation in the field. The core is 17 m below the TEC-12 window; the window itself was never cored.

## 6. TEC-10 mud log (Weatherford), the El Abra section

`data/processed/tec10/tec10_mudlog_intervals.csv` (320 intervals). Casing 7" at 2,282.7 mMD; mud dropped from 1.36 to 1.05–1.15 g/cm³ for the reservoir section. Cuttings 2,288–2,320 mMD are 40–60 % soft grey calcareous shale, 20–40 % white-cream mudstone and mudstone-to-wackestone, 10–20 % sandstone; carbonate rises to 70 % at 2,320 and 100 % from 2,346 mMD. Total gas 1–3 units through the whole section (background 8 units in the Tantoyuca above); the only higher readings are 6.9 units at 2,362–2,365 and 12 units at 2,440–2,445 mMD. No oil show is recorded anywhere in the El Abra ("SIN ACEITE"/"POBRE" legend). In subsea terms (survey, KB 6.13 m): the TEC-12 window 2,294–2,311 mSS corresponds to about 2,329–2,346 mMD, which the mud log describes as 70 % compact mudstone-wackestone with 30 % soft calcareous shale and 2–3 units of gas. This is the lithological side of G-47: the window at TEC-10 is argillaceous mud-supported carbonate, and the log's neutron-density separation and PE 3.8 (task 9) are consistent with that rather than with a porous grainstone.

## 7. TEC-10 2018 well test (Weatherford daily reports)

`data/processed/welltest/tec10_welltest_2018_{hourly,daily}.csv`: 476 hourly rows, 348 flowing. Swabbing, acid (15 % HCl displaced with N₂) and clean-up occupy 29 Jun–22 Jul; the well flowed on a 12/64" choke from 23 Jul to 6 Aug 2018:

| Date | Oil bbl/d | Water bbl/d | BSW % | GOR scf/bbl (median) | WHP psig |
|---|---|---|---|---|---|
| 23 Jul | 41 | 337 | 89 | 1,008 | 328 |
| 27 Jul | 74 | 217 | 75 | 833 | 539 |
| 31 Jul | 104 | 197 | 66 | 809 | 595 |
| 4 Aug | 144 | 162 | 53 | 702 | 727 |
| 6 Aug (12 h) | 194 | 124 | 39 | 743 | 863 |

Cumulative 1,475 bbl, which is the "initial post-stim flow back yielded 1,475 bbl" of the Work Program. Measured GOR over the 15 flowing days: median 767 scf/bbl (P10–P90 597–942), oil-weighted 742, with residual N₂ from the displacement possible in the first days. This is a third field measurement above PEMEX's 336 scf/bbl PVT (G-31): 565 (1966–92 cumulative), 685 (TEC-6 1964 flowing survey), ~750 (TEC-10 2018). The API column of the form is blank on every sheet; the Intertek 30–31 °API (task 11) stands.

## 8. TEC-2 May 2018 slickline (Weatherford SL-424)

`data/processed/pressure/tec2_2018/`. Perforations 2,307–2,311 m, 2⅞" tubing, gauges 78446/79284. The report header gives initial 2,209.4 psi / 101.9 °C flowing (10 May) and final 3,440.98 psi / 99.6 °C (build-up end, 30 May) at the gauge. The operations log has the gauges fished from 2,263 m on 30 May and then stationed at 2,225 m for the static gradient. Stations (5-min stops, 25 m apart in the bottom hole): 3,355.1 psi at 2,225 m, gradient 0.1002 kg/cm²/m (9.83 kPa/m) over 2,150–2,225 m (oil), 0.040–0.050 kg/cm²/m gas-cut above 1,200 m, 0.009 above 800 m. The rendering keeps only 14,249 gauge lines (10–12 May flowing at 2,190–2,358 psi); the 20-day build-up series is lost to the truncation (G-52).

Cross-check of the IHS build-up used in task 5 (24,190 kPa at 2,309 mKB): the final gauge pressure 3,440.98 psi = 23,724 kPa at 2,263 mKB, plus 46 m × 9.83 kPa/m = 24,176 kPa at 2,309 mKB, within 14 kPa of IHS's "24,187 measured after 311 h". The 30-May static gradient extrapolates lower, 23,132 + 84 × 9.83 = 23,958 kPa at 2,309 mKB, 0.23 MPa below the build-up end, which is expected for a 10-minute station taken after the fishing run had disturbed the well. The dataset value stands; both readings are now in `tec2_2018/summary.json`.

## 9. Gaps touched

G-13 resolved (route found; binaries still not in `data/raw/`). G-22 narrowed (Work Program filed 345 kbbl). G-31, G-37, G-39, G-46, G-47 updated. New G-52 (rendering limits: figures and images not captured, gauge workbooks truncated at ~1 MB, well-test API column blank).
