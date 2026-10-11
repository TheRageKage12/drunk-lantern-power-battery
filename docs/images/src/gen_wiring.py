"""Generates ../wiring.svg (Green Lantern power battery - wiring diagram).

Run:  python3 gen_wiring.py      (needs only the Python stdlib; svgkit.py sits beside it)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK  # noqa: E402

OUT = os.path.join(HERE, "..", "wiring.svg")
MAG = "#b5179e"   # 3V3
W, H = 1100, 925
s = SVG(W, H, "Green Lantern power battery - wiring diagram")


# ------------------------------------------------------------------ local helpers
def vhops(x, y1, y2, hops, color, sw=2):
    """vertical wire from y1 (top) to y2 (bottom) with hop arcs at the given y's"""
    d = f"M{x},{y1}"
    for hy in sorted(hops):
        d += f" L{x},{hy - 6} A6,6 0 0 1 {x},{hy + 6}"
    d += f" L{x},{y2}"
    s.path(d, stroke=color, sw=sw)


def gnd_up(x, y, color=BLACK):
    """ground symbol whose bottom touches (x, y), pointing up"""
    s.path(f"M{x - 8},{y} L{x + 8},{y} M{x - 5.3},{y - 5} L{x + 5.3},{y - 5} M{x - 2},{y - 10} L{x + 2},{y - 10}",
           stroke=color, sw=2)


def diode_h(xa, xk, y, color, label=None, lab_dy=-9, size=8):
    """horizontal diode, anode at xa, cathode (bar) at xk; the wire ends are drawn by the caller"""
    direction = 1 if xk > xa else -1
    tip = xk - direction * 2
    base = tip - direction * 14
    s.path(f"M{base},{y - 6} L{base},{y + 6} L{tip},{y} Z", stroke=INK, sw=1.2, fill="#ffffff")
    s.path(f"M{tip},{y - 6} L{tip},{y + 6}", stroke=INK, sw=2)
    s.wire([(xa, y), (base, y)], color)
    s.wire([(tip, y), (xk, y)], color)
    if label:
        s.text((xa + xk) / 2, y + lab_dy, label, size=size, anchor="middle")


def buffer_gate(x, y, name, pin_in, pin_out, pin_oe, point_right=True, oe_up=False):
    """AHCT125 channel as a tri-state buffer triangle, 32 px wide, centred on y"""
    if point_right:
        s.path(f"M{x},{y - 13} L{x},{y + 13} L{x + 32},{y} Z", stroke=INK, sw=1.4, fill="#ffffff")
        xin, xout = x, x + 32
    else:
        s.path(f"M{x + 32},{y - 13} L{x + 32},{y + 13} L{x},{y} Z", stroke=INK, sw=1.4, fill="#ffffff")
        xin, xout = x + 32, x
    s.text(xin + (-5 if point_right else 5), y - 4, str(pin_in), size=8, anchor="end" if point_right else "start")
    s.text(xout + (5 if point_right else -5), y - 4, str(pin_out), size=8, anchor="start" if point_right else "end")
    s.text(x + 16, y + (-18 if not oe_up else 24), name, size=8.5, anchor="middle", weight="bold")
    # active-low OE pin with a bubble, tied to GND
    px = x + 16
    if oe_up:
        s.circle(px, y - 9, 2.5, fill="#ffffff", sw=1)
        s.wire([(px, y - 11.5), (px, y - 20)], BLACK)
        gnd_up(px, y - 20)
        s.text(px + 5, y - 15, str(pin_oe), size=8)
    else:
        s.circle(px, y + 9, 2.5, fill="#ffffff", sw=1)
        s.wire([(px, y + 11.5), (px, y + 20)], BLACK)
        s.gnd(px, y + 20)
        s.text(px + 5, y + 18, str(pin_oe), size=8)


