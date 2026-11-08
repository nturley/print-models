"""Design rules for the ball bearing (see ../README.md, "Parameters")."""

from pathlib import Path

import pytest

from scadcheck import Design, bounds, min_distance, standard_checks

# Requirements not stated in constants.scad.
CAGE_CLEARANCE = (0.2, 0.5)  # mm between cage and each race: must spin freely but not wobble
BALL_PLAY_MAX = 0.15  # mm between a ball and its groove: more than this and the bearing rattles
ALIGN_TOL = 0.01  # mm

BEARING = Design(
    root=Path(__file__).parents[1],
    parts={
        "outer-race": "parts/outer-race.scad",
        "inner-race": "parts/inner-race.scad",
        "cage": "parts/cage.scad",
    },
    vitamins={"steel-balls": "vitamins/steel-balls.scad"},
)
# Cage prints upside down so its solid top ring is on the bed (see parts/cage.scad).
BEARING["cage"].print_rotation = (180, 0, 0)
for _name, _color in {"outer-race": "#4f7cac", "inner-race": "#5fa38a", "cage": "#e0a040", "steel-balls": "#c0c4cc"}.items():
    BEARING[_name].color = _color

# watertight, fits printer, plate, rests flat, no interference (balls included)
globals().update(standard_checks(BEARING))


@pytest.fixture(scope="module")
def bearing() -> Design:
    return BEARING.ready()


@pytest.fixture(scope="module")
def c(bearing):
    return bearing.constants()


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
