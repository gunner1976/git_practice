"""Spend tracking from token usage, with a hard USD cap and a persistent ledger."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path


class BudgetExceeded(Exception):
    pass


def usage_dict(usage) -> dict:
    get = (lambda k: usage.get(k)) if isinstance(usage, dict) else (lambda k: getattr(usage, k, None))
    return {
        "input_tokens": get("input_tokens") or 0,
        "output_tokens": get("output_tokens") or 0,
        "cache_read_input_tokens": get("cache_read_input_tokens") or 0,
        "cache_creation_input_tokens": get("cache_creation_input_tokens") or 0,
    }


def call_cost(u: dict, price: dict) -> float:
    return (
        u["input_tokens"] * price["input"]
        + u["output_tokens"] * price["output"]
        + u["cache_read_input_tokens"] * price["cache_read"]
        + u["cache_creation_input_tokens"] * price["cache_write"]
    ) / 1e6


class Budget:
    """Thread-safe spend tracker. Spend already in the ledger (from earlier,
    possibly crashed, attempts of this run) counts against the cap."""

    def __init__(self, max_usd: float, ledger: Path, pricing: dict):
        self.max_usd = float(max_usd)
        self.ledger = Path(ledger)
        self.pricing = pricing
        self._lock = threading.Lock()
        self.spent = 0.0
        self.calls = 0
        if self.ledger.exists():
            for line in self.ledger.read_text().splitlines():
                if line.strip():
                    self.spent += json.loads(line)["cost_usd"]
                    self.calls += 1
        self.stopped = False

    def price_for(self, model: str) -> dict:
        if model in self.pricing:
            return self.pricing[model]
        for k, v in self.pricing.items():  # e.g. dated or suffixed ids
            if model.startswith(k):
                return v
        # Unknown model (e.g. a refusal fallback served the turn): charge the most
        # expensive configured rate so the cap stays conservative.
        return max(self.pricing.values(), key=lambda p: p["output"])

    def check(self, next_call_estimate: float = 0.0) -> None:
        """Raise BudgetExceeded if making another call could cross the cap."""
        with self._lock:
            if self.stopped or self.spent + next_call_estimate > self.max_usd:
                self.stopped = True
                raise BudgetExceeded(f"spent ${self.spent:.4f}; next call (~${next_call_estimate:.4f}) would cross the ${self.max_usd:.2f} cap")

    def record(self, model: str, usage, meta: dict) -> tuple[dict, float]:
        u = usage_dict(usage)
        cost = call_cost(u, self.price_for(model))
        with self._lock:
            self.spent += cost
            self.calls += 1
            self.ledger.parent.mkdir(parents=True, exist_ok=True)
            with self.ledger.open("a") as f:
                f.write(json.dumps({"ts": time.time(), "model": model, "usage": u, "cost_usd": cost, **meta}) + "\n")
        return u, cost
