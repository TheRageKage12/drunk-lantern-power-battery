"""Check outgoing-wire corridors against the existing printed geometry. No exports are changed.
Run from the repository root with the CAD/board Python environment."""
import sys, math, json
sys.path.insert(0,'docs/review/protoboard')
import offboard as O, routing as R, assembly_guide as A
import cadquery as cq
from parts import top as T, sphere as S
from assembly import place
from pathlib import Path
# Current source solids, without exporting/changing any printed files.
solids={
 'top cap':T.build_top_cap(),
 'cap floor':T.build_cap_floor().translate((0,0,O.FLOOR)),
 'wall extension':T.build_wall_extension().translate((0,0,O.P.Z_SPHERE_CENTER)),
}
print('built cap solids',flush=True)
# Import unchanged printed floor/lock-wall models and apply their source placements.
for name in ['bay_floor','lock_wall','led_panel','glass_well']:
 solids[name]=place(cq.importers.importStep(str(O.CAD/'output'/f'{name}.step')),S.placements().get(name))
print('loaded sphere internals',flush=True)
for name in ['powerbank_envelope','buck_envelope']:
 from parts import electronics as E
 # These two envelopes are cheap to construct from current dimensions.
 if name=='powerbank_envelope':
  solids[name]=E.pack(E.box(-O.P.POWERBANK_W/2,O.P.POWERBANK_W/2,-O.P.POWERBANK_L/2,O.P.POWERBANK_L/2,O.P.PACK_BED_T,O.P.PACK_BED_T+O.P.POWERBANK_T))
 else:
  x,y=O.P.BUCK_CAP_XY;solids[name]=E.cap(E.box(x-O.P.BUCK_L/2,x+O.P.BUCK_L/2,y-O.P.BUCK_W/2,y+O.P.BUCK_W/2,O.P.BUCK_STANDOFF,O.P.BUCK_STANDOFF+O.P.BUCK_H))
# Conservative full screw-head/collar cylinders, including the one nearest H06.
for i,a in enumerate(T.CAP_FLOOR_SCREW_ANGLES):
 x,y=T._ang_point(T.CAP_FLOOR_SCREW_R,a)
 solids[f'floor screw {i}']=cq.Workplane('XY').workplane(offset=O.FLOOR).center(x,y).circle(O.P.THUMB_HEAD_D/2).extrude(O.P.THUMB_HEAD_L+O.P.THUMB_COLLAR_L)

def points(path):
 for a,b in zip(path,path[1:]):
  n=max(1,math.ceil(math.dist(a,b)/2))
  for i in range(n):yield [x+(y-x)*i/n for x,y in zip(a,b)]
 yield path[-1]

records=[]
# Cache expensive bounding boxes for the repeated clearance queries.
shapes=[(name,s,s.BoundingBox()) for name,wp in solids.items() for s in wp.solids().vals()]

def check(name,path,radius):
 minimum=(999,None,None)
 for p in points(path):
  v=cq.Vertex.makeVertex(*p)
  for sn,solid,bb in shapes:
   if any(p[k]<getattr(bb,axis+'min')-radius-1 or p[k]>getattr(bb,axis+'max')+radius+1 for k,axis in enumerate('xyz')):continue
   distance=solid.distance(v)
   if solid.isInside(cq.Vector(*p)):distance=0
   if distance<minimum[0]:minimum=(distance,sn,p)
 records.append(dict(name=name,required_radius_mm=radius,minimum_distance_mm=round(minimum[0],3),nearest=minimum[1],point=minimum[2],passed=minimum[0]>=radius))
 if minimum[0]<radius:print('FAIL',name,'radius',radius,minimum,flush=True)
 else:print('PASS',name,'nearest',minimum[:2],flush=True)
 return minimum[0]>=radius
ok=True
for w in R.plan():
 if w['b']:continue
 d=O.plan(w,A.route_length(w)['cut'])
 path=[O.board_to_cap(p) for p in R.cable_exit(w)]+d['path'][1:]
 path=[[x,y,z+O.FLOOR] for x,y,z in path]
 ok=check(w['id'],path,1.4) and ok
for w in O.installation()['lower_runs']:
 ok=check(w['name'],w['path'],2.5) and ok
ok=check('Hall branch',O.installation()['hall_path'],2.5) and ok
# Combined lock/pump/LED bundle in the shared cap-floor opening/neck corridor.
start=[*O.PORT[:2],O.FLOOR+6]
common=[start,[*O.PORT[:2],O.FLOOR-3],[-30.,-36.,O.P.Z_SPHERE_TOP+10]]
ok=check('Shared neck bundle',common,3.5) and ok
# Reserve space for four 150 mm service loops above the small lock connector.
x,y,z,w,d,h=O.SERVICE_COIL
coil=cq.Workplane('XY').box(w,d,h).translate((x,y,O.FLOOR+z+h/2)).val()
coil_gap=min((coil.distance(s),name) for name,s,bb in shapes)
coil_ok=coil_gap[0]>=1
records.append(dict(name='Pump/LED service-loop space',required_clearance_mm=1,minimum_distance_mm=round(coil_gap[0],3),nearest=coil_gap[1],passed=coil_ok))
ok=coil_ok and ok
print('Service-loop space',coil_gap,coil_ok,flush=True)
report=dict(passed=ok,sample_pitch_mm=2,board_wire_envelope_radius_mm=1.4,lower_bundle_radius_mm=2.5,checks=records,scope='Existing cap, floor, wall extension, bay floor, lock wall, LED panel, glass well, battery, buck and cap-floor screw heads. Insulated bundles may touch each other. Includes a 28 × 28 × 18 mm service-loop reserve. Does not certify delivered connector sizes or hand soldering.')
Path('docs/review/protoboard/offboard-clearance.json').write_text(json.dumps(report,indent=2)+'\n')
print('ALL CLEAR',ok,flush=True)
raise SystemExit(0 if ok else 1)
