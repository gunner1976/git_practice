# Tecolutla LAS ingestion: findings (25 Oct 2026)

Outputs: `src/las_ingest.py`, `data/processed/petrophysics/las/las_catalog.csv` (106 rows), `las_curve_index.csv`, 94 `curves_<well>_<stem>.csv`. Depths below are mSS = MD − KB (casing_strings.csv KBs). TEC-10 uses the survey conversion in `TEC10_logs_mss.csv`, and TEC-11 uses its LWD TVD.

## 1. Inventory

- **Drive search:** 523 Tecolutla LAS, ZIP and RAR records (many copies across about 120 folders). Deduplicated by title + size, that is **115 unique**: 112 LAS, 2 RAR and 1 ZIP. Other fields (JS-, YPF, TEC.SC.*, Nicapa, MGH-412) were excluded.
- **On disk:** 106 LAS files, every SHA256 recorded in `data/manifest.csv`. The 26 earlier files were re-downloaded and all SHA256s matched; 72 rows were appended for new files. Of the 106, **94 have unique content**. 12 are byte-identical copies, flagged `duplicate_of`: the TON_* re-issues, the 101 BLOQUE/REGS pair, the TEC-11 R0x pairs, and `TECOLUTLA-2_RTG_…2019`, which is identical to `GR_CCL_…2019`.
- **New against the pre-ingestion manifest:** 74 files, 68 new contents (TEC-11 51, TEC-10 7, TEC-6 3, TEC-2 2, TEC-5 2, TEC-101 2, TEC-9 1).
- **Not downloaded (9):**
  - Over 10 MB: `TEC-10 Logs.LAS` (11.1 MB), `TECOLUTLA 10_CXD PROPIEDADES MECANICAS_26-04-2018.las` (12.4 MB), and `LAS Tecolutla 11-DES GAM_SST.las` / `tonalli_las_des_gam_sst_…28012019.las` (14.8 MB each).
  - Connector closed on files over about 6 MB: `BLOQUE_TECOLUTLA_6_IDWD_SCD_CCL_TIME_…2007.LAS` (6.5 MB), `TON_REGISTROS_TEC_10_.LAS_01082018.zip` (8.9 MB), `TECOLUTLA 10_OH_8750_INTERMEDIO_26-04-2018.las` (9.9 MB).
  - RAR, no extractor in the container: `LAS Tecolutla 11-DES GAM_SST.rar` and `rebuilt.…rar` (2.3 MB).
  - Not LAS, not attempted: the TEC-10 DLIS files (40–620 MB) and the LIS file.
- **TEC-7:** no LAS anywhere. All six "TEC-7 Logs were lost by PEMEX" folders are empty. `BLOQUE_TECOLUTLA_7_EXPEDIENTE_PERFORACION.zip` (14.3 MB, id 1GFD8njg…) is the only unopened TEC-7 drilling file. **G-14 stands.**

## 2. Logs by well

| Well | What exists (file) | Coverage vs El Abra |
|---|---|---|
| TEC-2 | 1956 GR, SP, SN, LN, NPHI, microlog (`TON_reparacion…`, = `…Original_OH_Logs`); 2018 cased-hole neutron; 2019 GR-CCL | OH 2,286–2,368 mSS; LN clipped (flat ≈945, sd 6) above 2,300 mSS, so window resistivity not measured |
| TEC-3 | 1956 GR, NEUT (counts), SP, SN, LN, LAT, CALI | to 2,374 mSS; El Abra top not in repo |
| TEC-5 | 1956 GR, NEUT, SP, SN, LN, INV, CALI (2 new files) | to 2,556 mSS; El Abra −2,551 (GLJ), so about 5 m of El Abra logged |
| TEC-6 | 1956 GR (non-API), NEUT counts; 2007 CBL/VDL (new); 2018 composite `TEC-6.LAS` | to 2,330 mSS |
| TEC-9 | 1973 GR, SP, SN, ILD, DT, SPHI, NEUT, CALI; 2018 copy `TEC-9.LAS` | to 2,345 mSS; ILD ends about 2,330, SN missing below 2,305 |
| TEC-10 | 2018 Weatherford triple combo (GR, NPRL/DPRL, DEN, PE, RILD/RILM), dipole and Stoneley sonic, CXD, CMI dips and fractures, CBL; **new:** IFR evaluation `tecolutla_10_wire.las` (PHIE, SWE, VSH, VOL_UWAT), LWD GAM/ROP, 26-Apr intermediate sonic (stops 2,279 mMD) | 2,225–2,445 mSS; IFR curves 2,305–2,438 mSS |
| TEC-11 | LWD GR, ROP, resistivity RPD2/RPS2 (`LAS Tecolutla 11-DES.las`, new); lateral GR, DTC, DTS, PHIS (29 progressive snapshots); 2019 SLB CBL/GR | resistivity ends 2,341 mMD (about 2,236 mSS, 70 m above El Abra); lateral 2,242–2,331 mSS with **no resistivity** |
| TEC-101 | 1972 GR, SP, SN, ILD/CILD, DT, SPHI, NEUT; 2018 copies `TEC-101.LAS`, `MYDATA.LAS` | to 2,356 mSS (KB 8) |
| TEC-7 | none | — |

