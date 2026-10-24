"""Test coupon for the 6-32 heat-set inserts the thumbscrews thread into: a block with three insert holes and a 2 mm
plate (THUMB_WEB, what each thumbscrew clamps in the lantern) with its counterbore.

    cd cad && python3 thumb_test.py        # -> output/thumb_test.stl (print in PETG like the lantern, ~8 g)

Melt an insert (initeq #6-32 long) into each hole with the soldering iron, top flush. Pick the hole where it goes in
straight, sits flush and doesn't spin when the thumbscrew is tightened through the plate, and set THUMB_INSERT_HOLE in
params.py to that size (4.8 is designed in). Not part of build.py: it is a tool, not a part of the lantern.
"""
import os
import cadquery as cq
import params as P

HOLES = (4.6, 4.8, 5.0)
PITCH = 16.0


def build():
    h = P.THUMB_INSERT_DEPTH + 1.5
    block = cq.Workplane('XY').box(PITCH * len(HOLES), 14, h, centered=(True, True, False))
    for i, d in enumerate(HOLES):
        x = (i - (len(HOLES) - 1) / 2) * PITCH
        block = block.cut(cq.Workplane('XY').workplane(offset=h - P.THUMB_INSERT_DEPTH).center(x, 0).circle(d / 2).extrude(P.THUMB_INSERT_DEPTH + 1))
        label = cq.Workplane('XZ').workplane(offset=7.0).center(x, h / 2).text(f'{d:.1f}', 3.5, 0.6, combine=False)
        block = block.cut(label.translate((0, 0.01, 0)))
    t = P.THUMB_PAD_T
    plate = cq.Workplane('XY').box(16, 14, t, centered=(True, True, False)).translate((0, 22, 0))
    plate = plate.cut(cq.Workplane('XY').workplane(offset=-1).center(0, 22).circle(P.THUMB_CLEAR / 2).extrude(t + 2))
    plate = plate.cut(cq.Workplane('XY').workplane(offset=P.THUMB_WEB).center(0, 22).circle(P.THUMB_CB_D / 2).extrude(t))
    return block.union(plate)


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'thumb_test.stl')
    c = build()
    cq.exporters.export(c, out, tolerance=0.03, angularTolerance=0.1)
    print('wrote', out, round(c.val().Volume() / 1000, 1), 'cm3')
