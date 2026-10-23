"""fluid-path.svg: a true section of the CAD assembly at x = 0 (side view, front on the left), with the
tube, the cables, the hand and the glass's way out drawn over it.  Needs the cad/ environment and a built
cad/output (python3 cad/build.py), because the outlines come from the exported STLs."""
import os
import sys

import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.abspath(os.path.join(HERE, "..", "..", "..", "cad"))
sys.path.insert(0, HERE)
sys.path.insert(0, CAD)
from svgkit import SVG, GREY, INK  # noqa: E402
import params as P  # noqa: E402
import render_views as RV  # noqa: E402
import parts.sphere as SP  # noqa: E402
import parts.bells as BL  # noqa: E402
import parts.top as TP  # noqa: E402
import parts.base as BS  # noqa: E402

BLUE, LBLUE, PURPLE = "#1d4ed8", "#bfdbfe", "#7c3aed"
PRINT, PRINT_EDGE = "#a5d6a7", "#2e7d32"
SKIN, SKIN_EDGE = "#f1d3bd", "#a1887f"
HW, HW_EDGE = "#ffe0b2", "#ef6c00"

W, H = 1150, 900
SC = 1.5                      # px per mm
X0, Y0 = 560, 860             # assembly (y, z) = (0, 0) -> px

def px(y, z):
    return X0 + SC * y, Y0 - SC * z


s = SVG(W, H, "Green Lantern power battery - fluid path and layout, true section at x = 0")
s.text(20, 30, "Fluid path and layout — section through the centre, seen from the side", size=18, weight="bold")
s.text(20, 48, "Rev C, drawn from the CAD (cad/output); 1.5 px = 1 mm. Audience (front lens) on the left, your side (the hand bell) on the right. Tube route approximate.",
       size=11, color="#555")

pl = RV.placements()
M = RV.load_placed(pl)
TO_YZ = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], dtype=float)


def poly_d(poly):
    def ring(coords):
        pts = [px(y, z) for y, z in coords]
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return " ".join([ring(poly.exterior.coords)] + [ring(i.coords) for i in poly.interiors])


def draw_polys(polys, fill, edge, sw=0.9, dash=None, opacity=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    for p in polys:
        s.add(f'<path d="{poly_d(p)}" fill="{fill}" fill-rule="evenodd" stroke="{edge}" stroke-width="{sw}"'
              f' stroke-linejoin="round"{ds}{op}/>')


def section(name):
    sec = M[name].section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
    if sec is None:
        return []
    planar, _ = sec.to_planar(to_2D=TO_YZ, check=False)
    return list(planar.polygons_full)


def silhouette(name):
    """outline of the part projected onto the YZ plane (for parts off the section plane)"""
    m = M[name]
    tri = m.vertices[m.faces][:, :, 1:]
    polys = [Polygon(t) for t in tri if Polygon(t).area > 1e-6]
    u = trimesh.path.polygons.unary_union(polys) if hasattr(trimesh.path.polygons, "unary_union") else None
    if u is None:
        from shapely.ops import unary_union
        u = unary_union(polys)
    return list(u.geoms) if isinstance(u, MultiPolygon) else [u]


# ------------------------------------------------------------------ hardware behind the section (projected)
for n, fill in (("powerbank_envelope", "#e0e0e0"), ("pump_envelope", "#e0e0e0"), ("bag_envelope", LBLUE)):
    draw_polys(silhouette(n), fill, "#757575", sw=1, dash="4,3", opacity=0.85)
for n in ("handle_pivot_left",):
    draw_polys(silhouette(n), "none", GREY, sw=1, dash="5,4")
draw_polys(silhouette("nozzle_guide"), "#cfd8dc", INK, sw=1)

import math
Zc0, R = P.Z_SPHERE_CENTER, P.SPHERE_D / 2
# sphere outline: this cut passes through both openings, so dash the shell between each opening and the flats
for sgn, r_open in ((-1, P.LENS_OPENING_R), (1, P.HAND_OPENING_R)):
    for zs in (1, -1):
        t0, t1 = math.asin(r_open / R), math.asin(P.SPHERE_CUT / R)
        pts = [px(sgn * R * math.cos(t), Zc0 + zs * R * math.sin(t)) for t in np.linspace(t0, t1, 20)]
        s.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), stroke=PRINT_EDGE, sw=1.2, dash="6,4")

