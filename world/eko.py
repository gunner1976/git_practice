"""EKO: the agents' planet. We know its specifics (planets/EKO.md); the agents don't.

Everything observable follows from one set of parameters:
  * EKO's radius and mass give surface gravity g = GM/R^2, used by the island's physics;
  * EKO turns once per solar day and circles its star once per year, on a tilted axis;
  * the moon orbits EKO by Kepler's third law (period from EKO's mass and the moon's distance),
    on an orbit slightly inclined to EKO's orbit, so it shows phases and, near its nodes,
    lunar eclipses (EKO's shadow on the moon) and solar eclipses (the moon in front of the star);
  * fixed stars turn about the celestial pole, which stands at the observer's latitude.

Positions are computed in an inertial equatorial frame centred on EKO: the star's and the
moon's directions from the orbital elements, the observer on EKO's surface from latitude and
the local sidereal angle, and altitude/azimuth in the observer's local frame. The moon is
seen topocentrically (its parallax matters for solar eclipses); the star is effectively at
infinity. A session spans one EKO day, sunrise to sunrise, compressed into the session's
simulated clock; consecutive sessions are consecutive days.
"""

from __future__ import annotations

import math

import numpy as np

G = 6.674e-11


def _unit(ra: float, dec: float) -> np.ndarray:
    return np.array([math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec)])


def _ecl_to_eq(lon: float, lat: float, eps: float) -> np.ndarray:
    v = np.array([math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)])
    c, s = math.cos(eps), math.sin(eps)
    return np.array([v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]])


def _overlap(r1: float, r2: float, d: float) -> float:
    """Area of overlap of two circles (radii r1, r2, centre distance d)."""
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2
    a = r1 * r1 * math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1))
    b = r2 * r2 * math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2))
    c = 0.5 * math.sqrt(max(0.0, (-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2)))
    return a + b - c


