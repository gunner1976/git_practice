# Task 9 — Log correlation panel on a subsea datum, GR polarity, and what the logs say about the TEC-12 target

Script: `src/log_panel.py`. Outputs: `data/processed/petrophysics/{TEC6,TEC2,TEC9,TEC10,TEC11}_logs_mss.csv` (curves with mSS), `TEC2_gr2019_mss.csv`, `TEC2_n2018_mss.csv`, `perforations_mss.csv`, `gr_polarity.csv`, `tec10_archie.csv`, `summary.json`, `figures/09_log_panel.png`.

## 1. What was used

| Well | File (`petrophysics/LAS/`) | Vintage | Curves | Depth handling |
|---|---|---|---|---|
| TEC-6 | `BLOQUE_TECOLUTLA_6_GR_NEUT_100_2335.LAS` | 1956 | GR (old scale 0.9–8), neutron counts | vertical, KB 6.0 m (header CSV) |
| TEC-2 | `Tecolutla 2_Original_OH_Logs.LAS` (2,290–2,372 mMD); `TECOLUTLA-2_GR_CCL_…2019.las`; `TECOLUTLA-2_NEUTRON_05-04-2018.las` | 1956 digitised 2018; 2019; 2018 | GR api, SP, SN, LN, NPHI; cased-hole GR (cps); neutron porosity (stops at 2,286 mMD, above the reservoir) | vertical, KB 4.0 (survey form 3.8) |
| TEC-9 | `TECOLUTLA-9_RESISTIVO_SONICO_NEUTRON_2345_2000_08MAY1973P.LAS` | 1973 | GR, neutron counts, ILD, SN, SP, DT, sonic porosity (sparse) | vertical, KB 5.0 |
| TEC-10 | `TECOLUTLA-10_LAS_2280.50m-2487.00m_02MAY2018.las` (+ CXD, dipolar sonic, Stoneley, CMI fracture-density files) | 2018 Weatherford | GR, limestone neutron and density porosity, PE, deep/medium induction | MD to TVDSS from the TEC_10 survey (85 stations), KB 6.13 |
| TEC-11 | `Tecolutla 11_LAS_GR_SST_3283 mMD.las` (LWD) | 2018 | GR, compressional sonic, TVD | LWD TVD minus KB 4.70; the hole is 61–90°, so 900 m of lateral collapse onto 90 m of the TVDSS axis |

Not used: TEC-3 and TEC-5 (1956, dry holes), TEC-101 (1972, squeezed), the TEC-10 cement bond log, the CMI dip and fracture products (fracture density available in `TECOLUTLA 10_CMI FRACTURE DENSITY…las`, 0–7 fractures per metre, not part of this panel). TEC-7 has no logs (G-14).

## 2. GR polarity: confirmed, field-wide

Spearman rank correlation of GR against a porosity indicator in the 2,280–2,380 mSS window (`gr_polarity.csv`):

| Well | Porosity indicator | ρ(GR, porosity) | ρ(GR, log resistivity) |
|---|---|---|---|
| TEC-2 1956 | NPHI | +0.34 | +0.26 (long normal) |
| TEC-2 2018 cased hole (2,150–2,282 mSS) | NPRL | +0.40 | — |
| TEC-9 1973 | sonic porosity / −neutron counts | +0.49 / +0.65 | −0.77 (ILD) |
| TEC-10 2018 | NPRL | +0.28 | −0.19 (ILD) |
| TEC-11 2018 LWD | Wyllie sonic porosity | +0.18 | — |
| TEC-6 1956 | −neutron counts | −0.04 (no relation) | — |

In every well with a usable porosity curve, GR **rises** with porosity. The review's warning stands and should be stated in the handover in these terms: at Tecolutla a low, "clean" gamma ray marks the tight, recrystallised miliolid facies, and the porous intervals are the high-GR ones. Any GR-based shale volume or net-to-gross cut-off from a standard workflow will discard the reservoir. In TEC-9 and TEC-10 the high-GR porous intervals are also the **low-resistivity** ones, which is the subject of section 4.

## 3. Depths on one datum

| Item | mMD | mSS | Source |
|---|---|---|---|
| TEC-6 produced intervals | 2314–2316, 2324–2327, 2336–2338 | 2308–2310, 2318–2321, 2330–2332 | perforations CSV, KB 6.0 |
| TEC-6 bridge plug / top squeezed | 2303–2304 | 2297–2298 | same |
| TEC-2 active interval | 2307.4–2311 | 2303.4–2307 | same, KB 4.0 |
| TEC-9 produced interval | 2328–2333 | 2323–2328 | same, KB 5.0 |
| TEC-10 producing perforations | 2349.5–2350.5, 2351.5–2353 | **2314.3–2318** (survey) vs 2311.5–2315 (By Zone / review) | survey CSV; G-46 closed on the survey basis |
| TEC-10 upper zone (review: "high-porosity reef margin") | ~2302–2346 | 2270–2311 | logs |
| TEC-12 target window | — | 2294–2311 | review v3 §6.1 |
| TEC-11 lateral | 2563–3283 | 2305–2331 | task 3 |

The TEC-10 survey puts the top perforation 2.8 m deeper subsea than the figure carried in the By Zone sheet and the review, so "16.5 m higher" becomes about 20 m on the survey basis (G-46). All PEMEX production and TEC-10's production came from **2,303 to 2,332 mSS**; nothing in the field has ever been produced from the 2,294–2,311 mSS window except the top 4 m of TEC-2's active interval.

## 4. The TEC-12 target window as seen by the two wells with resistivity

