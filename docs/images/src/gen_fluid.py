import sys, math
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

BLUE = "#1d4ed8"
LBLUE = "#bfdbfe"
PGREEN = "#2a9d2a"
BODY = "#f1f1f1"
W, H = 1000, 850
s = SVG(W, H, "Green Lantern power battery - fluid path and internal layout, side view")

s.text(20, 32, "Fluid path and internal layout — side view (section)", size=18, weight="bold")
s.text(20, 50, "1.8× rebuild, ~430 mm tall; schematic, not to scale", size=11, color="#555")

CX = 500
# ------------------------------------------------------------------ handle (outline)
s.path("M350,406 L350,250 A150,150 0 0 1 650,250 L650,406", stroke=GREY, sw=10, dash=None, opacity=0.35)
s.path("M350,406 L350,250 A150,150 0 0 1 650,250 L650,406", stroke=GREY, sw=1, dash="6,4")
s.circle(350, 406, 5, fill="#bdbdbd", stroke=GREY, sw=1)
s.circle(650, 406, 5, fill="#bdbdbd", stroke=GREY, sw=1)

# ------------------------------------------------------------------ base drum
s.rect(362, 770, 276, 20, fill=BODY, sw=1.4)             # foot step
s.rect(372, 650, 256, 122, fill=BODY, sw=1.4)            # drum
# lower dish (mouth down) - hollow
s.path("M374,650 L448,540 L552,540 L626,650 Z", stroke=INK, sw=1.4, fill=BODY)
# upper dish (mouth up)
s.path("M374,160 L448,272 L552,272 L626,160", stroke=INK, sw=1.4, fill=BODY)
s.path("M374,160 L626,160", stroke=INK, sw=1, dash="3,3")
# sphere, truncated to flat faces at x=415 / 585
s.path("M415,302 A134,134 0 0 1 585,302 L585,510 A134,134 0 0 1 415,510 Z", stroke=INK, sw=1.6, fill="#ffffff")
s.path("M500,274 L500,538", stroke=GREY, sw=1, dash="4,3")   # split line front/back halves

# ------------------------------------------------------------------ sphere interior
# glass bay
s.rect(455, 330, 90, 150, fill="#fafafa", stroke=INK, sw=1, dash="2,2")
# drip tray
s.rect(460, 478, 88, 8, fill="#cfd8dc", sw=1)
# shot glass
s.path("M470,478 L476,400 L524,400 L530,478 Z", stroke=INK, sw=1.4, fill="#eef6ff")
s.path("M472,452 L528,452", stroke=BLUE, sw=1, dash="3,2")
# nozzle clip + tube end
s.rect(512, 362, 18, 14, fill="#cfd8dc", sw=1)
# front diffuser window + strip (left flat face)
s.path("M415,327 L415,484", stroke=PGREEN, sw=7, opacity=0.6)
s.path("M427,338 L427,474", stroke=PGREEN, sw=1.2, dash="3,3")
for k in range(9):
    s.circle(427, 342 + k * 16.5, 2.4, fill="#4caf50", stroke="none")
# rear hatch (right flat face)
s.path("M585,350 L585,480", stroke="#8d6e63", sw=6)
s.rect(581, 346, 8, 6, fill="#5d4037", stroke="none")        # hinge
s.rect(581, 474, 8, 6, fill="#9e9e9e", stroke="none")        # magnet latch
# reach-in arrow
s.arrow([(660, 430), (596, 430)], "#8d6e63", sw=2)

# ------------------------------------------------------------------ charging socket in the upper-dish floor
s.rect(458, 258, 84, 32, fill="#dcdcdc", sw=1.2)             # housing
s.rect(458, 250, 20, 8, fill="#a5d6a7", sw=0.8)              # NeoPixel halo left
s.rect(522, 250, 20, 8, fill="#a5d6a7", sw=0.8)              # halo right
s.rect(478, 246, 44, 12, fill="#bdbdbd", sw=1)               # rotor
# finger ring standing in the pocket
s.circle(500, 228, 18, fill="none", stroke="#2e7d32", sw=5)
s.rect(492, 206, 16, 8, fill="#2e7d32", stroke="none")

