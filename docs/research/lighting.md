> **Historical.** Written early in the design (revisions 2-5). It still describes WS2812B/NeoPixel strips from Adafruit on a 5 V bank (built: a 12 V green COB strip). The current design is in `docs/BUILD_GUIDE.md`, `cad/params.py` and `cad/DESIGN_CONTRACT.md`; the decisions are summarised in `docs/review/CONTEXT.md`.

# Lighting research: "almost obnoxiously bright" green

Scope: charging-socket ring, sphere glow, diffusion, AHCT125 level-shifter wiring, light choreography.
Driver: XIAO RP2040 (3.3 V) -> SN74AHCT125N (shortlisted, not bought) -> WS2812B data. 5 V from the USB power bank.

## Decisions / recommendations

- Socket ring: Adafruit NeoPixel Ring 24 (product 1586), 65.5 mm OD / 52.3 mm ID / 3.2 mm thick (Adafruit page), 24 px. Pads: GND, PWR +5V (two of each on this ring), Data Input, Data Output. Chainable: Data OUT -> next Data IN.
- Sphere glow: WS2812B 5 V strip, 60 LED/m, 1 m, IP30, black PCB (BTF-LIGHTING, ASIN B01CDTED80). 60 px, 10 mm wide, 16.7 mm pitch, 3-pin connectors pre-installed. Cut into 8 rows x 7 px (56 px used, 4 spare) soldered as a serpentine onto a flat white-PETG carrier that sits 25 mm behind the front diffuser and doubles as the front wall of the hidden glass bay. Total chain: 56 (sphere) + 24 (ring) = 80 px (plan power for 84 if you keep all 60).
- Why not the others: 144/m gives no more light within the same 5 V current budget (light out is set by amps, not LED count), needs a 5 V/6 A supply per the brand and runs hotter (the BTF 144/m is $16.99 vs $8.99 for 60/m on Amazon; the Adafruit 144/m is $59.95); WS2815 12 V still needs 4 wires (12V, GND, DI, BI), the brand recommends 12 V/3 A for 1 m, and it ties the LEDs to the PD-trigger 12 V budget shared with the pump; FCOB 160/m is the only real upgrade (dot-free at half the diffuser distance) but needs 5 V/3 A per metre, the per-colour draw is not published, and reviews say it is hard to cut cleanly; 2 x 3 W green LEDs need a buck driver each, a heatsink, a 4th PWM channel and cannot do a swirl.
- Currents (Adafruit rule: 60 mA/px full white = 20 mA per colour channel): full green (0,255,0) = 80 px x 20 mA = 1.60 A; "white-ish green" (40,255,40) = 26.3 mA/px = 2.10 A. With all 84 px: 1.68 A / 2.21 A. Budget assumption (estimate): one 5 V / 2.4-3 A bank port for XIAO + LEDs; pump on the separate 12 V PD-trigger port. Keep continuous LED draw <= 2.0 A, flash <= 2.2 A for <= 200 ms. If the bank port is rated 2.4 A or less, call setBrightness(220) once in setup() as a hard ceiling.
- Diffuser: print the front window in white PETG, 0.8 mm (4 x 0.2 mm layers, 100 % infill, flat on the bed). Print a 0.6 mm test coupon too; pick the one that hides the dots. Do not use the green PETG for the diffuser (green over green loses output and shifts hue); natural/clear PETG at 1.2 mm passes more light but shows every LED unless sanded (220 grit) and spaced further.
- Distance LED-to-diffuser >= LED pitch (lighting-industry 1:1 rule): 60/m pitch 16.7 mm -> use 20-25 mm. For the socket ring (pitch about 7.7 mm) put the translucent ring 8-10 mm above the LEDs, or 5 mm if it is 1.0 mm white PETG.
- Sphere interior: do NOT line with aluminium tape (specular; mirrors each LED into the diffuser, crinkles). Print the LED carrier and glass-bay walls in white PETG, or brush/spray the bay walls matte white. Leave the green PETG sphere walls unlined so the whole sphere glows (2.4 mm green PETG transmits; test with a phone torch - estimate).
- Heat: 56 px full green = 1.1 A x 5 V = 5.6 W, but only for ~15 s per pour; IDLE is <= 0.3 W. WS2812B junction limit is +70 C (datasheet). Add 3-4 hidden 2 x 10 mm vent slots at the top-rear of the sphere and keep the strip off the PETG with the white carrier. No fan needed.
- AHCT125 (DIP-14): VCC pin 14, GND pin 7, 1OE pin 1 -> GND, 1A pin 2 <- XIAO data pin, 1Y pin 3 -> 470 ohm -> first Data In. Tie the unused gates: pins 4, 10, 13 (2OE/3OE/4OE) and pins 5, 9, 12 (2A/3A/4A) to GND (datasheet: all unused inputs must be at VCC or GND). 100 nF ceramic across pins 14/7. Optional: use gate 2 (2A pin 5 -> 2Y pin 6, 2OE pin 4 to GND) as a second independent data line for the ring instead of chaining.
- Data resistor 330-470 ohm, placed at the LED end of the wire (Adafruit Uberguide). 1000 uF 6.3 V+ electrolytic across 5 V/GND at the strip's power entry. Connect order: GND, then 5 V, then data. Data wire < 1 m (Adafruit: degrades over ~3 ft). Feed 5 V/GND to the ring directly from the 5 V bus (22 AWG), not through the strip end.
- Data pin: any digital pin. The transcript used D4 = GPIO6 (Seeed wiki); D4/D5 are I2C0 but nothing else uses I2C. Chain order: XIAO -> AHCT125 -> sphere strip (px 0-55) -> ring (px 56-79). Note: the repo firmware (firmware/green_lantern/green_lantern.ino) instead drives the ring on D4 and the strip on D5 as two separate NeoPixel objects, i.e. the "optional gate 2" wiring below; either works, keep the wiring and the sketch consistent.

