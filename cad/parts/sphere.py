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

# hatch (rear): rounded rectangle, bottom-hinged door
HATCH_W, HATCH_H, HATCH_R = P.HATCH_W, P.HATCH_H, 14.0    # 110 x 96
HATCH_Z0 = -48.0                            # bottom edge (collar top is at -49.5)
HATCH_ZC = HATCH_Z0 + HATCH_H / 2           # 0
LIP_W, LIP_T = 5.0, 2.4                     # door lip inside the wall
HINGE_PIN_D, HINGE_PIN_L = 3.0, 4.0
MAG_Z = HATCH_Z0 + HATCH_H - 12.0           # magnet pairs near the top corners
MAG_X = HATCH_W / 2 - 12.0

# bay floor, tray, carrier
BAY_FLOOR_OD = 131.0
PLATFORM_W, PLATFORM_L, PLATFORM_H = 72.0, 92.0, 4.5     # raised so the tray clears the hatch sill
PLATFORM_Y0 = -36.0
RAIL_H, RAIL_T = 3.0, 2.0
TRAY_W, TRAY_L, TRAY_T = 60.0, 70.0, 2.0
TRAY_Y0 = -30.0                             # tray rear end at rest (its ring centred on the axis)
TRAY_TRAVEL = P.GLASS_TRAY_TRAVEL           # 45
GLASS_RING_ID = P.GLASS_D_BASE + 4.0        # 44
GLASS_RING_H, GLASS_RING_WALL = 8.0, 2.0
TRAY_TOP_Z = BAY_FLOOR_Z + P.FLOOR + PLATFORM_H + TRAY_T   # -44.0: glass stands here
CARRIER_Y = -35.0
CARRIER_W, CARRIER_H, CARRIER_T = 110.0, 104.0, 2.4
STRIP_ROWS, STRIP_LEDS, ROW_PITCH = 9, 6, 12.0
STRIP_CH_W, STRIP_CH_D, STRIP_CH_L = 10.5, 1.5, 102.0
GROMMET_XY = (-48.0, 20.0)
WIRE_SLOT_XY = (48.0, 20.0)

# handle bosses (match parts.handle): pocket 14.6 x 10.6 x 12 deep, open up, mouth at the equator
LEG_X = P.SPHERE_D / 2 + P.HANDLE_INNER_GAP + P.HANDLE_SECTION_T / 2   # 105
HANDLE_PLANE_Y = P.WALL + P.HANDLE_SECTION_T / 2                        # 7.4
BOSS_POCKET_W = P.HANDLE_SECTION_W + 2 * P.FIT    # 14.6 (X)
BOSS_POCKET_T = P.HANDLE_SECTION_T + 2 * P.FIT    # 10.6 (Y)
BOSS_POCKET_DEPTH = 12.0
BOSS_SCREW_Z = -BOSS_POCKET_DEPTH / 2       # -6 (assembly 244.5)

# nozzle clip
NOZZLE_MOUNT = (-45.0, 66.6, 35.0)          # on the inner wall, rear-left, above the glass
GLASS_AIM = (12.0, 5.0, -44.0 + P.GLASS_H)  # inside wall of the glass at rim height

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


