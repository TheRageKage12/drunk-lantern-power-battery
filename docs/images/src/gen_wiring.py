import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-temprepo/45c7fed5-b38c-5bcd-8935-8412da500de5/scratchpad")
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

MAG = "#b5179e"   # 3V3
W, H = 1100, 925
s = SVG(W, H, "Green Lantern power battery - wiring diagram")


def vhops(x, y1, y2, hops, color, sw=2):
    """vertical wire from y1 (top) to y2 (bottom) with hop arcs at the given y's"""
    d = f"M{x},{y1}"
    for hy in sorted(hops):
        d += f" L{x},{hy - 6} A6,6 0 0 1 {x},{hy + 6}"
    d += f" L{x},{y2}"
    s.path(d, stroke=color, sw=sw)


# ------------------------------------------------------------------ title + legend
s.text(20, 32, "Green Lantern power battery — wiring diagram", size=20, weight="bold")
lx = 20
for col, lab, w in ((RED, "+5 V", 30), (ORANGE, "+12 V (pump)", 30), (MAG, "3V3 (Hall)", 30), (BLACK, "GND", 30), (GREEN, "logic signal (arrow = direction)", 30)):
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
BX0, BX1, BY0, BY1 = 20, 694, 76, 903
s.rect(BX0, BY0, BX1 - BX0, BY1 - BY0, fill="none", stroke=GREY, sw=1.2, dash="7,5", rx=6)
s.text(BX0 + 8, 70, "BASE DRUM — power bank, master switch, fuses, electronics tray, pump", size=11, weight="bold", color="#444")
SX0, SX1, SY0, SY1 = 730, 1090, 76, 524
s.rect(SX0, SY0, SX1 - SX0, SY1 - SY0, fill="none", stroke=GREY, sw=1.2, dash="7,5", rx=6)
s.text(SX0, 70, "CHARGING SOCKET MODULE (top dish) — 6-wire connector J1", size=11, weight="bold", color="#444")
PX0, PX1, PY0, PY1 = 730, 1090, 548, 903
s.rect(PX0, PY0, PX1 - PX0, PY1 - PY0, fill="none", stroke=GREY, sw=1.2, dash="7,5", rx=6)
s.text(PX0, 542, "SPHERE — WS2812B strip behind the diffuser — 3-wire connector J2", size=11, weight="bold", color="#444")

# ------------------------------------------------------------------ power bank
s.rect(40, 88, 130, 142, rx=6, sw=1.4)
s.text(105, 143, "USB power bank", size=12, anchor="middle", weight="bold")
s.text(105, 157, "USB PD, two ports", size=10, anchor="middle")
s.text(105, 169, "(or 5 V + 5→12 V boost)", size=9, anchor="middle", color="#555")
s.rect(160, 103, 12, 14, fill="#ddd", sw=1)
s.text(156, 101, "USB-A 5 V", size=10, anchor="end")
s.rect(160, 173, 12, 14, fill="#ddd", sw=1)
s.text(156, 203, "USB-C PD", size=10, anchor="end")
s.wire([(100, 230), (100, 246)], BLACK)
s.gnd(100, 246)
s.text(110, 258, "− of both cables", size=9, color="#555")

# 5 V and 12 V lines to the switch
s.wire([(172, 110), (250, 110)], RED)
s.wire([(172, 180), (185, 180)], ORANGE)
s.rect(185, 168, 60, 24, rx=4, fill="#fff3e0", sw=1.2)
s.text(215, 184, "PD trigger", size=10, anchor="middle")
s.wire([(245, 180), (250, 180)], ORANGE)
s.text(185, 252, "USB-C PD trigger cable (set to 12 V)", size=10)

# ------------------------------------------------------------------ master switch (DPST)
s.rect(250, 88, 90, 116, rx=4, sw=1.4)
for y, col in ((110, RED), (180, ORANGE)):
    s.wire([(250, y), (268, y)], col)
    s.path(f"M268,{y} L300,{y - 14}", stroke=INK, sw=1.8)
    s.dot(268, y, INK, r=2.5)
    s.dot(300, y, INK, r=2.5)
    s.wire([(300, y), (340, y)], col)
s.path("M284,101 L284,173", stroke=INK, sw=1.2, dash="3,3")
s.text(295, 218, "master power switch", size=11, anchor="middle")
s.text(295, 231, "DPST rocker (or 2 × SPST)", size=10, anchor="middle")

