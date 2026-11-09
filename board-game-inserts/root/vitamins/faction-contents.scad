// Faction cards and token stacks at measured size, sitting where they're stored. Fit checks only.
include <../constants.scad>
use <../lib/faction-layout.scad>

faction = "marquise";
in_layout = true;
show = "all";   // "cards", "tokens" or "all"

module faction_contents(f, show = "all") {
    // card stack in the slot
    if (show != "tokens") translate([slot_x0() + card_clr, slot_y0() + card_clr, floor_t])
        cube([card_w, card_l, faction_cards_h(f)]);
    // stack in the warrior bin's corner pocket (Marquise score marker)
    if (show != "cards") for (t = bin_corner_tokens(f)) {
        s = bin_pocket_size(); o = bin_pocket_origin(); h = t[1] * token_t;
        translate([o[0] + s / 2 - square_tile / 2, o[1] + s / 2 - square_tile / 2, faction_box_h - token_headroom - h])
            cube([square_tile, square_tile, h]);
    }
    // token stacks, centred in their pockets, on the raised floors
    toks = faction_tokens(f);
    p = token_pockets(f);
    if (show != "cards") for (i = [0 : len(toks) - 1]) {
        h = toks[i][1] * token_t;
        translate([column_x + column_w / 2, p[i][0] + p[i][1] / 2, pocket_floor_z(f, toks[i])])
            if (toks[i][0] == "round") cylinder(d = round_token_d, h = h, $fn = 64);
            else translate([-square_tile / 2, -square_tile / 2, 0]) cube([square_tile, square_tile, h]);
    }
}

translate(in_layout ? faction_pos(faction) : [0, 0, 0]) faction_contents(faction, show);
