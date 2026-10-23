"""The agent's notes directory: its only long-term memory."""

from __future__ import annotations

import difflib
import shutil
from pathlib import Path

MAX_FILE_CHARS = 40_000


class NotesError(Exception):
    pass


class Notes:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, rel: str) -> Path:
        rel = rel.strip().lstrip("/")
        if not rel:
            raise NotesError("Empty path.")
        p = (self.root / rel).resolve()
        if self.root.resolve() not in p.parents:
            raise NotesError("Notes paths must stay inside your notes directory.")
        return p

    def list(self) -> list[str]:
        return sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file())

    def read(self, rel: str) -> str:
        p = self._path(rel)
        if not p.is_file():
            raise NotesError(f"No such note: {rel}")
        return p.read_text()

    def write(self, rel: str, content: str) -> dict:
        if len(content) > MAX_FILE_CHARS:
            raise NotesError(f"Notes files are limited to {MAX_FILE_CHARS} characters.")
        p = self._path(rel)
        old = p.read_text() if p.is_file() else ""
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        diff = "".join(difflib.unified_diff(old.splitlines(True), content.splitlines(True), f"a/{rel}", f"b/{rel}"))
        return {"path": rel, "diff": diff, "chars_before": len(old), "chars_after": len(content)}

    def snapshot(self, dest: Path) -> None:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(self.root, dest)

    def restore(self, src: Path) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)
        shutil.copytree(src, self.root)

    def dump(self) -> dict[str, str]:
        return {f: (self.root / f).read_text() for f in self.list()}
