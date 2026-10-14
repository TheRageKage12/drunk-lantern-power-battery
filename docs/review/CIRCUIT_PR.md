# Revise the battery, gate drive and sensor circuits

Update the electronics plan with a higher-current battery, a dedicated MOSFET driver, revised Hall and
twist-switch inputs, stronger pump protection and a removable USB power-isolation link. The PR includes
the connected circuit diagram (SVG, PNG and generator), matching build and test instructions, updated
firmware wiring comments, and the proposed shopping-list edits below.

## Circuit changes and why

- **Battery:** replace the 2400 mAh KBT pack labelled 2 A with the 3000 mAh, 3 A TalentCell YB1203000
  for more current headroom and capacity. Document the new barrel lead, charger and pack-switch operation.
- **Gate drive:** replace the 74AHCT125 logic buffer and DIP-14 socket with a TC4427CPA dual gate driver
  and DIP-8 socket. Add a 47 Ω series resistor and 10 kΩ gate-to-source pull-down to each MOSFET to
  limit switching transients and hold an undriven gate off. Retain the two driver-input pull-downs and
  specify IRLZ44NPBF as the required MOSFET.
- **5 V supply and bypass:** correct the diagram so U1 and the Hall sensor receive the buck's full 5 V
  before the XIAO supply diode. Explicitly draw U1's 0.1 µF bypass, add 1 µF alongside it, and add 0.1 µF
  at the Hall sensor to reduce local supply disturbances.
- **Hall input:** remove the series diode and connect the A3144's open-collector output directly to
  GPIO D1, with a 4.7 kΩ pull-up to 3.3 V. This gives a defined input voltage without the diode's voltage drop.
- **Twist input:** replace D2F-L with D2F-01L for low-current switching. Add a 3.3 kΩ resistor from 5 V
  to the switch contact, a diode with its stripe toward switch NO, and a 4.7 kΩ GPIO pull-up to 3.3 V.
  This supplies contact current while keeping GPIO D2 isolated from 5 V.
- **Protection:** increase C2's voltage rating from 16 V to 25 V, keeping 2200 µF, and replace the pump's
  1 A NTE585 flyback diode with a 3 A/40 V NTE586 for more voltage and current margin, respectively.
- **USB servicing:** add removable JP1 after the XIAO supply diode. Removing it isolates the battery
  feed during USB use. Document USB-only flashing with socketed U1 removed and the power sequence for
  calibration with U1 installed.

The diagram shows these changes in **one connected schematic**, including every used GPIO, driver pin,
added resistor and capacitor. Visible wires, junction dots and crossing bridges make the connections
traceable; the existing optional PRIME button is now drawn explicitly.

![Updated circuit diagram](../images/wiring.png)

[Full-size SVG](../images/wiring.svg) · [Generator](../images/src/gen_wiring.py)

The [build guide](../BUILD_GUIDE.md#4-electronics-build-it-on-the-bench-first) explains setting the buck to
5.0 V before connecting electronics, battery/charging wiring, USB servicing, and bench checks for GPIO
levels, startup behavior, load current and heating. README and review notes reflect the revised parts
and pending cost/fit checks. Firmware changes are comments only; behavior and GPIO assignments are unchanged.
Battery CAD changes are deferred to a separate PR; the existing supports still fit the old KBT pack.

## Spreadsheet edits after acceptance

The [shared Sheet](https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit)
remains unchanged. Apply these edits after PR acceptance and separate owner review. Match rows by item,
preserve purchase/ownership status and update quantity-dependent totals. Prices below were checked October 13.

| Row / item | Planned edit | Notes |
|---|---|---|
| 33 — Battery | Replace with one [TalentCell YB1203000 kit](https://www.amazon.com/dp/B00MHNQIR2), $22.99. | 3000 mAh, 3 A; 105 × 65 × 25 mm. |
| 30 — Microswitch | Replace with [D2F-01L four-pack](https://www.amazon.com/dp/B0DBV9JX6L), $7.99; one used. | Marketplace candidate; see sourcing below. |
| 3 — Driver | Replace 74AHCT125 with **TC4427CPA, DIP-8**, quantity 1. | Source/price pending. |
| 12 — IC socket | Replace DIP-14 with [DIP-8 socket](https://vetco.net/products/8-pin-ic-socket-2-54mm-spacing-0-1), $1.24. | Fits new driver. |
| 4 — MOSFETs | Specify **IRLZ44NPBF**, quantity 2; keep Vetco link. | Remove “IRLB8721 also fine” note. |
| 5 — Diodes | NTE585: **3 → 2**. Add one [NTE586, 3 A/40 V](https://vetco.net/products/nte586_40_volt_3a_schottky_rectifier_do27_-_nte586), $2.02. | NTE586 replaces pump flyback diode. |
| 6 — 10 kΩ resistors | Quantity **2 → 4**, $0.29 each. | Add two gate pull-downs. |
| New — Resistors | Add **2 × [47 Ω](https://vetco.net/products/nte-qw047_47_ohm_1-4_watt_resistor)**, **2 × [4.7 kΩ](https://vetco.net/products/nte-qw247_4-7k_ohm_1-4_watt_resistor)** and **1 × [3.3 kΩ](https://vetco.net/products/nte-qw233_3-3k_ohm_1-4_watt_resistor)**; $0.29 each. | Gates, GPIO pull-ups, switch contact. |
| 9 — Ceramic capacitors | 0.1 µF: **2 → 3**, $0.25 each. Add **1 × 1 µF X7R, ≥16 V**. | 1 µF source/price pending. |
| 10 — Bulk capacitor | Replace 2200 µF/16 V with [2200 µF/25 V](https://vetco.net/products/2200uf25vdc_2200uf_25_volt_electrolytic_capacitor), $3.05. | Same capacitance, higher voltage rating. |
| New — JP1 | Add [header strip](https://vetco.net/products/40-pin-breakable-male-single-row-header-connector-pc-mount-0-1-spacing), $1.99, and [shunt](https://vetco.net/products/vupn8912_0-1_-_2-54mm_shunt_-_jumper), $0.25. | Two header pins used; REMOVE FOR USB. |

Known price changes total **+$2.19, plus the new driver and 1 µF capacitor**, before tax/shipping.
Recheck prices before updating totals.

**Sourcing still open:** find TC4427CPA and 1 µF capacitor listings from Amazon or Vetco with timely
delivery. The switch candidate showed October 14 Prime / October 18 standard delivery to Seattle on
October 13; its claimed Omron origin is unverified. JP1 and its service procedure are additional details
proposed for review in this PR.

## Validation

- SVG/PNG regenerated and visually checked; pin mapping, diode polarity, pull-up rails and component
  counts checked against the build guide and references below.
- All 20 firmware simulation scenarios passed. Target compilation was not rerun (`arduino-cli` unavailable).
- No CAD changes or new-battery fit verification. Electrical measurements await assembly.

References: [Microchip TC4427](https://ww1.microchip.com/downloads/en/DeviceDoc/20001422G.pdf),
[Omron D2F](https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2f.pdf),
[Seeed power/GPIO guidance](https://wiki.seeedstudio.com/XIAO-RP2040/),
[TalentCell specifications](https://talentcell.com/lithium-ion-battery/12v/yb1203000.html).
