# Tecolutla seismic: what is on the Drive (read-only review, 2026-10-25)

Paths below start at the shared drive root "Drive" (id 0AHfoefRKXj-LUk9PVA). Every row, with IDs, is in `seismic_inventory.csv` next to this file.

## 1. The leads that turned out not to be Tecolutla
- **The `353307/353308/353309_1_TC-SB-G2/G4.segy` files (9.8–14.4 GB) are not Tecolutla.** They sit in `Drive/Data Room/17246`, `/17888` and `/17889`, and one more copy is in `.../Round 3.2/`. "TC-SB" is the CNH Ronda 3.2 block code for Terrestre Convencional, Sabinas-Burgos. TC-SB-G2 and TC-SB-G4 are Burgos gas blocks; `Round 3.2 Work.xlsx` lists TC-SB-02, G1, 04, G2, G4, G5 and 12. The files at each size are the same size and probably repeat one delivery. Nothing sits next to them except Burgos and Tabasco LAS files. There is no EBCDIC header file, navigation or report.
- **The "1a. Segy" folders are not Tecolutla.** They belong to the IHSA data packs for Burgos blocks A-1, BG-01 and BG-04: Orozco-Esquina, Cuitlahuac and Algodonero 3D, plus numbered CNIH 2D lines.
- I paged through all 11 pages of the `.sgy/.segy/.zgy` title search. The rest is SRDE, Furbero, Chalupa and other VSPs, Arrastradero/Paraiso/Comalcalco 2D, Fortuna Nacional, Burgos, and two SRDE Petrel ZGYs. The only exceptions are the items listed in section 2.

## 2. What the Tecolutla seismic package actually contains
**Acquisition and processing history.** This comes from the Earth Signal proposal (Sept 2016), the processing report (Apéndice 4, Aug 2018) and the interpretation summaries.
- **Survey:** PEMEX's 3D (Furbero Ampliación merge). The block reprocessing used a partial 3D of 4,729 shots, 192 of them vibroseis and the rest dynamite. The earlier processed cut covered 105 km²; the reprocessed area was about 150 km² including tails. Coverage reaches MH-412 / Miguel Hidalgo to the northwest. Elevations are 0–80 m.
- **Earth Signal reprocessing, 2017–18:**
  - 25 × 25 m bins; inlines run NE–SW; QC lines are IL200 and XL400.
  - Two-layer refraction statics plus first-break tomography, then residual statics.
  - Spherical divergence correction (T^1.4 for vibroseis, T^1.8 for dynamite) and surface-consistent scaling. Offsets limited to 4,500 m.
  - Ground-roll attenuation (max 500 m/s, up to 20 Hz). Instrument dephasing and vibroseis designature to minimum phase. 5-component surface-consistent deconvolution.
  - Frequency-dependent noise attenuation, TPXY cross-spread noise attenuation and time-offset residual scaling.
  - 5D MWNI interpolation (offsets 0–4,500 m at 150 m; 3 azimuths of 60°), then anisotropic Kirchhoff PSTM with horizon-guided velocities, plus FXY decon.
  - Products: PSTM stack, gathers, angle stacks (0–12°, 12–24°, 24–36°), RMS and interval velocities, and a depth migration on a subset of the volume.
- **DMI Kirchhoff PSDM, 2018:** produced CRP gathers, an "enhanced" stack, 5°/10°/30° angle stacks and a well-calibrated structural velocity dated 29 Sept 2018. Jamiesco then built AVO fluid factor and sparse-spike impedance from these for Tec-11 planning.
- **Interpretation (Petrel 2017, May 2018):**
  - Tied to MH-412 sonic and density: Tantoyuca is a peak; Top El Abra is the trough-to-peak zero crossing.
  - Picked every 10th line, then autotracked.
  - Depth conversion used average velocity from the Earth Signal stacking velocity, bulk-shifted to the well tops and flexed by minimum curvature. Recommendations included PSDM and AVO.
  - Jamiesco later found a −45° phase difference on the PSDM stack at Tec-10, and that the 10° near stack ties without phase correction.

**Seismic data actually on the Drive**

