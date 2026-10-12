import sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

W, H = 1300, 610
s = SVG(W, H, "Green Lantern power battery - firmware state machine")
s.text(20, 32, "Firmware state machine — green_lantern.ino (hold-to-pour)", size=20, weight="bold")
s.text(20, 52, "loop() at ~100 Hz: readInputs() → pumpService() → global ring interlock → state switch → lightService()", size=11, color="#555")

BW, BH, BY = 136, 182, 150
xs = [30, 202, 374, 546, 718, 890]
fills = ["#eeeeee", "#e3f2e3", "#c8e6c9", "#b9dfba", "#f1fff1", "#e6e6e6"]
names = ["IDLE", "ARMED", "POURING", "HOLDING", "FINALE", "LOCKED"]
leds = [
    ["light: dark", "(or the idle glow", "if you set one)"],
    ["light: fades up", "to ~15 %"],
    ["light: climbs", "steadily from 15 %", "to 90 % over the", "pour (pourMs)"],
    ["light: steady 90 %"],
    ["light: swells to", "100 % (0.4 s), holds", "0.3 s, fades out", "over 1.2 s"],
    ["light: dark"],
]
pumps = [
    ["pump: OFF"],
    ["pump: OFF"],
    ["pump: ON at the", "speed setting, soft", "start, runs pourMs,", "20 s hard cap"],
    ["pump: OFF (pour", "complete), waiting", "for the release"],
    ["pump: OFF"],
    ["pump: OFF until the", "ring is removed"],
]
for i, x in enumerate(xs):
    s.rect(x, BY, BW, BH, rx=8, fill=fills[i], stroke=INK, sw=1.6)
    s.text(x + BW / 2, BY + 24, names[i], size=15, anchor="middle", weight="bold")
    s.path(f"M{x + 10},{BY + 33} L{x + BW - 10},{BY + 33}", stroke="#999", sw=1)
    s.lines(x + 10, BY + 50, leds[i], size=10, lh=12.5)
    s.path(f"M{x + 10},{BY + 118} L{x + BW - 10},{BY + 118}", stroke="#999", sw=1, dash="2,2")
    s.lines(x + 10, BY + 133, pumps[i], size=10, lh=12, color=ORANGE if i == 2 else "#444", weight="bold" if i == 2 else "normal")

# forward transitions (between boxes, arrows at y = BY+45) + labels above
AY = BY + 45
trans = [
    ["ring in", "≥ 100 ms"],
    ["twist held ≥ 40 ms,", "ring in, no pour", "yet → pump on"],
    ["pourMs done", "(or 20 s cap)"],
    ["ring turned back", "(switch released)"],
    ["swell + fade", "done (1.9 s)"],
]
for i in range(5):
    x1 = xs[i] + BW
    x2 = xs[i + 1]
    s.arrow([(x1, AY), (x2 - 1, AY)], INK, sw=2)
    gx = (x1 + x2) / 2
    s.lines(gx, 84, trans[i], size=10, anchor="middle", lh=12)
    s.path(f"M{gx},{84 + 12 * len(trans[i]) - 8} L{gx},{AY - 6}", stroke="#999", sw=1, dash="2,2")

# early release: POURING -> FINALE along the bottom
EY = BY + BH + 24
s.wire([(xs[2] + 112, BY + BH), (xs[2] + 112, EY), (xs[4] + 30, EY), (xs[4] + 30, BY + BH + 1)], "#1d4ed8", sw=2, marker="arrB")
s.lines((xs[2] + xs[4]) / 2 + 70, EY + 15, ["let go early: the pump stops where it is,", "the light swells ~10 % and fades out"], size=10, anchor="middle", lh=12, color="#1d4ed8")

# LOCKED -> IDLE (normal exit) along the bottom
LY = BY + BH + 62
s.wire([(xs[5] + 68, BY + BH), (xs[5] + 68, LY), (xs[0] + 95, LY), (xs[0] + 95, BY + BH + 1)], INK, sw=2, marker="arrK")
s.lines(xs[5] + 60, LY + 14, ["ring removed ≥ 200 ms: only a", "removed ring re-arms the prop"], size=10, anchor="end", lh=12)

