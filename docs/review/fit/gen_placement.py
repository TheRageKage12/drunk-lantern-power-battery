"""Conceptual placement study; dimensions are review assumptions, not PCB routing.
Run this script, then rsvg-convert placement-study.svg to placement-study.png.
"""
from pathlib import Path
import math, html
out=Path(__file__).resolve().parent
s=[]
def add(x): s.append(x)
def text(x,y,t,size=14,color='#203247',anchor='start'):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(t)}</text>')
def rect(x,y,w,h,fill,stroke='#698095',rx=0):add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>')
def poly(points,fill,stroke='#698095'):
    add('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}"/>')
def line(x1,y1,x2,y2,color='#698095',width=1):add(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="{width}" fill="none"/>')
add('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1110" viewBox="0 0 1200 1110"><rect width="1200" height="1110" fill="#f6f8fb"/><g font-family="Arial, sans-serif">')
text(38,40,'Electronics fit — proposed arrangement',27)
text(38,68,'Dimensions from the current CAD. Placement study, not a pin-by-pin soldering template.',16)
rect(25,90,580,560,'white','#d6dee8',12)
text(45,121,'1  Component side of the 70 × 50 mm board',20)
text(45,147,'Landscape on the existing vertical panel; component side faces the shell.',13)
ox,oy,k=55,181,7
rect(ox,oy,70*k,50*k,'#f1e4c5','#9e8656')
# Verified 24 x 18 pattern, nominally centred; exact edge offsets must be measured.
for c in range(24):
 for r in range(18):
  x=ox+(5.79+c*2.54)*k;y=oy+(3.41+r*2.54)*k
  add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.7" fill="#b8aa8b"/>')
rect(ox+65*k,oy,5*k,50*k,'#fce5e5','#cc8282')
for x,y in [(15,15),(55,15),(15,45),(55,45)]:
 add(f'<rect x="{ox+(x-4.5)*k}" y="{oy+(y-4.5)*k}" width="{9*k}" height="{9*k}" fill="#f6f8fb" stroke="#a5b1be" stroke-dasharray="3 3"/>')
 add(f'<circle cx="{ox+x*k}" cy="{oy+y*k}" r="{1.6*k}" fill="white" stroke="#546a80"/>')
def block(x,y,w,h,label,fill):
 rect(ox+x*k,oy+y*k,w*k,h*k,fill)
 text(ox+(x+w/2)*k,oy+(y+h/2)*k+4,label,12,anchor='middle')
block(20,1,30,18,'C2 • lying flat','#ffe2aa')
block(2,22,21,18,'XIAO → USB left','#cde8f8')
block(27,21,11,20,'U1','#d6ddf7')
block(41,23,10,5,'Q1','#e3d9ef');block(41,33,10,5,'Q2','#e3d9ef')
block(3,2,7,18,'A','#d7eedc');block(58,21,7,19,'B','#d7eedc')
block(27,43,11,5,'R3/4','#d7eedc');block(40,41,9,8,'D1/JP1','#cde8f8')
block(23.5,25,3,5,'C3','#d7eedc')
text(45,560,'A: R1, R2, C1 battery sensing. B: R5, R6, R7, D3 sensor interface.',13)
text(45,583,'B stays ≤3 mm high; the last 5 mm stays empty to clear a passing shell boss.',13)
text(45,606,'Dashed squares: 9 mm mounting keep-outs. Other boxes reserve working space.',13)
text(45,629,'C2 box allows 30 × 18 mm including bent leads; actual part size is unpublished.',13)
# plan views
for cx,title,sub in [(895,'2  Above the deck','Pump and bottle are the existing CAD envelopes.')]:
 rect(620,90,555,560,'white','#d6dee8',12);text(640,121,title,20);text(640,147,sub,13)
scale=2.0
cx,cy=895,385
def xy(x,y):return cx+x*scale,cy-y*scale
def boxxy(x,y,w,h,fill):poly([xy(x-w/2,y-h/2),xy(x+w/2,y-h/2),xy(x+w/2,y+h/2),xy(x-w/2,y+h/2)],fill)
add(f'<circle cx="{cx}" cy="{cy}" r="{89.6*scale}" fill="#f6f9fc" stroke="#526c80" stroke-width="3"/>')
xx,yy=xy(-40,-8);add(f'<circle cx="{xx}" cy="{yy}" r="{38*scale}" fill="#d7eedc" stroke="#6d9b77"/>');text(xx,yy,'Jar',17,anchor='middle')
boxxy(30,32,64,40,'#dce4f6');boxxy(30,-27,40,78,'#dce4f6');xx,yy=xy(30,32);text(xx,yy,'Pump head',14,anchor='middle');xx,yy=xy(30,-27);text(xx,yy,'Motor',14,anchor='middle')
a=math.radians(115);n=(math.cos(a),math.sin(a));t=(-math.sin(a),math.cos(a))
def rt(r,u):return xy(r*n[0]+u*t[0],r*n[1]+u*t[1])
poly([rt(r,u) for r,u in [(54.5,-26),(57.5,-26),(57.5,26),(54.5,26)]],'#a5b9c6')
poly([rt(r,u) for r,u in [(62,-35),(63.194,-35),(63.194,35),(62,35)]],'#cca55b')
# Central region reserves tall component projection only, not full board.
poly([rt(r,u) for r,u in [(63.194,-15),(81.194,-15),(81.194,15),(63.194,15)]],'#ffe2aa')
for a_deg in [0,140,225]:
 a=math.radians(a_deg);na=(math.cos(a),math.sin(a));ta=(-math.sin(a),math.cos(a))
 poly([xy(r*na[0]+u*ta[0],r*na[1]+u*ta[1]) for r,u in [(75.5,-5),(89.6,-5),(89.6,5),(75.5,5)]],'#f6b5b5','#b46161')
text(640,582,'Red: shell retaining bosses. Their paths must stay clear during removal.',13)
text(640,605,'Gold: board and central capacitor space. Grey: existing support panel.',13)
text(640,628,'Body bore Ø179.2 mm. Wires, cradles and fasteners omitted for clarity.',13)
# Bottom left floor view smaller scale
rect(25,670,580,415,'white','#d6dee8',12);text(45,702,'3  Under the deck — new battery body',20)
cx,cy,scale=228,900,1.72
add(f'<circle cx="{cx}" cy="{cy}" r="{89.6*scale}" fill="#f6f9fc" stroke="#526c80" stroke-width="2"/>')
boxxy(0,0,65,105,'#ffe2aa');boxxy(-58,0,22,47,'#cde8f8');boxxy(56,0,19,36,'#edf0f5');boxxy(15,71.5,26,23,'#f6b5b5')
for x in [-33,33]:
 for y in [-55,0,55]:boxxy(x,y,9,9,'#acbac7')
text(228,886,'TalentCell',14,anchor='middle');text(228,907,'105 × 65',14,anchor='middle');text(228,928,'25 mm tall',13,anchor='middle')
text(401,776,'Existing tray features:',14)
text(401,803,'Blue: buck pocket',13);text(401,828,'Grey: old pillars',13);text(401,853,'Red: S1 pocket',13)
text(401,890,'New pack overlaps',14,'#ad4141');text(401,911,'the old pillars/stops.',14,'#ad4141')
text(401,950,'Plug and switch access',13);text(401,971,'need reserved space.',13)
text(45,1065,'Separate CAD PR: enlarge the pocket and keep the deck height initially.',13)
rect(620,670,555,415,'white','#d6dee8',12)
text(640,702,'What the fit depends on',20)
notes=[('Board mounting','Bottom edge 2 mm above deck; 70 mm edge horizontal.'),('Wall clearance','About 26 mm at the middle, 19 mm at the outer ends.'),('Tall components','Central C2 ≤18 mm projection; MOSFETs ≤22 mm.'),('Service clearance','Keep tall parts away from the end beside the 140° boss.'),('Battery space','25 mm pack leaves 17 mm below the existing deck.'),('Still to verify','Actual C2, buck, pump, plug and assembled cable sizes.')]
y=741
for title,body in notes:
 text(640,y,title,15);text(640,y+22,body,13);y+=54
add('</g></svg>')
(out/'placement-study.svg').write_text('\n'.join(s))
r=56+1.5+4.5+0.047*25.4
print('board face radius:',r)
print('wall gap centre/ends:',89.6-r, math.sqrt(89.6**2-35**2)-r)
print('board bottom/top:',49,99,'screw z:',54,84)
print('battery floor/bodytop/deckunderside:',2,27,44)
print('board-edge 140deg boss starts at component height:',(75.5-35*math.sin(math.radians(25)))/math.cos(math.radians(25))-r)
