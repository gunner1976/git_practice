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
