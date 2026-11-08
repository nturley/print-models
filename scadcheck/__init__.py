"""Test 3D-print designs (OpenSCAD or Blender): render parts to STL, then check geometry with pytest."""

from .checks import standard_checks
from .design import Design, Part, blend, read_constants, scad
from .geom import Distance, bounds, intersection_volume, is_watertight, min_distance, overhang_area, size

__all__ = [
    "Design",
    "Distance",
    "Part",
    "blend",
    "bounds",
    "intersection_volume",
    "is_watertight",
    "min_distance",
    "overhang_area",
    "read_constants",
    "scad",
    "size",
    "standard_checks",
]
