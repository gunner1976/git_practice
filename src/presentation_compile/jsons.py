"""opex_breakdown.json, drilling_costs.json, technical_tables.json. Values transcribed from the repo files cited beside them."""
import json, pandas as pd
REPO = "/home/user/git_practice/"
OUT = "data/processed/presentation/"
FX21 = 21.0  # stated in the source sheet itself (Tonalli Op Cost 290920.xlsx, "FX 21")

# ---------------------------------------------------------------- opex_breakdown.json
sep20 = [("Crew / field supervision (SIIC 'José')", 280000, "MXN"), ("Vacuum truck (Kefren/TDH)", 108000, "MXN"), ("Diesel", 60000, "MXN"),
         ("Consumables", 40000, "MXN"), ("Frac tank rental (Oro Negro)", 32000, "MXN"), ("Water analysis (Mensuranda)", 21000, "MXN"),
         ("Crude analysis (Intertek)", 1468, "USD"), ("Demulsifier (Apollo)", 925, "USD")]
sep_items = []
for lab, v, cur in sep20:
    sep_items.append(dict(category=lab, amount=v, currency=cur, usd_per_month=round(v / FX21, 0) if cur == "MXN" else v,
                          usd_basis="MXN / 21 (the rate stated in the source sheet)" if cur == "MXN" else "as stated (USD)"))
los21 = pd.read_csv(OUT + "opex_annual_lines.csv"); l21 = los21[los21.year == 2021]
ob = dict(
    title="Tecolutla field opex at its leanest, and the economic-model cost assumptions",
    currency_rule="Amounts in the source currency; USD only where the source gives USD or states the FX rate.",
    leanest_sustained_producing_level=dict(
        statement="Lowest sustained producing-field opex: USD 24.3-25.4 k/month in Jul-Nov 2020; USD 29.1 k/month average through 2021 (349,282 / 12). Field opex only: excludes G&A, regulatory and area charges.",
        jul_nov_2020_range_usd_per_month=[24300, 25400], avg_2021_usd_per_month=29107,
        sources=["data/processed/database_review/acc_findings.md s.1 finding 2 (Jul-Nov 2020 24.3-25.4 k/month; 2021 averaged 29.1 k/month)",
                 "data/processed/database_review/acc_review.csv row 1l_gSKHt (final 2021 LOS opex 349,282)"]),
    sep_2020_cost_sheet=dict(
        description="Monthly operating payments, Tonalli Op Cost 290920.xlsx (Sep 2020), the only line-item monthly cost structure at the lean level",
        total_usd_per_month=28155, fx_mxn_per_usd_stated_in_source=21, items=sep_items,
        not_included="separator rental MXN 216,000/month ended Mar-2020 (invoices Sep-2019 to Mar-2020)",
        sources=["data/processed/deck_notes/drive_reads_notes.md line 19 (Drive 1K3fXnOeKw8A7fzFnb3onriNZPKfBe2P1)",
                 "data/processed/deck_notes/accounting_notes.md s.4 'Sept-2020 run-rate'", "src/overview_figures.py figure 23 (28.155 k bar)"]),
    lean_full_year_2021_by_category=dict(
        description="2021 lease operating statement by category; usd_per_month = annual / 12 (a period average computed here, not monthly actuals)",
        items=[dict(category=r.line_item_as_in_source, usd_year=int(r.usd), usd_per_month=round(r.usd / 12, 0)) for r in l21.itertuples()],
        total_usd_year=349282, total_usd_per_month=29107,
        source="data/processed/database_review/acc_review.csv row 1l_gSKHt (final 2021 sheet of the Dec-2022 LOS workbook)"),
    shut_in_standby_2022=dict(statement="While shut in (Mar-Oct 2022) standby cost about USD 5-8 k/month: supervision 3.3 k, tanks 2 k, fees 1.3 k; field supervision MXN 68,000/month",
                              source="data/processed/database_review/acc_review.csv row 1l_gSKHt interpretation"),
    holding_cost_no_production=dict(y2023_usd=627273, y2023_usd_per_month=52273, y2024_usd=289000, y2025_usd=248000, statement="2023 care and maintenance ~52 k/month with no split (G-70); 2024-25 opex 289 k and 248 k with no sales (~21-24 k/month)",
                                    sources=["data/processed/database_review/acc_findings.md s.1 finding 3", "data/processed/database_review/res_findings.md item 5 (Tonalli P&L 1QOiCRJv, 1kPVuMAR)"]),
    excluded_overheads=dict(cnh_reported_2022_admin_usd_per_month=39177, detail="Jul-Oct 2022 monthly CNH reports: contract administration fee 8,104, project administration 7,870, office 6,101, information administration 6,101, personnel 11,000 USD/month", source="docs/13_cnh_filings_gis_cmi.md s.2 'Costs'",
                            g_and_a_2019_usd=673984, g_and_a_source="data/processed/deck_notes/accounting_notes.md s.5"),
    peak_structure_2019_for_contrast=dict(total_usd=839052, items={"Separator rental": 186456, "Site engineers": 173474, "Tanks": 112290, "Trucking emulsion": 91583, "Water trucking": 83944,
                                                                   "Water disposal fee (1.33 USD/bbl)": 32534, "Sampling": 36139, "Chem/stim": 46952, "Water-injection well equipment rental": 75680},
                                          source="data/processed/database_review/acc_review.csv row 1FCUF9Pp (2019 Total Company LOS)"),
    economic_model_assumptions=dict(
        description="TEC-12 economics rebuild (src/econ_rebuild.py dict P; terms from the 2023 IFR workbook 'Model (Tec-10 & Tec-12)'), 2026 USD, inflated 2 %/yr from 2026",
        fixed_usd_per_well_month=2500, battery_fixed_usd_per_month=10000, disposal_well_fixed_usd_per_month=1500,
        variable_usd_per_bbl_oil=7.25, variable_usd_per_bbl_oil_note="= 5.00 + 2.25 trucking/handling (2023 workbook H15)",
        variable_usd_per_bbl_water=3.25, variable_usd_per_bbl_water_note="= 2.25 + 1.00 (2023 workbook H16)",
        abandonment_usd=150000, inflation_per_yr=0.02, cost_base_year=2026,
        incremental_case_fixed="well fixed 2,500 only (battery, disposal and area fees carried by producing TEC-10)",
        area_charges=dict(as_paid_usd_per_month=5224, as_paid_build="FMP contractual quota MXN 29,829/month at the model's 18 MXN/USD (= 1,657) + IEEH USD 42,800/yr (= 3,567)",
                          statutory_exploration_usd_per_month=2638, extraction_phase_usd_per_month=3922, applies_to="stand-alone case only"),
        glj_comparison=dict(glj_ye2025_fixed_usd_per_well_month=1670, glj_variable_usd_per_bbl=5.85, glj_water_charge="none", glj_abandonment_usd_per_well=75000,
                            glj_ye2022_field_fixed_usd_per_yr=227000, glj_ye2019="2,200 $/well/month + 294 k$/yr", source="docs/10_econ_rebuild.md bridge; data/processed/database_review/res_findings.md item 7"),
        sources=["src/econ_rebuild.py lines 20-31 (P dict)", "data/processed/econ_rebuild/summary.json 'parameters'", "docs/10_econ_rebuild.md", "data/processed/econ_2023/assumptions.csv rows 18-25", "docs/01_econ_2023.md cost table"]))
