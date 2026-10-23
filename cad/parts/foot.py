"""
foot.py - rev C (2026-10-23): the short flared neck between the drum and the sphere (replaces dish_lower).

One revolved part, printed spigot down in its assembly orientation:
    spigot   into the drum's top band, 3 radial M3 from the band into inserts in the spigot (as the old lower dish)
    flare    45 deg from the drum's 190 mm out to the 136.8 mm neck (the steepest overhang printed without support)
    neck     25 mm straight, up to the sphere's bottom flat
    riser    a locating ring up through the sphere's collar to BAY_FLOOR_Z: the bay floor sits on its top, 36 mm above
             the flat, exactly where it sat on the old lower dish; 3 radial M3 from the sphere's collar into it

The glass well hangs 13 mm down into the neck; the tube and the pump's two wires pass down the middle to the cartridge.
Assembly frame: Z up from the table, origin on the lantern axis.
"""
import math
import cadquery as cq
import params as P
import common as C
from parts import sphere as S

R_RIM = P.D_MAX / 2                                  # 95
DRUM_BORE_R = P.BASE_BODY_D / 2 - P.WALL             # 89.6: the drum's one straight bore (base.R_IN)
SPIGOT_R = DRUM_BORE_R - P.FIT                       # 89.3
SPIGOT_RI = SPIGOT_R - P.WALL                        # 86.9
Z_SPIGOT0 = P.BASE_H - P.JOINT_SPIGOT_H              # 72
Z_RIM = P.BASE_H                                     # 80: bears on the drum's top band
Z_NECK0 = Z_RIM + P.FLARE_H                          # 106.6
Z_FLAT = P.Z_FOOT_FLAT                               # 131.6: the sphere's bottom flat
R_NECK = S.FLAT_D / 2                                # 68.4
RISER_R = S.OPENING_ID / 2 - P.FIT                   # 65.7: in the sphere's collar
RISER_RI = RISER_R - P.WALL                          # 63.3 (the bay floor, OD 131, rests on 63.3 .. 65.5)
Z_RISER1 = P.Z_SPHERE_CENTER + S.BAY_FLOOR_Z         # 167.8
FLARE_WALL_R = P.WALL / math.cos(math.radians(P.FLARE_ANGLE))   # 3.4 radial = 2.4 normal
NECK_RI = R_NECK - P.WALL                            # 66.0
BEARING_T = 2.5                                      # ring joining the neck to the riser, under the sphere's flat

Z_DRUM_SCREWS = P.BASE_H - 5.0                       # 75: MATING base.BASE_JOINT_Z
Z_SPHERE_SCREWS = P.Z_SPHERE_CENTER + S.Z_LOWER_SCREWS   # 134.6
JOINT_ANGLES = C.joint_angles()                      # 90, 210, 330
BOSS_W, BOSS_DEPTH = 10.0, P.M3_INSERT_DEPTH + 1.5   # radial insert bosses (8 deep)


def _inner_cone(z):
    return R_RIM - (z - Z_RIM) - FLARE_WALL_R


def profile():
    # 45 deg V where the spigot's bore meets the flare's inner cone, so nothing overhangs flat
    d = (_inner_cone(Z_RIM) - SPIGOT_RI) / 2
    z_cone_end = Z_RIM + (R_RIM - FLARE_WALL_R - NECK_RI)
    return [
        (SPIGOT_RI, Z_SPIGOT0), (SPIGOT_R, Z_SPIGOT0), (SPIGOT_R, Z_RIM), (R_RIM, Z_RIM),
        (R_NECK, Z_NECK0), (R_NECK, Z_FLAT), (RISER_R, Z_FLAT), (RISER_R, Z_RISER1), (RISER_RI, Z_RISER1),
        (RISER_RI, Z_FLAT - BEARING_T), (NECK_RI, Z_FLAT - BEARING_T),     # 2.7 mm overhang, printed
        (NECK_RI, z_cone_end), (SPIGOT_RI + d, Z_RIM + d), (SPIGOT_RI, Z_RIM),
    ]


def face_r(r):
    """A boss's flat outer face sits this far out, so its corners, not its middle, are on r."""
    return math.sqrt(r * r - (BOSS_W / 2) ** 2)


def _boss(r_face, z0, z1, angle, corbel_r=None):
    """Insert boss on the inside of a ring: r_face - BOSS_DEPTH .. r_face, z0 .. z1, BOSS_W wide. With corbel_r, a 45 deg
    wedge under it out to that radius (printed spigot down, its underside would otherwise be a flat overhang)."""
    r_face = face_r(r_face)
    r0 = r_face - BOSS_DEPTH
    if corbel_r is None:
        pts = [(r0, z0), (r_face, z0), (r_face, z1), (r0, z1)]
    else:
        pts = [(r0, z0), (corbel_r, z0 - (corbel_r - r0)), (corbel_r, Z_FLAT - BEARING_T), (r_face, Z_FLAT - BEARING_T),
               (r_face, z1), (r0, z1)]
    blk = cq.Workplane('XZ').polyline(pts).close().extrude(BOSS_W / 2, both=True)
    return blk.rotate((0, 0, 0), (0, 0, 1), angle)


def build_foot():
    f = cq.Workplane('XZ').polyline(profile()).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    for a in JOINT_ANGLES:
        f = f.union(_boss(SPIGOT_R, Z_SPIGOT0, Z_RIM + 4.0, a))
        f = f.union(_boss(RISER_R, Z_FLAT - BEARING_T, Z_SPHERE_SCREWS + 6.0, a, corbel_r=NECK_RI + 0.3))
    for a in JOINT_ANGLES:
        f = f.cut(C.radial_hole(Z_DRUM_SCREWS, a, SPIGOT_R + 0.5, SPIGOT_R - face_r(SPIGOT_R) + P.M3_INSERT_DEPTH + 0.5, P.M3_INSERT_HOLE))
        f = f.cut(C.radial_hole(Z_SPHERE_SCREWS, a, RISER_R + 0.5, RISER_R - face_r(RISER_R) + P.M3_INSERT_DEPTH + 0.5, P.M3_INSERT_HOLE))
    # notch in the riser's top for the guide boss glued under the bay floor
    gz = Z_RISER1 + S.GUIDE_INSERT_BOSS_BOTTOM - P.FIT
    f = f.cut(cq.Workplane('XY').workplane(offset=gz).center(*S.GUIDE_SCREW)
              .circle(S.GUIDE_INSERT_BOSS_R + P.FIT).extrude(Z_RISER1 - gz + 1))
    return f


def build():
    return {'foot': build_foot().translate((0, 0, -Z_SPIGOT0))}   # spigot on the bed


def placements():
    return {'foot': ((0, 0, 1), 0, (0, 0, Z_SPIGOT0))}
