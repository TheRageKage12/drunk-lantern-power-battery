"""
dish_lower / dish_upper: the two conical reflector dishes (Hedo3D "reflector.stl" look at 1.8x).

Both dishes are one revolved profile (mouth rim, cone, neck floor/flange, locating ring or plug)
plus a few insert bosses and holes.  Every mating number is derived from params and exposed as a
module-level constant so the base / sphere / socket modules can match it.  See NOTES-dishes.md.

Assembly frame: Z up, origin at the centre of the base bottom.
Print frames:
  dish_lower : mouth DOWN (spigot ring + 3 bosses on the bed), narrow floor + locating ring at the top.
  dish_upper : floor DOWN (locating plug on the bed), mouth at the top.
Both print orientations coincide with the assembly orientation, so placements() is a pure Z shift.

Original reflector.stl (measured with trimesh, see NOTES): outer cone ~25 deg from vertical, mouth
rim ~1.5-3 mm straight with a rounded lip, narrow end = flat annulus with a centre hole.
"""
import math

import cadquery as cq

import params as P
import common as C

# ------------------------------------------------------------------ joint with the base (dish_lower)
# The base drum (parts/base.py) has ONE straight bore from its floor to its top: R_IN = BASE_BODY_D/2 - WALL,
# i.e. the top band (at D_MAX) is a 5.4 mm thick wall, not a WALL-thick band.  The spigot must match the
# base's real bore, so take it from the base module when it is importable and fall back to the same formula.
try:
    from parts.base import BASE_TOP_INNER_D         # 169.2 = BASE_BODY_D - 2*WALL  (base.py: 2 * R_IN)
except Exception:                                   # running dishes.py stand-alone
    BASE_TOP_INNER_D = P.BASE_BODY_D - 2 * P.WALL
SPIGOT_OD = BASE_TOP_INNER_D - 2 * P.FIT            # spigot ring OD that slides into the base -> 168.6
SPIGOT_ID = SPIGOT_OD - 2 * P.WALL                  # 163.8
SPIGOT_H = P.JOINT_SPIGOT_H                         # 8
Z_BASE_JOINT_SCREWS = P.BASE_H - 5.0                # radial M3 screws through the base top band (assembly Z) -> 110
JOINT_BOSS_ANGLES = C.joint_angles()                # [90, 210, 330] deg, first at +Y (rear)
JOINT_BOSS_W = 10.0                                 # tangential width of each radial insert boss
JOINT_BOSS_T = 8.0                                  # Z thickness of each radial insert boss ("8 mm thick")
JOINT_BOSS_DEPTH = P.M3_INSERT_DEPTH + 1.5          # radial depth of the boss from its outer face -> 8.0
# The mouth rim (r_mouth - CONE_WALL_RADIAL .. r_mouth) overhangs the spigot OD by RIM_GROOVE_W (defined with
# the cone geometry below); the underside between the two is a 45 deg roof (printable) and only the rim wall
# footprint (RIM_BEARING_W wide) is a flat bearing ring on the base's top band.

# ------------------------------------------------------------------ joint with the sphere (both dishes)
SPHERE_FLAT_D = C.sphere_flat_d(P.SPHERE_D, P.SPHERE_CUT)   # 136.8 - flat face dia of the truncated sphere
SPHERE_OPENING_ID = SPHERE_FLAT_D - 2 * P.WALL               # 132.0 - the sphere module MUST bore its flat
#                                                            openings to this ID over LOCATING_RING_H_* depth
LOCATING_RING_OD = SPHERE_OPENING_ID - 2 * P.FIT             # 131.4 - ring/plug that goes inside the opening
LOCATING_RING_ID = LOCATING_RING_OD - 2 * P.WALL             # 126.6 - lower dish ring ID (bay floor seat)
LOCATING_RING_H_LOWER = 6.0                                  # lower dish: thin ring on top of the floor
# upper dish: a solid plug so the part prints flat on its floor; thick enough for the socket inserts
LOCATING_RING_H_UPPER = max(6.0, P.SOCKET_PLATE_T + P.M3_INSERT_DEPTH + 1.5 - P.FLOOR)   # 9.0
DISH_FLANGE_D = SPHERE_FLAT_D                                # neck floor plate OD = sphere flat (bearing face)
Z_SPHERE_LOWER_SCREWS = P.Z_LOWER_DISH_TOP + 2.0             # sphere radial M3 holes, bottom joint (assembly Z) -> 179
Z_SPHERE_UPPER_SCREWS = P.Z_SPHERE_TOP - 2.0                 # sphere radial M3 holes, top joint (assembly Z)
BAY_FLOOR_SEAT_Z = P.Z_LOWER_DISH_TOP + LOCATING_RING_H_LOWER  # the bay_floor disc (OD 131) rests on the ring top

