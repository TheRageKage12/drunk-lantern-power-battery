# Prototype-board assembly

[Step-by-step guide](assembly.html) · [Full layout](index.html) · [Two-sided drawing](both-sides.png) · [PDF](board-assembly.pdf) · [Solder schedule](WIRE_SCHEDULE.md)

Use the existing **70 × 50 mm isolated-pad board** and the six colours of insulated stranded 22 AWG.
The components have moved; the printed enclosure and its four mounting holes have not.

1. Solder the front components with the board held by its edges.
2. Fit the insulated loops over that face. Each wire end goes through its **own empty hole**.
   On the back, its short stripped end bends to the indicated component joint. There are no bare buses or separate lead offcuts.
3. Fit the four indicated wire pairs together before soldering either wire. The guide handles this order.
4. Add C1/C3 and R3/R4 on the back, using their own component leads. Then add C2's two sleeved pigtails.
5. Secure C2 on the cap floor, insulate the three power-harness splices, and fit the board on its spacers.

The guide highlights one solder point at a time, retains completed work, and supplies cut lengths and 1:1 bend templates.
Use **Fit** to show the whole board; changing steps keeps your chosen view. A pad is the copper ring around a hole.
Hole names are assigned from the component face; the rear view is mirrored.

## Mounting and fit

Use four **20 mm unthreaded nylon spacers**, bore ≥3.2 mm and OD ≤6 mm, with **M3×25 screws** (heads ≤Ø6 mm).
The existing 10 mm posts give 30 mm under the solder face. Nominal screw engagement is 25 − 20 − 1.2 = **3.8 mm**;
check the screws clamp the board without bottoming out. Do not add washers that reduce that engagement.

The XIAO now faces USB toward column X; U1's notch also faces column X. Q1's printed face faces row 18;
Q2's printed face faces column A. D1's stripe goes to L05 and D3's stripe to S01. JP1 is R18/S18.
C2 positive remains F02, negative F04, now via pigtails. Leave JP1 open for USB and follow the build guide's power procedure.

| Check | Modeled allowance / physical acceptance |
|---|---|
| Wire | Nominal Ø1.7 mm; reserve Ø1.8 mm for the owner's [Electronix Express kit](https://www.elexp.com/products/27wk22str25wire-kit-22ga-str-6-25ft-spool), [B00B4ZQ3L0](https://www.amazon.com/dp/B00B4ZQ3L0). |
| Bends | 4 mm centreline radius in three dimensions. A roughly 6.5 mm round former produces that radius with this wire. This is a forming target, not a published minimum bend rating. |
| Front loops | Nominal top 32.9 mm. Allow **2 mm extra bow**; finished loops must stay ≤35 mm above the front face. The enclosure check reserves 40 mm, leaving 5 mm beyond that acceptance limit. |
| Rear soldering | Joint allowance Ø2 × 2.5 mm; trim component pins to ≤1.5 mm. Long wires stay on the other face, so they do not obstruct the iron. |
| Bare wire ends | The routed ends retain ≥0.52 mm from other Ø2 mm joints and ≥0.60 mm from unrelated ends. They are fixed at their hole and destination joint. Two ends have a small sideways bend shown in the drawing. |
| Insulated wires | Nominal minimum skin separation 0.57 mm, including curve approximation allowance. Jackets may touch as loops flex; the design does **not** depend on an air gap between insulated wires. Keep jackets intact and bare joints separate. |
| Components | Minimum body gap 1.09 mm. Front wires nominally clear bodies by ≥1.05 mm and exposed axial-component leads by ≥1.29 mm. |
| Mounting screws | Wire paths leave a Ø10 mm access corridor. Spacers have a 0.25 mm radial allowance in the rear checks; use insulating nylon spacers. |
| Small rear parts | Keep within 21 mm of the solder face, leaving at least 8.5 mm above the floor with 0.5 mm mounting variation. |
| C2 support | Case ≤Ø18 × 25 mm, lying along the row direction. A ≤25.4 × 25.4 × 5 mm tie base sits on the existing floor, centred below board coordinate **(36.5,16)**. Its case, tie and base fit within the 30 mm space. Leave the vent clear. |

**Physical fit is still required.** The capacitors are not available to measure yet, and their listings omit case dimensions.
Check all limits before soldering. Use a tip no wider than 2 mm; the rear resistors need an angled approach toward row 18. Dry-fit the raised board and retained capacitor; close the enclosure without pressing
on wires. A failed fit means reforming the loops or revising the layout, not tightening screws to flatten it.

