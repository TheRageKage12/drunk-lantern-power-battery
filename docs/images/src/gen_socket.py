import sys, math
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY, INK

W, H = 1100, 800
s = SVG(W, H, "Green Lantern power battery - charging socket mechanism")
s.text(20, 30, "The lock — face views at 0° (rest) and 45° (fired), and section A–A", size=18, weight="bold")
s.text(20, 48, "schematic, ~3 px = 1 mm; seen from your side (the hand opening); the twist is counterclockwise; exact geometry in cad/parts/socket.py", size=11, color="#555")

SC = 3.0  # px per mm
MIRROR = True   # the lock is built mirrored (params.LOCK_TWIST = 'ccw'): draw the face views mirrored too
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
    if MIRROR:
        s.add(f'<g transform="translate({2 * cx},0) scale(-1,1)">')
    # lock wall behind, and the base plate's two mounting ears (lower left / lower right, screwed to the wall)
    s.rect(cx - 140, cy - 140, 280, 280, fill="#f4f4f4", stroke="#bbb", sw=1)
    for ang in (130.0, 230.0):                       # 40 and 140 deg in the socket frame, drawn clockwise from 12
        ex, ey = pol(cx, cy, 53, ang)
        bx, by = pol(cx, cy, 36, ang)
        s.path(f"M{bx:.1f},{by:.1f} L{ex:.1f},{ey:.1f}", stroke="#cfcfcf", sw=30)
        s.circle(ex, ey, 15, fill="#cfcfcf", stroke="#999", sw=1)
        s.circle(ex, ey, 5, fill="#fff", stroke="#777", sw=1)
    # housing (76 OD) - its face is what you see
    s.circle(cx, cy, 38 * SC, fill="#ececec", stroke="#999", sw=1.2)
    s.circle(cx, cy, 25 * SC, fill="#dedede", sw=1.2)
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
    # emblem pocket: the ring's raised emblem (circle + two bars) is the key; bars level at rest
    s.circle(cx, cy, 6.3 * SC, fill="#8d8d8d", sw=1)
    for sy in (-1, 1):
        s.rect(cx - 7.8 * SC, cy + (sy * 9.0 - 1.7) * SC, 15.6 * SC, 3.4 * SC, fill="#8d8d8d", sw=1)
    s.circle(cx, cy, 3.3 * SC, fill="#a5a5a5", sw=0.8)
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
    if MIRROR:
        s.add("</g>")
    if theta:
        tx, ty = pol(cx, cy, 43, 18)
        s.text(2 * cx - tx if MIRROR else tx, ty, "twist 45°", size=10, color="#e65100", anchor="end" if MIRROR else "start")


top_view(330, 262, 0, "A  rest, 0°")
top_view(720, 262, 45, "B  fired, 45° (held against the spring)")

# ---------------------------------------------------------------- labels for the top views
PANEL_CX = None


def lab(x, y, rows, tx, ty, anchor="start", size=9.5):
    if MIRROR and PANEL_CX is not None:
        tx = 2 * PANEL_CX - tx
    s.lines(x, y, rows, size=size, lh=12, anchor=anchor)
    ax = x - 5 if anchor == "start" else x + 5
    s.path(f"M{ax},{y - 4} L{tx},{ty}", stroke="#999", sw=1)
    s.dot(tx, ty, "#999", r=2.2)

