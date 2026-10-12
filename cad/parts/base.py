"""
base.py - the lantern's base drum, its rear service door, the hardware deck, and the envelopes.

Parts (print orientation, bed = XY, min z = 0):
  base               drum, printed floor-down, open top (identity placement)
  base_door          curved rear door panel, printed standing on its bottom (lip) edge
  base_deck          flat deck plate that drops in over the power bank and carries the bottle
                     cradle, the pump saddles and the electronics panel (printed flat, identity + lift)
  bottle_envelope    stepped cylinder: body BOTTLE_D x BOTTLE_BODY_H_EST, shoulder, neck/cap to BOTTLE_H
  pump_envelope      KPHM200: head box PUMP_W x PUMP_H x PUMP_HEAD_L_EST + motor can PUMP_MOTOR_D, PUMP_L long,
                     lying with the motor axis along Y, head face toward the rear door
  powerbank_envelope box POWERBANK_W (X) x POWERBANK_L (Y) x POWERBANK_T (Z) lying flat on the floor

Assembly frame: Z up, origin at the centre of the base bottom, +Y = rear (door), -Y = front.
All numbers derive from params.py; the layout and the reasons are in NOTES-base.md.
"""
import math
import cadquery as cq
import params as P
from common import insert_boss, radial_hole, joint_angles

# ------------------------------------------------------------------ drum silhouette (contract)
R_MAX = P.D_MAX / 2                       # bands top and bottom
R_BODY = P.BASE_BODY_D / 2                # drum body between the bands
R_IN = R_BODY - P.WALL                    # inner wall radius, one straight bore from floor to top
BASE_TOP_INNER_D = 2 * R_IN               # MATING: dish_lower spigot OD = BASE_TOP_INNER_D - 2*FIT
BAND_STEP = R_MAX - R_BODY                # bands stand this far proud of the body (3.0)
BAND_TOP_Z0 = P.BASE_H - P.BASE_BAND_H    # bottom of the top band (88)
TOP_CHAMFER_H = BAND_STEP                 # 45 deg transition body -> top band (printable overhang)
BOTTOM_CHAMFER = 1.5                      # chamfer on the bottom outer edge (nod to the original's rolled foot)
SPIGOT_ZONE_Z0 = P.BASE_H - P.JOINT_SPIGOT_H   # the dish spigot occupies r <= R_IN above this Z (92)

# ------------------------------------------------------------------ dish joint screws (contract)
BASE_JOINT_Z_BELOW_TOP = 5.0
BASE_JOINT_Z = P.BASE_H - BASE_JOINT_Z_BELOW_TOP     # MATING: Z of the 3 radial M3 holes (95.0)
BASE_JOINT_ANGLES = joint_angles()                   # MATING: 90, 210, 330 deg (first at +Y)
BASE_JOINT_CBORE_DEPTH = 3.0
BASE_JOINT_R_OUTER = R_MAX                           # the holes start on the band's outer surface

