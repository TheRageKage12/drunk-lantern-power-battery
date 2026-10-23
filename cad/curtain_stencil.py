"""Cutting stencil for the hand-side cover: lay it on the frosted polypropylene divider and cut round it and along it.

    cd cad && python3 curtain_stencil.py   # -> output/curtain_stencil.stl (any colour, no supports, ~14 g)

A 1.6 mm open frame the exact size of the cover: a rim, a rail either side of each cut, rings round the holes, and
bars tying it together (2026-10-23: was a solid plate, ~45 g). Hold it down on the divider (tape or a hand flat on it):
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
RAIL = 2.4                                       # plastic either side of each slot
RIM_IN = BL.R_LIP_R                              # rim 78 .. 85.5: carries the clamp-screw holes
HUB_R, BAR_W = 6.0, 4.0


def build():
    rs = P.CURTAIN_SLIT_R
    s = cq.Workplane('XY').circle(BL.CURTAIN_R).circle(RIM_IN).extrude(T)
    s = s.union(cq.Workplane('XY').circle(HUB_R).extrude(T))
    for k in range(P.CURTAIN_SLITS):
        a = k * 360 / P.CURTAIN_SLITS + 180 / P.CURTAIN_SLITS
        rails = cq.Workplane('XY').center(rs / 2, 0).rect(rs, SLOT_W + 2 * RAIL).extrude(T)
        rails = rails.union(cq.Workplane('XY').center(rs, 0).circle(P.CURTAIN_HOLE_D / 2 + RAIL).extrude(T))
        rails = rails.union(cq.Workplane('XY').center((rs + RIM_IN) / 2 + 0.5, 0).rect(RIM_IN - rs + 1, BAR_W).extrude(T))
        slot = cq.Workplane('XY').workplane(offset=-1).center(rs / 2, 0).rect(rs, SLOT_W).extrude(T + 2)
        hole = cq.Workplane('XY').workplane(offset=-1).center(rs, 0).circle(P.CURTAIN_HOLE_D / 2).extrude(T + 2)
        s = s.union(rails.rotate((0, 0, 0), (0, 0, 1), a)).cut(slot.union(hole).rotate((0, 0, 0), (0, 0, 1), a))
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
