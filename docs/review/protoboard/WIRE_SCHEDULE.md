# Board solder schedule

Generated from `design.json`. Hole names are assigned from the component side. The rear view is mirrored.

| Wire | Solder points in order | Colour | Starting cut |
|---|---|---|---|
| W01 | P17 → Q15 → T16 → S18 | white | 45 mm |
| W04 | A08 → B10 → A15 → A13 | black | 74 mm |
| W07 | I13 → G13 → G08 → F10 | black | 74 mm |
| W15 | P07 → P09 → S03 → R03 | green | 78 mm |
| W25 | M03 → M02 → S02 → S01 | yellow | 67 mm |
| W16 | O07 → O09 → V08 → V09 | yellow | 100 mm |
| W22 | H07 → G05 → I03 → I02 | white | 42 mm |
| H03 | W03 → W01 | black | 92 mm + measured external run |
| H08 | N02 → M02 | yellow | 98 mm + measured external run |
| W05 | A16 → A13 → B08 → C10 | black | 99 mm |
| W10 | D08 → E10 → D15 → D13 | black | 68 mm |
| H09 | R04 → R03 | green | 101 mm + measured external run |
| W23 | H02 → I02 → I10 → G10 | white | 62 mm |
| H05 | V03 → V01 | blue | 128 mm + measured external run |
| W13 | Q07 → Q09 → B05 → C05 | yellow | 104 mm |
| W24 | B01 → A01 → G02 → F02 | red | 70 mm |
| W19 | M07 → M09 → C15 → C13 | blue | 92 mm |
| W12 | N04 → N03 → R07 → R09 | green | 74 mm |
| W14 | E04 → C05 → A06 → A05 | yellow | 74 mm |
| W06 | B07 → C10 → I12 → G13 | black | 96 mm |
| W09 | O17 → P15 → C08 → E10 | black | 116 mm |
| W26 | L06 → L05 → P18 → R18 | white | 83 mm |
| W21 | B15 → B13 → I14 → H16 | blue | 104 mm |
| W02 | G03 → F04 → D01 → C01 | black | 86 mm |
| W03 | E01 → C01 → A07 → B10 | black | 102 mm |
| W17 | W08 → V09 → M01 → N01 | yellow | 115 mm |
| H02 | F03 → F04 | black | 123 mm + measured external run |
| W08 | H08 → F10 → O18 → P15 | black | 113 mm |
| H04 | J18 → H18 | black | 202 mm + measured external run |
| H07 | G04 → G05 | white | 137 mm + measured external run |
| H01 | E02 → F02 | red | 156 mm + measured external run |
| W18 | N07 → N09 → F15 → F13 | blue | 133 mm |
| W11 | N17 → O15 → S07 → R09 | green | 119 mm |
| W20 | E15 → E13 → U03 → U01 | blue | 133 mm |
| H06 | J17 → H17 | yellow | 189 mm + measured external run |
| C2_1 | F02 → C2.1 | red | 55 mm |
| C2_2 | F04 → C2.2 | black | 70 mm |

## Power harness

- **J_LOAD:** S1.OUT, H01, BUCK.IN+, PUMP.+, LED.+.
- **J_GND:** BATTERY.-, BUCK.IN-, H02, H03, H04, LOCK.GND.
- **J_5V:** BUCK.OUT+, H07, LOCK.5V.

Buck IN− and OUT− must have continuity; only IN− gets a separate return wire. Pump and LED source returns join logic ground only at J_GND. D2 stays at the pump; C4 at the Hall sensor.

## Component leads

| Lead | Hole or existing joint | Connection |
|---|---|---|
| MCU.5V | Q15 | XIAO_5V |
| MCU.GND | P15 | GND |
| MCU.3V3 | O15 | 3V3 |
| MCU.D10 | N15 | NC_D10 |
| MCU.D9 | M15 | NC_D9 |
| MCU.D8 | L15 | NC_D8 |
| MCU.D7 | K15 | NC_D7 |
| MCU.D0 | Q09 | ADC |
| MCU.D1 | P09 | HALL |
| MCU.D2 | O09 | TWIST |
| MCU.D3 | N09 | PWM_P |
| MCU.D4 | M09 | PWM_L |
| MCU.D5 | L09 | NC_D5 |
| MCU.D6 | K09 | NC_D6 |
| U1.1 | G13 | GND |
| U1.2 | F13 | PWM_P |
| U1.3 | E13 | GATE_P |
| U1.4 | D13 | GND |
| U1.5 | C13 | PWM_L |
| U1.6 | B13 | GATE_L |
| U1.7 | A13 | GND |
| U1.8 | A10 | NC_U8 |
| U1.9 | B10 | GND |
| U1.10 | C10 | GND |
| U1.11 | D10 | NC_U11 |
| U1.12 | E10 | GND |
| U1.13 | F10 | GND |
| U1.14 | G10 | 5V_REG |
| Q1.G | U01 | GATE_P |
| Q1.D | V01 | DRAIN_P |
| Q1.S | W01 | GND |
| Q2.G | H16 | GATE_L |
| Q2.D | H17 | DRAIN_L |
| Q2.S | H18 | GND |
| R1.1 | A01 | VLOAD |
| R1.2 | A05 | ADC |
| R2.1 | C01 | GND |
| R2.2 | C05 | ADC |
| R3.1 | F13 | PWM_P |
| R3.2 | G13 | GND |
| R4.1 | C13 | PWM_L |
| R4.2 | D13 | GND |
| R5.1 | N03 | 3V3 |
| R5.2 | R03 | HALL |
| R6.1 | R09 | 3V3 |
| R6.2 | V09 | TWIST |
| R7.1 | I02 | 5V_REG |
| R7.2 | M02 | SW |
| D1.1 | G05 | 5V_REG |
| D1.2 | L05 | AFTER_D1 |
| D3.1 | N01 | TWIST |
| D3.2 | S01 | SW |
| C1.1 | C05 | ADC |
| C1.2 | C01 | GND |
| C3.1 | G10 | 5V_REG |
| C3.2 | A13 | GND |
| C2.1 | F02 | VLOAD |
| C2.2 | F04 | GND |
| JP1.1 | R18 | AFTER_D1 |
| JP1.2 | S18 | XIAO_5V |
