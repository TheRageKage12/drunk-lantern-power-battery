"""Relocated components and dedicated stranded-wire holes; printed mounts stay fixed."""
from pathlib import Path
import json
DESIGN=json.loads(Path(__file__).with_name('design.json').read_text())
COLS='ABCDEFGHIJKLMNOPQRSTUVWX'
PITCH=2.54
ORIGIN=(5.79,3.41)
MOUNTS=DESIGN['hardware']['mounts']
PINS=DESIGN['pins']
PARTS=[dict(ref=ref,kind=kind,value=value,a=PINS[ref+'.1']['pad'],b=PINS[ref+'.2']['pad'])
       for ref,kind,value in [
           ('R1','resistor','100k'),('R2','resistor','22k'),
           ('R3','resistor','10k'),('R4','resistor','10k'),
           ('R5','resistor','4.7k'),('R6','resistor','4.7k'),('R7','resistor','3.3k'),
           ('D1','diode','NTE585'),('D3','diode','NTE585'),
           ('C1','ceramic','0.1uF'),('C3','ceramic','0.1uF'),
           ('C2','electrolytic','2200uF/25V'),('JP1','jumper','REMOVE FOR USB')]]
WIRES=[e for e in DESIGN['edges'] if e['b']]
HARNESS=[(e['id'],e['a'],e['net'],DESIGN['cables'][e['id']]) for e in DESIGN['edges'] if not e['b']]
NETS={'3V3': ('#8d36b7', '3.3 V'),
 '5V_REG': ('#d12b36', 'Regulated 5 V'),
 'ADC': ('#19826b', 'Battery sense'),
 'AFTER_D1': ('#db546b', 'D1 → JP1'),
 'DRAIN_L': ('#a63261', 'LED return'),
 'DRAIN_P': ('#146c79', 'Pump return'),
 'GATE_L': ('#75621a', 'LED gate'),
 'GATE_P': ('#9e5819', 'Pump gate'),
 'GND': ('#334155', 'Ground'),
 'HALL': ('#419626', 'Hall signal'),
 'PWM_L': ('#2887a6', 'LED PWM'),
 'PWM_P': ('#1763c0', 'Pump PWM'),
 'SW': ('#b660a0', 'Switch contact'),
 'TWIST': ('#9a3b92', 'Twist GPIO'),
 'VLOAD': ('#b96500', 'Switched battery'),
 'XIAO_5V': ('#b31845', 'JP1 → XIAO 5V')}
def cr(pad):return COLS.index(pad[0]),int(pad[1:])-1
def mm(pad):
    c,r=cr(pad);return ORIGIN[0]+c*PITCH,ORIGIN[1]+r*PITCH
