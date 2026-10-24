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
