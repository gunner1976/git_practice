"""The island with the paper's agent interface (Cloos et al. 2026, App. A.6-A.7 and B).

Same terrain, objects and settling physics as `World`, but:
  * actions are the paper's six: MoveTo(position), Jump, Stop, Pickup(position),
    Place(position, rotation), Throw(direction, speed), plus Observe;
  * positions are reported the paper's way: [x, y, z] with y up, origin at the
    island centre, entities named Block_N, Rock, Ring, ImpactBlock_N, Peak, Spire;
  * every action returns a short JSON result with a `lastActionResult` code taken
    from the paper's list; MoveTo just reports where you ended up;
  * Pickup works within 6 m, Place within 7 m, Throw speed is clamped to 10 m/s and
    gets an upward impulse;
  * a jump leaves you in the air until your next action: MoveTo then lets you land
    on ledges up to the jump height, and Throw inherits part of the jump's velocity
    (the paper's agents discovered this; it was not designed);
  * a hard rock impact (speed and energy thresholds) spawns up to eight small
    ImpactBlocks around the impact point;
  * objects that come to rest in the sea are lost until the next reset.

Internally the world keeps its own frame (x, y on the ground, z up, origin at a
corner), so replays and scoring work unchanged.
"""

from __future__ import annotations

import json
import math

from .island import EPS, HAND_HEIGHT, SHAPES, ActionError, World

SHAPES.setdefault("impact", ((0.4, 0.4, 0.4), 0.3))

RGB = {
    "red": [0.83, 0.23, 0.18], "orange": [0.94, 0.54, 0.11], "yellow": [0.95, 0.81, 0.11], "green": [0.25, 0.64, 0.30],
    "blue": [0.18, 0.44, 0.84], "purple": [0.48, 0.27, 0.77], "pink": [0.94, 0.50, 0.71], "white": [0.96, 0.96, 0.94],
    "black": [0.13, 0.13, 0.14], "grey": [0.55, 0.57, 0.59], "brown": [0.54, 0.35, 0.17], "teal": [0.08, 0.61, 0.61],
    "gold": [0.85, 0.65, 0.13], "stone": [0.62, 0.58, 0.52],
}


def _r(v: float) -> float:
    return round(float(v), 2)