# ------------------------------------------------------------------ cone geometry (both dishes)
CONE_H = P.DISH_H - P.DISH_RIM_H - P.FLOOR          # 69: straight cone between the rim and the floor plate
CONE_DR = (P.DISH_MOUTH_D - P.DISH_NECK_D) / 2.0    # 35: radial change over CONE_H
CONE_HALF_ANGLE_DEG = math.degrees(math.atan2(CONE_DR, CONE_H))   # 26.9 deg from vertical
CONE_K = CONE_DR / CONE_H                           # dr/dz of the cone surface
CONE_WALL_RADIAL = P.WALL / math.cos(math.radians(CONE_HALF_ANGLE_DEG))   # radial offset for a true WALL thickness
RIM_BEARING_W = CONE_WALL_RADIAL                    # flat ring under the rim wall that bears on the base band (2.69)
RIM_GROOVE_W = (P.DISH_MOUTH_D / 2 - RIM_BEARING_W) - SPIGOT_OD / 2   # rim inner wall to spigot OD -> 3.0
RIM_GROOVE_ANGLE_DEG = 45.0                         # the groove roof rises at this overhang angle (printable)
COLLAR_ANGLE_DEG = 45.0                             # 45 deg flare under the lower dish flange (printability)
FLOOR_SUPPORT_ANGLE_DEG = 50.0                      # overhang angle (from vertical) of the support cone under the lower floor
MOUTH_CHAMFER = 1.5                                 # cosmetic lip on the upper mouth (original has a rounded lip)

# ------------------------------------------------------------------ socket module seat (dish_upper)
SOCKET_COUNTERBORE_D = P.SOCKET_PLATE_D + 0.6       # 100.6
SOCKET_COUNTERBORE_DEPTH = P.SOCKET_PLATE_T         # 3: faceplate top ends up flush with the floor top
SOCKET_BOLT_ANGLES = [45.0, 135.0, 225.0, 315.0]    # 4 x M3 inserts on SOCKET_BOLT_CIRCLE, clear of the +Y wire slot
Z_UPPER_FLOOR_TOP = P.Z_SPHERE_TOP + P.FLOOR        # assembly Z of the upper floor top face = faceplate top
Z_SOCKET_PLATE_SEAT = Z_UPPER_FLOOR_TOP - SOCKET_COUNTERBORE_DEPTH   # counterbore floor the faceplate sits on
UPPER_WIRE_SLOT_W, UPPER_WIRE_SLOT_L = 10.0, 8.0    # wire notch in the +Y edge of the floor hole, 10 wide, 8 radial
UPPER_FLOOR_HOLE_D = P.DISH_NECK_HOLE_D             # 80 (SOCKET_HOUSING_OD 76 passes it from above, rev 3)
assert P.SOCKET_HOUSING_OD + 2 * P.FIT <= UPPER_FLOOR_HOLE_D, 'socket housing cannot pass the dish floor hole'

