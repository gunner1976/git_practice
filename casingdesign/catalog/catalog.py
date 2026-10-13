"""Pipe body, grade and connection catalog loaded from CSV data files.

The CSV files are intentionally plain so an engineer can audit and extend them
(e.g. add a vendor's premium connection or proprietary grade) without touching code.
"""
from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from importlib import resources

from casingdesign.ratings import (
    PipeGeometry,
    burst_rating,
    collapse_rating,
    pipe_body_yield,
)


@dataclass(frozen=True)
class Grade:
    name: str
    min_yield: float
    max_yield: float
    min_tensile: float
    sour_service: bool


@dataclass(frozen=True)
class PipeItem:
    od: float
    nominal_weight: float
    wall: float
    drift: float

    @property
    def geometry(self) -> PipeGeometry:
        return PipeGeometry(self.od, self.wall)

    @property
    def id(self) -> float:
        return self.geometry.id


@dataclass(frozen=True)
class Connection:
    name: str
    tension_efficiency: float
    burst_efficiency: float
    collapse_efficiency: float
    notes: str = ""


@dataclass(frozen=True)
class PipeSpec:
    """A fully specified casing item: pipe body + grade + connection."""

    pipe: PipeItem
    grade: Grade
    connection: Connection

    @property
    def geometry(self) -> PipeGeometry:
        return self.pipe.geometry

    @property
    def label(self) -> str:
        return (
            f'{self.pipe.od:g}" {self.pipe.nominal_weight:g}# {self.grade.name} '
            f"{self.connection.name}"
        )

    # Ratings: body ratings reduced by connection efficiency where the connection governs.
    @cached_property
    def burst(self) -> float:
        return burst_rating(self.geometry, self.grade.min_yield) * self.connection.burst_efficiency

    @cached_property
    def collapse(self) -> float:
        return (
            collapse_rating(self.geometry, self.grade.min_yield)
            * self.connection.collapse_efficiency
        )

    @cached_property
    def body_yield(self) -> float:
        return pipe_body_yield(self.geometry, self.grade.min_yield)

    @cached_property
    def joint_strength(self) -> float:
        return self.body_yield * self.connection.tension_efficiency

    @property
    def tension_rating(self) -> float:
        return min(self.body_yield, self.joint_strength)


def _read_csv(name: str) -> list[dict[str, str]]:
    with resources.files("casingdesign.catalog.data").joinpath(name).open(newline="") as f:
        return list(csv.DictReader(f))


class Catalog:
    def __init__(self, grades: Iterable[Grade], pipes: Iterable[PipeItem],
                 connections: Iterable[Connection]):
        self.grades = {g.name: g for g in grades}
        self.pipes = list(pipes)
        self.connections = {c.name: c for c in connections}

    @classmethod
    def default(cls) -> Catalog:
        grades = [
            Grade(r["grade"], float(r["min_yield_psi"]), float(r["max_yield_psi"]),
                  float(r["min_tensile_psi"]), r["sour_service"].lower() == "true")
            for r in _read_csv("grades.csv")
        ]
        pipes = [
            PipeItem(float(r["od_in"]), float(r["nominal_weight_lbft"]), float(r["wall_in"]),
                     float(r["drift_in"]))
            for r in _read_csv("pipe.csv")
        ]
        conns = [
            Connection(r["connection"], float(r["tension_efficiency"]),
                       float(r["burst_efficiency"]), float(r["collapse_efficiency"]),
                       r.get("notes", ""))
            for r in _read_csv("connections.csv")
        ]
        return cls(grades, pipes, conns)

    def pipe(self, od: float, nominal_weight: float) -> PipeItem:
        for p in self.pipes:
            if abs(p.od - od) < 1e-6 and abs(p.nominal_weight - nominal_weight) < 1e-6:
                return p
        raise KeyError(f"no pipe {od}in {nominal_weight}# in catalog")

    def pipes_for_od(self, od: float) -> list[PipeItem]:
        return [p for p in self.pipes if abs(p.od - od) < 1e-6]

    def spec(self, od: float, nominal_weight: float, grade: str,
             connection: str = "BTC") -> PipeSpec:
        return PipeSpec(self.pipe(od, nominal_weight), self.grades[grade],
                        self.connections[connection])

    def candidates(self, od: float, grades: Iterable[str] | None = None,
                   connection: str = "BTC", sour: bool = False) -> list[PipeSpec]:
        """All pipe x grade combinations for an OD, for the optimizer."""
        names = list(grades) if grades else list(self.grades)
        out = []
        for p in self.pipes_for_od(od):
            for g in names:
                grade = self.grades[g]
                if sour and not grade.sour_service:
                    continue
                out.append(PipeSpec(p, grade, self.connections[connection]))
        return out
