# Prompt: building a narrated, animated presentation with neural EN/ES voice-over

Use this as a brief for another agent. It records how the Tecolutla presentation app (`presentation_app/`) was built and what went wrong along the way.

---

You are building a self-narrating technical presentation: a single-page web app in which slides build in steps, the camera or charts animate, and a natural-sounding voice reads the narration in English or Spanish, with synchronised captions. Follow the approach below. It is proven, and each rule exists because the alternative failed.

## 1. Voice: pre-render neural audio offline; do not rely on the browser's speech engine

- The Web Speech API (`speechSynthesis`) sounds robotic on most machines, varies by browser and operating system, and, when no Spanish voice is installed, reads Spanish with an English voice. Use it only as a fallback.
- Render the narration offline with open-source neural TTS on CPU:
  - **English:** Kokoro v1.0 through `kokoro-onnx` (voice `af_heart`; British alternatives `bf_emma` and `bm_george`). Model files `kokoro-v1.0.onnx` and `voices-v1.0.bin` come from the GitHub release `thewh1teagle/kokoro-onnx` → `model-files-v1.0`. Use `lang='en-us'`.
  - **Spanish:** Piper `es_MX-claude-high` (rhasspy/piper-voices on Hugging Face), a voice trained on a native Mexican speaker, so the accent is authentic. Kokoro's Spanish voices (`ef_dora`, `em_alex`) are trained on limited data; offer one as an alternative only.
  - Kokoro runs at roughly 0.4–1× real time on 4 CPU cores; Piper is about 10× faster. Budget about an hour for 35 minutes of English. Make the renderer resumable, and able to re-render only named steps (for example an env var `REDO="slide#step,…"`), so a one-line text fix does not cost a full re-render.
- Write **one MP3 per narration step** (mono, 48 kbit/s, `ffmpeg -codec:a libmp3lame`), plus a JSON file of caption timings: `{slideId: {step: [[t0, t1, captionText], …]}}`. Per-step files mean the player never seeks. Seeking inside one long file fails on hosts without HTTP byte-range support, and playback silently restarts at 0.
- Group sentences into chunks of up to about 220 characters. Render each chunk separately, normalise its peak, and add about 0.3 s of silence between chunks. Each chunk becomes one caption line.
- I could not listen to the output. A Whisper check (faster-whisper `small`) confirmed the language and intelligibility but cannot rank naturalness, so have a human listen to a sample in each language before rendering everything.

## 2. Two texts: what is shown and what is spoken

Captions show the written text. The engine gets a spoken form produced by a separate normalisation function per language. Keep the browser fallback and the offline renderer on the **same** rules. A bug we hit: the speech form was leaking into the captions ("tech 10" instead of "TEC-10").

English spoken-form rules:
- Well names: `TEC-10` → "tech 10".
- Units: `bbl/d` → "barrels a day", `MMbbl` → "million barrels", `mSS` → "metres subsea", `°API` → "degrees A P I", `%` → "percent".
- Acronyms spelled out where needed: CNH → "C N H", GLJ, WTI, PVT, PSTM.
- Dashes: en dash → "to", minus sign → "minus".
- **Years 1900–1999 as spoken English:** 1980 → "nineteen eighty", 1907 → "nineteen oh seven", 1960s → "nineteen sixties". Leave 2000s to the engine ("two thousand twenty"). Match with `(?<![\d,.])(19\d\d)(s?)(?!\d|,\d)`. A lookahead of `(?![\d,])` wrongly skips "1971," before a comma.

Spanish spoken-form rules:
- `TEC-10` → "Tec 10"; units in Spanish ("barriles por día", "metros bajo el nivel del mar").
- **Strip thousands separators** (`2,294` → `2294`), or the engine reads the comma as a decimal point.
- Years stay as the engine reads them ("mil novecientos ochenta" is correct Spanish).

Translation:
- Translate the narration once into a JSON file keyed `slideId#step`, in natural Mexican Spanish for a petroleum audience. Keep well names and acronyms, spell out numbers where the English spells them out, and add no facts.
- Running three parallel translator agents on about 45 lines each works well. Validate the result: same keys, the same well names in every line.
- On-slide text can stay in English; say so in the UI.

## 3. Player rules

