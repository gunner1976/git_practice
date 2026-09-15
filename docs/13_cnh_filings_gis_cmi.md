# 13. CNH filings, the CNH field polygon, the CMI fracture products, and two web checks

Second pass over the open gaps that did not need Kevin. Sources are the Tonalli regulatory folders on the Drive (read through the connector's text rendering, `data/processed/drive_text/`), the CNH Ronda 1 GIS files (binary download, `data/raw/cnh_gis/`), the TEC-10 CMI LAS products already in `data/raw/`, and two web searches.

## 1. What Tonalli actually filed with CNH for TEC-12 (G-22)

`Tabla Producción 2021.xlsx` (saved 1 Oct 2020) and `Tabla Producción 2022.xlsx` (31 Aug 2022) are the CNH Plan-de-Desarrollo forecast tables. Both carry TEC-12DES as an incremental profile starting at 300.2, 246.5, 212.7, 189.1, 171.4, 157.6, 146.4, 137.2, 129.3, 122.6 bbl/d. That is the month-average of the IFR Aug-2020 curve (qi 342 bbl/d, b 1.7, Di 3.507/yr) to the decimal, i.e. the 345/400 kbbl curve reconciled in task 6 (`data/processed/forecast/tec12_profiles_monthly.csv`, column `ifr_2020_bpd`). The 2022 table adds TEC-13DES with the identical profile three months later. The 500 kbbl "FOR CNH TRANSITION PLAN" block in the 2022 economic models was therefore not what went into the production-forecast filings. Base profiles filed: TEC-2 23.6 → 20.6 bbl/d and TEC-10 47.3 → 41.2 bbl/d over the year, 76–79 and 148–154 bbl/d water. Saved as `data/processed/cnh/cnh_filed_tec12_profile.csv`.

## 2. Annual production filings 2020–2021 and the 2022 monthly report (G-32)

| Year | Net oil, bbl | Water, bbl | Water cut | Gas, MMcf | GOR, scf/bbl | API (monthly range) | Origin stated |
|---|---|---|---|---|---|---|---|
| 2020 (Anexo III.8.III) | 16,132 (gross oil column sums to 18,973) | 47,732 | 72–75 % | 21.96 | 1,157 on gross, 1,361 on net | 28.1–29.9 | "Pozos Tecolutla 2 y Tecolutla 10" |
| 2021 (Anexo III.8.III) | 17,402 | 73,827 | 81 % | 14.95 | 859 | 28.4–30.4, avg 29.28 | "Pozo Tecolutla 10" every month |
| Jul–Oct 2022 (Informe mensual 4.1) | 0 / 189 / 49 / 0 per month | 0 / 2,218 / 511 / 0 | — | 0.6 | — | — | field |

Monthly table with the database comparison: `data/processed/cnh/cnh_production_filings_2020_2022.csv`, `cnh_vs_database_monthly.csv`. Findings:

- The 2021 filing matches the ticket-based database month by month within −9 to +2 % (annual −3 %), and the filing names TEC-10 as the sole origin for all of 2021. So the 2021 sales are TEC-10 production; TEC-2 was shut in or commingled without allocation (GLJ's note "commingled for testing with Tecolutla-10" dates from 31 Jan 2020).
- The 2020 filing's monthly oil column is gross (18,973 bbl, matching the database's PEMEX-measured tickets within 0–4 % in most months) while its total line reports 16,132 bbl net. The database therefore carries about 15 % of water in the 2020 oil figure if the filing's net is right (G-53).
- April–June 2020 were zero in the filing and absent in the database: a three-month shut-in (price collapse), not a data gap.
- 2022: the approved programme was 1,400 bbl/month; reported net oil was 238 bbl in four months. The field was effectively shut in from July 2022. The database's "~25 bbl/d in 2022" is a first-half average.
- Gas: 14.9 MMcf in 2021 on 17.4 kbbl gives 859 scf/bbl, a fourth measurement above PEMEX's 336 scf/bbl PVT (G-31 now has 565, 685, ~750, 859). The 2020 gas has a 7.8 MMcf August that is probably a measurement or flaring artefact.
- API 28.4–30.4 monthly through 2020–21 confirms the Intertek 30–31 °API stock-tank values (task 11).
- Costs: the Jul–Oct 2022 monthly reports show an approved LISH budget of USD 190,595/month against USD 39,177/month actually spent (contract administration fee 8,104, project administration 7,870, office 6,101, information administration 6,101, personnel 11,000), the field being shut in. That is the floor of the corporate and regulatory overhead in v3's "USD 1.05 MM/yr" finding: about USD 0.47 MM/yr with no production.
- Per-well monthly volumes after Nov 2019 sit in the "Anexo I. Formatos mensuales" zip attachments of the measurement reports (VHP format). Only the November 2022 zip is on the Drive (`data/raw/cnh_reports/Nov-22/`): TEC-10DES produced 15 days, 2,260 bbl gross / 678 bbl net, 1,582 bbl water, 0.9 MMcf flared under the approved evaluation programme, 30.9 °API, 1.6 % S, 48.8 lb/Mbbl salt; 916 bbl were delivered to PEMEX at CAB Poza Rica on four truck days (24, 25, 29, 30 Nov). The field was restarted in late November 2022 on TEC-10 alone at about 45 bbl/d net. G-32 stays open for the 2020 and 2022 well split; 2021 and Nov 2022 are TEC-10.
- Sales prices (G-24): the CRE semi-annual sales reports for contractors (CRE-17-054-C, Jan and Jul 2022) exist on the Drive only as acknowledgement receipts; their `anexo1.xlsx` with volumes and prices is not present. The PEMEX price factor still cannot be settled from the Drive.

## 3. The CNH field polygon (G-43)

`CNH_R01_L03_2015-campos.shp` (Ronda 1, tercera convocatoria data room, WGS84) holds 13 field outlines; record 8 is Tecolutla. Its area in UTM 14N is **3.141 km²**, which is the "3.1 km²" in the CNH El Abra table, and all nine well locations in the well-header CSV fall inside it (`figures/13_cnh_polygon.png`, `data/processed/cnh/tecolutla_cnh_polygon.csv`). Bounding box 97°00.2'–97°01.5' W, 20°26.7'–20°27.8' N. IFR's 630 ac is 2.55 km², 81 % of the CNH outline; GLJ's 401/515/630 ac are 1.62/2.08/2.55 km². The CNH polygon is a 2015 administrative outline around the PEMEX wells, not a mapped closure, so it is an upper bound for area, consistent with its use as the P10 end of the task-7 range. The contract-area polygon (`AC_R1_3aConv_pol.shp`, 7.2 km²) is also on the Drive and was not needed.

## 4. TEC-10 CMI fracture products (G-09)

`src/cmi_fractures.py` reads the Weatherford fracture-density LAS (1-m counts, P10/P21/P32), the dip-pick LAS (105 picks: 72 bedding, 33 fractures) and the dipole-sonic anisotropy LAS. Zones in mMD with survey-based mSS (`data/processed/petrophysics/tec10_cmi_zones.csv`, `figures/14_cmi_fractures.png`):

| Zone | mSS | Conductive (open) | Mixed | Resistive (cemented) | P32, 1/m | Bedding dip, median | Fracture dip, median |
|---|---|---|---|---|---|---|---|
| Above window, 2,296–2,329 mMD | 2,264–2,295 | 0 | 0 | 0 | 0 | 20° (14 picks) | — |
| **TEC-12 window, 2,329–2,346** | **2,295–2,311** | **0** | **3** | **6** | 0.30 | 13° (1) | 35° (3) |
| Perforated, 2,346–2,356 | 2,311–2,320 | 0 | 0 | 0 | 0 | 40° (2) | — |
| Below perforations, 2,356–2,400 | 2,320–2,362 | 6 | 28 | 0 | 0.45 | 8° (19) | 72° (11) |
| Deep El Abra, 2,400–2,488 | 2,362–2,446 | 18 | 32 | 6 | 0.35 | 8° (36) | 53° (19) |

Reading: the image log sees no open fracture in the TEC-12 window at TEC-10, only cemented and mixed ones; the perforated 10 m that produced has no picked fractures at all, so TEC-10's production is matrix (or sub-resolution vuggy) flow, consistent with the core's 0.1–0.5 mD plugs and the +4.9 skin. Open fractures concentrate below 2,320 mSS, in the interval every well was perforated in and where the water comes from. Dipole-sonic shear anisotropy is 0–2.5 %, i.e. no stress- or fracture-induced anisotropy at log scale. The review's wording stays "CMI, not FMI"; G-09 is now evaluated and closed. The 8-m "kh" interval IHS assumed (13.2 m) is not a fracture corridor.

## 5. Web checks

**2025 fiscal reform (G-49).** The Ley del Sector Hidrocarburos (LSH) of 18 Mar 2025 replaced the 2014 Ley de Hidrocarburos; its Reglamento followed on 3 Oct 2025, and CNH's functions pass to the Comisión Nacional de Energía. The secondary sources reachable from this session agree that (i) the new simplified regime, the "derecho petrolero para el bienestar" at 30 % of the value of oil produced, applies to holders of assignments (Pemex), not to contracts; (ii) the economic conditions of existing exploration and extraction contracts remain those set by SHCP under the Ley de Ingresos sobre Hidrocarburos, with the 2025 LISH Reglamento updating procedures; and (iii) the Reglamento contemplates substitution of contracts by assignments "to benefit the State, increase the petroleum rent or strengthen the state enterprise". For the handover: the task-10 fiscal terms (31.22 % bid royalty, basic royalty, contractual fee, 30 % ISR) stand, but the incoming operator needs counsel's confirmation on the substitution clause and on the 2026 contractual-fee and surface-tax indexation. Law-firm pages are blocked by the session proxy, so this rests on search snippets: Greenberg Traurig (Feb and Oct 2025), Holland & Knight (Oct and Nov 2025), Mijares, and the Reglamento text on diputados.gob.mx.

**Drilling cost index (G-45).** The BLS producer price index for drilling oil and gas wells (PCU213111213111, Dec 1985 = 100) reads 396.7 in Dec 2025 and 396.1 in Feb 2026 per the FRED page snippet; the Nov 2020 base value is on the same page but FRED, BLS and the mirror sites are all blocked from this session. Once the Nov 2020 value is read, the AFE escalation factor is simply 396 divided by it; the assumed 1.15/1.25/1.40 in task 8 stand until then.

## 6. Gaps touched

G-22 resolved (filed profile is the IFR 2020 curve). G-43 resolved (3.141 km², all wells inside). G-09 resolved (CMI evaluated). G-32 narrowed (field-level 2020–2022 known; well split still in zip attachments). G-49 narrowed (contract terms preserved per secondary sources; counsel to confirm). G-45 partly (latest index known, base still needed). G-53 new (2020 filing gross vs net oil).
