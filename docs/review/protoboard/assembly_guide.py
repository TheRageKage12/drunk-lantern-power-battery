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
# Planned NTE QW values: Vetco lists 5%; the NTE series sheet specifies 2%.
# Show both tolerance bands, as requested, without changing the resistance.
RESISTOR_BANDS={'100k':['brown','black','yellow'],'22k':['red','red','orange'],
                '10k':['brown','black','orange'],'4.7k':['yellow','violet','red'],
                '3.3k':['orange','orange','red']}

def route_length(w):
    formed=R.length(w['path3d'])+R.length(R.cable_exit(w));tails=sum(R.length(t['path'])+2.1 for t in w['tails'])
    # 6 mm is trimming stock, not an extra loop left on the finished board.
    return dict(formed=round(formed,1),tails=round(tails,1),trim=6,cut=math.ceil(formed+tails+6))

def assembly_order(routes):
    groups=R.validate(routes)['assembly_groups'];byid={w['id']:w for w in routes}
    return [byid[n] for group in groups for n in group]

def wire_actions(w):
    """Prepare both ends before insertion; keep trimming stock on bare ends."""
    tails=w['tails'];a=tails[0]
    for t in tails:t['strip_mm']=math.ceil(R.length(t['path'])+2.1)
    if len(tails)==2:
        # Keep the covered span at the planned length, rounded up by <1 mm.
        # The existing 6 mm trimming allowance becomes accessible bare stock.
        span=math.ceil(R.length(w['path3d']))
        spare=w['length']['cut']-span-sum(t['strip_mm'] for t in tails)
        assert spare>=0
        a['prepare_strip_mm']=a['strip_mm']+spare//2
        tails[1]['prepare_strip_mm']=tails[1]['strip_mm']+spare-spare//2
        w['covered_mm']=span
    else:
        a['prepare_strip_mm']=a['strip_mm']+3
    cut=f"Cut {w['length']['cut']} mm of {w['colour']} wire." if w['b'] else f"Use the cable calculator below to find the cut length for this {w['colour']} wire."
    if len(tails)==2:
        b=tails[1]
        strip=(f"Strip {a['prepare_strip_mm']} mm at each end." if a['prepare_strip_mm']==b['prepare_strip_mm'] else f"Strip {a['prepare_strip_mm']} mm at A; {b['prepare_strip_mm']} mm at B.")
        prepare=cut+' '+strip
        fit=f"Bend a loop about {round(w['depth']+w['od']/2)} mm high. With components facing you, insert A into {a['anchor']} and B into {b['anchor']}."
    else:
        prepare=cut+f" Strip {a['prepare_strip_mm']} mm at the board end only."
        fit=f"With components facing you, insert the bare end into {a['anchor']}. Route the insulated cable past the board edge as drawn."
    entries=' and '.join(t['anchor'] for t in tails)
    links='; '.join(t['anchor']+' against the existing pin at '+t['node'] for t in tails)
    nodes=' and '.join(t['node'] for t in tails)
    rings='copper ring' if len(tails)==1 else 'copper rings'
    attachment='the wire end to that pin' if len(tails)==1 else 'the wire ends to those pins'
    return [prepare,fit,
            ('After fitting both wires, turn' if len(w['group'])==2 else 'Turn')+f' the board over. Solder the wire to the {rings} around {entries}.',
            f'Bend the bare end from {links}.',
            'Trim each bare end just beyond its pin, leaving it touching the pin.',
            f'Reheat the existing solder at {nodes} to join {attachment}.']

