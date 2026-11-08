// Faction box, top piece: warrior bin + token column, an open cup that sits on the base
// (faction-base.scad), located by two pins pressed into holes in its underside (glue optional).
// Its floor is the card slot's ceiling. Prints upright (floor on the bed).
//   - Warrior bin: 65 wide, full inside depth.
//   - Token column on the right: one pocket per stack, floor raised so the stack ends just below
//     the rim (hollow underneath), and a finger notch in the outer wall beside it.
//   - Pin holes go up into small posts inside the pocket hollows.
//   - No lid: in the box, the board stack caps every tray.
//   - Rounded corners and a grooved underside (anti-warp texture), except over the card slot.
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

        // warrior bin, full inside depth
        translate([wall, wall, fz0]) rbox([bin_w, d - 2 * wall, h], ri);

        for (i = [0 : len(pockets) - 1]) {
            p = pockets[i];
            fz = pocket_floor_z(f, toks[i]);
            yc = p[0] + p[1] / 2;
            // pocket, from its raised floor up through the rim
            translate([column_x, p[0], fz]) rbox([column_w, p[1], h], ri);
            // hollow under the raised floor
            if (fz - pocket_floor_t > fz0 + 1)
                translate([column_x, p[0], fz0]) rbox([column_w, p[1], fz - pocket_floor_t - fz0], ri);
            // finger notch through the outer wall, rounded at the bottom
            nz = fz + finger_notch_keep;
            translate([w - wall - 1, yc, 0]) hull() {
                translate([0, 0, nz + finger_notch_w / 2]) rotate([0, 90, 0]) cylinder(d = finger_notch_w, h = wall + 2, $fn = 48);
                translate([0, -finger_notch_w / 2, h]) cube([wall + 2, finger_notch_w, 1]);
            }
        }

        // spare compartment at the front of the column, if the tokens leave room
        if (spare > 5) translate([column_x, wall, fz0]) rbox([column_w, spare, h], ri);

        // anti-warp texture on the underside, kept off the card slot ceiling
        translate([0, 0, z0]) difference() {
            warp_relief([w, d], relief_pitch, relief_bar);
            translate([wall - 0.5, d - wall - card_slot_l - 0.5, -1]) cube([card_slot_w + 1, card_slot_l + wall + 2, 2]);
        }
    }
}

module faction_top(f) {
    assert(min([for (ok = pin_post_fits(f)) ok ? 1 : 0]) == 1, str(f, ": a pin post doesn't fit under its pocket floor"));
    z0 = base_h(f);
    difference() {
        union() {
            faction_top_shell(f);
            // posts for the pin holes, standing in the pocket hollows
            for (p = pin_positions()) translate([p[0], p[1], top_floor_z(f) - eps])
                cylinder(d = boss_d(), h = boss_top(f) - top_floor_z(f) + eps, $fn = 48);
        }
        // pin holes from the underside, with a chamfered mouth
        for (p = pin_positions()) translate([p[0], p[1], z0]) {
            translate([0, 0, -1]) cylinder(d = pin_d + pin_fit, h = 1 + pin_h + pin_hole_extra, $fn = 48);
            translate([0, 0, -eps]) cylinder(d1 = pin_d + pin_fit + 2 * pin_hole_chamfer, d2 = pin_d + pin_fit, h = pin_hole_chamfer, $fn = 48);
        }
    }
}

translate(in_layout ? faction_pos(faction) : [0, 0, 0])
    color(faction_color(faction)) faction_top(faction);
