# Project context: decisions, reasons and open items

Written on 2026-10-13 at the end of the design sessions and kept current since (see the Change log at the end),
for anyone, person or Claude session, picking up this project. It condenses about
100 messages between Kevin (the owner) and Claude, plus 9 CAD revisions. **Read this before changing anything.**
Each decision here was made on purpose, usually by Kevin. Don't reverse one unless you've found a concrete defect,
and even then, ask Kevin first (see the review prompt).

The original brief and ChatGPT plan are in `docs/research/BRIEF.md` and `docs/research/chatgpt-transcript.md`.
Revision history is in `cad/DESIGN_CONTRACT.md` (revisions 2-9g). The repository is
`TheRageKage12/drunk-lantern-power-battery` (renamed from `temprepo` on 2026-10-14).

---

## 1. The project

- **What it is:** a Halloween party prop. It's a 3D-printed Green Lantern power battery (lantern) that secretly
  pours a shot while Kevin recites the oath with his ring in the lock.
- **Size:** about 47 cm tall, 19 cm across at the base.
- **Based on:** Hedo3D's "Green Lantern luminous" (CC BY-NC 4.0, in `original-model/`), scaled up and hollowed
  for the hardware.
- **Team:** Kevin (owner, wears the ring), Sky and Duncan.
- **Deadline:** Halloween 2026. Written on 2026-10-13. Every part has to arrive in time to print, build and test.
  Amazon items show Prime delivery Oct 14-15. The filament is the slowest at Oct 18.
- **Status:** designed, modelled and simulated, not built. Nothing has been measured yet. As of the last message,
  Kevin had not confirmed any order. Ask before assuming anything has been bought.
- **Printer:** Kevin's heavily modified Ender 3, 230 x 230 x 240 mm bed. Every part must fit, and the build checks
  this.
- **Location:** Seattle, so local stores are in the Seattle area (see the shopping list).

## 2. Kevin's preferences (follow these)

**Communication**
- Concise answers. He got frustrated with ChatGPT's long essays and its habit of dropping links.

**Links and stores**
- Prefer Amazon. Every link must go to the exact product (`amazon.com/dp/<ASIN>`), **never a search page**.
- Check each listing's delivery date. It must arrive **before Halloween**, ideally with Prime.
- **No Adafruit.** It ships too slowly.
- **No Jameco.** It was too late for the Hall sensor.
- For small parts sold in huge packs (screws, valves, springs), find a local store that sells a few:
  - Vetco Electronics (Bellevue) for electronics.
  - Tacoma Screw (Ballard) for screws, by the piece.
  - Ace Hardware for the spring.
- Jar, shot glass and curtain sheet: Kevin buys these locally and measures them in the store.
- Kevin already owns Gorilla Glue super glue. Don't add glue to the list.

**Cost**
- Cost matters. The ChatGPT plan was about $100. An early draft of ours hit about $350, and Kevin was unhappy
  about it.
- He accepted about $135-140. The changes that followed (battery pack, wider base, A3144 post, local items)
  brought it to **about $186-190**, which he has accepted. Show any cost increase explicitly and get approval.
- If a part or material has no good match, think of alternatives and **ask Kevin**. Don't quietly substitute.

**Git**
- Use **a new branch for each feature or piece of work**, then open a PR to merge it.
- Check a PR's state before pushing to it or saying it's ready. Earlier sessions twice pushed to, or described as
  open, PRs that were already merged.
