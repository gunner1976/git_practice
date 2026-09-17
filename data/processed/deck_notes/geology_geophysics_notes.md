# Geology and geophysics notes for the Tecolutla handover deck

Prepared 17 Sep 2026 from the repo sources listed in §0. Everything in §1–§8 is what the sources say, with the source key and page/slide/sheet in brackets. My own interpretation is confined to §9 "Reader's notes". Images extracted from the decks and the docx are in `data/processed/deck_notes/img/` (index in §10).

## 0. Source inventory and readability

| Key | File | What it is | Readable? |
|---|---|---|---|
| RES | `data/raw/appraisal_plan/6 -Resumen Campo Tecolutla.docx` | PEMEX/CNH Ronda 1 data-room field summary in Spanish, data at 1 Jan 2014, 10 sections, 7 tables, 12 figures | Text and tables fully extractable; figures exported (see §10) |
| PR | `data/raw/tec12_drill/Petrel Robertson Tec-12 Assessment.pdf` | 3-page geoscience + reservoir-engineering memo on the TEC-12 location (undated, after TEC-10 production start) | Full text. Its "Figure 2" (reprocessed seismic) is **not** in the PDF; the only embedded images are 2×2 px bullet glyphs |
| SEIS | `data/raw/tec12_drill/Tec 12 Seismic images.pptx` | 3 slides, one screenshot each, titles only | Titles extracted; 3 images exported |
| XS | `data/raw/petrophysics/XSections & Logs Eduardo Navarrete.pptx` | 16 slides: structure map, three log cross-sections in mSS, log inventory, per-well log panels with perforations, 2,315 mSS contour polygon | Titles/labels extracted; 12 unique images exported |
| TAN | `data/raw/petrophysics/Tantoyuca TEC-2,6,9.pptx` | 3 slides on the Tantoyuca/El Abra contact in TEC-2, TEC-6, TEC-9 | Text extracted; 3 images |
| T9SS | `data/raw/petrophysics/TEC-9 SS Logs.pptx` | 1 slide, TEC-9 logs in mSS with porosity annotations | Title only; 1 image |
| DEPTH | `data/raw/tec12_2020/ElAbra Depth Tec12.pptx` | 1 slide: Petrel top El Abra TVDSS depth map, 5 m contours, "Tec 12 BottomHole" label | Title extracted; map image exported from the zip (it is a picture fill, not a picture shape) |
| SSH | `data/raw/tec12_2020/TEC-12 Proposed S-Shaped Well Design.pptx` | 1 slide well sketch (casing depths only) | Text extracted; no geology |
| SINK | `data/raw/geology/tec10_image_log/Tec-10 Summary Modern day Image (sink hole).pptx` | 1 slide: satellite image of a sinkhole field + karst block diagram + text boxes | Text extracted; 2 images |
| ANA | `data/raw/appraisal_plan/El Abra Trend Field Analogies.xlsx` | one sheet `Sheet1`, 45 El Abra fields × 72 columns of CNH production/reserves data (to Apr 2015) | Fully readable. **No porosity, thickness, N/G or depth columns exist** |
| WP | `data/processed/drive_text/Tecolutla_Work_Program_Tec-12_Drill.pdf.txt` | Connector text of the 14.5 MB "Tecolutla Work Program – Tec 12 Well Planning" deck (Drive 1FY4O-cKf7cINcYyidWWQmVOeh4xOyfrR, modified 2023-09-29) | Slide text only; maps/logs/seismic not captured |
| BK20 / S21 | `Tec-12_Back-up_Slides_Aug2020.pptx.txt`, `Tec_12_Sept2021.pptx.txt` (same folder) | Text of two image-only decks | 2 and 4 lines of text respectively |
| T11ML | `data/raw/geology/Tec-11 DES Sample Descriptions/Tecolutla-11Des Columna Litologica 40-3283 MD.pdf` | Rise Energy mud log TEC-11DES, 20 pp, cuttings every 5 m | Full text. **Names no formation tops at all** (lithology only) |
| T10ML / T10LIT | `Masterlog_Tecolutla_10_470_a_2490m.pdf.txt`, `Litologia_Tecolutla_10.pdf.txt` | Weatherford masterlog header/annotations and 2-m lithology percentages for TEC-10 | Text; no formation names, one bracketed "El Abra top ~2310 m log-based" note added by the connector |
| T10CORE | `data/processed/drive_text/Tecolutla10_ReporteFinal_V603-18.pdf.txt` | Stratascan core-1 petrography and plug data, TEC-10 (also Drive 1OG5lzvlcG8_8V8hsF6H3bOggAFC_LOtn) | Text |
| PROG | `data/raw/tec12_regulatory/Programa de perforación Tecolutla 12.pdf` (73 pp, Sept 2020; VER1.1 copy in `ye2020_reserves/`, and `Tecolutla-12DES Perforacion.pdf` differs only in the water-cut assumption) | CNH drilling programme; §3–4 are the geological prognosis | Full text; figures 2–6 not captured |
| SEIS18 | Drive 14mWChMGdg-_80K4wkBs1OmHp7LtphyhE `Tecolutla 3D Seismic Interpretation Summary.docx` (Aug/Oct 2018) | Tonalli's own 3D interpretation write-up | Via `data/processed/deck_notes/drive_reads_notes.md` §Geology |
| T6FR / T5FR | Drive 1c2-WKxkltAM17-cCAZTe8pEoJcgwZwnr `TECOLUTLA_6_INFORME_FINAL.pdf`; 19i5buDsYV-_J_DWv5vN2Rg_tke7kuGpo `BLOQUE_TECOLUTLA_5_INFORME_FINAL.PDF` (PEMEX 1956) | Final well reports with tops and the first structural interpretation | Via `drive_reads_notes.md` |
| D03 / D07 / D13 | `docs/03_tec11_facies.md`, `docs/07_volumetrics.md`, `docs/13_cnh_filings_gis_cmi.md` | Repo notes already written | Reused |
| HDR | `data/raw/geology/Tecolutla Well header Information/Tecolutla Well Header Information.csv` | 9 wells: KB, TD, lat/lon, UTM | Read |
| CMI | `data/processed/drive_text/TECOLUTLA_10_CMI_INTERPRETED_IMAGE.pdf.txt` | Weatherford CMI image, 2,280.5–2,487 m | Track headers only; the image itself is not text |

Not readable / not present: PR "Figure 2"; the WP deck's maps, log panels and seismic sections (only text); PROG figures 2–6 (random-line seismic through TEC-6/TEC-12/TEC-9, structure map, correlation section, basin cross-section); the Petrel project and the Top El Abra TWT/depth XYZ surfaces named in SEIS18 are not in the repo.

## 1. Regional setting as the sources describe it

