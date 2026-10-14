"""Generate the reviewed electrical schematic; CAD battery fit is a separate revision.
Run: python3 docs/images/src/gen_wiring.py
Named nets connect across panels. SVG output is committed beside wiring.png.
"""
from pathlib import Path
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

MAG = "#8b36ad"
s = SVG(1600, 1430, "Green Lantern — reviewed circuit")


def panel(x, y, w, h, title):
    s.rect(x, y, w, h, stroke="#cbd5e1", rx=8)
    s.text(x + 18, y + 28, title, size=18, weight="bold")


def box(x, y, w, h, title, rows=()):
    s.rect(x, y, w, h, fill="#f1f5f9", rx=5)
    s.text(x + w/2, y + 24, title, size=16, anchor="middle", weight="bold")
    s.lines(x + w/2, y + 46, rows, size=12, anchor="middle")


def net(x, y, name, color=GREEN, anchor="start"):
    s.dot(x, y, color, r=3)
    s.text(x, y - 9, name, size=12, color=color, anchor=anchor, weight="bold")


def ground(x, y):
    s.gnd(x, y)


def cap(x, top, bottom, label, color=RED, positive=False):
    mid = (top + bottom)/2
    s.wire([(x, top), (x, mid - 4)], color)
    s.path(f"M{x-11},{mid-4} H{x+11} M{x-11},{mid+4} H{x+11}", sw=2)
    s.wire([(x, mid + 4), (x, bottom)], BLACK)
    s.text(x + 17, mid + 4, label, size=12)
    if positive:
        s.text(x - 23, mid - 8, "+", size=15)
    ground(x, bottom)


def diode(x1, x2, y, label, color=GREEN):
    # Anode at x1; vertical cathode bar at the right, toward x2.
    mid = (x1 + x2)/2
    s.wire([(x1, y), (mid - 9, y)], color)
    s.path(f"M{mid-9},{y-9} L{mid-9},{y+9} L{mid+7},{y} Z M{mid+8},{y-10} V{y+10}", sw=1.7, fill="#e2e8f0")
    s.wire([(mid + 8, y), (x2, y)], color)
    s.text(mid, y - 18, label, size=12, anchor="middle")


s.text(24, 38, "Green Lantern power battery — circuit revision", size=25, weight="bold")
s.text(24, 66, "Matching net names are connected. All grounds are common. Dots join wires; unmarked crossings do not.", size=14)

# POWER: battery output also accepts charging, before S1.
panel(20, 90, 1560, 310, "Power and charging")
box(45, 145, 210, 92, "TalentCell YB1203000", ["3000 mAh • 3 A max", "9–12.6 V • DC5521 centre +"])
s.wire([(255, 185), (390, 185)], ORANGE, sw=3)
s.dot(330, 185, ORANGE)
s.pin(390, 185); s.pin(430, 185)
s.wire([(390, 183), (425, 165)], BLACK)
s.text(410, 150, "S1 master switch", size=13, anchor="middle")
s.wire([(430, 185), (650, 185)], ORANGE, sw=3)
net(545, 185, "VLOAD", ORANGE)
s.wire([(255, 220), (280, 220), (280, 246)], BLACK); ground(280, 246)
box(45, 285, 210, 70, "J1 charge jack", ["DC5521 • centre +"])
s.wire([(330, 185), (330, 305), (255, 305)], ORANGE)
s.wire([(255, 338), (280, 338), (280, 360)], BLACK); ground(280, 360)
s.text(340, 337, "Pack switch ON for use/charge; S1 OFF to charge.", size=13)
s.text(340, 362, "Use supplied 12.6 V charger; J1 switched contact unused.", size=13)
s.wire([(550, 185), (550, 222)], ORANGE); s.dot(550, 185, ORANGE)
cap(550, 222, 298, "C2 2200 µF / 25 V", ORANGE, positive=True)
box(650, 145, 210, 92, "LM2596 buck", ["IN+ = VLOAD; IN− = GND", "Set OUT to 5.0 V unloaded"])
s.wire([(755, 237), (755, 263)], BLACK); ground(755, 263)
s.wire([(860, 185), (995, 185)], RED, sw=3)
net(890, 185, "+5V_REG", RED)
s.text(885, 240, "To U1 and Hall sensor", size=13, color=RED)
s.text(885, 259, "BEFORE D1", size=13, color=RED, weight="bold")
diode(995, 1125, 185, "D1 NTE585", RED)
s.wire([(1125, 185), (1195, 185)], RED)
s.pin(1195, 185); s.pin(1225, 185)
s.rect(1189, 179, 42, 12, fill="none", stroke=RED, sw=2)
s.text(1210, 150, "JP1 removable shunt", size=13, anchor="middle")
s.wire([(1225, 185), (1485, 185)], RED)
net(1485, 185, "XIAO_5V", RED, "end")
s.text(1060, 218, "D1 stripe toward XIAO", size=12)
s.lines(1040, 283, ["JP1 fitted: battery operation, USB unplugged.",
    "JP1 removed: USB powers XIAO; S1 powers U1/loads.",
    "Never connect USB with JP1 fitted.",
    "USB-only flashing: remove U1 from its socket first."], size=13, lh=24)

