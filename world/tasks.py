"""Automatic scoring of Phase B tasks from world state.

Each scorer returns a dict with a `score` (the primary number used in the
analysis) plus supporting detail.
"""

from __future__ import annotations

import math

from .island import World


def spire_objects(w: World) -> dict:
    sx, sy, top = w.terrain.spire_summit
    on = [
        o.id
        for o in w.objects.values()
        if not o.held and math.dist((o.x, o.y), (sx, sy)) <= w.terrain.spire_radius and o.z >= top - 0.3
    ]
    return {"score": len(on), "objects": on}


def tallest_tower(w: World) -> dict:
    """Height (m) of the tallest stack of >= 2 objects, measured from the ground
    under its bottom object, after the world has settled (so it is stable)."""
    w.settle()
    best = {"score": 0.0, "n_objects": 0, "objects": []}
    for o in w.objects.values():
        if o.held:
            continue
        chain = [o]
        cur = o
        while True:
            _, sups = w.support(cur)
            if not sups:
                break
            cur = max(sups, key=lambda s: s.top)
            chain.append(cur)
        if len(chain) < 2:
            continue
        base = chain[-1]
        h = o.top - w.terrain.height(base.x, base.y)
        if h > best["score"]:
            best = {"score": round(h, 3), "n_objects": len(chain), "objects": [c.id for c in reversed(chain)]}
    return best


def ring_on_peak(w: World) -> dict:
    r = w.objects["ring_1"]
    px, py, pz = w.terrain.peak_summit
    d = math.dist((r.x, r.y), (px, py))
    ok = (not r.held) and d <= 2.0 and r.z >= pz - 1.0
    return {"score": int(ok), "ring_height": round(r.z, 2), "dist_to_summit": round(d, 2)}


def make_cubes(w: World) -> dict:
    n = sum(1 for o in w.objects.values() if o.shape == "cube")
    return {"score": n - w.n_initial_cubes, "cubes": n}


TASKS = {
    "spire_objects": spire_objects,
    "tallest_tower": tallest_tower,
    "ring_on_peak": ring_on_peak,
    "make_cubes": make_cubes,
}


def score(task: str, w: World) -> dict:
    return TASKS[task](w)