# ------------------------------------------------------------------ fuses
for y, col, lab in ((110, RED, "F1  3 A"), (180, ORANGE, "F2  1.5 A")):
    s.wire([(340, y), (360, y)], col)
    s.rect(360, y - 6, 50, 12, sw=1.4)
    s.path(f"M360,{y} L410,{y}", stroke=INK, sw=1)
    s.text(385, y - 11, lab, size=10, anchor="middle")

# +5 V rail
s.wire([(410, 110), (1062, 110), (1062, 390), (940, 390)], RED, sw=2.4)
s.text(560, 104, "+5 V rail", size=10, color=RED, weight="bold")
# 12 V to D4184
s.wire([(410, 180), (445, 180), (445, 280), (60, 280), (60, 390), (80, 390)], ORANGE)
s.text(300, 275, "+12 V", size=10, color=ORANGE, weight="bold")

# capacitor across 5 V rail
s.dot(430, 110, RED)
s.wire([(430, 110), (430, 128)], RED)
s.path("M420,128 L440,128 M420,135 L440,135", stroke=INK, sw=2.2)
s.wire([(430, 135), (430, 148)], BLACK)
s.gnd(430, 148)
s.text(445, 125, "C1 1000 µF ≥10 V", size=10)
s.text(445, 137, "(+ to rail, next to the LEDs)", size=9, color="#555")

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
    used_l = i in (1, 2, 3, 4, 5)
    used_r = i in (0, 1, 2)
    s.pin(XL, y, INK if used_l else GREY)
    s.pin(XR, y, INK if used_r else GREY)
    s.text(XL + 7, y + 3.5, lpins[i], size=9, color=INK if used_l else GREY, weight="bold" if used_l else "normal")
    s.text(XR - 7, y + 3.5, rpins[i], size=9, anchor="end", color=INK if used_r else GREY, weight="bold" if used_r else "normal")

# XIAO power
vhops(655, 110, 595, [166, 194, 422], RED)       # 5V stub up to rail, VCC tap down to AHCT125
s.wire([(620, 370), (655, 370)], RED)
s.dot(655, 110, RED); s.dot(655, 370, RED)
s.wire([(655, 595), (380, 595), (380, 610)], RED)
s.wire([(620, 396), (634, 396)], BLACK)
s.gnd(634, 396)
s.wire([(620, 422), (672, 422), (672, 222), (720, 222)], MAG)

# XIAO signals
s.arrow([(720, 166), (470, 166), (470, 422), (520, 422)], GREEN, sw=2)   # D2 <- switch
s.arrow([(720, 194), (490, 194), (490, 396), (520, 396)], GREEN, sw=2)   # D1 <- Hall
s.arrow([(520, 448), (240, 448)], GREEN, sw=2)                           # D3 -> pump
s.arrow([(520, 474), (275, 474), (275, 660), (330, 660)], GREEN, sw=2)   # D4 -> 1A
s.arrow([(520, 500), (258, 500), (258, 730), (330, 730)], GREEN, sw=2)   # D5 -> 2A
s.text(498, 161, "SW (active LOW, INPUT_PULLUP)", size=9, color=GREEN)
s.text(498, 189, "HALL (LOW = ring present)", size=9, color=GREEN)
s.text(330, 443, "PUMP (HIGH = on, PWM soft start)", size=9, color=GREEN)

# ------------------------------------------------------------------ D4184 module
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
s.wire([(120, 480), (120, 540)], ORANGE)
s.wire([(200, 480), (200, 540)], ORANGE)
# pump
s.rect(90, 540, 140, 70, rx=10, sw=1.4)
s.text(112, 553, "+", size=11, anchor="middle", weight="bold")
s.text(208, 553, "−", size=11, anchor="middle", weight="bold")
s.text(160, 572, "Kamoer KPHM200", size=11, anchor="middle", weight="bold")
s.text(160, 586, "peristaltic pump, 12 V DC", size=9, anchor="middle")
s.text(160, 599, "200 mL/min, ~0.7 A (swap leads = reverse)", size=8, anchor="middle", color="#555")

