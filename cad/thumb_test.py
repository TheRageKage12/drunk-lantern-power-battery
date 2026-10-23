"""Test coupon for the knurled thumbscrews: a block with three pilot holes and a 3 mm plate like the sphere's collar.

    cd cad && python3 thumb_test.py        # -> output/thumb_test.stl (print in PETG like the lantern, ~6 g)

Drive a thumbscrew (6-32, PC-case thread) through the plate into each pilot hole. Pick the hole where it cuts a firm
thread and still turns by hand, and set THUMB_PILOT in params.py to that size (2.8 is designed in).
Not part of build.py: it is a tool, not a part of the lantern.
"""
import os
import cadquery as cq
import params as P

PILOTS = (2.6, 2.8, 3.0)
DEPTH = 6.5 + 1.0


def build():
    w = 16.0 * len(PILOTS)
    block = cq.Workplane('XY').box(w, 14, DEPTH + 1.5, centered=(True, True, False))
    for i, d in enumerate(PILOTS):
        x = (i - (len(PILOTS) - 1) / 2) * 16.0
        block = block.cut(cq.Workplane('XY').workplane(offset=1.5).center(x, 0).circle(d / 2).extrude(DEPTH + 1))
        label = cq.Workplane('XZ').workplane(offset=7.0).center(x, (DEPTH + 1.5) / 2).text(f'{d:.1f}', 3.5, 0.6, combine=False)
        block = block.cut(label.translate((0, 0.01, 0)))
    plate = cq.Workplane('XY').box(16, 14, P.THUMB_GRIP, centered=(True, True, False)).translate((0, 22, 0))
    plate = plate.cut(cq.Workplane('XY').workplane(offset=-1).center(0, 22).circle(P.THUMB_CLEAR / 2).extrude(P.THUMB_GRIP + 2))
    return block.union(plate)


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'thumb_test.stl')
    c = build()
    cq.exporters.export(c, out, tolerance=0.03, angularTolerance=0.1)
    print('wrote', out, round(c.val().Volume() / 1000, 1), 'cm3')
