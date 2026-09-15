# 14. Water-saturation sensitivity for the TEC-12 window at TEC-10 (G-47)

Script `src/sw_sensitivity.py`; outputs `data/processed/petrophysics/tec10_sw_sensitivity_zones.csv` (72 cases × 6 zones), `tec10_sw_sensitivity_curves.csv`, `figures/15_sw_sensitivity.png`. Input is the TEC-10 2018 triple-combo already processed in task 9 (`TEC10_logs_mss.csv`), cased hole above 2,245 mSS excluded.

## 1. Why a sensitivity and not an answer

There is no core electrical measurement (m, n), no water analysis (Rw) and no core in the window (task 12 §5). Book-value Archie in task 9 gave Sw ≈ 1 in the window, but it also gives Sw 0.8–1.2 in the interval that produced 30 % oil, so the book parameters are wrong somewhere. This pass therefore fixes the unknowns by anchoring the model to the well's own behaviour and reports the window **relative to the perforated interval**:

| Anchor | Constraint | What it fixes |
|---|---|---|
| A | Sw = 1 below GLJ's lowest known oil, −2,374.2 mSS (2,374–2,447 mSS, ILD 45 ohm·m) | apparent Rw for each m and porosity basis |
| B | Sw = 0.55 in the perforated interval 2,311–2,320 mSS (IHS 2018 test-model saturation) | apparent Rw from a known producer |
| C | Rw 0.054 ohm·m, a = 1 (PEMEX 45,000 ppm at 98.6 °C) | book value, for reference |

Crossed with m ∈ {1.8, 2.0, 2.2}, n = 2, two porosity bases (mean of neutron and density limestone porosity, or density alone) and a Simandoux clay correction with Vsh from the neutron-density separation against a shale point of 20, 25 or 30 pu and Rsh 4 ohm·m.

Zone medians from the log: window Rt 5.2 ohm·m, φN 10.0 %, φD 6.7 % (separation +3.4 pu), GR 134, PE 3.86; perforated Rt 30, φN 1.4 %, φD 5.8 % (separation −3.7 pu), GR 79, PE 5.09; below LKO Rt 45, φN 0, φD 4.2 %, PE 5.11.

## 2. Result

| Porosity basis | Window Sw (anchors A / B / C, m = 2, clay 25 pu) | Perforated Sw | Window ÷ perforated, all m and clay cases |
|---|---|---|---|
| Density porosity | ≥ 1.5 / 1.18 / ≥ 1.5 | 0.97 / 0.62 / 0.81 | 1.4 – 1.9 |
| Mean neutron-density | 0.78 / 0.68 / 1.22 | 0.70 / 0.60 / 1.16 | 0.9 – 1.2 |

Across all 72 cases the window's median Sw ranges 0.57–1.5 (median 1.17); only one case puts it below 0.6. The clay correction moves the window by +0.05 to +0.10 only, because the neutron-density Vsh is 13 % and Rsh is close to Rt. The choice that matters is the porosity curve in the tight zones, where the neutron reads 0–1 % against 4–6 % on the density:

- **If the density porosity is right**, the aquifer below the LKO has Rwa ≈ 0.075 ohm·m (which is the PEMEX value at 65 °C), the perforated interval sits at Sw 0.6–1.0 depending on m, and the window is water-saturated on every anchor (Sw ≥ 1.1 even after a clay correction). Its 5 ohm·m is fully explained by 6–7 % of water-filled porosity plus clay.
- **If the neutron porosity is right** in the tight zones (2 % total), Rwa there is 0.02 ohm·m, and on that basis the window, the perforations and the aquifer all look alike: the window is no worse than the interval that produced (ratio 0.9–1.2) but no better, and the "aquifer" would itself be at Sw 0.6–0.7, which contradicts the LKO.

The core decides between the two. The three plugs from 2,352–2,353 mMD in the perforated interval measure 2.3, 6.7 and 7.6 % helium porosity with 2.70–2.71 g/cm³ grain density (task 12 §5); the density log through that interval reads 5.8 % and the neutron 1.4 %. The density curve matches the core; the neutron does not. The near-zero neutron in the produced interval is the signature of a light hydrocarbon (gas) effect, and it flips sign exactly at 2,311 mSS: below, density > neutron (hydrocarbon); above, in the window, neutron > density (clay-bound water). On the core-supported basis the window is water-bearing at TEC-10.

