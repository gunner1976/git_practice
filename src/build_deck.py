"""Task 10: build the handover presentation from the figures and task notes.
Usage: python src/build_deck.py  -> docs/Tecolutla_TEC12_Handover.pptx
"""
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BL = prs.slide_layouts[6]
def slide(title, bullets=None, fig=None, fig_w=8.3, notes=None, fig_left=None):
    s = prs.slides.add_slide(BL)
    tb = s.shapes.add_textbox(Inches(0.4), Inches(0.2), Inches(12.5), Inches(0.8)); p = tb.text_frame.paragraphs[0]; p.text = title; p.font.size = Pt(24); p.font.bold = True
    if fig:
        left = Inches(0.3) if fig_left is None else Inches(fig_left)
        s.shapes.add_picture(fig, left, Inches(1.0), width=Inches(fig_w))
    if bullets:
        x = Inches(0.3 + fig_w + 0.2) if fig else Inches(0.5); w = Inches(13.0 - (0.3 + fig_w + 0.2)) if fig else Inches(12.3)
        tb = s.shapes.add_textbox(x, Inches(1.0), w, Inches(6.2)); tf = tb.text_frame; tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = b; p.font.size = Pt(12 if fig else 14); p.space_after = Pt(6)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s
slide("Tecolutla / TEC-12 — technical handover on reconciled data", [
    "Contractual Area 24, Tampico-Misantla, Veracruz. Operator Tonalli Energía (IFR JV).",
    "Two deliverables: field history on reconciled data; TEC-12 new-drill justification.",
    "Everything traces to a file, sheet and cell: 150 source files (SHA256 manifest), ten task notes, 50-item gap register.",
    "Prepared by Kevin Gunning, P.Eng. Version 4 of the review, September 2026.",
    "Conventions: depths mMD / mSS as labelled; USD unless labelled CAD; pressures at 2,300 mSS; nothing interpolated."])
slide("1. What changed from version 3", [
    "Field cumulative: 1.72 MMbbl recorded + 0.43 MMbbl PEMEX wellfile allocations = the '2.0'. v3 table omitted TEC-7 (267 kbbl).",
    "Pressure: 24.65 MPa (1956, 2 h 45 min) to 24.15 MPa (2018, three wells) at 2,300 mSS: 2 % in 62 years; >99 % of voidage replaced by influx.",
    "Type curve: the 345-400 kbbl curve embeds PEMEX recompletions; TEC-10 declines with b 0.49 to ~100 kbbl. Range 65 / 218 / 366 kbbl.",
    "Target window 2,294-2,311 mSS: water at TEC-10 on core-supported porosity (Sw >= 1.1, no open fractures); at parity with the 353-kbbl producer at TEC-9 on an uncorrected 1973 sonic. Every barrel produced came from 2,303-2,332 mSS. Log and test the window at TEC-12 before completing (G-47).",
    "OOIP 7.8 (CNH) vs 11.2 (IFR) is petrophysics, not geometry: P90/P50/P10 8.1 / 10.0 / 12.2 MMbbl.",
    "AFE is USD 1,572,724 (deleted formula explains the 5,000); escalated base USD 1.97 MM / CAD 2.74 MM.",
    "Every IFR model since 2020 costs TEC-12 as a TEC-10 re-entry, not the S-shape AFE well.",
    "Rebuilt economics: incremental to a producing TEC-10, NPV10 +0.76 MM at WTI 70; stand-alone, break-even at WTI ~72."])
slide("2. Production database: 1,341 tidy rows, six sources, no interpolation", [
    "CNH monthly 1966-2016 (four wells), CNH field level 1960-65, Tonalli tests, TEC-10 daily 2018-19, trucking tickets, PEMEX statements.",
    "Recorded 1.72 MMbbl to Dec 2022; 0.48 MMbbl of the March 2020 By Zone total is wellfile allocation.",
    "GOR: cumulative 565 scf/bbl 1966-92 (the source of IFR's 552); PEMEX measured 685 on TEC-6 in 1964. Stock-tank oil 30-31 API (Intertek 2018-19, OCR). No lab Rs or Pb exists.",
    "No per-well data after Nov 2019: sales are commingled (G-32).",
    "66 runs of missing months in the CNH record cannot be told from shut-ins (G-34)."], "figures/04_production_history.png", 8.0)
slide("3. Pressure at one datum: strong aquifer, measurable decline", [
    "21 surveys 1956-2018 restated at 2,300 mSS; all 16 PEMEX scans OCR-verified (Tesseract + RapidOCR), one transcription error corrected.",
    "Initial 24.65 MPa is a 2 h 45 min reading on a new well; 1964 statics after 75-95 days agree.",
    "1971 TEC-6: 23.24 to 24.35 MPa between 4 and 74 days shut-in. Short shut-ins understate.",
    "2018: 24.14-24.16 MPa in three wells after ~2 MMbbl. Expansion alone would supply 11 kbbl.",
    "Both 2018 build-ups needed a constant-pressure boundary; TEC-10 also a no-flow boundary at 125 m.",
    "Recommendation 8 of v3 stands: the current shut-in is a free multi-year build-up. Measure it."], "figures/05_pressure_depletion.png", 7.6)
