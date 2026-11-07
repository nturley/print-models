"""Downloadable build outputs: print-oriented STLs, a zip of them, and a 3MF of the bed layout."""

from __future__ import annotations

import os
import re
import subprocess
import zipfile
from pathlib import Path
from xml.sax.saxutils import quoteattr

import numpy as np
import trimesh

from .design import Design


def write_3mf(path: Path, objects: list[tuple[str, trimesh.Trimesh]]) -> None:
    """Minimal 3MF: one named object per mesh, already positioned in bed coordinates (mm)."""
    model = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
        "<resources>",
    ]
    for i, (name, mesh) in enumerate(objects, start=1):
        model.append(f'<object id="{i}" name={quoteattr(name)} type="model"><mesh><vertices>')
        model.extend(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in mesh.vertices)
        model.append("</vertices><triangles>")
        model.extend(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.faces)
        model.append("</triangles></mesh></object>")
    model.append("</resources><build>")
    model.extend(f'<item objectid="{i}"/>' for i in range(1, len(objects) + 1))
    model.append("</build></model>")

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
            "</Types>",
        )
        z.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
            "</Relationships>",
        )
        z.writestr("3D/3dmodel.model", "\n".join(model))


def export_downloads(design: Design) -> list[dict]:
    """Write print-ready files into the build dir; return them as report entries."""
    out = design.build_dir
    plate = design.plate
    w, d, _ = plate.printer.volume
    downloads = []

    # 3MF of the whole plate, in slicer bed coordinates (origin at the front-left corner).
    to_bed = np.eye(4)
    to_bed[:3, 3] = [w / 2, d / 2, 0]
    placed = []
    for p in design.printed():
        m = p.mesh.copy()
        m.apply_transform(to_bed @ plate.transforms[p.name])
        placed.append((p.name, m))
    plate_file = out / f"{design.name}-plate.3mf"
    write_3mf(plate_file, placed)
    downloads.append({"label": f"Plate for {plate.printer.name} (.3mf)", "file": plate_file.name})

    # Individual STLs in print orientation, centred, resting on z=0.
    (out / "print").mkdir(parents=True, exist_ok=True)
    stls = []
    for p in design.printed():
        m = p.print_mesh.copy()
        m.apply_translation([-m.bounds[:, 0].mean(), -m.bounds[:, 1].mean(), 0])
        f = out / "print" / f"{p.name}.stl"
        m.export(f)
        stls.append(f)
    zip_file = out / f"{design.name}-stl.zip"
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as z:
        for f in stls:
            z.write(f, f"{design.name}/{f.name}")
    downloads.append({"label": "All parts, print orientation (.zip of STLs)", "file": zip_file.name})

    for d_ in downloads:
        d_["bytes"] = (out / d_["file"]).stat().st_size
    return downloads


def repo_info(path: Path) -> dict | None:
    """GitHub URL and commit for source links: from GitHub Actions env, else local git."""
    if os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_SHA"):
        server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        return {"url": f"{server}/{os.environ['GITHUB_REPOSITORY']}", "ref": os.environ["GITHUB_SHA"]}
    try:
        git = lambda *a: subprocess.run(["git", *a], cwd=path, capture_output=True, text=True, check=True).stdout.strip()
        remote, sha = git("remote", "get-url", "origin"), git("rev-parse", "HEAD")
    except (OSError, subprocess.CalledProcessError):
        return None
    m = re.match(r"(?:https://|git@)github\.com[/:](.+?)(?:\.git)?$", remote)
    return {"url": f"https://github.com/{m.group(1)}", "ref": sha} if m else None
