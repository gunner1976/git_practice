# SEMANTIC_MEMORY.md - What I Know and I Can Do

## Index
Tools & basics; Placing/stacking; Throwing (blocks, Rock, Ring); Builds

## Tools & basics
- *verified* write_note OVERWRITES. Use append_note to add; to edit, read first then rewrite whole file.
- *verified* Island: 12 blocks (1x1x1), Ring, Rock, hills, Spire mesa (-14,8), Peak (12,12). Fully explored: no NPCs, no other players, world is static unless I act. Waiting yields nothing.
- *verified* move_to is straight-line and stops silently at obstacles (pillars, wall); use waypoints. Can't climb onto blocks/wall. Peak summit (12,3.98,12) is walkable.
- *verified* pickup reach ~2.5-4u (more generous vertically); holds one object only (AlreadyHolding; to grab another, place the first somewhere free, e.g. y+1.2 above ground at ~2u away). NoBlock => stale coords or something rests on top; re-observe, pick top object first.
- *verified* wait() often wakes early or returns 0 hours.

## Placing / stacking
- *verified* Place fails (Occupied) if overlapping; place ~+0.1-0.2 above resting height. Block rests at lower center +1.0; Ring ~0.57 above block center. Place reach ~3.7u.
- *mistake* Arches (lintel over gap between pillars, gaps 0.2-0.5) failed 3 times: lintel slides onto the -x pillar. Don't retry.
- *mistake* ImpactBlock (0.4) pyramids/caps slump: a second row on a 0.5-spaced base row and the Rock cap collapsed immediately on the last attempt. Only plain vertical 0.4-block stacks (5 high) stayed up; use those for knock-down targets.

## Throwing
- *verified* Blocks: range ≈ v²/15 at 45°; speed capped (~15u max; speed 40 gives same). To relocate objects, lob at 45° and pick up where it lands.
- *verified* Rock thrown at speed >=~26 spawns 1-2 ImpactBlocks (0.4, pickup-able); speed 20 or less spawns none.
- *verified* Heavy 1.0 blocks never topple from throws. Light ImpactBlock structures topple with an accurate throw: from ~6.5u dir [0,0.08,1] speed 22 hit; from 2.5u flat throw overshoots; ~0.12 up at 10u.
- *verified* Ring is light and lofts far: speed 10.5 steep flew ~17u. Speed 8, dir [0.87,1.0,-0.5], from ~6u away and 4u below landed it on top of a 3-high pillar. Use speed ~8 for short tosses.

## Builds (current)
- 4-high wall of Blocks at (-3..-5,-20), no Ring; 3-high pillar at (-6.75,-15) (Blocks 3,2,5) with Ring on top; 5 ImpactBlocks loose in a row near (5,2) with Rock beside them (~4.7,1.2).
