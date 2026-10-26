"""Build the Tecolutla time-lapse dataset (wells.json, events.json, pressure.json).
Every number is transcribed from a file in /home/user/git_practice; the source is cited per item.
Monthly producing / shut-in runs for the PEMEX-era wells are derived from data/processed/tecolutla_production.csv
(CNH monthly records; the original CNH tables carry explicit zero-production rows for every gap, cnh_findings.md section 1).
"""
import json, math
from pathlib import Path
import pandas as pd

REPO = Path("/home/user/git_practice")
OUT = Path("data/processed/presentation")
OUT.mkdir(parents=True, exist_ok=True)
M3_BBL = 6.2898          # bbl per m3 (as instructed)
M3M3_SCF = 5.6146        # scf/bbl per m3/m3
KGCM2_MPA = 0.0980665
MPA_PSI = 145.0377

def bbl(m3): return round(m3 * M3_BBL, 1)
def scf(r): return round(r * M3M3_SCF)

# ---------------------------------------------------------------- CNH-derived runs
prod = pd.read_csv(REPO / "data/processed/tecolutla_production.csv", parse_dates=["date"])
cnh = prod[prod.source_kind == "cnh_monthly_pemex_era"]
CNH_SRC = ("data/processed/tecolutla_production.csv (CNH monthly, source_kind cnh_monthly_pemex_era); gaps are reported "
           "zero-production months per data/processed/database_review/cnh_findings.md §1 (G-34 closed)")

def runs(well, start=None, end=None, min_gap=3):
    """Producing runs from CNH monthly rows; gaps of >= min_gap months become shut_in segments.
    Gaps shorter than min_gap months are folded into the producing run and counted in the note."""
    d = cnh[cnh.well == well]
    if start: d = d[d.date >= start]
    if end: d = d[d.date <= end]
    months = sorted(d.date.dt.to_period("M").unique())
    segs, s, prev, short = [], months[0], months[0], 0
    for m in months[1:]:
        gap = (m - prev).n - 1
        if gap >= min_gap:
            segs.append(dict(frm=str(s), to=str(prev), status="producing", short_gaps=short))
            segs.append(dict(frm=str(prev + 1), to=str(m - 1), status="shut_in", short_gaps=0))
            s, short = m, 0
        elif gap > 0:
            short += gap
        prev = m
    segs.append(dict(frm=str(s), to=str(prev), status="producing", short_gaps=short))
    out = []
    for g in segs:
        note = "CNH monthly record"
        if g["status"] == "shut_in":
            note = f"no production in the CNH record ({(pd.Period(g['to'])-pd.Period(g['frm'])).n+1} months; reported zero months)"
        elif g["short_gaps"]:
            note += f"; includes {g['short_gaps']} month(s) of short (<{min_gap}-month) zero-production gaps not shown separately"
        out.append({"from": g["frm"], "to": g["to"], "status": g["status"], "note": note, "source": CNH_SRC})
    return out

def seg(frm, to, status, note, source, uncertain=None):
    d = {"from": frm, "to": to, "status": status, "note": note, "source": source}
    if uncertain: d["uncertain"] = True; d["uncertain_why"] = uncertain
    return d

WN = "data/processed/deck_notes/wells_ops_reserves_notes.md"
DRN = "data/processed/deck_notes/drive_reads_notes.md"
GAPS = "docs/gaps.md"
BRF = "docs/18_kinjal_briefing.md"
DBR = "docs/19_database_review.md"
GOV = "docs/17_government_records.md"
PGP = "data/processed/tecolutla_production_gaps_pemex.csv"
CAS = "data/processed/wells/casing_strings.csv"
T7 = "data/processed/database_review/tec7_expediente_findings.md"
ENG = "data/processed/database_review/eng_findings.md"
CNHF = "data/processed/database_review/cnh_findings.md"
REG = "data/processed/database_review/reg_findings.md"
RES = "data/processed/database_review/res_findings.md"
RESR = "data/processed/database_review/res_review.csv"
ACCR = "data/processed/database_review/acc_review.csv"
PRES = "data/processed/database_review/pres_findings.md"
GEO = "data/processed/database_review/geo_findings.md"
LASC = "data/processed/database_review/las_findings_colab.md"
GGN = "data/processed/deck_notes/geology_geophysics_notes.md"
SURV = "data/raw/geology/Directional Survey/TECOLUTLA DIRECTIONAL SURVEY DATA.CSV"
V4 = "docs/Tecolutla_Field_History_and_TEC12_Review_v4.md"
P05 = "docs/05_pressure.md"
P04 = "docs/04_production_database.md"
P03 = "docs/03_tec11_facies.md"
P13 = "docs/13_cnh_filings_gis_cmi.md"
P09 = "docs/09_log_panel.md"
PCSV = "data/processed/pressure/tecolutla_pressures.csv"
OCRC = "data/processed/pressure/ocr/pressure_scans_ocr_check.csv"
ACCN = "data/processed/deck_notes/accounting_notes.md"
SMAP = "src/structure_map.py"
BDF = "src/block_deck_figures.py"

# ================================================================= WELLS
wells = []

# ---------------- TEC-2
tec2_tl = [
    seg("1956-04-16", "1956-05-31", "drilling", "spud 16 Apr 1956; open-hole test of 2,307.4-2,321.7 m and static pressure 24 May; deepened to 2,375 m, logged 27 May, 4 1/2 in liner cemented 28 May; rig release 31 May 1956", f"{WN} §2.4; {CAS}; {GOV}"),
    seg("1956-06-01", "1956-06-08", "testing", "perforated tests 2,345-2,349 and 2,335-2,339 m (8 Jun 1956: 72 m3/d)", f"{GOV}; {PGP}"),
    seg("1956-06-09", "1957-03", "producing", "completed 9 Jun 1956; flowing from 2,335-2,339 m to the battery to Mar 1957; no monthly volumes exist", f"{PGP} (TEC-2 1956-06..1957-03); {WN} §2.4"),
    seg("1957-04", "1971-11", "shut_in", "closed 'por alto contenido de agua salada' (high salt-water cut)", f"{PGP}; {BRF} A4"),
    seg("1971-12-27", "1972-01", "workover", "Reparacion Mayor No.1 (rig 5615) 27-29 Dec 1971: 2,335-2,339 m cemented, 2,307-2,311 m shot and acidised; to battery late Jan 1972", PGP),
] + runs("TEC-2", "1972-01-01", "2014-12-31")
tec2_tl += [
    seg("2015-01", "2016-01", "producing", "13 monthly rows exist only in a later IFR copy, integer bbl/d with water rising exactly 390 bbl/month (hand-entered, G-33); cedula gives last production 15 Jan 2016", f"{P04} §3; {GAPS} G-33, G-34; {GOV}",
        uncertain="CNH original record ends 2014-12; PEMEX Dec 2015 report says the field was closed; PE2017 gives last production Dec 2014"),
    seg("2016-02", "2018-05", "shut_in", "field shut in at handover (Acta Hora Cero 23 Nov 2016); static gradient run 27 Mar 2018", f"{P04} §3; {P05} §2"),
    seg("2018-05", "2018-05-30", "workover", "clean-out found paraffin in tubing; test and IHS build-up 8-30 May 2018 (final flow 50 bbl/d oil, 453 bbl/d water)", f"{BRF} A5; {WN} §3.3; {P05} §5"),
    seg("2018-06", "2018-08", "shut_in", "shut in for lack of water disposal", f"{BRF} A5"),
    seg("2018-09", "2018-09", "testing", "test month, 411 bbl oil sold", f"{P04} §4; tecolutla_production.csv (tonalli_monthly_test_2018)"),
    seg("2018-10", "2019-01", "shut_in", "no TEC-2 sales tickets between Sep 2018 and Jun 2019", "data/processed/tecolutla_production.csv (tonalli_trucking_sales: TEC-2 tickets only in 2018-09 and 2019-06)",
        uncertain="status inferred from the absence of sales tickets, not from a status report"),
    seg("2019-02", "2019-02", "workover", "add-perf 2,319-2,320 mKB (RTG 1 11/16 in, 3 spm) per operations log", f"{GAPS} G-59; {CAS}", uncertain="May 2019 Tonalli schematic does not show this interval (G-59 weakened)"),
    seg("2019-03", "2019-04", "shut_in", "no TEC-2 sales tickets", "data/processed/tecolutla_production.csv", uncertain="inferred from the absence of sales tickets"),
    seg("2019-05", "2019-05", "workover", "permanent plug at 2,322.5 m over wet deeper perforations; packer 2,292.65 m", f"{GAPS} G-59; {ENG} item 4"),
    seg("2019-06", "2019-09", "producing", "69-day test 47 bbl/d oil at 75 % water cut, ~250 psi; 2,045 bbl sold Jun 2019; shut in Sep 2019 as uneconomic", f"{BRF} A5; {DRN} (directors' memo 6 Sep 2019)"),
    seg("2019-09", "2020-01-30", "shut_in", "uneconomic, USD 8 k demobilisation", f"{WN} §3.3"),
    seg("2020-01-31", "2020-03", "producing", "commingled for testing with TEC-10 (GLJ note)", f"{WN} §2.4 (GLJ20 Table 2.2 note 2)", uncertain="per-well volumes after Nov 2019 not separable (G-32)"),
    seg("2020-04", "2020-06", "shut_in", "field shut in (price collapse); CNH 2020 filing zeros", f"{P13} §2"),
    seg("2020-07", "2020-09", "producing", "CNH 2020 filing origin 'Pozos Tecolutla 2 y Tecolutla 10'; GLJ Table 1 last production 2020-09; last reported rate 18 bbl/d at 72 % water cut (Sep 2020)", f"{P13} §2; {WN} §2.4; {BRF} A5", uncertain="no per-well volumes (G-32)"),
    seg("2020-10", "2022-11", "shut_in", "2021 CNH filing names TEC-10 as the only origin", f"{P13} §2"),
    seg("2022-12", "2023-01", "producing", "after a Dec 2022 workover (GLJ YE2022: restarted at 23 bopd 'but uneconomic'); 2022: 31 days on, 22.8 bbl/d on-stream, 80.4 % water cut; last production Jan 2023 at 16 bbl/d (GLJ YE2025 Table 1)", f"{RESR} rows 8, 14, 33; {GAPS} G-65"),
    seg("2023-02", None, "shut_in", "shut in since Jan 2023; GLJ YE2025 carries it PDNP with a 15 k$ workover in Aug 2026 (no record that it was done)", f"{RES} YE2024-25 table; {GAPS} G-65",
        uncertain="shut-in cause and date conflict: GLJ 'early 2023, environmental permit'; CNH filings show the field effectively shut from Jul 2022; Tonalli stopped production 4 Feb 2022"),
]

wells.append({
    "well": "TEC-2", "alias": "Tecolutla-2 (discovery well)", "uwi": "1030022460",
    "surface_x": 707586.77, "surface_y": 2262986.35, "coord_source": f"{WN} §1.1 (well header CSV, UTM 14N WGS84)",
    "kb_m": 4.00, "kb_note": "repository uses 4.00 m; PEMEX 1956/1971 and Tonalli 2016 give rotary table 3.80 m (G-58, G-72)",
    "td_mmd": 2375.0, "td_mss": 2371.0, "td_note": "vertical; TD - KB 4.00 (2,371.2 with KB 3.80); PE2017 table gives TD 2,379 m",
    "el_abra_top_mss": -2301.6, "el_abra_top_note": "tops table 2,305.64 mMD (-2,301.6 mSS); GLJ map -2,302; cuttings reading 2,320 mMD / -2,316 mSS conflicts (G-77)",
    "spud": "1956-04-16", "completed": "1956-06-09", "rig_release": "1956-05-31",
    "type": "vertical", "deviation": None,
    "purpose": "exploration (discovery well, 520 m SW of TEC-3)", "result": "producer (oil; gas at the top of El Abra on the first test)",
    "initial_test": {
        "date": "1956-06-08", "interval_mmd": "2335-2339", "oil_m3_d": 72, "oil_bbl_d": bbl(72),
        "water_pct": "8 (PEMEX expediente); 5-9 (Forma 19); ByZone 'up to 9.4'", "gor_m3_m3": 96, "gor_scf_bbl": scf(96),
        "choke": "6 mm", "source": f"{PGP} (TEC-2 1956-06 row); {GOV} (Forma 19); {WN} §2.2 (ByZone 453 bbl/d, 541 scf/bbl)",
        "other_tests_1956": [
            {"interval_mmd": "2307.4-2321.7 (open hole, after 1,900 L acid)", "oil_m3_d": 41, "oil_bbl_d": bbl(41), "gas_m3_d": 47702, "gor_m3_m3": 1163, "gor_scf_bbl": scf(1163), "choke": "6 mm", "note": "gas-cap gas at the top of El Abra; FTP 174 kg/cm2"},
            {"interval_mmd": "2345-2349", "oil_m3_d": 56, "oil_bbl_d": bbl(56), "gas_m3_d": 4320, "gor_m3_m3": 77, "gor_scf_bbl": scf(77), "note": "later squeezed; 0 bbl produced"}]},
    "intervals": [
        {"interval_mmd": "2335-2339", "interval_mss": "2331-2335", "period": "Jun 1956 - Mar 1957 (squeezed Dec 1971)", "oil_bbl": 40885, "basis": "PEMEX wellfile (6.5 x10^3 m3)"},
        {"interval_mmd": "2307.4-2311", "interval_mss": "2303.4-2307", "period": "Jan 1972 - Jan 2016; Tonalli 2018-2023", "oil_bbl": 320334, "basis": "CNH monthly to 2016-01 (3,660 bbl of it hand-entered, G-33)"},
        {"interval_mmd": "2319-2320", "interval_mss": "2315-2316", "period": "add-perf Feb 2019", "oil_bbl": None, "basis": "operations log only (G-59)"}],
    "cum_oil_bbl": 371177, "cum_oil_basis": "arithmetic sum of 40,885 (wellfile 1956-57) + 320,334 (CNH 1972-2016) + 9,958 (Tonalli era since 2018, Sep 2022 Jaguar deck per drive_reads_notes). GLJ gives 329.2 kbbl to Dec 2022 (excludes the 1956-57 wellfile volume).",
    "cum_oil_sources": f"{WN} §2.2, §2.3; {DRN} (task 18 reads); {RESR} row 8",
    "status_now": "shut in since Jan 2023; restorable on paper (GLJ YE2025: PDNP, 15 k$ workover planned Aug 2026); no record of the 2026 workover in the repository",
    "status_timeline": tec2_tl,
})