# MCU: labelled nets keep low-voltage connections readable.
panel(20, 420, 400, 450, "Controller — 3.3 V GPIO")
box(45, 475, 230, 315, "Seeed XIAO RP2040")
for y, pin, label, color in [
    (535, "5V", "XIAO_5V", RED), (570, "3V3", "+3V3", MAG),
    (610, "D0", "BAT_SENSE", GREEN), (645, "D1", "HALL", GREEN),
    (680, "D2", "TWIST", GREEN), (715, "D3", "PUMP_PWM", GREEN),
    (750, "D4", "LED_PWM", GREEN)]:
    s.text(265, y + 4, pin, size=13, anchor="end")
    s.wire([(275, y), (310, y)], color)
    net(310, y, label, color)
s.wire([(150, 790), (150, 815)], BLACK); ground(150, 815)
s.text(175, 810, "GND", size=12)
s.text(40, 850, "Optional PRIME: D6 → momentary button → GND", size=12)

# DUAL GATE DRIVER, DIP8 pin numbering from Microchip DS20001422G.
panel(440, 420, 660, 450, "U1 — TC4427CPA dual non-inverting gate driver")
box(685, 555, 195, 205, "TC4427CPA", ["DIP-8", "1, 8: no connection"])
net(780, 480, "+5V_REG", RED)
s.wire([(780, 480), (780, 555)], RED)
s.text(790, 546, "6 VDD", size=12)
s.wire([(780, 760), (780, 800)], BLACK); ground(780, 800)
s.text(790, 782, "3 GND", size=12)
for x, label in [(930, "C3 0.1 µF"), (1025, "C4 1 µF")]:
    s.wire([(780, 500), (x, 500)], RED)
    s.dot(x, 500, RED)
    cap(x, 500, 570, label)
s.dot(780, 500, RED)
for y, label, ip, op, out, rx, rlabel in [
    (660, "PUMP_PWM", "2 IN A", "7 OUT A", "PUMP_DRV", 565, "R3 10 kΩ"),
    (725, "LED_PWM", "4 IN B", "5 OUT B", "LED_DRV", 650, "R4 10 kΩ")]:
    net(465, y, label)
    s.wire([(465, y), (685, y)], GREEN)
    s.text(695, y + 4, ip, size=12)
    s.text(870, y + 4, op, size=12, anchor="end")
    s.wire([(880, y), (985, y)], GREEN); net(985, y, out)
    s.dot(rx, y, GREEN)
    bottom = 705 if ip == "2 IN A" else 815
    s.res_v(rx, y, bottom, rlabel, lab_dx=-85, size=11)
    ground(rx, bottom)
s.text(465, 850, "C3 + C4: short leads directly across pins 6 and 3.", size=13)

# LOADS, each low-side MOSFET has series gate resistor and gate-source pull-down.
panel(1120, 420, 460, 705, "Pump and lighting")

def load_stage(y, title, q, drive, rg, rpd, flyback=False):
    net(1330, y, "VLOAD", ORANGE)
    s.wire([(1330, y), (1330, y + 30)], ORANGE)
    box(1260, y + 30, 220, 65, title, ["+ above • − below"])
    s.wire([(1330, y + 95), (1330, y + 130)], BLACK)
    box(1260, y + 130, 220, 72, q + " IRLZ44NPBF", ["1 G     2 D/tab     3 S"])
    s.text(1340, y + 124, "D", size=12)
    net(1145, y + 180, drive)
    s.res_h(1145, 1260, y + 180, rg + " 47 Ω", lab_dy=24, size=12)
    s.dot(1245, y + 180, GREEN)
    s.res_v(1245, y + 180, y + 264, rpd + " 10 kΩ", lab_dx=-98, size=11)
    s.wire([(1245, y + 264), (1330, y + 264), (1330, y + 202)], BLACK)
    ground(1330, y + 264)
    s.text(1340, y + 225, "S → GND", size=12)
    if flyback:
        # Cathode bar is at the upper (positive) terminal.
        s.wire([(1330, y + 12), (1530, y + 12), (1530, y + 45)], ORANGE)
        s.dot(1330, y + 12, ORANGE)
        s.path(f"M1521,{y+62} H1539 L1530,{y+46} Z M1520,{y+45} H1540", fill="#e2e8f0", sw=1.7)
        s.wire([(1530, y + 62), (1530, y + 112), (1330, y + 112)], BLACK)
        s.dot(1330, y + 112)
        s.lines(1510, y + 143, ["D2", "NTE586", "3 A / 40 V", "stripe ↑"], size=10, anchor="middle")

