"""Fit / clearance checks run after a full build. Fill in per DESIGN_CONTRACT.md 'Checks'."""
import cadquery as cq
import params as P
from assembly import place


def inter_volume(a, b):
    # A failed boolean is an unverified clearance, never evidence of zero overlap.
    # Intersect solid pairs explicitly: OCC common on a compound containing
    # overlapping component allowances can otherwise depend on operand order.
    volume = 0.0
    for left in a.solids().vals():
        lb = left.BoundingBox()
        for right in b.solids().vals():
            rb = right.BoundingBox()
            if any(min(getattr(lb, ax+'max'), getattr(rb, ax+'max')) -
                   max(getattr(lb, ax+'min'), getattr(rb, ax+'min')) <= 1e-7 for ax in 'xyz'):
                continue
            volume += left.intersect(right).Volume()
    return volume


def run(all_parts, placements):
    print('--- checks ---')
    placed = {n: place(wp, placements.get(n)) for n, (wp, _m) in all_parts.items()}
    problems = 0
    # 1. validity
    for n, wp in placed.items():
        if not wp.val().isValid():
            print(f'FAIL valid: {n}'); problems += 1
        ns = len(wp.val().Solids())
        if ns != 1 and not n.endswith('_envelope'):   # a printed part must be one body (rev 9g: the rear half's flange floated as two loose arcs)
            print(f'FAIL bodies: {n} is {ns} solids'); problems += 1
    # 2. hardware envelopes in the assembly frame must not hit any wall
    envelopes = {}
    for n in [k for k in list(placed) if k.endswith('_envelope') and k != 'switch_envelope']:
        envelopes[n] = placed.pop(n)
    SHELL = ('base', 'dish_lower')   # parts that move with the lantern when it is lifted off the base cartridge
    for en, env in envelopes.items():
        if en.endswith('_sweep_envelope'):   # must also clear the hardware the cartridge carries
            for hn in (k for k in envelopes if not k.endswith('_sweep_envelope')):
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
    problems += electronics_checks(all_parts, placements)
    print(f'--- checks done: {problems} problem(s) ---')
    return problems


def electronics_checks(all_parts, placements):
    """Strict checks for the small electronic parts and their reserved wiring space.

    Do not use the older 200 mm3 general tolerance: it could hide a thin PCB or
    solder joint cutting through plastic. Mounting holes/pads are cut out explicitly.
    Also test the continuous retaining-boss sweep, not just the installed shell.
    """
    placed = {n: place(wp, placements.get(n)) for n, (wp, _) in all_parts.items()}
    electronic = [n for n, (_, module) in all_parts.items() if module == 'parts.electronics']
    targets = electronic + ['powerbank_envelope']
    problems = 0
    pairs = set()
    for en in targets:
        for other in placed:
            pair = tuple(sorted((en, other)))
            if en == other or pair in pairs:
                continue
            pairs.add(pair)
            v = inter_volume(placed[en], placed[other])
            if v > 0.5:
                print(f'FAIL electronics: {en} vs {other}: {v:.2f} mm3')
                problems += 1
    print(f'electronics: {len(pairs)} component / shell-removal checks, {problems} problem(s); reserved dimensions require measurement')
    return problems
