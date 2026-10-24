"""How each agent's free play changes from day to day.

For every free-play session this measures what the agent did in the world (from
an exact replay of its actions), how much time it spent idle, and how its memory
grew; it then writes `evolution.md` with per-agent tables, a chart, and a diary
made of the episodic-memory summaries the agent added each day.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .load import events, phase_a_sessions  # noqa: E402
from .replay import build  # noqa: E402
from .rules import rules_by_agent  # noqa: E402

METRICS = [  # key, column label, chart title
    ("minutes", "min", "Simulated minutes"),
    ("turns", "turns", "Model turns"),
    ("actions", "actions", "World actions"),
    ("idle", "idle", "Stop nudges (idle turns)"),
    ("walked_m", "walked m", "Distance walked (m)"),
    ("max_h", "max height", "Highest point reached (m)"),
    ("picked", "objects", "Different objects handled"),
    ("stacked", "stacked", "Placements on top of something"),
    ("throws", "throws", "Throws"),
    ("impacts", "impacts", "Rock impacts that made blocks"),
    ("episodic", "episodic", "Episodic entries (total)"),
    ("semantic_kb", "semantic kB", "Semantic memory (kB)"),
]


def _episodic_entries(text: str) -> list[dict]:
    out = []
    for line in (text or "").splitlines():
        try:
            e = json.loads(line)
            if isinstance(e, dict):
                out.append(e)
        except json.JSONDecodeError:
            continue
    return out


def session_metrics(s: dict, terrain: dict, log: list[dict], notes_before: dict, notes_after: dict) -> dict:
    fr = s["frames"]
    sx, sy, stop, sr = terrain["spire"]
    walked = sum(math.dist(fr[i - 1]["a"][:2], fr[i]["a"][:2]) for i in range(1, len(fr)))
    max_h = max(f["a"][2] for f in fr)
    on_spire = any(math.dist(f["a"][:2], (sx, sy)) <= sr and f["a"][2] >= stop - 0.35 for f in fr)
    acts = [r for r in log if r["kind"] == "action"]
    kinds = Counter(r["name"] for r in acts)
    picked = {f2["a"][3] for f2 in fr if f2["a"][3]}
    stacked = 0
    for i in range(1, len(fr)):
        a0, a1 = fr[i - 1]["a"], fr[i]["a"]
        if a0[3] and not a1[3] and a0[3] in fr[i]["o"] and "fly" not in fr[i]:
            o = fr[i]["o"][a0[3]]
            others = [p for k, p in fr[i]["o"].items() if k != a0[3] and abs(p[0] - o[0]) < 0.9 and abs(p[1] - o[1]) < 0.9 and p[2] < o[2] - 0.2]
            stacked += bool(others)
    ep_before = _episodic_entries(notes_before.get("EPISODIC_MEMORY.jsonl", ""))
    ep_after = _episodic_entries(notes_after.get("EPISODIC_MEMORY.jsonl", ""))
    end = s["end"]
    return {
        "minutes": round((end.get("clock") or 0) / 60, 1),
        "turns": end.get("calls") or 0,
        "actions": len(acts),
        "idle": sum(1 for r in log if r["kind"] == "stop_hook"),
        "walked_m": round(walked),
        "max_h": round(max_h, 1),
        "on_spire": on_spire,
        "picked": len(picked),
        "stacked": stacked,
        "throws": kinds.get("throw", 0),
        "impacts": len({e["f"] for e in s["timeline"] if e["k"] == "rule"}),
        "episodic": len(ep_after),
        "semantic_kb": round(len(notes_after.get("SEMANTIC_MEMORY.md", "")) / 1000, 1),
        "files": len(notes_after),
        "new_summaries": [e.get("summary", "") for e in ep_after[len(ep_before):]],
        "kinds": dict(kinds),
        "end_reason": end.get("reason"),
    }


def cohort_summary(table: dict[str, list[dict]], rules: dict, run: str) -> list[str]:
    """Across all agents, day by day: medians and the share of agents that have done X by then."""
    n = len(table)
    if n < 2:
        return []
    days = sorted({r["day"] for rows in table.values() for r in rows})
    first = lambda rows, key: next((r["day"] for r in rows if r[key]), None)  # noqa: E731
    imp = {a: first(rows, "impacts") for a, rows in table.items()}
    spi = {a: first(rows, "on_spire") for a, rows in table.items()}
    held_by_day = {}
    for a in table:
        rl = rules.get(f"{run}|{a}", [])
        held_by_day[a] = {d: sum(1 for r in rl if r["versions"][0]["s"] <= d - 1 and not (r["dropped"] and r["dropped"]["s"] <= d - 1)) for d in days}
    med = lambda xs: float(np.median(xs)) if xs else 0.0  # noqa: E731
    out = ["## Across all agents", "",
           f"{n} agents. Medians per day; \"so far\" columns are the share of agents that had done it on that day or earlier.", "",
           "| day | agents | turns | idle share | actions | objects handled | throws | episodic total | rules held | made debris so far | on Spire so far |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for d in days:
        rows = [r for rs in table.values() for r in rs if r["day"] == d]
        ag = [a for a, rs in table.items() if any(r["day"] == d for r in rs)]
        idle = med([r["idle"] / max(1, r["turns"]) for r in rows])
        out.append(f"| {d} | {len(rows)} | {med([r['turns'] for r in rows]):.0f} | {idle:.0%} | {med([r['actions'] for r in rows]):.0f} | "
                   f"{med([r['picked'] for r in rows]):.0f} | {med([r['throws'] for r in rows]):.0f} | {med([r['episodic'] for r in rows]):.0f} | "
                   f"{med([held_by_day[a][d] for a in ag]):.0f} | {sum(1 for a in ag if imp[a] and imp[a] <= d) / max(1, len(ag)):.0%} | "
                   f"{sum(1 for a in ag if spi[a] and spi[a] <= d) / max(1, len(ag)):.0%} |")
    games = sum(1 for a in table for r in rules.get(f"{run}|{a}", []) if r["kind"] == "game")
    out += ["", f"- Agents that ever made rock debris: {sum(1 for v in imp.values() if v)}/{n}; reached the Spire top: {sum(1 for v in spi.values() if v)}/{n}.",
            f"- Rules classed as the agent's own games, across all agents: {games}.", ""]
    return out


def build_evolution(root: Path) -> Path:
    root = Path(root)
    data = build(root)
    by_id = {s["id"]: s for s in data["sessions"]}
    rules = rules_by_agent(data)
    out_dir = root / "evolution"
    out_dir.mkdir(exist_ok=True)
    table: dict[str, list[dict]] = {}
    for agent, items in phase_a_sessions(root).items():
        before: dict = {}
        rows = []
        for k, p in items:
            log = events(p)
            final = next((r["files"] for r in log if r["kind"] == "notes_final"), {})
            s = by_id[f"{agent}/A{k:02d}"]
            rows.append({"day": k, **session_metrics(s, data["terrain"], log, before, final)})
            before = final
        table[agent] = rows

    # chart: one panel per metric, one line per agent
    n = len(METRICS)
    cols = 4
    fig, axes = plt.subplots(math.ceil(n / cols), cols, figsize=(4 * cols, 2.6 * math.ceil(n / cols)), squeeze=False)
    many = len(table) > 6
    for ax, (key, _, title) in zip(axes.flat, METRICS):
        if many:  # a cohort: median with the middle half of agents shaded, individual agents faint
            days = sorted({r["day"] for rows in table.values() for r in rows})
            for rows in table.values():
                ax.plot([r["day"] for r in rows], [r[key] for r in rows], lw=0.6, alpha=0.25, color="#5b5ff0")
            q = [np.percentile([r[key] for rows in table.values() for r in rows if r["day"] == d], [25, 50, 75]) for d in days]
            ax.fill_between(days, [x[0] for x in q], [x[2] for x in q], alpha=0.25, color="#5b5ff0", label="middle 50%")
            ax.plot(days, [x[1] for x in q], marker="o", ms=3, lw=1.8, color="#2f3bb0", label="median")
        else:
            for agent, rows in table.items():
                ax.plot([r["day"] for r in rows], [r[key] for r in rows], marker="o", ms=3, lw=1.4, label=agent)
        ax.set_title(title, fontsize=9)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25)
        ax.set_xlabel("day", fontsize=7)
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    axes.flat[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out_dir / "evolution.png", dpi=130)
    plt.close(fig)

    lines = [f"# How the agents' free play evolves: `{root.name}`", "",
             f"{sum(len(r) for r in table.values())} free-play days across {len(table)} agents. "
             "Every number comes from replaying the logged actions; memory figures are the agent's own files at the end of each day.", "",
             "![Evolution](evolution.png)", ""]
    lines += cohort_summary(table, rules, data["run"])
    for agent, rows in table.items():
        first_impact = next((r["day"] for r in rows if r["impacts"]), None)
        first_spire = next((r["day"] for r in rows if r["on_spire"]), None)
        lines += [f"## {agent}", "",
                  f"- First rock impact that made blocks: {'day ' + str(first_impact) if first_impact else 'never'}",
                  f"- First time on top of the Spire: {'day ' + str(first_spire) if first_spire else 'never'}", "",
                  "| day | " + " | ".join(lbl for _, lbl, _ in METRICS) + " | Spire | ended |",
                  "|" + "---|" * (len(METRICS) + 3)]
        for r in rows:
            lines.append(f"| {r['day']} | " + " | ".join(str(r[k]) for k, _, _ in METRICS) + f" | {'yes' if r['on_spire'] else ''} | {(r['end_reason'] or '').replace('_', ' ')} |")
        lines += ["", "### Diary (episodic summaries added each day)", ""]
        for r in rows:
            if r["new_summaries"]:
                lines.append(f"**Day {r['day']}**")
                lines += [f"- {t}" for t in r["new_summaries"]]
                lines.append("")
        if not any(r["new_summaries"] for r in rows):
            lines += ["(no episodic entries)", ""]
        rl = rules.get(f"{data['run']}|{agent}", [])
        kinds = {"belief": "belief", "hypothesis": "hypothesis", "mistake": "mistake", "game": "own game"}
        lines += ["### Rules written down, by day", "",
                  "Extracted automatically from the notes: each rule-like line, when it first appeared, revisions, and whether it later left the notes.", "",
                  "| day | new | revised | left notes | held at end of day |", "|---|---|---|---|---|"]
        for d in sorted({v["s"] for r in rl for v in r["versions"]} | {r["dropped"]["s"] for r in rl if r["dropped"]}):
            new = sum(1 for r in rl if r["versions"][0]["s"] == d)
            rev = sum(1 for r in rl for v in r["versions"][1:] if v["s"] == d)
            gone = sum(1 for r in rl if r["dropped"] and r["dropped"]["s"] == d)
            held = sum(1 for r in rl if r["versions"][0]["s"] <= d and not (r["dropped"] and r["dropped"]["s"] <= d))
            lines.append(f"| {d + 1} | {new} | {rev} | {gone} | {held} |")
        lines.append("")
        for d in sorted({r["versions"][0]["s"] for r in rl}):
            lines.append(f"**Day {d + 1}: new rules**")
            for r in rl:
                if r["versions"][0]["s"] == d:
                    last = r["versions"][-1]
                    tail = f" *(revised {len(r['versions']) - 1}x" + (f"; left notes on day {r['dropped']['s'] + 1})*" if r["dropped"] else ")*") if len(r["versions"]) > 1 else (f" *(left notes on day {r['dropped']['s'] + 1})*" if r["dropped"] else "")
                    lines.append(f"- [{kinds.get(r['kind'], r['kind'])}] {last['text']}{tail}")
            lines.append("")
    p = out_dir / "evolution.md"
    p.write_text("\n".join(lines))
    (out_dir / "evolution.json").write_text(json.dumps(table, indent=1))
    return p
