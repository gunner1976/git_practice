# Geology folder (key `geo`): findings

Folder: TECOLUTLA DATAROOM / Geology (`1VviB3hrMR29ZAP6Qnu_Q4xfGgMuftzI6`), 22 subfolders, 98 files.

## Counts

| Item | n |
|---|---|
| Files inventoried | 98 (all ids unique, no in-folder duplicates) |
| Covered (title in covered_titles.txt, size identical to the repo copy) | 84 |
| Unique, not yet covered | 14 |
| Read in full | 2 (formation tops CSV, XRD workbook) |
| Partial (text layer gives only headers or scales) | 6 (five Weatherford TEC-10 PDF prints, XRD log PDF) |
| Unreadable (connector returned no text) | 1 (XRD report PDF) |
| Image skipped (TIFF, cannot be rendered) | 1 |
| Binary, metadata only | 4 (TEC-10 DLIS: sonic raw up/down, sonic processed, Stoneley) |
| Not read | 0 |

The folder `Tecolutla Well Logs/Tecolutla 7/TEC-7 Logs were lost by PEMEX` is empty. Its name is the only record that TEC-7 has no logs.

## Ranked findings

**1. The XRD shows the whole TEC-12 window at TEC-10 is Tantoyuca, not El Abra (G-47, decisive).**
Source: `100851_Tonalli Energy_Tecolutla-10_RockWise Report_05028AM.xlsx` (`1qbViWE2lr-EL5Pcc7CU8_-VwbbTE3jS5`). It holds bulk XRD on 62 cutting samples, 2,290–2,490 mMD, dated 2018-05-02.
- Samples are labelled Tantoyuca down to 2,346 mMD and El Abra from 2,348 mMD. On the survey basis that boundary is at 2,311.0–2,312.9 mSS. The logs agree: GR falls from 82 to 36 gAPI and ILD rises from 9 to 19–29 ohm·m at 2,345–2,346 mMD.
- In the window (2,328–2,346 mMD, i.e. 2,294–2,311 mSS, 10 samples), the means are quartz 31 %, quartz plus feldspar 38 % (range 31–47), total clay 9 % (3–16), calcite 50 %, dolomite 0.7 % (0–2) and pyrite 3 % (4–6 % at 2,336–2,346 mMD).
- El Abra below 2,348 mMD is 91–100 % calcite with up to 6 % dolomite. The perforated samples (2,350 and 2,352 mMD) are 97–98 % calcite.
- **What this means:** the 2026-10-24 G-47 update said 13–16 m of the TEC-10 window lies above the El Abra top. The XRD shows it is all 17 m. TEC-10's "window is water-saturated" result (Sw ≥ 1.1) therefore measures a silty calcareous marl and says nothing about El Abra saturation at the crest.
- **Correction:** the review calls PE 3.8 an "argillaceous/dolomitic" response. Dolomite is ≤ 2 %, so it is not dolomitic. Quartz and clay diluting the calcite explain the PE; my rough mass-weighted estimate is about 3.7 b/e at 2,330 mMD.
- Pyrite at 4–6 % may also lower the induction resistivity.
- **For the presentation:** TEC-9 (top −2,296 mSS) becomes the only well that actually samples the crestal El Abra window. The TEC-12 case rests on TEC-12 being structurally about 14 m higher than TEC-10.
- Caveats: these are cuttings (lag and caving), sampled every 2 m, with total clay only (no clay types). No TOC data despite the template notes.

**2. The "GR polarity confirmed field-wide" claim does not hold at TEC-10 inside the El Abra.**
I recomputed Spearman rank correlations from the repo's `data/processed/petrophysics/TEC10_logs_mss.csv`, split at the XRD top (2,311 mSS):

| TEC-10 interval | GR vs neutron | GR vs density porosity |
|---|---|---|
| 2,280–2,380 mSS (as published) | 0.28 | — |
| Tantoyuca only | 0.71 | 0.46 |
| El Abra only | −0.20 | −0.40 |

TEC-9 (0.45 vs sonic) and TEC-2 (0.34 vs neutron) keep a positive correlation within the El Abra. At TEC-10 the published polarity is a lithology contrast between the two formations. Briefing A7 ("high GR marks porosity") and `docs/09` §2 should say so, or drop TEC-10 from the claim.