# abort: ring pulled during POURING / HOLDING / FINALE -> pump off -> LOCKED; ARMED -> IDLE
RY = BY + BH + 100
for i in (2, 3, 4):
    s.wire([(xs[i] + 20, BY + BH), (xs[i] + 20, RY)], RED, sw=1.8, dash="6,4")
s.wire([(xs[2] + 20, RY), (xs[5] + 30, RY), (xs[5] + 30, BY + BH + 1)], RED, sw=1.8, dash="6,4", marker="arrR")
s.rect(330, RY + 8, 470, 22, rx=11, fill="#fdecea", stroke=RED, sw=1)
s.text(565, RY + 23, "ring pulled out: pump off within 60 ms → LOCKED (from ARMED: back to IDLE)", size=11, anchor="middle", weight="bold", color=RED)

# boot entry
s.arrow([(xs[0] + 68, 110), (xs[0] + 68, BY - 1)], INK, sw=2)
s.text(xs[0] + 74, 125, "boot", size=10)

# ------------------------------------------------------------------ interlocks panel
PX, PY, PW, PH = 1060, 72, 220, 390
s.rect(PX, PY, PW, PH, rx=8, fill="#fffbe6", stroke="#c9a227", sw=1.4)
s.text(PX + PW / 2, PY + 22, "Safety interlocks", size=13, anchor="middle", weight="bold")
s.path(f"M{PX + 12},{PY + 30} L{PX + PW - 12},{PY + 30}", stroke="#c9a227", sw=1)
items = [
    ["Pump pin driven LOW first", "thing in setup(), before", "anything else."],
    ["Switch alone never pumps;", "Hall alone never pumps."],
    ["Dead-man: the pump runs", "only while the twist is held."],
    ["Exactly one pour per ring", "insertion (pouredThis-", "Insertion flag)."],
    ["Ring removed at any time", "→ pump off at once (checked", "every loop, outside states)."],
    ["Absolute cap MAX_PUMP_MS", "= 20 s inside pumpService(),", "independent of the states."],
    ["Switch already pressed at", "boot (jammed cam) is ignored", "until it is released."],
    ["Debounce: Hall 100 ms in /", "200 ms out; switch 40 ms."],
    ["Hardware: 10 k pull-downs", "hold both MOSFETs off", "while the XIAO boots."],
]
y = PY + 48
for it in items:
    s.circle(PX + 16, y - 4, 3, fill="#c9a227", stroke="none")
    s.lines(PX + 26, y, it, size=9.5, lh=11.5)
    y += 11.5 * len(it) + 7

# ------------------------------------------------------------------ timing + bench strip
s.rect(30, 470, 1010, 120, rx=8, fill="#f5f5f5", stroke="#bbb", sw=1)
s.text(44, 491, "Timing constants", size=12, weight="bold")
s.lines(44, 509, [
    "HALL_DEBOUNCE_MS 100   ·   RING_GONE_MS 200   ·   POUR_ABORT_MS 60   ·   SWITCH_DEBOUNCE_MS 40   ·   PUMP_RAMP_MS 300   ·   MAX_PUMP_MS 20 000",
    "DEFAULT_POUR_MS 11 000 (the length of the build-up)   ·   DEFAULT_PUMP_SPEED 70 % (sets the volume: calibrate)",
    "Light: ARMED_LEVEL 15 %   ·   POUR_PEAK 90 %   ·   EARLY_BUMP +10 %   ·   finale 0.4 s up, 0.3 s hold, 1.2 s fade   ·   idle glow 0",
], size=10, lh=14)
s.text(44, 565, "Bench (USB serial, 115200):", size=11, weight="bold")
s.text(210, 565, "status  ·  cal 10000  ·  pour 11000  ·  speed 70  ·  leds 255  ·  idle 0  ·  save  ·  stop", size=10, family="Menlo, Consolas, monospace")
s.text(44, 582, "Legend:", size=10, weight="bold")
s.wire([(100, 578), (130, 578)], INK, sw=2, marker="arrK"); s.text(136, 582, "transition", size=10)
s.wire([(210, 578), (240, 578)], "#1d4ed8", sw=2, marker="arrB"); s.text(246, 582, "early release", size=10)
s.wire([(330, 578), (360, 578)], RED, sw=1.8, dash="6,4", marker="arrR"); s.text(366, 582, "ring pulled out", size=10)

open(os.path.join(HERE, "..", "state-machine.svg"), "w").write(s.finish())
print("written")