TEC-10 (2018), Archie with a = 1, m = 2, n = 2, Rw 0.054 ohm·m at 98.6 °C (PEMEX 45,000 ppm, 0.075 at 65 °C), porosity = mean of limestone neutron and density porosity; uncalibrated to core (`tec10_archie.csv`):

| mSS | mMD | GR | φ | ILD ohm·m (median) | Archie Sw | m with φ ≥ 6 % | m with φ ≥ 6 % and Sw ≤ 50 % |
|---|---|---|---|---|---|---|---|
| 2270–2294 | 2303–2328 | 91 | 0.107 | 4.1 | 0.99 | 25.2 | 0.0 |
| **2294–2311 (TEC-12 window)** | 2328–2346 | 83 | 0.089 | 5.2 | 0.99 | 16.5 | **0.0** |
| 2311–2320 (TEC-10 perforations) | 2346–2356 | 44 | 0.054 | 30 | 0.79 | 4.1 | 2.2 |
| 2320–2340 | 2356–2377 | 65 | 0.053 | 17 | 0.91 | 6.6 | 1.0 |
| 2340–2360 | 2377–2398 | 71 | 0.026 | 51 | 0.96 | 0.2 | 0.0 |
| 2360–2450 | 2398–2490 | 84 | 0.03 | 40–54 | 0.95 | 3.2 | 0.9 |

Three things are visible on the panel without any Archie assumptions:

1. In TEC-10 the porous upper zone (2,270–2,311 mSS, 9–11 % porosity, 41 m thick) reads **4–5 ohm·m**, and resistivity jumps to 15–50 ohm·m exactly where porosity drops below 6 % at ~2,311 mSS. Tonalli perforated the base of that transition (2,314–2,318 mSS) and the well produces at 30–40 % oil cut with 55 % water saturation in the IHS test model.
2. TEC-9 (1973) shows the same pattern: ILD 3–5 ohm·m from 2,270 to ~2,308 mSS, rising to ~40 ohm·m below, and its 353 kbbl came from 2,323–2,328 mSS in the high-resistivity section.
3. In TEC-10 the upper zone's neutron porosity exceeds its density porosity by 5–6 porosity units and the PE is 3.8 against 5.0 below: the response of an argillaceous or dolomitic interval, not of a clean limestone.

Two readings are possible, and the logs alone do not separate them:

- **Free water**: the porous upper zone is water-bearing at TEC-10 and TEC-9, the oil column is the lower-porosity, higher-resistivity rock below ~2,310 mSS, and the field's high water cuts and the aquifer signature (task 5) follow. On this reading the TEC-12 window at 2,294–2,311 mSS is above the oil, not above the water.
- **Clay-bound water**: the upper zone is an argillaceous carbonate whose low resistivity and high GR come from clay, its effective porosity is much lower than the 9–11 % total, and a shaly-carbonate model (not Archie) would return hydrocarbon in the better streaks. On this reading the window is a poorer, thinner reservoir than "15 m of net pay", not a water zone.

Either way, the premise that the window is "un-perforated crestal El Abra pay that PEMEX logged" is not supported by the resistivity of the two wells that have it. PEMEX did not perforate it in TEC-6 (bridge plug at 2,297 mSS instead), TEC-9 or TEC-2 above 2,303 mSS, and Tonalli did not perforate it in TEC-10 after logging it with a modern suite. The TEC-2 1956 long normal reads 100–900 ohm·m through the same depths, but a 64-inch normal in a 1956 hole is not comparable to an induction log and the digitised curve carries no calibration.

## 5. What this means for the handover

1. Present the panel with the GR-polarity result and the resistivity contrast at ~2,310 mSS in TEC-9 and TEC-10. It is the single most important technical uncertainty on TEC-12 and it is visible in data the incoming operator will look at first.
2. Commission a proper petrophysical evaluation of TEC-10 before the well is sanctioned: core calibration from the TEC-10 core report (`Tecolutla-10 Core and Sample Descriptions/Core/`, 2,352 m plug data), a shaly-carbonate saturation model, and a check of Rw against the 2018 water analyses. The Archie pass here is a screening calculation with book parameters.
3. If the free-water reading holds, the TEC-12 target should move down to the 2,311–2,332 mSS interval that has produced in every well, which changes the "higher on structure" argument to a "between two producers, same interval" argument. That interval is 4–9 m thick at TEC-10 and TEC-6 with 5–6 % porosity, consistent with the task-7 finding that porosity and net-to-gross, not area, decide the volumes.
4. The CMI fracture-density log (0–7 fractures per metre over 2,296–2,488 mMD) and the dipole sonic anisotropy in TEC-10 have not been examined here; they bear on the karst/fracture risk in the Petrel Robertson note and should be part of the same evaluation. The image log is a Weatherford CMI, not an FMI (G-09).

## 6. Caveats

- Old logs (1956, 1973) are digitised with unknown scales: GR values for TEC-6 are 0.9–8.2 units, neutron curves are counts; only their shapes are used.
- TEC-2's 2018 neutron log stopped at 2,286 mMD, 21 m above the perforations, so TEC-2 has no modern porosity in the reservoir.
- TEC-10 KB: 6.13 m in the survey CSV and header CSV, 5.13 m in the masterlog and cement bond log headers. Decision of 16 Sep 2026 (Kevin Gunning): the directional-survey KB 6.13 m is the package basis for every TEC-10 subsea depth (G-46 resolved).
- Archie inputs (Rw, m, n) are book values; the TEC-10 water analyses in `fluid_analyses/` were not read.
