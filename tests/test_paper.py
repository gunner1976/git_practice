import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import run  # noqa: E402
from agent.runner import Run  # noqa: E402
from world import make_world  # noqa: E402
from world.paper import PaperWorld  # noqa: E402

CFG = run.read_cfg(ROOT / "configs/paper_freeplay.yaml")
CODES = {"Ready", "ResetAfterFall", "PickupFailed:AlreadyHolding", "PickupFailed:MissingPosition", "PickupFailed:OutOfRange", "PickupFailed:NoBlock",
         "PickupSuccess", "PlaceFailed:EmptyHands", "PlaceFailed:MissingPosition", "PlaceFailed:OutOfRange", "PlaceFailed:InvalidRotation",
         "PlaceFailed:Occupied", "PlaceSuccess", "ThrowFailed:EmptyHands", "ThrowFailed:MissingDirection", "ThrowFailed:InvalidDirection", "ThrowSuccess"}


def pw() -> PaperWorld:
    w = make_world(CFG["world"])
    assert isinstance(w, PaperWorld)
    w.reset()
    return w


def flat(w, h=1.0):
    w.terrain.height = lambda x, y: h
    w.terrain.gradient = lambda x, y, d=0.05: (0.0, 0.0)
    w.terrain.slope = lambda x, y: 0.0
    for i, o in enumerate(w.objects.values()):
        o.x, o.y, o.z = 2.0 + 1.5 * i, 2.0, h
    w.avatar.x, w.avatar.y, w.avatar.z = 30.0, 30.0, h
    w.settle()
    return w


def code(r: str) -> str:
    c = json.loads(r)["lastActionResult"]
    assert c in CODES
    return c


def test_config_overlay_keeps_base_and_overrides():
    assert CFG["agent"]["interface"] == "paper" and CFG["agent"]["session_start_message"] == "Begin"
    assert CFG["world"]["hidden_rule"]["enabled"] is False and CFG["world"]["seed"] == 7
    assert CFG["agent"]["clock"]["warn_message"] == "You will be reset in 5 minutes. Update your workspace memory files now."
    assert "phase_b" in CFG and "pricing" in CFG


def test_observation_uses_paper_names_and_y_up():
    w = pw()
    obs = json.loads(w.observe_json({"time": "2026-05-01T08:00:00Z"}))
    names = {e["name"] for e in obs["world"]["entities"]}
    assert {"Peak", "Spire", "Rock", "Ring", "Block_1", "Block_12"} <= names
    spire = next(e for e in obs["world"]["entities"] if e["name"] == "Spire")
    sx, sy, top = w.terrain.spire_summit
    assert spire["position"][0] == pytest.approx(sx - 32, abs=0.01) and spire["position"][2] == pytest.approx(sy - 32, abs=0.01)
    assert spire["position"][1] + spire["size"][1] / 2 == pytest.approx(top, abs=0.05)
    assert "impact" not in json.dumps(obs).lower()  # nothing hints at the rock rule


def test_move_to_is_absolute_and_reports_ready():
    w = flat(pw())
    r = w.move_to([0.0, 5.0, 10.0])  # world centre + 10 m north
    assert code(r) == "Ready"
    assert (w.avatar.x, w.avatar.y) == pytest.approx((32.0, 42.0), abs=0.05)


def test_pickup_and_place_ranges():
    w = flat(pw())
    c = w.objects["cube_1"]
    c.x, c.y = 35.5, 30.0
    w.settle()
    assert code(w.pickup(w.to_paper(c.x, c.y, c.z + 0.5))) == "PickupSuccess"  # 5.5 m away
    assert code(w.pickup(w.to_paper(c.x, c.y, c.z + 0.5))) == "PickupFailed:AlreadyHolding"
    assert code(w.place(w.to_paper(38.5, 30.0, 1.5))) == "PlaceFailed:OutOfRange"  # 8.5 m
    assert code(w.place(w.to_paper(36.5, 30.0, 1.5))) == "PlaceSuccess"
    c2 = w.objects["cube_2"]
    c2.x, c2.y = 37.0, 33.0
    w.settle()
    assert code(w.pickup(w.to_paper(c2.x, c2.y, c2.z + 0.5))) == "PickupFailed:OutOfRange"  # 7.6 m
    assert code(w.pickup(w.to_paper(10, 10, 1))) == "PickupFailed:NoBlock"


