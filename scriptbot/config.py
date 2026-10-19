from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Feed:
    name: str
    url: str


@dataclass
class Config:
    feeds: list[Feed]
    timezone: str = "America/Edmonton"
    lookback_hours: int = 24
    top_n: int = 5
    max_candidates: int = 120
    max_summary_chars: int = 600
    recent_history_days: int = 7
    model: str = "claude-opus-5-5"
    effort: str = "high"
    max_tokens: int = 16000
    folder_name: str = "AI Channel Scripts"
    doc_title_prefix: str = "AI Daily Script"
    database: str = "data/stories.db"
    feed_timeout_seconds: int = 20


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text()) or {}

    feeds = []
    for item in raw.get("feeds") or []:
        if isinstance(item, str):
            feeds.append(Feed(name=item, url=item))
        else:
            feeds.append(Feed(name=item.get("name") or item["url"], url=item["url"]))
    if not feeds:
        raise ValueError(f"{path}: 'feeds' must list at least one RSS URL")

    anthropic_cfg = raw.get("anthropic") or {}
    google_cfg = raw.get("google") or {}
    defaults = Config(feeds=[])

    return Config(
        feeds=feeds,
        timezone=raw.get("timezone", defaults.timezone),
        lookback_hours=int(raw.get("lookback_hours", defaults.lookback_hours)),
        top_n=int(raw.get("top_n", defaults.top_n)),
        max_candidates=int(raw.get("max_candidates", defaults.max_candidates)),
        max_summary_chars=int(raw.get("max_summary_chars", defaults.max_summary_chars)),
        recent_history_days=int(raw.get("recent_history_days", defaults.recent_history_days)),
        model=anthropic_cfg.get("model", defaults.model),
        effort=anthropic_cfg.get("effort", defaults.effort),
        max_tokens=int(anthropic_cfg.get("max_tokens", defaults.max_tokens)),
        folder_name=google_cfg.get("folder_name", defaults.folder_name),
        doc_title_prefix=google_cfg.get("doc_title_prefix", defaults.doc_title_prefix),
        database=raw.get("database", defaults.database),
        feed_timeout_seconds=int(raw.get("feed_timeout_seconds", defaults.feed_timeout_seconds)),
    )
