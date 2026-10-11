"""
base.py - the lantern's base drum, its rear service door and the hardware envelopes.

Parts (print orientation, bed = XY, min z = 0):
  base               drum, printed floor-down, open top (identity placement)
  base_door          curved rear door panel, printed standing on its bottom edge
  bottle_envelope    cylinder BOTTLE_D x BOTTLE_H (clearance check only)
  pump_envelope      stepped cylinder: motor PUMP_MOTOR_D + head PUMP_HEAD_D, PUMP_L long, VERTICAL
  powerbank_envelope box POWERBANK_T x POWERBANK_L x POWERBANK_W standing on its long edge

Assembly frame: Z up, origin at the centre of the base bottom, +Y = rear (door), -Y = front.
All numbers derive from params.py; the layout decisions are in NOTES-base.md.
"""
import math
import cadquery as cq
import params as P
from common import insert_boss, magnet_pocket, radial_hole, joint_angles

# ------------------------------------------------------------------ drum silhouette (contract)
R_MAX = P.D_MAX / 2                       # bands top and bottom
R_BODY = P.BASE_BODY_D / 2                # drum body between the bands
R_IN = R_BODY - P.WALL                    # inner wall radius, straight from floor to top
BASE_TOP_INNER_D = 2 * R_IN               # MATING: the dish_lower spigot OD = this - 2*FIT
BAND_STEP = R_MAX - R_BODY                # how far the bands stand proud of the body (3.0)
BAND_TOP_Z0 = P.BASE_H - P.BASE_BAND_H    # bottom of the top band
TOP_CHAMFER_H = BAND_STEP                 # 45 deg transition body -> top band (printable overhang)
BOTTOM_CHAMFER = 1.5                      # small chamfer on the bottom outer edge (orig. rolled foot)

# ------------------------------------------------------------------ dish joint screws (contract)
BASE_JOINT_Z_BELOW_TOP = 5.0
BASE_JOINT_Z = P.BASE_H - BASE_JOINT_Z_BELOW_TOP     # MATING: Z of the 3 radial M3 holes (95.0)
BASE_JOINT_ANGLES = joint_angles()                   # MATING: 90, 210, 330 deg (first at +Y)
BASE_JOINT_CBORE_DEPTH = 3.0
BASE_JOINT_R_OUTER = R_MAX                           # hole starts on the band's outer surface

# ------------------------------------------------------------------ rear door (contract + decisions)
DOOR_SILL = 10.0                                      # contract: bottom edge 10 mm above the floor
DOOR_Z0 = P.FLOOR + DOOR_SILL                         # 12
DOOR_Z1 = DOOR_Z0 + P.BASE_DOOR_H                     # 88 (= bottom of the top band)
DOOR_LIP = 4.0                                        # overlap of the outer plate on left/right/bottom
DOOR_PLATE_T = 2.0                                    # outer plate thickness (stands proud of the body)
DOOR_PLATE_R = R_BODY + DOOR_PLATE_T                  # outer radius of the plate (89)
DOOR_PLUG_T = P.WALL                                  # plug = wall thickness, flush inside
DOOR_X_HALF = P.BASE_DOOR_W / 2
DOOR_MAG_INSET = 8.0                                  # magnet centres from the opening edges
DOOR_MAG_X = DOOR_X_HALF - DOOR_MAG_INSET             # +/-47
DOOR_MAG_Z = (DOOR_Z0 + DOOR_MAG_INSET, DOOR_Z1 - DOOR_MAG_INSET)   # 20, 80
TAB_T = 4.0                                           # corner stop tabs inside the wall
TAB_IN = 14.0                                         # tab reach into the opening (past the edge)
TAB_OUT = 6.0                                         # tab reach behind the wall
DOOR_SWITCH_D = 12.5                                  # panel-mount rocker / latching switch hole
DOOR_SWITCH_XZ = (-28.0, 62.0)                        # over the electronics tray side
DOOR_USB_NOTCH_W, DOOR_USB_NOTCH_H = 10.0, 8.0        # USB-C cable notch in the bottom edge
DOOR_USB_NOTCH_X = 19.0                               # centred over the power bank's +Y end

