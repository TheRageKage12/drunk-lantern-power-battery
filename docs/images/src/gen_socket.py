import sys, math
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

W, H = 1100, 800
s = SVG(W, H, "Green Lantern power battery - charging socket mechanism")
s.text(20, 30, "Charging socket mechanism — top views at 0° (rest) and 45° (fired), and section A–A", size=18, weight="bold")
s.text(20, 48, "schematic, ~3 px = 1 mm; twist is clockwise seen from above; see cad/parts/socket.py for the exact geometry", size=11, color="#555")

SC = 3.0  # px per mm
HALO_FILL = "#c8f5c8"


def pol(cx, cy, r_mm, ang_deg):
    """angle measured clockwise from 12 o'clock"""
    a = math.radians(ang_deg)
    return cx + r_mm * SC * math.sin(a), cy - r_mm * SC * math.cos(a)


def arc_path(cx, cy, r_mm, a1, a2):
    x1, y1 = pol(cx, cy, r_mm, a1)
    x2, y2 = pol(cx, cy, r_mm, a2)
    large = 1 if abs(a2 - a1) > 180 else 0
    return f"M{x1:.1f},{y1:.1f} A{r_mm*SC:.1f},{r_mm*SC:.1f} 0 {large} 1 {x2:.1f},{y2:.1f}"


def top_view(cx, cy, theta, title):
    s.text(cx, cy - 150, title, size=13, anchor="middle", weight="bold")
    # faceplate 90 x 90 with 4 M3 inserts
    s.rect(cx - 135, cy - 135, 270, 270, rx=18, fill="#f4f4f4", sw=1.4)
    for dx in (-1, 1):
        for dy in (-1, 1):
            s.circle(cx + dx * 117, cy + dy * 117, 5, fill="#fff", sw=1.2)
            s.circle(cx + dx * 117, cy + dy * 117, 2, fill="#999", stroke="none")
    # halo (translucent ring) 68 OD / 50 ID over the NeoPixel ring
    s.path(arc_path(cx, cy, 34, 0, 359.9) + " Z", stroke=INK, sw=1.2, fill=HALO_FILL)
    s.circle(cx, cy, 25 * SC, fill="#dedede", sw=1.2)
    for k in range(24):
        x, y = pol(cx, cy, 29.5, k * 15)
        s.circle(x, y, 3.5, fill="#4caf50", stroke="none")
    # housing bore lip with loading gap at 12 o'clock
    s.path(arc_path(cx, cy, 18.3, 0, 360), stroke="#777", sw=2)
    # radial plunger channel at 300 deg (lower-right): r 18.3..34, 5.6 wide
    def rad_rect(r0, r1, hw, ang, **kw):
        pts = [pol(cx, cy, r0, ang + hw / r0 * 57.3), pol(cx, cy, r1, ang + hw / r1 * 57.3),
               pol(cx, cy, r1, ang - hw / r1 * 57.3), pol(cx, cy, r0, ang - hw / r0 * 57.3)]
        s.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", **kw)
    rad_rect(18.3, 34, 2.8, 300, stroke="#888", sw=1.2, fill="#f3f3f3", dash="3,2")
    # stop channel for the lug: 128..187 deg, r 18.3..23.5 (its end walls are the hard stops)
    s.path(arc_path(cx, cy, 21, 128, 187), stroke="#ddd", sw=14)
    s.path(arc_path(cx, cy, 21, 128, 187), stroke="#888", sw=1, dash="3,2")
    # D2F-L body at 3 o'clock, long side tangent (vertical)
    sx = cx + 26 * SC
    s.rect(sx, cy - 20, 17, 38, fill="#e8e8e8", sw=1.2)
    s.circle(sx + 8, cy - 11, 1.8, fill="#555", stroke="none")
    s.circle(sx + 8, cy + 8.5, 1.8, fill="#555", stroke="none")
    # ---- rotating group
    s.add(f'<g transform="rotate({theta} {cx} {cy})">')
    s.circle(cx, cy, 18 * SC, fill="#bdbdbd", sw=1.4)                    # rotor 36 OD
    # ramp on the rim, 300..345 deg at rest: r rises 18 -> 22, pushes the plunger out as the rotor turns
    ramp = [pol(cx, cy, 18, a) for a in range(300, 346, 5)] + [pol(cx, cy, 18 + 4 * (a - 300) / 45, a) for a in range(345, 299, -5)]
    s.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ramp) + " Z", stroke=INK, sw=1.2, fill="#a5a5a5")
    # stop lug at 180 deg (-X), 4 mm wide, out to r 22.5
    s.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in [pol(cx, cy, 17, 186), pol(cx, cy, 22.5, 186), pol(cx, cy, 22.5, 174), pol(cx, cy, 17, 174)]) + " Z", stroke=INK, sw=1.2, fill="#777")
    # keyed pocket: 24 mm disc + 6 mm tab pointing to 12 o'clock
    s.circle(cx, cy, 12 * SC, fill="#8d8d8d", sw=1)
    s.rect(cx - 3 * SC, cy - 17.5 * SC, 6 * SC, 6 * SC, fill="#8d8d8d", sw=1)
    s.circle(cx, cy, 12 * SC, fill="none", sw=1)
    # magnet pocket (hidden under the pocket floor)
    s.circle(cx, cy, 3 * SC, fill="#616161", sw=1, dash="2,2")
    # cam lobe on the rim, 50..70 deg at rest, 3 mm lift: presses the lever between 33 and 45 deg of twist
    s.path(f"M{pol(cx, cy, 18, 50)[0]:.1f},{pol(cx, cy, 18, 50)[1]:.1f} Q{pol(cx, cy, 23, 60)[0]:.1f},{pol(cx, cy, 23, 60)[1]:.1f} {pol(cx, cy, 18, 70)[0]:.1f},{pol(cx, cy, 18, 70)[1]:.1f}", stroke=INK, sw=1.2, fill="#bdbdbd")
    s.add("</g>")
    # plunger + spring in the radial channel: pushed out 4 mm when fired
    lift = 4 if theta else 0
    rad_rect(18.3 + lift, 22.8 + lift, 2.4, 300, stroke=INK, sw=1.2, fill="#1565c0")
    pts = []
    n = 8
    for k in range(n + 1):
        r = 22.8 + lift + (34 - 22.8 - lift) * k / n
        a = 300 + (1.4 if k % 2 else -1.4) * 57.3 / r
        pts.append(pol(cx, cy, r, a))
    s.wire(pts, "#1565c0", sw=1.6)
    # the switch lever: pressed or not
    if theta == 0:
        s.path(f"M{sx - 1},{cy + 14} L{sx - 9},{cy - 16}", stroke=INK, sw=2.2)
    else:
        s.path(f"M{sx - 1},{cy + 14} L{sx - 3},{cy - 16}", stroke=INK, sw=2.2)
    # rotation arrow
    if theta:
        s.path(arc_path(cx, cy, 39, -8, 40), stroke="#e65100", sw=2, marker="arrO")
        s.text(*pol(cx, cy, 43, 18), "twist 45°", size=10, color="#e65100", anchor="start")


