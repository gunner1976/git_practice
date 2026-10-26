# 21 — Presentation app: Tecolutla Field Story

Artifact: https://claude.ai/artifact/8njDjF1MuYdgDV7jmwW92g. It is private until shared from the page's Share menu.

## What it is

The app is a single web page with three tabs.

1. **Presentation.** It has 33 slides that play themselves with narration through the browser's speech engine. The control bar can change the voice and speed, turn captions on or off, and pause or step through the slides. Each slide builds in steps that are timed to the narration. The keys are space (play/pause) and ←/→ (step back and forward).
   - The 3-D slides share one field model. It includes the El Abra top (Jan 2019 grid), coloured from blue for the deep flanks to red at the crest, and the wells from the directional surveys. Wells are coloured by their status at any date, and columns on the reef grow with each well's cumulative oil and water.
   - **Field history** is a time-lapse from 1956 to Oct 2026. It plays in eight chapters, with oil stacked by well and the pressure surveys accumulating.
   - **Well by well** flies to each well in turn: TEC-6, 2, 7, 9, then the edge wells TEC-3/5/101, then TEC-10 and TEC-11 (two slides, one on the concept and one on the failures). Each well's production and events are revealed up to its state today.
   - **The field today** covers the current state, with TEC-10 restorable on a solvent schedule and TEC-2 intermittent.
2. **Field in 3-D.** This is an explorer for the PEMEX PSTM 554702 (displayed in depth at the well-tie velocities) and the 2019 PSDM. It has inline, crossline and depth slices, vertical exaggeration, a history date slider with playback, buttons to fly to each well, and view presets.
3. **Data.** This tab holds tables of wells, events, pressures, annual production by well, and the sources.

## How it is built

| Step | Script | Output |
|---|---|---|
| Seismic atlases, surfaces, well paths | `src/export_viewer_data.py <out>` | `pstm.png`, `psdm.png` (8-bit), `viewer_meta.json` |
| Compiled tables | `src/presentation_compile/*.py` | `data/processed/presentation/` (wells, events, pressure, production by well, opex, costs, technical tables; every value cites its source) |
| App data | `src/build_app_data.py <out>` | `app_data.json` |
| Page | `presentation_app/build.py` (sources in `presentation_app/src/`) | `index.html`, with the modules inlined; three.js 0.160 and d3 7.9 come from CDNs |

The narrated history is written from `events.json`, `wells.json`, `tec11_story.md` and `tec10_tec2_status.md`.

## Responses to the 26 Oct review points

1. **Golden Lane setting.** There is a new regional map slide: the Natural Earth coastline, a schematic rim trace, and Tecolutla at the south-eastern tip.
2. **Structure map.** It is recoloured blue to red, with red highest. The same ramp is used on the 3-D surface.
3. **Pressure.** The chart now starts at zero and adds a pressure-versus-cumulative chart with a closed-reservoir line. Without an aquifer the field would have reached its bubble point after about 0.1 MMbbl; it actually lost 0.5 MPa over 2.06 MMbbl.
4. **Production.** Full-width charts stacked by well show five producers (TEC-2, 6, 7, 9, 10), the March 1972 peak (932 bbl/d from three wells), and cumulative by well. The government SIH portal was unreachable (G-82).
5. **TEC-11.** One slide shows the concept as an animated schematic. A second plots the well along its length against the grid top, coloured by sonic, and steps through the failures: casing, fish, unisolated acid, water, plug, cost.
6. **TEC-10 logs.** They are redrawn as four simple tracks, with the marl, the El Abra top, the perforations and the TEC-12 reef top marked.
7. **Operations and costs.** Oil and water rates are plotted against monthly opex from 2018 to 2025, and the decline is explained. Annual-only years are drawn dashed.
8. **The marl.** A correlation panel shows the window as reef at the crest and marl at TEC-10/101, with the XRD results and a log-contrast table.
9. **Legibility.** All charts are drawn natively at slide scale, with fonts of 19–28 px and plain number formats.
10. **Technical slides.** Added slides cover fluids and gas (oil API, gas composition, GOR history, gas situation, no PVT), core (plugs, Dean-Stark, matrix vs well-test permeability), oil in place (sources, Monte Carlo, tornado), the drilling cost breakdown (TEC-12 AFE, per-well actuals), and the lean opex breakdown (Sep 2020 cost sheet).
11. **TEC-10 and TEC-2.** They are shown as restorable from Feb 2023: TEC-10 at about 30–45 bbl/d on a solvent or hot-oil schedule, TEC-2 intermittent at 16–23 bbl/d. The incremental economics depend on TEC-10 being back on.

