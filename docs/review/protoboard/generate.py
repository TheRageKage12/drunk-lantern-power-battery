"""Build both board faces, the interactive full layout, schedule, PNG and PDF."""
from pathlib import Path
import argparse,html,json,subprocess,tempfile,shutil
import layout as L
import routing as R
import mechanical as M
import assembly_guide as A
OUT=Path(__file__).resolve().parent
ESC=html.escape

def validate():return R.validate()
def svg(body,width=1330,height=1330):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{body}</svg>'

class Drawing:
 def __init__(self,data,rear=False):self.data=data;self.rear=rear;self.s=[];self.scale=15;self.ox=130;self.oy=400
 def pt(self,x,y):return self.ox+(70-x if self.rear else x)*self.scale,self.oy+y*self.scale
 def line(self,points,color,width=2,extra=''):
  d=' '.join(('M' if i==0 else 'L')+','.join(f'{v:.2f}'for v in self.pt(*p[:2])) for i,p in enumerate(points))
  self.s.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>')
 def rect(self,x,y,w,h,fill,extra=''):
  xx,yy=self.pt(x+w if self.rear else x,y);self.s.append(f'<rect x="{xx}" y="{yy}" width="{w*self.scale}" height="{h*self.scale}" fill="{fill}" stroke="#69756e" stroke-width="1.5" {extra}/>')
 def text(self,x,y,t,size=20,anchor='start'):
  self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="#27382e">{ESC(str(t))}</text>')
 def circle(self,x,y,r,fill,extra=''):
  xx,yy=self.pt(x,y);self.s.append(f'<circle cx="{xx}" cy="{yy}" r="{r*self.scale}" fill="{fill}" {extra}/>')
 def draw(self):
  self.s.append('<g font-family="Arial,sans-serif">');self.text(45,48,'SOLDER SIDE · mirrored' if self.rear else 'COMPONENT SIDE · USB right',29)
  self.text(45,84,'Short stripped ends and underside parts' if self.rear else 'Insulated loops · form with 4 mm bend radius',21)
  self.text(45,116,'Row 01 stays at the top. Hole names do not change when the board is flipped.',18)
  self.rect(0,0,70,50,'#faf3e5')
  for c in L.COLS:
   for r in range(1,19):self.circle(*L.mm(c+f'{r:02}'),.37,'#c5b48f')
  for x,y in L.MOUNTS:
   self.circle(x,y,5,'#f4f4ef','stroke="#93a096" stroke-dasharray="5 4"');self.circle(x,y,1.6,'white','stroke="#647367"')
  for part in self.data['parts']:
   x,y,w,h,z0,z1=part['bounds'];n=part['ref'];same=part['side']==('rear'if self.rear else'front')
   self.s.append(f'<g opacity="{.8 if same else .12}">');
   if part['side']=='front' and len(part['pins'])==2:self.line([L.mm(p) for p in part['pins']],'#6b7a70',4)
   self.rect(x,y,w,h,'#cddfd6' if n in ('MCU','U1') else '#ebd8ad');xx,yy=self.pt(x+w/2,y+h/2);self.text(xx,yy+6,n,22,'middle')
   if n=='C2':
    for i,pg in enumerate(self.data['pigtails']):
     xx,yy,z=pg['path'][-1];self.line([[xx,yy],[xx,3.5]],'#6b7a70',4);tx,ty=self.pt(xx,5);self.text(tx,ty,'+' if i==0 else '−',20,'middle')
   if n=='U1':self.circle(x+w-1,y+h/2,.55,'#3f5a48')
   if n in ('D1','D3'):self.line([[x+w-.6,y],[x+w-.6,y+h]],'#394b42',7)
   if n in ('Q1','Q2'):self.line([[x,y+h],[x+w,y+h]] if n=='Q1' else [[x,y],[x,y+h]],'#394b42',7)
   if part['side']=='rear' and n!='C2':
    for ref,p in self.data['rear_leads'].items():
     if ref.startswith(n+'.'):self.line(p,'#6b7a70',4)
   self.s.append('</g>')
  for w in self.data['routes']:
   self.s.append(f'<g class="wire" data-id="{w["id"]}" data-net="{w["net"]}"><title>{ESC(w["id"]+": "+w["a"]+" → "+str(w["b"] or w['label']))}</title>')
   for p,diam in w['segments']:
    bare=diam==1;same=(bare or w['surface']=='rear') if self.rear else (not bare and w['surface']!='rear');opacity=1 if same else .1
    self.line(p,'#fff',diam*5+3,f'opacity="{opacity}"');self.line(p,'#a6895f' if bare else self.data['colours'][w['colour']],diam*5,f'opacity="{opacity}"')
   self.s.append('</g>')
  bypad={}
  for ref,p in self.data['pins'].items():bypad.setdefault(p['pad'],[]).append((ref,p['net']))
  for pad,refs in bypad.items():
   net=refs[0][1];detail=pad+' · '+', '.join(r for r,n in refs)+' · '+net
   self.s.append(f'<g class="pad" tabindex="0" data-pad="{pad}" data-net="{net}" data-detail="{ESC(detail)}"><title>{ESC(detail)}</title>')
   self.circle(*L.mm(pad),.5,'#a3bcb0' if net.startswith('NC') else '#5a7866','stroke="#fff" stroke-width="1.5"');self.s.append('</g>')
  for c in L.COLS:
   xx,yy=self.pt(L.mm(c+'01')[0],-2.3);self.text(xx,yy,c,19,'middle')
  for r in range(1,19):
   xx,yy=self.pt(-2.3,L.mm('A'+f'{r:02}')[1]);self.text(xx,yy+6,f'{r:02}',19,'middle')
  self.text(45,1240,'70 × 50 mm board · existing mounting holes · 20 mm removable spacers',20)
  self.text(45,1275,'C2 mounts on a tie base on the floor. Check actual part sizes before soldering.',18)
  self.s.append('</g>');return ''.join(self.s)

