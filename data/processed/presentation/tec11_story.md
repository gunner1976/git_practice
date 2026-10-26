# TEC-11DES: the horizontal that never tested its concept

Depths are mMD below KB (4.70 m) and mSS (metres below sea level) from the directional survey (`data/raw/geology/Directional Survey/TECOLUTLA DIRECTIONAL SURVEY DATA.CSV`, interpolated in `data/processed/tec11/facies_along_hole.csv`). Paths are relative to the repository root.

## 1. Concept: why a horizontal, and what it was meant to prove

- **The idea.** Put a long lateral in the top of the oil column, complete it open hole and produce it at low drawdown so the water arrives later. That is Kevin's description, which the briefing confirms as the intent (`docs/18_kinjal_briefing.md` A5).
- **The fracture argument.** The operator drilled the well at about 320° to cut critically stressed natural fractures predicted from TEC-10 (SHmax 80°, a conjugate set). The survey confirms the azimuth: 316° building to 327–331° (`data/processed/database_review/pres_findings.md` §4; `docs/03_tec11_facies.md` §2).
- **The karst argument.** A slide claims the horizontal path "will be able to drill through small sub-seismic sinkholes and back into El Abra Reservoir" (`data/processed/deck_notes/geology_geophysics_notes.md` §2, sink-hole slide).
- **What it was meant to prove: that horizontals would work for field development.** The January 2019 forecast carried TEC-11, TEC-12 and TEC-13 as horizontals at 694 bbl/d each, about 0.69 MMbbl per well, against TEC-10's 149 bbl/d (`data/processed/database_review/eng_findings.md` item 6). GLJ's YE2019 report still booked TEC-12 and TEC-13 as horizontals, at USD 2.4 MM each (`data/processed/database_review/res_findings.md`).
- **Pre-drill screening.** A Babu–Odeh horizontal-productivity model (`HWrates (TEC-11).xls`) was used. It is a model, not test data (`data/processed/deck_notes/wells_ops_reserves_notes.md` §0).

## 2. The plan

| Item | Plan | Source |
|---|---|---|
| Surface location | TEC-2 pad, X 707,605.00, Y 2,263,031.17 (UTM 14N) | survey CSV |
| Budget | Drilling AFE TON2018DR002, USD 2,250,000. All-in budget USD 3,934,870 | `data/processed/deck_notes/accounting_notes.md` §2 |
| Landing | The Jan 2019 deck's cross-section labels a "TEC-11 landing" but gives no number. The same deck says "PEMEX OWC 90 m lower than TEC-11 planned perfs". With the 2,380 mTVDss original FWL from the Jul 2019 deck, that would put the planned perforations near 2,290 m. That is arithmetic across two decks, not a stated value | `pres_findings.md` §3 |
| Completion | Ten 2 m plug-and-perf intervals at 2,624–2,806 mMD (2,313–2,323 mSS) in the Jan 2019 deck. The cost workbook plan was 20 perforated intervals, 20 stimulations, a 14-day flow test and 30 days in all | `data/processed/petrophysics/perforations_mss.csv`; `wells_ops_reserves_notes.md` §2.4 |
| Logging | LWD gamma ray and sonic. Resistivity was recorded only to 2,341 mMD (about 2,236 mSS). No pilot hole | `data/processed/database_review/las_findings.md`; `docs/18_kinjal_briefing.md` A5 |

## 3. What happened, step by step

