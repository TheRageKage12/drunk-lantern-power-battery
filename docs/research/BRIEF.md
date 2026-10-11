# Project brief: Green Lantern power battery that pours a shot

Owner: Kevin (software engineer, has a 3D printer, Seattle area). Halloween costume prop.
Repo: /home/user/temprepo (branch claude/green-lantern-battery-prop-7bn4rp).

## What the prop must do (final agreed interaction, from the ChatGPT transcript)
1. An empty shot glass is placed INSIDE the lantern, hidden from the audience.
2. Kevin inserts his Green Lantern ring into a "charging socket" on the lantern.
   A magnet hidden in the ring is detected by a Hall sensor -> lantern starts a slow green pulse (ARMED).
3. He recites the oath while the glow builds.
4. On the last line he twists the ring ~45 degrees in the socket. A cam on the rotating socket presses a
   microswitch. Firmware requires Hall=present AND switch=pressed AND not-already-poured.
5. Bright green flash, ~200 ms later the peristaltic pump runs a calibrated time; LED light show continues
   during the ~10 s pour. Rotor spring-returns to 0 deg when released.
6. System LOCKS until the ring is removed (one pour per insertion). Removing the ring mid-pour stops the pump.
7. He reaches into the lantern and pulls out the filled glass.

Safety interlocks required in firmware: pump OFF at boot; switch alone never pumps; Hall alone never pumps;
one pour per insertion; ring removal aborts/locks; absolute max pump runtime; master power switch.

## Hardware Kevin has ALREADY BOUGHT (Amazon ASINs, verified by fetching the listings)
| ASIN | What it is | Notes |
|---|---|---|
| B09HGVLHFV | **Kamoer KPHM200 peristaltic pump, 12 V DC, 200 mL/min, tube 3.2 mm ID x 6.4 mm OD** | Replaces the 5 V Adafruit 3910 that ChatGPT specced. Needs a 12 V rail. ~0.7 A at 12 V per a retailer listing (verify). |
| B08RYFGNMK | JoyTube food-grade silicone tubing **1/8" ID x 3/16" OD**, 3 ft | 3.18 x 4.76 mm, wall 0.8 mm. **Too thin-walled for the KPHM200 head (needs 6.4 mm OD / 1.6 mm wall).** Usable only as inlet/outlet tubing with a barb, not inside the pump head. Correct size is 1/8" ID x 1/4" OD (3.2 x 6.35 mm). |
| B0DRNTQ338 | Seeed Studio XIAO RP2040 (pre-soldered headers) | 21 x 17.8 mm, 3.3 V logic, GPIO not 5 V tolerant. |
| B01NBE2XIR | HiLetgo A3144 (3144E) Hall effect sensor module, 5 pcs | 5 V module with pull-up + LED, digital open-collector output; unipolar (needs the correct magnet pole facing the sensor). Output would be 5 V -> needs divider or 3.3 V supply trick. Replaces the DRV5032 ChatGPT specced. |
| B0DBV8XGG4 | D2F-L style 3-pin lever microswitch, SPDT, 1.47 N, pack of 4 | Omron D2F-L equivalent: body 12.8 x 5.8 x 6.5 mm, 2 mounting holes dia ~2.35 on 6.5 mm centers, hinge lever. |
| B0FMJH3DML | Dual D4184 high-power MOSFET trigger switch module, 5-36 V, 15 A, 6 pcs | ~34 x 17 x 12 mm. Terminals: DC+ DC- (supply), OUT+ OUT- (load), PWM/TRIG + GND (signal, 3.3-20 V ok). Replaces Adafruit 5648. |
| B08R6BCSYC | SN74AHCT125N quad buffer, DIP-14, 10 pcs | 3.3 V -> 5 V level shifter for NeoPixel data. |
| B0CBRVF4PN | SMARTAKE 6 x 2 mm neodymium disc magnets, 45 pcs | For the ring key, hatch latches, magnetic detents. |
| B0DFCBSBZV | Creality PETG filament, green, 1.75 mm, 1 kg | |
| B01IUVHB8E | Gikfun 12 V dosing pump AE1207 (older purchase, likely superseded by the Kamoer) | 2 mm ID tube, ~100 mL/min claimed, slow. |
| B092V8PR3Y | Kamoer silicone tubing 2 mm ID x 4 mm OD, 3 m (older purchase for the Gikfun) | Does not fit KPHM200 head. |

