"""Outgoing-wire cut plan, anchored to the unchanged cap and lantern CAD.

Lengths are conservative cutting blanks, not claims of measured hardware lead lengths.
The fixed board route is retained. Free wires follow the cap's wall-side cable lane;
pump/LED service loops live beside the cap-floor opening, never under the board.
"""
from pathlib import Path
import math, sys
import routing as R
import mechanical as M

CAD = Path(__file__).resolve().parents[3] / 'cad'
sys.path.insert(0, str(CAD))
import params as P
from parts import top as T, sphere as S, base as B

FLOOR = T.Z_CAP_FLOOR
FACE = FLOOR + T.BOARD_STANDOFF + M.BOARD_SPACER + P.PERFBOARD_T
# New wiring locations within the existing free lane; these are not printed features.
JOINS = {'J_LOAD': [-73., 20., 6.], 'J_GND': [-73., 0., 6.], 'J_5V': [-73., -20., 6.]}
PORT = [*P.CAP_WIRE_HOLE_XY, 6.]
LOCK_PLUG = [PORT[0], PORT[1]+12., 6.]
PUMP_JOIN = [PORT[0]-3., PORT[1]+2., 6.]
LED_JOIN = [PORT[0]+3., PORT[1]+2., 6.]
# 150 mm lets the floor rise from its ledge to the cap rim (74 mm), with lateral movement.
SERVICE_COIL = [-44., -54., 14., 28., 28., 18.]  # centre X/Y, bottom Z, reserved W/D/H
SERVICE = 150
TRIM = 20  # bend/position variation and final trimming, in addition to local board stock
END_STRIP = 8  # reserved at far end; trim to the actual connector pigtail/splice

SPECS = {
 'H01': ('Battery-positive lead', 'J_LOAD', 'battery +', 'red', 'Switched battery-positive join',
         'Joins the switched battery lead, buck IN+, pump + and LED +.'),
 'H02': ('Controller ground lead', 'J_GND', 'logic ground', 'black', 'Common ground join',
         'Joins battery −, buck IN− and the other ground wires.'),
 'H03': ('Pump ground lead', 'J_GND', 'pump ground', 'black', 'Common ground join',
         'Ground connection for the pump-switching transistor; this does not go directly to the pump.'),
 'H04': ('LED ground lead', 'J_GND', 'LED ground', 'black', 'Common ground join',
         'Ground connection for the LED-switching transistor; this does not go directly to the LEDs.'),
 'H05': ('Pump negative lead', 'PUMP_JOIN', 'pump −', 'blue', 'Pump-lead join at the cap opening',
         'Continues down to the existing 2-pin pump plug, then to pump − and D2’s unstriped end.'),
 'H06': ('LED negative lead', 'LED_JOIN', 'LED −', 'yellow', 'LED-lead join at the cap opening',
         'Continues to the shared negative wire for all LED strips.'),
 'H07': ('5 V supply lead', 'J_5V', '5 V', 'white', '5 V join',
         'Joins buck OUT+ and the lock cable’s 5 V wire.'),
 'H08': ('Twist-switch signal lead', 'LOCK_PLUG', 'twist signal', 'yellow', '4-pin lock connector · switch signal',
         'The matching connector wire continues to the microswitch’s NO terminal; COM goes to ground.'),
 'H09': ('Hall-sensor signal lead', 'LOCK_PLUG', 'Hall signal', 'green', '4-pin lock connector · Hall signal',
         'The matching connector wire continues to Hall sensor OUT (pin 3).'),
}


def board_to_cap(point):
 x,y=T.board_point(*point[:2]);return [x,y,FACE-FLOOR+point[2]]


