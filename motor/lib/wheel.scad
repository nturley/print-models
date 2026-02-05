module wheel(big_holes=true) {
    difference() {
        cylinder(h=4, r=14);
        if (big_holes) {
            for (i=[0:1:4]) {
                rotate([0,0,90*i])
                translate([8,0,-0.01])
                cylinder(h=4.02, r=4.5);
            }
        } else {
            for (i=[0:1:9]) {
                rotate([0,0,45*i])
                translate([10.7,0,-0.01])
                cylinder(h=4.02, r=2);
            }
        }
    }
}