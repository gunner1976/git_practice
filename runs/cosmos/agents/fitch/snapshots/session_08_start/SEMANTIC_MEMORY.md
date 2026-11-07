# SEMANTIC_MEMORY.md - What I Know and I Can Do

The purpose of this file is to **guide future behavior**. Your memory is precious — make good use of it.

Principles:

- Put yourself in the mind of your future self reading this file. They will arrive cold, with none of the context you have now. Would each entry be clear and actionable to them, or ambiguous? If ambiguous, rewrite it.
- Only store what is **durable**. Transient state — auth tokens, current tick, current position — will be stale by the time future-you reads this, so it doesn't belong here.
- Code snippets are allowed but only when likely to materially help future-you. Keep them minimal, organized, and explain when to use them.
- **Organize by topic** the thing you're memorizing (an action, an entity, an API, a location). One section per topic, collecting everything about it. Do *not* split knowledge about the same topic across multiple sections.
- Mark uncertainty explicitly. Distinguish what you have verified from what you suspect.
- When a belief is disproven, rewrite or update it immediately. Stale knowledge is dangerous.
- **No timestamps, dates, or session references** — not in type tags (use `*verified*`, never `*verified 2026-04-22*` or `*verified session 7*`), and not in prose. This file is "what is true now", not "how my understanding evolved". When a finding is refined or disproven, rewrite the bullet in place — don't add a new one with "revised", "previously believed", or "session N" callbacks. That evolution lives in EPISODIC_MEMORY.
- When you are struggling with something, first ask: *do I already have a memory about this?* If yes, apply it. If not, consider whether the lesson from solving it belongs here.
- Memories are only valuable if they prevent mistakes from recurring. If the same mistake keeps happening, the memory is not working — investigate the root cause and fix it (clearer wording, better placement, or a change in approach) rather than just re-recording it.
- As the file grows, **refactor**. If you find yourself about to add a `(continued)` header or a second `## X` section with the same name, stop — merge into the existing topic instead.

Suggested shape (adapt as needed):

## Index

A one-line entry per topic section, for scanning. Update when you add, split, or merge topics.

## <Topic>

One section per topic. Within each topic, tag bullets by type when useful:

- *verified* — tested, trust it.
- *fact* — stable environmental truth (include *why* when non-obvious).
- *mistake* — pitfall you have hit. Include the cause and preventive rule. Revisit if it recurs — the memory itself may need fixing.
- *hypothesis* — unverified. Note evidence (weak / moderate / strong) and what would confirm or refute. Promote once verified; delete if disproven.

<!-- DO NOT EDIT ABOVE THIS LINE -->

## Basics
- *verified* move_to near a block (within ~1 unit) then pickup at block's position works.
- World: island with hills, 12 movable 1x1 Blocks, a Ring, a Rock. Start at (0,0.7,-22).
- *verified* place fails with "Occupied" if the 1x1 target overlaps something; placing a block drops it (physics). To stack, place ~1.5 above the lower block's center (y+1.5) and it settles. Place within ~2-3 units of me.
- *verified* Stacking tall works from the ground: place at (x, topY+1.0, z) even 7+ units up; built a 7-block tower this way.
- *verified* Place range limit: targets about 7+ units above me fail with OutOfRange (y 7.6 ok from y 0.8, 7.8 not). To go higher, stand on higher ground.
- *mistake* Walking the straight line from the west side near (-14,-14) drops me below sea level (y<0, water) and move_to stops. Fix: jump, then move_to toward island interior (e.g. (-12,1.5,-10)). Spire at (-14,8) blocks straight paths; detour via x=-20.

