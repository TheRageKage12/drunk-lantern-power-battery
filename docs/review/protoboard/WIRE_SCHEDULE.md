# Perfboard wire and solder schedule

Generated from `layout.py`. Front coordinates are retained on the mirrored rear view.

## Cable attachments (solder side)

| Cable | Pad | Other end | Centre behind board |
|---|---|---|---|
| H01 | N01 | S1 switched output | 5.6 mm |
| H02 | N02 | Battery negative | 8.2 mm |
| H03 | O01 | Buck IN+ | 5.6 mm |
| H04 | O02 | Buck IN− | 8.2 mm |
| H05 | P09 | Buck OUT+ (set to 5.0 V) | 3 mm |
| H06 | P02 | Buck OUT− | 5.6 mm |
| H07 | R01 | Pump + / D2 striped end | 3 mm |
| H08 | Q13 | Pump − / D2 unstriped end | 8.2 mm |
| H09 | S01 | LED harness + | 3 mm |
| H10 | Q17 | LED harness − | 5.6 mm |
| H11 | T03 | Lock +5 V: A3144 pin 1 / C4 | 3 mm |
| H12 | V13 | Lock HALL: A3144 pin 3 | 8.2 mm |
| H13 | X03 | Lock SW: microswitch NO | 3 mm |
| H14 | I05 | Lock GND: Hall pin 2 / COM / C4 | 3 mm |

## Every board wire

| Wire | From | To | Net | Construction |
|---|---|---|---|---|
| W01 | N01 | O01 | VLOAD | Bare tinned link |
| W02 | R01 | S01 | VLOAD | Bare tinned link |
| W03 | O01 | R01 | VLOAD | Bare tinned link |
| W04 | F02 | I02 | VLOAD | Bare tinned link |
| W05 | N02 | O02 | GND | Bare tinned link |
| W06 | O02 | P02 | GND | Bare tinned link |
| W07 | P02 | Q02 | GND | Bare tinned link |
| W08 | F04 | I03 | GND | Bare tinned link |
| W09 | R13 | Q02 | GND | Insulated; centre 3.0 mm behind board |
| W10 | R17 | P02 | GND | Insulated; centre 8.2 mm behind board |
| W11 | I08 | I05 | GND | Bare tinned link |
| W12 | A01 | F02 | VLOAD | Insulated; centre 3.0 mm behind board |
| W13 | M10 | M09 | GND | Bare tinned link |
| W14 | M13 | M12 | GND | Bare tinned link |
| W15 | B09 | B07 | GND | Bare tinned link |
| W16 | M12 | N12 | GND | Bare tinned link |
| W17 | I14 | I16 | GND | Bare tinned link |
| W18 | N16 | M18 | GND | Bare tinned link |
| W19 | I08 | I11 | GND | Bare tinned link |
| W20 | I11 | I14 | GND | Bare tinned link |
| W21 | J08 | M09 | GND | Bare tinned link |
| W22 | M13 | N13 | GND | Bare tinned link |
| W23 | M09 | R09 | GND | Insulated; centre 3.0 mm behind board |
| W24 | C01 | B07 | GND | Insulated; centre 8.2 mm behind board |
| W25 | B09 | J08 | GND | Insulated; centre 8.2 mm behind board |
| W27 | R08 | P09 | 5V_REG | Bare tinned link |
| W29 | M08 | P09 | 5V_REG | Bare tinned link |
| W31 | T03 | R03 | 5V_REG | Bare tinned link |
| W32 | W08 | G17 | AFTER_D1 | Insulated; centre 3.0 mm behind board |
| W33 | A09 | H17 | XIAO_5V | Insulated; centre 8.2 mm behind board |
| W34 | V09 | X09 | 3V3 | Bare tinned link |
| W35 | C09 | V09 | 3V3 | Insulated; centre 5.6 mm behind board |
| W36 | A05 | A07 | ADC | Bare tinned link |
| W37 | A05 | C05 | ADC | Bare tinned link |
| W38 | A15 | A07 | ADC | Insulated; centre 5.6 mm behind board |
| W40 | B15 | V13 | HALL | Insulated; centre 5.6 mm behind board |
| W41 | X13 | X14 | TWIST | Bare tinned link |
| W42 | C15 | X14 | TWIST | Insulated; centre 5.6 mm behind board |
| W44 | X03 | X18 | SW | Insulated; centre 8.2 mm behind board |
| W45 | D15 | J16 | PWM_P | Insulated; centre 5.6 mm behind board |
| W46 | J09 | D15 | PWM_P | Insulated; centre 3.0 mm behind board |
| W47 | J12 | I18 | PWM_L | Insulated; centre 8.2 mm behind board |
| W48 | E15 | J12 | PWM_L | Insulated; centre 3.0 mm behind board |
| W49 | J10 | P13 | GATE_P | Insulated; centre 3.0 mm behind board |
| W50 | J13 | P17 | GATE_L | Insulated; centre 8.2 mm behind board |
| W53 | J08 | I08 | GND | Bare tinned link |
| W54 | J11 | I11 | GND | Bare tinned link |
| W55 | J14 | I14 | GND | Bare tinned link |
| W56 | I02 | L01 | VLOAD | Bare tinned link |
| W57 | L01 | N01 | VLOAD | Bare tinned link |
| W58 | I03 | L02 | GND | Bare tinned link |
| W59 | L02 | N02 | GND | Bare tinned link |
| W60 | R03 | R05 | 5V_REG | Bare tinned link |
| W61 | R05 | R08 | 5V_REG | Bare tinned link |
| W62 | I05 | I03 | GND | Bare tinned link |
| W63 | N12 | N10 | GND | Bare tinned link |
| W64 | N10 | M10 | GND | Bare tinned link |
| W65 | N13 | N16 | GND | Bare tinned link |