NOT yet bought (Kevin's open questions): LEDs ("almost obnoxiously bright" - more LEDs or bigger ones? power impact?),
USB power bank (any requirements?), reservoir bottle, shot glass, compression/torsion springs (what size?), M3
screws/heat-set inserts, wire, switch, fuse, resistors, capacitor, and where in the Seattle area to buy small
quantities of misc hardware and magnets.

## The lantern model (Hedo3D "Green Lantern luminous", Cults3D #40633, CC BY-NC 4.0) - files in original-model/
Measured STL extents (mm, X Y Z as exported; most parts are modeled with Y as the vertical axis):
- base.stl 98.4 x 53.0 x 98.4 (stepped round drum, hollow, open side). base_snap.stl = same with a 44x33 side window for cover.stl (57x33x2 door) + cover_lock_1/2 twist latch.
- reflector.stl 97.2 x 97.1 x 43.0 (conical dish, 97 mouth, ~40 mm hole at the narrow end). reflector_reed.stl = same with a reed-switch channel.
- sphere.stl 65 x 101 x 101 (101 mm sphere truncated to 65 mm thick -> two flat faces ~77 mm dia; has a large arched window on one side for the green_diffusor.stl disc, 60 mm dia x 0.8 mm).
- handle.stl 134 x 148 x 6 flat arch with pegs at the ends. connection.stl / connection_2.stl small pads.
- fingerring_20mm.stl 27 x 27 x 28.7 (ring with a flat emblem face), fingerring_15mm.stl 20 x 20 x 23.7.
Assembly order (bottom to top): base -> reflector (mouth down) -> sphere -> reflector_reed (mouth up, ring rests in it) -> handle over the top.
Designer's print notes: 0.2 mm layers, 30% infill, supports only for the sphere.
At stock size (~100 mm diameter, ~240 mm tall) NOTHING fits inside. Renders: docs/images/original-parts-sheet-*.png

## Design direction already chosen (keep unless research shows a real problem)
- Rebuild the lantern parametrically in CadQuery (cad/lantern.py) at ~1.8x the original proportions
  (sphere/base ~180 mm dia, fits a 220 x 220 mm bed; parts split as needed), with real 2.4 mm walls instead of
  scaled-up walls. Original decorative proportions preserved. Everything printable without supports where possible.
- Base drum (bottom): houses the 250 mL reservoir bottle (vertical, protruding up into the hollow lower reflector),
  the KPHM200 pump, the USB power bank, electronics tray (XIAO, D4184 module, AHCT125, 12 V source), master switch,
  rear service door.
- Lower reflector: inverted dish between base and sphere; tube + wires pass through its neck.
- Sphere (split front/back halves): HIDDEN GLASS BAY in the center with a cradle + removable drip tray; rear
  hatch (magnet-latched, faces Kevin) to reach in and grab the glass; nozzle holder above the glass; front arched
  window with green diffuser and a WS2812B strip behind it for the big glow; wire channel up to the socket.
- Upper reflector: dish opening upward; the removable CHARGING SOCKET module mounts in its floor:
  fixed housing + rotating keyed rotor (OD ~44), 0/45 deg hard stops (pin in arc slot), spring return, cam lobe ->
  D2F-L microswitch (slotted mount), A3144 Hall sensor centered under the rotor floor (magnet centered in the ring
  key so rotation does not move it), 24-px NeoPixel ring (65.5 OD / 52.3 ID) around the rotor under a translucent
  ring, 4x M3 heat-set inserts.
- Ring key cap: a small printed disc with a key tab and a 6x2 magnet pocket that glues onto the ring's face
  (works with the kit's fingerring_20mm or a store-bought ring), matching the rotor pocket.
- Handle: printed arch in two halves with a lap joint, bosses on the sphere equator.
- Power: 12 V for the pump (from the USB power bank via a USB-C PD 12 V trigger cable or a 5->12 V boost), 5 V for
  XIAO + LEDs; common ground; master switch; fuse.
- Firmware: Arduino sketch for XIAO RP2040 (Adafruit NeoPixel lib), state machine IDLE->ARMED->FLASH->POURING->LOCKED.

## Deliverables
1. cad/ : parametric CadQuery source + exported STL (and STEP) for every new part.
2. firmware/ : the sketch.
3. docs/BUILD_GUIDE.md : BOM with purchase links (Amazon / Adafruit / big-box / Seattle-area stores), print settings,
   step-by-step assembly, wiring, calibration, testing, cleaning; diagrams and renders in docs/images/.
4. Everything committed and pushed.

Full ChatGPT transcript (long, 125 KB): docs/research/chatgpt-transcript.md
Tooling available: python3 with cadquery 2.8, trimesh, manifold3d, numpy, PIL, reportlab; cad/render_stl.py (software STL renderer -> PNG). No OpenSCAD/FreeCAD/Blender. No arduino-cli (check before assuming).
