# How the agents' free play evolves: `pilot-20261024-005431`

10 free-play days across 1 agents. Every number comes from replaying the logged actions; memory figures are the agent's own files at the end of each day.

![Evolution](evolution.png)

## agent_1

- First rock impact that made blocks: day 2
- First time on top of the Spire: day 5

| day | min | turns | actions | idle | walked m | max height | objects | stacked | throws | impacts | episodic | semantic kB | Spire | ended |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20.3 | 86 | 77 | 9 | 551 | 4.2 | 13 | 9 | 1 | 0 | 11 | 2.2 |  | session time up |
| 2 | 20.2 | 64 | 106 | 16 | 563 | 4.4 | 13 | 9 | 9 | 2 | 29 | 2.4 |  | session time up |
| 3 | 20.1 | 77 | 55 | 23 | 467 | 4.6 | 6 | 1 | 8 | 0 | 46 | 3.8 |  | session time up |
| 4 | 20.2 | 78 | 71 | 18 | 224 | 5.6 | 13 | 8 | 8 | 5 | 63 | 2.8 |  | session time up |
| 5 | 20.1 | 80 | 91 | 13 | 384 | 5.5 | 11 | 6 | 4 | 2 | 73 | 2.8 | yes | session time up |
| 6 | 20.1 | 106 | 43 | 61 | 132 | 4.6 | 6 | 5 | 4 | 4 | 83 | 2.9 |  | session time up |
| 7 | 20.6 | 73 | 61 | 20 | 251 | 4.6 | 7 | 5 | 7 | 2 | 95 | 3.4 |  | session time up |
| 8 | 20.2 | 77 | 47 | 24 | 336 | 3.1 | 8 | 5 | 7 | 0 | 113 | 3.6 |  | session time up |
| 9 | 20.0 | 82 | 89 | 17 | 542 | 4.6 | 14 | 9 | 1 | 1 | 128 | 4.1 |  | session time up |
| 10 | 20.1 | 116 | 25 | 83 | 89 | 4.6 | 4 | 3 | 3 | 1 | 138 | 4.3 |  | session time up |

### Diary (episodic summaries added each day)

**Day 1**
- Picked up a block and placed it nearby on my first outing.
- Started a two-block tower by stacking Block_5 on Block_4.
- Fetched Block_3 from across the hill and made the tower three blocks tall.
- Added Block_12 to the tower, making it four blocks tall.
- Placed Block_6 (purple) on the tower, making it five blocks.
- Tower reached six blocks after adding Block_10.
- Added Block_8 as the seventh block of the tower after one out-of-range failure.
- Built a step block beside the tower and climbed it to place an eighth tower block (pink).
- Used every block on the island: finished a 10-high tower with a staircase beside it.
- Cleaned up semantic memory and headed toward the Ring before the reset.
- Picked up the Ring and threw it, testing the throw tool for the first time.

**Day 2**
- Found the world reset, then threw the Rock onto Peak.
- Threw the Rock hard and it spawned impact debris on landing.
- Threw Block_3 across a hill to compare with the Rock.
- Threw the Rock gently and got no debris.
- Threw the Rock at speed 20 and saw no debris.
- Confirmed fast Rock throws spawn impact debris.
- Threw the Rock at speed 25 and still got no debris.
- Threw a block at speed 50 and it only went about 11 units.
- Stacked Block_3 on Block_10 on the hill near Spire.
- Added Block_7 to make a three-block tower near Spire.
- Made the Spire-side tower four blocks tall with Block_9.
- Topped the tower at five blocks with Block_1.
- Added Block_11, making the Spire-side tower six blocks tall.
- Got stuck at my tower, then built a step block and made it seven blocks tall.
- Placed Block_8 at y~9.9, making the tower eight blocks tall.
- Finished a 9-block tower with a stair and 2-block column, using all 12 blocks.
- Reorganized semantic memory before the reset.
- Threw the Ring at speed 30 and got no debris.

**Day 3**
- Confirmed the world reset again and threw Block_4 gently.
- Threw a block at a placed block and it sailed past without a knock.
- Threw Block_4 point-blank at Block_12 and it still passed through untouched.
- Threw the Rock at Block_12 and it stopped against it without moving it.
- Walked east to the island edge and was stopped at x≈32.
- Probed the west and south edges of the island.
- Freed myself from a stuck spot and found the north edge near z=-32.
- Rewrote semantic memory into a clean, consolidated form.
- Threw the Rock at speed 30 at Block_12 and it just landed on top.
- Climbed to the summit of Peak and found nothing there.
- Placed Block_3 on the summit of Peak.
- Threw Block_3 off Peak and it traveled about 9 units.
- Placed Block_3 with a 45-degree yaw to test rotation.
- Tested whether a rotated block has a wider footprint by placing Block_5 beside it.
- Carried the Ring to Peak and set it on top of Block_3.
- Threw the Rock at speed 30 hoping for debris and got none.
- Threw the Rock steeply downward at speed 30 and got no debris again.