- Each slide is `build(el) → steps[]`, with each step `{say, run(fast)}`. The step's narration length drives its animation length: read the duration from the timing JSON and divide by the playback rate. Fall back to a words-per-second estimate.
- **Speed slider:** set `audio.playbackRate` live with `preservesPitch = true`. With browser voices the rate applies only from the next utterance, so cancel and re-speak the current chunk at the new rate.
- Call `audio.play()` synchronously inside the Play click handler (no `await` before it), or Safari blocks it.
- A cancelled utterance must not clear the caption that a newer one has just set: check the generation counter before clearing.
- Play-loop race: when restarting playback (for example after a language switch), give each loop a token and let only the current loop null the loop reference. Otherwise playback silently stops.
- Pre-fetch the current slide's step files when it opens.
- List voices as: studio (neural) voices for the current language first, then browser voices ranked so that "Natural", "Neural", "Online", "Premium" and "Google" come first and novelty voices last. Never offer an English voice for Spanish.

## 4. Animation and 3-D lessons (three.js, d3)

- One WebGL canvas can be shared between the presentation and an explorer tab. **Pause rendering** behind 2-D slides, but when another tab opens, **reset every state a slide may have changed**: auto-orbit, markers, label visibility, surface opacity, vertical exaggeration, highlight and camera. Build the first slide before choosing the opening tab, so its scene cannot overwrite the explorer's.
- Transparent materials are depth-sorted per object and can make a surface vanish behind seismic slices. Keep surfaces opaque unless a slide needs transparency.
- Labels: anchor each well label where the well enters the reservoir, place labels each frame with collision avoidance, and draw a leader line and dot to the anchor (an SVG overlay). Labels floating above the wells read as a screen in front of the scene, not as attached to anything.
- **Focus mode for the "money" well:** fade the other wells (opacity about 0.16), hide clutter such as cumulative-production columns, put a halo tube round the featured well, and add a pulsing target marker with its own label where it reaches the objective. Keep the camera close and on the side from which the target is visible.
- Surface-location views: draw pads as boxes and plan-view well traces on a ground grid. A camera inside the wellbores shows nothing useful.
- Vertical exaggeration of about 2.5×. The default explorer view frames the reservoir plus the lower about 600 m of each wellbore, not the whole column to surface.

## 5. Data honesty in charts

- Distinguish **reported zero or shut-in months** (draw 0) from **months with no record** (break the line, or hatch the band and label it "no monthly record"). Derive zeros only from sourced non-producing periods, and log the rule.
- Show water cut on a right axis as a volume-weighted 3-month value, null while the well is shut in. Monthly ratios at tiny rates are noise.
- Put the sources on every slide, keep units throughout, and never interpolate silently.

## 6. Testing headless

- Use Playwright Chromium with `--use-angle=swiftshader --enable-unsafe-swiftshader` (the older `--use-gl=swiftshader` blocks the main thread). Route CDN script URLs to local copies.
- Screenshot every slide at its last step, and key slides at step 0. Assert no page errors. Check audio by reading `currentTime`, `paused` and the caption text, and by moving the speed slider.
- For a static deck, measure overflow automatically: flag any in-flow element whose bottom passes the footer.

## Reference implementation

The working code is in this repository:
- `presentation_app/tts/render.py` (renderer: chunking, spoken form, per-step MP3, timings, `REDO`).
- `presentation_app/src/engine.js` (narrator: studio audio, browser fallback, rates, captions, player).
- `presentation_app/src/field3d.js` (labels with leaders, focus mode, target marker, pads).
- `presentation_app/narration_en.json` and `presentation_app/narration_es.json` (source and translated scripts).

## 7. Safari / iPhone lessons (added 29 Oct 2026)

- **Guard every `speechSynthesis` call.** On an iPhone viewing the public link, the speech API threw during start-up ("undefined is not an object (evaluating 'Object.getPrototypeOf(voice)')"). The narrator now treats the browser engine as optional; any failure only removes the fallback voices.
- **Never let a cancelled step touch the shared `<audio>` element.** The old loop's late `pause()` aborted the new clip (WebKit reports `AbortError`). Only `cancel()` pauses; a stale loop just returns.
- **Test in WebKit on Linux:** install Playwright WebKit into its own folder (`PLAYWRIGHT_BROWSERS_PATH=<dir> node <playwright>/cli.js install webkit`) plus the apt libraries it lists (GTK 4, GStreamer GL/bad/good/libav and others). Run with `devices['iPhone 14']` and the landscape variant, and log `play()` and `pause()` calls. The live claude.ai link cannot be opened by an automated browser (bot check), so test a local copy.
- **Phones:** let control groups wrap, hide text labels and keep icons, and compact the header in short landscape viewports. Recommend landscape or a laptop for the 3-D tab.
