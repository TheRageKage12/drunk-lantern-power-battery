# Green Lantern power battery that pours a shot

A Halloween prop: a 3D-printed Green Lantern power battery (about 470 mm tall, 190 mm across at the base)
with a hidden peristaltic pump, a hidden nozzle, and a twist-to-pour lock inside the sphere.
Punch in through a strip curtain so the ring seats in the lock, then twist and hold it through the oath: the
pump pours about 1 oz into the shot glass under the lock while the light climbs; turn back and the light
swells and goes dark. Slide the glass out and drink. Current prices and purchase status are maintained in the shared shopping Sheet.

Start here: **[docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md)** (parts list with links, printing,
assembly, wiring, firmware, calibration, testing, cleaning). Shopping list (who has what, what's left to buy, links and prices): the
[shared Google Sheet](https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit).

**Current build:** [circuit](docs/images/wiring.svg), [board assembly](docs/review/protoboard/README.md),
and [CAD fit limits](cad/README.md#electronics-fit-limits). The tray now fits the selected TalentCell case;
verify the listed component and connector dimensions before printing. The shopping Sheet matches this circuit.

**3D assembly viewer:** [open in the browser](https://raw.githack.com/TheRageKage12/drunk-lantern-power-battery/main/docs/assembly-viewer/index.html): every part colour-coded, 14 assembly steps and an exploded view
(`docs/assembly-viewer/index.html`; it also opens from a downloaded copy).

**Assembly videos:** [Build order (4:30)](docs/videos/assembly-guide.mp4) ·
[Exploded assembly (0:12)](docs/videos/separate-and-assemble.mp4) ·
[Opening for service (0:12)](docs/videos/service-access.mp4).

## The printed parts

All 25 parts as exported from `cad/output/` (iso view). Front, top and iso views of each part are in
[`docs/images/stl/`](docs/images/stl/).

![the 25 printed parts](docs/images/stl/parts-iso.png)

## Repository map

| Path | What it is |
|---|---|
| `docs/BUILD_GUIDE.md` | The build guide. |
| `docs/images/` | Wiring, fluid path, state machine, socket mechanism diagrams and CAD renders; `stl/` has a preview of every printed part. |
| `docs/review/` | The design-review handoff: `CONTEXT.md` (every decision and why), `PROGRESS.md` (what the review checked and changed, and the open questions), the prompt and the conversation transcript. |
| `docs/research/` | Early research notes (historical: several choices were later superseded, see `docs/review/CONTEXT.md`), the project brief, and the original ChatGPT transcript. |
| `cad/` | Parametric CadQuery model. `params.py` holds every dimension; `parts/*.py` build the parts; `python3 build.py` exports `cad/output/*.stl` and `*.step`, an assembly, and runs fit checks. See `cad/README.md` and `cad/DESIGN_CONTRACT.md`. |
| `cad/output/` | Ready-to-slice STL files (and STEP files) for every printed part. |
| `firmware/green_lantern/` | Arduino sketch for the Seeed XIAO RP2040. |
| `firmware/test/` | Host-side simulation of the firmware interlocks (`make test`). |
| `original-model/` | The stock lantern this design scales up: Hedo3D "Green Lantern luminous" (Cults3D #40633), CC BY-NC 4.0. Kept for reference and for the ring. |

## Regenerating the CAD

```bash
pip install cadquery trimesh manifold3d numpy pillow networkx scipy shapely
cd cad
python3 build.py            # all parts -> cad/output/, assembly, checks
python3 build.py socket     # one module only
python3 render_stl.py output ../docs/images/stl   # PNG previews of every printed part + parts-iso.png sheet (--all adds the check volumes)
```

## Firmware

```bash
cd firmware
arduino-cli core install rp2040:rp2040 --additional-urls https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
arduino-cli compile --fqbn rp2040:rp2040:seeed_xiao_rp2040 green_lantern
cd test && make test        # simulated interlock scenarios, all must PASS
```

## Credits and license

The lantern shape is derived from Hedo3D's "Green Lantern luminous" model
(https://cults3d.com/en/3d-model/game/green-lantern-luminous), licensed CC BY-NC 4.0.
This repository's derived CAD, firmware and documentation are for personal, non-commercial use
under the same terms. Green Lantern is a trademark of DC Comics; this is a fan-made costume prop.
