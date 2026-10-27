# Prototype-board assembly

[Step-by-step guide](assembly.html) · [Full layout](index.html) · [Two-sided drawing](both-sides.png) · [PDF](board-assembly.pdf) · [Solder schedule](WIRE_SCHEDULE.md)

Use the existing **70 × 50 mm isolated-pad board** and the six colours of insulated stranded 22 AWG.
The components have moved; the printed enclosure and its four mounting holes have not.

1. Solder the front components with the board held by its edges.
2. Fit the insulated loops over that face. Each wire end goes through its **own empty hole**.
   On the back, its short stripped end bends to the indicated component joint. There are no bare buses or separate lead offcuts.
3. Fit the four indicated wire pairs together before soldering either wire. The guide handles this order.
4. Add R3, R4, C1, then C3 on the back, using their own component leads. Then add C2's two sleeved pigtails.
5. Secure C2 on the battery under its strap, insulate the power-harness splices, and mount the board on two M3 nuts per hole.

Each step completes one component, one wire, or a pair of wires that must be fitted together. All joints for that task are highlighted; completed work stays visible. Cut lengths and 1:1 bend templates are available when needed.
The socket and controller steps open a close-up with staggered hole labels and leader lines. Use **Fit** to show the whole board, or **Part close-up** to return. Changing steps keeps your chosen side of the board. A pad is the copper ring around a hole.
Each component step includes a shape illustration and its orientation. Names such as D1 are circuit labels; NTE585 is a part number.
**H04 means column H, row 4** in this guide. The blue guides locate the selected hole; click another marked hole to move them.
These labels may not be printed on the physical board. A01 is the upper-left grid hole on the component face; flip left-to-right
for soldering, keeping row 01 at the top. The rear view is mirrored, but every hole keeps its name.

## Mounting and fit

Use **eight existing M3 nuts and four M3×10 screws**: two nuts beneath each board hole, on the unchanged 10 mm printed posts.
The nominal lift is 4.8 mm, giving **14.8 mm below the solder face** and **4.0 mm thread engagement** (10 − 4.8 − 1.2).
Dry-fit before wiring. Keep the nuts aligned, seat all four corners evenly, and check that the board clamps without bottoming the screws.
Do not add washers. The checks include the nuts' conductive hex corners (5.5 mm across flats, plus placement allowance).

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
| Mounting screws | Wire paths leave a clear Ø8.2 mm access corridor; use screw heads ≤Ø6 mm. Metal nut corners include 0.25 mm radial allowance; solder joints clear that enlarged envelope by ≥0.62 mm. Do not leave stray strands in the mounting areas. |
| Small rear parts | Lay C1/C3 and R3/R4 flat. Rear parts, joints and wires must stay within **11 mm** of the solder face, leaving **≥3.3 mm** to the floor with 0.5 mm mounting variation. |
| C2 support | Case ≤Ø18 × 25 mm, lying on the battery along its length. Centre it under the existing strap, at board coordinate **(14.5,90.5)**. Reserve 2 mm for the strap. Keep the vent and lead seal uncovered. |

**Physical fit is still required.** The capacitors are not available to measure yet, and their listings omit case dimensions.
Check all limits before soldering. Use a tip no wider than 2 mm. The rear-part checks include the completed wire-anchor joints,
not just component terminals. Fit R3/R4 before C1, then C3, so later bodies do not block the iron. The guide supplies 1:1 lead templates; R4's longer lead needs at least **26 mm untrimmed**.
Dry-fit the complete assembly and close the lid without pressing on wires. Do not tighten screws to flatten a failed fit.

Cut **350 mm from the existing 19 mm ONE-WRAP roll**. Thread the battery slots first, fit the battery LED-face down, and
lay C2 on top along the pack's long direction. Centre the strap across its case; a 25 mm case leaves about 3 mm exposed
at each end. Leave ≥50 mm of strap overlap and trim excess only after fitting. Tighten enough to prevent C2 sliding or
rolling, without crushing its sleeve. Pull-test with power disconnected before connecting the board; the leads must not
hold the capacitor in place. No adhesive base or new mounting hardware is needed.

## Resistor identification

Each resistor illustration shows its four bands, in both gold-end (5%) and red-end (2%) versions.
Either version meets the circuit's 5% acceptance limit; either physical orientation works.

