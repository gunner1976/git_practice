"""SQLite record of used stories and completed daily runs."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SCHEMA = """
CREATE TABLE IF NOT EXISTS used_stories (
    url_key  TEXT PRIMARY KEY,
    url      TEXT NOT NULL,
    title    TEXT NOT NULL,
    source   TEXT,
    used_on  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    run_date   TEXT PRIMARY KEY,
    doc_id     TEXT NOT NULL,
    doc_url    TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

_TRACKING_PREFIXES = ("utm_", "mc_")
_TRACKING_PARAMS = {"fbclid", "gclid", "ref", "cmpid", "taid", "source"}


def normalize_url(url: str) -> str:
    """Canonical form used to recognise the same article across runs."""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    query = [
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.lower().startswith(_TRACKING_PREFIXES) and k.lower() not in _TRACKING_PARAMS
    ]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(("https", host, path, urlencode(sorted(query)), ""))


class Store:
    def __init__(self, path: str | Path):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def used_keys(self) -> set[str]:
        return {row[0] for row in self.conn.execute("SELECT url_key FROM used_stories")}

    def recent_titles(self, today: date, days: int) -> list[str]:
        cutoff = (today - timedelta(days=days)).isoformat()
        rows = self.conn.execute(
            "SELECT title FROM used_stories WHERE used_on >= ? ORDER BY used_on DESC", (cutoff,)
        )
        return [row[0] for row in rows]

    def has_run(self, run_date: date) -> str | None:
        row = self.conn.execute(
            "SELECT doc_url FROM runs WHERE run_date = ?", (run_date.isoformat(),)
        ).fetchone()
        return row[0] if row else None

    def record_run(self, run_date: date, doc_id: str, doc_url: str, stories) -> None:
        """Mark stories used and the day done, atomically."""
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.conn:
            self.conn.executemany(
                "INSERT OR IGNORE INTO used_stories (url_key, url, title, source, used_on) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (normalize_url(s.url), s.url, s.title, s.source, run_date.isoformat())
                    for s in stories
                ],
            )
            self.conn.execute(
                "INSERT OR REPLACE INTO runs (run_date, doc_id, doc_url, created_at) "
                "VALUES (?, ?, ?, ?)",
                (run_date.isoformat(), doc_id, doc_url, now),
            )
