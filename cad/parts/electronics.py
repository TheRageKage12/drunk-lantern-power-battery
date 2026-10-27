"""Non-printing electronics envelopes for the circuit-review board layout.

Coordinates are deliberately conservative rectangular allowances, not detailed component
models. Unpublished dimensions must fit these limits before printing/soldering. See
cad/README.md. Board positions follow docs/review/protoboard/{layout,generate}.py.
All solids here are already in the assembly frame; none are printable parts.

Rev C (2026-10-23): the board, battery, buck module, power switch and charge socket live in the top cap, on the cap
floor plate (parts/top.py). The board lies flat, component face up, on the existing 10 mm posts plus two M3 nuts (4.8 mm) per post.
"""
from pathlib import Path

import cadquery as cq
import params as P
from parts import top as T, base as B

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'docs/review/protoboard'))
import layout as L
import mechanical as M

Z_FLOOR = T.Z_CAP_FLOOR                              # the cap floor plate's top, assembly z
BOARD_BACK = Z_FLOOR + T.BOARD_STANDOFF + M.BOARD_SPACER
BOARD_FACE = BOARD_BACK + P.PERFBOARD_T


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))


def compound(items):
    solids = [solid for item in items for solid in item.solids().vals()]
    # Merge touching/overlapping allowances; preserve disjoint components as a compound.
    return cq.Workplane('XY').newObject([solids[0].fuse(*solids[1:]).clean()])


def board_box(left, top, width, height, depth0, depth1):
    """Component-side drawing mm, top-left origin; depth is outward from the board face (up)."""
    (xa, ya), (xb, yb) = T.board_point(left, top), T.board_point(left+width, top+height)
    return box(min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), BOARD_FACE+depth0, BOARD_FACE+depth1)


def board_place(wp):
    return wp   # board_box already places the board in the cap (kept so tests read as before)


def cap(wp):
    """Cap-floor frame (z = 0 the plate's top) -> assembly."""
    return wp.translate((0, 0, Z_FLOOR))


def pack(wp):
    """Pack frame (z = 0 the plate's top) -> assembly."""
    return cap(T.pack_to_cap(wp))


def board_assembly():
    """Reserved assembly volume; internal spacing is checked by routing/mechanical.

    The broad front reserve includes 7.1 mm above the nominal wire loops. Rear
    volumes follow the parts/lead paths so they do not fill the printed posts.
    """
    import numpy as np
    hardware = L.DESIGN['hardware']
    outline = [T.board_point(x, y) for x, y in hardware['front_outline']]
    front = cq.Workplane('XY').polyline(outline).close().extrude(hardware['front_reserve'])
    items = [front.translate((0, 0, BOARD_FACE)),
             board_box(0, 0, 70, 50, -3.7, 0),
             board_box(4, -18, 62, 14, -12.2, 10)]
    items += [board_box(*v) for n, v in M.bounds().items() if v[5] < 0 or n == 'C2']
    # Reserve the whole lead face: the supplier does not publish C2's lead pitch.
    items.append(board_box(27, 80.5, 10, 20, 10, 30))
    for path in L.DESIGN['leads'].values():
        p = np.array(path)
        for i in range(0, len(p)-1, 8):
            c = p[i:i+9]
            lo, hi = c.min(0)-.4, c.max(0)+.4
            items.append(board_box(lo[0], lo[1], hi[0]-lo[0], hi[1]-lo[1], -1.2-hi[2], -1.2-lo[2]))
    # The first 35 mm is located by the board joint/template. Free runs reserve
    # Ø4 mm around Ø1.8 mm wire, allowing 1.1 mm of forming variation per side.
    for w in L.DESIGN['pigtails']:
        p = np.array(w['path'])
        for i in range(0, len(p)-1, 4):
            c = p[i:i+5]
            travel = np.linalg.norm(np.diff(p[:i+5], axis=0), axis=1).sum()
            radius = 2.0 if travel > 35 else 1.3
            lo, hi = c.min(0)-radius, c.max(0)+radius
            items.append(board_box(lo[0], lo[1], hi[0]-lo[0], hi[1]-lo[1], -1.2-hi[2], -1.2-lo[2]))
    items += [cq.Workplane('XY').workplane(offset=Z_FLOOR+T.BOARD_STANDOFF).center(*T.board_point(x,y)).circle(L.DESIGN['hardware']['spacer_od_max']/2).circle(1.6).extrude(M.BOARD_SPACER) for x,y in L.MOUNTS]
    xslot=T.HW+T.STOP_GAP+T.STOP_T+1+T.STRAP_SLOT_W/2
    y0,y1=P.BATTERY_STRAP_Y-10,P.BATTERY_STRAP_Y+10;top=P.PACK_BED_T+P.POWERBANK_T
    items += [pack(box(-xslot,xslot,y0,y1,-T.CAP_FLOOR_T,-T.CAP_FLOOR_T+2)),pack(box(-xslot,xslot,y0,y1,top,top+20))]
    items += [pack(box(s*xslot-1,s*xslot+1,y0,y1,-T.CAP_FLOOR_T,top+1)) for s in (-1,1)]
    return compound(items)


