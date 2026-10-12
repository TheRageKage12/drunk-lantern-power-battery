"""
handle: the flat carrying arch over the lantern (Hedo3D "handle.stl" look at 1.8x), in HANDLE_PIECES = 4 pieces.

    handle_leg_left / handle_leg_right : straight bars rising from the sphere's handle bosses at +/-X
    handle_arc_left / handle_arc_right : quarter arcs (radius ARC_R) meeting at the top centre

The arch lies in a plane parallel to the assembly XZ plane at Y = HANDLE_PLANE_Y (just behind the sphere
split plane, where the contract puts the bosses on the rear half).  Section HANDLE_SECTION_W (in-plane,
radial) x HANDLE_SECTION_T (out of plane, along Y) with 2 mm rounded edges, like the original flat bar.

Joints (3): leg->arc at the tangent points and arc->arc at the top centre.  Every joint is a LAP_L long
half-thickness lap split on the arch mid-plane (Y = HANDLE_PLANE_Y) with 2 x M3_CLEAR through screws;
the nut sits in a hex pocket on the rear (+Y) face, the screw head on the front face.  Each piece keeps the
SAME half (front or rear) at all of its laps, so printed flat with the removed side up, the laps are steps
cut from the top of the print and nothing overhangs.

Print frame: arch plane on the bed (T = 10 up), min z = 0, XY bbox centred on the origin.
See NOTES-handle.md for the boss pocket requirement handed to the sphere module.
"""
import math

import cadquery as cq

import params as P

# ------------------------------------------------------------------ section and arch geometry
W = P.HANDLE_SECTION_W                                   # 14: in-plane (radial) width of the bar
T = P.HANDLE_SECTION_T                                   # 10: out-of-plane thickness (along assembly Y)
EDGE_R = 2.0                                             # rounded section edges (original bar is fully rounded)
LEG_X = P.SPHERE_D / 2 + P.HANDLE_INNER_GAP + T / 2      # 131: centreline X of each leg (sphere module matches this)
ARC_R = LEG_X                                            # semicircular top arc, centred on the lantern axis
Z_ARC_CENTER = P.Z_HANDLE_TOP - ARC_R                    # 335: arc centre = leg top / tangent point
HANDLE_PLANE_Y = P.WALL + T / 2                          # 7.4: arch mid-plane, bosses on the rear half (y > 0)
HANDLE_INNER_GAP_ACTUAL = LEG_X - W / 2 - P.SPHERE_D / 2  # 34: true clearance leg inner face <-> sphere surface

# ------------------------------------------------------------------ boss pocket in the sphere (requirement, see NOTES)
BOSS_POCKET_DEPTH = 12.0                                 # the leg plugs this far down into the boss
BOSS_POCKET_W = W + 2 * P.FIT                            # 14.6: pocket size along X (radial)
BOSS_POCKET_T = T + 2 * P.FIT                            # 10.6: pocket size along Y
Z_BOSS_POCKET_TOP = P.Z_SPHERE_CENTER                    # 250.5: pocket mouth is at the sphere equator
Z_LEG_BOTTOM = Z_BOSS_POCKET_TOP - BOSS_POCKET_DEPTH     # 238.5
LEG_SCREW_Z = Z_BOSS_POCKET_TOP - BOSS_POCKET_DEPTH / 2  # 244.5: one M3 across the plug, axis along X
LEG_SCREW_CB_D = P.M3_HEAD_D + 0.6                       # head counterbore on the leg's outer (+/-X) face
LEG_SCREW_CB_DEPTH = 2.0
LEG_TIP_CHAMFER = 0.8                                    # lead-in on the plug end

# ------------------------------------------------------------------ lap joints
LAP_L = 24.0                                             # overlap length of every lap joint
LAP_T = T / 2                                            # half-thickness laps, split on the arch mid-plane
LAP_SCREW_PITCH = LAP_L / 2                              # 2 screws per joint, 6 mm from each end of the lap
NUT_AF = 5.6                                             # hex pocket across flats (M3 nut 5.5)
NUT_POCKET_DEPTH = 2.6                                   # M3 nut is 2.4 thick; leaves 2.4 mm under the pocket
TIP_GAP = P.FIT                                          # each lap tip is shortened so it does not jam on the shoulder
LAP_OVERSHOOT_DEG = 12.0                                 # arcs are revolved past the top centre, then trimmed

