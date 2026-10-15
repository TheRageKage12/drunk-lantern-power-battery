"""Generate one connected wiring diagram, with explicit power and signal wires.
Run: python3 docs/images/src/gen_wiring.py
Render: rsvg-convert -o docs/images/wiring.png docs/images/wiring.svg
"""
from pathlib import Path
from svgkit import SVG, RED, ORANGE, BLACK, GREEN, GREY

MAG = '#8b36ad'
s = SVG(2100, 1230, 'Green Lantern — connected circuit diagram')
bridges = []


def box(x, y, w, h, title, rows=(), fill='#f1f5f9'):
    s.rect(x, y, w, h, fill=fill, rx=6)
    s.text(x+w/2, y+28, title, size=18, anchor='middle', weight='bold')
    s.lines(x+w/2, y+51, rows, size=14, anchor='middle', lh=21)


def wire(points, color=GREEN, width=2.4):
    s.wire(points, color, sw=width)


def dot(x, y, color=GREEN):
    s.dot(x, y, color, r=4)


def pin(x, y, label, side='right', color=GREEN):
    s.pin(x, y, color, r=4)
    if side == 'left':
        s.text(x+12, y+5, label, size=15)
    elif side == 'right':
        s.text(x-12, y+5, label, size=15, anchor='end')
    elif side == 'top':
        s.text(x+10, y-12, label, size=15)
    else:
        s.text(x+10, y+22, label, size=15)


def ground(x, y):
    s.gnd(x, y, size=1.2)


def cap(x, top, bottom, label, color=RED, positive=False):
    mid=(top+bottom)/2
    wire([(x,top),(x,mid-5)],color)
    s.path(f'M{x-12},{mid-5} H{x+12} M{x-12},{mid+5} H{x+12}', sw=2)
    wire([(x,mid+5),(x,bottom)],BLACK)
    s.text(x+20,mid+5,label,size=14)
    if positive:
        s.text(x-27,mid-10,'+',size=18)
    ground(x,bottom)


def diode(x1, x2, y, label, color=GREEN, forward=True):
    mid=(x1+x2)/2
    a,k=(mid-10,mid+9) if forward else (mid+10,mid-9)
    wire([(x1,y),(mid-11,y)],color)
    s.path(f'M{a},{y-10} V{y+10} L{k},{y} Z M{k},{y-12} V{y+12}',sw=1.8,fill='#e2e8f0')
    wire([(mid+11,y),(x2,y)],color)
    s.text(mid,y-24,label,size=14,anchor='middle')


def horizontal_bridge(x, y, color):
    bridges.append((f'M{x-9},{y} Q{x},{y-17} {x+9},{y}', f'M{x-9},{y} H{x+9}', color))


def vertical_bridge(x, y, color):
    bridges.append((f'M{x},{y-9} Q{x+17},{y} {x},{y+9}', f'M{x},{y-9} V{y+9}', color))


s.text(35,38,'Green Lantern power battery — connected wiring diagram',size=28,weight='bold')
s.text(35,68,'Dots join wires. Bridge marks cross without joining. All ground symbols connect to the common GND rail.',size=16)
for x,color,label in [(1380,ORANGE,'Battery rail'),(1570,RED,'Regulated 5 V'),(1780,MAG,'3.3 V'),(1930,GREEN,'Signal')]:
    wire([(x,57),(x+28,57)],color,3)
    s.text(x+36,62,label,size=14)

# Battery and charging: the jack joins the battery before S1.
box(40,140,230,110,'TalentCell YB1203000',['3000 mAh • 3 A maximum','DC5521 centre-positive'],fill='#fff7e6')
pin(270,180,'+','right',ORANGE)
wire([(270,180),(355,180)],ORANGE,3)
dot(300,180,ORANGE)
s.pin(355,180); s.pin(400,180)
wire([(356,177),(396,158)],BLACK)
s.text(375,142,'S1 power',size=16,anchor='middle',weight='bold')
wire([(400,180),(440,180),(440,100)],ORANGE,3)
wire([(440,100),(2050,100)],ORANGE,3.5)
s.text(2050,88,'VLOAD: switched battery, 9–12.6 V (not regulated)',size=16,anchor='end',color=ORANGE,weight='bold')
pin(155,250,'−','bottom',BLACK)
wire([(155,250),(155,269)],BLACK); ground(155,269)
box(40,295,230,85,'J1 charge jack',['DC5521 • third contact unused'],fill='#fff7e6')
wire([(300,180),(300,329),(270,329)],ORANGE)
pin(270,329,'+','right',ORANGE)
pin(155,380,'sleeve −','bottom',BLACK)
wire([(155,380),(155,403)],BLACK); ground(155,403)