# ------------------------------------------------------------------ AHCT125 schematic box
AX, AY = 330, 610
s.rect(AX, AY, 100, 150, rx=4, sw=1.4)
s.text(380, 678, "AHCT125", size=9, anchor="middle", weight="bold")
s.text(380, 689, "3.3 → 5 V buffer", size=8, anchor="middle")
s.pin(AX, 632); s.text(AX + 5, 635, "1  1OE", size=8.5)
s.pin(AX, 660); s.text(AX + 5, 663, "2  1A", size=8.5)
s.pin(AX, 700); s.text(AX + 5, 703, "4  2OE", size=8.5)
s.pin(AX, 730); s.text(AX + 5, 733, "5  2A", size=8.5)
s.pin(AX + 100, 660); s.text(AX + 95, 663, "1Y  3", size=8.5, anchor="end")
s.pin(AX + 100, 730); s.text(AX + 95, 733, "2Y  6", size=8.5, anchor="end")
s.pin(380, AY); s.text(380, 623, "14 VCC", size=8.5, anchor="middle")
s.pin(380, AY + 150); s.text(380, 753, "7 GND", size=8.5, anchor="middle")
s.wire([(AX, 632), (306, 632)], BLACK); s.gnd(306, 632)
s.wire([(AX, 700), (306, 700)], BLACK); s.gnd(306, 700)
s.wire([(380, 760), (380, 768)], BLACK); s.gnd(380, 768)
s.text(440, 606, "SN74AHCT125N, DIP-14 (pinout at left)", size=9, color="#555")
# outputs
s.res_h(430, 530, 660, "330 Ω", GREEN)
s.arrow([(530, 660), (684, 660), (684, 250), (720, 250)], GREEN, sw=2)
s.text(545, 655, "RING DIN", size=9, color=GREEN)
s.res_h(430, 530, 730, "330 Ω", GREEN)
s.arrow([(530, 730), (720, 730)], GREEN, sw=2)
s.text(545, 725, "STRIP DIN", size=9, color=GREEN)

# ------------------------------------------------------------------ DIP-14 pinout inset
s.rect(30, 625, 215, 250, fill="#fafafa", stroke=GREY, sw=1, dash="4,3", rx=4)
s.text(137, 640, "SN74AHCT125N — DIP-14, top view, notch up", size=9, anchor="middle", weight="bold")
s.rect(105, 652, 60, 210, rx=2, sw=1.4, fill="#eeeeee")
s.path("M129,652 A6,6 0 0 0 141,652", stroke=INK, sw=1.4)
s.dot(112, 662, INK, r=2.5)
left = ["1  1OE→GND", "2  1A←D4", "3  1Y→ring", "4  2OE→GND", "5  2A←D5", "6  2Y→strip", "7  GND"]
right = ["14 VCC +5 V", "13 4OE→GND", "12 4A→GND", "11 4Y n/c", "10 3OE→GND", "9  3A→GND", "8  3Y n/c"]
for i in range(7):
    y = 668 + i * 30
    s.path(f"M95,{y} L105,{y} M165,{y} L175,{y}", stroke=INK, sw=2)
    s.text(92, y + 3, left[i], size=8.5, anchor="end")
    s.text(178, y + 3, right[i], size=8.5)
s.text(135, 760, "74", size=9, anchor="middle", color="#666")
s.text(135, 771, "AHCT", size=9, anchor="middle", color="#666")
s.text(135, 782, "125", size=9, anchor="middle", color="#666")