**Day 4**
- New session: world reset again, same layout. Observed only; nothing new tried.
- Threw the Rock flat east at speed 30 from Hill_2 and got 2 ImpactBlocks; found a debris recipe.
- Picked up both ImpactBlocks and stacked them into a 2-piece tower at (26,*,-8).
- Threw the Rock flat from low ground at speed 30: 8.6 units, no debris. Debris seems to need a drop from height or a longer flight.
- Threw the Rock east from Peak summit at speed 30 and got 4 ImpactBlocks; launch height seems to drive debris count.
- Threw the Rock from Peak summit at speed 20: another 4 ImpactBlocks, so speed is not the key; 10 debris pieces now exist near (26,0.4,12).
- Built a small 2-piece debris tower at (22,*,12) on the Peak slope (first place failed Occupied by terrain, retried 0.5 higher worked).
- Debris tower at (22,*,12) now 5 pieces tall (y up to ~3.1); some pickups return NoBlock for no clear reason, just pick another piece.
- Debris tower at (22,*,12) is now 7 pieces tall (top ~3.9).
- Fetched the Rock and threw it again from Peak summit east at speed 25 to farm more debris (result not yet checked).
- My Rock throw hit the debris tower and knocked it apart; learned ImpactBlocks are movable by the Rock.
- Threw an ImpactBlock east at speed 20 and it disappeared from the world.
- Rewrote semantic memory into a clean consolidated form with a Debris section.
- Stood on a block atop Peak and threw the Rock: only 2 debris, so height doesn't scale the count (looks random 2-4).
- Cleaned semantic memory: merged the height-doesn't-matter correction into the Debris recipe.
- Another summit Rock throw (dir 1,0.1,-0.4) gave 4 more debris; ~14 pieces made this session with no cap seen. Memory files updated before reset.
- Carried an ImpactBlock to Peak summit and placed it on top of Block_3, mixing big and small material.

**Day 5**
- New session: world reset again, same layout; reviewed memory and observed only.
- Threw the Rock flat east from Peak summit and got 4 ImpactBlocks again.
- Placed one ImpactBlock on the Peak slope at (23,*,9); first try was Occupied, 0.7 higher worked.
- Stacked three ImpactBlocks into a tower at (23,*,9), top at y~2.07.
- Capped the debris tower at (23,*,9) with the Ring.
- Threw the Ring at the debris tower and it passed through, leaving the tower intact.
- Tried to climb the Spire mesa with a stair block and reached its east edge but could not walk onto it.
- Built a 6-block staircase and climbed onto the Spire mesa; the top is empty.
- Threw the Rock west from the Spire top and got just 1 ImpactBlock at the island rim.
- Rewrote semantic memory cleanly before the reset, adding a Climbing section.

**Day 6**
- New session: world reset again, same layout; observed only.
- Threw Rock from Peak summit with upward angle (1,0.4,0) speed 30: landed ~(29,-0.3,12), only 1 ImpactBlock; flat throws seem better (2-4).
- Threw Rock south from Peak summit (0,0.1,1) speed 30: 4 ImpactBlocks near (12,0.3,26); direction doesn't matter, flat works.
- Built a 4-piece debris tower at (12,*,25.5) on flat ground south of Peak (z=22 was Occupied by the slope).
- Capped the debris tower at (12,*,25.5) with the Rock; it holds.
- Placed Block_8 on top of the Rock-capped debris tower at (12,*,25.5): debris, rock and block stack together.
- Dismantled the cap, threw Rock from Peak at the 4-piece debris tower: top piece knocked off, 3 new ImpactBlocks spawned, lower 3 stayed.
- Threw the Rock point-blank south at the tower; it vanished from the world (lost for this session) along with one ImpactBlock.
- Rebuilt the tower with Block_8 on top of 3 debris pieces; session wrapped up, Rock lost until reset.
- Consolidated semantic memory before reset (flat throws any direction, tower stacking, Rock-loss warning).

**Day 7**
- New session: world reset again, same layout; observed only.
- Threw the Rock west from Peak summit and got 2 ImpactBlocks.
- Stacked the two new ImpactBlocks into a tower at (3,*,12) on the Peak slope.
- Capped the debris tower with Block_8 and hit it with the Rock; the tower did not move.
- Swapped the cap for the Ring and hit the tower with the Rock: nothing toppled.
- Threw Block_8 at 45 degrees from the Peak summit and it flew ~17 units.
- Threw Block_8 at slope 0.6 from the summit and it flew ~17.8 units, about the same as at 45 degrees.
- Threw the Rock north at slope 0.7 from the summit and got 2 ImpactBlocks ~15 away.
- Stacked the two new ImpactBlocks into a tower at (12,*,-4.5) on Hill_2.
- Capped the Hill_2 debris tower with the Rock.
- Picked up the Ring from the tower to compare its throw range; reset arrived before throwing.
- Threw the Ring at 45 degrees from the summit and it disappeared from the world.

