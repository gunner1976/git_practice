# SEMANTIC_MEMORY.md - What I Know and I Can Do

Organize by topic; tag bullets *verified* / *fact* / *mistake* / *hypothesis*. No dates or session references. Rewrite bullets in place when refined.

## Index
- World: island layout
- Moving: move_to behavior and pitfalls
- Picking up / placing / stacking
- Throwing
- Objects: Ring, Rock

## World
- *fact* Start at [0,0.7,-22]. Island: hills (Peak, Hill_1-4), a mesa (Spire at -14,8), 12 unanchored 1x1x1 Blocks, a Ring, a Rock. No other players seen.
- *fact* observe returns every entity with position; use it after any action to verify results.

## Moving
- *verified* move_to returns Ready immediately and the position updates.
- *mistake* A straight move_to can get stuck against the Spire mesa: it returns Ready but position doesn't change. Fix: use waypoints, e.g. [-8,1,12] then [-3,1.5,0] to cross the island.

## Picking up / placing / stacking
- *verified* pickup needs me within ~2 units of the object (else PickupFailed:OutOfRange). Holding one item at a time.
- *verified* place inside terrain/object fails (PlaceFailed:Occupied). Place slightly above the surface and it settles by physics.
- *verified* Stacking: place ~0.7 above the top block's center at the same x,z; settles flush (1 unit apart). A 4-block tower plus Ring is stable.

## Throwing
- *verified* throw {direction, speed}: Rock thrown dir [-1,0.3,-0.5] speed 15 flew ~13 units; a flat throw of a block ([-1,0.1,0], speed 25) went ~10 units and stopped short (likely hit tower). Throws spawn small ImpactBlock entities.

## Objects
- *verified* Ring has no buttons (press -> NothingInReach); decorative, stackable.
- *verified* A point-blank throw ([-1,0.5,0], speed 30) of a Block at the tower moved it only ~2 units and did not topple the 4-block tower. Thrown blocks seem to land softly; throws can't knock stacks over (as tested).
- *fact* Time passes quickly (day to night within ~35 ticks); stars appear in observe at night.

## Building arches
- *mistake* Pillars 2 apart (centers) leave a gap exactly 1 wide; a 1x1 lintel placed between them falls through to the ground. Blocks are 1 wide, so a lintel only bridges a gap < 1: space pillars ~1.5 apart (centers), or offset the lintel so it rests on both.
- *fact* Blocks cannot be knocked off a stack by throwing; stacking is sturdy.
- *fact* Fetching blocks: unanchored loose blocks remain around the island (e.g. near Peak, Hill_4, west edge); use waypoints around the Spire.
- *verified* Pillars at x=-8 and x=-9.5 (centers 1.5 apart): a lintel placed at x=-8.75 slid/settled onto one pillar (x=-9.5, stacked 2 high) rather than bridging. Bridging gaps with 1x1 blocks seems unreliable; placement appears to snap onto the nearest block below. Untested idea: place the lintel exactly at the midpoint with pillars centers 0.9 apart, or place with a rotation.
- *mistake* move_to can silently fail (position unchanged) when I'm wedged beside placed blocks or near the island's NW edge (~(-14,-16), y drops below 0). Fix: jump, step away via a nearby waypoint, and head through the island interior (e.g. [-8,1.5,-10]) before going west.