# ------------------------------------------------------------------ title + legend
s.text(20, 32, "Green Lantern power battery — wiring diagram", size=20, weight="bold")
lx = 20
for col, lab, w in ((RED, "+5 V bus", 30), (ORANGE, "+12 V bus", 30), (MAG, "3V3 (Hall)", 30), (BLACK, "GND", 30), (GREEN, "logic signal (arrow = direction)", 30)):
    s.wire([(lx, 52), (lx + w, 52)], col)
    s.text(lx + w + 6, 56, lab, size=11)
    lx += w + 6 + int(len(lab) * 6.2) + 18
s.gnd(lx + 8, 46)
s.text(lx + 22, 56, "= common ground (all tied together)", size=11)
lx += 22 + 200
s.dot(lx + 4, 52, GREEN)
s.text(lx + 12, 56, "junction", size=11)
lx += 12 + 62
s.path(f"M{lx},60 L{lx},57 A6,6 0 0 1 {lx},45 L{lx},43", stroke=RED, sw=2)
s.wire([(lx - 10, 51), (lx + 10, 51)], GREEN)
s.text(lx + 16, 56, "hop = no connection", size=11)

# ------------------------------------------------------------------ dashed group boxes
BX0, BX1, BY0, BY1 = 20, 700, 76, 903
s.rect(BX0, BY0, BX1 - BX0, BY1 - BY0, fill="none", stroke=GREY, sw=1.2, dash="7,5", rx=6)
s.text(BX0 + 8, 70, "BASE DRUM — power bank, PD cable, master switch, fuses, buck, electronics tray, pump", size=11, weight="bold", color="#444")
SX0, SX1, SY0, SY1 = 736, 1090, 76, 524
s.rect(SX0, SY0, SX1 - SX0, SY1 - SY0, fill="none", stroke=GREY, sw=1.2, dash="7,5", rx=6)
s.text(SX0, 70, "CHARGING SOCKET MODULE (top dish) — 6-wire connector J1", size=11, weight="bold", color="#444")
PX0, PX1, PY0, PY1 = 736, 1090, 548, 903
s.rect(PX0, PY0, PX1 - PX0, PY1 - PY0, fill="none", stroke=GREY, sw=1.2, dash="7,5", rx=6)
s.text(PX0, 542, "SPHERE — WS2812B strip behind the diffuser — 3-wire connector J2", size=11, weight="bold", color="#444")

# ------------------------------------------------------------------ power bank (one USB-C PD port, 12 V PDO)
s.rect(40, 88, 130, 142, rx=6, sw=1.4)
s.text(105, 112, "INIU B61", size=12, anchor="middle", weight="bold")
s.text(105, 126, "USB-C PD power bank", size=10, anchor="middle")
s.text(105, 138, "(offers a 12 V PDO)", size=9, anchor="middle", color="#555")
s.text(105, 158, "USB-A port: unused", size=8.5, anchor="middle", color="#777")
s.rect(160, 173, 12, 14, fill="#ddd", sw=1)
s.text(156, 203, "USB-C PD", size=10, anchor="end")
s.wire([(100, 230), (100, 246)], BLACK)
s.gnd(100, 246)
s.text(110, 258, "cable −", size=9, color="#555")

# PD trigger cable -> master switch -> F1 -> 12 V bus
s.wire([(172, 180), (185, 180)], ORANGE)
s.rect(185, 168, 60, 24, rx=4, fill="#fff3e0", sw=1.2)
s.text(215, 184, "PD trigger", size=10, anchor="middle")
s.wire([(245, 180), (260, 180)], ORANGE)
s.text(185, 252, "USB-C PD trigger cable, set to 12 V", size=10)

s.rect(260, 150, 70, 60, rx=4, sw=1.4)
s.wire([(260, 180), (272, 180)], ORANGE)
s.path("M272,180 L302,166", stroke=INK, sw=1.8)
s.dot(272, 180, INK, r=2.5)
s.dot(302, 180, INK, r=2.5)
s.wire([(302, 180), (330, 180)], ORANGE)
s.text(295, 224, "master power switch", size=11, anchor="middle")
s.text(295, 237, "SPST rocker (DPST fine too)", size=10, anchor="middle")

