"""Rear wiring with formed bends, solder envelopes and assembly tolerances.

The selected topology is in layout.py. Geometry is regenerated deterministically;
no ideal vertical-to-horizontal corners or unmodelled shared-pad fan-out are used.
All dimensions are mm, depth positive away from the solder face.
"""
import math
import numpy as np
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
import layout as L
import mechanical as M

OD=M.WIRE_OD
BARE_OD=1.0
BEND_RADIUS=4.0  # chosen forming target, NOT an unpublished manufacturer rating
BARE_BEND_RADIUS=1.0
WIRE_MOVEMENT=.4
FLOOR_TOLERANCE=.5
BOW_ALLOWANCE=.5
CLEAR=.2
JOINT_CLEAR=.4
LAYERS=(6.0,9.0,12.0)
REAR_GAP=M.REAR_GAP


def clean(points):
    result=[]
    for p in points:
        p=[float(v) for v in p]
        if not result or math.dist(p,result[-1])>1e-8:result.append(p)
    return result


def arch(a,b,height,offset_a=(0,0),offset_b=(0,0)):
    a=np.array(L.mm(a));b=np.array(L.mm(b));oa=np.array(offset_a);ob=np.array(offset_b)
    va=a+oa;vb=b+ob;length=np.linalg.norm(vb-va);direction=(vb-va)/length
    assert length>=2*BEND_RADIUS
    r=BEND_RADIUS;t=np.linspace(0,math.pi/2,65)
    def leg(pad,offset,u):
        top=height-r
        assert not np.any(offset) or top-.55>=4
        z=np.linspace(.55,top,65);f=np.clip((z-.55)/4,0,1);f=3*f*f-2*f*f*f
        rise=np.c_[pad+f[:,None]*offset,z]
        turn=np.c_[pad+offset+(r-r*np.cos(t))[:,None]*u,top+r*np.sin(t)]
        return np.vstack([rise,turn])
    start=leg(a,oa,direction);end=leg(b,ob,-direction)[::-1]
    centre=np.c_[va+np.linspace(r,length-r,max(2,math.ceil(length*5)))[:,None]*direction,
                 np.full(max(2,math.ceil(length*5)),height)]
    return clean(np.vstack([start,centre,end]))


def flat(pads):
    """Round bare-conductor corners inside their soldered anchor region."""
    points=[np.array(L.mm(p)) for p in pads]; result=[[*points[0],.55]]
    for a,b,c in zip(points,points[1:],points[2:]):
        u=(b-a)/np.linalg.norm(b-a);v=(c-b)/np.linalg.norm(c-b)
        if np.dot(u,v)>.99:continue
        r=BARE_BEND_RADIUS;centre=b-u*r+v*r
        for t in np.linspace(0,math.pi/2,17):
            pt=centre-v*r*math.cos(t)+u*r*math.sin(t)
            result.append([*pt,.55])
    result.append([*points[-1],.55])
    return clean(result)


def cable(pad,index):
    """Fan out below the board; turn upward beyond its edge, away from the floor."""
    x,y=L.mm(pad);end_x=x
    # First 2 mm are stripped, then PVC stays on. The small straight fan-out
    # joins the outward tangent before the 4 mm bend at the board edge.
    # Cubic horizontal fan-out has zero lateral slope at both ends.
    pts=[[x,y-(1-math.cos(t)),math.sin(t)] for t in np.linspace(0,math.pi/2,33)]
    pts.extend([[x,yy,1.0] for yy in np.linspace(y-1,-2,50)])
    for t in np.linspace(0,math.pi/2,65):
        pts.append([end_x,-2-4*math.sin(t),1-4*(1-math.cos(t))])
    pts.extend([[end_x,-6,z] for z in np.linspace(-3,-7,21)])
    return clean(pts)


def plan():
    routes=[]
    for w in L.WIRES:
        r=dict(w);r['od']=BARE_OD if w['bare'] else OD
        r['depth']=.55 if w['bare'] else w['depth']
        r['path3d']=flat(w['pads']) if w['bare'] else arch(w['a'],w['b'],w['depth'],w.get('offset_a',(0,0)),w.get('offset_b',(0,0)))
        r['path']=[[p[0],p[1]] for p in r['path3d']]
        routes.append(r)
    order=sorted(L.HARNESS,key=lambda h:L.mm(h[1])[0])
    for i,(ref,pad,net,label) in enumerate(order):
        pts=cable(pad,i)
        routes.append(dict(id=ref,a=pad,b=None,bare=False,net=net,depth=1.0,od=OD,
                           anchors=[pad],path3d=pts,path=[p[:2] for p in pts],exit=pts[-1][:2]))
    return sorted(routes,key=lambda r:r['id'])


def length(points):return sum(math.dist(a,b) for a,b in zip(points,points[1:]))


