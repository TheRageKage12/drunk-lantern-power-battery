# Prototype-board assembly

[Step-by-step soldering guide](assembly.html) · [Full layout viewer](index.html) · [Two-sided drawing](both-sides.png) ·
[Printable PDF](board-assembly.pdf) · [Solder schedule](WIRE_SCHEDULE.md)

The layout uses the planned Vetco VUPN2924 70 × 50 mm board. Follow the
[build guide](../../BUILD_GUIDE.md#6-electrical-track) for the circuit,
off-board wiring, power sequencing and commissioning. This page covers the board layout itself.

## Guided assembly with six wire colours

Open [assembly.html](assembly.html) directly in a browser; it is self-contained and works offline.
It highlights one solder point at a time, keeps earlier work visible and saves your place.
Use Next/Previous or the step list; front, mirrored rear and tilted views are available.
There are 190 solder operations, plus short fitting and inspection steps.

Fit components first, then the short tinned links, then insulated wires in the shown order.
Work with the board off its posts. Outgoing cables join the sequence at their assigned height;
thread the cap-floor cables before soldering, as EL-9 requires.

The guide uses the owner's [Electronix Express stranded 22 AWG kit](https://www.amazon.com/dp/B00B4ZQ3L0).
The [supplier lists approximately 1.7 mm outside diameter](https://www.elexp.com/collections/hook-up-wire-stranded/products/27wk22str25wire-kit-22ga-str-6-25ft-spool);
the routing reserves **1.8 mm**. **The printed CAD, 10 mm posts, mounting holes and component positions are unchanged.**
The wire stack reaches **9.1 mm**, leaving **0.9 mm** to the floor.

Short tinned links replace bulky insulated loops and distribute ground and power through spare pads.
Several outgoing cables attach directly to their circuit points, eliminating intermediate wires and joints.
There are **33 insulated runs instead of 61**, including the 14 outgoing cables, and 39 short bare links.
Each component lead carries at most two insulated wire ends. The circuit and independent pump/LED source
returns are unchanged; the quiet ground bus joins the input return beside C2.

The geometric check allows **at least 0.5 mm between unrelated wire corridors**. Every joint still needing
solder retains an approach for a **2 mm tip with 0.4 mm lateral clearance**. Higher wires may cover finished
lower joints. The three insulated-wire layers have **0.8 mm vertical clearance at crossings**;
follow each route and its crossing instructions.

Cut estimates include the route, end rises, short tinned ends and 4–8 mm trimming allowance.
Trim the second end after fitting; do not leave the extra as a loop. For outgoing cables, enter the measured
external run and service slack. Pump/LED slack starts at EL-9's 150 mm and stays outside the board gap.
The page includes a CSV cut list.

Only six spool colours are used; labels identify connections that share a colour. Red is switched battery,
black ground, white the 5 V paths, green 3.3 V/Hall, yellow sense/twist/LED return, and blue PWM/gates/pump return.
Do not treat a blue/yellow load return as ground or join white supply paths across D1/JP1.

## Reading the drawing

- Hole names A–X / 01–18 are assigned from the component side. The solder-side view is mirrored;
  keep the same physical edge at the top when turning the board over. Supplier lettering may differ.
- A pad is the copper soldering spot around a hole. Coloured dots mark occupied pads; a diagonal
  mark means an unused device pin, soldered mechanically with no wire. Small squares mark cable
  attachments or wire junctions. Large dashed squares reserve space around mounting screws.
- Each solid coloured path is one rear wire, soldered only at its endpoints. Bends and crossings
  are not joints. Only the links marked BARE in the schedule are stripped; keep all other wires insulated.
- Dashed coloured lines are cables leaving the board. Cable IDs are distinct from hole names:
  cable H02 attaches to hole N02; hole F02 is C2 positive. Use the solder schedule for every endpoint.
- In the viewer, connection buttons highlight groups of connected points (nets); **Show W…**
  highlights one wire. Click a coloured spot for its connection. **+ / −** zoom; **Fit** resets.

## Placement and soldering

1. Confirm the physical board's 24 × 18 hole array and its edge offsets. The drawing assumes
   2.54 mm spacing, starting 5.79 mm from the left and 3.41 mm from the top. It is not a drill template.
2. Mount the board component side up on the cap floor's four 10 mm standoffs (rev C: the cap floor in the top
   cap), rear wiring in the 10 mm under it. Check the four screw centres against the printed standoffs before
   drilling 3.2 mm holes at
   (x,y) = (18,17), (55,15), (15,45), (58,45) mm from the component-side top-left. Keep each 9 × 9 mm area clear.
3. Fit the small parts and DIP-14 socket before the XIAO and tall parts. U1's notch faces row 01;
   XIAO USB faces column A. Q1/Q2 printed faces face row 18, with G-D-S pins from columns P to R.
   Keep their metal drain tabs separate. Follow the drawing's diode stripes and C2 polarity.
4. Lay C2 flat with insulated formed leads; reserve a case no larger than **25 mm long × 18 mm
   diameter**. Its actual dimensions remain unverified. Secure its body independently of its leads,
   leave the vent clear and revise the placement if it is too large.
5. Solder the rear links with the board detached from its standoffs. Start with the 39 short tinned
   links, then work outward through the assigned heights: **3.0, 5.6, 8.2 mm** from the solder face
   to wire centre. The schedule gives each wire's layer. Use the owner’s stranded 22 AWG wire; the routing check reserves **1.8 mm** over insulation. Trim leads and keep
   solder joints within **1.5 mm** of the back face. Lay wire ends against the joint rather than
   forcing several wires through one hole. A shared endpoint is one solder joint; crossings elsewhere
   must remain insulated. Form smooth bends; drawn corners are routing guides, not cut lengths.
6. Square junction pads carry wires only; their connections are listed in the schedule. Strain-relieve cables
   H01–H14, checking connector positions end-to-end rather than relying on wire colours.
   D2 stays at the pump and C4 at the Hall sensor; neither belongs on this board.

## Fit and checks before power

The cap floor's standoffs provide **10 mm under the board**, outside four 9 × 9 mm screw areas.
The outer wire layer reserves 9.1 mm including insulation, leaving 0.9 mm to the cap floor.
Use M3 screw heads (and any washers) no larger than Ø6 mm; the component placement includes access for a straight
hex key with the lid off and the cap floor lifted out. Install the four M3-thread brass inserts in the standoffs' Ø4 × 6.5 mm
bores before mounting the board. Use M3×6 screws; check engagement with any washers added and do not
let a screw bottom out in the insert.

The component-side drawing and CAD use the **same individual body allowances**, with at least
1 mm between them. The smallest gap is **1.10 mm (U1 to R3)**; C3 is now **3.47 mm from U1**.
Q1/Q2 project at most 22 mm from the front. C2 projects at most 19 mm including retention beneath
its Ø18 mm case and overhangs the board's top by 2 mm. The column-X edge must stay within the
shown small-part allowances (3.2 mm resistors, 3.4 mm diode).

The checks cover body-to-body spacing, screw access, insulated wire corridors and their terminal
rises, solder height and the rear stack. **They do not verify
supplier-unspecified dimensions, wire bend radii or the detailed fan-out at shared solder joints.** Dry-fit the populated board and formed wires
before fastening it to the standoffs; do not compress wires to make it fit. Final fit still depends on the delivered parts and soldering workmanship.

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
| Rear wire | Owner’s Electronix Express stranded 22 AWG: nominal Ø1.7 mm; reserve Ø1.8 mm, ≥0.5 mm between unrelated wire corridors. Solder-joint allowance Ø1.9 × 1.5 mm. |

The circuit values and shopping-list items are unchanged. Component placement and mounting holes match the existing printed enclosure; only rear wiring changes in this revision.

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
`routing.py` checks wire corridors and writes their depths through the generator. `generate.py` combines the
SVG drawings with the `viewer.html` template. Run from this directory:

```sh
python3 generate.py
python3 generate.py --export
python3 assembly_guide.py
python3 -m pytest test_assembly.py -q
```

The first command rebuilds the standalone viewer and solder schedule with NumPy and Shapely installed. `--export` also rebuilds the combined PNG and four-page PDF; it requires `rsvg-convert`
on PATH and the Python `pypdf` package. Intermediate SVGs and PDF pages are created in a temporary
directory and removed automatically. No intermediate exports need to be committed.

`assembly_guide.py` combines the existing pin placement and saved `routing.json` with `assembly-template.html`.
It writes the standalone `assembly.html`; it does not rewrite the reference paths or CAD dimensions.
Its tests cover every lead/endpoint, layer and crossing order, shared-joint history, cut allowances, and rejection
of deliberately invalid endpoints, crossings, wire diameter, height and screw intrusions. Pytest is needed only
for the last command. Regenerate the guide whenever placement or saved routes change.
