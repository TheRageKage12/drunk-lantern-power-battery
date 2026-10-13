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

## Revision 3 (after the adversarial design review, docs/research/design-critique.md) - supersedes conflicts above
1. **Reservoir = squat wide-mouth jar** (8 oz straight-sided PET, 70-400 neck, ~71 x 72 mm incl. cap; envelope
   BOTTLE_D x BOTTLE_H = 76 x 76). It stands on the base deck and is refilled IN PLACE through the rear door with a
   funnel (cap top must be below the door's top edge). Cradle: a ring ID 72, 8 mm tall, plus a strap. The cap is
   drilled for the 6.4 mm tube (snug 6 mm hole) and a 2.5 mm vent. BASE_H is now 115, door 110 x 90 (Z 12..102).
2. **Hatch and glass tray.** Hatch 110 x 105 mm rounded rectangle at +Y, centre Z = sphere centre - 8. The hatch
   DOOR is bottom-hinged (two 3 mm printed pins into 3.3 mm holes in the sphere wall, door stops at ~100 deg),
   magnet-latched at the top (2 pairs, magnets touching). The glass sits on a **glass_tray** (flat, 2 mm, with the
   glass ring ID GLASS_D_BASE+4 x 8 mm tall and a pull tab) that slides GLASS_TRAY_TRAVEL mm out through the hatch
   on two rails in the bay_floor (rails 3 mm tall, tray has matching grooves, an end stop so it cannot fall out).
   Pulling the tab presents the glass through the hatch; no reaching into the sphere.
3. **Socket module geometry.** SOCKET_HOUSING_OD = 76 so it passes the 80 mm dish hole from above (the faceplate
   100 mm sits in the counterbore). ROTOR_OD = 36, ROTOR_H = 16, SOCKET_HOUSING_H = 22. Cam lift CAM_LIFT = 5 mm
   (lever free 10 mm, operate ~6.8 mm above the switch mounting face), switch mount slotted +/- 2 mm. Return spring:
   compression 0.4 x 5 x 30 mm in a tangential closed pocket (5.6 wide, 31 deep) at the skirt; rotor arm at
   R = ROTOR_OD/2 + 1.5; preload 2 mm; compute and state the compression at 45 deg (expect ~17 mm). Stop pin = an
   M3 x 8 screw in a heat-set insert in the rotor skirt riding in the 45 deg arc slot (steel stop, replaceable);
   the loading gap at 90 deg lets the rotor drop in; slot ends keep >= 2.4 mm wall. Hall carrier accepts the
   DRV5032 breakout (primary, lies flat, sensor on the axis, 2 mm under the key-cap magnet) or the A3144 module.
   Key-cap bayonet: the key tab enters only at 0 deg, so the ring is removable only at rest.
4. **Nozzle.** The tube enters the bay from the rear-left wall at NOZZLE_ANGLE_DEG (45) aimed at the inside wall of
   the glass, tip NOZZLE_TIP_ABOVE_RIM (10) above the rim; the last 30 mm may be a rigid stainless 1/8" barb.
   nozzle_clip holds the tube at that angle. Bay free height = socket housing bottom - bay floor: assert the glass
   envelope + 10 mm + tube OD fits with the 45 deg approach (no U-bend).
5. **Power architecture (final).** ONE USB-C PD port of a bank that offers a 12 V PDO (INIU B61) -> 12 V PD trigger
   cable -> master switch -> 2 A fuse -> 12 V bus -> D4184 (pump) AND a 12 V -> 5 V buck (Pololu D24V22F5 or an
   LM2596 module) -> 3 A fuse -> 5 V bus (XIAO via a 1N5819 into its 5V pin, NeoPixels, 1000 uF). Simple alternative:
   Adafruit 3910 5 V pump + any 5 V/3 A bank, no 12 V at all. The 5 V -> 12 V step-up cable is a fallback only.
   Base electronics tray must fit: XIAO perfboard 50 x 70, D4184 34 x 17, buck module 44 x 22 x 14, two inline fuse
   holders, the PD trigger cable's inline module (~45 x 20 x 12). Door panel: 19 x 13 rocker cutout, 12 mm PRIME
   momentary button hole, panel-mount USB-C extension (24 mm hole) is NOT needed (the bank is charged through the
   door); add a 10 x 8 notch instead for the trigger cable if the bank's port faces the door.
6. **Firmware**: PRIME button on D6 (hold = pump runs, IDLE only, 20 s cap); pour-abort on Hall loss >= 60 ms;
   separate POURING brightness cap; brighter idle pilot glow (bank keep-alive); pump trigger via AHCT125 ch.3.

## Revision 4 (as built, see parts/socket.py and parts/sphere.py) - supersedes the socket section above
- Rotor: flat 36 x 8 mm disc. Under the faceplate lip its rim carries a printed STOP LUG (channel walls = hard
  stops at 0 and 45 deg), a CAM LOBE (3 mm lift, presses the D2F-L lever between ~33 and 45 deg) and a RAMP
  (4 mm rise over 45 deg). No loading gap: the rotor goes in from below and `socket_base` closes the housing
  with 3 x M3 into captured nuts. Return: a radial spring plunger (0.5 x 5 x 10 mm spring) on the ramp at 300 deg.
- Hall board sits chip-down in a pocket under `socket_base` with a sensor window on the axis (~8 mm to the
  magnet; fine for the DRV5032, A3144 users bend the sensor up through the window and stack magnets).
- Switch on a pegged `switch_bracket` in a slotted recess of the base plate. Module depth 13 mm below the
  faceplate plus the Hall connector.
- Sphere: window 90 x 87, hatch 110 x 96 bottom-hinged, glass on a sliding tray on a raised platform, LED
  carrier 9 rows x 6 px at y = -35, diffuser at y = -60. Handle 6 mm from the sphere (rear half 221 mm wide).
- Bed: the owner's Ender 3 is 230 x 230 x 240.

## Revision 5 (budget build, ~$140)
- M3 screws thread straight into 2.7 mm pilot holes (`M3_INSERT_HOLE`); 4.0 restores heat-set inserts.
- No NeoPixel ring or halo at the socket (`LED_RING = False` in parts/socket.py).
- No master-switch hole in the base door (`DOOR_SWITCH_D = 0`).
- Hall pocket widened to fit the Adafruit DRV5032 board (`HALL_PCB_W = 17.8`).
- Light = one plain 12 V green strip (16 x 5 cm pieces, 2 per carrier channel; 8 channels since rev 7) switched by a MOSFET.
- The LM2596 buck sits in the left floor crescent of the base; the right crescent pocket is a spare.

## Revision 6 (punch-in layout) - supersedes the socket mounting, hatch and tray above
- The hand goes in horizontally like a punch through an open 120 x 96 mm port in the rear sphere half. No hatch
  door, hinge or hatch magnets.
- The socket is inside the sphere, its axis along +Y facing the port, ring centre `SOCKET_Z_LOCAL` = 11 mm above
  the sphere centre. `socket_base` grows two ears at r = 53 (+-X) that screw through two 8 mm `socket_standoff`s
  to the back of the LED carrier (2 x M3x20 + nuts). The housing has no faceplate flange.
- `top_cap` (a 3 mm disc with 4 countersunk M3 holes) closes the upper dish's old socket counterbore.
- The glass hangs in `glass_well` below the fist (rim at sphere z = -32, ~20 mm under the knuckles). Revision 7
  replaces the round cup with a slot, see below.
- The tube rises through the bay floor into `nozzle_guide`: 5.5 mm straight, then a 22 mm radius quarter bend
  that points the tip horizontally over the glass. The socket and LED cables go down a 7 mm hole in the bay floor.
- Checks: the fist (100 x 58 mm ellipse, 85 mm long) and forearm (60 mm) envelopes must clear every part except
  the switch envelope. The hand port is 120 x 96 mm.

## Revision 7 (slide-out glass)
- A round well 52 mm deep made the glass rise 52 mm before it could move sideways, and the nozzle tip and the
  socket's lower edge both hang over that path. `glass_well` is now a 54 x 78 mm slot (`GLASS_SLIDE` = 24): the
  glass pours at the front end (centre y = -2) and is pulled back to y = +22 before it is lifted. A 1.5 mm ridge
  across the floor just behind the glass base holds it at the pour position (a gentle slope would not: glass on
  PETG needs ~15-20 deg to slide, and that would tip a full glass).
- Tube tip at (-14, -6), 14 mm from the pour centre and 28 mm from the lift axis (2 mm clear of the rim). The guide
  exit (grommet) is at (-41, -6); the cable hole at (+38, -6).
- `dish_lower` floor hole 80 -> 102 mm (`DISH_LOWER_HOLE_D`) so the slot hangs through it. The bay floor rests on
  the locating ring, not the hole edge.
- `glass_path_envelope` (the slide at rim height plus the vertical lift cylinder, rim + 1.5 mm) must clear every
  part. With `GLASS_SLIDE` near 0 it hits the socket and the nozzle guide, which is the bug this revision fixes.
- `glass_well` prints floor down, as it hangs, with a 45 deg skirt under the flange.
- Fixes found by an overlap audit at 0.05 cm3 (the build check fails only above 1 cm3):
  - `led_carrier`: the spacer posts pointed backward, and the untracked print-bed shift moved the whole carrier to
    the diffuser. Now the posts reach forward from the LED face to the diffuser and the back face is at y = -35,
    where the bay floor slots and the socket standoffs expect it. Height 104 -> 99 (it ran 4 mm into the upper
    dish plug), 8 LED channels at 11.5 mm pitch (the 9th was only 2 mm deep), notches in both bottom corners
    clear the bay floor drip lip.
  - `sphere.placements()` undoes each part's print-bed shift (`_SHIFT`) before rotating back. `sphere_rear` had
    been placed 3 mm too far back.
  - Front-half flange screws moved from 0/60/120/180 deg to 30/150/210/330 deg: the 60 and 120 deg bosses sat
    above the top flat, floating, where the upper dish plug goes.
  - The diffuser ledge and the diffuser are clipped to |z| < 49 so they stay off the dish plugs.
  - `glass_well` skirt reduced to 2 mm and seated in a 45 deg chamfer on the bay floor slot.

## Revision 8 (lock wall layout) - supersedes the socket mounting, LED carrier and glass position above
- Two openings: the hand opening on the owner's side (+Y, 120 x 96 mm, closed by a curtain of frosted
  polypropylene strips clamped under the upper dish plug on r = 62 by `curtain_clamp`) and the display window
  (-Y, diffuser). Light also leaves through the top: `top_diffuser` (1.2 mm frosted centre) replaces `top_cap`,
  with 5 pieces of 8 mm strip stuck around the 80 mm hole wall under it (the wall is 8 mm tall).
