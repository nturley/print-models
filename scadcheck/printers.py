"""Printer build volumes, used for bed-fit tests and the viewer's print-bed view."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Printer:
    name: str
    volume: tuple[float, float, float]  # x, y, z in mm; printable area is centred on the origin
    # Outline of the physical build plate (x, y) in the same centred coordinates, for
    # the viewer. Hand-drawn from measurements; None draws a plain margin around the area.
    plate: tuple[tuple[float, float], ...] | None = None


def _plate_with_front_tabs(half_w: float, back: float, front: float, tab_front: float,
                           tab_outer: float, tab_inner: float) -> tuple[tuple[float, float], ...]:
    return (
        (-half_w, back), (half_w, back), (half_w, front),
        (tab_outer, tab_front), (tab_inner, tab_front), (tab_inner - 4, front),
        (-(tab_inner - 4), front), (-tab_inner, tab_front), (-tab_outer, tab_front), (-half_w, front),
    )


PRINTERS = {
    # Volumes: https://store.creality.com/ca/blogs/buying-guides/creality-k2-plus-vs-k2-pro-vs-k2
    # K2 plate: ~278mm square spring-steel sheet with two pull tabs at the front, measured
    # from Creality Print 7.0's bed model (not copied: Creality Print is AGPL).
    "creality-k2": Printer("Creality K2", (260, 260, 260),
                           _plate_with_front_tabs(139, 138.2, -139, -156.2, 135, 114)),
    "creality-k2-pro": Printer("Creality K2 Pro", (300, 300, 300)),
    "creality-k2-plus": Printer("Creality K2 Plus", (350, 350, 350)),
}

DEFAULT_PRINTER = "creality-k2"
