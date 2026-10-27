# Perfboard wire and solder schedule

Generated from `layout.py`. Front coordinates are retained on the mirrored rear view.

## Cable attachments (solder side)

| Cable | Pad | Other end | Centre behind board |
|---|---|---|---|
| H01 | J01 | S1 switched output | 1 mm |
| H02 | N01 | Battery negative | 1 mm |
| H03 | K01 | Buck IN+ | 1 mm |
| H04 | O01 | Buck IN− | 1 mm |
| H05 | R01 | Buck OUT+ (set to 5.0 V) | 1 mm |
| H06 | P01 | Buck OUT− | 1 mm |
| H07 | L01 | Pump + / D2 striped end | 1 mm |
| H08 | T01 | Pump − / D2 unstriped end | 1 mm |
| H09 | M01 | LED harness + | 1 mm |
| H10 | U01 | LED harness − | 1 mm |
| H11 | S01 | Lock +5 V: A3144 pin 1 / C4 | 1 mm |
| H12 | V01 | Lock HALL: A3144 pin 3 | 1 mm |
| H13 | W01 | Lock SW: microswitch NO | 1 mm |
| H14 | Q01 | Lock GND: Hall pin 2 / COM / C4 | 1 mm |

## Every board wire

| Wire | From | To | Net | Construction |
|---|---|---|---|---|
| W01 | C13 | C15 | TWIST | Bare tinned link |
| W02 | D14 | D15 | PWM_P | Bare tinned link |
| W03 | I14 | F14 → E14 → E15 | PWM_L | Bare tinned link |
| W04 | X16 | X18 | SW | Bare tinned link |
| W05 | T02 | T01 | DRAIN_P | Bare tinned link |
| W06 | X06 | W06 → W03 → U03 → U01 | DRAIN_L | Bare tinned link |
| W07 | W02 | V02 → V01 | HALL | Bare tinned link |
| W08 | N01 | N04 | GND | Bare tinned link |
| W09 | O01 | O03 | GND | Bare tinned link |
| W10 | Q16 | Q17 | DRAIN_L | Bare tinned link |
| W11 | N01 | O01 | GND | Bare tinned link |
| W12 | O01 | P01 | GND | Bare tinned link |
| W13 | P01 | Q01 | GND | Bare tinned link |
| W14 | Q08 | Q09 → R09 | GND | Bare tinned link |
| W15 | Q01 | Q04 → Q07 → Q08 | GND | Bare tinned link |
| W16 | Q08 | O08 → O09 → M09 | GND | Bare tinned link |
| W17 | M09 | M10 | GND | Bare tinned link |
| W18 | L12 | M12 | GND | Bare tinned link |
| W19 | L11 | L12 | GND | Bare tinned link |
| W20 | L10 | L11 | GND | Bare tinned link |
| W21 | M10 | L10 | GND | Bare tinned link |
| W22 | M12 | M13 | GND | Bare tinned link |
| W23 | L11 | J11 | GND | Bare tinned link |
| W24 | L14 | J14 | GND | Bare tinned link |
| W25 | L12 | L14 | GND | Bare tinned link |
| W26 | M16 | N16 | GND | Bare tinned link |
| W27 | L14 | L16 → M16 | GND | Bare tinned link |
| W28 | M16 | M18 | GND | Bare tinned link |
| W29 | L10 | L08 → J08 | GND | Bare tinned link |
| W30 | J08 | I08 → I05 → I04 → F04 | GND | Bare tinned link |
| W31 | C04 | C01 | GND | Bare tinned link |
| W32 | F04 | C04 | GND | Bare tinned link |
| W33 | C04 | B04 → B07 | GND | Bare tinned link |
| W34 | B07 | B09 | GND | Bare tinned link |
| W35 | S03 | S01 | 5V_REG | Bare tinned link |
| W36 | T03 | S03 | 5V_REG | Bare tinned link |
| W37 | S01 | R01 | 5V_REG | Bare tinned link |
| W38 | R07 | R08 | 5V_REG | Bare tinned link |
| W39 | S03 | R03 → R06 → R07 | 5V_REG | Bare tinned link |
| W40 | R08 | S08 → S10 → P10 → P09 | 5V_REG | Bare tinned link |
| W41 | N08 | M08 | 5V_REG | Bare tinned link |
| W42 | R12 | R13 | GND | Bare tinned link |
| W43 | S16 | S17 → R17 | GND | Bare tinned link |
| W44 | I14 | I12 → J12 | PWM_L | Bare tinned link |
| W45 | I18 | I15 → I14 | PWM_L | Bare tinned link |
| W46 | N13 | P13 | GATE_P | Bare tinned link |
| W47 | J10 | K10 | GATE_P | Bare tinned link |
| W48 | J16 | J15 | PWM_P | Bare tinned link |
| W49 | D14 | D13 → G13 → G10 → I10 → I09 → J09 | PWM_P | Bare tinned link |
| W50 | J01 | K01 | VLOAD | Bare tinned link |
| W51 | K01 | L01 | VLOAD | Bare tinned link |
| W52 | L01 | M01 | VLOAD | Bare tinned link |
| W53 | J01 | G01 → G02 → F02 | VLOAD | Bare tinned link |
| W54 | B01 | A01 | VLOAD | Bare tinned link |
| W55 | F02 | F01 | VLOAD | Bare tinned link |
| W56 | A05 | A07 | ADC | Bare tinned link |
| W57 | A14 | A15 | ADC | Bare tinned link |
| W58 | A07 | A08 | ADC | Bare tinned link |
| W59 | C06 | C05 | ADC | Bare tinned link |
| W60 | A05 | A02 | ADC | Bare tinned link |
| W61 | P11 | S11 → T11 → T09 → V09 | 3V3 | Bare tinned link |
| W62 | C09 | C10 → D10 | 3V3 | Bare tinned link |
| W63 | V09 | X09 | 3V3 | Bare tinned link |
| W64 | O14 | R14 → U14 → X14 | TWIST | Bare tinned link |
| W65 | X14 | X13 | TWIST | Bare tinned link |
| W66 | V13 | W13 → W10 | HALL | Bare tinned link |
| W67 | F12 | C12 → B12 → B15 | HALL | Bare tinned link |
| W68 | V13 | U13 | HALL | Bare tinned link |
| W69 | X01 | W01 | SW | Bare tinned link |
| W70 | X01 | X03 | SW | Bare tinned link |
| W71 | C11 | B11 → B10 → A10 → A09 | XIAO_5V | Bare tinned link |
| W72 | H17 | H16 | XIAO_5V | Bare tinned link |
| W73 | O17 | P17 | GATE_L | Bare tinned link |
| W74 | J13 | K13 | GATE_L | Bare tinned link |
| W75 | N06 | O06 → O05 | DRAIN_P | Bare tinned link |
| W76 | Q13 | Q12 → N12 → N10 | DRAIN_P | Bare tinned link |
| W77 | U08 | W08 | AFTER_D1 | Bare tinned link |
| W78 | P15 | S15 → T15 | AFTER_D1 | Bare tinned link |
| W79 | G17 | G18 | AFTER_D1 | Bare tinned link |
| W80 | Q16 | X06 | DRAIN_L | Insulated; centre 6.0 mm behind board |
| W81 | N08 | R07 | 5V_REG | Insulated; centre 6.0 mm behind board |
| W82 | R12 | N04 | GND | Insulated; centre 9.0 mm behind board |
| W83 | S16 | O03 | GND | Insulated; centre 12.0 mm behind board |
| W84 | N13 | K10 | GATE_P | Insulated; centre 6.0 mm behind board |
| W85 | D14 | J15 | PWM_P | Insulated; centre 6.0 mm behind board |
| W86 | B01 | F01 | VLOAD | Insulated; centre 6.0 mm behind board |
| W87 | A14 | A08 | ADC | Insulated; centre 6.0 mm behind board |
| W88 | C06 | A02 | ADC | Insulated; centre 6.0 mm behind board |
| W89 | P11 | D10 | 3V3 | Insulated; centre 9.0 mm behind board |
| W90 | O14 | C13 | TWIST | Insulated; centre 9.0 mm behind board |
| W91 | W02 | W10 | HALL | Insulated; centre 9.0 mm behind board |
| W92 | F12 | U13 | HALL | Insulated; centre 9.0 mm behind board |
| W93 | X01 | X16 | SW | Insulated; centre 12.0 mm behind board |
| W94 | C11 | H16 | XIAO_5V | Insulated; centre 12.0 mm behind board |
| W95 | O17 | K13 | GATE_L | Insulated; centre 6.0 mm behind board |
| W96 | T02 | O05 | DRAIN_P | Insulated; centre 6.0 mm behind board |
| W97 | N06 | N10 | DRAIN_P | Insulated; centre 9.0 mm behind board |
| W98 | U08 | T15 | AFTER_D1 | Insulated; centre 12.0 mm behind board |
| W99 | P15 | G18 | AFTER_D1 | Insulated; centre 9.0 mm behind board |

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
| H01 | J01 | VLOAD |
| H02 | N01 | GND |
| H03 | K01 | VLOAD |
| H04 | O01 | GND |
| H05 | R01 | 5V_REG |
| H06 | P01 | GND |
| H07 | L01 | VLOAD |
| H08 | T01 | DRAIN_P |
| H09 | M01 | VLOAD |
| H10 | U01 | DRAIN_L |
| H11 | S01 | 5V_REG |
| H12 | V01 | HALL |
| H13 | W01 | SW |
| H14 | Q01 | GND |
| BUS.RETURN_P | N02 | GND |
| BUS.RETURN_L | O02 | GND |
| BUS.A02 | A02 | ADC |
| BUS.A03 | A03 | ADC |
| BUS.A04 | A04 | ADC |
| BUS.A06 | A06 | ADC |
| BUS.A08 | A08 | ADC |
| BUS.A10 | A10 | XIAO_5V |
| BUS.A14 | A14 | ADC |
| BUS.B01 | B01 | VLOAD |
| BUS.B04 | B04 | GND |
| BUS.B05 | B05 | GND |
| BUS.B06 | B06 | GND |
| BUS.B08 | B08 | GND |
| BUS.B10 | B10 | XIAO_5V |
| BUS.B11 | B11 | XIAO_5V |
| BUS.B12 | B12 | HALL |
| BUS.B13 | B13 | HALL |
| BUS.B14 | B14 | HALL |
| BUS.C02 | C02 | GND |
| BUS.C03 | C03 | GND |
| BUS.C04 | C04 | GND |
| BUS.C06 | C06 | ADC |
| BUS.C10 | C10 | 3V3 |
| BUS.C11 | C11 | XIAO_5V |
| BUS.C12 | C12 | HALL |
| BUS.C13 | C13 | TWIST |
| BUS.C14 | C14 | TWIST |
| BUS.D04 | D04 | GND |
| BUS.D10 | D10 | 3V3 |
| BUS.D12 | D12 | HALL |
| BUS.D13 | D13 | PWM_P |
| BUS.D14 | D14 | PWM_P |
| BUS.E04 | E04 | GND |
| BUS.E12 | E12 | HALL |
| BUS.E13 | E13 | PWM_P |
| BUS.E14 | E14 | PWM_L |
| BUS.F01 | F01 | VLOAD |
| BUS.F12 | F12 | HALL |
| BUS.F13 | F13 | PWM_P |
| BUS.F14 | F14 | PWM_L |
| BUS.G01 | G01 | VLOAD |
| BUS.G02 | G02 | VLOAD |
| BUS.G04 | G04 | GND |
| BUS.G10 | G10 | PWM_P |
| BUS.G11 | G11 | PWM_P |
| BUS.G12 | G12 | PWM_P |
| BUS.G13 | G13 | PWM_P |
| BUS.G14 | G14 | PWM_L |
| BUS.G18 | G18 | AFTER_D1 |
| BUS.H01 | H01 | VLOAD |
| BUS.H04 | H04 | GND |
| BUS.H10 | H10 | PWM_P |
| BUS.H14 | H14 | PWM_L |
| BUS.H16 | H16 | XIAO_5V |
| BUS.I01 | I01 | VLOAD |
| BUS.I04 | I04 | GND |
| BUS.I05 | I05 | GND |
| BUS.I06 | I06 | GND |
| BUS.I07 | I07 | GND |
| BUS.I08 | I08 | GND |
| BUS.I09 | I09 | PWM_P |
| BUS.I10 | I10 | PWM_P |
| BUS.I12 | I12 | PWM_L |
| BUS.I13 | I13 | PWM_L |
| BUS.I14 | I14 | PWM_L |
| BUS.I15 | I15 | PWM_L |
| BUS.I16 | I16 | PWM_L |
| BUS.I17 | I17 | PWM_L |
| BUS.J15 | J15 | PWM_P |
| BUS.K08 | K08 | GND |
| BUS.K10 | K10 | GATE_P |
| BUS.K11 | K11 | GND |
| BUS.K13 | K13 | GATE_L |
| BUS.K14 | K14 | GND |
| BUS.L08 | L08 | GND |
| BUS.L09 | L09 | GND |
| BUS.L10 | L10 | GND |
| BUS.L11 | L11 | GND |
| BUS.L12 | L12 | GND |
| BUS.L13 | L13 | GND |
| BUS.L14 | L14 | GND |
| BUS.L15 | L15 | GND |
| BUS.L16 | L16 | GND |
| BUS.M16 | M16 | GND |
| BUS.M17 | M17 | GND |
| BUS.N03 | N03 | GND |
| BUS.N04 | N04 | GND |
| BUS.N06 | N06 | DRAIN_P |
| BUS.N08 | N08 | 5V_REG |
| BUS.N09 | N09 | GND |
| BUS.N10 | N10 | DRAIN_P |
| BUS.N11 | N11 | DRAIN_P |
| BUS.N12 | N12 | DRAIN_P |
| BUS.N13 | N13 | GATE_P |
| BUS.O03 | O03 | GND |
| BUS.O05 | O05 | DRAIN_P |
| BUS.O06 | O06 | DRAIN_P |
| BUS.O08 | O08 | GND |
| BUS.O09 | O09 | GND |
| BUS.O12 | O12 | DRAIN_P |
| BUS.O13 | O13 | GATE_P |
| BUS.O14 | O14 | TWIST |
| BUS.O17 | O17 | GATE_L |
| BUS.P08 | P08 | GND |
| BUS.P10 | P10 | 5V_REG |
| BUS.P11 | P11 | 3V3 |
| BUS.P12 | P12 | DRAIN_P |
| BUS.P14 | P14 | TWIST |
| BUS.P15 | P15 | AFTER_D1 |
| BUS.Q02 | Q02 | GND |
| BUS.Q03 | Q03 | GND |
| BUS.Q04 | Q04 | GND |
| BUS.Q05 | Q05 | GND |
| BUS.Q06 | Q06 | GND |
| BUS.Q07 | Q07 | GND |
| BUS.Q08 | Q08 | GND |
| BUS.Q09 | Q09 | GND |
| BUS.Q10 | Q10 | 5V_REG |
| BUS.Q11 | Q11 | 3V3 |
| BUS.Q12 | Q12 | DRAIN_P |
| BUS.Q14 | Q14 | TWIST |
| BUS.Q15 | Q15 | AFTER_D1 |
| BUS.Q16 | Q16 | DRAIN_L |
| BUS.R03 | R03 | 5V_REG |
| BUS.R04 | R04 | 5V_REG |
| BUS.R05 | R05 | 5V_REG |
| BUS.R06 | R06 | 5V_REG |
| BUS.R07 | R07 | 5V_REG |
| BUS.R10 | R10 | 5V_REG |
| BUS.R11 | R11 | 3V3 |
| BUS.R12 | R12 | GND |
| BUS.R14 | R14 | TWIST |
| BUS.R15 | R15 | AFTER_D1 |
| BUS.S02 | S02 | 5V_REG |
| BUS.S03 | S03 | 5V_REG |
| BUS.S08 | S08 | 5V_REG |
| BUS.S09 | S09 | 5V_REG |
| BUS.S10 | S10 | 5V_REG |
| BUS.S11 | S11 | 3V3 |
| BUS.S14 | S14 | TWIST |
| BUS.S15 | S15 | AFTER_D1 |
| BUS.S16 | S16 | GND |
| BUS.S17 | S17 | GND |
| BUS.T02 | T02 | DRAIN_P |
| BUS.T09 | T09 | 3V3 |
| BUS.T10 | T10 | 3V3 |
| BUS.T11 | T11 | 3V3 |
| BUS.T14 | T14 | TWIST |
| BUS.T15 | T15 | AFTER_D1 |
| BUS.U02 | U02 | DRAIN_L |
| BUS.U03 | U03 | DRAIN_L |
| BUS.U08 | U08 | AFTER_D1 |
| BUS.U09 | U09 | 3V3 |
| BUS.U13 | U13 | HALL |
| BUS.U14 | U14 | TWIST |
| BUS.V02 | V02 | HALL |
| BUS.V03 | V03 | DRAIN_L |
| BUS.V08 | V08 | AFTER_D1 |
| BUS.V14 | V14 | TWIST |
| BUS.W02 | W02 | HALL |
| BUS.W03 | W03 | DRAIN_L |
| BUS.W04 | W04 | DRAIN_L |
| BUS.W05 | W05 | DRAIN_L |
| BUS.W06 | W06 | DRAIN_L |
| BUS.W09 | W09 | 3V3 |
| BUS.W10 | W10 | HALL |
| BUS.W11 | W11 | HALL |
| BUS.W12 | W12 | HALL |
| BUS.W13 | W13 | HALL |
| BUS.W14 | W14 | TWIST |
| BUS.X01 | X01 | SW |
| BUS.X02 | X02 | SW |
| BUS.X06 | X06 | DRAIN_L |
| BUS.X16 | X16 | SW |
| BUS.X17 | X17 | SW |
