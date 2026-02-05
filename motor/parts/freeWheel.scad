include <../lib/wheel.scad>

module freeWheel() {
    difference() {
        wheel();
        
        translate([0,0,-0.01])
        cylinder(h=4.02, r=1.5);
        
    }
}

freeWheel();