s.wire([(330, 180), (345, 180)], ORANGE)
s.rect(345, 174, 50, 12, sw=1.4)
s.path("M345,180 L395,180", stroke=INK, sw=1)
s.text(370, 166, "F1  2 A slow-blow", size=10, anchor="middle")
s.wire([(395, 180), (470, 180), (470, 165)], ORANGE)
s.dot(420, 180, ORANGE)
s.wire([(420, 180), (420, 280), (60, 280), (60, 390), (80, 390)], ORANGE)
s.text(300, 275, "+12 V bus", size=10, color=ORANGE, weight="bold")

# C2 2200 uF across the 12 V bus at the D4184 input
s.dot(130, 280, ORANGE)
s.wire([(130, 280), (130, 296)], ORANGE)
s.path("M120,296 L140,296 M120,303 L140,303", stroke=INK, sw=2.2)
s.wire([(130, 303), (130, 316)], BLACK)
s.gnd(130, 316)
s.text(142, 300, "C2 2200 µF 16 V", size=9)
s.text(142, 311, "(at the D4184 input)", size=8.5, color="#555")

# ------------------------------------------------------------------ buck 12 V -> 5 V, F2, 5 V bus
s.rect(440, 130, 80, 35, rx=4, fill="#fff3e0", sw=1.4)
s.text(480, 144, "Pololu D24V22F5", size=9, anchor="middle", weight="bold")
s.text(480, 156, "buck 12 V → 5 V, 2.5 A", size=8.5, anchor="middle")
s.pin(470, 165, ORANGE); s.text(476, 176, "VIN", size=7.5, color="#555")
s.pin(440, 148); s.wire([(440, 148), (425, 148)], BLACK); s.gnd(425, 148)
s.pin(500, 130, RED); s.text(506, 125, "VOUT", size=7.5, color="#555")
s.wire([(500, 130), (500, 110), (520, 110)], RED)
s.rect(520, 104, 50, 12, sw=1.4)
s.path("M520,110 L570,110", stroke=INK, sw=1)
s.text(545, 98, "F2  3 A", size=10, anchor="middle")
s.wire([(570, 110), (1062, 110), (1062, 390), (940, 390)], RED, sw=2.4)
s.text(700, 99, "+5 V bus", size=10, color=RED, weight="bold", anchor="middle")

# C1 1000 uF across the 5 V bus
s.dot(600, 110, RED)
s.wire([(600, 110), (600, 128)], RED)
s.path("M590,128 L610,128 M590,135 L610,135", stroke=INK, sw=2.2)
s.wire([(600, 135), (600, 148)], BLACK)
s.gnd(600, 148)
s.text(592, 126, "C1 1000 µF ≥10 V", size=9, anchor="end")
s.text(592, 137, "(next to the LEDs)", size=8.5, anchor="end", color="#555")

# ------------------------------------------------------------------ XIAO RP2040
XL, XR, XT = 520, 620, 330
s.rect(XL, XT, 100, 230, rx=8, sw=1.8, fill="#f7f7f7")
s.rect(548, 322, 44, 14, rx=4, fill="#cfcfcf", sw=1)
s.text(570, 349, "USB-C", size=8, anchor="middle", color="#555")
s.text(570, 436, "XIAO", size=13, anchor="middle", weight="bold")
s.text(570, 452, "RP2040", size=13, anchor="middle", weight="bold")
s.text(570, 466, "top view, USB-C up", size=8, anchor="middle", color="#555")
s.text(570, 490, "3.3 V logic only", size=8, anchor="middle", color="#555")
lpins = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]
rpins = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
for i in range(7):
    y = 370 + i * 26
    used_l = i in (1, 2, 3, 4, 5, 6)
    used_r = i in (0, 1, 2)
    s.pin(XL, y, INK if used_l else GREY)
    s.pin(XR, y, INK if used_r else GREY)
    s.text(XL + 7, y + 3.5, lpins[i], size=9, color=INK if used_l else GREY, weight="bold" if used_l else "normal")
    s.text(XR - 7, y + 3.5, rpins[i], size=9, anchor="end", color=INK if used_r else GREY, weight="bold" if used_r else "normal")