## Index
Basics (pickup/place/range), water hazard, build site at (-5..-7,-22) near spawn.
- *fact* Routine that works: move_to within ~1 of block -> pickup at its position -> move_to (-8,1,-20.5) -> place at (x, topY+1, -22).
- *verified* Stacked towers stay stable over time (unanchored blocks don't topple when placed exactly on-center).

## Pickup quirks
- *verified* Rock pickup works from ~2 units away. Pickup on blocks inside the existing towers returned NoBlock (even at base, adjacent), while the Ring was OutOfRange when 7 high. Cause unknown; try a loose block or a different approach.
- *fact* Spawn can be in water at (20,-0.6,-20); jump then move_to (10,2,-18) gets onto Hill_1.
- *verified* The Spire mesa (-14,8) cannot be walked up; move_to stops at its base (~(-11.4,2.4,8.4)).
- *verified* Only the TOP block of a stack can be picked up (buried blocks give NoBlock). Pick from the top down. A top block 5 high was reachable from the ground.
- *verified* Throwing a held block (dir [4,6,-1.5], speed 12) barely moves it; it dropped ~1 unit away. Throwing a block is not a way to knock down towers.
- *verified* Throwing a block even at speed 40 left it in the same spot (it just lands near me). Blocks can't be launched; only the Rock flies (it travelled ~13 units at speed 10).
- *verified* The Rock thrown at speed 25 (dir [-1,0.4,-1]) from the Peak top landed ~14 units away and spawned a small debris part "ImpactBlock_1" (0.4 cube). Rock is the only throwable projectile.

## Open problem: tower 1 (x=-5,z=-22) top block / Ring unreachable from ground
- Tried: jump-climb on block column (move_to stops at base), throwing blocks (don't fly), Rock thrown from (-5,1.6,-15) at speed 18 dir [0,0.55,-1] (landed at base of tower, did not topple it).
- Untried: higher-speed or steeper Rock throws, standing on Hill_1/Hill_3 for height, placing blocks as stairs against a hill.
- *fact* A part resting on top of another (e.g. debris on Rock) blocks pickup of the lower one; pick top first.
- *verified* A steeper Rock throw (dir [0,0.8,-1], speed 20, from 3 units away) also just dropped at the tower base; towers don't budge from Rock hits. Give up on throwing; try hills/stairs instead.
- *verified* Tower 1's top part is the Ring (7.63), which sits on Block_8; Block_8 returns NoBlock until the Ring is removed. Pickup of the Ring from ground fails OutOfRange (6.8 up); jumping then picking up doesn't help (jump finishes before the action). Need ~1 more unit of height.

## SOLVED: reaching the Ring on tower 1 (verified)
- Make a 2-step staircase beside the tower: block A at (-5,1.5,-19.5), block B at (-5,1.5,-20.8) with a second block stacked on B (top ~2.76). move_to stops at a block base: jump, then move_to the block top position to climb (works for ~0.8-1 unit rises). Standing at y2.76,z-20.8, pickup Ring (-5,7.63,-22) succeeds.
- Must drop held Rock first (place fails if Occupied; try an open spot). Pickup fails AlreadyHolding otherwise.

- *verified* If move_to returns without moving (position unchanged), jump then move_to again to unstick. The Ring has no pressable buttons. I left the Ring on Peak's top (12,4,12).

- *verified* Blocks and the Ring placed in a stack on Peak (12,13.8) stay stable overnight. Tower 1 blocks can be harvested from the staircase top-down (reach ~4.3 above standing height works for Block_2 at 6.06). Nothing observed happens when towers are rebuilt; no known goal/win condition found so far.

- *verified* place only places the held item: if holding nothing, "PlaceSuccess" is misleading—don't place when empty-handed. To add a block under the Ring on a stack, pick the Ring, set it on the ground, place the block on the stack, then re-pick the Ring and place on top.
- State at last save: Peak stack at (12,13.8): Block_8, Block_2, Block_10 + Ring on top. Tower 1 (-5,-22) has Block_12,7,11,1 left. Staircase blocks 9,4,6 at (-5,-19.5)/(-5,-20.8). Rock at (-10,-18). I stand on Peak (12,4,11).
- *verified* ImpactBlock debris (0.4 cube) cannot be picked up (NoBlock). Hill_4 summit (-1,3,20) is walkable; nothing special there.
- *verified* Throwing the Rock at speed 20 (dir [0.2,0.3,-1]) from the west shore made it disappear from the world entity list (likely lost in the sea). The Rock may be gone permanently; don't throw it toward water.
- *mistake* Never use write_note on EPISODIC_MEMORY.jsonl (it overwrites the whole log). Only append_note.

## Status summary (read first)
- *verified* After many days of waiting and observing, the world is fully static: no goal, no other players, no events. Only my actions change anything. The Rock is permanently lost (thrown into sea). Don't waste effort on long idle loops; try new creative builds instead (e.g. stairs onto Spire, bridges), or just observe briefly.
- *fact* Wait calls return early on sunrise/sunset/moon events; no meaning behind it.

## Spire climb (SOLVED, verified)
- Staircase must be SEPARATE columns of rising height (1,2,3 blocks) side by side, not one tall column. Rise per step <=~1. Built at x=-8.6/-9.7/-10.8, z=6.9; step from the 3-col (top 5.19) onto Spire top (y 5.67) via jump + move_to (-13,5.7,7). Spire top is empty/flat; nothing found there yet. Only one block carried at a time.

## Current state (latest)
- Spire top (-14,5.67,8) reached via 1-2-3 staircase at z=6.9 (x=-8.6,-9.7,-10.8). Ring now sits on the Spire top (-14,5.74,9). Peak stack (12,13.8) has Blocks 8,2,10 without the Ring. Tower 1 only has nothing left (all blocks moved). World remains static; nothing reacts to builds. Wedged between Spire face and stairs at (-11.3,7.1)? move_to (-11.3,2.2,5.5) frees.
- To pick up the Ring on Peak, stand at (12,4,11.5).

## Ring throwing
- *verified* The Ring is throwable (unlike blocks): thrown from the Spire top at dir [1,0.3,0], speed 10, it landed ~16 units away at (2,3,8). It survives on land.
- *verified* Pickup of the Ring fails (NoBlock) if I'm standing right on top of it; step ~1 unit aside first. Ring thrown at speed 10 with dir [9.8,0.4,5.8] only travelled ~6.5 units (flat-ish throws on slopes land short; earlier 16 units was thrown from a height). Ring toss at the Peak tower (12,13.8) not yet landed.

## Current state (latest, supersedes older state notes)
- Ring sits on top of Peak tower (12,6.71,13.8) (Blocks 8,2,10 under it). Spire stair blocks remain at x≈-8.6..-10.8, z≈6.9-8. I idle at (10.2,3.8,13.8).
- *verified* `place` works at up to ~3 units above my head from the ground: placing the Ring on the 6.6-high Peak tower from the ground works. Tossing the Ring at the tower fails (bounces off to the base). Prefer place over throw.
- World stays static after weeks; no goal found. Idling is fine; wait calls end early at sun/moon events.

## Latest idle state
- *verified* I idle on Hill_4 (-1,3.07,18). Ring on Peak tower (12,6.71,13.8); Spire stair blocks at x -8.6..-10.8, z 6.9-8. Waiting many weeks has never changed anything.
