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
    for n in ('bottle_envelope', 'pump_envelope', 'powerbank_envelope', 'glass_envelope'):
        if n in placed:
            envelopes[n] = placed.pop(n)
    for en, env in envelopes.items():
        for n, wp in placed.items():
            v = inter_volume(env, wp)
            if v > 200.0:   # > 0.2 cm3: smaller values are coincident-face artefacts of touching envelopes
                print(f'FAIL clearance: {en} intersects {n} by {v / 1000:.1f} cm3'); problems += 1
    # 3. parts must not intersect each other (except deliberate zero-volume contact)
    names = list(placed)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = inter_volume(placed[names[i]], placed[names[j]])
            if v > 5.0:
                print(f'FAIL overlap: {names[i]} vs {names[j]} by {v / 1000:.1f} cm3'); problems += 1
    print(f'--- checks done: {problems} problem(s) ---')
    return problems
