"""Explicit perfboard placement and point-to-point wiring; component-side coordinates.
Run generate.py to validate the connectivity and render both faces.
"""
COLS='ABCDEFGHIJKLMNOPQRSTUVWX'
PITCH=2.54
ORIGIN=(5.79,3.41) # nominal centred array; verify physical board before drilling
MOUNTS=[(15,15),(55,15),(15,45),(55,45)] # from TOP left, mm
PINS={}
PARTS=[]
def pin(ref,pad,net):
    assert pad not in [p['pad'] for p in PINS.values()],(ref,pad)
    PINS[ref]={'pad':pad,'net':net}
def part(ref,value,a,b,na,nb,kind='resistor'):
    pin(ref+'.1',a,na);pin(ref+'.2',b,nb)
    PARTS.append(dict(ref=ref,value=value,a=a,b=b,kind=kind))
for i,name in enumerate(['5V','GND','3V3','D10','D9','D8','D7']):
    pin('MCU.'+name,COLS[i]+'09',{'5V':'XIAO_5V','GND':'GND','3V3':'3V3'}.get(name,'NC_'+name))
for i,name in enumerate(['D0','D1','D2','D3','D4','D5','D6']):
    pin('MCU.'+name,COLS[i]+'15',{'D0':'ADC','D1':'HALL','D2':'TWIST','D3':'PWM_P','D4':'PWM_L'}.get(name,'NC_'+name))
u1nets={1:'GND',2:'PWM_P',3:'GATE_P',4:'GND',5:'PWM_L',6:'GATE_L',7:'GND',8:'NC_U8',9:'GND',10:'GND',11:'NC_U11',12:'GND',13:'GND',14:'5V_REG'}
for n in range(1,15):pin('U1.'+str(n),f'J{8+n:02d}' if n<=7 else f'M{23-n:02d}',u1nets[n])
for ref,row,net in [('Q1',10,'P'),('Q2',14,'L')]:
    for col,suffix,n in [('P','G','GATE_'),('Q','D','DRAIN_'),('R','S','')]:pin(ref+'.'+suffix,f'{col}{row:02d}',n+net if n else 'GND')
part('R1','100k','A02','A06','VLOAD','ADC')
part('R2','22k','B02','B06','GND','ADC')
part('R3','10k','J17','M17','PWM_P','GND')
part('R4','10k','J18','M18','PWM_L','GND')
part('R5','4.7k','V09','V13','3V3','HALL')
part('R6','4.7k','W09','W13','3V3','TWIST')
part('R7','3.3k','U09','U13','5V_REG','SW')
part('D1','NTE585','N17','Q17','5V_REG','AFTER_D1','diode')
part('D3','NTE585','W14','W18','TWIST','SW','diode')
part('C1','0.1uF','A07','B07','ADC','GND','ceramic')
part('C3','0.1uF','N08','O08','5V_REG','GND','ceramic')
part('C2','2200uF/25V','H02','H04','VLOAD','GND','electrolytic')
part('JP1','REMOVE FOR USB','N18','O18','AFTER_D1','XIAO_5V','jumper')
HARNESS=[
 ('H01','N01','VLOAD','S1 switched output'),('H02','N02','GND','Battery negative / J1 sleeve'),
 ('H03','O01','VLOAD','Buck IN+'),('H04','O02','GND','Buck IN−'),
 ('H05','P01','5V_REG','Buck OUT+ (set to 5.0 V)'),('H06','P02','GND','Buck OUT−'),
 ('H07','R01','VLOAD','Pump + / D2 striped end'),('H08','R02','DRAIN_P','Pump − / D2 unstriped end'),
 ('H09','S01','VLOAD','LED + (JST SM)'),('H10','S02','DRAIN_L','LED − (JST SM)'),
 ('H11','U08','5V_REG','Lock +5 V: A3144 pin 1 / C4'),('H12','V08','HALL','Lock HALL: A3144 pin 3'),
 ('H13','W08','SW','Lock SW: microswitch NO'),('H14','X08','GND','Lock GND: Hall pin 2 / COM / C4')]
for ref,pad,net,label in HARNESS:pin(ref,pad,net)
pin('BUS.GND','Q02','GND')
pin('BUS.LOGIC','L16','GND')
WIRES=[]
def wire(a,b,bare=False):
    WIRES.append({'id':f'W{len(WIRES)+1:02d}','a':a,'b':b,'bare':bare})
# High-current distribution: short bus links and independent load returns.
for a,b,bare in [('N01','O01',True),('R01','S01',True),('O01','R01',False),('H02','N01',False),
 ('N02','O02',True),('O02','P02',True),('P02','Q02',True),('H04','N02',False),
 ('R10','Q02',False),('R14','P02',False),('L16','O02',False)]:wire(a,b,bare)
# Quiet ground branches; the motor/LED currents do not pass through MCU or U1 ground pads.
for a,b in [('B09','L16'),('B09','B07'),('B07','B02'),('J15','M17'),('M17','M18'),
 ('J15','O08'),('M14','M13'),('M13','M11'),('M11','M10'),('J09','M10'),('J12','M14'),('O08','M10'),('X08','O08')]:wire(a,b)
for a,b in [('P01','N08'),('N08','M09'),('N08','U08'),('U08','U09'),('P01','N17'),
 ('Q17','N18'),('O18','A09'),('C09','V09'),('V09','W09'),
 ('A06','B06'),('B06','A07'),('A07','A15'),('A02','H02'),
 ('V13','V08'),('V13','B15'),('W13','C15'),('W13','W14'),('U13','W18'),('U13','W08'),
 ('D15','J10'),('J10','J17'),('E15','J13'),('J13','J18'),
 ('J11','P10'),('J14','P14'),('Q10','R02'),('Q14','S02')]:wire(a,b)
wire('L16','J15')
NETS={
 'VLOAD':('#b96500','Switched battery'), 'GND':('#334155','Ground'),
 '5V_REG':('#d12b36','Regulated 5 V'), 'AFTER_D1':('#db546b','D1 → JP1'),
 'XIAO_5V':('#b31845','JP1 → XIAO 5V'), '3V3':('#8d36b7','3.3 V'),
 'ADC':('#19826b','Battery sense'), 'HALL':('#419626','Hall signal'),
 'TWIST':('#9a3b92','Twist GPIO'), 'SW':('#b660a0','Switch contact'),
 'PWM_P':('#1763c0','Pump PWM'), 'PWM_L':('#2887a6','LED PWM'),
 'GATE_P':('#9e5819','Pump gate'), 'GATE_L':('#75621a','LED gate'),
 'DRAIN_P':('#146c79','Pump return'), 'DRAIN_L':('#a63261','LED return')}
def cr(pad):return COLS.index(pad[0]),int(pad[1:])-1
def mm(pad):
 c,r=cr(pad);return ORIGIN[0]+c*PITCH,ORIGIN[1]+r*PITCH
