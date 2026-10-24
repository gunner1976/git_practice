import math
from pathlib import Path

import pytest
import yaml

from world import ActionError, World, score

CFG = yaml.safe_load((Path(__file__).resolve().parents[1] / "config.yaml").read_text())["world"]


def world(**over):
    cfg = {**CFG, **over}
    return World(cfg)


def flat_world(h=1.0):
    w = world()
    w.terrain.height = lambda x, y: h
    w.terrain.gradient = lambda x, y, d=0.05: (0.0, 0.0)
    w.terrain.slope = lambda x, y: 0.0
    for i, o in enumerate(w.objects.values()):  # park everything in a row along one edge
        o.x, o.y, o.z = 2.0 + 1.5 * i, 2.0, h
    w.avatar.x, w.avatar.y, w.avatar.z = 30.0, 30.0, h
    w.settle()
    return w


def put(w, oid, x, y, z):
    o = w.objects[oid]
    o.x, o.y, o.z = x, y, z
    return o


def test_deterministic_and_seeded():
    assert world().observe() == world().observe()
    assert world(seed=8).observe() != world().observe()


def test_gravity_drops_objects_to_ground():
    w = flat_world()
    o = put(w, "cube_1", 30, 30, 7.0)
    w.settle()
    assert o.z == pytest.approx(1.0)


def test_stacking():
    w = flat_world()
    put(w, "cube_1", 30, 30, 1.0)
    b = put(w, "cube_2", 30.2, 30, 4.0)
    w.settle()
    assert b.z == pytest.approx(2.0)


def test_overhanging_cube_topples_off():
    w = flat_world()
    put(w, "cube_1", 30, 30, 1.0)
    b = put(w, "cube_2", 30.7, 30, 2.0)  # centre of mass outside the support
    w.settle()
    assert b.z == pytest.approx(1.0)
    assert b.x > 30.7
    assert any(e["type"] == "toppled" for e in w.events)


def test_stack_centre_of_mass_topples_staircase():
    # each cube alone is supported (0.4 offset < 0.5) but the top two together overhang cube_1
    w = flat_world()
    put(w, "cube_1", 30, 30, 1.0)
    put(w, "cube_2", 30.4, 30, 2.0)
    put(w, "cube_3", 30.8, 30, 3.0)
    w.settle()
    assert max(o.top for o in w.objects.values()) < 4.0 - 1e-6


def test_objects_tumble_off_steep_slopes():
    w = world()
    sx, sy, top = w.terrain.spire_summit
    o = put(w, "cube_1", sx + w.terrain.spire_radius, sy, top)  # right on the cliff edge
    w.settle()
    assert o.z < top - 1.0
    assert w.terrain.slope(o.x, o.y) <= CFG["physics"]["slide_slope"] + 1e-9


def test_object_rests_on_gentle_ground():
    w = world()
    o = w.objects["cube_3"]
    before = (o.x, o.y, o.z)
    w.settle()
    assert (o.x, o.y, o.z) == before


def test_ballistic_arc_matches_analytic_range():
    w = flat_world(h=1.0)
    w.avatar.holding = "cube_1"
    w.objects["cube_1"].held = True
    force, ang = 10.0, math.radians(45)
    w.throw("cube_1", [math.cos(ang), 0, math.sin(ang)], force)
    v = force / math.sqrt(1.0)
    g, h0 = CFG["physics"]["gravity"], 1.2
    t = (v * math.sin(ang) + math.sqrt((v * math.sin(ang)) ** 2 + 2 * g * h0)) / g
    expected = v * math.cos(ang) * t
    assert w.objects["cube_1"].x - 30.0 == pytest.approx(expected, abs=0.15)


def test_thrown_object_collides_with_stack_side():
    w = flat_world()
    for i, z in enumerate((1.0, 2.0, 3.0)):
        put(w, f"cube_{i + 2}", 33.0, 30.0, z)
    w.settle()
    w.avatar.holding = "cube_1"
    w.objects["cube_1"].held = True
    w.throw("cube_1", [1, 0, 0.05], 12)
    c = w.objects["cube_1"]
    assert c.x < 33.0 - 0.99  # stopped beside the tower, didn't pass through it


