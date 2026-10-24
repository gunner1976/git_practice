# SEMANTIC_MEMORY.md - What I Know and I Can Do

## Index
- Actions
- World

## Actions
- *verified* move_to then pickup at an entity's position works (pickup succeeded from ~1 unit away).
- *fact* Persona name conflict: SOUL says Kip, system says Eko. I go by Eko.

## World
- *fact* Small island with hills (Peak, Hill_1-4, Spire mesa), 12 unanchored 1x1 blocks, a Ring, and a Rock. Start near (0,0.7,-22).

## Building
- *verified* Stacking: place at the target block's x,z with y = target y + 1.0 (blocks are 1x1x1). Placed blocks stay put exactly there. Walk within ~1-5 units of the target first; place worked from ~1.5 units away.
- *verified* Carrying a block while move_to works fine.
- *verified* Rock can be picked up and placed on a block stack (place y = block top + half its height, ~5.4 on a 4-block column).
- *verified* Throw: direction [-1,0.3,0], speed 10 sent a block ~13 units horizontally from ~1.7 height. Throw drops what you hold.

## Movement
- *mistake* move_to over long distances may stop partway (blocked by terrain like the Spire mesa) or leave me in a pit/water (y<0). Cure: use short waypoint hops and check position; if stuck (position unchanged after move_to), jump(), then move_to a nearby spot.
- *verified* Pickup/place range is only a few units; PickupFailed:OutOfRange / PlaceFailed:OutOfRange means walk closer. A failed pickup leaves hands empty so a later place gives EmptyHands.
- *fact* Route from SW corner (Ring at -19,18) to the tower (-9,-18) works going via (-20,8),(-20,2),(-18,-10), then ending near (-12,-16) (avoid -14,-13: pit).

## Open ideas
- Untried: jumping onto/climbing the tower, building a second structure from the 8 remaining blocks, throwing at the tower to test collisions.

- *verified* A thrown block (speed 12, flat) hitting the base of the 4-block tower did not topple it; the block just dropped beside it. The stacked tower is stable against light impacts.

- *verified* Climbing: plain move_to onto a 1-high block fails (stays at ground). Do jump() then immediately move_to the block's top (y = block top + ~0.5): I landed on it (y 2.14). Combine with stacked blocks to build stairs; tower top (~5) would need ~4 stair steps.

- *verified* Two-step climb works: jump()+move_to up each 1-high step (reached y=3.14 on a 2-high column). The move_to to a target beyond a gap onto the tower failed; I just walked down to the ground. A single jump gains ~1 unit, so every step must be at most 1 higher than the last, with no gap larger than ~0.5.

## Climbing recipe (verified)
- Stair of columns heights 1,2,2,3 along x = -5.5,-6.5,-7.5 (1.0 spacing) reached the tower side. Repeating jump() + move_to(next column top, y = top+0.5) worked each step; final jump reached y=5.12 at the tower's edge (x=-8.7), at the top-block level.
- Need 1-high first step; a 2-high column from ground is too high.
- Remaining loose blocks: Block_3 (SW), Block_5 (W). Tower at (-9.2,-18.2).

- *verified* The stair recipe above puts me standing on top of the 4-block tower (y=5.12), confirmed by observation. Stair and tower stay stable while I stand on them.

- *mistake/uncertain* From the tower's top edge (standing at -8.7,5.12) pickup of the Rock at its exact position (-9.2,5.42) returned PickupFailed:NoBlock, even though it was 0.5 away. Cause unknown (maybe I overlap the target or it is occluded); try stepping to a different spot before retrying. Throw without holding gives ThrowFailed:EmptyHands.

- *verified* Stacked Rock and Ring on the tower top cannot be picked up from the tower's edge (NoBlock twice), and move_to onto the tower top itself doesn't move me (blocked). Descend by walking off / move_to ground. Pickup items from ground level next to the target instead.

## Island geography (verified by getting stuck)
- The island's west/southwest edge near the tower is WATER: points like (-13,-14) and (-16,-20) put me at y≈-0.8 (swimming/stuck). Never route west of x≈-12 for z between -22 and -10.
- Earlier trip to the SW corner worked by going through the island centre/Spire side via (-11,8)->(-15,6)->(-20,8)->(-19,16.5). Return the same way, hopping in short waypoints; route from the tower toward the centre first (e.g. (-5,-10),(-8,0)).
- Stuck in water: jump() then move_to a nearby point back toward the island (east).
