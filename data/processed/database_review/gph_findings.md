# Findings: TECOLUTLA DATAROOM / Geophysics and / El Abra Trend (key gph)

Folders: Geophysics `1f2lWl36bRe1bBapdeYEY4rkYSir-FpNS` (3 files, no subfolders); El Abra Trend `1bvCZDbBZvkwvJY2R7MQw1TAv7-OPhYbO` (2 files, no subfolders).

## Counts

| Item | n |
|---|---|
| Files inventoried | 5 |
| Unique | 5 (no duplicates inside the folders) |
| Read in full | 1 (Petrel readme docx) |
| Read partially (text only, images dropped) | 1 (Round 2.3 TM-01 deck, 18.2 MB) |
| Covered (title already read; re-read to confirm same content) | 1 (El Abra Trend Field Analogies.xlsx) |
| Binary, metadata only | 2 (Petrel.zip, Tec_PSDM2019.zgy) |
| Not read | 0 |

## Ranked findings

**1. G-55: the Petrel project and the 2019 PSDM volume ARE on the Drive.**
- `Tec_PSDM2019.zgy` (`1qdKlGUK5l9hETyrwmcy1FSbZDwmrBf7I`): 710,410,240 B, modified 2019-01-25. The readme calls it the "3D PSDM volume in depth domain". It is in **ZGY (Petrel) format, not SEG-Y**. Petrel opens it directly. A SEG-Y can be exported from Petrel, or converted with the open-source OpenZGY tools.
- `Petrel.zip` (`1cxtvuC5-2RkldobWZcCS4B2eN_blSKJy`): 17,013,922 B, modified 2019-01-25. It holds the .pet file and the .ptd folder.
- `Tecolutla Petrel Project.docx` (`1VQyPtOrQsHQiQdxV03XyYWSMT2L3LHLr`, 2019-01-31) lists what the project contains:
  - the PSDM volume, which has to be re-linked to the .zgy with "reconnect missing file";
  - Tecolutla wells and planned wells;
  - well logs and **synthetic seismograms**;
  - tops El Abra and "Tantoyuka A";
  - the block outline;
  - horizon surfaces for Top El Abra and Top Tantoyuka.

What is still **not** found in either folder:
- any SEG-Y;
- the Earth Signal PSTM volume, gathers and angle stacks;
- the velocity cube or velocity model (the readme does not list one);
- XYZ grid exports;
- the Earth Signal and DMI processing reports;
- Petrel Robertson's Figure 2 and the random lines from the drilling programme.

At 17 MB the zip cannot hold a seismic volume, so a PSTM or velocity cube would have to be a separate file. This is an inference from file size and is not verified. Bin size, fold, bandwidth, areal extent and depth range all stay unquotable until the files are opened.

Recommended G-55 status: "Partially resolved: Petrel project + PSDM 2019 (ZGY) located; SEG-Y/PSTM/velocity/reports still missing."

**2. An earlier IFR OOIP of 26 MMbbl for Tecolutla. This number is not in the repository.**

Source: the `Round 2.3 TM-01 Block.pptx` (`142XvPwho8KQR8eCEMwDavZh8Id4hLpGI`, modified 2018-02-13), table "El Abra Seismic Template Summary". It sets IFR volumes against CNIH (CNH) volumes for each field.

For Tecolutla, IFR gives:
- OOIP **26 MMbbl** and GOR 515 scf/bbl;
- 13.4 bcf solution gas, with no gas cap;
- recovery factor 7 % oil and 13 % gas;
- **remaining oil 7.9 MMbbl**.

The CNH columns give 7.8 MMbbl, 1.9 MMbbl produced and 24 %. The 7.9 reproduces as 26 × about 38 % minus 1.9, which is Miguel Hidalgo's IFR recovery factor applied to Tecolutla. That is my arithmetic; the deck does not give a method.

The deck predates the TEC-10 and TEC-11 results. It shows IFR's OOIP falling from 26 to 11.2 MMbbl, against a P50 of 10.0 and the CNH 7.8. This should go on the OOIP-history slide, because a Kinjal engineer may come across the 26 figure. It extends the OOIP reconciliation (G-41).

**3. AVO and rock-physics work existed by early 2018, and the deck itself calls the result inconclusive.** Slide titles and text in the same deck cover:
- in-situ Vp/Vs reservoir differentiation;
- brine, oil and gas carbonate plotted against the background Vp–Vs trend;
- an MH-412 synthetic tie to a 10° angle stack, with "fair correlation at ZOI";
- an AVO fluid-factor (AVOFF) volume, the carbonate trend over 5–45°, and PSTM gathers.

The conclusion: the fluid factor "may be resolving" hydrocarbon-charged El Abra, but forward models predict only a subtle difference between brine and hydrocarbon. Calibration is still needed. Inversion is limited by a complex velocity field.

