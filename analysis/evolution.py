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

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .load import events, phase_a_sessions  # noqa: E402
from .replay import build  # noqa: E402

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


def build_evolution(root: Path) -> Path:
    root = Path(root)
    data = build(root)
    by_id = {s["id"]: s for s in data["sessions"]}
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
    for ax, (key, _, title) in zip(axes.flat, METRICS):
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
    p = out_dir / "evolution.md"
    p.write_text("\n".join(lines))
    (out_dir / "evolution.json").write_text(json.dumps(table, indent=1))
    return p
