> **Historical.** Revision C (2026-10-23) has no dishes: the foot (`parts/foot.py`) and the top cap (`parts/top.py`) replace them. See `DESIGN_CONTRACT.md`, revision C.

> **Superseded in part.** Written for revision 3 (180 mm lower dish mouth, the old base spigot). Since revision 9f the base bands and the lower dish mouth are `D_MAX` = 190 mm and the upper dish keeps 180 (`UPPER_DISH_MOUTH_D`); the current numbers are in `params.py` and `DESIGN_CONTRACT.md`.

# NOTES - dishes module (`cad/parts/dishes.py`)

Parts: `dish_lower`, `dish_upper`. Both are one revolved (r, z) profile + insert bosses + holes. All numbers
derive from `params.py` (rev 3: BASE_H = 115); the mating numbers below are module-level constants other
modules must import/match. The values quoted are what the module currently evaluates to.

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
| `BASE_TOP_INNER_D` | **169.2** - imported from `parts.base` (= BASE_BODY_D - 2 WALL; the base has one straight bore, the D_MAX band is a 5.4 mm wall). Fallback formula is the same if the base is not importable | base |
| `SPIGOT_OD` / `SPIGOT_ID` / `SPIGOT_H` | 168.6 / 163.8 / 8 | base (bore 169.2 -> radial gap FIT = 0.30, verified from the mesh incl. the boss corners) |
| `Z_BASE_JOINT_SCREWS` | 110 (= BASE_H - 5) | **base**: 3 radial M3_CLEAR holes (counterbored from outside) at this Z (base.py `BASE_JOINT_Z`, verified equal) |
| `JOINT_BOSS_ANGLES` | [90, 210, 330] deg, first at +Y | base and sphere radial holes |
| `SPHERE_FLAT_D` | 136.8 | sphere |
| `SPHERE_OPENING_ID` | **132.0** = flat_d - 2 WALL | **sphere**: both flat openings must have this ID (bore / trim the inner edge of the shell to 132.0) for at least `LOCATING_RING_H_UPPER` (9 mm) depth from the flat. A plain 2.4 mm spherical shell has a 130.4 ID edge at the cut, so the sphere module must open it by 0.8 mm on diameter; above the flat the shell recedes outward anyway |
| `LOCATING_RING_OD` | 131.4 (radial gap FIT to 132.0, verified incl. boss corners) | sphere |
| `LOCATING_RING_ID` | 126.6 (lower ring only) | bay_floor (OD 131 rests ON the ring top, not inside it) |
| `LOCATING_RING_H_LOWER` | 6.0 | sphere bottom opening depth |
| `LOCATING_RING_H_UPPER` | 9.0 (solid plug, see below) | sphere top opening depth |
| `BAY_FLOOR_SEAT_Z` | 198 = Z_LOWER_DISH_TOP (192) + 6 | bay_floor / sphere (glass bay floor level) |
| `Z_SPHERE_LOWER_SCREWS` | 194 = Z_LOWER_DISH_TOP + 2 | **sphere**: 3 radial M3_CLEAR holes through the bottom flat collar, angles above |
| `Z_SPHERE_UPPER_SCREWS` | 307 = Z_SPHERE_TOP (309) - 2 | **sphere**: 3 radial M3_CLEAR holes through the top collar |
| `DISH_FLANGE_D` | 136.8 | sphere flat bears on this plate (lower: top face at Z 192, upper: underside at Z 309) |
| `SOCKET_COUNTERBORE_D` / depth | 100.6 / 3.0 | socket faceplate (OD 100 x 3) sits flush with the upper floor top |
| `SOCKET_BOLT_ANGLES` | [45, 135, 225, 315] deg on `SOCKET_BOLT_CIRCLE` 88 | **socket**: 4 x M3 clearance holes in the faceplate at these angles |
| `Z_UPPER_FLOOR_TOP` / `Z_SOCKET_PLATE_SEAT` | 311 / 308 (Z_SPHERE_TOP + 2 / Z_SPHERE_TOP - 1) | socket module |
| `UPPER_FLOOR_HOLE_D` | 80 (SOCKET_HOUSING_OD 76 passes with 2 mm radial room; asserted in the module) | socket |
| `UPPER_WIRE_SLOT_W` x `_L` | 10 x 8 at +Y, in the hole edge (r 40..48), full floor depth | socket wire exit notch at +Y |
| `CONE_HALF_ANGLE_DEG` | 26.9 | handle / renders |
| `RIM_BEARING_W` / `RIM_GROOVE_W` | 2.69 / 3.0: flat bearing ring under the rim wall; 45 deg groove between it and the spigot | base top band (r 84.6..90): the dish bears on r 87.3..90 |

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
   mouth-down print. The wedge is hidden inside the dish (print z 65..83 = assembly Z 172..190), costs ~33 cm3 of
   model volume (mostly infill) and stays clear of the bottle (top Z 110) and of the 80 mm pass-through.
   50 deg was chosen over 45 deg (more plastic) and over 55-60 deg (PETG sags). Contract limit is 60 deg.
