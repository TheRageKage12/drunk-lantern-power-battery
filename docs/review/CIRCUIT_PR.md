# Correct gate drive and sensor wiring; adopt the TalentCell battery

The existing circuit uses a logic buffer to drive MOSFET gates and places the driver/Hall supply after a
voltage-dropping diode. This revision gives the loads a dedicated gate driver, keeps sensor inputs at
3.3 V, and adds explicit decoupling and protection margins.

- Select the TalentCell YB1203000 (3000 mAh, 3 A maximum) in place of the KBT pack labelled 2 A;
  document its barrel lead, supplied charger and pack-switch requirements.
- Replace 74AHCT125 with TC4427CPA; add 47 Ω gate resistors, gate-source pull-downs and local bypass.
  Supply U1/Hall directly from the regulated 5 V rail; retain the Schottky only on the XIAO supply branch.
- Wire Hall OUT directly with a 3.3 V pull-up. Specify D2F-01L and add its contact-current resistor and
  diode-isolated GPIO input. Upgrade the bulk capacitor to 25 V and pump flyback diode to 3 A.
- Add removable JP1 for USB calibration supply isolation, explicit service sequencing and bench checks.
  Firmware changes are comments only; pin assignments and behavior stay the same.

**Scope:** CAD changes belong in a separate PR. Existing tray/deck exports still fit the old KBT pack.
The live shopping Sheet is unchanged; the edits below wait for acceptance and separate owner review.

## Updated circuit

![Updated circuit diagram](../images/wiring.png)

[Full-size SVG](../images/wiring.svg) · [Generator](../images/src/gen_wiring.py) · [Build instructions](../BUILD_GUIDE.md#4-electronics-build-it-on-the-bench-first)

## Spreadsheet edits after acceptance

Apply these deltas to the [shared Sheet](https://docs.google.com/spreadsheets/d/17pCjma48U2CBcsrsc3ZVFVb3nuV0KqnQlag0SO8B_yU/edit).
Row numbers refer to the reviewed sheet; match Item text before editing. Preserve ownership/purchase status,
update quantity-dependent formulas, and distinguish packs purchased from parts used.

| Existing row/item | Planned edit | Purpose / Notes |
|---|---|---|
| 33 — KBT battery | Replace with [TalentCell YB1203000](https://www.amazon.com/dp/B00MHNQIR2), $22.99, one kit. | 3000 mAh; 3 A max; 9–12.6 V; 105 × 65 × 25 mm. Supplied charger and splitter included. Pack switch ON to charge; CAD update pending. |
| 30 — D2F-L four-pack | Replace with [D2F-01L four-pack](https://www.amazon.com/dp/B0DBV9JX6L), $7.99; one used. | Fast candidate: Oct 14 Prime / Oct 18 standard displayed for Seattle on Oct 13. Pecafeitas listing; genuine Omron origin/contact material unverified. Confirm marking, fit and operation. |
| 3 — 74AHCT125 | Replace with **TC4427CPA, DIP-8**, one used; price/link pending. | Dual non-inverting driver. Resolve an acceptable Amazon/Vetco source and early delivery before ordering. |
| 12 — DIP-14 socket | Replace with [DIP-8 socket](https://vetco.net/products/8-pin-ic-socket-2-54mm-spacing-0-1), $1.24. | Matches U1; socket also permits removal for USB-only flashing. |
| 4 — MOSFET | Set Item to **IRLZ44NPBF**, retain quantity 2 and existing Vetco link. | Replace “IRLB8721 also fine” note: vendor URL/title stale; verify IRLZ44N marking; review substitutions. |
| 5 — NTE585 diodes | Reduce quantity **3 → 2**; add one [NTE586 3 A/40 V](https://vetco.net/products/nte586_40_volt_3a_schottky_rectifier_do27_-_nte586), $2.02. | NTE585: XIAO supply and twist signal. NTE586: pump flyback, stripe toward battery positive. |
| 6 — 10 kΩ resistors | Increase quantity **2 → 4** ($0.29 each). | Two input pull-downs plus two gate-source pull-downs. |
| New resistors | Add **2 × [47 Ω](https://vetco.net/products/nte-qw047_47_ohm_1-4_watt_resistor)**, **2 × [4.7 kΩ](https://vetco.net/products/nte-qw247_4-7k_ohm_1-4_watt_resistor)**, **1 × [3.3 kΩ](https://vetco.net/products/nte-qw233_3-3k_ohm_1-4_watt_resistor)**; $0.29 each. | Gate series, GPIO pull-ups to 3.3 V, and switch contact current respectively. |
| 9 — 0.1 µF capacitors | Increase quantity **2 → 3** ($0.25 each); add **1 × 1 µF X7R ceramic, ≥16 V**, price/link pending. | ADC, driver and Hall 0.1 µF; additional 1 µF at driver. Resolve Amazon/Vetco capacitor listing. |
| 10 — bulk capacitor | Replace 2200 µF/16 V with [2200 µF/25 V](https://vetco.net/products/2200uf25vdc_2200uf_25_volt_electrolytic_capacitor), $3.05. | More voltage margin, unchanged capacitance. |
| New — JP1 | Add one [breakaway header strip](https://vetco.net/products/40-pin-breakable-male-single-row-header-connector-pc-mount-0-1-spacing), $1.99 (two pins used), and one [2.54 mm shunt](https://vetco.net/products/vupn8912_0-1_-_2-54mm_shunt_-_jumper), $0.25. | Removable XIAO battery-feed link; label REMOVE FOR USB. Additional detail proposed in this PR. |

Known changes total **+$2.19 plus the full purchase cost of the new driver and 1 µF capacitor**, before
shipping/tax, using the observed prices above. Battery/switch changes offset each other. Reprice before
editing totals; do not retain the earlier DigiKey estimate or add a new supplier.

## Validation and remaining review

- Regenerated SVG and PNG; checked pin mapping, diode polarity, GPIO pull-up rails and component counts
  against the build guide and manufacturer references below. Diagram visually inspected.
- All **20 firmware simulation scenarios pass**. No executable firmware changes.
- Target compile not rerun: `arduino-cli` is unavailable. CAD intentionally unchanged; no CAD regeneration
  or fit claim for the new battery. Hardware current, temperature and startup checks await assembly.
- **Before ordering:** resolve early-delivery TC4427CPA and 1 µF capacitor sources, review the fast switch
  listing and the added JP1 service procedure/cost. This is a local draft, not a purchasing release.

References: [Microchip TC4427](https://ww1.microchip.com/downloads/en/DeviceDoc/20001422G.pdf),
[Omron D2F](https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2f.pdf),
[Seeed power/GPIO guidance](https://wiki.seeedstudio.com/XIAO-RP2040/),
[TalentCell specifications](https://talentcell.com/lithium-ion-battery/12v/yb1203000.html).