# ------------------------------------------------------------------ rear door
DOOR_SILL = 10.0                                      # contract: bottom edge 10 mm above the floor
DOOR_Z0 = P.FLOOR + DOOR_SILL                         # 12
DOOR_Z1 = DOOR_Z0 + P.BASE_DOOR_H                     # 88 (= bottom of the top band)
DOOR_X_HALF = P.BASE_DOOR_W / 2
DOOR_LIP = 4.0                                        # outer plate overlap on left / right / bottom
DOOR_PLATE_T = 2.0                                    # outer plate thickness, proud of the body
DOOR_PLATE_R = R_BODY + DOOR_PLATE_T                  # 89; the bands are recessed to R_BODY under the lip
DOOR_PLUG_CHAMFER = 1.6                               # 45 deg under the plug so it prints standing up
DOOR_MAG_X = DOOR_X_HALF - 8.0                        # +/-47
DOOR_MAG_Z = (DOOR_Z0 + 6.0, DOOR_Z1 - 8.0)           # 18, 80
TAB_T = 4.0                                           # corner stop tabs inside the wall (magnet pockets)
TAB_IN = 14.0                                         # tab reach sideways into the opening
TAB_OUT = 6.0                                         # tab reach behind the wall (sideways / down)
TAB_Z_BOTTOM = (DOOR_Z0 - TAB_OUT, DOOR_Z0 + 10.5)    # 6..22.5  (stays under the deck)
TAB_Z_TOP = (DOOR_Z1 - TAB_IN, SPIGOT_ZONE_Z0 - 1.0)  # 74..91   (stays under the dish spigot)
DOOR_SWITCH_D = 0.0                                   # no master switch in the budget build (unplug the bank); 12.5 or 16 adds the hole
DOOR_SWITCH_XZ = (-30.0, 72.0)                        # upper left: nothing but the electronics panel behind it
USB_NOTCH_W = 14.0                                    # passes a USB-C plug body (12 x 6.5) + cable
SILL_NOTCH_H = 6.0                                    # notch in the base sill under the door opening (z 6..12)
DOOR_NOTCH_H = 7.0                                    # notch in the door's bottom edge (plate bottom + 7)
USB_X = 0.0                                           # the bank's ports are at the middle of its +Y end

# ------------------------------------------------------------------ power bank pocket (floor, centred)
BANK_HALF_W = P.POWERBANK_W / 2                       # 35.5 across X
BANK_HALF_L = P.POWERBANK_L / 2                       # 76.5 along Y, ports toward +Y (door)
BANK_END_STOP_T, BANK_END_STOP_H = P.WALL, 12.0
BANK_END_STOP_GAP = 0.3
BANK_END_STOP_X = (12.0, 20.0)                        # two blocks at +Y leaving the middle free for the plug
BANK_STRAP_Y = 31.0                                   # strap slot centres at y = +/- this
STRAP_SLOT_L, STRAP_SLOT_W = 22.0, 3.0                # for a 20 mm hook-and-loop strap

# ------------------------------------------------------------------ deck on pillars
PILLAR_S = 9.0                                        # square pillars
PILLAR_X = BANK_HALF_W + 1.0 + PILLAR_S / 2           # 41: inner faces also guide the bank sideways
PILLAR_Y = (-55.0, 0.0, 55.0)
PILLAR_INSERTS = ((PILLAR_X, 0.0), (-PILLAR_X, 0.0), (PILLAR_X, 55.0))   # 3 = unambiguous orientation
DECK_GAP = 4.0                                        # over the bank, room for the straps
DECK_Z0 = P.FLOOR + P.POWERBANK_T + DECK_GAP          # MATING: deck underside (23)
PILLAR_H = DECK_Z0 - P.FLOOR
DECK_T = 3.0
DECK_TOP = DECK_Z0 + DECK_T                           # MATING: everything on the deck starts here (26)
DECK_R = R_IN - P.FIT                                 # drops in from the open top
DECK_PORT_NOTCH = (30.0, 10.0)                        # notch in the deck edge at +Y to see the bank's ports

# ------------------------------------------------------------------ pump (on the deck, axis along Y)
PUMP_HEAD_L_EST = 40.0                                # head box length along the axis (estimate)
PUMP_MOTOR_L = P.PUMP_L - PUMP_HEAD_L_EST             # 78
PUMP_X = 30.0                                         # rev 3: shifted right 2 mm to clear the 76 mm jar ring (motor corner r 82.8)
PUMP_HEAD_FACE_Y = 52.0                               # head face (tube ports) toward the door
PUMP_AXIS_Z = DECK_TOP + P.PUMP_H / 2                 # 57.5
PUMP_HEAD_SADDLE_Y = PUMP_HEAD_FACE_Y - PUMP_HEAD_L_EST + 2.0 + 4.0   # U-saddle centre (y 20)
PUMP_HEAD_SADDLE_H, PUMP_SADDLE_T, PUMP_SADDLE_WALL = 20.0, 8.0, 8.0
PUMP_MOTOR_SADDLE_Y = PUMP_HEAD_FACE_Y - P.PUMP_L + 8.0 + 4.0          # half-round centre (y -54)
PUMP_HEAD_STRAP_Y = (28.0, 50.0)                      # deck slots either side of the head
PUMP_MOTOR_STRAP_Y = (-50.0, -28.0)                   # deck slots either side of the motor can
PUMP_STRAP_GAP = 1.5