# XIAO power: 5 V bus -> 1N5819 -> 5V pin (anode on the bus side)
vhops(660, 110, 600, [194, 222, 422], RED)        # bus drop; continues down to the U1 power stub
s.dot(660, 110, RED); s.dot(660, 370, RED)
diode_h(660, 620, 370, RED, label="1N5819", lab_dy=-10)
s.text(640, 386, "USB programming OK", size=7, anchor="middle", color="#555")
s.wire([(660, 600), (640, 600)], RED)
s.wire([(620, 396), (634, 396)], BLACK)
s.gnd(634, 396)
vhops(676, 166, 422, [194, 222], MAG)
s.wire([(620, 422), (676, 422)], MAG)
s.wire([(676, 166), (726, 166)], MAG)

# XIAO signals
s.arrow([(726, 194), (490, 194), (490, 396), (520, 396)], GREEN, sw=2)   # D1 <- Hall
s.arrow([(726, 222), (470, 222), (470, 422), (520, 422)], GREEN, sw=2)   # D2 <- switch
s.text(498, 189, "HALL (LOW = ring present)", size=9, color=GREEN)
s.text(498, 217, "SW (active LOW, INPUT_PULLUP)", size=9, color=GREEN)
# D3 -> 10 k pull-down -> U1C (pins 9 -> 8, OE 10) -> D4184 PWM/TRIG
s.wire([(520, 448), (332, 448)], GREEN)
s.dot(400, 448, GREEN)
s.wire([(400, 448), (400, 436)], GREEN)
s.rect(394, 412, 12, 24, sw=1.3)
s.wire([(400, 412), (400, 404)], BLACK)
gnd_up(400, 404)
s.text(410, 428, "10 kΩ", size=9)
s.text(410, 439, "pull-down", size=8, color="#555")
buffer_gate(300, 448, "U1C", 9, 8, 10, point_right=False, oe_up=True)
s.arrow([(300, 448), (240, 448)], GREEN, sw=2)
s.text(432, 443, "PUMP (HIGH = on)", size=9, color=GREEN)
# D4 -> U1A -> 330 R -> ring DIN ; D5 -> U1B -> 330 R -> strip DIN
s.wire([(520, 474), (275, 474), (275, 638), (300, 638)], GREEN)
s.wire([(520, 500), (258, 500), (258, 700), (300, 700)], GREEN)
buffer_gate(300, 638, "U1A", 2, 3, 1)
buffer_gate(300, 700, "U1B", 5, 6, 4)
s.res_h(332, 420, 638, "330 Ω", GREEN)
s.arrow([(420, 638), (690, 638), (690, 250), (726, 250)], GREEN, sw=2)
s.text(440, 633, "RING DIN", size=9, color=GREEN)
s.res_h(332, 420, 700, "330 Ω", GREEN)
s.arrow([(420, 700), (726, 700)], GREEN, sw=2)
s.text(440, 695, "STRIP DIN", size=9, color=GREEN)
# D6 <- PRIME momentary button to GND
s.wire([(520, 526), (470, 526)], GREEN)
s.pin(470, 526); s.pin(440, 526)
s.path("M474,517 L436,517 M455,517 L455,509", stroke=INK, sw=1.8)
s.wire([(440, 526), (420, 526)], BLACK)
s.gnd(420, 526)
s.text(290, 573, "PRIME button (momentary, in the base door panel):", size=9)
s.text(290, 585, "hold = pump runs, only when idle. D6 INPUT_PULLUP, active LOW.", size=9)

