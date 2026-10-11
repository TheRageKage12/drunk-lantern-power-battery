# Power system research (USB power bank -> 5 V + 12 V)

Scope: pump (Kamoer KPHM200, 12 V), XIAO RP2040 + WS2812B LEDs (5 V), everything from one USB power bank in the lantern base. All numbers below come from the linked pages; anything not confirmed is labeled "estimate".

## Decisions / recommendations

- **Topology: ONE 5 V port feeds everything.** Bank USB-A (5 V/3 A) -> USB-A pigtail -> master switch -> fuse -> 5 V bus (XIAO 5V pin, NeoPixel ring, LED strip, 1000 uF cap). A 5 V -> 12 V step-up cable hangs off the same 5 V bus and feeds the D4184 MOSFET module (DC+/DC-) which switches the pump. Ground is common by construction (the boost cable is non-isolated). Do NOT use two ports of the bank at once (see common-ground section: a 10K bank throttles / drops PD when a second port is loaded).
- **12 V source, primary = option (b), a USB 5 V -> 12 V step-up cable.** Buy [B0CF5DR1JJ](https://www.amazon.com/dp/B0CF5DR1JJ) (12 V, 1.2 A max, "do not exceed 14 W", input 5 V 2-3 A, 5.5x2.1 mm plug) and, as cheap spares, the [HiLetgo 3-pack B073R7Z7CL](https://www.amazon.com/dp/B073R7Z7CL) (12 V, 10 W max, $7.99 for 3). The pump is rated 0.7 A / 10 W at 12 V, so the 1.2 A cable has margin; the 10 W HiLetgo is right at the limit. Cut the barrel plug off and solder to the D4184 DC+/DC- after checking polarity with a meter (listings do not reliably state center-positive).
- **12 V fallback = option (c), MT3608 boost module** ([Dorhea 10-pack B0BGLGL9RV](https://www.amazon.com/dp/B0BGLGL9RV), $7.99 for 10, 2-24 V in, 5-28 V out, 2 A peak; listings say keep continuous load <= ~1.2 A). Set to 12.0 V with a meter BEFORE connecting the pump. Use only if the cable sags under pump inrush. XL6009 ([B07L64GJ42](https://www.amazon.com/dp/B07L64GJ42), 6-pack, 3-32 V in) also works but is larger and its "4 A" is a peak figure.
- **Option (a), USB-C PD 12 V trigger cable, is NOT the primary.** It only works on a bank that advertises a 12 V PDO. Anker 10K banks advertise 5/9/15 V, no 12 V ([Chargerlab A1235 teardown](https://www.chargerlab.com/anker-powercore-10000-pd-power-bank-a1235-in-depth-review-compact-wonder/)); a fixed-12 V cable on such a bank gives 5 V or 9 V, not 12 ([Adafruit 5450 notes](https://www.adafruit.com/product/5450)). If you ever move to a bigger LED build (>15 W), the path is: INIU B61 (USB-C PDO 12 V/1.5 A) + [wininks 12 V trigger cable B0FD9P7PV4](https://www.amazon.com/dp/B0FD9P7PV4) ($9.97, 12 V 3 A, center-positive) on the USB-C port ONLY, then a 12 V -> 5 V buck for the LEDs. That is a bigger redesign; not needed for 84 LEDs.
- **Power bank: Anker 313 Power Bank (PowerCore 10K), model A1229, the current USB-C-output revision** ([Amazon B0D5CLSMFB](https://www.amazon.com/dp/B0D5CLSMFB), $21.99). 10,000 mAh, USB-A and USB-C outputs 5 V/3 A, documented **trickle-charging mode** (press the power button twice, or hold 2 s; LED turns green; press once to exit). Size per the Anker manual 149.5 x 68.5 x 14.5 mm, 206.5 g, so it fits the 150 x 75 x 25 mm pocket if the pocket is lengthened to ~153 mm plus ~25 mm cable clearance at the port end. Make sure the listing says "USB-C in & out, 5 V/3 A": the older A1229 revision has USB-A output 5 V/2.4 A only (12 W), which is too little during a pour.
- **Low-current auto-off: this build is probably safe even without trickle mode, but design for it anyway.** Banks cut output when load drops below roughly 50-200 mA. The lantern idles at ~0.13 A (XIAO ~50 mA + 84 WS2812B at ~1 mA each when dark); keep a faint idle "pilot" glow on the 24-px ring (~0.1 A extra) so idle draw is ~0.25 A, comfortably above any threshold. Trickle mode is the belt-and-braces backup. Mount the bank with its power button reachable through the service door (printed plunger or cut-out).
- **Current budget / runtime:** worst realistic peak is ~2.9 A at 5 V during a pour (pump 2.0 A reflected + LEDs at 50 %). Firmware should cap LED brightness at ~40-50 % during POURING and never do full-white on the 60-LED strip (3.6 A by itself). Expect ~26 h idle, ~9 h armed-pulsing, and a full Halloween night (4 h glow + 30 pours) uses ~2.3 Ah of the ~6.5 Ah usable at 5 V.
- **Protection and switching:** master switch on the 5 V line right after the USB-A pigtail (KCD1 rocker, 19 x 13 mm cutout, 6 A, or Adafruit 916 16 mm latching metal button with LED, 3 A). Fuse the 5 V bus with a 5x20 mm **3 A slow-blow (T3A)** (the bank itself limits at ~3 A so the fuse is wiring/cap-short insurance); fuse the 12 V pump leg with **1 A slow-blow (T1A)**. 1000 uF 10 V across the 5 V bus at the LED feed; 1000 uF 16 V across the 12 V rail at the D4184 input (absorbs motor inrush). 22 AWG silicone wire everywhere; 20 AWG for the main 5 V trunk if > 0.5 m. JST-SM 3-pin for ring and strip, Dupont for Hall and microswitch.
- **Charging without opening the lantern:** panel-mount USB-C extension (female on the base rear, male plugged permanently into the bank's USB-C INPUT port). Anker PowerCore banks do not pass-through (charge and discharge at once), so charge with the master switch OFF. The bank charges at 5 V/2 A (manual), ~5 h from empty.
- **Firmware adds for power:** PWM soft-start on the D4184 PWM pin (ramp 0 -> 100 % over ~300 ms) to tame inrush through the boost cable; brightness cap during POURING; idle pilot glow; "pump off at boot" already required.

## Facts and numbers

| Item | Value | Source |
|---|---|---|
| KPHM200 pump rating | 12 V, 0.7 A, 10 W, DC brushed motor, 3.2 x 6.4 mm BPT tube (retailer listing; no Kamoer datasheet found; Amazon page gives only "12 V, 200 mL/min") | [robu.in KPHM200](https://robu.in/product/kamoer-12v-0-7a-10w-260ml-min-kphm200-sw3b16-peristaltic-pump), [Amazon B09HGVLHFV](https://www.amazon.com/dp/B09HGVLHFV) |
| Pump reflected to 5 V input of a boost | 8.4 W / 0.85 = 9.9 W -> 2.0 A at 5 V (calculation, 85 % efficiency estimate) | calc |
| WS2812B / NeoPixel current | up to 60 mA per pixel full white; 20 mA per pixel typical for colors/animations; bulk cap 500-1000 uF, 6.3 V or higher | [Adafruit NeoPixel Uberguide](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels) |
| WS2812B measured | 33.5 mA and 52.5 mA per LED max on two tested types; just under 1 mA per LED when dark | [PJRC measurement](https://www.pjrc.com/how-much-current-do-ws2812-neopixel-leds-really-use/) |
| 24-px NeoPixel ring | 65.5 mm OD, 52.3 mm ID, ~18 mA per LED drive, 5 V, $16.95 | [Adafruit 1586](https://www.adafruit.com/product/1586) |
| XIAO RP2040 | 21 x 17.8 mm; can be powered through the 5V pin (VBUS); 3V3 is output only; board current not stated (~50 mA is an estimate) | [Seeed wiki](https://wiki.seeedstudio.com/XIAO-RP2040/) |
| Anker 313 (A1229) spec | Output 5 V/2.4 A (older rev) or USB-A/USB-C 5 V/3 A (current rev); input 5 V/2 A; 149.5 x 68.5 x 14.5 mm, 206.5 g; trickle mode: press twice or hold 2 s, LED green, press once to exit; USB-C and micro-USB inputs cannot be used together | [Anker A1229 manual PDF](https://salesforce-knowledge-download.s3.us-west-2.amazonaws.com/000008479/en_US/000008479.pdf), [Anker service page](https://service.anker.com/product-description/a085g000004x2B4AAI/anker-313-power-bank-powercore-10k), [Anker product page](https://www.anker.com/products/a1229), [Amazon B0D5CLSMFB](https://www.amazon.com/dp/B0D5CLSMFB) |
| Usable capacity of a 10,000 mAh bank at 5 V | Anker: "between 6,000 and 6,660 mAh"; INIU B61 measured 35.2 Wh at 5 V/1 A (7,000 mAh at 5 V), 32.2 Wh at 5 V/3 A | Anker listing text via search; [techtest.org INIU B61](https://techtest.org/iniu-powerbank-klein-aber-stark-22-5w-10000mah/) |
| Anker 10K PD PDO list (why 12 V trigger fails) | PD 5 V/3 A, 9 V/2 A, 15 V/1.25 A; no 12 V | [Chargerlab A1235](https://www.chargerlab.com/anker-powercore-10000-pd-power-bank-a1235-in-depth-review-compact-wonder/) |
| INIU B61 (BI-B61) PDO list | USB-C PD 5 V/3 A, 9 V/2.22 A, 12 V/1.5 A; USB-A QC 5 V/4.5 A, 9 V/2 A, 12 V/1.5 A; "can fully power only one port at a time; with several ports in use output is heavily throttled and fast-charge modes are disabled"; 4.1 x 2.6 x 0.9 in (104 x 66 x 23 mm), 6.9 oz | [techtest.org](https://techtest.org/iniu-powerbank-klein-aber-stark-22-5w-10000mah/), [Amazon B09176JCKZ](https://www.amazon.com/dp/B09176JCKZ) |
| PD trigger cable (wininks) | 12 V nominal (11.8-12.2 V), 3 A peak, 36 W, center-pin positive, 100 cm, USB-C PD source must offer 12 V; $9.97 | [Amazon B0FD9P7PV4](https://www.amazon.com/dp/B0FD9P7PV4) |
| PD trigger behaviour without 12 V PDO | "If your USB PD power supply does not explicitly have 12V out, this cable will provide 5V or some other lower voltage" | [Adafruit 5450](https://www.adafruit.com/product/5450) (12 V/5 A cable, $7.95, 5.5 x 2.5 mm center-positive) |
| 5 V -> 12 V cable, 1.2 A | "DC 12V 1.2A max instead of normal 0.7A", input USB 5 V 2-3 A, "do not use for more than 14 watts", 5.5 x 2.1 mm, 5 ft | [Amazon B0CF5DR1JJ](https://www.amazon.com/dp/B0CF5DR1JJ) |
| 5 V -> 12 V cable, HiLetgo | 12 V, max power 10 W, 5.5 x 2.1 mm male, 1 m, 3 pcs, $7.99 | [Amazon B073R7Z7CL](https://www.amazon.com/dp/B073R7Z7CL) |
| MT3608 module | 2-24 V in, 5-28 V out adjustable, 2 A max (listings: ~1.2 A continuous), 10 pcs $7.99 | [Amazon B0BGLGL9RV](https://www.amazon.com/dp/B0BGLGL9RV) |
| XL6009 module | 3-32 V in, 5-35 V out, "4 A" (peak), 6 pcs, price not confirmed | [Amazon B07L64GJ42](https://www.amazon.com/dp/B07L64GJ42) |
| Auto-off threshold | "often around 50-200 mA"; one builder measured ~150 mA minimum on his bank; a low-current mode on one bank still shut off after a couple of hours | [0110.be](https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks) |
| Keep-alive load (if ever needed) | constant 6-150 mA adjustable load, inline; pulsed designs "did not work reliably with all battery packs" | [SOTAbeams keep-alive](https://www.sotabeams.co.uk/usb-battery-pack-keep-alive-load/) |
| Anker pass-through | Anker staff: pass-through removed from PowerCore line (except PowerCore Fusion) | [Anker community](https://community.anker.com/t/which-portable-chargers-support-pass-through-charging/31361) via search |
| 22 AWG wire | 16.143 ohm per 1000 ft (0.053 ohm/m); 3 A over a 1 m loop drops 0.16 V (calc) | [AWG chart](https://www.mfgrobots.com/Article/mfg/it/23730.html) |
| Adafruit 916 switch | 16 mm hole, latching, 3 A / 250 VDC contacts, LED 3-6 V with built-in resistor, panel 1-13 mm, $4.95 | [Adafruit 916](https://www.adafruit.com/product/916) |
| KCD1-101 rocker | 2-pin ON-OFF, 19 x 13 mm panel cutout, 6 A/250 VAC, 10 pcs (price not confirmed, page errored) | [Amazon B0DCP39JKT](https://www.amazon.com/dp/B0DCP39JKT) |
| D4184 module (owned) | DC+/DC- supply, OUT+/OUT- load, PWM/TRIG + GND signal 3.3-20 V | BRIEF.md |

### Current budget (5 V bus, worst realistic)

| Load | Idle (dark + pilot) | Armed (green pulse) | Flash (200 ms, green 100 %) | Pouring (10 s) | Notes |
|---|---|---|---|---|---|
| XIAO RP2040 | 0.05 A | 0.05 A | 0.05 A | 0.05 A | estimate |
| 24-px ring (24 x 20 mA green full) | 0.10 A (pilot ~20 %) | 0.17 A (avg 35 %) | 0.48 A | 0.24 A (cap 50 %) | 1.44 A if full white; avoid |
| 60-LED strip (60 x 20 mA green full) | 0.06 A (dark, ~1 mA each) | 0.42 A (avg 35 %) | 1.20 A | 0.60 A (cap 50 %) | 3.60 A full white; never |
| Pump via boost (8.4 W / 0.85 / 5 V) | 0 | 0 | 0 | 2.0 A | 0.7 A at 12 V rated |
| **Total at 5 V** | **~0.2 A** | **~0.65 A** | **~1.7 A** | **~2.9 A** | bank port limit 3 A |

Runtime on 10,000 mAh (~6.5 Ah usable at 5 V): idle ~30 h, armed ~10 h; one party night (4 h at avg 0.5 A + 30 pours x 10 s x 2.9 A = 2.0 + 0.24 Ah) uses ~2.3 Ah, i.e. 2-3 nights per charge. If the pour peak must stay under 2.4 A (old-revision bank), cap LEDs at 20 % during the pour.

## Products to buy

| Item | Exact product | Price | Link | Why |
|---|---|---|---|---|
| Power bank | Anker 313 Power Bank (PowerCore 10K), A1229, USB-C in/out revision, 10,000 mAh, 5 V/3 A, trickle mode | $21.99 | [B0D5CLSMFB](https://www.amazon.com/dp/B0D5CLSMFB) | Documented trickle mode, 14.5 mm thick, fits the base pocket; 3 A port covers the pour peak |
| 5 V -> 12 V cable (primary) | USB-A to DC 5.5x2.1 mm step-up cable, 12 V 1.2 A max, 5 ft | not confirmed (est. $8-10) | [B0CF5DR1JJ](https://www.amazon.com/dp/B0CF5DR1JJ) | 1.2 A rating clears the pump's 0.7 A with margin |
| 5 V -> 12 V cable (spares) | HiLetgo 3 pcs USB to DC step-up, 12 V, 10 W, 1 m | $7.99 | [B073R7Z7CL](https://www.amazon.com/dp/B073R7Z7CL) | Known brand, three spares; 10 W is marginal for 0.7 A |
| Boost module (fallback) | Dorhea MT3608 2 A adjustable boost, 10 pcs | $7.99 | [B0BGLGL9RV](https://www.amazon.com/dp/B0BGLGL9RV) | Bench fallback if the cable sags; set 12.0 V before use |
| USB-A power pigtail | ELNONE 2 pcs USB-A male to bare wire, 22 AWG, 0.3 m, 5 V 3 A | not confirmed | [B0CPYQVPKX](https://www.amazon.com/dp/B0CPYQVPKX) | Takes 5 V off the bank's USB-A port into the switch/fuse |
| Master switch (hidden) | KCD1-101 rocker, 2-pin ON-OFF, 19 x 13 mm cutout, 6 A, 10 pcs | not confirmed (est. $6-8) | [B0DCP39JKT](https://www.amazon.com/dp/B0DCP39JKT) | Cheap, 6 A, snaps into a 2.4 mm wall |
| Master switch (lit option) | Adafruit 916 rugged metal on/off, 16 mm, red LED ring, 3 A | $4.95 | [Adafruit 916](https://www.adafruit.com/product/916) | Latching, LED runs from 5 V, confirmed 16 mm hole |
| Fuse holders + fuses | 108 pc kit: 5x20 mm inline holders (16/18/20/22 AWG, 26 cm) + fast-blow fuses 0.2-20 A incl. 1 A, 2 A, 3 A, 5 A | not confirmed | [B0B684JNKK](https://www.amazon.com/dp/B0B684JNKK) | Use F3A/F5A on 5 V, F1A or F2A on 12 V; or buy T3A/T1A slow-blow: [Amazon search](https://www.amazon.com/s?k=5x20mm+slow+blow+fuse+T3A+T1A) |
| Fuse holder only (alt) | uxcell 10 pcs inline screw-type 5x20 mm holder, 18 AWG | not confirmed | [B07SPCPD7P](https://www.amazon.com/dp/B07SPCPD7P) | If you only want holders |
| Bulk cap, 5 V rail | BOJACK 1000 uF 10 V, 8 x 12 mm, 10 pcs | not confirmed (est. $6) | [B07SD7376B](https://www.amazon.com/dp/B07SD7376B) | Adafruit's 500-1000 uF recommendation |
| Bulk cap, 12 V rail | 1000 uF 16 V radial, 10 pcs | not confirmed | [Amazon search](https://www.amazon.com/s?k=1000uF+16V+electrolytic+capacitor) | Across D4184 DC+/DC- to absorb pump inrush |
| LED connectors | BTF-LIGHTING 20 pairs JST SM 3-pin, 22 AWG, 15 cm | $9.99 | [B01DC0KIT2](https://www.amazon.com/dp/B01DC0KIT2) | Pluggable ring/strip; 22 AWG is fine for <=1.5 A per run |
| Hookup wire | TUOFENG 22 AWG silicone wire kit, 6 colors x 26.3 ft | $15.99 | [B07G2JWYDW](https://www.amazon.com/dp/B07G2JWYDW) | Flexible, heat-safe for soldering |
| Panel-mount USB-C | AAOTOKK USB-C male to female panel-mount screw cable, 0.3 m, 3 A | $9.69 | [B08HS6X44P](https://www.amazon.com/dp/B08HS6X44P) | Charge the bank through the base wall |
| (Only for option a) | wininks USB-C PD trigger to 5.5x2.1 mm, fixed 12 V, 3 A, 1 m | $9.97 | [B0FD9P7PV4](https://www.amazon.com/dp/B0FD9P7PV4) | Needs a 12 V-PDO bank such as INIU B61 [B09176JCKZ](https://www.amazon.com/dp/B09176JCKZ) |

## Common-ground check

- Inside any single power bank all output ports share the battery negative; PD negotiation changes only VBUS on the USB-C port. Tying the GND of a 12 V PD output to the GND of a 5 V USB-A output of the same bank is electrically fine (no isolation to break, no loop). I found no manufacturer page that states this explicitly; it follows from the single-cell construction and from the "2-way independent design" measurement on the Anker A1235 where both ports were loaded together ([Chargerlab](https://www.chargerlab.com/anker-powercore-10000-pd-power-bank-a1235-in-depth-review-compact-wonder/)).
- The real problem is power sharing, not ground: on the INIU B61 "only one port can be fully powered at a time; with several ports in use the output is heavily throttled and fast-charge modes are disabled" ([techtest.org](https://techtest.org/iniu-powerbank-klein-aber-stark-22-5w-10000mah/)), i.e. the 12 V PDO would drop to 5 V the moment the USB-A port is loaded. Behaviour is model-specific and undocumented on most 10K banks. Hence: single-port design (chosen), common ground automatic.
- In the chosen design the boost cable, D4184 module, XIAO and LEDs all return to the same 5 V GND. Keep the pump wires twisted and routed away from the LED data line and Hall sensor; put the 12 V cap at the D4184.

## Wiring summary

```
Bank USB-A (5V/3A) --pigtail--> MASTER SWITCH --> FUSE T3A --> 5V BUS (+1000uF 10V)
   5V BUS --> XIAO 5V pin, AHCT125 VCC, A3144 VCC
   5V BUS --> JST-SM --> 24-px ring (inject at ring), 60-LED strip (inject both ends)
   5V BUS --> 5V->12V step-up cable --> FUSE T1A --> D4184 DC+/DC- (+1000uF 16V) --> OUT+/OUT- --> pump
   XIAO GPIO --> D4184 PWM/TRIG (soft-start PWM), D4184 GND --> common GND
Bank USB-C input <-- panel-mount USB-C extension (charge with master switch OFF)
```

## Open questions / risks

- KPHM200 current (0.7 A / 10 W) is from a retailer listing, not a Kamoer datasheet; the Kamoer PDF found on robu.in is the KPHM100 manual (12 V brushed version 0.5 A, 6 W). Measure the pump on the bench; if it exceeds ~0.9 A running, go to the MT3608 module or a 15 W-class boost.
- Motor inrush through a 10-14 W boost cable is unverified. Mitigation: 1000 uF 16 V on the 12 V rail + PWM soft-start. If the cable brown-outs, the fallback module is on the BOM.
- Anker 313 revisions: the current Amazon listing (B0D5CLSMFB) shows USB-A/USB-C output 5 V/3 A and model A1229, while the Anker manual PDF for A1229 shows 5 V/2.4 A USB-A-only output. Confirm the received unit's label says 5 V/3 A; if it is the 2.4 A unit, cap LEDs to 20 % during the pour.
- Trickle mode duration: Anker does not publish whether trickle mode times out; one blog reports another brand's low-current mode shutting off after "a couple of hours". The idle pilot glow (~0.25 A total) is the primary defence; verify on the bench that the bank stays on for 2+ h with the lantern idle.
- Does the bank auto-wake when the master switch applies load? Most do; if not, the power button must be reachable (design the bank pocket with button access anyway).
- Prices marked "not confirmed" were not visible in the fetched page text; the ASIN and title/spec were confirmed. Polarity of the 5 V -> 12 V cables is not stated on the pages fetched: check with a meter before wiring.
- Panel-mount USB-C flange dimensions and screw spacing were not on the page; measure the part before cutting the base (estimate: flange ~25 x 12 mm, screws ~20 mm apart).
- If the LED count grows (e.g. 144-LED strip), the 15 W single-port budget is gone; that is the point to switch to a 12 V/1.5 A PDO bank (INIU B61) + 12 V trigger cable + 12 V -> 5 V buck, or to a 45 W bank with a 15 V/20 V trigger and two bucks.
