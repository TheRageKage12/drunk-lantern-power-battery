# Full perfboard assembly

[Assembly PDF (four pages)](board-assembly.pdf) · [Interactive two-sided diagram](index.html) · [Both sides, SVG](both-sides.svg) ·
[Component side](component-side.png) · [Solder side](solder-side.png) ·
[Every wire and solder pad](WIRE_SCHEDULE.md)

This implements the reviewed circuit on the planned Vetco VUPN2924 70 × 50 mm perfboard. It replaces
the earlier block placement proposal with specific holes and an explicit wire schedule. The circuit
and shopping-list quantities are unchanged. The layout is electrically checked, not physically built.

## Reading the drawing

- Coordinates **A–X / 01–18 are defined by the component-side drawing**. Use these coordinates even if
  the board's factory markings are on its copper side. The rear view is mirrored horizontally; its
  columns read X–A. Keep the same physical edge at the top when turning the board over.
- A coloured-ring solder dot is an occupied pad. A small diagonal mark indicates an unused device pin:
  solder it mechanically, but attach no wire. Square pads are rear cable attachments or wire junctions.
- Components go on the plain side; leads, header pins and socket pins pass through and solder on the
  copper side. Pigtails attach directly to the rear pads; they do not protrude through C2's footprint.
- **Every solid coloured rear path is a separate wire.** Only its endpoints are soldered. Corners and
  crossings are not solder joints. White outlines distinguish overlapping insulated wires.
- W01, W02 and W05–W07 are short bare copper links between adjacent same-net pads. Insulate every
  other wire, including wires crossing unused pads. Do not connect a whole row as on a breadboard.
- Dashed wires H01–H14 leave the board; their destinations are in the cable table. H labels are cable
  IDs, not hole coordinates: for example cable H02 attaches to pad N02; **pad H02 is C2 positive**.
- The four large dashed squares reserve space for mounting screws. Their circles mark the 3.2 mm
  holes to drill; keep the surrounding 9 × 9 mm squares clear of components and wires.
- A pad is the copper soldering spot around a hole. A net is a group of points connected electrically
  by wires. In the interactive view, a connection button such as **Ground** highlights its wiring
  while keeping both sides visible. In the wire list, **Show W…** highlights one wire and its two soldering holes.
  Point at, click or keyboard-focus a coloured spot to display its hole and component connection.
- Use **+ / −** to enlarge or reduce either drawing; scroll horizontally to see enlarged areas.
  **Fit** resets the scale. Instructions are under **How to read this diagram**. The HTML is self-contained and works without internet access.

## Placement and assembly

1. Dry-fit the actual board, XIAO, socket and capacitor. The drawing uses the verified 24 × 18 hole
   count and 2.54 mm pitch, but assumes a centred array: first hole 5.79 mm from the left edge and
   3.41 mm from the top. Measure that registration before transferring mounting-hole locations.
2. Mount landscape, bottom edge 2 mm above the deck. Four 3.2 mm mounting holes are at x=15/55 mm
   and y=15/45 mm **from the component-side top-left corner**. Keep the 9 × 9 mm mounting areas
   clear of copper connections and solder. Do not drill through a populated board.
3. Install the small parts and DIP14 socket, then the XIAO headers, Q1/Q2 and JP1 header. U1's notch
   points to row 01. XIAO USB points toward the A edge. The MOSFET printed faces point toward row 18;
   their pins run G-D-S from P to R. Keep their metal drain tabs separate. Use U1=74AHCT125 and
   Q1/Q2=IRLZ44NPBF; this is not a generic MOSFET-module pinout. Keep their tops within 22 mm of the
   board face and the three right-side resistors and D3 within 3 mm of the board face.
4. D1 has anode at N17 and striped cathode at Q17. D3 has anode at W14 and striped cathode at W18.
   C1/C3 are non-polarized. JP1 uses N18/O18; fit a removable shunt for normal battery operation and
   remove it for USB service, following the build guide's complete power procedure.
5. C2 lies across the upper middle. Its **maximum reserved case envelope is 25 mm long × 18 mm
   diameter**, with insulated formed leads reaching H02 (+) and H04 (−). Its listed case dimensions
   are unpublished. If the purchased capacitor exceeds that envelope, revise its placement rather
   than forcing it into this layout. Do not stress the lead seal; secure the body independently of
   its leads, keep the vent unobstructed and keep its projection toward the shell within 18 mm.
