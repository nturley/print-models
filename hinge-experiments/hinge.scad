$fn=40;

module hinge() {
    flap_length = 5;
    flap_thickness = 8;
    min_flap_thickness = 5;

    
    translate([0,6,5])
    rotate([90,0,0]) {
        
        
        // female hinge cylinder bottom cap
        // bottom is filled 1, then 3 is empty
        difference() {
            cylinder(4, r=5);

            translate([0,0,1])
            cylinder(4, r=3);
        }

        // female hinge cylinder top cap
        // top is filled 1, then 3 is empty
        // hovering 4mm above the bottom female cylinder
        difference() {
            translate([0, 0, 8])
            cylinder(4, r=5);

            translate([0, 0, 7])
            cylinder(4, r=3);
        }

        // female flap
        
        translate([4, -flap_thickness, 0])
        cube([flap_length, flap_thickness, 12]);

        // connect flap to cylinder
        translate([-5,-flap_thickness,0])
        cube([9.5, flap_thickness - 3, 4]);
        
        //square off corner
        translate([-5,-5,0])
        cube([2, 5, 4]);

        // connect flap to cylinder
        translate([-5,-flap_thickness,8])
        cube([9.5, flap_thickness - 3, 4]);
        
        translate([-5,-5,8])
        cube([2, 5, 4]);
        //square off corner



        // open position
        rotate([0,0,180]) {
            // male hinge cylinder middle
            // 1-fill, 1 gap, 2, 4, 2, 1 gap, 1 fill.
            translate([0, 0, 2])
            cylinder(8, r=2.8);

            // thin rect to connect flap to cylinder
            translate([-3.5, 0, 4.5])
            cube([11, min_flap_thickness, 3]);

            // flap from male hinge
            translate([5.5, 0, 0])
            cube([flap_length, flap_thickness, 12]);
        }
        
        
    }
}

hinge();