# Green Lantern power battery that pours a shot: build guide

A 3D-printed Green Lantern power battery, about 50 cm tall and 19 cm across at the base, with a hidden pump, a
hidden nozzle and a twist-to-pour lock.

The sphere has two openings:

- the **hand opening** on your side, closed by a curtain of frosted plastic strips;
- the frosted **display window** on the far side.

Throughout this guide, "your side" means the hand opening and "display side" means the window opposite it.

**The show in one paragraph.** Push the empty shot glass in under the lock until it clicks. Punch in, ring face
first, and the ring seats in the lock: the lantern glows faintly. Twist 45 degrees and hold it while you recite the
oath. Behind the lock wall the pump pours about 1 oz into the glass while the light climbs from 15 % to 90 % over
about 11 seconds. Turn back and the light swells to full, then goes dark. Grip the glass, slide it toward you, lift
it and bring it out.

![interaction timeline](images/interaction.png)

**Status.** Designed, modelled and simulated; not yet built.

- The firmware compiles and passes 20 simulated safety scenarios (`firmware/test`).
- The CAD passes its fit checks, including the TalentCell mount and the electronics clearance envelopes. Those
  checks use the reserved sizes in [CAD fit limits](../cad/README.md#electronics-fit-limits), so measure the real
  capacitor, connectors, buck, switch and jar before printing. The battery and the pump are already measured.
- Every bay is parametric (`cad/params.py`): a measured number is a one-line change and a re-run of
  `python3 build.py`.

## Viewer and videos

- **3D assembly viewer:** [open it in the browser](https://raw.githack.com/TheRageKage12/drunk-lantern-power-battery/main/docs/assembly-viewer/index.html).
  Each printed part has its own colour. The 14 steps follow the subassemblies and section 9, and an exploded view
  shows how everything stacks. Click a part for its name and print notes.
- **Videos:** [step-by-step assembly (4:30)](videos/assembly-guide.mp4) ·
  [exploded assembly (0:12)](videos/separate-and-assemble.mp4) ·
  [opening for service (0:12)](videos/service-access.mp4).
  - The step-by-step video follows the build order and has chapter markers. Two orange-tube cutaways show the
    pump-to-floor route and the nozzle threading.
  - The exploded video shows how the parts fit together; use the step-by-step video for the order.
  - The pump outlet and the loose service loop are illustrative. Wiring, the curtain and the screws are described in
    this guide but not animated.
  - **Skip the "Install the charge jack" chapter.** The jack is no longer fitted: you charge through the splitter's
    female end (section 12).

## Contents

1. [How it works](#1-how-it-works)
2. [Shopping list](#2-shopping-list)
3. [Print the parts](#3-print-the-parts)
4. [Electronics (build it on the bench first)](#4-electronics-build-it-on-the-bench-first)
5. [Firmware](#5-firmware)
6. [The lock](#6-the-lock)
7. [The fluid path](#7-the-fluid-path)
8. [The lock wall, the curtain and the top](#8-the-lock-wall-the-curtain-and-the-top)
9. [Final assembly](#9-final-assembly)
10. [Calibration](#10-calibration)
11. [Test before the party](#11-test-before-the-party)
12. [Performing it](#12-performing-it)
13. [Cleaning and storage](#13-cleaning-and-storage)
14. [Troubleshooting](#14-troubleshooting)
15. [What this budget build leaves out](#15-what-this-budget-build-leaves-out-and-how-to-add-it-back)

---

## 1. How it works

```
 0. before: push the empty glass in under the lock until it clicks over the ridge at the stop
 1. punch in, ring face first (6x2 mm magnet hidden in the printed ring) -> Hall sensor sees it -> light fades up to ~15 %
 2. twist 45 deg counterclockwise and HOLD -> a cam clicks the microswitch -> pump starts, light starts climbing
 3. keep holding through the oath: the pump runs ~11 s while the light climbs to ~90 %
 4. let the ring turn back (spring) -> light swells to 100 % and goes dark
 5. grip the front of the glass, slide it 3 cm toward you, lift it ~5 cm out of its slot and bring it out

 Let go early: the pump stops where it is, the light swells ~10 % and goes dark.
 Safety: the pump only runs while the ring is in AND the twist is held, and only once per insertion.
```

| Where | What is there |
|---|---|
| Top dish | A frosted disc in its floor. A ring of LED strip in the hole under it makes the top glow. |
| Sphere, your side | The hand opening (120 x 96 mm), closed by a curtain of frosted plastic strips that your hand and the glass push through. |
| Sphere, inside | The **lock wall**, 2.5 cm past the centre (toward the display window).<br>• **On its face, facing you:** the lock and a column of LEDs either side. The lock is a rotor with the keyed ring pocket, 0 and 45 degree hard stops, a spring plunger that returns it, a cam, the D2F-01L microswitch and the A3144 Hall sensor.<br>• **Under the lock:** the glass, in a slot.<br>• **Behind the wall, out of sight:** the nozzle, over the back third of the glass, and 4 rows of LEDs facing the display window. |
| Sphere, display side | The white diffuser window. |
| Lower dish | Hollow neck: the glass slot hangs into it; the tube and the cables pass through it. |
| Base | A removable **cartridge** that slides up into the base drum, held by 3 thumbscrews underneath.<br>• **Floor:** the 12 V battery pack, lying flat, with the buck converter beside it.<br>• **Deck above it:** the jar, the Kamoer pump and the electronics board.<br>• **Nothing shows on the shell.** The power switch sits in a pocket under the cartridge floor (tip the lantern to flip it), and the battery's charge-level LEDs show through a thin slot in the floor.<br>• **To refill or charge:** undo the thumbscrews and lift the lantern off; the cartridge stays on the table, with the charge lead waiting inside. |

![fluid path and layout](images/fluid-path.png)

The drink touches only the jar, the platinum-silicone tube and the glass. No printed part is in the liquid path.

---

## 2. Shopping list

The live list, with who has each item and what is left to buy, is the
[shared Google Sheet](https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit).
The tables below describe the same parts and why each one was chosen; the Sheet is the source of truth for
quantities, prices and who has what.

- **Prices.** Amazon prices were checked on 2026-10-15, Vetco's on 2026-10-13. Prices marked "~" are estimates.
- **Item numbers** are only for this guide; the Sheet doesn't use them.

### 2.1 Order online

| # | Item | Buy | Price | Notes |
|---|---|---|---|---|
| 1 | Pump | [Kamoer KPHM200, 12 V (B09HGVLHFV)](https://www.amazon.com/dp/B09HGVLHFV) | $28.00 | 200 mL/min or more at 12 V, 0.7 A. Run at ~70 % speed it pours about 1 oz in 11 s. |
| 2 | Tubing | [AUBER 1/8" ID x 1/4" OD platinum-cured silicone, 10 ft (B0DKB1NKB4)](https://www.amazon.com/dp/B0DKB1NKB4) | $13.99 | The exact 3.2 x 6.4 mm size the Kamoer head needs. FDA 21 CFR 177.2600, NSF 51. Thinner 1/8" x 3/16" tube will not pump. One run is ~95 cm; the rest covers replacements (the tube is the part that wears). |
| 3 | LED strip | [HAMRVL COB LED strip, green, 12 V, 8 mm, 5 m (B0CKYFLZFQ)](https://www.amazon.com/dp/B0CKYFLZFQ) | $14.99 | COB: 320 LEDs/m under one continuous coating, so it glows evenly with no dots. Cuts every 25 mm. You use 75 cm in 7 pieces. Its current isn't listed; COB strips like it draw roughly 0.8 A/m, so ~0.6 A for 75 cm. |
| 4 | Buck converter | [LM2596 step-down module, 5-pack (B0DBVYP91F)](https://www.amazon.com/dp/B0DBVYP91F) | $7.99 | 9–12.6 V in, set to 5.0 V out for the XIAO, gate driver and Hall sensor. 43 x 21 mm. |
| 5 | Magnets | [6 x 2 mm neodymium, 45-pack (B0CBRVF4PN)](https://www.amazon.com/dp/B0CBRVF4PN) | $6.29 | 1 in the ring key (the pack is the smallest sensible buy). |
| 6 | Vent valve | [AQUANEAT aquarium check valves, 10-pack (B086JRH4WS)](https://www.amazon.com/dp/B086JRH4WS) | $4.79 | One goes in the jar lid: lets air in as the pump draws the drink out, but nothing out if the jar tips. Fits 3/16" airline. |
| 7 | Microcontroller | [Seeed XIAO RP2040, pre-soldered (B0DRNTQ338)](https://www.amazon.com/dp/B0DRNTQ338) | $10.99 | |
| 8 | 12 V battery pack | [TalentCell YB1203000 with charger (B00MHNQIR2)](https://www.amazon.com/dp/B00MHNQIR2) | $22.99 | 3000 mAh, 3 A maximum output, 105 x 65 x 25 mm; output falls from 12.6 to 9 V as it drains. Its one DC5521 port is both input and output, and its own switch must be ON to charge. You also use its supplied charger (12.6 V, 0.5 A, ~6 h) and its 1-female-to-2-male splitter, which replaces a charge jack (section 4, step 2). The cartridge tray is built for this case. |
| 9 | D2F-01L lever microswitch, 4-pack (1 used) | [Amazon B0DBV9JX6L](https://www.amazon.com/dp/B0DBV9JX6L) | $7.97 | Third-party (Pecafeitas) listing of the 0.1 A hinge-lever version. Omron's datasheet gives its minimum load as 1 mA at 5 V (the plain D2F needs 100 mA), which the section 4 interface supplies. Omron provenance is not verified: check the marking, the peg spacing against `switch_bracket`, and that it clicks reliably 50 times. |
| 10 | Heat-set inserts | [ruthex RX-M3x5.7 brass, 100-pack (B08BCRZZS3)](https://www.amazon.com/dp/B08BCRZZS3) | $9.99 | 32 used. 5.7 mm long, made for a 4.0 mm hole: the 32 receiving bores are 4.0 x 6.5 mm (section 3). Any plain M3 x 5.7 x 4.6 mm brass insert is the same part. |

> **Hall sensor alternative (not recommended).** The lock is built for the A3144 from Vetco (item 11), on a post
> that reaches up inside the rotor to about 3 mm from the magnet. An Adafruit DRV5032 board (#6051) also works: set
> `HALL_SENSOR = 'DRV5032'` in `cad/params.py` and reprint `rotor` and `socket_base`. It sits under the plate, 7.7 mm
> from the magnet instead of 3, and works on 3.3 V with either magnet pole. Adafruit ships slowly.

### 2.2 Pick up locally

| # | Item | Where | Price | Notes |
|---|---|---|---|---|
| 11 | Hall sensor, A3144 | [Vetco, VUPN6596](https://vetco.net/products/vupn6596_hall-effect_sensor_-_allegro_a3144eua_d63) | $1.99 | Runs on 5 V, reacts to one magnet pole. It sits on a post inside the lock, ~3 mm from the magnet: about 90 mT there, 2.5 x its worst-case switch point. |
| 12 | Cable plugs | Vetco: [JST PH 4-pin pair](https://vetco.net/products/jst-ph-2-0-4-pin-connector-male-female-pair-pre-wired) ($2.24) for the lock cable, [JST SM 2-pin pair](https://vetco.net/products/vupn1054_jst_sm_2_pin_m-f_pair_locking_connector) ($1.75) for the LED leads | $3.99 | So the lantern unplugs from the base cartridge. |
| 13 | 74AHCT125 quad buffer, DIP-14 | [Vetco, VUPN524](https://vetco.net/products/vupn524_quad_level-shifter_-_74ahct125_-_3v_to_5v_d96) | $2.95 | Turns the XIAO's 3.3 V into a clean 5 V gate signal for both MOSFETs. Must be AHCT, not HC. |
| 14 | 2 x IRLZ44NPBF N-MOSFET | [Vetco, VUPN1682](https://vetco.net/products/vupn1682_mosfet_mosft_for_micro_controllers_-_30v_-_60a_-_irlb8721pbf_d151) | $5.34 | Exact part: IRLZ44NPBF, TO-220. The page's URL and title are out of date, but its detail table names the IRLZ44NPBF. Check the IRLZ44N marking on the part. |
| 15 | Small parts | Vetco | $24.47 | 2 x NTE585 and 1 x NTE586 (3 A/40 V) diodes; resistors 2 x 10 kΩ, 2 x 4.7 kΩ, 1 x 3.3 kΩ, 1 x 100 kΩ, 1 x 22 kΩ; 3 x 0.1 µF ceramic and 1 x 2200 µF/25 V capacitors; a DIP-14 socket; a breakaway header and a shunt for JP1; the 5 x 7 cm protoboard, 22 AWG stranded wire and 1/8" heat-shrink. |
| 16 | Power switch | [Vetco 30-10005, SPST mini toggle with leads](https://vetco.net/products/30-10005_spst_miniature_toggle_switch_w-wire_leads_on-off_6a) | $4.95 | On-off, 1/4" bushing (6.5 mm panel hole), 6 A at 12 V. |
| 17 | M3 screws and nuts | Tacoma Screw, by the piece ([or the Amazon M3 kit, B0HKFCTLK8](https://www.amazon.com/dp/B0HKFCTLK8), $8.99, which has no countersunk screws) | ~$12 | 4 x M3x6, 17 x M3x8, 8 x M3x8 flat-head (countersunk), 6 x M3x10, 11 x M3x12, 14 nuts. They go into the 32 heat-set inserts (item 10), except the 3 thumbscrews, the 5 lock screws and the 6 handle lap screws, which use the 14 nuts. |
| 18 | Compression spring | Ace Hardware, Hillman spring drawer (bring calipers) | ~$1.50 | About 0.4-0.5 mm wire, 5 mm outside diameter, ~10 mm long (cut a longer one down). A retractable pen's spring also fits but is softer. |
| 19 | Straps and zip ties | Hardware store: VELCRO One-Wrap roll, 3/4" x 12 ft, model 90340 (Kevin has it), plus ~10 small zip ties (2.5 mm wide) | ~$9 | Cut the roll into 4 straps: two for the pump, one for the jar, one for the battery. The battery strap's lower run sits in a 2 mm recess under the tray, so it must be no thicker than 2 mm (One-Wrap measures about 1 mm). The zip ties hold the LM2596 and tidy the cables. |
| 20 | Curtain sheet | Target, Fred Meyer, Office Depot (school aisle): one clear-frosted polypropylene folder, binder divider or report cover | ~$3 | Polypropylene flexes thousands of times, lets the light through and hides the inside. One sheet makes the curtain (13 strips 12 x 97 mm). 0.3-0.5 mm; thinner parts more easily. Not PVC/vinyl, which cracks at the folds. |
| 21 | Food-safe jar | Kevin has one: a Ball 8 oz quilted jelly jar (Fred Meyer and Target sell 12-packs) | ~$5 | **No bigger than 73 mm across and 108 mm tall, lid included**; Kevin's measures 73 x 100-105 mm. Holds ~200 mL usable, 5-6 pours. The lid must be drillable. |
| 22 | Shot glass, 1.5 oz | Kevin has one (48 mm across, 60 mm tall); otherwise Bargreen Ellingson or any kitchen store | ~$4 | **Up to 52 mm across the top and 62 mm tall** (Libbey 1.5 oz glasses fit). About 1.3 cm of it stands above the slot for your fingers; a heavy base helps. |
| 23 | Super glue | the Gorilla Glue super glue you already have (any cyanoacrylate works) | - | For the magnets, the nuts, the Hall sensor and a few dots on the diffuser. |

> **No charge jack.** There is nothing to buy for charging. The battery's supplied splitter is "1 female to 2
> male", with all three ends joined. One male plug stays in the battery, the other is cut off to make the lead to the
> board, and the charger plugs into the female end with the lantern lifted off (section 4 step 2, section 12). The
> deck's 11.3 mm hole stays empty, so a jack can be added later.

**Total: about $206 before tax** (2026-10-21, from the Sheet):

| Store | Total |
|---|---:|
| Amazon (items 1-10) | $127.99 |
| Vetco (items 11-16) | $43.69 |
| Tacoma Screw (item 17) | ~$12 |
| Hardware store (straps, zip ties) | ~$9 |
| Ace and local (spring, curtain sheet, jar, shot glass) | ~$13.50 |

The total assumes you already have:

- **PETG filament.** About 1.2 kg of green at the settings in section 3 (two 1 kg spools: the second covers the
  rest, the supports and one failed big part), ~30 g of white or natural for the diffusers, and under 1 g of white
  for the ring's emblem outline (~$49 for two green spools and one white).
- **Basic tools:**
  - soldering iron and solder, multimeter, calipers, wire strippers, a heat gun or lighter;
  - a drill with 3.2, 5 and 6 mm bits, flush cutters, pliers or a small wrench for the switch nut;
  - a 2.5 mm hex key (a long or ball-end one, for the sphere's flange screws and the handle) and a 2 mm hex key for
    the countersunk screws;
  - a small flat screwdriver for the LM2596's trimmer, a hobby knife and a ruler;
  - a USB-C data cable and a laptop with the Arduino IDE for the XIAO;
  - a kitchen scale or measuring cup for calibration (1 g of water = 1 mL).
- **Supplies:** a dab of silicone grease or petroleum jelly for the lock's ramp and plunger, double-sided tape for
  the curtain, ~220 grit sandpaper.

### 2.3 Seattle-area stores (verified open on 2026-10-11; call before driving for specific stock)

| Store | Address, hours | Buy here |
|---|---|---|
| [Vetco Electronics](https://vetco.net) | 12718 Northup Way STE 100, Bellevue 98005, (425) 641-7275. Mon-Fri 9-6, Sat 10-3:30 | The A3144, MOSFETs, diodes, resistors, capacitors, protoboard, IC socket, wire, heat-shrink, power switch and the two JST plugs. Not stocked: XIAO, magnets, check valves. |
| [Tacoma Screw Products, Ballard](https://www.tacomascrew.com/LocationFinder) | 3930 Leary Way NW, Seattle 98107, (206) 632-7565. Mon-Fri 7-5, Sat 9-1 | M3 screws and nuts by the piece, springs. Georgetown branch: 1121 S Bailey St, Mon-Fri 7-5. |
| [McLendon Hardware](https://www.mclendons.com/locations) | White Center: 10210 16th Ave SW, Seattle 98146. Renton: 440 Rainier Ave S | Spring drawers, metric screws, glue. |
| Ace Hardware (Magnolia, Maple Leaf, West Seattle Junction), Stoneway Hardware | Seattle neighbourhoods | The lock spring (Hillman spring drawer), fasteners by the piece. |
| Target, Fred Meyer, Office Depot/OfficeMax | Several in Seattle | The curtain sheet: a clear-frosted polypropylene folder or divider (school aisle). Home Depot has no good match. |
| Petco, PetSmart, aquarium shops | Several in Seattle | A single aquarium check valve, if you skip the Amazon 10-pack. |
| [Bargreen Ellingson](https://www.bargreen.com/locations/seattle) | SoDo showroom, Mon-Fri 10-3 | 1.5 oz shot glasses. |
| [Micro Homebrew](https://www.microhomebrew.com/) | Kenmore, (425) 892-8425 | Small food-safe bottles and jars. They do not stock the 1/8" pump tubing. |

Hardwick's in the U-District closed in 2020. Sound Homebrew Supply could not be confirmed open.

---

## 3. Print the parts

All files are in `cad/output/` (STL for slicing, STEP for editing).

- **What to print:** the 26 parts in the [part list](#part-list) below, plus `ring_sizer` first. Print `key_cap`
  only if you use a bought ring instead of `key_ring`. `assembly.stl` and the `*_envelope.stl` files are check
  volumes, not parts.
- **Bed size:** everything fits your 230 x 230 x 240 mm Ender 3. The widest part is the rear sphere half at
  221 mm (because of the handle bosses); the tallest is the base at 147 mm. Centre the big parts.
- **Adhesion:** a skirt is enough, except for the two sphere halves and `dish_lower`, whose first layer is only a
  2.4 mm ring: give those a 6 mm brim.

### PETG settings (0.4 mm nozzle)

| Setting | Value |
|---|---|
| Layer height | 0.2 mm |
| Nozzle / bed | 235-245 °C / 75-85 °C |
| Walls | 4 perimeters, 5 top and 5 bottom layers |
| Infill | 25-30 % gyroid (100 % for the two diffusers) |
| Outer wall speed | 40-60 mm/s |
| Fan | off for the first 3 layers, then 30-50 % |
| Bed surface | textured PEI, or glue stick on smooth PEI |
| Elephant-foot compensation | 0.2 mm (Cura: Initial Layer Horizontal Expansion -0.2) |

- **Why the elephant-foot setting matters:** the spigots, the locating rings and the drum's bore all mate on their
  first layers with 0.3 mm of clearance a side, and a flared first layer on both parts eats that. If a ring still
  binds, sand the smaller part's edge.
- Turn "print thin walls" on for `socket_base` (the sensor post's walls).
- Do not anneal.

### Heat-set inserts

Install the brass inserts before assembly.

- All 32 receiving holes are **4 mm across × 6.5 mm deep**. The listed ruthex RX-M3x5.7 (5.7 mm long, 4.6 mm across,
  made for a 4.0 mm hole) or any plain M3 x 5.7 x 4.6 mm brass insert fits; a 5 mm-wide "M3 x 4 x 5" insert does not.
- Test one in a scrap print first, at the supplier's installation temperature.
- Fit each flush with the entry face, let it cool, and check that a screw turns freely before mounting anything.
- The 3.4 mm screw through-holes, countersinks and captured-nut pockets are separate features: no inserts there.
- **The bay floor's insert needs its boss glued on first.** The 2 mm floor is too thin to hold an insert, so its bore
  carries on into `guide_boss`, a small separate puck (printed apart so the floor prints flat without supports):
  1. Put a thin ring of super glue round the boss's open (bore) face and press it onto the underside of the floor
     (the side without the lip), over the insert hole near the tube hole.
  2. Line the two bores up with a 4 mm drill bit pushed through both, and hold it until the glue sets. Pull the bit
     out.
  3. Stand the floor on the boss on the bench (prop the far edge level on a book) and set the insert from the top,
     through the floor and into the boss. Pressing pushes the two parts together, and the insert locks them. In the
     lantern the nozzle guide's screw pulls the boss up against the floor too.

| Printed part | Inserts | Entry side |
|---|---:|---|
| `base_tray` | 3 | Tops of the deck-support pillars |
| `base_deck` | 4 | Faces of the circuit-board mounting pads |
| `dish_lower` | 6 | Outside faces of the two rings, three per ring |
| `dish_upper` | 11 | Four top-diffuser holes, three outer radial holes, four underside curtain-clamp holes |
| `sphere_front` | 4 | Split-face bosses |
| `sphere_rear` | 2 | Inner walls of the two handle sockets; insert before fitting the legs |
| `bay_floor` + `guide_boss` | 1 | Top face, under the nozzle-guide foot, through the floor into the glued-on boss (below) |
| `socket_housing` | 1 | Open back, beside the switch cavity |

### Test prints (before any big part)

1. **Size the ring.** Print `ring_sizer.stl` (ten labelled test bands, 18.5–23 mm, ~12 g, no supports).
   - Pick the band that slides over the knuckle of your left middle finger with slight resistance.
   - Set `RING_ID` in `cad/params.py` to that size **plus 0.5 mm** (the ring's band is much wider than the test
     bands, so it fits tighter) and re-run `python3 build.py`.
   - Print `key_ring`. It should slide onto your finger past the knuckle; its raised emblem drops into the rotor's
     emblem-shaped pocket (bars level, either way up) and turns the rotor, with a little play. If the finger hole is
     wrong, change `RING_ID` again and reprint (about 9 g).
2. **The lock:** `socket_housing`, `rotor`, `socket_base`, `plunger`. The rotor turns 45 degrees with slight drag
   and the plunger snaps it back. If it binds, raise `FIT` in `cad/params.py` by 0.05 and reprint the rotor.
3. **The glass:** `glass_well` with your real shot glass. The glass slides the length of the slot, clicks over the
   ridge at the far end, and comes back out. If it is wider than 52 mm at the top it won't fit; pick another glass.
4. **The other sliding fits**, each as soon as both parts exist:
   - `base_tray` up into `base` (sand the tray's edge, not the drum, if it binds);
   - `dish_lower`'s spigot into the top of `base` (the tightest joint);
   - `socket_housing` into the floor hole of `dish_upper`;
   - `glass_well` into `bay_floor`'s slot;
   - a handle leg into a boss of `sphere_rear`, before you print the arcs.
5. **Hand check (optional).** The CAD clears a fist 106 x 76 mm (yours is under 4 x 3 in). To be sure before the
   big prints, cut a 120 x 96 mm hole in a box and punch through it with a shot glass held under your fist. Both
   must pass without scraping.

### Part list

| Part | Size (mm) | Orientation on the bed | Supports | Colour | ~g |
|---|---|---|---|---|---|
| `base` (drum) | 190 x 190 x 147 | top band down | no | green | 280 |
| `base_tray` (cartridge floor, with the switch pocket and LED slot) | 179 x 179 x 44 | flat | no | green | 91 |
| `base_deck` | 179 x 179 x 47 | flat | under the four electronics mounting pads; remove fully before fitting board | any | 111 |
| `thumb_knob` (print 3) | 10 x 10 x 6 | flat | no | any | 1 |
| `dish_lower` | 190 x 190 x 91 | mouth down | the 2.8 mm ring under the rim, 8 mm up: supports touching the build plate only | green | 184 |
| `dish_upper` | 180 x 180 x 86 | floor down, mouth up | the 2.7 mm ring under the floor, 9 mm up: supports touching the build plate only | green | 220 |
| `top_diffuser` | 100 x 100 x 3 | flat (countersunk) face down | no | white | 19 |
| `sphere_front` (display side) | 180 x 117 x 80 | split face down, dome up | inside only, around the window (tree) | green | 72 |
| `sphere_rear` (your side) | 221 x 117 x 76 | split face down, dome up | inside only, around the hand opening (tree) | green | 69 |
| `diffuser` | 118 x 98 x 1 | flat, 100% infill | no | white | 13 |
| `lock_wall` | 120 x 102 x 36 | front face down, posts up | no | white or any | 23 |
| `curtain_clamp` | 115 x 38 x 3 | flat | no | green | 3 |
| `bay_floor` | 131 x 131 x 4 | floor down, drip lip up, as exported | no | any | 21 |
| `guide_boss` (glued under `bay_floor`) | 8 x 8 x 6 | bore up, as exported | no | any | <1 |
| `glass_well` | 64 x 93 x 52 | floor down, flange up | no | any | 38 |
| `nozzle_guide` | 47 x 17 x 34 | foot down, as exported | a small tree support under the end of the bend | any | 3 |
| `handle_leg_left` | 14 x 126 x 10 | flat | no | green | 17 |
| `handle_leg_right` | 14 x 126 x 10 | flat | no | green | 17 |
| `handle_arc_left` | 120 x 132 x 10 | flat | no | green | 25 |
| `handle_arc_right` | 120 x 132 x 10 | flat | no | green | 25 |
| `socket_housing` | 76 x 76 x 10 | ring face down | no | green | 32 |
| `rotor` | 44 x 37 x 8 | bottom face down (skirt on the bed, key pocket up) | no | green | 7 |
| `socket_base` | 95 x 79 x 7 | bottom face down, sensor post up | no | any | 18 |
| `switch_bracket` | 23 x 10 x 7 | flat, pegs up | no | any | 1 |
| `plunger` | 5 x 5 x 4 | nose up | no | any | 1 |
| `key_ring` | 27 x 27 x 34 | emblem down, as exported | under the head (around the emblem, touching the plate) and inside the finger hole | white for 3 layers, then green (below) | 8 |
| `key_cap` (only for a bought ring) | 24 x 24 x 6 | glue face down, emblem up | no | green | 2 |
| `ring_sizer` (test print, ten bands) | 196 x 61 x 8 | flat | no | any | 12 |
| **Total** | | | | | **~1240 g** |

**Supports.** None, except:

- **Inside the two sphere halves.** Print them split-face down; the last 15 mm of dome around the window and the
  hand opening overhang more than 45 degrees, so enable tree supports on the inside only.
- **Under the two dishes' bearing rings.** They start in mid-air 8-9 mm up; "touching build plate only" support is
  a short ring that pulls off clean.
- **Under the nozzle guide's bend.** It prints foot down, and the last 45 degrees of its bend hang past horizontal,
  so give it a small tree support there.
- **Under the key ring's head and inside its finger hole.**

**Colours.** Print both diffusers (`diffuser`, `top_diffuser`) in white or natural PETG at 100 % infill; green works
but is dimmer. A white `lock_wall` reflects more light out of the hand opening.

**Weights.** The grams column assumes the settings above: the parts are mostly wall, so count about 1.1 g per cm³
(the diffusers are solid).

### The ring's white outline

`key_ring` prints emblem down. Its first 0.6 mm (three 0.2 mm layers) are only the faces of the emblem's circle and
bars; the centre disc starts at 0.6 mm. So a filament change after layer 3 gives a white emblem outline on a green
ring:

1. Start the print with **white** PETG loaded.
2. Add a filament change before **layer 4 (Z 0.8 mm)**: in Cura, Extensions > Post Processing > Filament Change at
   layer 4; in PrusaSlicer or Orca, the "+" on the layer slider at 0.8 mm. Both insert `M600`; if your firmware
   lacks it, use "Pause at height" and swap by hand.
3. When the green goes in, push it through until it runs clean green, with no white streaks, and wipe the nozzle:
   the first green layer is the visible centre disc.
4. Three layers of white over green can look pale mint. Let the first ring run about 1.5 mm past the swap, cancel
   it and look at the emblem before printing the whole ring.

The magnet ends up behind green plastic. A plain green ring (no swap) works the same in the lock.

![key_ring with a white emblem outline](images/ring-white-outline.png)

![all printed parts](images/cad-parts-sheet.png)

![assembly](images/cad-assembly-iso.png) ![cutaway](images/cad-cutaway.png)

---

## 4. Electronics (build it on the bench first)

![wiring diagram](images/wiring.png)

Build the circuit on the 5 x 7 cm perfboard and test it before anything goes into the lantern.

- Follow the [two-sided perfboard layout](review/protoboard/README.md) and its
  [wire-by-wire solder schedule](review/protoboard/WIRE_SCHEDULE.md). The rear view is mirrored; pad names stay
  the same.
- Check the actual hole-array position and C2 case size before you start.
- Read [USB programming and calibration power](#usb-programming-and-calibration-power) before you plug in USB.

1. **Board, XIAO and U1.**
   - Orient the perfboard 70 mm across and 50 mm tall.
   - Drill four 3.2 mm holes at (x, y) = (18, 17), (55, 15), (15, 45) and (58, 45) mm from the component-side
     top-left corner (the [board layout](review/protoboard/README.md) is the reference). Check them against the
     printed panel first, and keep each 9 x 9 mm mounting area clear.
   - Fit the XIAO and a **DIP-14 socket** for U1; leave U1 out for the first USB flashing.
   - Fit a two-pin 2.54 mm header for JP1 and label it **REMOVE FOR USB**.
2. **Battery lead, charge socket and S1.** The supplied TalentCell splitter is "1 female to 2 male", with all three
   ends joined. With the battery and the charger unplugged:
   - One **male** plug stays as it is: it goes in the battery's port.
   - Cut the other **male** plug off, leaving its lead long: that is the battery lead to the board.
   - The **female** end stays as it is: that is the **charge socket**. The charger plugs in here and charges the
     pack through the splitter, with nothing to unplug (section 12).

   Then:
   - Do not cut or open the pack. Find centre-positive and sleeve-negative with the meter's continuity setting; do
     not trust the wire colours.
   - Plug the splitter into the pack, turn the pack's switch ON, and confirm 9–12.6 V and the polarity on the cut
     lead and at the female end. Unplug again before soldering.
   - Positive goes to S1. S1's other terminal is **VLOAD**, the switched battery rail. Negative goes to the common
     ground.
   - Solder **C2 2200 µF/25 V** from VLOAD to ground, positive to VLOAD. It smooths short dips; it cannot carry an
     overloaded or stalled motor.
3. **Battery sense.** R1 100 kΩ from VLOAD to D0; R2 22 kΩ and C1 0.1 µF from D0 to ground. At a full 12.6 V pack,
   D0 sees 2.27 V. Keep this wire away from the motor wiring.
4. **Buck converter (set its output first).**
   - Connect only LM2596 IN+ to VLOAD and IN− to ground; leave OUT unloaded.
   - Turn the pack and S1 on. With the meter on DC volts across OUT+/OUT−, turn the trimmer until it reads
     **5.0 V**. Switch off before attaching anything else.
   - OUT+ is **+5V_REG**: U1 and the Hall sensor connect straight to it.
   - The XIAO's 5V pin is fed through **D1 NTE585** (stripe toward the XIAO), then **JP1** in series. Grounds stay
     connected even with JP1 removed.
   - D1 stops current flowing back into the buck, but it does not protect the USB host from battery power:
     **remove JP1 before connecting USB**.
5. **U1 (74AHCT125).** Use **74AHCT125**, not 74HC125.
   - Pin 14 to +5V_REG, pin 7 to ground. Solder **C3 0.1 µF ceramic** straight across those pins with short leads.
   - Ground all four output-enable pins (1, 4, 10, 13) and the unused inputs (9, 12); leave the unused outputs
     (8, 11) unconnected.
   - XIAO D3 goes to pin 2 (pump); D4 goes to pin 5 (light). R3 and R4, **10 kΩ**, go from those two inputs to
     ground.
   - Check the socket notch against the [DIP-14 pinout](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf) before
     inserting U1, with all power disconnected.
6. **MOSFETs (IRLZ44NPBF).** Label facing you, leads down: pin 1 gate, pin 2 drain (also the tab), pin 3 source.
   - U1 pin 3 goes straight to Q1's gate (pump); U1 pin 6 straight to Q2's gate (light).
   - Both sources go to ground.
   - Pump negative to Q1's drain, strip negative to Q2's drain; both loads' positives to VLOAD.
   - Run the pump and strip returns separately to the common power ground; don't route their current through the
     Hall/XIAO ground wiring.
7. **Pump flyback diode.** D2 **NTE586, 3 A/40 V**, straight across the pump terminals: stripe (cathode) to VLOAD,
   anode to Q1's drain. Do not use the 1 A NTE585 here.
8. **Lock wires.**
   - **Hall sensor (A3144)**, printed face toward you, leads down: pin 1 to +5V_REG, pin 2 to ground, pin 3 straight
     to XIAO D1. R5 **4.7 kΩ from D1 to XIAO 3V3**, never to 5 V. Its open-collector output needs no series diode.
   - Fit **C4 0.1 µF across sensor pins 1 and 2, at the sensor**, below its mounting pocket, with insulated leads.
   - **Microswitch (D2F-01L):** COM to ground, NO to the SW wire, NC unused.
   - On the board: R7 **3.3 kΩ** from +5V_REG to SW; R6 **4.7 kΩ** from XIAO 3V3 to D2;
     **D3 NTE585, anode to D2, stripe (cathode) to SW**.
   - How it works: closed contacts pull D2 low; open contacts leave D2 at 3.3 V while the switch side rises to 5 V.
     R7 puts about 1.5 mA through the closed contacts (the D2F-01L needs at least 1 mA) and R6 adds about 0.6 mA.
     The firmware's internal pull-ups can stay on alongside R5 and R6.
   - **Lock cable:** 4 wires, **+5V_REG, HALL, SW, GND**, about 45 cm, with the JST PH plug about 10 cm from the
     board. R5–R7 and D3 stay on the board.
   - **Do not solder the Hall sensor to the cable yet:** its leads must first pass through the sensor post's slot
     (section 6). Clip it on temporarily for the bench checks. Solder the switch wires before mounting the switch.
   - **LED lead:** VLOAD and Q2's drain, through the JST SM pair; leave the far end bare until section 8.
   - Thread the lantern-side wires through the bay-floor hole before fitting the plug housings.
9. **Commission it before assembly.** Flash it using the power procedure below.
   - **Without loads** (pump and strip disconnected), in USB calibration mode:
     - +5V_REG at U1 and at the Hall sensor reads 5.0 V;
     - GPIO D1 and D2 read about 3.3 V when open and below 0.8 V when active;
     - `status` follows the magnet and the twist every time, including with the cable moved;
     - the battery reading matches the meter within 0.2 V after `vcal`;
     - both MOSFET gates are low at idle.
   - **With loads:** connect the pump and strip with the power off. With a fully charged pack and the real strip
     length:
     - check full brightness, current and heating (`idle 255` for 100 % PWM, then `idle 0` and `save`);
     - measure current **in series**, with a suitably rated, fused meter; never put a meter in current mode
       across the battery;
     - run short water pours with the LEDs on and measure the combined running current (the estimate is ~1.3 A,
       not a measured figure; a normal meter may miss start-up peaks);
     - watch for resets, protection trips and hot wiring or MOSFETs. Stop and investigate overheating, a stall
       or a trip; never stall the pump on purpose.
   - Every power-up must leave the pump off. The brief LED blink at boot is intentional.

### USB programming and calibration power

Normal operation is battery-only. Two rules always apply:

- **Never attach USB with JP1 fitted.** JP1 isolates only the XIAO's supply.
- **Never move JP1 or insert or remove U1 with power connected.**

There are three power modes:

| Mode | When | Sequence |
|---|---|---|
| **USB-only flashing** | The very first upload, before the buck is set | S1 OFF, pack unplugged, JP1 removed, **U1 out of its socket** (that also disconnects the XIAO's outputs from the unpowered buffer). Connect USB, upload, unplug USB, then refit U1. No load tests in this mode. |
| **USB calibration and testing** | `status`, `cal`, `vcal`, priming, cleaning | With all power off, remove JP1. Turn the pack and S1 ON, check +5V_REG, then connect USB: USB powers only the XIAO and the buck powers U1 and the Hall sensor. To attach the pump and LED leads, power down (USB out first, then S1 OFF), connect them, and repeat. Finish with `stop`, unplug USB, then S1 OFF. Refit JP1 only after USB is unplugged and the power is off. |
| **Battery operation** | Normal use | USB unplugged, U1 in, JP1 fitted. Pack switch ON, then S1 ON. |

- **S1 is the on/off switch.** The pack's own switch stays ON: it has no hole in the floor and is reached only with
  the lantern lifted off (at the battery's end, under the deck's edge).
- **Storage:** S1 OFF. For more than a few weeks, also turn the pack switch OFF the next time the lantern is lifted
  off.
- If the pack trips or +5V_REG fails during USB testing, unplug USB at once and find out why before retrying.

An optional PRIME button goes between D6 and ground. Holding it runs the pump only when no ring is in.
It's not in the parts list; the serial `cal` command or a test pour does the same job.

---

## 5. Firmware

Source: `firmware/green_lantern/green_lantern.ino`. Board: Seeed XIAO RP2040 on the "Raspberry Pi
Pico/RP2040" Arduino core by Earle Philhower. No extra libraries.

**First follow section 4's USB power procedure.**

**Arduino IDE.** Boards Manager: install "Raspberry Pi Pico/RP2040" (Earle Philhower). Select "Seeed XIAO
RP2040", open the sketch, upload. If no port appears, hold the XIAO's BOOT button while plugging it in.

**Command line.**

```bash
cd firmware
arduino-cli core install rp2040:rp2040 --additional-urls https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
arduino-cli compile --fqbn rp2040:rp2040:seeed_xiao_rp2040 green_lantern
arduino-cli upload  --fqbn rp2040:rp2040:seeed_xiao_rp2040 -p /dev/ttyACM0 green_lantern
cd test && make test     # 20 simulated scenarios, all must PASS
```

![state machine](images/state-machine.png)

| Pin | Function |
|---|---|
| D0 | Battery sense (100 k / 22 k divider from the switched +12 V) |
| D1 | Hall sensor OUT (LOW = ring present) |
| D2 | Microswitch NO (COM to GND) |
| D3 | Pump, through U1 to Q1 |
| D4 | LED strip, through U1 to Q2 |
| D6 | Optional PRIME button to GND |

Serial console at 115200 baud. Type a command and press Enter:

| Command | What it does |
|---|---|
| `status` | Shows state, ring, switch, pump, pour time, speed, brightness, idle glow, battery voltage. |
| `cal 10000` | Runs the pump 10 s without the ring, for calibration (refused while a pour is running). |
| `pour 11000` | Pour time in ms (500 to 20000): the length of the light build-up. |
| `speed 70` | Pump speed in percent (30 to 100): sets how much is poured in that time. |
| `leds 255` | Maximum LED brightness, 0 to 255. |
| `idle 0` | Glow when idle, 0 to 255 (default dark). |
| `vcal 12.31` | Tells it what your meter reads across the pack, to calibrate the battery reading. |
| `save` | Stores pour time, speed, brightness, idle glow and the `vcal` correction so they survive a power cycle. |
| `stop` | Stops the pump now. |

The light levels live near the top of the sketch: `ARMED_LEVEL` (15 %), `POUR_PEAK` (90 %), `EARLY_BUMP`
(10 %) and the finale timings (0.4 s swell, 0.3 s hold, 1.2 s fade). They are perceived brightness, so the
climb looks steady to the eye.

**Safety interlocks, all tested in simulation:** pump off at boot. The switch alone never pumps; the ring
alone never pumps. The pump runs only while the twist is held. One pour per insertion; letting go early
does not resume. Pulling the ring mid-pour stops the pump within about 60 ms. A
switch already pressed at boot or at insertion is ignored until released. A 20 s hard cap applies to every
pump run.

---

## 6. The lock

![socket mechanism](images/socket-mechanism.png)

Parts: `socket_housing`, `rotor`, `socket_base`, `switch_bracket`, `plunger`, `key_ring`. Plus 3 x M3x8 flat-head and 3
nuts for the base plate, 1 x M3x8 flat-head for the switch bracket, 2 x M3x10 and 2 nuts to mount it on the
lock wall, the spring, the microswitch, the A3144 and one magnet.

The lock is screwed to the face of the lock wall with its ring pocket facing you, so you seat the ring by
punching in. The rotor is a flat 36 mm disc. Under the housing's front lip its edge carries three features: a
stop lug in a channel whose ends are the 0 and 45 degree stops, a cam that presses the switch lever 3 mm
from about 30 degrees to the stop, and a ramp that pushes the spring plunger out so the rotor snaps back when you let go.

1. **Nuts.** Drop M3 nuts into the three hex pockets on the underside of `socket_housing`. A dab of super glue
   holds each.
2. **Ring.** `key_ring` is the ring and the lock's key in one print.
   - **How it keys.** Its raised Green Lantern emblem (the circle and two bars, 4 mm proud, faces printed white:
     section 3) is the key. The rotor's pocket is the emblem's negative, so the bars turn the rotor when you twist.
     There is no tab.
   - **Find the magnet's switching face.** The A3144 reacts to one magnet pole only. With the sensor wired to the
     board (section 4) and `status` running, hold each face of the magnet to the sensor's printed face. The face
     that gives `ring=present` goes **down**, toward the ring's face. Mark it.
   - **Glue the magnet in.** The pocket opens inside the band, so the magnet never shows. Put a drop of super glue
     in the pocket from inside the band, push the magnet to the bottom with a hex key, and let it set before you
     wear the ring. It sits behind the centre disc under 0.6 mm of plastic, about 3.7 mm from the sensor: about
     53 mT at the worst rotor position, against the A3144's 35 mT maximum switch point.
   - **Wear it on your left middle finger.** Make the fist you will punch with, ring face forward, palm down: the
     emblem's bars lie level, which is how the pocket sits at rest, and the twist is counterclockwise as you see it
     (your thumb rolls up). `LOCK_TWIST = 'cw'` in `cad/params.py` gives a clockwise version.
   - **Bought ring instead:** print `key_cap` (a 24 mm disc carrying the same raised emblem). Glue the magnet into
     the pocket in its flat top, switching face toward the emblem, then glue that flat top onto a ring face at
     least 24 mm across, with the bars across the finger.
3. **Hall sensor.** `socket_base` has a short round post in the middle with a small pocket on its tip. Bend
   the A3144's three leads 90 degrees right at the body, toward its unprinted back, so that with the printed
   face up they point straight down; feed them down the slot at the pocket's edge and out through the bottom
   of the plate, and lay the sensor in the pocket **printed face up** (flush with the top). A dot of glue holds
   it. Cut the three leads to different lengths under the plate, solder the cable to them and sleeve each joint:
   staggered, the sleeves fit side by side in the wall's window. The rotor turns
   around the post; the magnet ends up about 3 mm above the sensor. Fit C4 across pins 1 and 2 below the pocket,
   insulate it and secure it so it cannot obstruct the rotor or the cable slot.
4. **Rotor and plunger.** Turn `socket_housing` upside down. Smear a little silicone grease or petroleum jelly
   on the rotor's rim (the ramp and the cam), the plunger's nose and the bore: dry PETG on PETG has about the
   same friction (0.3-0.4) as the ramp's slope (0.26), so an unlubricated rotor can sit at 45 degrees instead
   of returning; greased (about 0.1) it returns. Lay the spring in the open radial trough at the rim, closed end
   outward, then the `plunger` between the spring and the bore, flat end on the spring, rounded nose toward
   the bore. Hold it with a finger and lower the `rotor` into the bore, stop lug down into
   its channel (it fits one way only). Twist to 45 degrees and let go: it should snap back every time. If it
   only creeps back, add grease. It doesn't matter for the show either way: you turn the ring back yourself on
   the last word, and the firmware only watches the switch. Too stiff to twist with a finger: use a softer
   spring (0.4 mm wire).
5. **Switch.** With its two wires already soldered on (section 4 step 8), press the microswitch onto the two
   pegs of `switch_bracket`, lever toward the rotor, and lay the bracket in its recess in `socket_base`, its
   round hole over the slot at the lever end. Lead the two wires out through the notch in the plate's rim at
   the bottom (the plate has a matching notch; in the lantern it faces down).
6. **Close and tune.** Screw `socket_base` onto the housing: 3 x M3x8 flat-head up from below into the nuts, and
   a 4th flat-head up through the slot and the bracket into the housing, left loose. All four heads sit flush,
   so the plate lies flat on the lock wall later. Twist slowly: the lever should start to move at about 30
   degrees and click at about 40, before the stop at 45. To tune, loosen the 4th screw and push it along its
   slot (it carries the bracket, 1 mm either way), then tighten. The switch must never be what stops the rotor.
7. **Cycle it 50 times** and watch `status`: `switch=pressed` only near the end of the twist, `ring=present`
   for the whole twist.
8. **Mount** it on the face of `lock_wall` (section 8): the two ears go down, one M3x10 through each ear and
   the wall, nut on the back. The lock cable passes through the wall: the sensor's three joints through the
   rectangular window behind the lock, the switch wires through the small window under it, where the plate's
   rim notch lands. Leave the cable long enough to reach the base (about 45 cm).

---

## 7. The fluid path

1. **Jar lid.** Drill a 6 mm hole near the edge and push the tube through it (it seals itself) until it reaches
   5 mm above the jar's bottom. **Vent:** the check valve's barbs are made for 3/16" airline, wider than the pump
   tube, so the valve gets its own hole on the opposite side. Measure the barb (about 5 mm), drill the hole to
   that size, push the valve's lower barb through the lid from above until its ridge seats, with the arrow
   pointing **down into the jar**, and seal round it with a dab of super glue. Air gets in as the
   pump draws the drink out (without it the jar goes under vacuum and the pours shrink), but if the jar tips,
   nothing comes out. Blow through it to check: air goes in, not out. The valve stands about 25 mm above the
   lid. Put it on the side of the lid nearest the drum wall: over the middle and the outer side there are
   35-75 mm of room, but toward the lantern's centre the glass well hangs to about 27 mm above the lid.
2. **Pump head.** Open the Kamoer's head cap, lay the tube around the rollers, close the cap. Use one
   continuous piece of tube from the jar to the nozzle: no joints, nothing to leak.
3. **Route** (steps 3 to 5 describe the path; you thread it in section 9, steps 3 to 5, once those parts are
   in place). The pump sits in its saddles on the deck, head toward your side so you can open the cap later,
   held by two 20 mm straps through the deck's slots. The tube goes up through the lower dish neck and the tube hole in
   `bay_floor` (behind the lock wall, on your right as you look in), then through `nozzle_guide`.
4. **Nozzle.** The guide stands behind the wall and bends the tube up, over and **45 degrees down**. Its open
   side faces the wall, which holds the tube in. Leave 5 mm of tube sticking out of its end, cut square with a
   sharp blade. The tube end sits about 7 mm above the rim, over the back third of the glass, pointing down
   into it: the stream lands about 19 mm from the glass centre at any pump speed, and the last drop falls
   straight in. (A level tip would throw the stream sideways, onto the rim at the default speed.)
5. **Service loop.** Leave about 30 cm of extra tube between the pump and the bay floor, coiled loosely (no
   tighter than a 5 cm circle, or it kinks) in the space above the jar and pump. That slack lets you lift the
   lantern off the cartridge and set it down beside it without disconnecting the tube.
6. **Prime.** Follow section 4's USB calibration power sequence (JP1 removed); section 10 explains
   access to the XIAO. With water in the jar and the glass in its slot, run `cal 6000` until water reaches
   the nozzle. The tube stays full between pours. Unplug USB before switching S1 off.

---

## 8. The lock wall, the curtain and the top

![cutaway](images/cad-cutaway.png)

Cut the COB strip on its marked cut lines (every 25 mm) into 7 pieces: four of 10 cm, two of 5 cm and one of
25 cm. Every piece is wired in parallel: all + pads together, all − pads together. The 22 AWG wire is fine; mark
the + wires with a dot of paint or a bit of red heat-shrink (or buy a second colour). Direction doesn't matter
on a single-colour strip.

1. **Back of the wall (display window).** One 10 cm piece in each of the 4 channels on the back of
   `lock_wall`, LEDs facing out.
2. **Face of the wall (hand opening).** One 5 cm piece in each of the two vertical channels beside the lock. Pass
   their wires to the back through the small hole at the bottom of each channel.
3. **Lock.** Screw the lock onto the wall (section 6, step 8). Solder the wall's + and − to the LED lead you
   made in section 4 step 8 (its bare end), so it runs down with the lock cable.
4. **Top.** Stick the 25 cm piece around the inside of the hole in the floor of `dish_upper`, LEDs facing
   the centre: it goes once round (the hole is 25.1 cm around) and the hole wall is 8 mm tall, the same as the strip. Let their leads hang down from the display side
   of the hole, so they fall behind the lock wall. Screw `top_diffuser` into the counterbore above them
   (4 x M3x8 flat-head, from above).
5. **Curtain.** From one frosted sheet, cut 13 strips 12 mm wide and 97 mm long. Lay them side by side, each
   overlapping the next by 2 mm, along the curved `curtain_clamp`, and screw the clamp to the underside of
   `dish_upper`'s plug (4 x M3x8 into the four inserts that bracket one of the plug's three radial screw holes;
   that side faces the hand opening), the strips sandwiched between. A strip of double-sided tape or a few
   dots of glue on the clamp hold the 13 strips while you screw it. They hang down behind the hand opening once the dish is on.
6. **Display diffuser.** It sits on the ledge behind the window of `sphere_front`. A few dots of glue hold it.

---

## 9. Final assembly

Bottom to top. "Left" and "right" are as you see them standing at the hand opening, looking in.

1. **Cartridge.** Work through these in order:
   - **Tray.** Stand `base_tray` with the switch pocket (the raised box near the rim) toward you.
   - **Buck.** The LM2596 goes in its pocket on the right, on its four 2 mm printed corner supports, zip-tied
     through the slots beside it. Check that no solder joint on its underside rests on a support.
   - **Power switch.** S1 goes up into the pocket's ceiling from below, nut tight.
   - **Strap first.** Thread a 20 mm strap through both battery slots before fitting the pack. Its lower run sits in
     the recess under the tray and must be no thicker than 2 mm.
   - **Battery.** Push the splitter's male plug into the battery's port. Lay the TalentCell flat on its 1 mm printed bed, 7 mm toward
     you from the middle:
     - **LED face down**, the five fuel-gauge dots over the thin floor slot;
     - **connector and switch end away from you**, against the low end stop;
     - the plug's cord folded back in a U-turn over the plug. Plug and U-turn reach about 35 mm from the battery's
       end, which leaves ~6 mm to the drum wall.

     The [battery seat drawing](images/battery-seat.png) has the measurements. Turn the battery's own switch ON (it
     stays ON), then tighten the strap: the deck is 16 mm above the case and does not hold it down.
   - **Charge socket.** Tuck the splitter's female end beside the battery's end, where you can reach it with the
     lantern lifted off, and tie it to a floor tie slot so it can't fall into the pump's way.
   - **Leads.** Route and tie the battery lead along the tray edge to S1, clear of the retaining bosses. Bring the
     pack's and S1's leads up through the open notch at the deck's edge. (The deck's other slot is a closed hole, so
     a soldered lead can't be threaded through it later.)
   - **Deck.** Drop `base_deck` in on top: 3 x M3x8 into the three pillars that have holes (it fits one way). The
     deck's 11.3 mm hole, near its left edge, stays empty.
   - **Check the LEDs.** Turn the cartridge over and check that the battery's LEDs show through the slot.
   - **Jar.** Into its ring, with a strap through the finger slots.
   - **Pump.** Fit the tube now, while the cartridge is open: open the head, lay the continuous tube around the
     rollers and close the cap. Leave the outlet end free for threading to the nozzle later. Then seat the pump in
     its saddles, sliding it along until the silver motor rests in its curved cradle, and secure it with two straps.
   - **Board.** Remove all print support from the four board pads, then screw the board to the deck's vertical
     panel (4 x M3x6 through the holes you drilled). Clipped leads and rear wiring must stay within the 10 mm gap
     behind it (see the board guide's pad positions and wire layers). Keep the inline lock and LED plugs above the
     empty module pocket on the left, clear of the battery supports.
   - **Service check.** With the shell off you can reach JP1 and the pack switch. For pack service, undo the three
     deck screws.
2. **Drum.** Push an M3 nut into the slot in each of the 3 bosses inside the bottom of `base` (a dab of glue
   holds each). Push an M3x12 screw head-first into each `thumb_knob` from below and glue it. Then `dish_lower`:
   its spigot goes into the top of the drum, 3 x M3x8 from outside. The drum stays with the lantern from now on.
3. **Bay floor.** From here until step 9 the open drum has the tube and the cables coming out of its bottom, so
   stand the lantern on two blocks (a couple of books) to keep its rim off them.
   - Lay `bay_floor` on the lower dish's locating ring. The long slot points at you; the two short slots for the
     wall's tabs sit either side in the far half. The tube hole and the 7 mm cable hole are beyond the wall line:
     tube on the right, cables on the left.
   - The lock cable and LED lead already pass through the cable hole (section 4 step 8); their plugs go down
     through the lower dish to the board.
   - Take the free end of the tube coming from the pump on the cartridge, beside the shell. Leave about 30 cm extra
     between the pump and the bay floor for the service loop, then feed the end up through the lower dish neck and
     the tube hole in `bay_floor`. There is no connector at the floor.
   - Drop `glass_well` into the long slot, its ridge end toward the display side; it hangs from its flange.
4. **Nozzle.** Push the tube up through the hole in `nozzle_guide`'s foot and along the channel, pressing it
   in through the open side where it resists (the slit is a little narrower than the tube), so 5 mm sticks out
   past the end, pointing down. Screw the foot into the bay-floor insert (1 x M3x8), open side toward you,
   the curve reaching toward the middle. The glued-on boss below the floor fits the matching relief in the lower dish.
5. **Lock wall.** Stand the wall in its two slots, lock facing you. Its back closes the nozzle guide's open
   side; check the tube sits in the channel and its end still points down into the glass slot. Take up the
   slack in the lock cable and LED leads down through the cable hole.
6. **Sphere.** Slide `sphere_front`, with the diffuser in it, in from the display side until it sits on the
   lower dish and the wall's four posts touch the diffuser. Slide `sphere_rear` in from your side. The flange ring is inside
   the rear half, flush with the split: drive the 4 x M3x10 through it into the front half's bosses from inside,
   reaching in through the hand opening and the top opening with a ball-end or long 2.5 mm key (do this before
   the upper dish goes on). Then 3 x M3x8 through the lower joint into the dish's ring (the holes sit 3 mm above
   the sphere's flat; the heads stand a little proud on the curve, that is normal).
7. **Top.** Stand `dish_upper` (with the top diffuser, the LED ring and the curtain on it) beside the sphere
   and solder its ring's leads (~30 cm) to the wall's LED lead, sleeved. Then lower it onto the sphere so the
   curtain goes down behind the hand opening, feeding the slack down behind the wall, and screw it on, 3 x M3x8.
8. **Handle.** The part names are from the display side, so `handle_leg_left` goes on your right. Each leg
   plugs into a boss on the rear half, counterbore facing outward; one M3x12 each goes in horizontally through
   the round hole in the boss's outer wall, 6 mm into the leg's counterbore and on into the insert on the sphere
   side, pointing at the lantern's axis (a long 2.5 mm hex key). The two arcs lap-joint to the legs and to
   each other with 6 x M3x12 and nuts, left leg with left arc.
9. **Join the lantern and the cartridge.** Plug the lock and LED plugs together, coil the tube's slack above
   the jar, and lower the lantern over the cartridge. The three notches in the deck's edge and the three
   bosses inside the drum only line up one way. Tip the lantern a little and turn the 3 thumbscrews up into the
   bosses from underneath, finger-tight.

- Keep the pump wires twisted and away from the Hall and switch wires.
- **On and off:** tip the lantern and flip S1 in the pocket under the cartridge floor, on your side. It is out of
  sight from every angle.

---

## 10. Calibration

**Reaching the XIAO.** Its USB port is on the cartridge, under the lantern, so every `status`, `cal` and `vcal`
here, in sections 11 and 13 and on the day means: switch off, undo the 3 thumbscrews, lift the lantern off and
stand it beside the cartridge on two blocks (a couple of books), so the tube and the two cables run out under
the drum's rim without being crushed. The glass stays in the lantern under the nozzle; the 30 cm service loop
reaches.

**Follow section 4's USB calibration power sequence: JP1 removed, U1 installed,
regulated 5 V present before USB is connected.** Unplug USB before switching S1 off.

Water in the jar, the shot glass in its slot (only the shot glass fits under the nozzle; weigh what it pours on
a kitchen scale, 1 g = 1 mL, or tip it into a measuring cup). Connect USB serial using section 4's power procedure.

First the battery reading: measure across the pack (or the rail) with the meter, type `vcal` and that number
(for example `vcal 12.31`), then `status` should show the same. Type `save` to keep it.

The pour time is the length of the show, so set it first and then adjust the pump speed until that time
pours the amount you want.

```
pour 11000       the build-up lasts 11 s (match it to how long you hold the twist)
cal 11000        pours for 11 s at the current speed (70 %): measure the volume
speed 60         too much? lower the speed (too little? raise it) and run cal 11000 again
save             when it pours 30-37 mL (1 to 1.25 oz)
```

Then repeat with the real drink: liqueur is thicker than water and the nozzle is about 15 cm above the pump, so
expect a little less than with water. A 1.5 oz glass with 30-37 mL in it can be carried without spilling.

---

## 11. Test before the party

- [ ] Power on: dark, pump silent.
- [ ] Twist the empty lock: nothing.
- [ ] Insert the ring: the light fades up to a faint glow, no pump.
- [ ] Twist and hold: the pump runs the calibrated time while the light climbs; it stays bright after the pump stops.
- [ ] Let go: the rotor returns, the light swells to full and goes dark.
- [ ] Twist and hold again with the ring still in: nothing.
- [ ] New insertion, twist, let go after 3 s: the pump stops at once, the light swells a little and goes dark.
- [ ] Remove the ring and reinsert it, twist: one new pour.
- [ ] Pull the ring out mid-pour: the pump stops at once.
- [ ] 20 water pours in a row: every pour lands in the glass, no drips anywhere.
- [ ] Carry and tilt the lantern with water in it, then leave it 30 minutes: dry inside.
- [ ] On the day: `status` reads about 11.5 V or more (roughly half charge or better). Below that, charge first.
- [ ] `status` shows the battery voltage. With a pack below 10.5 V (or a bench supply set to 10 V), inserting the ring double-blinks before the glow.
- [ ] Lantern lifted off, S1 OFF, pack switch ON, charger in the splitter's female end: the charger's LED shows charging; tip the lantern and the battery's LEDs show through the floor slot.
- [ ] Push the empty glass in until it clicks, pour water, then take it out: grip, slide 3 cm toward you, lift, out through the curtain, without spilling.
- [ ] Your fist goes through the curtain and into the lock, and back out, without catching.
- [ ] With the lights on in a dim room, the curtain, the display window and the top all glow; you can't see the nozzle.

---

## 12. Performing it

### On the day

1. Charge if `status` reads below about 11.5 V (section 11).
2. Fill the jar with the real drink.
3. With the lantern still standing beside the cartridge (section 10), prime with `cal 8000` into the shot glass
   until the drink reaches the nozzle. The line is empty after cleaning; empty the glass as needed.
4. Put the lantern on and do one full test pour into the glass: the first pour of the night should not be the one
   in front of a guest.

### The performance

Set the lantern on a table with the hand opening toward you. Reach through the curtain, lower the empty glass
into the near end of its slot and push it all the way back until it clicks over the ridge: that is the pour
position, under the lock.

1. Make a fist (ring on your left middle finger) and punch in through the curtain, ring face first, until the ring
   seats in the lock. The lantern glows faintly.
2. Twist 45 degrees counterclockwise and hold it as you start the oath. The pump starts and the light begins to
   climb.
3. Keep holding through the oath. After about 11 seconds the pour is done; the light sits at 90 % until you
   turn back, so a longer oath is fine.
4. On the last word, turn back. The light swells to full and goes dark.
5. Draw your fist back a little and open your hand: the front of the glass is right under the lock. Grip it,
   slide it about 3 cm toward you, lift it straight up out of the slot and bring it out through the curtain.

### Charging

Nothing needs unplugging.

1. S1 OFF, USB unplugged.
2. Undo the 3 thumbscrews and lift the lantern off; the cartridge stays on the table.
3. Plug the supplied TalentCell 12.6 V charger into the splitter's female end, tucked beside the battery's end. The
   battery's own switch must be ON to charge (it stays ON).
4. The charger's LED is red while charging and green when done. A full charge takes about 6 h at 0.5 A.

**When to charge:** after every party, or whenever `status` reads below about 11.5 V (roughly half); the strip dims
as the pack drains. The battery's own charge-level LEDs show through the slot in the floor whenever you tip the
lantern. The double blink as you punch in (below 10.5 V) is a late warning. How voltage maps to runtime still needs
checking on the finished prop, so treat 11.5 V as a rough guide, not a precise fuel gauge.

### Refilling (about 2 minutes)

1. Switch off. Tip the lantern slightly and undo the 3 thumbscrews underneath.
2. Lift the lantern off by its handle and set it down beside the cartridge. The tube and the cables have
   enough slack; unplug the two cable plugs if you want the lantern completely free. The three knobs drop out
   of their wells once undone: keep them with the cartridge.
3. Undo the jar's strap and unscrew the lid; the pickup tube comes out with it.
4. Fill the jar and put the lid back on.
5. Lower the lantern back over the cartridge and do the thumbscrews up.

---

## 13. Cleaning and storage

Same night, before the sugar dries:

1. Switch off, lift the lantern off the cartridge and stand it beside it (section 10).
   Connect USB serial using section 4's power procedure.
   Empty the jar, half-fill it with warm water, and put the shot glass in its slot.
2. `cal 8000` pours about 22 mL into the glass. Empty the glass and repeat 4 or 5 times. Only the shot
   glass fits under the nozzle, so keep each run short: `cal 20000` would pour ~55 mL and overflow it.
3. Unscrew the jar lid and hold the pickup tube out of the water. Run `cal 8000` twice more to push the
   line empty.
4. Rinse the jar, the lid and its vent valve. Open the pump head and lift the tube off the rollers. Let
   everything air-dry with the tube ends open.

**Never leave liqueur in the tube overnight:** the sugar gums up the bore and the rollers.

**Storage:** S1 and the TalentCell switch OFF, USB unplugged, and the pump head open so the tube isn't crushed for
months. Replace the pump tube when it looks cloudy or flattened.

---

## 14. Troubleshooting

| Symptom | Check |
|---|---|
| Ring not detected | Are both cable plugs connected (easy to forget after a refill)? `status` with the ring in. Is the A3144 printed face up on its post? Is the magnet's switching face toward the ring's face (section 6, step 2)? Is pin 1 on 5 V? |
| Ring won't seat in the pocket | The rotor is not at rest: turn it back by hand (and grease it, section 6 step 4). The emblem's bars must be level (the rotor's rest position) to drop into the pocket. |
| Nothing lights, no response | JP1 fitted with USB unplugged? Pack switch and S1 on? Pack flat: `status` over USB or the meter on the rail; charge it. Plugs connected? |
| Pump won't stop | Switch S1 off. The firmware caps every run at 20 s; if it runs again on its own, the switch lever is stuck pressed (bracket slid too far toward the cam, section 6 step 6) or D2 is shorted to ground. |
| No pour on the twist | `status` while twisting: the switch must read `pressed` before the hard stop. Slide the switch bracket toward the cam. |
| Pump hums, no flow | Tube not seated under the rollers, head cap open, the service loop kinked when the lantern went back on, or the wrong (thin-walled) tube. |
| Pours shrink after a few in a row, jar dents in | The vent valve is in backwards (arrow must point into the jar) or blocked. |
| Pump doesn't run at all | Switch on? Check the rail gives 9–12.6 V (meter). Check Q1's pins (gate, drain, source) and the 10 k on D3. |
| XIAO resets when the pump starts | 12 V sagging: C2 missing, or the pack nearly empty (charge it). |
| LEDs stay dark or stay on | Q2 wiring, U1 supply/input/output wiring, or U1's output-enable pins not grounded. |
| Double blink when the ring goes in | Low battery (below 10.5 V): charge it. If the pack is full, check the reading against your meter and run `vcal`. |
| Pours shrink as the night goes on | The battery reading is off or not connected (`status` says `not sensed`): check the divider on D0, then `vcal`. |
| Rotor sticks | Clean PETG strings out of the bore, sand lightly, or reprint the rotor with `FIT` + 0.05. |
| Rotor doesn't return on its own | Grease the ramp, the plunger nose and the bore (section 6, step 4). A stiffer spring doesn't help: it is the ramp's slope against dry friction. Turning the ring back by hand works the same for the firmware. |
| Drips after the pour | Trim the tube end square; make sure 5 mm sticks out of the guide. |
| Pour misses the glass | The glass was not pushed all the way back: it must click over the ridge. |
| The glass catches on the way out | Slide it toward you the full 3 cm before lifting: lifting early hits the lock. |
| Your hand catches on the curtain | Trim the strips 5 mm shorter, or use a thinner sheet (a 0.3 mm report cover). |

---

## 15. What this budget build leaves out, and how to add it back

| Upgrade | Cost | How |
|---|---|---|
| Glowing ring around the lock (24-pixel NeoPixel ring + translucent halo) | ~$17 | Set `LED_RING = True` in `cad/parts/socket.py`; the ring needs addressable-LED code, which is in the git history before the budget change. |
| Fuse | ~$3 | An inline 2 A slow-blow fuse between the pack and S1. The pack's protection board already cuts out on a short. |
| Steady LED brightness on a draining battery | ~$6 | A small buck-boost converter set to 12.0 V between the +12 V rail and the LED strip's + (the pump keeps its firmware compensation). Without it the strip dims as the pack drains: ~70 % of its current at half charge (~11.3 V), a third to a half at 10 V. Charging at half keeps it bright enough. |
| PRIME button | ~$2 | 12 mm momentary button from D6 to ground. Already supported by the firmware. |
| Pinch clamp for carrying a full jar | ~$6 | [Tubing pinch clamps (B0FCM98N2Q)](https://www.amazon.com/dp/B0FCM98N2Q). |

**Why these choices.** The Kamoer pump states 200 mL/min as a minimum, so it reliably pours 1 to 1.25 oz in
10-15 s. Two Adafruit 5 V pumps state 100 mL/min each as a maximum and often miss that window. A green COB LED
strip is enough for a glow that just gets brighter, glows without visible dots, and it runs from the same 12 V as the pump. The reservoir
is a narrow jar (73 mm at most) because it shares the deck with the pump under the lower dish. The glass sits about 5 cm down in
a slot because the sphere is only 10 cm tall inside and your fist and the lock need the space above it; that is
also why it slides toward you before it lifts out. The early research notes are in `docs/research/`; they are partly superseded, and the
current numbers are the ones in this guide and in `cad/params.py`.
