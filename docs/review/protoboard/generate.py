"""Validate and build the board viewer/schedule; --export also renders the PNG and PDF."""
from pathlib import Path
from collections import defaultdict
import argparse, heapq, math, html, json
from layout import *
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
        if w['bare']:assert math.dist(mm(a),mm(b))<2.55,w
        parent[root(a)]=root(b)
    groups=defaultdict(set)
    for pad,(ref,net) in BY_PAD.items():groups[net].add(root(pad))
    assert all(len(g)==1 for n,g in groups.items()),groups
    # Mechanical pins with no external connection must remain separate, not tied to ground.
    assert sum(n.startswith('NC') for _,n in BY_PAD.values())==8
    assert len(HARNESS)==14 and len(PARTS)==13 and len(PINS)==76
    return {'occupied_pads':len(PINS),'wires':len(WIRES),'nets':len(NETS),'unused_device_pins':8,
            'result':'All intended nets connected; no cross-net wires; no occupied pad in mount keepouts.'}

def gp(pad):
    c,r=cr(pad);return(c*4,r*4)
def xy(g):return(ORIGIN[0]+g[0]*PITCH/4,ORIGIN[1]+g[1]*PITCH/4)
used={gp(p) for p in BY_PAD}
blocked=set()
for gx in range(-7,99):
 for gy in range(-3,72):
  x,y=xy((gx,gy))
  if any(abs(x-mx)<5.25 and abs(y-my)<5.25 for mx,my in MOUNTS):blocked.add((gx,gy))
occ=defaultdict(int)

def route(w):
    start,goal=gp(w['a']),gp(w['b'])
    if w['bare']:
        a,b=sorted([start,goal]);path=[(x,a[1]) for x in range(a[0],b[0]+1)]
        if path[0]!=start:path.reverse()
    else:
        forbidden=set(blocked)
        for p in used-{start,goal}:
            for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]:forbidden.add((p[0]+dx,p[1]+dy))
        def h(p):return abs(p[0]-goal[0])+abs(p[1]-goal[1])
        first=(start[0],start[1],-1);dist={first:0};prev={};q=[(h(start),0,first)]
        last=None
        while q:
            _,cost,state=heapq.heappop(q)
            if cost!=dist[state]:continue
            p=state[:2]
            if p==goal:last=state;break
            for d,(dx,dy) in enumerate([(1,0),(-1,0),(0,1),(0,-1)]):
                n=(p[0]+dx,p[1]+dy)
                if n in forbidden or not(-7<=n[0]<=98 and -3<=n[1]<=71):continue
                # Prefer spaced routes; crossing another insulated wire is allowed.
                penalty=occ[n]*8+sum(occ[(n[0]+a,n[1]+b)] for a,b in [(1,0),(-1,0),(0,1),(0,-1)])*1.6
                if h(n)<3 or h(start)<3:penalty=0
                nc=cost+1+penalty+(0.7 if state[2]!=-1 and d!=state[2] else 0)
                ns=(*n,d)
                if nc<dist.get(ns,1e9):dist[ns]=nc;prev[ns]=state;heapq.heappush(q,(nc+h(n),nc,ns))
        assert last,('route failed',w)
        path=[]
        while last!=first:path.append(last[:2]);last=prev[last]
        path.append(start);path.reverse()
    assert not(set(path)&blocked),(w,'wire through mounting pad')
    for p in path[1:-1]:occ[p]+=1
    corners=[path[0]]
    for i in range(1,len(path)-1):
        if (path[i][0]-path[i-1][0],path[i][1]-path[i-1][1])!=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1]):corners.append(path[i])
    corners.append(path[-1]);w['path']=[xy(p) for p in corners]
    w['length_mm']=round((len(path)-1)*PITCH/4,1)