# ------------------------------------------------------------------ print frame z levels
# dish_lower (mouth down): spigot bottom on the bed
L_Z_SPIGOT0 = 0.0
L_Z_RIM0 = SPIGOT_H                                 # rim bottom / bearing ring (= base top in assembly)
L_Z_RIM1 = L_Z_RIM0 + P.DISH_RIM_H                  # rim top = cone start
L_Z_GROOVE1 = L_Z_RIM0 + RIM_GROOVE_W / math.tan(math.radians(RIM_GROOVE_ANGLE_DEG))   # groove roof apex -> 11.0
L_Z_SHOULDER1 = L_Z_RIM1                            # shoulder plate (spigot ID .. rim) fills the rim height
assert L_Z_SHOULDER1 - L_Z_GROOVE1 >= P.WALL - 1e-6, 'rim shoulder too thin above the spigot groove'
L_Z_FLOOR0 = L_Z_RIM1 + CONE_H                      # floor plate underside = cone end
L_Z_FLOOR1 = L_Z_FLOOR0 + P.FLOOR                   # floor top (= Z_LOWER_DISH_TOP in assembly)
L_Z_RING1 = L_Z_FLOOR1 + LOCATING_RING_H_LOWER      # locating ring top
LOWER_PRINT_TO_ASSEMBLY_DZ = P.BASE_H - SPIGOT_H    # rim bottom lands on Z = BASE_H

# dish_upper (floor down): plug bottom on the bed
U_Z_PLUG0 = 0.0
U_Z_FLANGE0 = LOCATING_RING_H_UPPER                 # flange underside (= Z_SPHERE_TOP in assembly)
U_Z_FLOOR1 = U_Z_FLANGE0 + P.FLOOR                  # floor top
U_Z_RIM0 = U_Z_FLOOR1 + CONE_H                      # cone end = rim bottom
U_Z_RIM1 = U_Z_RIM0 + P.DISH_RIM_H                  # mouth top (= Z_UPPER_DISH_TOP in assembly)
UPPER_PRINT_TO_ASSEMBLY_DZ = P.Z_SPHERE_TOP - LOCATING_RING_H_UPPER


# ================================================================== helpers
def _revolve_profile(points_rz):
    """Revolve a closed (r, z) polygon about the Z axis -> solid of revolution."""
    wp = cq.Workplane('XZ').polyline([(r, z) for r, z in points_rz]).close()
    return wp.revolve(360.0, (0, 0, 0), (0, 1, 0))


def _radial_block(r_inner, r_outer, width, z0, z1, angle_deg):
    """Box between radii r_inner..r_outer, `width` wide tangentially, z0..z1, rotated to angle_deg.
    The flat outer face is pulled in so its CORNERS sit on the cylinder r_outer (a flat face at
    r_outer would have corners at sqrt(r_outer^2 + (width/2)^2), i.e. proud of a mating OD by ~0.15)."""
    r_face = math.sqrt(r_outer ** 2 - (width / 2) ** 2)
    blk = (cq.Workplane('XY')
           .box(r_face - r_inner, width, z1 - z0, centered=(False, True, False))
           .translate((r_inner, 0, z0)))
    return blk.rotate((0, 0, 0), (0, 0, 1), angle_deg)


def _radial_pilot(z, angle_deg, r_face, depth=P.M3_INSERT_DEPTH, d=P.M3_INSERT_HOLE):
    """Insert pilot hole pointing OUTWARD: starts just outside the face at r_face, goes `depth` inward."""
    eps = 0.5
    return C.radial_hole(z, angle_deg, r_face + eps, depth + eps, d)


def _line_hit_cone(r0, z0, slope_rz, cone_r_at, cone_z_a, cone_z_b):
    """Intersect the line r = r0 + slope_rz*(z - z0) with the cone surface r = cone_r_at(z)
    (both linear in z). Returns (r, z)."""
    # r0 + s*(z - z0) = ra + k*(z - za)   where cone_r_at(z) = ra + k*(z - za)
    ra, rb = cone_r_at(cone_z_a), cone_r_at(cone_z_b)
    k = (rb - ra) / (cone_z_b - cone_z_a)
    z = (ra - k * cone_z_a - r0 + slope_rz * z0) / (slope_rz - k)
    return cone_r_at(z), z