# U1 power stub
s.rect(500, 582, 140, 44, rx=4, fill="#f7f7f7", sw=1.2)
s.text(570, 595, "U1 SN74AHCT125N power", size=8.5, anchor="middle", weight="bold")
s.text(570, 606, "pin 14 VCC ← 5 V bus, pin 7 → GND", size=8, anchor="middle")
s.text(570, 617, "ch. 4 unused: pins 12, 13 → GND", size=8, anchor="middle")
s.pin(640, 600, RED)
s.pin(530, 626); s.wire([(530, 626), (530, 636)], BLACK); s.gnd(530, 636)

# ------------------------------------------------------------------ D4184 module, flyback diode, J3, pump
s.rect(80, 360, 160, 120, rx=4, sw=1.4)
s.text(160, 400, "D4184", size=12, anchor="middle", weight="bold")
s.text(160, 414, "dual MOSFET", size=10, anchor="middle")
s.text(160, 426, "trigger module", size=10, anchor="middle")
s.pin(80, 390); s.text(86, 393, "DC+", size=9)
s.pin(80, 420); s.text(86, 423, "DC−", size=9)
s.pin(240, 410); s.text(234, 413, "GND", size=9, anchor="end")
s.pin(240, 448); s.text(234, 451, "PWM/TRIG", size=9, anchor="end")
s.pin(120, 480); s.text(120, 474, "OUT+", size=9, anchor="middle")
s.pin(200, 480); s.text(200, 474, "OUT−", size=9, anchor="middle")
s.wire([(80, 420), (62, 420)], BLACK); s.gnd(62, 420)
s.wire([(240, 410), (266, 410)], BLACK); s.gnd(266, 410)
s.wire([(120, 480), (120, 530)], ORANGE)
s.wire([(200, 480), (200, 530)], ORANGE)
# flyback diode across the motor terminals: anode at OUT-, cathode (bar) at OUT+
s.dot(120, 500, ORANGE); s.dot(200, 500, ORANGE)
diode_h(200, 120, 500, ORANGE)
s.text(160, 492, "1N5819 flyback", size=8, anchor="middle")
s.text(160, 514, "(bar = cathode to OUT+)", size=7.5, anchor="middle", color="#555")
# J3 2-pin pump connector
s.rect(104, 522, 112, 16, rx=4, fill="#e6e6e6", sw=1.2)
s.pin(120, 530, ORANGE, r=3.5); s.pin(200, 530, ORANGE, r=3.5)
s.text(160, 534, "J3  2-pin", size=8, anchor="middle", weight="bold")
s.wire([(120, 538), (120, 548)], ORANGE)
s.wire([(200, 538), (200, 548)], ORANGE)
# pump
s.rect(90, 548, 140, 62, rx=10, sw=1.4)
s.text(112, 561, "+", size=11, anchor="middle", weight="bold")
s.text(208, 561, "−", size=11, anchor="middle", weight="bold")
s.text(160, 579, "Kamoer KPHM200", size=11, anchor="middle", weight="bold")
s.text(160, 592, "peristaltic pump, 12 V DC", size=9, anchor="middle")
s.text(160, 604, "200 mL/min, ~0.7 A (swap leads = reverse)", size=8, anchor="middle", color="#555")

# ------------------------------------------------------------------ DIP-14 pinout inset
s.rect(30, 625, 215, 250, fill="#fafafa", stroke=GREY, sw=1, dash="4,3", rx=4)
s.text(137, 640, "U1 SN74AHCT125N — DIP-14, top view, notch up", size=9, anchor="middle", weight="bold")
s.rect(105, 652, 60, 210, rx=2, sw=1.4, fill="#eeeeee")
s.path("M129,652 A6,6 0 0 0 141,652", stroke=INK, sw=1.4)
s.dot(112, 662, INK, r=2.5)
left = ["1  1OE→GND", "2  1A←D4", "3  1Y→ring", "4  2OE→GND", "5  2A←D5", "6  2Y→strip", "7  GND"]
right = ["14 VCC +5 V", "13 4OE→GND", "12 4A→GND", "11 4Y n/c", "10 3OE→GND", "9  3A←D3", "8  3Y→pump"]
for i in range(7):
    y = 668 + i * 30
    s.path(f"M95,{y} L105,{y} M165,{y} L175,{y}", stroke=INK, sw=2)
    s.text(92, y + 3, left[i], size=8.5, anchor="end")
    s.text(178, y + 3, right[i], size=8.5)
