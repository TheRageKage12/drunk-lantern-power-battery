# Green Lantern power battery that pours a shot

A Halloween prop: a 3D-printed Green Lantern power battery (about 480 mm tall, 180 mm diameter)
with a hidden peristaltic pump, a hidden shot glass, and a twist-to-pour ring socket.
Insert the ring, recite the oath, twist the ring 45 degrees on the last line, and the lantern
flashes and fills the glass while the light show runs.

Start here: **[docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md)** (parts list with links, printing,
assembly, wiring, firmware, calibration, testing, cleaning).

## Repository map

| Path | What it is |
|---|---|
| `docs/BUILD_GUIDE.md` | The build guide. |
| `docs/images/` | Wiring, fluid path, state machine, socket mechanism diagrams and CAD renders. |
| `docs/research/` | Research notes behind every decision (pump, power, lighting, electronics, mechanical, Seattle sourcing, design critique), the project brief, and the original ChatGPT transcript. |
| `cad/` | Parametric CadQuery model. `params.py` holds every dimension; `parts/*.py` build the parts; `python3 build.py` exports `cad/output/*.stl` and `*.step`, an assembly, and runs fit checks. See `cad/README.md` and `cad/DESIGN_CONTRACT.md`. |
| `cad/output/` | Ready-to-slice STL files (and STEP files) for every printed part. |
| `firmware/green_lantern/` | Arduino sketch for the Seeed XIAO RP2040. |
| `firmware/test/` | Host-side simulation of the firmware interlocks (`make test`). |
| `original-model/` | The stock lantern this design scales up: Hedo3D "Green Lantern luminous" (Cults3D #40633), CC BY-NC 4.0. Kept for reference and for the ring. |

## Regenerating the CAD

```bash
pip install cadquery trimesh manifold3d numpy pillow networkx scipy
cd cad
python3 build.py            # all parts -> cad/output/, assembly, checks
python3 build.py socket     # one module only
python3 render_stl.py output /tmp/renders   # PNG previews of every STL
```

## Firmware

```bash
cd firmware
arduino-cli core install rp2040:rp2040 --additional-urls https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
arduino-cli lib install "Adafruit NeoPixel"
arduino-cli compile --fqbn rp2040:rp2040:seeed_xiao_rp2040 green_lantern
cd test && make test        # simulated interlock scenarios, all must PASS
```

## Credits and license

The lantern shape is derived from Hedo3D's "Green Lantern luminous" model
(https://cults3d.com/en/3d-model/game/green-lantern-luminous), licensed CC BY-NC 4.0.
This repository's derived CAD, firmware and documentation are for personal, non-commercial use
under the same terms. Green Lantern is a trademark of DC Comics; this is a fan-made costume prop.
