# Task 16 — Block and development history presentation

Output: `docs/Tecolutla_Block_and_Development_History.pptx` (52 slides, built by `src/build_block_deck.py`), with `src/block_deck_figures.py` producing `data/processed/wells/casing_strings.csv` and figures 18–20 (wellbore schematics, per-well histories, block chronology).

## What the deck covers

Thirteen sections, in the order Kevin asked for them: block overview and chronology; well-by-well histories and wellbore schematics; pressure history; production summary; fluid analysis; rock analysis and the TEC-10 core; geology with regional context; geophysics; reserves; accounting since Tonalli took over; crude marketing; operations; and the decisions and gap register the incoming operator inherits. Every slide carries a notes-page line naming its sources.

## Sources beyond the repository

Four agent notes in `data/processed/deck_notes/` (fluids/rock/core, geology/geophysics, wells/operations/reserves, accounting) summarise the raw files already in `data/raw/` and 60-odd Drive files read for this deck through the connector's text rendering. `data/processed/deck_notes/drive_reads_notes.md` lists each Drive file with its id and the facts taken from it; the ones that mattered most:

- PEMEX final well reports for TEC-5 and TEC-6 (1956) and estados mecánicos for TEC-5, 7, 9 and 101 (2006 updates): casing strings, tops, initial tests, the first structural interpretation.
- Halliburton post-operative cementing reports for TEC-10 (13 3/8", 9 5/8", 7", 4 1/2" liner) and TEC-11 (7"); the Latina injectivity test on TEC-10's lower perforations; Tonalli estados mecánicos for TEC-2, TEC-7 (2019 injection string) and TEC-11 (2022 composite plug); the TEC-11 temporary-abandonment notice.
- The 2018 "Tecolutla 3D Seismic Interpretation Summary", the May-2017 Plan de Evaluación (English rendering), the GLJ YE2019 top-El-Abra map, the Stratascan petrography report.
- Tonalli's letters to PEMEX of 8 Feb and 21 Jul 2022 (the shut-in and the transition-programme approval), the 2022 share-transaction memo (Idesa out, Jaguar in), the 2024–25 abandonment-trust sheet.
- Accounting: the 2019 budget-vs-actual workbook, the Dec-2022 cash reconciliation, the Sep-2024 cash-call summary, the H1-2024 cash-flow statement, the Sep-2020 operating-cost sheet and the Sep-2019 directors' memo; the YE2021 GLJ reserve report draft; the SASISOPA inventory; the PEMEX pricing template and the transport-system specification.

Two of the accounting renderings were cut by the connector at about 1 MB, so 2020–21 actuals and the 2022 AP/AR/VAT sheets are absent; the 39 MB 2021 G&A workbook could not be rendered at all. The PEMEX survey scans of 1957/1972/1991 carry no text. None of these Drive files were pulled into `data/raw/` (they were read, not downloaded), so they are not in `data/manifest.csv`; their ids are in the notes.

## New gaps raised by the deck

G-54 TEC-2 and TEC-3 casing records; G-55 the seismic package (volumes, Petrel project, velocity model, grids) is not in the repository; G-56 accounting actuals for 2020–21 and 2023 and the unreadable 2021 G&A file; G-57 TEC-7 injection volumes, pressures and the current state of the 2019 injection string.

## Reproduce

```
.venv/bin/python src/block_deck_figures.py
.venv/bin/python src/build_block_deck.py
```
