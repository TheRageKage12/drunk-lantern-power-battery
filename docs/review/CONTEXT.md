# Review context: decisions, reasons and open items

Written on 2026-10-13 at the end of the design sessions, for whoever reviews this project next. It condenses about
100 messages between Kevin (the owner) and Claude, plus 9 CAD revisions. **Read this before changing anything.**
Each decision here was made on purpose, usually by Kevin. Don't reverse one unless you've found a concrete defect,
and even then, ask Kevin first (see the review prompt).

The original brief and ChatGPT plan are in `docs/research/BRIEF.md` and `docs/research/chatgpt-transcript.md`.
Revision history is in `cad/DESIGN_CONTRACT.md` (revisions 2-9f).

---

## 1. The project

- **What it is:** a Halloween party prop. It's a 3D-printed Green Lantern power battery (lantern) that secretly
  pours a shot while Kevin recites the oath with his ring in the lock.
- **Size:** about 47 cm tall, 19 cm across at the base.
- **Based on:** Hedo3D's "Green Lantern luminous" (CC BY-NC 4.0, in `original-model/`), scaled up and hollowed
  for the hardware.
- **Deadline:** Halloween 2026. Today is 2026-10-13. Every part has to arrive in time to print, build and test.
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
- PRs #1-#4 are all merged into `main`.

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
  - a cam that lifts a D2F-L lever microswitch 3 mm
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
  - Wiring: VCC on 5 V. Its OUT goes through a 1N5819 (stripe toward the sensor) to D1, using the internal
    pull-up, so D1 never sees 5 V.
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
  5. **KBT 12 V 2400 mAh**, the current choice
- **Current: KBT 12 V 2400 mAh 3S2P Li-ion (B0C241NS29, the "2400 mAh, bare leads" variant, $21.99),
  70 x 55 x 40 mm, built-in protection board, charger included.**
  - Kevin corrected an earlier misreading: B0C241NS29 is the right listing and variant. Make sure the 2400 mAh
    bare-leads variant is the one selected.
- The charge jack (2.1 mm panel jack, 8 mm hole) and an SPST mini toggle (1/4" bushing, 6.5 mm hole) sit in a port
  panel on the tray. The switch stops the ~15 mA idle drain while stored. The drum has a notch open at the
  bottom, so it still lifts off.
- An LM2596 buck converter makes 5 V. The XIAO is fed through a 1N5819.
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
- Seeed XIAO RP2040 (B0DRNTQ338).
- 74AHCT125 as a 5 V gate driver (it must be **AHCT**).
- 2x IRLZ44N low-side MOSFETs: pump on D3, LEDs on D4, 10 k pull-downs.
- 1N5819 flyback diode across the pump.
- A3144 on D1, D2F-L on D2, battery sense on D0 (100 k/22 k divider plus 0.1 µF).
- Optional PRIME button on D6.
- 2200 µF bulk capacitor.
- No fuse; the pack's protection board cuts out on a short. A 2 A fuse is listed as an upgrade.

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
- (Fixed in the review, see PROGRESS.md phase 1.) The firmware comment at `pinMode(HALL_PIN, INPUT_PULLUP)`
  mentioned an "A3144 divider"; the A3144 is wired through a diode.
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
