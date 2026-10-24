import json
from pathlib import Path

import pytest
import yaml

from agent.client import MockClient
from agent.cost import Budget, BudgetExceeded, call_cost
from agent.notes import Notes, NotesError
from agent.runner import Run
from agent.tools import ALL_TOOLS

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
SOUL = (ROOT / "soul.md").read_text()


def small_cfg(steps=15):
    cfg = json.loads(json.dumps(CFG))
    cfg["agent"]["steps_per_session"] = steps
    return cfg


def test_souls_have_no_goals_rewards_or_games():
    for p in [ROOT / "soul.md", *sorted((ROOT / "souls").glob("*.md"))]:
        low = p.read_text().lower()
        for word in ("goal", "reward", "game", "play", "task", "score", "rock", "cube", "spawn", "egg", "secret", "hidden"):
            assert word not in low, (p.name, word)


def test_tool_schemas_are_well_formed():
    names = [t["name"] for t in ALL_TOOLS]
    assert len(names) == len(set(names))
    assert {"move", "jump", "pick_up", "place", "throw", "wait", "read_note", "write_note", "list_notes"} == set(names)
    for t in ALL_TOOLS:
        assert t["input_schema"]["type"] == "object"


def test_notes_stay_inside_directory(tmp_path):
    n = Notes(tmp_path / "notes")
    d = n.write("a/b.md", "hello\n")
    assert "+hello" in d["diff"]
    assert n.read("a/b.md") == "hello\n"
    with pytest.raises(NotesError):
        n.write("../escape.md", "x")
    with pytest.raises(NotesError):
        n.read("/etc/passwd")


def test_cost_formula():
    price = CFG["pricing"]["claude-sonnet-5-5"]
    u = {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000, "cache_creation_input_tokens": 1_000_000}
    assert call_cost(u, price) == pytest.approx(2 + 10 + 0.2 + 2.5)


def test_budget_cap_stops_cleanly(tmp_path):
    run = Run(tmp_path / "r", small_cfg(40), SOUL, max_usd=0.02, mock=True)
    run.phase_a(1, 3, 40, 1)
    assert run.budget.stopped
    assert run.budget.spent <= 0.02
    assert run.stopped_reason
    log = (tmp_path / "r/phase_a/agent_1/session_01.jsonl").read_text().splitlines()
    assert json.loads(log[-1])["kind"] == "aborted"
    # resuming with a higher cap finishes the job, and earlier spend still counts
    spent_before = run.budget.spent
    run2 = Run(tmp_path / "r", small_cfg(40), SOUL, max_usd=50, mock=True)
    assert run2.budget.spent == pytest.approx(spent_before)
    run2.phase_a(1, 3, 40, 1)
    assert all(run2.state["phase_a"][f"agent_1/{k}"]["done"] for k in (1, 2, 3))
    assert list((tmp_path / "r/phase_a/agent_1").glob("*.crashed*.jsonl"))


class Crashy(MockClient):
    def __init__(self, at):
        super().__init__(seed=1)
        self.at = at

    def create(self, *a, **k):
        if self.n + 1 == self.at:
            raise RuntimeError("simulated crash")
        return super().create(*a, **k)


def test_resume_after_crash_restores_notes(tmp_path, monkeypatch):
    run = Run(tmp_path / "r", small_cfg(15), SOUL, max_usd=50, mock=True)
    run.phase_a(1, 1, 15, 1)  # session 1 completes
    notes_dir = tmp_path / "r/agents/agent_1/notes"
    after_s1 = Notes(notes_dir).dump()
    monkeypatch.setattr(run, "_client", lambda seed: Crashy(at=6))
    with pytest.raises(RuntimeError):
        run.phase_a(1, 2, 15, 1)  # session 2 crashes part-way
    assert not run.state["phase_a"].get("agent_1/2", {}).get("done")
    (notes_dir / "debris.md").write_text("written during the crashed attempt")
    run2 = Run(tmp_path / "r", small_cfg(15), SOUL, max_usd=50, mock=True)
    assert Notes(tmp_path / "r/agents/agent_1/snapshots/session_02_start").dump() == after_s1
    run2.phase_a(1, 2, 15, 1)
    assert run2.state["phase_a"]["agent_1/2"]["done"]
    assert "debris.md" not in Notes(notes_dir).dump()
    assert (tmp_path / "r/phase_a/agent_1/session_02.crashed1.jsonl").exists()


