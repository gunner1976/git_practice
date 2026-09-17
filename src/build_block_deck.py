"""Task 16: block and development history presentation for the incoming operator.
Usage: .venv/bin/python src/build_block_deck.py -> docs/Tecolutla_Block_and_Development_History.pptx
Content is drawn from the task notes (docs/*.md), the agent notes in data/processed/deck_notes/ and the
Drive renderings listed in data/processed/deck_notes/drive_reads_notes.md. Every number on a slide has a
source in one of those files; the notes slide of each section names them.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import json, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BL = prs.slide_layouts[6]
INK = RGBColor(0x0b, 0x0b, 0x0b); INK2 = RGBColor(0x52, 0x51, 0x4e); ACC = RGBColor(0x2a, 0x78, 0xd6)
N = [0]

def _title(s, title):
    tb = s.shapes.add_textbox(Inches(0.4), Inches(0.15), Inches(12.5), Inches(0.8)); tb.text_frame.word_wrap = True; p = tb.text_frame.paragraphs[0]
    p.text = title; p.font.size = Pt(22 if len(title) <= 75 else 18); p.font.bold = True; p.font.color.rgb = INK
    N[0] += 1
    fb = s.shapes.add_textbox(Inches(12.3), Inches(7.05), Inches(0.9), Inches(0.3)); q = fb.text_frame.paragraphs[0]
    q.text = str(N[0]); q.font.size = Pt(9); q.font.color.rgb = INK2

def section(title, sub):
    s = prs.slides.add_slide(BL); N[0] += 1
    tb = s.shapes.add_textbox(Inches(0.8), Inches(2.3), Inches(11.5), Inches(1.5)); tb.text_frame.word_wrap = True; p = tb.text_frame.paragraphs[0]
    p.text = title; p.font.size = Pt(30); p.font.bold = True; p.font.color.rgb = ACC
    tb = s.shapes.add_textbox(Inches(0.8), Inches(3.8), Inches(11.5), Inches(2.0)); tf = tb.text_frame; tf.word_wrap = True
    for i, b in enumerate(sub):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = b; p.font.size = Pt(14); p.font.color.rgb = INK2
    return s

def slide(title, bullets=None, fig=None, fig_w=8.3, notes=None, size=None):
    s = prs.slides.add_slide(BL); _title(s, title)
    if fig:
        s.shapes.add_picture(str(ROOT / fig), Inches(0.3), Inches(1.0), width=Inches(fig_w))
    if bullets:
        x = Inches(0.3 + fig_w + 0.2) if fig else Inches(0.5); w = Inches(13.0 - (0.3 + fig_w + 0.2)) if fig else Inches(12.3)
        tb = s.shapes.add_textbox(x, Inches(1.0), w, Inches(6.0)); tf = tb.text_frame; tf.word_wrap = True
        fs = size or (11 if fig else 13)
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = b; p.font.size = Pt(fs); p.space_after = Pt(5); p.font.color.rgb = INK
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def table(title, header, rows, colw=None, bullets=None, fs=9, notes=None, top=1.0, height=None):
    s = prs.slides.add_slide(BL); _title(s, title)
    nrows, ncols = len(rows) + 1, len(header)
    tw = Inches(12.4) if not bullets else Inches(8.4)
    h = Inches(height) if height else Inches(min(5.8, 0.28 * nrows + 0.3))
    shp = s.shapes.add_table(nrows, ncols, Inches(0.45), Inches(top), tw, h); t = shp.table
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
        tb = s.shapes.add_textbox(Inches(9.0), Inches(top), Inches(4.0), Inches(6.0)); tf = tb.text_frame; tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = b; p.font.size = Pt(10.5); p.space_after = Pt(5)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def two_figs(title, figs, widths, bullets=None, notes=None):
    s = prs.slides.add_slide(BL); _title(s, title)
    x = 0.3
    for f, w in zip(figs, widths):
        s.shapes.add_picture(str(ROOT / f), Inches(x), Inches(1.0), width=Inches(w)); x += w + 0.2
    if bullets:
        tb = s.shapes.add_textbox(Inches(x), Inches(1.0), Inches(13.0 - x), Inches(6.0)); tf = tb.text_frame; tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = b; p.font.size = Pt(9.5); p.space_after = Pt(4)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

# ============================ CONTENT ============================
cas = pd.read_csv(ROOT / "data/processed/wells/casing_strings.csv")
prod = pd.read_csv(ROOT / "data/processed/tecolutla_production.csv", parse_dates=["date"])
press = pd.read_csv(ROOT / "data/processed/pressure/tecolutla_pressures.csv")
sett = json.load(open(ROOT / "data/processed/price/pemex_settlements_summary.json"))
vol = json.load(open(ROOT / "data/processed/volumetrics/summary.json"))
fc = json.load(open(ROOT / "data/processed/forecast/summary.json"))

s = prs.slides.add_slide(BL); N[0] += 1
tb = s.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.5), Inches(1.5)); p = tb.text_frame.paragraphs[0]
tb.text_frame.word_wrap = True; p.text = "Tecolutla field, Contractual Area 24: block and development history"; p.font.size = Pt(30); p.font.bold = True; p.font.color.rgb = ACC
tb = s.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(11.5), Inches(2.5)); tf = tb.text_frame; tf.word_wrap = True
for i, b in enumerate(["Technical handover to the incoming operator: wells, wellbores, pressure, production, fluids, rock and core, geology and geophysics, reserves, accounting since Tonalli took over, crude marketing, operations.",
                        "Prepared by Kevin Gunning, P.Eng., September 2026, on the reconciled data package (docs/, data/processed/) and the Tonalli Drive files listed in data/processed/deck_notes/.",
                        "Conventions: depths mMD below KB or mSS as labelled (TEC-10 on the directional survey, KB 6.13 m); pressures at 2,300 mSS; USD unless labelled MXN or CAD; nothing interpolated; gaps stated on the slide where they bite."]):
    q = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); q.text = b; q.font.size = Pt(14); q.font.color.rgb = INK2

slide("Contents", [
    "1  Block overview and chronology 1956-2024",
    "2  Well-by-well histories and wellbore schematics",
    "3  Pressure history",
    "4  Production summary and charts",
    "5  Fluid analysis: oil, gas, water, PVT",
    "6  Rock analysis and the TEC-10 core",
    "7  Geology with regional context",
    "8  Geophysics: the 3D survey and its interpretation",
    "9  Reserves and resources",
    "10 Accounting summary since Tonalli took over (2016-2024)",
    "11 Crude marketing",
    "12 Operations overview",
    "13 What the incoming operator inherits: decisions, gaps and the register"], size=14)

# ---------- 1 Block overview ----------
section("1. Block overview and chronology", ["Contractual Area 24 (Tecolutla), Tampico-Misantla basin, Veracruz; licence CNH-R01-L03-A24/2016 (Round 1.3).",
    "Nine PEMEX-era wells 1956-1973, four producers; Tonalli Energía from 2016: TEC-2 workover, TEC-10 and TEC-11 drilled 2018; shut in since February 2022."])
slide("The block: location, wells and offset fields", [
    "About 60 km ESE of Poza Rica, municipality of Tecolutla; wells 5.5 km NE of highway 180 via Plan de Villa Cuauhtémoc; nearest towns Gutiérrez Zamora and Tecolutla (2017 Plan de Evaluación base-map captions).",
    "CNH field polygon 3.14 km², all nine wells inside (task 13); contract area 7.2 km² carries the surface fee in the fiscal terms.",
    "Offsets: Miguel Hidalgo field to the NW (separated by the structurally low TEC-5), Ignacio Allende to the SE, San Andrés block and Paso de Oro to the SW.",
    "PEMEX produced every well to a single-well battery and vented the gas; no separation or measurement facility existed in the block at handover in 2016.",
    "Legacy 3D seismic (~150 km²) covers the whole block and Miguel Hidalgo; reprocessed by Tonalli in 2017-18 (section 8).",
    "Wells: TEC-2 (1956 discovery), TEC-3 (salt water), TEC-5 (low, dry), TEC-6, TEC-7, TEC-9, TEC-101 (water, plugged 1972), TEC-10DES and TEC-11DES (2018)."], "figures/13_cnh_polygon.png", 7.0,
    notes="Sources: Figure 1-3 Block Base Map verbiage.docx (Drive 1hSasL3U); docs/13_cnh_filings_gis_cmi.md; Tecolutla 3D Seismic Interpretation Summary.docx (14mWChMG).")
slide("Chronology 1956-2024", ["Discovery and PEMEX development 1956-1973; production recorded monthly by CNH from 1966; last PEMEX-era month January 2016.",
    "Tonalli Energía (IFR / Grupo Idesa) took the block in 2016; Plan de Evaluación 2017; 3D reprocessing; TEC-2 workover and test 2018; TEC-10DES drilled April-May 2018; TEC-11DES horizontal November-December 2018 found 100 % water.",
    "2019: PEMEX factoring stalled, TEC-2 shut in September, TEC-11 plugged; 2020: early-production sales contract with PEP (21 Jul) but the Programa de Transición was dismissed (7 Aug); 2022: Informe de Evaluación rejected (3 Feb), field shut in (4 Feb), Programa de Transición approved (18 Jul), Idesa exits and Jaguar buys 50 % (25 Aug).",
    "2024: abandonment trust reserve USD 411 k; cash calls continue (section 10)."], "figures/20_block_timeline.png", 9.6,
    notes="Sources: PEMEX informes finales TEC-5/6 (19i5buDs, 1c2-WKxk), estados mecánicos, CNH database (task 4), Tonalli letters to PEP 8 Feb and 21 Jul 2022 (1Z5EAMWG, 1BJf7OGI), 2022 Purchase and Sale Transactions memo (1ffaRgaw), Fideicomiso 2024-2025 (1XSHXSKe).")
table("Regulatory status: what the incoming operator steps into", ["Date", "Event", "Source"], [
    ["2016", "Contract CNH-R01-L03-A24/2016 (Round 1.3) to Tonalli Energía S.A.P.I. de C.V.; 25-year term", "CONTRATO_CNH-R01-L03-A24.2016 (1BRBFpBv); Fideicomiso sheet"],
    ["May 2017", "Plan de Evaluación approved; ASEA implementation-plan approval Mar 2018 (ASEA_UGI_DGGEERC_0190_2018)", "Plan de Evaluación 0517 (1P7EHEf7); ASEA oficio"],
    ["2 Jul 2020", "Informe de Evaluación and Programa de Transición filed", "Tonalli letter TON-PEP-SOL/2022-1A"],
    ["21 Jul 2020", "Contrato de Compraventa de Petróleo de Producción Temprana with PEMEX Exploración y Producción", "same"],
    ["7 Aug 2020", "CNH dismissed the Programa de Transición and the Informe; COVID acuerdos extended the Plan de Evaluación to 27 Nov 2020, 27 Aug 2021, then 24 Nov 2021", "same (oficios 260.0338, 260.0488, 260.0995/2021)"],
    ["19 Nov 2021", "Informe de Evaluación and Programa de Transición refiled", "same"],
    ["3-8 Feb 2022", "Informe resolved unfavourably; Tonalli withdrew the Programa request and stopped production on 4 Feb; CNH accepted the withdrawal", "same"],
    ["18 Jul 2022", "Resolución CNH.E.56.001/2022 approves the Programa de Transición (oficio 220.0504/2022)", "Tonalli letter TON-PEP-SOL/2022-2 (1BJf7OGI)"],
    ["25 Aug 2022", "Petro Frontera buys Idesa's 50 % for 100 MXN and sells 50 % to Jaguar E&P for USD 850 k; Jaguar to post the CNH guarantee and operate; Idesa loans forgiven", "2022 Purchase and Sale Transactions memo"],
    ["Apr 2022", "TEC-11DES temporary-abandonment notice (art. 54); reclassification to injector filed 18 Oct 2019", "Anexo 4 aviso (18kU9Zb7)"],
    ["2024-25", "Abandonment reserve USD 411,032 (four wells + line, separator, dam); trust balance MXN 6.94 MM", "Fideicomiso-Reserva de Abandono 2024-2025"],
    ["Mar 2025", "Fiscal reform: contract terms preserved per secondary sources; regulator now CNE; substitution clause to be checked (G-49)", "docs/gaps.md G-49"],
], colw=[1.3, 8.0, 3.1], fs=8.5, notes="A Plan de Desarrollo has never been approved; the field has produced under the evaluation period and the transition programme only.")

# ---------- 2 Wells ----------
section("2. Well-by-well histories and wellbore schematics", ["Nine wells; casing from PEMEX estados mecánicos (2006 updates) and informes finales (1956), Halliburton post-operative reports (2018) and Tonalli estados mecánicos (2019-2022).",
    "TEC-2 and TEC-3 casing strings are not in any file read; the TEC-2 diagram exists only as an image (G-54)."])
pw = prod[prod.well != "FIELD"].groupby("well").agg(first=("date", "min"), last=("date", "max"), oil=("oil_bbl", "sum"), water=("water_bbl", "sum"), gas=("gas_mcf", "sum"))
def f(w, k, d=0):
    return f"{pw.loc[w, k]:,.{d}f}" if w in pw.index else "-"
def dt(w, k):
    return f"{pw.loc[w, k]:%Y-%m}" if w in pw.index else "-"
table("Well summary", ["Well", "Drilled", "KB m / TD mMD", "Result and status", "Top El Abra mSS", "Production record (monthly DB)", "Oil kbbl / water kbbl / gas MMcf"], [
    ["TEC-2", "1956 (discovery)", "4.00 / 2,375", "Producer 1956-2016; Tonalli workover and test May 2018 (8 m³/d oil, 90 % water, skin +196); shut in Sep 2019", "-2,302 (GLJ map)", f"{dt('TEC-2','first')} to {dt('TEC-2','last')}", f"{f('TEC-2','oil')[:-4]} / {f('TEC-2','water')[:-4]} / {pw.loc['TEC-2','gas']/1e3:,.0f}"],
    ["TEC-3", "1956", "6.00 / 2,381", "Salt water in open hole 2,376.8-2,380.8; plugged; delimits the NE flank", "-2,370 (label uncertain)", "-", "-"],
    ["TEC-5", "Jun-Jul 1956", "4.00 / 2,562", "Structurally low, El Abra at 2,551 mSS, not tested; plugged 28 Jul 1956; separates Tecolutla from Miguel Hidalgo", "-2,551", "-", "-"],
    ["TEC-6", "Sep-Oct 1956", "5.67 / 2,339", "Producer, initial 77 m³/d on 8 mm, 3.4 % water; recompleted 2314-2327 m; last production Dec 2006; 388 kbbl wellfile allocation before 1966", "-2,294 / -2,296 (report)", f"{dt('TEC-6','first')} to {dt('TEC-6','last')}", f"{f('TEC-6','oil')[:-4]} / {f('TEC-6','water')[:-4]} / {pw.loc['TEC-6','gas']/1e3:,.0f}"],
    ["TEC-7", "Jan 1957", "5.00 / 2,340", "Producer 2,310-2,313 m; last PEMEX static 1998; Tonalli water-injection string (2 3/8 in, packer 2,300 m) 2019", "-2,304", f"{dt('TEC-7','first')} to {dt('TEC-7','last')}", f"{f('TEC-7','oil')[:-4]} / {f('TEC-7','water')[:-4]} / {pw.loc['TEC-7','gas']/1e3:,.0f}"],
    ["TEC-9", "Apr-May 1973", "5.07 / 2,340", "Producer 2,328-2,333 m (91.6 m³/d initial); closed Jan 1999, produced again 2003-2012; monument", "-2,296", f"{dt('TEC-9','first')} to {dt('TEC-9','last')}", f"{f('TEC-9','oil')[:-4]} / {f('TEC-9','water')[:-4]} / {pw.loc['TEC-9','gas']/1e3:,.0f}"],
    ["TEC-101", "1972", "8.00 / 2,804", "Water-invaded, structurally low, plugged 31 Mar 1972; fish at 926 m", "-2,334", "-", "-"],
    ["TEC-10DES", "11 Apr-4 May 2018", "6.13 / 2,490", "J-shape; cored, logged (Weatherford suite incl. CMI), tested Jul-Aug 2018 (31 m³/d oil, k 18 mD, skin +5); produced to Nov 2019 and 2020-22; shut in Feb 2022, restarted Nov 2022", "-2,310", f"{dt('TEC-10','first')} to {dt('TEC-10','last')} (+ commingled 2020-22)", f"{f('TEC-10','oil')[:-4]} / {f('TEC-10','water')[:-4]} / {pw.loc['TEC-10','gas']/1e3:,.0f}"],
    ["TEC-11DES", "11 Nov-18 Dec 2018", "4.70 / 3,283", "Horizontal, 720 m lateral at 2,305-2,331 mSS; 100 % water (260 bpd, Jul 2019); composite plug 2,400 m Aug 2019; injector reclassification filed; temporary abandonment 2022", "-2,312", "May-Aug 2019 water only", "0 / 4 / 0"],
], colw=[0.9, 1.3, 1.2, 4.6, 1.2, 1.7, 1.5], fs=8, notes="Sources: PEMEX informes finales and estados mecánicos (Drive ids in drive_reads_notes.md), Tecolutla Well Header Information.csv, data/processed/tecolutla_production.csv, GLJ Map 2 Top Depth Structure YE2019 (1xGo-WvP), IHS PTA reports, Anexo 4 aviso de abandono temporal TEC-11.")
slide("Wellbore schematics (depth to scale)", [
    "PEMEX wells: 9 5/8 in surface casing at 500-600 m (807 m at TEC-101), 6 5/8 in production casing to ~2,300 m, 4 1/2 in liners across the El Abra at TEC-6 and TEC-7; TEC-9 6 5/8 in P-110 to TD.",
    "TEC-10DES: 13 3/8 in at 30 m, 9 5/8 in H-40 at 470 m, 7 in L-80 26 lb/ft at 2,285 m cemented to surface, 4 1/2 in L-80 liner 2,133-2,489 m; perforations 2,349.5-2,353 m (active), 2,394-2,414 m (inactive), 2,433.5-2,442.5 m (tight: admitted only at 2,120 psi in the June 2018 injectivity test).",
    "TEC-11DES: 7 in 26 lb/ft at 2,354 m cemented to surface; 4 1/2 in liner in the lateral; composite plug at 2,400 mMD; tubing-less.",
    "TEC-7 carries a 2 3/8 in string with a packer at ~2,300 m for water injection (2019); TEC-2 has an active interval 2,307.4-2,311 m, squeezed intervals and two bridge plugs below.",
    "TEC-2 and TEC-3 casing: not in any file read; the PEMEX drawings for those two wells were not found (G-54).",
    "Full table: data/processed/wells/casing_strings.csv (63 rows, each with its source)."], "figures/18_wellbore_schematics.png", 8.9, size=10,
    notes="Casing sources: TECOLUTLA_6_INFORME_FINAL (1c2-WKxk), BLOQUE_TECOLUTLA_5/7/9/101_ESTADO_MECANICO (1VCktsVx, 1UZlBMHq, 1ys9wOiU, 1a00morB), Anexo 3 estado mecanico final tec-7 (11Wasndd), Halliburton TEC-10 reports (1_5UzGZI, 16_dQsnw, 10f2RlOT), TEC-11 TR 7 report (1CL89Fst), Anexo 4 aviso abandono temporal (18kU9Zb7).")
slide("Per-well production histories", [
    "TEC-6 was the workhorse: 507 kbbl in the monthly record 1966-2006 plus 388 kbbl allocated in the PEMEX wellfile before 1966; three producing intervals stepping down the section.",
    "TEC-7: 267 kbbl, almost all in 1968-1990 from 2,310-2,313 m; TEC-9: 353 kbbl 1973-2012 from one interval, 2,328-2,333 m, with a 2003-2012 second life.",
    "TEC-2: 323 kbbl 1972-2016 with rising water from 2008; the 2018 workover test produced 8 m³/d oil at 90 % water and a skin of +196.",
    "TEC-10: 88 kbbl Jul 2018-Nov 2019 in the monthly record (44 kbbl in the daily file from Sep 2018), first full month 181 bbl/d, 78 bbl/d at 12 months; 2020-22 sales are commingled field volumes: 39 kbbl through the PEMEX settlements.",
    "GOR 400-800 scf/bbl through 1966-92 (cumulative 565), rising only where gas was field-allocated or at low tubing pressure on TEC-10 (docs/04 §5).",
    "Gaps in the traces are missing months in the CNH record (66 runs), not shut-ins (G-34)."], "figures/19_well_histories.png", 8.6, size=10,
    notes="data/processed/tecolutla_production.csv; docs/04_production_database.md; data/processed/production_summary.json.")

# ---------- 3 Pressure ----------
section("3. Pressure history", ["21 surveys 1956-2018 restated at 2,300 mSS with a 10.5 kPa/m gradient; all 16 PEMEX scans OCR-verified.", "Initial 24.65 MPa (May 1956); 24.14-24.16 MPa in three wells in 2018 after about 2 MMbbl: 2 % depletion, more than 99 % of voidage replaced by the aquifer."])
pr = press[press.usable_static | press.kind.str.contains("1956")].copy()
rows = [[r.date, r.well, r.kind, f"{r.gauge_depth_mss:,.0f}" if pd.notna(r.gauge_depth_mss) else "-", f"{r.p_2300mss_mpa:.2f}", (r.quality_flag if isinstance(r.quality_flag, str) else "")[:70]] for r in press.itertuples()]
table("Static and build-up pressures at 2,300 mSS", ["Date", "Well", "Kind", "Gauge depth mSS", "p at 2,300 mSS, MPa", "Flag"], rows, colw=[1.0, 0.8, 1.9, 1.2, 1.3, 6.2], fs=7.5,
      notes="data/processed/pressure/tecolutla_pressures.csv (src/pressure_db.py); docs/05_pressure.md; TEC-10 on KB 6.13 m (G-46 closed).")
slide("Depletion and aquifer support", [
    "24.65 MPa on 24 May 1956 (TEC-2 after 2 h 45 min on a new well) to 24.14-24.16 MPa in 2018 (TEC-2 static gradient after two years shut in, TEC-2 and TEC-10 build-up p*): 0.5 MPa in 62 years.",
    "1964 statics after 75-95 days shut-in agree with the initial; the 1971 TEC-6 series shows short shut-ins understating reservoir pressure by up to 1 MPa (23.2 MPa at 4 days, 24.4 MPa at 74 days).",
    "Rock and fluid expansion for 0.5 MPa on 11 MMbbl OOIP would supply ~11 kbbl; the aquifer has replaced over 99 % of 2 MMbbl of voidage.",
    "Both 2018 build-ups needed a constant-pressure boundary (700 m at TEC-2, 195 m at TEC-10) and TEC-10 a no-flow boundary at 125 m.",
    "Gradient surveys 2018: reservoir temperature 97.5-99.3 °C at 2,120-2,250 m.",
    "The current shut-in (since Feb 2022) is a free multi-year build-up: a static gradient on TEC-10 before any new drilling is the cheapest measurement in the field."], "figures/05_pressure_depletion.png", 7.8, size=11,
    notes="docs/05_pressure.md; IHS PTA reports; fluids_rock_core_notes.md §4 (temperatures).")

# ---------- 4 Production ----------
section("4. Production summary", ["1,341 tidy rows from six sources (CNH monthly 1966-2016, CNH field level 1960-65, Tonalli tests, TEC-10 daily, trucking tickets, PEMEX statements); nothing interpolated.",
    "Recorded 1.72 MMbbl to Dec 2022; with the PEMEX wellfile allocations 1.97-2.0 MMbbl."])
slide("Field production 1960-2022", [
    "PEMEX era 1966-2016: 1.45 MMbbl in the four-well monthly record (TEC-6 507, TEC-9 353, TEC-2 320, TEC-7 267 kbbl) plus 182 kbbl at field level 1960-65 and 482 kbbl of wellfile allocations not in any monthly file.",
    "Tonalli era: TEC-10 44 kbbl daily-metered Sep 2018-Nov 2019; PEMEX statements 63 kbbl Sep 2018-Nov 2020; settlements 39.3 kbbl 2020-22 (16.1 kbbl 2020 net, 17.4 kbbl 2021 filed with CNH, 0.9 kbbl 2022).",
    "Water: 1.07 MMbbl recorded; field water cut rose from <5 % in the 1960s to 60-85 % in the Tonalli era (TEC-10 40 % rising to 85 %).",
    "Gas: 965 MMcf recorded 1966-2016, vented at single-well batteries; solution GOR about 550-570 scf/bbl on 27 years of production.",
    "Rates never exceeded ~500 bbl/d per well; the field made 100-300 bbl/d for most of its life and 20-70 bbl/d in 2020-22 on TEC-10 alone.",
    "No per-well data after Nov 2019: sales are commingled (G-32); 2020 CNH filing net (16,132) vs gross (18,973) is a PEMEX accounting adjustment, not water (G-53)."], "figures/04_production_history.png", 8.0, size=10.5,
    notes="data/processed/production_summary.json; docs/04; docs/13 (CNH filings); docs/15 (settlements).")
slide("Type curve and what a new well can be expected to do", [
    "The 345-400 kbbl 'type curve' in every IFR model is the four PEMEX wells stacked by month on production, and it embeds recompletions (the average rises again at months 100-130 and 250-300).",
    "TEC-10, the only single-completion well with daily data: 181 bbl/d first full month, 78 at 12 months, ~21 at 45 months; b 0.49; about 104 kbbl EUR.",
    "GLJ YE2020 for TEC-12: 203 / 343 / 502 kbbl (1P/2P/3P); Petrel Robertson 100 bbl/d base, 200 upside.",
    "Recommended range for a new vertical well in the produced interval: low 100 bbl/d and 65 kbbl; base 180 bbl/d, b 0.9, 218 kbbl; high 300 bbl/d, 366 kbbl.",
    "Water-limited from the first year in every well; recompletion up-section was PEMEX's tool for a second life."], "figures/06_type_curve_forecast.png", 8.4, size=11,
    notes="docs/06_forecast.md; data/processed/forecast/summary.json.")

# ---------- 5 Fluids ----------
section("5. Fluid analysis", ["Stock-tank oil, separator gas and produced water were measured in 2018-19 by SGS, Corelab and Intertek, and by PEMEX in 1956-1975.",
    "No laboratory PVT study exists: every bubble point, Rs, Bo and live viscosity in circulation is a correlation or a PEMEX analogue (EO-41)."])
table("Oil: laboratory analyses", ["Sample", "Date", "Lab", "°API", "S % m/m", "Viscosity", "Pour °C", "BS&W", "Salt lb/Mbbl", "Notes"], [
    ["TEC-2 whole crude, test separator", "17 May 2018", "SGS Deer Park", "28.4", "1.66", "13.7 cSt @40 °C; 3.9 @98.9", "-18", "38 % (as received)", "95", "RVP 2.1 psi; acid no. 0.33; treated with demulsifier"],
    ["TEC-10 Zone C, well sample", "27 Jul 2018", "SGS Deer Park", "26.5", "1.67", "18.7 cSt @40; 9.4 @60", "-24", "40-44 %", "138", "H2S 38 ppm liquid, mercaptan S 218 ppm; Si 4 ppm: clean-up sample"],
    ["TEC-10 shore tank", "21 Nov 2018", "Intertek Coatzacoalcos", "30.4", "1.66", "-", "-", "0.03 %", "10", "RVP 5.7 psi"],
    ["TEC-10 shore tank", "11 Dec 2018", "Intertek", "30.8", "1.08", "-", "-", "4.0 %", "15", "RVP 7.3 psi"],
    ["TEC-10 tank 10", "15 Jan 2019", "Intertek", "30.1", "1.57", "-", "-", "0.3 %", "72", "RVP 7.0 psi"],
    ["TEC-10DES 'muestreo de fondo' zones A+B / B / C", "Jul-Aug 2018", "SGS Coatzacoalcos", "SG 0.958 / 0.922 / 0.933", "2.56 / 2.33 / 0.71", "776 / 396 / 231 SUS @100 °F", "-", "-", "-", "do not match the tank oil; zone meaning not stated (gap)"],
    ["TEC-11 Tantoyuca 2,361-2,364 m", "22 Aug 2019", "Química Apollo", "17.0", "-", "-", "-", "32 % water", "52,058 mg/l water", "asphaltenes 9.8 %, resins 21.5 %: a different, heavy oil"],
    ["PEMEX Engler forms TEC-2/6/7", "1956-1975", "PEMEX Poza Rica", "0.857-0.881 g/cm³ @20/4 (~29-33 °API)", "-", "76-115 SSU @~30 °C", "-", "-", "-", "eight of nine forms readable by OCR; check scans before quoting"],
    ["CNH monthly filings", "2020-2022", "Tonalli", "28.4-30.9", "1.6", "-", "-", "-", "49", "PEMEX settlements: 25.7-30.9 °API, 1.5-1.9 % S"],
], colw=[2.0, 1.0, 1.3, 1.3, 0.9, 1.5, 0.6, 1.0, 0.9, 1.9], fs=7.5,
    notes="fluids_rock_core_notes.md §1 (file/page for each row). Reading: the reservoir oil is a consistent 28-31 °API, 1.1-1.7 % S sour-ish crude; the PEMEX Ronda-1 table (20 °API, 11.2 cp) describes Ezequiel Ordóñez-41, not Tecolutla.")
table("Gas and water", ["Item", "TEC-6 casing gas, 28 Aug 1970 (PEMEX)", "TEC-2 separator gas, 17 May 2018", "TEC-10 separator gas, 27 Jul 2018", "Water, TEC-2 separator 17 May 2018", "Water, TEC-10 separator 27 Jul 2018"], [
    ["C1 / C2 / C3 mol %", "79.8 / 7.9 / 4.2", "70.4 / 6.7 / 4.3", "70.3 / 7.7 / 4.7", "TDS mg/l: 50,145", "TDS mg/l: 36,788"],
    ["CO2 / H2S / N2 mol %", "4.78 / 0.66 / -", "10.57 / 1.75 / 0.92", "11.14 / 0.99 / 0.81", "Na 16,627; Ca 2,000; Mg 510; Cl 30,250; SO4 560; HCO3 98", "Na 13,352; Ca 480; Mg 170; Cl 20,850; SO4 670; HCO3 1,135"],
    ["Gas gravity (air = 1)", "0.730", "0.842", "0.829", "SG 1.0326; pH 6.68", "SG 1.0239; pH 6.98"],
    ["Gross heating value BTU/scf", "1,152", "1,155", "1,133", "Rw 0.128 ohm·m @75 °F", "Rw 0.196 ohm·m @75 °F"],
    ["GPM C3+", "2.06", "3.07", "2.79", "Type: connate (lab); Na-Cl, Ca second cation", "Type: connate; Na-Cl, HCO3 above SO4 and Ca"],
    ["Note", "H2S 420 grains/100 scf; casing pressure 76 kg/cm²", "GPA 2286; 6.3 kg/cm²(a), 38.8 °C", "GPA 2286; 8.8 kg/cm²(a), 32.6 °C", "well making ~90 % water; Ryznar corrosive", "TEC-10 swabbed and acidised in Jul 2018; scaling tendency"],
], colw=[1.6, 2.0, 2.0, 2.0, 2.4, 2.4], fs=8,
    notes="fluids_rock_core_notes.md §2-3. PEMEX petrophysics used 45,000 ppm and Rw 0.075 ohm·m at 65 °C; the repo Archie pass uses Rw 0.054 at 98.6 °C, bracketed by the two 2018 waters (0.048-0.074 at reservoir temperature). Field-titration salinities during the tests (19-22 kppm at TEC-10, 69-91 kppm at TEC-2) do not match the laboratory TDS; neither analysis is tied to a formation.")
table("PVT: what is measured, what is correlated", ["Property", "PEMEX Ronda-1 table (EO-41 analogue)", "IFR PVT calculator (Vasquez-Beggs)", "IHS 2018 well-test models", "Measured at Tecolutla"], [
    ["Oil gravity", "20 °API", "28.4 °API input", "28.0-28.2 °API", "26.5-30.8 °API stock tank; 28.4 field density on the TEC-2 test"],
    ["Solution GOR", "336 scf/bbl (59.9 m³/m³)", "552 scf/bbl assumed", "541-570 scf/bbl", "never measured; produced GOR 565 cum. 1966-92, 685 (1964), 740-770 on TEC-10 (2018)"],
    ["Bubble point", "1,877 psi", "2,849 psia hard-coded (correlation gave more than initial pressure)", "2,901 / 3,452 psia assumed in the IPRs", "never measured; initial pressure 3,575 psia"],
    ["Bo", "1.19", "1.30 at Pb", "1.28-1.30", "never measured"],
    ["Live oil viscosity", "11.2 cp", "0.62 cp", "0.72-0.74 cp", "dead oil 13.7-18.7 cSt at 40 °C only"],
    ["Compressibility", "-", "co 1.6e-5 /psi", "co 1.2e-5 /psi; ct 1.4e-5 (TEC-2), 4.2e-5 (TEC-10, anomalous)", "never measured"],
    ["Reservoir temperature", "65 °C", "95 °C entered (converted wrongly to 228.6 °F)", "98.6-101 °C", "97.5-99.3 °C, 2018 gradient surveys"],
    ["Reservoir pressure", "252 kg/cm² initial", "3,684 psia", "24.19-24.30 MPa at gauge", "24.65 MPa (1956) to 24.14 MPa (2018) at 2,300 mSS"],
], colw=[1.6, 2.2, 2.6, 2.6, 3.4], fs=8.5,
    notes="fluids_rock_core_notes.md §4 and Reader's notes. Two errors in PVT Calculator (Tecolutla).xlsx: Oil!K11 temperature conversion, and the oil SG passed as gas gravity. With the measured gas gravity and 28-30 °API, an Rs of 550-750 scf/bbl gives Pb of roughly 2,700-3,500 psia at 98 °C: the reservoir is near-saturated, which is consistent with TEC-10's GOR rise at low tubing pressure. One bottom-hole sample from TEC-10 would close G-31.")

# ---------- 6 Rock and core ----------
section("6. Rock analysis and the TEC-10 core", ["One core, 1.3 m recovered of 10 m attempted at 2,352-2,362 mMD (inside the perforated interval), three horizontal plugs, six thin sections; no electrical properties, capillary pressure or relative permeability.",
    "Logs: 1956-1973 PEMEX suites on TEC-2/6/9, Weatherford 2018 suite on TEC-10 (GR, neutron-density, PE, induction, dipole sonic, Stoneley, CMI image)."])
table("TEC-10 core 1: routine analysis, saturations and petrography", ["Plug / sample", "Depth mMD", "He porosity (500 / 3,400 psi)", "k Klinkenberg mD (500 / 3,400 psi)", "Grain density", "Dean-Stark oil / water % PV", "Thin section", "Visual porosity", "Hydrocarbons"], [
    ["N1PS", "2,352.15", "-", "-", "-", "-", "grainstone, miliolids/textulariids, rare rudists, strongly recrystallised", "intercrystalline, moldic; ~3-5 %", "none"],
    ["N1H1", "2,352.25", "2.3 / 1.7 %", "0.020 / 0.004", "2.696", "58.8 / 23.9", "grainstone-packstone", "~2 %", "none"],
    ["N1PM", "2,352.38", "-", "-", "-", "-", "wackestone, planktonic forams (Globotruncana), pyrite", "none", "none"],
    ["N1H2", "2,352.70", "6.7 / 6.3 %", "0.956 / 0.356", "2.709", "19.7 / 20.5", "grainstone, intraclasts", "intercrystalline micro; ~3 %", "none"],
    ["N1H3", "2,352.89", "7.6 / 7.2 %", "0.174 / 0.084", "2.713", "13.8 / 17.8", "grainstone, calcite-sealed fractures", "~4 %", "none"],
    ["N1PI", "2,353.24", "-", "-", "-", "-", "grainstone, sealed fractures, micrite-filled cavity", "~3 %", "none"],
], colw=[0.9, 0.9, 1.5, 1.6, 0.9, 1.5, 2.9, 1.5, 0.9], fs=8,
    bullets=None, notes="Stratascan V603-18 (Tecolutla10_ReporteFinal text), plug workbook Tecolutla10N1(3)PetrofBasica, petrography PDF (1OG5lzvl). Hand specimen: 'posibles trazas de aceite'; thin sections: no hydrocarbons in all six; Dean-Stark 14-59 % PV oil. Core so fractured it stayed in the sleeve; Weatherford: 'El Abra es un mudstone-wackestone muy fracturado'. Spectral GR 10-34 API, K 0.03-0.24 %. Depositional environment: outer platform. The lab's 'Cretácico Superior' and the Globotruncana wackestone deserve a geologist's look at the El Abra top pick.")
slide("What the rock data say about flow", [
    "Plug permeability at stress 0.004-0.36 mD against 18 mD from the TEC-10 well test on 13.2 m and 50 mD at TEC-2 on 8 m: flow is through fractures and vugs the plugs do not sample; matrix porosity 6-8 % in the grainstone, near zero in the argillaceous wackestone.",
    "CMI image (right): 0-7 fractures/m; no open fracture in the TEC-12 window (2,294-2,311 mSS) or in the perforated 10 m; open fractures begin below 2,320 mSS in the produced, water-bearing interval (G-09 closed).",
    "Log zoning at TEC-10 (Archie, Rw 0.054, uncalibrated): window φ 8.9 %, Rt 5.2 ohm·m, Sw ~1.0, 16.5 m above 6 % porosity but 0 m of pay; perforated interval φ 5.4 %, Rt 30, Sw 0.79; below 2,340 mSS φ 2.5-3 %, Rt 40-54.",
    "Mud log 2,328-2,346 mMD: 70 % compact mudstone-wackestone, 30 % soft calcareous shale, 1-3 gas units, no show; 2,346-2,360 m: 100 % mudstone-wackestone, calcimetry 86-90 %.",
    "Mechanical (dynamic, dipole sonic): E 4-5 Mpsi and brittleness 43 % above 2,330 m against 9-10 Mpsi and 73-76 % below 2,380 m; closure-stress gradient 0.66-0.84 psi/ft; no UCS or static calibration.",
    "Well tests (IHS 2018): TEC-2 skin +196 (damaged 1956 completion), TEC-10 skin +4.9; both models need a constant-pressure boundary."], "figures/14_cmi_fractures.png", 6.4, size=10,
    notes="fluids_rock_core_notes.md §6; docs/09, docs/13, docs/14; data/processed/petrophysics/summary.json.")
slide("Logs on one datum and the two readings of the upper zone", [
    "GR rises with porosity in every well (Spearman +0.28 to +0.49): clean GR is the tight miliolid facies, so a low-GR cut-off would discard the pay.",
    "Produced intervals sit at 2,303-2,332 mSS in every well; nothing has ever been produced from the 2,294-2,311 mSS window except the top 4 m of TEC-2's active interval.",
    "Sw sensitivity (72 cases anchored to the aquifer and the producing interval): the window is water at TEC-10 on the core-supported density porosity (Sw ≥ 1.1); at TEC-9, 118 m from the TEC-12 location, the 1973 sonic puts the window at parity with the 353-kbbl producer unless 20 %+ of its porosity is shale effect.",
    "Neutron-density crossover flips sign at 2,311 mSS; PE 3.8-3.9 in the window vs 5.1 in the perforations: argillaceous carbonate above, clean limestone below.",
    "Consequence for any new well: log and test the upper zone before completing; plan the base case on 2,311-2,332 mSS (G-47)."], "figures/09_log_panel.png", 8.6, size=10.5,
    notes="docs/09_log_panel.md; docs/14_sw_sensitivity.md; figures 15-16.")

# ---------- 7 Geology ----------
IMG = "data/processed/deck_notes/img/"
section("7. Geology with regional context", ["Faja de Oro Terrestre: the reef atoll rimming the Tuxpan platform, Tampico-Misantla basin; Tecolutla is a small high on the SE fringing reef between Miguel Hidalgo (NW) and Ignacio Allende (SE).",
    "What the sources say, what they leave out (seal, source rock, stage age, spill point), and where the well tops disagree."])
two_figs("Regional setting: the Golden Lane atoll and the El Abra facies model", [IMG + "resumen_campo_03_Figura_iii_1_Secci_n_s_smica_regional_en_tiempo_en_direcci_n.jpeg", IMG + "resumen_campo_05_Figura_iv_1_Secci_n_del_S_smica_del_Campo_Tecolutla_con_el_m.png"], [4.3, 3.9], [
    "Golden Lane (Faja de Oro): an ellipsoidal carbonate atoll ~150 × 70 km, 1,200 m thick, grown on a basement high in the Early Cretaceous; reef facies on the outer edge, lagoonal patch reefs inside; end-Albian sea-level fall exposed the upper reef, cut channels through the rim and improved reservoir quality (2017 Plan de Evaluación, p12-13).",
    "Tecolutla sits on the SE fringing reef: rudist patch-reef packstones and grainstones; PEMEX facies model pre-reef grainstone-packstone (reservoir) / reef wackestone-grainstone / post-reef mudstone-wackestone (PEMEX Resumen §iv).",
    "Left: PEMEX 2011 PSTM time section SW-NE through TEC-101, TEC-2, TEC-3: Tamabra and San Andrés horizons dipping under the platform edge, the El Abra reef block between two flank faults, Tertiary above.",
    "Right: PEMEX section with the facies cartoon (cuenca, talud, barrera arrecifal, post-arrecife, plataforma interna); the wells sit in the post-reef/lagoon zone at the crest.",
    "Age is given only as 'Cretácico Medio' in every project source; Albian-Cenomanian is the literature assignment, not project data. No source names the seal or the source rock."],
    notes="geology_geophysics_notes.md §1, §10.3; images from 6 -Resumen Campo Tecolutla.docx figures iii.1 and iv.1.")
table("Stratigraphic column and formation tops (mMD below KB; mSS where the source gives it)", ["Formation", "TEC-5 (1956, flank)", "TEC-6 (1956)", "TEC-9 (1973)", "TEC-12 prognosis (2020)", "Character"], [
    ["Tuxpan", "40", "40", "-", "40 (-32 mSS)", "sands"],
    ["Escolín", "580", "727 (721 mSS)", "738", "734.5 (-726)", "shale"],
    ["Coatzintla", "1,160", "1,121 (1,115)", "1,133", "1,136.7 (-1,117)", "shale"],
    ["Palma Real Superior", "1,790", "1,748 (1,742)", "1,759", "1,770.2 (-1,743)", "shale"],
    ["Palma Real Inferior", "2,035", "2,010 (2,004)", "2,019", "2,030.2 (-2,003)", "shale"],
    ["Tantoyuca (Upper Eocene)", "2,210", "2,229 (2,223)", "2,219", "2,237.2 (-2,210)", "shale, bentonite, sand stringers; rests directly on El Abra at the crest"],
    ["Chicontepec Inferior", "2,427", "absent (eroded)", "absent", "-", "present only on the flank"],
    ["San Felipe (Upper Cretaceous)", "2,497", "absent (eroded)", "absent", "-", "58 m at TEC-5, 24 m at TEC-3"],
    ["El Abra (Middle Cretaceous) top", "2,555 (2,551 mSS)", "2,302 (2,296 mSS; logs 2,294)", "2,310 (2,296 mSS)", "2,323.2 (-2,296)", "recrystallised miliolid grainstone to mudstone-wackestone"],
    ["TD", "2,562.1", "2,338.9", "2,340", "2,360 (-2,333)", ""],
], colw=[2.2, 1.6, 2.0, 1.4, 2.0, 3.2], fs=8.5,
    notes="geology_geophysics_notes.md §2.1 and §10.5. Top El Abra per well on the GLJ YE2019 map (mSS): TEC-6 -2,294; TEC-9 -2,296; TEC-2 -2,302; TEC-7 -2,304; TEC-10 -2,310; TEC-11 -2,312; TEC-101 -2,334; TEC-5 -2,551. TEC-2 has three different top picks in the files (2,304 / 2,307 / 2,316-2,320 mMD); TEC-11's mud log names no formations (carbonate-dominant from 2,360 mMD). The TEC-12 prognosis reproduces the TEC-6 tops within a few metres: it is a TEC-6 analogue, not a seismic depth at the TEC-12 location.")
two_figs("Structure: PEMEX 2014 depth map and Tonalli's 2020 Petrel map", [IMG + "resumen_campo_04_Figura_iii_2_Mapa_estructural_en_profundidad_del_yacimiento.jpeg", IMG + "elabra_depth_tec12_s01_top_el_abra_depth_map_TVDSS_5m.png"], [3.6, 4.6], [
    "PEMEX (left, 20 m contours): NW-SE elongated anticline, crest -2,300 to -2,320 m around TEC-2/101/6/9/7, normal faults on both flanks parallel to the axis; TEC-3 on the NE flank at -2,400; TEC-5 far NW at -2,551.",
    "Tonalli 2020 (right, 5 m contours from the reprocessed 3D): two 2,290 m culminations (at TEC-2 and at TEC-6/9) with a 2,300 m saddle near TEC-7/101: total relief across the drilled area of order 10-25 m; two closed lows and a second high to the NW.",
    "Well tops (2,294-2,310 mSS across TEC-6, 9, 2, 7, 10) support only ~15 m of relief; the 'structurally higher' argument for a new well rests on metres, not on a separate closure.",
    "Trap: 'four-way closure by deposition and erosion' (2020 programme, Petrel Robertson: no faults between TEC-6 and TEC-9) versus PEMEX's fault-bounded anticline; the flank faults lie outside the drilled area.",
    "Contact: three numbers in circulation and no stated spill point: 'water at 2,350 m' (2017 plan), wet TEC-2 perforations at 2,331-2,345 mSS, and Petrel Robertson's deep contact -2,374 mSS used for OOIP; TEC-3 (NE) and TEC-5 (NW) found water."],
    notes="geology_geophysics_notes.md §3, §8, §10.6. Image sources: Resumen figure iii.2; ElAbra Depth Tec12.pptx.")
two_figs("Reservoir: facies, porosity and the log evidence across the wells", [IMG + "xsections_navarrete_s02_Imagen_3_b654210f.png", IMG + "tantoyuca_tec269_s03_Imagen_6_26c443a1.png"], [4.4, 3.9], [
    "PEMEX petrophysics: porosity 5-12 %, Sw 24-38 %, Archie with Rw 0.075 at 65 °C; 2017 plan: permeability 6-10 mD (up to 200 mD from the 1956 TEC-2 test), gross 70 m, net 25 m; IFR 2020: gross 42.3 m, net 16.9 m, φ 7 %, Sw 30 %.",
    "Porosity types claimed: intergranular, fracture, karst (vugs and dissolution caverns). Measured: 2-8 % matrix porosity and 0.004-1 mD in the one core; open fractures on the image log only below 2,320 mSS.",
    "Cuttings: TEC-6 and TEC-9 upper El Abra is cream miliolid grainstone with compact mudstone; TEC-2's upper 55 m is dark shale with dense limestone and flint, the top pick disputed; TEC-10 window 70 % mudstone-wackestone and 30 % soft calcareous shale; TEC-11's 720 m lateral is 60 % mudstone-wackestone, 33 % mixed wackestone-grainstone, no pure grainstone.",
    "Left: Navarrete log cross-section in mSS through the producers; right: the Tantoyuca/El Abra contact panel (ILD jumps from ~2 to >50 ohm·m at the contact in TEC-9).",
    "The reservoir the wells actually produced from is a 20-30 m interval at 2,303-2,332 mSS; the 'never perforated' upper 15 m is the appraisal target and the main uncertainty (section 6)."],
    notes="geology_geophysics_notes.md §2.2, §4; docs/03, docs/09, docs/14.")
slide("Analogues on the El Abra trend (CNH data to 2015)", [
    "45 El Abra fields in the IFR analogue workbook (CNH 2015 data): reef-rim fields 35; current recovery factor median 30 %, 3P EUR recovery median 31 % (P90-P10 12-40 %, max 53 %).",
    "Tecolutla holds 2.5 MMbbl/km² against a reef-rim median of 8.3 MMbbl/km²: a thin accumulation for the trend.",
    "Recovery to date 25 % on the CNH OOIP (7.8 MMbbl) or 20 % on the Monte Carlo P50 (10.0 MMbbl); the trend says 30 % is ordinary, which leaves 0.3-1.3 MMbbl depending on the OOIP.",
    "Nearest rim analogues in the table: Álamo-San Isidro (211 MMbbl OOIP, RF 34.5 %, 26.5 °API), Acuatempa (102 MMbbl, 29.7 %), Alazán (66 MMbbl, 29.7 %); interior fields recover 10-37 %.",
    "The workbook has no porosity, thickness or depth columns: the analogue argument is a recovery-factor argument only."], "figures/07_volumetrics.png", 7.6, size=11,
    notes="El Abra Trend Field Analogies.xlsx (45 rows); data/processed/volumetrics/summary.json trend_rf; docs/07_volumetrics.md.")

# ---------- 8 Geophysics ----------
section("8. Geophysics: the 3D survey and its interpretation", ["PEMEX 2011 Furbero-Presidente Alemán-Remolino 3D (PSTM), ~150 km² delivered at signing; reprocessed 2017-18 (Earth Signal PSTM, DMI Kirchhoff PSDM), tied at Miguel Hidalgo MH-412.",
    "What was interpreted, what it changed (TEC-10 came in low; TEC-13 downgraded) and what is not in the package (volumes, velocities, grids)."])
two_figs("Seismic data and the 2018 interpretation", [IMG + "tec12_seismic_s02_Picture_6_e9cc2507.png", IMG + "tec12_seismic_s01_Picture_2_aad0cd1a.png"], [4.9, 3.4], [
    "Data: 2011 PEMEX regional 3D, 'not designed to image the shallow El Abra' (Petrel Robertson); quality fair to good in and around the El Abra, very poor NE of Tecolutla and above ~1 s.",
    "Reprocessing 2017-18: PSTM with gathers, angle stacks and a velocity volume (Earth Signal); Kirchhoff PSDM (DMI); Petrel project with the TEC-10 well tie; Top El Abra TWT and depth surfaces exported.",
    "Tie: MH-412 at Miguel Hidalgo, the nearest well with dipole sonic and density: Tantoyuca = peak, Top El Abra = trough-to-peak zero crossing on a very high impedance contrast; picked every 10th line, autotracked, depth-converted with the average velocity, bulk-shifted and flexed to well tops.",
    "Left: traverse TEC-10, 9, 7, 2 with the top-El-Abra pick on a strong continuous reflector, gently domed, no fault breaks; right: 3D view TEC-10 to TEC-9 over the depth surface (the 1800/1850 labels are not mSS: a different surface or TWT, do not quote depths from it).",
    "Findings used by the 2020 programme: no faults or unconformities between TEC-6 and TEC-9; no karst or fault signature at the TEC-12 location; an undrilled high NW of TEC-9; TEC-13 structurally lower on the revised map."],
    notes="Tecolutla 3D Seismic Interpretation Summary.docx (14mWChMG); Petrel Robertson Tec-12 Assessment.pdf; Programa de perforación Tecolutla 12 pp10-15; Tec 12 Seismic images.pptx.")
slide("Geophysics: limits and gaps", [
    "Depth accuracy: TEC-10 came in lower than prognosis (the number is not in any source); 'tuning of the 3D frequencies is still an issue'; Petrel Robertson's mitigation was to drill TEC-12 as close to TEC-9 as possible (77 m bottom-hole to bottom-hole on the header coordinates).",
    "The 2020 TEC-12 prognosis is the TEC-6 column, not a seismic depth: the seismic contributes the map, not the prognosis.",
    "Not in the package: the seismic volumes, the Petrel project, the TWT and depth grids, the velocity cube, the reprocessing reports, survey geometry (bin, fold, bandwidth), any checkshot or synthetic at a Tecolutla well, any attribute or AVO product, Petrel Robertson's Figure 2, the programme's random lines.",
    "The sink-hole slide (TEC-10 'encountered a small sinkhole') is an assertion with a satellite photo and a textbook diagram; the masterlog, lithology log, CMI and core report record no losses, cavities or sinkhole.",
    "For the incoming operator: obtain the Petrel project and SEG-Y from Tonalli/Jaguar; a checkshot or VSP in the next well and a tie at Tecolutla itself would convert the map from a Miguel Hidalgo-calibrated surface to a local one."], IMG + "tec12_seismic_s03_Picture_4_c8014f19.png", 4.2, size=11,
    notes="geology_geophysics_notes.md §5, §7, §8.")

# ---------- 11 Crude marketing ----------
section("11. Crude marketing", ["Sole buyer PEMEX Exploración y Producción under the early-production sales contract of 21 Jul 2020; trucked to the Ezequiel Ordóñez battery; priced weekly off the Istmo USGC reference.",
    "37 monthly settlements 2020-22 give the realised price: 0.81 × WTI volume-weighted (task 15)."])
slide("How the crude is sold and priced", [
    "Route: single-well battery at the TEC-10/TEC-2 pad (separator, tanks) to PEMEX's Ezequiel Ordóñez facility by rented 30 m³ vacuum-pressure trucks (Transportes TDH, 2020); no pipeline; a 2 in sour-service flowline TEC-10 to the TEC-2 pad was specified in 2020 (TONALLI-INFRA-002).",
    "Contract: Contrato de Compraventa de Petróleo de Producción Temprana PEP-Tonalli, 21 Jul 2020; measurement agreement (Acuerdo de medición Tonalli-PEMEX, 2018); monthly POA/POT/POM volume nominations with tolerance and a 5 % penalty on shortfalls (PEMEX weekly price sheet template).",
    "Price: precio de compra = reference price × C (constante de rendimiento, 0.896-0.916 for 26-31 °API and 1.5-1.9 % S) minus tarifa PEP (0.59 falling to 0.51 USD/bbl from Mar 2021) minus tarifa logística (2.20) minus TRI (0) minus 3 % margen comercial; reference = (0.4 WTS + 0.4 LLS + 0.2 Brent + 6.50) × 0.9965 weekly.",
    "Result: reference/WTI median 0.97; realised/WTI 0.81 volume-weighted (2020 0.81, 2021 0.81, 2022 0.79; P10-P90 0.77-0.84); fixed deductions 3.8-5.3 USD/bbl; ajuste comercial USD 8.3 k in total.",
    "Volumes and revenue: 39,327 bbl and USD 1.80 MM in 2020-22 (27 months with deliveries); quality 25.7-30.9 °API, BS&W 0.0-0.4 % on Tonalli tickets.",
    "The 2022 models' 0.801 was the measured factor; the 2023 model's 0.90 and the 2020 model's 0.95 overstate revenue by 11 and 17 %."], "figures/17_realised_price.png", 7.2, size=10.5,
    notes="docs/15_pemex_settlements.md; data/processed/price/; Tonalli letters to PEP 2022; ESPECIFICACION DE SISTEMA DE TRANSPORTE (1LawOYRR); Copia de Tecolutla (Pemex Feb 2020 Pricing Calc).xlsx (1TMCaeXh); TDH letter (1zM6upX2).")
slide("Crude marketing: collection risk and what to negotiate", [
    "2019: PEMEX issued the COPADE but did not load the July invoice (USD 263 k incl. VAT) into the NAFIN factoring portal; revenue assumed 60 days after COPADE; the directors' memo of Sep 2019 modelled scenarios where PEMEX did not pay to year-end and where TEC-10 was shut in from October (Tonalli 2019 Budget and Forecasts Analysis).",
    "VAT: about USD 1.2 MM recoverable at Aug 2019; refunds of 95 k (2017) and 555 k (2018) applied for through Yaxkin Consulting; VAT on sales can only be netted in months with revenue.",
    "The sales contract's clause 4 required the CNH transition-programme dictamen, delivered only in July 2022; while shut in (Feb 2022 onward) the POA/POT/POM nominations could not be met.",
    "Alternatives never exercised in the files read: sale to a private buyer or refinery, gas monetisation (gas has always been vented or flared; 1,130-1,155 BTU/scf, 11 % CO2, 1-1.75 % H2S).",
    "For the incoming operator: the formula is transparent and the settlements reconcile to the trucking tickets within 1-4 %; the commercial issues are payment timing, the quality constant (sulphur), the fixed 2.7-3.3 USD/bbl of tariffs and the 3 % margin, and the nomination penalties on an intermittent producer."], size=12,
    notes="Tonalli 2019 Budget and 2019 Forecasts Analysis - FINAL.docx (1DvcwTMU); docs/15; fluids notes §2.")

# ---------- 10 Accounting ----------
section("10. Accounting summary since Tonalli took over (2016-2024)", ["Cash basis, from the IFR budget-vs-actual workbook (2016-2019), the 2022 cash reconciliation, the 2024 cash-call summary and the H1-2024 cash-flow statement; no P&L or balance sheet in the files read.",
    "Partner money in about USD 16.7 MM (2020-21 not in the sheets); gross oil revenue USD 4.45 MM 2018-22; well capital ~USD 7.9 MM incurred 2018-19."])
table("Capital, revenue, costs and funding by year (USD, cash basis)", ["Item", "2016-17", "2018", "2019", "2020", "2021", "2022", "2023", "2024 (to Sep)"], [
    ["Partner contributions / loans", "3,250,000", "6,998,500", "2,250,000", "n/s (forecast 1.1 MM)", "n/s", "419,118 (Jaguar 331 k, Petro Frontera 88 k)", "1,731,177 (Jaguar 1.64 MM, PF 88 k)", "2,070,613 Jaguar loans + 121 k interest"],
    ["Oil sales, bbl", "-", "15,415", "32,747", "19,041", "17,546", "2,740", "Jan invoice only", "-"],
    ["Gross revenue", "-", "920,662", "1,731,700", "681,874", "939,419", "178,032", "-", "-"],
    ["Royalties (share of revenue)", "-", "379,450 (41 %)", "706,221 (41 %)", "n/s", "n/s", "n/s", "n/s", "232,481 arrears + 150,390 penalties (Apr)"],
    ["Operating costs", "-", "288,134", "839,052", "forecast 460,769; Sep-20 run-rate 28 k/month", "n/s", "MXN ledger only (trucking, admin, HEPR ~160 k MXN/month)", "n/s", "1,351,098 incl. CNH settlement 442,894 and SEMARNAT fine 606,093"],
    ["G&A", "1,373,983", "1,309,749", "673,984", "forecast 382,100", "n/s (39 MB file unread)", "MXN ledger: payroll, IMSS, taxes; severance MXN 659,860 Dec-22", "n/s", "294,959 Jaguar admin fee + audit, legal"],
    ["Regulatory", "≥ 657,015", "671,017 (incl. 228,220 bid rounds 3.2/3.3)", "112,605", "forecast 20-65 k", "n/s", "CNH tax ~MXN 15 k/month", "n/s", "~770 k fines and fees"],
    ["Capital", "n/s", "4,135,710 (TEC-10 2.44 MM, TEC-2 WO 0.61 MM, TEC-11 0.82 MM)", "2,335,691 (TEC-11 1.72 MM)", "forecast 2,054,331, mostly TEC-11 payables", "n/s", "n/s", "n/s", "45,206"],
    ["Net VAT cash", "n/s", "(661,822)", "(56,198) after 246,854 refunds", "forecast +489,135", "n/s", "n/s", "n/s", "no refunds"],
    ["Cash at year-end", "856,195 (1 Jan 2018)", "326,935", "422,063", "forecast 39,229", "≈ 79 k (MXN 1.62 MM)", "≈ 6.3 k (MXN 129 k)", "8,752", "17,565 (30 Jun)"],
], colw=[1.7, 1.0, 1.7, 1.3, 1.5, 1.1, 1.6, 1.2, 1.5], fs=7.5,
    notes="accounting_notes.md §2-§9 with sheet/row provenance; n/s = not in sheets. Sources: TONALLI BUDGET - Actual 2019 Forecast 2020 (1JyC2TvK), Tonalli Cash Dec 31 2022 (1TrF0pz3), Summary of Cash Calls Sep 2024 (19JmTOqp), 06_CashFlow acumulado (1AnU2ero), docs/15 for 2020-22 revenue. Two renderings were truncated by the connector at ~1 MB, so 2020-21 actuals and the 2022 AP/AR/VAT sheets are absent.")
slide("Wells: AFE against actual, and what was left unpaid", [
    "TEC-10 (2018): AFE USD 2.92 MM; USD 2.04 MM booked to 15 Jun 2018; USD 2.58 MM cash paid 2018-19 for drill and complete.",
    "TEC-11 (2018-19): drilling AFE USD 2.25 MM, tracker USD 3.03 MM at 26 Dec 2018, actual USD 3.11 MM (+USD 251 k 'QMAX over budget'); completion 0.96 MM vs 0.83 MM; Tantoyuca test 0.21 MM; all-in USD 4.40 MM vs USD 3.93 MM budget (+12 %) for a well that made water.",
    "TEC-2 workovers USD 0.76 MM (2018-19); TEC-7 water-injection conversion USD 0.10 MM; seismic reprocessing USD 61 k (2018) against USD 78 k planned; landowner fees USD 73 k.",
    "Cash paid on wells by end-2019 USD 6.46 MM against ~USD 7.9 MM incurred: ~USD 1.9 MM of TEC-11 invoices carried into 2020 as 'payment of accrued capital costs' (directors' memo: payables USD 2.3 MM at 30 Jun 2019); 2019 legal invoices were still being paid in June 2024.",
    "TEC-12: a budget row from 2019 onward, always zero; no spend through September 2024. AFE USD 1.57 MM at Nov-2020 pricing (docs/08).",
    "2016-17: USD 1.37 MM G&A and at least USD 0.66 MM regulatory before any well was touched (consultants, data rooms, Round 3.2/3.3 bids, insurance, legal)."], "figures/08_afe.png", 6.0, size=10.5,
    notes="accounting_notes.md §2; drilling-cost workbooks (E, F, G); docs/08_afe.md.")
slide("Cash position and the funding story", [
    "2018: USD 7.0 MM contributed, USD 7.3 MM net outflow; cash fell from 4.1 MM (Feb) to 0.33 MM (Dec) while TEC-10 and TEC-11 were drilled.",
    "2019: cash 12 k in June and 19 k in August; PEMEX failed to load the July invoice into the NAFIN factoring portal; USD 1.55 MM shortfall to year-end; USD 2.25 MM contributed; TEC-2 shut in; VAT refunds USD 247 k in Nov-Dec.",
    "2020-21: no actuals in the sheets; revenue USD 0.68 MM (COVID, no deliveries Apr-Jun) and 0.94 MM; the January-2020 forecast needed a further USD 1.1 MM.",
    "2022: field shut in Feb; PEMEX paid MXN 8.2 MM for late-2021/early-2022 deliveries 3-5 months late (May-Jul); Idesa's last entries Mar-May; Jaguar's first cash calls 15 Sep 2022; five staff paid off in December (MXN 660 k); year-end cash ≈ USD 6 k.",
    "2023: Jaguar funded MXN 27.6 MM (USD 1.54 MM) to September and MXN 7.7 MM more to December; Petro Frontera (IFR) contributed USD 176 k and was served a default notice on 1 Oct 2023: diluted from 50 % to 44.19 % (Sep) and 42.63 % (Dec 2023), 40.24 % potential at Feb 2024.",
    "2024: Jaguar loans USD 2.07 MM to September (interest ~10-12 %/yr per JOA), spent on the CNH arrears and penalties (USD 443 k, April), the SEMARNAT PPCIEM fine (USD 606 k, May), audit, legal, environmental monitoring and the Jaguar admin fee (~USD 55 k/month); no crew, trucking or diesel lines: the field was not producing. Year-end 2024 forecast still USD 1.3 MM short."], "figures/21_funding_and_cash.png", 6.2, size=10,
    notes="accounting_notes.md §6-§8; Tonalli 2019 Budget and Forecasts Analysis (directors' memo, 1DvcwTMU); 2022 Purchase and Sale Transactions memo (1ffaRgaw) for the ownership change the accounting sheets do not record.")
slide("Accounting: what the incoming operator should ask for", [
    "The 2020-2021 actuals (cash, opex, G&A, VAT, contributions) and the 2023 operating costs: none are in the files read; the 39 MB G&A workbook for 2021 could not be rendered.",
    "A balance sheet: payables at 25 Aug 2022 were USD 2.14 MM per the share-sale valuation; the abandonment trust column is empty in the 2024 sheets while the Fideicomiso sheet shows MXN 6.94 MM and a USD 411 k reserve.",
    "The VAT position after 2019 (about USD 1.2 MM recoverable in Aug 2019, USD 247 k refunded, USD 0.7 MM forecast for 2020, nothing since).",
    "Royalties 2020-2024 by month: only the April-2024 arrears settlement (USD 232 k + USD 150 k penalties) is visible; the monthly contractual quota to the FMP is the recurring fiscal line.",
    "The JOA loan terms between Jaguar and Tonalli, the dilution mechanics (default notices Oct and Dec 2023) and the share register: the 2022 memo values 50 % of Tonalli at USD 1.32 MM net of payables and development costs.",
    "Order of magnitude since 2016: ~USD 16.7 MM of partner money plus USD 4.45 MM gross revenue in; ~USD 6.5 MM capital paid (7.9 MM incurred), ~3.7 MM G&A, ~2.2 MM regulatory and fines, ~1.1 MM opex, ~1 MM net VAT visible out; 2020-23 is the unquantified balance."], size=12,
    notes="accounting_notes.md §9-§10.")

# ---------- 9 Reserves ----------
section("9. Reserves and resources", ["PEMEX 2014: OOIP 7.8 MMbbl, RF 24 %, 6 kbbl 2P remaining at 9 bbl/d. GLJ YE2020 and YE2021: 2P 862-885 kbbl gross, of which TEC-10 196-205 and two undrilled wells (TEC-12, TEC-13) the rest.",
    "OOIP 8-10-12 MMbbl (P90-P50-P10, task 7); remaining oil at a trend recovery factor 0.3-1.3 MMbbl depending on the OOIP."])
table("Reserves by evaluator and category (gross, kbbl oil)", ["Evaluator, effective date", "1P (PDP / total)", "2P (PDP / total)", "3P (PDP / total)", "Undrilled wells carried", "PV10 BTAX, total 2P (USD MM)", "Source"], [
    ["PEMEX / CNH data room, 1 Jan 2014", "6", "6", "156", "none; OOIP 7.8 MMbbl, RF to date 24.4 %", "-", "6 -Resumen Campo Tecolutla.docx tables ii.1-ii.3"],
    ["CNH El Abra trend table, Apr 2015", "-", "-", "3P EUR 2,129 (27 %)", "produced 1,913", "-", "El Abra Trend Field Analogies.xlsx"],
    ["GLJ, 31 Dec 2020 (Tonalli, project 1212851)", "99 / 326", "125 / 862", "164 / 1,238", "TEC-12 DIR 197 / 335 / 493; TEC-13 HZ 322 (2P) / 460 (3P)", "7.46", "YE2020 Corporate Summary Detail (Final)"],
    ["GLJ, 31 Dec 2021, Draft 1 (project 1223410)", "92 / 329", "125 / 885", "170 / 1,279", "TEC-12 DIR 209 / 350 / 516; TEC-13 HZ 339 / 486", "9.88", "Tecolutla (Tonalli) Dec 31 2021 Reserve Report Draft 1 (1cILp0-I)"],
    ["Jaguar transaction valuation, 25 Aug 2022", "-", "2P PV15 9.134 less development 3.972, abandonment 0.388, payables 2.141 = 2.633 net", "-", "TEC-12 and TEC-13 development USD 3.97 MM", "-", "2022 Purchase and Sale Transactions memo (1ffaRgaw)"],
    ["Repo (tasks 6-7), Sep 2026", "-", "TEC-12 P50 218 kbbl (P90 65, P10 366) for a new vertical well in the produced interval", "-", "no TEC-13", "incremental NPV10 +0.27 MM at WTI 70 (0.81 price factor)", "docs/06, docs/10, docs/15"],
], colw=[2.2, 1.2, 2.2, 1.3, 2.4, 1.3, 1.8], fs=8,
    notes="wells_ops_reserves_notes.md §4.1-4.2. GLJ YE2020 to YE2021 reconciliation: total 2P 862 + 40 technical revisions - 17 production = 885 kbbl. GLJ economic parameters: 88 % of Brent less 2.73-2.79 USD/bbl transport; royalty burden ~39 % of revenue; opex 1,400-1,670 USD/well/month + 3.75-5.85 USD/bbl + 227-276 kUSD/yr field; capital TEC-12 USD 1.5 MM, TEC-13 USD 2.4 MM; abandonment 75 kUSD/well. GLJ's TEC-10 2P profile was overtaken by actual decline within a year (G-39).")
table("OOIP by source and the recovery-factor arithmetic", ["Source", "Area", "Gross m / N/G", "φ", "Sw", "Bo", "OOIP MMbbl", "Recovery basis"], [
    ["PEMEX 2014 (CNH data room)", "2.5 km²", "-", "5-12 %", "24-38 %", "1.19", "7.8", "24.4 % to date; 3P final 26.4 %"],
    ["IFR 'Summary (GLJ)' sheet, all models 2020-23", "630 ac", "42.3 / 0.40", "7 %", "30 %", "1.19", "11.2", "2 MMbbl = 18 %; 1.2 MMbbl remaining at 29 %"],
    ["GLJ 1P / 2P / 3P (YE2020 = YE2021)", "401 / 515 / 630 ac", "GRV 59.6 / 74.1 / 87.4 kac·ft; 0.40", "5 / 6 / 7 %", "30 %", "1.19", "5.44 / 8.30 / 11.16", "EUR 31-36 % / 21-31 % / 17-27 %"],
    ["Petrel Robertson geomodel, OWC -2,374 mSS", "2.55 km²", "46.8 / 0.43", "5.6 %", "20 %", "1.19", "11.96 (12.04 on TEC-10 logs only; 7.59 on vintage logs)", "-"],
    ["Repo Monte Carlo (task 7)", "-", "-", "-", "-", "-", "P90 8.1 / P50 10.0 / P10 12.2", "remaining at trend 29 %: 0.3 (CNH) / 0.9 (P50) / 1.3 (IFR) MMbbl"],
], colw=[2.6, 1.2, 2.0, 0.9, 0.8, 0.6, 2.2, 2.3], fs=8.5,
    bullets=None, notes="docs/07_volumetrics.md; wells_ops_reserves_notes.md §4.3; GLJ method: Petrel model from Tonalli, porosity from TEC-9 and TEC-10 only, Sw 30 % by Simandoux at TEC-9, N/G 40 %, OWC -2,374.2 mSS (LKO in TEC-3); low case only south of TEC-11 because of the TEC-11 water. The 7.8 vs 11.2 difference is petrophysics (porosity and N/G), not geometry (task 7).")
slide("Reserves: what to carry forward", [
    "Producing reserves are one well: TEC-10 at 80-100 bbl/d initial in GLJ's decline (b 0.4-0.6) against an actual b of 0.49 and ~104 kbbl EUR; GLJ's 2P 196-205 kbbl for TEC-10 is high on the evidence (task 6).",
    "Everything else is undrilled: TEC-12 (vertical, 250-600 kbbl technical in GLJ; 65-218-366 kbbl in this package) and TEC-13 (horizontal, 400-600 kbbl in GLJ, no basis in this package after TEC-11).",
    "The field is 25 % recovered on the CNH OOIP and 20 % on the P50; the El Abra reef-rim median is 30 %: the prize is a few hundred kbbl to about 1.3 MMbbl, most of it in the upper, never-perforated zone whose fluid content is the open question (section 6).",
    "Price: GLJ used 88 % of Brent; the settlements measure 0.81 × WTI (about 0.77 × Brent): apply the measured factor to any re-run.",
    "Fiscal: contract royalties ~39-44 % of revenue; the March 2025 reform preserved contract terms per secondary sources (G-49, counsel to confirm).",
    "For a re-booking: one static gradient on TEC-10, one bottom-hole fluid sample, a core-calibrated petrophysical pass on the upper zone, and the seismic package from Tonalli/Jaguar would remove the four largest uncertainties."], "figures/06_type_curve_forecast.png", 6.4, size=11,
    notes="docs/06, docs/07, docs/10, docs/15; wells_ops_reserves_notes.md §4.4-4.6.")

# ---------- 12 Operations ----------
section("12. Operations overview", ["A minimal, largely rented battery on the TEC-10/TEC-2 pad; trucking to PEMEX's Ezequiel Ordóñez station; water hauled to third-party disposal until Aug 2019, then injected at TEC-7.",
    "Operating mode 2018-2022, the cost base, staffing as the tickets show it, and the filing calendar the incoming operator inherits."])
table("Facilities: planned (2017) versus as operated (2018-2022)", ["Item", "2017 Plan de Evaluación design", "As built / as operated", "Source"], [
    ["Battery", "'Batería de recolección TEC-10': two 36 in × 120 in three-phase separators with turbine meters (600 m³/d liquid), two 750-bbl API-650 tanks expandable to six, water tank, fuel-gas system, up to two 1.5 MW generators, API-521 flare, truck-loading meter", "Wellsite test equipment; rented three-phase separator MXN 216 k/month Sep 2019-Mar 2020; own three-phase separator (20 in OD × 10 ft, 1,440 psi, NACE) and ecological burner from 8 Mar 2020; rented frac tanks (Oro Negro, MXN 32 k/month) throughout; 60 m³ pit; two 8.3 HP motor-pumps", "PE2017; SASISOPA inventory (1Kc7j1Ue); Op Cost 290920; Fideicomiso 2024"],
    ["Flowlines", "Discharge lines TEC-2 and TEC-10 to the battery", "514 m of 2 in sch 80 A106 Gr B sour-service line with class 300 valves installed 17 Dec 2019 (0.52 km TEC-10DES to TEC-2 pad in the abandonment list); spec TONALLI-INFRA-002 issued Feb 2020", "Inventory row 89; 1LawOYRR"],
    ["Export", "Trucks to PEMEX EORD (Ezequiel Ordóñez) then PEMEX 12 in line", "885 truck tickets Jul 2018-Dec 2022: 519 loads to Ezequiel Ordóñez (EZOR), 4 to Santa Agueda; hauliers PHC 258, Nuevo Amanecer 197, TDH 175 (2021-22), Carga Sedimentaria 153, CBG 61; 30 m³ vacuum-pressure units; PEMEX-agreed BS&W and monthly conciliation", "Tecolutla Production Tracking.xlsx (TRUCKING, Reconciliation)"],
    ["Water", "Injection-pump space for 2,000 m³/d", "Hauled: 3.7 kbbl flowback to ESA (2018), 12 kbbl to Mozutla-1 (2018), 44 kbbl to Mozutla-1/-7 (2019); from Aug 2019 TEC-7 injection string (2 3/8 in, packer ±2,300 m); no injected volumes or pressures in any file; 2020-21 produced water 48 and 74 kbbl (WC 72-81 %)", "Tracking; Anexo 3 estado mecánico TEC-7; CNH annual filings"],
    ["Gas", "Fuel gas and flare", "Vented/flared throughout; 0.9 MMcf flared Nov 2022 under the approved evaluation-programme burn; 1,130-1,155 BTU/scf, 11 % CO2, 1-1.75 % H2S", "CNH_DGM_BALANCES; fluids notes §2"],
    ["Measurement", "Turbine meters, TOM tickets", "Fiscal turbine meter at 'CAB Poza Rica'; delivery at Estación de Bombeo Ezequiel Ordóñez, La Guasima, Papantla; ticket top/mid/bottom BS&W and API; PEMEX statements reconcile to tickets within 2 %", "Tabla Informe Mensual CNH Nov 2022; Reconciliation"],
], colw=[1.2, 4.0, 5.2, 2.0], fs=8,
    notes="wells_ops_reserves_notes.md §3.1-3.4. The SASISOPA inventory (107 lines, Apr 2020) is a materials list: wellheads and trees (7 1/16 in 5,000 psi), casing and tubing tallies for TEC-10 and TEC-11, stimulation tools, pumps, hoses, SCBA, the flowline, separator and burner; no tank farm appears in it.")
table("Operating mode 2018-2023", ["Period", "Producing", "What happened"], [
    ["Mar-Aug 2018", "TEC-10 flowback", "TEC-2 static gradient and 22-day test (8 m³/d oil, 90 % water); TEC-10 drilled 11 Apr-4 May, flowback 23 Jul-6 Aug, build-up to 31 Aug"],
    ["Sep-Dec 2018", "TEC-10 (+ TEC-2 test)", "First sales to EZOR Sep 2018; TEC-10 ~181 bbl/d in Oct; TEC-11 drilled 11 Nov-18 Dec; 14.4 kbbl sold"],
    ["Jan-Aug 2019", "TEC-10, TEC-2", "TEC-11 completion May-Sep: water only; TEC-7 converted to injector 26 Aug; last water hauls Aug 2019; 33.8 kbbl sold in the year"],
    ["Sep 2019-Mar 2020", "TEC-10 (TEC-2 shut in Sep 2019, commingled again for testing from 31 Jan 2020)", "PEMEX factoring stalled; break-even 60 bbl/d at USD 54; own separator and burner 8 Mar 2020; last load 20 Mar 2020"],
    ["Apr-Jun 2020", "none", "Shut in on the price collapse; no deliveries; Programa de Transición request dismissed 7 Aug 2020"],
    ["Jul 2020-Jan 2022", "TEC-10 only", "1,300-2,600 bbl/month (2020), 730-2,335 (2021); choke opened Feb 2021; 17.2 and 18.0 kbbl sold; water cut 72-81 %"],
    ["4 Feb-23 Nov 2022", "none", "Production stopped after the CNH rejected the Informe de Evaluación; Programa de Transición approved 18 Jul; Jaguar in 25 Aug; TEC-11 temporary abandonment notice"],
    ["24 Nov-Dec 2022", "TEC-10", "Restarted: 678 bbl net in 15 days (Nov), 916 bbl delivered; 4 loads in December unsettled; five staff paid off 15-20 Dec"],
    ["2023-2024", "none recorded", "All four Tonalli-era wells listed shut-in in the 2024 abandonment sheet; 2024 payments show environmental monitoring, audit, legal and fines but no crew, trucking or diesel"],
], colw=[1.6, 2.4, 8.4], fs=8.5,
    notes="wells_ops_reserves_notes.md §3.3; accounting_notes.md §4, §8; docs/13.")
slide("Cost base, staffing, filings and HSE", [
    "Cost base at Sep 2020 (field producing ~50 bbl/d): about USD 28 k/month: crew MXN 280 k (Servicio de Ingeniería, Instrumentación y Conexos), vacuum truck MXN 108 k (TDH), diesel 60 k, consumables 40 k, frac tank 32 k, water analyses 21 k, Intertek crude analysis USD 1.5 k, demulsifier USD 0.9 k; separator rental added MXN 216 k/month until March 2020. 2019 opex USD 839 k (USD 25.6/bbl); GLJ carried 1,400-1,670 USD/well/month plus 3.75-5.85 USD/bbl plus USD 227-276 k/yr field.",
    "Staff: a contracted field crew; Tonalli site signatories on the tickets (Bernardo Leandro López, José Briviesca Ramos, Francisco Ramírez, Roberto Maldonado); a SISOPA coordinator; corporate administration USD 39 k/month in the 2022 CNH report; no headcount table exists; severance for five staff in Dec 2022.",
    "Filings: CNH monthly production, test, daily-by-installation and balance formats (DGM 01-07), the monthly activities-and-investments report (contract clause 4.1), annual consolidated production (Anexo III.8.III), annual production forecast table, CRE semi-annual sales report, PEMEX monthly conciliation; LISH exploration fee and activity tax on 7.16 km² (USD ~1.1 k/month now, 3.6 k in the extraction phase).",
    "HSE and regulatory: SASISOPA in place (Apr 2020 inventory; drills, PPE, H2S training, gas detection); flowline and storage to NOM-009-ASEA-2017 and NOM-006-ASEA-2017, NACE MR0175; ASEA implementation-plan approval 2018 and 2022 correspondence; SEMARNAT PPCIEM fine USD 606 k paid May 2024; CNH arrears and penalties USD 443 k paid April 2024; quarterly OGI-camera emissions monitoring contracted in 2024.",
    "Wells to watch: TEC-9 wellhead flagged as a safety and environmental hazard in the Work Program; TEC-11 plugged with a composite plug only (no cement); TEC-7 injection string status unknown since 2019; TEC-2 and TEC-3 casing records missing."], size=11,
    notes="wells_ops_reserves_notes.md §3.5-3.8; accounting_notes.md §4-§5; drive_reads_notes.md.")

# ---------- 13 Closing ----------
section("13. What the incoming operator inherits", ["Four shut-in Tonalli-era wells, a minimal battery, a transition programme approved in 2022, a 50/50-turned-57/43 partnership funded by Jaguar loans, and one open technical question worth more than everything else."])
slide("Decisions and the register", [
    "Technical: (1) static gradient on TEC-10 after four years shut in; (2) bottom-hole fluid sample for a first PVT (G-31); (3) core-calibrated petrophysics of the upper zone at TEC-10 and a log-and-test-before-completing rule for any new well (G-47); (4) obtain the Petrel project, SEG-Y and velocity model; (5) settle one top-El-Abra pick per well and the TEC-2/TEC-3 casing records (G-54).",
    "Commercial: the PEMEX formula is transparent (0.81 × WTI realised); the issues are payment timing, nomination penalties on an intermittent producer and the 2.7-3.3 USD/bbl of fixed tariffs.",
    "Financial: no 2020-21 or 2023 actuals in the files; payables were USD 2.14 MM at Aug 2022; Jaguar loans USD 2.07 MM in 2024 at JOA interest; fines and arrears of ~USD 1.05 MM paid in 2024; abandonment reserve USD 411 k against a MXN 6.9 MM trust.",
    "Regulatory: a Plan de Desarrollo has never been approved; the field produced under the evaluation period and the transition programme; 2025 reform terms to be confirmed by counsel (G-49).",
    "Economics of the next well (task 10, 0.81 price factor): incremental to a producing TEC-10, NPV10 +0.27 MM at WTI 70, break-even ~65; stand-alone break-even ~80: it works for an operator that already carries the field.",
    "Register: 53 gaps in docs/gaps.md, 13 open before this deck; new items from this deck are G-54 (TEC-2/3 casing), G-55 (seismic package not in the repo), G-56 (2020-21 and 2023 accounting actuals, 2021 G&A file unreadable), G-57 (TEC-7 injection volumes and current string status)."], size=12,
    notes="docs/gaps.md; docs/Tecolutla_Field_History_and_TEC12_Review_v4.md.")
table("Sources behind this deck", ["Section", "Repository notes", "Drive files read for this deck (ids in data/processed/deck_notes/drive_reads_notes.md)"], [
    ["1, 2", "docs/04, 13; data/processed/wells/casing_strings.csv", "PEMEX informes finales TEC-5/6; estados mecánicos TEC-5/7/9/101 (2006) and TEC-2/7/11 (2019-22); Halliburton TEC-10 and TEC-11 cementing reports; Latina injectivity test; TEC-11 abandonment notice; Tonalli letters to PEP 2022; 2022 share transactions memo; Fideicomiso 2024-25"],
    ["3, 4", "docs/05, 04, 06, 12", "IHS PTA reports (repo); CNH Nov-2022 formats (repo)"],
    ["5, 6", "data/processed/deck_notes/fluids_rock_core_notes.md; docs/09, 12, 14", "Stratascan petrography (1OG5lzvl); 25 fluid analyses (repo)"],
    ["7, 8", "data/processed/deck_notes/geology_geophysics_notes.md; docs/03, 07, 13", "3D Seismic Interpretation Summary (2018); Plan de Evaluación May 2017 (English); GLJ YE2019 top-structure map; block base-map captions"],
    ["9", "data/processed/deck_notes/wells_ops_reserves_notes.md §4; docs/06, 07", "GLJ YE2021 Draft 1 reserve report; YE2020 detail (repo)"],
    ["10", "data/processed/deck_notes/accounting_notes.md", "TONALLI BUDGET Actual 2019 Forecast 2020; Tonalli Cash Dec 2022; Summary of Cash Calls Sep 2024; 06_CashFlow acumulado 2024; Op Cost Sep 2020; directors' memo Sep 2019"],
    ["11", "docs/15", "PEMEX Feb-2020 pricing calc; transport-system specification; TDH letter"],
    ["12", "wells_ops_reserves_notes.md §3", "SASISOPA inventory Apr 2020; Tecolutla Production Tracking.xlsx (repo)"],
], colw=[0.8, 3.6, 8.0], fs=8.5)

prs.save(str(ROOT / "docs/Tecolutla_Block_and_Development_History.pptx")); print("deck saved", len(prs.slides), "slides")
