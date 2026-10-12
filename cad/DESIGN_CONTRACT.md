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
- Light = one plain 12 V green strip (18 x 5 cm pieces, 2 per carrier channel) switched by a MOSFET.
- The LM2596 buck sits in the left floor crescent of the base; the right crescent pocket is a spare.

## Revision 6 (punch-in layout) - supersedes the socket mounting, hatch and tray above
- The hand goes in horizontally like a punch through an open 120 x 96 mm port in the rear sphere half. No hatch
  door, hinge or hatch magnets.
- The socket is inside the sphere, its axis along +Y facing the port, ring centre `SOCKET_Z_LOCAL` = 11 mm above
  the sphere centre. `socket_base` grows two ears at r = 53 (+-X) that screw through two 8 mm `socket_standoff`s
  to the back of the LED carrier (2 x M3x20 + nuts). The housing has no faceplate flange.
- `top_cap` (a 3 mm disc with 4 countersunk M3 holes) closes the upper dish's old socket counterbore.
- The glass hangs in `glass_well`, a 54 mm ID cup that drops through the bay floor into the lower dish neck: rim
  at sphere z = -38, about 25 mm below the fist, so the fingers open straight onto it.
- The tube rises through the bay floor at (-34.5, -4) into `nozzle_guide`: 5.5 mm straight, then a 22 mm radius
  quarter bend that points the tip horizontally over the glass. The cable for the socket and LEDs goes down the
  7 mm hole at (+34.5, -4).
- Checks: the fist (100 x 58 mm ellipse, 85 mm long) and forearm (60 mm) envelopes must clear every part except
  the switch envelope.