class PaperWorld(World):
    def __init__(self, cfg: dict, seed: int | None = None):
        super().__init__(cfg, seed)
        self.pcfg = cfg["paper"]
        self.half = self.size / 2
        self.air: dict | None = None  # set by a jump, cleared by the next action
        self.last_result = "Ready"
        self.impacts = 0
        self.lost: list[str] = []

    def reset(self) -> None:
        super().reset()
        self.air = None
        self.last_result = "Ready"
        self.impacts = 0
        self.lost = []

    # ------------------------------------------------------------ frames
    def to_paper(self, x: float, y: float, z: float) -> list[float]:
        return [_r(x - self.half), _r(z), _r(y - self.half)]

    def from_paper(self, p) -> tuple[float, float, float]:
        if not isinstance(p, (list, tuple)) or len(p) < 3:
            raise ValueError("position must be [x, y, z]")
        x, up, z = (float(v) for v in p[:3])
        return x + self.half, z + self.half, up

    def name_of(self, o) -> str:
        if o.shape == "cube":
            return "Block_" + o.id.split("_")[1]
        if o.shape == "impact":
            return "ImpactBlock_" + o.id.split("_")[1]
        return {"rock": "Rock", "ring": "Ring", "egg": "Egg"}.get(o.shape, o.id)

    def _by_name(self, name: str):
        for o in self.objects.values():
            if self.name_of(o) == name:
                return o
        return None

    # ------------------------------------------------------------ results
    def _player(self) -> dict:
        a = self.avatar
        held = self.objects.get(a.holding) if a.holding else None
        return {"position": self.to_paper(a.x, a.y, a.z), "holding": self.name_of(held) if held else None,
                "airborne": self.air is not None, "lastActionResult": self.last_result}

    def _result(self, code: str) -> str:
        self.last_result = code
        return json.dumps({"tick": self.time, "lastActionResult": code, "player": self._player()})

    def observe_json(self, extra: dict | None = None) -> str:
        ents = []
        t = self.terrain
        px, py, pz = t.peak_summit
        ents.append({"name": "Peak", "entity_type": "terrain", "position": self.to_paper(px, py, pz / 2), "size": [_r(4 * t.peak.sigma), _r(pz), _r(4 * t.peak.sigma)],
                     "shape": "hill", "color": [0.38, 0.6, 0.31], "anchored": True})
        sx, sy, top = t.spire_summit
        base = t._ground(sx + t.spire_radius + 1, sy)
        ents.append({"name": "Spire", "entity_type": "terrain", "position": self.to_paper(sx, sy, (top + base) / 2),
                     "size": [_r(2 * t.spire_radius), _r(top - base), _r(2 * t.spire_radius)], "shape": "mesa", "color": [0.38, 0.35, 0.33], "anchored": True})
        for i, h in enumerate(t.hills, 1):
            hz = t.height(h.x, h.y)
            ents.append({"name": f"Hill_{i}", "entity_type": "terrain", "position": self.to_paper(h.x, h.y, hz / 2), "size": [_r(4 * h.sigma), _r(hz), _r(4 * h.sigma)],
                         "shape": "hill", "color": [0.45, 0.66, 0.36], "anchored": True})
        for o in sorted(self.objects.values(), key=lambda q: (q.shape != "cube", q.id)):
            if o.held:
                continue
            ents.append({"name": self.name_of(o), "entity_type": "part", "position": self.to_paper(o.x, o.y, o.z + o.sz / 2), "size": [_r(o.sx), _r(o.sz), _r(o.sy)],
                         "shape": "block" if o.shape in ("cube", "impact") else o.shape, "color": RGB.get(o.colour, [0.5, 0.5, 0.5]), "anchored": False})
        obs = {"tick": self.time, "game_status": "active", **(extra or {}), "player": self._player(), "other_players": [], "world": {"entities": ents}}
        return json.dumps(obs, separators=(",", ":"))

    # ------------------------------------------------------------ helpers
    def _land(self) -> None:
        """Come down from a jump that wasn't followed by a move or a throw."""
        self.air = None
        a = self.avatar
        a.z = self.surface_at(a.x, a.y)

    def _walk(self, tx: float, ty: float, climb: float, budget: float) -> float:
        """Walk straight toward (tx, ty) for at most `budget` metres, rising at most
        `climb` per 0.2 m sub-step. Returns the distance covered."""
        a = self.avatar
        wade = float(self.cfg["sea_level"]) - float(self.cfg["max_wade_depth"])
        dx, dy = tx - a.x, ty - a.y
        dist = min(math.hypot(dx, dy), budget)
        if dist < EPS:
            return 0.0
        ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
        n = max(1, math.ceil(dist / 0.2))
        gone = 0.0
        for _ in range(n):
            st = dist / n
            nx, ny = a.x + ux * st, a.y + uy * st
            if not (0 <= nx <= self.size and 0 <= ny <= self.size) or self.terrain.height(nx, ny) < wade:
                break
            h = self.surface_at(nx, ny)
            if h - a.z > climb:
                break
            a.x, a.y, a.z = nx, ny, h
            gone += st
        return gone

    # ------------------------------------------------------------ actions
    def move_to(self, position) -> str:
        tx, ty, _ = self.from_paper(position)
        a = self.avatar
        jump_h = float(self.av_cfg["jump_height"])
        step_up = float(self.av_cfg["step_up"])
        if self.air is not None:  # jump-move combo: the first stretch is in the air
            base_z = self.air["z0"]
            a.z = base_z + jump_h
            self._walk_air(tx, ty, base_z + jump_h, float(self.av_cfg["jump_distance"]))
            self.air = None
            a.z = self.surface_at(a.x, a.y)
        self._walk(tx, ty, step_up, float(self.pcfg["max_move_distance"]))
        self._after("move")
        return self._result("Ready")

    def _walk_air(self, tx, ty, ceiling, budget) -> None:
        """Horizontal travel while airborne: anything whose surface is below `ceiling`
        can be landed on; higher things stop you."""
        a = self.avatar
        dx, dy = tx - a.x, ty - a.y
        d = math.hypot(dx, dy)
        if d < EPS:
            return
        dist = min(d, budget)
        n = max(1, math.ceil(dist / 0.1))
        for _ in range(n):
            nx, ny = a.x + dx / d * dist / n, a.y + dy / d * dist / n
            if not (0 <= nx <= self.size and 0 <= ny <= self.size) or self.surface_at(nx, ny) > ceiling:
                break
            a.x, a.y = nx, ny

    def jump(self, *_args, **_kw) -> str:
        if self.air is not None:
            self._land()
        a = self.avatar
        self.air = {"z0": a.z, "vz": math.sqrt(2 * float(self.phys["gravity"]) * float(self.av_cfg["jump_height"]))}
        self.time += 1
        return self._result("Ready")

    def stop(self) -> str:
        if self.air is not None:
            self._land()
        self._after("stop")
        return self._result("Ready")

    def pickup(self, position) -> str:
        if self.air is not None:
            self._land()
        a = self.avatar
        if a.holding:
            return self._fail("PickupFailed:AlreadyHolding")
        if position is None:
            return self._fail("PickupFailed:MissingPosition")
        x, y, up = self.from_paper(position)
        best, bd = None, 1e9
        for o in self._free():
            d = math.dist((o.x, o.y, o.z + o.sz / 2), (x, y, up))
            if d < bd:
                best, bd = o, d
        if best is None or bd > float(self.pcfg["pickup_snap"]):
            return self._fail("PickupFailed:NoBlock")
        o = best
        if math.dist((o.x, o.y, o.z), (a.x, a.y, a.z)) > float(self.pcfg["pickup_range"]):
            return self._fail("PickupFailed:OutOfRange")
        if self.standing_on() is o or self.resting_on(o):
            return self._fail("PickupFailed:NoBlock")
        o.held = True
        a.holding = o.id
        self._after("pick_up", id=o.id)
        return self._result("PickupSuccess")

    def place(self, position, rotation=None) -> str:
        if self.air is not None:
            self._land()
        a = self.avatar
        if not a.holding:
            return self._fail("PlaceFailed:EmptyHands")
        if position is None:
            return self._fail("PlaceFailed:MissingPosition")
        if rotation is not None and not (isinstance(rotation, dict) and all(isinstance(v, (int, float)) for v in rotation.values())):
            return self._fail("PlaceFailed:InvalidRotation")
        x, y, up = self.from_paper(position)
        o = self.objects[a.holding]
        if math.dist((x, y, up), (a.x, a.y, a.z)) > float(self.pcfg["place_range"]) or not (0 <= x <= self.size and 0 <= y <= self.size):
            return self._fail("PlaceFailed:OutOfRange")
        bottom = up - o.sz / 2
        ox, oy, oz = o.x, o.y, o.z
        o.x, o.y, o.z = x, y, bottom
        clash = bottom < self.terrain.height(x, y) - 0.15 or any(
            p is not o and p.overlaps_xy(o) and p.z < o.top - 0.05 and p.top > o.z + 0.05 for p in self._free())
        if clash:
            o.x, o.y, o.z = ox, oy, oz
            return self._fail("PlaceFailed:Occupied")
        o.held = False
        a.holding = None
        if rotation:
            o.__dict__["yaw"] = float(rotation.get("yaw", 0.0))
        self._after("place", id=o.id)
        return self._result("PlaceSuccess")

    def throw_at(self, direction, speed) -> str:
        a = self.avatar
        if not a.holding:
            if self.air is not None:
                self._land()
            return self._fail("ThrowFailed:EmptyHands")
        if direction is None:
            return self._fail("ThrowFailed:MissingDirection")
        try:
            dx, dy_up, dz = (float(v) for v in list(direction)[:3])
        except (TypeError, ValueError):
            return self._fail("ThrowFailed:InvalidDirection")
        n = math.sqrt(dx * dx + dy_up * dy_up + dz * dz)
        if n < EPS:
            return self._fail("ThrowFailed:InvalidDirection")
        sp = min(max(float(speed or 0.0), 0.0), float(self.pcfg["max_throw_speed"]))
        vx, vy, vz = dx / n * sp, dz / n * sp, dy_up / n * sp + float(self.pcfg["throw_up_impulse"])
        z0 = a.z + HAND_HEIGHT
        if self.air is not None:  # thrown mid-jump: inherit part of the jump's velocity
            vz += float(self.pcfg["inherit_fraction"]) * self.air["vz"]
            z0 += float(self.av_cfg["jump_height"]) * 0.5
        o = self.objects[a.holding]
        o.held = False
        a.holding = None
        o.x, o.y, o.z = a.x, a.y, z0
        x0, y0 = o.x, o.y
        ix, iy, iz = self._fly(o, (vx, vy, vz))
        g = float(self.phys["gravity"])
        hv = math.hypot(vx, vy)
        if hv > 1e-3:
            tt = math.hypot(ix - x0, iy - y0) / hv
        else:  # straight up: time to come back down to the impact height
            tt = (vz + math.sqrt(max(0.0, vz * vz + 2 * g * (z0 - iz)))) / g
        vimp = math.hypot(hv, vz - g * tt)
        self.events.append({"type": "landed", "id": o.id, "at": [_r(ix), _r(iy), _r(iz)], "speed": _r(sp), "impact_speed": _r(vimp)})
        if self.air is not None:
            self._land()
        imp = self.pcfg["impact"]
        if imp.get("enabled", True) and o.shape == "rock":
            energy = 0.5 * o.mass * vimp * vimp
            if vimp >= float(imp["min_speed"]) and energy >= float(imp["min_energy"]):
                k = min(int(imp["max_blocks"]), 1 + int((energy - float(imp["min_energy"])) // float(imp["energy_per_block"])))
                self._shatter(ix, iy, iz, k)
        self._after("throw", id=o.id, speed=sp)
        return self._result("ThrowSuccess")

    def _shatter(self, x: float, y: float, z: float, k: int) -> None:
        self.impacts += 1
        start = sum(1 for o in self.objects.values() if o.shape == "impact")
        for i in range(k):
            ang = 2 * math.pi * i / k + 0.37 * self.impacts
            r = 0.75 + 0.25 * (i % 2)
            oid = f"impact_{start + i + 1}"
            o = self._add(oid, "impact", "stone", self._clamp(x + math.cos(ang) * r), self._clamp(y + math.sin(ang) * r))
            o.z = max(z, self.terrain.height(o.x, o.y))
            self.spawned += 1
            self.events.append({"type": "spawn", "id": oid, "at": [_r(o.x), _r(o.y), _r(o.z)], "hidden_rule": True, "rule": "rock_impact"})

    def _fail(self, code: str) -> str:
        self.time += 1
        return self._result(code)

    def _after(self, action: str, **info) -> None:
        super()._after(action, **info)
        sea = float(self.cfg["sea_level"])
        for o in list(self._free()):
            if o.top < sea - 0.05 and self.terrain.height(o.x, o.y) < sea:
                del self.objects[o.id]
                self.lost.append(o.id)
                self.events.append({"type": "lost", "id": o.id})

    # ------------------------------------------------------------ dispatch
    def dispatch(self, name: str, args: dict) -> tuple[str, bool]:
        """Run one paper action; returns (json_result, is_error)."""
        try:
            if name == "move_to":
                r = self.move_to(args.get("position"))
            elif name == "jump":
                r = self.jump()
            elif name == "stop":
                r = self.stop()
            elif name == "pickup":
                r = self.pickup(args.get("position"))
            elif name == "place":
                r = self.place(args.get("position"), args.get("rotation"))
            elif name == "throw":
                r = self.throw_at(args.get("direction"), args.get("speed"))
            else:
                return f"Unknown action {name}.", True
        except (ValueError, TypeError, ActionError) as e:
            return f"Invalid input for {name}: {e}", True
        return r, "Failed" in self.last_result