# ------------------------------------------------------------------ interior layout (see NOTES-base.md)
# bottle, front-left
BOTTLE_XY = (-33.0, -15.0)
BOTTLE_RING_ID = P.BOTTLE_D + 1.0
BOTTLE_RING_WALL = 3.0
BOTTLE_RING_H = 10.0
BOTTLE_FINGER_W, BOTTLE_FINGER_H, BOTTLE_FINGER_T = 12.0, 28.0, 3.0
BOTTLE_FINGER_ANGLES = (90.0, 210.0, 330.0)
STRAP_SLOT_L, STRAP_SLOT_W = 22.0, 3.0               # for a 20 mm hook-and-loop strap

# pump, front-right, standing VERTICAL (motor down, head up) - see NOTES for why not horizontal
PUMP_XY = (56.0, -22.0)
PUMP_HEAD_L_EST = 40.0                                # head length estimate (motor = PUMP_L - this)
PUMP_MOTOR_L = P.PUMP_L - PUMP_HEAD_L_EST             # 52
PUMP_RING_ID = P.PUMP_MOTOR_D + 1.0
PUMP_RING_WALL = 3.0
PUMP_RING_H = 12.0
PUMP_SADDLE_T = 8.0
PUMP_SADDLE_H = 36.0                                  # top well below the head shoulder (z 2 + 52)
PUMP_SADDLE_SPAN = 160.0                              # degrees of the half-round, on the wall side
PUMP_SADDLE_SLOT_ANGLE = 50.0                         # strap slots at +/- this from the saddle centre
PUMP_SADDLE_SLOT_Z0 = 8.0                             # slot bottom above the floor
PUMP_FLOOR_SLOT_OFFSET = 25.0                         # floor slots either side for an over-the-top strap

# power bank, right, standing on its long edge, ports toward the door (+Y)
POWERBANK_X0 = 7.0
POWERBANK_X1 = POWERBANK_X0 + P.POWERBANK_T           # 33
POWERBANK_STOP_H = 12.0
POWERBANK_STOP_T = P.WALL
POWERBANK_SLOT_Y = 40.0                               # strap slots at y = +/- this
POWERBANK_SLOT_GAP = 1.5                              # slot inner edge from the bank face

# electronics tray, rear-centre-left (behind the door)
TRAY_XY = (-19.0, 48.0)
TRAY_L, TRAY_W, TRAY_H = 50.0, 40.0, 2.0
TRAY_GRID = (40.0, 30.0)                              # M3 insert bosses for the perfboard
TRAY_BOSS_D = 9.0
# D4184 MOSFET module outline, rear-right beside the bank, long axis along Y
D4184_XY = (47.5, 34.0)
D4184_OUTLINE = (P.D4184_W + 2.0, P.D4184_L + 2.0)              # 19 x 36 pocket outline
D4184_FRAME_T, D4184_FRAME_H = 1.2, 3.0
D4184_BOSS_GAP = 1.0                                  # boss edge from the outline (edge-clamp with a washer)

# cable management / drains
ZIPTIE_R = R_IN - 6.6                                 # anchor radius (78)
ZIPTIE_ANGLES = (20.0, 160.0, 240.0, 300.0)
ZIPTIE_SLOT = (4.5, 2.0)                              # for a 3.6-4.8 mm cable tie
ZIPTIE_PITCH = 7.0                                    # the two slots of one anchor
DRAIN_D = 8.0
DRAIN_XY = ((-8.0, -78.0), (-28.0, -72.0))

