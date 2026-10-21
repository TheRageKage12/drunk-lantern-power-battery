"""Battery seat and LED slot, dimensioned (numbers come from cad/params.py and cad/parts/base.py).

    python3 gen_battery_seat.py      # -> ../battery-seat.svg and ../battery-seat.png
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "cad"))
from svgkit import SVG, GREEN, GREY, INK
import params as P
from parts import base as B

W, H = 1180, 900
s = SVG(W, H, "Battery seat and LED slot")
BLUE, SLOT, PACK_FILL = "#1d4ed8", "#14532d", "#eef6ee"


def dim(x1, y1, x2, y2, label, side=0, color=BLUE, size=11, anchor="middle", dx=0, dy=0):
    """Dimension line with arrows at both ends; label at its middle, nudged by (dx, dy)."""
    s.path(f"M{x1},{y1} L{x2},{y2}", stroke=color, sw=1.1)
    for (ax, ay, bx, by) in ((x1, y1, x2, y2), (x2, y2, x1, y1)):
        s.path(f"M{bx},{by} L{ax},{ay}", stroke=color, sw=1.1, marker="arrB")
    s.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, label, size=size, anchor=anchor, color=color, weight="bold")


def ext(x1, y1, x2, y2):
    s.path(f"M{x1},{y1} L{x2},{y2}", stroke=GREY, sw=0.8, dash="3 3")


half_w, half_l = P.POWERBANK_W / 2, P.POWERBANK_L / 2
lx0, lx1 = P.PACK_LED_X
slot_c = -half_l + P.PACK_LED_IN                       # slot centre (y)
sy0, sy1 = slot_c - P.PACK_LED_SLOT / 2, slot_c + P.PACK_LED_SLOT / 2
from_port = (half_w - lx1, half_w - lx0)              # slot ends measured from the pack's port-side edge (x = +32.5)

s.text(20, 32, "Battery seat and LED slot: check these against the real battery before printing base_tray",
       size=18, weight="bold")
s.text(20, 52, "All sizes in mm. Generated from cad/params.py (PACK_*) and cad/parts/base.py; "
       "regenerate with docs/images/src/gen_battery_seat.py.", size=11, color="#555")

# ---------------------------------------------------------------- A: the cartridge floor from above
S, CX, CY = 3.0, 330, 450                            # px per mm, tray centre on the page
X = lambda x: CX - x * S                              # standing at the hand opening: -X is on your right
Y = lambda y: CY + y * S                              # -Y (the battery's port end) is away from you, at the top
s.text(30, 92, "A. Cartridge floor from above", size=15, weight="bold")
s.text(30, 110, "Standing at the hand opening, looking down. The battery lies LED face DOWN.", size=11, color="#555")
s.circle(CX, CY, B.TRAY_R * S, fill="#fafafa", stroke=INK, sw=1.4)
s.text(CX + B.TRAY_R * S * 0.72, CY + B.TRAY_R * S * 0.78, f"tray Ø{2 * B.TRAY_R:.1f}", size=11, color=GREY)
s.rect(X(half_w), Y(-half_l), P.POWERBANK_W * S, P.POWERBANK_L * S, fill=PACK_FILL, stroke=GREEN, sw=1.6, dash="6 4")
s.text(CX, CY + 10, "battery 65 x 105 x 25", size=12, anchor="middle", color=GREEN, weight="bold")
s.text(CX, CY + 26, "(centred on the tray)", size=10, anchor="middle", color=GREEN)
stop_y0 = -half_l - B.BANK_END_STOP_GAP - B.BANK_END_STOP_T
s.rect(X(half_w), Y(stop_y0), P.POWERBANK_W * S, B.BANK_END_STOP_T * S, fill="#9ca3af", stroke="none", sw=0)
s.text(X(-half_w) + 6, Y(stop_y0) - 6, "low end stop (3 mm tall)", size=9.5, color="#555")
s.rect(X(lx1), Y(sy0), (lx1 - lx0) * S, P.PACK_LED_SLOT * S, fill=SLOT, stroke=SLOT, sw=1)
s.text(X(lx0) + 8, Y(slot_c) + 4, "LED slot (through the floor)", size=10.5, color=SLOT, weight="bold")
for x, name in ((P.PACK_PORT_X, "port"), (P.PACK_SWITCH_X, "rocker")):
    s.circle(X(x), Y(-half_l) + 1, 4, fill=INK, stroke=INK)
    s.text(X(x), Y(-half_l) + 16, name, size=10, anchor="middle")
s.path(f"M{CX},{CY + B.TRAY_R * S + 34} L{CX},{CY + B.TRAY_R * S + 10}", stroke=INK, sw=1.4, marker="arrK")
s.text(CX, CY + B.TRAY_R * S + 50, "hand opening (you stand here)", size=11, anchor="middle")
s.text(CX, CY - B.TRAY_R * S - 12, "display side", size=11, anchor="middle")
# dimensions
dim(X(half_w), Y(half_l) + 22, X(-half_w), Y(half_l) + 22, "65", dy=14)
ext(X(half_w), Y(half_l), X(half_w), Y(half_l) + 28); ext(X(-half_w), Y(half_l), X(-half_w), Y(half_l) + 28)
dim(X(half_w) - 110, Y(-half_l), X(half_w) - 110, Y(half_l), "105", anchor="end", dx=-6)
ext(X(half_w), Y(-half_l), X(half_w) - 116, Y(-half_l)); ext(X(half_w), Y(half_l), X(half_w) - 116, Y(half_l))
dim(X(-half_w) + 40, Y(0), X(-half_w) + 40, Y(-half_l), "52.5 tray centre", anchor="start", dx=6, size=10)
s.text(X(-half_w) + 46, Y(-half_l / 2) + 14, "to the port end", size=10, color=BLUE, weight="bold")
ext(X(-half_w), Y(0), X(-half_w) + 46, Y(0))
dim(X(0), Y(stop_y0), X(0), Y(-B.TRAY_R), f"{B.TRAY_R - half_l:.1f} from the battery end to the rim", anchor="start", dx=6, size=10)
ext(X(-half_w), Y(-half_l), X(-half_w) + 46, Y(-half_l))
dim(X(lx1), Y(sy1) + 16, X(lx0), Y(sy1) + 16, f"{lx1 - lx0:.0f}", dy=13)
dim(X(half_w), Y(sy1) + 40, X(lx1), Y(sy1) + 40, f"{from_port[0]:.1f}", dy=13)
dim(X(lx0), Y(sy1) + 40, X(-half_w), Y(sy1) + 40, f"{half_w + lx0:.1f}", dy=13)
ext(X(lx1), Y(sy1), X(lx1), Y(sy1) + 46); ext(X(lx0), Y(sy1), X(lx0), Y(sy1) + 46)
dim(X(half_w) - 16, Y(-half_l), X(half_w) - 16, Y(slot_c), f"{P.PACK_LED_IN:.1f} to slot centre", anchor="end", dx=-6, size=10)
ext(X(half_w), Y(slot_c), X(half_w) - 22, Y(slot_c))
s.text(X(half_w) - 22, Y(sy1) + 6, f"slot {P.PACK_LED_SLOT:.0f} wide", size=10, anchor="end", color=BLUE)

# ---------------------------------------------------------------- B: the battery in your hand
S2, BX, BY = 6.0, 700, 730                            # px per mm; (BX, BY) = the battery's port-side corner of the end edge
U = lambda u: BX + u * S2                             # u: mm from the port-side edge (left, as you hold it)
V = lambda v: BY - v * S2                             # v: mm in from the end edge (the port/rocker end, toward you)
s.text(640, 92, "B. The battery in your hand", size=15, weight="bold")
s.text(640, 110, "LED face up, port end toward you, port on your left (how you measured it).", size=11, color="#555")
s.text(640, 126, "Measure the dots and check they sit inside the dashed slot outline.", size=11, color="#555")
L_SHOW = 42
s.path(f"M{U(0)},{V(L_SHOW)} L{U(0)},{V(0)} L{U(P.POWERBANK_W)},{V(0)} L{U(P.POWERBANK_W)},{V(L_SHOW)}",
       stroke=GREEN, sw=1.8, fill=PACK_FILL)
s.path(f"M{U(0)},{V(L_SHOW)} L{U(P.POWERBANK_W)},{V(L_SHOW)}", stroke=GREEN, sw=1, dash="2 5")
s.text(U(P.POWERBANK_W / 2), V(L_SHOW) - 8, "rest of the battery (105 long)", size=10, anchor="middle", color=GREEN)
s.text(U(P.POWERBANK_W / 2), V(0) + 54, "end face: port and rocker", size=10.5, anchor="middle", color=INK)
for u, name in ((half_w - P.PACK_PORT_X, "port"), (half_w - P.PACK_SWITCH_X, "rocker")):
    s.circle(U(u), V(0) + 8, 5, fill=INK, stroke=INK)
    s.text(U(u), V(0) + 28, name, size=10, anchor="middle")
u0, u1 = from_port
s.rect(U(u0), V(P.PACK_LED_IN + P.PACK_LED_SLOT / 2), (u1 - u0) * S2, P.PACK_LED_SLOT * S2,
       fill="none", stroke=SLOT, sw=1.6, dash="6 3")
s.text(U(u1) + 8, V(P.PACK_LED_IN) + 4, "floor slot lands here", size=10.5, color=SLOT, weight="bold")
PHOTO_DOTS = (14.7, 21.4, 27.7, 33.9, 40.6)           # from the end face's left edge, scaled off TalentCell's photo
for u in PHOTO_DOTS:
    s.circle(U(u), V(P.PACK_LED_IN), 3.2, fill="#22c55e", stroke="#15803d", sw=1)
s.text(U(2), V(L_SHOW) + 18, "5 LED dots: 12.7 in and 25.4 long are your numbers; their", size=10, color="#15803d")
s.text(U(2), V(L_SHOW) + 31, "position across the battery is estimated from TalentCell's photo", size=10, color="#15803d")
# dimensions
dim(U(0), V(0) + 72, U(half_w - P.PACK_PORT_X), V(0) + 72, f"{half_w - P.PACK_PORT_X:.1f}", dy=13)
dim(U(0), V(0) + 100, U(half_w - P.PACK_SWITCH_X), V(0) + 100, f"{half_w - P.PACK_SWITCH_X:.1f}", dy=13)
dim(U(0), V(0) + 128, U(P.POWERBANK_W), V(0) + 128, "65", dy=13)
dim(U(0), V(P.PACK_LED_IN + 7), U(u0), V(P.PACK_LED_IN + 7), f"{u0:.1f}", dy=-5)
dim(U(0), V(P.PACK_LED_IN + 14), U(u1), V(P.PACK_LED_IN + 14), f"{u1:.1f}", dy=-5)
ext(U(u0), V(P.PACK_LED_IN + 3), U(u0), V(P.PACK_LED_IN + 9)); ext(U(u1), V(P.PACK_LED_IN + 3), U(u1), V(P.PACK_LED_IN + 16))
dim(U(P.POWERBANK_W) + 20, V(0), U(P.POWERBANK_W) + 20, V(P.PACK_LED_IN), f"{P.PACK_LED_IN:.1f}", anchor="start", dx=6)
dim(U(P.POWERBANK_W) + 64, V(P.PACK_LED_IN - P.PACK_LED_SLOT / 2), U(P.POWERBANK_W) + 64, V(P.PACK_LED_IN + P.PACK_LED_SLOT / 2),
    f"{P.PACK_LED_SLOT:.0f}", anchor="start", dx=6)
ext(U(P.POWERBANK_W), V(P.PACK_LED_IN), U(P.POWERBANK_W) + 26, V(P.PACK_LED_IN))
ext(U(P.POWERBANK_W), V(0), U(P.POWERBANK_W) + 26, V(0))
s.lines(640, 160, [
    "Check:",
    f"  first dot at least {u0:.1f} from the left (port-side) edge",
    f"  last dot at most {u1:.1f} from the left edge",
    f"  dots {P.PACK_LED_IN - P.PACK_LED_SLOT / 2:.1f}-{P.PACK_LED_IN + P.PACK_LED_SLOT / 2:.1f} in from the end edge",
    "If a dot falls outside, send the numbers: the slot moves",
    "with PACK_LED_X / PACK_LED_IN in cad/params.py.",
], size=11.5, lh=17)

out = os.path.join(HERE, "..", "battery-seat.svg")
open(out, "w").write(s.finish())
try:
    import cairosvg
    cairosvg.svg2png(url=out, write_to=out[:-4] + ".png", output_width=2 * W)
except ImportError:
    print("cairosvg not installed: PNG not written")
print("written")
