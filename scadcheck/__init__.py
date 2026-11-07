"""Test OpenSCAD designs: render parts to STL, then check geometry with pytest."""

from .design import Design, Part, read_constants
from .geom import Distance, bounds, intersection_volume, is_watertight, min_distance, overhang_area, size

__all__ = [
    "Design",
    "Distance",
    "Part",
    "bounds",
    "intersection_volume",
    "is_watertight",
    "min_distance",
    "overhang_area",
    "read_constants",
    "size",
]
