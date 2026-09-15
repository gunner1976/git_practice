# Reading notes on the review (v3)

Read in full on 2026-09-15. These are the points a careful second reader would raise before the document goes to the incoming operator's technical team, with what each one needs to close it. Arithmetic checks were done on the numbers as stated in the review; nothing here has yet been checked against the source files.

## Checks that pass

- **Volumetrics reproduce.** 2.5 km² × 16.9 m × 0.07 × (1 − 0.30) / 1.19 = 1.74 MMsm³ = 10.9 MMbbl, against the stated 11.2 MMbbl. The 2.5% gap is rounding of the input parameters. Net pay 42.3 m × 0.40 = 16.9 m also reproduces.
- **Remaining recoverable reproduces.** 11.2 × 0.29 − 2.0 = 1.25 MMbbl, stated as "roughly 1.2".
- **Per-well sub-totals reproduce.** TEC-6 509,490 + 84,293 + 305,499 = 899,282 bbl. TEC-2 40,885 + 320,334 = 361,219 bbl.
- **The overhead conclusion survives** whichever way the EBITDA bridge is resolved (see below): $8.32 MM of fixed charge against $8.59 MM of NOI is 97% in the most-likely case.

## Points to resolve

1. **Field cumulative does not sum from the table (G-11).** TEC-6 899 + TEC-9 353 + TEC-2 361 + TEC-10 55 = 1,668 mbbl, not 2.0 MMbbl. TEC-7 is fitted in the type curve, so it produced, but it has no row. Pre-1960 field-level volumes are not assigned to wells. The 18% recovery factor is only as good as the 2.0 MMbbl. Task 4 closes this from the production workbooks.

2. **The EBITDA bridge in Section 6.5 is not the one the text describes.** NOI minus the three overhead lines does not give the tabulated EBITDA in any case. The residual is −2.22, −2.84, −3.64 and −4.43 $MM for the low to high cases, which is 40%, 33%, 29% and 27% of NOI: consistent with the Simmons 40%-before-payout, 20%-after carry, with earlier payout in the higher cases. So the tabulated EBITDA is *after* the Simmons carry, and the sentence "before the Simmons carry is even applied" contradicts the table. Task 1 and 2 rebuild the bridge line by line from the workbook.

3. **Simmons sales volumes are two wells, not one.** The 390 to 799 mbbl "8-yr sales" include TEC-13 from January 2022. They must not be compared with the 345 mbbl single-well type curve or the Petrel Robertson EUR without splitting TEC-12 out. Task 6.

4. **TEC-11 is described as horizontal, but the execution record has it at 61°.** Section 4 has the well "building to 61°" and at "~61°" at 2,357 mMD. Section 5.2 has carbonate entered at about 2,360 mMD, and the review then treats 2,360 to 3,283 mMD as a ~900 m lateral. Whether the well ever reached ~90° is not stated anywhere in the review. If the "lateral" stayed at 60 to 70°, then 900 m of measured depth gains 300 to 450 m of TVD and the toe is far below the oil-water contact. That would be a second, independent reason for the well to water out, and it changes the facies argument from "wrong rock" to "wrong rock, and also too deep". Task 3 settles this from the directional survey; until then, the deck should not draw TEC-11 as a horizontal lateral.

5. **Section 5.3 mixes mMD and mSS for the offset wells.** "TEC-9 at 2,308–2,311 mMD is cream miliolid grainstone" is set beside "-2,314 to -2,319 mSS" for the same well's highest perforation. With KB elevations of tens of metres, these are different intervals. The well-header CSV has the KBs; task 3 and 9 restate every depth in mSS.

6. **"16.5 m higher on structure" (Section 3) needs its basis stated.** TEC-10 top perforation −2,311.5 mSS against the TEC-6 target top −2,294 mSS is 17.5 m; against TEC-9's −2,296 mSS it is 15.5 m. 16.5 m is the mean of the two. Say so, or pick one.

7. **"Intermediate casing $187,384" against a casing design with no intermediate string.** Section 6.2 lists conductor, surface and a 7" production string to 2,350 m; Section 6.3's largest tubular line is called intermediate casing. Most likely the AFE treats the 7" as intermediate with the contingent 5" liner as production. Task 8 reconciles the AFE line names with the casing design.

8. **Dates in the chronology are copy dates, not authoring dates (G-08).** Every file in the TEC-12 Drill folder was written to the drive between 15:36 and 15:38 on 29 Sep 2023. The Work Program PDF exists at the same byte size with a February 2021 date elsewhere on the drive. "Sept 2023 — final TEC-12 work program, Petrel Robertson assessment and economics" may be right for the economics workbook (its name carries the date) and wrong for the other two. Task 1 reads the internal PDF metadata and title pages.

9. **The TEC-10 image log is a CMI, not an FMI (G-09).** Weatherford Compact Micro-Imager, 2,280.5 to 2,487 mMD, logged 2 May 2018. The interpreted image and the dip-pick LAS are on the drive. Section 3, Section 6.6 and Section 10 should say CMI. The recommendation to run an image log in TEC-12 stands.

10. **Eduardo's critique is probably not lost (G-02).** The file is 143 KB. A title-only .docx is about 12 KB. The connector most likely dropped tracked changes, comments or embedded images. To be read natively before the review's item 10 in Section 8 is repeated to the buyer.

11. **A GLJ independent reserves evaluation is missing from the forecast table (G-12).** The YE2020 GLJ report for Tecolutla (final April 2021) with its draft export workbooks and a management Q&A sits on the drive. It is an independent evaluator's view of TEC-12 and the producing wells, and it belongs in Section 6.4 beside Petrel Robertson. Task 6.

12. **Two AFE workbooks (G-10).** The April 2021 version and the September 2021 "(2)" version differ in size. The $5,000 discrepancy should be located in both before it is described as "the" AFE's discrepancy.

13. **Minor unit notes.** The 1964 TEC-6 flow test (9 m³/d oil, 1.1 × 10³ m³/d gas) is about 57 bbl/d and 39 Mscf/d, GOR about 690 scf/bbl. Show field units alongside for a North American reader. All dollar figures remain unconverted and presumed USD, per the review's own caution.

## What the notes do not change

The spine of the argument is intact: aquifer-supported, water-limited field; TEC-10 as the minimum case; TEC-11 in the wrong facies (possibly also too deep); TEC-12 into logged, un-perforated pay between two prolific wells; economics that failed on overhead rather than at the well. The points above are about making each link in that chain traceable to a source, which is what the task queue does.
