"""
Shared parameters for the Green Lantern shot-pouring power battery.

ALL geometry in millimetres. Coordinate system for the ASSEMBLY: Z up, origin at the
centre of the base's bottom face. Each part module builds its part in its own natural
print orientation and exposes `assembly_transform()` info via build.py.

Everything here is a design decision that other modules depend on. Change values here,
never hard-code mating dimensions inside a part file. See DESIGN_CONTRACT.md.
"""

# ---------------------------------------------------------------- global look
SCALE = 1.8                 # original Hedo3D model was ~100 mm dia; we are ~180 mm
D_MAX = 190.0               # base bands and lower dish mouth (rev 9f: 180 -> 190 for room around the jar and pump)
WALL = 2.4                  # shell wall thickness (6 perimeters at 0.4 mm)
FLOOR = 2.0                 # floors / plates
FIT = 0.30                  # radial clearance per side for sliding / rotating printed fits
SNUG = 0.15                 # clearance per side for press / locating fits

# ---------------------------------------------------------------- hardware (measured or from datasheets)
M3_CLEAR = 3.4              # clearance hole for M3 screws
M3_INSERT_HOLE = 2.7        # M3 screws thread straight into the printed plastic (no heat-set inserts).
                            # Upgrade: set 4.0 for M3 x 5.7 mm heat-set inserts (4.6 mm OD) and re-run.
M3_INSERT_DEPTH = 6.5       # thread engagement depth (also fits a 5.7 mm insert + 0.8 for melt)
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
PUMP_L = 118.0              # Kamoer KPHM200 overall 115.6 mm (Amazon dims) + margin; head end = tube ports
PUMP_HEAD_D = 64.0          # KPHM200 is ~64 x 63 mm across the head (box-like); saddle for a 64 mm round/box
PUMP_MOTOR_D = 40.0         # motor can diameter (estimate; a 300 g 1:8 gear motor)
PUMP_W, PUMP_H = 64.0, 63.0 # envelope width/height when lying with the motor axis horizontal
TUBE_OD = 6.4               # 1/8" ID x 1/4" OD food-grade silicone for the head
TUBE_ID = 3.2
TUBE_GROMMET_D = 7.0        # hole for the tube to pass a wall

# Reservoir (rev 3): a SQUAT wide-mouth jar, refilled in place through the door with a funnel.
# 8 oz straight-sided PET jar, 70-400 neck, ~71 mm dia x ~72 mm tall with cap. Envelope below.
BOTTLE_D = 76.0             # jar envelope diameter (71 + cap/clearance)
BOTTLE_H = 76.0             # jar envelope height incl. cap; standing on the deck its cap stays below the door top
BOTTLE_NECK_D = 73.0        # 70-400 cap OD (tube + vent holes are drilled in the cap)

GLASS_D_TOP = 52.0          # envelope covers Libbey 5120 (51 top, 60 tall) and Torque 92440 Tritan (48 top, 54 tall)
GLASS_D_BASE = 40.0
GLASS_H = 62.0

POWERBANK_L, POWERBANK_W, POWERBANK_T = 70.0, 55.0, 40.0   # KBT 12 V 2400 mAh Li-ion pack (6 cells, 2 layers, protection board), flat on the tray
PORT_ANGLE = 90.0           # charge jack + power switch panel in the base's bottom band, on the owner's side
PORT_W, PORT_H = 42.0, 12.0 # notch in the drum's bottom band (open at the bottom); the tray's panel fills it
PORT_JACK_D, PORT_SWITCH_D = 8.0, 6.5   # panel-mount DC5521 jack (8 mm hole) and mini toggle switch (1/4" or M6 bushing)

# ---------------------------------------------------------------- stack (bottom to top)
BASE_H = 115.0              # base drum height (rev 3: taller so the reservoir jar + cap clear the door top)
BASE_BAND_H = 12.0          # decorative bands top and bottom at D_MAX
BASE_BODY_D = D_MAX - 6.0   # drum body between the bands (184)
SERVICE_SCREW_ANGLES = (0.0, 140.0, 225.0)   # rev 9: 3 thumbscrews from underneath hold the base cartridge in the drum (no door)

