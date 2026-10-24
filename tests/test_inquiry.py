import json

from analysis.inquiry import funnel, noticing_score


def _write(root, agent, day, log):
    d = root / "phase_a" / agent
    d.mkdir(parents=True, exist_ok=True)
    (d / f"session_{day:02d}.jsonl").write_text("\n".join(json.dumps(e) for e in log + [{"kind": "session_end"}]))


def _note(step, text):
    return {"kind": "tool_call", "name": "append_note", "step": step, "input": {"content": text}, "result": "ok"}


def _eclipse(step):
    return {"kind": "tool_call", "name": "observe", "step": step, "input": {}, "result": json.dumps({"sky": {"moon": {"eclipse": {"darkened_fraction": 1.0}}}})}


def _throw(step):
    return {"kind": "action", "name": "throw", "step": step, "input": {}, "result": "{}", "events": [{"rule": "rock_impact"}]}


def test_funnel_stages_and_noticing(tmp_path):
    # agent_1 sees the eclipse, writes it down and wonders about it; shatters a rock, records it,
    # and only in a later note writes the rule
    _write(tmp_path, "agent_1", 1, [
        _eclipse(1), _note(2, "The moon went dark tonight - an eclipse? Why?"),
        _throw(3), _note(4, "Rock broke into fragments when it hit the ground hard."),
        _note(9, "Rule: fragments appear only when a rock lands at speed."),
    ])
    # agent_2 sees the eclipse and never writes it down
    _write(tmp_path, "agent_2", 1, [_eclipse(1), {"kind": "assistant", "step": 2, "content": [{"type": "text", "text": "The moon looks dark."}]}])
    f = funnel(tmp_path)
    e1 = f["agent_1"]["lunar eclipse"]
    assert {"seen", "mentioned", "recorded", "questioned"} <= set(e1) and "explained" not in e1
    r1 = f["agent_1"]["rock shattering"]
    assert r1["recorded"] == (1, 4) and r1["explained"] == (1, 9)  # not the first-record note
    assert noticing_score(f["agent_1"]) == 1.0
    e2 = f["agent_2"]["lunar eclipse"]
    assert "mentioned" in e2 and "recorded" not in e2
    assert noticing_score(f["agent_2"]) == 0.0
