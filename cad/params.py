"""
Shared parameters for the Green Lantern shot-pouring power battery.

ALL geometry in millimetres. Coordinate system for the ASSEMBLY: Z up, origin at the
centre of the base's bottom face. Each part module builds its part in its own natural
print orientation and exposes `assembly_transform()` info via build.py.

Everything here is a design decision that other modules depend on. Change values here,
never hard-code mating dimensions inside a part file. See DESIGN_CONTRACT.md.
"""
import math

# ---------------------------------------------------------------- global look
SCALE = 1.8                 # original Hedo3D model was ~100 mm dia; we are ~180 mm
D_MAX = 190.0               # base bands and lower dish mouth (rev 9f: 180 -> 190 for room around the jar and pump)
WALL = 2.4                  # shell wall thickness (printed as 4 perimeters + infill between them)
FLOOR = 2.0                 # floors / plates
FIT = 0.30                  # radial clearance per side for sliding / rotating printed fits
SNUG = 0.15                 # clearance per side for press / locating fits

# ---------------------------------------------------------------- hardware (measured or from datasheets)
M3_CLEAR = 3.4              # clearance hole for M3 screws
M3_INSERT_HOLE = 4.0        # brass heat-set insert bore, per the selected hardware plan
M3_INSERT_DEPTH = 6.5       # blind bore depth: exceeds the required 6 mm
M3_HEAD_D = 6.0             # socket head diameter (for counterbores)
MAGNET_D = 6.0              # 6 x 2 mm neodymium disc (owner has 45)
MAGNET_T = 2.0
MAGNET_POCKET_D = MAGNET_D + 0.3   # press fit pocket
MAGNET_POCKET_T = MAGNET_T + 0.2

NEOPIXEL_RING_OD = 65.5     # Adafruit 1586, 24 px
NEOPIXEL_RING_ID = 52.3
NEOPIXEL_RING_T = 3.2       # PCB thickness; LEDs add ~1.6 mm on top

XIAO_L, XIAO_W, XIAO_H = 21.0, 17.8, 3.5            # Seeed XIAO RP2040
D4184_L, D4184_W, D4184_H = 34.0, 17.0, 12.0        # dual MOSFET module
HALL_PCB_L, HALL_PCB_W, HALL_PCB_T = 31.0, 17.8, 1.6  # pocket fits the Adafruit DRV5032 board (25.6 x 17.8, slides along the length to centre its chip) or an A3144 module (31 x 15)
HALL_SENSOR_OFFSET = 3.0    # sensor element centre from the short PCB edge where it sits
D2F_L, D2F_W, D2F_H = 12.8, 5.8, 6.5                # D2F-L body (lever adds ~ 13.5 mm along L)
D2F_HOLE_D, D2F_HOLE_PITCH = 2.4, 6.5               # two mounting holes through the body
D2F_LEVER_LEN = 13.5                                # free end measured from the hinge pivot

# ---------------------------------------------------------------- pump / fluid (Kamoer KPHM200, 12 V)
PUMP_L = 118.0              # Kamoer KPHM200 overall, measured 114 mm (Kevin, 2026-10-23) + margin; head end = tube ports
PUMP_HEAD_D = 64.0          # head measured 2.5 x 2.5 in (63.5 mm square, Kevin); saddle for a 64 mm box
PUMP_MOTOR_D = 40.0         # silver motor can, measured 40 mm across and ~50 mm long (Kevin, 2026-10-23)
PUMP_W, PUMP_H = 64.0, 64.0 # envelope width/height when lying with the motor axis horizontal (63.5 measured)
TUBE_OD = 6.4               # 1/8" ID x 1/4" OD food-grade silicone for the head
TUBE_ID = 3.2
TUBE_GROMMET_D = 7.0        # hole for the tube to pass a wall

