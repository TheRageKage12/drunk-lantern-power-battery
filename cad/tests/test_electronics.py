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
assert B.DECK_GAP == 17
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

# A <=1 mm strap must pass both floor slots, under the floor and over the pack
# without intersecting the side rails or the six pillars.
xslot = B.BANK_HALF_W+B.BANK_END_STOP_GAP+B.BANK_END_STOP_T+1+B.STRAP_SLOT_W/2
y0, y1 = P.BATTERY_STRAP_Y-10, P.BATTERY_STRAP_Y+10
top = P.FLOOR+P.POWERBANK_T
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
old_d = P.PERFBOARD_CAP_D
P.PERFBOARD_CAP_D = 30
assert inter_volume(E.build()['board_components_envelope'], placed['base']) > .5
P.PERFBOARD_CAP_D = old_d

print('ELECTRONICS FIT OK: battery, fixed deck, rear wiring, strap route; oversized capacitor and boss collision detected')
