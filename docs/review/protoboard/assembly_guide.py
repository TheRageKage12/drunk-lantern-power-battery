"""Generate complete assembly tasks, retaining every joint in the checked design."""
from pathlib import Path
import json,math,hashlib
from collections import defaultdict
import layout as L
import routing as R
import mechanical as M
import offboard as O
import verification as V
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
    cut=f"Cut {w['length']['cut']} mm of {w['colour']} wire."
    if len(tails)==2:
        b=tails[1]
        strip=(f"Strip {a['prepare_strip_mm']} mm at each end." if a['prepare_strip_mm']==b['prepare_strip_mm'] else f"Strip {a['prepare_strip_mm']} mm from one end (A), {b['prepare_strip_mm']} mm from the other (B).")
        prepare=cut+' '+strip
        ends=(f"the ends through {a['anchor']} and {b['anchor']}" if a['prepare_strip_mm']==b['prepare_strip_mm'] else f"A through {a['anchor']} and B through {b['anchor']}")
        fit=f"From the component side, insert {ends}, leaving a loop about {round(w['depth']+w['od']/2)} mm above the board."
    else:
        prepare=cut+f" Strip {a['prepare_strip_mm']} mm at the board end only."
        fit=f"With components facing you, insert the bare end into {a['anchor']}. Route the insulated cable past the board edge as drawn."
    entries=' and '.join(t['anchor'] for t in tails)
    links='; '.join(t['anchor']+' → pin '+t['node'] for t in tails)
    rings='copper ring' if len(tails)==1 else 'copper rings'
    actions=[prepare,fit,
            ('After fitting both wires, turn' if len(w['group'])==2 else 'Turn')+f' the board over. Solder the wire to the {rings} around {entries}.',
            f'Bend the bare ends to touch the existing pins: {links}.',
            'Trim the ends just past those pins.',
            'Solder each wire end onto its pin’s existing joint.']
    if len(tails)==1:
        actions[3]=f"Bend the bare end underneath to touch the existing pin at {a['node']}."
        actions[4]='Trim the bare end just past that pin.'
        actions[5]='Solder the wire onto the pin’s existing joint.'
    if not w['b']:
        actions.append(f"Label the free end ‘{w['outbound']['tag']}’ and leave it insulated and unconnected for now.")
    return actions

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
            if ref in ('C1','C3'):
                actions.insert(0,'Check the capacitor is marked 104 or 0.1 µF. Either leg can go to either marked joint.')
            if ref in ('R3','R4'):
                actions.insert(0,'Before attaching it, measure across the loose resistor’s legs with the meter on Ω: 9.4–10.6 kΩ. Once installed, other parts can change the reading.')
            text=' '.join(actions)
        fit=add('component',title,text,ref=ref,phase=phase,actions=actions,joints=[dict(pad=p['pad'],owner=ref) for _,p in pp])
        if ref in L.DESIGN['rear_bodies']:
            points=[p['pad'] for _,p in pp]
            steps[fit].update(check_setup='Power disconnected · inspect both new joints before adding the next part.',
                check_note='The meter cannot reliably measure a capacitor’s value while it is connected to the rest of this circuit.' if ref in ('C1','C3') else '',
                checks=[V.row('No new solder short',points[1],points[0],'Must not remain below 10 Ω. A rising capacitor reading is normal; inspect both new joints if it stays low.')])
        parts.append(dict(ref=ref,name=ref,identity=identity,fit=fit,solder=[fit],bounds=M.bounds()[ref],pins=[p['pad'] for _,p in pp],side='rear' if phase=='Underside parts' else 'front'))
    for ref in ['R1','R2','R5','R6','R7','D1','D3','U1','JP1','MCU','Q1','Q2']:component(ref,'Front components')
    add('check','Test the first components','',phase='Inspect',
        actions=['Check D1’s stripe is at L05 and D3’s stripe at S01. The socket notch and USB face column X; Q1’s printed face points to row 18, Q2’s to column A.',
                 'Look between the solder joints: no loose copper strands or solder joining separate copper rings. Gently move each part; its legs must stay fixed in their joints.'],
        check_setup=V.OFF+' '+V.METER,checks=V.first(),check_note='Measure the solder joints on the back. These resistor ranges allow either supplied tolerance plus meter error. Test diodes in diode mode, not the beep mode. If your diode result differs, verify the meter on a spare diode before continuing.')
    for group in report['assembly_groups']:
        joints=[]
        for name in group:
            w=byid[name];w.update(exit3d=R.cable_exit(w),surface='front',colour=NET_COLOUR[w['net']],length=route_length(w),segments=R.pieces(w),label=L.DESIGN['cables'].get(name,L.NETS[w['net']][1]),earlier_crossings=[],group=group)
            if not w['b']:
                w['outbound']=O.plan(w,w['length']['cut'])
                w['length']['cut']=w['outbound']['cut_mm']
            w['assembly_actions']=wire_actions(w)
            for t in w['tails']:pins['WIRE.'+t['id']]=dict(pad=t['anchor'],net=w['net'])
            for t in w['tails']:
                joints.extend([dict(pad=t['anchor'],owner=name),dict(pad=t['node'],owner=name)])
        text='Fit both loops together before soldering either wire.' if len(group)==2 else ''
        title='Install '+' + '.join(group)
        if len(group)==1 and not byid[group[0]]['b']:
            out=byid[group[0]]['outbound']
            title='Attach '+(out['title'] if out['title'].startswith(('LED','Hall','5')) else out['title'][0].lower()+out['title'][1:])+' · wire '+group[0]
            text='To '+out['destination'].lower()+'. Attach only the board end in this step.'
        idx=add('wire',title,text,wires=group,phase='Insulated wires',joints=joints,
                check_setup='Power disconnected · meter on Ω.',checks=[c for name in group for c in V.wire(byid[name])],
                check_note='Gently move the insulated wire: the reading must stay steady and the joints must not move. Check that no loose strand touches a neighbouring joint.' )
        for name in group:byid[name].update(prepare=idx,joints=[idx],check=idx)
    add('check','Test the wiring before covering it','',phase='Inspect',checks=V.wiring(),check_setup=V.OFF+' '+V.METER,
        check_note='These tests check the socket ground connections and the supply paths. The unused socket outputs A10 and D10 must remain unconnected. Fix any failure before fitting the parts on the back.')
    for ref in L.DESIGN['rear_order']:component(ref,'Underside parts')
    capfit=len(steps)
    aux=[]
    for i,(ref,pad,colour) in enumerate([('C2.1','F02','red'),('C2.2','F04','black')]):
        pg=L.DESIGN['pigtails'][i];path=[[x,y,-1.2-z] for x,y,z in pg['path']];cut=math.ceil((R.length(path)+8)/5)*5
        w=dict(id=pg['id'],a=pad,b=ref,anchor_a=pad,anchor_b=ref,net=L.PINS[ref]['net'],bare=False,od=1.8,colour=colour,surface='rear',depth=max(p[2] for p in pg['path']),path3d=path,path=[p[:2] for p in path],exit3d=[],segments=[(path,1.8)],anchors=[pad],label=ref,length=dict(formed=round(R.length(path),1),tails=1.2,trim=6.8,cut=cut),earlier_crossings=[],group=[pg['id']],joints=[])
        polarity='positive' if colour=='red' else 'striped negative'
        idx=add('wire','Connect C2 · '+colour+' lead (2200 µF / 25 V)','Form the wire to the template. Insert into '+pad+' from the back, flush with the front, and solder on the back. Slide on heat-shrink, solder the other end to C2’s '+polarity+' leg. Keep the sleeve back for the meter check below, then cover the joint and shrink.',wires=[w['id']],ref='C2',points=[path[-1]],joints=[dict(pad=pad,owner=w['id'])],phase='Large capacitor')
        steps[idx].update(check_setup='Power disconnected · meter on Ω. Test before shrinking the sleeve over the capacitor leg.',checks=V.wire(w),check_note='Red must reach the leg without the negative stripe; black must reach the leg beside the negative stripe. Cover each bare connection separately after the checks pass.')
        w.update(prepare=idx,joints=[idx],check=idx,assembly_actions=[
            f'Cut {cut} mm of {colour} wire.',
            'Remove enough plastic coating from each end to make its solder connection. Gently twist the exposed copper strands together.',
            steps[idx]['text']]);aux.append(w)
    add('check','Strap the battery and C2 in place','Cut 350 mm of ONE-WRAP and thread the floor slots. Fit the battery LED-side down and C2 along its top. Strap across C2’s middle, leaving both ends clear and at least 50 mm overlap. Pull-test: C2 must not slide.',phase='Large capacitor')
    parts.append(dict(ref='C2',name='C2',identity=component_identity('C2'),fit=capfit,solder=[],bounds=M.bounds()['C2'],pins=['F02','F04'],side='external'))
    add('check','Set the buck output before joining the harness','Keep the board, sensors, pump and LEDs disconnected for this test.',phase='Power harness',
        actions=['With the battery unplugged, connect battery positive to S1’s input, S1’s output only to buck IN+, and battery negative only to buck IN−. Leave both buck OUT terminals disconnected. Insulate the temporary connections.',
                 'Set the meter to DC volts (20 V range if it is manual). Black probe on OUT−, red on OUT+. Connect the battery and turn the pack and S1 on.',
                 'Turn the buck’s adjustment screw slowly until the meter reads 5.00 V; it may take several turns. Switch S1 off and on again: the output must stay between 4.9 and 5.1 V.',
                 'Switch off and unplug the battery. Wait until the output reads below 0.1 V. Remove the temporary connections before making the harness joins.'],
        checks=[V.row('Buck output','buck OUT−','buck OUT+','4.9–5.1 V; aim for 5.00 V.','DC V',pads=[])],check_setup='Black meter lead in COM, red in V/Ω. Do not connect the board to an unadjusted buck.')
    for j in L.DESIGN['harness']:
        add('splice','Make '+j['id']+' · '+L.NETS[j['net']][1],'Join '+', '.join(j['members'])+'. Test before sliding the sleeve over the joint; then cover all bare metal and overlap each wire’s insulation.',phase='Power harness',checks=V.splice(j['net']),check_setup='Battery and USB unplugged · meter on Ω.',check_note='Also probe between every member’s exposed copper and this join before covering it: each must read within 2 Ω of touching the tips together. Gently pull each insulated wire; none may slide out.')
    add('check','Check for shorts before power','',phase='Power harness',
        check_setup=V.OFF+' First use DC volts: F02 to F04 and G10 to F04 must each read below 0.1 V. If not, wait; do not short a capacitor to discharge it. Then switch to Ω.',
        checks=V.unpowered(),check_note='Wait 10 seconds for each reading, then reverse the probes and repeat. Capacitors can make the reading start low and rise; a brief beep is not a failed test. A reading above 10 Ω is only a short-circuit screen, not proof the wiring is correct. Keep all three power joins separately insulated.')
    add('check','Check the mounted board','Keep the battery and USB unplugged.',phase='Final checks',
        actions=['Mount with two M3 nuts under each hole and M3×10 screws. No solder joint, clipped lead or bare wire may touch a nut or screw.',
                 'Check from the board face with a ruler: front loops no higher than 35 mm; rear parts and wires no more than 11 mm below the back. Look underneath: nothing may touch the floor.',
                 'Close the lid gently, then reopen it. No wire should be pressed down or trapped at the rim. C2 must stay under its strap when gently pulled.',
                 'Repeat the previous short-circuit checks with the board mounted; metal hardware must not create a new connection.'])
    add('check','Power the board without loads','Pump, LEDs and lock connector stay unplugged. USB stays unplugged.',phase='Final checks',
        actions=['Upload the project firmware first if needed: follow the build guide’s USB-only flashing procedure, with the battery unplugged, jumper cap removed and driver chip out. Unplug USB when finished.',
                 'With all power disconnected, insert the 74AHCT125 chip with its notch toward column X. Check that every leg enters the socket. Fit the jumper cap across JP1’s two pins.',
                 'Set the meter to DC volts. Clip black to ground at F04 while power is off. Connect the battery, turn the pack and S1 on, and take the readings below with the red probe. Touch only one joint at a time.',
                 'If any supply or signal is outside the stated range, or a part becomes hot, switch off immediately. Do not connect loads. Turn S1 off and unplug the battery after testing.'],
        check_setup='Battery power only · black probe at F04 · red probe at each listed point. Firmware must be running with idle brightness set to 0; allow the startup blink to finish.',checks=V.powered(),
        check_note='If the idle setting was changed, use the next step’s USB procedure to send idle 0, then repeat the gate checks. Do not diagnose a disconnected pump or LED by measuring its negative wire: that output can float.')
    add('check','Test the sensors before connecting loads','Use the detailed no-load tests in EL-10 of the build guide (linked below). Pump and LEDs remain disconnected.',phase='Final checks',
        actions=['With all power off, attach the completed lock cable and remove the jumper cap from JP1. Keep the driver chip installed. Check the Hall sensor’s supply polarity before turning on.',
                 'Turn battery power on and verify 4.9–5.1 V from G10 to F04. Then connect USB, open the serial monitor at 115200 baud and send idle 0.',
                 'Run the checks below. Remove the magnet and release the switch before testing either gate. Follow EL-10 for battery calibration.',
                 'Finish by sending stop, unplugging USB first, then switching off and unplugging the battery. Refit the jumper cap only after all power is disconnected.'],
        check_setup='Black probe at F04 · meter on DC volts. Move the magnet away and release the switch before each baseline reading.',
        checks=[V.row('Hall supply','F04','Hall pin 1','4.9–5.1 V.','DC V',pads=['F04']),
                V.row('Hall signal','F04','P09','Magnet away: 3.0–3.4 V. Magnet at sensing face: below 0.8 V.','DC V'),
                V.row('Twist signal','F04','O09','Released: 3.0–3.4 V. Pressed: below 0.8 V.','DC V'),
                V.row('Pump gate command','F04','U01','Send cal 10000: above 0.5 V after 1 s. Send stop: below 0.2 V.','DC V'),
                V.row('LED gate command','F04','H16','Send idle 255: 4.7–5.1 V. Send idle 0: below 0.2 V.','DC V')],
        check_note='Send status after each change: ring=present/absent must follow the magnet; switch=pressed/released must follow the switch. Repeat five times while gently moving the cable. No flickering or missed changes. The pump gate is pulsed, so a DC meter shows an average, not necessarily 5 V. Finish with idle 0 and stop; do not save the temporary idle 255 setting.')
    source=b''.join(p.read_bytes() for p in [HERE/'design.json',HERE/'assembly_guide.py',HERE/'offboard.py',HERE/'verification.py',HERE/'routing.py',O.CAD/'params.py',O.CAD/'parts/top.py'])
    return dict(enclosure=O.installation(),version=hashlib.sha256(source).hexdigest()[:12],diameter=1.8,gap=M.REAR_GAP,routes=[byid[n] for g in report['assembly_groups'] for n in g]+aux,steps=steps,parts=parts,pins=pins,mounts=L.MOUNTS,colours=COLOURS,nets={n:dict(label=v[1],colour=NET_COLOUR[n])for n,v in L.NETS.items()},rear_leads=L.DESIGN['leads'],rear_bodies=L.DESIGN['rear_bodies'],offboard_cap=L.DESIGN['offboard_cap'],pigtails=L.DESIGN['pigtails'],report=report,source='Existing board and printed parts · Existing M3 nuts and M3×10 screws · 27 October 2026')

def main():
    routes=R.plan();data=make_data(routes)
    O.write_notes(data['routes'],HERE/'OFFBOARD_WIRING.md')
    (HERE/'routing.json').write_text(json.dumps(routes,separators=(',',':'))+'\n')
    (HERE/'assembly.html').write_text((HERE/'assembly-template.html').read_text().replace('/*__ASSEMBLY_DATA__*/',json.dumps(data,separators=(',',':')).replace('</','<\\/')))
    print(json.dumps(dict(steps=len(data['steps']),solder_operations=sum(len(s.get('joints',[])) for s in data['steps']),**data['report']),indent=2))
if __name__=='__main__':main()
