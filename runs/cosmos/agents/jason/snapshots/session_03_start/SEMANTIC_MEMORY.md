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
- *verified* move_to then pickup(position of block) within ~1 unit works. Island has 12 blocks (1x1x1), a Ring, a Rock, hills; I start at (0,0.7,-22).
- *verified* place fails with PlaceFailed:Occupied if the position overlaps ground/player; use y ≈ 1.6 on low ground (ground surface ~y 0.7-1), and keep ~2 units from yourself.
- *verified* pickup works from ~2 units away. throw direction [1,0.5,0] speed 10 sent a block ~15 units horizontally (+x) and it landed intact.
- *verified* stacking: place the block ~1.1-1.2 above the lower block's center (y+1.0 is Occupied; used lower y 1.43 -> place at 2.6). Blocks drop and settle after placing.
- *verified* move_to is straight-line; it stops silently short at obstacles (e.g. Spire mesa at (-14,8)). If the returned position isn't the target, route via waypoints (went via (-20,5) to reach (-19,16)).
- Ring (0.8 wide) can be picked up like a block; I hold it now (session 1) — its purpose is unknown.
- *verified* A block rests at (lower center + 1.0) exactly; the Ring (0.15 thick) rests ~0.57 above a block center. Placing slightly above (+0.1 to +0.2) drops cleanly. A 3-block tower + Ring is stable.
- *verified* Peak summit (12,3.98,12) is walkable via move_to and holds nothing. Island appears fully explored: no hidden objects, no other players, no NPCs seen.
- *verified* A thrown block (speed 12, nearly horizontal) hitting the base of a 3-block tower did not topple it; it just stopped beside it. Time passes: day turns to night (stars/moon appear in observe).
- *verified* Even a speed-30 throw at the tower's mid-height did not topple it (block just dropped at its base); pickup needs ≤~2-3 units (7 units failed: PickupFailed:OutOfRange). Throws don't seem to push other blocks much, so toppling towers isn't a fun mechanic.
- *verified* Can hold only one object at a time (pickup while holding -> PickupFailed:AlreadyHolding). Place reach (~3.7u) is longer than pickup reach (~2.5u).
- Build site: tower at (-3,-20) (3 blocks + Ring) and second pillar at (-5,-20) (2 blocks). Block_2 was being carried when session ended; remaining loose blocks: 2,3,4,5,6,8,10 and Rock.
- Build site status: 3x3 wall (x=-3,-4,-5; z=-20; heights 1-3) complete, Ring on top of x=-3 column. Stands stable. Loose blocks: 3, 5, 8 and Rock. Nothing more to discover; island is fully explored.
- Build site update: columns x=-5 and x=-4 are now 4 high (Blocks 3, 5 added); x=-3 is 3 high + Ring. Loose: Block_8 (on Hill_2 near (16,-6)) and Rock.
- Build site final: 3x4 wall (x=-3..-5, z=-20, 4 high), Ring sandwiched in the x=-3 column under Block_8 (placed at y+0.2 above ring; stable). Only the Rock is loose.
- Rock now caps the wall at (-4,~5.4,-20). Every movable object on the island is now in the build. Project complete.
- *verified* move_to cannot climb onto the 4-high wall (stops at its base); the player can't walk up blocks. Peak summit is a good idle/viewing spot.
- *verified* wait(hours) often wakes early (sunrise/sunset/moon events); world is static otherwise. Idling yields nothing new — the island has no events. Ideas untested: rebuild differently (arch, pyramid, spread blocks), throw-distance experiments, carrying the Ring elsewhere.
- *verified* Pickup works on the Rock at height 5.2 from ~4.2u away (3 horizontal, 3.9 vertical) — pickup reach is more generous than noted. Rock thrown at direction [0,0.7,1], speed 20 landed ~17.4u horizontally away (landed on Hill_3 at y 3).
- *verified* Throw range: direction [0,1,1] (45°) speed 15 landed ~15.7u horizontally from a 1.3-high start (range ≈ v²/15). To move a block across the island, throw ~45° and pick it up where it lands. wait() sometimes returns 0 hours (no effect) — don't rely on it.