# ------------------------------------------------------------------ printed parts, cut at x = 0
for n in sorted(M):
    if n.endswith("_envelope") or n.startswith("handle") or n == "screw_cap":
        continue
    fill = "#ffffff" if n in ("diffuser", "led_panel", "halo_ring", "wall_extension") else ("#e0e0e0" if n in ("bay_floor", "guide_boss", "glass_well", "lock_wall", "base_tray", "cap_floor", "bag_cover") else PRINT)
    draw_polys(section(n), fill, PRINT_EDGE if fill == PRINT else "#616161", sw=0.9)

# ------------------------------------------------------------------ LED strips (green)
LED = "#43a047"


def led(y0, y1, z0, z1):
    (x0, py0), (x1, py1) = px(min(y0, y1), z0), px(max(y0, y1), z1)
    s.rect(x0, py1, x1 - x0, py0 - py1, fill=LED, stroke="none", sw=0)


yp = SP.PANEL_BACK_Y - SP.PANEL_T                        # rows on the white LED panel's front, facing the lens
for z0 in SP.PANEL_ROWS_Z:
    led(yp - 2.5, yp, Zc0 + z0 - 4, Zc0 + z0 + 4)
for sg in (-1, 1):                                        # the two bells' rings and the cap's emblem strips
    led(-BL.F_LED_S[0], -BL.F_LED_S[1], Zc0 + sg * BL.F_LED_R - 2.5, Zc0 + sg * BL.F_LED_R + 2.5)
    led(BL.R_LED_S[0], BL.R_LED_S[1], Zc0 + sg * BL.R_LED_R - 2.5, Zc0 + sg * BL.R_LED_R + 2.5)
    led(sg * (TP.R_CAP_IN - 2.5), sg * TP.R_CAP_IN, *TP.CAP_LED_Z)
zc0, zc1 = SP.FRONT_COL_Z                                 # columns on the front face, beside the lock (behind the cut)
(x0, y0), (x1, y1) = px(SP.WALL_FRONT_Y, SP.WALL_Z0 + zc0 + Zc0), px(SP.WALL_FRONT_Y + 1.5, SP.WALL_Z0 + zc1 + Zc0)
s.rect(x0, y1, x1 - x0, y0 - y1, fill="none", stroke=LED, sw=1.4, dash="3,2")

# ------------------------------------------------------------------ glass, at the pour position and on its way out
gz0 = P.Z_SPHERE_CENTER + P.GLASS_TOP_Z_LOCAL - P.GLASS_H
gy = P.GLASS_POUR_Y
rb, rt = P.GLASS_D_BASE / 2, P.GLASS_D_TOP / 2


def glass(yc, zb, **kw):
    pts = [px(yc - rb, zb), px(yc + rb, zb), px(yc + rt, zb + P.GLASS_H), px(yc - rt, zb + P.GLASS_H)]
    s.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", **kw)


glass(gy, gz0, stroke=INK, sw=1.4, fill="#eef6ff")
lx0, ly = px(gy - rb - 1, gz0 + 0.55 * P.GLASS_H)
lx1, _ = px(gy + rb + 4, gz0 + 0.55 * P.GLASS_H)
s.path(f"M{lx0:.1f},{ly:.1f} L{lx1:.1f},{ly:.1f}", stroke=BLUE, sw=1, dash="3,2")
y_out = gy + P.GLASS_SLIDE
z_lift = P.Z_SPHERE_CENTER - 52.5 + P.FLOOR + 2.0 + 1.0       # base just over the flange
glass(y_out, z_lift, stroke="#90a4ae", sw=1.2, fill="none", dash="4,3")

# ------------------------------------------------------------------ the hand
fe, fa = M["fist_envelope"].bounds, M["hand_path_envelope"].bounds
(fx0, fz1), (fx1, fz0) = px(fe[0][1], fe[1][2]), px(fe[1][1], fe[0][2])
(ax0, az1), (ax1, az0) = px(fa[0][1] + 10, fa[1][2] - 14), px(fa[1][1] + 25, fa[0][2] + 14)
s.rect(ax0, az1, ax1 - ax0, az0 - az1, rx=14, fill=SKIN, stroke=SKIN_EDGE, sw=1.2)
s.rect(fx0, fz1, fx1 - fx0, fz0 - fz1, rx=22, fill=SKIN, stroke=SKIN_EDGE, sw=1.2)
# ring on the finger, face on the socket
rx_, rz_ = px(-13.8 + 6, P.Z_SPHERE_CENTER + P.SOCKET_Z_LOCAL)
s.circle(rx_, rz_, 9, fill="none", stroke="#2e7d32", sw=4)

