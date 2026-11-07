# SEMANTIC_MEMORY.md - What I Know and I Can Do

Principles: store only durable, actionable knowledge; organize by topic; mark verified vs hypothesis; no timestamps or session references; rewrite in place when beliefs change.

## Index
- Pickup / Place
- Movement
- Throw
- World layout

## Pickup / Place
- *verified* move_to within ~1 unit of an item, then pickup at the item's exact position works (blocks, Rock, Ring).
- *verified* place near ground level (y≈0.9–1.5) fails "Occupied" (overlaps terrain/self). Place a few units above the target x,z; the item drops and rests on what is below.
- *verified* Blocks stack (height 1.0). Tower of 4 blocks + Rock + Ring is stable.
- *verified* place max range ≈ 6 units total from me; farther gives OutOfRange. Good staging spot for building at (-5,-18): stand at (-2,1.2,-19), place at y ≤ 6.2.
- *verified* Ring has no "use" button (press fails NothingInReach). No pressable thing found yet.

## Movement
- *verified* move_to has no pathfinding: placed blocks and terrain (hills, Spire mesa) block it. If position doesn't change or stops short, route via waypoints.
- *verified* Route to Ring in SW corner: (-20,3) → (-21,12) → (-19.2,17.2) (Spire at (-14,8) blocks the direct path). Return via (-14,-12).
- *verified* jump works (airborne:true).

## Throw
- *verified* distance ≈ 1.13 × speed with direction pitched ~0.3 up (e.g. [-1,0.3,0]) on flat ground. Use speed ≈ distance/1.13.
- *verified* direction is accurate (stays on the same line). Speed 10 overshoots the island and the item is lost permanently. Keep speed ≤ ~7 and aim inland.

## World layout
- Island ~±25 units, hills (Peak, Hill_1..4) and Spire mesa; no other players seen.
- 11 blocks remain (Block_10 lost). Tower at (-5,-18) holds Blocks 12,7,11,1 + Rock + Ring.
- Untried: throwing into the tower (does it topple?), building walls/bridges, pressing buttons on other objects.

## Tower durability
- *verified* A block thrown at the tower (speed 5.5, pitch 0.5) hit it and fell beside it; the tower didn't move. A lone thrown block can't topple it.
- *verified* I can climb onto a 1-high block: jump then move_to a point on top of it (stood at y≈2.2 on Block_2). Stair-stacking blocks next to the tower could let me climb it (untested).
- *verified* Climbing the tower directly from Block_2 (jump + move_to onto the 2nd block up) failed; I ended on the ground. Likely only ~1 unit step-up works per attempt; a staircase would need steps of 1 height each.

## Stair climbing
- *verified* Stair of Block_9 (-2.9), Block_2 + Block_6 stack (-3.9): jump + move_to climbs each 1-high step fine (reached y 3.22). Final hop onto tower Block_11 (top 4.19) failed, fell to ground. Tower is probably too narrow/shifted or the last step needs a closer start; try stepping closer (x≈-4.4) before the hop.
- *verified* Stair climbing: each 1-high step works, but the hop from Block_6 top (3.22) onto the tower's Block_11 top (4.19) fails twice (a ~1 step from the 3rd level isn't reliable). Also: standing in the 0.1 gap between stack and tower wedges me; walk out via -z/+z first. Hypothesis: need a stack whose top is level with Block_7 top plus a 1-step, i.e. build a full staircase (heights 1,2,3,4).
- *verified* SOLVED: climbed the tower top (y 5.19). Staircase: Block_3 at (-1.9), Block_9+Block_4 at (-2.9), Block_2+6+5 at (-3.9), each step 1 higher; jump+move_to per step, then jump+move_to (-4.8,4.8,-18) lands on Block_1 top. Rule: each step must be a single 1-high rise from a standing surface; a column must not sit directly on the block I'm standing on.
- *verified* From the tower top I can pick up the Ring/Rock directly (range fine) and place it back. Nothing else happens up there; no hidden trigger found.
- *verified* press "use" while holding a Block fails NothingInReach: blocks have no buttons either. Nothing pressable found anywhere.

## Current state (update)
- All blocks except lost Block_10 are placed: tower+staircase at (-5,-18); Block_8 on Peak summit. Waiting is cheap (wait wakes on sun/moon changes). The world is static without other players.
