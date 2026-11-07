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
