"""One session: a fresh context, a reset world, a fixed budget of world actions."""

from __future__ import annotations

import datetime as dt
import json
import math
import time
from pathlib import Path

from world import World
from world.rules import ground_truth

from .client import block_to_dict
from .cost import Budget, usage_dict
from .notes import Notes
from .tools import calculate, extra_tools, run_notes_tool, run_world_tool, tool_set


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


def paper_system_prompt(prompt: str, notes: Notes) -> str:
    """Paper App. A.1: SOUL.md, SEMANTIC_MEMORY.md and the timestamp + summary of each
    EPISODIC_MEMORY.jsonl line are appended to the system prompt at session start."""
    files = notes.dump()
    parts = [prompt.rstrip(), "", "Initial workspace memory files at session start:",
             "These are the file contents as they existed when this session began."]
    for name in ("SOUL.md", "SEMANTIC_MEMORY.md"):
        if name in files:
            parts += ["", f"## {name}", files[name].rstrip()]
    if "EPISODIC_MEMORY.jsonl" in files:
        lines = []
        for line in files["EPISODIC_MEMORY.jsonl"].splitlines():
            try:
                e = json.loads(line)
                lines.append(json.dumps({"timestamp": e.get("timestamp"), "summary": e.get("summary")}, ensure_ascii=False))
            except (json.JSONDecodeError, AttributeError):
                continue
        parts += ["", "## EPISODIC_MEMORY.jsonl (timestamp and summary of each entry)", *lines]
    return "\n".join(parts)