# ================================================================== dish_lower
def _lower_profile():
    """Closed (r, z) profile of dish_lower in the print frame (mouth down)."""
    r_mouth = P.DISH_MOUTH_D / 2
    r_neck = P.DISH_NECK_D / 2
    r_hole = P.DISH_LOWER_HOLE_D / 2    # rev 7: wide enough for the glass slot
    r_flange = DISH_FLANGE_D / 2
    r_ring_o, r_ring_i = LOCATING_RING_OD / 2, LOCATING_RING_ID / 2
    r_sp_o, r_sp_i = SPIGOT_OD / 2, SPIGOT_ID / 2
    r_rim_i = r_mouth - RIM_BEARING_W   # = r_mouth - CONE_WALL_RADIAL: rim wall = cone wall

    # cone surfaces, print frame: wide at L_Z_RIM1 (bottom), narrow at L_Z_FLOOR0 (top)
    def outer(z):
        return r_mouth - CONE_K * (z - L_Z_RIM1)

    def inner(z):
        return outer(z) - CONE_WALL_RADIAL

    # collar: 45 deg flare from the flange edge down to the outer cone (so the flange prints without supports)
    tan_c = math.tan(math.radians(COLLAR_ANGLE_DEG))
    r_c, z_c = _line_hit_cone(r_flange, L_Z_FLOOR0, +1.0 / tan_c, outer, L_Z_RIM1, L_Z_FLOOR0)
    # support cone under the floor: from the hole edge outward/down at FLOOR_SUPPORT_ANGLE_DEG to the inner cone
    tan_s = math.tan(math.radians(FLOOR_SUPPORT_ANGLE_DEG))
    r_s, z_s = _line_hit_cone(r_hole, L_Z_FLOOR0, -tan_s, inner, L_Z_RIM1, L_Z_FLOOR0)

    # rim underside: 45 deg groove roof from the spigot OD out to the rim inner wall, then the flat bearing ring
    groove = [(r_rim_i, L_Z_GROOVE1), (r_rim_i, L_Z_RIM0)] if RIM_GROOVE_W > 0.3 else []

    return [
        (r_hole, L_Z_FLOOR0),            # hole edge, floor underside
        (r_s, z_s),                      # support cone meets the inner cone
        (inner(L_Z_RIM1), L_Z_RIM1),     # inner cone bottom = rim inner top = shoulder top (outer end)
        (r_sp_i, L_Z_SHOULDER1),         # shoulder top, inward to the spigot ID
        (r_sp_i, L_Z_SPIGOT0),           # spigot inner, down to the bed
        (r_sp_o, L_Z_SPIGOT0),           # spigot bottom face
        (r_sp_o, L_Z_RIM0),              # spigot outer up to the rim bottom level
        *groove,                         # groove roof (45 deg) up to the rim inner wall, back down to the bearing ring
        (r_mouth, L_Z_RIM0),             # rim bottom: flat bearing ring RIM_BEARING_W wide on the base top band
        (r_mouth, L_Z_RIM1),             # straight rim
        (r_c, z_c),                      # outer cone up to the collar
        (r_flange, L_Z_FLOOR0),          # collar flare out to the flange edge
        (r_flange, L_Z_FLOOR1),          # flange edge
        (r_ring_o, L_Z_FLOOR1),          # floor top out to the ring
        (r_ring_o, L_Z_RING1),           # locating ring outer
        (r_ring_i, L_Z_RING1),           # ring top
        (r_ring_i, L_Z_FLOOR1),          # ring inner
        (r_hole, L_Z_FLOOR1),            # floor top in to the hole
    ]