# ---------------- TEC-3
wells.append({
    "well": "TEC-3", "uwi": "1030022461", "surface_x": 707858.90, "surface_y": 2263433.11, "coord_source": f"{WN} §1.1",
    "kb_m": 6.00, "kb_note": "1956 PEMEX records give 5.78 m (G-54 update, G-72)",
    "td_mmd": 2380.5, "td_mss": 2374.5, "td_note": "vertical; TD - KB 6.00 (2,374.7 with KB 5.78); header CSV 2,381",
    "el_abra_top_mss": -2372.6, "el_abra_top_note": "tops table 2,378.58 mMD (geo_findings §3)",
    "spud": "1956-02-10", "completed": "1956-03-07", "type": "vertical", "deviation": None,
    "purpose": "exploration (first Tecolutla well)", "result": "dry: oil over salt water on test; plugged ('invaded by water')",
    "initial_test": {"date": "1956 (before 7 Mar)", "interval_mmd": "2376.8-2380.8 (open hole DST, ~2,370-2,375 mSS)", "oil_bbl_d": None,
        "recovery": "980 m of gassy oil (0.909 g/cc, ~24 API) + 80 m salt water in 1,060 m of 4 1/2 in pipe (CNH tables mis-transcribe as '980 m3')",
        "water_pct": "16 (Tecolutla Summary.xlsx)", "gor": None, "choke": None, "pressure": "20/50 kg/cm2 flowing; 230 kg/cm2 after 10-min shut-in",
        "source": f"{CNHF} §4; {ENG} item 10; {WN} §2.4"},
    "cum_oil_bbl": 0, "cum_oil_basis": "never produced",
    "status_now": "plugged and abandoned 1956 (surface shoe 601.7 m; cement plugs 2,310-2,380.5 and 571.7-625 m)",
    "status_timeline": [
        seg("1956-02-10", "1956-03-07", "drilling", "drilled to the top of El Abra; DST 2,376.8-2,380.8 m", f"{WN} §2.4; {GGN} §10.2"),
        seg("1956-03-07", None, "dry_abandoned", "abandoned 7 Mar 1956; lowest known oil -2,374.2 mSS used by GLJ as OWC", f"{CAS}; {CNHF} §4")],
})

# ---------------- TEC-5
wells.append({
    "well": "TEC-5", "uwi": "1030022462", "surface_x": 706443.52, "surface_y": 2263588.88, "coord_source": f"{WN} §1.1",
    "kb_m": 4.00, "kb_note": "LAS header 4.3 m (G-72)", "td_mmd": 2562.1, "td_mss": 2558.1, "td_note": "vertical; TD - KB",
    "el_abra_top_mss": -2551.0, "el_abra_top_note": "El Abra 2,555 mMD, 5 m penetrated, 248 m lower than TEC-2 (PEMEX 1956 final report)",
    "spud": "1956-06-25", "completed": "1956-07-28", "type": "vertical", "deviation": None,
    "purpose": "exploration (1,290 m NW of TEC-2)", "result": "dry: structurally low, water; no tests",
    "initial_test": None, "cum_oil_bbl": 0, "cum_oil_basis": "never produced",
    "status_now": "plugged and abandoned 1956",
    "status_timeline": [
        seg("1956-06-25", "1956-07-28", "drilling", "full column incl. San Felipe 58 m; El Abra 2,555 mMD", f"{DRN} (TEC-5 informe final)"),
        seg("1956-07-28", None, "dry_abandoned", "plugged 28 Jul 1956 (plugging programme dated 31 Jul 1956)", f"{CAS}; {CNHF} §4")],
})

# ---------------- TEC-6
tec6_tl = [
    seg("1956-09-08", "1956-10-16", "drilling", "spud 8 Sep, TD 16 Oct 1956 (rig release 15 Oct per ByZone)", f"{DRN} (TEC-6 informe final)"),
    seg("1956-10", "1965-12", "producing", "open hole 2,336-2,338 m; TEC-6 was the field's only producer from Mar 1957 to Oct 1971; no per-well monthly volumes before 1966 (field-level 1960-65)", f"{PGP}; {P04} §3; {BRF} A4"),
] + runs("TEC-6", "1966-01-01", "1971-07-31") + [
    seg("1971-08-02", "1971-10", "shut_in", "closed 2 Aug 1971 for a pressure build-up; 11 static surveys to 18 Oct 1971", f"{PGP}; {P05} §2"),
    seg("1971-11", "1972-01", "workover", "rigless squeeze of 2,336-2,338 m (Nov 1971), finished with rig from TEC-2 (13 Jan 1972); CNH shows 520 bbl in 6 days in Nov 1971", f"{PGP}", uncertain="CNH Nov-1971 production row vs expediente 'closed until the Nov-1971 workover'"),
] + runs("TEC-6", "1972-02-01", "1976-01-31") + [
    seg("1976-02", "1976-02", "workover", "Feb 1976 repair: 2,324-2,327 m invaded; recompleted 2,314-2,316 m; post-repair sampling 26-27 Mar 1976", PGP),
] + runs("TEC-6", "1976-03-01", "2006-12-31") + [
    seg("2007-01", "2007-02-22", "shut_in", "no 2007 production in the CNH record", CNH_SRC, uncertain="cnh_findings says the well 'ran on a PCP until 2007-02-26'"),
    seg("2007-02-23", "2007-04-03", "workover", "abandonment operations 23 Feb - 3 Apr 2007 (estado mecanico gives last intervention 5 Mar - 2 Apr 2007); gas at surface; 6 5/8 in breach 352-1,100 m", f"{CNHF} §6; {ENG} item 3; {GAPS} G-63"),
    seg("2007-04-03", None, "plugged", "plugged and abandoned by PEMEX; plugs 298.06 m, retainer 1,947.62 m, ~2,235-2,280 m", f"{CAS}; {GAPS} G-63"),
]
wells.append({
    "well": "TEC-6", "uwi": "1030022463", "surface_x": 707493.99, "surface_y": 2262529.05, "coord_source": f"{WN} §1.1",
    "kb_m": 5.67, "kb_note": "PEMEX 1956 final report 5.67 m; header CSV 6.00 m (pressure work uses 6.0)",
    "td_mmd": 2338.9, "td_mss": 2333.2, "td_note": "vertical; TD - KB 5.67",
    "el_abra_top_mss": -2296.0, "el_abra_top_note": "PEMEX 1956: 2,302 mMD / -2,296 mSS (36 m penetrated); tops table -2,294.1; GLJ -2,294",
    "spud": "1956-09-08", "completed": "1956-10-16", "type": "vertical", "deviation": None,
    "purpose": "development", "result": "producer",
    "initial_test": {"date": "1956-10", "interval_mmd": "2336-2338 (open hole, 3 7/8 in, after 960 L acid)", "oil_m3_d": 77, "oil_bbl_d": bbl(77),
        "water_pct": 3.4, "gor_m3_m3": 97, "gor_scf_bbl": scf(97), "choke": "not stated (TP 40 / TR 7 kg/cm2)",
        "source": f"{DRN} (TECOLUTLA_6_INFORME_FINAL.pdf)",
        "conflict": f"PEMEX production expediente: 92 m3/d ({bbl(92)} bbl/d) on 10 mm, RGA 104, 3.4 % water ({PGP}); ByZone 579 bbl/d, 576 scf/bbl ({WN} §2.2)"},
    "intervals": [
        {"interval_mmd": "2336-2338", "interval_mss": "2330-2332", "period": "Oct 1956 - Feb 1972", "oil_bbl": 509993, "basis": "122,004 bbl monthly records + ~388 kbbl PEMEX wellfile allocation"},
        {"interval_mmd": "2324-2327", "interval_mss": "2318-2321", "period": "Feb 1972 - Jan 1976", "oil_bbl": 84293, "basis": "CNH monthly"},
        {"interval_mmd": "2314-2316", "interval_mss": "2308-2310", "period": "Mar 1976 - Dec 2006", "oil_bbl": 305499, "basis": "CNH monthly"},
        {"interval_mmd": "2303-2304", "interval_mss": "2297-2298", "period": "-", "oil_bbl": None, "basis": "bridge plug; window above never perforated"}],
    "cum_oil_bbl": 899785, "cum_oil_basis": "ByZone sum of three intervals (509,993 + 84,293 + 305,499); ~388 kbbl of it is a wellfile allocation. CNH monthly 1966-2006 alone: 507,185 bbl (GLJ 507.2 kbbl).",
    "cum_oil_sources": f"{V4} §2.2; {WN} §2.3",
    "status_now": "plugged and abandoned 2007 (casing parted at 352 m); beside the TEC-10/TEC-12 pad",
    "status_timeline": tec6_tl,
})