class Drawing:
 def __init__(self,rear=False):self.s=[];self.rear=rear;self.k=16;self.ox=88;self.oy=266
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
  # component outlines on rear stay faint, showing what each pin belongs to.
  f='#eef2f7' if self.rear else '#d2e8f4'
  self.rect(3.0,22.45,21,17.8,f)
  self.rect(0.5,27.0,4.0,8.8,'#c7d0da')
  self.mt(13.5,30,'XIAO',23);self.mt(13.5,32.5,'RP2040',18);self.mt(2.4,31.7,'USB',12)
  self.rect(27.2,21.6,10.5,19.6,'#e0e4f1')
  self.mt(32.45,30,'U1',20);self.mt(32.45,33,'AHCT125',13)
  self.line([(30.7,21.6),(30.7,23),(34.2,23),(34.2,21.6)],'#475569',2)
  for ref,row in [('Q1',10),('Q2',14)]:
   x,y=mm('Q'+str(row));self.rect(x-5.2,y-2.25,10.4,4.5,'#d9dce2')
   self.mt(x,y-2.8,ref+'  IRLZ44N',15)
   # Printed face points to bottom edge; top-view lead order is G,D,S left to right.
   self.line([(x-5.2,y+2.2),(x+5.2,y+2.2)],'#253448',5)
   self.mt(x,y+4.4,'printed face ↓',12)
  for p in PARTS:
   a,b=mm(p['a']),mm(p['b']);kind=p['kind'];ref=p['ref']
   if kind=='electrolytic':
    self.rect(25,.5,25,18,'#fae2b1','#b18745')
    self.line([a,(25,a[1])],'#b96500',3);self.line([b,(25,b[1])],'#334155',3)
    self.mt(37,10,'C2 • flat',20);self.mt(37,12.5,'2200 µF / 25 V',17)
    self.mt(37,15.5,'case ≤25 × Ø18 mm',13)
    self.mt(a[0]-1.2,a[1]-0.3,'+',19);self.mt(b[0]-1.2,b[1]+1.7,'−',19)
    continue
   if kind=='jumper':
    self.rect(a[0]-1,a[1]-1,4.54,2,'#d3e3f3');self.mt(a[0]+1.27,a[1]+3,'JP1',15);continue
   self.line([a,b],'#758195',2.6)
   mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
   if kind=='ceramic':
    self.rect(mx-2.1,my-1.1,4.2,2.2,'#f5ca84');self.mt(mx,my-1.6,ref,15)
   else:
    vertical=a[0]==b[0];length=5.6 if kind=='resistor' else 5.2;width=2.0 if kind=='resistor' else 2.6
    self.rect(mx-width/2 if vertical else mx-length/2,my-length/2 if vertical else my-width/2,width if vertical else length,length if vertical else width,'#eddbb9' if kind=='resistor' else '#6e7786')
    px,py=self.point(mx,my)
    self.text(px,py+4,ref,12,'middle','#283649' if kind=='resistor' else 'white',extra=f'transform="rotate({-90 if vertical else 0} {px} {py})"')
    if kind=='diode':
     if vertical:self.line([(mx-width/2,my+length/2-.7),(mx+width/2,my+length/2-.7)],'#f8fafc',4)
     else:self.line([(mx+length/2-.7,my-width/2),(mx+length/2-.7,my+width/2)],'#f8fafc',4)
     self.mt(b[0]+(1 if vertical else 0),b[1]+1.7,'K',12)
 def draw(self):
  self.add('<g font-family="Arial, sans-serif">')
  self.text(42,38,'SOLDER SIDE — mirrored' if self.rear else 'COMPONENT SIDE — USB at left',29)
  self.text(42,70,'Flip the board left ↔ right; top stays top. Pad names do not change.' if self.rear else '70 × 50 mm • 24 × 18 holes • 2.54 mm pitch • all point-to-point wires are on rear.',18)
  self.text(42,100,'Insulated wires cross without joining. Solder only at marked endpoints; bends are not joints.' if self.rear else 'Solid dots: through-hole leads. Square ports: rear-only cable attachment pads.',17)
  self.text(42,127,'Only W01, W02 and W05–W07 are short bare bus links. All other links are insulated.' if self.rear else 'Coordinates are assigned by this drawing; supplier lettering may be on the opposite face.',17)
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
   # Flying leads: solder to rear pad without pushing a second wire through a populated hole.
   for idx,(ref,pad,net,label) in enumerate(HARNESS):
    x,y=mm(pad)
    if idx<10:
     end=(x+(.15 if idx%2==0 else -1.2),-7 if idx%2==0 else -3.8)
     pts=[(x,y),(end[0],y-.4),end]
    else:
     end=(73.1,17.0+(idx-10)*6.0);pts=[(x,y),(x+.85,y+.85),(72.1,y+.85+(idx-10)*1.25),end]
    self.add(f'<g class="harness" data-net="{net}"><title>{ref}: {pad} → {ESC(label)}</title>')
    self.line(pts,'white',7);self.line(pts,NETS[net][0],3.4,True)
    self.mt(end[0],end[1]-.5,ref,12)
    self.add('</g>')
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
   for row in [10,14]:
    for col,lab in zip('PQR','GDS'):
     x,y=mm(f'{col}{row:02d}');self.mt(x,y+1.55,lab,13)
  for c in range(24):
   x,_=mm(COLS[c]+'01');self.mt(x,-1.1,COLS[c],16);self.mt(x,52.0,COLS[c],16)
  for r in range(18):
   _,y=mm('A'+f'{r+1:02d}');self.mt(-1.7,y+.35,f'{r+1:02d}',15);self.mt(71.7,y+.35,f'{r+1:02d}',15)
  self.text(42,1146,'Solder-side drawing shows every wire; use the wire schedule or interactive net filter to trace crowded areas.' if self.rear else 'U1 notch ↑   •   Q1/Q2 printed faces ↓   •   D1 stripe → Q17   •   D3 stripe → W18   •   C2 + H02 / − H04',17)
  self.text(42,1176,'Grey squares: 9 × 9 mm mounting keep-outs. Drill centres: x=15/55, y=15/45 mm from front top-left.',16)
  self.text(42,1204,'Grid offsets are nominal. Verify the board and dry-fit C2 before drilling or soldering. This is not a 1:1 drill template.',16)
  self.add('</g>');return ''.join(self.s)

