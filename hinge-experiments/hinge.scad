$fn=40;


// female hinge cylinder bottom
// bottom is filled 1, then 3 is empty
difference() {
    cylinder(4, r=5);

    translate([0,0,1])
    cylinder(4, r=3);
}

// female hinge cylinder top
// top is filled 1, then 3 is empty
// hovering 4mm above the bottom female cylinder
difference() {
    translate([0, 0, 8])
    cylinder(4, r=5);

    translate([0, 0, 7])
    cylinder(4, r=3);
}

// female plate
translate([4, -2.6, 0])
cube([10, 2.5, 12]);


// male hinge cylinder middle
// 1-fill, 1 gap, 2, 4, 2, 1 gap, 1 fill.
translate([0, 0, 2])
cylinder(8, r=2.8);

// thin rect from male hinge
translate([0, 0.1, 4.5])
cube([10, 2.5, 3]);

// big contact plate from male hinge
translate([5.5, 0.1, 0])
cube([8.5, 2.5, 12]);