| Date | Step | mMD | mSS | Source |
|---|---|---|---|---|
| 11 Nov 2018 | Spud. The accounting notes give 9 Nov, with pre-spud work 9–13 Nov | 0 | +4.7 | `wells_ops_reserves_notes.md` §2.4; `accounting_notes.md` |
| Nov 2018 | Pump failure in the surface hole. The auto-driller failed while building angle. 47° at 2,209 m, 60° at 2,318 m | 2,209 / 2,318 | 2,161 / 2,225 | `docs/03_tec11_facies.md` §2; review v3 §4 |
| 24–25 Nov 2018 | Only 25 m in the last 24 h (2,332–2,357). The 7" 26 lb/ft casing was set at 2,354.44 m at about 61.6°. A hydraulic-arm failure while running casing; 51.5 h from casing point to cemented | 2,354.44 | ~2,243 | `drive_reads_notes.md` (Halliburton 25 Nov 2018) |
| Nov–Dec 2018 | Carbonate becomes the dominant cuttings lithology | 2,360 | 2,245 | `docs/03_tec11_facies.md` §3 |
| | Lateral begins (≥ 80°) | 2,563 | 2,305 | same |
| | Grey-green bentonitic shale inside the "carbonate" | 2,584–2,615 | 2,308–2,312 | same |
| | 90° reached. The lateral is then held at 2,322–2,324 mSS to 3,140 mMD | 2,727 | 2,323 | same |
| | The only moderate oil show in the well | 2,920–2,945 | ~2,323 | same |
| | 30–40 % bentonite over the last 180 m | 3,103–3,283 | 2,322–2,331 | same |
| 18 Dec 2018 | TD at 82°, 1,190 m from surface (BHL X 706,847.16, Y 2,263,952.40). The 4½" liner and tie-back were run. The liner hanger was damaged, the tie-back string was faulty and then damaged, lost pieces were fished, and the liner needed two cement jobs | 3,283 | 2,331.0 | survey CSV; `wells_ops_reserves_notes.md` §2.4 |
| 26 Dec 2018 | Rig released. Drilling cost USD 3,025,996 against the 2.25 MM AFE (USD 3,105,308 final) | | | `accounting_notes.md` §2 |
| Jan 2019 | CBL and wellbore clean-up, USD 129,360 | | | same |
| May 2019 | Completion. A 5.9 m fish (bit plus watermelon mill) was lost at 2,866–2,872 m. The liner, from the tie-back at 1,869.18 m, ends at 2,863 m. The 411 m of open hole beyond it (2,872–3,283 m) could not be re-entered | 1,869–2,863; fish 2,866–2,872 | 1,864–2,323; 2,323 | `data/processed/wells/casing_strings.csv`; `eng_findings.md` item 2 |
| Jun 2019 | Five 3 m perforations: 2,643.5–2,646.5, 2,673.5–2,676.5, 2,700.5–2,703.5, 2,726.5–2,729.5 and 2,742.5–2,745.5 m. The selective acid tool could not pass the damaged liner hanger, so acid was bull-headed from surface without isolation. Pressure broke down quickly, and acid went in at low pressure and high rate. There was some oil, then 100 % water: "acid likely entered a fracture and induced an overwhelming flow of water from the aquifer" | 2,643.5–2,745.5 | 2,316–2,323 (the Jul 2019 deck says 2,316–2,322 mTVDss) | `casing_strings.csv`; `docs/12_drive_large_files.md` §1 |
| to 12 Jul 2019 | About 935 bbl of water (1.5–2× the load) at 78,000 ppm Cl ("still spent acid"), with trace oil only. Test on 11 Jul: 260 bbl/d water on a 12/64" choke at 195 psi WHP. The final Tonalli schematic gives 286 bbl/d water at 100 % water cut | | | `pres_findings.md` §4; `drive_reads_notes.md` |
| 11–12 Aug 2019 | Boss composite blind plug (10,000 psi) set in the 4½" liner. Well killed with 1.06 g/cc brine; no cement | ~2,400 | ~2,263 | `drive_reads_notes.md` (Anexo 4) |
| Aug 2019 | Tantoyuca recompletion above the plug. The 22 Aug sample from 2,361–2,364 m was 17.0 °API with 31.8 % water. Trace oil and 96 bbl/d of water. Cost USD 206,225 | 2,361–2,364 | ~2,246–2,247 | `data/processed/deck_notes/fluids_rock_core_notes.md`; briefing A5 |
| 28 Aug – 2 Sep 2019 | Tantoyuca flow test, about 4.5 days (flow from 28 Aug 20:00; log ends 2 Sep 08:00). Choke 14/64" (12/64" in the daily summaries). WHP 350 psi at start, 160 psi by 29 Aug, then 165–170 psi. Water 192 bbl/d at start, mostly 96–144, ending at 96 bbl/d; daily water 80 / 120 / 100 / 102 / 126 bbl, total 528 bbl. Oil columns blank, BSW 100 %, natural flow. Jaguar deck: "final rates: 0 bbl/d oil (trace) - 96 bbl/d water - 0 mcf/d gas - ~170 psi flowing pressure - cumulative water 528 bbl - 17 API". No stabilised oil rate exists; the oil was a trace | 2,361–2,364 | ~2,246–2,247 | `Tantoyuca Seguimiento Tec #11 apertura.xlsx` (Drive 1AVbAb4iXaUEWQ0kTOJTBIwft6fyu29oo, one sheet per day 28 Aug–1 Sep); `Tecolutla Discussion with Jaguar (Sep 1st, 2022) Final.pdf` (Drive 1974i04rU2wMb73auSql8T3JiHZGznv_O, slide ~25 "5.2 Tec-11 HZ Drill (Tantoyuca)"; ~slide 24 gives the El Abra 11-day test: 0 oil, 286 bbl/d water, ~200 psi, 3,713 bbl cumulative water) |
| May–Aug 2019 | 26 truckloads, 4,397 bbl of water. This is the well's only production record; no oil was sold | | | `docs/04_production_database.md` §4 |
| 6 Sep 2019 | Completion finished. Final schematic issued 25 Sep 2019 | | | `drive_reads_notes.md`; `eng_findings.md` |
| 18 Oct 2019 | Reclassified from producer to injector with CNH | | | `drive_reads_notes.md` |
| Apr 2022 | Temporary-abandonment notice (art. 54). The 2024 abandonment reserve is USD 99,233, "water invaded", tubing-less | | | `drive_reads_notes.md` |

