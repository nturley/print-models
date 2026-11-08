# Board game inserts

3D-printed box inserts for board games. One subfolder per game; shared
parametric modules live in `lib/`.

## Layout

```
board-game-inserts/
  lib/            shared modules (trays, lids, card wells, labels)
  root/           Root (Leder Games)
    README.md     requirements + print notes
    constants.scad  measured box/component dimensions
    parts/        one tray per file
    vitamins/     cards, meeples, boards — for fit checks only
    tests/        scadcheck tests (fits in box, lid closes, fits on K2 bed)
```

## Shared requirements (all games)

- Every tray fits on the Creality K2 bed (260 × 260 mm) without splitting.
- Insert plus boards/rulebooks fill the box to the lid with ≤ 1 mm play, so
  nothing moves when the box is carried or stored on its side.
- Dimensions come from measured values in each game's `constants.scad`,
  never hard-coded in parts. Clearances are named constants
  (e.g. `fit_clearance`, `card_clearance`).
- Pockets for small tokens use scooped/curved floors so pieces slide out.
- Card wells have a finger notch on at least one side.
- Prefer designs that print without supports.
- Tests check: every part inside the box cavity, no part-to-part
  intersection, total stack height ≤ box depth minus board stack.