def plan(w, local_cut):
 title,target,tag,colour,destination,connection=SPECS[w['id']]
 exit=board_to_cap(R.cable_exit(w)[-1])
 dest=JOINS.get(target,{'LOCK_PLUG':LOCK_PLUG,'PUMP_JOIN':PUMP_JOIN,'LED_JOIN':LED_JOIN}.get(target))
 # Move inward from the wall before running along it, clear of the floor thumbscrew at (-85,0).
 # Square-corner waypoint length is deliberately conservative for free, rounded bends.
 if target in JOINS:
  path=[exit,[-73.,exit[1],exit[2]],[-73.,exit[1],6.],dest]
  route='Down beside the board, then along the gap between the board and cap wall.'
 else:
  path=[exit,[-73.,exit[1],exit[2]],[-73.,exit[1],6.],[-73.,-43.,6.],[-62.,-43.,6.],dest]
  route='Down beside the board, around the end nearest the buck, then to the cap-floor wire opening.'
 path=[p for i,p in enumerate(path) if not i or math.dist(p,path[i-1])>.01]
 travel=R.length(path)
 slack=SERVICE if w['id'] in ('H05','H06') else 20
 total=math.ceil((local_cut+travel+slack+END_STRIP+TRIM)/10)*10
 return dict(title=title,target=target,tag=tag,destination=destination,connection=connection,
             colour=colour,path=path,route=route,local_mm=local_cut,external_mm=round(travel,1),
             slack_mm=slack,end_mm=END_STRIP,trim_mm=TRIM,cut_mm=total,
             slack_note=('Keep the extra 150 mm in a loose loop beside the cap-floor opening so the plate can lift out.'
                         if slack==SERVICE else 'Leave a small loose bend beside the board; trim at the final join.'),
             later=('Connect the far end when assembling the power joins.' if target in JOINS else
                    'Connect the far end when fitting the cap-floor wiring; keep the existing plug.'))


def installation():
 """CAD landmarks for the destination map and downstream cut list."""
 # These lower runs connect to the cap leads: do NOT add them to the nine board cuts.
 start=[*P.CAP_WIRE_HOLE_XY,FLOOR-3]
 neck=[-30.,-36.,P.Z_SPHERE_TOP+10]
 wall=[-30.,-36.,P.Z_SPHERE_CENTER+T.WEXT_Z0-5]
 # LED join behind the wall's upper edge, between wall and LED panel.
 led=[0.,-36.,P.Z_SPHERE_CENTER+S.WALL_Z0+S.BACK_ROWS[-1]]
 # Lock connector's mating half is above the cap-floor hole. The run enters the Hall window.
 hall=[0.,S.WALL_BACK_Y-4.,P.Z_SPHERE_CENTER+P.SOCKET_Z_LOCAL]
 switch=[0.,S.WALL_BACK_Y-4.,P.Z_SPHERE_CENTER+P.SOCKET_Z_LOCAL-S.SWITCH_WIRE_NOTCH_R]
 bay=[*S.WIRE_SLOT_XY,P.Z_SPHERE_CENTER+S.BAY_FLOOR_Z]
 plug=[16.,-75.,52.]  # centre of the existing pump_plug_envelope in electronics.py
 motor=[B.PUMP_X,B.PUMP_HEAD_FACE_Y-P.PUMP_L-3.,B.PUMP_AXIS_Z]
 pump=[start,neck,[-30.,-36.,wall[2]+12],[30.,-38.,wall[2]+12],
       [30.,-38.,bay[2]+16],[*bay[:2],bay[2]+12],bay,[35.,-32.,105.],[35.,-65.,80.],plug]
 led_path=[start,neck,wall,led]
 hall_path=[[*LOCK_PLUG[:2],FLOOR+LOCK_PLUG[2]],[*PORT[:2],FLOOR+6],start,neck,wall,hall]
 switch_path=[[*LOCK_PLUG[:2],FLOOR+LOCK_PLUG[2]],[*PORT[:2],FLOOR+6],start,neck,wall,switch]
 def stock(name,path,slack,colours,destination):
  travel=R.length(path);cut=math.ceil((travel+slack+2*END_STRIP+TRIM)/25)*25
  return dict(name=name,path=path,travel_mm=round(travel,1),slack_mm=slack,cut_mm=cut,colours=colours,destination=destination)
 lower=[stock('Pump trunk',pump,75,['red','blue'],'Existing 2-pin pump plug at the cartridge'),
        stock('LED trunk',led_path,30,['red','yellow'],'LED common + and − behind the lock wall'),
        stock('Lock cable',switch_path,60,['white','black','yellow','green'],'Existing 4-pin plug to the Hall sensor and microswitch')]
 # Both lock signals share the longest route; shorter branches are trimmed at assembly.
 cap_jumpers=[]
 for name,source,dest,colour,slack in [
     ('Pump positive cap lead','J_LOAD',PUMP_JOIN,'red',SERVICE),
     ('LED positive cap lead','J_LOAD',LED_JOIN,'red',SERVICE),
     ('Lock 5 V cap lead','J_5V',LOCK_PLUG,'white',20),
     ('Lock ground cap lead','J_GND',LOCK_PLUG,'black',20)]:
  path=[JOINS[source],[-73.,-43.,6.],dest]
  cap_jumpers.append(stock(name,path,slack,[colour],source+' to '+('4-pin lock plug' if dest==LOCK_PLUG else 'matching lead at cap opening')))
 return dict(floor_z=round(FLOOR,2),cap_top_z=round(P.Z_CAP_TOP,2),board_face_z=round(FACE,2),
             board=[list(T.board_point(x,y)) for x,y in [(0,0),(70,0),(70,50),(0,50)]],
             battery=[P.PACK_CAP_XY[0]-P.POWERBANK_W/2,P.PACK_CAP_XY[1]-P.POWERBANK_L/2,P.POWERBANK_W,P.POWERBANK_L],
             buck=[P.BUCK_CAP_XY[0]-P.BUCK_L/2,P.BUCK_CAP_XY[1]-P.BUCK_W/2,P.BUCK_L,P.BUCK_W],
             joins=JOINS,port=PORT,lock_plug=LOCK_PLUG,pump_join=PUMP_JOIN,led_join=LED_JOIN,
             cap_jumpers=cap_jumpers,lower_runs=lower,hall_path=hall_path,switch_path=switch_path,motor=motor,pump_plug=plug,
             radius=P.D_MAX/2,service_mm=SERVICE,service_coil=SERVICE_COIL)