def test_heavier_objects_fly_shorter():
    d = {}
    for oid in ("cube_1", "rock_1"):
        w = flat_world()
        w.avatar.holding = oid
        w.objects[oid].held = True
        w.throw(oid, [1, 0, 1], 8.0)
        d[oid] = w.objects[oid].x - 30
    assert d["rock_1"] < d["cube_1"]


# ---------------------------------------------------------------- hidden rule
def _throw_rock(w, force):
    w.avatar.holding = "rock_1"
    w.objects["rock_1"].held = True
    w.throw("rock_1", [1, 0.2, 0.6], force)


def test_hard_rock_throw_spawns_cube_at_impact():
    w = flat_world()
    _throw_rock(w, CFG["hidden_rule"]["rock_spawn_force"] + 0.5)
    cubes = [o for o in w.objects.values() if o.shape == "cube"]
    assert len(cubes) == 13
    new = w.objects["cube_13"]
    rock = w.objects["rock_1"]
    assert math.dist((new.x, new.y), (rock.x, rock.y)) < 1.5
    assert new.z == pytest.approx(1.0)
    spawn = [e for e in w.events if e["type"] == "spawn"]
    assert spawn and spawn[0]["hidden_rule"] is True


def test_soft_rock_throw_does_not_spawn():
    w = flat_world()
    _throw_rock(w, CFG["hidden_rule"]["rock_spawn_force"] - 0.5)
    assert sum(o.shape == "cube" for o in w.objects.values()) == 12


def test_threshold_is_inclusive_and_only_for_rock():
    w = flat_world()
    _throw_rock(w, CFG["hidden_rule"]["rock_spawn_force"])
    assert w.spawned == 1
    w2 = flat_world()
    w2.avatar.holding = "cube_1"
    w2.objects["cube_1"].held = True
    w2.throw("cube_1", [1, 0, 1], 20)
    assert w2.spawned == 0


def test_repeated_throws_spawn_more_and_reset_restores():
    w = world()
    rock = w.objects["rock_1"]
    for _ in range(3):
        w.avatar.x, w.avatar.y = rock.x, rock.y - 1
        w.avatar.z = w.surface_at(w.avatar.x, w.avatar.y)
        w.pick_up("rock_1")
        w.throw("rock_1", [0, 1, 0.5], 15)
    assert score("make_cubes", w)["score"] == 3
    assert w.observe() != world().observe()
    w.reset()
    assert w.observe() == world().observe()
    assert w.time == 0


def test_spawn_cap():
    w = flat_world()
    w.rule = {**w.rule, "max_spawned": 2}
    for _ in range(4):
        _throw_rock(w, 15)
        w.objects["rock_1"].held = False
    assert w.spawned == 2


def test_observation_never_mentions_the_rule():
    w = flat_world()
    _throw_rock(w, 15)
    text = w.observe() + w.landmarks_text()
    assert "spawn" not in text.lower() and "rule" not in text.lower()


# ------------------------------------------------------------------- avatar
def test_cannot_walk_up_spire_but_can_walk_up_peak():
    w = world()
    sx, sy, top = w.terrain.spire_summit
    w.avatar.x, w.avatar.y = sx + 4, sy
    w.avatar.z = w.surface_at(w.avatar.x, w.avatar.y)
    for _ in range(4):
        w.move(-1.5, 0)
    assert w.avatar.z < top - 2
    px, py, pz = w.terrain.peak_summit
    w.avatar.x, w.avatar.y = px, py - 14
    w.avatar.z = w.surface_at(w.avatar.x, w.avatar.y)
    for _ in range(4):
        w.move(0, 3)
    w.move(0, 2)
    assert w.avatar.z == pytest.approx(pz, abs=0.3)