# Reservoir (rev 3): a SQUAT wide-mouth jar on the cartridge deck (rev 9: lift the lantern off to refill it).
# 8 oz straight-sided PET jar, 70-400 neck, ~71 mm dia x ~72 mm tall with cap. Envelope below.
BOTTLE_D = 76.0             # jar envelope diameter (71 + cap/clearance)
BOTTLE_H = 108.0            # jar envelope height incl. cap, standing on the deck (Kevin's 8 oz Ball jar: 100-105 mm, 73 mm across)
BOTTLE_NECK_D = 73.0        # 70-400 cap OD (tube + vent holes are drilled in the cap)

GLASS_D_TOP = 52.0          # envelope covers Libbey 5120 (51 top, 60 tall) and Torque 92440 Tritan (48 top, 54 tall)
GLASS_D_BASE = 40.0
GLASS_H = 62.0

POWERBANK_L, POWERBANK_W, POWERBANK_T = 105.0, 65.0, 25.0  # TalentCell YB1203000
# rev C: the battery and the board live in the top cap, on a separate cap floor plate.
# PACK FRAME (the measured numbers below): pack centred on the origin, length along Y, end face (port, rocker) at -Y,
# LED face down (2026-10-21) so its five fuel-gauge LEDs show through a slot in the plate under it.
BATTERY_STRAP_Y = 18.0      # pack frame: the hook-and-loop strap crosses here
BATTERY_STRAP_T = 2.0       # recessed under-plate strap allowance (VELCRO One-Wrap measured ~1 mm; 2 mm for margin)
PACK_BED_T = 1.0            # the pack lies on a 1 mm bed over the strap recess
# Electronics fit limits, not claims that unmeasured supplier parts have these dimensions.
PERFBOARD_W, PERFBOARD_H, PERFBOARD_T = 70.0, 50.0, 1.2
# Component sizes and mounting coordinates: docs/review/protoboard/mechanical.py and layout.py
BUCK_L, BUCK_W, BUCK_H = 43.0, 21.0, 14.0  # reserve above printed corner supports; measure actual module
BUCK_STANDOFF = 2.0
# Kevin's caliper numbers: port centre 14.3 mm and rocker centre 44.5 mm from the end face's left edge (port on the
# left, LEDs up); LED slot 12-17 mm in from the end edge and 14-40 mm from the port-side edge. LED face down mirrors X.
PACK_PORT_X = 32.5 - 14.3       # 18.2 (pack frame)
PACK_SWITCH_X = 32.5 - 44.5     # -12.0
PACK_LED_FROM_PORT = (14.0, 40.0)
PACK_LED_X = (32.5 - PACK_LED_FROM_PORT[1], 32.5 - PACK_LED_FROM_PORT[0])   # (-7.5, 18.5)
PACK_LED_FROM_END = (12.0, 17.0)
PACK_LED_IN = sum(PACK_LED_FROM_END) / 2          # slot centre, 14.5
PACK_LED_SLOT = PACK_LED_FROM_END[1] - PACK_LED_FROM_END[0]   # 5.0
# The battery lead is the splitter's straight male plug in the port (Kevin: 28.6 mm out, ~12 mm across); its cord
# folds back in a U-turn reaching BATTERY_PLUG_TURN from the battery's end.
BATTERY_PLUG_OUT, BATTERY_PLUG_D = 28.6, 12.0
BATTERY_PLUG_TURN = 35.0
# Cap layout. CAP-FLOOR FRAME: the lantern axis at the origin, z = 0 the top of the cap floor plate, -Y the display side.
PACK_CAP_XY = (27.5, -2.5)      # pack centre; turned 180 deg, so its end face (port) points to +Y and its LED row sits
                                # at y 35.5, x 9..35: inside the neck bore and on the hand side of the lock wall, so you
                                # read the charge dots by looking up through the hand opening
