"""
handle.py - rev C (2026-10-23): the loop handle on ring pivots at the sphere's sides (as on the classic battery).

    handle_pivot_left / _right  ring pivot boss over the sphere's seam: 2 M3 into inserts in the two halves, a bore for
                                the handle's shaft, a cross screw riding in a groove on the shaft
    handle_end_left / _right    shaft + spoke out along X + a 30 mm corner + the first 30 deg of the big arc
    handle_arc_1 .. _3          the rest of the big arc in 40 deg pieces

Shape (in the arch plane, sphere frame): each spoke runs out along X from its pivot to x = LOOP_R - CORNER_R, the corner
turns it up, and the big arc (radius LOOP_R about a point CORNER_R above the sphere centre) goes over the top. The
spokes lie on the pivot axis, so the whole loop turns about its own spokes, like the replica's wire handle: up to
carry, or down flat to either side to lie around the lantern's middle for display. The groove on each shaft spans
+-105 deg, so the cross screw stops the loop at level on both sides and keeps the shaft in its bore.

Joints: every joint between pieces is a LAP_L long half-thickness lap split on the arch mid-plane with 2 x M3 (nut in a
hex pocket on the +Y face). Each piece keeps the same half at both its laps; it prints flat with the cut side up.
Section HANDLE_SECTION_W (in the plane) x HANDLE_SECTION_T (along Y), 2 mm rounded edges.
"""
import math
import cadquery as cq
import params as P
from parts import sphere as S

W, T = P.HANDLE_SECTION_W, P.HANDLE_SECTION_T        # 14 x 10
EDGE_R = 2.0
LOOP_R, CORNER_R = P.HANDLE_LOOP_R, P.HANDLE_CORNER_R
ZC = CORNER_R                                        # big arc centre height in the sphere frame
X_CORNER = LOOP_R - CORNER_R                         # spoke ends / corner starts
# pivot
PIVOT_R, PIVOT_X1 = P.PIVOT_D / 2, S.R_OUT + P.PIVOT_T   # outer face at x = 128
SHAFT_R = P.HANDLE_SHAFT_D / 2                       # 6
BORE_R = SHAFT_R + P.FIT
SHAFT_X0 = S.R_OUT + 1.5                             # shaft tip, 1.5 mm off the sphere
SPOKE_X0 = PIVOT_X1 + 0.5                            # the flat-bar section starts just outside the pivot face
GROOVE_X, GROOVE_W, GROOVE_D = (SHAFT_X0 + PIVOT_X1) / 2, P.M3_CLEAR + 0.4, 1.5
GROOVE_HALF = 105.0                                  # deg either side of the top
CROSS_Z = SHAFT_R - GROOVE_D + P.M3_CLEAR / 2 - 0.2  # cross screw axis height over the shaft axis (rides the groove floor)
RING_GROOVES = (10.0, 20.0)                          # decorative rings on the pivot face (the mount screws sit between)
NUT_AF, NUT_POCKET_DEPTH = 5.6, 2.6
# laps
LAP_L = 24.0
TIP_GAP = P.FIT
JOINTS = (30.0, 70.0, 110.0, 150.0)                  # big-arc angles (deg, 0 = right, 90 = top)
PIECES = [('handle_end_right', -90.0, 30.0, 'rear'), ('handle_arc_1', 30.0, 70.0, 'front'),
          ('handle_arc_2', 70.0, 110.0, 'rear'), ('handle_arc_3', 110.0, 150.0, 'front'),
          ('handle_end_left', 150.0, 270.0, 'rear')]
BIG = 800.0


def _section(origin, normal, xdir):
    """Rounded W x T section: W along xdir (in the arch plane), T along Y."""
    pl = cq.Plane(origin=origin, xDir=xdir, normal=normal)
    return cq.Workplane(pl).sketch().rect(W, T).vertices().fillet(EDGE_R).finalize()


def centreline():
    """Right half's path from the spoke start (at the pivot face) to the top, then mirrored: one wire, XZ plane."""
    a = cq.Workplane('XZ').moveTo(-SPOKE_X0, 0).lineTo(-X_CORNER, 0)
    a = a.threePointArc((-X_CORNER - CORNER_R * math.sin(math.radians(45)), CORNER_R * (1 - math.cos(math.radians(45)))),
                        (-LOOP_R, ZC))
    a = a.threePointArc((0, ZC + LOOP_R), (LOOP_R, ZC))
    a = a.threePointArc((X_CORNER + CORNER_R * math.sin(math.radians(45)), CORNER_R * (1 - math.cos(math.radians(45)))),
                        (X_CORNER, 0))
    return a.lineTo(SPOKE_X0, 0)


