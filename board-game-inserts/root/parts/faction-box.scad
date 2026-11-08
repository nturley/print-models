// A whole faction box as glued together: base (card slot) + top (warriors and tokens).
// For viewing; print faction-base.scad and faction-top.scad separately, both upright.
include <../constants.scad>
use <faction-base.scad>
use <faction-top.scad>

faction = "marquise";
in_layout = true;

module faction_box(f) {
    faction_base(f);
    faction_top(f);
}

translate(in_layout ? faction_pos(faction) : [0, 0, 0])
    color(faction_color(faction)) faction_box(faction);