yc = BL.R_LIP_S - BL.CURTAIN_T / 2                        # the one-piece cover at the rear bell's mouth (flaps part for the arm)
for z0, z1 in ((BL.R_LIP_R, P.CURTAIN_SLIT_R), (-P.CURTAIN_SLIT_R, -BL.R_LIP_R)):
    s.path("M{:.1f},{:.1f} L{:.1f},{:.1f}".format(*px(yc, Zc0 + z0), *px(yc, Zc0 + z1)), stroke="#64b5f6", sw=2.2, opacity=0.9)
for sg in (1, -1):
    s.path("M{:.1f},{:.1f} L{:.1f},{:.1f}".format(*px(yc, Zc0 + sg * P.CURTAIN_SLIT_R), *px(yc - 30, Zc0 + sg * 40)),
           stroke="#64b5f6", sw=2.2, dash="4,2", opacity=0.9)

# ------------------------------------------------------------------ tube (blue) and cables (purple)
bag, pump = M["bag_envelope"].bounds, M["pump_envelope"].bounds
tip_z = Zc0 + SP.NOZZLE_TIP_Z
wy, wz = BS.WELL_XY[1], BS.FLOOR_T + 2.0                  # the tube's tip in the bag, clipped at the well
ny = BS.TUBE_NOTCH_Y                                      # over the splash wall's notch to the pump's inlet
tube = [(wy, wz), (wy + 4, 40.0), (ny, BS.SPLASH_H + 4), (20.0, 110.0), (SP.GROMMET_XY[1], Zc0 + SP.BAY_FLOOR_Z),
        (P.NOZZLE_TIP_XY[1], tip_z)]
s.wire([px(*p) for p in tube], BLUE, sw=2.4)
for a, b in ((0, 1), (3, 4), (4, 5)):
    (xa, ya), (xb, yb) = px(*tube[a]), px(*tube[b])
    s.arrow([(xa + 0.35 * (xb - xa), ya + 0.35 * (yb - ya)), (xa + 0.6 * (xb - xa), ya + 0.6 * (yb - ya))], BLUE, sw=2.4)
tx, tz = px(P.NOZZLE_TIP_XY[1], tip_z)
s.arrow([(tx, tz + 6), (tx, tz + 18)], BLUE, sw=1.6)          # the stream falls into the glass
cable = [(SP.WALL_BACK_Y - 1.0, Zc0 + P.SOCKET_Z_LOCAL), (SP.WALL_BACK_Y - 2.0, Zc0 + 70.0), (P.CAP_WIRE_HOLE_XY[1], P.Z_SPHERE_TOP + 20),
         (P.CAP_WIRE_HOLE_XY[1], TP.Z_CAP_FLOOR + 8)]
s.wire([px(*p) for p in cable], PURPLE, sw=1.5, dash="5,3")
pump_lead = [(-75.0, 52.0), (-50.0, 110.0), (-35.0, Zc0 - 60), (SP.WIRE_SLOT_XY[1], Zc0 + SP.BAY_FLOOR_Z), (SP.WALL_BACK_Y - 3.0, Zc0 - 30)]
s.wire([px(*p) for p in pump_lead], PURPLE, sw=1.5, dash="5,3")

# ------------------------------------------------------------------ the glass's way out
(gx_, gyp) = px(gy, gz0 + P.GLASS_H + 4)
(ox_, _) = px(y_out, gz0 + P.GLASS_H + 4)
s.arrow([(gx_ + 4, gyp), (ox_ - 4, gyp)], "#455a64", sw=1.6)
(lx_, ltop) = px(y_out + 2, z_lift + P.GLASS_H + 6)
s.arrow([(lx_, gyp - 4), (lx_, ltop)], "#455a64", sw=1.6)
(px_, _) = px(170, 0)
s.arrow([(lx_ + 6, ltop + 4), (px_, ltop + 4)], "#455a64", sw=1.6)

