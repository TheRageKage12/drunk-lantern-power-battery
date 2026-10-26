# Project context: decisions, reasons and open items

Written on 2026-10-13 at the end of the design sessions and kept current since (see the Change log at the end),
for anyone, person or Claude session, picking up this project. It condenses about
100 messages between Kevin (the owner) and Claude, plus 9 CAD revisions and the rev C redesign (2026-10-23). **Read this before changing anything.**
Each decision here was made on purpose, usually by Kevin. Don't reverse one unless you've found a concrete defect,
and even then, ask Kevin first (see the review prompt).

The original brief and ChatGPT plan are in `docs/research/BRIEF.md` and `docs/research/chatgpt-transcript.md`.
Revision history is in `cad/DESIGN_CONTRACT.md` (revisions 2-9i and C). The repository is
`TheRageKage12/drunk-lantern-power-battery` (renamed from `temprepo` on 2026-10-14).

---

## 1. The project

- **What it is:** a Halloween party prop. It's a 3D-printed Green Lantern power battery (lantern) that secretly
  pours a shot while Kevin recites the oath with his ring in the lock.
- **Shape (rev C, 2026-10-23):** the classic battery: an 80 mm drum (190 mm across), a 45° flare and 25 mm neck, a
  224 mm sphere with a lens bell in front and a hand bell behind, a mirrored neck and flare, a 190 x 80 mm top cap and
  the emblem lid; a loop handle on ring pivots at the sphere's sides.
- **Size:** about 45 cm tall to the lid, 49 cm with the handle up; 22.4 cm across the sphere, 32 cm front to back
  across the bells, 48 cm across the handle loop (from the CAD assembly).
- **Based on:** Hedo3D's "Green Lantern luminous" (CC BY-NC 4.0, in `original-model/`), scaled up and hollowed
  for the hardware.
- **Team:** Kevin (owner, wears the ring), Sky and Duncan.
- **Deadline:** Halloween 2026. Written on 2026-10-13. Every part has to arrive in time to print, build and test.
  Re-checked 2026-10-15: every Amazon item in stock, Prime delivery Oct 16-17, free delivery Oct 20; the Auber tubing
  had 2 left and the pump 12, so order those first.
- **Status:** designed, modelled and simulated, not built. Nothing has been measured yet. As of 2026-10-15 the Sheet
  shows nothing bought except what Sky and Kevin already own (tools, white PETG). Ask before assuming anything has been bought.
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
- Every PR so far (#1-#14) is merged into `main`. #13 (Duncan, electrical revision) and #14 (Duncan, CAD fit,
  inserts, videos) were merged on 2026-10-14; #15 is this review.
- Any PR that changes a decision, part, quantity, price or dimension also updates this file and its Change
  log. Refresh `transcript.md` at the end of a working session, not on every push.

**Repo content**
- No model identifiers in commits, docs or code.
- Commits carry the session's attribution lines.

## 3. How the show works (Kevin's own spec; don't change it)

1. Push the empty shot glass in under the lock until it clicks.
2. **Punch in horizontally**, fist first, ring face forward, through the frosted cover in the hand bell on Kevin's side.
   The ring is on the **left hand**. The Hall sensor sees the ring's magnet, and the light fades up to ~15 %.
3. **Twist 45° counterclockwise and hold.** Counterclockwise puts the hand in a better position to grab the
   glass. A cam clicks the microswitch, then:
   - the pump starts, about 1 oz in ~11 s (a bit under a full shot is fine)
   - the light climbs to ~90 % over the same time. This is the distraction while it pours.
4. Turn back (a spring returns the rotor). The light swells to 100 % and goes dark.
5. Grip the glass, slide it ~3 cm toward you, lift it out and bring it out through the cover.

- **Letting go early** stops the pump where it is. The light bumps ~10 %, then goes dark.
- The pump runs only while the ring is in AND the twist is held, and only once per insertion.
- The light should only **gradually increase in intensity**. No other light effects.
- Kevin's fist is under 4" wide x 3" tall. The model uses a 106 x 76 mm envelope through the 140 mm hand opening.
  Kevin said not to worry much about how far off-centre his fist is. Rev C puts the lock face about 16-17 cm in from
  the rear bell's mouth (8 cm in rev 9): **not yet tried by hand** (a box test is suggested; shortening the rear bell is
  the fallback).

## 4. Decision log (current state; the latest decision wins)

### Pump and fluid path
- **Pump: Kamoer KPHM200 12 V peristaltic (B09HGVLHFV), one pump.**
  - Rejected: two cheaper Adafruit 5 V pumps. They would barely make the 10-15 s window, need two tubes, and come
    from Adafruit.
  - Measured by Kevin 2026-10-23 (head 63.5 mm square, motor 40 x ~50 mm, 114 mm overall). Rev C: it lies on the
    cartridge floor at `PUMP_X` 37 (moved 7 mm right for a bigger bag bay), head in a U-saddle, one strap round the
    motor; it is now the tallest thing in the base and sets the 80 mm drum.
- **Tube: 1/8" ID x 1/4" OD platinum silicone, Auber 10 ft (B0DKB1NKB4).** Kevin asked if 3 ft would do. The
  10 ft listing was kept because the size is exact and it's cheap; the build uses well under 3 ft.
