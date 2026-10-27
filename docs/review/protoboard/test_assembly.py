"""Electrical completeness, ordering and negative geometry checks for the guide."""
import copy
import json
from pathlib import Path
import pytest
import assembly as A
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
    assert len(solder)==178
    assert max(s['index'] for s in solder if 'wire' not in s)<min(s['index'] for s in solder if 'wire' in s)


def test_layers_and_crossings_are_installed_in_order(guide):
    routes=guide['routes'];by_id={w['id']:w for w in routes}
    assert [w['depth'] for w in routes]==sorted(w['depth'] for w in routes)
    for w in routes:
        assert w['prepare']<min(w['joints'])<=max(w['joints'])<w['check']
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
    assert len(visits['O02'])>=4


def test_lengths_include_end_rises_and_not_unknown_harness(guide):
    for w in guide['routes']:
        length=w['length']
        assert length['cut']>=length['planar']+length['rises']+length['tails']-0.15
        if not w['bare']:
            assert length['rises']==round((w['depth']-.55)*(2 if w['b'] else 1),1)
        assert w['colour'] in {'red','black','white','blue','yellow','green'}
    # Long off-board slack is never invented as part of the saved route length.
    assert next(w for w in guide['routes'] if w['id']=='H07')['length']['cut']<100


def test_existing_default_validation_is_unchanged():
    original=json.loads((Path(__file__).parent/'routing.json').read_text())
    assert R.validate(original)['routes']==66


@pytest.mark.parametrize('damage',['endpoint','height','mount','diameter','crossing'])
def test_bad_routes_rejected(damage):
    routes=load_routes();by_id={w['id']:w for w in routes};w=by_id['W35']
    if damage=='endpoint':w['path'][0][0]+=2
    if damage=='height':w['depth']=9.5
    if damage=='mount':w['path'].insert(1,list(L.MOUNTS[0]))
    if damage=='diameter':w['od']=2.54
    if damage=='crossing':
        # Force an upper-layer path onto its lower crossing partner.
        by_id['W42']['depth']=2.7
    with pytest.raises(AssertionError):A.validate_routes(routes)
