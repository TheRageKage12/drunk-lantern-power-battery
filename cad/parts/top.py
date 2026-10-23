"""
top.py - rev C (2026-10-23): the mirrored top (replaces dish_upper and top_diffuser) and what lives in it.

    top_cap         one revolved part: a plug into the sphere's top collar, the 25 mm neck, the 45 deg flare and the 190 mm
                    cap, 80 mm tall, with a thickened rim carrying 3 L-grooves for the lid. Printed plug down.
    cap_floor       separate plate on a ledge at the bottom of the cap (a cap floor printed in place would be a 185 mm
                    bridge). Carries the battery (LED face down over a slot: look up the neck to read it), the board on
                    standoffs, the buck module, the power switch S1 in a box (lever up) and the charge socket. 3 M3.
    halo_ring       WHITE. A cup: the tube drops into the cap rim and carries the 3 bayonet lugs (quarter-turn twist-lock
                    with a click), the flange shows as a glowing band around the rim, and its 1.2 mm top is the emblem's
                    diffuser. Printed top down.
    emblem_lid      green disc glued on the halo ring, with the lantern emblem cut through it
    emblem_centre   green disc for the middle of the emblem's ring (an island in the cut-out), glued on the halo ring
    wall_extension  WHITE. Stands on the printed lock wall's top edge and reaches up under the top cap's plug, whose
                    notches catch its two tabs: it braces the wall (rev 9 braced it with posts to the old diffuser) and
                    hides the wires that run up behind it.

Assembly frame: Z up from the table, origin on the lantern axis, -Y the display side.
"""
import math
import sys
from pathlib import Path
import cadquery as cq
import params as P
import common as C
from parts import sphere as S
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'docs/review/protoboard'))
import layout as board_layout   # noqa: E402

R_CAP = P.D_MAX / 2                                  # 95
R_CAP_IN = R_CAP - P.WALL                            # 92.6
R_NECK = S.FLAT_D / 2                                # 68.4
PLUG_R = S.OPENING_ID / 2 - P.FIT                    # 65.7: into the sphere's top collar
PLUG_RI = PLUG_R - P.WALL                            # 63.3
Z_FLAT = P.Z_SPHERE_TOP                              # 309.0
Z_PLUG0 = Z_FLAT - S.OPENING_DEPTH                   # 300.0
Z_NECK1 = Z_FLAT + P.NECK_H                          # 334.0
Z_CAP0, Z_TOP = P.Z_CAP0, P.Z_CAP_TOP                # 360.6, 440.6
FLARE_WALL_R = P.WALL / math.cos(math.radians(P.FLARE_ANGLE))
LEDGE_RI = 88.0                                      # the cap floor rests on a ledge r 88 .. 92.6
LEDGE_T = 3.0
CAP_FLOOR_T = 3.0
Z_CAP_FLOOR0 = Z_CAP0 + LEDGE_T                      # 363.6: underside of the cap floor plate
Z_CAP_FLOOR = Z_CAP_FLOOR0 + CAP_FLOOR_T             # 366.6: its top (z = 0 of the cap-floor frame)
CAP_FLOOR_R = R_CAP_IN - P.FIT                       # 92.3
CAP_FLOOR_SCREW_R = 85.0                             # far enough in that each insert stays inside the flare wall
CAP_FLOOR_SCREW_ANGLES = (60.0, 180.0, 300.0)        # clear of the battery, board, buck, S1 and the charge socket
RIM_RI, RIM_H = 89.0, 14.0                           # thickened rim for the lid's L-grooves
Z_SPHERE_SCREWS = P.Z_SPHERE_CENTER + S.Z_UPPER_SCREWS   # 306.0
JOINT_ANGLES = S.TOP_JOINT_ANGLES                  # 30, 150, 270: clear of the wall extension's tabs
BOSS_W, BOSS_DEPTH = 10.0, P.M3_INSERT_DEPTH + 1.5

