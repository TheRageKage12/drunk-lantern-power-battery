# Review progress

Full-project review, started 2026-10-13 on branch `claude/full-review`. Rules and decisions: [CONTEXT.md](CONTEXT.md).
Each phase below was committed and pushed when it finished, so the repo is consistent at every entry.

## Questions for Kevin

(Decisions I would change or that need your call. Nothing here was changed in the repo.)

**Both answered 2026-10-13:** 1. keep the DRV5032 fallback, marked "not recommended" in the guide. 2. accept the
lock as it is: grease it, test it on the bench first (it is the first print anyway); if it still sticks, the
steeper-ramp change below is the fix.

2. **Lock self-return is marginal by calculation** (phase 2). The return ramp rises 4 mm over the 45-degree
   arc (slope 0.26); dry PETG on PETG has a friction coefficient of about 0.3-0.4, so an unlubricated rotor is
   self-locking: it stays at 45 degrees when you let go. Greased (0.1-0.15) the ramp drives it back, but the
   net torque is small (roughly 3 mN m at full twist after the bore friction). I added grease to the guide and
   a troubleshooting row, and did not change the CAD: a steeper ramp needs more spring travel than the 10 mm
   spring has (coil bind), and the show does not depend on it (you turn the ring back on the last word, the
   firmware only watches the switch). If you want a guaranteed snap-back, the change is a 6 mm rise with a
   12-14 mm spring and a deeper pocket, which means reprinting the housing and the plunger. Accept, or change?
1. **DRV5032 fallback text.** The guide (section 2.1, under the Amazon table), `cad/params.py` and the firmware
   still describe the Adafruit DRV5032 board as an "if you ever have one" alternative to the A3144. It costs
   nothing and the CAD option works, but CONTEXT says no Adafruit. Keep as a documented alternative (my
   suggestion) or cut it?

## Phase 1: consistency (done)

Baseline before any change: `build.py` 0 problems, `test_socket.py` OK, firmware 20/20, compile 63136 bytes.

**Verified consistent (no change needed):** Amazon rows sum to $118.02, Vetco rows to $41.88, PDF totals
185.90 / 228.87 / 290.59; every ASIN, Vetco link, price and quantity agrees across guide 2.1-2.2, the shopping
list and the PDF; screw counts in guide sections 6, 8, 9 tally exactly to the Tacoma list (5 x M3x6, 11 x M3x8,
4 x M3x8 flat, 6 x M3x10, 20 x M3x12, 15 nuts); all section/step cross-references and image/file links resolve;
pins D0-D6, the A3144 diode direction (stripe to the sensor), the 3 diodes, resistor and capacitor counts,
74AHCT125 pin use, the divider ratio, the thresholds (10.5 V, 0.8-1.4) and the firmware defaults agree between
the firmware, the wiring diagram, the guide and the shopping list; `wiring.png` matched its source; the part
table's grams sum to 849 g; the firmware has 20 scenarios.

**Fixed:**
- Grand total: README and guide said ~$190, the list and PDF $186 / $185.90. All now say about $186, and the
  guide's total line now states what it includes (the ~$14 of local estimates: spring, jar, curtain sheet,
  glass) instead of listing the jar and glass under "assumes you already have".