# ------------------------------------------------------------------ alternative insets
# alt Hall
s.rect(255, 790, 220, 105, fill="#fffdf5", stroke=GREY, sw=1, dash="4,3", rx=4)
s.text(263, 804, "alternative: 5 V A3144 Hall module", size=10, weight="bold")
s.text(263, 816, "(module OUT idles at 5 V — check D1 HIGH ≤ 3.3 V)", size=8.5, color="#555")
s.rect(263, 822, 56, 60, rx=3, sw=1.2)
s.text(291, 840, "A3144", size=9, anchor="middle", weight="bold")
s.text(291, 851, "module", size=9, anchor="middle")
s.text(291, 862, "(5 V)", size=9, anchor="middle")
s.pin(319, 830); s.wire([(319, 830), (345, 830)], RED); s.text(349, 833, "5 V", size=9, color=RED)
s.pin(319, 850)
s.res_h(319, 400, 850, "4.7 kΩ", GREEN, size=9)
s.dot(410, 850, GREEN)
s.arrow([(400, 850), (455, 850)], GREEN, sw=2)
s.text(458, 853, "D1", size=9, color=GREEN, weight="bold")
s.wire([(410, 850), (410, 858)], GREEN)
s.rect(404, 858, 12, 20, sw=1.3)
s.wire([(410, 878), (410, 884)], BLACK); s.gnd(410, 884)
s.text(420, 872, "22 kΩ", size=9)
s.pin(319, 870); s.wire([(319, 870), (345, 870)], BLACK); s.gnd(345, 870)
s.text(326, 828, "VCC", size=7.5, anchor="start", color="#555")
s.text(326, 847, "OUT", size=7.5, anchor="start", color="#555")
# alt pump
s.rect(485, 790, 207, 105, fill="#fffdf5", stroke=GREY, sw=1, dash="4,3", rx=4)
s.text(493, 804, "alternative: Adafruit 3910 5 V pump", size=10, weight="bold")
s.text(493, 816, "no 12 V rail, no PD cable, ~2× slower pour", size=8.5, color="#555")
s.rect(520, 826, 66, 56, rx=3, sw=1.2)
s.text(553, 848, "same", size=8, anchor="middle", weight="bold")
s.text(553, 858, "D4184", size=8, anchor="middle", weight="bold")
s.pin(520, 838); s.text(524, 841, "DC+", size=7.5)
s.pin(520, 866); s.text(524, 869, "DC−", size=7.5)
s.pin(586, 838); s.text(582, 841, "OUT+", size=7.5, anchor="end")
s.pin(586, 866); s.text(582, 869, "OUT−", size=7.5, anchor="end")
s.wire([(493, 838), (520, 838)], RED); s.text(493, 833, "+5 V rail", size=7.5, color=RED)
s.wire([(520, 866), (505, 866)], BLACK); s.gnd(505, 866)
s.wire([(586, 838), (612, 838)], RED)
s.wire([(586, 866), (612, 866)], RED)
s.rect(612, 828, 74, 50, rx=8, sw=1.2)
s.text(649, 846, "Adafruit 3910", size=8, anchor="middle", weight="bold")
s.text(649, 857, "5 V peristaltic", size=8, anchor="middle")
s.text(649, 868, "~100 mL/min", size=8, anchor="middle", color="#555")

# ------------------------------------------------------------------ J1 socket connector (6 wires)
s.rect(720, 96, 30, 168, rx=5, fill="#e6e6e6", sw=1.2)
j1 = [("5 V", 110, RED), ("GND", 138, BLACK), ("SW", 166, GREEN), ("HALL", 194, GREEN), ("3V3", 222, MAG), ("RING DIN", 250, GREEN)]
for lab, y, col in j1:
    s.pin(735, y, col, r=3.5)
    s.text(755, y - 4, lab, size=8.5, color=col, weight="bold")
s.text(735, 277, "J1  6-pin", size=8.5, anchor="middle", weight="bold")
s.text(735, 288, "(JST-XH)", size=8, anchor="middle", color="#555")
# 5 V trunk down the gutter to J2 (hops over the J1 signals)
s.dot(706, 110, RED)
vhops(706, 110, 674, [166, 194, 222, 250], RED)
s.wire([(706, 674), (720, 674)], RED)
# J1 GND on the socket side
s.wire([(750, 138), (768, 138)], BLACK); s.gnd(768, 138)

# ---- microswitch
s.rect(820, 122, 140, 56, rx=4, sw=1.4)
s.text(905, 142, "D2F-L", size=10, anchor="middle", weight="bold")
s.text(905, 154, "lever microswitch", size=9, anchor="middle")
s.text(905, 166, "cam presses it at ~40°", size=8, anchor="middle", color="#555")
s.pin(820, 140); s.text(826, 143, "NO", size=8.5)
s.pin(820, 158); s.text(826, 161, "COM", size=8.5)
s.pin(820, 174, GREY); s.text(826, 177, "NC n/c", size=8, color=GREY)
s.wire([(750, 166), (780, 166), (780, 140), (820, 140)], GREEN)
s.wire([(820, 158), (800, 158)], BLACK); s.gnd(800, 158)