# ------------------------------------------------------------------ bottle (on the deck, -X)
BOTTLE_RING_ID = P.BOTTLE_D + 1.0
BOTTLE_RING_WALL, BOTTLE_RING_H = 3.0, 10.0
BOTTLE_RING_GAP = 2.0                                 # ring OD to the pump head envelope
# rev 3: squat 8 oz jar (envelope BOTTLE_D x BOTTLE_H = 76 x 76). Front-left of the deck: the ring (OD 83) only
# reaches x = +1 at y = -8, where the pump is the 40 mm motor can (x 10..50), so it clears the head box (x -2..62).
BOTTLE_X = -40.0
BOTTLE_Y = -8.0
BOTTLE_FINGER_W, BOTTLE_FINGER_H, BOTTLE_FINGER_T = 12.0, 28.0, 3.0
BOTTLE_FINGER_ANGLES = (0.0, 120.0, 240.0)
# (the old stepped Boston-round envelope is gone: the jar is a plain cylinder)

# ------------------------------------------------------------------ electronics
# XIAO perfboard: vertical panel on the deck, rear-left, face toward the wall / visible through the door
EPANEL_ANGLE = 115.0                                  # direction (deg from +X) of the panel's normal
EPANEL_R = 56.0                                       # radius of the panel mid-plane
EPANEL_W, EPANEL_H, EPANEL_T = 52.0, 44.0, 3.0
EPANEL_GRID = (40.0, 30.0)                            # M3 insert pads (across, up)
EPANEL_PAD = 9.0
EPANEL_PAD_PROUD = P.M3_INSERT_DEPTH + 1.0 - EPANEL_T  # pad depth so insert pocket + 1 mm floor fit (4.5)
# Spare pocket on the base floor, right crescent (under the deck): fits a D4184 MOSFET module if you use one
# (the budget build puts its two MOSFETs on the perfboard instead)
D4184_XY = (56.0, 0.0)
D4184_OUTLINE = (P.D4184_W + 2.0, P.D4184_L + 2.0)   # 19 x 36 pocket outline
D4184_FRAME_T, D4184_FRAME_H = 1.2, 3.0
D4184_BOSS_D = 9.0
D4184_BOSS_GAP = 1.0                                  # edge-clamp bosses just outside the short ends
# LM2596 12 V -> 5 V buck module (43 x 21 mm) on the base floor, left crescent (under the deck)
BOOST_L, BOOST_W = 45.0, 20.0
BOOST_XY = (-58.0, 0.0)
BOOST_OUTLINE = (BOOST_W + 2.0, BOOST_L + 2.0)

# cable management / drains (base floor)
ZIPTIE_R = R_IN - 5.6                                 # 79
ZIPTIE_ANGLES = (50.0, 130.0, 230.0, 310.0)
ZIPTIE_SLOT = (4.5, 2.0)
ZIPTIE_PITCH = 7.0
DRAIN_D = 8.0
DRAIN_XY = ((-40.0, -68.0), (40.0, -68.0))
DECK_WIRE_SLOT = (14.0, 8.0)
DECK_WIRE_SLOTS_XY = ((PUMP_X, -70.0), (-25.0, 70.0))  # pump leads down to the D4184; XIAO / bank leads


