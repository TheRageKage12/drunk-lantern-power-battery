# Prototype-board assembly

[Step-by-step soldering guide](assembly.html) · [Full layout viewer](index.html) · [Two-sided drawing](both-sides.png) ·
[Printable PDF](board-assembly.pdf) · [Solder schedule](WIRE_SCHEDULE.md)

The layout uses the planned Vetco VUPN2924 70 × 50 mm board. Follow the
[build guide](../../BUILD_GUIDE.md#6-electrical-track) for the circuit,
off-board wiring, power sequencing and commissioning. This page covers the board layout itself.

## Assembly

Open [assembly.html](assembly.html) in a browser. Each step highlights one solder point,
keeps earlier work visible and saves your place. Detailed calculations stay here, out of the workbench view.

1. Fit and solder the components with the board off its mounts.
2. Form the short bare tracks from your wire, lightly tin them, and solder every marked anchor.
   Bends are anchored; straight spans between anchors are at most three holes (7.62 mm).
3. Fit the outgoing cable row and retain it flat, side by side. Its bends turn upward beyond the board edge.
4. Install the insulated jumpers in the guide’s access-checked order (lower wires first at crossings). Every jumper uses its **own empty holes**;
   no thick wire is added to a component lead. Form the bends before soldering either end.
5. Check continuity, shorts, polarity and height; mount the board only after it fits without squeezing wires.

The guide provides a cut length, actual side profile and downloadable **1:1 forming template** for each wire.
Print templates at 100% and check their 10 mm scale. Insulated bends use a **4 mm centreline radius**;
a 6.5 mm round former gives about that radius with this wire. This is a design target, not a supplier bend rating.
Bare conductor bends are formed before tinning. Do not kink the PVC or leave loose strands.

For insulated jumpers, strip 4 mm and insert each end **1.2 mm**, flush with the component face.
Mark that insertion depth before fitting, including holes hidden under component bodies. Do not force tinned
ends into a hole: insert the twisted, untinned strands and solder afterward. Existing leads may share a
flat tinned track; the insulated jumpers each have a separate hole.

Cut estimates use the **curved 3-D length**, through-board ends and trimming stock. Trim after forming;
excess stock is not a retained slack loop. For cables, add the measured external run and service slack.
Pump/LED service slack stays outside the board gap. Cable colours and a CSV cut list are in the guide.

## Mounting hardware — no reprints

Use **four 6 mm-long unthreaded spacers**, with a bore of at least 3.2 mm and outside diameter no greater
than 6 mm, plus **four M3×12 screws**. Place one spacer on each existing 10 mm printed post.
This gives **16 mm from the solder face to the cap floor**. Screw engagement is 12 − 6 − 1.2 = **4.8 mm**,
the same as the original M3×6 screw without a spacer. Keep screw heads at most Ø6 mm and tighten gently.

The board, component positions, mounting holes and **all printed geometry remain unchanged**.
The non-printing electronics model checks the raised board, removable spacers and rounded cable exit against
the enclosure. It is not a replacement print file. Fit the existing M3 inserts before mounting the board.

The four mounting centres remain (18,17), (55,15), (15,45), (58,45) mm from the component-side top-left.
Confirm the physical board grid and post locations before drilling Ø3.2 mm board holes; the drawing is not a drill template.

## Fit allowances

| Item | Design allowance |
|---|---|
| Wire | [Electronix Express 27WK22STR25](https://www.elexp.com/products/27wk22str25wire-kit-22ga-str-6-25ft-spool), the owner’s [B00B4ZQ3L0 kit](https://www.amazon.com/dp/B00B4ZQ3L0): nominal Ø1.7 mm; model Ø1.8 mm. |
| Solder joints | Up to Ø2 mm × **2.5 mm high**; trim component leads to ≤1.5 mm before wiring. |
| Insulated jumpers | Rounded 4 mm bends, with crowns at 6, 9 or 12 mm from the rear face. |
| Maximum nominal wire height | **12.9 mm**, including insulation. |
| Additional wire bow | **0.5 mm** beyond the nominal height. |
| Mount/board vertical variation | **0.5 mm** deducted from the 16 mm space. |
| Remaining floor clearance | **2.1 mm after both allowances**, versus the previous 0.9 mm before allowances. |
| Wire movement | 0.4 mm per free insulated jumper; crossing checks retain clearance after that movement. |
| Printed-post variation | Posts expanded by 0.25 mm per side in the detailed clearance check. |

The cable row is a **retained parallel bundle**, with 0.74 mm nominal space between neighbouring insulated
wires; it does not have the independent movement allowance of the free jumpers. Retain the row with tape
while soldering and strain-relieve it before mounting. Keep its external service loops outside the board gap.
The cable-exit envelope includes 0.5 mm for positioning. Short bare tracks are supported at their solder anchors.

**Physical acceptance check:** the installed space must measure at least **15.5 mm**, and the completed rear
wiring must stay within **13.5 mm** of the solder face, leaving at least **2 mm** clear. Check the spaces beside
all four posts as well. Do not tighten the screws to flatten wires. A failed fit check means reforming the wire,
not compressing it. These calculations establish a build allowance; they do not certify an unbuilt board.

The circuit is unchanged. Pump and LED source returns remain separate until the input ground bus;
logic returns do not run through those load-return branches. D2 remains at the pump and C4 at the Hall sensor.
Follow the [build guide](../../BUILD_GUIDE.md#6-electrical-track) for the buck adjustment, power sequencing and USB procedure.

## Reading the drawing

- Hole names A–X / 01–18 are assigned from the component side. On the mirrored solder-side view,
  keep row 01 at the top. Supplier lettering may differ.
- A pad is the copper soldering spot around a hole. Small squares mark cable or wire junctions;
  large dashed squares reserve the mounting areas. A diagonal mark means an unused device pin.
- Bare tracks join **all their listed solder anchors**. Insulated arches cross other wires without joining.
  The guide highlights each intermediate anchor separately.
- Cable H02 is a cable identifier, not hole H02. Use the generated schedule for each cable’s current pad.
- The viewer’s connection buttons highlight a circuit connection group (a “net”). Click a solder point
  to identify it; use + / − to zoom and Fit to reset.

The component-side body checks still allow at least 1 mm between bodies (minimum 1.10 mm).
C2 must fit its **Ø18 × 25 mm** allowance and be secured independently of its leads, with its vent clear.
Actual component sizes that the suppliers do not publish still need checking against the limits below.

## Dimensions used

“Limit” means a required purchasing/assembly size, not a measurement supplied by the vendor.
Check those items before soldering; a part over its limit needs a different part or a revised layout.

| Part | Evidence and drawing allowance |
|---|---|
| XIAO RP2040 | [Seeed board/footprint](https://wiki.seeedstudio.com/XIAO-RP2040/): 21 × 17.8 mm, 15.24 mm header-row pitch. Allow 21.5 × 18.3 mm; **12 mm assembled height is a limit**, including headers and pins trimmed on the rear. |
| U1 + socket | [TI PDIP-14](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf): 2.54 mm lead pitch, 7.62 mm rows. [Vetco socket](https://vetco.net/products/14-pin-ic-socket-2-54mm-spacing-0-1) does not specify its outer body: **limit 11 × 20.5 × 10.5 mm** including the IC. |
| Q1/Q2 | [Infineon IRLZ44N TO-220 drawing](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irlz44n-datasheet-en.pdf): maximum 10.54 × 4.69 mm section, 15.24 mm body/tab height. Allow 10.8 × 4.9 mm and trim/form leads to keep total projection ≤22 mm. |
| R1–R7 | Axial body **limit 6.8 × Ø2.7 mm**, projection 3.2 mm. All spans leave at least 1 mm of straight lead at each end before bending. |
| D1/D3 | Body **limit 5.5 × Ø2.9 mm**, projection 3.4 mm. This exceeds [Vishay DO-41](https://www.vishay.com/docs/88525/1n5817.pdf) maxima (5.2 × Ø2.7 mm), but that is a package reference, not a dimensional guarantee for the listed NTE585. |
| C1/C3 | [Vetco disc capacitor](https://vetco.net/products/vupn6606_ceramic_capacitor_0-1_uf_-2080_50_volts_z5u) has no mechanical drawing. **Limit Ø10 × 4 mm thick, 13 mm mounted height**; form leads to the shown 2.54/5.08 mm spans without bending at the coating. |
| C2 | [Vetco 2200 µF / 25 V](https://vetco.net/products/2200uf25vdc_2200uf_25_volt_electrolytic_capacitor) omits case size. **Limit Ø18 × 25 mm**, laid flat; leads have 6.5 mm between pad and case for insulated forming. Secure the body without covering its vent. |
| JP1 | Header + shunt **limit 5.5 × 2.5 × 8 mm**. |
| Rear wire | Owner’s Electronix Express stranded 22 AWG: nominal Ø1.7 mm; reserve Ø1.8 mm. Solder-joint allowance Ø2 × 2.5 mm; formed bends and movement allowances as above. |

The circuit values are unchanged. The hardware list now adds four 6 mm spacers and replaces the four board M3×6 screws with M3×12; the spreadsheet has not been edited. Component placement and mounting holes match the existing printed enclosure; rear wiring and removable mounting hardware change in this revision.

With all power disconnected and U1 removed, use the schedule to check continuity for each wire,
inspect for solder bridges and confirm component orientation. Then follow the build guide's
staged power-up procedure. Software checks cannot establish solder quality or thermal behaviour.

## Sources and regeneration

Pin placement was checked against [Seeed's standard XIAO RP2040 pinout](https://wiki.seeedstudio.com/XIAO-RP2040/)
and [official footprint library](https://files.seeedstudio.com/wiki/XIAO-KiCad-Library/New_XIAO_Series_Footprints.zip)
(15.24 mm header-row separation), [TI's 74AHCT125 datasheet](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf),
and the [reviewed circuit](../../images/wiring.svg). Board specifications come from
[Vetco's exact listing](https://vetco.net/products/phenolic-protoboard-1-97-x-2-76-inch).

`layout.py` defines placement and wire endpoints; `mechanical.py` supplies shared body dimensions;
`routing.py` generates rounded 3-D paths and checks joints, wire crossings, posts, spacers and the floor. `generate.py` combines the
SVG drawings with the `viewer.html` template. Run from this directory:

```sh
python3 generate.py
python3 generate.py --export
python3 assembly_guide.py
python3 -m pytest test_assembly.py -q
```

The first command rebuilds the standalone viewer and solder schedule with NumPy and Shapely installed. `--export` also rebuilds the combined PNG and multi-page PDF; it requires `rsvg-convert`
on PATH and the Python `pypdf` package. Intermediate SVGs and PDF pages are created in a temporary
directory and removed automatically. No intermediate exports need to be committed.

`assembly_guide.py` combines the existing pin placement and saved `routing.json` with `assembly-template.html`.
It writes the standalone `assembly.html`; it does not rewrite the reference paths or CAD dimensions.
Its tests cover every lead and anchor, tip access and crossing order, shared-joint history, curved cut lengths,
independent load returns, and rejection of tighter bends, oversized joints/wire, reduced floor space and post intrusions. Pytest is needed only
for the last command. Regenerate the guide whenever placement or saved routes change.
