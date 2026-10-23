"""The ladder: a staged tournament over souls and memories.

Every contestant is the same model; what differs, and what is being selected,
is the soul (system prompt) it runs under and the notes it has written.

For each stage, every surviving agent:
  1. plays freely for `free_sessions` sessions on the stage's island, with the
     stage's hidden rules switched on; its notes persist (and carry on to later stages);
  2. is evaluated on each of `eval_seeds`: a fresh island layout, the stage's rules,
     a copy of its notes, and `eval_message` as the only prompt. A target rule counts
     as exploited in a seed when it fires at least `exploit_threshold` times
     (rock: 3; eggs: 1);
  3. advances only if every target is exploited in >= `min_seeds` of the seeds.

After the last stage each survivor's notes are tested for transfer: a fresh copy
with the graduate's notes, and a fresh copy with empty notes, both run the last
stage's evaluation. Then a graduation bundle is written for human review.

Run layout additions (runs/<run_id>/):
  souls/<contestant>.md
  ladder/<stage>/<agent>/free_NN.jsonl, eval_<seed>.jsonl
  ladder/transfer/<agent>/{with_notes,empty}_<seed>.jsonl
  graduates/<agent>/{soul.md, notes/, trace.json, REVIEW_REQUIRED.md}
  ladder_results.jsonl          one line per evaluation session
"""

from __future__ import annotations

import copy
import json
import shutil
import traceback
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from world import World
from world.rules import RULES

from .cost import BudgetExceeded
from .loop import JsonlLog, run_session
from .notes import Notes
from .runner import Run, _archive_partial

REVIEW_TEXT = """# Review required before any deployment

This bundle won a simulated tournament on a toy island. That shows one thing: that under
this soul, with these notes, the model found hidden mechanics in a small text world more
reliably than the other contestants did.

It does not show judgement about real-world side effects, safety, or fitness for any
particular job. Before loading it into another system:

1. Read `notes/` in full. It is model-written text that will become part of a prompt.
2. Read `trace.json` and spot-check the logged sessions it points to.
3. Give the deployed agent only the permissions its job needs, and keep a human approving
   consequential actions until it has a track record in that setting.
"""


def stage_world_cfg(base: dict, stage: dict) -> dict:
    c = copy.deepcopy(base)
    active = set(stage["rules"])
    c["hidden_rule"]["enabled"] = "rock_spawn" in active
    c["hidden_rule"]["randomize"] = bool(stage.get("randomize"))
    for rid in c.get("rules", {}):
        c["rules"][rid]["enabled"] = rid in active
        c["rules"][rid]["randomize"] = bool(stage.get("randomize"))
    unknown = active - set(RULES)
    if unknown:
        raise KeyError(f"stage {stage['name']}: unknown rules {sorted(unknown)}")
    return c


def _notes_text(root: Path) -> str:
    return "\n".join(p.read_text() for p in sorted(Path(root).rglob("*")) if p.is_file())


def _articulates(rule: str, text: str) -> bool:
    if rule == "rock_spawn":
        from analysis.discovery import mentions_rule

        return mentions_rule(text)
    return bool(RULES[rule].keywords.search(text))


