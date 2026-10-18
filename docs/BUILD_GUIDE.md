# Green Lantern power battery that pours a shot: build guide (electrical revision)

A 3D-printed Green Lantern power battery, about 47 cm tall and 19 cm across at the base, with a hidden pump, a hidden
nozzle and a twist-to-pour lock. The sphere has two openings: the **hand opening** on your side, closed by a
curtain of frosted plastic strips, and the frosted **display window** on the far side. Push the empty shot
glass in under the lock until it clicks. Punch in, ring face first, and the ring seats in the lock: the lantern
glows faintly. Twist 45 degrees and hold it while you recite the oath. Behind the lock wall the pump pours
about 1 oz into the glass while the light climbs from 15 % to 90 % over about 11 seconds. Turn back and the
light swells to full, then goes dark. Grip the glass, slide it toward you, lift it and bring it out.

"Your side" means the hand opening; "display side" means the window opposite it.

**3D assembly viewer:** [open it in the browser](https://raw.githack.com/TheRageKage12/drunk-lantern-power-battery/main/docs/assembly-viewer/index.html). Each printed part has its own colour; the 14 steps follow
section 9 and the subassemblies, and an exploded view shows how everything stacks. Click a part for its name and print notes.

**Assembly videos:** [Step-by-step assembly guide (4:30)](videos/assembly-guide.mp4) ·
[Exploded assembly (0:12)](videos/separate-and-assemble.mp4) ·
[Opening for service (0:12)](videos/service-access.mp4).
The assembly guide follows the build order and includes chapter markers. The exploded view illustrates
how the parts fit together; use the guide for the actual sequence. The guide includes two orange-tube
cutaways showing the pump-to-floor route and nozzle threading. The pump outlet and loose service loop
are illustrative; confirm their fit with the actual parts. Wiring, curtain and metal fasteners are
described where needed but are not individually animated.

![interaction timeline](images/interaction.png)

**Status.** Designed, modelled and simulated; not yet built. The firmware previously compiled and still passes 20 simulated
safety scenarios (`firmware/test`). The CAD now includes the TalentCell mount and electronics clearance envelopes.
The fit checks cover the reserved dimensions in [CAD fit limits](../cad/README.md#electronics-fit-limits);
measure the actual capacitor, connectors, buck, switch, pump and jar before printing. Every bay is parametric
(`cad/params.py`), so a measured number is a one-line change and a re-run of `python3 build.py`.

---

## 1. How it works

```
 0. before: push the empty glass in under the lock until it clicks over the ridge at the stop
 1. punch in, ring face first (6x2 mm magnet in a printed key cap) -> Hall sensor sees it -> light fades up to ~15 %
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
| Sphere, inside | The **lock wall**, 2.5 cm past the centre (toward the display window). On its face, facing you: the lock (a rotor with the keyed ring pocket, 0 and 45 degree hard stops, a spring plunger that returns it, a cam, the D2F-01L microswitch and the A3144 Hall sensor) and a column of LEDs either side. Under the lock: the glass, in a slot. Behind the wall, out of sight: the nozzle, over the back third of the glass, and 4 rows of LEDs facing the display window. |
| Sphere, display side | The white diffuser window. |
| Lower dish | Hollow neck: the glass slot hangs into it; the tube and the cables pass through it. |
| Base | A removable **cartridge**: the 12 V battery pack flat on its floor, a deck above it with the jar, the Kamoer pump and the electronics board, and the buck converter beside the pack. Nothing shows on the shell: the power switch sits in a pocket under the cartridge floor (tip the lantern to flip it) and the charge jack is on the deck, pointing up. It slides up into the base drum and is held by 3 thumbscrews underneath, out of sight. To refill or charge: undo them and lift the lantern off; the cartridge stays on the table. |

![fluid path and layout](images/fluid-path.png)

The drink touches only the jar, the platinum-silicone tube and the glass. No printed part is in the liquid path.

---

## 2. Shopping list

The live list, with who has each item and what is left to buy, is the [shared Google Sheet](https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit). The tables
below describe the current circuit (the 2026-10-14 electrical revision, recorded in [CIRCUIT_PR.md](review/CIRCUIT_PR.md));
the Sheet carries the same parts, plus the heat-set inserts and straps.

Amazon prices, stock and delivery were re-checked on 2026-10-15: everything in stock, Prime delivery Oct 16-17 and
free delivery Oct 20 (Amazon's default address; Seattle should match within a day). The Auber tubing showed only 2 left
and the pump 12: order those first. Vetco prices are from 2026-10-13; prices with "~" are estimates. Confirm at checkout.

### 2.1 Order online

| # | Item | Buy | Price | Notes |
|---|---|---|---|---|
| 1 | Pump | [Kamoer KPHM200, 12 V (B09HGVLHFV)](https://www.amazon.com/dp/B09HGVLHFV) | $28.00 | 200 mL/min or more at 12 V, 0.7 A. Run at ~70 % speed it pours about 1 oz in 11 s. |
| 2 | Tubing | [AUBER 1/8" ID x 1/4" OD platinum-cured silicone, 10 ft (B0DKB1NKB4)](https://www.amazon.com/dp/B0DKB1NKB4) | $13.99 | The exact 3.2 x 6.4 mm size the Kamoer head needs. FDA 21 CFR 177.2600, NSF 51. Thinner 1/8" x 3/16" tube will not pump. One run is ~90 cm; the rest covers replacements (the tube is the part that wears). |
| 3 | LED strip | [HAMRVL COB LED strip, green, 12 V, 8 mm, 5 m (B0CKYFLZFQ)](https://www.amazon.com/dp/B0CKYFLZFQ) | $14.99 | COB: 320 LEDs/m under one continuous coating, so it glows evenly with no dots. Cuts every 25 mm. You use 75 cm in 7 pieces. Its current isn't listed; COB strips like it draw roughly 0.8 A/m, so ~0.6 A for 75 cm. |
| 4 | Buck converter | [LM2596 step-down module, 5-pack (B0DBVYP91F)](https://www.amazon.com/dp/B0DBVYP91F) | $7.99 | 9–12.6 V in, set to 5.0 V out for the XIAO, gate driver and Hall sensor. 43 x 21 mm. |
| 5 | Magnets | [6 x 2 mm neodymium, 45-pack (B0CBRVF4PN)](https://www.amazon.com/dp/B0CBRVF4PN) | $6.29 | 1 in the ring key (the pack is the smallest sensible buy). |
| 5c | Vent valve | [AQUANEAT aquarium check valves, 10-pack (B086JRH4WS)](https://www.amazon.com/dp/B086JRH4WS) | $4.79 | One goes in the jar lid: lets air in as the pump draws the drink out, but nothing out if the jar tips. Fits 3/16" airline. |
| 6 | Microcontroller | [Seeed XIAO RP2040, pre-soldered (B0DRNTQ338)](https://www.amazon.com/dp/B0DRNTQ338) | $10.99 | |
| 8 | 12 V battery pack | [TalentCell YB1203000 with charger (B00MHNQIR2)](https://www.amazon.com/dp/B00MHNQIR2) | $22.99 | 3000 mAh, 3 A maximum output, 105 x 65 x 25 mm. Output varies from 12.6 to 9 V. Use its supplied charger (12.6 V, 0.5 A, ~6 h) and a male DC5521 lead cut from its supplied splitter. Its one DC5521 port is both input and output, and its own switch must be ON to charge (TalentCell manual). The cartridge tray is built for this case (rev 9i). |
| 9 | D2F-01L lever microswitch, 4-pack (1 used) | [Amazon B0DBV9JX6L](https://www.amazon.com/dp/B0DBV9JX6L) | $7.97 | Third-party (Pecafeitas) listing of the 0.1 A hinge-lever version. Omron's datasheet gives its minimum load as 1 mA at 5 V (the plain D2F needs 100 mA), which the section 4 interface supplies. Omron provenance is not verified: check the marking, the peg spacing against `switch_bracket`, and that it clicks reliably 50 times. |
| 13a | Heat-set inserts | [ruthex RX-M3x5.7 brass, 100-pack (B08BCRZZS3)](https://www.amazon.com/dp/B08BCRZZS3) | $9.99 | 32 used. 5.7 mm long, made for a 4.0 mm hole: the 32 receiving bores are 4.0 x 6.5 mm (section 3). Any plain M3 x 5.7 x 4.6 mm brass insert is the same part. |

**Hall sensor alternative (not recommended: Adafruit ships slowly, and the board sits 7.7 mm from the magnet
instead of 3).** The lock is built for the A3144 from Vetco (item 7), on a post that reaches up
inside the rotor to about 3 mm from the magnet. If you ever have an Adafruit DRV5032 board (#6051) instead, set
`HALL_SENSOR = 'DRV5032'` in `cad/params.py` and reprint `rotor` and `socket_base`: it then sits under the plate,
works on 3.3 V and either magnet pole.

### 2.2 Pick up locally

| # | Item | Where | Price | Notes |
|---|---|---|---|---|
| 7 | Hall sensor, A3144 | [Vetco, VUPN6596](https://vetco.net/products/vupn6596_hall-effect_sensor_-_allegro_a3144eua_d63) | $1.99 | Runs on 5 V, reacts to one magnet pole. It sits on a post inside the lock, ~3 mm from the magnet: about 90 mT there, 2.5 x its worst-case switch point. |
| 5b | Cable plugs | Vetco: [JST PH 4-pin pair](https://vetco.net/products/jst-ph-2-0-4-pin-connector-male-female-pair-pre-wired) ($2.24) for the lock cable, [JST SM 2-pin pair](https://vetco.net/products/vupn1054_jst_sm_2_pin_m-f_pair_locking_connector) ($1.75) for the LED leads | $3.99 | So the lantern unplugs from the base cartridge. |
| 5a | Curtain sheet | Target, Fred Meyer, Office Depot (school aisle): one clear-frosted polypropylene folder, binder divider or report cover | ~$3 | Polypropylene flexes thousands of times, lets the light through and hides the inside. One sheet makes the curtain (13 strips 12 x 97 mm). 0.3-0.5 mm; thinner parts more easily. Not PVC/vinyl, which cracks at the folds. |
| 10 | 74AHCT125 quad buffer, DIP-14 | [Vetco, VUPN524](https://vetco.net/products/vupn524_quad_level-shifter_-_74ahct125_-_3v_to_5v_d96) | $2.95 | Turns the XIAO's 3.3 V into a clean 5 V gate signal for both MOSFETs. Must be AHCT, not HC. |
| 11 | 2 x IRLZ44NPBF N-MOSFET | [Vetco, VUPN1682](https://vetco.net/products/vupn1682_mosfet_mosft_for_micro_controllers_-_30v_-_60a_-_irlb8721pbf_d151) | $5.34 | Exact required part: IRLZ44NPBF, TO-220. Vendor URL/title is stale; its detail table names IRLZ44NPBF. Verify IRLZ44N marking; review substitutions before use. |
| 12 | Small parts | Vetco and Amazon; proposed Sheet edits in [electrical PR draft](review/CIRCUIT_PR.md#spreadsheet-edits-after-acceptance) | Reprice after review | 2 x NTE585, 1 x NTE586 (3 A/40 V); 2 x 10 kΩ, 2 x 4.7 kΩ, 1 x 3.3 kΩ, 1 x 100 kΩ, 1 x 22 kΩ; 3 x 0.1 µF ceramic, 1 x 2200 µF/25 V; DIP-14 socket; JP1 two-pin header and shunt; existing perfboard, wire and heat-shrink. |
| 12a | Power switch | [Vetco 30-10005, SPST mini toggle with leads](https://vetco.net/products/30-10005_spst_miniature_toggle_switch_w-wire_leads_on-off_6a) | $4.95 | On-off, 1/4" bushing (6.5 mm panel hole), 6 A at 12 V. |
| 12b | Charge jack | [Vetco 2112, 2.1 mm DC panel jack](https://vetco.net/products/2112_2-1mm_dc_power_panel_mount_jack) | $2.88 | DC5521 (5.5 x 2.1 mm) female, 8 mm panel hole; the battery's charger plugs into it. |
| 13 | M3 screws and nuts | Tacoma Screw, by the piece ([or the Amazon M3 kit, B0HKFCTLK8](https://www.amazon.com/dp/B0HKFCTLK8), $8.99, which has no countersunk screws) | ~$12 | 4 x M3x6, 17 x M3x8, 8 x M3x8 flat-head (countersunk), 6 x M3x10, 11 x M3x12, 14 nuts. They go into the 32 heat-set inserts (item 13a), except the 3 thumbscrews, the 5 lock screws and the 6 handle lap screws, which use the 14 nuts. |
| 14 | Compression spring | Ace Hardware, Hillman spring drawer (bring calipers) | ~$1-2 | About 0.4-0.5 mm wire, 5 mm outside diameter, ~10 mm long (cut a longer one down). A retractable pen's spring also fits but is softer. |
| 15 | Super glue | the Gorilla Glue super glue you already have (any cyanoacrylate works) | - | For the magnets, the key cap, the nuts, the Hall sensor and a few dots on the diffuser. |

**Total: about $205 before tax** (2026-10-15): Amazon $127.99 (the inserts included), Vetco $46.57, Tacoma Screw ~$12, straps and
zip ties ~$5, and ~$13.50 of local estimates for the spring, the jar, the curtain sheet and the shot glass. The
[shopping sheet](https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit) has the live store-by-store figures and who already has what. The 2026-10-13
design was about $186: the electrical revision added $4.69, the heat-set inserts $9.99, the straps and ties ~$5 (listed before,
but left out of the old total) and the green filament rose by $3 a spool. Two of the local items have size limits; measure in the store:

- **A food-safe jar no bigger than 73 mm across (lid included) and 76 mm tall** (Micro Homebrew in Kenmore has small food-safe jars; measure with the lid on).
- **A 1.5 oz shot glass** up to 52 mm across the top and 62 mm tall (Libbey 1.5 oz glasses fit). About 1.3 cm of it stands above the slot for your fingers; a heavy base helps.

The total assumes you already have:

- **PETG filament.** About 1.2 kg of green at the settings in section 3 (two 1 kg spools: the second covers the rest, the supports and one failed big part) plus ~30 g of white or natural for the diffusers (~$49 for two green spools and one white).
- Basic tools: soldering iron and solder, multimeter, calipers, a drill with 3.2, 5 and 6 mm bits, flush cutters, a
  2.5 mm hex key (a long or ball-end one for the sphere's flange screws and the handle) and a 2 mm hex key for the
  countersunk screws, a small flat screwdriver for the LM2596's trimmer, a hobby knife and ruler, a USB-C data
  cable for the XIAO, and a kitchen scale or measuring cup for calibration (1 g of water = 1 mL).
- A dab of silicone grease or petroleum jelly for the lock's ramp and plunger.
- 4 hook-and-loop straps 20 mm wide (two pump, one jar, one battery; battery strap <=1 mm thick beneath tray) and about 10 small zip ties
  (2.5 mm wide, for the LM2596 and cable tidying). Any hardware store, ~$5 if you have none.

### 2.3 Seattle-area stores (verified open on 2026-10-11; call before driving for specific stock)

| Store | Address, hours | Buy here |
|---|---|---|
| [Vetco Electronics](https://vetco.net) | 12718 Northup Way STE 100, Bellevue 98005, (425) 641-7275. Mon-Fri 9-6, Sat 10-3:30 | The A3144, MOSFETs, diodes, resistors, capacitors, protoboard, IC socket, wire, heat-shrink, power switch, charge jack and the two JST plugs. Not stocked: XIAO, magnets, check valves. |
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

All files are in `cad/output/` (STL for slicing, STEP for editing). Print only the 25 parts in the table:
`assembly.stl` and the `*_envelope.stl` files are check volumes, not parts. Everything fits your 230 x 230 x
240 mm Ender 3. The widest part is the rear sphere half at 221 mm (because of the handle bosses), the tallest is
the base at 115 mm. Centre the big parts. A skirt is enough, except for the two sphere halves and `dish_lower`,
whose first layer is only a 2.4 mm ring: give those a 6 mm brim.

**PETG settings (0.4 mm nozzle):** 0.2 mm layers, nozzle 235-245 C, bed 75-85 C, 4 perimeters, 5 top and
bottom layers, 25-30 % gyroid infill, outer walls 40-60 mm/s, fan off for the first 3 layers then 30-50 %.
Textured PEI, or glue stick on smooth PEI. Do not anneal. Set 0.2 mm of elephant-foot compensation (Cura:
initial layer horizontal expansion -0.2): the spigots, the locating rings and the drum's bore all mate on their
first layers, with 0.3 mm of clearance a side, and a flared first layer on both parts eats that. If a ring still
binds, sand the smaller part's edge. Turn "print thin walls" on for `socket_base` (the sensor post's walls).

**Install the brass heat-set inserts before assembly.** All 32 receiving holes are **4 mm diameter ×
6.5 mm deep**. The listed ruthex RX-M3x5.7 (5.7 mm long, 4.6 mm across, made for a 4.0 mm hole) or any plain M3 x 5.7 x 4.6 mm
brass insert fits; a 5 mm-wide "M3 x 4 x 5" insert does not. Fit them flush with the
entry face, let them cool, and check that each screw turns freely before mounting components. Follow the
insert supplier's installation temperature and test one in a scrap print first. The 3.4 mm screw
through-holes, countersinks and captured-nut pockets retain their separate dimensions.

| Printed part | Inserts | Entry side |
|---|---:|---|
| `base_tray` | 3 | Tops of the deck-support pillars |
| `base_deck` | 4 | Faces of the circuit-board mounting pads |
| `dish_lower` | 6 | Outside faces of the two rings, three per ring |
| `dish_upper` | 11 | Four top-diffuser holes, three outer radial holes, four underside curtain-clamp holes |
| `sphere_front` | 4 | Split-face bosses |
| `sphere_rear` | 2 | Inner walls of the two handle sockets; insert before fitting the legs |
| `bay_floor` | 1 | Top face, under the nozzle-guide foot |
| `socket_housing` | 1 | Open back, beside the switch cavity |

Print these first, before any big part, and check them:

1. `socket_housing`, `rotor`, `socket_base`, `plunger`: the rotor turns 45 degrees with slight drag and the
   plunger snaps it back. If it binds, raise `FIT` in `cad/params.py` by 0.05 and reprint the rotor.
2. `key_cap`: drops into the rotor pocket one way only, with a little play.
3. `glass_well` with your real shot glass: it slides the length of the slot, clicks over the ridge at the far
   end, and comes back out. If your glass is wider than 52 mm at the top it won't fit; pick another glass.
3a. The other sliding fits, each as soon as both parts exist: `base_tray` up into `base` (sand the tray's edge,
   not the drum, if it binds), `dish_lower`'s spigot into the top of `base` (the tightest joint), `socket_housing`
   into the floor hole of `dish_upper`, `glass_well` into `bay_floor`'s slot, and a handle leg into a boss of
   `sphere_rear` before you print the arcs.
4. **Optional hand check.** The CAD clears a fist 106 x 76 mm (yours is under 4 x 3 in). If you want to be
   sure before the big prints: cut a 120 x 96 mm hole in a box and punch through it with a shot glass held
   under your fist. Both must pass without scraping.

### Part list

| Part | Size (mm) | Orientation on the bed | Supports | Colour | ~g |
|---|---|---|---|---|---|
| `base` (drum) | 190 x 190 x 115 | top band down | no | green | 232 |
| `base_tray` (cartridge floor, with the switch pocket) | 179 x 179 x 44 | flat | no | green | 91 |
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
| `bay_floor` | 131 x 131 x 10 | insert boss up, as exported | under the recessed floor inside the drip lip | any | 21 |
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
| `key_cap` | 28 x 24 x 3 | flat face down | no | green | 2 |
| **Total** | | | | | **~1240 g** |

Supports: none, except inside the two sphere halves, beneath the inverted bay floor, under the nozzle guide's bend, and the thin rings under the
two dishes' bearing faces (they start in mid-air 8-9 mm up; "touching build plate only" support is a short ring
that pulls off clean). Print the halves split-face
down; the last 15 mm of dome around the window and the hand opening overhang more than 45 degrees, so enable
tree supports on the inside only. The `nozzle_guide` prints foot down; the last 45 degrees of its bend hang past
horizontal, so give it a small tree support there. The grams column assumes the settings above (the parts are
mostly wall, so count about 1.1 g per cm3; the diffusers are solid). Print both diffusers (`diffuser`, `top_diffuser`) in white or natural PETG at 100 % infill: green works
but is dimmer. A white `lock_wall` reflects more light out of the hand opening.

![all printed parts](images/cad-parts-sheet.png)

![assembly](images/cad-assembly-iso.png) ![cutaway](images/cad-cutaway.png)

---

## 4. Electronics (build it on the bench first)

![wiring diagram](images/wiring.png)

Build the circuit on the 5 x 7 cm perfboard and test it before anything goes into the lantern.

Use the [two-sided perfboard layout](review/protoboard/README.md) and its
[wire-by-wire solder schedule](review/protoboard/WIRE_SCHEDULE.md). The rear view is mirrored;
pad names stay the same. Check the actual hole-array position and C2 case size before assembly.

1. **Board, XIAO and U1.** Orient the perfboard 70 mm across and 50 mm tall. Drill four 3.2 mm
   holes at (x, y) = (18, 17), (55, 15), (15, 45) and (58, 45) mm from the component-side top-left corner
   (the [board layout](review/protoboard/README.md) is the reference), checking against the printed panel first. Keep each 9 x 9 mm mounting area clear. Fit the XIAO and a **DIP-14 socket** for U1; leave U1 out
   during initial USB flashing. Fit a two-pin 2.54 mm header for JP1 and label it **REMOVE FOR USB**.
2. **Battery, charge jack and S1.** With battery and charger unplugged, cut one male DC5521 lead
   from the supplied TalentCell splitter to make the battery pigtail. Do not cut or open the pack.
   Identify centre-positive and sleeve-negative with a continuity meter; do not rely on wire colour.
   Plug the finished, insulated pigtail into the pack. With its own switch ON, confirm 9–12.6 V and polarity.
   Power off and unplug again before soldering. Positive goes to J1 centre and S1; S1's other terminal is
   **VLOAD**, the switched battery rail. Negative goes to J1 sleeve and the common ground.
   Identify J1's contacts with a plug and continuity meter; its third, switched contact is unused and insulated.
   Solder **C2 2200 µF/25 V** from VLOAD to ground, positive to VLOAD. It buffers short disturbances;
   it cannot sustain an overloaded or stalled motor. Charge with **S1 OFF, pack switch ON**, using only
   the supplied 12.6 V charger through J1. The pack lies flat on the cartridge floor under a 20 mm strap (section 9).
2a. **Battery sense.** R1 100 kΩ from VLOAD to D0; R2 22 kΩ and C1 0.1 µF from D0 to ground.
   At a full 12.6 V pack, D0 sees 2.27 V. Keep this signal away from motor wiring.
3. **Set the buck output first.** Connect only LM2596 IN+ to VLOAD and IN− to ground; leave OUT unloaded.
   Turn the pack and S1 on. With the meter on DC volts across OUT+/OUT−, adjust the trimmer to **5.0 V**.
   Switch off before attaching anything else. OUT+ is **+5V_REG**: connect U1 and the Hall sensor directly
   here. Feed the XIAO 5V pin through **D1 NTE585**, stripe toward the XIAO, then **JP1** in series.
   Grounds stay connected even with JP1 removed. D1 blocks reverse flow into the buck, but does not
   isolate the USB host from battery power: **remove JP1 before connecting USB**.
4. **U1 (74AHCT125).** Keep the original buffer. Pin 14 to +5V_REG, pin 7 to ground; solder the
   existing **C3 0.1 µF ceramic** directly across those pins with short leads. Ground all four output-enable
   pins (1, 4, 10, 13) and the unused inputs (9, 12); leave unused outputs (8, 11) unconnected.
   XIAO D3 goes to pin 2 (pump); D4 goes to pin 5 (light). R3/R4 remain **10 kΩ** from those respective
   inputs to ground. Check the socket notch and [DIP-14 pinout](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf)
   before inserting U1 with all power disconnected. Use **74AHCT125**, not 74HC125.
5. **MOSFETs.** IRLZ44NPBF, label facing you and leads down: pin 1 gate, pin 2 drain (also tab), pin 3 source.
   U1 pin 3 connects directly to Q1's gate (pump); U1 pin 6 directly to Q2's gate (light), as in the original
   circuit. Both sources go to ground. Pump negative goes to Q1 drain, strip negative to Q2 drain;
   both loads' positives go to VLOAD. Run pump/strip returns separately to the common power ground;
   do not route their current through the Hall/MCU ground wiring. Verify startup behavior on the bench.
6. **Pump flyback.** D2 **NTE586, 3 A/40 V**, directly across the pump terminals: stripe/cathode to VLOAD,
   anode to Q1 drain. The orientation is unchanged. Do not use the 1 A NTE585 here.
7. **Lock wires.** A3144, printed face toward you, leads down: pin 1 to +5V_REG, pin 2 to ground,
   pin 3 directly to D1 (the XIAO GPIO). R5 **4.7 kΩ from D1 to XIAO 3V3**, never to 5 V.
   Fit **C4 0.1 µF across sensor pins 1 and 2 at the sensor**, below its mounting pocket with insulated leads.
   Its open-collector output needs no series diode.

   Microswitch **D2F-01L**: COM to ground, NO to the SW wire, NC unused. On the board, R7 **3.3 kΩ**
   connects +5V_REG to SW. R6 **4.7 kΩ** connects XIAO 3V3 to D2 (the GPIO).
   **D3 NTE585 anode to GPIO D2, stripe/cathode to SW/NO**: closed contacts pull the GPIO low;
   open contacts leave it at 3.3 V while the switch side rises to 5 V. R7 provides about 1.5 mA through
   closed contacts; the GPIO pull-up adds about 0.6 mA. The original weak internal pull-up alone is not
   the specified interface. The firmware's internal pull-ups may remain enabled alongside R5/R6.

   Make the 4-wire lock cable: **+5V_REG, HALL, SW, GND**, about 40 cm, JST PH plug about 10 cm from the
   board. Keep R5–R7 and D3 on the board. **Do not solder the Hall sensor to the cable yet:** its leads
   must first pass the sensor post slot (section 6). Clip it temporarily for bench checks. Solder the switch
   wires before mounting it. Make the LED lead with a JST SM pair, VLOAD and Q2 drain, leaving the far end
   bare until section 8. Thread lantern-side wires through the bay-floor hole before fitting plug housings.
8. **Commission before enclosure assembly.** Flash using the power procedure below. First leave pump and
   strip disconnected. In USB calibration mode, check +5V_REG at U1 and Hall is 5.0 V; check GPIO D1/D2
   are approximately 3.3 V open and below 0.8 V when asserted. `status` must follow the magnet and twist
   repeatedly, including with the cable moved; battery reading should match the meter within 0.2 V after
   `vcal`. Verify both MOSFET gates are low at idle. Then connect loads with power off.

   With a fully charged pack and the intended strip length, check full brightness, current and heating
   before enclosing it (use `idle 255` for 100% PWM, then restore `idle 0` and `save`). Measure current **in series** with
   a suitably rated, fused meter, never with the meter in current mode across the battery. Run short water
   pours with the LEDs on, watch for resets/protection trips and hot wiring/MOSFETs, and measure combined
   running current; the estimate is ~1.3 A, not a measured specification. A normal meter may miss startup
   peaks. Stop and investigate overheating, a stall or a protection trip; do not deliberately stall the pump.
   Confirm every power-up leaves the pump off; the brief LED boot blink is intentional.

### USB programming and calibration power

Normal operation is battery-only. **Never attach USB with JP1 fitted.** JP1 isolates only the XIAO supply.
Removing U1 for USB-only flashing also disconnects the GPIO signals from the unpowered buffer.

- **USB-only flashing:** S1 OFF, pack unplugged, JP1 removed, **U1 removed from its socket**. Connect USB,
  upload, then unplug USB before reinserting U1. No load tests in this mode.
- **USB calibration/testing with U1 installed:** with all power off, remove JP1. Leave the pump and
  LED leads disconnected during the initial bench check. Turn the pack and S1 ON first, verify +5V_REG, then connect USB; USB powers
  only the XIAO while the buck powers U1/Hall. After the controller settles at idle, power down (USB out
  first, then S1 OFF), attach loads, and repeat this sequence for testing. End with `stop`, unplug USB,
  then switch S1 OFF. Refit JP1 only after USB is unplugged and power is off.
- **Battery operation:** USB unplugged, U1 installed, JP1 fitted; pack switch ON, then S1 ON. Turn both
  switches OFF for storage. Never move JP1 or insert/remove U1 with power connected.

If the pack trips or +5V_REG fails during USB testing, unplug USB promptly and investigate before retrying.

An optional PRIME button goes between D6 and ground. Holding it runs the pump only when no ring is in.
It's not in the parts list; the serial `cal` command or a test pour does the same job.

---

## 5. Firmware

Source: `firmware/green_lantern/green_lantern.ino`. Board: Seeed XIAO RP2040 on the "Raspberry Pi
Pico/RP2040" Arduino core by Earle Philhower. No extra libraries.

**First follow section 4’s USB power procedure.**

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

Parts: `socket_housing`, `rotor`, `socket_base`, `switch_bracket`, `plunger`, `key_cap`. Plus 3 x M3x8 flat-head and 3
nuts for the base plate, 1 x M3x8 flat-head for the switch bracket, 2 x M3x10 and 2 nuts to mount it on the
lock wall, the spring, the microswitch, the A3144 and one magnet.

The lock is screwed to the face of the lock wall with its ring pocket facing you, so you seat the ring by
punching in. The rotor is a flat 36 mm disc. Under the housing's front lip its edge carries three features: a
stop lug in a channel whose ends are the 0 and 45 degree stops, a cam that presses the switch lever 3 mm
from about 30 degrees to the stop, and a ramp that pushes the spring plunger out so the rotor snaps back when you let go.

1. **Nuts.** Drop M3 nuts into the three hex pockets on the underside of `socket_housing`. A dab of super glue
   holds each.
2. **Ring key.** The A3144 reacts to one magnet pole only. With the sensor wired to the board (section 4) and
   `status` running, hold each face of the magnet to the sensor's printed face: the face that gives
   `ring=present` must face **out** of the pocket in `key_cap`. The cap has a closed flat face (the one that was
   on the print bed) and a face with the open magnet pocket: the pocket face goes into the rotor, toward the
   sensor, and the flat face is glued to the ring. Mark the magnet, then glue it in. Scuff
   the ring's flat face and the key cap. Put the ring on your left hand and make the fist you will punch with,
   ring face forward, held the way you start the twist (for example palm down). Glue the key cap on so its tab
   points to your right. In the lock the tab then sits at the rest position, and the twist is counterclockwise
   as you see it (from palm down, your thumb rolls up). The lock is built mirrored for this;
   `LOCK_TWIST = 'cw'` in `cad/params.py` gives the clockwise version.
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
5. **Switch.** With its two wires already soldered on (section 4 step 7), press the microswitch onto the two
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
   rim notch lands. Leave the cable long enough to reach the base (about 40 cm).

---

## 7. The fluid path

1. **Jar lid.** Drill a 6 mm hole near the edge and push the tube through it (it seals itself) until it reaches
   5 mm above the jar's bottom. **Vent:** the check valve's barbs are made for 3/16" airline, wider than the pump
   tube, so the valve gets its own hole on the opposite side. Measure the barb (about 5 mm), drill the hole to
   that size, push the valve's lower barb through the lid from above until its ridge seats, with the arrow
   pointing **down into the jar**, and seal round it with a dab of super glue. Air gets in as the
   pump draws the drink out (without it the jar goes under vacuum and the pours shrink), but if the jar tips,
   nothing comes out. Blow through it to check: air goes in, not out. The valve stands about 25 mm above the
   lid; the lower dish leaves about 40 mm.
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
6. **Prime.** Follow section 4’s USB calibration power sequence (JP1 removed); section 10 explains
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
   made in section 4 step 7 (its bare end), so it runs down with the lock cable.
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

1. **Cartridge.** Stand `base_tray` with the switch pocket (the raised box near the rim) toward you. The
   LM2596 goes in its pocket on the right, on its four 2 mm printed corner supports, zip-tied through the slots beside it.
   Check that no underside solder joint rests on a support.
   The TalentCell lies flat in the middle, **connector/switch end away from you (-Y)**, at the low end stop.
   Thread a 20 mm strap through both slots before fitting the pack; its lower run sits in the underside
   recess and must be no thicker than 1 mm. Tighten the strap: the deck is 17 mm above the case and does
   not retain it. Check the plugged-in lead and bend fit the 25 mm space beyond the battery end.
   S1 in the pocket's ceiling from below, nut tight. Bring the pack's and S1's leads up
   through the open notch at the deck's edge (the deck's other slot is a closed hole, so
   a soldered lead can't be threaded through it later), then `base_deck` drops in on top (3 x M3x8 into the
   three pillars that have holes; it fits one way). The jack goes socket-up in the relocated 8 mm hole
   on the side opposite the buck converter (+X, y=-25), clear of the populated board. Check its charging
   plug fits with the shell off. Jar in its ring with a strap through the finger slots. **Fit the tube
   to the pump now, while the cartridge is exposed:** open the head, lay the continuous tube around
   the rollers and close the cap. Leave the outlet end free for later threading to the nozzle. Then
   seat the pump in its saddles and secure it with two straps. Electronics board on the deck's vertical panel (4 x M3x6 through the holes you
   drilled). Keep the inline lock/LED plugs above the unused module pocket, clear of the battery supports.
   Remove all print support from the four board pads; clipped leads and rear wiring must stay within
   the 10 mm gap (use the revised pad positions and wire layers in the board guide). Verify access to JP1 and the pack switch with the shell off; undo the three deck screws
   if needed for pack service. Route and tie the battery lead along the tray edge, clear of retaining bosses.
2. **Drum.** Push an M3 nut into the slot in each of the 3 bosses inside the bottom of `base` (a dab of glue
   holds each). Push an M3x12 screw head-first into each `thumb_knob` from below and glue it. Then `dish_lower`:
   its spigot goes into the top of the drum, 3 x M3x8 from outside. The drum stays with the lantern from now on.
3. **Bay floor.** From here until step 9 the open drum has the tube and the cables coming out of its bottom,
   so stand the lantern on two blocks (a couple of books) to keep its rim off them.
   Lay `bay_floor` on the lower dish's locating ring: the long slot points at you, the two short slots for the
   wall's tabs sit either side in the far half, the tube hole and the 7 mm cable hole are beyond the wall line
   (tube on the right, cables on the left; the lock cable and LED lead already pass through it, section 4
   step 7, and their plugs go down through the lower dish to the board). Take the free end of the continuous
   tube leaving the pump on the cartridge beside the shell. Leave about 30 cm extra between pump and bay floor
   for the service loop, then feed the end up through the lower dish neck and the separate tube hole in
   `bay_floor`. There is no connector at the floor. Drop `glass_well` into the long slot, its ridge end
   toward the display side; it hangs from its flange.
4. **Nozzle.** Push the tube up through the hole in `nozzle_guide`'s foot and along the channel, pressing it
   in through the open side where it resists (the slit is a little narrower than the tube), so 5 mm sticks out
   past the end, pointing down. Screw the foot into the bay-floor insert (1 x M3x8), open side toward you,
   the curve reaching toward the middle. The insert boss below the floor fits the matching relief in the lower dish.
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

Keep the pump wires twisted and away from the Hall and switch wires. To turn the lantern on or off, tip it
and flip the switch in the pocket under the cartridge floor, on your side; it is out of sight from every angle.

---

## 10. Calibration

**Reaching the XIAO.** Its USB port is on the cartridge, under the lantern, so every `status`, `cal` and `vcal`
here, in sections 11 and 13 and on the day means: switch off, undo the 3 thumbscrews, lift the lantern off and
stand it beside the cartridge on two blocks (a couple of books), so the tube and the two cables run out under
the drum's rim without being crushed. The glass stays in the lantern under the nozzle; the 30 cm service loop
reaches.

**Follow section 4’s USB calibration power sequence: JP1 removed, U1 installed,
regulated 5 V present before USB is connected.** Unplug USB before switching S1 off.

Water in the jar, the shot glass in its slot (only the shot glass fits under the nozzle; weigh what it pours on
a kitchen scale, 1 g = 1 mL, or tip it into a measuring cup). Connect USB serial using section 4’s power procedure.

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

Then repeat with the real drink: liqueur is thicker than water and the nozzle is about 12 cm above the pump, so
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
- [ ] S1 OFF, pack switch ON, USB unplugged: the supplied charger indicates charging through J1.
- [ ] Push the empty glass in until it clicks, pour water, then take it out: grip, slide 3 cm toward you, lift, out through the curtain, without spilling.
- [ ] Your fist goes through the curtain and into the lock, and back out, without catching.
- [ ] With the lights on in a dim room, the curtain, the display window and the top all glow; you can't see the nozzle.

---

## 12. Performing it

Set the lantern on a table with the hand opening toward you. Reach through the curtain, lower the empty glass
into the near end of its slot and push it all the way back until it clicks over the ridge: that is the pour
position, under the lock.

1. Make a fist (ring on your left hand) and punch in through the curtain, ring face first, until the ring
   seats in the lock. The lantern glows faintly.
2. Twist 45 degrees counterclockwise and hold it as you start the oath. The pump starts and the light begins to climb.
3. Keep holding through the oath. After about 11 seconds the pour is done; the light sits at 90 % until you
   turn back, so a longer oath is fine.
4. On the last word, turn back. The light swells to full and goes dark.
5. Draw your fist back a little and open your hand: the front of the glass is right under the lock. Grip it,
   slide it about 3 cm toward you, lift it straight up out of the slot and bring it out through the curtain.

**On the day:** charge (section 11's 11.5 V line), fill the jar with the real drink, and with the lantern still
standing beside the cartridge (section 10) prime with `cal 8000` into the shot glass until the drink reaches the
nozzle (the line is empty after cleaning; empty the glass as needed). Put the lantern on and do one full test
pour into the glass: the first pour of the night should not be the one in front of a guest. Then the empty
glass goes in and you are ready.

**Charging:** S1 OFF, TalentCell pack switch ON, USB unplugged. Lift the lantern off (3 thumbscrews)
and plug the supplied TalentCell 12.6 V charger into the jack on the deck: it points up at the deck's edge on your left, a
little toward the display side (the side away from the buck converter). The lantern can go back on while it charges if you
route the charger lead out under the rim on blocks, or just leave it beside the cartridge. A full charge takes about 6 h at the charger's 0.5 A. Charge after
every party, or whenever `status` reads below about 11.5 V (roughly half): the strip dims as the pack drains.
The double blink as you punch in (below 10.5 V) is a late warning. Runtime and state of charge versus voltage
need checking on the assembled prop; do not treat the voltage threshold as a precise 50% fuel gauge.

**Refilling** (about 2 minutes):
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
   Connect USB serial using section 4’s power procedure.
   Empty the jar, half-fill it with warm water, and put the shot glass in its slot.
2. `cal 8000` pours about 22 mL into the glass. Empty the glass and repeat 4 or 5 times. Only the shot
   glass fits under the nozzle, so keep each run short: `cal 20000` would pour ~55 mL and overflow it.
3. Unscrew the jar lid and hold the pickup tube out of the water. Run `cal 8000` twice more to push the
   line empty.
4. Rinse the jar, the lid and its vent valve. Open the pump head and lift the tube off the rollers. Let
   everything air-dry with the tube ends open.

 Never leave liqueur in the tube overnight: the sugar gums up the bore and the rollers.
Store with S1 and the TalentCell switch OFF, USB unplugged, and the head open so the tube is not crushed for months. Replace the pump tube when it looks cloudy or
flattened.

---

## 14. Troubleshooting

| Symptom | Check |
|---|---|
| Ring not detected | Are both cable plugs connected (easy to forget after a refill)? `status` with the ring in. Is the A3144 printed face up on its post? Is the magnet's switching face facing out of the key cap (section 6, step 2)? Is pin 1 on 5 V? |
| Ring won't seat in the pocket | The rotor is not at rest: turn it back by hand (and grease it, section 6 step 4). The key cap's tab must point at the rest notch. |
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
is a squat jar because it shares the deck with the pump under the lower dish. The glass sits about 5 cm down in
a slot because the sphere is only 10 cm tall inside and your fist and the lock need the space above it; that is
also why it slides toward you before it lifts out. The early research notes are in `docs/research/`; they are partly superseded, and the
current numbers are the ones in this guide and in `cad/params.py`.
