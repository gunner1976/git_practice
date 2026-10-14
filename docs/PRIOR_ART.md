# Prior art review — open-source casing / well-design code

Reviewed 2026-10-14 by pulling the sources (not just READMEs). Licences matter: we
may reuse *data* and *ideas* from everything below, but copy *code* only from
permissive (Apache/MIT) projects. Nothing here is a StressCheck/WELLCAT substitute.

| Project | What it is | Licence | Useful to us |
|---|---|---|---|
| [welleng](https://github.com/jonnymaserati/welleng) (v0.29) | Trajectory, ISCWSA error models, anti-collision, T&D, kick tolerance, Landmark EDM/COMPASS/.wbp and WITSML readers, API 5CT catalogue | Apache-2.0 | **Yes — data and import path** |
| [pwploads](https://github.com/pro-well-plan/pwploads) (v0.4.1) | Casing load cases (SI units), API collapse with axial correction, VME ellipse, plots | LGPL-3.0 | Ideas / cross-check only |
| [CasingCalculator](https://github.com/clgoodrich/CasingCalculator) | Script on welleng: MASP, cement volumes, DF from a SQLite pipe table | none stated | No |
| [digitalmodel #2201](https://github.com/vamseeachanta/digitalmodel/issues/2201) | Planned worn/corroded casing capacity per TR 5C3 | — | Watch |

## What we took from welleng (Apache-2.0, attributed in `catalog/data/sources.md`)
- **Pipe catalogue cross-check**: all 49 of our API 5CT items matched its independently
  transcribed table except one drift (9-5/8" 36#: 8.796 -> 8.765, fixed). Imported its
  22 additional sizes (now 71 items, incl. 6-5/8, 11-3/4, 18-5/8).
- **Collapse constants**: our A,B,C,F,G computed from yield reproduce its API TR 5C3
  Table 6/7 values to the published rounding (J55/L80/P110). Independent validation.
- **Coupling dimensions (5CT Tables E.27/E.28)**: exposed an error — we had used
  special-clearance BTC coupling ODs for 4-1/2..7" (fixed to regular W). Also shows API
  LTC couplings exist only up to 9-5/8" (and 20"), so LTC is no longer offered for
  10-3/4..18-5/8".
- **Premium connections**: welleng deliberately carries names only (VAM TOP, TenarisHydril
  Wedge, etc.) with performance fields null — same policy we adopted: vendor data is
  user-supplied, never fabricated.

## What we learned from pwploads (ideas only, LGPL)
Its load-case list is a useful completeness check against ours:
- Has, we have: running/overpull, green-cement pressure test, cementing, displacement to
  gas, gas kick (driller's method, Boyle expansion, bubble in casing x DP annulus),
  tubing leak with packer, stimulation, full/partial evacuation, drilling losses,
  pressure test, mud drop.
- Has, we lack: **depleted-zone external pressure** (mud level falls to balance a
  depleted zone — relevant to infill onshore wells), **DST partial evacuation**,
  **injection with influenced zone**, **ballooning** and **thermal axial loads** (we
  are non-thermal by scope, but ballooning is cheap and we should add it), **shock
  load** while running (a*v*A*sqrt(E*rho)), **drag** via a T&D model.
- Its kick model expands the bubble with Boyle's law and locates it in the annulus
  (casing ID x drillpipe OD); ours puts a fixed-volume bubble at the top of the casing.
  Ours is more conservative for burst; theirs is closer to what circulating out looks
  like. Worth offering both.
- Its bending-force term uses the classic 63 x DLS x OD x W form; we use E*(D/2)/R on
  stress, equivalent.
- Code quality: list comprehensions over numpy, several bugs (partial evacuation
  overwrites the list; depleted-zone loop assigns a scalar) — do not reuse.

## welleng pieces worth integrating later
1. **Landmark import**: `welleng.exchange.edm_stream.EDMReader` reads EDM/COMPASS exports
   (surveys, pore/frac/temperature gradients, cases, assemblies). That is the practical
   route to "import an existing StressCheck well" — our roadmap item.
2. **Kick tolerance**: a full NOGEPA-50 static formula plus a gas-migration engine; we
   could compute the *allowable* kick volume (KT) for a shoe depth, not just evaluate a
   given influx.
3. **Trajectory**: ISCWSA-grade survey handling and .wbp import would replace our
   minimum-curvature-only trajectory for real surveys.
4. **Tubing catalogue** (`tubing.json`) when we extend to tubing design.

## CasingCalculator — reviewed, rejected
Collapse load uses MD instead of TVD, dead-code Barlow, hard-coded 0.465 psi/ft pore
gradient, no API 5C3 formulas, no licence. Nothing to borrow.
