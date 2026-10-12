"""
Render assembly views from cad/output: iso / front / rear / top, a cutaway through x=0, an exploded view
and a contact sheet of every printed part.  Output: docs/images/cad-*.png

    python3 render_views.py
"""
import importlib
import math
import os
import pkgutil
import sys

import numpy as np
import trimesh
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'output')
IMG = os.path.join(HERE, '..', 'docs', 'images')
sys.path.insert(0, HERE)
import parts  # noqa: E402

GREEN = (62, 160, 84)
DARK = (40, 110, 60)
GREY = (150, 150, 150)
ORANGE = (235, 150, 60)     # hardware envelopes
WHITE = (235, 235, 235)     # diffuser / halo
COLORS = {'diffuser': WHITE, 'halo': WHITE, 'base_door': DARK, 'sphere_hatch': DARK}


def placements():
    pl = {}
    for m in pkgutil.iter_modules(parts.__path__):
        mod = importlib.import_module(f'parts.{m.name}')
        if hasattr(mod, 'placements'):
            pl.update(mod.placements())
    return pl


def load_placed(pl):
    """name -> trimesh in the assembly frame."""
    meshes = {}
    for fn in sorted(os.listdir(OUT)):
        if not fn.endswith('.stl') or fn.startswith('assembly'):
            continue
        name = fn[:-4]
        m = trimesh.load(os.path.join(OUT, fn), force='mesh')
        if name in pl:
            axis, ang, (dx, dy, dz) = pl[name]
            if ang:
                m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(ang), axis))
            m.apply_translation((dx, dy, dz))
        meshes[name] = m
    return meshes


def render(items, out, size=900, az=35, el=25, title=None, zoom=0.92):
    """items: list of (mesh, color). Painter's algorithm, orthographic, no GPU."""
    allv = np.vstack([m.vertices for m, _ in items])
    center = (allv.min(axis=0) + allv.max(axis=0)) / 2
    a, e = math.radians(az), math.radians(el)
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
    R = Rx @ Rz
    light = np.array([-0.4, -0.7, 0.6]); light /= np.linalg.norm(light)
    tris, depth, cols = [], [], []
    for m, color in items:
        v = (m.vertices - center) @ R.T
        f = m.faces
        t = v[f]
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        nl = np.linalg.norm(n, axis=1); nl[nl == 0] = 1; n /= nl[:, None]
        shade = np.clip(0.35 + 0.65 * np.abs(n @ light), 0, 1)
        tris.append(t); depth.append(t[:, :, 1].mean(axis=1))
        cols.append(np.array(color)[None, :] * shade[:, None])
    tris = np.vstack(tris); depth = np.concatenate(depth); cols = np.vstack(cols)
    pts = tris[:, :, [0, 2]].reshape(-1, 2)
    span = max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]), 1e-6)
    scale = size * zoom / span
    pts = (pts - pts.min(axis=0)) * scale
    pts[:, 1] = pts[:, 1].max() - pts[:, 1]
    pad = (size - pts.max(axis=0)) / 2
    pts = (pts + pad).reshape(-1, 3, 2)
    order = np.argsort(depth)[::-1]
    img = Image.new('RGB', (size, size + (28 if title else 0)), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for i in order:
        c = tuple(int(x) for x in cols[i])
        d.polygon([tuple(p) for p in pts[i]], fill=c)
    if title:
        d.text((10, size + 8), title, fill=(0, 0, 0))
    img.save(out)


def main():
    os.makedirs(IMG, exist_ok=True)
    pl = placements()
    meshes = load_placed(pl)
    printed = {n: m for n, m in meshes.items() if not n.endswith('_envelope')}
    envelopes = {n: m for n, m in meshes.items() if n.endswith('_envelope')}
    solid = [(m, COLORS.get(n, GREEN)) for n, m in printed.items()]

    render(solid, os.path.join(IMG, 'cad-assembly-iso.png'), az=35, el=22, title='assembly, iso (front-left)')
    render(solid, os.path.join(IMG, 'cad-assembly-front.png'), az=0, el=0, title='assembly, front (audience side)')
    render(solid, os.path.join(IMG, 'cad-assembly-rear.png'), az=180, el=0, title='assembly, rear (owner side: door + hatch)')
    render(solid, os.path.join(IMG, 'cad-assembly-top.png'), az=0, el=89, title='assembly, top')

    # cutaway: keep x < 0 half of every printed part, show envelopes whole (they are inside)
    cut = []
    for n, m in printed.items():
        try:
            s = trimesh.intersections.slice_mesh_plane(m, plane_normal=[-1, 0, 0], plane_origin=[0, 0, 0], cap=True)
        except Exception:
            s = trimesh.intersections.slice_mesh_plane(m, plane_normal=[-1, 0, 0], plane_origin=[0, 0, 0], cap=False)
        if s is not None and len(s.faces):
            cut.append((s, COLORS.get(n, GREEN)))
    for n, m in envelopes.items():
        cut.append((m, ORANGE))
    render(cut, os.path.join(IMG, 'cad-cutaway.png'), az=90, el=12, title='cutaway at x=0 seen from +X; orange = hardware envelopes (jar, pump, bank, glass)')

    # exploded: lift each printed part by its order in Z
    names = sorted(printed, key=lambda n: printed[n].bounds[0][2])
    expl = []
    for i, n in enumerate(names):
        m = printed[n].copy(); m.apply_translation((0, 0, 35 * i)); expl.append((m, COLORS.get(n, GREEN)))
    render(expl, os.path.join(IMG, 'cad-exploded.png'), az=35, el=18, title='exploded (each part lifted 35 mm per step)')

    # per-part sheet (print orientation = raw STL)
    tiles = []
    for fn in sorted(os.listdir(OUT)):
        if fn.endswith('.stl') and not fn.endswith('_envelope.stl') and not fn.startswith('assembly'):
            m = trimesh.load(os.path.join(OUT, fn), force='mesh')
            tmp = os.path.join(OUT, '_tile.png')
            render([(m, GREEN)], tmp, size=300, az=35, el=25, title=f'{fn[:-4]}  {np.round(m.extents, 0).astype(int).tolist()} mm')
            tiles.append(Image.open(tmp).copy())
    if tiles:
        cols = 4
        rows = (len(tiles) + cols - 1) // cols
        w, h = tiles[0].size
        sheet = Image.new('RGB', (cols * w, rows * h), (255, 255, 255))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * w, (i // cols) * h))
        sheet.save(os.path.join(IMG, 'cad-parts-sheet.png'))
        os.remove(os.path.join(OUT, '_tile.png'))
    print('rendered', len(printed), 'parts ->', os.path.abspath(IMG))


if __name__ == '__main__':
    main()
