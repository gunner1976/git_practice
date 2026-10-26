# Can TEC-10 and TEC-2 still produce? Evidence to Oct 2026

Paths are relative to `/home/user/git_practice`. Rates are bbl/d of oil unless stated.

## TEC-10DES: facts

| Date | Fact | Source |
|---|---|---|
| Aug 2018 | Zone C (2,349.5–2,353 mMD; 2,314.3–2,317.6 mSS on the survey) flowed 194 bbl/d at 39 % water and 863 psig on 12/64" after stimulation. IHS build-up: k 18 mD, skin +4.9, p* 24.14 MPa at datum, with an aquifer boundary at 195 m | `data/processed/welltest/tec10_welltest_2018_daily.csv`; `docs/05_pressure.md` |
| Oct 2018 → Nov 2019 | Monthly mean fell from 181 to 77 bbl/d. Water cut rose 42 → 67 %, tubing pressure fell 875 → 450 psi, and GOR rose to 1,800–2,500 scf/bbl once tubing pressure dropped below 500 psi. Total 44,468 bbl in 431 days | `docs/04_production_database.md` §4–5; `data/processed/tecolutla_tec10_daily.csv` |
| 2019 | Four APSOL-AP "organic system" solvent jobs of 2–3 m³ each (21 Jun, 13 Aug, 1 Nov, 23 Dec 2019). Composition not confirmed. The oil's pour point is −24 °C and it is 28.9 % C10–C20, consistent with wax dropping out in cool tubing | `docs/18_kinjal_briefing.md` A6 |
| 2020 | Stimulation line of USD 4,225 in Dec 2020 (well not named) | `data/processed/database_review/acc_review.csv` (2020 LOS) |
| 2021 | Sole producer in the field. 17,402 bbl net, 81 % water, GOR 859 scf/bbl. GLJ gives a 47.9 bbl/d average at 80.9 % water. Choke opened 25 Feb 2021. "Injection pump and stims" USD 29,154 for the year | `docs/13_cnh_filings_gis_cmi.md` §2; `wells_ops_reserves_notes.md` §2.4; `acc_review.csv` (2022 workbook, final 2021) |
| Dec 2021 | 1,062 bbl oil and 6,453 bbl water, i.e. 34 bbl/d at 86 % water. Cumulative 75,832 bbl | `data/processed/cnh/cnh_production_filings_2020_2022.csv`; briefing A5 |
| 4 Feb 2022 | Field shut in after CNH rejected the Informe de Evaluación. The Sep 2022 Jaguar deck notes "stim required during restart" | `drive_reads_notes.md`; briefing A5 |
| 24–30 Nov 2022 | Restarted after a stimulation (USD 20,003, Nov 2022). 15 producing days: 2,260 bbl gross, 678 bbl net, 1,582 bbl water (70 % water cut), 0.9 MMcf flared, 30.9 °API. That is about 45 bbl/d net | `acc_review.csv` (2022 LOS); `docs/13_cnh_filings_gis_cmi.md` §2 |
| 2022 (GLJ) | 181 days on, 8.4 bbl/d on-stream (3.5 bbl/d calendar), 65.7 % water, GOR 8,162 scf/stb. GLJ: "producing at marginal rates and requires a workover to alleviate paraffin" (15 k$ planned for Feb 2023). Cumulative 77.1 kbbl at 31 Dec 2022 | `data/processed/database_review/res_review.csv` row 8 |
| Jan 2023 | Last production, 2 bbl/d (GLJ YE2025 Table 1). Shut in since | `res_findings.md` finding 4 |
| YE2024 → YE2025 (GLJ) | Carried as PDNP: restart Aug 2026 with a 15 k$ workover, EUR 225 / 300 / 383 kbbl, 33 bbl/d forecast for 2026 together with TEC-02. The text mentions "hot oil/acid workovers in 2026". The repository has no record that the workover was done | `res_findings.md` YE2024–25 table; `res_review.csv` rows 14, 33 |
| Wellbore | 4½" liner 2,133.42–2,489.33 m; 7" casing to 2,285 m, cemented to surface. A Jul 2019 "estado mecánico final" (well not named) shows 2⅜" tubing on a packer at 2,057 m. Zones A and B are below the producing zone and did not produce. Survey KB 6.13 m | `data/processed/wells/casing_strings.csv` |
| Reservoir | 24.14 MPa at datum in Aug 2018, 2 % below the 1956 initial. Both 2018 build-ups needed an aquifer (constant-pressure) boundary. No pressure measured since 2018 | `docs/05_pressure.md` §3 |

## TEC-2: facts

