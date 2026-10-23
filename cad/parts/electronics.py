"""Non-printing electronics envelopes for the circuit-review board layout.

Coordinates are deliberately conservative rectangular allowances, not detailed component
models. Unpublished dimensions must fit these limits before printing/soldering. See
cad/README.md. Board positions follow docs/review/protoboard/{layout,generate}.py.
All solids here are already in the assembly frame; none are printable parts.
"""
from pathlib import Path

import cadquery as cq
import params as P
from parts import base as B

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'docs/review/protoboard'))
import layout as L
import mechanical as M

BOARD_BACK = B.EPANEL_R + B.EPANEL_T / 2 + B.EPANEL_PAD_PROUD
BOARD_FACE = BOARD_BACK + P.PERFBOARD_T
BOARD_TOP = B.DECK_TOP + P.PERFBOARD_BOTTOM_GAP + P.PERFBOARD_H


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))


def compound(items):
    solids = [solid for item in items for solid in item.solids().vals()]
    # Merge touching/overlapping allowances; preserve disjoint components as a compound.
    return cq.Workplane('XY').newObject([solids[0].fuse(*solids[1:]).clean()])


def board_box(left, top, width, height, depth0, depth1):
    """Component-side drawing mm, top-left origin; depth is outward from board face."""
    return box(BOARD_FACE+depth0, BOARD_FACE+depth1,
               left-P.PERFBOARD_W/2, left+width-P.PERFBOARD_W/2,
               BOARD_TOP-top-height, BOARD_TOP-top)


def board_place(wp):
    return wp.rotate((0, 0, 0), (0, 0, 1), B.EPANEL_ANGLE)


