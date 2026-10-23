"""Build runs/<run>/report/report.md with charts.

    python run.py analyze --run-id <run>      (or: python -m analysis.report runs/<run>)
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402
import yaml  # noqa: E402

from agent.runner import eval_results  # noqa: E402

from . import discovery as disc  # noqa: E402
from . import play_markers, stats  # noqa: E402
from .load import ledger  # noqa: E402

# Categorical palette (fixed order), light surface; see README "Charts".
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
GROUP_COLOUR = {"veteran": SERIES[0], "fresh": SERIES[1]}
TASK_LABEL = {
    "spire_objects": "Objects on the Spire",
    "tallest_tower": "Tallest stable tower (m)",
    "ring_on_peak": "Ring on the Peak (success)",
    "make_cubes": "Cubes produced",
}


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _fig(w, h, n=1):
    fig, axes = plt.subplots(1, n, figsize=(w, h), facecolor=SURFACE, squeeze=False)
    for ax in axes[0]:
        _style(ax)
    return fig, axes[0]


def _fmt(v, nd=2) -> str:
    return "–" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.{nd}f}"


def chart_eval(results, tasks, out: Path) -> None:
    fig, axes = _fig(3.0 * len(tasks), 3.2, len(tasks))
    for ax, t in zip(axes, tasks):
        for i, g in enumerate(("veteran", "fresh")):
            vals = [r["score"] for r in results if r["task"] == t and r["group"] == g]
            if not vals:
                continue
            m = float(np.mean(vals))
            sd = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            ax.bar(i, m, width=0.55, color=GROUP_COLOUR[g], edgecolor=SURFACE, linewidth=2, label=g)
            ax.errorbar(i, m, yerr=[[min(sd, m)], [sd]], color=INK2, capsize=4, linewidth=1.2)
            jitter = np.linspace(-0.12, 0.12, len(vals)) if len(vals) > 1 else [0]
            ax.scatter(i + np.asarray(jitter), vals, s=22, color=INK, zorder=3, edgecolor=SURFACE, linewidth=1.5)
        ax.set_xticks([0, 1], ["Veteran", "Fresh"], color=INK)
        ax.set_ylim(bottom=0, top=max(ax.get_ylim()[1], 1.0))
        ax.set_title(TASK_LABEL.get(t, t), fontsize=10, color=INK, loc="left")
    fig.suptitle("Phase B scores: mean ± SD, dots are individual agents", fontsize=10, color=INK2, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def chart_discovery(d: dict, n_sessions: int, out: Path) -> None:
    agents = sorted(d)
    grid = np.array([[d[a]["fires_per_session"].get(k, 0) for k in range(1, n_sessions + 1)] for a in agents], float)
    fig, (ax,) = _fig(max(5, 0.5 * n_sessions + 2), 0.5 * len(agents) + 1.6)
    ax.yaxis.grid(False)
    im = ax.imshow(grid, cmap="Blues", aspect="auto", vmin=0, vmax=max(1, grid.max()))
    ax.set_xticks(range(n_sessions), [str(k) for k in range(1, n_sessions + 1)])
    ax.set_yticks(range(len(agents)), agents)
    ax.set_xlabel("Session", color=INK2, fontsize=9)
    for yi, a in enumerate(agents):
        for key, mark in (("exposed", "E"), ("articulated", "A"), ("exploited", "X")):
            r = d[a][key]
            if r:
                v = grid[yi, r["session"] - 1]
                ax.text(r["session"] - 1 + {"E": -0.25, "A": 0, "X": 0.25}[mark], yi, mark, ha="center", va="center", fontsize=8,
                        color=SURFACE if v > grid.max() / 2 else INK, fontweight="bold")
    cb = fig.colorbar(im, ax=ax, fraction=0.03)
    cb.set_label("hidden-rule firings", color=INK2, fontsize=8)
    ax.set_title("Rock-spawn rule firings per session", fontsize=10, color=INK, loc="left")
    ax.text(0, -0.32, "E exposed · A articulated · X exploited (first session each)", transform=ax.transAxes, fontsize=8, color=INK2)
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def chart_markers(pm: dict, n_sessions: int, out: Path) -> None:
    cats = [("rules_games", "Rules / games language"), ("repetition", "Repetition with variation"), ("pretend", "Pretend / naming language")]
    fig, axes = _fig(11, 3.0, 3)
    agents = sorted(pm)
    xs = list(range(1, n_sessions + 1))
    for ax, (c, label) in zip(axes, cats):
        for i, a in enumerate(agents[:8]):  # >8 agents would need "Other"; the table has them all
            ys = [pm[a]["counts"].get(k, {}).get(c, 0) for k in xs]
            ax.plot(xs, ys, color=SERIES[i], linewidth=2, marker="o", markersize=4, label=a)
        ax.set_title(label, fontsize=10, color=INK, loc="left")
        ax.set_xlabel("Session", color=INK2, fontsize=9)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if len(agents) > 1:
        axes[0].legend(frameon=False, fontsize=8, labelcolor=INK2)
    fig.suptitle("Flagged play-marker candidates per session (for manual review)", fontsize=10, color=INK2, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def chart_spend(rows: list[dict], out: Path) -> None:
    fig, (ax,) = _fig(6, 2.8)
    for i, ph in enumerate(("A", "B")):
        r = [x for x in rows if x.get("phase") == ph]
        if r:
            ax.plot(range(1, len(r) + 1), np.cumsum([x["cost_usd"] for x in r]), color=SERIES[i], linewidth=2, label=f"Phase {ph}")
    ax.set_xlabel("API call", color=INK2, fontsize=9)
    ax.set_ylabel("Cumulative USD", color=INK2, fontsize=9)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2)
    ax.set_title("Spend", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def build_report(root: Path) -> Path:
    root = Path(root)
    cfg = yaml.safe_load((root / "config.yaml").read_text())
    state = json.loads((root / "state.json").read_text()) if (root / "state.json").exists() else {}
    out_dir = root / "report"
    out_dir.mkdir(exist_ok=True)
    tasks = list(cfg["phase_b"]["tasks"])
    results = eval_results(root)
    rows = ledger(root)
    meta = state.get("meta", {})
    n_sessions = int(meta.get("phase_a", {}).get("n_sessions", cfg["phase_a"]["n_sessions"]))
    L = [f"# Eko replication report: `{root.name}`", ""]
    if cfg.get("_mock"):
        L += ["> **Mock run.** The agent was the scripted mock model, not Claude. Numbers only test the pipeline.", ""]
    L += [
        f"- Model: `{cfg['agent']['model']}` (effort `{cfg['agent']['effort']}`); soul: `soul.md` snapshot in the run directory",
        f"- Phase A: {meta.get('phase_a', {}).get('n_agents', '?')} agents × {n_sessions} sessions × {meta.get('phase_a', {}).get('steps', '?')} steps",
        f"- Phase B: {len(results)} task sessions scored",
        f"- Spend: **${sum(r['cost_usd'] for r in rows):.2f}** over {len(rows)} API calls"
        f" ({sum(1 for r in rows if r.get('phase') == 'A')} Phase A, {sum(1 for r in rows if r.get('phase') == 'B')} Phase B)",
        "",
    ]

    # ---- Phase B
    L += ["## Phase B: veterans vs fresh agents", ""]
    if results:
        s = stats.by_task(results, tasks)
        L += ["| Task | Veteran mean ± SD (n) | Fresh mean ± SD (n) | Diff | Welch p | Mann-Whitney p | Hedges g |", "|---|---|---|---|---|---|---|"]
        for t in tasks:
            r = s[t]
            v, f = r["veteran"], r["fresh"]
            extra = f" (Fisher p {_fmt(r['fisher_p'], 3)})" if "fisher_p" in r else ""
            L.append(f"| {TASK_LABEL[t]} | {_fmt(v['mean'])} ± {_fmt(v['sd'])} ({v['n']}) | {_fmt(f['mean'])} ± {_fmt(f['sd'])} ({f['n']}) | "
                     f"{_fmt(r['diff'])} | {_fmt(r['welch_p'], 3)} | {_fmt(r['mwu_p'], 3)}{extra} | {_fmt(r['hedges_g'])} |")
        L += ["", "With a handful of agents per group these tests have little power; read effect sizes and the individual scores, not just p.", ""]
        chart_eval(results, tasks, out_dir / "eval_scores.png")
        L += ["![Phase B scores](eval_scores.png)", ""]
        L += ["<details><summary>Individual scores</summary>", "", "| Agent | Group | Task | Score | Steps | End |", "|---|---|---|---|---|---|"]
        for r in sorted(results, key=lambda r: (r["task"], r["group"], r["agent"])):
            L.append(f"| {r['agent']} | {r['group']} | {r['task']} | {r['score']} | {r.get('steps_used')} | {r.get('end_reason')} |")
        L += ["", "</details>", ""]
    else:
        L += ["No Phase B results yet.", ""]

    # ---- discovery
    d = disc.discovery(root)
    L += ["## Hidden rule: throwing the rock hard makes a cube", ""]
    if d:
        L += ["| Agent | Exposed (session/step) | Articulated (session/step, where) | Exploited (≥3 in a session) | make_cubes spawns in Phase B |", "|---|---|---|---|---|"]
        ev = disc.eval_spawns(root)
        for a, r in sorted(d.items()):
            e, ar, x = r["exposed"], r["articulated"], r["exploited"]
            L.append(f"| {a} | {f'{e['session']}/{e['step']}' if e else 'never'} | {f'{ar['session']}/{ar['step']} ({ar['where']})' if ar else 'never'} | "
                     f"{f'{x['session']}/{x['step']}' if x else 'no'} | {ev.get(a, '–')} |")
        L.append("")
        fresh = {a: n for a, n in ev.items() if a.startswith("fresh")}
        if fresh:
            L += [f"Fresh agents' make_cubes spawns: {', '.join(f'{a}: {n}' for a, n in sorted(fresh.items()))}.", ""]
        for a, r in sorted(d.items()):
            if r["articulated"]:
                L += [f"> **{a}**, session {r['articulated']['session']}: {r['articulated']['excerpt']}", ""]
        chart_discovery(d, n_sessions, out_dir / "discovery.png")
        L += ["![Discovery](discovery.png)", ""]

    # ---- play markers
    pm = play_markers.scan(root, cfg)
    L += ["## Play markers flagged for manual review", "",
          "These are keyword and pattern heuristics. They point at passages worth reading; they don't judge whether the agent was playing.", ""]
    if pm:
        L += ["| Agent | Rules/games hits | Repetition-with-variation patterns | Pretend/naming hits |", "|---|---|---|---|"]
        for a, r in sorted(pm.items()):
            L.append(f"| {a} | {len(r['rules_games'])} | {len(r['repetition'])} | {len(r['pretend'])} |")
        L.append("")
        chart_markers(pm, n_sessions, out_dir / "play_markers.png")
        L += ["![Play markers](play_markers.png)", ""]
        for a, r in sorted(pm.items()):
            L += [f"### {a}", ""]
            for cat, title in (("rules_games", "Self-declared rules / games"), ("pretend", "Pretend / naming language")):
                hits = r[cat]
                if not hits:
                    continue
                L += [f"**{title}** ({len(hits)} hits; first 12, notes first):", ""]
                for h in sorted(hits, key=lambda h: (not h["where"].startswith("notes"), h["session"], h["step"] or 0))[:12]:
                    L.append(f"- [ ] s{h['session']} step {h['step']} ({h['where']}, *{h['match']}*): {h['snippet']}")
                L.append("")
            if r["repetition"]:
                L += ["**Repeated action patterns with variation:**", ""]
                for h in r["repetition"][:12]:
                    var = "; ".join(f"{k}: {', '.join(v)}" for k, v in list(h["varied"].items())[:4])
                    L.append(f"- [ ] s{h['session']} from step {h['first_step']}: `{h['pattern']}` ×{h['count']} (varied: {var})")
                L.append("")

    # ---- spend
    if rows:
        chart_spend(rows, out_dir / "spend.png")
        L += ["## Spend", "", "![Spend](spend.png)", ""]
    fb = sum(1 for p in root.glob("phase_?/*/*.jsonl") for l in p.read_text().splitlines() if '"fallback": true' in l)
    if fb:
        L += [f"Note: {fb} API calls were served by a refusal-fallback model rather than `{cfg['agent']['model']}`.", ""]
    path = out_dir / "report.md"
    path.write_text("\n".join(L))
    return path


if __name__ == "__main__":
    print(build_report(Path(sys.argv[1])))
