// Layout for the shared tray: where each token stack, the dice, the suit-marker bowl and the deck sit.
// The token section is the front half (y 0 .. shared_d), the deck section the back half.
include <../constants.scad>

function sum(v, i = 0) = i >= len(v) ? 0 : v[i] + sum(v, i + 1);

// Footprint of a stack (without clearance) and its height.
function stack_size(t) =
    t[0] == "square" ? [square_tile, square_tile]
    : [t[1] * die_corner, die_corner];   // dice: side by side in one slot
function stack_h(t) = t[0] == "dice" ? die_flat : t[1] * token_t;
// Pocket footprint: the stack plus clearance; the suit bowl spans the tray.
function pocket_size(t) =
    t[0] == "bowl" ? [shared_w - 2 * wall - 2 * suit_bowl_margin, suit_bowl_l]
    : stack_size(t) + [2, 2] * shared_clr;

// Pocket floor: the stack's top ends token_headroom below the rim (the bowl: its deepest point).
function stack_floor_z(t) =
    t[0] == "bowl" ? faction_box_h - suit_bowl_depth : faction_box_h - token_headroom - stack_h(t);

// Bowl trough: a cylinder along x whose arc spans the bowl's front-to-back length at the rim and
// dips suit_bowl_depth in the middle. Returns [radius, axis height].
function bowl_arc() =
    let (half = suit_bowl_l / 2, dd = suit_bowl_depth, r = (half * half + dd * dd) / (2 * dd))
    [r, faction_box_h - dd + r];

// Every pocket in the token section: [[kind, count, icon], x_centre, y_centre, pocket_w, pocket_l],
// tray coordinates. Rows are listed back to front. The front row sits against the front wall (its
// finger notches go through it); the other rows, and the pockets in every row, are spread evenly.
function shared_pockets() =
    let (
        iw = shared_w - 2 * wall,
        id = shared_d - 2 * wall,
        n = len(shared_rows),
        depths = [for (r = shared_rows) max([for (t = r) pocket_size(t)[1]])],
        rest = id - depths[n - 1],                                   // depth left for the other rows
        vgap = (rest - sum([for (i = [0 : n - 2]) depths[i]])) / n   // n-1 rows: n gaps
    )
    assert(vgap >= 2, "shared tray rows don't fit")
    [for (i = [0 : n - 1])
        let (
            row = shared_rows[i],
            widths = [for (t = row) pocket_size(t)[0]],
            hgap = (iw - sum(widths)) / (len(row) + 1),
            yc = i == n - 1 ? wall + depths[i] / 2
                 : wall + id - vgap * (i + 1) - (i == 0 ? 0 : sum([for (j = [0 : i - 1]) depths[j]])) - depths[i] / 2
        )
        for (j = [0 : len(row) - 1])
            [row[j],
             wall + hgap * (j + 1) + (j == 0 ? 0 : sum([for (m = [0 : j - 1]) widths[m]])) + widths[j] / 2,
             yc, pocket_size(row[j])[0], pocket_size(row[j])[1]]];

// The front row's pockets sit against the front wall and get finger notches through it.
function front_row(p) = p[2] - p[4] / 2 <= wall + 0.01;

// Smallest gap between pockets in any row (must be at least ~2 mm of wall).
function shared_min_hgap() =
    min([for (r = shared_rows)
        (shared_w - 2 * wall - sum([for (t = r) pocket_size(t)[0]])) / (len(r) + 1)]);

function lowest_floor(pockets) = min([for (p = pockets) stack_floor_z(p[0])]);

// Deck section: the deck pocket (cards + card_clr each side), centred in the back half.
function deck_pocket() = [card_w + 2 * card_clr, card_l + 2 * card_clr];
function deck_floor_z() = faction_box_h - deck_headroom - deck_h;
function deck_centre() = [shared_w / 2, shared_d + shared_d / 2];
