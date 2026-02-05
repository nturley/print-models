include <../lib/wheel.scad>

module driveWheel() {
    difference() {
        wheel();
        
        translate([0,0,-0.01])
        cylinder(h=4.02, r=2);
    }
    
    translate([-2.5,1,0])
    cube([5,2,4]);
    
    difference() {
        translate([0,0,4])
        cylinder(h=10, r=3.4);
        
        translate([0,0,3.99])
        cylinder(h=10.02, r=2.6);
    }
}

driveWheel();