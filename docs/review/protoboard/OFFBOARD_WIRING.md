# Outgoing wires and enclosure cut plan

The nine **H wire IDs are wire labels, not hole names**. Each board step attaches one end only. Keep the free end insulated and label it; connect it during cap-floor assembly. Use the existing insulated stranded 22 AWG. No printed parts change.

## Board leads — cut these during the guide

| Wire label | Colour | Cut | Connect the free end later |
|---|---|---:|---|
| H01 · Battery-positive lead | red | **250 mm** | Switched battery-positive join |
| H02 · Controller ground lead | black | **190 mm** | Common ground join |
| H03 · Pump ground lead | black | **170 mm** | Common ground join |
| H04 · LED ground lead | black | **260 mm** | Common ground join |
| H05 · Pump negative lead | blue | **400 mm** | Pump-lead join at the cap opening |
| H06 · LED negative lead | yellow | **440 mm** | LED-lead join at the cap opening |
| H07 · 5 V supply lead | white | **190 mm** | 5 V join |
| H08 · Twist-switch signal lead | yellow | **220 mm** | 4-pin lock connector · switch signal |
| H09 · Hall-sensor signal lead | green | **230 mm** | 4-pin lock connector · Hall signal |

The pump and LED leads stop at sleeved joins beside the cap-floor opening; they do **not** reach the pump or LED strips by themselves. The signal leads stop at the cap-side **existing 4-pin lock connector**. Keep the existing 2-pin pump connector at the cartridge. Use continuity to match connector wires; do not rely on their insulation colours.

## Separate wires for later enclosure assembly

These are additional pieces, not extra length to add to the board cuts above. Cut the stated length for **each** colour. At prewired plugs, retain the connector pigtails and trim the new wire to meet them, keeping the slack specified below.

| Piece | Colours | Cut each | Route / destination |
|---|---|---:|---|
| Pump positive cap lead | red | **275 mm** | J_LOAD to matching lead at cap opening |
| LED positive cap lead | red | **300 mm** | J_LOAD to matching lead at cap opening |
| Lock 5 V cap lead | white | **125 mm** | J_5V to 4-pin lock plug |
| Lock ground cap lead | black | **125 mm** | J_GND to 4-pin lock plug |
| Pump trunk | red, blue | **525 mm** | Existing 2-pin pump plug at the cartridge |
| LED trunk | red, yellow | **225 mm** | LED common + and − behind the lock wall |
| Lock cable | white, black, yellow, green | **300 mm** | Existing 4-pin plug to the Hall sensor and microswitch |

1. Keep J_LOAD (switched battery +), J_GND (ground), and J_5V (regulated 5 V) as three separate insulated joins in the wall-side lane beside the board. The map places them along that lane: J_LOAD toward S1, J_5V toward the buck, ground between them.
2. At the cap opening, join the blue board lead to the blue pump trunk and the red pump cap lead to its red trunk. Join yellow to yellow and red to red for the LED pair. Sleeve each splice separately. Retain 150 mm of slack in **each cap-side pump and LED lead**, loosely coiled beside the opening; do not fold it beneath the board.
3. The lock connector remains beside the opening. Its cap side receives Hall signal (green board lead), twist signal (yellow board lead), 5 V (white), and ground (black). Pass the separate four-wire lock cable down through the opening and behind the wall extension. At the lock, white goes to Hall pin 1, black to pin 2 and switch COM, green to Hall pin 3, yellow to switch NO. Leave switch NC unused.
4. The pump pair runs down behind the wall, through the existing 7 mm bay-floor cable hole at (35, −32), then through the foot to the pump plug. Twist red/blue loosely together. Keep the lower 75 mm allowance near the plug so it can be reached and unplugged before lifting the lantern off the cartridge. D2 remains across the pump terminals.
5. The LED pair stops at the common LED wiring behind the upper lock wall. All LED negatives join yellow; all positives join red. The individual LED-strip branch wiring is unchanged.
6. Keep the lock wiring separate from the pump pair below the cap opening. Leave 60 mm slack in the lock cable and 30 mm at the LED join. Route everything on the display side of the wall, clear of the glass, nozzle and moving lock parts.

## Basis of the cut lengths

CAD references: `cad/params.py`, `cad/parts/top.py` (`board_point`, cap floor and wire opening), `cad/parts/sphere.py` (wall and bay-floor cable hole), and the pump plug envelope in `cad/parts/electronics.py`. Route definitions and arithmetic live in `offboard.py`.
The cap floor is at Z=366.57 mm and the rim at Z=440.57 mm. Two M3 nuts per post put the board component face at Z=382.57 mm. The existing 150 mm service allowance exceeds twice the 74.0 mm floor-to-rim rise.
Board cuts = existing formed board portion and its solder/trim stock + planned cap-lane travel + slack + 8 mm for the far-end connection + 20 mm fitting/trim allowance, rounded **up** to 10 mm. Lower-run cuts use CAD waypoints, the stated slack, two 8 mm ends and 20 mm trim stock, rounded up to 25 mm. Square-corner distances conservatively allow room to form smooth bends. Do not make sharp creases at the drawn corners.
The clearance check reserves 28 × 28 × 18 mm for the pump/LED slack loops beside the opening, above the lock connector, outside the board footprint.
The 20 mm trim stock is removed at final fitting; it is not another loop to store. These are cutting blanks based on the planned layout, not measurements of the delivered connector pigtails. Position the printed parts and connectors as shown, then trim only the excess while retaining the designated service slack.

| Board lead | Board portion + stock | Cap-lane travel | Slack | End + trim | Cut |
|---|---:|---:|---:|---:|---:|
| H01 | 145 | 55.2 | 20 | 28 | 250 mm |
| H02 | 112 | 28.2 | 20 | 28 | 190 mm |
| H03 | 81 | 33.2 | 20 | 28 | 170 mm |
| H04 | 191 | 14.2 | 20 | 28 | 260 mm |
| H05 | 117 | 95.8 | 150 | 28 | 400 mm |
| H06 | 175 | 81.6 | 150 | 28 | 440 mm |
| H07 | 126 | 11.2 | 20 | 28 | 190 mm |
| H08 | 87 | 81.2 | 20 | 28 | 220 mm |
| H09 | 90 | 88.2 | 20 | 28 | 230 mm |

H06 turns inward above the cap-floor thumbscrew head before descending. Its former straight drop was too close to that head. This changes only the free wire bend, not the PCB holes or printed parts.