| Item | Size | Copies | What it is |
|---|---|---|---|
| `Tec_PSDM2019.zgy` | 710,410,240 B | 6, identical (Kevin/Tecolutla (Shared)/Geophysics/Data; 3 × "YE 2018 Reserves (Tecolutla)/Geophysics"; Due Diligence 5.7.4 Geophysics; IFR Team Folder/TECOLUTLA DATAROOM/Geophysics) | Post-stack PSDM, **depth domain** (DMI), the volume behind the Petrel project |
| `Petrel.zip` + readme docx | 17,013,922 B | 6 | .pet/.ptd: wells and planned wells, logs, synthetics, El Abra and Tantoyuca A tops and surfaces, block outline. The seismic has to be reconnected to the ZGY |
| `554702/554703_UNION_FURBERO_AMPLIACION_MIGPRESTM{SFSG,CFCG}_..._Cut_Tecolutla.segy` | 1,069,414,632 B each | 1 each (Tonalli Team Folder/Block - Tecolutla/Dataroom/Dataroom1) | Legacy PEMEX/PGS **PSTM time** stack, CNH Ronda 1.3 cut: raw (SFSG) and filtered/gained (CFCG) |
| `rd026878_Vel_RMS_migracion_Cut_Tecolutla` / `rd026729_Vel_RMS_residuales_...` | 14 KB / 64 KB | 7 each | Legacy migration velocities as Petrel point ASCII (X, Y, Z, V), about 640 m spacing |
| ELABRA_TIME_GRID / ELABRA_DEPTH_GRID / Tec-10 synthetic | 90 MB / 8.9 MB / 8.7 KB | 2 each | Oct 2018 CNH deliverables from the PSTM interpretation |
| `ElAbraXYZJan2019_GRE.csv` (= `ElAbra1.txt`, node for node) | 88 KB | 2 | Jan 2019 Top El Abra depth grid |
| Aug 2018 XYZ (`Tecolutla_Depth_ElAbra_Aug2018`, `TopElAbra_seismic_peak`) | 0.6–0.85 MB | csv + xlsx | Earlier picks and depth maps |

**Total unique seismic bulk on Drive: about 2.85 GB** (0.71 GB ZGY + 2 × 1.07 GB legacy SEG-Y).

## 3. What is missing
None of the following turned up in any title or full-text search: "Earth Signal", PSTM, PSDM, DMI, angle, gathers, velocity, EBCDIC/header, .vel or MH-412.
- **Earth Signal:** no PSTM SEG-Y (raw or whitened), no migrated or 5D gathers, no angle stacks, no RMS or interval velocity SEG-Y, no fold cube, no statics or near-surface ASCII. Also no proper processing report; Apéndice 4 is a slide deck, and the .ppt is unreadable.
- **DMI:** no PSDM gathers, angle stacks, "enhanced" stack or velocity model (including the 29 Sept 2018 calibrated velocity), and no DMI report.
- **Jamiesco:** none of the attribute volumes.
- **Survey description:** no EBCDIC headers or SEG-Y byte maps for any Tecolutla volume, no SPS/navigation or bin-grid corner file, and no field data. So inline/crossline ranges, sample rate, record length and the ZGY's survey CRS are **not documented on the Drive**. Only the well-tie screenshot gives a clue (IL about 105–113, XL about 389–397 at Tec-10). That volume's numbering differs from the IL200/XL400 used in Earth Signal's QC.
- `Line_12_Final_PSTM_Gathers.sgy`, in Curtis Hess's home folder, has no link to Tecolutla.

## 4. Minimum set needed
**(a) QC the interpretation:**
- `Tec_PSDM2019.zgy` (1qdKlGUK…) with `Petrel.zip` (1cxtvuC5…) and its readme
- ElAbraXYZJan2019_GRE.csv, ELABRA_TIME/DEPTH_GRID and Tec-10 synthetic
- Apéndice 4 and 5, and the TECOLUTLA-10 Calibration deck

That is about 0.82 GB in all. For an independent time-domain check, add 554702 (SFSG, 1.07 GB) and rd026878. Ask Tonalli/IFR, Earth Signal or DMI for the missing PSTM, angle stacks, gathers and velocities.

**(b) Map the crest at TEC-12:** the PSDM ZGY plus the Petrel project (for the well tops and the TEC-10/11 ties) and the Jan 2019 depth grid.
- The ZGY's datum and CRS must first be confirmed inside Petrel, because no header text exists.
- Fixing the reported −45° phase, or using near stacks, needs the DMI angle stacks, which are missing.

## 5. Facts from the sidecars that bear on TEC-12 and Top El Abra
- **CRS:** UTM zone 14N, WGS84 (lat/long and XY in `Tecolutla Well Header Information.csv`; the Tec-10 location is given in ITRF2008). Tec-10 is at X 707,574.96, Y 2,262,437.07, KB 6.13 m. MH-412 is at X 704,865.05, Y 2,265,487.32, KB 8 m, TD 2,478 m, about 4 km northwest.
- **The Jan 2019 depth grid (50 m nodes) has two crests:**
  - A northern culmination at −2,284.4 m, at X 707,350, Y 2,263,169.
  - A southern high at about −2,285.7 m, at X 707,650, Y 2,262,468.
- **TEC-12DES, from the completion programme of Feb 2021:**
  - Surface location X 707,582, Y 2,262,425, on the Tec-10 pad; rotary table 8.2 m.
  - S-shaped well with about 175 m of departure toward azimuth 78°, putting the bottom hole near X 707,754, Y 2,262,460. The header reads 3,341 m MD, which conflicts with the directional table.
  - Prognosed Top El Abra is −2,296 m below sea level (2,304.2 m TVD below rotary table).
  - The grid reads about −2,289.4 m at that bottom hole and is shallowest about 100 m to the west. The target is therefore near, but not on, the southern seismic crest, and the prognosis is about 7 m deeper than the grid.
- The 2018 PNG map shows crest closures of −2,240 to −2,260 m, which differ from the 2019 grid. Sources disagree by up to about 45 m, so the depth datum (sea level or rotary table) and the velocity version need to be reconciled.
