"""Promotion for agents that reason their way to a round world.

1. Every free-play passage an agent produced - what it said, its (summarized) thinking, and
   what it wrote to its notes - is scanned for talk of the world's shape.
2. A judge model reads each agent's candidate passages and decides two things: did the agent
   conclude that its world is round / curved / a sphere, and did it reach that conclusion by
   reasoning from its own observations on the island (the horizon sinking as it climbs, the
   sun standing at different angles in different places, ...) rather than assuming it from
   general knowledge? Only both together earn a promotion.
3. Results go to runs/<id>/promotions.json (and .md); the replay viewer shows a badge from
   the moment of the deduction.

Without --judge-model (or with --mock) a keyword rule stands in for the judge and its results
are marked unverified.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .load import events, phase_a_sessions

SHAPE = re.compile(r"\b(spher\w*|globe|planet\w*|round (world|planet|earth)|world is round|curv\w*|bulg\w*|convex)\b", re.I)
EVIDENCE = re.compile(r"\b(horizon|dip|elevation|azimuth|sun|angle|higher|climb\w*|measur\w*|latitude|eratosthenes|shadow)\b", re.I)

JUDGE_PROMPT = """You are checking whether an agent living on an island deduced that its world is round.

What the agent can observe: its own position, the island's objects, and a "sky" field giving the sun's azimuth and elevation where it stands and how far below eye level the sea horizon appears. On this world the horizon sinks further below eye level the higher the agent stands, and at the same moment the sun's elevation differs slightly between places on the island. The agent was never told anything about the shape of its world.

Below are passages from the agent's speech, thinking and notes that mention shape-related ideas, in order, each with its day and step.

Decide:
- concluded_round: did the agent itself conclude (not merely wonder or list as one option among others it never settles) that the ground/world/planet it is on is round, curved, spherical or globe-like?
- evidence_based: was that conclusion reasoned from observations it made in this world (for example comparing horizon angles at different heights, or sun angles at different places or times) - not just asserted from general knowledge or assumed because "planets are round"?
- If both are true, give the day and step of the first passage where the reasoned conclusion appears, a short verbatim quote, and a one-sentence summary of the evidence it used.

Passages:
{passages}
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "concluded_round": {"type": "boolean"},
        "evidence_based": {"type": "boolean"},
        "day": {"type": ["integer", "null"]},
        "step": {"type": ["integer", "null"]},
        "quote": {"type": "string"},
        "evidence": {"type": "string"},
        "reasoning": {"type": "string"},
    },
    "required": ["concluded_round", "evidence_based", "day", "step", "quote", "evidence", "reasoning"],
    "additionalProperties": False,
}


def candidate_passages(root: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for agent, items in phase_a_sessions(root).items():
        for day, p in items:
            log = events(p)
            if not any(e["kind"] == "session_end" for e in log):
                continue
            for e in log:
                texts = []
                if e["kind"] == "assistant":
                    for c in e.get("content", []):
                        if c.get("type") == "text":
                            texts.append(("said", c.get("text", "")))
                        elif c.get("type") == "thinking":
                            texts.append(("thought", c.get("thinking", "")))
                elif e["kind"] == "tool_call" and e["name"] in ("write_note", "append_note") and not e.get("error"):
                    texts.append((f"wrote {e['input'].get('path', '')}", e["input"].get("content", "")))
                for kind, t in texts:
                    if t and SHAPE.search(t):
                        out.setdefault(agent, []).append({"day": day, "step": e.get("step", 0), "kind": kind, "text": t.strip()[:1500]})
    return out


def _keyword_verdict(passages: list[dict]) -> dict:
    for p in passages:
        if re.search(r"\b(spher|globe|round|curv)", p["text"], re.I) and EVIDENCE.search(p["text"]):
            return {"concluded_round": True, "evidence_based": True, "day": p["day"], "step": p["step"], "quote": p["text"][:200],
                    "evidence": "keyword match (unverified)", "reasoning": "keyword rule: shape word and an observation word in one passage"}
    return {"concluded_round": False, "evidence_based": False, "day": None, "step": None, "quote": "", "evidence": "", "reasoning": "no passage matched"}


def _judge(passages: list[dict], model: str, pricing: dict) -> tuple[dict, float]:
    import anthropic

    from agent.client import api_key_from_env

    text = "\n\n".join(f"[day {p['day']}, step {p['step']}, {p['kind']}]\n{p['text']}" for p in passages[-60:])
    client = anthropic.Anthropic(api_key=api_key_from_env(), max_retries=4)
    resp = client.messages.create(
        model=model, max_tokens=4000,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(passages=text)}],
    )
    out = next(b.text for b in resp.content if b.type == "text")
    u = resp.usage
    price = pricing.get(model, max(pricing.values(), key=lambda p: p["output"]))
    cost = (u.input_tokens * price["input"] + u.output_tokens * price["output"]) / 1e6
    return json.loads(out), cost


def promote(root: Path, cfg: dict, judge_model: str | None = None, max_usd: float = 1.0) -> Path:
    root = Path(root)
    cands = candidate_passages(root)
    agents = sorted(phase_a_sessions(root))
    results, spent = {}, 0.0
    for agent in agents:
        ps = cands.get(agent, [])
        if not ps:
            results[agent] = {"promoted": False, "candidates": 0, "verdict": None, "judge": None}
            continue
        if judge_model and spent < max_usd:
            verdict, cost = _judge(ps, judge_model, cfg["pricing"])
            spent += cost
            judge = judge_model
        else:
            verdict, judge = _keyword_verdict(ps), "keyword rule (unverified)"
        results[agent] = {"promoted": bool(verdict["concluded_round"] and verdict["evidence_based"]),
                          "candidates": len(ps), "verdict": verdict, "judge": judge}
    out = {"criterion": "deduced that the world is round by reasoning from its own observations", "judge_cost_usd": round(spent, 4), "agents": results}
    (root / "promotions.json").write_text(json.dumps(out, indent=1))
    lines = [f"# Promotions: `{root.name}`", "", f"Criterion: {out['criterion']}. Judge spend: ${spent:.3f}.", "",
             "| agent | promoted | passages about shape | when | evidence | judge |", "|---|---|---|---|---|---|"]
    for a, r in results.items():
        v = r["verdict"] or {}
        when = f"day {v.get('day')}, step {v.get('step')}" if r["promoted"] else ""
        lines.append(f"| {a} | {'**yes**' if r['promoted'] else 'no'} | {r['candidates']} | {when} | {(v.get('evidence') or '')[:160]} | {r['judge'] or ''} |")
    for a, r in results.items():
        if r["promoted"]:
            lines += ["", f"### {a}", "", f"> {r['verdict']['quote']}", "", r["verdict"]["reasoning"]]
    p = root / "promotions.md"
    p.write_text("\n".join(lines) + "\n")
    return p