4. **Upper dish locating "ring" is a solid 9 mm plug** (annulus r 40..65.7) instead of a 2.4 mm ring with hanging
   bosses. A thin ring with 8 mm bosses below it and 4 socket bosses under the floor would leave the floor plate
   6+ mm above the bed with nothing under it; a solid plug prints flat on the bed and already contains every boss.
   Thickness = SOCKET_PLATE_T + M3_INSERT_DEPTH + 1.5 - FLOOR = 9: the 4 socket insert pockets go from the
   counterbore floor 6.5 mm down and leave a 1.5 mm skin above the bed. The 3 radial sphere pilots sit 2 mm below the
   flange underside with 5 mm of plug below them.
5. **Lower ring stays a thin 6 mm ring** (lighter, leaves room for tube/wires) with 3 radial boss blocks
   (10 wide x 8 radial x 8 tall, fused into the floor plate). "4 mm tall" from the contract was raised to 6 so the
   4 mm pilot at +2 keeps 2 mm of material above it in the boss.
6. **Spigot bosses stand on the bed** inside the spigot ring (10 wide x 8 radial x 14 tall, fused into the rim
   shoulder), pilots point outward from the spigot OD so the inserts are set from outside before assembly. The
   shoulder plate (spigot ID .. rim wall, print z 11..14) joins the spigot ring to the mouth rim.
7. **Spigot matches the base's real bore (169.2), and the rim underside is grooved.** The base drum has one straight
   bore (BASE_BODY_D - 2 WALL), so the spigot OD is 168.6 and the mouth rim (r 87.3..90) overhangs the spigot OD by
   3.0 mm. The rim underside between the spigot OD and the rim inner wall is a 45 deg roof (`RIM_GROOVE_ANGLE_DEG`,
   apex at print z 11.0) so only the rim wall footprint (`RIM_BEARING_W` = 2.69) is a flat ring printed over air;
   that ring is the bearing face on the base's top band (r 84.6..90). The groove roof sits 0.3 mm above the band's
   inner edge, so the dish rests on the flat ring only. The shoulder above the groove is 3.0 mm (>= WALL, asserted).
8. **Radial boss blocks are pulled in so their corners sit ON the mating cylinder.** A flat 10 mm wide face at the
   spigot / ring OD has corners at sqrt(r^2 + 5^2), i.e. 0.14-0.19 mm proud of the OD, which would eat half of the
   0.30 FIT. `_radial_block` now places the face at sqrt(r_outer^2 - (w/2)^2); the pilot still starts at the true OD.
9. **Rim inner diameter is 174.6**, not 175.2: the rim wall is the same perpendicular 2.4 mm as the cone (radial
   2.69). Nothing mates with the rim ID.
10. **Upper wire slot is a 10 x 8 notch in the +Y edge of the 80 hole, under the faceplate**, not "just outside the
    counterbore": the counterbore (r 50.3) is only 2 mm from the inner cone wall (r 52.3), so there is no floor outside
    it inside the dish. The socket housing's +Y wire notch lines up with it; the faceplate covers it.
11. Socket bosses at 45/135/225/315 deg (not 0/90/...) so none collides with the +Y wire notch; each pocket keeps a
    1.7 mm wall to the 80 hole (BC 88 - insert 4.6 OD).
12. No hardware envelopes are returned by this module (`checks.py` checks every `*_envelope`; they belong to the
    base / sphere / electronics modules). The full build's clearance check (base envelopes vs
    dish_lower) passes with 0 problems.

## Print orientation
- `dish_lower`: mouth DOWN, spigot ring + 3 bosses on the bed (min z = 0), ring + bosses at the top. Print height
  91 mm. Overhangs: cone inner surface 26.9 deg, collar 45 deg, floor support cone 50 deg, groove roof 45 deg, all
  < 60 deg -> **no supports**. One small exception: the flat bearing ring under the rim wall (2.7 mm wide, z = 8)
  is printed over air (short horizontal ledge, fine in PETG; kept flat because it is the bearing face).
- `dish_upper`: floor DOWN, plug on the bed (min z = 0), mouth up. Print height 86 mm. Overhangs: cone outer surface
  26.9 deg, flange step 2.7 mm outward at z = 9 -> **no supports**.
- Cone angle from params: atan(35 / 69) = **26.9 deg from vertical**, well under the 60 deg limit.
- Both parts print in their assembly orientation, so `placements()` are pure Z translations
  (lower +107 = BASE_H - JOINT_SPIGOT_H, upper +300 = Z_SPHERE_TOP - 9).

