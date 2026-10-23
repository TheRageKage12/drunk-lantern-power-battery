"""Full-size cutting template for the hand-side cover (one frosted polypropylene disc with 8 cuts).

    python3 docs/images/src/gen_curtain_template.py   # -> docs/images/curtain_template.pdf (+ .png preview)

Print the PDF at 100 % ("actual size", not "fit to page") on letter paper and check the 50 mm bar with a ruler.
Sizes come from cad/params.py and cad/parts/bells.py.
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'cad'))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import params as P
from parts import bells as BL

W, H = 215.9, 279.4                                  # letter, mm
fig = plt.figure(figsize=(W / 25.4, H / 25.4))
ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect('equal'); ax.axis('off')
cx, cy = W / 2, 150.0
ax.add_patch(Circle((cx, cy), BL.CURTAIN_R, fill=False, lw=1.2, color='black'))
ax.add_patch(Circle((cx, cy), BL.R_LIP_R, fill=False, lw=0.6, ls='--', color='#2a7a3a'))
for k in range(P.CURTAIN_SLITS):
    a = math.radians(k * 360 / P.CURTAIN_SLITS + 180 / P.CURTAIN_SLITS)
    ex, ey = cx + P.CURTAIN_SLIT_R * math.cos(a), cy + P.CURTAIN_SLIT_R * math.sin(a)
    ax.plot([cx, ex], [cy, ey], color='#c00', lw=1.0)
    ax.add_patch(Circle((ex, ey), P.CURTAIN_HOLE_D / 2, fill=False, lw=1.0, color='#c00'))
for t in BL.CLAMP_SCREW_ANGLES:                      # clamp screw holes (the clamp ring lines up with these too)
    a = math.radians(t)
    ax.add_patch(Circle((cx + BL.CLAMP_SCREW_R * math.cos(a), cy + BL.CLAMP_SCREW_R * math.sin(a)), P.M3_CLEAR / 2,
                        fill=False, lw=1.0, color='#0050c0'))
ax.plot([20, 70], [18, 18], color='black', lw=2); ax.text(45, 21, '50 mm: check this with a ruler', ha='center', fontsize=8)
txt = [('HAND-SIDE COVER: cutting template (print at 100 %, actual size)', 'black', 11, 'bold'),
       ('Tape it to the frosted polypropylene divider (0.3-0.5 mm). Cut the black circle (%d mm).' % round(2 * BL.CURTAIN_R), 'black', 9, 'normal'),
       ('RED: punch the %d small holes first (%.0f mm: hole punch or hot nail), then cut the %d lines from the centre to them.'
        % (P.CURTAIN_SLITS, P.CURTAIN_HOLE_D, P.CURTAIN_SLITS), '#c00', 9, 'normal'),
       ('BLUE: the %d clamp-ring screw holes (%.1f mm). Green dashed: the part that shows inside the bell\'s lip.'
        % (len(BL.CLAMP_SCREW_ANGLES), P.M3_CLEAR), '#0050c0', 9, 'normal'),
       ('Don\'t cut past the red holes: the uncut ring is what holds it in one piece and makes the flaps spring shut.', 'black', 9, 'normal')]
for i, (t, c, fs, fw) in enumerate(txt):
    ax.text(W / 2, H - 14 - 7 * i, t, ha='center', fontsize=fs, color=c, fontweight=fw)
out = os.path.join(ROOT, 'docs', 'images', 'curtain_template.pdf')
fig.savefig(out); fig.savefig(out[:-4] + '.png', dpi=60)
print('wrote', out)
