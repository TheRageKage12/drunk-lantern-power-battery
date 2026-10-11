"""Simple painter's-algorithm STL renderer -> PNG (no GPU needed)."""
import sys, os, math, numpy as np, trimesh
from PIL import Image, ImageDraw

def render(mesh, out, size=700, az=35, el=25, color=(70,170,90), bg=(255,255,255), title=None):
    m = mesh.copy()
    v = m.vertices - m.bounds.mean(axis=0)
    # rotate: azimuth about Z(up), elevation about X
    a, e = math.radians(az), math.radians(el)
    Rz = np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    Rx = np.array([[1,0,0],[0,math.cos(e),-math.sin(e)],[0,math.sin(e),math.cos(e)]])
    v = v @ Rz.T @ Rx.T
    # screen: x right, z up(view y), depth = -y
    pts = v[:, [0,2]]
    depth = v[:,1]
    scale = (size*0.9) / max(np.ptp(pts[:,0]), np.ptp(pts[:,1]), 1e-6)
    pts = (pts - pts.min(axis=0)) * scale
    pts[:,1] = pts[:,1].max() - pts[:,1]
    pad = (size - pts.max(axis=0)) / 2
    pts = pts + pad
    f = m.faces
    tri = v[f]
    n = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
    nl = np.linalg.norm(n, axis=1); nl[nl==0]=1; n = n/nl[:,None]
    light = np.array([-0.4, -0.7, 0.6]); light/=np.linalg.norm(light)
    shade = np.clip(0.35 + 0.65*np.abs(n@light), 0, 1)
    order = np.argsort(depth[f].mean(axis=1))[::-1]  # far first (y toward viewer negative?)
    img = Image.new('RGB', (size, size+ (30 if title else 0)), bg)
    d = ImageDraw.Draw(img)
    P = pts[f]
    for i in order:
        c = tuple(int(ch*shade[i]) for ch in color)
        d.polygon([tuple(p) for p in P[i]], fill=c)
    if title:
        d.text((10, size+8), title, fill=(0,0,0))
    img.save(out)

if __name__ == '__main__':
    src, outdir = sys.argv[1], sys.argv[2]
    for fn in sorted(os.listdir(src)):
        if not fn.lower().endswith('.stl'): continue
        m = trimesh.load(os.path.join(src, fn), force='mesh')
        for az, el, tag in [(35,25,'iso'),(0,0,'front'),(0,89,'top')]:
            render(m, os.path.join(outdir, f"{fn[:-4]}_{tag}.png"), az=az, el=el, title=f"{fn} {tag}  ext={np.round(m.extents,1)}")
        print("rendered", fn)
