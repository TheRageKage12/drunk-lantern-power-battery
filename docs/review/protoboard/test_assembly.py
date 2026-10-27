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
  solder=[s['pad'] for s in data['steps'] if s.get('wire')==w['id'] and s['kind']=='solder']
  assert solder==w['anchors']
  assert w['length']['cut']>=w['length']['formed']
 assert len(data['routes'])==37

def test_weaving_pairs_fitted_before_any_joint(data):
 routes={w['id']:w for w in data['routes']}
 for group in data['report']['assembly_groups']:
  assert max(routes[n]['prepare'] for n in group)<min(min(routes[n]['joints']) for n in group)
 assert len(data['report']['preformed_pairs'])==4

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
 assert M.BOARD_SPACER==20 and M.REAR_GAP==30
 assert sorted(len(j['members']) for j in L.DESIGN['harness'])==[3,5,6]
 assert 'M3×25' in ' '.join(s['text'] for s in data['steps'])


def test_rear_lead_and_iron_collisions_rejected():
 from redesign.rear import check_rear
 from redesign.check import mm
 d=copy.deepcopy(L.DESIGN);d['leads']['C1.1']=d['leads']['C3.1']
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)
 d=copy.deepcopy(L.DESIGN)
 # A normal approach hits R3's upright body; cached passing numbers cannot hide it.
 d['tool_access']['R3.1']=[[99,0,0]]
 with pytest.raises(AssertionError):check_rear(d,mm,segments_gap)
