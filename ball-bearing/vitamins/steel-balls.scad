include <../constants.scad>

module SteelBalls() {
    // Balls
    num_balls = 8;
    for (i = [0 : num_balls - 1]) {
        rotate([0, 0, i * 360 / num_balls])
            translate([pitch_r, 0, 0])
                sphere(r = ball_r, $fn = 32);
    }
}

SteelBalls();