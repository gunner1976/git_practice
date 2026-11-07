# SEMANTIC_MEMORY.md - What I Know and I Can Do

(Persona note: SOUL.md says name Stu, task prompt says Eko; I've used Eko.)

## Index
- World
- Movement
- Pickup / Place / Stacking
- Throwing
- Press / Ring
- Ideas to try

## World
- *fact* Start ~[0,0.7,-22]. Island has 12 unanchored 1x1x1 Blocks (Block_1..12), a Ring, a Rock, hills (Peak, Hill_1-4) and the Spire mesa at [-14,8]. No other players seen.
- *fact* Day/night cycle exists (night arrived after ~40 ticks). Object positions in observe persist; things I move stay where left.

## Movement
- *mistake* move_to does not path-find: it stops dead against obstacles (towers, Spire) yet returns "Ready". Always check returned position; route via waypoints (west side x=-20 passes the Spire; also go around my tower).

## Pickup / Place / Stacking
- *verified* move_to within ~1-1.5 units of an object, then pickup at its exact position -> PickupSuccess. Holds one item at a time.
- *verified* place can fail with PlaceFailed:Occupied if overlapping something; retry ~2 units away.
- *verified* Stacking: place at (x, top_y+1.1, z) of the stack from ~1.5 units away on the ground; it settles, +1.0 height per block. Built 6-block tower plus Ring on top (top y≈8) at [-3.1,*,-13.54]; no reach limit hit, stable.

## Throwing
- *verified* direction [1,0.5,0] speed 10 -> block flew ~14.5 units. From ~11 units, direction=(target-me) with y=+1.5, speed 12 lands within ~1 unit of target. Rock thrown at tower base did not topple it.

## Press / Ring
- *verified* Ring is pickable/placeable. press "use" -> PressFailed:NothingInReach; real button names unknown (hypothesis: only certain objects have buttons).

## Ideas to try
- Collect remaining blocks (3,4,5,6,8,9) for a second structure; throw harder/higher at tower; jump onto tower/Spire; speak.

## Misc
- *verified* jump works (airborne:true). speak returns SpeakSuccess:NobodyHears when alone on the island.
