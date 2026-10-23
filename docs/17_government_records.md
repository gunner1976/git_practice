# 17 — Gap investigation from government records

Request: use the government databases to close as many open gaps as possible.

## Access

The Mexican government portals cannot be reached from this session. The egress proxy refuses CONNECT to sih.hidrocarburos.gob.mx, cnih.cnh.gob.mx, datos.gob.mx, www.gob.mx, dof.gob.mx, www.diputados.gob.mx, sener, cne, banxico and inegi, and also to the US series hosts (fred.stlouisfed.org, download.bls.gov, eia.gov). No call was retried and none was routed around. Two routes were used instead:

1. **Government records already on the Drive.** These are copies of the CNIH data-room well files (PEMEX expedientes), Tonalli's filings to CNH and ASEA, and CNH acknowledgements. All were read through the Drive connector.
2. **Web search snippets** for the PPI value (G-45) and the 2025 reform (G-49). These are secondary sources only.

## Records read

| Record | Issuer / addressee | Drive id | Used for |
|---|---|---|---|
| Cédula de registro de estado de integridad, Tec-2 (15 Mar 2017) | Tonalli → CNH, contract clause 3.3 | `1P4eFDsW6xpFsFb4S9s3jdUl5j1k_6exm` | G-54 |
| Tecolutla-2 schematic, Oct 1971 | PEMEX | `1EEKXJxWHVn1g44DTN-xnZnrBSbxQppkf` | G-54, G-58 |
| TEC-2 weekly drilling reports, Forma 19, Mar 1955 – Jun 1956 | PEMEX | `1oHDmwaMhtvQy_51s1n7pa9JuZX4xN-9c` | G-54 |
| Cédula Tec-3 + PEMEX estado mecánico (updated 19 May 2006) | Tonalli → CNH; PEMEX | `1PpxStcYGyXzXPPzjzlp6xOVRTlwu-OfZ`, `1XtyXmV6SmyF0mUuUvOHnsMk9SKUcuUYu` | G-54 |
| Cédula Tec-7 (15 Mar 2017) | Tonalli → CNH | `1tUSdBpr_Wdjn2yHDR5PDkHmIrUBqecg9` | TEC-7 casing check |
| Tecolutla-7 schematic, Sep 1971 | PEMEX Poza Rica | `18-XZwHrGKz9NVG76y2eVjEvEUzUuw4PR` | TEC-7 casing check, G-58 |
| Well and installation inventory (Mar 2017); clause 3.3 b summary (24 Apr 2017) | Tonalli → CNH | `1CJsWXuRFRTMkrBBYVQROBEDv-tIwOB9z`, `1LFEZMY1EQyhpdOfsd5EqnDGtpmewEUII` | well status at handover |
| Acta Protocolo Hora Cero (23 Nov 2016) | PEP-APPRA → Tonalli | `1uOaAbWhflFxmdk6fq84USxf44yUmPota` | handover date |
| ASEA compliance reports, TEC-7 injection, May–Nov 2020 and Jun–Nov 2021 | Tonalli → ASEA | `1yqY55qQG4yx_ubG89r3f0oe9Ec-HC-tY`, `1DblNjvezUTzyp73OqzAdNxeEViUdM_5P` | G-57 |
| CNH DGM VHP (Oct 2022) and balances (Nov 2022) | Tonalli → CNH | `1nu0xjN2oJW9CDIbPp5wU9_mLhsT_URrG`, `1Tl6W3WCgtqkGxTlraqLtY-QHNfdxqBPG` | G-32 check (consistent with the register) |

## Findings

**G-54 is closed.** The TEC-2 and TEC-3 casing programmes are now in `data/processed/wells/casing_strings.csv` (69 rows) and figure 18:

- **TEC-2:** 9 5/8" J-55 at 607.9 m; 6 5/8" N-80/J-55 20–24 lb/ft at 2,307.4 m; 4 1/2" J-55 11.6 lb/ft liner from 2,288.7 to 2,375 m; cement bottom plug at 2,366 m.
- **TEC-3:** 9 5/8" J-55 36 lb/ft at 501.35 m; 8 5/8" open hole to 2,380.5 m; cement plugs at 2,310–2,380.5 m and 571.7–625 m.

**TEC-2 discovery tests (1956, PEMEX Forma 19).** Rates are as printed (m³/d, 6 mm choke):

- **2,307.4–2,321.7 m, open hole, after acid:** 41 m³/d oil and 47,702 m³/d gas, GOR 1,163 m³/m³. This is gas-cap gas at the top of the El Abra. Flowing bottom-hole pressure was 234.2 kg/cm² at 2,310 m bnm. Static pressure was 252 kg/cm²; the page prints its depth as "2010 m.bnm", which is probably an OCR error for 2,310. The 252 kg/cm² matches the initial pressure already cited from the RES (para 117).
- **2,345–2,349 m:** 56 m³/d oil and 4,320 m³/d gas, GOR 77. This interval was later squeezed.
- **2,335–2,339 m:** 72 m³/d oil and 6,900 m³/d gas, GOR 96. Water cut was 5–9 % and salinity about 45,000–50,000 ppm.
- **Logs:** electric log, microlog and caliper from 2,307 to 2,372 m, and a radioactive log from 100 to 2,372 m, all run 27 May 1956.

**TEC-7 casing is confirmed** by the 2017 cédula and the 1971 schematic: 9 5/8" at 600.5 m; 6 5/8" 20–24 lb/ft J-55 at 2,306.5 m; 4 1/2" J-55 11.6 lb/ft liner from 2,281 to 2,340 m; mechanical plug at 2,330 m. The schematic gives spud as 21 Nov 1956 and completion as 22 Jan 1957; the cédula says 25 Jan 1957.

**Status at handover (2017 cédulas).** TEC-2 and TEC-7 were closed, "hermético", with heads partially dismantled. Both were accepted without integrity studies because they form part of the development plan. The TEC-2 last-production line reads QL 19 m³/d at 80 % water (15 Jan 2016). That is 120 bbl/d liquid, about 24 bbl/d oil and 96 bbl/d water, so the inventory's "95 bpd" for TEC-2 is the water rate, not oil. TEC-7's last line is 18.7 bbl/d at 45 % water.

**G-57 is narrowed.** TEC-7 was operated as a produced-water injector under ASEA authorisation ASEA/UGI/DGGEERC/1712/2019, with compliance reports for 2020 and 2021. Volumes and pressures are still missing.

**G-45 is unchanged.** The Nov-2020 PPI value is still not readable.

**G-49 is narrowed.** Secondary sources say pre-2025 contracts keep their terms, and the CNH Feb 2025 suspension of evaluation periods and transition programmes applies to Tecolutla. The DOF wording is unverified.

**G-58 is new and minor.** The 1971 PEMEX elevation references (TEC-2 E.R. 3.80 m, TEC-7 E.M.R. 4.80 m) differ by 0.2 m from the KBs used in the repository.

## What would close the rest

- **Network access** to sih.hidrocarburos.gob.mx (per-well monthly production 2020–2022 for G-32/G-53; injection volumes for G-57), download.bls.gov or fred.stlouisfed.org (G-45), and dof.gob.mx or diputados.gob.mx (G-49). The environment's network access can be widened under the cloud environment settings.
- **Requests to Tonalli/Jaguar:** the per-well VHP zips for 2020–2022, the TEC-7 injection log, the Petrel/SEG-Y package (G-55) and the 2020–2023 ledgers (G-56).
