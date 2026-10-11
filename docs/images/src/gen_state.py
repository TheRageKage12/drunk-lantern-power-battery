import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-temprepo/45c7fed5-b38c-5bcd-8935-8412da500de5/scratchpad")
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

W, H = 1100, 600
s = SVG(W, H, "Green Lantern power battery - firmware state machine")
s.text(20, 32, "Firmware state machine — green_lantern.ino", size=20, weight="bold")
s.text(20, 52, "loop() at ~100 Hz: readInputs() → pumpService() → global ring interlock → state switch → show()", size=11, color="#555")

BW, BH, BY = 136, 182, 150
xs = [30, 205, 380, 555, 730]
fills = ["#eeeeee", "#e3f2e3", "#f1fff1", "#c8e6c9", "#dcedc8"]
names = ["IDLE", "ARMED", "FLASH", "POURING", "LOCKED"]
leds = [
    ["LEDs: faint green", "ember, 6–13/255,", "4 s breathe (never", "looks dead)"],
    ["LEDs: slow charging", "pulse, 1.6 s period;", "ceiling 90→170 over", "20 s; one bright", "pixel orbits the ring"],
    ["LEDs: ring + strip", "full white-green", "flash for 220 ms"],
    ["strip: bright green", "swirl (120–255);", "ring: breathing +", "6-px comet head"],
    ["LEDs: afterglow", "200→60 over 4 s,", "then steady 60"],
]
pumps = [
    ["pump: OFF"],
    ["pump: OFF"],
    ["pump: OFF", "(starts on exit)"],
    ["pump: ON — PWM", "ramp 40→255 in", "300 ms, runs pourMs,", "hard cap 20 s"],
    ["pump: OFF; stays", "locked until the", "ring is removed"],
]
for i, x in enumerate(xs):
    s.rect(x, BY, BW, BH, rx=8, fill=fills[i], stroke=INK, sw=1.6)
    s.text(x + BW / 2, BY + 24, names[i], size=15, anchor="middle", weight="bold")
    s.path(f"M{x + 10},{BY + 33} L{x + BW - 10},{BY + 33}", stroke="#999", sw=1)
    s.lines(x + 10, BY + 50, leds[i], size=10, lh=12.5)
    s.path(f"M{x + 10},{BY + 118} L{x + BW - 10},{BY + 118}", stroke="#999", sw=1, dash="2,2")
    s.lines(x + 10, BY + 133, pumps[i], size=10, lh=12, color=ORANGE if i == 3 else "#444", weight="bold" if i == 3 else "normal")

# forward transitions (between boxes, arrows at y = BY+45) + labels above
AY = BY + 45
trans = [
    ["ring present", "≥ 100 ms", "(Hall LOW)"],
    ["ring AND switch", "(cam at ~40°) AND", "not poured yet"],
    ["after 220 ms:", "pumpStart(pourMs)"],
    ["pour done", "(pourMs elapsed", "or 20 s cap hit)"],
]
for i in range(4):
    x1 = xs[i] + BW
    x2 = xs[i + 1]
    s.arrow([(x1, AY), (x2 - 1, AY)], INK, sw=2)
    gx = (x1 + x2) / 2
    s.lines(gx, 84, trans[i], size=10, anchor="middle", lh=12)
    s.path(f"M{gx},{84 + 12 * len(trans[i]) - 8} L{gx},{AY - 6}", stroke="#999", sw=1, dash="2,2")

# LOCKED -> IDLE (normal exit) along the bottom
s.wire([(xs[4] + 60, BY + BH), (xs[4] + 60, 362), (xs[0] + 95, 362), (xs[0] + 95, BY + BH + 1)], INK, sw=2, marker="arrK")
s.lines(785, 374, ["ring absent ≥ 200 ms:", "only a removed ring re-arms the prop"], size=10, anchor="end", lh=12)