- Guide and shopping list still asked for a 2.5 mm drill bit (the old open vent hole); only 6 mm is drilled.
- "Loctite" removed from the glue row; "nuts only for the thumbscrews" corrected (the lock's 6 and the
  handle's 6 take nuts too, 15 in all); the Amazon M3 kit fallback mentioned in the guide is now in the
  shopping list as well.
- Half-charge voltage: 11.2 V in section 15 vs 11.5 V elsewhere; now 11.3 V in section 15 (a resting 3S pack
  at half charge), 11.5 V stays as the "charge first" line.
- `cad/README.md` said the jar is "76 mm across the cap"; 76 is the CAD envelope, the buying limit is 73 mm
  (`BOTTLE_NECK_D`). Reworded.
- README and guide no longer send the reader to `docs/research/` for current numbers; it is labelled early
  and partly superseded. `cad/NOTES-dishes.md` got the same banner as `NOTES-base.md`.
- `params.py` comments still spoke of the door, the hatch, the glass tray and the WS2812B strip; the four
  unused rev-6 parameters are now marked unused (kept so old notes still read).
- Firmware: `save` help and the guide's `save` row said `vcal` saves itself; it does not (`vcal` only sets
  `battScale` in RAM, `save` writes it). Section 10 now says `save` after `vcal`. `cal` is refused only while
  a pour runs, not "only when idle". Section 4 step 8 said the strip glows faintly when first connected; the
  idle glow defaults to 0, so it blinks once at power-up and stays dark. Stale comments fixed: the "A3144
  divider" at `pinMode(HALL_PIN)`, "3V3 -> DRV5032 VCC" as if unconditional, "30-35 mL" vs the guide's 30-37,
  "3-cell" vs 3S2P. The lock-cable and LED plug pin order (5V, HALL OUT, SW, GND; +, -) is now written in the
  firmware header and on the wiring diagram, not only in guide step 7.
- Wiring diagram: dropped the 3.3 V legend entry (nothing in the A3144 build uses 3.3 V); the Hall diode is
  labelled "on the board" (the guide puts it there, the drawing had it inside the lock group). State diagram:
  `vcal` added to the bench command strip. Both SVGs and PNGs regenerated.
- Lock: the guide said the cam starts moving the lever at 33 degrees; the CAD (`CAM_START`) and
  `test_socket.py` (first lever contact between 30 and 35) say 30. Guide now says 30.

**CAD defects found by tracing every screw (all fixed, `DESIGN_CONTRACT.md` rev 9g, verified with probe
cylinders in the assembly and a negative control):**
- **The sphere halves had no screw holes for the dish joints.** `radial_screw_cutters` started every hole at
  r = 92 (sphere radius + 2) and went 8.4 mm inward, but at the joint height the collar wall is at r 66..70, so
  all six holes and counterbores missed the shell. The dish-side pilots existed. The cutters now start at the
  shell surface on the hole axis. The screws also moved from 2 to 3 mm above the flats (`JOINT_SCREW_ABOVE_FLAT`):
  at 2 mm a 5.5 mm socket head would have overlapped the dish flange below it.
- **Screw lengths that could not seat:** drum-to-dish and sphere-to-dish screws were M3x12 into 6.5 mm pilots
  behind 2.4-3 mm of wall (max 9.2 mm): now M3x8. Handle leg screws: an M3x12 through the 14 mm leg with a 2 mm
  counterbore ended exactly at the pocket wall (0 mm of thread), and the boss's outer wall had no hole to reach
  the head: the boss now has a 6.6 mm access hole and the leg's counterbore is 6 mm deep (3.7 mm of thread).
  Lock base plate: an M3x8 from the counterbore reached 0.6 mm into solid faceplate; and the counterbore left
  the heads 1 mm proud under the plate, which is supposed to sit flat on the lock wall: the three holes are now
  countersunk, M3x8 flat head from below.
- **Switch bracket screw:** the captured nut under the bracket needed 2.6 mm in a 1.5 mm floor (it stood 1.1 mm
  into the recess, lifting the switch into the faceplate), and an M3x6 from above would have ended 2.5 mm below
  the plate, in the lock wall. The screw now goes up from below (countersunk slot in the plate) through a round
  hole in the bracket into a 6 mm pilot in the housing beside the switch body. Side effect: the switch can be
  tuned with the lock closed (loosen, push the screw along its slot, tighten).
- Screw list now: 4 x M3x6, 17 x M3x8, 8 x M3x8 flat, 6 x M3x10, 11 x M3x12, 14 nuts (same 46 screws; guide
  rows, section 6/9 steps, shopping list and PDF updated).
- Guide step 9.6 told the builder to "fit the two alignment pins"; no pins exist in the CAD (a rev-1 leftover).
- `nozzle_guide` is exported foot down with the bend vertical; the table said "on its side, no supports", but
  on its side the foot hangs 10 mm below the channel. Now: foot down, small tree support under the end of the
  bend (the last 45 degrees hang past horizontal).