def nozzle_clip_and_boss():
    """Clip holding the tube at ~45 deg aimed at the glass; boss on the rear half inner wall."""
    mx, my, mz = NOZZLE_MOUNT
    d = cq.Vector(GLASS_AIM[0] - mx, GLASS_AIM[1] - my, GLASS_AIM[2] - mz).normalized()
    # boss: a 12 mm cylinder along the local inward normal, 8 mm proud of the wall, with an M3 insert
    n = cq.Vector(-mx, -my, -mz).normalized()
    boss = cq.Workplane(cq.Plane(origin=cq.Vector(mx, my, mz) - n * 3.0, normal=n)).circle(6.0).extrude(11.0)
    boss_hole = cq.Workplane(cq.Plane(origin=cq.Vector(mx, my, mz) + n * 8.0, normal=-n)).circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH)
    # clip (print frame: flat on the bed): block 30 x 12 x 10 with a C-channel for the tube and a screw hole
    clip = cq.Workplane('XY').box(30, 12, 10, centered=(True, True, False))
    clip = clip.cut(cq.Workplane('XY').workplane(offset=5.5).rect(32, P.TUBE_OD + 0.2).extrude(10))      # slot down to the bore
    clip = clip.cut(cq.Workplane('YZ').workplane(offset=-16).center(0, 5.5).circle(P.TUBE_OD / 2 + 0.1).extrude(32))
    clip = clip.cut(cq.Workplane('XY').workplane(offset=-1).center(0, 0).circle(P.M3_CLEAR / 2).extrude(12))
    return boss, boss_hole, clip, d


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

    # ---- rear: flange, hatch, hinge holes, magnet pockets, handle bosses, nozzle boss
    rear = rear.union(flange_solid())
    rear = rear.cut(rounded_rect_cutter_y(HATCH_W, HATCH_H, HATCH_R, 40, 100, HATCH_ZC))
    for sx in (-1, 1):
        # hinge pin holes beside the bottom corners (axis along X), in the wall
        x_hole = sx * (HATCH_W / 2 + 2.6)
        y_hole = math.sqrt(max(R_OUT ** 2 - x_hole ** 2 - (HATCH_Z0 + 4) ** 2, 1))
        rear = rear.cut(cq.Workplane('YZ').workplane(offset=x_hole - sx * 4).center(y_hole - 1.2, HATCH_Z0 + 4).circle(HINGE_PIN_D / 2 + 0.15).extrude(sx * 8))
        # magnet pockets in the inner wall at the top corners (open inward)
        xm = sx * MAG_X
        ym = math.sqrt(R_IN ** 2 - xm ** 2 - MAG_Z ** 2)
        nvec = cq.Vector(xm, ym, MAG_Z).normalized()
        # pocket cut INTO the wall from its inner surface (opens inward, toward the door lip); 1.6 deep so the
        # magnet stands 0.4 proud and touches its partner in the lip
        rear = rear.cut(C.magnet_pocket((xm, ym, MAG_Z), normal=(nvec.x, nvec.y, nvec.z), t=1.6))
        blk, bc = handle_boss(sx)
        rear = rear.union(blk)
        for c in bc:
            rear = rear.cut(c)
    boss, boss_hole, clip, d = nozzle_clip_and_boss()
    rear = rear.union(boss).cut(boss_hole)
    return front, rear, clip, d


def hatch_door():
    """Curved door: shell segment covering the opening + inner lip, hinge pins, magnet pockets, pull tab."""
    outer = cq.Workplane('XY').sphere(R_OUT).cut(cq.Workplane('XY').sphere(R_IN))
    door = outer.intersect(rounded_rect_cutter_y(HATCH_W - 2 * P.FIT, HATCH_H - 2 * P.FIT, HATCH_R, 40, 100, HATCH_ZC))
    lip = cq.Workplane('XY').sphere(R_IN - 0.1).cut(cq.Workplane('XY').sphere(R_IN - LIP_T))
    lip_outline = rounded_rect_cutter_y(HATCH_W + 2 * LIP_W, HATCH_H + LIP_W, HATCH_R + LIP_W, 40, 100, HATCH_ZC + LIP_W / 2)
    lip = lip.intersect(lip_outline)
    door = door.union(lip)
    for sx in (-1, 1):
        x_pin = sx * (HATCH_W / 2 - P.FIT)
        y_pin = math.sqrt(R_OUT ** 2 - x_pin ** 2 - (HATCH_Z0 + 4) ** 2) - 1.2
        pin = cq.Workplane('YZ').workplane(offset=x_pin - sx * 0.5).center(y_pin, HATCH_Z0 + 4).circle(HINGE_PIN_D / 2).extrude(sx * (HINGE_PIN_L + 0.5))
        door = door.union(pin)
        xm = sx * MAG_X
        ym = math.sqrt((R_IN - 0.1) ** 2 - xm ** 2 - MAG_Z ** 2)   # lip outer surface (touches the wall)
        nvec = cq.Vector(xm, ym, MAG_Z).normalized()
        door = door.cut(C.magnet_pocket((xm, ym, MAG_Z), normal=(-nvec.x, -nvec.y, -nvec.z), t=1.6))   # opens outward
    # pull tab at the top edge, outside
    zt = HATCH_Z0 + HATCH_H - 6
    yt = math.sqrt(R_OUT ** 2 - zt ** 2)
    tab = big_box(-10, 10, yt - 1, yt + 3, zt - 3, zt + 3)
    return door.union(tab)


