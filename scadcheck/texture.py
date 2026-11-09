"""Surface textures cut into a part's outer faces after rendering (OpenSCAD's own booleans are far
too slow for fine textures; manifold3d does a face in well under a second).

    part.texture = {"kind": "wood_grain", "faces": ["-x", "+x", "-y", "+y"], "depth": 0.4}

Faces are the part's bounding-box sides (in its assembled position). The texture is only ever cut
inward, so the part keeps its outside size and every fit check still applies.
"""

from __future__ import annotations

import numpy as np
import trimesh

import manifold3d


def to_manifold(mesh: trimesh.Trimesh, name: str) -> manifold3d.Manifold:
    solid = manifold3d.Manifold(manifold3d.Mesh(
        vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.asarray(mesh.faces, dtype=np.uint32)))
    if solid.status() != manifold3d.Error.NoError:
        raise ValueError(f"{name}: mesh is not a valid manifold ({solid.status()})")
    return solid

DEFAULTS = {"depth": 0.4, "spacing": 2.8, "mm_per_px": 0.5, "seed": 1,
            # smooth band at the bottom: grooves in the first layers split them apart (the
            # anti-warp V-groove print failed that way) and weaken the brim
            "keep_bottom": 1.0}


def _upsample(grid: np.ndarray, h: int, w: int) -> np.ndarray:
    """Smooth (cosine-weighted bilinear) upsampling of a small random grid to h x w."""
    gz, gx = grid.shape
    zs, xs = np.linspace(0, gz - 1, h), np.linspace(0, gx - 1, w)
    z0, x0 = np.minimum(zs.astype(int), gz - 2), np.minimum(xs.astype(int), gx - 2)
    tz, tx = zs - z0, xs - x0
    tz, tx = (1 - np.cos(np.pi * tz)) / 2, (1 - np.cos(np.pi * tx)) / 2
    a = grid[np.ix_(z0, x0)]
    b = grid[np.ix_(z0, x0 + 1)]
    c = grid[np.ix_(z0 + 1, x0)]
    d = grid[np.ix_(z0 + 1, x0 + 1)]
    top = a + (b - a) * tx[None, :]
    bot = c + (d - c) * tx[None, :]
    return top + (bot - top) * tz[:, None]


def wood_grain(w_mm: float, h_mm: float, mm_per_px: float, spacing: float, seed: int) -> np.ndarray:
    """Height map (rows = height, cols = along the face), 0 = surface, 1 = full groove depth.
    Long, gently wavy grain lines running along the face, with drifting spacing and broken strength."""
    rng = np.random.default_rng(seed)
    w, h = max(2, int(round(w_mm / mm_per_px)) + 1), max(2, int(round(h_mm / mm_per_px)) + 1)
    z = np.linspace(0, h_mm, h)[:, None] * np.ones((1, w))

    def noise(scale_x, scale_z, octaves):
        total, amp = np.zeros((h, w)), 1.0
        for o in range(octaves):
            gx = max(2, int(w_mm / scale_x * 2 ** o) + 2)
            gz = max(2, int(h_mm / scale_z * 2 ** o) + 2)
            total += amp * _upsample(rng.standard_normal((gz, gx)), h, w)
            amp *= 0.5
        return total

    warp = 1.1 * noise(45, 30, 2) + 0.25 * noise(15, 10, 1)
    phase = (z + warp) / spacing + 0.35 * noise(70, 45, 1)
    dist = np.abs(phase - np.round(phase)) * spacing
    width = 0.5 * (1 + 0.3 * noise(25, 12, 2))
    groove = np.clip(1 - dist / np.maximum(width, 0.15), 0, 1) ** 1.5
    breakup = np.clip(0.75 + 0.5 * noise(15, 6, 2), 0, 1)
    return np.clip(groove * breakup, 0, 1)


def _height_slab(u: np.ndarray, v: np.ndarray, depth: np.ndarray, frame) -> trimesh.Trimesh:
    """Closed solid between the textured surface (depth into the part) and a flat face 1 mm outside.
    frame(u, v, n) maps face coordinates (along, up, inward depth) to xyz arrays."""
    h, w = depth.shape
    U, V = np.meshgrid(u, v)
    top = np.stack(frame(U, V, depth), -1).reshape(-1, 3)
    bot = np.stack(frame(U, V, np.full_like(depth, -1.0)), -1).reshape(-1, 3)
    idx = np.arange(h * w).reshape(h, w)
    o = h * w
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, :-1], idx[1:, 1:]
    faces = [np.stack([a, c, b], -1), np.stack([b, c, d], -1),
             np.stack([a + o, b + o, c + o], -1), np.stack([b + o, d + o, c + o], -1)]

    def side(ids):
        p, q = ids[:-1], ids[1:]
        return np.concatenate([np.stack([p, q, p + o], -1), np.stack([q, q + o, p + o], -1)])

    faces = [f.reshape(-1, 3) for f in faces] + [side(idx[0, :]), side(idx[:, -1]), side(idx[-1, ::-1]), side(idx[::-1, 0])]
    slab = trimesh.Trimesh(np.vstack([top, bot]), np.concatenate(faces), process=True)
    trimesh.repair.fix_normals(slab)
    return slab


def _face_frame(face: str, lo: np.ndarray, hi: np.ndarray):
    """(u range, frame) for a bounding-box side: u runs along the face horizontally, v = z."""
    axis = "xy".index(face[1])
    other = 1 - axis
    sign = 1 if face[0] == "-" else -1           # inward direction along `axis`
    plane = lo[axis] if face[0] == "-" else hi[axis]

    def frame(u, v, n):
        xyz = [None, None, v]
        xyz[axis] = plane + sign * n
        xyz[other] = u
        return xyz

    return (lo[other], hi[other]), frame


def apply_texture(mesh: trimesh.Trimesh, spec: dict) -> trimesh.Trimesh:
    if spec.get("kind") != "wood_grain":
        raise ValueError(f"unknown texture: {spec.get('kind')}")
    opts = {**DEFAULTS, **spec}
    lo, hi = mesh.bounds
    result = to_manifold(mesh, "textured part")
    for i, face in enumerate(opts["faces"]):
        (u0, u1), frame = _face_frame(face, lo, hi)
        grain = wood_grain(u1 - u0, hi[2] - lo[2], opts["mm_per_px"], opts["spacing"], opts["seed"] + i)
        u = np.linspace(u0, u1, grain.shape[1])
        v = np.linspace(lo[2], hi[2], grain.shape[0])
        grain = grain * np.clip((v - lo[2] - opts["keep_bottom"]) / 0.5, 0, 1)[:, None]   # fade in above it
        slab = _height_slab(u, v, opts["depth"] * grain, frame)
        result = result - to_manifold(slab, f"{face} grain")
    out = result.to_mesh()
    return trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3], np.asarray(out.tri_verts), process=True)
