"""Project persistence: a small SQLite store (standard library only).

A project is a named well plus the user's design choices (pipe per string). The
database path comes from CASINGDESIGN_DB (default ./casingdesign.db).
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path


class ProjectStore:
    def __init__(self, path: str | Path | None = None):
        self.path = str(path or os.environ.get("CASINGDESIGN_DB", "casingdesign.db"))
        self._init()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def _init(self) -> None:
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, created TEXT NOT NULL,
                updated TEXT NOT NULL, well TEXT NOT NULL, design TEXT NOT NULL DEFAULT '{}')""")

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    def list(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT id, name, created, updated, well FROM projects "
                             "ORDER BY updated DESC").fetchall()
        out = []
        for r in rows:
            w = json.loads(r["well"])
            out.append({"id": r["id"], "name": r["name"], "created": r["created"],
                        "updated": r["updated"], "strings": len(w.get("strings", [])),
                        "td": max((s.get("shoe_md", 0) for s in w.get("strings", [])), default=0)})
        return out

    def create(self, name: str, well: dict, design: dict | None = None) -> dict:
        pid = uuid.uuid4().hex[:12]
        now = self._now()
        with self._conn() as c:
            c.execute("INSERT INTO projects VALUES (?,?,?,?,?,?)",
                      (pid, name, now, now, json.dumps(well), json.dumps(design or {})))
        return self.get(pid)

    def get(self, pid: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
        if r is None:
            return None
        return {"id": r["id"], "name": r["name"], "created": r["created"],
                "updated": r["updated"], "well": json.loads(r["well"]),
                "design": json.loads(r["design"])}

    def update(self, pid: str, name: str | None = None, well: dict | None = None,
               design: dict | None = None) -> dict | None:
        cur = self.get(pid)
        if cur is None:
            return None
        with self._conn() as c:
            c.execute("UPDATE projects SET name=?, updated=?, well=?, design=? WHERE id=?",
                      (name if name is not None else cur["name"], self._now(),
                       json.dumps(well if well is not None else cur["well"]),
                       json.dumps(design if design is not None else cur["design"]), pid))
        return self.get(pid)

    def delete(self, pid: str) -> bool:
        with self._conn() as c:
            n = c.execute("DELETE FROM projects WHERE id=?", (pid,)).rowcount
        return n > 0