# ---------------- TEC-7
tec7_tl = [
    seg("1956-11-21", "1957-01-25", "drilling", "spud 21 Nov 1956 (rig 63); TD 9 Jan 1957 at 2,340.0 m; completion dated 22, 25 or 26 Jan 1957 in different documents; rig released 27 Jan", f"{T7} header"),
    seg("1957-01-26", "1957-03-12", "producing", "flowing from 2,335-2,337 m; 4,129 m3 (26.0 kbbl) to Mar 1957 (1971 program says 3,471 m3)", f"{T7} §4-5; {PGP}"),
    seg("1957-03-12", "1971-08", "shut_in", "'rapidly invaded by salt water'; 1964 repair approved but not executed; CNH shows 40 bbl in Jun 1968, not supported by the expediente", f"{T7} §5; {PGP}", uncertain="Dec-1964 surveys quote 72-95 days shut-in, inconsistent with continuous closure since 1957"),
    seg("1971-08", "1971-10-08", "workover", "rigless workover 9 Sep - 6 Oct 1971: 2,335-2,337 m squeezed; 2,310-2,313 m perforated and acidised", f"{T7} §6"),
] + runs("TEC-7", "1971-10-01", "2006-12-31") + [
    seg("2007-01", "2019-06-15", "shut_in", "closed after Dec 2006 (PE2017); cedula 15 Mar 2017: closed, hermetic, last line 18.7 bbl/d at 45 % water", f"{GOV}; {WN} §2.4"),
    seg("2019-06-16", "2019-06-23", "workover", "minor repair from 16 Jun 2019; Quimica Apollo stimulation 23 Jun 2019", f"{GAPS} G-57"),
    seg("2019-06-24", "2019-08-06", "testing", "2,310-2,313 m made 182 bbl/d water, 100 % water cut; 3,252 bbl hauled Jun-Jul 2019", f"{BRF} A5; {P04} §4"),
    seg("2019-08-07", "2023-01", "injector", "produced-water disposal by triplex pump from 7 Aug 2019; ASEA authorisation 1712/2019 (15 Nov 2019); ASEA compliance reports May-Nov 2020 and Jun-Nov 2021; injection-pump costs Dec 2020 and Sep 2022 (LOS); no volumes or pressures in any file (G-57)", f"{BRF} A5; {GAPS} G-57; {ACCR}",
        uncertain="end date not recorded; set to the field's last production month (Jan 2023) as the latest date water needed disposal"),
    seg("2023-02", None, "shut_in", "2024 abandonment sheet lists TEC-7 as 'Shut-in' (injection string not mentioned)", f"{DRN} (Fideicomiso 2024-2025)",
        uncertain="start of shut-in inferred from the field shut-in; current wellhead state unknown (G-57)"),
]
wells.append({
    "well": "TEC-7", "uwi": "1030022466 (UWIs of TEC-7 and TEC-101 swapped in the header CSV, G-74)", "surface_x": 707945.70, "surface_y": 2262705.90, "coord_source": f"{WN} §1.1",
    "kb_m": 4.80, "kb_note": "all 1956-71 PEMEX records: rotary table 4.80 m, ground 1.34 m (G-58 closed); repository earlier used 5.00",
    "td_mmd": 2340.0, "td_mss": 2335.2, "td_note": "vertical; driller TD 2,340.0 m; informe final 2,340.5 m / 2,335.5 mbnm",
    "el_abra_top_mss": -2304.0, "el_abra_top_note": "E-log corrected top 2,309 mbmr / -2,304 mbnm (expediente p70); tops table -2,304.0; GLJ -2,304.2",
    "spud": "1956-11-21", "completed": "1957-01-25", "completed_note": "22 Jan (schematic), 25 Jan (cedula/informe final) or 26 Jan 1957 (1964 program)",
    "type": "vertical", "deviation": None, "purpose": "development", "result": "producer (later produced-water injector)",
    "initial_test": {"date": "1957-01-23", "interval_mmd": "2335-2337", "oil_m3_d": 89, "oil_bbl_d": bbl(89), "water_pct": "4.8 (radiogram) / 2.2 (informe final)",
        "gor_m3_m3": 93, "gor_scf_bbl": scf(93), "choke": "6 mm", "note": "2-hour test; FTP 68, FCP 54 kg/cm2; gas 8,300 m3/d",
        "source": f"{T7} §4",
        "conflict": f"repository/ByZone 352 bbl/d (521 scf/bbl, 7.5 % water) is the 56 m3/d ({bbl(56)} bbl/d) first full day to battery, 25 Jan 1957 (G-81)"},
    "recompletion_test": {"date": "1971-10-06", "interval_mmd": "2310-2313 (2305-2308 mSS)", "oil_m3_d": 76, "oil_bbl_d": bbl(76), "water_pct": 0.2, "gor_m3_m3": 78, "gor_scf_bbl": scf(78), "choke": "5 mm", "source": f"{T7} §6"},
    "intervals": [
        {"interval_mmd": "2335-2337", "interval_mss": "2330-2332", "period": "Jan-Mar 1957 (+40 bbl Jun 1968 in CNH)", "oil_bbl": 25971, "basis": f"4,129.0 m3 x 6.2898 (expediente p56; alt. 3,471 m3 = {round(3471*M3_BBL)} bbl)"},
        {"interval_mmd": "2310-2313", "interval_mss": "2305-2308", "period": "Oct 1971 - Dec 2006", "oil_bbl": 266988, "basis": "CNH monthly"}],
    "cum_oil_bbl": 293001, "cum_oil_basis": "arithmetic: 266,988 (CNH 1971-2006) + 40 (Jun 1968) + 25,971 (1957, 4,129 m3). GLJ 267.0 kbbl excludes 1957.",
    "cum_oil_sources": f"{V4} §2.2; {T7}",
    "status_now": "shut in; equipped as produced-water injector (2 3/8 in string, packer ~2,300 m, Aug 2019); current wellhead state unknown (G-57)",
    "status_timeline": tec7_tl,
})

# ---------------- TEC-9
tec9_tl = [seg("1973-04-01", "1973-05-19", "drilling", "spud 1 Apr, TD 7 May, completed 19 May 1973", f"{DRN} (BLOQUE_TECOLUTLA_9_ESTADO_MECANICO)")] \
    + runs("TEC-9", "1973-05-01", "1999-01-31") + [
    seg("1999-02", "2003-05", "shut_in", "closed Jan 1999 (PEMEX estado mecanico); CNH zero rows Feb 1999 - May 2003; field-wide shut-in", f"{GAPS} G-62; {ENG} item 7"),
] + runs("TEC-9", "2003-06-01", "2012-07-31") + [
    seg("2012-08", "2012-09", "shut_in", "after Jul 2012 last CNH month", CNH_SRC),
    seg("2012-10", "2012-11", "workover", "failed workover: restriction milled, casing damage 544-718 m; squeeze with retainer 2,312.36 m, plugs 736-470 m", f"{REG} finding 7; {CNHF} §6; {WN} §2.4"),
    seg("2012-12", "2013-01-03", "shut_in", "definitive plug pending in Dec 2012 (XPS logs)", CNHF),
    seg("2013-01-04", None, "plugged", "plugged 4 Jan 2013; WP calls it 'closed, not properly abandoned', wellhead a safety/environmental hazard; returned to CNH/SENER by Tonalli", f"{GAPS} G-62; {WN} §2.4",
        uncertain="'plugged' (CNH files) vs 'temporarily abandoned Nov 2012' (cnh_findings) vs 'not properly abandoned' (Work Program)"),
]
wells.append({
    "well": "TEC-9", "uwi": "1030022465", "surface_x": 707833.50, "surface_y": 2262336.31,
    "coord_source": f"{WN} §1.1 (header CSV); PEMEX estado mecanico prints UTM 707,873.67 / 2,262,243.38 (~100 m away; datum not stated, G-74)",
    "kb_m": 5.07, "kb_note": "PEMEX estado mecanico 5.07 m (GL 1.24); header CSV 5.00",
    "td_mmd": 2340.0, "td_mss": 2326.1, "td_note": "PEMEX: TD 2,340 mMD = 2,331.2 mTVD (KB 5.07). Directional survey CSV gives 2,324.85 mTVD / -2,319.85 mSS at 2,340 mMD (conflict)",
    "el_abra_top_mss": -2296.0, "el_abra_top_note": "2,310 mMD / 2,301 mTVD KB / -2,296 mSS (estado mecanico); GLJ -2,295.87; every source agrees",
    "spud": "1973-04-01", "completed": "1973-05-19", "type": "deviated",
    "deviation": {"kickoff_m": 296, "direction": "N6 deg 15 min W", "max_inclination": "11 deg 15 min", "displacement_m": 112,
        "back_to_vertical_from_mmd": 1192, "cause": "a dropped piece of equipment changed the plan (WP); fish (4 1/2 in slips) at 388 m in the first hole",
        "source": f"{DRN} (estado mecanico); {WN} §2.4",
        "conflicts": "Work Program displacement 117.9 m (117.2 N, 12.5 W); directional survey CSV (UWI 1030022465) holds 9.5 deg from 1,928 m to TD and 205 m N at TD"},
    "purpose": "development", "result": "producer",
    "initial_test": {"date": "1973-05", "interval_mmd": "2328-2333", "interval_mss": "2314-2319 (estado mecanico TVD 2,319-2,324 mTVD) vs 2,323-2,328 (MD - KB, docs/09)",
        "oil_bbl_d": 189, "water_pct": 0.6, "gor_scf_bbl": 765, "choke": "3.5 mm (estado mecanico)", "source": f"{WN} §2.2 (ByZone Test Info)",
        "conflict": f"PEMEX estado mecanico: 91.6 m3/d ({bbl(91.6)} bbl/d) on 3.5 mm, RGA 230 m3/m3 ({scf(230)} scf/bbl). CNH peak month Dec 1973 155 bbl/d. Estado mecanico 'final Sep 1998' 30 m3/d ({bbl(30)} bbl/d) vs CNH Sep 1998 15 bbl/d at 75 % water."},
    "cum_oil_bbl": 352601, "cum_oil_basis": "CNH monthly May 1973 - Jul 2012 (one interval); 266,478 bbl water",
    "cum_oil_sources": f"{V4} §2.2; {WN} §2.3",
    "status_now": "plugged 4 Jan 2013; wellhead flagged as a hazard; returned to CNH/SENER",
    "status_timeline": tec9_tl,
})

# ---------------- TEC-101
wells.append({
    "well": "TEC-101", "uwi": "1030022464 (swapped with TEC-7 in header CSV, G-74)", "surface_x": 707336.30, "surface_y": 2262779.00, "coord_source": f"{WN} §1.1",
    "kb_m": 8.00, "kb_note": "LAS header 7.6 m (G-72)", "td_mmd": 2804.0, "td_mss": 2796.0, "td_note": "vertical; PEMEX TD 2,804 m; header CSV 2,363 m is unexplained",
    "el_abra_top_mss": -2334.0, "el_abra_top_note": "2,341 mMD (CD tops table; casing CSV 2,342); sharp on ILD and sonic",
    "spud": "1972-01-28", "completed": "1972-03-31", "completed_note": "drilled 28 Jan - 16 Mar 1972, plugged 31 Mar 1972 (G-61); ByZone gives rig release 31 May 1972; the 15 Apr / 31 Oct 1972 dates belong to Cuesta Blanca-2",
    "type": "vertical", "deviation": None, "purpose": "exploration / delineation", "result": "dry: water-invaded, structurally low",
    "initial_test": None, "cum_oil_bbl": 0, "cum_oil_basis": "never produced",
    "status_now": "plugged and abandoned 1972 (plug monument dated 3 Apr 1972)",
    "status_timeline": [
        seg("1972-01-28", "1972-03-16", "drilling", "logs dated 22 Feb 1972; open hole 8 5/8 in 2,718-2,804 m", f"{GAPS} G-61; {CAS}"),
        seg("1972-03-31", None, "dry_abandoned", "plugged 31 Mar 1972, water-invaded", f"{GAPS} G-61")],
})

# ---------------- TEC-10
tec10_tl = [
    seg("2018-04-11", "2018-05-04", "drilling", "spud 11 Apr (QMAX/conductor) or 16 Apr 2018 (masterlog); core 28-30 Apr; TD 1 May; logs 2 May; liner cemented 4 May", f"{WN} §2.4; {DRN}"),
    seg("2018-05-05", "2018-09-19", "testing", "CBL 31 May; zone A injectivity 30 Jun-1 Jul; zone B weak water inflow; zone C flowback 23 Jul-6 Aug; IHS build-up to 31 Aug", f"{WN} §2.4; {ENG} item 9; {P05}"),
    seg("2018-09-20", "2020-03", "producing", "daily record 20 Sep 2018 - 24 Nov 2019 (44,468 bbl); commingled sales after; last load 20 Mar 2020", f"{P04} §4; {WN} §3.3"),
    seg("2020-04", "2020-06", "shut_in", "field shut in (price collapse)", f"{P13} §2"),
    seg("2020-07", "2022-02-04", "producing", "2021 CNH filing: TEC-10 only origin, 17,402 bbl, 81 % water; Dec 2021 ~34 bbl/d at 86 % water", f"{P13} §2; cnh_production_filings_2020_2022.csv"),
    seg("2022-02-04", "2022-11-23", "shut_in", "production stopped 4 Feb 2022 after CNH rejected the evaluation report; Jaguar deck: 'stim required during restart'. CNH monthly shows 189 bbl (Aug) and 49 bbl (Sep 2022) into tank inventory, well not named", f"{DRN} (20220209 Aviso paro); {BRF} A5; {P13} §2",
        uncertain="Aug-Sep 2022 field volumes (238 bbl) are not attributed to a well"),
    seg("2022-11-24", "2023-01", "producing", "restart after a Nov-2022 stimulation (USD 20,003): 15 days, 678 bbl net, 1,582 bbl water; last production Jan 2023 at 2 bbl/d (GLJ)", f"{P13} §2; {ACCR} (2022 LOS); {RES}"),
    seg("2023-02", None, "shut_in", "shut in; GLJ: 'producing at marginal rates and requires a workover to alleviate paraffin' (YE2022), PDNP with 15 k$ workover Aug 2026 (YE2025)", f"{RESR} rows 8, 33",
        uncertain="shut-in cause and date conflict (G-65)"),
]
wells.append({
    "well": "TEC-10", "alias": "TEC-10DES", "uwi": "TEC_10", "surface_x": 707574.96, "surface_y": 2262437.07,
    "coord_source": f"{SURV} (row MD 0) and header CSV; masterlog prints surface 707,554.956 / 2,262,437.068 (20 m different in X, unresolved)",
    "kb_m": 6.13, "kb_note": "adopted by decision 16 Sep 2026 (G-46); masterlog, CBL and Weatherford headers give 5.13; PETRA LAS EKB 6.1",
    "td_mmd": 2490.0, "td_mss": 2447.39, "td_note": "survey: 2,490 mMD = 2,453.52 mTVD = -2,447.39 mSS",
    "el_abra_top_mss": -2309.7, "el_abra_top_note": "tops table 2,344.58 mMD (-2,309.7); log top -2,309.5 to -2,310.3; XRD top 2,348 mMD (-2,312.9); GLJ -2,309.93",
    "spud": "2018-04-11", "completed": "2018-09-20", "completed_note": "TD 1 May 2018; on production from 20 Sep 2018 (daily record) / 7-8 Oct 2018 (transition-plan docx)",
    "type": "directional",
    "deviation": {"shape": "J", "kickoff_mmd": "~1,590 (survey inclination exceeds 1 deg from 1,589 mMD)", "inclination": "~18-20 deg from ~1,880 mMD to TD", "azimuth": "~S 8-10 deg E (170-174 deg)",
        "target_x": 707589.60, "target_y": 2262253.10, "target_source": "masterlog 'Objetivo'",
        "bhl_x": 707597.80, "bhl_y": 2262198.67, "bhl_source": SURV,
        "displacement_m": 193.3, "displacement_note": "192.59 m S, 16.56 m E (Work Program)", "source": f"{SURV}; {WN} §2.4"},
    "purpose": "development / appraisal (cored, modern log suite)", "result": "producer (oil from zone C; zones A and B no oil)",
    "initial_test": {"date": "2018-08-06", "interval_mmd": "2349.5-2350.5 + 2351.5-2353.0 (zone C)", "interval_mss": "2314.3-2317.6 (survey; By Zone sheet 2,311.5-2,315, G-46)",
        "oil_bbl_d": 193.6, "water_pct": 39.1, "gor_scf_bbl": 743, "choke": "12/64 in", "whp_psig": 863,
        "note": "last day of the post-stimulation flowback 23 Jul - 6 Aug 2018 (oil 41 -> 194 bbl/d, BS&W 89 -> 39 %, 1,475 bbl). Jaguar deck: 182 bbl/d at 39 % water, ~880 psi (Jul 2018). Peak daily 231.6 bbl/d on 20 Oct 2018 (762 scf/bbl, 25.3 % water, 772 psi)",
        "source": "data/processed/welltest/tec10_welltest_2018_daily.csv; " + f"{BRF} A5; {WN} §2.2"},
    "cum_oil_bbl": 77100, "cum_oil_basis": "GLJ YE2022: 77.1 kbbl to 31 Dec 2022 (Jan 2023 adds a few bbl). Other bases: 44,468 (daily sheet to 24 Nov 2019); 47,811 (ByZone to Mar 2020); 58.4 kbbl (GLJ to Dec 2020); 75,832 (Jaguar deck to Dec 2021)",
    "cum_oil_sources": f"{RESR} row 8; {P04} §4; {WN} §2.3",
    "status_now": "shut in since Jan 2023; restorable per GLJ (PDNP, paraffin workover 15 k$ planned Aug 2026); no record the workover was done",
    "status_timeline": tec10_tl,
})

