"""Model clients: the real Anthropic API, and a scripted mock for tests / dry runs."""

from __future__ import annotations

import json
import math
import random
import re
from types import SimpleNamespace

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicClient:
    def __init__(self, model: str, effort: str, max_tokens: int, refusal_fallback: bool, thinking_display: str = "summarized"):
        import anthropic  # imported lazily so tests and mock runs don't need a key

        self.anthropic = anthropic
        self.client = anthropic.Anthropic(max_retries=4)  # reads ANTHROPIC_API_KEY
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
        self.refusal_fallback = refusal_fallback
        self.thinking_display = thinking_display
        self.mock = False

    def create(self, system: str, tools: list[dict], messages: list):
        kwargs = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            tools=tools,
            messages=messages,
            output_config={"effort": self.effort},
            # adaptive thinking is the default on these models; "summarized" makes the
            # reasoning readable in transcripts (billing is the same either way)
            thinking={"type": "adaptive", "display": self.thinking_display},
            cache_control={"type": "ephemeral"},  # auto-caches the growing session prefix
        )
        if self.refusal_fallback:
            return self.client.beta.messages.create(betas=[FALLBACK_BETA], fallbacks="default", **kwargs)
        return self.client.messages.create(**kwargs)

    @staticmethod
    def fallback_ran(resp) -> bool:
        return any(getattr(e, "type", None) == "fallback_message" for e in (getattr(resp.usage, "iterations", None) or []))


def block_to_dict(b) -> dict:
    if isinstance(b, dict):
        return b
    return b.model_dump(mode="json", exclude_none=True)


class MockClient:
    """A cheap scripted 'agent' that wanders, fiddles with objects, sometimes throws
    the rock hard and writes notes. Usage numbers are synthetic (chars / 4)."""

    def __init__(self, model: str = "mock", seed: int = 0, **_):
        self.model = model
        self.rng = random.Random(seed)
        self.mock = True
        self.n = 0
        self.target: str | None = None

    @staticmethod
    def fallback_ran(resp) -> bool:
        return False

    @staticmethod
    def _last_obs(messages) -> str:
        for m in reversed(messages):
            c = m["content"] if isinstance(m, dict) else None
            texts = [c] if isinstance(c, str) else [x.get("content", "") for x in (c or []) if isinstance(x, dict) and isinstance(x.get("content"), str)]
            for t in reversed(texts):
                if "You are at (" in t:
                    return t
        return ""

    @staticmethod
    def _parse(obs: str):
        m = re.search(r"You are at \(([-\d.]+), ([-\d.]+), ([-\d.]+)\), holding (\S+)\.", obs)
        me = (float(m.group(1)), float(m.group(2)), m.group(4).rstrip(".")) if m else (0.0, 0.0, "nothing")
        objs = {g[0]: (float(g[1]), float(g[2])) for g in re.findall(r"^(\w+_\d+): \w+ \w+ @ ([-\d.]+) ([-\d.]+)", obs, re.M)}
        return me, objs

    def create(self, system: str, tools: list[dict], messages: list):
        self.n += 1
        r = self.rng
        last = messages[-1]["content"]
        last_text = json.dumps(last) if not isinstance(last, str) else last
        (ax, ay, holding), objs = self._parse(self._last_obs(messages))
        if self.n == 1:
            calls = [("list_notes", {})]
        elif "light is fading" in last_text:
            calls = [("write_note", {"path": "journal.md", "content": f"Day {self.n}: I threw the rock hard and a new cube appeared.\nRule: count the throws.\n"})]
        elif "nothing more can happen" in last_text.lower():
            return self._resp([("text", "I'll rest.")], stop="end_turn", messages=messages)
        elif r.random() < 0.05:
            return self._resp([("text", "Hmm.")], stop="end_turn", messages=messages)
        elif r.random() < 0.05:
            calls = [("write_note", {"path": "games.md", "content": "Let's call the red cube a planet. New game: rock toss, round 1.\n"})]
        elif holding != "nothing":
            if holding == "rock_1" or r.random() < 0.5:
                calls = [("throw", {"id": holding, "direction": [r.uniform(-1, 1), r.uniform(-1, 1), 0.8], "force": r.choice([6, 12, 16])})]
            else:
                calls = [("place", {"id": holding, "x": ax + 1, "y": ay, "z": 3})]
        else:
            if self.target not in objs:
                self.target = "rock_1" if r.random() < 0.6 else r.choice(sorted(objs) or ["rock_1"])
            tx, ty = objs.get(self.target, (ax, ay))
            dx, dy = tx - ax, ty - ay
            if math.hypot(dx, dy) <= 2.0:
                calls = [("pick_up", {"id": self.target})]
                self.target = None
            else:
                calls = [("move", {"dx": dx, "dy": dy})] if r.random() < 0.85 else [("jump", {"dx": 1, "dy": 0})]
        return self._resp([("text", "Let me see.")] + calls, stop="tool_use", messages=messages)

    def _resp(self, items, stop, messages):
        content = []
        for name, inp in items:
            if name == "text":
                content.append({"type": "text", "text": inp})
            else:
                content.append({"type": "tool_use", "id": f"toolu_mock_{self.n}_{len(content)}", "name": name, "input": inp})
        prompt_chars = len(json.dumps(messages, default=str))
        usage = {
            "input_tokens": 50,
            "output_tokens": 60,
            "cache_read_input_tokens": max(0, prompt_chars // 4 - 400),
            "cache_creation_input_tokens": 350,
        }
        return SimpleNamespace(content=content, stop_reason=stop, usage=usage, model=self.model, stop_details=None)


def make_client(cfg: dict, mock: bool, seed: int = 0):
    a = cfg["agent"]
    if mock:
        return MockClient(seed=seed)
    return AnthropicClient(a["model"], a["effort"], int(a["max_tokens"]), bool(a["refusal_fallback"]), a.get("thinking_display", "summarized"))