## Facts and numbers

| Fact | Value | Source |
|---|---|---|
| NeoPixel Ring 24 dims | OD 65.5 mm, ID 52.3 mm, thick 3.2 mm, 24 x 5050, ~18 mA constant-current drive per LED, $16.95, ships with WS2812B or SK6812 LEDs | [Adafruit 1586](https://www.adafruit.com/product/1586) |
| Ring 24 thickness (guide) | "about 3.6 mm (1.6 mm PCB + 2 mm LEDs)" - plan clearance for 3.6 mm | [Uberguide rings](https://learn.adafruit.com/adafruit-neopixel-uberguide/neopixel-rings) |
| Ring pads | 5V (two on large rings), GND (two), Data IN, Data OUT; chain Data OUT -> Data IN; data wires < ~3 ft (the Uberguide best-practices page is looser: "a meter or two is usually no problem") | [Adafruit soldering rings](https://learn.adafruit.com/make-it-glow-how-to-solder-neopixels-a-beginners-guide/soldering-rings) |
| Ring pads (reseller naming) | GND, PWR +5V, Data Input, Data Out; "~50 mA per LED at full white (~1.2 A max for the ring)"; ID 52.5 mm | [Pololu 2538](https://www.pololu.com/product/2538) |
| Per-pixel current | 60 mA max at full white; 20 mA/px rule of thumb for typical colour | [Uberguide power](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels) |
| Capacitor / resistor / shifter | 500-1000 uF, 6.3 V+ across +/-; 300-500 ohm at the pixel end of the data wire; 3.3 V MCUs "must use a logic level shifter such as a 74AHCT125 or 74HCT245"; connect GND, +5V, then data | [Uberguide best practices](https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices) |
| SN74AHCT125 pinout (DIP N) | 1OE=1, 1A=2, 1Y=3, 2OE=4, 2A=5, 2Y=6, GND=7, 3Y=8, 3A=9, 3OE=10, 4Y=11, 4A=12, 4OE=13, VCC=14; OE low = output enabled; VCC 4.5-5.5 V; VIH min 2.0 V; unused inputs must be tied to VCC or GND | [TI datasheet PDF](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf) |
| WS2812B limits | VDD 3.5-5.3 V abs max; Topt -25 to +70 C; VIH 0.7 VDD (= 3.5 V at 5 V, so 3.3 V logic is out of spec); green 510-525 nm, 290 mcd typ | [WS2812B datasheet (LuxaLight copy)](https://www.luxalight.eu/sites/default/files/downloads/2020-03/Datasheet_WS2812B.pdf) |
| BTF 60/m 1 m strip | $8.99 (fetched 2026-10-11); 60 LED/IC/px, 10 mm wide x 2 mm (IP30), "DC5V 2A 10W" recommended, "18 watts" in the Amazon spec table, colour order G R B, 3-pin connectors pre-installed both ends, size options 60/100/144 px per 3.2 ft | [Amazon B01CDTED80](https://www.amazon.com/dp/B01CDTED80) |
| BTF 144/m 1 m strip | $16.99; 144 px, DC5V, IP30, black PCB, 12 mm wide; "Recommended power supply: DC5V 6A 30W" | [Amazon B01CDTEJR0](https://www.amazon.com/dp/B01CDTEJR0) |
| Adafruit 144/m strip | 35 W max (~7 A at 5 V) per metre, 15 mm wide, $59.95/m | [Adafruit 1506](https://www.adafruit.com/product/1506) |
| Adafruit 60/m strip | 18 W max (~3.5 A at 5 V) per metre, 12.5 mm wide, 1 m out of stock, 2 m $49.90 | [Adafruit 1138](https://www.adafruit.com/product/1138) |
| BTF FCOB 160/m 1 m | $13.99; 160 LED/m, 160 IC/m, 5 mm wide (10 mm option), IP30, "Cut every 12.5mm (marked)", "A 5V/3A adapter per 3.2FT (160 LEDs) is recommended", operating temp -20 to +45 C | [Amazon B0CNXKSWD7](https://www.amazon.com/dp/B0CNXKSWD7) |
| BTF WS2815 12 V 1 m | $20.99; 144 px, DC12V, IP30, white PCB, 12 mm wide, dual-signal (BI backup) 4-pin; "Recommended power supply: DC12V 3A 36W" (= ~21 mA/px at 12 V, derived); per-pixel draw not on page | [Amazon B07LG6521N](https://www.amazon.com/dp/B07LG6521N) |
| 3 W green LED | $10.69; LEDGUHON, 700 mA, 3.0-3.4 V, 140 deg, 520-525 nm, 20 mm star base, 5 pcs | [Amazon B0D8VXVHX6](https://www.amazon.com/dp/B0D8VXVHX6) |
| 3 W CC driver | CoCocina 3 pcs; 5-35 V in, 700 mA +/- 20 mA out, "High level turn off the output, Low level open the output", LED string must be 2-3 V below input; listing "Currently unavailable" at fact-check | [Amazon B08CKKLG8S](https://www.amazon.com/dp/B08CKKLG8S) |
| Diffuser distance rule | "the distance between the LEDs and the cover should be equal to the LED pitch" | [Lumistrips backlighting guide](https://us.lumistrips.com/lumistrips-blog/led-pitch-and-distance-to-cover-for-optimum-backlighting/) |
| Printed diffuser experience | 2 layers at 0.2 mm first, thicken if too bright; no infill over the light path (one poster got the best result at 100 % infill with ironed top layers); "~1 cm offset" claim (unverified: Printables page returned 403) | [Bambu forum](https://forum.bambulab.com/t/led-diffuser-using-transparent-pc/185469), [Printables diffuser (unverified)](https://www.printables.com/model/34916-deformable-led-light-diffuser) |
| White paint vs foil | flat white ~85-90 % diffuse; aluminium ~94-98 % but specular (foil is a mirror, paint is a diffuser) - percentages unverified (thread returned 403 at fact-check); the specular-vs-diffuse point stands on its own | [trains.com thread (unverified)](https://forum.trains.com/t/white-paint-or-aluminum-foil-which-is-better-light-amplifier/285026) |
| XIAO RP2040 pins | D4 = GPIO6 (SDA0), D5 = GPIO7, D6 = GPIO0, D7 = GPIO1, D8 = GPIO2, D9 = GPIO4, D10 = GPIO3; 5V pin = VBUS in/out; MCU is 3.3 V, >3.3 V on GPIO damages it | [Seeed wiki](https://wiki.seeedstudio.com/XIAO-RP2040/) |
| Bank port ratings (example: Philips DLP5720C 20000 mAh, 2x USB-A + USB-C PD) | USB-A: 5 V/2.4 A; USB-C: 5 V/2 A, 9 V/3 A, 12 V/3 A, 14.5 V/3 A, 20 V/2.25 A. Note the USB-C port gives only 2 A at 5 V on this bank - the 5 V/3 A, 9 V/2.22 A, 12 V/1.67 A set is the generic 20 W PD profile (unsourced, estimate), not this sheet | [Philips DLP5720C leaflet](https://www.documents.philips.com/assets/20231123/ed8fa24a16ad4398a7bbb0c30045cbe4.pdf) |
| Adafruit_NeoPixel API | signatures below are from the library header | [Adafruit_NeoPixel.h](https://raw.githubusercontent.com/adafruit/Adafruit_NeoPixel/master/Adafruit_NeoPixel.h) |

Current table (20 mA per colour channel at value 255, scaled linearly; estimates):

| State | Pixels and colour | Current |
|---|---|---|
| Idle breathe 3-10 % green, sphere only | 56 px x (0, 8-26, 0) | 0.03-0.11 A |
| Armed peak 100 % green | 80 px x (0,255,0) | 1.60 A |
| Flash 200 ms | 80 px x (40,255,40) | 2.10 A |
| Pouring swirl (avg 75 % green) | 56 px avg (0,190,0) + ring comet | ~0.95 A avg, 1.3 A peak |
| Locked afterglow hold 25 % | 80 px x (0,64,0) | 0.40 A |
| All 84 px full green / (40,255,40) | | 1.68 A / 2.21 A |

## Products to buy

| Item | Exact product | Price | Link | Why |
|---|---|---|---|---|
| Socket ring | Adafruit NeoPixel Ring - 24 x 5050 RGB LED, product 1586 | $16.95 (page) | [Adafruit 1586](https://www.adafruit.com/product/1586) | Fits the 44 mm rotor (ID 52.3) inside a 65.5 mm OD pocket; chainable |
| Sphere strip | BTF-LIGHTING WS2812B DC5V 3.28FT 60LED IP30, black PCB, pure gold wires | $8.99 (fetched) | [Amazon B01CDTED80](https://www.amazon.com/dp/B01CDTED80) | 60 px / 1.2 A full green, 10 mm wide, pre-wired 3-pin ends, cheapest bright option |
| Data resistor | Adafruit Through-Hole Resistors 470 ohm 5 % 1/4 W, pack of 25 (product 2781) | $0.75 | [Adafruit 2781](https://www.adafruit.com/product/2781) | 330-470 ohm series resistor on each data line |
| Bulk capacitor | E-Projects 1000 uF 16 V 105 C radial, pack of 5 | $6.63 (fetched) | [Amazon B07YN6DS58](https://www.amazon.com/dp/B07YN6DS58) | Uberguide 500-1000 uF at the strip power entry |
| Decoupling cap | 0.1 uF (100 nF) ceramic, any kit | ~$5 | [Amazon search](https://www.amazon.com/s?k=100nF+ceramic+capacitor+kit) | Across AHCT125 pins 14/7 |
| Diffuser + carrier filament | AMOLEN PETG bundle 4 x 250 g: translucent clear/white, red, green, blue | $24.99 (fetched) | [Amazon B08Z77GCM4](https://www.amazon.com/dp/B08Z77GCM4) | Small spools to test white vs translucent-green diffusers without buying 1 kg |
| Alt. white PETG | SUNLU PETG 1.75 mm 1 kg White | $15.99 (fetched) | [Amazon B085TH48N6](https://www.amazon.com/dp/B085TH48N6) | If a full spool of white is wanted (carrier, bay walls, diffuser) |
| Wire | 22 AWG silicone hook-up wire (5 V/GND) + 26 AWG (data) | ~$15 | [Amazon search](https://www.amazon.com/s?k=22+awg+silicone+wire+kit) | 2 A runs base -> sphere -> socket |
| Runner-up strip | BTF-LIGHTING FCOB WS2812B DC5V 3.2FT 160LED 5 mm IP30 | $13.99 (fetched) | [Amazon B0CNXKSWD7](https://www.amazon.com/dp/B0CNXKSWD7) | Dot-free glow if the 25 mm gap cannot be had; needs 5 V/3 A |
| Not recommended | BTF WS2815 12 V 1 m 144 px | $20.99 | [Amazon B07LG6521N](https://www.amazon.com/dp/B07LG6521N) | 4 wires, shares 12 V with pump, no 5 V saving worth the complexity |
| Not recommended | LEDGUHON 3 W green 700 mA star x5 + CoCocina 700 mA buck driver x3 (driver listing currently unavailable) | $10.69 + n/a | [LED B0D8VXVHX6](https://www.amazon.com/dp/B0D8VXVHX6), [driver B08CKKLG8S](https://www.amazon.com/dp/B08CKKLG8S) | Needs heatsinks, extra PWM pin, no swirl |

## Wiring (AHCT125, DIP-14, notch up, pin 1 top-left)

```
XIAO 5V  ----+---- AHCT125 pin 14 (VCC)      100 nF between pin 14 and pin 7
XIAO GND ----+---- AHCT125 pin 7  (GND)
             +---- pins 1 (1OE), 4, 10, 13 (2OE,3OE,4OE), 5, 9, 12 (2A,3A,4A) -> GND
XIAO D4 (GPIO6) -> pin 2 (1A)
pin 3 (1Y) -> 470 ohm (at the strip end of the wire) -> strip Data In (px 0)
strip Data Out -> ring Data Input (px 56..79); ring Data Out unused
5 V bus -> 1000 uF (+) -> strip 5V and ring PWR +5V (separate 22 AWG runs); all GND common
```

## Choreography (all colours as (R,G,B); gamma via gamma32; frame rate 50 Hz)

| State | Look | Timing | Brightness | Current |
|---|---|---|---|---|
| IDLE | slow breathe, sphere only; ring off | 4.0 s period, sine | 3 % floor to 10 % peak green | <= 0.11 A |
| ARMED (ring inserted) | pulse that builds while the oath is spoken; ring runs a 4 px comet | period 1.2 s shrinking to 0.5 s over 15 s; floor 15 -> 60 %, peak 40 -> 100 % | up to 100 % green | <= 1.60 A at the final peaks |
| FLASH (twist) | everything to white-ish green, then snap down | 200 ms hold, 150 ms linear fall to 50 % | (40,255,40) | 2.10 A for 0.2 s |
| POURING (10 s) | travelling sine wave down the serpentine rows + 2 px ring comet with tail | wave period 0.6 s, comet 1 rev/s | 50 % base, 100 % crests | ~0.95 A avg, 1.3 A peak |
| LOCKED | afterglow: exponential fall then shimmer | 2 s fall 100 -> 25 %, then 25-35 % at 0.5 Hz until ring removed; 1 s fade to IDLE | 25-35 % green | ~0.4-0.56 A |
| ABORT (ring pulled mid-pour) | 3 red blinks then LOCKED | 3 x 150 ms on/off | (255,0,0) at 60 % | 0.96 A peak |

Library calls (signatures from Adafruit_NeoPixel.h):

```cpp
#include <Adafruit_NeoPixel.h>
constexpr uint16_t N_SPHERE = 56, N_RING = 24, N_PX = N_SPHERE + N_RING;
constexpr int16_t  LED_PIN  = D4;                       // GPIO6 on XIAO RP2040
Adafruit_NeoPixel px(N_PX, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  px.begin();                 // bool begin(void)
  px.setBrightness(255);      // call ONCE; 220 if the bank port is <= 2.4 A
  px.clear(); px.show();      // pump stays off until the state machine says so
}

// helpers: pct 0..255 scales the green channel; sine8(x) returns 0..255 sine of x/256 turns
static inline uint32_t green(uint8_t v)            { return px.gamma32(px.Color(0, v, 0)); }
static inline uint32_t whitish(uint8_t v)          { return px.gamma32(px.Color(v * 40 / 255, v, v * 40 / 255)); }
static inline uint8_t  lerp8(uint8_t a, uint8_t b, uint8_t t) { return (uint8_t)(a + (int16_t)(b - a) * t / 255); } // signed: works for b < a too

void breathe(uint32_t ms, uint16_t period_ms, uint8_t lo, uint8_t hi) {       // IDLE / ARMED
  uint8_t s = px.sine8((uint8_t)(ms * 256UL / period_ms));                    // 0..255
  px.fill(green(lerp8(lo, hi, s)), 0, N_SPHERE);                             // sphere only
}
void flash(bool on) { px.fill(on ? whitish(255) : green(128)); }             // FLASH (fill all)
void swirl(uint32_t ms) {                                                     // POURING
  for (uint16_t i = 0; i < N_SPHERE; i++) {
    uint8_t row = i / 7;                                                      // serpentine row index
    uint8_t s = px.sine8((uint8_t)(ms * 256UL / 600 + row * 32));
    px.setPixelColor(i, green(lerp8(128, 255, s)));
  }
  uint16_t head = (ms / (1000 / N_RING)) % N_RING;                            // 1 rev / s
  px.fill(0, N_SPHERE, N_RING);
  for (uint8_t k = 0; k < 6; k++)                                             // comet + tail
    px.setPixelColor(N_SPHERE + (head + N_RING - k) % N_RING, green(255 >> k));
}
void afterglow(uint32_t ms_since_lock) {                                      // LOCKED
  uint8_t v = ms_since_lock < 2000 ? lerp8(255, 64, ms_since_lock * 255 / 2000)
                                   : lerp8(64, 90, px.sine8(ms_since_lock * 256UL / 2000));
  px.fill(green(v));
}
// in loop(): pick the state function, then px.show();  (never call show() faster than ~every 3 ms for 80 px)
```

Notes: setBrightness() is lossy and meant for one call in setup (Adafruit guide); all animation scaling is done in the helpers. ColorHSV(hue, sat, val) with hue 0x5555 (green) is the alternative if you want the hue to drift slightly toward cyan during POURING. px.numPixels() returns 80.

## Open questions / risks

- Amazon prices were fetched on 2026-10-11 and will drift; the 3 W driver listing (B08CKKLG8S) is currently unavailable (irrelevant unless the not-recommended 3 W LED route is taken).
- 5 V budget is an assumption: confirm the chosen bank's 5 V port rating (needs 5 V/3 A, or 2.4 A with setBrightness(220)) and that it will run two ports at once (5 V for logic/LEDs, 12 V PD for the pump). Real banks vary: the Philips DLP5720C leaflet gives 5 V/2.4 A on USB-A and only 5 V/2 A on USB-C, so read the fine print of the actual bank.
- The 1586 ring may ship with SK6812 instead of WS2812B LEDs (Adafruit page); both work with NEO_GRB + NEO_KHZ800.
- Ring thickness is listed as 3.2 mm (product page) and ~3.6 mm (learn guide); design the socket pocket for 4 mm.
- WS2812B VIH is 0.7 VDD (3.5 V at 5 V), so the AHCT125 is mandatory, not optional. The common "diode-drop the first pixel" trick is not needed because the shifter gives a true 5 V swing.
- Serpentine means 7 solder jumpers (5V, GND, DI each) on the carrier. If that is unwelcome, the 100 LED/m option on the same listing (10 mm pitch) makes 6 rows x 10 px with the diffuser at 10-12 mm; or the FCOB strip (cut every 12.5 mm).
- Heat in the closed sphere was estimated from power, not measured: run a 10-minute full-green soak test with the sphere closed and check the strip and PETG by touch; add vents if the carrier is more than warm.
- Whether 2.4 mm green PETG walls glow enough to be worth leaving unlined was not tested; print one sphere half first and hold the strip inside.

## Fact-check notes (2026-10-11)

Independently re-fetched every cited page (Adafruit 1586/1506/1138/2781, Uberguide power/best-practices/rings/arduino-library-use, soldering-rings guide, Pololu 2538, TI SN74AHCT125 PDF, WS2812B PDF, Seeed XIAO RP2040 wiki, Adafruit_NeoPixel.h, Lumistrips, Bambu forum, Philips PDF, and Amazon B01CDTED80 / B01CDTEJR0 / B0CNXKSWD7 / B07LG6521N / B0D8VXVHX6 / B08CKKLG8S / B07YN6DS58 / B08Z77GCM4 / B085TH48N6). Re-computed the current table from the 20 mA/channel rule (all rows check out; "pouring" and "peak" rows are rounded estimates).

Changed:
- Bank-port row: the cited Philips PDF is the DLP5720C (20000 mAh), not a "DLP7721C", and lists USB-A 5 V/2.4 A and USB-C 5 V/2 A, 9 V/3 A, 12 V/3 A, 14.5 V/3 A, 20 V/2.25 A. The old "5 V/3 A, 9 V/2.22 A, 12 V/1.67 A" figures were not from that document and are now marked as the generic 20 W PD profile (unsourced estimate).
- "144/m costs ~4x": wrong for the Amazon part (BTF 144/m $16.99 vs 60/m $8.99); rewritten with the fetched prices and the brand's 5 V/6 A recommendation. Added BTF 144/m width (12 mm, not the Adafruit 15 mm).
- WS2815 row: replaced the "~15 mA/px, retailer spec" guess with the listing's own "DC12V 3A 36W" recommendation (~21 mA/px derived); added price and 12 mm width.
- Filled in fetched Amazon prices (strip $8.99, FCOB $13.99, WS2815 $20.99, capacitor $6.63, AMOLEN $24.99, SUNLU $15.99, 3 W LED $10.69) and marked the CoCocina 3 W driver listing "Currently unavailable".
- Marked the trains.com reflectance percentages and the Printables "~1 cm offset" as (unverified): both pages returned HTTP 403 and the search budget was exhausted, so no substitute source could be found.
- Header: the AHCT125 was listed as "bought"; per the brief nothing has been bought.
- Added a note that the repo firmware uses two data pins (D4 ring, D5 strip), matching the "optional gate 2" wiring, not the single chain the text assumes.
- Fixed lerp8(): the unsigned cast made it wrong whenever b < a (the LOCKED afterglow call); now uses signed math.

Confirmed as written: Adafruit 1586 dimensions/price/18 mA/WS2812B-or-SK6812; Uberguide 3.6 mm ring thickness; ring pads and 3 ft data-wire note; 60 mA / 20 mA rule; 500-1000 uF, 300-500 ohm, 74AHCT125/74HCT245, GND-5V-data order; SN74AHCT125 DIP pinout, 4.5-5.5 V, VIH 2.0 V, OE active-low, unused-inputs note; WS2812B abs-max VDD 3.5-5.3 V, Topt -25 to +70 C, VIH 0.7 VDD, green 510-525 nm 290 mcd; BTF 60/m specs (10 mm, DC5V 2A, 18 W, GRB, connectors, 60/100/144 options); FCOB 160/m specs; Adafruit 1506 (35 W, 15 mm, $59.95) and 1138 (18 W, 12.5 mm, 1 m out of stock, 2 m $49.90); Adafruit 2781 ($0.75, 25 pcs); Pololu pad names / 52.5 mm ID / ~1.2 A; Lumistrips pitch = distance rule; XIAO RP2040 D4-D10 GPIO map, 5V = VBUS, 3.3 V warning; Adafruit_NeoPixel API signatures; setBrightness "once in setup, lossy" guidance.

Still unverified: reflectance percentages (paint vs foil); Printables 1 cm offset; whether 2.4 mm green PETG glows usefully (untested); heat in the closed sphere (estimated, not measured); the generic 20 W PD port profile.
