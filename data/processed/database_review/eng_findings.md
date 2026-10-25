# Engineering folder: findings (key `eng`)

Folder: TECOLUTLA DATAROOM / Engineering (`1TEJCjAs8Cu_OYn74-UjuEVY7PBgBxmFJ`), with subfolders Pressures, Fluid Analyzes, Wellbore Diagrams and Well Tests. No deeper subfolders.

## Counts
- Files inventoried: **35** (plus 4 subfolders). All unique within the folder. The IHS English and Spanish reports are translations, not byte duplicates.
- **Covered: 10.** These match a covered title at the same size: Intertek 20190118, TEC-2 Gas Comps, TEC-2 Muestreo, both IHS Spanish reports, and estado mecánico 5, 7, 9 and 101. The tenth is `Tecolutla2 Analisis Stiff`, which has the same size as the covered TEC-2 Stiff; I read it and the content is identical.
- **Read: 21. Partial: 4.**
  - `201809 Tecolutla-10 Welltest Data.xlsx`: the text rendering is cut at about 1 MB, in the gauge columns.
  - `20190128 Tec-11 Wellbore Diagram.pdf`: the drawing did not render.
  - The two IHS English reports: I read the summary and conclusions only. They match the covered Spanish copies.
- Binaries: 0. Not read: 0. Images: 0.

## Most important new facts and corrections (ranked)

1. **PEMEX booked no proved or probable reserves at Tecolutla in 2015.** The CNH "Volumen original, reservas y producción acumulada al 1 de enero de 2015" table (`1EemRu29…`) gives for Tecolutla:
   - Original oil 7.8 MMbbl and original gas 8.8 bcf.
   - **1P 0.0, 2P 0.0, 3P 0.1 MMbbl.**
   - Cumulative 1.9 MMbbl oil and 1.7 bcf gas (2.2 MMboe).

   This is the official baseline before Tonalli, and the planned post-closing third-party reserve report will be compared with it. It is not in the repository. Use it for the Kinjal reserves-classification question. It also confirms G-41 (7.8 MMbbl CNH volume).

2. **The TEC-11 mechanical state in the repository is wrong** (`Tec-11 VF.pdf`, Tonalli, 25 Sep 2019):
   - The 4½" 13.5 lb/ft L-80 liner runs from a tie-back at **1,869.18 mMD to 2,863 mMD**, not to TD.
   - A 5.9 m **fish** sits at 2,866–2,872 mMD, and **open hole** runs from 2,872 to 3,283 mMD.
   - The water-invaded perforations are five 3 m intervals from **2,643.5 to 2,745.5 mMD**. The repository has "ten proposed 2 m intervals 2,624–2,806" and the briefing has 2,674–2,745.
   - The surface casings are 9⅝" H-40 at 500 m and 13⅜" at 40 m.

   Fix `casing_strings.csv` and figure 18, and the briefing A5 wording.

3. **TEC-6 was abandoned by PEMEX in 2007 with a parted production casing at 352 m** (`BLOQUE_TECOLUTLA_6_ESTADO_MECANICO.pdf`, updated 31 Aug 2007):
   - The last intervention ran 5 Mar to 2 Apr 2007.
   - The 6⅝" casing is broken ("rotura") at 352 m.
   - Plugs are set at 298.06 m, at a cement retainer at 1,947.62 m (squeeze holes at 1,965–1,967 m) and at about 2,235–2,280 m.

   The repository's TEC-6 record stops at the 1956 completion. TEC-12 will be drilled from the TEC-10 pad next to TEC-6, so this matters for anti-collision, shallow integrity and the abandonment-liability answer (briefing B3-17, B5-25).

4. **The May 2019 TEC-2 schematic does not show the 2,319–2,320 m add-perf** (`Tec-2 VF.pdf`, 16 May 2019).
   - It shows the packer at 2,292.65 m and the mechanical plug at 2,322 m, both consistent with G-59.
   - The only producing interval it shows is 2,307–2,311 m (1972). So the G-59 correction now rests on the operations log alone. Confirm it from the perforating job ticket before the slide states it as fact.
   - Two smaller points: the liner top is 2,284.37 m against PEMEX's 2,288.70 m, and the "P.T. 2,490 md" label was copied from the TEC-10 template.

5. **PEMEX measured 263–410 mD at TEC-2 in 1956** (`Tecolutla-2 Well Test May 24, 1956.pdf`, memo DIY-101, Ing. E. G. Loreto):
   - The open-hole interval was 2,307–2,322 m, tested on a 6 mm choke and then built up from 243.2 to 252.0 kg/cm² at 2,310 m.
   - Results: Ko 410 mD from the build-up and 263 mD from Darcy. PEMEX called both approximate, and the OCR of the calculation page is poor.
   - For comparison: IHS matched 50 mD with skin +196 at TEC-2 in 2018 and 18 mD at TEC-10; the core plugs measure 0.04–1.2 mD.

   This supports the fracture-flow argument and the TEC-2 workover case (review §7). The build-up chart also confirms the 3.80 m rotary-table elevation (G-58) and the 2 h 45 min reading (G-36).

