"""One-off fix for paint-tray.blend, run headless:

    blender -b --factory-startup --disable-autoexec paint-tray.blend --python fix_mirror_seams.py -- out.blend

Outer and Inner are quarter models (a box cut by booleans) mirrored in X and Y. The
quarter is a closed solid, so its walls on the mirror planes end up *inside* the
mirrored result as zero-thickness sheets. This adds a "Remove Interior Faces" geometry
nodes modifier at the end of each stack that deletes every face whose edges are all
shared by more than two faces (Edge Neighbors > Face Count). An outside face always has
at least one ordinary two-face edge, so only the internal walls go. The original
modifiers stay editable. (A self-union Mesh Boolean doesn't remove these walls.)
"""

import sys

import bpy

GROUP = "Remove Interior Faces"
MODIFIER = "Remove Interior Faces"


def node_group() -> bpy.types.NodeTree:
    if GROUP in bpy.data.node_groups:
        return bpy.data.node_groups[GROUP]
    ng = bpy.data.node_groups.new(GROUP, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nodes, links = ng.nodes, ng.links
    group_in = nodes.new("NodeGroupInput")
    group_out = nodes.new("NodeGroupOutput")
    neighbors = nodes.new("GeometryNodeInputMeshEdgeNeighbors")  # Face Count per edge
    shared = nodes.new("FunctionNodeCompare")  # edge used by more than two faces
    shared.data_type, shared.operation = "INT", "GREATER_THAN"
    shared.inputs["B"].default_value = 2
    on_edges = nodes.new("GeometryNodeFieldOnDomain")  # evaluate per edge; a face is
    on_edges.domain, on_edges.data_type = "EDGE", "BOOLEAN"  # true when all its edges are
    delete = nodes.new("GeometryNodeDeleteGeometry")
    delete.domain, delete.mode = "FACE", "ONLY_FACE"
    for node, x in [(group_in, -800), (neighbors, -800), (shared, -550), (on_edges, -300), (delete, 0), (group_out, 250)]:
        node.location = (x, -200 if node in (neighbors, shared, on_edges) else 0)
    links.new(neighbors.outputs["Face Count"], shared.inputs["A"])
    links.new(shared.outputs["Result"], on_edges.inputs[0])
    links.new(on_edges.outputs[0], delete.inputs["Selection"])
    links.new(group_in.outputs["Geometry"], delete.inputs["Geometry"])
    links.new(delete.outputs["Geometry"], group_out.inputs["Geometry"])
    return ng


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    group = node_group()
    for name in ["Outer", "Inner"]:
        obj = bpy.data.objects[name]
        if MODIFIER in obj.modifiers:
            continue
        mod = obj.modifiers.new(MODIFIER, "NODES")  # appended last, after the Mirror
        mod.node_group = group
        print(f"fix: added {MODIFIER!r} to {name} (stack: {[m.name for m in obj.modifiers]})")
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True, copy=True)
    print(f"fix: saved {out}")


main()
