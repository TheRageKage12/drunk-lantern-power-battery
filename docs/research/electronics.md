# Electronics: sensors, switching, microcontroller wiring

Scope: XIAO RP2040, HiLetgo A3144 Hall module, D2F-L microswitch, dual D4184 MOSFET module, SN74AHCT125N, 6x2 mm magnets, the full net list, and the connector/protoboard plan. Pins match `firmware/green_lantern/green_lantern.ino` (D1 Hall, D2 switch, D3 pump, D4 ring, D5 strip).

## Decisions / recommendations

- **XIAO pin map used:** D1 = GPIO27 (Hall), D2 = GPIO28 (switch), D3 = GPIO29 (pump PWM), D4 = GPIO6 (ring data), D5 = GPIO7 (strip data). All 11 digital pins (D0-D10) have internal pull-ups (RP2040 RPU 50-80 kOhm), so `INPUT_PULLUP` is fine on D1 and D2. GPIO is 3.3 V only; never put 5 V on a pin.
- **Power the XIAO through its 5V pin, with a 1N5819 in series** (anode on the 5 V bus, cathode on the XIAO 5V pin). The v1.3 schematic shows the header's "5V" pin is the raw USB **VBUS** net; it feeds the 3.3 V LDO through Schottky D2, so feeding 5 V into that pin does power the board. Without the series diode, an external 5 V would back-feed any plugged-in USB cable (Seeed staff: "Please don't do so" on dual power). Rule for the build guide: flash over USB only with the master switch OFF.
- **Hall module: run it at 5 V, never at 3.3 V** (A3144 datasheet: 4.5-24 V operation). Interface its OUT to the 3.3 V GPIO with a **diode, not a divider**: 1N5819 (or 1N4148) with anode on XIAO D1, cathode on module OUT; D1 = `INPUT_PULLUP`. Magnet present -> OUT sinks -> D1 reads roughly 0.3-0.6 V (A3144 Vout(sat) 175 mV typ / 400 mV max at 20 mA, plus the Schottky drop at the ~50 uA the RP2040 pull-up supplies; still < VIL 0.8 V). Magnet absent -> diode blocks the module's 5 V pull-up, D1 sits at 3.3 V. This works whatever the module's pull-up value is. The 4.7k/6.8k divider is **not** safe blind: if the module pull-up is 10 k the high level would be 5 x 6.8/(10+4.7+6.8) = 1.58 V, below the RP2040 VIH of 2.0 V.
- **Magnet orientation and gap:** unipolar switch, one pole must face the branded (printed) face of the TO-92-style sensor. The fetched Allegro datasheet does not name the pole (south is the usual convention for Allegro unipolar switches, but that is unverified here), so test it: the module's LED lights when it trips; flip the magnet if it does not, then mark the ring-cap magnet. Keep the total distance magnet-face to sensor-package-face at **3 mm or less** (2 mm is comfortable): a 6x2 N35 disc gives roughly 1450 G at 2 mm and 880 G at 3 mm against a worst-case A3144 operate point of 350 G (25 C) / 450 G (full temperature). With ~0.8 mm ring-cap floor + ~0.8 mm rotor floor, budget about 1.4 mm of air. **Stacking two magnets helps** (about +40 %: 1240 G at 3 mm, 800 G at 4 mm) and is the fix if the socket geometry forces a 4 mm gap. Do not put the sensor behind a wall thicker than 2.4 mm total.
- **Better Hall sensor (recommended, per the brief): Adafruit #6051 DRV5032 breakout** ($4.95, in stock; made by ScoutMakes, sold by Adafruit). The TI DRV5032 runs from 1.65-5.5 V, so it is powered from the XIAO 3V3 pin and its output goes straight to D1 with no diode, no divider and no 5 V on the socket cable. Every DRV5032 variant is far more sensitive than the A3144 (max operate threshold 4.8 mT = 48 G for the FA/FB/FC/FD versions, 9.5 mT for AJ, 63 mT for ZE, vs 350-450 G for the A3144), and the F-series parts except FD are **omnipolar**, which removes the pole-orientation problem. Two cautions: (1) the Adafruit page does not say which variant is fitted (unverified; read the marking on the SOT-23/TO-92 and check the table below), and an omnipolar 48 G part will also see the hatch-latch magnets if they are within a few cm of the socket, so keep other magnets away from the rotor floor; (2) the sampled output updates at 20 Hz (FA/FC/FD/DU) or 5 Hz (FB), i.e. up to 50 ms / 200 ms latency, which is fine for ring-present detection but means a 5 Hz FB part would make the ring-removal abort feel slow. If the fitted part is push-pull (FA/FB/FD/DU), do not enable the XIAO pull-up; if open-drain (FC/AJ/ZE), use `INPUT_PULLUP`. Keep the HiLetgo A3144 module as the fallback with the 5 V + diode interface above.
- **Microswitch:** wire **NO -> D2, COM -> GND**, leave NC open. Software debounce 20 ms (Omron spec: contact make/break 1 ms max). Real hinge-lever operating force is **0.78 N max** (the Amazon title's 1.47 N is the pin-plunger figure). Cam design: lever free position is 10 mm max above the mounting face and it operates at 6.8 +/- 1.5 mm, so the click can happen anywhere between 8.3 mm and 5.3 mm above the mounting face. Design the cam to press the lever down to about 5 mm above the mounting face (up to ~5 mm of travel from a 10 mm free position) and slot the mount to tune the click point; do not drive the lever flat against the body (OT is only 0.55 mm min past OP).
- **Pump driver:** dual D4184 module, TRIG = XIAO D3 via one spare SN74AHCT125 channel (gives a clean 5 V gate signal; Rds(on) is spec'd at 4.5 V, not 3.3 V), module GND tied to XIAO GND, DC+/DC- from the fused 12 V rail, OUT+/OUT- to the pump. **Add a 1N5819 across the pump** (cathode to OUT+/motor +, anode to OUT-/motor -); the module has no flyback diode. **Add a 10 k pull-down on D3** (and on the AHCT125 input) so the pump cannot twitch while the RP2040 pins float at boot. PWM at 1-2 kHz for the 150 ms soft-start ramp (module spec 0-20 kHz).
- **Level shifter:** SN74AHCT125N on 5 V, all four OE pins to GND. Channel 1: D4 -> 330 R -> ring DIN. Channel 2: D5 -> 330 R -> strip DIN. Channel 3: D3 -> D4184 TRIG. Channel 4: tie input to GND, output unused.
- **Build it on a 5 x 7 cm double-sided perfboard**, XIAO in two 1x7 female header strips (rows 15.24 mm apart, 2.54 mm pitch), AHCT125 in a 14-pin DIP socket, JST-XH headers: J1 socket module 5-pin (5V, GND, HALL, SW, RING_DATA), J2 window strip 3-pin (5V, GND, STRIP_DATA), J3 pump 2-pin (12 V, from the D4184 OUT terminals). The Seeed Grove shield is **not** recommended (4-pin 2.0 mm Grove ports, no 5-pin, no 12 V).
- **Grounds:** power-bank GND, boost/PD 12 V GND, D4184 DC- and GND, XIAO GND, AHCT125 GND, Hall GND, switch COM, LED GND all one net. Keep the pump wires twisted and away from the two NeoPixel data lines and the Hall wire.

## Facts and numbers

| Item | Value | Source |
|---|---|---|
| XIAO D0..D3 | GPIO26, 27, 28, 29 (ADC0-3) | [Seeed wiki XIAO RP2040](https://wiki.seeedstudio.com/XIAO-RP2040/) |
| XIAO D4, D5 | GPIO6 (SDA), GPIO7 (SCL) | same |
| XIAO D6, D7 | GPIO0 (TX), GPIO1 (RX) | same |
| XIAO D8, D9, D10 | GPIO2 (SCK), GPIO4 (MISO), GPIO3 (MOSI) | same |
| XIAO onboard LEDs | red GPIO17, green GPIO16, blue GPIO25 (active low); NeoPixel GPIO12 with power enable GPIO11 (v1.3 schematic nets: IO25_RGB-B on GPIO25, NEO_PWR on GPIO11). Note the wiki page now also covers the RP2040 Plus, whose table is laid out differently | wiki + schematic |
| XIAO board size | 21 x 17.8 mm; no mounting holes (castellated edge pads only; the DXF has just two ~1.0 mm vias/test holes at (4.58, 16.07) and (13.83, 5.10) mm, not usable for screws) | wiki + [Seeed DXF](https://files.seeedstudio.com/wiki/XIAO-RP2040/res/XIAO-RP2040-DXF.zip) (parsed with ezdxf) |
| XIAO header geometry | 7 pins per side on 2.54 mm pitch (x = 4.275 + n x 2.54 mm in DXF coordinates); castellation centers on the board edges at y = 2.261 and 20.041 mm, i.e. **17.78 mm** apart; through-hole drill centers at y = 3.531 and 18.771 mm, i.e. **15.24 mm** apart exactly (0.600 in = 6 perfboard pitches); drill ~0.85 mm, pad 1.6 mm | Seeed DXF (circle centers read from the file, not a render) |
| XIAO 5V pin | Header pin on net "VBUS" (the 7x2 header symbol in the schematic), same net as USB-C VBUS; VBUS -> D2 (NRS0320MW2T1G Schottky) -> VIN -> U4 RS3236-3.3YUTDN4 LDO -> 3V3 | [Seeed schematic v1.3 PDF](https://files.seeedstudio.com/wiki/XIAO-RP2040/res/Seeed-Studio-XIAO-RP2040-v1.3.pdf) |
| Can it be powered via the 5V pin? | Yes ("power the device with a 5V supply via VIN-PIN and 5V-PIN"); Seeed staff on USB + external 5 V at once: "Please don't do so" | wiki; [Seeed forum 281506](https://forum.seeedstudio.com/t/will-having-both-usb-and-5v-power-active-cause-problems/281506) |
| XIAO 3V3 pin budget | RS3236: "500mA Output Current", input 2.5-7.5 V, LDO with current limit and thermal shutdown (do not run LEDs from it; a DRV5032 at a few uA is fine) | [RUNIC RS3236 datasheet](https://www.run-ic.com/upload/goods/20240319/202403191550106713.pdf) (fetched, rev C.6.1) |
| RP2040 GPIO thresholds at IOVDD 3.3 V | VIH min 2.0 V, VIL max 0.8 V (Table "Digital IO characteristics"); internal pull-up RPU and pull-down RPD 50-80 kOhm | [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) (now redirects to pip-assets.raspberrypi.com; fetched) |
| A3144 supply | 4.5-24 V operating (28 V abs max); open-collector output sinks up to 25 mA; Vout(sat) 400 mV max at 20 mA | [Allegro A3141-4 datasheet](https://www.allegromicro.com/-/media/files/datasheets/a3141-2-3-4-datasheet.pdf) |
| A3144 Bop / Brp at 25 C | Bop 70 min, 350 max G; Brp 50 min, 330 max G; hysteresis 20 G min, 55 typ | same |
| A3144 over temperature and supply | Operate 35-450 G, release 25-430 G | same |
| A3144 package / pins | UA 3-lead SIP viewed from branded side: 1 = VCC, 2 = GND, 3 = OUTPUT; Hall element 0.50 mm below the branded face | same |
| A3144 pole | Branded side detects one pole; "south" is the usual Allegro convention but is **(unverified)**: neither the fetched A3144 datasheet nor the ProtoSupplies page names it (ProtoSupplies: "detects the one pole of the magnet", reverse the magnet if it does not respond). Confirm with the module LED | [ProtoSupplies 3144](https://protosupplies.com/product/hall-effect-3144/) |
| HiLetgo module | Title: "HiLetgo 5pcs Hall Effect Magnetic Sensor Module 3144E A3144 Hall Effect Sensor DC 5V for Arduino PIC AVR Smart Cars"; overview table: Voltage 5 V, 5 items; bullets are generic ("Hall Switch Integrated Circuit Using hall Effect Principle"). Pin order, pull-up value and LED are not on the page; typical 3-pin boards are "-", "+" (middle), "S" (unverified). Measure S-to-+ with power off: ~10 k means a pull-up is fitted | [Amazon B01NBE2XIR](https://www.amazon.com/dp/B01NBE2XIR) (fetched; no price shown without cart) |
| 6x2 disc field (Br 1.17-1.21 T, N35) | surface 3250-3360 G; 1 mm 2290-2370; 1.5 mm 1830-1890; 2 mm 1440-1480; 3 mm 880-910; 4 mm 550-570; 5 mm 360-370 G (computed) | formula and N35 Br from [Supermagnete FAQ](https://www.supermagnete.de/eng/faq/How-do-you-calculate-the-magnetic-flux-density) and [Supermagnete grade table](https://www.supermagnete.de/eng/physical-magnet-data) |
| Two 6x2 stacked (6x4 cylinder) | 2 mm 1990-2060 G; 3 mm 1240-1280; 4 mm 800-830; 5 mm 530-550 G (computed) | same formula |
| SMARTAKE magnets | Listing says 6x2 mm neodymium, grade not stated (assume N35; a Supermagnete 6x2 N45 is 7.26 N adhesive force for comparison) | [Amazon B0CBRVF4PN](https://www.amazon.com/dp/B0CBRVF4PN); [Supermagnete S-06-02-N](https://www.supermagnete.de/eng/disc-magnets-neodymium/disc-magnet-6mm-2mm_S-06-02-N) |
| D2F-L body | 12.8 +/-0.15 long x 5.8 +/-0.15 wide (both dimensioned on the sheet); 6.5 mm height is the usual catalog figure, not dimensioned on the fetched sheet; two 2.0 (+0.12/0) mm mounting holes on 6.5 mm centers (+/-0.1 in the terminal drawing, +/-0.15 in the mounting-hole drawing), M2 screws with plain or spring washers, 0.08-0.1 N m; terminal pitch 5.08 mm; approx. 0.5 g | [Omron D2F datasheet (DigiKey copy)](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/875/D2F_0318_DS.pdf) |
| D2F-L hinge lever | lever 12.8 mm long (t = 0.3 stainless), actuation point 10.8 mm from hinge; OF 0.78 N max (80 gf), RF 0.05 N min, OT 0.55 mm min, MD 0.5 mm max, FP 10 mm max, OP 6.8 +/-1.5 mm; no pretravel figure for lever models | same |
| D2F ratings | SPDT, 3 A 125 VAC / 2 A 30 VDC (1.47 N general purpose); mechanical life 1,000,000; contact make/break 1 ms max | same |
| D2F terminals | COM at the hinge end, NO in the middle, NC at the lever-tip end (silkscreen on body) | same, page 4 photo |
| Amazon D2F-L listing | "D2F-L 3-Pin Basic Limit Switch (Pack of 4) - SPDT 1.47N Hinge Lever Subminiature, 3A 125V, PCB Mount, IP54", brand **Pecafeitas** (a generic D2F-L clone, not Omron; Omron's own datasheet lists the D2F as IP40). Bullets: "SPDT Contact Type", "Hinge Lever Actuator", "PCB Mount Design"; overview: 125 V, 3 A, 3-pin. The 1.47 N in the title is the pin-plunger OF; a real hinge lever is 0.78 N max, and this clone's force is unverified | [Amazon B0DBV8XGG4](https://www.amazon.com/dp/B0DBV8XGG4) (fetched) |
| Dual D4184 module | Title: "6 PCS Dual High-Power MOSFET Trigger Switch Drive Module, Upgrade 0-20KHz PWM Adjustment Electronic Switch Control Board Motor Speed Controller, Lamp Brightness Control, DC 5V-36V 400W, 15A (Max 30A)", brand Ceksezx; overview: 15 A, 6 contacts, PCB mount. Terminal names, trigger range and size below come from the SCCC page for the same generic module, not from this listing | [Amazon B0FMJH3DML](https://www.amazon.com/dp/B0FMJH3DML) (fetched) |
| Dual D4184 terminals and limits | TRIG/PWM + GND (signal), DC+/DC- (supply), OUT+/OUT- (load); trigger 3.3-20 V DC; load 5-36 V; 15 A continuous; PWM 0-20 kHz; 34 x 17 x 12 mm; onboard LED when on; no flyback diode mentioned | [SCCC product page](https://scccltd.com/products/400w-15a-mos-fet-trigger-switch-drive-module-pwm-control) |
| AOD4184A MOSFET | 40 V, 50 A; Vgs(th) 1.7 / 2.1 / 2.6 V; Rds(on) 5.8 typ / 7 max mOhm at 10 V, 7.6 / 9.5 mOhm at 4.5 V; Fig. 5 shows Rds(on) climbing steeply below ~3.5-4 V; body diode Vsd 0.7-1 V | [AOS AOD4184A datasheet](https://aosmd.com/res/datasheets/AOD4184A.pdf) |
| Single-channel D4184 module (for reference) | opto-isolated version: 1 k input resistor, 4.7 k gate pull-down, no flyback diode; "3.3 and 5V logic compatible" | [ProtoSupplies D4184](https://protosupplies.com/product/d4184-mosfet-control-module/) |
| SN74AHCT125 | VIH 2.0 V min, VIL 0.8 V max at Vcc 4.5-5.5 V (so 3.3 V drives it); unused inputs must be tied to Vcc or GND | [TI datasheet](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf) |
| DRV5032 (alternative Hall sensor) | VCC 1.65-5.5 V; variants: DG 3.4 mT unipolar push-pull 80 Hz; DU 3.9 mT unipolar push-pull 20 Hz; FA 4.8 mT omnipolar push-pull 20 Hz; FB 4.8 mT omnipolar push-pull 5 Hz; FC 4.8 mT omnipolar open-drain 20 Hz; FD 4.8 mT unipolar push-pull 20 Hz; AJ 9.5 mT omnipolar open-drain; ZE 63 mT omnipolar open-drain. F-series Bop +/-1.5 min / +/-3 typ / +/-4.8 max mT, Brp +/-0.5 / 1.5 / 3 mT. Unipolar OUT1 responds to north, OUT2 to south poles at the top of the package | [TI DRV5032 datasheet](https://www.ti.com/lit/ds/symlink/drv5032.pdf) (fetched) |
| Adafruit #6051 | "ScoutMakes DRV5032 Digital Magnetic Hall Effect Sensor", $4.95, in stock; 1.65-5.5 V; 3-pin header plus JST PH 2 mm 3-pin connector; 25.6 x 17.8 x 7.2 mm. Variant, LED, pull-up and mounting holes not stated on the page (unverified) | [Adafruit 6051](https://www.adafruit.com/product/6051) (fetched) |
| Pump current | Kamoer KPHM200 (ASIN B09HGVLHFV) bullet: "Voltage: DC 12V 0.7A, Flow rate: 200ml/min, 3 rotors low pulse, weight: 302g, BPT Tubing size: 3.2mm ID x6.4mm OD" (bullet read from the amazon.in page of the same ASIN; amazon.com shows the same title, price $28.00). Kamoer's KPHM100 manual rates the equivalent 10 W brushed 12 V motor at 0.8 A, so size the 12 V fuse for ~1 A running. The Robu page ("0.7A 10W 260ml/min") is behind a Cloudflare check and could not be re-verified; its 260 mL/min figure is dropped | [Amazon B09HGVLHFV](https://www.amazon.com/dp/B09HGVLHFV); Kamoer KPHM100 product manual (file CPBZ-KPHM100-01, 2022-11-23; PDF saved by the earlier research pass, URL not re-verified) |

## Wiring table and net list

Pin assignment (XIAO RP2040):

| XIAO pin | GPIO | Mode | Goes to |
|---|---|---|---|
| D1 | 27 | INPUT_PULLUP | anode of 1N5819 whose cathode is Hall module OUT ("S") |
| D2 | 28 | INPUT_PULLUP | D2F-L NO terminal |
| D3 | 29 | OUTPUT / PWM | AHCT125 input 3A (pin 9) + 10 k to GND |
| D4 | 6 | OUTPUT | AHCT125 input 1A (pin 2) |
| D5 | 7 | OUTPUT | AHCT125 input 2A (pin 5) |
| 5V | VBUS | power in | cathode of 1N5819 from the 5 V bus |
| 3V3 | - | unused output | nothing (leave free) |
| GND | - | - | GND net |

Nets:

| Net | Members |
|---|---|
| BAT_5V | power bank USB-A/C 5 V out -> master switch -> fuse F1 (5 V rail, est. 3 A; size to final LED count) -> 5V_BUS |
| 5V_BUS | 1N5819 anode (to XIAO 5V); AHCT125 pin 14 (Vcc) with 0.1 uF to GND; Hall module "+"; NeoPixel ring 5V and strip 5V (each with the 1000 uF cap at the LED end); input of the 12 V boost or PD trigger cable (if it is fed from the 5 V rail; a USB-C PD 12 V trigger instead plugs into the bank's PD port and bypasses this net) |
| 12V | boost/PD 12 V out -> fuse F2 (1.5 A, est.) -> D4184 DC+ |
| PUMP+ | D4184 OUT+ -> J3 pin 1 -> pump red; 1N5819 cathode |
| PUMP- | D4184 OUT- -> J3 pin 2 -> pump black; 1N5819 anode |
| PUMP_TRIG | AHCT125 pin 8 (3Y) -> D4184 TRIG/PWM |
| HALL_RAW | Hall module "S" -> cathode of D-Hall (1N5819); other side of that diode is XIAO D1 |
| SW_NO | D2F-L NO -> XIAO D2 |
| RING_DATA | AHCT125 pin 3 (1Y) -> 330 R -> ring DIN |
| STRIP_DATA | AHCT125 pin 6 (2Y) -> 330 R -> strip DIN |
| GND | power bank GND, boost/PD GND, D4184 DC- and signal GND, XIAO GND, AHCT125 pin 7 and OE pins 1/4/10/13, AHCT125 pin 12 (4A, unused input tied low), Hall "-", D2F-L COM, ring GND, strip GND, 10 k pull-down on D3 |

Connectors (JST-XH 2.54 mm):

| Conn | Pins | Function |
|---|---|---|
| J1 socket module | 1 5V, 2 GND, 3 HALL_RAW, 4 SW_NO, 5 RING_DATA | the whole charging socket unplugs in one cable |
| J2 window strip | 1 5V, 2 GND, 3 STRIP_DATA | |
| J3 pump | 1 PUMP+, 2 PUMP- | 12 V, 0.7 A |

Firmware consequences: D1 reads LOW when the ring is present; D2 reads LOW when the cam presses the switch; D3 HIGH = pump on; pump trigger is forced low at boot by the 10 k pull-down until `pinMode(PUMP_PIN, OUTPUT)` runs.

Errors in the ChatGPT transcript wiring (section 6 near the end):

- "XIAO 3V3 ---- DRV5032 VCC / D1 <--- DRV5032 OUT": the bought A3144 module is 5 V only and its OUT idles at 5 V; wiring it like the DRV5032 puts 5 V on a 3.3 V-only GPIO. Use 5 V power plus the diode interface above.
- "Pump+ on the 5 V bus, MOSFET Driver (Adafruit 5648) on Pump-": the Kamoer KPHM200 is 12 V, so the pump needs the 12 V rail and the D4184 module's DC+/DC-/OUT+/OUT- terminals; the 5648's STLP-style pinout does not apply. The D4184 module has no flyback diode (the 5648 did), so add the 1N5819.
- "2 A fuse" on the 5 V bus was sized for a 5 V pump; with the pump on 12 V the 5 V fuse only needs to cover XIAO + LEDs (size to final LED count) and the 12 V branch needs its own fuse.
- Only one NeoPixel data line (D4) is shown; the firmware drives two (D4 ring, D5 strip), so two AHCT125 channels and two 330 R resistors.
- "Hall sensor power 3V3" in the pin table: wrong for the A3144; the XIAO 3V3 pin is left unused.
- Nothing in the transcript about powering the XIAO through the 5V pin while USB is connected; add the series 1N5819 and the "USB only with the master switch off" rule.

## Products to buy

| Item | Exact product | Price | Link | Why |
|---|---|---|---|---|
| Perfboard | 5x7CM Double Side Prototype Board Perforated Through Hole 0.1" White, pack of 2 | not shown on fetched page (est. $6) | [Amazon B07FTMJPHX](https://www.amazon.com/dp/B07FTMJPHX) | main electronics tray board; 50 x 70 mm fits the base drum |
| Alt. perfboard | Prototype PCB Board Double Sided 4 x 6cm FR-4, tin plated, 2.54 mm pitch, 10 pack | not shown (est. $8) | [Amazon B0B63NP3Y5](https://www.amazon.com/dp/B0B63NP3Y5) | smaller boards for the socket module (Hall + JST header) |
| Female headers (unverified: listing "Currently unavailable" on 2026-10-11) | 1x40 Pin 2.54mm Pitch Straight Single Row PCB Female Headers, 30 pcs | - | [Amazon B07VBYD2C3](https://www.amazon.com/dp/B07VBYD2C3) | cut two 1x7 strips so the pre-soldered XIAO plugs in; buy any 2.54 mm single-row female header strip instead (Vetco Electronics, Bellevue, stocks them) |
| JST-XH kit | Keszoox XH 2.54mm JST Connector Socket Kit with Pre-Crimped Cables Wire 2/3/4/5/6/7/8/9/10 Pin Housing, 22AWG, 10 colors | not shown (est. $16) | [Amazon B096Q81JBB](https://www.amazon.com/dp/B096Q81JBB) | 2-, 3- and 5-pin housings, board headers and pre-crimped leads (no crimper needed) |
| Diodes | Chanzon 100pcs 1N5819 Schottky Barrier Rectifier Diodes 1A 40V DO-41 | not shown (est. $6) | [Amazon B079KG1TN2](https://www.amazon.com/dp/B079KG1TN2) | pump flyback, Hall level diode, XIAO 5V-pin isolation (3 used) |
| Resistors (unverified: listing "Currently unavailable" on 2026-10-11) | OCR 600pcs 30 Values Resistor Kit, 1 ohm-1M ohm, 1/4 W, 1 % metal film | - | [Amazon B01N0RGA3O](https://www.amazon.com/dp/B01N0RGA3O) | 330 R x2 (NeoPixel data), 10 k (pump pull-down); only three resistors are needed, so buy singles locally (Vetco) or any in-stock 1/4 W kit that lists 330 R and 10 k |
| Better Hall sensor | ScoutMakes DRV5032 Digital Magnetic Hall Effect Sensor breakout | $4.95 (shown on page) | [Adafruit 6051](https://www.adafruit.com/product/6051) | 3.3 V native, no diode/divider, omnipolar on most variants; replaces the HiLetgo A3144 module (see Decisions) |
| Not recommended | seeed studio Seeeduino XIAO Grove Shield Extension Board with Embedded Battery Management chip (Amazon listing "Currently unavailable") | - | [Amazon B08BLCFDZB](https://www.amazon.com/dp/B08BLCFDZB); [Seeed product page](https://www.seeedstudio.com/Grove-Shield-for-Seeeduino-XIAO-p-4621.html) | 8 Grove ports (2 I2C, 1 UART, rest GPIO), all 4-pin 2.0 mm; no 5-pin, no 12 V; perfboard is simpler |

Prices: Amazon pages fetched in this session (and re-fetched by the fact-checker) returned "To see product details, add this item to your cart" instead of a price, so every Amazon price above is an estimate; only the Adafruit price was read from the page.

## Open questions / risks

- HiLetgo module schematic (pull-up value, LED wiring, pin order) could not be read from the Amazon page. Before soldering: identify "-" (marked), "+" (middle) and "S"; measure S-to-+ resistance with power off. The diode interface works either way; a divider would not.
- Magnet grade of the SMARTAKE discs is not stated; field numbers assume N35 (Br 1.17-1.21 T). If the module LED does not trip at the designed 2-3 mm gap, stack a second magnet or trim the rotor floor.
- Which pole faces the branded face: Allegro's 2000-era A3144 datasheet text does not say "south"; the ProtoSupplies page says "the labeled side detects one pole, flip the magnet if needed". Test once and mark the ring-cap magnet before gluing. (Moot with an omnipolar DRV5032.)
- Adafruit #6051: the DRV5032 variant on the board is not stated; the output type (push-pull vs open-drain), sampling rate (20 Hz vs 5 Hz) and pole response depend on it. Read the package marking or test with the ring before committing the firmware pull-up setting.
- Dual D4184 module input circuit (gate resistor, pull-down, any zener) is undocumented; after wiring, measure OUT- to DC- while the pump runs (expect < 0.1 V). If it is higher, the 5 V trigger via AHCT125 is already the fix; also confirm the module's GND and DC- are internally common (expect yes, measure continuity).
- XIAO through-hole row spacing (approx. 15.2 mm) was measured from a DXF render, not a dimensioned drawing; test-fit the female headers on the perfboard before soldering (every 2.54 mm grid fits a 6-hole gap = 15.24 mm).
- 5 V and 12 V fuse values are estimates until the LED count and the boost/PD source are final.
- The XIAO's RS3236 LDO is only used for the RP2040 itself here; do not hang the Hall module or LEDs on 3V3.

## Fact-check notes (2026-10-11, independent re-verification)

Checked by fetching every cited page/PDF again (datasheets converted with pdftotext, the XIAO DXF parsed with ezdxf, the Omron sheet read as page images). Web search was unavailable during the check, so only direct fetches were used.

Confirmed as written: XIAO D0-D10 GPIO map and 21 x 17.8 mm (Seeed wiki); VBUS -> NRS0320 -> RS3236-3.3 -> 3V3 path and 5V-pin powering (v1.3 schematic + wiki "via VIN-PIN and 5V-PIN"); Seeed staff "Please don't do so" on dual power (forum 281506); RP2040 VIH 2.0 / VIL 0.8 V at 3.3 V and RPU/RPD 50-80 kOhm; all A3144 electrical and magnetic numbers, pinout and 0.50 mm element depth; every computed 6x2 / 6x4 N35 field value (re-run with the Supermagnete formula, Br 1.17-1.21 T, agrees to the stated rounding); Supermagnete S-06-02-N is N45 / 7.26 N; all D2F-L operating characteristics (OF 0.78 N, RF 0.05 N, OT 0.55, MD 0.5, FP 10, OP 6.8 +/-1.5, lever 12.8 with 10.8 actuation point), 1 ms contact time, 1,000,000 mechanical life, 3 A 125 VAC / 2 A 30 VDC, 5.08 mm pitch, 2.0 mm holes on 6.5 mm, M2 at 0.08-0.1 N m, COM at the hinge end; SCCC D4184 module specs (TRIG 3.3-20 V, load 5-36 V, 15 A, 0-20 kHz, 3.4 x 1.7 x 1.2 cm, LED, no diode mentioned); AOD4184A ratings and the Fig. 5 knee near 4 V; SN74AHCT125 VIH/VIL; ProtoSupplies single D4184 (1 k, 4.7 k, PC817, no flyback); existence of ASINs B01NBE2XIR, B0DBV8XGG4, B0FMJH3DML, B0CBRVF4PN, B0DRNTQ338, B08R6BCSYC, B07FTMJPHX, B0B63NP3Y5, B096Q81JBB, B079KG1TN2.

Changed:
- XIAO header rows: replaced the "approx. 15.2 mm, measured from a render" estimate with the exact DXF drill centers (15.24 mm between through-hole rows, 17.78 mm between castellation rows) and noted the two ~1 mm vias that are not mounting holes.
- Pump current: the Robu page is Cloudflare-blocked, so the 0.7 A figure is now sourced to the ASIN B09HGVLHFV bullet ("DC 12V 0.7A, 200ml/min"); the Robu "260 mL/min" was dropped (Amazon and the brief say 200 mL/min); added Kamoer's 0.8 A rating for the same 10 W motor class as the fuse-sizing figure.
- RS3236 row: datasheet now fetched (500 mA, 2.5-7.5 V in).
- Hall level diode: "D1 reads ~0.4 V" widened to 0.3-0.6 V with the Vout(sat) max and Schottky drop spelled out.
- Cam travel: the "push ~3.5 mm down from free (to ~5 mm)" sentence was self-contradictory (10 - 3.5 = 6.5); rewritten around OP 5.3-8.3 mm.
- "South pole faces the branded face" downgraded to unverified: neither fetched source names the pole.
- D2F-L body: 6.5 mm height marked as catalog figure (not dimensioned on the fetched sheet); hole-spacing tolerance corrected to the two values the sheet gives.
- Amazon D2F-L (brand Pecafeitas, IP54 clone) and D4184 (brand Ceksezx) listings annotated as generics; the D2F-L clone's force is unverified.
- Products: B07VBYD2C3 headers, B01N0RGA3O resistor kit and B08BLCFDZB Grove shield are "Currently unavailable" on Amazon as of this check; marked and given local alternatives. Grove shield port count (8) added from Seeed's page.
- Added the DRV5032 / Adafruit #6051 recommendation the brief asks for (decision bullet, two fact rows, product row, open question), with the TI variant table.

Still unverified: HiLetgo module pin order, pull-up and LED wiring (not on the listing); SMARTAKE magnet grade (not on the listing); which DRV5032 variant is on Adafruit #6051; A3144 detected pole; the Pecafeitas clone's actual operating force and dimensions; all Amazon prices (pages hide price until add-to-cart); the Robu page itself.