- **Reservoir (rev C, 2026-10-23): a 32 oz spouted pouch (amazon.com/dp/B09WR13XDT)** lying flat in the cartridge's
  D-shaped bay beside the pump, under `bag_cover`. About 0.65 L of room, so it fills to roughly 22 oz. A 32 oz bag
  keeps filling until the bay is full; the 16/15 oz flat pouches Kevin found are too wide to lie loose in the bay.
  - The floor has 45° fillets and falls 2° to a well in the back corner (`WELL_XY`); a C-clip by the well, tilted 15°,
    holds the tube's notched tip on the well's bottom **with the bag's film still round it**, so the last of the
    drink drains to the tube.
  - Rigging: a 6 mm hole in the pouch's cap, the 1/4" tube pushed through, long enough inside to reach the clip; one
    or two ~3 mm V-notches in its tip so the film can't seal over it; squeeze the air out. No vent: the bag collapses.
  - The jar, the Masontops vent lid and the check valve are gone (rev 9 history in the change log).
  - Rejected: a slot to feed the excess bag through the cover (the drink can't pull film through, and it would pool
    on the cover); a home-made heat-sealed bag; a rigid box.
  - **Refilling (Kevin, 2026-10-24):** the guide's procedure is fine; he'd rather fill the bag **in place in the bay**
    so it takes the most drink (guide section 12 has both). Keep hold of the cap while it's off: the tube turns with
    it, and screwing it back undoes the twist. A tube coupling, a removable fill bin and a tighter bag seal are in
    `docs/FUTURE.md`.
  - The pickup tube can't leak because the pump's rollers pinch it shut.
- **Nozzle (rev 9c, unchanged in rev C):**
  - The guide bends the tube **135°**, so the tip points 45° down and sits 6.7 mm above the rim, hidden behind the
    lock wall over the back third of the glass. The bend runs sideways behind the wall; Kevin asked on 2026-10-23
    whether the internals should turn 90° so it comes "straight on", then decided (2026-10-24) to **leave it where it
    is**, since the LED panel now hides it completely.
  - It replaced a 90° bend that threw the stream onto the rim. The stream lands about 19 mm from the glass centre
    at any pump speed.
- **Cleaning:** run warm water, then air, with `cal 8000`. Keep each run short: `cal 20000` would overflow the
  glass.

### Lock (socket)
- Flat 36 mm rotor with a keyed ring pocket:
  - hard stops at 0° and 45°
  - a cam that lifts a D2F-01L lever microswitch 3 mm (verify the purchased switch fits the existing bracket)
  - a radial spring plunger that returns the rotor
  - a 6 x 2 mm magnet hidden inside `key_ring`, a printed Green Lantern ring whose raised emblem is the key;
    the rotor pocket is the emblem's negative, no tab (since 2026-10-19; `key_cap` is the fallback for a bought ring)
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

### Layout (rev C, 2026-10-23; the lock wall itself is rev 8)
- **How rev C came about:** Kevin wanted it to look like Hal Jordan's classic battery (14:29), picked "the emblem lid
  and option C" (14:44: bigger sphere with bells, battery and electronics in a top cap, drink bag in the base, a short
  flared foot), asked for a mirrored top (15:15) and approved the mock-up (15:20). The lower and upper dishes, the
  display window, the hand port and the strip curtain are retired (`dishes.py` is out of the build).
- **Sphere:** 224 mm (the largest half the 230 mm bed takes), split front/back, the flats kept at 136.8 mm. Round
  openings: the lens opening (r 57) in front and the **hand opening, 140 mm** (r 70) behind, widened from 130 so a
  hand holding a full glass has room (Kevin, 16:40).
- **Bells** slide over plain collars round the openings: front 64 mm long (mouth r 84), rear 60 mm (mouth r 90);
  throats 8.5 mm thick for the thumbscrews' inserts. Each bell's LED lead is soldered into the harness with ~20 cm of slack, so the bell slides off and rests beside the lantern (no plug, see below).
- The internals keep their height relative to the sphere centre, so the **lock wall** (2.5 cm past the centre, toward
  the audience), bay floor, guide boss, glass well, nozzle guide and the lock carry over unchanged; the foot's riser
  now holds the bay floor. The glass sits in its slot under the lock and hangs into the foot's neck; a 1.5 mm ridge
  clicks it in; it slides toward Kevin, then lifts.
