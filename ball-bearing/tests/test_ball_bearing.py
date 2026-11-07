"""Design rules for the ball bearing (see ../README.md, "Parameters")."""

from itertools import combinations
from pathlib import Path

import pytest

from scadcheck import Design, bounds, intersection_volume, is_watertight, min_distance, size

# Requirements not stated in constants.scad.
CAGE_CLEARANCE = (0.2, 0.5)  # mm between cage and each race: must spin freely but not wobble
BALL_PLAY_MAX = 0.15  # mm between a ball and its groove: more than this and the bearing rattles
ALIGN_TOL = 0.01  # mm


@pytest.fixture(scope="module")
def bearing() -> Design:
    design = Design(
        root=Path(__file__).parents[1],
        parts={
            "outer-race": "parts/outer-race.scad",
            "inner-race": "parts/inner-race.scad",
            "cage": "parts/cage.scad",
        },
        vitamins={"steel-balls": "vitamins/steel-balls.scad"},
    )
    # Cage prints upside down so its solid top ring is on the bed (see parts/cage.scad).
    design["cage"].print_rotation = (180, 0, 0)
    design["outer-race"].color = "#4f7cac"
    design["inner-race"].color = "#5fa38a"
    design["cage"].color = "#e0a040"
    design["steel-balls"].color = "#c0c4cc"
    return design.render()


@pytest.fixture(scope="module")
def c(bearing):
    return bearing.constants()


ALL_PARTS = ["outer-race", "inner-race", "cage", "steel-balls"]


@pytest.mark.parametrize("name", ALL_PARTS)
def test_watertight(bearing, name):
    """Every mesh is a closed, consistently wound solid."""
    assert is_watertight(bearing[name])


@pytest.mark.parametrize("name", ["outer-race", "inner-race", "cage"])
def test_fits_printer(bearing, measure, name):
    """Each printed part, in print orientation, fits the printer's build volume."""
    dims = bearing[name].print_mesh.extents
    measure(f"{name} max dimension", max(dims), max=min(bearing.printer_spec.volume))
    assert all(d <= v for d, v in zip(dims, bearing.printer_spec.volume))


def test_plate_fits(bearing, measure):
    """All printed parts fit on one plate together."""
    plate = bearing.plate
    measure("plate width used", plate.size[0], max=plate.printer.volume[0])
    measure("plate depth used", plate.size[1], max=plate.printer.volume[1])
    assert plate.fits


@pytest.mark.parametrize("name", ["outer-race", "inner-race", "cage"])
def test_rests_flat_on_bed(bearing, measure, name):
    """In print orientation, each part has a real footprint on the bed (not a point or edge)."""
    m = bearing[name].print_mesh
    on_bed = m.area_faces[(m.face_normals[:, 2] < -0.999) & (m.triangles[:, :, 2].max(axis=1) < 1e-3)].sum()
    measure(f"{name} bed contact area", on_bed, min=1.0, units="mm²")
    assert on_bed >= 1.0


@pytest.mark.parametrize("a,b", list(combinations(ALL_PARTS, 2)))
def test_no_interference(bearing, measure, a, b):
    """No two parts (balls included) occupy the same space."""
    vol = measure(f"{a} ∩ {b}", intersection_volume(bearing[a], bearing[b]), max=0.001, units="mm³")
    assert vol <= 0.001


@pytest.mark.parametrize("race", ["outer-race", "inner-race"])
def test_cage_race_clearance(bearing, measure, race):
    """The cage clears each race enough to spin, but not so much that it wobbles."""
    lo, hi = CAGE_CLEARANCE
    d = measure(f"cage ↔ {race}", min_distance(bearing["cage"], bearing[race]), min=lo, max=hi)
    assert lo <= d.distance <= hi


@pytest.mark.parametrize("race", ["outer-race", "inner-race"])
def test_ball_groove_fit(bearing, measure, race):
    """Balls run free in each groove without rattling."""
    d = measure(f"balls ↔ {race}", min_distance(bearing["steel-balls"], bearing[race]), min=0, max=BALL_PLAY_MAX)
    assert 0 < d.distance <= BALL_PLAY_MAX


def test_balls_clear_cage(bearing, measure):
    """Balls don't rub on the cage pockets."""
    d = measure("balls ↔ cage", min_distance(bearing["steel-balls"], bearing["cage"]), min=0)
    assert d.distance > 0


@pytest.mark.parametrize("race", ["outer-race", "inner-race"])
def test_race_bottom_aligned_with_balls(bearing, measure, c, race):
    """Race bottoms line up with the ball bottoms, so balls can be pushed into the track."""
    # Compare with the nominal ball, not the vitamin mesh: OpenSCAD spheres have no
    # vertex at the poles, so the mesh is ~0.012mm short top and bottom at $fn=32.
    offset = bounds(bearing[race])[0, 2] - (-c["ball_r"])
    measure(f"{race} bottom − ball bottom", offset, min=-ALIGN_TOL, max=ALIGN_TOL)
    assert abs(offset) <= ALIGN_TOL


def test_cage_top_above_balls(bearing, measure, c):
    """The cage top clears the ball tops, so the cage is one continuous piece."""
    gap = bounds(bearing["cage"])[1, 2] - c["ball_r"]  # nominal ball top, see above
    measure("cage top − ball top", gap, min=c["cage_top_extension"] - ALIGN_TOL)
    assert gap >= c["cage_top_extension"] - ALIGN_TOL


@pytest.mark.parametrize("race", ["outer-race", "inner-race"])
def test_race_top_above_cage(bearing, measure, c, race):
    """Race tops stand above the cage top."""
    gap = bounds(bearing[race])[1, 2] - bounds(bearing["cage"])[1, 2]
    measure(f"{race} top − cage top", gap, min=c["race_top_extension"] - ALIGN_TOL)
    assert gap >= c["race_top_extension"] - ALIGN_TOL
