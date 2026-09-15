# Task 3 — TEC-11 lateral: mud-log facies posted on the directional survey

Sources:
- `data/raw/geology/Tec-11 DES Sample Descriptions/Tecolutla-11Des Columna Litologica 40-3283 MD.pdf` — Rise Energy mud log, TECOLUTLA-11DES, cuttings every 5 m, 40–3,283 mMD, dated 4 Dec 2018, 20 pages, bilingual (Spanish description is the primary text, English is a translation).
- `data/raw/geology/Directional Survey/TECOLUTLA DIRECTIONAL SURVEY DATA.CSV` — 98 stations for TEC-11DES (MD, TVD, TVDSS, inclination, azimuth, offsets), Drive date 27 Jan 2019. The same file holds 85 stations for TEC_10 and 26 for a well coded `1030022465` (unidentified, G-29).
Script: `src/tec11_mudlog.py`. Outputs: `data/processed/tec11/mudlog_intervals.csv` (185 parsed intervals with raw Spanish and English text), `facies_along_hole.csv` (1 m sampling with mMD, mTVD, mSS, inclination, dominant lithology, grainstone-bearing and mudstone–wackestone percentages, oil show), `facies_summary.csv`, `summary.json`, `figures/03_tec11_lateral_facies.png`.

## 1. Method

1. The PDF text was parsed into intervals (top–base mMD), the mud logger's percentage line, and the description. Single-depth samples run to the next sample top. Percentages given as ranges ("90-95 / 5-10") are taken at their midpoints. Four intervals (2,590–2,615 mMD and three others) have no percentage line in the PDF text; their first-named lithology is taken as 100 % and they are marked `MISSING` in `pct_raw`.
2. Each description was split into lithology phrases; phrases opening with *trazas de*, *esporádicos fragmentos* or *nota* are traces and were dropped. Each remaining phrase is classed by the first lithology word in it. Dunham textures are kept as the logger wrote them: **grainstone** (no mud texture named), **grainstone-wackestone** (grainstone named first, e.g. "GRAINSTONE-WACKESTONE"), **wackestone-grainstone** (wackestone named first, e.g. "WACKESTONE EN PARTE GRAINSTONE", "WACKESTONE - GRAINSTONE DE MILIOLIDOS"), **mudstone-wackestone**, **packstone**; plus shale, sandstone, bentonite, chert.
3. Percentages are assigned to the phrases in order. The dominant lithology of each sample is the largest share. Oil shows are read from the Spanish *impregnación* wording: *moderada* = moderate, *pobre* = poor, *escasa* = scarce.
4. MD was converted to TVD, TVDSS and inclination by linear interpolation between survey stations (27 m spacing; minimum-curvature TVD is already in the CSV, so the interpolation error is well under 1 m). Depths are quoted as mMD and m subsea (mSS) throughout; the survey's TVDSS column is positive-up with a 4.7 m surface elevation, and mSS here is the depth below sea level.

## 2. Trajectory facts from the survey

| Item | Value | Source |
|---|---|---|
| Surface location | TEC-2 pad (mud log header "LOCATION: TECOLUTLA-2"; survey origin) | mud log p.1, survey row 1 |
| Kick-off | below 1,000 mMD; 47° at 2,209 mMD | survey |
| 60° reached | 2,318 mMD, 2,225 mSS | survey |
| 80° reached (start of lateral as defined here) | 2,563 mMD, 2,305 mSS | survey |
| 90° reached | 2,727 mMD, 2,323 mSS | survey |
| Lateral depth range (≥ 80°) | 2,305–2,331 mSS; held at 2,322–2,324 mSS from 2,727 to 3,140 mMD, then dropping to 2,331 mSS at TD | survey |
| Total depth | 3,283 mMD, 2,331 mSS, 82° | survey |
| Azimuth | 316° building to 327–331° in the lateral | survey |
| Horizontal displacement at TD | 1,190 m from the TEC-2 surface location | survey |

The lateral sits 4–12 m **below** the highest TEC-6/TEC-9 perforations quoted in the review (2,308–2,319 mSS, review v3 §5). The review's phrase "roughly 2,311+ mSS" is therefore slightly shallow; "2,305–2,331 mSS, mostly 2,322–2,324" is the survey value.

## 3. Facies along the hole

Carbonate becomes the dominant cuttings lithology at **2,360 mMD (2,245 mSS, 61°)**. Above it the shale carries carbonate fragments from 2,215 mMD (traces of white mudstone) and 5–30 % mudstone–wackestone from 2,340 mMD. The clastic section, as the review says, ends about 2,185–2,360 mMD depending on whether the first carbonate traces or the first carbonate-dominant sample is used.

