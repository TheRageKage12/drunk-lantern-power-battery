"""
sphere.py - the lantern body: two sphere halves, bay floor, guide boss, glass well, nozzle guide, lock wall, plus the
glass, glass path and hand envelopes.

Rev C (2026-10-23): a 224 mm sphere with the same 136.8 mm flats. A round lens opening in the front half takes the
front bell, a round hand opening in the rear half takes the rear bell (parts/bells.py). Everything inside (bay floor,
glass well, nozzle, lock wall, lock) keeps its height relative to the sphere centre, so the printed parts carry over;
the foot's riser (parts/foot.py) now holds the bay floor up.

Local frame ("sphere frame"): origin at the sphere centre (assembly Z = Z_SPHERE_CENTER), Z up,
front (audience, lens) = -Y, rear (owner, hand opening) = +Y. Halves split on the XZ plane (y = 0).
"""
import math
import cadquery as cq
import params as P
import common as C

R_OUT = P.SPHERE_D / 2                      # 112
R_IN = R_OUT - P.WALL                       # 109.6
CUT = P.SPHERE_CUT                          # 88.7: flats at +/- CUT
FLAT_D = C.sphere_flat_d(P.SPHERE_D, CUT)   # 136.8
OPENING_ID = FLAT_D - 2 * P.WALL            # 132.0: MATING with the neck locating rings (OD 131.4)
OPENING_DEPTH = 9.0                         # collar depth from each flat
COLLAR_R_OUT = OPENING_ID / 2 + 4.5         # 70.5: the collar ring inside each flat (the shell alone gives 1.2 mm)
Z_LOWER_SCREWS = -CUT + P.JOINT_SCREW_ABOVE_FLAT   # -85.7, matches foot.Z_SPHERE_SCREWS
Z_UPPER_SCREWS = CUT - P.JOINT_SCREW_ABOVE_FLAT    # +85.7, matches top.Z_SPHERE_SCREWS
# Thumbscrews (2026-10-23) at both flats, toward the back and sides, away from the front lens (and clear of the wall
# extension's tabs at the top): the top cap and the base come off with them, leaving the sphere.
JOINT_ANGLES = (10.0, 90.0, 170.0)          # bottom flat, into the foot's riser
TOP_JOINT_ANGLES = JOINT_ANGLES             # top flat, into the top cap's plug
BAY_FLOOR_Z = -52.5                         # rev C: held at the rev-9 height (36 mm above the flat) on the foot's riser

# flange (joining ring inside the rear half, flush with the split face; the front half's bosses meet it there)
# rev 9g: it used to span the split with its OD 0.3 inside the rear half's bore, so it never fused with the shell
# (sphere_rear exported as 3 bodies, standing on two loose arcs). Now it is fused and flush: the dish rings
# align the halves, the four screws hold them together.
FLANGE_W, FLANGE_T = P.SPHERE_FLANGE_W, 3.0 # 8 wide, 2 x FLANGE_T thick, all in the rear half
FLANGE_R_OUT = R_IN + 0.5                   # 88.1: overlaps the wall so the union fuses
FLANGE_R_IN = R_IN - P.FIT - FLANGE_W       # 79.3
FLANGE_SCREW_ANGLES = (30.0, 150.0, 210.0, 330.0)   # in the XZ plane from +X; |z| = 41.7 stays inside the clipped flange
FLANGE_SCREW_R = FLANGE_R_IN + FLANGE_W / 2 # 83.3
BOSS_L = 9.0                                # insert boss length along -Y on the front half

# rev C openings and the bell mounts (2026-10-23): a plain collar stands out round each opening; the bell slides over it
# and two thumbscrews from below, through the bell's throat into bosses in the collar, hold it. No tools needed.
# Bell frame: the bell's axis is +Z (s = distance out from the sphere centre); sign -1 front (-Y), +1 rear (+Y).
LENS_R, HAND_R = P.LENS_OPENING_R, P.HAND_OPENING_R    # 57, 70
COLLAR_T = 3.7                              # collar wall
COLLAR_OUT = 7.6                            # collar end, this far out from the sphere surface at the opening edge
BELL_LOCK_ANGLES = (225.0, 315.0)           # thumbscrews in the XZ plane from +X: under the bell, either side
THUMB_PILOT_DEPTH = 6.5
PAD_R = 4.5
PIVOT_ENTRY = 0.6                           # the curved surface over a 4 mm bore: full wall starts this far in
# ring pivots for the handle: each pivot boss (parts/handle.py) sits over the seam and screws into both halves
PIVOT_SCREWS = ((-12.0, -10.0), (12.0, -10.0))   # (y, z) of the two M3 inserts on each side, axis along X
PIVOT_BOSS_DEPTH = P.M3_INSERT_DEPTH + 2.5   # insert boss length inward from the outer surface (its entry is curved)

