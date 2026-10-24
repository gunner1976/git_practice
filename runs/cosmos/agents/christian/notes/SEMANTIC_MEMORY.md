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
