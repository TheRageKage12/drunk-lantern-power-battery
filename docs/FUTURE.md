# Future scope and improvement ideas

One place for everything we've decided **not** to do for Halloween 2026 but might do later. Nothing here is part of
the current build. When an idea gets picked up, move it into the design (CAD, guide, `docs/review/CONTEXT.md`) and
delete it here. Add new ideas at the end of the right section with the date and who raised it.

Everything here stays future scope until Kevin picks it up (2026-10-24). Costs are rough estimates; candidate
listings are noted where someone has looked, but nothing here is on the Sheet.

## Drink and refilling

| Idea | Why | How / notes |
|---|---|---|
| **Stop the tube twisting when the bag's cap turns** (Kevin, 2026-10-24) | Refilling in place means unscrewing the pouch's cap, and the tube runs through the cap, so the tube twists with it. | Options, best first: (1) a food-safe barbed Luer-lock pair for 1/8" ID tube, one half fixed through the cap, the other on the tube: twist off, unscrew, fill, reconnect (a joint on the pump's suction side, so tighten it well); (2) a small food-safe barbed swivel between cap and tube (neater, harder to find); (3) no hardware: a loose hole in the cap with a soft silicone grommet so the cap turns round the tube (weaker seal). For now: keep hold of the cap while it's off; screwing it back undoes the twist (guide section 12). Candidates for (1), checked 2026-10-24 (Prime, next day; sold only in packs, none stated food-grade): male 1/8" barb, 10-pack, [B09PTX6M2Z](https://www.amazon.com/dp/B09PTX6M2Z) $7.59, and female 1/8" barb, 10-pack, [B08414YZLM](https://www.amazon.com/dp/B08414YZLM) $10.11 (~$18 the pair; Luer is a standard, so mixed brands fit). |
| **Removable fill bin** (Kevin, 2026-10-24) | Lift the drink out to refill at the sink, then drop it back in, without touching the bag's shape in the bay. | A drop-in tray in the cartridge's bag bay with its own clip-on lid holding the bag; pairs with the quick-disconnect above. CAD: a new part in `parts/base.py` inside today's bay, keeping the draining floor, well and clip. |
| **A fill hole in the bag cover over the spout** (2026-10-24) | Filling in place with the cover on would let the bag take the bay's full shape (today the cover comes off to reach the spout). | A capped opening in `bag_cover` over the well corner, big enough for the cap and a funnel. |
| **Seal the bag in more tightly** (Kevin, 2026-10-24) | So the bag fills to the bay's full shape and can't shift or bulge past the cover. | A snug lid on the fill bin above, or a tighter `bag_cover` (a lip all round, a latch instead of just resting). |

## Lighting

| Idea | Cost | How / notes |
|---|---|---|
| Glowing ring around the lock (24-pixel NeoPixel ring + translucent halo) | ~$17 | Set `LED_RING = True` in `cad/parts/socket.py`; the ring needs addressable-LED code, which is in the git history before the budget change. (Moved from the build guide's section 16.) |
| Steady LED brightness on a draining battery | ~$6 | A small buck-boost converter set to 12.0 V between the +12 V rail and the LED strip's + (the pump keeps its firmware compensation). Without it the strip dims as the pack drains: ~70 % of its current at half charge (~11.3 V), a third to a half at 10 V. Charging at half keeps it bright enough. (From the guide's section 16 and CONTEXT, power.) |
| A separately dimmable channel for the hand side | ~$3 | One more MOSFET plus firmware, no reprint, if the audience side and the hand side need balancing (rev 8 note in CONTEXT; today the hand side is deliberately a little dimmer). |
| Line or paint the inside of the sphere white or silver | ~$0-10 | More light reaches the windows. Suggested during rev C, never confirmed. |
| Clear front lens | ~$5-15 | A bought clear acrylic or polycarbonate disc (118 mm, 1.5-3 mm) instead of the frosted printed lens: looking into the bell at the glowing LED panel, brighter. Needs the lens pocket adjusted for its thickness. Printed "clear" PETG comes out cloudy. Rejected for now (2026-10-23). |

## Electrical and serviceability

| Idea | Cost | How / notes |
|---|---|---|
| Plugs on the remaining soldered leads | ~$1.75 per JST SM 2-pin pair (Vetco) | Today only the lock cable (4-pin, cap floor) and the pump (2-pin, cartridge) have plugs. Plugs on the cap floor's LED and pump leads let it lift right out; plugs on each bell's LED lead let a bell come off completely. Kevin chose to solder with slack for now (2026-10-23). |
| Fuse | ~$3 | An inline 2 A slow-blow fuse between the pack and S1. The pack's protection board already cuts out on a short. (Moved from the build guide's section 16.) |
| PRIME button | ~$2 | 12 mm momentary button from D6 to ground; the firmware already supports it. (Moved from the build guide's section 16.) |
| Channels in the CAD for the bell LED leads | $0 | The bells' leads currently run along the inside of the shell held by dots of glue; a printed clip or groove would hold them neatly. |
| Space for the tube's slack coil | $0 | The guide leaves ~30 cm of tube coiled above the cartridge; no space for it is modelled in rev C. |

## Mechanical

| Idea | Cost | How / notes |
|---|---|---|
| Steel axles for the handle | ~$9-15 | `HANDLE_AXLE = 'pin'` in `params.py`: a glued 1/4 x 2 in dowel pin instead of the printed 12 mm shaft (stronger if the lantern is yanked or swung). Means reprinting both end pieces and both pivots. Rejected for now: the pins found were expensive or not on Prime (2026-10-23). |
| Thumbscrews for the drum-to-foot joint | $0 (Kevin has spares) | Swap the 3 M3s under green caps for inside thumbscrews into 6-32 inserts (16 of 23 thumbscrews used): no caps at all on the drum. Needs the drum band about 1 mm thicker again. Offered 2026-10-23, not chosen. |
| Guaranteed lock snap-back | reprint | The rotor's return ramp is marginal when dry (grease it, and the hand turns it back anyway). A 6 mm rise with a 12-14 mm spring and a deeper pocket, reprinting the housing and the plunger (PROGRESS, phase 2; accepted as is 2026-10-13). |
