"""Provenance helper.

Every derived number in the package should be traceable to a raw source file
(and, where possible, a sheet+cell or a page). `Cite` objects render to a short
inline tag for figures/tables and to a full reference line for docs, and they
resolve the source file's SHA256 from data/manifest.csv so a citation is pinned
to the exact bytes that were read.

    >>> c = Cite("data/raw/tec12_drill/2023-09-29 Tec-12 Economics.xlsm",
    ...          sheet="Inputs", cell="C12", note="oil price, USD/bbl")
    >>> str(c)
    '2023-09-29 Tec-12 Economics.xlsm!Inputs!C12'
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.csv"


@lru_cache(maxsize=1)
def _manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open(newline="") as f:
        return {r["path"]: r for r in csv.DictReader(f)}


@dataclass(frozen=True)
class Cite:
    path: str                       # repo-relative path under data/raw
    sheet: str | None = None        # Excel sheet name
    cell: str | None = None         # cell or range, e.g. "C12" or "B4:F20"
    page: int | None = None         # PDF / deck page number (1-based)
    note: str = ""                  # what the number is
    _m: dict = field(default_factory=dict, init=False, repr=False, compare=False)

    @property
    def name(self) -> str:
        return Path(self.path).name

    @property
    def sha256(self) -> str:
        return _manifest().get(self.path, {}).get("sha256", "UNMANIFESTED")

    @property
    def file_id(self) -> str:
        return _manifest().get(self.path, {}).get("file_id", "")

    def __str__(self) -> str:
        loc = ""
        if self.sheet:
            loc += f"!{self.sheet}"
        if self.cell:
            loc += f"!{self.cell}"
        if self.page is not None:
            loc += f" p.{self.page}"
        return f"{self.name}{loc}"

    def short(self) -> str:
        """Tag for figure captions: name + location + first 8 chars of sha."""
        return f"{self} [{self.sha256[:8]}]"

    def full(self) -> str:
        """Reference line for docs."""
        bits = [str(self)]
        if self.note:
            bits.append(self.note)
        bits.append(f"Drive ID {self.file_id or '?'}")
        bits.append(f"sha256 {self.sha256}")
        return " | ".join(bits)


def unmanifested(paths: list[str]) -> list[str]:
    """Return any cited paths that are not in the manifest — a provenance hole."""
    m = _manifest()
    return [p for p in paths if p not in m]
