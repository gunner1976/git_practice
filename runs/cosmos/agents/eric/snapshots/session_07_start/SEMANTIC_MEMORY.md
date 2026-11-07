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
- *verified* move_to near an item (within ~1 unit) then pickup at its position works.
- World: island with hills, 12 loose 1x1 blocks, a Ring, a Rock. Start at (0,0.7,-22).
- *mistake/unknown* place near me at ground level (y 0.5-1.5, within ~2 units) returned PlaceFailed:Occupied three times; cause unknown (try farther/higher spots or different yaw). throw (direction, speed 5) works.
- *verified* Fix for PlaceFailed:Occupied: place at a higher y (e.g. 3.0, ~2 above ground); low y values are likely inside terrain. Block then drops/settles. Placing ~1.7 units away worked.
- *verified* Stacking works: place ~1 unit above the top block's center and it settles on it (blocks are 1x1x1, unanchored but stable). A 3-block tower succeeded.
- *verified* move_to can stall when a mesa (Spire at -14,8) is in the straight path: position stays unchanged. Route via waypoints (e.g. via (-21,1.2,8)) to go around.
- Tower site: column at (-8.5, y, -16.5): 5 blocks plus Ring on top.

## Building Projects (state may be stale; re-observe)
- Tower 1 at (-8.5, y, -16.5): Blocks 7,12,11,1,10 + Ring on top (stable). Tower 2 at (-10.5, y, -17.5): Blocks 6,5,3 (3rd unconfirmed).
- Efficient loop: move_to near block, pickup, move_to (-10.5,1.3,-15.5), place at x,(top y + ~1.2),z. Always route around Spire via (-21,1.2,8) when going south<->north on west side.
- Remaining loose: Block_2,4,8,9, Rock. Idea: continue tower 2 or build a wall.
- Observe only occasionally; place calls reliably succeed with y ≈ top+1.2.
- Update: Tower 2 now confirmed 4 blocks (6,5,3,4), stable. Remaining loose: Block_2, 8, 9, Rock (all on the east/south-east side).
- Update: Tower 2 now 6 blocks (6,5,3,4,2,8), stable, top ~6.7. Only Block_9 (5.46,3.8,7.18) and Rock (8.93,2.86,-10.38) remain loose.
- Update: All items now placed. Tower 2 = 7 blocks (Block_9 on top). Rock sits on Ring atop tower 1. Place has a max reach: y 9.1 from ground failed OutOfRange; y 7.9 worked.
- verified: move_to straight from tower site to Peak summit (12,4.2,12) works; summit y≈3.98. Nothing else of interest found there.
- fact: Lunar eclipses happen (observed one reach totality, darkened_fraction 1.0, visible in observe sky.moon.eclipse). wait() wakes early on sky events (moonrise, sunset, moon light change).

## Current World State (re-observe to confirm)
- All 12 blocks, Ring, Rock placed in two stable towers at (-8.5,-16.5) [5 blocks+Ring+Rock] and (-10.5,-17.5) [7 blocks]. No other players seen. Towers survive days of waiting. Standing spot for placing: (-10.5,1.3,-15.5). I usually end up idle on Peak summit (12,3.98,12).
- *verified* pickup has a max reach too: a block at y 7.7 was OutOfRange from the ground, so tall towers can't be dismantled from the top without a boost.
- *unverified* Pickup at Block_2 (y 5.68, tower 2, from (-10.5,1.37,-15.5), just after a jump) returned NoBlock instead of OutOfRange; meaning unclear (maybe position must match more exactly, or the jump shifted things).
- *verified* Pickup of stacked blocks in tower 2 (Block_2 at y5.68, Block_6 at y1.68) gives NoBlock even from 1.5 units away; only the top block gives a range error. Stacked blocks are probably unpickable (or sealed in by neighbors). Don't waste time dismantling towers.
- *verified* The island's west edge is near x≈-14 at z≈-17: moving toward (-30,1,-20) stopped at (-14.4,-0.56,-16.8) (shore, y below 0). No need to explore west of there.
- *verified* Southeast edge: move_to (30,1,30) stops at about (17.6,-0.8,16.4) (shore). Island is roughly x -14..+20, z -20..+20.
- *verified* North edge near (2.7,-0.65,-27). Moves to targets beyond the shore stop at the shore; from the SE shore (17.6,-0.8,16.4) a move toward (0,1,40) did not move at all (start at shore, go inland first).
- *verified* South edge near (0,-0.7,29). Island spans roughly z -27..+29, x -14..+18+ (east edge not checked). Mapping done.
- *verified* East edge near x=20 (z=0). Island fully mapped: x -14..20, z -27..29.
- *verified* speak works but returns NobodyHears (no other players exist). throw with empty hands fails EmptyHands. wait sometimes returns 0 hours immediately (time seems to stall); nothing to do about it.

## Throw experiments
- *verified* The top item of a tower (Rock, y 6.8) can be picked up from the ground next to it (-8.5,1.6,-14.5). Throw dir [1,0.5,0] speed 15 landed the Rock ~14.5 units away (and ~0.7 lower). Rock is now loose at about (6,2.3,-14.5), not on the Ring.
- *verified* Placing Rock at y 7.1 above (-8.5,*,-16.5) settles it back on the Ring (y 6.82). Rock can be moved off/on the tower freely; it's the only tower item pickable from the ground.

## Idle behaviour
- *verified* wait(12) usually wakes early on sky events (sunrise/sunset/moonrise/moonset), returning 0.2-9 hours. Repeating it is safe; the world is static without other players.

## Session habits
- *verified* After a reset, the first observe shows me on Peak summit (12,3.98,12) and the world unchanged; towers persist across resets. wait(12) returns early on sky events (0.2-10 h).

- *verified* Throw speed 30 at dir [1,0.3,0] landed Rock only ~12.5 units away (less than speed 15 at 0.5 slope); speed isn't linear in range—a higher arc matters more. Rock restored on Ring afterward.

- *fact* Idle sessions: world is static, no other players ever. Long wait(12) loops just burn turns; nothing changes. If bored, try new experiments (throw arcs ~45° for max range, new tower sites).