**Day 8**
- New session: world reset again, same layout; observed only.
- Picked up Block_4 and placed it at (-0.2,2.5,-18); simple routine, nothing new learned.
- Threw Block_12 at 45 degrees (dir 0,1,1) speed 20 from low ground (-9.2,2,-16): landed ~13 away on Hill_3 at (-9.2,3.9,-3.1). Arcs from low ground reach ~13, beyond flat 9-11.
- Updated semantic memory with the 45-degree low-ground arc range (~13) and noted Rock-capped towers hold.
- Threw Block_4 at 45 degrees speed 40 from (-0.2,1.8,-15.5): landed ~13.3 away, same as speed 20. Speed confirmed irrelevant for range.
- Threw Block_4 at slope 0.5 (dir 0,0.5,1) speed 20 from (-0.2,2.5,-5): landed 13.1 away, identical to the 45-degree throws. Range seems capped ~13 for slopes 0.5-1 from low ground.
- Threw Block_4 at slope 0.25 speed 20 from (-0.2,2.6,5) toward -z: landed 11.1 away. So low-ground range: slope 0.25 ~11, slopes 0.5 and 1.0 ~13.
- Consolidated semantic memory: folded throw range-by-slope findings into the Throwing section.
- Threw Block_4 east from (28,0,0) toward the island edge: it stopped at x=32 (the bound) instead of vanishing. Edge acts as a wall for blocks; vanishing items (Rock, Ring, ImpactBlocks) must have another cause.
- Updated semantic memory: bounds are a wall for thrown Blocks; reframed the vanishing-items open question.
- Threw the Ring east (dir 1,0.7,0) from (27,0.2,4.7) toward the edge: it vanished, whereas Block_4 stopped at x=32 the same way. Ring vanishes where a Block stays; maybe it slips past/under the bound. Ring lost until reset.
- Threw the Rock east (dir 1,0.7,0) from (28,-0.1,-6.3) toward the edge: it vanished with no debris. Confirmed: Ring and Rock vanish when thrown into the edge/bound while Blocks stay. Rock and Ring both lost until reset.
- Consolidated semantic memory with an Edge rule (Ring/Rock vanish at the bound, Blocks stay).
- With the Rock lost, stacked Block_6 on Block_5 on Hill_1 at (10,*,-15.6) to make a 2-block tower.
- Added Block_3 to the Hill_1 tower at (10,*,-15.6): now 3 blocks.
- Verified by observe that the 3-block tower at (10,*,-15.6) stands at y 2.8/3.8/4.8. Session state: Rock and Ring lost, tower built; memory files up to date.
- Added Block_12 to the Hill_1 tower at (10,*,-15.6): now 4 blocks.
- Added Block_10 to the Hill_1 tower at (10,*,-15.6): now 5 blocks (top ~y 6.8). Session also: range-by-slope throws, Ring and Rock vanish at the bound (Blocks stay). Memory files up to date before reset.

**Day 9**
- New session: world reset, same layout; picked up Block_4, nothing new learned.
- Placed Block_4 at (-3,3,-10); routine, no new findings. Memory is up to date.
- Stacked Block_12 on Block_4 at (-3,*,-10): 2-block tower. Nothing new learned.
- Added Block_3 to the tower at (-3,*,-10): now 3 blocks (verified 2 by observe first). Nothing new learned.
- Added Block_5 to the tower at (-3,*,-10): now 4 blocks. Nothing new learned.
- Added Block_6 to the tower at (-3,*,-10): now 5 blocks (top ~y 7.7). Nothing new learned.
- Observed: 5-block tower at (-3,*,-10) verified standing, y 2.69..6.69 at 1.0 spacing.
- Added Block_10 to the tower at (-3,*,-10): now 6 blocks (top ~y 7.7). Nothing new learned.
- Tower at (-3,*,-10) reached 7 blocks. Placing 8.7 high from ground failed OutOfRange; placed Block_7 as a step at (-1,*,-10), jumped on it, then placement worked.
- Tried an 8th block at y~9.7 from the step: OutOfRange again. A single step is not enough above 7 blocks; would need a 2-block stair.
- Built a 1-2 stair (x=0.5 and x=-1 columns) beside the tower and placed the 8th block at (-3,~9.7,-10). Stair of 1,2 gives enough reach for 8 blocks.
- Placed the 9th block (Block_11) at (-3,~10.7,-10) from the 2-high stair while jumping. All 12 blocks used. Got wedged between tower and step once; move_to south freed me.
- Verified 9-block tower (top y 10.69). Threw Rock from summit west-ish (-1,0.1,0.3) speed 25: 2 ImpactBlocks near (0,2.3,15.5).
- Picked up ImpactBlock_1 to try capping the 9-block tower at (-3,*,-10) via the stair; reset arrived first. Session: built 9-block tower with 1-2 stair, learned step/stair/jump-place reach tricks.
- Tried to cap the 9-block tower with an ImpactBlock at y 11.4 from the 2-high stair: OutOfRange. 9 blocks (top 10.7) is the reach limit with this stair.

