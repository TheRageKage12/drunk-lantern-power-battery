"""Cutting stencil for the hand-side cover: lay it on the frosted polypropylene divider and cut round it and along it.

    cd cad && python3 curtain_stencil.py   # -> output/curtain_stencil.stl (any colour, no supports, ~45 g)

A 1.6 mm plate the exact size of the cover. Hold it down on the divider (tape or a hand flat on it):
  1. punch or melt the 8 small holes through the round holes at the ends of the slots (a hot nail or a hole punch);
  2. run a sharp hobby knife along each of the 8 slots, from the centre out to its hole;
  3. mark the 6 clamp-screw holes through the small holes near the edge, and punch them;
  4. cut round the stencil's edge.
The slots never reach the edge, so the stencil (and the cover) stays in one piece. The same shapes as the paper
template (docs/images/curtain_template.pdf), from the same numbers. Not part of build.py: it is a tool, not a part.
"""
import math
import os
import cadquery as cq
import params as P
from parts import bells as BL

T = 1.6
SLOT_W = 1.2                                     # a hobby knife blade runs in it


def build():
    s = cq.Workplane('XY').circle(BL.CURTAIN_R).extrude(T)
    for k in range(P.CURTAIN_SLITS):
        a = k * 360 / P.CURTAIN_SLITS + 180 / P.CURTAIN_SLITS
        slot = cq.Workplane('XY').workplane(offset=-1).center(P.CURTAIN_SLIT_R / 2, 0) \
            .rect(P.CURTAIN_SLIT_R, SLOT_W).extrude(T + 2)
        hole = cq.Workplane('XY').workplane(offset=-1).center(P.CURTAIN_SLIT_R, 0).circle(P.CURTAIN_HOLE_D / 2).extrude(T + 2)
        s = s.cut(slot.union(hole).rotate((0, 0, 0), (0, 0, 1), a))
    for t in BL.CLAMP_SCREW_ANGLES:
        x, y = BL.CLAMP_SCREW_R * math.cos(math.radians(t)), BL.CLAMP_SCREW_R * math.sin(math.radians(t))
        s = s.cut(cq.Workplane('XY').workplane(offset=-1).center(x, y).circle(P.M3_CLEAR / 2).extrude(T + 2))
    return s


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'curtain_stencil.stl')
    s = build()
    cq.exporters.export(s, out, tolerance=0.03, angularTolerance=0.1)
    bb = s.val().BoundingBox()
    print('wrote', out, round(s.val().Volume() / 1000, 1), 'cm3', f'{bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm',
          'solids:', len(s.solids().vals()))
