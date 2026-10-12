# Green Lantern power battery that pours a shot: build guide (budget build, ~$140)

A 3D-printed Green Lantern power battery, about 47 cm tall and 18 cm across, with a hidden pump, a hidden
shot glass and a twist-to-pour ring socket. Insert the ring and the lantern starts to glow. Recite the oath
while it brightens. Twist the ring 45 degrees on the last line: it goes to full brightness and pours about
1 oz into the glass in roughly 9 seconds. Open the hatch on your side, pull the tray, hand over the glass.

![interaction timeline](images/interaction.svg)

**Status.** Designed, modelled and simulated; not yet built. The firmware compiles and passes 17 simulated
safety scenarios (`firmware/test`). The CAD passes its fit checks. Two things must be measured on the real
parts before you print the big pieces: the Kamoer pump's outline and your jar. Every bay is parametric
(`cad/params.py`), so a measured number is a one-line change and a re-run of `python3 build.py`.

---

## 1. How it works

```
 ring with a 6x2 mm magnet in a printed key cap  -> Hall sensor under the socket  -> ARMED: the light starts to climb
 recite the oath (the light brightens steadily for 15 s, then holds)
 twist the ring 45 deg                            -> a cam on the rotor clicks a microswitch
 firmware: ring present AND switch AND no pour yet this insertion -> full brightness, pump runs ~9 s
 let go: the rotor springs back. The prop stays LOCKED until the ring is removed.
```

| Where | What is inside |
|---|---|
| Top dish | The charging socket: a rotor with the keyed ring pocket, 0 and 45 degree hard stops, a spring plunger that returns it, a cam, the D2F-L microswitch and the DRV5032 Hall sensor. Four M3 screws hold it in. |
| Sphere | The shot glass on a slide-out tray behind a hinged hatch on your side. Rows of green LED strip on a carrier plate behind the white diffuser window on the audience side. The nozzle clip above the glass. |
| Lower dish | Hollow neck: the tube and the socket cable pass through it. |
| Base | The jar reservoir and the Kamoer pump on a deck, the power bank flat on the floor under the deck, the electronics board, the buck converter. Rear door for refilling and charging. |

![fluid path and layout](images/fluid-path.svg)

The drink touches only the jar, the platinum-silicone tube and the glass. No printed part is in the liquid path.

---

## 2. Shopping list

Prices with "~" are estimates: Amazon hid some prices from my lookups, and the LED strip, buck module and
Vetco parts were not checked listing by listing. Confirm at checkout.

### 2.1 Order online