- Filament: the table's grams were volume x 0.76 g/cm3, but 2.4 mm walls at 4 perimeters and solid floors
  print ~85-100 % dense. Rescaled at 1.1 g/cm3 (diffusers solid): ~1.23 kg total, 1.2 kg green. Two spools
  still cover it, with less to spare than the guide implied.
- "The nozzle is 20 cm above the pump" (section 10): it is about 12 cm (tip z 220, pump axis z 78).
- Vent valve: the AQUANEAT barbs fit 3/16" airline, wider than the 1/8" pump tube the guide pushed them into.
  Step 7.1 now puts the valve's barb through its own ~5 mm hole in the lid (measure the barb), sealed with glue;
  the 40 mm of headroom under the dish fits the ~25 mm valve.
- Stale numbers in `dishes.py` comments (180 mm era) corrected; `docs/make_shopping_pdf.py` added so the PDF can
  be regenerated (it was not in the repo).

**Checks after phase 1:** `build.py` 0 problems (34 parts, all fit the bed), `test_socket.py` OK (lever contact
30-35 deg, post clear of the pushed-in rotor), firmware 20/20, compile 63136 bytes. CAD renders, the wiring,
state and lock diagrams and the PDF regenerated.

## Phase 2: revalidation of the risky numbers (done)

Independent recomputation; the design values held except where noted. Working below.

**Hall sensor (A3144 on the post).** On-axis field of a 6 x 2 mm disc, B(z) = Br/2 [(z+L)/sqrt(R²+(z+L)²) −
z/sqrt(R²+z²)], R 3, L 2, Br 1.17 T (N35 minimum). Magnet face to Hall element: 3.0 mm at rest, 1.8 mm with
the rotor pushed fully in (1.2 mm play), 3.4 mm with the rotor at the lip. Field 88 / 158 / 73 mT. Worst case
73 mT against the A3144's maximum operate point of 35 mT: **2.1x margin** at the weakest position, over the
whole play. Release: minimum release point 5 mT is reached ~11 mm from the element, i.e. with the ring pulled
~8 mm out; at hand speed that is tens of ms, well inside the 60 ms abort window. Twisting does not change the
distance (magnet and sensor are both on the axis). The sensor test in `test_socket.py` (post clear of the
pushed-in rotor) still passes.

**Nozzle.** Tip at (-2.7, -31.1), 19.3 mm from the glass centre, 6.7 mm above the rim, pointing 45 degrees
down along +X (tangential to the glass, not toward its centre). Bore 3.2 mm; 200-260 mL/min pump, flow ~linear
with speed; pulsation peaks taken as 1.5x the mean.

| Case | Jet speed | Radius at the rim plane | Meets the inner wall |
|---|---|---|---|
| 70 %, 200 mL/min | 0.29 m/s | 19.2 mm | 22.7 mm below the rim |
| 70 %, 260 | 0.38 | 19.2 | 18.2 |
| 100 %, 260 | 0.54 | 19.3 | 13.9 |
| 100 %, 1.5x peak | 0.81 | 19.4 | 11.0 |

Inner rim radius is ~23.5 mm, so the stream enters the glass at every speed with ~4 mm to spare and runs down
the far wall; no change. (The old level tip landed on the rim at 70 %, as the contract records.)