| Parts | Value | First three bands |
|---|---|---|
| R1 | 100 kΩ | Brown · black · yellow |
| R2 | 22 kΩ | Red · red · orange |
| R3, R4 | 10 kΩ | Brown · black · orange |
| R5, R6 | 4.7 kΩ | Yellow · violet · red |
| R7 | 3.3 kΩ | Orange · orange · red |

The planned NTE QW parts have conflicting tolerance documentation: [Vetco's listing](https://vetco.net/products/nte-qw247_4-7k_ohm_1-4_watt_resistor)
says 5%, while [NTE's series datasheet](https://static6.arrow.com/aropdfconversion/b7940565efd0f9772de4494dc62a7ce878d576bb/quarter.pdf)
specifies 2% for these values. Both versions are shown. Band meanings follow the
[Vishay colour chart](https://www.vishay.com/docs/49411/resistor_color_code_calculator.pdf).

## Wire preparation

Cut one wire at a time. Cut lengths use the curved 3-D path, through-board ends, rear tails and **6 mm trimming stock**.
That stock is trimmed off; it is not a slack loop left on the board. The rounded routes themselves provide the rise and room
for forming. Outgoing leads include the rounded turn outside the board; add the measured external run and service slack.
Keep the pump/LED service slack outside the board footprint.

Strip enough to reach the indicated joint on the back, keeping the rest insulated. Gently twist the strands, insert them
**untinned**, and keep the insulation against the front face. Solder the wire's own hole first; form its short end along the
highlighted rear path, then solder the destination. Lightly tin the exposed end as part of this operation. No loose strands,
no solder bridges, and no forcing pre-tinned wire into the nominal 1 mm holes. Do not bend at a ceramic capacitor's coating.

C2’s insulated leads run beneath the board, around its column-X side, then across the battery. The free runs reserve
Ø4 mm for the Ø1.8 mm wire; the first 35 mm follows the joint/forming template. Keep the completed underside within 11 mm.
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
| Resistors | Body limit 6.8 × Ø2.7 mm. R3/R4 lie flat on the rear, connected with their own leads; retain ≥26 mm on R4’s C13 end before forming. Other resistors lie on the front. |
| D1/D3 | Body limit 5.5 × Ø2.9 mm. [Vishay DO-41 reference](https://www.vishay.com/docs/88525/1n5817.pdf) is smaller; this is not a dimensional guarantee for NTE585. |
| C1/C3 | [Vetco disc](https://vetco.net/products/vupn6606_ceramic_capacitor_0-1_uf_-2080_50_volts_z5u): no mechanical drawing. Require ≤Ø10 × 4 mm and sufficient untrimmed leads to reach the indicated joints without bending at the coating. |
| C2 | [Vetco 2200 µF / 25 V](https://vetco.net/products/2200uf25vdc_2200uf_25_volt_electrolytic_capacitor): no case drawing. Require ≤Ø18 × 25 mm; fit pigtails to its actual lead spacing. |
| JP1 | Header and shunt ≤5.5 × 2.5 × 8 mm. |

## Checks and regeneration

`design.json` is the placement and route data. `mechanical.py` supplies shared size allowances; `routing.py` validates the
wire paths. `redesign/check.py` checks exact polyline separation with a curve allowance, 4 mm bend construction, connectivity,
separate wire holes, the order of crossings, rear lead/metal-nut separation and access with a 2 mm iron tip widening to 5 mm over 12 mm. `cad/parts/electronics.py` checks the assembly reserve against the enclosure.
These are design checks, not measurements of an assembled board.

```sh
python3 assembly_guide.py
python3 generate.py --export
python3 -m pytest test_assembly.py -q
```

Python dependencies: NumPy, SciPy, Shapely, NetworkX, pytest, pypdf; PNG/PDF export also uses `rsvg-convert`.
Keep all power disconnected for continuity checks, then follow [EL-10 commissioning](../../BUILD_GUIDE.md#el-10-commission-the-board-without-loads).
The spreadsheet has not been edited. Allocate eight M3 nuts and four M3×10 screws from the existing hardware to the board;
whole-device use becomes 22 nuts and ten M3×10 screws. No nylon spacers, M3×25 screws or adhesive tie base are required.
The existing larger power-splice heat-shrink requirement remains.
