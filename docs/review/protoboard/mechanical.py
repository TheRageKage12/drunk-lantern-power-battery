"""Measured-pitch placement and explicit body/assembly limits, in millimetres.

Front face is z=0; rear depth d corresponds to z=-1.2-d. No printed dimensions change.
"""
import math
import layout as L
BOARD_THICKNESS=1.2
PRINTED_POST_HEIGHT=10.
BOARD_SPACER=L.DESIGN["hardware"]["spacer"]
REAR_GAP=PRINTED_POST_HEIGHT+BOARD_SPACER
WIRE_OD=1.8
JOINT_HEIGHT=2.5
JOINT_RADIUS=1.
MOUNT_TOOL_RADIUS=3.
MIN_BODY_GAP=1.

def bounds(cap_length=25,cap_diameter=18,mosfet_height=22):
    b={n:tuple(v) for n,v in L.DESIGN['bodies'].items()}
    for n,s in L.DESIGN['rear_bodies'].items():
        x=min(p[0] for p in s['xy']);y=min(p[1] for p in s['xy']);w=max(p[0] for p in s['xy'])-x;h=max(p[1] for p in s['xy'])-y
        b[n]=(x,y,w,h,-1.2-s['z1'],-1.2-s['z0'])
    for n in ['Q1','Q2']:b[n]=(*b[n][:5],mosfet_height)
    x,y,w,h,z0,z1=L.DESIGN['offboard_cap']['bounds'];b['C2']=(x,y,cap_length,cap_diameter+2,z0,z0+cap_diameter+2)
    return b

def rect_gap(a,b):
    dx=max(a[0]-b[0]-b[2],b[0]-a[0]-a[2],0);dy=max(a[1]-b[1]-b[3],b[1]-a[1]-a[3],0)
    return math.hypot(dx,dy)

def gap3(a,b):return math.hypot(rect_gap(a,b),max(a[4]-b[5],b[4]-a[5],0))

def validate(bodies=None):
    bodies=bounds() if bodies is None else bodies;pairs=[]
    for i,(n,a) in enumerate(bodies.items()):
        for m,b in list(bodies.items())[i+1:]:
            if {n,m}=={'MCU','USB_ACCESS'}:continue
            g=gap3(a,b);assert g>=1-1e-6,(n,m,'body gap',g);pairs.append((g,n,m))
        for x,y in L.MOUNTS:
            if a[5]>=0:
                g=rect_gap(a,(x,y,0,0))-MOUNT_TOOL_RADIUS
                assert g>=1-1e-6,(n,'screw access',g)
            else:
                radius=L.DESIGN['hardware']['spacer_od_max']/2
                radial=max(0,rect_gap(a,(x,y,0,0))-radius)
                vertical=max(a[4]+1.2,-1.2-BOARD_SPACER-a[5],0)
                assert math.hypot(radial,vertical)>=1-1e-6,(n,'metal nut stack')
                assert gap3(a,(x-4.75,y-4.75,9.5,9.5,-1.2-REAR_GAP,-1.2-BOARD_SPACER))>=1-1e-6,(n,'printed post')
    return sorted(pairs)
