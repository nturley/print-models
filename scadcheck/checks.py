"""Standard checks every design gets. In a design's test file:

    from scadcheck import Design, standard_checks

    BEARING = Design(root=..., parts=..., vitamins=...)      # cheap: nothing renders yet
    globals().update(standard_checks(BEARING))

    @pytest.fixture(scope="module")
    def bearing():
        return BEARING.ready()                               # renders once, on first use

That adds, each parametrized per part (or pair) so they show up individually:

    test_watertight              every part: the mesh as exported is a closed solid
    test_print_matches_assembly  parts with a separate print file: same volume as assembled
    test_fits_printer            printed parts: fit the build volume (packed designs only)
    test_plate_fits              all printed parts fit on one plate together
    test_rests_flat_on_bed       printed parts have a real footprint on the bed
    test_no_interference         every pair of parts: no shared volume

Design-specific checks (clearances, gear mesh, hinges...) stay in the test file.
"""

from __future__ import annotations

from itertools import combinations

import pytest

from .design import Design
from .geom import intersection_volume, is_watertight

BED_CONTACT_MIN = 1.0  # mm² of first-layer contact for a part to count as resting flat


def bed_contact_area(design: Design, name: str) -> float:
    """Area of the part's downward faces lying on the bed, as laid out on the plate."""
    m = design[name].print_mesh.copy()
    m.apply_transform(design.plate.transforms[name])
    down = m.face_normals[:, 2] < -0.999
    on_bed = m.triangles[:, :, 2].max(axis=1) < 1e-3
    return float(m.area_faces[down & on_bed].sum())


def standard_checks(
    design: Design,
    *,
    skip_pairs: set[frozenset[str]] = frozenset(),
    pair_tolerance: dict[frozenset[str], float] | None = None,
    interference_tolerance: float = 0.001,
    print_match_tolerance: float = 0.1,
) -> dict:
    """Test functions for `design`, to add to a test module with globals().update(...).

    skip_pairs: part pairs not checked for interference (e.g. meshing gears, whose
        teeth are drawn at an arbitrary rotation; check those another way).
    pair_tolerance: mm³ of overlap allowed for particular pairs (e.g. a snug key).
    interference_tolerance: mm³ allowed for every other pair (numerical noise).
    print_match_tolerance: % volume difference allowed between a part's print file
        and its assembled render (catches $fn differences).
    """
    pair_tolerance = pair_tolerance or {}
    names = [p.name for p in design]
    printed = [p.name for p in design.printed()]
    separate_print = [p.name for p in design.printed() if p.print_source]
    pairs = [pair for pair in combinations(names, 2) if frozenset(pair) not in skip_pairs]
    tests = {}

    @pytest.mark.parametrize("name", names)
    def test_watertight(measure, name):
        """The mesh as exported is a closed, consistently wound solid."""
        part = design.ready()[name]
        if part.blend_objects is not None:
            measure(f"{name} internal wall faces", part.interior_faces_removed, max=0, units="faces")
        assert is_watertight(part), (
            f"{name} isn't a closed solid"
            + (f": {part.interior_faces_removed} faces form zero-thickness walls inside it"
               if part.interior_faces_removed else "")
        )

    tests["test_watertight"] = test_watertight

    if separate_print:
        @pytest.mark.parametrize("name", separate_print)
        def test_print_matches_assembly(measure, name):
            """The part file you slice has the same geometry as the part in the assembly
            (fails when the part file renders at a different $fn than the assembly)."""
            part = design.ready()[name]
            assembled, printed_vol = part.mesh.volume, part.print_mesh.volume
            diff = measure(f"{name} printed vs assembled volume", 100 * (printed_vol - assembled) / assembled,
                           min=-print_match_tolerance, max=print_match_tolerance, units="%")
            assert abs(diff) <= print_match_tolerance, (
                f"{name}: print file volume differs from assembly by {diff:+.3f}% "
                f"(limit ±{print_match_tolerance}%); check $fn in the part file")

        tests["test_print_matches_assembly"] = test_print_matches_assembly

    if printed and not design.print_in_place:
        @pytest.mark.parametrize("name", printed)
        def test_fits_printer(measure, name):
            """Each printed part fits the printer's build volume."""
            d = design.ready()
            dims, volume = d[name].print_mesh.extents, d.printer_spec.volume
            measure(f"{name} max dimension", max(dims), max=min(volume))
            assert all(a <= b for a, b in zip(dims, volume)), (
                f"{name} is {' × '.join(f'{a:.1f}' for a in dims)} mm; "
                f"{d.printer_spec.name} holds {' × '.join(f'{b:g}' for b in volume)} mm")

        tests["test_fits_printer"] = test_fits_printer

    if printed:
        def test_plate_fits(measure):
            """All printed parts fit on one plate together (with plate groups: each bed fits)."""
            plate = design.ready().plate
            w, d, h = plate.printer.volume
            measure("plate width used", plate.size[0], max=w)
            measure("plate depth used", plate.size[1], max=d)
            if design.print_in_place:
                measure("height", plate.size[2], max=h)
            assert plate.fits, (
                f"parts need {' × '.join(f'{a:.1f}' for a in plate.size)} mm; "
                f"{plate.printer.name} holds {w:g} × {d:g} × {h:g} mm")

        @pytest.mark.parametrize("name", printed)
        def test_rests_flat_on_bed(measure, name):
            """Each printed part has a real footprint on the bed (not a point or edge)."""
            area = measure(f"{name} bed contact area", bed_contact_area(design.ready(), name),
                           min=BED_CONTACT_MIN, units="mm²")
            assert area >= BED_CONTACT_MIN, (
                f"{name} touches the bed with only {area:.2f} mm²; check its print orientation")

        tests["test_plate_fits"] = test_plate_fits
        tests["test_rests_flat_on_bed"] = test_rests_flat_on_bed

    if pairs:
        @pytest.mark.parametrize("a,b", pairs)
        def test_no_interference(measure, a, b):
            """No two parts occupy the same space."""
            d = design.ready()
            limit = pair_tolerance.get(frozenset((a, b)), interference_tolerance)
            vol = measure(f"{a} ∩ {b}", intersection_volume(d[a], d[b]), max=limit, units="mm³")
            assert vol <= limit, f"{a} and {b} overlap by {vol:.3f} mm³ (limit {limit} mm³)"

        tests["test_no_interference"] = test_no_interference

    return tests
