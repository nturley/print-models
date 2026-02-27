include <../constants.scad>

module InnerRace() {
    race_bottom = ball_r;
    race_top = ball_r + cage_top_extension + race_top_extension;
    race_h = race_bottom + race_top;
    inner_race_or = pitch_r - race_bore_offset;
    inner_race_ir = pitch_r - ball_r - race_inner_wall;

    difference() {
        translate([0, 0, -race_bottom])
            cylinder(h = race_h, r = inner_race_or, $fn = 64);
        translate([0, 0, -race_bottom - epsilon])
            cylinder(h = race_h + 2 * epsilon, r = inner_race_ir, $fn = 64);
        rotate_extrude($fn = 64)
            translate([pitch_r, 0, 0])
                circle(r = groove_r, $fn = 32);
    }
}

InnerRace();