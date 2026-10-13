"""
base.py - the lantern's base: an outer drum (part of the lantern shell) and a removable CARTRIDGE.

The cartridge (tray + deck + 12 V battery pack + jar + pump + electronics) slides up into the open bottom of the
drum and is held by three thumbscrews from underneath, hidden while the lantern stands. To refill: undo the
thumbscrews and lift the lantern off by its handle; the cartridge stays on the table (rev 9; no service door).

Parts (print orientation, bed = XY, min z = 0):
  base               drum, open both ends, printed TOP BAND DOWN (its 3 nut bosses then print without support)
  base_tray          cartridge floor: bank pocket, deck pillars, buck-converter pocket, drains, 3 knob pads
  thumb_knob         knurled knob that grips an M3x12 socket screw (print 3)
  base_deck          flat deck plate that drops in over the battery pack and carries the bottle
                     cradle, the pump saddles and the electronics panel (printed flat, identity + lift)
  bottle_envelope    stepped cylinder: body BOTTLE_D x BOTTLE_BODY_H_EST, shoulder, neck/cap to BOTTLE_H
  pump_envelope      KPHM200: head box PUMP_W x PUMP_H x PUMP_HEAD_L_EST + motor can PUMP_MOTOR_D, PUMP_L long,
                     lying with the motor axis along Y, head face toward the owner's side
  powerbank_envelope box POWERBANK_W (X) x POWERBANK_L (Y) x POWERBANK_T (Z) lying flat on the floor

Assembly frame: Z up, origin at the centre of the base bottom, +Y = the owner's side, -Y = display side.
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

# ------------------------------------------------------------------ cartridge joint (rev 9, replaces the door)
USB_X = 0.0                                           # the bank's ports are at the middle of its +Y end
SERVICE_ANGLES = P.SERVICE_SCREW_ANGLES               # (0, 140, 225): clear of the bank, pillars, pockets, jar fingers
SERVICE_R = 79.0                                      # thumbscrew axis radius (knob clears the drum wall)
BOSS_R0 = 75.5                                        # drum nut bosses: r 75.5 .. wall, BOSS_Z0 .. BOSS_Z1
BOSS_Z0, BOSS_Z1 = 8.0, 18.0
BOSS_W = 10.0
NUT_Z0, NUT_T, NUT_AF = 11.0, 2.8, 5.8                # side-loading nut slot, opening toward the inside
PAD_R0 = 70.0                                         # tray pads under the bosses: r 70 .. tray edge, z 0 .. BOSS_Z0
PAD_W = 22.0
WELL_D, WELL_DEPTH = 20.0, 6.0                        # finger well for the knob, from below
KNOB_D, KNOB_H = 10.0, 5.5
TRAY_R = R_IN - P.FIT                                 # 84.3, same as the deck
SERVICE_SWEEP_Z1 = SPIGOT_ZONE_Z0 - 1.0               # the bosses pass down over the cartridge from here

# ------------------------------------------------------------------ battery pack pocket (floor, centred)
BANK_HALF_W = P.POWERBANK_W / 2                       # 27.5 across X
BANK_HALF_L = P.POWERBANK_L / 2                       # along Y, ports toward +Y (owner's side)
BANK_END_STOP_T, BANK_END_STOP_H = P.WALL, 12.0
BANK_END_STOP_GAP = 0.3
BANK_END_STOP_X = (7.0, P.POWERBANK_W / 2)            # two blocks at +Y leaving the middle free for the plug
STRAP_SLOT_L, STRAP_SLOT_W = 22.0, 3.0                # for a 20 mm hook-and-loop strap

# ------------------------------------------------------------------ deck on pillars
PILLAR_S = 9.0                                        # square pillars
PILLAR_X = BANK_HALF_W + 1.0 + PILLAR_S / 2           # 33: inner faces also guide the bank sideways
PILLAR_Y = (-55.0, 0.0, 55.0)
PILLAR_INSERTS = ((PILLAR_X, 0.0), (-PILLAR_X, 0.0), (PILLAR_X, 55.0))   # 3 = unambiguous orientation
DECK_GAP = 2.0                                        # over the pack: holds it down (a thin strap still fits)
DECK_Z0 = P.FLOOR + P.POWERBANK_T + DECK_GAP          # MATING: deck underside (44)
PILLAR_H = DECK_Z0 - P.FLOOR
DECK_T = 3.0
DECK_TOP = DECK_Z0 + DECK_T                           # MATING: everything on the deck starts here (47)
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
    return drum.cut(_cyl(R_IN, P.BASE_H + 2, z0=-1))          # open at the bottom: the cartridge comes out there


# ------------------------------------------------------------------ base floor features
def _bank_pocket():
    """End stops and side rails for the flat battery pack, and a strap slot pair across its middle. The +Y end
    stop is two blocks: the pack's DC socket and its plug sit in the gap, toward the port panel."""
    y_stop = BANK_HALF_L + BANK_END_STOP_GAP + BANK_END_STOP_T / 2
    adds = [_box(2 * BANK_END_STOP_X[1], BANK_END_STOP_T, BANK_END_STOP_H, 0, -y_stop, P.FLOOR)]
    for sx in (-1, 1):   # +Y end: two blocks, the middle stays free for the plug
        xc = sx * (BANK_END_STOP_X[0] + BANK_END_STOP_X[1]) / 2
        adds.append(_box(BANK_END_STOP_X[1] - BANK_END_STOP_X[0], BANK_END_STOP_T, BANK_END_STOP_H, xc, y_stop, P.FLOOR))
    x_rail = BANK_HALF_W + BANK_END_STOP_GAP + BANK_END_STOP_T / 2
    rail_l = BANK_HALF_L - STRAP_SLOT_L / 2 - 4.0
    for sx in (-1, 1):   # side rails either side of the strap, so the narrow bank cannot slide sideways
        for sy in (-1, 1):
            adds.append(_box(BANK_END_STOP_T, rail_l, BANK_END_STOP_H, sx * x_rail, sy * (BANK_HALF_L - rail_l / 2), P.FLOOR))
    x_slot = x_rail + BANK_END_STOP_T / 2 + 1.0 + STRAP_SLOT_W / 2
    cuts = [_box(STRAP_SLOT_W, STRAP_SLOT_L, P.FLOOR + 2, sx * x_slot, 0.0, -1) for sx in (-1, 1)]
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


