import json

from analysis.closure import closures, openness


def _write(root, agent, day, log):
    d = root / "phase_a" / agent
    d.mkdir(parents=True, exist_ok=True)
    (d / f"session_{day:02d}.jsonl").write_text("\n".join(json.dumps(e) for e in log + [{"kind": "session_end"}]))


def _say(step, text):
    return {"kind": "assistant", "step": step, "content": [{"type": "text", "text": text}]}


def _note(step, text):
    return {"kind": "tool_call", "name": "append_note", "step": step, "input": {"content": text}, "result": "ok"}


def test_closure_grounding_lock_in_and_reopening(tmp_path):
    # Ada closes the moon on a hunch, writes it down as a rule, and on later days only restates it
    _write(tmp_path, "ada", 1, [_say(1, "The moon is way too far to reach."), _note(2, "Moon: unreachable. Don't re-test.")])
    _write(tmp_path, "ada", 2, [_say(1, "I have no new idea for the moon; it is still out of reach.")])
    # Bo measures the moon first, closes it, and reopens it the next day with a new plan to reach it
    _write(tmp_path, "bo", 1, [_say(1, "The moon is about 1 degree across, so its distance is large."), _say(2, "Reaching the moon seems impossible for now.")])
    _write(tmp_path, "bo", 2, [_say(1, "New plan: maybe I can estimate how far the moon is and find a way to get closer.")])
    # Cy changes plan rather than giving up; Di closes something on its last day so far
    _write(tmp_path, "cy", 1, [_say(1, "I can't reach the tower top there, so I'll try a stair instead.")])
    _write(tmp_path, "di", 1, [_say(1, "The Spire top is unreachable.")])
    c = closures(tmp_path)
    (a,) = c["ada"]
    assert a["topic"] == "the moon" and not a["grounded"] and a["locked_in"] and a["reopened"] is None and a["restated"] == 2
    assert openness(c["ada"]) == 0.0
    (b,) = c["bo"]
    assert b["grounded"] and b["reopened"]["at"] == [2, 1] and openness(c["bo"]) == 1.0
    assert c["cy"] == [] and openness(c["cy"]) == 1.0
    assert c["di"][0]["pending"] and openness(c["di"]) == 1.0
