import sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

W, H = 1100, 470
s = SVG(W, H, "Green Lantern power battery - performance timeline")
s.text(20, 30, "The performance — timeline of one pour", size=20, weight="bold")
s.text(20, 48, "seconds are approximate; the pour length comes from the water calibration (pourMs)", size=11, color="#555")

T0, T1 = -5, 40
X0, X1 = 70, 1060
def X(t):
    return X0 + (t - T0) * (X1 - X0) / (T1 - T0)

# ------------------------------------------------------------------ bands
bands = [
    ("state", 168, 24, [(-5, 0, "#e0e0e0", "IDLE"), (0, 20, "#c8e6c9", "ARMED"), (20, 20.22, "#ffffff", ""), (20.22, 33.5, "#81c784", "POURING"), (33.5, 36, "#a5d6a7", "LOCKED"), (36, 40, "#e0e0e0", "IDLE")]),
    ("LEDs", 198, 22, [(-5, 0, "#e8f5e9", "ember"), (0, 20, "#c8e6c9", "pulse builds (ceiling rises over 20 s)"), (20, 20.22, "#ffffff", ""), (20.22, 33.5, "#66bb6a", "swirl + comet"), (33.5, 36, "#a5d6a7", "afterglow"), (36, 40, "#e8f5e9", "ember")]),
    ("pump", 226, 18, [(-5, 20.22, "#f5f5f5", "off"), (20.22, 33.5, "#ffcc80", "ON: 0.3 s ramp, then full speed"), (33.5, 40, "#f5f5f5", "off")]),
    ("ring", 250, 18, [(-5, 0, "#f5f5f5", "out"), (0, 20, "#dcedc8", "in the socket at 0°"), (20, 21, "#aed581", ""), (21, 36, "#dcedc8", "in at 0° (sprung back)"), (36, 40, "#f5f5f5", "out")]),
]
for name, y, h, segs in bands:
    s.text(X0 - 8, y + h / 2 + 4, name, size=11, anchor="end", weight="bold")
    for t1, t2, col, lab in segs:
        x1, x2 = X(t1), X(t2)
        s.rect(x1, y, max(x2 - x1, 1), h, fill=col, stroke="#999", sw=0.8)
        if lab:
            s.text((x1 + x2) / 2, y + h / 2 + 3.5, lab, size=9, anchor="middle")
# flash marker (220 ms is too narrow to label inside)
s.rect(X(20) - 1, 168, 4, 52, fill="#ffffff", stroke="#f9a825", sw=1.2)
s.text(X(20) + 1, 160, "FLASH 220 ms", size=8.5, anchor="middle", color="#8d6e00")
s.text(X(20.5), 263, "45°", size=8, anchor="middle")

# ------------------------------------------------------------------ axis
AXY = 282
s.path(f"M{X0},{AXY} L{X1},{AXY}", stroke=INK, sw=1.6, marker="arrK")
for t in range(-5, 41, 5):
    x = X(t)
    s.path(f"M{x},{AXY - 4} L{x},{AXY + 4}", stroke=INK, sw=1.2)
    s.text(x, AXY + 17, f"{t} s" if t != 0 else "0 s (ring in)", size=9.5, anchor="middle")
for t in range(-5, 40):
    x = X(t)
    s.path(f"M{x},{AXY - 2} L{x},{AXY + 2}", stroke="#999", sw=0.8)


def callout(num, t, bx, by, rows, above, width=172):
    """numbered text block whose leader runs from the time t to the block"""
    x = X(t)
    s.circle(bx + 9, by - 4, 9, fill="#1b5e20", stroke="none")
    s.text(bx + 9, by - 0.5, str(num), size=10, anchor="middle", color="#fff", weight="bold")
    s.lines(bx + 24, by, rows, size=10, lh=12.5)
    if above:
        s.path(f"M{x},{166} L{x},{by + 12.5 * len(rows) - 4} L{min(max(bx + 24, x - 40), bx + width - 20)},{by + 12.5 * len(rows) - 4}", stroke="#999", sw=1)
        s.dot(x, 166, "#1b5e20", r=2.5)
    else:
        s.path(f"M{x},{AXY + 24} L{x},{by - 14} L{min(max(bx + 24, x - 40), bx + width - 20)},{by - 14}", stroke="#999", sw=1)
        s.dot(x, AXY + 24, "#1b5e20", r=2.5)


# above the bands
callout(0, -4, 60, 78, ["Before: put the empty shot", "glass in the bay, shut the", "rear hatch. Faint ember."], True)
callout(2, 10, 250, 78, ["Recite the oath (~15–20 s).", "The glow pulses and builds;", "one pixel orbits the socket."], True)
callout(4, 20.22, 500, 78, ["FLASH: ring + strip white-", "green for 220 ms, then the", "pump soft-starts (0.3 s)."], True)
callout(6, 27, 720, 78, ["~13 s pour with the swirl", "light show; the hidden glass", "fills behind the diffuser."], True)
callout(8, 36, 920, 78, ["Remove the ring → IDLE", "ember. Ready for the", "next insertion."], True, width=160)
# oath span bracket
s.path(f"M{X(1)},150 L{X(1)},144 L{X(19)},144 L{X(19)},150", stroke="#1b5e20", sw=1.2)
s.text(X(10), 140, "oath", size=8.5, anchor="middle", color="#1b5e20")

# below the axis
callout(1, 0, 60, 348, ["Insert the ring: the magnet", "trips the Hall sensor →", "ARMED after 100 ms."], False)
callout(3, 20, 330, 348, ["Last line: twist the ring 45°", "against the spring → the cam", "clicks the microswitch."], False)
callout(5, 21, 560, 348, ["Let go: the rotor springs", "back to 0° (switch releases;", "the pour carries on)."], False)
callout(7, 33.5, 760, 348, ["Pour done → LOCKED after-", "glow (4 s fade to steady).", "No second pour this insertion."], False)
callout(9, 38, 950, 400, ["Open the rear hatch,", "reach in, take the", "full glass. Cheers."], False, width=140)

# notes
s.text(20, 455, "Pulling the ring out at any moment stops the pump immediately and returns to IDLE. The hatch faces the owner; the audience only sees the glow through the front window.", size=9.5, color="#444")

open(os.path.join(HERE, "..", "interaction.svg"), "w").write(s.finish())
print("written")