# ------------------------------------------------------------------ small helpers
def _cyl(r, h, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(h)


def _ring(r_out, r_in, h, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r_out).circle(r_in).extrude(h)


def _box(lx, ly, lz, x=0.0, y=0.0, z0=0.0):
    """Box centred on (x, y), sitting on z0."""
    return cq.Workplane('XY').box(lx, ly, lz, centered=(True, True, False)).translate((x, y, z0))


def _rot_z(wp, deg, about=(0.0, 0.0)):
    """Rotate about a vertical axis through (about)."""
    return wp.translate((-about[0], -about[1], 0)).rotate((0, 0, 0), (0, 0, 1), deg).translate((about[0], about[1], 0))


def _union_all(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


def _wall_angle_at_x(x):
    """Angle (deg) of the point on the +Y inner wall with this x."""
    return math.degrees(math.atan2(math.sqrt(R_IN ** 2 - x * x), x))


def _radial_cutter(x, z, d, r0, r1):
    """Cylinder of dia d along the radial direction through (x, +Y wall, z), from radius r0 to r1."""
    a = math.radians(_wall_angle_at_x(x))
    n = cq.Vector(math.cos(a), math.sin(a), 0)
    origin = cq.Vector(r0 * math.cos(a), r0 * math.sin(a), z)
    return cq.Workplane(cq.Plane(origin=origin, normal=n)).circle(d / 2).extrude(r1 - r0)


# ------------------------------------------------------------------ drum
def _drum():
    """Outer silhouette: bottom band D_MAX, body BASE_BODY_D, 45 deg step, top band D_MAX; hollow."""
    bottom_band = _cyl(R_MAX, P.BASE_BAND_H).edges('<Z').chamfer(BOTTOM_CHAMFER)
    body = _cyl(R_BODY, BAND_TOP_Z0 - TOP_CHAMFER_H - P.BASE_BAND_H, z0=P.BASE_BAND_H)
    step = cq.Workplane('XY').add(cq.Solid.makeCone(R_BODY, R_MAX, TOP_CHAMFER_H,
                                                    pnt=cq.Vector(0, 0, BAND_TOP_Z0 - TOP_CHAMFER_H)))
    top_band = _cyl(R_MAX, P.BASE_BAND_H, z0=BAND_TOP_Z0)
    drum = _union_all([bottom_band, body, step, top_band])
    interior = _cyl(R_IN, P.BASE_H, z0=P.FLOOR)          # straight bore from the floor to the top
    return drum.cut(interior)


def _door_opening_cutters():
    """The door opening plus the two shallow (1 mm) recesses in the bands where the door plate overlaps."""
    opening = _box(P.BASE_DOOR_W, 60.0, P.BASE_DOOR_H, 0, 40.0 + 30.0, DOOR_Z0)
    half_w = DOOR_X_HALF + DOOR_LIP + P.FIT
    outside_plate = _cyl(R_MAX + 2.0, P.BASE_H).cut(_cyl(DOOR_PLATE_R, P.BASE_H))      # r > plate radius
    bottom_recess = _box(2 * half_w, 60.0, DOOR_Z0 - (DOOR_Z0 - DOOR_LIP - P.FIT), 0, 70.0,
                         DOOR_Z0 - DOOR_LIP - P.FIT).intersect(outside_plate)
    # the side lips run up to the band: notch the 45 deg step where they pass
    side_notch = _box(2 * half_w, 60.0, TOP_CHAMFER_H + 0.01, 0, 70.0,
                      BAND_TOP_Z0 - TOP_CHAMFER_H).intersect(outside_plate)
    return [opening, bottom_recess, side_notch]


def _door_tabs():
    """Four corner stop tabs inside the wall; the door plug rests on them, magnets pull it on."""
    tabs = []
    ann = _ring(R_IN, R_IN - TAB_T, P.BASE_H)
    for sx in (-1, 1):
        x0 = sx * (DOOR_X_HALF - TAB_IN)
        x1 = sx * (DOOR_X_HALF + TAB_OUT)
        for z_mag, z_edge, dz in ((DOOR_MAG_Z[0], DOOR_Z0, 1), (DOOR_MAG_Z[1], DOOR_Z1, -1)):
            z_lo = min(z_edge - dz * TAB_OUT, z_edge + dz * TAB_IN)
            z_hi = max(z_edge - dz * TAB_OUT, z_edge + dz * TAB_IN)
            box = _box(abs(x1 - x0), 60.0, z_hi - z_lo, (x0 + x1) / 2, 70.0, z_lo)
            tabs.append(ann.intersect(box))
    return tabs


def _door_tab_pockets():
    """Magnet pockets in the tabs, opened toward the door (+radial)."""
    pockets = []
    for sx in (-1, 1):
        for z in DOOR_MAG_Z:
            pockets.append(_radial_cutter(sx * DOOR_MAG_X, z, P.MAGNET_POCKET_D,
                                          R_IN - P.MAGNET_POCKET_T, R_IN + 0.5))
    return pockets


# ------------------------------------------------------------------ floor features
def _bottle_cradle():
    bx, by = BOTTLE_XY
    r_in = BOTTLE_RING_ID / 2
    r_out = r_in + BOTTLE_RING_WALL
    ring = _ring(r_out, r_in, BOTTLE_RING_H, bx, by, P.FLOOR)
    parts = [ring]
    slots = []
    for a in BOTTLE_FINGER_ANGLES:
        # finger: tangential plate on the ring OD, rising above the ring, with a vertical strap slot
        finger = _box(BOTTLE_FINGER_T, BOTTLE_FINGER_W, BOTTLE_RING_H + BOTTLE_FINGER_H,
                      r_in + BOTTLE_FINGER_T / 2, 0, P.FLOOR)
        slot_z0 = P.FLOOR + BOTTLE_RING_H + (BOTTLE_FINGER_H - STRAP_SLOT_L) / 2
        slot = _box(BOTTLE_FINGER_T + 2, STRAP_SLOT_W, STRAP_SLOT_L, r_in + BOTTLE_FINGER_T / 2, 0, slot_z0)
        parts.append(_rot_z(finger, a).translate((bx, by, 0)))
        slots.append(_rot_z(slot, a).translate((bx, by, 0)))
    return parts, slots


def _pump_cradle():
    """Vertical pump: floor ring around the motor can + a tall half-round saddle on the wall side
    with a pair of strap slots, + two floor slots for a second strap over the top of the pump."""
    px, py = PUMP_XY
    wall_dir = math.degrees(math.atan2(py, px))         # direction from the axis to the pump = wall side
    r_in = PUMP_RING_ID / 2
    ring = _ring(r_in + PUMP_RING_WALL, r_in, PUMP_RING_H, px, py, P.FLOOR)
    # saddle: annular sector built at the origin facing +X, rotated to the wall direction
    r_out = r_in + PUMP_SADDLE_T
    ann = _ring(r_out, r_in, PUMP_SADDLE_H, 0, 0, P.FLOOR)
    half = PUMP_SADDLE_SPAN / 2
    fan_pts = [(0.0, 0.0)] + [((r_out + 5) * math.cos(math.radians(a)), (r_out + 5) * math.sin(math.radians(a)))
                              for a in [-half + i * (2 * half) / 8 for i in range(9)]]
    fan = cq.Workplane('XY').workplane(offset=P.FLOOR - 1).polyline(fan_pts).close().extrude(PUMP_SADDLE_H + 2)
    saddle = ann.intersect(fan)
    slots = []
    for s in (-1, 1):
        slot = _box(PUMP_SADDLE_T + 4, STRAP_SLOT_W, STRAP_SLOT_L, r_in + PUMP_SADDLE_T / 2, 0,
                    P.FLOOR + PUMP_SADDLE_SLOT_Z0)
        slots.append(_rot_z(slot, s * PUMP_SADDLE_SLOT_ANGLE))
    # floor slots either side (perpendicular to the wall direction), long axis along the wall direction
    for s in (-1, 1):
        slots.append(_box(STRAP_SLOT_L, STRAP_SLOT_W, P.FLOOR + 2, 0, s * PUMP_FLOOR_SLOT_OFFSET, -1))
    saddle = _rot_z(saddle, wall_dir).translate((px, py, 0))
    slots = [_rot_z(sl, wall_dir).translate((px, py, 0)) for sl in slots]
    return [ring, saddle], slots


def _powerbank_tray():
    xc = (POWERBANK_X0 + POWERBANK_X1) / 2
    y_end = P.POWERBANK_L / 2
    stops = [_box(P.POWERBANK_T, POWERBANK_STOP_T, POWERBANK_STOP_H, xc, s * (y_end + POWERBANK_STOP_T / 2), P.FLOOR)
             for s in (-1, 1)]
    slots = []
    for sy in (-1, 1):
        for x in (POWERBANK_X0 - POWERBANK_SLOT_GAP - STRAP_SLOT_W / 2,
                  POWERBANK_X1 + POWERBANK_SLOT_GAP + STRAP_SLOT_W / 2):
            slots.append(_box(STRAP_SLOT_W, STRAP_SLOT_L, P.FLOOR + 2, x, sy * POWERBANK_SLOT_Y, -1))
    return stops, slots


def _electronics_tray():
    tx, ty = TRAY_XY
    plinth = _box(TRAY_L, TRAY_W, TRAY_H, tx, ty, P.FLOOR)
    parts, holes = [plinth], []
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = (tx + sx * TRAY_GRID[0] / 2, ty + sy * TRAY_GRID[1] / 2, P.FLOOR + TRAY_H)
            boss, hole = insert_boss(None, c, boss_d=TRAY_BOSS_D)
            parts.append(boss)
            holes.append(hole)
    # D4184 module: raised outline frame + 2 edge-clamp insert bosses at the short ends
    dx, dy = D4184_XY
    ow, ol = D4184_OUTLINE
    frame = _box(ow + 2 * D4184_FRAME_T, ol + 2 * D4184_FRAME_T, D4184_FRAME_H, dx, dy, P.FLOOR).cut(
        _box(ow, ol, D4184_FRAME_H + 2, dx, dy, P.FLOOR))
    parts.append(frame)
    for sy in (-1, 1):
        c = (dx, dy + sy * (ol / 2 + D4184_FRAME_T + D4184_BOSS_GAP + TRAY_BOSS_D / 2), P.FLOOR)
        boss, hole = insert_boss(None, c, boss_d=TRAY_BOSS_D, boss_h=P.M3_INSERT_DEPTH + 1.5)
        parts.append(boss)
        holes.append(hole)
    return parts, holes


def _floor_cutters():
    """Zip-tie anchor slot pairs along the wall and the two drain holes at the front."""
    cutters = []
    for a in ZIPTIE_ANGLES:
        for s in (-1, 1):
            slot = _box(ZIPTIE_SLOT[1], ZIPTIE_SLOT[0], P.FLOOR + 2, ZIPTIE_R, s * ZIPTIE_PITCH / 2, -1)
            cutters.append(_rot_z(slot, a))
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
    base = _drum()
    for c in _door_opening_cutters():
        base = base.cut(c)
    adds, cuts = [], []
    adds += _door_tabs()
    cuts += _door_tab_pockets()
    p, c = _bottle_cradle(); adds += p; cuts += c
    p, c = _pump_cradle(); adds += p; cuts += c
    p, c = _powerbank_tray(); adds += p; cuts += c
    p, c = _electronics_tray(); adds += p; cuts += c
    base = base.union(_union_all(adds))
    cuts += _floor_cutters()
    cuts += _joint_screw_cutters()
    for c in cuts:
        base = base.cut(c)
    return base


# ------------------------------------------------------------------ door panel
def _door_panel_assembly_frame():
    """Curved panel: outer plate (opening + lip on left/right/bottom, 2 mm, proud of the body) and a
    plug that fills the opening flush with the inner wall. Built in the assembly frame."""
    y_box = _box(400.0, 100.0, 400.0, 0, 50.0, -100.0)   # keep only the +Y side
    plate = _ring(DOOR_PLATE_R, R_BODY, (DOOR_Z1 - P.FIT) - (DOOR_Z0 - DOOR_LIP), 0, 0, DOOR_Z0 - DOOR_LIP)
    plate = plate.intersect(_box(2 * (DOOR_X_HALF + DOOR_LIP), 100.0, 200.0, 0, 50.0, 0)).intersect(y_box)
    plug_h = P.BASE_DOOR_H - 2 * P.FIT
    plug = _ring(R_BODY + 0.01, R_IN, plug_h, 0, 0, DOOR_Z0 + P.FIT)   # 0.01 overlap into the plate
    plug = plug.intersect(_box(2 * (DOOR_X_HALF - P.FIT), 100.0, 200.0, 0, 50.0, 0)).intersect(y_box)
    # 45 deg chamfer under the plug so it prints standing on the plate edge with no overhang
    plug = plug.cut(cq.Workplane('XY').add(cq.Solid.makeCone(R_IN, R_BODY + 0.5, R_BODY + 0.5 - R_IN,
                                                             pnt=cq.Vector(0, 0, DOOR_Z0 + P.FIT))))
    door = plate.union(plug)
    # magnet pockets, opened on the inside face toward the tabs
    for sx in (-1, 1):
        for z in DOOR_MAG_Z:
            door = door.cut(_radial_cutter(sx * DOOR_MAG_X, z, P.MAGNET_POCKET_D, R_IN - 0.5, R_IN + P.MAGNET_POCKET_T))
    # switch hole, normal to the panel
    sx, sz = DOOR_SWITCH_XZ
    door = door.cut(_radial_cutter(sx, sz, DOOR_SWITCH_D, R_IN - 1.0, DOOR_PLATE_R + 1.0))
    # USB-C cable notch in the bottom edge
    notch = _box(DOOR_USB_NOTCH_W, 60.0, DOOR_USB_NOTCH_H + DOOR_LIP + 1.0, DOOR_USB_NOTCH_X, 70.0,
                 DOOR_Z0 - DOOR_LIP - 1.0)
    door = door.cut(notch)
    return door


def build_door():
    door = _door_panel_assembly_frame()
    bb = door.val().BoundingBox()
    shift = (0.0, -(bb.ymin + bb.ymax) / 2, -bb.zmin)
    return door.translate(shift), tuple(-s for s in shift)


# ------------------------------------------------------------------ hardware envelopes (print frame = on z=0)
def _envelopes():
    bx, by = BOTTLE_XY
    bottle = _cyl(P.BOTTLE_D / 2, P.BOTTLE_H, bx, by)
    px, py = PUMP_XY
    pump = _cyl(P.PUMP_MOTOR_D / 2, PUMP_MOTOR_L, px, py).union(
        _cyl(P.PUMP_HEAD_D / 2, PUMP_HEAD_L_EST, px, py, PUMP_MOTOR_L))
    bank = _box(P.POWERBANK_T, P.POWERBANK_L, P.POWERBANK_W, (POWERBANK_X0 + POWERBANK_X1) / 2, 0)
    return {'bottle_envelope': bottle, 'pump_envelope': pump, 'powerbank_envelope': bank}


_DOOR_SHIFT = None


def build():
    global _DOOR_SHIFT
    door, _DOOR_SHIFT = build_door()
    parts = {'base': build_base(), 'base_door': door}
    parts.update(_envelopes())
    return parts


def placements():
    door_shift = _DOOR_SHIFT or build_door()[1]
    on_floor = ((0, 0, 1), 0, (0, 0, P.FLOOR))
    return {
        'base': ((0, 0, 1), 0, (0, 0, 0)),
        'base_door': ((0, 0, 1), 0, door_shift),
        'bottle_envelope': on_floor,
        'pump_envelope': on_floor,
        'powerbank_envelope': on_floor,
    }
