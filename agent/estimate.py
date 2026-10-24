"""Extrapolate the cost of a full run from a pilot's ledger.

The prompt grows roughly linearly within a session (each action appends an
observation), so per-call prompt size is fit as  P(step) = a + b*step  and the
session cost is  K * (a + b*S/2) * effective_input_price + K * out_tokens * output_price,
with K = calls-per-step * S. The effective input price uses the pilot's own mix
of uncached / cache-read / cache-write tokens, so it reflects the cache hit
rate actually achieved, repriced for whichever model is being estimated.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def _load(root: Path) -> list[dict]:
    p = Path(root) / "ledger.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def eff_in_per_tok(m: dict, price: dict) -> float:
    return sum(m["mix"][k] * price[k] for k in m["mix"]) / 1e6


def session_model(root: Path) -> dict:
    rows = [r for r in _load(root) if r.get("phase") == "A"]
    if not rows:
        raise ValueError("pilot ledger has no Phase A calls")
    steps = np.array([r["step"] for r in rows], float)
    prompt = np.array([r["usage"]["input_tokens"] + r["usage"]["cache_read_input_tokens"] + r["usage"]["cache_creation_input_tokens"] for r in rows], float)
    out = np.array([r["usage"]["output_tokens"] for r in rows], float)
    b, a = np.polyfit(steps, prompt, 1) if len(set(steps)) > 1 else (0.0, prompt.mean())
    mix = {k: sum(r["usage"][f] for r in rows) / prompt.sum() for k, f in
           (("input", "input_tokens"), ("cache_read", "cache_read_input_tokens"), ("cache_write", "cache_creation_input_tokens"))}
    sessions = {(r["agent"], r["session"]) for r in rows}
    max_step = {}
    for r in rows:
        k = (r["agent"], r["session"])
        max_step[k] = max(max_step.get(k, 0), r["step"])
    total_steps = sum(max_step.values()) or 1
    return {
        "a": float(a),
        "b": float(b),
        "mix": mix,  # share of prompt tokens that were uncached / cache reads / cache writes
        "out_tokens_per_call": float(out.mean()),
        "calls_per_step": len(rows) / total_steps,
        "pilot_cost": sum(r["cost_usd"] for r in rows),
        "pilot_sessions": len(sessions),
        "pilot_calls": len(rows),
    }


def session_cost(m: dict, steps: int, price: dict) -> float:
    k = m["calls_per_step"] * steps
    return k * (m["a"] + m["b"] * steps / 2) * eff_in_per_tok(m, price) + k * m["out_tokens_per_call"] * price["output"] / 1e6


def estimate(root: Path, cfg: dict, model: str | None = None) -> dict:
    m = session_model(root)
    model = model or cfg["agent"]["model"]
    price = cfg["pricing"][model]
    steps = int(cfg["agent"]["steps_per_session"])
    n, s = int(cfg["phase_a"]["n_agents"]), int(cfg["phase_a"]["n_sessions"])
    n_tasks = len(cfg["phase_b"]["tasks"])
    n_fresh = int(cfg["phase_b"]["n_fresh"] or n)
    per = session_cost(m, steps, price)
    a_cost = n * s * per
    b_cost = n_tasks * (n + n_fresh) * per
    total = a_cost + b_cost
    return {
        "model": model,
        "fit": m,
        "per_session_usd": per,
        "phase_a_sessions": n * s,
        "phase_b_sessions": n_tasks * (n + n_fresh),
        "phase_a_usd": a_cost,
        "phase_b_usd": b_cost,
        "total_usd": total,
        "range_usd": (0.6 * total, 1.8 * total),
    }


def format_estimate(e: dict, steps: int, price: dict) -> str:
    f = e["fit"]
    return "\n".join([
        f"Pilot: {f['pilot_sessions']} sessions, {f['pilot_calls']} API calls, ${f['pilot_cost']:.4f}",
        f"Fit: prompt tokens per call = {f['a']:.0f} + {f['b']:.1f} x step; {f['calls_per_step']:.2f} calls/step; "
        f"{f['out_tokens_per_call']:.0f} output tokens/call; effective input ${eff_in_per_tok(f, price) * 1e6:.3f}/MTok "
        f"(cache-read share {f['mix']['cache_read']:.0%})",
        f"Model {e['model']}: ~${e['per_session_usd']:.2f} per {steps}-step session",
        f"Phase A: {e['phase_a_sessions']} sessions ~ ${e['phase_a_usd']:.2f}",
        f"Phase B: {e['phase_b_sessions']} sessions ~ ${e['phase_b_usd']:.2f}",
        f"Total ~ ${e['total_usd']:.2f}  (plausible range ${e['range_usd'][0]:.2f} - ${e['range_usd'][1]:.2f})",
    ])


def clock_model(root: Path) -> dict:
    """Pilot fit for clock-based (paper) sessions: prompt tokens per call against the
    call's index within its session, and simulated seconds per call."""
    rows = [r for r in _load(root) if r.get("phase") == "A" and "clock" in r]
    if not rows:
        raise ValueError("pilot ledger has no clock-based Phase A calls")
    idx = np.array([r["call"] for r in rows], float)
    prompt = np.array([r["usage"]["input_tokens"] + r["usage"]["cache_read_input_tokens"] + r["usage"]["cache_creation_input_tokens"] for r in rows], float)
    b, a = np.polyfit(idx, prompt, 1) if len(set(idx)) > 1 else (0.0, prompt.mean())
    mix = {k: sum(r["usage"][f] for r in rows) / prompt.sum() for k, f in
           (("input", "input_tokens"), ("cache_read", "cache_read_input_tokens"), ("cache_write", "cache_creation_input_tokens"))}
    last: dict = {}
    for r in rows:
        last[(r["agent"], r["session"])] = max(last.get((r["agent"], r["session"]), 0.0), float(r["clock"]))
    return {
        "a": float(a), "b": float(b), "mix": mix,
        "out_tokens_per_call": float(np.mean([r["usage"]["output_tokens"] for r in rows])),
        "seconds_per_call": sum(last.values()) / len(rows),
        "pilot_cost": sum(r["cost_usd"] for r in rows), "pilot_sessions": len(last), "pilot_calls": len(rows),
    }


