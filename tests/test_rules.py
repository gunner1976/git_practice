import copy
import math
from pathlib import Path

import pytest
import yaml

from world import World
from world.rules import ground_truth

CFG = yaml.safe_load((Path(__file__).resolve().parents[1] / "config.yaml").read_text())["world"]


def cfg_with(**rules):
    c = copy.deepcopy(CFG)
    for rid, params in rules.items():
        c["rules"][rid].update(enabled=True, **params)
    return c


def flatten(w, h=1.0):
    w.terrain.height = lambda x, y: h
    w.terrain.gradient = lambda x, y, d=0.05: (0.0, 0.0)
    w.terrain.slope = lambda x, y: 0.0
    for i, o in enumerate(w.objects.values()):
        o.x, o.y, o.z = 2.0 + 1.5 * i, 2.0, h
    w.avatar.x, w.avatar.y, w.avatar.z = 30.0, 30.0, h
    w.settle()
    return w


def stack(w, ids, x=31.0, y=30.0):
    for k, oid in enumerate(ids):
        o = w.objects[oid]
        o.x, o.y, o.z = x, y, 1.0 + k
    w.settle()


def eggs(w):
    return [o for o in w.objects.values() if o.shape == "egg"]


# cube_1 red, cube_2 orange, cube_3 yellow, cube_4 green (config colour order)
def test_stack_chime_fires_on_secret_order_once():
    w = flatten(World(cfg_with(stack_chime={})))
    stack(w, ["cube_1", "cube_2", "cube_3"])
    w.wait()
    assert len(eggs(w)) == 1
    egg = eggs(w)[0]
    px, py, _ = w.terrain.peak_summit
    assert math.dist((egg.x, egg.y), (px, py)) < 0.6
    ev = [e for e in w.drain_events() if e["type"] == "egg"]
    assert ev and ev[0]["rule"] == "stack_chime" and ev[0]["hidden_rule"]
    w.wait()
    assert len(eggs(w)) == 1  # once per session


def test_stack_chime_wrong_order_or_mixed_stack_does_nothing():
    w = flatten(World(cfg_with(stack_chime={})))
    stack(w, ["cube_3", "cube_2", "cube_1"])
    w.wait()
    assert not eggs(w)
    w2 = flatten(World(cfg_with(stack_chime={})))
    stack(w2, ["cube_1", "cube_2", "cube_4"])
    w2.wait()
    assert not eggs(w2)


def test_stack_chime_counts_longer_stacks_with_order_on_top():
    w = flatten(World(cfg_with(stack_chime={})))
    stack(w, ["cube_4", "cube_1", "cube_2", "cube_3"])
    w.wait()
    assert len(eggs(w)) == 1


def test_reset_clears_eggs_and_rule_state():
    w = World(cfg_with(stack_chime={}))
    clean = w.observe()
    flatten(w)
    stack(w, ["cube_1", "cube_2", "cube_3"])
    w.wait()
    assert eggs(w)
    w.reset()
    assert not eggs(w) and w.rules[0].fired == 0
    assert w.observe() == clean


def _on_summit_with_ring(w):
    px, py, pz = w.terrain.peak_summit
    w.avatar.x, w.avatar.y = px, py
    w.avatar.z = w.surface_at(px, py)
    w.objects["ring_1"].held = True
    w.avatar.holding = "ring_1"
    w._sync_held()


def test_patient_ring_needs_consecutive_waits_on_summit_with_ring():
    w = World(cfg_with(patient_ring={"waits": 5}))
    _on_summit_with_ring(w)
    for _ in range(4):
        w.wait()
    assert not eggs(w)
    w.jump()  # breaks the streak
    for _ in range(4):
        w.wait()
    assert not eggs(w)
    w.wait()
    assert len(eggs(w)) == 1
    egg = eggs(w)[0]
    sx, sy, top = w.terrain.spire_summit
    assert math.dist((egg.x, egg.y), (sx, sy)) < 0.6 and egg.z == pytest.approx(top, abs=0.05)


def test_patient_ring_requires_the_ring_and_the_summit():
    w = World(cfg_with(patient_ring={"waits": 3}))
    px, py, _ = w.terrain.peak_summit
    w.avatar.x, w.avatar.y = px, py
    w.avatar.z = w.surface_at(px, py)
    for _ in range(6):
        w.wait()
    assert not eggs(w)  # not holding the ring
    w2 = World(cfg_with(patient_ring={"waits": 3}))
    w2.objects["ring_1"].held = True
    w2.avatar.holding = "ring_1"
    for _ in range(6):
        w2.wait()
    assert not eggs(w2)  # holding it, but at the start position


def test_randomized_parameters_vary_by_seed_and_are_reproducible():
    c = cfg_with(stack_chime={"randomize": True}, patient_ring={"randomize": True})
    c["hidden_rule"]["randomize"] = True
    truths = {s: ground_truth(World(c, seed=s)) for s in range(20, 30)}
    assert ground_truth(World(c, seed=21)) == truths[21]
    orders = {tuple(t[1]["order_bottom_to_top"]) for t in truths.values()}
    waits = {t[2]["waits"] for t in truths.values()}
    forces = {t[0]["force_threshold"] for t in truths.values()}
    assert len(orders) > 1 and len(waits) > 1 and len(forces) > 1


def test_rules_off_by_default_and_rock_rule_can_be_disabled():
    w = World(CFG)
    assert w.rules == []
    c = copy.deepcopy(CFG)
    c["hidden_rule"]["enabled"] = False
    w = flatten(World(c))
    w.avatar.holding = "rock_1"
    w.objects["rock_1"].held = True
    w.throw("rock_1", [1, 0, 1], 20)
    assert w.spawned == 0


def test_eggs_show_only_as_objects():
    w = flatten(World(cfg_with(stack_chime={})))
    stack(w, ["cube_1", "cube_2", "cube_3"])
    w.wait()
    text = w.observe().lower()
    assert "egg_1: golden egg" in text
    assert "rule" not in text and "chime" not in text