def build_dish_lower():
    body = _revolve_profile(_lower_profile())
    r_sp_o = SPIGOT_OD / 2
    r_ring_o = LOCATING_RING_OD / 2
    z_base_screw = Z_BASE_JOINT_SCREWS - LOWER_PRINT_TO_ASSEMBLY_DZ          # print z of the base joint screws
    z_sphere_screw = Z_SPHERE_LOWER_SCREWS - LOWER_PRINT_TO_ASSEMBLY_DZ      # print z of the sphere joint screws

    for a in JOINT_BOSS_ANGLES:
        # spigot insert boss: inside the spigot ring, standing on the bed, fused up into the rim shoulder
        # (the shoulder is solid from the spigot ID to the rim between L_Z_GROOVE1 and L_Z_SHOULDER1)
        body = body.union(_radial_block(r_sp_o - JOINT_BOSS_DEPTH, r_sp_o, JOINT_BOSS_W,
                                        L_Z_SPIGOT0, L_Z_SHOULDER1, a))
        # locating ring insert boss: inside the ring, fused down into the floor plate
        body = body.union(_radial_block(r_ring_o - JOINT_BOSS_DEPTH, r_ring_o, JOINT_BOSS_W,
                                        L_Z_FLOOR0, L_Z_RING1, a))
    for a in JOINT_BOSS_ANGLES:
        body = body.cut(_radial_pilot(z_base_screw, a, r_sp_o))        # pilot from the spigot OD inward
        body = body.cut(_radial_pilot(z_sphere_screw, a, r_ring_o))    # pilot from the ring OD inward
    return body


# ================================================================== dish_upper
def _upper_profile():
    """Closed (r, z) profile of dish_upper in the print frame (floor down, mouth up)."""
    r_mouth = P.DISH_MOUTH_D / 2
    r_neck = P.DISH_NECK_D / 2
    r_hole = UPPER_FLOOR_HOLE_D / 2
    r_flange = DISH_FLANGE_D / 2
    r_plug = LOCATING_RING_OD / 2
    r_rim_i = r_mouth - CONE_WALL_RADIAL
    ch = MOUTH_CHAMFER

    def outer(z):
        return r_neck + CONE_K * (z - U_Z_FLOOR1)

    def inner(z):
        return outer(z) - CONE_WALL_RADIAL

    tan_c = math.tan(math.radians(COLLAR_ANGLE_DEG))
    r_c, z_c = _line_hit_cone(r_flange, U_Z_FLOOR1, -1.0 / tan_c, outer, U_Z_FLOOR1, U_Z_RIM0)

    return [
        (r_hole, U_Z_PLUG0),             # plug bottom, hole edge
        (r_plug, U_Z_PLUG0),             # plug bottom face (on the bed)
        (r_plug, U_Z_FLANGE0),           # plug outer (goes inside the sphere top opening)
        (r_flange, U_Z_FLANGE0),         # flange underside (sits on the sphere flat)
        (r_flange, U_Z_FLOOR1),          # flange edge
        (r_c, z_c),                      # collar flare up to the outer cone
        (r_mouth, U_Z_RIM0),             # outer cone up to the rim
        (r_mouth, U_Z_RIM1 - ch),        # straight rim
        (r_mouth - ch, U_Z_RIM1),        # outer lip chamfer
        (r_rim_i + ch, U_Z_RIM1),        # mouth top
        (r_rim_i, U_Z_RIM1 - ch),        # inner lip chamfer
        (r_rim_i, U_Z_RIM0),             # rim inner
        (inner(U_Z_FLOOR1), U_Z_FLOOR1), # inner cone down to the floor top
        (r_hole, U_Z_FLOOR1),            # floor top in to the hole
    ]