The 2018 composites `TEC-2/6/9/101.LAS` (Aug 2018) and `MYDATA.LAS` (Dec 2018) hold no new measurements. Their curves correlate at r = 1.000 with the originals at zero shift. `GR_CNVT` is TEC-6's old GR multiplied by about 16.4, and `NEUT_NRM` is the neutron multiplied by 0.27.

## 3. QC issues

1. **KB and elevation conflicts in headers:**
   - TEC-10: every Weatherford file gives EKB/EREF 5.13, against the 6.13 package basis.
   - TEC-11: the 2019 Schlumberger CBL headers carry APD/EDF 6.13, which is TEC-10's value (TEC-11 KB 4.7), so the header was copied.
   - TEC-2: EREF 3.8 against 4.0.
   - TEC-3: EKB 6.08 against 6.0.
   - TEC-5: EKB 4.3 against 4.0.
   - TEC-6: 5.73 (2007), 5.6 (1956 file) and 6.0 (`TEC-6.LAS`, also used by task 9), against 5.67.
   - TEC-101: ELEV 7.6 against EKB 8.0.
   - TEC-9: 5.0 against 5.07.
2. **Digitised pre-1975 logs are unscaled:**
   - GR reads 1–8 units in TEC-3, TEC-5 and TEC-6.
   - Neutron curves are in counts.
   - TEC-2 microlog reads 210–260 "ohm·m", which is physically impossible.
   - TEC-2 SP is positive.
   - `Tecolutla 2.LAS` (2015) is a different digitisation: SN is 9.4 times larger and NPHI is −1.8 to −2.0. Do not use it.
3. **`TEC-11 Gamma Ray.las` is not a log of the well:** the header depth unit is M but the curve unit is FT, sampling is irregular, and r ≈ 0 against the actual TEC-11 GR. It is most likely the pre-drill forward model (geosteering folder, 27 Oct 2018). Exclude it.
4. **WellSight files are headerless ASCII:** their columns were identified at r = 1.000 against the TEC-11 LAS as MD, TVD, ROP, HAGRT, DTC and DTS. The two "Dir Survey" files are mislabelled: they hold HAGRT and ROP, not survey data.
5. **TEC-10 LWD GAM is not depth-matched to the wireline:** best shift −3.4 m, r = 0.84 for the real-time file and only 0.61 for the memory file. Use the wireline GR.
6. **TEC-10 header inconsistency:** the CMI dips header copies the 26-Apr intermediate-run header (TD 2,288, "Matriz: Arenisca 2.65"). The main run states carbonate 2.71, so DPRL is correct.
7. **Other format notes:** TEC-11 PHIS reads 13–19 % against core and density porosity of 2–8 % at TEC-10, so the LWD sonic porosity is not usable quantitatively. TEC-2 and TEC-6 (2007) files are wrapped, and TEC-6 (2007) is logged upward. The 2,652 m TEC-11 snapshot carries 100+ mostly empty semblance arrays.

## 4. Interpretation for the TEC-12 window (G-47)

**a. TEC-10: the IFR evaluation is new evidence.** `tecolutla_10_wire.las` is an IFR project export with unknown parameters, uncalibrated.

| mSS | PHIE | SWE | VSH | Net pay (PHIE ≥ 4 %, SWE < 0.6), m TVD |
|---|---|---|---|---|
| 2,305–2,311 (window, lower part) | 0.005 | 1.00 | 0.74 | 0 |
| 2,311–2,314 | 0.011 | 1.00 | 0.05 | 0 |
| 2,314–2,318 (perforations) | 0.067 | 0.62 | 0.03 | 2.2 |
| 2,318–2,320 | 0.098 | 0.58 | 0.02 | 0.9 |
| 2,320–2,332 | 0.069 | 0.81 | 0.06 | 2.7 |
| 2,332–2,374 | 0.013–0.016 | 0.93–0.94 | ~0.1 | 1.5 (tight streaks) |

