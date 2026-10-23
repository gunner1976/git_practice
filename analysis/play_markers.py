"""Flag candidate play markers for manual review. These are heuristics:
they find things worth reading, they do not decide whether the agent played.

  rules_games  - self-declared rules, games, records, challenges, scores (notes + speech)
  repetition   - action n-grams repeated within a session with varied parameters
  pretend      - pretend / naming / personifying language ("let's call this cube a planet")
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from .load import events, phase_a_sessions

RULES = re.compile(
    r"\b(game|rules?|challenge|record|high ?score|score[sd]?|points?|round \d+|level \d+|personal best|attempt #?\d+|"
    r"win|won|lose|lost|lava|basketball|juggl\w*|hoop|target|bullseye|streak|tournament|competition|olympics?|"
    r"doesn'?t count|counts? as|no hands|allowed|forbidden|must not)\b",
    re.I,
)
PRETEND = re.compile(
    r"\b(pretend\w*|imagin\w*|as if|let'?s say|make[- ]believe|i'?ll call|let'?s call|call(?:ed|ing)? (?:it|this|them|him|her)|"
    r"nam(?:e|ed|ing) (?:it|this|them|him|her)|christen\w*|planets?|moons?|solar system|castle|temple|shrine|altar|throne|"
    r"village|kingdom|king|queen|monster|dragon|friends?|family|pet|baby|creature|spirit|god|offering|ritual|ceremony|"
    r"museum|monument|garden|home)\b",
    re.I,
)


def _texts(e: dict) -> list[tuple[str, str]]:
    if e["kind"] == "assistant":
        return [("speech", c.get("text") or c.get("thinking") or "") for c in e["content"] if c["type"] in ("text", "thinking")]
    if e["kind"] == "notes_diff":
        added = "\n".join(l[1:] for l in e["diff"].splitlines() if l.startswith("+") and not l.startswith("+++"))
        return [(f"notes:{e['path']}", added)]
    return []


def _snippet(text: str, m: re.Match, width: int = 110) -> str:
    a, b = max(0, m.start() - width), min(len(text), m.end() + width)
    return ("…" if a else "") + text[a:b].replace("\n", " ").strip() + ("…" if b < len(text) else "")


def _param_sig(name: str, inp: dict) -> tuple:
    def r(v):
        if isinstance(v, (int, float)):
            return round(float(v), 1)
        if isinstance(v, list):
            return tuple(r(x) for x in v)
        return v
    return tuple(sorted((k, r(v)) for k, v in (inp or {}).items()))


def _contains(big: tuple, small: tuple) -> bool:
    return any(big[i:i + len(small)] == small for i in range(len(big) - len(small) + 1))


def repetition(actions: list[tuple[int, str, dict]], ns: list[int], min_count: int) -> list[dict]:
    """Action-name n-grams that recur (non-overlapping) >= min_count times in a session
    while their parameters vary. Shorter patterns contained in a reported longer one
    with at least as many repeats are dropped."""
    names = [a[1] for a in actions]
    found: list[dict] = []
    for n in sorted(ns, reverse=True):
        grams: dict[tuple, list[int]] = defaultdict(list)
        for i in range(len(names) - n + 1):
            g = tuple(names[i:i + n])
            if grams[g] and i < grams[g][-1] + n:
                continue  # keep occurrences non-overlapping
            grams[g].append(i)
        for g, occ in grams.items():
            if len(occ) < min_count or set(g) <= {"move", "jump", "wait"}:
                continue  # only getting around: not interesting without an object in play
            if any(_contains(f["_gram"], g) and f["count"] >= len(occ) for f in found):
                continue
            varied: dict[str, set] = defaultdict(set)
            for s in occ:
                for j in range(n):
                    for k, v in (actions[s + j][2] or {}).items():
                        varied[f"{g[j]}.{k}"].add(str(_param_sig("", {k: v})[0][1]))
            varied = {k: sorted(v)[:6] for k, v in varied.items() if len(v) > 1}
            if not varied:
                continue  # identical repeats: repetition without variation
            found.append({"_gram": g, "pattern": " → ".join(g), "count": len(occ), "first_step": actions[occ[0]][0], "varied": varied})
    found.sort(key=lambda f: -f["count"] * len(f["_gram"]))
    return [{k: v for k, v in f.items() if k != "_gram"} for f in found[:8]]


def scan(root: Path, cfg: dict) -> dict[str, dict]:
    ns = list(range(cfg["analysis"]["repeat_ngram"][0], cfg["analysis"]["repeat_ngram"][1] + 1))
    min_count = int(cfg["analysis"]["repeat_min"])
    out = {}
    for agent, sessions in phase_a_sessions(root).items():
        rec = {"rules_games": [], "pretend": [], "repetition": [], "counts": defaultdict(lambda: {"rules_games": 0, "pretend": 0, "repetition": 0})}
        for k, path in sessions:
            actions = []
            for e in events(path):
                if e["kind"] == "action" and not e["error"]:
                    actions.append((e["step"], e["name"], e["input"]))
                for where, text in _texts(e):
                    for cat, rx in (("rules_games", RULES), ("pretend", PRETEND)):
                        for m in rx.finditer(text):
                            rec["counts"][k][cat] += 1
                            rec[cat].append({"session": k, "step": e.get("step"), "where": where, "match": m.group(0), "snippet": _snippet(text, m)})
            for r in repetition(actions, ns, min_count):
                rec["counts"][k]["repetition"] += 1
                rec["repetition"].append({"session": k, **r})
        rec["counts"] = dict(rec["counts"])
        out[agent] = rec
    return out