**Day 10**
- New session: world reset, same layout; observed only.
- Threw Rock from summit toward Spire (-1,0.1,-0.3) speed 25: landed ~(1,3,8.7), 2 ImpactBlocks. Consistent with recipe; nothing new.
- Stacked the two new ImpactBlocks into a 2-piece tower at (5,*,9) on the Peak slope; both places succeeded first try.
- Capped the (5,*,9) debris tower with the Rock; place succeeded.
- Observed: Rock-capped 2-piece debris tower at (5,*,9) stands (y 3.71/4.11/4.61). Session otherwise routine.
- Threw Block_10 from (-5,2.4,5) at slope 0.5 toward the Rock-capped tower: landed only ~7.5 away at (1.7,3.3,7.7), short of the tower (rising Peak slope cuts the arc). Tower untouched.
- Got wedged against my own tower at (5,*,9) (move_to did nothing); jump + move_to away freed me. Threw Block_10 from the summit at the tower: landed beside it at (6.1,4.3,9.5), tower untouched. Blocks can't topple towers.
- Placed Block_10 on top of the Rock cap at (5,5.4,9): tower is now debris, debris, Rock, Block.
- Verified by observe: 4-part mixed tower at (5,*,9) stands (debris 3.71, 4.11, Rock 4.61, Block_10 5.41).
- Session wrap-up: built Rock+Block-capped debris tower at (5,*,9), learned slope-short throws and the wedge fix again. Memory up to date before reset.

### Rules written down, by day

Extracted automatically from the notes: each rule-like line, when it first appeared, revisions, and whether it later left the notes.

| day | new | revised | left notes | held at end of day |
|---|---|---|---|---|
| 1 | 18 | 4 | 5 | 13 |
| 2 | 16 | 9 | 14 | 15 |
| 3 | 16 | 10 | 9 | 22 |
| 4 | 16 | 13 | 22 | 16 |
| 5 | 9 | 13 | 8 | 17 |
| 6 | 8 | 12 | 6 | 19 |
| 7 | 29 | 8 | 25 | 23 |
| 8 | 7 | 7 | 8 | 22 |
| 9 | 3 | 0 | 0 | 25 |
| 10 | 1 | 0 | 0 | 26 |

