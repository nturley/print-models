

// measurements

module switch() {

    mid_diameter = 18.5;
    cap_diameter = 23;
    cap_height = 3;
    mid_height = 16;
    doohickey_thickness = 1;
    doohickey_widest = 23;
    mid_divot_diameter = 16.7;
    bottom_to_divot_top = 8.5;

    difference() {
        cylinder(h=mid_height, r=mid_diameter/2);

        translate([0, mid_divot_diameter/2+5,bottom_to_divot_top-2.5])
        cube([10,10,5], center=true);

        translate([0, -mid_divot_diameter/2-5,bottom_to_divot_top-2.5])
        cube([10,10,5], center=true);
    }



    translate([0,0,mid_height])
    cylinder(h=cap_height, r=cap_diameter/2);
}

switch();