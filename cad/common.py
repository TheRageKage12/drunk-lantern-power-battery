"""Shared CadQuery helpers for every part module."""
import math
import cadquery as cq
import params as P


def insert_boss(wp_solid, center, normal_axis='Z', boss_d=9.0, boss_h=None, hole_d=P.M3_INSERT_HOLE,
                hole_depth=P.M3_INSERT_DEPTH):
    """Return (boss_solid, hole_solid) cylinders for an M3 heat-set insert at `center`.
    Caller unions the boss and cuts the hole. normal_axis: 'Z' (boss grows +Z from center) or a
    cq.Vector direction. boss_h defaults to hole_depth + 1.5."""
    boss_h = boss_h or hole_depth + 1.5
    if normal_axis == 'Z':
        d = cq.Vector(0, 0, 1)
    else:
        d = cq.Vector(*normal_axis).normalized()
    c = cq.Vector(*center)
    boss = cq.Workplane(cq.Plane(origin=c, normal=d)).circle(boss_d / 2).extrude(boss_h)
    hole = cq.Workplane(cq.Plane(origin=c + d * (boss_h - hole_depth), normal=d)).circle(hole_d / 2).extrude(hole_depth + 0.01)
    return boss, hole


def magnet_pocket(center, normal=(0, 0, 1), d=P.MAGNET_POCKET_D, t=P.MAGNET_POCKET_T):
    """Cylinder to CUT for a 6x2 magnet pocket; pocket opens toward +normal from `center`."""
    return cq.Workplane(cq.Plane(origin=cq.Vector(*center), normal=cq.Vector(*normal))).circle(d / 2).extrude(t)


def radial_hole(z, angle_deg, r_outer, length, d):
    """Cylinder to CUT: a radial hole at height z, pointing inward from radius r_outer."""
    a = math.radians(angle_deg)
    origin = cq.Vector(r_outer * math.cos(a), r_outer * math.sin(a), z)
    normal = cq.Vector(-math.cos(a), -math.sin(a), 0)
    return cq.Workplane(cq.Plane(origin=origin, normal=normal)).circle(d / 2).extrude(length)


def joint_angles(n=P.JOINT_SCREWS, first_deg=90.0):
    """Angles of the radial joint screws; first one at +Y (rear)."""
    return [first_deg + i * 360.0 / n for i in range(n)]


def rounded_rect_cutter(w, h, r, depth, origin=(0, 0, 0), normal=(0, 0, 1), xdir=None):
    plane = cq.Plane(origin=cq.Vector(*origin), normal=cq.Vector(*normal), xDir=cq.Vector(*xdir) if xdir else None)
    return cq.Workplane(plane).rect(w, h).extrude(depth).edges('|' + 'Z' if normal == (0, 0, 1) else None).fillet(r) if False else \
        cq.Workplane(plane).sketch().rect(w, h).vertices().fillet(r).finalize().extrude(depth)


def cone_shell(d_bottom, d_top, h, wall):
    """Hollow truncated cone (open both ends), axis Z, bottom at z=0."""
    outer = cq.Solid.makeCone(d_bottom / 2, d_top / 2, h)
    inner = cq.Solid.makeCone(d_bottom / 2 - wall, d_top / 2 - wall, h)
    return cq.Workplane('XY').add(outer).cut(cq.Workplane('XY').add(inner))


def sphere_flat_d(d, cut):
    """Diameter of the flat face when a sphere of diameter d is cut at distance `cut` from its centre."""
    r = d / 2
    return 2 * math.sqrt(r * r - cut * cut)


def bbox(solid):
    bb = solid.val().BoundingBox() if isinstance(solid, cq.Workplane) else solid.BoundingBox()
    return (bb.xlen, bb.ylen, bb.zlen)


def rotate_about(wp, axis, angle_deg):
    """Rotate a Workplane solid about an axis through the origin."""
    if angle_deg == 0:
        return wp
    return wp.rotate((0, 0, 0), axis, angle_deg)
