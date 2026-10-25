# Presentations folder (key: pres): findings

Folder: TECOLUTLA DATAROOM / Presentations (`1wsEyq3xMMNyFu4w4GLfSJVsA7tAfo18r`). It holds two files and no subfolders. Neither file was in `covered_ids.txt` or `covered_titles.txt`. One of the two could not be read, so I also read four related versions held in other folders. Those rows are marked `[outside assigned folder]` in `pres_inventory.csv` and `pres_review.csv`.

## Counts

| | In folder | Related, outside folder | Total |
|---|---|---|---|
| Inventoried | 2 | 31 | 33 |
| Unique | 2 | 12 | 14 |
| Read | 1 (`1lea5umst…`) | 4 (`1gJNicmV…`, `1nhRmg3Q…`, `15NoXLu55…`, `1LKG5MBh…`) | 5 |
| Unreadable | 1 (`16NYnJalc3…`) | 2 (the AF and KPG versions) | 3 |
| Duplicates | 0 | 19 (15 copies of the Tec-11 Final pptx; 4 others) | 19 |
| Not read (earlier drafts) | 0 | 6 (GRE, GRE conflicted copy, CAH 01-25, 2019-01-24 draft, July 2019 pptx, a 3,645,177 B PDF variant) | 6 |
| Covered / binaries | 0 / 0 | 0 / 0 | 0 / 0 |

## Ranked findings

