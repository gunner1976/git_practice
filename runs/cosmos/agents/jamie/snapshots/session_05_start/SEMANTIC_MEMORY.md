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
- *verified* Placing a block ~1.2 above a pillar top at the same x,z settles onto it flush (pillar of 3 stable at x=-9.5).
- *verified* A block placed with a 0.5 overhang past a pillar's edge (x offset 0.5) stays put, so cantilevers hold. Idea: build a pillar on each side with 0.5 overhangs to make the gap bridgeable.
- *mistake* Cantilever bridge attempt: a half-overhanging block was stable alone, but placing a Ring (0.8 wide) between two overhangs 0.5 apart knocked the west overhang and top pillar block off (they fell to the ground). The lintel placement displaces neighbors; overlapping placement physically shoves blocks. Leave a real gap (>=0.1) or don't place while overlapping.
- *fact* The "collapse" was likely the Ring placed at a spot that was inside the pillar column (x=-8.25 shoved blocks and the Ring got wedged mid-pillar at x=-9.45, lifting upper blocks ~0.15). Always observe after each placement. Pillars with 0.5-0.3 overhangs hold; to bridge, gap must be < lintel width (Ring 0.8, Block 1.0) but also > 0 clearance.
- *mistake* Cantilever/overhang bridge: after adding a lintel resting on two overhangs, both pillars toppled entirely (all blocks fell). Overhang stacks are marginally stable and any added load collapses them. Don't build bridges with overhangs; use pillars centered and a lintel only if a wider piece exists. Also loose blocks I walk near may get shoved.
- *verified* I can climb onto a single placed block: move_to a point on top of it (after a jump) puts me standing on it (y rises ~0.8). Placing at a spot overlapping me fails (Occupied); step back first.
- *mistake* Standing between two blocks ~1.1 apart wedges me (move_to north/south and jump do nothing). Fix: move_to sideways along the gap axis (e.g. change x by 1), then go around. Leave >=1.5 between blocks I stand between.
- *verified* Two-step climb works: ground -> 1-high block (jump + move_to top) -> adjacent 2-high stack (jump + move_to top), reaching y~3.5. Leave a ~1 gap between steps, not wedged.
- *hypothesis* Next goal: staircase 1-high, 2-high, 3-high blocks (each adjacent, ~1 apart) to climb higher; I can pick up blocks from atop a stack if within ~2 units.
- *verified* Staircase 1 -> 2 -> 3 blocks high (adjacent stacks ~1.1 apart) is climbable with jump + move_to onto each top; reached y~4.6. I can pick up blocks from standing on a stack if within ~2 units.
- *mistake* pickup on blocks at x=-7,z=-17 (Block_1/Block_11, in the old east pillar) returned NoBlock even within 1 unit; the observed positions may be unreliable for stacked/ resting blocks. Rock pickup worked fine. Try pickup on the exact observed coordinates from a fresh observe, or from another side.
- *hypothesis* Blocks 1, 3, 7, 11 (old east pillar remnants) never change position across many observations and can't be picked up; they may be stuck/frozen. Use other blocks (2, 5, 6, 10, 12 are in my staircase; 4, 8, 9 are far away on hills).
- *verified* Rock can be placed atop a 3-block stack (place ~0.5 above top) and rests there stably; pickup of Rock from 2 units away works.
- *verified* place works at a distance (~2-3 units, even at height 5.5 from the ground), so I can cap towers without climbing.
- *verified* Walking to the Peak summit (12,3.98,12) via [0,2,-5] works in two move_to calls; Peak top is y~3.98.
- *verified* Loose blocks 4, 8, 9 are pickup-able and carryable to the Peak; placing each ~1.1 above the stack top settles flush. Peak beacon (3 blocks at 12,*,12.8) is stable.
- *fact* throw with empty hands returns ThrowFailed:EmptyHands; pick something up first.
- *fact* State of the island: west tower (3 blocks + Rock + Ring at -8.5,*,-14.5) and Peak beacon (3 blocks at 12,*,12.8) both stable across nights. Exploration is basically exhausted; remaining ideas: taller towers, climbable stairs on Peak.
- *mistake* Throwing a Block hard ([1,0.6,0], speed 30) from the Peak summit made it vanish from the world (flew off the island / despawned). Don't throw blocks you want to keep. Only 11 blocks remain (Block_4 lost).
- *mistake* pickup of Block_12 at its observed position (-8.5,1.98,-15.6) returns NoBlock even from 1.5 away; blocks in the old west staircase (5,6,10,12,2) may be stuck/unpickable like 1,3,7,11. Rock and Ring and loose hill blocks (4,8,9) were pickable. Use observed-fresh coords, or pick loose ones only.
- *verified* Correction: the top block of a stack is pickable (Block_6 at -8.5,2.98,-15.6 worked from (-9.5,-16)); blocks buried beneath another (Block_12) give NoBlock. Pick from the top down.
- *verified* Beacon on Peak can be capped with Ring then Rock (place ~0.5-0.8 above top); stable. Moving pieces top-down from the west tower works (Ring, Rock pickable).
- *verified* Peak staircase (1-block step at x=8.8, 2-block pillar at x=10, z=12.8) climbable: approach the step straight on (from z=11.2), jump, move_to its top; then jump, move_to the pillar top (y~6). Diagonal approaches fail.
- *fact* Island is now fully used: all loose blocks are in the Peak structure; remaining west blocks (1,3,7,11,12) are stuck/unpickable.
- *verified* "Stuck" east-stack blocks are NOT stuck: Block_3 (top of stack) picked up fine from (-5.5,-16.5). Rule: pick top-down, approach from within ~1.5. Blocks 7, 11, 1 remain available at around (-6,-17). Pillar at Peak x=10 now 3 high (Blocks 2,10,3).
- *verified* ALL blocks are pickable if top-of-stack (Block_12, Block_1 too); the earlier "stuck" notes were wrong. West tower and east stack are now fully emptied. Peak staircase at z=12.8: x=7.7 (2 high), x=8.8 (2 high), x=10 (3 high); beacon at x=12 (3 blocks+Ring+Rock). Plan: place held Block_12 at x=6.6 as the 1-high first step; steps then go 1,2,2,3 (the 2->2->3 chain is climbable by jump+move_to straight on).
- *verified* Full Peak staircase (heights 1,2,2,3 at x=6.6,7.7,8.8,10; z=12.8) climbed from the ground to y~7 with jump + move_to on each step. Project complete; all 12 blocks placed.
- *verified* Can't cross from the 3-high pillar (x=10) to the beacon (x=12) by move_to: I walk off and drop to the ground at (11.5,3.92). The beacon is not climbable (it's too tall and no step reaches it).
