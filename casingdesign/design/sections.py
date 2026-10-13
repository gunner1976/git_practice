"""Tapered (sectional) string designs: a list of pipe sections from top to bottom."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from casingdesign.catalog import PipeSpec


@dataclass(frozen=True)
class Section:
    top_md: float
    bottom_md: float
    spec: PipeSpec

    @property
    def length(self) -> float:
        return self.bottom_md - self.top_md


@dataclass(frozen=True)
class StringDesign:
    """Sections ordered top-down, contiguous, covering hanger to shoe."""

    sections: tuple[Section, ...]

    def __post_init__(self):
        if not self.sections:
            raise ValueError("a design needs at least one section")
        for a, b in zip(self.sections, self.sections[1:]):
            if abs(a.bottom_md - b.top_md) > 1e-6:
                raise ValueError("sections must be contiguous")

    @classmethod
    def uniform(cls, top_md: float, bottom_md: float, spec: PipeSpec) -> StringDesign:
        return cls((Section(top_md, bottom_md, spec),))

    @property
    def top_md(self) -> float:
        return self.sections[0].top_md

    @property
    def bottom_md(self) -> float:
        return self.sections[-1].bottom_md

    @property
    def is_uniform(self) -> bool:
        return len(self.sections) == 1

    @property
    def label(self) -> str:
        if self.is_uniform:
            return self.sections[0].spec.label
        return " / ".join(f"{s.spec.label} ({s.top_md:.0f}-{s.bottom_md:.0f})"
                          for s in self.sections)

    def section_index(self, md: np.ndarray) -> np.ndarray:
        """Index of the section in effect at each MD (bottom boundary belongs to the
        upper section, except the shoe which belongs to the last)."""
        bounds = np.array([s.bottom_md for s in self.sections[:-1]])
        return np.searchsorted(bounds, md, side="left")

    def spec_at(self, md: np.ndarray) -> list[PipeSpec]:
        return [self.sections[i].spec for i in self.section_index(md)]

    def per_depth(self, md: np.ndarray, attr: str) -> np.ndarray:
        """Array of a PipeSpec attribute (e.g. 'burst') at each MD."""
        vals = np.array([getattr(s.spec, attr) for s in self.sections], dtype=float)
        return vals[self.section_index(md)]

    def weight_per_ft(self, md: np.ndarray) -> np.ndarray:
        from casingdesign.loads.axial import weight_per_ft
        vals = np.array([weight_per_ft(s.spec) for s in self.sections])
        return vals[self.section_index(md)]
