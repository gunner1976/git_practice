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
SHAPES.setdefault("tablet", ((1.2, 0.3, 0.9), 1000.0))  # the mission tablet: far too heavy to lift
SHAPES.setdefault("phone", ((0.08, 0.16, 0.02), 0.2))  # the mission phone (world/phone.py)
PHONE_REACH, PHONE_EARSHOT = 2.5, 15.0

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
        # a round planet (world/sky.py), if configured: the sky in observations shows its shape
        self.planet = None
        if cfg.get("planet"):
            from .sky import Planet

            self.planet = Planet(cfg["planet"], (self.terrain.cx, self.terrain.cy))
        self.day_fraction = 0.5  # set by the session loop from its clock
        # EKO, the full planet (world/eko.py): its gravity drives the island's physics and its sky
        # (star, moon, stars) is what the agent sees; sky_tau is EKO time, set by the session loop
        self.eko = None
        self.sky_tau = 0.0
        if cfg.get("eko"):
            from .eko import Eko

            self.eko = Eko(cfg["eko"], (self.terrain.cx, self.terrain.cy))
            earth_g = float(self.phys["gravity"])
            self.phys = {**self.phys, "gravity": self.eko.g}
            # same legs, different gravity: a jump reaches higher in proportion to 1/g
            self.av_cfg = {**self.av_cfg, "jump_height": float(self.av_cfg["jump_height"]) * earth_g / self.eko.g}
        # the mission (cfg "mission"): trials that carry over between days (achievements, kept by
        # the runner per agent); when all are done a tablet appears on the Spire's top, readable
        # only from close by
        self.mission = cfg.get("mission")
        self.achievements: dict = {}
        # with mission reward "phone", a phone appears instead of the tablet; its line to the
        # partner agent is attached by the runner (world/phone.py)
        self.line = None
        self.notices_q: list[str] = []
        self._announced = False

    def reset(self) -> None:
        super().reset()
        self.air = None
        self.last_result = "Ready"
        self.impacts = 0
        self.lost = []
        self._announced = False
        self.notices_q = []
        self._mission_check()

    def set_state(self, state: dict, avatar: bool = True) -> None:
        super().set_state(state, avatar)
        self.air = None
        self.last_result = "Ready"
        self._mission_check()

    # ------------------------------------------------------------ the mission
    def _achieve(self, name: str) -> None:
        if not self.achievements.get(name):
            self.achievements[name] = True
            self.events.append({"type": "achievement", "name": name})

    def _mission_check(self, events: list[dict] | None = None) -> None:
        m = self.mission
        if not m:
            return
        trials = m.get("trials", {})
        if trials.get("tower_height") and not self.achievements.get("tower"):
            from .tasks import tallest_tower

            if tallest_tower(self)["n_objects"] >= int(trials["tower_height"]):
                self._achieve("tower")
        if trials.get("rock_fragments") and any(e.get("rule") == "rock_impact" for e in (events or [])):
            self._achieve("rock_fragments")
        needed = [k for k, v in (("tower", trials.get("tower_height")), ("rock_fragments", trials.get("rock_fragments")),
                                 ("saw_lunar_eclipse", trials.get("saw_lunar_eclipse"))) if v]
        if not all(self.achievements.get(k) for k in needed):
            return
        reward = m.get("reward", "tablet")
        oid = f"{reward}_1"
        if oid not in self.objects:
            sx, sy, top = self.terrain.spire_summit
            ground = self.surface_at(sx, sy)
            o = self._add(oid, reward, "black" if reward == "phone" else "stone", sx, sy)
            o.z = ground
            self.events.append({"type": "spawn", "id": oid, "at": [_r(o.x), _r(o.y), _r(o.z)], "hidden_rule": True, "rule": f"mission_{reward}"})
        if m.get("announce") and not self._announced and not self.achievements.get(f"found_{reward}"):
            self._announced = True  # once a day until it is found
            self.notices_q.append(str(m["announce"]).strip())

    # ------------------------------------------------------------ the phone
    def has_phone(self) -> bool:
        return "phone_1" in self.objects

    def phone_reach(self) -> str | None:
        """'hand' (held), 'near' (within reach), 'earshot', or None (no phone, or far off)."""
        o = self.objects.get("phone_1")
        if o is None:
            return None
        a = self.avatar
        if a.holding == "phone_1":
            return "hand"
        d = math.dist((o.x, o.y, o.z), (a.x, a.y, a.z))
        return "near" if d <= PHONE_REACH else "earshot" if d <= PHONE_EARSHOT else None

    def notices(self) -> list[str]:
        """What the agent perceives without acting this turn: an announcement, the phone."""
        out, self.notices_q = self.notices_q, []
        if self.line is not None:
            out += self.line.poll()
        return out

    def press(self, button) -> str:
        if self.air is not None:
            self._land()
        code = self.line.press(str(button)) if self.line is not None and self.has_phone() else "PressFailed:NothingInReach"
        if code.startswith("PressSuccess"):
            self._achieve("pressed_" + ("call" if "Ring" in code or "Conn" in code or "NoAnswer" in code else "end"))
            if code.endswith("Connected"):
                self._achieve("connected")
        self.time += 1
        return self._result(code)

    def speak(self, text) -> str:
        code = self.line.speak(str(text)) if self.line is not None else "SpeakSuccess:NobodyHears"
        if code.endswith("IntoPhone"):
            self._achieve("spoke_on_phone")
        self.time += 1
        return self._result(code)

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
        return {"rock": "Rock", "ring": "Ring", "egg": "Egg", "tablet": "Tablet", "phone": "Phone"}.get(o.shape, o.id)

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
            ent = {"name": self.name_of(o), "entity_type": "part", "position": self.to_paper(o.x, o.y, o.z + o.sz / 2), "size": [_r(o.sx), _r(o.sz), _r(o.sy)],
                   "shape": "block" if o.shape in ("cube", "impact") else "slab" if o.shape == "tablet" else o.shape,
                   "color": RGB.get(o.colour, [0.5, 0.5, 0.5]), "anchored": o.shape == "tablet"}
            if o.shape == "tablet":
                a = self.avatar
                near = math.hypot(a.x - o.x, a.y - o.y) <= 2.5 and abs(a.z - o.z) <= 2.0
                ent["attributes"] = {"inscription": self.mission["message"]} if near else {"marks": "something is carved on it, too small to read from here"}
                if near:
                    self._achieve("read_mission")
            if o.shape == "phone":
                reach = self.phone_reach()
                if reach in ("hand", "near"):
                    ent["attributes"] = {"buttons": ["call", "end call"], "line": self.line.status() if self.line is not None else "quiet"}
                    self._achieve("found_phone")
                else:
                    ent["attributes"] = {"looks_like": "a small black object"}
            ents.append(ent)
        obs = {"tick": self.time, "game_status": "active", **(extra or {}), "player": self._player(), "other_players": [], "world": {"entities": ents}}
        if self.avatar.holding == "phone_1":
            obs["player"]["holding_attributes"] = {"buttons": ["call", "end call"], "line": self.line.status() if self.line is not None else "quiet"}
            self._achieve("found_phone")
        if self.eko is not None:
            a = self.avatar
            obs["sky"] = self.eko.sky(a.x, a.y, max(self.terrain.height(a.x, a.y), a.z), self.sky_tau)
            moon = obs["sky"].get("moon")
            if self.mission and isinstance(moon, dict) and moon.get("eclipse", {}).get("darkened_fraction", 0) >= 0.5:
                self._achieve("saw_lunar_eclipse")
                self._mission_check()
        elif self.planet is not None:
            a = self.avatar
            az, el = self.planet.sun(a.x, a.y, self.day_fraction)
            ground = self.terrain.height(a.x, a.y) if a.z <= self.terrain.height(a.x, a.y) + 1e-6 else a.z
            obs["sky"] = {"sun": {"azimuth_deg": round(az, 2), "elevation_deg": round(el, 2)},
                          "sea_horizon": {"angle_below_eye_level_deg": round(self.planet.horizon_dip(max(ground, a.z)), 2)}}
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
            if not self._inside(nx, ny) or self.terrain.height(nx, ny) < wade:
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
            if not self._inside(nx, ny) or self.surface_at(nx, ny) > ceiling:
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
        if best is None or bd > float(self.pcfg["pickup_snap"]) or best.shape == "tablet":
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
        if math.dist((x, y, up), (a.x, a.y, a.z)) > float(self.pcfg["place_range"]) or not self._inside(x, y):
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
        n = 0
        legacy = bool(self.pcfg.get("legacy_impact_ids"))
        start = sum(1 for o in self.objects.values() if o.shape == "impact")
        for i in range(k):
            ang = 2 * math.pi * i / k + 0.37 * self.impacts
            r = 0.75 + 0.25 * (i % 2)
            if legacy:
                # runs made before this was fixed numbered new debris by counting what was left,
                # which could reuse the id of a piece still on the island and silently replace it;
                # kept only so those runs replay exactly
                oid = f"impact_{start + i + 1}"
            else:
                n += 1
                while f"impact_{n}" in self.objects or f"impact_{n}" in self.lost:
                    n += 1
                oid = f"impact_{n}"
            o = self._add(oid, "impact", "stone", self._clamp(x + math.cos(ang) * r), self._clamp(y + math.sin(ang) * r))
            o.z = max(z, self.terrain.height(o.x, o.y))
            self.spawned += 1
            self.events.append({"type": "spawn", "id": oid, "at": [_r(o.x), _r(o.y), _r(o.z)], "hidden_rule": True, "rule": "rock_impact"})

    def _fail(self, code: str) -> str:
        self.time += 1
        return self._result(code)

    def _after(self, action: str, **info) -> None:
        super()._after(action, **info)
        self._mission_check(self.events)
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
            elif name == "press":
                r = self.press(args.get("button", ""))
            elif name == "speak":
                r = self.speak(args.get("text", ""))
            else:
                return f"Unknown action {name}.", True
        except (ValueError, TypeError, ActionError) as e:
            return f"Invalid input for {name}: {e}", True
        return r, "Failed" in self.last_result
