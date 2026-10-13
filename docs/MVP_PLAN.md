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
- Load cases: pressure test, gas to surface or kick tolerance (finite influx, frac and
  BOP capped), tubing leak, stimulation, full evacuation, cementing, lost returns,
  running + overpull.
- Pipe/grade/connection catalog in editable CSV; API 5C3 joint strength for STC/LTC/BTC.
- Static-temperature yield derating (linear, configurable slope).
- Optimizer: cheapest passing uniform pipe per string, and cheapest tapered design
  (section length and count limits, exact composite re-check).
- CLI with JSON well files; web UI with form editor, plots and design envelope.

## Explicit non-goals (post-MVP)
- Thermal: transient temperatures, APB, thermal cycling, wellhead growth.
- Deepwater / BSEE requirements.
- Reliability-based design, casing wear, buckling, premium connection envelopes.
- Liners and tiebacks.

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
1. Verify round-thread engaged lengths against API 5B; load vendor premium connection data.
2. Liners/tiebacks; buckling; casing wear derating.
3. Service-life axial changes (ballooning), then APB for thermal wells.
4. Report generator (PDF) for regulatory submission; StressCheck import.
5. Side-by-side validation against a licensed StressCheck/WELLCAT run.
