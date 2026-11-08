// Layout for the shared tray: where each token stack, the dice and the deck sit.
// The token section is the front half (y 0 .. shared_d), the deck section the back half.
include <../constants.scad>

function sum(v, i = 0) = i >= len(v) ? 0 : v[i] + sum(v, i + 1);

// Footprint of a stack (without clearance) and its height.
function stack_size(t) =
    t[0] == "square" ? [square_tile, square_tile]
    : t[0] == "suit" ? [suit_w, suit_l]
    : [t[1] * die_corner, die_corner];   // dice: side by side in one slot
function stack_h(t) = t[0] == "dice" ? die_flat : t[1] * token_t;
function pocket_size(t) = stack_size(t) + [2, 2] * shared_clr;

// Pocket floor: the stack's top ends token_headroom below the rim.
function stack_floor_z(t) = faction_box_h - token_headroom - stack_h(t);

// Every pocket in the token section: [[kind, count], x_centre, y_centre, pocket_w, pocket_l], tray coordinates.
// Rows are listed back to front; pockets in a row, and the rows, are spread evenly.
function shared_pockets() =
    let (
        iw = shared_w - 2 * wall,
        id = shared_d - 2 * wall,
        depths = [for (r = shared_rows) max([for (t = r) pocket_size(t)[1]])],
        vgap = (id - sum(depths)) / (len(shared_rows) + 1)
    )
    assert(vgap >= 2, "shared tray rows don't fit")
    [for (i = [0 : len(shared_rows) - 1])
        let (
            row = shared_rows[i],
            widths = [for (t = row) pocket_size(t)[0]],
            hgap = (iw - sum(widths)) / (len(row) + 1),
            yc = wall + id - vgap * (i + 1) - (i == 0 ? 0 : sum([for (j = [0 : i - 1]) depths[j]])) - depths[i] / 2
        )
        for (j = [0 : len(row) - 1])
            [row[j],
             wall + hgap * (j + 1) + (j == 0 ? 0 : sum([for (m = [0 : j - 1]) widths[m]])) + widths[j] / 2,
             yc, pocket_size(row[j])[0], pocket_size(row[j])[1]]];

// Smallest gap between pockets in any row (must be at least ~2 mm of wall).
function shared_min_hgap() =
    min([for (r = shared_rows)
        (shared_w - 2 * wall - sum([for (t = r) pocket_size(t)[0]])) / (len(r) + 1)]);

function lowest_floor(pockets) = min([for (p = pockets) stack_floor_z(p[0])]);

// Deck section: the deck pocket (cards + card_clr each side), centred in the back half.
function deck_pocket() = [card_w + 2 * card_clr, card_l + 2 * card_clr];
function deck_floor_z() = faction_box_h - token_headroom - deck_h;
function deck_centre() = [shared_w / 2, shared_d + shared_d / 2];
