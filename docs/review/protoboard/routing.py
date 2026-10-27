"""Finite-diameter rear-wire routing, with four explicit assembly layers.

Every cable and board link has a reserved path, including its rise from the solder
joint. Same-pad ends share a solder joint; other insulated wires cannot overlap.
Uses shapely for geometric clearance checks; no CAD runtime required.
"""
import heapq, math
import numpy as np
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
import shapely
import layout as L

import mechanical as M
OD=M.WIRE_OD
CLEAR=.25
LAYERS=(2.7,4.6,6.5,8.4) # centres measured back from the solder face
REAR_GAP=M.REAR_GAP
STEP=.635


# A fixed routing priority makes regeneration deterministic. Long crowded links
# need room before the remaining short links are placed.
ORDER=['H10', 'W29', 'W09', 'W27', 'W11', 'W48', 'W47', 'W45', 'W40', 'H04', 'W10', 'W04', 'H02', 'W39', 'W08', 'H06', 'W51', 'W25', 'W33', 'H08', 'W38', 'W50', 'W35', 'W42', 'W23', 'W49', 'W26', 'W46', 'W52']

def plan(order=ORDER):
    routes=[]
    # Route internal links first; cable exits use the same finite-diameter rules.
    jobs=[dict(w) for w in L.WIRES]
    for i,(ref,pad,net,_) in enumerate(L.HARNESS):
        jobs.append(dict(id=ref,a=pad,b=None,bare=False,net=net,exit=(L.mm('K01')[0]+i*L.PITCH,-5.48)))
    jobs.sort(key=lambda w:(not w['bare'],order.index(w['id']) if w['id'] in order else 999,w['id'].startswith('H'),-math.dist(L.mm(w['a']), L.mm(w['b']) if w['b'] else w['exit'])))
    # Board is extended only above the top for the guided cable fan-out.
    xs=np.arange(-2,99)*STEP+L.ORIGIN[0]; ys=np.arange(-14,73)*STEP+L.ORIGIN[1]
    points=shapely.points(np.tile(xs,len(ys)),np.repeat(ys,len(xs)))
    domain=box(1,-7,69,49)
    mounts=unary_union([box(x-4.5,y-4.5,x+4.5,y+4.5) for x,y in L.MOUNTS])
    base_ok=shapely.contains(domain,points) & ~shapely.intersects(mounts.buffer(1.3),points)
    def grid(p):return int(round((p[0]-xs[0])/STEP)),int(round((p[1]-ys[0])/STEP))
    def xy(p):return (float(xs[p[0]]),float(ys[p[1]]))
    for job in jobs:
        start=L.mm(job['a']); end=L.mm(job['b']) if job['b'] else job['exit']
        pads={job['a']}|({job['b']} if job['b'] else set())
        if job['bare']:
            routes.append(dict(job,path=[start,end],depth=.55,od=.8));continue
        candidates=[]
        for depth in LAYERS:
            obstacles=[Point(L.mm(p['pad'])).buffer(OD/2+M.JOINT_RADIUS+.15) for p in L.PINS.values() if p['pad'] not in pads]; impossible=False
            for other in routes:
                # Shared pad branches merge within a small joint region only.
                shared=pads & ({other['a']}|({other['b']} if other['b'] else set()))
                shared_zone=unary_union([Point(L.mm(p)).buffer(2.3) for p in shared])
                line=LineString(other['path'])
                if abs(depth-other['depth'])<OD/2+other['od']/2+CLEAR:
                    obstacles.append(line.buffer(OD/2+other['od']/2+CLEAR).difference(shared_zone))
                # A higher wire's terminal leg is also an obstacle to a lower wire.
                if other['depth']>=depth-OD/2-other['od']/2-CLEAR:
                    for pad in (other['a'],other['b']):
                        if pad and pad not in shared:obstacles.append(Point(L.mm(pad)).buffer(OD/2+other['od']/2+CLEAR))
                # A new terminal leg must not cut through an existing horizontal wire.
                if depth>=other['depth']-OD/2-other['od']/2-CLEAR and other['depth']>1.5:
                    for p,pad in ((start,job['a']),(end,job['b'])):
                        if pad and pad not in shared and line.distance(Point(p))<OD/2+other['od']/2+CLEAR:
                            impossible=True
            if impossible:continue
            blocked=unary_union(obstacles)
            ok=(base_ok & ~shapely.intersects(blocked,points)).reshape(len(ys),len(xs))
            a,b=grid(start),grid(end)
            # Exact endpoint coordinates are on-grid except cable exits; the last segment is checked below.
            if not ok[a[1],a[0]] or not ok[b[1],b[0]]:continue
            first=(*a,-1); costs={first:0};prev={};q=[(0,0,first)];last=None
            while q:
                _,cost,state=heapq.heappop(q)
                if cost!=costs.get(state):continue
                x,y,d=state
                if (x,y)==b:last=state;break
                for nd,(dx,dy) in enumerate(((1,0),(-1,0),(0,1),(0,-1))):
                    nx,ny=x+dx,y+dy
                    if not(0<=nx<len(xs) and 0<=ny<len(ys) and ok[ny,nx]):continue
                    nc=cost+1+(3 if d not in (-1,nd) else 0)
                    ns=(nx,ny,nd)
                    if nc<costs.get(ns,1e20):
                        costs[ns]=nc;prev[ns]=state;heapq.heappush(q,(nc+abs(nx-b[0])+abs(ny-b[1]),nc,ns))
            if last is None:continue
            path=[]
            while last!=first:path.append(last[:2]);last=prev[last]
            path.append(a);path.reverse()
            corners=[path[0]]
            for i in range(1,len(path)-1):
                if (path[i][0]-path[i-1][0],path[i][1]-path[i-1][1])!=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1]):corners.append(path[i])
            corners.append(path[-1]);path=[xy(p) for p in corners];path[0]=start;path[-1]=end
            line=LineString(path)
            if line.intersects(blocked) or line.buffer(OD/2+.49).intersects(mounts):continue
            candidates.append((line.length+depth*.1,depth,path))
        if not candidates:
            raise AssertionError(('No physical wire route',job['id'],job['a'],job['b']))
        _,depth,path=min(candidates)
        routes.append(dict(job,path=path,depth=depth,od=OD))
    return sorted(routes,key=lambda w:w['id'])



