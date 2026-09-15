# Task 5 — Pressure history at a common datum and the depletion picture

Script: `src/pressure_db.py`. Outputs: `data/processed/pressure/tecolutla_pressures.csv` (21 surveys), `pressure_summary.json`, `figures/05_pressure_depletion.png`.

Sources:
- `geology/Tecolutla Pressure Summary.xlsx` sheet `all`: IFR's transcription of 20 PEMEX bottom-hole pressure surveys 1956–1998 plus the Tonalli March 2018 static gradient, with IFR's own datum correction to 2,300 m below KB.
- `pressures/*.pdf`: the 18 PEMEX survey forms. They are image scans with no text layer and no OCR is available in this environment; four were read visually against the transcription (TEC-2 24 May 1956, TEC-2 5 Dec 1964, TEC-6 18 Oct 1971, TEC-7 6 Oct 1998) and agree to the last digit.
- `development_plan/Tecolutla 2 Final Report (IHS PTA) Spanish.pdf` and `Tecolutla 10 Final Report (IHS PTA) Spanish.pdf`: 2018 build-up interpretations (WellTest, IHS, June and October 2018).
- Cumulative oil at each survey date from task 4 (`tecolutla_field_monthly.csv`, plus the 0.43 MMbbl of wellfile block totals that predate the 1960 series).

## 1. Datum and corrections

- Datum used here: **2,300 m subsea**. The IFR summary uses 2,300 m below KB, which is a different level in each well (KB 3.8 m TEC-2, 4.8 m TEC-7, 7.1 m TEC-10, TEC-6 not recorded, assumed 4.0 m). The two bases differ by 0.04–0.07 MPa; small, but a handover table must say which it uses (G-35).
- Gauge-to-datum correction at 10.5 kPa/m, the reservoir gradient IHS derived from the 2018 build-ups. All gauges sit within 35 m of the datum, so the choice of gradient (oil 8.7 versus 10.5 kPa/m) moves any value by at most 0.06 MPa; both are in the CSV.
- Nothing is interpolated between surveys. Each row keeps the gauge depth, the raw reading, the shut-in time and the source.

## 2. The dataset

| Date | Well | Kind | Shut-in | Gauge mSS | p at gauge kPa | **p at 2,300 mSS MPa** | Use |
|---|---|---|---|---|---|---|---|
| 1956-05-24 | TEC-2 | static gradient | 2 h 45 min | 2,306 | 24,713 (252.0 kg/cm²) | 24.65 | reference only: not a stabilised static, but the well was new |
| 1964-12-02 | TEC-6 | flowing (9 m³/d) | — | 2,333 | 18,989 | 18.64 | flowing, excluded |
| 1964-12-05 | TEC-2 | static gradient | 75 d | 2,331 | 24,683 | 24.36 | yes |
| 1964-12-08 | TEC-2 | static gradient | 78 d | 2,331 | 24,713 | 24.39 | yes |
| 1964-12-08 | TEC-7 | static gradient | 95 d | 2,305 | 24,713 | 24.66 | yes |
| 1971-08-06 → 10-18 | TEC-6 | static gradients, 11 runs | 4 → 74 d | 2,333 | 23,565 → 24,674 | 23.22 → 24.33 | yes; a 74-day build-up |
| 1973-06-04 | TEC-6 | flowing before shut-in | — | 2,311 | 22,771 | 22.66 | flowing, excluded |
| 1998-10-06 | TEC-7 | static gradient | not stated | 2,320 | 24,736 (252.2 kg/cm²) | 24.52 | yes |
| 2018-03-27 | TEC-2 | static gradient | 2 years+ (field shut in since Jan 2016) | 2,246 (gauge stopped above perfs) | 23,591 | 24.16 | yes, extrapolated 54 m at a water gradient by IFR |
| 2018-05-30 | TEC-2 | build-up p* | 13 d | 2,305 | 24,190 | 24.14 | yes; IHS model extrapolation, last point 24,187 still rising |
| 2018-08-31 | TEC-10 | build-up p* | 25 d | 2,315 | 24,304 | 24.15 | yes; IHS model extrapolation |

## 3. What the data say

