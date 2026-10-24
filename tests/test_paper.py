import json
import math
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
         "PlaceFailed:Occupied", "PlaceSuccess", "ThrowFailed:EmptyHands", "ThrowFailed:MissingDirection", "ThrowFailed:InvalidDirection", "ThrowSuccess",
         # the mission phone's (not in the paper)
         "PressFailed:NothingInReach", "PressFailed:NoSuchButton", "PressSuccess:Ringing", "PressSuccess:NoAnswer", "PressSuccess:Connected",
         "PressSuccess:AlreadyConnected", "PressSuccess:CallEnded", "PressSuccess:NoCall", "SpeakSuccess:IntoPhone", "SpeakSuccess:NobodyHears"}


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


def test_water_world_has_no_edge():
    cfg = run.read_cfg(ROOT / "configs/waterworld.yaml")["world"]
    w = make_world(cfg)
    w.reset()
    t = w.terrain
    assert t.height(-200, 500) == pytest.approx(-60.0) and t.height(32, 32) > 0  # deep ocean far away, land in the middle
    c = w.objects["cube_1"]
    w.avatar.x, w.avatar.y, w.avatar.z = c.x + 1, c.y, w.surface_at(c.x + 1, c.y)
    assert code(w.pickup(w.to_paper(c.x, c.y, c.z + 0.5))) == "PickupSuccess"
    w.avatar.x, w.avatar.y = 40.0, 6.5  # on the south shore
    w.avatar.z = w.surface_at(40.0, 6.5)
    w.throw_at([0, 0.3, -1], 10)  # out to sea, south
    ev = [e for e in w.drain_events() if e["type"] == "landed"][0]
    assert ev["at"][1] < 0  # flew past where the old map edge was
    assert "cube_1" not in w.objects and "cube_1" in w.lost  # and sank
    w.move_to(w.to_paper(40.0, -100.0, 0))  # try to walk out to sea
    assert w.avatar.y > 0 and w.terrain.height(w.avatar.x, w.avatar.y) > -1.0


def test_round_world_sky_and_promotion_flow(tmp_path):
    from analysis.promotion import promote
    from world.sky import Planet

    cfg = run.read_cfg(ROOT / "configs/round_world.yaml")
    w = make_world(cfg["world"])
    w.reset()
    p = w.planet
    _, south = p.sun(32, 8, 0.5)
    _, north = p.sun(32, 56, 0.5)
    assert south - north == pytest.approx(48 / 2000 * 180 / math.pi, abs=0.05)  # Eratosthenes across the island
    assert p.horizon_dip(5.7) > p.horizon_dip(0.5) > 0  # the horizon sinks as you climb
    assert "sky" in json.loads(w.observe_json())
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    r = Run(tmp_path / "r", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True)
    r.phase_a(1, 1, 150, 1)
    notes = tmp_path / "r/phase_a/agent_1/session_01.jsonl"
    with notes.open("a") as f:  # a hand-made deduction, to exercise the detector without an API call
        f.write(json.dumps({"kind": "tool_call", "step": 7, "name": "append_note", "input": {"path": "SEMANTIC_MEMORY.md",
                "content": "- *verified* The horizon dips 2.6 deg from the beach but 4.9 deg from the Spire: the ground is curved, a sphere."}, "result": "ok", "error": False}) + "\n")
    out = promote(tmp_path / "r", cfg, judge_model=None)
    res = json.loads((tmp_path / "r/promotions.json").read_text())["agents"]["agent_1"]
    assert res["promoted"] and res["verdict"]["step"] == 7 and "unverified" in res["judge"]
    assert "**yes**" in out.read_text()


def test_planet_eko_physics_and_sky():
    cfg = run.read_cfg(ROOT / "configs/eko.yaml")
    w = make_world(cfg["world"])
    w.reset()
    e = w.eko
    assert e.g == pytest.approx(8.60, abs=0.01) and w.phys["gravity"] == e.g          # gravity from mass and radius
    assert w.av_cfg["jump_height"] == pytest.approx(1.3 * 9.8 / e.g)                   # same legs, lower gravity
    assert e.month / e.day == pytest.approx(10.12, abs=0.01)                           # Kepler's third law
    D = e.day
    noon = e.sky(32, 32, 1.0, D / 2)["sun"]
    assert noon["elevation_deg"] == pytest.approx(90 - 23, abs=0.5) and noon["azimuth_deg"] == pytest.approx(180, abs=1)
    night = e.sky(32, 32, 1.0, 3 * D)                                                 # session 3, total eclipse
    assert night["daylight"] == "night" and night["moon"]["eclipse"]["darkened_fraction"] > 0.99
    assert len(night["brightest_stars"]) > 0
    partial = e.sky(32, 32, 1.0, 3 * D - 0.05 * D)["moon"]["eclipse"]
    assert 0 < partial["darkened_fraction"] < 1 and partial["shadow_edge"] == "a curved arc"
    # the stars turn about a pole that stands at the island's latitude
    import numpy as np
    pole = np.array([0.0, 0.0, 1.0])
    _, up, east, north = e._observer(32, 32, 3 * D)
    az, el = e._altaz(pole, up, east, north)
    assert el == pytest.approx(23, abs=0.01) and (az < 1 or az > 359)
    # the session clock maps onto EKO days, and observations carry the sky
    assert e.session_tau(3, 0.0, 1200) == pytest.approx(2.25 * D)
    w.sky_tau = 3 * D
    assert json.loads(w.observe_json())["sky"]["moon"]["eclipse"]["darkened_fraction"] > 0.99