# ---------------- TEC-11
wells.append({
    "well": "TEC-11", "alias": "TEC-11DES", "uwi": "TEC-11DES", "surface_x": 707605.00, "surface_y": 2263031.17,
    "coord_source": f"{SURV} (row MD 0; TEC-2 pad)", "kb_m": 4.70, "kb_note": "SLB CBL headers carry 6.13 (copied from TEC-10, G-72)",
    "td_mmd": 3283.0, "td_mss": 2331.02, "td_note": "survey: 3,283 mMD = 2,335.72 mTVD = -2,331.02 mSS at 81.95 deg",
    "el_abra_top_mss": None, "el_abra_top_note": "unresolved (G-75): tops table -2,311.9 (2,611.8 mMD); mud-log carbonate onset 2,360 mMD (-2,245 mSS, called 'Tantoyuca_A' in the tops table); lateral 4-10 m above the Jan-2019 grid top; lateral sonic median 73 us/ft like Tantoyuca marl",
    "spud": "2018-11-11", "spud_note": "11 Nov 2018 (cost tracker day 1, CNH notice); accounting notes say 9 Nov 2018 (pre-spud 9-13 Nov)",
    "completed": "2019-09-06", "rig_release": "2018-12-26", "type": "horizontal",
    "deviation": {"kickoff": "below 1,000 mMD", "landing": "80 deg at 2,563 mMD (2,304.6 mSS); 90 deg at 2,727 mMD (2,322.9 mSS)", "azimuth": "316 deg building to 327-331 deg",
        "lateral_mss": "2,305-2,331, held 2,322-2,324 from 2,727 to 3,140 mMD", "bhl_x": 706847.16, "bhl_y": 2263952.40, "displacement_m": 1190,
        "source": f"{P03} §2; {SURV}"},
    "purpose": "horizontal development / proof of concept for horizontal wells (TEC-12, TEC-13 were carried as horizontals at 694 bbl/d each in the Jan 2019 forecast)",
    "result": "water (100 % water cut); trace oil",
    "initial_test": {"date": "2019-07-11", "interval_mmd": "2643.5-2745.5 (five 3-m perforations, 2,316-2,323 mSS)", "oil_bbl_d": 0, "water_bbl_d": 260, "water_pct": 100,
        "gor": None, "choke": "12/64 in", "whp_psi": 195, "note": "final Tonalli schematic (25 Sep 2019): 286 bbl/d water, 100 % water cut; Tantoyuca retest Aug 2019 trace 17 API oil and 96 bbl/d water",
        "source": f"{DRN} (Anexo 4 aviso abandono temporal); {BRF} A5"},
    "cum_oil_bbl": 0, "cum_oil_basis": "no oil sold; 4,397 bbl water hauled May-Aug 2019 (only production record)",
    "status_now": "temporarily abandoned (CNH art. 54 notice Apr 2022); composite plug ~2,400 mMD; reclassified as injector candidate Oct 2019",
    "status_timeline": [
        seg("2018-11-11", "2018-12-26", "drilling", "TD 18 Dec 2018; rig release 26 Dec 2018", f"{WN} §2.4"),
        seg("2018-12-27", "2019-04", "shut_in", "awaiting completion; CBL / wellbore clean-up Jan 2019 (USD 129,360)", f"{ACCN} §2"),
        seg("2019-05", "2019-06", "workover", "completion: fish (bit + watermelon mill) left at 2,866-2,872 mMD; five perforations 2,643.5-2,745.5 mMD; acid bullheaded without isolation", f"{CAS}; {DBR} §2.10; {DRN}"),
        seg("2019-07", "2019-08-10", "testing", "11 Jul 2019: 260 bbl/d water on 12/64 in, 195 psi", DRN),
        seg("2019-08-11", "2019-08-12", "plugged", "Boss composite blind plug set at ~2,400 mMD, killed with 1.06 brine, no cement", DRN),
        seg("2019-08-13", "2019-09-06", "testing", "Tantoyuca test (oil sample 22 Aug 2019 from 2,361-2,364 m: 17.0 API); completion finished 6 Sep 2019", f"data/processed/deck_notes/fluids_rock_core_notes.md; {DRN}"),
        seg("2019-09-07", None, "plugged", "closed pending possible water injection; temporary abandonment notice Apr 2022", DRN, uncertain="temporarily abandoned, not permanently plugged")],
})

# ---------------- TEC-12
wells.append({
    "well": "TEC-12", "alias": "TEC-12DES (planned)", "surface_x": 707582.0, "surface_y": 2262425.0,
    "coord_source": "Prog12 conductor location (wells_ops_reserves_notes §2.4); seismic_findings.md §5; src/structure_map.py",
    "kb_m": 8.2, "kb_note": "planned GL 4.5 m + 3.7 m table",
    "td_mmd": 2360.0, "td_mss": 2332.8, "td_note": "Programa de perforacion Sept 2020: TD 2,360 mMD / 2,341 mTVD / -2,332.8 mSS; Work Program and AFE S-shape: TD 2,370 mMD / 2,352.6 mTVD",
    "el_abra_top_mss": -2296.0, "el_abra_top_note": "prognosis -2,296 mSS (2,323.2 mMD, 2,304.2 mTVD; a TEC-6 analogue); Jan-2019 grid -2,289.4; PEMEX PSTM estimate -2,293 (+/- ~4 m)",
    "spud": None, "completed": None, "type": "planned",
    "deviation": {"shape": "S-shape (build to 13.5-15 deg, drop to vertical by 1,560 mMD) or build-and-hold 14-15 deg", "azimuth_deg": 78.433, "displacement_m": 174.5,
        "bhl_x": 707754.0, "bhl_y": 2262460.0, "bhl_note": "Prog12 target 707,753 / 2,262,460; seismic_findings/structure_map 707,754 / 2,262,460",
        "source": f"{WN} §2.4; {SMAP}"},
    "purpose": "development / appraisal-producer from the TEC-10 pad; target the top ~8 m of El Abra at the crest (TEC-9 analogue)", "result": "not drilled",
    "initial_test": None, "cum_oil_bbl": 0, "cum_oil_basis": "not drilled",
    "planned_cost": "AFE USD 1,572,724 (Nov 2020 pricing); PPI-indexed USD 2.04 MM (Sep 2026); GLJ YE2025 capex 1.9 MM$ in Jul 2028",
    "status_now": "planned, not drilled (Oct 2026); GLJ YE2025 schedules it for Jul 2028 (text says 2027)",
    "status_timeline": [seg("2019-01", None, "planned", "first appears as a horizontal at 694 bbl/d in the Jan 2019 forecast; directional programme Sept 2020; in the Programa de Transicion approved 18 Jul 2022; GLJ on-stream date slipped May 2021 -> 2022 -> Sep 2023 -> 2025 -> Apr 2027 -> Jul 2028", f"{ENG} item 6; {RES}; {WN} §2.4")],
})

# ================================================================= EVENTS
events = []
def E(date, well, cat, title, detail, source, uncertain=None):
    assert len(title) <= 60, (len(title), title)
    d = {"date": date, "well": well, "category": cat, "title": title, "detail": detail, "source": source}
    if uncertain: d["uncertain"] = True; d["uncertain_why"] = uncertain
    events.append(d)

E("1956-02-10", "TEC-3", "drilling", "PEMEX spuds TEC-3, the first Tecolutla well",
  "Exploration well drilled to the top of the El Abra reef; TD 2,380.5 m.", f"{WN} §2.4 (PE2017)")
E("1956-03-07", "TEC-3", "abandonment", "TEC-3: oil over salt water on test, plugged",
  "Drill-stem test of 2,376.8-2,380.8 m (~2,370-2,375 mSS) recovered 980 m of gassy ~24 API oil and 80 m of salt water in the pipe; plugged 7 Mar 1956. Its lowest known oil (-2,374.2 mSS) is GLJ's oil-water contact.",
  f"{CNHF} §4; {ENG} item 10; {WN} §2.4")
E("1956-04-16", "TEC-2", "drilling", "TEC-2 spudded 520 m SW of TEC-3",
  "The discovery well; vertical, 13 1/4 in hole to 610 m, 9 5/8 in casing at 607.9 m.", f"{GGN} §10.2; {CAS}")
E("1956-05-24", "TEC-2", "test", "TEC-2 top of El Abra flows gas-rich oil",
  f"Open hole 2,307.4-2,321.7 m after 1,900 L acid: 41 m3/d ({bbl(41)} bbl/d) oil with 47,702 m3/d gas (GOR 1,163 m3/m3, ~6,500 scf/bbl) on a 6 mm choke: gas-cap gas at the top of El Abra.",
  f"{GOV}; {WN} §2.4")
E("1956-05-24", "TEC-2", "pressure", "Initial pressure 252 kg/cm2 (24.65 MPa)",
  "Static 252.0 kg/cm2 at 2,310 m after only 2 h 45 min shut-in (built up from 243.2); 24.65 MPa (3,575 psia) at the 2,300 mSS datum. PEMEX's 'initial pressure'. PEMEX estimated 263-410 mD from this test.",
  f"{P05} §2-3; {ENG} item 5; {GAPS} G-36")
E("1956-05-31", "TEC-2", "drilling", "TEC-2 deepened to 2,375 m, liner run",
  "Deepened with a 5 5/8 in bit to 2,375 m, logged 27 May (E-log, microlog, radioactive), 4 1/2 in liner 2,288.7-2,375 m cemented 28 May; rig released 31 May 1956.",
  f"{GOV}; {CAS}")
E("1956-06-08", "TEC-2", "test", "TEC-2 tests 453 bbl/d from 2,335-2,339 m",
  f"72 m3/d ({bbl(72)} bbl/d) oil, GOR 96 m3/m3 (~{scf(96)} scf/bbl), 5-9 % water of 45,000-50,000 ppm on 6 mm. A deeper test at 2,345-2,349 m gave 56 m3/d ({bbl(56)} bbl/d) and was later squeezed.",
  f"{GOV}; {PGP}")
E("1956-06-09", "TEC-2", "completion", "Discovery: TEC-2 completed in El Abra",
  "Completed 9 Jun 1956 as an oil producer from 2,335-2,339 m (2,331-2,335 mSS) and put on the battery as a flowing well in June 1956.",
  f"{WN} §2.4; {PGP}")
