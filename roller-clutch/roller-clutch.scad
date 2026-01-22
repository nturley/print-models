$fn = 50;

num_rollers = 9;
angle_step = 360 / num_rollers;
height = 4;
delta_height = .2;
roller_radius = 2.2;

// extrude a 2D shape into a 3D shape with a skinny waist
// We angle in at 45 degrees and then outward at 45 degrees
module treedee() {
    hull() {
        // turn a 2D shape into a flat 3d shape
        linear_extrude(delta_height)
        children();
        
        // skinnier version at the "skinny waist".
        translate([0,0,height/2])
        linear_extrude(delta_height)
        // inward offset by half height to get a 45 degree angle
        offset(r=-height/3)
        children();
    }
    // repeat going from the top to the middle
    hull() {
        translate([0,0,height])
        linear_extrude(delta_height)
        children();
        
        translate([0,0,height/2])
        linear_extrude(delta_height)
        offset(r=-height/3)
        children();
    }
}

// hour glass shaped roller
module Roller() {
    treedee() {
        circle(r=roller_radius);
    }
}

module OuterWheel() {
    difference() {
        cylinder(h=height, r=25);
        
        translate([0,0,-.1])
        scale([1,1,1.1])
        treedee() {
            circle(r=21.2);
        }
    }
}

// the roller hole will be at a large radius in disengaged position
// and a small radius in the jammed position.
module RollerHole() {
    num_circles = 6;
    outer_radius = 20;
    start_radius = 3.4;
    radius_decrease = .3;
    // end_radius = start_radius - 6*.6
    

    // Create hulls between consecutive circles
    for (i = [0 : num_circles - 2]) {
        angle_i = i * angle_step*.6 / num_circles;
        angle_next = (i + 1) * angle_step*.6 / num_circles;
        
        radius_i = start_radius - i * radius_decrease;
        radius_next = start_radius - (i + 1) * radius_decrease;
        
        // Position centers so outer edges touch the boundary circle
        center_dist_i = outer_radius - radius_i;
        center_dist_next = outer_radius - radius_next;
        
        pos_i = [center_dist_i * cos(angle_i), center_dist_i * sin(angle_i)];
        pos_next = [center_dist_next * cos(angle_next), center_dist_next * sin(angle_next)];
        
        treedee() {
            hull() {
                translate(pos_i)
                    circle(r=radius_i);
                translate(pos_next)
                    circle(r=radius_next);
            }
        }
    }
}

module InnerWheel() {
    difference() {
        treedee() {
            circle(r=20.4);
        }
        
        translate([0,0,-1])
        cylinder(h=height+2, r=14);
        
        for (i = [0:num_rollers-1]) {    
            rotate([0,0,i*angle_step])
            translate([2.4,0,-.1])
            scale([1,1,1.1])
            RollerHole();
        }
    }
}

module Rollers() {
    for (i = [0:num_rollers-1]) {    
        rotate([0,0,angle_step * i])
        translate([18.4,0,0])
        Roller();
    }
}

module Clutch() {
    OuterWheel();
    InnerWheel();
    Rollers();
}

Clutch();