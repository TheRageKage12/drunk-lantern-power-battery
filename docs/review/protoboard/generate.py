"""Validate and build the board viewer/schedule; --export also renders the PNG and PDF."""
from pathlib import Path
from collections import defaultdict
import argparse, math, html, json
from layout import *
import mechanical as M
import routing as R
OUT=Path(__file__).resolve().parent
ESC=html.escape
BY_PAD={p['pad']:(ref,p['net']) for ref,p in PINS.items()}

def validate():
    parent={p:p for p in BY_PAD}
    def root(p):
        if parent[p]!=p:parent[p]=root(parent[p])
        return parent[p]
    for ref,p in PINS.items():
        x,y=mm(p['pad'])
        assert all(not(abs(x-mx)<5.25 and abs(y-my)<5.25) for mx,my in MOUNTS),(ref,'mount keepout')
    for w in WIRES:
        a,b=w['a'],w['b']
        assert a in BY_PAD and b in BY_PAD,w
        assert BY_PAD[a][1]==BY_PAD[b][1],('short',w)
        assert not BY_PAD[a][1].startswith('NC'),('NC wired',w)
        w['net']=BY_PAD[a][1]
        for pad in w.get('pads',[a,b]):
            assert BY_PAD[pad][1]==w['net'],('cross-net pad',w['id'],pad)
            parent[root(a)]=root(pad)
        parent[root(a)]=root(b)
    for ref,pad,net,label in HARNESS:
        assert BY_PAD[pad][1]==net, (ref,'cable connected to wrong net')
    groups=defaultdict(set)
    for pad,(ref,net) in BY_PAD.items():groups[net].add(root(pad))
    assert all(len(g)==1 for n,g in groups.items()),groups
    # Mechanical pins with no external connection must remain separate, not tied to ground.
    assert sum(n.startswith('NC') for _,n in BY_PAD.values())==8
    assert len(HARNESS)==14 and len(PARTS)==13
    return {'occupied_pads':len(PINS),'wires':len(WIRES),'nets':len(NETS),'unused_device_pins':8,
            'result':'All intended nets connected; no cross-net wires; no occupied pad in mount keepouts.'}