def reference_pages(data):
 pages=[]
 for start in range(0,len(data['routes']),30):
  s=['<g font-family="Arial,sans-serif">'];s.append('<text x="45" y="55" font-size="28">WIRE CUTS AND SOLDER POINTS</text>')
  for i,w in enumerate(data['routes'][start:start+30]):
   text=f"{w['id']} · {w['colour']} · {' → '.join(w['anchors']+([w['b']] if w['surface']=='rear' else []))} · start {w['length']['cut']} mm"+(' + measured external run' if not w['b'] else '')
   s.append(f'<text x="45" y="{115+i*36}" font-size="20">{ESC(text)}</text>')
  s.append('<text x="45" y="1260" font-size="19">Trim after forming. Spare cut length is not an extra loop to leave on the board.</text></g>');pages.append(svg(''.join(s)))
 return pages

def export(front,rear,data):
 from pypdf import PdfWriter
 renderer=shutil.which('rsvg-convert');assert renderer,'rsvg-convert is required'
 with tempfile.TemporaryDirectory(prefix='lantern-board-') as temp:
  temp=Path(temp);combined=temp/'both.svg';combined.write_text(svg(front+'<g transform="translate(1330 0)">'+rear+'</g>',2660))
  subprocess.run([renderer,'-o',str(OUT/'both-sides.png'),str(combined)],check=True)
  writer=PdfWriter()
  for i,page in enumerate([svg(front),svg(rear),*reference_pages(data)]):
   f=temp/f'{i}.svg';pdf=temp/f'{i}.pdf';f.write_text(page);subprocess.run([renderer,'--format','pdf','-o',str(pdf),str(f)],check=True);writer.append(pdf)
  writer.write(OUT/'board-assembly.pdf');writer.close()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--export',action='store_true');args=parser.parse_args()
 data=A.make_data(R.plan());front=Drawing(data).draw();rear=Drawing(data,True).draw()
 buttons='<button data-net="">All wiring</button>'+''.join(f'<button data-net="{n}" style="border-color:{c}">{ESC(label)}</button>'for n,(c,label)in L.NETS.items())
 rows=''.join(f'<tr data-id="{w["id"]}" data-net="{w["net"]}" data-a="{w["a"]}" data-b="{w["b"] or w["label"]}" data-pads="{" ".join(w["anchors"])}"><td><button class="trace">Show {w["id"]}</button></td><td>{ESC(" → ".join(w["anchors"]+([w["b"]] if w["surface"]=="rear" else [])))}</td><td>{ESC(L.NETS[w["net"]][1])}</td><td>{w["colour"]} · {w["length"]["cut"]} mm'+(' + measured run' if not w['b'] else '')+'</td></tr>'for w in data['routes'])
 cables=''.join(f'<tr><td>{n}</td><td>{p}</td><td>{ESC(label)}</td><td>{net}</td></tr>'for n,p,net,label in L.HARNESS)
 page=(OUT/'viewer.html').read_text()
 for k,v in dict(BUTTONS=buttons,FRONT=svg(front),REAR=svg(rear),WIRES=rows,CABLES=cables).items():page=page.replace('{{'+k+'}}',v)
 (OUT/'index.html').write_text(page)
 schedule='# Board solder schedule\n\nGenerated from `design.json`. Hole names are assigned from the component side. The rear view is mirrored.\n\n| Wire | Solder points in order | Colour | Starting cut |\n|---|---|---|---|\n'
 for w in data['routes']:schedule+=f"| {w['id']} | {' → '.join(w['anchors']+([w['b']] if w['surface']=='rear' else []))} | {w['colour']} | {w['length']['cut']} mm"+(' + measured external run' if not w['b'] else '')+' |\n'
 schedule+='\n## Power harness\n\n'
 for j in L.DESIGN['harness']:schedule+='- **'+j['id']+':** '+', '.join(j['members'])+'.\n'
 schedule+='\nBuck IN− and OUT− must have continuity; only IN− gets a separate return wire. Pump and LED source returns join logic ground only at J_GND. D2 stays at the pump; C4 at the Hall sensor.\n\n## Component leads\n\n| Lead | Hole or existing joint | Connection |\n|---|---|---|\n'
 for ref,p in L.PINS.items():schedule+=f"| {ref} | {p['pad']} | {p['net']} |\n"
 (OUT/'WIRE_SCHEDULE.md').write_text(schedule)
 if args.export:export(front,rear,data)
 print('Generated full layout, schedule'+(', PNG and PDF'if args.export else''))
if __name__=='__main__':main()
