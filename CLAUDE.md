# Drunk Lantern power battery

A 3D-printed Green Lantern power battery that secretly pours a shot, built for Halloween 2026 by Kevin, Sky and
Duncan. CadQuery CAD in `cad/`, XIAO RP2040 firmware in `firmware/`, the build guide in `docs/BUILD_GUIDE.md`.

## Before you do anything

1. Read `docs/review/CONTEXT.md`. It holds every design decision, the reason for it, what was rejected, and how
   the owners want to work. A decision there stands unless you find a concrete defect (a wrong number, a part
   that doesn't fit, something unsafe, something that won't arrive in time); if you would change one, ask first.
2. Skim the end of `docs/review/PROGRESS.md` for the latest review state and open questions.
3. `docs/review/transcript.md` is the design conversation up to the review. Search it to check why something was
   decided; don't read all of it.

## Working rules

- **One branch per piece of work**, from the latest `main`, then a PR. Never push to a branch whose PR is merged.
  Check the PR's state before every push and before calling it ready. Only the owners merge.
- **Keep the handoff current.** Any PR that changes a decision, a part, a quantity, a price, a dimension or how
  the team works also updates `docs/review/CONTEXT.md` (the decision and why, dated). Add a line to its
  "Change log" section.
- **The shopping list is the shared Google Sheet** linked from the README; there is no copy in the repo. Edit it
  in place (it has Status, Have, Still to get, Who has it and Category columns). Don't recreate it.
- **Checks before pushing CAD or firmware changes:**
  `cd cad && python3 build.py && python3 tests/test_socket.py` (0 problems, SOCKET MECHANISM OK),
  `cd firmware/test && make test` (all pass), and the arduino-cli compile in the README. Regenerate any image
  whose source changed (`cad/render_views.py`, `cad/render_stl.py output ../docs/images/stl`, `cad/export_viewer.py`, `docs/images/src/gen_*.py`).
- **Links:** exact product pages only (Amazon `/dp/<ASIN>`), never search pages; check delivery before Oct 31.
- No model identifiers in commits, code or docs.