6. Make the bare adjacent-pad links first. Fit the insulated rear wires in schedule order, keeping
   them flat and leaving the mounting squares clear. The drawn bends indicate routes, not exact
   cut lengths. Leave enough slack for gentle bends and strip only the soldered ends. Inspect each
   joint for bridges to neighbouring pads. Do not rely on the small copper pads as load-current buses:
   W01–W10 and the pump/LED/battery pigtails use the planned 22 AWG conductors. The other connections
   can also use that wire if laid flat; check insulation thickness at crossings against the 4.5 mm
   rear clearance. No extra terminal blocks or XIAO sockets are assumed.
7. Q02 is a power-ground junction and L16 is a quiet-ground junction. No additional component goes
   in either hole. Solder their listed wire ends to the pad. The load returns join the power-ground
   distribution directly; they do not pass through the XIAO ground pin. Rear wires terminate at the
   component's solder joint instead of squeezing multiple conductors through an occupied hole.
8. Attach and strain-relieve H01–H14. Use the JST PH four-wire lock cable and JST SM LED cable already
   planned. Colours in the diagram identify nets; match connector positions end-to-end with a meter
   rather than relying on prewired cable colours. The connector manufacturer cavity numbering has
   not been assumed here.

## Parts away from the board

- Battery + connects to J1 centre and the input of S1. S1 output is H01/N01. Battery − connects to
  J1 sleeve and H02/N02. Insulate J1's unused switched terminal.
- Buck IN+/IN− use H03/H04; OUT+/OUT− use H05/H06. Adjust to 5.0 V while unloaded before connecting
  its output to this board.
- Pump +/− use H07/H08. D2 NTE586 stays directly across the pump terminals, stripe to pump +.
- LED +/− use H09/H10 through the JST SM pair.
- The lock cable is H11 (+5V), H12 (HALL), H13 (SW), H14 (GND). A3144, printed face toward you and
  leads down: pin 1=H11, pin 2=H14, pin 3=H12. C4 0.1 µF goes across pins 1–2 at the sensor. Twist
  switch COM=H14, NO=H13, NC unused. C4 and D2 are deliberately absent from the perfboard picture.

## Checks before power

Use the wire schedule as the assembly checklist, with battery, buck and USB disconnected and U1
removed from its socket. Verify continuity for every listed wire and inspect for unintended bridges.
Semiconductors can affect resistance readings, so do not interpret every finite resistance as a short.
Confirm the polarity of D1/D3/C2, separate MOSFET tabs, U1 orientation and a removable JP1. Then use
[the build guide's staged commissioning procedure](../../BUILD_GUIDE.md#4-electronics-build-it-on-the-bench-first).

The generator checks 76 occupied pads, 52 board wires and all 16 connected nets, including intentionally
unused pins. It rejects cross-net wires, disconnected intended nets, occupied mounting areas and routed
board wires through mounting areas. It does **not** validate solder quality, actual component sizes,
wire thickness, capacitor lead-forming, thermal behaviour or the complete three-dimensional enclosure.
The separate CAD PR still needs the populated-board and cable clearance checks.

## Sources and regeneration

Pin placement was checked against [Seeed's standard XIAO RP2040 pinout](https://wiki.seeedstudio.com/XIAO-RP2040/)
and [official footprint library](https://files.seeedstudio.com/wiki/XIAO-KiCad-Library/New_XIAO_Series_Footprints.zip)
(15.24 mm header-row separation), [TI's 74AHCT125 datasheet](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf),
and the [reviewed circuit](../../images/wiring.svg). Board specifications come from
[Vetco's exact listing](https://vetco.net/products/phenolic-protoboard-1-97-x-2-76-inch).

`layout.py` holds the component pads and explicit wire endpoints. Run `python3 generate.py` in this
folder to check and rebuild the SVGs, interactive HTML, JSON and wire schedule; render the SVGs with
`rsvg-convert` for PNG/PDF. Generator routing is for insulated wires, not copper PCB traces.