def test_trait_ranking_puts_persistence_first(tmp_path):
    from analysis.traits import WEIGHTS, trait_report

    assert WEIGHTS["persistence"] > WEIGHTS["curiosity"] and WEIGHTS["persistence"] > WEIGHTS["innovation"]
    cfg = run.read_cfg(ROOT / "configs/eko.yaml")
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    Run(tmp_path / "r", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True).phase_a(3, 2, 150, 3)
    text = trait_report(tmp_path / "r").read_text()
    assert "| 1 | agent_" in text and "| 3 | agent_" in text
    ranked = json.loads((tmp_path / "r/traits.json").read_text())
    assert ranked[0]["total"] >= ranked[-1]["total"] and all(0 <= r["persistence"] <= 1 for r in ranked)


def test_mission_tablet_appears_after_the_trials_and_reads_only_up_close(tmp_path):
    from analysis.replay import write_viewer

    cfg = run.read_cfg(ROOT / "configs/eko_mission.yaml")
    w = make_world(cfg["world"])
    w.reset()
    assert "tablet_1" not in w.objects
    w.achievements = {"tower": True, "rock_fragments": True}
    w.reset()
    assert "tablet_1" not in w.objects                                           # one trial still missing
    w.sky_tau = 3 * w.eko.day                                                     # session 3's eclipse night
    json.loads(w.observe_json())
    assert w.achievements.get("saw_lunar_eclipse") and "tablet_1" in w.objects    # the tablet appears
    tab = w.objects["tablet_1"]
    sx, sy, top = w.terrain.spire_summit
    assert math.hypot(tab.x - sx, tab.y - sy) < 0.01 and tab.z == pytest.approx(top, abs=0.1)
    far = next(e for e in json.loads(w.observe_json())["world"]["entities"] if e["name"] == "Tablet")
    assert "inscription" not in far["attributes"]
    w.avatar.x, w.avatar.y, w.avatar.z = tab.x + 1.5, tab.y, top                  # on the Spire top, next to it
    near = next(e for e in json.loads(w.observe_json())["world"]["entities"] if e["name"] == "Tablet")
    assert near["attributes"]["inscription"] == "Your mission is to reach the moon." and w.achievements.get("read_mission")
    assert code(w.pickup(w.to_paper(tab.x, tab.y, tab.z + 0.4))) == "PickupFailed:NoBlock"  # can't carry it off
    # a run: trials persist between days, and replays stay exact
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    r = Run(tmp_path / "r", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True)
    r.phase_a(2, 2, 150, 2)
    assert (tmp_path / "r/agents/agent_1/achievements.json").exists()
    outs, n, bad = write_viewer(tmp_path / "r")
    assert n == 4 and bad == []


def test_phone_live_call_between_two_agents_who_earned_it(tmp_path):
    from analysis.replay import write_viewer
    from world.phone import Switchboard

    cfg = run.read_cfg(ROOT / "configs/eko_phone.yaml")
    t = [0.0]
    board = Switchboard(["agent_1", "agent_2"], ring_seconds=60, now=lambda: t[0])
    w1, w2 = make_world(cfg["world"]), make_world(cfg["world"])
    for a, w in (("agent_1", w1), ("agent_2", w2)):
        board.attach(a, w)
        board.start(a)
        w.achievements = {"tower": True, "rock_fragments": True}
        w.reset()
    assert not w1.has_phone() and code(w1.press("call")) == "PressFailed:NothingInReach"
    # agent_1 completes the trials: the phone appears on the Spire and a voice announces it
    w1.achievements["saw_lunar_eclipse"] = True
    w1.reset()
    assert w1.has_phone() and w1.notices() == ["Something is waiting for you at the top of the Spire."]
    ph = w1.objects["phone_1"]
    w1.avatar.x, w1.avatar.y, w1.avatar.z = ph.x + 1.0, ph.y, ph.z
    phone = next(e for e in json.loads(w1.observe_json())["world"]["entities"] if e["name"] == "Phone")
    assert phone["attributes"]["buttons"] == ["call", "end call"] and w1.achievements.get("found_phone")
    assert code(w1.press("call")) == "PressSuccess:NoAnswer"           # the partner hasn't earned a phone
    assert code(w1.speak("hello?")) == "SpeakSuccess:NobodyHears"
    # agent_2 earns its phone too, but is far from it: the ringing is out of earshot
    w2.achievements["saw_lunar_eclipse"] = True
    w2.reset()
    w2.notices()
    assert code(w1.press("call")) == "PressSuccess:Ringing"
    assert w2.notices() == []
    q = w2.objects["phone_1"]
    w2.avatar.x, w2.avatar.y, w2.avatar.z = q.x + 1.0, q.y, q.z           # climbs up: hears it ring, once
    assert w2.notices() == ["You hear a phone ringing nearby."] and w2.notices() == []
    assert code(w2.press("call")) == "PressSuccess:Connected"
    assert w1.notices() == ["The ringing stops. The line is open."]
    assert code(w1.speak("Is someone there?")) == "SpeakSuccess:IntoPhone"
    assert w2.notices() == ['A voice comes from the phone: "Is someone there?"']
    assert code(w2.press("end call")) == "PressSuccess:CallEnded" and w1.notices() == ["The line goes quiet."]
    # an unanswered call stops ringing after ring_seconds
    w1.press("call")
    t[0] += 61
    assert w1.notices() == ["The phone stops ringing. Nobody answered."]
    # a partner out of session can't be reached
    board.stop("agent_2")
    assert code(w1.press("call")) == "PressSuccess:NoAnswer"
    # a mock run: the pair runs in parallel with the switchboard, and replays stay exact
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    r = Run(tmp_path / "r", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True)
    r.phase_a(2, 1, 150, 1)
    outs, n, bad = write_viewer(tmp_path / "r")
    assert n == 2 and bad == []
