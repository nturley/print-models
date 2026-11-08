"""Checks for the wire spool rack (see ../README.md).

The legs are a vendor STL (vendor/Wire_Holder_Stackable_V1.stl) placed by
parts/holder_leg.scad; two crossDowels interlock in an X through the legs' square
holes; six spools hang on the dowels; the wire guide sits in a slot in both legs.
Each part is rendered in place via `spool-rack.scad -D part="<name>"` for fit checks,
and from its parts/ file for the print checks.
"""

from pathlib import Path

import numpy as np
import pytest

from scadcheck import Design, min_distance, read_constants, scad, standard_checks

ROOT = Path(__file__).parents[1]
PRINTED = {
    "leg-left": "parts/holder_leg.scad",
    "leg-right": "parts/holder_leg.scad",
    "dowel-a": "parts/crossDowel.scad",
    "dowel-b": "parts/crossDowel.scad",
    "wire_guide": "parts/wire_guide.scad",
}
LEGS, DOWELS = ["leg-left", "leg-right"], ["dowel-a", "dowel-b"]
# Files that each declare their own copy of the shared dimensions.
CONSTANT_FILES = ["spool-rack.scad", "parts/crossDowel.scad", "parts/wire_guide.scad", "vitamins/spool.scad"]
HOLE_ALIGN_TOL = 0.25  # mm between a wire-guide hole and the middle of its spool

RACK = Design(
    root=ROOT,
    parts={n: scad("spool-rack.scad", part=n, print=src) for n, src in PRINTED.items()},
    vitamins={"spools": scad("spool-rack.scad", part="spools")},
)
for _leg in LEGS:
    RACK[_leg].print_rotation = (0, 90, 0)  # holder_leg.scad stands it up; print it flat
for _name, _color in {"leg-left": "#4f7cac", "leg-right": "#4f7cac", "dowel-a": "#e0a040", "dowel-b": "#d9773a",
                      "wire_guide": "#5fa38a", "spools": "#c0c4cc"}.items():
    RACK[_name].color = _color

# watertight, print file matches assembly, fits printer, plate, rests flat, and no
# interference (the dowels interlock and sit in the legs' holes; the guide in its slot)
globals().update(standard_checks(RACK))


@pytest.fixture(scope="module")
def rack() -> Design:
    return RACK.ready()


def test_shared_dimensions_agree(measure):
    """Every file that repeats a shared dimension (spool size, gaps, post width...) uses the same value."""
    values = {f: read_constants(ROOT / f) for f in CONSTANT_FILES}
    names = {n for v in values.values() for n in v}
    mismatched = {
        n: {f: v[n] for f, v in values.items() if n in v}
        for n in sorted(names)
        if len({v[n] for v in values.values() if n in v}) > 1
    }
    shared = [n for n in names if sum(n in v for v in values.values()) > 1]
    measure("dimensions shared between files", len(shared), units="")
    measure("shared dimensions that disagree", len(mismatched), max=0, units="")
    assert not mismatched, mismatched


# ---------- fit in the rack ----------

@pytest.mark.parametrize("other", [*LEGS, *DOWELS, "wire_guide"])
def test_spools_turn_freely(rack, measure, other):
    """Spools don't touch the legs, dowels or wire guide, so they can turn."""
    d = measure(f"spools ↔ {other}", min_distance(rack["spools"], rack[other]), min=0)
    assert d.distance > 0


def _spool_centres(rack) -> list[float]:
    return sorted(float(np.mean(np.asarray(s.bounding_box())[[0, 3]])) for s in rack["spools"].manifold.decompose())


def _guide_hole_centres(rack) -> list[float]:
    """x of each wire hole, from a slice through the guide's floor (print_mesh keeps assembly x)."""
    polys = rack["wire_guide"].print_manifold.slice(1.0).to_polygons()
    holes = [np.asarray(p)[:, :2] for p in polys if np.ptp(np.asarray(p)[:, 0]) < 6]
    return sorted(float(h[:, 0].mean()) for h in holes)


def test_wire_holes_line_up_with_spools(rack, measure):
    """Each wire-guide hole sits over the middle of its spool, so wire feeds straight."""
    spools, holes = _spool_centres(rack), _guide_hole_centres(rack)
    assert len(holes) == len(spools), f"{len(holes)} holes for {len(spools)} spools"
    worst = measure("worst hole-to-spool offset", max(abs(h - s) for h, s in zip(holes, spools)),
                    max=HOLE_ALIGN_TOL)
    assert worst <= HOLE_ALIGN_TOL
