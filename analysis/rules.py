"""The rules an agent writes down over time.

Every write to an agent's notes is replayed in order. After each write the file
is split into rule-like items: in the paper's SEMANTIC_MEMORY.md, every bullet
below the template header (with its *verified* / *fact* / *hypothesis* /
*mistake* tag and its topic heading); in free-form notes, sentences that state a
regularity or a self-imposed rule. Items are matched to the previous version of
the same file by text similarity, so each rule gets a history: when it first
appeared, each revision, and when (if ever) it was dropped.

Each item is also sorted into a kind:
  game       a rule or goal the agent sets for itself (a game, challenge, record, ritual)
  belief     what it holds true about the world (verified, fact or untagged)
  hypothesis what it suspects but hasn't confirmed
  mistake    a pitfall it hit and the rule it made to avoid it
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "paper" / "workspace"
SKIP_FILES = {"SOUL.md", "EPISODIC_MEMORY.md", "EPISODIC_MEMORY.jsonl"}
TAG = re.compile(r"\*(verified|fact|mistake|hypothesis)\*", re.I)
GAME = re.compile(r"\b(game|games|challenge|my rules?|house rules?|score|scored|round|personal best|record attempt|ritual|tradition|"
                  r"for fun|just because|self-imposed|my own goal|i'll only|i only allow|no hands|blindfold|course|lap|tournament)\b", re.I)
RULEISH = re.compile(r"\b(rule|always|never|only|must|spawns?|works|fails|can't|cannot|too steep|resets?|threshold|reach|limit|capped|clamped|"
                     r"verified|confirmed|key finding|reliably|every time|each time|regardless)\b|>=|<=", re.I)
NOT_RULE = re.compile(r"^(plan|idea|ideas|next|todo|to do|check|tomorrow|try|maybe|goal for|today)\b|\btomorrow\b|^day \d+:?\s*(woke|walked|nothing)", re.I)
GUESS = re.compile(r"\b(maybe|might|perhaps|probably|seems|unknown|unclear|investigate|test:|suspect)\b|\?", re.I)
_template_lines: set[str] | None = None


def _templates() -> set[str]:
    global _template_lines
    if _template_lines is None:
        _template_lines = set()
        if TEMPLATE_DIR.exists():
            for f in TEMPLATE_DIR.iterdir():
                _template_lines |= {_norm(l) for l in f.read_text().splitlines() if l.strip()}
    return _template_lines


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", s)).strip().lower()


def extract(path: str, text: str) -> list[dict]:
    """Rule-like items in one file: [{"text", "tag", "topic"}]."""
    if Path(path).name in SKIP_FILES or not text:
        return []
    items: list[dict] = []
    tpl = _templates()
    if "<!-- DO NOT EDIT ABOVE THIS LINE -->" in text:
        text = text.split("<!-- DO NOT EDIT ABOVE THIS LINE -->", 1)[1]
    structured = bool(re.search(r"^\s*[-*] ", text, re.M)) and (bool(TAG.search(text)) or path.upper().startswith("SEMANTIC"))
    topic = ""
    if structured:
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                topic = s.lstrip("#").strip()
                continue
            if not re.match(r"^[-*] ", s) or _norm(s) in tpl or topic.lower() == "index":
                continue
            body = s[2:].strip()
            m = TAG.search(body)
            items.append({"text": TAG.sub("", body).strip(" -:—"), "tag": m.group(1).lower() if m else "", "topic": topic})
    else:
        for para in re.split(r"\n+", text):
            for sent in re.split(r"(?<=[.!?;])\s+", para.strip()):
                s = sent.strip(" -*")
                if len(s) < 12 or _norm(s) in tpl:
                    continue
                if NOT_RULE.search(s):
                    continue
                if RULEISH.search(s) or GAME.search(s):
                    m = TAG.search(s)
                    items.append({"text": TAG.sub("", s).strip(), "tag": m.group(1).lower() if m else "", "topic": ""})
    for it in items:
        tag = it["tag"] or ("hypothesis" if GUESS.search(it["text"]) else "")
        it["kind"] = "game" if GAME.search(it["text"]) or GAME.search(it["topic"]) else {"hypothesis": "hypothesis", "mistake": "mistake"}.get(tag, "belief")
    return [it for it in items if it["text"]]


def _sim(a: str, b: str) -> float:
    """Character similarity, or word overlap for rules that were reworded."""
    na, nb = _norm(a), _norm(b)
    wa, wb = set(re.findall(r"[a-z0-9]+", na)), set(re.findall(r"[a-z0-9]+", nb))
    jac = len(wa & wb) / max(1, len(wa | wb))
    return max(SequenceMatcher(None, na, nb).ratio(), jac + 0.15)


def track(sessions: list[dict]) -> list[dict]:
    """Rule histories for one agent. `sessions` are replay sessions in order, each with
    notes_start, timeline (note events) and frames. Positions are (session index, frame)."""
    rules: list[dict] = []
    active: dict[str, list[dict]] = {}  # file -> its live rules
    files: dict[str, str] = {}

    def at(si: int, s: dict, f: int) -> dict:
        fr = s["frames"][min(f, len(s["frames"]) - 1)]
        return {"s": si, "sid": s["id"], "label": s["label"], "f": f, "step": fr["step"]}

    def update(path: str, text: str, where: dict) -> None:
        new = extract(path, text)
        live = active.get(path, [])
        used: set[int] = set()
        nxt = []
        for it in new:
            best, bs = None, 0.0
            for i, r in enumerate(live):
                if i in used:
                    continue
                sc = _sim(it["text"], r["versions"][-1]["text"])
                if sc > bs:
                    best, bs = i, sc
            if best is not None and bs >= 0.5:
                used.add(best)
                r = live[best]
                if _norm(r["versions"][-1]["text"]) != _norm(it["text"]) or r["versions"][-1]["tag"] != it["tag"]:
                    r["versions"].append({**where, "text": it["text"], "tag": it["tag"]})
                    if it["kind"] != "belief" or r["kind"] == "belief":
                        r["kind"] = it["kind"]
                nxt.append(r)
            else:
                r = {"id": len(rules), "file": path, "topic": it["topic"], "kind": it["kind"], "versions": [{**where, "text": it["text"], "tag": it["tag"]}], "dropped": None}
                rules.append(r)
                nxt.append(r)
        for i, r in enumerate(live):
            if i not in used and r["dropped"] is None:
                r["dropped"] = where
        active[path] = nxt

    for si, s in enumerate(sessions):
        if si == 0:
            for p, txt in (s.get("notes_start") or {}).items():
                files[p] = txt
                update(p, txt, at(0, s, 0))
        for e in s["timeline"]:
            if e["k"] != "note":
                continue
            old = files.get(e["p"], "")
            txt = old + ("" if not old or old.endswith("\n") else "\n") + e["t"] if e.get("append") else e["t"]
            files[e["p"]] = txt
            update(e["p"], txt, at(si, s, e["f"]))
    for r in rules:
        r["revisions"] = len(r["versions"]) - 1
    return rules


def rules_by_agent(data: dict) -> dict[str, list[dict]]:
    """`run|agent` -> rule histories, for every free-play agent in replay data."""
    groups: dict[str, list[dict]] = {}
    for s in data["sessions"]:
        if s["phase"] == "A":
            groups.setdefault(f"{s.get('run', data.get('run'))}|{s['agent']}", []).append(s)
    return {k: track(v) for k, v in groups.items()}