def build():
    M.validate()
    t_mid = P.PACK_BED_T + P.POWERBANK_T / 2
    end = -P.POWERBANK_L / 2
    out = {
        'board_assembly_envelope': board_assembly(),
        'powerbank_envelope': pack(box(-P.POWERBANK_W/2, P.POWERBANK_W/2, -P.POWERBANK_L/2, P.POWERBANK_L/2,
                                       P.PACK_BED_T, P.PACK_BED_T+P.POWERBANK_T)),
        # The splitter's straight male plug in the pack's port, its cord folded back in a U-turn that reaches
        # BATTERY_PLUG_TURN from the battery's end, then up over the pack.
        'battery_connector_envelope': pack(compound([
            cq.Workplane('XZ').workplane(offset=-end).center(P.PACK_PORT_X, t_mid)
              .circle(P.BATTERY_PLUG_D/2).extrude(P.BATTERY_PLUG_OUT),
            box(P.PACK_PORT_X-4, P.PACK_PORT_X+4, end-P.BATTERY_PLUG_TURN, end-P.BATTERY_PLUG_OUT+1,
                t_mid-4, t_mid+P.BATTERY_PLUG_D/2+5),
            box(P.PACK_PORT_X-3, P.PACK_PORT_X+3, end-P.BATTERY_PLUG_TURN, end,
                t_mid+P.BATTERY_PLUG_D/2, P.PACK_BED_T+P.POWERBANK_T+8)])),
    }
    bx, by = P.BUCK_CAP_XY
    lx, ly = T.BUCK_DIMS
    out['buck_envelope'] = cap(box(bx-lx/2, bx+lx/2, by-ly/2, by+ly/2, P.BUCK_STANDOFF, P.BUCK_STANDOFF+P.BUCK_H))
    out['buck_wires_envelope'] = cap(compound([      # leads off both short ends
        box(bx+sign*lx/2-(10 if sign < 0 else 0), bx+sign*lx/2+(10 if sign > 0 else 0), by-9, by+9, 6, 18)
        for sign in (-1, 1)]))
    # The lock cable's plug and the coiled slack of the soldered LED and pump leads, over the hole they come up through.
    out['inline_connectors_envelope'] = cap(box(-58, -36, -66, -46, 0.2, 16))
    sx, sy = P.SWITCH_CAP_XY
    roof = T.SWITCH_BOX[2]
    body = box(sx-6.5, sx+6.5, sy-4.5, sy+4.5, roof-P.WALL-18, roof-P.WALL)     # hangs from the roof inside the box
    bush = cq.Workplane('XY').workplane(offset=roof-P.WALL).center(sx, sy).circle(3.1).extrude(P.WALL+18)
    nut = cq.Workplane('XY').workplane(offset=roof).center(sx, sy).circle(5.5).extrude(3)
    out['power_switch_envelope'] = cap(body.union(bush).union(nut))
    cx, cy = P.CHARGE_SOCKET_XY
    out['charge_socket_envelope'] = cap(cq.Workplane('YZ').workplane(offset=cx-15).center(cy, 6.2).circle(6).extrude(30))
    # D2 is across the motor terminals, beyond the motor's -Y end; includes insulation/leads.
    yend = B.PUMP_HEAD_FACE_Y-P.PUMP_L
    out['pump_diode_envelope'] = box(B.PUMP_X-8, B.PUMP_X+8, yend-6, yend-1,
                                    B.PUMP_AXIS_Z-4, B.PUMP_AXIS_Z+4)
    # The pump's 2-pin plug, unplugged when the lantern is lifted off the cartridge.
    out['pump_plug_envelope'] = box(6, 26, -80, -70, 42, 62)
    # C4 and insulated joints behind the fixed lock wall, centred on its existing Hall window.
    z = P.Z_SPHERE_CENTER+P.SOCKET_Z_LOCAL
    y = P.LOCK_FACE_Y-P.SOCKET_MODULE_DEPTH-P.LOCK_WALL_T
    out['hall_capacitor_envelope'] = box(-4, 4, y-6.5, y-.5, z-4, z+4)
    return out


def placements():
    return {}  # already in assembly coordinates
