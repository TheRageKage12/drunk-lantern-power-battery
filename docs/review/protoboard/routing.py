"""Insulated front-side routes; each end gets a dedicated hole and a short rear tail."""
import copy, math
import numpy as np
import layout as L
import mechanical as M
from redesign.check import check

def length(p):return sum(math.dist(a,b) for a,b in zip(p,p[1:]))

def plan():
    routes=[]
    for e in L.DESIGN['edges']:
        w=copy.deepcopy(e);w.update(bare=False,od=1.8,depth=max(p[2] for p in e['path']),path3d=e['path'],path=[p[:2] for p in e['path']],anchors=[],tails=[])
        for side in ('a','b'):
            if not e[side]:continue
            t=next(t for t in L.DESIGN['tails'] if t['id']==e['id']+side)
            w['anchors'] += [t['anchor'],t['node']];w['tails'].append(copy.deepcopy(t))
        routes.append(w)
    return routes

def cable_exit(w):
    if w['b']:return []
    x=w['path3d'][-1][0]
    a=np.linspace(0,math.pi/2,33)
    p=[[x,-12+4*math.cos(t),8-4*math.sin(t)] for t in a]
    p += [[x,-12-4*math.sin(t),4*math.cos(t)] for t in a[1:]]
    p.append([x,-16,-10.2])
    return p

def pieces(w):
    s=[(w['path3d'],1.8)]
    if not w['b']:s.append((cable_exit(w),1.8))
    for t in w['tails']:
        x,y=L.mm(t['anchor']);s.append(([[x,y,0],[x,y,-2.3]],1.0))
        s.append(([[x,y,-1.2-z] for x,y,z in t['path']],1.0))
    return s

def validate(routes=None):
    routes=plan() if routes is None else routes;d=copy.deepcopy(L.DESIGN)
    assert len(routes)==35 and {w['id'] for w in routes}=={e['id'] for e in d['edges']}
    for e in d['edges']:
        w=next(w for w in routes if w['id']==e['id'])
        assert w['od']==1.8 and not w['bare']
        assert abs(w['depth']-max(p[2] for p in w['path3d']))<.001
        assert np.allclose(w['path'],np.array(w['path3d'])[:,:2],atol=.001)
        e['path']=w['path3d']
        for k in ['a','b','anchor_a','anchor_b','net']:
            if k in e:assert e[k]==w[k],('route endpoint changed',w['id'],k)
    report=check(d)
    report.update(routes=len(routes),minimum_body_gap_mm=round(M.validate()[0][0],3))
    return report
