# Tecolutla LAS from the Colab extract: findings (26 Oct 2026)

**Processing.**
- The 17 LAS gzips in `data/raw/colab_out/` were gunzipped to `data/raw/colab_out/las/`.
- Prefixes were shortened: `TON_REGISTROS…zip__…__` became `TONzip__`, and the RAR prefixes became `rar__` / `rebuilt_rar__`. The mapping is in `data/processed/petrophysics/las/colab_las_name_map.csv`.
- Each file has a `derived` row in `data/manifest.csv`.
- The files were ingested by `src/las_ingest.py`, with the new folder added to `RAW`. The catalogue now holds 123 files, 99 of them unique contents (was 106 / 94).
- mSS = MD − KB. TEC-10 uses `TEC10_logs_mss.csv`; TEC-11 uses TVD − 4.7.

## 1. Inventory

| File | Well | Curves | mMD | duplicate_of |
|---|---|---|---|---|
| `TEC-10 Logs.LAS` (PETRA, 11 Oct 2018, **EKB 6.1**) | TEC-10 | DPRL, NPRL, GRGC, DTC, RILD, **R20O/R40O/R85O** | DTC 50–2,489; rest 2,255–2,489 | new |
| `…CXD PROPIEDADES MECANICAS_26-04-2018` | TEC-10 | 38 curves: dynamic moduli, BRIT, CSG, PP_NORMAL, SVERTICAL_EXT, DTC/DTS, density-neutron | 425–2,279.5 | new |
| `…OH_8750_INTERMEDIO_26-04-2018` (+ `TONzip__` copy) | TEC-10 | 34 curves: GR, density-neutron-PE, array induction R20–R85/RTAO, imager calipers, tilt | 425–2,288.7 | new; zip copy identical |
| `TONzip__` CMI ×2, CXD ×2, dipole ×2, Stoneley, `TECOLUTLA-10_LAS` | TEC-10 | as before | — | byte-identical to on-disk files |
| `LAS Tecolutla 11-DES GAM_SST.las` | TEC-11 | TVD, ROP, HAGRT, **recorded** DTC/DTS, 192 semblance arrays (96 populated); **no resistivity** | 2,352.9–3,282.9 | new |
| `tonalli_…28012019`, `rar__…`, `rebuilt_rar__…` | TEC-11 | same | same | byte-identical to the above, including both RAR extracts |
| `BLOQUE_TECOLUTLA_6_IDWD_SCD_CCL_TIME_…2007` | TEC-6 | IDWD, SCD (depth channels, 0.1 in, equal to MD), CCL, TIME | 2,281.6–4.4, logged up | new; same header as the 2007 CBL |
| `TECOLUTLA-10_LIS_…02MAY2018.lis.gz` | TEC-10 | the 26 main-run channels, 9,438 frames, 2,255.0–2,490.9 | — | same as `TECOLUTLA-10_LAS_…` (r 0.995–0.9999) |

**The LIS file** is TIF-wrapped, and its back-pointers are corrupt. It was decoded with `dlisio` 1.0.4 after stripping the TIF wrapper, working in the scratchpad only.

**Other near-duplicates:**
- The composite's DPRL, NPRL, GRGC and RILD are the main-run curves with light edits (identical zone medians; RILD log-r 0.999 at zero shift).
- Its DTC is the dipole DTC spliced across both runs (r ≥ 0.9997), with a gap at 2,279.5–2,316.8 mMD.
- The full TEC-11 file is **not** a copy of the 3,283 m real-time snapshot. It is the recorded (memory) data: HAGRT r 0.986, DTC r 0.913.

## 2. New facts

**TEC-10 array induction over El Abra** is only in `TEC-10 Logs.LAS`. It comes from the same tool as the main run, reprocessed: R40O ≈ RILM, and R85O ≈ 1.2 × RILD. The main-run mud is brine (Rmf 0.09 ohm·m), so deep reads above shallow everywhere.

| mSS | GR | DPRL | R20O | R40O | R85O | R85/R20 |
|---|---|---|---|---|---|---|
| 2,294–2,311 (window) | 85 | 0.067 | 3.2 | 4.8 | 5.6 | 1.8 |
| 2,311–2,314 | 47 | 0.030 | 6.8 | 20.7 | 35.2 | 5.2 |
| 2,314–2,332 (producing) | 45 | 0.082 | 5.2 | 12.0 | 18.3 | 3.5 |
| 2,332–2,374 | 74 | 0.037 | 7.1 | 25.5 | 69.7 | 9.8 |

