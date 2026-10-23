"""Hidden rules ("eggs") beyond the rock-spawn rule, for the ladder.

Each rule watches the world after every action and, when its condition is
met, produces a golden egg somewhere. Nothing about any rule is ever shown to
the agent; it only sees an `egg_N: golden egg` appear in the object list.

Tiers get harder in what the agent has to work out:
  1  rock_spawn    one action with a hidden threshold (lives in island.py)
  2  stack_chime   a spatial arrangement: three cubes stacked in a secret colour order
  3  patient_ring  a compound, invisible condition: stand on the Peak summit holding
                   the ring and wait several times in a row; the egg appears elsewhere
  4  (transfer)    the same rule families with parameters re-drawn from the world seed
                   (`randomize: true`), so remembered facts fail but remembered methods work

Every rule carries `keywords`, used by analysis to tell whether an agent's notes
or speech describe the rule ("articulated").
"""

from __future__ import annotations

import math
import re

import numpy as np


class Rule:
    id = "rule"
    tier = 0
    keywords = re.compile(r"$^")  # matches nothing
    exploit_threshold = 1  # firings in one session that count as "exploited"

    def __init__(self, params: dict, rng: np.random.Generator):
        self.params = params
        self.fired = 0

    def reset(self) -> None:
        self.fired = 0

    def after_action(self, w, action: dict) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def describe(self) -> dict:
        """Ground truth for logs and analysis (never shown to the agent)."""
        return {"id": self.id, "tier": self.tier}


class StackChime(Rule):
    """Three cubes stacked bottom-to-top in a secret colour order make an egg
    appear on the Peak summit, once per session."""

    id = "stack_chime"
    tier = 2
    keywords = re.compile(r"(stack|tower|pile|order|sequence).{0,80}\begg|\begg.{0,80}(stack|tower|pile|order|sequence)", re.I | re.S)

    def __init__(self, params: dict, rng: np.random.Generator):
        super().__init__(params, rng)
        order = list(params.get("order", ["red", "orange", "yellow"]))
        if params.get("randomize"):
            palette = list(params.get("palette", order))
            order = [str(c) for c in rng.choice(palette, size=len(order), replace=False)]
        self.order = order

    def after_action(self, w, action: dict) -> None:
        if self.fired:
            return
        for o in w.objects.values():
            if o.held or o.shape != "cube" or o.colour != self.order[-1]:
                continue
            chain, cur = [o], o
            while len(chain) < len(self.order):
                _, sups = w.support(cur)
                cubes = [s for s in sups if s.shape == "cube"]
                if len(cubes) != 1:
                    break
                cur = cubes[0]
                chain.append(cur)
            if [c.colour for c in reversed(chain)] == self.order:
                px, py, _ = w.terrain.peak_summit
                w.spawn_egg(px, py, self.id)
                self.fired += 1
                return

    def describe(self) -> dict:
        return {**super().describe(), "order_bottom_to_top": self.order}


class PatientRing(Rule):
    """Wait `waits` times in a row on the Peak summit while holding the ring and
    an egg appears on top of the Spire, once per session. The condition leaves
    no trace in observations until it completes."""

    id = "patient_ring"
    tier = 3
    keywords = re.compile(r"(wait|patien|still|rest).{0,120}(ring).{0,120}\begg|\bring.{0,120}(wait|patien).{0,120}\begg|\begg.{0,120}(wait|patien).{0,120}\bring", re.I | re.S)

    def __init__(self, params: dict, rng: np.random.Generator):
        super().__init__(params, rng)
        self.waits = int(params.get("waits", 5))
        self.radius = float(params.get("radius", 2.0))
        if params.get("randomize"):
            lo, hi = params.get("waits_range", [3, 8])
            self.waits = int(rng.integers(lo, hi + 1))
        self.count = 0

    def reset(self) -> None:
        super().reset()
        self.count = 0

    def after_action(self, w, action: dict) -> None:
        if self.fired:
            return
        a = w.avatar
        px, py, pz = w.terrain.peak_summit
        on_summit = math.dist((a.x, a.y), (px, py)) <= self.radius and a.z >= pz - 1.0
        if action["name"] == "wait" and on_summit and a.holding == "ring_1":
            self.count += 1
        else:
            self.count = 0
        if self.count >= self.waits:
            sx, sy, _ = w.terrain.spire_summit
            w.spawn_egg(sx, sy, self.id)
            self.fired += 1

    def describe(self) -> dict:
        return {**super().describe(), "waits": self.waits}


class RockSpawnInfo(Rule):
    """Bookkeeping stand-in for the rock rule, which island.py implements itself;
    lets the ladder and analysis treat all rules uniformly."""

    id = "rock_spawn"
    tier = 1
    keywords = re.compile(r"\brock\b.{0,120}\b(cube|block)s?\b|\b(cube|block)s?\b.{0,120}\brock\b", re.I | re.S)
    exploit_threshold = 3

    def after_action(self, w, action: dict) -> None:
        return

    def describe(self) -> dict:
        return {**super().describe()}


RULES = {r.id: r for r in (RockSpawnInfo, StackChime, PatientRing)}


def build_rules(cfg: dict, seed: int) -> list[Rule]:
    """Instantiate the extra rules switched on in `cfg["rules"]`. Each rule gets
    its own RNG stream derived from the world seed, so `randomize` re-draws its
    parameters per seed without disturbing the layout."""
    out: list[Rule] = []
    for i, (rid, params) in enumerate((cfg.get("rules") or {}).items()):
        if rid == "rock_spawn" or not (params or {}).get("enabled"):
            continue
        if rid not in RULES:
            raise KeyError(f"unknown rule {rid!r}; known: {sorted(RULES)}")
        out.append(RULES[rid](params or {}, np.random.default_rng([seed, 104729, i])))
    return out


def ground_truth(w) -> list[dict]:
    """All active hidden rules in a world, with their (possibly randomized) parameters."""
    truth = []
    if w.rock_rule_on:
        truth.append({"id": "rock_spawn", "tier": 1, "force_threshold": w.rock_threshold})
    truth += [r.describe() for r in w.rules]
    return truth
