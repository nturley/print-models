include <../vendor/gear.scad>

module gear2() {
    spur_gear (modul=0.5, tooth_number=10, width=5, bore=0, helix_angle=0, optimized=true);
    
    difference() {
        cylinder(h=12.3,r=2);
        
        translate([-2.5,1,7.01])
        cube([5,3,5]);
    }
}
gear2();