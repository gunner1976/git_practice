"""Fetch RSS/Atom feeds and keep entries from the lookback window."""
from __future__ import annotations

import calendar
import hashlib
import html
import logging
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser

from .config import Feed
from .store import normalize_url

log = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; ai-script-bot/1.0; +https://github.com/)"
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


@dataclass
class Story:
    id: str
    title: str
    url: str
    source: str
    published: datetime
    summary: str


def clean_text(raw: str, limit: int | None = None) -> str:
    text = _WS_RE.sub(" ", html.unescape(_TAG_RE.sub(" ", raw or ""))).strip()
    if limit and len(text) > limit:
        text = text[: limit - 1].rsplit(" ", 1)[0] + "…"
    return text


def _entry_time(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed = entry.get(key)
        if parsed:
            # feedparser normalises these struct_times to UTC.
            return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)
    return None


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def fetch_feed(feed: Feed, timeout: int) -> bytes:
    req = urllib.request.Request(feed.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_entries(feed: Feed, content: bytes, since: datetime, summary_chars: int) -> list[Story]:
    parsed = feedparser.parse(content)
    if parsed.bozo and not parsed.entries:
        raise ValueError(f"unparseable feed: {parsed.bozo_exception}")

    stories = []
    for entry in parsed.entries:
        url = entry.get("link")
        title = clean_text(entry.get("title", ""))
        published = _entry_time(entry)
        # Undated entries are skipped: we can't prove they are from the last 24h.
        if not url or not title or published is None or published < since:
            continue
        summary = entry.get("summary") or ""
        if not summary and entry.get("content"):
            summary = entry["content"][0].get("value", "")
        stories.append(
            Story(
                id="",
                title=title,
                url=url,
                source=feed.name,
                published=published,
                summary=clean_text(summary, summary_chars),
            )
        )
    return stories


def collect_stories(
    feeds: list[Feed],
    since: datetime,
    exclude_keys: set[str],
    *,
    timeout: int = 20,
    summary_chars: int = 600,
    max_candidates: int = 120,
    fetch=fetch_feed,
) -> list[Story]:
    """Fetch every feed, drop old/used/duplicate entries, return newest first."""
    collected: list[Story] = []
    failures = 0
    for feed in feeds:
        try:
            entries = parse_entries(feed, fetch(feed, timeout), since, summary_chars)
        except Exception as exc:  # one bad feed shouldn't sink the run
            failures += 1
            log.warning("Feed failed: %s (%s): %s", feed.name, feed.url, exc)
            continue
        log.info("%s: %d entries in window", feed.name, len(entries))
        collected.extend(entries)

    if failures == len(feeds):
        raise RuntimeError("Every configured feed failed to load")

    collected.sort(key=lambda s: s.published, reverse=True)
    seen_urls, seen_titles, unique = set(exclude_keys), set(), []
    for story in collected:
        url_key, title_key = normalize_url(story.url), _title_key(story.title)
        if url_key in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        seen_titles.add(title_key)
        story.id = "s" + hashlib.sha1(url_key.encode()).hexdigest()[:8]
        unique.append(story)

    if len(unique) > max_candidates:
        log.info("Capping %d candidates to the newest %d", len(unique), max_candidates)
    return unique[:max_candidates]