## 3. What this does and does not settle

- It settles that the logs, calibrated to the well's own aquifer and its own producing interval, do not support hydrocarbon in the window at the TEC-10 location under any Rw or m in the tested range, unless the density porosity is wrong by a factor of two where the core says it is right.
- It does not settle the window at the TEC-12 location, 175 m away and structurally 3–17 m higher. The same test at TEC-9, the closer offset, is in §5 and gives a different answer.
- It does not replace a core-calibrated evaluation: m in a recrystallised, partly vuggy grainstone can be well above 2.2, which would move every zone toward water, not the window toward oil.

## 5. The same test at TEC-9 (1973 logs), 118 m from the TEC-12 location

`src/sw_sensitivity_tec9.py`, `data/processed/petrophysics/tec9_sw_sensitivity_zones.csv`, `figures/16_tec9_rwa.png`. TEC-9 has no density log and no logged aquifer (the 1973 log stops at 2,345 mSS), so porosity comes from the sonic (Wyllie, limestone matrix) and the only anchor is the interval TEC-9 produced 353 kbbl from, 2,323–2,328 mSS (Sw 0.55 and 0.70 tried) plus the book Rw.

| Zone at TEC-9 | ILD ohm·m | Sonic φ | GR | Rt·φ² |
|---|---|---|---|---|
| TEC-12 window 2,294–2,311 mSS | 8.7 | 12.7 % (SPHI 13 %) | 41 | 0.140 |
| tight 2,311–2,320 | 83 | 3.0 % | 21 | 0.073 |
| produced 2,323–2,328 | 53 | 4.8 % | 17 | 0.123 |

At TEC-9 the window has six times lower resistivity than the produced interval but 2.6 times its sonic porosity, so on Archie its apparent water resistivity is the same or slightly higher: window ÷ produced Sw = 0.85–1.03 with the sonic porosity as logged, for any m in 1.8–2.2 and any anchor. That is the opposite of TEC-10 on the density basis. The catch is the sonic: in an argillaceous carbonate it over-reads porosity, and the window at TEC-9 has the less negative SP (−80 vs −110 mV) and higher GR that at Tecolutla go with the more porous, more argillaceous facies. Cutting the window's sonic porosity by 20 % moves the ratio to 1.1–1.3; by 40 % to 1.5–1.6, i.e. water. PEMEX's cuttings at TEC-9 called the window "cream miliolid grainstone" and the Work Program quoted 3–11 % porosity for it, so a real porosity difference between the two wells is plausible: TEC-10's window is 70 % mudstone-wackestone with 30 % shale in its cuttings (task 12 §6).

Two-well reading: at TEC-10 the window is water on the porosity the core supports; at TEC-9 it is at parity with a 353-kbbl producer if the 1973 sonic porosity is real, and water if a fifth or more of it is shale effect. The 1973 short normal reads below the induction in the window (5.3 vs 8.7 ohm·m), which in a water zone with fresh mud would be the other way round; it is a weak hint of hydrocarbon or of salty mud, and cannot be pushed further without the mud record.

## 4. Consequence for TEC-12

The base case for the well should be written on the produced interval, 2,311–2,332 mSS, not on the window; the window is upside if TEC-12 finds it cleaner (lower N-D separation, PE near 5) than TEC-10 did. A logging programme that can test this on the day is a triple-combo with PE, a neutron-density pair and, if the window looks different from TEC-10, a sidewall core or an MDT pressure/sample in it before the completion is designed. G-47 stays open as the decisive item, narrowed to: the window is water at TEC-10 on the core-supported porosity and at parity with the producer at TEC-9 on an uncorrected 1973 sonic; TEC-12, between the two, must log it with a density-neutron pair and PE and test it before the completion is designed. The section order here is 1, 2, 3, 5, 4 so that the TEC-9 evidence sits before the consequence.
