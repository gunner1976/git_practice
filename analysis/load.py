"""Readers for a run directory."""

from __future__ import annotations

import json
from pathlib import Path


def events(path: Path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def phase_a_sessions(root: Path) -> dict[str, list[tuple[int, Path]]]:
    """agent -> [(session_number, log_path)] in order, skipping crashed attempts."""
    out: dict[str, list[tuple[int, Path]]] = {}
    for p in sorted((Path(root) / "phase_a").glob("*/session_??.jsonl")):
        out.setdefault(p.parent.name, []).append((int(p.stem.split("_")[1]), p))
    return out


def phase_b_logs(root: Path) -> list[tuple[str, str, Path]]:
    out = []
    for p in sorted((Path(root) / "phase_b").glob("*/*.jsonl")):
        if ".crashed" not in p.name:
            out.append((p.parent.name, p.stem, p))
    return out


def ledger(root: Path) -> list[dict]:
    p = Path(root) / "ledger.jsonl"
    return events(p) if p.exists() else []
