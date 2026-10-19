"""Render key_ring in its two print colours: a white emblem outline on a green ring.

    cd cad && python3 build.py && python3 render_ring_colour.py    # -> ../docs/images/ring-white-outline.png

key_ring prints emblem down. Its first EM_STEP mm (0.6 mm, three 0.2 mm layers) are only the faces of the circle
and bars; the centre disc starts at EM_STEP. Printing those layers white and the rest green gives a white outline
with a green centre, with no CAD change. Each STL triangle is coloured by its print height, as the printer will.
"""
import math, os, numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFont
from parts.socket import EM_STEP

HERE = os.path.dirname(os.path.abspath(__file__))
GREEN, WHITE, BG = np.array([38, 150, 64]), np.array([238, 238, 232]), (247, 247, 244)


def render(mesh, colours, az, el, size=520, ss=3):
    """Painter's-algorithm render of the ring as worn (emblem up), supersampled ss times."""
    v = mesh.vertices.copy()
    v[:, 2] = -v[:, 2]                       # print frame has the emblem on the bed; flip it up
    v -= (v.max(0) + v.min(0)) / 2
    a, e = math.radians(az), math.radians(el)
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
    v = v @ Rz.T @ Rx.T
    f = mesh.faces[:, ::-1]                  # the flip mirrors the mesh; reverse winding to match
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1), 1e-9)[:, None]
    light = np.array([-0.45, -0.6, 0.66]); light /= np.linalg.norm(light)
    shade = np.clip(0.38 + 0.62 * np.abs(n @ light), 0, 1)
    S = size * ss
    pts = v[:, [0, 2]] * (S * 0.86 / 40.0)
    pts[:, 1] = -pts[:, 1]
    pts += S / 2
    img = Image.new('RGB', (S, S), BG)
    d = ImageDraw.Draw(img)
    for i in np.argsort(v[:, 1][f].mean(1))[::-1]:
        d.polygon([tuple(p) for p in pts[f[i]]], fill=tuple(int(c) for c in colours[i] * shade[i]))
    return img.resize((size, size), Image.LANCZOS)


if __name__ == '__main__':
    mesh = trimesh.load(os.path.join(HERE, 'output', 'key_ring.stl'), force='mesh')
    colours = np.tile(GREEN, (len(mesh.faces), 1)).astype(float)
    colours[mesh.triangles_center[:, 2] < EM_STEP] = WHITE
    T = 520
    sheet = Image.new('RGB', (2 * T, T + 70), BG)
    for k, (az, el) in enumerate([(30, 38), (0, 89.9)]):
        sheet.paste(render(mesh, colours, az, el, T), (k * T, 0))
    ImageDraw.Draw(sheet).text((20, T + 18), f'key_ring, white outline: layers below {EM_STEP:.1f} mm white, the rest green',
                               fill=(40, 40, 40), font=ImageFont.load_default(size=22))
    out = os.path.join(HERE, '..', 'docs', 'images', 'ring-white-outline.png')
    sheet.save(out)
    print('wrote', os.path.normpath(out))
