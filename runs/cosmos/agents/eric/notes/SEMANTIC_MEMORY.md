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
