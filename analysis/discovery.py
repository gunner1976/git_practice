"""Did each agent discover the hidden rock-spawn rule, and when?

Three levels, each with the (session, step) it first happened:
  exposed     - the rule fired at least once (a hard rock throw), noticed or not
  articulated - the agent wrote about the rock making / spawning cubes, in notes or speech
  exploited   - the rule fired >= 3 times within one session (deliberate use)
"""

from __future__ import annotations

import re
from pathlib import Path

from .load import events, phase_a_sessions, phase_b_logs

ROCK = re.compile(r"\brock\b", re.I)
CUBE = re.compile(r"\b(cube|block|box)e?s?\b", re.I)
MAKE = re.compile(r"\b(spawn\w*|appear\w*|creat\w*|produc\w*|generat\w*|new|make[s]?|made|summon\w*|multipl\w*|birth\w*|materiali[sz]\w*)\b", re.I)


def mentions_rule(text: str) -> bool:
    for sent in re.split(r"(?<=[.!?\n])", text):
        if ROCK.search(sent) and CUBE.search(sent) and MAKE.search(sent):
            return True
    return False


def _added(diff: str) -> str:
    return "\n".join(l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))


def scan_log(path: Path, rule: str = "rock_spawn") -> dict:
    """First firing steps of one hidden rule in a session log, and the first time
    after that the agent described it. The rock rule uses the rock/cube/make
    sentence test; egg rules use their own `keywords` regex from world/rules.py."""
    from world.rules import RULES

    describes = mentions_rule if rule == "rock_spawn" else (lambda t: bool(RULES[rule].keywords.search(t)))
    fired: list[int] = []
    articulated = None
    for e in events(path):
        if e["kind"] == "hidden_rule_fired":
            if e["event"].get("rule", "rock_spawn") == rule:
                fired.append(e["step"])
        elif articulated is None and fired:
            text = ""
            if e["kind"] == "notes_diff":
                text = _added(e["diff"])
            elif e["kind"] == "assistant":
                text = " ".join(c.get("text", "") or c.get("thinking", "") for c in e["content"] if c["type"] in ("text", "thinking"))
            if text and describes(text):
                articulated = {"step": e.get("step"), "where": "notes" if e["kind"] == "notes_diff" else "speech", "excerpt": text.strip()[:300]}
    return {"fired_steps": fired, "articulated": articulated}


def discovery(root: Path) -> dict[str, dict]:
    out = {}
    for agent, sessions in phase_a_sessions(root).items():
        rec = {"exposed": None, "articulated": None, "exploited": None, "fires_per_session": {}}
        for k, path in sessions:
            s = scan_log(path)
            rec["fires_per_session"][k] = len(s["fired_steps"])
            if s["fired_steps"] and rec["exposed"] is None:
                rec["exposed"] = {"session": k, "step": s["fired_steps"][0]}
            if s["articulated"] and rec["articulated"] is None:
                rec["articulated"] = {"session": k, **s["articulated"]}
            if len(s["fired_steps"]) >= 3 and rec["exploited"] is None:
                rec["exploited"] = {"session": k, "step": s["fired_steps"][2]}
        out[agent] = rec
    return out


def eval_spawns(root: Path) -> dict[str, int]:
    """Hidden-rule firings in each agent's make_cubes evaluation session."""
    out = {}
    for agent, task, path in phase_b_logs(root):
        if task == "make_cubes":
            out[agent] = sum(1 for e in events(path) if e["kind"] == "hidden_rule_fired" and e["event"].get("rule", "rock_spawn") == "rock_spawn")
    return out
