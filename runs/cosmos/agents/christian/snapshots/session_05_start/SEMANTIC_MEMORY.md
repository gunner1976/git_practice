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

## Actions
- *verified* move_to next to a block (within ~1 unit), then pickup at the block's position works.
- *fact* World: island with hills, 12 blocks, a Ring, a Rock. Start at (0,0.7,-22).
- *verified* place at y≈1.2 fails with "Occupied" (inside terrain); y=2.0 succeeded. Place a little above the ground and let it drop/settle.
- *verified* Placed blocks fall under gravity and stack (blocks are 1x1x1, unanchored). Ground near (-3,-20) is at y≈0.9. Stacking by placing above the stack works.
- *verified* place has a max reach (~6.5 units from me): y=8.0 from a standing height of 1.15 gave OutOfRange; y=7.6 worked. For taller towers, build a second stack/ramp to stand on, or place beside.
- *mistake* move_to straight through the Spire mesa (-14,8) stops short silently (result still "Ready"). Route around via waypoints, e.g. (-19,1.5,6), then the target. Always check returned position.
- *verified* Ring at far SW corner (-19,18) can be picked up.
- *verified* Peak summit (12,12) is at y≈3.98, walkable; nothing special there. Day/night cycle exists (night with moon and stars); the 7-block tower stays stable.
- *verified* throw direction [0,0.5,-1] speed 10 from (5.4,3.4,8.2): block landed ~16 units away at (5.4,2.9,-7.7). Direction is world-space; -z is "forward" toward the tower side.

