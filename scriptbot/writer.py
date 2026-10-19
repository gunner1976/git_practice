"""Rank candidate stories and write the episode script with Claude."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date

import anthropic

from .feeds import Story

log = logging.getLogger(__name__)

WORDS_PER_SECOND = 2.5  # conversational YouTube delivery, ~150 wpm

SYSTEM_PROMPT = """\
You are the head writer for a daily YouTube Short-style AI news show. The host \
is an AI, and it knows it: it is witty, plain-spoken, a little self-deprecating \
about being a language model, and never hypes. The audience is curious tech \
people who want the signal in 90 seconds.

Each day you get a list of candidate stories (from RSS feeds, last 24 hours). Your job:

1. Rank and pick the {top_n} most important AI stories for this audience. Favour \
genuine news (launches, research results, policy, funding with real consequences, \
notable failures) over opinion pieces, listicles, promos, and minor updates. When \
several candidates cover the same event, pick the single best one. Skip anything \
that is a follow-up of an event in the "already covered" list unless there is a \
substantial new development.
2. Write a script that reads aloud in about 90 seconds (210-240 spoken words in total \
across hook, roundup, take and signoff):
   - hook: one or two punchy sentences that make people stay. No "Welcome back".
   - roundup: one tight beat per chosen story, in ranked order, 1-3 sentences each. \
State what happened and why it matters. Do not invent facts beyond the provided \
title and summary; if details are thin, stay general rather than guessing.
   - take: one clearly opinionated take on one of the chosen stories. Commit to a \
position and give a reason. Mark it as opinion in the voice ("Here's my take...").
   - signoff: a short self-aware sign-off from the AI host (a wink about being an \
AI), plus a nudge to subscribe. One or two sentences.
Write for the ear: short sentences, no URLs, no markdown, no stage directions, no emoji.

Refer to stories only by the ids you were given."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "episode_title": {"type": "string", "description": "YouTube title, under 70 characters"},
        "ranking": {
            "type": "array",
            "description": "Chosen stories, most important first",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "why": {"type": "string", "description": "One sentence: why it made the cut"},
                },
                "required": ["id", "why"],
                "additionalProperties": False,
            },
        },
        "hook": {"type": "string"},
        "roundup": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "line": {"type": "string"}},
                "required": ["id", "line"],
                "additionalProperties": False,
            },
        },
        "take": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "text": {"type": "string"}},
            "required": ["id", "text"],
            "additionalProperties": False,
        },
        "signoff": {"type": "string"},
    },
    "required": ["episode_title", "ranking", "hook", "roundup", "take", "signoff"],
    "additionalProperties": False,
}


@dataclass
class RankedStory:
    story: Story
    why: str
    line: str


@dataclass
class Script:
    episode_title: str
    hook: str
    roundup: list[RankedStory]
    take_story: Story
    take: str
    signoff: str

    @property
    def spoken_text(self) -> str:
        parts = [self.hook, *(r.line for r in self.roundup), self.take, self.signoff]
        return "\n".join(parts)

    @property
    def word_count(self) -> int:
        return len(self.spoken_text.split())

    @property
    def est_seconds(self) -> int:
        return round(self.word_count / WORDS_PER_SECOND)

    @property
    def stories(self) -> list[Story]:
        return [r.story for r in self.roundup]


class ScriptError(RuntimeError):
    pass


def build_user_message(stories: list[Story], recent_titles: list[str], today: date) -> str:
    candidates = [
        {
            "id": s.id,
            "title": s.title,
            "source": s.source,
            "published_utc": s.published.strftime("%Y-%m-%d %H:%M"),
            "summary": s.summary,
        }
        for s in stories
    ]
    covered = "\n".join(f"- {t}" for t in recent_titles) or "(none)"
    return (
        f"Episode date: {today.isoformat()}\n\n"
        f"Already covered in recent episodes:\n{covered}\n\n"
        f"Candidate stories ({len(candidates)}):\n"
        f"{json.dumps(candidates, ensure_ascii=False, indent=1)}"
    )


def parse_script(data: dict, stories: list[Story], top_n: int) -> Script:
    """Validate model output against the real candidate list."""
    by_id = {s.id: s for s in stories}
    why = {}
    for item in data["ranking"]:
        if item["id"] in by_id and item["id"] not in why:
            why[item["id"]] = item["why"]
        else:
            log.warning("Ignoring unknown or duplicate ranked id %r", item["id"])

    roundup, seen = [], set()
    for item in data["roundup"]:
        sid = item["id"]
        if sid not in by_id or sid in seen:
            log.warning("Ignoring unknown or duplicate roundup id %r", sid)
            continue
        seen.add(sid)
        roundup.append(RankedStory(story=by_id[sid], why=why.get(sid, ""), line=item["line"].strip()))

    if not roundup:
        raise ScriptError("Model returned no roundup items that match candidate stories")
    if len(roundup) > top_n:
        roundup = roundup[:top_n]
    expected = min(top_n, len(stories))
    if len(roundup) < expected:
        log.warning("Roundup has %d stories; expected %d", len(roundup), expected)

    take_id = data["take"]["id"]
    take_story = by_id.get(take_id) or roundup[0].story
    return Script(
        episode_title=data["episode_title"].strip(),
        hook=data["hook"].strip(),
        roundup=roundup,
        take_story=take_story,
        take=data["take"]["text"].strip(),
        signoff=data["signoff"].strip(),
    )


def write_script(
    client: anthropic.Anthropic,
    stories: list[Story],
    recent_titles: list[str],
    today: date,
    *,
    model: str,
    effort: str,
    max_tokens: int,
    top_n: int,
) -> Script:
    response = client.beta.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT.format(top_n=top_n),
        messages=[{"role": "user", "content": build_user_message(stories, recent_titles, today)}],
        output_config={
            "effort": effort,
            "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA},
        },
        # On a safety-classifier false positive, retry server-side on the
        # model Anthropic recommends for that refusal category.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    log.info(
        "Claude request %s: model=%s stop=%s in=%s out=%s",
        response._request_id, response.model, response.stop_reason,
        response.usage.input_tokens, response.usage.output_tokens,
    )

    if response.stop_reason == "refusal":
        details = response.stop_details
        raise ScriptError(f"Model declined the request: {details.category if details else 'unknown'}")
    if response.stop_reason == "max_tokens":
        raise ScriptError("Response hit max_tokens before the script was complete; raise anthropic.max_tokens")

    text = next((b.text for b in response.content if b.type == "text"), None)
    if not text:
        raise ScriptError("Model returned no text content")
    return parse_script(json.loads(text), stories, top_n)
