"""pytest plugin: collect measurements from tests and write <design>/build/report.json.

Tests call the `measure` fixture to record a value (optionally with two points to
draw in the viewer). After the run, each design that had tests gets a report with
its parts and every test's outcome and measurements.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from .design import REGISTRY
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


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        info = _tests.setdefault(report.nodeid, {})
        info.update(
            nodeid=report.nodeid,
            outcome=report.outcome,
            message=str(report.longrepr.reprcrash.message) if report.failed and hasattr(report.longrepr, "reprcrash") else None,
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
        report = {
            "design": name,
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "parts": [
                {
                    "name": p.name,
                    "kind": p.kind,
                    "stl": p.stl.relative_to(design.build_dir).as_posix(),
                    "color": p.color,
                }
                for p in design
            ],
            "tests": tests,
        }
        out = Path(design.build_dir) / "report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
