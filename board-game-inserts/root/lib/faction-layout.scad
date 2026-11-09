// Shared layout for the faction box and its contents: token pockets, card slot, shelf.
include <../constants.scad>

function sum(v, i = 0) = i >= len(v) ? 0 : v[i] + sum(v, i + 1);
function token_size(t) = t[0] == "round" ? round_token_d : t[0] == "pawn" ? pawn_l : square_tile;   // length along the column
function token_stack_h(t) = t[0] == "pawn" ? warrior_t : t[1] * token_t;

// Pockets along the token column, from the back wall forward: [[y_start, length], ...].
// Spare column length is shared out as clearance, up to token_pocket_clr_max per pocket;
// anything left over at the front is closed over (flush with the rim) in the top piece.
function token_pockets(f) =
    let (
        toks = faction_tokens(f),
        n = len(toks),
        sizes = [for (t = toks) token_size(t)],
        free = column_l - sum(sizes) - (n - 1) * divider_t,
        extra = min(free / n, token_pocket_clr_max),
        lens = [for (s = sizes) s + extra],
        ends = [for (i = [0 : n - 1]) faction_box_d - wall - (i == 0 ? 0 : sum([for (j = [0 : i - 1]) lens[j]]) + i * divider_t)]
    )
    assert(free >= 0, str(f, ": token stacks don't fit in the column"))
    [for (i = [0 : n - 1]) [ends[i] - lens[i], lens[i]]];

function spare_length(f) =
    let (p = token_pockets(f), last = p[len(p) - 1])
    last[0] - divider_t - wall;

// The box is two open cups glued together: the base (card slot) and the top (warriors + tokens).
// Corner pocket in the warrior bin (back-right, against the divider next to the token column),
// for factions whose column is full.
function bin_pocket_size(t) = token_size(t) + 2 * bin_pocket_clr;
function bin_pocket_origin(t) = [wall + bin_w - bin_pocket_size(t), faction_box_d - wall - bin_pocket_size(t)];

function slot_height(f) = faction_cards_h(f) + slot_headroom;
function base_h(f) = one_piece(f) ? 0 : floor_t + slot_height(f);   // where the top piece starts (0: one piece)
function top_floor_z(f) = base_h(f) + floor_t;       // floor of the warrior bin

// Pocket floor height: the stack's top ends token_headroom below the rim.
function pocket_floor_z(f, t) = max(top_floor_z(f), faction_box_h - token_stack_h(t) - token_headroom);

// One-piece box (Vagabond): top-loaded card pocket where the warrior bin would be, centred front to
// back, floor raised so the cards end token_headroom below the rim.
function top_card_origin() = [wall, (faction_box_d - card_slot_l) / 2];
function top_card_floor_z(f) = faction_box_h - token_headroom - faction_cards_h(f);

// Alignment pins, one in each corner. On the base they stand on the solid strips beside and in
// front of the (centred) card slot. In the top piece the two on the warrior-bin side go into the
// bin's raised solid floor; the two on the token side go up into posts inside the pocket hollows.
function pin_positions() =
    [for (x = [wall + pin_inset, faction_box_w - wall - pin_inset], y = [wall + pin_inset, faction_box_d - wall - pin_inset]) [x, y]];
function in_column(pos) = pos[0] >= column_x && pos[0] <= column_x + column_w;
function boss_d() = pin_d + pin_fit + 2 * boss_wall;
function boss_top(f) = base_h(f) + pin_h + pin_hole_extra + floor_t;   // hole depth + a 1.2 mm cap

// Warrior bin floor: raised to the top of the pin holes, so the holes under it stay inside a solid
// floor and the bin bottom is flat.
function bin_floor_z(f) = boss_top(f);

// Card slot, centred side to side in the base.
function slot_x0() = (faction_box_w - card_slot_w) / 2;
function slot_y0() = faction_box_d - wall - card_slot_l;

// Each token-column pin's post must fit under the raised floor of the pocket above it
// (or in the closed-over leftover space at the front). Pins under the bin go into its solid floor.
function pin_post_fits(f) =
    let (toks = faction_tokens(f), p = token_pockets(f))
    [for (pos = pin_positions()) if (in_column(pos))
        let (hits = [for (i = [0 : len(p) - 1]) if (pos[1] >= p[i][0] && pos[1] <= p[i][0] + p[i][1]) i])
        len(hits) == 0 || boss_top(f) <= pocket_floor_z(f, toks[hits[0]]) - pocket_floor_t];

// Every pin must stand on solid base, clear of the card slot (with ~1 mm to spare).
function pins_clear_slot() =
    min([for (p = pin_positions())
        (p[0] + pin_d / 2 + 1 <= slot_x0() || p[0] - pin_d / 2 - 1 >= slot_x0() + card_slot_w
         || p[1] + pin_d / 2 + 1 <= slot_y0()) ? 1 : 0]) == 1;
