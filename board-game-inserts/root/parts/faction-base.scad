// Faction box, bottom piece: the card slot. Solid apart from the slot, so its whole top is a flat
// face against the top piece (faction-top.scad), with two alignment pins that press into holes in it.
// The slot is open at the back so the faction cards slide in and out sideways; the top piece's
// smooth bed-side floor is the slot's ceiling, so nothing bridges. Prints upright, no overhangs.
// Rounded corners and a grooved bottom (anti-warp texture) keep the thin slab flat on the bed.
// Render one with:  openscad -D 'faction="eyrie"' -o eyrie-base.stl faction-base.scad
include <../constants.scad>
use <../lib/faction-layout.scad>
use <../../lib/print.scad>

faction = "marquise";
in_layout = true;   // place at its position in the insert (false: at the origin)

module faction_base(f) {
    w = faction_box_w;
    d = faction_box_d;
    h = base_h(f);
    slot_y = d - wall - card_slot_l;
    cx = wall + card_slot_w / 2;

    difference() {
        rbox([w, d, h], corner_r);

        // card slot, open through the back wall
        translate([wall, slot_y, floor_t]) rbox([card_slot_w, card_slot_l + wall + 1, h], corner_r - wall);

        // pinch notch through the floor at the slot opening
        translate([0, 0, -1]) hull() {
            translate([cx, d - pinch_notch_l + pinch_notch_w / 2, 0]) cylinder(d = pinch_notch_w, h = floor_t + 2, $fn = 64);
            translate([cx - pinch_notch_w / 2, d - 1, 0]) cube([pinch_notch_w, 2, floor_t + 2]);
        }

        // push hole under the closed end of the slot
        translate([cx, slot_y + card_push_hole_d / 2 + 4, -1]) cylinder(d = card_push_hole_d, h = floor_t + 2, $fn = 64);

        // anti-warp texture on the bottom
        warp_relief([w, d], relief_pitch, relief_bar);
    }

    // alignment pins, chamfered at the tip
    for (p = pin_positions()) translate([p[0], p[1], h - eps]) {
        cylinder(d = pin_d, h = pin_h - pin_chamfer + eps, $fn = 48);
        translate([0, 0, pin_h - pin_chamfer + eps]) cylinder(d1 = pin_d, d2 = pin_d - 2 * pin_chamfer, h = pin_chamfer, $fn = 48);
    }
}

translate(in_layout ? faction_pos(faction) : [0, 0, 0])
    color(faction_color(faction)) faction_base(faction);
