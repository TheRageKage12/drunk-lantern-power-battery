"""Rear lead, spacer and soldering-tool checks, recomputed from design geometry.

Depth is measured from the copper face. The front loops are fitted before these
parts, so the iron never needs to reach through an insulated-wire stack.
"""
import itertools, math
import numpy as np
from shapely.geometry import Point, Polygon, box

def sample(points, step=.15):
    p=np.asarray(points,float); d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    t=np.linspace(0,d[-1],max(2,math.ceil(d[-1]/step)+1))
    return np.array([np.interp(t,d,p[:,i]) for i in range(3)]).T

def body_distance(points,b):
    shape=Polygon(b['xy']); p=np.asarray(points)
    xy=np.array([shape.distance(Point(*q[:2])) for q in p])
    z=np.maximum(np.maximum(b['z0']-p[:,2],p[:,2]-b['z1']),0)
    return np.hypot(xy,z)

def check_rear(d, mm, segments_gap):
    leads=d['leads']; bodies=d['rear_bodies']; pins=d['pins']; mounts=d['hardware']['mounts']
    lead_min=100.; tool_min=100.
    for ref,path in leads.items():
        for name,b in bodies.items():
            if name==ref.split('.')[0]:continue
            gap=float(body_distance(path,b).min())-.35
            assert gap>=.5,(ref,name,'rear lead/body',gap)
            lead_min=min(lead_min,gap)
    for (a,p),(b,q) in itertools.combinations(leads.items(),2):
        if pins[a]['pad']==pins[b]['pad']:continue
        gap=segments_gap(p,q)-.7
        assert gap>=.5,(a,b,'rear lead separation',gap)
        lead_min=min(lead_min,gap)
    # Threaded metal nuts, printed posts, and every solder joint are obstacles.
    # The 6.85 mm nut envelope includes hex corners and 0.25 mm placement error.
    padset={p['pad'] for p in pins.values()} | {t['anchor'] for t in d['tails']}
    joints={p:sample([[*mm(p),0],[*mm(p),2.5]]) for p in padset}
    nut_min=100.
    for m in mounts:
        radius=d['hardware']['spacer_od_max']/2
        for pad in padset:
            gap=float(np.linalg.norm(mm(pad)-m))-radius-1
            assert gap>=.5,(pad,m,'joint/metal nut',gap)
            nut_min=min(nut_min,gap)
        obstacles=[dict(xy=list(Point(*m).buffer(radius).exterior.coords),z0=0,z1=d['hardware']['spacer']),
                   dict(xy=list(box(m[0]-4.75,m[1]-4.75,m[0]+4.75,m[1]+4.75).exterior.coords),z0=d['hardware']['spacer'],z1=d['hardware']['rear_gap'])]
        for ob in obstacles:
            for name,b in bodies.items():
                gap=math.hypot(Polygon(b['xy']).distance(Polygon(ob['xy'])),max(b['z0']-ob['z1'],ob['z0']-b['z1'],0))
                assert gap>=1,(name,m,'rear body/mount',gap)
            paths=[(ref,p,.35,.5) for ref,p in leads.items()]+[(t['id'],t['path'],.5,.5) for t in d['tails']]+[(p['id'],p['path'],.9,.7) for p in d['pigtails']]
            for name,path,r,minimum in paths:
                gap=float(body_distance(path,ob).min())-r
                assert gap>=minimum,(name,m,'mount clearance',gap)
    for ref,path in leads.items():
        for t in d['tails']:
            if t['node']==pins[ref]['pad']:continue
            assert segments_gap(path,t['path'])-.85>=.5,(ref,t['id'],'rear lead/tail')
    for pg in d['pigtails']:
        p=np.array(pg['path'])
        for name,b in bodies.items():
            assert body_distance(p,b).min()-.9>=.99,(pg['id'],name,'pigtail/body')
        for ref,path in leads.items():
            assert segments_gap(p,path)-1.25>=.5,(pg['id'],ref,'pigtail/rear lead')
        for t in d['tails']:
            if t['node']==pins[pg['ref']]['pad']:continue
            assert segments_gap(p,t['path'])-1.4>=.5,(pg['id'],t['id'],'pigtail/tail')
        for pad,path in joints.items():
            if pad==pins[pg['ref']]['pad']:continue
            assert segments_gap(p,path)-1.9>=.5,(pg['id'],pad,'pigtail/joint')
    assert segments_gap(*(p['path'] for p in d['pigtails']))-1.8>=.8
    sleeves=[]
    for pg in d['pigtails']:
        x,y,z=pg['path'][-1];sleeves.append([[27,y,z],[37,y,z]])
    assert segments_gap(*sleeves)-3>=1.5
    for i,sleeve in enumerate(sleeves):
        assert segments_gap(sleeve,d['pigtails'][1-i]['path'])-2.4>=.5
    deepest=max([b['z1'] for b in bodies.values()]+[max(p[2] for p in path)+.35 for path in leads.values()]+[max(p[2] for p in pg['path'])+.9 for pg in d['pigtails']])
    assert deepest<=11,('rear assembly depth',deepest)
    assert d['hardware']['rear_gap']-.5-11>=3.3-1e-6
    # Recompute tool access at each assembly stage. Touch the side of the joint;
    # the target lead's first 3 mm is the contact region, not an ignored whole lead.
    # The 2 mm tip widens to 5 mm over 12 mm. Offset axes still intersect the joint.
    order=d['rear_order']
    assert set(order)==set(bodies) and len(order)==len(bodies)
    for ref in leads:
        name=ref.split('.')[0];fitted=set(order[:order.index(name)+1])
        pad=pins[ref]['pad'];points=[];labels=[];radii=[]
        for other,path in leads.items():
            if other.split('.')[0] not in fitted:continue
            points.extend(path);labels.extend([other]*len(path));radii.extend([.35]*len(path))
        for t in d['tails']:
            points.extend(t['path']);labels.extend([t['node']]*len(t['path']));radii.extend([.5]*len(t['path']))
        for other,path in joints.items():
            points.extend(path);labels.extend([other]*len(path));radii.extend([1]*len(path))
        points=np.array(points);labels=np.array(labels);radii=np.array(radii)
        joint=np.array([*mm(pad),.7])
        contact=(labels==ref)&(np.linalg.norm(points-joint,axis=1)<3)
        mask=(labels!=pad)&~contact;best=-100
        for approach in d['tool_access'][ref]:
            _,tilt,az,*offset=approach;dx,dy=offset or [0,0]
            assert math.hypot(dx,dy)<=.75+1e-6,('tip misses joint',ref)
            t=np.linspace(0,18,121);theta=math.radians(tilt);phi=math.radians(az)
            direction=[math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)]
            p=np.array([*(mm(pad)+[dx,dy]),1.8])+t[:,None]*direction
            r=1+np.minimum(t,12)*1.5/12
            gap=float((np.linalg.norm(p[:,None,:]-points[None,mask,:],axis=2)-r[:,None]-radii[None,mask]).min())
            for name,b in bodies.items():
                if name in fitted:gap=min(gap,float((body_distance(p,b)-r).min()))
            best=max(best,gap)
        assert best>=.4,(ref,'iron approach',best)
        tool_min=min(tool_min,best)
    return dict(maximum_rear_extent_mm=round(deepest,3),minimum_nut_to_joint_gap_mm=round(nut_min,3),minimum_rear_lead_gap_mm=round(lead_min,3),minimum_iron_clearance_mm=round(tool_min,3))
