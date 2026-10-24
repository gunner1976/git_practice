"""The island's planet: a small sphere, so its shape can be measured from the island.

Physics on the island stays flat (over 60 m the curvature of a 2 km planet drops the
ground by under a metre, too little to matter for walking or throwing). What the sphere
changes is what an observer sees:
  * the sea horizon sits below eye level by the dip angle acos(R / (R + h)), so it sinks
    further the higher you stand;
  * the sun's elevation and azimuth depend on where on the sphere you stand, so at the same
    moment two places on the island see it at slightly different angles (Eratosthenes);
  * the planet turns, and each day-session runs from sunrise to sunset.
Positions on the island map to latitude/longitude around the island's centre.
"""

from __future__ import annotations

import math


class Planet:
    def __init__(self, cfg: dict, centre: tuple[float, float]):
        self.radius = float(cfg.get("radius", 2000.0))
        self.lat0 = math.radians(float(cfg.get("latitude", 20.0)))
        self.declination = math.radians(float(cfg.get("sun_declination", 0.0)))
        self.eye_height = float(cfg.get("eye_height", 1.6))
        self.cx, self.cy = centre

    def latlon(self, x: float, y: float) -> tuple[float, float]:
        """(latitude, longitude offset) in radians of an island point; +y is north, +x east."""
        lat = self.lat0 + (y - self.cy) / self.radius
        lon = (x - self.cx) / (self.radius * math.cos(self.lat0))
        return lat, lon

    def sun(self, x: float, y: float, day_fraction: float) -> tuple[float, float]:
        """Sun (azimuth, elevation) in degrees at (x, y), `day_fraction` of the way from sunrise
        (0) to sunset (1) at the island's centre. Azimuth: 0 = north, 90 = east."""
        lat, lon = self.latlon(x, y)
        hour = math.radians(-90.0 + 180.0 * day_fraction) + lon
        d = self.declination
        sin_el = math.sin(lat) * math.sin(d) + math.cos(lat) * math.cos(d) * math.cos(hour)
        el = math.asin(max(-1.0, min(1.0, sin_el)))
        az = math.atan2(-math.cos(d) * math.sin(hour), math.sin(d) * math.cos(lat) - math.cos(d) * math.sin(lat) * math.cos(hour))
        return (math.degrees(az) % 360.0, math.degrees(el))

    def horizon_dip(self, ground_height: float) -> float:
        """Angle (degrees) the sea horizon sits below eye level for an observer standing on
        ground `ground_height` metres above sea level."""
        h = max(0.0, ground_height) + self.eye_height
        return math.degrees(math.acos(self.radius / (self.radius + h)))