def clock_session_cost(m: dict, seconds: float, cap_tokens: float, price: dict) -> tuple[float, int]:
    k = max(1, int(seconds / max(m["seconds_per_call"], 1e-6)))
    tokens = sum(min(m["a"] + m["b"] * i, cap_tokens) for i in range(1, k + 1))
    return tokens * eff_in_per_tok(m, price) + k * m["out_tokens_per_call"] * price["output"] / 1e6, k


def format_clock_estimate(root: Path, cfg: dict) -> str:
    m = clock_model(root)
    a = cfg["agent"]
    secs = float(a["clock"]["session_seconds"])
    cap = float(a.get("context_prune_chars") or 4e6) / 3.5
    n, s = int(cfg["phase_a"]["n_agents"]), int(cfg["phase_a"]["n_sessions"])
    lines = [f"Pilot: {m['pilot_sessions']} sessions, {m['pilot_calls']} API calls, ${m['pilot_cost']:.4f}",
             f"Fit: prompt tokens per call = {m['a']:.0f} + {m['b']:.1f} x call (capped near {cap:,.0f} by context clearing); "
             f"{m['seconds_per_call']:.1f} simulated s/call; {m['out_tokens_per_call']:.0f} output tokens/call"]
    for model in dict.fromkeys([a["model"], "claude-sonnet-5-5", "claude-opus-5-5"]):
        if model not in cfg["pricing"]:
            continue
        per, k = clock_session_cost(m, secs, cap, cfg["pricing"][model])
        tot = n * s * per
        lines.append(f"{model}: ~{k} calls and ~${per:.2f} per {secs / 60:.0f}-minute day; {n} agents x {s} days ~ ${tot:.2f}"
                     f" (range ${0.6 * tot:.2f}-${1.8 * tot:.2f}; memory in the prompt grows over the days, so later days cost more)")
    return "\n".join(lines)


def token_profile(root: Path) -> dict:
    """Average tokens per call and calls per simulated agent-day, from a clock-based run's ledger."""
    rows = [r for r in _load(root) if r.get("phase") == "A" and "clock" in r]
    if not rows:
        raise ValueError(f"{root} has no clock-based Phase A calls")
    n = len(rows)
    avg = {k: sum(r["usage"][f] for r in rows) / n for k, f in
           (("input", "input_tokens"), ("output", "output_tokens"), ("cache_read", "cache_read_input_tokens"), ("cache_write", "cache_creation_input_tokens"))}
    last: dict = {}
    for r in rows:
        last[(r["agent"], r["session"])] = max(last.get((r["agent"], r["session"]), 0.0), float(r["clock"]))
    return {"per_call": avg, "seconds": sum(last.values()), "calls": n, "model": rows[0].get("model")}


def price_watch(root: Path, pricing: dict, agents: int = 1000, days: int = 10, day_minutes: float = 20, budget: float = 100.0) -> str:
    """Cost of `agents` x `days` free-play days for every priced model, using the token profile
    measured in `root` (so the behaviour assumed is that run's). Batch = 50% off."""
    p = token_profile(root)
    calls_per_day = p["calls"] / (p["seconds"] / (day_minutes * 60))
    agent_days = agents * days
    lines = [f"Profile from {Path(root).name} ({p['model']}): {calls_per_day:.0f} calls per {day_minutes:g}-minute day; per call "
             + ", ".join(f"{k} {v:,.0f}" for k, v in p["per_call"].items()) + " tokens",
             f"Target: {agents} agents x {days} days = {agent_days:,} agent-days for under ${budget:,.0f}"
             f" (= ${budget / agent_days:.4f} per agent-day)", "",
             f"{'model':24s} {'per agent-day':>14s} {'total':>12s} {'with batch':>12s}  verdict"]
    for model, pr in sorted(pricing.items(), key=lambda kv: kv[1]["output"]):
        per = calls_per_day * sum(p["per_call"][k] * pr[k] for k in p["per_call"]) / 1e6
        tot = per * agent_days
        ok = "UNDER budget" if tot < budget else ("under with batch" if tot / 2 < budget else f"needs {tot / budget:.0f}x cheaper")
        lines.append(f"{model:24s} {'$' + format(per, '.4f'):>14s} {'$' + format(tot, ',.0f'):>12s} {'$' + format(tot / 2, ',.0f'):>12s}  {ok}")
    return "\n".join(lines)
