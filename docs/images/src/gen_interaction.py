import sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

W, H = 1100, 470
s = SVG(W, H, "Green Lantern power battery - performance timeline")
s.text(20, 30, "The performance — timeline of one pour", size=20, weight="bold")
s.text(20, 48, "hold-to-pour: the pour and the brightening light happen during the oath; seconds are approximate (pour time = pourMs)", size=11, color="#555")

T0, T1 = -4, 24
X0, X1 = 70, 1060
def X(t):
    return X0 + (t - T0) * (X1 - X0) / (T1 - T0)

# ------------------------------------------------------------------ bands
P0, P1 = 2.0, 13.0     # pour: twist at 2 s, ~11 s
R1 = 15.0              # ring turned back
F1 = R1 + 1.9          # finale done
OUT = 19.0             # ring out
bands = [
    ("state", 168, 24, [(T0, 0, "#e0e0e0", "IDLE"), (0, P0, "#e3f2e3", "ARMED"), (P0, P1, "#81c784", "POURING"), (P1, R1, "#b9dfba", "HOLDING"), (R1, F1, "#f1fff1", "FINALE"), (F1, OUT, "#e0e0e0", "LOCKED"), (OUT, T1, "#e0e0e0", "IDLE")]),
    ("light", 198, 22, [(T0, 0, "#ffffff", "dark"), (0, P0, "#e8f5e9", "15 %"), (P0, P1, "#81c784", "climbs 15 % → 90 %"), (P1, R1, "#43a047", "90 %"), (R1, R1 + 0.7, "#2e7d32", ""), (R1 + 0.7, F1, "#c8e6c9", "fade"), (F1, T1, "#ffffff", "dark")]),
    ("pump", 226, 18, [(T0, P0, "#f5f5f5", "off"), (P0, P1, "#ffcc80", "ON ~11 s (about 1 oz)"), (P1, T1, "#f5f5f5", "off")]),
    ("ring", 250, 18, [(T0, 0, "#f5f5f5", "out"), (0, P0, "#dcedc8", "in, 0°"), (P0, R1, "#aed581", "twisted to 45° and held"), (R1, OUT, "#dcedc8", "back at 0°"), (OUT, T1, "#f5f5f5", "hand out")]),
]
for name, y, h, segs in bands:
    s.text(X0 - 8, y + h / 2 + 4, name, size=11, anchor="end", weight="bold")
    for t1, t2, col, lab in segs:
        x1, x2 = X(t1), X(t2)
        s.rect(x1, y, max(x2 - x1, 1), h, fill=col, stroke="#999", sw=0.8)
        if lab:
            s.text((x1 + x2) / 2, y + h / 2 + 3.5, lab, size=9, anchor="middle", color="#fff" if col in ("#43a047",) else INK)
s.text(X(R1 + 0.35), 194, "100 %", size=8.5, anchor="middle", color="#1b5e20")

# ------------------------------------------------------------------ axis
AXY = 282
s.path(f"M{X0},{AXY} L{X1},{AXY}", stroke=INK, sw=1.6, marker="arrK")
for t in range(-4, 25, 2):
    x = X(t)
    s.path(f"M{x},{AXY - 4} L{x},{AXY + 4}", stroke=INK, sw=1.2)
    s.text(x, AXY + 17, f"{t} s" if t != 0 else "0 s (ring in)", size=9.5, anchor="middle")
for t in range(-4, 24):
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
callout(0, -3, 60, 78, ["Before: empty shot glass", "pushed back under the lock.", "Lantern dark."], True)
callout(2, 7, 300, 78, ["Hold the twist through the oath:", "the pump pours and the light", "climbs from 15 % to 90 %."], True, width=200)
callout(4, R1, 600, 78, ["Turn back: the light swells", "to 100 %, then goes dark.", "The pour is complete."], True, width=190)
callout(6, OUT, 860, 78, ["Grip the glass, slide it", "toward you, lift it out:", "re-arms for next time."], True, width=170)
# oath span bracket
s.path(f"M{X(P0)},150 L{X(P0)},144 L{X(R1)},144 L{X(R1)},150", stroke="#1b5e20", sw=1.2)
s.text(X((P0 + R1) / 2), 140, "the oath", size=8.5, anchor="middle", color="#1b5e20")

# below the axis
callout(1, 0, 60, 348, ["Punch in, ring face first:", "the light fades up to ~15 %."], False)
callout(3, P0, 260, 348, ["On the first line, twist 45° and", "hold: the cam clicks the switch", "and the pump starts."], False, width=200)
callout(5, P1, 520, 348, ["The pour finishes (~11 s) while", "you are still holding; the light", "stays at 90 %."], False, width=200)
callout(7, OUT + 1, 800, 348, ["Bring the glass out", "through the cover.", "Cheers."], False)

# notes
s.text(20, 455, "Let go early and the pump stops where it is; the light swells ~10 % and goes dark (no resume until the ring is removed and re-inserted). Pulling the ring out stops the pump within 60 ms.", size=9.5, color="#444")

open(os.path.join(HERE, "..", "interaction.svg"), "w").write(s.finish())
print("written")