1. **Initial pressure.** The number in circulation, 24.7 MPa (PEMEX "252 kg/cm²"), is the 24 May 1956 TEC-2 reading after 2 h 45 min shut-in, 252.0 kg/cm² at 2,310 mKB. It is not a stabilised static, but the well had produced almost nothing, so it is a fair initial. At 2,300 mSS it is 24.65 MPa (3,575 psia). The 1964 surveys on TEC-2 and TEC-7 after 75–95 days, at 24.36–24.66 MPa, bracket the same value after 0.58 MMbbl of production.
2. **1971–1998.** TEC-6 after 74 days: 24.33 MPa (0.74 MMbbl). TEC-7 in 1998: 24.52 MPa (1.78 MMbbl). No measurable trend within the ±0.15 MPa scatter of the surveys.
3. **2018.** Three independent measurements in three wells agree at **24.14–24.16 MPa at 2,300 mSS** (3,500–3,505 psia) after 2.06 MMbbl including the wellfile allocations (1.63 MMbbl recorded). IHS's own datum table gives the same result: TEC-2 24,190 kPa at 2,305 mSS and TEC-10 24,304 kPa at 2,315 mSS lie on one 10.5 kPa/m gradient.
4. **Depletion 1956 to 2018: 0.5 MPa, 2 % of initial** (24.65 → 24.15 MPa), over roughly 1.9–2.1 MMbbl of oil and 0.65 MMbbl of recorded water. Rock and fluid expansion alone (N 11.2 MMbbl, ct 1.98 × 10⁻⁶ /kPa from the IHS TEC-2 report, Δp 500 kPa) would supply about 11 kbbl, so more than 99 % of the voidage has been replaced by water influx. That is the quantitative form of the review's "strong aquifer support".
5. **Short shut-ins understate pressure.** The 1971 TEC-6 series climbs from 23.22 MPa at 4 days to 24.33 MPa at 74 days and is still not flat at 40 days (24.43) versus 74 days (24.33, within scatter). The 2018 build-ups (13 and 25 days) had to be model-extrapolated for the same reason. Any future static survey after the 2020–2023 shut-in should be read as a multi-year build-up, which is the review's recommendation 8, and should be reported at 2,300 mSS with the gauge depth and gradient stated.
6. **Both 2018 build-ups needed a constant-pressure boundary** to match late-time data (TEC-2 at 700 m, TEC-10 at 195 m from the well), which is the aquifer seen in the transient. TEC-10 also required a no-flow boundary at 125 m, consistent with the facies edge that TEC-11 found to the north-west.

## 4. Test of the review's claim

The review says "reservoir pressure is reported at original 1956 pressure of 24.7 MPa" and "datum pressures at 2,300 m cluster tightly at 23.2–24.7 MPa from 1956 to 2018". On this dataset:

- The 23.2 MPa low end is the 4-day point of the 1971 TEC-6 build-up, not a reservoir pressure. Excluding surveys shorter than a week, the static range is 24.14–24.66 MPa.
- "At original pressure" should be written as **"within 0.5 MPa (2 %) of the 1956 initial after ~2 MMbbl"**. The difference is measurable and consistent across three wells in 2018, and it is what a strong but finite aquifer looks like. The conclusion (water, not pressure, limits recovery) stands.
- The PVT quoted by PEMEX (Pb 132 kg/cm² = 12.9 MPa) and by IFR (Pb 2,849 psi = 19.6 MPa) are both far below the 24.1 MPa reservoir pressure, so the reservoir is undersaturated on either basis and the produced-GOR behaviour in task 4 is not a reservoir-wide gas liberation. Which Pb is right still matters for TEC-12 inflow at low flowing pressure (G-31): TEC-2 flowed at 16.8 MPa and TEC-10 at 21.3 MPa bottom-hole in 2018.

## 5. Other numbers worth carrying forward from the IHS reports

| | TEC-2 (May 2018) | TEC-10 (Aug 2018) |
|---|---|---|
| Interval | 2,307–2,311 mKB | 2,349.5–2,350.5 and 2,351.5–2,353.0 mKB MD (2,322.1 mTVD reference) |
| kh/μ | 5,838 mD·m/mPa·s | 519 mD·m/mPa·s |
| k (oil), h | 50 mD, 8 m (assumed h) | 18 mD, 13.2 m (assumed h) |
| Skin | +196 (flow efficiency 0.05) | +4.9 (flow efficiency 0.63) |
| Last flow | 50 bbl/d oil, 453 bbl/d water at 16.8 MPa BHFP | 196 bbl/d oil, 114 bbl/d water at 21.3 MPa BHFP |
| Fluid used | 28.0 °API, μ 0.74 cp, Bo 1.283, Rs 96.4 m³/m³ (541 scf/bbl), Vasquez-Beggs | 28.2 °API, μ 0.72 cp, Bo 1.296, Rs 101.6 m³/m³ (570 scf/bbl) |
| Reservoir temperature | 101.0 °C | 98.6 °C |

TEC-2's skin of +196 is the well, not the rock: a workover candidate, and a warning that PEMEX-era per-well rates say little about the reservoir. TEC-10's 18 mD over 13.2 m with a boundary at 125 m is the only modern reservoir-quality measurement in the field and is the right anchor for TEC-12's inflow.
