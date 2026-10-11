# Adversarial design review (before CAD is frozen)

Scope: BRIEF.md, cad/DESIGN_CONTRACT.md + params.py + NOTES-dishes.md + parts/base.py, firmware/green_lantern/green_lantern.ino,
the five sibling research notes (electronics, power, lighting, mechanical, pump-and-plumbing), and the final ChatGPT
plan sections of the transcript ("Tech Spec and Build Procedure", "Build Procedure", hidden-glass update, owner's last message).
Severity: BLOCKER = CAD or purchase cannot proceed correctly; MAJOR = will fail or disappoint at the party; MINOR = polish.

## Decisions / recommendations (the short list)

- Change the reservoir from the 133 mm tall Boston round to a jar/pouch that fits entirely inside the 100 mm base and can be
  refilled through the rear door: standing on base.py's deck (top Z 26) its cap must stay below the door's top edge (Z 88), i.e.
  a jar no taller than ~60 mm, or a pouch; vent it with a tube, not an open hole (issues 1, 5, 7).
- Widen the sphere hatch to at least 105 x 100 mm and make the glass cradle a pull-out tray that rides on the hatch door, so the
  glass is presented instead of fished out of a 180 mm sphere with one hand (issues 2, 3).
- Fix the socket module geometry before modelling: housing OD <= 78 mm so it passes the 80 mm dish hole; rotor becomes a
  ~10 mm disc (not 22 mm) so the Hall sensor sits 2 mm under the magnet; cam lift ~4-5 mm (not 1.2); spring numbers from
  mechanical.md (2 mm preload, ~10 mm at 45 deg), not the contract's 40 %/75 % (issues 9-12).
- Hall sensor: make the Adafruit/ScoutMakes DRV5032 (#6051) the primary, A3144 the alternate. DRV5032 runs at 3.3 V (no
  diode/divider), trips at 3-4.8 mT (vs A3144 35-45 mT) and senses perpendicular to its board, which matches a magnet on the
  rotor axis above a board lying flat (issues 10, 17).
- Fluid path: nozzle must approach the glass from the side at 45 deg (or through a short rigid stainless tip); there is no
  room for a 6.4 mm silicone tube to U-turn above the glass (issue 4). Tube cannot be "one continuous piece" if the bottle
  cap must come off for refills unless the cap is drilled and the tube pushed through (it is: keep that).
- Power: the single 5 V port + 10-14 W step-up cable + 10 W pump + LEDs is the weakest link (3.0-3.3 A at 5 V during a pour,
  against a 3 A port). Bench-test with a USB meter before committing; preferred fix is a 12 V-PDO bank + 12 V trigger cable
  with a 12 V -> 5 V buck for LEDs/XIAO (one port, 18 W), fallback is the Pololu U3V70F12 boost (issue 15).
- Firmware: add a hidden PRIME button (D6) so a bottle swap at the party does not need a laptop; raise the idle "pilot"
  current so the bank does not auto-off; abort on raw Hall loss (<= 30 ms) instead of the 200 ms "ring gone" filter; add a
  separate POURING brightness cap (issues 22, 16, 23, 15).
- Resolve the two remaining document conflicts now: one NeoPixel chain (lighting.md) vs two data pins (firmware/electronics.md);
  12 V from a PD port (lighting.md budget) vs boost cable (power.md). (The pump-orientation conflict is already resolved: the
  current base.py mounts the pump horizontally on a deck, head toward the door, as contract rev. 2 asks.)

## Facts and numbers

| Fact | Value | Source |
|---|---|---|
| Stack heights (assembly Z, mm) | base top 100; lower dish top 177; sphere centre 235.5; sphere top 294; bay floor seat 183 | cad/params.py derived values; cad/NOTES-dishes.md (`BAY_FLOOR_SEAT_Z` = 183) |
| Socket module depth below faceplate | 30 (`SOCKET_HOUSING_H`), faceplate seat Z = sphere top - 1 = 293 -> housing bottom ~263 | cad/params.py, cad/NOTES-dishes.md |
| Free height in the glass bay | 263 - 183 = 80 mm (calc) | from the two rows above |
| Glass envelope + nozzle gap | 62 + 12 = 74 mm; tube OD 6.4 -> tube top edge at 74 + 6.4 = 80.4 mm (calc) | cad/params.py `GLASS_H`, `TUBE_OD`; contract "tip 12 mm above the glass rim" |
| Hatch opening | 78 x 92 mm, centre Z 227.5 (sphere centre - 8) -> Z 181.5 to 273.5 | cad/params.py `HATCH_W/H`, DESIGN_CONTRACT.md |
| Dish neck hole vs socket housing | hole 80, housing OD 92, faceplate 100 | cad/NOTES-dishes.md "Known issues", cad/params.py |
| Base interior / door | base 100 tall, door opening 110 x 76 at Z 12-88; bottle envelope 60 x 136 standing on the deck (deck top Z 26) at (-39.5, 0), so the cap top is at Z ~162 with 2.7 mm to the lower-dish cone | cad/parts/base.py `DOOR_Z0/Z1`, `BOTTLE_X/Y`, `DECK_TOP`; cad/params.py `BOTTLE_H`; cad/NOTES-base.md ("bottle top at Z 162") |
| Pump orientation | NO conflict in the current code: base.py lies the pump "with the motor axis along Y, head face toward the rear door" on a deck (axis Z 57.5, top Z 89, under the 92 mm spigot zone), matching contract rev. 2; cad/NOTES-base.md exists and documents it | cad/parts/base.py `PUMP_AXIS_Z`, `PUMP_HEAD_FACE_Y`; cad/NOTES-base.md; cad/DESIGN_CONTRACT.md Revision 2 |
| Spring compression conflict | contract: "~40 % compressed at 0 deg, ~75 % at 45 deg" on a 20 mm spring (= 8 and 15 mm); mechanical.md: 2 mm preload, 9.9 mm at 45 deg, solid height ~8.5 mm | cad/DESIGN_CONTRACT.md; docs/research/mechanical.md |
| Cam lift conflict | contract: cam lift 1.2 mm; Omron D2F-L hinge lever: FP 10 mm max, OP 6.8 +/- 1.5 mm, OT 0.55 mm min, OF 0.78 N max -> the click can sit anywhere 5.3-8.3 mm above the mounting face, so electronics.md asks the cam to press the lever to ~5 mm above the face, "up to ~5 mm of travel from a 10 mm free position" | cad/DESIGN_CONTRACT.md; docs/research/electronics.md; [Omron D2F datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2f.pdf) (fetched, text extracted) |
| DRV5032 supply / thresholds | VCC 1.65-5.5 V; FA/FB/FC versions BOP +/-1.5 min, +/-3 typ, +/-4.8 mT max; AJ 9.5 mT max; 20 Hz sampling (50 ms period typ, 75 max) for DU/FA/FC/AJ; FA push-pull omnipolar, FC open-drain omnipolar, DU unipolar push-pull | [TI DRV5032 datasheet](https://www.ti.com/lit/ds/symlink/drv5032.pdf) (fetched, text extracted): features list, Table "Device Comparison", section 6.5 |
| DRV5032 sensing axis | "sensitive to the magnetic field component that is perpendicular to the top of the package" (sec. 7.3.1); flux bottom-to-top is positive, "This condition exists when a south magnetic pole is near the top of the package" (same section, Figure 7-1 text) | same datasheet, sec. 7.3.1 |
| ScoutMakes/Adafruit DRV5032 breakout #6051 | $4.95; "1.65-V to 5.5-V supply"; 25.6 x 17.8 x 7.2 mm; JST PH 3-pin; variant, polarity and output type NOT stated on the page | [Adafruit 6051](https://www.adafruit.com/product/6051) |
| A3144 thresholds (for comparison) | Bop 350 G max at 25 C, 450 G over temperature; supply 4.5-24 V | docs/research/electronics.md (Allegro datasheet, not re-fetched) |
| 6 x 2 N35 field on axis | ~1450 G at 2 mm, ~880 G at 3 mm, ~560 G at 4 mm, ~373 G at 5 mm | docs/research/electronics.md and mechanical.md (computed from the Supermagnete formula / K&J calculator, not re-fetched) |
| KY-003-style A3144 module | A3144 unipolar; "4.5-24 V (5 V typical; 3.3 V is below rated spec)"; pins "-", middle "+", "S"; 680 ohm on board; power LED; 18.5 x 15 mm. Output goes LOW "when a magnet's south pole faces the marked side of the chip"; sensor mounting orientation (upright vs flat) not described | [arduinomodules.info KY-003](https://arduinomodules.info/ky-003-hall-magnetic-sensor-module/) |
| HiLetgo module B01NBE2XIR | title only: "HiLetgo 5pcs Hall Effect Magnetic Sensor Module 3144E A3144 ... DC 5V"; layout not retrievable | [Amazon B01NBE2XIR](https://www.amazon.com/dp/B01NBE2XIR) |
| RP2040 analogWrite | default PWM 1 kHz; analogWriteFreq 100 Hz-1 MHz; PWM "will continue until a digitalWrite or other digital output is performed" | [arduino-pico analog docs](https://arduino-pico.readthedocs.io/en/latest/analog.html) |
| Pololu U3V70F12 12 V step-up | $25.95; input 2.9-12 V; 12 V +/-4 %; input current up to 6 A prolonged, 7-8 A for seconds, 10 A cycle-by-cycle limit; 80-95 % efficiency; 40.6 x 15.2 x 4.6 mm. Output current at 5 V in: ~2.0-2.4 A (my calc from 6 A x eff x 5/12, not a page figure) | [Pololu 2895](https://www.pololu.com/product/2895) |
| Pololu D24V22F5 5 V step-down | $18.95; input 5.3-36 V; 5 V, 2.5 A typical max; 85-95 %; 17.8 x 17.8 x 8 mm; reverse-voltage protection and thermal shutdown | [Pololu 2858](https://www.pololu.com/product/2858) |
| 5 V -> 12 V cable limits (plan's primary) | B0CF5DR1JJ: 12 V 1.2 A max, "do not use for more than 14 watts"; HiLetgo B073R7Z7CL: 10 W max | docs/research/power.md (not re-fetched) |
| Pump power | 12 V, 0.7 A (Amazon bullet, per pump-and-plumbing.md); Kamoer's own parameter page lists the brushed KPHM200-SW/SV at "10W", 12 V/24 V, >= 200 mL/min -> 10 W / 0.85 / 5 V = 2.35 A at the bank (calc) | docs/research/pump-and-plumbing.md; [Kamoer KPHM200 params](https://www.kamoer.com/us/product/params.html?id=4001) (re-fetched) |
| 5 V budget during a pour | power.md: ~2.9 A (pump 2.0 A reflected + LEDs 50 %); with Kamoer's 10 W and the firmware's actual POURING levels: ~3.2 A (calc below) | docs/research/power.md; firmware animatePouring() |
| Firmware POURING LED current (calc) | strip 120-255 x 160/255 -> avg ~119/255 x 20 mA x 60 px = 0.56 A; ring ~0.25 A; XIAO 0.05 A; total LEDs+MCU ~0.85 A | firmware/green_lantern/green_lantern.ino `animatePouring`, `DEFAULT_MAX_BRIGHT` 160 |
| Firmware IDLE current (calc) | ring/strip values 3-8 after cap -> ~0.04 A lit + ~0.08 A dark-pixel quiescent + XIAO 0.05 = ~0.17 A | firmware `animateIdle`; power.md (1 mA/px dark, 50-200 mA bank auto-off threshold) |
| Pour math | 200 mL/min = 3.33 mL/s: 30 mL in 9.0 s, 44 mL in 13.2 s; robu's 260 mL/min: 44 mL in 10.2 s | docs/research/pump-and-plumbing.md |
| Ethanol flammable range | LEL 3.3 %, UEL 19 % by volume in air at 20 C | [Engineering ToolBox](https://www.engineeringtoolbox.com/explosive-concentration-limits-d_423.html) |
| Vetco Electronics | 12718 Northup Way, STE 100, Bellevue, WA 98005; 425-641-7275; Mon-Fri 9-6, Sat 10-3:30; resistors, electrolytic caps, fuses, wire, toggle/rocker/pushbutton switches; no mention of heat-set inserts or magnets | [vetco.net](https://vetco.net/) |
| Tacoma Screw Products (Seattle branches) | Ballard: 3930 Leary Way N.W., 98107 (Mon-Fri 7-5, Sat 9-1); Georgetown: 1121 S. Bailey Street, 98108; Kirkland: 11200 120th Avenue N.E., 98033; Kent: 22123 84th Avenue S., 98032; Everett: 11630 Airport Road, 98204 (branches Mon-Fri 7-5 unless noted) | [Tacoma Screw LocationFinder](https://www.tacomascrew.com/LocationFinder) |
| McLendon Hardware | White Center: 10210 16th Ave. SW, Seattle 98146 (Mon-Sat 8-8, Sun 9-7); Renton: 440 Rainier Ave. S, 98057 (Mon-Fri 7-8, Sat 8-8, Sun 9-7); Woodinville: 17705 130th Ave. NE, 98072; Kent: 23662 104th Ave. SE, 98031 | [mclendons.com/locations](https://www.mclendons.com/locations) |
| Sound Homebrew Supply | the domain is dead for homebrew purposes: soundhomebrew.com 301s to theapexautoworks.com, which 301s again to kwgearhydraulic.com and then to a spam page; do NOT list it | fetch chain of soundhomebrew.com (re-fetched) |
| Hand breadth | Male hand breadth: mean 9.04 cm, 5th 8.36, 50th 9.03, 95th 9.76 cm (N = 1774; population not named in the table). So ~84-98 mm across the knuckles; a claw grip on a 50 mm glass needing ~90-100 mm of clear width is still an estimate on top of that | [NC State Ergonomics Center anthropometric tables (PDF)](https://multisite.eos.ncsu.edu/www-ergocenter-ncsu-edu/wp-content/uploads/sites/18/2016/06/Anthropometric-Detailed-Data-Tables.pdf) (fetched, text extracted) |
| Silicone tube bend radius | NOT confirmed (unverified: Freelin-Wade 503, NewAge 404, Cole-Parmer 403 on the fact-check pass). Estimate: 1/4" OD, 1.6 mm wall silicone kinks below ~20-25 mm centreline radius | estimate (pump-and-plumbing.md also says ~25 mm, estimate) |

## Products to buy (only what this review adds or changes; everything else is in the sibling notes)

| Item | Exact product | Price | Link | Why |
|---|---|---|---|---|
| Hall sensor (make primary) | ScoutMakes DRV5032 Digital Magnetic Hall Effect Sensor breakout, JST PH 3-pin | $4.95 | [Adafruit 6051](https://www.adafruit.com/product/6051) | 3.3 V native, 10x more sensitive than A3144, senses perpendicular to the board so it lies flat under the rotor; variant (FA push-pull vs FC open-drain) is not on the page: firmware must work with either (INPUT_PULLUP is harmless for push-pull) |
| 12 V -> 5 V buck (for the PD-trigger architecture) | Pololu 5V, 2.5A Step-Down Voltage Regulator D24V22F5 | $18.95 | [Pololu 2858](https://www.pololu.com/product/2858) | Lets everything run from ONE 12 V PD port: pump direct, LEDs + XIAO via this buck; reverse-voltage protection, thermal shutdown |
| 12 V boost (fallback if the step-up cable sags) | Pololu 12V Step-Up Voltage Regulator U3V70F12 | $25.95 | [Pololu 2895](https://www.pololu.com/product/2895) | ~2 A at 12 V from a 5 V input (calc), 10 A cycle-by-cycle limit; needs the firmware soft-start and a 2200 uF cap or it will trip the bank's 3 A port on inrush |
| 12 V PD trigger cable + 12 V-PDO bank | wininks USB-C PD 12 V trigger to 5.5 x 2.1 mm, 3 ft (B0FD9P7PV4) + INIU B61 10,000 mAh 22.5 W (B09176JCKZ; PD 5 V/3 A, 9 V/2.22 A, 12 V/1.5 A, only one port at full power) | $9.97 / $20.69 (both per power.md; Amazon hides prices from the fetcher) | [B0FD9P7PV4](https://www.amazon.com/dp/B0FD9P7PV4), [B09176JCKZ](https://www.amazon.com/dp/B09176JCKZ), [techtest.org B61 PDO list](https://techtest.org/iniu-powerbank-klein-aber-stark-22-5w-10000mah/) | The alternative power architecture (issue 15); listings and the PDO list re-fetched |
| Reservoir (replace the Boston round) | squat wide-mouth PET jar no taller than ~60 mm so the cap stays below the door top at Z 88 when standing on the deck: 8 oz 89-400 ~89 x 50 mm or 4 oz 70-400 ~71 x 45 mm (estimates) (unverified: no specific listing was fetched) | not confirmed | [Amazon search](https://www.amazon.com/s?k=8+oz+clear+PET+plastic+jar+wide+mouth+70-400) | Fits inside the 100 mm base, refills through the door with a funnel; alt: the 8 oz food-grade pouch B0B8VQNJVR already in pump-and-plumbing.md (collapses, no vent) |
| Rigid nozzle tip | 304/316 stainless 1/8" hose-barb 90 deg elbow (unverified: no specific listing was fetched), or the straight MAACFLOW stainless 1/8" barb union, barb OD 0.16", pack of 2 (B0CFQJXTN6, re-fetched) set at 45 deg | not confirmed | [Amazon search](https://www.amazon.com/s?k=1%2F8+barb+elbow+stainless+steel+90+degree) | Turns the tube down into the glass in 15 mm instead of a 25 mm silicone bend (issue 4) |
| Prime button | any 12 mm panel-mount momentary pushbutton, NO | ~$1 local | Vetco (above) | Hidden inside the service door; hold = pump runs (issue 22) |
| Hall/switch line conditioning | 2 x 10 k resistors, 2 x 100 nF ceramic, 1 x 100 nF across the pump motor terminals | from the kits already listed | Vetco / resistor kit in electronics.md | Stops 800 kHz LED-data and brush noise from toggling a 50-80 k pulled-up GPIO on a 350 mm wire (issue 17) |
| 12 V rail cap | 2200 uF 16 V electrolytic (instead of 1000 uF) | ~$1 | Vetco | Pump inrush buffer on the boost output |

## Open questions / risks

- Kevin's printer model/bed size is still unknown (mechanical.md): decides whether 180 mm parts need splitting. Ask before freezing the split.
- Which DRV5032 variant is on the #6051 board (FA push-pull or FC open-drain) and its sensing face (board top vs bottom): test with the magnet before the hall_carrier is cut.
- Whether the HiLetgo A3144 module's sensor stands upright (face vertical) or lies flat: unconfirmed; if upright it cannot see an axial magnet and the leads must be re-bent.
- KPHM200 inrush current and the bank port's over-current behaviour: a 10 s bench pour with a USB meter and the full LED show decides issue 15.
- Hand breadth / hatch size: the anthropometric table gives 84-98 mm (5th-95th male) across the knuckles; the extra width a claw grip needs is still a guess. Print the rear sphere half first and try the reach with the real glass.
- Bottle vent vs tilt: no page covers it; the vent-tube fix is reasoning, not a tested spec.
- The jar and the 90 deg elbow are search links, not confirmed ASINs (unverified).

---

## Numbered issues

### A. Fluid system and reservoir

**1. BLOCKER - The reservoir cannot be installed, removed or refilled.**
What: a 57 x 133 mm Boston round (136 mm with cap, `BOTTLE_H`) stands on the base's deck (deck top Z 26) in a 100 mm tall base; its cap top sits at Z ~162, inside the lower dish cone with only 2.7 mm of radial margin (NOTES-base.md). The only access is the rear door at Z 12-88 (`DOOR_Z0/Z1`, base.py). A 136 mm bottle cannot be tilted out through a 76 mm tall opening while its top is captured in a cone that narrows upward, and the cap (with the tube through it) is unreachable for refilling.
Evidence: base.py `BOTTLE_X = -39.5`, `BOTTLE_Y = 0`, `DECK_TOP = 26`, `DOOR_Z0 = 12`, `DOOR_Z1 = 88`; params `BOTTLE_H = 136`; cad/NOTES-base.md "bottle top at Z 162 ... cap top (z 162) margin 2.7 mm"; BRIEF "250 mL reservoir bottle (vertical, protruding up into the hollow lower reflector)".
Fix: use a reservoir whose cap is below the door's top edge (Z 88). The bottle stands on the deck (Z 26), so that means a jar no taller than ~60 mm: a squat wide-mouth PET jar (e.g. 8 oz 89-400 "salve" jar ~89 dia x 50 tall, or a 4 oz 70-400 jar ~71 x 45; dims unverified, no listing fetched) refilled in place through the door with a funnel, or the 8 oz pouch from pump-and-plumbing.md laid flat. A 75-80 mm tall 8 oz jar on the deck puts its cap at Z ~101-106, above the door, so it only works if the deck is cut away so the jar stands on the floor beside the bank (NOTES-base.md says nothing fits beside the bank at floor level, so check that first). Keep the drilled-cap tube pass-through. If the Boston round is kept, the base must grow to ~150 mm or the bottle must come out through the top (remove the lower dish: 3 screws), which is not party-friendly.

**2. BLOCKER - The hatch is too narrow for a hand holding the glass.**
What: `HATCH_W` = 78 mm. The glass is 48-52 mm across the top; a claw grip from above adds a finger on each side, roughly 90-100 mm (estimate; the bare male hand is 84-98 mm across the knuckles, 5th-95th percentile, NC State table above). The reach is 90 mm into a dark sphere while the other hand holds a ~2 kg lantern by a handle on the sphere's equator.
Evidence: params `HATCH_W, HATCH_H = 78.0, 92.0`, `GLASS_D_TOP = 52`; BRIEF step 7 "He reaches into the lantern and pulls out the filled glass".
Fix: hatch >= 105 x 100 mm (the rear half has the room: flat-to-flat 117 mm, equator 180), AND make the glass cradle a tray that slides out through the hatch on two printed rails, pulled by a tab that is part of the hatch door (bottom-hinged door, the tray rides on it). The glass is then lifted straight up from a presented tray with no reach. This also keeps a spilled glass on the tray instead of in the sphere.

**3. MAJOR - One-handed ergonomics are not designed in.**
What: insert ring with hand A into a 77 mm deep dish at the top, twist, then open a magnet-latched hatch at the back with the same hand A while hand B holds the lantern by its handle (lantern CG below the equator, so it swings). The hatch cover is loose (magnets only) and will be dropped.
Evidence: contract "sphere_hatch cover with a 5 mm lip, 4 magnet pockets ... finger notch"; BRIEF handle "arch ... bosses on the sphere equator".
Fix: bottom-hinged hatch (two 3 mm pins) that stops at ~100 deg open and carries the tray (issue 2); state in the build guide that the ritual is performed with the lantern set on a table or hung on the forearm. Add a tether or hinge to the base door too.

**4. MAJOR - No room for the tube to turn down into the glass.**
What: free bay height is 263 - 183 = 80 mm; glass 62 + 12 mm nozzle gap puts the tube tip at 74 mm; a 6.4 mm OD tube arriving horizontally already reaches 80.4 mm, and a 180 deg U-bend in 1.6 mm-wall silicone needs ~20-25 mm radius (estimate) -> ~100 mm. It collides with the socket housing bottom.
Evidence: params `SOCKET_HOUSING_H = 30`, `GLASS_H = 62`, `TUBE_OD = 6.4`; NOTES-dishes `BAY_FLOOR_SEAT_Z = 183`, `Z_SOCKET_PLATE_SEAT = Z_SPHERE_TOP - 1`; contract "holds the tube end ... pointing down into the glass centre, tip 12 mm above the glass rim".
Fix: (a) nozzle at 45 deg aimed at the inside wall, entering from the rear-left wall at Z ~250, tip 8-10 mm above the rim (pump-and-plumbing already recommends aiming at the wall); (b) a rigid stainless elbow or a straight barb as the last 30 mm so the bend is in metal; (c) shorten the socket housing to ~18 mm by flattening the rotor (issue 10); (d) prefer the 54 mm Torque glass in params (`GLASS_H` 56). Add the tube bend envelope to checks.py.

**5. MAJOR - Vent hole = leak when the lantern tilts; vacuum lock if there is no vent.**
What: the plan drills a 2-3 mm open vent in the cap of a 250 mL bottle that will be nearly full and will be carried, swung and tilted. Liquid runs out of the vent onto the base floor, where the power bank and XIAO live.
Evidence: contract rev. 2 "24-410 cap (drilled: 6 mm tube hole + 2.5 mm vent)"; transcript "If using a rigid sealed bottle, provide a sanitary vent".
Fix: vent through a second 60-80 mm length of the same silicone tube pushed through the cap, running up to the top of the base (above the liquid level at any tilt up to ~60 deg); or use the collapsible pouch (no vent at all). Keep the electronics tray on 10 mm standoffs and give the bottle pocket a 5 mm lip (a cup, not a ring) so a cap leak stays in the pocket; base.py already has two 8 mm floor drains (`DRAIN_XY`) - keep them.

**6. MAJOR - Spill path from the glass bay to the electronics.**
What: the bay floor has a 7 mm tube grommet hole and a 14 x 8 mm wire slot and only a 2 mm lip. A 30-44 mL glass tipped by a careless reach drains through those holes into the lower dish and onto the base floor.
Evidence: contract bay_floor "raised 2 mm lip (drip tray) ... one `TUBE_GROMMET_D` hole at the rear-left ... 14 x 8 mm wire slot".
Fix: 8 mm lip; raise the grommet hole and wire slot on 10 mm chimneys; route the wires in a covered channel on the rear half's inner wall; the pull-out tray from issue 2 catches the glass's own spills.

**7. MINOR - Alcohol vapour in the base.**
What: a vented bottle of 35 % ABV in a ~2.4 L box with a brushed motor and a rocker switch. Ethanol LEL is 3.3 % v/v ([Engineering ToolBox](https://www.engineeringtoolbox.com/explosive-concentration-limits-d_423.html)); reaching it would take only ~0.15 g of ethanol vapour in a sealed 2.4 L base (calc), but the base is far from sealed (door gaps, 80 mm neck opening) and a 2.5 mm hole diffuses very slowly, so the real risk is low.
Fix: the vent tube from issue 5 ends in the lower dish (which opens into the sphere, which has the top vents from lighting.md), plus 3 x 2 x 15 mm slots low in the base wall. Don't seal the base. Odor from a drilled cap is unavoidable; a pouch is odor-tight.

**8. MINOR - Drips, siphon, kinks, cleaning.**
Drips: only the hanging drop at the open tube end; tray covers it. Siphon: bottle below the pump and the occluded head prevent it; but the storage advice "leave the tube out of the rollers" turns the system into an open siphon if the bottle is full and the lantern is laid on its side - say "empty bottle before releasing the head". Kinks: route the tube from the pump head (which faces the door) up the +X side of the lower dish with no bend tighter than 25 mm; the 80 mm neck hole and the bay-floor grommet must be offset so the tube passes vertically through both. Cleaning: the one-piece tube from bottle to nozzle cannot be removed without pulling it through two grommets; make the bay-floor grommet a slot with a snap cover so the tube lifts out.

### B. Socket module mechanics

**9. BLOCKER - Socket housing does not pass the dish floor hole.**
What: `SOCKET_HOUSING_OD` 92 and faceplate 100 vs `DISH_NECK_HOLE_D` 80. Already flagged in NOTES-dishes.md "Known issues" but not resolved in the contract.
Fix: housing OD 78 (ring recess 66.1 + 2 x 2.4 wall = 71; the switch and spring pocket can live inside r 39 if the switch is tangential at r 24-30), everything below the faceplate <= 79.4. Otherwise the module must be screwed to the dish from below before the dish is mounted (serviceable only by removing the upper dish: 3 screws + the J1 connector reachable through the hatch - acceptable but say so).

**10. BLOCKER - Rotor height vs Hall gap is geometrically impossible as written.**
What: the rotor is a 22 mm tall cup with the key pocket on top (3.5 deep) and a 1.2 mm floor, so the floor underside is ~4.7 mm below the top; the Hall sensor must sit 0.4 mm under that floor, i.e. INSIDE the hollow skirt, 17 mm above the skirt's bottom edge, while the skirt rotates 45 deg and carries the stop pin, cam and spring arm on its outside. A side slot for a 15 mm wide PCB plus 45 deg travel is an ~85 deg cut-out in the skirt.
Evidence: params `ROTOR_H = 22`, `ROTOR_FLOOR_T = 1.2`, `KEY_T = 3`; contract "hall_carrier slot directly under the rotor floor (PCB slides in from the side ... sensor face 0.4 mm below the rotor floor)".
Fix: rotor = solid disc ~10 mm tall (pocket 3.5 + floor 1.2 + 5 mm body) with the cam lobe, stop pin and spring arm on its rim; Hall carrier is a flat shelf directly under the disc; housing height then ~18 mm, which also helps issue 4. Magnet-to-element distance becomes 1.2 + 0.4 + 0.5 = 2.1 mm (plus the 0.6 mm key-cap skin if the magnet is pocketed from the top; pocket it from the underside as the contract says).

**11. MAJOR - Cam lift 1.2 mm cannot operate a D2F-L hinge lever.**
What: the lever's free position is up to 10 mm above the mounting face and it operates at 6.8 +/- 1.5 mm (Omron D2F datasheet, confirmed: FP max 10 mm, OP 6.8 +/- 1.5 mm, OT min 0.55 mm): 1.2 mm of lift works only if the switch is pre-positioned within 1.2 mm of its operate point, which the +/-1.5 mm OP tolerance makes a per-switch fiddle, and leaves no overtravel.
Evidence: contract "cam lobe (ramps from 30 deg, full lift at 40 deg; lift 1.2 mm over the skirt OD)" vs electronics.md "Design the cam to press the lever down to about 5 mm above the mounting face (up to ~5 mm of travel from a 10 mm free position)".
Fix: cam lift 4-5 mm, ramp from 20 to 38 deg (at r 22 that is ~7 mm of arc for 4-5 mm lift, ~35 deg ramp), symmetric ramps so the spring return does not snag the lever tip; lever oriented so the cam approaches from the free end toward the hinge; slotted mount (already planned) for +/-2 mm.

**12. MAJOR - Spring numbers in the contract go solid before 45 deg.**
What: "~40 % compressed at 0 deg, ~75 % at 45 deg" on a 20 mm free-length spring is 8 mm and 15 mm of compression; solid height of a 0.5 x 5 x 20 spring is ~8.5 mm (mechanical.md), so it is solid 4 mm before the stop. It also implies 7 mm of travel at the arm, which at r 10 is 40 deg, not 45.
Evidence: contract Socket module bullet; mechanical.md spring section.
Fix: use mechanical.md: arm radius 10 mm, 7.9 mm travel, 2 mm preload (18 mm installed), 9.9 mm compressed at 45 deg (10.1 mm installed), pocket 5.6 wide x 21 deep with closed ends; buy both 0.4 and 0.5 mm wire and pick by feel. Add a 0-deg magnet detent pair at the rim (>= 25 mm from the Hall) for the "click".

**13. MINOR - Torque path through a glued 3 mm key cap, and the ring slipping on the finger.**
What: 2-5 N.cm at a 6 x 4 mm tab = ~4 N on the tab, fine for PETG; the CA joint on a 24 mm disc sees <0.1 MPa, fine. The weak point is the ring rotating on the finger before the rotor moves.
Fix: keep spring torque at the low end (0.4 mm wire first), use the magnet detent for the "click" feel, and tell the user to twist with the thumb against the ring band. Make the key-cap tab a trapezoid (wider at the root) and the rotor pocket 4 mm deep so the tab, not the glue line, carries the torque. Engagement 3 mm is enough; do not deepen the pocket (ring must pull out at any angle, per the tech spec).

**14. MINOR - Hard stops, retention, wear.**
The 4 x 4 mm printed stop pin in a 45 deg arc slot takes every twist; mechanical.md's M3-screw-in-insert pin is better and replaceable. The arc-slot "loading gap at 90 deg" retains the rotor axially only while the spring arm blocks 90 deg; if the spring is removed for service the rotor falls out - acceptable, document it. Put a trace of silicone grease on the bore; PETG-on-PETG dry squeaks after a few hundred cycles (estimate). Rotor pocket floor: the ring face rests on the rotor top, so the 3.5 mm pocket depth is fine.

### C. Electrical and power

**15. MAJOR - The 5 V-only power path is within a few percent of the bank's port limit during a pour.**
What: pump 10 W (Kamoer) through a boost at ~85 % = 2.35 A at 5 V, plus the firmware's POURING light show ~0.85 A (calc from `animatePouring` at `maxBright` 160) = ~3.2 A on a 3 A port; motor inrush on top. The chosen step-up cable is rated 1.2 A / 14 W (B0CF5DR1JJ) or 10 W (HiLetgo), i.e. at or below the pump's running power. lighting.md budgeted the LEDs against a bank port that does NOT also carry the pump; power.md later moved the pump onto the same port and asked for a 50 % LED cap during pouring, which the firmware does not implement separately from the global cap.
Evidence: power.md current table ("~2.9 A ... bank port limit 3 A"); lighting.md "Budget assumption: one 5 V / 2.4-3 A bank port for XIAO + LEDs; pump on the separate 12 V PD-trigger port"; firmware `DEFAULT_MAX_BRIGHT = 160`.
Fix (in order): (1) bench-test first: real pump current at 12 V with Jagermeister-viscosity liquid, then a full pour with the LED show and a USB meter on the bank; (2) add a `POUR_BRIGHT` cap (~100) in firmware; (3) if the bank trips or the cable sags, go to ONE USB-C PD port at 12 V (bank with a 12 V PDO such as the INIU B61 in power.md + the wininks 12 V trigger cable) -> pump direct through the D4184, and a Pololu D24V22F5 buck for the 5 V bus: 18 W budget, no boost, no reflected inrush; (4) the Pololu U3V70F12 is the stronger boost if the 5 V-only topology must stay, with a 2200 uF cap and the soft-start (its 10 A cycle limit will otherwise trip the bank).

**16. MAJOR - Idle current may be below the bank's auto-off threshold.**
What: firmware IDLE draws ~0.17 A (calc); power.md says banks cut off at 50-200 mA and planned a ~0.25 A pilot glow, which the firmware's `animateIdle` (values 3-8 after the cap) does not deliver. The bank's button is inside the base.
Fix: ring pilot at ~25 % green (24 x 20 mA x 0.25 = 0.12 A) in IDLE, verify >= 0.3 A total with a meter; enable Anker trickle mode as backup; make the bank's button reachable through the door (base.py has no button access feature).

**17. MAJOR - High-impedance Hall and switch lines run 350 mm next to two 800 kHz LED data lines.**
What: D1 and D2 rely on the RP2040's 50-80 k internal pull-ups (electronics.md), through a diode for the A3144. That is a 50-80 k source impedance on a long unshielded wire bundled with NeoPixel data and 5 V; false "ring present" or "switch" edges are plausible. The firmware's 100 ms / 40 ms debounce helps but a 1 kHz burst of coupled edges resets the debounce timer continuously (`hallChanged = now` on every raw edge), which can hold `hallStable` false during a pour -> spurious abort.
Fix: 10 k external pull-ups to 3.3 V at the XIAO on D1 and D2, 100 nF to GND at the pin (0.1 ms RC), 100 nF across the pump motor terminals, pump wires twisted and kept in the base; in firmware, debounce with a counter/majority filter rather than "time since last edge".

**18. MINOR - Fuses and level shifting.**
The T3A fuse on a 3 A-limited USB port never opens before the bank's own protection; keep it only as wiring-short insurance or drop it. The T1A on the 12 V leg sees 2-3 A inrush for 0.1-0.3 s; a T-type survives that, an F-type will not - specify T. AHCT125 for both data lines and the D4184 trigger is correct (WS2812B VIH 0.7 Vdd). D4184 "dual" module: use one channel, tie the other's TRIG to GND. The XIAO 5V-pin series 1N5819 is correct; note it also makes "USB plugged in while master ON" safe (the diode blocks back-feed), so the "USB only with master OFF" rule is for the bank's benefit (no pass-through), not the XIAO's.

### D. Printing, assembly, structure

**19. RESOLVED (was listed as MAJOR) - Pump orientation: base.py already follows the contract.**
What: the current base.py lies the KPHM200 with its motor axis along Y on a deck (deck top Z 26, pump axis Z 57.5, pump top Z 89, under the 92 mm dish-spigot zone), head face at Y 52 toward the rear door "so the tube can be loaded through the door without removing the pump" - exactly what contract rev. 2 asks. cad/NOTES-base.md exists and documents the deck, the saddles and the clearances. An earlier draft of this review described a vertical pump at (56, -22) reaching Z 120; that is not what the code does.
Residual: `PUMP_HEAD_L_EST` = 40 mm is an estimate (NOTES-base.md "Known issues"); if the real head is longer than ~46 mm the motor saddle must move toward -Y. Measure the pump before printing the deck.

**20. MINOR - Handle boss vs sphere flange screw collision; hanging tilt.**
Handle bosses at +/-X on the equator (rear half, 6 mm behind the split) and the sphere flange screws "at the equator sides + top/bottom" occupy the same spot; move the flange screws to +/-45 deg. Bosses 6 mm behind the split plane tilt the hanging lantern ~2 deg (calc) - ignore. A 2.2 kg lantern (PETG ~1.1 kg + pump 0.30 + bank 0.21 + full bottle 0.28 + glass, wires, LEDs; estimate) hangs on two M3 screws in inserts in 14 x 10 bosses: make the bosses 25 x 20 x 15 mm blocks fused to the shell with 100 % infill, and put the lap joint of the arch 30-40 mm from a boss (mechanical.md).

**21. MINOR - Upper dish / socket serviceability and wire route.**
Socket module is serviced from above (4 screws) only if the J1 connector can be unplugged: put J1 on a 150 mm pigtail reachable through the hatch, or mount J1 on the socket housing's underside facing the hatch. Wires from the base pass the glass bay: use a covered channel on the rear half's inner wall (also fixes issue 6). Sphere halves: print split-plane down; the window and hatch become roof holes in that orientation, so no supports are needed there - only the internal window ledge ring overhangs; chamfer it 45 deg. Bed: still blocked on Kevin's printer model (mechanical.md).

### E. Firmware

**22. MAJOR - No way to prime or purge at the party.**
What: priming after a bottle swap needs the serial `cal` command (laptop) or ring-insert-twist cycles (9-10 s each into a glass). pump-and-plumbing.md says "hold a service button" - no such button exists in the firmware or CAD.
Fix: `PRIME_PIN = D6` (INPUT_PULLUP, momentary button inside the service door): while held and state is IDLE or LOCKED, run the pump at full duty, capped by `MAX_PUMP_MS`; LEDs dim blue so it is obviously a service mode. Add a panel hole in base_door.

**23. MINOR - Ring-removal abort is delayed up to 200 ms, and the Hall debounce is edge-retriggered.**
`readInputs()` requires `RING_GONE_MS` (200) of continuous absence before `hallStable` drops; the spec says "immediately". Scenario n in the test harness documents a <200 ms dropout being ignored mid-pour (good for noise), but with 3.3 mL/s that is 0.7 mL - fine. The bigger problem is issue 17's edge-retrigger. Fix: abort POURING on `hallRaw` absent for >= 30 ms (separate short filter), keep 200 ms for the LOCKED -> IDLE reset.

**24. MINOR - Firmware vs documents.**
`MAX_PUMP_MS` 20 s vs pump-and-plumbing "hard max 15 s" (pick 15 s: 20 s = 66 mL, more than a 1.5 oz glass holds). `DEFAULT_POUR_MS` 10000 vs 30 mL = 9000. Ring removed mid-pour goes to IDLE, BRIEF/tech spec say LOCKED - functionally identical since LOCKED exits on ring removal anyway, but lighting.md's "3 red blinks" abort cue is not implemented; add it. lighting.md's single chain (strip then ring on D4) vs firmware's two pins (D4 ring, D5 strip): firmware/electronics.md win; update lighting.md. `pumpStop()` after `analogWrite` uses `digitalWrite` - correct per arduino-pico docs ("PWM will continue until a digitalWrite ... is performed"). millis() wrap: `since()` is wrap-safe and tested (scenario j); `tri()` and the comet index glitch one frame at wrap - harmless. show() blocking: 84 px ~2.5 ms per loop at ~100 Hz - fine.

**25. MINOR - Transcript sketch bugs (for the record; the repo sketch already fixes these).**
No max-runtime cap; `setGreen()` calls `show()` inside the state machine every loop (blocking); `ring` (raw) used for the abort while `ringStable` is used to arm (a 1-sample glitch aborts a pour); LOCKED entry `state = ring ? LOCKED : IDLE` uses the raw read; no one-pour-per-insertion flag (a held switch re-fires after LOCKED -> IDLE -> ARMED if the ring is re-seen); switch pressed at boot with the ring in fires immediately; 12-px ring hard-coded; `now - stateStarted` is wrap-safe but `(now / 6) % 400` is not an issue. None of these need action.

### F. Owner's questions that were never answered in the transcript (now answered in the sibling notes)

- LED brightness/power: lighting.md + power.md answer it, but their budgets contradict (issue 15); the final answer is "60/m strip + 24-px ring, ~1.6 A full green, cap during pour".
- Power bank: power.md answers (Anker 313 A1229, 5 V/3 A revision, trickle mode) - subject to issue 15/16.
- Spring size: mechanical.md answers (0.4-0.5 x 5 x 20 compression; torsion alternate) - subject to issue 12.
- Seattle stores: now confirmed above (Vetco Bellevue; Tacoma Screw Ballard/Georgetown/Kirkland/Kent; McLendon White Center/Renton/Woodinville/Kent). Sound Homebrew Supply is gone; a homebrew-shop tubing source is still unconfirmed - the AUBER 10 ft on Amazon is the practical answer.
- Missing supplies: see checklist below.

## Design decisions to change in the BRIEF

1. Reservoir: "squat wide-mouth PET jar (<= ~60 mm tall on the deck, cap below Z 88) or 8 oz pouch, entirely inside the base, refilled through the rear door; vented by tube" replaces "250 mL bottle protruding up into the lower reflector".
2. Sphere: "rear hatch >= 105 x 100 mm, bottom-hinged door carrying a pull-out glass tray" replaces "hatch (magnet-latched) to reach in and grab the glass".
3. Socket: "housing OD <= 78 mm, rotor a ~10 mm disc, Hall sensor on a shelf directly under it, cam lift 4-5 mm, D2F-L at 38 deg, stop at 45" replaces the "rotating keyed rotor (OD ~44)" line; Hall primary = DRV5032 #6051, A3144 alternate.
4. Nozzle: "45 deg approach from the bay wall, rigid stainless tip, 8-10 mm above the rim" replaces "nozzle holder above the glass".
5. Power: keep the single-port 5 V design as the first thing to bench-test, but write the 12 V-PDO + buck architecture into the BRIEF as the approved fallback with its parts (INIU B61 + wininks trigger + Pololu D24V22F5).
6. Pump orientation: no change needed; base.py already mounts it horizontally on a deck, head to the door (contract rev. 2).
7. Firmware: add PRIME button, POUR brightness cap, idle pilot >= 0.3 A, 30 ms raw-Hall abort, `MAX_PUMP_MS` 15 s.
8. Serving: 30 mL (9 s) in a 1.5 oz glass is the default; 44 mL (13 s) is allowed only with a 2 oz glass and a taller bay - the "~10 s" show length is a firmware constant, not a pump constraint.

## Missing supplies checklist (not on the shortlist, not clearly in the sibling BOMs)

- [ ] DRV5032 breakout (Adafruit 6051) - primary Hall sensor
- [ ] Momentary pushbutton for PRIME (12 mm panel mount), plus a 20 x 12 or 19 x 13 rocker for master power
- [ ] 2 x 10 k pull-ups, 3 x 100 nF ceramic (D1, D2, motor), 10 k pull-down on D3, 2 x 330-470 R data resistors
- [ ] 3 x 1N5819 (pump flyback, XIAO 5V feed, A3144 interface if used)
- [ ] 1000 uF 10 V (5 V bus) and 2200 uF 16 V (12 V rail) electrolytics
- [ ] 5 x 20 mm fuse holders + T3A and T1A slow-blow fuses
- [ ] 5 V -> 12 V source: step-up cable (B0CF5DR1JJ) now, OR INIU B61 + wininks 12 V trigger + Pololu D24V22F5 buck, OR Pololu U3V70F12
- [ ] USB-A pigtail (bank 5 V out) and a panel-mount USB-C extension for charging through the door
- [ ] JST-XH 5/3/2-pin connector kit, 22 AWG silicone wire (red/black) + 26 AWG (signal), heat-shrink
- [ ] 5 x 7 cm perfboard, 2 x 1x7 female headers, DIP-14 socket
- [ ] AUBER 1/8" x 1/4" platinum silicone tube, 10 ft (pump head + inlet + outlet + vent tube)
- [ ] Rigid nozzle tip (stainless 1/8" barb, straight or elbow) and a tube pinch clamp
- [ ] Reservoir: squat wide-mouth PET jar (<= ~60 mm tall) + spare caps (drill 6.5 mm tube hole + 6.5 mm vent-tube hole), or 8 oz pouches
- [ ] Shot glass: Libbey 92440 Torque 1.5 oz Tritan (or Libbey 5120 glass)
- [ ] Return springs: Mardatt 240-pc compression kit (0.4 and 0.5 x 5 x 20) or uxcell 0.4 x 5 x 20
- [ ] M3 heat-set inserts (ruthex 5.7 mm), M3 x 8/10/12 socket screws, 2 x M2 x 8 + nuts for the D2F-L
- [ ] 3 mm steel or printed alignment pins; 2 x 3 mm hinge pins for the hatch door
- [ ] 20 mm hook-and-loop strap (pump/bank), cable ties 3.6 mm, silicone grease
- [ ] White/natural PETG for the diffuser, LED carrier and bay tray; CA glue + activator; 5-minute epoxy
- [ ] Local: Vetco (Bellevue) for resistors/caps/fuses/switches/wire; Tacoma Screw Ballard or Georgetown for M3 hardware and springs; McLendon White Center for the Everbilt/Hillman spring assortment, funnel, grease

## Fact-check notes (2026-10-11, independent pass)

Re-fetched and confirmed as written: TI DRV5032 datasheet (VCC 1.65-5.5 V; F-series BOP +/-1.5/+/-3/+/-4.8 mT; AJ 9.5 mT; 20 Hz
sampling 13.3-20-37 Hz = 27/50/75 ms; FA push-pull omnipolar, FC open-drain omnipolar, DU unipolar push-pull; sec. 7.3.1 sensing axis);
Adafruit 6051 ($4.95, 1.65-5.5 V, 25.6 x 17.8 x 7.2 mm, JST PH 3-pin, variant/polarity not stated); arduinomodules.info KY-003 (4.5-24 V,
3.3 V below spec, pins -/+/S, 680 ohm, LED, 18.5 x 15 mm); arduino-pico analog docs (1 kHz default, 100 Hz-1 MHz, PWM continues until a
digitalWrite); Pololu 2895 ($25.95, 2.9-12 V in, 12 V +/-4 %, 6 A prolonged / 7 A seconds / 10 A cycle-by-cycle, 80-95 %, 40.6 x 15.2 x 4.6 mm);
Pololu 2858 ($18.95, 5.3-36 V in, 2.5 A typ, 85-95 %, 17.8 x 17.8 x 8 mm, reverse-voltage protection, thermal shutdown); Engineering ToolBox
(ethanol LEL 3.3 %, UEL 19 %, 20 C); Vetco (address, phone, hours, categories); Tacoma Screw (all five addresses); McLendon (all four
addresses and the White Center / Renton hours); soundhomebrew.com redirect chain; Amazon B01NBE2XIR, B0FD9P7PV4, B09176JCKZ, B0CFQJXTN6,
B0B8VQNJVR, B09C1DDHRV, B076LZZQPW, B08BCRZZS3, B0DKB1NKB4, B0CF5DR1JJ, B073R7Z7CL, B0D5CLSMFB (titles match; Amazon shows no prices or
availability to the fetcher, so every Amazon price in this file is from the sibling notes); Omron D2F datasheet (D2F-L: OF 0.78 N, RF 0.05 N,
OT 0.55 mm, MD 0.5 mm, FP 10 mm max, OP 6.8 +/-1.5 mm); Kamoer KPHM200 parameter page (brushed SW/SV: 10 W, 12/24 V, >= 200 mL/min);
techtest.org INIU B61 PDO list (12 V/1.5 A; one port at full power). Repo values re-read from params.py, base.py, NOTES-dishes.md,
NOTES-base.md, DESIGN_CONTRACT.md, the firmware and the sibling notes: stack heights, 80 mm bay height, hatch 78 x 92 at Z 181.5-273.5,
socket OD 92 / plate 100 / hole 80, rotor 22 / floor 1.2, cam lift 1.2, 40 %/75 % spring, mechanical.md 2 mm / 9.9 mm / 8.5 mm solid,
firmware constants (maxBright 160, idle 6-13 -> 3-8 after the cap, pouring 120-255 strip / 140-225 ring, HALL 100 ms, SWITCH 40 ms,
RING_GONE 200 ms, MAX_PUMP 20 s, POUR 10 s) and test scenarios j and n.

Corrected:
- Issue 19 and the "pump orientation conflict" row: the current base.py mounts the pump HORIZONTALLY on a deck (axis Z 57.5, head toward
  the door), matching contract rev. 2, and cad/NOTES-base.md exists. The vertical-pump claim and the "NOTES-base.md does not exist" claim
  were wrong; issue 19 is now marked resolved and the decisions list no longer asks for that change.
- Bottle position: base.py puts it on the deck at (-39.5, 0), not at (-33, -15); its cap top is at Z ~162 (deck top 26 + 136), not ~138.
  This makes issue 1 worse, not better (the cap is deeper inside the lower-dish cone), and it also invalidates the original fix: a
  75-80 mm jar on the deck would still top out above the door (Z 88), so the jar must be <= ~60 mm tall or stand on the floor.
- Issue cross-references in the short list and product table were renumbered to match the numbered sections.
- Cam lift: electronics.md no longer says "~3.5 mm"; it asks for up to ~5 mm of travel (press to ~5 mm above the mounting face). The
  recommendation is now 4-5 mm everywhere in this file.
- DRV5032 polarity sentence is in sec. 7.3.1 (not 8.3). 6 x 2 N35 field at 3 mm / 5 mm now quoted as ~880 G / ~373 G to match the
  sibling notes.
- Hand breadth now has a source (NC State table: male 5th-95th 8.36-9.76 cm); the 90-100 mm claw-grip width remains an estimate.
- Pump 10 W is now sourced to the Kamoer parameter page (re-fetched) instead of only pump-and-plumbing.md.

Still unverified: silicone tube minimum bend radius (three vendor pages blocked); the 8 oz wide-mouth jar and the 90 deg stainless elbow
(search links only); Amazon prices and the "Currently unavailable" status of B0CF5DR1JJ (taken from power.md); the HiLetgo A3144 module's
sensor orientation; which DRV5032 variant is on the #6051 board; KPHM200 inrush current; the bottle-vent-vs-tilt reasoning.
