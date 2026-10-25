# CNH Dataroom (folder 1HKWpLfCMrK_RVhxcKWbhpIXoRyPqsTEn): findings

The 2015 CNH Ronda 1 L03 data room for Tecolutla: PEMEX CD tables, 1956–73 well files, 2006–12 intervention logs, the Sep 2015 field survey, shapefiles and seismic velocity picks. Ids and provenance per file are in `cnh_review.csv`.

## Ranked findings

1. **G-34 can be closed. The "missing months" in the CNH production record are reported zero-production months.** The original CNH CD monthly tables are `08_CD_PRODUCCION MENSUAL` (1F-kYxj1… for TEC-2, 6 and 7; 13Im0f1z… for TEC-9). On the 1,161 common rows their volumes match the repository's IFR copy to within 0.43 bbl. The originals also carry 781 explicit zero rows with 0 producing days: TEC-2 177, TEC-6 153, TEC-7 333 and TEC-9 118. These rows fill every one of the 66 internal gap runs exactly, including 1978-06 to 1979-09, TEC-9 1999-02 to 2003-05 and TEC-7 1990-02 to 2006-09. The IFR copy had dropped them. The remaining uncovered months are pre-record or post-record only: TEC-2 1956–71, TEC-6 1956–65, TEC-7 1957 to 1968-05, and 2019–22. The TEC-2 record ends in 2014-12. The repository's 13 TEC-2 rows for 2015-01 to 2016-01 are not in the CNH record, which supports the G-33 "hand-entered" flag. PEMEX's December 2015 measurement report (1TrrRlHM…) also says "no production, the field is closed".

2. **The TEC-101 chronology in the repository belongs to another well.** `BLOQUE_TECOLUTLA_101_EXPEDIENTE_PERFORACION.PDF` (1R1pJ2iy…, with a copy and a "Notes" copy) is the final drilling report of **Cuesta Blanca-2** in Cd. Serdán, Puebla. Rig 4017 moved there "coming from Tecolutla-101" on 1972-04-15. The well's objective was Lower Cretaceous/Jurassic clastics, its open hole went to 2,678 m, and it ended on 1972-10-31. `Tecolutla 101.docx` (2016) is an English translation of that report. The repository's TEC-101 facts all come from Cuesta Blanca-2: spud 15 Apr 1972, rig release 31 Oct 1972, Jurassic syn-rift objective, problems at 2,678 m. TEC-101's own records give a different history. The PEMEX well shapefile (1dLTXyAj…) has drilling from 1972-01-28 to 1972-03-16. The log files are dated 22 Feb 1972. The estado mecánico gives plugging on 31 Mar 1972; this date is correct, not "[sic]". The 2015 field survey records a plug monument dated 3 Apr 1972. TD is 2,804 m and top El Abra is at 2,341 mMD (CD tops table). **New gap: correct `wells_ops_reserves_notes.md` (TEC-101 row) and `geology_geophysics_notes.md` l.260.**

3. **The TEC-3 surface casing was set at 601.7 m, not 501.35 m.** Three 1956 PEMEX records agree: the final report (1_JknB-X…), the exploration file (1wE8xjBe…) and the production file (1K1l1fei…). All give a 9 5/8" J-55 36 lb/ft shoe at 601.7 m, cemented on 1956-02-15. The bridge plug at 571.7–625 m was set "to drown the 9 5/8" shoe". The 2006 PEMEX sketch, and `casing_strings.csv` after it, give 501.35 m, which is TEC-5's shoe depth. The same records give TEC-3 KB 5.78 m (repository 6.00 m). This refines the closure of G-54.

4. **The lowest known oil and the OWC have independent 1956 support.** The TEC-3 drill-stem test over 2,376.8–2,380.8 m (2,370–2,375 mSS, at the top of El Abra) recovered 980 m of gassy oil (density 0.909, about 24 °API) and 80 m of salt water. It used 1,060 m of 4½" pipe. Pressures were 20/50 kg/cm² flowing and 230 kg/cm² after a 10-minute shut-in. The CNH tables transcribe the recovery as "980 m³". It is metres of pipe fill. The TEC-5 plugging programme of 31 Jul 1956 (1ITy0WZg…) places the oil–salt-water level from TEC-3 at about 2,373 mSS (OCR). That is the GLJ LKO of −2,374.2 mSS. The TEC-5 exploration file adds that Miguel Hidalgo's water level is about 203 m above TEC-5's El Abra top, which puts it near 2,350 mSS. Miguel Hidalgo is therefore a separate accumulation.

5. **A cheap stimulation lifted TEC-9 about tenfold in 2012.** The PEMEX log 1GjR7jb1… records TEC-9 at 10–11 bopd net on a 3 mm choke, with carbonate scale found at 1,790 m. The job pumped 5 m³ OSA-M solvent, 2 m³ diverter, 3 m³ 15 % HCl and 17 m³ diesel. Afterwards the well made 101.6 bopd net (113 bpd gross, 90 % oil) at 710 psi casing pressure. CNH monthly records then show 33–46 bopd for April–July 2012. The rate fell because of near-wellbore damage, not depletion. This fits the strong-aquifer storyline and is evidence for low-cost remedial upside.

