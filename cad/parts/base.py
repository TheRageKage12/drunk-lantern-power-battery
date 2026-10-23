"""
base.py - rev C (2026-10-23): the 80 mm drum (part of the lantern shell) and the one-piece CARTRIDGE.

The cartridge is one printed floor with the pump on its saddles, a splash wall, and the drink bag beside it. The battery
and the board moved up into the top cap, so nothing else is down here. To refill: twist the lantern a little
anticlockwise (seen from above) and lift it off by its handle; the cartridge stays on the table, the bag lifts out.
Only the tube and the pump's two wires (through one plug) cross between the lantern and the cartridge.

Parts (print orientation, bed = XY, min z = 0):
  base               drum, open both ends, printed upright; 3 bayonet lugs inside its bottom edge (45 deg undersides)
  base_tray          the cartridge: floor, bayonet collar with 3 L-slots and click bumps, pump saddles and strap slots,
                     splash wall between the pump and the bag
  pump_envelope      KPHM200: head box PUMP_W x PUMP_H x PUMP_HEAD_L_EST + motor can PUMP_MOTOR_D, PUMP_L long,
                     lying with the motor axis along Y, head face (tube ports) toward the owner's side
  bag_envelope       the space for the drink bag (about 0.4 L of drink): the D-shaped bay left of the splash wall
  lug_sweep_envelope what the lugs pass through as the lantern is lowered on and twisted

Assembly frame: Z up, origin at the centre of the base bottom, +Y = the owner's side, -Y = display side.
"""
import math
import cadquery as cq
import params as P
from common import radial_hole, joint_angles

# ------------------------------------------------------------------ drum silhouette (contract)
R_MAX = P.D_MAX / 2                       # bands top and bottom
R_BODY = P.BASE_BODY_D / 2                # drum body between the bands
R_IN = R_BODY - P.WALL                    # 89.6: one straight bore
BASE_TOP_INNER_D = 2 * R_IN               # MATING: foot spigot OD = BASE_TOP_INNER_D - 2*FIT
BAND_STEP = R_MAX - R_BODY                # 3.0
BAND_TOP_Z0 = P.BASE_H - P.BASE_BAND_H    # 68
BOTTOM_CHAMFER = 1.5

# ------------------------------------------------------------------ foot joint screws (contract)
BASE_JOINT_Z = P.BASE_H - 5.0                        # MATING: foot.Z_DRUM_SCREWS (75)
BASE_JOINT_ANGLES = joint_angles()                   # 90, 210, 330 deg (first at +Y)
BASE_JOINT_CBORE_DEPTH = 3.0

# ------------------------------------------------------------------ bayonet (replaces the rev-9 thumbscrews)
LUG_ANGLES = (30.0, 150.0, 270.0)                    # drum lugs, at their LOCKED position
LUG_TWIST = 20.0                                     # entry slots are this far anticlockwise of the locked lugs
LUG_W = 10.0                                         # tangential
LUG_R0 = R_IN - 2.0                                  # 87.6: lugs stand 2 mm proud of the bore
LUG_Z = (6.0, 12.0)                                  # flat top at 12; a 45 deg underside down to 3.5 at the wall
TRAY_R = R_IN - P.FIT                                # 89.3
COLLAR_RI, COLLAR_H = TRAY_R - P.WALL, 22.0          # bayonet collar 86.9 .. 89.3, 22 tall
LEG_Z = (3.0, 12.5)                                  # horizontal leg of each L-slot
SLOT_W = LUG_W + 2.0
BUMP_DEG, BUMP_DROP = 6.0, 0.7                       # click bump hanging from the leg's ceiling, 6 deg past entry

