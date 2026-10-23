"""
handle.py - rev C (2026-10-23): the loop handle on ring pivots at the sphere's sides (as on the classic battery).

    handle_pivot_left / _right  ring pivot boss over the sphere's seam: 2 M3 into inserts in the two halves, a bore for
                                the axle, and an arc groove in its face that stops the handle level on both sides
    handle_end_left / _right    hub + spoke out along X + a 30 mm corner + the first 45 deg of the big arc
    handle_arc_1, _2            the rest of the big arc, 45 deg each

Shape (in the arch plane, sphere frame): each spoke runs out along X from its pivot to x = LOOP_R - CORNER_R, the corner
turns it up, and the big arc (radius LOOP_R about a point CORNER_R above the sphere centre) goes over the top. The
spokes lie on the pivot axis, so the whole loop turns about them, like the replica's wire handle: up to carry, or down
flat to either side to lie around the lantern's middle for display.

Axles (P.HANDLE_AXLE): by default a 12 mm shaft printed on each spoke's end turns in the pivot's bore; the 'pin' option
glues a steel 1/4 x 2 in dowel pin in instead (stronger: the printed shaft is the first thing to break if the handle is
yanked). A tab on the spoke's hub rides in the pivot's arc groove and stops the loop just past level either way.
Nothing holds the axles in their bores axially: the two spokes face each other, so the assembled loop cannot pull off
both at once. Fit the two end pieces into the pivots first, then join the arcs.

Joints (2026-10-23): the loop is split at 45, 90 and 135 deg, away from the corners where the load is highest. Each
joint is a LAP_L long half-thickness lap split on the arch mid-plane with 3 x M3 (nut in a hex pocket on the +Y face),
glued with epoxy. Each piece keeps the same half at both its laps; it prints flat with the cut side up, at 100% infill.
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
PIN_R, PIN_L = P.HANDLE_PIN_D / 2, P.HANDLE_PIN_L
PRINTED = P.HANDLE_AXLE == 'printed'
SHAFT_R = P.HANDLE_SHAFT_D / 2
BORE_R = SHAFT_R + P.FIT if PRINTED else PIN_R + 0.2  # the axle turns in the pivot
PIN_HOLE_R = PIN_R + 0.1                             # glued into the spoke
PIN_X0 = S.R_OUT + 1.5                               # pin tip, 1.5 mm off the sphere
SPOKE_X0 = PIVOT_X1 + 0.5                            # the hub starts just outside the pivot face
HUB_R, HUB_T = 12.0, 6.0                             # hub on the spoke's end: round seen end-on, flat sides
TAB_R, TAB_W, TAB_H = 9.5, 3.0, 2.5                  # stop tab on the hub's face (radius, width, how far it stands out)
STOP_DEPTH = 3.0                                     # arc groove in the pivot's face
STOP_HALF = 90.0 + math.degrees(math.atan(TAB_W / 2 / TAB_R)) + 1.0   # the groove runs this far either side of the top
RING_GROOVES = (20.0,)                               # decorative ring on the pivot face (the mount screws sit inside it)
NUT_AF, NUT_POCKET_DEPTH = 5.6, 2.6
# laps
LAP_L = 40.0
LAP_SCREWS = 3
TIP_GAP = P.FIT
JOINTS = (45.0, 90.0, 135.0)                         # big-arc angles (deg, 0 = right, 90 = top)
PIECES = [('handle_end_right', -90.0, 45.0, 'rear'), ('handle_arc_1', 45.0, 90.0, 'front'),
          ('handle_arc_2', 90.0, 135.0, 'rear'), ('handle_end_left', 135.0, 270.0, 'front')]
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


def hub(sign):
    """Round hub on the spoke's end with the stop tab on its face (toward the pivot) and the hole the pin is glued in."""
    x0, x1 = sorted((sign * SPOKE_X0, sign * (SPOKE_X0 + HUB_T)))
    h = cq.Workplane('YZ').workplane(offset=x0).circle(HUB_R).extrude(x1 - x0)
    h = h.intersect(cq.Workplane('XY').box(BIG, T, BIG))   # flat sides: the piece still prints flat
    t0, t1 = sorted((sign * (SPOKE_X0 - TAB_H), sign * SPOKE_X0))
    h = h.union(cq.Workplane('XY').box(t1 - t0 + 0.5, TAB_W, TAB_W).translate(((t0 + t1) / 2 + sign * 0.25, 0, TAB_R)))
    return h


def pin_hole(sign):
    x0, x1 = sorted((sign * (SPOKE_X0 - TAB_H - 1), sign * (PIN_X0 + PIN_L + 0.5)))
    return cq.Workplane('YZ').workplane(offset=x0).circle(PIN_HOLE_R).extrude(x1 - x0)


def shaft(sign):
    """Printed axle: round, with flats at y = +-T/2 so the end piece prints flat, from the pivot's depth into the hub."""
    x0, x1 = sorted((sign * PIN_X0, sign * (SPOKE_X0 + HUB_T)))
    s = cq.Workplane('YZ').workplane(offset=x0).circle(SHAFT_R).extrude(x1 - x0)
    return s.intersect(cq.Workplane('XY').box(BIG, T, BIG))


def pin(sign):
    """The steel dowel pin, as placed (an envelope: bought, not printed)."""
    x0, x1 = sorted((sign * PIN_X0, sign * (PIN_X0 + PIN_L)))
    return cq.Workplane('YZ').workplane(offset=x0).circle(PIN_R).extrude(x1 - x0)


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
    return [(LOOP_R * math.cos(math.radians(phi + k * d * 0.6)), ZC + LOOP_R * math.sin(math.radians(phi + k * d * 0.6)))
            for k in range(-(LAP_SCREWS // 2), LAP_SCREWS // 2 + 1)]


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
        for sign, end in ((1, 'handle_end_right'), (-1, 'handle_end_left')):
            if name == end:
                p = p.union(hub(sign))
                p = p.union(shaft(sign)) if PRINTED else p.cut(pin_hole(sign))
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
    # arc groove for the hub's stop tab: from level on one side, over the top, to level on the other
    n = 24
    pt = lambda r, t: (r * math.cos(math.radians(90 + t)), r * math.sin(math.radians(90 + t)))
    ts = [-STOP_HALF + 2 * STOP_HALF * i / n for i in range(n + 1)]
    r0, r1 = TAB_R - TAB_W / 2 - 0.5, TAB_R + TAB_W / 2 + 0.5
    arc = cq.Workplane('YZ').workplane(offset=face - sign * STOP_DEPTH).polyline(
        [pt(r1, t) for t in ts] + [pt(r0, t) for t in reversed(ts)]).close().extrude(sign * (STOP_DEPTH + 1))
    b = b.cut(arc)
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
    out = dict(_CACHE[0])
    if not PRINTED:
        out['handle_pin_right_envelope'] = pin(1)
        out['handle_pin_left_envelope'] = pin(-1)
    return out


def placements():
    build()
    pl = dict(_CACHE[1])
    if not PRINTED:
        for n in ('handle_pin_right_envelope', 'handle_pin_left_envelope'):
            pl[n] = ((0, 0, 1), 0, (0, 0, P.Z_SPHERE_CENTER))
    return pl


def swing(placed, angle):
    """A loop piece already placed in the assembly, turned about the pivot axis (X through the sphere centre)."""
    return placed.rotate((0, 0, P.Z_SPHERE_CENTER), (1, 0, P.Z_SPHERE_CENTER), angle)
