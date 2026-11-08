"""Checks for the motor car (see ../README.md).

Parts are rendered twice: in place, via `motorCar.scad -D part="<name>"`, for fit
checks, and from parts/<name>.scad (what gets sliced) for the print checks.
"""

from pathlib import Path

import numpy as np
import pytest

from scadcheck import Design, min_distance, scad, standard_checks
from scadcheck.geom import Distance

PRINTED = ["frame", "gear1", "gear2", "driveShaft", "driveWheel", "freeWheel"]
VITAMINS = ["motor", "batteryAAHolder"]

MODULE = 0.5  # gear module, mm
# (driving part, its tooth count, driven part, its tooth count). The motor's own gear is 10T.
GEAR_PAIRS = [("motor", 10, "gear1", 24), ("gear2", 10, "driveShaft", 31)]
BACKLASH = (0.0, 0.15)  # mm of extra centre distance: >0 so teeth don't bind, small so they don't skip
# Gear teeth are drawn at an arbitrary rotation in the assembly, so meshing pairs are
# checked by centre distance (test_gear_mesh), not by overlap.
MESHING = {frozenset((a, b)) for a, _, b, _ in GEAR_PAIRS}
KEYED_TOLERANCE = 0.5  # mm³ allowed where a key sits in a slot (snug fit)
KEYED = {frozenset(("gear1", "gear2")), frozenset(("driveShaft", "driveWheel"))}
WHEELS = ["driveShaft", "driveWheel", "freeWheel"]  # driveShaft has a wheel on its end
MIN_GROUND_CLEARANCE = 3.0  # mm under the frame
MAX_TILT_DEG = 3.0

CAR = Design(
    root=Path(__file__).parents[1],
    parts={n: scad("motorCar.scad", part=n, print=f"parts/{n}.scad") for n in PRINTED},
    vitamins={n: scad("motorCar.scad", part=n) for n in VITAMINS},
)
for _name, _color in {
    "frame": "#4f7cac", "gear1": "#e0a040", "gear2": "#d9773a", "driveShaft": "#5fa38a",
    "driveWheel": "#7fb069", "freeWheel": "#a066b0", "motor": "#c0c4cc", "batteryAAHolder": "#8a8f98",
}.items():
    CAR[_name].color = _color

# watertight, print file matches assembly, fits printer, plate, rests flat, no interference
globals().update(standard_checks(
    CAR, skip_pairs=MESHING, pair_tolerance={pair: KEYED_TOLERANCE for pair in KEYED},
))


@pytest.fixture(scope="module")
def car() -> Design:
    return CAR.ready()


# ---------- fit in the car ----------

def _axis_xz(car, name) -> np.ndarray:
    """Gear axes run along y; the part's bounding box is centred on its axis in x/z."""
    lo, hi = car[name].mesh.bounds
    return np.array([(lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2])


@pytest.mark.parametrize("a,ta,b,tb", GEAR_PAIRS, ids=[f"{a}-{b}" for a, _, b, _ in GEAR_PAIRS])
def test_gear_mesh(car, measure, a, ta, b, tb):
    """Meshing gears sit at the ideal centre distance plus a little backlash."""
    ideal = MODULE * (ta + tb) / 2
    pa, pb = _axis_xz(car, a), _axis_xz(car, b)
    y = car[b].mesh.bounds[:, 1].mean()  # draw the line through the driven gear
    centre = Distance(float(np.linalg.norm(pa - pb)), [pa[0], y, pa[1]], [pb[0], y, pb[1]])
    measure(f"{a} ↔ {b} centre distance (ideal {ideal})", centre)
    extra = measure(f"{a} ↔ {b} backlash", centre.distance - ideal, min=BACKLASH[0], max=BACKLASH[1])
    assert BACKLASH[0] <= extra <= BACKLASH[1]


@pytest.mark.parametrize("name", ["gear1", "driveShaft", "driveWheel"])
def test_moving_parts_clear_frame(car, measure, name):
    """Parts that spin don't rub on the frame."""
    d = measure(f"{name} ↔ frame", min_distance(car[name], car["frame"]), min=0)
    assert d.distance > 0


def test_ground_clearance(car, measure):
    """The frame stays off the ground, with all wheels doing the touching."""
    lowest_wheel = min(car[w].mesh.bounds[0, 2] for w in WHEELS)
    clearance = measure("frame ground clearance", car["frame"].mesh.bounds[0, 2] - lowest_wheel,
                        min=MIN_GROUND_CLEARANCE)
    assert clearance >= MIN_GROUND_CLEARANCE


def test_sits_level(car, measure):
    """Front and rear wheels reach the ground at about the same height."""
    rear = np.mean([car[w].mesh.bounds[0, 2] for w in ["driveShaft", "driveWheel"]])
    front = car["freeWheel"].mesh.bounds[0, 2]
    wheelbase = abs(_axis_xz(car, "driveShaft")[0] - _axis_xz(car, "freeWheel")[0])
    tilt = measure("tilt front to back", np.degrees(np.arctan2(abs(rear - front), wheelbase)),
                   max=MAX_TILT_DEG, units="°")
    assert tilt <= MAX_TILT_DEG
