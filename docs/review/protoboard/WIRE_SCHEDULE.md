# Perfboard wire and solder schedule

Generated from `layout.py`. Front coordinates are retained on the mirrored rear view.

## Cable attachments (solder side)

| Cable | Pad | Other end |
|---|---|---|
| H01 | N01 | S1 switched output |
| H02 | N02 | Battery negative / J1 sleeve |
| H03 | O01 | Buck IN+ |
| H04 | O02 | Buck IN− |
| H05 | P01 | Buck OUT+ (set to 5.0 V) |
| H06 | P02 | Buck OUT− |
| H07 | R01 | Pump + / D2 striped end |
| H08 | R02 | Pump − / D2 unstriped end |
| H09 | S01 | LED + (JST SM) |
| H10 | S02 | LED − (JST SM) |
| H11 | U08 | Lock +5 V: A3144 pin 1 / C4 |
| H12 | V08 | Lock HALL: A3144 pin 3 |
| H13 | W08 | Lock SW: microswitch NO |
| H14 | X08 | Lock GND: Hall pin 2 / COM / C4 |

## Every board wire

| Wire | From | To | Net | Construction |
|---|---|---|---|---|
| W01 | N01 | O01 | VLOAD | Bare adjacent-pad link |
| W02 | R01 | S01 | VLOAD | Bare adjacent-pad link |
| W03 | O01 | R01 | VLOAD | Insulated rear wire |
| W04 | H02 | N01 | VLOAD | Insulated rear wire |
| W05 | N02 | O02 | GND | Bare adjacent-pad link |
| W06 | O02 | P02 | GND | Bare adjacent-pad link |
| W07 | P02 | Q02 | GND | Bare adjacent-pad link |
| W08 | H04 | N02 | GND | Insulated rear wire |
| W09 | R10 | Q02 | GND | Insulated rear wire |
| W10 | R14 | P02 | GND | Insulated rear wire |
| W11 | L16 | O02 | GND | Insulated rear wire |
| W12 | B09 | L16 | GND | Insulated rear wire |
| W13 | B09 | B07 | GND | Insulated rear wire |
| W14 | B07 | B02 | GND | Insulated rear wire |
| W15 | J15 | M17 | GND | Insulated rear wire |
| W16 | M17 | M18 | GND | Insulated rear wire |
| W17 | J15 | O08 | GND | Insulated rear wire |
| W18 | M14 | M13 | GND | Insulated rear wire |
| W19 | M13 | M11 | GND | Insulated rear wire |
| W20 | M11 | M10 | GND | Insulated rear wire |
| W21 | J09 | M10 | GND | Insulated rear wire |
| W22 | J12 | M14 | GND | Insulated rear wire |
| W23 | O08 | M10 | GND | Insulated rear wire |
| W24 | X08 | O08 | GND | Insulated rear wire |
| W25 | P01 | N08 | 5V_REG | Insulated rear wire |
| W26 | N08 | M09 | 5V_REG | Insulated rear wire |
| W27 | N08 | U08 | 5V_REG | Insulated rear wire |
| W28 | U08 | U09 | 5V_REG | Insulated rear wire |
| W29 | P01 | N17 | 5V_REG | Insulated rear wire |
| W30 | Q17 | N18 | AFTER_D1 | Insulated rear wire |
| W31 | O18 | A09 | XIAO_5V | Insulated rear wire |
| W32 | C09 | V09 | 3V3 | Insulated rear wire |
| W33 | V09 | W09 | 3V3 | Insulated rear wire |
| W34 | A06 | B06 | ADC | Insulated rear wire |
| W35 | B06 | A07 | ADC | Insulated rear wire |
| W36 | A07 | A15 | ADC | Insulated rear wire |
| W37 | A02 | H02 | VLOAD | Insulated rear wire |
| W38 | V13 | V08 | HALL | Insulated rear wire |
| W39 | V13 | B15 | HALL | Insulated rear wire |
| W40 | W13 | C15 | TWIST | Insulated rear wire |
| W41 | W13 | W14 | TWIST | Insulated rear wire |
| W42 | U13 | W18 | SW | Insulated rear wire |
| W43 | U13 | W08 | SW | Insulated rear wire |
| W44 | D15 | J10 | PWM_P | Insulated rear wire |
| W45 | J10 | J17 | PWM_P | Insulated rear wire |
| W46 | E15 | J13 | PWM_L | Insulated rear wire |
| W47 | J13 | J18 | PWM_L | Insulated rear wire |
| W48 | J11 | P10 | GATE_P | Insulated rear wire |
| W49 | J14 | P14 | GATE_L | Insulated rear wire |
| W50 | Q10 | R02 | DRAIN_P | Insulated rear wire |
| W51 | Q14 | S02 | DRAIN_L | Insulated rear wire |
| W52 | L16 | J15 | GND | Insulated rear wire |

