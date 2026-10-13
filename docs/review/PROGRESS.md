# Review progress

Full-project review, started 2026-10-13 on branch `claude/full-review`. Rules and decisions: [CONTEXT.md](CONTEXT.md).
Each phase below was committed and pushed when it finished, so the repo is consistent at every entry.

## Questions for Kevin

(Decisions I would change or that need your call. Nothing here was changed in the repo.)

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
