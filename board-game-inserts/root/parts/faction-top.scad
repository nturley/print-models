// Faction box, top piece: warrior bin + token column, an open cup that sits on the base
// (faction-base.scad), located by two pins pressed into holes in its underside (glue optional).
// Its floor is the card slot's ceiling. Prints upright (floor on the bed).
//   - Warrior bin: 65 wide, full inside depth, flat floor raised above the pin holes.
//   - Token column on the right: one pocket per stack, floor raised so the stack ends just below
//     the rim (hollow underneath, with a 45° peaked roof so nothing bridges), and a finger notch
//     in the outer wall beside it, down to the pocket floor. Round tokens get round pockets.
//   - Four pin holes, one per corner: bin side into the bin's solid floor, token side into posts.
//   - No lid: in the box, the board stack caps every tray.
//   - Rounded corners (anti-warp).
// Render one with:  openscad -D 'faction="eyrie"' -o eyrie-top.stl faction-top.scad
include <../constants.scad>
use <../lib/faction-layout.scad>
use <../../lib/print.scad>

faction = "marquise";
in_layout = true;

module faction_top_shell(f) {
    w = faction_box_w;
    d = faction_box_d;
    z0 = base_h(f);
    h = faction_box_h;
    fz0 = top_floor_z(f);
    toks = faction_tokens(f);
    pockets = token_pockets(f);
    spare = spare_length(f);
    ri = corner_r - wall;   // inner corners keep the wall thickness at the rounded outer corners

    difference() {
        translate([0, 0, z0]) rbox([w, d, h - z0], corner_r);

        // warrior bin, full inside depth, flat floor raised above the pin holes
        translate([wall, wall, bin_floor_z(f)]) rbox([bin_w, d - 2 * wall, h], ri);

        for (i = [0 : len(pockets) - 1]) {
            p = pockets[i];
            fz = pocket_floor_z(f, toks[i]);
            yc = p[0] + p[1] / 2;
            // pocket, from its raised floor up through the rim: fully rounded for round tokens
            translate([column_x, p[0], fz])
                rbox([column_w, p[1], h], toks[i][0] == "round" ? min(column_w, p[1]) / 2 : ri);
            // hollow under the raised floor, with a peaked roof (no bridging)
            if (fz - pocket_floor_t > fz0 + 1)
                translate([column_x, p[0], fz0]) tent_bays([column_w, p[1]], fz - pocket_floor_t - fz0, bay_max_w, divider_t, ri);
            // finger notch through the outer wall, flat-bottomed at the pocket floor (small rounded corners)
            nz = fz + finger_notch_keep;
            translate([w - wall - 1, yc, 0]) hull() {
                for (s = [-1, 1]) translate([0, s * (finger_notch_w / 2 - notch_corner_r), nz + notch_corner_r])
                    rotate([0, 90, 0]) cylinder(r = notch_corner_r, h = wall + 2, $fn = 24);
                translate([0, -finger_notch_w / 2, h]) cube([wall + 2, finger_notch_w, 1]);
            }
        }

        // leftover column space at the front (Eyrie, Vagabond): closed over flush with the rim so
        // nothing falls in, hollow underneath with a peaked roof (no bridging)
        if (spare > 5) translate([column_x, wall, fz0]) tent_bays([column_w, spare], h - pocket_floor_t - fz0, bay_max_w, divider_t, ri);
    }
}

// Extra pocket walled off in the warrior bin's back-left corner (Marquise score marker): a solid
// corner block from the bin floor to the rim, with the pocket, its peaked-roof hollow and a finger
// notch through the left outer wall cut into it.
module bin_pocket_block(f) {
    s = bin_pocket_size();
    o = bin_pocket_origin();
    for (t = bin_corner_tokens(f))
        translate([wall - eps, o[1] - divider_t, bin_floor_z(f) - eps])
            cube([s + divider_t + eps, s + divider_t + eps, faction_box_h - bin_floor_z(f) + eps]);
}

module bin_pocket_cuts(f) {
    s = bin_pocket_size();
    o = bin_pocket_origin();
    ri = corner_r - wall;
    for (t = bin_corner_tokens(f)) {
        fz = faction_box_h - token_headroom - t[1] * token_t;
        translate([o[0], o[1], fz]) rbox([s, s, faction_box_h], ri);
        translate([o[0], o[1], bin_floor_z(f)]) tent_bays([s, s], fz - pocket_floor_t - bin_floor_z(f), bay_max_w, divider_t, ri);
        translate([-1, o[1] + s / 2, 0]) hull() {
            for (sg = [-1, 1]) translate([0, sg * (finger_notch_w / 2 - notch_corner_r), fz + notch_corner_r])
                rotate([0, 90, 0]) cylinder(r = notch_corner_r, h = wall + 2, $fn = 24);
            translate([0, -finger_notch_w / 2, faction_box_h]) cube([wall + 2, finger_notch_w, 1]);
        }
    }
}

module faction_top(f) {
    assert(finger_notch_w < square_tile, "finger notch must be narrower than the tokens");
    assert(min([for (ok = pin_post_fits(f)) ok ? 1 : 0]) == 1, str(f, ": a pin post doesn't fit under its pocket floor"));
    z0 = base_h(f);
    difference() {
        union() {
            faction_top_shell(f);
            // posts for the token-side pin holes, standing in the pocket hollows
            // (the bin-side holes go into the bin's raised solid floor)
            for (p = pin_positions()) if (in_column(p)) translate([p[0], p[1], top_floor_z(f) - eps])
                cylinder(d = boss_d(), h = boss_top(f) - top_floor_z(f) + eps, $fn = 48);
            bin_pocket_block(f);
        }
        bin_pocket_cuts(f);
        // pin holes from the underside, with a chamfered mouth
        for (p = pin_positions()) translate([p[0], p[1], z0]) {
            translate([0, 0, -1]) cylinder(d = pin_d + pin_fit, h = 1 + pin_h + pin_hole_extra, $fn = 48);
            translate([0, 0, -eps]) cylinder(d1 = pin_d + pin_fit + 2 * pin_hole_chamfer, d2 = pin_d + pin_fit, h = pin_hole_chamfer, $fn = 48);
        }
    }
}

translate(in_layout ? faction_pos(faction) : [0, 0, 0])
    color(faction_color(faction)) faction_top(faction);
