"""The inquiry funnel: how far each agent took each notable thing it met.

For every phenomenon the world produced in front of an agent, the agent's logs are read for
how far it went, in order:

  seen        it was exposed to it (an observation showed it, or its own action caused it)
  mentioned   it said or thought something about it
  recorded    it wrote it down in its notes, unprompted
  questioned  it asked about it or proposed a cause (a question, "maybe", "why", "hypothesis")
  tested      it went back to it on purpose: observed it again or repeated the action that caused it
  explained   it wrote a cause or a rule for it in a later note than the one that first recorded
              it (for the eclipse: only a verified round-world deduction, from promotions.json)

Phenomena: the lunar eclipse (seen = an observation that reported it), the rock shattering
(seen = its own throw made fragments), losing something to the sea, the mission tablet, and
the mission phone (seen = it appeared, or the agent heard something from it).
Recording what it notices is scored as its own trait ("noticing"): the share of phenomena an
agent saw that it also wrote down.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .load import events, phase_a_sessions

STAGES = ["seen", "mentioned", "recorded", "questioned", "tested", "explained"]

PHENOMENA = {
    "lunar eclipse": {
        "words": re.compile(r"eclipse|moon.{0,60}(dark|shadow|red|dim)|(dark|shadow).{0,60}moon", re.I | re.S),
        "cause": re.compile(r"(shadow of|our shadow|planet'?s shadow|world'?s shadow|island'?s shadow|blocked by|passes? (through|into)|because).{0,120}", re.I | re.S),
    },
    "rock shattering": {
        "words": re.compile(r"impact ?block|fragment|debris|shatter|broke into|small (cube|block)s?", re.I),
        "cause": re.compile(r"(only|whenever|when|if|threshold|speed|hard|>=|at least|because).{0,80}(rock|throw|speed|impact)|(rock|throw|impact).{0,80}(threshold|speed|>=|at least)", re.I | re.S),
    },
    "lost at sea": {
        "words": re.compile(r"(lost|gone|vanish|disappear|sank|sunk|sea|water|ocean).{0,60}(rock|ring|block|cube)|(rock|ring|block|cube).{0,60}(lost|gone|vanish|disappear|sank|sunk|into the (sea|water|ocean))", re.I | re.S),
        "cause": re.compile(r"(sea|water|ocean|sink|sank|edge).{0,80}(lost|gone|vanish|disappear)|(lost|gone|vanish|disappear).{0,80}(sea|water|ocean|sink|sank)", re.I | re.S),
    },
    "the phone": {
        "words": re.compile(r"phone|ringing|\bcall\b|voice", re.I),
        "cause": re.compile(r"(another|other|second|different) (agent|person|being|mind|island|one)|someone else|not alone", re.I),
    },
    "the tablet": {
        "words": re.compile(r"tablet|inscription|carved|mission", re.I),
        "cause": re.compile(r"mission|reach the moon", re.I),
    },
}
QUESTION = re.compile(r"\?|\b(why|maybe|perhaps|might|hypothes\w+|wonder|what causes|could it|test whether|investigate|curious)\b", re.I)


def _texts(e: dict) -> list[tuple[str, str]]:
    if e["kind"] == "assistant":
        return [("speech", c.get("text", "") or c.get("thinking", "")) for c in e.get("content", []) if c.get("type") in ("text", "thinking")]
    if e["kind"] == "tool_call" and e["name"] in ("write_note", "append_note") and not e.get("error"):
        return [("note", e["input"].get("content", ""))]
    return []


def _exposures(e: dict) -> set[str]:
    out = set()
    if e["kind"] == "tool_call" and e["name"] == "observe" and '"eclipse"' in e.get("result", ""):
        out.add("lunar eclipse")
    if e["kind"] == "action":
        for ev in e.get("events", []):
            if ev.get("rule") == "rock_impact":
                out.add("rock shattering")
            if ev.get("type") == "lost":
                out.add("lost at sea")
            if ev.get("rule") == "mission_tablet":
                out.add("the tablet")
            if ev.get("rule") == "mission_phone":
                out.add("the phone")
    if e["kind"] == "world_events":
        rules = {ev.get("rule") for ev in e.get("events", [])}
        if "mission_tablet" in rules:
            out.add("the tablet")
        if "mission_phone" in rules:
            out.add("the phone")
    if e["kind"] == "heard":
        out.add("the phone")
    return out


def funnel(root: Path) -> dict[str, dict[str, dict]]:
    """agent -> phenomenon -> {stage: (day, step) of first reaching it}"""
    root = Path(root)
    promos = {}
    pp = root / "promotions.json"
    if pp.exists():
        promos = {a: r for a, r in json.loads(pp.read_text())["agents"].items() if r.get("promoted")}
    out: dict[str, dict[str, dict]] = {}
    for agent, items in phase_a_sessions(root).items():
        st: dict[str, dict] = {}
        revisits: dict[str, int] = {}
        for day, p in items:
            log = events(p)
            if not any(e["kind"] == "session_end" for e in log):
                continue
            for e in log:
                at = (day, e.get("step", 0))
                for ph in _exposures(e):
                    s = st.setdefault(ph, {})
                    if "seen" in s and "recorded" in s:
                        revisits[ph] = revisits.get(ph, 0) + 1  # met it again after writing it down
                        if revisits[ph] >= 2:
                            s.setdefault("tested", at)
                    s.setdefault("seen", at)
                for kind, t in _texts(e):
                    for ph, pat in PHENOMENA.items():
                        s = st.get(ph)
                        if not s or "seen" not in s or not pat["words"].search(t):
                            continue
                        s.setdefault("mentioned", at)
                        if kind == "note":
                            s.setdefault("recorded", at)
                        if QUESTION.search(t):
                            s.setdefault("questioned", at)
                        # a cause written in a later note than the first record: describing what
                        # happened as it is first written down is not yet explaining it
                        if kind == "note" and ph != "lunar eclipse" and s["recorded"] < at and pat["cause"].search(t):
                            s.setdefault("explained", at)
        if agent in promos and "lunar eclipse" in st:
            v = promos[agent]["verdict"]
            st["lunar eclipse"].setdefault("explained", (v.get("day"), v.get("step")))
        out[agent] = st
    return out


def noticing_score(f: dict[str, dict]) -> float:
    """Share of the phenomena an agent saw that it also wrote down."""
    seen = [ph for ph, s in f.items() if "seen" in s]
    return sum(1 for ph in seen if "recorded" in f[ph]) / len(seen) if seen else 0.0


def funnel_report(root: Path) -> Path:
    root = Path(root)
    f = funnel(root)
    lines = [f"# Inquiry funnel: `{root.name}`", "",
             "How far each agent took each notable thing it met: " + " -> ".join(STAGES) + ". "
             "Cells give the day.step it first reached that stage; blank = never.", ""]
    for ph in PHENOMENA:
        rows = [(a, s[ph]) for a, s in sorted(f.items()) if ph in s]
        if not rows:
            continue
        counts = [sum(1 for _, s in rows if k in s) for k in STAGES]
        lines += [f"## {ph}", "", "Agents reaching each stage: " + ", ".join(f"{k} {c}" for k, c in zip(STAGES, counts)), "",
                  "| agent | " + " | ".join(STAGES) + " |", "|---|" + "---|" * len(STAGES)]
        for a, s in rows:
            lines.append(f"| {a} | " + " | ".join(f"{s[k][0]}.{s[k][1]}" if k in s else "" for k in STAGES) + " |")
        lines.append("")
    lines += ["## Noticing (what it saw, it wrote down)", "", "| agent | phenomena seen | written down | noticing |", "|---|---|---|---|"]
    for a, s in sorted(f.items()):
        seen = [ph for ph, x in s.items() if "seen" in x]
        lines.append(f"| {a} | {len(seen)} | {sum(1 for ph in seen if 'recorded' in s[ph])} | {noticing_score(s):.0%} |")
    (root / "inquiry.json").write_text(json.dumps(f, indent=1))
    p = root / "inquiry.md"
    p.write_text("\n".join(lines) + "\n")
    return p
