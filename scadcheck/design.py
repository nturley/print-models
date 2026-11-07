"""Render an OpenSCAD design's parts to STL and load them as meshes."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
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


@dataclass
class Part:
    name: str
    source: Path  # .scad file that renders this part in its assembled position
    stl: Path
    kind: str = "part"  # "part" (printed) or "vitamin" (off-the-shelf hardware)
    color: str | None = None
    defines: dict = field(default_factory=dict)  # -D overrides for `source`
    print_source: Path | None = None  # .scad that renders the printed geometry, if not `source`
    print_raw: Path | None = None  # where print_source renders to
    # How the part goes on the bed, as OpenSCAD rotate([x, y, z]) degrees, applied to
    # the print geometry (print_source if set, else the assembled part).
    print_rotation: tuple[float, float, float] = (0, 0, 0)

    @cached_property
    def mesh(self) -> trimesh.Trimesh:
        """The part in its assembled position."""
        return trimesh.load(self.stl, force="mesh")

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

    def jobs(self) -> list[tuple[Path, dict, Path]]:
        """(scad file, -D defines, output stl) renders this part needs."""
        out = [(self.source, self.defines, self.stl)]
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
                    source=self.root / spec["scad"],
                    stl=self.build_dir / sub / f"{name}.stl",
                    kind=kind,
                    defines=spec["defines"],
                    print_source=self.root / spec["print"] if spec.get("print") else None,
                    print_raw=self.build_dir / "raw" / f"{name}.stl" if spec.get("print") else None,
                )
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
        return layout_plate(self.printed(), self.printer_spec, self.plate_spacing)

    def render(self, force: bool = False) -> "Design":
        """Render every part to STL, in parallel; skip outputs newer than all .scad sources."""
        newest_src = max(p.stat().st_mtime for p in self.root.rglob("*.scad"))
        jobs = [
            (src, {**defines, **self.defines}, out)
            for part in self
            for src, defines, out in part.jobs()
            if force or self.defines or not out.exists() or out.stat().st_mtime <= newest_src
        ]
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            for future in [pool.submit(_openscad, *job) for job in jobs]:
                future.result()
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