**Pour and battery compensation.** Duty = speed x 12/Vbat, clamped 0.8-1.4: the motor sees 0.70 x 12 = 8.4 V
from 12.6 V down to 8.6 V (then 8.3 V at the clamp), so pour volume is constant over the pack's whole range
(the protection board cuts at ~9 V). 11 s at 70 % of 200-260 mL/min is 26-33 mL, i.e. about 1 oz; calibration
sets the exact figure. Idle current ~15-20 mA from 12 V (XIAO ~25 mA at 5 V through the LM2596 at ~80 %, plus
the buck's quiescent); a pour is ~13 s at ~1.3 A = 4.7 mAh, so 2400 mAh is ~400 pours or ~5 h of idle plus
100 pours. "Well over 100 pours" holds.

**Power.** Peak ~1.3 A (pump 0.7, COB ~0.6, idle 0.02). 22 AWG (53 mΩ/m): 1 m of pump wiring drops ~70 mV,
nothing. IRLZ44N at Vgs 5 V: Rds(on) ~28 mΩ, 14 mW in the pump leg, 10 mW in the LED leg; PWM is the core's
default 1 kHz (`analogWriteFreq` is not called), gate charge ~48 nC through the 74AHCT125's ±8 mA gives ~6 µs
edges, ~50 mW of switching loss: no heatsink, the TO-220 stays cold. IRLB8721 (the part Vetco's page name
mentions) is the same or better on every number. LM2596: 4.5-40 V in, needs ~1.5-2 V of headroom, so 5.0 V
holds down to ~7 V input, below the pack's cut-off. C2 (2200 µF) inrush at switch-on is a sub-ms spike that a
3S protection board (ms-scale overcurrent delay, 3-6 A trip) ignores; the pump's soft start (16 % PWM) keeps the
motor's stall surge out of it too. Off-state drain: the divider and everything else sit behind S1; only the
pack's own protection board draws (µA), so months of storage. The charge jack is ahead of S1, so charging
works with the lantern off, as intended.

**Battery sense.** 100 k / 22 k from 12.6 V gives 2.27 V at D0 (ADC limit 3.3 V); 5 % resistors could be ±7 %
in ratio, which `vcal` removes. The 18 kΩ source impedance would be too high for the RP2040's ADC sample
capacitor on its own; the 0.1 µF at the pin supplies the sample charge, so the reading is fine (keep the cap).

**Gate drive.** XIAO high (3.3 V) vs 74AHCT125 VIH 2.0 V: 1.3 V of margin. Outputs swing to ~4.5-5 V, above
the IRLZ44N's rated Rds(on) point. OE pins grounded = enabled. The 10 k pull-downs on D3/D4 hold the inputs
low while the XIAO boots. During the ~ms before the 5 V rail is up, the buffer's output protection diode clamps
the gates near 0 V, so the Miller kick from the 12 V step at the drain cannot reach the 1 V threshold: no
start-up twitch. (A 100 k gate-to-ground resistor would be belt-and-braces; not needed, not added.)

**Clearances at 190 mm** (minimum distance, envelope to part, from the assembled CAD):

| Envelope | Closest parts |
|---|---|
| Jar | deck 0 (sits on it), tray 3.0, lower dish 5.4, drum 10.8 |
| Pump | deck 0, tray 3.0, lower dish 6.0, drum 6.8 |
| Battery pack | tray 0, deck 2.0 (holds it down), drum 31 |
| Thumbscrew boss sweep | tray 0 (its finger wells), deck 1.0, knobs 2.0, jar 6.5, pump 14.5, pack 30.8 |
| Glass at the pour position | well 0, lock wall / lock 3.0, bay floor 4.5, nozzle guide 6.9 |
| Glass slide-out path | well 0, lock wall / lock 0.5, rotor 2.0, key cap 2.5 |
| Fist | lock face 0 (the ring on it), rotor 0.5, key cap 1.0, curtain clamp 1.5, sphere 3.0 |
| Forearm | curtain clamp 9.5, sphere 11 |

The pump envelope is still the estimate from the contract (measure the real pump before printing `base` and
`dish_lower`); the 6 mm it has is what the 190 mm base bought.

**Lock spring and return (new finding, see question 2).** 0.5 mm music wire, 4.5 mm mean coil, ~8 active
coils: k ≈ 0.85 N/mm, so 1.0 N at rest (1.2 mm preload) and 4.4 N at 45 degrees (5.2 mm; 4.8 mm of the 10 mm
spring left, above its ~3 mm solid height). The ramp rises 4 mm over the 15.7 mm arc at r 22: slope 0.26
(14 degrees). Return drive = N (sin a − µ cos a): with dry PETG µ ≈ 0.35 it is negative (self-locking); greased
µ ≈ 0.12 it is ~0.6 N, ~13 mN m at the ramp, against ~10 mN m of friction where the plunger pushes the rotor
against the far side of the bore. The spring's stiffness cancels out of this ratio, so a stiffer spring does not
help and a pen spring does not hurt the return; it only changes the feel and the detent hold. Guide: grease
added (section 6 step 4, troubleshooting, tools list). CAD unchanged.

**Timing (firmware vs guide).** Hall debounce 100 ms before ARMED, switch 40 ms, abort 60 ms, ring-gone reset
200 ms, 20 s cap: the guide's statements match; the 20 simulated scenarios cover each.

Checks after phase 2: docs only (guide, shopping list, PDF); build/test state unchanged from phase 1.

## Phase 3: buildability (done)

Three passes: the guide walked as a first-time builder with only the shopping list; every STL checked for
printability as exported (trimesh: bodies, overhangs steeper than 45 degrees off the bed, bridges, thickness,
bed footprint); party failure modes against the troubleshooting table.

**CAD defects found and fixed (`DESIGN_CONTRACT.md` rev 9g, second batch):**
- **`sphere_rear` was three bodies.** Its joining flange (OD 87.3) sat 0.3 mm inside the shell's bore (87.6)
  and never fused; the export stood on two loose flange arcs with the whole shell 3 mm above the bed. The ring
  now lives inside the rear half, flush with the split, and the front half's bosses meet it there (same 3.7 mm
  of thread, probed). The dish rings align the halves. `checks.py` now fails any printed part that is not one
  solid.
