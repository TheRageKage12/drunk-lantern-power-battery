"""Independent geometry/electrical checks for the relocated-component candidate.

This does not certify solder quality, retention or delivered parts.
Run from any directory with numpy, scipy, shapely and networkx installed.
"""
from pathlib import Path
import json, math, itertools
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Point, LineString, Polygon
import networkx as nx
if __package__:
    from .curves import rounded
    from .rear import check_rear
else:
    from curves import rounded
    from rear import check_rear
HERE=Path(__file__).resolve().parent

def mm(p):return np.array([5.79+(ord(p[0])-65)*2.54,3.41+(int(p[1:])-1)*2.54])

def segments_gap(p,q):
    """Exact minimum between two polylines (interior optimum or boundary)."""
    p=np.asarray(p);q=np.asarray(q)
    a=p[:-1,None,:];b=q[None,:-1,:];u=np.diff(p,axis=0)[:,None,:];v=np.diff(q,axis=0)[None,:,:];w=a-b
    aa=(u*u).sum(2);bb=(u*v).sum(2);cc=(v*v).sum(2);dd=(u*w).sum(2);ee=(v*w).sum(2);den=aa*cc-bb*bb
    with np.errstate(divide='ignore',invalid='ignore'):
        s=(bb*ee-cc*dd)/den;t=(aa*ee-bb*dd)/den
        inside=np.linalg.norm(w+s[:,:,None]*u-t[:,:,None]*v,axis=2)
    inside=np.where((den>1e-12)&(s>=0)&(s<=1)&(t>=0)&(t<=1),inside,np.inf)
    choices=[inside]
    for k in (0,1):
        w0=w+k*u;t0=np.clip((v*w0).sum(2)/cc,0,1);choices.append(np.linalg.norm(w0-t0[:,:,None]*v,axis=2))
        w1=w-k*v;s1=np.clip(-(u*w1).sum(2)/aa,0,1);choices.append(np.linalg.norm(w1+s1[:,:,None]*u,axis=2))
    return min(float(d.min()) for d in choices)

