"""Phase A (free play), Phase B (evaluation) and the pilot, with resumable state.

Run directory layout (runs/<run_id>/):
  config.yaml, soul.md          snapshots of what the run was started with
  state.json                    which sessions / eval jobs are complete
  ledger.jsonl                  one line per API call: usage and USD cost
  agents/<agent>/notes/         the agent's live long-term memory
  agents/<agent>/snapshots/     notes as they were at the start of each session
  phase_a/<agent>/session_NN.jsonl
  phase_b/<agent>/<task>.jsonl, phase_b/<agent>/<task>_notes/
  eval_results.jsonl

The unit of resumption is a session: a session that crashed (or hit the cost
cap) part-way is re-run from scratch after restoring the notes it started with.
Money spent on the aborted attempt stays in the ledger and counts against --max-usd.
"""

from __future__ import annotations

import copy
import json
import shutil
import threading
import traceback
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from world import World, make_world, score

from .client import make_client
from .cost import Budget, BudgetExceeded
from .loop import JsonlLog, run_session
from .notes import Notes


class Run:
    def __init__(self, root: Path, cfg: dict, soul: str, max_usd: float, mock: bool = False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        cfg_file, soul_file = self.root / "config.yaml", self.root / "soul.md"
        if cfg_file.exists():  # resuming: the run keeps the config and soul it started with
            cfg = yaml.safe_load(cfg_file.read_text())
            soul = soul_file.read_text()
            mock = cfg.get("_mock", False)
        else:
            cfg = copy.deepcopy(cfg)
            cfg["_mock"] = mock
            cfg_file.write_text(yaml.safe_dump(cfg, sort_keys=False))
            soul_file.write_text(soul)
        self.cfg, self.soul, self.mock = cfg, soul, mock
        self.base_dir = Path(__file__).resolve().parents[1]
        pricing = dict(cfg["pricing"])
        if mock:
            pricing["mock"] = pricing[cfg["agent"]["model"]]
        self.budget = Budget(max_usd, self.root / "ledger.jsonl", pricing)
        self._lock = threading.Lock()
        self.state_path = self.root / "state.json"
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {"phase_a": {}, "phase_b": {}}
        self.stopped_reason: str | None = None
        self.board = None   # the phone switchboard (world/phone.py), when the mission reward is a phone
        self.dawn = None    # optional (agent, session) -> text added to that day's opening (agent/cosmos.py)
        self.soul_for = None  # optional agent -> its own system prompt (agent/cosmos.py: its name)

    # -------------------------------------------------------------- state io
    def _save(self) -> None:
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1))
        tmp.replace(self.state_path)

    def mark(self, phase: str, key: str, value) -> None:
        with self._lock:
            self.state[phase][key] = value
            self._save()

    def set_meta(self, **kw) -> None:
        with self._lock:
            self.state.setdefault("meta", {}).update(kw)
            self._save()

    def _client(self, seed: int):
        return make_client(self.cfg, self.mock, seed=seed)

    def _world(self, seed: int | None = None) -> World:
        return make_world(self.cfg["world"], seed=seed)

    # --------------------------------------------------------------- phase A
    def phase_a(self, n_agents: int, n_sessions: int, steps: int, parallel: int) -> None:
        self.set_meta(phase_a={"n_agents": n_agents, "n_sessions": n_sessions, "steps": steps})
        agents = [f"agent_{i + 1}" for i in range(n_agents)]
        self.free_play(agents, n_sessions, steps, parallel)

    def free_play(self, agents: list[str], n_sessions: int | dict, steps: int, parallel: int, pair_order: list[str] | None = None) -> None:
        """Each named agent plays up to day `n_sessions` (or its own entry, if a dict); days already
        done are skipped. Phone partners are paired in the order of `pair_order` (default `agents`)."""
        if (self.cfg["world"].get("mission") or {}).get("reward") == "phone":
            from world.phone import Switchboard

            # calls are live, so both ends of every pair must be running at the same time
            self.board = Switchboard(pair_order or agents, ring_seconds=float(self.cfg["world"]["mission"].get("ring_seconds", 120)))
            parallel = len(agents)
        upto = n_sessions if isinstance(n_sessions, dict) else {a: n_sessions for a in agents}
        with ThreadPoolExecutor(max_workers=max(1, min(parallel, len(agents)))) as ex:
            list(ex.map(lambda ag: self._agent_free_play(ag, upto[ag], steps), agents))

    def _agent_free_play(self, agent: str, n_sessions: int, steps: int) -> None:
        notes = Notes(self.root / "agents" / agent / "notes")
        snaps = self.root / "agents" / agent / "snapshots"
        tpl = self.cfg["agent"].get("workspace_template")
        if tpl and not notes.list() and not (snaps / "session_01_start").exists():
            # paper App. A.2-A.3: SOUL.md and the two memory-file headers are there on day one
            src = Path(tpl) if Path(tpl).is_absolute() else self.base_dir / tpl
            for f in sorted(src.iterdir()):
                if f.is_file():
                    notes.write(f.name, f.read_text())
        client = self._client(seed=zlib.crc32(agent.encode()))
        world = self._world()
        board = self.board
        if board is not None:
            board.attach(agent, world)
        for k in range(1, n_sessions + 1):
            key = f"{agent}/{k}"
            if self.state["phase_a"].get(key, {}).get("done"):
                continue
            if self.budget.stopped:
                return
            snap = snaps / f"session_{k:02d}_start"
            if snap.exists():
                notes.restore(snap)  # re-running a crashed session: undo its partial notes
            else:
                notes.snapshot(snap)
            log_path = self.root / "phase_a" / agent / f"session_{k:02d}.jsonl"
            _archive_partial(log_path)
            log = JsonlLog(log_path)
            opening = self._opening(world, steps, session=k)
            extra = self.dawn(agent, k) if self.dawn else None
            if extra:
                opening += "\n\n" + extra.strip()
            wdir = self.root / "agents" / agent / "world"
            start_state = None
            if self.cfg["world"].get("persist") and k > 1:
                prev = wdir / f"session_{k - 1:02d}_end.json"
                start_state = json.loads(prev.read_text()) if prev.exists() else None
            ach_path = self.root / "agents" / agent / "achievements.json"
            if hasattr(world, "achievements"):  # mission trials carry over between days
                world.achievements = json.loads(ach_path.read_text()) if ach_path.exists() else {}
            meta = {"phase": "A", "agent": agent, "session": k}
            eko_path = self.root / "agents" / agent / "eko_clock.json"
            if getattr(world, "eko", None) is not None and eko_path.exists():
                # EKO time carries on: wake at the first dawn after the last session ended
                meta["eko_start_tau"] = world.eko.next_dawn(json.loads(eko_path.read_text())["tau"])
            if board is not None:
                board.start(agent)
            try:
                res = run_session(
                    cfg=self.cfg, client=client, budget=self.budget, world=world, notes=notes, soul=self.soul_for(agent) if self.soul_for else self.soul,
                    log=log, steps=steps, opening=opening, meta=meta,
                    start_state=start_state,
                )
                if getattr(world, "mission", None):
                    ach_path.write_text(json.dumps(world.achievements))
                if "eko_tau_end" in res:
                    e = world.eko
                    eko_path.write_text(json.dumps({"tau": res["eko_tau_end"], "eko_day": int((res["eko_tau_end"] - e.day / 4) // e.day) + 1}))
                if self.cfg["world"].get("persist"):
                    wdir.mkdir(parents=True, exist_ok=True)
                    (wdir / f"session_{k:02d}_end.json").write_text(json.dumps(world.state()))
                log("notes_final", files=notes.dump())
                self.mark("phase_a", key, {"done": True, **res})
            except BudgetExceeded as e:
                log("aborted", reason="budget", detail=str(e))
                self.stopped_reason = str(e)
                return
            except Exception as e:  # noqa: BLE001 - logged, session left incomplete for resume
                log("aborted", reason="error", detail=repr(e), tb=traceback.format_exc())
                self.stopped_reason = f"{agent} session {k}: {e!r}"
                raise
            finally:
                if board is not None:
                    board.stop(agent)
                log.close()

    def _opening(self, world: World, steps: int, task: str | None = None, session: int | None = None) -> str:
        a = self.cfg["agent"]
        lm = world.landmarks_text() if a["describe_landmarks"] else ""
        text = a["session_start_message"].format(landmarks=lm, steps=steps).strip()
        ch = a.get("challenge")
        if ch and session is not None and (not ch.get("days") or session in ch["days"]):
            text += "\n\n" + ch["message"].strip()
        if task:
            text += "\n\n" + self.cfg["phase_b"]["task_message"].format(task=task, steps=steps).strip()
        return text

    # --------------------------------------------------------------- phase B
    def phase_b(self, parallel: int) -> None:
        pa = self.state.get("meta", {}).get("phase_a", {})
        n_vet = int(pa.get("n_agents", self.cfg["phase_a"]["n_agents"]))
        pb = self.cfg["phase_b"]
        n_fresh = int(pb["n_fresh"] or n_vet)
        steps = int(pb["steps_per_task"] or pa.get("steps") or self.cfg["agent"]["steps_per_session"])
        seed = pb["world_seed"] if pb["world_seed"] is not None else self.cfg["world"]["seed"]
        jobs = [(f"agent_{i + 1}", "veteran", t) for i in range(n_vet) for t in pb["tasks"]]
        jobs += [(f"fresh_{i + 1}", "fresh", t) for i in range(n_fresh) for t in pb["tasks"]]
        self.set_meta(phase_b={"n_veterans": n_vet, "n_fresh": n_fresh, "steps": steps, "world_seed": seed})
        with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
            list(ex.map(lambda j: self._eval_job(*j, steps=steps, seed=seed), jobs))

    def _eval_job(self, agent: str, group: str, task: str, steps: int, seed: int) -> None:
        key = f"{agent}/{task}"
        if self.state["phase_b"].get(key, {}).get("done") or self.budget.stopped:
            return
        workdir = self.root / "phase_b" / agent / f"{task}_notes"
        if workdir.exists():
            shutil.rmtree(workdir)
        src = self.root / "agents" / agent / "notes"
        if group == "veteran" and src.exists():
            shutil.copytree(src, workdir)  # each task starts from the end-of-Phase-A memory
        notes = Notes(workdir)
        world = self._world(seed)
        log_path = self.root / "phase_b" / agent / f"{task}.jsonl"
        _archive_partial(log_path)
        log = JsonlLog(log_path)
        try:
            res = run_session(
                cfg=self.cfg, client=self._client(seed=zlib.crc32(key.encode())), budget=self.budget, world=world, notes=notes,
                soul=self.soul, log=log, steps=steps, opening=self._opening(world, steps, self.cfg["phase_b"]["tasks"][task]),
                meta={"phase": "B", "agent": agent, "group": group, "task": task},
            )
            sc = score(task, world)
            log("score", task=task, **sc)
            rec = {"agent": agent, "group": group, "task": task, "seed": seed, **sc, **res}
            with self._lock, (self.root / "eval_results.jsonl").open("a") as f:
                f.write(json.dumps(rec) + "\n")
            self.mark("phase_b", key, {"done": True, "score": sc["score"]})
        except BudgetExceeded as e:
            log("aborted", reason="budget", detail=str(e))
            self.stopped_reason = str(e)
        except Exception as e:  # noqa: BLE001
            log("aborted", reason="error", detail=repr(e), tb=traceback.format_exc())
            self.stopped_reason = f"{key}: {e!r}"
            raise
        finally:
            log.close()


def _archive_partial(path: Path) -> None:
    if path.exists():
        i = 1
        while path.with_suffix(f".crashed{i}.jsonl").exists():
            i += 1
        path.rename(path.with_suffix(f".crashed{i}.jsonl"))


def eval_results(root: Path) -> list[dict]:
    """Latest result per (agent, task); tolerant of duplicates from resumed runs."""
    p = Path(root) / "eval_results.jsonl"
    out: dict[tuple, dict] = {}
    if p.exists():
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[(r["agent"], r["task"])] = r
    return list(out.values())
