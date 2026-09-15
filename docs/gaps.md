# Gaps and provenance flags

Anything unreadable, missing, unsubstantiated or inconsistent is logged here rather than smoothed over. Entries are dated and kept when resolved (status updated), so the log is an audit trail.

| # | Date | Item | Status |
|---|---|---|---|
| G-01 | 2026-09-15 | `Tecolutla_Field_History_and_TEC12_Review.md` (v3) is not in this repo and a title search of the shared drive returns nothing. Kevin is supplying it separately. Task 10 cannot start until it is in `docs/`. | Open |
| G-02 | 2026-09-15 | `Eduardo's Comments to Drilling Cost Estimate.docx` (reported as title-only) is not in the TEC-12 Drill folder or its `OLD` subfolder. Its Drive ID is unknown. | Open |
| G-03 | 2026-09-15 | `2023-09-29 Tec-12 Economics.xlsm` and the Aug 2020 economic model both carry a Drive modifiedTime of 18 Aug 2025, well after the dates in their names. Confirm with Kevin whether content changed or whether this is a re-save/upload artefact. Internal workbook metadata (docProps/core.xml) will be checked on pull. | Open |
| G-04 | 2026-09-15 | `Tecolutla Type Curve.xlsx` exists twice with different IDs, sizes and dates (TEC-12 Drill, 3 Mar 2021, 146,818 B; Appraisal Plan, 15 Mar 2022, 139,055 B). Both pulled; to be diffed in task 6. | Open |
| G-05 | 2026-09-15 | Petrophysics, Pressures and Fluid Analyzes folders, the Pressure Summary workbook and the three Geology CSVs were not visible in the top-level listing of the Geology folder. The IDs from the kickoff are used directly; their parent folders will be recorded from the API on pull. | Open |
| G-06 | 2026-09-15 | `Tecolutla Production Tracking.xlsx` (to Dec 2022) was not visible in the top-level Development Plan listing. ID from the kickoff used directly. | Open |
| G-07 | 2026-09-15 | rclone cannot be installed in this environment (its download host is blocked by the session proxy). The Google Drive API is reachable, so the pull uses the Python client instead. | Resolved — no impact |

## Known data gaps carried in from the kickoff

- No production data pre-1960; none for 1965–1972.
- OOIP stated as 11.2 MMbbl (volumetrics) and 7.8 MMbbl (El Abra analogue table) in the same deck — task 7.
- AFE sheet: $5,000 internal arithmetic discrepancy, no currency label — task 8.
- Forecast basis differs by roughly a factor of two between Petrel Robertson (100 bbl/d base) and IFR (250 bbl/d; 345 mbbl type curve) — task 6.
