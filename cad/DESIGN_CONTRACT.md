# CAD design contract (read before touching any part file)

Units mm. Assembly frame: Z up, origin at the centre of the base bottom. "Front" = -Y (audience side,
diffuser window). "Rear" = +Y (owner side: base service door, sphere hatch). All numbers come from
`params.py`; part files import it and never hard-code mating dimensions.

Every part module lives in `cad/parts/<name>.py` and exposes:

```python
def build() -> dict[str, cadquery.Workplane]   # part name -> solid, in PRINT orientation (Z up on the bed)
def placements() -> dict[str, tuple[rotation_axis_tuple, angle_deg, (dx,dy,dz)]]  # print -> assembly
```

`build.py` imports every module, exports `cad/output/<part>.stl` (+ `.step`), builds the assembly
scene for renders, and runs the fit checks in `checks.py`.

## Stack and joints (bottom to top)
1. **base** (print open side up... i.e. floor on the bed): drum, outer bands `D_MAX` top and bottom,
   body `BASE_BODY_D`. Open top. Rear door opening `BASE_DOOR_W x BASE_DOOR_H` centred at +Y, bottom edge
   10 mm above the floor; a separate **base_door** panel (overlapping 4 mm lip, 4 magnets in pockets) covers it.
   Internal: 3 radial M3 clearance holes (`JOINT_SCREWS`, counterbored from outside) through the top band
   at Z = BASE_H - 5, first at +Y. The floor carries: bottle cradle ring (ID `BOTTLE_D`+1), pump strap
   cradle (two saddles for `PUMP_HEAD_D`/`PUMP_MOTOR_D`, 4 slots for a 20 mm hook-and-loop strap),
   power-bank tray (`POWERBANK_*`, strap slots), electronics tray with 4 M3 insert bosses on a 40 x 30
   grid plus a flat area, a 20 x 12 mm cutout in the floor edge for the master rocker switch? NO - the
   switch goes in the rear door panel (12 mm hole), the USB-C charge port is reached by opening the door.
   A `TUBE_GROMMET_D` hole and a 12 x 8 mm wire slot are NOT needed in the base (the top is open).
2. **dish_lower** (print mouth down = big end on the bed): cone from `DISH_MOUTH_D` (bottom) to
   `DISH_NECK_D` (top) over `DISH_H`, rim `DISH_RIM_H` cylindrical. A spigot ring (OD = base top inner
   diameter - 2*FIT, height `JOINT_SPIGOT_H`) hangs below the rim and carries 3 radial insert bosses
   (pilot `M3_INSERT_HOLE`) matching the base screws. Narrow end: flat annular floor with
   `DISH_NECK_HOLE_D` hole; the floor has a raised locating ring (OD = sphere flat dia - 2*FIT, 4 mm
   tall) that sits inside the sphere's bottom flat opening; 3 radial M3 clearance holes through the
   sphere wall mate with insert bosses in this ring (same pattern as the base joint, first at +Y).
