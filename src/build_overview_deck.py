"""Task 19: technical overview deck for an external engineering review (Kinjal, Oct 2026).
Usage: .venv/bin/python src/overview_figures.py && .venv/bin/python src/build_overview_deck.py
       -> docs/Tecolutla_Technical_Overview.pptx
Every number on a slide is from the repository (docs/, data/processed/) or the Drive files it cites; the
speaker notes of each slide carry the questions a reviewing engineer is likely to ask, with the answers and sources.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = "data/processed/deck_notes/img/"
prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BL = prs.slide_layouts[6]
INK = RGBColor(0x0b, 0x0b, 0x0b); INK2 = RGBColor(0x52, 0x51, 0x4e); ACC = RGBColor(0x2a, 0x78, 0xd6)
N = [0]
FOOT = "Tecolutla field, Contract Area 24 - technical overview, October 2026"

def _title(s, title):
    tb = s.shapes.add_textbox(Inches(0.4), Inches(0.15), Inches(12.5), Inches(0.8)); tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]; p.text = title; p.font.size = Pt(22 if len(title) <= 75 else 18); p.font.bold = True; p.font.color.rgb = INK
    N[0] += 1
    fb = s.shapes.add_textbox(Inches(0.4), Inches(7.05), Inches(10), Inches(0.3)); q = fb.text_frame.paragraphs[0]
    q.text = FOOT; q.font.size = Pt(8); q.font.color.rgb = INK2
    fb = s.shapes.add_textbox(Inches(12.3), Inches(7.05), Inches(0.9), Inches(0.3)); q = fb.text_frame.paragraphs[0]
    q.text = str(N[0]); q.font.size = Pt(9); q.font.color.rgb = INK2

def _bullets(s, x, y, w, h, bullets, fs):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(b, tuple):  # (bold lead, rest)
            r = p.add_run(); r.text = b[0]; r.font.bold = True; r.font.size = Pt(fs); r.font.color.rgb = INK
            r = p.add_run(); r.text = b[1]; r.font.size = Pt(fs); r.font.color.rgb = INK
        else:
            p.text = b; p.font.size = Pt(fs); p.font.color.rgb = INK
        p.space_after = Pt(5)

def slide(title, bullets=None, fig=None, fig_w=8.3, notes=None, size=None, fig_top=1.0):
    s = prs.slides.add_slide(BL); _title(s, title)
    if fig:
        pic = s.shapes.add_picture(str(ROOT / fig), Inches(0.3), Inches(fig_top), width=Inches(fig_w))
        if pic.height > Inches(5.9):  # keep tall figures clear of the footer
            pic.width = int(pic.width * Inches(5.9) / pic.height); pic.height = Inches(5.9)
        fig_w = pic.width / 914400
    if bullets:
        x = 0.3 + fig_w + 0.2 if fig else 0.5; w = 13.0 - x if fig else 12.3
        _bullets(s, x, 1.0, w, 6.0, bullets, size or (11 if fig else 14))
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def wide_fig(title, fig, bullets, notes=None, fig_w=12.4, fig_h=None, size=11):
    """Figure across the top, bullets in two columns underneath."""
    s = prs.slides.add_slide(BL); _title(s, title)
    pic = s.shapes.add_picture(str(ROOT / fig), Inches(0.45), Inches(0.95), width=Inches(fig_w)) if not fig_h else \
          s.shapes.add_picture(str(ROOT / fig), Inches(0.45), Inches(0.95), height=Inches(fig_h))
    top = 0.95 + pic.height / 914400 + 0.1
    half = (len(bullets) + 1) // 2
    _bullets(s, 0.5, top, 6.1, 6.9 - top, bullets[:half], size)
    _bullets(s, 6.8, top, 6.1, 6.9 - top, bullets[half:], size)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def table(title, header, rows, colw=None, bullets=None, fs=10, notes=None, top=1.0, bw=4.0):
    s = prs.slides.add_slide(BL); _title(s, title)
    tw = 12.4 if not bullets else 12.4 - bw - 0.2
    shp = s.shapes.add_table(len(rows) + 1, len(header), Inches(0.45), Inches(top), Inches(tw), Inches(0.3 * (len(rows) + 1))); t = shp.table
    if colw:
        for j, cw in enumerate(colw): t.columns[j].width = Inches(cw)
    for j, hdr in enumerate(header):
        c = t.cell(0, j); c.text = str(hdr)
        for p in c.text_frame.paragraphs: p.font.size = Pt(fs); p.font.bold = True
    for i, r in enumerate(rows, 1):
        for j, v in enumerate(r):
            c = t.cell(i, j); c.text = "" if v is None else str(v)
            for p in c.text_frame.paragraphs: p.font.size = Pt(fs)
    if bullets:
        _bullets(s, 0.45 + tw + 0.2, top, bw, 6.0, bullets, 10.5)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def two_figs(title, figs, widths, bullets=None, notes=None, size=10):
    s = prs.slides.add_slide(BL); _title(s, title)
    x = 0.3
    for f, w in zip(figs, widths):
        s.shapes.add_picture(str(ROOT / f), Inches(x), Inches(1.0), width=Inches(w)); x += w + 0.2
    if bullets:
        _bullets(s, x, 1.0, 13.0 - x, 6.0, bullets, size)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def Q(*pairs):
    """Speaker notes: anticipated questions with answers."""
    return "\n\n".join(f"Q: {q}\nA: {a}" for q, a in pairs)

# ============================ 1. Title ============================
s = prs.slides.add_slide(BL); N[0] += 1
tb = s.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(11.5), Inches(1.4)); tb.text_frame.word_wrap = True
p = tb.text_frame.paragraphs[0]; p.text = "Tecolutla Field, Contract Area 24 (Veracruz, Mexico)"; p.font.size = Pt(32); p.font.bold = True; p.font.color.rgb = ACC
p = tb.text_frame.add_paragraph(); p.text = "Technical overview"; p.font.size = Pt(24); p.font.color.rgb = INK
_bullets(s, 0.8, 3.9, 11.5, 2.5, [
    "Prepared for Kinjal - October 2026",
    "Kevin Gunning, P.Eng.",
    "Depths in m subsea (mSS) unless marked mMD; pressures at 2,300 mSS; USD. Sources for every figure are in the speaker notes and the data package."], 14)
s.notes_slide.notes_text_frame.text = "Purpose: a technical walk-through of the field, the 2018-19 programme and the remaining opportunity (TEC-12), with the data behind each statement. Every slide's notes list the questions we expect and the answers."

# ============================ 2. At a glance ============================
table("Tecolutla at a glance", ["Item", "Value", "Source"], [
    ["Setting", "SE end of the Golden Lane (Faja de Oro) El Abra reef rim, Tampico-Misantla basin; ~60 km ESE of Poza Rica", "PEMEX field summary; 2017 evaluation plan"],
    ["Contract", "CNH-R01-L03-A24/2016 licence (Round 1.3, Aug 2016); operator Tonalli Energía; 7.2 km²", "contract; CNH"],
    ["Reservoir", "El Abra (Middle Cretaceous) reef-margin grainstone-packstone; top 2,294-2,310 mSS across the wells", "well tops, GLJ YE2019 map"],
    ["Field area / OOIP", "2.5-3.1 km²; 7.8 MMbbl (PEMEX/CNH booked), 11.2 MMbbl (IFR), P50 10.0 MMbbl", "docs/07_volumetrics.md"],
    ["Produced", "1.98 MMbbl to end-2022 (about 20-25 % of OOIP); peak 932 bbl/d (Mar 1972)", "docs/04; PEMEX summary"],
    ["Drive", "Strong bottom-water aquifer: ~70 psi decline in 62 years", "docs/05_pressure.md"],
    ["Oil", "26.5-31 °API, 1.6-1.9 % S; GOR ~560-860 scf/bbl; sour gas (H2S 0.7-1.7 mol %)", "lab analyses; CNH filings"],
    ["Wells", "7 PEMEX wells 1956-73 (4 producers); TEC-10DES and TEC-11DES drilled 2018", "well files"],
    ["Status (latest in files, 2022)", "TEC-10 and TEC-2 producible, TEC-7 water disposal; TEC-12 approved in the 2022 transition programme, not drilled", "CNH filings"],
], colw=[2.0, 7.2, 3.2], fs=10,
    notes=Q(("How big is it really?", "Small: 2.5-3.1 km², OOIP 7.8-11.2 MMbbl, ~2 MMbbl produced. Remaining recoverable 0.3-1.6 MMbbl, most likely ~0.9 MMbbl at the reef-rim trend recovery (docs/07_volumetrics.md)."),
              ("Who has interests?", "Tonalli Energía operates the licence; IFR/Petro Frontera and Jaguar (from Aug 2022) are the partners. Confirm current equity before the meeting.")))

# ============================ 3. Regional ============================
two_figs("Regional setting: a small high on the Golden Lane reef rim", [IMG + "resumen_campo_03_Figura_iii_1_Secci_n_s_smica_regional_en_tiempo_en_direcci_n.jpeg", IMG + "resumen_campo_05_Figura_iv_1_Secci_n_del_S_smica_del_Campo_Tecolutla_con_el_m.png"], [4.3, 3.9], [
    "Golden Lane: an Early-Cretaceous carbonate atoll about 150 × 70 km and 1,200 m thick, rimming the Tuxpan platform; reef facies on the outer edge.",
    "Tecolutla sits at the SE end of the onshore rim, between the Miguel Hidalgo block (NW) and Ignacio Allende (SE); same El Abra play as the giant Golden Lane fields, at a much smaller scale.",
    "End-Albian exposure improved reservoir quality (karst, recrystallisation); Tertiary Tantoyuca rests directly on the El Abra over the crest (unconformity).",
    "Left: PEMEX regional time section across the platform edge. Right: field section with the facies model (basin, slope, reef barrier, back-reef, inner platform).",
    "Analogues: 45 El Abra fields in the CNH table; reef-rim median recovery 31 % (3P EUR); Tecolutla has 2.5 MMbbl/km² against a median 8.3."], size=10,
    notes=Q(("What is the seal and source?", "No project document names them. Regionally the seal is the Tertiary shale over the unconformity (Tantoyuca/Chicontepec) and the source is Upper Jurassic. Cite as regional literature, not field data."),
              ("Why is it so much poorer than the Golden Lane giants?", "Lower porosity and net-to-gross in the recrystallised miliolid facies (2-11 % porosity, matrix 0.04-1.2 mD on core); it is a small culmination of 10-25 m relief. Volumes are set by porosity and N/G, not area (task 7).")))

# ============================ 4. Structure ============================
two_figs("Structure and well locations", [IMG + "resumen_campo_04_Figura_iii_2_Mapa_estructural_en_profundidad_del_yacimiento.jpeg", IMG + "elabra_depth_tec12_s01_top_el_abra_depth_map_TVDSS_5m.png"], [3.6, 4.6], [
    "NW-SE elongated culmination on the reef rim; normal faults on both flanks parallel to the axis (PEMEX); no faults between TEC-6 and TEC-9 (Petrel Robertson).",
    "Top El Abra (mSS): TEC-6 2,294; TEC-9 2,296; TEC-2 2,300-2,302; TEC-7 2,304; TEC-10 2,307-2,310; TEC-11 2,312. The crest is at TEC-6/TEC-9.",
    "Tonalli 2020 map (right, 5 m contours, reprocessed 3D): culminations of ~2,290 m at TEC-6/TEC-9 and at TEC-2; relief across the drilled area 10-25 m.",
    "Flank wells TEC-3 (NE), TEC-5 (NW) and TEC-101 found the El Abra low and wet; they define the edges.",
    "TEC-12 location: on the crest between TEC-6/TEC-9 and TEC-10, 118 m from TEC-9 and 175 m from TEC-10."], size=10,
    notes=Q(("How reliable is the depth map?", "PEMEX 2011 PSTM, reprocessed by Earth Signal in 2018 and interpreted in Petrel; the velocity tie is to Miguel Hidalgo, not to a Tecolutla checkshot. TEC-10 came in a few metres low against prognosis. Well control is good on the crest; flanks rely on seismic. The SEG-Y and Petrel project are with Tonalli/Jaguar, not in our package (G-55)."),
              ("Where is the oil-water contact?", "Not a single flat number. Statements in circulation: 'water at 2,350 m' (2017 plan), wet TEC-2 perforations at 2,331-2,345 mSS, lowest known oil -2,374 mSS (GLJ, used for OOIP). Production history shows water coning around producers rather than a flat rising contact (slide 8).")))

# ============================ 5. Rock and fluids ============================
table("Reservoir rock and fluids", ["Property", "Value", "Basis"], [
    ["Facies", "Recrystallised miliolid grainstone to mudstone-wackestone; high GR marks the porous facies (not shale)", "TEC-10 core and logs; TEC-11 mud log"],
    ["Porosity", "2-11 %; producing intervals 5-6 %", "logs; TEC-10 core plugs 2.3 / 6.7 / 7.6 %"],
    ["Permeability", "Matrix 0.04-1.2 mD (core); 18 mD effective from the TEC-10 build-up", "core; IHS 2018 PTA"],
    ["Fractures", "0-7 open/mixed fractures per metre on the TEC-10 image log", "Weatherford CMI 2,296-2,488 mMD"],
    ["Initial pressure", "252 kg/cm² (24.7 MPa) at ~2,310 m, 1956", "PEMEX drilling report TEC-2"],
    ["Temperature", "~98-99 °C at reservoir", "log headers"],
    ["Oil", "26.5-31 °API; 1.6-1.9 % S; 13.7-18.7 cSt at 40 °C (dead); pour point -24 °C", "SGS, Intertek, PEMEX settlements"],
    ["Gas", "GOR 560 (1966-92), 762 (2018 test), 859 (2021) scf/bbl; H2S 0.66-1.75 mol %, CO2 ~11 %", "lab gas analyses; CNH filings"],
    ["Water", "Formation water ~45,000-50,000 ppm", "PEMEX 1956 tests"],
    ["Wax", "Paraffin deposits in tubing (TEC-2, 2018); handled with periodic solvent clean-ups", "Tonalli operations log"],
    ["PVT", "No laboratory PVT study exists; correlations and a PEMEX analogue only", "G-31"],
], colw=[1.9, 6.6, 3.9], fs=9.5,
    notes=Q(("Is there a PVT?", "No measured PVT (bubble point, Rs, Bo). A bottom-hole or recombined sample should be part of TEC-12."),
              ("Matrix permeability is sub-millidarcy - how does it flow?", "Through fractures and vugs. The TEC-10 build-up gives 18 mD effective; the image log shows up to 7 fractures/m. That is also why water moves fast along fractures and the wells cone."),
              ("H2S handling?", "Sour service: separator gas 0.7-1.7 mol % H2S. Gas is flared under the evaluation-period approval; H2S detection and SCBA are in the SASISOPA.")))

# ============================ 6. Aquifer ============================
slide("Drive mechanism: a strong bottom-water aquifer", [
    ("Pressure barely moved. ", "24.65 MPa (1956) → 24.4-24.7 (1964) → 24.5 (1998) → 24.14-24.16 MPa (2018) at 2,300 mSS: about 0.5 MPa (70 psi) after ~1.9 MMbbl and 62 years."),
    ("Transients see it. ", "Both 2018 build-ups needed a constant-pressure boundary to match late time: 195 m from TEC-10, 700 m from TEC-2."),
    ("Water behaviour. ", "Every well watered out; PEMEX shut TEC-2 and TEC-7 in 1957-71 'for high salt-water content' and re-perforated higher."),
    ("Consequences. ", "Voidage is replaced, so recovery is about sweep and water management, not pressure support. Rate per well is limited by coning, and water handling is the main operating cost."),
    ("Implication for new wells. ", "Low drawdown, completion high in the column, and in-field water disposal."),
], fig="figures/05_pressure_depletion.png", fig_w=7.4,
    notes=Q(("How confident is the pressure data?", "18 PEMEX survey forms were OCR'd and checked against IFR's transcription (15 of 16 agree to the last digit), plus the 2018 Tonalli gradient and two IHS build-ups. All corrected to 2,300 mSS at 10.5 kPa/m (docs/05_pressure.md)."),
              ("Could it be a gas cap and not an aquifer?", "No: pressure maintenance with rising water cut in every well is aquifer behaviour. There was a small gas cap at the crest in 1956 (TEC-2 top test, GOR ~6,500 scf/bbl), which is a separate point for TEC-12 (slide 17).")))

# ============================ 7. Production history ============================
slide("Production history: 1956-2022", [
    "1956-1965: four wells flow from the El Abra; TEC-2 and TEC-7 shut in for salt water from 1957, TEC-6 carries the field.",
    "1971-72 workovers re-perforate TEC-2 and TEC-7 higher; field peak 932 bbl/d in March 1972; TEC-9 drilled 1973.",
    "1973-2012: decline with rising water cut; intermittent operation; TEC-9's second life 2003-2012.",
    "2016: PEMEX hands over; 1.9 MMbbl produced; field shut in Feb 2016 - mid 2018.",
    "2018-2022: Tonalli/IFR programme. TEC-10 75.8 kbbl to Dec 2021 (first full month 181 bbl/d); TEC-2 10.0 kbbl since 2018; PEMEX-measured sales 63 kbbl Sep 2018 - Nov 2020.",
    "GOR stable at 400-800 scf/bbl through 1966-92 (cumulative 565); no sign of a gas-cap blow-down.",
], fig="figures/04_production_history.png", fig_w=8.0, size=11,
    notes=Q(("Why the gaps in the record?", "Gaps are months missing from the CNH per-well series. The PEMEX well files show most pre-1985 gaps were shut-in or workover months (e.g. TEC-2/TEC-7 shut in for salt water 1957-71). Post-1985 gaps are unexplained (G-34)."),
              ("What is the Tonalli-era per-well split after 2019?", "Field sales 2020-22 are commingled tickets (~90 % TEC-10 by the 2021 CNH filing). Per-well CNH formats exist only for Nov 2022 in our package (G-32).")))

# ============================ 8. Interval ladder ============================
slide("How the field was produced: each well chased the water upward", [
    "TEC-6, TEC-2 and TEC-7 each moved 10-25 m up the column as the bottom water arrived (faded bars = earlier intervals).",
    "TEC-9 is the exception: 353 kbbl from one interval 27-32 m below its top El Abra, never re-perforated.",
    "The water did not rise as a flat plane: TEC-10 (2018) found an oil-bearing interval at 2,314-2,318 mSS, 7-11 m below the last TEC-2/TEC-7 intervals, and produced it at 30-60 % oil cut.",
    "Water advances by coning and along fractures around each producer, which leaves oil between and above the old wells.",
    ("Under-exploited top of the zone: ", "the crest wells left the top of the El Abra unperforated, 14 m at TEC-6 (2,294-2,308 mSS) and 27 m at TEC-9 (2,296-2,323 mSS). Nothing has produced from 2,294-2,303 mSS anywhere in the field."),
], fig="figures/22_interval_ladder.png", fig_w=8.6, size=10.5,
    notes=Q(("Is the 'oil deeper than last produced' claim fair given TEC-9?", "Yes against TEC-2 and TEC-7, which were last producing from 2,303-2,308 mSS. TEC-9 produced deeper (2,323-2,328) until 2012. The point is that the oil column is still there between the old producers, not that oil is deeper than anything produced."),
              ("TEC-7 tested 100 % water at 2,305-2,308 in 2019 - doesn't that say the top is wet?", "Tonalli suspected bad cement or a leaking plug giving access to the lower perforations (Sep 2022 review). TEC-2, 1-7 m below its top, still makes oil at 72-90 % water cut. Both are flank-side of the crest."),
              ("Sources?", "docs/09_log_panel.md §3 (one datum); perforations CSV; PEMEX expedientes; Tonalli operations log; GLJ/XS top picks.")))

# ============================ 9. 2018-19 programme ============================
table("IFR/Tonalli programme 2018-2019: what was done and what it showed", ["Well", "Work", "Result", "What it told us"], [
    ["TEC-10DES (Apr-May 2018)", "New J-shape well from a new pad; modern logs (incl. image log), core at 2,352 m, three zones tested", "Zones A/B (2,394-2,442 mMD) tight, no flow. Zone C 2,314-2,318 mSS: 182 bbl/d oil at 39 % WC, ~880 psi FTP; 75.8 kbbl to Dec 2021", "Oil column intact below the last PEMEX intervals; flowing well"],
    ["TEC-2 (2018, 2019)", "Wellhead repair, clean-out (paraffin); 2019 add-perf 2,315-2,316 mSS and plug over wet deep perfs", "2018: 50 bbl/d oil at 90 % WC; 2019: 47 bbl/d at 75 % WC, ~250 psi; 10.0 kbbl since 2018", "Old wells can be restored; water shut-off pays"],
    ["TEC-7 (Jun-Aug 2019)", "Workover, acid; tested 2,305-2,308 mSS", "182 bbl/d water, no oil", "Converted to produced-water disposal (triplex pump, ASEA-authorised)"],
    ["TEC-11DES (Nov-Dec 2018)", "720 m open-hole horizontal from the TEC-2 pad, aimed at the top of the zone for low drawdown", "Lateral at 2,305-2,331 mSS in tight mudstone; open hole lost; liner perfs 286 bbl/d water", "Execution failure; the concept is untested (slide 12)"],
    ["Facilities (2019)", "TEC-10 to TEC-2 flowline; separator purchased; in-field disposal", "One battery; water trucking ended Aug 2019", "Field opex down by about two-thirds (slide 13)"],
], colw=[1.9, 3.6, 3.9, 3.0], fs=9.5,
    notes=Q(("Why didn't TEC-10's deeper zones flow?", "Zones A/B (2,394-2,442 mMD) are tight, low-porosity El Abra below the producing column; the 2018 injectivity test needed 2,120 psi to admit fluid. They were isolated below a bridge plug at 2,382 m."),
              ("What did the programme cost?", "TEC-10 actual USD 2.04 MM against a 2.92 MM AFE; TEC-11 USD 3.03 MM against 2.25 MM (drilling cost to rig release)."),
              ("Sources", "Activities performed in Tecolutla.xlsx (Tonalli operations log); Tecolutla Discussion with Jaguar, 1 Sep 2022; TEC-10/TEC-11 cost trackers.")))

# ============================ 10. TEC-10 ============================
slide("TEC-10DES: confirming the oil column between the old producers", [
    "J-shape well from a new pad beside TEC-6, 193 m step-out to the south; top El Abra 2,307-2,310 mSS.",
    "Modern suite: triple-combo, dipole sonic, Weatherford CMI image log; 10 m core at 2,352 mMD (grainstone, 2-8 % porosity, Dean-Stark oil 14-59 % PV).",
    "Perforated 2,349.5-2,353 mMD (2,314-2,318 mSS) at the resistivity break (4-5 → 15-50 ohm·m), acidised, flowed.",
    "Test: 182 bbl/d oil, 118 bbl/d water, 146 Mcf/d, ~880 psi flowing (Jul 2018); IHS build-up: k 18 mD, skin +5, aquifer boundary at 195 m.",
    "Production: 181 bbl/d first full month; qi 152 bbl/d, b ≈ 0.5 decline; 75.8 kbbl to Dec 2021, last rate 34 bbl/d at 86 % WC; flowing throughout, kept on with solvent clean-ups.",
    "Lesson for TEC-12: log and core before perforating; low-GR intervals are the tight rock here, high-GR the porous rock."], fig="figures/09_log_panel.png", fig_w=7.6, size=10.5,
    notes=Q(("Why only 3.5 m perforated?", "Tonalli perforated the high-resistivity interval directly below the porosity/resistivity break; the porous low-resistivity zone above was judged wet or shaly (slide 17)."),
              ("What was the decline?", "Hyperbolic fit qi 152 bbl/d, Di 0.79/yr, b ≈ 0.49 on 15 months of daily data plus 2020-22 sales (docs/06_forecast.md)."),
              ("Why is it shut in?", "Shut in Feb 2022 (rate and cash), restarted Nov 2022 on TEC-10 alone; Tonalli noted a stimulation needed on restart.")))

# ============================ 11. TEC-2 / TEC-7 / operating practice ============================
slide("Restoring old wells and running the field", [
    ("TEC-2 restart. ", "2018 clean-out found paraffin in the tubing; 7-day test 50 bbl/d oil at 90 % WC. 2019: add-perf at 2,315-2,316 mSS, permanent plug at 2,322.5 mMD to shut off wet deeper perforations; 69-day test 47 bbl/d at 75 % WC."),
    ("TEC-2 operating practice. ", "Produced in cycles: on until the water cut climbs, shut in to let the cone subside, then back on; last reported 18 bbl/d oil at 72 % WC (Sep 2020)."),
    ("TEC-7 disposal. ", "Tested 100 % water in 2019; converted to produced-water injection by triplex pump from 7 Aug 2019 under ASEA authorisation 1712/2019. Indicative injectivity 0.5-1 bbl/min at under 450 psi on the 2019 job."),
    ("TEC-10 flowing. ", "Natural flow from 880 psi (2018) declining; no artificial lift needed to date."),
    ("Solvent clean-ups. ", "Aromatic solvent jobs (2-3 m³ APSOL-AP) to remove wax from tubing and the near-wellbore: six jobs in 2019, four on TEC-10 and two on TEC-2, repeated as needed; oil cut and rate recover for a period after each job."),
    ("Water handling. ", "TEC-10 production flows to the TEC-2 battery (2 in, 504 m line); separation, tankage, crude trucked to PEMEX; water to TEC-7."),
], size=13,
    notes=Q(("What is APSOL-AP?", "Química Apollo's aromatic organic system (Kevin: confirm the composition, usually xylene-based, before calling it xylene)."),
              ("Is there evidence the solvent jobs work?", "Operating experience: rate and oil cut recovered after jobs. The daily data for 2019 are in the TEC-10 daily file (data/processed/tecolutla_tec10_daily.csv) if a before/after plot is requested."),
              ("Is the TEC-2 cycling documented?", "The 2018-2020 tests and rates are documented; the on/off schedule is operating practice, not a separate dataset. Per-well volumes after Nov 2019 are commingled (G-32)."),
              ("How much water can TEC-7 take?", "No long-term injection log is in our package (G-57). The 2019 stimulation job pumped 0.5-1 bbl/min at 250-440 psi surface pressure; the 2020-21 ASEA compliance reports confirm continuous injection.")))

# ============================ 12. TEC-11 ============================
slide("TEC-11DES horizontal: the concept and why the well did not test it", [
    ("Concept. ", "A 720 m open-hole lateral in the top of the El Abra from the TEC-2 pad: low drawdown along a long contact to delay water coning."),
    ("What was drilled. ", "Lateral at 2,305-2,331 mSS (mostly 2,322-2,324), 4-12 m below the TEC-6/TEC-9 high, through 923 m of mostly mudstone-wackestone."),
    ("Execution problems. ", "Navigation below plan, no pilot hole and no logs while drilling, hole collapse in the lateral, failed tie-back and liner cement job, fish; the open-hole section could not be re-entered."),
    ("Test. ", "Liner perforations 2,674-2,745 mMD flowed 286 bbl/d water, no oil; Tantoyuca recompletion trace 17 °API oil; composite plug at 2,400 m (Aug 2019)."),
    ("Lessons applied to TEC-12. ", "A conventional deviated well to the crest, a full open-hole log suite before completion, and perforations chosen on the logs."),
], fig="figures/03_tec11_lateral_facies.png", fig_w=6.8, size=11,
    notes=Q(("Does TEC-11 condemn the top-of-zone idea?", "No. The lateral sat 4-12 m below the crest in tight mudstone facies and the open hole was never tested; the water came through liner perforations near 2,322-2,331 mSS."),
              ("What did it cost?", "USD 3.03 MM to rig release against a 2.25 MM AFE."),
              ("Source", "docs/03_tec11_facies.md; Rise Energy mud log; Tonalli operations log; Sep 2022 Jaguar review.")))

# ============================ 13. Opex ============================
wide_fig("Operations and opex: logistics brought field costs down by two-thirds", "figures/23_field_opex.png", [
    ("2019, two wells on test: ", "USD 54-83 k/month field opex (839 k for the year, 25.6 USD/bbl), with a rented separator (MXN 216 k/month) and water trucked out."),
    ("Changes: ", "TEC-7 disposal (Aug 2019, water trucking ends); TEC-10 to TEC-2 flowline and one battery (Nov 2019); separator bought, rental ended Mar 2020; TEC-2 shut in when uneconomic."),
    ("Sep 2020 run-rate: ", "about USD 28 k/month: crew MXN 280 k, vacuum truck 108 k, diesel 60 k, frac tank 32 k, consumables and lab; roughly 13-16 USD/bbl at 2020 volumes."),
    ("Crude logistics: ", "trucked to PEMEX at CAB Poza Rica; demulsifier treatment and monthly crude-quality analyses; PEMEX fixed tariffs 2.7-3.3 USD/bbl."),
], fig_h=4.0, size=10.5,
    notes=Q(("Are these audited numbers?", "2018-19 are monthly management actuals from the Tonalli budget-to-actual workbook; Sep 2020 is a cost sheet. 2020-21 audited actuals are not in our package (G-56)."),
              ("What is the all-in cost?", "Field opex excludes G&A (USD 674 k in 2019; corporate administration USD 39 k/month in the 2022 CNH report) and regulatory costs (exploration fee and activity tax ~USD 1.1 k/month)."),
              ("What opex does the TEC-12 case assume?", "7.25 USD/bbl oil + 3.25 USD/bbl water + 2,500 USD/well/month + 10 k battery + 1.5 k disposal per month (2023 model terms), consistent with the 2020 run-rate.")))

# ============================ 14. Wellbores ============================
slide("Wellbores: all nine wells documented", [
    "PEMEX wells: 9 5/8 in surface casing at 500-610 m (807 m at TEC-101), 6 5/8 in production casing to ~2,300 m, 4 1/2 in liners across the El Abra (TEC-2, TEC-6, TEC-7); TEC-3, TEC-5, TEC-101 plugged.",
    "TEC-10: 7 in L-80 to 2,285 mMD cemented to surface; 4 1/2 in L-80 liner 2,133-2,489 mMD; perforations 2,349.5-2,353 mMD.",
    "TEC-11: 7 in to 2,354 mMD; 4 1/2 in liner in the lateral; composite plug at 2,400 mMD.",
    "Integrity: TEC-2 and TEC-7 were accepted from PEMEX in 2017 without integrity tests (heads partially dismantled, no leaks); TEC-9 wellhead needs repair or abandonment.",
    "Abandonment reserve USD 411 k (four wells + line, separator, pit); trust balance MXN 6.94 MM (2024-25).",
    "Full casing table with a source on every row: data/processed/wells/casing_strings.csv."], fig="figures/18_wellbore_schematics.png", fig_w=8.6, size=10.5,
    notes=Q(("Where do the TEC-2/TEC-3 casing data come from?", "PEMEX 1956 weekly drilling reports and the 2017 CNH clause-3.3 well-integrity forms (G-54 closed)."),
              ("Liabilities?", "TEC-9 wellhead (flagged as a safety/environmental hazard in the Work Program), TEC-11 composite plug only (no cement), and the four-well abandonment reserve.")))

# ============================ 15. Volumes ============================
slide("Volumes: in place, produced and remaining", [
    ("OOIP. ", "7.8 MMbbl PEMEX/CNH booked; 11.2 MMbbl IFR (modern-log petrophysics); probabilistic P90/P50/P10 8.1 / 10.0 / 12.2 MMbbl."),
    ("Produced. ", "1.98 MMbbl to end-2022 (1.72 monthly record + PEMEX wellfile allocations): 18-25 % of OOIP."),
    ("Analogue recovery. ", "45 El Abra fields: reef-rim 3P EUR recovery P90/median/P10 12 / 31 / 40 %; best 53 %."),
    ("Remaining recoverable. ", "0.3-1.6 MMbbl; most likely ~0.9 MMbbl at trend-average recovery."),
    ("Where it is. ", "Between and above the old producers on the crest, where the aquifer has coned rather than swept (slide 8)."),
    ("Booked. ", "GLJ YE2020 2P for TEC-12: 343 kbbl (221 bbl/d first month)."),
    ("The lever is petrophysics. ", "Porosity and net-to-gross, not area, drive the 4 MMbbl OOIP uncertainty; TEC-12's logs measure it directly."),
], fig="figures/07_volumetrics.png", fig_w=7.6, size=10.5,
    notes=Q(("Why such a range in OOIP?", "Same area; the difference is net pay and porosity (old PEMEX logs vs 2018 modern logs). Petrel Robertson's model gives either depending on which logs are used."),
              ("Reserves status?", "GLJ audited reserves YE2019/YE2020 (TEC-12 2P 343 kbbl); YE2024 and YE2025 reserve reports exist in the Tonalli files and should be shared in the data room.")))

# ============================ 16. TEC-12 opportunity ============================
table("TEC-12: the remaining opportunity is the unswept top of the El Abra on the crest", ["Well", "Top El Abra mSS", "Highest perforation mSS", "Unperforated top", "Result"], [
    ["TEC-6 (crest)", "2,294", "2,308", "14 m", "507 kbbl recorded + 388 kbbl allocated; 3 intervals stepping up"],
    ["TEC-9 (crest)", "2,296", "2,323", "27 m", "353 kbbl from one interval"],
    ["TEC-2", "2,300-2,302", "2,303", "1-3 m", "320 kbbl 1972-2016; 10 kbbl 2018-20"],
    ["TEC-7", "2,304", "2,305", "1 m", "267 kbbl; 100 % water 2019"],
    ["TEC-10 (2018)", "2,307-2,310", "2,314", "4-7 m", "oil at 30-60 % cut, 75.8 kbbl"],
    ["TEC-12 (planned)", "~2,296 (prognosis)", "to be chosen on logs", "target 2,294-2,311", "crest, 118 m from TEC-9, 175 m from TEC-10"],
], colw=[1.5, 1.4, 1.6, 1.5, 2.2], fs=10, bw=4.0, bullets=[
    "Every well that produced from near its top El Abra (TEC-2, TEC-7) did so 6-10 m lower on structure than the crest.",
    "On the crest, the top 14-27 m of the El Abra was left unperforated by PEMEX: it is the highest, least-drained part of the field.",
    "TEC-12 targets it from the TEC-10 pad: S-shape well, target El Abra at -2,296 mSS, TD 2,360 mMD (-2,333 mSS), 7 in casing to TD, AFE USD 1.57 MM.",
    "Fallback: the 2,311-2,332 mSS interval that produced in every well."],
    notes=Q(("Why is TEC-12 better than re-perforating TEC-6 or TEC-9?", "TEC-6 is plugged (bridge plug at 2,297 mSS, 2006) and TEC-9's wellhead is in poor condition; neither has modern logs. A new well gives modern logs, a sample and a clean completion at the crest."),
              ("How big is the attic?", "Not separately mapped. The crest above ~2,303 mSS is thin (about 10 m) and limited in area; booked TEC-12 2P is 343 kbbl (GLJ YE2020) from the whole column at the crest. Treat the attic as upside, the produced interval as the base."),
              ("Source", "docs/09_log_panel.md §3; GLJ YE2019 top picks; TEC-12 drilling programme (Prog12 p.7-8, 27); docs/08_afe.md.")))

# ============================ 17. TEC-12 logs and plan ============================
two_figs("TEC-12: what the offset logs say, and how the well is designed to answer it", ["figures/15_sw_sensitivity.png", "figures/16_tec9_rwa.png"], [4.4, 4.0], [
    ("TEC-9 (118 m away, 1973 logs): ", "the window 2,296-2,311 mSS is inside the El Abra; its water saturation is at parity with the interval that made 353 kbbl (window ÷ producer Sw 0.85-1.03 on sonic porosity)."),
    ("TEC-10 (175 m away, 2018 logs): ", "the same depths read 4-5 ohm·m with clay-type neutron-density separation and are water on the core-supported porosity. But at TEC-10 the top El Abra is 2,307-2,310 mSS, so most of those depths lie above the reservoir (mud log: 30 % calcareous shale)."),
    ("Risks: ", "argillaceous upper El Abra (lower effective porosity); a small crestal gas cap in 1956 (TEC-2 top test GOR ~6,500 scf/bbl; PEMEX gas-oil level ~2,315 mSS in 1971); water close below."),
    ("Plan: ", "triple-combo with PE, resistivity and image log, formation pressures and a fluid sample across 2,290-2,335 mSS; perforate on the data; low drawdown; solvent clean-ups as needed."),
    ("Decision rule: ", "perforate the window if logs show El Abra with low clay and hydrocarbon; otherwise complete in the 2,311-2,332 mSS producing interval."),
], size=9.5,
    notes=Q(("Your own logs at TEC-10 say the upper zone is wet. Why drill for it?", "At TEC-10 the window depths (2,294-2,311 mSS) are mostly above the log top El Abra (2,307-2,310), in a shaly section (mud log: 70 % mudstone-wackestone, 30 % calcareous shale). At TEC-9 and at the TEC-12 location the El Abra top is ~2,296 mSS, so the same depths are reservoir. TEC-9, the nearer offset, shows the window at parity with a 353-kbbl producer. TEC-12 is designed to settle it with modern logs and a sample before any perforation."),
              ("What if the sonic porosity at TEC-9 is overstated by shale?", "With a 20 % shale correction the window's Sw is 1.1-1.3 times the producer's; with 40 %, 1.5-1.6 times. That is why the plan includes PE and density-neutron to measure clay, and a pressure/sample test."),
              ("Is the crest gas?", "There was gas at the top of TEC-2 in 1956 (open-hole test 2,303-2,318 mSS: 41 m³/d oil, 47,702 m³/d gas) and PEMEX marked a gas-oil level at ~2,315 mSS in 1971. Field GOR stayed 400-1,100 scf/bbl through decades of crestal production, so any remaining cap is small. Logs (neutron-density crossover) and the fluid sample will show it."),
              ("Sources", "docs/09_log_panel.md §4; docs/14_sw_sensitivity.md §2, §5; TEC-10 masterlog; PEMEX TEC-2 drilling reports (1956) and 1971 schematic; G-47.")))

# ============================ 18. TEC-12 economics ============================
slide("TEC-12: forecast and economics", [
    ("Well: ", "S-shape from the TEC-10 pad, ~13 days drilling, AFE USD 1.57 MM (drill, complete, equip)."),
    ("Forecast range: ", "first-month rate 100-221 bbl/d across the studies; repository base 50 / 133 / 178 kbbl at 1 / 5 / 10 years, EUR 218 kbbl; GLJ 2P 343 kbbl."),
    ("Price: ", "measured realisation 0.81 × WTI (PEMEX settlements 2020-22)."),
    ("Incremental to a producing TEC-10 ", "(battery and disposal already carried): NPV10 before tax +0.27 MM at WTI 70, +0.89 MM at WTI 80; payout 23-32 months; break-even WTI ~65."),
    ("Stand-alone: ", "break-even WTI ~80."),
    ("Upside: ", "high profile positive from WTI 60 incremental; a successful window completion would also re-rate the crest for a follow-up well (TEC-13)."),
    ("Basis: ", "2023 fiscal terms (31.22 % bid royalty + basic royalty, 30 % tax); 2025 reform not modelled."),
], fig="figures/10_econ_rebuild.png", fig_w=7.4, size=10.5,
    notes=Q(("Why is the base EUR lower than GLJ's 343 kbbl?", "The repository base uses TEC-10's own decline (b ≈ 0.5) rather than a PEMEX-style type curve (b 1.2-1.7). GLJ 2P is the booked number; ours is a conservative check (docs/06_forecast.md)."),
              ("Downside case?", "Low profile (65 kbbl EUR) is negative at every price tested; that is the case where the window adds nothing and the produced interval underperforms."),
              ("Source", "docs/10_econ_rebuild.md; data/processed/econ_rebuild/; docs/08_afe.md.")))

# ============================ 19. Commercial & regulatory ============================
slide("Commercial and regulatory position", [
    ("Offtake: ", "crude sold to PEMEX at CAB Poza Rica under a 2018 sales contract (amended 2019); formula price realised at 0.81 × WTI (2020-22 volume-weighted); quality 28-31 °API, 1.5-1.9 % S; fixed tariffs 2.7-3.3 USD/bbl."),
    ("Fiscal: ", "licence contract with 31.22 % bid royalty plus basic royalty, exploration/extraction fee on 7.2 km², 30 % income tax."),
    ("Regulatory: ", "evaluation period and transition programme (approved 18 Jul 2022, includes TEC-12); Development Plan to be submitted. CNH's functions passed to the CNE in 2025; pre-reform contracts keep their terms (to be confirmed by counsel)."),
    ("Environmental: ", "ASEA impact authorisation (2017, extended to Oct 2023) and TEC-7 injection authorisation (2019); gas flared under the evaluation approval; SEMARNAT and CNH arrears settled in 2024."),
    ("Abandonment: ", "reserve USD 411 k; trust MXN 6.94 MM."),
], size=13,
    notes=Q(("What happens to the contract under the 2025 reform?", "Secondary sources (GT Law, Holland & Knight) say pre-existing contracts keep their terms; the CNE now regulates; CNH suspended evaluation periods and transition programmes in Feb 2025 while contractors kept executing approved plans. Counsel to confirm against the DOF text (G-49)."),
              ("Payment risk?", "PEMEX pays through the NAFIN factoring portal; 2019 saw invoice-loading delays. Settlements 2020-22 reconcile within 1-4 % of the tickets (docs/15_pemex_settlements.md)."),
              ("Gas?", "Flared under the evaluation-period approval; volumes ~0.1-0.2 MMcf/d sour gas; a gas solution may be required in the Development Plan.")))

# ============================ 20. Data and open items ============================
slide("Data available and open technical items", [
    ("Data package: ", "reconciled production database 1956-2022; 21 pressure surveys on one datum; casing and completion table for all wells; TEC-10 logs, core and image log; TEC-9 and older logs; well tests and PTA; volumetrics; economics; PEMEX settlements; CNH filings."),
    ("Held by the operator, to be provided: ", "3D seismic (SEG-Y), Petrel project and velocity model; YE2024/YE2025 reserve reports; TEC-7 injection records; 2020-23 accounts."),
    ("Open technical items: ", "no laboratory PVT; no core electrical properties (m, n) or recent water analysis; per-well split of 2020-22 sales; a single agreed top-El-Abra pick per well."),
    ("What TEC-12 resolves: ", "upper-El-Abra saturation and clay content, current contact and any gas cap at the crest, PVT, and the petrophysics behind the 4 MMbbl OOIP range."),
], size=14,
    notes="Kevin: the repository's gap register (docs/gaps.md) lists each item with its status. Items not to lead with but to answer if asked: TEC-9 Tonalli testing (no record found - confirm), solvent product composition, 2020-21 actual opex.")

# ============================ Backup ============================
s = prs.slides.add_slide(BL); N[0] += 1
tb = s.shapes.add_textbox(Inches(0.8), Inches(3.0), Inches(11.5), Inches(1.0)); p = tb.text_frame.paragraphs[0]
p.text = "Backup"; p.font.size = Pt(30); p.font.bold = True; p.font.color.rgb = ACC

table("Backup: well tests 1956-2019", ["Well", "Date", "Interval", "Oil", "Water / WC", "Gas / GOR", "FTP / notes"], [
    ["TEC-2", "May 1956", "2,307.4-2,321.7 mMD open hole", "41 m³/d", "1.5-9 %", "47,702 m³/d; 1,163 m³/m³", "174 kg/cm²; gas at the top"],
    ["TEC-2", "Jun 1956", "2,345-2,349 mMD", "56 m³/d", "6-13 %", "4,320 m³/d; 77 m³/m³", "squeezed later"],
    ["TEC-2", "Jun 1956", "2,335-2,339 mMD", "72 m³/d", "5-9 %", "6,900 m³/d; 96 m³/m³", "placed on production"],
    ["TEC-6", "Oct 1956", "2,336-2,338 mMD", "77 m³/d", "3.4 %", "-", "8 mm choke"],
    ["TEC-7", "Jan 1957", "2,335-2,337 mMD", "352 bbl/d", "-", "-", "initial test"],
    ["TEC-9", "May 1973", "2,328-2,333 mMD", "91.6 m³/d", "-", "-", "initial"],
    ["TEC-2", "May 2018", "2,307.4-2,311 + deep", "50 bbl/d", "454 bbl/d (90 %)", "220 Mcf/d", "~500 psi; 7 days"],
    ["TEC-10", "Jul 2018", "2,349.5-2,353 mMD", "182 bbl/d", "118 bbl/d (39 %)", "146 Mcf/d", "~880 psi"],
    ["TEC-10", "Sep 2018", "same", "131 bbl/d", "125 bbl/d (49 %)", "100 Mcf/d", "~520 psi"],
    ["TEC-2", "May-Sep 2019", "after plug + add-perf", "47 bbl/d", "141 bbl/d (75 %)", "69 Mcf/d", "~250 psi; 69 days"],
    ["TEC-7", "Jun 2019", "2,310-2,313 mMD", "0", "182 bbl/d (100 %)", "0", "~230 psi; converted to disposal"],
    ["TEC-11", "May-Jul 2019", "liner perfs 2,674-2,745 mMD", "0", "286 bbl/d (100 %)", "0", "~200 psi"],
], colw=[0.9, 1.2, 2.6, 1.1, 1.8, 2.2, 2.6], fs=9,
    notes="Sources: PEMEX TEC-2 weekly drilling reports 1956 (1oHDmwaM); TEC-6 informe final; PEMEX summary tables; Tonalli operations log; Sep 2022 Jaguar review; IHS PTA reports.")

table("Backup: pressure surveys at 2,300 mSS", ["Date", "Well", "Type", "Pressure MPa", "Note"], [
    ["1956-05-24", "TEC-2", "static (2 h 45 min)", "24.65", "new well; 252 kg/cm²"],
    ["1964-12-05/08", "TEC-2", "static (75-78 d)", "24.36-24.39", ""],
    ["1964-12-08", "TEC-7", "static (95 d)", "24.66", ""],
    ["1971-08 to 10", "TEC-6", "74-day build-up", "23.24 → 24.35", "11 runs"],
    ["1998-10-06", "TEC-7", "static", "24.52", "252.2 kg/cm²"],
    ["2018-03-27", "TEC-2", "static after 2+ years shut in", "24.16", "extrapolated 54 m"],
    ["2018-05-30", "TEC-2", "build-up p*", "24.14", "IHS; constant-pressure boundary 700 m"],
    ["2018", "TEC-10", "build-up", "24.14 (gauge 2,316 mSS)", "k 18 mD, skin +5; boundary 195 m"],
], colw=[1.8, 1.0, 3.0, 2.6, 4.0], fs=10, notes="docs/05_pressure.md; data/processed/pressure/tecolutla_pressures.csv.")

out = ROOT / "docs/Tecolutla_Technical_Overview.pptx"
prs.save(out); print(f"saved {out.name}: {len(prs.slides)} slides")
