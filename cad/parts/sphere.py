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
Z_LOWER_SCREWS = -CUT + 2.0                 # -56.5 (assembly 194)
Z_UPPER_SCREWS = CUT - 2.0                  # +56.5 (assembly 307)
JOINT_ANGLES = C.joint_angles()             # 90, 210, 330 (first at +Y)
BAY_FLOOR_Z = -CUT + 6.0                    # -52.5: bay_floor rests on the lower dish ring top (assembly 198)

# flange (register ring on the rear half, enters the front half)
FLANGE_W, FLANGE_T = P.SPHERE_FLANGE_W, 3.0 # 8 wide, 3 mm into the front half
FLANGE_R_OUT = R_IN - P.FIT                 # 87.3
FLANGE_R_IN = FLANGE_R_OUT - FLANGE_W       # 79.3
FLANGE_SCREW_ANGLES = (0.0, 180.0, 60.0, 120.0)   # in the XZ plane from +X
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

# bay floor, LED carrier
BAY_FLOOR_OD = 131.0
CARRIER_Y = -35.0
CARRIER_W, CARRIER_H, CARRIER_T = 110.0, 104.0, 2.4
STRIP_ROWS, STRIP_LEDS, ROW_PITCH = 9, 6, 12.0
STRIP_CH_W, STRIP_CH_D, STRIP_CH_L = 10.5, 1.5, 102.0
# punch-in layout: the glass sits in a sloped slot below the knuckles. It pours at the front end, under the
# nozzle tip, and is pulled back GLASS_SLIDE mm before lifting, so the lift path is clear of the tip and the
# socket. The tube and the cables pass through the bay floor inside the lower dish hole, outside the slot.
GLASS_OUT_Y = P.GLASS_POUR_Y + P.GLASS_SLIDE                # +22: glass centre where it is lifted out
WELL_YC = (P.GLASS_POUR_Y + GLASS_OUT_Y) / 2               # slot centre
WELL_L = P.GLASS_SLIDE + P.WELL_ID                         # 78: inner slot length
WELL_FLANGE_W, WELL_FLANGE_T = 3.0, 2.0
GLASS_BASE_Z = P.GLASS_TOP_Z_LOCAL - P.GLASS_H            # -100: slot floor under the glass at the pour position
GROMMET_XY = (P.NOZZLE_TIP_XY[0] - P.NOZZLE_TIP_OUT - P.NOZZLE_BEND_R, P.NOZZLE_TIP_XY[1])   # (-41, -6): tube exit
WIRE_SLOT_XY = (38.0, -6.0)
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
    cuts = []
    for a in angles:
        cuts.append(C.radial_hole(z, a, R_OUT + 2, P.WALL + 6, P.M3_CLEAR))
        cuts.append(C.radial_hole(z, a, R_OUT + 2, 2.0 + 2.0, P.M3_HEAD_D + 0.2))   # 2 mm counterbore
    return cuts


def flange_solid():
    f = (cq.Workplane('XZ').workplane(offset=-FLANGE_T)   # spans y in [-FLANGE_T, +FLANGE_T]
         .circle(FLANGE_R_OUT).circle(FLANGE_R_IN).extrude(2 * FLANGE_T))
    f = f.intersect(big_box(-100, 100, -10, 10, -CUT + OPENING_DEPTH + 0.5, CUT - OPENING_DEPTH - 0.5))
    # keep the flange clear of the hatch opening on the rear half (hatch is at +Y so the flange ring at y~0 is fine)
    for a in FLANGE_SCREW_ANGLES:
        x, z = FLANGE_SCREW_R * math.cos(math.radians(a)), FLANGE_SCREW_R * math.sin(math.radians(a))
        f = f.cut(cq.Workplane('XZ').workplane(offset=-FLANGE_T - 1).center(x, z).circle(P.M3_CLEAR / 2).extrude(2 * FLANGE_T + 2))
    return f


def front_bosses():
    """Insert bosses on the front half's inner wall for the flange screws (axis along Y)."""
    adds, cuts = [], []
    for a in FLANGE_SCREW_ANGLES:
        x, z = FLANGE_SCREW_R * math.cos(math.radians(a)), FLANGE_SCREW_R * math.sin(math.radians(a))
        boss = cq.Workplane('XZ').workplane(offset=FLANGE_T + P.FIT).center(x, z).circle(4.5).extrude(BOSS_L)   # y from -3.3 to -12.3
        adds.append(boss)
        cuts.append(cq.Workplane('XZ').workplane(offset=FLANGE_T + P.FIT - 0.5).center(x, z).circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH + 0.5))
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
    return blk, [pocket, insert]



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
    return cq.Workplane('XY').circle(DIFF_D / 2).extrude(DIFF_T)


