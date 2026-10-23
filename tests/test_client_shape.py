"""Checks the real Anthropic request shape offline, against a stub HTTP transport."""

import json

import anthropic
import httpx2 as httpx

from agent.client import AnthropicClient, block_to_dict
from agent.tools import ALL_TOOLS

REPLY = {
    "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-sonnet-5-5",
    "content": [
        {"type": "thinking", "thinking": "", "signature": "sig"},
        {"type": "tool_use", "id": "toolu_1", "name": "move", "input": {"dx": 1, "dy": 0}},
    ],
    "stop_reason": "tool_use", "stop_sequence": None,
    "usage": {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 100},
}


def _client(seen, fallback):
    def handler(req):
        seen.append((req, json.loads(req.content)))
        return httpx.Response(200, json=REPLY)

    c = AnthropicClient.__new__(AnthropicClient)
    c.client = anthropic.Anthropic(api_key="test", base_url="http://stub.local",
                                   http_client=anthropic.DefaultHttpxClient(transport=httpx.MockTransport(handler)))
    c.model, c.effort, c.max_tokens, c.refusal_fallback, c.mock = "claude-sonnet-5-5", "medium", 8000, fallback, False
    c.thinking_display = "summarized"
    return c


def test_request_shape_and_thinking_round_trip():
    seen = []
    c = _client(seen, fallback=True)
    r = c.create("soul text", ALL_TOOLS, [{"role": "user", "content": "hi"}])
    req, body = seen[0]
    assert req.headers["anthropic-beta"] == "server-side-fallback-2026-07-01"
    assert body["fallbacks"] == "default"
    assert body["cache_control"] == {"type": "ephemeral"}
    assert body["output_config"] == {"effort": "medium"}
    assert body["system"] == "soul text" and len(body["tools"]) == len(ALL_TOOLS)
    assert body["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert "temperature" not in body
    msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": r.content},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "ok"}]}]
    c.create("soul text", ALL_TOOLS, msgs)
    assert seen[1][1]["messages"][1]["content"][0] == {"type": "thinking", "thinking": "", "signature": "sig"}
    assert block_to_dict(r.content[1])["name"] == "move"


def test_no_fallback_uses_plain_messages():
    seen = []
    _client(seen, fallback=False).create("s", ALL_TOOLS, [{"role": "user", "content": "hi"}])
    assert "fallbacks" not in seen[0][1]
    assert "beta" not in str(seen[0][0].url)