def _sector_box(r0, r1, w, z0, z1, angle):
    """Block from r0 to r1 (radially), w wide, z0..z1, centred on angle (deg)."""
    return _rot_z(_box(r1 - r0, w, z1 - z0, (r0 + r1) / 2, 0.0, z0), angle)


def _service_xy(a):
    return SERVICE_R * math.cos(math.radians(a)), SERVICE_R * math.sin(math.radians(a))


def _drum_bosses():
    """Three nut bosses inside the drum's bottom. A 45 deg roof on their upper side lets the drum print
    top band down without support."""
    adds, cuts = [], []
    ch = R_IN - BOSS_R0
    for a in SERVICE_ANGLES:
        blk = _sector_box(BOSS_R0, R_IN + 0.5, BOSS_W, BOSS_Z0, BOSS_Z1, a)
        roof = (cq.Workplane('XZ').polyline([(BOSS_R0, BOSS_Z1), (R_IN + 0.5, BOSS_Z1), (R_IN + 0.5, BOSS_Z1 + ch + 0.5)])
                .close().extrude(BOSS_W / 2, both=True))
        adds += [blk, _rot_z(roof, a)]
        x, y = _service_xy(a)
        cuts.append(_cyl(P.M3_CLEAR / 2, BOSS_Z1 - BOSS_Z0 + 2, x, y, BOSS_Z0 - 1))
        # nut slot: the nut slides in flats-first from the inside face
        cuts.append(_sector_box(BOSS_R0 - 1, SERVICE_R, NUT_AF + 0.2, NUT_Z0, NUT_Z0 + NUT_T, a))
        cuts.append(cq.Workplane('XY').workplane(offset=NUT_Z0).center(x, y)
                    .polygon(6, (NUT_AF + 0.2) / math.cos(math.radians(30))).extrude(NUT_T)
                    .rotate((x, y, 0), (x, y, 1), a))
    return adds, cuts


def build_base():
    """The drum: part of the lantern shell. No floor, no door; three nut bosses for the thumbscrews."""
    drum = _drum()
    adds, cuts = _drum_bosses()
    drum = drum.union(_union_all(adds))
    return _cut_all(drum, cuts + _joint_screw_cutters() + [_drum_port_notch()])


def _tray_pads():
    """Pads under the drum bosses, each with a finger well for its thumbscrew knob, from below."""
    adds, cuts = [], []
    for a in SERVICE_ANGLES:
        adds.append(_sector_box(PAD_R0, TRAY_R + 1, PAD_W, 0.0, BOSS_Z0, a).intersect(_cyl(TRAY_R, BOSS_Z0)))
        x, y = _service_xy(a)
        cuts.append(_cyl(WELL_D / 2, WELL_DEPTH + 1, x, y, -1))
        cuts.append(_cyl(P.M3_CLEAR / 2, BOSS_Z0 + 2, x, y, -1))
    return adds, cuts


