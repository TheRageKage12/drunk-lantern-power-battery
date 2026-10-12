"""Place every part in the assembly frame, export assembly.step and a trimesh scene for renders."""
import os
import cadquery as cq


def place(wp, placement):
    """placement: (axis, angle_deg, (dx, dy, dz)) = rotate about the origin then translate,
    or a list of such steps applied in order."""
    if placement is None:
        return wp
    steps = placement if isinstance(placement, list) else [placement]
    out = wp
    for axis, angle, (dx, dy, dz) in steps:
        if angle:
            out = out.rotate((0, 0, 0), axis, angle)
        out = out.translate((dx, dy, dz))
    return out


def write_assembly(all_parts, placements, out_dir):
    asm = cq.Assembly(name='lantern')
    for name, (wp, _mod) in all_parts.items():
        placed = place(wp, placements.get(name))
        asm.add(placed, name=name)
    path = os.path.join(out_dir, 'assembly.step')
    asm.save(path)
    # also one merged STL of the whole assembly for quick viewing
    merged = None
    for name, (wp, _mod) in all_parts.items():
        placed = place(wp, placements.get(name))
        merged = placed if merged is None else merged.add(placed)
    if merged is not None:
        cq.exporters.export(merged, os.path.join(out_dir, 'assembly.stl'), tolerance=0.1, angularTolerance=0.2)
    print(f'assembly: {len(all_parts)} parts -> {path}')