E("1956-07-28", "TEC-5", "abandonment", "TEC-5 finds El Abra 248 m low, plugged",
  "El Abra at 2,555 mMD (-2,551 mSS), 248 m lower than TEC-2 and water-bearing; no tests; plugged 28 Jul 1956. Marks the separation from the Miguel Hidalgo field.",
  f"{DRN}; {CAS}")
E("1956-09-08", "TEC-6", "drilling", "TEC-6 spudded", "Development well on the crest; El Abra reached at 2,302 mMD (-2,296 mSS), 7 m higher than TEC-2.", f"{DRN}")
E("1956-10", "TEC-6", "completion", "TEC-6 completed open hole: ~480-580 bbl/d",
  f"Open hole 2,336-2,338 m (2,330-2,332 mSS) after 960 L acid: 77 m3/d ({bbl(77)} bbl/d) oil, 3.4 % water (final report). The production file gives 92 m3/d ({bbl(92)} bbl/d) on 10 mm.",
  f"{DRN}; {PGP}", uncertain="two PEMEX documents give different initial rates")
E("1956-11-21", "TEC-7", "drilling", "TEC-7 spudded", "Development well 456 m from TEC-2; TD 2,340 m on 9 Jan 1957.", f"{T7}")
E("1957-01-23", "TEC-7", "test", "TEC-7 tests 560 bbl/d from 2,335-2,337 m",
  f"2-hour test on 6 mm: 89 m3/d ({bbl(89)} bbl/d) oil, 8,300 m3/d gas, GOR 93 m3/m3. First full day to battery (25 Jan) was 56 m3/d ({bbl(56)} bbl/d), the figure usually quoted.",
  f"{T7} §4; {GAPS} G-81", uncertain="completion date given as 22, 25 or 26 Jan 1957")
E("1957-03", "TEC-2", "shut_in", "TEC-2 shut in for salt water",
  "Flowed from 2,335-2,339 m from Jun 1956 to Mar 1957, ending at 45 m3/d (283 bbl/d) with 80 % water on 4 mm; 6.5 x10^3 m3 (40,885 bbl). Closed 'por alto contenido de agua salada' until 1971.",
  f"{PGP}; {BRF} A4")
E("1957-03-12", "TEC-7", "shut_in", "TEC-7 shut in after 7 weeks: salt water",
  "Interval 'rapidly invaded by salt water'; last rate 15 m3/d with 44 % water on 3 mm, 50,000 ppm. 4,129 m3 (26.0 kbbl) produced; the 1971 programme says 3,471 m3.",
  f"{T7} §5")
E("1957-04", "FIELD", "production", "TEC-6 alone carries the field to 1971",
  "With TEC-2 and TEC-7 closed by salt water, TEC-6 was the only producer from spring 1957 until Oct 1971 (one 40-bbl TEC-7 month in Jun 1968 in the CNH table is not supported by the PEMEX file).",
  f"{PGP}; {BRF} A4; {P04} §1")
E("1960-01", "FIELD", "production", "First monthly records: about 100 bbl/d",
  "CNH field-level monthly series begins (no well split): 1960 average 103 bbl/d; 182 kbbl in 1960-65 at 75-115 bbl/d. Nothing monthly exists before 1960.",
  f"{P04} §2-3; data/processed/tecolutla_field_monthly.csv")
E("1964-12-02", "TEC-6", "pressure", "TEC-6 flowing survey: 194 kg/cm2",
  "Flowing 193.63 kg/cm2 at 2,337 m on a 3 mm choke, 9 m3/d (57 bbl/d) oil, 3 % water, RGA 122 m3/m3 (685 scf/bbl). Not a static pressure.",
  f"{PCSV}; {P05} §2")
E("1964-12-08", "FIELD", "pressure", "1964 statics: still ~252 kg/cm2",
  "TEC-2 after 75-78 days shut-in and TEC-7 after 95 days read 251.7-252.0 kg/cm2 at gauge: 24.36-24.66 MPa at 2,300 mSS, after ~0.58 MMbbl including wellfile allocations.",
  f"{P05} §2-3; {PCSV}", uncertain="TEC-7 expediente dates its survey 12 Dec 1964 at 251.90 kg/cm2, and the 95-day shut-in conflicts with closure since 1957")
E("1964", "TEC-7", "workover", "TEC-7 repair approved but never done",
  "1964 programme: plug at 2,330 m and new perforations at 2,325-2,327 m. Approved, but the well was still shut with 2,335-2,337 m open in Dec 1964.",
  f"{T7} §5")
E("1966-01", "TEC-6", "production", "Per-well monthly record begins (TEC-6)",
  "CNH per-well record starts; TEC-6 alone at 66-105 bbl/d in 1966 with 2-19 % water.",
  "data/processed/tecolutla_production.csv (TEC-6 1966)")
E("1971-08-02", "TEC-6", "pressure", "TEC-6 closed for a 74-day build-up",
  "Eleven static surveys at 2,337 m, 6 Aug - 18 Oct 1971: 240.3 rising to 251.6 kg/cm2, i.e. 23.24 -> 24.35 MPa at datum. Short shut-ins understate pressure by up to 1 MPa.",
  f"{P05} §2-3; {OCRC}")
E("1971-10-09", "TEC-7", "workover", "TEC-7 recompleted 25 m higher: 478 bbl/d",
  f"Rigless workover 9 Sep - 6 Oct 1971: 2,335-2,337 m squeezed with 5,000 kg cement; 2,310-2,313 mbmr (2,305-2,308 mSS) perforated and acidised (2 m3 15 % HCl); 76 m3/d ({bbl(76)} bbl/d), GOR 78 m3/m3, 0.2 % water on 5 mm; to battery 9 Oct.",
  f"{T7} §6")
E("1971-11", "TEC-6", "workover", "TEC-6 squeezed and moved up to 2,324-2,327 m",
  "Original open hole 2,336-2,338 m (~510 kbbl, mostly a wellfile allocation) cement-squeezed in Nov 1971; finished with the rig from TEC-2 (13 Jan 1972); 2,324-2,327 m (2,318-2,321 mSS) on production Feb 1972, test 264 bbl/d, 2 % water.",
  f"{PGP}; {WN} §2.2")
E("1971-12-27", "TEC-2", "workover", "TEC-2 recompleted at 2,307-2,311 m",
  "Major workover 27-29 Dec 1971: 2,335-2,339 m cemented, 2,307-2,311 m (2,303-2,307 mSS) perforated and acidised; to battery late Jan 1972. PEMEX's Oct 1971 schematic marks a gas-oil level at 2,319 mKB (~2,315 mSS).",
  f"{PGP}; {DRN} (Tecolutla-2 Schematic Oct 1971)")
E("1972-01-28", "TEC-101", "drilling", "TEC-101 spudded", "Exploration/delineation well west of the crest; drilled to 2,804 m by 16 Mar 1972.", f"{GAPS} G-61")
E("1972-03", "FIELD", "production", "Field peak: 932 bbl/d in March 1972",
  "Monthly record: TEC-7 442 + TEC-2 269 + TEC-6 221 = 931.6 bbl/d (28,881 bbl in 31 days), three wells, ~0 % water. The 1972 calendar-day average was 624 bbl/d.",
  "data/processed/tecolutla_production.csv (CNH monthly, 1972-03); data/processed/tecolutla_field_monthly.csv; Resumen via wells_ops_reserves_notes §1")
E("1972-03-31", "TEC-101", "abandonment", "TEC-101 water-invaded, plugged",
  "El Abra at 2,341 mMD (-2,334 mSS), structurally low; open hole 2,718-2,804 m water-invaded; plugged 31 Mar 1972. Never produced.",
  f"{GAPS} G-61; {CAS}", uncertain="ByZone gives rig release 31 May 1972; header CSV TD 2,363 m vs 2,804 m")
E("1973-04-01", "TEC-9", "drilling", "TEC-9 spudded (deviated to 112 m N)",
  "A dropped piece of equipment forced a deviation from 296 m, N6 15'W, max 11 15', 112 m displacement, back to vertical from 1,192 m; TD 2,340 mMD (2,331.2 mTVD) on 7 May 1973.",
  f"{DRN}; {WN} §2.4")
E("1973-05-19", "TEC-9", "completion", "TEC-9 completed at 2,328-2,333 m",
  f"Initial test 189 bbl/d, 765 scf/bbl, 0.6 % water (ByZone). The PEMEX estado mecanico gives 91.6 m3/d ({bbl(91.6)} bbl/d) on 3.5 mm, RGA 230. This one interval later made 352,601 bbl.",
  f"{WN} §2.2, §2.4; {DRN}", uncertain="initial-rate conflict; interval depth is 2,314-2,319 mSS on the PEMEX TVD but 2,323-2,328 mSS as MD-KB in docs/09")
E("1973-06-04", "TEC-6", "pressure", "TEC-6 flowing survey 232 kg/cm2",
  "Flowing 232.2 kg/cm2 at 2,315 m before shut-in (22.68 MPa at datum); flowing BHP 16.6 MPa. The Work Program table lists it as a 22.8 MPa static.",
  f"{PCSV}; {WN} §2.5", uncertain="labelled static in the Work Program, flowing in the scan/IFR summary")
E("1974-10", "FIELD", "shut_in", "Field-wide shut-in, Oct 1974 - Apr 1975",
  "CNH monthly table shows zero production in every well for seven months; no reason recorded.", f"{ENG} item 7; {CNHF} §1")
E("1976-03", "TEC-6", "workover", "TEC-6 moved up again to 2,314-2,316 m",
  "Feb 1976 repair: 2,324-2,327 m water-invaded after 84,293 bbl; recompleted at 2,314-2,316 m (2,308-2,310 mSS), on production Mar 1976. A bridge plug at 2,303-2,304 m (2,297 mSS) left the window above unperforated.",
  f"{PGP}; {V4} §2.2; {P09} §3")
E("1977-08", "TEC-6", "production", "TEC-6 second peak: 293 bbl/d",
  "Best month of the 2,314-2,316 m interval (293 bbl/d); field average 347 bbl/d in 1977. This interval made 305,499 bbl to Dec 2006.",
  f"{WN} §2.2; data/processed/tecolutla_field_monthly.csv")
E("1978-06", "FIELD", "shut_in", "Field-wide shut-in, Jun 1978 - Sep 1979",
  "Sixteen months of zero production in all wells (CNH zero rows); 1979 field average 12 bbl/d. Reason not recorded.", f"{ENG} item 7; {CNHF} §1")
E("1980", "FIELD", "production", "1980s: wells cycled at 25-40 bbl/d, 50-80 % water",
  "PEMEX sheets show wells tested at 4-6 m3/d (25-38 bbl/d) with 50-80 % water on 2-4 mm chokes, then closed for months; TEC-7 water cut swung 1.6-99 % in 1979-80. Field averaged 3-85 bbl/d in 1980-84.",
  f"{PGP}; {T7} §8; data/processed/tecolutla_field_monthly.csv")
E("1990-02", "TEC-7", "shut_in", "TEC-7 closed for 16 years",
  "Last month Jan 1990 at ~3 bbl/d; zero rows Feb 1990 - Sep 2006.", "data/processed/tecolutla_production.csv; " + CNHF)
E("1998-10-06", "TEC-7", "pressure", "1998: TEC-7 at 250.6 kg/cm2, no depletion",
  "Static 250.63 kg/cm2 (3,565 psi) at the 2,311.5 m mid-perforation and 252.23 at 2,325 m; 24.52 MPa at 2,300 mSS after ~1.78 MMbbl (with allocations).",
  f"{T7} §7; {PCSV}")
E("1999-01", "TEC-9", "shut_in", "TEC-9 closed; field shut in 1999-2003",
  "TEC-9 'closed Jan 1999' (final PEMEX test Sep 1998); CNH shows zero production in every well Feb 1999 - May 2003.",
  f"{GAPS} G-62; {ENG} item 7")
E("2003-06", "TEC-9", "production", "TEC-9 restarts at ~100-110 bbl/d",
  "After four years shut in TEC-9 returned at 112.6 bbl/d (Jul 2003) with zero water recorded; TEC-6 restarted Aug 2003. Field averaged 161-170 bbl/d (calendar-day) in 2004-05.",
  "data/processed/tecolutla_production.csv; data/processed/tecolutla_field_monthly.csv")
E("2006-09", "TEC-2", "production", "TEC-2 back on after 1999-2006 shut-in",
  "TEC-2 resumed in Sep 2006 after zero rows from Feb 1999; TEC-7 produced Oct-Nov 2006 at 37-39 bbl/d with 29-31 % water.",
  "data/processed/tecolutla_production.csv")
E("2006-12", "TEC-7", "production", "TEC-7 and TEC-6 last production",
  "Both wells' last CNH month is Dec 2006 (TEC-7 10 bbl/d at 45 % water; TEC-6 13 bbl/d at 34 % water). TEC-7 cumulative 2,310-2,313 m: 266,988 bbl.",
  f"data/processed/tecolutla_production.csv; {V4} §2.2")
