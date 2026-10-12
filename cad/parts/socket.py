"""
socket.py - the twist-to-pour charging socket (rev 4).

Socket frame: Z up, origin on the rotor axis at the FACEPLATE TOP (assembly Z = Z_UPPER_FLOOR_TOP = 311).
+Y = rear (wire exit toward the dish floor's +Y wire slot). Rotor angles are measured CCW from +X seen from
above; the ring is twisted CLOCKWISE seen from above, so a rotor feature at rest angle `a` is at `a - phi`
after a twist of `phi` degrees.

Parts (print orientation noted in build()):
  socket_housing  faceplate (OD 100 x 3) + housing puck (OD 76, 6.7 deep) with every cavity; printed faceplate down
  rotor           disc OD 36 x 8 with the keyed pocket on top, and below the faceplate lip: the stop lug, the
                  switch cam lobe and the plunger ramp, all one polygon extrusion
  socket_base     plate OD 76 x 3.5 that closes the housing from below: holds the Hall board (chip down, sensor
                  window on the axis), the switch bracket recess with a captured nut, 3 screw holes
  switch_bracket  16 x 10 x 2 slide with two pegs for the D2F-L, M3 slot for +/- 2 mm radial tuning
  plunger         4.5 mm long spring plunger with a rounded nose
  halo            (only if LED_RING) translucent ring over a 24-px NeoPixel ring
  key_cap         24 mm keyed disc with the magnet pocket, glued to the ring's face
  switch_envelope D2F-L body + lever at rest, for the collision test (not printed)

Mechanism, from the top: ring + key_cap drop into the rotor pocket (one orientation). Twist clockwise:
  - the stop lug rides in a 59 deg channel whose walls are the 0 and 45 deg hard stops;
  - the cam lobe lifts the D2F-L lever 3 mm between 30 and 40 deg of twist (click before the stop);
  - the ramp pushes the spring plunger out 4 mm; let go and the plunger pushes the rotor back to 0.
The rotor is assembled from BELOW into the housing (lugs under the faceplate lip), then socket_base closes it.
"""
import math
import cadquery as cq
import params as P

# ------------------------------------------------------------------ dimensions
# In the punch-in layout the socket stands inside the sphere, so the faceplate shrinks to the housing OD
# (no screws through it); the base plate carries two mounting ears instead.
PLATE_D = P.SOCKET_HOUSING_OD if P.SOCKET_IN_SPHERE else P.SOCKET_PLATE_D
PLATE_T = P.SOCKET_PLATE_T                 # 3
HOUSING_OD = P.SOCKET_HOUSING_OD           # 76
BOLT_R = P.SOCKET_BOLT_CIRCLE / 2          # 44
BOLT_ANGLES = (45.0, 135.0, 225.0, 315.0)  # must match dishes.SOCKET_BOLT_ANGLES

ROTOR_R = P.ROTOR_OD / 2                   # 18
ROTOR_TOP = -0.5                           # rotor top face sits 0.5 below the faceplate surface
ROTOR_H = 8.0                              # rev 4: a flat rotor; the Hall board sits just under it
ROTOR_BOT = ROTOR_TOP - ROTOR_H            # -8.5
BORE_R = ROTOR_R + P.FIT                   # 18.3
LUG_TOP = -PLATE_T - 0.4                   # lugs start 0.4 under the faceplate lip (-3.4)
CAVITY_TOP = -PLATE_T                      # -3: the faceplate underside retains the lugs
HOUSING_BOT = -9.7                         # housing puck bottom = socket_base top
HOUSING_H = -CAVITY_TOP + (-HOUSING_BOT)   # 6.7 below the faceplate
BASE_T = 3.5
BASE_BOT = HOUSING_BOT - BASE_T            # -13.2
MODULE_DEPTH = -BASE_BOT                   # 13.2 below the faceplate top (+ ~6 mm Hall connector)

