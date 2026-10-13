"""
sphere.py - the lantern body: two sphere halves, hatch door, diffuser, bay floor, glass tray, LED carrier,
nozzle clip, plus the glass envelope.

Local frame ("sphere frame"): origin at the sphere centre (assembly Z = Z_SPHERE_CENTER), Z up,
front (audience, window) = -Y, rear (owner, hatch) = +Y. Halves split on the XZ plane (y = 0).
"""
import math
import cadquery as cq
import params as P
import common as C

R_OUT = P.SPHERE_D / 2                      # 90
R_IN = R_OUT - P.WALL                       # 87.6
CUT = P.SPHERE_CUT                          # 58.5: flats at +/- CUT
FLAT_D = C.sphere_flat_d(P.SPHERE_D, CUT)   # 136.8
OPENING_ID = FLAT_D - 2 * P.WALL            # 132.0: MATING with the dish locating rings (OD 131.4)
OPENING_DEPTH = 9.0                         # collar depth from each flat (dishes.LOCATING_RING_H_UPPER)
Z_LOWER_SCREWS = -CUT + P.JOINT_SCREW_ABOVE_FLAT   # -55.5 (assembly 195), matches dishes.Z_SPHERE_LOWER_SCREWS
Z_UPPER_SCREWS = CUT - P.JOINT_SCREW_ABOVE_FLAT    # +55.5 (assembly 306)
JOINT_ANGLES = C.joint_angles()             # 90, 210, 330 (first at +Y)
BAY_FLOOR_Z = -CUT + 6.0                    # -52.5: bay_floor rests on the lower dish ring top (assembly 198)

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

# window (front) and diffuser
WIN_W, WIN_H = P.WINDOW_W, P.WINDOW_H       # 90 x 87: rectangle + semicircle top, centred so it clears the collars
WIN_R = WIN_W / 2                           # 45
WIN_Z0 = -(WIN_H - WIN_R)                   # -42 bottom edge; top of the arch at +45
DIFF_Y = -60.0                              # diffuser plane (chord radius 63.8 there)
DIFF_D, DIFF_T = P.DIFFUSER_D, P.DIFFUSER_T # 118 x 1.0
LEDGE_T, LEDGE_W = 2.0, 6.0                 # ring the diffuser rests against (far side)

# hand port (rear): open rounded rectangle the fist punches through
HATCH_W, HATCH_H, HATCH_R = P.HATCH_W, P.HATCH_H, 14.0    # 120 x 96
HATCH_Z0 = -48.0                            # bottom edge (collar top is at -49.5)
HATCH_ZC = HATCH_Z0 + HATCH_H / 2           # 0

# bay floor and lock wall (rev 8)
BAY_FLOOR_OD = 131.0
WALL_T = P.LOCK_WALL_T
WALL_FRONT_Y = P.LOCK_FACE_Y - P.SOCKET_MODULE_DEPTH      # -25.2: the socket base plate sits here
WALL_BACK_Y = WALL_FRONT_Y - WALL_T                        # -27.6: LED rows for the display window, tube behind
WALL_W, WALL_H = 120.0, 99.0                               # from the bay floor top to 1 mm under the upper plug
WALL_Z0 = -CUT + 6.0 + P.FLOOR                             # -50.5: bay floor top (wall-local z = 0)
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
WALL_POSTS = ((-40.0, 55.0), (40.0, 55.0), (-47.0, 25.0), (47.0, 25.0))   # spacer posts to the diffuser
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
WIRE_SLOT_XY = (35.0, -32.0)                               # cables down, behind the wall
WIRE_HOLE_D = 7.0

# handle bosses (match parts.handle): pocket 14.6 x 10.6 x 12 deep, open up, mouth at the equator
LEG_X = P.SPHERE_D / 2 + P.HANDLE_INNER_GAP + P.HANDLE_SECTION_T / 2   # 105
HANDLE_PLANE_Y = P.WALL + P.HANDLE_SECTION_T / 2                        # 7.4
BOSS_POCKET_W = P.HANDLE_SECTION_W + 2 * P.FIT    # 14.6 (X)
BOSS_POCKET_T = P.HANDLE_SECTION_T + 2 * P.FIT    # 10.6 (Y)
BOSS_POCKET_DEPTH = 12.0
BOSS_SCREW_Z = -BOSS_POCKET_DEPTH / 2       # -6 (assembly 244.5)