# panel A: left column, right-aligned at x=165
cx, cy = 330, 262
PANEL_CX = cx
lab(165, 112, ["cam lobe on the rim", "(50\u201370\u00b0 at rest, 3 mm lift)"], *pol(cx, cy, 23, 60), anchor="end")
lab(165, 150, ["rotor drops in from below; the", "base plate closes the housing", "and carries the Hall sensor post"], *pol(cx, cy, 18.3, 10), anchor="end")
lab(165, 200, ["housing, 76 mm across: its", "face is flush with the ring pocket"], *pol(cx, cy, 38, 300), anchor="end")
lab(165, 240, ["stop lug (printed, at %s o'clock)" % ("3" if MIRROR else "9"), "in a 59\u00b0 channel: its walls are", "the hard stops at 0\u00b0 and 45\u00b0"], *pol(cx, cy, 20, 180), anchor="end")
lab(165, 290, ["emblem pocket: the ring's", "raised emblem is the key;", "its bars turn the rotor"], *pol(cx, cy, 9, 270), anchor="end")
lab(165, 340, ["6\u00d72 mm magnet hidden in", "the ring, on the axis: it never", "moves when the ring is twisted"], cx - 4, cy + 4, anchor="end")
lab(165, 390, ["0.5\u00d75\u00d710 mm spring + plunger in a", "radial pocket press on the rim", "ramp: it pushes the rotor back to 0\u00b0"], *pol(cx, cy, 30, 300), anchor="end")
lab(165, 440, ["two ears on the base plate:", "M3x10 + nut through the lock wall"], *pol(cx, cy, 53, 230), anchor="end")
lab(165, 478, ["ramp on the rim, 300\u2013345\u00b0"], *pol(cx, cy, 20, 322), anchor="end")
# panel B: right column, left-aligned at x=875
cx, cy = 720, 262
PANEL_CX = cx
lab(875, 112, ["twist the ring 45\u00b0 %s" % ("counterclockwise" if MIRROR else "clockwise"), "(as you see it)"], *pol(cx, cy, 39, 30), anchor="start")
lab(875, 160, ["stop lug against the channel", "wall = 45\u00b0 hard stop"], *pol(cx, cy, 20, 135), anchor="start")
lab(875, 205, ["D2F-01L on a sliding bracket", "(its screw rides in a slot: loosen,", "push, tighten to tune the click)"], cx + 26 * SC + 17, cy - 17, anchor="start")
lab(875, 250, ["cam lobe has pressed the D2F-01L", "lever 3 mm after ~40\u00b0 of twist:", "click (SW goes LOW)"], *pol(cx, cy, 23, 20), anchor="start")
lab(875, 300, ["magnet still centred on the", "Hall sensor: Hall stays LOW", "through the whole twist"], cx + 4, cy + 4, anchor="start")
lab(875, 350, ["plunger pushed out 4 mm by the", "ramp; let go and it pushes the", "rotor back to 0\u00b0 (switch releases)"], *pol(cx, cy, 30, 300), anchor="start")
lab(875, 400, ["ramp now under the plunger"], *pol(cx, cy, 21, 290), anchor="start")

PANEL_CX = None

# ---------------------------------------------------------------- section A-A
s.path("M60,488 L1040,488", stroke="#ccc", sw=1)
s.text(20, 512, "Section A–A (axis, stop lug, switch) — ring inserted, 0°; drawn face up (in the lantern the face points at you)", size=13, weight="bold")
cx, Y0 = 520, 582   # Y0 = the socket face
# housing cup: 80 OD, 70 ID, floor 2.4 mm
s.rect(cx - 120, Y0 + 9, 15, 95, fill="#d7d7d7", sw=1.2)
s.rect(cx + 105, Y0 + 9, 15, 95, fill="#d7d7d7", sw=1.2)
s.rect(cx - 120, Y0 + 97, 240, 7, fill="#d7d7d7", sw=1.2)
# the lock wall under the base plate (2.4 mm), with the window for the cables
s.rect(cx - 170, Y0 + 104, 340, 7, fill="#e0e0e0", sw=1.2)
s.rect(cx - 51, Y0 + 104, 102, 7, fill="#ffffff", sw=1, dash="2,2")
# housing lip around the ring pocket
s.rect(cx - 102, Y0, 27, 9, fill="#f4f4f4", sw=1.2)
s.rect(cx + 75, Y0, 27, 9, fill="#f4f4f4", sw=1.2)
s.rect(cx - 75, Y0, 5, 9, fill="#f4f4f4", sw=1.2)
s.rect(cx + 70, Y0, 5, 9, fill="#f4f4f4", sw=1.2)
# rotor: 44 OD body, flange tab under the lip, pocket on top, recess underneath for the sensor
s.rect(cx - 66, Y0 + 3, 132, 54, fill="#bdbdbd", sw=1.2)
s.rect(cx - 72, Y0 + 9, 6, 6, fill="#9e9e9e", sw=1)            # flange tab (left, 9 o'clock)
s.rect(cx - 19, Y0 + 3, 38, 12, fill="#8d8d8d", sw=1)          # emblem pocket (circle section)
s.rect(cx - 16, Y0 + 18, 32, 39, fill="#ffffff", sw=1)         # blind hole from below (1 mm skin under the magnet)
# the ring's raised emblem in the pocket; magnet hidden behind the centre disc
s.rect(cx - 18, Y0 - 2, 36, 16, fill="#2e7d32", sw=1)
s.rect(cx - 9, Y0 + 4, 18, 6, fill="#616161", sw=0.8)
s.text(cx, Y0 + 9, "N  S", size=6, anchor="middle", color="#fff", weight="bold")
s.rect(cx - 40, Y0 - 6, 80, 5, fill="#2e7d32", sw=1)           # ring head resting on the rotor face
# the ring band
s.circle(cx, Y0 - 34, 34, fill="none", stroke="#2e7d32", sw=9)
# A3144 on a post that rises from the base plate into the rotor's blind hole, on the axis
s.rect(cx - 12, Y0 + 30, 24, 67, fill="#d7d7d7", sw=1)         # post (stationary; the rotor turns around it)
s.rect(cx - 8, Y0 + 30, 16, 6, fill="#222", sw=0.6)            # A3144, printed face up
s.wire([(cx - 6, Y0 + 36), (cx - 6, Y0 + 125)], "#7c3aed", sw=1.2, dash="4,3")   # leads down the post
# switch under the cam lobe (right): body on the floor, lever on top
s.rect(cx + 64, Y0 + 70, 38, 17, fill="#e8e8e8", sw=1.2)
s.path(f"M{cx + 98},{Y0 + 68} L{cx + 66},{Y0 + 62}", stroke=INK, sw=2.2)
s.rect(cx + 64, Y0 + 87, 38, 10, fill="#d7d7d7", sw=1)          # slotted mount block
s.path(f"M{cx + 60},{Y0 + 48} L{cx + 74},{Y0 + 48} L{cx + 74},{Y0 + 58} L{cx + 60},{Y0 + 58}", stroke=INK, sw=1, dash="3,2", fill="none")  # cam lobe (out of plane)
# spring, end-on (out of plane), lower-left
s.circle(cx - 87, Y0 + 80, 7, fill="none", stroke="#1565c0", sw=1.4, dash="3,2")
# cable out through the floor
s.wire([(cx + 40, Y0 + 97), (cx + 40, Y0 + 125)], "#7c3aed", sw=1.6, dash="4,3")
s.text(cx + 46, Y0 + 128, "socket cable to the base", size=9, color="#7c3aed")
# axis line
s.path(f"M{cx},{Y0 - 80} L{cx},{Y0 + 115}", stroke="#999", sw=0.8, dash="8,3,2,3")

