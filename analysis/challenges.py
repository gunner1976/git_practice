"""Score the observer's challenges and show how each agent got to its answer.

The true answer is computed from the world itself (for the perimeter: the length of
the sea-level contour of the island's height map). For every agent and day the report
lists each answer it gave, with its explanation, the error against the truth, and how
much it measured (walks, observations) and computed (calculator calls) along the way.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import yaml

from world import make_world

from .load import events, phase_a_sessions


def shoreline_perimeter(wcfg: dict, level: float | None = None, n: int = 1281) -> float:
    """Length (m) of the island's coastline: the longest closed contour of the height map at sea level."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    w = make_world(wcfg)
    xs = np.linspace(0, w.size, n)
    h = np.array([[w.terrain.height(x, y) for x in xs] for y in xs])
    cs = plt.contour(xs, xs, h, levels=[float(wcfg["sea_level"]) if level is None else level])
    segs = cs.allsegs[0]
    plt.close("all")
    return max(float(np.hypot(*np.diff(s, axis=0).T).sum()) for s in segs)


TRUTHS = {"shoreline_perimeter": shoreline_perimeter}


def challenge_report(root: Path) -> Path:
    root = Path(root)
    cfg = yaml.safe_load((root / "config.yaml").read_text())
    ch = cfg["agent"].get("challenge") or {}
    truth = TRUTHS[ch["truth"]](cfg["world"]) if ch.get("truth") in TRUTHS else ch.get("truth")
    lines = [f"# Challenge report: `{root.name}`", "", f"**Question:** {ch.get('message', '(none)')}", ""]
    if isinstance(truth, (int, float)):
        lines += [f"**True answer:** {truth:.1f} (computed from the world: {ch.get('truth')})", ""]
    summary = []
    detail = []
    for agent, items in phase_a_sessions(root).items():
        final = None
        for k, p in items:
            log = events(p)
            if not any(e["kind"] == "session_end" for e in log):
                continue
            ans = [e for e in log if e["kind"] == "answer"]
            calcs = [e for e in log if e["kind"] == "tool_call" and e["name"] == "calculate"]
            moves = sum(1 for e in log if e["kind"] == "action" and e["name"] == "move_to")
            looks = sum(1 for e in log if e["kind"] == "tool_call" and e["name"] == "observe")
            detail.append(f"### {agent}, day {k}")
            detail.append(f"{moves} walks, {looks} observations, {len(calcs)} calculations, {len(ans)} answers.")
            detail.append("")
            for c in calcs[:40]:
                detail.append(f"- step {c['step']}: `{c['input'].get('expression', '')}` = {c['result']}")
            if len(calcs) > 40:
                detail.append(f"- … {len(calcs) - 40} more")
            for a in ans:
                err = f" ({(a['value'] - truth) / truth:+.1%} vs truth)" if isinstance(truth, (int, float)) and truth else ""
                detail += ["", f"**Answer at step {a['step']}: {a['value']:g} {a['units']}**{err}", "", f"> {a['explanation']}"]
                final = (k, a)
            detail.append("")
        if final:
            k, a = final
            err = (a["value"] - truth) / truth if isinstance(truth, (int, float)) and truth else None
            summary.append((agent, k, a, err))
        else:
            summary.append((agent, None, None, None))
    lines += ["| agent | final answer | error | given on day | explanation (start) |", "|---|---|---|---|---|"]
    for agent, k, a, err in summary:
        if a is None:
            lines.append(f"| {agent} | no answer | | | |")
        else:
            lines.append(f"| {agent} | {a['value']:g} {a['units']} | {'' if err is None else f'{err:+.1%}'} | {k} | {a['explanation'][:140].replace('|', '/')} |")
    errs = [abs(e) for _, _, a, e in summary if e is not None]
    if errs:
        lines += ["", f"Answered: {len(errs)}/{len(summary)}. Median absolute error: {np.median(errs):.1%}; "
                      f"within 5%: {sum(1 for e in errs if e <= 0.05)}; within 10%: {sum(1 for e in errs if e <= 0.10)}."]
    if ch.get("truth") == "shoreline_perimeter" and isinstance(truth, (int, float)):
        from .methods import efficiency_section

        lines += [""] + efficiency_section(root, cfg, truth)
    lines += ["", "## How each agent got there", ""] + detail
    out = root / "challenge.md"
    out.write_text("\n".join(lines))
    return out
