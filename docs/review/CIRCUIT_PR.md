# Revise the battery, gate drive and sensor circuits

Revise the power and control circuit to give the pump and lighting more current headroom, improve
MOSFET switching, and make ring/twist detection more reliable. Update the connected circuit diagram
and [build instructions](../BUILD_GUIDE.md#4-electronics-build-it-on-the-bench-first) to match.

## Circuit changes and why

| Circuit | Change | Why |
|---|---|---|
| Battery | KBT 2400 mAh / 2 A → TalentCell YB1203000, 3000 mAh / 3 A. | More current headroom and capacity. |
| Gate drive | 74AHCT125 → TC4427CPA; add 47 Ω gate resistors and 10 kΩ gate-to-source pull-downs. | Faster gate charging reduces switching losses; resistors damp oscillations and hold undriven gates off. |
| 5 V supply | Move driver and Hall feeds ahead of the XIAO supply diode in the diagram. | Give both the full regulated 5 V without the diode's voltage drop. |
| Driver capacitors | Draw the existing required 0.1 µF capacitor; add 1 µF beside it. | Correct the missing diagram detail and support brief gate-charging current pulses. |
| Hall sensor | Add local 0.1 µF bypass; remove output diode; add 4.7 kΩ pull-up to 3.3 V. | Reduce supply noise and obtain a defined GPIO signal without an unnecessary diode drop. |
| Twist switch | D2F-L → D2F-01L; add 3.3 kΩ from 5 V to the contact, an isolating diode, and 4.7 kΩ GPIO pull-up to 3.3 V. | Use contacts intended for small signals and supply enough contact current for reliable detection while keeping 5 V off the GPIO. |
| Protection | Bulk capacitor: 2200 µF/16 V → 2200 µF/25 V. Pump flyback diode: 1 A NTE585 → 3 A/40 V NTE586. | More capacitor voltage margin and more diode current margin during motor switch-off. |
| USB power | Add removable JP1 in the XIAO battery feed; remove it during USB use. | Prevent the battery supply from feeding the USB connection. |

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
| 3 — Driver | Replace with [TC4427CPA, DIP-8 ten-pack](https://www.amazon.com/dp/B0992V3MNM), **$21.00**; one used. | PCComponentsCompany; delivery Oct 21. |
| 12 — IC socket | Replace DIP-14 with [DIP-8 socket](https://vetco.net/products/8-pin-ic-socket-2-54mm-spacing-0-1), $1.24. | Fits new driver. |
| 4 — MOSFETs | Specify **IRLZ44NPBF**, quantity 2; keep Vetco link. | Remove “IRLB8721 also fine” note. |
| 5 — Diodes | NTE585: **3 → 2**. Add one [NTE586, 3 A/40 V](https://vetco.net/products/nte586_40_volt_3a_schottky_rectifier_do27_-_nte586), $2.02. | NTE586 replaces pump flyback diode. |
| 6 — 10 kΩ resistors | Quantity **2 → 4**, $0.29 each. | Add two gate pull-downs. |
| New — Resistors | Add **2 × [47 Ω](https://vetco.net/products/nte-qw047_47_ohm_1-4_watt_resistor)**, **2 × [4.7 kΩ](https://vetco.net/products/nte-qw247_4-7k_ohm_1-4_watt_resistor)** and **1 × [3.3 kΩ](https://vetco.net/products/nte-qw233_3-3k_ohm_1-4_watt_resistor)**; $0.29 each. | Gates, GPIO pull-ups, switch contact. |
| 9 — Ceramic capacitors | 0.1 µF: **2 → 3**, $0.25 each. Add one [Multicomp MCMLR50V105KX7R, 1 µF/50 V X7R](https://www.amazon.com/dp/B005S3O6L8), **$1.50 + $4.95 shipping**. | Radial leads; salefolks; delivery Oct 23. |
| 10 — Bulk capacitor | Replace 2200 µF/16 V with [2200 µF/25 V](https://vetco.net/products/2200uf25vdc_2200uf_25_volt_electrolytic_capacitor), $3.05. | Same capacitance, higher voltage rating. |
| New — JP1 | Add [header strip](https://vetco.net/products/40-pin-breakable-male-single-row-header-connector-pc-mount-0-1-spacing), $1.99, and [shunt](https://vetco.net/products/vupn8912_0-1_-_2-54mm_shunt_-_jumper), $0.25. | Two header pins used; REMOVE FOR USB. |

These selections put the parts increase at **$24.69**, plus the capacitor's **$4.95 shipping**, tax and
any other shipping charges. Delivery dates are Amazon's October 13 estimates for Seattle; the capacitor
also advertises October 19–21 with faster shipping (additional charge not shown).
