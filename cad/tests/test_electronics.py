"""Regression checks for the cap layout (rev C): battery retention, rear wiring, the strap route and the cap wall."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import params as P
from parts import top as T, electronics as E
from assembly import place
from checks import inter_volume

parts = T.build()
placed = {n: place(s, T.placements().get(n)) for n, s in parts.items()}
electronic = E.build()

assert T.BOARD_STANDOFF + E.M.BOARD_SPACER == E.M.REAR_GAP, 'The standoffs are the board\'s rear wiring gap'
for n in ('cap_floor', 'top_cap'):
    assert inter_volume(electronic['powerbank_envelope'], placed[n]) < .5, n
    assert inter_volume(electronic['battery_connector_envelope'], placed[n]) < .5, n
assert inter_volume(electronic['board_wiring_envelope'], placed['cap_floor']) < .5
# The battery's LED row must be readable from below: inside the neck bore and on the hand side of the lock wall.
import math
x0, x1 = P.PACK_LED_X
y_led = -P.POWERBANK_L / 2 + P.PACK_LED_IN
for x in (x0, x1):
    pt = T.pack_to_cap(T._box(0.01, 0.01, 0.01, x, y_led)).val().Center()
    assert math.hypot(pt.x, pt.y) < T.NECK_RI - 5, 'LED row outside the neck bore'
    assert pt.y > T.WEXT_Y + T.WEXT_T, 'LED row hidden behind the lock wall'

# A <=2 mm strap must pass both plate slots, under the plate and over the pack
# without hitting the rails, the board or anything else on the plate.
xslot = T.HW + T.STOP_GAP + T.STOP_T + 1 + T.STRAP_SLOT_W / 2
y0, y1 = P.BATTERY_STRAP_Y - 10, P.BATTERY_STRAP_Y + 10
top = P.PACK_BED_T + P.POWERBANK_T
strap = E.pack(E.compound([
    E.box(-xslot, xslot, y0, y1, -T.CAP_FLOOR_T, -T.CAP_FLOOR_T + P.BATTERY_STRAP_T),
    E.box(-xslot, xslot, y0, y1, top, top + P.BATTERY_STRAP_T),
    *[E.box(s * xslot - .5, s * xslot + .5, y0, y1, -T.CAP_FLOOR_T, top + 1) for s in (-1, 1)],
]))
assert inter_volume(strap, placed['cap_floor']) < .5, 'Strap blocked by the plate or rails'
for n, env in electronic.items():
    if n != 'powerbank_envelope':
        assert inter_volume(strap, env) < .5, f'Strap hits {n}'

# Negative controls: the model must catch a component past the board's edge hitting the cap wall, and the battery
# shifted 20 mm toward its plug, even if the PCB itself still fits.
bad_edge_part = E.board_box(20, -40, 10, 10, 5, 10)
assert inter_volume(bad_edge_part, placed['top_cap']) > .5
shifted_plug = electronic['battery_connector_envelope'].translate((0, 20, 0))
assert inter_volume(shifted_plug, placed['top_cap']) > .5

# Former near-touching C3 and a moved socket must fail body spacing checks,
# even though a fused component envelope would hide their overlap.
def rejects(action):
    try: action()
    except AssertionError: return
    raise AssertionError('Negative control was incorrectly accepted')
bodies = E.M.bounds()
u = bodies['U1']
bodies['C3'] = (u[0] + u[2] + .01, u[1], 10, 4, 0, 13)
rejects(lambda: E.M.validate(bodies))
bodies = E.M.bounds()
bodies['R1'] = (18 - 2, 17 - 2, 4, 4, 0, 3)
rejects(lambda: E.M.validate(bodies))

import routing, json, copy
routes = json.loads((Path(__file__).resolve().parents[2] / 'docs/review/protoboard/routing.json').read_text())
routing.validate(routes)
bad = copy.deepcopy(routes)
next(w for w in bad if not w['bare'])['depth'] = 9.5
rejects(lambda: routing.validate(bad))
bad = copy.deepcopy(routes)
next(w for w in bad if not w['bare'])['od'] = 1.2
rejects(lambda: routing.validate(bad))
# Artificial same-layer crossing between unrelated wires, preserving endpoints.
bad = copy.deepcopy(routes)
a, b = [w for w in bad if w['id'] in ('W13', 'W41')]
a['path'] = [a['path'][0], b['path'][0], a['path'][-1]]
a['depth'] = b['depth']
rejects(lambda: routing.validate(bad))

print('ELECTRONICS FIT OK: battery in the cap, LED row visible, rear wiring, strap route; wall and plug collisions detected')
