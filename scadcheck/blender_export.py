"""Export parts from a .blend file to STL. Runs *inside* Blender:

    blender -b --factory-startup --disable-autoexec design.blend \
        --python scadcheck/blender_export.py -- spec.json

spec.json: {"parts": {"<part name>": {"objects": ["Obj", ...], "out": "/path/part.stl"}}}
An "objects" entry of "collection:<Name>" means every mesh object in that collection
(recursively). Each part is the listed objects' evaluated meshes (modifiers applied,
hidden or not) in world coordinates, joined into one STL. Units follow the file's
scene: with Length = millimetres and Unit Scale = 0.001, one Blender unit is 1 mm.
"""

import json
import struct
import sys
from pathlib import Path

import bmesh
import bpy


def objects_for(names: list[str]) -> list[bpy.types.Object]:
    found = []
    for name in names:
        if name.startswith("collection:"):
            coll = bpy.data.collections.get(name.split(":", 1)[1])
            if coll is None:
                raise SystemExit(f"no collection {name!r} in {bpy.data.filepath}")
            found += [o for o in coll.all_objects if o.type == "MESH"]
        else:
            obj = bpy.data.objects.get(name)
            if obj is None:
                raise SystemExit(f"no object {name!r} in {bpy.data.filepath}")
            found.append(obj)
    return found


def triangles(obj, depsgraph, to_mm: float):
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(obj.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    tris = [[tuple(v.co * to_mm) for v in f.verts] for f in bm.faces]
    bm.free()
    ev.to_mesh_clear()
    return tris


def write_stl(path: Path, tris) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"scadcheck blender export".ljust(80, b" "))
        fh.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            fh.write(struct.pack("<12fH", 0, 0, 0, *a, *b, *c, 0))


def main():
    spec = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
    units = bpy.context.scene.unit_settings
    to_mm = units.scale_length * 1000 if units.system == "METRIC" else 1.0  # Blender units -> mm
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for name, part in spec["parts"].items():
        tris = [t for obj in objects_for(part["objects"]) for t in triangles(obj, depsgraph, to_mm)]
        if not tris:
            raise SystemExit(f"part {name!r} has no geometry")
        write_stl(Path(part["out"]), tris)
        print(f"scadcheck: exported {name} ({len(tris)} triangles)")


main()