# ------------------------------------------------------------------ base interior
# power bank on edge (front) + electronics tray above it
s.rect(380, 690, 36, 92, fill="#e0e0e0", sw=1.2)
s.rect(378, 660, 64, 14, fill="#c8e6c9", sw=1.2)
# pump: head + motor
s.circle(453, 737, 21, fill="#e0e0e0", sw=1.3)
for a in (90, 210, 330):
    s.circle(453 + 10 * math.cos(math.radians(a)), 737 + 10 * math.sin(math.radians(a)), 4, fill="#9e9e9e", stroke="none")
s.rect(474, 719, 40, 38, fill="#e0e0e0", sw=1.3)
# bottle at the rear, protruding into the lower dish hollow
s.rect(518, 605, 72, 177, rx=10, fill="#ffffff", sw=1.4)
s.rect(518, 655, 72, 127, rx=10, fill=LBLUE, stroke="none")      # liquid
s.rect(518, 605, 72, 177, rx=10, fill="none", sw=1.4)
s.rect(538, 593, 36, 14, fill="#9e9e9e", sw=1)                 # cap
s.path("M570,593 L570,586", stroke=INK, sw=1)                  # vent hole
s.arrow([(584, 570), (572, 586)], GREY, sw=1.2)
# pickup tube inside the bottle
s.path("M556,607 L556,772", stroke=BLUE, sw=2.2)
s.arrow([(556, 760), (556, 700)], BLUE, sw=2.2)
# rear wall: master switch + service door
s.rect(626, 656, 10, 14, fill="#424242", sw=1)
s.path("M628,682 L628,775", stroke="#8d6e63", sw=6)
s.rect(624, 678, 8, 6, fill="#5d4037", stroke="none")
s.rect(624, 770, 8, 6, fill="#5d4037", stroke="none")

# ------------------------------------------------------------------ tube + fluid path
# bottle cap -> pump inlet
s.path("M556,593 L556,573 L443,573 L443,717", stroke=BLUE, sw=2.2)
s.arrow([(520, 573), (470, 573)], BLUE, sw=2.2)
# pump outlet -> grommet -> nozzle
s.path("M463,717 L463,585 L530,585 L530,520 L548,520 L548,372 L521,372 L521,392", stroke=BLUE, sw=2.2)
s.arrow([(463, 700), (463, 640)], BLUE, sw=2.2)
s.arrow([(548, 500), (548, 420)], BLUE, sw=2.2)
s.arrow([(521, 378), (521, 395)], BLUE, sw=2.2)
# grommet
s.rect(524, 536, 12, 8, fill="#424242", stroke="none")
# wire channel (dashed grey) from the tray up to the socket
s.path("M420,660 L420,622 L450,622 L450,522 L444,522 L444,292 L470,278", stroke="#7c3aed", sw=1.4, dash="5,3")

# ------------------------------------------------------------------ headers
s.text(40, 100, "FRONT (audience)", size=15, weight="bold")
s.text(960, 100, "REAR (owner)", size=15, weight="bold", anchor="end")
s.arrow([(40, 112), (170, 112)], GREY, sw=1.2)
s.arrow([(960, 112), (830, 112)], GREY, sw=1.2)


def label(x, y, rows, tx, ty, anchor="start", color=INK, size=11):
    """text block at (x,y) with a leader to (tx,ty)"""
    s.lines(x, y, rows, size=size, anchor=anchor, color=color, lh=13)
    ax = x + (6 if anchor == "start" else -6)
    if anchor == "start":
        ax = x - 6
    s.path(f"M{ax},{y - 4} L{tx},{ty}", stroke=GREY, sw=1)
    s.dot(tx, ty, GREY, r=2.2)


