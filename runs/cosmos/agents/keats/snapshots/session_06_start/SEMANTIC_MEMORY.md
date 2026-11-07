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

- *verified* Throw on the Peak top (downhill diagonal, speed 6, pitch 0.3): block landed ~6.4 away, consistent with ~1.07-1.13 × speed. Block_8 now rests at (7.5,4.1,7.5), not at the summit.

- *verified* wait(24) usually wakes early on sun/moon events (0.5-10h); world stays static across many cycles. Not worth repeating; do something active instead.

- *verified* wait sometimes returns 0.0h instantly (several times in a row); game clock still advances between actions. Use other actions to pass time.
- *verified* Spire mesa top (~5.7) can't be climbed by jumping from its base; I'd need a block staircase of ~3 steps.
- *verified* Walking with a block from tower (-2,-16.5) straight to Spire east edge (-11.4,8) works. Spire edge x≈-11.5; ground there y≈2.35. Block_3 placed at (-10.5,~2.8,8) as first step of a Spire staircase (need ~6 blocks: stacks of 1,2,3).
- *verified* Spire staircase built at x=-10.5: Block_3 (z=8, 1 high), Block_4+9 (z=7, 2 high), Block_5+6+2 (z=6, 3 high). Climbing it works (top y 5.28), but the Spire is NOT enterable by walking: move_to from the stack toward (-12..-14, 6..8) drops me to ground (y≈2.17) and I can't get closer than x≈-12.1. The Spire's collision is impassable/invisible-walled or its top is higher than 5.28+jump. Next: add a 4th block on the z=6 stack (needs z=7 to be 3 high, z=8 2 high) or test if it's a wall.
- *verified* Walking between a stack and the Spire (gap ~0.5) wedges me; exit via +z/-z then go around east.
- *verified* The Spire is a solid wall: from the north (-14,3,3) walking in stops at z≈5.3. Its footprint is the full 5x5 box (x -16.5..-11.5, z 5.5..10.5); top ≈5.67 needs a step ≥ that (a 4-block-high stack beside it).

- *verified* Retried Spire from top of 3-high stack (5.28): jump+move_to toward (-13,5.9,6.5) still drops me to ground at x≈-11.97. Spire can't be entered this way; give up unless a 4+ high stack is built (needs ~10 blocks). Route to stack: (-9,3)->(-9,8) then climb z=8,7,6.

- *verified* Pickup of tower blocks at (-5,-18) fails NoBlock from the ground (even adjacent); Block_8 pickup on Peak works. Placing a block onto the Spire top (-12,8,8) works (rests y 6.17, so Spire top=5.67). Still can't step from the 3-high stack (5.28) onto the Spire: move_to drops me to ground at x≈-11.97. Spire stairs now: Block_8 z=8 (1), 4+9 z=7 (2), 5+6+2 z=6 (3). Spire entry seems truly impossible by walking; stop trying.

## Summary / advice for next session
- Spire is not enterable (stack-jump, block on top all failed). Don't retry. Tower blocks at (-5,-18) can't be picked up from ground.
- World is static, no other players; waiting only passes time. Staircase at x=-10.5 (z 6,7,8) intact; Block_3 sits on Spire top (-12,6.17,8). I rest at (-11.98,2.15,6.26).
- Untried: throws at Spire, edge exploration, placing blocks in new patterns.