# screw positions in the arch plane (x, z), assembly frame
LEG_LAP_Z = (Z_ARC_CENTER - LAP_L / 2 - LAP_SCREW_PITCH / 2, Z_ARC_CENTER - LAP_L / 2 + LAP_SCREW_PITCH / 2)
TOP_LAP_X = (-LAP_SCREW_PITCH / 2, LAP_SCREW_PITCH / 2)
TOP_LAP_Z = tuple(Z_ARC_CENTER + math.sqrt(ARC_R ** 2 - x ** 2) for x in TOP_LAP_X)   # arc centreline height
JOINT_SCREWS = {   # joint -> [(x, z), ...]; every hole axis is along Y
    'left': [(-LEG_X, z) for z in LEG_LAP_Z],
    'top': list(zip(TOP_LAP_X, TOP_LAP_Z)),
    'right': [(LEG_X, z) for z in LEG_LAP_Z],
}
# which half each piece KEEPS at its laps ('front' = y < plane, 'rear' = y > plane); every joint pairs one of each
KEEPS = {'handle_leg_left': 'rear', 'handle_arc_left': 'front', 'handle_arc_right': 'rear', 'handle_leg_right': 'front'}
BIG = 1000.0


# ------------------------------------------------------------------ helpers (all in the arch-local frame: y = 0 mid-plane)
def section(origin):
    """Rounded W x T section on an XY workplane at `origin` (W along X, T along Y)."""
    return cq.Workplane('XY', origin=origin).sketch().rect(W, T).vertices().fillet(EDGE_R).finalize()


def straight_bar(x, z0, z1):
    """Straight piece of bar, centreline at x, from z0 up to z1."""
    return section((x, 0, z0)).extrude(z1 - z0)


def quarter_arc_left(angle_deg):
    """Arc of bar from the left tangent point (-ARC_R, Z_ARC_CENTER) sweeping over the top by angle_deg."""
    # workplane origin is the tangent point; the revolve axis (local coords) is the Y line through x = 0 global
    arc = section((-ARC_R, 0, Z_ARC_CENTER)).revolve(angle_deg, (ARC_R, 0, 0), (ARC_R, 1, 0))
    if arc.val().BoundingBox().zmax < Z_ARC_CENTER + 1:        # revolve went downward: flip the axis direction
        arc = section((-ARC_R, 0, Z_ARC_CENTER)).revolve(angle_deg, (ARC_R, 0, 0), (ARC_R, -1, 0))
    return arc


def half_box(side, x0, x1, z0, z1):
    """Box covering one thickness half ('front' y<0 or 'rear' y>0) over the given x / z range (to CUT a lap)."""
    y0, y1 = (-BIG, 0.0) if side == 'front' else (0.0, BIG)
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def x_halfspace(x_min=None, x_max=None):
    """Box used to trim a piece to x >= x_min and/or x <= x_max."""
    lo = -BIG if x_min is None else x_min
    hi = BIG if x_max is None else x_max
    return cq.Workplane('XY').box(hi - lo, 2 * BIG, 2 * BIG, centered=False).translate((lo, -BIG, -BIG))


def y_hole(x, z, d):
    """Through hole along Y at (x, z)."""
    return cq.Workplane(cq.Plane(origin=(x, -BIG / 2, z), normal=(0, 1, 0), xDir=(1, 0, 0))).circle(d / 2).extrude(BIG)


def nut_pocket(x, z):
    """Hex pocket for an M3 nut, opening on the rear (+Y) face of the bar."""
    d_circ = NUT_AF / math.cos(math.radians(30))
    plane = cq.Plane(origin=(x, T / 2 + 0.01, z), normal=(0, -1, 0), xDir=(1, 0, 0))
    return cq.Workplane(plane).polygon(6, d_circ).extrude(NUT_POCKET_DEPTH + 0.01)


def other(side):
    return 'front' if side == 'rear' else 'rear'


def add_joint_screws(body, joint, keeps):
    """2 x M3 clearance holes through the joint; the piece that keeps the rear half also gets the nut pockets."""
    for (x, z) in JOINT_SCREWS[joint]:
        body = body.cut(y_hole(x, z, P.M3_CLEAR))
        if keeps == 'rear':
            body = body.cut(nut_pocket(x, z))
    return body