json.dump(ob, open(OUT + "opex_breakdown.json", "w"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- drilling_costs.json
afe = json.load(open(REPO + "data/processed/afe/summary.json"))
byday = pd.read_csv(REPO + "data/processed/afe/afe_by_day.csv"); byday["stage"] = byday.stage.str.strip()
short = {"rig & rig move": "Rig & move", "tubulars & wellhead": "Tubulars & WH", "mud, fluids & disposal": "Mud & fluids", "downhole tools & directional": "Directional & tools",
         "logging, perforating & completion": "Logs, perf & compl.", "supervision, engineering & HSE": "Supervision & eng.", "cementing": "Cementing", "site & civil": "Site & civil"}
phase_lab = {"Pad & Cellar construction, Conductor hammering": "Pre-spud (pad, cellar, conductor)", '12 1/4"': '12¼" hole', '8 1/2"': '8½" hole', "Completion": "Completion"}
ph = byday.groupby("stage", sort=False).agg(usd=("daily_total_usd", "sum"), days=("day", "count")).reset_index()
dc = dict(
    title="Drilling and completion costs: TEC-12 AFE and actual Tonalli wells",
    currency="USD (AFE currency confirmed USD, docs/08_afe.md s.3, G-44)",
    tec12_afe=dict(
        afe_total_usd_nov2020=1572724, note_5000="AFE is 1,572,724 not 1,567,724: SUB formula for Drilling Pad Maintenance (5,000) deleted in the Sep-2021 copy",
        days=dict(pre_spud=6, drilling_and_completion=14, first_date="2020-11-09", last_date="2020-12-08"),
        by_category=[dict(label=short[c["category"]], category=c["category"], usd_2020=round(c["usd_2020"], 0), share=c["share"]) for c in afe["categories"]],
        by_phase=[dict(label=phase_lab[r.stage], usd_2020=round(r.usd, 0), days=int(r.days)) for r in ph.itertuples()],
        by_phase_note="phase totals summed here from afe_by_day.csv daily totals",
        by_day=[dict(day=str(r.day).strip(), stage=r.stage, date=r.date, daily_usd=round(r.daily_total_usd, 0), cumulative_usd=round(r.cumulative_usd, 0)) for r in byday.itertuples()],
        top_lines=[dict(label=t["description"], vendor=t["vendor"], usd_2020=t["usd_2020"]) for t in afe["top_lines"]],
        absent_from_afe="contingency, production casing, cement bond log, owner's costs, insurance",
        escalation=[dict(case=e["case"], factor=e["escalation_factor"], usd_2026=e["usd"], cad_spot_1p3915=e["cad_at_spot"]) for e in afe["escalation"]],
        escalation_basis="base x1.297 = US drilling PPI (FRED PCU213111213111) 401.286 Sep-2026 / 309.400 Nov-2020; low x1.15, high x1.40 kept as range; spent Jan 2027 at USD 2.08 MM in the economics",
        other_tec12_cost_quotes=[dict(label="Programme rig-phase cost (Prog12 p.58)", usd=804750), dict(label="Work Program 'Total cost'", usd=1500000), dict(label="GLJ YE2020 DCET", usd=1500000),
                                 dict(label="GLJ YE2025 capex (directional, 2023 $)", usd=1900000), dict(label="GLJ YE2020 horizontal (2020 $)", usd=2400000), dict(label="IFR 2023 economics (TEC-10 re-entry)", usd=1800000)],
        other_quotes_sources="data/processed/deck_notes/wells_ops_reserves_notes.md TEC-12DES; data/processed/database_review/res_findings.md item 7; docs/08_afe.md s.4",
        sources=["data/processed/afe/summary.json", "data/processed/afe/afe_categories.csv", "data/processed/afe/afe_by_day.csv", "data/processed/afe/afe_escalated.csv", "docs/08_afe.md"]),
    actual_wells=dict(
        tax_pool_basis=dict(description="Capital per well, tax-cost basis, Dec-2023 tax-pool schedule (Drive 1YKAgyRk), costs incurred 2017-2021",
            wells=[dict(label="TEC-10", usd=2956480, parts={"Drill": 1682270, "Complete": 569765, "Core": 68200, "Site": 405745, "Casing & tubing": 200000, "Survey, access, roads (2017)": 30500}),
                   dict(label="TEC-11 (HZ)", usd=3514960, parts={"Drill": 2869365, "Complete": 206225, "Casing & tubing": 439370}),
                   dict(label="TEC-2 workovers", usd=860450, parts={"Site prep": 71575, "Wellhead": 38790, "Initial workover & swab": 513360, "Site expansion for TEC-11": 143435, "Added perforations": 93290}),
                   dict(label="TEC-7 workover (injector)", usd=172225),
                   dict(label="Facilities 2019-20", usd=92599, parts={"TEC-2/TEC-10 pipeline": 29243, "Separator": 22407, "60 m3 tank": 10302, "Refurbished injection pump": 30647}),
                   dict(label="TEC-12 pad works (2021)", usd=15000)],
            pool_total_31dec2023_usd=7611714,
            sources=["data/processed/database_review/acc_findings.md s.1 finding 4", "data/processed/database_review/acc_review.csv row 1YKAgyRk (part split for TEC-2 and facilities)"]),
        tec10_other=dict(afe_usd=2924760, afe_ref="AFE ST028, 1 Jan 2018 basis (TEC-10 Updated Drilling Cost Summary 15Jun2018.xlsx AFE Cover O39)",
                         actual_to_15jun2018_usd=2039002, actual_split={"Drilling": 1810649, "Tangibles": 228353}, cash_paid_2018_19_usd=2584844,
                         sources=["data/processed/deck_notes/accounting_notes.md s.2", "data/processed/deck_notes/wells_ops_reserves_notes.md TEC-10DES"]),
        tec11_other=dict(afe_drilling_usd=2250000, afe_ref="AFE TON2018DR002",
                         actual_vs_budget_by_phase=[dict(label="Drilling", actual=3105308, budget=2853870), dict(label="CBL / clean-up", actual=129360, budget=100000),
                                                    dict(label="Completion (Workstrings)", actual=962850, budget=831000), dict(label="Tantoyuca test", actual=206225, budget=150000),
                                                    dict(label="Total", actual=4403743, budget=3934870)],
                         tracker_26dec2018_total_usd=3025996, tracker_main_items={"Rig": 582846, "Mud": 449500, "Directional": 230600, "Cement": 232500, "Prod. casing": 219000, "Int. casing": 215000, "Rig move": 195000, "Location": 195000},
                         caveat="tax pools carry 3.51 MM vs 4.40 MM 'actual': the 0.96 MM Workstrings completion invoices left the pool in 2020 (possible liability, G-64)",
                         sources=["data/processed/afe/summary.json 'tec11'", "data/processed/deck_notes/accounting_notes.md s.2", "data/processed/database_review/acc_findings.md finding 5"]),
        tec2_tec7_cash=dict(tec2_workovers_cash_2018_19_usd=757408, tec2_detail={"Initial workover": 656290, "Add. perf and workover (2019)": 101118}, tec7_workover_cash_usd=95848,
                            source="data/processed/deck_notes/accounting_notes.md s.2 table (Monthly Summary capital, cash basis)")))
json.dump(dc, open(OUT + "drilling_costs.json", "w"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- technical_tables.json
FRC = "data/processed/deck_notes/fluids_rock_core_notes.md"
vol = json.load(open(REPO + "data/processed/volumetrics/summary.json"))
src = pd.read_csv(REPO + "data/processed/volumetrics/ooip_by_source.csv")
lab = {"IFR Summary (GLJ) sheet (all economic models 2020-2023)": "IFR (GLJ sheet)", "Petrel Robertson, deep contact -2374 mSS, all wells": "Petrel Robertson, all wells",
       "Petrel Robertson, TEC-10 new logs only": "PR, TEC-10 logs", "Petrel Robertson, TEC-2, 9 and 10 logs": "PR, vintage logs", "CNH / PEMEX official (El Abra trend table)": "CNH / PEMEX booked"}
logst = json.load(open(OUT + "_logstats.json"))
def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items() if k != "n" and not (k == "DTC_us_ft_TEC10Logs")}
    return o
tt = dict(
    oil=dict(
        no_lab_pvt="No laboratory PVT study exists: no measured bubble point, Rs, Bo, live viscosity or compressibility. Every PVT number in circulation is a correlation or the PEMEX Ezequiel Ordonez-41 analogue.",
        api_by_sample=[
            dict(sample="TEC-2 whole crude, test separator", date="2018-05-17", lab="SGS Deer Park", api=28.4, sulphur_pct=1.66, viscosity="13.67 cSt @40 °C; 3.911 cSt @98.9 °C", note="38 % water as sampled"),
            dict(sample="TEC-10 Zone C well sample", date="2018-07-27", lab="SGS Deer Park", api=26.5, sulphur_pct=1.67, viscosity="18.73 cSt @40 °C; 9.369 cSt @60 °C", note="early clean-up, 40-44 % water; H2S vapour 1,000 ppm"),
            dict(sample="TEC-10 shore tank", date="2018-11-21", lab="Intertek", api=30.42, sulphur_pct=1.66, viscosity=None, note="OCR"),
            dict(sample="TEC-10 shore tank", date="2018-12-11", lab="Intertek", api=30.78, sulphur_pct=1.08, viscosity=None, note="OCR"),
            dict(sample="TEC-10 'Tanque 10'", date="2019-01-15", lab="Intertek", api=30.1, sulphur_pct=1.57, viscosity=None, note="OCR"),
            dict(sample="TEC-2 test, field density", date="2018-05", lab="Weatherford (field)", api=28.38, sulphur_pct=None, viscosity=None, note="0.885 SG @60 °F"),
            dict(sample="TEC-9", date="2012", lab="PEMEX", api="30.1-30.3", sulphur_pct=None, viscosity="dead oil 13.2 cP @26 °C; 3.4 cP @90 °C", note="docs/gaps.md G-31 update 2026-10-25"),
            dict(sample="CNH monthly filings (field)", date="2020-2021", lab="filing", api="28.4-30.4", sulphur_pct=None, viscosity=None, note="monthly range"),
            dict(sample="TEC-10DES (CNH VHP)", date="2022-11", lab="filing", api=30.9, sulphur_pct=1.6, viscosity=None, note="salt 48.8 lb/Mbbl"),
            dict(sample="TEC-11 Tantoyuca (not El Abra)", date="2019-08-22", lab="Química Apollo", api=17.0, sulphur_pct=None, viscosity=None, note="asphaltenes 9.84 %")],
        bottom_hole_samples_unexplained=[dict(sample="TEC-10DES Zone A+B", date="2018-07-12", sg=0.9577, sulphur_pct=2.56, viscosity="776 SUS @100 °F"), dict(sample="TEC-10DES Zone B", date="2018-07-12", sg=0.9223, sulphur_pct=2.33, viscosity="396 SUS @100 °F")],
        pemex_1956_75_densities_20_4=dict(range=[0.857, 0.881], samples={"TEC-6 1956": 0.874, "TEC-7 1957": 0.871, "TEC-6 1959": 0.881, "TEC-7 1971": 0.868, "TEC-2 1974": 0.857, "TEC-6 Jun-1974": 0.868, "TEC-6 1975": 0.867, "TEC-7 1975": 0.863}, note="OCR of handwritten forms"),
        pvt_measured_vs_correlated=[
            dict(property="Oil gravity, °API", pemex_eo41="20", ifr_calculator="28.4", ihs_tec2="28.0", ihs_tec10="28.2", measured="26.5-30.8 stock tank"),
            dict(property="Rs, scf/bbl", pemex_eo41="336 (59.9 m3/m3)", ifr_calculator="552 assumed", ihs_tec2="541", ihs_tec10="570", measured="never measured; produced GOR 565 (1966-92 cum)"),
            dict(property="Bubble point, psia", pemex_eo41="1,877 (132 kg/cm2)", ifr_calculator="2,849 hard-coded", ihs_tec2="2,901 (IPR)", ihs_tec10="3,452 (IPR)", measured="never measured"),
            dict(property="Bo, rb/stb", pemex_eo41="1.1923", ifr_calculator="1.299 at Pb", ihs_tec2="1.283", ihs_tec10="1.296", measured="never measured"),
            dict(property="Live-oil viscosity, cP", pemex_eo41="11.2", ifr_calculator="0.624 at Pb", ihs_tec2="0.739", ihs_tec10="0.718", measured="dead oil only: 13.67 cSt (TEC-2), 18.73 cSt (TEC-10) @40 °C"),
            dict(property="Reservoir temperature, °C", pemex_eo41="65", ifr_calculator="95", ihs_tec2="101.0", ihs_tec10="98.6", measured="97.5-99.3 (2018 gradient surveys)"),
            dict(property="Initial pressure", pemex_eo41="252 kg/cm2", ifr_calculator="3,684 psia", ihs_tec2="24,190 kPa(a) @2,309 m", ihs_tec10="24,304 kPa(a) @2,322 mTVD", measured="see docs/05_pressure.md")],
        source=FRC + " s.1, s.4; docs/gaps.md G-31"),
    gas=dict(
        compositions_mol_pct=[
            dict(well="TEC-6", date="1970-08-28", sample="casing gas (PEMEX 105/70, OCR)", N2=None, CO2=4.78, H2S=0.66, C1=79.81, C2=7.91, C3=4.24, iC4=0.51, nC4=1.18, iC5=0.25, nC5=0.27, C6plus=0.42, gas_gravity=0.730, mw=21.139, ghv_btu_scf=1152),
            dict(well="TEC-2", date="2018-05-17", sample="separator gas 6.3 kg/cm2a, 38.8 °C", N2=0.920, CO2=10.572, H2S=1.746, C1=70.442, C2=6.665, C3=4.252, iC4=1.159, nC4=1.697, iC5=0.681, nC5=0.731, C6plus=1.135, gas_gravity=0.842, mw=24.4, ghv_btu_scf=1155),
            dict(well="TEC-10", date="2018-07-27", sample="test separator 8.8 kg/cm2a, 32.6 °C", N2=0.812, CO2=11.142, H2S=0.989, C1=70.321, C2=7.707, C3=4.701, iC4=1.119, nC4=1.545, iC5=0.505, nC5=0.490, C6plus=0.669, gas_gravity=0.829, mw=24.0, ghv_btu_scf=1133)],
        compositions_source=FRC + " s.2 (C6plus for 2018 = reported C6+ mol %; TEC-6 = 'hexanos y más pesados')",
        produced_gor_history_scf_bbl=[
            dict(period="1956 initial tests (By Zone)", gor="431-576 (TEC-2, 6, 7); TEC-9 1973 765", source="data/processed/production_summary.json solution_gor_refs"),
            dict(period="1964-12 TEC-6 flowing survey", gor=685, source="docs/gaps.md G-31"),
            dict(period="1966-1992 cumulative (field)", gor=565, source="data/processed/production_summary.json cumulative_gor"),
            dict(period="1993-1999 cumulative", gor=1073, source="production_summary.json (allocation-affected)"),
            dict(period="2003-2012 cumulative", gor=556, source="production_summary.json"),
            dict(period="2013-2016 cumulative", gor=9535, source="production_summary.json (TEC-2 late-life allocation artefact)"),
            dict(period="all 1966-2016", gor=667, source="production_summary.json"),
            dict(period="TEC-10 flowback Jul-Aug 2018", gor="median 767 (P10-P90 597-942)", source="docs/gaps.md G-31"),
            dict(period="TEC-10 initial test 2018-10-20", gor=762, source="production_summary.json / By Zone"),
            dict(period="2020 CNH filing", gor="1,157 on gross oil; 1,361 on net", source="docs/13_cnh_filings_gis_cmi.md s.2"),
            dict(period="2021 CNH filing", gor=859, source="docs/13_cnh_filings_gis_cmi.md s.2"),
            dict(period="GLJ 12 months to Oct 2019", gor="field 1,342; TEC-10 1,265; TEC-2 1,787", source="docs/gaps.md G-31 2026-10-25"),
            dict(period="GLJ TEC-10 Q4-2021", gor=1127, source="data/processed/deck_notes/wells_ops_reserves_notes.md"),
            dict(period="GLJ TEC-10 2022", gor=8162, source="docs/gaps.md G-31 2026-10-25")],
        tec10_monthly_gor_scf_bbl=json.load(open(REPO + "data/processed/production_summary.json"))["tec10_monthly_gor"],
        tec10_monthly_gor_source="data/processed/production_summary.json tec10_monthly_gor (daily sheet; Ptbg 875 -> 450-500 psi)",
        situation=dict(
            solution_gor="about 550-570 scf/bbl (IFR 552 = 1966-92 cumulative 565; IHS TEC-10 570; IHS TEC-2 541); PEMEX 336 scf/bbl does not describe this fluid",
            gas_cap_evidence="1956 TEC-2 open-hole test 2,307.4-2,321.7 mKB (top El Abra): 41 m3/d oil, 47,702 m3/d gas, GOR 1,163 m3/m3 (~6,500 scf/bbl), PTP 174 kg/cm2; deeper tests GOR 77 and 96 m3/m3. PEMEX 1971 TEC-2 schematic gas-oil level at 2,319 mKB (~2,315 mSS). Probably a small crestal gas cap originally; current extent unknown",
            flaring="2017 plan justified flaring with GOR 60 m3/m3 (337 scf/bbl) vs 742-859 measured 2018-21 (~2.5x), under a 98 % utilisation norm; declared 6,000 m3/d produced, 4,000 flared; Nov-2022 0.9 MMcf flared 'quema aprobada' (G-67)",
            tec10_gor_rise="TEC-10 monthly GOR 643-1,038 in the first year, rising above 1,800 from Aug 2019 as tubing pressure fell to 450-500 psi; local gas breakout near the wellbore, consistent with Pb above the flowing pressure",
            sources=["docs/17_government_records.md (TEC-2 1956 tests)", "docs/18_kinjal_briefing.md lines 133, 205", "docs/gaps.md G-67, G-31", "docs/04_production_database.md s.5"])),
    water=dict(
        analyses=[dict(well="TEC-2", date="2018-05-17", tds_mg_l=50145.4, nacl_equiv_ppm=49912.5, cl_mg_l=30250, resistivity_ohmm_75F=0.128, ph=6.68, sg=1.0326),
                  dict(well="TEC-10", date="2018-07-27", tds_mg_l=36787.5, nacl_equiv_ppm=34402.5, cl_mg_l=20850, resistivity_ohmm_75F=0.196, ph=6.98, sg=1.0239)],
        other=[dict(item="PEMEX El Abra formation water", value="45,000 ppm; Rw 0.075 ohm·m @65 °C"), dict(item="Rw used in repo Archie", value="0.054 ohm·m @98.6 °C"),
               dict(item="Rw from 2018 lab @98.6 °C (Arps, reader's note)", value="TEC-10 0.074; TEC-2 0.048 ohm·m"),
               dict(item="TEC-2 2018 test field salinity", value="69,000-90,750 ppm"), dict(item="TEC-10 2018 flowback field salinity", value="19,000-22,000 ppm"),
               dict(item="TEC-11 Tantoyuca water phase", value="Cl 31,550 mg/l; salinity 52,058 mg/l")],
        source=FRC + " s.3"),
    core=dict(
        well="TEC-10 core 1", interval_cut_mMD="2,352-2,362 attempted", recovery="1.20-1.32 m (12-14 %)", subsea="~2,317 mSS (inside the perforated interval)", age_lab="Cretácico Superior",
        plugs=[dict(plug="N1H1", depth_mMD=2352.25, phi_ambient=0.030, phi_500psi=0.0234, phi_3400psi=0.0173, k_air_500_mD=0.037, k_klink_500_mD=0.020, k_klink_3400_mD=0.004, grain_density=2.696, so_pct_pv=58.8, sw_pct_pv=23.9, sg_pct_pv=17.3),
               dict(plug="N1H2", depth_mMD=2352.70, phi_ambient=0.076, phi_500psi=0.0665, phi_3400psi=0.0633, k_air_500_mD=1.158, k_klink_500_mD=0.956, k_klink_3400_mD=0.356, grain_density=2.709, so_pct_pv=19.7, sw_pct_pv=20.5, sg_pct_pv=59.8),
               dict(plug="N1H3", depth_mMD=2352.89, phi_ambient=0.079, phi_500psi=0.0755, phi_3400psi=0.0715, k_air_500_mD=0.245, k_klink_500_mD=0.174, k_klink_3400_mD=0.084, grain_density=2.713, so_pct_pv=13.8, sw_pct_pv=17.8, sg_pct_pv=68.4)],
        dean_stark_note="toluene extraction before cleaning; gas by difference; WBM, no tracer",
        petrography="Six thin sections 2,352.15-2,353.24 m: miliolid/textulariid grainstones (one argillaceous wackestone-packstone with Globotruncana at 2,352.38); recrystallised, calcite-cemented, sealed fractures; visual porosity 1-5 % (intercrystalline, moldic, dissolution 2-4 %); no hydrocarbons or impregnation in thin section; no dolomite/anhydrite; outer-shelf environment",
        contrast_with_well_test="plugs 0.1-0.5 mD Klinkenberg at stress vs 18 mD well-test k on 13.2 m: flow through fractures/vugs",
        source=FRC + " s.5"),
    ooip=dict(
        by_source=[dict(label=lab[r.source], ooip_mmbbl=r.ooip_mmbbl, area_km2=round(r.area_km2, 2), gross_m=None if pd.isna(r.gross_m) else round(r.gross_m, 1), ntg=None if pd.isna(r.ntg) else round(r.ntg, 3),
                        phi=None if pd.isna(r.phi) else round(r.phi, 4), sw=None if pd.isna(r.sw) else round(r.sw, 3), bo=None if pd.isna(r.bo) else r.bo, file=r.file, note=r.note) for r in src.itertuples()],
        monte_carlo_mmbbl=dict(p90=8.1, p50=10.0, p10=12.2, mean=10.09, draws=20000,
                               inputs_triangular=dict(area_km2=[2.40, 2.55, 3.12], gross_m=[40, 44, 47], ntg=[0.30, 0.40, 0.45], phi=[0.045, 0.060, 0.075], sw=[0.18, 0.25, 0.35], bo=[1.19, 1.25, 1.30])),
        tornado_mmbbl=dict(base_mode_case=vol["mode_case"], swing={k: dict(low=v[0], high=v[1]) for k, v in vol["swing"].items()}),
        recovery_factor_context=dict(reef_rim_median_rf_to_date=0.30, reef_rim_prod_weighted_rf=0.29, reef_rim_3p_eur_rf_p90_median_p10=[0.12, 0.31, 0.40], best_reef_rim_3p=0.53,
                                     tecolutla_cnh_basis="24.5 % to Apr 2015; ~25 % with production to 2022 on 7.8 MMbbl", tecolutla_ifr_basis="18 % on 11.2 MMbbl",
                                     ooip_density_mmbbl_km2=dict(tecolutla=2.5, reef_rim_median=8.3), n_fields=45),
        produced_mmbbl=dict(recorded_to_2022=1.715, with_wellfile_allocations=1.975),
        remaining_recoverable_mmbbl=dict(formula="OOIP x RF - 1.98 (allocation basis)", rf_columns=["25 %", "29 %", "33 %", "38 %"],
                                         rows={"CNH 7.8": [0.0, 0.3, 0.6, 1.0], "P90 8.1": [0.1, 0.4, 0.7, 1.1], "P50 10.0": [0.5, 0.9, 1.3, 1.8], "P10 12.2": [1.1, 1.6, 2.1, 2.7], "IFR 11.2": [0.8, 1.3, 1.7, 2.3], "PR 12.0": [1.0, 1.5, 2.0, 2.6]},
                                         note="summary.json labels the 29 % column 'RF 28%' (int(0.29*100) truncation in src/volumetrics.py line 63); values are at 29 %. CNH 7.8 at 25 % is -0.02, shown as 0.0. PR 12.0 row rounded here from summary.json"),
        handover_message="0.3-1.6 MMbbl remaining, ~0.9 MMbbl at trend-average recovery on the P50 OOIP",
        sources=["docs/07_volumetrics.md", "data/processed/volumetrics/ooip_by_source.csv", "data/processed/volumetrics/summary.json", "src/volumetrics.py"]),
    marl=dict(
        what_it_is="The 'marl' above El Abra is the Tantoyuca formation. At TEC-10 the whole 2,294-2,311 mSS TEC-12 window (2,328-2,346 mMD) is Tantoyuca on cuttings XRD; El Abra starts at 2,348 mMD (-2,312.9 mSS; log top 2,309.5-2,310.3 mSS). Low resistivity there is lithology (silty calcareous marl, pyrite 3-6 %), so TEC-10's water-saturated window result does not test crestal El Abra. TEC-101 shows the same signature above a sharp El Abra top at -2,334 mSS; the TEC-11 lateral sonic (~73 µs/ft) matches the marl, suggesting the lateral may never have entered El Abra.",
        xrd_tec10=dict(file="RockWise 100851 XRD workbook, Drive 1qbViWE2 (62 cuttings, 2,290-2,490 mMD, 2018-05-02)", window_10_samples=dict(quartz_pct=31, quartz_feldspar_pct="38 (31-47)", total_clay_pct="9 (3-16)", calcite_pct=50, dolomite_pct="0.7 (0-2)", pyrite_pct="3 (4-6 at 2,336-2,346 mMD)"),
                       el_abra=dict(calcite_pct="91-100", dolomite_pct="up to 6", perforated_samples_calcite_pct="97-98")),
        published_values=dict(tec10_window_ILD_median=5.2, tec10_window_R85_ohmm="~5.6 (never above 7)", tec10_window_PE=3.86, tec10_window_GR=134, tec10_perforated_PE=5.09, tec10_dtc_marl_us_ft=71, tec10_dtc_el_abra_us_ft="52-57", tec11_lateral_dtc_median_us_ft=73,
                              tec10_mechanics_window="YME ~5 Mpsi, PR 0.31, no Stoneley mobility", tec101_above_el_abra="ILD 5-7, SPHI 15-20 %, GR ~100", ifr_eval="2,305-2,311 mSS VSH 0.74, SWE 1.0; net pay 5.8 m all at 2,314-2,332 mSS",
                              note_gr134="docs/14 window GR 134 and perforated GR 79 are the GRGM curve; the main gr curve reads 85 and 43-45 over the same depths (both in log_ranges below)"),
        log_ranges_p10_p50_p90=clean(logst),
        log_ranges_note="Computed here from the repo log CSVs (P10/P50/P90 of samples in each unit). TEC-101 and TEC-9 are digitised vintage logs with uncalibrated GR scales; the TEC-101 DT values (160-250) are not in µs/ft as printed and the unit is not stated in the file - use for shape only. TEC-10 DTC from the dipole sonic file.",
        sources=["data/processed/database_review/geo_findings.md finding 1", "docs/gaps.md G-47 (2026-10-25, 2026-10-26), G-75, G-79", "docs/19_database_review.md", "docs/20_seismic.md", "docs/14_sw_sensitivity.md s.1", "data/processed/petrophysics/summary.json tec10_zones"]))
json.dump(tt, open(OUT + "technical_tables.json", "w"), indent=1, ensure_ascii=False)
print("ok", ph.to_string())