**3. The formation-tops table is the source of the GLJ map tops, and it adds new tops and contacts.**
Source: `Tecolutla Formation Tops.csv` (`1zT_XBQ63IFD4BLCv9SKMiO7j5cuc9DJq`), Drive date 2019-01-27, no author. It gives measured-depth tops for 9 wells.
- Converted to subsea depth, it reproduces the GLJ 2019 labels to within 0.3 m: TEC-6 −2,294.1, TEC-9 2,309.84 mMD, TEC-2 −2,301.6, TEC-7 −2,304.0, TEC-10 −2,309.7, TEC-11DES −2,311.9, TEC-101 −2,333.7 and TEC-5 −2,551.0 mSS.
- **New in the repo:** TEC-3 top El Abra 2,378.58 mMD = −2,372.6 mSS (unreadable on the GLJ map), and the first printed numbers for TEC-7 and TEC-11DES.
- **TEC-10 top:** 2,344.58 mMD = −2,309.7 mSS, 2.7 m deeper than the cross-section panel's 2,307 mSS that G-47 uses.
- **TEC-2 conflict:** the table's 2,305.64 mMD (−2,301.6 mSS) contradicts the TAN reading of 2,320 mMD / 2,316 mSS from cuttings.
- **TEC-11DES conflict:** the table puts El Abra at 2,611.8 mMD (−2,311.9 mSS), 66 m (vertical) below where the Rise mud log turns to carbonate (2,360 mMD, −2,245 mSS). The table calls that carbonate onset "Tantoyuca_A" (2,356.55 mMD). TEC-11's stratigraphy is unresolved.
- **Tantoyuca columns:** they are internally inconsistent (on TEC-3 and TEC-2, Tantoyuca_A is shallower than the Tantoyuca top) and sit up to 68 m off the PEMEX picks (TEC-6: 2,160.75 vs 2,229 mMD). Do not quote them.

**4. The oil-water contact: a fourth number (briefing Q2).**
The same table has an O/W_CONTACT column for two wells only:
- **TEC-3:** 2,380.00 mMD = −2,374.0 mSS. This is GLJ's lowest known oil (−2,374.2), placed at TEC-3 TD.
- **TEC-10:** 2,443.00 mMD = −2,402.8 mSS, 29 m deeper. This pick sits at the base of perforation zone A (2,433.5–2,442.5 mMD). That zone gave no inflow and was tight on the 2018-06-30 injectivity test, so the pick is an interpreter's line, not a tested contact.

Present both numbers, with that caveat, alongside "water at 2,350 m", the wet TEC-2 perforations and −2,374.

**5. TEC-10 Weatherford header (stereonet and borehole-shape prints).**
- **Elevation:** GL 1.00 m, DF 5.13 m. This is a third 5.13 m source against the adopted 6.13 m (G-46 was resolved by decision; nothing changes).
- **Depths:** TD driller 2,490, logger 2,487 m; casing logger 2,280.5 m.
- **Mud and temperature:** sodium brine 1.13 g/cc; Rm 0.12 ohm·m at 29 °C, Rmf 0.09, Rm 0.05 ohm·m at 99 °C; BHT 99 °C. The BHT confirms the 98.6 °C used in the Archie work.
- **Image-log picks:** the counts (bedding 57, mixed 21, conductive 8, resistive 4) match the repo dip LAS exactly. The bedding vector mean of 3°/267° has a resultant of 0.42, so the poles are scattered and it is not a structural dip.

## Repository impact summary

- **G-47:** narrowed and strengthened. TEC-10 does not test the El Abra window at all (XRD, logs and tops agree). The remaining risk is whether TEC-12 finds El Abra at about −2,296 mSS, with TEC-9 as the only analogue.
- **Partly closed:** the core notes' gap "no XRD/mineralogy" (item 7) for cuttings, though there is still none for the core. The geology notes' gaps on TEC-3, TEC-7 and TEC-11 tops (items 4–5) are partly closed.
- **Opened (proposed new gaps):**
  - The TEC-11DES El Abra pick vs its mud-log lithology.
  - The basis of the TEC-10 O/W pick at −2,402.8 mSS.
  - TEC-2 top: 2,305.64 vs 2,320 mMD.
- **Contradicts:** `docs/09` §2 and briefing A7 on GR polarity at TEC-10, and the review/G-47 wording "dolomitic".

## Obtain in native form

- The RockWise XRD report PDF (`1tattGcpgSvlBlNj06OdR_q7cbGBE2jB2`; empty text, it may hold a narrative) and the XRD log TIFF or PDF, for the window figure.
- The TEC-10 composite print (`1RjMK5X7FQ0-AJuHknOhHaVEX_qotNRyC`), a ready one-page well summary.
- The four TEC-10 DLIS files (509 MB in total) and the 1.07 GB job zip, needed only for sonic or Stoneley reprocessing (G-52).
- The interpreter's tops/contacts project (Petrel) behind `Tecolutla Formation Tops.csv`, so the TEC-10 O/W and TEC-11 picks can be explained (G-55).