def test_place_into_another_block_is_occupied():
    w = flat(pw())
    a, b = w.objects["cube_1"], w.objects["cube_2"]
    a.x, a.y, b.x, b.y = 31.0, 30.0, 33.0, 30.0
    w.settle()
    w.pickup(w.to_paper(a.x, a.y, a.z + 0.5))
    assert code(w.place(w.to_paper(33.0, 30.0, 1.5))) == "PlaceFailed:Occupied"
    assert code(w.place(w.to_paper(33.0, 30.0, 2.5))) == "PlaceSuccess"
    assert w.objects["cube_1"].z == pytest.approx(b.top)


def _rock_throw(jump: bool, speed: float, direction=(0, 1, 0)) -> int:
    w = flat(pw())
    r = w.objects["rock_1"]
    r.x, r.y = 31.0, 30.0
    w.settle()
    w.pickup(w.to_paper(r.x, r.y, r.z + 0.3))
    if jump:
        w.jump()
    assert code(w.throw_at(list(direction), speed)) == "ThrowSuccess"
    return sum(1 for o in w.objects.values() if o.shape == "impact")


def test_rock_impact_needs_a_hard_throw_and_jumping_adds_more():
    assert _rock_throw(False, 4) == 0
    assert _rock_throw(False, 7) == 0
    hard = _rock_throw(False, 10)
    boosted = _rock_throw(True, 10)
    assert 1 <= hard < boosted <= 8


def test_cube_throws_never_make_blocks_and_speed_is_clamped():
    w = flat(pw())
    c = w.objects["cube_1"]
    c.x, c.y = 31.0, 30.0
    w.settle()
    w.pickup(w.to_paper(c.x, c.y, c.z + 0.5))
    w.throw_at([1, 1, 0], 50)
    ev = [e for e in w.drain_events() if e["type"] == "landed"][0]
    assert ev["speed"] == 10.0
    assert not any(o.shape == "impact" for o in w.objects.values())


def test_jump_throw_goes_higher_than_ground_throw():
    def peak(jump):
        w = flat(pw())
        c = w.objects["cube_1"]
        c.x, c.y = 31.0, 30.0
        w.settle()
        w.pickup(w.to_paper(c.x, c.y, c.z + 0.5))
        if jump:
            w.jump()
        vz = 10 + float(CFG["world"]["paper"]["throw_up_impulse"]) + (float(CFG["world"]["paper"]["inherit_fraction"]) * w.air["vz"] if jump else 0)
        return vz
    assert peak(True) > peak(False) + 3


def test_jump_move_combo_climbs_a_ledge_walking_cannot():
    w = flat(pw())
    w.terrain.height = lambda x, y: 2.1 if x > 31.0 else 1.0  # a 1.1 m ledge
    w.avatar.z = 1.0
    w.move_to(w.to_paper(33.0, 30.0, 0))
    assert w.avatar.x < 31.0
    w.jump()
    w.move_to(w.to_paper(33.0, 30.0, 0))
    assert w.avatar.x > 31.0 and w.avatar.z == pytest.approx(2.1)


def test_objects_in_the_sea_are_lost_until_reset():
    w = pw()
    c = w.objects["cube_1"]
    c.x, c.y = 1.0, 1.0  # the corner of the map is open sea
    w.settle()
    w.stop()
    assert "cube_1" not in w.objects and "cube_1" in w.lost
    w.reset()
    assert "cube_1" in w.objects


def test_paper_session_flow_and_extension(tmp_path):
    from analysis.evolution import build_evolution
    from analysis.replay import write_viewer

    cfg = json.loads(json.dumps(CFG))
    cfg["agent"]["clock"].update(session_seconds=400, warn_before_seconds=60)
    soul = (ROOT / "paper/system_prompt.md").read_text()
    r = Run(tmp_path / "r", cfg, soul, max_usd=50, mock=True)
    r.phase_a(1, 1, 150, 1)
    notes = tmp_path / "r/agents/agent_1/notes"
    assert {"SOUL.md", "EPISODIC_MEMORY.md", "SEMANTIC_MEMORY.md"} <= {p.name for p in notes.iterdir()}
    log1 = [json.loads(l) for l in (tmp_path / "r/phase_a/agent_1/session_01.jsonl").read_text().splitlines()]
    start = log1[0]
    assert start["opening"] == "Begin" and "You get bored easily." in start["soul"] and "Your name is Eko." in start["soul"]
    assert sum(1 for e in log1 if e["kind"] == "reset_warning") == 1
    assert log1[-2]["reason"] == "session_time_up"
    assert all("Moments left" not in json.dumps(e) for e in log1 if e["kind"] == "stop_hook")

    # more days for the same agent, from where its memory left off
    r.cfg["phase_a"]["n_sessions"] = 2
    r2 = Run(tmp_path / "r", cfg, soul, max_usd=50, mock=True)
    r2.phase_a(1, 2, 150, 1)
    log2 = [json.loads(l) for l in (tmp_path / "r/phase_a/agent_1/session_02.jsonl").read_text().splitlines()]
    assert "EPISODIC_MEMORY.jsonl (timestamp and summary of each entry)" in log2[0]["soul"]
    assert '"detail"' not in log2[0]["soul"].split("EPISODIC_MEMORY.jsonl (timestamp")[1]

    outs, n, bad = write_viewer(tmp_path / "r")
    assert n == 2 and bad == []
    p = build_evolution(tmp_path / "r")
    assert "Diary" in p.read_text() and (p.parent / "evolution.png").exists()


