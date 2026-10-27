"""Generate a concise guide with one solder point per step, from the checked design."""
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
        if s.get('pad'):
            s['previous']=list(visits[s['pad']]);visits[s['pad']].append(s.get('ref',s.get('wire',title)))
        steps.append(s);return s['index']
    add('check','Disconnect all power','Battery and USB disconnected. Leave U1 out and JP1 open.',phase='Prepare')
    add('check','Check the parts before soldering','Board: 70 × 50 mm. C2: ≤Ø18 × 25 mm. C1/C3: ≤Ø10 × 4 mm. Check the other size limits in Build details.',phase='Prepare')
    add('check','Dry-fit the M3 mounting','Use two M3 nuts under each hole and four M3×10 screws. Aim for 14.8 mm below the board. Remove it for soldering.',phase='Prepare')
    add('check','Hold the board by its edges','Keep both faces off the bench. Use your insulated stranded 22 AWG; twist stripped ends gently and insert them untinned.',phase='Prepare')
    values={p['ref']:p['value'] for p in L.PARTS}
    instructions={
      'U1':'Empty socket: notch toward column X. Solder opposite corners first.',
      'MCU':'USB toward column X. Use the pre-soldered headers; no extra sockets.',
      'Q1':'Printed face toward row 18. Height including leads ≤22 mm.',
      'Q2':'Printed face toward column A. Height including leads ≤22 mm.',
      'D1':'Striped end in L05.', 'D3':'Striped end in S01.',
      'JP1':'Fit the header in R18/S18. Leave its shunt OFF.',
      'C1':'Rear: attach its own leads to R2 at C05/C01. Lay the disc flat, 6–10 mm below the solder face. Form its own leads to the template; no polarity.',
      'C3':'Rear: its own leads join U1 pin 14 (G10) to pin 7 (A13). Lay the disc flat, 6–10 mm below the solder face. Form its own leads to the template; no polarity.',
      'R3':'Rear: lay flat in the marked position, 5.5 mm off the solder face. Form its own leads to F13/G13; use the template.',
      'R4':'Rear: lay flat in the marked position, 5.5 mm off the solder face. Keep at least 26 mm of uncut lead on the C13 side; use the template.'}
    def component(ref,phase):
        pp=[(key,p) for key,p in L.PINS.items() if key.split('.')[0]==ref]
        if ref=='U1':pp.sort(key=lambda v:(v[0] not in ['U1.1','U1.8'],int(v[0].split('.')[1])))
        text=instructions.get(ref,'Fit the resistor in the marked holes. Leave 1 mm of straight lead beside its body before bending.')
        fit=add('fit','Fit '+ref+' · '+values.get(ref,{'MCU':'XIAO RP2040','U1':'DIP-14 socket','Q1':'pump MOSFET','Q2':'LED MOSFET'}.get(ref,'')),text,ref=ref,phase=phase)
        joints=[]
        for key,p in pp:
            detail='Solder this lead; trim to ≤1.5 mm. Joint height ≤2.5 mm.'
            if phase=='Underside parts':
                angle=L.DESIGN['tool_access'][key][0][1]
                detail='Solder its own lead onto this joint; do not force it into the hole. Touch the side of the joint with a ≤2 mm tip.'
                if ref in ['R3','R4']:detail+=' Approach from row 01; fit the capacitors later.'
            if p['net'].startswith('NC'):detail+=' Leave this pin unwired.'
            joints.append(add('solder','Solder '+key+' · '+p['pad'],detail,ref=ref,pad=p['pad'],phase=phase))
        parts.append(dict(ref=ref,name=ref,fit=fit,solder=joints,bounds=M.bounds()[ref],pins=[p['pad'] for _,p in pp],side='rear' if phase=='Underside parts' else 'front'))
    for ref in ['R1','R2','R5','R6','R7','D1','D3','U1','JP1','MCU','Q1','Q2']:component(ref,'Front components')
    add('check','Inspect the first joints','Check orientation and solder bridges. Keep U1 out and JP1 open.',phase='Inspect')
    add('check','Wires go over the component side','The short stripped ends turn along the back to the indicated joints. No bare buses or separate metal links.',phase='Insulated wires')
    for group in report['assembly_groups']:
        for name in group:
            w=byid[name];w.update(exit3d=R.cable_exit(w),surface='front',colour=NET_COLOUR[w['net']],length=route_length(w),segments=R.pieces(w),label=L.DESIGN['cables'].get(name,L.NETS[w['net']][1]),earlier_crossings=[],group=group)
            for t in w['tails']:pins['WIRE.'+t['id']]=dict(pad=t['anchor'],net=w['net'])
            strips='; '.join(t['anchor']+': '+str(math.ceil(R.length(t['path'])+3.1))+' mm' for t in w['tails'])
            text='Form the rounded loop using the template. Strip '+strips+'. '+('Fit together with '+next(n for n in group if n!=name)+' before soldering either wire.' if len(group)==2 else 'Insert into the marked empty holes; keep the insulation against the front face.')
            if not w['b']:text+=' Add the measured external run before cutting.'
            w['prepare']=add('wire','Prepare '+name+' · '+w['colour'],text,wire=name,phase='Insulated wires');w['joints']=[]
        if len(group)==2:add('check','Fit '+ ' + '.join(group)+' together','Match both loops before inserting their ends. Hold them with removable tape; do not force one through an already soldered loop.',wires=group,phase='Insulated wires')
        for name in group:
            w=byid[name]
            for t in w['tails']:
                w['joints'].append(add('solder','Anchor '+name+' · '+t['anchor'],'Solder the single stranded wire in this hole. Keep the loop relaxed and the strands together.',wire=name,pad=t['anchor'],phase='Insulated wires'))
                w['joints'].append(add('solder','Connect '+name+' · '+t['node'],'Bend this short end along the highlighted back-side path, then solder it to this joint. Keep it flat; trim any excess.',wire=name,pad=t['node'],phase='Insulated wires'))
            w['check']=w['joints'][-1]
    add('check','Check the board wiring','Check every listed wire for continuity and inspect neighbouring joints for bridges before adding the underside parts.',phase='Inspect')
    for ref in L.DESIGN['rear_order']:component(ref,'Underside parts')
    capfit=add('fit','Prepare C2 · 2200 µF / 25 V','Positive to red; striped negative to black. Keep the case ≤Ø18 × 25 mm. Sleeve the two lead joints separately.',ref='C2',phase='Large capacitor')
    aux=[]
    for i,(ref,pad,colour) in enumerate([('C2.1','F02','red'),('C2.2','F04','black')]):
        pg=L.DESIGN['pigtails'][i];path=[[x,y,-1.2-z] for x,y,z in pg['path']];cut=math.ceil((R.length(path)+8)/5)*5
        w=dict(id=pg['id'],a=pad,b=ref,anchor_a=pad,anchor_b=ref,net=L.PINS[ref]['net'],bare=False,od=1.8,colour=colour,surface='rear',depth=max(p[2] for p in pg['path']),path3d=path,path=[p[:2] for p in path],exit3d=[],segments=[(path,1.8)],anchors=[pad],label=ref,length=dict(formed=round(R.length(path),1),tails=1.2,trim=6.8,cut=cut),earlier_crossings=[],group=[pg['id']],joints=[])
        w['prepare']=add('wire','Prepare C2 '+colour+' pigtail','Form to the template; trim after fitting. Strip 3 mm at the board and 4 mm at the capacitor.',wire=w['id'],phase='Large capacitor')
        w['joints'].append(add('solder','Solder C2 '+colour+' lead · '+pad,'Insert from the back, flush with the front. Solder on the copper side; one wire through the hole.',pad=pad,wire=w['id'],phase='Large capacitor'))
        w['joints'].append(add('splice','Join C2 '+('positive' if colour=='red' else 'negative'),'Solder the '+colour+' pigtail to the '+('positive lead.' if colour=='red' else 'striped negative lead.')+' Slide its sleeve over the joint and shrink it.',wire=w['id'],point=path[-1],phase='Large capacitor'))
        w['check']=w['joints'][-1];aux.append(w)
    add('check','Fit the battery strap','Cut 350 mm from the existing ONE-WRAP roll. Thread the floor slots, fit the battery LED-side down, then place C2 under the loose strap.',phase='Large capacitor')
    add('check','Secure C2 independently','Lay C2 on the battery under its existing strap, along the pack’s length. Centre the strap on the case; keep both ends clear. Pull-test before mounting the board.',phase='Large capacitor')
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
    print(json.dumps(dict(steps=len(data['steps']),solder_operations=sum(s['kind']=='solder' for s in data['steps']),**data['report']),indent=2))
if __name__=='__main__':main()
