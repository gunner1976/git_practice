# Task queue

Work in order. Commit after each. Status is updated here as tasks close.

| # | Task | Inputs | Outputs | Status |
|---|---|---|---|---|
| 0 | Repo scaffold, access plan, working set | — | this repo, `docs/access_plan.md`, `data/working_set.csv` | Done — awaiting credentials |
| 1 | Parse the 2023 economics | `2023-09-29 Tec-12 Economics.xlsm` | `data/processed/econ_2023_*.csv`, `docs/01_econ_2023.md` | Blocked on pull |
| 2 | Reconcile the nine Feb 2022 models (+ Aug 2020 predecessor, + 2023) | ten `.xlsm` | diff matrix, lineage chart, recommendation | Blocked on pull |
| 3 | TEC-11 facies vs trajectory figure | mud log, directional survey | `figures/03_tec11_lateral_facies.png`, metres in grainstone vs mud/wackestone | Blocked on pull |
| 4 | Production database | all production workbooks | `data/processed/tecolutla_production.parquet` + CSV, GOR anomaly note | Blocked on pull |
| 5 | Pressure and depletion | Pressure Summary, Pressures folder, PTA reports | tidy pressure dataset at 2,300 m datum, p vs Np figure, test of "original pressure" claim | Blocked on pull |
| 6 | Type curve and forecast reconciliation | task 4 output, Type Curve workbooks, Petrel Robertson PDF | single base case with uncertainty range | Blocked on 4 |
| 7 | Volumetrics | Petrel Robertson Volumetrics, El Abra analogues, well logs | 11.2 vs 7.8 MMbbl reconciliation, probabilistic case | Blocked on pull |
| 8 | AFE escalation | AFE workbook, TEC-11 actual costs | line-by-line AFE in USD and CAD, escalated | Blocked on pull |
| 9 | Log petrophysics | LAS files | correlation panel TEC-2/6/9/10/11 with inverted-GR flag | Blocked on pull |
| 10 | Assemble | all of the above + review v3 | extended review `.md`, presentation | Blocked on G-01 |