def component_identity(ref):
    """Plain names and illustration labels, using the actual terminal assignments."""
    part=next((p for p in L.PARTS if p['ref']==ref),{})
    value=part.get('value','').replace('k',' kΩ').replace('uF',' µF')
    kind=part.get('kind',{'U1':'socket','MCU':'controller','Q1':'mosfet','Q2':'mosfet'}.get(ref))
    name={'resistor':value+' resistor','diode':'NTE585 diode','ceramic':value+' ceramic capacitor',
          'electrolytic':'2200 µF / 25 V capacitor','jumper':'two-pin header','socket':'14-pin socket',
          'controller':'XIAO RP2040 controller','mosfet':'IRLZ44N MOSFET'}[kind]
    note={'resistor':'Either way round. Match the resistance on the parts bag.',
          'diode':'The band marks the end that must go into '+L.PINS.get(ref+'.2',{}).get('pad','')+'.',
          'ceramic':'Either way round. Colour and markings may vary.',
          'electrolytic':'The minus stripe marks the negative leg: connect black there.',
          'jumper':'Leave the removable jumper cap off.',
          'socket':'Fit the empty socket now; the chip goes in later.',
          'controller':'The USB connector faces column X.',
          'mosfet':'Printed face toward '+('row 18.' if ref=='Q1' else 'column A.')}[kind]
    ends=[dict(pad=p['pad'],label=('Striped end' if key.endswith('.2') else 'Unstriped end') if kind=='diode' else key.split('.')[1])
          for key,p in L.PINS.items() if key.split('.')[0]==ref]
    identity=dict(kind=kind,name=name,note=note,ends=ends)
    if kind=='resistor':
        bands=RESISTOR_BANDS[part['value']]
        identity.update(bands=bands,band_variants=[dict(tolerance=5,bands=bands+['gold']),dict(tolerance=2,bands=bands+['red'])],
                        note=', '.join(bands)+', then gold (5%) or red (2%). Either way round.')
    return identity