- **Location and basin.** Tecolutla municipality, ~60 km E-SE of Poza Rica, Veracruz; geologically in the Tampico–Misantla basin; PEMEX assignment AR-0463 (valid to 2016); classified as an oil and gas producer in Middle Cretaceous El Abra rocks; field extent 2.5 km² [RES §i, para 50].
- **Play.** "A small high within the reef atoll that borders the Tuxpan platform, called the Faja de Oro Terrestre" [RES §iii, para 76]. "The Tecolutla field belongs to the Faja de Oro, within the oil fields of the El Abra reef margin, in the Tampico basin" [PROG p13]. CNH classifies it as play El Abra / Reef Rim / Terrestre [ANA Sheet1 row "Tecolutla"].
- **Depositional model.** "Regionally the sedimentary model for the El Abra Formation is limestone developed on the edges of the Tuxpan platform atoll during the Middle Cretaceous. Deposited in shallow water in facies: pre-reef grainstone and packstone with bioclasts (reservoir rock) in a high-energy setting; reef facies wackestone to grainstone of bioclasts (good reservoir rock); post-reef mudstone to wackestone indicating low energy" [RES §iv, para 85; repeated almost verbatim in PROG p8 §3.1]. RES Figure iv.1 (exported, §10) annotates a seismic section with CUENCA – TALUD – PRE-ARRECIFE – ARRECIFE and a purple post-reef/lagoon zone at the crest where the wells are, over a facies cartoon (cuenca, talud, barrera arrecifal, post-arrecife, plataforma interna) with thin-section photos.
- **Age.** El Abra = "Cretácico Medio" throughout [RES paras 50, 76, 85; PROG p8]; the TEC-6 final report calls it Middle Cretaceous and the overlying Tantoyuca Upper Eocene [T6FR]. No source gives a stage name (Albian/Cenomanian).
- **What lies above and below (seismic-scale).** "El Abra ~800 m thick Cretaceous carbonate over Jurassic shales and faulted basement; overlain by Tertiary deltaics that onlap the El Abra; very high impedance contrast at top" [SEIS18]. RES Figure iii.1 (exported) labels, on the SW basin side, "K. Tamabra" and "J.S. San Andrés" horizons dipping under the platform edge, "K. Abra (Arrecifal)" as the reef block bounded by two red faults, and "Terciario" above on both sides.
- **Seal.** No source names a seal. What they do say: on the TEC-6 culmination "Tantoyuca (Upper Eocene) rests directly on El Abra (Middle Cretaceous): no Middle/Lower Eocene, no Upper Cretaceous on the culmination, by erosion (Faja de Oro oscillations)" [T6FR]; on the flank TEC-5 has 58 m of San Felipe and 55 m of Chicontepec Inferior between Tantoyuca and El Abra [T5FR]. Tantoyuca in the TEC-12 prognosis is "shales with traces of bentonite and sand layers" [PROG p8]. Agua Nueva and Méndez are not mentioned anywhere in the sources.
- **Source rock.** Not stated in any source. (SEIS18's "Jurassic shales" below the El Abra are a seismic-stratigraphic description, not a source-rock statement.)
- **Trap.** RES: "an elongated anticlinal structure oriented NW-SE, with normal faults on its western and eastern flanks parallel to the axis of the structure, produced by tensional stresses" [RES §iii, paras 76, 79]. PROG: "a four-way closed structure created by a process of deposition and erosion. The reef-margin accumulation created a structural high along the El Abra reef margin. Subsequent exposure and subaerial erosion created channels crossing the reef margin that separated the Faja de Oro reef margin into discrete groups" [PROG p13]. SEIS18: "clear build-ups and dip-closed highs coincident with Tecolutla and Miguel Hidalgo". The 1956 TEC-6 report already had "NW–SE high with axis between TEC-6 and TEC-2; TEC-3 (plugged, salt water) limits the NE flank; SW flank and NW/SE ends undefined" [T6FR].
- **Drive mechanism.** "Hydraulic drive" [RES para 86; PROG p8]; "the variation of reservoir pressure through time is minimal, indicating an active bottom aquifer" [RES para 124]; static pressures 254 kg/cm² initial (plotted 1964), ~251.5 (1971), 251 (1998) [RES Fig vi.3, exported]; "reservoir pressure is currently at original pressure from 1956 (24.7 MPa)" [WP, volumetrics slide]; GOR steady through each well's life, gas cap "possible but not observed" [PR p1–3].
- **Discovery and PEMEX history.** Discovered by exploration well Tecolutla-2 in 1956, completed 9 Jun 1956 in El Abra, 453 bpd, 28 °API [RES paras 51, 116]. Initial reservoir pressure 252 kg/cm² [RES para 117]. Field peak 932 bpd in Mar 1972; cumulative 1.9 MMbbl oil and 1.7 Bcf gas at 1 Jan 2014; ~9 bpd in 2014 [RES paras 52, 118]. PEMEX drilled seven wells 1956–1972 giving four producers; Tonalli drilled TEC-10 and TEC-11 (horizontal) in 2018 [WP p1]. Well status 2014 per PEMEX: 4 drilled, 1 producing, 1 closed, 2 plugged [RES Table ii.4] (this counts only the wells PEMEX still carried; the header file lists TEC-2, 3, 5, 6, 7, 9, 101, 10, 11 [HDR]). Gathering: Estación de recolección Vicente Guerrero (shared with Gutiérrez Zamora and Vicente Guerrero fields), trucked to Batería Ezequiel Ordóñez [RES para 52]. PEMEX 2014 volumes: OOIP 7.8 MMbbl and 8.8 Bcf for 1P/2P/3P; remaining 1P/2P 0.006 MMbbl, 3P 0.156 MMbbl; RF to date 24.35 % oil / 19.31 % gas, final 3P 26.35 % [RES Tables ii.1–ii.3]. TEC-5 (1956) was structurally low and plugged, El Abra 248 m lower than TEC-2, "marks the separation from Miguel Hidalgo" [T5FR]; TEC-3 plugged with salt water [T6FR]; TEC-101 is the example of karst-related early water [PR p1].

## 2. Stratigraphic column and formation tops

### 2.1 Combined formation-tops table

Depths as the source gives them. mSS = metres below sea level. KB/RT from the same source unless noted.

| Formation | TEC-5 mMD [T5FR] | TEC-6 mMD / mSS [T6FR] | TEC-12 prognosis mSS / mTVD / mMD [PROG p8] | TEC-2 | TEC-9 | TEC-10 | TEC-7 |
|---|---|---|---|---|---|---|---|
| Tuxpan (sands) | 40 | 40 | −32 / 40.2 / 40.2 | – | – | – | – |
| Escolín (shale) | 580 | 727 / 721 | −726 / 734.2 / 734.5 | – | – | – | – |
| Coatzintla (shale) | 1,160 | 1,121 / 1,115 | −1,117 / 1,125.2 / 1,136.7 | – | – | – | – |
| Palma Real Superior (shale) | 1,790 | 1,748 / 1,742 | −1,743 / 1,751.2 / 1,770.2 | – | – | – | – |
| Palma Real Inferior (shale) | 2,035 | 2,010 / 2,004 | −2,003 / 2,011.2 / 2,030.2 | – | – | – | – |
| Tantoyuca (Upper Eocene; shale, bentonite, sand) | 2,210 | 2,229 / 2,223 | −2,210 / 2,218.2 / 2,237.2 | – | – | – | – |
| Chicontepec Inferior | 2,427 | absent | – | – | – | – | – |
| San Felipe | 2,497 | absent | – | – | – | – | – |
| **El Abra (top)** | 2,555 (2,551 mSS; 5 m penetrated) | 2,302 / 2,296 (36 m penetrated) | −2,296 / 2,304.2 / 2,323.2 "Caliza kárstica arrecifal" | 2,300 mSS (2,304 mMD) [XS s10]; declared 2,307 mMD but cuttings/logs suggest 2,320 mMD / 2,316 mSS [TAN s2] | 2,296 mSS (2,310 mMD) [XS s13; WP] | 2,307 mSS (2,316 mMD) [XS s11]; "~2,310 m log-based" [T10ML] | ~2,304 mSS (read from XS s6 image; no number printed) |
| TD | 2,562.1 | 2,338.9 | −2,332.8 / 2,341 / 2,360 | 2,375 [HDR] | 2,340 mMD / 2,331.2 mTVD [PROG p67] | 2,490 [HDR] | 2,340 [HDR] |
| KB / RT | 4.00 (GL 0.30) | 5.67 (GL 2.19) | RT 3.70, terrain 4.5 msnm [PROG p7] | 4.00 [HDR] | 5.00 [HDR] | 5.13 [T10ML] / 6.13 [HDR] | 5.00 [HDR] |

Notes on the table (see also §10.5 for the TEC-9 estado mecánico tops and the GLJ 2019 map tops, added in the second pass):
- TEC-6 top El Abra is 2,296 mSS in the 1956 report but plotted at **2,294 mSS (2,300 mMD)** on the XS s12 log panel and stated as "the Tec-6 logs show top El Abra at −2294 mSS (2 meters shallower)" [WP appendix]. Both are in the files.
- TEC-2 has three different tops in the sources (2,304 mMD; 2,307 mMD declared; 2,316–2,320 mMD from cuttings). TAN s2: "Top of El Abra in TEC-2 seems to be (from cuttings and from logs) at 2320md/2316mSS, but was declared as 2307mD." TEC-2 cuttings 2,270–2,325 mMD are dark grey shale with sparse dense limestone and black flint; 2,326–2,340 mMD white/cream limestone with isolated oil stains [TAN s2].
- TEC-9 and TEC-10 are deviated (TEC-9 117.9 m displacement, back to vertical from 1,192 m [PROG p67]; TEC-10 193.3 m displacement [WP]), so mMD − KB ≠ mSS.
- **TEC-11**: the mud log names no formations. Lithology-based transitions from D03: first carbonate traces at 2,215 mMD; 5–30 % mudstone–wackestone from 2,340 mMD; carbonate becomes dominant at **2,360 mMD (2,245 mSS, 61° inclination)**; carbonate section 2,360–3,283 mMD; a grey-green bentonitic shale re-appears inside the carbonate at 2,584–2,615 mMD (2,309–2,313 mSS); last 180 m (3,103–3,283 mMD) 30–40 % bentonite. WP: TEC-11 at 2,615–2,625 mMD (2,308 mSS) "white and light grey semicompacted mudstone with pyrite; bentonitic shale; chert". Casing note: samples 2,360–2,391 mMD contaminated with cement/metal [D03 §5].
- **TEC-10** lithology by 2-m sample [T10LIT]: shale 60 % / mudstone 20 % / sandstone 20 % to 2,304 m; 40/40/20 from 2,304–2,314; 50/40/10 to 2,320; **70 % mudstone + 30 % shale from 2,320–2,322 m onward**; 7" casing set at 2,282.72 m and mud cut from 1.36 to 1.05–1.15 g/cm³ for the El Abra hole [T10ML]. The masterlog's 470–2,200 m section is "lutita arenosa gris claro, calcárea" with sandstone stringers (Tertiary clastics), connection gas 1,367–8,984 units at 1,850–2,080 m [T10ML].
- The RES gives no tops table; its stratigraphy is limited to "Cretácico Medio, Formación El Abra".

### 2.2 Cuttings and core descriptions of the El Abra, by well
- TEC-6 2,305–2,310 mMD (2,297–2,302 mSS): cryptocrystalline white and cream limestone with frequent miliolids [WP appendix].
- TEC-9 2,308–2,311 mMD (2,294–2,297 mSS): cream miliolid grainstone, sparse wackestone, mudstone; 2,313–2,329 mMD (2,299–2,315 mSS): cream miliolid grainstone, compacted mudstone [WP appendix]. Gas shows in TEC-9: three slight at 2,071, 2,194, 2,330 mMD and one strong at 2,340 mMD [PROG p67].
- TEC-2: micro log "producing from high gamma-ray porous and permeable limestone"; "clean gamma-ray thin-bedded lagoon with miliolids"; cuttings 2,326–2,340 mMD "possible tidal channel", 2,340–2,370 mMD microcoquina of cemented miliolids, "back reef to lagoon" [WP].
- TEC-10 2,345 mMD (2,311 mSS): white-cream compacted mudstone with brown wackestone, partly recrystallised, traces of soft calcareous shale [WP]. Masterlog 2,310–2,490 m: mudstone white-cream compact, mudstone-wackestone brown, in part recrystallised, sporadic green bentonite; formation gas at 2,422 m TG 5,172 ppm with C1–nC5 and CO2 2,197 ppm [T10ML].
- TEC-10 core 1 (28–30 Apr 2018, ~2,352 m, 1.0 m recovered; the report's "5352" is a typo for 2352): upper and lower parts grainstone of benthic forams (miliolids, textularids), bioclasts and rare rudists, strongly recrystallised, good intercrystalline microporosity, fair vuggy microporosity, scarce microfractures, "possible traces of oil"; middle 2,352.38–2,352.61 m greenish-grey argillaceous wackestone–packstone, no visible porosity, with rare planktonic Globotruncana. Five thin sections: dissolution partly sealed by calcite; porosity intercrystalline, mouldic, intrafossil; visual porosity 1–4 %, 0 % in the wackestone; **no hydrocarbons in any thin section**. Plugs: 2,352.25 m φ 2.3 % k 0.037 mD; 2,352.70 m φ 6.7 % k 1.158 mD; 2,352.83 m φ 7.6 % k 0.245 mD; grain density 2.696–2.713 g/cm³. Core could not be removed from the sleeve because of fracturing. Environment "plataforma externa" [T10CORE lines 127–149, 209–211, 1009; drive_reads_notes §Geology].

## 3. Structure

- **PEMEX depth map (2014).** RES Figure iii.2 (exported): top Middle Cretaceous El Abra depth map, UTM 705,600–709,600 E / 2,261,500–2,266,000 N, colour scale −2,300 to −2,700 m, 20 m contours. Reading the image: a NW–SE closed high with crest class −2,300 to −2,320 m around TEO-2, TEO-101, TEO-6, TEO-9, TEO-7; TEO-3 on the NE flank in the −2,400 to −2,420 class; TEO-5 far NW in the −2,500s; red fault bands NW–SE on both flanks plus NE–SW cross-faults; scale bar 1,250 m. Text: "anticlinal, elongated, NW-SE, normal faults on the western and eastern flanks parallel to the axis" [RES para 79].
- **Tonalli Petrel depth map (2020).** DEPTH slide "El Abra Depth TVDSS (contour interval 5 m)", 500 m scale bar, "Tec 12 BottomHole" label placed at lower right next to Tecolutla-9. Reading the image: contour labels 2,290 m on two culminations (one at Tecolutla-2, one at Tecolutla-6/-9), 2,300 m between them near Tecolutla-7/101; the TEC-10 survey track drawn from surface to bottom hole SSE of TEC-6; TEC-11 track not shown; deep blue (2,700+; label 2,765) to the NE and W; two closed circular lows (contour labels in the 2,44x–2,5xx range) between the field and a second orange/yellow high in the NW corner (labels 2,405–2,420). The programme says the 3D "identified an undrilled structure NW of Tecolutla-9 and NE of Tecolutla-6" and that TEC-12 "is programmed to find the top El Abra between −2296 and −2306 m TVDSS" [PROG p11]. "No large-scale faulting on the seismic at or near the TEC-12 location"; "TEC-13 now structurally lower compared to TEC-12 and TEC-10 on the revised structure map generated by the 3D reprocessing" [PR p1]. "The 3D seismic shows that the correlation between Tecolutla-6 and Tecolutla-9 is not interrupted by major faults or unconformities; no major stratigraphic changes between them or the other wells" [PROG p15 §4.7].
- **2,315 mSS contour / 75 ac polygon.** BK20 text: "Contour at 2315 mSS. Tec 12. 75.3 ac / 30.5 ha. Based on known Tec-2 to Tec-7 distance of 456 m. Tecolutla: Pre Stack Depth Migrated 3D. Miguel Hidalgo Well Spacing." XS s15 "Contour at 2315mSS": the same green contour map as XS s1 (wells Tecolutla-2, 101, 7, 6, 9, 10; contour labels "0" and "50" only, i.e. a relative/last-two-digit labelling) with a blue hand-drawn polygon enclosing TEC-2 at its N tip, TEC-7 on the E edge, TEC-9 inside, TEC-10 bottom hole and TEC-6 on the W edge, and a "Tec 12" square between TEC-6 and TEC-9. The 456 m TEC-2/TEC-7 distance is the scale check (the header coordinates give 456 m; §9).
- **Closure / contact statements.** No source states a spill point or a closure height. Related statements: PR volumetrics "deep contact −2,374 mSS" [D07 §1]; "the water contact seen at TEC-10" [PR p2–3]; PROG objective "define the oil-water contact under current conditions" [p7]; TEC-6 report recommended TEC-7 "drilled to the salt water to find the OWC" [T6FR]; TEC-3 found salt water on the NE flank [T6FR]; WP pressure table shows water levels rising in the TEC-6 wellbore from 1,722 m (1971) to 2,130 m during the 1971 build-ups and 2,045 m in TEC-7 (1964). GLJ areas 401/515/630 ac; CNH polygon 3.141 km² is administrative, not a mapped closure [D13 §3].
- **TEC-12 location rationale (as stated).** "Low-risk location directly offsetting the damaged Tec-9 well"; "interpreted to be in a structurally higher position to the perfs of Tec 10, Tec 6, Tec 9, Tec-7 and Tec-2"; un-perforated El Abra at the top of TEC-9 (−2,296 to −2,311 mSS, 2,310–2,325 mMD, 3–11 % porosity) and TEC-6 (−2,294 to −2,307 mSS); "top of prospective Tec-9 area (−2296 mSS) is 16.5 m higher than the top of the Tec-10 perfs" [WP]. PROG: "located structurally west of Tecolutla-9 and east of Tecolutla-6 … because three potentially productive intervals were not exploited in Tecolutla-9 nor the upper part of Tecolutla-6" [p10]. PR: "drilling between two Pemex wells with good evidence of undeveloped pay in upper reservoir zones"; depth-accuracy risk "mitigated by drilling TEC-12 as close to TEC-9 as possible" [p1]. TEC-12 target: El Abra at −2,296 mSS / 2,304.2 mTVD / 2,323.2 mMD, displacement 174.5 m at azimuth 78.433°, target UTM 707,753 E / 2,262,460 N, conductor 707,582 / 2,262,425 (WGS84) [PROG p7]; S-shape plan: vertical to 570 m, build 1°/30 m to 14° at 990 m, hold to 1,290 m, drop to vertical by 1,710 m, TD 2,370 mMD / 2,352.6 mTVD, final departure 175.2 m (35.1 N, 171.6 E) [SPLAN p1]. Casing 13⅜" 30 m, 9⅝" 500 m, 7" 2,350 m, 2⅞" tubing with packer at 2,200 m [SSH; BH].
- **Inter-well displacements (as stated).** TEC-10: 192.59 m S, 16.56 m E, total 193.3 m. TEC-9: 117.23 m N, 12.52 m W, total 117.9 m. Proposed TEC-12: 171 m E, 35 m N, total 174.55 m [WP "Inter-Well Distances"]. TEC-2 to TEC-7 456 m [BK20].
- **Dips from the TEC-10 CMI** [D13 §4, from the Weatherford dip LAS]: bedding dip median 20° above the window (2,264–2,295 mSS, 14 picks), 13° in the TEC-12 window (1 pick), 40° in the perforated 2,311–2,320 mSS (2 picks), 8° below 2,320 mSS (55 picks). Fracture dips 35° (window), 72° (2,320–2,362 mSS), 53° (deeper). Dipole-sonic anisotropy 0–2.5 %. The CMI PDF itself carries only track headers (static/dynamic conductivity images, dip classes bedding cross-/deformed/general, fracture conductive/mixed/resistive) [CMI].

## 4. Reservoir description

- **Lithology and porosity types.** "Reservoir quality is directly related to secondary porosity of vugs, dissolution caverns and karst type" [RES para 86; PROG p8]. "3 types of porosity in El Abra: intergranular, fractures, karst" [WP appendix]. "High porosity reef margin found in Tec-10 upper zone" [WP, Tec-10 testing slide]. PR: "reservoir quality somewhat variable and developed in layers; difficult to assess quantitatively on old (gamma-neutron) log control, but good pay zones can be identified with confidence"; "regional karsting on top of reef likely improves reservoir quality overall, but introduces risk of sinkhole topography and fracturing that could provide access to deeper aquifer zones, causing premature water production, e.g. TEC-101" [PR p1].
- **PEMEX petrophysics.** Carbonates with porosity 5–12 % and Sw 24–38 % [RES para 100]; Archie with Rw 0.075 ohm-m at 65 °C (45,000 ppm), m 1.8–2, n 2, a 1 [RES Table v.1]. TEC-2 tests: 2,307.4–2,321.7 m φ 10–12 %, Sw 35–40 %, 258 bpd + 1.7 MMcfd (RGA 1,163); 2,345–2,349 m φ 6–8 %, Sw 55–60 %, 352 bpd; 2,335–2,339 m φ 5–6 %, Sw 60–65 %, 453 bpd [RES Table vi.1]. IFR net pay 16.9 m over 42.3 m gross (N/G 40 %), φ 7 %, Sw 30 % [WP volumetrics]. PR/GLJ/CNH variants and the 8–10–12 MMbbl OOIP range are in D07 §1–2.
- **Sink-hole slide** [SINK]. One Google satellite image (imagery ©2018 DigitalGlobe, 20 m scale bar, credit line reads "Canada") captioned "Present Day Sinkholes-UK analogous to Tec-10", with a "40m" scale label, and a textbook karst block diagram (stream sinks, blind valley, sinkholes, seepage, fractures, caves, sump, spring) captioned "Karst Formation Process". Text boxes: "Tec-10 encountered a small sinkhole like this. Small sinkholes can not be imaged on seismic at this depth (sub-seismic)"; "Tec-10 avoided large sinkholes like this. Large sinkholes can be imaged on seismic at this depth"; "Tec-11 horizontal path will be able to drill through small sub-seismic sinkholes and back into El Abra Reservoir". No log or seismic evidence is shown on the slide.
- **CMI fracture evidence at TEC-10** [D13 §4]: no open (conductive) fractures in the 2,295–2,311 mSS TEC-12 window (3 mixed, 6 resistive), none in the perforated 2,311–2,320 mSS; open fractures concentrate below 2,320 mSS (6 conductive, 28 mixed in 2,320–2,362; 18 conductive in 2,362–2,446). TEC-10's production is read as matrix/sub-resolution vuggy flow (plugs 0.04–1.2 mD, skin +4.9).
- **TEC-11 facies** [D03]: 923 m of carbonate hole, 622 m mudstone–wackestone-dominant, 240 m with grainstone named but always as mixed "wackestone-grainstone"/"grainstone-wackestone", compact, partly recrystallised; no sample logged as pure grainstone; oil shows moderate over 20 m, poor 259 m, scarce 125 m, none 519 m; lateral at 2,305–2,331 mSS, 4–12 m below the TEC-6/TEC-9 upper perforations.
- **Per-well log panels and perforations in mSS** [XS s10–s13, s6; numbers printed on the panels]:

| Well | Top El Abra | Perforations mSS (mMD) | Date | Initial rate | Comment on panel |
|---|---|---|---|---|---|
| TEC-2 | 2,300 (2,304 mMD) | 2,303–2,307 (2,307–2,311) | Jan-72 | 42 m³/d | "still producing 15 % oil as of today" |
| | | 2,331–2,335 (2,335–2,339) | Jun-56 | 72 m³/d, 8 % water | closed Jan-72 at 45 m³/d, 80 % water; plug set, cement on top |
| | | 2,341–2,345 (2,345–2,349) | Jun-56 | 56 m³/d, 30 % water | closed after perf |
| TEC-6 | 2,294 (2,300 mMD) | 2,308–2,310 (2,314–2,316) | Mar-76 | 27 m³/d, 0 % water | 305,499 bbl Mar-76–Dec-06 |
| | | 2,318–2,321 (2,324–2,327) | Feb-72 | 42 m³/d, 2 % water | 84,293 bbl Feb-72–Jan-76 |
| | | 2,330–2,332 (2,336–2,338) | Oct-56 | 92 m³/d, 5.8 % water | 509,490 bbl Oct-56–Dec-71 |
| TEC-9 | 2,296 (2,310 mMD) | 2,314–2,319 (2,328–2,333) | May-73 | 30 m³/d, 0.6 % water | 352,601 bbl May-73–Jul-12; green "never perforated" flags 2,296–2,314 |
| TEC-10 | 2,307 (2,316 mMD) | 2,311.5–2,312.5 and 2,313.5–2,315 (2,320.5–2,324 mMD) | May-18 | 23.8 m³/d, 50 % water | "still producing 30 % oil"; orange line at 2,329 mSS |
| TEC-7 | ~2,304 (image) | ~2,305–2,308 and ~2,331–2,332 (image) | – | – | no text on slide |

- TEC-9 log annotations: "3–8 %" at ~2,296–2,301 mSS and "4–6 %" at ~2,302–2,306 mSS on the SPHI track; ILD jumps from ~2 to >50 ohm-m at the Tantoyuca/El Abra contact (~2,296–2,300 mSS) [T9SS; TAN s3]. TEC-6/TEC-9 comparison label "Sw = 0.05 % Never Perforated" [WP; YE20PPT s8] (as printed; almost certainly a mislabel, see §9).
- TEC-2 upper zone: "GR-Neutron behaviour in this zone seems better than the current production zone; would need to know resistivity"; top of liner 2,280 mSS, 7" shoe 2,303 mSS [TAN s1].
- **Log inventory** [XS s9, "Tecolutla Field Logs"]: GR in all of TEC-101, 2, 3, 5, 6, 9, 10, 11; neutron in 101, 2, 3, 6, 9, 10; sonic (SPHI) in 101, 2, 3, 9, 10, 11; SP in 101, 2, 3, 5, 9; resistivity in 101, 2, 3, 5, 9, 10; caliper 101, 2, 3, 5, 6, 10; microlog TEC-2 only; density, shear sonic and borehole image TEC-10 only; CBL TEC-6, 10, 11; cased-hole ultrasonic TEC-2. TEC-7 has no logs listed.
- **Net pay claims by source.** PR: "net pay should be approximately 15 m, as compared with the 3 m seen at TEC-10" if the un-perforated zone is as on offset logs [PR p3]. WP: 16.9 m field-average net pay (N/G 0.40 × 42.3 m) [WP]; TEC-9 un-perforated 15 m (2,296–2,311 mSS) at 3–11 % porosity; TEC-6 un-perforated 13 m (2,294–2,307 mSS). Type-curve workbook: 9 m likely (N/G 0.6 of 15 m), 4.8–12 m low–high [D07 §5]. GLJ TEC-12 block: 4.99 m net (N/G 0.118) back-solved [D07 §5]. PEMEX 2014: none stated.
- **Fluids (for completeness).** 28 °API, Pb 132 kg/cm², density 0.9365 at surface [RES para 103]; PVT proxy Ezequiel Ordóñez-41: 20 °API (as tabled), Bo 1.1923, RGA 59.9 m³/m³, viscosity 11.2 cp [RES Table v.2]; PROG expects 28.6 °API, 11.2 cP, GOR 2,041 scf/bbl, H2S 1.75 %, TEC-6 gas 79.8 % C1, 4.78 % CO2, 0.66 % H2S [PROG p9].

## 5. Seismic

- **Data that exists.** PEMEX cube "Furbero–Presidente Alemán–Remolino", acquired 2011, regular-to-good quality, PSTM [RES para 76]. "Pemex shot regional 3D in 2011/12; wasn't designed specifically to image shallow El Abra play" [PR p1]. "~150 km² legacy 3D provided at signing, covering the block plus area W and N incl. Miguel Hidalgo field. Reprocessed by Earth Signal (PSTM volume, gathers, angle stacks, velocity volume); Kirchhoff PSDM by DMI. Petrel project with PSTM, velocity cube, TEC-10 logs and well tie; Top El Abra TWT and depth surfaces exported as XYZ" [SEIS18]. "Tecolutla: Pre Stack Depth Migrated 3D" [BK20]. Quality "fair–good in/around El Abra and onlapping Tertiary; very poor NE of Tecolutla and above ~1 s" [SEIS18]. No 2D lines are named anywhere; no line/inline numbers are given for any displayed section; PROG figs 2–3 are "random line" sections through TEC-6, TEC-12 and TEC-9 (SE–NW) [PROG p10; `Tecolutla-12DES Perforacion.pdf` p10 says "Sección sísmica Random line"].
- **Well tie and picking.** "Well tie at MH-412 (nearest well with dipole sonic + density): Tantoyuca = peak, Top El Abra = trough-to-peak zero crossing; high confidence in El Abra continuity MH→Tecolutla. Picked every 10th line + autotrack in Petrel; depth from average velocity, bulk shift, minimum-curvature flex to well tops" [SEIS18]. RES Figure iii.1 (time section, 1,000–2,500 ms, SW–NE through Teo-101, Tecolutla-2, Teo-3) annotates the top El Abra at "2270 m" at Tecolutla-2 and "2800 m" on the downthrown NE side.
- **Depth conversion / velocity statements.** Only the SEIS18 sentence above and the PR statements: "TEC 10 came in lower than the drilling prognosis for the reservoir. Seismic data now reprocessed and depth migrated to correct depth imaging issues"; "calibrating top reservoir depths will still have some inaccuracies as tuning of 3D dataset frequencies still an issue" [PR p1]. No velocity values, no time–depth pairs, no checkshot/VSP are in any source. (`Tec-12 Time vs Depth.pdf` is a drilling days-vs-depth curve, not seismic.)
- **Amplitude / attribute claims.** "Very high impedance contrast at top" El Abra [SEIS18]. Nothing else: no attribute maps, AVO, inversion or angle-stack products are described, although SEIS18 says gathers and angle stacks were delivered.
- **Karst and faults on seismic.** "No significant karsting signature, like that encountered in TEC-101, evident on seismic at or near the TEC-12 well"; "no evidence of large scale faulting on the seismic at or near the TEC-12 location" [PR p1]; small sinkholes "sub-seismic", large ones "can be imaged at this depth" [SINK].
- **What the `Tec 12 Seismic images.pptx` shows** (three Petrel screenshots, red/blue amplitude, no scale bars, no line numbers, no depth/time annotations; exported to img/):
  - s1 "Tec 10 Surface to Tec 9 Seismic and Top El Abra Depth Surface": 3D view of a vertical section (green and magenta well tracks, a third white vertical track to the right) hung over the coloured top-El-Abra depth surface; the green horizon pick sits on a strong band of reflectors at the base of the section and the surface is red (high) under the tracks, with contour labels 1800/1850 visible on the surface to the right (so the surface display is not in the same units as the 2,29x mSS map, or is a different surface; unresolved).
  - s2 "Tec 10, 9, 7, 2 Traverse": a 2D traverse with four well tracks (green deviated, magenta, white, yellow); green top-El-Abra pick on a strong continuous reflector, gently domed between the tracks, dropping steeply at the left (SW/W) end; a shallower strong reflector package ~40 % up the section. Layered, continuous reflectivity above and within the pick, no obvious fault breaks.
  - s3 "Tec 9 Bottom Hole, Tec 10 Surface to Tec 6": section with a purple vertical track and short green/pink tracks; green pick on a strong reflector forming a low-relief anticline centred on the purple track.
- **What is NOT available in the repo.** The seismic volumes, the Petrel project, the TWT/depth grids (XYZ), the velocity cube, the reprocessing reports, PR's Figure 2, the PROG random lines and structure figure, the WP appendix "Seismic Sections" and "3D Seismic View", any survey geometry (bin size, fold, frequency content), and any well-tie display at Tecolutla itself (the tie was at Miguel Hidalgo MH-412).

## 6. Analogue fields table (CNH data to April 2015)

Source: ANA `Sheet1` (header row 2; `Oil Curr RF` = produced/OOIP; EUR RF = (produced + reserves)/OOIP). Only these columns exist for rock/volume: area, OOIP, production, reserves, API, max rate. **No porosity, thickness, net pay, depth or OOIP/km² inputs are in the workbook** (the `Oil (Vo MMbbl/km²)` column is OOIP/area). The WP slide "El Abra Trend: Analogous Field Recovery Factors" is a reduced copy of this table.

| Field | Play2 | Setting | Area km² | OOIP MMbbl | Prod MMbbl | RF now % | 1P EUR MMbbl | 1P/2P/3P EUR RF % | API | Max rate kbbl/d |
|---|---|---|---|---|---|---|---|---|---|---|
| Aguacate | Reef Interior | Terrestre | 21.3 | 30.9 | 5.9 | 19.0 | 6.2 | 20.1/21.5/29.9 | 15 | 4.02 |
| Chiconcoa | Reef Interior | Terrestre | 1.5 | 0.6 | 0.1 | 18.4 | 0.1 | 20.7/20.7/20.7 | 17 | 0.03 |
| Copal | Reef Interior | Terrestre | 4.1 | 11.0 | 4.1 | 37.3 | 4.2 | 37.9/37.9/37.9 | 22 | 1.03 |
| Frijolillo | Reef Interior | Terrestre | 3.1 | 0.4 | 0.04 | 9.6 | 0.04 | 9.6/9.6/9.6 | 25.5 | 0.52 |
| Muro | Reef Interior | Terrestre | 5.1 | 73.9 | 23.0 | 31.2 | 23.2 | 31.4/31.4/31.9 | 17 | 5.85 |
| Solís Tierra Amarilla | Reef Interior | Terrestre | 31.3 | 83.3 | 13.5 | 16.2 | 13.7 | 16.4/16.4/17.3 | 18 | 1.27 |
| Sur Amatlán | Reef Interior | Terrestre | 1.9 | 451.5 | 135.6 | 30.0 | 137.4 | 30.4/30.4/30.5 | 19 | 1.44 |
| Tamiahua | Reef Interior | Terrestre | 41.4 | 7.6 | 0.2 | 3.2 | 0.2 | 3.2/3.2/3.2 | 26 | 0.18 |
| Temapache | Reef Interior | Terrestre | 45.0 | 18.3 | 3.9 | 21.1 | 4.2 | 22.8/22.8/22.8 | 18 | 3.03 |
| Vara Alta | Reef Interior | Terrestre | 17.6 | 1.6 | 0.2 | 12.5 | 0.2 | 13.0/44.9/44.9 | 13 | 0.26 |
| Acuatempa | Reef Rim | Terrestre | 6.6 | 101.7 | 30.2 | 29.7 | 31.2 | 30.7/31.8/31.8 | 20 | 3.70 |
| Álamo San Isidro | Reef Rim | Terrestre | 7.0 | 211.1 | 72.9 | 34.5 | 73.0 | 34.6/34.6/34.8 | 26.5 | 1.38 |
| Alazán | Reef Rim | Terrestre | 15.7 | 66.3 | 19.7 | 29.7 | 19.8 | 29.9/29.9/29.9 | 16 | 0.31 |
| Arrecife Medio | Reef Rim | Marino | 1.8 | 2.4 | 0.02 | 0.7 | 0.02 | 0.7/0.7/0.7 | 20 | 0.11 |
| Atún | Reef Rim | Marino | 18.3 | 309.4 | 41.0 | 13.3 | 42.3 | 13.7/14.0/14.4 | 40 | 30.5 |
| Bagre | Reef Rim | Marino | 34.5 | 216.7 | 73.9 | 34.1 | 77.4 | 35.7/37.5/37.5 | 36 | 17.4 |
| Caristay | Reef Rim | Terrestre | 2.1 | 0.4 | 0.2 | 45.2 | 0.2 | 45.2/45.2/45.2 | 17 | 0.11 |
| Cerro Viejo | Reef Rim | Terrestre | 12.9 | 89.2 | 26.5 | 29.7 | 26.8 | 30.0/30.3/30.6 | 22 | 0.39 |
| Chichimantla | Reef Rim | Terrestre | 5.7 | 14.6 | 6.0 | 40.8 | 6.1 | 41.6/41.6/43.6 | 20 | 1.57 |
| Escualo | Reef Rim | Marino | 2.0 | 5.2 | 1.9 | 36.5 | 1.9 | 36.5/36.5/36.5 | 36 | 2.09 |
| Ezequiel Ordóñez | Reef Rim | Terrestre | 5.2 | 175.0 | 65.7 | 37.6 | 66.0 | 37.7/37.7/37.7 | 21 | 5.57 |
| Gutiérrez Zamora | Reef Rim | Terrestre | 2.3 | 2.6 | 1.0 | 39.5 | 1.1 | 40.6/40.6/53.0 | 18 | 0.13 |
| Horcón | Reef Rim | Terrestre | 5.7 | 11.3 | 4.0 | 35.0 | 4.0 | 35.3/35.3/35.3 | 21 | 0.79 |
| Ignacio Allende | Reef Rim | Transicional | 2.2 | 0.3 | 0.08 | 27.0 | 0.08 | 27.0/27.0/27.0 | 20 | 0.15 |
| Isla de Lobos | Reef Rim | Marino | 2.2 | 57.7 | 22.5 | 39.0 | 22.5 | 39.0/39.0/39.0 | 41 | 6.65 |
| Juan Felipe | Reef Rim | Terrestre | 5.4 | 48.4 | 14.5 | 29.9 | 14.6 | 30.1/31.6/33.9 | 18 | 0.58 |
| Marsopa | Reef Rim | Marino | 4.8 | 68.6 | 19.1 | 27.9 | 19.3 | 28.1/32.7/33.5 | 35.1 | 10.7 |
| Mesa Cerrada | Reef Rim | Terrestre | 2.9 | 37.8 | 13.7 | 36.1 | 13.8 | 36.4/36.9/37.9 | 23 | 3.65 |
| Miguel Hidalgo | Reef Rim | Terrestre | 5.7 | 38.1 | 8.5 | 22.4 | 8.6 | 22.5/22.5/23.8 | 30 | 1.46 |
| Morsa | Reef Rim | Marino | 4.0 | 33.2 | 11.5 | 34.7 | 11.5 | 34.7/34.7/34.7 | 35 | 11.4 |
| Ocotepec | Reef Rim | Terrestre | 2.8 | 81.6 | 20.2 | 24.7 | 20.4 | 25.0/25.9/26.5 | 20 | 4.59 |
| Potrero del Llano Horcones | Reef Rim | Terrestre | 7.6 | 401.1 | 119.7 | 29.8 | 119.9 | 29.9/29.9/30.2 | 19 | 0.65 |
| San Diego Chiconcillo | Reef Rim | Terrestre | 46.7 | 44.6 | 0.8 | 1.8 | 0.9 | 1.9/2.7/6.4 | 11 | 0.53 |
| Santa Águeda | Reef Rim | Terrestre | 11.0 | 386.5 | 124.5 | 32.2 | 126.6 | 32.8/32.9/33.1 | 16 | 11.8 |
| Sur Chinampa Norte de Amatlán | Reef Rim | Terrestre | 22.7 | 718.8 | 214.8 | 29.9 | 217.1 | 30.2/30.2/30.4 | 27.5 | 1.74 |
| **Tecolutla** | Reef Rim | Terrestre | 3.1 | 7.8 | 1.9 | 24.5 | 2.0 | 25.0/25.0/27.2 | 28 | 0.93 |
| Tepetate Norte Chinampa | Reef Rim | Terrestre | 8.8 | 560.6 | 167.6 | 29.9 | 168.1 | 30.0/30.1/30.1 | 23 | 0.45 |
| Tiburón | Reef Rim | Marino | 2.5 (1.9 SUP_KM2) | 62.5 | 0.0 | 0.0 | 0.0 | 0/0/0 | 33 | 3.01 |
| Tierra Blanca-Chapopote-Núñez | Reef Rim | Terrestre | 29.2 | 352.5 | 105.3 | 29.9 | 105.6 | 30.0/30.0/31.0 | 18 | 0.96 |
| Tihuatlán | Reef Rim | Terrestre | 2.6 | 3.8 | 0.8 | 21.3 | 0.8 | 22.2/22.2/22.2 | 19 | 0.18 |
| Tintorera | Reef Rim | Marino | 4.5 (1.4 SUP_KM2) | 0.8 | 0.07 | 9.6 | 0.07 | 9.6/9.6/9.6 | 33 | 0.01 |
| Toteco Cerro Azul | Reef Rim | Terrestre | 36.5 | 1,256.9 | 377.4 | 30.0 | 379.5 | 30.2/30.2/30.3 | 19 | 3.11 |
| Vicente Guerrero | Reef Rim | Terrestre | 1.6 | 13.6 | 5.0 | 36.5 | 5.0 | 36.6/36.6/36.6 | 27 | 0.27 |
| Xocotla | Reef Rim | Terrestre | 5.1 | 4.3 | 1.7 | 40.3 | 1.8 | 40.8/40.8/40.8 | 16 | 0.30 |
| Zacamixtle | Reef Rim | Terrestre | 9.0 | 61.4 | 18.5 | 30.1 | 18.5 | 30.2/30.2/30.2 | 20 | 0.34 |
| **Total (45)** | | | 509.4 | 6,126.3 | 1,777.7 | 29.0 | 1,795.5 | 29.3/29.5/29.9 | | |

Header note in the sheet: "data for this section is based on CNH production data that only goes back to Jan-1960" [ANA row 1]. D07 §3 derives from this table: reef-rim median RF 30 %, production-weighted 29 %, 3P EUR RF P90/median/P10 12/31/40 %, best reef-rim 53 % (Gutiérrez Zamora); Tecolutla OOIP density 2.5 MMbbl/km² versus reef-rim median 8.3. WP: "up to 45 % recovery from other El Abra pools" (Caristay 45.2 %, Vara Alta 44.9 % 2P/3P). Neighbouring fields on the same gathering system: Gutiérrez Zamora (2.3 km², 2.6 MMbbl), Vicente Guerrero (1.6 km², 13.6 MMbbl), Ezequiel Ordóñez (5.2 km², 175 MMbbl) [ANA; RES para 52]; Miguel Hidalgo is the well-spacing analogue used by IFR [BK20] and the seismic tie well [SEIS18].

## 7. Gaps: what the deck section needs that no source provides

1. A named seal and source rock. No source names either; only the erosional absence of Upper Cretaceous on the crest (T6FR) and the Tantoyuca shale lithology (PROG) can be quoted.
2. A stage-level age for the El Abra at Tecolutla (only "Cretácico Medio") and any biostratigraphic control other than the single Globotruncana note in the core.
3. Closure height, spill point and the mapped area inside a specific contour other than the 2,315 mSS / 75.3 ac hand polygon. No source gives the contour used for GLJ's 401/515/630 ac.
4. A single agreed top-El-Abra pick per well: TEC-2 has three values (2,304, 2,307, 2,316–2,320 mMD), TEC-6 two (2,294 / 2,296 mSS), TEC-10 two (2,307 mSS log / "~2,310 m" mud log); TEC-7, TEC-3, TEC-101 tops are not printed anywhere in the repo (TEC-7 only readable from an image).
5. TEC-11 formation tops: the mud log names none; only the lithology change at 2,360 mMD is available. TEC-3, TEC-101 and TEC-7 final reports are not on the Drive list read.
6. Oil–water contact: no source states one. Candidates in the files are the PR "deep contact −2,374 mSS" and the water-bearing 2,331–2,345 mSS TEC-2 perforations; PROG lists defining the OWC as a TEC-12 objective.
7. Seismic: no line/inline/crossline numbers, no bin size, fold or bandwidth, no velocity values or time–depth table, no checkshot/VSP at Tecolutla, no synthetic at any Tecolutla well, no attribute maps, no image of the reprocessed PSDM at the TEC-12 location (PR Figure 2 missing), no quantified depth-prognosis miss at TEC-10 (PR says "came in lower", the number is absent).
8. The depth map's own numbers: DEPTH is a screenshot with 5 m contours but no legend scale; the crest and saddle values (2,290 / 2,300 m) are read from labels, not from a grid.
9. Any evidence, other than the SINK slide's assertion, that TEC-10 "encountered a small sinkhole" (the masterlog, lithology log, CMI summary and core report do not mention losses, cavities or a sinkhole; the sink-hole slide shows no data).
10. Porosity/thickness of the analogue fields: ANA has none; a proper analogue table (net pay, porosity, depth, drive) would need another source.
11. TEC-12 actual results: nothing in the repo indicates TEC-12 was drilled; all TEC-12 depths are prognoses.
12. The PEMEX 1956–1972 structural maps and the 2011 PSTM interpretation are only available as two small JPEGs in the RES docx.

## 8. Reader's notes (my interpretation, not in the sources)

- **Inter-well distances computed from HDR UTM coordinates**, with TEC-9 and TEC-12 bottom holes placed by the WP displacements (TEC-9 BH = surface + 117.23 N, −12.52 E; TEC-12 BH = TEC-10 pad + 35 N, 171 E; TEC-10 BH = masterlog "Objetivo" 707,589.6 / 2,262,253.1): TEC-2→TEC-7 456 m (matches BK20 exactly, so the header coordinates and the IFR map share a datum); TEC-10 pad→TEC-9 277 m; TEC-10 pad→TEC-6 123 m; TEC-10 BH→TEC-9 258 m; TEC-12 BH→TEC-9 surface 162 m, →TEC-9 BH **77 m**, →TEC-10 BH 269 m, →TEC-6 258 m, →TEC-7 308 m, →TEC-2 538 m; TEC-6→TEC-9 390 m; TEC-9→TEC-7 386 m. The PROG target (707,753 / 2,262,460) is the same point as the WP displacement to within a metre. So "as close to TEC-9 as possible" [PR] means about 77 m from the TEC-9 bottom hole.
- The TEC-12 prognosed column (PROG p8) reproduces the TEC-6 1956 tops within a few metres (Escolín 726 vs 721 mSS, Coatzintla 1,117 vs 1,115, Palma Real 1,743/2,003 vs 1,742/2,004, Tantoyuca 2,210 vs 2,223, El Abra 2,296 vs 2,296). The prognosis is therefore a TEC-6 analogue, not a seismic-derived depth at the TEC-12 location, which is consistent with PR's remark that depth accuracy is "mitigated by drilling TEC-12 as close to TEC-9 as possible".
- The seismic-derived Petrel map (DEPTH) shows two 2,290 m culminations and a 2,300 m saddle, i.e. total relief inside the field polygon of order 10–25 m over ~1.5 km, whereas the PEMEX 2014 map has a single crest class (−2,300 to −2,320) and 20 m contours. The well tops (2,294–2,307 mSS at TEC-6, 9, 2, 10, 7) support a top-El-Abra relief of only ~13 m across the drilled area. The TEC-12 "structurally higher" argument therefore rests on a few metres of relief plus the un-perforated interval, not on a distinct closure.
- The two closed circular lows west of the field on the DEPTH map and the "channels crossing the reef margin" of PROG p13 are the seismic-scale expression of the karst/erosion that PR and SINK discuss; the sources do not say this explicitly, and the lows could equally be velocity or picking artefacts on "very poor" data.
- The 1800/1850 labels on the SEIS s1 surface do not match the 2,29x mSS field values; that screenshot is probably displaying a different surface (or TWT in ms) than the DEPTH map. Do not quote depths from it.
- "Sw = 0.05 %" on the TEC-6/TEC-9 comparison label is not physically meaningful; it is most likely a mis-typed 5 % or a mislabelled porosity cut-off.
- The core (no hydrocarbons in six thin sections, 0.04–1.2 mD) and the CMI (no open fractures in the TEC-12 window at TEC-10) sit against the WP's "high porosity reef margin found in Tec-10 upper zone" and the sink-hole slide. The deck should present the core/CMI facts and the sink-hole slide as an assertion, and the "3 m net pay at TEC-10" [PR] as the calibration point for the "15 m at TEC-12" claim.
- The RES Table v.2 "20 °API" conflicts with the 28 °API in the RES text, PROG (28.6) and the CNH table (28); it is the Ezequiel Ordóñez-41 PVT proxy, not a Tecolutla measurement.
- Nothing in the seismic sources supports a fault-bounded trap at TEC-12 (PR and PROG both say no faults), but the PEMEX 2014 map draws NW–SE normal faults on both flanks. The deck should show both maps and say the flank faults are outside the drilled area.
- Stage assignment: the El Abra of the Faja de Oro is Albian–Cenomanian in the regional literature; none of the project sources say so, so it should be cited as literature, not as project data.

## 9. Exported images (`data/processed/deck_notes/img/`)

| File | Source | Content |
|---|---|---|
| `tec12_seismic_s01_Picture_2_*.png` | SEIS s1 | 3D view, seismic section over top-El-Abra surface, TEC-10/TEC-9 tracks |
| `tec12_seismic_s02_Picture_6_*.png` | SEIS s2 | Traverse TEC-10, 9, 7, 2 with green top-El-Abra pick |
| `tec12_seismic_s03_Picture_4_*.png` | SEIS s3 | Section TEC-9 BH – TEC-10 surface – TEC-6 |
| `elabra_depth_tec12_s01_top_el_abra_depth_map_TVDSS_5m.png` | DEPTH | Petrel top El Abra TVDSS map, 5 m contours, 500 m bar |
| `xsections_navarrete_s01_Imagen_2_*.png` | XS s1/3/5/7/14/16 | Green contour structure map with the seven wells |
| `xsections_navarrete_s15_Imagen_2_*.png` | XS s15 | Same map with the 2,315 mSS / 75.3 ac polygon and TEC-12 marker |
| `xsections_navarrete_s02_Imagen_3_*.png` | XS s2 | Cross-section TEC-10 – TEC-9 – TEC-2 in mSS, perforations and un-perforated flags |
| `xsections_navarrete_s04_Imagen_1_*.png` | XS s4 | Cross-section TEC-10 – TEC-6 – TEC-2 |
| `xsections_navarrete_s06_Imagen_3_*.png` | XS s6 | Cross-section TEC-10 – TEC-9 – TEC-7 |
| `xsections_navarrete_s08_Imagen_3_*.png` | XS s8 | Cross-section TEC-6 – TEC-9 – TEC-7 |
| `xsections_navarrete_s09_Picture_2_*.png` | XS s9 | "Tecolutla Field Logs" inventory matrix |
| `xsections_navarrete_s10_Picture_2_*.png` | XS s10 | TEC-2 GR/SP/micro/SN-LN/NPHI panel with perforation history |
| `xsections_navarrete_s11_Imagen_3_*.png` | XS s11 | TEC-10 modern log panel, top El Abra 2,307 mSS, 2018 perforations |
| `xsections_navarrete_s12_Picture_3_*.png` | XS s12 | TEC-6 GR/neutron panel, top 2,294 mSS, three perforation sets |
| `xsections_navarrete_s13_Picture_2_*.png` | XS s13 | TEC-9 GR/SP/neutron/SPHI/resistivity panel, top 2,296 mSS |
| `tantoyuca_tec269_s01_Imagen_11_*.png` | TAN s1 | TEC-2 GR/NPHI/LN in mSS, 2,295–2,370 |
| `tantoyuca_tec269_s03_Imagen_8_*.png` | TAN s3 | Scanned TEC-6 1956 GR-neutron strip (2,200–2,300 m) |
| `tantoyuca_tec269_s03_Imagen_6_*.png` | TAN s3 | TEC-9 GR/ILD/NEUT 2,190–2,310 mSS showing the Tantoyuca/El Abra contact |
| `tec9_sslogs_s01_Picture_2_*.png` | T9SS | TEC-9 CALI/SP/GR/SPHI/NEUT/ILD 2,265–2,335 mSS with 3–8 % and 4–6 % annotations |
| `tec10_sinkhole_s01_Picture_3_*.png` | SINK | Satellite image of a sinkhole field |
| `tec10_sinkhole_s01_Picture_1_*.png` | SINK | Karst block diagram |
| `resumen_campo_03_Figura_iii_1_*.jpeg` | RES Fig iii.1 | PEMEX SW–NE time section through Teo-101, Tecolutla-2, Teo-3 |
| `resumen_campo_04_Figura_iii_2_*.jpeg` | RES Fig iii.2 | PEMEX top El Abra depth map with faults, 2014 |
| `resumen_campo_05_Figura_iv_1_*.png` | RES Fig iv.1 | Seismic section with reef-facies model and thin-section photos |
| `resumen_campo_06_Figura_vi_3_*.jpeg` | RES Fig vi.3 | Static pressure history 254 → 251 kg/cm² |
| `resumen_campo_07_Figura_vii_1_*.png` | RES Fig vii.1 | PEMEX type-well mechanical sketch |

The docx logos and socio-economic tables (resumen_campo_01, 02, 08–12) were not kept.

## 10. Additions (second pass): the 2017 Plan de Evaluación and the PEMEX estados mecánicos

Source keys for this section. **PE17** = Drive `1P7EHEf7_Kx0d3Q1ggtlNiN1mOJBudD1q` "Plan de Evaluación (Tecolutla) 0517.es.en.pdf", the CNH evaluation plan of May 2017 in machine-translated English (text rendering in the session tool-results folder; page numbers are the "Page N from 98" footers). **EM9 / EM7 / EM5 / EM101** = PEMEX estados mecánicos, Drive `1ys9wOiU3wEZcPOBYqTGImBFUh6bShavH` (TEC-9), `1UZlBMHqRINt7shznmzawH4JM3W6TgcUt` (TEC-7), `1VCktsVx2MvIEIQA8HKgS0IYt-SC1NFBn` (TEC-5), `1a00morBDt-ubREnnrnxO0ZW5mYsEUUeJ` (TEC-101). **GLJMAP** = Drive `1xGo-WvPj4KPEOW8VMYgze6t73mTVYaM0` GLJ "Map 2 Top Depth Structure, El Abra" (31 Dec 2019). The estados mecánicos and GLJ map are quoted from `data/processed/deck_notes/drive_reads_notes.md` (second batch), not read directly.

### 10.1 Contract, area and reservoir summary table [PE17]
- Contract CNH-R01-L03-A24/2016, licence, signed 25 Aug 2016, Tonalli 100 %, contract area 7.16 km², minimum work 4,600 units [p9 Table 1]. Evaluation area 4.9 km² [p10 Table 2]; evaluation-area vertices in Table 8 [p50] span 97°00'–97°02' W, 20°26.5'–20°28' N.
- Table 2 "Characteristics of the assessment area" [p10–11]: discovery well Tecolutla-2, June 1956; formation El Abra; average depth of the producing formation 2,340 m; **"contact with water 2,350 m"** (datum not stated); 7 wells, 4 historic producers; depositional environment "coral barrier"; lithology limestone; era Mesozoic, period Cretaceous (the stage cell is garbled by the translation); basin Tampico–Misantla; Sw 24–38 %; porosity 5–12 %; **permeability 6–10 mD; gross thickness 70 m; net thickness 25 m**; oil 20 °API (as printed, the RES PVT-proxy value), 11.2 cP, initial GOR 59.9 m³/m³, Bo 1.192, sulphur 0.134 mol %, Pb 13.2 MPa; reservoir temperature 95 °C; initial pressure 25.4 MPa; recovery mechanism "hydraulic push (water)"; peak 932 bpd, March 1972; cumulative 1.9 MMbbl.

### 10.2 Field history as PE17 tells it [p11–13, p27 Table 3]
- PEMEX started 10 Feb 1956 with **Tecolutla-3**, drilled to the top of El Abra (TD 2,380.5 m); a formation test at 2,376.8–2,380.8 m recovered "980 m of oil and 80 m of water" in the pipe (as translated); abandoned 7 Mar 1956.
- **Tecolutla-2** spudded 16 Apr 1956, 520 m SW of TEC-3, completed 31 May 1956 at 2,375–2,379 m; three tests 252–453 bpd; the discovery well.
- **Tecolutla-5** spudded 25 Jun 1956, 1,290 m NW of TEC-2, TD 2,562 m, El Abra structurally low and water-bearing, abandoned; "marked the end of the exploration phase".
- All later wells within 500 m of TEC-2: **TEC-6** (Sep–Oct 1956, TD 2,338 m, 579 bpd from 2,336–2,338 m) and **TEC-7** (Nov 1956–Jan 1957, TD 2,340 m, 352 bpd from 2,335–2,337 m). Daily production before 1966 was not in the CNH data package.
- **Tecolutla-101** drilled from 15 Apr 1972 as a deeper exploration well "to investigate the Lower Cretaceous and Jurassic syn-rift stratigraphy"; drilling problems at 2,678 m, equipment left in hole, abandoned (TD 2,804 m; EM101: plugged 31 Mar 1972, water-invaded, structurally low, open hole 2,718–2,804 m).
- **Tecolutla-9** spudded 1 Apr 1973, TD 2,340 m, 189 bpd from 2,328–2,333 m; last production Jul 2012.
- All producers flowed naturally to a single battery and were trucked; gas vented or flared; from Feb 2016 all wells suspended or abandoned. Status at 2017: TEC-2 closed (last prod Dec 2014), TEC-7 closed (Dec 2006), TEC-6 plugged (Dec 2006), TEC-9 plugged, TEC-3/5/101 plugged; TEC-10 planned as a deviated well to ~2,500 m from the TEC-6 location.

### 10.3 Regional geology and trap as PE17 states it [p12–13]
- "The contract area is located at the southeastern end of the [Faja de Oro] El Abra reef in the Tampico–Misantla basin", offset by the geologically similar Miguel Hidalgo block (NW) and Ignacio Allende block (SE).
- "During the Early Cretaceous the Golden Lane reef developed on a pre-existing basement high, forming an ellipsoidal carbonate atoll about 150 km long, 70 km wide and 1,200 m thick. A reef facies developed along the outer edge and isolated lagoonal patch reefs formed in the protected interior. A sea-level drop at the end of the Albian resulted in subaerial exposure of the upper part of the reef, improving reservoir quality. Subaerial exposure also cut large channels through the reef margin which now provide the lateral oil trap and separate the individual blocks along the Golden Lane."
- "The contract area lies on the fringing reef of the Golden Lane and is composed of rudist patch-reef packstones and grainstones." "Reservoir quality of the reef margin was improved by post-depositional subaerial exposure that created dissolution cavities. Porosity 5–12 % with permeability up to 200 mD (from a single well test, Tecolutla-2). Reservoir quality may also have been improved by natural fractures related to post-depositional faulting."
- Seismic: "The 3D interpretation of the Furbero–Presidente [Alemán] volume acquired in 2011 identified a four-way closed structural high at an average depth of 2,340 m extending NW–SE across the block. No wells have been drilled since the 3D acquisition."
- Still not stated in PE17: seal, source rock, closure height, spill point.

### 10.4 The 2017 evaluation work programme [PE17 p33–45, p51–52, p60–64]
1. **TEC-2 major workover** (USD 676,372): static gradient "to confirm reservoir pressure and evaluate the oil column"; cased-hole GR/CCL and pulsed-neutron "to confirm formation tops, evaluate heterogeneity and porosity, identify intervals for future drilling or re-entry"; casing test; cement log; perforate and HCl-stimulate target El Abra intervals; 10-day and 120-day tests; rod pump.
2. **TEC-10 new drill** from the rehabilitated TEC-6 location, directional, "to 2,450 m TVD" (Table 5; the casing sheet prints final depth 2,400.0 / 2,550.0) "to assess fluid contacts"; ~10 m core (USD 33,211) for porosity, permeability, residual oil, facies; open-hole GR, dipole sonic, neutron, density and image log "to check the top of the formation, evaluate heterogeneity and porosity, take the log correlation for seismic interpretation and geomechanics, and image fractures and secondary porosity"; perforate porous intervals "above the oil–water contact"; acidise; 10/120-day tests (USD 567,715). TEC-10 prognosis tops on the casing sheet [p51–52], two unlabelled columns as printed: Palma Real Inferior 2,016.0 / 2,030.0; Tantoyuca 2,300.0 / 2,210.0; "El Abra porosity" 2,370.0 / 2,281.0; final depth 2,400.0 / 2,550.0 (the second column matches the TEC-12 mSS prognosis for Tantoyuca; which column is mMD and which mSS is not resolvable from the text).
3. **Seismic reprocessing and interpretation** of 7.12–7.2 km² (the contract area), 143 work units, USD 78,000: "to improve the image of the top of the El Abra reservoir, improve the velocity-model resolution and identify shallow drilling risks … enable more accurate prediction of remaining reserves and optimal development locations".
4. Total plan USD 10,474,253 over 12 months from 24 Feb 2017 [p45]. Reserves basis [p60]: "The Tonalli team's estimated reserves are higher than those provided to us, but our estimated reserves range is very wide"; no OOIP figure appears in the text (the 7.8 MMbbl / 24.35 % RF basis of 2014 is in RES).

### 10.5 Formation tops from the PEMEX estados mecánicos and the GLJ map

| Formation | TEC-9 mMD [EM9] | TEC-6 mMD / mSS [T6FR] | TEC-5 mMD [T5FR] | TEC-12 prognosis mMD (mTVD, mSS) [PROG p8] |
|---|---|---|---|---|
| Escolín | 738 | 727 / 721 | 580 | 734.5 (734.2, −726) |
| Coatzintla | 1,133 | 1,121 / 1,115 | 1,160 | 1,136.7 (1,125.2, −1,117) |
| Palma Real Superior | 1,759 | 1,748 / 1,742 | 1,790 | 1,770.2 (1,751.2, −1,743) |
| Palma Real Inferior | 2,019 | 2,010 / 2,004 | 2,035 | 2,030.2 (2,011.2, −2,003) |
| Tantoyuca | 2,219 | 2,229 / 2,223 | 2,210 | 2,237.2 (2,218.2, −2,210) |
| Chicontepec Inferior | – | absent | 2,427 | – |
| San Felipe | – | absent | 2,497 | – |
| El Abra | **2,310 (2,301 mTVD KB, 2,296 mSS)** | 2,302 / 2,296 | 2,555 / 2,551 mSS | 2,323.2 (2,304.2, −2,296) |
| PT | 2,340 | 2,338.9 | 2,562.1 | 2,360 (2,341, −2,332.8) |

- EM9 other facts: spud 1 Apr 1973, TD 7 May, completed 19 May 1973; GL 1.24 m, KB 5.07 m; UTM 707,873.67 / 2,262,243.38 (about 100 m from the header-CSV surface location 707,833.50 / 2,262,336.31; the header CSV is used for the §8 distances); deviated from 296 m, N6°15'W, 11°15', 112 m displacement; fish (4½" slips) at 388 m in the first hole, cemented; perforations 2,328–2,333 mMD (2,319–2,324 mTVD); logs induction, sonic porosity, microlog, dipmeter, GR, CBL; initial May 1973 on 3.5 mm choke 91.6 m³/d oil, RGA 230; final Sep 1998 30 m³/d, 4 % water; closed Jan 1999.
- EM7: perforations 2,310–2,313 m (open) and 2,335–2,337 m; 6⅝" casing to 2,306.5 m; 4½" liner 2,281–2,340 m; no tops in the summary. EM5: plugged 28 Jul 1956, 9⅝" at 501.35 m, open hole to 2,562.10 m. EM101: 9⅝" at 807.19 m, fish at 926 m, open hole 8⅝" 2,718–2,804 m.
- GLJMAP top El Abra (mSS, 10 m contours, NAD83 UTM 14N): TEC-6 −2,294; TEC-9 −2,295.87; TEC-2 −2,302; TEC-7 −2,304.2; TEC-10 −2,309.93; TEC-11 −2,311.88 (a second label reads −2,370.3); TEC-101 −2,334; TEC-5 −2,551; TEC-3 unreadable.

### 10.6 What the additions change in §1–§7
- **Water contact (gap 6):** PE17 Table 2 gives "contact with water 2,350 m" (datum unstated; with the 2,340 m "average depth of the producing formation" it reads as a well depth, i.e. roughly 2,345 mSS). This is a third number beside PR's −2,374 mSS deep contact and the TEC-2 wet perforations at 2,331–2,345 mSS; the deck should show all three with their provenance.
- **Permeability:** PE17 gives 6–10 mD (Table 2) and "up to 200 mD" from the TEC-2 test (p13), versus 0.04–1.2 mD core plugs and the 13.2 m "kh" interval of the IHS PTA cited in D13.
- **Thickness:** 70 m gross / 25 m net (PE17, 2017) versus 42.3 m gross / 16.9 m net (WP/IFR) and 46.8 m gross (PR); the deck's thickness slide needs to say which basis it uses.
- **Top El Abra per well:** GLJ's TEC-10 top (−2,309.93) is 3 m deeper than the XS panel's 2,307 mSS; GLJ TEC-2 −2,302 versus XS 2,300; GLJ TEC-7 −2,304.2 confirms the image reading in §2.1; TEC-9 is 2,296 mSS in EM9, XS, WP and GLJ (−2,295.87), the one well where every source agrees. TEC-101 top −2,334 mSS (GLJ) is the first number for that well in the repo.
- **Age:** PE17 places reef growth in the Early Cretaceous with end-Albian exposure; the reservoir interval itself is still only "Middle Cretaceous".
- **Seismic:** PE17 confirms the 2011 volume name and that the 2017 plan budgeted only a 7.2 km² reprocessing; SEIS18 later describes ~150 km² reprocessed (PSTM by Earth Signal, PSDM by DMI). The 2017 statement "four-way closed high at an average depth of 2,340 m" is the earliest structural claim by Tonalli.
- **Gaps added:** the TEC-3 formation-test record, the TEC-101 result at its Jurassic objective, the TEC-7 formation tops, and the "Tonalli team reserves" figure of 2017 are not in any text read.
