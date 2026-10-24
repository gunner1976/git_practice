"""Rank agents on the traits that get an EKOnian to the moon: persistence first, then curiosity
and innovation, with verified reasoning as the gate.

Everything is measured from what the agents did, across all their free-play days:

persistence (weight 0.5)
  retry       after a failed action, how often the agent tried the same kind of action again
              with different inputs within its next few actions (instead of giving up)
  pursuit     of the open questions it wrote down (hypotheses in its notes), the share it kept
              working on until they were revised or confirmed on a later day or later in the day
  stamina     how well its activity held up: world actions on its later days relative to its
              first, and the share of turns not spent idle
curiosity (weight 0.25)
  ground covered (2 m cells visited), different objects handled, sky observations made at night,
  and new questions (hypotheses) raised per day
innovation (weight 0.25)
  rules it wrote down that no other agent in the run wrote anything similar to

Each component is scaled to 0-1 across the agents in the run (so scores rank within a run).
An agent promoted for verified reasoning (promotions.json) has its total multiplied by 1.5.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np

from .load import events, phase_a_sessions
from .rules import _sim, rules_by_agent

WEIGHTS = {"persistence": 0.5, "curiosity": 0.25, "innovation": 0.25}
REASONING_BONUS = 1.5


def _failed(e: dict) -> bool:
    if e.get("error"):
        return True
    try:
        return "Failed" in json.loads(e["result"]).get("lastActionResult", "")
    except (ValueError, TypeError, AttributeError):
        return False


def _raw(root: Path, data: dict) -> dict[str, dict]:
    rules = rules_by_agent(data)
    out = {}
    for agent, items in phase_a_sessions(root).items():
        acts_per_day, idle, turns, fails, retries, cells, objects, sky_night, hyps = [], 0, 0, 0, 0, set(), set(), 0, 0
        for _, p in items:
            log = events(p)
            if not any(e["kind"] == "session_end" for e in log):
                continue
            acts = [e for e in log if e["kind"] == "action"]
            acts_per_day.append(len(acts))
            idle += sum(1 for e in log if e["kind"] == "stop_hook")
            turns += sum(1 for e in log if e["kind"] == "assistant")
            for i, a in enumerate(acts):
                if _failed(a):
                    fails += 1
                    nxt = acts[i + 1:i + 5]
                    if any(b["name"] == a["name"] and b["input"] != a["input"] for b in nxt):
                        retries += 1
                if a["name"] == "pickup" and not _failed(a):
                    try:
                        objects.add(json.loads(a["result"])["player"]["holding"])
                    except (ValueError, KeyError, TypeError):
                        pass
                try:
                    pos = json.loads(a["result"])["player"]["position"]
                    cells.add((round(pos[0] / 2), round(pos[2] / 2)))
                except (ValueError, KeyError, TypeError):
                    pass
            for e in log:
                if e["kind"] == "tool_call" and e["name"] == "observe":
                    try:
                        if json.loads(e["result"]).get("sky", {}).get("daylight") == "night":
                            sky_night += 1
                    except (ValueError, TypeError, AttributeError):
                        pass
        rl = rules.get(f"{data.get('run')}|{agent}", [])
        hyp = [r for r in rl if r["kind"] == "hypothesis"]
        pursued = sum(1 for r in hyp if len(r["versions"]) > 1 or (r["dropped"] and r["dropped"]["s"] > r["versions"][0]["s"]))
        days = max(1, len(acts_per_day))
        out[agent] = {
            "days": len(acts_per_day),
            "retry": retries / fails if fails else 0.5,
            "pursuit": pursued / len(hyp) if hyp else 0.0,
            "stamina": 0.5 * (min(1.5, np.mean(acts_per_day[1:]) / max(1, acts_per_day[0])) / 1.5 if len(acts_per_day) > 1 else 0.5) + 0.5 * (1 - idle / max(1, turns)),
            "ground": len(cells), "objects": len(objects), "night_sky_looks": sky_night, "questions_per_day": len(hyp) / days,
            "rules": [r["versions"][-1]["text"] for r in rl],
            "fails": fails, "retries": retries, "hypotheses": len(hyp), "pursued": pursued, "idle_share": idle / max(1, turns),
        }
    # innovation: rules nobody else wrote anything similar to
    for a, r in out.items():
        others = [t for b, rb in out.items() if b != a for t in rb["rules"]]
        r["unique_rules"] = sum(1 for t in r["rules"] if not any(_sim(t, o) >= 0.5 for o in others))
    return out


def _scale(vals: list[float]) -> list[float]:
    lo, hi = min(vals), max(vals)
    return [0.5 if hi - lo < 1e-9 else (v - lo) / (hi - lo) for v in vals]


def trait_report(root: Path) -> Path:
    from .replay import build

    root = Path(root)
    data = build(root)
    raw = _raw(root, data)
    agents = sorted(raw)
    if not agents:
        raise ValueError("no completed free-play days in this run")
    col = lambda k: _scale([float(raw[a][k]) for a in agents])  # noqa: E731
    retry, pursuit, stamina = col("retry"), col("pursuit"), col("stamina")
    ground, objects, night, quest = col("ground"), col("objects"), col("night_sky_looks"), col("questions_per_day")
    innov = col("unique_rules")
    promos = {}
    pp = root / "promotions.json"
    if pp.exists():
        promos = {a: r for a, r in json.loads(pp.read_text())["agents"].items() if r.get("promoted")}
    rows = []
    for i, a in enumerate(agents):
        pers = (retry[i] + pursuit[i] + stamina[i]) / 3
        cur = (ground[i] + objects[i] + night[i] + quest[i]) / 4
        inn = innov[i]
        total = WEIGHTS["persistence"] * pers + WEIGHTS["curiosity"] * cur + WEIGHTS["innovation"] * inn
        if a in promos:
            total *= REASONING_BONUS
        rows.append({"agent": a, "total": total, "persistence": pers, "curiosity": cur, "innovation": inn, "promoted": a in promos, **raw[a]})
    rows.sort(key=lambda r: -r["total"])
    lines = [f"# Traits: `{root.name}`", "",
             "Ranked on persistence (x0.5), curiosity (x0.25) and innovation (x0.25), each scaled 0-1 within this run; "
             f"a promotion for verified reasoning multiplies the total by {REASONING_BONUS}.", "",
             "| rank | agent | total | persistence | curiosity | innovation | reasoning | retried after failure | questions pursued | idle share | ground cells | night-sky looks | unique rules |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in enumerate(rows, 1):
        lines.append(f"| {k} | {r['agent']} | {r['total']:.2f} | {r['persistence']:.2f} | {r['curiosity']:.2f} | {r['innovation']:.2f} | "
                     f"{'promoted' if r['promoted'] else ''} | {r['retries']}/{r['fails']} | {r['pursued']}/{r['hypotheses']} | {r['idle_share']:.0%} | "
                     f"{r['ground']} | {r['night_sky_looks']} | {r['unique_rules']} |")
    (root / "traits.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "rules"} for r in rows], indent=1))
    p = root / "traits.md"
    p.write_text("\n".join(lines) + "\n")
    return p
