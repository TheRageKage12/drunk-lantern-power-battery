# Prototype-board assembly

[Interactive viewer](index.html) · [Two-sided drawing](both-sides.png) ·
[Printable PDF](board-assembly.pdf) · [Solder schedule](WIRE_SCHEDULE.md)

The layout uses the planned Vetco VUPN2924 70 × 50 mm board. Follow the
[build guide](../../BUILD_GUIDE.md#4-electronics-build-it-on-the-bench-first) for the circuit,
off-board wiring, power sequencing and commissioning. This page covers the board layout itself.

## Reading the drawing

- Hole names A–X / 01–18 are assigned from the component side. The solder-side view is mirrored;
  keep the same physical edge at the top when turning the board over. Supplier lettering may differ.
- A pad is the copper soldering spot around a hole. Coloured dots mark occupied pads; a diagonal
  mark means an unused device pin, soldered mechanically with no wire. Small squares mark cable
  attachments or wire junctions. Large dashed squares reserve space around mounting screws.
- Each solid coloured path is one rear wire, soldered only at its endpoints. Bends and crossings
  are not joints. Insulate all wires except the short bare links W01/W02/W05–W07.
- Dashed coloured lines are cables leaving the board. Cable IDs are distinct from hole names:
  cable H02 attaches to hole N02; hole H02 is C2 positive. Use the solder schedule for every endpoint.
- In the viewer, connection buttons highlight groups of connected points (nets); **Show W…**
  highlights one wire. Click a coloured spot for its connection. **+ / −** zoom; **Fit** resets.

## Placement and soldering

1. Confirm the physical board's 24 × 18 hole array and its edge offsets. The drawing assumes
   2.54 mm spacing, starting 5.79 mm from the left and 3.41 mm from the top. It is not a drill template.
2. Mount the board landscape, component side toward the shell, bottom 2 mm above the deck.
   Check the four screw centres against the printed panel before drilling 3.2 mm holes at
   x = 15/55 mm and y = 15/45 mm from the component-side top-left. Keep each 9 × 9 mm area clear.
3. Fit the small parts and DIP-14 socket before the XIAO and tall parts. U1's notch faces row 01;
   XIAO USB faces column A. Q1/Q2 printed faces face row 18, with G-D-S pins from columns P to R.
   Keep their metal drain tabs separate. Follow the drawing's diode stripes and C2 polarity.
4. Lay C2 flat with insulated formed leads; reserve a case no larger than **25 mm long × 18 mm
   diameter**. Its actual dimensions remain unverified. Secure its body independently of its leads,
   leave the vent clear and revise the placement if it is too large.
5. Solder the listed rear wires, starting with the bare links. Use the planned 22 AWG wire for
   W01–W10 and battery/pump/LED cables; do not rely on the small copper pads to carry load current.
   Other wires may use the same gauge if they fit. Attach wire ends at component solder joints
   instead of forcing multiple conductors through occupied holes. Drawn bends are not cut lengths.
6. Q02 and L16 are wire junctions with no additional component. Attach and strain-relieve cables
   H01–H14, checking connector positions end-to-end rather than relying on wire colours.
   D2 stays at the pump and C4 at the Hall sensor; neither belongs on this board.

## Fit and checks before power

Keep rear wires and clipped leads within the **4.5 mm** panel clearance. Q1/Q2 must project no more
than **22 mm** from the board face and C2 no more than **18 mm**. Keep the last 5 mm at the column-X
edge empty and nearby R5/R6/R7/D3 no more than 3 mm high to clear the shell's passing retaining boss.
Route cables clear of that path and check clearance while removing the shell.

Actual capacitor size, board hole offsets, wire crossings and assembled clearances still need
physical confirmation. The CAD now checks the board and reserved component/cable volumes against
the enclosure and its retaining-boss sweep; see [fit limits](../../../cad/README.md#electronics-fit-limits).
Remove print supports beneath the four mounting pads before assembly. This is not a verified physical build.

With all power disconnected and U1 removed, use the schedule to check continuity for each wire,
inspect for solder bridges and confirm component orientation. Then follow the build guide's
staged power-up procedure. The generator checks connectivity, unused pins, and wire/pad clearance
around mounting holes; it cannot check solder quality, physical fit or thermal behaviour.

## Sources and regeneration

Pin placement was checked against [Seeed's standard XIAO RP2040 pinout](https://wiki.seeedstudio.com/XIAO-RP2040/)
and [official footprint library](https://files.seeedstudio.com/wiki/XIAO-KiCad-Library/New_XIAO_Series_Footprints.zip)
(15.24 mm header-row separation), [TI's 74AHCT125 datasheet](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf),
and the [reviewed circuit](../../images/wiring.svg). Board specifications come from
[Vetco's exact listing](https://vetco.net/products/phenolic-protoboard-1-97-x-2-76-inch).

`layout.py` defines placement and wire endpoints; `generate.py` validates them and combines the
SVG drawings with the `viewer.html` template. Run from this directory:

```sh
python3 generate.py
python3 generate.py --export
```

The first command rebuilds the standalone viewer and solder schedule using Python's standard
library. `--export` also rebuilds the combined PNG and four-page PDF; it requires `rsvg-convert`
on PATH and the Python `pypdf` package. Intermediate SVGs and PDF pages are created in a temporary
directory and removed automatically. No intermediate exports need to be committed.
