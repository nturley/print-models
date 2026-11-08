// Root insert assembly: the four faction boxes and the shared tray in the box cavity, with
// their contents (transparent) and the board stack that caps them (no lids).
include <constants.scad>
use <parts/faction-box.scad>
use <parts/shared-tray.scad>
use <vitamins/faction-contents.scad>
use <vitamins/shared-contents.scad>

show_boards = true;

for (f = factions) translate(faction_pos(f)) {
    color(faction_color(f)) faction_box(f);
    %faction_contents(f);
}

// shared tray (right-hand column): deck at the back, tokens and dice at the front
translate([shared_x, 0, 0]) {
    color("#b9955a") shared_tray();
    %shared_deck_contents();
    %shared_token_contents();
}

// board stack lying on top of the insert, and the box cavity floor
if (show_boards) %translate([0, 0, insert_h]) cube([insert_w, insert_d, board_stack_h]);
%translate([-(box_inner_w - insert_w) / 2, -(box_inner_d - insert_d) / 2, -0.5]) cube([box_inner_w, box_inner_d, 0.5]);