def svg(body,width=1330,height=1230):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{body}</svg>'


def reference_pages():
 d=Drawing();d.add('<g font-family="Arial, sans-serif">')
 d.text(42,45,'CABLE CONNECTIONS AND COLOUR KEY',29)
 d.text(42,85,'Dashed leads on the solder-side drawing. Attach to the rear copper pads.',19)
 for i,(ref,pad,net,label) in enumerate(HARNESS):
  y=135+i*38;d.text(48,y,ref,18);d.text(130,y,pad,18);d.text(230,y,label,18,color=NETS[net][0])
 d.text(42,705,'OFF-BOARD CONNECTIONS',23)
 lines=[
 'Battery + → J1 centre and S1 input. S1 output → H01. Battery − → J1 sleeve and H02.',
 'Leave J1 switched contact unused. Set the buck output to 5.0 V before connecting H05/H06.',
 'D2 NTE586 across pump terminals: stripe to pump +. C4 0.1 µF across A3144 pins 1–2.',
 'A3144: printed face toward you, leads down; pins 1/2/3 = +5V/GND/HALL.',
 'Twist switch COM → GND, NO → SW; NC unused. Lock cable uses the JST PH pair.',
 'JP1: fit shunt for battery operation; remove for USB and follow build-guide power procedure.'
 ]
 for i,line in enumerate(lines):d.text(42,744+i*28,line,17)
 for i,(net,(color,label)) in enumerate(NETS.items()):
  col,row=divmod(i,4);d.text(42+col*318,965+row*38,'● '+label,16,color=color)
 d.text(42,1165,'Cable H02 is an identifier, not a pad: it attaches to N02. Pad H02 is C2 positive.',17)
 d.add('</g>');connections=svg(''.join(d.s))
 d=Drawing();d.add('<g font-family="Arial, sans-serif">')
 d.text(42,45,'WIRE-BY-WIRE SOLDER SCHEDULE',29)
 d.text(42,82,'Use component-side pad names on both faces. All links on rear; solder only at their two endpoints.',18)
 for i,w in enumerate(WIRES):
  col,row=divmod(i,26);x=42+col*650;y=162+row*35
  d.text(x,y,w['id'],18);d.text(x+70,y,w['a']+' → '+w['b'],18)
  d.text(x+235,y,w['net'],16,color=NETS[w['net']][0])
  d.text(x+400,y,'BARE link' if w['bare'] else 'insulated',16)
 d.text(42,1140,'Q02 and L16 are wire junction pads; no component goes in these holes.',18)
 d.text(42,1175,'Crossings and bends are not joints. Keep all other bare metal inside a solder fillet.',18)
 d.add('</g>');return connections,svg(''.join(d.s))

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
 for w in sorted(WIRES,key=lambda w:(not w['bare'], {'GATE_P':0,'GATE_L':0,'GND':2}.get(w['net'],1),math.dist(mm(w['a']),mm(w['b'])))):
  route(w)
 for w in WIRES:assert w['path'][0]==mm(w['a']) and w['path'][-1]==mm(w['b'])
 front,rear=Drawing().draw(),Drawing(True).draw()
 rows='\n'.join(f'| {w["id"]} | {w["a"]} | {w["b"]} | {w["net"]} | {"Bare adjacent-pad link" if w["bare"] else "Insulated rear wire"} |' for w in WIRES)
 pins='\n'.join(f'| {ref} | {p["pad"]} | {p["net"]} |' for ref,p in PINS.items())
 harness='\n'.join(f'| {ref} | {pad} | {label} |' for ref,pad,net,label in HARNESS)
 (OUT/'WIRE_SCHEDULE.md').write_text('# Perfboard wire and solder schedule\n\nGenerated from `layout.py`. Front coordinates are retained on the mirrored rear view.\n\n## Cable attachments (solder side)\n\n| Cable | Pad | Other end |\n|---|---|---|\n'+harness+'\n\n## Every board wire\n\n| Wire | From | To | Net | Construction |\n|---|---|---|---|---|\n'+rows+'\n\n## Every component lead and attachment pad\n\nFor resistors/capacitors `.1` and `.2` are drawing lead IDs. C2.1 is +; C2.2 is −. For diodes, .1 is anode and .2 is striped cathode. U1 numbers are actual IC pin numbers.\n\n| Lead | Pad | Net |\n|---|---|---|\n'+pins+'\n')
 buttons='<button data-net="">All wiring</button>'+''.join(f'<button data-net="{n}" style="border-color:{color}">{ESC(label)}</button>' for n,(color,label) in NETS.items())
 trs=''.join(f'<tr data-id="{w["id"]}" data-net="{w["net"]}" data-a="{w["a"]}" data-b="{w["b"]}"><td><button class="trace" aria-label="Show wire {w["id"]}">Show {w["id"]}</button></td><td>{w["a"]} → {w["b"]}</td><td>{ESC(NETS[w["net"]][1])}</td><td>{"Bare copper link" if w["bare"] else "Insulated wire"}</td></tr>' for w in WIRES)
 hrs=''.join(f'<tr><td>{r}</td><td>{p}</td><td>{ESC(l)}</td></tr>' for r,p,n,l in HARNESS)
 page=(OUT/'viewer.html').read_text()
 for key,value in {'BUTTONS':buttons,'FRONT':svg(front),'REAR':svg(rear),'WIRES':trs,'CABLES':hrs}.items():
  page=page.replace('{{'+key+'}}',value)
 (OUT/'index.html').write_text(page)
 if args.export:export(front,rear)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
