

// measurements


module batteryAAHolder() {
    holder_length = 57;
    holder_width = 17;
    holder_height = 13.8;
    center_hole_to_top = 5.5;
    mount_hole_diameter = 2.5;

    cut_out_bottom = 5.5;
    middle_cut_out_width = 20;

    top_cutout_width = 8;

    thickness = 1.5;
    circle_thickness = .8;

    episilon = .001;

    circle_radius = holder_width/2;
    circle_z = holder_height - circle_radius;

    difference() {
        cube([holder_length, holder_width, circle_z]);
        
        translate([thickness, thickness, thickness])
        cube([holder_length-2*thickness, holder_width-2*thickness, circle_z]);

        translate([holder_length/2, holder_width/2,-episilon])
        cylinder(h=10, r=mount_hole_diameter/2);
    }
    
    difference() {
        translate([0,holder_width/2,circle_z])
        rotate([0,90,0])
        cylinder(h=holder_length, r=holder_width/2);

        translate([thickness,holder_width/2,circle_z])
        rotate([0,90,0])
        cylinder(h=holder_length-thickness*2, r=holder_width/2-thickness);

        translate([-episilon,0,-10+circle_z])
        cube([holder_length+2*episilon, holder_width, 10]);

        translate([holder_length/2-middle_cut_out_width/2, 0, circle_z-episilon])
        cube([middle_cut_out_width, holder_width, 10]);

        translate([thickness, holder_width/2-top_cutout_width/2, 0])
        cube([holder_length-thickness*2, top_cutout_width, 20]);

    }

}

batteryAAHolder();