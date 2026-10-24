"""
bells.py - rev C (2026-10-23): the two lens bells on the sphere's window sides, the front lens and the curtain clamp.

    bell_front     on the lens opening (-Y). LED collar band behind the lens, the lens on a ledge in front of it.
    bell_rear      on the hand opening (+Y). LED rim band in the throat, the one-piece frosted cover clamped at the mouth.
    diffuser       the front lens: a full round 118 mm white disc (the rev-9 diffuser had 98 mm flats: reprint)
    curtain_clamp  full ring that clamps the one-piece frosted cover's uncut edge to the inside of the rear bell's
                   mouth lip, holding it flat (4 countersunk M3 x 8 from behind it, inside the bell, into pilots in the
                   lip: the mouth face shows no screws)

Each bell is a revolved profile about its own axis, cut by the sphere's outer surface so its throat sits on the shell.
Its throat slides over the collar round the opening (sphere.bell_collar) and two thumbscrews hold it (2026-10-23): no
tools needed. They run parallel to the axis from inside the sphere (sphere.bell_mounts) into 6-32 inserts in the
throat, which is 8.5 mm thick for them; a small boss under each fills the flat spot on the shell. Nothing shows. Its LED strip's lead is soldered with slack, so it rests beside the lantern when off. Printed mouth down: the inner cone is under 35 deg from vertical; the inward steps are 45 deg or under 3 mm.

Bell frame: the bell axis is +Z, the sphere centre at the origin, s (= z) the distance out from the centre.
"""
import math
import cadquery as cq
import params as P
from parts import sphere as S

R = S.R_OUT


def _s_surface(r):
    """Distance from the centre along the axis to the sphere's outer surface at radius r from the axis."""
    return math.sqrt(R * R - r * r)


# ------------------------------------------------------------------ front bell (lens)
F_EDGE = _s_surface(S.LENS_R)                # 96.4: sphere surface at the opening edge
F_MOUTH = F_EDGE + P.FRONT_BELL_L            # 160.4
F_OUT = P.FRONT_BELL_MOUTH_R                 # 84
F_LED_R, F_LED_S = 61.0, (106.0, 116.0)      # LED collar band: 37.5 cm of 10 mm COB strip, facing the axis
F_THROAT_OUT = F_LED_R + S.BELL_THROAT_T     # 69.5: throat band, 8.5 mm wall round the thumbscrews' inserts
F_LEDGE_S = 117.5                            # the lens rests on this face (toward the mouth)
LENS_R = P.DIFFUSER_D / 2                    # 59
F_LENS_POCKET = LENS_R + P.SNUG              # 59.15: the lens presses in, a few dots of glue hold it
F_CONE_S = 120.0                             # the inner chamfer starts here
F_OUTER_CONE_S = 106.0                       # outer: the throat band (bayonet), then a cone to the mouth
F_WALL = 2.6                                 # radial wall of the cone (2.5 mm normal: 4 perimeters)


def _f_outer(s):
    return F_THROAT_OUT + (F_OUT - F_THROAT_OUT) * (s - F_OUTER_CONE_S) / (F_MOUTH - F_OUTER_CONE_S)


def _meet_45(r0, s0, outer, wall):
    """Where a 45 deg line out from (r0, s0) meets the inner wall surface outer(s) - wall."""
    k = (outer(s0 + 1.0) - outer(s0))
    d = (outer(s0) - wall - r0) / (1.0 - k)
    return r0 + d, s0 + d


def front_profile():
    s0 = S.CUT - 10                          # well inside the sphere; the sphere cut trims it
    return [
        (F_LED_R, s0),                         # bore over the bayonet collar, then the LED band
        (F_LED_R, F_LED_S[1]),
        (S.LENS_R, F_LED_S[1]),                # ledge (2 mm overhang when printed)
        (S.LENS_R, F_LEDGE_S),
        (F_LENS_POCKET, F_LEDGE_S),            # lens pocket
        (F_LENS_POCKET, F_CONE_S),
        _meet_45(F_LENS_POCKET, F_CONE_S, _f_outer, F_WALL),   # 45 deg chamfer out to the wall
        (F_OUT - F_WALL, F_MOUTH),             # inner cone
        (F_OUT, F_MOUTH),                      # mouth face (on the bed)
        (F_THROAT_OUT, F_OUTER_CONE_S),        # outer cone
        (F_THROAT_OUT, s0),
    ]


