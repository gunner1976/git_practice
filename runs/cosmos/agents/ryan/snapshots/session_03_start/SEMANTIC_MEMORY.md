# SEMANTIC_MEMORY.md - What I Know and I Can Do

## Index
- World layout
- Pickup / place / stack
- Throw
- Movement
- Press

## World layout
- *fact* Island with hills (Peak, Hill_1..4), a mesa "Spire" at (-14,8), 12 loose 1x1 blocks (Block_1..12), a Ring, a Rock. Start at (0,0.7,-22). Day/night cycle passes quickly (a few ticks = hours).
- *fact* I built a tower (Blocks 12,7,1,10 + Ring) at x=-5.07, z=-18.5 near the start. Remaining loose blocks: 2,3,4,5,6,8,9 and Rock. Block_11 was lost to the sea.

## Pickup / place / stack
- *verified* move_to within ~1.5 units, then pickup at the object's position -> PickupSuccess.
- *verified* place only succeeds if the target is above ground/other blocks; aim ~1.5 above surface (or higher; it falls and settles). Too low = PlaceFailed:Occupied (inside terrain).
- *verified* Stacking: place at same x,z, y a bit above top block; settles at 1.0 spacing. Reach up to ~5 units high from the ground works.
- *verified* Ring can be picked/placed, but has no buttons.

## Throw
- *verified* throw {direction, speed}: speed 15 toward the island edge makes the item vanish (lost). Don't throw toward edges unless you accept losing it.
- *mistake* Throwing beside a tower collides and drops the item at my feet / I can end up standing on it. Step away first.

## Movement
- *fact* move_to is a straight line with no pathfinding; it stops early at blocks/terrain (Spire, tower). Use waypoints (e.g. x=-20 around the Spire, z=-22 south of the tower).
- *mistake* Near (-15,-14) I dropped to y≈-0.8 and move_to stalled. Choosing a different inland target freed me.

## Press
- *verified* press fails (NothingInReach) when holding the Ring. No entity with buttons found yet; explore for one.
- *hypothesis* Remaining unexplored: Rock, Peak summit, and whether blocks can be thrown to hit things.
- *verified* Thrown Rock at speed 14 (direction mostly horizontal, slight upward) traveled ~11 units and landed short; on impact it spawned a small debris entity "ImpactBlock_1" (0.4 cube). Throws are short-range/arcing; to hit a target ~15 away use more speed/upward angle.
- *verified* Throw calibration: direction vector [-4.6,1.5,-2.1] (target 5 away, slight upward) at speed 10 landed the Rock right beside its target. Direction is normalized by aim; speed ~10 reaches ~5 units, so range grows with speed (14 reached ~11). Light rock does not topple the tower.
- *verified* Throw calibration: direction [-4.6,1.5,-2.1] (target ~5 away, slight upward) at speed 10 landed the Rock right beside the tower; speed 14 earlier reached ~11. Range grows with speed. A light rock does not topple the tower.
- *verified* Block thrown at speed 13 (direction [-1,0.15,0]) from 8 units away stopped ~1.5 short of the tower and did not topple it; rough rule: flat range ≈ speed/2 to speed*0.8 units. The tower is very stable.
- *verified* Peak summit (12,4,12) is empty: no buttons or objects. Peak is the plain top of a hill (height ~4). Nothing pressable found anywhere so far; world seems to have no interactive entities besides movable parts.
- *verified* Spire mesa can't be walked or jumped onto (blocked at its edge, x≈-11.4). Idea: stack blocks (e.g. Block_6 nearby) as steps to reach its top.
- *fact* Spire top is y≈5.67, ground near it y≈2.1. Need ~3 stacked steps. Block_6 now placed at (-10,2.67,8) as the first step; Block_5 (-21,1,2) and Block_3 (-12,1.5,19.8) are the nearest spares. Place near Spire fails (Occupied) at x=-11.8; its edge is further out than it looks.
- *verified* Block_5 stacked on Block_6 at (-10,~3.7,8): 2-high column. I can't climb onto it with move_to (stops at its base); move_to won't climb even 1 block. Stairs need a ramp of different heights AND maybe jumping; untested whether jump clears 1 block. To reach Spire waypoint via (-11,2,1) when going west (Spire blocks the direct line).
- *verified* Jump then move_to onto a 2-block column fails. Climbing onto blocks/Spire seems impossible; abandon Spire-top plan (Peak summit was reachable only because it's a gentle slope). Column of Blocks 5,6 left at (-10,_,8).
- *verified* Block thrown from 3.5 units at speed 12, slight upward: landed at the tower base, tower unmoved. Thrown blocks seem to lose momentum on contact; I conclude the tower can't be toppled by throwing. Stop trying.
- *state* Current layout: tower (Blocks 12,7,1,10 + Ring) at (-5.07,_,-18.5) with Block_2 buttress at (-5.07,1.77,-17.4); column Blocks 6,5 at (-10,_,8) by the Spire. Free blocks: 3,4,8,9. Nothing to press, nothing climbable beyond hills.
- *verified* East edge walk: (18,-0.7,-21) and (23,-0.8,-3) are low shoreline spots (y≈-0.75); no entities out there. Island extends to roughly x=23 east.
- *mistake* Shoreline dips (y≈-0.75, e.g. (23,-3)) trap move_to; escape by targeting a nearby inland point to the west (e.g. (18,1,-8)), then continue. Stay off the shore.
- *state* Tower now has a 2-block buttress (Blocks 2,9) at (-5.07,_,-17.4). Free blocks: 3,4,8. Stable over time.
- *verified* Spire is walled on all four sides (stopped at x=-11.4 E, z=5.4 S, x=-16.7 W, ~z=10.1 N). Not walkable. No new entity visible on top in observe. A lunar eclipse was seen on night of 2026-05-03 (moon 93% shadowed).