# section labels: left
LXS = 300
lab(LXS, 567, ["printed Green Lantern ring, emblem", "first: the emblem drops into the", "pocket, the head rests on the rotor"], cx - 30, Y0 - 50, anchor="end", size=9.5)
lab(LXS, 617, ["stop lug on the rotor rim rides in", "a channel under the housing's lip;", "the lip also retains the rotor"], cx - 50, Y0 + 40, anchor="end", size=9.5)
lab(LXS, 667, ["lock wall behind the base plate;", "a window in it passes the cables", "to the hidden side"], cx - 140, Y0 + 108, anchor="end", size=9.5)
lab(LXS, 717, ["spring + plunger (out of plane,", "lower right) in a radial pocket,", "10 mm spring, 4 mm stroke"], cx - 94, Y0 + 80, anchor="end", size=9.5)
lab(LXS, 762, ["housing puck 76 OD, 6.7 deep;", "base plate 3.5 mm, 3× M3 + nuts"], cx - 120, Y0 + 100, anchor="end", size=9.5)
# section labels: right
RXS = 760
lab(RXS, 567, ["6×2 mm magnet inside the ring,", "0.6 mm behind the emblem's centre"], cx + 9, Y0 + 7, anchor="start", size=9.5)
lab(RXS, 612, ["rotor 36 OD × 8 flat disc; its rim", "lug rides under the housing's lip"], cx + 66, Y0 + 20, anchor="start", size=9.5)
lab(RXS, 657, ["A3144 on a post up inside the rotor,", "~3.7 mm below the magnet; the rotor", "turns around the post"], cx + 8, Y0 + 33, anchor="start", size=9.5)
lab(RXS, 707, ["D2F-01L on its pegged bracket in the", "base plate (lobe dashed: at 50–70°,", "out of this plane)"], cx + 90, Y0 + 70, anchor="start", size=9.5)
lab(RXS, 757, ["cables through the wall window,", "down behind the wall to the base"], cx + 40, Y0 + 115, anchor="start", size=9.5)

open(os.path.join(HERE, "..", "socket-mechanism.svg"), "w").write(s.finish())
print("written")