class Eko:
    def __init__(self, cfg: dict, island_centre: tuple[float, float]):
        self.cfg = cfg
        self.R = float(cfg["radius_km"]) * 1000.0
        self.M = float(cfg["mass_kg"])
        self.g = G * self.M / self.R**2
        self.day = float(cfg["solar_day_hours"]) * 3600.0          # noon to noon
        self.year = float(cfg["year_days"]) * self.day
        self.tilt = math.radians(float(cfg["axial_tilt_deg"]))
        self.sidereal_day = self.day * self.year / (self.year + self.day)
        self.lat0 = math.radians(float(cfg["island_latitude_deg"]))
        self.lon0 = math.radians(float(cfg.get("island_longitude_deg", 0.0)))
        self.cx, self.cy = island_centre
        self.eye = float(cfg.get("eye_height_m", 1.6))
        # the star
        self.sun_ang_r = math.radians(float(cfg["star_apparent_diameter_deg"])) / 2
        # the moon: Kepler's third law around EKO
        m = cfg["moon"]
        self.a = float(m["distance_km"]) * 1000.0
        self.Rm = float(m["radius_km"]) * 1000.0
        self.month = 2 * math.pi * math.sqrt(self.a**3 / (G * self.M))     # sidereal
        self.synodic = 1.0 / (1.0 / self.month - 1.0 / self.year)
        self.incl = math.radians(float(m["inclination_deg"]))
        # epoch: tau = 0 is local midnight at the island; first full moon (on a node, so a total
        # lunar eclipse) at the midnight of the configured day
        self.sun_lon0 = math.radians(float(cfg.get("star_longitude_at_epoch_deg", 0.0)))
        tf = (int(m["first_full_moon_day"]) - 1) * self.day + self.day  # that day's midnight
        sun_at_full = self.sun_lon0 + 2 * math.pi * tf / self.year
        self.node = sun_at_full + math.pi + math.radians(float(m.get("node_offset_deg", 0.0)))
        self.moon_lon0 = sun_at_full + math.pi - 2 * math.pi * tf / self.month
        # sidereal angle chosen so the island has local midnight at tau = 0
        self.theta0 = math.pi + self._sun_ra(0.0)
        rng = np.random.default_rng(int(cfg.get("star_seed", 23)))
        n = int(cfg.get("n_stars", 60))
        self.stars = [(f"star_{i + 1:02d}", float(rng.uniform(0, 2 * math.pi)), float(math.asin(rng.uniform(-1, 1))), float(rng.uniform(0, 6)))
                      for i in range(n)]  # (name, RA, Dec, magnitude)

    # ------------------------------------------------------------ time
    def session_tau(self, session: int, clock: float, session_seconds: float) -> float:
        """EKO time (s since epoch) for a moment in a session: each session runs from the
        island's dawn to the next dawn of day `session`."""
        dawn = (session - 1) * self.day + self.day / 4
        return dawn + self.day * min(1.0, clock / max(1e-9, session_seconds))

    # ------------------------------------------------------------ bodies
    def _sun_lon(self, tau: float) -> float:
        return self.sun_lon0 + 2 * math.pi * tau / self.year

    def _sun_dir(self, tau: float) -> np.ndarray:
        return _ecl_to_eq(self._sun_lon(tau), 0.0, self.tilt)

    def _sun_ra(self, tau: float) -> float:
        v = self._sun_dir(tau)
        return math.atan2(v[1], v[0])

    def _moon_vec(self, tau: float) -> np.ndarray:
        lon = self.moon_lon0 + 2 * math.pi * tau / self.month
        lat = math.asin(math.sin(self.incl) * math.sin(lon - self.node))
        return self.a * _ecl_to_eq(lon, lat, self.tilt)

    def _observer(self, x: float, y: float, tau: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        lat = self.lat0 + (y - self.cy) / self.R
        lon = self.lon0 + (x - self.cx) / (self.R * math.cos(self.lat0))
        th = self.theta0 + 2 * math.pi * tau / self.sidereal_day + lon
        up = np.array([math.cos(lat) * math.cos(th), math.cos(lat) * math.sin(th), math.sin(lat)])
        east = np.array([-math.sin(th), math.cos(th), 0.0])
        north = np.array([-math.sin(lat) * math.cos(th), -math.sin(lat) * math.sin(th), math.cos(lat)])
        return up * self.R, up, east, north

    @staticmethod
    def _altaz(d: np.ndarray, up, east, north) -> tuple[float, float]:
        d = d / np.linalg.norm(d)
        return math.degrees(math.atan2(d @ east, d @ north)) % 360.0, math.degrees(math.asin(max(-1.0, min(1.0, d @ up))))

    def lunar_eclipse(self, tau: float) -> tuple[float, float]:
        """(fraction of the moon's disc in EKO's full shadow, shadow-edge radius / moon radius)."""
        anti = -self._sun_dir(tau)
        mv = self._moon_vec(tau)
        sep = math.acos(max(-1.0, min(1.0, (mv / np.linalg.norm(mv)) @ anti)))
        umbra = (self.R - self.a * math.tan(self.sun_ang_r)) / self.a  # angular radius at the moon's distance
        moon = self.Rm / self.a
        return _overlap(moon, umbra, sep) / (math.pi * moon * moon), umbra / moon

    def sky(self, x: float, y: float, ground: float, tau: float) -> dict:
        """What an observer standing at island point (x, y), on ground `ground` m above sea level,
        sees at EKO time tau."""
        pos, up, east, north = self._observer(x, y, tau)
        sun = self._sun_dir(tau)
        s_az, s_el = self._altaz(sun, up, east, north)
        mv = self._moon_vec(tau)
        topo = mv - pos
        m_az, m_el = self._altaz(topo, up, east, north)
        m_r = self.Rm / np.linalg.norm(topo)
        out: dict = {}
        if s_el > -0.5:
            sun_obs = {"azimuth_deg": round(s_az, 2), "elevation_deg": round(s_el, 2), "apparent_diameter_deg": round(math.degrees(2 * self.sun_ang_r), 3)}
            sep = math.acos(max(-1.0, min(1.0, (topo / np.linalg.norm(topo)) @ sun)))
            covered = _overlap(self.sun_ang_r, m_r, sep) / (math.pi * self.sun_ang_r**2)
            if covered > 0.001:
                sun_obs["covered_fraction"] = round(min(1.0, covered), 3)
            out["sun"] = sun_obs
        else:
            out["sun"] = "below the horizon"
        state = "day" if s_el > 0 else "twilight" if s_el > -12 else "night"
        out["daylight"] = state
        if m_el > -0.5:
            elong = math.acos(max(-1.0, min(1.0, (mv / np.linalg.norm(mv)) @ sun)))
            moon = {"azimuth_deg": round(m_az, 2), "elevation_deg": round(m_el, 2), "apparent_diameter_deg": round(math.degrees(2 * m_r), 3),
                    "lit_fraction": round((1 - math.cos(elong)) / 2, 3)}
            dark, edge = self.lunar_eclipse(tau)
            if dark > 0.001:
                moon["eclipse"] = {"darkened_fraction": round(min(1.0, dark), 3),
                                   "shadow_edge": "a curved arc" if dark < 0.999 else "the whole disc is in shadow",
                                   "shadow_edge_radius_in_moon_radii": round(edge, 2)}
            out["moon"] = moon
        else:
            out["moon"] = "below the horizon"
        if s_el < -12:
            stars = []
            for name, ra, dec, mag in self.stars:
                az, el = self._altaz(_unit(ra, dec), up, east, north)
                if el > 5:
                    stars.append((mag, {"name": name, "azimuth_deg": round(az, 1), "elevation_deg": round(el, 1)}))
            out["brightest_stars"] = [s for _, s in sorted(stars, key=lambda t: t[0])[:10]]
        h = max(0.0, ground) + self.eye
        out["sea_horizon"] = {"angle_below_eye_level_deg": round(math.degrees(math.acos(self.R / (self.R + h))), 3)}
        return out

    def facts(self) -> dict:
        """Derived quantities for the spec sheet and for scoring answers."""
        return {
            "surface_gravity_m_s2": self.g,
            "circumference_km": 2 * math.pi * self.R / 1000,
            "escape_velocity_km_s": math.sqrt(2 * G * self.M / self.R) / 1000,
            "mean_density_kg_m3": self.M / (4 / 3 * math.pi * self.R**3),
            "sidereal_day_hours": self.sidereal_day / 3600,
            "moon_sidereal_month_days": self.month / self.day,
            "moon_synodic_month_days": self.synodic / self.day,
            "moon_apparent_diameter_deg": math.degrees(2 * self.Rm / self.a),
            "umbra_radius_in_moon_radii": self.lunar_eclipse(0.0)[1],
        }