KEY_POCKET_R = P.KEY_D / 2 + P.FIT         # 12.3
KEY_POCKET_DEPTH = P.KEY_T + 0.5           # 3.5
KEY_TAB_W = P.KEY_TAB_W + 2 * P.FIT        # 6.6 (tab at rest angle 0 = +X)
KEY_TAB_L = P.KEY_TAB_L + P.FIT            # 4.3 radial
POCKET_FLOOR = ROTOR_TOP - KEY_POCKET_DEPTH   # -4.0: magnet bottom face sits here

# Optional NeoPixel ring at the socket. The budget build has no LEDs here (the sphere strip carries the
# light), so the recess and the halo part are off. Set True to restore them.
LED_RING = False
# NeoPixel ring recess (from the top) and halo
RING_RECESS_RO = P.NEOPIXEL_RING_OD / 2 + 0.3   # 33.05
RING_RECESS_RI = P.NEOPIXEL_RING_ID / 2 - 0.3   # 25.85
RING_RECESS_DEPTH = P.NEOPIXEL_RING_T + 0.2     # 3.4: PCB flush, LEDs stand 1.6 proud under the halo
HALO_H, HALO_SKIN, HALO_RIM = 4.0, 1.2, 1.0
HALO_RO, HALO_RI = RING_RECESS_RO + HALO_RIM, RING_RECESS_RI - HALO_RIM
WIRE_NOTCH_ANGLE, WIRE_NOTCH_R, WIRE_NOTCH_W, WIRE_NOTCH_T = 90.0, 29.5, 6.0, 3.0   # +Y, r 28..31

# stop lug and its channel (hard stops)
STOP_ANGLE = 180.0                         # rest angle of the stop lug (-X)
STOP_W_DEG = 2 * math.degrees(math.atan2(2.0, 20.0))   # 4 mm wide lug at r 20 -> ~11.4 deg
STOP_R_OUT = 22.5
CHANNEL_A0 = STOP_ANGLE - P.ROTOR_TRAVEL_DEG - STOP_W_DEG / 2 - 0.6   # 128.7 (45 deg end stop)
CHANNEL_A1 = STOP_ANGLE + STOP_W_DEG / 2 + 0.6                        # 186.3 (0 deg end stop)
CHANNEL_R_OUT = STOP_R_OUT + 1.0

# switch: lever tip at rest angle LEVER_TIP_ANGLE, r LEVER_REST_R; cam lobe lifts it CAM_LIFT
LEVER_TIP_ANGLE = 20.0
LEVER_REST_R = ROTOR_R + 0.8               # 18.8
LEVER_LEN = 13.0
SWITCH_FACE_N = 8.0                        # lever rest height above the switch mounting face (2 mm preload)
CAM_START = LEVER_TIP_ANGLE + 30.0         # 50: lobe begins to touch at 30 deg of twist
CAM_FULL0 = LEVER_TIP_ANGLE + 37.0         # 57: full lift from 37 deg
CAM_FULL1 = LEVER_TIP_ANGLE + 46.0         # 66: full lift until 46 deg (past the 45 deg stop)
CAM_END = CAM_FULL1 + 4.0                  # 70
CAM_R = ROTOR_R + P.CAM_LIFT               # 21
SWITCH_T0, SWITCH_T1 = 0.0, P.D2F_L        # body extent along the tangent from the lever tip
SWITCH_N0 = SWITCH_FACE_N                  # mounting face radial offset from the lever rest line
SWITCH_N1 = SWITCH_N0 + P.D2F_H            # 14.5
SWITCH_Z_TOP = -3.9                        # body top (just under the ring recess floor at -3.4)
SWITCH_Z_BOT = SWITCH_Z_TOP - P.D2F_W      # -9.7 = housing bottom: the body stands on the bracket
PEG_D, PEG_H = 2.3, 4.5
BRACKET_W, BRACKET_L, BRACKET_T = 16.0, 10.0, 2.0

