"""Rear lead, spacer and soldering-tool checks, recomputed from design geometry.

Depth is measured from the copper face. The front loops are fitted before these
parts, so the iron never needs to reach through an insulated-wire stack.
"""
import itertools, math
import numpy as np
from shapely.geometry import Point, Polygon

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
    for t in d['tails']:
        p=np.array(t['path'])
        for m in mounts:
            gap=np.linalg.norm(p[:,:2]-m,axis=1).min()-3.25-.5
            assert gap>=.49,(t['id'],'tail/spacer',gap)
    for pg in d['pigtails']:
        p=np.array(pg['path'])
        for name,b in bodies.items():
            assert body_distance(p,b).min()-.9>=.99,(pg['id'],name,'pigtail/body')
        for m in mounts:
            for radius,z0,z1 in [(3.25,0,20),(6.72,20,30)]:
                radial=np.maximum(np.linalg.norm(p[:,:2]-m,axis=1)-radius,0)
                axial=np.maximum(np.maximum(z0-p[:,2],p[:,2]-z1),0)
                assert np.hypot(radial,axial).min()-.9>=.7,(pg['id'],'pigtail/post')
        for ref,path in leads.items():
            assert segments_gap(p,path)-1.25>=.5,(pg['id'],ref,'pigtail/rear lead')
    assert segments_gap(*(p['path'] for p in d['pigtails']))-1.8>=.8
    # Sleeved C2 joints: reserve Ø3 mm along the lead face. Actual lead pitch may
    # differ; the full connection box is also reserved in the enclosure model.
    sleeves=[]
    for pg in d['pigtails']:
        x,y,z=pg['path'][-1]; sleeves.append([[x,-8,z],[x,3.5,z]])
    assert segments_gap(*sleeves)-3>=1.5
    for i,sleeve in enumerate(sleeves):
        assert segments_gap(sleeve,d['pigtails'][1-i]['path'])-2.4>=.5
    # Confirm each indicated iron approach against CURRENT geometry; stored gap
    # numbers are not evidence. A 2 mm tip widens to a 5 mm barrel over 12 mm.
    points=[]; labels=[]; radii=[]
    for ref,path in leads.items():
        points.extend(path);labels.extend([pins[ref]['pad']]*len(path));radii.extend([.35]*len(path))
    for t in d['tails']:
        points.extend(t['path']);labels.extend([t['node']]*len(t['path']));radii.extend([.5]*len(t['path']))
    for pad in {p['pad'] for p in pins.values()}:
        path=sample([[*mm(pad),0],[*mm(pad),2.5]])
        points.extend(path);labels.extend([pad]*len(path));radii.extend([1]*len(path))
    points=np.array(points);labels=np.array(labels);radii=np.array(radii)
    for ref in leads:
        pad=pins[ref]['pad']; mask=labels!=pad; best=-100
        for _,tilt,az in d['tool_access'][ref]:
            t=np.linspace(0,18,121); theta=math.radians(tilt); phi=math.radians(az)
            direction=[math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)]
            p=np.array([*mm(pad),1.8])+t[:,None]*direction
            r=1+np.minimum(t,12)*1.5/12
            gap=float((np.linalg.norm(p[:,None,:]-points[None,mask,:],axis=2)-r[:,None]-radii[None,mask]).min())
            for b in bodies.values():gap=min(gap,float((body_distance(p,b)-r).min()))
            best=max(best,gap)
        assert best>=.4,(ref,'iron approach',best)
        tool_min=min(tool_min,best)
    return dict(minimum_rear_lead_gap_mm=round(lead_min,3),minimum_iron_clearance_mm=round(tool_min,3))
