"""Render an OpenSCAD design's parts to STL and load them as meshes."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
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


@dataclass
class Part:
    name: str
    source: Path  # .scad file that renders this part standalone
    stl: Path
    kind: str = "part"  # "part" (printed) or "vitamin" (off-the-shelf hardware)
    color: str | None = None
    # How the part goes on the bed, as OpenSCAD rotate([x, y, z]) degrees from its
    # assembly orientation. The bed layout then drops it onto z=0.
    print_rotation: tuple[float, float, float] = (0, 0, 0)

    @cached_property
    def mesh(self) -> trimesh.Trimesh:
        return trimesh.load(self.stl, force="mesh")

    @property
    def print_matrix(self) -> np.ndarray:
        """4x4 rotation into print orientation (same convention as OpenSCAD rotate())."""
        rx, ry, rz = np.radians(self.print_rotation)
        return trimesh.transformations.euler_matrix(rx, ry, rz, "sxyz")

    @cached_property
    def print_mesh(self) -> trimesh.Trimesh:
        """The part in print orientation, resting on z=0."""
        m = self.mesh.copy()
        m.apply_transform(self.print_matrix)
        m.apply_translation([0, 0, -m.bounds[0, 2]])
        return m

    @cached_property
    def manifold(self) -> manifold3d.Manifold:
        m = self.mesh
        solid = manifold3d.Manifold(
            manifold3d.Mesh(
                vert_properties=np.asarray(m.vertices, dtype=np.float32),
                tri_verts=np.asarray(m.faces, dtype=np.uint32),
            )
        )
        if solid.status() != manifold3d.Error.NoError:
            raise ValueError(f"{self.name}: mesh is not a valid manifold ({solid.status()})")
        return solid


@dataclass
class Design:
    """A design folder plus the parts/vitamins to render from it.

    `parts` and `vitamins` map a part name to a .scad path relative to `root`.
    Each .scad file must render the part on its own (call its module at the bottom).
    """

    root: Path
    parts: dict[str, str]
    vitamins: dict[str, str] = field(default_factory=dict)
    defines: dict[str, float | str] = field(default_factory=dict)  # openscad -D overrides
    build_dir: Path | None = None
    printer: str = DEFAULT_PRINTER  # key into scadcheck.printers.PRINTERS
    plate_spacing: float = 5.0  # mm between parts in the bed layout

    def __post_init__(self):
        self.root = Path(self.root).resolve()
        self.build_dir = Path(self.build_dir or self.root / "build").resolve()
        self._parts: dict[str, Part] = {}
        for kind, table in (("part", self.parts), ("vitamin", self.vitamins)):
            for name, src in table.items():
                sub = "" if kind == "part" else "vitamins"
                self._parts[name] = Part(
                    name=name,
                    source=self.root / src,
                    stl=self.build_dir / sub / f"{name}.stl",
                    kind=kind,
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
        """Render every part to STL; skip parts whose STL is newer than all .scad sources."""
        newest_src = max(p.stat().st_mtime for p in self.root.rglob("*.scad"))
        for part in self:
            if not force and not self.defines and part.stl.exists() and part.stl.stat().st_mtime > newest_src:
                continue
            part.stl.parent.mkdir(parents=True, exist_ok=True)
            cmd = [openscad_exe(), "-o", str(part.stl)]
            for k, v in self.defines.items():
                cmd += ["-D", f"{k}={v}"]
            cmd.append(str(part.source))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 or not part.stl.exists():
                raise RuntimeError(f"openscad failed for {part.source}:\n{result.stderr}")
        return self

    def constants(self, filename: str = "constants.scad") -> dict[str, float]:
        return read_constants(self.root / filename)


@dataclass
class Plate:
    """Printed parts arranged on one bed. The bed is centred on the origin, top at z=0."""

    printer: Printer
    transforms: dict[str, np.ndarray]  # part name -> 4x4, assembly coords -> bed coords
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
        lo =trimesh.transform_points(p.mesh.vertices, p.print_matrix).min(axis=0)
        move = np.eye(4)
        move[:3, 3] = [sx - used_x / 2 - lo[0], sy - used_y / 2 - lo[1], -lo[2]]
        transforms[p.name] = move @ p.print_matrix
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