In the window, R85 stays at or below 7 ohm·m in every 2 m bin, and the invasion contrast is the lowest in the well. That fits low-permeability, conductive Tantoyuca, with no hydrocarbon signature.

**Log El Abra top at TEC-10:** 2,344.4–2,345.2 mMD (**2,309.5–2,310.3 mSS**). Across it DTC goes from 69 to 51 µs/ft, GR from 84 to 37, and NPRL from 0.10 to 0.00.

**Mechanics, dipole, Stoneley and CMI.** These are the 02-May files: on disk before, but not interpreted.

| mSS | DTC/DTS | Vp/Vs | YME Mpsi | PR | BRIT % | Stoneley index | CMI cond/mixed/res |
|---|---|---|---|---|---|---|---|
| window | 71/135 | 1.91 | 5.0 | 0.31 | 49 | 1.005 (1.02–1.04 at 2,300–2,304) | 0/3/6 |
| 2,311–2,314 | 52/98 | 1.89 | 9.7 | 0.31 | 81 | 1.00 | 0 |
| producing | 57/127 | 2.23* | 5.9 | 0.38* | 32 | **1.02–1.03** (1.06 at 2,316) | 0/3/0 |
| 2,332–2,374 | 53/100 | 1.91 | 9.3 | 0.31 | 76 | 1.00 | 6/36/0 |

\*43 % of producing-interval DTS samples are quality-flagged, so that row's Vp/Vs and PR are unreliable.

How the Stoneley index was built: measured DTST ÷ a tube-wave prediction from DTS and density (mud 1.13 g/cm³), set to 1.00 in tight El Abra. On this index only the producing interval shows mobility.

Shear anisotropy is null above 2,332 mSS and 3.1 % below 2,374 mSS (fast azimuth 39°). The window is soft, ductile rock, not fractured carbonate.

**TEC-11 lateral (2,563–3,283 mMD, 2,304.8–2,331.2 mSS):** still no resistivity. Recorded DTS has 2,047 samples against 1,082 real-time. Where both exist, recorded minus real-time is −0.1 µs/ft for DTC and −2.1 µs/ft for DTS. Lateral DTC has a median of 73 µs/ft (Wyllie 18 %), against 52–57 in TEC-10 El Abra. So the high sonic porosity is not a real-time artefact.

**TEC-6, 13 Mar 2007 (first log of the abandonment):**
- Header notes: fluid level 45 m, "pozo no mantenía nivel de fluido", PI at 2,275 m.
- CCL collars are regular, with a median spacing of 9.8 m: 342.9, 353.2 and 363.3 m. There is no anomaly at 352 m, and the 33 mV CBL dip there is an ordinary collar dip.
- So on that date the casing was continuous at 352 m. Either the parting came later, or it was an unseparated connection at 353.2 m.
- The CBL (on disk before) reads 38–52 mV from 45 to about 2,000 m, which means little or no bond (uncalibrated). It reads 5–14 mV at 2,040–2,210 m and about 1 mV at 2,220–2,281 m.
- There was no effective cement across the 352–1,100 m breach.

## 3. Implications

- **G-47:** No new log samples the crestal El Abra window. At TEC-10 the window is Tantoyuca on every new measurement: 3–6 ohm·m, YME 5, no Stoneley mobility, no conductive fractures. TEC-11's lateral still has no resistivity. The TEC-12 programme (density-neutron, PE, pressures, sample) stands.
- **G-71:** All nine items are now on disk: the seven large LAS (with the ZIP members) and the two RARs. The LIS has also been decoded. Only the TEC-10 DLIS remain, and they would add the raw array induction and waveforms.
- **G-72:** `TEC-10 Logs.LAS` gives EKB 6.1. That is a log header supporting the 6.13 basis against Weatherford's 5.13.
- **G-63:** Add the TEC-6 CCL and CBL observations.

## 4. Contradictions and QC

1. The log El Abra top (2,309.5–2,310.3 mSS) is 2.6–3.4 m above the XRD pick (−2,312.9) and matches GLJ (−2,310). The difference is probably cuttings lag.
2. `PP_NORMAL` in both CXD files is 0.44 × TVD in **metres**, a psi/ft gradient applied to metres. It gives about 1,016 psi in the window instead of about 3,330. Do not use it. SVERTICAL_EXT, at about 1.0 psi/ft, is consistent.
3. The intermediate-run header gives sandstone matrix 2.65 and TD 2,288 m. This confirms the source of the CMI-header error (`las_findings.md` QC item 6).
4. `las_findings.md` lists only RILD/RILM for TEC-10 over El Abra. Array induction exists over that interval only in the PETRA composite.