# ------------------------------------------------------------------ labels
def label(x, y, rows, tx, ty, anchor="start", size=11):
    s.lines(x, y, rows, size=size, anchor=anchor, color=INK, lh=13)
    ax = x - 6 if anchor == "start" else x + 6
    s.path(f"M{ax},{y - 4} L{tx:.1f},{ty:.1f}", stroke=GREY, sw=1)
    s.dot(tx, ty, GREY, r=2.2)


Zc = P.Z_SPHERE_CENTER
LX, RX = 300, 820
label(LX, 95, ["emblem lid on a white halo ring; 2 LED", "strips on the cap wall light it"], *px(-TP.R_CAP_IN + 1, TP.CAP_LED_Z[1]), anchor="end")
label(LX, 150, ["cap floor: battery, board, buck,", "power switch, charge socket (lid off)"], *px(-30, TP.Z_CAP_FLOOR + 10), anchor="end")
label(LX, 215, ["front bell: LED ring behind the", "frosted lens (audience side)"], *px(-BL.F_LEDGE_S, Zc + 40), anchor="end")
label(LX, 285, ["white LED panel: 4 rows on its front,", "hides the spout and the glass"], *px(yp, Zc + 30), anchor="end")
label(LX, 355, ["lock wall: the lock on its face,", "the spout hidden behind it"], *px(SP.WALL_BACK_Y, Zc + 45), anchor="end")
label(LX, 425, ["spout behind the wall: the tube", "pours into the back third of the glass"], *px(P.NOZZLE_TIP_XY[1], tip_z), anchor="end")
label(LX, 495, ["glass slot: push the glass back", "to the stop (a ridge clicks it in)"], *px(-30, gz0 + 4), anchor="end")
label(LX, 570, ["foot: the slot hangs in its neck;", "tube and pump wires pass up"], *px(-50, 150), anchor="end")
label(LX, 650, ["pump wires: one plug, up to the cap"], *px(-75, 52), anchor="end")
label(LX, 730, ["Kamoer KPHM200 pump (behind", "the section), head toward your side"], *px(pump[0][1] + 10, 40), anchor="end")

label(RX, 150, ["lock, LED and pump leads run up", "behind the wall to plugs at the cap floor"], *px(P.CAP_WIRE_HOLE_XY[1], P.Z_SPHERE_TOP + 20))
label(RX, 230, ["one-piece frosted cover: 8 flaps", "fold round your arm, spring shut"], *px(yc, Zc + 70))
label(RX, 300, ["your fist, punched in; the ring", "face sits in the lock; LED ring", "in the hand bell"], *px(40, Zc + 20))
label(RX, 390, ["to take the glass: grip its front,", "1  slide it toward you %d mm" % P.GLASS_SLIDE, "2  lift it clear of the slot",
                "3  bring it out through the cover"], *px(y_out + 26, z_lift + P.GLASS_H - 4))
label(RX, 500, ["glass rim 3 mm under the lock"], *px(gy + rt - 2, gz0 + P.GLASS_H))
label(RX, 640, ["32 oz drink bag under its cover; tube", "tip clipped in the well, then through", "the pump (behind the section) and up"], *px(wy, wz + 4))
label(RX, 730, ["cartridge: twist the lantern and", "lift it off to refill"], *px(80, 6))

# legend
lx, ly = 560, 890
s.wire([(lx, ly - 4), (lx + 28, ly - 4)], BLUE, sw=2.4)
s.text(lx + 34, ly, "drink", size=11)
s.path(f"M{lx + 90},{ly - 4} L{lx + 118},{ly - 4}", stroke=PURPLE, sw=1.5, dash="5,3")
s.text(lx + 124, ly, "cables", size=11)
s.rect(lx + 185, ly - 11, 18, 12, fill=PRINT, stroke=PRINT_EDGE, sw=0.9)
s.text(lx + 209, ly, "printed, cut", size=11)
s.rect(lx + 290, ly - 11, 18, 12, fill="#e0e0e0", stroke="#757575", sw=1, dash="4,3")
s.text(lx + 314, ly, "behind the cut", size=11)
s.path("M40,890 L115,890 M40,885 L40,895 M115,885 L115,895", stroke=INK, sw=1.5)
s.text(77, 880, "50 mm", size=10, anchor="middle")

open(os.path.join(HERE, "..", "fluid-path.svg"), "w").write(s.finish())
print("written")
