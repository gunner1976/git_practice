# 20 — Seismic: what the PSDM and the PEMEX PSTM say about TEC-12

Date: 2026-10-26. The three Tecolutla seismic volumes on the Drive were too large for the connector. They were read in Google Colab with `colab/tecolutla_seismic_extract.ipynb` (run on the data owner's account, 2026-10-26 16:02–16:06 UTC, 0 errors; every source and output checksummed in `data/raw/colab_out/manifest.json`). The field-area windows were then analysed here with `src/seismic_colab_analysis.py`. Outputs: `data/processed/seismic/` (`seismic_ties.csv`, `seismic_loo.csv`, `seismic_summary.json`, `pstm_reef_top.csv`, `psdm_reef_top.csv`), `figures/26_seismic_sections.png`, `figures/27_seismic_structure_maps.png`.

## 1. The volumes

| Volume | What the files say | Window extracted |
|---|---|---|
| `Tec_PSDM2019.zgy` (DMI PSDM, 710 MB) | 426 inlines (220–645) × 275 crosslines × 4,201 samples; z from −280 at 2 m; corners in UTM 14N; 8-bit storage; no z unit or datum recorded | 173 × 174 traces at 25 m, z 1,900–2,800 |
| `554702 … MIGPRESTM SFSG` (PEMEX/PGS PSTM, raw, 1.07 GB) | Petrel 2013 export, 5 May 2015; UTM 14 WGS84; inlines 3970–4260, crosslines 12135–12392; 75,078 traces; 2 ms to 7 s; IEEE float; inline in bytes 189 (and 5/9), crossline in bytes 21 (and 193) | 14,880 traces, 1,200–2,400 ms |
| `554703 … CFCG` (same, filtered/gained) | identical geometry | same window (trace headers byte-identical to 554702) |

The textual headers fill the "no EBCDIC headers or survey geometry" part of G-55. The PSDM z axis is read as metres below sea level: the reef reflectors sit at 2,250–2,350 where the well tops are 2,294–2,334 mSS. Dominant wavelength at reservoir level is about 67 m, so the PSDM cannot resolve vertical differences much under 15–20 m.

## 2. Method

In each volume the reef-top trough–peak pair was auto-tracked from a seed at the TEC-12 bottom hole, within the field (where the Jan 2019 grid is shallower than −2,345 m). The tracker takes the strongest same-sign extremum within ±4 ms (PSTM) or ±2 m (PSDM) of the neighbouring trace. The tracked events were then tied to the eight vertical-well tops. For the PSTM, each well gives an average velocity to the peak (top ÷ half the peak time). The velocity at any point is the inverse-distance mean of the wells, and leave-one-out over the wells measures the depth-prediction error. Polarity is not stated in the files; "peak" and "trough" refer to sample sign only.

## 3. Results

**PEMEX PSTM: supports TEC-12 as the crest.**
- The reef-top pair tracks over 95–100 % of the field. Peak time correlates with the well tops (r = +0.69).
- The time high is on TEC-6, TEC-12, TEC-9 and TEC-10 (figure 27, middle panel), which is where the well tops are highest.
- At the TEC-12 bottom hole the peak is at 1,565.5 ms. Only TEC-6 (1,562.1 ms, 270 m west) is earlier among the wells; TEC-9 is 1,568.5, TEC-10 1,574.3, TEC-2 1,577.4, TEC-7 1,581.1 and TEC-101 1,581.8 ms. Only 3 % of tracked field traces are earlier than TEC-12.
- Average velocities to the peak are consistent at the crestal wells: TEC-6 2,937, TEC-9 2,928, TEC-10 2,934 m/s; TEC-2 2,918, TEC-7 2,914, TEC-101 2,951.
- **Depth at TEC-12 from the PSTM: −2,293 mSS** (inverse-distance velocity 2,929 m/s). Using the TEC-9 and TEC-10 velocities gives −2,291.5 to −2,296.8. The Jan 2019 grid gives −2,289.4 and the drilling prognosis −2,296.
- Leave-one-out error is ±2.5–2.7 m at the three crestal wells around TEC-12 (TEC-6, TEC-9, TEC-10) and 13–18 m at the flank and northern wells (TEC-2, TEC-7, TEC-101). TEC-12 sits among the crestal wells, so its estimate should carry roughly ±3–5 m.
- **The Jan 2019 grid's northern culmination (−2,284.4 at X 707,351 Y 2,263,169) is not high on the PSTM.** Its trough is 20.6 ms later than at TEC-12 and its peak about 41 ms later (the peak may skip a cycle there). That is roughly 30–60 m deeper at crestal velocities.

**DMI PSDM: does not resolve the El Abra top.**
- The strongest reef-level reflectors run continuously at 2,280–2,320 m but are highest along the west (TEC-101, TEC-2, the northern area) and lower at TEC-9 and TEC-12 (figure 27, right panel). That is the reverse of the log tops: tracked peak depth vs well tops gives r = −0.48.
- The log tops sit at different positions relative to the reflectors: at the reflector at TEC-9 and TEC-6, about 20 m below at TEC-10, about 45 m below at TEC-101.
- This fits the XRD result that a Tantoyuca marl overlies the El Abra and thickens off the crest (G-47). The PSDM images the top of the composite carbonate package, not the El Abra top, and its depth conversion may also carry lateral velocity error. Jamiesco reported a −45° phase difference on this stack at TEC-10.
- The Jan 2019 grid honours the well tops (±2 m). Its bulls-eye lows at TEC-101 and TEC-10 come from the tops, not from a reflector. Its northern high appears to follow the PSDM reflector, which the PEMEX PSTM does not support.
- Between TEC-6 and TEC-101 both volumes show a disrupted zone about 150–250 m wide. It may be a fault, a karst feature or a processing artefact; not interpreted here.

## 4. What this means for the presentation

1. The structural case for TEC-12 is now supported independently. The PEMEX PSTM, processed years before any Tonalli interpretation, puts TEC-12 at the top of the southern culmination. With the crestal wells' velocities it gives −2,293 ± ~4 mSS, which brackets the grid (−2,289) and the prognosis (−2,296). TEC-12 is about 3 m higher than TEC-9 and 17 m higher than TEC-10 at El Abra level.
2. The seismic cannot tell whether El Abra at TEC-12 starts at the top of the carbonate package (like TEC-9) or 20 m lower (like TEC-10). That is a stratigraphic question, and the well is the test (G-47).
3. Drop the "undrilled northern culmination" as a follow-up target until it is re-examined. It is a feature of the PSDM-based grid, and the PEMEX PSTM puts it 30–60 m deeper.
4. Do not show the PSDM as confirming the crest. If John asks about the 2018–19 reprocessing, the answer is that the PSDM is visually better but does not map the El Abra top at this resolution; the legacy PSTM ties the wells better.

## 5. Limits

- The PSDM depth axis unit and datum are inferred, not recorded.
- Auto-tracking used one event pair; no manual interpretation, no well-synthetic tie, no phase correction.
- The velocity model is the six-well average-velocity field, not a seismic velocity cube. The DMI and Earth Signal velocity volumes are still missing (G-55).
- The PSTM window is the PEMEX cut of 2015, not the Earth Signal 2018 reprocessing.
