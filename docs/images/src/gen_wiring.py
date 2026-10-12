"""Wiring diagram for the budget build: 12 V USB-C PD power, LM2596 buck, XIAO RP2040, 74AHCT125 gate
driver, two low-side MOSFETs (pump, plain green LED strip), DRV5032 Hall sensor, D2F-L switch.
Writes ../wiring.svg."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

MAG = "#a21caf"   # 3.3 V
W, H = 1290, 880
s = SVG(W, H, "Green Lantern power battery - wiring (budget build)")


def box(x, y, w, h, title, sub=None, fill="#f5f5f5", dash=None):
    s.rect(x, y, w, h, fill=fill, sw=1.4, rx=6, dash=dash)
    s.text(x + w / 2, y + 20, title, size=13, anchor="middle", weight="bold")
    if sub:
        s.lines(x + w / 2, y + 36, sub, size=10, anchor="middle", color="#444")


def pin(x, y, label, side, color=INK):
    s.circle(x, y, 3.2, fill="#ffffff", stroke=color, sw=1.4)
    if side == "in-left":      # label inside a box whose left edge is at x
        s.text(x + 7, y + 4, label, size=10.5)
    elif side == "in-right":
        s.text(x - 7, y + 4, label, size=10.5, anchor="end")
    elif side == "out-left":
        s.text(x - 7, y + 4, label, size=10.5, anchor="end")
    elif side == "out-right":
        s.text(x + 7, y + 4, label, size=10.5)
    elif side == "below":
        s.text(x + 6, y + 15, label, size=10)
    elif side == "above":
        s.text(x + 6, y - 6, label, size=10)


def dot(x, y, c=INK):
    s.dot(x, y, c, r=3.4)


def resistor_v(x, y_top, label, ground=True):
    s.rect(x - 6, y_top, 12, 30, fill="#ffffff", sw=1.3)
    s.text(x + 10, y_top + 19, label, size=9.5)
    if ground:
        s.wire([(x, y_top + 30), (x, y_top + 38)], BLACK, sw=1.4)
        s.gnd(x, y_top + 38)


# ---------------------------------------------------------------- title, legend, rails
s.text(24, 34, "Green Lantern power battery - wiring (budget build)", size=20, weight="bold")
lx = 24
for col, lab in ((ORANGE, "+12 V"), (RED, "+5 V"), (MAG, "3.3 V"), (BLACK, "GND"), (GREEN, "signal")):
    s.wire([(lx, 56), (lx + 26, 56)], col, sw=3)
    s.text(lx + 32, 60, lab, size=11)
    lx += 95
s.text(lx + 10, 60, "All ground symbols are one net. A dot is a joint; lines that cross without a dot do not connect.",
       size=10.5, color="#444")

RAIL12, GND_Y = 120, 800
s.wire([(400, RAIL12), (W - 20, RAIL12)], ORANGE, sw=3.2)
s.text(W - 20, RAIL12 - 8, "+12 V rail", size=11, anchor="end", color=ORANGE, weight="bold")
s.wire([(16, GND_Y), (W - 20, GND_Y)], BLACK, sw=3)
s.text(W - 20, GND_Y + 18, "GND rail", size=11, anchor="end", weight="bold")

# ---------------------------------------------------------------- power bank + PD cable
box(24, 84, 170, 90, "Power bank", ["USB-C PD with a 12 V profile", "(e.g. INIU B61)"])
s.rect(188, 124, 12, 14, fill="#bbbbbb", sw=1)
box(220, 96, 150, 60, "PD 12 V cable", ["Adafruit 5450,", "barrel plug cut off"], fill="#fff7e6")
s.wire([(200, 131), (220, 131)], GREY, sw=3)
s.wire([(370, 112), (400, 112), (400, RAIL12)], ORANGE, sw=3)
s.text(374, 106, "+", size=12, weight="bold", color=ORANGE)
s.wire([(370, 146), (386, 146), (386, 176)], BLACK, sw=2.4)
s.gnd(386, 176)
s.text(374, 162, "-", size=13, weight="bold")

# C2 across the 12 V rail
cx = 450
s.wire([(cx, RAIL12), (cx, 150)], ORANGE, sw=2)
s.path(f"M{cx-12},150 L{cx+12},150 M{cx-12},158 Q{cx},152 {cx+12},158", stroke=INK, sw=2)
s.wire([(cx, 156), (cx, 172)], BLACK, sw=2)
s.gnd(cx, 172)
s.text(cx + 16, 156, "C2 2200 µF 16 V (+ to the rail)", size=10)
dot(cx, RAIL12, ORANGE)

# ---------------------------------------------------------------- LM2596 buck -> 1N5819 -> XIAO 5V
box(40, 230, 160, 92, "LM2596 buck", ["12 V in, 5.0 V out:", "set it to 5.0 V with a meter", "BEFORE connecting the XIAO"], fill="#fff7e6")
pin(80, 230, "IN+", "above", ORANGE)
s.wire([(80, 230), (80, 196), (415, 196), (415, RAIL12)], ORANGE, sw=2.2)
dot(415, RAIL12, ORANGE)
pin(120, 322, "GND", "below", BLACK)
s.wire([(120, 322), (120, 344), (16, 344), (16, GND_Y)], BLACK, sw=2)
pin(200, 260, "", "out-right", RED)
s.text(206, 254, "OUT+ 5 V", size=10, color=RED)
s.wire([(200, 260), (262, 260)], RED, sw=2.4)
s.path("M262,252 L262,268 L276,260 Z M276,252 L276,268", stroke=INK, sw=1.6, fill="#dddddd")
s.text(269, 244, "1N5819", size=10, anchor="middle")
s.text(212, 284, "stripe toward the XIAO", size=9.5, color="#555")
s.wire([(276, 260), (330, 260)], RED, sw=2.4)

# ---------------------------------------------------------------- XIAO
XX, XY, XW, XH = 330, 230, 170, 270
xl, xr = XX, XX + XW
box(XX, XY, XW, XH, "XIAO RP2040")
s.lines(XX + XW / 2, XY + XH + 16, ["3.3 V logic. Program it over USB-C", "with the power bank unplugged."], size=10, anchor="middle", color="#444")
pin(xl, 260, "5V", "in-left", RED)
pin(xl, 290, "GND", "in-left", BLACK)
pin(xl, 320, "3V3", "in-left", MAG)
pin(xr, 350, "D4", "in-right", GREEN)
pin(xr, 380, "D3", "in-right", GREEN)
pin(xr, 420, "D1", "in-right", GREEN)
pin(xr, 450, "D2", "in-right", GREEN)
s.circle(xr, 480, 3.2, fill="#ffffff", stroke=GREY, sw=1.4)
s.text(xr - 7, 484, "D6 (optional PRIME", size=10, anchor="end", color="#555")
s.text(xr - 7, 496, "button to GND)", size=10, anchor="end", color="#555")
s.wire([(xl, 290), (300, 290), (300, 304)], BLACK, sw=2)
s.gnd(300, 304)

# +5 V branch to U1 pin 14
dot(310, 260, RED)
s.wire([(310, 260), (310, 210), (700, 210), (700, 560)], RED, sw=2.2)
s.text(505, 204, "+5 V to U1 pin 14", size=10, color=RED, anchor="middle")

# ---------------------------------------------------------------- 74AHCT125 (U1)
AX, AY, AW, AH = 600, 560, 200, 150
box(AX, AY, AW, AH, "74AHCT125 (U1)", ["3.3 V -> 5 V gate driver", "14 = +5 V, 7 = GND, 0.1 µF across", "OE pins 1, 4, 10, 13 -> GND", "unused inputs 9, 12 -> GND"], fill="#eef6ff")
s.text(706, 554, "pin 14", size=9.5, color=RED)
pin(AX, 640, "5  2A", "in-left", GREEN)
pin(AX + AW, 640, "2Y  6", "in-right", GREEN)
pin(AX, 680, "2  1A", "in-left", GREEN)
pin(AX + AW, 680, "1Y  3", "in-right", GREEN)
s.wire([(AX + AW / 2, AY + AH), (AX + AW / 2, GND_Y)], BLACK, sw=2)
s.text(AX + AW / 2 + 6, AY + AH + 14, "7", size=9.5)
dot(AX + AW / 2, GND_Y)

# D4 (light) -> 2A, D3 (pump) -> 1A, each with a 10 k pull-down so the outputs stay LOW while the XIAO boots
s.wire([(xr, 350), (585, 350), (585, 640), (AX, 640)], GREEN, sw=2)
s.wire([(xr, 380), (565, 380), (565, 680), (AX, 680)], GREEN, sw=2)
s.text(590, 344, "LIGHT", size=9.5, color=GREEN)
s.text(570, 374, "PUMP", size=9.5, color=GREEN)
dot(585, 470, GREEN); s.wire([(585, 470), (618, 470), (618, 484)], GREEN, sw=1.6); resistor_v(618, 484, "10 k")
dot(565, 470, GREEN); s.wire([(565, 470), (545, 470), (545, 484)], GREEN, sw=1.6); resistor_v(545, 484, "10 k")


# ---------------------------------------------------------------- MOSFET stages + loads
def stage(cx_load, load, sub, gate_y, mosfet_label, flyback):
    lx0 = cx_load - 70
    box(lx0, 250, 140, 70, load, sub, fill="#fff7e6")
    plus_x, minus_x = cx_load - 40, cx_load + 40
    s.wire([(plus_x, RAIL12), (plus_x, 250)], ORANGE, sw=2.4)
    dot(plus_x, RAIL12, ORANGE)
    s.text(plus_x + 5, 246, "+", size=12, weight="bold", color=ORANGE)
    mx, my = cx_load - 30, gate_y - 56
    s.wire([(minus_x, 320), (minus_x, my)], BLACK, sw=2.4)
    s.text(minus_x + 6, 336, "-", size=13, weight="bold")
    s.rect(mx, my, 100, 76, fill="#f0f0f0", sw=1.4, rx=4)
    s.text(mx + 50, my + 30, mosfet_label, size=12, anchor="middle", weight="bold")
    s.text(mx + 50, my + 45, "IRLZ44N", size=9.5, anchor="middle", color="#444")
    pin(mx + 70, my, "D", "below")
    pin(mx, gate_y, "G", "in-left")
    pin(mx + 70, my + 76, "S", "above")
    s.wire([(mx + 70, my + 76), (mx + 70, GND_Y)], BLACK, sw=2.4)
    dot(mx + 70, GND_Y)
    s.wire([(AX + AW, gate_y), (mx, gate_y)], GREEN, sw=2)
    if flyback:
        fx = cx_load + 100
        s.wire([(plus_x, 236), (fx, 236), (fx, 262)], ORANGE, sw=1.6)
        dot(plus_x, 236, ORANGE)
        s.path(f"M{fx-8},{276} L{fx+8},{276} L{fx},{262} Z M{fx-8},{262} L{fx+8},{262}", stroke=INK, sw=1.5, fill="#dddddd")
        s.wire([(fx, 276), (fx, 380), (minus_x, 380)], BLACK, sw=1.6)
        dot(minus_x, 380)
        s.lines(fx + 10, 290, ["1N5819", "flyback,", "stripe to +12 V"], size=9.5)


stage(900, "Green LED strip", ["plain 12 V, 75 cm in 15 pieces,", "all in parallel, ~0.35 A"], 640, "Q2 light", False)
stage(1070, "Kamoer KPHM200", ["12 V peristaltic pump", "~0.7 A"], 680, "Q1 pump", True)

# ---------------------------------------------------------------- charging socket (dashed group)
s.rect(30, 560, 440, 200, fill="none", stroke=GREY, sw=1.2, rx=8, dash="6,4")
s.rect(38, 568, 392, 17, fill="#ffffff", stroke="#ffffff", sw=0)
s.text(42, 581, "the lock (on the lock wall in the sphere): one cable down behind the wall to the base", size=11, weight="bold", color="#555")
box(40, 590, 190, 70, "DRV5032 Hall sensor", ["Adafruit 6051. Chip on the", "rotor axis, under the magnet"], fill="#f3e8ff")
pin(230, 610, "VIN", "in-right", MAG)
pin(230, 628, "OUT", "in-right", GREEN)
pin(230, 646, "GND", "in-right", BLACK)
s.wire([(230, 610), (280, 610), (280, 320), (xl, 320)], MAG, sw=2)
s.wire([(230, 628), (515, 628), (515, 420), (xr, 420)], GREEN, sw=2)
s.wire([(230, 646), (250, 646), (250, GND_Y)], BLACK, sw=1.8)
dot(250, GND_Y)
box(40, 680, 190, 64, "D2F-L microswitch", ["pressed by the rotor cam", "at ~40 deg of twist"], fill="#f3e8ff")
pin(230, 702, "NO", "in-right", GREEN)
pin(230, 724, "COM", "in-right", BLACK)
s.wire([(230, 702), (525, 702), (525, 450), (xr, 450)], GREEN, sw=2)
s.wire([(230, 724), (240, 724), (240, GND_Y)], BLACK, sw=1.8)
dot(240, GND_Y)

# ---------------------------------------------------------------- notes
s.lines(24, GND_Y + 36, [
    "The pump and the LED strip are switched on their low side: + to the +12 V rail, - to the MOSFET drain, source to GND.",
    "The 10 k resistors keep both MOSFETs off while the XIAO boots. D1 and D2 use the XIAO's internal pull-ups.",
    "No master switch or fuse in this build: unplug the cable at the power bank to turn it off; the bank has its own overcurrent cut-out.",
], size=10.5, color="#333")

open(os.path.join(HERE, "..", "wiring.svg"), "w").write(s.finish())
print("written")