# ------------------------------------------------------------------ pieces (arch-local frame)
def leg(sign, keeps):
    """Straight leg at x = sign * LEG_X: plug end at the bottom, lap at the top (joint with the arc)."""
    x = sign * LEG_X
    body = straight_bar(x, Z_LEG_BOTTOM, Z_ARC_CENTER - TIP_GAP)
    try:   # lead-in chamfer on the plug end (cosmetic / insertion aid; skipped if OCC refuses)
        body = body.faces('<Z').chamfer(LEG_TIP_CHAMFER)
    except Exception:
        pass
    # lap: remove the other half over the top LAP_L of the leg
    body = body.cut(half_box(other(keeps), x - W, x + W, Z_ARC_CENTER - LAP_L, Z_ARC_CENTER + 1))
    body = add_joint_screws(body, 'left' if sign < 0 else 'right', keeps)
    # boss screw: M3 across the plug along X, head counterbored on the outer face
    outer = x + sign * W / 2
    hole = cq.Workplane(cq.Plane(origin=(x - sign * W, 0, LEG_SCREW_Z), normal=(sign, 0, 0), xDir=(0, 1, 0)))
    body = body.cut(hole.circle(P.M3_CLEAR / 2).extrude(2 * W))
    cb = cq.Workplane(cq.Plane(origin=(outer + sign * 0.01, 0, LEG_SCREW_Z), normal=(-sign, 0, 0), xDir=(0, 1, 0)))
    body = body.cut(cb.circle(LEG_SCREW_CB_D / 2).extrude(LEG_SCREW_CB_DEPTH + 0.01))
    return body


def arc(sign, keeps):
    """Quarter arc on the sign side (+1 right, -1 left): straight LAP_L tangent run at the bottom (joint with
    the leg) then a quarter circle to the top centre with a LAP_L/2 overshoot (joint with the other arc)."""
    # build the LEFT arc, mirror afterwards for the right one
    straight = straight_bar(-ARC_R, Z_ARC_CENTER - LAP_L + TIP_GAP, Z_ARC_CENTER)
    body = straight.union(quarter_arc_left(90.0 + LAP_OVERSHOOT_DEG))
    body = body.cut(x_halfspace(x_min=LAP_L / 2 - TIP_GAP))         # trim the overshoot at the top lap tip
    # laps: bottom (with the leg) and top (with the other arc), both remove the same half
    rm = other(keeps)
    body = body.cut(half_box(rm, -ARC_R - W, -ARC_R + W, Z_ARC_CENTER - LAP_L - 1, Z_ARC_CENTER))
    body = body.cut(half_box(rm, -LAP_L / 2, LAP_L / 2, Z_ARC_CENTER + ARC_R - W, Z_ARC_CENTER + ARC_R + W))
    if sign > 0:
        body = body.mirror('YZ')
    body = add_joint_screws(body, 'left' if sign < 0 else 'right', keeps)
    body = add_joint_screws(body, 'top', keeps)
    return body


# ------------------------------------------------------------------ assembly / print frames
def assembly_solids():
    """All four pieces in the ASSEMBLY frame (arch plane moved to Y = HANDLE_PLANE_Y)."""
    local = {
        'handle_leg_left': leg(-1, KEEPS['handle_leg_left']),
        'handle_leg_right': leg(+1, KEEPS['handle_leg_right']),
        'handle_arc_left': arc(-1, KEEPS['handle_arc_left']),
        'handle_arc_right': arc(+1, KEEPS['handle_arc_right']),
    }
    return {n: wp.translate((0, HANDLE_PLANE_Y, 0)) for n, wp in local.items()}


def print_rotation(name):
    """(axis, angle) of the print->assembly rotation.  Pieces that keep the rear half have their laps cut
    from the front, so the FRONT (-Y) must face up in print: print = R_x(-90)(assembly), placement +90."""
    return ((1, 0, 0), 90.0) if KEEPS[name] == 'rear' else ((1, 0, 0), -90.0)


def _frames():
    """Compute print-oriented solids and their placements from the assembly-frame solids."""
    parts, places = {}, {}
    for name, asm in assembly_solids().items():
        axis, angle = print_rotation(name)
        rot = asm.rotate((0, 0, 0), axis, -angle)                  # inverse rotation -> arch plane on the bed
        bb = rot.val().BoundingBox()
        shift = (-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin)   # centre XY, sit on z = 0
        parts[name] = rot.translate(shift)
        # placement: assembly = R(print) + t  with  print = R^-1(assembly) + shift  ->  t = -R(shift)
        r_shift = cq.Workplane('XY').add(cq.Vertex.makeVertex(*shift)).rotate((0, 0, 0), axis, angle).val().toTuple()
        places[name] = (axis, angle, tuple(-c for c in r_shift))
    return parts, places


_CACHE = None


def build():
    global _CACHE
    if _CACHE is None:
        _CACHE = _frames()
    return _CACHE[0]


def placements():
    build()
    return _CACHE[1]