PACK_CAP_ROT = 180.0
BOARD_CAP_XY = (-38.0, 0.0)     # perfboard centre, component face up, turned 90 deg: its drawing's top edge toward -X
BOARD_CAP_ROT = 90.0            # (the cable exit to the wall side), its USB end toward -Y
BUCK_CAP_XY = (0.0, -69.5)      # LM2596 module, long side along X, past the battery's far end
SWITCH_CAP_XY = (-30.0, 60.0)   # S1 in a box on the plate, lever up, reached with the lid off
CHARGE_SOCKET_XY = (40.0, 60.0)    # the splitter's female end (the charge socket) stows here, along X, tied down loosely;
                                   # lift it out on its cord to charge with the lid off
CAP_WIRE_HOLE_XY = (-47.0, -55.0)  # the lock, LED and pump leads come up the neck and through the plate here
PORT_SWITCH_D = 6.5             # S1 mini toggle (1/4" or M6 bushing)

# ---------------------------------------------------------------- stack (bottom to top), rev C (2026-10-23)
# Classic proportions (Hal Jordan's battery): 80 mm drum, short flared foot neck, 224 mm sphere with lens bells, a
# mirrored top (neck, flare, 190 mm cap) holding the battery and board, emblem lid. Lower/upper dishes retired.
BASE_H = 80.0               # drum height: the pump (64 tall on a 3 mm floor) is the tallest thing in the cartridge
BASE_BAND_H = 12.0          # decorative bands top and bottom at D_MAX
BASE_BODY_D = D_MAX - 6.0   # drum body between the bands (184)
FLARE_ANGLE = 45.0          # foot and top flares, from vertical: the steepest overhang the printer takes unsupported
NECK_H = 25.0               # straight neck between each flare and the sphere flat (foot and top)
CAP_H = 80.0                # top cap cylinder, 190 mm across like the drum
CARTRIDGE_FLOOR_T = 3.0     # one-piece cartridge floor (replaces tray + deck)
JOINT_SPIGOT_H = 8.0        # spigot height: foot -> drum
JOINT_SCREWS = 3            # radial M3 screws per joint, 120 deg apart, first at +Y (rear)
JOINT_SCREW_ABOVE_FLAT = 3.0  # sphere <-> neck screws this far from the sphere flats

SPHERE_D = 224.0            # rev C: 180 -> 224, the largest half that fits the bed split front/back
SPHERE_FLAT_D = 136.8       # flats keep their size, so the neck joints are the old dish joints
SPHERE_CUT = math.sqrt((SPHERE_D / 2) ** 2 - (SPHERE_FLAT_D / 2) ** 2)   # 88.69: flats at +/- SPHERE_CUT
SPHERE_SPLIT = 'front-back' # halves split on the XZ plane (front half y<0 toward audience, rear half y>0 toward owner)
SPHERE_FLANGE_W = 8.0       # internal joining flange width
SPHERE_SCREWS = 4           # M3 through the flange at the equator sides + top/bottom
DIFFUSER_D = 118.0          # front lens: a full round 118 mm white disc in the front bell (rev C: no flats)
DIFFUSER_T = 1.0
LENS_OPENING_R = 57.0       # rev C: round opening in the front half; the lens bell's throat
HAND_OPENING_R = 65.0       # rev C: round hand opening in the rear half (fist 106 x 76 passes with 12 mm all round)
FRONT_BELL_L, REAR_BELL_L = 64.0, 60.0   # bell length from the sphere surface at the opening edge to the mouth
FRONT_BELL_MOUTH_R, REAR_BELL_MOUTH_R = 84.0, 90.0   # outer mouth radii
# Unused since rev 8 (kept so old notes still read): the glass tray, the 90 deg wall nozzle and the WS2812B strip channel.
GLASS_TRAY_TRAVEL = 45.0
NOZZLE_ANGLE_DEG = 45.0
NOZZLE_TIP_ABOVE_RIM = 10.0
STRIP_W = 10.0

