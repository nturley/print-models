"""Design rules for the Root insert (see ../README.md).

Marquise, Eyrie and Alliance boxes are two printed pieces pinned together: the base (side-loading
card slot) and the top (warrior bin + token column). The Vagabond box is one piece: no warriors, so
its cards lie in a top-loaded pocket and its pawn goes in the token column.
"""

import re
import subprocess
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from scadcheck import Design, bounds, min_distance, overhang_area, standard_checks
from scadcheck.design import openscad_exe, scad

FACTIONS = ["marquise", "eyrie", "alliance", "vagabond"]
TWO_PIECE = ["marquise", "eyrie", "alliance"]
PRINTED = [f"{f}-{p}" for f in TWO_PIECE for p in ("base", "top")] + ["vagabond-box"]
COLORS = {"marquise": "#d9782d", "eyrie": "#3d6fb4", "alliance": "#4e9a48", "vagabond": "#8b8f88"}
WARRIORS = {"marquise": (25, 16.5, 22), "eyrie": (20, 16.5, 22), "alliance": (10, 18.7, 18.9)}
PILE_LOOSENESS = 0.55   # a loose pile fills ~55% of its bin (bounding boxes)
MAX_PILE_DEPTH = 4      # warriors: bins must hold the pile no deeper than this
TOL = 0.01

ROOT = Design(
    root=Path(__file__).parents[1],
    parts={
        **{f"{f}-base": scad("parts/faction-base.scad", faction=f) for f in TWO_PIECE},
        **{f"{f}-top": scad("parts/faction-top.scad", faction=f) for f in TWO_PIECE},
        "vagabond-box": scad("parts/faction-top.scad", faction="vagabond"),   # one piece
        "shared-tray": "parts/shared-tray.scad",
    },
    vitamins={
        **{f"{f}-cards": scad("vitamins/faction-contents.scad", faction=f, show="cards") for f in FACTIONS},
        **{f"{f}-tokens": scad("vitamins/faction-contents.scad", faction=f, show="tokens") for f in FACTIONS},
        "shared-deck-cards": scad("vitamins/shared-contents.scad", show="deck"),
        "shared-token-stacks": scad("vitamins/shared-contents.scad", show="tokens"),
    },
)
for _f in FACTIONS:
    for _p in (f"{_f}-base", f"{_f}-top", f"{_f}-box"):
        if _p in ROOT.parts:
            ROOT[_p].color = COLORS[_f]
    ROOT[f"{_f}-cards"].color = ROOT[f"{_f}-tokens"].color = "#efe6d2"
ROOT["shared-tray"].color = "#b9955a"
# wood grain on the four outer walls (horizontal lines, cut 0.4 mm in); rims, pockets and icons stay smooth
ROOT["shared-tray"].texture = {"kind": "wood_grain", "faces": ["-x", "+x", "-y", "+y"], "depth": 0.4}
ROOT["shared-deck-cards"].color = ROOT["shared-token-stacks"].color = "#efe6d2"

# One print bed per filament colour: each faction's pieces print together, and the shared tray alone.
PLATES = {"marquise": "Marquise", "eyrie": "Eyrie", "alliance": "Alliance", "vagabond": "Vagabond"}
for _p in ROOT.printed():
    _f = _p.name.split("-")[0]
    _p.plate = PLATES.get(_f, "Shared")

# watertight, fits printer, every bed fits, rests flat, no interference (contents included;
# base and top only touch)
globals().update(standard_checks(ROOT))


@pytest.fixture(scope="module")
def root() -> Design:
    return ROOT.ready()


@pytest.fixture(scope="module")
def c(root):
    return root.constants()


def box_parts(f):
    return [f"{f}-base", f"{f}-top"] if f in TWO_PIECE else [f"{f}-box"]


def _box_bounds(root, f):
    bs = [bounds(root[p]) for p in box_parts(f)]
    return np.min([b[0] for b in bs], axis=0), np.max([b[1] for b in bs], axis=0)


@pytest.mark.parametrize("f", FACTIONS)
def test_box_size(root, measure, c, f):
    """Every faction box (assembled) is the same size: 91 x 106.5 x 46."""
    lo, hi = _box_bounds(root, f)
    for i, (axis, want) in enumerate(zip("xyz", (c["faction_box_w"], c["faction_box_d"], c["faction_box_h"]))):
        measure(f"{f} {axis} size", hi[i] - lo[i], min=want - TOL, max=want + TOL)
        assert abs(hi[i] - lo[i] - want) <= TOL


@pytest.mark.parametrize("f", TWO_PIECE)
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


@pytest.mark.parametrize("f", TWO_PIECE)
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


