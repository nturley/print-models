"""pytest plugin: collect measurements from tests and write <design>/build/report.json.

Tests call the `measure` fixture to record a value (optionally with two points to
draw in the viewer). After the run, each design that had tests gets a report with
its parts and every test's outcome and measurements.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pytest

from .design import REGISTRY
from .exports import export_downloads, repo_info
from .geom import Distance

_measurements: dict[str, list[dict]] = {}  # nodeid -> measurements
_tests: dict[str, dict] = {}  # nodeid -> test info


def _design_of(nodeid: str) -> str:
    return nodeid.replace("\\", "/").split("/", 1)[0]


@pytest.fixture
def measure(request):
    """measure(label, value, *, min=None, max=None, units="mm")

    `value` may be a float or a geom.Distance (its closest points get drawn).
    `min`/`max` are the limits the test asserts, shown alongside the value.
    """
    nodeid = request.node.nodeid

    def record(label: str, value, *, min=None, max=None, units: str = "mm"):
        entry = {"label": label, "units": units, "min": min, "max": max}
        if isinstance(value, Distance):
            entry["value"] = round(value.distance, 4)
            entry["points"] = [value.point_a, value.point_b]
        else:
            entry["value"] = round(float(value), 4)
        _measurements.setdefault(nodeid, []).append(entry)
        return value

    return record


def _short_message(report) -> str | None:
    """One readable line for the viewer: the assertion's own message if it has one,
    otherwise pytest's summary with numpy wrappers like np.float64(1.5) unwrapped."""
    crash = getattr(report.longrepr, "reprcrash", None)
    if crash is None:
        return None
    text = re.sub(r"np\.(?:float|int)\d*\(([^()]*)\)", r"\1", str(crash.message))
    first = text.splitlines()[0] if text else ""
    return first.removeprefix("AssertionError: ")


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        info = _tests.setdefault(report.nodeid, {})
        info.update(
            nodeid=report.nodeid,
            outcome=report.outcome,
            message=_short_message(report) if report.failed else None,
        )


def pytest_collection_modifyitems(items):
    for item in items:
        doc = getattr(item.function, "__doc__", None)
        _tests.setdefault(item.nodeid, {})["doc"] = doc.strip().splitlines()[0] if doc else None
        _tests[item.nodeid]["name"] = item.name


def pytest_sessionfinish(session):
    by_design: dict[str, list[dict]] = {}
    for nodeid, info in _tests.items():
        if "outcome" not in info:
            continue  # not run (deselected)
        info["measurements"] = _measurements.get(nodeid, [])
        by_design.setdefault(_design_of(nodeid), []).append(info)

    for name, tests in by_design.items():
        design = REGISTRY.get(name)
        if design is None:
            continue
        plate = design.plate
        printer = plate.printer
        repo_root = design.root.parent
        readme = design.root / "README.md"
        report = {
            "design": name,
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "repo": repo_info(repo_root),
            "readme": readme.relative_to(repo_root).as_posix() if readme.exists() else None,
            "downloads": export_downloads(design),
            "printer": {
                "name": printer.name,
                "volume": list(printer.volume),
                "plate": [list(pt) for pt in printer.plate] if printer.plate else None,
            },
            "plate_size": [round(v, 3) for v in plate.size],
            "parts": [
                {
                    "name": p.name,
                    "kind": p.kind,
                    "stl": p.stl.relative_to(design.build_dir).as_posix(),
                    "source": p.link_source.relative_to(repo_root).as_posix(),
                    "print_stl": f"print/{p.name}.stl" if p.kind == "part" else None,
                    "color": p.color,
                    # as printed for printed parts, as assembled for vitamins
                    "size": [round(v, 3) for v in (p.print_mesh if p.kind == "part" else p.mesh).extents],
                    # row-major 4x4 placing print_stl on the print bed (printed parts only)
                    "plate": plate.transforms[p.name].round(6).ravel().tolist() if p.name in plate.transforms else None,
                }
                for p in design
            ],
            "tests": tests,
        }
        out = Path(design.build_dir) / "report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