# ------------------------------------------------------------------ rear bell (hand opening)
R_EDGE = _s_surface(S.HAND_R)                # 91.2
R_MOUTH = R_EDGE + P.REAR_BELL_L             # 151.2
R_OUT = P.REAR_BELL_MOUTH_R                  # 90
R_LED_R, R_LED_S = 74.0, (104.0, 114.0)      # LED rim band: a full ring, ~45 cm of strip (2026-10-23, was 25-30 cm)
R_THROAT_OUT = R_LED_R + S.BELL_THROAT_T     # 82.5: throat band, 8.5 mm wall round the thumbscrews' inserts
R_LIP_R = 78.0                               # the mouth lip: the curtain sits against its inner face
R_LIP_T = 4.0
R_LIP_S = R_MOUTH - R_LIP_T                  # 147.2: lip inner face (curtain seat)
R_MOUTH_BAND_S = R_MOUTH - 16.0              # outer: cylindrical mouth band from here
R_OUTER_CONE_S = 100.0
R_WALL = 2.8
CURTAIN_R = 85.5                             # the one-piece frosted cover (see params CURTAIN_SLITS): 171 mm across
CURTAIN_T = 0.5
CLAMP_R = (R_LIP_R, R_OUT - R_WALL - 0.5)    # 78 .. 86.7
CLAMP_T = 4.5                                # a countersunk M3 x 8 flush in its back bites 3 mm into the lip
CLAMP_CSK = (P.M3_HEAD_D + 0.4, 1.9)         # countersink: diameter at the face, depth (90 deg flat head)
CLAMP_PILOT, CLAMP_PILOT_DEPTH = 2.5, 3.2    # self-tapping pilot in the 4 mm lip: 0.8 mm (4 layers) left on the mouth face
CLAMP_SCREW_R = sum(CLAMP_R) / 2             # 81.75
CLAMP_SCREW_ANGLES = tuple(45.0 + 90.0 * k for k in range(4))   # around the bell axis, from +X: 4 of Kevin's 8 flat heads (the lock uses the other 4)


def _r_outer(s):
    if s >= R_MOUTH_BAND_S:
        return R_OUT
    return R_THROAT_OUT + (R_OUT - R_THROAT_OUT) * (s - R_OUTER_CONE_S) / (R_MOUTH_BAND_S - R_OUTER_CONE_S)


def rear_profile():
    s0 = S.CUT - 10
    return [
        (R_LED_R, s0),                         # bore over the bayonet collar, then the LED band
        (R_LED_R, R_LED_S[1]),
        _meet_45(R_LED_R, R_LED_S[1], _r_outer, R_WALL),       # 45 deg chamfer out to the wall
        (R_OUT - R_WALL, R_MOUTH_BAND_S),      # inner cone
        (R_OUT - R_WALL, R_LIP_S),
        (R_LIP_R, R_LIP_S),                    # curtain seat (faces up when printed)
        (R_LIP_R, R_MOUTH),                    # mouth lip
        (R_OUT, R_MOUTH),                      # mouth face (on the bed)
        (R_OUT, R_MOUTH_BAND_S),               # mouth band
        (R_THROAT_OUT, R_OUTER_CONE_S),        # outer cone
        (R_THROAT_OUT, s0),
    ]


# ------------------------------------------------------------------ build
def _revolve(pts):
    return cq.Workplane('XZ').polyline(pts).close().revolve(360.0, (0, 0, 0), (0, 1, 0))


def bell_bore(sign):
    return S.collar_dims(sign)[1] + P.FIT


def _bell(pts, sign):
    """The revolved bell, cut by the sphere, with a boss filling each flat spot on the shell and a 6-32 insert bore up
    its axis (the bell prints mouth down, so the insert goes in from the throat end, pointing up: no overhang)."""
    b = _revolve(pts).cut(cq.Workplane('XY').sphere(R))
    rs, sf = S.bell_screw_r(sign), S.bell_screw_s(sign)
    for a in S.BELL_LOCK_ANGLES[sign]:
        rot = lambda w: w.rotate((0, 0, 0), (0, 0, 1), S.bell_frame_angle(sign, a))
        b = b.union(rot(cq.Workplane('XY').workplane(offset=sf).center(rs, 0).circle(S.BELL_SPOT_R - P.SNUG).extrude(8.0)))
        b = b.cut(rot(cq.Workplane('XY').workplane(offset=sf - 0.5).center(rs, 0).circle(P.THUMB_INSERT_HOLE / 2)
                      .extrude(P.THUMB_INSERT_DEPTH + 0.5)))
    return b


