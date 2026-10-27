"""Electrical completeness, ordering and negative geometry checks for the guide."""
import copy
import json
from pathlib import Path
import pytest
import assembly_guide as A
import layout as L
import routing as R


def load_routes():
    routes=json.loads((Path(__file__).parent/'routing.json').read_text())
    for w in routes:
        if not w['bare']:w['od']=A.DIAMETER
    return routes


@pytest.fixture(scope='module')
def guide():
    return A.make_data(load_routes())


def test_every_component_lead_and_wire_end_once(guide):
    steps=guide['steps']
    solder=[s for s in steps if s['kind']=='solder']
    expected={p['pad'] for key,p in L.PINS.items() if '.' in key and not key.startswith('BUS.')}
    leads=[s['pad'] for s in solder if 'wire' not in s]
    assert set(leads)==expected and len(leads)==len(expected)==60
    for w in L.WIRES:
        operations=[s['pad'] for s in solder if s.get('wire')==w['id']]
        assert operations==[w['a'],w['b']]
    for ref,pad,net,label in L.HARNESS:
        assert [s['pad'] for s in solder if s.get('wire')==ref]==[pad]
    assert len(solder)==190
    assert max(s['index'] for s in solder if 'wire' not in s)<min(s['index'] for s in solder if 'wire' in s)


def test_layers_and_crossings_are_installed_in_order(guide):
    routes=guide['routes'];by_id={w['id']:w for w in routes}
    assert [w['depth'] for w in routes]==sorted(w['depth'] for w in routes)
    for w in routes:
        assert w['prepare']<min(w['joints'])<=max(w['joints'])==w['check']
        for other in w['earlier_crossings']:
            assert by_id[other]['check']<w['prepare']
            assert by_id[other]['depth']<w['depth']
    # A known upper-layer wire must explain its existing obstructions.
    assert by_id['W42']['earlier_crossings']


def test_shared_joint_history_excludes_future_work(guide):
    visits={}
    for step in guide['steps']:
        if step.get('pad'):
            assert step['previous']==visits.get(step['pad'],[])
            visits.setdefault(step['pad'],[]).append(step.get('ref',step.get('wire',step['title'])))
    assert len(visits['P09'])>=4


def test_lengths_include_end_rises_and_not_unknown_harness(guide):
    for w in guide['routes']:
        length=w['length']
        assert length['cut']>=length['planar']+length['rises']+length['tails']-0.15
        if not w['bare']:
            assert length['rises']==round((w['depth']-.55)*(2 if w['b'] else 1),1)
        assert w['colour'] in {'red','black','white','blue','yellow','green'}
    # Long off-board slack is never invented as part of the saved route length.
    assert next(w for w in guide['routes'] if w['id']=='H07')['length']['cut']<100


def test_reference_and_guide_use_the_same_clearances():
    original=json.loads((Path(__file__).parent/'routing.json').read_text())
    assert R.validate(original)['routes']==72


def test_hand_assembly_margins_and_shared_points(guide):
    from collections import Counter
    from shapely.geometry import LineString, Point
    import mechanical as M
    routes=guide['routes']
    assert guide['diameter']==1.8 and guide['gap']==10
    assert guide['gap']-guide['report']['maximum_rear_extent_mm']>=.9-1e-6
    counts=Counter(p for w in routes if not w['bare'] for p in (w['a'],w['b']) if p)
    for ref,pin in L.PINS.items():
        # No component lead must carry three thick insulated wire ends.
        if '.' in ref and not ref.startswith('BUS.'):
            assert counts[pin['pad']]<=2, (ref,counts[pin['pad']])
    depths=sorted({w['depth'] for w in routes if not w['bare']})
    assert depths==[3.0,5.6,8.2]
    assert all(b-a-guide['diameter']>=.8-1e-6 for a,b in zip(depths,depths[1:]))
    assert sum(not w['bare'] for w in routes)==33
    for w in routes:
        if w['bare']:
            assert LineString(w['path']).length <= 8.1
    # Finished lower joints can be covered; unfinished ones cannot. Walk the
    # actual solder sequence independently from the routing planner.
    last_joint={s['pad']:s['index'] for s in guide['steps'] if s.get('pad')}
    covered=[]
    for w in routes:
        for pin in L.PINS.values():
            pad=pin['pad']
            if pad in (w['a'],w['b']):continue
            distance=LineString(w['path']).distance(Point(L.mm(pad)))
            if distance < w['od']/2+1.4:
                assert last_joint[pad] < w['prepare'], (w['id'],pad)
                covered.append((w['id'],pad))
    assert covered, 'Exercise the finished-joint overpass cases'


def test_direct_cables_and_load_returns():
    # Direct cable attachments must preserve the circuit, including the two
    # independent high-current source returns to the input ground bus.
    cables={r:(p,n) for r,p,n,label in L.HARNESS}
    for cable,pin in [('H05','C3.1'),('H08','Q1.D'),('H10','Q2.D'),('H11','R7.1'),('H12','R5.2'),('H13','R7.2')]:
        assert cables[cable]==(L.PINS[pin]['pad'],L.PINS[pin]['net'])
    wires={w['id']:w for w in L.WIRES}
    assert (wires['W09']['a'],wires['W09']['b'])==('R13','Q02')
    assert (wires['W10']['a'],wires['W10']['b'])==('R17','P02')


@pytest.mark.parametrize('damage',['endpoint','height','mount','diameter','crossing'])
def test_bad_routes_rejected(damage):
    routes=load_routes();by_id={w['id']:w for w in routes};w=by_id['W35']
    if damage=='endpoint':w['path'][0][0]+=2
    if damage=='height':w['depth']=16.5
    if damage=='mount':w['path'].insert(1,list(L.MOUNTS[0]))
    if damage=='diameter':w['od']=2.54
    if damage=='crossing':
        # Force an upper-layer path onto its lower crossing partner.
        guide=A.make_data(copy.deepcopy(routes))
        upper=next(r for r in guide['routes'] if r['earlier_crossings'])
        by_id[upper['id']]['depth']=by_id[upper['earlier_crossings'][0]]['depth']
    with pytest.raises(AssertionError):A.validate_routes(routes)
