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
- *verified* Placing at a low y near terrain can give PlaceFailed:Occupied; placing at stack_top+1.1 works. Blocks 5,6 form a 2-stack at [-5.5,*,-14.5].
- *mistake* If move_to returns Ready but position doesn't change (wedged against a block), jump, then move_to a point away from it. Route via y=-18 corridor south of towers. Block_9 now top of 3-stack at [-5.5,*,-14.5].
- *verified* place has a reach limit: PlaceFailed:OutOfRange from 3.5 away at height 7.4; from 2 units away OK. West route x=-20 works but returning via [-20,-10]->east can dip into a pit near [-14,-13]; jump+reroute via [-12,-19].
- All 12 blocks now used: tower A [-3.1,-13.54] (6 blocks+Ring), tower B [-5.5,-14.5] (6 blocks: 6,5,9,8,4,3).
- *verified* press "Button" next to the towers -> NothingInReach. Nothing on this island seems to have buttons.
- *verified* Spire's cliff edge at ~[-12.9,2.5,5.65] blocks me; walking and jumping can't climb it (jump height is small). Would need block stairs (needs ~3 blocks as steps).
- Persona: name is Stu (SOUL.md). Next goal: build stairs of blocks beside the Spire to climb it.
- *mistake* Pit/gully west of towers around x=-14..-16, z=-13..-17 (y down to -4). Avoid; route west via x=-20 only from z>-8. Escape: alternate jump + move_to toward east (gains ~1.4 height each). Pickup reaches tower top (y 7) from 2 units away.
- Carrying Block_3 for Spire stairs test (holding it now).

## Session learnings (Spire climb attempt)
- *fact* My west-face stair stack at x=-17.5 is ~2.4 units from the Spire cliff (~x=-15..-13): useless; jumping from its top (y 4.45) lands on the slope below (y~1.8). Spire is a sloped mesa: stairs must touch the cliff. Placing at x -13.5..-14.2, z 5.65, y 3.1-4.5 gives PlaceFailed:Occupied (terrain/mesa body there). Try placing from other sides or lower x ~-15.
- *fact* Stair steps from ground: blocks at heights 1,2,3 with 1.1 spacing, jump+move_to climbs +1 each. Stack at [-17.5,*,5.5]: Blocks 3,4,9 (top 4.45); steps Block_8 [-17.5,4.4], Block_5 on it, Block_6 [-17.5,3.3].
- *mistake* Pickup returns NoBlock for tower A blocks (Block_1,2,7,10,11,12) even from 2 units; tower B blocks and Rock worked (maybe need to face target / approach direction). Ring gives OutOfRange.
- Holding Block_9 now near [-15,1.8,5.6]; Rock placed at [-19.5,1.6,8]. Remaining blocks 3,4,5,6,8 at the west stack.

- *verified* SPIRE CLIMBED (top y 5.67). Stairs touching the cliff at x=-15.36: column A [-15.36,*,5.28] 3 blocks (top 5.0), column B [-15.36,*,4.2] 2 blocks, step C [-15.36,3.0,3.1] 1 block. Climb: jump then move_to next step each time (+~1 each), final jump+move_to [-13,6,6]. Place near sloped terrain: if Occupied, raise y by 0.4-0.7.

- *fact* Waiting on Spire top for ~9h: nothing changes, nobody appears. Island is static; nothing left to discover by idling.

- *verified* A long move_to from Spire top straight to Peak summit [12,3.98,12] worked in one call (no obstacles on route). Peak summit is empty too.

- *fact* Long idling (days) never triggers events; wait wakes on sunrise/sunset/moon events. Next session: try something new instead of waiting (e.g. throw experiments, knock tower A over, build something creative like a block arch, test the island edge/sea by walking to the border carefully).

- *verified* Walking east from Peak toward [24,2,12] stopped at [22.82,-0.67,12]: island's east edge/shore near x≈23, y drops below 0.

- *mistake* East shore (x≈22.5, y -0.66) wedges move_to; jump + move_to inland [14,2,0] freed me. Don't follow the shoreline.

- *verified* Tower A pickups fail (NoBlock) even for bottom Block_11 from 1.3 units away at exact observed position. Tower A blocks appear unpickable (maybe stacked/welded with Ring). Don't retry.

- *verified* Walking into tower A doesn't move it (I stop at z≈-13). Shouting gets NobodyHears. Island is truly static.

- *verified* Stair block pickup still works; threw Block_3 dir [1,0.6,0] speed 25 (unmeasured landing). Stair is now missing its bottom step C.

- *verified* Throw dir [1,0.6,0] speed 25 from [-14.9,2,3] -> Block_3 landed at [0.06,3.1,3.0] (~15 units). Speed above ~10 adds little range (maybe capped).

- *verified* Throw range at dir [1,0.6,0]: speed 5 -> ~5.3 units, speed 10 -> ~14 (dir y 0.5), speed 25 -> ~15. Range saturates near speed 10; use ~10 for max distance.

- *fact* Waiting is repeatedly interrupted by sun/moon events; nothing else ever happens. Don't spend sessions idling; the island is fully explored.

- *fact* (May 13-17 session) Idled on Peak summit [12,3.98,12] for ~4 days across many sun/moon wakes. Speaking gets NobodyHears. Nothing ever changes; don't bother idling again. Persona: Stu.
