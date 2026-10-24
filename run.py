#!/usr/bin/env python3
"""Eko replication harness CLI.

  python run.py pilot    --max-usd 3                 # 1 agent, 2 sessions, 30 steps; prints transcript, notes, cost, estimate
  python run.py freeplay --run-id main --max-usd 60  # Phase A (refuses to start before a real pilot exists)
  python run.py eval     --run-id main --max-usd 60  # Phase B on the same run
  python run.py all      --run-id main --max-usd 120 # Phase A then Phase B
  python run.py analyze  --run-id main               # stats, discovery, play markers, report.md + charts
  python run.py evolve   --run-id main               # day-by-day change in each agent's free play: runs/<id>/evolution/
  python run.py viewer   --run-id main               # replay viewer (3D world / 2D map toggle, rules over time): runs/<id>/viewer.html
  python run.py estimate --run-id <pilot-id>         # re-print the full-run estimate from a pilot
  python run.py ladder-estimate --run-id <pilot-id>  # upper-bound cost of the ladder from a pilot
  python run.py price-watch                          # is 1000 agents x 10 days under $100 yet, per model (--price adds models)
  python run.py ladder   --run-id L1 --max-usd 300   # staged egg-hunt tournament over souls + memories

Re-running any command with the same --run-id resumes it.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent.estimate import estimate, format_clock_estimate, format_estimate  # noqa: E402
from agent.runner import Run  # noqa: E402
from analysis.transcript import render  # noqa: E402


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def read_cfg(path: Path) -> dict:
    """A config may name another with `extends:`; its keys override that base."""
    path = Path(path)
    cfg = yaml.safe_load(path.read_text())
    base = cfg.pop("extends", None)
    return _merge(read_cfg(path.parent / base), cfg) if base else cfg


def load_cfg(args) -> dict:
    cfg = read_cfg(Path(args.config))
    if args.model:
        cfg["agent"]["model"] = args.model
    if getattr(args, "effort", None):
        cfg["agent"]["effort"] = args.effort
    if getattr(args, "agents", None):
        cfg["phase_a"]["n_agents"] = args.agents
    if getattr(args, "sessions", None):
        cfg["phase_a"]["n_sessions"] = args.sessions
    if getattr(args, "steps", None):
        cfg["agent"]["steps_per_session"] = args.steps
    if getattr(args, "parallel", None):
        cfg["phase_a"]["parallel_agents"] = args.parallel
    if getattr(args, "session_minutes", None) and cfg["agent"].get("clock"):
        c = cfg["agent"]["clock"]
        c["warn_before_seconds"] = float(c["warn_before_seconds"]) * args.session_minutes * 60 / float(c["session_seconds"])
        c["session_seconds"] = args.session_minutes * 60
    if not 1 <= cfg["phase_a"]["n_agents"] <= 10000:
        sys.exit("n_agents must be between 1 and 10000")
    if not 1 <= cfg["phase_a"]["n_sessions"] <= 500:
        sys.exit("n_sessions must be between 1 and 500")
    return cfg


def open_run(args, cfg) -> Run:
    max_usd = args.max_usd if args.max_usd is not None else cfg["budget"]["max_usd"]
    soul = Path(cfg["agent"]["soul_path"] if Path(cfg["agent"]["soul_path"]).is_absolute() else ROOT / cfg["agent"]["soul_path"]).read_text()
    return Run(ROOT / "runs" / args.run_id, cfg, soul, max_usd=max_usd, mock=args.mock)


def find_real_pilot() -> Path | None:
    for st in sorted((ROOT / "runs").glob("*/state.json")):
        s = json.loads(st.read_text())
        if s.get("meta", {}).get("kind") == "pilot" and not s["meta"].get("mock") and s["meta"].get("complete"):
            return st.parent
    return None


def report_stop(run: Run) -> None:
    print(f"\nSpent so far on this run: ${run.budget.spent:.4f} over {run.budget.calls} API calls (cap ${run.budget.max_usd:.2f}).")
    if run.stopped_reason:
        print(f"Stopped early: {run.stopped_reason}\nRe-run the same command with the same --run-id (and a higher --max-usd if needed) to resume.")


def cmd_pilot(args) -> None:
    cfg = load_cfg(args)
    p = cfg["pilot"]
    cfg["phase_a"].update(n_agents=p["n_agents"], n_sessions=p["n_sessions"], parallel_agents=1)
    full_steps = int(cfg["agent"]["steps_per_session"])
    cfg["agent"]["steps_per_session"] = p["steps_per_session"]
    if cfg["agent"].get("clock") and p.get("session_seconds"):
        full_secs = float(cfg["agent"]["clock"]["session_seconds"])
        cfg["agent"]["clock"]["session_seconds"] = p["session_seconds"]
        cfg["agent"]["clock"]["warn_before_seconds"] = float(cfg["agent"]["clock"]["warn_before_seconds"]) * p["session_seconds"] / full_secs
    args.run_id = args.run_id or time.strftime("pilot-%Y%m%d-%H%M%S")
    run = open_run(args, cfg)
    run.set_meta(kind="pilot", mock=run.mock)
    run.phase_a(p["n_agents"], p["n_sessions"], p["steps_per_session"], 1)
    done = all(v.get("done") for v in run.state["phase_a"].values()) and len(run.state["phase_a"]) == p["n_agents"] * p["n_sessions"]
    run.set_meta(complete=done)
    parts = [f"# Pilot {args.run_id}{' (MOCK model: costs are synthetic)' if run.mock else ''}", ""]
    for log in sorted((run.root / "phase_a").glob("*/session_??.jsonl")):
        parts.append(render(log))
    parts.append("## Notes directory at the end of the pilot\n")
    for f in sorted((run.root / "agents").glob("*/notes/**/*")):
        if f.is_file():
            parts += [f"### {f.relative_to(run.root)}", "```", f.read_text().rstrip(), "```", ""]
    parts.append(f"## Cost\n\nPilot spend: **${run.budget.spent:.4f}** over {run.budget.calls} API calls.\n")
    full_cfg = load_cfg(args)
    if full_cfg["agent"].get("clock"):
        parts += ["## Estimated cost of the configured free play", "", "```", format_clock_estimate(run.root, full_cfg), "```"]
        full_cfg = None
    try:
        if full_cfg is None:
            raise ValueError("free play only")
        est = estimate(run.root, full_cfg, model=run.cfg["agent"]["model"])
        parts += ["## Estimated cost of the full default run", "", "```", format_estimate(est, full_steps, full_cfg["pricing"][est["model"]]), "```"]
        if full_cfg["agent"]["model"] != "claude-opus-5-5":
            e2 = estimate(run.root, full_cfg, model="claude-opus-5-5")
            parts.append(f"\nSame run on claude-opus-5-5: ~${e2['total_usd']:.2f} (range ${e2['range_usd'][0]:.2f}-${e2['range_usd'][1]:.2f}).")
    except ValueError as e:
        if str(e) != "free play only":
            parts.append(f"(no estimate: {e})")
    text = "\n".join(parts)
    (run.root / "pilot_report.md").write_text(text)
    print(text)
    print(f"\nWritten to {run.root / 'pilot_report.md'}")
    report_stop(run)


def _require_pilot(args) -> None:
    if args.mock or args.skip_pilot_check:
        return
    if find_real_pilot() is None:
        sys.exit("No completed (non-mock) pilot found under runs/. Run `python run.py pilot --max-usd 3` and review it first.")


def cmd_freeplay(args) -> None:
    _require_pilot(args)
    cfg = load_cfg(args)
    run = open_run(args, cfg)
    if "kind" not in run.state.get("meta", {}):  # extending a pilot keeps it a pilot
        run.set_meta(kind="full", mock=run.mock)
    if args.sessions and args.sessions > run.cfg["phase_a"]["n_sessions"]:
        # more days for the same agents: they pick up from the memory they wrote
        run.cfg["phase_a"]["n_sessions"] = args.sessions
        (run.root / "config.yaml").write_text(yaml.safe_dump(run.cfg, sort_keys=False))
        print(f"Extending free play to {args.sessions} days per agent.")
    pa = run.cfg["phase_a"]
    run.phase_a(pa["n_agents"], pa["n_sessions"], run.cfg["agent"]["steps_per_session"], pa["parallel_agents"])
    report_stop(run)


def cmd_eval(args) -> None:
    _require_pilot(args)
    cfg = load_cfg(args)
    run = open_run(args, cfg)
    run.phase_b(parallel=args.parallel or run.cfg["phase_a"]["parallel_agents"])
    report_stop(run)


def cmd_all(args) -> None:
    cmd_freeplay(args)
    run = open_run(args, load_cfg(args))
    if not run.budget.stopped and all(v.get("done") for v in run.state["phase_a"].values()):
        cmd_eval(args)


def cmd_analyze(args) -> None:
    from analysis.report import build_report

    path = build_report(ROOT / "runs" / args.run_id)
    print(f"Report written to {path}")


def cmd_evolve(args) -> None:
    from analysis.evolution import build_evolution

    print(f"Evolution report written to {build_evolution(ROOT / 'runs' / args.run_id)}")


def cmd_viewer(args) -> None:
    from analysis.replay import write_viewer

    outs, n, bad = write_viewer(ROOT / "runs" / args.run_id, [ROOT / "runs" / r for r in (args.include or [])])
    print(f"Replay viewer for {n} sessions written to {outs[0]}")
    for sid, d in bad:
        print(f"  {sid}: replay diverged from the log at step {d['step']}")


def cmd_price_watch(args) -> None:
    """Is 1000 agents x 10 days under budget yet, for each priced model? --price adds models,
    e.g. --price my-model=0.2,0.8,0.02,0.25 (USD per million: input, output, cache read, cache write)."""
    from agent.estimate import price_watch

    cfg = load_cfg(args)
    pricing = dict(cfg["pricing"])
    for spec in args.price or []:
        name, vals = spec.split("=", 1)
        i, o, cr, cw = (float(v) for v in vals.split(","))
        pricing[name] = {"input": i, "output": o, "cache_read": cr, "cache_write": cw}
    print(price_watch(ROOT / "runs" / (args.run_id or "pilot-20261024-005431"), pricing, agents=args.agents or 1000,
                      days=args.sessions or 10, budget=args.max_usd or 100.0))


def cmd_estimate(args) -> None:
    cfg = load_cfg(args)
    root = ROOT / "runs" / args.run_id
    if cfg["agent"].get("clock"):
        print(format_clock_estimate(root, cfg))
        return
    e = estimate(root, cfg, model=args.model)
    print(format_estimate(e, cfg["agent"]["steps_per_session"], cfg["pricing"][e["model"]]))


def ladder_sessions(cfg: dict) -> int:
    """Upper bound on sessions in a ladder run (every agent clears every stage)."""
    lad = cfg["ladder"]
    n = len(lad["contestants"]) * int(lad.get("replicates", 1))
    per_agent = sum(int(s["free_sessions"]) + len(s["eval_seeds"]) for s in lad["stages"])
    transfer = 2 * len(lad["stages"][-1]["eval_seeds"]) if lad.get("transfer_check", True) else 0
    return n * (per_agent + transfer)


def cmd_ladder(args) -> None:
    from agent.ladder import Ladder, ladder_summary

    _require_pilot(args)
    cfg = load_cfg(args)
    if args.steps:
        cfg["ladder"]["steps_per_session"] = args.steps
    lad = Ladder(ROOT / "runs" / args.run_id, cfg, max_usd=args.max_usd if args.max_usd is not None else cfg["budget"]["max_usd"], mock=args.mock, base_dir=ROOT)
    lad.set_meta(kind="ladder", mock=lad.mock)
    print(f"Ladder: {len(lad.agents())} agents, at most {ladder_sessions(lad.cfg)} sessions.")
    graduates = lad.run(parallel=args.parallel or lad.cfg["phase_a"]["parallel_agents"])
    text = ladder_summary(lad.root)
    (lad.root / "ladder_report.md").write_text(text)
    print(text)
    print(f"Graduates: {', '.join(graduates) if graduates else 'none'}")
    report_stop(lad)


def cmd_ladder_estimate(args) -> None:
    cfg = load_cfg(args)
    if args.steps:
        cfg["ladder"]["steps_per_session"] = args.steps
    steps = int(cfg["ladder"].get("steps_per_session") or cfg["agent"]["steps_per_session"])
    n = ladder_sessions(cfg)
    from agent.estimate import session_cost, session_model

    model = args.model or cfg["agent"]["model"]
    m = session_model(ROOT / "runs" / args.run_id)
    per = session_cost(m, steps, cfg["pricing"][model])
    print(f"Ladder upper bound: {n} sessions x ~${per:.2f} ({model}, {steps} steps) = ~${n * per:.2f}"
          f" (range ${0.6 * n * per:.2f}-${1.8 * n * per:.2f}); eliminations make the real figure lower.")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("pilot", cmd_pilot), ("freeplay", cmd_freeplay), ("eval", cmd_eval), ("all", cmd_all), ("analyze", cmd_analyze), ("viewer", cmd_viewer), ("evolve", cmd_evolve), ("estimate", cmd_estimate),
                     ("ladder", cmd_ladder), ("ladder-estimate", cmd_ladder_estimate), ("price-watch", cmd_price_watch)]:
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        p.add_argument("--config", default=str(ROOT / "config.yaml"))
        p.add_argument("--run-id", required=name in ("freeplay", "eval", "all", "analyze", "viewer", "evolve", "estimate", "ladder", "ladder-estimate"))
        p.add_argument("--max-usd", type=float, help="hard spend cap for this run (USD)")
        p.add_argument("--model", help="e.g. claude-sonnet-5-5 or claude-opus-5-5")
        p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
        p.add_argument("--agents", type=int)
        p.add_argument("--sessions", type=int)
        p.add_argument("--steps", type=int)
        p.add_argument("--parallel", type=int)
        p.add_argument("--session-minutes", type=float, help="length of a simulated day (clock-based configs)")
        p.add_argument("--mock", action="store_true", help="use the scripted mock model (no API calls)")
        p.add_argument("--skip-pilot-check", action="store_true")
        if name == "price-watch":
            p.add_argument("--price", action="append", metavar="MODEL=IN,OUT,CACHE_READ,CACHE_WRITE", help="price a model not in config.yaml (USD per million tokens)")
        if name == "viewer":
            p.add_argument("--include", action="append", metavar="RUN_ID", help="also show this run (same island); repeatable")
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
