"""Generate complete assembly tasks, retaining every joint in the checked design."""
from pathlib import Path
import json,math,hashlib
from collections import defaultdict
import layout as L
import routing as R
import mechanical as M
HERE=Path(__file__).resolve().parent
COLOURS={'red':'#c42d32','black':'#292c32','white':'#fafafa','blue':'#2363bb','yellow':'#efd04a','green':'#2f8451'}
NET_COLOUR=dict(VLOAD='red',GND='black',**{'5V_REG':'white','AFTER_D1':'white','XIAO_5V':'white','3V3':'green'},HALL='green',SW='yellow',TWIST='yellow',ADC='yellow',PWM_P='blue',GATE_P='blue',PWM_L='blue',GATE_L='blue',DRAIN_P='blue',DRAIN_L='yellow')

def route_length(w):
    formed=R.length(w['path3d'])+R.length(R.cable_exit(w));tails=sum(R.length(t['path'])+2.1 for t in w['tails'])
    # 6 mm is trimming stock, not an extra loop left on the finished board.
    return dict(formed=round(formed,1),tails=round(tails,1),trim=6,cut=math.ceil(formed+tails+6))

def assembly_order(routes):
    groups=R.validate(routes)['assembly_groups'];byid={w['id']:w for w in routes}
    return [byid[n] for group in groups for n in group]