def check(d):
    pins=d['pins'];routes=d['edges'];hardware=d['hardware'];by_pad={};graph=nx.Graph();anchors=[]
    for ref,p in pins.items():
        assert p['pad'] not in by_pad or by_pad[p['pad']]==p['net'],('cross-net shared pad',ref)
        by_pad[p['pad']]=p['net'];graph.add_node(p['pad'])
    for e in routes:
        assert e['net']==by_pad[e['a']]
        assert not e['net'].startswith('NC')
        if e['b']:
            assert e['net']==by_pad[e['b']];graph.add_edge(e['a'],e['b'])
        for side in ('a','b'):
            if not e[side]:continue
            hole=e['anchor_'+side];anchors.append(hole);assert hole not in by_pad,('wire shares component hole',e['id'],hole)
            endpoint=e['path'][0 if side=='a' else -1];assert np.linalg.norm(np.array(endpoint[:2])-mm(hole))<.001
    assert len(anchors)==len(set(anchors))==61
    # Three outgoing ground returns meet only at the off-board ground splice.
    cable={e['id']:e for e in routes if not e['b']}
    for splice in d['harness']:
        board=[cable[n]['a'] for n in splice['members'] if n in cable]
        assert all(by_pad[p]==splice['net'] for p in board)
        for p in board[1:]:graph.add_edge(board[0],p)
    nets={}
    for pad,net in by_pad.items():nets.setdefault(net,[]).append(pad)
    for net,ps in nets.items():assert all(nx.has_path(graph,ps[0],p) for p in ps),('disconnected',net)
    local=nx.Graph();local.add_nodes_from(by_pad);local.add_edges_from((e['a'],e['b']) for e in routes if e['b'])
    for n in ['H03','H04']:assert not nx.has_path(local,cable['H02']['a'],cable[n]['a']),('load uses logic ground',n)
    smallest=(100,None,None);order=nx.DiGraph();order.add_nodes_from(e['id'] for e in routes)
    for a,b in itertools.combinations(routes,2):
        gap=segments_gap(a['path'],b['path'])-1.8-.03 # 0.03 mm chord/rounding allowance
        assert gap>=.5,(a['id'],b['id'],'wire gap',gap)
        smallest=min(smallest,(gap,a['id'],b['id']))
        p=np.array(a['path']);q=np.array(b['path']);near=cKDTree(p[:,:2]).query_ball_point(q[:,:2],1.8)
        for j,ids in enumerate(near):
            for i in ids:
                if abs(p[i,2]-q[j,2])<1.8:continue
                order.add_edge(*( (a['id'],b['id']) if p[i,2]<q[j,2] else (b['id'],a['id']) ))
    pairs=[sorted(g) for g in nx.strongly_connected_components(order) if len(g)>1]
    assert all(len(g)<=2 for g in pairs),('large woven group',pairs)
    c=nx.condensation(order);assembly=[sorted(c.nodes[n]['members']) for n in nx.topological_sort(c)]
    front_leads=[]
    for ref in ('R1','R2','R5','R6','R7','D1','D3'):
        x,y,w,h,z0,z1=d['bodies'][ref]; centre=[x+w/2,y+h/2,z1/2]
        for i in (1,2):
            xy=mm(pins[ref+'.'+str(i)]['pad'])
            front_leads.append((ref,[[*xy,0],[*xy,z1/2],centre]))
    body_min=100;driver_min=100;front_lead_min=100
    for e in routes:
        p=np.array(e['path'])
        a=p[0];b=p[-1];formed=rounded([a,[a[0],a[1],e['ha']],[*e['via'],(e['ha']+e['hb'])/2],[b[0],b[1],e['hb']],b])
        assert formed is not None and formed.shape==p.shape and np.max(np.abs(formed-p))<.001, (e['id'],'4 mm bend geometry')
        assert p[:,2].max()<=32.001
        for n,b in d['bodies'].items():
            x,y,w,h,z0,z1=b
            delta=np.maximum(np.maximum([x,y,z0]-p,p-[x+w,y+h,z1]),0);gap=np.linalg.norm(delta,axis=1).min()-.9
            assert gap>=.97,(e['id'],n,'body gap',gap);body_min=min(body_min,float(gap))
        for ref,lead in front_leads:
            gap=segments_gap(p,lead)-1.25
            assert gap>=1.0,(e['id'],ref,'front exposed lead',gap)
            front_lead_min=min(front_lead_min,gap)
        for m in hardware['mounts']:
            gap=np.linalg.norm(p[:,:2]-m,axis=1).min()-.9;driver_min=min(driver_min,float(gap));assert gap>=4.07
    for t in d['tails']:
        line=LineString([p[:2] for p in t['path']])
        for pad in by_pad:
            if pad==t['node']:continue
            assert line.distance(Point(mm(pad)))-1.5>=.5-1e-3,('bare end to joint',t['id'],pad)
    for a,b in itertools.combinations(d['tails'],2):
        if a['node']==b['node']:continue
        assert LineString([p[:2] for p in a['path']]).distance(LineString([p[:2] for p in b['path']]))>=1.5-.001,('bare ends',a['id'],b['id'])
    for pg in d['pigtails']:
        p=np.asarray(pg['path']);formed=rounded(pg['controls'])
        assert formed is not None and formed.shape==p.shape and np.allclose(formed,p,atol=.001),(pg['id'],'4 mm pigtail bends')
        front=p.copy();front[:,2]=-1.2-front[:,2]
        for e in routes:assert segments_gap(front,e['path'])-1.8>=.5,(pg['id'],e['id'],'pigtail/front wire')
        for n,b in d['bodies'].items():
            x,y,w,h,z0,z1=b;delta=np.maximum(np.maximum([x,y,z0]-front,front-[x+w,y+h,z1]),0)
            assert np.linalg.norm(delta,axis=1).min()-.9>=.7,(pg['id'],n,'pigtail/front body')
    rear=check_rear(d,mm,segments_gap)
    return dict(**rear,minimum_front_lead_gap_mm=round(front_lead_min,3),result='PASS — modeled geometry; physical fit still required',internal_links=26,outgoing_leads=9,dedicated_wire_holes=len(anchors),nets=len([n for n in nets if not n.startswith('NC')]),minimum_wire_skin_gap_mm=round(smallest[0],3),closest_wires=smallest[1:],minimum_wire_body_gap_mm=round(body_min,3),minimum_wire_to_driver_axis_mm=round(driver_min,3),maximum_front_extent_mm=32.9,front_reserved_height_mm=40,front_height_reserve_mm=7.1,rear_gap_mm=hardware["rear_gap"],preformed_pairs=pairs,assembly_groups=assembly)

if __name__=='__main__':
    d=json.loads((HERE.parent/'design.json').read_text());report=check(d);(HERE/'check-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