# Buck input and bulk capacitor.
dot(560,100,ORANGE)
wire([(560,100),(560,278),(330,278),(330,403),(260,403),(260,430)],ORANGE)
box(60,430,250,125,'LM2596 buck',fill='#fff7e6')
s.lines(185,516,['Set OUT to 5.0 V with a meter','before connecting electronics'],size=14,anchor='middle',lh=20)
pin(260,430,'IN+','top',ORANGE)
pin(175,555,'IN− / OUT−','bottom',BLACK)
wire([(175,555),(175,590)],BLACK); ground(175,590)
pin(310,480,'OUT+','right',RED)
dot(670,100,ORANGE)
cap(670,100,270,'C2 2200 µF / 25 V',ORANGE,positive=True)

# 5 V: branch to Hall/driver is before the isolation diode.
wire([(310,480),(390,480)],RED,3)
dot(350,480,RED)
wire([(350,480),(350,310),(1250,310),(1250,550)],RED,3)
s.text(1010,292,'+5V_REG — U1 and Hall, before D1',size=16,color=RED,weight='bold')
diode(390,475,480,'D1 NTE585',RED)
wire([(475,480),(510,480)],RED)
s.pin(510,480); s.pin(540,480)
s.rect(504,473,42,14,fill='none',stroke=RED,sw=2)
s.text(525,444,'JP1',size=15,anchor='middle',weight='bold')
wire([(540,480),(600,480)],RED)
s.lines(360,521,['D1 stripe → XIAO','JP1: remove for USB'],size=14,lh=22)

# Controller, visible wire to every used GPIO.
box(600,370,260,470,'Seeed XIAO RP2040',['3.3 V GPIO'])
pin(600,480,'5V','left',RED)
pin(600,560,'3V3','left',MAG)
pin(600,620,'D1 • Hall','left')
pin(600,680,'D2 • twist','left')
pin(860,610,'D3 • pump PWM','right')
pin(860,710,'D4 • light PWM','right')
pin(800,370,'','top')
s.text(790,355,'D0 • battery sense',size=15,anchor='end')
pin(820,840,'GND','bottom',BLACK)
wire([(820,840),(820,1180)],BLACK,2.8)
pin(700,840,'D6','bottom')
wire([(700,840),(700,920)],GREEN)
s.pin(700,920); s.pin(700,965)
wire([(700,965),(678,927)],BLACK)
s.lines(715,945,['PRIME','optional'],size=14,lh=20)
wire([(700,965),(700,995)],BLACK); ground(700,995)

# Battery divider and filter connect physically to D0.
dot(840,100,ORANGE)
s.res_v(840,100,210,'R1 100 kΩ',ORANGE,size=14)
dot(840,210)
s.res_v(840,210,270,'R2 22 kΩ',lab_dx=-112,size=14)
ground(840,270)
wire([(840,210),(960,210)])
dot(900,210); dot(960,210)
cap(960,210,270,'C1 0.1 µF',GREEN)
wire([(900,210),(900,350),(800,350),(800,370)])
vertical_bridge(900,310,GREEN)
s.text(1065,242,'12.6 V → 2.27 V at D0',size=14,color=GREY)

# Original 74AHCT125 buffer and existing local 0.1 uF bypass.
box(1120,550,270,330,'U1 74AHCT125',['DIP-14 • 3.3 V → 5 V'],fill='#eef6ff')
pin(1250,550,'14 VCC','top',RED)
pin(1250,880,'7 GND','bottom',BLACK)
wire([(1250,880),(1250,1180)],BLACK,2.8)
s.lines(1255,710,['OE 1, 4, 10, 13 + IN 9, 12','connect to pin 7 / GND','OUT 8, 11 unconnected'],size=13,anchor='middle',lh=22)
wire([(1250,310),(1380,310)],RED)
dot(1250,310,RED); dot(1380,310,RED)
cap(1380,310,410,'C3 0.1 µF')
s.text(1280,480,'C3: short leads at pins 14 / 7',size=13)
pin(1120,650,'2 IN A','left'); pin(1390,650,'3 OUT A','right')
pin(1120,830,'5 IN B','left'); pin(1390,830,'6 OUT B','right')
wire([(860,610),(940,610),(940,650),(1120,650)])
wire([(860,710),(900,710),(900,830),(1120,830)])
dot(980,650); s.res_v(980,650,708,'R3 10 kΩ',size=14); ground(980,708)
dot(1060,830); s.res_v(1060,830,925,'',size=14); ground(1060,925)
s.text(1050,881,'R4 10 kΩ',size=14,anchor='end')

