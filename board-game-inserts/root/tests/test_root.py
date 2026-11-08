"""Design rules for the Root faction boxes (see ../README.md).

Each faction box is two printed pieces glued together: the base (card slot) and the top
(warrior bin + token column).
"""

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from scadcheck import Design, bounds, min_distance, overhang_area, standard_checks
from scadcheck.design import scad

FACTIONS = ["marquise", "eyrie", "alliance", "vagabond"]
COLORS = {"marquise": "#d9782d", "eyrie": "#3d6fb4", "alliance": "#4e9a48", "vagabond": "#8b8f88"}
WARRIORS = {"marquise": (25, 16.5, 22), "eyrie": (20, 16.5, 22), "alliance": (10, 18.7, 18.9), "vagabond": (1, 16.5, 22)}
PILE_LOOSENESS = 0.55   # a loose pile fills ~55% of its bin (bounding boxes)
MAX_PILE_DEPTH = 4      # warriors: bins must hold the pile no deeper than this
TOL = 0.01

ROOT = Design(
    root=Path(__file__).parents[1],
    parts={
        **{f"{f}-base": scad("parts/faction-base.scad", faction=f) for f in FACTIONS},
        **{f"{f}-top": scad("parts/faction-top.scad", faction=f) for f in FACTIONS},
    },
    vitamins={
        **{f"{f}-cards": scad("vitamins/faction-contents.scad", faction=f, show="cards") for f in FACTIONS},
        **{f"{f}-tokens": scad("vitamins/faction-contents.scad", faction=f, show="tokens") for f in FACTIONS},
    },
)
for _f in FACTIONS:
    ROOT[f"{_f}-base"].color = ROOT[f"{_f}-top"].color = COLORS[_f]
    ROOT[f"{_f}-cards"].color = ROOT[f"{_f}-tokens"].color = "#efe6d2"

# watertight, fits printer, rests flat, no interference (contents included; base and top only touch).
# Not "plate fits": each faction prints in its own colour, so a print is one base + its top;
# all 8 pieces together don't fit one bed.
_checks = standard_checks(ROOT)
_checks.pop("test_plate_fits", None)
globals().update(_checks)


@pytest.fixture(scope="module")
def root() -> Design:
    return ROOT.ready()


@pytest.fixture(scope="module")
def c(root):
    return root.constants()


def _box_bounds(root, f):
    b, t = bounds(root[f"{f}-base"]), bounds(root[f"{f}-top"])
    return np.minimum(b[0], t[0]), np.maximum(b[1], t[1])


@pytest.mark.parametrize("f", FACTIONS)
def test_box_size(root, measure, c, f):
    """Every glued faction box is the same size: 91 x 106.5 x 46."""
    lo, hi = _box_bounds(root, f)
    for i, (axis, want) in enumerate(zip("xyz", (c["faction_box_w"], c["faction_box_d"], c["faction_box_h"]))):
        measure(f"{f} {axis} size", hi[i] - lo[i], min=want - TOL, max=want + TOL)
        assert abs(hi[i] - lo[i] - want) <= TOL


@pytest.mark.parametrize("f", FACTIONS)
def test_pieces_meet(root, measure, c, f):
    """The top sits flat on the base's top face, and the alignment pins stand pin_h above it
    (they sit in the top's holes: the no-interference check covers the fit)."""
    joint = c["floor_t"] + c[f"{f}_cards_h"] + c["slot_headroom"]   # base height
    gap = bounds(root[f"{f}-top"])[0, 2] - joint
    measure(f"{f} top underside − base top", gap, min=-TOL, max=TOL)
    assert abs(gap) <= TOL
    pins = bounds(root[f"{f}-base"])[1, 2] - joint
    measure(f"{f} pin height", pins, min=c["pin_h"] - TOL, max=c["pin_h"] + TOL)
    assert abs(pins - c["pin_h"]) <= TOL