def diffuser():
    return cq.Workplane('XY').circle(DIFF_D / 2).extrude(DIFF_T)


def bay_floor():
    f = cyl(BAY_FLOOR_OD / 2, 0, P.FLOOR)
    f = f.union(cyl(BAY_FLOOR_OD / 2, 0, P.FLOOR + 2.0).cut(cyl(BAY_FLOOR_OD / 2 - 1.6, -1, P.FLOOR + 3)))   # drip lip
    plat = big_box(-PLATFORM_W / 2, PLATFORM_W / 2, PLATFORM_Y0, PLATFORM_Y0 + PLATFORM_L, P.FLOOR, P.FLOOR + PLATFORM_H)
    f = f.union(plat)
    for sx in (-1, 1):
        x = sx * (TRAY_W / 2 + P.FIT + RAIL_T / 2)
        f = f.union(big_box(x - RAIL_T / 2, x + RAIL_T / 2, PLATFORM_Y0, PLATFORM_Y0 + PLATFORM_L, P.FLOOR + PLATFORM_H, P.FLOOR + PLATFORM_H + RAIL_H))
    # rear stop so the tray cannot be pushed off the back; front end nub
    f = f.union(big_box(-TRAY_W / 2, TRAY_W / 2, PLATFORM_Y0, PLATFORM_Y0 + 2, P.FLOOR + PLATFORM_H, P.FLOOR + PLATFORM_H + RAIL_H))
    # carrier tab slots, grommet hole, wire slot
    for sx in (-1, 1):
        f = f.cut(big_box(sx * 30 - 6, sx * 30 + 6, CARRIER_Y - 1.6, CARRIER_Y + 1.6, -1, P.FLOOR + 1))
    f = f.cut(cyl(P.TUBE_GROMMET_D / 2, -1, P.FLOOR + 3, *GROMMET_XY))
    f = f.cut(big_box(WIRE_SLOT_XY[0] - 7, WIRE_SLOT_XY[0] + 7, WIRE_SLOT_XY[1] - 4, WIRE_SLOT_XY[1] + 4, -1, P.FLOOR + 3))
    return f


def glass_tray():
    t = big_box(-TRAY_W / 2, TRAY_W / 2, 0, TRAY_L, 0, TRAY_T)
    ring = cyl(GLASS_RING_ID / 2 + GLASS_RING_WALL, TRAY_T, TRAY_T + GLASS_RING_H, 0, -TRAY_Y0).cut(cyl(GLASS_RING_ID / 2, TRAY_T - 1, TRAY_T + GLASS_RING_H + 1, 0, -TRAY_Y0))
    t = t.union(ring)
    tab = big_box(-9, 9, TRAY_L, TRAY_L + 12, 0, TRAY_T + 2)
    t = t.union(tab).cut(cyl(2.5, -1, TRAY_T + 3, 0, TRAY_L + 7))
    # stop nub under the tray's rear edge (rides behind the rail stop... simple: nub at the rear, under)
    return t