def _port_panel():
    """Curved panel in the drum's bottom-band notch, flush with the band: charge jack and power switch.
    A floor tab carries it out from the tray edge; two ribs brace it."""
    a = math.radians(P.PORT_ANGLE)
    half = P.PORT_W / 2 - P.FIT                       # panel half-width (in the notch, with clearance)
    r_out, r_in = R_MAX - P.FIT, R_MAX - P.FIT - 3.0  # 3 mm curved skin, flush with the band
    window = _box(2 * half, 40.0, P.PORT_H - P.FIT, 0.0, (R_MAX + 70.0) / 2 + 2.0, 0.0)     # along +Y, then rotated
    skin = _ring(r_out, r_in, P.PORT_H - P.FIT).intersect(window)
    tab = _ring(r_out, TRAY_R - 1.0, P.FLOOR).intersect(window)
    ribs = [_box(2.4, r_in - 74.0 + 0.5, P.PORT_H - P.FIT, sx * (half - 1.2), (74.0 + r_in) / 2, 0.0) for sx in (-1, 1)]
    panel = _union_all([skin, tab] + ribs)
    z = P.FLOOR + (P.PORT_H - P.FIT - P.FLOOR) / 2
    for x, d in ((-half / 2, P.PORT_JACK_D), (half / 2, P.PORT_SWITCH_D)):     # jack on the left, switch on the right (seen from outside: mirrored)
        panel = panel.cut(cq.Workplane('XZ').workplane(offset=-(R_MAX + 2)).center(x, z).circle(d / 2).extrude(R_MAX + 2 - 74.0))
    return _rot_z(panel, P.PORT_ANGLE - 90.0)


def _drum_port_notch():
    """Notch in the drum's bottom band for the port panel. Open at the bottom, so the drum still lifts off."""
    return _rot_z(_box(P.PORT_W, 30.0, P.PORT_H + 1.0, 0.0, R_MAX - 6.0, -1.0), P.PORT_ANGLE - 90.0)


def build_tray():
    """Cartridge floor: everything that used to stand on the base floor."""
    tray = _cyl(TRAY_R, P.FLOOR)
    adds, cuts = [], []
    for fn in (_bank_pocket, _pillars, _floor_electronics, _tray_pads):
        a, c = fn()
        adds += a
        cuts += c
    tray = tray.union(_union_all(adds + [_port_panel()]))
    return _cut_all(tray, cuts + _floor_cutters())


def build_knob():
    """Knurled thumbscrew knob: an M3x12 socket screw goes in head-first from below and is glued; print 3."""
    k = _cyl(KNOB_D / 2, KNOB_H)
    for i in range(12):
        k = k.cut(_rot_z(_cyl(0.9, KNOB_H + 2, KNOB_D / 2 + 0.3, 0, -1), i * 30.0))
    return k.cut(_cyl(5.7 / 2, 3.2, z0=-0.01)).cut(_cyl(P.M3_CLEAR / 2, KNOB_H + 2, z0=-1))


def _service_sweep():
    """Everything the drum's bosses pass through when the lantern is lowered over the cartridge."""
    return _union_all([_sector_box(BOSS_R0 - 0.5, R_IN, BOSS_W + 1.0, BOSS_Z0, SERVICE_SWEEP_Z1, a)
                       for a in SERVICE_ANGLES])


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
    for a in SERVICE_ANGLES:     # notches so the drum's bosses pass the deck when the lantern is lowered on
        cuts.append(_sector_box(BOSS_R0 - 1.5, DECK_R + 1, BOSS_W + 3.0, DECK_Z0 - 1, DECK_Z0 + DECK_T + 1, a))
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


def build():
    parts = {'base': build_base().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, P.BASE_H)),   # top band down
             'base_tray': build_tray(), 'base_deck': build_deck(), 'thumb_knob': build_knob(),
             'service_sweep_envelope': _service_sweep()}
    parts.update(_envelopes())
    return parts


def placements():
    on_floor = ((0, 0, 1), 0, (0, 0, P.FLOOR))
    on_deck = ((0, 0, 1), 0, (0, 0, DECK_TOP))
    kx, ky = _service_xy(SERVICE_ANGLES[0])
    return {
        'base': ((1, 0, 0), 180, (0, 0, P.BASE_H)),          # printed top band down: flip back
        'base_tray': ((0, 0, 1), 0, (0, 0, 0)),
        'thumb_knob': ((0, 0, 1), 0, (kx, ky, WELL_DEPTH - KNOB_H)),   # one of three shown, in its well
        'service_sweep_envelope': ((0, 0, 1), 0, (0, 0, 0)),
        'base_deck': ((0, 0, 1), 0, (0, 0, DECK_Z0)),
        'bottle_envelope': on_deck,
        'pump_envelope': on_deck,
        'powerbank_envelope': on_floor,
    }