def test_session_log_contents(tmp_path):
    run = Run(tmp_path / "r", small_cfg(20), SOUL, max_usd=50, mock=True)
    run.phase_a(1, 1, 20, 1)
    kinds = [json.loads(l)["kind"] for l in (tmp_path / "r/phase_a/agent_1/session_01.jsonl").read_text().splitlines()]
    for k in ("session_start", "observation", "assistant", "action", "tool_call", "session_end"):
        assert k in kinds
    end = [json.loads(l) for l in (tmp_path / "r/phase_a/agent_1/session_01.jsonl").read_text().splitlines() if '"session_end"' in l][0]
    assert end["steps_used"] == 20
    led = (tmp_path / "r/ledger.jsonl").read_text().splitlines()
    assert all("usage" in json.loads(l) and "cost_usd" in json.loads(l) for l in led)


def test_eval_veterans_get_memory_fresh_get_none(tmp_path):
    cfg = small_cfg(10)
    run = Run(tmp_path / "r", cfg, SOUL, max_usd=50, mock=True)
    run.phase_a(2, 1, 10, 1)
    run.phase_b(parallel=2)
    res = [json.loads(l) for l in (tmp_path / "r/eval_results.jsonl").read_text().splitlines()]
    assert len(res) == 4 * 4
    assert {r["group"] for r in res} == {"veteran", "fresh"}
    assert len({r["seed"] for r in res}) == 1
    vet_notes = tmp_path / "r/phase_b/agent_1/make_cubes_notes"
    fresh_log = (tmp_path / "r/phase_b/fresh_1/make_cubes.jsonl").read_text()
    assert any(vet_notes.iterdir())
    assert "your notes directory is empty" in fresh_log


def test_analysis_report_builds(tmp_path):
    from analysis.report import build_report

    run = Run(tmp_path / "r", small_cfg(25), SOUL, max_usd=50, mock=True)
    run.set_meta(phase_a={"n_agents": 2, "n_sessions": 2, "steps": 25})
    run.phase_a(2, 2, 25, 2)
    run.phase_b(parallel=4)
    p = build_report(tmp_path / "r")
    text = p.read_text()
    assert "veterans vs fresh" in text and "Hidden rule" in text and "Play markers" in text
    assert (p.parent / "eval_scores.png").exists()


def test_replay_viewer_matches_logs(tmp_path):
    from analysis.replay import write_viewer

    run = Run(tmp_path / "r", small_cfg(20), SOUL, max_usd=50, mock=True)
    run.phase_a(2, 2, 20, 2)
    run.phase_b(parallel=4)
    outs, n, bad = write_viewer(tmp_path / "r")
    assert n == 2 * 2 + 4 * 4
    assert bad == []
    for out in outs:
        html = out.read_text()
        assert "/*__DATA__*/null" not in html and '"sessions":' in html


def test_prune_context_trims_rarely_and_keeps_turn_order():
    from agent.loop import prune_context

    msgs = [{"role": "user", "content": "Begin"}]
    for i in range(60):
        msgs.append({"role": "assistant", "content": [{"type": "tool_use", "id": f"t{i}", "name": "observe", "input": {}}]})
        msgs.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 500}]})
    n = prune_context(msgs, 20000)
    assert n > 0 and msgs[1]["role"] == "assistant" and "cleared" in msgs[0]["content"]
    assert len(json.dumps(msgs)) <= 10000 + 1200
    # the next few turns stay under the limit, so nothing is trimmed (the cache survives)
    for i in range(5):
        msgs.append({"role": "assistant", "content": [{"type": "tool_use", "id": f"u{i}", "name": "observe", "input": {}}]})
        msgs.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"u{i}", "content": "y" * 500}]})
        assert prune_context(msgs, 20000) == 0
