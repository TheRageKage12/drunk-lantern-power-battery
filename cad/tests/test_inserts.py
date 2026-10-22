"""Check all insert bores against real CAD solids, rather than just parameter values.

The bore must be empty, its side wall continuous, and its blind end backed by
plastic. Entry-face curvature is excluded only for the first 0.15 mm of wall.
"""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq
import params as P
from parts import base as B, sphere as S, dishes as D, socket as K
solids={'base_tray':B.build_tray(),'base_deck':B.build_deck(), 'dish_lower':D.build_dish_lower(), 'dish_upper':D.build_dish_upper(), 'bay_floor':S.bay_floor().union(S.guide_boss()), 'socket_housing':K.housing_solid()}
solids['sphere_front'],solids['sphere_rear']=S.build_halves()
rows=[]
def add(n,p,d): rows.append((n,p,d))
def pol(r,a): a=math.radians(a); return r*math.cos(a),r*math.sin(a)
for x,y in B.PILLAR_INSERTS: add('base_tray',(x,y,B.DECK_Z0),(0,0,-1))
for x,y in B.board_layout.MOUNTS:
    px,py=B.EPANEL_R+B.EPANEL_T/2+B.EPANEL_PAD_PROUD,x-P.PERFBOARD_W/2
    a=math.radians(B.EPANEL_ANGLE)
    add('base_deck',(px*math.cos(a)-py*math.sin(a),px*math.sin(a)+py*math.cos(a),B.DECK_T+P.PERFBOARD_BOTTOM_GAP+P.PERFBOARD_H-y),(-math.cos(a),-math.sin(a),0))
for a in D.JOINT_BOSS_ANGLES:
    for n,r,z in [('dish_lower',D.SPIGOT_OD/2,D.Z_BASE_JOINT_SCREWS-D.LOWER_PRINT_TO_ASSEMBLY_DZ),('dish_lower',D.LOCATING_RING_OD/2,D.Z_SPHERE_LOWER_SCREWS-D.LOWER_PRINT_TO_ASSEMBLY_DZ),('dish_upper',D.LOCATING_RING_OD/2,D.Z_SPHERE_UPPER_SCREWS-D.UPPER_PRINT_TO_ASSEMBLY_DZ)]:
        x,y=pol(r,a); dx,dy=pol(-1,a); add(n,(x,y,z),(dx,dy,0))
for a in D.SOCKET_BOLT_ANGLES: add('dish_upper',(*pol(P.SOCKET_BOLT_CIRCLE/2,a),D.U_Z_FLOOR1-D.SOCKET_COUNTERBORE_DEPTH),(0,0,-1))
for a in P.CURTAIN_SCREW_ANGLES: add('dish_upper',(*pol(P.CURTAIN_R,a),D.U_Z_PLUG0),(0,0,1))
for a in S.FLANGE_SCREW_ANGLES:
    x,z=pol(S.FLANGE_SCREW_R,a); add('sphere_front',(x,-P.FIT,z),(0,-1,0))
for s in (-1,1): add('sphere_rear',(s*(S.LEG_X-S.BOSS_POCKET_W/2),S.HANDLE_PLANE_Y,S.BOSS_SCREW_Z),(-s,0,0))
add('bay_floor',(*S.GUIDE_SCREW,P.FLOOR),(0,0,-1))
add('socket_housing',(*K.switch_screw_xy(),K.HOUSING_BOT),(0,0,1))
def volume(wp): return sum(s.Volume() for s in wp.solids().vals())
def cylinder(p,d,r,z0,z1,inner=None):
    plane=cq.Plane(origin=cq.Vector(*[p[i]+d[i]*z0 for i in range(3)]),normal=cq.Vector(*d))
    wp=cq.Workplane(plane).circle(r)
    if inner: wp=wp.circle(inner)
    return wp.extrude(z1-z0)
fail=[]
for i,(n,p,d) in enumerate(rows):
    solid=solids[n]
    bore=cylinder(p,d,1.999,0,6.499)
    wall=cylinder(p,d,3,.15,6.45,2.001)
    end=cylinder(p,d,1.99,6.501,7.49)
    blocked=volume(bore.intersect(solid)); missing=volume(wall.cut(solid)); opened=volume(end.cut(solid))
    print(i+1,n, 'blocked',round(blocked,4),'missing 1mm wall',round(missing,4),'missing end',round(opened,4),flush=True)
    if max(blocked,missing,opened)>.02: fail.append((n,p,blocked,missing,opened))
assert len(rows) == 32
assert not fail, fail
# Regression controls: detect the old 2.7 mm bore and a shallow 2 mm floor.
p, d = (0, 0, 0), (0, 0, 1)
old_bore = cylinder(p, d, 4, 0, 8).cut(cylinder(p, d, 1.35, -.1, 6.5))
assert volume(cylinder(p, d, 1.999, 0, 6.499).intersect(old_bore)) > 1
thin_floor = cylinder(p, d, 4, 0, 2).cut(cylinder(p, d, 2, -.1, 2.1))
assert volume(cylinder(p, d, 3, .15, 6.45, 2.001).cut(thin_floor)) > 1

# Check the new boss and matching dish relief at the real assembly height.
from checks import inter_volume
floor = solids['bay_floor'].translate((0, 0, S.Z_ASM + S.BAY_FLOOR_Z))
dish = solids['dish_lower'].translate((0, 0, D.LOWER_PRINT_TO_ASSEMBLY_DZ))
assert inter_volume(floor, dish) < .01, 'Nozzle insert boss hits lower dish'
# The housing bore, bracket hole and base slot must remain aligned. Test the
# screw shank through the entire stack in the unmirrored socket frame.
sx, sy = K.switch_screw_xy()
shank = cylinder((sx,sy,K.BASE_BOT),(0,0,1),1.49,0,K.BASE_T+3)
base = K.base_solid()
bracket = K.bracket_solid().rotate((0,0,0),(0,0,1),K.LEVER_TIP_ANGLE-90)
bx,by=K.frame_point(K.BRACKET_T_CENTRE,K.SWITCH_N0+3.5,K.LEVER_TIP_ANGLE,K.LEVER_REST_R)
bracket=bracket.translate((bx,by,K.HOUSING_BOT-K.BRACKET_T))
assert inter_volume(shank,base) < .01
assert inter_volume(shank,bracket) < .01
assert inter_volume(bracket,solids['socket_housing']) < .01
print('INSERT FIT OK: 32 bores at 4 x 6.5 mm, 1 mm side/end backing; nozzle relief and switch screw alignment')