def segments(points):
    p=np.asarray(points);a=p[:-1];b=p[1:];keep=np.linalg.norm(b-a,axis=1)>1e-8
    return a[keep],b[keep]


def segment_distance(points,other):
    """Exact minimum between the polyline segments, not just sampled vertices."""
    a,aa=segments(points);b,bb=segments(other)
    if not len(a) or not len(b):return math.inf
    u=(aa-a)[:,None,:];v=(bb-b)[None,:,:];w=a[:,None,:]-b[None,:,:]
    A=np.sum(u*u,axis=2);B=np.sum(u*v,axis=2);C=np.sum(v*v,axis=2)
    D=np.sum(u*w,axis=2);E=np.sum(v*w,axis=2);den=A*C-B*B
    s=np.divide(B*E-C*D,den,out=np.zeros_like(den),where=abs(den)>1e-14)
    t=np.divide(A*E-B*D,den,out=np.zeros_like(den),where=abs(den)>1e-14)
    interior=(abs(den)>1e-14)&(s>=0)&(s<=1)&(t>=0)&(t<=1)
    dist=np.where(interior,np.sum((w+s[:,:,None]*u-t[:,:,None]*v)**2,axis=2),np.inf)
    # Four constrained boundary cases also cover parallel segments.
    for ss in (0,1):
        tt=np.clip((E+ss*B)/C,0,1)
        dist=np.minimum(dist,np.sum((w+ss*u-tt[:,:,None]*v)**2,axis=2))
    for tt in (0,1):
        ss=np.clip((tt*B-D)/A,0,1)
        dist=np.minimum(dist,np.sum((w+ss[:,:,None]*u-tt*v)**2,axis=2))
    return float(np.sqrt(dist.min()))


def outside_joints(points,pads):
    # Densify before trimming so the exemption never extends beyond the actual
    # 2 mm diameter, 2.5 mm tall solder envelope. Return separate line fragments.
    dense=[]
    for a,b in zip(points,points[1:]):
        dense.extend(np.linspace(a,b,max(2,math.ceil(math.dist(a,b)/.05)),endpoint=False))
    dense.append(points[-1]);groups=[];group=[]
    for p in dense:
        inside=any(math.dist(p[:2],L.mm(q))<=M.JOINT_RADIUS and p[2]<=M.JOINT_HEIGHT for q in pads)
        if inside:
            if len(group)>1:groups.append(group)
            group=[]
        else:group.append(p)
    if len(group)>1:groups.append(group)
    return groups


def pieces(route):
    """Split at insulation boundaries; 2 mm stripped ends are real geometry."""
    if route['bare']:return [(route['path3d'],BARE_OD)]
    pts=route['path3d'];total=length(pts)
    cuts=[2.0]+([total-2.0] if route['b'] else [])
    result=[];section=[pts[0]];travel=0;which=0
    for a,b in zip(pts,pts[1:]):
        span=math.dist(a,b)
        while which<len(cuts) and travel<cuts[which]<=travel+span:
            t=(cuts[which]-travel)/span
            point=[x+(y-x)*t for x,y in zip(a,b)];section.append(point)
            result.append((clean(section),BARE_OD if which==0 else OD))
            section=[point];which+=1
        section.append(b);travel+=span
    result.append((clean(section),BARE_OD if route['b'] else OD))
    return result

def minimum_radius(points):
    p=np.asarray(clean(points));a=p[1:-1]-p[:-2];b=p[2:]-p[1:-1]
    cross=np.linalg.norm(np.cross(a,b),axis=1)
    length_product=np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1)*np.linalg.norm(a+b,axis=1)
    radii=np.divide(length_product,2*cross,out=np.full_like(cross,np.inf),where=cross>1e-10)
    return float(radii.min()) if len(radii) else math.inf

