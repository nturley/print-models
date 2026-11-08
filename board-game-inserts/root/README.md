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
|   | **Height budget** | 71 − 24 − ~1 lid clearance ≈ **46** insert height (Walking through Root goes on top if thin, or in a pocket) |
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
     46 mm, the boards lie flat across them, and the box lid holds the boards
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

Current favourite: **"Matching faction boxes"**. All trays are full height (46).

```
┌──────────┬──────────┬─────────────────────┐
│ Marquise │ Eyrie    │ Shared deck (centred)│
├──────────┼──────────┼─────────────────────┤
│ Alliance │ Vagabond │ Shared: items, ruins,│
│          │          │ score, dice, suits   │
└──────────┴──────────┴─────────────────────┘
   91         91          94      (rows 106.5 deep)
```

**Faction box**: the same 91 × 106.5 × 46 outside for all four, with
parameters that differ per faction (card slot height, pockets). **Two pieces
glued together**, both open cups that print upright with no supports:

- **Base** (`parts/faction-base.scad`): the **side-loading card slot**, 65 × 90
  inside, open through the back wall so cards slide in and out sideways.
  Height = floor + card stack + 0.8 mm (Marquise/Alliance 2.7, Eyrie 5.8,
  Vagabond 10.2). Pinch notch in the floor at the opening, push hole under the
  closed end. **Solid apart from the slot**, so its whole top is a flat face
  against the top piece (the slicer's infill keeps the filament cost low). In
  the insert, the opening faces the box wall or a neighbouring tray, so cards
  can't slide out.
- **Joint:** two **5 mm pins, 4 mm tall**, stand on the base (in the token
  column strip, 10 mm from the front and back walls) and go into matching
  holes in the top's underside. The holes are 0.15 mm larger than the pins
  (`pin_fit`; FDM holes print slightly small, so this should come out as a
  light press fit). They go up into small posts inside the token-pocket
  hollows. Pin tips and hole mouths are chamfered. Glue is optional.
- **Top** (`parts/faction-top.scad`): its 1.2 mm floor is the slot's ceiling,
  and since that's the side printed against the bed, the cards slide on a
  smooth face and **nothing bridges** (not over the cards, not over the slot
  mouth). The **warrior bin** (65 wide, full inside depth) sits on that floor,
  so cards come out without disturbing the warriors. Piles: Marquise ≈ 22 mm,
  Eyrie ≈ 17.5, Alliance ≈ 8.5.
- The only overhangs are the 21.6 mm ceilings over the token-pocket hollows
  (tested).
- Press the top onto the base; add glue (CA or similar) on the flat joint
  face if the press fit is loose.
- **Token column** beside the slot and bin, 21.6 mm wide behind a 1.2 mm
  divider. One pocket per stack, with its **floor raised so the stack ends
  1 mm below the rim** (hollow underneath), and a **14 mm finger notch in the
  outer wall** beside each pocket, down to 2 mm above the pocket floor. In the
  insert, that wall presses against the next tray or the box wall, so nothing
  escapes through the notch. Eyrie and Vagabond have a spare compartment at
  the front of the column.

Model: `constants.scad`, `parts/faction-base.scad` + `parts/faction-top.scad`
(`-D 'faction="eyrie"'`), `parts/faction-box.scad` (the two glued, for viewing),
`root-insert.scad` (assembly). Tests: `uv run pytest board-game-inserts/root`.

### Printing

- Both pieces print upright, no supports.
- **Warping:** the first Marquise base (a thin 91 × 106.5 slab) lifted at the
  corners and failed. Since then, both pieces have **4 mm rounded corners** and
  an **anti-warp texture**: a 10 mm grid of 0.3 mm V-grooves in the bottom face
  (`warp_relief()` in `board-game-inserts/lib/print.scad`, same trick as the
  motor car frame), kept off the card slot ceiling on the top piece. Also
  clean the plate (soap and water / IPA), check the bed temperature, and use a
  5–8 mm brim if corners still lift.

### First test print: things to check

- Pin fit: too tight, too loose, or a good press fit? Tune `pin_fit`
  (0.15 now; try 0.1 tighter / 0.25 looser). A quick way to test: print just
  one base and top for the Marquise (the thinnest base).
- Can 2 cards be pinched out of the 1.5 mm Marquise/Alliance slots?
- Are the finger notches big enough to tip tokens out of their pockets?

**Shared tray** (94 × 106.5, 90.8 × 103.3 inside): three rows, each stack
evenly spaced across the width and the rows evenly spaced front to back:

- Back row: 3 suit marker stacks (rabbit, fox, mouse), long side running
  front to back (≈ 13 mm gaps; lying sideways would leave only ≈ 1 mm).
- Middle row: 2 dice.
- Front row: 4 square stacks: items ×2 (12 + 11), ruins, score markers.

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
