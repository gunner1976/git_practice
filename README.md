# Eko island: a small replication harness

This harness reruns, on a smaller scale, the setup of Cloos, Norelli, Durbin, Andreas, Rus & Isola,
*Is this machine playing?* ([arXiv:2610.07130](https://arxiv.org/abs/2610.07130), Oct 2026). In that
study, Claude agents ("Eko") were left on a text-described virtual island with no task, memory kept
in text files, and an island that reset every hour. The veterans were then tested on tasks against
fresh copies.

The harness has five parts:

- **`world/`**: a deterministic, seedable 3D island with simple physics and one hidden rule.
- **`agent/`**: a Claude tool-use loop with a notes directory as its only long-term memory, plus the cost guard and resume logic.
- **`runs/`**: one directory per run, holding JSONL logs of everything.
- **`analysis/`**: stats, hidden-rule discovery, play-marker flags, transcripts and a markdown report with charts.
- **`soul.md`** and **`config.yaml`**: the system prompt and every knob.

## Quick start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m pytest -q                      # 45 tests: physics, hidden rules, loop, resume, cost cap, request shape, ladder

# 1. Pilot (always first): 1 agent, 2 sessions, 30 steps. Prints the transcript, notes, cost and a full-run estimate.
python run.py pilot --max-usd 3

# 2. Full run, only after reviewing the pilot. Phase A, then Phase B. Re-running the same command resumes it.
python run.py all --run-id main --max-usd 120
#    or the phases separately:
python run.py freeplay --run-id main --max-usd 70
python run.py eval     --run-id main --max-usd 120   # the cap covers the whole run's ledger

# 3. Analysis -> runs/main/report/report.md (+ PNG charts)
python run.py analyze --run-id main

# Other
python run.py pilot --mock                # whole pipeline with a scripted fake agent, no API calls
python run.py estimate --run-id <pilot> --model claude-opus-5-5
python -m analysis.transcript runs/main/phase_a/agent_1/session_03.jsonl
```

Useful flags: `--model claude-opus-5-5`, `--effort low|medium|high|xhigh|max`, `--agents N` (≤13),
`--sessions S` (≤30), `--steps K`, `--parallel P`, `--config other.yaml`.

`freeplay`, `eval` and `all` refuse to start until a completed pilot that used the real model
exists under `runs/`. `--skip-pilot-check` overrides this.

## The world (`world/`)

- **Terrain** (`terrain.py`): the island is 64 × 64 m and sinks into the sea at the edges. It has a
  few gentle random hills and two named high points:
  - **Peak**: a smooth hill about 11.6 m high. You can walk up it. Its flanks are steep enough that
    objects roll off them, but its summit area holds objects.
  - **Spire**: a flat-topped mesa, top at about 5.5 m, with a cliff about 3.5 m high. You can't
    walk up the cliff, and a single jump (1.3 m) doesn't reach the top. To get up, you build a
    staircase of cube stacks 1, 2 and 3 high and jump from the top one. You can also throw objects
    onto the top.
- **Objects** (`island.py`): 12 cubes (1 m, 1 kg, 12 colours), 1 rock (0.7 m, 4 kg), 1 ring
  (0.8 × 0.15 m, 0.3 kg). Each has an id, shape, colour, mass and position. All are axis-aligned
  boxes for physics. The initial layout is drawn from `world.seed`.
- **Physics**: after every action the world settles to rest.
  - Gravity: objects drop onto the highest surface below them.
  - Stacking: an object can rest on top of other objects.
  - Toppling: an object topples if the centre of mass of it and everything resting on it lies
    outside the footprint of its supports.
  - Collisions: overlapping objects get pushed on top, and a thrown object stops when it hits the
    side of something.
  - Slopes: objects on terrain steeper than `slide_slope` tumble downhill.
  - Throws follow a ballistic arc integrated at 20 ms. Launch speed is `force / sqrt(mass)`, from
    hand height.
- **Avatar actions**:
  - `move(dx, dy)`: walk up to 3 m. You can't climb rises of more than 0.5 m per 0.2 m step.
  - `jump(dx?, dy?)`: up to 1.5 m across and 1.3 m up.
  - `pick_up(id)`: reach is 2.5 m, and you hold one thing at a time.
  - `place(id, x, y, z)`: release height z, up to 2.5 m above your feet.
  - `throw(id, [dx, dy, dz], force)`: force from 0 to 20.
  - `wait`.
- **Hidden rule**: throwing the rock with force ≥ 10 spawns a new cube where it lands. Nothing in
  the soul, the tools or the observations mentions it.
- **Observation** (text only): your position and what you're holding, then one line per object
  (`cube_3: yellow cube @ 31.8 18.9 2.0`).
- **Sessions**: each session has a fixed budget of world actions (default 150, standing in for the
  paper's 1-hour sessions). `World.reset()` restores the exact initial state at the start of every
  session.

## The agent (`agent/`)

- **API**: one Messages API call per turn, made by `client.py`. Defaults:
  - Model: `claude-sonnet-5-5`; `claude-opus-5-5` is also supported.
  - Effort: `medium`, with adaptive thinking shown as summaries so transcripts include the reasoning.
  - Automatic prompt caching.
  - The server-side refusal fallback (see the assumptions below).
- **Tools**: the six world actions, plus `list_notes`, `read_note` and `write_note`, all confined to
  the agent's own notes directory.
- **Context**: each session starts from an empty context. It holds only the soul (as the system
  prompt), an opening message, and whatever the agent reads from its notes.
- **`soul.md`**: the system prompt, loaded from `agent.soul_path` and snapshotted into each run.
  It has no goals, rewards or mention of games; a test enforces that.
  - To study how much the framing drives behaviour, copy it (say to `soul_minimal.md`), point
    `agent.soul_path` at the copy and use a new `--run-id`.
- **Stop hook**: if the agent ends its turn without acting, it gets `stop_hook_message` (the paper
  used a similar nudge to keep going), up to `max_stop_nudges` times per session.

## Phases

- **Phase A, free play** (`run.py freeplay`):
  - N agents (default 3, up to 13) × S sessions (default 10, up to 30).
  - Each agent has its own `agents/<agent>/notes/`.
  - Agents run in parallel threads; sessions within an agent run in order.
- **Phase B, evaluation** (`run.py eval`):
  - Every veteran, plus an equal number of fresh agents (same soul, empty notes), does each task in
    its own session with the same step budget, on the same world seed:
    1. `spire_objects`: put as many objects as possible on the Spire.
    2. `tallest_tower`: build the tallest stable tower.
    3. `ring_on_peak`: get the ring onto the Peak.
    4. `make_cubes`: produce as many cubes as possible.
  - Scoring (`world/tasks.py`) reads only the final world state:
    - `spire_objects`: objects resting on the Spire top.
    - `tallest_tower`: height in metres of the tallest settled stack of ≥ 2 objects, measured from
      the ground under its base.
    - `ring_on_peak`: 1 if the ring rests within 2 m of the summit, else 0.
    - `make_cubes`: cubes minus 12.

## The ladder (`agent/ladder.py`, `world/rules.py`)

A staged tournament built on the same world and loop. Every contestant is the same model, so what
is being selected is a **soul plus the notes it writes**. The winner is that pair, exported as a
bundle for human review.

```bash
python run.py ladder-estimate --run-id <pilot-id>       # upper-bound cost from a real pilot
python run.py ladder --run-id L1 --max-usd 300          # run or resume
```

**Hidden rules ("eggs")**, all invisible to the agent except as objects that appear:

| Tier | Rule | Condition | Effect |
|---|---|---|---|
| 1 | `rock_spawn` | throw the rock with force ≥ 10 | a cube appears where it lands |
| 2 | `stack_chime` | stack three cubes bottom-to-top red, orange, yellow | a golden egg appears on the Peak summit (once per session) |
| 3 | `patient_ring` | stand on the Peak summit holding the ring and `wait` 5 times in a row | a golden egg appears on top of the Spire (once per session) |
| 4 | transfer | all three, with the threshold, colour order and wait count re-drawn from each seed | memorised facts fail; methods that found them should still work |

Add a rule by subclassing `Rule` in `world/rules.py` (an `after_action` hook, a `tier`, a
`keywords` regex for detecting when notes describe it) and registering it in `RULES`.

**Stages** (`ladder.stages` in `config.yaml`). For each surviving agent:

1. `free_sessions` of free play on the stage's island with its rules switched on. Notes persist
   through the whole ladder.
2. One evaluation session on each of `eval_seeds`: a new island layout, the stage's rules, a copy
   of the agent's notes, and `eval_message` ("Something is hidden on this island…") as the only
   prompt. A target counts as exploited when it fires at least its `exploit_threshold` times in the
   session (rock: 3, eggs: 1).
3. The agent advances only if every target is exploited in at least `min_seeds` seeds (default 2
   of 3). Selection is over repeated trials, so one lucky session can't carry an agent.

`replicates` (default 2) runs independent copies of each soul, and the report also summarises
results per soul. The default contestants are `soul.md` ("curious"), `souls/systematic.md` and
`souls/minimal.md`. None mention goals, games, eggs or secrets; a test checks this.

**After the top stage:**

- *Notes transfer check*: for each graduate, a fresh copy given the graduate's notes and a fresh
  copy with empty notes both run the final stage's evaluation. Notes that make a fresh copy better
  are the strongest evidence that the graduate learned something reusable.
- *Graduation bundle* in `graduates/<agent>/`: `soul.md`, `notes/`, `trace.json` (every stage,
  every evaluation, firings, first-find steps, whether its notes already described the rule, and
  log paths) and `REVIEW_REQUIRED.md`. Nothing is deployed automatically. The bundle shows
  skill at finding hidden mechanics in a toy text world, not real-world judgement, so a person
  should read the notes and scope permissions before loading it anywhere.

Each evaluation also records process signals: steps to first find, and `prior_knowledge` (whether
the notes already described the rule before the session began).

Outputs: `ladder_report.md`, `ladder_results.jsonl` (one line per evaluation session), and logs
under `ladder/<stage>/<agent>/`. Resume and the cost cap work the same as for the other commands.

**Not done yet**: Tier 4 is still the island with re-drawn parameters. A truly un-island-like
final world (different objects and setting, same tool shape) is the next step for testing
transfer.

## Logs (`runs/<run_id>/`)

| File | Contents |
|---|---|
| `config.yaml`, `soul.md` | exactly what the run was started with (a resume reuses them) |
| `ledger.jsonl` | one line per API call: model, token usage, USD cost, agent/session/step |
| `phase_a/<agent>/session_NN.jsonl` | every observation, assistant message (text, summarized thinking, tool calls) with usage and cost, world action and result, physics events, notes tool call, **notes diff**, hidden-rule firing, stop-hook nudge, final world state, final notes |
| `phase_b/<agent>/<task>.jsonl` | the same, plus a `score` event |
| `agents/<agent>/notes/`, `snapshots/` | live memory, and memory at the start of each session |
| `eval_results.jsonl`, `state.json` | scores, and the progress used for resuming |
| `pilot_report.md`, `report/report.md` | human-readable outputs |

## Analysis (`analysis/`)

- **`stats.py`**: per-task mean and SD for veterans vs fresh agents, Welch's t-test, Mann-Whitney U,
  Hedges' g, and Fisher's exact test for the binary ring task.
- **`discovery.py`**: for each agent, when the rock-spawn rule was first:
  - *exposed*: fired at all;
  - *articulated*: described in notes or speech, i.e. a sentence that mentions the rock, a cube and
    creating or appearing;
  - *exploited*: fired ≥ 3 times in one session.

  It also counts firings in each agent's `make_cubes` evaluation session.
- **`play_markers.py`**: flags passages for you to review by hand, as checkboxes in the report:
  - self-declared rules or games (game, rule, record, round 3, doesn't count, …) in notes and speech;
  - action n-grams (3 to 5 actions long) repeated ≥ 3 times in a session with varied parameters;
  - pretend or naming language (let's call, planet, temple, pretend, …).

  These are search heuristics, not judgements.
- **`report.py`**: writes `report.md` with tables, excerpts and four charts: scores, discovery
  heatmap, markers per session, and spend.

## Guardrails

- **Cost cap**:
  - `--max-usd` applies to the whole run directory. Spend is computed from each response's `usage`,
    with the per-MTok prices in `config.yaml` (uncached input, output, cache read, cache write).
  - Before each call the harness checks that `spent + 1.25 × last call` stays under the cap. If it
    wouldn't, the run stops cleanly: the session log gets an `aborted` event and the command prints
    how to resume.
  - With `P` parallel workers, the overshoot is at most about one call per worker.
  - Calls served by an unknown model (such as a refusal fallback) are charged at the most expensive
    configured rate.
- **Resume**:
  - The unit of resumption is a session. Re-run the same command with the same `--run-id`.
  - Completed sessions are skipped.
  - A session that crashed or hit the cap is re-run from scratch. Its notes are restored from the
    snapshot taken when it first started, and the partial log is kept as `*.crashedN.jsonl`.
  - Spend from aborted attempts stays in the ledger and still counts against the cap.
- **Pilot first**: `run.py pilot` and the pilot-check described above.

## Assumptions and departures from the paper

I couldn't fetch the paper's full text from the build environment (arxiv.org was blocked). The
setup below comes from the abstract and search excerpts of the paper and its companion site,
`machineplaying.org`, plus press coverage. **Check each item against the PDF.**

What the excerpts say about the paper:

- 13 agents, about 30 hours each, on Claude Code with Claude Opus 4.7.
- Text perception, and move / jump / pick up / place / throw actions.
- Text-file memory that persists across hourly world resets.
- A "naturally curious" SOUL.md.
- An automatic message that urges the agent on when it stops.
- The one non-standard mechanic is that the rock makes new cubes when thrown hard enough.
- The Spire is the highest mesa and can't be reached with a simple jump.
- Play judged against four hallmarks: self-made rules, repetition with variation, pretending objects
  are something else, and pursuing goals for their own sake.

Where things were unclear, I used your defaults and the choices below:

1. **Harness.** The paper used Claude Code on Opus 4.7. This uses a minimal Messages API tool loop
   on `claude-sonnet-5-5` by default (or `claude-opus-5-5`). There is no bash, file system or web
   access, only the island and notes tools.
2. **Session length.** 150 world actions stand in for one hour. Notes tool calls don't use up
   world steps but are capped at 80 per session. After the last action, the agent gets a
   "day is ending" message and 3 notes-only turns, so it can write its memory.
3. **What the agent is told.** It sees "Moments left today: N" (`show_steps_remaining`). The
   opening message names the Peak and the Spire with rough coordinates (`describe_landmarks`); the
   paper's agents clearly knew these names, but whether they got coordinates is unknown.
4. **Soul wording.** `soul.md` is my own short text built around the reported "naturally curious"
   framing. It tells the agent that days reset and that only its notes persist. It is not the
   paper's SOUL.md.
5. **Physics.** The paper used a game engine. Here every object is a box with no rotation, friction
   or bounce, and the world settles to rest after each action. The avatar has no collision body:
   if you place an object where you stand, you end up on top of it. Mass is not shown in
   observations. The task description lists mass as an object property but not as part of the
   observation.
6. **Hidden rule details.** The threshold is 10 on a 0–20 force scale, so roughly half of all
   throws that hard trigger it. The cube appears 0.9 m beyond the rock's landing point, along the
   throw's direction, so it doesn't pin the rock. Spawns are capped at 60 per session to keep
   observations bounded.
7. **Evaluation memory.** Each task starts from a copy of the veteran's notes as they stood at the
   end of Phase A. Notes written during one task never reach another task, so task order can't
   matter. Fresh agents start each task with an empty directory.
8. **Evaluation world.** By default the evaluation uses the same island seed as free play, so
   veterans know the layout. That matches "tested against fresh copies" in the same world. Set
   `phase_b.world_seed` to test transfer to a new layout.
9. **Scoring definitions.** These are my own operationalisations (see Phases above). Objects
   still in the agent's hands don't count.
10. **Refusal fallback.** `fallbacks: "default"` is on, so a turn the safety classifiers decline is
    re-run on another model rather than ending the session. Any such call is flagged
    (`"fallback": true`) and counted in the report. Set `agent.refusal_fallback: false` if
    model purity matters more than continuity.
11. **Not deterministic.** The world is deterministic given its seed, but model sampling is not.
    Repeated runs give different behaviour.
12. **Small samples.** With 3 versus 3 agents the significance tests are very underpowered. The
    report says so and shows the individual scores.

## Tests

`tests/test_physics.py` covers:

- determinism;
- gravity, stacking, overhang toppling and staircase centre-of-mass toppling;
- slope tumbling;
- ballistic range against the analytic formula;
- side collisions and mass effects;
- the hidden rule: threshold, inclusivity, rock-only, repeated spawns, reset, cap, and that it never
  appears in observations;
- Spire and Peak reachability: you can't walk or single-jump onto the Spire, but a 3-2-1 staircase
  gets you up;
- pick-up and place rules;
- task scorers.

`tests/test_harness.py` covers:

- that the soul has no goal, reward or game words;
- notes sandboxing and the cost formula;
- the cost cap stopping cleanly and then resuming;
- crash, resume and notes restore;
- log contents;
- that veterans get their memory and fresh agents don't;
- that the report builds.

`tests/test_rules.py` covers each egg rule's trigger, near-misses, once-per-session firing,
reset, seed-randomised parameters, and that eggs appear only as objects. `tests/test_ladder.py`
runs whole ladders with the mock agent: stage rule switching, full graduation with bundle and
transfer check, elimination, and resume after the cost cap.

`tests/test_client_shape.py` checks the real API request and the thinking-block round trip against
a stub HTTP transport.

## Sources

- Cloos et al., *Is this machine playing?*, [arXiv:2610.07130](https://arxiv.org/abs/2610.07130), and the companion site https://machineplaying.org/
- [MIT Technology Review, 19 Oct 2026](https://www.technologyreview.com/2026/10/19/1147095/ai-stranded-claude-virtual-desert-island-play/)
- [The Next Web](https://thenextweb.com/news/mit-claude-agents-virtual-island-play), [Gizmodo](https://gizmodo.com/researchers-stranded-an-ai-agent-on-a-virtual-island-things-got-very-weird-2000825998), [DEV Community](https://dev.to/techaiwire/claude-opus-47-agents-invent-games-on-a-virtual-island-4h7l), [Mezha](https://mezha.net/eng/news/mezha-fee5d6bca690475f34839095_ai_agents_left)