def loop_solid():
    """The whole flat bar (no shafts), sphere frame, arch plane y = 0."""
    path = centreline()
    sec = _section((-SPOKE_X0, 0, 0), (1, 0, 0), (0, 0, 1))
    return sec.sweep(path, transition='round')


def shaft(sign):
    """Round shaft (flats at y = +-T/2 so it prints flat) from the spoke into the pivot, with its stop groove."""
    x0, x1 = sorted((sign * SHAFT_X0, sign * (SPOKE_X0 + 3.0)))
    s = cq.Workplane('YZ').workplane(offset=x0).circle(SHAFT_R).extrude(x1 - x0)
    s = s.intersect(cq.Workplane('XY').box(BIG, T, BIG))
    g0, g1 = sorted((sign * (GROOVE_X - GROOVE_W / 2), sign * (GROOVE_X + GROOVE_W / 2)))
    ring = cq.Workplane('YZ').workplane(offset=g0).circle(SHAFT_R + 1).circle(SHAFT_R - GROOVE_D).extrude(g1 - g0)
    pts = [(0, 0)] + [(0 + 2 * SHAFT_R * math.sin(math.radians(t)), 2 * SHAFT_R * math.cos(math.radians(t)))
                      for t in range(-int(GROOVE_HALF), int(GROOVE_HALF) + 1, 15)]
    sector = cq.Workplane('YZ').workplane(offset=g0 - 1).polyline(pts).close().extrude(g1 - g0 + 2)
    return s.cut(ring.intersect(sector))


