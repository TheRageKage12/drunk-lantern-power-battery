"""
Render assembly views from cad/output: iso / front / rear / top, a cutaway through x=0, the cartridge, the cap's
electronics, an exploded view and a contact sheet of every printed part.  Output: docs/images/cad-*.png

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
COLORS = {'diffuser': WHITE, 'halo_ring': WHITE, 'wall_extension': WHITE, 'base_tray': DARK, 'cap_floor': DARK,
          'lock_wall': WHITE, 'led_panel': WHITE, 'socket_housing': GREY, 'rotor': GREY, 'socket_base': GREY, 'key_cap': GREY,
          'switch_bracket': GREY, 'plunger': GREY, 'glass_well': DARK, 'bay_floor': DARK, 'guide_boss': DARK, 'nozzle_guide': DARK}


TOOLS = {'thumb_test', 'emblem_jig', 'curtain_stencil', 'ring_sizer'}   # tool prints in cad/output, not lantern parts
ALTERNATES = {'key_cap'}                                                 # same pocket as key_ring (the default)
LED = (90, 255, 110)
SKIN = (230, 190, 160)
# exploded view: (dx, dy, dz) mm per part; anything not listed stays put
EXPLODE = {'top_cap': (0, 0, 120), 'cap_floor': (0, 0, 175), 'halo_ring': (0, 0, 250), 'emblem_lid': (0, 0, 275),
           'emblem_centre': (0, 0, 285), 'wall_extension': (0, 0, 55),
           'sphere_front': (0, -45, 0), 'sphere_rear': (0, 45, 0), 'bell_front': (0, -120, 0), 'diffuser': (0, -175, 0),
           'bell_rear': (0, 120, 0), 'curtain_clamp': (0, 170, 0), 'led_panel': (0, -18, 0),
           'handle_end_left': (-40, 0, 170), 'handle_end_right': (40, 0, 170), 'handle_arc_1': (0, 0, 200),
           'handle_arc_2': (0, 0, 200), 'handle_pivot_left': (-40, 0, 0), 'handle_pivot_right': (40, 0, 0),
           'glass_well': (0, 0, -35), 'foot': (0, 0, -95), 'base': (0, 0, -165), 'screw_cap': (0, 25, -165),
           'bag_cover': (0, 0, -215), 'base_tray': (0, 0, -260)}


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
        if name in TOOLS or name in ALTERNATES:
            continue
        m = trimesh.load(os.path.join(OUT, fn), force='mesh')
        if name in pl:
            steps = pl[name] if isinstance(pl[name], list) else [pl[name]]
            for axis, ang, (dx, dy, dz) in steps:
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
        if m.extents.max() > 60 and len(m.faces) < 200000:   # split big flat faces so the depth sort is right
            v, f = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=12.0)
            m = trimesh.Trimesh(v, f, process=False)
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
    render(solid, os.path.join(IMG, 'cad-assembly-rear.png'), az=180, el=0, title='assembly, your side: hand opening with the lock inside (cover not shown)')
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
        if n == 'fist_envelope':
            cut.append((m, SKIN))                   # the hand at the lock
        elif n.endswith('led_envelope'):
            cut.append((m, LED))
        elif n not in ('hand_path_envelope', 'glass_path_envelope', 'lug_sweep_envelope', 'curtain_envelope'):
            cut.append((m, ORANGE))
    render(cut, os.path.join(IMG, 'cad-cutaway.png'), az=-90, el=12,
           title='cutaway from the side; audience left, your side right; orange = bought parts (size allowances); green = LED strip; tan = hand')

    cartridge = [(meshes['base_tray'], DARK), (meshes['pump_envelope'], GREY), (meshes['bag_envelope'], (205, 175, 95)),
                 (meshes['pump_diode_envelope'], ORANGE), (meshes['pump_plug_envelope'], ORANGE)]
    lid = meshes['bag_cover'].copy(); lid.apply_translation((0, 0, 45)); cartridge.append((lid, GREEN))
    render(cartridge, os.path.join(IMG, 'cad-cartridge.png'), az=145, el=35,
           title='cartridge, bag cover lifted: pump (grey), 32 oz drink bag (tan), pump plug; drum and lantern removed')

    cap_names = ('cap_floor', 'powerbank_envelope', 'perfboard_envelope', 'board_components_envelope', 'buck_envelope',
                 'power_switch_envelope', 'charge_socket_envelope', 'battery_connector_envelope', 'inline_connectors_envelope')
    cap_colors = {'powerbank_envelope': (60, 70, 85), 'perfboard_envelope': (190, 145, 85),
                  'board_components_envelope': (75, 110, 165), 'buck_envelope': (75, 110, 165)}
    render([(meshes[n], cap_colors.get(n, COLORS.get(n, ORANGE))) for n in cap_names if n in meshes],
           os.path.join(IMG, 'cad-cap.png'), az=25, el=50,
           title='cap floor (inside the top cap, under the lid): battery, board, buck module, power switch, charge socket')

    # exploded: each part moved along the way it comes off (top stack up, bottom down, bells out, handle up)
    expl = []
    for n, m in printed.items():
        m = m.copy(); m.apply_translation(EXPLODE.get(n, (0, 0, 0))); expl.append((m, COLORS.get(n, GREEN)))
    render(expl, os.path.join(IMG, 'cad-exploded.png'), az=35, el=18, title='exploded: each part moved the way it comes off')

    # per-part sheet (print orientation = raw STL)
    tiles = []
    for fn in sorted(os.listdir(OUT)):
        if fn.endswith('.stl') and not fn.endswith('_envelope.stl') and not fn.startswith('assembly') and fn[:-4] not in TOOLS:
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
