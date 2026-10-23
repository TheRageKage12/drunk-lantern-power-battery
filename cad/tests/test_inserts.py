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
for sx in (-1, 1):
    for y, z in S.PIVOT_SCREWS:
        x = math.sqrt(S.R_OUT ** 2 - y * y - z * z) - S.PIVOT_ENTRY
        add('sphere_front' if y < 0 else 'sphere_rear', (sx * x, y, z), (-sx, 0, 0))
for n, r, up in (('bell_front', S.FRONT_BELL_SCREW_R, 1), ('bell_rear', S.REAR_BELL_SCREW_R, -1)):
    for a in S.BELL_SCREW_ANGLES:
        x, y = pol(r, a); add(n, (x, up * y, BL.insert_entry(r)), (0, 0, 1))
for a in BL.CLAMP_SCREW_ANGLES: add('curtain_clamp', (*pol(BL.CLAMP_SCREW_R, a), 0), (0, 0, 1))
for a in F.JOINT_ANGLES:
    for r, z in ((F.SPIGOT_R, F.Z_DRUM_SCREWS), (F.RISER_R, F.Z_SPHERE_SCREWS)):
        x, y = pol(F.face_r(r), a); dx, dy = pol(-1, a); add('foot', (x, y, z), (dx, dy, 0))
for a in T.JOINT_ANGLES:
    x, y = pol(T.face_r(T.PLUG_R), a); dx, dy = pol(-1, a); add('top_cap', (x, y, T.Z_SPHERE_SCREWS), (dx, dy, 0))
for a in T.CAP_FLOOR_SCREW_ANGLES: add('top_cap', (*pol(T.CAP_FLOOR_SCREW_R, a), T.Z_CAP_FLOOR0), (0, 0, -1))
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
assert len(rows) == 35, len(rows)
assert not fail, fail
# Regression controls: detect the old 2.7 mm bore and a shallow 2 mm floor.
p, d = (0, 0, 0), (0, 0, 1)
old_bore = cylinder(p, d, 4, 0, 8).cut(cylinder(p, d, 1.35, -.1, 6.5))
assert volume(cylinder(p, d, 1.999, 0, 6.499).intersect(old_bore)) > 1
thin_floor = cylinder(p, d, 4, 0, 2).cut(cylinder(p, d, 2, -.1, 2.1))
assert volume(cylinder(p, d, 3, .15, 6.45, 2.001).cut(thin_floor)) > 1

# ---------------------------------------------------------------- screw shanks at the assembled positions
mods = (B, S, F, T, BL, H)
placed = {}
for m in mods:
    built, pl = m.build(), m.placements()
    for n, wp in built.items():
        if not n.endswith('_envelope'):
            placed[n] = place(wp, pl.get(n))
ZC = P.Z_SPHERE_CENTER
shanks = []   # (label, start point, direction, length, parts it passes through)
for a in S.BELL_SCREW_ANGLES:   # M3x12 from the pads inside the sphere into the bells
    x, z = pol(S.FRONT_BELL_SCREW_R, a)
    shanks.append(('front bell', (x, -S.FRONT_PAD_Y, ZC + z), (0, -1, 0), 12, ('sphere_front', 'bell_front')))
    x, z = pol(S.REAR_BELL_SCREW_R, a)
    shanks.append(('rear bell', (x, S.REAR_PAD_Y, ZC + z), (0, 1, 0), 12, ('sphere_rear', 'bell_rear')))
for sx, n in ((1, 'handle_pivot_right'), (-1, 'handle_pivot_left')):   # M3x20 from the pivot's counterbore
    for y, z in S.PIVOT_SCREWS:
        shanks.append(('pivot', (sx * (H.PIVOT_X1 - 3.0), y, ZC + z), (-sx, 0, 0), 20, (n, 'sphere_front' if y < 0 else 'sphere_rear')))
for a in B.BASE_JOINT_ANGLES:   # M3x8 through the drum's band into the foot
    shanks.append(('drum-foot', (*pol(B.R_MAX - B.BASE_JOINT_CBORE_DEPTH, a), B.BASE_JOINT_Z), (*pol(-1, a), 0), 8, ('base', 'foot')))
for a, z, part in [(a, S.Z_LOWER_SCREWS, 'foot') for a in S.JOINT_ANGLES] + [(a, S.Z_UPPER_SCREWS, 'top_cap') for a in S.TOP_JOINT_ANGLES]:
    r0 = math.sqrt(S.R_OUT ** 2 - z * z) - 2.0          # the sphere's counterbore floor
    shanks.append(('sphere-' + part, (*pol(r0, a), ZC + z), (*pol(-1, a), 0), 10, ('sphere_front', 'sphere_rear', part)))
for a in T.CAP_FLOOR_SCREW_ANGLES:
    shanks.append(('cap floor', (*pol(T.CAP_FLOOR_SCREW_R, a), T.Z_CAP_FLOOR), (0, 0, -1), 8, ('cap_floor', 'top_cap')))
for a in BL.CLAMP_SCREW_ANGLES:   # countersunk M3x10 from the rear bell's mouth face into the clamp
    x, z = pol(BL.CLAMP_SCREW_R, a)
    shanks.append(('curtain clamp', (x, BL.R_MOUTH, ZC + z), (0, -1, 0), 10, ('bell_rear', 'curtain_clamp')))
for phi in H.JOINTS:   # M3x10 through each lap
    for x, z in H.screw_points(phi):
        shanks.append(('handle lap', (x, -P.HANDLE_SECTION_T / 2, ZC + z), (0, 1, 0), 10, [n for n in placed if n.startswith('handle_')]))
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
assert inter_volume(cylinder((p0[0] + 3, p0[1], p0[2]), (0, -1, 0), 1.4, 0, 12), placed['bell_front']) > 1

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