# Pump / LED loads; all load supplies and gate-drive paths are wired.
def stage(x, gate_y, title, q):
    box(x,190,170,90,title,['12 V • + top / − bottom'],fill='#fff7e6')
    px,dx=x+40,x+130
    wire([(px,100),(px,190)],ORANGE,3); dot(px,100,ORANGE)
    wire([(dx,280),(dx,gate_y-50)],BLACK,3)
    box(x,gate_y-50,170,110,q+' IRLZ44NPBF')
    s.text(x+85,gate_y+32,'TO-220; tab = drain',size=12,anchor='middle')
    pin(dx,gate_y-50,'2 D','top',BLACK)
    pin(x,gate_y,'1 G','left')
    pin(dx,gate_y+60,'','bottom',BLACK)
    s.text(dx-10,gate_y+53,'3 S',size=14,anchor='end')
    wire([(dx,gate_y+60),(dx,1180)],BLACK,3)
    dot(dx,1180,BLACK)

stage(1530,650,'Kamoer KPHM200','Q1')
stage(1840,830,'Green COB strip','Q2')
s.lines(1950,310,['~75 cm','7 parallel pieces'],size=14,anchor='end',lh=20)
wire([(1390,650),(1530,650)])
wire([(1390,830),(1840,830)])
horizontal_bridge(1660,830,GREEN)

# Flyback cathode to pump positive, anode to switched negative.
dot(1570,168,ORANGE)
wire([(1570,168),(1760,168),(1760,227)],ORANGE)
s.path('M1750,252 H1770 L1760,230 Z M1748,229 H1772',sw=2,fill='#e2e8f0')
wire([(1760,252),(1760,365),(1660,365)],BLACK)
dot(1660,365,BLACK)
s.lines(1740,395,['D2 NTE586','3 A / 40 V','stripe toward +'],size=14,anchor='middle',lh=22)

# Hall: local capacitor and external 3.3 V pull-up; OUT is direct to GPIO.
box(80,675,260,135,'A3144',fill='#f3e8ff')
s.lines(80,856,['Hall sensor: printed face forward,','leads down: 1 VCC, 2 GND, 3 OUT'],size=14,lh=20)
pin(340,710,'1 VCC','right',RED)
pin(340,750,'3 OUT','right')
pin(340,790,'2 GND','right',BLACK)
wire([(350,480),(350,630),(420,630),(420,710),(340,710)],RED)
dot(370,630,RED); cap(370,630,690,'')
s.text(330,665,'C4 0.1 µF',size=14,anchor='end')
s.text(80,610,'C4 at the sensor, after the cable',size=14,color=GREY)
wire([(340,790),(370,790),(370,835)],BLACK); ground(370,835)
wire([(340,750),(550,750),(550,620),(600,620)])
horizontal_bridge(420,750,GREEN)
horizontal_bridge(470,750,GREEN)
# 3V3 goes only to R5 and R6, never to the sensor supply.
wire([(600,560),(470,560),(470,825),(530,825)],MAG)
dot(470,610,MAG)
wire([(470,610),(495,610),(495,650)],MAG)
s.res_v(495,650,750,'')
s.lines(505,690,['R5','4.7 kΩ'],size=12,lh=17)
dot(495,750)
s.res_v(530,825,980,'')
s.lines(515,890,['R6','4.7 kΩ'],size=14,anchor='end',lh=20)
dot(530,980)

# Twist switch: resistor supplies contact current; Schottky cathode at NO.
box(80,940,260,130,'D2F-01L microswitch',['NC terminal unused'],fill='#f3e8ff')
s.text(80,1105,'Lever pressed by rotor cam',size=14)
pin(340,980,'NO','right')
pin(340,1040,'COM','right',BLACK)
wire([(340,1040),(370,1040),(370,1180)],BLACK)
dot(370,1180,BLACK)
wire([(340,980),(440,980)])
dot(420,980)
dot(420,710,RED)
wire([(420,710),(420,815)],RED)
s.res_v(420,815,905,'',RED)
s.lines(406,854,['R7','3.3 kΩ'],size=14,anchor='end',lh=20)
wire([(420,905),(420,980)])
diode(440,510,980,'D3 NTE585',forward=False)
wire([(510,980),(575,980),(575,680),(600,680)])
s.lines(400,1030,['D3 stripe ← switch NO','R7: ~1.5 mA through closed contacts','D1 / D2 GPIO pull-ups: 3.3 V only'],size=14,lh=24)

# Common ground rail; local ground symbols use this same return.
wire([(40,1180),(2050,1180)],BLACK,3.5)
dot(820,1180,BLACK); dot(1250,1180,BLACK)
ground(2050,1180)
s.text(2030,1210,'COMMON GND',size=17,anchor='end',weight='bold')

# Erase straight crossing segments and draw wire bridges above vertical wires.
# Only specified crossings are changed; the uninterrupted path remains one wire.
for path,straight,color in bridges:
    s.path(straight,stroke='white',sw=7)
    s.path(path,stroke='white',sw=7)
    s.path(path,stroke=color,sw=2.4)

out=Path(__file__).resolve().parent.parent/'wiring.svg'
out.write_text(s.finish())
print(out)
