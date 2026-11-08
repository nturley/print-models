// Root insert assembly: the four faction boxes in the box cavity, with their contents (transparent)
// and the board stack that caps them (no lids).
// The shared deck and shared trays aren't modelled yet; they're shown as outlines on the right.
include <constants.scad>
use <parts/faction-box.scad>

use <vitamins/faction-contents.scad>

show_boards = true;

for (f = factions) translate(faction_pos(f)) {
    color(faction_color(f)) faction_box(f);

    %faction_contents(f);
}

// placeholders: shared deck (back) and shared tray (front)
%translate([2 * faction_box_w, insert_d / 2, 0]) cube([insert_w - 2 * faction_box_w, insert_d / 2, insert_h]);
%translate([2 * faction_box_w, 0, 0]) cube([insert_w - 2 * faction_box_w, insert_d / 2, insert_h]);
// board stack lying on top of the insert, and the box cavity floor
if (show_boards) %translate([0, 0, insert_h]) cube([insert_w, insert_d, board_stack_h]);
%translate([-(box_inner_w - insert_w) / 2, -(box_inner_d - insert_d) / 2, -0.5]) cube([box_inner_w, box_inner_d, 0.5]);
