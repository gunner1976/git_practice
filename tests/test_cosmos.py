import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import run  # noqa: E402
from agent.cosmos import Cosmos  # noqa: E402


def _cosmos(root, max_usd=50):
    cfg = run.read_cfg(ROOT / "configs/cosmos.yaml")
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60)
    return Cosmos(root, cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=max_usd, mock=True)


def test_cosmos_agents_persist_and_hear_shared_discoveries(tmp_path):
    from analysis.replay import write_viewer

    c = _cosmos(tmp_path / "cosmos")
    assert c.add(["Christian", "Vern", "Keats"]) == ["christian", "vern", "keats"]
    assert "Your name is Vern." in (tmp_path / "cosmos/agents/vern/notes/SOUL.md").read_text()
    c.advance(1)
    assert c.days_lived() == {"christian": 1, "vern": 1, "keats": 1}
    # Christian is promoted (as the judge would record it): the discovery is shared with the others
    (tmp_path / "cosmos/promotions.json").write_text(json.dumps({"agents": {
        "christian": {"promoted": True, "judge": "test", "verdict": {"day": 1, "step": 9, "quote": "The shadow on the moon is curved, so my world is round.", "evidence": "eclipse"}},
        "vern": {"promoted": False}, "keats": {"promoted": False}}}))
    import analysis.promotion as pr
    keep, pr.promote = pr.promote, lambda *a, **k: None
    try:
        new = c.judge(None)
    finally:
        pr.promote = keep
    assert [d["name"] for d in new] == ["Christian"] and new[0]["shared"] and not new[0]["assisted_by"]
    # a newcomer joins later, on its own day 1
    c.add(["Kip"])
    c.advance(1)
    assert c.days_lived() == {"christian": 2, "vern": 2, "keats": 2, "kip": 1}
    opening = lambda a, d: json.loads((tmp_path / f"cosmos/phase_a/{a}/session_{d:02d}.jsonl").read_text().splitlines()[0])["opening"]  # noqa: E731
    assert "from Christian on another world" in opening("vern", 2) and "my world is round" in opening("kip", 1)
    assert "another world" not in opening("christian", 2)
    # the world persisted: day 2 started from day 1's end state
    first = json.loads((tmp_path / "cosmos/phase_a/keats/session_02.jsonl").read_text().splitlines()[0])
    assert "Your name is Keats." in first["soul"] and "Eko." not in first["soul"].split("\n")[1]
    assert "start_state" in json.loads((tmp_path / "cosmos/phase_a/vern/session_02.jsonl").read_text().splitlines()[0])
    # Vern now reaches the same conclusion on day 2, after hearing it: promoted but assisted, not re-shared
    (tmp_path / "cosmos/promotions.json").write_text(json.dumps({"agents": {
        "christian": {"promoted": True, "judge": "test", "verdict": {"day": 1, "step": 9, "quote": "x"}},
        "vern": {"promoted": True, "judge": "test", "verdict": {"day": 2, "step": 4, "quote": "Round, like Christian said."}}}}))
    pr.promote = lambda *a, **k: None
    try:
        new = c.judge(None)
    finally:
        pr.promote = keep
    assert [d["name"] for d in new] == ["Vern"] and new[0]["assisted_by"] == ["round_world:christian"] and not new[0]["shared"]
    # the observer tells one agent something once; only that agent lives the next day
    assert c.tell("keats", "Your mission is to reach the moon.") == 3
    c.advance(1, only=["keats"])
    assert c.days_lived() == {"christian": 2, "vern": 2, "keats": 3, "kip": 1}
    assert opening("keats", 3).count("Your mission is to reach the moon.") == 1
    # state survives reopening, and every day replays exactly
    assert _cosmos(tmp_path / "cosmos").agents == ["christian", "vern", "keats", "kip"]
    outs, n, bad = write_viewer(tmp_path / "cosmos")
    assert n == 8 and bad == []


def test_wait_and_multi_day_sessions_carry_eko_time(tmp_path):
    from analysis.replay import write_viewer

    cfg = run.read_cfg(ROOT / "configs/cosmos.yaml")
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60, wait_tool=True, days_per_session=3)
    c = Cosmos(tmp_path / "c", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True)
    c.add(["Ada"])
    c.advance(2)
    logs = [[json.loads(l) for l in (tmp_path / f"c/phase_a/ada/session_{k:02d}.jsonl").read_text().splitlines()] for k in (1, 2)]
    ends = [next(e for e in L if e["kind"] == "session_end") for L in logs]
    waits = [e for L in logs for e in L if e["kind"] == "wait"]
    assert waits and all(w["hours"] <= w["hours_asked"] + 1e-9 for w in waits)
    assert any(w["woke"] != "time passed" for w in waits)               # something in the sky woke it
    day = c.run._world().eko.day
    for e in ends:  # waiting lets a session cover more than one EKO day, never more than three
        assert e["eko_tau_end"] - e["eko_tau_start"] <= 3 * day + 1
    assert max(e["eko_tau_end"] - e["eko_tau_start"] for e in ends) > day
    assert ends[1]["eko_tau_start"] >= ends[0]["eko_tau_end"]            # time carries on: next dawn
    eko = c.run._world().eko
    assert ends[1]["eko_tau_start"] == eko.wake_after(ends[0]["eko_tau_end"])  # the next dawn, or on if it just passed one
    assert json.loads((tmp_path / "c/agents/ada/eko_clock.json").read_text())["eko_day"] >= 2
    outs, n, bad = write_viewer(tmp_path / "c")
    assert n == 2 and bad == []


def test_sync_brings_everyone_to_the_same_eko_day(tmp_path):
    cfg = run.read_cfg(ROOT / "configs/cosmos.yaml")
    cfg["agent"]["clock"].update(session_seconds=300, warn_before_seconds=60, wait_tool=True, days_per_session=3)
    c = Cosmos(tmp_path / "c", cfg, (ROOT / "paper/system_prompt.md").read_text(), max_usd=50, mock=True)
    c.add(["Ada", "Bo", "Cy"])
    c.advance(1, only=["ada"])
    c.advance(1, only=["ada"])
    assert c.eko_day("ada") > c.eko_day("bo") == 0
    c.sync_to(4)
    assert {a: c.eko_day(a) for a in c.agents} == {"ada": 4, "bo": 4, "cy": 4}
    D = c.run._world().eko.day
    for a in c.agents:  # nobody ran past the end of day 4 (beyond the last turn's few minutes)
        for p in sorted((tmp_path / f"c/phase_a/{a}").glob("session_*.jsonl")):
            end = next(json.loads(l) for l in p.read_text().splitlines() if '"session_end"' in l)
            assert end["eko_tau_end"] < 4 * D + D / 4 + 0.05 * D
    # one more shared day for everyone: they all wake at the same dawn
    c.sync_to(5)
    assert set(c.eko_day(a) for a in c.agents) == {5}
