import json
from pathlib import Path

import yaml

from agent.ladder import Ladder, ladder_summary, stage_world_cfg
from world import World

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())


def lenient_cfg(steps=12):
    cfg = json.loads(json.dumps(CFG))
    cfg["ladder"]["steps_per_session"] = steps
    cfg["ladder"]["replicates"] = 1
    cfg["ladder"]["contestants"] = cfg["ladder"]["contestants"][:2]
    for st in cfg["ladder"]["stages"]:
        st["free_sessions"] = 1
        st["eval_seeds"] = st["eval_seeds"][:2]
        st["min_seeds"] = 0  # everyone advances, so the whole ladder is exercised
    return cfg


def test_stage_world_cfg_switches_rules():
    stages = {s["name"]: s for s in CFG["ladder"]["stages"]}
    w1 = World(stage_world_cfg(CFG["world"], stages["tier1"]))
    assert w1.rock_rule_on and w1.rules == []
    w3 = World(stage_world_cfg(CFG["world"], stages["tier3"]))
    assert {r.id for r in w3.rules} == {"stack_chime", "patient_ring"}
    a = World(stage_world_cfg(CFG["world"], stages["tier4_transfer"]), seed=1401)
    b = World(stage_world_cfg(CFG["world"], stages["tier4_transfer"]), seed=1402)
    assert (a.rock_threshold, a.rules[0].order, a.rules[1].waits) != (b.rock_threshold, b.rules[0].order, b.rules[1].waits)


def test_full_ladder_graduates_with_bundle_and_transfer(tmp_path):
    lad = Ladder(tmp_path / "L", lenient_cfg(), max_usd=50, mock=True, base_dir=ROOT)
    survivors = lad.run(parallel=2)
    assert survivors == ["curious_r1", "systematic_r1"]
    g = lad.state["ladder"]["graduation"]
    assert g["done"] and set(g["transfer"]) == set(survivors)
    b = tmp_path / "L/graduates/curious_r1"
    assert (b / "soul.md").read_text() == (ROOT / "soul.md").read_text()
    assert (b / "REVIEW_REQUIRED.md").exists() and (b / "notes").is_dir()
    trace = json.loads((b / "trace.json").read_text())
    assert [s["stage"] for s in trace["stages"]] == [s["name"] for s in CFG["ladder"]["stages"]]
    rows = [json.loads(l) for l in (tmp_path / "L/ladder_results.jsonl").read_text().splitlines()]
    assert {r["kind"] for r in rows} == {"eval", "with_notes", "empty"}
    assert "Graduates" in ladder_summary(tmp_path / "L")


def test_strict_ladder_eliminates_and_stops(tmp_path):
    cfg = lenient_cfg()
    for st in cfg["ladder"]["stages"]:
        st["min_seeds"] = 99  # impossible
    lad = Ladder(tmp_path / "L", cfg, max_usd=50, mock=True, base_dir=ROOT)
    assert lad.run(parallel=2) == []
    assert "tier2" not in {k.split("/")[1] for k in lad.state["ladder"] if k.startswith("free/")}
    assert not (tmp_path / "L/graduates").exists()


def test_ladder_resumes_after_budget_stop(tmp_path):
    lad = Ladder(tmp_path / "L", lenient_cfg(), max_usd=0.05, mock=True, base_dir=ROOT)
    assert lad.run(parallel=1) == [] and lad.budget.stopped
    done_before = sum(1 for v in lad.state["ladder"].values() if v.get("done"))
    lad2 = Ladder(tmp_path / "L", lenient_cfg(), max_usd=50, mock=True, base_dir=ROOT)
    assert lad2.run(parallel=2) == ["curious_r1", "systematic_r1"]
    assert sum(1 for v in lad2.state["ladder"].values() if v.get("done")) > done_before
