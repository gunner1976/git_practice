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