class Ladder(Run):
    def __init__(self, root: Path, cfg: dict, max_usd: float, mock: bool = False, base_dir: Path | None = None):
        base_dir = Path(base_dir or Path(__file__).resolve().parents[1])
        first_soul = (base_dir / cfg["ladder"]["contestants"][0]["soul"]).read_text()
        super().__init__(root, cfg, first_soul, max_usd=max_usd, mock=mock)
        self.state.setdefault("ladder", {})
        lad = self.cfg["ladder"]
        self.souls: dict[str, str] = {}
        sd = self.root / "souls"
        sd.mkdir(exist_ok=True)
        for c in lad["contestants"]:
            p = sd / f"{c['id']}.md"
            if not p.exists():  # snapshot on first start; a resume reuses the snapshot
                p.write_text((base_dir / c["soul"]).read_text())
            self.souls[c["id"]] = p.read_text()
        self.steps = int(lad.get("steps_per_session") or self.cfg["agent"]["steps_per_session"])

    # ------------------------------------------------------------ helpers
    def agents(self) -> list[tuple[str, str]]:
        """(agent_id, contestant_id) for every replicate."""
        reps = int(self.cfg["ladder"].get("replicates", 1))
        return [(f"{c['id']}_r{r + 1}", c["id"]) for c in self.cfg["ladder"]["contestants"] for r in range(reps)]

    def _done(self, key: str) -> dict | None:
        v = self.state["ladder"].get(key)
        return v if v and v.get("done") else None

    def _session(self, *, soul, notes, world, log_path, opening, meta) -> dict:
        _archive_partial(log_path)
        log = JsonlLog(log_path)
        try:
            res = run_session(
                cfg=self.cfg, client=self._client(seed=zlib.crc32(str(log_path).encode())), budget=self.budget,
                world=world, notes=notes, soul=soul, log=log, steps=self.steps, opening=opening, meta=meta,
            )
            log("notes_final", files=notes.dump())
            return res
        except BudgetExceeded as e:
            log("aborted", reason="budget", detail=str(e))
            self.stopped_reason = str(e)
            raise
        except Exception as e:
            log("aborted", reason="error", detail=repr(e), tb=traceback.format_exc())
            self.stopped_reason = f"{log_path}: {e!r}"
            raise
        finally:
            log.close()

    def _eval_opening(self, world: World) -> str:
        return self._opening(world, self.steps) + "\n\n" + self.cfg["ladder"]["eval_message"].strip()

    # ------------------------------------------------------------ the ladder
    def run(self, parallel: int) -> list[str]:
        """Run (or resume) the ladder. Returns the graduates, or [] if none (yet)."""
        survivors = [a for a, _ in self.agents()]
        contestant = dict(self.agents())
        for stage in self.cfg["ladder"]["stages"]:
            prior = self._done(f"stage/{stage['name']}")
            if prior:
                survivors = prior["advanced"]
                continue
            if not survivors or self.budget.stopped:
                break
            wcfg = stage_world_cfg(self.cfg["world"], stage)
            with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
                results = list(ex.map(lambda a: self._run_agent_stage(a, contestant[a], stage, wcfg), survivors))
            if self.budget.stopped or any(r is None for r in results):
                break
            advanced = [r["agent"] for r in results if r["advanced"]]
            self.mark("ladder", f"stage/{stage['name']}", {
                "done": True, "advanced": advanced, "eliminated": [a for a in survivors if a not in advanced],
                "results": results,
            })
            survivors = advanced
        else:
            if survivors and not self.budget.stopped and not self._done("graduation"):
                self._transfer_and_graduate(survivors, contestant)
        g = self._done("graduation")
        return g["graduates"] if g else []

    def _run_agent_stage(self, agent: str, cid: str, stage: dict, wcfg: dict) -> dict | None:
        soul = self.souls[cid]
        notes = Notes(self.root / "agents" / agent / "notes")
        snaps = self.root / "agents" / agent / "snapshots"
        sname = stage["name"]
        try:
            world = World(wcfg, seed=stage.get("world_seed"))
            for k in range(1, int(stage["free_sessions"]) + 1):
                key = f"free/{sname}/{agent}/{k}"
                if self._done(key):
                    continue
                snap = snaps / f"{sname}_free_{k:02d}_start"
                if snap.exists():
                    notes.restore(snap)  # re-running a crashed session
                else:
                    notes.snapshot(snap)
                res = self._session(
                    soul=soul, notes=notes, world=world,
                    log_path=self.root / "ladder" / sname / agent / f"free_{k:02d}.jsonl",
                    opening=self._opening(world, self.steps),
                    meta={"phase": "L", "stage": sname, "agent": agent, "contestant": cid, "session_kind": "free", "session": k},
                )
                self.mark("ladder", key, {"done": True, **res})
            per_seed = [self._eval_seed(agent, cid, stage, wcfg, seed, notes.root) for seed in stage["eval_seeds"]]
        except BudgetExceeded:
            return None
        min_seeds = int(stage["min_seeds"])
        passes = {t: sum(1 for s in per_seed if s["exploited"][t]) for t in stage["targets"]}
        mode = stage.get("advance", "all")
        ok = [passes[t] >= min_seeds for t in stage["targets"]]
        return {
            "agent": agent, "contestant": cid, "passes": passes, "min_seeds": min_seeds,
            "advanced": all(ok) if mode == "all" else any(ok),
            "eggs_found": sum(sum(s["fires"].values()) for s in per_seed),
        }

    def _eval_seed(self, agent, cid, stage, wcfg, seed, notes_src: Path, tag: str | None = None, group: str | None = None) -> dict:
        sname = stage["name"] if tag is None else "transfer"
        key = f"eval/{sname}/{agent}/{tag or ''}{seed}"
        prior = self._done(key)
        if prior:
            return prior["result"]
        base = self.root / "ladder" / sname / agent
        workdir = base / f"{tag or 'eval'}_{seed}_notes"
        if workdir.exists():
            shutil.rmtree(workdir)
        if notes_src is not None and Path(notes_src).exists():
            shutil.copytree(notes_src, workdir)
        notes = Notes(workdir)
        prior_text = _notes_text(workdir)
        world = World(wcfg, seed=int(seed))
        res = self._session(
            soul=self.souls[cid], notes=notes, world=world,
            log_path=base / f"{tag or 'eval'}_{seed}.jsonl", opening=self._eval_opening(world),
            meta={"phase": "L", "stage": sname, "agent": agent, "contestant": cid, "session_kind": tag or "eval", "seed": seed},
        )
        fires = {t: len(res["rule_fires"].get(t, [])) for t in stage["targets"]}
        result = {
            "agent": agent, "contestant": cid, "stage": stage["name"], "kind": tag or "eval", "group": group, "seed": seed,
            "fires": fires,
            "first_step": {t: (res["rule_fires"].get(t) or [None])[0] for t in stage["targets"]},
            "exploited": {t: fires[t] >= RULES[t].exploit_threshold for t in stage["targets"]},
            # did its notes already describe the rule before this session started?
            "prior_knowledge": {t: _articulates(t, prior_text) for t in stage["targets"]},
            "steps_used": res["steps_used"], "end_reason": res["end_reason"],
        }
        with self._lock, (self.root / "ladder_results.jsonl").open("a") as f:
            f.write(json.dumps(result) + "\n")
        self.mark("ladder", key, {"done": True, "result": result})
        return result

    # ------------------------------------------------------- after the top
    def _transfer_and_graduate(self, graduates: list[str], contestant: dict) -> None:
        stage = self.cfg["ladder"]["stages"][-1]
        wcfg = stage_world_cfg(self.cfg["world"], stage)
        transfer = {}
        if self.cfg["ladder"].get("transfer_check", True):
            try:
                for g in graduates:
                    src = self.root / "agents" / g / "notes"
                    w = [self._eval_seed(g, contestant[g], stage, wcfg, s, src, tag="with_notes", group="fresh+notes") for s in stage["eval_seeds"]]
                    e = [self._eval_seed(g, contestant[g], stage, wcfg, s, None, tag="empty", group="fresh") for s in stage["eval_seeds"]]
                    transfer[g] = {
                        "with_notes_exploited": sum(all(r["exploited"].values()) for r in w),
                        "empty_exploited": sum(all(r["exploited"].values()) for r in e),
                        "n_seeds": len(stage["eval_seeds"]),
                    }
            except BudgetExceeded:
                return
        for g in graduates:
            self._bundle(g, contestant[g], transfer.get(g))
        self.mark("ladder", "graduation", {"done": True, "graduates": graduates, "transfer": transfer})

    def _bundle(self, agent: str, cid: str, transfer: dict | None) -> None:
        out = self.root / "graduates" / agent
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        (out / "soul.md").write_text(self.souls[cid])
        shutil.copytree(self.root / "agents" / agent / "notes", out / "notes")
        stages = []
        for stage in self.cfg["ladder"]["stages"]:
            st = self.state["ladder"].get(f"stage/{stage['name']}", {})
            mine = next((r for r in st.get("results", []) if r["agent"] == agent), None)
            evals = [v["result"] for k, v in self.state["ladder"].items() if k.startswith(f"eval/{stage['name']}/{agent}/")]
            stages.append({"stage": stage["name"], "targets": stage["targets"], "summary": mine, "evals": evals,
                           "logs": f"ladder/{stage['name']}/{agent}/"})
        trace = {"agent": agent, "contestant": cid, "model": self.cfg["agent"]["model"], "stages": stages,
                 "notes_transfer": transfer, "spend_usd_whole_run": round(self.budget.spent, 4)}
        (out / "trace.json").write_text(json.dumps(trace, indent=1))
        (out / "REVIEW_REQUIRED.md").write_text(REVIEW_TEXT)


