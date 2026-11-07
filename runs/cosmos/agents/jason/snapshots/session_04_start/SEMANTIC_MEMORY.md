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
- *verified* Rock thrown at direction [-1,1,-1] speed 30 landed at the island center (0,2.9,0), ~17u away, and spawned two small "ImpactBlock" debris parts (0.4 size) beside it. Hard impacts create debris, so throws can produce new objects. Rock can be moved from the wall top freely (wall stays stable).
- *verified* A speed-20 Rock throw (landed ~15u away on Hill_4) produced no debris; the debris at speed 30 likely needs a hard/high-speed impact (hypothesis: threshold between 20 and 30). Fall from a high start (Peak, 4u) may also matter.
- *verified* Debris is tied to the LOCATION, not (only) speed: the Rock landing at the island center (0,2.88,0) twice (speeds 30 and 26) each spawned a new ImpactBlock (0.4 size, now 3 exist near center). Landing elsewhere (speed 20, Hill_4) spawned none. Hypothesis: the center spot (0,0) is a special target/hit zone. Next: test a slow throw landing on (0,0), and see if ImpactBlocks are pickup-able/stackable.
- *verified* ImpactBlocks are normal pickup-able, throwable objects. A slow throw (speed 5) of one landed near (0,-2) and created no further debris (so no debris from slow/small impacts).
- *verified (correction)* Debris is speed-driven, not location-driven: Rock thrown at speed 26 toward -x landed (-16,2,3) and spawned 2 ImpactBlocks; speed 20 spawned none, speed 5 none. Threshold is between 20 and 26 (impact speed). Each hard Rock impact spawns 1-2 small 0.4 ImpactBlocks, which are pickup-able. Ignore my earlier "center spot" hypothesis.
- *verified* A near-flat throw (direction [0,0.05,-1], speed 24) from 10u away hit the ground ~9u out, short of the tower at 10.5u; flat throws lose ~1.5u of range per 10u to drop. Aim slightly higher (~0.1-0.15) for direct hits. Tower unaffected, no debris.
- *verified* A Rock thrown from 10u, direction [0,0.12,-1], speed 28 scored a direct hit and scattered the 5-ImpactBlock tower (no debris). Light 0.4 blocks topple; heavy 1.0 wall blocks did not at speed 30. So toppling needs a light target and an accurate throw (aim ~0.12 up at 10u).
- *fact* Current layout: 3x4 wall at (-3..-5,-20) with Ring inside (no Rock). 5 ImpactBlocks + Rock were scattered near (0,-0.5) after I toppled them; positions drift, so observe before pickup (PickupFailed:NoBlock means stale coordinates).
- *idea* Rebuild the ImpactBlock tower and repeat the knock-down throw game (aim ~0.12 up at 10u, speed 28).
- *fact* Pickup uses the object's position as listed in observe; one PickupFailed:NoBlock happened at y 2.78 even though a block was listed nearby, while y 3.18 on the same stack worked. If a pickup fails, re-observe and try the neighboring block or move closer.
- *verified* PickupFailed:NoBlock can occur when another object (e.g. Rock) rests on top of the target; pick the top object first.