# ---- DRV5032 Hall breakout
s.rect(820, 184, 140, 72, rx=4, sw=1.4)
s.text(905, 205, "Adafruit DRV5032", size=10, anchor="middle", weight="bold")
s.text(905, 218, "Hall breakout #6051", size=9, anchor="middle")
s.text(905, 231, "omnipolar · 3.3 V OUT", size=8, anchor="middle", color="#555")
s.text(905, 244, "LOW when the magnet is near", size=8, anchor="middle", color="#555")
s.pin(820, 194); s.text(826, 197, "OUT", size=8.5)
s.pin(820, 222, MAG); s.text(826, 225, "VIN", size=8.5, color=MAG)
s.pin(890, 256); s.text(900, 274, "GND", size=8)
s.wire([(750, 194), (820, 194)], GREEN)
s.wire([(750, 222), (820, 222)], MAG)
s.wire([(890, 256), (890, 264)], BLACK); s.gnd(890, 264)
# magnet hint
s.rect(975, 190, 26, 10, fill="#9e9e9e", sw=1)
s.text(988, 198, "N S", size=7, anchor="middle", color="#fff", weight="bold")
s.text(975, 214, "6×2 mm magnet", size=8, color="#555")
s.text(975, 225, "in the ring key,", size=8, color="#555")
s.text(975, 236, "on the rotor axis", size=8, color="#555")

# ---- NeoPixel ring
CX, CY = 880, 390
s.circle(CX, CY, 60, fill="#e8f5e9", sw=1.4)
s.circle(CX, CY, 46, fill="#ffffff", sw=1.2)
import math
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
s.lines(733, 482, [
    "Hall: Adafruit DRV5032 breakout (#6051) runs from the XIAO 3V3 and",
    "its OUT is 3.3 V logic → straight to D1 with INPUT_PULLUP, no divider.",
    "Omnipolar: magnet pole orientation does not matter. The magnet sits",
    "on the rotor axis, so twisting the ring never moves it off the sensor.",
], size=8.5, color="#333", lh=11)

# ------------------------------------------------------------------ J2 sphere connector + strip
s.rect(720, 660, 30, 84, rx=5, fill="#e6e6e6", sw=1.2)
for lab, y, col in (("5 V", 674, RED), ("GND", 702, BLACK), ("DIN", 730, GREEN)):
    s.pin(735, y, col, r=3.5)
    s.text(755, y - 4, lab, size=8.5, color=col, weight="bold")
s.text(735, 757, "J2  3-pin", size=8.5, anchor="middle", weight="bold")
s.wire([(750, 674), (790, 674)], RED)
s.wire([(750, 702), (790, 702)], BLACK); s.gnd(770, 704)
s.arrow([(750, 730), (788, 730)], GREEN, sw=2)
s.rect(790, 654, 250, 92, rx=4, sw=1.4, fill="#f7f7f7")
s.pin(790, 674, RED); s.text(796, 677, "5V", size=8.5, weight="bold")
s.pin(790, 702, BLACK); s.text(796, 705, "GND", size=8.5, weight="bold")
s.pin(790, 730, GREEN); s.text(796, 733, "DIN", size=8.5, weight="bold")
s.text(930, 670, "WS2812B strip, 5 V, 60 px", size=10, anchor="middle", weight="bold")
for i in range(9):
    s.rect(836 + i * 22, 686, 14, 14, fill="#4caf50", stroke="none", rx=2)
    s.path(f"M{843 + i * 22},707 L{843 + i * 22},712", stroke="#4caf50", sw=1)
s.arrow([(836, 718), (1020, 718)], GREY, sw=1)
s.text(930, 739, "data flows this way — DIN is the end nearest the connector", size=8, anchor="middle", color="#555")
s.lines(733, 782, [
    "Set STRIP_COUNT in the sketch to the real pixel count. Keep the two data",
    "wires short and twisted with GND; the 330 Ω resistors sit at the AHCT125 end.",
    "Power: 24 + 60 px at maxBright 160 can draw ~2 A on the 5 V rail → F1 3 A,",
    "C1 1000 µF next to the LEDs, and a power bank rated ≥ 2.4 A on the 5 V port.",
], size=8.5, color="#333", lh=11)
s.lines(733, 842, [
    "COMMON GROUND: every ground symbol is the same net. Tie together:",
    "power bank −, XIAO GND, D4184 DC− and GND, AHCT125 pin 7 (+ OE pins),",
    "DRV5032 GND, switch COM, ring GND, strip GND. Unused AHCT125 inputs",
    "(3A, 4A, 3OE, 4OE) are tied to GND too.",
], size=8.5, color="#333", lh=11, weight="normal")

open("/home/user/temprepo/docs/images/wiring.svg", "w").write(s.finish())
print("written")