# socket module (lives in the upper dish floor; see DESIGN_CONTRACT.md for the mechanism)
SOCKET_PLATE_D = 100.0      # faceplate OD, sits in a 100.6 mm counterbore in the dish floor
SOCKET_PLATE_T = 3.0
SOCKET_BOLT_CIRCLE = 88.0   # 4 x M3 into heat-set inserts in the dish floor
ROTOR_OD = 36.0             # rev 3: smaller rotor so a 30 mm compression spring covers the 45 deg arc at the skirt
ROTOR_H = 16.0
ROTOR_TRAVEL_DEG = 45.0
HALL_SENSOR = 'A3144'       # 'A3144' (Vetco, TO-92 "UA" package on a post up inside the rotor) or 'DRV5032' (Adafruit board under the plate)
A3144_L, A3144_W, A3144_T = 4.06, 3.05, 1.57   # UA package body: along the lead row, lead edge to top edge, thickness
A3144_ELEMENT_DEPTH = 0.5   # Hall element below the printed face
KEY_D = 24.0                # ring key cap disc diameter
KEY_T = 3.0
KEY_TAB_W, KEY_TAB_L = 6.0, 4.0
# key_ring (2026-10-19): the ring and its key in one print, the magnet hidden inside. Worn on the LEFT MIDDLE finger.
RING_ID = 20.5              # finger hole: measure the middle finger across the knuckle and change this one number
RING_HEAD_D = 27.0          # emblem head, as Hedo3D's fingerring_20mm (rests on the rotor face, outside the 24.6 mm pocket)
RING_HEAD_T = 6.1           # plastic between the face and the finger (the magnet pocket runs through it)
RING_PALM_W = 8.0           # band width on the palm side
RING_MAGNET_SKIN = 0.6      # plastic left over the magnet on the visible face (3 layers): hides it, +0.6 mm to the sensor
ROTOR_FLOOR_T = 1.2         # plastic between magnet (in key cap) and Hall sensor
SOCKET_HOUSING_OD = 76.0    # rev 3
SOCKET_HOUSING_H = 22.0     # below the faceplate (rev 3: shorter, frees bay height for the nozzle)
CAM_LIFT = 3.0              # D2F-L hinge lever rests 8 mm above its mounting face (2 mm preloaded from the 10 mm free position); the cam presses it to 5 mm
# Return spring (rev 4): a RADIAL spring plunger pressing on a ramp on the rotor's edge (rotary-switch detent).
# The ramp rises CAM_RISE over the 45 deg twist, so the spring force makes a return torque and a click at rest.
SPRING_D = 5.0              # compression spring OD
SPRING_WIRE = 0.5
SPRING_PRELOAD = 1.2        # compression at 0 deg
CAM_RISE = 4.0              # ramp height on the rotor edge over 45 deg
PLUNGER_L = 4.5
SPRING_FREE_L = 10.0        # 0.5 x 5 x 10 mm; compressed 1.2 at rest, 5.2 at 45 deg (solid height ~3)
SPRING_POCKET_D = 5.6       # spring OD + 0.6; closed ends; depth = free length + 1

# handle (rev C): a loop on ring pivots at the sphere's sides. Spokes run out along X from the pivots, a 30 mm corner
# turns them up, and a 230 mm arc goes over the top. It swings flat (either way) to lie around the middle for display.
HANDLE_SECTION_W, HANDLE_SECTION_T = 14.0, 10.0
HANDLE_LOOP_R = 235.0       # big arc radius (centreline): its inside clears the lid's edge by ~12 mm as it swings
HANDLE_CORNER_R = 30.0      # spoke -> arc corner; the big arc's centre is this far above the sphere centre
PIVOT_D, PIVOT_T = 44.0, 16.0   # ring pivot boss on each side of the sphere, over the seam
HANDLE_SHAFT_D = 12.0       # round shaft on the end of each spoke, turning in the pivot (flats at +/- T/2 for printing)

