include <../vendor/gear.scad>
include <../lib/wheel.scad>

module driveShaft() {
    translate([0,0,4])
    spur_gear (modul=0.5, tooth_number=31, width=5, bore=0, helix_angle=0, optimized=true);
    
    difference() {
        translate([0,0,4])
        cylinder(h=61, r=1.8);
    
        translate([-2.5,1,61])
        cube([5,3,5]);
    }
        
    wheel(big_holes=false);
}

driveShaft();