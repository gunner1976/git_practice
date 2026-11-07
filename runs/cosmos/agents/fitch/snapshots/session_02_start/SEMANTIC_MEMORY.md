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