## Index (added)
Actions (place/pickup/move_to/throw), building, world layout — all in "Actions" bullets above.
- *verified* Throw [0,0.55,-1] speed 12 from (-3,1.9,-12) landed at only (-3,1.6,-18.8) (~7 units, probably hit terrain/slope). Throw range depends on terrain; it did not topple the 7-block tower (tower blocks are stable).
- *fact* Persona note: my name is Eko (the SOUL file's "Christian" line conflicts; Eko is the in-world name).
- *hypothesis* To build taller than ~7 blocks, stand on a stack of blocks/hill and place above; untested.
- *verified* Jump then move_to onto a 1-high block lets me climb on top of it (stood at y≈2.07 on a block resting on ground y≈0.9). Stairs of 1-block steps are climbable; this should extend place reach upward.

## Moon mission
- *verified* Ring has no pressable buttons (press -> NothingInReach); throwing it straight up at speed 50 just drops it back. Time advances ~80 min per few actions; moon was below horizon in daytime.
- *hypothesis* Moon cannot be reached by stacking the 12 blocks; check sky.moon direction at night before more attempts.
- *mistake* After pickup/throw near the tower I got wedged against blocks: move_to returned Ready but position didn't change. Fix: jump, then move_to a nearby waypoint.
- *verified* Rock has no buttons either. Throwing it straight up at speed 100 left it at my feet and spawned two small 0.4 "ImpactBlock" debris parts nearby (cause unclear; throw seems to hit something low overhead or fall right back). Nothing that helps reach the moon.
- *verified* Moon rises in the east (azimuth ~80°, elevation grows ~7° per ~30 min world time) in the late afternoon (~16:45 world time) while sun still up; observe.sky.moon gives azimuth/elevation. Moon is huge (1° apparent) but unreachable: a rock thrown at it at speed 200 landed ~12 units away on the ground (throws are heavily capped). Waiting ~8 move_to calls ≈ 80 min world time.
- *verified* Spire mesa walls (~3.5 high) can't be climbed by jumping alone; move_to up it stops at its foot (y≈2). Needs a block stair. Not worth it for the moon mission.
- *fact* Persona: SOUL.md says my name is Christian (use that).
- *verified* move_to from the Spire's west side toward the south (-12,18) gets blocked by the mesa; route via (-19,1.5,12) first. Stair-up-Spire attempt: block placed against wall at (-16.5,~2.4,6), another placed nearby at (-16.5,~4,7.2); Spire top not yet reached (unneeded for mission).
- *fact* Mission "reach the moon" appears infeasible: moon rises east late afternoon, reachable height/range is ~12 units. Don't spend more sessions on it unless a new mechanism is found.
- *fact* Spire stair needs ~4 stacked blocks beside the wall (top ≈5.7, ground ≈0.9); only 2 blocks are near it, the other 10 are at the tower (-3,-20). Carrying seems one at a time, so it's ~10 trips; judged not worth it.
- *verified* Carrying is one block at a time (pickup fails AlreadyHolding). Route tower->Spire: (-5,1.5,-18) -> (-19,1.5,0) -> (-17.5,1.5,6).
- *mistake* Stair steps must be ≤~1.0 high. Standing height on ground ≈1.5, block top ≈2.6 (1.1 up): jump+move_to onto it fails. Stacking blocks as a column gives no usable steps; need a half-height first step (e.g. put the first block on a slightly raised spot) or a staggered staircase where each step is ~0.9 above the last. Column of 3 blocks stands at (-16.5,*,6) against Spire wall.
- *verified* Wedging between a placed block and the mesa wall makes move_to a no-op; picking up the adjacent block alone didn't free me, but a short move_to away from the wall (west) did. A 0.15-high Ring used as a first step (stand 1.6) still failed to reach a block top at 2.6. Next idea: use the Rock (0.6 high) at (21,-7.6) as the first step.
- *verified* Rock placed on top of the Ring forms a first step: from ground, jump+move_to onto it works (stood y≈2.2). But from the rock, jump+move_to onto the adjacent block top (2.6) still no-ops (position unchanged) even though the rise is only ~0.4, so the blocker is likely move_to refusing targets overlapping/adjacent to a block, not jump height. Untested: walk off via move_to to a target slightly above the block (y 3.5) from 2+ units away, or build a gentler ramp.
- *verified* Climbing recipe: a Rock (0.6 high) placed on the ground gives a first step (jump, then move_to its top works, stand y≈2.2). Approach steps along a clear line; a step placed in the straight path between me and the target blocks move_to (stops short), so approach from a direction without obstacles. Current setup: Rock at (-16.5,*,4.9) south of 3-block column at (-16.5,*,6) against Spire wall (x=-16.5). I'm standing on the Rock; next try: jump + move_to (-16.5,2.7,6.0) (block top 2.6), then 3.6, 4.6, then mesa top 5.7.
- *mistake* Leave no gap between step and block: a Rock 0.25 away let me fall into the gap. Even flush against the column (Rock at (-16.5,*,5.1), me on it at y 2.22), jump then move_to onto the block top (2.6) leaves me in place. The jump seems to land before move_to starts, so move_to just walks into the wall. Climbing blocks only worked once, from an approach where ground was ~1.5 and target within ~1 high. Stop trying to climb this column; consider a new idea (e.g. place blocks while standing on the rock, building up under me).
- *verified* place at my own position fails (Occupied), so I cannot raise myself by placing blocks under my feet. Pickup reach from y 2.2 covers a block top at y 4.1.
- *verified* Wedge fix: when move_to is a no-op, call jump, then move_to in the same batch to a point away from the blocks; it frees me.
- *verified* Hill_4 summit (-2,2.9,20) is walkable; nothing special there.
- *verified* East side (x>14 at z=20, x~21 at z=2) is low ground at y≈-0.75 (below the usual 1.1 level, maybe shoreline/water); nothing found there.
- *mistake* Heading to x>20 on the east side puts me at y -0.75 then -1.5 (sinking into a slope/sea edge) and move_to stalls. Stay at x<=18; recover with jump + move_to toward the island center (12,3,1).
- *verified* North edge (z -20 to -24) is walkable, ground y 1.07 falling to 0.35 near the start point; nothing found. The whole island perimeter is now explored with no special objects.
- *mistake* Pickup of tower blocks at (-3, 1.43..8.43, -20) returns NoBlock (or OutOfRange for the top) even when standing 1 unit away, though observe lists them there and I'm physically blocked by the tower. Cause unknown; maybe the tower is stale/locked. Hauling blocks from the tower to the Spire is therefore not currently possible.
- *verified* Pickup/place still work for loose blocks near the Spire (Block_3 picked up from 1.5 units away and replaced), so the tower pickup failure is specific to the tower (cause unknown).
- *verified* Climbing a single block from ground works: ground here is ≈1.45, a block placed on it tops at 2.45; jump then move_to its top (from ~1.5 away) puts me on it. The Spire stair needs a true staircase (separate stacks of 1,2,3,4 blocks = 10 blocks; stacked columns are no use because upper blocks cover lower tops). Only 3 loose blocks near the Spire, so Spire top is infeasible unless tower blocks become pickable.
- *verified* Tower pickup also fails from the east side (-1.8,*,-20); pickup of the tower is NoBlock from every side tried (south, east). Stop retrying.
- *verified* Throwing the Rock at the tower (speed 30, from 6 units) does not dislodge or free the tower blocks. Tower idea closed.
- *verified* press next to the tower returns NothingInReach: tower blocks have no buttons.
