# SEMANTIC_MEMORY.md - What I Know and I Can Do

## Index
Actions; World layout; Climbing/Spire; Tower; Moon; Idle policy

## Actions
- *verified* move_to next to a block (within ~1 unit), then pickup at the block's position works. Carrying is one item at a time.
- *verified* place: y≈1.2 is "Occupied"; place a little above ground and it settles. Max reach ~6.5 units. Placing at my own position fails (can't build under myself).
- *verified* Blocks are 1x1x1, unanchored, stack under gravity.
- *verified* throw is heavily capped in range (~7-16 units). Direction is world space. Never throw unique objects (Rock was lost to the sea twice that way).
- *mistake* move_to can silently stop short (result still "Ready"). Always check the returned position. Wedged against blocks/walls: call jump and move_to in the SAME batch to a point away from them.
- *verified* Ring and Rock have no buttons; tower blocks have no buttons (press -> NothingInReach).
- *verified* ImpactBlocks (0.4 size) are pickable.
- *mistake* write_note overwrites the file. Use append_note for additions to memory files.

## World layout
- Island with hills (Peak summit (12,12) y≈3.98, Hill_1..4), Spire mesa at (-14,8) top ≈5.7, 12 blocks, Ring, Rock (lost), 3 ImpactBlocks. Start (0,0.7,-22). Ground ≈0.9-1.5.
- Perimeter fully explored; nothing special anywhere. East edge x>20 slopes into the sea (stalls move_to). No other players (speak -> NobodyHears).
- Route around Spire: via (-19,1.5,y) waypoints; the mesa blocks straight move_to.
- Day/night cycle exists.

## Climbing / Spire
- *verified* A single block on ground (top ≈2.45) is climbable: jump then move_to its top from ~1.5 away. Stacked columns are not climbable (step ~1.1 too high; move_to flaky).
- Spire top needs a staggered staircase (stacks of 1,2,3,4 = 10 blocks). Only 4 loose blocks (3,5,6,9) near the Spire, so infeasible unless the tower blocks become pickable.

## Tower
- 7+ blocks stacked at (-3,*,-20). *verified* Pickup returns NoBlock from every side; throws don't dislodge it. Permanently unpickable. Don't retry.

## Moon
- *verified* Moon rises east/night, phases vary, appears huge but unreachable (throws capped ~12 units, stacking impossible). Mission judged infeasible.

## Idle policy
- The island is static and fully explored; repeated observe/wander yields nothing. When asked to continue, a cheap move_to or short note is enough; don't re-test tower pickup, moon, or Spire climb unless a genuinely new idea appears.

## Status (2026-05-09)
- World still static across many sessions. Rock is lost. East edge (x≈20) slopes below sea level (y -0.67). Idle policy stands: cheap move_to, brief notes, no re-testing of tower/moon/Spire.