# abort edges: ring absent in ARMED / FLASH / POURING -> pump off -> IDLE
for i in (1, 2, 3):
    s.wire([(xs[i] + 30, BY + BH), (xs[i] + 30, 404)], RED, sw=1.8, dash="6,4")
s.wire([(xs[3] + 30, 404), (xs[0] + 40, 404), (xs[0] + 40, BY + BH + 1)], RED, sw=1.8, dash="6,4", marker="arrR")
s.rect(290, 410, 420, 22, rx=11, fill="#fdecea", stroke=RED, sw=1)
s.text(500, 425, "ABORT: ring absent ≥ 200 ms in any state → pumpStop() → IDLE", size=11, anchor="middle", weight="bold", color=RED)

# boot entry
s.arrow([(xs[0] + 68, 110), (xs[0] + 68, BY - 1)], INK, sw=2)
s.text(xs[0] + 74, 125, "boot", size=10)

# ------------------------------------------------------------------ interlocks panel
PX, PY, PW, PH = 890, 72, 195, 360
s.rect(PX, PY, PW, PH, rx=8, fill="#fffbe6", stroke="#c9a227", sw=1.4)
s.text(PX + PW / 2, PY + 22, "Safety interlocks", size=13, anchor="middle", weight="bold")
s.path(f"M{PX + 12},{PY + 30} L{PX + PW - 12},{PY + 30}", stroke="#c9a227", sw=1)
items = [
    ["Pump pin driven LOW first", "thing in setup(), before", "anything else."],
    ["Switch alone never pumps;", "Hall alone never pumps."],
    ["Exactly one pour per ring", "insertion (pouredThis-", "Insertion flag)."],
    ["Ring removed at any time", "→ pump off at once (checked", "every loop, outside states)."],
    ["Absolute cap MAX_PUMP_MS", "= 20 s inside pumpService(),", "independent of the states."],
    ["Switch already pressed at", "boot (jammed cam) is ignored", "until it is released."],
    ["Debounce: Hall 100 ms in /", "200 ms out; switch 40 ms."],
    ["Hardware: master switch,", "fuses on 5 V and 12 V."],
]
y = PY + 48
for it in items:
    s.circle(PX + 16, y - 4, 3, fill="#c9a227", stroke="none")
    s.lines(PX + 26, y, it, size=9.5, lh=11.5)
    y += 11.5 * len(it) + 7

# ------------------------------------------------------------------ timing + bench strip
s.rect(30, 455, 836, 120, rx=8, fill="#f5f5f5", stroke="#bbb", sw=1)
s.text(44, 476, "Timing constants", size=12, weight="bold")
s.lines(44, 494, [
    "HALL_DEBOUNCE_MS 100   ·   RING_GONE_MS 200   ·   SWITCH_DEBOUNCE_MS 40   ·   FLASH_MS 220   ·   PUMP_RAMP_MS 300",
    "DEFAULT_POUR_MS 10 000 (replace after water calibration; a 44 mL shot at 200 mL/min ≈ 13 s)   ·   MAX_PUMP_MS 20 000",
    "DEFAULT_MAX_BRIGHT 160/255 (current budget for 84 pixels)",
], size=10, lh=14)
s.text(44, 550, "Bench (USB serial, 115200):", size=11, weight="bold")
s.text(210, 550, "status  ·  cal 10000 (pump for 10 s without the ring)  ·  pour 13000  ·  leds 160  ·  save  ·  stop", size=10, family="Menlo, Consolas, monospace")
s.text(44, 567, "Legend:", size=10, weight="bold")
s.wire([(100, 563), (130, 563)], INK, sw=2, marker="arrK"); s.text(136, 567, "transition", size=10)
s.wire([(210, 563), (240, 563)], RED, sw=1.8, dash="6,4", marker="arrR"); s.text(246, 567, "abort path (ring pulled)", size=10)

open("/home/user/temprepo/docs/images/state-machine.svg", "w").write(s.finish())
print("written")
