include <../vendor/gear.scad>

module gear1() {
    spur_gear (modul=0.5, tooth_number=24, width=5, bore=4.2, helix_angle=0, optimized=false);
    translate([-2.5,1,0])
    cube([5,3,5]);
}

gear1();