def prune_context(messages: list, limit_chars: int, keep_fraction: float = 0.5) -> int:
    """Stand-in for a coding agent's context compaction. Once the conversation passes
    `limit_chars`, the oldest turns (after the opening message) are dropped until it is
    back under `keep_fraction` of the limit, and a note saying so is added to the opening
    message. Trimming well below the limit means it happens rarely, so the prompt cache
    is rebuilt once per trim instead of on every turn. Returns the number of messages dropped."""
    size = lambda ms: len(json.dumps(ms, default=str))  # noqa: E731
    if len(messages) < 4 or size(messages) <= limit_chars:
        return 0
    target = limit_chars * keep_fraction
    cut = 1
    while cut < len(messages) - 2 and size(messages[:1] + messages[cut:]) > target:
        cut += 1
    while cut < len(messages) - 1 and messages[cut].get("role") != "assistant":
        cut += 1  # the kept part must start with an assistant turn, right after the opening message
    if cut <= 1:
        return 0
    dropped = cut - 1
    del messages[1:cut]
    note = "[Earlier turns from this session were cleared to save space. Your workspace files are unchanged.]"
    first = messages[0]
    if isinstance(first.get("content"), str) and note not in first["content"]:
        first["content"] = f"{first['content']}\n\n{note}"
    return dropped


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
    start_state: dict | None = None,
) -> dict:
    a = cfg["agent"]
    world.reset()
    if start_state:  # the world persists: the island is as the agent left it
        world.set_state(start_state, avatar=bool(cfg["world"].get("persist_avatar", True)))
    show_left = bool(a["show_steps_remaining"])
    tools, world_names, notes_names, query_names = tool_set(cfg)
    extras = extra_tools(cfg)
    tools = tools + extras
    extra_names = {t["name"] for t in extras}
    clk = a.get("clock")  # paper mode: the session is an hour of simulated wall-clock time
    clock = 0.0
    warned = False
    if clk:
        steps = 10**9
        start_utc = dt.datetime.fromisoformat(clk["start_utc"].replace("Z", "+00:00")) + dt.timedelta(hours=int(meta.get("session") or 1) - 1)

    eko = getattr(world, "eko", None)
    # EKO time: the session starts at a dawn (carried over from the last session by the runner, or
    # the session's own day) and runs at one EKO day per session_seconds of activity, plus any time
    # the agent spends waiting. A session may span several EKO days (clock.days_per_session): the
    # awake budget stays the same, so only waiting can cover the extra days.
    slept = 0.0
    if eko is not None and clk:
        ss = float(clk["session_seconds"])
        start_tau = float(meta["eko_start_tau"]) if meta.get("eko_start_tau") is not None else eko.session_tau(int(meta.get("session") or 1), 0.0, ss)
        span_end = start_tau + float(clk.get("days_per_session", 1)) * eko.day
        warn_tau = eko.day * float(clk["warn_before_seconds"]) / ss

    def eko_tau() -> float:
        return start_tau + eko.day * clock / ss + slept

    def near_end() -> bool:
        """Inside the end-of-day warning window: of the awake budget, or of the session's EKO span."""
        return clock >= float(clk["session_seconds"]) - float(clk["warn_before_seconds"]) or (eko is not None and eko_tau() >= span_end - warn_tau)

    def day_frac() -> dict:
        """Fraction of the EKO day since dawn, for the replay's daylight."""
        return {"df": round(((eko_tau() - eko.day / 4) / eko.day) % 1.0, 4)} if eko is not None and clk else {}

    def wait(hours) -> tuple[str, bool, dict]:
        nonlocal slept
        try:
            h = max(0.0, min(float(hours), 200.0))
        except (TypeError, ValueError):
            return "Wait needs a number of hours.", True, {}
        t0 = eko_tau()
        limit = max(t0, span_end - warn_tau)  # waiting stops where the end-of-day warning begins
        target, t, reason = min(t0 + h * 3600.0, limit), t0, "time passed"
        a_ = world.avatar
        before = eko.senses(a_.x, a_.y, t0)
        names = (("the sun rose", "the sun set"), ("the moon rose", "the moon set"), ("the moon's light changed", "the moon's light changed"))
        while t < target:
            t = min(target, t + 600.0)  # look up every 10 EKO minutes
            now = eko.senses(a_.x, a_.y, t)
            changed = [names[i][0 if now[i] else 1] for i in range(3) if now[i] != before[i]]
            if changed:
                reason = changed[0]
                break
        slept += t - t0
        return json.dumps({"lastActionResult": "WaitSuccess", "waited_hours": round((t - t0) / 3600.0, 2), "woke": reason, "time": now_iso()}), False, \
            {"hours_asked": h, "hours": round((t - t0) / 3600.0, 3), "woke": reason}

    def now_iso() -> str:
        if eko is not None and clk:  # EKO's own clock: its days and hours
            base = dt.datetime.fromisoformat(clk["start_utc"].replace("Z", "+00:00"))
            return (base + dt.timedelta(seconds=eko_tau())).strftime("%Y-%m-%dT%H:%M:%SZ")
        return (start_utc + dt.timedelta(seconds=clock)).strftime("%Y-%m-%dT%H:%M:%SZ") if clk else ""

    def status(used: int) -> str:
        return f"\nMoments left today: {steps - used}" if show_left else ""

    if a.get("memory_injection") == "paper":
        soul = paper_system_prompt(soul, notes)
    elif a.get("inject_notes"):
        # paper App. A.1: memory is appended to the system prompt at each session start
        files = notes.dump()
        if files:
            soul = soul + "\n\n# Your notes as they were when this day began\n" + "\n".join(f"\n## {k}\n{v}" for k, v in files.items())
    first_obs = world.observe()
    first = f"{opening}\n\n{first_obs}{status(0)}" if a.get("initial_observation", True) else opening
    messages: list = [{"role": "user", "content": first}]
    log("session_start", **meta, steps=steps, soul=soul, opening=opening, world_seed=world.seed, hidden_rules=ground_truth(world),
        **({"achievements": dict(world.achievements)} if getattr(world, "mission", None) else {}),
        **({"start_state": world.state()} if start_state else {}))
    if a.get("initial_observation", True):
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
        if clk and clock >= float(clk["session_seconds"]):
            end_reason = "session_time_up"
            break
        if eko is not None and clk and eko_tau() >= span_end:
            end_reason = "session_span_over"
            break
        budget.check(last_cost * 1.25)  # raises BudgetExceeded
        if a.get("context_prune_chars"):
            n_cleared = prune_context(messages, int(a["context_prune_chars"]))
            if n_cleared:
                log("context_pruned", step=used, cleared=n_cleared, messages_left=len(messages))
        resp = client.create(soul, tools, messages)
        calls += 1
        if grace is not None:
            grace -= 1
        model = getattr(resp, "model", a["model"]) or a["model"]
        if clk:
            clock += float(clk["turn_seconds"]) + float(clk["seconds_per_output_token"]) * usage_dict(resp.usage)["output_tokens"]
        u, last_cost = budget.record(model, resp.usage, {**meta, "call": calls, "step": used, **({"clock": round(clock, 1)} if clk else {})})
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
            if clk:  # time spent idle between the agent stopping and the nudge (0 = just the turn's latency)
                clock += float(clk.get("idle_seconds", 0.0))
            hook = a["stop_hook_message"] if not a.get("stop_hook_observation", True) else f"{a['stop_hook_message']}\n\n{world.observe()}{status(used)}"
            heard = world.notices() if hasattr(world, "notices") else []
            if heard:
                log("heard", step=used, texts=heard, **({"clock": round(clock, 1)} if clk else {}))
                hook = f"{hook}\n\n" + "\n".join(heard)
            hook_content: list | str = hook
            if clk and not warned and near_end():
                warned = True
                log("reset_warning", step=used, clock=round(clock, 1))
                hook_content = f"{hook}\n\n{clk['warn_message']}"
            messages.append({"role": "user", "content": hook_content})
            continue

        results: list[dict] = []
        last_world_idx = None
        for tu in tool_uses:
            name, args = tu["name"], tu.get("input") or {}
            if name in world_names:
                if grace is not None or used >= steps:
                    msg, err = "The day is over; nothing more can happen in the world today.", True
                    log("action_refused", name=name, input=args)
                else:
                    ax0, ay0 = world.avatar.x, world.avatar.y
                    msg, err = run_world_tool(world, name, args)
                    if clk:
                        walked = math.hypot(world.avatar.x - ax0, world.avatar.y - ay0)
                        clock += float(clk["action_seconds"]) + walked / float(clk["walk_speed"])
                    used += 1
                    events = world.drain_events()
                    for e in events:
                        if e.get("hidden_rule"):
                            rule_fires.setdefault(e.get("rule", "rock_spawn"), []).append(used)
                            if e.get("type") == "spawn":
                                spawn_steps.append(used)
                            log("hidden_rule_fired", step=used, event=e)
                    log("action", step=used, name=name, input=args, result=msg, error=err, events=events, **({"clock": round(clock, 1)} if clk else {}), **day_frac())
                    for e in events:
                        if e.get("type") == "achievement":
                            log("achievement", step=used, name=e["name"])
                    last_world_idx = len(results)
            elif name in extra_names:
                if clk:
                    clock += float(clk["query_seconds"])
                if name == "wait":
                    msg, err, info = wait(args.get("hours")) if eko is not None and clk else ("Nothing happens.", True, {})
                    log("wait", step=used, **info, **({"clock": round(clock, 1)} if clk else {}), **day_frac())
                elif name == "calculate":
                    try:
                        msg, err = calculate(str(args.get("expression", ""))), False
                    except Exception as e:  # noqa: BLE001 - any bad expression goes back to the agent
                        msg, err = f"Could not evaluate: {e}", True
                else:  # answer
                    try:
                        value = float(args["value"])
                        msg, err = "The voice hears your answer.", False
                        log("answer", step=used, value=value, units=str(args.get("units", "")), explanation=str(args.get("explanation", "")),
                            **({"clock": round(clock, 1)} if clk else {}))
                    except (KeyError, TypeError, ValueError):
                        msg, err = "An answer needs a numeric value.", True
                log("tool_call", step=used, name=name, input=args, result=msg[:4000], error=err)
            elif name in query_names:
                if clk and hasattr(world, "day_fraction"):
                    world.day_fraction = min(1.0, clock / float(clk["session_seconds"]))
                if clk and eko is not None:
                    world.sky_tau = eko_tau()
                msg, err = world.observe_json({"time": now_iso()}), False
                seen = world.drain_events() if getattr(world, "mission", None) else []
                if seen:  # an observation can complete a trial (the eclipse) or reveal the tablet
                    log("world_events", step=used, events=seen)
                    for e in seen:
                        if e.get("type") == "achievement":
                            log("achievement", step=used, name=e["name"])
                if clk:
                    clock += float(clk["query_seconds"])
                log("tool_call", step=used, name=name, input=args, result=msg[:20000], error=err)  # keep what the agent saw (the night sky is long)
            elif name in notes_names:
                if clk:
                    clock += float(clk["query_seconds"])
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

        if last_world_idx is not None and not clk:
            obs = world.observe()
            log("observation", step=used, text=obs)
            r = results[last_world_idx]
            r["content"] = f"{r['content']}\n\n{obs}{status(used)}"
        user_content: list = list(results)
        heard = world.notices() if hasattr(world, "notices") else []
        if heard:  # what reaches the agent unbidden: an announcement, a ringing phone, a voice
            log("heard", step=used, texts=heard, **({"clock": round(clock, 1)} if clk else {}))
            user_content.append({"type": "text", "text": "\n".join(heard)})
        if clk and not warned and near_end():
            warned = True
            log("reset_warning", step=used, clock=round(clock, 1))
            user_content.append({"type": "text", "text": clk["warn_message"]})
        if used >= steps and grace is None:
            grace = int(a["end_grace_turns"])
            user_content.append({"type": "text", "text": a["session_end_message"]})
            log("session_ending", step=used)
        messages.append({"role": "user", "content": user_content})

    state = world.state()
    log("session_end", reason=end_reason, steps_used=used, api_calls=calls, notes_ops=notes_ops, nudges=nudges, world=state, spawn_steps=spawn_steps,
        rule_fires=rule_fires, **({"clock_seconds": round(clock, 1)} if clk else {}),
        **({"eko_tau_start": round(start_tau, 1), "eko_tau_end": round(eko_tau(), 1), "eko_hours_waited": round(slept / 3600.0, 2)} if eko is not None and clk else {}))
    return {"end_reason": end_reason, "steps_used": used, "api_calls": calls, "spawn_steps": spawn_steps, "rule_fires": rule_fires,
            **({"clock_seconds": round(clock, 1)} if clk else {}),
            **({"eko_tau_end": round(eko_tau(), 1), "eko_hours_waited": round(slept / 3600.0, 2)} if eko is not None and clk else {})}
