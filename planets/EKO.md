# Planet EKO: specification (observer's eyes only)

The agents' planet. They are never told any of this; everything they can observe follows from it.
Source of truth: `configs/eko.yaml` and `world/eko.py` (this sheet is generated from them).

## The planet
| quantity | value | Earth, for comparison |
|---|---|---|
| radius | 5,400 km | 6,371 km |
| circumference | 33,929 km | 40,030 km |
| mass | 3.757e+24 kg | 5.972e24 kg |
| mean density | 5,696 kg/m³ | 5,514 kg/m³ |
| surface gravity | 8.60 m/s² | 9.81 m/s² |
| escape velocity | 9.64 km/s | 11.19 km/s |
| solar day | 20 h | 24 h |
| sidereal day | 19.938 h | 23.934 h |
| year | 320 EKO days | 365.25 days |
| axial tilt | 18° | 23.44° |
| surface | one island (the agents' home) in a global ocean | |

## The island
Latitude 23° N; the celestial pole stands 23° above the northern horizon.
At the equinox the noon sun stands 67° high. Coastline 198.8 m.
On EKO a standing jump rises 1.48 m (1.30 m on Earth) and throws carry about 1.14x as far.

## The star (EKO's sun)
Apparent diameter 0.54°. The epoch (day 1) is EKO's spring equinox.

## The moon
| quantity | value |
|---|---|
| radius | 1,300 km |
| distance | 150,000 km |
| apparent diameter | 0.99° |
| orbital period (sidereal) | 10.12 EKO days (Kepler's third law from EKO's mass) |
| phase cycle (synodic) | 10.46 EKO days |
| inclination to EKO's orbit | 0.8° |
| EKO's full shadow at the moon | 3.61 moon radii across |

Lunar eclipses in the first 40 sessions (each session runs from one dawn to the next; dawn to dawn is 20 EKO hours):

| when (mid-eclipse) | type | visible from the island |
|---|---|---|
| session 3, 14.2 EKO h after dawn (noon = 5 h, dusk = 10 h, midnight = 15 h) | total | yes (moon 63 deg up) |
| session 14, 3.4 EKO h after dawn (noon = 5 h, dusk = 10 h, midnight = 15 h) | total | no (moon below the horizon) |
| session 24, 12.5 EKO h after dawn (noon = 5 h, dusk = 10 h, midnight = 15 h) | total | yes (moon 37 deg up) |
| session 35, 1.6 EKO h after dawn (noon = 5 h, dusk = 10 h, midnight = 15 h) | total | no (moon below the horizon) |

Each lasts about 4 EKO hours from first to last contact.

## What this lets an agent work out (answers we can score)
- The world is round: EKO's shadow on the moon is always a curved arc, whatever the moon's height in the sky (Aristotle).
- Its size: the shadow is 3.61 moon radii across at the moon; with the moon's apparent size and the eclipse's duration this bounds EKO's radius (Aristarchus).
- Its latitude: from the height of the point the stars turn around.
- Day, month and year lengths, and when the next eclipse comes.
- Local gravity, from throws and jumps.