# bay floor and lock wall (rev 8)
BAY_FLOOR_OD = 131.0
WALL_T = P.LOCK_WALL_T
WALL_FRONT_Y = P.LOCK_FACE_Y - P.SOCKET_MODULE_DEPTH      # -25.2: the socket base plate sits here
WALL_BACK_Y = WALL_FRONT_Y - WALL_T                        # -27.6: LED rows for the display window, tube behind
WALL_W, WALL_H = 120.0, 99.0                               # from the bay floor top (rev 9: to 1 mm under the old upper dish plug)
WALL_Z0 = BAY_FLOOR_Z + P.FLOOR                            # -50.5: bay floor top (wall-local z = 0)
NOTCH_HW = 33.0                                            # notch over the glass slot (flange at +-32)
NOTCH_TOP = P.GLASS_TOP_Z_LOCAL + 3.0 - WALL_Z0            # 16.5: lower edge of the wall over the glass
TAB_X0, TAB_X1 = 42.0, 50.0                                # tabs into the bay floor slots
STRIP_CH_W, STRIP_CH_D = 10.2, 1.5                         # channels for 8 mm strip
BACK_ROWS = (34.0, 65.5, 76.5, 87.5)                       # wall-local z of the 4 rows on the back face (2 x 5 cm each)
BACK_ROW_L = 100.0
FRONT_COL_X, FRONT_COL_Z = 54.0, (29.5, 79.5)              # one 5 cm column either side of the lock
HALL_WIN_W, HALL_WIN_H = 34.0, 18.0                        # window behind the Hall board for the cables
SWITCH_WIRE_NOTCH_R = 29.5                                 # = socket.WIRE_NOTCH_R: the plate's wire notch, at socket +Y
SWITCH_WIRE_WIN = (9.0, 7.0)                               # window in the wall under that notch (notch is 6 x 3)
WALL_POSTS = ((-40.0, 55.0), (40.0, 55.0), (-47.0, 25.0), (47.0, 25.0))   # spacer posts (rev 9: to the diffuser at y -60); rev C: free ends
DIFF_Y, DIFF_T = -60.0, 1.0                 # rev 9 diffuser plane: the printed wall's posts still end here
GLASS_OUT_Y = P.GLASS_POUR_Y + P.GLASS_SLIDE                # +17: glass centre where it is lifted out
WELL_YC = (P.GLASS_POUR_Y + GLASS_OUT_Y) / 2               # slot centre
WELL_L = P.GLASS_SLIDE + P.WELL_ID                         # 78: inner slot length
WELL_FLANGE_W, WELL_FLANGE_T = 3.0, 2.0
WELL_SKIRT = P.FLOOR                        # 45 deg skirt height = bay floor thickness
GLASS_BASE_Z = P.GLASS_TOP_Z_LOCAL - P.GLASS_H            # -100: slot floor under the glass at the pour position
_BEND = math.radians(P.NOZZLE_BEND_DEG)
NOZZLE_DIR = (math.sin(_BEND), math.cos(_BEND))            # tube direction at the tip in (x, z): 45 deg down
ARC_END = (P.NOZZLE_BEND_R * (1 - math.cos(_BEND)), P.NOZZLE_RISE + P.NOZZLE_BEND_R * math.sin(_BEND))   # from the floor exit
NOZZLE_TIP_DXZ = (ARC_END[0] + P.NOZZLE_TIP_OUT * NOZZLE_DIR[0], ARC_END[1] + P.NOZZLE_TIP_OUT * NOZZLE_DIR[1])
GROMMET_XY = (P.NOZZLE_TIP_XY[0] - NOZZLE_TIP_DXZ[0], P.NOZZLE_TIP_XY[1])   # (-37, -31.1): tube exit
NOZZLE_TIP_Z = WALL_Z0 + NOZZLE_TIP_DXZ[1]                 # -30.3: tube end, 6.7 mm above the rim
GUIDE_SCREW = (GROMMET_XY[0] - 8.0, GROMMET_XY[1] - 10.0)   # nozzle guide foot screw
GUIDE_INSERT_BOSS_R = 4.0                   # 2 mm plastic wall around the 4 mm insert bore
GUIDE_INSERT_BOSS_BOTTOM = P.FLOOR - P.M3_INSERT_DEPTH - 1.5  # 1.5 mm closed end below the insert
WIRE_SLOT_XY = (35.0, -32.0)                               # cables down, behind the wall
WIRE_HOLE_D = 7.0