The best streak is 2,317–2,318 mSS (PHIE 0.10–0.12, SWE 0.35–0.40). The IFR curves do not reach 2,294–2,305 mSS. Where they do cover the window, 2,305–2,309.5 mSS is shale (VSH 0.5–1.0). This fits the 2,307–2,310 El Abra top: the TEC-10 "window" is mostly above El Abra, and the IFR evaluation finds no hydrocarbon above 2,314 mSS. The CMI files give 9 fractures in the window, none conductive. All 24 conductive fractures lie below 2,332 mSS.

**b. TEC-101 (logs on disk before but never used).** El Abra top is sharp at **2,334 mSS**: ILD jumps from about 7 to 70–360 ohm·m, SPHI drops from 15 % to 2–4 %, and SP shifts by −10 to −40 mV. This is the first log confirmation of the GLJ −2,334 pick. At TEC-101 the window depths (2,294–2,311 mSS) lie above El Abra and read ILD 5–7 ohm·m, SPHI 15–20 % and GR about 100. That is the same low-resistivity signature as TEC-10's window. The logged 22 m of El Abra are tight, so their resistivity does not indicate the fluid.

**c. TEC-9: the window is two units.**

| mSS | ILD median, ohm·m | SPHI median | GR |
|---|---|---|---|
| 2,296–2,304 (top 8 m of El Abra) | 8.0 | 0.148 | 37–51 |
| 2,305–2,311 | 56–84 (median 70) | 0.052 | 16–26 |
| 2,311–2,320 | 83 | 0.033 | — |
| 2,323–2,328 (producer) | 53 | 0.051 | — |

The parity result in task 14 (median ILD 8.7 over 17 m) therefore rests on the top 8 m only. The lower 6 m of the window is tight and resistive.

**d. TEC-3 (dry hole, water on formation test).** Normals rise to 10–20 at 2,304–2,324 mSS, fall to about 5 at 2,324–2,336, and read 1–2 ohm·m at 2,340–2,368 mSS. SP reverses at about 2,324. The El Abra top is unknown, and the curves are unscaled digitisations. This is only a qualitative low-resistivity reference below about 2,340 mSS.

**e. TEC-5.** The deepest 25 m (2,526–2,550 mSS, just above the −2,551 top) read 0.5–0.9 ohm·m. That is water, 200 m below the field, so it has no bearing on the window.

**f. Oil-water contact.** There is no new direct contact.
- At TEC-10, IFR SWE goes to about 1 below 2,332 mSS, and conductive fractures appear only below 2,332.
- No other well with resistivity reaches the GLJ LKO (−2,374.2) except TEC-3, which is unscaled.
- TEC-11's lateral (2,242–2,331 mSS) has no resistivity, so its water production cannot be tested against logs.

**g. TEC-7, TEC-3, TEC-5, TEC-101.**
- TEC-7: nothing new.
- TEC-5: two new 1956 files.
- TEC-3 and TEC-101: no new files, but their logs are now parsed, and TEC-101 gives a usable El Abra top.

## 5. Implications and recommended presentation additions

1. **Add TEC-101 and the IFR TEC-10 evaluation to the log panel.** Both show that low resistivity at 2,294–2,311 mSS is the argillaceous unit above El Abra wherever El Abra is deeper. The window is not a water leg in that unit.
2. **Restate the TEC-12 window stratigraphically.** The prospective unit is the top ~8 m of El Abra (TEC-9 analogue, 2,296–2,304 mSS: SPHI about 15 %, ILD about 8), not a 17 m depth band. Below it the rock is tight (SPHI 3–5 %).
3. **Quote IFR net pay at TEC-10 as 5.8 m TVD (2,314–2,332 mSS), none above 2,314.** Flag it as third-party, with unknown parameters and no core calibration.
4. **Add a QC slide:** the KB conflicts (TEC-10 5.13 vs 6.13 and TEC-11 header 6.13 are material for mSS), the unscaled 1950s logs, and the clipped TEC-2 LN, which means TEC-2 offers no window resistivity.
5. **Open items:**
   - Retrieve `TEC-10 Logs.LAS` (11 MB), the full TEC-11 GAM_SST LAS (14.8 MB) and the TEC-7 expediente ZIP outside the connector (6 MB limit).
   - Obtain the IFR parameter report (the `IFR_Tecolutla_10_MGH_412*.pptx` files sit in the same folder).
   - The TEC-12 test programme in G-47 (density-neutron, PE, pressures and a sample in the window) stands.