def test_single_jump_cannot_reach_spire_but_staircase_can():
    w = world()
    sx, sy, top = w.terrain.spire_summit
    w.avatar.x, w.avatar.y = sx + 3.0, sy
    w.avatar.z = w.surface_at(w.avatar.x, w.avatar.y)
    w.jump(-1.5, 0)
    assert w.avatar.z < top - 1
    # staircase: 3-stack at +3.6, 2-stack at +4.6, 1 cube at +5.6
    ids = iter(f"cube_{i}" for i in range(1, 7))
    for dx, n in ((3.6, 3), (4.6, 2), (5.6, 1)):
        for k in range(n):
            put(w, next(ids), sx + dx, sy, 20 + k)
    w.settle()
    w.avatar.x, w.avatar.y = sx + 6.8, sy
    w.avatar.z = w.surface_at(w.avatar.x, w.avatar.y)
    for _ in range(3):
        w.jump(-1.0, 0)
    w.jump(-1.5, 0)
    assert w.avatar.z == pytest.approx(top, abs=1e-6)


def test_pick_up_rules():
    w = flat_world()
    put(w, "cube_1", 31, 30, 1)
    put(w, "cube_2", 31, 30, 2)
    w.settle()
    with pytest.raises(ActionError):
        w.pick_up("cube_1")  # cube_2 is on it
    w.pick_up("cube_2")
    with pytest.raises(ActionError):
        w.pick_up("cube_1")  # hands full
    with pytest.raises(ActionError):
        w.pick_up("nope")
    w.place("cube_2", 32, 30, 1)
    with pytest.raises(ActionError):
        w.pick_up("ring_1")  # far away


def test_place_can_build_a_tower_and_score_it():
    w = flat_world()
    for i in range(1, 5):
        put(w, f"cube_{i}", 30 + i, 33, 1)
    w.settle()
    for i in range(1, 5):
        oid = f"cube_{i}"
        w.avatar.x, w.avatar.y, w.avatar.z = 30 + i, 32, 1.0
        w.pick_up(oid)
        w.avatar.x, w.avatar.y = 30, 30
        if i == 4:  # z = 4 is beyond reach_up from the ground
            with pytest.raises(ActionError):
                w.place(oid, 31, 30, 4.0)
        else:
            w.place(oid, 31, 30, float(i))
    s = score("tallest_tower", w)
    assert s["n_objects"] == 3
    assert s["score"] == pytest.approx(3.0)


def test_spire_and_peak_scoring():
    w = world()
    sx, sy, top = w.terrain.spire_summit
    put(w, "cube_1", sx, sy, top + 2)
    put(w, "rock_1", sx + 1, sy, top + 2)
    px, py, pz = w.terrain.peak_summit
    put(w, "ring_1", px + 0.5, py, pz + 1)
    w.settle()
    assert score("spire_objects", w)["score"] == 2
    assert score("ring_on_peak", w)["score"] == 1


def test_move_blocked_by_object_vs_terrain():
    w = flat_world()
    rock = put(w, "rock_1", 32.0, 30.0, 1.0)
    w.settle()
    assert rock.sz > float(w.av_cfg["step_up"])
    r = w.move(3, 0)
    assert r.endswith("An object blocks your way.")
    assert w.avatar.x < 32.0

    w = flat_world()
    w.terrain.height = lambda x, y: 3.0 if x > 31.0 else 1.0
    r = w.move(3, 0)
    assert r.endswith("Something too steep blocks your way.")
    assert w.avatar.x < 31.0


def test_irregular_island_outline():
    from analysis.challenges import shoreline_perimeter

    base = dict(CFG)
    shaped = {**CFG, "island_shape": {"lobes": [[3, 0.12, 20]], "bays": [{"angle": 0, "depth": 0.5, "width": 11}], "seabed_steepness": 4.0}}
    w0, w1 = World(base), World(shaped)
    t = w1.terrain
    assert t.radius_at(0.0) < 0.75 * t.radius_at(math.pi)         # the bay cuts into the east side
    assert w0.terrain.radius_at(1.0) == w0.terrain.island_r          # no shape: the usual round island
    assert t.height(t.cx + t.radius_at(math.pi) + 1, t.cy) < -0.8    # steep seabed: no wading beyond the shore
    assert shoreline_perimeter(shaped) > shoreline_perimeter(base)
