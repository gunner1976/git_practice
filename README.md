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
