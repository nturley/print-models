"""Checks for the foldable paint tray (see ../README.md).

A Blender design: `Outer` is the middle panel and `Inner` (mirrored) is the two end
panels, joined by print-in-place hinges. Both are exported from paint-tray.blend with
their modifiers applied, exactly where they sit in the file, and print together as is.
"""

from pathlib import Path

import numpy as np
import pytest

from scadcheck import Design, blend, min_distance, standard_checks
from scadcheck.geom import Distance

# Print-in-place gap: wide enough not to fuse when printed, narrow enough not to flop.
HINGE_GAP = (0.3, 0.8)  # mm
PULL = 1.0  # mm: an end panel moved this far in any direction must hit the middle panel
# Hinge axes run along x at this height, at these y positions (Pin objects in the .blend
# sit at z=5; the Mirror modifier puts the second hinge at y=-100).
HINGE_Z = 5.0
HINGE_Y = {"front": -100.0, "back": 0.0}
FOLD = 180  # degrees each end panel must fold up over the middle panel

TRAY = Design(
    root=Path(__file__).parents[1],
    parts={"outer": blend("paint-tray.blend", "Outer"), "inner": blend("paint-tray.blend", "Inner")},
    print_in_place=True,
)
TRAY["outer"].color = "#4f7cac"
TRAY["inner"].color = "#e0a040"

# watertight (no internal walls from the Mirror modifier), plate, every panel on the
# first layer, and the panels don't overlap
globals().update(standard_checks(TRAY))


@pytest.fixture(scope="module")
def tray() -> Design:
    return TRAY.ready()


@pytest.fixture(scope="module")
def end_panels(tray) -> dict:
    """The two end panels (separate bodies of `inner`), keyed by which hinge holds them."""
    bodies = sorted(tray["inner"].manifold.decompose(), key=lambda c: np.asarray(c.bounding_box())[1])
    return dict(zip(["front", "back"], bodies))


# ---------- hinges ----------

def test_hinge_gap(tray, measure):
    """Hinge parts are far enough apart not to fuse when printed in place, close enough not to flop."""
    lo, hi = HINGE_GAP
    d = measure("outer ↔ inner gap", min_distance(tray["outer"], tray["inner"]), min=lo, max=hi)
    assert lo <= d.distance <= hi


DIRECTIONS = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0), "+z": (0, 0, 1), "-z": (0, 0, -1)}


@pytest.mark.parametrize("hinge", list(HINGE_Y))
@pytest.mark.parametrize("direction", list(DIRECTIONS))
def test_hinge_is_captive(tray, end_panels, measure, hinge, direction):
    """Pulling an end panel in any direction runs into the middle panel: it can't fall off."""
    moved = end_panels[hinge].translate(tuple(PULL * a for a in DIRECTIONS[direction]))
    hit = measure(f"{hinge} panel pulled {PULL}mm {direction}: overlap", (moved ^ tray["outer"].manifold).volume(),
                  min=0.001, units="mm³")
    assert hit > 0.001


@pytest.mark.parametrize("hinge", list(HINGE_Y))
def test_end_panel_folds_over(tray, end_panels, measure, hinge):
    """Each end panel swings up and over onto the middle panel without hitting anything."""
    y = HINGE_Y[hinge]
    sign = -1 if hinge == "front" else 1  # both fold up toward the middle
    panel, outer = end_panels[hinge], tray["outer"].manifold
    reached = 0
    for angle in range(5, FOLD + 1, 5):
        swung = panel.translate((0, -y, -HINGE_Z)).rotate((sign * angle, 0, 0)).translate((0, y, HINGE_Z))
        if (swung ^ outer).volume() > 0.001:
            break
        reached = angle
    lo, hi = tray["outer"].mesh.bounds
    axis = Distance(float(hi[0] - lo[0]), [float(lo[0]), y, HINGE_Z], [float(hi[0]), y, HINGE_Z])
    measure(f"{hinge} hinge axis", axis)
    measure(f"{hinge} panel folds freely to", reached, min=FOLD, units="°")
    assert reached >= FOLD