def make_data(routes):
    report=R.validate(routes);byid={w['id']:w for w in routes};steps=[];visits=defaultdict(list);parts=[];pins=dict(L.PINS)
    def add(kind,title,text,**kw):
        s=dict(kind=kind,title=title,text=text,index=len(steps),**kw)
        s['pads']=list(dict.fromkeys(j['pad'] for j in s.get('joints',[])))
        s['previous']=list(dict.fromkeys(owner for pad in s['pads'] for owner in visits[pad]))
        for j in s.get('joints',[]):visits[j['pad']].append(j['owner'])
        steps.append(s);return s['index']
    values={p['ref']:p['value'] for p in L.PARTS}
    instructions={
      'U1':'Fit the empty socket with its notch toward column X. Solder two opposite corners, then the remaining pins. Leave the chip out.',
      'MCU':'Fit the XIAO with USB toward column X, using its existing headers. Solder both rows of pins.',
      'Q1':'Fit with its printed face toward row 18. Keep the top within 22 mm of the board. Solder all three legs and clip off the excess.',
      'Q2':'Fit with its printed face toward column A. Keep the top within 22 mm of the board. Solder all three legs and clip off the excess.',
      'D1':'Fit the diode with its striped end in L05. Solder both ends on the back and clip off the excess.',
      'D3':'Fit the diode with its striped end in S01. Solder both ends on the back and clip off the excess.',
      'JP1':'Fit the header in R18/S18 and solder both pins. Leave the removable shunt off.',
      'C1':'Lay the disc flat on the back, following the lead template. Solder its legs onto C05 and C01; either way round. Keep it clear of the board and nearby joints.',
      'C3':'Lay the disc flat on the back, following the lead template. Solder its legs onto G10 and A13; either way round. Keep it clear of the board and nearby joints.',
      'R3':'Form the legs to the template and lay the resistor flat on the back. Solder onto F13 and G13, approaching from row 01. Clip excess only after fitting.',
      'R4':'Keep the long leg uncut until fitted. Form to the template, lay flat on the back and solder onto C13 and D13, approaching from row 01. Then clip any excess.'}
    def component(ref,phase):
        pp=[(key,p) for key,p in L.PINS.items() if key.split('.')[0]==ref]
        if ref=='U1':pp.sort(key=lambda v:(v[0] not in ['U1.1','U1.8'],int(v[0].split('.')[1])))
        text=instructions.get(ref,'Bend the legs to fit the marked holes. Insert the resistor from the component side, solder both ends on the back, then clip off the excess.')
        fit=add('component','Install '+ref+' · '+values.get(ref,{'MCU':'XIAO RP2040','U1':'DIP-14 socket','Q1':'pump MOSFET','Q2':'LED MOSFET'}.get(ref,'')),text,ref=ref,phase=phase,joints=[dict(pad=p['pad'],owner=ref) for _,p in pp])
        parts.append(dict(ref=ref,name=ref,fit=fit,solder=[fit],bounds=M.bounds()[ref],pins=[p['pad'] for _,p in pp],side='rear' if phase=='Underside parts' else 'front'))
    for ref in ['R1','R2','R5','R6','R7','D1','D3','U1','JP1','MCU','Q1','Q2']:component(ref,'Front components')
    add('check','Inspect the first joints','Check orientation and solder bridges. Keep U1 out and JP1 open.',phase='Inspect')
    for group in report['assembly_groups']:
        joints=[]
        for name in group:
            w=byid[name];w.update(exit3d=R.cable_exit(w),surface='front',colour=NET_COLOUR[w['net']],length=route_length(w),segments=R.pieces(w),label=L.DESIGN['cables'].get(name,L.NETS[w['net']][1]),earlier_crossings=[],group=group)
            for t in w['tails']:pins['WIRE.'+t['id']]=dict(pad=t['anchor'],net=w['net'])
            for t in w['tails']:
                joints.extend([dict(pad=t['anchor'],owner=name),dict(pad=t['node'],owner=name)])
        text=('Fit both loops together before soldering either wire. ' if len(group)==2 else 'Fit the loop shown over the component side. ')
        text+='On the back, solder each wire in its own hole, then bend its stripped end along the shown path and solder it to the connected joint. Clip excess.'
        idx=add('wire','Install '+' + '.join(group),text,wires=group,phase='Insulated wires',joints=joints)
        for name in group:byid[name].update(prepare=idx,joints=[idx],check=idx)
    add('check','Check the board wiring','Check every listed wire for continuity and inspect neighbouring joints for bridges before adding the underside parts.',phase='Inspect')
    for ref in L.DESIGN['rear_order']:component(ref,'Underside parts')
    capfit=len(steps)
    aux=[]
    for i,(ref,pad,colour) in enumerate([('C2.1','F02','red'),('C2.2','F04','black')]):
        pg=L.DESIGN['pigtails'][i];path=[[x,y,-1.2-z] for x,y,z in pg['path']];cut=math.ceil((R.length(path)+8)/5)*5
        w=dict(id=pg['id'],a=pad,b=ref,anchor_a=pad,anchor_b=ref,net=L.PINS[ref]['net'],bare=False,od=1.8,colour=colour,surface='rear',depth=max(p[2] for p in pg['path']),path3d=path,path=[p[:2] for p in path],exit3d=[],segments=[(path,1.8)],anchors=[pad],label=ref,length=dict(formed=round(R.length(path),1),tails=1.2,trim=6.8,cut=cut),earlier_crossings=[],group=[pg['id']],joints=[])
        polarity='positive' if colour=='red' else 'striped negative'
        idx=add('wire','Connect C2 · '+colour+' lead (2200 µF / 25 V)','Form the wire to the template. Insert into '+pad+' from the back, flush with the front, and solder on the back. Slide on heat-shrink, solder the other end to C2’s '+polarity+' leg, then cover that joint and shrink.',wires=[w['id']],ref='C2',points=[path[-1]],joints=[dict(pad=pad,owner=w['id'])],phase='Large capacitor')
        w.update(prepare=idx,joints=[idx],check=idx);aux.append(w)
    add('check','Strap the battery and C2 in place','Cut 350 mm of ONE-WRAP and thread the floor slots. Fit the battery LED-side down and C2 along its top. Strap across C2’s middle, leaving both ends clear and at least 50 mm overlap. Pull-test: C2 must not slide.',phase='Large capacitor')
    parts.append(dict(ref='C2',name='C2',fit=capfit,solder=[],bounds=M.bounds()['C2'],pins=['F02','F04'],side='external'))
    for j in L.DESIGN['harness']:
        add('splice','Make '+j['id']+' · '+L.NETS[j['net']][1],'Join '+', '.join(j['members'])+'. Sleeve the entire joint and overlap each wire’s insulation. Keep it in the cable space beside the board.',phase='Power harness')
    add('check','Check the buck ground','With power disconnected, confirm buck IN− and OUT− have continuity. Only IN− needs the harness return; do not omit it.',phase='Power harness')
    add('check','Fit and inspect','Mount with two M3 nuts per hole and M3×10 screws. Front loops ≤35 mm; rear parts and wires ≤11 mm. Close the lid without pressing on anything.',phase='Final checks')
    add('check','Commission without loads','Insert U1, notch toward column X. Set the buck to 5.0 V before connecting it. Continue with EL-10 in the build guide; follow SW-6 for USB.',phase='Final checks')
    source=(HERE/'design.json').read_bytes()+(HERE/'assembly_guide.py').read_bytes()
    return dict(version=hashlib.sha256(source).hexdigest()[:12],diameter=1.8,gap=M.REAR_GAP,routes=[byid[n] for g in report['assembly_groups'] for n in g]+aux,steps=steps,parts=parts,pins=pins,mounts=L.MOUNTS,colours=COLOURS,nets={n:dict(label=v[1],colour=NET_COLOUR[n])for n,v in L.NETS.items()},rear_leads=L.DESIGN['leads'],rear_bodies=L.DESIGN['rear_bodies'],offboard_cap=L.DESIGN['offboard_cap'],pigtails=L.DESIGN['pigtails'],report=report,source='Existing board and printed parts · Existing M3 nuts and M3×10 screws · 27 October 2026')

def main():
    routes=R.plan();data=make_data(routes)
    (HERE/'routing.json').write_text(json.dumps(routes,separators=(',',':'))+'\n')
    (HERE/'assembly.html').write_text((HERE/'assembly-template.html').read_text().replace('/*__ASSEMBLY_DATA__*/',json.dumps(data,separators=(',',':')).replace('</','<\\/')))
    print(json.dumps(dict(steps=len(data['steps']),solder_operations=sum(len(s.get('joints',[])) for s in data['steps']),**data['report']),indent=2))
if __name__=='__main__':main()