@pytest.mark.parametrize("f", FACTIONS)
def test_pin_clearance(root, measure, c, f):
    """Each pin has pin_fit/2 of clearance all round in its hole (a light press fit once printed)."""
    # base and top touch along the joint, so measure from just the pins (the base above the joint)
    joint = c["floor_t"] + c[f"{f}_cards_h"] + c["slot_headroom"]
    base = root[f"{f}-base"].mesh
    pins = base.submesh([np.nonzero(base.triangles_center[:, 2] > joint + 0.05)[0]], append=True)
    want = c["pin_fit"] / 2
    d = measure(f"{f} pin ↔ hole", min_distance(SimpleNamespace(mesh=pins), root[f"{f}-top"]),
                min=want - 0.01, max=want + 0.01)
    assert abs(d.distance - want) <= 0.01


@pytest.mark.parametrize("f", FACTIONS)
def test_slot_headroom(root, measure, c, f):
    """The top's floor (the slot ceiling) clears the cards by the slot headroom."""
    d = measure(f"{f} slot ceiling ↔ cards", min_distance(root[f"{f}-top"], root[f"{f}-cards"]),
                min=c["slot_headroom"] - TOL, max=c["slot_headroom"] + TOL)
    assert abs(d.distance - c["slot_headroom"]) <= TOL


@pytest.mark.parametrize("piece", ["base", "top"])
@pytest.mark.parametrize("f", FACTIONS)
def test_printable_without_supports(root, measure, c, f, piece):
    """Printed upright, the only overhangs are the short ceilings over the token-pocket hollows:
    nothing hangs over the cards or the warrior bin, so no bridge is wider than the token column."""
    m = root[f"{f}-{piece}"].mesh
    steep = -m.face_normals[:, 2] > np.cos(np.radians(45))
    on_bed = m.triangles[:, :, 2].max(axis=1) < m.bounds[0, 2] + TOL
    tri = m.triangles[steep & ~on_bed]
    measure(f"{f}-{piece} overhang", float(m.area_faces[steep & ~on_bed].sum()), units="mm²")
    if len(tri):
        x0 = bounds(root[f"{f}-base"])[0, 0] + c["column_x"]
        xs = tri[:, :, 0] - x0
        span = xs.max() - xs.min()
        measure(f"{f}-{piece} widest overhang", span, max=c["column_w"] + TOL)
        assert xs.min() >= -TOL and xs.max() <= c["column_w"] + TOL


def test_boxes_inside_insert(root, measure, c):
    """All four boxes fit in the insert envelope, so the board stack lies flat on top."""
    lo = np.min([bounds(root[n])[0] for n in ROOT.parts], axis=0)
    hi = np.max([bounds(root[n])[1] for n in ROOT.parts], axis=0)
    measure("faction block height", hi[2] - lo[2], max=c["insert_h"] + TOL)
    assert (lo >= -TOL).all()
    assert (hi <= np.array([c["insert_w"], c["insert_d"], c["insert_h"]]) + TOL).all()


@pytest.mark.parametrize("f", FACTIONS)
def test_contents_below_rim(root, measure, c, f):
    """Token stacks end just below the rim: easy to reach, and the board stack still caps them."""
    gap = _box_bounds(root, f)[1][2] - bounds(root[f"{f}-tokens"])[1, 2]
    measure(f"{f} rim − top of contents", gap, min=c["token_headroom"] - TOL, max=c["token_headroom"] + TOL)
    assert abs(gap - c["token_headroom"]) <= TOL


@pytest.mark.parametrize("f", FACTIONS)
def test_warrior_bin_holds_pile(measure, c, f):
    """The warrior bin holds the loose pile no deeper than MAX_PILE_DEPTH warriors."""
    n, w, l = WARRIORS[f]
    area = c["bin_w"] * (c["faction_box_d"] - 2 * c["wall"])
    pile = n * w * l * c["warrior_t"] / PILE_LOOSENESS / area
    bin_floor = 2 * c["floor_t"] + c[f"{f}_cards_h"] + c["slot_headroom"]
    limit = min(c["faction_box_h"] - bin_floor, MAX_PILE_DEPTH * c["warrior_t"])
    measure(f"{f} warrior pile depth", pile, max=limit)
    assert pile <= limit
