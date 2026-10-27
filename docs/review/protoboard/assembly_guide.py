"""Build the standalone, one-joint-at-a-time board assembly guide.

Electrical placement comes from layout.py. Routes reserve 1.8 mm for the owner's nominal 1.7 mm stranded wire.
Run with NumPy and Shapely installed: python3 assembly_guide.py
"""
from pathlib import Path
import hashlib
import json
import math
from collections import defaultdict

from shapely.geometry import LineString, Point
import layout as L
import mechanical as M
import routing as R
import generate as G

HERE = Path(__file__).resolve().parent
DIAMETER = M.WIRE_OD
COLOURS = {
    'red': '#c42d32', 'black': '#292c32', 'white': '#fafafa',
    'blue': '#2363bb', 'yellow': '#efd04a', 'green': '#2f8451',
}
NET_COLOUR = dict(
    VLOAD='red', GND='black', **{'5V_REG': 'white', 'AFTER_D1': 'white',
    'XIAO_5V': 'white', '3V3': 'green'}, HALL='green', SW='yellow',
    TWIST='yellow', ADC='yellow', PWM_P='blue', GATE_P='blue',
    PWM_L='blue', GATE_L='blue', DRAIN_P='blue', DRAIN_L='yellow')
BY_PAD = {p['pad']: (ref, p['net']) for ref, p in L.PINS.items()}


def route_length(w):
    """Actual curved centreline plus through-board tails and trimming stock."""
    formed=R.length(w['path3d'])
    tails=0 if w['bare'] else M.BOARD_THICKNESS if not w['b'] else 2*(M.BOARD_THICKNESS+.55)
    trim=4 if w['bare'] else 6
    return dict(planar=round(formed,1),rises=0,tails=round(tails,1),trim=trim,
                formed=round(formed,1),cut=math.ceil(formed+tails+trim))


def assembly_order(routes):
    """Finish obstructed joints first, and put crossing lower wires in first."""
    pending={w['id']:w for w in routes}; before={id:set() for id in pending}
    lines={w['id']:LineString(w['path']) for w in routes}
    for a in routes:
        for b in routes:
            if a is b:continue
            shared=set(a['anchors']) & set(b['anchors'])
            if any(lines[a['id']].distance(Point(L.mm(p))) < a['od']/2+1.4-1e-6
                   for p in set(b['anchors'])-shared):before[a['id']].add(b['id'])
            if a['bare'] and not b['bare']:before[b['id']].add(a['id'])
            if not a['b'] and b['b'] and not b['bare']:before[b['id']].add(a['id'])
            if (not a['bare'] and not b['bare'] and a['b'] and b['b']
                and a['depth']<b['depth'] and lines[a['id']].intersects(lines[b['id']])):
                before[b['id']].add(a['id'])
    ordered=[]
    while pending:
        ready=[w for id,w in pending.items() if not(before[id] & pending.keys())]
        assert ready, ('Impossible soldering order', sorted(pending))
        w=min(ready,key=lambda w:(w['depth'],w['id']))
        ordered.append(pending.pop(w['id']))
    return ordered


def validate_routes(routes):
    result = R.validate(routes)
    # A finished joint may be covered by a later wire. Every joint that still
    # needs soldering must retain a straight approach for a 2 mm tip + 0.4 mm.
    ordered=assembly_order(routes)
    for i,w in enumerate(ordered):
        line=LineString(w['path'])
        future={p for later in ordered[i+1:] for p in later['anchors']}
        for pad in future - set(w['anchors']):
            assert line.distance(Point(L.mm(pad))) >= w['od']/2 + 1.4 - 1e-6, (w['id'],pad,'tip access')
    return result


