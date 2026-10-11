# NOTES - dishes module (`cad/parts/dishes.py`)

Parts: `dish_lower`, `dish_upper`. Both are one revolved (r, z) profile + insert bosses + holes. All numbers
derive from `params.py`; the mating numbers below are module-level constants other modules must import/match.

## Original reflector.stl, measured (trimesh sections) and what we reproduce at 1.8x
| feature (original, mm) | measured | ours (params) |
|---|---|---|
| mouth OD / height | 97.2 / 43 | 180 / 77 |
| outer cone angle from vertical | ~25 deg (r 31.9 -> 48.6 over z 4 -> 40) | **26.9 deg** (r 55 -> 90 over `CONE_H` = 77 - 6 - 2 = 69) |
| mouth rim, straight + rounded lip | ~1.5-3 mm straight, ~2 mm round | 6 mm straight (`DISH_RIM_H`), 1.5 mm chamfered lip on the upper mouth only |
| narrow end | flat annulus, hole 51.6, OD 62.8 (sits on the 77 sphere flat) | flat annulus, hole 80 (`DISH_NECK_HOLE_D`), neck 110, floor plate OD 136.8 (= sphere flat) |
| wall | ~5 mm (scaled-model wall) | 2.4 mm true thickness (radial offset 2.69 = WALL / cos 26.9) |

The two dishes have identical cone / rim / neck silhouettes (mirror images), so the stack keeps the hourglass look.

## Mating constants (module-level in dishes.py)
| constant | value | who must match it |
|---|---|---|
| `BASE_TOP_INNER_D` | 175.2 = D_MAX - 2 WALL | **base**: the top band bore the spigot slides into |
| `SPIGOT_OD` / `SPIGOT_ID` / `SPIGOT_H` | 174.6 / 169.8 / 8 | base (bore = 175.2 -> radial gap FIT = 0.3, verified from geometry) |
| `Z_BASE_JOINT_SCREWS` | 95 (= BASE_H - 5) | **base**: 3 radial M3_CLEAR holes (counterbored from outside) at this Z |
| `JOINT_BOSS_ANGLES` | [90, 210, 330] deg, first at +Y | base and sphere radial holes |
| `SPHERE_FLAT_D` | 136.8 | sphere |
| `SPHERE_OPENING_ID` | **132.0** = flat_d - 2 WALL | **sphere**: both flat openings must have this ID (bore / trim the inner edge of the shell to 132.0) for at least `LOCATING_RING_H_UPPER` (9 mm) depth from the flat. A plain 2.4 mm spherical shell has a 130.4 ID edge at the cut, so the sphere module must open it by 0.8 mm on diameter; above the flat the shell recedes outward anyway |
| `LOCATING_RING_OD` | 131.4 (radial gap FIT to 132.0, verified) | sphere |
| `LOCATING_RING_ID` | 126.6 (lower ring only) | bay_floor (OD 131 rests ON the ring top, not inside it) |
| `LOCATING_RING_H_LOWER` | 6.0 | sphere bottom opening depth |
| `LOCATING_RING_H_UPPER` | 9.0 (solid plug, see below) | sphere top opening depth |
| `BAY_FLOOR_SEAT_Z` | 183 = Z_LOWER_DISH_TOP + 6 | bay_floor / sphere (glass bay floor level) |
| `Z_SPHERE_LOWER_SCREWS` | 179 = Z_LOWER_DISH_TOP + 2 | **sphere**: 3 radial M3_CLEAR holes through the bottom flat collar, angles above |
| `Z_SPHERE_UPPER_SCREWS` | Z_SPHERE_TOP - 2 = 292 | **sphere**: 3 radial M3_CLEAR holes through the top collar |
| `DISH_FLANGE_D` | 136.8 | sphere flat bears on this plate (lower: top face, upper: underside) |
| `SOCKET_COUNTERBORE_D` / depth | 100.6 / 3.0 | socket faceplate (OD 100 x 3) sits flush with the upper floor top |
| `SOCKET_BOLT_ANGLES` | [45, 135, 225, 315] deg on `SOCKET_BOLT_CIRCLE` 88 | **socket**: 4 x M3 clearance holes in the faceplate at these angles |
| `Z_UPPER_FLOOR_TOP` / `Z_SOCKET_PLATE_SEAT` | Z_SPHERE_TOP + 2 / Z_SPHERE_TOP - 1 | socket module |
| `UPPER_FLOOR_HOLE_D` | 80 | socket housing must pass this (see Known issues) |
| `UPPER_WIRE_SLOT_W` x `_L` | 10 x 8 at +Y, in the hole edge (r 40..48), full floor depth | socket wire exit notch at +Y |
| `CONE_HALF_ANGLE_DEG` | 26.9 | handle / renders |

## Decisions (where the contract was silent, fuzzy or impossible)
1. **Neck floor is a full flange of OD = sphere flat (136.8), not just the 110 neck.** With the locating ring OD
   131.4 inside a 132 sphere opening, the sphere's flat edge (r 66..68.4) would otherwise rest on nothing. The flange
   gives the sphere a bearing face and looks exactly like the original's visible step between the 113 neck and the
   138 flat.
2. **45 deg collar between the cone and the flange on both dishes** (`COLLAR_ANGLE_DEG`). The lower dish prints mouth
   down, so the 13.4 mm outward flange would be a horizontal overhang at the top of the print; the collar makes it a
   45 deg overhang. The upper dish gets the same collar purely so the two necks look identical (it is a roof there).
