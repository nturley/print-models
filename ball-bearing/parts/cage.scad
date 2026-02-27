include <../constants.scad>

module Cage() {
    // distance from ball bottom to cage bottom
    cage_bottom_subtraction = 0.7;

    // hole is 20% larger than the ball
    pocket_conformity = 1.2;
    // distance between cage and the race
    race_cage_clearance = 0.35;
    
    cage_bottom = ball_r - cage_bottom_subtraction;
    cage_h = cage_bottom + ball_r + cage_top_extension;
    pocket_r = ball_r * pocket_conformity;
    cage_or = pitch_r + race_bore_offset - race_cage_clearance;
    cage_ir = pitch_r - race_bore_offset + race_cage_clearance;

    translate([0, 0, -cage_bottom])
    difference() {
        cylinder(h = cage_h, r = cage_or, 
                 center = false, $fn = 64);
        translate([0, 0, -epsilon])
        cylinder(h = cage_h + 2 * epsilon, r = cage_ir, 
                 center = false, $fn = 64);
        
        for (i = [0 : num_balls - 1]) {
            rotate([0, 0, i * 360 / num_balls])
                translate([pitch_r, 0, cage_bottom])
                    sphere(r = pocket_r, $fn = 32);
        }
    }
}

//rotate([180,0,0])
Cage();