JOINT_SPIGOT_H = 8.0        # spigot height for base->lower dish and sphere->upper dish joints
JOINT_SCREWS = 3            # radial M3 screws per joint, 120 deg apart, first at +Y (rear)

DISH_H = 77.0               # reflector dish height (43 x 1.8)
DISH_MOUTH_D = D_MAX        # lower dish wide end outer diameter (matches the base)
UPPER_DISH_MOUTH_D = 180.0  # upper dish mouth: kept at 180 so the handle legs (which pass its rim) and the sphere bosses stay on the bed
DISH_NECK_D = 110.0         # narrow end outer diameter (sits on the sphere flat)
DISH_NECK_HOLE_D = 80.0     # through hole in the narrow floor (tube, wires, socket module)
DISH_RIM_H = 6.0            # straight cylindrical rim at the mouth

SPHERE_D = 180.0
SPHERE_CUT = 58.5           # flats at +/- SPHERE_CUT from the sphere centre (-> flat dia ~136.8)
SPHERE_SPLIT = 'front-back' # halves split on the XZ plane (front half y<0 toward audience, rear half y>0 toward owner)
SPHERE_FLANGE_W = 8.0       # internal joining flange width
SPHERE_SCREWS = 4           # M3 through the flange at the equator sides + top/bottom
WINDOW_W, WINDOW_H = 90.0, 87.0     # front arched window: must clear the 9 mm collars at both flats
DIFFUSER_D = 118.0          # front diffuser disc (sits behind the window on an internal ledge)
DIFFUSER_T = 1.0
HATCH_W, HATCH_H = 120.0, 96.0      # rear hand port (rev 6: open, no door; 120 wide so a 90 mm fist clears even 15 mm off-centre; 96 = all the height between the collars)
GLASS_TRAY_TRAVEL = 45.0    # the glass sits on a tray that slides out through the hatch on two rails in the bay floor
NOZZLE_ANGLE_DEG = 45.0     # nozzle enters from the rear-left wall at 45 deg aimed at the inside wall of the glass
NOZZLE_TIP_ABOVE_RIM = 10.0
STRIP_W = 10.0              # WS2812B strip width; strip channel inside the front half, around the window

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
ROTOR_FLOOR_T = 1.2         # plastic between magnet (in key cap) and Hall sensor
SOCKET_HOUSING_OD = 76.0    # rev 3: MUST pass through the DISH_NECK_HOLE_D (80) hole from above
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

# handle
HANDLE_SECTION_W, HANDLE_SECTION_T = 14.0, 10.0
HANDLE_INNER_GAP = 6.0      # clearance between sphere surface and handle leg (original: legs nearly tangent)
HANDLE_TOP_CLEAR = 80.0     # clearance above the upper dish mouth for a hand + ring
HANDLE_PIECES = 4           # 2 legs + 2 quarter arcs, lap joints with 2 x M3 each

# derived heights (assembly, Z from the ground)
Z_BASE_TOP = BASE_H
Z_LOWER_DISH_TOP = BASE_H + DISH_H
Z_SPHERE_CENTER = Z_LOWER_DISH_TOP + SPHERE_CUT
Z_SPHERE_TOP = Z_SPHERE_CENTER + SPHERE_CUT
Z_UPPER_DISH_TOP = Z_SPHERE_TOP + DISH_H
Z_HANDLE_TOP = Z_UPPER_DISH_TOP + HANDLE_TOP_CLEAR

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
DISH_LOWER_HOLE_D = 104.0    # lower dish floor hole: the slot and the tube pass through it into the dish cone
FIST_W, FIST_H, FIST_LEN, FOREARM_R = 106.0, 76.0, 85.0, 30.0   # owner's fist is under 4 x 3 in
FIST_Z_OFFSET = 3.0          # fist centre above the ring centre
CURTAIN_R = 62.0             # strip curtain hangs from the upper dish plug on this radius, behind the hand port
CURTAIN_HALF_ANGLE = 62.0    # arc spans +-62 deg either side of +Y (covers the 120 mm port seen from inside)
CURTAIN_SCREW_ANGLES = (40.0, 70.0, 110.0, 140.0)   # clamp screws into the upper dish plug (90 deg has the dish's radial screw)
