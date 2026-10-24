"""How efficiently, and how originally, agents measured the island, next to human methods.

Human baselines are scripted and run in the same world (no model involved), so their error
and effort are exact:
  radial + circle    walk out from the centre in k directions to the waterline, perimeter = 2*pi*mean radius
  radial + polygon   the same probes, perimeter = the polygon through the probe endpoints
  coast walk         follow the shoreline, mark k waypoints, perimeter = sum of the segments
For each agent: its final answer and error, and the effort spent up to that answer (metres
walked, actions, simulated minutes, API dollars), plus a method label read from what it did -
its trail (spokes to the coast, share of the coast it walked) and its explanation - and a
flag when the method matches none of the human ones.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from world import make_world

from .load import events, phase_a_sessions

COAST_NEAR = 2.5  # metres: a trail point this close to the waterline counts as "at the coast"


def shoreline(wcfg: dict, n: int = 641) -> np.ndarray:
    """The coastline as a closed polyline of (x, y) points, in the world's internal frame."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    w = make_world(wcfg)
    xs = np.linspace(0, w.size, n)
    h = np.array([[w.terrain.height(x, y) for x in xs] for y in xs])
    cs = plt.contour(xs, xs, h, levels=[float(wcfg["sea_level"])])
    segs = cs.allsegs[0]
    plt.close("all")
    return max(segs, key=lambda s: float(np.hypot(*np.diff(s, axis=0).T).sum()))


