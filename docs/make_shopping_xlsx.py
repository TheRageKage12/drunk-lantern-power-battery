"""Write docs/SHOPPING_LIST.xlsx: the shopping list as an editable spreadsheet (opens in Excel; File > Import in
Google Sheets). Same items, prices and links as SHOPPING_LIST.md; edit either, but keep them in step.

    python3 docs/make_shopping_xlsx.py
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SHOPPING_LIST.xlsx')
AMZ = 'https://www.amazon.com/dp/'
VET = 'https://vetco.net/products/'
TAC = 'https://www.tacomascrew.com/Product/'

# (store, needed, qty, item, link, unit price, price is an estimate, notes)
ROWS = [
    ('Amazon', 'Required', 1, 'Pump: Kamoer KPHM200, 12 V', AMZ + 'B09HGVLHFV', 28.00, False, 'Prime, Oct 15'),
    ('Amazon', 'Required', 1, 'Tubing: Auber 1/8" ID x 1/4" OD platinum silicone, 10 ft (exactly this size)', AMZ + 'B0DKB1NKB4', 13.99, False, 'Prime, Oct 14. Only 4 left'),
    ('Amazon', 'Required', 1, 'Battery: KBT 12 V 2400 mAh, 70 x 55 x 40 mm, bare leads, with charger', AMZ + 'B0C241NS29', 21.99, False, 'Prime, Oct 14. Pick the 2400 mAh bare-leads variant'),
    ('Amazon', 'Required', 1, 'Microcontroller: Seeed XIAO RP2040, pre-soldered', AMZ + 'B0DRNTQ338', 10.99, False, 'Prime, Oct 14'),
    ('Amazon', 'Required', 1, 'Lever microswitch D2F-L, 4-pack', AMZ + 'B0DBV8XGG4', 8.99, False, 'Prime, Oct 14'),
    ('Amazon', 'Required', 1, 'LED strip: HAMRVL green COB, 12 V, 8 mm, 5 m', AMZ + 'B0CKYFLZFQ', 14.99, False, 'Prime, Oct 14'),
    ('Amazon', 'Required', 1, 'Buck converter LM2596, 5-pack', AMZ + 'B0DBVYP91F', 7.99, False, 'Prime, Oct 14'),
    ('Amazon', 'Required', 1, 'Magnets 6 x 2 mm, 45 pcs', AMZ + 'B0CBRVF4PN', 6.29, False, 'Prime, Oct 14'),
    ('Amazon', 'Required', 1, 'Vent valve: AQUANEAT aquarium check valve, 10 pcs (1 used)', AMZ + 'B086JRH4WS', 4.79, False, 'Prime, Oct 14. Or 1 from a pet store aquarium aisle. Its barb goes through its own ~5 mm hole in the jar lid'),
    ('Vetco', 'Required', 1, 'A3144 Hall sensor', VET + 'vupn6596_hall-effect_sensor_-_allegro_a3144eua_d63', 1.99, False, ''),
    ('Vetco', 'Required', 1, '74AHCT125 (must be AHCT)', VET + 'vupn524_quad_level-shifter_-_74ahct125_-_3v_to_5v_d96', 2.95, False, ''),
    ('Vetco', 'Required', 2, 'IRLZ44N MOSFET', VET + 'vupn1682_mosfet_mosft_for_micro_controllers_-_30v_-_60a_-_irlb8721pbf_d151', 2.67, False, 'IRLB8721 also fine'),
    ('Vetco', 'Required', 1, 'SPST mini toggle switch with leads (1/4" bushing)', VET + '30-10005_spst_miniature_toggle_switch_w-wire_leads_on-off_6a', 4.95, False, ''),
    ('Vetco', 'Required', 1, '2.1 mm DC panel jack (8 mm hole)', VET + '2112_2-1mm_dc_power_panel_mount_jack', 2.88, False, ''),
    ('Vetco', 'Required', 3, '1N5819-type Schottky diode (NTE585)', VET + 'nte585_40_volt_1a_schottky_rectifier_do41_-_nte585', 0.94, False, ''),
    ('Vetco', 'Required', 2, '10 k resistor', VET + 'nte-qw310_10k_ohm_1-4_watt_resistor', 0.29, False, ''),
    ('Vetco', 'Required', 1, '100 k resistor', VET + 'nte-qw410_100k_ohm_1-4_watt_resistor', 0.29, False, ''),
    ('Vetco', 'Required', 1, '22 k resistor', VET + 'nte-qw322_22k_ohm_1-4_watt_resistor', 0.29, False, ''),
    ('Vetco', 'Required', 2, '0.1 µF ceramic capacitor', VET + 'vupn6606_ceramic_capacitor_0-1_uf_-2080_50_volts_z5u', 0.25, False, ''),
    ('Vetco', 'Required', 1, '2200 µF 16 V capacitor', VET + '2200uf16vdc_2200uf_16_volt_electrolytic_capacitor', 2.80, False, ''),
    ('Vetco', 'Required', 1, '5 x 7 cm protoboard', VET + 'phenolic-protoboard-1-97-x-2-76-inch', 3.49, False, 'Drill 4 x 3.2 mm holes on 40 x 30 mm'),
    ('Vetco', 'Required', 1, '14-pin IC socket', VET + '14-pin-ic-socket-2-54mm-spacing-0-1', 1.95, False, ''),
    ('Vetco', 'Required', 1, '22 AWG stranded wire', VET + 'hookup_wire_stranded_22_ga', 5.37, False, ''),
    ('Vetco', 'Required', 1, '1/8" heat-shrink, 4 ft', VET + '1-8_heat_shrink_tubing_4_long', 1.69, False, ''),
    ('Vetco', 'Required', 1, 'Lock cable plug: JST PH 4-pin pair, pre-wired', VET + 'jst-ph-2-0-4-pin-connector-male-female-pair-pre-wired', 2.24, False, ''),
    ('Vetco', 'Required', 1, 'LED lead plug: JST SM 2-pin locking pair', VET + 'vupn1054_jst_sm_2_pin_m-f_pair_locking_connector', 1.75, False, ''),
    ('Tacoma Screw', 'Required', 4, 'M3 x 6 socket head', TAC + '223-306-3', 0.20, True, 'Sold by the piece in store'),
    ('Tacoma Screw', 'Required', 17, 'M3 x 8 socket head', TAC + '223-308-3', 0.20, True, ''),
    ('Tacoma Screw', 'Required', 8, 'M3 x 8 flat head (countersunk)', TAC + '224-308-4', 0.20, True, '4 go under the lock plate; not in the Amazon kit'),
    ('Tacoma Screw', 'Required', 6, 'M3 x 10 socket head', TAC + '223-310-3', 0.20, True, ''),
    ('Tacoma Screw', 'Required', 11, 'M3 x 12 socket head', TAC + '223-312-3', 0.20, True, ''),
    ('Tacoma Screw', 'Required', 14, 'M3 hex nut', TAC + '231-003-1', 0.20, True, ''),
    ('Ace Hardware', 'Required', 1, 'Compression spring ~0.4-0.5 mm wire, 5 mm OD, ~10 mm long (cut longer ones)', '', 1.50, True, 'Hillman spring drawer; bring calipers. A pen spring works but is softer'),
    ('Local', 'Required', 1, 'Jar, food-safe, drillable lid: max 73 mm across with lid, 76 mm tall', 'https://www.microhomebrew.com/', 5.00, True, 'Micro Homebrew, Kenmore, (425) 892-8425'),
    ('Local', 'Required', 1, 'Curtain sheet: clear-frosted polypropylene divider or report cover, 0.3-0.5 mm', '', 3.00, True, 'Target, Fred Meyer, Office Depot. Must say polypropylene, not PVC/vinyl'),
    ('Local', 'Required', 1, 'Shot glass 1.5 oz: max 52 mm across the top, 62 mm tall', 'https://www.bargreen.com/locations/seattle', 4.00, True, 'Bargreen Ellingson SoDo, Mon-Fri 10-3. Heavy base helps'),
    ('Amazon', 'If needed', 2, 'Green PETG 1 kg (Creality); parts need ~1.2 kg', AMZ + 'B0D4MBDL8B', 13.99, False, 'Free delivery Oct 18'),
    ('Amazon', 'If needed', 1, 'White PETG 1 kg (Overture), diffusers ~30 g', AMZ + 'B07PDV9RC8', 14.99, False, 'Prime, Oct 14'),
    ('Amazon', 'If needed', 1, 'Soldering iron kit, 80 W LCD', AMZ + 'B08R3515SF', 9.96, False, 'Prime, Oct 14'),
    ('Amazon', 'If needed', 1, 'Multimeter, AstroAI 2000-count', AMZ + 'B01ISAMUA6', 14.39, False, 'Prime, Oct 14'),
    ('Amazon', 'If needed', 1, 'Digital calipers, Adoric 0-6"', AMZ + 'B07DFFYCXS', 8.99, False, 'Prime, Oct 14'),
    ('Amazon', 'If needed', 1, 'Drill bits, metric 1.5-10 mm, 15-piece cobalt (3.2, 5, 6 mm used)', AMZ + 'B07B7L6WVY', 22.99, False, 'Prime, Oct 14'),
    ('Amazon', 'If needed', 1, 'Flush cutters, KATA mini', AMZ + 'B07VGK8GBL', 5.39, False, 'Prime, Oct 14'),
    ('Hardware store', 'If needed', 1, 'Hook-and-loop straps 20 mm (2-3) and ~10 small zip ties', '', 5.00, True, 'Skip if you have them'),
]

STORES = [
    ('Amazon', 'amazon.com', '', 'One order; prices and delivery dates read 2026-10-13'),
    ('Vetco', '12718 Northup Way STE 100, Bellevue', '(425) 641-7275', 'Mon-Fri 9-6, Sat 10-3:30'),
    ('Tacoma Screw', '3930 Leary Way NW, Seattle (Ballard)', '(206) 632-7565', 'Mon-Fri 7-5, Sat 9-1. Fallback: Amazon M3 kit B0HKFCTLK8 ($8.99) covers all but the 8 flat heads'),
    ('Ace Hardware', 'Magnolia, Maple Leaf, West Seattle Junction', '', 'Hillman spring drawer'),
    ('Local', 'Micro Homebrew (Kenmore), Target / Fred Meyer / Office Depot, Bargreen Ellingson (SoDo)', '', 'Jar, curtain sheet, shot glass'),
]
ALREADY_HAVE = ['Super glue (Gorilla Glue)', 'Silicone grease or petroleum jelly (lock)',
                'Hex keys 2 and 2.5 mm (long or ball-end 2.5)', 'USB-C data cable', 'Kitchen scale or measuring cup']

F = 'Arial'
HEAD = Font(name=F, bold=True, color='FFFFFF')
HEAD_FILL = PatternFill('solid', fgColor='2E7D32')
INPUT = Font(name=F, color='0000FF')
BODY = Font(name=F)
BOLD = Font(name=F, bold=True)
THIN = Border(bottom=Side(style='thin', color='DDDDDD'))
MONEY = '$#,##0.00'

wb = Workbook()
ws = wb.active
ws.title = 'Shopping list'
cols = ['Bought?', 'Store', 'Needed', 'Qty', 'Item', 'Link', 'Unit price', 'Line total', 'Price is estimate', 'Notes']
widths = [10, 15, 11, 6, 62, 16, 11, 11, 10, 60]
for i, (c, w) in enumerate(zip(cols, widths), 1):
    cell = ws.cell(row=1, column=i, value=c)
    cell.font, cell.fill = HEAD, HEAD_FILL
    cell.alignment = Alignment(vertical='center', wrap_text=True)
    ws.column_dimensions[cell.column_letter].width = w
ws.freeze_panes = 'A2'

first = 2
for r, (store, need, qty, item, link, price, est, notes) in enumerate(ROWS, first):
    ws.cell(r, 1, 'No').font = INPUT
    ws.cell(r, 2, store).font = BODY
    ws.cell(r, 3, need).font = BODY
    ws.cell(r, 4, qty).font = INPUT
    ws.cell(r, 5, item).font = BODY
    if link:
        c = ws.cell(r, 6, f'=HYPERLINK("{link}","open listing")')
        c.font = Font(name=F, color='0563C1', underline='single')
    p = ws.cell(r, 7, price); p.font = INPUT; p.number_format = MONEY
    t = ws.cell(r, 8, f'=D{r}*G{r}'); t.font = BODY; t.number_format = MONEY
    ws.cell(r, 9, 'Yes' if est else 'No').font = BODY
    ws.cell(r, 10, notes).font = BODY
    for c in range(1, 11):
        ws.cell(r, c).border = THIN
        ws.cell(r, c).alignment = Alignment(vertical='top', wrap_text=c in (5, 10))
last = first + len(ROWS) - 1

dv = DataValidation(type='list', formula1='"Yes,No"', allow_blank=False)
ws.add_data_validation(dv); dv.add(f'A{first}:A{last}')
ws.conditional_formatting.add(f'A{first}:J{last}', FormulaRule(formula=[f'$A{first}="Yes"'],
                              fill=PatternFill('solid', fgColor='E8F5E9'), font=Font(name=F, color='888888')))

# summary to the right of nothing: below the table
s = last + 2
ws.cell(s, 5, 'Totals (update automatically)').font = BOLD
summary = [('Amazon, required', f'=SUMIFS(H{first}:H{last},B{first}:B{last},"Amazon",C{first}:C{last},"Required")'),
           ('Vetco', f'=SUMIFS(H{first}:H{last},B{first}:B{last},"Vetco")'),
           ('Tacoma Screw (estimate)', f'=SUMIFS(H{first}:H{last},B{first}:B{last},"Tacoma Screw")'),
           ('Ace and local (estimate)', f'=SUMIFS(H{first}:H{last},B{first}:B{last},"Ace Hardware")+SUMIFS(H{first}:H{last},B{first}:B{last},"Local")'),
           ('Total, required', f'=SUMIFS(H{first}:H{last},C{first}:C{last},"Required")'),
           ('Optional filament and tools', f'=SUMIFS(H{first}:H{last},C{first}:C{last},"If needed")'),
           ('Still to buy (required, Bought? = No)', f'=SUMIFS(H{first}:H{last},C{first}:C{last},"Required",A{first}:A{last},"No")'),
           ('Spent so far (Bought? = Yes)', f'=SUMIFS(H{first}:H{last},A{first}:A{last},"Yes")')]
for i, (label, f) in enumerate(summary, s + 1):
    ws.cell(i, 5, label).font = BOLD if label.startswith('Total') else BODY
    c = ws.cell(i, 8, f); c.number_format = MONEY; c.font = BOLD if label.startswith('Total') else BODY
n = s + len(summary) + 2
ws.cell(n, 5, 'How to use: set Bought? to Yes as you go (the row greys out). Blue cells are inputs: edit Qty or '
              'Unit price and the totals follow. "Price is estimate" = Yes marks the store and local prices that are guesses.').font = Font(name=F, italic=True, color='555555')
ws.cell(n, 5).alignment = Alignment(wrap_text=True)
ws.row_dimensions[n].height = 45

st = wb.create_sheet('Stores')
for i, (h, w) in enumerate(zip(['Store', 'Where', 'Phone', 'Hours / notes'], [16, 60, 16, 80]), 1):
    c = st.cell(1, i, h); c.font, c.fill = HEAD, HEAD_FILL
    st.column_dimensions[c.column_letter].width = w
for r, row in enumerate(STORES, 2):
    for i, v in enumerate(row, 1):
        c = st.cell(r, i, v); c.font = BODY; c.alignment = Alignment(wrap_text=True, vertical='top')
r = len(STORES) + 3
st.cell(r, 1, 'Already have').font = BOLD
for k, v in enumerate(ALREADY_HAVE, r + 1):
    st.cell(k, 1, '•').font = BODY
    st.cell(k, 2, v).font = BODY

wb.save(OUT)
print('wrote', OUT, f'({len(ROWS)} rows)')