- **Front window (Kevin's "option D", 2026-10-23):** a plain white `led_panel` on the lock wall's four posts, in
  front of the spout, the glass and the back of the wall, with the **4 LED rows on its front**, ~5 cm behind the
  frosted front lens (`diffuser`, a full 118 mm disc: reprint the rev 9 one, which had flats). Why: rev C moved the lens
  out into the bell, so without the panel the spout guide and the glass would show as shadows. The light passes one
  frosted layer, not two. Rejected: a frosted panel with the LEDs behind it (dimmer), a clear lens (printed clear PETG
  is cloudy; a bought acrylic disc would be needed). The wall's back channels stay unused; no reprint.
- **Hand side (2026-10-23): one frosted polypropylene disc** (binder divider, 171 mm) with 8 cuts 62 mm from the
  centre, each ending in a punched 3 mm hole, so it looks like the front window when the hand is out; the 8 flaps fold
  round the arm and spring back flat. A full `curtain_clamp` ring presses its uncut edge flat against the rear bell's
  lip (4 countersunk M3x8 from inside). Rejected: one slit down the middle (two floppy halves that won't close).
  Cutting aids: `docs/images/curtain_template.pdf` (1:1) or the printed `cad/curtain_stencil.py` (open frame, ~14 g).
  Material as before: polypropylene, not PVC or vinyl (Target, Fred Meyer, Office Depot).
- **Light balance:** the audience side slightly brighter than the hand side (Kevin, 15:03: "the hand opening should be
  slightly dimmer"); still true with the full rear ring because of the panel's 40 cm.
- **Top cap:** one revolved part (plug into the sphere's top collar, neck, 45° flare, 190 mm cap with a thick rim
  carrying the lid's L-grooves); `wall_extension` (white) stands on the lock wall and catches in notches in the plug:
  it braces the wall and hides the wires running up.
- **Lid:** `halo_ring` (white cup: 3 bayonet lugs, a 4 mm flange that glows round the rim, its 1.2 mm top is the
  emblem's diffuser) with the green `emblem_lid` glued on and `emblem_centre` as the island; twist 20° clockwise past a
  click (no locking screw: it is opened often and carries no weight; Kevin agreed since nothing could hide a
  thumbscrew there). Two short pieces of 1.75 mm filament line the lid up; `cad/emblem_jig.py` centres the island.
  `top_diffuser` is retired.
- **Handle:** a loop on ring pivots at the sphere's sides (like the replica's wire handle), 235 mm arc radius, swings
  flat either way to lie round the middle. Joints at 45/90/135° (away from the corners): 40 mm laps, 3 M3x8 + nut and
  epoxy each, section 14 x 13.5 mm (thickened from 10 so heads and nuts sink under caps), pieces and pivots at 100 %
  infill. **Printed 12 mm axles by default** (Kevin, 17:47); the steel-pin option stays in the CAD (`HANDLE_AXLE`).
  Rejected: steel dowel pins (Everbilt ~$4.28 each "expensive as hell", Amazon packs not Prime), a steel rod through the
  handle (needs a vise), an inner/outer lap split to hide the screws (about 4x weaker in bending). **Rest direction
  (2026-10-24, Kevin): it swings either way and rests down on either side for now; no detent.**

### Base (rev C, 2026-10-23)
- **`foot`** replaces the lower dish: a spigot into the drum, the 45° flare, the neck, and a riser through the
  sphere's bottom collar to the bay floor.
- **Drum (`base`) 80 mm:** with the battery and board gone, the pump is the tallest thing down there. The drum is
  fixed to the foot (3 M3x8 under green caps; its top band is 2 mm thicker inward there so 3.3 mm of plastic sits under
  each head, Kevin 20:29). It stays M3 under Kevin's thumbscrew rule because it never comes apart in normal use (the
  offer to switch it to inside thumbscrews was not answered).
- **One-piece cartridge (`base_tray`):** a 3 mm floor, the pump saddle, a splash wall between pump and bag (66 mm,
  with a tube notch), the draining bag bay and clip, and the bayonet collar. `base_deck` and `thumb_knob` are retired.
  It twist-locks to the drum (3 lugs, 20°, click bumps): **to refill, twist the lantern a little anticlockwise and
  lift it off by the handle**; the cartridge stays on the table (Kevin kept the twist-lock, 17:28; thumbscrews from
  underneath would mean tipping the lantern at every refill).
- **`bag_cover`:** a D-shaped lid on the splash wall and the raised rim (Kevin 19:00: "a cover over the drink pocket…
  so the bag pushes against that"), a 22 mm finger hole; the bag, spout and cap all stay under it.
- Only the pump's 2 wires (through one plug) and the tube cross between the lantern and the cartridge.

### Fasteners (rev C, 2026-10-23)
- **Kevin's rule (17:17):** "things that might disconnect regularly should use the thumbscrews as long as they're
  strong enough and the printing makes sense. Other things should use the M3 and other screws we already have." He
  has 23 knurled PC-case thumbscrews (6-32, 6.5 mm thread, 7 mm collar, 11 x 8.7 mm head).
- **Nothing shows when it sits on the table** (Kevin, 20:47). Every thumbscrew turns from inside:
  - bells: 2 each, parallel to the hand, heads inside the sphere behind the top edge of the opening (45° either side
    of the top); renders showed them through the hand opening at the sides or underneath, so they moved;
  - top cap: 3 inside its neck (lid and cap floor out to reach); cap floor: 3 under the lid; foot: 3 inside its neck
    (lantern off the cartridge, reach up the drum).
- **6-32 brass heat-set inserts under every thumbscrew** so nothing wears (Kevin, 20:43): initeq #6-32 long
  (amazon.com/dp/B076QY9858, 20-pack, bought). 4.8 x 7 mm holes (`THUMB_INSERT_*`); print `cad/thumb_test.py` to
  confirm. Each thumbscrew grips ~4.2 mm. Rejected fallback: 6-32 nuts in pockets.
- Other outside screws sit under flush green `screw_cap` discs (print 25: drum 3, handle 18, pivots 4); pivot M3s
  come from inside the sphere; the curtain clamp's from inside the bell.
- **Counts:** thumbscrews 13 of 23; 6-32 inserts 13 of 20; M3 inserts 17 (flange 4, pivots 4, foot spigot 3, board
  standoffs 4, guide boss 1, socket housing 1); M3x6 4, M3x8 socket 13, M3x8 flat 8, M3x10 6, M3x12 4, nuts 14 — all
  from what Kevin already owns. New purchases: only the pouch and the inserts.
- Rejected: twist-on (bayonet) bells, built and then dropped once the thumbscrews held them (Kevin 17:20: "do we still
  need the twist on part?"); a multi-turn thread (winds up the LED wires).

### Threaded mounts — 2026-10-14

- The owner selected brass heat-set inserts and requested 4 mm holes at least 6 mm deep. All M3 receiving bores
  are Ø4 × 6.5 mm (17 in rev C; 32 in rev 9), for M3 internal threads; this supersedes the self-tapping plan.
- Added backing at the handle mounts and a nozzle insert boss beneath the bay floor, with a matching
  lower-dish relief. The bay floor now prints inverted with support inside its drip lip.
- Moved the twist-switch mounting screw 1.5 mm away from the cavity, with its bracket and base slot,
  to leave plastic around the wider insert. Switch-body and nozzle positions remain unchanged.
- Install inserts before mechanical assembly. The existing screw clearance holes, countersinks and
  14 nut joints remain unchanged.
- Listing (2026-10-15 review): ruthex RX-M3x5.7, 100 for $9.99 (Amazon B08BCRZZS3, Prime Oct 17). Its data
  sheet calls for exactly a 4.0 mm hole, and at 5.7 mm long it leaves 0.8 mm of the 6.5 mm bore under it. Any plain
  M3 x 5.7 x 4.6 mm insert is the same part; the 5 mm-wide "M3 x 4 x 5" type does not fit. In the Sheet as a
  Fasteners row. Engagement with the existing screw lengths (checked): drum/dish and sphere/dish M3x8 reach 5.3 mm
  into the insert, the deck M3x8 5 mm, the board M3x6 4.8 mm, the handle M3x12 4 mm, the switch-bracket M3x8 ~4.5 mm.

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
  - Verified 2026-10-15 against TalentCell's 12 V manual: the YB1203000 has ONE DC5521 port, labelled
    "Input/Output", a power button and an LED; "push the switch to position I to make the charging circuit
    breakover"; it "can output while charging"; input 12.6 V 3 A max, charger 12.6 V 0.5 A, ~6 h, 190 g. So J1
    wired across the pack lead ahead of S1 is the right place, and the pack's switch has to be reachable (rev C: on
    the cap floor, under the lid). A 2019
    independent test (SotaBeams) measured 2.4 Ah (80 % of rated) and 11 V at 3 A on one unit; at our ~1.3 A peak
    and ~5 mAh per pour that is still hundreds of pours.
  - J1's third (switched) contact is unused; the charger's LED (red charging, green done) is the charge indicator.
  - CAD now uses the 105 × 65 × 25 mm case, connector/switch end toward -Y. Revised tray rails,
    end stops and pillars match the wider footprint; deck holes follow. Keep the deck underside at
    z=44 mm independently of pack thickness. A required 20 mm strap retains the pack; its <=2 mm
    lower run is recessed under the tray (2 mm since 2026-10-23, the pack on a 1 mm bed). Verify the supplied plug and bend fit the 25 mm end allowance.
- **Rev C (2026-10-23): every electronic part lives on `cap_floor` in the top cap** (Kevin 15:03: "Do all the
  electronics live inside the sphere, so we don't have to deal with… pulling out wires?"): the battery (LED face down
  over a slot, so its charge dots show looking up through the hand opening), the board on four 10 mm standoffs, the
  buck, S1 in a box with its lever up (6.5 mm hole), and the charge socket (the splitter's female end, tied down).
  Lid off to switch on, charge, plug in USB or pull JP1; no lifting the lantern off for these. The lock, LED and pump
  leads come up behind the lock wall and the wall extension through the cap floor's wire hole: the lock cable through
  its 4-pin plug, the LED and pump leads soldered with ~15 cm of slack so the floor lifts out still connected. Nothing shows on the shell. The switch stops the ~15 mA idle drain while stored. About
  230 g sits up top (accepted). The rev 9h switch pocket under the cartridge and the deck jack hole are gone.
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
- **12 V green COB strip, 8 mm (HAMRVL B0CKYFLZFQ, 5 m reel).** Rev C: cut on its 25 mm marks into 10 pieces,
  ~158 cm, all in parallel on the one light channel: front bell ring 37.5 cm (behind the lens), rear bell ring ~45 cm
  (a full ring since 2026-10-23, was 25-30 cm), `led_panel` 4 x 10 cm, lock-face columns 2 x 5 cm, and ~25 cm in the
  top cap for the emblem (two 12.5 cm pieces on the cap wall under the rim; Kevin 14:56 "keep 25 cm").
- Current: ~0.8 A/m estimated, so ~1.25 A at full and ~2.0 A peak with the pump, inside the pack's 3 A (measure it).
  Runtime is not a concern: the light is only on during a pour (idle 0 by default; `leds` caps the maximum, default 255), so hundreds of pours per
  charge (Kevin, 21:46).
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
- Switch: Amazon B0DBV9JX6L, Pecafeitas D2F-01L four-pack, $7.97 (2026-10-15; Prime Oct 17). Its Omron
  provenance is not authenticated (the listing never says Omron). Verify marking/mechanics and repeated
  operation. Owner rejected the Oct 27 alternative as too late. Omron's D2F datasheet (checked 2026-10-15):
  minimum applicable load 100 mA at 5 V for the plain D2F, 1 mA at 5 V for the D2F-01; the 0.1 A hinge-lever
  model's operating force is 0.78 N max, same body and lever as the D2F-L the CAD was drawn for. R7 puts
  ~1.5 mA through the closed contact, plus ~0.65 mA from R6 through D3: 2x the minimum.
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
the 2026-10-13 starting point; the sheet is the source of truth. **2026-10-15:** parts total about $205 before tax
(Amazon $127.99 with the $9.99 inserts, Vetco $46.57, Tacoma ~$12, Ace ~$1.50, jar/glass/curtain ~$12, straps and
ties ~$5); tools and filament (now $16.99 a green spool) are extra. The increase since $186: the electrical revision
$4.69, the inserts $9.99, the straps ~$5 that were listed but never in the total, and the switch 2 cents cheaper.
**2026-10-21:** about $206 (Amazon $127.99, Vetco $43.69 after the jack came off, Tacoma ~$12, the VELCRO One-Wrap
roll $9 plus zip ties, Ace and local ~$13.50); build guide section 2 has the store table.
| Store | Total | Notes |
|---|---|---|
| Amazon | $118.02 | 9 items |
| Vetco | $41.88 | 17 lines, website prices |
| Tacoma Screw | ~$12 | estimate; M3 by the piece |
| Ace + local items | ~$14 | spring, jar, curtain, glass; estimates |
| **Total** | **~$186** | Filament (2 green PETG, 1 white) and tools are optional extras. |

- Amazon delivery dates were read from the listings on 2026-10-13 using a San Francisco default address.
- Part quantities Kevin asked about:
  - plugs: one of each pair
  - spring: 1

## 5. Accepted risks and things to measure on the real parts

| Item | Risk | What the guide says |
|---|---|---|
| Pump outline | Measured 2026-10-23 (head 63.5 mm square, motor 40 x ~50 mm, 114 mm overall) | Head 0.5 mm off the cartridge rim at `PUMP_X` 37: check the real head |
| Drink bag | 32 oz pouch in a 0.65 L bay; fills to ~22 oz | Lay it flat, spout at the well, tube clipped |
| 6-32 insert hole | 4.8 mm designed in | Print `thumb_test.py` first |
| Reach to the lock | ~16-17 cm in from the rear bell's mouth | **Validated 2026-10-24** (Kevin's box test with a 14 cm hole); fallback is trimming the hand bell |
| Shot glass | Bought locally; **validated 2026-10-24** | ≤ 52 mm across the top, ≤ 62 mm tall |
| COB current | ~1.25 A estimated for ~158 cm (~2.0 A peak with the pump) | Measure with the multimeter |
| LED dimming on a draining pack | Accepted | Charge at ~half; buck-boost is an upgrade |
| Pen spring fallback | ~1/3 stiffness; stiffness cancels out of the greased return, only fit matters (OD ≤ 5 mm, cut to 10 mm, solid length < 4.5 mm) | Guide SH-3 check, then BU-1 step 4 snap-back test |
| Sphere halves | 224 mm, dome up; short flat overhang under each bell thumbscrew pad | Print notes in the guide |
| Fist envelope | Estimated | A mock-up print is suggested |
| Filament | ~2.8 kg if solid (~2.6 kg green; STL volumes), less at real infill; Kevin has ~1.8 kg green | Slice everything and read the total; then buy a green spool or print hidden parts (cap floor, cartridge, bag cover, bay floor parts) in white: not decided |

## 6. Known loose ends a reviewer should look at

- `docs/research/*.md` was written early (rev 2-5 era) and still describes the power bank, Adafruit parts and other
  superseded choices. These are background, not the current spec. Either mark them as historical or leave them, but
  the guide must never point to them for a current number.
- `cad/NOTES-base.md`, `NOTES-dishes.md` and `NOTES-handle.md` are marked superseded/historical. Same caution applies.
- **Future ideas** (upgrades, deferred and rejected-for-now options) are collected in `docs/FUTURE.md` (2026-10-24).
- **Open in rev C (2026-10-24):** the 6-32 hole from `thumb_test.py` (TBD); filament (another green spool vs white
  hidden parts, to discuss after slicing); `RING_ID` (several rings, possibly different sizes; sizes later). Settled:
  handle rests either way; drum-to-foot stays M3 under caps (thumbscrews are in FUTURE); reach and shot glass
  validated; epoxy on hand.
- **Plugs (Kevin, 2026-10-23): no more for now.** The one JST SM 2-pin pair stays on the pump at the cartridge (it
  unplugs at every refill); the LED and pump leads at the cap floor and the two bells' LED leads are soldered with
  slack instead (those only come apart for repairs). Revisit later: each extra plug is a Vetco pair, ~$1.75.
- Firmware wiring comments now match the electrical revision: Hall OUT directly to D1 with an external
  3.3 V pull-up. Internal pull-ups remain enabled; no firmware behavior change.
- `key_ring` is generated since 2026-10-19 (sized by `RING_ID`); `key_cap` remains for a bought ring.
  `cad/render_ring_colour.py` re-renders its two-colour picture after a ring change.
- The Tacoma Screw and local-item prices are estimates.
- The rendering tools are home-made:
  - `cad/render_views.py` is a painter's-algorithm renderer. It now subdivides large faces, because large faces
    used to make the back panel look wrong.
  - Don't read rendering artefacts as CAD defects. Check against `checks.py` and the STL itself.
- Totals and counts appear in several places: the guide, the Sheet, the guide's part table (~2.8 kg if solid
  in rev C) and the diagrams. **They drift.** Check them against each other. `docs/images/fluid-path.*` is redrawn for
  rev C; `battery-seat.*` still shows the rev 9 cartridge seat (the cap floor's seat follows the same `PACK_*` numbers)
  and is kept as history until redrawn.

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

- **2026-10-14, CAD circuit fit:** resize TalentCell tray supports and matching deck holes while keeping
  the deck at z=44 mm. Ports face -Y to avoid the hidden switch pocket. Strap slots move clear of pillars;
  add an underside recess for the required strap. Remove mounting-pad gussets that intruded into board
  wiring space (four small print supports now required). Add non-printing electronic/component/cable
  envelopes and strict assembly/removal checks; dimensions not published by suppliers remain explicit
  limits to measure. Outer shell and circuit unchanged. PR #13 merged; its live Sheet updates are complete.

- CAD fit follow-up: the charging plug at the old jack position overlapped the populated board. Move
  the deck jack to (74, -25), retaining upward access with the shell off; model both jack and plugged-in
  lead. Compound-solid collision checks now examine solid pairs to avoid operand-order false negatives.

- **2026-10-14, brass inserts:** owner requested Ø4 mm bores at least 6 mm deep. Updated all 32 to
  6.5 mm depth, reinforced handle/nozzle mounts, relieved the lower dish and moved the switch screw
  with its bracket/slot. Added solid-geometry bore, wall, end-depth and mating-clearance checks;
  regenerated ten changed printed parts and the assembly previews. See the threaded-mount decision above.

- **2026-10-14, assembly videos in the repository:** owner requested the three MP4s in PR #14,
  without the local web page. Store them in `docs/videos/`, linked from README and BUILD_GUIDE:
  assembly order (4:08, 34 chapters), exploded view (0:12) and service access (0:12).

- **2026-10-14, show the tubing route:** the owner pointed out that the assembly video did not show
  running the tube from pump to nozzle. Added two animated cutaways before the lock wall is installed:
  pump outlet/service loop through lower dish and bay floor, then the nozzle riser/bend and 5 mm tip.
  Video is now 4:30 with 36 chapters. Lower routing and pump port are illustrative; the floor hole and
  nozzle path follow the CAD. The written guide explicitly identifies the free end and service slack.

- **2026-10-14, make pump-tube timing explicit:** Step 17 is now titled “Fit the tube, then mount the
  pump” and instructs opening the head/loading the tube while the cartridge is exposed, leaving the
  outlet end free before joining the shell. The build guide repeats this order. Video timing stays unchanged.

- **2026-10-15, review of Duncan's revisions (PR #15).** Re-ran every check on the merged PRs #13 and #14: CAD build
  0 problems (553 electronics pairs), socket, electronics and insert tests OK, firmware 20/20 and 63136 bytes.
  Verified against sources: the TalentCell manual (one input/output port, switch ON to charge, 0.5 A charger),
  Omron's D2F datasheet (1 mA minimum load for the D2F-01) and the ruthex insert data (4.0 mm hole). Nothing in
  the circuit or the CAD needed changing. Fixed: the committed `dish_lower.stl` had one coarse facet 0.7 mm inside
  the outer cone (re-exported, with the assembly and renders); the guide's board-hole coordinates (15/55, 15/45)
  disagreed with the board drawing's (18,17), (55,15), (15,45), (58,45); three "pending a separate PR" leftovers;
  the charge-jack position in section 12 (it is on your left now, not your side); the Sheet's protoboard note and
  strap count (4, battery strap <= 1 mm). Added: the heat-set inserts to the Sheet and the guide ($9.99), a
  2026-10-15 Amazon stock/delivery check (tubing: 2 left), the new total (~$205). The three videos were checked
  chapter by chapter against the guide and the CAD (inserts, strap, underside switch, relocated jack, tube route)
  and match; they have no source in the repo, so a design change means re-recording them.

- **2026-10-17, 3D assembly viewer.** Kevin asked for a colour-coded assembly view. `docs/assembly-viewer/index.html`
  shows every part from the CAD in its own colour, 14 assembly steps (the four subassemblies, the cartridge, the
  lantern, the final join) and an adjustable exploded view; bought parts appear as their size allowances. It is one
  self-contained file (meshes inlined, three.js from a CDN), viewable at https://raw.githack.com/TheRageKage12/drunk-lantern-power-battery/main/docs/assembly-viewer/index.html
  or from a downloaded copy. `cad/export_viewer.py` regenerates it; part colours, offsets and step text are in
  `viewer.template.html`. Re-run it after any CAD change, like the renders.

- **2026-10-19, printed key ring, left middle finger.** Kevin asked whether the ring would both fit the lock and look
  like a Green Lantern ring. Gluing the plain 24 mm key cap onto Hedo3D's ring would have hidden its emblem, and the
  27 mm head would land on the rotor face before the 3 mm cap reached the 3.5 mm pocket floor. `key_ring` replaces
  both: the ring and key in one print, the key a full 3.5 mm deep, the emblem cut 0.6 mm into its face, and (Kevin's
  request) the magnet hidden in a pocket opened from inside the band, 0.6 mm under the face. Cost: the magnet is
  0.6 mm farther from the sensor, ~55 mT at the worst rotor position against a 35 mT maximum operate point (1.6x;
  was 2.1x). Worn on the left middle finger, as Green Lanterns wear it; `RING_ID` 20.5 mm from Kevin's 20 mm
  measurement, to confirm on the middle finger. Same day, Kevin asked for the bold emblem and no tab: the raised
  emblem (circle and bars, 4 mm proud, the centre disc 0.6 mm lower like the real emblem) is now the key, and the rotor
  pocket is its negative, so the bars turn the rotor; it fits either way up. **The rotor must be (re)printed from this
  version.** Magnet to sensor 3.7 mm nominal, ~53 mT worst case (1.5x). The ring now needs support under its head
  when printed emblem-down.
  Kevin's middle finger measured 20-25 mm with calipers, too wide a range to print from, so `cad/ring_sizer.py` makes
  ten labelled test bands (18.5-23 mm); `RING_ID` = the band that fits over the knuckle + 0.5 mm.
- **2026-10-19, white emblem outline on the ring.** Kevin chose a white outline (option C of three mock-ups: all
  green, whole emblem white, outline white). The ring prints emblem down and its first 0.6 mm (`EM_STEP`) are only
  the circle and bar faces, so a filament change before layer 4 (Z 0.8 mm) gives white faces and a green centre with
  no CAD change, using the white PETG the team already has (<1 g). The whole-white emblem was rejected because the
  magnet sits behind only 0.6 mm of the centre disc and would show through white. Three white layers over green may
  look pale; the guide says to test the first 1.5 mm. Kevin dropped ring LEDs (glove-wired coin cell) and glow
  filament (cost). `cad/render_ring_colour.py` renders `docs/images/ring-white-outline.png`.
  Step 2 of `docs/videos/assembly-guide.mp4` (9-16 s) still showed the old tabbed key cap glued onto a ring; that
  slide was replaced with the white-outline `key_ring` and the new magnet step (same timing and chapters). The video
  has no source in the repo, so any later change to it is a frame edit like this one.
- **2026-10-19, charge jack is the Vetco 321B.** Vetco ran out of the 2112 (8 mm hole). Kevin's first find, the
  Velleman CD021, is an inline jack with no thread or nut, so it can't sit in the deck. The 321B is the same DC5521
  female panel jack, in stock, $2.99, but takes a 7/16" (11.1 mm) hole and is 12.4 mm wide: `PORT_JACK_D` 11.3 mm,
  jack envelope 13 x 13 mm below the deck and a 17 mm nut allowance above it. The deck stays solid round the hole and
  all checks pass. A deck already printed with the 8 mm hole can be opened up instead of reprinted.
- **2026-10-20, no charge jack for now.** Vetco's shelf had no 2.1 mm panel jack (the 2.5 mm one they offered won't
  take the charger's 2.1 mm plug). Kevin chose to skip the jack: the TalentCell's single DC5521 port is both input
  and output, so you charge by unplugging the battery lead at the pack and plugging the charger in, pack switch ON.
  The port and switch are at the pack's -Y end, about 12 mm in from the tray edge between two pillars, with nothing
  but the drum in the way (probed), so they're reachable with the lantern lifted off. Cost: you swap plugs to charge,
  and must remember to plug the lead back in. The CAD is unchanged: the deck keeps its 11.3 mm hole and the jack
  envelope, so a jack can be added later across the lead ahead of S1. Guide, board docs (J1 removed) and the Sheet
  updated; Vetco -$2.99. Chapter "Install the charge jack" in `docs/videos/assembly-guide.mp4` is now optional.
- **2026-10-21, battery LEDs show through the floor; charge through the splitter (supersedes the 2026-10-20 plug
  swap).** Kevin pointed out the supplied splitter is "1 female to 2 male", all ends joined: one male stays in the
  battery, the other is cut for the board, and the female end is the charge socket, so charging never needs anything
  unplugged (the manual says the pack can output while charging). The female end stays inside, beside the battery's
  end; charge with the lantern lifted off. The pack lies LED face down over a 26 x 6 mm floor slot so its five
  fuel-gauge dots show from underneath (12.7 mm in from the end and 25.4 mm long are Kevin's caliper numbers; the
  row's offset across the pack is from TalentCell's photo, so `docs/images/battery-seat.png` asked him to confirm it; after checking the battery he set the slot to run 14 to
  40 mm from the port-side edge, `PACK_LED_FROM_PORT`).
  Tried the same day and dropped by Kevin: an exposed horizontal charge slot under the floor (it needed a right-angle
  battery plug and sat next to the rocker's finger hole; no other floor spot fits the 71 mm socket-plus-plug run).
  The pack's rocker has no floor hole: it stays ON, S1 is the power switch. The battery lead's straight plug with its cord
  folded back in a U-turn reaches 35 mm from the battery's end (Kevin). Centred, the drum wall at the port is only
  35.2 mm away, so at Kevin's request the battery moved 7 mm toward +Y (`PACK_Y`; its +Y end stop now merges into
  the S1 pocket): ~6 mm clear. Moving the S1 pocket to go further was considered and not needed. The deck's
  11.3 mm jack hole stays, empty.
- **2026-10-21, whole-repo audit and build guide reformat.** Kevin asked for everything to be checked and the guide
  made easy to read. No design decision changed. Guide: contents list; viewer and video notes as bullets; shopping
  items renumbered 1-23 with the strap roll, jar and shot glass as their own rows, small parts priced from the Sheet
  ($24.47), a "no charge jack" note and a store-by-store total (about $206, up from $202 because the One-Wrap roll is
  $9, not the ~$5 estimated); print settings, inserts and test prints as tables and lists (`ring_sizer` added to the
  part list); section 4's invalid "2a" step renumbered (cross-references now say step 8 for the lock wires); the
  power modes as a table; section 9 step 1 split into labelled sub-steps; section 12 reordered (on the day, the
  performance, charging, refilling). Stale "charge jack fitted" text fixed in the `params.py` and `electronics.py`
  comments, `cad/README.md` (the old 25 mm plug/switch-face row removed; the jack reserve marked optional),
  `DESIGN_CONTRACT.md` (LED slot 26 x 5 mm, centred 14.5 mm in; print bed 230 x 230 x 240; no service door),
  `gen_wiring.py` (J1 box now "Charge socket", the splitter's female end), the protoboard sheet ("charge at the
  splitter's female end") and the viewer's cartridge steps (battery LED face down, U-turn, switch ON in step 1). The
  cartridge and cutaway renders no longer draw the optional jack's reserve. Unused `BATTERY_PLUG_Z0` removed. The
  optional-jack envelopes stay in the fit checks so a jack can still be added later.
- **2026-10-22, the bay floor's insert boss is a separate glued-on part.** Kevin pointed out that `bay_floor` had
  features on both faces (the drip lip up, the nozzle guide's insert boss down), so it printed boss-up with the
  whole 2 mm floor on supports. The boss is now `guide_boss` (8 x 6 mm, printed bore up), super-glued under the
  floor and lined up with a 4 mm drill bit; the insert is then set from the top through the floor into the boss.
  The screw's pull presses the boss against the floor, so the glue only locates it. `bay_floor` prints floor down,
  lip up, no supports. The placed geometry is unchanged (checked against the old part to 0.000002 mm), so the lower
  dish relief, the nozzle height and the insert count (32) stay as they were. The drip lip stays: it keeps spills
  on the tray, off the cartridge below.
- **2026-10-23, battery strap recess 2 mm.** Kevin measured the VELCRO One-Wrap at about 1 mm but wasn't sure, and
  asked for 2 mm. The tray floor is only 2 mm, so `BATTERY_STRAP_T` = 2 alone would have cut through it. Instead
  the pack lies on a 1 mm printed bed (`PACK_BED_T`, bridged out to the strap slots across the strap band), so 1 mm
  of floor stays over the recess. Nothing else moves: the deck stays at z=44 (16 mm over the pack instead of 17),
  the lantern's height is unchanged, the LED slot cuts through the bed too, and the battery plug envelope rises
  1 mm with the pack. All checks pass; `test_electronics.py` now runs its strap route with a 2 mm strap.
- **2026-10-23, pump measured.** Kevin measured the Kamoer KPHM200: head 2.5 x 2.5 in (63.5 mm square), silver
  motor can 40 mm across and just under 5 cm long, 4.5 in (114 mm) overall from the motor's tabs. Everything fits
  the existing cradles; the only change is `PUMP_H` 63 -> 64 mm (the head is 0.5 mm taller than reserved), which
  raises the pump axis and motor saddle 0.5 mm. The envelope keeps ~6 mm to the drum and lower dish. "Measure the
  pump" removed from the guide, CAD notes and viewer (the assembly video never said it). The head box length
  (`PUMP_HEAD_L_EST`, 40 mm) stays an allowance; the pump slides along the saddles to seat the motor.
- **2026-10-23, taller drum for an 8 oz jar.** Kevin wanted more drink per fill than a 4 oz jar (~3 pours). The
  jar can't get wider (73 mm is the limit beside the pump), so the drum grew instead: `BASE_H` 115 -> 147 and
  `BOTTLE_H` 76 -> 108 for his 8 oz Ball quilted jelly jar (73 mm across, 100-105 mm tall with the lid; ~200 mL
  usable, 5-6 pours). Only `base` changes shape; everything above it moves up 32 mm and the lantern is ~50 cm tall.
  Scratch builds at 145 and 175 mm both passed every check; 147 leaves 2-3 mm over the jar. The vent valve's ~40 mm
  of headroom is unchanged. Lock cable now ~45 cm, the nozzle ~15 cm above the pump, one tube run ~95 cm. Kevin's
  shot glass (48 x 60 mm) fits the well.
- **2026-10-23, silicone vent lid instead of the check valve.** Kevin has a Masontops fermentation kit
  (B01H7GI7V8). One Pickle Pipe lid, trimmed to the jar's flat-lid size and turned valve-down under the jar's band,
  is the vent: air in, nothing out when tipped (Kevin's tip test passed), food-grade, no glue or drilled metal, and
  nothing above the lid but the tube. A submerged valve still vents by bubbling, so the jar can be filled full.
  The check valve is dropped from the guide and the Sheet (-$4.79; total about $201). Guide section 7 step 1,
  cleaning and troubleshooting rewritten for it.
- **2026-10-23, rev C: the classic battery shape** (branch `claude/classic-battery`). Kevin chose concept C with the
  emblem lid (14:44) and approved the mock-up (15:20): 224 mm sphere with a lens bell and a 140 mm hand bell, foot,
  80 mm drum, one-piece cartridge with a 32 oz pouch (B09WR13XDT) under a cover on a draining floor, every electronic
  part on a cap floor in the mirrored top cap, emblem lid with a white halo, loop handle on ring pivots with printed
  axles. Then, the same day: every fastener hidden (thumbscrews from inside into 6-32 inserts B076QY9858, other heads
  under 25 green caps), bell thumbscrews parallel to the hand over the openings, the drum band and handle thickened,
  Kevin's white LED panel in front of the spout and glass, a full rear LED ring, a 25 cm emblem ring in the cap
  (~158 cm of strip), and a one-piece slit hand-side cover with a full clamp ring, template and stencil. Retired:
  dishes, display window, strip curtain, jar and vent lid, cartridge battery and deck, thumb knobs, top diffuser.
  Guide, viewer, videos, renders, CAD README and design contract updated. Open items in §6.
- **2026-10-23, no extra plugs.** Rev C would have needed 4 more JST SM 2-pin pairs (cap floor LED and pump leads,
  both bells). Kevin: leave it at the one pair for now (the pump at the cartridge); the rest are soldered with slack.
- **2026-10-24, future list; spout and refill settled.** Kevin: leave the spout as it is (the LED panel hides it);
  the refill guide is fine and he'd fill in place under the cover. New `docs/FUTURE.md` collects every future idea
  (moved there from the guide's section 16, CONTEXT and PROGRESS), plus his new ones: a tube coupling or swivel so
  the bag's cap can turn, a removable fill bin, and a tighter bag seal.
- **2026-10-24, build guide rewritten as a design proposal.** Kevin asked for `docs/BUILD_GUIDE.md` to read like a
  senior engineer's proposal to leadership and the build team: executive summary, requirements with verification,
  system design, then six tracks (Shopping SH, Electrical EL, Software SW, Fluids FL, Printing PR, Build BU), each a
  numbered procedure with tests built in and "Blocked by" lines between tracks; current state only, no names, no
  decision history (that stays here). Build steps keep the viewer's 0-16 numbering. Also settled: the handle swings
  either way and rests down (no detent); reach and shot glass validated; epoxy on hand; drum-to-foot stays M3;
  `thumb_test` and filament still open; ring sizes later. Pen-spring check added (guide SH-3).
- **2026-10-24, 3D printing tracker.** Kevin asked for a print tracker: the shared Sheet has a new "3D printing" tab
  (one row per printed part in the guide's print order, with a Status dropdown, Printed/Left counts, settings,
  grams if solid from the STL volumes (~2.86 kg: ~2.10 green, ~0.19 white, ~0.58 any colour), inserts, the build step
  each part unblocks, and who is printing it). The guide's PR-5 and `CLAUDE.md` point to it.
- **2026-10-26, smooth STLs.** The first printed `bell_front` showed flat vertical facets: `build.py` exported every
  STL at 0.15 rad angular tolerance, ~55 segments round a 150 mm bell (~8.5 mm flats, visible in glossy PETG). Printed
  parts now export at 0.02 mm / 0.05 rad (~250 segments on the bells, ~1.8 mm flats, 0.003 mm deep); envelopes stay
  coarse. STLs grow from ~17 MB to ~36 MB. The print also showed a wandering seam line: the guide's PR-3 now says to
  align the seam on the hidden side (bells: underneath, opposite the midpoint of the two insert holes). Reprint
  `bell_front` from the new STL if the facets bother you.
- **2026-10-26, old-STL prints stay; reprint at the end.** Old and new STLs fit each other (same geometry; the old
  mesh only cuts inside curves: the worst mixed joint, a new `halo_ring` in an old `top_cap` rim, keeps >= 0.18 of its
  0.3 mm a side). Kevin: defer reprints to the end to finish in time. Marked Reprint in the Sheet: `bell_front`,
  `foot`, `base`, `top_cap`; parts not yet printed are noted "new STL only". Guide PR-6 gains sanding steps as the
  alternative to a reprint.