def led_carrier():
    c = big_box(-CARRIER_W / 2, CARRIER_W / 2, 0, CARRIER_T, 0, CARRIER_H)
    for i in range(STRIP_ROWS):
        z0 = 6.0 + i * ROW_PITCH
        c = c.cut(big_box(-STRIP_CH_L / 2, STRIP_CH_L / 2, -1, STRIP_CH_D, z0, z0 + STRIP_CH_W))   # channels face -Y (toward the diffuser)
    # tabs into the bay floor slots, wire notch at the bottom-right corner
    for sx in (-1, 1):
        c = c.union(big_box(sx * 30 - 5.5, sx * 30 + 5.5, 0, CARRIER_T, -P.FLOOR - 0.5, 0))
    c = c.cut(big_box(CARRIER_W / 2 - 14, CARRIER_W / 2 + 1, -1, CARRIER_T + 1, 0, 8))
    # four spacer posts reaching the diffuser (25 mm)
    for (x, z) in ((-40, 20), (40, 20), (-40, 85), (40, 85)):
        c = c.union(big_box(x - 3, x + 3, -(DIFF_Y - CARRIER_Y) + DIFF_T, 0, z - 3, z + 3))
    return c


def build():
    front, rear, clip, d = build_halves()
    out = {
        'sphere_front': front.rotate((0, 0, 0), (1, 0, 0), -90),   # (x,y,z)->(x,z,-y): dome up, split face on the bed
        'sphere_rear': rear.rotate((0, 0, 0), (1, 0, 0), 90),      # (x,y,z)->(x,-z,y)
        'sphere_hatch': hatch_door().rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 0, 0)),
        'diffuser': diffuser(),
        'bay_floor': bay_floor(),
        'glass_tray': glass_tray(),
        'led_carrier': led_carrier().rotate((0, 0, 0), (1, 0, 0), -90),   # lie flat: channels up
        'nozzle_clip': clip,
        'glass_envelope': cq.Workplane('XY').add(cq.Solid.makeCone(P.GLASS_D_BASE / 2 + 1.0, P.GLASS_D_TOP / 2, P.GLASS_H)),   # tapered like a shot glass
    }
    # normalise min z to 0 for the rotated parts
    for k in ('sphere_front', 'sphere_rear', 'sphere_hatch', 'led_carrier'):
        bb = out[k].val().BoundingBox()
        out[k] = out[k].translate((0, 0, -bb.zmin))
    return out


def placements():
    Z = Z_ASM
    hatch_bb = hatch_door().rotate((0, 0, 0), (1, 0, 0), 90).val().BoundingBox()
    carrier_bb = led_carrier().rotate((0, 0, 0), (1, 0, 0), -90).val().BoundingBox()
    front_bb = build_halves()[0].rotate((0, 0, 0), (1, 0, 0), -90).val().BoundingBox()
    rear_bb = build_halves()[1].rotate((0, 0, 0), (1, 0, 0), 90).val().BoundingBox()
    return {
        'sphere_front': ((1, 0, 0), 90, (0, 0, Z)),       # inverse of -90 is +90 ... after the zmin shift (zmin = 0 since split face at y=0)
        'sphere_rear': ((1, 0, 0), -90, (0, 0, Z)),
        'sphere_hatch': ((1, 0, 0), -90, (0, 0, Z)),
        'diffuser': ((1, 0, 0), 90, (0, DIFF_Y - DIFF_T, Z)),   # disc in XZ plane at y = DIFF_Y-1..DIFF_Y (after +90: z->-y... see note)
        'bay_floor': ((0, 0, 1), 0, (0, 0, Z + BAY_FLOOR_Z)),
        'glass_tray': ((0, 0, 1), 0, (0, TRAY_Y0, Z + BAY_FLOOR_Z + P.FLOOR + PLATFORM_H)),
        'led_carrier': ((1, 0, 0), 90, (0, CARRIER_Y, Z + BAY_FLOOR_Z + P.FLOOR)),
        'nozzle_clip': ((0, 0, 1), 0, (NOZZLE_MOUNT[0] + 8, NOZZLE_MOUNT[1] - 10, Z + NOZZLE_MOUNT[2] - 5)),
        'glass_envelope': ((0, 0, 1), 0, (0, 0, Z + TRAY_TOP_Z)),
    }