## Assembly / insertion
1. Set 6 heat-set inserts in `dish_lower` from OUTSIDE (3 in the spigot ring at Z 110, 3 in the locating ring at
   Z 194) and 3 radial inserts in the `dish_upper` plug from outside, plus 4 vertical inserts in the upper floor's
   counterbore (socket screws) before assembly. The spigot inserts have only 1.0 mm of plastic below them (the hole is
   3 mm above the spigot's bottom edge, fixed by the contract's Z = BASE_H - 5 with an 8 mm spigot): set them gently
   and not deeper than flush.
2. Drop `dish_lower` into the base top band (spigot slides in with 0.3 mm radial clearance, rim rests on the band top);
   3 x M3 from outside through the base band into the spigot inserts, first screw at the rear (+Y).
3. Sphere halves register over the lower ring (inner edge of the bottom flat on the ring OD, flat on the flange);
   3 x M3 through the sphere's bottom collar at Z 194. The bay_floor disc (OD 131) rests on the ring top at Z 198.
4. `dish_upper` plug drops into the sphere's top opening, flange on the top flat; 3 x M3 through the sphere's top
   collar at Z 307.
5. Socket module: faceplate into the 100.6 counterbore (top flush with the floor at Z 311), 4 x M3 into the floor
   inserts; wires through the +Y notch at the hole edge. Housing (OD 76, 22 tall) hangs to Z 287; the glass bay
   (floor 198 + glass 62 + 10 nozzle + 6.4 tube = 276.4) clears it by 10.6 mm.

## Known issues / for other modules
- The sphere module must provide the 132.0 ID openings and the radial M3 holes at the Z / angles above; the collar
  region of the spherical shell near the flats is only 2.4 mm thick (outer r 70.0 at the screw Z), so it may want a
  short internal collar there.
- Spigot insert pockets: 1.0 mm of plastic under the pilot (0.7 mm around a 4.6 mm insert), contract-driven (see
  Assembly 1). If this proves too fragile, the base could move its joint holes up to Z = BASE_H - 4.
- Dishes are ~200 cm3 of model volume each (the 180 mm cone shell alone is ~85 cm3 at full density); expect
  ~150-200 g of PETG per dish with 30 % infill.

## Review (independent reviewer, 2026-10-12)
Checked: build (no `!` lines), STL watertight / single body for both parts, bounding boxes on the bed (min z = 0),
renders (iso/front/top/underside + axial sections), mesh-measured fits, hole positions probed in the assembly frame
(`isInside` along each hole axis at the contract Z / angles), overhang faces, thin features (raster erosion of axial
sections at 1.0 and 2.3 mm), and the full build with `checks.py` (0 problems).

Problems found and fixed in `dishes.py`:
1. **Spigot did not fit the base (critical).** The module assumed the base top band bore = D_MAX - 2 WALL = 175.2 and
   made a 174.6 spigot; the base module (`parts/base.py`) has a straight 169.2 bore. The lower dish could not be
   assembled. Fix: `BASE_TOP_INNER_D` is now imported from `parts.base` (fallback: BASE_BODY_D - 2 WALL), spigot OD
   168.6, ID 163.8; mesh-verified: max r of the spigot incl. bosses = 84.300 = bore/2 - FIT.
2. **Rim underside overhang grew to 5.7 mm** with the smaller spigot (rim bottom r 84.3..90 over air). Fix: 45 deg
   groove roof from the spigot OD to the rim inner wall, flat bearing ring only under the rim wall (2.7 mm, same as
   the original design's ledge); shoulder thickness above the groove asserted >= WALL.
3. **Boss corners proud of the mating ODs.** The flat-faced radial boss boxes stuck out 0.14 mm (spigot) / 0.19 mm
   (locating ring) beyond the cylinder, halving the FIT clearance. Fix in `_radial_block` (face pulled in so the
   corners lie on the cylinder). Ring OD now 131.39 incl. corners.
4. Stale `SOCKET_HOUSING_OD 92` comment/notes (params rev 3 = 76): replaced by an assert that the housing passes
   the floor hole; NOTES Z values updated from BASE_H = 100 to BASE_H = 115 (joint screws 110, floor top 192, bay
   floor 198, sphere top 309, mouth 386).
Verified OK as designed: counterbore 100.6 x 3, socket pockets 4.0 x 6.5 with a 1.5 mm skin, wire notch, plug
pilots 2 mm under the flange, lower ring pilots with 2 mm above, floor 2.0 (FLOOR), cone wall 2.4 perpendicular,
all overhangs <= 50 deg except the two 2.7 mm bearing ledges, placements land every datum on the contract Z.
Not fixable here: the 1.0 mm skin under the spigot inserts (contract Z), see Known issues.