def _wedge(a0, a1):
    """Prism (along Y) of all points whose angle about the big arc's centre lies in a0..a1 (deg)."""
    n = max(2, int((a1 - a0) / 10) + 1)
    pts = [(0, ZC)] + [(BIG * math.cos(math.radians(a0 + (a1 - a0) * i / n)), ZC + BIG * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
                       for i in range(n + 1)]
    return cq.Workplane('XZ').polyline(pts).close().extrude(BIG / 2, both=True)


def _half(side):
    y0 = -BIG if side == 'front' else 0.0
    return cq.Workplane('XY').box(BIG * 4, BIG, BIG * 4).translate((0, y0 + BIG / 2, 0))


def _other(side):
    return 'front' if side == 'rear' else 'rear'


def _lap_deg():
    return math.degrees(LAP_L / 2 / LOOP_R), math.degrees(TIP_GAP / LOOP_R)


def screw_points(phi):
    d, _ = _lap_deg()
    return [(LOOP_R * math.cos(math.radians(phi + s * d / 2)), ZC + LOOP_R * math.sin(math.radians(phi + s * d / 2)))
            for s in (-1, 1)]


def _y_hole(x, z, d):
    return cq.Workplane(cq.Plane(origin=(x, -BIG / 2, z), normal=(0, 1, 0), xDir=(1, 0, 0))).circle(d / 2).extrude(BIG)


def _nut_pocket(x, z):
    plane = cq.Plane(origin=(x, T / 2 + 0.01, z), normal=(0, -1, 0), xDir=(1, 0, 0))
    return cq.Workplane(plane).polygon(6, NUT_AF / math.cos(math.radians(30))).extrude(NUT_POCKET_DEPTH + 0.01)


def pieces():
    """All loop pieces in the sphere frame (upright)."""
    full = loop_solid()
    d, g = _lap_deg()
    out = {}
    for name, a0, a1, keeps in PIECES:
        lo = a0 - d + g if a0 in JOINTS else a0
        hi = a1 + d - g if a1 in JOINTS else a1
        p = full.intersect(_wedge(lo, hi))
        for phi in (a0, a1):
            if phi in JOINTS:
                p = p.cut(_half(_other(keeps)).intersect(_wedge(phi - d - 1, phi + d + 1)))
                for x, z in screw_points(phi):
                    p = p.cut(_y_hole(x, z, P.M3_CLEAR))
                    if keeps == 'rear':
                        p = p.cut(_nut_pocket(x, z))
        if name == 'handle_end_right':
            p = p.union(shaft(+1))
        if name == 'handle_end_left':
            p = p.union(shaft(-1))
        out[name] = p
    return out


def pivot(sign):
    """Ring pivot boss on the sphere's side at x = sign * R (sphere frame), its inner face following the sphere."""
    x0, x1 = sorted((sign * (S.R_OUT - 8.0), sign * PIVOT_X1))
    b = cq.Workplane('YZ').workplane(offset=x0).circle(PIVOT_R).circle(BORE_R).extrude(x1 - x0)
    b = b.edges(cq.selectors.NearestToPointSelector((sign * PIVOT_X1, 0, PIVOT_R))).chamfer(1.5)
    # (the sphere primitive's seam runs through +X: turn it out of the way or the boolean fails on the right pivot)
    b = b.cut(cq.Workplane('XY').sphere(S.R_OUT).rotate((0, 0, 0), (0, 0, 1), 45))
    face = sign * PIVOT_X1
    for r in RING_GROOVES:                           # concentric rings on the face
        b = b.cut(cq.Workplane('YZ').workplane(offset=face - sign * 0.8).circle(r + 0.6).circle(r - 0.6).extrude(sign * 2))
    for y, z in S.PIVOT_SCREWS:                      # into the sphere's inserts, heads counterbored
        b = b.cut(cq.Workplane('YZ').workplane(offset=x0 - 1).center(y, z).circle(P.M3_CLEAR / 2).extrude(x1 - x0 + 2))
        b = b.cut(cq.Workplane('YZ').workplane(offset=face + sign * 0.01).center(y, z)
                  .circle(P.M3_HEAD_D / 2 + 0.3).extrude(-sign * 3.0))
    # cross screw along Y over the shaft, riding in its groove: nut pocket at -Y, head counterbore at +Y
    b = b.cut(cq.Workplane('XZ').workplane(offset=-BIG / 2).center(sign * GROOVE_X, CROSS_Z).circle(P.M3_CLEAR / 2).extrude(BIG))
    b = b.cut(cq.Workplane('XZ').workplane(offset=-(PIVOT_R + 1)).center(sign * GROOVE_X, CROSS_Z)
              .circle(P.M3_HEAD_D / 2 + 0.3).extrude(4.0 + 1))
    b = b.cut(cq.Workplane(cq.Plane(origin=(sign * GROOVE_X, -PIVOT_R - 1, CROSS_Z), normal=(0, 1, 0), xDir=(1, 0, 0)))
              .polygon(6, NUT_AF / math.cos(math.radians(30))).extrude(NUT_POCKET_DEPTH + 1 + 1.5))
    return b


# ------------------------------------------------------------------ frames
def _print_rotation(keeps):
    """The lap's cut side faces up: rear-keeping pieces print front (-Y) up."""
    return ((1, 0, 0), 90.0) if keeps == 'rear' else ((1, 0, 0), -90.0)


def _frames():
    parts, places = {}, {}
    zc = P.Z_SPHERE_CENTER
    keeps = {n: k for n, _, _, k in PIECES}
    solids = pieces()
    solids['handle_pivot_right'] = pivot(+1)
    solids['handle_pivot_left'] = pivot(-1)
    keeps['handle_pivot_right'] = keeps['handle_pivot_left'] = None
    for name, s in solids.items():
        if keeps[name] is None:                      # pivots print outer face down
            sign = 1 if name.endswith('right') else -1
            axis, angle = (0, 1, 0), -90.0 * sign
        else:
            axis, angle = _print_rotation(keeps[name])
        rot = s.rotate((0, 0, 0), axis, -angle)
        bb = rot.val().BoundingBox()
        shift = (-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin)
        parts[name] = rot.translate(shift)
        r_shift = cq.Workplane('XY').add(cq.Vertex.makeVertex(*shift)).rotate((0, 0, 0), axis, angle).val().toTuple()
        places[name] = (axis, angle, (-r_shift[0], -r_shift[1], zc - r_shift[2]))
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


def swing(placed, angle):
    """A loop piece already placed in the assembly, turned about the pivot axis (X through the sphere centre)."""
    return placed.rotate((0, 0, P.Z_SPHERE_CENTER), (1, 0, P.Z_SPHERE_CENTER), angle)
