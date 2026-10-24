"""Render a session JSONL log as a readable markdown transcript.

    python -m analysis.transcript runs/<run>/phase_a/agent_1/session_01.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def render(path: Path, max_obs_lines: int = 20) -> str:
    out = [f"## {Path(path).parent.name} / {Path(path).stem}", ""]
    for line in Path(path).read_text().splitlines():
        e = json.loads(line)
        k = e["kind"]
        if k == "session_start":
            out += [f"*Opening message:* {e['opening']}", ""]
        elif k == "assistant":
            u = e["usage"]
            for c in e["content"]:
                if c["type"] == "text" and c["text"].strip():
                    out.append(f"**Eko:** {c['text'].strip()}")
                elif c["type"] == "thinking" and c.get("thinking"):
                    out.append(f"> *(thinking)* {c['thinking'].strip()}")
                elif c["type"] == "tool_use":
                    out.append(f"- `{c['name']}({json.dumps(c.get('input', {}))})`")
            out.append(f"  <sub>call {e['call']} · in {u['input_tokens']} / cache-read {u['cache_read_input_tokens']} / cache-write {u['cache_creation_input_tokens']} / out {u['output_tokens']} · ${e['cost_usd']:.4f}{' · FALLBACK' if e.get('fallback') else ''}</sub>")
        elif k == "action":
            out.append(f"  - step {e['step']}: {e['result']}{' (error)' if e['error'] else ''}")
        elif k == "hidden_rule_fired":
            out.append(f"  - **[hidden rule fired: {e['event']['id']} spawned]**")
        elif k == "tool_call" and e["name"] == "observe":
            try:
                n = len(json.loads(e["result"])["world"]["entities"])
                out.append(f"  - world `observe` -> {n} entities")
            except (json.JSONDecodeError, KeyError):
                out.append("  - world `observe` -> (truncated in log)")
        elif k == "tool_call":
            res = e["result"].replace("\n", " / ")
            out.append(f"  - notes `{e['name']}` -> {res[:300]}")
        elif k == "reset_warning":
            out.append(f"  - *(reset warning sent at {e['clock'] / 60:.1f} min)*")
        elif k == "context_pruned":
            out.append(f"  - *(context trimmed: {e['cleared']} older messages dropped)*")
        elif k == "notes_diff":
            out += ["```diff", e["diff"].rstrip()[:3000], "```"]
        elif k == "observation" and e["step"] == 0:
            lines = e["text"].splitlines()
            out += ["```", *lines[:max_obs_lines], "```"]
        elif k == "stop_hook":
            out.append(f"  - *(stop hook nudge #{e['n']})*")
        elif k == "session_ending":
            out.append("  - *(session-end message sent; notes-only grace turns)*")
        elif k == "session_end":
            clock = f", {e['clock_seconds'] / 60:.0f} simulated minutes" if e.get("clock_seconds") else ""
            out += ["", f"*Session ended: {e['reason']}, {e['steps_used']} steps, {e['api_calls']} API calls{clock}.*"]
        elif k == "aborted":
            out += ["", f"*ABORTED: {e['reason']} {e.get('detail', '')}*"]
        elif k == "score":
            out.append(f"*Score ({e['task']}): {e['score']}*")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(render(Path(p)))
