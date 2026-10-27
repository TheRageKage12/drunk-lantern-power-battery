"""Electrical topology, access order and physical negative controls."""
import json
import math
from collections import Counter,defaultdict
from pathlib import Path
import pytest
from shapely.geometry import LineString,Point
import assembly_guide as A
import layout as L
import mechanical as M
import routing as R

@pytest.fixture(scope='module')
def guide():
    saved=json.loads((Path(__file__).parent/'routing.json').read_text())
    assert saved==json.loads(json.dumps(R.plan())), 'Regenerate the reference routes'
    return A.make_data(saved)

def test_every_lead_and_anchor_once(guide):
    solder=[s for s in guide['steps'] if s['kind']=='solder']
    leads=[s['pad'] for s in solder if 'wire' not in s]
    expected={p['pad'] for key,p in L.PINS.items() if '.' in key and not key.startswith('BUS.')}
    assert set(leads)==expected and len(leads)==len(expected)==60
    for w in guide['routes']:
        assert [s['pad'] for s in solder if s.get('wire')==w['id']]==w['anchors']
    assert len(solder)==320
    assert max(s['index'] for s in solder if 'wire' not in s)<min(s['index'] for s in solder if 'wire' in s)

def test_access_and_crossing_order(guide):
    routes=guide['routes'];by_id={w['id']:w for w in routes}
    last_joint={s['pad']:s['index'] for s in guide['steps'] if s.get('pad')}
    covered=[]
    for w in routes:
        assert w['prepare']<min(w['joints'])<=max(w['joints'])==w['check']
        for other in w['earlier_crossings']:
            assert by_id[other]['check']<w['prepare']
            assert by_id[other]['depth']<w['depth']
        for pad in last_joint.keys()-set(w['anchors']):
            if LineString(w['path']).distance(Point(L.mm(pad))) < w['od']/2+1.4-1e-6:
                assert last_joint[pad]<w['prepare'],(w['id'],pad)
                covered.append((w['id'],pad))
    assert covered
    # This pair requires departing from simple low-to-high ordering for access.
    assert by_id['W97']['check']<by_id['W82']['prepare']
    assert any(w['earlier_crossings'] for w in routes)

def test_shared_history(guide):
    visits={}
    for s in guide['steps']:
        if s.get('pad'):
            assert s['previous']==visits.get(s['pad'],[])
            visits.setdefault(s['pad'],[]).append(s.get('ref',s.get('wire',s['title'])))

def test_lengths_follow_curves(guide):
    for w in guide['routes']:
        tails=0 if w['bare'] else M.BOARD_THICKNESS if not w['b'] else 2*(M.BOARD_THICKNESS+.55)
        assert w['length']['cut']==math.ceil(R.length(w['path3d'])+tails+(4 if w['bare'] else 6))
        if w['b'] and not w['bare'] and not(w.get('offset_a') or w.get('offset_b')):
            expected=math.dist(L.mm(w['a']),L.mm(w['b']))+2*w['depth']-1.1+(math.pi-4)*4
            assert abs(R.length(w['path3d'])-expected)<.002
        assert w['colour'] in {'red','black','white','blue','yellow','green'}
    assert next(w for w in guide['routes'] if w['id']=='H07')['length']['cut']<100

def test_hardware_and_hand_assembly_allowances(guide):
    assert M.PRINTED_POST_HEIGHT==10 and M.BOARD_SPACER==6 and M.REAR_GAP==16
    assert guide['diameter']==1.8 and guide['report']['remaining_floor_clearance_mm']>=2
    assert guide['report']['maximum_rear_extent_mm']==12.9
    assert M.JOINT_HEIGHT==2.5
    assert guide['report']['minimum_insulated_gap_mm']>=1.18
    counts=Counter(p for w in guide['routes'] if not w['bare'] for p in w['anchors'])
    assert max(counts.values())==1
    component={p['pad'] for k,p in L.PINS.items() if not k.startswith('BUS.')}
    for w in guide['routes']:
        if not w['bare'] and w['b']:assert not(set(w['anchors'])&component)
        if w['bare']:
            assert all(math.dist(L.mm(a),L.mm(b))<=7.62+.001 for a,b in zip(w['anchors'],w['anchors'][1:]))
        for points,diameter in R.pieces(w):
            if diameter==R.OD:assert R.minimum_radius(points[1:-1])>=3.99

def test_ground_returns_do_not_share_logic_track():
    graph=defaultdict(set)
    for w in L.WIRES:
        pads=w.get('pads',w['anchors'])
        for a,b in zip(pads,pads[1:]):graph[a].add(b);graph[b].add(a)
    def reachable(start,removed=()):
        seen=set();todo=[start]
        while todo:
            node=todo.pop()
            if node in seen or node in removed:continue
            seen.add(node);todo.extend(graph[node]-seen)
        return seen
    source1=L.PINS['Q1.S']['pad'];source2=L.PINS['Q2.S']['pad'];logic=L.PINS['MCU.GND']['pad']
    assert {source2,logic,'N01','O01'}<=reachable(source1)
    assert not({source2,logic}&reachable(source1,{'N01','O01'}))
    assert logic not in reachable(source2,{'N01','O01'})

@pytest.mark.parametrize('damage',['bend','joint','gap','post','diameter'])
def test_physical_negative_controls(monkeypatch,damage):
    if damage=='bend':monkeypatch.setattr(R,'BEND_RADIUS',2.0)
    if damage=='joint':monkeypatch.setattr(M,'JOINT_HEIGHT',5.0)
    if damage=='gap':monkeypatch.setattr(M,'REAR_GAP',14.0)
    if damage=='post':
        wire=next(w for w in L.WIRES if w['id']=='W93')
        monkeypatch.delitem(wire,'offset_b')
    if damage=='diameter':monkeypatch.setattr(R,'OD',2.54)
    # Freshly regenerated geometry must fail; this is not just stale-file detection.
    with pytest.raises(AssertionError):R.validate(R.plan())
