"""Geometric checks between parts.

All results come from tessellated meshes, so they are only as accurate as the
design's $fn. OpenSCAD puts polygon vertices *on* the true circle, so curved
holes come out slightly smaller and curved bosses slightly flatter than designed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import trimesh
from trimesh.collision import CollisionManager

from .design import Part


@dataclass
class Distance:
    distance: float
    point_a: list[float]  # closest point on A
    point_b: list[float]  # closest point on B

    def __float__(self):
        return self.distance


def min_distance(a: Part, b: Part) -> Distance:
    """Closest approach between the *surfaces* of two parts (0 if they touch or cross).

    Surface distance can't see a part sitting entirely inside another one, so pair
    this with `intersection_volume` when that's possible.
    """
    manager = CollisionManager()
    manager.add_object("a", a.mesh)
    dist, data = manager.min_distance_single(b.mesh, return_data=True)
    return Distance(
        distance=max(float(dist), 0.0),
        point_a=np.asarray(data.point("a")).round(4).tolist(),
        point_b=np.asarray(data.point("__external")).round(4).tolist(),
    )


def intersection_volume(a: Part, b: Part) -> float:
    """Volume (mm^3) shared by two solids; > 0 means they collide."""
    return float((a.manifold ^ b.manifold).volume())


def bounds(part: Part) -> np.ndarray:
    """[[xmin, ymin, zmin], [xmax, ymax, zmax]]"""
    return part.mesh.bounds


def size(part: Part) -> np.ndarray:
    return part.mesh.extents


def is_watertight(part: Part) -> bool:
    """The mesh exactly as exported is a closed, consistently wound solid."""
    m = part.raw_mesh
    return bool(m.is_watertight and m.is_winding_consistent)


def overhang_area(part: Part, max_angle_deg: float = 45.0, floor_tol: float = 0.01) -> float:
    """Downward-facing area (mm^2) steeper than `max_angle_deg` from vertical,
    excluding faces lying on the build plate (in the part's current orientation)."""
    m: trimesh.Trimesh = part.mesh
    down = -m.face_normals[:, 2]
    steep = down > np.cos(np.radians(max_angle_deg))
    on_floor = m.triangles[:, :, 2].max(axis=1) < m.bounds[0, 2] + floor_tol
    return float(m.area_faces[steep & ~on_floor].sum())
