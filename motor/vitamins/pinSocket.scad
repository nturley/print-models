
epsilon = .001;

module pinSocket(num_pins=2) {

    for (i = [0:num_pins-1]) {
        translate([2.5/2, 2.54/2+2.54*i, -3.15/2])
        cube([.4, .64, 3.15], center=true);
    }

    difference() {
        cube([2.5, 2.54*num_pins, 8.5]);

        for (i = [0:num_pins-1]) {
            translate([2.5/2, 2.54/2+2.54*i, 8.5-4+epsilon])
            cube([1.2, 1.2, 8], center=true);
        }

    }
}

pinSocket();