@pytest.mark.parametrize("f", TWO_PIECE)
def test_slot_headroom(root, measure, c, f):
    """The top's floor (the slot ceiling) clears the cards by the slot headroom."""
    d = measure(f"{f} slot ceiling ↔ cards", min_distance(root[f"{f}-top"], root[f"{f}-cards"]),
                min=c["slot_headroom"] - TOL, max=c["slot_headroom"] + TOL)
    assert abs(d.distance - c["slot_headroom"]) <= TOL


@pytest.mark.parametrize("part", PRINTED)
def test_printable_without_supports(root, measure, c, part):
    """Printed upright, nothing bridges: every hollow has a 45° peaked roof, so the only flat
    downward faces are the ~5 mm ceilings of the pin holes."""
    f = part.split("-")[0]
    m = root[part].mesh
    flat_down = (m.face_normals[:, 2] < -0.99) & (m.triangles[:, :, 2].max(axis=1) > m.bounds[0, 2] + TOL)
    origin = _box_bounds(root, f)[0]
    inset = c["wall"] + c["pin_inset"]
    pins = [origin[:2] + [x, y] for x in (inset, c["faction_box_w"] - inset)
            for y in (inset, c["faction_box_d"] - inset)]
    hole_r = (c["pin_d"] + c["pin_fit"]) / 2 + c["pin_hole_chamfer"]
    in_hole = np.min([np.linalg.norm(m.triangles_center[:, :2] - p, axis=1) for p in pins], axis=0) <= hole_r + TOL
    area = measure(f"{part} flat ceilings (not pin holes)", float(m.area_faces[flat_down & ~in_hole].sum()),
                   max=TOL, units="mm²")
    assert area <= TOL, "a flat ceiling (bridge) other than a pin hole top"


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


@pytest.mark.parametrize("f", TWO_PIECE)
def test_warrior_bin_holds_pile(measure, c, f):
    """The warrior bin holds the loose pile no deeper than MAX_PILE_DEPTH warriors."""
    n, w, l = WARRIORS[f]
    area = c["bin_w"] * (c["faction_box_d"] - 2 * c["wall"])
    pile = n * w * l * c["warrior_t"] / PILE_LOOSENESS / area
    base_h = c["floor_t"] + c[f"{f}_cards_h"] + c["slot_headroom"]
    bin_floor = base_h + c["pin_h"] + c["pin_hole_extra"] + c["floor_t"]   # raised above the pin holes
    limit = min(c["faction_box_h"] - bin_floor, MAX_PILE_DEPTH * c["warrior_t"])
    measure(f"{f} warrior pile depth", pile, max=limit)
    assert pile <= limit


def test_vagabond_cards_on_top(root, measure, c):
    """The Vagabond's cards lie in the top-loaded pocket, deck_headroom below the rim (room to thicken)."""
    gap = _box_bounds(root, "vagabond")[1][2] - bounds(root["vagabond-cards"])[1, 2]
    measure("vagabond rim − top of cards", gap, min=c["deck_headroom"] - TOL, max=c["deck_headroom"] + TOL)
    assert abs(gap - c["deck_headroom"]) <= TOL


def test_vagabond_one_piece(root, measure, c):
    """The Vagabond box is one part sitting on the box floor (no base, no pins)."""
    lo, hi = bounds(root["vagabond-box"])
    measure("vagabond box bottom", lo[2], min=-TOL, max=TOL)
    assert abs(lo[2]) <= TOL and "vagabond-base" not in ROOT.parts


# ---- Shared tray (right-hand column) ----

SHARED_CONTENTS = ["shared-deck-cards", "shared-token-stacks"]


def test_shared_tray_size(root, measure, c):
    """The shared tray fills the right-hand column: 94 x 213 x 46."""
    size = np.subtract(*bounds(root["shared-tray"])[::-1])
    for i, (axis, want) in enumerate(zip("xyz", (c["shared_w"], c["shared_tray_d"], c["faction_box_h"]))):
        measure(f"shared tray {axis} size", size[i], min=want - TOL, max=want + TOL)
        assert abs(size[i] - want) <= TOL


def test_whole_insert_fills_envelope(root, measure, c):
    """Faction boxes + shared tray exactly fill the 276 x 213 x 46 insert space."""
    lo = np.min([bounds(root[n])[0] for n in ROOT.parts], axis=0)
    hi = np.max([bounds(root[n])[1] for n in ROOT.parts], axis=0)
    for i, (axis, want) in enumerate(zip("xyz", (c["insert_w"], c["insert_d"], c["insert_h"]))):
        measure(f"insert {axis}", hi[i] - lo[i], min=want - TOL, max=want + TOL)
        assert abs(hi[i] - lo[i] - want) <= TOL and abs(lo[i]) <= TOL