def bay_floor():
    """Floor of the glass bay (drip tray): slot for the glass well, tube hole, cable hole, carrier slots."""
    f = cyl(BAY_FLOOR_OD / 2, 0, P.FLOOR)
    f = f.union(cyl(BAY_FLOOR_OD / 2, 0, P.FLOOR + 2.0).cut(cyl(BAY_FLOOR_OD / 2 - 1.6, -1, P.FLOOR + 3)))   # drip lip
    f = f.cut(slot(P.WELL_ID + 2 * P.WELL_WALL + 2 * P.FIT, WELL_L + 2 * P.WELL_WALL + 2 * P.FIT, -1, P.FLOOR + 1))
    for sx in (-1, 1):
        f = f.cut(big_box(sx * 30 - 6, sx * 30 + 6, CARRIER_Y - 1.6 - 1.2, CARRIER_Y + 1.6 - 1.2, -1, P.FLOOR + 1))
    f = f.cut(cyl(P.TUBE_GROMMET_D / 2, -1, P.FLOOR + 3, *GROMMET_XY))
    f = f.cut(cyl(WIRE_HOLE_D / 2, -1, P.FLOOR + 3, *WIRE_SLOT_XY))
    f = f.cut(cyl(P.M3_INSERT_HOLE / 2, -1, P.FLOOR + 1, GROMMET_XY[0] - 2.0, GROMMET_XY[1] + 12.0))   # nozzle guide screw
    return f


def slot(w, l, z0, z1, yc=None):
    """Stadium (two half-circles joined by straight sides) along Y, w wide and l long overall, centred on the slot."""
    yc = WELL_YC if yc is None else yc
    return cq.Workplane('XY').workplane(offset=z0).center(0, yc).slot2D(l, w, angle=90).extrude(z1 - z0)


def glass_well():
    """Sloped slot the glass slides in. Hangs from its flange on the bay floor into the lower dish.
    Built and printed floor down: z = 0 is the outside bottom, the flange is at the top with a 45 deg skirt."""
    top = (BAY_FLOOR_Z + P.FLOOR + WELL_FLANGE_T) - (GLASS_BASE_Z - P.FLOOR)   # outside bottom -> flange top
    ow, ol = P.WELL_ID + 2 * P.WELL_WALL, WELL_L + 2 * P.WELL_WALL
    fw = WELL_FLANGE_W
    w = slot(ow, ol, 0, top)
    w = w.union(slot(ow + 2 * fw, ol + 2 * fw, top - WELL_FLANGE_T, top))
    skirt = (cq.Workplane('XY').workplane(offset=top - WELL_FLANGE_T - fw).center(0, WELL_YC).slot2D(ol, ow, angle=90)
             .workplane(offset=fw).slot2D(ol + 2 * fw, ow + 2 * fw, angle=90).loft())
    w = w.union(skirt)
    w = w.cut(slot(P.WELL_ID, WELL_L, P.FLOOR, top + 1))
    # sloped floor: flat under the glass at the pour position, then a wedge rising toward the rear (+Y), so a
    # glass left anywhere in the slot slides forward to the pour position
    t = math.tan(math.radians(P.WELL_SLOPE_DEG))
    y0, y1 = WELL_YC - WELL_L / 2, WELL_YC + WELL_L / 2
    ys = P.GLASS_POUR_Y + P.GLASS_D_BASE / 2 + 1.0          # slope starts just behind the glass base
    wedge = (cq.Workplane('YZ').polyline([(ys, P.FLOOR), (y1, P.FLOOR), (y1, P.FLOOR + (y1 - ys) * t),
                                           (ys, P.FLOOR)]).close()
             .extrude(P.WELL_ID / 2 + 1, both=True))
    return w.union(wedge.intersect(slot(P.WELL_ID + 0.2, WELL_L + 0.2, 0, top)))


def glass_path():
    """Everything the glass passes through on the way out: the slide back at rim height, then the lift."""
    r = P.GLASS_D_TOP / 2 + 1.5
    z0 = BAY_FLOOR_Z + P.FLOOR + WELL_FLANGE_T                # flange top
    rim = P.GLASS_TOP_Z_LOCAL + P.GLASS_SLIDE * math.tan(math.radians(P.WELL_SLOPE_DEG)) + 1.0   # rim, pulled back (upper bound)
    slide = slot(2 * r, P.GLASS_SLIDE + 2 * r, z0, rim)
    lift = cq.Workplane('XY').workplane(offset=z0).center(0, GLASS_OUT_Y).circle(r).extrude(P.GLASS_H + 3.0)
    return slide.union(lift)