def build():
    pcb = board_box(0, 0, P.PERFBOARD_W, P.PERFBOARD_H, -P.PERFBOARD_T, 0)
    # Space for wires behind the board; the screw pads are intentionally excluded.
    rear = board_box(0, 0, P.PERFBOARD_W, P.PERFBOARD_H,
                     -P.PERFBOARD_T-B.EPANEL_PAD_PROUD+0.2, -P.PERFBOARD_T-0.2)
    for x, y in L.MOUNTS:
        cutter = cq.Workplane(cq.Plane(origin=(BOARD_BACK-1, x-P.PERFBOARD_W/2, BOARD_TOP-y),
                                     normal=(1, 0, 0))).circle(1.6).extrude(P.PERFBOARD_T+2)
        pcb = pcb.cut(cutter)
        rear = rear.cut(board_box(x-4.6, y-4.6, 9.2, 9.2, -P.PERFBOARD_T-B.EPANEL_PAD_PROUD-1, 1))
    bodies = M.bounds()
    M.validate(bodies)
    components = [board_box(*bounds) for bounds in bodies.values()]
    out = {
        'perfboard_envelope': board_place(pcb),
        'board_components_envelope': board_place(compound(components)),
        'board_wiring_envelope': board_place(rear),
        # Local cable exit above the board, behind the component face; tie to the panel.
        'board_cable_exit_envelope': board_place(board_box(25, -7, 42, 7, -P.PERFBOARD_T-9.2, -P.PERFBOARD_T-.2)),
        # The splitter's straight male plug in the pack port (pack LED face down, port at PACK_PORT_X), its cord folded
        # back in a U-turn that reaches BATTERY_PLUG_TURN from the battery's end, then up toward the deck.
        'battery_connector_envelope': compound([
            cq.Workplane('XZ').workplane(offset=P.POWERBANK_L/2-P.PACK_Y).center(P.PACK_PORT_X, P.PACK_Z+P.POWERBANK_T/2)
              .circle(P.BATTERY_PLUG_D/2).extrude(P.BATTERY_PLUG_OUT),
            box(P.PACK_PORT_X-4, P.PACK_PORT_X+4, P.PACK_Y-P.POWERBANK_L/2-P.BATTERY_PLUG_TURN, P.PACK_Y-P.POWERBANK_L/2-P.BATTERY_PLUG_OUT+1,
                P.PACK_Z+P.POWERBANK_T/2-4, P.PACK_Z+P.POWERBANK_T/2+P.BATTERY_PLUG_D/2+5),
            box(P.PACK_PORT_X-3, P.PACK_PORT_X+3, P.PACK_Y-P.POWERBANK_L/2-P.BATTERY_PLUG_TURN, P.PACK_Y-P.POWERBANK_L/2,
                P.PACK_Z+P.POWERBANK_T/2+P.BATTERY_PLUG_D/2, P.BATTERY_PLUG_Z1)]),
    }
    bx, by = B.BOOST_XY
    out['buck_envelope'] = box(bx-P.BUCK_W/2, bx+P.BUCK_W/2,
                               by-P.BUCK_L/2, by+P.BUCK_L/2, P.FLOOR+P.BUCK_STANDOFF, P.FLOOR+P.BUCK_STANDOFF+P.BUCK_H)
    out['buck_wires_envelope'] = compound([
        box(bx-9, bx+9, by+sign*P.BUCK_L/2-(10 if sign<0 else 0),
            by+sign*P.BUCK_L/2+(10 if sign>0 else 0), 8, 20) for sign in (-1, 1)])
    # Inline lock/LED plugs plus short wire bends above the unused module pocket.
    out['inline_connectors_envelope'] = box(47, 67, -32, 32, 10, 26)
    sx, sy = P.SWITCH_POCKET_XY
    ceiling = P.SWITCH_POCKET_DEPTH+P.WALL
    stem = cq.Workplane('XY').workplane(offset=7).center(sx, sy).circle(3.1).extrude(ceiling-7)
    nut = cq.Workplane('XY').workplane(offset=17).center(sx, sy).circle(5.5).extrude(3)
    out['power_switch_envelope'] = stem.union(nut).union(box(sx-6.5, sx+6.5, sy-4.5, sy+4.5, ceiling, ceiling+18))
    jx, jy = P.JACK_XY
    # Optional charge jack (not fitted since 2026-10-20; the splitter's female end is the charge socket). This reserve
    # keeps the deck hole usable for a later jack: body/terminals below deck, bushing in hole, nut above.
    jack = box(jx-6.5, jx+6.5, jy-6.5, jy+6.5, B.DECK_Z0-20, B.DECK_Z0)   # 321B body 12.4 mm wide
    jack = jack.union(cq.Workplane('XY').workplane(offset=B.DECK_Z0).center(jx, jy).circle(P.PORT_JACK_D/2-0.1).extrude(B.DECK_T))
    jack = jack.union(cq.Workplane('XY').workplane(offset=B.DECK_TOP).center(jx, jy).circle(8.5).extrude(3))   # 7/16" nut across corners
    out['charge_jack_envelope'] = jack
    # The optional jack's charger plug, attached only with the lantern lifted off. Cable exits upward.
    plug = cq.Workplane('XY').workplane(offset=B.DECK_TOP+3).center(jx, jy).circle(6).extrude(30)
    out['charge_plug_envelope'] = plug.union(box(jx-4, jx+4, jy-4, jy+4, B.DECK_TOP+33, B.DECK_TOP+43))
    # D2 is across the motor terminals, beyond the motor's -Y end; includes insulation/leads.
    yend = B.PUMP_HEAD_FACE_Y-P.PUMP_L
    out['pump_diode_envelope'] = box(B.PUMP_X-10, B.PUMP_X+10, yend-11, yend-1,
                                    B.PUMP_AXIS_Z-4, B.PUMP_AXIS_Z+4)
    # C4 and insulated joints behind the fixed lock wall, centred on its existing Hall window.
    z = P.Z_SPHERE_CENTER+P.SOCKET_Z_LOCAL
    y = P.LOCK_FACE_Y-P.SOCKET_MODULE_DEPTH-P.LOCK_WALL_T
    out['hall_capacitor_envelope'] = box(-4, 4, y-6.5, y-.5, z-4, z+4)
    return out


def placements():
    return {}  # already in assembly coordinates
