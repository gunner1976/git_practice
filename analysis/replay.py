"""Rebuild every session of a run frame by frame for the replay viewer.

The world is deterministic, so feeding each logged action back through `World`
reproduces the island exactly; every replayed result is checked against the
logged one and the first mismatch (if any) is reported with the session.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import yaml

from agent.tools import run_world_tool
from world import World, make_world
from world.island import HAND_HEIGHT

from .load import events, phase_a_sessions, phase_b_logs
from .rules import rules_by_agent

GRID = 128  # heightmap samples per side


def _r(v: float) -> float:
    return round(float(v), 2)


class _Tracing:
    """Mixin for a world that keeps a coarse sample of each throw's flight for drawing."""

    def _fly(self, o, vel):
        x0, y0, z0 = o.x, o.y, o.z
        ix, iy, iz = super()._fly(o, vel)
        g = float(self.phys["gravity"])
        total = math.hypot(ix - x0, iy - y0)
        hv = math.hypot(vel[0], vel[1])
        path = [[_r(x0), _r(y0), _r(z0)]]
        if hv > 1e-6 and total > 0.05:
            tend = total / hv
            for i in range(1, 12):
                t = tend * i / 12
                path.append([_r(x0 + vel[0] * t), _r(y0 + vel[1] * t), _r(z0 + vel[2] * t - 0.5 * g * t * t)])
        else:  # straight up (or nearly): show the rise and fall in place
            tup = max(vel[2], 0.0) / g
            path.append([_r(x0), _r(y0), _r(z0 + 0.5 * g * tup * tup)])
        path.append([_r(ix), _r(iy), _r(iz)])
        self.last_flight = path
        return ix, iy, iz


def _snapshot(w: World) -> dict:
    a = w.avatar
    return {
        "a": [_r(a.x), _r(a.y), _r(a.z), a.holding],
        "o": {o.id: [_r(o.x), _r(o.y), _r(o.z), int(o.held)] for o in w.objects.values()},
    }


def _objects_meta(w: World) -> dict:
    return {o.id: [o.shape, o.colour, _r(o.sx), _r(o.sy), _r(o.sz)] for o in w.objects.values()}


def terrain_grid(w: World) -> dict:
    n, size = GRID, w.size
    rows = []
    for j in range(n):
        y = (j + 0.5) * size / n
        rows.append([round(w.terrain.height((i + 0.5) * size / n, y), 2) for i in range(n)])
    px, py, pz = w.terrain.peak_summit
    sx, sy, sz = w.terrain.spire_summit
    return {
        "n": n, "size": size, "h": rows,
        "sea": float(w.cfg["sea_level"]), "wade": float(w.cfg["sea_level"]) - float(w.cfg["max_wade_depth"]),
        "peak": [_r(px), _r(py), _r(pz)], "spire": [_r(sx), _r(sy), _r(sz), _r(w.terrain.spire_radius)],
    }


def replay_session(path: Path, wcfg: dict, notes_start: dict[str, str]) -> dict:
    recs = events(path)
    start = next(r for r in recs if r["kind"] == "session_start")
    base = type(make_world(wcfg, seed=start.get("world_seed")))
    w = type("Tracing" + base.__name__, (_Tracing, base), {})(wcfg, seed=start.get("world_seed"))
    w.reset()
    if start.get("start_state"):  # a persistent world: start from how the previous day ended
        w.set_state(start["start_state"])
    meta = _objects_meta(w)
    frames = [{"step": 0, **_snapshot(w)}]
    timeline: list[dict] = []
    notes = dict(notes_start)
    diverged = None
    end = {}
    cost = 0.0
    for r in recs:
        k = r["kind"]
        fi = len(frames) - 1
        if k == "assistant":
            cost += float(r.get("cost_usd") or 0.0)
            for c in r.get("content", []):
                if c.get("type") == "text" and c.get("text", "").strip():
                    timeline.append({"f": fi, "k": "say", "t": c["text"].strip()})
                elif c.get("type") == "thinking" and c.get("thinking", "").strip():
                    timeline.append({"f": fi, "k": "think", "t": c["thinking"].strip()})
        elif k == "action":
            msg, err = run_world_tool(w, r["name"], r["input"])
            w.drain_events()
            if diverged is None and msg != r["result"]:
                diverged = {"step": r["step"], "logged": r["result"], "replayed": msg}
            fr = {"step": r["step"], **_snapshot(w)}
            if "clock" in r:
                fr["c"] = r["clock"]
            if r["name"] == "throw" and not err and getattr(w, "last_flight", None):
                thrown = r["input"].get("id") or next((e["id"] for e in r.get("events", []) if e.get("type") == "landed"), None)
                fr["fly"] = [thrown, w.last_flight]
                w.last_flight = None
            spawns = [e["id"] for e in r.get("events", []) if e.get("type") in ("spawn", "egg")]
            if spawns:
                fr["spawn"] = spawns
                for oid in spawns:
                    if oid in w.objects:
                        meta[oid] = _objects_meta(w)[oid]
            frames.append(fr)
            timeline.append({"f": len(frames) - 1, "k": "act", "t": f"{r['name']}({_args(r['input'])})", "r": r["result"], "e": int(bool(r["error"]))})
            for e in r.get("events", []):
                if e.get("hidden_rule"):
                    timeline.append({"f": len(frames) - 1, "k": "rule", "t": e.get("rule", "hidden rule"), "id": e.get("id")})
        elif k == "tool_call":
            if r["name"] in ("write_note", "append_note") and not r.get("error"):
                p, content = r["input"].get("path"), r["input"].get("content", "")
                if r["name"] == "append_note":
                    old = notes.get(p, "")
                    content_full = old + ("" if not old or old.endswith("\n") else "\n") + content
                else:
                    content_full = content
                notes[p] = content_full
                timeline.append({"f": fi, "k": "note", "p": p, "t": content, **({"append": 1} if r["name"] == "append_note" else {})})
            elif r["name"] == "calculate":
                timeline.append({"f": fi, "k": "calc", "t": r["input"].get("expression", ""), "r": r["result"], "e": int(bool(r.get("error")))})
            elif r["name"] == "answer" and not r.get("error"):
                inp = r["input"]
                timeline.append({"f": fi, "k": "answer", "t": f"{inp.get('value')} {inp.get('units', '')}".strip(), "r": inp.get("explanation", "")})
            elif r["name"] == "read_note":
                timeline.append({"f": fi, "k": "read", "p": r["input"].get("path")})
        elif k == "stop_hook":
            timeline.append({"f": fi, "k": "nudge", "n": r.get("n")})
        elif k == "score":
            end["score"] = r.get("score")
        elif k == "session_end":
            end.update(reason=r.get("reason"), steps=r.get("steps_used"), calls=r.get("api_calls"), clock=r.get("clock_seconds"))
        elif k == "notes_final":
            notes = r.get("files", notes)
    return {
        "opening": start.get("opening", ""), "objects": meta, "frames": frames, "timeline": timeline,
        "notes_start": notes_start, "end": end, "cost": round(cost, 4), "diverged": diverged,
        "clock": (end.get("clock") or None),
        "final_notes": notes,
    }


