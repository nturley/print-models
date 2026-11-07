include <../vitamins/gear-motor.scad>
use <../vitamins/switch.scad>

epsilon=.001;

//parameters
enclosure_thickness = 1;

// derived constants
enclosure_outer_radius = motor_outer_radius + enclosure_thickness;
enclosure_inner_radius = motor_inner_radius + enclosure_thickness;
enclosure_outer_height = motor_outer_length + 2*enclosure_thickness;
enclosure_inner_height = motor_inner_length + 2*enclosure_thickness;

module enclosure() {
    cylinder(h=enclosure_outer_height, r=enclosure_outer_radius);
    cylinder(h=enclosure_inner_height, r=enclosure_inner_radius);
    
    translate([0,-enclosure_outer_radius+9.87,(shaft_length+enclosure_thickness)/2])
    cube([24,20,shaft_length+enclosure_thickness], center=true);
}

module cradle() {
    difference() {
        translate([0,0,13])
        rotate([90,0,0])
        difference() {
            enclosure();
            
            translate([0,0,enclosure_thickness])
            rotate([0,0,90])
            motorBody();
            
            translate([-20,-keep_out_diameter/2,-.01])
            cube([40,40,40]);
            
            
        }
    
    
        translate([8.5,-shaft_length+5-enclosure_thickness+.7,enclosure_outer_radius])
        rotate([90,0,0])
        cylinder(h=6, r=7);
    }
}

module cradleWall() {
    difference() {
        translate([5,-shaft_length-2-enclosure_thickness,0])
        cube([7,2,17]);
        
        translate([8.5,-shaft_length+5,enclosure_outer_radius])
        rotate([90,0,0])
        cylinder(h=10, r=2);
    }
}

module frame() {
    difference() {
        union() {
            cradle();
            cradleWall();
            }
            
        translate([9.4,2,2.6])
        rotate([90,0,0])
        cylinder(h=enclosure_outer_height+25, r=2);
        
        for (i = [0:1:3]) {
            translate([0, -10 * i, 0])    
            rotate([45, 0, 0])
            cube([50, .4, .4], center=true);
        }
        
        for (i = [0:1:2]) {
            translate([-10*i+10, -20, 0])    
            rotate([45, 0, 90])
            cube([50, .4, .4], center=true);
        }

        translate([-13,-40,-1])
        scale([1.4,1,1])
        cylinder(h=10, r=10);
    }
    
    difference() {
        freeWheelClips();
        
        for (i = [0:1:2]) {
            translate([-8*i-30, -20, 0])    
            rotate([45, 0, 90])
            cube([50, .4, .4], center=true);
        }
    }

    difference() {
        translate([-30,-27,0])
        cube([18,20,3]);

        translate([-30,-27,-epsilon])
        scale([2.75,1,1])
        cylinder(h=3+2*epsilon, r=6.5);

        translate([-30,-7,-epsilon])
        scale([2.75,1,1])
        cylinder(h=3+2*epsilon, r=6.5);
    }

    translate([-21, -17, 3])
    cylinder(h=1.5, r=.9);
    

    translate([18.5,-17,2.5])
    cube([13,20,5], center=true);

    translate([23.5,-17,13])
    difference() {
        cube([3,20,26], center=true);

        rotate([0,90,0])
        translate([-17,0,-2.5])
        cylinder(h=5, r=9.4);
    }

    translate([14,-17,13])
    difference() {
        cube([3,20,26], center=true);

        rotate([0,90,0])
        translate([-17,0,-2.5])
        cylinder(h=5, r=9.4);
    }
}


module wire_holder() {
    difference() {
        translate([0,0,6])
        cube([3.5, 3.5, 7], center=true);
        
        motor_wire_jumper();
    }
}

module freeWheelClips() {
    translate([-48,-15,0])
    cube([18,1.4,3]);
    
    translate([-46,-15,1.5])
    difference() {
        sphere(1.5);
        
        translate([-2,0,-2])
        cube([5,5,5]);
    }
    
    translate([-48,-20.6,0])
    cube([18,1.4,3]);
    
    translate([-46,-19.2,1.5])
    mirror([0,1,0])
    difference() {
        sphere(1.5);
        
        translate([-2,0,-2])
        cube([5,5,5]);
    }
}

frame();