# left column labels (anchor end, text ends at x=300)
LX = 300
label(LX, 150, ["handle arch — outline only (it really", "spans left–right across this view)"], 351, 300, anchor="end")
label(LX, 205, ["upper dish, mouth up", "(charging socket in its floor)"], 405, 207, anchor="end")
label(LX, 300, ["sphere: two printed halves", "split on the dashed line"], 432, 300, anchor="end")
label(LX, 365, ["front window: white diffuser,", "green LED strip rows behind it"], 414, 380, anchor="end")
label(LX, 440, ["hidden glass bay with cradle;", "shot glass sits inside"], 456, 430, anchor="end")
label(LX, 520, ["bay-floor grommet (tube seal)"], 523, 540, anchor="end")
label(LX, 580, ["lower dish, mouth down — hollow,", "tube and wires pass its neck"], 400, 612, anchor="end")
label(LX, 640, ["wire channel to the socket", "(dashed purple)"], 420, 640, anchor="end")
label(LX, 690, ["electronics board: XIAO, AHCT125,", "2 MOSFETs, LM2596 buck"], 376, 667, anchor="end")
label(LX, 745, ["USB-C PD power bank (12 V),", "flat on the floor under the deck"], 379, 735, anchor="end")
label(LX, 805, ["base drum (stepped foot)"], 372, 782, anchor="end")

# right column labels (anchor start at x=700)
RX = 700
label(RX, 150, ["ring key cap in the rotor pocket", "(6×2 mm magnet on the axis)"], 519, 228, anchor="start")
label(RX, 205, ["charging socket module: rotor, Hall", "sensor, microswitch, return plunger"], 543, 270, anchor="start")
label(RX, 300, ["tube rises behind the bay", "to the nozzle clip"], 549, 440, anchor="start")
label(RX, 365, ["nozzle clip above the glass", "(aims into the centre)"], 531, 369, anchor="start")
label(RX, 420, ["rear hatch, magnet-latched:", "reach in, take the glass"], 592, 410, anchor="start")
label(RX, 480, ["removable drip tray under the glass"], 549, 482, anchor="start")
label(RX, 560, ["silicone tube from the pump", "(1/8\" ID × 1/4\" OD in the head)"], 531, 575, anchor="start")
label(RX, 612, ["vented cap: air in as liquid leaves;", "pickup tube reaches the bottom"], 575, 600, anchor="start")
label(RX, 660, ["(no master switch: unplug the bank)"], 637, 663, anchor="start")
label(RX, 700, ["8 oz (250 mL) squat jar on the", "deck, refilled through the door"], 591, 690, anchor="start")
label(RX, 760, ["rear service door: refill the", "jar, charge/unplug the bank"], 632, 745, anchor="start")

# pump label under the base
s.lines(468, 822, ["Kamoer KPHM200 peristaltic pump, 12 V"], size=11, anchor="middle")
s.path("M468,810 L468,772", stroke=GREY, sw=1)
s.dot(468, 772, GREY, r=2.2)
s.text(490, 757, "pump", size=8, color="#555")

# legend
lx, ly = 660, 822
s.wire([(lx, ly - 4), (lx + 28, ly - 4)], BLUE, sw=2.2, marker="arrB")
s.text(lx + 34, ly, "liquid path", size=11)
s.path(f"M{lx + 110},{ly - 4} L{lx + 138},{ly - 4}", stroke="#7c3aed", sw=1.4, dash="5,3")
s.text(lx + 144, ly, "wires", size=11)
s.path(f"M{lx + 190},{ly - 4} L{lx + 218},{ly - 4}", stroke="#8d6e63", sw=6)
s.text(lx + 224, ly, "hinged door / hatch", size=11)
# scale bar: 50 mm = 72 px (1.45 px/mm)
s.path("M40,822 L112,822 M40,817 L40,827 M112,817 L112,827", stroke=INK, sw=1.5)
s.text(76, 838, "50 mm", size=10, anchor="middle")

open(os.path.join(HERE, "..", "fluid-path.svg"), "w").write(s.finish())
print("written")
