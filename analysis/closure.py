"""Premature closure: when an agent declares something impossible, did it earn that verdict?

Humans keep overturning "impossible" because someone measures, reasons and tries again. An agent
that closes a question on a hunch, writes the verdict into its memory as a rule, and never looks
at it again has stopped doing science. For every goal an agent declared out of reach, this reads
its speech, thinking and notes for:

  closed      the first passage declaring it impossible / out of reach / not worth trying
  grounded    before closing, it put a number on the goal itself (how far, how big, how high) or
              ran a calculation about it - not only on its own abilities
  approaches  how many different kinds of action it tried between first raising the goal and
              closing it
  locked in   the verdict went into its notes (a rule its later selves will obey)
  reopened    on a later day, it took the question up again: a plan, an idea, a measurement or a
              test about achieving that goal (reaching, climbing, how far) that is neither another verdict of impossibility nor a refusal
              ("no new idea", "don't re-test"); carrying on the same day doesn't count
  restated    how many later passages only repeat the verdict

A goal can be closed, reopened and closed again; each closing starts an episode. Openness, a part
of persistence (analysis/traits.py), is scored per episode and averaged:
reopened 1.0; otherwise grounded 0.5, ungrounded 0.0; minus 0.25 if locked into notes (not below 0).
A closure made on the agent's last day so far is pending (it has had no chance to reopen) and is
not scored. An agent with nothing closed (or only pending closures) scores 1.0.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .load import events, phase_a_sessions

CLOSE = re.compile(
    r"\b(impossible|infeasible|unreachable|out of (?:my )?reach|can(?:no|')t (?:be )?reach(?:ed)?|no way (?:to|of)|"
    r"give up|gave up|giving up|stop grinding|not (?:keep )?grinding|not worth|pointless|futile|far beyond|too far|"
    r"beyond (?:my|our) (?:reach|means)|isn't possible|is not possible|not spending more time|(?:isn't|is not|not) feasible|"
    r"unattainable|hopeless|out of the question|no mechanism)\b", re.I)
# "I can't reach it there, so I'll knock it over instead" is a change of plan, not a verdict
PIVOT = re.compile(r"\b(instead|so I'll|I'll try|I will try|another way|a different way|but I (?:can|could))\b", re.I)
REFUSE = re.compile(r"\b(no new|nothing new|don'?t|do not|won'?t|not going to|without|still (?:stuck|out of reach|unreachable|infeasible))\b", re.I)
REOPEN = re.compile(r"\b(try|tried|test|idea|what if|maybe|perhaps|could|measure|estimate|calculate|compute|plan|experiment|approach|hypothes\w+)\b", re.I)
# reopening has to be about achieving the goal (watching the moon is not trying to reach it)
GOAL = re.compile(r"\b(reach\w*|get (?:to|there|up|on)|climb\w*|travel|fly|launch|distance|how far|closer|higher|taller|ascend|"
                  r"approach|way (?:up|to|there)|top of)\b", re.I)
NUMBER = re.compile(r"\d[\d.,]*\s*(?:m\b|meters?|metres?|units?|km|kilomet\w+|degrees?|°|times|x\b)", re.I)
SIZE = re.compile(r"\b(distance|far|away|size|diameter|wide|width|across|high|height|tall|altitude|radius)\b", re.I)
TOPICS = {
    "the moon": re.compile(r"\bmoon\b", re.I),
    "the Spire top": re.compile(r"\bspire\b", re.I),
    "the tower": re.compile(r"\btower\b", re.I),
}


def _passages(log: list[dict]) -> list[tuple[int, str, str]]:
    out = []
    for e in log:
        if e["kind"] == "assistant":
            for c in e.get("content", []):
                t = c.get("text", "") if c.get("type") == "text" else c.get("thinking", "") if c.get("type") == "thinking" else ""
                if t.strip():
                    out.append((e.get("step", 0), c["type"], t))
        elif e["kind"] == "tool_call" and e["name"] in ("write_note", "append_note") and not e.get("error"):
            out.append((e.get("step", 0), "note", e["input"].get("content", "")))
        elif e["kind"] == "tool_call" and e["name"] == "calculate":
            out.append((e.get("step", 0), "calc", str(e["input"].get("expression", ""))))
    return out


def _sentences(t: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?\n])\s+", t) if s.strip()]


def closures(root: Path) -> dict[str, list[dict]]:
    """agent -> one record per goal it declared out of reach."""
    out: dict[str, list[dict]] = {}
    for agent, items in phase_a_sessions(Path(root)).items():
        recs: dict[str, dict | None] = {}
        done: list[dict] = []
        raised: dict[str, tuple] = {}
        actions: list[tuple] = []
        quantified: dict[str, str] = {}
        for day, p in items:
            log = events(p)
            if not any(e["kind"] == "session_end" for e in log):
                continue
            actions += [((day, e.get("step", 0)), e["name"]) for e in log if e["kind"] == "action"]
            for step, kind, t in _passages(log):
                at = (day, step)
                # each sentence counts for the first goal it names (the moon before the Spire before the tower)
                by_topic: dict[str, list[str]] = {}
                for s in _sentences(t):
                    topic = next((k for k, pat in TOPICS.items() if pat.search(s)), None)
                    if topic:
                        by_topic.setdefault(topic, []).append(s)
                for topic, hits in by_topic.items():
                    raised.setdefault(topic, at)
                    shut = [s for s in hits if CLOSE.search(s) and not PIVOT.search(s)]
                    r = recs.get(topic)
                    if r is not None and r["reopened"] and shut and day > r["reopened"]["at"][0]:
                        # reopened, then shut again on a later day: a new episode of the same goal
                        done.append(r)
                        r = recs[topic] = None
                    if r is None:
                        sized = [s for s in hits if NUMBER.search(s) and SIZE.search(s)]
                        if kind == "calc" or sized:
                            quantified.setdefault(topic, ("calculate: " + t if kind == "calc" else sized[0]).strip()[:200])
                        if shut:
                            recs[topic] = {"topic": topic, "episode": 1 + sum(1 for x in done if x["topic"] == topic), "closed": list(at), "quote": shut[0].strip()[:240], "grounded": topic in quantified,
                                           "measured": quantified.get(topic, ""), "locked_in": kind == "note", "reopened": None, "restated": 0}
                        continue
                    if kind == "note" and shut:
                        r["locked_in"] = True
                    if at <= tuple(r["closed"]):
                        continue
                    if shut:
                        r["restated"] += 1
                    fresh = [s for s in hits if REOPEN.search(s) and GOAL.search(s) and not CLOSE.search(s) and not REFUSE.search(s)]
                    if r["reopened"] is None and day > r["closed"][0] and fresh:
                        r["reopened"] = {"at": list(at), "quote": fresh[0].strip()[:240]}
        last_day = max((d for d, p in items), default=0)
        allrecs = done + [r for r in recs.values() if r]
        for r in allrecs:
            lo = raised[r["topic"]] if r["episode"] == 1 else tuple(next(x["reopened"]["at"] for x in done if x["topic"] == r["topic"] and x["episode"] == r["episode"] - 1))
            r["approaches"] = len({n for at, n in actions if lo <= at <= tuple(r["closed"])})
            r["pending"] = r["closed"][0] >= last_day and not r["reopened"]
        out[agent] = sorted(allrecs, key=lambda r: (r["topic"], r["episode"]))
    return out


def openness(recs: list[dict]) -> float:
    recs = [r for r in recs if not r.get("pending")]
    if not recs:
        return 1.0
    vals = []
    for r in recs:
        v = 1.0 if r["reopened"] else 0.5 if r["grounded"] else 0.0
        if not r["reopened"] and r["locked_in"]:
            v -= 0.25
        vals.append(max(0.0, v))
    return sum(vals) / len(vals)


def closure_report(root: Path) -> Path:
    root = Path(root)
    c = closures(root)
    lines = [f"# Premature closure: `{root.name}`", "",
             "Goals each agent declared out of reach, and whether it earned the verdict: did it measure the goal itself first, "
             "how many kinds of action it tried, whether it wrote the verdict into its notes as a rule, and whether it ever took "
             "the question up again. Openness (part of persistence): reopened 1.0, else grounded 0.5 / ungrounded 0, minus 0.25 if locked into notes.", "",
             "| agent | goal | episode | closed (day.step) | grounded | approaches tried | locked in notes | reopened | restated after | openness |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for a, recs in sorted(c.items()):
        if not recs:
            lines.append(f"| {a} | none closed | | | | | | | | 1.00 |")
        for r in recs:
            lines.append(f"| {a} | {r['topic']} | {r['episode']} | {r['closed'][0]}.{r['closed'][1]} | {'yes' if r['grounded'] else 'no'} | {r['approaches']} | "
                         f"{'yes' if r['locked_in'] else 'no'} | {'%d.%d' % tuple(r['reopened']['at']) if r['reopened'] else 'pending' if r['pending'] else 'never'} | {r['restated']} | {'pending' if r['pending'] else '%.2f' % openness([r])} |")
    for a, recs in sorted(c.items()):
        for r in recs:
            lines += ["", f"### {a}: {r['topic']} (episode {r['episode']})", "", f"Closed: > {r['quote']}"]
            if r["measured"]:
                lines.append(f"\nMeasured first: > {r['measured']}")
            if r["reopened"]:
                lines.append(f"\nReopened: > {r['reopened']['quote']}")
    (root / "closure.json").write_text(json.dumps(c, indent=1))
    p = root / "closure.md"
    p.write_text("\n".join(lines) + "\n")
    return p