def _args(d: dict) -> str:
    parts = []
    for k, v in d.items():
        parts.append(f"{k}={json.dumps(v) if not isinstance(v, str) else v}")
    return ", ".join(parts)


def build(root: Path) -> dict:
    root = Path(root)
    cfg = yaml.safe_load((root / "config.yaml").read_text())
    wcfg = cfg["world"]
    sessions = []
    end_notes: dict[str, dict] = {}
    for agent, items in phase_a_sessions(root).items():
        notes: dict[str, str] = {}
        for k, p in items:
            s = replay_session(p, wcfg, notes)
            notes = s.pop("final_notes")
            sessions.append({"id": f"{agent}/A{k:02d}", "agent": agent, "phase": "A", "label": f"Day {k}", **s})
        end_notes[agent] = notes
    tasks = cfg.get("phase_b", {}).get("tasks", {})
    for agent, task, p in phase_b_logs(root):
        s = replay_session(p, wcfg, end_notes.get(agent, {}) if agent.startswith("agent_") else {})
        s.pop("final_notes")
        sessions.append({"id": f"{agent}/{task}", "agent": agent, "phase": "B", "label": task, "task": tasks.get(task, ""), **s})
    w = make_world(wcfg)
    clk = cfg.get("agent", {}).get("clock")
    return {"run": root.name, "terrain": terrain_grid(w), "hand": HAND_HEIGHT, "sessions": sessions,
            "session_seconds": float(clk["session_seconds"]) if clk else None}


def build_many(roots: list[Path]) -> dict:
    """Several runs of the same island in one viewer, with a run picker."""
    parts = [build(r) for r in roots]
    first = parts[0]
    runs, sessions, promos = [], [], {}
    for root, d in zip(roots, parts):
        if (d["terrain"]["size"], d["terrain"]["n"]) != (first["terrain"]["size"], first["terrain"]["n"]):
            raise ValueError(f"{Path(root).name} uses a different map size; give it its own viewer")
        cfg = yaml.safe_load((Path(root) / "config.yaml").read_text())
        kind = "paper free play" if cfg.get("agent", {}).get("interface") == "paper" else ("pilot" if d["run"].startswith("pilot") else "replication")
        runs.append({"run": d["run"], "kind": kind, "session_seconds": d["session_seconds"], "sessions": len(d["sessions"])})
        for s in d["sessions"]:
            sessions.append({**s, "run": d["run"], "session_seconds": d["session_seconds"], "full_day": bool(cfg.get("world", {}).get("eko"))})
        pp = Path(root) / "promotions.json"
        if pp.exists():
            for agent, r in json.loads(pp.read_text())["agents"].items():
                if r.get("promoted"):
                    promos[f"{d['run']}|{agent}"] = {"day": r["verdict"].get("day"), "step": r["verdict"].get("step"),
                                                     "quote": r["verdict"].get("quote", ""), "evidence": r["verdict"].get("evidence", "")}
    terrains = {d["run"]: d["terrain"] for d in parts[1:] if d["terrain"] != first["terrain"]}  # runs on a different island
    return {"run": first["run"], "runs": runs, "terrain": first["terrain"], "terrains": terrains, "hand": first["hand"],
            "sessions": sessions, "session_seconds": None, "promotions": promos}


def write_viewer(root: Path, include: list[Path] | None = None):
    """Writes viewer.html (3D island with a 2D map toggle, field log, rules and notes)
    into the run directory; `include` adds other runs of the same island."""
    data = build_many([Path(root), *[Path(p) for p in (include or [])]])
    data["rules"] = rules_by_agent(data)
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    tpl = Path(__file__).with_name("viewer.html").read_text()
    out = Path(root) / "viewer.html"
    out.write_text(tpl.replace("/*__DATA__*/null", blob))
    outs = [out]
    bad = [(s["id"], s["diverged"]) for s in data["sessions"] if s["diverged"]]
    return outs, len(data["sessions"]), bad
