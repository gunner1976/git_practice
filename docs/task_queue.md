# Task queue

Work in order. Commit after each. Status is updated here as tasks close.

| # | Task | Inputs | Outputs | Status |
|---|---|---|---|---|
| 0 | Repo scaffold, access plan, working set, review v3 read | — | this repo, `docs/access_plan.md`, `data/working_set.csv`, `docs/review_v3_reading_notes.md` | Done — 140 files pulled via connector; 10 large files await API credentials (G-13) |
| 1 | Parse the 2023 economics | `2023-09-29 Tec-12 Economics.xlsm` | `data/processed/econ_2023/`, `docs/01_econ_2023.md` | Done — parsed from cached values, pandas cross-check in place of LibreOffice (G-16); G-17..G-20 raised |
| 2 | Reconcile the nine Feb 2022 models (+ Aug 2020 predecessor, + 2023) | eleven `.xlsm` | `data/processed/econ_lineage/diff_matrix.md`, `figures/02_econ_model_lineage.png`, `docs/02_econ_lineage.md` | Done — 2023 structure recommended as base with capital, price and profile to be replaced (tasks 6, 8); G-21..G-26 raised |
| 3 | TEC-11 facies vs trajectory figure | mud log, directional survey | `figures/03_tec11_lateral_facies.png`, `data/processed/tec11/`, `docs/03_tec11_facies.md` | Done — lateral 720 m: 240 m grainstone-bearing (mixed textures only), 419 m mudstone-wackestone; G-27..G-29 |
| 4 | Production database | all production workbooks | `data/processed/tecolutla_production.parquet` + CSV, GOR anomaly note | Ready |
| 5 | Pressure and depletion | Pressure Summary, Pressures folder, PTA reports | tidy pressure dataset at 2,300 m datum, p vs Np figure, test of "original pressure" claim | Ready |
| 6 | Type curve and forecast reconciliation | task 4 output, Type Curve workbooks, Petrel Robertson PDF | single base case with uncertainty range | Blocked on 4 |
| 7 | Volumetrics | Petrel Robertson Volumetrics, El Abra analogues, well logs | 11.2 vs 7.8 MMbbl reconciliation, probabilistic case | Ready |
| 8 | AFE escalation | AFE workbook, TEC-11 actual costs | line-by-line AFE in USD and CAD, escalated | Ready |
| 9 | Log petrophysics | LAS files | correlation panel TEC-2/6/9/10/11 with inverted-GR flag | Ready |
| 10 | Assemble | all of the above + review v3 | extended review `.md`, presentation | Blocked on 1–9 |