# derived heights (assembly, Z from the ground)
FLARE_H = (D_MAX - SPHERE_FLAT_D) / 2 / math.tan(math.radians(FLARE_ANGLE))   # 26.6
Z_BASE_TOP = BASE_H
Z_FOOT_FLAT = BASE_H + FLARE_H + NECK_H         # 131.6: foot neck top = sphere bottom flat
Z_SPHERE_CENTER = Z_FOOT_FLAT + SPHERE_CUT      # 220.3
Z_SPHERE_TOP = Z_SPHERE_CENTER + SPHERE_CUT     # 309.0: sphere top flat
Z_CAP0 = Z_SPHERE_TOP + NECK_H + FLARE_H        # 360.6: cap cylinder starts
Z_CAP_TOP = Z_CAP0 + CAP_H                      # 440.6: cap rim (the halo and lid sit on it)

# ---------------------------------------------------------------- lock wall layout (rev 8)
# Two openings in the sphere: the hand port on your side (+Y) and the display window on the far side (-Y).
# Just inside the hand port stands the LOCK WALL with the socket on its face; you punch in, ring face first.
# The glass sits in a slot under the lock: you lower it into the near end of the slot and push it back to the
# stop, where the wall crosses its back third. Behind the wall the nozzle pours into that back third, out of
# sight. To take it, grip the front of the glass, slide it toward you GLASS_SLIDE mm and lift it out.
# LED strips on both faces and the top edge of the wall light the hand port (through a strip curtain), the
# display window (through the diffuser) and the top dish (through a diffuser disc).
SOCKET_IN_SPHERE = True
LOCK_TWIST = 'ccw'           # twist direction as you see it: 'ccw' mirrors the whole lock left-right ('cw' = as designed)
SOCKET_Z_LOCAL = 4.0         # ring centre height, sphere frame (0 = sphere centre)
SOCKET_MODULE_DEPTH = 13.2   # socket face -> back of its base plate (socket.MODULE_DEPTH)
LOCK_FACE_Y = -12.0          # socket face (y); the wall's front face is SOCKET_MODULE_DEPTH behind it
LOCK_WALL_T = 2.4
SOCKET_STANDOFF = 0.0        # the base plate screws straight onto the wall
SOCKET_EAR_R = 53.0          # two mounting ears on the base plate
SOCKET_EAR_ANGLES = (40.0, 140.0)   # both below the lock: clear of the back LED rows and the front columns
GLASS_TOP_Z_LOCAL = -37.0    # glass rim: 3 mm under the lock and the wall's lower edge; ~13 mm stands above the slot
WELL_ID, WELL_WALL = 54.0, 2.0
GLASS_POUR_Y = -12.0         # glass centre at the back stop (= under the socket face)
GLASS_SLIDE = 29.0           # slide this far toward you, then lift: the rim then clears the socket face
WELL_RIDGE_H = 1.5           # ridge in front of the glass base at the stop: it clicks into place
NOZZLE_TIP_XY = (-2.7, -31.1)   # tube end behind the wall, 19 mm from the glass centre (rim inner radius ~23.5)
NOZZLE_TIP_OUT = 5.0         # tube length left sticking out of the guide
NOZZLE_RISE = 11.0           # straight rise above the bay floor before the bend
NOZZLE_BEND_R = 18.0         # bend radius (~3 x the tube OD): the riser stands outside the slot
NOZZLE_BEND_DEG = 135.0      # past horizontal: the tip points 45 deg down, so the stream dives into the glass
                             # instead of being thrown across it (a level tip threw it onto the rim at 70 % speed)
FIST_W, FIST_H, FIST_LEN, FOREARM_R = 106.0, 76.0, 85.0, 30.0   # owner's fist is under 4 x 3 in
FIST_Z_OFFSET = 3.0          # fist centre above the ring centre
# rev C: the strip curtain is a frosted disc slit into strips, clamped by its upper arc in the rear bell's mouth.
CURTAIN_HALF_ANGLE = 70.0    # clamped arc either side of the top
