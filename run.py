#!/usr/bin/env python3
"""Eko replication harness CLI.

  python run.py pilot    --max-usd 3                 # 1 agent, 2 sessions, 30 steps; prints transcript, notes, cost, estimate
  python run.py freeplay --run-id main --max-usd 60  # Phase A (refuses to start before a real pilot exists)
  python run.py eval     --run-id main --max-usd 60  # Phase B on the same run
  python run.py all      --run-id main --max-usd 120 # Phase A then Phase B
  python run.py analyze  --run-id main               # stats, discovery, play markers, report.md + charts
  python run.py estimate --run-id <pilot-id>         # re-print the full-run estimate from a pilot

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

from agent.estimate import estimate, format_estimate  # noqa: E402
from agent.runner import Run  # noqa: E402
from analysis.transcript import render  # noqa: E402


def load_cfg(args) -> dict:
    cfg = yaml.safe_load(Path(args.config).read_text())
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
    if not 1 <= cfg["phase_a"]["n_agents"] <= 13:
        sys.exit("n_agents must be between 1 and 13")
    if not 1 <= cfg["phase_a"]["n_sessions"] <= 30:
        sys.exit("n_sessions must be between 1 and 30")
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
    try:
        est = estimate(run.root, full_cfg, model=run.cfg["agent"]["model"])
        parts += ["## Estimated cost of the full default run", "", "```", format_estimate(est, full_steps, full_cfg["pricing"][est["model"]]), "```"]
        if full_cfg["agent"]["model"] != "claude-opus-5-5":
            e2 = estimate(run.root, full_cfg, model="claude-opus-5-5")
            parts.append(f"\nSame run on claude-opus-5-5: ~${e2['total_usd']:.2f} (range ${e2['range_usd'][0]:.2f}-${e2['range_usd'][1]:.2f}).")
    except ValueError as e:
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
    run.set_meta(kind="full", mock=run.mock)
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


def cmd_estimate(args) -> None:
    cfg = load_cfg(args)
    root = ROOT / "runs" / args.run_id
    e = estimate(root, cfg, model=args.model)
    print(format_estimate(e, cfg["agent"]["steps_per_session"], cfg["pricing"][e["model"]]))


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("pilot", cmd_pilot), ("freeplay", cmd_freeplay), ("eval", cmd_eval), ("all", cmd_all), ("analyze", cmd_analyze), ("estimate", cmd_estimate)]:
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        p.add_argument("--config", default=str(ROOT / "config.yaml"))
        p.add_argument("--run-id", required=name in ("freeplay", "eval", "all", "analyze", "estimate"))
        p.add_argument("--max-usd", type=float, help="hard spend cap for this run (USD)")
        p.add_argument("--model", help="e.g. claude-sonnet-5-5 or claude-opus-5-5")
        p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
        p.add_argument("--agents", type=int)
        p.add_argument("--sessions", type=int)
        p.add_argument("--steps", type=int)
        p.add_argument("--parallel", type=int)
        p.add_argument("--mock", action="store_true", help="use the scripted mock model (no API calls)")
        p.add_argument("--skip-pilot-check", action="store_true")
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