E("2007-04", "TEC-6", "abandonment", "TEC-6 abandoned: casing parted at 352 m",
  "Gas at surface and a 6 5/8 in breach at 352-1,100 m; ran on a PCP to 26 Feb 2007; abandoned Feb-Apr 2007 with plugs at 298 m, a retainer at 1,947.6 m and ~2,235-2,280 m. Cumulative ~900 kbbl (incl. ~388 kbbl allocation).",
  f"{CNHF} §6; {ENG} item 3; {GAPS} G-63", uncertain="a 13 Mar 2007 CCL shows no anomaly at 352 m; dates differ (23 Feb-3 Apr vs 5 Mar-2 Apr 2007)")
E("2010", "TEC-9", "workover", "TEC-9 shallow casing breach repaired",
  "9 5/8 in breach at ~70 m repaired in 2010; a second 6 5/8 in breach at ~530-833 m remained.", f"{CNHF} §6; {CAS}")
E("2012", "TEC-9", "stimulation", "TEC-9 solvent + acid: 10 -> 101.6 bopd",
  "At 10-11 bopd on a 3 mm choke with carbonate scale at 1,790 m, PEMEX pumped 5 m3 OSA-M solvent, 2 m3 diverter, 3 m3 15 % HCl and 17 m3 diesel; 101.6 bopd net (113 gross) at 710 psi after, then 33-46 bopd Apr-Jul 2012. H2S present.",
  f"{CNHF} §5, §7; {BRF} A5", uncertain="job month not given; CNH monthly jumps from 11.6 bbl/d (Mar 2012) to 35 bbl/d (Apr 2012)")
E("2012-07", "TEC-9", "production", "TEC-9 last production month",
  "Jul 2012: 32.6 bbl/d at 55 % water; 352,601 bbl from one interval since 1973.", "data/processed/tecolutla_production.csv")
E("2012-11", "TEC-9", "workover", "TEC-9 workover fails; well squeezed",
  "Oct-Nov 2012: a restriction was milled, damaging casing at 544-718 m; squeezed through a retainer at 2,312.36 m with plugs at 736-470 m. The 2,296-2,311 mSS top of El Abra was cemented without ever being perforated.",
  f"{REG} finding 7; {CNHF} §6; {WN} §2.4")
E("2013-01-04", "TEC-9", "abandonment", "TEC-9 plugged",
  "Plugged 4 Jan 2013. The Work Program later calls it 'closed, not properly abandoned' with a hazardous wellhead; Tonalli returned it to CNH/SENER.",
  f"{GAPS} G-62; {WN} §2.4", uncertain="'temporarily abandoned' vs 'plugged' in different files")
E("2014-01-01", "FIELD", "regulatory", "PEMEX: 1.9 MMbbl produced, field at ~9 bbl/d",
  "PEMEX field summary: cumulative 1.9 MMbbl oil and 1.7 Bcf gas at 1 Jan 2014; ~9 bbl/d in 2014; booked OOIP 7.8 MMbbl; one producer.",
  f"{GGN} §1; {WN} §1")
E("2014-12", "TEC-2", "production", "TEC-2 last CNH-sourced month: 9 bbl/d",
  "Dec 2014: 9 bbl/d oil at 91 % water. The CNH record ends here; 13 later rows (2015-Jan 2016) are hand-entered.",
  f"data/processed/tecolutla_production.csv; {CNHF} §1; {GAPS} G-33")
E("2015-01-01", "FIELD", "regulatory", "CNH books 1P 0.0 / 2P 0.0 / 3P 0.1 MMbbl",
  "CNH table at 1 Jan 2015: original oil 7.8 MMbbl, cumulative 1.9 MMbbl, reserves 1P 0.0, 2P 0.0, 3P 0.1 MMbbl.", f"{ENG} item 1")
E("2015-09-21", "BLOCK", "corporate", "Tonalli Energia incorporated",
  "Founded by Grupo IDESA and Petro Frontera (IFR), 50 % each.", f"{REG} finding 11")
E("2015-12", "FIELD", "shut_in", "PEMEX reports: 'no production, field closed'",
  "PEMEX's December 2015 measurement report states the field is closed.", f"{CNHF} §1")
E("2016-01-15", "TEC-2", "production", "TEC-2 last PEMEX production line",
  "2017 integrity cedula: last production 15 Jan 2016, 19 m3/d liquid at 80 % water (~24 bbl/d oil, ~96 bbl/d water).",
  f"{GOV}", uncertain="CNH record ends Dec 2014; PEMEX said the field was closed in Dec 2015; 2015-16 rows hand-entered")
E("2016-08-25", "BLOCK", "regulatory", "Licence contract CNH-R01-L03-A24/2016",
  "Ronda 1 (third tender) licence to Tonalli: 25-year term to 25 Aug 2041 plus two conditional 5-year extensions; guarantee USD 1,764,100; minimum work 4,600 units; change of control needs CNH consent; 7.16 km2 contract area.",
  f"{REG} finding 1, 3; {CNHF} finding 10", uncertain="block deck timeline puts the licence at 2016-03 (unsourced); GLJ20 says 'awarded 2018'")
E("2016-11-23", "BLOCK", "corporate", "Acta Hora Cero: PEMEX hands field to Tonalli",
  "Acta Protocolo Hora Cero signed by PEP-APPRA and Tonalli on 23 Nov 2016; all wells shut in or abandoned.", f"{GOV}")
E("2017-03-15", "FIELD", "regulatory", "Integrity cedulas: TEC-2 and TEC-7 closed, sealed",
  "Both wells registered as closed and hermetic with heads partly dismantled; accepted without integrity studies because they form part of the plan.",
  f"{GOV}")
E("2017-05-19", "BLOCK", "regulatory", "Plan de Evaluacion filed with CNH",
  "Programme: TEC-2 major workover (USD 676,372), new TEC-10 directional well with core, 3D reprocessing; plan total ~USD 10.2-10.5 MM over 12 months.",
  f"{REG}; {GGN} §10.4")
E("2018-01-11", "BLOCK", "regulatory", "Plan amended: committed workover moved to TEC-7",
  "The Jan 2018 revision moved the USD 676,372 major workover from TEC-2 to TEC-7 (test intervals 2,310-2,313 and 2,313-2,318 m).",
  f"{REG} finding 2", uncertain="CNH approval of the amendment is not in the files (G-66)")
E("2018-03-27", "TEC-2", "pressure", "TEC-2 after 2 years shut-in: 24.16 MPa",
  "Static gradient to 2,250 mKB (gauge stopped above the perforations): 240.56 kg/cm2 (23.59 MPa) at gauge; 24.16 MPa (3,504 psia) at 2,300 mSS on a water-gradient extrapolation.",
  f"{P05} §2; {PCSV}")
E("2018-04-11", "TEC-10", "drilling", "TEC-10DES spudded from the TEC-6 pad",
  "Tonalli's first well: J-shape directional from a new pad beside TEC-6, rig DTM-638, AFE USD 2.92 MM; conductor 11 Apr (masterlog spud 16 Apr).",
  f"{WN} §2.4", uncertain="spud 11 Apr (QMAX) vs 16 Apr 2018 (masterlog)")
E("2018-04-28", "TEC-10", "drilling", "TEC-10 cores El Abra at 2,352 m",
  "Core 1, 2,352-2,353 mMD (~2,317 mSS), 1.30 m recovered: recrystallised miliolid grainstone, plug porosity 2.3-7.6 %, permeability 0.04-1.16 mD.",
  f"{GAPS} G-47 (update); {DRN}")
E("2018-05-01", "TEC-10", "drilling", "TEC-10 at TD 2,490 mMD; full log suite",
  "TD 2,490 mMD (2,453.5 mTVD, -2,447.4 mSS), ~19 deg; open-hole suite incl. CMI image 2 May; 4 1/2 in liner 2,133-2,489 m cemented 4 May. El Abra top -2,309.7 mSS; the 2,294-2,311 mSS 'window' above it is Tantoyuca marl on XRD.",
  f"{WN} §2.4; {SURV}; {GEO} §1")
E("2018-05-10", "TEC-2", "workover", "TEC-2 cleaned out; tests 50 bbl/d at 90 % water",
  "Workover found paraffin in the tubing; test and build-up 8-30 May 2018 ended at 50 bbl/d oil and 453 bbl/d water (16.8 MPa BHFP). Shut in afterwards for lack of water disposal.",
  f"{BRF} A5; {P05} §5; {WN} §3.3")
E("2018-05-30", "TEC-2", "pressure", "TEC-2 build-up p* 24,190 kPa",
  "IHS interpretation: 24,190 kPa (pi 3,508 psia) at 2,309 mKB = 24.14 MPa at 2,300 mSS; k 50 mD, skin +196, constant-pressure (aquifer) boundary at 700 m.",
  f"{P05} §2, §5")
E("2018-06-30", "TEC-10", "test", "TEC-10 deep zones A and B: no oil",
  "Zone A (2,433-2,442 mMD) took fluid only at 3,000-3,500 psi and gave no inflow after acid; zone B (2,394.5-2,413.5 mMD) gave weak water inflow (16.9 m3 recovered vs 19.6 m3 injected).",
  f"{ENG} item 9; {DRN}")
E("2018-07-23", "TEC-10", "test", "TEC-10 zone C flowback: up to 194 bbl/d",
  "Perforations 2,349.5-2,353 mMD (2,314.3-2,317.6 mSS) after stimulation; 23 Jul-6 Aug on 12/64 in: oil 41 -> 194 bbl/d, water cut 89 -> 39 %, GOR ~743 scf/bbl, WHP 328 -> 863 psig; 1,475 bbl.",
  "data/processed/welltest/tec10_welltest_2018_daily.csv; " + f"{WN} §2.4")
E("2018-08-31", "TEC-10", "pressure", "TEC-10 build-up: 24.14 MPa at datum",
  "IHS: 24,304 kPa (pi 3,525 psia) at 2,322.1 mTVD KB = 24.14 MPa at 2,300 mSS; k 18 mD, skin +4.9; aquifer boundary at 195 m and a no-flow boundary at 125 m.",
  f"{P05} §2, §5")
E("2018-09-20", "TEC-10", "production", "TEC-10 on production; first sales to PEMEX",
  "Daily production record starts 20 Sep 2018; first truck sales Sep 2018. Oct 2018 averaged 181 bbl/d oil.",
  f"{P04} §4; {WN} §3.3")
E("2018-10-20", "TEC-10", "production", "TEC-10 peak day: 232 bbl/d",
  "231.6 bbl/d oil, 78 bbl/d water, 762 scf/bbl at 772 psi tubing pressure.", f"{PRES} finding 5; {WN} §2.2")
E("2018-11-11", "TEC-11", "drilling", "TEC-11DES horizontal spudded from TEC-2 pad",
  "Drilling AFE USD 2.25 MM; planned azimuth ~320 deg to cut natural fractures predicted from TEC-10.",
  f"{WN} §2.4; {PRES} finding 4", uncertain="accounting notes give spud 9 Nov 2018")
E("2018-11-25", "TEC-11", "drilling", "TEC-11 7 in casing set at 2,354 m (61 deg)",
  "Slow build (auto-driller failure; last 24 h only 25 m); 7 in shoe 2,354.44 mMD (~2,243 mSS) cemented with returns; a hydraulic-arm failure while running casing (51.5 h from casing point to cemented).",
  f"{WN} §2.4; {P03}")
E("2018-12-18", "TEC-11", "drilling", "TEC-11 reaches TD 3,283 mMD",
  "80 deg at 2,563 mMD (2,305 mSS), 90 deg at 2,727 mMD (2,323 mSS); TD 3,283 mMD at 2,331 mSS, 1,190 m from surface. 720 m lateral, mostly mudstone-wackestone; liner hanger damaged, tie-back faulty, two cement jobs. Rig released 26 Dec; drilling USD 3.11 MM vs 2.25 MM AFE.",
  f"{P03} §2-3; {WN} §2.4; {ACCN} §2")
E("2019-01", "BLOCK", "corporate", "Plan: TEC-11/12/13 horizontals at 694 bbl/d",
  "Jan 2019 forecast carried TEC-11, TEC-12 and TEC-13 as horizontals at 694 bbl/d each (~0.69 MMbbl per well).", f"{ENG} item 6")
E("2019-02", "TEC-2", "workover", "TEC-2 add-perf at 2,319-2,320 m",
  "Operations log: correlation log 2,325-2,120 m and a 1 11/16 in RTG gun, 3 spm, at 2,319-2,320 mKB (2,315-2,316 mSS).",
  f"{GAPS} G-59", uncertain="the May 2019 Tonalli schematic does not show this interval; estado mecanico text reads 2,019-2,020 (typo)")