6. **Abandonment state (liability).** TEC-6 leaked gas at surface and had a 6 5/8" breach at 352–1,100 m. It ran on a PCP until 2007-02-26 and was abandoned 2007-02-23 to 04-03 (1EldJkzk…, 1--MROmJ…, 11Zewmh1…). TEC-9 had a 9 5/8" breach at about 70 m (repaired 2010) and a 6 5/8" breach at about 530–833 m. It was squeezed in Nov 2012 (retainer at 2,312.36 m; plugs at 736–470 m), with the definitive plug still pending in Dec 2012 (XPS logs). The repository says "closed Jan 1999", but TEC-9 produced 2003–12 and was temporarily abandoned in Nov 2012.

7. **H2S was present at TEC-9 in 2012.** PEMEX rigged up Halliburton equipment "for wells with H2S presence" and killed the well with mud carrying a gas scavenger (19ro5aaF…). This supports briefing B4 for the PEMEX era as well as TEC-10.

8. **Fluids (G-31).** TEC-9 oil in 2012 (1UL3YTUv…): 30.1–30.3 °API. Dead-oil viscosity was 13.2 cP at 26 °C and 3.4 cP at 90 °C, so about 3 cP at reservoir temperature and less as live oil. The PEMEX 11.2/52.1 cP (Ezequiel Ordóñez-41 analogue) are not Tecolutla values. Water salinity in the 2009–15 samples has a median of 25,000–27,000 ppm.

9. **Seismic (G-55).** Two Petrel RMS-velocity point sets are present (CNIH ids rd026878 and rd026729). The residual set has 103 locations and 1,607 picks of 2,050–5,728 m/s. Near TEC-2 the picks are 2,981 m/s at 1,764 ms and 3,363 m/s at 2,246 ms, a Dix interval velocity of about 4.5 km/s. The CNH map names the 3D "554703_Un_Furb_Ampl_Mig". The SEG-Y is still missing.

10. **Areas and reserves (G-43, G-60).** Contract area 7.16192 km², which confirms the repository. CNH field polygon 3.11504 km² (repository uses 3.141). PEMEX gives a 4.9 km² reservoir area, k 6–10 mD and net 25 m. PEMEX's 2015 forecast booked 10 kbbl in every category from 1P to 3P (11L658JY…).

## Contradictions with the repository

- TEC-101 dates and objective (finding 2).
- TEC-3 surface shoe is at 601.7 m, not 501.35 m. TEC-3 KB is 5.78 m, not 6.00 m.
- TEC-6 on 1971-08-12: the CNH survey gives 246.7 kg/cm² at the 2,337 m gauge; the repository (IFR) carries 248.0, which is 0.13 MPa higher. This is possibly a second transcription error after G-51; check it against the scan. The other 15 surveys agree within 0.04 kg/cm².
- The UWIs for TEC-7 and TEC-101 (…464 and …466) are swapped in the repository header CSV.
- The PEMEX/CNH layers are NAD27, which sits about 27 m E and 200 m S of the repository's WGS84 coordinates. Do not mix the two.
- PEMEX reported the field "closed" in Dec 2015, but the repository has TEC-2 rows to Jan 2016 (G-33).
- The CNH `12_CD_PARAMETROS` porosity and Sw for TEC-2 contradict the PEMEX Resumen. Do not use them.

## Gaps closed or opened

- **Closed:** G-34.
- **Refined:** G-54 (TEC-3 shoe); G-43 (3.115 and 4.9 km²); G-55 (velocity picks); G-31 (viscosity curve, H2S at TEC-9).
- **New:** TEC-101 chronology; TEC-6 1971-08-12 reading; UWI swap; datum offset; PEMEX-era casing breaches at TEC-6 and TEC-9.

## Obtain natively

- SEG-Y and velocity volumes for the 3D "554703_Un_Furb_Ampl_Mig" (G-55).
- A cleaner scan of the TEC-3 expediente de producción.
- AutoCAD originals of the DTI and E-PTEC drawings.
- The TEC-9 expediente de producción. The CD tables cite it but it is not in this folder.

## Counts

- Inventoried: **190** files in 33 folders.
- Duplicates within the folder: **18**.
- Covered: **51** (by id, title or byte-identical size; the TEC-2/6/7/9 expedientes are the repository's copies).
- Read: **67**, plus **1 partial**. Of these, 23 XLS, XPS, dbf and velocity-ASCII files were downloaded to the scratchpad and parsed.
- Binary: **17**.
- Unreadable: **15** (vector drawings and images).
- Image skipped: **16**.
- Not read: **5**.
