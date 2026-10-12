# NOTES - handle module (`cad/parts/handle.py`)

Parts (`HANDLE_PIECES` = 4): `handle_leg_left`, `handle_leg_right`, `handle_arc_left`, `handle_arc_right`.
A flat carrying arch in a plane parallel to the assembly XZ plane: two straight legs rising from bosses on the
sphere at +/-X, two quarter arcs of radius `ARC_R` meeting at the top centre (`Z_HANDLE_TOP`). No hardware
envelopes belong to this module.

## Original handle.stl, measured (trimesh) and what we reproduce
| feature (original, mm) | measured | ours (params) |
|---|---|---|
| arch | 134 wide x 148 tall x 6 thick; straight legs + a full semicircle (outer R ~67) | legs at centreline X = +/-131, semicircle R 131 on top, 276 wide x 234.5 tall (incl. the 12 mm plugs) |
| bar section | ~6 x 6, rounded | 14 (in-plane) x 10 (out of plane), 2 mm rounded edges (`HANDLE_SECTION_W x _T`, `EDGE_R`) |
| legs | inner faces ~120 apart on a 101 sphere (nearly tangent), small pegs at the ends | inner faces 248 apart (34 mm from the 180 sphere, see decision 1); plug ends go 12 mm into sphere bosses |

## Mating constants (module-level in handle.py)
| constant | value | who must match it |
|---|---|---|
| `LEG_X` | **131.0** = SPHERE_D/2 + HANDLE_INNER_GAP + HANDLE_SECTION_T/2 | **sphere**: centreline X of each boss pocket (+/-) |
| `HANDLE_PLANE_Y` | **7.4** = WALL + HANDLE_SECTION_T/2 | **sphere**: Y of the pocket centre (arch mid-plane, on the rear half) |
| `Z_BOSS_POCKET_TOP` | 250.5 = Z_SPHERE_CENTER | **sphere**: pocket mouth height (equator) |
| `BOSS_POCKET_DEPTH` | 12.0 | **sphere**: pocket depth (pocket floor at Z 238.5 = `Z_LEG_BOTTOM`) |
| `BOSS_POCKET_W` x `BOSS_POCKET_T` | 14.6 x 10.6 (= section + 2 FIT each way) | **sphere**: pocket size, 14.6 along X, 10.6 along Y, open at the top (+Z) |
| `LEG_SCREW_Z` | 244.5 = pocket top - 6 | **sphere**: 1 x M3 heat-set insert (pilot `M3_INSERT_HOLE`, depth `M3_INSERT_DEPTH`) in the pocket's INNER wall (sphere side), axis along X, at Y = `HANDLE_PLANE_Y` |
| `ARC_R` / `Z_ARC_CENTER` | 131 / 335 | renders only |
| `JOINT_SCREWS` | left: (-131, 317), (-131, 329); top: (-6, 465.9), (+6, 465.9); right: (131, 317), (131, 329) - (x, z), axes along Y | nobody (internal to the handle) |
| `W`, `T`, `LAP_L`, `LAP_T` | 14, 10, 24, 5 | - |

### Boss pocket requirement for the sphere module (summary)
Two bosses on the **rear** sphere half, mirror images at X = +/-131, Y = 7.4, equator height. Each is a rectangular
socket **14.6 (X) x 10.6 (Y) x 12 deep**, open upward, mouth at Z = 250.5, floor at Z = 238.5, with >= WALL
(2.4) around it; its front wall sits exactly on the split plane (Y = 0 .. 2.4). One M3 heat-set insert in the wall
on the sphere side of the pocket, hole axis along X at Z = 244.5, Y = 7.4 (the leg's clearance hole and a 6.6 x 2
counterbore for the screw head are on the leg's outer face, so the screw goes in from outside, pointing at the
lantern axis). The pocket centre is 41 mm outside the sphere surface, so the boss is an arm (or a bracket) reaching
out from the equator region of the rear half; it needs to carry the lantern's weight when lifted by the handle.
Suggestion: a 14 x 10 arm with a triangular gusset down the sphere surface, or a separate screwed-on bracket if the
sphere halves' print orientation (split plane on the bed, arm 2.4 mm above the bed, 40 mm cantilever) makes the
overhang awkward.

## Decisions (where the contract was silent, fuzzy or contradictory)
1. **`LEG_X` uses HANDLE_SECTION_T/2 as the task specified** (131.0), although the bar's radial (in-plane) dimension
   is W = 14, not T = 10, so the true inner clearance leg face <-> sphere is **34 mm** (`HANDLE_INNER_GAP_ACTUAL`),
   not 36. The value is kept because the sphere module is told to match this formula; changing it to W/2 is a
   one-line edit in both modules if a strict 36 mm is wanted.