**Which formation was the lateral in?** This is unresolved (G-75), and the sources disagree:

- **Mud log (Rise Energy).** The lateral is "carbonate": 419 m mudstone–wackestone, 240 m with grainstone named (never pure grainstone), 31 m shale and 30 m bentonite-dominant. Version 3 of the review concluded "TEC-11 did penetrate El Abra" (`docs/03_tec11_facies.md`; `docs/Tecolutla_Field_History_and_TEC12_Review.md` §5.3).
- **Formation-tops table.** El Abra starts at 2,611.8 mMD (−2,311.9 mSS). The table calls the carbonate onset at 2,356.55 mMD "Tantoyuca_A" (`data/processed/database_review/geo_findings.md` §3).
- **Jan 2019 depth grid.** The lateral sits 4–10 m above the mapped El Abra top: well minus grid is −10.5 to +2.1 m, median −5.7 m (`data/processed/seismic/tec11_vs_grid.csv`).
- **Recorded sonic.** Over 2,563–3,283 mMD the median DTC is 73 µs/ft (Wyllie 18 %). That matches the Tantoyuca marl at TEC-10 (71 µs/ft) and not TEC-10's El Abra (52–57 µs/ft). No resistivity was run (`data/processed/database_review/las_findings_colab.md`; `docs/gaps.md` G-75, 26 Oct). The repository's current interpretation, flagged as interpretation, is that the lateral may have stayed in the marl above El Abra.

## 4. Costs

| Phase | Budget, USD | Actual, USD |
|---|---|---|
| Drilling | 2,853,870 (AFE 2,250,000) | 3,105,308 |
| CBL and clean-up (Jan 2019) | 100,000 | 129,360 |
| Completion (May–Jun 2019) | 831,000 | 962,850 ("Workstrings invoices") |
| Tantoyuca, including testing (Aug 2019) | 150,000 | 206,225 |
| **All-in** | **3,934,870** | **4,403,743 (+12 %)** |

Source: `Tec 11 Summary of Costs (Actual and Budgeted).xlsx`, via `accounting_notes.md` §2.

The 2023 tax pool carries TEC-11 at only USD 3,514,960 (drilling 2,869,365, completion 206,225, casing and tubing 439,370). From 2020 the completion line was cut from 1,401,250 to 206,225. The roughly USD 0.96 MM gap matches the Workstrings completion invoices. Whether those invoices were paid, waived, disputed or are still owed is unknown (`docs/gaps.md` G-64; `data/processed/database_review/acc_findings.md` §5). About USD 1.87 MM of TEC-11 cost was unpaid at the end of 2019 (`accounting_notes.md` §2).

## 5. Why the concept is still untested

1. **The lateral probably never reached its target rock.** The intent was the top of the El Abra. The sonic, the grid and the tops table all point to a lateral in or just above the overlying unit, and the only evidence of El Abra is the cuttings description. No resistivity was run over the lateral, so its saturation cannot be checked (G-75; `las_findings.md`).
2. **No pilot hole and no logs while drilling to steer on.** The operations log lists "wrong navigation", "well collapse (horizontal section)", "lack of logs" and "lack of pilot hole" (`docs/18_kinjal_briefing.md` A5).
3. **Mechanical failures took away the completion that had been designed.** The damaged liner hanger and failed tie-back stopped the selective tool, and the fish closed off the far 411 m. Only 5 intervals were perforated, against 10 (Jan 2019 deck) or 20 (cost plan) planned, all within 2,643.5–2,745.5 m. The acid went in without isolation.
4. **The water came through conduits the well design aimed at.** The operator's July 2019 post-mortem says "faults and fractures connect aquifer to oil column". The well was steered to cut those fractures, and the unisolated acid job probably opened them: "natural fractures could have been enhanced by acid stimulation" (`pres_findings.md` §4). The test therefore measured the aquifer's reach through fractures, not the deliverability of a lateral in reservoir rock.
5. **Nothing has replaced it.** TEC-12 was redesigned as a near-vertical S-shape well (`docs/Tecolutla_Field_History_and_TEC12_Review_v4.md` §6.2), so no horizontal well in the top of El Abra has ever been drilled at Tecolutla. The briefing's framing: "the concept was tested by a well that missed the target", which makes it an execution failure, not a negative reservoir test (A5, C6).

**Caveats.** Cuttings in a 90° hole can smear 5–15 m, and samples at 2,360–2,391 mMD were contaminated with cement and metal (`docs/03_tec11_facies.md` §5). The LWD sonic porosity (13–19 %) cannot be used quantitatively (`las_findings.md`). The plug depth, Tantoyuca interval and shoe in mSS are interpolated from the survey.