def make_data(routes):
    report=R.validate(routes);byid={w['id']:w for w in routes};steps=[];visits=defaultdict(list);parts=[];pins=dict(L.PINS)
    def add(kind,title,text,**kw):
        s=dict(kind=kind,title=title,text=text,index=len(steps),**kw)
        s['pads']=list(dict.fromkeys(j['pad'] for j in s.get('joints',[])))
        s['previous']=list(dict.fromkeys(owner for pad in s['pads'] for owner in visits[pad]))
        for j in s.get('joints',[]):visits[j['pad']].append(j['owner'])
        steps.append(s);return s['index']
    instructions={
      'U1':'Fit the empty socket with its notch toward column X. Solder two opposite corners, then the remaining pins. Leave the chip out.',
      'MCU':'Fit the XIAO with USB toward column X, using its existing headers. Solder both rows of pins.',
      'Q1':'Fit with its printed face toward row 18. Keep the top within 22 mm of the board. Solder all three legs and clip off the excess.',
      'Q2':'Fit with its printed face toward column A. Keep the top within 22 mm of the board. Solder all three legs and clip off the excess.',
      'D1':'Put the unstriped end into H04 and the striped end into L05, from the component side. Solder both ends on the back and clip off the excess.',
      'D3':'Put the unstriped end into N01 and the striped end into S01, from the component side. Solder both ends on the back and clip off the excess.',
      'JP1':'Fit the header in R18/S18 and solder both pins. Leave the removable jumper cap off.',
    }
    def component(ref,phase):
        pp=[(key,p) for key,p in L.PINS.items() if key.split('.')[0]==ref]
        if ref=='U1':pp.sort(key=lambda v:(v[0] not in ['U1.1','U1.8'],int(v[0].split('.')[1])))
        text=instructions.get(ref,'Bend the legs to fit the marked holes. Insert the resistor from the component side, solder both ends on the back, then clip off the excess.')
        identity=component_identity(ref)
        title='Install the socket for chip U1' if ref=='U1' else 'Install '+identity['name']+' · '+ref
        actions=[]
        if ref in L.DESIGN['rear_bodies']:
            holes=' and '.join(p['pad'] for _,p in pp)
            title='Attach '+identity['name']+' · '+ref
            actions=[
                ('Turn the board over: exposed solder joints face you.' if ref==L.DESIGN['rear_order'][0] else 'Keep the exposed solder joints facing you.')+' Leave the existing connections in place.',
                f'Bend the metal legs as drawn to reach the existing {holes} joints. Keep the body raised as shown in the side view.',
                'Mark the legs where they meet the joints. Remove the part and trim at those marks before soldering, then refit.',
                'Hold each leg tip against its joint. Heat until solder melts around the tip; hold still until it sets. Repeat for the other leg.']
            text=' '.join(actions)
        fit=add('component',title,text,ref=ref,phase=phase,actions=actions,joints=[dict(pad=p['pad'],owner=ref) for _,p in pp])
        parts.append(dict(ref=ref,name=ref,identity=identity,fit=fit,solder=[fit],bounds=M.bounds()[ref],pins=[p['pad'] for _,p in pp],side='rear' if phase=='Underside parts' else 'front'))
    for ref in ['R1','R2','R5','R6','R7','D1','D3','U1','JP1','MCU','Q1','Q2']:component(ref,'Front components')
    add('check','Inspect the first joints','Check that every part faces the direction shown and that no solder accidentally joins neighbouring holes. Leave the installed 14-pin socket empty and the jumper cap off JP1’s two pins.',phase='Inspect')
    for group in report['assembly_groups']:
        joints=[]
        for name in group:
            w=byid[name];w.update(exit3d=R.cable_exit(w),surface='front',colour=NET_COLOUR[w['net']],length=route_length(w),segments=R.pieces(w),label=L.DESIGN['cables'].get(name,L.NETS[w['net']][1]),earlier_crossings=[],group=group)
            w['assembly_actions']=wire_actions(w)
            for t in w['tails']:pins['WIRE.'+t['id']]=dict(pad=t['anchor'],net=w['net'])
            for t in w['tails']:
                joints.extend([dict(pad=t['anchor'],owner=name),dict(pad=t['node'],owner=name)])
        text='Fit both loops together before soldering either wire. Select each wire below for its instructions.' if len(group)==2 else ''
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
        w.update(prepare=idx,joints=[idx],check=idx,assembly_actions=[
            f'Cut {cut} mm of {colour} wire.',
            'Remove enough plastic coating from each end to make its solder connection. Gently twist the exposed copper strands together.',
            steps[idx]['text']]);aux.append(w)
    add('check','Strap the battery and C2 in place','Cut 350 mm of ONE-WRAP and thread the floor slots. Fit the battery LED-side down and C2 along its top. Strap across C2’s middle, leaving both ends clear and at least 50 mm overlap. Pull-test: C2 must not slide.',phase='Large capacitor')
    parts.append(dict(ref='C2',name='C2',identity=component_identity('C2'),fit=capfit,solder=[],bounds=M.bounds()['C2'],pins=['F02','F04'],side='external'))
    for j in L.DESIGN['harness']:
        add('splice','Make '+j['id']+' · '+L.NETS[j['net']][1],'Join '+', '.join(j['members'])+'. Sleeve the entire joint and overlap each wire’s insulation. Keep it in the cable space beside the board.',phase='Power harness')
    add('check','Check the buck ground','With power disconnected, confirm buck IN− and OUT− have continuity. Only IN− needs the harness return; do not omit it.',phase='Power harness')
    add('check','Fit and inspect','Mount with two M3 nuts per hole and M3×10 screws. Front loops ≤35 mm; rear parts and wires ≤11 mm. Close the lid without pressing on anything.',phase='Final checks')
    add('check','Commission without loads','Plug the 74AHCT125 chip (U1) into its socket, notch toward column X. Set the buck to 5.0 V before connecting it. Continue with EL-10 in the build guide; follow SW-6 for USB.',phase='Final checks')
    source=(HERE/'design.json').read_bytes()+(HERE/'assembly_guide.py').read_bytes()
    return dict(version=hashlib.sha256(source).hexdigest()[:12],diameter=1.8,gap=M.REAR_GAP,routes=[byid[n] for g in report['assembly_groups'] for n in g]+aux,steps=steps,parts=parts,pins=pins,mounts=L.MOUNTS,colours=COLOURS,nets={n:dict(label=v[1],colour=NET_COLOUR[n])for n,v in L.NETS.items()},rear_leads=L.DESIGN['leads'],rear_bodies=L.DESIGN['rear_bodies'],offboard_cap=L.DESIGN['offboard_cap'],pigtails=L.DESIGN['pigtails'],report=report,source='Existing board and printed parts · Existing M3 nuts and M3×10 screws · 27 October 2026')

def main():
    routes=R.plan();data=make_data(routes)
    (HERE/'routing.json').write_text(json.dumps(routes,separators=(',',':'))+'\n')
    (HERE/'assembly.html').write_text((HERE/'assembly-template.html').read_text().replace('/*__ASSEMBLY_DATA__*/',json.dumps(data,separators=(',',':')).replace('</','<\\/')))
    print(json.dumps(dict(steps=len(data['steps']),solder_operations=sum(len(s.get('joints',[])) for s in data['steps']),**data['report']),indent=2))
if __name__=='__main__':main()
