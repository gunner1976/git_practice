"""Heightmap for the island: a low radial island, a few gentle hills, the Peak
(a tall smooth hill you can walk up) and the Spire (a flat-topped mesa with a
cliff you cannot walk up and cannot clear with a single jump)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def _smoothstep(v: float) -> float:
    v = min(max(v, 0.0), 1.0)
    return v * v * (3 - 2 * v)


@dataclass
class Hill:
    x: float
    y: float
    amp: float
    sigma: float

    def __call__(self, x: float, y: float) -> float:
        d2 = (x - self.x) ** 2 + (y - self.y) ** 2
        return self.amp * math.exp(-d2 / (2 * self.sigma**2))


class Terrain:
    CLIFF_WIDTH = 0.3  # horizontal width of the Spire's cliff face (metres)

    def __init__(self, cfg: dict, rng: np.random.Generator):
        self.size = float(cfg["size"])
        self.cx = self.cy = self.size / 2
        self.island_r = self.size * 0.44
        shape = cfg.get("island_shape") or {}
        # optional irregular outline: the island's radius varies with direction (lobes), bays cut
        # into it, and the seabed can drop off faster beyond the shore
        self.lobes = [tuple(map(float, l)) for l in shape.get("lobes", [])]  # (k, amplitude, phase_deg)
        self.bays = [(math.radians(float(b["angle"])), float(b["depth"]), math.radians(float(b["width"]))) for b in shape.get("bays", [])]
        self.seabed_steepness = float(shape.get("seabed_steepness", 1.0))
        p, s = cfg["peak"], cfg["spire"]
        self.peak = Hill(p["x"], p["y"], p["height"], p["sigma"])
        self.spire_xy = (float(s["x"]), float(s["y"]))
        self.spire_radius = float(s["radius"])
        self.hills: list[Hill] = []
        tries = 0
        while len(self.hills) < int(cfg.get("hills", 0)) and tries < 500:
            tries += 1
            x, y = rng.uniform(8, self.size - 8, size=2)
            if math.dist((x, y), (p["x"], p["y"])) < 12 or math.dist((x, y), self.spire_xy) < 9:
                continue
            if math.dist((x, y), (self.cx, self.cy)) > self.radius_at(math.atan2(y - self.cy, x - self.cx)) * 0.8:
                continue
            self.hills.append(Hill(float(x), float(y), float(rng.uniform(0.8, 2.2)), float(rng.uniform(3, 5))))
        self.spire_top = self._ground(*self.spire_xy) + float(s["height"])

    def radius_at(self, theta: float) -> float:
        """The island's base radius in direction theta (radians, 0 = +x/east, counter-clockwise)."""
        f = 1.0 + sum(a * math.cos(k * theta + math.radians(ph)) for k, a, ph in self.lobes)
        for ang, depth, width in self.bays:
            d = math.atan2(math.sin(theta - ang), math.cos(theta - ang))
            f -= depth * math.exp(-0.5 * (d / width) ** 2)
        return self.island_r * max(0.15, f)

    def _ground(self, x: float, y: float) -> float:
        """Terrain without the Spire."""
        r = math.hypot(x - self.cx, y - self.cy)
        big_r = self.radius_at(math.atan2(y - self.cy, x - self.cx)) if (self.lobes or self.bays) else self.island_r
        h = 2.5 * (1 - (r / big_r) ** 2)
        if h < 0:
            h *= self.seabed_steepness
        h += self.peak(x, y)
        for hill in self.hills:
            h += hill(x, y)
        return h

    def spire_weight(self, x: float, y: float) -> float:
        d = math.dist((x, y), self.spire_xy)
        return _smoothstep((self.spire_radius - d) / self.CLIFF_WIDTH + 0.5)

    def height(self, x: float, y: float) -> float:
        g = self._ground(x, y)
        w = self.spire_weight(x, y)
        return g + w * max(0.0, self.spire_top - g)

    def gradient(self, x: float, y: float, h: float = 0.05) -> tuple[float, float]:
        gx = (self.height(x + h, y) - self.height(x - h, y)) / (2 * h)
        gy = (self.height(x, y + h) - self.height(x, y - h)) / (2 * h)
        return gx, gy

    def slope(self, x: float, y: float) -> float:
        return math.hypot(*self.gradient(x, y))

    @property
    def peak_summit(self) -> tuple[float, float, float]:
        return (self.peak.x, self.peak.y, self.height(self.peak.x, self.peak.y))

    @property
    def spire_summit(self) -> tuple[float, float, float]:
        return (*self.spire_xy, self.spire_top)