# plunger + ramp
PLUNGER_ANGLE = 300.0
RAMP_A0, RAMP_A1, RAMP_DROP = PLUNGER_ANGLE, PLUNGER_ANGLE + P.ROTOR_TRAVEL_DEG, 5.0   # 300..345, back to 18 by 350
RAMP_R = ROTOR_R + P.CAM_RISE              # 22
PLUNGER_D = P.SPRING_D + 0.2               # 5.2
PLUNGER_CH_W = P.SPRING_POCKET_D           # 5.6
PLUNGER_CH_Z0, PLUNGER_CH_Z1 = HOUSING_BOT, -4.2    # 5.5 tall, 0.8 skin under the ring recess
PLUNGER_CH_R0, PLUNGER_CH_R1 = BORE_R, 34.0         # closed end 1.6 + 2.4 from the outside
PLUNGER_CH_LEN = PLUNGER_CH_R1 - PLUNGER_CH_R0      # 15.7 = plunger 4.5 + spring 10 + preload 1.2

# base plate screws: M3 into captured nuts in the housing (no inserts in the thin zone under the ring recess)
BASE_SCREW_R = 26.5
BASE_SCREW_ANGLES = (100.0, 220.0, 330.0)
NUT_AF, NUT_T = 5.8, 2.6

# Hall board (chip DOWN so the JST connector hangs below the plate; the DRV5032 is sensitive enough)
HALL_POCKET_L, HALL_POCKET_W, HALL_POCKET_D = P.HALL_PCB_L + 0.6, P.HALL_PCB_W + 0.6, P.HALL_PCB_T + 0.2
SENSOR_WINDOW = 8.0                        # square hole on the axis through the plate (A3144 option: bend it up here)
MAGNET_TO_SENSOR = (POCKET_FLOOR - (HOUSING_BOT - 0.1 - P.HALL_PCB_T - 0.9))   # ~7.7 mm, see NOTES

Z_FACEPLATE_TOP = P.Z_SPHERE_TOP + P.FLOOR     # 311 assembly (top-dish layout only)
EAR_W, EAR_ANGLES = 10.0, P.SOCKET_EAR_ANGLES   # base-plate ears; socket angle a -> sphere (x, z) = (cos a, -sin a)
STANDOFF_OD = 7.0
FACE_Y = P.LOCK_FACE_Y                         # socket face y, assembly frame; the base plate sits on the lock wall
assert abs(MODULE_DEPTH - P.SOCKET_MODULE_DEPTH) < 1e-6, 'params.SOCKET_MODULE_DEPTH out of date'


# ------------------------------------------------------------------ helpers
def pol(r, a_deg):
    a = math.radians(a_deg)
    return (r * math.cos(a), r * math.sin(a))