Metres by dominant lithology (from `facies_summary.csv`):

| Segment | Length m | Grainstone | Grainstone-wackestone | Wackestone-grainstone | Mudstone-wackestone | Shale | Bentonite |
|---|---|---|---|---|---|---|---|
| Carbonate section, 2,360 mMD to TD | 923 | 0 | 50 | 190 | 622 | 31 | 30 |
| Build in carbonate (61° to 80°), 2,360–2,563 mMD | 198 | 0 | 0 | 0 | 198 | 0 | 0 |
| Lateral (≥ 80°), 2,563 mMD to TD | 720 | 0 | 50 | 190 | 419 | 31 | 30 |

Percentage-weighted over the 720 m lateral: grainstone-bearing textures 224 m, mudstone–wackestone 362 m, the balance shale, bentonite and minor sandstone.

Where the grainstone is:

| Interval mMD | mSS | Texture as logged | Shows |
|---|---|---|---|
| 2,650–2,655 | 2,321 | "GRAINSTONE-WACKESTONE blanco, café claro, semicompacto" | none |
| 2,655–2,745 | 2,321–2,327 | "WACKESTONE en parte GRAINSTONE" then "WACKESTONE - GRAINSTONE DE MILIOLIDOS ... compacto, en parte recristalizado" | none |
| 2,750–2,840 | 2,327 | alternating wackestone-grainstone and grainstone-wackestone (70–100 %), 10–20 % bentonite in places | poor impregnation, yellow fluorescence 2,755–2,790 |
| 2,865–2,880 | 2,328 | wackestone-grainstone | none |
| 2,935–2,945 | 2,328 | wackestone-grainstone | **moderate impregnation** (the only moderate show in the well, 2,920–2,945 mMD, with the mudstone-wackestone above it) |
| 3,135–3,165 | 2,327 | wackestone-grainstone 60–70 % with 30–40 % bentonite | none |

Everything else in the lateral is mudstone–wackestone (white, cream, light brown, semicompact, in part recrystallised) with poor or scarce oil impregnation between 2,485 and 2,580 mMD and 2,885 and 3,035 mMD, and no show at all over 482 of the 720 m.

Two features the review does not mention:

- **Shale inside the carbonate section at 2,584–2,615 mMD** (78–82°, 2,309–2,313 mSS): three samples of grey-green bentonitic shale with 10 % bentonite. Either a shale interbed or the well briefly crossing the top of the El Abra while still building angle. It sits at the shallowest point of the lateral.
- **Bentonite-rich last 180 m (3,103–3,283 mMD)**: 30–40 % bentonite in every sample, with the well dropping from 2,322 to 2,331 mSS. The lateral was drifting out of clean carbonate as it ended.

## 4. What this settles

- The review's statement that TEC-11 "ran through roughly 900 m of dominantly mudstone–wackestone with only intermittent miliolid grainstone" is confirmed on the numbers: 923 m of carbonate section, 622 m of it mudstone–wackestone-dominant, and 240 m in which grainstone is named.
- **No sample in the well is logged as pure grainstone.** The miliolid grainstone occurs only as "wackestone-grainstone" or "grainstone-wackestone" mixed textures, and the logger records it as compact and partly recrystallised, with poor or no oil impregnation over 200 of the 240 m. The review's word "grainstone" should be qualified to "wackestone to grainstone, compact" in the deck (G-27).
- The oil shows are weak everywhere: 20 m moderate, 259 m poor, 125 m scarce, 519 m none over the carbonate section. The one moderate show (2,920–2,945 mMD) is in the best 100 m of rock (2,865–2,945 mMD).
- The lateral was at the right depth relative to the TEC-6/TEC-9 perforations, 4–12 m deeper. Depth is not the explanation; facies is, as the review concludes.
- Vertical section: the well crossed only 86 m of true vertical carbonate (2,245–2,331 mSS) while drilling 923 m of hole, so the mud log cannot be used as a vertical facies profile of the El Abra at this location.

## 5. Caveats

- Cuttings at 5 m in a 90° hole with 8½" bit lag can smear 5–15 m; the intervals are the logger's, not corrected for lag.
- Samples at 2,360–2,391 mMD are noted as contaminated with cement and metal burr (a cement plug and casing shoe); the lithology there is unreliable.
- 28 of the 100 carbonate-section descriptions have part of the English translation appended to the Spanish text by the PDF layout; classification uses the Spanish keywords and is unaffected, but `description_es` in the CSV is not clean for those rows.
- Percentages are the mud logger's visual estimates.
