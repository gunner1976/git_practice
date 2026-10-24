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
- *verified* move_to near a block (within ~1-2 units) then pickup with its exact position works (PickupSuccess).
- *fact* World: small island with hills, 12 loose Blocks (1x1x1), a Ring, a Rock. Start around (0,0.7,-22).
- *mistake* place at low y (1.0-1.5) fails "Occupied" (ground/terrain overlap). Place at y~3 worked (block drops).
- *verified* throw direction [1,0.5,0] speed 10 sent a block ~14 units along +x (x from -9 to 5.5). Direction is world-space, +x = east.
- *mistake* move_to can silently stall against a block (position unchanged, still "Ready"). Fix: jump, or route via an intermediate waypoint around it.
- *verified* Rock is pickup-able too.
- *verified* throw [0,0.3,1] speed 20 with the light Rock went only ~12 units along +z (landed on a hill, which may cut it short). Range isn't simply proportional to speed; terrain matters. +z = south/forward.
- *verified* Ring (far SW corner, ~(-19,1,18)) is pickup-able; it has no "use" button (press -> NothingInReach). Long move_to across the island works in 2 waypoints.
- *verified* Placing drops the item from the given position; placing a block above another item stacks it on top (Block on Ring ended at y~1.76 over ring y 1.18). Stacking works for building.
- *verified* Tower building: stand ~1.5 units from the column, place at the same x,z with y a few units above the top; blocks land flush (1.0 spacing) and stay stable. 3 blocks + Ring stable so far.
- *verified* A 5-block tower (+Ring base) stays stable; place still works from the ground at y up to 7.5 (no reach limit seen for place). Island nightfall happens ~every 8 sim-hours of ticks; time jumps between observations.
- *fact* The Spire mesa at (-14,8) blocks movement in a straight line (move_to stalls at its edge). Route around it via e.g. (-8,12) -> (-4,0) -> north. Straight lines between SW corner and north area hit it.

## Current project / state (may be stale)
- Tower at (-18.5, y, 16) in SW corner: Ring base + 5 blocks (Block_3,5,6,4,9). Was carrying Block_11 (brown) toward it. Remaining loose blocks: 1,2,7,8,10,12 + Rock.
- Workflow loop: observe -> move_to (waypoints) -> pickup exact pos -> move to (-17,1.2,16) -> place at (-18.5, top+1.5, 16).
- Tools never verified: press on other objects (only tried Ring: nothing). Idea: test throw range at multiple speeds on flat ground.
- *verified* Place has a reach limit: from ground (y~1.2, 1.5 units from target) placing at y=8.5 -> PlaceFailed:OutOfRange, y=7.0 OK (roughly <=6-7 units above me). To build taller, I'd need to climb (e.g. stand on the tower/blocks) or jump.
- Tower is now Ring + 6 blocks (added Block_11 brown).
- *verified* Place reach from ground: y=7.8 OK, y=8.5 fails. Limit ~8 above ground / ~7 above my feet. Tower now Ring + 7 blocks (Block_1 red added).

## Moon
- *fact* The moon rises in the east (azimuth ~78°) roughly 6-7 sim-hours after waiting from daytime; observe's sky field shows it. Apparent size ~1° (a distant celestial body). No known way to reach it; a block tower (~8 units) is hopeless. *hypothesis*: unreachable by design.

## Interaction limits
- *verified* pickup of the top tower block from the ground fails OutOfRange (reach is short vertically); press "use" with nothing held/nearby gives NothingInReach. Blocks seem to have no buttons.

## Tower status
- *verified* Tower (Ring + 7 blocks, top y~7.76) is at the place-reach limit; placing at y=8.8 from the ground fails OutOfRange. To go higher I must stand higher (e.g. build a stair of blocks beside the tower and climb). Route to fetch far blocks: (-8,1.5,12) -> (-4,1.5,-10) -> (-4,1.5,-21) works without stalls.

## Climbing
- *verified* Player cannot climb onto a 2-block-high column (jump + move_to stalls at its base). 1-block steps are untested. A stair would need 1-unit increments, using many blocks.

- *verified* A 1-block step is climbable (jump then move_to onto it). Standing on one block raises place reach by ~1: tower grew to Ring + 8 blocks (top y~8.76) by placing from atop Block_12 at (-16,1.8,16). Further growth needs a taller stand, i.e. a stair of 1-unit steps.

## Current project state (may be stale)
- Tower at (-18.5,16): Ring + 8 blocks (top y~8.76). Stair beside it: Block_12 at (-16,16) and Block_2 at (-17,16), each 1 high. Plan: stack another block on Block_2 (2 high), climb from Block_12, place more on the tower. Remaining loose: Block_8 (~16,-6), Rock (~8,2); I was holding Block_10 in the NE when last active. Moon is considered unreachable; this is just a build project.

- *verified* Stair works: ground -> Block_12 (1 high at (-16,16)) -> 2-high column (Block_2+Block_10 at (-17,16)); each step is one jump + move_to. Standing on top gives y~3.24. Need to carry a block up there (hold it while climbing) to place higher on the tower. Remaining loose: Block_8 (~16,-6), Rock.

## Rock
- *verified* Throwing the Rock straight up [0,1,0] speed 30 just drops it back at my feet and spawns small 0.4 "ImpactBlock" debris parts. Nothing launches skyward; the moon cannot be reached by throwing.

