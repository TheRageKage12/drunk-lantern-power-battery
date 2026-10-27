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
    """Conservative blank: orthogonal corridor + rises + termination + trim.

    The model reserves the wire's height; it does not invent a second slack hump
    above that height. Round corners during dry fit and trim unused allowance.
    """
    planar = sum(math.dist(a, b) for a, b in zip(w['path'], w['path'][1:]))
    ends = 2 if w['b'] else 1
    rise = 0 if w['bare'] else ends * (w['depth'] - .55)
    tails = .8 if w['bare'] else 2 * ends
    trim = 3 if w['bare'] else max(4, min(8, planar * .05))
    return dict(planar=round(planar, 1), rises=round(rise, 1), tails=tails,
                trim=round(trim, 1), cut=math.ceil(planar + rise + tails + trim))


def validate_routes(routes):
    result = R.validate(routes)
    # A finished joint may be covered by a later wire. Every joint that still
    # needs soldering must retain a straight approach for a 2 mm tip + 0.4 mm.
    ordered=sorted(routes,key=lambda w:(w['depth'],w['id']))
    for i,w in enumerate(ordered):
        line=LineString(w['path'])
        future={p for later in ordered[i+1:] for p in (later['a'],later['b']) if p}
        for pad in future - {w['a'],w['b']}:
            assert line.distance(Point(L.mm(pad))) >= w['od']/2 + 1.4 - 1e-6, (w['id'],pad,'tip access')
    return result


def make_data(routes):
    G.validate()
    report = validate_routes(routes)
    routes = sorted(routes, key=lambda w: (w['depth'], w['id']))
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
    add('check', 'Keep the existing mounts',
        'The printed posts provide 10 mm below the board. Solder with the board removed; dry-fit before fastening.', phase='Prepare')
    add('check', 'Prepare your wire',
        'Use your six colours of stranded 22 AWG, up to Ø1.8 mm over insulation. Tin 2 mm at each end.', phase='Prepare')

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
                'Solder, cool, then trim to ≤1.5 mm above the board.' +
                (' No wire connects here.' if nc else ''),
                ref=ref, pad=pin['pad'], phase='Components'))
        component_data.append(dict(ref=ref, name=name, fit=fit, solder=joint_steps,
                                   bounds=M.bounds()[ref], pins=[p['pad'] for _, p in pins]))

    add('check', 'Inspect the component joints',
        'Check polarity and look for solder bridges. U1 stays out; JP1 stays open.', phase='Inspect')
    add('check', 'Thread the outgoing cables',
        'Thread pump, LED and lock leads through the cap floor. Lift the board free and park the long ends out of the way.', phase='Prepare cables')

    last_depth = None
    for w in routes:
        w['net'] = BY_PAD[w['a']][1]
        w['colour'] = NET_COLOUR[w['net']]
        w['length'] = route_length(w)
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
        phase = 'Bare links' if w['bare'] else 'Wiring · '+{3.0:'lower',5.6:'middle',8.2:'upper'}[w['depth']]
        if w['depth'] != last_depth:
            add('check', 'Start '+phase.lower(),
                ('Strip and tin each short link. Keep it close to the board; no stray strands.' if w['bare'] else
                 f"Keep the top of each wire about {w['depth']+w['od']/2:g} mm off the board. Tape in place; leave earlier wires undisturbed."), phase=phase)
            last_depth = w['depth']
        dest = w['b'] or w['label']
        prep = (f"Strip and tin the link. Finish at about {w['length']['planar']+.8:.1f} mm; no stray strands." if w['bare'] else
                'Form the shown path with relaxed bends. Leave the second end long; trim it after fitting.' if w['b'] else
                'Measure the external run below, then form the shown board route. Keep service slack outside the board gap.')
        w['prepare'] = add('wire', f"Prepare {w['id']} · {w['a']} → {dest}", prep, wire=w['id'], phase=phase)
        w['joints'] = []
        for end, pad in enumerate([w['a']] + ([w['b']] if w['b'] else [])):
            detail = ('Solder beside the existing lead; do not force another wire through the hole.' if not end else
                      'Trim to fit, tin 2 mm, then solder. Leave the wire relaxed.')
            if w['bare']:detail = 'Solder this end. Keep the bare bridge over these two pads only.'
            if end or not w['b']:detail += ' Check continuity and neighbouring pads.'
            w['joints'].append(add('solder', f"Solder {w['id']} {'second' if end else 'first'} end · {pad}", detail,
                                    wire=w['id'], pad=pad, phase=phase))
        w['check'] = w['joints'][-1]

    add('check','Check the finished board',
        'Check all connections and unintended shorts. Dry-fit on the existing 10 mm posts without squeezing wires; then insert U1, notch toward row 01.', phase='Final checks')
    add('check','Set the buck to 5.0 V before connecting it',
        'Continue with EL-6–EL-12 in the build guide. D2 goes at the pump; C4 at the Hall sensor. Follow SW-6 for USB.', phase='Final checks')

    for i, step in enumerate(steps):step['index']=i
    source = b''.join((HERE/f).read_bytes() for f in ('layout.py','mechanical.py','routing.json','assembly_guide.py'))
    return dict(version=hashlib.sha256(source).hexdigest()[:12], diameter=DIAMETER,
                gap=M.REAR_GAP, routes=routes, steps=steps, parts=component_data,
                pins=L.PINS, mounts=L.MOUNTS, colours=COLOURS,
                nets={n:dict(label=v[1],colour=NET_COLOUR[n]) for n,v in L.NETS.items()},
                report=report, source='Existing 10 mm mounts · 27 October 2026')


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
