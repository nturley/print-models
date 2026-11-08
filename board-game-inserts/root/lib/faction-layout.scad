// Shared layout for the faction box and its contents: token pockets, card slot, shelf.
include <../constants.scad>

function sum(v, i = 0) = i >= len(v) ? 0 : v[i] + sum(v, i + 1);
function token_size(t) = t[0] == "round" ? round_token_d : square_tile;

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
function slot_height(f) = faction_cards_h(f) + slot_headroom;
function base_h(f) = floor_t + slot_height(f);       // base height = where the top piece starts
function top_floor_z(f) = base_h(f) + floor_t;       // floor of the warrior bin

// Pocket floor height: the stack's top ends token_headroom below the rim.
function pocket_floor_z(f, t) = max(top_floor_z(f), faction_box_h - t[1] * token_t - token_headroom);

// Alignment pins: in the token column, near the front and back walls. On the base they stand
// on its flat top; in the top piece the holes go up into posts inside the pocket hollows.
function pin_positions() = [
    [column_x + column_w / 2, wall + pin_inset],
    [column_x + column_w / 2, faction_box_d - wall - pin_inset],
    corner_pin_position(),
];
// Third pin, on the warrior-bin side: front-left corner, on the base's solid strip in front of the
// card slot. In the top piece its hole goes up into a small corner block in the warrior bin.
function corner_pin_position() = [wall + corner_pin_inset, wall + corner_pin_inset];
function in_column(pos) = pos[0] >= column_x && pos[0] <= column_x + column_w;
function boss_d() = pin_d + pin_fit + 2 * boss_wall;
function boss_top(f) = base_h(f) + pin_h + pin_hole_extra + floor_t;   // hole depth + a 1.2 mm cap

// Each token-column pin's post must fit under the raised floor of the pocket above it
// (or in the closed-over leftover space at the front). The corner pin's block sits in the warrior bin.
function pin_post_fits(f) =
    let (toks = faction_tokens(f), p = token_pockets(f))
    [for (pos = pin_positions()) if (in_column(pos))
        let (hits = [for (i = [0 : len(p) - 1]) if (pos[1] >= p[i][0] && pos[1] <= p[i][0] + p[i][1]) i])
        len(hits) == 0 || boss_top(f) <= pocket_floor_z(f, toks[hits[0]]) - pocket_floor_t];

// The corner pin must stand on solid base, in front of the card slot.
function corner_pin_fits() =
    let (pos = corner_pin_position(), slot_y = faction_box_d - wall - card_slot_l)
    pos[1] + pin_d / 2 + 1 <= slot_y;