# lid bayonet: lugs on the halo ring's tube, L-grooves in the cap rim; push down, twist LID_TWIST clockwise (from above)
LID_LUG_ANGLES = (0.0, 120.0, 240.0)                 # entry slots
LID_TWIST = 20.0
LUG_W, LUG_H, LUG_D = 10.0, 5.0, 2.2                 # tangential, height, radial
HALO_TUBE_R = RIM_RI - P.FIT                         # 88.7
HALO_TUBE_T, HALO_TUBE_H = 2.0, 10.0
HALO_FLANGE_H = 4.0                                  # the glowing band: 4 mm tall all round, 190 mm across
HALO_SKIN = 1.2                                      # emblem diffuser (6 layers of white PETG)
GROOVE_R = HALO_TUBE_R + LUG_D + P.FIT               # 91.2
Z_LUG0 = Z_TOP - 8.5                                 # lug z range Z_LUG0 .. Z_LUG0 + LUG_H
GROOVE_Z = (Z_LUG0 - 0.5, Z_LUG0 + LUG_H + 0.5)
DETENT_DEG = 14.0                                    # the lug clicks past a 0.3 mm bump this far into its turn
LID_R, LID_T = 91.0, 2.4                             # green lid disc: the halo flange shows outside r 91
# the emblem (as seen from the front): a ring with a bar over and under it, bars parallel to X
EMBLEM_RING = (26.0, 38.0)
EMBLEM_BAR_X, EMBLEM_BAR_Y = 64.0, (41.0, 51.0)
# the lid lines up on the halo ring with two short pins of 1.75 mm filament in matching holes (asymmetric: one way only)
LID_PIN_R, LID_PIN_ANGLES, LID_PIN_D = 89.0, (90.0, 200.0), 2.0


def _ang_point(r, a):
    return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))