def cyl(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def sector(r_in, r_out, a0, a1, z0, z1):
    """Annular sector (a0 < a1, span < 180) between z0 and z1."""
    am = (a0 + a1) / 2
    wp = (cq.Workplane('XY').workplane(offset=z0)
          .moveTo(*pol(r_in, a0)).lineTo(*pol(r_out, a0))
          .threePointArc(pol(r_out, am), pol(r_out, a1))
          .lineTo(*pol(r_in, a1))
          .threePointArc(pol(r_in, am), pol(r_in, a0)).close())
    return wp.extrude(z1 - z0)


def frame_box(t0, t1, n0, n1, z0, z1, angle_deg, origin_r):
    """Box in the tangent frame of the point at (origin_r, angle): t = clockwise tangent, n = radial outward."""
    bx = (cq.Workplane('XY').workplane(offset=z0).center((t0 + t1) / 2, (n0 + n1) / 2)
          .rect(t1 - t0, n1 - n0).extrude(z1 - z0))
    # local frame: +x = t (clockwise tangent), +y = n (radial). Radial direction is angle; clockwise tangent = angle - 90.
    bx = bx.rotate((0, 0, 0), (0, 0, 1), angle_deg - 90.0)
    ox, oy = pol(origin_r, angle_deg)
    return bx.translate((ox, oy, 0))


def rotor_profile_points(step_deg=1.0):
    """Polar profile r(a) of the rotor's lower ring: base 18, plus stop lug, cam lobe and plunger ramp."""
    pts = []
    n = int(360 / step_deg)
    for i in range(n):
        a = i * step_deg
        r = ROTOR_R
        # stop lug
        if abs(((a - STOP_ANGLE + 180) % 360) - 180) <= STOP_W_DEG / 2:
            r = STOP_R_OUT
        # cam lobe for the switch lever
        if CAM_START <= a < CAM_FULL0:
            r = max(r, ROTOR_R + P.CAM_LIFT * (a - CAM_START) / (CAM_FULL0 - CAM_START))
        elif CAM_FULL0 <= a <= CAM_FULL1:
            r = max(r, CAM_R)
        elif CAM_FULL1 < a <= CAM_END:
            r = max(r, ROTOR_R + P.CAM_LIFT * (CAM_END - a) / (CAM_END - CAM_FULL1))
        # plunger ramp
        if RAMP_A0 <= a <= RAMP_A1:
            r = max(r, ROTOR_R + P.CAM_RISE * (a - RAMP_A0) / (RAMP_A1 - RAMP_A0))
        elif RAMP_A1 < a <= RAMP_A1 + RAMP_DROP:
            r = max(r, ROTOR_R + P.CAM_RISE * (RAMP_A1 + RAMP_DROP - a) / RAMP_DROP)
        pts.append(pol(r, a))
    return pts


# ------------------------------------------------------------------ parts (socket frame)
def rotor_solid():
    top = cyl(ROTOR_R, ROTOR_BOT, ROTOR_TOP)
    lower = (cq.Workplane('XY').workplane(offset=ROTOR_BOT).polyline(rotor_profile_points()).close()
             .extrude(LUG_TOP - ROTOR_BOT))
    r = top.union(lower)
    # keyed pocket: disc + tab notch at +X, chamfered edge so the ring finds it
    r = r.cut(cyl(KEY_POCKET_R, POCKET_FLOOR, ROTOR_TOP + 1))
    r = r.cut(cq.Workplane('XY').workplane(offset=POCKET_FLOOR)
              .center(KEY_POCKET_R + KEY_TAB_L / 2 - 0.5, 0).rect(KEY_TAB_L + 1.0, KEY_TAB_W)
              .extrude(ROTOR_TOP - POCKET_FLOOR + 1))
    try:
        r = r.faces('>Z').edges(cq.selectors.RadiusNthSelector(0)).chamfer(0.8)
    except Exception:
        pass
    return r


def housing_solid():
    h = cyl(PLATE_D / 2, -PLATE_T, 0.0)                       # faceplate
    h = h.union(cyl(HOUSING_OD / 2, HOUSING_BOT, -PLATE_T))    # puck
    cuts = []
    # faceplate screws (counterbored from the top)
    for a in (BOLT_ANGLES if not P.SOCKET_IN_SPHERE else ()):
        x, y = pol(BOLT_R, a)
        cuts.append(cyl(P.M3_CLEAR / 2, -PLATE_T - 1, 1, x, y))
        cuts.append(cyl(P.M3_HEAD_D / 2 + 0.2, -1.2, 1, x, y))
    # NeoPixel ring recess and its wire notch
    if LED_RING:
        cuts.append(cyl(RING_RECESS_RO, -RING_RECESS_DEPTH, 1).cut(cyl(RING_RECESS_RI, -RING_RECESS_DEPTH - 1, 2)))
    cuts.append(frame_box(-WIRE_NOTCH_W / 2, WIRE_NOTCH_W / 2, -WIRE_NOTCH_T / 2, WIRE_NOTCH_T / 2,
                          HOUSING_BOT - 1, -RING_RECESS_DEPTH + 0.5, WIRE_NOTCH_ANGLE, WIRE_NOTCH_R))
    # rotor bore through the faceplate, rotor cavity below it
    cuts.append(cyl(BORE_R, HOUSING_BOT - 1, 1))
    # stop channel (its end walls are the hard stops)
    cuts.append(sector(BORE_R - 0.5, CHANNEL_R_OUT, CHANNEL_A0, CHANNEL_A1, HOUSING_BOT - 1, CAVITY_TOP))
    # cam lobe sweep + lever travel + switch body
    cuts.append(sector(BORE_R - 0.5, CAM_R + 0.8, CAM_START - P.ROTOR_TRAVEL_DEG - 3, CAM_END + 2, HOUSING_BOT - 1, CAVITY_TOP))
    cuts.append(frame_box(-2.0, SWITCH_T1 + 2.0, -0.8, SWITCH_N1 + 0.8, HOUSING_BOT - 1, CAVITY_TOP,
                          LEVER_TIP_ANGLE, LEVER_REST_R))
    # plunger ramp sweep and the plunger channel
    cuts.append(sector(BORE_R - 0.5, RAMP_R + 0.6, RAMP_A0 - P.ROTOR_TRAVEL_DEG - 2, RAMP_A1 + RAMP_DROP + 1, HOUSING_BOT - 1, CAVITY_TOP))
    cuts.append(frame_box(-PLUNGER_CH_W / 2, PLUNGER_CH_W / 2, PLUNGER_CH_R0 - 0.5 - BORE_R, PLUNGER_CH_R1 - BORE_R,
                          PLUNGER_CH_Z0 - 1, PLUNGER_CH_Z1, PLUNGER_ANGLE, BORE_R))
    # captured nuts + screw holes for the base plate
    for a in BASE_SCREW_ANGLES:
        x, y = pol(BASE_SCREW_R, a)
        cuts.append(cq.Workplane('XY').workplane(offset=HOUSING_BOT - 1).center(x, y)
                    .polygon(6, NUT_AF / math.cos(math.radians(30))).extrude(NUT_T + 1))
        cuts.append(cyl(P.M3_CLEAR / 2, HOUSING_BOT - 1, -3.8, x, y))
    for c in cuts:
        h = h.cut(c)
    return h


def base_solid():
    b = cyl(HOUSING_OD / 2, BASE_BOT, HOUSING_BOT)
    if P.SOCKET_IN_SPHERE:   # two mounting ears, screwed through standoffs to the LED carrier
        for a in EAR_ANGLES:
            ex, ey = pol(P.SOCKET_EAR_R, a)
            arm = frame_box(-EAR_W / 2, EAR_W / 2, 0.0, P.SOCKET_EAR_R - HOUSING_OD / 2 + EAR_W / 2 + 2.0,
                            BASE_BOT, HOUSING_BOT, a, HOUSING_OD / 2 - 2.0)
            b = b.union(arm).union(cyl(EAR_W / 2, BASE_BOT, HOUSING_BOT, ex, ey))
            b = b.cut(cyl(P.M3_CLEAR / 2, BASE_BOT - 1, HOUSING_BOT + 1, ex, ey))
    cuts = []
    for a in BASE_SCREW_ANGLES:
        x, y = pol(BASE_SCREW_R, a)
        cuts.append(cyl(P.M3_CLEAR / 2, BASE_BOT - 1, HOUSING_BOT + 1, x, y))
        cuts.append(cyl(P.M3_HEAD_D / 2 + 0.2, BASE_BOT - 1, BASE_BOT + 2.0, x, y))
    # Hall board pocket from below (long side along X), sensor window on the axis
    cuts.append(cq.Workplane('XY').workplane(offset=BASE_BOT - 1).rect(HALL_POCKET_L, HALL_POCKET_W)
                .extrude(HALL_POCKET_D + 1))
    cuts.append(cq.Workplane('XY').workplane(offset=BASE_BOT - 1).rect(SENSOR_WINDOW, SENSOR_WINDOW)
                .extrude(BASE_T + 2))
    # switch bracket recess (top), its screw hole and captured nut (bottom)
    bt0, bt1 = SWITCH_T0 + (SWITCH_T1 - SWITCH_T0) / 2 - 9.0, SWITCH_T0 + (SWITCH_T1 - SWITCH_T0) / 2 + 9.0
    bn0, bn1 = SWITCH_N0 - 2.5, SWITCH_N0 + 9.5   # recess spans the body footprint + slide room
    cuts.append(frame_box(bt0, bt1, bn0, bn1, HOUSING_BOT - BRACKET_T, HOUSING_BOT + 1, LEVER_TIP_ANGLE, LEVER_REST_R))
    sx, sy = switch_screw_xy()
    cuts.append(cyl(P.M3_CLEAR / 2, BASE_BOT - 1, HOUSING_BOT + 1, sx, sy))
    cuts.append(cq.Workplane('XY').workplane(offset=BASE_BOT - 1).center(sx, sy)
                .polygon(6, NUT_AF / math.cos(math.radians(30))).extrude(NUT_T + 1))
    # wire notch continues through the plate; two cable-tie slots
    cuts.append(frame_box(-WIRE_NOTCH_W / 2, WIRE_NOTCH_W / 2, -WIRE_NOTCH_T / 2, WIRE_NOTCH_T / 2,
                          BASE_BOT - 1, HOUSING_BOT + 1, WIRE_NOTCH_ANGLE, WIRE_NOTCH_R))
    for a in (150.0, 250.0):
        cuts.append(frame_box(-1.5, 1.5, -2.0, 2.0, BASE_BOT - 1, HOUSING_BOT + 1, a, 33.0))
    for c in cuts:
        b = b.cut(c)
    return b


def switch_screw_xy():
    t = SWITCH_T0 + (SWITCH_T1 - SWITCH_T0) / 2
    n = SWITCH_N0 + 3.5
    return frame_point(t, n, LEVER_TIP_ANGLE, LEVER_REST_R)


def frame_point(t, n, angle_deg, origin_r):
    ox, oy = pol(origin_r, angle_deg)
    a = math.radians(angle_deg)
    tx, ty = math.sin(a), -math.cos(a)        # clockwise tangent
    nx, ny = math.cos(a), math.sin(a)
    return (ox + t * tx + n * nx, oy + t * ty + n * ny)


def bracket_solid():
    """Printed flat: plate 16 x 10 x 2 with two pegs on top, slot along the radial direction."""
    b = cq.Workplane('XY').rect(BRACKET_W, BRACKET_L).extrude(BRACKET_T)
    for dx in (-P.D2F_HOLE_PITCH / 2, P.D2F_HOLE_PITCH / 2):
        b = b.union(cq.Workplane('XY').workplane(offset=BRACKET_T).center(dx, 0).circle(PEG_D / 2).extrude(PEG_H))
    b = b.cut(cq.Workplane('XY').workplane(offset=-1).slot2D(7.0, P.M3_CLEAR, angle=90).extrude(BRACKET_T + 2))
    return b


def plunger_solid():
    p = cq.Workplane('XY').circle(PLUNGER_D / 2).extrude(PLUNGER_L_EFF())
    p = p.faces('>Z').fillet(PLUNGER_D / 2 - 0.3)
    return p


def PLUNGER_L_EFF():
    return P.PLUNGER_L


def halo_solid():
    h = cyl(HALO_RO, 0, HALO_H).cut(cyl(HALO_RI, -1, HALO_H + 1))
    h = h.cut(cyl(RING_RECESS_RO, -1, HALO_H - HALO_SKIN).cut(cyl(RING_RECESS_RI, -2, HALO_H + 1)))
    return h


def key_cap_solid():
    k = cq.Workplane('XY').circle(P.KEY_D / 2).extrude(P.KEY_T)
    k = k.union(cq.Workplane('XY').center(P.KEY_D / 2 + P.KEY_TAB_L / 2 - 0.5, 0).rect(P.KEY_TAB_L + 1.0, P.KEY_TAB_W).extrude(P.KEY_T))
    k = k.cut(cq.Workplane('XY').workplane(offset=-1).circle(P.MAGNET_POCKET_D / 2).extrude(P.MAGNET_POCKET_T + 1))
    return k


def switch_envelope_solid():
    """D2F-L body at rest + lever (0.5 mm plate at the rest line), socket frame."""
    body = frame_box(SWITCH_T0, SWITCH_T1, SWITCH_N0, SWITCH_N1, SWITCH_Z_BOT, SWITCH_Z_TOP, LEVER_TIP_ANGLE, LEVER_REST_R)
    lever = frame_box(0.0, LEVER_LEN, -0.25, 0.25, SWITCH_Z_BOT + 2.5, SWITCH_Z_TOP - 2.5, LEVER_TIP_ANGLE, LEVER_REST_R)
    return body.union(lever)


# ------------------------------------------------------------------ build / placements
_cache = {}


def _parts_socket_frame():
    if not _cache:
        _cache.update({
            'socket_housing': housing_solid(),
            'rotor': rotor_solid(),
            'socket_base': base_solid(),
            'switch_envelope': switch_envelope_solid(),
        })
    return _cache


def _flip_to_bed(wp):
    """socket frame -> print frame: turn upside down and put min z on the bed; returns (part, z_shift)."""
    f = wp.rotate((0, 0, 0), (1, 0, 0), 180)
    dz = -f.val().BoundingBox().zmin
    return f.translate((0, 0, dz)), dz


_SHIFT = {}


def build():
    sf = _parts_socket_frame()
    out = {}
    for name in ('socket_housing', 'rotor', 'socket_base', 'switch_envelope'):
        out[name], _SHIFT[name] = _flip_to_bed(sf[name])
    out['switch_bracket'] = bracket_solid()
    out['plunger'] = plunger_solid()
    out['key_cap'] = key_cap_solid().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, P.KEY_T))  # flat top down
    if P.SOCKET_IN_SPHERE and P.SOCKET_STANDOFF > 0:
        st = cyl(STANDOFF_OD / 2, 0, P.SOCKET_STANDOFF).cut(cyl(P.M3_CLEAR / 2, -1, P.SOCKET_STANDOFF + 1))
        out['socket_standoff'] = st          # print 2
    if LED_RING:
        out['halo'] = halo_solid().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, HALO_H))   # skin down
    return out