E("2019-05", "TEC-11", "completion", "TEC-11 completion: fish left at 2,866 m",
  "A bit and watermelon mill (5.9 m) were lost at 2,866-2,872 mMD; the 4 1/2 in liner ends at 2,863 m and the 411 m of open hole beyond (2,872-3,283 mMD) could not be re-entered.",
  f"{CAS}; {ENG} item 2")
E("2019-05", "TEC-2", "workover", "TEC-2 plug shuts off wet deep perforations",
  "Permanent plug at 2,322.5 m with packer at 2,292.65 m (schematic 16 May 2019).", f"{GAPS} G-59; {ENG} item 4")
E("2019-06", "TEC-11", "completion", "TEC-11 perforated and acidised unisolated",
  "Five 3 m perforations 2,643.5-2,745.5 mMD (2,316-2,323 mSS). The selective acid tool could not pass the damaged liner hanger, so acid was bullheaded; pressure broke down quickly; some oil, then 100 % water.",
  f"{ENG} item 2; docs/12_drive_large_files.md §1; {WN} §2.4")
E("2019-06", "TEC-2", "production", "TEC-2 69-day test: 47 bbl/d at 75 % water",
  "Test on 2,307-2,311 (+2,319-2,320) m at ~250 psi; 2,045 bbl sold in Jun 2019.", f"{BRF} A5; data/processed/tecolutla_production.csv")
E("2019-06-21", "TEC-10", "stimulation", "TEC-10 APSOL-AP solvent job (1 of 4)",
  "2-3 m3 of APSOL-AP 'organic system' (Quimica Apollo or TPM) against wax; further TEC-10 jobs 13 Aug, 1 Nov and 23 Dec 2019. Product composition unconfirmed (not necessarily xylene).",
  f"{BRF} A6")
E("2019-06-23", "TEC-7", "workover", "TEC-7 reopened: 182 bbl/d of pure water",
  "Repair from 16 Jun; 23 Jun stimulation (3.15 bbl solvent, 12.6 bbl acid, 36 bbl brine at 0.5-1 bpm, 250-440 psi). 2,310-2,313 m made 182 bbl/d water, 100 % water cut; bad cement or a leaking plug suspected.",
  f"{BRF} A5; {GAPS} G-57")
E("2019-07-11", "TEC-11", "test", "TEC-11 tests 260 bbl/d water, trace oil",
  "On 12/64 in at 195 psi WHP; ~935 bbl of water by 12 Jul at 78,000 ppm Cl (still spent acid). Final schematic: 286 bbl/d water, 100 % water cut.",
  f"{DRN}; {PRES} finding 4")
E("2019-08-07", "TEC-7", "injection", "TEC-7 converted to produced-water injector",
  "Triplex-pump injection from 7 Aug 2019; 2 3/8 in string with packer at ~2,300 m (schematic 26 Aug 2019). Short-test injectivity ~700-1,400 bbl/d at <450 psi. Ended water trucking.",
  f"{BRF} A5; {GAPS} G-57; {WN} §2.1")
E("2019-08-11", "TEC-11", "abandonment", "TEC-11 composite plug set at 2,400 m",
  "Boss composite blind plug (10,000 psi) set in the 4 1/2 in liner at ~2,400 mMD (~2,263 mSS) on 11-12 Aug 2019; killed with 1.06 g/cc brine; no cement.",
  f"{DRN}")
E("2019-08-13", "FIELD", "stimulation", "APSOL-AP solvent jobs on TEC-10 and TEC-2",
  "Second TEC-10 job and first TEC-2 job of the 2019 programme (2-3 m3 each).", f"{BRF} A6")
E("2019-08-22", "TEC-11", "test", "TEC-11 Tantoyuca test: 17 API oil, water",
  "Uphole test above the plug; oil sample from 2,361-2,364 m (~2,246 mSS) was 17.0 API with 31.8 % water; trace oil and 96 bbl/d water. Cost USD 206,225.",
  f"data/processed/deck_notes/fluids_rock_core_notes.md; {BRF} A5; {ACCN} §2")
E("2019-09-06", "TEC-11", "completion", "TEC-11 work ends; USD 4.40 MM all-in",
  "Completion finished 6 Sep 2019. All-in USD 4,403,743 vs 3,934,870 budget; the tax pool carries only 3.51 MM, the ~0.96 MM gap matching 'Workstrings invoices' of unknown status.",
  f"{DRN}; {ACCN} §2; {GAPS} G-64")
E("2019-09-06", "TEC-2", "shut_in", "TEC-2 shut in as uneconomic",
  "Directors' memo (6 Sep 2019): TEC-2 uneconomic, shut in Sep 2019 (USD 8 k demobilisation); break-even 60 bbl/d at USD 54/bbl.",
  f"{DRN}")
E("2019-10-18", "TEC-11", "regulatory", "TEC-11 reclassified producer -> injector",
  "Filed with CNH; well closed pending possible water injection.", f"{DRN}")
E("2019-11-15", "TEC-7", "regulatory", "ASEA authorises TEC-7 water injection",
  "Authorisation ASEA/UGI/DGGEERC/1712/2019 under MIA 1077/2017 (extended to 26 Oct 2023).", f"{GAPS} G-57; {DRN}")
E("2019-12-17", "FIELD", "production", "TEC-10 to TEC-2 flowline installed",
  "514 m of 2 in sour-service line consolidated tankage and testing at one battery.", f"{WN} §3.1.3; {BRF} A9")
E("2019-12-23", "FIELD", "stimulation", "Last documented APSOL jobs (TEC-10, TEC-2)",
  "Fourth TEC-10 and second TEC-2 solvent job of 2019; six jobs in all. Jobs after 2019 are not itemised in the files.", f"{BRF} A6")
E("2020-01-31", "TEC-2", "production", "TEC-2 commingled for testing with TEC-10",
  "GLJ note; the 2020 CNH filing names both wells as origin. Per-well volumes after Nov 2019 are not separable.",
  f"{WN} §2.4; {GAPS} G-32", uncertain="no per-well data (G-32)")
E("2020-04", "FIELD", "shut_in", "Field shut in Apr-Jun 2020 (price collapse)",
  "CNH 2020 filing reports zero production for three months; no sales tickets.", f"{P13} §2")
E("2020-07-02", "BLOCK", "regulatory", "Evaluation report and transition plan filed",
  "Tonalli files the Informe de Evaluacion and Programa de Transicion request; CNH dismisses both on 7 Aug 2020.", f"{DRN}")
E("2020-07-21", "BLOCK", "corporate", "PEMEX early-production sales contract",
  "Contrato de Compraventa de Petroleo de Produccion Temprana PEP-Tonalli; realised price averaged 0.81 x WTI in 2020-22.",
  f"{DRN}; {BRF} A8")
E("2020-09", "TEC-2", "production", "TEC-2 last reported rate: 18 bbl/d",
  "18 bbl/d oil at 72 % water cut (Sep 2020); GLJ lists Sep 2020 as last production; ~10.0 kbbl since 2018.",
  f"{BRF} A5; {WN} §2.4")
E("2020-12", "FIELD", "stimulation", "Stimulation booked Dec 2020 (USD 4,225)",
  "2020 lease operating statement carries a USD 4,225 stimulation in December; well not named.", f"{ACCR} (2020 LOS)", uncertain="well and fluid not recorded")
E("2021-02-25", "TEC-10", "production", "TEC-10 choke opened",
  "GLJ note: choke increased 25 Feb 2021. TEC-10 was the only producer in 2021: 17,402 bbl net, 81 % water, GOR 859 scf/bbl; 2021 average 47.9 bbl/d (GLJ).",
  f"{WN} §2.4; {P13} §2")
E("2021-12", "TEC-10", "production", "TEC-10 down to 34 bbl/d at 86 % water",
  "Dec 2021: 1,062 bbl oil and 6,453 bbl water; 75.8 kbbl cumulative. GLJ Q4-2021: 35 bbl/d, 210 bbl/d water, GOR 1,127.",
  f"data/processed/cnh/cnh_production_filings_2020_2022.csv; {BRF} A5; {WN} §2.3")
E("2022-02-04", "FIELD", "shut_in", "CNH rejects evaluation; field shut in",
  "CNH resolved the Informe de Evaluacion unfavourably on 3 Feb 2022; on 4 Feb Tonalli withdrew its transition request and stopped production. Jaguar deck: TEC-10 'stim required during restart'.",
  f"{DRN}; {BRF} A5", uncertain="other sources date the shut-in to Jul 2022 (CNH filings) or early 2023 (GLJ, environmental permit), G-65")
E("2022-04", "TEC-11", "regulatory", "TEC-11 temporary-abandonment notice",
  "Aviso de abandono temporal (art. 54) filed; 100 % water, composite plug at ~2,400 m.", f"{DRN}")
E("2022-07-18", "BLOCK", "regulatory", "CNH approves the Programa de Transicion",
  "Resolution CNH.E.56.001/2022; approved programme was 1,400 bbl/month; TEC-12 in the plan.", f"{DRN}; {P13} §2")
E("2022-08", "FIELD", "production", "238 bbl produced to tank, Aug-Sep 2022",
  "CNH monthly reports: 189 bbl (Aug) and 49 bbl (Sep) net oil, no sales; these became the 238 bbl opening inventory of Nov 2022.",
  f"{P13} §2; {WN} §3.6", uncertain="well not named")
E("2022-08-25", "BLOCK", "corporate", "IDESA exits; Jaguar buys 50 % of Tonalli",
  "Petro Frontera bought IDESA's 50 % for MXN 100 and sold 50 % to Jaguar for USD 850,000; Jaguar to become operator.", f"{DRN}")
E("2022-11-24", "TEC-10", "stimulation", "TEC-10 stimulated and restarted",
  "Nov 2022 stimulation (USD 20,003); 15 producing days: 2,260 bbl gross, 678 bbl net, 1,582 bbl water (70 %), 0.9 MMcf flared, 30.9 API; 916 bbl delivered 24-30 Nov.",
  f"{ACCR} (2022 LOS); {P13} §2")
E("2022-12", "TEC-2", "workover", "TEC-2 worked over; restarts at 23 bopd",
  "GLJ YE2022: workover Dec 2022, restarted at 23 bopd but uneconomic; 31 days on in 2022 at 22.8 bbl/d, 80.4 % water.",
  f"{RES} finding 3; {RESR} row 8")
E("2023-01", "FIELD", "shut_in", "Last production: TEC-2 16, TEC-10 2 bbl/d",
  "GLJ Table 1: last production month Jan 2023 for both wells; 530 bbl sold in 2023. GLJ cites an environmental permit; IFR representation letters say all permits are in place.",
  f"{RES} finding 4; {GAPS} G-65; {BRF} A9", uncertain="shut-in cause unresolved (G-65)")
E("2023-10-01", "BLOCK", "corporate", "Petro Frontera diluted to 42.63 %",
  "Default notice 1 Oct 2023: IFR diluted to 44.19 %, then 42.63 % at 31 Dec 2023; Jaguar 57.37 %.", f"{ACCN} §7-8")
E("2023-10-26", "TEC-7", "regulatory", "TEC-7 injection MIA extension ends",
  "The MIA 1077/2017 extension under which TEC-7 injected ran 26 Oct 2020 - 26 Oct 2023.", f"{DRN}",
  uncertain="no document links this to the shut-in; whether it was renewed is not in the files")
E("2024", "FIELD", "shut_in", "2024: no production; holding cost USD 289 k",
  "GLJ YE2024 shows zero production; Tonalli P&L opex USD 289 k (one USD 7,003 revenue line in Jul 2024). Abandonment reserve USD 411 k for four wells and facilities.",
  f"{RESR} rows 14, 21; {DRN}", uncertain="source of the Jul-2024 revenue not stated")
E("2025-02", "BLOCK", "regulatory", "CNH suspends evaluation and transition clocks",
  "Acuerdo CNH.E.08.01.25 suspended exploration/evaluation periods and transition programmes.", f"{GAPS} G-49")
E("2025-03-18", "BLOCK", "regulatory", "New hydrocarbons law; CNH replaced by CNE",
  "Ley del Sector Hidrocarburos: existing contracts keep their terms; CNH functions pass to the Comision Nacional de Energia; Reglamento 3 Oct 2025.", f"{GAPS} G-49")
E("2026-04-28", "BLOCK", "regulatory", "GLJ YE2025 for Kinjal: 348/903/1,383 kbbl",
  "No producing reserves; TEC-10 and TEC-2 PDNP with 15 k$ workovers in Aug 2026; TEC-12 drilled Jul 2028 (text says 2027) at USD 1.9 MM.",
  f"{RES} YE2024-25 section")
E("2026-05-25", "BLOCK", "corporate", "Kinjal: Tonalli debt to go at closing",
  "Release: all Tonalli indebtedness eliminated at closing; field-wide reserve report planned after closing.", f"{BRF} header")
