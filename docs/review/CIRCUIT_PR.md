# Revise the battery, gate drive and sensor circuits

Revise the power and control circuit to give the pump and lighting more current headroom, improve
MOSFET switching, and make ring/twist detection more reliable. Update the connected circuit diagram
and [build instructions](../BUILD_GUIDE.md#4-electronics-build-it-on-the-bench-first) to match.

## Circuit changes and why

- **Battery:** replace the 2400 mAh, 2 A KBT pack with the 3000 mAh, 3 A TalentCell YB1203000 for
  more current headroom and capacity.
- **Gate drive:** replace the 74AHCT125 logic buffer with a TC4427CPA gate driver. The driver can
  charge and discharge the MOSFET gates faster, reducing the time spent partially on and the associated
  heating. Add 47 Ω gate resistors to damp switching oscillations and 10 kΩ gate-to-source pull-downs
  to hold the pump and lights off when the driver is not driving them.
- **5 V wiring:** move the driver and Hall sensor supply connections ahead of the XIAO supply diode
  in the diagram. They need the buck's full 5 V; the diode's voltage drop should affect only the XIAO branch.
- **Local capacitors:** draw the driver's 0.1 µF bypass capacitor that was already required by the build
  guide but missing from the diagram. Also add two new capacitors: 1 µF beside the driver to support its
  brief gate-charging current pulses, and 0.1 µF at the Hall sensor to reduce supply noise at the end of its cable.
- **Hall input:** remove the series diode and connect the A3144 output directly to GPIO D1 with a
  4.7 kΩ pull-up to 3.3 V. The sensor's open-collector output already pulls the signal to ground without
  feeding 5 V into the GPIO; the diode adds an unnecessary voltage drop.
- **Twist input:** replace D2F-L with D2F-01L, which is intended for low-current signals. The weak GPIO
  pull-up alone supplies too little contact current for its specified operating conditions. Add a 3.3 kΩ
  resistor from 5 V to supply about 1.5 mA through closed contacts, improving reliable switch detection.
  A diode blocks that 5 V from the GPIO, whose own 4.7 kΩ pull-up keeps its signal at 3.3 V.
- **Protection:** change the 2200 µF capacitor from 16 V to 25 V for more voltage margin, and replace
  the pump's 1 A flyback diode with a 3 A/40 V NTE586 for more current margin when the motor switches off.
- **USB power:** add removable JP1 in the XIAO's battery supply branch. Remove it for programming or
  calibration over USB to prevent the battery supply from feeding the USB connection. The build guide
  covers the accompanying driver power sequence.

Battery CAD changes belong in a separate PR. Firmware behavior and GPIO assignments are unchanged.

![Updated circuit diagram](../images/wiring.png)

[Full-size SVG](../images/wiring.svg) · [Generator](../images/src/gen_wiring.py)

## Spreadsheet edits after acceptance

The [shared Sheet](https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit)
will be updated after PR acceptance and separate owner review. Each replacement or added item will get
its purchase link, quantity and current price, and the affected totals will be recalculated. Existing
purchase/ownership status will be preserved. Prices below are the October 13 estimates.

| Row / item | Planned edit | Notes |
|---|---|---|
| 33 — Battery | Replace with one [TalentCell YB1203000 kit](https://www.amazon.com/dp/B00MHNQIR2), $22.99. | 3000 mAh, 3 A; 105 × 65 × 25 mm. |
| 30 — Microswitch | Replace with [D2F-01L four-pack](https://www.amazon.com/dp/B0DBV9JX6L), $7.99; one used. | Seller’s claimed Omron origin unverified. |
| 3 — Driver | Replace 74AHCT125 with **TC4427CPA, DIP-8**, quantity 1. | Source/price pending. |
| 12 — IC socket | Replace DIP-14 with [DIP-8 socket](https://vetco.net/products/8-pin-ic-socket-2-54mm-spacing-0-1), $1.24. | Fits new driver. |
| 4 — MOSFETs | Specify **IRLZ44NPBF**, quantity 2; keep Vetco link. | Remove “IRLB8721 also fine” note. |
| 5 — Diodes | NTE585: **3 → 2**. Add one [NTE586, 3 A/40 V](https://vetco.net/products/nte586_40_volt_3a_schottky_rectifier_do27_-_nte586), $2.02. | NTE586 replaces pump flyback diode. |
| 6 — 10 kΩ resistors | Quantity **2 → 4**, $0.29 each. | Add two gate pull-downs. |
| New — Resistors | Add **2 × [47 Ω](https://vetco.net/products/nte-qw047_47_ohm_1-4_watt_resistor)**, **2 × [4.7 kΩ](https://vetco.net/products/nte-qw247_4-7k_ohm_1-4_watt_resistor)** and **1 × [3.3 kΩ](https://vetco.net/products/nte-qw233_3-3k_ohm_1-4_watt_resistor)**; $0.29 each. | Gates, GPIO pull-ups, switch contact. |
| 9 — Ceramic capacitors | 0.1 µF: **2 → 3**, $0.25 each. Add **1 × 1 µF X7R, ≥16 V**. | 1 µF source/price pending. |
| 10 — Bulk capacitor | Replace 2200 µF/16 V with [2200 µF/25 V](https://vetco.net/products/2200uf25vdc_2200uf_25_volt_electrolytic_capacitor), $3.05. | Same capacitance, higher voltage rating. |
| New — JP1 | Add [header strip](https://vetco.net/products/40-pin-breakable-male-single-row-header-connector-pc-mount-0-1-spacing), $1.99, and [shunt](https://vetco.net/products/vupn8912_0-1_-_2-54mm_shunt_-_jumper), $0.25. | Two header pins used; REMOVE FOR USB. |

The new driver and 1 µF capacitor are specified in this circuit, but we have not yet selected Amazon or
Vetco listings with suitable delivery dates. Their purchase links and prices must be filled in to complete
the shopping-list changes and calculate the revised total.