def validate(routes, wire_od=None, clearance=CLEAR, joint_clearance=.15):
    """Independently check saved paths, wire crossings, terminal rises and mounts.

    Shared endpoint regions allow wire fan-out that is not modelled in detail.
    Paths describe routing corridors, not a supplier-specified bend radius. The
    drawing remains a soldering guide; form bends and inspect the assembled stack.
    """
    wire_od=M.WIRE_OD if wire_od is None else wire_od
    assert len(routes)==len(L.WIRES)+len(L.HARNESS)
    by_id={w['id']:w for w in routes}
    assert len(by_id)==len(routes)
    for w in L.WIRES:
        r=by_id[w['id']]
        assert (r['a'],r['b'],r['bare'])==(w['a'],w['b'],w['bare'])
    for ref,pad,net,_ in L.HARNESS:
        assert by_id[ref]['a']==pad and by_id[ref]['b'] is None
    mounts=unary_union([box(x-4.5,y-4.5,x+4.5,y+4.5) for x,y in L.MOUNTS])
    room=unary_union([box(0,0,70,50),box(25,-7,67,0)])
    for i,w in enumerate(routes):
        assert math.dist(w['path'][0],L.mm(w['a']))<1e-6
        if w['b']:assert math.dist(w['path'][-1],L.mm(w['b']))<1e-6
        assert w['od']==(.8 if w['bare'] else wire_od), (w['id'],'wire diameter')
        assert w['bare'] or w['depth']-w['od']/2>=M.JOINT_HEIGHT+.25, (w['id'],'solder height')
        assert w['depth']+w['od']/2<=REAR_GAP-.5, (w['id'],'rear gap')
        line=LineString(w['path']);tube=line.buffer(w['od']/2)
        assert room.covers(tube),(w['id'],'outside reserved volume')
        assert tube.distance(mounts)>=.49,(w['id'],'mount pad')
        pads={w['a']}|({w['b']} if w['b'] else set())
        if not w['bare']:
            for pin in L.PINS.values():
                if pin['pad'] not in pads:
                    assert line.distance(Point(L.mm(pin['pad'])))>=w['od']/2+M.JOINT_RADIUS+joint_clearance-1e-6,(w['id'],'unrelated joint',pin)
        for other in routes[:i]:
            otherpads={other['a']}|({other['b']} if other['b'] else set())
            shared=pads & otherpads
            joint=unary_union([Point(L.mm(p)).buffer(2.3) for p in shared])
            ol=LineString(other['path'])
            separation=(w['od']+other['od'])/2+clearance
            if abs(w['depth']-other['depth'])<separation-1e-6:
                assert not line.intersects(ol.buffer(separation-1e-6).difference(joint)),(w['id'],other['id'],'crossing')
            for upper,lower,lp in ((w,other,ol),(other,w,line)):
                if upper['bare'] or lower['depth']<=1.5:continue
                if upper['depth']>=lower['depth']-separation:
                    for pad in (upper['a'],upper['b']):
                        if pad and pad not in shared:
                            assert lp.distance(Point(L.mm(pad)))>=separation-1e-6,(w['id'],other['id'],'terminal rise')
    return {'routes':len(routes),'maximum_rear_extent_mm':max(w['depth']+w['od']/2 for w in routes)}


if __name__=='__main__':
    import json
    routes=plan()
    print(json.dumps(validate(routes),indent=2))
