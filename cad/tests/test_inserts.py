"""Check all insert bores against real CAD solids, rather than just parameter values, and every screw's shank
through the parts it joins, at their assembled positions.

The bore must be empty, its side wall continuous, and its blind end backed by
plastic. Entry-face curvature is excluded only for the first 0.15 mm of wall
(entries on the sphere's curved surface start where the full wall does).
"""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq
import params as P
from parts import base as B, sphere as S, socket as K, foot as F, top as T, bells as BL, handle as H
from assembly import place
from checks import inter_volume

solids = {'bay_floor': S.bay_floor().union(S.guide_boss()), 'socket_housing': K.housing_solid(),
          'foot': F.build_foot(), 'top_cap': T.build_top_cap(), 'cap_floor': T.build_cap_floor(),
          'bell_front': BL.bell_front(), 'bell_rear': BL.bell_rear(), 'curtain_clamp': BL.curtain_clamp()}
solids['sphere_front'], solids['sphere_rear'] = S.build_halves()
rows = []
def add(n, p, d): rows.append((n, p, d))
def pol(r, a): a = math.radians(a); return r * math.cos(a), r * math.sin(a)

for a in S.FLANGE_SCREW_ANGLES:
    x, z = pol(S.FLANGE_SCREW_R, a); add('sphere_front', (x, -P.FIT, z), (0, -1, 0))
solids['handle_pivot_right'], solids['handle_pivot_left'] = H.pivot(1), H.pivot(-1)
for sx, n in ((1, 'handle_pivot_right'), (-1, 'handle_pivot_left')):   # from the face against the sphere (curved entry)
    for y, z in S.PIVOT_SCREWS:
        x = math.sqrt(S.R_OUT ** 2 - y * y - z * z) + S.PIVOT_ENTRY
        add(n, (sx * x, y, z), (sx, 0, 0))
for a in F.JOINT_ANGLES:
    x, y = pol(F.face_r(F.SPIGOT_R), a); dx, dy = pol(-1, a); add('foot', (x, y, F.Z_DRUM_SCREWS), (dx, dy, 0))
pilots = []   # thumbscrew pilot holes (self-tapping, no insert); all blind, the heads inside the lantern
for z, angles in ((S.Z_LOWER_SCREWS, S.JOINT_ANGLES), (S.Z_UPPER_SCREWS, S.TOP_JOINT_ANGLES)):   # out into the collars
    for a in angles:
        pilots.append(('sphere_rear', (*pol(S.OPENING_ID / 2, a), z), (*pol(1, a), 0)))
for sign, n in ((-1, 'bell_front'), (1, 'bell_rear')):   # bell thumbscrews, out into the throats (bell frame)
    for a in S.BELL_LOCK_ANGLES[sign]:
        ab = S.bell_frame_angle(sign, a)
        pilots.append((n, (*pol(BL.bell_bore(sign), ab), S.lock_s(sign)), (*pol(1, ab), 0)))
for a in T.CAP_FLOOR_SCREW_ANGLES:
    pilots.append(('top_cap', (*pol(T.CAP_FLOOR_SCREW_R, a), T.Z_CAP_FLOOR0), (0, 0, -1)))
for mx, my in T.board_layout.MOUNTS: add('cap_floor', (*T.board_point(mx, my), T.BOARD_STANDOFF), (0, 0, -1))
add('bay_floor', (*S.GUIDE_SCREW, P.FLOOR), (0, 0, -1))
add('socket_housing', (*K.switch_screw_xy(), K.HOUSING_BOT), (0, 0, 1))

def volume(wp): return sum(s.Volume() for s in wp.solids().vals())
def cylinder(p, d, r, z0, z1, inner=None):
    plane = cq.Plane(origin=cq.Vector(*[p[i] + d[i] * z0 for i in range(3)]), normal=cq.Vector(*d))
    wp = cq.Workplane(plane).circle(r)
    if inner: wp = wp.circle(inner)
    return wp.extrude(z1 - z0)
fail = []
for i, (n, p, d) in enumerate(rows):
    solid = solids[n]
    bore = cylinder(p, d, 1.999, 0, 6.499)
    wall = cylinder(p, d, 3, .15, 6.45, 2.001)
    end = cylinder(p, d, 1.99, 6.501, 7.49)
    blocked = volume(bore.intersect(solid)); missing = volume(wall.cut(solid)); opened = volume(end.cut(solid))
    print(i + 1, n, 'blocked', round(blocked, 4), 'missing 1mm wall', round(missing, 4), 'missing end', round(opened, 4), flush=True)
    if max(blocked, missing, opened) > .02: fail.append((n, p, blocked, missing, opened))