class Drawing:
 def __init__(self,rear=False):self.s=[];self.rear=rear;self.k=16;self.ox=88;self.oy=300
 def add(self,v):self.s.append(v)
 def point(self,x,y):return(self.ox+(70-x if self.rear else x)*self.k,self.oy+y*self.k)
 def text(self,x,y,t,size=16,anchor='start',color='#263649',extra=''):
  self.add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" {extra}>{ESC(str(t))}</text>')
 def mt(self,x,y,t,size=16,anchor='middle',color='#263649'):
  a,b=self.point(x,y);self.text(a,b,t,size,anchor,color)
 def rect(self,x,y,w,h,fill,stroke='#627084',dash=False):
  a,b=self.point(x+w if self.rear else x,y)
  self.add(f'<rect x="{a}" y="{b}" width="{w*self.k}" height="{h*self.k}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" {"stroke-dasharray=\"5 4\"" if dash else ""}/>')
 def line(self,points,color,width=3,dash=False):
  points=[self.point(*p) for p in points];self.add('<path d="'+' '.join(('M' if i==0 else 'L')+f'{p[0]:.2f},{p[1]:.2f}' for i,p in enumerate(points))+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {"stroke-dasharray=\"5 4\"" if dash else ""}/>')
 def circle(self,x,y,r,fill,stroke='#64748b',width=1.5):
  a,b=self.point(x,y);self.add(f'<circle cx="{a}" cy="{b}" r="{r*self.k}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
 def body(self):
  for ref,(x,y,w,h,d0,d1) in M.bounds().items():
   if ref=='USB':
    self.rect(x,y,w,h,'#c7d0da'); self.mt(x+w/2,y+h/2,'USB',11);continue
   color=('#d2e8f4' if ref=='MCU' else '#e0e4f1' if ref=='U1' else '#fae2b1' if ref=='C2'
          else '#d9dce2' if ref in ('Q1','Q2') else '#f5ca84' if ref in ('C1','C3') else '#eddbb9')
   self.rect(x,y,w,h,color)
   label_y = y+.95 if ref in ('Q1','Q2') else y-.5 if ref=='JP1' else y+h/2+.35
   self.mt(x+w/2,label_y,{'MCU':'XIAO RP2040','C2':'C2 · flat'}.get(ref,ref),15)
   if ref=='C2':self.mt(x+w/2,y+h/2+3,'25 × Ø18 mm maximum',12)
   if ref=='U1':self.line([(x+w/2-1.5,y),(x+w/2-1.5,y+1.2),(x+w/2+1.5,y+1.2),(x+w/2+1.5,y)],'#475569',2)
   if ref in ('Q1','Q2'):self.line([(x,y+h),(x+w,y+h)],'#253448',4)
  for p in PARTS:
   a,b=mm(p['a']),mm(p['b']);x,y,w,h,_,_=M.bounds()[p['ref']]
   if p['ref']=='C2':
    self.line([a,(25,a[1])],'#b96500',2);self.line([b,(25,b[1])],'#334155',2)
   elif p['kind']=='diode':
    if a[0]==b[0]:self.line([(x,y+h-.6),(x+w,y+h-.6)],'#475569',3)
    else:self.line([(x+w-.6,y),(x+w-.6,y+h)],'#475569',3)
 def draw(self):
  self.add('<g font-family="Arial, sans-serif">')
  self.text(42,38,'SOLDER SIDE — mirrored' if self.rear else 'COMPONENT SIDE — USB at left',29)
  self.text(42,70,'Flip the board left ↔ right; top stays top. Pad names do not change.' if self.rear else '70 × 50 mm • 24 × 18 holes • 2.54 mm pitch • all point-to-point wires are on rear.',18)
  self.text(42,100,'Insulated wires cross without joining. Solder at marked anchors; crossings do not join.' if self.rear else 'Solid dots: through-hole leads. Square ports: rear-only cable attachment pads.',17)
  self.text(42,127,'Bare tracks are anchored at each bend and at most three holes apart.' if self.rear else 'Coordinates are assigned by this drawing; supplier lettering may be on the opposite face.',17)
  if not self.rear:
   self.text(42,166,'R1 100k · R2 22k · R3/R4 10k · R5/R6 4.7k · R7 3.3k',18)
   self.text(42,191,'C1/C3 0.1 µF · D1/D3 NTE585 · JP1 removable shunt (remove for USB)',18)
   self.text(42,216,'D2 stays at the pump; C4 stays at the Hall sensor. Neither mounts on this board.',17)
  self.rect(0,0,70,50,'#fbf5e8','#887555')
  self.rect(65,0,5,50,'#fce8e8','#e3c1c1')
  for mx,my in MOUNTS:
   self.rect(mx-4.5,my-4.5,9,9,'#edf0f5','#9ba7b4',True);self.circle(mx,my,1.6,'white')
  if self.rear:
   self.add('<g opacity="0.35">');self.body();self.add('</g>')
  for c in range(24):
   for r in range(18):
    pad=f'{COLS[c]}{r+1:02d}';x,y=mm(pad)
    if any(abs(x-mx)<4.5 and abs(y-my)<4.5 for mx,my in MOUNTS):continue
    self.circle(x,y,.44,'#f8f5e9','#c7b993',1)
  if not self.rear:self.body()
  if self.rear:
   for w in WIRES:
    color=NETS[w['net']][0];self.add(f'<g class="wire" data-id="{w["id"]}" data-net="{w["net"]}"><title>{w["id"]}: {w["a"]} ↔ {w["b"]} · {w["net"]}</title>')
    self.line(w['path'],'#fffdf7',8 if w['bare'] else 7)
    self.line(w['path'],color,4.3 if w['bare'] else 3.2)
    self.add('</g>')
   # Flying leads use their own holes; the bare tracks join them on the rear.
   for ref,pad,net,label in HARNESS:
    route=next(w for w in ALL_ROUTES if w['id']==ref);pts=route['path'];end=pts[-1]
    self.add(f'<g class="harness" data-net="{net}"><title>{ref}: {pad} → {ESC(label)}</title>')
    self.line(pts,'white',7);self.line(pts,NETS[net][0],3.4,True)
    self.mt(end[0],end[1]-.5-(route['depth']-3)*.7,ref,10);self.add('</g>')
  for pad,(ref,net) in BY_PAD.items():
   x,y=mm(pad);color=NETS.get(net,('#778293',''))[0]
   label=f'Hole {pad}: {ref} — {NETS.get(net,("", "unused pin; no wire"))[1]}'
   self.add(f'<g class="pad" data-pad="{pad}" data-net="{net}" data-detail="{ESC(label)}" tabindex="0" role="button" aria-label="{ESC(label)}"><title>{ESC(label)}</title>')
   self.circle(x,y,.9,'transparent','none',0)
   if ref.startswith('H') or ref.startswith('BUS.'):self.rect(x-.65,y-.65,1.3,1.3,'#f8fafc',color)
   self.circle(x,y,.49,'#e9eef5',color,2.5)
   if not net.startswith('NC'):self.circle(x,y,.15,color,color,1)
   else:self.line([(x-.23,y-.23),(x+.23,y+.23)],'#718096',1.4)
   self.add('</g>')
  if not self.rear:
   for i,name in enumerate(['5V','GND','3V3','D10','D9','D8','D7']):self.mt(*[mm(COLS[i]+'09')[0],26.0],name,12)
   for i,name in enumerate(['D0','D1','D2','D3','D4','D5','D6']):self.mt(mm(COLS[i]+'15')[0],37.5,name,12)
   for n in range(1,15):
    x,y=mm(PINS['U1.'+str(n)]['pad']);self.mt(x+(1.2 if n<=7 else -1.2),y+.3,n,11)
   for row in [13,17]:
    for col,lab in zip('PQR','GDS'):
     x,y=mm(f'{col}{row:02d}');self.mt(x,y+1.55,lab,13)
  for c in range(24):
   x,_=mm(COLS[c]+'01');self.mt(x,-3.4,COLS[c],16);self.mt(x,52.0,COLS[c],16)
  for r in range(18):
   _,y=mm('A'+f'{r+1:02d}');self.mt(-1.7,y+.35,f'{r+1:02d}',15);self.mt(71.7,y+.35,f'{r+1:02d}',15)
  self.text(42,1180,'Solder-side drawing shows every wire; use the wire schedule or interactive net filter to trace crowded areas.' if self.rear else 'U1 notch ↑   •   Q1/Q2 printed faces ↓   •   D1 stripe → W08   •   D3 stripe → X18   •   C2 + F02 / − F04',17)
  self.text(42,1210,'Grey squares: 9 × 9 mm mounting keep-outs. Centres (x,y): (18,17), (55,15), (15,45), (58,45) mm.',16)
  self.text(42,1238,'Grid offsets are nominal. Verify the board and dry-fit C2 before drilling or soldering. This is not a 1:1 drill template.',16)
  self.add('</g>');return ''.join(self.s)

def svg(body,width=1330,height=1264):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{body}</svg>'


def reference_pages():
 d=Drawing();d.add('<g font-family="Arial, sans-serif">')
 d.text(42,45,'CABLE CONNECTIONS AND COLOUR KEY',29)
 d.text(42,85,'Dashed leads attach to rear copper pads. Last column: wire centre behind the board.',19)
 for i,(ref,pad,net,label) in enumerate(HARNESS):
  y=135+i*38;d.text(48,y,ref,18);d.text(130,y,pad,18);d.text(230,y,label,18,color=NETS[net][0]);d.text(1140,y,f"{next(w for w in ALL_ROUTES if w['id']==ref)['depth']:g} mm",17)
 d.text(42,705,'OFF-BOARD CONNECTIONS',23)
 lines=[
 "Battery + → S1 input. S1 output → H01. Battery − → H02. (No charge jack: charge at the splitter's female end.)",
 'Set the buck output to 5.0 V before connecting H05/H06.',
 'D2 NTE586 across pump terminals: stripe to pump +. C4 0.1 µF across A3144 pins 1–2.',
 'A3144: printed face toward you, leads down; pins 1/2/3 = +5V/GND/HALL.',
 'Twist switch COM → GND, NO → SW; NC unused. Lock cable uses the JST PH pair.',
 'JP1: fit shunt for battery operation; remove for USB and follow build-guide power procedure.'
 ]
 for i,line in enumerate(lines):d.text(42,744+i*28,line,17)
 for i,(net,(color,label)) in enumerate(NETS.items()):
  col,row=divmod(i,4);d.text(42+col*318,965+row*38,'● '+label,16,color=color)
 d.text(42,1165,'Cable H02 attaches to N01. Capacitor C2 positive uses F02.',17)
 d.add('</g>');connections=svg(''.join(d.s))
 pages=[connections]
 for start in range(0,len(WIRES),32):
  d=Drawing();d.add('<g font-family="Arial, sans-serif">')
  d.text(42,45,'WIRE AND SOLDER ANCHORS',29)
  d.text(42,82,'Solder every listed hole. Bare tracks are supported at bends and ≤3 holes apart.',18)
  for i,w in enumerate(WIRES[start:start+32]):
   y=130+i*32
   d.text(42,y,w['id'],16);d.text(115,y,' → '.join(w['anchors']),16)
   d.text(630,y,w['net'],15,color=NETS[w['net']][0])
   d.text(850,y,'BARE track' if w['bare'] else f"Rounded arch · top {w['depth']+.9:g} mm",15)
  d.text(42,1210,'6 mm removable spacers + existing 10 mm posts. Printed parts stay unchanged.',17)
  d.add('</g>');pages.append(svg(''.join(d.s)))
 return pages

def export(front,rear):
 """Render kept artifacts using temporary SVG/PDF intermediates."""
 import shutil, subprocess, tempfile
 from pypdf import PdfWriter
 renderer=shutil.which('rsvg-convert')
 if not renderer:raise SystemExit('--export requires rsvg-convert on PATH')
 with tempfile.TemporaryDirectory(prefix='lantern-board-') as directory:
  tmp=Path(directory)
  combined=tmp/'both-sides.svg'
  combined.write_text(svg(front+'<g transform="translate(1330 0)">'+rear+'</g>',2660))
  subprocess.run([renderer,'-o',str(OUT/'both-sides.png'),str(combined)],check=True)
  writer=PdfWriter()
  for i,page in enumerate((svg(front),svg(rear),*reference_pages())):
   source=tmp/f'{i}.svg';target=tmp/f'{i}.pdf'
   source.write_text(page)
   subprocess.run([renderer,'--format','pdf','-o',str(target),str(source)],check=True)
   writer.append(target)
  writer.write(OUT/'board-assembly.pdf')
  writer.close()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--export',action='store_true',help='also render PNG/PDF (requires rsvg-convert and pypdf)')
 args=parser.parse_args()
 report=validate()
 global ALL_ROUTES
 gaps=M.validate()
 ALL_ROUTES=R.plan()
 R.validate(ALL_ROUTES)
 report.update(minimum_body_gap_mm=round(gaps[0][0],3),wire_od_mm=M.WIRE_OD,rear_gap_mm=M.REAR_GAP)
 for w in WIRES:
  physical=next(r for r in ALL_ROUTES if r['id']==w['id'])
  w.update(physical)
  w['length_mm']=round(sum(math.dist(a,b) for a,b in zip(w['path'],w['path'][1:])),1)
 (OUT/'routing.json').write_text(json.dumps(ALL_ROUTES,indent=2)+'\n')
 front,rear=Drawing().draw(),Drawing(True).draw()
 rows='\n'.join(f'| {w["id"]} | {w["a"]} | {' → '.join(w['anchors'][1:])} | {w["net"]} | {"Bare tinned link" if w["bare"] else f"Insulated; centre {w['depth']} mm behind board"} |' for w in WIRES)
 pins='\n'.join(f'| {ref} | {p["pad"]} | {p["net"]} |' for ref,p in PINS.items())
 harness='\n'.join(f'| {ref} | {pad} | {label} | {next(w for w in ALL_ROUTES if w["id"]==ref)["depth"]:g} mm |' for ref,pad,net,label in HARNESS)
 (OUT/'WIRE_SCHEDULE.md').write_text('# Perfboard wire and solder schedule\n\nGenerated from `layout.py`. Front coordinates are retained on the mirrored rear view.\n\n## Cable attachments (solder side)\n\n| Cable | Pad | Other end | Centre behind board |\n|---|---|---|---|\n'+harness+'\n\n## Every board wire\n\n| Wire | From | To | Net | Construction |\n|---|---|---|---|---|\n'+rows+'\n\n## Every component lead and attachment pad\n\nFor resistors/capacitors `.1` and `.2` are drawing lead IDs. C2.1 is +; C2.2 is −. For diodes, .1 is anode and .2 is striped cathode. U1 numbers are actual IC pin numbers.\n\n| Lead | Pad | Net |\n|---|---|---|\n'+pins+'\n')
 buttons='<button data-net="">All wiring</button>'+''.join(f'<button data-net="{n}" style="border-color:{color}">{ESC(label)}</button>' for n,(color,label) in NETS.items())
 trs=''.join(f'<tr data-id="{w["id"]}" data-net="{w["net"]}" data-a="{w["a"]}" data-b="{w["b"]}"><td><button class="trace" aria-label="Show wire {w["id"]}">Show {w["id"]}</button></td><td>{w["a"]} → {w["b"]}</td><td>{ESC(NETS[w["net"]][1])}</td><td>{"Bare copper link" if w["bare"] else f"Insulated; {w['depth']:g} mm behind board"}</td></tr>' for w in WIRES)
 hrs=''.join(f'<tr><td>{r}</td><td>{p}</td><td>{ESC(l)}</td><td>{next(w for w in ALL_ROUTES if w["id"]==r)["depth"]:g} mm</td></tr>' for r,p,n,l in HARNESS)
 page=(OUT/'viewer.html').read_text()
 for key,value in {'BUTTONS':buttons,'FRONT':svg(front),'REAR':svg(rear),'WIRES':trs,'CABLES':hrs}.items():
  page=page.replace('{{'+key+'}}',value)
 (OUT/'index.html').write_text(page)
 if args.export:export(front,rear)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