def make_data(routes):
    G.validate()
    report = validate_routes(routes)
    routes = assembly_order(routes)
    harness = {r: label for r, pad, net, label in L.HARNESS}
    steps = []
    visits = defaultdict(list)

    def add(kind, title, text, **extra):
        s = dict(kind=kind, title=title, text=text, **extra)
        if s.get('pad'):
            s['previous'] = list(visits[s['pad']])
            visits[s['pad']].append(s.get('ref', s.get('wire', title)))
        steps.append(s)
        return len(steps)-1

    add('check', 'Disconnect all power',
        'Battery, USB and buck disconnected. Leave U1 out and JP1 open.', phase='Prepare')
    add('check', 'Check the board and mounts',
        '70 × 50 mm, isolated pads. Match the four screw holes to the cap floor; drill Ø3.2 mm before soldering.', phase='Prepare')
    add('check', 'Add four 6 mm spacers',
        'Use Ø3.2 mm holes, ≤6 mm outside diameter, and M3×12 screws. Existing 10 mm posts stay; wiring space becomes 16 mm.', phase='Prepare')
    add('check', 'Prepare your wire',
        'Use your six colours of stranded 22 AWG, up to Ø1.8 mm over insulation. Bare tracks are lightly tinned. Leave through-hole wire ends untinned until fitted.', phase='Prepare')

    parts = {p['ref']: p for p in L.PARTS}
    order = ['R1','R2','R3','R4','R5','R6','R7','D1','D3','U1','JP1','C1','C3','MCU','Q1','Q2','C2']
    component_data = []
    for ref in order:
        pins = [(key, p) for key, p in L.PINS.items() if key.split('.')[0] == ref]
        if ref == 'U1':
            pins.sort(key=lambda item: (item[0] not in ('U1.1','U1.8'), int(item[0].split('.')[1])))
        if ref == 'MCU':
            pins.sort(key=lambda item: (item[0] not in ('MCU.5V','MCU.D6'), list(L.PINS).index(item[0])))
        name = f"{ref} · {parts[ref]['value']}" if ref in parts else {'U1':'U1 · empty DIP-14 socket','MCU':'XIAO RP2040','Q1':'Q1 · pump MOSFET','Q2':'Q2 · LED MOSFET'}[ref]
        detail = ('Bend the leads to the highlighted holes.' if ref.startswith('R') else
            'Stripe toward '+('W08.' if ref=='D1' else 'X18.') if ref.startswith('D') else
            'Notch toward row 01. Fit the empty socket; solder opposite corners first.' if ref=='U1' else
            'USB toward column A. Use direct headers, without extra sockets.' if ref=='MCU' else
            'Printed face toward row 18. Keep the two metal tabs apart.' if ref in ('Q1','Q2') else
            'Positive to F02, striped negative to F04. Lie flat and secure; case ≤ Ø18 × 25 mm. Insulate formed leads.' if ref=='C2' else
            'Fit the two-pin header; leave the shunt OFF.' if ref=='JP1' else
            'No polarity. Bend leads away from the ceramic coating.')
        fit = add('fit', 'Fit '+name, detail, ref=ref, phase='Components')
        joint_steps = []
        for key, pin in pins:
            nc = pin['net'].startswith('NC')
            joint_steps.append(add('solder', f"Solder {key} · {pin['pad']}",
                'Solder, cool, then trim the lead to ≤1.5 mm. Keep the finished joint below 2.5 mm.' +
                (' No wire connects here.' if nc else ''),
                ref=ref, pad=pin['pad'], phase='Components'))
        component_data.append(dict(ref=ref, name=name, fit=fit, solder=joint_steps,
                                   bounds=M.bounds()[ref], pins=[p['pad'] for _, p in pins]))

    add('check', 'Inspect the component joints',
        'Check polarity and look for solder bridges. U1 stays out; JP1 stays open.', phase='Inspect')
    add('check', 'Thread the outgoing cables',
        'Thread pump, LED and lock leads through the cap floor. Lift the board free and park the long ends out of the way.', phase='Prepare cables')

    add('check', 'Keep the cable row flat',
        'Retain the outgoing wires side by side. Their bends turn upward beyond the board edge; service loops stay outside the board gap.', phase='Prepare cables')
    last_depth = None
    for w in routes:
        w['net'] = BY_PAD[w['a']][1]
        w['colour'] = NET_COLOUR[w['net']]
        w['length'] = route_length(w)
        w['segments'] = R.pieces(w)
        w['label'] = harness.get(w['id'], L.NETS[w['net']][1])
        w['earlier_crossings'] = []
        for old in routes:
            if old is w:break
            if old['depth'] >= w['depth']:continue
            intersections = LineString(w['path']).intersection(LineString(old['path']))
            shared = {w['a'],w['b']} & {old['a'],old['b']} - {None}
            for pad in shared:
                intersections = intersections.difference(Point(L.mm(pad)).buffer(2.3))
            if not intersections.is_empty:
                w['earlier_crossings'].append(old['id'])
        phase = 'Bare tracks' if w['bare'] else 'Cable row' if not w['b'] else 'Arches · '+{6.0:'lower',9.0:'middle',12.0:'upper'}[w['depth']]
        if w['depth'] != last_depth:
            add('check', 'Start '+phase.lower(),
                ('Strip, form and lightly tin. Solder each marked anchor; no loose strands.' if w['bare'] else
                 f"Keep the top of each wire about {w['depth']+w['od']/2:g} mm off the board. Form before soldering; leave earlier wires undisturbed."), phase=phase)
            last_depth = w['depth']
        dest = w['b'] or w['label']
        prep = ('Form the shown track; tin lightly. Anchor every marked hole, including the bends.' if w['bare'] else
                'Form both rounded bends before fitting. Strip 4 mm; insert each end 1.2 mm into its empty hole, flush with the front.' if w['b'] else
                'Measure the external run below. Strip 4 mm at the board end; insert 1.2 mm, flush with the front. Keep the cable row flat.')
        if w.get('offset_a') or w.get('offset_b'):
            bends=[]
            for end in ('a','b'):
                offset=w.get('offset_'+end)
                if offset:
                    direction=('column X' if offset[0]>0 else 'column A') if offset[0] else ('row 18' if offset[1]>0 else 'row 01')
                    bends.append(w[end]+' toward '+direction)
            prep+=' Lean '+', '.join(bends)+' by 0.6 mm; match both template views.'
        w['prepare'] = add('wire', f"Prepare {w['id']} · {w['a']} → {dest}", prep, wire=w['id'], phase=phase)
        w['joints'] = []
        for end, pad in enumerate(w['anchors']):
            detail = ('Solder this anchor. Keep strands together and the track flat.' if w['bare'] else
                      'Solder the single wire in this hole. Keep the formed bend relaxed; joint ≤2.5 mm high.')
            if end==len(w['anchors'])-1:detail+=' Check continuity and neighbouring pads.'
            w['joints'].append(add('solder', f"Solder {w['id']} · {pad}", detail,
                                    wire=w['id'], pad=pad, phase=phase))
        w['check'] = w['joints'][-1]

    add('check','Check the finished board',
        'Check all connections and unintended shorts. Fit the 6 mm spacers. Check at least 2 mm remains below the wiring without squeezing it; then insert U1, notch toward row 01.', phase='Final checks')
    add('check','Set the buck to 5.0 V before connecting it',
        'Continue with EL-6–EL-12 in the build guide. D2 goes at the pump; C4 at the Hall sensor. Follow SW-6 for USB.', phase='Final checks')

    for i, step in enumerate(steps):step['index']=i
    source = b''.join((HERE/f).read_bytes() for f in ('layout.py','mechanical.py','routing.json','assembly_guide.py'))
    return dict(version=hashlib.sha256(source).hexdigest()[:12], diameter=DIAMETER,
                gap=M.REAR_GAP, routes=routes, steps=steps, parts=component_data,
                pins=L.PINS, mounts=L.MOUNTS, colours=COLOURS,
                nets={n:dict(label=v[1],colour=NET_COLOUR[n]) for n,v in L.NETS.items()},
                report=report, source='Existing 10 mm posts + 6 mm removable spacers · 27 October 2026')


def main():
    routes=json.loads((HERE/'routing.json').read_text())
    for w in routes:
        if not w['bare']:w['od']=DIAMETER
    data=make_data(routes)
    html=(HERE/'assembly-template.html').read_text().replace('/*__ASSEMBLY_DATA__*/',
            json.dumps(data,separators=(',',':')).replace('</','<\\/'))
    (HERE/'assembly.html').write_text(html)
    print(json.dumps(dict(steps=len(data['steps']), solder_operations=sum(s['kind']=='solder' for s in data['steps']), **data['report']),indent=2))


if __name__=='__main__':main()
