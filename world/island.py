"""The island world: objects, simple physics, avatar actions and text observations.

Physics is deliberately simple and fully deterministic:
  * every object is an axis-aligned box (x, y = footprint centre, z = bottom);
  * after any action the world is *settled*: objects fall onto the highest
    surface beneath them (terrain or another object's top), objects whose
    load sits outside their supporters' footprints topple off, and objects
    resting on terrain steeper than `slide_slope` tumble downhill;
  * thrown objects follow a ballistic arc, integrated at `dt`, and stop at
    the first terrain or object they touch.

The hidden rule (never described to the agent): throwing the rock with
force >= `rock_spawn_force` spawns a new cube where it lands.
"""

from __future__ import annotations

import copy
import math
from dataclasses import asdict, dataclass

import numpy as np

from .terrain import Terrain

EPS = 1e-6
SHAPES = {
    #        size (sx, sy, sz)   mass
    "cube": ((1.0, 1.0, 1.0), 1.0),
    "rock": ((0.7, 0.7, 0.6), 4.0),
    "ring": ((0.8, 0.8, 0.15), 0.3),
}
HAND_HEIGHT = 1.2


@dataclass
class Obj:
    id: str
    shape: str
    colour: str
    mass: float
    sx: float
    sy: float
    sz: float
    x: float
    y: float
    z: float
    held: bool = False

    @property
    def top(self) -> float:
        return self.z + self.sz

    def overlaps_xy(self, o: "Obj") -> bool:
        return abs(self.x - o.x) < (self.sx + o.sx) / 2 - EPS and abs(self.y - o.y) < (self.sy + o.sy) / 2 - EPS

    def contains_xy(self, x: float, y: float, margin: float = 0.0) -> bool:
        return abs(x - self.x) <= self.sx / 2 + margin and abs(y - self.y) <= self.sy / 2 + margin


@dataclass
class Avatar:
    x: float
    y: float
    z: float
    holding: str | None = None


class ActionError(Exception):
    """An action that could not be carried out; the message goes back to the agent."""