## Every component lead and attachment pad

For resistors/capacitors `.1` and `.2` are drawing lead IDs. C2.1 is +; C2.2 is −. For diodes, .1 is anode and .2 is striped cathode. U1 numbers are actual IC pin numbers.

| Lead | Pad | Net |
|---|---|---|
| BUS.GN13 | N13 | GND |
| BUS.GN12 | N12 | GND |
| BUS.GN10 | N10 | GND |
| BUS.G05 | I05 | GND |
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
| U1.1 | J08 | GND |
| U1.2 | J09 | PWM_P |
| U1.3 | J10 | GATE_P |
| U1.4 | J11 | GND |
| U1.5 | J12 | PWM_L |
| U1.6 | J13 | GATE_L |
| U1.7 | J14 | GND |
| U1.8 | M14 | NC_U8 |
| U1.9 | M13 | GND |
| U1.10 | M12 | GND |
| U1.11 | M11 | NC_U11 |
| U1.12 | M10 | GND |
| U1.13 | M09 | GND |
| U1.14 | M08 | 5V_REG |
| Q1.G | P13 | GATE_P |
| Q1.D | Q13 | DRAIN_P |
| Q1.S | R13 | GND |
| Q2.G | P17 | GATE_L |
| Q2.D | Q17 | DRAIN_L |
| Q2.S | R17 | GND |
| R1.1 | A01 | VLOAD |
| R1.2 | A05 | ADC |
| R2.1 | C01 | GND |
| R2.2 | C05 | ADC |
| R3.1 | J16 | PWM_P |
| R3.2 | N16 | GND |
| R4.1 | I18 | PWM_L |
| R4.2 | M18 | GND |
| R5.1 | V09 | 3V3 |
| R5.2 | V13 | HALL |
| R6.1 | X09 | 3V3 |
| R6.2 | X13 | TWIST |
| R7.1 | T03 | 5V_REG |
| R7.2 | X03 | SW |
| D1.1 | R08 | 5V_REG |
| D1.2 | W08 | AFTER_D1 |
| D3.1 | X14 | TWIST |
| D3.2 | X18 | SW |
| C1.1 | A07 | ADC |
| C1.2 | B07 | GND |
| C3.1 | P09 | 5V_REG |
| C3.2 | R09 | GND |
| C2.1 | F02 | VLOAD |
| C2.2 | F04 | GND |
| JP1.1 | G17 | AFTER_D1 |
| JP1.2 | H17 | XIAO_5V |
| H01 | N01 | VLOAD |
| H02 | N02 | GND |
| H03 | O01 | VLOAD |
| H04 | O02 | GND |
| H06 | P02 | GND |
| H07 | R01 | VLOAD |
| H09 | S01 | VLOAD |
| BUS.GND | Q02 | GND |
| BUS.G08 | I08 | GND |
| BUS.G11 | I11 | GND |
| BUS.G14 | I14 | GND |
| BUS.V02 | I02 | VLOAD |
| BUS.V01 | L01 | VLOAD |
| BUS.G03 | I03 | GND |
| BUS.G02 | L02 | GND |
| BUS.FIVE03 | R03 | 5V_REG |
| BUS.FIVE05 | R05 | 5V_REG |
| BUS.LOGIC | I16 | GND |