def _sector(r0, r1, a0, a1, z0, z1):
    """Annular sector r0..r1 between angles a0..a1 (deg, a1 > a0), z0..z1."""
    n = max(4, int((a1 - a0) / 3) + 1)
    outer = [_ang_point(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    inner = [_ang_point(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return cq.Workplane('XY').workplane(offset=z0).polyline(outer + inner).close().extrude(z1 - z0)


# ------------------------------------------------------------------ top cap
NECK_RI = R_NECK - P.WALL                            # 66.0
BEARING_T = 2.5                                      # ring joining the plug to the neck, on the sphere's flat


def profile():
    z_cone0 = Z_NECK1 - (R_NECK - FLARE_WALL_R - NECK_RI)     # inner cone meets the neck bore
    z_ledge0 = z_cone0 + (LEDGE_RI - NECK_RI)
    return [
        (PLUG_RI, Z_PLUG0), (PLUG_R, Z_PLUG0), (PLUG_R, Z_FLAT), (R_NECK, Z_FLAT), (R_NECK, Z_NECK1),
        (R_CAP, Z_CAP0), (R_CAP, Z_TOP), (RIM_RI, Z_TOP), (RIM_RI, Z_TOP - RIM_H),
        (R_CAP_IN, Z_TOP - RIM_H - (R_CAP_IN - RIM_RI)),        # 45 deg under the thick rim
        (R_CAP_IN, Z_CAP_FLOOR0), (LEDGE_RI, Z_CAP_FLOOR0), (LEDGE_RI, z_ledge0), (NECK_RI, z_cone0),
        (NECK_RI, Z_FLAT + BEARING_T), (PLUG_RI, Z_FLAT + BEARING_T),
    ]


def face_r(r):
    """A boss's flat outer face sits this far out, so its corners, not its middle, are on r."""
    return math.sqrt(r * r - (BOSS_W / 2) ** 2)


def _boss(r_face, z0, z1, angle, inward=True, corbel=0.0):
    """Insert boss block against a wall at r_face, BOSS_W wide, z0..z1, growing inward; corbel = 45 deg wedge depth."""
    r_face = face_r(r_face)
    r0 = r_face - BOSS_DEPTH if inward else r_face
    pts = [(r0, z0), (r_face, z0 - corbel), (r_face, z1), (r0, z1)]
    return cq.Workplane('XZ').polyline(pts).close().extrude(BOSS_W / 2, both=True).rotate((0, 0, 0), (0, 0, 1), angle)


def build_top_cap():
    c = cq.Workplane('XZ').polyline(profile()).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    outer = cq.Workplane('XZ').polyline([(0, Z_FLAT), (R_NECK - 0.5, Z_FLAT), (R_NECK - 0.5, Z_NECK1), (R_CAP - 0.5, Z_CAP0 + 0.5),
                                          (R_CAP - 0.5, Z_TOP), (0, Z_TOP)]).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    for a in JOINT_ANGLES:                                   # plug bosses for the sphere's 3 radial screws
        c = c.union(_boss(PLUG_R, Z_PLUG0, Z_FLAT + BEARING_T, a))
    for a in CAP_FLOOR_SCREW_ANGLES:                         # cap floor bosses under the ledge (45 deg corbels)
        r0 = CAP_FLOOR_SCREW_R - 3.3
        pts = [(r0, Z_CAP_FLOOR0 - 8.0), (R_CAP_IN + 0.5, Z_CAP_FLOOR0 - 8.0 - (R_CAP_IN + 0.5 - r0)),
               (R_CAP_IN + 0.5, Z_CAP_FLOOR0), (r0, Z_CAP_FLOOR0)]
        c = c.union(cq.Workplane('XZ').polyline(pts).close().extrude(BOSS_W / 2, both=True)
                    .rotate((0, 0, 0), (0, 0, 1), a).intersect(outer))
    for a in JOINT_ANGLES:
        c = c.cut(C.radial_hole(Z_SPHERE_SCREWS, a, PLUG_R + 0.5, PLUG_R - face_r(PLUG_R) + P.M3_INSERT_DEPTH + 0.5, P.M3_INSERT_HOLE))
    for a in CAP_FLOOR_SCREW_ANGLES:
        x, y = _ang_point(CAP_FLOOR_SCREW_R, a)
        c = c.cut(cq.Workplane('XY').workplane(offset=Z_CAP_FLOOR0 - P.M3_INSERT_DEPTH).center(x, y)
                  .circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH + 0.5))
    # lid L-grooves: an entry slot down from the rim, then a leg turning clockwise seen from above (negative angle)
    half = math.degrees(LUG_W / 2 / GROOVE_R) + 1.0
    for a in LID_LUG_ANGLES:
        c = c.cut(_sector(RIM_RI - 0.5, GROOVE_R, a - half, a + half, GROOVE_Z[0], Z_TOP + 1))
        c = c.cut(_sector(RIM_RI - 0.5, GROOVE_R, a - LID_TWIST - half, a + half, GROOVE_Z[0], GROOVE_Z[1]))
        bx, by = _ang_point(GROOVE_R + 0.5, a - DETENT_DEG)  # click bump: a rod standing 0.3 mm proud of the groove floor
        c = c.union(cq.Workplane('XY').workplane(offset=GROOVE_Z[0]).center(bx, by).circle(0.8)
                    .extrude(GROOVE_Z[1] - GROOVE_Z[0]).intersect(cq.Workplane('XY').circle(R_CAP - 0.5).extrude(Z_TOP + 1)))
    # notches in the plug's bottom edge for the wall extension's tabs
    for sx in (-1, 1):
        x0, x1 = sorted((sx * WEXT_TAB_X[0], sx * WEXT_TAB_X[1]))
        c = c.cut(cq.Workplane('XY').box(x1 - x0 + 2 * P.FIT, WEXT_T + 2 * P.FIT, WEXT_TAB_H + P.FIT, centered=(True, True, False))
                  .translate(((x0 + x1) / 2, WEXT_Y, Z_PLUG0 - 1)))
    return c


# ------------------------------------------------------------------ wall extension (sphere frame z, assembly x/y)
WEXT_T = S.WALL_T
WEXT_Y = (S.WALL_FRONT_Y + S.WALL_BACK_Y) / 2        # -26.4: in line with the lock wall
WEXT_HW = 57.0                                       # half width: the plug ring's bore is at x 57.5 here
WEXT_Z0 = S.WALL_Z0 + S.WALL_H                       # 48.5: the printed wall's top edge (sphere frame)
WEXT_Z1 = Z_PLUG0 - P.Z_SPHERE_CENTER - 0.5          # 79.2: 0.5 under the plug
WEXT_TAB_X, WEXT_TAB_H = (53.0, 59.5), 4.0         # tabs up into notches in the plug ring (x 57.5 .. 60.1 here)
WEXT_LEG = 8.0                                       # legs down over the wall's top edge


def build_wall_extension():
    """Sphere frame (assembly x, y; z from the sphere centre). Legs over the wall's top edge only where its faces are
    bare: in front outside the lock housing (|x| > 40), behind outside the LED rows (|x| > 51). Printed standing on
    the legs (the 3 mm channel between them is a short bridge)."""
    yf, yb = S.WALL_FRONT_Y, S.WALL_BACK_Y
    box = lambda x0, x1, y0, y1, z0, z1: cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    e = box(-WEXT_HW, WEXT_HW, yb, yf, WEXT_Z0 + P.FIT, WEXT_Z1)
    e = e.union(box(-WEXT_HW, WEXT_HW, yb - P.FIT - 1.6, yf + P.FIT + 1.6, WEXT_Z0 + P.FIT, WEXT_Z0 + 6.0))   # leg bar
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 40.0, sx * WEXT_HW))
        e = e.union(box(x0, x1, yf + P.FIT, yf + P.FIT + 1.6, WEXT_Z0 - WEXT_LEG, WEXT_Z1))
        x0, x1 = sorted((sx * 51.0, sx * WEXT_HW))
        e = e.union(box(x0, x1, yb - P.FIT - 1.6, yb - P.FIT, WEXT_Z0 - WEXT_LEG, WEXT_Z1))
        x0, x1 = sorted((sx * WEXT_TAB_X[0], sx * WEXT_TAB_X[1]))
        e = e.union(box(x0, x1, yb, yf, WEXT_Z1 - 1.0, WEXT_Z1 + 0.5 + WEXT_TAB_H - 0.5))
    return e


# ------------------------------------------------------------------ cap floor (cap-floor frame: z = 0 its top face)
def _box(lx, ly, lz, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane('XY').box(lx, ly, lz, centered=(True, True, False)).translate((x, y, z0))


def pack_to_cap(wp):
    """Pack frame (pack centred on the origin, length along Y, end face at -Y) -> cap-floor frame."""
    return wp.rotate((0, 0, 0), (0, 0, 1), P.PACK_CAP_ROT).translate((*P.PACK_CAP_XY, 0))


STOP_T, STOP_H, STOP_GAP, PORT_STOP_H = P.WALL, 12.0, 0.3, 3.0
STRAP_SLOT_L, STRAP_SLOT_W = 22.0, 3.0               # 20 mm hook-and-loop strap
HW, HL = P.POWERBANK_W / 2, P.POWERBANK_L / 2


def _pack_bed():
    """Pack frame: rails and end stops (low at the port end), strap slots, the bed, the LED slot. z = 0 the plate top."""
    y_stop = HL + STOP_GAP + STOP_T / 2
    adds = [_box(P.POWERBANK_W, STOP_T, STOP_H, 0, y_stop),
            _box(P.POWERBANK_W, STOP_T, PORT_STOP_H, 0, -y_stop)]
    x_rail = HW + STOP_GAP + STOP_T / 2
    g0, g1 = P.BATTERY_STRAP_Y - STRAP_SLOT_L / 2 - 4.0, P.BATTERY_STRAP_Y + STRAP_SLOT_L / 2 + 4.0
    for sx in (-1, 1):
        for y0, y1 in ((-HL, g0), (g1, HL)):
            adds.append(_box(STOP_T, y1 - y0, STOP_H, sx * x_rail, (y0 + y1) / 2))
    adds.append(_box(P.POWERBANK_W, P.POWERBANK_L, P.PACK_BED_T))
    x_slot = x_rail + STOP_T / 2 + 1.0 + STRAP_SLOT_W / 2
    adds.append(_box(2 * x_slot - STRAP_SLOT_W, STRAP_SLOT_L, P.PACK_BED_T, 0, P.BATTERY_STRAP_Y))
    cuts = [_box(STRAP_SLOT_W, STRAP_SLOT_L, CAP_FLOOR_T + 2, sx * x_slot, P.BATTERY_STRAP_Y, -CAP_FLOOR_T - 1) for sx in (-1, 1)]
    cuts.append(_box(2 * x_slot, STRAP_SLOT_L, P.BATTERY_STRAP_T + 1, 0, P.BATTERY_STRAP_Y, -CAP_FLOOR_T - 1))
    x0, x1 = P.PACK_LED_X
    cuts.append(_box(x1 - x0, P.PACK_LED_SLOT, CAP_FLOOR_T + P.PACK_BED_T + 2, (x0 + x1) / 2, -HL + P.PACK_LED_IN, -CAP_FLOOR_T - 1))
    return adds, cuts, x_slot


BOARD_STANDOFF = 10.0                                # = mechanical.REAR_GAP: wires run under the board
BOARD_PAD = 9.0
SWITCH_BOX = (26.0, 23.0, 22.0)                      # outer x, y, height; S1 hangs from its roof, lever up
SWITCH_WIRE_WIN = (12.0, 12.0)                       # opening in the box's +X wall for the leads
WIRE_HOLE = (16.0, 10.0)
ZIPTIE_SLOT = (4.5, 2.0)


def board_point(x_d, y_d):
    """Board drawing mm (from top-left, component side up) -> cap-floor frame x, y (turned by BOARD_CAP_ROT)."""
    u, v = x_d - P.PERFBOARD_W / 2, P.PERFBOARD_H / 2 - y_d
    a = math.radians(P.BOARD_CAP_ROT)
    bx, by = P.BOARD_CAP_XY
    return bx + u * math.cos(a) - v * math.sin(a), by + u * math.sin(a) + v * math.cos(a)


BUCK_DIMS = (P.BUCK_L, P.BUCK_W)                     # x, y on the plate (long side along X)


def build_cap_floor():
    plate = cq.Workplane('XY').workplane(offset=-CAP_FLOOR_T).circle(CAP_FLOOR_R).extrude(CAP_FLOOR_T)
    adds, cuts = [], []
    a, c, _ = _pack_bed()
    adds += [pack_to_cap(w) for w in a]
    cuts += [pack_to_cap(w) for w in c]
    for mx, my in board_layout.MOUNTS:               # standoffs with inserts from the top
        x, y = board_point(mx, my)
        adds.append(_box(BOARD_PAD, BOARD_PAD, BOARD_STANDOFF, x, y))
        cuts.append(cq.Workplane('XY').workplane(offset=BOARD_STANDOFF - P.M3_INSERT_DEPTH).center(x, y)
                    .circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH + 0.5))
    bx, by = P.BUCK_CAP_XY                           # buck module corner supports and two cable ties across it
    lx, ly = BUCK_DIMS
    for sx in (-1, 1):
        for sy in (-1, 1):
            adds.append(_box(3, 3, P.BUCK_STANDOFF, bx + sx * (lx / 2 - 1.5), by + sy * (ly / 2 - 1.5)))
            cuts.append(_box(ZIPTIE_SLOT[0], ZIPTIE_SLOT[1], CAP_FLOOR_T + 2, bx + sx * lx / 4, by + sy * (ly / 2 + 3.0), -CAP_FLOOR_T - 1))
    sx, sy = P.SWITCH_CAP_XY                         # S1 box
    w, l, h = SWITCH_BOX
    adds.append(_box(w, l, h, sx, sy))
    cuts.append(_box(w - 2 * P.WALL, l - 2 * P.WALL, h - P.WALL, sx, sy, 0.0))
    cuts.append(cq.Workplane('XY').workplane(offset=h - P.WALL - 1).center(sx, sy).circle(P.PORT_SWITCH_D / 2).extrude(P.WALL + 2))
    cuts.append(_box(P.WALL + 2, SWITCH_WIRE_WIN[0], SWITCH_WIRE_WIN[1], sx + w / 2 - P.WALL / 2, sy, -0.01))
    cx, cy = P.CHARGE_SOCKET_XY                      # charge socket: two cable-tie slot pairs under the barrel
    for dx in (-8.0, 8.0):
        for dy in (-8.0, 8.0):
            cuts.append(_box(ZIPTIE_SLOT[1], ZIPTIE_SLOT[0], CAP_FLOOR_T + 2, cx + dx, cy + dy, -CAP_FLOOR_T - 1))
    wx, wy = P.CAP_WIRE_HOLE_XY
    cuts.append(cq.Workplane('XY').workplane(offset=-CAP_FLOOR_T - 1).center(wx, wy).slot2D(WIRE_HOLE[0], WIRE_HOLE[1]).extrude(CAP_FLOOR_T + 2))
    for a in CAP_FLOOR_SCREW_ANGLES:
        x, y = _ang_point(CAP_FLOOR_SCREW_R, a)
        cuts.append(cq.Workplane('XY').workplane(offset=-CAP_FLOOR_T - 1).center(x, y).circle(P.M3_CLEAR / 2).extrude(CAP_FLOOR_T + 2))
    for w_ in adds:
        plate = plate.union(w_)
    for c_ in cuts:
        plate = plate.cut(c_)
    return plate


# ------------------------------------------------------------------ halo ring and lid (assembled, locked position)
def build_halo_ring():
    r0 = HALO_TUBE_R - HALO_TUBE_T
    h = cq.Workplane('XY').workplane(offset=Z_TOP - HALO_TUBE_H).circle(HALO_TUBE_R).circle(r0).extrude(HALO_TUBE_H)
    h = h.union(cq.Workplane('XY').workplane(offset=Z_TOP).circle(R_CAP).extrude(HALO_FLANGE_H))
    h = h.cut(cq.Workplane('XY').workplane(offset=Z_TOP - 1).circle(r0).extrude(HALO_FLANGE_H - HALO_SKIN + 1))
    half = math.degrees(LUG_W / 2 / HALO_TUBE_R)
    for a in LID_PIN_ANGLES:                         # pin holes in the flange top (on the bed when printed)
        x, y = _ang_point(LID_PIN_R, a - LID_TWIST)
        h = h.cut(cq.Workplane('XY').workplane(offset=Z_TOP + HALO_FLANGE_H - 2.0).center(x, y).circle(LID_PIN_D / 2).extrude(2.1))
    for a in LID_LUG_ANGLES:                         # lugs at their locked angle
        h = h.union(_sector(HALO_TUBE_R - 0.5, HALO_TUBE_R + LUG_D, a - LID_TWIST - half, a - LID_TWIST + half,
                            Z_LUG0, Z_LUG0 + LUG_H))
    return h


def _emblem(z0, h):
    e = cq.Workplane('XY').workplane(offset=z0).circle(EMBLEM_RING[1]).circle(EMBLEM_RING[0]).extrude(h)
    for sy in (-1, 1):
        y0, y1 = sorted((sy * EMBLEM_BAR_Y[0], sy * EMBLEM_BAR_Y[1]))
        e = e.union(cq.Workplane('XY').box(2 * EMBLEM_BAR_X, y1 - y0, h, centered=(True, True, False)).translate((0, (y0 + y1) / 2, z0)))
    return e


def build_emblem_lid():
    z0 = Z_TOP + HALO_FLANGE_H
    lid = cq.Workplane('XY').workplane(offset=z0).circle(LID_R).extrude(LID_T)
    lid = lid.edges('>Z').chamfer(1.0)
    for a in LID_PIN_ANGLES:                         # matching pin holes in its underside (assembled position)
        x, y = _ang_point(LID_PIN_R, a - LID_TWIST)
        lid = lid.cut(cq.Workplane('XY').workplane(offset=z0 - 0.1).center(x, y).circle(LID_PIN_D / 2).extrude(1.1))
    return lid.cut(_emblem(z0 - 1, LID_T + 2)).cut(cq.Workplane('XY').workplane(offset=z0 - 1).circle(EMBLEM_RING[0]).extrude(LID_T + 2))


def build_emblem_centre():
    z0 = Z_TOP + HALO_FLANGE_H
    return cq.Workplane('XY').workplane(offset=z0).circle(EMBLEM_RING[0] - P.FIT).extrude(LID_T)


# ------------------------------------------------------------------ module API
def build():
    out = {
        'top_cap': build_top_cap().translate((0, 0, -Z_PLUG0)),                       # plug on the bed
        'cap_floor': build_cap_floor().translate((0, 0, CAP_FLOOR_T)),                 # flat, features up
        'halo_ring': build_halo_ring().rotate((0, 0, 0), (1, 0, 0), 180)
                     .translate((0, 0, Z_TOP + HALO_FLANGE_H)),                        # top (skin) down
        'emblem_lid': build_emblem_lid().translate((0, 0, -(Z_TOP + HALO_FLANGE_H))),
        'emblem_centre': build_emblem_centre().translate((0, 0, -(Z_TOP + HALO_FLANGE_H))),
        'wall_extension': build_wall_extension().translate((0, 0, -(WEXT_Z0 - WEXT_LEG))),   # standing on its legs
    }
    return out


def placements():
    zl = Z_TOP + HALO_FLANGE_H
    return {
        'top_cap': ((0, 0, 1), 0, (0, 0, Z_PLUG0)),
        'cap_floor': ((0, 0, 1), 0, (0, 0, Z_CAP_FLOOR - CAP_FLOOR_T)),
        'halo_ring': ((1, 0, 0), 180, (0, 0, zl)),
        'emblem_lid': ((0, 0, 1), 0, (0, 0, zl)),
        'emblem_centre': ((0, 0, 1), 0, (0, 0, zl)),
        'wall_extension': ((0, 0, 1), 0, (0, 0, P.Z_SPHERE_CENTER + WEXT_Z0 - WEXT_LEG)),
    }
