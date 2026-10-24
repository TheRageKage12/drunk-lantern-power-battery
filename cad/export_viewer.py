"""Build docs/assembly-viewer/index.html: the 3D assembly viewer with every part's mesh inlined.

    cd cad && python3 export_viewer.py

Each part is placed in the assembly frame (as in build.py), tessellated, packed as float32
vertices + uint32 triangles and inlined as base64, so the page is one self-contained file that
opens from GitHub (via a static-file proxy) or from a downloaded copy. Re-run after any CAD change.
Part names, colours, explode offsets and the assembly steps live in viewer.template.html.
The tools (thumb_test, emblem_jig, curtain_stencil, ring_sizer) are not part of the lantern and are left out.
"""
import sys, os, json, base64, importlib, pkgutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np, cadquery as cq
import parts
from assembly import place
DOCS = os.path.join(HERE, '..', 'docs', 'assembly-viewer')
SKIP = {'key_cap'}                         # alternative to key_ring for the same pocket; key_ring is the default
KEEP_ENV = {'pump_envelope', 'bag_envelope', 'powerbank_envelope', 'perfboard_envelope', 'board_components_envelope',
            'buck_envelope', 'power_switch_envelope', 'charge_socket_envelope', 'glass_envelope',
            'front_led_envelope', 'rear_led_envelope', 'panel_led_envelope', 'cap_led_envelope', 'curtain_envelope'}
TOL, ANG_TOL = 0.12, 0.2                   # tessellation: linear (mm) and angular (rad) tolerance

meshes = {}
for m in pkgutil.iter_modules(parts.__path__):
    mod = importlib.import_module(f'parts.{m.name}')
    if not hasattr(mod, 'build'): continue
    built = mod.build(); pl = mod.placements() if hasattr(mod, 'placements') else {}
    for name, wp in built.items():
        if name in SKIP: continue
        if name.endswith('_envelope') and name not in KEEP_ENV: continue
        meshes[name] = place(wp, pl.get(name))

# screw_cap is placed at the drum screw at +Y (90 deg); copy it to the other two drum screws. The handle-lap and
# pivot caps (22 more) are too small to read at viewer scale and are left out.
from parts import base as B
for i, a in enumerate(B.BASE_JOINT_ANGLES[1:], 2):
    meshes[f'screw_cap_{i}'] = meshes['screw_cap'].rotate((0, 0, 0), (0, 0, 1), a - B.BASE_JOINT_ANGLES[0])

index, blobs, off = [], [], 0
for name, wp in meshes.items():
    shape = wp.val() if len(wp.vals()) == 1 else cq.Compound.makeCompound(wp.vals())
    vs, tris = shape.tessellate(TOL, ANG_TOL)
    v = np.array([[p.x, p.y, p.z] for p in vs], dtype=np.float32)
    t = np.array(tris, dtype=np.uint32)
    bb = [v.min(0).round(2).tolist(), v.max(0).round(2).tolist()]
    vb = v.tobytes(); ib = t.astype(np.uint32).tobytes()
    index.append({'name': name, 'v': [off, len(v)], 'i': [off + len(vb), len(t) * 3], 'bbox': bb})
    blobs += [vb, ib]; off += len(vb) + len(ib)
    if '-v' in sys.argv:
        print(f'  {name:28s} {len(t):7d} tris  bbox {bb[0]} .. {bb[1]}')
data = base64.b64encode(b''.join(blobs)).decode('ascii')
tpl = open(os.path.join(DOCS, 'viewer.template.html'), encoding='utf-8').read()
assert tpl.count('<script>/*MESH_DATA*/</script>') == 1
inline = '<script>window.MESH_INDEX=' + json.dumps(index, separators=(',', ':')) + ';window.MESH_B64="' + data + '";</script>'
out = os.path.join(DOCS, 'index.html')
open(out, 'w', encoding='utf-8').write(tpl.replace('<script>/*MESH_DATA*/</script>', inline))
print(f'{len(index)} meshes, {off} bytes packed -> {os.path.relpath(out)} ({os.path.getsize(out) / 1e6:.1f} MB)')