| # | Item | Buy | Price | Notes |
|---|---|---|---|---|
| 1 | Pump | [Kamoer KPHM200, 12 V (B09HGVLHFV)](https://www.amazon.com/dp/B09HGVLHFV) | $28 | 200 mL/min or more at 12 V, 0.7 A. 1 oz in about 7-9 s. |
| 2 | Tubing | [AUBER 1/8" ID x 1/4" OD platinum-cured silicone, 10 ft (B0DKB1NKB4)](https://www.amazon.com/dp/B0DKB1NKB4) | $14 | The exact 3.2 x 6.4 mm size the Kamoer head needs. FDA 21 CFR 177.2600, NSF 51. Thinner 1/8" x 3/16" tube will not pump. |
| 3 | LED strip | [12 V green LED strip, single colour](https://www.amazon.com/s?k=12V+green+LED+strip+single+color+2835+60+LED) | ~$12 | Pick: 12 V, green only (not RGB), 2835 or 5050 LEDs, 60 LEDs/m, 8 or 10 mm wide, cuttable every 3 LEDs (5 cm). You use 90 cm. |
| 4 | Buck converter | [LM2596 step-down module, multipack](https://www.amazon.com/s?k=LM2596+buck+converter+module) | ~$8 | 12 V in, set to 5.0 V out for the XIAO and the level shifter. 43 x 21 mm. |
| 5 | Magnets | [6 x 2 mm neodymium, 45-pack (B0CBRVF4PN)](https://www.amazon.com/dp/B0CBRVF4PN) | ~$7 | 1 in the ring key, 4 in the hatch, 8 in the base door. |
| 6 | Microcontroller | [Seeed XIAO RP2040, pre-soldered (B0DRNTQ338)](https://www.amazon.com/dp/B0DRNTQ338) | ~$10 | |
| 7 | Hall sensor | [Adafruit DRV5032 breakout #6051](https://www.adafruit.com/product/6051) | $4.95 | Runs on 3.3 V, very sensitive, either magnet pole works. |
| 8 | 12 V cable | [Adafruit USB-C PD 12 V trigger cable #5450](https://www.adafruit.com/product/5450) | $7.95 | Asks the power bank for 12 V. You cut the barrel plug off. |
| | Adafruit shipping | | ~$8 | Ships from Brooklyn in 1-2 business days; USPS Ground Advantage is 2-5 more. Order it first. |

**Faster alternative to the Adafruit order.** Use the [wininks USB-C PD 12 V cable (B0FD9P7PV4)](https://www.amazon.com/dp/B0FD9P7PV4)
(~$10) and an A3144 Hall sensor from Vetco ($1.99). The A3144 needs 5 V and a diode on its output (section 4)
and is less sensitive: bend its leads so it stands up through the sensor window, and stack two magnets in
the key cap. Saves the shipping wait; costs about $7 less.

### 2.2 Pick up locally (or order the Amazon kit in brackets)

| # | Item | Where | Price | Notes |
|---|---|---|---|---|
| 9 | Lever microswitch, D2F-L size | Vetco ([or the 4-pack, B0DBV8XGG4](https://www.amazon.com/dp/B0DBV8XGG4), ~$8) | ~$3 | Body 12.8 x 5.8 x 6.5 mm, two mounting holes 6.5 mm apart, hinge lever. The socket bracket is built for this size: take calipers to the store. |
| 10 | 74AHCT125 quad buffer, DIP-14 | Vetco, VUPN524 | $2.95 | Turns the XIAO's 3.3 V into a clean 5 V gate signal for both MOSFETs. |
| 11 | 2 x logic-level N-MOSFET | Vetco | ~$3 | IRLZ44N or similar, TO-220, at least 3 A at 12 V. |
| 12 | Small parts | Vetco | ~$12 | 2 x 1N5819 diodes, 2 x 10 k resistors, 1 x 0.1 µF ceramic, 1 x 2200 µF 16 V electrolytic, a 5 x 7 cm perfboard (protoboard VUPN2924, $3.49), a 14-pin DIP socket, 22 AWG wire, heat-shrink. |
| 13 | M3 screws and nuts | Tacoma Screw, by the piece ([or the M3 kit, B0HKFCTLK8](https://www.amazon.com/dp/B0HKFCTLK8), ~$18) | ~$12 | 5 x M3x6, 11 x M3x8, 4 x M3x10, 17 x M3x12, 10 nuts. They thread straight into the printed holes. |
| 14 | Compression spring | Vetco (Hillman, $1.29) or any spring drawer | ~$1 | 0.5 mm wire, 5 mm outside diameter, about 10 mm long. Bring calipers. |
| 15 | Super glue | anywhere | ~$5 | For the magnets and the key cap. |

**Total: about $140.** That assumes you already have:

- **A power bank with a 12 V USB-C output.** Look for "12V⎓1.5A" printed on the bank or on its listing. If
  yours lacks it, the [INIU B61 (B09176JCKZ)](https://www.amazon.com/dp/B09176JCKZ) has it (~$21).
- **PETG filament.** About 0.9 kg of green plus a little white or natural for the diffuser (~$40 if you need two spools).
- **A food-safe jar no bigger than 76 mm across and 76 mm tall** (an 8 oz straight-sided PET jar, ~$8 if you need one).
- **A 1.5 oz shot glass** up to 52 mm across the top and 62 mm tall (Libbey 1.5 oz glasses fit).
- Basic tools: soldering iron, multimeter, calipers, a drill with 2.5 mm and 6 mm bits, flush cutters.

### 2.3 Seattle-area stores (verified open on 2026-10-11; call before driving for specific stock)

| Store | Address, hours | Buy here |
|---|---|---|
| [Vetco Electronics](https://vetco.net) | 12718 Northup Way STE 100, Bellevue 98005, (425) 641-7275. Mon-Fri 9-6, Sat 10-3:30 | Diodes, resistors, capacitors, MOSFETs, the 74AHCT125, microswitches, perfboard, DIP sockets, wire, heat-shrink, A3144, Hillman springs. Not stocked: XIAO, magnets. |
| [Tacoma Screw Products, Ballard](https://www.tacomascrew.com/LocationFinder) | 3930 Leary Way NW, Seattle 98107, (206) 632-7565. Mon-Fri 7-5, Sat 9-1 | M3 screws and nuts by the piece, springs. Georgetown branch: 1121 S Bailey St, Mon-Fri 7-5. |
| [McLendon Hardware](https://www.mclendons.com/locations) | White Center: 10210 16th Ave SW, Seattle 98146. Renton: 440 Rainier Ave S | Spring drawers, metric screws, glue. |
| Stoneway Hardware, Ace stores (Magnolia, Maple Leaf, Junction) | Seattle neighbourhoods | Fasteners by the piece, spring drawers, glue. |
| [Bargreen Ellingson](https://www.bargreen.com/locations/seattle) | SoDo showroom, Mon-Fri 10-3 | 1.5 oz shot glasses. |
| [Micro Homebrew](https://www.microhomebrew.com/) | Kenmore, (425) 892-8425 | Small food-safe bottles and jars. They do not stock the 1/8" pump tubing. |

Hardwick's in the U-District closed in 2020. Sound Homebrew Supply could not be confirmed open.

---

## 3. Print the parts

All files are in `cad/output/` (STL for slicing, STEP for editing). Everything fits your 230 x 230 x 240 mm
Ender 3. The widest part is the rear sphere half at 221 mm (because of the handle bosses), the tallest is the
base at 115 mm. Centre the big parts and use a skirt, not a brim.

**PETG settings (0.4 mm nozzle):** 0.2 mm layers, nozzle 235-245 C, bed 75-85 C, 4 perimeters, 5 top and
bottom layers, 25-30 % gyroid infill, outer walls 40-60 mm/s, fan off for the first 3 layers then 30-50 %.
Textured PEI, or glue stick on smooth PEI. Do not anneal.

**Screws go straight into the plastic.** Every screw hole is a 2.7 mm pilot. Drive each M3 in slowly the
first time so it cuts its own thread, and don't over-tighten. If a hole strips, a heat-set insert rescues it
(see section 15).

Print these first, before any big part, and check them:

1. `socket_housing`, `rotor`, `socket_base`, `plunger`: the rotor turns 45 degrees with slight drag and the
   plunger snaps it back. If it binds, raise `FIT` in `cad/params.py` by 0.05 and reprint the rotor.
2. `key_cap`: drops into the rotor pocket one way only, with a little play.
3. `sphere_hatch` with its magnets: the latch holds.

### Part list

| Part | Size (mm) | Orientation on the bed | Supports | Colour | ~g |
|---|---|---|---|---|---|
| `base` | 180 x 180 x 115 | floor down, open top up | no | green | 175 |
| `base_deck` | 169 x 167 x 47 | flat | no | green | 72 |
| `base_door` | 118 x 25 x 94 | standing on its lip edge | no | green | 37 |
| `dish_lower` | 180 x 180 x 91 | mouth down | no | green | 155 |
| `dish_upper` | 180 x 180 x 86 | floor down, mouth up | no | green | 152 |
| `sphere_front` | 180 x 138 x 80 | split face down, dome up | inside only, around the window (tree) | green | 51 |
| `sphere_rear` | 221 x 117 x 79 | split face down, dome up | inside only, around the hatch (tree) | green | 51 |
| `sphere_hatch` | 120 x 101 x 45 | convex side up | no | green | 46 |
| `diffuser` | 118 x 118 x 1 | flat, 100% infill | no | white | 8 |
| `led_carrier` | 110 x 106 x 26 | flat, channels up | no | white | 14 |
| `bay_floor` | 131 x 131 x 10 | flat | no | any | 45 |
| `glass_tray` | 60 x 82 x 10 | flat | no | any | 9 |
| `nozzle_clip` | 30 x 12 x 10 | flat | no | any | 2 |
| `handle_leg_left` | 14 x 126 x 10 | flat | no | green | 12 |
| `handle_leg_right` | 14 x 126 x 10 | flat | no | green | 12 |
| `handle_arc_left` | 120 x 132 x 10 | flat | no | green | 18 |
| `handle_arc_right` | 120 x 132 x 10 | flat | no | green | 17 |
| `socket_housing` | 100 x 100 x 10 | faceplate down | no | green | 30 |
| `rotor` | 44 x 37 x 8 | top face down | no | green | 5 |
| `socket_base` | 76 x 76 x 4 | top face down | no | any | 11 |
| `switch_bracket` | 16 x 10 x 6 | flat | no | any | 0 |
| `plunger` | 5 x 5 x 4 | nose up | no | any | 0 |
| `key_cap` | 28 x 24 x 3 | flat face down | no | green | 1 |
| **Total** | | | | | **~922 g** |

Supports: none, except inside the two sphere halves. Print them split-face down; the last 15 mm of dome
around the window and the hatch overhang more than 45 degrees, so enable tree supports on the inside only.
The diffuser should be white or natural PETG, 0.8 mm, 100 % infill: a green diffuser works but is dimmer.

![all printed parts](images/cad-parts-sheet.png)

![assembly](images/cad-assembly-iso.png) ![cutaway](images/cad-cutaway.png)

---

## 4. Electronics (build it on the bench first)

![wiring diagram](images/wiring.svg)

Build the circuit on the 5 x 7 cm perfboard and test it before anything goes into the lantern.

1. **XIAO and U1.** Solder two 1x7 female header strips 15.24 mm apart for the XIAO, or solder it straight to
   the board. Solder the 14-pin DIP socket for the 74AHCT125 (U1).
2. **12 V in.** Cut the barrel plug off the PD cable. Plug the cable into the power bank and check with the
   meter that the centre wire reads about +12 V. Centre wire to the +12 V rail, outer wire to ground.
   Solder C2 (2200 µF 16 V) across the rail, stripe (−) to ground.
3. **5 V.** Wire the LM2596's IN+ and IN− to the 12 V rail and ground. **Turn its little screw until OUT reads
   5.0 V on the meter before connecting anything to it.** Then OUT+ feeds U1 pin 14, and also the XIAO's 5V pin
   through a 1N5819 (stripe toward the XIAO). That diode lets you plug the XIAO into a laptop without feeding
   the lantern. Even so, unplug the power bank while flashing.
4. **U1 (74AHCT125).** Pin 14 to +5 V, pin 7 to ground, 0.1 µF between them. The four OE pins (1, 4, 10, 13)
   and the unused inputs (9, 12) to ground. XIAO D3 to pin 2 (pump), XIAO D4 to pin 5 (light). A 10 k from D3
   to ground and another from D4 to ground, so nothing switches on while the XIAO boots.
5. **MOSFETs.** IRLZ44N pins, facing the label, left to right: gate, drain, source. Q1 (pump): gate from U1
   pin 3, source to ground, drain to the pump's − wire. Q2 (light): gate from U1 pin 6, source to ground, drain
   to the LED strip's − wire. The pump's + and the strip's + go to the +12 V rail.
6. **Flyback diode.** Solder a 1N5819 across the pump's two wires, stripe on the + side. It protects Q1 from
   the motor's voltage spike when it switches off.
7. **Socket wires.** DRV5032: VIN to the XIAO's 3V3, GND to ground, OUT to D1. Microswitch: NO to D2, COM to
   ground. Use one 4-wire cable (3V3, HALL, SW, GND) from the socket down to the board.
8. **Check before connecting the pump.** Flash the firmware (section 5), open the serial console, type
   `status`. Hold a magnet over the Hall sensor and press the switch lever: `ring=present` and
   `switch=pressed` should follow. Then connect the strip: it should glow faintly.

An optional PRIME button goes between D6 and ground. Holding it runs the pump only when no ring is in.
It's not in the parts list; the serial `cal` command or a test pour does the same job.

---

## 5. Firmware

Source: `firmware/green_lantern/green_lantern.ino`. Board: Seeed XIAO RP2040 on the "Raspberry Pi
Pico/RP2040" Arduino core by Earle Philhower. No extra libraries.

**Arduino IDE.** Boards Manager: install "Raspberry Pi Pico/RP2040" (Earle Philhower). Select "Seeed XIAO
RP2040", open the sketch, upload. If no port appears, hold the XIAO's BOOT button while plugging it in.

**Command line.**

```bash
cd firmware
arduino-cli core install rp2040:rp2040 --additional-urls https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
arduino-cli compile --fqbn rp2040:rp2040:seeed_xiao_rp2040 green_lantern
arduino-cli upload  --fqbn rp2040:rp2040:seeed_xiao_rp2040 -p /dev/ttyACM0 green_lantern
cd test && make test     # 17 simulated scenarios, all must PASS
```

![state machine](images/state-machine.svg)

| Pin | Function |
|---|---|
| D1 | Hall sensor OUT (LOW = ring present) |
| D2 | Microswitch NO (COM to GND) |
| D3 | Pump, through U1 to Q1 |
| D4 | LED strip, through U1 to Q2 |
| D6 | Optional PRIME button to GND |

Serial console at 115200 baud. Type a command and press Enter:

| Command | What it does |
|---|---|
| `status` | Shows state, ring, switch, pump, pour time, speed, brightness, idle glow. |
| `cal 10000` | Runs the pump 10 s without the ring, for calibration (only when idle). |
| `pour 9000` | Pour time in ms (500 to 20000). |
| `speed 80` | Pump speed in percent (30 to 100). Lower = slower, longer pour for the same volume. |
| `leds 255` | Maximum LED brightness, 0 to 255. |
| `idle 20` | The faint glow when idle, 0 to 255. Raise it if the power bank switches itself off. |
| `save` | Stores pour time, speed, brightness and idle glow so they survive a power cycle. |
| `stop` | Stops the pump now. |

`RAMP_MS` near the top of the sketch is how long the light takes to climb after the ring goes in (15000 ms by
default). Set it to the length of your oath and re-upload.

**Safety interlocks, all tested in simulation:** pump off at boot. The switch alone never pumps; the ring
alone never pumps. One pour per insertion. Pulling the ring mid-pour stops the pump within about 60 ms. A
switch already pressed at boot or at insertion is ignored until released. A 20 s hard cap applies to every
pump run.

---

## 6. The charging socket

![socket mechanism](images/socket-mechanism.svg)

Parts: `socket_housing`, `rotor`, `socket_base`, `switch_bracket`, `plunger`, `key_cap`. Plus 4 x M3x8 for the
faceplate, 3 x M3x8 and 3 nuts for the base plate, 1 x M3x6 and a nut for the switch bracket, the spring,
the microswitch, the DRV5032 board and one magnet.

The rotor is a flat 36 mm disc. Under the faceplate lip its edge carries three features: a stop lug in a
channel whose ends are the 0 and 45 degree stops, a cam that presses the switch lever 3 mm between 33 and
45 degrees, and a ramp that pushes the spring plunger out so the rotor snaps back when you let go.

1. **Nuts.** Drop M3 nuts into the three hex pockets on the underside of `socket_housing` and the one under
   `socket_base`. A dab of super glue holds each.
2. **Ring key.** Glue the magnet into the pocket under `key_cap` (either pole works with the DRV5032). Scuff
   the ring's flat face and the key cap, and glue the key cap on with the tab pointing along the finger.
3. **Hall sensor.** Lay the DRV5032 board in the pocket under `socket_base`, components down. The pocket is
   longer than the board: slide it until its chip sits under the square window on the axis, then hold it
   with two dots of glue. The magnet ends up about 8 mm above the
   chip, which the DRV5032 detects easily.
4. **Rotor and plunger.** Turn `socket_housing` upside down. Drop the spring into the straight radial pocket,
   then the `plunger` nose-first on top. Hold it with a finger and lower the `rotor` into the bore, lugs down
   into their channels, key-pocket tab toward the faceplate's +X screw hole. Twist to 45 degrees and let go:
   it must snap back every time. Too stiff to twist with a finger: use a softer spring (0.4 mm wire).
5. **Switch.** Press the microswitch onto the two pegs of `switch_bracket`, lever toward the rotor. Screw the
   bracket loosely into its recess in `socket_base` (M3x6 through the slot into the nut).
6. **Close and tune.** Screw `socket_base` onto the housing (3 x M3x8). Twist slowly: the lever should start to
   move at about 33 degrees and click at about 40, before the stop at 45. Slide the bracket in its slot to
   tune, then tighten. The switch must never be what stops the rotor.
7. **Cycle it 50 times** and watch `status`: `switch=pressed` only near the end of the twist, `ring=present`
   for the whole twist.
8. **Mount** with 4 x M3x8 through the faceplate into the top dish floor. Route the socket cable through the
   slot in the dish floor.

---

## 7. The fluid path

1. **Jar lid.** Drill a 6 mm hole near the edge for the tube and a 2.5 mm vent hole on the other side. Push the
   tube through the 6 mm hole (it seals itself) until it reaches 5 mm above the jar's bottom.
2. **Pump head.** Open the Kamoer's head cap, lay the tube around the rollers, close the cap. Use one
   continuous piece of tube from the jar to the nozzle: no joints, nothing to leak.
3. **Route.** The pump sits in its saddles on the deck, head toward the rear door so you can open the cap
   later, held by a strap or zip tie. The tube goes up through the lower dish neck, through the hole in
   `bay_floor`, up the rear-left wall of the sphere into `nozzle_clip`.
4. **Nozzle.** The clip holds the tube end at 45 degrees, aimed at the inside wall of the glass, about 10 mm
   above the rim. Aiming at the wall hides splash and catches the last drop.
5. **Prime.** Water in the jar, then `cal 6000` from the laptop (or a pour into a cup) until water reaches
   the nozzle. The tube stays full between pours.

---

## 8. The sphere

1. **LED carrier.** Cut the strip into 18 pieces of 3 LEDs (5 cm each, cut on the copper pads). Stick two
   pieces end to end in each of the 9 channels of `led_carrier`, LEDs facing out. Wire every + pad together
   and every − pad together (thin wire, short jumpers between the pieces, row to row). Direction doesn't
   matter on a single-colour strip. Run one + and one − lead down to the board.
2. **Diffuser.** It sits on the ledge behind the front window. The carrier stands 25 mm behind it on its four
   posts, with its tabs in the slots of `bay_floor`.
3. **Bay floor and tray.** `bay_floor` sits on the lower dish floor inside the sphere. `glass_tray` slides on
   its two rails; the glass stands in the tray's ring. Pull the tab to bring the glass out through the hatch.
4. **Hatch.** Glue 2 magnets into the door's lip and 2 into the sphere's rebate so that each pair attracts and
   the faces touch when it's closed. Mark the polarity with a pen before gluing. The door's two pins snap into
   the holes at the bottom of the opening.
5. **Nozzle clip.** One M3x8 into the boss on the rear half's inside wall, above and behind the glass.
6. **Join the halves.** Feed the socket cable and the LED leads up the inside of the rear half, fit the two
   alignment pins, then 4 x M3x10 through the rear half's flange into the front half.

---

## 9. Final assembly

Bottom to top:

1. `base`. Power bank flat on the floor, held with a strap. `base_deck` drops in on top of it (3 x M3x8 into
   the pillars). Jar in its ring, pump in its saddles. Electronics board on the deck's vertical panel
   (4 x M3x6). LM2596 in the left floor crescent.
2. `dish_lower`: its spigot goes into the base top, 3 x M3x12 from outside.
3. The assembled sphere onto the lower dish's locating ring, 3 x M3x12.
4. `dish_upper` with the socket onto the sphere's top, 3 x M3x12.
5. Handle: the legs plug into the sphere's bosses (1 x M3x12 each), the two arcs lap-joint to the legs and to each
   other with 6 x M3x12 and nuts.
6. `base_door` with its 4 magnets snaps onto the back. Glue 4 matching magnets into the door frame first.

Keep the pump wires twisted and away from the Hall and switch wires. To turn the lantern off, open the door
and unplug the cable from the power bank.

---

## 10. Calibration

Water in the jar, a measuring cup under the nozzle, laptop on the serial console:

```
cal 10000        measure the volume; repeat 3 times and average
flow_mL_per_s  = volume_mL / 10
pour time (ms) = target_mL / flow_mL_per_s * 1000      e.g. 30 mL at 3.3 mL/s -> 9000
pour 9000
save
```

Then repeat with the real drink: liqueur is thicker than water and the nozzle is 20 cm above the pump, so
expect a little less flow. Target 30-37 mL (1 to 1.25 oz) in a 1.5 oz glass so it can be carried.

If the pour finishes before your light show does, slow the pump instead of shortening the show: `speed 70`,
then re-measure and set `pour` again.

---

## 11. Test before the party

- [ ] Power on: faint glow, pump silent.
- [ ] Twist the empty socket: nothing.
- [ ] Insert the ring: the glow climbs steadily, no pump.
- [ ] Twist: full brightness, the pump runs the calibrated time. Let go: the rotor returns.
- [ ] Twist again with the ring still in: nothing.
- [ ] Remove the ring and reinsert it, twist: one new pour.
- [ ] Pull the ring out mid-pour: the pump stops at once.
- [ ] 20 water pours in a row: every pour lands in the glass, no drips anywhere.
- [ ] Carry and tilt the lantern with water in it, then leave it 30 minutes: dry inside.
- [ ] The power bank stays on after 20 minutes idle (if not: `idle 40`, `save`).
- [ ] The hatch stays shut when the lantern swings.

---

## 12. Performing it

Set the lantern on a table or hang it on your forearm: one hand does the ring, the other opens the hatch
afterwards. Glass on the tray, tray in, hatch shut. Insert the ring, speak, twist on the last line and hold
the twist for a moment, then let go: the pour carries on by itself. Remove the ring (that re-arms the prop),
open the hatch, pull the tray, hand over the glass. Refill the jar through the rear door.

---

## 13. Cleaning and storage

Same night: put warm water in the jar and run `cal 20000` into a cup twice, then once more with the tube
out of the water to push the line empty. Open the pump head and lift the tube off the rollers. Let it air-dry
with both ends open. Never leave liqueur in the tube overnight: the sugar gums up the bore and the rollers.
Store with the head open so the tube isn't crushed for months. Replace the pump tube when it looks cloudy or
flattened.

---

## 14. Troubleshooting

| Symptom | Check |
|---|---|
| Ring not detected | `status` with the ring in. Is the DRV5032 chip under the window, on the axis? Is the magnet glued in the key cap? |
| No pour on the twist | `status` while twisting: the switch must read `pressed` before the hard stop. Slide the switch bracket toward the cam. |
| Pump hums, no flow | Tube not seated under the rollers, head cap open, or the wrong (thin-walled) tube. |
| Pump doesn't run at all | Check the PD cable gives 12 V (meter). Check Q1's pins (gate, drain, source) and the 10 k on D3. |
| XIAO resets when the pump starts | 12 V sagging: C2 missing, bank nearly empty, or the bank doesn't really offer 12 V. |
| LEDs stay dark or stay on | Q2 wiring, or U1's OE pins not grounded. |
| Power bank switches off when idle | `idle 40` then `save`; or turn on the bank's low-current mode if it has one. |
| Rotor sticks | Clean PETG strings out of the bore, sand lightly, or reprint the rotor with `FIT` + 0.05. |
| Drips after the pour | Lower the nozzle a little or trim the tube end square. |

---

## 15. What this budget build leaves out, and how to add it back

| Upgrade | Cost | How |
|---|---|---|
| Glowing ring around the socket (24-pixel NeoPixel ring + translucent halo) | ~$17 | Set `LED_RING = True` in `cad/parts/socket.py`; the ring needs addressable-LED code, which is in the git history before the budget change. |
| Heat-set inserts instead of screwing into plastic | ~$10 | Set `M3_INSERT_HOLE = 4.0` in `cad/params.py` and re-run `build.py`. Inserts: [ruthex M3 x 5.7 mm (B08BCRZZS3)](https://www.amazon.com/dp/B08BCRZZS3). |
| Master power switch and fuses | ~$8 | Set `DOOR_SWITCH_D = 12.5` in `cad/parts/base.py` for a switch hole in the door. Put the switch and a 2 A slow-blow fuse in the 12 V lead. |
| PRIME button | ~$2 | 12 mm momentary button from D6 to ground. Already supported by the firmware. |
| Pinch clamp for carrying a full jar | ~$6 | [Tubing pinch clamps (B0FCM98N2Q)](https://www.amazon.com/dp/B0FCM98N2Q). |

**Why these choices.** The Kamoer pump states 200 mL/min as a minimum, so it reliably pours 1 to 1.25 oz in
10-15 s. Two Adafruit 5 V pumps state 100 mL/min each as a maximum and often miss that window. A plain LED
strip is enough for a glow that just gets brighter, and it runs from the same 12 V as the pump. The reservoir
is a squat jar because a tall bottle cannot leave the base through the door. The glass sits on a slide-out
tray because reaching into a dark 18 cm sphere one-handed doesn't work. The research behind every number is
in `docs/research/`.