s.text(135, 760, "74", size=9, anchor="middle", color="#666")
s.text(135, 771, "AHCT", size=9, anchor="middle", color="#666")
s.text(135, 782, "125", size=9, anchor="middle", color="#666")

# ------------------------------------------------------------------ alternative insets
# alt Hall: 5 V A3144 module with the diode interface
s.rect(255, 790, 220, 105, fill="#fffdf5", stroke=GREY, sw=1, dash="4,3", rx=4)
s.text(263, 804, "alternative: 5 V A3144 Hall module", size=10, weight="bold")
s.text(263, 816, "diode interface, no divider; D1 stays INPUT_PULLUP", size=8.5, color="#555")
s.rect(263, 822, 56, 60, rx=3, sw=1.2)
s.text(291, 840, "A3144", size=9, anchor="middle", weight="bold")
s.text(291, 851, "module", size=9, anchor="middle")
s.text(291, 862, "(5 V)", size=9, anchor="middle")
s.pin(319, 830); s.wire([(319, 830), (345, 830)], RED); s.text(349, 833, "5 V bus", size=9, color=RED)
s.pin(319, 850)
diode_h(400, 319, 850, GREEN)           # anode toward D1 (right), cathode at the module OUT (left)
s.text(360, 840, "1N5819", size=8, anchor="middle")
s.arrow([(400, 850), (455, 850)], GREEN, sw=2)
s.text(458, 853, "D1", size=9, color=GREEN, weight="bold")
s.text(360, 869, "anode → D1, cathode → OUT:", size=7.5, anchor="middle", color="#555")
s.text(360, 879, "magnet pulls D1 to ~0.4 V, never 5 V", size=7.5, anchor="middle", color="#555")
s.pin(319, 870); s.wire([(319, 870), (335, 870), (335, 882)], BLACK); s.gnd(335, 882)
s.text(326, 828, "VCC", size=7.5, anchor="start", color="#555")
s.text(326, 847, "OUT", size=7.5, anchor="start", color="#555")
# alt pump: Adafruit 3910 on 5 V
s.rect(485, 790, 207, 105, fill="#fffdf5", stroke=GREY, sw=1, dash="4,3", rx=4)
s.text(493, 804, "alternative: Adafruit 3910 5 V pump", size=10, weight="bold")
s.text(493, 816, "no PD cable, no buck: plain 5 V/3 A USB-A → F2 → 5 V bus", size=8.5, color="#555")
s.rect(520, 826, 66, 56, rx=3, sw=1.2)
s.text(553, 848, "same", size=8, anchor="middle", weight="bold")
s.text(553, 858, "D4184", size=8, anchor="middle", weight="bold")
s.pin(520, 838); s.text(524, 841, "DC+", size=7.5)
s.pin(520, 866); s.text(524, 869, "DC−", size=7.5)
s.pin(586, 838); s.text(582, 841, "OUT+", size=7.5, anchor="end")
s.pin(586, 866); s.text(582, 869, "OUT−", size=7.5, anchor="end")
s.wire([(493, 838), (520, 838)], RED); s.text(493, 833, "5 V bus", size=7.5, color=RED)
s.wire([(520, 866), (505, 866)], BLACK); s.gnd(505, 866)
s.wire([(586, 838), (612, 838)], RED)
s.wire([(586, 866), (612, 866)], RED)
s.rect(612, 828, 74, 50, rx=8, sw=1.2)
s.text(649, 846, "Adafruit 3910", size=8, anchor="middle", weight="bold")
s.text(649, 857, "5 V peristaltic", size=8, anchor="middle")
s.text(649, 868, "~100 mL/min, ~2× slower", size=7.5, anchor="middle", color="#555")
s.text(493, 890, "keep the flyback diode and J3", size=7.5, color="#555")