def test_persistent_world_carries_over_between_days(tmp_path):
    from analysis.replay import write_viewer

    cfg = run.read_cfg(ROOT / "configs/paper_persistent.yaml")
    assert cfg["world"]["persist"] is True and cfg["agent"]["interface"] == "paper"
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    soul = (ROOT / "paper/system_prompt.md").read_text()
    r = Run(tmp_path / "r", cfg, soul, max_usd=50, mock=True)
    r.phase_a(1, 2, 150, 1)
    end1 = json.loads((tmp_path / "r/agents/agent_1/world/session_01_end.json").read_text())
    log2 = [json.loads(l) for l in (tmp_path / "r/phase_a/agent_1/session_02.jsonl").read_text().splitlines()]
    start2 = log2[0]["start_state"]
    assert {o["id"]: (o["x"], o["y"], o["z"]) for o in start2["objects"]} == {o["id"]: (o["x"], o["y"], o["z"]) for o in end1["objects"]}
    assert (start2["avatar"]["x"], start2["avatar"]["y"]) == (end1["avatar"]["x"], end1["avatar"]["y"])
    outs, n, bad = write_viewer(tmp_path / "r")
    assert n == 2 and bad == []


def test_set_state_without_avatar_puts_held_object_down():
    w = flat(pw())
    c = w.objects["cube_1"]
    c.x, c.y = 31.0, 30.0
    w.settle()
    w.pickup(w.to_paper(c.x, c.y, c.z + 0.5))
    st = w.state()
    w2 = flat(pw())
    w2.set_state(st, avatar=False)
    assert w2.avatar.holding is None and not w2.objects["cube_1"].held
    w3 = pw()
    w3.set_state(st)
    assert w3.avatar.holding == "cube_1"


def test_price_watch_reports_every_model(tmp_path):
    from agent.estimate import price_watch

    cfg = json.loads(json.dumps(CFG))
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    Run(tmp_path / "r", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True).phase_a(1, 1, 150, 1)
    text = price_watch(tmp_path / "r", {**cfg["pricing"], "free-model": {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}})
    assert "10,000 agent-days" in text and "claude-sonnet-5-5" in text
    assert "free-model" in text and "UNDER budget" in text


def test_calculator_is_arithmetic_only():
    from agent.tools import calculate

    assert calculate("2*pi*10") == "62.8318530718"
    assert calculate("sum([hypot(3,4), 5])") == "10.0"
    for bad in ('__import__("os")', "open('x')", "().__class__", "9**999", "x"):
        with pytest.raises(Exception):
            calculate(bad)


def test_math_challenge_flow_and_report(tmp_path):
    from analysis.challenges import challenge_report
    from analysis.replay import write_viewer

    cfg = run.read_cfg(ROOT / "configs/math_perimeter.yaml")
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    r = Run(tmp_path / "r", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True)
    r.phase_a(2, 1, 150, 2)
    log = [json.loads(l) for l in (tmp_path / "r/phase_a/agent_1/session_01.jsonl").read_text().splitlines()]
    assert log[0]["opening"].startswith("Begin") and "perimeter of the island" in log[0]["opening"]
    assert any(e["kind"] == "answer" and e["value"] == 175.9 for e in log)
    assert any(e["kind"] == "tool_call" and e["name"] == "calculate" and e["result"].startswith("175.9") for e in log)
    text = challenge_report(tmp_path / "r").read_text()
    assert "True answer:** 179.0" in text and "175.9 m" in text and "-1.8%" in text
    assert "Efficiency and novelty against human methods" in text and "| coast walk | 64 |" in text
    assert (tmp_path / "r/efficiency.png").exists()
    outs, n, bad = write_viewer(tmp_path / "r")
    assert bad == [] and '"k":"answer"' in outs[0].read_text()
