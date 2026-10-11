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
D_MAX = 180.0               # nominal max outer diameter: base top band, dish mouths, sphere
WALL = 2.4                  # shell wall thickness (6 perimeters at 0.4 mm)
FLOOR = 2.0                 # floors / plates
FIT = 0.30                  # radial clearance per side for sliding / rotating printed fits
SNUG = 0.15                 # clearance per side for press / locating fits

# ---------------------------------------------------------------- hardware (measured or from datasheets)
M3_CLEAR = 3.4              # clearance hole for M3 screws
M3_INSERT_HOLE = 4.0        # pilot hole for M3 x 5.7 mm heat-set insert (4.6 mm OD) in PETG
M3_INSERT_DEPTH = 6.5       # pocket depth for the insert (insert 5.7 + 0.8 for melt)
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
HALL_PCB_L, HALL_PCB_W, HALL_PCB_T = 31.0, 15.0, 1.6  # HiLetgo A3144 module (verify yours)
HALL_SENSOR_OFFSET = 3.0    # sensor element centre from the short PCB edge where it sits
D2F_L, D2F_W, D2F_H = 12.8, 5.8, 6.5                # D2F-L body (lever adds ~ 13.5 mm along L)
D2F_HOLE_D, D2F_HOLE_PITCH = 2.4, 6.5               # two mounting holes through the body
D2F_LEVER_LEN = 13.5                                # free end measured from the hinge pivot

# ---------------------------------------------------------------- pump / fluid (Kamoer KPHM200, 12 V)
PUMP_L = 92.0               # overall length incl. motor (ESTIMATE until research confirms; bracket is a strap cradle)
PUMP_HEAD_D = 42.0          # pump head diameter (ESTIMATE)
PUMP_MOTOR_D = 30.0         # motor can diameter (ESTIMATE)
TUBE_OD = 6.4               # 1/8" ID x 1/4" OD food-grade silicone for the head
TUBE_ID = 3.2
TUBE_GROMMET_D = 7.0        # hole for the tube to pass a wall

BOTTLE_D = 62.0             # 8 oz PET Boston round incl. tolerance (ESTIMATE, verify)
BOTTLE_H = 136.0            # with cap
BOTTLE_NECK_D = 28.0        # 24-410 cap OD ~ 27-28

GLASS_D_TOP = 52.0          # shot glass envelope: 2 oz glass top OD
GLASS_D_BASE = 42.0
GLASS_H = 72.0

POWERBANK_L, POWERBANK_W, POWERBANK_T = 150.0, 72.0, 26.0   # pocket (strap-retained); most 10k banks are smaller

# ---------------------------------------------------------------- stack (bottom to top)
BASE_H = 100.0              # base drum height
BASE_BAND_H = 12.0          # decorative bands top and bottom at D_MAX
BASE_BODY_D = 174.0         # drum body between the bands
BASE_DOOR_W, BASE_DOOR_H = 110.0, 76.0   # rear service door opening in the base wall

JOINT_SPIGOT_H = 8.0        # spigot height for base->lower dish and sphere->upper dish joints
JOINT_SCREWS = 3            # radial M3 screws per joint, 120 deg apart, first at +Y (rear)

DISH_H = 77.0               # reflector dish height (43 x 1.8)
DISH_MOUTH_D = D_MAX        # wide end outer diameter
DISH_NECK_D = 110.0         # narrow end outer diameter (sits on the sphere flat)
DISH_NECK_HOLE_D = 80.0     # through hole in the narrow floor (tube, wires, socket module)
DISH_RIM_H = 6.0            # straight cylindrical rim at the mouth

SPHERE_D = 180.0
SPHERE_CUT = 58.5           # flats at +/- SPHERE_CUT from the sphere centre (-> flat dia ~136.8)
SPHERE_SPLIT = 'front-back' # halves split on the XZ plane (front half y<0 toward audience, rear half y>0 toward owner)
SPHERE_FLANGE_W = 8.0       # internal joining flange width
SPHERE_SCREWS = 4           # M3 through the flange at the equator sides + top/bottom
WINDOW_W, WINDOW_H = 108.0, 108.0   # front arched window (60 x 1.8 = 108)
DIFFUSER_D = 118.0          # front diffuser disc (sits behind the window on an internal ledge)
DIFFUSER_T = 1.0
HATCH_W, HATCH_H = 78.0, 92.0       # rear hatch opening (hand/glass access); magnet-latched cover
STRIP_W = 10.0              # WS2812B strip width; strip channel inside the front half, around the window

# socket module (lives in the upper dish floor; see DESIGN_CONTRACT.md for the mechanism)
SOCKET_PLATE_D = 100.0      # faceplate OD, sits in a 100.6 mm counterbore in the dish floor
SOCKET_PLATE_T = 3.0
SOCKET_BOLT_CIRCLE = 88.0   # 4 x M3 into heat-set inserts in the dish floor
ROTOR_OD = 44.0
ROTOR_H = 22.0
ROTOR_TRAVEL_DEG = 45.0
KEY_D = 24.0                # ring key cap disc diameter
KEY_T = 3.0
KEY_TAB_W, KEY_TAB_L = 6.0, 4.0
ROTOR_FLOOR_T = 1.2         # plastic between magnet (in key cap) and Hall sensor
SOCKET_HOUSING_OD = 92.0
SOCKET_HOUSING_H = 30.0     # below the faceplate
SPRING_D = 6.0              # compression spring OD (5-6 mm), ~0.5 mm wire, 20 mm free length
SPRING_FREE_L = 20.0
SPRING_POCKET_D = 7.0

# handle
HANDLE_SECTION_W, HANDLE_SECTION_T = 14.0, 10.0
HANDLE_INNER_GAP = 36.0     # clearance between sphere surface and handle leg
HANDLE_TOP_CLEAR = 80.0     # clearance above the upper dish mouth for a hand + ring
HANDLE_PIECES = 4           # 2 legs + 2 quarter arcs, lap joints with 2 x M3 each

# derived heights (assembly, Z from the ground)
Z_BASE_TOP = BASE_H
Z_LOWER_DISH_TOP = BASE_H + DISH_H
Z_SPHERE_CENTER = Z_LOWER_DISH_TOP + SPHERE_CUT
Z_SPHERE_TOP = Z_SPHERE_CENTER + SPHERE_CUT
Z_UPPER_DISH_TOP = Z_SPHERE_TOP + DISH_H
Z_HANDLE_TOP = Z_UPPER_DISH_TOP + HANDLE_TOP_CLEAR