# ------------------------------------------------------------------ J1 socket connector (6 wires)
s.rect(720, 96, 30, 168, rx=5, fill="#e6e6e6", sw=1.2)
j1 = [("5 V", 110, RED), ("GND", 138, BLACK), ("3V3", 166, MAG), ("HALL", 194, GREEN), ("SW", 222, GREEN), ("RING DIN", 250, GREEN)]
for lab, y, col in j1:
    s.pin(735, y, col, r=3.5)
    s.text(755, y - 4, lab, size=8.5, color=col, weight="bold")
s.text(735, 277, "J1  6-pin", size=8.5, anchor="middle", weight="bold")
s.text(735, 288, "(JST-XH)", size=8, anchor="middle", color="#555")
# 5 V trunk down the gutter to J2 (hops over the J1 signals)
s.dot(712, 110, RED)
vhops(712, 110, 644, [166, 194, 222, 250], RED)
s.wire([(712, 644), (720, 644)], RED)
# J1 GND on the socket side
s.wire([(750, 138), (768, 138)], BLACK); s.gnd(768, 138)

# ---- DRV5032 Hall breakout (3V3 + OUT straight to D1)
s.rect(820, 146, 140, 64, rx=4, sw=1.4)
s.text(905, 163, "Adafruit DRV5032", size=10, anchor="middle", weight="bold")
s.text(905, 176, "Hall breakout #6051", size=9, anchor="middle")
s.text(905, 189, "omnipolar · 3.3 V OUT", size=8, anchor="middle", color="#555")
s.text(905, 202, "LOW when the magnet is near", size=8, anchor="middle", color="#555")
s.pin(820, 166, MAG); s.text(826, 169, "VIN", size=8.5, color=MAG)
s.pin(820, 194); s.text(826, 197, "OUT", size=8.5)
s.pin(960, 200); s.wire([(960, 200), (978, 200)], BLACK); s.gnd(978, 200); s.text(946, 197, "GND", size=8, anchor="end")
s.wire([(750, 166), (820, 166)], MAG)
s.wire([(750, 194), (820, 194)], GREEN)

# ---- microswitch
s.rect(820, 214, 140, 56, rx=4, sw=1.4)
s.text(905, 234, "D2F-L", size=10, anchor="middle", weight="bold")
s.text(905, 246, "lever microswitch", size=9, anchor="middle")
s.text(905, 258, "cam presses it at ~40°", size=8, anchor="middle", color="#555")
s.pin(820, 222); s.text(826, 225, "NO", size=8.5)
s.pin(820, 240); s.text(826, 243, "COM", size=8.5)
s.pin(820, 258, GREY); s.text(826, 261, "NC n/c", size=8, color=GREY)
s.wire([(750, 222), (820, 222)], GREEN)
s.wire([(820, 240), (800, 240)], BLACK); s.gnd(800, 240)
# magnet hint
s.rect(975, 232, 26, 10, fill="#9e9e9e", sw=1)
s.text(988, 240, "N S", size=7, anchor="middle", color="#fff", weight="bold")
s.text(975, 256, "6×2 mm magnet", size=8, color="#555")
s.text(975, 267, "in the ring key,", size=8, color="#555")
s.text(975, 278, "on the rotor axis", size=8, color="#555")

# ---- NeoPixel ring
CX, CY = 880, 390
s.circle(CX, CY, 60, fill="#e8f5e9", sw=1.4)
s.circle(CX, CY, 46, fill="#ffffff", sw=1.2)
for k in range(24):
    a = 2 * math.pi * k / 24
    s.circle(CX + 53 * math.cos(a), CY + 53 * math.sin(a), 3.2, fill="#4caf50", stroke="none")