## Testing

Every slide and both other tabs were run in headless Chromium (ANGLE SwiftShader) with no script errors. Narration was exercised in muted mode only. Voice quality depends on the viewer's browser: Edge and Chrome offer natural voices, and Safari offers Siri voices.

## Round 2 changes (26 Oct 2026)

- Well-by-well charts show a 3-month volume-weighted water cut on a right axis.
- Documented non-producing months are drawn as zeros (CNH-reported zeros, G-34; shut-in segments of each well's status history). 1956–59 and other months with no monthly record are hatched or left as breaks, never zero. Rule in `data/processed/presentation/production_notes.md` "Zero months"; G-87.
- Narration: captions show the written text (TEC-10), the speech engine gets the spoken form. Voices are ranked (neural / natural / premium first, novelty voices last); default rate 0.95. EN/ES toggle: Spanish narration and captions from `presentation_app/narration_es.json` (keyed `slideId#step`, translated from `narration_en.json`); slide text stays English.
- New content: Cerro Azul No. 4 and the TM-01 block on the Golden Lane slide (G-89); the TEC-11 Tantoyuca test (G-88); recovery against 45 El Abra fields with the four nearest pools (`analogue_rf.csv`); TEC-12 opens from a surface view of the pads with plan-view well traces; sales point PEMEX CAB Poza Rica.

## Narration audio (26 Oct 2026)

The browser speech engine gave poor voices, and an English voice when no Spanish one was installed. The narration is now pre-recorded with open-source neural voices and shipped as audio, so it no longer depends on the viewer's browser:

- English: Kokoro v1.0 (`kokoro-onnx`, voice `af_heart`), model `kokoro-v1.0.onnx` sha256 7d5df8ec…, voices `voices-v1.0.bin` sha256 bca610b8… (GitHub release thewh1teagle/kokoro-onnx `model-files-v1.0`).
- Spanish: Piper `es_MX-claude-high` (rhasspy/piper-voices on Hugging Face), a native Mexican-Spanish voice.
- `presentation_app/tts/render.py` writes one MP3 per step (`audio/<voice>/<slideId>__<step>.mp3`, mono 48 kbit/s) and caption timings (`audio/<voice>.json`). One file per step means playback never seeks, so it works on hosts without byte-range support.
- Spoken form follows the same rules as the app (TEC-10 → "tech 10" / "Tec 10"; Spanish strips thousands commas so the engine does not read them as decimals).
- The speed slider sets the audio playback rate live, with pitch preserved. The browser voices remain in the voice list as a fallback; Spanish never falls back to an English voice.
- A recogniser check (faster-whisper small) identified all candidate Spanish voices as Spanish with probability ≥ 0.96; it cannot rank naturalness.

## Slides tab and 3-D explorer fixes (26 Oct 2026)

- **Slides tab.** The static technical deck (formerly the separate Slides artifact K35tjz1TuyDcSzbwPZKdwc, now marked superseded on its first slide) is a tab of the app: 38 slides, notes toggle (N), keyboard paging, Print / PDF (one slide per page). Sources: `presentation_app/deck/slides/*.html` and `deck_order.json`; `build_deck_json.py` bundles them into `deck/deck.json` with images under `deck/img/` (figures captured from the app; not in git).
- **Field in 3-D.** The explorer now resets everything the presentation may have changed (auto-spin, TEC-12 pad markers, labels off, surface transparency, VE, camera); the first slide is built before the opening tab so it cannot overwrite the explorer. The El Abra surface is opaque unless a slide asks otherwise (transparent sorting could hide it behind seismic). Default view "Reservoir" frames the reef and the lower ~600 m of the wellbores. Well labels are anchored on the wellbore just above its cumulative column, placed to avoid overlaps, and joined to the well by a leader line.
- Narration audio (both voices, ~28 MB) is published with the app and regenerated with `presentation_app/tts/render.py`; it is not committed.