top_view(330, 262, 0, "A  rest, 0°")
top_view(720, 262, 45, "B  fired, 45° (held against the spring)")

# ---------------------------------------------------------------- labels for the top views
def lab(x, y, rows, tx, ty, anchor="start", size=9.5):
    s.lines(x, y, rows, size=size, lh=12, anchor=anchor)
    ax = x - 5 if anchor == "start" else x + 5
    s.path(f"M{ax},{y - 4} L{tx},{ty}", stroke="#999", sw=1)
    s.dot(tx, ty, "#999", r=2.2)

# panel A: left column, right-aligned at x=165 (ordered so the leaders never cross)
cx, cy = 330, 262
lab(165, 112, ["cam lobe on the rim", "(50\u201370\u00b0 at rest, 3 mm lift)"], *pol(cx, cy, 23, 60), anchor="end")
lab(165, 150, ["rotor drops in from below; the", "base plate closes the housing", "and carries the Hall board"], *pol(cx, cy, 18.3, 10), anchor="end")
lab(165, 200, ["translucent halo ring (68 OD)", "over the 24-px NeoPixel ring"], *pol(cx, cy, 31, 300), anchor="end")
lab(165, 240, ["stop lug (printed, at 9 o'clock)", "in a 59\u00b0 channel: its walls are", "the hard stops at 0\u00b0 and 45\u00b0"], *pol(cx, cy, 20, 180), anchor="end")
lab(165, 290, ["keyed pocket: 24 mm disc +", "6\u00d74 mm tab (matches the", "ring key cap)"], *pol(cx, cy, 12, 270), anchor="end")
lab(165, 340, ["6\u00d72 mm magnet in the key cap,", "on the axis: it never moves", "when the ring is twisted"], cx - 4, cy + 4, anchor="end")
lab(165, 390, ["0.5\u00d75\u00d710 mm spring + plunger in a", "radial pocket press on the rim", "ramp: it pushes the rotor back to 0\u00b0"], *pol(cx, cy, 30, 300), anchor="end")
lab(165, 440, ["faceplate 100 mm round,", "4\u00d7 M3 into dish-floor inserts"], cx - 117, cy + 117, anchor="end")
lab(165, 478, ["ramp on the rim, 300\u2013345\u00b0"], *pol(cx, cy, 20, 322), anchor="end")
# panel B: right column, left-aligned at x=875
cx, cy = 720, 262
lab(875, 112, ["twist the ring 45\u00b0 clockwise", "(seen from above)"], *pol(cx, cy, 39, 30), anchor="start")
lab(875, 160, ["stop lug against the channel", "wall = 45\u00b0 hard stop"], *pol(cx, cy, 20, 135), anchor="start")
lab(875, 205, ["D2F-L on a slotted bracket", "(slide it to tune the click angle)"], cx + 26 * SC + 17, cy - 17, anchor="start")
lab(875, 250, ["cam lobe has pressed the D2F-L", "lever 3 mm after ~40\u00b0 of twist:", "click (SW goes LOW)"], *pol(cx, cy, 23, 20), anchor="start")
lab(875, 300, ["magnet still centred on the", "Hall sensor: Hall stays LOW", "through the whole twist"], cx + 4, cy + 4, anchor="start")
lab(875, 350, ["plunger pushed out 4 mm by the", "ramp; let go and it pushes the", "rotor back to 0\u00b0 (switch releases)"], *pol(cx, cy, 30, 300), anchor="start")
lab(875, 400, ["ramp now under the plunger"], *pol(cx, cy, 21, 290), anchor="start")