assert len(rows) == 17, len(rows)
assert not fail, fail
# Thumbscrew pilots: open for the thread's length, 1.5 mm of plastic round them and 1 mm behind the tip.
for n, p, d in pilots:
    solid = solids[n]
    bore = cylinder(p, d, P.THUMB_PILOT / 2 - .001, 0, F.THUMB_PILOT_DEPTH - .001)
    wall = cylinder(p, d, P.THUMB_PILOT / 2 + 1.5, .15, F.THUMB_PILOT_DEPTH - .05, P.THUMB_PILOT / 2 + .001)
    end = cylinder(p, d, P.THUMB_PILOT / 2 - .01, F.THUMB_PILOT_DEPTH + .5 + .001, F.THUMB_PILOT_DEPTH + 1.5)
    v = (volume(bore.intersect(solid)), volume(wall.cut(solid)), volume(end.cut(solid)))
    print('pilot', n, [round(x, 4) for x in v])
    assert max(v) < .02, (n, p, v)
assert len(pilots) == 13
# Curtain clamp pilots in the rear bell's 4 mm lip: open for the screw's bite, 0.6 mm of skin left on the mouth face.
for a in BL.CLAMP_SCREW_ANGLES:
    p, d = (BL.CLAMP_SCREW_R * math.cos(math.radians(a)), -BL.CLAMP_SCREW_R * math.sin(math.radians(a)), BL.R_LIP_S), (0, 0, 1)
    v = (volume(cylinder(p, d, BL.CLAMP_PILOT / 2 - .001, 0, BL.CLAMP_PILOT_DEPTH - .001).intersect(solids['bell_rear'])),
         volume(cylinder(p, d, BL.CLAMP_PILOT / 2 - .01, BL.CLAMP_PILOT_DEPTH + .1, BL.R_LIP_T - .1).cut(solids['bell_rear'])))
    print('clamp pilot', [round(x, 4) for x in v])
    assert max(v) < .02, (a, v)
# Regression controls: detect the old 2.7 mm bore and a shallow 2 mm floor.
p, d = (0, 0, 0), (0, 0, 1)
old_bore = cylinder(p, d, 4, 0, 8).cut(cylinder(p, d, 1.35, -.1, 6.5))
assert volume(cylinder(p, d, 1.999, 0, 6.499).intersect(old_bore)) > 1
thin_floor = cylinder(p, d, 4, 0, 2).cut(cylinder(p, d, 2, -.1, 2.1))
assert volume(cylinder(p, d, 3, .15, 6.45, 2.001).cut(thin_floor)) > 1

# ---------------------------------------------------------------- screw shanks at the assembled positions
mods = (B, S, F, T, BL, H)
placed = {}
envelopes = {}
from parts import electronics as E
for m in mods + (E,):
    built, pl = m.build(), m.placements()
    for n, wp in built.items():
        (envelopes if n.endswith('_envelope') else placed)[n] = place(wp, pl.get(n))
ZC = P.Z_SPHERE_CENTER


def clear_of_all(solid, label, skip=()):
    """A screw head (or knob) must not hit any part or envelope."""
    for n_, wp in list(placed.items()) + list(envelopes.items()):
        if n_ in skip or n_ in ('fist_envelope', 'hand_path_envelope', 'glass_path_envelope'):
            continue
        assert inter_volume(solid, wp) < .01, (label, 'hits', n_)


def knob(p, d, r_floor):
    """Thumbscrew collar (in its counterbore) and knurled head, from the counterbore floor along d."""
    c = cylinder(p, d, P.THUMB_COLLAR_D / 2, .05, P.THUMB_COLLAR_L)
    return c.union(cylinder(p, d, P.THUMB_HEAD_D / 2, P.THUMB_COLLAR_L + .05, P.THUMB_COLLAR_L + P.THUMB_HEAD_L))
shanks = []   # (label, start point, direction, length, parts it passes through)
for sign, n, half in ((-1, 'bell_front', 'sphere_front'), (1, 'bell_rear', 'sphere_rear')):   # bell thumbscrews
    for a in S.BELL_LOCK_ANGLES[sign]:
        r_floor = S.collar_dims(sign)[1] - P.THUMB_WEB        # counterbore floor: the collar bears here
        x, z = pol(r_floor, a); dx, dz = pol(1, a)
        p = (x, sign * S.lock_s(sign), ZC + z)
        shanks.append(('bell thumbscrew', p, (dx, 0, dz), P.THUMB_THREAD_L, (n, half)))
        clear_of_all(knob(p, (-dx, 0, -dz), r_floor), 'bell thumbscrew head')
for sx, n in ((1, 'handle_pivot_right'), (-1, 'handle_pivot_left')):   # M3x12 from inside the sphere
    for y, z in S.PIVOT_SCREWS:
        half = 'sphere_front' if y < 0 else 'sphere_rear'
        p = (sx * S.pivot_seat_x(y, z), y, ZC + z)
        shanks.append(('pivot', p, (sx, 0, 0), H.PIVOT_SCREW_L, (n, half)))
        clear_of_all(cylinder(p, (-sx, 0, 0), P.M3_HEAD_D / 2 - .3, .05, 3.0), 'pivot screw head')
for a in B.BASE_JOINT_ANGLES:   # M3x8 through the drum's band into the foot
    shanks.append(('drum-foot', (*pol(B.R_MAX - B.BASE_JOINT_CBORE_DEPTH, a), B.BASE_JOINT_Z), (*pol(-1, a), 0), 8, ('base', 'foot')))
