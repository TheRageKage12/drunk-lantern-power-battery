# NOTES-base: base drum, rear door, hardware deck

Module `cad/parts/base.py`. Parts: `base`, `base_door`, `base_deck` (printed) and the envelopes
`bottle_envelope`, `pump_envelope`, `powerbank_envelope` (clearance checks only, not printed).
Built against `params.py` / `DESIGN_CONTRACT.md` **revision 2** (KPHM200 pump, Anker 313 bank, 60 mm bottle).

## Mating constants (import from `parts.base`)
| constant | value | who uses it |
|---|---|---|
| `BASE_TOP_INNER_D` | 169.2 (= BASE_BODY_D - 2*WALL; one straight bore floor to top) | dish_lower spigot OD = this - 2*FIT = 168.6 |
| `BASE_JOINT_Z` | 95.0 (= BASE_H - 5) | dish_lower spigot insert bosses |
| `BASE_JOINT_ANGLES` | (90, 210, 330) deg, first at +Y | same |
| `BASE_JOINT_CBORE_DEPTH` | 3.0, M3_HEAD_D from the outside, through M3_CLEAR | - |
| `SPIGOT_ZONE_Z0` | 92: nothing in the base rises above this inside r < R_IN | deck / pump height budget |
| `DECK_Z0`, `DECK_TOP` | 23 / 26: deck underside / top face (assembly Z) | bottle + pump stand on DECK_TOP |
| `BOTTLE_X, BOTTLE_Y` | (-39.5, 0) bottle axis | bay_floor / dish: bottle top at Z 162 |
| `PUMP_X`, `PUMP_HEAD_FACE_Y`, `PUMP_AXIS_Z` | 28 / 52 / 57.5: pump axis along Y, head face toward the door | tube routing |
| `EPANEL_*` | XIAO perfboard panel on the deck, rear-left, normal at 115 deg, r = 56 | wiring |

The band wall at the three joint holes is 5.4 mm (R_MAX - R_IN): the 3 mm counterbore leaves exactly WALL.

## Why the layout looks like this (ASCII, assembly frame, +Y = rear/door at the top)

```
                       +Y (REAR, door 110 wide, z 12..88)
          ............ [door] ............. [tab]
    [tab]  .   XIAO panel (vertical,       .
           .   face -> wall, r=56 @115deg) .     pump HEAD box 64x40x63
           .                      ____________________   y 12..52, x -4..60
           .      bottle ring    |  U-saddle y 14..22  |  tube ports face +Y
           .      ID 61 @        |____________________|
   boost   .     (-39.5, 0)        | strap slots |       D4184 on the floor
   module  .     3 fingers         |   motor can |       x 46.5..65.5, y -18..18
   on the  .     0/120/240 deg     |   r 20, y   |       (under the deck, right crescent)
   floor   .                       |  -66 .. 12  |
   (left   .                       | round saddle|
   crescent)                       |  y -58..-50 |
           .                       '-------------'
           .  POWER BANK flat on the floor, 71 (X) x 153 (Y) x 17, centred, under the deck
           .  ports at +Y end (z ~10.5) -> sill notch + door notch
          drains (+-40, -68)
                       -Y (FRONT)
   Deck: disc OD 168.6, 3 thick, z 23..26, on 6 pillars 9x9 at (+-41, -55/0/55); 3 M3 inserts
   (41,0) (-41,0) (41,55) so it only goes in one way.  Pump top z 89, bottle top z 162.
```

Key numbers (all derived in the module): inner bore r = 84.6. Bank corners sit at r = 84.3 when it is
centred, so a 153 x 71 slab is pinned to the centre of the floor in any orientation - nothing else fits
beside it at floor level. Hence the **deck**: a second floor that drops in from the open top and carries
everything tall. The right/left crescents beside the bank (|x| > 36.5, under the deck) hold the D4184 and
the 5->12 V boost module, which do not need regular access.

Pump: KPHM200 as a stepped envelope (head box 64 x 63 x 40, motor can dia 40, 118 overall). With the
bottle ring at -X the pump axis can be no further left than x = 28 (ring OD to head box gap 2 mm); at
x = 28 the head corner (60, 52) is at r 79.4 (1.2 mm inside the door tabs) and the motor end corner
(48, -66) at r 81.6 (3 mm from the wall). The pump top (z 89) stays under the dish spigot zone (z 92).
Head toward +Y so the tube can be loaded through the door without removing the pump.

Bottle: on the deck at (-39.5, 0). Against the dish_lower cone (inner radius ~ 87.4 - 0.4545*(z-100)):
body top (z 126) margin 6.1 mm, cap top (z 162) margin 2.7 mm. The envelope is stepped (body 60 x 100,
14 mm shoulder cone to 34, neck/cap 34 to 136) because a 60 x 136 cylinder cannot clear the cone at any
reachable offset; an 8 oz Boston round's straight body ends well below 100 mm.