slide("4. TEC-11: 720 m of lateral, metres by facies", [
    "Carbonate from 2,360 mMD (2,245 mSS); lateral at 2,305-2,331 mSS, 4-12 m below the TEC-6/9 highest perforations.",
    "Lateral: 419 m mudstone-wackestone, 240 m grainstone-bearing (all mixed textures, compact), 31 m shale, 30 m bentonite.",
    "One moderate show (2,920-2,945 mMD); no show over 482 of 720 m.",
    "Facies, not depth. Exploration risk on a step-out, correctly taken and answered.",
    "Wording: 'wackestone to grainstone, compact', not 'miliolid grainstone' (G-27)."], "figures/03_tec11_lateral_facies.png", 8.2)
slide("5. Eleven economic models, one basis", [
    "Aug 2020, nine 'Feb 2022' (saved 11 Apr - 21 Jun 2022, suffixes out of order), Sept/Oct 2023.",
    "TEC-12 curve identical in all: qi 342, b 1.7, 300 bbl/d first month, 401 kbbl.",
    "What moved: WTI 30/90/GLJ deck/85; PEMEX factor 0.95/0.801/0.90 (unsourced); well count; window placement.",
    "v6-v9 exclude 3.45 MM of TEC-12/13 capital by placing it before the window.",
    "2023 workbook descends from the 2020 file and prices TEC-12 as a 1.8 MM TEC-10 re-entry.",
    "Use the 2023 structure with new capital, price and profile; retire the 2022 series as a reference."], "figures/02_econ_model_lineage.png", 8.2)
slide("6. Type curve and the TEC-12 range", [
    "Four PEMEX wells stacked by month on production reproduce the IFR workbook; the average rises again at months 100-130 and 250-300 as wells were re-perforated.",
    "TEC-10 (single completion, daily data): 181 bbl/d first full month, 78 at 12 months, ~21 at 45 months; b 0.49; ~104 kbbl.",
    "GLJ YE2020: 203 / 343 / 502 kbbl; Petrel Robertson 100 bbl/d base, 200 upside; Simmons volumes include TEC-13.",
    "Recommended: low 100 bbl/d, 65 kbbl; base 180 bbl/d, b 0.9, 218 kbbl; high 300 bbl/d, 366 kbbl.",
    "The 345 kbbl becomes the P10, requiring a PEMEX-style 30-year life with recompletions."], "figures/06_type_curve_forecast.png", 8.4)
slide("7. OOIP: 7.8 vs 11.2 is petrophysics", [
    "7.8 MMbbl = PEMEX/CNH booked volume (3.1 km2). 11.2 = IFR, 630 ac, N/G 0.40, phi 7 %.",
    "Petrel Robertson geomodel: 7.6 with TEC-2/9 vintage-log petrophysics, 12.0 with TEC-10's logs, same rock volume.",
    "Monte Carlo P90/P50/P10: 8.1 / 10.0 / 12.2 MMbbl. Porosity and N/G swing +-2.5 MMbbl each.",
    "Tecolutla holds 2.5 MMbbl/km2 vs a reef-rim median of 8.3; RF to date 25 % (CNH) or 20 % (P50) vs trend 30 %.",
    "Remaining at 29 %: 0.3 (CNH) / 0.9 (P50) / 1.3 (IFR) MMbbl. TEC-12's logs are the appraisal of this 4 MMbbl spread."], "figures/07_volumetrics.png", 8.4)
slide("8. Logs on one datum: GR polarity and the target window", [
    "GR rises with porosity in every well (Spearman +0.28 to +0.49): clean GR = tight miliolid facies.",
    "Produced intervals: TEC-6 2,308-2,332, TEC-9 2,323-2,328, TEC-2 2,303-2,307, TEC-10 2,314-2,318 mSS.",
    "Target window 2,294-2,311 mSS: TEC-10 phi 9-11 %, ILD 4-5 ohm.m, N-D separation, PE 3.8, Archie Sw ~1; TEC-9 ILD 3-5 ohm.m.",
    "Resistivity rises to 15-50 ohm.m below ~2,310 mSS in both wells; Tonalli did not perforate the upper zone after logging it.",
    "Free water or clay-bound water in an argillaceous carbonate: the logs alone cannot say. Core-calibrated evaluation of TEC-10 before sanction (G-47).",
    "TEC-10 top perf is 2,314 mSS on the survey vs 2,311.5 in the summary sheet (G-46)."], "figures/09_log_panel.png", 8.6)