for a, z, part, r_out in [(a, S.Z_LOWER_SCREWS, 'foot', F.RISER_R) for a in S.JOINT_ANGLES] + \
                         [(a, S.Z_UPPER_SCREWS, 'top_cap', T.PLUG_R) for a in S.TOP_JOINT_ANGLES]:
    # thumbscrews from inside the neck: collar on the counterbore floor, thread out through the web into the collar
    r_floor = r_out - P.THUMB_WEB
    p = (*pol(r_floor, a), ZC + z)
    shanks.append(('thumbscrew ' + part, p, (*pol(1, a), 0), P.THUMB_THREAD_L, ('sphere_front', 'sphere_rear', part)))
    clear_of_all(knob(p, (*pol(-1, a), 0), r_floor), 'thumbscrew head ' + part)
for a in T.CAP_FLOOR_SCREW_ANGLES:   # thumbscrews down through the cap floor; heads on top among the electronics
    p = (*pol(T.CAP_FLOOR_SCREW_R, a), T.Z_CAP_FLOOR)
    shanks.append(('cap floor', p, (0, 0, -1), P.THUMB_THREAD_L, ('cap_floor', 'top_cap')))
    clear_of_all(knob(p, (0, 0, 1), 0), 'cap floor thumbscrew head')
for a in BL.CLAMP_SCREW_ANGLES:   # M3x8 from the clamp's back (inside the bell) into the lip's pilots
    x, z = pol(BL.CLAMP_SCREW_R, a)
    p = (x, BL.R_LIP_S - BL.CURTAIN_T - BL.CLAMP_T + BL.CLAMP_CB, ZC + z)
    shanks.append(('curtain clamp', p, (0, 1, 0), 8, ('curtain_clamp',)))
    clear_of_all(cylinder(p, (0, -1, 0), P.M3_HEAD_D / 2 - .3, .05, 3.0), 'clamp screw head')
for a in B.BASE_JOINT_ANGLES:   # the green caps fit over the heads, flush with the band
    p = (*pol(B.R_MAX - B.DRUM_CAP_T, a), B.BASE_JOINT_Z)
    cap = cylinder(p, (*pol(1, a), 0), B.DRUM_CAP_D / 2, 0, B.DRUM_CAP_T)
    assert inter_volume(cap, placed['base']) < .01, ('drum cap', a)
for phi in H.JOINTS:   # M3x10 through each lap
    for x, z in H.screw_points(phi):
        shanks.append(('handle lap', (x, -P.HANDLE_SECTION_T / 2 + H.LAP_CB, ZC + z), (0, 1, 0), 8, [n for n in placed if n.startswith('handle_')]))
bad = []
for label, p0, d, length, names in shanks:
    shank = cylinder(p0, d, 1.4, 0, length)
    for n in names:
        v = inter_volume(shank, placed[n])
        if v > .01:
            bad.append((label, n, round(v, 2)))
print(f'{len(shanks)} screw shanks checked through their parts')
assert not bad, bad
# negative control: a shank 3 mm off its holes must be caught
p0 = shanks[0][1]
assert inter_volume(cylinder((p0[0] + 3, p0[1], p0[2]), (0, 0, 1), 1.4, 0, 10), placed['bell_front']) > 1

# Bells: they clear the sphere in place, and with the thumbscrews out they slide straight off their collars.
for sign, n, half in ((-1, 'bell_front', 'sphere_front'), (1, 'bell_rear', 'sphere_rear')):
    bell, shell = placed[n], placed[half]
    assert inter_volume(bell, shell) < .01, n
    for d in (3, 6, 12):
        assert inter_volume(bell.translate((0, sign * d, 0)), shell) < .01, (n, d)
print('BELLS OK: in place and straight off')

# Insert boss under the bay floor vs the foot's notch, at the real assembly height.
floor = solids['bay_floor'].translate((0, 0, S.Z_ASM + S.BAY_FLOOR_Z))
assert inter_volume(floor, placed['foot']) < .01, 'Nozzle insert boss hits the foot riser'
# The housing bore, bracket hole and base slot must remain aligned. Test the
# screw shank through the entire stack in the unmirrored socket frame.
sx, sy = K.switch_screw_xy()
shank = cylinder((sx, sy, K.BASE_BOT), (0, 0, 1), 1.49, 0, K.BASE_T + 3)
base = K.base_solid()
bracket = K.bracket_solid().rotate((0, 0, 0), (0, 0, 1), K.LEVER_TIP_ANGLE - 90)
bx, by = K.frame_point(K.BRACKET_T_CENTRE, K.SWITCH_N0 + 3.5, K.LEVER_TIP_ANGLE, K.LEVER_REST_R)
bracket = bracket.translate((bx, by, K.HOUSING_BOT - K.BRACKET_T))
assert inter_volume(shank, base) < .01
assert inter_volume(shank, bracket) < .01
assert inter_volume(bracket, solids['socket_housing']) < .01
print(f'INSERT FIT OK: {len(rows)} bores at 4 x 6.5 mm, 1 mm side/end backing; {len(shanks)} screw shanks aligned; nozzle notch and switch screw alignment')