class World:
    def __init__(self, cfg: dict, seed: int | None = None):
        self.cfg = cfg
        self.seed = int(cfg["seed"] if seed is None else seed)
        self.rng = np.random.default_rng(self.seed)
        self.phys = cfg["physics"]
        self.av_cfg = cfg["avatar"]
        self.rule = cfg["hidden_rule"]
        self.size = float(cfg["size"])
        self.terrain = Terrain(cfg, self.rng)
        self.objects: dict[str, Obj] = {}
        self.time = 0
        self.events: list[dict] = []
        self.spawned = 0
        self._place_initial_objects(cfg)
        s = self.av_cfg["start"]
        self.avatar = Avatar(s["x"], s["y"], 0.0)
        self.settle()
        self.avatar.z = self.surface_at(self.avatar.x, self.avatar.y)
        self.events.clear()
        self._initial = copy.deepcopy((self.objects, self.avatar, self.spawned))

    # ------------------------------------------------------------------ setup
    def _random_lowland(self, taken: list[tuple[float, float]]) -> tuple[float, float]:
        sx, sy = self.terrain.spire_xy
        px, py, _ = self.terrain.peak_summit
        for _ in range(10_000):
            x, y = (float(v) for v in self.rng.uniform(6, self.size - 6, size=2))
            h = self.terrain.height(x, y)
            if not (0.5 < h < 4.0) or self.terrain.slope(x, y) > 0.3:
                continue
            if math.dist((x, y), (sx, sy)) < self.terrain.spire_radius + 2.5 or math.dist((x, y), (px, py)) < 8:
                continue
            if any(math.dist((x, y), t) < 1.6 for t in taken):
                continue
            return round(x, 2), round(y, 2)
        raise RuntimeError("could not place objects; check terrain config")

    def _add(self, oid: str, shape: str, colour: str, x: float, y: float, z: float | None = None) -> Obj:
        (sx, sy, sz), mass = SHAPES[shape]
        if z is None:
            z = self.terrain.height(x, y)
        o = Obj(oid, shape, colour, mass, sx, sy, sz, x, y, z)
        self.objects[oid] = o
        return o

    def _place_initial_objects(self, cfg: dict) -> None:
        taken: list[tuple[float, float]] = []
        colours = list(cfg["cube_colours"])
        for i in range(int(cfg["n_cubes"])):
            x, y = self._random_lowland(taken)
            taken.append((x, y))
            self._add(f"cube_{i + 1}", "cube", colours[i % len(colours)], x, y)
        for oid, shape, colour in (("rock_1", "rock", "grey"), ("ring_1", "ring", "gold")):
            x, y = self._random_lowland(taken)
            taken.append((x, y))
            self._add(oid, shape, colour, x, y)
        self.n_initial_cubes = int(cfg["n_cubes"])

    def reset(self) -> None:
        """Restore the exact initial state (start of every session)."""
        self.objects, self.avatar, self.spawned = copy.deepcopy(self._initial)
        self.time = 0
        self.events = []

    # --------------------------------------------------------------- queries
    def _free(self) -> list[Obj]:
        return [o for o in self.objects.values() if not o.held]

    def support(self, o: Obj) -> tuple[float, list[Obj]]:
        """Highest surface under `o` and the objects that provide it."""
        best = self.terrain.height(o.x, o.y)
        sup: list[Obj] = []
        for p in self._free():
            if p is o or not o.overlaps_xy(p):
                continue
            # only things whose bottom is below ours can hold us up; exact ties are
            # broken by id so two objects created at one spot end up stacked
            if p.z > o.z + EPS or (abs(p.z - o.z) <= EPS and p.id >= o.id):
                continue
            if p.top > best + 1e-4:
                best, sup = p.top, [p]
            elif abs(p.top - best) <= 1e-4:
                sup.append(p)
        return best, sup

    def resting_on(self, o: Obj) -> list[Obj]:
        return [p for p in self._free() if p is not o and p.overlaps_xy(o) and abs(p.z - o.top) < 1e-3]

    def _load_above(self, o: Obj) -> list[Obj]:
        seen: dict[str, Obj] = {}
        stack = [o]
        while stack:
            for p in self.resting_on(stack.pop()):
                if p.id not in seen:
                    seen[p.id] = p
                    stack.append(p)
        return list(seen.values())

    def surface_at(self, x: float, y: float) -> float:
        h = self.terrain.height(x, y)
        for o in self._free():
            if o.contains_xy(x, y):
                h = max(h, o.top)
        return h

    def standing_on(self) -> Obj | None:
        a = self.avatar
        for o in self._free():
            if o.contains_xy(a.x, a.y) and abs(o.top - a.z) < 1e-3:
                return o
        return None

    # --------------------------------------------------------------- physics
    def settle(self) -> None:
        slide_slope = float(self.phys["slide_slope"])
        slide_step = float(self.phys["slide_step"])
        for _ in range(int(self.phys["max_settle_iters"])):
            moved = False
            for o in sorted(self._free(), key=lambda q: (q.z, q.id)):
                sup_h, sups = self.support(o)
                if abs(o.z - sup_h) > 1e-6:
                    if o.z > sup_h + 0.05:
                        self.events.append({"type": "fell", "id": o.id, "from": round(o.z, 2), "to": round(sup_h, 2)})
                    o.z = sup_h
                    moved = True
                    continue
                if sups:
                    group = [o] + self._load_above(o)
                    m = sum(g.mass for g in group)
                    cx = sum(g.mass * g.x for g in group) / m
                    cy = sum(g.mass * g.y for g in group) / m
                    if not any(s.contains_xy(cx, cy) for s in sups):
                        bx = sum(s.x for s in sups) / len(sups)
                        by = sum(s.y for s in sups) / len(sups)
                        dx, dy = cx - bx, cy - by
                        n = math.hypot(dx, dy) or 1.0
                        shift = max(o.sx, o.sy) * 0.75
                        o.x = self._clamp(o.x + dx / n * shift)
                        o.y = self._clamp(o.y + dy / n * shift)
                        self.events.append({"type": "toppled", "id": o.id, "off": [s.id for s in sups]})
                        moved = True
                else:
                    gx, gy = self.terrain.gradient(o.x, o.y)
                    g = math.hypot(gx, gy)
                    if g > slide_slope:
                        o.x = self._clamp(o.x - gx / g * slide_step)
                        o.y = self._clamp(o.y - gy / g * slide_step)
                        self.events.append({"type": "tumbled", "id": o.id})
                        moved = True
            if not moved:
                break
        self._collapse_events()

    def _collapse_events(self) -> None:
        """Merge runs of consecutive tumble events per object so logs stay small."""
        out: list[dict] = []
        for e in self.events:
            if e["type"] == "tumbled" and out and out[-1]["type"] == "tumbled" and out[-1]["id"] == e["id"]:
                out[-1]["n"] = out[-1].get("n", 1) + 1
            else:
                out.append(e)
        self.events = out

    def _clamp(self, v: float) -> float:
        return min(max(v, 0.0), self.size)

    def _fly(self, o: Obj, vel: tuple[float, float, float]) -> tuple[float, float, float]:
        """Integrate a ballistic arc. Returns the impact point (x, y, z)."""
        g, dt = float(self.phys["gravity"]), float(self.phys["dt"])
        vx, vy, vz = vel
        for _ in range(20_000):
            px, py, pz = o.x, o.y, o.z
            vz -= g * dt
            o.x, o.y, o.z = o.x + vx * dt, o.y + vy * dt, o.z + vz * dt
            if not (0 <= o.x <= self.size and 0 <= o.y <= self.size):
                o.x, o.y = self._clamp(o.x), self._clamp(o.y)
                break
            if o.z <= self.terrain.height(o.x, o.y):
                if self.terrain.height(o.x, o.y) > pz + 0.3:  # struck a cliff face: drop back
                    o.x, o.y = px, py
                break
            hit = None
            for p in self._free():
                if p is o or not o.overlaps_xy(p):
                    continue
                if o.z < p.top and o.top > p.z:
                    hit = p
                    break
            if hit is not None:
                if pz < hit.top - 1e-3:  # came in from the side: stop beside it
                    o.x, o.y = px, py
                break
        o.z = max(o.z, self.terrain.height(o.x, o.y))
        return o.x, o.y, o.z

    # --------------------------------------------------------------- actions
    def _obj(self, oid: str) -> Obj:
        if oid not in self.objects:
            raise ActionError(f"There is no object called '{oid}'.")
        return self.objects[oid]

    def _sync_held(self) -> None:
        a = self.avatar
        if a.holding:
            o = self.objects[a.holding]
            o.x, o.y, o.z = a.x, a.y, a.z + HAND_HEIGHT

    def _after(self) -> None:
        self.settle()
        self.avatar.z = self.surface_at(self.avatar.x, self.avatar.y)
        self._sync_held()
        self.time += 1

    def move(self, dx: float, dy: float) -> str:
        a = self.avatar
        dist = math.hypot(dx, dy)
        if dist < EPS:
            self._after()
            return "You stay where you are."
        mx = float(self.av_cfg["max_move"])
        if dist > mx:
            dx, dy, dist = dx * mx / dist, dy * mx / dist, mx
        n = max(1, math.ceil(dist / 0.2))
        step_up = float(self.av_cfg["step_up"])
        wade = float(self.cfg["sea_level"]) - float(self.cfg["max_wade_depth"])
        msg = None
        travelled = 0.0
        for _ in range(n):
            nx, ny = a.x + dx / n, a.y + dy / n
            if not (0 <= nx <= self.size and 0 <= ny <= self.size):
                msg = "You reach the edge of the world."
                break
            if self.terrain.height(nx, ny) < wade:
                msg = "The water is too deep to go further."
                break
            h = self.surface_at(nx, ny)
            if h - a.z > step_up:
                msg = "Something too steep blocks your way."
                break
            a.x, a.y, a.z = nx, ny, h
            travelled += dist / n
        self._after()
        return f"You moved {travelled:.1f} m." + (f" {msg}" if msg else "")

    def jump(self, dx: float = 0.0, dy: float = 0.0) -> str:
        a = self.avatar
        dist = math.hypot(dx, dy)
        jd = float(self.av_cfg["jump_distance"])
        if dist > jd:
            dx, dy, dist = dx * jd / dist, dy * jd / dist, jd
        if dist < EPS:
            self._after()
            return "You jump in place and land again."
        nx, ny = self._clamp(a.x + dx), self._clamp(a.y + dy)
        h = self.surface_at(nx, ny)
        wade = float(self.cfg["sea_level"]) - float(self.cfg["max_wade_depth"])
        if h - a.z > float(self.av_cfg["jump_height"]) or self.terrain.height(nx, ny) < wade:
            self._after()
            return "You jump, but can't make it there, and land back where you started."
        a.x, a.y, a.z = nx, ny, h
        self._after()
        return f"You jump and land at height {a.z:.1f}."

    def pick_up(self, oid: str) -> str:
        a = self.avatar
        o = self._obj(oid)
        if a.holding:
            raise ActionError(f"You are already holding {a.holding}.")
        if math.hypot(o.x - a.x, o.y - a.y) > float(self.av_cfg["reach"]):
            raise ActionError(f"{oid} is out of reach.")
        if not (a.z - 1.5 <= o.z <= a.z + float(self.av_cfg["reach_up"])):
            raise ActionError(f"{oid} is too far above or below you.")
        if self.standing_on() is o:
            raise ActionError(f"You are standing on {oid}.")
        if self.resting_on(o):
            raise ActionError(f"Something is resting on top of {oid}.")
        o.held = True
        a.holding = oid
        self._after()
        return f"You pick up {oid}."

    def place(self, oid: str, x: float, y: float, z: float) -> str:
        a = self.avatar
        o = self._obj(oid)
        if a.holding != oid:
            raise ActionError(f"You are not holding {oid}.")
        if math.hypot(x - a.x, y - a.y) > float(self.av_cfg["reach"]):
            raise ActionError("That spot is out of reach.")
        if not (0 <= x <= self.size and 0 <= y <= self.size):
            raise ActionError("That spot is outside the world.")
        if z > a.z + float(self.av_cfg["reach_up"]):
            raise ActionError("You can't reach that high.")
        o.held = False
        a.holding = None
        o.x, o.y = float(x), float(y)
        o.z = max(float(z), self.support(o)[0])
        # you can't wedge an object into a gap under something else: it goes on top
        blocking = [p.top for p in self._free() if p is not o and p.overlaps_xy(o) and p.z < o.top and p.top > o.z]
        if blocking:
            o.z = max(blocking)
        self._after()
        return f"You set down {oid}; it rests at ({o.x:.1f}, {o.y:.1f}, {o.z:.1f})."

    def throw(self, oid: str, direction: list[float], force: float) -> str:
        a = self.avatar
        o = self._obj(oid)
        if a.holding != oid:
            raise ActionError(f"You are not holding {oid}.")
        if len(direction) == 2:
            direction = [direction[0], direction[1], 0.0]
        dx, dy, dz = (float(v) for v in direction[:3])
        n = math.sqrt(dx * dx + dy * dy + dz * dz)
        if n < EPS:
            raise ActionError("Throw direction must be non-zero.")
        force = min(max(float(force), 0.0), float(self.av_cfg["max_force"]))
        speed = force / math.sqrt(o.mass)
        o.held = False
        a.holding = None
        o.x, o.y, o.z = a.x, a.y, a.z + HAND_HEIGHT
        ix, iy, iz = self._fly(o, (dx / n * speed, dy / n * speed, dz / n * speed))
        self.events.append({"type": "landed", "id": oid, "at": [round(ix, 2), round(iy, 2), round(iz, 2)], "force": force})
        if o.shape == "rock" and force >= float(self.rule["rock_spawn_force"]) and self.spawned < int(self.rule["max_spawned"]):
            self._spawn_cube(ix, iy, iz, dx, dy)
        self._after()
        return f"You throw {oid}. It lands near ({o.x:.1f}, {o.y:.1f}, {o.z:.1f})."

    def _spawn_cube(self, x: float, y: float, z: float, dx: float, dy: float) -> None:
        # Spawned just beyond the rock along the throw's horizontal direction, so it
        # doesn't sit on top of the rock and pin it.
        h = math.hypot(dx, dy)
        ux, uy = (dx / h, dy / h) if h > EPS else (1.0, 0.0)
        off = 0.9
        colours = list(self.cfg["cube_colours"])
        idx = self.n_initial_cubes + self.spawned + 1
        while f"cube_{idx}" in self.objects:
            idx += 1
        oid = f"cube_{idx}"
        self._add(oid, "cube", colours[(idx - 1) % len(colours)], self._clamp(x + ux * off), self._clamp(y + uy * off), z)
        self.spawned += 1
        self.events.append({"type": "spawn", "id": oid, "at": [round(x, 2), round(y, 2), round(z, 2)], "hidden_rule": True})

    def wait(self) -> str:
        self._after()
        return "You wait a moment."

    # ------------------------------------------------------------ observation
    def observe(self) -> str:
        a = self.avatar
        held = a.holding or "nothing"
        lines = [f"You are at ({a.x:.1f}, {a.y:.1f}, {a.z:.1f}), holding {held}.", "Objects (id, colour shape, x y z):"]
        for o in sorted(self.objects.values(), key=lambda q: _natural(q.id)):
            where = "in your hands" if o.held else f"{o.x:.1f} {o.y:.1f} {o.z:.1f}"
            lines.append(f"{o.id}: {o.colour} {o.shape} @ {where}")
        return "\n".join(lines)

    def landmarks_text(self) -> str:
        px, py, pz = self.terrain.peak_summit
        sx, sy, sz = self.terrain.spire_summit
        return (
            "The island is hilly. Two high points stand out: the Peak, a tall rounded hill whose summit is near "
            f"({px:.0f}, {py:.0f}, {pz:.0f}), and the Spire, a steep-sided flat-topped rock near ({sx:.0f}, {sy:.0f}, {sz:.0f})."
        )

    def drain_events(self) -> list[dict]:
        ev, self.events = self.events, []
        return ev

    def state(self) -> dict:
        return {
            "time": self.time,
            "avatar": asdict(self.avatar),
            "objects": [asdict(o) for o in self.objects.values()],
            "spawned": self.spawned,
        }


def _natural(oid: str) -> tuple:
    head, _, num = oid.rpartition("_")
    return (head, int(num)) if num.isdigit() else (oid, 0)