def build_dish_upper():
    body = _revolve_profile(_upper_profile())
    r_plug = LOCATING_RING_OD / 2
    z_sphere_screw = Z_SPHERE_UPPER_SCREWS - UPPER_PRINT_TO_ASSEMBLY_DZ     # print z of the sphere top screws
    z_cb_floor = U_Z_FLOOR1 - SOCKET_COUNTERBORE_DEPTH                     # counterbore floor (faceplate seat)

    # socket faceplate counterbore in the floor top
    cb = (cq.Workplane('XY').workplane(offset=z_cb_floor)
          .circle(SOCKET_COUNTERBORE_D / 2).extrude(SOCKET_COUNTERBORE_DEPTH + 1.0))
    body = body.cut(cb)
    # 4 vertical insert pockets for the socket screws, from the counterbore floor down into the plug
    for a in SOCKET_BOLT_ANGLES:
        x = P.SOCKET_BOLT_CIRCLE / 2 * math.cos(math.radians(a))
        y = P.SOCKET_BOLT_CIRCLE / 2 * math.sin(math.radians(a))
        pocket = (cq.Workplane('XY').workplane(offset=z_cb_floor - P.M3_INSERT_DEPTH)
                  .center(x, y).circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH + 0.5))
        body = body.cut(pocket)
    # 3 radial pilots in the plug's outer face (the solid plug is the "boss"), matching the sphere's top holes
    for a in JOINT_BOSS_ANGLES:
        body = body.cut(_radial_pilot(z_sphere_screw, a, r_plug))
    # wire notch: +Y edge of the floor hole, UPPER_WIRE_SLOT_W wide, UPPER_WIRE_SLOT_L radial, full floor depth
    r_hole = UPPER_FLOOR_HOLE_D / 2
    slot = (cq.Workplane('XY')
            .box(UPPER_WIRE_SLOT_W, UPPER_WIRE_SLOT_L + 1.0, U_Z_FLOOR1 + 2.0, centered=(True, False, False))
            .translate((0, r_hole - 1.0, -1.0)))
    body = body.cut(slot)
    # pilots in the plug's underside for the strip-curtain clamp (sphere.curtain_clamp), behind the hand port
    for a in P.CURTAIN_SCREW_ANGLES:
        x, y = P.CURTAIN_R * math.cos(math.radians(a)), P.CURTAIN_R * math.sin(math.radians(a))
        body = body.cut(cq.Workplane('XY').workplane(offset=U_Z_PLUG0 - 0.5).center(x, y)
                        .circle(P.M3_INSERT_HOLE / 2).extrude(P.M3_INSERT_DEPTH + 0.5))
    return body


# ================================================================== module API
def build_top_diffuser():
    """Frosted disc over the upper dish floor hole: light from the LED ring inside the hole comes out of the top.
    Sits in the old socket counterbore on 4 countersunk screws. 1.2 mm thick over the hole; print it flat face
    down in white or natural PETG."""
    d = SOCKET_COUNTERBORE_D - 2 * P.FIT
    t = SOCKET_COUNTERBORE_DEPTH
    disc = cq.Workplane('XY').circle(d / 2).extrude(t)
    disc = disc.cut(cq.Workplane('XY').workplane(offset=t - 1.8).circle(UPPER_FLOOR_HOLE_D / 2 - 1.0).extrude(2))   # thin centre
    for a in SOCKET_BOLT_ANGLES:
        x = P.SOCKET_BOLT_CIRCLE / 2 * math.cos(math.radians(a))
        y = P.SOCKET_BOLT_CIRCLE / 2 * math.sin(math.radians(a))
        disc = disc.cut(cq.Workplane('XY').workplane(offset=-1).center(x, y).circle(P.M3_CLEAR / 2).extrude(t + 2))
        disc = disc.cut(cq.Workplane('XY').add(cq.Solid.makeCone(P.M3_HEAD_D / 2 + 0.3, P.M3_CLEAR / 2, 1.8,
                                                                  pnt=cq.Vector(x, y, 0))))   # countersink, bed side
    return disc


def build():
    out = {
        'dish_lower': build_dish_lower(),
        'dish_upper': build_dish_upper(),
    }
    if P.SOCKET_IN_SPHERE:
        out['top_diffuser'] = build_top_diffuser()
    return out


def placements():
    """Print frame -> assembly frame. Both dishes print in their assembly orientation: pure Z shifts."""
    return {
        'dish_lower': ((0, 0, 1), 0.0, (0.0, 0.0, LOWER_PRINT_TO_ASSEMBLY_DZ)),
        'dish_upper': ((0, 0, 1), 0.0, (0.0, 0.0, UPPER_PRINT_TO_ASSEMBLY_DZ)),
        # printed flat (countersunk) face down: flip so that face is on top in the dish
        'top_diffuser': ((1, 0, 0), 180.0, (0.0, 0.0, Z_SOCKET_PLATE_SEAT + SOCKET_COUNTERBORE_DEPTH)),
    }


if __name__ == '__main__':
    for n, s in build().items():
        print(n, s.val().isValid(), C.bbox(s))
