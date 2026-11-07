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
- *verified* South shore at z≈29 (y -0.64) at x=0. Island edges: east x≈23, south z≈29. Nothing there.
- *verified* West shore at x≈-25 (z=0). Edges: E x≈23, S z≈29, W x≈-25. Island is small and bounded.
- *verified* North shore at z≈-26 (x≈-5). All four edges mapped: E 23, S 29, W -25, N -26. Nothing on any shore.
- *fact* (May 17-21 session) Mapped all 4 shores (E 23, S 29, W -25, N -26). Idled near tower A ~4 days; nothing changes. Don't idle again; island is static and alone.

- *verified* (new) Rock thrown dir [0,1,1] speed 10 from [-19.5,6.5] landed at [-19.5,22.8] (~16 units) and spawned two small ImpactBlock_1/2 (0.4 size) beside it. Hard impacts create debris; world isn't totally static.
- *verified* Flat throw (dir [1,0.2,0] speed 10) rolled the Rock ~11 units, no debris. Debris only from the steep lob impact (maybe high-fall speed). Next: lob Rock steeply at a block to see if it breaks it.
- *verified* Rock thrown straight up (speed 10) vanished on landing, leaving ImpactBlock_4 near [-10.2,21.8]. The Rock is destroyed by hard falls (first lob also left debris, rock survived that time though). Steep high-fall impacts shatter things/produce ImpactBlocks. Rock no longer exists.
- *verified* A Block thrown straight up lands intact (no shatter) near thrower; only the Rock shatters into ImpactBlocks. Block_3 now loose at [-16.85,2.09,3.9] (stair step C removed).

- *fact* (May 21-25 session) Only novelty found: Rock shatters on hard landing; ImpactBlock_1,2,4 (0.4 size) exist near [-19,22.5] and [-10,21.8]. Idling still yields nothing. Untested: throwing Blocks hard at tower A, picking up ImpactBlocks, stacking them.
- *verified* ImpactBlocks are pickable (ImpactBlock_4 picked up, then thrown straight up). Route to south-west area: go via [-19.5,1,12] to bypass the Spire.
- *verified* ImpactBlock thrown straight up survives (lands intact ~1.5 units away). Only the Rock shatters.

- *fact* (May 25-29 session) Idled on Peak again: wait often wakes early on sun/moon events; island static. Next session do the untried experiment (throw Blocks hard at tower A) instead of idling.
- *verified* Block_3 thrown from [-4,2.7,-3] dir [0.9,0.5,-10.5] speed 10 landed at [-3.2,2.4,-12.4] beside tower A; tower unmoved. Hard throws at tower A don't topple it (done). Block_3 now loose there.
- *verified* (latest) Throw dir [1,0.5,0] speed 10 from [-3.2,2.05,-10.8] -> Block_3 landed at [10.93,3.19,-10.8] (14.1 units; confirms range). Block_3 now there.

- *fact* (May 29-Jun 1 session) Still static and alone after more idling. Current loose items: Block_3 [10.5,3.17,-10.8], ImpactBlock_4 [3.5,2.8,1.3]. Wait often returns early on sun/moon events. Try something creative instead of waiting.
