$fn=40;


rotate([90,0,0]) {

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

// big female plate
plate_thickness = 5;
translate([4, -plate_thickness, 0])
cube([10, plate_thickness, 12]);

// little plate
translate([0,-5,0])
cube([4.5, 2, 4]);

// little plate
translate([0,-5,8])
cube([4.5, 2, 4]);



rotate([0,0,180]) {
// male hinge cylinder middle
// 1-fill, 1 gap, 2, 4, 2, 1 gap, 1 fill.
translate([0, 0, 2])
cylinder(8, r=2.8);

// thin rect from male hinge
translate([0, 0.1, 4.5])
cube([10, 4.5, 3]);
    
translate([-.5, 2.4, 4.5])
cylinder(3, r=2.2);

// big contact plate from male hinge
translate([5.5, 0.1, 0])
cube([8.5, 4.5, 12]);
}


}