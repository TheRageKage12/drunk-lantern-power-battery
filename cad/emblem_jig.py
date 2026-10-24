"""Glue-up guide for the emblem's centre disc: it centres emblem_centre in the lid's round cut-out.

    cd cad && python3 emblem_jig.py        # -> output/emblem_jig.stl (any colour, no supports, ~14 g)

The lid itself needs no guide: two short pieces of 1.75 mm filament in the pin holes of the halo ring and the lid
line it up, the right way round. Once the lid is glued on: drop this guide into the lid's round cut-out (its flange
rests on the lid), put a little glue in the middle of the disc's underside, drop the disc into the guide's bore,
press it down, and lift the guide straight off after half a minute.
Not part of build.py: it is a tool, not a part of the lantern.
"""
import os
import cadquery as cq
import params as P
from parts import top as T

FLANGE_R, FLANGE_T = T.EMBLEM_RING[1] + 7.0, 1.2


def build():
    r_out = T.EMBLEM_RING[1] - P.SNUG                 # fits the lid's 76 mm round cut-out
    r_in = T.EMBLEM_RING[0] - P.FIT + P.SNUG          # the disc slides in
    tube = cq.Workplane('XY').circle(r_out).circle(r_in).extrude(T.LID_T)
    flange = cq.Workplane('XY').workplane(offset=T.LID_T).circle(FLANGE_R).circle(r_in).extrude(FLANGE_T)
    jig = tube.union(flange)
    return jig.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, T.LID_T + FLANGE_T))   # flange on the bed


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'emblem_jig.stl')
    j = build()
    cq.exporters.export(j, out, tolerance=0.03, angularTolerance=0.1)
    print('wrote', out, round(j.val().Volume() / 1000, 1), 'cm3')