@pytest.mark.parametrize("contents", SHARED_CONTENTS)
def test_shared_contents_below_rim(root, measure, c, contents):
    """The deck and every stack end below the rim by their headroom (the deck gets extra: cards
    thicken with age), so the board stack caps them."""
    want = c["deck_headroom"] if contents == "shared-deck-cards" else c["token_headroom"]
    gap = bounds(root["shared-tray"])[1, 2] - bounds(root[contents])[1, 2]
    measure(f"{contents}: rim − top", gap, min=want - TOL, max=want + TOL)
    assert abs(gap - want) <= TOL


def test_deck_centred(root, measure, c):
    """The shared deck sits in the middle of the tray's back half."""
    t, d = bounds(root["shared-tray"]), bounds(root["shared-deck-cards"])
    want = np.array([t[0, 0] + c["shared_w"] / 2, t[0, 1] + c["shared_d"] * 1.5])
    off = (d[0, :2] + d[1, :2]) / 2 - want
    measure("deck off centre", float(np.abs(off).max()), max=TOL)
    assert np.abs(off).max() <= TOL


@pytest.mark.parametrize("contents", SHARED_CONTENTS)
def test_shared_tray_clears_contents(root, measure, contents):
    """Cards, stacks and dice don't touch the pocket walls (they rest only on floors)."""
    d = measure(f"shared tray ↔ {contents}", min_distance(root["shared-tray"], root[contents]), min=0)
    assert d.distance >= 0


def test_shared_tray_no_bridges(root, measure):
    """Printed upright, nothing bridges: the hollows have 45° roofs, so no flat downward face."""
    m = root["shared-tray"].mesh
    flat_down = (m.face_normals[:, 2] < -0.99) & (m.triangles[:, :, 2].max(axis=1) > m.bounds[0, 2] + TOL)
    area = measure("shared tray flat ceilings", float(m.area_faces[flat_down].sum()), max=TOL, units="mm²")
    assert area <= TOL


def test_icons_leave_floor(measure, c):
    """Pocket icons are debossed into the floors without getting close to the hollows underneath."""
    left = measure("floor left under an icon", c["pocket_floor_t"] - c["icon_depth"], min=0.5)
    assert left >= 0.5, "icons cut too deep into the pocket floors"


def _svg_icons():
    text = (Path(__file__).parents[1] / "lib" / "icons.scad").read_text(encoding="utf-8")
    return re.findall(r'"([a-z-]+)"', re.search(r"function svg_icons\(\) = \[(.*?)\];", text, re.S).group(1))


@pytest.mark.parametrize("name", _svg_icons())
def test_icon_cuts_cleanly(tmp_path, measure, name):
    """Each SVG icon actually cuts into a part: CGAL silently skips a broken (not closed) icon."""
    import trimesh
    lib = (Path(__file__).parents[1] / "lib" / "icons.scad").as_posix()
    src = tmp_path / "icon.scad"
    src.write_text(f'use <{lib}>\n'
                   f'difference() {{ translate([-10, -10, 0]) cube([20, 20, 2]); '
                   f'translate([0, 0, 1.4]) linear_extrude(1) icon("{name}", 13); }}\n', encoding="utf-8")
    out = tmp_path / "icon.stl"
    run = subprocess.run([openscad_exe(), "-o", str(out), str(src)], capture_output=True, text=True)
    assert "not closed" not in run.stderr, f"{name}: OpenSCAD rejected the icon mesh"
    removed = measure(f"{name} icon cut volume", 800 - trimesh.load(out).volume, min=5, units="mm³")
    assert removed >= 5, f"{name}: the icon didn't cut into the part"


def test_suit_bowl_holds_markers(measure, c):
    """The suit-marker bowl holds all 12 loose markers (bounding boxes at the usual pile looseness)."""
    half, dd = c["suit_bowl_l"] / 2, c["suit_bowl_depth"]
    r = (half * half + dd * dd) / (2 * dd)
    segment = r * r * np.arccos((r - dd) / r) - (r - dd) * np.sqrt(2 * r * dd - dd * dd)   # trough cross-section
    length = c["shared_w"] - 2 * c["wall"] - 2 * c["suit_bowl_margin"] - c["suit_bowl_l"] / 2   # rounded ends ~ lose half
    need = 12 * c["suit_w"] * c["suit_l"] * c["token_t"] / PILE_LOOSENESS
    have = measure("suit bowl volume", segment * length / 1000, min=need / 1000, units="cm³")
    assert have >= need / 1000, "the suit bowl is too small for 12 loose markers"


def test_deck_scoop_below_cards(root, measure, c):
    """The deck scoops dip below the card floor, so a finger gets under the bottom card."""
    measure("deck scoop drop below the card floor", c["deck_scoop_drop"], min=3)
    assert c["deck_scoop_drop"] >= 3