2. **Arch plane at Y = 7.4** (`HANDLE_PLANE_Y` = WALL + T/2): the contract puts the bosses "on the rear half 6 mm
   behind the split plane". With a 10 mm pocket and a 2.4 mm front wall, 7.4 is the smallest offset that keeps the
   whole boss on the rear half with full wall thickness. The 7.4 mm offset of the arch from the lantern's centre
   plane is invisible on a 180 mm sphere. The sphere module may change it by changing this one constant.
3. **Semicircle radius = LEG_X (131) measured on the bar centreline**, top of the centreline at `Z_HANDLE_TOP` (466);
   the bar's outer surface is 7 mm above it and the clearance from the upper dish mouth to the underside of the
   arch is `HANDLE_TOP_CLEAR` - W/2 = 73 mm.
4. **Three lap joints, all split on the arch mid-plane** (half-thickness 5 mm laps, 24 mm long): leg <-> arc at the
   tangent points (the arc piece carries a 24 mm straight tangent run so the lap is straight) and arc <-> arc at the
   top (each arc overshoots the centre by 12 mm, trimmed by vertical planes at x = +/-12). Because the lap faces are
   parallel to the bed, each piece keeps the SAME half at all its laps (`KEEPS`: leg_left rear, arc_left front,
   arc_right rear, leg_right front), so printed with the removed side up every lap is a step cut from the top of the
   print and nothing overhangs. The leg top and arc tips are shortened by FIT (0.3) so the tips never jam on the
   shoulders; the lap faces themselves are a zero-clearance flat-on-flat fit (verified: zero overlap between placed
   pieces, and the union fills the full section at every lap).
5. **Screws: 2 x M3_CLEAR per joint, 12 mm apart, through the full 10 mm thickness along Y.** Nut pockets (hex,
   5.6 across flats, 2.6 deep, 2.4 mm of plastic left under them) open on the REAR (+Y, owner side) face, in the
   piece that keeps the rear half (leg_left for the left joint, arc_right for the top and right joints). The screw
   head sits on the front face without a counterbore (a 3 mm counterbore would leave only 2 mm of the 5 mm lap);
   use M3 x 12 button-head or socket-head screws. The hex pockets end up on the bed face of the print (the kept half's
   outer face is always down); the 2.4 mm roof of each pocket is a 5.6 mm bridge with the 3.4 hole in the middle -
   printable without supports.
6. **Boss screw across the plug along X** (not along Y): the pocket's Y walls are only 2.4 thick, too thin for a
   6.5 mm insert, whereas the pocket's inner (sphere-side) wall is the body of the boss arm. 0.8 mm lead-in chamfer on
   the plug end.
7. No fillets after the booleans: the rounded section comes from extruding / revolving a rounded-rectangle sketch,
   which is robust; lap steps and hole edges stay sharp.

## Print orientation
All four pieces print FLAT: arch plane on the bed, 10 mm tall, removed lap side UP, XY bbox centred on the origin,
min z = 0. No supports (the only bridges are the 5.6 mm nut-pocket roofs). Legs 14 x 96.2 x 10; arcs 149.7 x 161.7 x 10
(fit a 220 bed without rotation). 3-4 perimeters recommended; the laps and legs see the whole lantern's weight.
Placements are a +/-90 deg rotation about X (which face is up depends on `KEEPS`) plus a translation, computed
numerically in `_frames()` and verified to reproduce the assembly-frame solids exactly.

## Assembly / insertion
1. Lay the four pieces on a table rear face DOWN (hex pockets down): drop an M3 nut into each of the 6 hex pockets
   (leg_left: 2, arc_right: 4); a dab of glue keeps them in while assembling.
2. Lap the pieces: arc_left onto leg_left, arc_right onto arc_left at the top, leg_right under arc_right. The tips
   land against the shoulders with 0.3 mm play; the holes line up (verified in the assembly frame).
3. 6 x M3 x 12 from the FRONT face into the nuts. The assembled arch is 276 wide x 234.5 tall x 10.
4. Set the two heat-set inserts in the sphere bosses (axis along X, from the pocket side, or from outside through a
   pilot in the arm if the sphere module provides one). Plug both legs 12 mm into the bosses (0.3 mm clearance per
   side), then 2 x M3 x 10 through the legs' outer counterbored holes into the inserts.
5. The handle is removable as a unit (two screws) for transport; the arch pieces can also be printed in a contrasting
   colour.

## Known issues / for other modules
- The sphere module must provide the bosses described above; they are 41 mm outside the sphere surface, so they are
  structural arms, not simple pads (see the requirement block). `checks.py` currently has no handle-specific check;
  the boss pocket fit can be checked by intersecting the placed leg with the placed sphere_rear (expect 0) once the
  sphere module exists.
- `HANDLE_INNER_GAP` is realised as 34 mm (decision 1).
- Screw heads on the front face are proud (no counterbore).