**1. The IFR November 2023 Presentation is unreadable through the connector. Get it natively.**
- The file is `16NYnJalc3fEUc5lOLROVxpilf8P_iZUW`, 53.2 MB, last modified 2023-10-19.
- `read_file_content` returns an empty rendering for this copy, for its same-size duplicate, for the AF version (2023-10-23) and for the KPG version (`1vxjGZmcH46z5uEZK7Y3c56ES7VvrlKpr`, 2023-10-24, Kevin's edit and the latest one).
- It is probably the deck shown alongside the Nov 2023 share consolidation and the 2023-10-24 TEC-12 economics. If so, it is the last set of claims a counterparty saw before Kinjal: TEC-12 rate and EUR, reserves, and the price factor (G-17, G-18, G-24, G-38).
- No PDF export of it exists on the Drive. Ask Kevin for the KPG pptx or a PDF.

**2. In 2019 the operator already suspected the TEC-12 window was a transition zone (bears on G-47).**
- Source: the July 2019 strategy deck (`1LKG5MBhO4vRyvHMnAEhudF_6UNm-vQvQ`, p15) and the 2022 IDESA re-issue (`15NoXLu55…`).
- The deck states: "Either the regional free water level has risen from 2,380 mTVDss to approx 2,316 mTVDss, with a transition zone above it, or the water is coming up through fractures from a high permeability aquifer."
- Under the first reading, the 2,294–2,311 mSS window sits in the transition zone, which matches the 4–5 ohm·m readings.
- This is the operator's own words supporting the repository's caution. Use it on the TEC-12 risk slide.
- Depths in the deck are on the By Zone basis (TEC-10 at 2,311.5–2,315), not the survey basis (G-46).

**3. A fourth OWC/FWL figure exists: original FWL 2,380 mTVDss** (July 2019 deck p13 and p15; IDESA 2022).
- Add it to briefing B1.2, which currently lists three figures.
- It is within about 6 m of the TEC-3 lowest known oil (−2,374.2 mSS) that GLJ used.
- The Jan 2019 deck instead says only "PEMEX OWC 90 m lower than TEC-11 planned perfs" and prints no number. Combined with the 2,380 m figure, that would put the planned perfs near 2,290 m, inside the TEC-12 window. This is arithmetic from two decks, not a stated value; verify it against the TEC-11 well plan.

**4. TEC-11 lessons, in the operator's own words** (July 2019 p11–p14; IDESA 2022).
- TEC-11 was drilled at 320° to cut critically stressed natural fractures (SHmax 80°, a conjugate set) predicted from TEC-10. The survey gives 316–331°, which confirms this.
- The same deck says "faults and fractures connect aquifer to oil column". IDESA 2022 adds "natural fractures could have been enhanced by acid stimulation".
- **New test detail, not in the repository:**
  - By 2019-07-12 TEC-11 had produced about 935 bbl of water, 1.5–2× its load fluid, at 78,000 ppm Cl ("still spent acid"), with only trace oil.
  - TEC-10 needed more than 1,100 bbl of water (15–20× load) before it showed measurable oil.
  - So the July 2019 read on TEC-11 was premature. The later 286 bbl/d water liner test settled the result.
- This supports the briefing's "execution, not reservoir" framing (A5, C6). Add one lesson: well azimuth and an unisolated acid job targeted the aquifer conduits.

**5. The Jan 2019 TEC-11 Results deck (`1lea5umst…`) confirms the TEC-10 daily data exactly.**
- The Interval C chart (inferred slide 7) is the same series as `data/processed/tecolutla_tec10_daily.csv`. Both give:
  - on 2018-10-20: 231.6 bbl/d oil, 78.3 bbl/d water, 176.4 Mcf/d gas, 771.5 psi;
  - a 124-day sum of 19,132 bbl (the deck says "over 19,000").
- Also confirmed:
  - 1,475 bbl post-stimulation flowback;
  - TEC-2 316 kbbl since 1972, consistent with the repository's 328,146 bbl less about 10 kbbl Tonalli-era oil;
  - TEC-2 cuttings at 2,326–2,370 mMD: miliolid microcoquina with isolated light-brown oil stains.

**6. Claims in that deck that the repository contradicts.** Do not reuse them unqualified.
- **"Stable oil cut and high flowing pressures."** Water cut went from 42 % to 49 % and Ptbg from 875 to 527 psi (monthly averages) inside the deck's own window.
- **"High-porosity reef margin in TEC-10 upper zone / excellent reservoir."** The repository reads 4–5 ohm·m with Sw ≥ 1.1 on the core-supported porosity (G-47).
- **"Natural fractures throughout the El Abra on FMI."** The tool is a CMI. No open fractures appear in the window or in the perforations; they start only below 2,320 mSS (G-09).
- **"Successfully drilled, cased TEC-11 … multiple completion intervals."** The liner hanger and tie-back failed, and the lateral was in mudstone–wackestone below target (G-27, G-28).
- **"TEC-11 similar section to TEC-2."** This is not supported, and "limestone at 2,611 mMD" falls inside the logged 2,584–2,615 mMD shale. Check it.
- **Tantoyuca "upside".** The test gave trace oil at 17 °API and 96 bbl/d of water.

**7. Possible dating error in briefing A5.**
- The briefing gives "131 bbl/d at 49 % (Sep 2018)".
- In the daily series, 131–133 bbl/d at 49 % water cut falls on 2019-01-19 to 01-21. Sep 2018 averaged 101 bbl/d at 63 % water cut, during clean-up.
- Check the source (Jaguar deck) before quoting it.

**8. Quote worth using:** "Huge aquifer with a relatively small oil reservoir" (IDESA 2022, PSDM map slide). It is IFR's own summary and matches the review's framing.

## Figures worth reusing

Slide and page numbers are inferred from text order; the renderings drop all images (G-52).

- **July 2019 PDF** (`1LKG5MBh…`, 3.7 MB, within the connector download limit, so the most practical source):
  - p3: PSDM map with the oil/aquifer outline;
  - p4: seismic traverse TEC-5 to TEC-7;
  - p6: producing-wells cross-section at −2,300/−2,320/−2,340 m;
  - p12: top El Abra map with SHmax and TEC-11;
  - p13: seismic depth section with original and possible current FWL.
- **Jan 2019 pptx** (`1lea5umst…`):
  - s5/s15: 3D top El Abra with OWCs;
  - s7: TEC-10 test chart;
  - s16: TEC-2 facies table;
  - s19: TEC-10 tie to the DMI-enhanced PSDM.
- **2020-09-22 cut-down** (`1nhRmg3Q…`, 5.9 MB): structure figures only.

These are the only seismic displays available while G-55 (SEG-Y and Petrel) is open. They are images, not data.

## Gaps

| Gap | Effect |
|---|---|
| G-47 | Supported. Operator's 2019 transition-zone hypothesis (finding 2). |
| G-09 | Confirmed open as a wording fix: the IFR decks say FMI. |
| G-55 | Image-only stopgap identified (figures above). |
| New | IFR Nov 2023 deck unreadable (finding 1). |
| New | Briefing B1.2 OWC list incomplete (finding 3). |
| New | Briefing A5 Sep 2018 test figure possibly misdated (finding 7). |

No gap is closed.

## Files to obtain natively

1. `1vxjGZmcH46z5uEZK7Y3c56ES7VvrlKpr`, IFR Nov 2023 KPG pptx, or a PDF of it.
2. `1LKG5MBhO4vRyvHMnAEhudF_6UNm-vQvQ`, July 2019 strategy PDF, for its figures.
3. `1lea5umstKZro_FJ6vVrr6LR4FXXpX3Ac`, Tec-11 Results Final pptx, for the seismic and test images.
