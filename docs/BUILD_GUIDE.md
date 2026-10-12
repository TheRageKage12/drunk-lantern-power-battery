# Green Lantern power battery that pours a shot: build guide

A 3D-printed Green Lantern power battery, about 47 cm tall and 18 cm across, with a hidden peristaltic
pump, a hidden shot glass, and a twist-to-pour ring socket. Insert the ring, recite the oath, twist the
ring 45 degrees on the last line: the lantern flashes and fills the glass while the light show runs.
Pull the tray out of the hatch on the back and take the glass.

![interaction timeline](images/interaction.svg)

**Status of this guide.** Everything here was designed and cross-checked on paper and in CAD; no physical
prototype has been built yet. Component sizes come from manufacturer pages and Amazon listings that were
fetched and double-checked (see `docs/research/`), but two things must be measured on the real parts before
you glue anything: the Kamoer pump's exact outline and mounting holes (Kamoer does not publish a drawing) and
your jar's cap diameter. Every bay in the CAD is parametric (`cad/params.py`), so a measured number is a
one-line change and a re-run of `python3 build.py`.

---

## 1. How it works

```
 ring (6x2 mm magnet in a printed key cap)      -> Hall sensor under the socket floor   -> ARMED (slow green pulse)
 recite the oath, then twist the ring 45 deg    -> cam on the rotor presses a microswitch -> FLASH
 firmware: ring present AND switch AND not yet poured                                    -> pump runs ~9 s (30 mL)
 rotor springs back when you let go; the prop stays LOCKED until the ring is removed     -> remove ring -> IDLE
```

| Where | What is inside |
|---|---|
| Top dish | The charging socket: rotor with the keyed ring pocket, 45 degree hard stops, return spring, cam, D2F-L microswitch, DRV5032 Hall sensor, 24-pixel NeoPixel ring under a translucent halo. Removable: four M3 screws. |
| Sphere | Hidden shot glass on a slide-out tray behind a hinged, magnet-latched hatch (your side). WS2812B strip on a white carrier plate behind the green diffuser window (audience side). Nozzle clip above the glass. |
| Lower dish | Hollow neck: the tube and the socket cable pass through it. |
| Base drum | 8 oz jar reservoir, Kamoer KPHM200 pump, USB-C power bank, electronics board, master switch and PRIME button in the rear door. |

![fluid path and internal layout](images/fluid-path.svg)

The beverage touches only the jar, the platinum-silicone tube and the glass. No printed part is in the
liquid path.

---

## 2. Shopping list

Links are to Amazon where a listing was confirmed (fetched on 2026-10-11; Amazon hides some prices from
automated readers, so "~" prices are estimates). For small parts sold only in big packs, the **Local**
column names a Seattle-area store that sells singles. Store details are in section 2.5.

### 2.1 Electronics

