"""One session: a fresh context, a reset world, a fixed budget of world actions."""

from __future__ import annotations

import json
import time
from pathlib import Path

from world import World
from world.rules import ground_truth

from .client import block_to_dict
from .cost import Budget
from .notes import Notes
from .tools import ALL_TOOLS, NOTES_NAMES, WORLD_NAMES, run_notes_tool, run_world_tool


class JsonlLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = self.path.open("w")

    def __call__(self, kind: str, **data) -> None:
        self.f.write(json.dumps({"ts": round(time.time(), 3), "kind": kind, **data}, default=str) + "\n")
        self.f.flush()

    def close(self) -> None:
        self.f.close()


def run_session(
    *,
    cfg: dict,
    client,
    budget: Budget,
    world: World,
    notes: Notes,
    soul: str,
    log: JsonlLog,
    steps: int,
    opening: str,
    meta: dict,
) -> dict:
    a = cfg["agent"]
    world.reset()
    show_left = bool(a["show_steps_remaining"])

    def status(used: int) -> str:
        return f"\nMoments left today: {steps - used}" if show_left else ""

    first_obs = world.observe()
    messages: list = [{"role": "user", "content": f"{opening}\n\n{first_obs}{status(0)}"}]
    log("session_start", **meta, steps=steps, soul=soul, opening=opening, world_seed=world.seed, hidden_rules=ground_truth(world))
    log("observation", step=0, text=first_obs)

    used = notes_ops = calls = nudges = 0
    grace: int | None = None
    last_cost = 0.0
    end_reason = "unknown"
    spawn_steps: list[int] = []
    rule_fires: dict[str, list[int]] = {}

    while True:
        if calls >= int(a["max_api_calls_per_session"]):
            end_reason = "max_api_calls"
            break
        if grace is not None and grace <= 0:
            end_reason = "steps_exhausted"
            break
        budget.check(last_cost * 1.25)  # raises BudgetExceeded
        resp = client.create(soul, ALL_TOOLS, messages)
        calls += 1
        if grace is not None:
            grace -= 1
        model = getattr(resp, "model", a["model"]) or a["model"]
        u, last_cost = budget.record(model, resp.usage, {**meta, "call": calls, "step": used})
        content = [block_to_dict(b) for b in resp.content]
        log(
            "assistant",
            call=calls,
            step=used,
            stop_reason=resp.stop_reason,
            model=model,
            fallback=client.fallback_ran(resp),
            usage=u,
            cost_usd=last_cost,
            content=[{k: v for k, v in c.items() if k != "signature"} for c in content if c.get("type") != "thinking" or c.get("thinking")],
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "refusal":
            log("refusal", details=block_to_dict(resp.stop_details) if resp.stop_details else None)
            end_reason = "refusal"
            break

        tool_uses = [c for c in content if c.get("type") == "tool_use"]
        if not tool_uses:
            if grace is not None:
                end_reason = "steps_exhausted"
                break
            nudges += 1
            if nudges > int(a["max_stop_nudges"]):
                end_reason = "agent_stopped"
                break
            log("stop_hook", n=nudges)
            messages.append({"role": "user", "content": f"{a['stop_hook_message']}\n\n{world.observe()}{status(used)}"})
            continue

        results: list[dict] = []
        last_world_idx = None
        for tu in tool_uses:
            name, args = tu["name"], tu.get("input") or {}
            if name in WORLD_NAMES:
                if grace is not None or used >= steps:
                    msg, err = "The day is over; nothing more can happen in the world today.", True
                    log("action_refused", name=name, input=args)
                else:
                    msg, err = run_world_tool(world, name, args)
                    used += 1
                    events = world.drain_events()
                    for e in events:
                        if e.get("hidden_rule"):
                            rule_fires.setdefault(e.get("rule", "rock_spawn"), []).append(used)
                            if e.get("type") == "spawn":
                                spawn_steps.append(used)
                            log("hidden_rule_fired", step=used, event=e)
                    log("action", step=used, name=name, input=args, result=msg, error=err, events=events)
                    last_world_idx = len(results)
            elif name in NOTES_NAMES:
                notes_ops += 1
                if notes_ops > int(a["max_notes_ops_per_session"]):
                    msg, err, diff = "You have used your notes enough for today.", True, None
                else:
                    msg, err, diff = run_notes_tool(notes, name, args)
                log("tool_call", step=used, name=name, input=args, result=msg[:4000], error=err)
                if diff:
                    log("notes_diff", step=used, **diff)
            else:
                msg, err = f"Unknown tool {name}.", True
            results.append({"type": "tool_result", "tool_use_id": tu["id"], "content": msg, **({"is_error": True} if err else {})})

        if last_world_idx is not None:
            obs = world.observe()
            log("observation", step=used, text=obs)
            r = results[last_world_idx]
            r["content"] = f"{r['content']}\n\n{obs}{status(used)}"
        user_content: list = list(results)
        if used >= steps and grace is None:
            grace = int(a["end_grace_turns"])
            user_content.append({"type": "text", "text": a["session_end_message"]})
            log("session_ending", step=used)
        messages.append({"role": "user", "content": user_content})

    state = world.state()
    log("session_end", reason=end_reason, steps_used=used, api_calls=calls, notes_ops=notes_ops, nudges=nudges, world=state, spawn_steps=spawn_steps, rule_fires=rule_fires)
    return {"end_reason": end_reason, "steps_used": used, "api_calls": calls, "spawn_steps": spawn_steps, "rule_fires": rule_fires}