# ---------------------------------------------------------------- section A-A
s.path("M60,488 L1040,488", stroke="#ccc", sw=1)
s.text(20, 512, "Section A–A (axis, stop pin, switch) — ring inserted, 0°", size=13, weight="bold")
cx, Y0 = 520, 582   # Y0 = top of the faceplate
# housing cup: 80 OD, 70 ID, floor 2.4 mm
s.rect(cx - 120, Y0 + 9, 15, 95, fill="#d7d7d7", sw=1.2)
s.rect(cx + 105, Y0 + 9, 15, 95, fill="#d7d7d7", sw=1.2)
s.rect(cx - 120, Y0 + 97, 240, 7, fill="#d7d7d7", sw=1.2)
# bosses with inserts
for dx in (-1, 1):
    s.rect(cx + dx * 128 - 8, Y0 + 9, 16, 28, fill="#d7d7d7", sw=1.2)
    s.rect(cx + dx * 128 - 3, Y0 + 9, 6, 20, fill="#9e9e9e", sw=0.8)
# faceplate 3 mm with bore 47 mm; halo 68/50 flush; LED PCB underneath
s.rect(cx - 135, Y0, 33, 9, fill="#f4f4f4", sw=1.2)
s.rect(cx + 102, Y0, 33, 9, fill="#f4f4f4", sw=1.2)
s.rect(cx - 102, Y0, 27, 9, fill=HALO_FILL, sw=1.2)
s.rect(cx + 75, Y0, 27, 9, fill=HALO_FILL, sw=1.2)
s.rect(cx - 75, Y0, 5, 9, fill="#f4f4f4", sw=1.2)
s.rect(cx + 70, Y0, 5, 9, fill="#f4f4f4", sw=1.2)
s.rect(cx - 98, Y0 + 9, 20, 5, fill="#2e7d32", sw=0.8)      # LED PCB
s.rect(cx + 78, Y0 + 9, 20, 5, fill="#2e7d32", sw=0.8)
s.rect(cx - 91, Y0 + 5, 6, 4, fill="#ffeb3b", sw=0.6)        # LED
s.rect(cx + 85, Y0 + 5, 6, 4, fill="#ffeb3b", sw=0.6)
# rotor: 44 OD body, flange tab under the lip, pocket on top, recess underneath for the sensor
s.rect(cx - 66, Y0 + 3, 132, 54, fill="#bdbdbd", sw=1.2)
s.rect(cx - 72, Y0 + 9, 6, 6, fill="#9e9e9e", sw=1)            # flange tab (left, 9 o'clock)
s.rect(cx - 36, Y0 + 3, 72, 8, fill="#8d8d8d", sw=1)           # key pocket
s.rect(cx - 30, Y0 + 20, 60, 37, fill="#ffffff", sw=1)         # recess from below
# ring key cap in the pocket, magnet centred
s.rect(cx - 36, Y0 + 3, 72, 8, fill="#2e7d32", sw=1)
s.rect(cx - 9, Y0 + 4, 18, 6, fill="#616161", sw=0.8)
s.text(cx, Y0 + 9, "N  S", size=6, anchor="middle", color="#fff", weight="bold")
# the ring standing on its key cap
s.circle(cx, Y0 - 34, 34, fill="none", stroke="#2e7d32", sw=9)
# Hall sensor on a post under the rotor floor, on the axis
s.rect(cx - 4, Y0 + 23, 8, 5, fill="#222", sw=0.6)             # sensor chip
s.rect(cx - 22, Y0 + 28, 44, 5, fill="#1a237e", sw=0.8)        # breakout PCB
s.rect(cx + 14, Y0 + 33, 7, 64, fill="#d7d7d7", sw=1)          # post to the floor
# stop pin: M3 screw through the rotor into the arc slot in the floor
s.rect(cx - 53, Y0 + 1, 6, 98, fill="#444", sw=0.8)
s.rect(cx - 57, Y0 - 1, 14, 4, fill="#444", sw=0.8)
s.rect(cx - 60, Y0 + 97, 20, 7, fill="#ffffff", sw=1)           # arc slot (open through the floor)
# switch under the cam lobe (right): body on the floor, lever on top
s.rect(cx + 64, Y0 + 70, 38, 17, fill="#e8e8e8", sw=1.2)
s.path(f"M{cx + 98},{Y0 + 68} L{cx + 66},{Y0 + 62}", stroke=INK, sw=2.2)
s.rect(cx + 64, Y0 + 87, 38, 10, fill="#d7d7d7", sw=1)          # slotted mount block
s.path(f"M{cx + 60},{Y0 + 48} L{cx + 74},{Y0 + 48} L{cx + 74},{Y0 + 58} L{cx + 60},{Y0 + 58}", stroke=INK, sw=1, dash="3,2", fill="none")  # cam lobe (out of plane)
# spring, end-on (out of plane), lower-left
s.circle(cx - 87, Y0 + 80, 7, fill="none", stroke="#1565c0", sw=1.4, dash="3,2")
# cable out through the floor
s.wire([(cx + 40, Y0 + 97), (cx + 40, Y0 + 125)], "#7c3aed", sw=1.6, dash="4,3")
s.text(cx + 46, Y0 + 128, "J1 6-wire cable to the base", size=9, color="#7c3aed")
# axis line
s.path(f"M{cx},{Y0 - 80} L{cx},{Y0 + 115}", stroke="#999", sw=0.8, dash="8,3,2,3")