| # | Item | Buy | Price | Local option | Notes |
|---|---|---|---|---|---|
| 1 | Microcontroller | [Seeed XIAO RP2040, pre-soldered (B0DRNTQ338)](https://www.amazon.com/dp/B0DRNTQ338) | ~$10 | Vetco does not stock it | 3.3 V logic. |
| 2 | Ring sensor | [Adafruit DRV5032 Hall breakout #6051](https://www.adafruit.com/product/6051) | $4.95 | Vetco: A3144EUA $1.99 (5 V part, needs the diode interface in section 5) | Runs from 3.3 V, 10x more sensitive than the A3144, omnipolar. The HiLetgo A3144 5-pack ([B01NBE2XIR](https://www.amazon.com/dp/B01NBE2XIR)) works as the alternative. |
| 3 | Twist switch | [D2F-L lever microswitch, 4-pack (B0DBV8XGG4)](https://www.amazon.com/dp/B0DBV8XGG4) | ~$8 | Vetco: lever microswitch TEA-A-7038 $2.99 | Omron D2F-L equivalent. Lever force 0.78 N max. |
| 4 | Pump driver | [Dual D4184 MOSFET trigger module, 6-pack (B0FMJH3DML)](https://www.amazon.com/dp/B0FMJH3DML) | ~$10 | | 5-36 V, 15 A; one module used. |
| 5 | Level shifter | [SN74AHCT125N DIP-14, 10-pack (B08R6BCSYC)](https://www.amazon.com/dp/B08R6BCSYC) | ~$8 | Vetco: 74AHCT125 VUPN524 $2.95 | Three channels used: ring data, strip data, pump trigger. |
| 6 | Socket LEDs | [Adafruit NeoPixel Ring 24 #1586](https://www.adafruit.com/product/1586) | $16.95 | | 65.5 mm OD, fits around the rotor. |
| 7 | Sphere LEDs | [BTF-LIGHTING WS2812B 5 V, 60 LED/m, 1 m, IP30 (B01CDTED80)](https://www.amazon.com/dp/B01CDTED80) | $8.99 | Vetco: 1 m WS2812 strip VUPN2314 $19.95 | Cut into 9 rows of 6 (54 px) on the white carrier plate. |
| 8 | Power bank | [INIU B61 10,000 mAh 22.5 W (B09176JCKZ)](https://www.amazon.com/dp/B09176JCKZ) | ~$21 | | USB-C PD with a 12 V/1.5 A profile: this is what makes the single-cable 12 V design work. 104 x 66 x 23 mm. |
| 9 | 12 V cable | [wininks USB-C PD trigger cable, fixed 12 V, 5.5 x 2.1 mm (B0FD9P7PV4)](https://www.amazon.com/dp/B0FD9P7PV4) | ~$10 | | Negotiates 12 V from the bank. [Adafruit 5450](https://www.adafruit.com/product/5450) ($7.95, 5.5 x 2.5 mm plug) is equivalent. |
| 10 | 12 V to 5 V buck | [Pololu D24V22F5 5 V 2.5 A regulator #2858](https://www.pololu.com/product/2858) | $18.95 | | Feeds the XIAO and LEDs. Cheaper alternative: any [LM2596 module](https://www.amazon.com/s?k=LM2596+buck+converter+module+3A) (43 x 21 x 14 mm, set to 5.0 V with a meter before connecting anything). |
| 11 | Diodes | [1N5819 Schottky, 100-pack (B079KG1TN2)](https://www.amazon.com/dp/B079KG1TN2) | ~$6 | Vetco (singles) | Three used: pump flyback, XIAO 5 V feed, A3144 interface if you use that sensor. |
| 12 | Resistors | 330 ohm x2, 10 k x2, 1/4 W | ~$1 | Vetco (singles) | Any kit works ([Adafruit 2781](https://www.adafruit.com/product/2781) 470 ohm 25-pack is fine for the data lines). |
| 13 | Capacitors | [1000 uF 10 V, 10-pack (B07SD7376B)](https://www.amazon.com/dp/B07SD7376B); 2200 uF 16 V x1; 100 nF ceramic x3 | ~$8 | Vetco (singles) | 1000 uF on the 5 V rail at the LEDs, 2200 uF on the 12 V rail at the pump module, 100 nF on the AHCT125 and the Hall line. |
| 14 | Fuses | 2 inline 5 x 20 mm holders + T2A and T3A slow-blow | ~$8 | Vetco: holder VUPN643 $2.99, slow-blow 5-packs $6.50-7.50 | [This kit (B0B684JNKK)](https://www.amazon.com/dp/B0B684JNKK) has holders but only fast-blow fuses; use 3 A fast on the 5 V leg and 2 A fast on the 12 V leg if that is what you have. |
| 15 | Master switch | [Adafruit 916 16 mm latching metal button with LED](https://www.adafruit.com/product/916) | $4.95 | Vetco: thin rocker 6 A VUPN1102 $2.99 | The door panel has a 19 x 13 mm rocker cutout; a 16 mm button needs a 16 mm hole instead (edit `DOOR_SWITCH_D` in `cad/parts/base.py`). |
| 16 | PRIME button | [12 mm panel-mount momentary push button](https://www.amazon.com/s?k=12mm+momentary+push+button+switch+panel+mount) | ~$6 | Vetco (single) | Hidden inside the service door. Hold it to run the pump for priming. |
| 17 | Perfboard | [5 x 7 cm double-sided perfboard, 2-pack (B07FTMJPHX)](https://www.amazon.com/dp/B07FTMJPHX) | ~$6 | Vetco: protoboard VUPN2924 $3.49 | Mounts on the base deck's electronics panel (40 x 30 mm M3 grid). |
| 18 | Headers | 2.54 mm single-row female header strip (cut two 1x7) | ~$5 | Vetco | So the XIAO plugs in. |
| 19 | Connectors | [JST-XH kit with pre-crimped leads (B096Q81JBB)](https://www.amazon.com/dp/B096Q81JBB); [JST-SM 3-pin pairs, 20 pack (B01DC0KIT2)](https://www.amazon.com/dp/B01DC0KIT2) | ~$16 + $9 | Vetco: JST pre-wired pairs $2.89-2.99 | J1 socket (6-pin), J2 strip (3-pin), J3 pump (2-pin). |
| 20 | Wire | [22 AWG silicone hook-up wire kit (B07G2JWYDW)](https://www.amazon.com/dp/B07G2JWYDW) | ~$15 | Vetco: by the foot | Plus heat-shrink. |

### 2.2 Fluid path

| # | Item | Buy | Price | Local option | Notes |
|---|---|---|---|---|---|
| 21 | Pump | [Kamoer KPHM200-SW3B16, 12 V, 200 mL/min (B09HGVLHFV)](https://www.amazon.com/dp/B09HGVLHFV) | $28 | | 30 mL in ~9 s. 12 V, 0.7 A. Simpler/slower alternative: [Adafruit 3910 5 V pump](https://www.adafruit.com/product/3910) $24.95 (30 mL in ~18 s, no 12 V parts needed: skip items 9 and 10 and feed 5 V straight from a USB-A port). |
| 22 | Tubing | [AUBER 1/8" ID x 1/4" OD platinum-cured silicone, 10 ft (B0DKB1NKB4)](https://www.amazon.com/dp/B0DKB1NKB4) | $13.99 | Homebrew shops rarely stock 1/8" ID; buy online | Exactly 3.2 x 6.4 mm, the size the KPHM200 head is built for. FDA 21 CFR 177.2600, USP VI, NSF 51. One continuous piece from jar to nozzle. Do NOT use thinner-walled 1/8" x 3/16" tube in the pump head. |
| 23 | Reservoir | 8 oz clear PET straight-sided jar with 70-400 lid, e.g. [Uline S-25185W](https://www.uline.com/Product/Detail/S-25185W/Jars/Clear-PET-Straight-Sided-Plastic-Jars-8-oz-White-Cap) or [Amazon search](https://www.amazon.com/s?k=8+oz+clear+PET+plastic+jars+70-400+lids) | ~$8 | Container Store Bellevue, Daiso, Uwajimaya, Micro Homebrew (Kenmore) | About 73 mm wide x 76 mm tall. The bay takes up to 76 mm across the cap. 250 mL = eight 30 mL pours. |
| 24 | Pinch clamp | [Plastic tubing pinch clamps 1/4-1/2", 10-pack (B0FCM98N2Q)](https://www.amazon.com/dp/B0FCM98N2Q) | ~$6 | | Clamp the tube when carrying a full lantern or swapping jars. |
| 25 | Nozzle tip (optional) | [Stainless 1/8" hose barb union, 2-pack (B0CFQJXTN6)](https://www.amazon.com/dp/B0CFQJXTN6) | ~$9 | | A rigid 30 mm tip in the nozzle clip makes the 45 degree aim repeatable. |
| 26 | Shot glass | [Libbey 92440 Infinium Torque 1.5 oz Tritan (search)](https://www.amazon.com/s?k=Libbey+92440+Infinium+Torque) or [Libbey 1.5 oz glass shot set, 6-piece (B001K42BSO)](https://www.amazon.com/dp/B001K42BSO) | ~$10 | Bargreen Ellingson SoDo showroom (Mon-Fri 10-3) | Torque: 54 mm tall, 48 mm top, shatterproof. Libbey 5120 glass: 60 x 51 mm. Both fit the tray. |
| 27 | Small funnel, 6 mm and 2.5 mm drill bits | any | ~$5 | Home Depot | For refilling and for the jar lid. |

### 2.3 Printing and hardware

| # | Item | Buy | Price | Local option | Notes |
|---|---|---|---|---|---|
| 28 | Green PETG | [Creality PETG green 1 kg (B0DFCBSBZV)](https://www.amazon.com/dp/B0DFCBSBZV) x2 | ~$40 | | The printed set is roughly 1.1-1.3 kg of PETG; buy two spools. |
| 29 | White/translucent PETG | [SUNLU PETG white 1 kg (B085TH48N6)](https://www.amazon.com/dp/B085TH48N6) or [AMOLEN 4 x 250 g bundle (B08Z77GCM4)](https://www.amazon.com/dp/B08Z77GCM4) | $16-25 | | Diffuser, halo, LED carrier, glass tray. |
| 30 | Heat-set inserts | [ruthex M3 x 5.7 mm, 100-pack (B08BCRZZS3)](https://www.amazon.com/dp/B08BCRZZS3) | ~$10 | No Seattle retail source; online only | About 30 used. |
| 31 | M3 screws and nuts | [M3 304 stainless socket-head kit (B0HKFCTLK8)](https://www.amazon.com/dp/B0HKFCTLK8) | ~$18 | Tacoma Screw Ballard or Georgetown (by the piece); Ace/McLendon Hillman packs | Need 6, 8, 10, 12, 16 mm lengths plus a few nuts. |
| 32 | Return spring | [Mardatt 240-pc compression spring kit (B09C1DDHRV)](https://www.amazon.com/dp/B09C1DDHRV) | ~$12 | Vetco: Hillman compression spring $1.29 (bring calipers); Ace/McLendon spring drawers; McMaster for exact spec | Design spring: 0.5 mm wire, 5 mm OD, 10 mm free length, in the radial plunger pocket (0.4 mm wire for a softer twist). |
| 33 | Magnets | [SMARTAKE 6 x 2 mm neodymium, 45-pack (B0CBRVF4PN)](https://www.amazon.com/dp/B0CBRVF4PN) | ~$7 | [K&J D41](https://www.kjmagnetics.com/proddetail.asp?prod=D41) $0.28 each | 1 in the ring, 4 in the hatch, 8 in the base door. |
| 34 | Epoxy | [J-B Weld ClearWeld 5-minute, 2 syringes (B09C6R4VSQ)](https://www.amazon.com/dp/B09C6R4VSQ) | ~$9 | Home Depot / McLendon | PETG-to-PETG permanent joints. |
| 35 | CA glue + activator | [Starbond medium CA + accelerator (B09Z36D448)](https://www.amazon.com/dp/B09Z36D448) | ~$25 | Home Depot: Loctite Plastics Bonding System | Magnets, ring key cap, tacking. Any medium CA works. |
| 36 | Straps and ties | 20 mm hook-and-loop strap (Velcro One-Wrap), 4 mm zip ties | ~$8 | Home Depot | Pump, jar, power bank retention. |

**Totals (estimates).** Electronics ~$215, fluid path ~$80, printing and hardware ~$150: about **$445** buying
everything new on Amazon, or about **$350** if you buy the single-use items (resistors, caps, fuses, switch,
headers, springs, screws) at Vetco and Tacoma Screw instead of in kits. The printed set is about 0.9 kg of
PETG plus supports, so two spools of green and a part spool of white cover it. The ChatGPT transcript's "$100"
covered only the core electronics and pump; those alone are ~$170 here (items 1-11, 21-23).

### 2.4 Tools

Soldering iron (a flat or dedicated insert tip for the heat-set inserts), multimeter, calipers, drill with
2.5 mm and 6 mm bits, hobby knife, 220-grit sandpaper, isopropyl alcohol, small flush cutters, needle-nose
pliers, a USB power meter (optional but useful for the current checks in section 10).

### 2.5 Seattle-area stores (verified open on 2026-10-11; call before driving for specific stock)

| Store | Address, hours | Buy here |
|---|---|---|
| [Vetco Electronics](https://vetco.net) | 12718 Northup Way STE 100, Bellevue 98005, (425) 641-7275. Mon-Fri 9-6, Sat 10-3:30 | Single resistors, capacitors, diodes, fuses and holders, switches, JST pairs, perfboard, headers, wire, heat-shrink, 74AHCT125, A3144, WS2812 strip, Hillman springs. Not stocked: XIAO, magnets, heat-set inserts. |
| [Tacoma Screw Products, Ballard](https://www.tacomascrew.com/LocationFinder) | 3930 Leary Way NW, Seattle 98107, (206) 632-7565. Mon-Fri 7-5, Sat 9-1 | M3 screws, nuts, washers by the piece; springs. Georgetown branch: 1121 S Bailey St, Mon-Fri 7-5. |
| [McLendon Hardware](https://www.mclendons.com/locations) | White Center: 10210 16th Ave SW, Seattle 98146. Renton: 440 Rainier Ave S | Spring assortment drawers, metric screws, epoxy, CA, straps. |
| Stoneway Hardware, Ace stores (Magnolia, Maple Leaf, Junction) | Seattle neighbourhoods | Fasteners by the piece, Hillman spring drawers, adhesives. |
| [Micro Homebrew](https://www.microhomebrew.com/) | Kenmore, (425) 892-8425 | Food-grade tubing by the foot (3/16" and 1/4" ID; not the 1/8" pump size), small bottles. Sound Homebrew Supply and Mountain Homebrew could not be confirmed open. |
| [Bargreen Ellingson](https://www.bargreen.com/locations/seattle) | SoDo showroom, Mon-Fri 10-3 | Commercial 1.5 oz shot glasses, squeeze bottles. |
| [KCLS Bellevue Library Makerspace](https://kcls.org/bellevuemakerspace/) | Bellevue Library, free, 2 h/week reservation | Prusa Core One (250 x 220 x 270 mm) and MK4 printers with PETG, if your bed is smaller than 220 mm. |

Hardwick's in the U-District closed in 2020 (moved to Idaho). Metrix Create:Space and SoDo MakerSpace are gone.

---

## 3. Print the parts

All files are in `cad/output/` (STL for slicing, STEP for editing). Everything fits your 230 x 230 x 240 mm
Ender 3; the widest part is the rear sphere half at 221 mm (its handle bosses), the tallest is the base at
115 mm. Centre the big parts and use a skirt, not a brim. (On a 220 mm bed the rear half needs the bosses
trimmed to separate brackets; on a 180 mm bed scale the lantern to 1.6x in `cad/params.py`.)

**PETG settings (Creality PETG, 0.4 mm nozzle):** 0.2 mm layers, nozzle 235-245 C, bed 75-85 C, 4 perimeters,
5 top/bottom layers, 25-30 % gyroid infill, outer walls 40-60 mm/s, fan off for the first 3 layers then
30-50 %, textured PEI or glue stick on smooth PEI. Do not anneal.

Print these three test pieces first, before any big part:

1. `rotor`, `socket_housing`, `socket_base` and `plunger`: check that the rotor turns 45 degrees in its bore
   with slight drag and the plunger clicks it back. If it binds, raise `FIT` in `params.py` by 0.05 and
   reprint the rotor only.
2. `key_cap`: check that it drops into the rotor pocket in exactly one orientation with a little play.
3. `sphere_hatch` with 4 magnets: check the latch holds.

### Part list

| Part | File | Size (mm) | Print orientation | Supports | Colour | ~PETG g |
|---|---|---|---|---|---|---|
| base | `cad/output/base.stl` | 180 x 180 x 115 | floor down, open top up | no | green | 175 |
| base_deck | `cad/output/base_deck.stl` | 169 x 167 x 47 | flat | no | green | 72 |
| base_door | `cad/output/base_door.stl` | 118 x 25 x 94 | standing on its lip edge | no | green | 37 |
| dish_lower | `cad/output/dish_lower.stl` | 180 x 180 x 91 | mouth down | no | green | 154 |
| dish_upper | `cad/output/dish_upper.stl` | 180 x 180 x 86 | floor down, mouth up | no | green | 152 |
| sphere_front | `cad/output/sphere_front.stl` | 180 x 138 x 80 | split face down, dome up | yes: interior around the window (tree supports) | green | 50 |
| sphere_rear | `cad/output/sphere_rear.stl` | 221 x 117 x 79 | split face down, dome up | yes: interior around the hatch | green | 51 |
| sphere_hatch | `cad/output/sphere_hatch.stl` | 120 x 101 x 45 | convex side up | no | green | 46 |
| diffuser | `cad/output/diffuser.stl` | 118 x 118 x 1 | flat, 100% infill | no | white | 8 |
| led_carrier | `cad/output/led_carrier.stl` | 110 x 106 x 26 | flat, channels up | no | white | 14 |
| bay_floor | `cad/output/bay_floor.stl` | 131 x 131 x 10 | flat | no | white or green | 45 |
| glass_tray | `cad/output/glass_tray.stl` | 60 x 82 x 10 | flat | no | white | 9 |
| nozzle_clip | `cad/output/nozzle_clip.stl` | 30 x 12 x 10 | flat | no | green | 2 |
| handle_leg_left | `cad/output/handle_leg_left.stl` | 14 x 126 x 10 | flat | no | green | 12 |
| handle_leg_right | `cad/output/handle_leg_right.stl` | 14 x 126 x 10 | flat | no | green | 12 |
| handle_arc_left | `cad/output/handle_arc_left.stl` | 120 x 132 x 10 | flat | no | green | 18 |
| handle_arc_right | `cad/output/handle_arc_right.stl` | 120 x 132 x 10 | flat | no | green | 17 |
| socket_housing | `cad/output/socket_housing.stl` | 100 x 100 x 10 | faceplate down | no | green | 26 |
| rotor | `cad/output/rotor.stl` | 44 x 37 x 8 | top face down | no | green | 5 |
| socket_base | `cad/output/socket_base.stl` | 76 x 76 x 4 | top face down | no | green | 11 |
| switch_bracket | `cad/output/switch_bracket.stl` | 16 x 10 x 6 | flat | no | any | 0 |
| plunger | `cad/output/plunger.stl` | 5 x 5 x 4 | nose up | no | any | 0 |
| halo | `cad/output/halo.stl` | 68 x 68 x 4 | skin down | no | white/translucent | 2 |
| key_cap | `cad/output/key_cap.stl` | 28 x 24 x 3 | flat face down | no | green | 1 |
| **Total** | | | | | | **~919 g** (at 30 % infill; plus supports) |

![all printed parts](images/cad-parts-sheet.png)

![assembly](images/cad-assembly-iso.png) ![cutaway](images/cad-cutaway.png)


Supports: none, except inside the two sphere halves (print them split-face down; the last 15 mm of dome
around the window and hatch overhang more than 45 degrees, so enable tree supports on the inside only).
The dish cones are 27 degrees from vertical and print clean.

---

## 4. Bench electronics (do this first, on the desk)

![wiring diagram](images/wiring.svg)

Build the whole circuit on the 5 x 7 cm perfboard before anything goes in the lantern. Reference designators
match the diagram.

1. **Headers.** Solder two 1x7 female header strips 15.24 mm apart so the XIAO plugs in with its USB-C port
   toward a board edge. Solder a 14-pin DIP socket for the SN74AHCT125N (U1).
2. **Power rails.** Make a +12 V rail, a +5 V rail and a ground rail along the board edges.
   - The PD trigger cable's barrel plug gets cut off; strip it and check polarity with the meter while it is
     plugged into the bank (the centre conductor should read +12 V). Cable + goes to the master switch, then
     to the F1 holder (2 A), then to the +12 V rail. Cable - goes to ground.
   - C2 2200 uF 16 V across +12 V and ground, right at the D4184 module's DC+/DC- screw terminals.
   - Buck module: VIN to +12 V, GND to ground, VOUT to the F2 holder (3 A), then to the +5 V rail. If you use an
     LM2596 module, set it to 5.0 V with the meter BEFORE wiring anything to its output.
   - C1 1000 uF 10 V across +5 V and ground near where the LED leads leave the board.
   - XIAO 5V pin: from the +5 V rail through D1 (1N5819, stripe toward the XIAO). This diode lets you plug the
     XIAO into a laptop for programming without back-feeding the lantern. Still: flash with the master switch OFF.
   - XIAO GND to ground. The XIAO 3V3 pin feeds only the Hall sensor.
3. **U1 (SN74AHCT125N).** Pin 14 to +5 V, pin 7 to ground, 100 nF between them. Pins 1, 4, 10, 13 (the four OE
   pins) and pins 12 (4A) to ground. Inputs: pin 2 from XIAO D4, pin 5 from D5, pin 9 from D3. Outputs: pin 3
   through 330 ohm to J1 RING DIN, pin 6 through 330 ohm to J2 STRIP DIN, pin 8 directly to the D4184 PWM/TRIG
   terminal. Add a 10 k from D3 to ground so the pump cannot twitch while the XIAO boots.
4. **D4184 module.** DC+ to +12 V, DC- to ground, GND (signal) to ground, PWM/TRIG from U1 pin 8. OUT+ and
   OUT- go to J3 (pump). Solder D2 (1N5819) across OUT+ and OUT- with the stripe on OUT+: that is the flyback
   diode the module lacks.
5. **Inputs.** D1 (Hall), D2 (switch) and D6 (PRIME) are inputs with internal pull-ups. The Hall sensor's OUT
   goes to D1 with a 100 nF to ground at the board; the microswitch NO to D2 and COM to ground; the PRIME button
   between D6 and ground.
   - If you use the 5 V A3144 module instead of the DRV5032: power it from +5 V and connect its OUT to D1
     through a 1N5819 with the stripe toward the module (anode on D1). The magnet then pulls D1 to about 0.4 V
     and D1 never sees 5 V. Do not use a resistor divider; the module's own pull-up makes that unsafe.
6. **Connectors.** J1 (socket, 6-pin): 5V, GND, 3V3, HALL, SW, RING DIN. J2 (strip, 3-pin): 5V, GND, DIN.
   J3 (pump, 2-pin). Use the pre-crimped JST-XH leads; the strip's own 3-pin JST-SM pigtail plugs into J2.
7. **Flash the firmware** (section 5) with nothing but the XIAO plugged into USB, then connect the ring, the
   strip, the Hall sensor and the switch on the bench and check with the serial console that `status` shows the
   ring and switch changing as you hold a magnet near the sensor and press the lever.
8. **Current check.** With a USB meter on the bank: idle should read about 0.2 A at 12 V... the meter reads at
   the bank's 12 V output, so expect roughly 0.1 A idle, 0.5 A during ARMED, and about 1.2-1.4 A during a pour
   (pump 0.7 A plus LEDs through the buck). The INIU B61's 12 V profile is rated 1.5 A.

**Ground.** Every ground in the lantern is one net: cable -, buck GND, D4184 DC- and GND, XIAO GND, U1 pin 7
and the OE pins, Hall GND, switch COM, PRIME button, ring and strip GND, the 10 k pull-down, C1 and C2 -.

---

## 5. Firmware

Source: `firmware/green_lantern/green_lantern.ino`. Board: Seeed XIAO RP2040 on the "Raspberry Pi Pico/RP2040"
Arduino core by Earle Philhower. Library: Adafruit NeoPixel.

```bash
cd firmware
arduino-cli core install rp2040:rp2040 --additional-urls https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
arduino-cli lib install "Adafruit NeoPixel"
arduino-cli compile --fqbn rp2040:rp2040:seeed_xiao_rp2040 green_lantern
arduino-cli upload  --fqbn rp2040:rp2040:seeed_xiao_rp2040 -p /dev/ttyACM0 green_lantern   # or use the Arduino IDE
```

In the Arduino IDE: Boards Manager, install "Raspberry Pi Pico/RP2040" (Earle Philhower), select
"Seeed XIAO RP2040", install "Adafruit NeoPixel", open the sketch, upload. If the board does not show a port,
hold the BOOT button while plugging it in and upload again.

![state machine](images/state-machine.svg)

| Pin | Function |
|---|---|
| D1 | Hall sensor OUT (active LOW = ring present), INPUT_PULLUP |
| D2 | Microswitch NO (COM to GND), INPUT_PULLUP |
| D3 | Pump trigger, through U1 channel 3 to the D4184 (PWM soft start) |
| D4 | NeoPixel ring data (24 px) through U1 channel 1 |
| D5 | WS2812B strip data (60 px) through U1 channel 2 |
| D6 | PRIME button to GND, INPUT_PULLUP |

Serial console (115200 baud) commands, type and press Enter:

| Command | What it does |
|---|---|
| `status` | Prints state, ring, switch, pump, pour time, brightness cap. |
| `cal 10000` | Runs the pump for 10000 ms without the ring (calibration; only works when idle). |
| `pour 9000` | Sets the pour time in ms for this session (500 to 20000). |
| `leds 160` | Sets the maximum brightness 0-255. |
| `save` | Stores pour time and brightness in flash so they survive power cycles. |
| `stop` | Stops the pump now. |

Constants worth knowing (top of the sketch): `STRIP_COUNT` (set to your real pixel count), `POUR_MAX_BRIGHT`
(110: caps the LEDs while the pump runs so the 12 V budget holds), `MAX_PUMP_MS` (20 s hard cap), `POUR_ABORT_MS`
(60 ms: how fast a pulled ring stops the pump), `IDLE_PILOT` (the faint ring glow that keeps the power bank
from switching itself off).

Interlocks, all verified by the simulation in `firmware/test/` (`make test`, 16 scenarios): pump off at boot;
switch alone never pumps; ring alone never pumps; one pour per insertion; a ring removed mid-pour stops the pump
within one loop pass after 60 ms; a switch already pressed at boot or at insertion is ignored until released;
the hard cap applies to every pump run including PRIME and `cal`.

---

## 6. The charging socket

![socket mechanism](images/socket-mechanism.svg)

Parts: `socket_housing` (faceplate + housing puck), `rotor`, `socket_base` (closes the housing from below and
holds the Hall board), `switch_bracket`, `plunger`, `halo`, `key_cap`, plus 4 x M3x8 (faceplate), 3 x M3x8 and
3 nuts (base plate), 1 x M3x6 and nut (switch bracket), the 0.5 x 5 x 10 mm spring, the D2F-L, the Hall board,
the 24-px ring and one 6 x 2 mm magnet. The rotor is a flat 36 mm disc; under the faceplate lip its edge
carries three features that do all the work: a stop lug running in a channel whose walls are the 0 and 45
degree hard stops, a cam lobe that presses the D2F-L lever 3 mm between 33 and 45 degrees, and a ramp that
pushes a spring-loaded plunger out 4 mm so the rotor snaps back to 0 when you let go.

1. **Inserts and nuts.** With the iron at about 245 C, set heat-set inserts in the 4 faceplate bosses under the
   upper dish floor. Drop M3 nuts into the three hex pockets on the underside of `socket_housing` and the one
   under `socket_base` (a dab of CA holds them).
2. **Ring key.** Glue the 6 x 2 mm magnet into the pocket on the underside of `key_cap` with CA (pole does not
   matter for the DRV5032; for an A3144 test which pole trips the sensor first and glue that pole facing down).
   Glue the key cap to the flat face of your ring with CA (scuff both faces first), tab pointing along the
   finger. The kit's `fingerring_20mm.stl` already has the key merged in (`key_ring.stl`) if you want to print
   the ring too.
3. **Hall sensor.** Press the DRV5032 board into the pocket on the underside of `socket_base`, components
   DOWN (the JST connector hangs below the plate), so the chip sits under the square sensor window on the
   axis; a drop of CA on two corners holds it. The chip ends up about 8 mm below the key-cap magnet, which a
   DRV5032 sees easily (it trips below 5 mT; the magnet gives about 15 mT there). A3144 module instead: bend
   its sensor leads so the sensor stands up through the window to within 3 mm of the rotor, and glue a
   second magnet on top of the first in the key cap.
4. **NeoPixel ring.** Drop the 24-px ring into the recess on top of the faceplate, LEDs up, wires through the
   notch. Snap the `halo` over it.
5. **Rotor and plunger.** Turn `socket_housing` upside down. Drop the spring into the radial pocket (the
   straight channel at the lower right), the `plunger` nose-first on top of it, and hold it in with a finger
   while you lower the `rotor` into the bore, lugs down into their channels, with the key-pocket tab pointing
   at the faceplate's +X screw hole. Twist to 45 degrees and let go: it must snap back to 0 every time. Too
   weak: the 0.5 mm spring is the design; too stiff to twist with a finger: use the 0.4 mm one.
6. **Switch.** Press the D2F-L onto the two pegs of `switch_bracket` (lever toward the rotor) and screw the
   bracket into its recess in `socket_base` with the M3 through the slot, loosely.
7. **Close and tune.** Screw `socket_base` onto the housing with the three M3x8 into the captured nuts. Twist
   the rotor slowly: the lever should start to move at about 33 degrees and click at about 40, before the stop
   at 45. Slide the bracket in its slot to tune, then tighten. Never let the switch be the stop.
8. **Cycle it.** 50 twists. Check with the serial console that `status` shows `switch=pressed` only near the end
   of the twist and `ring=present` through the whole twist with the ring inserted.
9. **Mount.** Four M3x8 through the faceplate into the upper dish floor. Route the 6-wire J1 cable through the
   wire slot in the dish floor.

---

## 7. The fluid path

1. **Jar lid.** Drill a 6 mm hole near the lid's edge for the tube and a 2.5 mm vent hole on the opposite
   side. Push the silicone tube through the 6 mm hole (it self-seals) so it reaches 5 mm above the jar
   bottom. Optional: a 6 mm grommet makes the pass-through neater.
2. **Pump head.** Open the KPHM200's quick-release head cap, lay the tube around the rollers with the tube
   coming in from the jar on one port and going out to the nozzle on the other, close the cap. Use ONE
   continuous piece of the 1/8" x 1/4" tube from jar to nozzle: no joints, nothing to leak.
3. **Route.** Pump in its saddles on the deck with the head face toward the rear door (so you can open the cap
   later without removing the pump), strap it down. Tube up through the lower dish neck, through the grommet
   hole in `bay_floor`, up the rear-left wall of the sphere into `nozzle_clip`.
4. **Nozzle.** The clip holds the last 30 mm of tube (or the stainless barb) at 45 degrees, aimed at the inside
   wall of the glass, tip 10 mm above the rim. Aiming at the wall hides splash and lands the last drop.
5. **Prime.** Jar full of water, master switch on, hold PRIME until water reaches the nozzle (4-6 s), release.
   The tube stays full between pours.
6. **Carry.** Put the pinch clamp on the tube between jar and pump whenever you carry the lantern with a full
   jar, and take it off before the party.

---

## 8. The sphere

1. **LED carrier.** Cut the WS2812B strip into 9 pieces of 6 LEDs (cut on the copper pads). Stick them into
   the 9 channels of `led_carrier`, all arrows pointing the same way, and solder the ends serpentine-style
   (end of row 1 to start of row 2, and so on: 5V to 5V, GND to GND, DO to DI). Feed 5 V and ground into the
   first row AND the last row. The first row's DI gets the J2 pigtail. Set `STRIP_COUNT` to 54.
2. **Diffuser.** Print `diffuser` in white PETG at 0.8 mm (0.6 and 1.0 mm coupons are worth a test). It sits
   on the ledge behind the front window; the carrier stands 25 mm behind it, held by the tabs in `bay_floor`.
3. **Bay floor and tray.** `bay_floor` sits on the lower dish floor inside the sphere. `glass_tray` slides on
   its two rails and stops at the end of travel; the glass sits in the tray's ring. Pull the tab to present
   the glass through the hatch.
4. **Hatch.** Glue 4 magnets into the hatch door's lip and 4 into the sphere's rebate so that each pair attracts
   and the faces touch when closed (mark polarity with a pen before gluing). The door's two pins snap into the
   holes at the bottom of the opening and it swings down about 100 degrees.
5. **Nozzle clip.** One M3x8 into the insert in the rear half, above and behind the glass.
6. **Handle bosses.** The legs plug down into the two sockets on the rear half's equator and are pinned with
   one M3 each.
7. **Join the halves.** Two alignment pins, then 4 x M3x10 through the rear half's flange into the front half's
   inserts. Feed the J1 socket cable up the inside of the rear half before closing.

---

## 9. Final assembly

Order, bottom to top: `base` with `base_deck` dropped in (3 M3 into the pillars) and the power bank strapped
flat on the floor under the deck; jar in its ring and pump in its saddles on the deck; the electronics board on
the deck's vertical panel (4 x M3x6), the D4184 and the buck in the floor crescents; `dish_lower` spigot into
the base top, 3 radial M3x12 from outside into the spigot inserts; the assembled sphere onto the lower dish's
locating ring, 3 radial M3x12; `dish_upper` with the socket module onto the sphere's top, 3 radial M3x12;
handle legs into the bosses, the two arcs lap-jointed at the top with 2 x M3x16 and nuts; `base_door` with the
switch and PRIME button fitted, magnets glued in, snapped on.

Cables: J1 (socket) down the rear of the sphere, through the lower dish neck to the board. J2 (strip) short,
inside the sphere. J3 (pump) stays in the base. Keep the pump leads twisted and away from the data lines.

---

## 10. Calibration

With water in the jar, a measuring cup under the nozzle and the laptop on the serial console:

```
cal 10000        -> measure the volume, repeat five times, average
flow_mL_per_s  = volume_mL / 10
POUR_MS        = target_mL / flow_mL_per_s * 1000      e.g. 30 mL at 3.3 mL/s -> 9000
pour 9000
save
```

Then repeat with the real liqueur: Jagermeister is thicker than water and the nozzle is 20 cm above the pump,
so expect a little less than the rated 200 mL/min. A 1.5 oz glass holds 44 mL; 30 mL leaves room to carry it.

---

## 11. Test before the party

- [ ] Power on: pump silent, ring glows faintly, nothing else.
- [ ] Twist the empty socket: nothing.
- [ ] Insert the ring: slow green pulse, no pump.
- [ ] Twist: flash, pump runs the calibrated time, light show, then afterglow. Let go: the rotor returns.
- [ ] Twist again with the ring still in: nothing.
- [ ] Remove the ring, reinsert, twist: one new pour.
- [ ] Pull the ring out mid-pour: pump stops at once.
- [ ] 20 water pours in a row; no drips anywhere, every pour lands in the glass.
- [ ] Carry the lantern around and tilt it with water in it, then leave it 30 minutes: dry inside.
- [ ] PRIME works only when idle and only while held.
- [ ] Power bank does not switch off after 20 minutes idle (if it does, raise `IDLE_PILOT`).
- [ ] Hatch door holds shut when the lantern is swung.

---

## 12. Performing it

Set the lantern on a table or hang it on your forearm for the ritual: one hand holds the ring, the other
opens the hatch afterwards. Glass on the tray, tray in, hatch shut, PRIME held for a second if the lantern sat
for a while. Insert the ring, speak, twist on the last line and hold the twist for the flash, then let go: the
pump keeps running for the calibrated time while you finish the pose. Remove the ring (that re-arms the prop),
open the hatch, pull the tray, hand over the glass. Refill the jar through the rear door with the funnel.

---

## 13. Cleaning and storage

Same night: swap the jar for one with warm water, hold PRIME for 30 s into a cup, twice, then run 10 s with
the tube out of the water to push the line empty. Open the pump head cap and lift the tube off the rollers.
Air-dry with both ends open. Wipe the tray and bay floor with a damp cloth. Never leave liqueur in the tube
overnight: the sugar gums the bore and the rollers. Store with the head cap open so the silicone is not
crushed for months; replace the pump tube when it looks cloudy or flat.

---

## 14. Troubleshooting

| Symptom | Check |
|---|---|
| Ring not detected | `status` while holding the ring in. DRV5032: is the chip on the rotor axis and within 2-3 mm of the magnet? A3144: wrong magnet pole, or the module is on 3.3 V (it needs 5 V). |
| Detected but no flash on twist | `status` while twisting: switch must read pressed before the hard stop. Slide the switch bracket toward the cam. |
| Pump hums but no flow | Tube not seated under the rollers, head cap open, or the thin 1/8" x 3/16" tube got used. |
| Pump runs then the XIAO reboots | 12 V sag: check the PD cable really negotiates 12 V (meter), C2 present, bank charged. |
| LEDs flicker or wrong colours | Data wire too long or no 330 ohm; AHCT125 OE pins not grounded; strip order is GRB in the sketch. |
| Power bank turns off while idle | Raise `IDLE_PILOT` in the sketch, or enable the bank's low-current mode if it has one. |
| Rotor sticks | Sand the bore lightly or reprint with `FIT` + 0.05. PETG strings: clean the bore. |
| Drips after the pour | Lower the nozzle angle a little, shorten the free tube end, or fit the stainless tip. |

---

## 15. Appendix: design decisions and the questions from the ChatGPT thread

- **Why a squat jar, not a Boston round:** a 133 mm bottle cannot leave a 115 mm base through the door and its
  cap would be buried in the dish cone. The 76 mm jar refills in place with a funnel.
- **Why the glass is in the sphere on a tray:** a 110 x 105 mm hatch plus a slide-out tray presents the glass
  without reaching into a dark 180 mm sphere with one hand.
- **LED brightness and power:** 84 pixels can draw 5 A at full white; at full green they draw about 1.7 A.
  The sketch caps everything at 160/255 and at 110/255 while the pump runs, which keeps the whole lantern
  inside the bank's 12 V/1.5 A profile. If you want more, add a second strip row set and a bank with a 20 V
  profile and a bigger buck; the limit is current, not LED count.
- **Power bank requirements:** USB-C PD with a 12 V profile (the INIU B61 has one; the Anker 313 does not),
  and either a low-current mode or the firmware's idle pilot glow so it does not shut off between pours.
- **Spring size:** compression, 0.5 mm wire, 5 mm OD, 10 mm free, 1.2 mm preload, 5.2 mm compressed at 45
  degrees, acting radially on a 4 mm ramp in the rotor's edge (0.4 mm wire for a softer twist). A tangential
  spring long enough for 45 degrees of arc does not fit in a 76 mm housing, and magnets cannot return the
  rotor from 45 degrees; they only work as a detent at 0.
- **Why 12 V from the bank rather than a 5 V-to-12 V cable:** the pump's 0.7 A at 12 V would pull 2.4 A from a
  5 V port before the LEDs, right at a USB-A port's limit; a native 12 V profile has margin.
- **What the simulation does not cover:** the real Hall sensor's response, the real spring feel and the real
  pump flow. Those are the first three things to measure.
- Research behind every number: `docs/research/*.md` (each file has a fact-check section at the end).