E("2026-09-03", "BLOCK", "corporate", "IFR agrees to buy Jaguar's 57.37 %",
  "Definitive agreement gives the resulting issuer (Kinjal reverse takeover) 100 % of Tonalli and the block, subject to TSXV, shareholder and Mexican (SENER) approvals.", f"{BRF} header")
E("2026-10", "FIELD", "shut_in", "Today: every well shut in or abandoned",
  "TEC-10, TEC-2 shut in since Jan 2023; TEC-7 shut-in injector; TEC-11 temporarily abandoned; TEC-3, 5, 6, 9, 101 plugged; TEC-12 undrilled. No record that the planned Aug 2026 workovers took place.",
  f"{RES}; {BRF} B3", uncertain="status as of the files read; no 2026 operations record in the repository")
# TEC-12 planning milestones
E("2020-09", "TEC-12", "regulatory", "TEC-12 drilling programme issued",
  "Programa de perforacion: directional from the TEC-10 pad, target El Abra -2,296 mSS at 2,323.2 mMD, TD 2,360 mMD; 7 in to TD; open-hole density, neutron, induction, GR.",
  f"{WN} §2.4")
E("2020-11", "TEC-12", "corporate", "TEC-12 AFE: USD 1,572,724 (S-shape)",
  "AFE priced on Nov 2020 (2018 contract) rates; PPI-indexed to Sep 2026 it is USD 2.04 MM.", f"{V4} §6.3; docs/08_afe.md")

events.sort(key=lambda e: (e["date"] + "-00-00")[:10])

# ================================================================= PRESSURE
pc = pd.read_csv(REPO / PCSV)
ocr = pd.read_csv(REPO / OCRC)
kg_lookup = {(r.date, r.well): r.transcription_kgcm2 for r in ocr.itertuples()}
kg_lookup[("1971-08-09", "TEC-6")] = 244.6   # corrected from scan (G-51)
press = []
for r in pc.itertuples():
    kg = kg_lookup.get((r.date, r.well))
    if r.date == "1998-10-06": kg = 252.232
    typ = {"static gradient": "static", "flowing survey": "flowing", "build-up, extrapolated p*": "build-up p*"}[r.kind]
    rec = {"date": r.date, "well": r.well, "type": typ,
           "shut_in_days": None if (isinstance(r.shut_in_days, float) and math.isnan(r.shut_in_days)) else round(r.shut_in_days, 2),
           "gauge_depth_mkb": r.gauge_depth_mkb, "depth_mss": round(r.gauge_depth_mss, 1),
           "pressure_kgcm2": round(kg, 2) if kg else round(r.p_gauge_kpa / 1000 / KGCM2_MPA, 2),
           "pressure_kgcm2_basis": "as read on the PEMEX form" if kg else "converted from kPa",
           "pressure_mpa": round(r.p_gauge_kpa / 1000, 3), "pressure_psi": round(r.p_gauge_kpa / 1000 * MPA_PSI, 1),
           "datum_2300mss_mpa": round(r.p_2300mss_mpa, 2), "datum_2300mss_psia": round(r.p_2300mss_psia, 0),
           "datum_basis": "corrected to 2,300 mSS at 10.5 kPa/m (docs/05_pressure.md §1)",
           "usable_as_static": bool(r.usable_static), "comment": r.comment if isinstance(r.comment, str) else "",
           "source": f"{PCSV} (from {r.source}); {P05}"}
    if r.quality_flag and isinstance(r.quality_flag, str): rec["flag"] = r.quality_flag
    press.append(rec)

def addp(**k): press.append(k)
for p in press:
    if p["date"] == "1956-05-24": p["note"] = "2 h 45 min shut-in (build-up 243.2 -> 252.0 kg/cm2); PEMEX 'initial'; Forma 19 prints depth '2010 m.bnm', probably OCR for 2,310 (docs/17)"; p["usable_as_static"] = True; p["usable_note"] = "reference initial, not stabilised"
    if p["date"] == "1964-12-08" and p["well"] == "TEC-7":
        p["uncertain"] = True; p["uncertain_why"] = "TEC-7 expediente gives 251.90 kg/cm2 (3,583 psi) at 2,310 m on 12 Dec 1964 with water level 2,045 m (tec7_expediente_findings §7); 95-day shut-in inconsistent with closure since 1957"
    if p["well"] == "TEC-6" and p["date"].startswith("1971") and p["shut_in_days"] and p["shut_in_days"] < 7:
        p["note"] = "shut-in under 7 days: build-up incomplete; excluded from the static range in docs/05_pressure.md §4"
    if p["date"] == "1971-08-09": p["flag"] = "transcription 248.0 corrected to 244.6 from the scan (G-51)"
    if p["date"] == "1971-08-12": p["uncertain"] = True; p["uncertain_why"] = "CNH survey table gives 246.7 kg/cm2 at 2,337 m vs 248.0 here (0.13 MPa, G-73)"
    if p["date"] == "1973-06-04": p["uncertain"] = True; p["uncertain_why"] = "Work Program table lists this as a 22.8 MPa static; IFR summary and scan say flowing before shut-in (flowing BHP 16.6 MPa)"
    if p["date"] == "1998-10-06": p["note"] = "also 250.634 kg/cm2 at the 2,311.5 m mid-perforation (3,565 psi, expediente p112); wellbore full of brine, no packer"
    if p["date"] == "2018-03-27": p["note"] = "gauge stopped at 2,250 mKB above the perforations; extrapolated 54 m at a water gradient by IFR; ~2 years shut-in (field shut since Jan 2016)"
    if p["date"] == "2018-05-30": p["note"] = "IHS p* (pi 3,508 psia); last measured 24,187 kPa after 311 h; Weatherford build-up end 3,441 psi at the 2,263 m gauge reproduces it within 0.01 MPa (v4 §2.4)"
    if p["date"] == "2018-08-31": p["note"] = "IHS p* (pi 3,525 psia) at 2,322.1 mTVD KB; last measured 24,283 kPa after 598 h; IHS used KB 7.1 (2,315 mSS)"

addp(date="1956", well="TEC-3", type="DST", shut_in_days=round(10/1440, 4), gauge_depth_mkb="2376.8-2380.8 (test interval)", depth_mss="~2370-2375",
     pressure_kgcm2=230.0, pressure_kgcm2_basis="as reported", pressure_mpa=round(230*KGCM2_MPA, 3), pressure_psi=round(230*KGCM2_MPA*MPA_PSI, 1),
     datum_2300mss_mpa=None, datum_basis="no datum correction in any source; 10-minute shut-in, not stabilised", usable_as_static=False,
     comment="flowing 20/50 kg/cm2; 980 m oil + 80 m salt water recovered; eng_findings gives 'final shut-in 23 MPa'",
     source=f"{CNHF} §4; {ENG} item 10")
addp(date="1956-05-24", well="TEC-2", type="flowing", shut_in_days=None, gauge_depth_mkb=2310, depth_mss="~2306",
     pressure_kgcm2=234.2, pressure_kgcm2_basis="as reported (Forma 19)", pressure_mpa=round(234.2*KGCM2_MPA, 3), pressure_psi=round(234.2*KGCM2_MPA*MPA_PSI, 1),
     datum_2300mss_mpa=None, datum_basis="not corrected in source", usable_as_static=False,
     comment="flowing BHP during the open-hole gas-cap test (2,307.4-2,321.7 m), 6 mm choke", source=GOV)
addp(date="2017", well="FIELD", type="static (unreferenced)", shut_in_days=None, gauge_depth_mkb=None, depth_mss=None,
     pressure_kgcm2=None, pressure_mpa="25.1-25.4", pressure_psi=None, datum_2300mss_mpa=None, datum_basis="no datum given",
     usable_as_static=False, comment="2017 summary 'Psr' quoted without datum; working value, do not quote",
     source=f"{ENG} (contradictions section); {GAPS} G-35", uncertain=True, uncertain_why="no datum, well or date of measurement")
addp(date="2018-05", well="TEC-2", type="flowing", shut_in_days=None, gauge_depth_mkb=2309, depth_mss=2305.2,
     pressure_kgcm2=round(16.8/KGCM2_MPA, 1), pressure_kgcm2_basis="converted", pressure_mpa=16.8, pressure_psi=2436,
     datum_2300mss_mpa=None, datum_basis="flowing", usable_as_static=False,
     comment="final flow before the build-up: 50 bbl/d oil, 453 bbl/d water; Pwf 2,436 psia, WHP 515 psia", source=f"{P05} §5; {WN} §2.4")
addp(date="2018-08-06", well="TEC-10", type="static (IPR input) and flowing", shut_in_days=None, gauge_depth_mkb=None, depth_mss=None,
     pressure_kgcm2=None, pressure_mpa=round(3510/MPA_PSI, 2), pressure_psi=3510, datum_2300mss_mpa=None, datum_basis="depth not stated",
     usable_as_static=False, comment="Quick IPR: Ps 3,510 psi, Pwf 3,118 psi, PI 0.78 bbl/d/psi; last flow before build-up 196 bbl/d oil, 114 bbl/d water at 21.3 MPa BHFP",
     source=f"{WN} §2.4 (20180726 Tec-10 Quick IPR2.xlsx); {P05} §5")

press.sort(key=lambda p: (str(p["date"]) + "-00-00")[:10])
pressure_out = {
    "summary": {
        "datum": "2,300 m subsea; gauge-to-datum at 10.5 kPa/m (IHS reservoir gradient); KBs TEC-2 3.8, TEC-6 6.0, TEC-7 4.8, TEC-10 6.13 m",
        "initial": "24 May 1956 TEC-2: 252.0 kg/cm2 at 2,310 mKB after 2 h 45 min = 24.65 MPa (3,575 psia) at datum",
        "latest": "2018: three wells 24.14-24.16 MPa (3,500-3,505 psia) at datum (TEC-2 static gradient 27 Mar; TEC-2 p* 30 May; TEC-10 p* 31 Aug)",
        "change": "-0.51 MPa (-74 psi, ~2 %) over 62 years and ~1.9-2.1 MMbbl of oil; expansion alone would supply ~11 kbbl, so >99 % of voidage replaced by water influx (docs/05_pressure.md §3)",
        "stabilised_static_range": "24.14-24.66 MPa for every survey with >= 1 week shut-in, 1964-2018",
        "exceptions": [
            "1971 TEC-6 build-up: 23.24 MPa after 4 days rising to 24.35 MPa after 74 days - short shut-ins understate by up to ~1 MPa (the review's 23.2 MPa low end is this 4-day point)",
            "Flowing surveys: TEC-6 1964 (18.66 MPa datum) and 1973 (22.68 MPa, mislabelled static in the Work Program); TEC-2 1956 flowing 234.2 kg/cm2; 2018 BHFP TEC-2 16.8, TEC-10 21.3 MPa",
            "TEC-3 1956 DST 230 kg/cm2 after 10 min at ~2,372 mSS: not stabilised, no datum value",
            "TEC-7 Dec 1964: date (8 vs 12 Dec) and value (252.0 vs 251.90 kg/cm2) differ between the IFR summary and the expediente",
            "TEC-6 12 Aug 1971: 248.0 (IFR) vs 246.7 kg/cm2 (CNH table), G-73; 9 Aug 1971 corrected 248.0 -> 244.6 from the scan (G-51)",
            "2017 'Psr 25.1-25.4 MPa' has no datum and should not be plotted",
            "No pressure measurement exists after Aug 2018; the field has been shut in since Jan 2023 (a long-shut-in static on TEC-10 is the recommended next measurement)"],
        "conversion": "1 kg/cm2 = 0.0980665 MPa; 1 MPa = 145.0377 psi",
    },
    "measurements": press,
}

# ================================================================= WRITE
wells_out = {"_readme": {
  "coordinates": "UTM zone 14N, WGS84, metres. Do not mix with PEMEX/CNH NAD27 layers (~27 m E, 200 m S offset, G-74).",
  "depths": "mMD below KB; mSS = metres below sea level, positive down unless shown negative (tops are given negative, as in the sources).",
  "status_timeline": "Segments are in chronological order. Where two segments share a boundary month (source dates are month-only), apply them in list order: the later segment wins. CNH-derived runs fold zero-production gaps shorter than 3 months into the producing run and say so in the note.",
  "units": "oil m3/d x 6.2898 = bbl/d; GOR m3/m3 x 5.6146 = scf/bbl; original units kept alongside",
  "built_by": "scratchpad/build_compile.py from files in /home/user/git_practice (read-only)"},
  "wells": wells}
for name, obj in [("wells.json", wells_out), ("events.json", events), ("pressure.json", pressure_out)]:
    (OUT / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str))
print(len(wells), "wells;", len(events), "events;", len(press), "pressure rows")
for w in wells: print(w["well"], len(w["status_timeline"]), "timeline segments")