C2 must be retained independently of its leads. One option is a [Vetco 1-inch cable-tie base](https://vetco.net/products/sr-wm-abb_cable_tie_mount_-_1_x_1_adhesive_backed_qty_100)
(25.4 mm square; **check delivered height ≤5 mm**). It is sold as 100 for $14.95, checked 27 October 2026; only one is needed.
An existing base within the same size limit is suitable. Clean the floor and follow the adhesive's cure/application instructions;
pull-test the mount before attaching the board. Position the tie around the case, away from its vent and lead seal.
The fit calculation does not establish adhesive strength. No print changes or new supplier are required.

## Wire preparation

Cut one wire at a time. Cut lengths use the curved 3-D path, through-board ends, rear tails and **6 mm trimming stock**.
That stock is trimmed off; it is not a slack loop left on the board. The rounded routes themselves provide the rise and room
for forming. Outgoing leads include the rounded turn outside the board; add the measured external run and service slack.
Keep the pump/LED service slack outside the board footprint.

Strip only the lengths shown for that wire (typically 6–12 mm at a board end). Gently twist the strands, insert them
**untinned**, and keep the insulation against the front face. Solder the wire's own hole first; form its short end along the
highlighted rear path, then solder the destination. Lightly tin the exposed end as part of this operation. No loose strands,
no solder bridges, and no forcing pre-tinned wire into the nominal 1 mm holes. Do not bend at a ceramic capacitor's coating.

For C2, trim and sleeve each pigtail joint separately. Leave enough capacitor lead for a 3–4 mm overlap, without bending at
the seal. Adjust the final insulated section to the delivered lead pitch, keeping the two sleeves separate. The body limit
and drawing are envelopes, not a claim that the supplier guarantees a particular lead pitch.

## Harness changes

Three insulated splices replace the crowded on-board power fan-out:

| Splice | Connections |
|---|---|
| J_LOAD · switched battery | S1 output, H01, buck IN+, pump +, LED + |
| J_GND · ground | Battery −, buck IN−, H02 logic return, H03 pump source, H04 LED source, lock ground |
| J_5V · regulated 5 V | Buck OUT+, H07, lock +5 V |

H05 goes to pump −, H06 to LED −, H08 to microswitch NO, and H09 to Hall OUT. Check continuity between the buck's IN− and
OUT− before omitting a separate OUT− lead. Pump and LED source returns remain independent until J_GND; they do not flow
through the logic-ground chain. D2 stays at the pump and C4 at the Hall sensor. Circuit values and GPIO connections are unchanged.

Make these splices on the bench, with sleeves already on the wires. Divide the five/six wires into two opposing bundles,
lightly pre-tin, overlap their stripped ends and solder. Cover all bare conductor and overlap the jackets with heat-shrink;
allow a finished splice diameter ≤5.5 mm. The existing 1/8-inch sleeve may not pass over these bundles: obtain **6 mm 3:1
heat-shrink** for the two larger splices. Retain the joins beside the board's top edge (row 01), below the cable turns, rather
than adding a lump beneath the board. The cable reserve is checked against the fixed enclosure; final external lead lengths
and service loops must be fitted to the device.

## Component size evidence

| Part | Source / assembly limit |
|---|---|
| Board | [Vetco VUPN2924](https://vetco.net/products/phenolic-protoboard-1-97-x-2-76-inch), 70 × 50 mm, 24 × 18 holes at 2.54 mm pitch. Confirm actual edge offsets before drilling. Existing mounting centres: (18,17), (55,15), (15,45), (58,45) mm. |
| XIAO | [Seeed](https://wiki.seeedstudio.com/XIAO-RP2040/), 21 × 17.8 mm and 15.24 mm header-row spacing. Reserve 21.5 × 18.3 × 12 mm including headers. |
| U1/socket | [TI PDIP-14](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf), 2.54 mm pitch and 7.62 mm rows. [Vetco socket](https://vetco.net/products/14-pin-ic-socket-2-54mm-spacing-0-1) outer size is unpublished: require ≤20.5 × 11 × 10.5 mm assembled. |
| Q1/Q2 | [Infineon TO-220](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44n-datasheet-en.pdf), section ≤10.54 × 4.69 mm. Reserve 10.8 × 4.9 mm and ≤22 mm mounted height. |
| Resistors | Body limit 6.8 × Ø2.7 mm. R3/R4 stand on the rear, connected with their own leads; other resistors lie on the front. |
| D1/D3 | Body limit 5.5 × Ø2.9 mm. [Vishay DO-41 reference](https://www.vishay.com/docs/88525/1n5817.pdf) is smaller; this is not a dimensional guarantee for NTE585. |
| C1/C3 | [Vetco disc](https://vetco.net/products/vupn6606_ceramic_capacitor_0-1_uf_-2080_50_volts_z5u): no mechanical drawing. Require ≤Ø10 × 4 mm and sufficient untrimmed leads to reach the indicated joints without bending at the coating. |
| C2 | [Vetco 2200 µF / 25 V](https://vetco.net/products/2200uf25vdc_2200uf_25_volt_electrolytic_capacitor): no case drawing. Require ≤Ø18 × 25 mm; fit pigtails to its actual lead spacing. |
| JP1 | Header and shunt ≤5.5 × 2.5 × 8 mm. |

## Checks and regeneration

`design.json` is the placement and route data. `mechanical.py` supplies shared size allowances; `routing.py` validates the
wire paths. `redesign/check.py` checks exact polyline separation with a curve allowance, 4 mm bend construction, connectivity,
separate wire holes the order of crossings, rear lead/spacer separation and access with a 2 mm iron tip widening to 5 mm over 12 mm. `cad/parts/electronics.py` checks the assembly reserve against the enclosure.
These are design checks, not measurements of an assembled board.

```sh
python3 assembly_guide.py
python3 generate.py --export
python3 -m pytest test_assembly.py -q
```

Python dependencies: NumPy, SciPy, Shapely, NetworkX, pytest, pypdf; PNG/PDF export also uses `rsvg-convert`.
Keep all power disconnected for continuity checks, then follow [EL-10 commissioning](../../BUILD_GUIDE.md#el-10-commission-the-board-without-loads).
The spreadsheet has not been edited. Hardware follow-up: four 20 mm nylon spacers, four M3×25 screws, one tie base and a short
length of suitable larger heat-shrink, replacing the previous 6 mm spacer/M3×12 proposal.
