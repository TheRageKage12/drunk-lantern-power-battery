"""Connectivity, physical failure cases and completeness of the soldering sequence."""
import copy,json,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parent))
import layout as L, mechanical as M, routing as R, assembly_guide as A
from redesign.check import check,segments_gap

@pytest.fixture(scope='module')
def routes():return R.plan()
@pytest.fixture(scope='module')
def data(routes):return A.make_data(copy.deepcopy(routes))

def test_all_nets_and_separate_load_returns(routes):
 r=R.validate(routes);assert r['nets']==16 and r['dedicated_wire_holes']==61
 assert r['front_height_reserve_mm']>=7

def test_short_and_duplicate_wire_hole_rejected():
 d=copy.deepcopy(L.DESIGN);d['edges'][0]['net']='GND'
 with pytest.raises(AssertionError):check(d)
 d=copy.deepcopy(L.DESIGN);d['edges'][1]['anchor_a']=d['edges'][0]['anchor_a']
 with pytest.raises(AssertionError):check(d)

def test_wire_collision_rejected(routes):
 bad=copy.deepcopy(routes);bad[0]['path3d'][10]=bad[1]['path3d'][10];bad[0]['path']=[p[:2] for p in bad[0]['path3d']]
 with pytest.raises(AssertionError):R.validate(bad)

def test_wrong_diameter_and_height_rejected(routes):
 for key,value in [('od',1.2),('depth',9.5)]:
  bad=copy.deepcopy(routes);bad[0][key]=value
  with pytest.raises(AssertionError):R.validate(bad)

def test_component_and_mount_collisions_rejected():
 b=M.bounds();b['R1']=b['MCU']
 with pytest.raises(AssertionError):M.validate(b)
 b=M.bounds();b['R1']=(16,15,4,4,0,3)
 with pytest.raises(AssertionError):M.validate(b)

def test_all_solder_points_once_per_wire(data):
 for w in data['routes']:
  solder=[j['pad'] for s in data['steps'] for j in s.get('joints',[]) if j['owner']==w['id']]
  assert solder==w['anchors']
  assert w['length']['cut']>=w['length']['formed']
 assert len(data['routes'])==37

def test_prepared_wire_reaches_both_joints_without_stripping_the_loop(data):
 for w in data['routes']:
  if not w.get('tails'):continue
  for t in w['tails']:
   assert t['prepare_strip_mm']>=R.length(t['path'])+2.3
  if len(w['tails'])==2:
   covered=w['length']['cut']-sum(t['prepare_strip_mm'] for t in w['tails'])
   route=R.length(w['path3d'])
   assert route<=covered<route+1
   assert covered==w['covered_mm']

def test_weaving_pairs_fitted_before_any_joint(data):
 routes={w['id']:w for w in data['routes']}
 for group in data['report']['assembly_groups']:
  fitting=[routes[n]['prepare'] for n in group]
  soldering=[routes[n]['joints'][0] for n in group]
  assert max(fitting)<min(soldering)
  assert len(set(fitting+soldering))==2*len(group)
  for name in group:
   w=routes[name];fit=data['steps'][w['prepare']];solder=data['steps'][w['joints'][0]]
   assert fit['wire_stage']=='fit' and fit['wires']==[name] and not fit['joints']
   assert solder['wire_stage']=='solder' and solder['wires']==[name]
   assert {j['owner'] for j in solder['joints']}=={name}
   if len(group)==2:assert fit['text'].startswith('Fit both loops together before soldering either wire.')
 assert len(data['report']['preformed_pairs'])==4

def test_every_wire_action_is_a_numbered_navigable_step(data):
 assert [s['index'] for s in data['steps']]==list(range(len(data['steps'])))
 for w in data['routes']:
  if not w.get('tails'):continue
  appearances=[s for s in data['steps'] if w['id'] in s.get('wires',[])]
  assert [s['wire_stage'] for s in appearances]==['fit','solder']
  assert all(w['id'] in s['title'] for s in appearances)

def test_components_are_complete_tasks_and_no_joints_lost(data):
 assert data['steps'][0]['ref']=='R1'
 for p in data['parts']:
  if p['side']=='external':continue
  step=data['steps'][p['fit']]
  assert step['ref']==p['ref'] and step['kind']=='component'
  assert step['pads']==p['pins'] and p['solder']==[step['index']]
  assert [j['pad'] for s in data['steps'] for j in s.get('joints',[]) if j['owner']==p['ref']]==p['pins']
 assert sum(len(s.get('joints',[])) for s in data['steps'])==182
 assert len(data['steps'])<100

def test_component_identification_matches_board_assignments(data):
 for part in data['parts']:
  info=part['identity']
  assert info['kind'] and info['name'] and info['note']
  assert {e['pad'] for e in info['ends']}==set(part['pins'])
 for ref in ['D1','D3']:
  info=next(p for p in data['parts'] if p['ref']==ref)['identity']
  assert info['name']=='NTE585 diode'
  assert info['ends']==[{'label':'Unstriped end','pad':L.PINS[ref+'.1']['pad']},
                        {'label':'Striped end','pad':L.PINS[ref+'.2']['pad']}]
 assert A.component_identity('U1')['kind']=='socket'