- Every PR so far (#1-#9) is merged into `main`.
- Any PR that changes a decision, part, quantity, price or dimension also updates this file and its Change
  log. Refresh `transcript.md` at the end of a working session, not on every push.

**Repo content**
- No model identifiers in commits, docs or code.
- Commits carry the session's attribution lines.

## 3. How the show works (Kevin's own spec; don't change it)

1. Push the empty shot glass in under the lock until it clicks.
2. **Punch in horizontally**, fist first, ring face forward, through a strip curtain on Kevin's side of the sphere.
   The ring is on the **left hand**. The Hall sensor sees the ring's magnet, and the light fades up to ~15 %.
3. **Twist 45° counterclockwise and hold.** Counterclockwise puts the hand in a better position to grab the
   glass. A cam clicks the microswitch, then:
   - the pump starts, about 1 oz in ~11 s (a bit under a full shot is fine)
   - the light climbs to ~90 % over the same time. This is the distraction while it pours.
4. Turn back (a spring returns the rotor). The light swells to 100 % and goes dark.
5. Grip the glass, slide it ~3 cm toward you, lift it out and bring it out through the curtain.

- **Letting go early** stops the pump where it is. The light bumps ~10 %, then goes dark.
- The pump runs only while the ring is in AND the twist is held, and only once per insertion.
- The light should only **gradually increase in intensity**. No other light effects.
- Kevin's fist is under 4" wide x 3" tall. The model uses a 106 x 76 mm envelope through a 120 x 96 mm opening.
  Kevin said not to worry much about how far off-centre his fist is.

## 4. Decision log (current state; the latest decision wins)

### Pump and fluid path
- **Pump: Kamoer KPHM200 12 V peristaltic (B09HGVLHFV), one pump.**
  - Rejected: two cheaper Adafruit 5 V pumps. They would barely make the 10-15 s window, need two tubes, and come
    from Adafruit.
  - Kamoer publishes no drawing, so the CAD envelope is an estimate (64 x 63 x 40 head plus a 40 mm motor can,
    118 mm long). **Measure it when it arrives.** There is about 6 mm of clearance.
- **Tube: 1/8" ID x 1/4" OD platinum silicone, Auber 10 ft (B0DKB1NKB4).** Kevin asked if 3 ft would do. The
  10 ft listing was kept because the size is exact and it's cheap; the build uses well under 3 ft.
- **Reservoir: squat food-safe jar,** at most 73 mm across including the lid, at most 76 mm tall. It sits on the
  cartridge deck. Bought locally (Micro Homebrew, Kenmore).
- **Jar vent: a one-way aquarium check valve** in a second 6 mm hole in the lid, arrow pointing into the jar.
  - It replaced a 2.5 mm open hole after Kevin raised the leak risk.
  - The pickup tube can't leak because the pump's rollers pinch it shut.
  - Listing: AQUANEAT 10-pack (B086JRH4WS), only 1 is used. A pet store's aquarium aisle also has them.
- **Nozzle (rev 9c):**
  - The guide bends the tube **135°**, so the tip points 45° down and sits 6.7 mm above the rim, hidden behind the
    lock wall over the back third of the glass.
  - It replaced a 90° bend that threw the stream onto the rim. The stream lands about 19 mm from the glass centre
    at any pump speed.
- **Cleaning:** run warm water, then air, with `cal 8000`. Keep each run short: `cal 20000` would overflow the
  glass.

### Lock (socket)
- Flat 36 mm rotor with a keyed ring pocket:
  - hard stops at 0° and 45°
  - a cam that lifts a D2F-01L lever microswitch 3 mm (verify the purchased switch fits the existing bracket)
  - a radial spring plunger that returns the rotor
  - a 6 x 2 mm magnet in a printed key cap glued to the ring
- Mirrored for **counterclockwise** (`LOCK_TWIST = 'ccw'`).
- Kevin asked if it could be simpler. The decision was to **keep it as is**.
- **Spring:** about 0.4-0.5 mm wire, 5 mm OD (fits a 5.6 mm pocket), ~10 mm long. Buy one from Ace's Hillman
  drawer. A pen spring works as a fallback but is about a third as stiff, so check the snap-back.
- **Hall sensor (rev 9d): A3144** (Vetco, $1.99). It replaced the DRV5032 board, which couldn't be sourced in time.
  - The A3144 lies face up in a pocket on a **post** on `socket_base`, reaching up into a blind hole in the
    rotor. That puts it ~3 mm from the magnet: about 88 mT from an N35 magnet, against a worst-case operate
    point of 35 mT.
  - The post top is set by the rotor's 1.2 mm axial play. `tests/test_socket.py` pushes the rotor down and
    checks it doesn't hit the post.
  - Rejected: "stack two magnets". It doesn't fit.
  - The A3144 has one pole: if the ring isn't detected, flip the magnet.
  - The DRV5032 stays documented as a "not recommended" fallback (Kevin, 2026-10-13).
  - The spring return is marginal by calculation (self-locking when dry, slow when greased): accepted; grease it,
    and the hand turns the ring back anyway (Kevin, 2026-10-13). A steeper ramp needs a longer spring and a
    housing reprint; see PROGRESS.md.
  - Wiring (electrical revision): VCC directly on regulated 5 V; local 0.1 µF bypass to ground.
    Open-collector OUT directly to D1, with 4.7 kΩ to XIAO 3V3. No series Hall diode or 5 V pull-up.
- `socket_base` prints **bottom-down**, so the post isn't printed upside down.

### Layout (rev 8, the lock-wall layout)
- The sphere has two openings:
  - the **hand opening** (120 x 96 mm) on Kevin's side, closed by a frosted polypropylene strip curtain
  - the **display window** on the far side
- The **lock wall** stands 2.5 cm past the sphere centre, toward the display window. It carries:
  - on its face (toward Kevin): the lock, plus a column of LEDs on each side
  - behind it (hidden): the nozzle and 4 rows of LEDs facing the window
- The glass sits in a slot under the lock and hangs into the lower dish neck. A 1.5 mm ridge clicks it into place.
  It slides out toward Kevin, then lifts.
- **Light balance:** Kevin wanted the two sides roughly even, then decided to **keep it as is**. The display side
  is brighter. If needed later, a separately dimmable channel needs only one MOSFET plus firmware, no reprint.
- Curtain: one letter-size **polypropylene** binder divider or report cover, 0.3-0.5 mm, cut into 13 strips.
  - Bought locally: Target, Fred Meyer, Office Depot.
  - Not PVC or vinyl, which crack.
  - The Amazon option (B0FM41G21X) arrives after Halloween. Home Depot has nothing suitable.

### Base (rev 9, cartridge; rev 9f, 190 mm)
- Kevin's requirement for refills in the field: undo hidden thumbscrews, lift the lantern off, unplug the cable and
  the tube, fill the jar, then reverse. **Everything electrical and fluid stays on the cartridge.**
- The cartridge holds:
  - the battery flat on the tray floor
  - a deck above it with the jar ring, the pump saddles and the electronics board
  - the buck converter beside the pack
- Three printed knurled knobs grip M3 screws into nuts trapped in the drum. The cable to the sphere has plugs:
  - JST PH 4-pin for the lock
  - JST SM 2-pin for the LEDs
- Thread the cables through the 7 mm bay-floor hole **before** fitting the plug housings.
- **Wider base: the base and lower dish are 190 mm (`D_MAX`), widened from 180 mm.**
  - Kevin asked for this ("expand by 5-10 mm") to fix tight clearances after the 40 mm-thick battery raised the
    deck. Those clearances were 0.5 mm at the jar and 1 mm at the pump.
  - The upper dish stays 180 mm (`UPPER_DISH_MOUTH_D`) with its own cone. At 190 mm, the handle arcs touched it
    from the side, and raising the handle didn't help.
  - `DECK_GAP = 2` keeps the pack held down.

### Power (the latest decision wins; this changed several times)
- History:
  1. INIU power bank plus Adafruit PD trigger cable
  2. VEGER bank plus AITRIP 12 V trigger board
  3. A friend's suggestion: a bare-lead battery pack
  4. KBT 12 V 1200 mAh (70 x 55 x 20 mm)
  5. KBT 12 V 2400 mAh (superseded by the electrical review)
  6. **TalentCell YB1203000 3000 mAh / 3 A**, selected during the electrical review
- **Current electrical choice: TalentCell YB1203000 (Amazon B00MHNQIR2, $22.99 observed),
  3000 mAh, 3 A max output, 105 x 65 x 25 mm, with supplied 12.6 V/0.5 A charger.**
  - Its output is 9–12.6 V, not regulated 12 V. The KBT product label says 2 A; earlier 2.4 A assumptions
    were incorrect. The new pack adds current margin and capacity for a $1 price increase.
  - Use a male DC5521 pigtail cut from the supplied splitter, verified centre-positive. Keep charge jack
    before S1; use the supplied charger. TalentCell's own switch must be ON for operation and charging;
    S1 remains OFF during charging. Both switches OFF for storage.
  - **CAD remains at the old KBT 70 x 55 x 40 mm envelope.** Battery supports, connector/switch access,
    deck height and clearances are deferred to a separate CAD PR at the owner's request. Do not treat
    existing base exports as ready for this battery. No mechanical geometry changes in this revision.
- The charge jack (2.1 mm panel jack, 8 mm hole) and an SPST mini toggle (1/4" bushing, 6.5 mm hole): since
  2026-10-14 (rev 9h) nothing shows on the shell. The switch is in a pocket under the cartridge floor, lever
  down (tip the lantern to flip it); the jack is on the deck, socket up, reached with the lantern lifted off.
  Kevin chose this over a port panel in the drum's bottom band (visible from his side) and over both
  underneath (which needs a cable groove at the rim). The switch stops the ~15 mA idle drain while stored.
- An LM2596 makes regulated 5.0 V directly for U1 and Hall. Only the XIAO supply branch passes through
  an NTE585 Schottky and removable JP1. Remove JP1 before USB; follow the guide’s service sequence.
  JP1 is a reviewable addition for supply isolation during calibration (Vetco header + shunt, $2.24).
- **Low battery (Kevin's decision):** "We shouldn't ever go below 50% battery." No buck-boost for now; it's
  listed as an upgrade only.
  - The firmware boosts the pump's PWM as the voltage drops (k = 12/Vbat, clamped 0.8-1.4), so the pour size
    holds.
  - The LED strip dims anyway, because its resistors and LED forward voltage make it nonlinear: ~70 % at 11.2 V,
    a third to a half at 10 V.
  - Below 10.5 V the light gives a double blink when the ring goes in.
  - Charge at about half.
- 8 AA cells were also raised; the KBT pack was chosen instead.

### Lighting
- **12 V green COB strip, 8 mm (HAMRVL B0CKYFLZFQ).** Cut on its 25 mm marks into 7 pieces (~75 cm total), all in
  parallel, about 0.6 A (estimated; measure it).
- Plain strip on one MOSFET channel. Dropped in the budget cut: the NeoPixel ring around the lock and addressable
  LEDs. `LED_RING = False`; this is an upgrade only.

### Electronics (see `docs/images/wiring.png`)
- Seeed XIAO RP2040 (B0DRNTQ338); GPIO assignments and firmware behavior are unchanged.
- Retain the original 74AHCT125 in its DIP-14 socket: pin 14 regulated 5 V, pin 7 ground;
  D3 → input 2 / output 3 → pump gate; D4 → input 5 / output 6 → light gate. Ground OE pins
  1/4/10/13 and unused inputs 9/12; leave outputs 8/11 open. Keep the existing C3 0.1 µF bypass
  and two 10 kΩ input pull-downs. No new gate series resistors or gate-to-source resistors.
  No practical need for replacing the gate driver has been established; retain the original design.
- Two IRLZ44NPBF low-side MOSFETs, driven directly by the original buffer. Specify the exact MOSFET
  in Item and vendor-title discrepancy in Notes. Normal startup/load/temperature checks remain necessary;
  withdrawing the replacement is not a claim that the original hardware has been tested.
- One added Hall capacitor C4 0.1 µF; total 0.1 µF count is three. Hall pull-up R5 4.7 kΩ,
  twist pull-up R6 4.7 kΩ, contact-current resistor R7 3.3 kΩ. October 20 delivery cutoff remains.
- NTE586 3 A/40 V flyback across pump, stripe to battery positive. Two NTE585 remain: XIAO supply and
  twist input. Capacitor C2 is 2200 µF/**25 V**; higher voltage rating does not extend overload runtime.
- Hall direct to D1 as above. D2F-01L switch: COM ground, NO through 3.3 kΩ to regulated 5 V; GPIO D2
  through 4.7 kΩ to 3V3 and Schottky anode at D2/cathode at NO. This supplies contact current without
  connecting the GPIO directly to 5 V. The 4-wire cable pinout remains 5V, HALL, SW/NO, GND.
- Fast switch purchase candidate: Amazon B0DBV9JX6L, Pecafeitas D2F-01L four-pack, $7.99; Oct 14 Prime /
  Oct 18 standard displayed for Seattle on Oct 13. Its Omron provenance is not authenticated. Verify
  marking/mechanics and repeated operation. Owner rejected the Oct 27 alternative as too late.
- Battery sense remains D0: 100 kΩ/22 kΩ + 0.1 µF. Optional PRIME stays on D6.
- Common ground, separate load-return routing; verify sensor levels and full-charge LED/combined-load
  current/heating on the bench. Startup/stall current and actual runtime are not measured yet.
- No fuse added in this revision; the pack has protection. The 3 A output rating is not a guaranteed
  protection-trip threshold. A jam/short is a fault to stop and investigate, not something C2 can sustain.
- USB-only flashing: remove JP1 and socketed U1 with power off. Powered USB calibration: JP1 removed,
  U1 installed and regulated supply present; follow guide sequencing. Ordinary operation is battery-only.

### Firmware (`firmware/green_lantern/green_lantern.ino`)
- States: IDLE, ARMED, POURING, HOLDING, FINALE, LOCKED.
- 10-bit PWM with gamma 2.2.
- Defaults: pour 11000 ms, speed 70 %, hard cap 20 s per pour, 60 ms ring-loss abort.
- Settings are saved in EEPROM emulation (magic `GL03`). Serial commands: `status`, `cal`, `pour`, `speed`,
  `leds`, `idle`, `save`, `stop`, `vcal`.
- Compiles for `rp2040:rp2040:seeed_xiao_rp2040` (63136 bytes).
- **20/20 simulated scenarios pass** (`firmware/test`, `make test`); they run the real `.ino` against mocks.
- Calibration is done with the shot glass only.

### Shopping (the shared Google Sheet, https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit; guide section 2)
Since 2026-10-14 the list lives only in the Google Sheet, edited by Kevin, Sky and Duncan (columns: Have, Still to get,
Who has it). The markdown, PDF and .xlsx copies were removed from the repo so they can't drift. Totals below are
the 2026-10-13 starting point; the sheet is the source of truth.
| Store | Total | Notes |
|---|---|---|
| Amazon | $118.02 | 9 items |
| Vetco | $41.88 | 17 lines, website prices |
| Tacoma Screw | ~$12 | estimate; M3 by the piece |
| Ace + local items | ~$14 | spring, jar, curtain, glass; estimates |
| **Total** | **~$186** | Filament (2 green PETG, 1 white) and tools are optional extras. |

- Amazon delivery dates were read from the listings on 2026-10-13 using a San Francisco default address.
- Part quantities Kevin asked about:
  - check valves: 1 used of 10
  - plugs: one of each pair
  - spring: 1

## 5. Accepted risks and things to measure on the real parts

| Item | Risk | What the guide says |
|---|---|---|
| Pump outline | Estimated; ~6 mm clearance | Measure, update `PUMP_*`, re-run `build.py` before printing the base |
| Jar | Bought locally | Must be ≤ 73 mm across with the lid, ≤ 76 mm tall |
| Shot glass | Bought locally | ≤ 52 mm across the top, ≤ 62 mm tall |
| COB current | ~0.6 A estimated | Measure with the multimeter |
| LED dimming on a draining pack | Accepted | Charge at ~half; buck-boost is an upgrade |
| Pen spring fallback | ~1/3 stiffness | Test the lock's snap-back (guide section 6, step 4) |
| Sphere halves | Need interior supports | Print notes in the guide |
| Fist envelope | Estimated | A mock-up print is suggested |

## 6. Known loose ends a reviewer should look at

- `docs/research/*.md` was written early (rev 2-5 era) and still describes the power bank, Adafruit parts and other
  superseded choices. These are background, not the current spec. Either mark them as historical or leave them, but
  the guide must never point to them for a current number.
- `cad/NOTES-base.md` is marked superseded. Same caution applies.
- Firmware wiring comments now match the electrical revision: Hall OUT directly to D1 with an external
  3.3 V pull-up. Internal pull-ups remain enabled; no firmware behavior change.
- `key_ring.stl` isn't generated; the guide says to glue `key_cap` onto any ring.
- The Tacoma Screw and local-item prices are estimates.
- The rendering tools are home-made:
  - `cad/render_views.py` is a painter's-algorithm renderer. It now subdivides large faces, because large faces
    used to make the back panel look wrong.
  - Don't read rendering artefacts as CAD defects. Check against `checks.py` and the STL itself.
- Totals and counts appear in several places: README, guide section 2, the shopping list, the PDF, guide
  section 3's part table (~850 g of filament) and the diagrams. **They drift.** Check them against each other.

## 7. Tooling notes for a fresh container

- CAD:
  - `pip install cadquery trimesh manifold3d numpy pillow networkx scipy shapely`
  - `cd cad && python3 build.py` (exports, then runs the checks; must report 0 problems)
  - `python3 tests/test_socket.py`
  - `python3 render_views.py` (rewrites `docs/images/cad-*.png`)
- Diagrams:
  - `docs/images/src/gen_*.py` write the SVGs.
  - The PNGs were made from the SVGs with Playwright at 2x. Keep the SVGs.
- Firmware:
  - The arduino-cli install script failed in an earlier container; downloading the release tarball from
    downloads.arduino.cc worked.
  - Install the core: `arduino-cli core install rp2040:rp2040 --additional-urls https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json`.
  - Then `cd firmware/test && make test`.
- Scraping Amazon from this environment:
  - curl gets a captcha. Playwright works on `/dp/<ASIN>` pages, sometimes after a "Continue shopping" page.
  - Search URLs are blocked; typing into the home-page search box works.
  - Amazon throttles parallel runs, so go one at a time.
  - Vetco: `vetco.net/search/suggest.json?q=` and `vetco.net/products/<handle>.json`.
  - Target and Home Depot block automated browsers, so their stock can't be checked.

## 8. Change log (newest last)

- **2026-10-13, full review (PR #6).** Four CAD defects fixed: no screw holes for the sphere/dish joints, three
  screws that could not seat, the rear sphere half exporting as three loose bodies, and nowhere for the switch
  wires to leave the lock. Plus print-orientation and guide fixes. Screw list now 4 x M3x6, 17 x M3x8, 8 x M3x8
  flat head, 6 x M3x10, 11 x M3x12, 14 nuts. Filament is about 1.2 kg (990 g of visible green parts). Details:
  `PROGRESS.md`.
- **2026-10-13, Kevin's answers.** Keep the DRV5032 fallback text, marked "not recommended". Accept the lock's
  spring return as it is: it is self-locking dry, so grease the ramp, plunger and bore and test it on the bench
  (the hand turns the ring back on the last word anyway).
- **2026-10-14, shopping list moved to the shared Google Sheet (PRs #7, #8).** The markdown, PDF and .xlsx
  copies were removed. The sheet has Status (Need / Partial / Have all, from Have vs Qty), Have, Still to get,
  Who has it (Kevin / Sky / Duncan), Category (Electronics, Fasteners, Fluid path, Lighting, Lock, Power, Shell,
  Supplies, Tools) and costs of what is left by store. Tools and supplies are in it too, without links or prices.
- **2026-10-14, README shows the printed parts (PR #9).** `docs/images/stl/` has front, top and iso renders of
  each printed part and a contact sheet; `cad/render_stl.py output ../docs/images/stl` regenerates them.
- **2026-10-14, painting instead of green filament: no.** The plastic needed is the same whatever the colour,
  and green PETG costs the same as any other. Paint (plastic primer, 2-3 cans) costs about what the green
  spools do, and the sliding fits (0.3 mm a side) would need masking. Instead: print the "any" parts (~215 g,
  including the lock wall) from leftover filament, and skip the white spool if someone has ~35 g of white or
  natural PETG for the two diffusers. Keep both green spools.
- **2026-10-14, hidden power port (rev 9h).** Kevin wanted no port visible from any angle. The drum's notch and
  the tray's port panel are gone; the switch sits in a 26 x 23 x 20 mm pocket under the tray floor on his side,
  the jack in the deck pointing up beside the lead notch. Cost: the lantern must be lifted off to charge, and
  it stands on two blocks when set beside the cartridge (the tube and cables pass under the rim).
- **2026-10-14, handoff.** `CLAUDE.md` at the repo root tells every session to read this file first and to keep
  it current.
- **2026-10-14, filament: two green spools stay.** Kevin asked whether one green spool would do if the "any" parts
  came from leftovers. No: the ~990 g of green is already only the visible parts, and with supports it comes to
  ~1,030 g. One spool would only work with `base_tray` in another colour too (~940 g, no margin for a failed
  print). Kevin kept two spools: the cost difference is small.
- **2026-10-14, blocks, not feet.** With the drum's notch gone, the lantern stands on two blocks (books, ~2-3 cm)
  whenever it sits beside the cartridge with the tube and cables attached, so the rim doesn't pinch them. Three
  printed 15 mm feet on the drum were offered instead; Kevin chose to leave it as is.

- **2026-10-14, electrical revision and board assembly:** selected TalentCell YB1203000, revised
  Hall/twist interfaces, 25 V capacitor, NTE586 pump diode and removable USB isolation jumper;
  original AHCT gate drive retained. See the current electronics section and `CIRCUIT_PR.md`.
  Added the complete two-sided board viewer, combined image, printable PDF and solder schedule.
  Keep the viewer simple, with both faces visible; maintain only final exports and their sources.
  Physical board offsets, capacitor dimensions and assembled clearances remain unverified.
  CAD changes are separate. Live Sheet edits wait for acceptance and separate owner review;
  estimated parts delta is $4.69 before tax/shipping, with an October 20 delivery cutoff.