- **Switch wires had nowhere to go.** They leave the base plate through its rim notch at socket +Y, which lands
  29.5 mm below the ring centre on solid lock wall; with the plate flat on the wall they were pinched. A 9 x 7
  window in the wall under the Hall window, on the notch's axis (probed, with a control 12 mm away hitting wall).
- `base`: printed top band down, the bottom band's step was a square 3 mm ledge all round, 103 mm up. It now
  has the same 45-degree cone as the top band.
- `rotor`: "top face down" bridged the 24.6 mm key-pocket ceiling (sag would eat the key cap's 0.5 mm play).
  Exported bottom down now (full disc on the bed, pocket printed from above).
- `nozzle_guide`: the C-channel's "open" side was a 1.7 mm slit with knife-edge lips, so the tube could not be
  pressed in as the guide said. The body face is now 1.5 mm from the bore centre: a 5.7 mm slit, lips that print.
- Sensor post radius 4.0 (walls beside the lead slot were 0.6 mm); tray finger wells 19 mm (20 broke out of the
  tray rim as a 0.3 mm wisp); back LED row 1 moved 1 mm (0.3 mm sliver to the Hall window).
- Not changed, documented instead: the two dishes' bearing rings (2.8 / 2.7 mm wide, 8-9 mm above the bed)
  start in mid-air; the table now asks for "touching build plate only" supports there. A CAD chamfer would
  change how the dish seats on the drum / the sphere, which is not worth it for a short ring of support.

**Guide: steps that would have stalled a first-time builder (all reworded):**
- The A3144 was soldered to its cable in section 4, but its bare leads must pass a 1.2 mm slot in section 6.
- The LED lead and its plug were "made" before any LED strip existed (section 8).
- The 5 x 7 cm protoboard has no mounting holes; the deck panel has four pads on 40 x 30 mm: drill them.
- Straps and zip ties (the CAD has slots for 20 mm straps and 2.5 mm ties) were on no list.
- The jack/switch/pack/buck leads are soldered on the bench, then the deck goes on over them: they must go
  through the deck's open edge notch (its two wire slots are closed holes).
- Every serial command (calibration, tests, cleaning, "on the day") needs the laptop on the XIAO, which is on
  the cartridge under the lantern: section 10 now says how (lift the lantern off, lead the tube and cables out
  through the port notch so the drum rim doesn't crush them) and section 13 is reordered.
- "Fit the two alignment pins" (none exist), "20 cm above the pump" (12), "cal into a cup" (only the glass
  fits), "press the tube into the channel" (now true), spring/plunger order, which key-cap face goes where,
  lead bend direction and staggered joints, where the flange screws are driven from (inside, before the top
  dish), soldering the top ring's leads before lowering the dish, handle part names being from the display
  side, the ridge end of the glass well, the three pillars with holes, the notch for the thumb knobs falling
  free, the brim for the three ring-footprint parts, elephant-foot compensation for the mating rings, "print
  thin walls" for the sensor post, and the tools list (hex keys, USB-C data cable, 3.2 mm bit, scale).
- Print-first list extended to the other sliding fits (tray in drum, dish spigot, housing in the top dish,
  well in the bay floor, a leg in its boss).

**Party failure modes:** troubleshooting rows added for a pump that won't stop, a ring that won't seat because
the rotor hasn't returned, a dark lantern, and plugs left unconnected after a refill; an "on the day" sequence
(charge, fill, prime, one test pour) in section 12.

Checks after phase 3: `build.py` 0 problems (now including the one-body check), `test_socket.py` OK with the
4.0 mm post, firmware unchanged (20/20). Renders and the PDF regenerated.

## Phase 4: simplification and cost (done)

Rules applied: no design change without Kevin; only pure wins applied (same part, cheaper or fewer). Prices
on the list were read from the listings on 2026-10-13, so I did not re-scrape every line; I checked the two
lines where a smaller pack could plausibly save money (results below).

**Applied (pure wins):** none. Checked on Amazon today: a 3 ft length of 1/8" x 1/4" food-grade silicone
(B0G1G5L8LS, $7.99, Prime Oct 14) would save $6, but one run with the 30 cm service loop is about 1.3 m, more
than 3 ft, and its food-contact claim ("meets sanitary standards") is vaguer than the Auber's FDA 21 CFR
177.2600 / NSF 51; the 10 ft Auber stays. Check valves: every 2-10 pack found costs $4.38-4.99, no cheaper
than the AQUANEAT 10-pack at $4.79; a single from a pet store (~$1-2) remains the saving, already in the list.

**Proposals (not applied; each needs Kevin's yes):**

1. **Drop the 74AHCT125 (U1), its socket and one 0.1 µF: saves ~$5.20 and 6 wiring steps.** Drive the two
   MOSFET gates straight from D3/D4 at 3.3 V. The IRLZ44N is specified at Vgs 5 V but its threshold is 1-2 V;
   at 3.3 V it has roughly 50-80 mΩ, which at 0.7 A is ~30-40 mW, still cold. Vetco's part is actually the
   IRLZ44NPBF today; if the bag turns out to be IRLB8721 (16 mΩ at 4.5 V, 1.35-2.35 V threshold) the margin
   is even better. Risk: low at these currents; the gate edges get slower (the XIAO's pins drive ~4-8 mA), so
   switching loss at 1 kHz stays under 100 mW. What changes: wiring diagram, guide section 4 steps 1 and 4,
   firmware nothing. I would keep U1: it costs $3 and removes a "why is my pump weak" question.
2. **(Moot since rev 9h, 2026-10-14: there is no port panel any more; Kevin chose a fully hidden switch and
   jack.)** USB reachable without lifting the lantern: +$6-9. A panel-mount USB-C extension (~20 cm, female to male)
   from the XIAO to a third hole in the port panel would make calibration, `vcal` and the cleaning runs a
   plug-in job. Needs a 24 x 10 mm cutout in `base_tray`'s port panel (PORT_W is 42, the jack and switch use
   ~30 of it, so the panel would have to grow to ~60 mm) and a matching wider drum notch. Worth it if you expect
   to recalibrate after the first party; not needed for one night.
3. **Six fewer nuts and screws on the handle: saves ~$1.50 and a store line.** The four lap joints (6 x M3x12
   + nuts) could be glued (PETG on PETG with CA glue holds a handle that only carries ~2 kg) or pinned with
   printed pegs. Keeps the lantern liftable by the handle either way. Low value; the screws also let you take
   the handle off to reach the top screws.
4. **One store fewer: Amazon M3 kit instead of Tacoma Screw.** The kit (B0HKFCTLK8, $8.99) covers 38 of the 46
   screws and the nuts; the 8 countersunk M3x8 still need a hardware-store stop (Ace sells them by the piece),
   so this only trades Tacoma for Ace, which you visit for the spring anyway. Net saving ~$3. Your call; the
   list now says this.
5. **Check valve: one from a pet store instead of the 10-pack: saves ~$3.** Already offered in the list.
6. **Tube: a shorter length.** 3 ft is too short (above); a 5 ft listing of the same spec would save ~$3 if one
   exists with Prime delivery. Not worth the risk of a lesser tube in the drink path.
7. **2200 µF to 1000 µF.** Saves cents; the XIAO-reset protection is about ESR and the pump's inrush, 1000 µF
   is enough at 1 kHz PWM. Not worth a change.
8. **Simpler lock return: none.** Reviewed in phase 2; the geometry is as simple as it gets for a spring return
   with a hard stop and a cam; the only simplification would be to drop the self-return and rely on the hand
   (the firmware already allows it), which saves the spring, plunger and ramp. Kevin said to keep the lock.
9. **Things I would not cut:** the battery sense (cents, gives constant pours and a warning), the power switch
   (storage drain), the check valve (a tipped jar over the electronics), the second green spool.

## Phase 5: polish (done)

- Every file in `docs/research/` carries a "Historical" banner naming what it still describes that was later
  superseded, and where the current design lives. `cad/NOTES-dishes.md` got its banner in phase 1.
- State diagram: the low-battery double blink is on it. Fluid-path diagram regenerated from the current CAD.
- README links the review folder; `cad/README.md`'s limitations mention the dish support rings; CONTEXT.md's
  loose-end list marks what the review fixed.
- Renders, diagrams and the PDF were regenerated in the phase that changed their source, so all are current.

Final checks on the branch head: `build.py` 0 problems (34 parts, all one body, all fit the bed),
`test_socket.py` OK, firmware 20/20, compile 63136 bytes.

## What was not done

- No listing was re-priced except the two checked in phase 4; the prices are the ones read on 2026-10-13.
- The pump's outline is still the contract's estimate; nothing in the review can replace measuring it.
- Nothing was merged; the PR waits for Kevin.

## Electrical revision — current handoff, 2026-10-14

- Local `circuit-review` includes the connected circuit diagram, revised build instructions,
  corrected firmware wiring comments and complete board assembly material. Firmware behavior and
  GPIO assignments are unchanged. `CIRCUIT_PR.md` records the changes and proposed Sheet edits.
- Board deliverables: two-sided viewer and PNG, four-page PDF, solder schedule and their sources.
  Instructions retain mounting and fit constraints; redundant exports and review history are excluded.
- Circuit/board generation and connectivity checks pass; viewer zoom and wire selection were checked
  in the browser. Firmware simulations previously passed 20/20; target compilation was unavailable
  (`arduino-cli` not installed). No hardware or populated-board CAD fit verification is claimed.
- Next: confirm actual board offsets and C2 dimensions; update battery supports and check hardware,
  cables and shell removal in the separate CAD PR. Live Sheet changes require separate owner review.
  Nothing published or purchased; CAD and the shared Sheet are unchanged.


## CAD circuit fit — 2026-10-14

PR #13 is merged and its Sheet updates are complete. New branch `cad-circuit-fit` updates the
TalentCell tray and matching deck holes, fixes the deck height at 44 mm, provides a required strap
route and printed buck supports, and moves the upward-facing charge jack clear of the board.
Board mounting pads now fit inside the drawing's screw keep-outs (print supports required).

Non-printing envelopes include the populated board, local rear wiring, plug/connector allowances,
S1, charge jack/plug, buck, pump diode and Hall capacitor. Full build: 553 strict electronics / shell
removal pairs checked, zero problems; all printed parts fit the bed. Socket mechanism and electronics
regression tests pass; firmware 20/20 and RP2040 compilation pass (63136 bytes). Updated exports and
renders accompany the source. Supplier dimensions listed as allowances still need measurement;
the complete harness and tool/finger access still require a physical fit check. After acceptance,
update the Sheet supplies bundle to four 20 mm straps plus its existing small zip ties; no Sheet write
in this CAD revision. See `cad/README.md` for limits and `docs/BUILD_GUIDE.md` for assembly.