def nozzle_guide():
    """Quarter-circle bore that turns the tube from vertical (out of the bay floor) to horizontal, pointing at
    the pour position ~17 mm above the rim. The tube sticks out NOZZLE_TIP_OUT past the end.
    Built in the sphere frame relative to the tube's floor exit."""
    r = P.NOZZLE_BEND_R
    bore_d = P.TUBE_OD + 0.6
    body_w = bore_d + 4.0
    h = P.NOZZLE_RISE
    # path in the XZ plane: straight up h, then a quarter arc ending horizontal, pointing +X (at the glass)
    path = cq.Workplane('XZ').moveTo(0, 0).lineTo(0, h).radiusArc((r, h + r), r)
    prof_o = cq.Workplane('XY').rect(body_w, body_w)
    outer = prof_o.sweep(path)
    bore = cq.Workplane('XY').workplane(offset=-1).circle(bore_d / 2).extrude(1).union(
        cq.Workplane('XY').circle(bore_d / 2).sweep(path))
    g = outer.cut(bore)
    foot = big_box(-body_w / 2 - 2, body_w / 2 + 2, -body_w / 2, body_w / 2 + 14, 0, 3.0)
    foot = foot.cut(cyl(bore_d / 2, -1, 4)).cut(cyl(P.M3_CLEAR / 2, -1, 4, -2.0, 12.0))
    return g.union(foot)


def led_carrier():
    c = big_box(-CARRIER_W / 2, CARRIER_W / 2, 0, CARRIER_T, 0, CARRIER_H)
    for i in range(STRIP_ROWS):
        z0 = 6.0 + i * ROW_PITCH
        c = c.cut(big_box(-STRIP_CH_L / 2, STRIP_CH_L / 2, -1, STRIP_CH_D, z0, z0 + STRIP_CH_W))   # channels face -Y (toward the diffuser)
    # tabs into the bay floor slots, wire notch at the bottom-right corner
    for sx in (-1, 1):
        c = c.union(big_box(sx * 30 - 5.5, sx * 30 + 5.5, 0, CARRIER_T, -P.FLOOR - 0.5, 0))
    c = c.cut(big_box(CARRIER_W / 2 - 14, CARRIER_W / 2 + 1, -1, CARRIER_T + 1, 0, 8))
    if P.SOCKET_IN_SPHERE:   # two holes for the socket mounting screws, outside the LED channels
        zc = P.SOCKET_Z_LOCAL - (BAY_FLOOR_Z + P.FLOOR)
        for sx in (-1, 1):
            c = c.cut(cq.Workplane('XZ').workplane(offset=-(CARRIER_T + 1)).center(sx * P.SOCKET_EAR_R, zc)
                      .circle(P.M3_CLEAR / 2).extrude(CARRIER_T + 2))
    # four spacer posts reaching the diffuser (25 mm)
    for (x, z) in ((-40, 20), (40, 20), (-40, 85), (40, 85)):
        c = c.union(big_box(x - 3, x + 3, -(DIFF_Y - CARRIER_Y) + DIFF_T, 0, z - 3, z + 3))
    return c


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
        'led_carrier': led_carrier().rotate((0, 0, 0), (1, 0, 0), -90),   # lie flat: channels up
        'nozzle_guide': nozzle_guide(),
        'glass_envelope': cq.Workplane('XY').add(cq.Solid.makeCone(P.GLASS_D_BASE / 2 + 1.0, P.GLASS_D_TOP / 2, P.GLASS_H)),
        'glass_path_envelope': glass_path(),
        # the hand: a fist (ring face on the socket) and the forearm through the port
        'fist_envelope': cq.Workplane('XZ').ellipse(P.FIST_W / 2, P.FIST_H / 2).extrude(-P.FIST_LEN),
        'forearm_envelope': cq.Workplane('XZ').circle(P.FOREARM_R).extrude(-60.0),
    }
    for k in ('sphere_front', 'sphere_rear', 'led_carrier'):
        bb = out[k].val().BoundingBox()
        out[k] = out[k].translate((0, 0, -bb.zmin))
    return out


def placements():
    Z = Z_ASM
    face_y = CARRIER_Y + P.SOCKET_STANDOFF + 13.2     # = socket.FACE_Y (faceplate surface)
    hand_z = Z + P.SOCKET_Z_LOCAL + 6.0                # fist centre a little above the ring
    gx, gy, gz = _guide_origin()
    return {
        'sphere_front': ((1, 0, 0), 90, (0, 0, Z)),
        'sphere_rear': ((1, 0, 0), -90, (0, 0, Z)),
        'diffuser': ((1, 0, 0), 90, (0, DIFF_Y - DIFF_T, Z)),
        'bay_floor': ((0, 0, 1), 0, (0, 0, Z + BAY_FLOOR_Z)),
        'glass_well': ((0, 0, 1), 0, (0, 0, Z + GLASS_BASE_Z - P.FLOOR)),   # printed the way it hangs
        'led_carrier': ((1, 0, 0), 90, (0, CARRIER_Y, Z + BAY_FLOOR_Z + P.FLOOR)),
        'nozzle_guide': ((0, 0, 1), 0, (gx, gy, Z + gz)),
        'glass_envelope': ((0, 0, 1), 0, (0, P.GLASS_POUR_Y, Z + GLASS_BASE_Z)),
        'glass_path_envelope': ((0, 0, 1), 0, (0, 0, Z)),
        'fist_envelope': ((0, 0, 1), 0, (0, face_y, hand_z)),
        'forearm_envelope': ((0, 0, 1), 0, (0, face_y + P.FIST_LEN - 10.0, hand_z)),
    }