def validate(routes,wire_od=None,clearance=CLEAR,joint_clearance=JOINT_CLEAR):
    expected={r['id']:r for r in plan()}
    assert len(routes)==len(expected) and len({r['id'] for r in routes})==len(expected)
    assert wire_od in (None,OD)
    occupied={p['pad']:p['net'] for p in L.PINS.values()}
    anchors={p for r in routes for p in r['anchors']}|{p['pad'] for k,p in L.PINS.items() if not k.startswith('BUS.')}
    mounts=unary_union([box(x-4.5,y-4.5,x+4.5,y+4.5) for x,y in L.MOUNTS])
    wire_min=math.inf;bare_min=math.inf;mount_min=math.inf
    for i,r in enumerate(routes):
        e=expected[r['id']]
        assert (r['a'],r['b'],r['bare'],r['net'])==(e['a'],e['b'],e['bare'],e['net']),r['id']
        assert r['depth']==e['depth'] and r['od']==e['od'],(r['id'],'height or diameter')
        assert r['path3d']==e['path3d'] and r['path']==e['path'],(r['id'],'unreviewed path')
        assert r['anchors']==e['anchors']
        for points,diameter in pieces(r):
            if diameter==OD:assert minimum_radius(points[1:-1])>=4-.01,(r['id'],'tight insulated bend')
        pts=np.array(r['path3d']);radius=r['od']/2
        if not r['bare'] and r['b']:
            fixed={p['pad'] for k,p in L.PINS.items() if not k.startswith('BUS.')}
            assert not (set(r['anchors']) & fixed),(r['id'],'insulated jumper requires its own holes')
        assert max(pts[:,2])+radius+BOW_ALLOWANCE<=M.REAR_GAP-FLOOR_TOLERANCE-2.0,(r['id'],'floor margin')
        if r['b']:
            tube=LineString(r['path']).buffer(radius)
            assert box(0,0,70,50).covers(tube),(r['id'],'board edge')
            gap=tube.distance(mounts);mount_min=min(mount_min,gap)
            assert gap>=.49,(r['id'],'mount keepout',gap)
        for mx,my in L.MOUNTS:
            # Printed 9 mm square posts end 6 mm below the board; above them
            # the removable spacer is only 6 mm in diameter.
            xy=np.maximum(np.abs(pts[:,:2]-[mx,my])-4.75,0)
            dz=np.maximum(np.maximum(M.BOARD_SPACER-pts[:,2],pts[:,2]-M.REAR_GAP),0)
            post=np.sqrt(np.sum(xy*xy,axis=1)+dz*dz)-radius-WIRE_MOVEMENT
            radial=np.maximum(0,np.linalg.norm(pts[:,:2]-[mx,my],axis=1)-3.25)
            vertical=np.maximum(np.maximum(-pts[:,2],pts[:,2]-M.BOARD_SPACER),0)
            spacer=np.hypot(radial,vertical)-radius-WIRE_MOVEMENT
            assert post.min()>=.19,(r['id'],'printed post tolerance',float(post.min()))
            assert spacer.min()>=.19,(r['id'],'spacer tolerance',float(spacer.min()))
        # Every unrelated solder joint is a cylinder, not a 2-D obstacle whose
        # height gets lost. Same-net joins may meet ONLY at declared anchors.
        for pad in anchors-set(r['anchors']):
            if occupied[pad]==r['net'] and r['bare'] and pad in r.get('pads',[]):continue
            for points,diameter in pieces(r):
                p=np.asarray(points)
                dxy=np.linalg.norm(p[:,:2]-L.mm(pad),axis=1)
                d=np.hypot(np.maximum(0,dxy-M.JOINT_RADIUS),np.maximum(0,p[:,2]-M.JOINT_HEIGHT))
                assert d.min()>=diameter/2+joint_clearance-.015,(r['id'],'joint',pad,float(d.min()-diameter/2))
        for q in routes[:i]:
            shared=set(r['anchors'])&set(q['anchors'])
            for rpoints,rd in pieces(r):
                for qpoints,qd in pieces(q):
                    rp=outside_joints(rpoints,shared) if shared else [rpoints]
                    qp=outside_joints(qpoints,shared) if shared else [qpoints]
                    dist=min((segment_distance(a,b) for a in rp for b in qp),default=math.inf)
                    gap=dist-(rd+qd)/2
                    target=1.0 if rd==OD and qd==OD else .7 if rd!=qd else .4
                    if r['id'].startswith('H') and q['id'].startswith('H'):target=.7
                    if shared:target=.1
                    assert gap>=target-.015,(r['id'],q['id'],'wire clearance',round(gap,3),target)
                    if rd==OD and qd==OD and not shared and not(r['id'].startswith('H') and q['id'].startswith('H')):wire_min=min(wire_min,gap)
                    elif not shared:bare_min=min(bare_min,gap)
    return dict(routes=len(routes),maximum_rear_extent_mm=max(r['depth']+r['od']/2 for r in routes),
                wire_bow_allowance_mm=BOW_ALLOWANCE,floor_tolerance_mm=FLOOR_TOLERANCE,
                remaining_floor_clearance_mm=round(M.REAR_GAP-max(r['depth']+r['od']/2 for r in routes)-BOW_ALLOWANCE-FLOOR_TOLERANCE,2),
                minimum_insulated_gap_mm=round(wire_min,3),minimum_bare_gap_mm=round(bare_min,3),
                minimum_mount_gap_mm=round(mount_min,3),minimum_insulated_bend_radius_mm=BEND_RADIUS,
                solder_height_mm=M.JOINT_HEIGHT)


if __name__=='__main__':
    import json
    print(json.dumps(validate(plan()),indent=2))
