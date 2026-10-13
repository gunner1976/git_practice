# Casing Design Tool — MVP Plan (onshore, non-thermal)

## Goal
A deterministic, auditable casing design engine for onshore wells that an experienced
well engineer trusts on first use: every number traceable to an API TR 5C3 clause and to
the inputs that produced it.

## In scope (MVP)
- US oilfield units throughout.
- Vertical and directional wells (minimum-curvature trajectory, dogleg bending).
- Surface, intermediate, production strings (liners after MVP).
- Ratings per API TR 5C3: burst, collapse (4 regimes + biaxial axial correction),
  pipe body yield, triaxial VME with Lame stresses and bending.
- Load cases: pressure test, gas to surface, tubing leak, stimulation, full evacuation,
  cementing, lost returns, running + overpull.
- Pipe/grade/connection catalog in editable CSV.
- Optimizer: cheapest passing item per string.
- CLI with JSON well files; results exportable as JSON.

## Explicit non-goals (post-MVP)
- Thermal: temperature derating, APB, thermal cycling, wellhead growth.
- Deepwater / BSEE requirements.
- Kick tolerance with finite influx volume (we use the conservative gas-to-surface case).
- Reliability-based design, casing wear, buckling, premium connection envelopes.

## Architecture
```
casingdesign/
  ratings/   api5c3.py (pure functions, clause-referenced), triaxial.py
  catalog/   CSV data + Catalog/PipeSpec
  well.py    pydantic models: Trajectory, Formation, CasingString, Well
  loads/     load cases -> internal/external pressure profiles; axial profiles
  design/    evaluate_string (design factors), optimize_string
  cli.py
tests/       benchmark against published API tables; worked-example wells
```

## Validation strategy
1. Ratings pinned to published API 5CT performance tables (done, 9 items).
2. Hand calculations for the biaxial collapse correction (done).
3. Worked example well with expected pass/fail outcomes (done).
4. Next: side-by-side comparison against a StressCheck/WELLCAT run on the same well
   (needs access to one licensed run); add each discrepancy as a test.

## Roadmap after MVP
1. Web UI (FastAPI + plots of load vs rating vs depth, VME ellipse).
2. Sectional (tapered) strings and liners.
3. Kick tolerance load case; buckling; wear derating.
4. Temperature derating, then APB for thermal wells.
5. Report generator (PDF) for regulatory submission.