def _resample(poly: np.ndarray, k: int) -> np.ndarray:
    seg = np.hypot(*np.diff(poly, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    at = np.linspace(0, cum[-1], k, endpoint=False)
    return np.stack([np.interp(at, cum, poly[:, 0]), np.interp(at, cum, poly[:, 1])], axis=1)


def _closed_length(pts: np.ndarray) -> float:
    return float(np.hypot(*np.diff(np.vstack([pts, pts[:1]]), axis=0).T).sum())


def human_baselines(wcfg: dict, truth: float) -> list[dict]:
    w = make_world(wcfg)
    t = w.terrain
    cx = cy = w.size / 2
    sea = float(wcfg["sea_level"])
    rows = []
    for k in (4, 8, 16, 32):
        ends, walked = [], 0.0
        for j in range(k):
            a = 2 * math.pi * j / k
            r = 0.0
            while r < w.size and t.height(cx + r * math.cos(a), cy + r * math.sin(a)) > sea:
                r += 0.25
            ends.append((cx + r * math.cos(a), cy + r * math.sin(a), r))
            walked += 2 * r
        pts = np.array([(x, y) for x, y, _ in ends])
        circ = 2 * math.pi * float(np.mean([r for *_, r in ends]))
        rows.append({"method": "radial + circle", "k": k, "estimate": circ, "walked": walked})
        rows.append({"method": "radial + polygon", "k": k, "estimate": _closed_length(pts), "walked": walked})
    coast = shoreline(wcfg)
    for k in (8, 16, 32, 64, 128):
        rows.append({"method": "coast walk", "k": k, "estimate": _closed_length(_resample(coast, k)), "walked": truth})
    for r in rows:
        r["error"] = (r["estimate"] - truth) / truth
    return rows


def _trail(frames: list[dict]) -> np.ndarray:
    """Avatar path, densified to ~0.5 m spacing."""
    pts = []
    for a, b in zip(frames, frames[1:]):
        p0, p1 = np.array(a["a"][:2]), np.array(b["a"][:2])
        n = max(1, int(np.linalg.norm(p1 - p0) / 0.5))
        pts += [p0 + (p1 - p0) * i / n for i in range(n)]
    if frames:
        pts.append(np.array(frames[-1]["a"][:2]))
    return np.array(pts) if pts else np.zeros((0, 2))


def agent_methods(root: Path, data: dict, wcfg: dict, truth: float) -> list[dict]:
    """Per agent: final answer, effort up to it, coast coverage, spokes, and a method label."""
    coast = _resample(shoreline(wcfg), 400)
    ledger = [json.loads(l) for l in (Path(root) / "ledger.jsonl").read_text().splitlines() if l.strip()]
    by_id = {s["id"]: s for s in data["sessions"]}
    out = []
    for agent, items in phase_a_sessions(root).items():
        final = None
        logs = []
        for k, p in items:
            log = events(p)
            if not any(e["kind"] == "session_end" for e in log):
                continue
            logs.append((k, log))
            for e in log:
                if e["kind"] == "answer":
                    final = (k, e)
        if final is None:
            out.append({"agent": agent, "answered": False})
            continue
        fk, fa = final
        walked = actions = calcs = 0
        minutes = 0.0
        trail = []
        for k, log in logs:
            if k > fk:
                break
            s = by_id.get(f"{agent}/A{k:02d}")
            frames = s["frames"] if s else []
            if k == fk:
                frames = [f for f in frames if f["step"] <= fa["step"]]
                minutes += (fa.get("clock") or 0) / 60
            else:
                minutes += max([e.get("clock", 0) for e in log if "clock" in e] or [0]) / 60
            tr = _trail(frames)
            if len(tr):
                trail.append(tr)
                walked += float(np.hypot(*np.diff(tr, axis=0).T).sum()) if len(tr) > 1 else 0.0
            actions += sum(1 for e in log if e["kind"] == "action" and (k < fk or e["step"] <= fa["step"]))
            calcs += sum(1 for e in log if e["kind"] == "tool_call" and e["name"] == "calculate" and (k < fk or e["step"] <= fa["step"]))
        cost = sum(r["cost_usd"] for r in ledger if r.get("agent") == agent and r.get("phase") == "A"
                   and (r["session"] < fk or (r["session"] == fk and r.get("clock", 0) <= (fa.get("clock") or 1e9))))
        allp = np.vstack(trail) if trail else np.zeros((0, 2))
        if len(allp):
            d = np.sqrt(((coast[:, None, :] - allp[None, :, :]) ** 2).sum(-1)).min(axis=1)
            coverage = float((d <= COAST_NEAR).mean())
            near = np.sqrt(((allp[:, None, :] - coast[None, :, :]) ** 2).sum(-1)).min(axis=1) <= COAST_NEAR
            spokes = int(np.sum(near[1:] & ~near[:-1]) + (1 if near[0] else 0))
        else:
            coverage, spokes = 0.0, 0
        text = fa["explanation"].lower()
        circle = any(w in text for w in ("2π", "2pi", "2*pi", "2 pi", "2·pi", "circle", "circular", "πr", "pi*r", "mean radius",
                                         "average radius", "shore radius", "mean shore", "radius of about", "radius ≈", "radius ~"))
        polygon = any(w in text for w in ("polygon", "segment", "sum of", "summed", "added up", "chord", "walked around", "traced", "traverse", "along the coast", "around the coast"))
        if coverage >= 0.6:
            method = "coast walk"
        elif polygon and spokes >= 3:
            method = "radial + polygon"
        elif circle:
            method = "radial + circle" if spokes >= 2 else "circle guess"
        else:
            method = "other"
        out.append({"agent": agent, "answered": True, "day": fk, "answer": fa["value"], "units": fa.get("units", ""),
                    "error": (fa["value"] - truth) / truth, "walked": walked, "actions": actions, "minutes": minutes,
                    "cost": cost, "calcs": calcs, "coverage": coverage, "spokes": spokes, "method": method,
                    "human_method": method in ("coast walk", "radial + polygon", "radial + circle", "circle guess"),
                    "explanation": fa["explanation"]})
    return out


def efficiency_chart(baselines: list[dict], agents: list[dict], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    style = {"radial + circle": ("#8a8f96", "o"), "radial + polygon": ("#4b5563", "s"), "coast walk": ("#0f766e", "^")}
    for m, (c, mk) in style.items():
        rs = [r for r in baselines if r["method"] == m]
        ax.plot([r["walked"] for r in rs], [abs(r["error"]) * 100 for r in rs], mk + "--", color=c, label=f"human: {m}", lw=1, ms=6)
        for r in rs:
            ax.annotate(f"k={r['k']}", (r["walked"], abs(r["error"]) * 100), textcoords="offset points", xytext=(4, 3), fontsize=7, color=c)
    ag = [a for a in agents if a.get("answered")]
    ax.scatter([a["walked"] for a in ag], [abs(a["error"]) * 100 for a in ag], s=46, color="#5b5ff0", edgecolor="k", zorder=5, label="agents")
    for a in ag:
        ax.annotate(a["agent"].replace("agent_", "a"), (a["walked"], abs(a["error"]) * 100), textcoords="offset points", xytext=(4, -9), fontsize=7)
    ax.set_xlabel("metres walked before the final answer")
    ax.set_ylabel("absolute error (%)")
    ax.set_yscale("symlog", linthresh=1)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="upper right")
    ax.set_title("Accuracy against effort: agents vs human methods", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def efficiency_section(root: Path, cfg: dict, truth: float) -> list[str]:
    from .replay import build

    data = build(root)
    base = human_baselines(cfg["world"], truth)
    agents = agent_methods(root, data, cfg["world"], truth)
    efficiency_chart(base, agents, Path(root) / "efficiency.png")
    lines = ["## Efficiency and novelty against human methods", "",
             "Human baselines are scripted and run in the same world, so their numbers are exact. "
             "Walking is the effort that dominates for a person; a coast walk always covers the whole coastline.", "",
             "![Efficiency](efficiency.png)", "",
             "| human method | k | estimate | error | metres walked |", "|---|---|---|---|---|"]
    for r in base:
        lines.append(f"| {r['method']} | {r['k']} | {r['estimate']:.1f} | {r['error']:+.1%} | {r['walked']:.0f} |")
    lines += ["", "| agent | method (from what it did) | answer | error | walked m | actions | sim. min | cost | calcs | coast covered | coast visits |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in agents:
        if not a.get("answered"):
            lines.append(f"| {a['agent']} | no answer | | | | | | | | | |")
            continue
        flag = "" if a["human_method"] else " **(not a human method)**"
        lines.append(f"| {a['agent']} | {a['method']}{flag} | {a['answer']:g} | {a['error']:+.1%} | {a['walked']:.0f} | {a['actions']} | "
                     f"{a['minutes']:.0f} | ${a['cost']:.2f} | {a['calcs']} | {a['coverage']:.0%} | {a['spokes']} |")
    ans = [a for a in agents if a.get("answered")]
    if ans:
        def best_human(walked: float) -> dict | None:
            ok = [r for r in base if r["walked"] <= walked]
            return min(ok, key=lambda r: abs(r["error"])) if ok else None
        beats = sum(1 for a in ans if (b := best_human(a["walked"])) is None or abs(a["error"]) < abs(b["error"]))
        from collections import Counter
        counts = Counter(a["method"] for a in ans)
        lines += ["", f"- Methods used: " + ", ".join(f"{m} x{n}" for m, n in counts.most_common()) + ".",
                  f"- Agents more accurate than the best human method that walks no further: {beats}/{len(ans)}.",
                  f"- Novel (matches no human method): {sum(1 for a in ans if not a['human_method'])}/{len(ans)}; "
                  f"rarest method in this cohort: {counts.most_common()[-1][0]} ({counts.most_common()[-1][1]}).", ""]
    return lines
