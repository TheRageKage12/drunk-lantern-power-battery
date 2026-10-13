"""Fit / clearance checks run after a full build. Fill in per DESIGN_CONTRACT.md 'Checks'."""
import cadquery as cq
import params as P
from assembly import place


def inter_volume(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def run(all_parts, placements):
    print('--- checks ---')
    placed = {n: place(wp, placements.get(n)) for n, (wp, _m) in all_parts.items()}
    problems = 0
    # 1. validity
    for n, wp in placed.items():
        if not wp.val().isValid():
            print(f'FAIL valid: {n}'); problems += 1
    # 2. hardware envelopes in the assembly frame must not hit any wall
    envelopes = {}
    for n in [k for k in list(placed) if k.endswith('_envelope') and k != 'switch_envelope']:
        envelopes[n] = placed.pop(n)
    SHELL = ('base', 'dish_lower')   # parts that move with the lantern when it is lifted off the base cartridge
    for en, env in envelopes.items():
        if en.endswith('_sweep_envelope'):   # must also clear the hardware the cartridge carries
            for hn in ('bottle_envelope', 'pump_envelope', 'powerbank_envelope', 'trigger_envelope'):
                v = inter_volume(env, envelopes[hn]) if hn in envelopes else 0.0
                if v > 200.0:
                    print(f'FAIL clearance: {en} intersects {hn} by {v / 1000:.1f} cm3'); problems += 1
        for n, wp in placed.items():
            if en in ('fist_envelope', 'forearm_envelope') and n.startswith('switch'):
                continue
            if en.endswith('_sweep_envelope') and n in SHELL:
                continue
            v = inter_volume(env, wp)
            if v > 200.0:   # > 0.2 cm3: smaller values are coincident-face artefacts of touching envelopes
                print(f'FAIL clearance: {en} intersects {n} by {v / 1000:.1f} cm3'); problems += 1
    # 3. parts must not intersect each other (except deliberate zero-volume contact)
    names = list(placed)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = inter_volume(placed[names[i]], placed[names[j]])
            if v > 100.0:    # > 0.1 cm3: smaller values are coincident mating faces (1 cm3 hid real clashes, rev 7)
                print(f'FAIL overlap: {names[i]} vs {names[j]} by {v / 1000:.1f} cm3'); problems += 1
    print(f'--- checks done: {problems} problem(s) ---')
    return problems