3. **Lower floor annulus is supported by an internal 50 deg cone** (`FLOOR_SUPPORT_ANGLE_DEG`): the 12.3 mm inward
   floor (from the inner cone wall at r 52.3 to the 80 hole) would be a horizontal overhang at the top of the
   mouth-down print. The wedge is hidden inside the dish, costs ~36 cm3 of model volume (mostly infill) and stays clear
   of the bottle (r <= 31, top ~Z 138) and of the 80 mm pass-through. 50 deg was chosen over 45 deg (more plastic) and
   over 55-60 deg (PETG sags). Contract limit is 60 deg.
4. **Upper dish locating "ring" is a solid 9 mm plug** (annulus r 40..65.7) instead of a 2.4 mm ring with hanging
   bosses. A thin ring with 8 mm bosses below it and 4 socket bosses under the floor would leave the floor plate
   6+ mm above the bed with nothing under it; a solid plug prints flat on the bed and already contains every boss.
   Thickness = SOCKET_PLATE_T + M3_INSERT_DEPTH + 1.5 - FLOOR = 9: the 4 socket insert pockets go from the
   counterbore floor 6.5 mm down and leave a 1.5 mm skin above the bed. The 3 radial sphere pilots sit 2 mm below the
   flange underside with 7 mm of plug below them.
5. **Lower ring stays a thin 6 mm ring** (lighter, leaves room for tube/wires) with 3 radial boss blocks
   (10 wide x 8 radial x 8 tall, fused into the floor plate). "4 mm tall" from the contract was raised to 6 so the
   4 mm pilot at +2 keeps >= 1.5 mm of material above it in the boss.
6. **Spigot bosses stand on the bed** inside the spigot ring (10 wide x 8 radial x 10.4 tall, fused into the rim
   shoulder), pilots point outward from the spigot OD so the inserts are set from outside before assembly. A
   `RIM_SHOULDER_T` = 2.4 plate joins the spigot ring to the mouth rim (the spigot is inboard of the rim wall).
7. **Rim inner diameter is 174.6**, not 175.2: the rim wall is the same perpendicular 2.4 mm as the cone (radial
   2.69). Nothing mates with the rim ID.
8. **Upper wire slot is a 10 x 8 notch in the +Y edge of the 80 hole, under the faceplate**, not "just outside the
   counterbore": the counterbore (r 50.3) is only 2 mm from the inner cone wall (r 52.3), so there is no floor outside
   it inside the dish. The socket housing's +Y wire notch lines up with it; the faceplate covers it.
9. Socket bosses at 45/135/225/315 deg (not 0/90/...) so none collides with the +Y wire notch; each pocket keeps a
   1.7 mm wall to the 80 hole (BC 88 - insert 4.6 OD).
10. No hardware envelopes are returned by this module: the four envelope names `checks.py` knows (bottle, pump,
    powerbank, glass) belong to the base / sphere modules. Bottle clearance was checked by hand (above).

## Print orientation
- `dish_lower`: mouth DOWN, spigot ring on the bed (min z = 0), ring + bosses at the top. Print height 91 mm.
  Overhangs: cone inner surface 26.9 deg, collar 45 deg, floor support cone 50 deg, all < 60 deg -> **no supports**.
  One small exception: the rim bottom face steps 2.7 mm outward over the spigot at z = 8 (a short horizontal
  overhang, fine in PETG, kept flat because it is the bearing face on the base top band).
- `dish_upper`: floor DOWN, plug on the bed (min z = 0), mouth up. Print height 86 mm. Overhangs: cone outer surface
  26.9 deg, flange step 2.7 mm outward at z = 9 -> **no supports**.
- Cone angle from params: atan(35 / 69) = **26.9 deg from vertical**, well under the 60 deg limit.
- Both parts print in their assembly orientation, so `placements()` are pure Z translations
  (lower +92 = BASE_H - JOINT_SPIGOT_H, upper +Z_SPHERE_TOP - 9).

## Assembly / insertion
1. Set 6 heat-set inserts in `dish_lower` from OUTSIDE (3 in the spigot ring at Z 95, 3 in the locating ring at
   Z 179) and 3 radial inserts in the `dish_upper` plug from outside, plus 4 vertical inserts in the upper floor's
   counterbore (socket screws) before assembly.
2. Drop `dish_lower` into the base top band (spigot slides in with 0.3 mm radial clearance, rim rests on the band top);
   3 x M3 from outside through the base band into the spigot inserts, first screw at the rear (+Y).
3. Sphere halves register over the lower ring (inner edge of the bottom flat on the ring OD, flat on the flange);
   3 x M3 through the sphere's bottom collar at Z 179. The bay_floor disc (OD 131) rests on the ring top at Z 183.
4. `dish_upper` plug drops into the sphere's top opening, flange on the top flat; 3 x M3 through the sphere's top
   collar at Z_SPHERE_TOP - 2.
5. Socket module: faceplate into the 100.6 counterbore (top flush with the floor), 4 x M3 into the floor inserts;
   wires through the +Y notch at the hole edge.

## Known issues / for other modules
- **`SOCKET_HOUSING_OD` (92) > `DISH_NECK_HOLE_D` (80)**: a 92 mm housing hung under a 100 mm faceplate cannot pass
  the 80 mm floor hole, so the socket module must keep everything below the faceplate at <= 79.4 OD (hole - 2 FIT),
  or split the housing. The task explicitly asked for the 80 hole with bosses on the 88 bolt circle, so the hole was
  left at 80 (`UPPER_FLOOR_HOLE_D`); enlarging it past 83 would cut into the socket insert pockets.
- The sphere module must provide the 132.0 ID openings and the radial M3 holes at the Z / angles above; the collar
  region of the spherical shell near the flats is only 2.4 mm thick, so it may want a short internal collar there.
- Dishes are ~190-200 cm3 of model volume each (the 180 mm cone shell alone is ~85 cm3 at full density); expect
  ~150-200 g of PETG per dish with 30 % infill.