def test_resistor_colours_decode_to_circuit_values(data):
 digits=['black','brown','red','orange','yellow','green','blue','violet','grey','white']
 values={p['ref']:float(p['value'][:-1])*1000 for p in L.PARTS if p['kind']=='resistor'}
 for part in data['parts']:
  if part['ref'] not in values:continue
  variants=part['identity']['band_variants']
  assert {v['tolerance'] for v in variants}=={2,5}
  for variant in variants:
   a,b,m,t=variant['bands']
   assert (10*digits.index(a)+digits.index(b))*10**digits.index(m)==values[part['ref']]
   assert {'gold':5,'red':2}[t]==variant['tolerance']

def test_capacitor_wires_include_both_connections(data):
 for w in data['routes']:
  if w['surface']!='rear':continue
  s=data['steps'][w['prepare']]
  assert s['pads']==w['anchors'] and s['points']==[w['path3d'][-1]]
  assert 'heat-shrink' in s['text']

def test_earlier_joints_preserved_for_reheating(data):
 owners={}
 for s in data['steps']:
  expected={owner for pad in s['pads'] for owner in owners.get(pad,[])}
  assert set(s['previous'])==expected
  for j in s.get('joints',[]):owners.setdefault(j['pad'],[]).append(j['owner'])

def test_underside_parts_after_wires(data):
 last=max(max(w['joints']) for w in data['routes'] if w['surface']=='front')
 assert all(p['fit']>last for p in data['parts'] if p['side']=='rear')
 assert {p['ref'] for p in data['parts']}=={ref.split('.')[0] for ref in L.PINS}

def test_cable_exits_clear_other_wires_and_capacitor_leads(routes):
 for a in routes:
  if a['b']:continue
  out=R.cable_exit(a)
  for b in routes:
   if a['id']!=b['id']:assert segments_gap(out,b['path3d'])>=2.3
  for p in L.DESIGN['pigtails']:
   rear=[[x,y,-1.2-z] for x,y,z in p['path']]
   assert segments_gap(out,rear)>=2.3

def test_cut_stock_accounts_for_3d_and_rear_tails(routes):
 for w in routes:
  cut=A.route_length(w)
  assert cut['cut']>=R.length(w['path3d'])+R.length(R.cable_exit(w))+sum(R.length(t['path'])+2.1 for t in w['tails'])+6-1e-6

def test_hardware_and_harness_are_explicit(data):
 assert M.BOARD_SPACER==4.8 and M.REAR_GAP==14.8
 assert sorted(len(j['members']) for j in L.DESIGN['harness'])==[3,5,6]
 assert 'M3×10' in ' '.join(s['text'] for s in data['steps'])


def test_rear_lead_and_iron_collisions_rejected():
 from redesign.rear import check_rear
 from redesign.check import mm
 d=copy.deepcopy(L.DESIGN);d['leads']['C1.1']=d['leads']['C3.1']
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)
 d=copy.deepcopy(L.DESIGN)
 # A centred vertical approach runs into the target lead beyond the contact region.
 d['tool_access']['R4.1']=[[99,0,0]]
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)


def test_metal_nuts_and_reduced_gap_rejected():
 from redesign.rear import check_rear
 from redesign.check import mm
 d=copy.deepcopy(L.DESIGN);d['hardware']['rear_gap']=10
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)
 d=copy.deepcopy(L.DESIGN);d['hardware']['mounts'][0]=list(mm('H04'))
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)


def test_capacitor_wire_crossing_rejected():
 from redesign.rear import check_rear
 from redesign.check import mm
 d=copy.deepcopy(L.DESIGN);d['pigtails'][1]['path']=d['pigtails'][0]['path']
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)


def test_front_routes_inside_stepped_enclosure_reserve():
 from shapely.geometry import Polygon,Point
 outline=Polygon(L.DESIGN['hardware']['front_outline'])
 for wire in L.DESIGN['edges']:
  for x,y,z in wire['path']:
   assert outline.contains(Point(x,y)) and outline.boundary.distance(Point(x,y))>=.9
 # The battery-strap corner is intentionally excluded, not silently reserved twice.
 assert not outline.contains(Point(15,53))
 assert outline.contains(Point(60,53))


def test_rear_component_leads_and_floor_allowance(routes):
 report=R.validate(routes)
 assert report['maximum_rear_extent_mm']<=11
 assert M.REAR_GAP-.5-11>=3.3-1e-6
 for path in L.DESIGN['leads'].values():assert R.length(path)<=25
 # Fixed mounting geometry and hardware are explicit in the guide data.
 assert L.DESIGN['hardware']['nut_count']==8
 assert L.DESIGN['hardware']['screw']=='M3x10'


def test_rear_order_preserves_iron_access(data):
 from redesign.rear import check_rear
 from redesign.check import mm
 sequence=[p['ref'] for p in data['parts'] if p['side']=='rear']
 assert sequence==L.DESIGN['rear_order']
 d=copy.deepcopy(L.DESIGN);d['rear_order']=['C3','C1','R3','R4']
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)