Z_ASM = P.Z_SPHERE_CENTER


def cyl(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def big_box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center((x0 + x1) / 2, (y0 + y1) / 2).rect(x1 - x0, y1 - y0).extrude(z1 - z0)


def shell():
    s = cq.Workplane('XY').sphere(R_OUT).cut(cq.Workplane('XY').sphere(R_IN))
    # a collar ring inside each flat: the neck plugs locate in it and its radial screws bite in it
    for z0 in (-CUT, CUT - OPENING_DEPTH):
        s = s.union(cyl(COLLAR_R_OUT, z0, z0 + OPENING_DEPTH).intersect(cq.Workplane('XY').sphere(R_OUT - 0.5)))
    for blk in thumb_bosses():
        s = s.union(blk.intersect(cq.Workplane('XY').sphere(R_OUT - 0.05)))
    s = s.intersect(big_box(-130, 130, -130, 130, -CUT, CUT))
    # open both flats to the mating ID over the collar depth
    s = s.cut(cyl(OPENING_ID / 2, -CUT - 1, -CUT + OPENING_DEPTH))
    s = s.cut(cyl(OPENING_ID / 2, CUT - OPENING_DEPTH, CUT + 1))
    return s


def y_cyl(r, y0, y1, x=0.0, z=0.0):
    """Cylinder along Y from y0 to y1 (either order) centred on (x, z)."""
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Workplane('XZ').workplane(offset=-hi).center(x, z).circle(r).extrude(hi - lo)


def bell_frame_angle(sign, a):
    """Assembly XZ angle -> bell-frame angle (the rear bell's frame is upside down: its +Y is the assembly's -Z)."""
    return a if sign < 0 else -a


def to_sphere(wp, sign):
    """Bell frame -> sphere frame."""
    return wp.rotate((0, 0, 0), (1, 0, 0), 90 if sign < 0 else -90)


def sector(r0, r1, a0, a1, z0, z1):
    """Annular sector r0..r1 between angles a0 < a1 (deg) about Z, z0..z1."""
    n = max(4, int((a1 - a0) / 3) + 1)
    pt = lambda r, a: (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
    pts = [pt(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [pt(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def collar_dims(sign):
    """(opening r, collar outer r, collar end s, -) for the front (-1) or rear (+1) opening."""
    r = LENS_R if sign < 0 else HAND_R
    s_end = math.sqrt(R_OUT ** 2 - r * r) + COLLAR_OUT
    return r, r + COLLAR_T, s_end, (s_end - 6.0, s_end - 1.0)


def lock_s(sign):
    return collar_dims(sign)[2] - 3.5


def bell_collar(sign):
    """Locating collar round an opening, in the bell frame, with a boss inside it under each thumbscrew (45 deg
    undersides: the halves print dome up). Returns (collar, pilot holes)."""
    r, ro, s_end, _ = collar_dims(sign)
    c = cq.Workplane('XY').circle(ro).circle(r).extrude(s_end)
    c = c.cut(cq.Workplane('XY').sphere(R_IN + 0.5))               # stops inside the shell
    sl = lock_s(sign)
    r0 = ro - (THUMB_PILOT_DEPTH + 1.5)
    hole = None
    for a in BELL_LOCK_ANGLES:
        ab = bell_frame_angle(sign, a)
        prof = [(r0, sl - 4.0), (ro - 0.5, sl - 4.0 - (ro - 0.5 - r0)), (ro - 0.5, s_end), (r0, s_end)]
        c = c.union(cq.Workplane('XZ').polyline(prof).close().extrude(5.0, both=True).rotate((0, 0, 0), (0, 0, 1), ab))
        h = cq.Workplane(cq.Plane(origin=(ro + 0.5, 0, sl), normal=(-1, 0, 0))).circle(P.THUMB_PILOT / 2) \
            .extrude(THUMB_PILOT_DEPTH + 0.5).rotate((0, 0, 0), (0, 0, 1), ab)
        hole = h if hole is None else hole.union(h)
    return c.intersect(cq.Workplane('XY').sphere(R_OUT + 40)), hole


def pivot_bosses(half):
    """M3 insert bosses (axis along X) for the handle's pivot bosses, on the given half ('front' y < 0, 'rear' y > 0)."""
    adds, cuts = [], []
    for sx in (-1, 1):
        for y, z in PIVOT_SCREWS:
            if (y < 0) != (half == 'front'):
                continue
            x_surf = math.sqrt(R_OUT ** 2 - y * y - z * z)
            x0 = sx * (x_surf - PIVOT_BOSS_DEPTH)
            boss = cq.Workplane('YZ').workplane(offset=x0).center(y, z).circle(PAD_R).extrude(sx * (PIVOT_BOSS_DEPTH + 2))
            adds.append(boss.intersect(cq.Workplane('XY').sphere(R_OUT - 0.2)))
            cuts.append(cq.Workplane('YZ').workplane(offset=sx * (x_surf + 0.5)).center(y, z)
                        .circle(P.M3_INSERT_HOLE / 2).extrude(-sx * (P.M3_INSERT_DEPTH + 0.5 + PIVOT_ENTRY)))
    return adds, cuts


THUMB_SEAT_R = OPENING_ID / 2 + P.THUMB_GRIP    # 69: flat seat for a thumbscrew's collar, 3 mm outside the bore


def radial_screw_cutters(z, angles):
    """Thumbscrew holes through the collar at height z: a flat seat spot-faced into the curved shell at THUMB_SEAT_R
    (the knurled head then stands clear of the surface for fingers), and a clearance hole into the plug's boss."""
    r_surf = math.sqrt(R_OUT ** 2 - z ** 2)        # 72.1 at z = +/-85.7
    cuts = []
    for a in angles:
        cuts.append(C.radial_hole(z, a, r_surf + 2.0, r_surf + 2.0 - (OPENING_ID / 2 - 1.0), P.THUMB_CLEAR))
        cuts.append(C.radial_hole(z, a, r_surf + 2.0, r_surf + 2.0 - THUMB_SEAT_R, P.THUMB_COLLAR_D + 0.8))
        cuts.append(C.radial_hole(z, a, R_OUT, R_OUT - THUMB_SEAT_R - P.THUMB_COLLAR_L, P.THUMB_HEAD_D + 2.0))   # head well
    return cuts


def thumb_bosses():
    """Solid blocks behind each thumbscrew, from the bore out to the shell, so the head's well cannot open into the
    sphere (the collar ring alone meets the shell only near the flat)."""
    out = []
    for zs, angles in ((-1, JOINT_ANGLES), (1, TOP_JOINT_ANGLES)):
        z0, z1 = sorted((zs * CUT, zs * (CUT - 16.0)))
        for a in angles:
            half = math.degrees(9.0 / OPENING_ID * 2)
            out.append(sector(OPENING_ID / 2, R_OUT, a - half, a + half, z0, z1))
    return out


def flange_solid():
    f = (cq.Workplane('XZ').workplane(offset=-2 * FLANGE_T)   # spans y in [0, 2 * FLANGE_T]: inside the rear half
         .circle(FLANGE_R_OUT).circle(FLANGE_R_IN).extrude(2 * FLANGE_T))
    f = f.intersect(big_box(-130, 130, -10, 10, -CUT + OPENING_DEPTH + 0.5, CUT - OPENING_DEPTH - 0.5))
    # keep the flange clear of the hatch opening on the rear half (hatch is at +Y so the flange ring at y~0 is fine)
    for a in FLANGE_SCREW_ANGLES:
        x, z = FLANGE_SCREW_R * math.cos(math.radians(a)), FLANGE_SCREW_R * math.sin(math.radians(a))
        f = f.cut(cq.Workplane('XZ').workplane(offset=-2 * FLANGE_T - 1).center(x, z).circle(P.M3_CLEAR / 2).extrude(2 * FLANGE_T + 2))
    return f


def front_bosses():
    """Insert bosses on the front half's inner wall for the flange screws (axis along Y)."""
    adds, cuts = [], []
    for a in FLANGE_SCREW_ANGLES:
        x, z = FLANGE_SCREW_R * math.cos(math.radians(a)), FLANGE_SCREW_R * math.sin(math.radians(a))
        boss = cq.Workplane('XZ').workplane(offset=P.FIT).center(x, z).circle(4.5).extrude(BOSS_L)   # y from -0.3 to -9.3
        adds.append(boss)
        cuts.append(cq.Workplane('XZ').workplane(offset=P.FIT - 0.5).center(x, z).circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH + 0.5))
    return adds, cuts


def build_halves():
    s = shell()
    cuts = radial_screw_cutters(Z_LOWER_SCREWS, JOINT_ANGLES) + radial_screw_cutters(Z_UPPER_SCREWS, TOP_JOINT_ANGLES)
    for c in cuts:
        s = s.cut(c)
    front = s.intersect(big_box(-130, 130, -130, 0, -130, 130))
    rear = s.intersect(big_box(-130, 130, 0, 130, -130, 130))

    # ---- front: lens opening and its bell collar, flange bosses, pivot bosses
    adds, fcuts = front_bosses()
    a, c = pivot_bosses('front')
    adds += a
    fcuts += c
    for a in adds:
        front = front.union(a)
    front = front.cut(y_cyl(LENS_R, -40, -130))
    collar, hole = bell_collar(-1)
    front = front.union(to_sphere(collar, -1)).cut(to_sphere(hole, -1))
    for c in fcuts:
        front = front.cut(c)

    # ---- rear: flange, hand opening (the fist goes in here) and its bell collar, pivot bosses
    rear = rear.union(flange_solid())
    adds, rcuts = pivot_bosses('rear')
    for a in adds:
        rear = rear.union(a)
    rear = rear.cut(y_cyl(HAND_R, 40, 130))
    collar, hole = bell_collar(+1)
    rear = rear.union(to_sphere(collar, +1)).cut(to_sphere(hole, +1))
    for c in rcuts:
        rear = rear.cut(c)
    return front, rear


def bay_floor():
    """Floor of the glass bay (drip tray): slot for the glass well, tube hole, cable hole, carrier slots."""
    f = cyl(BAY_FLOOR_OD / 2, 0, P.FLOOR)
    f = f.union(cyl(BAY_FLOOR_OD / 2, 0, P.FLOOR + 2.0).cut(cyl(BAY_FLOOR_OD / 2 - 1.6, -1, P.FLOOR + 3)))   # drip lip
    sw, sl = P.WELL_ID + 2 * P.WELL_WALL + 2 * P.FIT, WELL_L + 2 * P.WELL_WALL + 2 * P.FIT
    f = f.cut(slot(sw, sl, -1, P.FLOOR + 1))
    chamfer = (cq.Workplane('XY').center(0, WELL_YC).slot2D(sl, sw, angle=90)
               .workplane(offset=P.FLOOR).slot2D(sl + 2 * WELL_SKIRT, sw + 2 * WELL_SKIRT, angle=90).loft())
    f = f.cut(chamfer)                                       # seat for the well's skirt
    yc = (WALL_FRONT_Y + WALL_BACK_Y) / 2
    for sx in (-1, 1):                                        # slots for the lock wall's two tabs
        x0, x1 = sorted((sx * (TAB_X0 - 0.5), sx * (TAB_X1 + 0.5)))
        f = f.cut(big_box(x0, x1, yc - WALL_T / 2 - 0.4, yc + WALL_T / 2 + 0.4, -1, P.FLOOR + 1))
    f = f.cut(cyl(P.TUBE_GROMMET_D / 2, -1, P.FLOOR + 3, *GROMMET_XY))
    f = f.cut(cyl(WIRE_HOLE_D / 2, -1, P.FLOOR + 3, *WIRE_SLOT_XY))
    # The nozzle guide's insert bore goes through the 2 mm floor into guide_boss, glued underneath
    f = f.cut(cyl(P.M3_INSERT_HOLE / 2, -1, P.FLOOR + .5, *GUIDE_SCREW))
    return f


def guide_boss():
    """Insert boss glued under the bay floor (bay-floor frame). The 2 mm floor alone cannot retain a 6 mm insert, so
    the bore continues into this boss, which hangs into a matching notch in the foot's riser. A separate part so the
    bay floor prints flat, lip up, without supports."""
    b = cyl(GUIDE_INSERT_BOSS_R, GUIDE_INSERT_BOSS_BOTTOM, 0, *GUIDE_SCREW)
    return b.cut(cyl(P.M3_INSERT_HOLE / 2, P.FLOOR - P.M3_INSERT_DEPTH, 0.5, *GUIDE_SCREW))


def slot(w, l, z0, z1, yc=None):
    """Stadium (two half-circles joined by straight sides) along Y, w wide and l long overall, centred on the slot."""
    yc = WELL_YC if yc is None else yc
    return cq.Workplane('XY').workplane(offset=z0).center(0, yc).slot2D(l, w, angle=90).extrude(z1 - z0)


def glass_well():
    """Slot the glass slides in. Hangs from its flange on the bay floor, down into the foot's neck.
    Built and printed floor down: z = 0 is the outside bottom, the flange is at the top with a 45 deg skirt."""
    top = (BAY_FLOOR_Z + P.FLOOR + WELL_FLANGE_T) - (GLASS_BASE_Z - P.FLOOR)   # outside bottom -> flange top
    ow, ol = P.WELL_ID + 2 * P.WELL_WALL, WELL_L + 2 * P.WELL_WALL
    fw, sk = WELL_FLANGE_W, WELL_SKIRT
    w = slot(ow, ol, 0, top)
    w = w.union(slot(ow + 2 * fw, ol + 2 * fw, top - WELL_FLANGE_T, top))
    # 45 deg skirt under the flange (prints without support); it sits in the chamfer of the bay floor slot
    skirt = (cq.Workplane('XY').workplane(offset=top - WELL_FLANGE_T - sk).center(0, WELL_YC).slot2D(ol, ow, angle=90)
             .workplane(offset=sk).slot2D(ol + 2 * sk, ow + 2 * sk, angle=90).loft())
    w = w.union(skirt)
    w = w.cut(slot(P.WELL_ID, WELL_L, P.FLOOR, top + 1))
    # detent: a low triangular ridge across the floor just behind the glass base at the pour position
    ys, h = P.GLASS_POUR_Y + P.GLASS_D_BASE / 2 + 1.0, P.WELL_RIDGE_H
    ridge = (cq.Workplane('YZ').polyline([(ys, P.FLOOR - 0.1), (ys + 2 * h, P.FLOOR + h), (ys + 4 * h, P.FLOOR - 0.1)]).close()
             .extrude(P.WELL_ID / 2 + 1, both=True))
    return w.union(ridge.intersect(slot(P.WELL_ID + 0.2, WELL_L + 0.2, 0, top)))


HAND_PATH_Y1 = 160.0                        # rev C: the hand and the glass travel out past the rear bell's mouth (151)


def glass_path():
    """Everything the glass passes through on the way out: the slide back at rim height, the lift, then (rev C) out
    through the hand opening and the rear bell, carried upright with its base just over the drip lip."""
    r = P.GLASS_D_TOP / 2 + 1.5
    z0 = BAY_FLOOR_Z + P.FLOOR + WELL_FLANGE_T                # flange top
    rim = P.GLASS_TOP_Z_LOCAL + P.WELL_RIDGE_H + 1.0          # rim while the base rides over the ridge, + 1 mm
    slide = slot(2 * r, P.GLASS_SLIDE + 2 * r, z0, rim)
    lift = cq.Workplane('XY').workplane(offset=z0).center(0, GLASS_OUT_Y).circle(r).extrude(P.GLASS_H + 3.0)
    out = big_box(-r, r, GLASS_OUT_Y, HAND_PATH_Y1, z0 + 2.0, z0 + 2.0 + P.GLASS_H + 1.0)
    return slide.union(lift).union(out)


def nozzle_guide():
    """Curved channel behind the lock wall that turns the tube from vertical (out of the bay floor) through
    NOZZLE_BEND_DEG, so the tip points 45 deg down into the back third of the glass. Its +Y side is open (a C-channel):
    the wall's back face closes it, so the tube can sit 3.5 mm from the wall. The tube sticks out NOZZLE_TIP_OUT.
    Built relative to the tube's floor exit; +Y points at the wall."""
    r = P.NOZZLE_BEND_R
    bore_d = P.TUBE_OD + 0.6
    to_wall = WALL_BACK_Y - GROMMET_XY[1]                     # 3.5: bore centre -> wall back face
    half_x, back = bore_d / 2 + 1.2, bore_d / 2 + 1.6
    h = P.NOZZLE_RISE
    # path in the XZ plane: straight up h, then an arc turning toward +X (over the glass) past horizontal
    mid = (r * (1 - math.cos(_BEND / 2)), h + r * math.sin(_BEND / 2))
    path = cq.Workplane('XZ').moveTo(0, 0).lineTo(0, h).threePointArc(mid, ARC_END)
    y0, y1 = -back, to_wall - 1.5      # the bore breaks through the +Y face as a 5.7 mm slit: the tube presses in
    outer = cq.Workplane('XY').center(0, (y0 + y1) / 2).rect(2 * half_x, y1 - y0).sweep(path)
    bore = cq.Workplane('XY').workplane(offset=-1).circle(bore_d / 2).extrude(1).union(
        cq.Workplane('XY').circle(bore_d / 2).sweep(path))
    g = outer.cut(bore)
    sx, sy = GUIDE_SCREW[0] - GROMMET_XY[0], GUIDE_SCREW[1] - GROMMET_XY[1]
    foot = big_box(sx - 5.0, half_x, sy - 5.0, y1, 0, 3.0)
    foot = foot.cut(cyl(bore_d / 2, -1, 4)).cut(cyl(P.M3_CLEAR / 2, -1, 4, sx, sy))
    return g.union(foot)


def lock_wall():
    """The wall just inside the hand port: the lock on its front face, the nozzle hidden behind it, LED strips on
    both faces. Wall-local frame: x as the sphere, y = 0 the back face (display side), y = WALL_T the front face
    (your side), z = 0 the bay floor top."""
    T = WALL_T
    w = big_box(-WALL_W / 2, WALL_W / 2, 0, T, 0, WALL_H)
    w = w.cut(big_box(-NOTCH_HW, NOTCH_HW, -1, T + 1, -1, NOTCH_TOP))            # the glass passes under here
    for sx in (-1, 1):
        x0, x1 = sorted((sx * TAB_X0, sx * TAB_X1))
        w = w.union(big_box(x0, x1, 0, T, -P.FLOOR - 0.5, 0))                    # tabs into the bay floor
        x0, x1 = sorted((sx * (WALL_W / 2 - 8.0), sx * (WALL_W / 2 + 1)))
        w = w.cut(big_box(x0, x1, -1, T + 1, -1, 6.0))                          # clears the drip lip
    # LED channels: rows on the back face, a column either side of the lock on the front face
    for z0 in BACK_ROWS:
        w = w.cut(big_box(-BACK_ROW_L / 2, BACK_ROW_L / 2, -1, STRIP_CH_D, z0, z0 + STRIP_CH_W))
    for sx in (-1, 1):
        xc = sx * FRONT_COL_X
        w = w.cut(big_box(xc - STRIP_CH_W / 2, xc + STRIP_CH_W / 2, T - STRIP_CH_D, T + 1, *FRONT_COL_Z))
        w = w.cut(cq.Workplane('XZ').workplane(offset=-(T + 1)).center(xc, FRONT_COL_Z[0] - 3.0)
                  .circle(1.75).extrude(T + 2))                                 # wire hole to the back
    # the lock: two ear screws and the window behind the Hall board
    zr = P.SOCKET_Z_LOCAL - WALL_Z0
    for a in P.SOCKET_EAR_ANGLES:
        ex, ez = P.SOCKET_EAR_R * math.cos(math.radians(a)), zr - P.SOCKET_EAR_R * math.sin(math.radians(a))
        w = w.cut(cq.Workplane('XZ').workplane(offset=-(T + 1)).center(ex, ez).circle(P.M3_CLEAR / 2).extrude(T + 2))
    w = w.cut(big_box(-HALL_WIN_W / 2, HALL_WIN_W / 2, -1, T + 1, zr - HALL_WIN_H / 2, zr + HALL_WIN_H / 2))
    # window for the switch wires: they leave the base plate through its wire notch at socket +Y (r 28..31),
    # which lands that far BELOW the ring centre on the wall (socket +Y -> sphere -Z); rev 9g, it was solid wall
    w = w.cut(big_box(-SWITCH_WIRE_WIN[0] / 2, SWITCH_WIRE_WIN[0] / 2, -1, T + 1,
                      zr - SWITCH_WIRE_NOTCH_R - SWITCH_WIRE_WIN[1] / 2, zr - SWITCH_WIRE_NOTCH_R + SWITCH_WIRE_WIN[1] / 2))
    # spacer posts from the back face to the display diffuser
    post_y = (DIFF_Y - DIFF_T) - WALL_BACK_Y                  # -33.4
    for (x, z) in WALL_POSTS:
        w = w.union(big_box(x - 3, x + 3, post_y, 0, z - 3, z + 3))
    return w


def _guide_origin():
    return (GROMMET_XY[0], GROMMET_XY[1], BAY_FLOOR_Z + P.FLOOR)   # tube exit on the bay floor top


def build():
    front, rear = build_halves()
    out = {
        'sphere_front': front.rotate((0, 0, 0), (1, 0, 0), -90),   # dome up, split face on the bed
        'sphere_rear': rear.rotate((0, 0, 0), (1, 0, 0), 90),
        'bay_floor': bay_floor(),                       # floor on the bed, drip lip up, no supports
        'guide_boss': guide_boss().translate((-GUIDE_SCREW[0], -GUIDE_SCREW[1], -GUIDE_INSERT_BOSS_BOTTOM)),   # glue face up
        'glass_well': glass_well(),
        'lock_wall': lock_wall().rotate((0, 0, 0), (1, 0, 0), -90),     # lie flat: back face (rows, posts) up
        'nozzle_guide': nozzle_guide(),
        'glass_envelope': cq.Workplane('XY').add(cq.Solid.makeCone(P.GLASS_D_BASE / 2 + 1.0, P.GLASS_D_TOP / 2, P.GLASS_H)),
        'glass_path_envelope': glass_path(),
        # the hand: a fist (ring face on the socket), and the fist's path in through the rear bell (rev C)
        'fist_envelope': cq.Workplane('XZ').ellipse(P.FIST_W / 2, P.FIST_H / 2).extrude(-P.FIST_LEN),
        'hand_path_envelope': cq.Workplane('XZ').ellipse(P.FIST_W / 2, P.FIST_H / 2).extrude(-(HAND_PATH_Y1 - P.LOCK_FACE_Y - P.FIST_LEN)),
    }
    for k in ('sphere_front', 'sphere_rear', 'lock_wall'):
        bb = out[k].val().BoundingBox()
        _SHIFT[k] = -bb.zmin                           # placements() undoes this before rotating back
        out[k] = out[k].translate((0, 0, -bb.zmin))
    return out


_SHIFT = {}


def placements():
    Z = Z_ASM
    face_y = P.LOCK_FACE_Y                             # = socket.FACE_Y
    hand_z = Z + P.SOCKET_Z_LOCAL + P.FIST_Z_OFFSET
    gx, gy, gz = _guide_origin()
    if not _SHIFT:
        build()

    def unflat(k, angle, d):     # undo the print-bed shift, then rotate back into the sphere frame
        return [((0, 0, 1), 0, (0, 0, -_SHIFT[k])), ((1, 0, 0), angle, d)]
    return {
        'sphere_front': unflat('sphere_front', 90, (0, 0, Z)),
        'sphere_rear': unflat('sphere_rear', -90, (0, 0, Z)),
        'bay_floor': ((0, 0, 1), 0, (0, 0, Z + BAY_FLOOR_Z)),
        'guide_boss': ((0, 0, 1), 0, (GUIDE_SCREW[0], GUIDE_SCREW[1], Z + BAY_FLOOR_Z + GUIDE_INSERT_BOSS_BOTTOM)),
        'glass_well': ((0, 0, 1), 0, (0, 0, Z + GLASS_BASE_Z - P.FLOOR)),   # printed the way it hangs
        'lock_wall': unflat('lock_wall', 90, (0, WALL_BACK_Y, Z + WALL_Z0)),
        'nozzle_guide': ((0, 0, 1), 0, (gx, gy, Z + gz)),
        'glass_envelope': ((0, 0, 1), 0, (0, P.GLASS_POUR_Y, Z + GLASS_BASE_Z)),
        'glass_path_envelope': ((0, 0, 1), 0, (0, 0, Z)),
        'fist_envelope': ((0, 0, 1), 0, (0, face_y, hand_z)),
        'hand_path_envelope': ((0, 0, 1), 0, (0, face_y + P.FIST_LEN, hand_z)),
    }
