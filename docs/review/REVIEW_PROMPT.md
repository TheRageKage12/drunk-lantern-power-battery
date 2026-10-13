# Full-project review: session prompt

## Before you start (Kevin)

- **Auto-continue off.** Make sure `autoContinueAtUsageLimit` is off (in `/config`, or in your settings.json).
  It makes Claude Code wait for the usage limit to reset and then continue. With it off, the session stops at the limit
  instead of running on into the next window.
- **Extra usage off.** At claude.ai/settings/usage, turn off extra usage, or set its monthly spend limit to $0.
  Then hitting the limit stops the session instead of billing you.
- **Check usage.** Run `/usage` and note the percentage, then start the session with the prompt below.
- **After phase 1**, run `/usage` again and scale up:
  - If phase 1 used about 15 %, the plan below fits.
  - If it used much more, tell the session to skip phase 5.
- **Near ~90 %**, type "wrap up". Everything up to the last finished phase is already pushed.

The phases run in priority order, so if the limit cuts the session short, only the least important work is lost.

---

## The prompt (paste everything below this line)

You're doing a full review of this repo: a 3D-printed Green Lantern prop that secretly pours a shot. Kevin builds
it for Halloween 2026. Parts arrive from Oct 14 to Oct 18, so there's time to fix the design, but not to redesign
it.

**Read first, in this order:**
1. `docs/review/CONTEXT.md`. It holds every decision made so far, the reason for it, and what was rejected.
2. `docs/review/transcript.md`, if it exists. It's the full design conversation. Use it to check *why* something
   was decided; don't reread all of it.
3. `docs/BUILD_GUIDE.md`, `docs/SHOPPING_LIST.md`, `cad/params.py`, `cad/DESIGN_CONTRACT.md`,
   `firmware/green_lantern/green_lantern.ino`, and `docs/images/src/gen_wiring.py`.

**Rules**
- **Decided means decided.** Don't reverse a decision in CONTEXT.md without a concrete defect: a number that's
  wrong, a part that doesn't fit, something unsafe, or something that won't arrive in time. If you think a decision
  should change, add it to "Questions for Kevin" in `docs/review/PROGRESS.md` with the reason and the cost. Don't
  change it.
- **Cost.** Never raise it without asking Kevin. Savings are welcome if they don't hurt reliability or the delivery
  dates.
- **Links.** Exact product pages only (Amazon `/dp/<ASIN>`), never search pages. Check the listing's delivery date
  (before Oct 31, ideally Prime). No Adafruit or Jameco.
- **Prove findings.** Back each one with a computation, a CAD check or a test before you fix it. A rendering
  artefact is not a CAD defect.
- **Git.**
  - Work on a new branch, `claude/full-review`, from `main`.
  - After phase 1, open one PR for the whole review and add each later phase as commits on it.
  - Check the PR is still open before every push.
  - Never merge; Kevin does that.
- **After every phase:**
  - run the checks below and fix anything they catch
  - commit and push
  - add a short entry to `docs/review/PROGRESS.md`: what changed, what you verified, open questions
  - Finished phases must stay valid if the session stops at any point.
- **Subagents.** Use them for independent areas (CAD / firmware+electronics / docs+shopping) when it saves time.
  Run at most 3-4 at once, and give each one the CONTEXT.md rules.

**Checks** (set up the tools first; see CONTEXT.md section 7)
```
cd cad && python3 build.py && python3 tests/test_socket.py      # 0 problems, SOCKET MECHANISM OK
cd firmware/test && make test                                   # 20/20 PASS
arduino-cli compile --fqbn rp2040:rp2040:seeed_xiao_rp2040 firmware/green_lantern
```
Regenerate any image, render or PDF whose source changed.

### Phase 1: consistency (highest priority, ~20 % of the budget)
Check that every number agrees everywhere it appears:
- dimensions, part counts and print orientations: `params.py` vs the parts, the guide's part table and
  `cad/README.md`
- pins, voltages, part numbers and quantities: firmware vs wiring diagram vs guide section 4 vs shopping list
- prices and totals: README vs guide section 2 vs shopping list vs PDF
- diagram labels vs the current design
- build-guide steps vs the CAD (holes, screws and their counts, sizes)

Also count screws by size from the CAD and compare with the Tacoma Screw list. Fix every mismatch. Start from
the "Known loose ends" in CONTEXT.md section 6.

### Phase 2: revalidate the risky numbers (~20 %)
Recompute these independently, with your working in `PROGRESS.md`:
- **Hall sensor:** field at the A3144 vs its worst-case operate point, across the full 1.2 mm axial play.
- **Nozzle:** the stream trajectory at both the lowest and highest pump speeds.
- **Pour:** volume vs time at speed 70 %, including the battery compensation.
- **Power:** current budget, wire gauges, MOSFET heat, buck converter input range, what the protection board
  does, and the idle drain while switched off.
- **Clearances:** every fit at 190 mm, and the glass slide-out path.
- **Gate drive:** the 74AHCT125 driving the IRLZ44N gates.

Report the margins. Fix only the real problems.

### Phase 3: buildability (~25 %)
- **Walk the build guide as a first-time builder with only the shopping list in hand:**
  - missing steps, tools or parts
  - steps in the wrong order, or parts trapped by an earlier step
  - unclear wording
- **Printing on a 230 x 230 x 240 mm Ender 3:** print orientations, supports, tolerances, and which parts to print
  first to test fit (the lock).
- **Failure modes at the party:** spills, the ring not detected, the glass stuck, a low battery. Check the
  troubleshooting table covers each one.

### Phase 4: simplify and cut cost (~20 %)
- Fewer parts, screws or stores, or cheaper equivalents that still arrive before Halloween.
- Write each idea up as a proposal in `PROGRESS.md` (saving, risk, what changes). **Don't apply design changes.**
- Apply only pure wins that don't change the design, such as a cheaper listing of the identical part, with a
  verified link and delivery date.

### Phase 5: polish (whatever is left)
- Add detail where the guide is thin.
- Clarify the diagrams.
- Regenerate renders, PNGs and the shopping PDF.
- Mark `docs/research/` as historical, where it's out of date.

### At the end, or when Kevin says "wrap up"
- Finish or revert the change in progress, so the branch passes all checks.
- Push, and update the PR description: a summary per phase and the list of questions for Kevin.
- Stop.
