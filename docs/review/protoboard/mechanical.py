"""Shared component bounding boxes for the drawing and CAD. Units: mm.

Published package maxima and explicit purchasing/assembly limits are distinguished
in README.md. Bounds are body allowances, not the much smaller lead corridors.
Coordinates: left, top, width, height in the component-side drawing; outward depth.
"""
import math
import layout as L
MIN_BODY_GAP = 1.0
BOARD_THICKNESS = 1.2
REAR_GAP = 10.0
WIRE_OD = 1.6  # 1.44 mm listed finished OD, plus a modelling allowance
JOINT_HEIGHT = 1.5
JOINT_RADIUS = 0.95
MOUNT_TOOL_RADIUS = 3.0  # straight 2.5 mm hex key, screw head <=6 mm diameter

def bounds(cap_length=25, cap_diameter=18, mosfet_height=22):
    result = {}
    def body(ref,cx,cy,w,h,depth):
        result[ref]=(cx-w/2,cy-h/2,w,h,0,depth)
    body('MCU',*[(a+b)/2 for a,b in zip(L.mm(L.PINS['MCU.5V']['pad']),L.mm(L.PINS['MCU.D6']['pad']))],21.5,18.3,12)
    # USB projection belongs to MCU; it is not a separate colliding component.
    result['USB']=(.5,27,4,8.8,0,12)
    ul=L.mm(L.PINS['U1.1']['pad']);lr=L.mm(L.PINS['U1.8']['pad'])
    body('U1',(ul[0]+lr[0])/2,(ul[1]+lr[1])/2,11,20.5,10.5)
    result['C2']=(25,-2,cap_length,cap_diameter,0,cap_diameter+1) # 1 mm allowance for tape/retention under the case
    for ref in ('Q1','Q2'):
        x,y=L.mm(L.PINS[ref+'.D']['pad'])
        body(ref,x,y,10.8,4.9,mosfet_height)  # TO-220 max10.54 x4.69; trimmed leads +15.24 body
    for p in L.PARTS:
        ref=p['ref']
        if ref=='C2':continue
        a,b=L.mm(p['a']),L.mm(p['b']); cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2
        if p['kind']=='ceramic':w,h,d=10,4,13
        elif p['kind']=='jumper':w,h,d=5.5,2.5,8
        else:
            length,width,d=(6.8,2.7,3.2) if p['kind']=='resistor' else (5.5,2.9,3.4)
            w,h=(width,length) if a[0]==b[0] else (length,width)
            assert math.dist(a,b)>=length+2, (ref,'allow >=1 mm straight lead before each bend')
        body(ref,cx,cy,w,h,d)
    return result

def rect_gap(a,b):
    dx=max(a[0]-b[0]-b[2],b[0]-a[0]-a[2],0)
    dy=max(a[1]-b[1]-b[3],b[1]-a[1]-a[3],0)
    return math.hypot(dx,dy)

def validate(bodies=None):
    bodies=bounds() if bodies is None else bodies
    pairs=[]
    for i,(n,a) in enumerate(bodies.items()):
        for m,b in list(bodies.items())[i+1:]:
            if {n,m}=={'MCU','USB'}:continue
            gap=rect_gap(a,b)
            assert gap>=MIN_BODY_GAP-1e-6, (n,m,'body gap',round(gap,3))
            pairs.append((gap,n,m))
        for x,y in L.MOUNTS:
            gap=rect_gap(a,(x,y,0,0))-MOUNT_TOOL_RADIUS
            assert gap>=1-1e-6,(n,'screw / driver access',x,y,round(gap,3))
    return sorted(pairs)

if __name__=='__main__':
    print(validate()[:8])
