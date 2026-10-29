import math
import numpy as np
R=4.0
STEP=.65
def rounded(points):
 p=np.array(points,dtype=float)
 # A redundant point on a straight segment must not truncate the room for a bend.
 keep=[0]
 for i in range(1,len(p)-1):
  u=p[i]-p[i-1];v=p[i+1]-p[i]
  if np.linalg.norm(np.cross(u,v))>1e-5 or u@v<0:keep.append(i)
 p=p[keep+[len(p)-1]];cuts=[];arcs=[]
 for a,b,c in zip(p,p[1:],p[2:]):
  la=np.linalg.norm(b-a);lb=np.linalg.norm(c-b)
  if min(la,lb)<.01:return None
  u=(b-a)/la;v=(c-b)/lb;dot=float(np.clip(u@v,-1,1));theta=math.acos(dot)
  if theta<.001:cuts.append(0);arcs.append(np.array([b]));continue
  if theta>math.pi-.001:return None
  cut=R*math.tan(theta/2);cuts.append(cut)
  if cut>min(la,lb)-.01:return None
  start=b-u*cut;finish=b+v*cut;n=v-u*dot;n/=np.linalg.norm(n);centre=start+R*n
  va=(start-centre)/R;vb=(finish-centre)/R;axis=np.cross(va,vb);axis/=np.linalg.norm(axis)
  angle=math.acos(float(np.clip(va@vb,-1,1)))
  arcs.append(np.array([centre+R*(va*math.cos(t)+np.cross(axis,va)*math.sin(t)) for t in np.linspace(0,angle,max(8,math.ceil(angle*R/.2)))]))
 for i in range(len(cuts)-1):
  if cuts[i]+cuts[i+1]>np.linalg.norm(p[i+2]-p[i+1]):return None
 pts=np.vstack([p[0],*arcs,p[-1]])
 travel=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))];t=np.linspace(0,travel[-1],math.ceil(travel[-1]/STEP)+1)
 return np.array([np.interp(t,travel,pts[:,i]) for i in range(3)]).T