Proposed future work was to extend the fluid factor downdip to the south-east of Tecolutla, and to run prestack inversion to locate the downdip OWC. This bears on the briefing's OWC question (anticipated question 2). The repository says no AVO or attribute products are described anywhere (geology_geophysics_notes §5), so this corrects that note. It also adds the AVOFF volume and the angle stacks to the G-55 list of items to obtain.

**4. Analogue recovery factors: the IFR basis.**

The IFR column of the same table gives these figures:

| Field | IFR OOIP (MMbbl) | CNH OOIP (MMbbl) | IFR RF | Other |
|---|---|---|---|---|
| Miguel Hidalgo | 22.6 | 38.1 | 38 % oil, 28 % gas | GOR 1,100 scf/bbl; 4.2 bcf gas cap |
| Gutiérrez Zamora | 5.0 | 2.6 | 21 % | 0.85 MMbbl remaining |
| Vicente Guerrero | 6.0 | 13.6 | 83 % | |

The deck says Vicente Guerrero is "fully depleted", and that either IFR's OOIP is wrong or production has been overstated. It also says "Recent drilling results in Miguel Hidalgo confirm the high recovery factor", next to "Oil 33 Mbbl" and "Oil 61 Mbbl"; the text does not give the wells or dates.

The block summary reads: fields "more depleted than expected", missing monthly production data, and "inadequate resource to justify even low bid levels".

Use in the presentation: this supports a reef-rim recovery factor of about 30–38 % as the analogue range. It also shows that the operator's own analogue OOIPs differ from CNH's by a factor of 0.5–2.

**5. The El Abra analogue workbook in this folder is the same table as the covered copy.**
- This copy: `1gZ6FOKkY0-zd3CCHsIctdlUl6vji9xk6`, 50,895 B, modified 2018-04-23.
- Covered copy: `1eln5w1CtJgTptaIKe3_vQNnG3XEFVklk`, 51,524 B, 2022-03-08.
- The 45 fields, the header note and the totals match: 509.4 km², 6,126.3 MMbbl OOIP, 1,777.7 MMbbl produced, 1P EUR RF 29 %.
- The Tecolutla row matches too: 3.1 km², 7.8 MMbbl, 24.5 % to date, 3P EUR RF 27 %.

This confirms docs/07 and geology_geophysics_notes §6. The workbook has no aquifer, water-cut, pressure, drive-mechanism, porosity or thickness data. Aquifer behaviour of the analogues therefore cannot come from this folder, and gap 10 in geology_geophysics_notes stays open.

## Contradictions and corrections to the repository

- geology_geophysics_notes §7 item 7 says there is "no synthetic at any Tecolutla well". The Petrel readme says the project contains well logs and synthetic seismograms. Which wells is not stated, and the project has not been opened. Reword the item to "synthetics exist in the Petrel project; not yet viewed".
- geology_geophysics_notes §5 says no AVO, inversion or angle-stack products are described anywhere. The TM-01 deck describes an AVO fluid-factor volume, a 10° angle stack and PSTM gathers (2018-02).
- The OOIP history in the review and the briefing (7.8 / 11.2 / 10.0 MMbbl) leaves out IFR's earlier 26 MMbbl.
- The TM-01 deck assumes a GOR of 515 scf/bbl for Tecolutla. This is an IFR assumption, not a measurement, consistent with G-31 (no PVT).

## Gaps

- **G-55:** partially closed. The PSDM (ZGY) and the Petrel project are located. Still open: SEG-Y, PSTM, gathers and angle stacks, the AVOFF volume, the velocity model, and the Earth Signal and DMI reports.
- **G-41 (OOIP):** extended with the 26 MMbbl IFR figure from about 2018.
- **New, suggested:** the TM-01 deck's maps and sections exist only as images, which the connector dropped. These are the El Abra depth maps contoured to −2,380 m for Tecolutla, Miguel Hidalgo, Vicente Guerrero and Gutiérrez Zamora, the Tecolutla dip line, and the AVO sections. They need a native pull of the 18.2 MB pptx.

## Files to obtain or open in native form

1. `Tec_PSDM2019.zgy` (`1qdKlGUK5l9hETyrwmcy1FSbZDwmrBf7I`, 710 MB): open in Petrel or OpenZGY, then export a SEG-Y and record the survey geometry, extent and sample interval.
2. `Petrel.zip` (`1cxtvuC5-2RkldobWZcCS4B2eN_blSKJy`, 17 MB): unzip and open. Export the Top El Abra and Top Tantoyuca surfaces as XYZ, the well tops, the synthetics and the well ties.
3. `Round 2.3 TM-01 Block.pptx` (`142XvPwho8KQR8eCEMwDavZh8Id4hLpGI`, 18.2 MB): pull it natively for the depth maps, the dip line and the AVO figures.
4. Still to request from Tonalli or Jaguar, since none of these is on the Drive folders reviewed:
   - the Earth Signal PSTM and processing report;
   - the DMI PSDM report;
   - the velocity model;
   - the AVOFF volume and angle stacks.
