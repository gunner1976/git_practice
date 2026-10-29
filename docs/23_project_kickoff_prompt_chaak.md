# Kick-off prompt: narrated technical presentation app for Project Chaak

Paste the block below into the Project Chaak session. Fill in the bracketed items, or let the session ask for them.

---

I want you to build a narrated, animated technical presentation for **Project Chaak**, in the same format as the one built for the Tecolutla field (Contract Area 24). The audience is **[audience, e.g. a partner's technical team]**, and it must tell a strong technical story covering geology, history, operations, reserves and economics, ending at the current state of the project and the case for **[the key decision or next well]**.

**Reference.** The full method and lessons are in `docs/22_narrated_presentation_playbook.md` in the GitHub repository `gunner1976/git_practice`, branch `claude/tecolutla-tec12-handover-b45gx9`. Add that repository to this session (read access is enough) and read the playbook before you start. Reuse its code where it fits:
- `presentation_app/` holds the app sources and `build.py`.
- `presentation_app/tts/render.py` is the narration renderer.
- `presentation_app/src/engine.js` is the player and narrator.
- `presentation_app/src/field3d.js` is the 3-D scene.
- `presentation_app/tests/` holds the WebKit iPhone test and the broken-speech test.

**What to build.** A single-page app published as a private Artifact, with four tabs:
1. **Presentation:** slides that build in steps, narrated with captions. Include a well-by-well history in 3-D that aggregates over time to today, plus production, pressure and cost charts.
2. **Slides:** the same story as static 1920×1080 slides with speaker notes and Print / PDF.
3. **Field in 3-D:** the reservoir surface, wells and seismic, with toggles, a history slider and labelled wellbores.
4. **Data:** the tables behind the figures, with sources.

**Voice.**
- Pre-render the narration offline with Kokoro `af_heart` (English) and Piper `es_MX-claude-high` (Mexican Spanish): one MP3 per step plus a caption-timing JSON file.
- Add an EN/ES toggle and a live speed slider driven by `playbackRate`. Keep browser voices only as a guarded fallback.
- Read 1900s years as spoken English ("nineteen eighty"). In Spanish, strip thousands separators. Captions show the written text; the engine gets a spoken form.
- Translate the script into Mexican Spanish keyed `slideId#step`.
- I'll listen to a sample in each language before you render everything.

**Data rules (non-negotiable).**
- Units and provenance on every figure and slide; USD unless stated.
- Never convert a currency without a confirmed rate.
- Never interpolate silently. Show reported zero or shut-in months as 0 and months with no record as gaps, and say so on the chart.
- Log every gap, conflict or assumption in `docs/gaps.md`.
- Keep raw files immutable, with SHA-256 manifest rows.
- If a government or third-party portal blocks you, log it and move on; don't route around it.
- I'll correct facts as we go. Apply each correction everywhere (narration EN/ES, slides, data files), re-render only the affected audio steps, and log the change.

**Data.** Sources: **[repository / Drive folder / data room for Chaak]**. Key facts I can confirm on request: **[wells, operator, contract, current status]**. Ask me for anything you can't find instead of guessing.

**Working method.**
1. Inventory the data and propose a slide outline, with the key message of each slide, before building.
2. Build the data layer as scripts in the repository: a processed-data folder and an app-data builder.
3. Build and test the app:
   - Headless Chromium with `--use-angle=swiftshader --enable-unsafe-swiftshader`: screenshot every slide and check there are no errors.
   - Playwright WebKit with iPhone portrait and landscape profiles: check playback, the language switch and every tab.
   - Run the test that forces the speech engine to fail.
4. Publish privately, then iterate on my feedback.
5. Commit and push to a feature branch after each round. No pull request unless I ask.

**Watch-outs from Tecolutla.**
- Reset the shared 3-D state when switching tabs.
- Keep surfaces opaque.
- Anchor labels where each well enters the reservoir, with leader lines.
- Use a focus mode (fade the other wells, add a halo and a target marker) for the well the case rests on.
- Show surface pads in plan view.
- Never seek inside one long audio file.
- Call `play()` inside the tap.
- A cancelled step must never pause the player.

Start by reading the playbook and the data, then give me the outline and a list of the open questions only I can answer.