# section labels: left
LXS = 300
lab(LXS, 567, ["Green Lantern ring (20 mm), inserted", "face-down; the printed key cap is", "glued to its emblem face"], cx - 30, Y0 - 50, anchor="end", size=9.5)
lab(LXS, 617, ["stop lug on the rotor rim rides in", "a channel under the faceplate lip;", "the lip also retains the rotor"], cx - 50, Y0 + 40, anchor="end", size=9.5)
lab(LXS, 667, ["translucent halo flush with the", "faceplate; 24-px ring PCB right", "under it, LEDs facing up"], cx - 88, Y0 + 4, anchor="end", size=9.5)
lab(LXS, 717, ["spring + plunger (out of plane,", "lower right) in a radial pocket,", "10 mm spring, 4 mm stroke"], cx - 94, Y0 + 80, anchor="end", size=9.5)
lab(LXS, 762, ["housing puck 76 OD, 6.7 deep;", "base plate 3.5 mm, 3× M3 + nuts"], cx - 120, Y0 + 100, anchor="end", size=9.5)
# section labels: right
RXS = 760
lab(RXS, 567, ["6×2 mm magnet in the key cap,", "on the rotation axis"], cx + 9, Y0 + 7, anchor="start", size=9.5)
lab(RXS, 612, ["rotor 36 OD × 8 flat disc; its rim", "lugs ride under the faceplate lip"], cx + 66, Y0 + 20, anchor="start", size=9.5)
lab(RXS, 657, ["DRV5032 breakout in the base plate,", "chip down under the sensor window,", "~8 mm below the magnet"], cx + 4, Y0 + 26, anchor="start", size=9.5)
lab(RXS, 707, ["D2F-L on its pegged bracket in the", "base plate (lobe dashed: at 50–70°,", "out of this plane)"], cx + 90, Y0 + 70, anchor="start", size=9.5)
lab(RXS, 757, ["cables through the floor grommet", "down the sphere's wire channel"], cx + 40, Y0 + 115, anchor="start", size=9.5)

open(os.path.join(HERE, "..", "socket-mechanism.svg"), "w").write(s.finish())
print("written")