## Status summary (latest)
- Tower at (-18.5,16) is Ring + 10 blocks (top y~9.76); all 12 blocks used. Nothing left to build with. Moon unreachable (tower, throwing, waiting all tried). Next session: try something new (e.g. explore unvisited terrain, press buttons on other things) instead of idle waiting.
- *verified* Island NW edge: move_to (-20,1.5,-20) ends near (-14.8,-0.4,-17.9) (shore, y drops below 0). The NW corner is empty. Late-session wait() sometimes returns 0.0 hours elapsed.
- *verified* NE (20,-20) and SE (~20,14) shores are empty too; the island has no hidden objects beyond the 12 blocks, Ring, Rock.

## Peak
- *verified* Peak summit (12,~4,12) is reachable by move_to and is the island's highest ground; nothing is there and the view reveals no new entities (observe is global anyway).

- *verified* Throwing the Rock at direction [0,1,-0.2] speed 100 landed it only ~5.5 units away (and spawned ImpactBlock debris). Throw speed is effectively capped; no throw reaches the sky.

## Press (re-verified)
- *verified* press "use" while holding the Rock gives NothingInReach too. No object on the island has a button; stop trying.

## Rock (update)
- *verified* The Rock thrown east from (8,-1) at speed 15 disappeared from the entity list (likely flew off the island/despawned). Don't throw things you want to keep.

## Island edge
- *verified* East shore: move_to toward x=40 stops at ~(20.6,-0.6,-1); an invisible boundary blocks further travel. You can't leave the island.

## Strategy (read first)
- *verified* The world is fully static: no other players, no events, no hidden objects. Idle waiting (many sessions) never produced anything. Don't wait expecting change; only try genuinely new experiments, otherwise stop early.
- Untested ideas: dismantling the tower and rebuilding differently; throwing blocks at the tower; standing on top of the stair and jumping toward the tower.

## Tower climbing (verified)
- *verified* Jumping from atop the 2-high stair (y 3.24) toward the tower column does not get me onto it; I slid down to the ground beside it. The tower is not climbable.

## Tower collapse (verified)
- *verified* Throwing a block at the tower (from (-17.9,1.16,16), direction [-1,0.2,0], speed 20) knocked it apart: now a 5-block column (Block_3,5,6,7 + Ring) at x=-18.5, a second column at x=-20 (Blocks 4,9,1,8), and the stair at x=-17 stacked 4 high (Blocks 2,10,12,11). The tower is no longer 10 high. Blocks are physical and fragile when hit; don't throw near a tower you want to keep.

## Current state override
- The "Tower status/Current project/Status summary" sections above describe the old 10-block tower, which no longer exists (see Tower collapse). Current layout: columns at x=-18.5 (4 blocks on Ring), x=-20 (4 blocks), x=-17 (4 blocks). Rebuilding is optional; it achieves nothing for the moon.

## Spire (verified)
- The Spire mesa (~3.5 high) can't be climbed directly: move_to + jump stalls at its south edge (~(-15.1,2.4,10.3)). Would need a block stair of 1-unit steps (blocks are at the SW tower area).

## Spire (update, verified)
- Spire top is y~5.67 (ground ~1.7). Built a 1/2/3-block stair at x=-14, z=13.5/12.5/11.5 (still standing); climb with the loop: jump, then move_to 1 unit further at next top height (repeat x4) -> reach summit. Nothing is on top yet to see (check).
- Only the TOP block of a stack can be picked up, but reach vertically works up to y~4.5 from the ground.
- If move_to stalls wedged beside blocks and the spire, move sideways in x first, then go round.
- *verified* Carrying a block up the Spire stair and placing it on the summit works (Block_6 now at (-14,~6.2,8)). Possible: build a tower up there for extra height, but the moon is still out of reach in principle.

## Latest layout (read first, supersedes older layout notes)
- Spire summit (-14,5.67,8) holds a 2-block stack (Blocks 6,7). Stair columns on its south face at x=-14: z=13.5 (Block_8), z=12.5 (Blocks 1,9), z=11.5 (Block_4). Old columns near (-17..-20,16) partly dismantled. Player usually stands on Spire summit.
- Waiting on the summit through many sun/moon cycles still yields nothing; world is static. Wait() wakes on sunrise/moonrise/moon-light changes.

## Throw from height (verified)
- Block thrown from Spire summit (y 5.67) direction [1,0.3,0] speed 20 landed ~16 units east (x -14 -> 2). Block_7 is now at (2,3.4,8.6), no longer on the summit.
- Throw [1,1,0] speed 20 from summit landed ~17.6 east (Block_6 at (3.6,3.6,8.6)); barely farther than a flat 0.3-slope throw. Throw range seems capped ~16-18 at speed 20; both summit blocks (6,7) are now out on the east plain near x=2-3.

## Latest layout (newest, supersedes earlier layout notes)
- Blocks 6 and 7 are stacked as a 2-block monument on the east plain at (3.58, z 8.6); the Spire summit is empty. Other blocks: Spire south stair (x=-14, z 11.5-13.5) and SW columns near (-17..-18.5,16).
- Many more sessions of waiting (sun/moon cycles) on the east plain: world static. Wait often returns early on sunrise/sunset/moonrise/moonset. Don't repeat; only try genuinely new experiments.

## Sky (fact)
- At night observe's sky lists named stars (star_07 etc.) with azimuth/elevation; they are just sky decorations, same unreachable class as the moon.