| Date | Fact | Source |
|---|---|---|
| 1972 → Jan 2016 | 320,334 bbl from 2,307.4–2,311 mKB (2,303–2,307 mSS). Last CNH-sourced month, Dec 2014: 9 bbl/d at 91 % water. The 2017 cédula gives a last line of 19 m³/d liquid at 80 % water on 15 Jan 2016 (about 24 bbl/d oil). The 2015–16 rows were hand-entered (G-33) | `data/processed/tecolutla_production.csv`; `docs/17_government_records.md` |
| 2017 | Registered as closed and hermetic, head partly dismantled, accepted without integrity studies | `docs/17_government_records.md` |
| May 2018 | Workover found paraffin in the tubing. Test ended at 50 bbl/d oil and 453 bbl/d water (90 %) at 16.8 MPa BHFP. IHS: k 50 mD, **skin +196**, p* 24.14 MPa at datum. PEMEX measured 263–410 mD here in 1956. Shut in afterwards for lack of water disposal | `docs/05_pressure.md` §5; `eng_findings.md` item 5; briefing A5 |
| Feb 2019 | Add-perf at 2,319–2,320 mKB (2,315–2,316 mSS) per the operations log only; the May 2019 schematic does not show it (G-59) | `docs/gaps.md` G-59 |
| May 2019 | Permanent plug at 2,322.5 m shuts off the wet deeper perforations (2,330 m and deeper). Packer at 2,292.65 m | `casing_strings.csv`; G-59 |
| Jun–Sep 2019 | 69-day test: 47 bbl/d at 75 % water and about 250 psi. GLJ's 12 months to Oct 2019: 44.4 bbl/d on-stream, 73.8 % water. Shut in Sep 2019 as uneconomic (break-even 60 bbl/d at USD 54/bbl) | briefing A5; `res_review.csv` row 2; `drive_reads_notes.md` |
| 31 Jan 2020 → Sep 2020 | Commingled with TEC-10 "for testing". Last reported rate 18 bbl/d at 72 % water (Sep 2020). About 10.0 kbbl in total since 2018 | `wells_ops_reserves_notes.md` §2.4; briefing A5 |
| Dec 2022 → Jan 2023 | Workover in Dec 2022, restarted at 23 bopd; 31 days at 22.8 bbl/d on-stream, 80.4 % water, GOR 877. GLJ calls it "uneconomic". Last production Jan 2023 at 16 bbl/d | `res_review.csv` rows 8, 33; `res_findings.md` finding 3–4 |
| YE2024 → YE2025 (GLJ) | PDNP: restart Jan 2026 (YE2024), then a 15 k$ workover in Aug 2026 (YE2025). EUR 355–365 kbbl; remaining 25.3 / 30.3 / 35.3 kbbl (1P / 2P / 3P) | `res_review.csv` rows 8, 14, 33 |
| Facilities | Battery on the TEC-2 pad; 0.52 km 2" flowline to TEC-10 (installed 17 Dec 2019); 20" × 10 ft separator. The only disposal well is TEC-7 (state unknown, G-57). Abandonment reserve USD 102,893 | `wells_ops_reserves_notes.md` §3.1; `drive_reads_notes.md` |

## Conflicts to keep visible

- **Shut-in date and cause (G-65).** Tonalli stopped production on 4 Feb 2022 (letter to PEP). The CNH filings show the field effectively shut from Jul 2022. GLJ says "early 2023 due to an environmental permit". IFR's 2024–25 representation letters say all permits are in place. The 238 bbl produced to tank in Aug–Sep 2022 is not attributed to a well. The TEC-7 injection MIA extension expired on 26 Oct 2023; nothing in the files ties it to the shut-in.
- **Per-well volumes after Nov 2019 are not separable (G-32).** The 2021 filing names TEC-10 alone; for 2020 and 2022 the split is unknown.
- **No documented intermittent schedule.** The on/off operation of TEC-2 is described as practice. No day-by-day cycling series exists in the files (briefing A6, C4).

## What this implies (interpretation, not source)

TEC-10 looks mechanically restorable at a low rate. In its last steady period it made 34–48 bbl/d at 80–86 % water, and the Nov 2022 restart gave about 45 bbl/d net after one stimulation. The decline between treatments looks like wax and near-wellbore restriction rather than pressure loss: in 2018 the reservoir was at 24.1 MPa with an aquifer boundary 195 m away. A restart should therefore expect a solvent/hot-oil job at the start and repeat treatments, roughly 30–45 bbl/d at 70–85 % water, and a water-disposal route; GLJ's 33 bbl/d for 2026 is in that range. TEC-2 can probably also produce intermittently, but at about 16–23 bbl/d with 75–80 % water. With skin +196 in 2018, the well is choked by near-wellbore damage, and the 2019 plug isolates the wet deep perforations. On the evidence it pays only when it shares fixed costs with TEC-10, which is how GLJ and Tonalli treated it. Neither restart has been tested since Jan 2023, so both hinge on three things: the permit question (G-65), the state of TEC-7 as a disposal well (G-57), and whether the planned 15 k$ workovers happen.