# ------------------------------------------------------------------ pump (on the cartridge floor, axis along Y)
FLOOR_T = P.CARTRIDGE_FLOOR_T
PUMP_HEAD_L_EST = 40.0
PUMP_MOTOR_L = P.PUMP_L - PUMP_HEAD_L_EST
PUMP_X = 37.0                                        # 2026-10-23: 7 mm right (head corner 0.5 mm off the rim) for a bigger bay
PUMP_HEAD_FACE_Y = 52.0                              # head face (tube ports) toward the owner's side
PUMP_AXIS_Z = FLOOR_T + P.PUMP_H / 2                 # 35
PUMP_HEAD_SADDLE_Y = PUMP_HEAD_FACE_Y - PUMP_HEAD_L_EST + 2.0 + 4.0
PUMP_HEAD_SADDLE_H, PUMP_SADDLE_T, PUMP_SADDLE_WALL = 20.0, 8.0, 8.0
PUMP_MOTOR_SADDLE_Y = PUMP_HEAD_FACE_Y - P.PUMP_L + 8.0 + 4.0
PUMP_MOTOR_STRAP_Y = (-50.0, -28.0)                  # one strap round the motor; the head sits in its U-saddle (no room for
                                                     # a head strap once the pump moved right)
PUMP_STRAP_GAP = 1.5
STRAP_SLOT_W = 3.0

# ------------------------------------------------------------------ splash wall and bag bay
SPLASH_X = (2.0, 4.4)                                # right against the pump head
SPLASH_H = 66.0                                      # to just above the pump
COVER_T, COVER_LIP = 2.0, (2.0, 3.0)                  # bag cover on the splash wall and the raised rim; locating lip under it
BAG_X1, BAG_R, BAG_Z = SPLASH_X[0] - P.FIT - COVER_LIP[0] - 0.5, COLLAR_RI - 2.6, (FLOOR_T, SPLASH_H)   # under the cover
COVER_FINGER = ((-62.0, -20.0), 22.0)                 # finger hole to lift it
# bag floor (2026-10-23): a shallow cone falling 2 deg toward a well at the back end by the splash wall, where the
# bag's spout and the tube's tip sit, so the last of the drink runs to the tube; 45 deg fillets along the walls
WELL_XY, WELL_R, WELL_D = (-32.0, 52.0), 12.0, 2.0
FLOOR_RISE, FLOOR_SLOPE = WELL_D, math.tan(math.radians(2.0))
FILLET = 8.0
TUBE_NOTCH_Y, TUBE_NOTCH = 62.0, (8.0, 12.0)          # notch in the splash wall's top for the tube to the pump's inlet
# tube clip by the well: the tube's end stays inside the bag; press it, bag film and all, down into this C-clip so
# its notched tip lies in the well. Sized for the 6.4 mm tube plus two layers of pouch film.
CLIP_BORE, CLIP_OPEN, CLIP_WALL, CLIP_L = P.TUBE_OD + 0.8, P.TUBE_OD - 0.6, 2.0, 10.0
CLIP_TILT = 15.0                                     # deg down toward the well: the tube's tip rests on the well's bottom
CLIP_X = WELL_XY[0] + WELL_R + 2.0 + CLIP_L / 2      # between the well and the splash wall: the tube comes in from the
                                                     # spout and pump side (+X) and its tip points into the well (-X)
DRAIN_D, DRAIN_XY = 8.0, ((-40.0, -68.0), (40.0, -68.0))