# nozzle clip

Z_ASM = P.Z_SPHERE_CENTER


def cyl(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def big_box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center((x0 + x1) / 2, (y0 + y1) / 2).rect(x1 - x0, y1 - y0).extrude(z1 - z0)


def shell():
    s = cq.Workplane('XY').sphere(R_OUT).cut(cq.Workplane('XY').sphere(R_IN))
    s = s.intersect(big_box(-100, 100, -100, 100, -CUT, CUT))
    # open both flats to the mating ID over the collar depth
    s = s.cut(cyl(OPENING_ID / 2, -CUT - 1, -CUT + OPENING_DEPTH))
    s = s.cut(cyl(OPENING_ID / 2, CUT - OPENING_DEPTH, CUT + 1))
    return s


def arch_cutter(w, h_rect, r, y0, y1, zc_bottom):
    """Arch (rectangle w x h_rect with a semicircle r on top), extruded along Y from y0 to y1, bottom at zc_bottom."""
    prof = (cq.Workplane('XZ').workplane(offset=-y1)   # XZ workplane normal is -Y; offset so the extrusion spans y0..y1
            .moveTo(-w / 2, zc_bottom).lineTo(w / 2, zc_bottom).lineTo(w / 2, zc_bottom + h_rect)
            .threePointArc((0, zc_bottom + h_rect + r), (-w / 2, zc_bottom + h_rect)).close())
    return prof.extrude(y1 - y0)


def rounded_rect_cutter_y(w, h, r, y0, y1, zc):
    prof = cq.Workplane('XZ').workplane(offset=-y1).center(0, zc).sketch().rect(w, h).vertices().fillet(r).finalize()
    return prof.extrude(y1 - y0)


def radial_screw_cutters(z, angles):
    """Horizontal M3 holes through the collar wall at height z (the shell is at r = sqrt(R_OUT^2 - z^2) there,
    not R_OUT), with a 2 mm counterbore measured from the surface on the hole axis."""
    r_surf = math.sqrt(R_OUT ** 2 - z ** 2)        # 70.9 at z = +/-55.5
    r_start = r_surf + 1.0
    cuts = []
    for a in angles:
        cuts.append(C.radial_hole(z, a, r_start, r_start - (OPENING_ID / 2 - 1.0), P.M3_CLEAR))   # through the collar
        cuts.append(C.radial_hole(z, a, r_start, 1.0 + 2.0, P.M3_HEAD_D + 0.2))                  # 2 mm counterbore
    return cuts


def flange_solid():
    f = (cq.Workplane('XZ').workplane(offset=-2 * FLANGE_T)   # spans y in [0, 2 * FLANGE_T]: inside the rear half
         .circle(FLANGE_R_OUT).circle(FLANGE_R_IN).extrude(2 * FLANGE_T))
    f = f.intersect(big_box(-100, 100, -10, 10, -CUT + OPENING_DEPTH + 0.5, CUT - OPENING_DEPTH - 0.5))
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


def handle_boss(sign):
    """Rectangular socket for a handle leg at x = sign*LEG_X, open at the top (equator), on the rear half."""
    x0 = sign * (R_OUT - 2.0)
    x1 = sign * (LEG_X + BOSS_POCKET_W / 2 + 2.4)
    y0, y1 = 0.0, HANDLE_PLANE_Y + BOSS_POCKET_T / 2 + 2.4
    blk = big_box(min(x0, x1), max(x0, x1), y0, y1, -BOSS_POCKET_DEPTH - 4.0, 0.0)
    pocket = big_box(sign * LEG_X - BOSS_POCKET_W / 2, sign * LEG_X + BOSS_POCKET_W / 2,
                     HANDLE_PLANE_Y - BOSS_POCKET_T / 2, HANDLE_PLANE_Y + BOSS_POCKET_T / 2, -BOSS_POCKET_DEPTH, 1.0)
    # insert in the pocket's inner (sphere-side) wall, axis along X, from the pocket face inward
    ins_x = sign * (LEG_X - BOSS_POCKET_W / 2)
    insert = (cq.Workplane('YZ').workplane(offset=ins_x).center(HANDLE_PLANE_Y, BOSS_SCREW_Z)
              .circle(P.M3_INSERT_HOLE / 2).extrude(-sign * P.M3_INSERT_DEPTH))
    # access hole through the pocket's outer wall, so the leg screw's head can be reached with a hex key
    out_x = sign * (LEG_X + BOSS_POCKET_W / 2 - 0.5)
    access = (cq.Workplane('YZ').workplane(offset=out_x).center(HANDLE_PLANE_Y, BOSS_SCREW_Z)
              .circle((P.M3_HEAD_D + 0.6) / 2).extrude(sign * 6.0))
    return blk, [pocket, insert, access]



def build_halves():
    s = shell()
    cuts = radial_screw_cutters(Z_LOWER_SCREWS, JOINT_ANGLES) + radial_screw_cutters(Z_UPPER_SCREWS, JOINT_ANGLES)
    for c in cuts:
        s = s.cut(c)
    front = s.intersect(big_box(-100, 100, -100, 0, -100, 100))
    rear = s.intersect(big_box(-100, 100, 0, 100, -100, 100))

    # ---- front: window, diffuser ledge, flange bosses, carrier-independent
    front = front.cut(arch_cutter(WIN_W, WIN_H - WIN_R, WIN_R, -100, -60, WIN_Z0))
    ledge = (cq.Workplane('XZ').workplane(offset=-(DIFF_Y - DIFF_T - LEDGE_T)).circle(DIFF_D / 2 + 2).circle(DIFF_D / 2 - LEDGE_W).extrude(LEDGE_T))
    ledge = ledge.intersect(cq.Workplane('XY').sphere(R_IN + 0.5))
    ledge = ledge.intersect(big_box(-100, 100, -100, 100, -CUT + OPENING_DEPTH + 0.5, CUT - OPENING_DEPTH - 0.5))   # stay off the dish plugs
    front = front.union(ledge)
    adds, bcuts = front_bosses()
    for a in adds:
        front = front.union(a)
    for c in bcuts:
        front = front.cut(c)

    # ---- rear: flange, hand port (open: the fist goes in here), handle bosses
    rear = rear.union(flange_solid())
    rear = rear.cut(rounded_rect_cutter_y(HATCH_W, HATCH_H, HATCH_R, 40, 100, HATCH_ZC))
    for sx in (-1, 1):
        blk, bc = handle_boss(sx)
        rear = rear.union(blk)
        for c in bc:
            rear = rear.cut(c)
    return front, rear



def diffuser():
    # flats top and bottom keep it off the dish plugs (the window spans z -42..+45)
    h = 2 * (CUT - OPENING_DEPTH - 0.5)
    return cq.Workplane('XY').circle(DIFF_D / 2).extrude(DIFF_T).intersect(
        cq.Workplane('XY').rect(DIFF_D + 2, h).extrude(DIFF_T))


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
    f = f.cut(cyl(P.M3_INSERT_HOLE / 2, -1, P.FLOOR + 1, *GUIDE_SCREW))   # nozzle guide screw
    return f


def slot(w, l, z0, z1, yc=None):
    """Stadium (two half-circles joined by straight sides) along Y, w wide and l long overall, centred on the slot."""
    yc = WELL_YC if yc is None else yc
    return cq.Workplane('XY').workplane(offset=z0).center(0, yc).slot2D(l, w, angle=90).extrude(z1 - z0)


def glass_well():
    """Slot the glass slides in. Hangs from its flange on the bay floor into the lower dish.
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


def glass_path():
    """Everything the glass passes through on the way out: the slide back at rim height, then the lift."""
    r = P.GLASS_D_TOP / 2 + 1.5
    z0 = BAY_FLOOR_Z + P.FLOOR + WELL_FLANGE_T                # flange top
    rim = P.GLASS_TOP_Z_LOCAL + P.WELL_RIDGE_H + 1.0          # rim while the base rides over the ridge, + 1 mm
    slide = slot(2 * r, P.GLASS_SLIDE + 2 * r, z0, rim)
    lift = cq.Workplane('XY').workplane(offset=z0).center(0, GLASS_OUT_Y).circle(r).extrude(P.GLASS_H + 3.0)
    return slide.union(lift)


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


def curtain_clamp():
    """Arc bar that clamps the strip curtain to the underside of the upper dish plug, just inside the hand port.
    Printed flat. Frame: the sphere axis at the origin, the arc centred on +Y."""
    r0, r1 = P.CURTAIN_R - 4.0, P.CURTAIN_R + 3.0
    a = P.CURTAIN_HALF_ANGLE
    ring = cq.Workplane('XY').circle(r1).circle(r0).extrude(CLAMP_T)
    sector = (cq.Workplane('XY').polyline([(0, 0)] + [(1.5 * r1 * math.cos(math.radians(90 + t)), 1.5 * r1 * math.sin(math.radians(90 + t)))
                                                  for t in (-a, -a / 2, 0, a / 2, a)]).close().extrude(CLAMP_T))
    c = ring.intersect(sector)
    for t in P.CURTAIN_SCREW_ANGLES:
        x, y = P.CURTAIN_R * math.cos(math.radians(t)), P.CURTAIN_R * math.sin(math.radians(t))
        c = c.cut(cyl(P.M3_CLEAR / 2, -1, CLAMP_T + 1, x, y))
    return c


CLAMP_T = 3.0
UPPER_PLUG_H = max(6.0, P.SOCKET_PLATE_T + P.M3_INSERT_DEPTH + 1.5 - P.FLOOR)   # = dishes.LOCATING_RING_H_UPPER


def _guide_origin():
    return (GROMMET_XY[0], GROMMET_XY[1], BAY_FLOOR_Z + P.FLOOR)   # tube exit on the bay floor top


def build():
    front, rear = build_halves()
    out = {
        'sphere_front': front.rotate((0, 0, 0), (1, 0, 0), -90),   # dome up, split face on the bed
        'sphere_rear': rear.rotate((0, 0, 0), (1, 0, 0), 90),
        'diffuser': diffuser(),
        'bay_floor': bay_floor(),
        'glass_well': glass_well(),
        'lock_wall': lock_wall().rotate((0, 0, 0), (1, 0, 0), -90),     # lie flat: back face (rows, posts) up
        'curtain_clamp': curtain_clamp(),
        'nozzle_guide': nozzle_guide(),
        'glass_envelope': cq.Workplane('XY').add(cq.Solid.makeCone(P.GLASS_D_BASE / 2 + 1.0, P.GLASS_D_TOP / 2, P.GLASS_H)),
        'glass_path_envelope': glass_path(),
        # the hand: a fist (ring face on the socket) and the forearm through the port
        'fist_envelope': cq.Workplane('XZ').ellipse(P.FIST_W / 2, P.FIST_H / 2).extrude(-P.FIST_LEN),
        'forearm_envelope': cq.Workplane('XZ').circle(P.FOREARM_R).extrude(-60.0),
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
        'diffuser': ((1, 0, 0), 90, (0, DIFF_Y - DIFF_T, Z)),
        'bay_floor': ((0, 0, 1), 0, (0, 0, Z + BAY_FLOOR_Z)),
        'glass_well': ((0, 0, 1), 0, (0, 0, Z + GLASS_BASE_Z - P.FLOOR)),   # printed the way it hangs
        'lock_wall': unflat('lock_wall', 90, (0, WALL_BACK_Y, Z + WALL_Z0)),
        'curtain_clamp': ((0, 0, 1), 0, (0, 0, P.Z_SPHERE_TOP - UPPER_PLUG_H - CLAMP_T)),   # under the upper dish plug
        'nozzle_guide': ((0, 0, 1), 0, (gx, gy, Z + gz)),
        'glass_envelope': ((0, 0, 1), 0, (0, P.GLASS_POUR_Y, Z + GLASS_BASE_Z)),
        'glass_path_envelope': ((0, 0, 1), 0, (0, 0, Z)),
        'fist_envelope': ((0, 0, 1), 0, (0, face_y, hand_z)),
        'forearm_envelope': ((0, 0, 1), 0, (0, face_y + P.FIST_LEN - 10.0, hand_z)),
    }
