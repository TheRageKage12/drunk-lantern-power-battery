"""Regression checks for cartridge retention, rear wiring and moving-shell clearance."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import params as P
from parts import base as B, electronics as E
from assembly import place
from checks import inter_volume

parts = B.build()
placed = {n: place(s, B.placements().get(n)) for n, s in parts.items()}
electronic = E.build()

assert B.DECK_Z0 == 44 and B.DECK_TOP == 47, 'Battery thickness must not move the deck loads'
assert B.DECK_GAP == 16   # deck at z=44 over the pack on its 1 mm bed
for n in ('base_tray', 'base_deck', 'base'):
    assert inter_volume(placed['powerbank_envelope'], placed[n]) < .5, n
assert inter_volume(electronic['board_wiring_envelope'], placed['base_deck']) < .5
assert inter_volume(electronic['board_components_envelope'], electronic['charge_plug_envelope']) < .5
# The old jack location clashes with the populated board. Compound checks must
# report this whichever operand is first (not silently return zero).
old_plug = electronic['charge_plug_envelope'].translate((-8-P.JACK_XY[0], 80-P.JACK_XY[1], 0))
forward = inter_volume(old_plug, electronic['board_components_envelope'])
reverse = inter_volume(electronic['board_components_envelope'], old_plug)
assert forward > .5 and abs(forward-reverse) < .01

# A <=2 mm strap must pass both floor slots, under the floor and over the pack
# without intersecting the side rails or the six pillars.
xslot = B.BANK_HALF_W+B.BANK_END_STOP_GAP+B.BANK_END_STOP_T+1+B.STRAP_SLOT_W/2
y0, y1 = P.BATTERY_STRAP_Y-10, P.BATTERY_STRAP_Y+10
top = P.PACK_Z+P.POWERBANK_T
strap = E.compound([
    E.box(-xslot, xslot, y0, y1, 0, P.BATTERY_STRAP_T),
    E.box(-xslot, xslot, y0, y1, top, top+P.BATTERY_STRAP_T),
    *[E.box(s*xslot-.5, s*xslot+.5, y0, y1, 0, top+1) for s in (-1, 1)],
])
assert inter_volume(strap, placed['base_tray']) < .5, 'Strap blocked by tray/pillars'
assert inter_volume(strap, placed['base_deck']) < .5

# Negative controls: the model must catch a component in the boss sweep and an
# oversized capacitor hitting the wall, even if the PCB itself still fits.
bad_edge_part = E.board_place(E.board_box(65, 15, 5, 10, 5, 10))
assert inter_volume(bad_edge_part, placed['service_sweep_envelope']) > .5
oversized_cap = E.board_place(E.board_box(25,-2,25,30,0,31))
assert inter_volume(oversized_cap, placed['base']) > .5

# Former near-touching C3 and a moved socket must fail body spacing checks,
# even though a fused component envelope would hide their overlap.
def rejects(action):
    try: action()
    except AssertionError: return
    raise AssertionError('Negative control was incorrectly accepted')
bodies=E.M.bounds()
u=bodies['U1']
bodies['C3']=(u[0]+u[2]+.01,u[1],10,4,0,13)
rejects(lambda:E.M.validate(bodies))
bodies=E.M.bounds()
bodies['R1']=(18-2,17-2,4,4,0,3)
rejects(lambda:E.M.validate(bodies))

import routing, json, copy
routes=json.loads((Path(__file__).resolve().parents[2]/'docs/review/protoboard/routing.json').read_text())
routing.validate(routes)
bad=copy.deepcopy(routes)
next(w for w in bad if not w['bare'])['depth']=9.5
rejects(lambda:routing.validate(bad))
bad=copy.deepcopy(routes)
next(w for w in bad if not w['bare'])['od']=1.2
rejects(lambda:routing.validate(bad))
# Artificial same-layer crossing between unrelated wires, preserving endpoints.
bad=copy.deepcopy(routes)
a,b=[w for w in bad if w['id'] in ('W13','W41')]
a['path']=[a['path'][0],b['path'][0],a['path'][-1]]
a['depth']=b['depth']
rejects(lambda:routing.validate(bad))

print('ELECTRONICS FIT OK: battery, fixed deck, rear wiring, strap route; oversized capacitor and boss collision detected')