# ------------------------------------------------------------------ helpers
def _cyl(r, h, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(h)


def _box(lx, ly, lz, x=0.0, y=0.0, z0=0.0):
    return cq.Workplane('XY').box(lx, ly, lz, centered=(True, True, False)).translate((x, y, z0))


def _rot_z(wp, deg):
    return wp.rotate((0, 0, 0), (0, 0, 1), deg) if deg else wp


def _union_all(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


def _sector(r0, r1, a0, a1, z0, z1):
    """Annular sector r0..r1 between angles a0 < a1 (deg), z0..z1."""
    n = max(4, int((a1 - a0) / 3) + 1)
    pt = lambda r, a: (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
    pts = [pt(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [pt(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def _half_deg(width, r):
    return math.degrees(width / 2 / r)


# ------------------------------------------------------------------ drum
def _drum():
    """Bottom band D_MAX, body BASE_BODY_D, 45 deg steps, top band D_MAX; one bore; printed upright."""
    bottom_band = _cyl(R_MAX, P.BASE_BAND_H).edges('<Z').chamfer(BOTTOM_CHAMFER)
    step_b = cq.Workplane('XY').add(cq.Solid.makeCone(R_MAX, R_BODY, BAND_STEP, pnt=cq.Vector(0, 0, P.BASE_BAND_H)))
    body = _cyl(R_BODY, BAND_TOP_Z0 - BAND_STEP - P.BASE_BAND_H, z0=P.BASE_BAND_H)
    step = cq.Workplane('XY').add(cq.Solid.makeCone(R_BODY, R_MAX, BAND_STEP, pnt=cq.Vector(0, 0, BAND_TOP_Z0 - BAND_STEP)))
    top_band = _cyl(R_MAX, P.BASE_BAND_H, z0=BAND_TOP_Z0)
    drum = _union_all([bottom_band, step_b, body, step, top_band])
    return drum.cut(_cyl(R_IN, P.BASE_H + 2, z0=-1))


def _lug(angle):
    """Bayonet lug inside the drum's bottom: flat top, 45 deg underside (printed upright without support)."""
    r1 = R_IN + 0.5
    pts = [(LUG_R0, LUG_Z[0]), (LUG_R0, LUG_Z[1]), (r1, LUG_Z[1]), (r1, LUG_Z[0] - (r1 - LUG_R0))]
    blk = cq.Workplane('XZ').polyline(pts).close().extrude(LUG_W / 2, both=True)
    return _rot_z(blk, angle)


def build_base():
    drum = _drum()
    for a in LUG_ANGLES:
        drum = drum.union(_lug(a))
    for a in BASE_JOINT_ANGLES:     # 3 radial M3 through the top band into the foot's spigot, counterbored from outside
        drum = drum.cut(radial_hole(BASE_JOINT_Z, a, R_MAX + 1, 1 + BASE_JOINT_CBORE_DEPTH, P.M3_HEAD_D))
        drum = drum.cut(radial_hole(BASE_JOINT_Z, a, R_MAX + 1, R_MAX - R_IN + 2, P.M3_CLEAR))
    return drum


# ------------------------------------------------------------------ cartridge
def _collar():
    adds = [_cyl(TRAY_R, COLLAR_H).cut(_cyl(COLLAR_RI, COLLAR_H + 2, z0=-1))]
    a0 = math.degrees(math.acos(SPLASH_X[1] / TRAY_R))   # round the bag bay the rim goes up to the cover
    adds.append(_sector(COLLAR_RI, TRAY_R, a0, 360.0 - a0, COLLAR_H - 0.01, SPLASH_H))
    cuts = []
    hs, hl = _half_deg(SLOT_W, TRAY_R), _half_deg(LUG_W, TRAY_R) + 1.0
    for a in LUG_ANGLES:
        entry = a + LUG_TWIST
        cuts.append(_sector(COLLAR_RI - 0.5, TRAY_R + 0.5, entry - hs, entry + hs, LEG_Z[0], SPLASH_H + 1))
        cuts.append(_sector(COLLAR_RI - 0.5, TRAY_R + 0.5, a - hl, entry + hs, LEG_Z[0], LEG_Z[1]))
    bumps = [_sector(COLLAR_RI, TRAY_R, a + BUMP_DEG - 0.8, a + BUMP_DEG + 0.8, LEG_Z[1] - BUMP_DROP, LEG_Z[1] + 0.1)
             for a in LUG_ANGLES]
    return adds, cuts, bumps


def _pump_cradle():
    """U-saddle for the box head (its left cheek stops at the splash wall), round saddle for the motor can, 4 floor
    slots for 2 straps."""
    half_w = P.PUMP_W / 2 + 0.5
    head = _box(2 * (half_w + PUMP_SADDLE_WALL), PUMP_SADDLE_T, PUMP_HEAD_SADDLE_H, PUMP_X, PUMP_HEAD_SADDLE_Y, FLOOR_T)
    head = head.cut(_box(2 * half_w, PUMP_SADDLE_T + 2, PUMP_HEAD_SADDLE_H + 2, PUMP_X, PUMP_HEAD_SADDLE_Y, FLOOR_T))
    head = head.intersect(_box(200, 200, 200, 100 + SPLASH_X[1], 0, 0))
    r_m = P.PUMP_MOTOR_D / 2 + 0.5
    motor = _box(2 * (r_m + PUMP_SADDLE_WALL), PUMP_SADDLE_T, PUMP_AXIS_Z - FLOOR_T, PUMP_X, PUMP_MOTOR_SADDLE_Y, FLOOR_T)
    bore = cq.Workplane('XZ').workplane(offset=-(PUMP_MOTOR_SADDLE_Y + PUMP_SADDLE_T / 2 + 1)) \
        .center(PUMP_X, PUMP_AXIS_Z).circle(r_m).extrude(PUMP_SADDLE_T + 2)
    motor = motor.cut(bore)
    cuts = []
    for sx in (-1, 1):
        x_m = PUMP_X + sx * (P.PUMP_MOTOR_D / 2 + PUMP_STRAP_GAP + STRAP_SLOT_W / 2)
        y0, y1 = PUMP_MOTOR_STRAP_Y
        cuts.append(_box(STRAP_SLOT_W, y1 - y0, FLOOR_T + 2, x_m, (y0 + y1) / 2, -1))
    return [head, motor], cuts


def _splash_wall():
    x0, x1 = SPLASH_X
    w = _box(x1 - x0, 2 * COLLAR_RI, SPLASH_H - FLOOR_T, (x0 + x1) / 2, 0, FLOOR_T).intersect(_cyl(COLLAR_RI + 0.5, SPLASH_H))
    nw, nd = TUBE_NOTCH
    notch = _box(x1 - x0 + 2, nw, nd, (x0 + x1) / 2, TUBE_NOTCH_Y, SPLASH_H - nd + nw / 2) \
        .union(cq.Workplane('YZ').workplane(offset=x0 - 1).center(TUBE_NOTCH_Y, SPLASH_H - nd + nw / 2).circle(nw / 2).extrude(x1 - x0 + 2))
    return w.cut(notch)


def _bay_region(r, z0, z1):
    """The D-shaped bay left of the splash wall, inside radius r."""
    return _cyl(r, z1 - z0, z0=z0).intersect(_box(200, 400, 200, SPLASH_X[0] - 100, 0, 0))


def _bag_floor():
    """Raised floor of the bag bay: a cone rising FLOOR_SLOPE away from the well (the well's rim FLOOR_RISE above the
    tray floor), 45 deg fillets along the splash wall, the rim and the bay's two corners, and the well itself."""
    wx, wy = WELL_XY
    cone = cq.Workplane('XZ').polyline([(0, 0), (0, FLOOR_RISE), (300, FLOOR_RISE + 300 * FLOOR_SLOPE), (300, 0)]) \
        .close().revolve(360.0, (0, 0, 0), (0, 1, 0)).translate((wx, wy, FLOOR_T))
    f = _bay_region(COLLAR_RI + 0.3, FLOOR_T - 0.01, FLOOR_T + 20).intersect(cone)
    x0 = SPLASH_X[0]
    wall_f = cq.Workplane('XZ').polyline([(x0 + 0.3, FLOOR_T), (x0 - FILLET, FLOOR_T), (x0 + 0.3, FLOOR_T + FILLET + 0.3)]) \
        .close().extrude(COLLAR_RI, both=True)
    rim_f = cq.Workplane('XZ').polyline([(COLLAR_RI + 0.3, FLOOR_T), (COLLAR_RI - FILLET, FLOOR_T),
                                          (COLLAR_RI + 0.3, FLOOR_T + FILLET + 0.3)]).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    f = f.union(wall_f.intersect(_bay_region(COLLAR_RI + 0.3, FLOOR_T, FLOOR_T + 20)))
    f = f.union(rim_f.intersect(_bay_region(COLLAR_RI + 0.3, FLOOR_T, FLOOR_T + 20)))
    yt = math.sqrt(COLLAR_RI ** 2 - x0 ** 2)
    for s in (-1, 1):                                # the bay's two corners, where the wall meets the rim
        yc = math.sqrt(COLLAR_RI ** 2 - (x0 - FILLET) ** 2)
        tri = cq.Workplane('XY').workplane(offset=FLOOR_T).polyline(
            [(x0 + 0.3, s * (yt + 0.3)), (x0 + 0.3, s * (yt - FILLET)), (x0 - FILLET, s * (yc + 0.3))]).close().extrude(SPLASH_H - FLOOR_T)
        f = f.union(tri.intersect(_cyl(COLLAR_RI + 0.3, SPLASH_H)))
    rb = (WELL_R ** 2 + WELL_D ** 2) / (2 * WELL_D)  # spherical dish: WELL_R across, WELL_D deep, its bottom on the tray floor
    f = f.cut(cq.Workplane('XY').sphere(rb).translate((wx, wy, FLOOR_T + rb)))
    # the C-clip: a short ring along the tube, open on top, tilted CLIP_TILT down toward the well so the tube's tip
    # (over one layer of bag film) rests on the well's bottom; rounded so it can't cut the bag
    ro = CLIP_BORE / 2 + CLIP_WALL
    zc = clip_axis_z(CLIP_X)
    clip = cq.Workplane('YZ').workplane(offset=-CLIP_L / 2).circle(ro).extrude(CLIP_L)
    clip = clip.cut(cq.Workplane('YZ').workplane(offset=-CLIP_L / 2 - 1).circle(CLIP_BORE / 2).extrude(CLIP_L + 2))
    clip = clip.cut(_box(CLIP_L + 2, CLIP_OPEN, ro + 1, 0, 0, 0))
    try:
        clip = clip.edges('|X').fillet(0.6)
    except Exception:
        pass
    clip = clip.rotate((0, 0, 0), (0, 1, 0), -CLIP_TILT).translate((CLIP_X, wy, zc))
    foot = _box(CLIP_L * math.cos(math.radians(CLIP_TILT)), 2 * ro - 1.0, zc - FLOOR_T, CLIP_X, wy, FLOOR_T) \
        .cut(cq.Workplane('YZ').workplane(offset=-CLIP_L).circle(ro - 0.3).extrude(2 * CLIP_L)
             .rotate((0, 0, 0), (0, 1, 0), -CLIP_TILT).translate((CLIP_X, wy, zc)))
    return f.union(clip).union(foot)


def clip_axis_z(x):
    """Height of the tube's axis in the clip at x: it falls toward the well, reaching the well's bottom at its centre."""
    z_tip = FLOOR_T + 0.3 + P.TUBE_OD / 2            # bag film under the tube
    return z_tip + math.tan(math.radians(CLIP_TILT)) * (x - WELL_XY[0])


def build_tray():
    tray = _cyl(TRAY_R, FLOOR_T)
    adds, cuts, bumps = _collar()
    a, c = _pump_cradle()
    adds += a + [_splash_wall()]
    cuts += c
    tray = tray.union(_union_all(adds)).union(_bag_floor())
    for c in cuts:
        tray = tray.cut(c)
    for (x, y) in DRAIN_XY:
        tray = tray.cut(_cyl(DRAIN_D / 2, FLOOR_T + 2, x, y, -1))
    return tray.union(_union_all(bumps))


# ------------------------------------------------------------------ envelopes
def _envelopes():
    head = _box(P.PUMP_W, PUMP_HEAD_L_EST, P.PUMP_H, PUMP_X, PUMP_HEAD_FACE_Y - PUMP_HEAD_L_EST / 2, 0)
    motor = cq.Workplane('XZ').workplane(offset=-(PUMP_HEAD_FACE_Y - PUMP_HEAD_L_EST + 0.01)) \
        .center(PUMP_X, P.PUMP_H / 2).circle(P.PUMP_MOTOR_D / 2).extrude(PUMP_MOTOR_L)
    bag = _cyl(BAG_R, BAG_Z[1] - BAG_Z[0], z0=BAG_Z[0]).intersect(_box(200, 400, 200, BAG_X1 - 100, 0, 0)).cut(_bag_floor())
    sweep = []
    hl = _half_deg(LUG_W, LUG_R0)
    for a in LUG_ANGLES:     # down the entry slot from above the collar, then the twist along the leg
        sweep.append(_sector(LUG_R0, R_IN, a + LUG_TWIST - hl, a + LUG_TWIST + hl, LUG_Z[0] - 2.5, SPLASH_H + COVER_T + 3))
        sweep.append(_sector(LUG_R0, R_IN, a - hl, a + LUG_TWIST + hl, LUG_Z[0] - 2.5, LUG_Z[1]))
    return {'pump_envelope': head.union(motor), 'bag_envelope': bag, 'lug_sweep_envelope': _union_all(sweep)}


def build_cover():
    """Lid over the bag bay (assembly position): rests on the splash wall and the raised rim, a lip under it keeps it
    in place, a notch lets the drum's lug pass on its way down, a finger hole lifts it. The bag stays flat under it."""
    z0 = SPLASH_H
    c = _bay_region(TRAY_R - 0.3, z0, z0 + COVER_T).intersect(_box(200, 400, 200, SPLASH_X[1] - 0.2 - 100, 0, 0))
    lw, lh = COVER_LIP
    a0 = math.degrees(math.acos(SPLASH_X[0] / COLLAR_RI))
    c = c.union(_sector(COLLAR_RI - P.FIT - lw, COLLAR_RI - P.FIT, a0 + 2, 360 - a0 - 2, z0 - lh, z0 + 0.01))
    c = c.union(_box(lw, 2 * math.sqrt(COLLAR_RI ** 2 - SPLASH_X[0] ** 2) - 20, lh + 0.01,
                     SPLASH_X[0] - P.FIT - lw / 2, 0, z0 - lh))
    hs = _half_deg(SLOT_W, TRAY_R) + 1.0
    for a in LUG_ANGLES:
        e = a + LUG_TWIST
        c = c.cut(_sector(LUG_R0 - 0.5, TRAY_R + 1, e - hs, e + hs, z0 - lh - 1, z0 + COVER_T + 1))
    (fx, fy), fd = COVER_FINGER
    return c.cut(_cyl(fd / 2, COVER_T + 2, fx, fy, z0 - 1))


def build():
    parts = {'base': build_base(), 'base_tray': build_tray(),
             'bag_cover': build_cover().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, SPLASH_H + COVER_T))}   # top down
    parts.update(_envelopes())
    return parts


def placements():
    return {
        'base': ((0, 0, 1), 0, (0, 0, 0)),
        'base_tray': ((0, 0, 1), 0, (0, 0, 0)),
        'bag_cover': ((1, 0, 0), 180, (0, 0, SPLASH_H + COVER_T)),
        'pump_envelope': ((0, 0, 1), 0, (0, 0, FLOOR_T)),
        'bag_envelope': ((0, 0, 1), 0, (0, 0, 0)),
        'lug_sweep_envelope': ((0, 0, 1), 0, (0, 0, 0)),
    }