Electronics: a 50 x 40 flat plinth does not fit anywhere reachable (checked numerically), so the XIAO
perfboard mounts on a **vertical panel** on the deck, rear-left, 4 M3 insert pads on a 40 x 30 grid, board
face toward the rear-left wall, i.e. visible and reachable through the door; USB port of the XIAO faces the door.
The D4184 pocket outline (36 x 19) has two edge-clamp insert bosses at its short ends (M3 + washer over the PCB edge;
the module's own hole positions are unverified). The boost module outline has two cable-tie anchors.

## Door
- Opening per contract (110 x 76, bottom edge 10 above the floor, z 12..88). Door = curved outer plate
  (2 mm, proud of the body, lip 4 mm on left/right/bottom) + plug (WALL thick, flush inside, FIT per side).
- **Top lip omitted** (deviation): the top band starts exactly at z 88, so there is no body surface above
  the opening for a lip to sit on; the plug top ends FIT under the band's underside and the 3 mm band step
  shadows the joint. The bottom band and the 45 deg step are recessed to R_BODY under the lip footprint
  (leaves WALL = 2.4 there).
- 4 corner **stop tabs** inside the wall (4 thick) with magnet pockets opening outward; the plug has the
  matching pockets opening inward (magnet-to-magnet contact). Magnets at (+-47, 18) and (+-47, 80).
  Tabs stop at z 22.5 (under the deck) and z 91 (under the dish spigot).
- 12.5 mm switch hole at (-30, 72) (only the electronics panel is behind it). USB: a 14 x 6 notch in the base
  sill (z 6..12) plus a 14 x 7 notch in the door's bottom edge: together they pass a USB-C plug straight into
  the bank's port (port centre z ~10.5) with the door closed, and the plug is inserted through the same
  slot with the door open. 14 mm instead of 10 because a USB-C plug body is ~12 x 6.5.
- Print **standing on its bottom (lip) edge**; the plug has a 1.6 mm 45 deg chamfer underneath so the
  2.4 mm step prints without support. Use a brim.

## Other floor features
- Bank: side guidance by the pillars (36.5 from the centre, bank half width 35.5), end stops 12 tall
  (the +Y stop is two blocks leaving the middle 24 mm free for the plug), 2 strap slot pairs 22 x 3 at y = +-31.
- Pump: 2 straps through 4 deck slots (head pair y 28..50, motor pair y -50..-28), the strap runs under the
  deck (4 mm gap over the bank). Bottle: 3 fingers 12 x 28 with 22 x 3 slots.
- 4 cable-tie anchors (pairs of 4.5 x 2 slots) at r 79, 50/130/230/310 deg; 2 drain holes 8 mm at
  (+-40, -68) under the front of the deck; deck wire slots 14 x 8 at (28, -70) (pump leads) and (-25, 70)
  (XIAO/bank leads) plus a 30 x 10 notch in the deck edge at +Y to see the bank's ports.

## Print orientation / placements
- `base`: floor on the bed, identity. 45 deg step under the top band, no supports. ~211 cm3.
- `base_door`: standing on the lip edge; placement = translate only. ~41 cm3.
- `base_deck`: flat, features up; placement = translate (0, 0, 23). Pads on the electronics panel have 45 deg
  undersides. ~93 cm3.
- Envelopes: built on z = 0 at their XY, placed by translation (bank on FLOOR, bottle + pump on DECK_TOP).

## Assembly order
1. Lay the bank in, ports toward the door, strap it (2 straps). Boost module and D4184 into their outlines.
2. Drop the deck in (notch toward the door), 3 x M3 into the pillar inserts.
3. Pump into the saddles (head toward the door), 2 straps. Bottle into the ring, strap.
4. XIAO perfboard onto the panel pads (4 x M3). Wires down through the deck slots.
5. Door: magnets into the tabs and the plug (check polarity), switch into the door, plug the charge cable
   through the sill slot when needed.

## Deviations from the computed task / contract rev 2 (and why)
- Tiers: the contract's silhouette (D_MAX bands + BASE_BODY_D body) is used; the original's narrowing steps
  cannot coexist with a 180 mm top band, WALL >= 2.4 and a door spanning the whole body height.
- Pump is on a separate deck rather than on saddles grown from the floor (a bridge over a 71 mm bank is not
  printable support-free); the deck is also what makes the bottle reachable.
- Electronics tray is a vertical panel on the deck (rear-left) instead of a 50 x 40 plinth "at +X front":
  the +X side is the pump; no 50 x 40 flat footprint fits anywhere accessible.
- Door lip on 3 sides, USB notch 14 x 7 (+ sill notch), see above.
- Bottle envelope is stepped; pump envelope is stepped (head box + motor can) as rev 2 describes the KPHM200.
- BASE_H stays 100 (everything fits under the spigot zone at 92).

## Known issues / to verify with the real parts
- `PUMP_HEAD_L_EST` = 40 and `PUMP_MOTOR_L` = 78: if the real head is longer than ~46 mm the motor saddle
  (y -58..-50) sits under the head - move `PUMP_MOTOR_SADDLE_Y` toward -Y (there is 8 mm of room).
- Bank ports must be at the +Y end, near the middle of the 71 mm edge (Anker 313: yes). The ports sit 12 mm
  below the door sill, reached through the sill + door notch; the deck edge notch gives a view of them.
- Cap-top to dish margin 2.7 mm assumes a 2.4 mm dish wall; if dish_lower adds internal ribs near z 160
  at r < 59, move the bottle 2 mm toward +X by lowering `BOTTLE_RING_GAP` (and check the pump gap).
- Door magnets: 8 magnets total (4 + 4); pockets are 6.3 x 2.2.