def validate(plans):
 assert set(plans)==set(SPECS), 'Each outgoing wire needs one cut and destination'
 for name,p in plans.items():
  needed=p['local_mm']+R.length(p['path'])+p['slack_mm']+p['end_mm']+p['trim_mm']
  assert p['cut_mm']>=needed-0.01, (name,'cut too short',p['cut_mm'],needed)
  assert p['cut_mm']%10==0
  assert p['slack_mm']==(SERVICE if name in ('H05','H06') else 20)
  assert p['trim_mm']>=20 and p['end_mm']>=8
  assert p['target'] in set(JOINS)|{'PUMP_JOIN','LED_JOIN','LOCK_PLUG'}
  for point in p['path']:
   assert math.hypot(*point[:2])+1.4 < T.R_CAP_IN, (name,'outside cap')
   assert 1.4 < point[2] < 16, (name,'outside cable lane')
 assert SERVICE >= 2*(P.Z_CAP_TOP-FLOOR), 'Not enough cap-floor lift allowance'
 return True


def write_notes(routes, path):
 plans={w['id']:w['outbound'] for w in routes if w.get('outbound')};validate(plans)
 e=installation()
 lines=['# Outgoing wires and enclosure cut plan','',
 'The nine **H wire IDs are wire labels, not hole names**. Each board step attaches one end only. Keep the free end insulated and label it; connect it during cap-floor assembly. Use the existing insulated stranded 22 AWG. No printed parts change.','',
 '## Board leads — cut these during the guide','',
 '| Wire label | Colour | Cut | Connect the free end later |','|---|---|---:|---|']
 for name,p in sorted(plans.items()):lines.append(f"| {name} · {p['title']} | {p['colour']} | **{p['cut_mm']} mm** | {p['destination']} |")
 lines+=['','The pump and LED leads stop at sleeved joins beside the cap-floor opening; they do **not** reach the pump or LED strips by themselves. The signal leads stop at the cap-side **existing 4-pin lock connector**. Keep the existing 2-pin pump connector at the cartridge. Use continuity to match connector wires; do not rely on their insulation colours.','',
 '## Separate wires for later enclosure assembly','',
 'These are additional pieces, not extra length to add to the board cuts above. Cut the stated length for **each** colour. At prewired plugs, retain the connector pigtails and trim the new wire to meet them, keeping the slack specified below.','',
 '| Piece | Colours | Cut each | Route / destination |','|---|---|---:|---|']
 for r in e['cap_jumpers']+e['lower_runs']:lines.append(f"| {r['name']} | {', '.join(r['colours'])} | **{r['cut_mm']} mm** | {r['destination']} |")
 lines+=['','1. Keep J_LOAD (switched battery +), J_GND (ground), and J_5V (regulated 5 V) as three separate insulated joins in the wall-side lane beside the board. The map places them along that lane: J_LOAD toward S1, J_5V toward the buck, ground between them.',
 '2. At the cap opening, join the blue board lead to the blue pump trunk and the red pump cap lead to its red trunk. Join yellow to yellow and red to red for the LED pair. Sleeve each splice separately. Retain 150 mm of slack in **each cap-side pump and LED lead**, loosely coiled beside the opening; do not fold it beneath the board.',
 '3. The lock connector remains beside the opening. Its cap side receives Hall signal (green board lead), twist signal (yellow board lead), 5 V (white), and ground (black). Pass the separate four-wire lock cable down through the opening and behind the wall extension. At the lock, white goes to Hall pin 1, black to pin 2 and switch COM, green to Hall pin 3, yellow to switch NO. Leave switch NC unused.',
 '4. The pump pair runs down behind the wall, through the existing 7 mm bay-floor cable hole at (35, −32), then through the foot to the pump plug. Twist red/blue loosely together. Keep the lower 75 mm allowance near the plug so it can be reached and unplugged before lifting the lantern off the cartridge. D2 remains across the pump terminals.',
 '5. The LED pair stops at the common LED wiring behind the upper lock wall. All LED negatives join yellow; all positives join red. The individual LED-strip branch wiring is unchanged.',
 '6. Keep the lock wiring separate from the pump pair below the cap opening. Leave 60 mm slack in the lock cable and 30 mm at the LED join. Route everything on the display side of the wall, clear of the glass, nozzle and moving lock parts.','',
 '## Basis of the cut lengths','',
 'CAD references: `cad/params.py`, `cad/parts/top.py` (`board_point`, cap floor and wire opening), `cad/parts/sphere.py` (wall and bay-floor cable hole), and the pump plug envelope in `cad/parts/electronics.py`. Route definitions and arithmetic live in `offboard.py`.',
 f'The cap floor is at Z={e["floor_z"]} mm and the rim at Z={e["cap_top_z"]} mm. Two M3 nuts per post put the board component face at Z={e["board_face_z"]} mm. The existing 150 mm service allowance exceeds twice the {e["cap_top_z"]-e["floor_z"]:.1f} mm floor-to-rim rise.',
 'Board cuts = existing formed board portion and its solder/trim stock + planned cap-lane travel + slack + 8 mm for the far-end connection + 20 mm fitting/trim allowance, rounded **up** to 10 mm. Lower-run cuts use CAD waypoints, the stated slack, two 8 mm ends and 20 mm trim stock, rounded up to 25 mm. Square-corner distances conservatively allow room to form smooth bends. Do not make sharp creases at the drawn corners.',
 'The clearance check reserves 28 × 28 × 18 mm for the pump/LED slack loops beside the opening, above the lock connector, outside the board footprint.',
 'The 20 mm trim stock is removed at final fitting; it is not another loop to store. These are cutting blanks based on the planned layout, not measurements of the delivered connector pigtails. Position the printed parts and connectors as shown, then trim only the excess while retaining the designated service slack.','',
 '| Board lead | Board portion + stock | Cap-lane travel | Slack | End + trim | Cut |','|---|---:|---:|---:|---:|---:|']
 for name,p in sorted(plans.items()):lines.append(f"| {name} | {p['local_mm']} | {p['external_mm']} | {p['slack_mm']} | {p['end_mm']+p['trim_mm']} | {p['cut_mm']} mm |")
 lines+=['','H06 turns inward above the cap-floor thumbscrew head before descending. Its former straight drop was too close to that head. This changes only the free wire bend, not the PCB holes or printed parts.','']
 path.write_text('\n'.join(lines))
