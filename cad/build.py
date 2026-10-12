"""
Build every part, export STL/STEP, assemble, render and run checks.

    python3 build.py              # everything
    python3 build.py base socket  # only these modules

Each module in parts/ exposes build() -> {name: Workplane} (print orientation) and
placements() -> {name: (axis_xyz, angle_deg, (dx, dy, dz))} mapping print frame -> assembly frame.
"""
import importlib
import os
import sys
import time
import pkgutil

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
sys.path.insert(0, HERE)

import parts  # noqa: E402

PRINT_BED = (230.0, 230.0, 240.0)   # the owner's modified Ender 3


def discover(selected):
    mods = []
    for m in pkgutil.iter_modules(parts.__path__):
        if selected and m.name not in selected:
            continue
        mods.append(importlib.import_module(f'parts.{m.name}'))
    return mods


def export(name, wp):
    os.makedirs(OUT, exist_ok=True)
    stl = os.path.join(OUT, f'{name}.stl')
    step = os.path.join(OUT, f'{name}.step')
    cq.exporters.export(wp, stl, tolerance=0.05, angularTolerance=0.15)
    try:
        cq.exporters.export(wp, step)
    except Exception as e:  # STEP export is best-effort
        print(f'  ! STEP export failed for {name}: {e}')
    return stl


def main():
    selected = set(sys.argv[1:])
    t0 = time.time()
    all_parts = {}      # name -> (print-oriented Workplane, module name)
    placements = {}     # name -> (axis, angle, translate)
    for mod in discover(selected):
        t = time.time()
        built = mod.build()
        placed = mod.placements() if hasattr(mod, 'placements') else {}
        for name, wp in built.items():
            if not wp.val().isValid():
                print(f'  ! INVALID solid: {name}')
            x, y, z = (wp.val().BoundingBox().xlen, wp.val().BoundingBox().ylen, wp.val().BoundingBox().zlen)
            fits = x <= PRINT_BED[0] + 1e-6 and y <= PRINT_BED[1] + 1e-6 and z <= PRINT_BED[2] + 1e-6
            vol = wp.val().Volume() / 1000.0
            print(f'  {name:24s} {x:6.1f} x {y:6.1f} x {z:6.1f} mm  {vol:7.1f} cm3  {"fits bed" if fits else "!! TOO BIG"}')
            export(name, wp)
            all_parts[name] = (wp, mod.__name__)
            if name in placed:
                placements[name] = placed[name]
        print(f'{mod.__name__}: {len(built)} part(s) in {time.time() - t:.1f}s')

    # assembly (for renders + checks)
    if not selected:
        try:
            import assembly
            assembly.write_assembly(all_parts, placements, OUT)
        except Exception as e:
            print(f'assembly step skipped: {e}')
        try:
            import checks
            checks.run(all_parts, placements)
        except Exception as e:
            print(f'checks failed to run: {e}')
    print(f'done in {time.time() - t0:.1f}s -> {OUT}')


if __name__ == '__main__':
    main()