- `lock_wall` replaces `led_carrier`: 120 x 99 x 2.4 mm, front face at y = -25.2, standing in two bay floor slots
  with four posts to the diffuser. The lock (socket) screws straight onto its face with two ears at 40 and 140
  deg (2 x M3x10 + nuts; no standoffs); a 34 x 18 mm window behind the Hall board passes the cables. LED channels:
  4 rows of 2 x 5 cm on the back (display window), one 5 cm column either side of the lock on the front.
- Ring centre at z = +4 (socket face y = -12). The wall's lower edge is notched (66 mm wide) to 3 mm above the
  glass rim (z = -37). The glass is pushed back to the stop (centre y = -12, a 1.5 mm ridge clicks it in): the
  wall then crosses its back third. To remove it: slide 29 mm toward you, then lift ~49 mm (rim clears the lock
  face by 1.5 mm plus the envelope's 1.5 mm).
- The nozzle is behind the wall: `nozzle_guide` is now a C-channel (open toward the wall, which closes it) on a
  26 mm quarter bend from the tube exit at (-37, -31.1); the tube end at (-6, -31.1), z = -21.5, 20 mm from the
  glass centre. Cable hole at (35, -32). `DISH_LOWER_HOLE_D` 104.
- Fist envelope 106 x 76 mm (owner: under 4 x 3 in), centred 3 mm above the ring.
- `LOCK_TWIST = 'ccw'`: the owner twists counterclockwise (left hand, palm turning toward the glass). Every
  socket part is mirrored left-right (x -> -x in the socket frame) on output and its placement steps are
  conjugated by the same mirror; the mechanism code and `tests/test_socket.py` stay in the clockwise frame. The
  ears (40/140 deg) are a mirror pair, so the lock wall is unchanged. The key cap tab now rests at -X (your right).

## Revision 9 (base cartridge, no service door)
- The jar (76 mm tall on the deck at z 34) could not leave through the old door (top at z 102), and refilling
  in place was awkward. The base is now split: `base` is an open drum that stays with the lantern (joined to
  `dish_lower` by the same 3 radial screws), and the **cartridge** (`base_tray` + `base_deck` + bank + jar + pump
  + electronics) slides up into its open bottom. No door, no door magnets.
- Three thumbscrews from underneath (M3x12 glued into a printed `thumb_knob`, in 20 mm finger wells in the
  tray) go up into nuts in three bosses inside the bottom of the drum, at 0, 140 and 225 deg, r = 79. The
  bosses (r 75.5 .. wall, z 8..18, 45 deg roof, drum printed top band down) must pass down over the cartridge
  when the lantern is lowered on; the deck has notches at those angles.
- `service_sweep_envelope` (the bosses' path from z 8 up to the dish spigot zone) must clear the tray, the
  deck, the jar, the pump and the power bank; `checks.py` tests it against the hardware envelopes too.
  At 180 deg it would hit the jar and its ring, which is why the angles are uneven.
- Crossing the split: the tube keeps ~30 cm of slack (no joint in the drink path); the lock and LED cables get
  a 4-pin and a 2-pin plug.
- Power (rev 9a): VEGER 5000mAh 20W bank (77.2 x 35 x 24.7 mm, USB-C plug with 12V-1.6A PD) plus an AITRIP PDC004
  fixed-12V PD trigger board on its plug, replacing the Adafruit PD cable. The tray pocket has side rails and
  one central strap; the plug and board sit in the gap of the +Y end stop (`trigger_envelope`, also checked
  against the drum boss sweep). The deck drops 0.3 mm with the thinner bank.
- Power (rev 9b, supersedes 9a): KBT 12 V 1200 mAh 3-cell Li-ion pack, 70 x 55 x 20 mm, protection board and a
  DC5521 socket; no USB, no trigger board, no idle shut-off. The deck drops another 4.7 mm. The tray carries a
  port panel (curved 3 mm skin at the drum's inner wall, PORT_W x PORT_H, at PORT_ANGLE = 90, the owner's side)
  with an 8 mm hole for a panel-mount DC5521 charge jack and a 6.5 mm hole for a mini toggle switch (1/4" or M6 bushing); the drum
  has a matching notch open at its bottom edge so it lifts off over the panel. The jack is wired across the
  pack before the switch, so it charges in place with the switch off. Firmware reads the switched rail on D0
  through 100 k / 22 k, scales pump and LED duty by 12 / Vbat (0.8..1.4) and double-blinks on insertion below
  10.5 V. `trigger_envelope` is gone.
- Nozzle (rev 9c): with the tip level (90 deg bend, 15 mm above the rim, 20 mm from the glass centre) the
  stream left the tube at ~0.34 m/s at 70 % speed and travelled ~19 mm sideways before the rim plane, landing
  ~23 mm from the glass centre: on the rim of a 1.5 oz glass, and outside it at 100 %. `nozzle_guide` now
  bends NOZZLE_BEND_DEG = 135 (R 18, rise 11), so the tip points 45 deg down, 6.7 mm above the rim at
  (-2.7, -31.1). Projectile estimate: lands 19.2-19.4 mm from the glass centre from the last drop up to a
  1.5x pulse peak at 100 %. Guide top 1.3 mm under the lowest back LED row; tube exit unchanged at (-37, -31.1).
- Jar vent: a one-way (aquarium) check valve in the lid instead of an open hole, so a tipped jar can't leak.
- Hall sensor (rev 9d): `HALL_SENSOR = 'A3144'` (Vetco). Through the 4.5 mm rotor floor the A3144 sat ~5.5 mm from
  the 6x2 magnet: ~30 mT against a datasheet operate point of up to 35 mT. Now `rotor` has a 8.2 mm blind hole
  from below (1 mm skin under the magnet) and `socket_base` a 7.2 mm post with the sensor pocket on its tip,
  POST_TOP = skin - axial play (1.2) - 0.3, so a punch can't reach the sensor. Magnet to Hall element 3.0 mm
  (3.4 with the rotor at the lip): ~88 / 73 mT for N35. `tests/test_socket.py` checks the pushed-in rotor
  against the post. `'DRV5032'` restores the board pocket and window.
- Battery (rev 9e): KBT 12 V 2400 mAh, 70 x 55 x 40 mm (6 cells; the 1200 mAh pack's 1.2 A rating is at our
  ~1.3 A peak with a COB strip). The deck rises 18 mm (DECK_GAP 4 -> 2, the deck now holds the pack down).
  Fit checks pass, but the closest gaps are now radial, to the lower dish's inner wall above z 107: pump
  envelope top corner 0.98 mm, jar envelope 0.51 mm (the real jar, <= 73 mm with its lid, has ~2 mm). The
  pump envelope is an estimate: measure the head before printing base and dish_lower.
- LED strip: green COB, 8 mm, cut every 25 mm (HAMRVL B0CKYFLZFQ): back rows one 10 cm piece each, front
  columns 5 cm each, the top ring one 25 cm piece; ~0.6 A estimated for 75 cm.
- Wider base (rev 9f): D_MAX 180 -> 190 (base bands and the lower dish mouth; BASE_BODY_D = D_MAX - 6), so the
  raised jar and pump clear the lower dish's inner wall: pump envelope 6.0 mm, jar envelope 5.4 mm. The upper
  dish keeps a 180 mm mouth (UPPER_DISH_MOUTH_D, own cone slope): the handle legs pass its rim (2 mm), and moving
  them out would make sphere_rear ~231 mm wide, past the Ender 3 bed. The sphere is unchanged.
