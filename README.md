# Tecolutla / TEC-12 handover package

Technical handover for the Tecolutla field (Contractual Area 24, Tampico-Misantla Basin, Veracruz), operated by Tonalli Energia (IFR JV), for the incoming operator's technical team.

Two deliverables:

1. Field history review — what the rock has done since 1956, on reconciled data.
2. TEC-12 new-drill justification — the remaining opportunity, with the evidence for and against.

This is a transparent, evidence-first package. Where sources disagree, both are shown.

## Layout

| Path | Contents |
|---|---|
| `data/raw/` | Files pulled from the `International Frontier` shared drive. **Immutable. Never edit.** Git-ignored; audited by `data/manifest.csv`. |
| `data/working_set.csv` | The list of drive file/folder IDs to pull, with observed size and modified date. |
| `data/manifest.csv` | File ID, path, size, modified date, SHA256 of every raw file pulled. |
| `data/processed/` | Tidy derived datasets (parquet + CSV). |
| `src/` | Python modules: drive pull, citation helper, parsers, analyses. |
| `notebooks/` | Exploration notebooks, one per task. |
| `figures/` | Output figures, one per analysis, named `NN_description.png`. |
| `docs/` | Access plan, gaps log, the extended review document, presentation source. |

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

LibreOffice (`soffice`) is required for the headless recalculation pass on `.xlsm` workbooks.

## Conventions

- **Currency**: CAD is the presentation default, USD shown alongside source figures. A source figure with unconfirmed currency is flagged, never converted.
- **Units**: stated on every axis and column. Depths labelled mMD / mTVD / mSS.
- **Provenance**: every derived number cites source file, sheet/cell or page (see `src/cite.py`).
- **Gaps**: anything unreadable, missing or unsubstantiated is logged in `docs/gaps.md`, not interpolated around.

## Task queue

See `docs/task_queue.md`. Work is committed after each task.


## Outputs by task (September 2026)

| Task | Note | Data | Figure |
|---|---|---|---|
| 1 | `docs/01_econ_2023.md` | `data/processed/econ_2023/` | — |
| 2 | `docs/02_econ_lineage.md` | `data/processed/econ_lineage/` | `figures/02_econ_model_lineage.png` |
| 3 | `docs/03_tec11_facies.md` | `data/processed/tec11/` | `figures/03_tec11_lateral_facies.png` |
| 4 | `docs/04_production_database.md` | `data/processed/tecolutla_production.parquet` (+ CSV, gaps, allocations) | `figures/04_production_history.png` |
| 5 | `docs/05_pressure.md` | `data/processed/pressure/` | `figures/05_pressure_depletion.png` |
| 6 | `docs/06_forecast.md` | `data/processed/forecast/` | `figures/06_type_curve_forecast.png` |
| 7 | `docs/07_volumetrics.md` | `data/processed/volumetrics/` | `figures/07_volumetrics.png` |
| 8 | `docs/08_afe.md` | `data/processed/afe/` | `figures/08_afe.png` |
| 9 | `docs/09_log_panel.md` | `data/processed/petrophysics/` | `figures/09_log_panel.png` |
| 10 | `docs/10_econ_rebuild.md`, `docs/Tecolutla_Field_History_and_TEC12_Review_v4.md`, `docs/Tecolutla_TEC12_Handover.pptx` | `data/processed/econ_rebuild/` | `figures/10_econ_rebuild.png` |
| 11 (OCR) | `docs/11_ocr.md` | `data/processed/pressure/ocr/`, `data/processed/fluids/ocr/` | — |
| 12 (large files) | `docs/12_drive_large_files.md` | `data/processed/drive_text/`, `data/processed/tec10/`, `data/processed/welltest/`, `data/processed/pressure/tec2_2018/` | — |
| 13 (CNH filings, GIS, CMI) | `docs/13_cnh_filings_gis_cmi.md` | `data/processed/cnh/`, `data/processed/petrophysics/tec10_cmi_*.csv`, `data/raw/cnh_gis/` | `figures/13_cnh_polygon.png`, `figures/14_cmi_fractures.png` |

Gap register: `docs/gaps.md`. Rerun everything with the scripts in `src/` in task order; each script reads only `data/raw/` and earlier `data/processed/` outputs.

## Large Drive files (text route)

The connector refuses raw downloads above roughly 7–10 MB (G-13), but its `read_file_content` call returns a text rendering of any file the account can see. The ten large files (Work Program, GLJ YE2020 detail, core report, mud-log reports, masterlog, CMI image, two 2018 gauge workbooks, two decks) were read that way on 15 Sep 2026; the renderings live in `data/processed/drive_text/` and are listed in `data/manifest.csv` with `source_kind = drive-connector-text`. Figures and images are not captured and the two gauge workbooks are truncated at about 1 MB (G-52), so the binaries still belong in `data/raw/` when a Drive API pull (`src/pull_drive.py`) or a manual download is possible. Parsers on the renderings: `src/tec10_mudlog.py`, `src/welltest_2018_extract.py`, `src/tec2_2018_survey.py`. Small binaries (the CNH shapefile) download normally. GIS and image-log scripts: `src/cnh_polygon.py` (pyshp, pyproj), `src/cmi_fractures.py`.

## OCR

Scanned PDFs (the 18 PEMEX pressure forms, the 1956-2019 fluid analyses) have no text layer. Two engines are set up: Tesseract 5 with the Spanish pack (`apt-get install tesseract-ocr tesseract-ocr-spa`) and RapidOCR (pip, ONNX, no system dependency). `src/ocr_pressure_scans.py` and `src/ocr_fluids.py` render pages at 300 dpi with PyMuPDF, run both engines, keep the raw text under `data/processed/*/ocr/`, and parse the numbers that matter. RapidOCR reads the typewritten PEMEX forms reliably; Tesseract is kept as the cross-check. OCR output is always compared against a transcription or read by eye before it changes a dataset.