**Day 1: new rules**
- [belief] move_to near a block then pickup(block position) works; place(position) drops held item. *(left notes on day 1)*
- [belief] Island bounds (move_to clamps): x -28..32, z -32..29. Start (0,1,-22). Terrain: Peak, Spire mesa, Hill_1..4. *(revised 4x; left notes on day 7)*
- [belief] place has a short range (~5-6 units); OutOfRange means walk closer. Placing on an occupied spot fails; blocks stack if placed ~1 unit above another (they settle physically). *(left notes on day 1)*
- [belief] Blocks stack with 1.0 spacing; 9-block towers are stable. *(revised 3x; left notes on day 4)*
- [belief] A 6-block tower is stable, and placing from the ground at y up to 8 works from ~2.5 units away (reach isn't height-limited so far). *(left notes on day 1)*
- [belief] Place reach is a 3D distance (~7 units max?): y=9 from 2.5 horizontal away failed OutOfRange; moving to ~1.7 horizontal and y=8.6 worked. For tall towers, stand right beside it. *(left notes on day 1)*
- [belief] Blocks stack at 1.0 spacing (1.1 for side by side); 9-block towers stable. Tall towers: 1-high stair + 2-block column beside, place from the top. 12 blocks = 9 tower + 2 column + 1 stair. *(revised 4x; left notes on day 5)*
- [mistake] place fails "Occupied" if target overlaps terrain or my body. Place ~0.6 higher, stand >=2 units away. *(revised 3x; left notes on day 4)*
- [belief] Staircase climbing: each jump() + move_to onto a block adjacent and 1 higher works, so a 2-high column plus a 1-high stair lets me reach ~1 unit higher per column block. Fetch-and-stack total: all 12 blocks used (9 in tower, 2 as stairs, 1 as column). *(left notes on day 1)*
- [belief] Loose: 12 unanchored 1x1x1 Blocks, a Ring (~24.9,0.7,4.7), a Rock (~16.5,2.6,-6.3). *(revised 2x; left notes on day 7)*
- [belief] pickup needs me within ~1-2 units; one item held at a time. Occasional NoBlock: retry or pick another. *(revised 5x; left notes on day 7)*
- [belief] move_to is near-instant, walks terrain, blocked by standing blocks/piles/cliffs (debris towers too). Climb 1-high: jump(), move_to top. Descending is free. *(revised 5x; left notes on day 7)*
- [belief] place(pos) drops the held item. Fails with OutOfRange if the 3D distance is too large (about 5-7 units); walk closer. *(left notes on day 2)*
- [belief] 12 blocks were enough for: 9-block tower at ~(3,*,-13), a 2-block column at (4.5,*,-12), and a stair at (5.7,*,-12). *(left notes on day 2)*
- [belief] Haven't examined Ring or Rock (was walking to the Ring); try picking up and throwing them. *(left notes on day 2)*
- [belief] Untested: throw tool, how high the tower can go, whether the world persists across sessions. *(left notes on day 2)*
- [belief] pickup works on the Ring. throw({direction:[-1,0.5,0], speed:10}) sent the Ring ~9.5 units horizontally (landed on a hill, y 3.35). Direction need not be normalized. Distance grows with speed. *(left notes on day 2)*
- [belief] Tower of 9 blocks stood to y=10.56 with no collapse. *(left notes on day 2)*

**Day 2: new rules**
- [belief] World resets each session (blocks/ring/rock back at original spots). Rock is pickup-able; throw([0,1,1], speed 15) sent it ~13 units forward (landed on Peak). *(left notes on day 2)*
- [belief] Rock at speed 30 spawns 1-3 ImpactBlock debris (0.4 size, persist); speeds 12-25 none; blocks and Ring never do. *(revised 2x; left notes on day 4)*
- [belief] A Block thrown at speed 30, dir [-1,0.3,0] flew ~12 units with no debris (debris seems tied to the Rock, or to a harder impact). *(left notes on day 2)*
- [belief] Rock thrown gently (speed 12) made no debris, so debris likely needs a high-speed impact (speed 30 did it; the block at 30 didn't, so maybe Rock-specific too). *(left notes on day 2)*
- [belief] Rock at speed 20 (dir [0,0.2,-1]) also made no debris; threshold, if any, is between 20 and 30 (or depends on landing/angle). *(left notes on day 2)*
- [belief] Rock at speed 30 with flat angle [0,0.2,-1] also spawned debris (1 ImpactBlock). So debris is speed-driven (threshold between 20 and 30), count varies. Debris persists on the island. *(left notes on day 2)*
- [belief] Rock at speed 25 made no debris; debris threshold is between 25 and 30 (speed 30 worked twice). *(left notes on day 2)*
- [belief] Throw range is effectively capped ~11-15 units: a Block at speed 50 only went ~11 units, and no debris. Debris appears only for the Rock at speed ~30 (blocks never made any). *(left notes on day 2)*
- [mistake] Wedged between a block/tower and mesa: jump(), then move_to away. Stand >=3 from bases. *(revised 4x; left notes on day 7)*
- [belief] Ground placement failed at y=8.9 (6-block tower on a hill, top at 7.9). Fix: one step block beside the tower, move_to ~1.5 units from it, jump(), move_to its top; then place worked. *(left notes on day 2)*
- [belief] place(pos) fails OutOfRange beyond ~6.5 units above my feet. Placing a block under me lifts me. *(revised 2x; left notes on day 4)*
- [belief] World RESETS each session (builds and debris gone, Rock restored). Re-observe first. *(revised 3x; left notes on day 7)*
- [belief] Direction need not be normalized. Range capped ~11-15 units regardless of speed (block at 50 ~11; speed 10 ~10.7; Ring at 10 ~9.5; Rock at 15 ~13). *(revised 1x; left notes on day 4)*
- [hypothesis] Is debris Rock-specific? (try the Ring at 30). Try speed 27-28 for the exact threshold. *(left notes on day 3)*
- [hypothesis] Can blocks be thrown to knock down a tower? Can I build something taller than 9-12 blocks (only 12 blocks exist; ImpactBlocks are 0.4 size and could be extra material)? *(left notes on day 3)*
- [belief] Ring thrown at speed 30 went ~6.5 units (lands on hill) with no debris, so debris is Rock-only. *(left notes on day 3)*

**Day 3: new rules**
- [belief] Thrown block at speed 15, nearly flat, aimed at a block 5.5 units away: it passed the target without moving it (landed 4 units beyond). Either it flew over (thrown from head height) or no collision. Untested: aim lower/pitch down. Speed 10 flat throw went ~10.7 units. *(left notes on day 3)*
- [belief] Point-blank throw (slightly downward, speed 15) at an adjacent block also left it untouched; the projectile passed through to 7 units beyond. Thrown blocks seem not to collide with other blocks, so knocking towers over by throwing doesn't work. (Standing blocks DO block my own move_to.) *(left notes on day 3)*
- [belief] Rock thrown flat at speed 15 stopped dead against a placed block (landed just in front of it), and the block didn't budge. So the Rock collides with blocks but can't push them; earlier thrown blocks passed through. Placed blocks are effectively immovable by throws. *(left notes on day 3)*
- [belief] Island edge: move_to toward x=40/60 stops at x≈31.9 (y≈-0.7, ground slopes down). Can't leave the island; boundary is ~32 on +x, further than the ±25 item spread. *(left notes on day 3)*
- [belief] Edges (move_to clamps): +x ≈ 32, -x ≈ -28, +z ≈ 29 (y drops to ~-0.8 at edge). Island is roughly a 60-unit disc, slightly offset east. *(left notes on day 3)*
- [belief] z edge ≈ -32 (y≈-0.7). Island ≈ x -28..32, z -32..29. Being stuck next to a block: jump() then move_to works again. *(left notes on day 3)*
- [belief] Direction need not be normalized. Range ~10-15 regardless of speed. Blocks/Ring pass through placed blocks and debris, never make debris. Rock stops against placed blocks without moving them. *(revised 2x; left notes on day 7)*
- [hypothesis] Can ImpactBlock debris be used as extra building material? *(left notes on day 4)*
- [hypothesis] Does a Rock at speed 30 push a block? Is there anything off the island or at the Peak top? *(left notes on day 4)*
- [belief] Rock at speed 30 thrown at a placed block from 4 units: block unmoved, no debris, Rock ended up resting on top of it. Placed blocks are immovable even at max speed. (Debris likely needs a long flight/terrain impact.) *(left notes on day 4)*
- [belief] Peak summit (12,4.59,12) is reachable by move_to; nothing special there (no entities), just the highest ground. *(left notes on day 4)*
- [belief] Block thrown flat at speed 20 from Peak's edge went ~9 units horizontally (landed on the downslope); range stays ~10 regardless of height/speed. *(left notes on day 4)*
- [belief] place accepts a rotation (yaw 45 succeeded), but observe doesn't report rotation, so I can't verify its effect. *(left notes on day 4)*
- [belief] Block spacing test: a block placed at 0.9 from a neighbour is Occupied, at 1.1 succeeds. A yaw-45 block did not widen its footprint (1.1 spacing still worked), so rotation appears to be ignored or purely cosmetic. Placed blocks rest ~0.5 above the surface they land on. *(left notes on day 4)*
- [belief] Ring can be placed like a block (rests on top of a block at +0.6). Rock at speed 30 thrown upward-ish (pitch 0.2) landed only ~10 units away with no debris, so debris is not guaranteed at speed 30 (earlier throws that made debris were at other angles/targets). Debris-as-material remains untested. *(left notes on day 4)*
- [belief] Rock at speed 30 thrown steeply down (pitch -0.5) into nearby terrain went only 2.7 units and made no debris. Debris so far only appeared on earlier long flights landing far away (maybe needs real flight time/distance); still unexplained. 0 of 3 speed-30 throws this session made debris. *(left notes on day 4)*

**Day 4: new rules**
- [belief] Debris recipe: Rock from (15,2.6,-6) thrown dir (1,0.1,0) speed 30 flew ~12 units and landed at (27,0.4,-6) making 2 ImpactBlocks (0.4). Nearly flat throw with long flight over the downslope seems to work; steep/short or upward throws don't. *(left notes on day 4)*
- [belief] Debris can be picked up and placed, stacks at 0.4 spacing. No cap seen. A thrown ImpactBlock despawns. *(revised 3x; left notes on day 7)*
- [belief] Two ImpactBlocks stack with 0.4 spacing (y 0.39 then 0.79). Debris is small-scale building material; each Rock throw yields ~2. *(left notes on day 4)*
- [belief] Debris is not guaranteed: flat speed-30 throw from low ground (y 0.3) went 8.6 units and made none. The successful one started from a hill (y 2.6) and dropped to ground ~12 units away. Hypothesis: needs a longer/faster impact (height drop or distance >~10). *(left notes on day 4)*
- [belief] Recipe: Rock thrown FLAT (dir y ~0.1) speed 20-30 from Peak summit (12,4.6,12), any compass direction, lands ~14 away and makes 2-4 pieces (random). Upward angle (y 0.4) gave only 1. Low-ground throws give none; Spire-top west gave 1. Re-fetch the Rock each time. *(revised 4x; left notes on day 7)*
- [belief] Speed 20 from Peak summit also landed ~14 away and made 4 debris. So speed barely matters; the key is long flight from the summit (earlier speed-20/25 failures were from lower/short spots). Peak summit throw east = reliable 4 ImpactBlocks per throw (10 exist now). *(left notes on day 4)*
- [mistake] pickup NoBlock can happen even at ~1.5 range when the target is wedged next to the Rock/other pieces; approach from another side (or pick a different piece). Place works from ~3 away, so no need to walk to the tower. *(left notes on day 4)*
- [belief] Debris towers are NOT stable against throws: a Rock thrown from Peak summit east (speed 25) hit my 7-piece ImpactBlock tower at (22,*,12) and scattered it into pieces at x 20.8-22.6 (no new debris). Unlike the 1x1 Blocks (immovable), ImpactBlocks are pushed by the Rock. Keep debris towers out of the Rock's flight path; use summit throws toward x>24 for farming. *(left notes on day 4)*
- [belief] A thrown ImpactBlock vanished from the world (despawn). Don't throw debris you want. *(revised 1x; left notes on day 5)*
- [belief] place works up to ~6.5 away (stand ~3 away). If Occupied, place 0.5-0.7 higher or move to flat ground. Rotation is cosmetic. *(revised 2x; left notes on day 7)*
- [belief] Blocks stack at 1.0 spacing; 9-block towers stable. Placed Blocks immovable. Ring, Rock and Block all stack on debris towers (4 debris + Rock + Block worked). *(revised 2x; left notes on day 7)*
- [belief] Debris is dynamic: a Rock thrown through the tower scattered it. Keep towers out of the flight path. *(left notes on day 5)*
- [hypothesis] Does launch height scale debris count (tower-top throw)? Is there a cap on debris? *(left notes on day 4)*
- [hypothesis] Is there a cap on debris? Why do some pickups fail with NoBlock? *(revised 1x; left notes on day 5)*
- [belief] Launch height is NOT the driver of count: from 1 block above the summit (y 5.6), dir (1,0.1,0.4) speed 25 made only 2 pieces (landing (26,-0.2,17)). Counts seen: 2,2,4,4,2 — likely random 2-4 per big throw. Ignore my earlier "height scales count" guess; what matters is a long flight (~14) onto low ground. *(left notes on day 4)*
- [belief] Summit throw dir (1,0.1,-0.4) speed 25 landed ~14 away near (24.5,1,5.5) and made 4 pieces (counts seen: 2,2,4,4,2,4). No sign of a debris cap with 14+ pieces made in one session. Debris may rest on/near the Ring at (24.9,0.7,4.7). *(left notes on day 5)*

**Day 5: new rules**
- [belief] A Ring placed on top of a 3-piece debris tower stays put (y~2.35 on top of 2.07). Debris towers hold the Ring fine. *(left notes on day 5)*
- [mistake] throw with empty hands -> ThrowFailed:EmptyHands. *(revised 1x; left notes on day 7)*
- [belief] Only the Rock disturbs debris towers. Thrown Ring/blocks pass through. A thrown ImpactBlock despawns. *(revised 1x; left notes on day 6)*
- [belief] Spire mesa (x -16.5..-11.5, top y 3.52) isn't walkable from the east: a stair block at (-10.7,2.9,8) lets me reach (-11.5,3.73,8) but move_to inward then does nothing. Not tried: other sides, 2-block stair. *(left notes on day 5)*
- [belief] Each jump+move_to gains ~1 height. Spire climbed with 6 blocks: columns of 1,2,3 blocks in a row (x=-8.8,-9.9,-11.0 at z=7); a single stair block is not enough. *(revised 2x; left notes on day 7)*
- [belief] Rock thrown from Spire top (5.5) west (-1,0.1,0.3) speed 25 landed ~15 away at the island edge (-28.9,-0.3,12.5) and made only 1 ImpactBlock (id ImpactBlock_10) at x -27.9. Landing at the island rim/ground below y 0 gives fewer pieces. Peak summit east remains the best farm. *(left notes on day 5)*
- [belief] Terrain "position" is the BOX CENTER; top = y + size/2. Peak top 4.59 (summit (12,4.59,12)); Spire spans x -16.5..-11.5, z 5.5..10.5, y 2.0..5.52. Nothing on either summit. *(left notes on day 7)*
- [hypothesis] Why do some pickups fail with NoBlock? Does the Rock sinking at the rim (y<0) lose debris? Can other sides of Peak/Spire host better throws? *(left notes on day 6)*
- [belief] move_to from the Spire top to ground below works directly (no fall damage or blocking); descending is free, only climbing needs stairs. *(left notes on day 6)*

**Day 6: new rules**
- [belief] Upward-angled Rock throw (1,0.4,0) from Peak gave only 1 debris; keep throws flat (dir y ~0.1) for 2-4. *(left notes on day 6)*
- [belief] Flat Peak throws work in any direction (south gave 4 debris near (12,0.3,26)). *(left notes on day 6)*
- [belief] Peak's foot reaches ~z=23 on the south side; build on flat ground at z>=25 (e.g. (12,*,25.5)). *(revised 1x; left notes on day 7)*
- [belief] Debris towers (0.4 pieces) block walking like blocks; Rock can be placed as a cap. *(left notes on day 6)*
- [hypothesis] Does a mixed tower (Ring/Block on top) topple as a unit under a Rock hit? *(revised 1x; left notes on day 7)*
- [belief] Only the Rock disturbs debris towers; a hit from Peak knocked off just the top piece and spawned 3 new debris (hits make debris too). *(revised 1x; left notes on day 7)*
- [mistake] Rock thrown flat toward the south rim from 3 away vanished for the whole session. Don't throw the Rock toward the rim at close range; keep it recoverable. *(revised 1x; left notes on day 7)*
- [hypothesis] Why do some pickups fail with NoBlock? *(left notes on day 7)*

**Day 7: new rules**
- [belief] Island bounds (move_to clamps): x -28..32, z -32..29. Start (0,1,-22). Terrain: Peak, Spire mesa, Hill_1..4.
- [belief] Terrain "position" is the BOX CENTER; top = y + size/2. Peak top 4.59 (summit (12,4.59,12)); Spire spans x -16.5..-11.5, z 5.5..10.5, y 2.0..5.52. Nothing on either summit.
- [belief] Loose: 12 unanchored 1x1x1 Blocks, a Ring (~24.9,0.7,4.7), a Rock (~16.5,2.6,-6.3).
- [belief] World RESETS each session (builds and debris gone, Rock and Ring restored). Re-observe first. *(revised 1x)*
- [belief] Peak's foot reaches ~z=23 on the south side; build on flat ground at z>=25 (e.g. (12,*,25.5)).
- [belief] pickup needs me within ~1-2 units; one item held at a time. Occasional NoBlock: retry or pick another.
- [belief] move_to is near-instant, walks terrain, blocked by standing blocks/piles/cliffs (debris towers too). Climb 1-high: jump(), move_to top. Descending is free.
- [belief] place works up to ~6.5 away (stand ~3 away). If Occupied, place 0.5-1 higher (on slopes the piece settles down fine) or move to flat ground. Rotation is cosmetic. *(revised 1x)*
- [mistake] Wedged between a block/tower and mesa (move_to silently does nothing): jump(), then move_to away. Stand >=3 from bases.
- [mistake] throw with empty hands -> ThrowFailed:EmptyHands.
- [mistake] write_note overwrites the whole file; never write placeholders. Use append_note only for lines that belong at the end. Only call tools that exist. *(revised 2x)*
- [belief] Blocks stack at 1.0 spacing; 9-block towers stable. Placed Blocks immovable. Ring, Rock and Block all stack on debris towers (4 debris + Rock + Block worked).
- [belief] Each jump+move_to gains ~1 height. Spire climbed with 6 blocks: columns of 1,2,3 blocks in a row (x=-8.8,-9.9,-11.0 at z=7); a single stair block is not enough.
- [belief] Direction need not be normalized. Blocks/Ring pass through placed blocks and debris, never make debris. Rock stops against placed blocks without moving them. *(revised 1x)*
- [mistake] Rock thrown flat toward the south rim from 3 away vanished for the whole session. Don't throw the Rock toward the rim at close range; keep it recoverable. *(left notes on day 7)*
- [belief] Recipe: Rock thrown from Peak summit (12,4.6,12), any compass direction, flat (y ~0.1) or arced (y 0.7), speed 20-30, lands ~14-15 away and makes 1-4 pieces (random). Steep y 0.4 east once gave 1; Spire-top west gave 1. Low-ground throws give none. Re-fetch the Rock each time; keep throws away from the rim. *(revised 2x)*
- [belief] Debris can be picked up and placed, stacks at 0.4 spacing. No cap seen. *(revised 1x)*
- [belief] Rock hit on a bare debris tower knocks off the top piece and spawns ~3 new debris. A tower capped with a Block or the Ring did not move at all. Caps protect. A Rock-capped tower also held (placed, not hit). *(revised 2x)*
- [hypothesis] Why do some pickups fail with NoBlock?
- [hypothesis] Does a Rock hit on the Ring-capped or Rock-capped debris tower topple it? *(left notes on day 7)*
- [belief] A Ring-capped debris tower also survived a flat Rock throw (the Rock landed on top of it). Capped towers seem safe from Rock hits. *(left notes on day 7)*
- [hypothesis] Does a Rock-capped tower survive? (untested) *(left notes on day 8)*
- [belief] Range is set by slope (dir y/horizontal), NOT speed (20 vs 40 identical). From low ground: slope 0.25 ~11, 0.5 ~13, 1.0 ~13 (cap ~13). From Peak summit arcs ~15-18. Use slope >=0.5 for distance. *(revised 4x)*
- [belief] Ground off the Peak foot to the east is below 0 (y~-0.3 at x=28); still walkable.
- [hypothesis] Does an arced Rock throw from the summit make debris at a longer range? *(left notes on day 7)*
- [belief] (Debris addendum) Arced Rock throw from summit, dir y 0.7, also made 2 debris at ~15 range. So arcs work; debris count looks random 1-4 regardless of angle. *(left notes on day 7)*
- [mistake] (Throwing addendum) Ring thrown at 45 degrees from Peak summit (dir (1,1,0) speed 30) vanished from the world (like thrown ImpactBlocks). Don't throw the Ring if I want it back; Blocks and the Rock survive. *(left notes on day 7)*
- [mistake] Things can vanish when thrown: the Rock (flat toward the south rim from 3 away), the Ring (45 degrees from the summit), and any thrown ImpactBlock. Blocks have survived. Only throw what I can afford to lose; keep the Rock recoverable. *(left notes on day 8)*
- [hypothesis] Why do some thrown items vanish? (maybe fall out of bounds below the island) *(left notes on day 8)*

**Day 8: new rules**
- [belief] (Throwing addendum) From low ground, arcs with slope 0.5 and 1.0 both land ~13 away at speed 20 or 40: range looks capped ~13 for any moderate arc; only launch height (Peak) extends it. *(left notes on day 8)*
- [belief] (Throwing addendum) Low-ground range by slope: 0.25 -> ~11, 0.5 -> ~13, 1.0 -> ~13 (same at speed 20 or 40). *(left notes on day 8)*
- [belief] The bounds act as a wall for thrown Blocks too (a Block thrown east stopped at x=32, still present). *(left notes on day 8)*
- [hypothesis] Why do the Rock, Ring and ImpactBlocks vanish when thrown? Not simply the island edge (Blocks stop at the bound). Maybe small/light items are culled or fall through terrain. *(left notes on day 8)*
- [belief] (Open ideas addendum) The Ring thrown east toward the edge vanished while a Block thrown the same way stayed at x=32. Vanishing seems tied to small/thin items reaching the bound, not to Blocks. Untested: Rock thrown toward an edge. *(left notes on day 8)*
- [belief] Edge rule: a Block thrown into the island bound stops there (x=32) and stays. The Ring and the Rock thrown into the bound VANISH (no debris). Never throw them toward the rim; ImpactBlocks also vanished that way. Items lost until the reset. *(revised 1x)*
- [hypothesis] Why exactly do non-Block items vanish at the bound (fall through, culled)? Does a Rock thrown at the bound from the summit still vanish?

**Day 9: new rules**
- [belief] Tall towers: placing above ~6 blocks from ground fails OutOfRange. Place a block as a step beside the tower, jump onto it, then place (gains ~1 reach; worked for the 7th block).
- [belief] One step is enough for the 7th block but not the 8th; a 1,2 stair (columns beside tower, climb by jump+move_to) works for the 8th.
- [belief] Placing while airborne (jump then place) from the 2-high stair reached a 9th tower block at y~10.7. Don't walk between a tower and its stair when 1 apart: wedge; move_to along z frees you.

**Day 10: new rules**
- [belief] Throws toward a rising slope (Peak flank) land short (~7.5 at slope 0.5); throw from the summit down for range.
