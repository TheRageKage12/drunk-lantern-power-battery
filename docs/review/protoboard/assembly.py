"""Build the standalone, one-joint-at-a-time board assembly guide.

Electrical placement comes from layout.py. This guide's routes are separately
checked for the owner's nominal 1.7 mm Electronix Express stranded wire.
Run with NumPy and Shapely installed: python3 assembly.py
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
DIAMETER = 1.7
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
    tails = 1 if w['bare'] else 2 * ends
    trim = 3 if w['bare'] else max(4, min(8, planar * .05))
    return dict(planar=round(planar, 1), rises=round(rise, 1), tails=tails,
                trim=round(trim, 1), cut=math.ceil(planar + rise + tails + trim))


def validate_routes(routes):
    # Do not claim the old 1.6 mm model's margins for this thicker kit. The
    # centre paths still fit nominally, but the joint margin falls to 0.105 mm.
    result = R.validate(routes, wire_od=DIAMETER, clearance=.2, joint_clearance=.1)
    # A vertical 1.8 mm tip plus 0.1 mm clearance needs 1.85 mm from an unrelated
    # insulated centreline. Shared joints are intentionally reheated separately.
    for w in routes:
        if w['bare']:
            continue
        line = LineString(w['path'])
        for pad in BY_PAD:
            if pad not in (w['a'], w['b']):
                assert line.distance(Point(L.mm(pad))) >= w['od']/2 + .9 + .1 - 1e-6, (w['id'], pad, 'tip access')
    return result


def make_data(routes):
    G.validate()
    report = validate_routes(routes)
    routes = sorted(routes, key=lambda w: (w['depth'], w['id']))
    harness = {r: label for r, pad, net, label in L.HARNESS}
    # These captions deliberately follow rev C's actual cable arrangement.
    harness['H09'] = 'LED harness + (soldered; no extra plug)'
    harness['H10'] = 'LED harness − (soldered; no extra plug)'
    steps = []
    visits = defaultdict(list)

    def add(kind, title, text, **extra):
        s = dict(kind=kind, title=title, text=text, **extra)
        if s.get('pad'):
            s['previous'] = list(visits[s['pad']])
            visits[s['pad']].append(s.get('ref', s.get('wire', title)))
        steps.append(s)
        return len(steps)-1

    add('check', 'Start with a bare, unpowered board',
        'Disconnect battery, USB and buck supply. Leave the 74AHCT125 out of its socket and the JP1 shunt off. '
        'This guide follows the latest rev C board in the top cap. Fit components first; then build the rear wiring from the board outward.', phase='Prepare')
    add('check', 'Match the board and dry-fit the parts',
        'Use an isolated-pad board, 70 × 50 mm, 24 columns × 18 rows at 2.54 mm pitch. Confirm the actual hole offsets. '
        'Check the four mounts against the printed cap floor before drilling Ø3.2 mm; drill and clean before soldering. '
        'Keep the dashed 9 × 9 mm screw areas empty. The drawing is not a drill template.', phase='Prepare')
    add('check', 'Check the wire and practise a shared joint',
        'The Electronix Express kit is nominally Ø1.7 mm including PVC. Measure without crushing it. '
        'Practise attaching two tinned ends beside a component lead on spare pads: keep the joint below 1.5 mm high, '
        'without bridging its neighbours. Use a fine tip (modelled as Ø1.8 mm at the joint). Do not force a second wire into an occupied hole. '
        'Nominal clearance at some unrelated joints is only 0.105 mm; dry-fit each wire before soldering. '
        'If the wire is thicker than 1.7 mm, or a joint will not fit, stop and revise that route.', phase='Prepare')

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
        detail = ('No polarity. Bend leads without stressing the body.' if ref.startswith('R') else
            'Stripe toward '+('W08.' if ref=='D1' else 'X18.') if ref.startswith('D') else
            'Notch toward row 01. Solder opposite corners first, check that it sits flat, then solder the other pins. Leave the IC out.' if ref=='U1' else
            'USB faces column A. Fit the supplied headers directly; do not add tall sockets. Opposite corners first, then check alignment.' if ref=='MCU' else
            'Printed face toward row 18. Columns P / Q / R are gate / drain / source. Keep the metal tab clear of the other MOSFET.' if ref in ('Q1','Q2') else
            'Positive to F02; negative stripe to F04. Lie the can flat in its outline; insulate formed leads, secure its body and leave its vent uncovered. Maximum case Ø18 × 25 mm.' if ref=='C2' else
            'Fit the two-pin header. Leave its removable shunt OFF until the specified power-up procedure.' if ref=='JP1' else
            'No polarity. Form leads without bending at the ceramic coating.')
        fit = add('fit', 'Fit '+name, detail+' Hold it on the component side, then turn the board left-to-right: row 01 stays at the top.', ref=ref, phase='Components')
        joint_steps = []
        for key, pin in pins:
            nc = pin['net'].startswith('NC')
            joint_steps.append(add('solder', f"Solder {key} at {pin['pad']}",
                'Solder the pad and lead together. Let it cool, then trim the lead; '
                'keep the joint at most 1.5 mm above the rear face. '+
                ('This pin is mechanically soldered only; attach no wire.' if nc else 'Rear wires will attach to this joint later.'),
                ref=ref, pad=pin['pad'], phase='Components'))
        component_data.append(dict(ref=ref, name=name, fit=fit, solder=joint_steps,
                                   bounds=M.bounds()[ref], pins=[p['pad'] for _, p in pins]))

    add('check', 'Inspect every component joint before wiring',
        'Check diode stripes, C2 polarity, socket notch and MOSFET orientation against the component view. '
        'Look for bridges between adjacent pads. U1 stays out; JP1 stays open. Trim stray leads now, before wires hide them.', phase='Inspect')
    add('check', 'Prepare the outgoing cables before the wire layers',
        'Dry-fit the cap floor. Thread the lock, pump and LED leads through its wire hole before attaching them; '
        'then lift the board free for soldering. Keep the long ends parked outside the work area. '
        'Cable joints are interleaved with board wires so lower routes are not trapped underneath later ones. '
        'Keep the battery and buck disconnected throughout.', phase='Prepare cables')

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
        phase = 'Bare bridges' if w['bare'] else f"Wiring · {w['depth']:g} mm layer"
        if w['depth'] != last_depth:
            add('check', 'Start '+phase.lower(),
                ('Use short, fully tinned pieces of the 22 AWG conductor. There are only five bare adjacent-pad bridges. '
                 'No stray strands; no other wires may be left bare.' if w['bare'] else
                 f"Build this layer with wire centres about {w['depth']:g} mm behind the solder face. This includes a rise from each joint, not a flat wire. "
                 'Dry-form smooth bends, hold them with removable tape while fitting, and keep earlier wires in their own layers. '
                 'Do not add a hump above this layer to absorb excess length. Check the full 10 mm rear gap before continuing.'), phase=phase)
            last_depth = w['depth']
        dest = w['b'] or w['label']
        if w['b']:
            prep = (f"Cut a starting blank of {w['length']['cut']} mm from the {w['colour']} spool; label it {w['id']}. "
                    'This includes the routed distance, joint rises, 2 mm per termination and trimming allowance. ')
        else:
            prep = (f"Use {w['colour']} for {w['id']} → {w['label']}. The under-board portion needs about {w['length']['cut']} mm "
                    'before adding the external run. Measure the external run with the cap floor in place; use the cable calculator below. ')
        prep += ('Strip the bridge completely and tin the strands together. The finished bridge is about 3.5 mm long, '
                 'including a small overlap onto each pad; the starting blank is longer for handling. Trim overhangs before adding other wires.' if w['bare'] else
                 'Strip and lightly tin only the first 2 mm. Form the route and both end rises before heating any joint; '
                 'avoid sharp kinks or pushing neighbouring wires aside. Do not cut the whole batch before trying the first few.')
        w['prepare'] = add('wire', f"Prepare {w['id']} · {w['a']} → {dest}", prep, wire=w['id'], phase=phase)
        w['joints'] = []
        for end, pad in enumerate([w['a']] + ([w['b']] if w['b'] else [])):
            detail = ('Hold the tinned end against this rear pad or its existing component lead. '
                      'Solder, then let it cool. Keep insulation close; do not force a second wire into the hole.')
            if end:
                detail = ('Form the wire over the earlier routes listed below. Trim the second end to reach this pad '
                          'without pulling the first joint or leaving a loose loop. Strip/tin the final 2 mm and solder it beside the existing lead.')
            if w['bare']:
                detail = ('Keep the tinned bridge over these two adjacent pads only. '
                          'Solder this end and clip any handling tail, leaving roughly 0.5 mm overlap beyond each pad centre. '
                          'The finished bridge is about 3.5 mm, not the full starting blank. No bare strands may touch the next pad.')
            w['joints'].append(add('solder', f"Solder {w['id']} {'second' if end else 'first'} end · {pad}", detail,
                                    wire=w['id'], pad=pad, phase=phase))
        w['check'] = add('check', 'Check '+w['id'],
            (f"Meter {w['a']} to {w['b']} for continuity. " if w['b'] else
             f"Meter {w['a']} to the labelled free end of {w['id']}; leave the far end unpowered. ")+
            'Inspect both adjacent pads for bridges and tug gently on the insulated wire. '
            'Keep exposed metal within the joint. Recheck earlier wires sharing this pad after reheating. '
            'Secure outgoing cables off the board so movement cannot pull on copper pads.', wire=w['id'], phase=phase)

    add('check','Check the complete board before inserting U1',
        'With all power disconnected: check every wire endpoint against the cut list and every shared joint after its last reheat. '
        'Check the ground network at U1 pins 1, 4, 7, 9, 10, 12, 13; keep pins 8 and 11 isolated. '
        'Check for unintended shorts between supply and ground (capacitors can briefly affect a continuity reading). '
        'Dry-fit on the 10 mm standoffs: no wire may be pinched, and screw areas must remain clear. '
        'Only then insert U1 with its notch toward row 01.', phase='Final checks')
    add('check','Continue with staged power-up in the build guide',
        'This completes the board soldering, not commissioning. Set the buck to 5.0 V before connecting its output. '
        'D2 belongs at the pump and C4 at the Hall sensor. Follow EL-6 through EL-12 and the SW-6 USB rules; '
        'do not plug in USB with arbitrary battery/JP1/U1 combinations.', phase='Final checks')

    for i, step in enumerate(steps):step['index']=i
    source = b''.join((HERE/f).read_bytes() for f in ('layout.py','mechanical.py','routing.json','assembly.py'))
    return dict(version=hashlib.sha256(source).hexdigest()[:12], diameter=DIAMETER,
                gap=M.REAR_GAP, routes=routes, steps=steps, parts=component_data,
                pins=L.PINS, mounts=L.MOUNTS, colours=COLOURS,
                nets={n:dict(label=v[1],colour=NET_COLOUR[n]) for n,v in L.NETS.items()},
                report=report, source='main afc85d6 · 26 October 2026')


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