def ladder_summary(root: Path) -> str:
    """Markdown summary of a ladder run."""
    root = Path(root)
    state = json.loads((root / "state.json").read_text()).get("ladder", {})
    import yaml

    cfg = yaml.safe_load((root / "config.yaml").read_text())
    L = [f"# Ladder `{root.name}`", ""]
    if cfg.get("_mock"):
        L += ["> **Mock run**: scripted agent, not Claude.", ""]
    for stage in cfg["ladder"]["stages"]:
        st = state.get(f"stage/{stage['name']}")
        L += [f"## {stage['name']}: targets {', '.join(stage['targets'])} (need ≥{stage['min_seeds']} of {len(stage['eval_seeds'])} seeds)", ""]
        if not st:
            L += ["Not run (no survivors yet, or stopped by the cost cap).", ""]
            continue
        L += ["| Agent | Soul | Seeds exploited per target | Hidden-rule firings in eval | Result |", "|---|---|---|---|---|"]
        for r in st["results"]:
            L.append(f"| {r['agent']} | {r['contestant']} | {', '.join(f'{t}: {n}' for t, n in r['passes'].items())} | {r['eggs_found']} | "
                     f"{'advanced' if r['advanced'] else 'eliminated'} |")
        L.append("")
    by_soul: dict[str, list[int]] = {}
    for stage in cfg["ladder"]["stages"]:
        for r in (state.get(f"stage/{stage['name']}") or {}).get("results", []):
            by_soul.setdefault(r["contestant"], []).append(int(r["advanced"]))
    if by_soul:
        L += ["## By soul", "", "| Soul | Stage passes / attempts |", "|---|---|"]
        L += [f"| {s} | {sum(v)} / {len(v)} |" for s, v in sorted(by_soul.items())]
        L.append("")
    g = state.get("graduation")
    if g:
        L += ["## Graduates", ""]
        for a in g["graduates"]:
            t = g["transfer"].get(a)
            L.append(f"- **{a}**: bundle in `graduates/{a}/` (review required)"
                     + (f"; notes transfer: fresh copy with its notes cleared the final stage in {t['with_notes_exploited']}/{t['n_seeds']} seeds,"
                        f" fresh copy with empty notes in {t['empty_exploited']}/{t['n_seeds']}" if t else ""))
        L.append("")
    else:
        L += ["No graduates yet.", ""]
    return "\n".join(L)

