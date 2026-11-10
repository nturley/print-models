# Root insert — requirements (draft)

Base game only (Leder Games English edition). No expansions (out of
scope), unsleeved cards, stock cardboard/wood components.

> The French Matagot edition uses a different box (368 × 298 × 108 mm) and is
> out of scope.

## Box

| | Value | Source |
|---|---|---|
| External | 290 × 226 × 74 mm | retailer listings (Folded Space) |
| Internal cavity | ≈ 279 × 216 mm (11 × 8.5 in), depth **TODO** | rough user measurement; confirm in mm |
| Board stack (map + 4 faction boards + rulebooks + player aids) | **TODO: measure** | |
| Insert height budget | internal depth − board stack (Feldherr's is 50 mm) | |

Reference: the Feldherr base-box organizer is 277 × 213 × 50 mm.

**Fit strategy:** the box is too large for the calipers, so the footprint
comes from a fit test print, not a precise measurement.

1. Start with the insert footprint = cavity − 1.5 mm per side
   (≈ 276 × 213 mm), set by a single `box_clearance` constant.
2. Print `fit-test`: a 2 mm tall × 2 mm wide perimeter frame at that
   footprint (minutes to print). Drop it in the box: it should go in easily
   with no visible rattle.
3. Adjust `box_clearance`, reprint until it fits, then record the final value
   here.

The calipers handle everything else: box depth (depth rod), board-stack
thickness, pieces and the card deck.

## Contents to store

Counts from the official packing list
([AADL](https://aadl.org/files/catalog_guides/Root_%20A%20Game%20of%20Woodland%20Magic%20and%20Right%20-%20Packing%20List.pdf),
totals match [Leder Games](https://ledergames.com/root)).

| Group | Contents |
|---|---|
| Marquise de Cat | 25 warriors (orange), 6 sawmills, 6 workshops, 6 recruiters, 8 wood, 1 keep |
| Eyrie Dynasties | 20 warriors (blue), 7 roosts, 4 leader cards, 2 vizier cards |
| Woodland Alliance | 10 warriors (green), 3 bases, 10 sympathy tokens |
| Vagabond | 1 pawn (grey), 3 character cards, 3 relationship markers, 15 quest cards |
| Shared | 54-card deck, 23 items, 4 ruins, 4 score markers, 2 dice |
| Winter map | 12 suit markers (4 yellow, 4 red, 4 orange) |
| Other cards | 16 faction overview cards, 4 board setup example cards |
| Paper | map board, 4 faction boards, Law of Root, single sheet, Learning to Play, Walking through Root |

Piece shapes: all warriors/pawn are treated as one meeple size. **Square
tiles are 17.6 × 17.6 mm**: buildings (28), ruins (4), items (23) = 55
squares, plus score (4) and relationship (3) markers = **62 squares**.
**Round tokens Ø 19.2 × 2**: sympathy (10), wood (8), keep (1) = **19
rounds**. **Suit markers** (winter map only, randomly placed on the blank
clearings at setup): 12 irregular cardboard pieces, 28.7 × 14.7 × 2 (4 each
fox/red, rabbit/yellow, mouse/orange).

## Measurement checklist

Values in mm. The boards' length × width isn't needed: they're sized to the box
and lie on top of the insert, so only their stack thickness matters.

| # | What | Value |
|---|---|---|
| 1 | Lower box inside height (floor → wall top) | ≈ 71 |
| 2 | Lid inside depth | |
| 3 | Map board thickness (folded) | ≈ 14.2 |
|   | Full stack: map + 4 player boards + Law of Root + single sheet + Learning to Play | ≈ 24 |
|   | **Height budget** | 71 − 24 − 7 lid clearance = **40** insert height. (Was 46 with 1 mm clearance: the printed insert kept the box from closing, so trays were lowered; ~32 is the floor before warrior piles and stacks stop fitting.) |
| 3a | Map board footprint (folded) | ≈ 203 × 276 (8 × 10⅞ in): ~3 mm spare lengthwise, ~13 mm widthwise |
| 3b | Player boards (×4) footprint / stack | ≈ 213 × 278 (8⅜ × 10 15/16 in), the largest flat part, so the cavity is ≥ 278 long; stack of 4 ≈ 6.4 |
| 3c | Law of Root booklet + same-size single sheet: footprint / thickness | |
| 3d | Learning to Play booklet (much smaller): footprint / thickness | |
| 3e | Walking through Root booklet (very small): footprint / thickness | |
| 4 | Card width × length | 63 × 88 (standard). Wells ≈ 65 × 90; cards lie flat (63 > 46 insert height) |
| 5 | Shared deck height (54) / quest deck height (15) | 19 (≈ 0.35 per card) / ≈ 5.3 estimated |
| 6 | Other cards: quests, overview, vagabond roles etc. (all 63 × 88) | ≈ 8.2 stack |
| 6a | Eyrie cards (11, 63 × 88) | ≈ 3.8. All cards together ≈ 31 |
| 6b | Marquise / Alliance cards (a couple each: walkthrough + reference only) | < 1 each (estimated at 0.35/card) |
| 7 | Warrior meeples (all assumed alike) | ≈ 16.5–18.9 × 18.7–22 × 8.9 (cat / alliance measured); 25 loose ≈ 160 cm³ |
| 8 | Square tiles (buildings, ruins, items) | 17.6 × 17.6 × 2. Stacks: sawmill/workshop/recruiter 12 each, roost 14, base 6, ruin 8, items 46 (split, or a flat tray); wells ≈ 19 square |
| 9 | Round tokens (sympathy, wood, keep) | Ø 19.2 × 2. Stacks: sympathy 20, wood 16; wells ≈ Ø 20.5 |
| 9a | Suit markers (12, irregular) | 28.7 × 14.7 × 2 (thickness assumed). 12 stacked = 24; pocket ≈ 31 × 17 |
| 10 | Die (×2, rounded d12) | 21.7 flat to flat, 25.5 corner to corner. On a face: 21.7 tall, ≈ 25.5 footprint; pocket ≈ Ø 27 |

## Functional requirements

1. **One tray per faction.** Holds all of that faction's pieces and you
   can hand it to a player. *(proposed; confirm)*
2. **Shared tray** for the items, ruins, dice and score markers.
3. **Card storage** for the shared deck and quest deck, with finger notches.
   Each faction's reference/walkthrough cards go in a 65 × 90 pocket in that
   faction's tray (≈ 2 mm deep; Eyrie ≈ 5 mm for its 11 cards).
   *(proposed; confirm)*
4. The map board, faction boards and rulebooks lie flat on top of the insert,
   and the lid closes flush.
5. **Shake-proof in any orientation.** The box can be shaken, carried or
   stored on its side without anything mixing or coming loose:
   - **No lids: the board stack caps every tray.** All trays are the full
     40 mm, the boards lie flat across them, and the box lid holds the boards
     within ~1 mm of the tray tops, which is too small a gap for a 2 mm token or a warrior.
     (Trays can spill if tipped while out of the box; accepted.)
   - Insert fills the cavity with ≤ 1 mm play.
   - Pockets are sized close to their contents (≈ 0.5–1.5 mm clearance) so
     stacks can't shuffle.
6. **Warriors are stored as loose piles, not neat stacks.** Each bin is sized
   by volume: count × bounding box ÷ looseness (default 55%: the pieces fill
   55% of the bin), spread over the usable height but **never piled deeper
   than ~4 warriors (≈ 36 mm)**, so bins stay wide and easy to scoop from.
   For example, 25 cat warriors need ≈ 4,100 mm² of floor (≈ 64 × 65) and
   10 Alliance warriors ≈ 40 × 40.
7. **Every card stack has a finger notch** (≈ 12 mm scoop on one side) for
   lifting the cards out. This includes faction cards in floor pockets, so a
   floor pocket needs ≈ 65 × 102 inside the tray.

## Decisions

- **Base game only.** Expansions are out of scope; fit the base game exactly.
- **Filament colour per faction**: Marquise orange, Eyrie blue, Alliance
  green, Vagabond grey; shared trays in a neutral colour.

## Layout direction (from the 3D sandbox)

Current favourite: **"Matching faction boxes"**. All trays are full height (40).

```
┌──────────┬──────────┬─────────────────────┐
│ Marquise │ Eyrie    │ Shared deck (centred)│
├──────────┼──────────┼─────────────────────┤
│ Alliance │ Vagabond │ Shared: items, ruins,│
│          │          │ score, dice, suits   │
└──────────┴──────────┴─────────────────────┘
   91         91          94      (rows 106.5 deep)
```

**Faction box**: the same 91 × 106.5 × 40 outside for all four, with
parameters that differ per faction (card slot height, pockets). **Two pieces
glued together**, both open cups that print upright with no supports:

**Vagabond box: one piece.** The Vagabond has no warriors, so its box is just
the top piece printed from the floor up (`one_piece()` in `constants.scad`):
no base, no side slot, no pins. Its ~30 cards (8.2 mm) lie in a top-loaded
65 × 90 pocket where the warrior bin would be, floor raised so they end 5 mm
below the rim (the deck's extra room for cards that thicken), with a **30 mm finger scoop** centred on the left wall: it cuts through
the wall (which faces the Alliance box in the insert) and dips 5 mm below the
card floor, over a solid column and peaked-roof hollows underneath. The pawn gets
its own pocket in the token column. The other three factions keep the two-piece
box below.

- **Base** (`parts/faction-base.scad`): the **side-loading card slot**, 65 × 90
  inside, **centred side to side**, open through the back wall so cards slide in and out sideways.
  Height = floor + card stack + 1.5 mm headroom (Marquise/Alliance 3.4, Eyrie 6.5,
  Vagabond 10.9; 0.8 mm headroom looked too tight). Pinch notch in the floor at the opening, push hole under the
  closed end. **Solid apart from the slot**, so its whole top is a flat face
  against the top piece (the slicer's infill keeps the filament cost low). In
  the insert, the opening faces the box wall or a neighbouring tray, so cards
  can't slide out.
- **Joint:** four **4.8 mm pins, 4 mm tall**, one in each corner (6 mm from both
  walls), stand on the solid strips beside and in front of the centred card
  slot and go into matching holes in the top's underside. The two on the
  warrior-bin side go into the bin's raised solid floor; the two on the token
  side go up into small posts inside the token-pocket hollows.

  Holes are 5.15 mm (`pin_hole_d`); the pins are `pin_fit` smaller. At 0.15
  (5.0 mm pins) the orange Marquise was a perfect press fit but the green
  Alliance was too tight (filaments vary); at 0.25 (4.9 mm) the Vagabond was
  still tight. Pins are now **4.8 mm (`pin_fit` = 0.35)**: err on the loose
  side, since a loose fit takes a drop of glue but a tight one can crack a
  piece during assembly. Tune the pin, not the hole: a new base fits tops
  already printed. Pin tips and hole mouths are chamfered.
- **Top** (`parts/faction-top.scad`): its 1.2 mm floor is the slot's ceiling,
  and since that's the side printed against the bed, the cards slide on a
  smooth face and **nothing bridges** (not over the cards, not over the slot
  mouth). The **warrior bin** (65 wide, full inside depth) has a **flat floor
  raised to the top of the pin holes** (~5.6 mm above the joint, solid
  underneath), so nothing pokes up into it; cards come out without disturbing
  the warriors. Piles: Marquise ≈ 22 mm,
  Eyrie ≈ 17.5, Alliance ≈ 8.5.
- No bridges: the hollows have 45° peaked roofs (`tent_hollow()` in
  `board-game-inserts/lib/print.scad`); the only flat overhangs left are the
  5 mm tops of the pin holes (tested).
- Press the top onto the base; add glue (CA or similar) on the flat joint
  face if the press fit is loose.
- **Token column** beside the slot and bin, 21.6 mm wide behind a 1.2 mm
  divider. One pocket per stack, with its **floor raised so the stack ends
  2.5 mm below the rim** (hollow underneath, closed by a 45° peaked roof
  so nothing bridges), and a **14 mm finger notch in the
  outer wall** beside each pocket, **flat-bottomed at the pocket floor** so a
  fingernail fits under the bottom token (narrower than any token, so none
  can slip out). Pockets for round tokens (wood, keep, sympathy) are round. In the
  insert, that wall presses against the next tray or the box wall, so nothing
  escapes through the notch. Eyrie and Vagabond have leftover column space at
  the front: it's closed over flush with the rim (hollow underneath, peaked
  roof) so nothing can fall in.

**Pocket icons:** each token pocket has an icon debossed 0.6 mm into its
floor, so an empty pocket shows what goes in it. They're from
[game-icons.net](https://game-icons.net) (CC BY 3.0; artists credited in
`lib/icons/CREDITS.md`), stored as plain SVGs in `lib/icons/` and imported by
`lib/icons.scad`:

| Pocket | Icon |
|---|---|
| Wood / keep / sawmills / workshops / recruiters | log / castle / circular saw / anvil impact / shaking hands |
| Roosts | tree branch |
| Bases / sympathy | camping tent / fist |
| Relationship markers | hearts |
| Items (supply and Vagabond) | swap bag |
| Ruins | ancient columns |
| Score markers | round star |

No icon on the deck, the dice slot, the suit markers, the pawn (their pockets'
shapes say what they hold) or the blank spare tiles.

**Where the tokens go** (from the Law of Root, as transcribed at
therootdatabase.com). The **score marker is always in the top-right pocket**
(the back of the token column) of every faction box:

| Box | Token column (back to front) |
|---|---|
| Marquise | **score marker**, wood, sawmills, workshops, recruiters; the **keep** is in a round walled pocket in the warrior bin's back-right corner, next to the score marker (the column is full) |
| Eyrie | **score marker**, roosts |
| Alliance | **score marker**, sympathy, bases |
| Vagabond | **score marker**, relationship markers, **11 Vagabond-only items** (4 ruin items + 7 starting items, used only with the Vagabond: 9.3.4–9.3.5), **score marker**, **pawn**; its cards lie in a top-loaded pocket where the warrior bin would be |
| Shared tray | 12 supply items (placed every game: 5.1.5), ruins (every game: 5.1.4), suit markers, dice, deck, 18 blank spare tiles (not on the components list) |

Model: `constants.scad`, `parts/faction-base.scad` + `parts/faction-top.scad`
(`-D 'faction="eyrie"'`), `parts/faction-box.scad` (the two glued, for viewing),
`root-insert.scad` (assembly). Tests: `uv run pytest board-game-inserts/root`.

### Printing

- Both pieces print upright, no supports.
- **Warping:** the Marquise base is a thin 91 × 106.5 slab.
  - Print 1 (square corners, flat bottom) finished but **lifted at the
    corners**. Both pieces now have **4 mm rounded corners**.
  - Print 2 added an anti-warp texture (a 10 mm grid of V-grooves in the
    bottom face, `warp_relief()`) and **failed on the first layer**. The
    grooves were ~0.28 mm deep, deeper than the 0.2 mm first layer, so the
    slicer split the first layer into hundreds of separate 10 mm islands that
    gripped poorly and got knocked loose (K2, textured PEI, matte PLA). **No
    bottom texture now.**
  - Settings: **regular (outer) brim, 5 mm**, not brim ears (ears only go on
    sharp corners, and the corners are rounded). **Bed 60 °C** for PLA. Clean
    the plate with dish soap and water first. Optionally 210 °C nozzle for
    matte PLA.
  - Print 3 (rounded corners, no texture, regular 5 mm brim, bed raised to
    60 °C on the printer's screen during the print): **printed flat and
    clean**. Use these settings.
  - If it ever lifts again: raise the minimum base height (~4 mm) to stiffen it.

### First test print: things to check

- Pin fit: too tight, too loose, or a good press fit? Tune `pin_fit`
  (0.15 now; try 0.1 tighter / 0.25 looser). A quick way to test: print just
  one base and top for the Marquise (the thinnest base).
- Can 2 cards be pinched out of the 2.2 mm Marquise/Alliance slots?
- Are the finger notches big enough to tip tokens out of their pockets?

**Shared tray** (`parts/shared-tray.scad`): one piece filling the right-hand
column, 94 × 213 × 40 (fits the K2 bed).

- **Back half:** the 54-card deck in a 65 × 90 pocket centred in that half,
  floor raised so the deck ends 5 mm below the rim (extra room: cards thicken as they age), with a **26 mm finger
  scoop** on each long side (as big as fits inside the outer walls) that dips 5 mm
  below the card floor (to get under the bottom card), over a solid column.
- **Front half**, three rows:
  - Back row: **one pill-shaped bowl** (curved both ways) across the tray for all 12 suit markers, loose (they
    were too irregular for per-suit pockets): a trough with a curved floor,
    34 mm front to back, 17 mm deep (a half-round: as deep as it goes without undercutting the rim).
  - Middle row: **both dice in one long slot**, with a **20 mm scoop** at each end.
  - Front row: 4 square stacks (the 12 supply items, ruins, and the 18 blank
    spare tiles as two stacks of 9) **against the front wall**, each with a
    flat-bottomed finger notch through the wall down to its pocket floor,
    like the faction boxes.
  - 0.75 mm clearance around every stack; floors raised so everything ends
    2.5 mm below the rim.
- **Wood grain** on the four outer walls: horizontal grain lines cut 0.4 mm in
  (added after rendering, in `tests/test_root.py` via `part.texture`; the .scad
  stays smooth). The bottom 1 mm is left smooth for a clean first layer.
- 4 mm rounded corners; hollow underneath in peaked-roof bays (`tent_bays()`,
  one set per half at that half's height), so it prints upright with no
  supports and no bridges (tested). Layout in `lib/shared-layout.scad`; rows
  in `shared_rows` in `constants.scad`.

Minimum widths at 106.5 deep (4-warrior piles, 55% looseness): Marquise 91,
the other factions and the shared deck 69, combined shared tray 65 (or 36 as
a full-depth 213 strip).

## To settle by prototyping

These get decided by printing and trying a few iterations, so the design must
keep them swappable (lid style and tray top as parameters/modules in `lib/`,
not baked into each tray):

- **In-play use:** whether faction trays double as holders during play
  (e.g. the lid slides under the tray, pockets shaped for scooping).
- Labels: text or faction icons, embossed or debossed.
- Is there an acceptable limit on total print time or filament?

## Prior art

- [Feldherr organizer, base box](https://www.feldherr.com/feldherr-organizer-fuer-root-grundspielbox/a-62744) (foam, 277 × 213 × 50)
- [Folded Space Root insert](https://www.boardgamebliss.com/products/folded-space-root-expansions) (three layers + rulebooks)
- [Sigismond0 / Printables](https://printables.com/model/153481-root-organizer-for-base-game-extension-1-and-2/collections): a box per faction, rules engraved on the lids
- [Romn, Thingiverse 3092904](https://3dsearch.app/result/thingiverse/thing%3A3092904): popular 2018 box organizer
- [Root Board Game System (modular, 2×4 × 2 layers)](https://3dgo.app/models/thingiverse/5547235)