s.text(CX, CY - 2, "24-px", size=10, anchor="middle", weight="bold")
s.text(CX, CY + 10, "NeoPixel ring", size=9, anchor="middle")
s.pin(820, 390); s.pin(940, 390); s.pin(880, 450)
s.arrow([(750, 250), (772, 250), (772, 390), (818, 390)], GREEN, sw=2)
s.text(800, 384, "DIN", size=8.5, anchor="middle", color=GREEN, weight="bold")
s.text(975, 384, "5 V", size=8.5, color=RED, weight="bold")
s.wire([(880, 450), (880, 460)], BLACK); s.gnd(880, 460)
s.text(892, 466, "GND", size=8.5)
s.text(952, 436, "Adafruit #1586", size=9)
s.text(952, 447, "24-px ring, 65.5 OD", size=9)
s.text(952, 458, "under the halo", size=9)
# socket note
s.lines(743, 476, [
    "Hall: Adafruit DRV5032 breakout (#6051) runs from the XIAO 3V3 and",
    "its OUT is 3.3 V logic → straight to D1 with INPUT_PULLUP, no divider.",
    "Optional at the XIAO end of HALL: 10 k pull-up to 3V3 + 100 nF to GND.",
    "Omnipolar: magnet pole orientation does not matter. The magnet sits",
    "on the rotor axis, so twisting the ring never moves it off the sensor.",
], size=8.5, color="#333", lh=10.5)

# ------------------------------------------------------------------ J2 sphere connector + strip
s.rect(720, 630, 30, 84, rx=5, fill="#e6e6e6", sw=1.2)
for lab, y, col in (("5 V", 644, RED), ("GND", 672, BLACK), ("DIN", 700, GREEN)):
    s.pin(735, y, col, r=3.5)
    s.text(755, y - 4, lab, size=8.5, color=col, weight="bold")
s.text(735, 727, "J2  3-pin", size=8.5, anchor="middle", weight="bold")
s.wire([(750, 644), (790, 644)], RED)
s.wire([(750, 672), (790, 672)], BLACK); s.gnd(770, 674)
s.arrow([(750, 700), (788, 700)], GREEN, sw=2)
s.rect(790, 624, 250, 92, rx=4, sw=1.4, fill="#f7f7f7")
s.pin(790, 644, RED); s.text(796, 647, "5V", size=8.5, weight="bold")
s.pin(790, 672, BLACK); s.text(796, 675, "GND", size=8.5, weight="bold")
s.pin(790, 700, GREEN); s.text(796, 703, "DIN", size=8.5, weight="bold")
s.text(930, 640, "WS2812B strip, 5 V, 60 px", size=10, anchor="middle", weight="bold")
for i in range(9):
    s.rect(836 + i * 22, 656, 14, 14, fill="#4caf50", stroke="none", rx=2)
    s.path(f"M{843 + i * 22},677 L{843 + i * 22},682", stroke="#4caf50", sw=1)
s.arrow([(836, 688), (1020, 688)], GREY, sw=1)
s.text(930, 709, "data flows this way — DIN is the end nearest the connector", size=8, anchor="middle", color="#555")
s.lines(743, 752, [
    "Set STRIP_COUNT in the sketch to the real pixel count. Keep the two data",
    "wires short and twisted with GND; the 330 Ω resistors sit at the U1 end.",
    "Power: 24 + 60 px at maxBright 160 can draw ~2 A on the 5 V bus → buck",
    "2.5 A, F2 3 A, C1 1000 µF by the LEDs; pump + LEDs ≈ 1.5 A on 12 V → F1 2 A.",
], size=8.5, color="#333", lh=11)
s.lines(743, 812, [
    "COMMON GROUND: every ground symbol is the same net. Tie together:",
    "cable −, buck GND, D4184 DC− and GND, XIAO GND, U1 pin 7 (+ OE pins and",
    "the unused 4A/4OE), DRV5032 GND, switch COM, PRIME button, ring GND,",
    "strip GND, the 10 k pull-down, and the − ends of C1 and C2.",
], size=8.5, color="#333", lh=11)

with open(OUT, "w") as f:
    f.write(s.finish())
print("written", os.path.normpath(OUT))
