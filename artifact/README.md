# Browser-only build (Claude Artifact)

`casing_design.html` is a single page that runs the whole engine in the browser:

- `data.js` — catalog data generated from `casingdesign/catalog/data/*.csv`
- `engine.js` — JavaScript port of the Python engine (ratings, load cases, evaluation, optimizer)
- `ui.js` — the app (projects, guided steps, design, report, EDM import)
- `head.html` — title, theme tokens, styles, library loads

Rebuild: regenerate `data.js` (see git history for the generator), then concatenate
`head.html` + `<script>` data/engine/ui `</script>` into `casing_design.html`.

Parity: `engine.js` is checked against the Python engine on all catalog ratings and on
both example wells (evaluations and optimizer picks) — see the session notes; rerun the
check whenever either engine changes.
