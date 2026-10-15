# Handoff to SurCana Nexus — casing string design tool

Repo: `gunner1976/git_practice`, branch `casing-design-mvp` (will become `master` once Kevin merges).
Purpose: become the basis of a Nexus casing design tool, used from the Planner (`hub/pages/planner`) `casing` module.

## What is here
| Path | What | Status |
|---|---|---|
| `casingdesign/ratings/` | API TR 5C3 burst / collapse (4 regimes, biaxial) / pipe-body yield / VME triaxial / API joint strength | E (formulas per API TR 5C3; constants computed, not tabulated) |
| `casingdesign/catalog/data/*.csv` + `sources.md` | 71 API 5CT pipes, grades incl. M-65/R-95/C-110, couplings per 5CT E.27/E.28 | E; round-thread engaged lengths calibrated to published joint strengths — flag for API 5B verification |
| `casingdesign/loads/` | Onshore load cases: pressure test, gas-to-surface, kick tolerance, tubing leak, stimulation, full evacuation, cementing, lost returns, running + overpull; liner → parent inheritance | E (onshore convention, non-thermal) |
| `casingdesign/design/` | Per-depth cheapest-passing optimiser, tapered strings, exact re-check, $/lb pricing, grade preferences | E |
| `casingdesign/io/edm.py` | Landmark EDM (StressCheck) import | E |
| `artifact/` | Browser build: `engine.js` (parity-verified vs Python on 2,280 specs), `ui.js`, `planner_mode.js` (hub glue), `build.py` | E |
| `tests/` | 82 unit tests (`python3 -m pytest -q`) | — |
| `docs/PRIOR_ART.md` | What was reverse-engineered / compared (welleng, published API tables) | — |

Everything in this repo is a **design aid**, not issued-for-execution: no number from it is external-facing without WF12.

## What Nexus should do with it (suggested ingest)
1. Clone to an intake folder (not into `srde_econ/`), e.g. `reference/tools_intake/casing_design/` or `tools/casing_design_src/`; run `/ingest` on `docs/`, `casingdesign/catalog/sources.md`, `NEXUS_HANDOFF.md`.
2. `drilling-engineer` reviews: load-case set vs SRDE hazards (lost-circulation corridor 690–820 m, no LOT/FIT anywhere → frac gradient is S until measured, polymer-injection pressure on the 7"), units (engine runs ft/psi/ppg; Planner is m/kPa), and the casing rulings already in `srde-drilling`.
3. `procurement-engineer`: the price index is an internal relative index, not a quote — replace with TCO-engine prices when available (zero-footprint rule applies; no vendor contact pre-award).
4. Verify before trusting: `python3 -m pytest -q` (82 pass), `python3 -m casingdesign.cli demo`, and `node --check artifact/engine.js`.
5. Then decide on the integration. A worked Phase 1 exists as **srde-nexus branch `casing-design-tool`** (hub page `hub/pages/casing-design/index.html` built from `artifact/`, `plan_modules` casing module built + `analysis` block, registry entry, Planner design-check line, 6 tests, plan in `hub/CASING_DESIGN_INTEGRATION.md`). Treat it as a proposal to review, amend or redo — not as merged doctrine.

## Build the hub page from this repo
```
python3 artifact/build.py            # writes artifact/casing_design.html (standalone) and artifact/hub_index.html (hub)
cp artifact/hub_index.html <nexus>/hub/pages/casing-design/index.html
```
`planner_mode.js` is inert unless served under `/pages/` with `#…pwell=<well id>` in the URL.

## Known assumptions (all tagged in the UI "Planner basis" panel)
- Fracture gradient 0.70 psi/ft (13.46 ppg EMW) — **S assumed**, no LOT/FIT held (hazard H10); publish asks before writing it.
- Pore pressure from the Planner overlay 7.9 kPa/m = 6.72 ppg EMW, constant with depth (T record / E reading).
- Mud weight max(pore + 0.5, 8.6) ppg on every string — planning default, S.
- Temperature 18 °C + 0.031 °C/m from the Planner overlay, S.