6. **The January 2019 forecast carried TEC-11, -12 and -13 as horizontals at 694 bbl/d each** (`Tecolutla Production to Dec 2018.xlsx`, FORECAST rows):
   - Each well declines to 1 bbl/d after 30 years, about 0.69 MMbbl per well.
   - In the same workbook, TEC-10 runs from 149 bbl/d to about 329 kbbl.

   This gives the forecast lineage for the "rate assumption came down" slide: 694 bbl/d (Jan 2019 horizontal), then 342 bbl/d (Aug 2020 IFR vertical), then 180 bbl/d (current base). Relevant to G-18 and G-38.

7. **CNH field series 1960–2016** (`Oil/Gas production by field`). Field oil every month Jan 1966 – Jul 1971 at 30–100 bbl/d (TEC-6 alone); field-wide zeros Oct 1974 – Apr 1975, **Jun 1978 – Sep 1979, Feb 1999 – May 2003**, so those G-34 runs are true shut-ins. Peak 0.93 thousand bbl/d in Mar 1972 confirms 932 bbl/d. Resolution is 10 bbl/d: a cross-check only.

8. **TEC-10 test, 20 Sep 2018 – 28 Jan 2019** (`201809 … Welltest Data.xlsx`): 131 days on 12/64": 152.9 bbl/d oil, 138.1 bbl/d water, 161.8 Mcf/d, 52 % oil cut, Ptbg 680 psi, 20,025 bbl. PEMEX accepted 4,355 bbl for 1–29 Oct 2018 (meter vs truck 7.6 %). The 1,550–2,030 scf/bbl GOR of Sep–Oct coincides with orifice-plate changes ("irratic"); 720–830 scf/bbl at about 510 psi in Jan 2019 is the cleaner figure. Confirms the repository series and the G-31 caveat.

9. **TEC-10 lower zones** (IHS English): Zone A (2,433–2,442 mMD) no inflow after acid; Zone B (2,394.5–2,413.5 mMD) recovered 16.9 m³ water with the fluid level rising about 100 m/h, but less than the 19.6 m³ injected, so not conclusive; Zone C H₂S 140 ppm. Briefing A5 "A/B tight" should read "A tight, B weak water inflow".

10. **TEC-3 DST** (`Tecolutla Summary.xlsx`), 2,376.8–2,380.8 mKB (about 2,371–2,375 mSS): 980 m gasified oil + 80 m salt water, final shut-in 23 MPa, oil 909 kg/m³ (about 24 °API, denser than crestal 874–880), water cut 16 %. The deepest oil in the field, consistent with GLJ's −2,374 mSS lowest known oil, although PEMEX recorded the well as "invaded by water".

## Contradictions with the repository
- `casing_strings.csv` TEC-11 (item 2) and TEC-6 (item 3). G-59 (item 4). Briefing A5 TEC-11 perforations (item 2) and "A/B tight" (item 9).
- TEC-10, minor: the A/B interval limits are rounded in the CSV (VF and IHS give A2 2,433.0–2,437.0, A1 2,438.0–2,442.0, B1 2,410.5–2,413.5, B3 2,394.5–2,398.0); the conductor is at 40 m, not 30; the Aug 2018 string was 2⅞" on a 7" packer at 2,111 mMD.
- IFR 2018 `Well Reviews`: TEC-9 El Abra top 2,327 m (about 26 m below the GLJ pick) and temperatures of 65/82 °C (measured 97.5–101 °C). Working values; do not quote. The 2017 summary's Psr of 25.1–25.4 MPa has no datum (G-35).

## Gaps closed, narrowed or opened
- **Narrowed G-34:** the 1978–79 and 1999–2003 runs are CNH field-level zeros.
- **Confirmed G-36, G-37/G-51 and G-58:** the 1956 chart, and the 9 Aug 1971 error is already present in the Mar 2018 Pressure Summary.
- **Opened, G-59 follow-up:** obtain the Feb 2019 TEC-2 perforating ticket. The May 2019 schematic omits 2,319–2,320 m.
- **Opened, casing register:** update TEC-6 to the 2007 abandonment state, with the casing break at 352 m, and TEC-11 to the final state above. Relates to G-54.

## Files to obtain in native form
- `201809 Tecolutla-10 Welltest Data.xlsx` (3.76 MB): the rendering is truncated in the gauge section (same issue as G-52).
- `20190128 Tec-11 Wellbore Diagram.pdf`: the schematic graphic did not render.
- The PEMEX TEC-6 2007 abandonment report behind the estado mecánico (not in this folder).