## Every component lead and attachment pad

For resistors/capacitors `.1` and `.2` are drawing lead IDs. C2.1 is +; C2.2 is −. For diodes, .1 is anode and .2 is striped cathode. U1 numbers are actual IC pin numbers.

| Lead | Pad | Net |
|---|---|---|
| MCU.5V | A09 | XIAO_5V |
| MCU.GND | B09 | GND |
| MCU.3V3 | C09 | 3V3 |
| MCU.D10 | D09 | NC_D10 |
| MCU.D9 | E09 | NC_D9 |
| MCU.D8 | F09 | NC_D8 |
| MCU.D7 | G09 | NC_D7 |
| MCU.D0 | A15 | ADC |
| MCU.D1 | B15 | HALL |
| MCU.D2 | C15 | TWIST |
| MCU.D3 | D15 | PWM_P |
| MCU.D4 | E15 | PWM_L |
| MCU.D5 | F15 | NC_D5 |
| MCU.D6 | G15 | NC_D6 |
| U1.1 | J09 | GND |
| U1.2 | J10 | PWM_P |
| U1.3 | J11 | GATE_P |
| U1.4 | J12 | GND |
| U1.5 | J13 | PWM_L |
| U1.6 | J14 | GATE_L |
| U1.7 | J15 | GND |
| U1.8 | M15 | NC_U8 |
| U1.9 | M14 | GND |
| U1.10 | M13 | GND |
| U1.11 | M12 | NC_U11 |
| U1.12 | M11 | GND |
| U1.13 | M10 | GND |
| U1.14 | M09 | 5V_REG |
| Q1.G | P10 | GATE_P |
| Q1.D | Q10 | DRAIN_P |
| Q1.S | R10 | GND |
| Q2.G | P14 | GATE_L |
| Q2.D | Q14 | DRAIN_L |
| Q2.S | R14 | GND |
| R1.1 | A02 | VLOAD |
| R1.2 | A06 | ADC |
| R2.1 | B02 | GND |
| R2.2 | B06 | ADC |
| R3.1 | J17 | PWM_P |
| R3.2 | M17 | GND |
| R4.1 | J18 | PWM_L |
| R4.2 | M18 | GND |
| R5.1 | V09 | 3V3 |
| R5.2 | V13 | HALL |
| R6.1 | W09 | 3V3 |
| R6.2 | W13 | TWIST |
| R7.1 | U09 | 5V_REG |
| R7.2 | U13 | SW |
| D1.1 | N17 | 5V_REG |
| D1.2 | Q17 | AFTER_D1 |
| D3.1 | W14 | TWIST |
| D3.2 | W18 | SW |
| C1.1 | A07 | ADC |
| C1.2 | B07 | GND |
| C3.1 | N08 | 5V_REG |
| C3.2 | O08 | GND |
| C2.1 | H02 | VLOAD |
| C2.2 | H04 | GND |
| JP1.1 | N18 | AFTER_D1 |
| JP1.2 | O18 | XIAO_5V |
| H01 | N01 | VLOAD |
| H02 | N02 | GND |
| H03 | O01 | VLOAD |
| H04 | O02 | GND |
| H05 | P01 | 5V_REG |
| H06 | P02 | GND |
| H07 | R01 | VLOAD |
| H08 | R02 | DRAIN_P |
| H09 | S01 | VLOAD |
| H10 | S02 | DRAIN_L |
| H11 | U08 | 5V_REG |
| H12 | V08 | HALL |
| H13 | W08 | SW |
| H14 | X08 | GND |
| BUS.GND | Q02 | GND |
| BUS.LOGIC | L16 | GND |