3. **sphere_front / sphere_rear**: sphere `SPHERE_D`, truncated at +/- `SPHERE_CUT`, split on the XZ plane.
   Flat openings top and bottom have an inner ledge so the dish locating rings register. Internal joining
   flange `SPHERE_FLANGE_W` wide on the rear half along the split plane with 4 M3 clearance holes; the
   front half has matching insert bosses. Two 4 mm alignment pins. Front half: arched window
   (`WINDOW_W x WINDOW_H`, like the original: a tall arch with a round top) centred at -Y and Z = sphere
   centre; an internal ledge ring that holds **diffuser** (disc `DIFFUSER_D x DIFFUSER_T`, separate part
   printed in white/translucent) 6 mm behind the window; a 10.5 mm wide shallow channel around the window
   ledge for the WS2812B strip (adhesive back) facing inward/toward the diffuser edge. Rear half: hatch
   opening `HATCH_W x HATCH_H` (rounded rectangle) centred at +Y, Z = centre - 8; **sphere_hatch** cover with
   a 5 mm lip, 4 magnet pockets (mating pockets in the sphere wall), a finger notch at the bottom. Floor of
   the glass bay: the dish_lower locating ring hole is covered by a separate **bay_floor** disc (OD =
   `DISH_NECK_HOLE_D` - 2*FIT ... no: the bay floor sits ON the lower dish floor inside the sphere: disc
   OD = sphere flat dia - 2*WALL - 1, with a raised 2 mm lip (drip tray), a centred glass cradle ring
   (ID `GLASS_D_BASE`+4, 8 mm tall, 3 fingers), one `TUBE_GROMMET_D` hole at the rear-left for the
   tube coming up from the pump and a 14 x 8 mm wire slot at the rear-right. **nozzle_clip**: a small
   bracket that screws (1 x M3 insert) to the sphere's inner wall above and slightly behind the glass
   and holds the tube end (snap clip for `TUBE_OD`) pointing down into the glass centre, tip 12 mm above
   the glass rim.
4. **dish_upper** (print mouth UP, floor on the bed): mirror of dish_lower: narrow floor at the bottom
   with a locating ring that registers in the sphere's top flat, 3 radial insert bosses; the floor has a
   `SOCKET_PLATE_D` + 0.6 counterbore 3 mm deep and the `DISH_NECK_HOLE_D` through hole; 4 insert bosses
   on `SOCKET_BOLT_CIRCLE` for the socket module. Mouth `DISH_MOUTH_D` at the top. A 10 mm wire slot in
   the floor at +Y. The owner's hand goes into this dish to insert the ring.
5. **socket module** (several parts, see below) sits in the dish_upper floor, mechanism hanging down into
   the sphere's top region: keep its total depth below the faceplate <= `SOCKET_HOUSING_H`.
6. **handle**: `HANDLE_PIECES` pieces: two straight legs rising from bosses on the sphere equator at
   +/-X (boss: 14 x 10 mm socket, 12 mm deep, 1 x M3 insert each, printed as part of the sphere halves
   ... the equator is on the split plane, so each boss is split between the halves; instead put the bosses
   on the rear half 6 mm behind the split plane), and two quarter arcs meeting at the top centre with a
   lap joint (2 x M3 + nuts). Section `HANDLE_SECTION_W x HANDLE_SECTION_T`, rounded edges, inner
   clearance `HANDLE_INNER_GAP` from the sphere, top at `Z_HANDLE_TOP`. Optional 1/4" rod channel is NOT
   required.

## Socket module (the twist-to-pour mechanism)
Parts: **socket_housing** (faceplate + housing in one, printed faceplate DOWN on the bed),
**rotor**, **halo** (translucent ring over the NeoPixel ring), **key_cap** (glued to the ring),
**switch_bracket** (slotted, holds the D2F-L), **hall_carrier** (holds the A3144 PCB).
- Faceplate `SOCKET_PLATE_D x SOCKET_PLATE_T`, 4 x `M3_CLEAR` on `SOCKET_BOLT_CIRCLE`.
- NeoPixel ring recess from the TOP: annulus `NEOPIXEL_RING_OD`+0.6 / `NEOPIXEL_RING_ID`-0.6, depth
  `NEOPIXEL_RING_T` + 0.4, with a 3 x 6 mm wire notch to the underside; the **halo** ring (same annulus,
  4 mm tall, 1.2 mm top skin) snaps over it with 3 small tabs. The rotor bore (`ROTOR_OD` + 2*FIT) is
  inside the ring ID with >= 2 mm wall between bore and ring recess.
- Rotor: OD `ROTOR_OD`, height `ROTOR_H`. Top face: key pocket (disc `KEY_D`+2*FIT, depth `KEY_T`+0.5,
  plus the tab notch `KEY_TAB_W`+2*FIT wide, `KEY_TAB_L`+FIT deep radially, at 0 deg = +X). The pocket
  floor is `ROTOR_FLOOR_T` thick; the magnet sits in the key cap, centred on the rotation axis, so
  rotation does not move it relative to the Hall sensor below. Rotor skirt (below the faceplate):
  a radial stop pin (4 x 4 mm, 5 mm long) riding in a 45 deg arc slot in the housing wall; the slot has a
  loading gap at 90 deg so the rotor can be inserted at 90 deg then turned back (the spring arm prevents
  reaching 90 deg once installed) - this also retains the rotor axially. A cam lobe (ramps from 30 deg,
  full lift at 40 deg; lift 1.2 mm over the skirt OD) that presses the D2F-L lever. A spring arm
  (tangential post) that compresses a `SPRING_D` compression spring in a tangential pocket in the housing;
  spring is ~40% compressed at 0 deg (preload) and ~75% at 45 deg.
- Housing below the faceplate: OD `SOCKET_HOUSING_OD`, height `SOCKET_HOUSING_H`, open at the bottom;
  rotor bore through; arc slot; spring pocket (`SPRING_POCKET_D`, tangential, with a closed end);
  **hall_carrier** slot directly under the rotor floor (PCB `HALL_PCB_*` slides in from the side so the
  sensor element is on the axis, sensor face 0.4 mm below the rotor floor); switch bracket mounts with
  2 x M3 inserts and has 2 slotted holes (3.4 x 7 mm) so the switch position is tunable; wire exit
  notch at +Y to the dish floor's wire slot. Two 3 mm cable-tie slots.
- key_cap: disc `KEY_D x KEY_T`, tab `KEY_TAB_W x KEY_TAB_L` at +X, central magnet pocket on the
  UNDERSIDE (`MAGNET_POCKET_D x MAGNET_POCKET_T`, closed by 0.6 mm skin on top), top face slightly
  concave (0.5 mm) to glue onto a ring face. Also export **key_ring**: the original fingerring_20mm.stl
  with the key cap merged onto its flat emblem face (trimesh/manifold boolean union) so the owner can
  print a ready-made key ring.

## Print orientations and bed
All parts fit a 220 x 220 x 220 bed (largest: base/dish/sphere halves at 180 dia x <= 100 tall).
No part needs supports except the sphere halves (print open side down... i.e. the split plane on the bed,
the dome up; the window/hatch overhangs are < 60 deg because the arch tops are rounded). Document any
exception in build.py output.

## Checks (checks.py)
- Every solid is valid and watertight; volume > 0.
- Mating diameters: spigot ODs = bore IDs - 2*FIT (assert from the geometry, not from params only).
- Screw hole patterns coincide in the assembly frame (project the hole axes and compare).
- Clearance: bottle, pump, power bank, electronics envelopes (as boxes/cylinders in the assembly frame)
  do not intersect any wall (boolean intersection volume == 0) and do not intersect each other.
- Glass envelope + 12 mm nozzle gap + socket module depth fit between the sphere flats.
- Rotor can be inserted (slot loading gap) and turns 0..45 deg without the cam/pin/arm hitting walls
  (sweep check at 0, 15, 30, 40, 45 deg by boolean intersection of rotor vs housing == 0 except the
  spring pocket volume).
- Print envelope: bounding box of each part <= 220 x 220 x 220.

## Revision 2 (after hardware research) - supersedes anything above that conflicts
- The pump is the Kamoer KPHM200 (12 V): envelope ~116 x 64 x 63 mm, 300 g, tube ports on the head face
  (the face away from the motor). It no longer fits beside the bottle AND a flat power bank on the floor:
  put the power bank FLAT on the base floor (153 x 71 x 17) and the pump on a raised shelf/saddle above it
  (shelf top ~22 mm above the floor), lying with its motor axis horizontal, head toward the rear door so the
  tube can be loaded without removing the pump. Bottle stands at -X. Electronics tray at +X front. Base
  height may grow to 110 mm if needed (expose BASE_H use; the stack heights derive from it).
- Power: ONE 5 V port of the bank feeds everything; a 5->12 V step-up cable (max 1.2 A) hangs off the 5 V
  bus and feeds the MOSFET module. So the base needs room for: the bank, the boost cable's inline module
  (~45 x 20 x 12 mm), the D4184 module, the XIAO on a 40 x 30 perfboard, two inline fuse holders, the rocker
  switch in the door panel, and a panel-mount USB-C extension in the door panel (24 mm hole or 10 x 8 notch).
- Reservoir: 8 oz PET Boston round 57.2 x 132.6 mm, 24-410 cap (drilled: 6 mm tube hole + 2.5 mm vent).
- Shot glass: Libbey Torque 1.5 oz Tritan 54 mm tall / 48 mm top, or Libbey 5120 60 mm tall / 51 mm top.
  Serving 30 mL in ~9 s. Nozzle tip 10-15 mm above the rim, aimed at the inside wall of the glass.
- Lighting: 24-px NeoPixel ring in the socket; inside the sphere a 60/m WS2812B strip cut into 8 rows of
  7 px on a flat white-PETG 'led_carrier' plate ~110 x 110 mm standing 25 mm behind the front diffuser
  (it doubles as the front wall of the glass bay); ADD this part to the sphere module if not present:
  a plate with 8 parallel 10.5 x 1.5 mm shallow strip channels at 13 mm pitch, two tabs that drop into
  slots in the bay_floor, and a wire notch. The window-frame strip channel may stay as an alternative.
- The Hall sensor may be either the HiLetgo A3144 module (31 x 15 mm, sensor at the edge) or the Adafruit
  DRV5032 breakout (25.6 x 17.8 mm, sensor near the centre, JST PH at one end): make the hall_carrier a
  separate small part with the PCB slot length >= 32 mm and the stop position adjustable (two stop positions
  or a sliding stop), so the sensor element can be put on the rotor axis for either board.