slide("9. AFE: USD 1,572,724, priced on 2018 rates", [
    "Sep 2021 copy shows 1,567,724 because the SUB formula on Drilling Pad Maintenance (5,000) was deleted; daily totals still include it.",
    "Rig and move 27 %, tubulars and wellhead 23 %, mud and disposal 18 %; day rates identical to the TEC-11 Dec-2018 tracker.",
    "No contingency, no production casing, no owner's costs. TEC-11 came in +12 % over budget.",
    "Currency USD by evidence (Tonalli cost format 'Dolares', models in US$); author to confirm (G-44).",
    "Escalated to Sep 2026 (assumed x1.15 / 1.25 / 1.40; index blocked, G-45): USD 1.81 / 1.97 / 2.20 MM = CAD 2.52 / 2.74 / 3.06 MM at 1.3915."], "figures/08_afe.png", 8.4)
slide("10. Economics rebuilt on the 2023 structure", [
    "Fiscal and cost terms from the 2023 workbook; base profile; escalated base AFE; water cut following TEC-10; start Jan 2027; 100 % WI; no G&A, no carry.",
    "Stand-alone NPV10 BTAX at WTI 60/70/80: base -0.62 / -0.09 / +0.46 MM; high +0.03 / +0.77 / +1.53; low never positive.",
    "Incremental to a producing TEC-10 (battery and disposal already carried): base +0.06 / +0.76 / +1.41 MM, payout < 2 years at WTI 70.",
    "Royalty burden 42-44 % of revenue; fixed costs end the stand-alone base case at 69 months with 142 of 218 kbbl produced.",
    "WTI ~USD 100 in mid-Sep 2026 on a supply disruption; long-term decks 70-80. 2025 fiscal reform not reviewed (G-49).",
    "v3's overhead finding stands: the well works for an operator that already carries the field, not for a single-asset company."], "figures/10_econ_rebuild.png", 8.2)
slide("11. New sources read in the second pass: CNH polygon, CMI fractures", [
    "Ten large Drive files read through the connector's text rendering (Work Program, GLJ detail, core report, mud logs, gauge data): docs/12.",
    "CNH field polygon (2015 data room): 3.14 km2, all nine wells inside; IFR's 630 ac = 2.55 km2 is 81 % of it. An administrative outline, the upper bound of the OOIP range (G-43 closed).",
    "CNH forecast tables filed for 2021 and 2022 carry the IFR 2020 TEC-12 curve (300 bbl/d first month), not 500 kbbl (G-22 closed).",
    "CNH annual filings: 16.1 kbbl (2020, both wells, Apr-Jun shut in), 17.4 kbbl (2021, TEC-10 only, GOR 859 scf/bbl, 29.3 API); field shut in from Jul 2022, restarted late Nov 2022 on TEC-10.",
    "TEC-10 core (only rock data): recrystallised grainstone, 2-8 % porosity, 0.01-0.5 mD at stress, 14-59 % PV residual oil; no electrical properties.",
    "CMI (right): no open fracture in the TEC-12 window or the perforated 10 m; open fractures start below 2,320 mSS in the produced, water-bearing interval. TEC-10 is matrix flow (G-09 closed).",
    "Sw sensitivity (72 cases, anchored to the aquifer and the producing interval): the window is water at TEC-10 on the core-supported density porosity, Sw >= 1.1 vs 0.6-1.0 in the perforations; N-D crossover flips sign at 2,311 mSS. At TEC-9 (118 m from TEC-12) the 1973 sonic puts the window at parity with the 353-kbbl producer unless 20 %+ of its porosity is shale effect. Base case on 2,311-2,332 mSS; log and test the window at TEC-12 before completing (docs/14).",
    "2025 reform: contract fiscal terms preserved per secondary sources; regulator now CNE; contract-to-assignment substitution clause to be checked by counsel (G-49)."], "figures/14_cmi_fractures.png", 6.6)
slide("12. Decisions and the gap register", [
    "Before sanction: (1) core-calibrated petrophysics of TEC-10's upper zone (G-47); (2) static gradient on TEC-10 after the multi-year shut-in; (3) confirm AFE currency and re-index escalation (G-44, G-45); (4) pull the ten large-file binaries into data/raw (G-52; their text was read, docs/12).",
    "If the window is water: move the target to 2,311-2,332 mSS (the produced interval in every well) and re-run the base case.",
    "Quote volumes as: recorded 1.72 MMbbl; OOIP 8-10-12; TEC-12 65/218/366 kbbl; AFE USD 1.57 MM (2020) / ~2.0 MM (2026).",
    "Wording fixes for any external document: CMI not FMI; 'wackestone to grainstone, compact'; 'within 2 % of initial pressure'; Simmons volumes are two wells.",
    "53 gaps logged in docs/gaps.md with status; 15 remain open. Kevin: the Aug-2025 re-saves (G-03), which well the 2023 model priced (G-17), AFE currency (G-44), the 2020 CNH filing gross-vs-net oil (G-53), a Drive API pull or manual download of the ten large binaries (G-52)."])
prs.save("docs/Tecolutla_TEC12_Handover.pptx"); print("deck saved", len(prs.slides), "slides")