def bell_front():
    return _bell(front_profile(), -1)


def bell_rear():
    b = _bell(rear_profile(), +1)
    for a in CLAMP_SCREW_ANGLES:             # blind pilots in the lip for the clamp screws (top = -Y in this frame)
        x, y = CLAMP_SCREW_R * math.cos(math.radians(a)), -CLAMP_SCREW_R * math.sin(math.radians(a))
        b = b.cut(cq.Workplane('XY').workplane(offset=R_LIP_S - 0.5).center(x, y).circle(CLAMP_PILOT / 2).extrude(CLAMP_PILOT_DEPTH + 0.5))
    return b


def diffuser():
    """The front lens: full round, so the whole 114 mm opening glows (print flat in white PETG, 1 mm = 5 layers)."""
    return cq.Workplane('XY').circle(LENS_R).extrude(P.DIFFUSER_T)


def curtain_clamp():
    """Full ring: it presses the cover's uncut edge against the rear bell's lip all the way round, so the cover stays
    flat and its flaps spring back closed; 4 countersunk M3 x 8 from its back (inside the bell), through the cover into
    pilots in the lip (punch the cover's 4 holes using the ring as a guide). Printed flat, curtain face down; frame: the
    bell axis at the origin, z = 0 the face against the curtain."""
    r0, r1 = CLAMP_R
    c = cq.Workplane('XY').circle(r1).circle(r0).extrude(CLAMP_T)
    d, h = CLAMP_CSK
    for t in CLAMP_SCREW_ANGLES:
        x, y = CLAMP_SCREW_R * math.cos(math.radians(t)), CLAMP_SCREW_R * math.sin(math.radians(t))
        c = c.cut(cq.Workplane('XY').workplane(offset=-0.5).center(x, y).circle(P.M3_CLEAR / 2).extrude(CLAMP_T + 1))
        c = c.cut(cq.Workplane('XY').add(cq.Solid.makeCone(P.M3_CLEAR / 2, d / 2, h, pnt=cq.Vector(x, y, CLAMP_T - h + 0.001))))
    return c


def _ring(r0, r1, s0, s1):
    return cq.Workplane('XY').workplane(offset=s0).circle(r1).circle(r0).extrude(s1 - s0)


def build():
    return {
        'bell_front': bell_front().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, F_MOUTH)),   # mouth down
        'bell_rear': bell_rear().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, R_MOUTH)),
        'diffuser': diffuser(),
        'curtain_clamp': curtain_clamp(),
        # LED strips on the bands (COB strip ~2 mm thick) and the frosted curtain, for renders and checks
        'front_led_envelope': _ring(F_LED_R - 2.0, F_LED_R - 0.05, F_LED_S[0] + 0.05, F_LED_S[1] - 0.05),
        'rear_led_envelope': _ring(R_LED_R - 2.0, R_LED_R - 0.05, R_LED_S[0] + 0.05, R_LED_S[1] - 0.05),
        'curtain_envelope': cq.Workplane('XY').workplane(offset=R_LIP_S - CURTAIN_T).circle(CURTAIN_R).extrude(CURTAIN_T - 0.05),
    }


def _to_front():
    return ((1, 0, 0), 90, (0, 0, P.Z_SPHERE_CENTER))   # bell frame +Z -> assembly -Y


def _to_rear():
    return ((1, 0, 0), -90, (0, 0, P.Z_SPHERE_CENTER))


def placements():
    front, rear = _to_front(), _to_rear()
    flip = lambda s: ((1, 0, 0), 180, (0, 0, s))         # undo the mouth-down print flip
    return {
        'bell_front': [flip(F_MOUTH), front],
        'bell_rear': [flip(R_MOUTH), rear],
        'diffuser': [((0, 0, 1), 0, (0, 0, F_LEDGE_S)), front],
        # printed flat with its arc on +Y; turned 180 so the arc is on top once in the rear bell, against the lip
        'curtain_clamp': [((1, 0, 0), 180, (0, 0, R_LIP_S - CURTAIN_T)), rear],   # flipped: its face against the cover
        'front_led_envelope': front,
        'rear_led_envelope': rear,
        'curtain_envelope': rear,
    }