load_stage(480, "Kamoer KPHM200 12 V", "Q1", "PUMP_DRV", "R5", "R7", True)
load_stage(810, "12 V green COB • ~75 cm", "Q2", "LED_DRV", "R6", "R8")

# SENSOR CIRCUITS: local bypass, open collector and contact wetting circuit.
panel(20, 890, 620, 365, "Hall sensor — bare A3144")
box(45, 995, 220, 125, "A3144", ["Printed face toward viewer", "leads downward: 1, 2, 3", "1 VCC • 2 GND • 3 OUT"])
net(330, 955, "+5V_REG", RED)
s.wire([(330, 955), (330, 1020), (265, 1020)], RED)
s.text(270, 1012, "1", size=12)
s.wire([(330, 970), (490, 970)], RED); s.dot(330, 970, RED)
cap(490, 970, 1040, "C5 0.1 µF")
s.wire([(265, 1095), (300, 1095), (300, 1130)], BLACK); ground(300, 1130)
s.text(273, 1088, "2", size=12)
s.wire([(265, 1060), (390, 1060), (390, 1150), (565, 1150)], GREEN)
s.text(273, 1052, "3", size=12)
net(565, 1150, "HALL → D1", GREEN, "end")
net(450, 1060, "+3V3", MAG)
s.res_v(450, 1060, 1150, "R9 4.7 kΩ", lab_dx=12)
s.dot(450, 1150, GREEN)
s.lines(40, 1200, ["C5 goes at the sensor, after the cable; OUT connects directly to D1.",
    "No 5 V pull-up and no series diode on HALL."], size=13, lh=22)

panel(660, 890, 440, 365, "Twist — D2F-01L lever switch")
net(925, 955, "+5V_REG", RED)
s.res_v(925, 955, 1080, "R11 3.3 kΩ", lab_dx=12)
s.dot(925, 1080, GREEN)
net(700, 1080, "TWIST → D2")
net(740, 955, "+3V3", MAG)
s.res_v(740, 955, 1080, "R10 4.7 kΩ", lab_dx=12)
s.dot(740, 1080, GREEN)
diode(700, 925, 1080, "D3 NTE585")
s.wire([(925, 1080), (925, 1100)], GREEN)
s.pin(925, 1100); s.pin(925, 1150)
s.wire([(925, 1150), (902, 1110)], BLACK)
s.wire([(925, 1150), (925, 1175)], BLACK); ground(925, 1175)
s.text(945, 1105, "NO", size=12); s.text(945, 1154, "COM", size=12)
s.lines(680, 1200, ["D3 stripe toward NO; NC unused.", "R11 supplies ~1.5 mA when closed; GPIO stays at 3.3 V."], size=12, lh=22)

panel(1120, 1145, 460, 265, "Battery sense")
net(1170, 1198, "VLOAD", ORANGE)
s.res_v(1170, 1198, 1280, "R1 100 kΩ", ORANGE)
s.dot(1170, 1280, GREEN)
s.res_v(1170, 1280, 1370, "R2 22 kΩ")
ground(1170, 1370)
s.wire([(1170, 1280), (1380, 1280)], GREEN)
net(1380, 1280, "BAT_SENSE → D0", GREEN, "end")
s.dot(1360, 1280, GREEN)
cap(1360, 1280, 1370, "C1 0.1 µF", GREEN)
s.text(1150, 1395, "12.6 V × 22 / 122 = 2.27 V at D0", size=13)

s.lines(30, 1295, [
    "LOCK CABLE (JST PH 4-pin): +5V_REG, HALL, SW_NO (D3 cathode), GND. R9–R11 and D3 stay on the board.",
    "LED CABLE (JST SM 2-pin): VLOAD and Q2 drain. Keep pump/LED return currents out of sensor/MCU wiring.",
    "USB service: see build guide power sequence. JP1 only isolates the XIAO supply, not its GPIO connections.",
    "CAD FOLLOW-UP: existing battery supports fit the old KBT pack; TalentCell fit is a separate PR.",
], size=13, lh=28)

out = Path(__file__).resolve().parent.parent / "wiring.svg"
out.write_text(s.finish())
print(out)