# ------------------------------------------------------------------ small helpers
def _cyl(r, h, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(h)


def _ring(r_out, r_in, h, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r_out).circle(r_in).extrude(h)


def _box(lx, ly, lz, x=0.0, y=0.0, z0=0.0):
    """Box centred on (x, y) in plan, sitting on z0."""
    return cq.Workplane('XY').box(lx, ly, lz, centered=(True, True, False)).translate((x, y, z0))


def _rot_z(wp, deg):
    return wp.rotate((0, 0, 0), (0, 0, 1), deg) if deg else wp


def _union_all(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


def _cut_all(solid, cutters):
    for c in cutters:
        solid = solid.cut(c)
    return solid


def _wall_angle_at_x(x):
    """Angle (deg) of the point on the +Y inner wall with this x."""
    return math.degrees(math.atan2(math.sqrt(R_IN ** 2 - x * x), x))


def _radial_cutter(x, z, d, r0, r1):
    """Cylinder of dia d along the radial direction through (x, +Y wall, z), from radius r0 to r1."""
    a = math.radians(_wall_angle_at_x(x))
    n = cq.Vector(math.cos(a), math.sin(a), 0)
    origin = cq.Vector(r0 * math.cos(a), r0 * math.sin(a), z)
    return cq.Workplane(cq.Plane(origin=origin, normal=n)).circle(d / 2).extrude(r1 - r0)


def _frame(ow, ol, t, h, x, y, z0):
    """Raised rectangular outline (pocket wall) of inner size ow x ol."""
    return _box(ow + 2 * t, ol + 2 * t, h, x, y, z0).cut(_box(ow, ol, h + 2, x, y, z0 - 1))


def _slot_pair_cutters(x, y, pitch, slot_w, slot_l, z0, h, angle=0.0):
    """Two parallel floor slots (a cable-tie / strap anchor), rotated about the origin by angle."""
    out = []
    for s in (-1, 1):
        out.append(_rot_z(_box(slot_w, slot_l, h, x, y + s * pitch / 2, z0), angle))
    return out


# ------------------------------------------------------------------ drum
def _drum():
    """Outer silhouette: bottom band D_MAX, body BASE_BODY_D, 45 deg step, top band D_MAX; one bore."""
    bottom_band = _cyl(R_MAX, P.BASE_BAND_H).edges('<Z').chamfer(BOTTOM_CHAMFER)
    body = _cyl(R_BODY, BAND_TOP_Z0 - TOP_CHAMFER_H - P.BASE_BAND_H, z0=P.BASE_BAND_H)
    step = cq.Workplane('XY').add(cq.Solid.makeCone(R_BODY, R_MAX, TOP_CHAMFER_H,
                                                    pnt=cq.Vector(0, 0, BAND_TOP_Z0 - TOP_CHAMFER_H)))
    top_band = _cyl(R_MAX, P.BASE_BAND_H, z0=BAND_TOP_Z0)
    drum = _union_all([bottom_band, body, step, top_band])
    return drum.cut(_cyl(R_IN, P.BASE_H, z0=P.FLOOR))


def _door_opening_cutters():
    """Door opening, the USB plug notch in the sill, and the 1 mm band recesses the door plate sits in."""
    opening = _box(P.BASE_DOOR_W, 60.0, P.BASE_DOOR_H, 0, 70.0, DOOR_Z0)
    sill_notch = _box(USB_NOTCH_W, 60.0, SILL_NOTCH_H + 0.01, USB_X, 70.0, DOOR_Z0 - SILL_NOTCH_H)
    half_w = DOOR_X_HALF + DOOR_LIP + P.FIT
    outside_body = _cyl(R_MAX + 2.0, P.BASE_H).cut(_cyl(R_BODY, P.BASE_H))      # r > body: the lip sits on the body
    bottom_recess = _box(2 * half_w, 60.0, DOOR_LIP + P.FIT, 0, 70.0, DOOR_Z0 - DOOR_LIP - P.FIT)
    side_notch = _box(2 * half_w, 60.0, TOP_CHAMFER_H + 0.01, 0, 70.0, BAND_TOP_Z0 - TOP_CHAMFER_H)
    return [opening, sill_notch, bottom_recess.intersect(outside_body), side_notch.intersect(outside_body)]


def _door_tabs():
    """Four corner stop tabs inside the wall; the door plug rests on them, magnets pull it on."""
    tabs = []
    ann = _ring(R_IN, R_IN - TAB_T, P.BASE_H)
    for sx in (-1, 1):
        x0, x1 = sx * (DOOR_X_HALF - TAB_IN), sx * (DOOR_X_HALF + TAB_OUT)
        for (z_lo, z_hi) in (TAB_Z_BOTTOM, TAB_Z_TOP):
            tabs.append(ann.intersect(_box(abs(x1 - x0), 60.0, z_hi - z_lo, (x0 + x1) / 2, 70.0, z_lo)))
    return tabs


def _door_tab_pockets():
    return [_radial_cutter(sx * DOOR_MAG_X, z, P.MAGNET_POCKET_D, R_IN - P.MAGNET_POCKET_T, R_IN + 0.5)
            for sx in (-1, 1) for z in DOOR_MAG_Z]


# ------------------------------------------------------------------ base floor features
def _bank_pocket():
    """End stops for the flat power bank (sideways it is guided by the pillars) + 2 strap slot pairs."""
    y_stop = BANK_HALF_L + BANK_END_STOP_GAP + BANK_END_STOP_T / 2
    adds = [_box(2 * BANK_END_STOP_X[1], BANK_END_STOP_T, BANK_END_STOP_H, 0, -y_stop, P.FLOOR)]
    for sx in (-1, 1):   # +Y end: two blocks, the middle stays free for the charging plug
        xc = sx * (BANK_END_STOP_X[0] + BANK_END_STOP_X[1]) / 2
        adds.append(_box(BANK_END_STOP_X[1] - BANK_END_STOP_X[0], BANK_END_STOP_T, BANK_END_STOP_H, xc, y_stop, P.FLOOR))
    x_slot = BANK_HALF_W + PUMP_STRAP_GAP + STRAP_SLOT_W / 2
    cuts = [_box(STRAP_SLOT_W, STRAP_SLOT_L, P.FLOOR + 2, sx * x_slot, sy * BANK_STRAP_Y, -1)
            for sx in (-1, 1) for sy in (-1, 1)]
    return adds, cuts


def _pillars():
    adds, cuts = [], []
    for sx in (-1, 1):
        for y in PILLAR_Y:
            adds.append(_box(PILLAR_S, PILLAR_S, PILLAR_H, sx * PILLAR_X, y, P.FLOOR))
    for (x, y) in PILLAR_INSERTS:
        cuts.append(_cyl(P.M3_INSERT_HOLE / 2, P.M3_INSERT_DEPTH + 0.01, x, y, DECK_Z0 - P.M3_INSERT_DEPTH))
    return adds, cuts


def _floor_electronics():
    """D4184 pocket outline + 2 edge-clamp insert bosses (right crescent); boost module outline with
    two cable-tie anchors (left crescent). Both live under the deck."""
    adds, cuts = [], []
    dx, dy = D4184_XY
    ow, ol = D4184_OUTLINE
    adds.append(_frame(ow, ol, D4184_FRAME_T, D4184_FRAME_H, dx, dy, P.FLOOR))
    for sy in (-1, 1):
        c = (dx, dy + sy * (ol / 2 + D4184_FRAME_T + D4184_BOSS_GAP + D4184_BOSS_D / 2), P.FLOOR)
        boss, hole = insert_boss(None, c, boss_d=D4184_BOSS_D)
        adds.append(boss)
        cuts.append(hole)
    bx, by = BOOST_XY
    bw, bl = BOOST_OUTLINE
    adds.append(_frame(bw, bl, D4184_FRAME_T, D4184_FRAME_H, bx, by, P.FLOOR))
    for sy in (-1, 1):       # a cable-tie slot either side of the outline (across X), two ties along Y
        for sx in (-1, 1):
            cuts.append(_box(ZIPTIE_SLOT[1], ZIPTIE_SLOT[0], P.FLOOR + 2,
                             bx + sx * (bw / 2 + D4184_FRAME_T + 2.0), by + sy * bl / 4, -1))
    return adds, cuts


def _floor_cutters():
    """Cable-tie anchor slot pairs along the wall and the two drain holes at the front."""
    cutters = []
    for a in ZIPTIE_ANGLES:
        cutters += _slot_pair_cutters(ZIPTIE_R, 0.0, ZIPTIE_PITCH, ZIPTIE_SLOT[1], ZIPTIE_SLOT[0], -1, P.FLOOR + 2, a)
    for (x, y) in DRAIN_XY:
        cutters.append(_cyl(DRAIN_D / 2, P.FLOOR + 2, x, y, -1))
    return cutters


def _joint_screw_cutters():
    """3 radial M3 clearance holes through the top band, counterbored M3_HEAD_D x 3 from outside."""
    cutters = []
    for a in BASE_JOINT_ANGLES:
        cutters.append(radial_hole(BASE_JOINT_Z, a, BASE_JOINT_R_OUTER + 1, 1 + BASE_JOINT_CBORE_DEPTH, P.M3_HEAD_D))
        cutters.append(radial_hole(BASE_JOINT_Z, a, BASE_JOINT_R_OUTER + 1, BASE_JOINT_R_OUTER - R_IN + 2, P.M3_CLEAR))
    return cutters


def build_base():
    base = _cut_all(_drum(), _door_opening_cutters())
    adds, cuts = list(_door_tabs()), list(_door_tab_pockets())
    for fn in (_bank_pocket, _pillars, _floor_electronics):
        a, c = fn()
        adds += a
        cuts += c
    base = base.union(_union_all(adds))
    return _cut_all(base, cuts + _floor_cutters() + _joint_screw_cutters())


# ------------------------------------------------------------------ door panel
def _door_panel_assembly_frame():
    """Curved panel: outer plate (opening + lip left/right/bottom, proud of the body) and a plug that
    fills the opening flush with the inner wall. Built in the assembly frame."""
    y_half = _box(400.0, 100.0, 400.0, 0, 50.0, -100.0)   # keep only the +Y side
    plate = _ring(DOOR_PLATE_R, R_BODY, (DOOR_Z1 - P.FIT) - (DOOR_Z0 - DOOR_LIP), 0, 0, DOOR_Z0 - DOOR_LIP)
    plate = plate.intersect(_box(2 * (DOOR_X_HALF + DOOR_LIP), 100.0, 200.0, 0, 50.0, 0)).intersect(y_half)
    plug = _ring(R_BODY + 0.01, R_IN, P.BASE_DOOR_H - 2 * P.FIT, 0, 0, DOOR_Z0 + P.FIT)   # 0.01 overlap into the plate
    plug = plug.intersect(_box(2 * (DOOR_X_HALF - P.FIT), 100.0, 200.0, 0, 50.0, 0)).intersect(y_half)
    plug = plug.cut(cq.Workplane('XY').add(cq.Solid.makeCone(R_IN, R_IN + DOOR_PLUG_CHAMFER, DOOR_PLUG_CHAMFER,
                                                             pnt=cq.Vector(0, 0, DOOR_Z0 + P.FIT))))
    door = plate.union(plug)
    cuts = [_radial_cutter(sx * DOOR_MAG_X, z, P.MAGNET_POCKET_D, R_IN - 0.5, R_IN + P.MAGNET_POCKET_T)
            for sx in (-1, 1) for z in DOOR_MAG_Z]                                   # magnets, inside face
    if DOOR_SWITCH_D > 0:
        cuts.append(_radial_cutter(DOOR_SWITCH_XZ[0], DOOR_SWITCH_XZ[1], DOOR_SWITCH_D, R_IN - 1.0, DOOR_PLATE_R + 1.0))
    cuts.append(_box(USB_NOTCH_W, 60.0, DOOR_NOTCH_H + 1.0, USB_X, 70.0, DOOR_Z0 - DOOR_LIP - 1.0))   # USB notch
    return _cut_all(door, cuts)


def build_door():
    door = _door_panel_assembly_frame()
    bb = door.val().BoundingBox()
    shift = (0.0, -(bb.ymin + bb.ymax) / 2, -bb.zmin)
    return door.translate(shift), tuple(-s for s in shift)


# ------------------------------------------------------------------ deck (built in the assembly frame, then lowered)
def _bottle_cradle():
    r_in = BOTTLE_RING_ID / 2
    adds = [_ring(r_in + BOTTLE_RING_WALL, r_in, BOTTLE_RING_H, BOTTLE_X, BOTTLE_Y, DECK_TOP)]
    cuts = []
    for a in BOTTLE_FINGER_ANGLES:
        finger = _box(BOTTLE_FINGER_T, BOTTLE_FINGER_W, BOTTLE_RING_H + BOTTLE_FINGER_H,
                      r_in + BOTTLE_FINGER_T / 2, 0, DECK_TOP)
        slot_z0 = DECK_TOP + BOTTLE_RING_H + (BOTTLE_FINGER_H - STRAP_SLOT_L) / 2
        slot = _box(BOTTLE_FINGER_T + 2, STRAP_SLOT_W, STRAP_SLOT_L, r_in + BOTTLE_FINGER_T / 2, 0, slot_z0)
        adds.append(_rot_z(finger, a).translate((BOTTLE_X, BOTTLE_Y, 0)))
        cuts.append(_rot_z(slot, a).translate((BOTTLE_X, BOTTLE_Y, 0)))
    return adds, cuts


def _pump_cradle():
    """U-saddle for the box head, round-bottom saddle for the motor can, 4 deck slots for 2 straps."""
    half_w = P.PUMP_W / 2 + 0.5
    head = _box(2 * (half_w + PUMP_SADDLE_WALL), PUMP_SADDLE_T, PUMP_HEAD_SADDLE_H, PUMP_X, PUMP_HEAD_SADDLE_Y, DECK_TOP)
    head = head.cut(_box(2 * half_w, PUMP_SADDLE_T + 2, PUMP_HEAD_SADDLE_H + 2, PUMP_X, PUMP_HEAD_SADDLE_Y, DECK_TOP))
    r_m = P.PUMP_MOTOR_D / 2 + 0.5
    motor = _box(2 * (r_m + PUMP_SADDLE_WALL), PUMP_SADDLE_T, PUMP_AXIS_Z - DECK_TOP, PUMP_X, PUMP_MOTOR_SADDLE_Y, DECK_TOP)
    # XZ workplanes extrude toward -Y: start 1 mm behind the saddle and cut through it
    bore = cq.Workplane('XZ').workplane(offset=-(PUMP_MOTOR_SADDLE_Y + PUMP_SADDLE_T / 2 + 1)) \
        .center(PUMP_X, PUMP_AXIS_Z).circle(r_m).extrude(PUMP_SADDLE_T + 2)
    motor = motor.cut(bore)
    cuts = []
    for sx in (-1, 1):
        x_h = PUMP_X + sx * (P.PUMP_W / 2 + PUMP_STRAP_GAP + STRAP_SLOT_W / 2)
        x_m = PUMP_X + sx * (P.PUMP_MOTOR_D / 2 + PUMP_STRAP_GAP + STRAP_SLOT_W / 2)
        for (y0, y1), x in ((PUMP_HEAD_STRAP_Y, x_h), (PUMP_MOTOR_STRAP_Y, x_m)):
            cuts.append(_box(STRAP_SLOT_W, y1 - y0, DECK_T + 2, x, (y0 + y1) / 2, DECK_Z0 - 1))
    return [head, motor], cuts


def _electronics_panel():
    """Vertical plate on the deck with 4 M3 insert pads (EPANEL_GRID) on its wall-facing side.
    Built facing +X at the origin, then rotated to EPANEL_ANGLE and pushed out to EPANEL_R."""
    plate = _box(EPANEL_T, EPANEL_W, EPANEL_H, 0, 0, DECK_TOP)
    adds, cuts = [plate], []
    zc = DECK_TOP + EPANEL_H / 2
    for sy in (-1, 1):
        for sz in (-1, 1):
            yc, zp = sy * EPANEL_GRID[0] / 2, zc + sz * EPANEL_GRID[1] / 2
            x0, x1 = EPANEL_T / 2, EPANEL_T / 2 + EPANEL_PAD_PROUD
            # pad with a 45 deg underside so it prints without support (deck printed flat)
            prof = [(x0, zp - EPANEL_PAD / 2 - EPANEL_PAD_PROUD), (x1, zp - EPANEL_PAD / 2),
                    (x1, zp + EPANEL_PAD / 2), (x0, zp + EPANEL_PAD / 2)]
            pad = cq.Workplane('XZ').workplane(offset=-(yc + EPANEL_PAD / 2)).polyline(prof).close().extrude(EPANEL_PAD)
            adds.append(pad)
            hole = cq.Workplane(cq.Plane(origin=cq.Vector(x1 + 0.5, yc, zp), normal=cq.Vector(-1, 0, 0))) \
                .circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH + 0.5)
            cuts.append(hole)
    move = lambda wp: _rot_z(wp.translate((EPANEL_R, 0, 0)), EPANEL_ANGLE)
    return [move(a) for a in adds], [move(c) for c in cuts]


def build_deck():
    deck = _cyl(DECK_R, DECK_T, z0=DECK_Z0)
    adds, cuts = [], []
    for fn in (_bottle_cradle, _pump_cradle, _electronics_panel):
        a, c = fn()
        adds += a
        cuts += c
    deck = deck.union(_union_all(adds))
    for (x, y) in PILLAR_INSERTS:
        cuts.append(_cyl(P.M3_CLEAR / 2, DECK_T + 2, x, y, DECK_Z0 - 1))
    for (x, y) in DECK_WIRE_SLOTS_XY:
        cuts.append(_box(DECK_WIRE_SLOT[0], DECK_WIRE_SLOT[1], DECK_T + 2, x, y, DECK_Z0 - 1))
    cuts.append(_box(DECK_PORT_NOTCH[0], 2 * DECK_PORT_NOTCH[1], DECK_T + 2, USB_X, DECK_R, DECK_Z0 - 1))
    deck = _cut_all(deck, cuts)
    return deck.translate((0, 0, -DECK_Z0))         # print frame: flat on the bed


# ------------------------------------------------------------------ hardware envelopes (print frame = on z=0)
def _envelopes():
    bottle = _cyl(P.BOTTLE_D / 2, P.BOTTLE_H, BOTTLE_X, BOTTLE_Y)   # squat jar incl. cap (rev 3)
    head = _box(P.PUMP_W, PUMP_HEAD_L_EST, P.PUMP_H, PUMP_X, PUMP_HEAD_FACE_Y - PUMP_HEAD_L_EST / 2, 0)
    y_motor_end = PUMP_HEAD_FACE_Y - P.PUMP_L
    motor = cq.Workplane('XZ').workplane(offset=-(PUMP_HEAD_FACE_Y - PUMP_HEAD_L_EST + 0.01)) \
        .center(PUMP_X, P.PUMP_H / 2).circle(P.PUMP_MOTOR_D / 2).extrude(PUMP_MOTOR_L)
    pump = head.union(motor)
    bank = _box(P.POWERBANK_W, P.POWERBANK_L, P.POWERBANK_T, 0, 0, 0)
    return {'bottle_envelope': bottle, 'pump_envelope': pump, 'powerbank_envelope': bank}


_DOOR_SHIFT = None


def build():
    global _DOOR_SHIFT
    door, _DOOR_SHIFT = build_door()
    parts = {'base': build_base(), 'base_door': door, 'base_deck': build_deck()}
    parts.update(_envelopes())
    return parts


def placements():
    door_shift = _DOOR_SHIFT or build_door()[1]
    on_floor = ((0, 0, 1), 0, (0, 0, P.FLOOR))
    on_deck = ((0, 0, 1), 0, (0, 0, DECK_TOP))
    return {
        'base': ((0, 0, 1), 0, (0, 0, 0)),
        'base_door': ((0, 0, 1), 0, door_shift),
        'base_deck': ((0, 0, 1), 0, (0, 0, DECK_Z0)),
        'bottle_envelope': on_deck,
        'pump_envelope': on_deck,
        'powerbank_envelope': on_floor,
    }
