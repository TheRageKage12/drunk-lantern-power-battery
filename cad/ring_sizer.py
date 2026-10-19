"""Ring sizer for key_ring: ten test bands, 18.5 to 23.0 mm inside, each with its size engraved on a tab.

    cd cad && python3 ring_sizer.py        # -> output/ring_sizer.stl (one print, ten separate bands)

Print it (any colour, no supports, ~6 g), find the band that slides over the knuckle of your left middle finger
with slight resistance and doesn't spin loosely, then set RING_ID in params.py to that size plus 0.5 mm:
key_ring's band is much wider along the finger than these 8 mm bands, and a wide band fits tighter.
Not part of build.py: it is a measuring tool, not a part of the lantern.
"""
import os
import cadquery as cq

SIZES = [18.5 + 0.5 * i for i in range(10)]   # inside diameters, mm
WALL, HEIGHT = 1.6, 8.0                       # band wall and length along the finger
TAB_L, TAB_W, TAB_T = 12.0, 6.5, 2.4          # label tab on the outside, at the bed
TEXT_H, TEXT_D = 3.6, 0.6
PITCH_X, PITCH_Y = 40.0, 36.0


def band(d):
    r = d / 2
    b = cq.Workplane('XY').circle(r + WALL).circle(r).extrude(HEIGHT)
    tab = cq.Workplane('XY').center(r + WALL + TAB_L / 2 - 0.8, 0).rect(TAB_L, TAB_W).extrude(TAB_T)
    label = (cq.Workplane('XY').workplane(offset=TAB_T - TEXT_D).center(r + WALL + TAB_L / 2 - 0.4, 0)
             .text(f'{d:.1f}', TEXT_H, TEXT_D + 0.01, combine=False))
    return b.union(tab).cut(label)


def build():
    parts = None
    for i, d in enumerate(SIZES):
        x, y = (i % 5) * PITCH_X, (i // 5) * PITCH_Y
        b = band(d).translate((x, y, 0))
        parts = b if parts is None else parts.add(b)
    return parts


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'ring_sizer.stl')
    cq.exporters.export(build(), out, tolerance=0.03, angularTolerance=0.1)
    print('wrote', out)
