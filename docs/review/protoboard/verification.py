"""Beginner-facing checks, tied to physical board holes and assembly stage.

Resistance checks are assembly screens, not semiconductor specification tests.
Do not infer an open circuit from a missing continuity beep.
"""
import layout as L

DIRECT = 'Same as touching the probe tips (within 2 Ω).'
OFF = 'Battery and USB unplugged; pump, LEDs and lock cable disconnected. Keep the 74AHCT125 chip out of its socket and the jumper cap off the two JP1 pins.'
METER = 'Black lead in COM; red lead in V/Ω (never A). Ω measures resistance; kΩ means 1,000 Ω. Use auto-range, or a range above the expected reading. Touch the tips together and note the reading. OL means over range or disconnected.'
STOP = 'If a result does not match, stop here. Recheck the hole names and probe contact, then inspect that connection for a loose joint, wrong pin or stray strand. Repair with all power disconnected and repeat the check.'

def row(name,black,red,expected,mode='Ω',pads=None):
 return dict(name=name,black=black,red=red,expected=expected,mode=mode,pads=pads if pads is not None else [p for p in (black,red) if p in {x['pad'] for x in L.PINS.values()}])

def first():
 checks=[]
 for ref,low,high in [('R1','94','106'),('R2','20.7','23.3'),('R5','4.42','4.98'),('R6','4.42','4.98'),('R7','3.10','3.50')]:
  checks.append(row(ref,L.PINS[ref+'.2']['pad'],L.PINS[ref+'.1']['pad'],f'{low}–{high} kΩ'))
 for ref in ('D1','D3'):
  a,b=[L.PINS[ref+'.'+i]['pad'] for i in ('1','2')]
  checks.append(row(ref+' forward',b,a,'Typically 0.15–0.65 V. Swap probes: OL.','Diode'))
 return checks

def wire(w):
 if len(w.get('tails',[]))==2:
  return [row(w['id']+' end-to-end',w['a'],w['b'],DIRECT)]
 if w.get('tails'):
  t=w['tails'][0]
  return [row(w['id']+' board joint',t['anchor'],t['node'],DIRECT,pads=[t['anchor'],t['node']])]
 return [row(w['id']+' lead',w['a'],'C2 '+('positive leg' if w['colour']=='red' else 'striped negative leg'),DIRECT,pads=[w['a']])]

def wiring():
 # These connections exist before the three external ground returns are joined.
 return [row('Socket ground','F04',p,DIRECT) for p in ('G13','D13','A13','B10','C10','E10','F10')]+[
  row('Controller ground','F04','P15',DIRECT),
  row('5 V distribution','H04','G10',DIRECT),
  row('Jumper cap removed','R18','S18','No steady near-zero reading. Below 10 Ω: look for a jumper cap or solder bridge; other circuit paths can give a higher finite reading.'),
  row('Unused socket output','A10','B10','OL.'),
  row('Unused socket output','D10','E10','OL.')]

def unpowered():
 return [row('Buck ground','buck IN−','buck OUT−',DIRECT,pads=[]),
  row('Pump ground return','F04','W01',DIRECT),
  row('LED ground return','F04','H18',DIRECT)]+[
  row(name,a,b,'No steady reading below 10 Ω.')
  for name,a,b in [('Battery / ground','F04','F02'),('5 V / ground','F04','G10'),('Controller 5 V / ground','F04','Q15'),('3.3 V / ground','F04','O15'),('Battery / 5 V','G10','F02'),('Battery / controller 5 V','Q15','F02'),('Battery / 3.3 V','O15','F02')]]

def powered():
 return [row('Buck supply','F04','G10','4.9–5.1 V.','DC V'),
         row('Controller supply','F04','Q15','4.3–5.1 V.','DC V'),
         row('3.3 V supply','F04','O15','3.2–3.4 V.','DC V'),
         row('Battery sense','F04','Q09','About 0.18 × the F02-to-F04 voltage (2.27 V for 12.6 V); within 10%.','DC V'),
         row('Pump gate at idle','F04','U01','Below 0.2 V.','DC V'),
         row('LED gate at idle','F04','H16','Below 0.2 V after the startup blink.','DC V')]

def splice(net):
 return {
 'VLOAD':[row('Battery-positive board lead','F02','exposed J_LOAD join',DIRECT,pads=['F02'])],
 'GND':[row('Ground return',p,'exposed J_GND join',DIRECT,pads=[p]) for p in ('F04','W01','H18')],
 '5V_REG':[row('5 V board lead','H04','exposed J_5V join',DIRECT,pads=['H04'])]
 }[net]