def mount_step():
    """socket frame (faceplate top at the origin, +Z out of the face) -> assembly."""
    if P.SOCKET_IN_SPHERE:
        # rotate so the face points at the hand (+Y), socket +Y points down, then move onto the lock wall
        return ((1, 0, 0), -90, (0, FACE_Y, P.Z_SPHERE_CENTER + P.SOCKET_Z_LOCAL))
    return ((0, 0, 1), 0, (0, 0, Z_FACEPLATE_TOP))


def placements():
    if not _SHIFT:
        build()
    X = (1, 0, 0)
    bx, by = frame_point(SWITCH_T0 + (SWITCH_T1 - SWITCH_T0) / 2, SWITCH_N0 + 3.5, LEVER_TIP_ANGLE, LEVER_REST_R)
    px, py = pol(PLUNGER_CH_R0 + P.PLUNGER_L / 2 + 0.3, PLUNGER_ANGLE)
    m = mount_step()
    # print P = R180(S) + (0,0,dz)  =>  S = R180(P) + (0,0,dz)
    pl = {n: [(X, 180, (0, 0, _SHIFT[n])), m] for n in ('socket_housing', 'rotor', 'socket_base', 'switch_envelope')}
    pl['switch_bracket'] = [((0, 0, 1), LEVER_TIP_ANGLE - 90.0, (bx, by, HOUSING_BOT - BRACKET_T)), m]
    pl['plunger'] = [((0, 1, 0), 90, (px - P.PLUNGER_L / 2, py, (PLUNGER_CH_Z0 + PLUNGER_CH_Z1) / 2)), m]
    pl['key_cap'] = [(X, 180, (0, 0, POCKET_FLOOR + P.KEY_T)), m]
    if P.SOCKET_IN_SPHERE and P.SOCKET_STANDOFF > 0:
        ex, ey = pol(P.SOCKET_EAR_R, EAR_ANGLES[0])
        pl['socket_standoff'] = [((0, 0, 1), 0, (ex, ey, BASE_BOT - P.SOCKET_STANDOFF)), m]
    if LED_RING:
        pl['halo'] = [(X, 180, (0, 0, HALO_H)), m]
    return pl

