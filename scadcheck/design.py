"""Render a design's parts to STL (OpenSCAD or Blender) and load them as meshes."""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

from .printers import DEFAULT_PRINTER, PRINTERS, Printer

# Every Design built this session, so the pytest plugin can describe its parts
# in the report that the viewer reads.
REGISTRY: dict[str, "Design"] = {}


def openscad_exe() -> str:
    exe = os.environ.get("OPENSCAD") or shutil.which("openscad")
    if not exe:
        raise RuntimeError("openscad not found on PATH (or set $OPENSCAD)")
    return exe


def _openscad(source: Path, defines: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [openscad_exe(), "-o", str(out)]
    for k, v in defines.items():
        cmd += ["-D", f"{k}={json.dumps(v) if isinstance(v, str) else v}"]
    cmd.append(str(source))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not out.exists():
        raise RuntimeError(f"openscad failed for {source} {defines}:\n{result.stderr}")


BLENDER_EXPORT = Path(__file__).with_name("blender_export.py")


def blender_exe() -> str:
    exe = os.environ.get("BLENDER") or shutil.which("blender")
    if not exe:  # default Windows install location, newest version first
        found = sorted(glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe"), reverse=True)
        exe = found[0] if found else None
    if not exe:
        raise RuntimeError("blender not found on PATH (or set $BLENDER)")
    return exe


def _blender(blend_file: Path, parts: dict[str, tuple[list[str], Path]]) -> None:
    """Export several parts from one .blend in a single headless Blender run."""
    first_out = next(iter(parts.values()))[1]
    spec_file = first_out.parent / f".{blend_file.stem}-export.json"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text(json.dumps(
        {"parts": {name: {"objects": objs, "out": str(out)} for name, (objs, out) in parts.items()}}
    ), encoding="utf-8")
    cmd = [blender_exe(), "-b", "--factory-startup", "--disable-autoexec", str(blend_file),
           "--python", str(BLENDER_EXPORT), "--", str(spec_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    missing = [n for n, (_, out) in parts.items() if not out.exists()]
    if result.returncode != 0 or missing:
        raise RuntimeError(f"blender export failed for {blend_file} {missing}:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}")


def remove_interior_sheets(mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, int]:
    """Drop zero-thickness internal walls: flat face regions whose whole boundary lies
    on edges shared by more than two faces. Blender's Mirror modifier leaves one when
    the mirrored half is closed at the mirror plane. Returns (mesh, faces removed)."""
    edge_faces = defaultdict(list)
    tri_edges = lambda f: ((f[0], f[1]), (f[1], f[2]), (f[2], f[0]))
    for fi, f in enumerate(mesh.faces):
        for a, b in tri_edges(f):
            edge_faces[(min(a, b), max(a, b))].append(fi)
    parent = list(range(len(mesh.faces)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    normals = mesh.face_normals
    for faces in edge_faces.values():  # group coplanar neighbours joined by ordinary edges
        if len(faces) == 2 and abs(np.dot(normals[faces[0]], normals[faces[1]])) > 0.9999:
            parent[find(faces[0])] = find(faces[1])
    groups = defaultdict(list)
    for fi in range(len(mesh.faces)):
        groups[find(fi)].append(fi)
    drop = []
    for faces in groups.values():
        members = set(faces)
        boundary = [e for f in faces for e in tri_edges(mesh.faces[f])
                    if not set(edge_faces[(min(e), max(e))]) <= members]
        if boundary and all(len(edge_faces[(min(e), max(e))]) > 2 for e in boundary):
            drop += faces
    if not drop:
        return mesh, 0
    keep = np.ones(len(mesh.faces), dtype=bool)
    keep[drop] = False
    out = mesh.copy()
    out.update_faces(keep)
    out.remove_unreferenced_vertices()
    return out, len(drop)


def to_manifold(mesh: trimesh.Trimesh, name: str = "mesh") -> manifold3d.Manifold:
    """manifold3d solid from a trimesh, for booleans, slicing and decompose()."""
    solid = manifold3d.Manifold(
        manifold3d.Mesh(
            vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
            tri_verts=np.asarray(mesh.faces, dtype=np.uint32),
        )
    )
    if solid.status() != manifold3d.Error.NoError:
        raise ValueError(f"{name}: mesh is not a valid manifold ({solid.status()})")
    return solid


def scad(path: str, print: str | None = None, **defines) -> dict:
    """Part spec for Design(parts=...): render `path` with `-D` defines for the
    assembled position, and optionally a separate `print` file for the geometry that
    actually gets sliced (e.g. a part file that renders in print orientation).

        scad("motorCar.scad", part="gear1", print="parts/gear1.scad")
    """
    return {"scad": path, "print": print, "defines": defines}


def blend(path: str, objects: list[str] | str) -> dict:
    """Part spec for a Blender design: the listed objects (or "collection:<Name>") of
    `path`, with modifiers applied, joined into one part in their placed positions.

        blend("paint-tray.blend", ["Outer"])
    """
    return {"blend": path, "objects": [objects] if isinstance(objects, str) else list(objects)}


@dataclass
class Part:
    name: str
    source: Path  # .scad/.blend file that produces this part in its assembled position
    stl: Path
    kind: str = "part"  # "part" (printed) or "vitamin" (off-the-shelf hardware)
    color: str | None = None
    defines: dict = field(default_factory=dict)  # -D overrides for a .scad `source`
    blend_objects: list[str] | None = None  # objects to export from a .blend `source`
    print_source: Path | None = None  # .scad that renders the printed geometry, if not `source`
    print_raw: Path | None = None  # where print_source renders to
    # How the part goes on the bed, as OpenSCAD rotate([x, y, z]) degrees, applied to
    # the print geometry (print_source if set, else the assembled part).
    print_rotation: tuple[float, float, float] = (0, 0, 0)

    @cached_property
    def raw_mesh(self) -> trimesh.Trimesh:
        """The part exactly as exported (what the watertight check looks at)."""
        return trimesh.load(self.stl, force="mesh")

    @cached_property
    def _repaired(self) -> tuple[trimesh.Trimesh, int]:
        if self.blend_objects is None:
            return self.raw_mesh, 0
        return remove_interior_sheets(self.raw_mesh)

    @property
    def interior_faces_removed(self) -> int:
        return self._repaired[1]

    @property
    def mesh(self) -> trimesh.Trimesh:
        """The part in its assembled position. Blender exports have zero-thickness
        internal walls removed (see remove_interior_sheets) so they're valid solids."""
        return self._repaired[0]

    @property
    def print_matrix(self) -> np.ndarray:
        """4x4 rotation into print orientation (same convention as OpenSCAD rotate())."""
        rx, ry, rz = np.radians(self.print_rotation)
        return trimesh.transformations.euler_matrix(rx, ry, rz, "sxyz")

    @cached_property
    def print_mesh(self) -> trimesh.Trimesh:
        """The part as printed: print orientation, centred in x/y, resting on z=0."""
        m = (trimesh.load(self.print_raw, force="mesh") if self.print_source else self.mesh).copy()
        m.apply_transform(self.print_matrix)
        lo, hi = m.bounds
        m.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
        return m

    @property
    def link_source(self) -> Path:
        """The file a person edits for this part."""
        return self.print_source or self.source

    def jobs(self) -> list[tuple[Path, dict | list, Path]]:
        """(source file, -D defines or blend objects, output stl) renders this part needs."""
        out = [(self.source, self.blend_objects if self.blend_objects is not None else self.defines, self.stl)]
        if self.print_source:
            out.append((self.print_source, {}, self.print_raw))
        return out

    @cached_property
    def manifold(self) -> manifold3d.Manifold:
        return to_manifold(self.mesh, self.name)

    @cached_property
    def print_manifold(self) -> manifold3d.Manifold:
        return to_manifold(self.print_mesh, f"{self.name} (print)")


@dataclass
class Design:
    """A design folder plus the parts/vitamins to render from it.

    `parts` and `vitamins` map a part name to either a .scad path relative to `root`
    (the file renders the part on its own, in assembled position) or a `scad(...)` spec.
    """

    root: Path
    parts: dict[str, str | dict]
    vitamins: dict[str, str | dict] = field(default_factory=dict)
    defines: dict[str, float | str] = field(default_factory=dict)  # openscad -D overrides
    build_dir: Path | None = None
    printer: str = DEFAULT_PRINTER  # key into scadcheck.printers.PRINTERS
    plate_spacing: float = 5.0  # mm between parts in the bed layout
    # Print-in-place designs (e.g. hinged parts) print together exactly as assembled,
    # so the bed layout keeps their relative positions instead of packing them.
    print_in_place: bool = False

    def __post_init__(self):
        self.root = Path(self.root).resolve()
        self.build_dir = Path(self.build_dir or self.root / "build").resolve()
        self._parts: dict[str, Part] = {}
        for kind, table in (("part", self.parts), ("vitamin", self.vitamins)):
            for name, spec in table.items():
                spec = spec if isinstance(spec, dict) else scad(spec)
                sub = "" if kind == "part" else "vitamins"
                self._parts[name] = Part(
                    name=name,
                    source=self.root / (spec.get("scad") or spec["blend"]),
                    stl=self.build_dir / sub / f"{name}.stl",
                    kind=kind,
                    defines=spec.get("defines", {}),
                    blend_objects=spec.get("objects"),
                    print_source=self.root / spec["print"] if spec.get("print") else None,
                    print_raw=self.build_dir / "raw" / f"{name}.stl" if spec.get("print") else None,
                )
        self._rendered = False
        REGISTRY[self.root.name] = self

    @property
    def name(self) -> str:
        return self.root.name

    def __getitem__(self, name: str) -> Part:
        return self._parts[name]

    def __iter__(self):
        return iter(self._parts.values())

    def printed(self) -> list[Part]:
        return [p for p in self if p.kind == "part"]

    @property
    def printer_spec(self) -> Printer:
        return PRINTERS[self.printer]

    @cached_property
    def plate(self) -> "Plate":
        if self.print_in_place:
            return layout_in_place(self.printed(), self.printer_spec)
        return layout_plate(self.printed(), self.printer_spec, self.plate_spacing)

    def ready(self) -> "Design":
        """Render once (on first use) and return self; later calls are free."""
        if not self._rendered:
            self.render()
        return self

    def render(self, force: bool = False) -> "Design":
        """Render every part to STL, in parallel; skip outputs newer than their sources.

        A .scad output is stale when any .scad in the design is newer (includes can be
        anywhere); a .blend output when its .blend or the export script is newer.
        """
        scad_files = list(self.root.rglob("*.scad"))
        newest_scad = max((p.stat().st_mtime for p in scad_files), default=0)

        def stale(src: Path, out: Path) -> bool:
            if force or self.defines or not out.exists():
                return True
            deps = [src, BLENDER_EXPORT] if src.suffix == ".blend" else [newest_scad]
            newest = max(d if isinstance(d, float) else d.stat().st_mtime for d in deps)
            return out.stat().st_mtime <= newest

        scad_jobs, blend_jobs = [], defaultdict(dict)
        for part in self:
            for src, arg, out in part.jobs():
                if not stale(src, out):
                    continue
                if src.suffix == ".blend":
                    blend_jobs[src][part.name] = (arg, out)
                else:
                    scad_jobs.append((src, {**arg, **self.defines}, out))
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            futures = [pool.submit(_openscad, *job) for job in scad_jobs]
            futures += [pool.submit(_blender, src, parts) for src, parts in blend_jobs.items()]
            for future in futures:
                future.result()
        self._rendered = True
        return self

    def constants(self, filename: str = "constants.scad") -> dict[str, float]:
        return read_constants(self.root / filename)


@dataclass
class Plate:
    """Printed parts arranged on one bed. The bed is centred on the origin, top at z=0."""

    printer: Printer
    transforms: dict[str, np.ndarray]  # part name -> 4x4 placing its print_mesh on the bed
    size: tuple[float, float, float]  # extent of the arrangement (x, y, z), mm

    @property
    def fits(self) -> bool:
        return all(s <= v for s, v in zip(self.size, self.printer.volume))


def layout_in_place(parts: list[Part], printer: Printer) -> Plate:
    """Keep the parts as assembled: centre the whole group on the bed, lowest point on z=0."""
    if any(p.print_source or any(p.print_rotation) for p in parts):
        raise ValueError("print_in_place parts print as assembled: no print_source or print_rotation")
    lo = np.min([p.mesh.bounds[0] for p in parts], axis=0)
    hi = np.max([p.mesh.bounds[1] for p in parts], axis=0)
    to_bed = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    transforms = {}
    for p in parts:
        # print_mesh is the assembled mesh shifted by -(own centre x/y, own min z); undo that
        plo, phi = p.mesh.bounds
        own = np.array([-(plo[0] + phi[0]) / 2, -(plo[1] + phi[1]) / 2, -plo[2]])
        move = np.eye(4)
        move[:3, 3] = to_bed - own
        transforms[p.name] = move
    size = hi - lo
    return Plate(printer, transforms, (float(size[0]), float(size[1]), float(size[2])))


def layout_plate(parts: list[Part], printer: Printer, spacing: float) -> Plate:
    """Shelf-pack parts in print orientation: rows left to right, tallest-in-Y first,
    then centre the whole arrangement on the bed."""
    width = printer.volume[0]
    items = sorted(parts, key=lambda p: -p.print_mesh.extents[1])
    x = y = row_depth = 0.0
    spots = []
    for p in items:
        ex, ey, _ = p.print_mesh.extents
        if x > 0 and x + ex > width:
            x, y, row_depth = 0.0, y + row_depth + spacing, 0.0
        spots.append((p, x, y))
        x += ex + spacing
        row_depth = max(row_depth, ey)

    used_x = max((sx + p.print_mesh.extents[0] for p, sx, _ in spots), default=0.0)
    used_y = max((sy + p.print_mesh.extents[1] for p, _, sy in spots), default=0.0)
    used_z = max((p.print_mesh.extents[2] for p in parts), default=0.0)

    transforms = {}
    for p, sx, sy in spots:
        ex, ey, _ = p.print_mesh.extents  # print_mesh is centred in x/y on z=0
        move = np.eye(4)
        move[:3, 3] = [sx + ex / 2 - used_x / 2, sy + ey / 2 - used_y / 2, 0]
        transforms[p.name] = move
    return Plate(printer, transforms, (float(used_x), float(used_y), float(used_z)))


_ASSIGN = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*([^;]+);", re.M)


def read_constants(path: Path) -> dict[str, float]:
    """Read simple numeric `name = expr;` assignments from a .scad file.

    Expressions may use + - * / and earlier names; anything else is skipped.
    """
    text = re.sub(r"//.*", "", Path(path).read_text(encoding="utf-8"))
    values: dict[str, float] = {}
    for name, expr in _ASSIGN.findall(text):
        if not re.fullmatch(r"[\w\s.+\-*/()]+", expr):
            continue
        try:
            values[name] = float(eval(expr, {"__builtins__": {}}, dict(values)))
        except Exception:
            pass
    return values
