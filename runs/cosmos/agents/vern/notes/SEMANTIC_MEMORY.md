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
