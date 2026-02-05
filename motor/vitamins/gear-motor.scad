use <../vendor/gear.scad>
$fn=50;


// measurements
motor_outer_length = 23.5;
motor_inner_length = 27;
// dimple = 29
// 30.6
// 40.5 shaft to dimple
// dimple is 2mm. 38.5
motor_outer_diameter = 23.75;
motor_inner_diameter = 18.75;
keep_out_diameter = 8.4;
shaft_length = 38.5;
motor_terminal_height = 3.45;
motor_terminal_width = 2;
motor_terminal_length = 5;
motor_dimple_diameter = 8.45;
dimple_height = 2;
term2term = 19.3;

// derived constants
motor_outer_radius = motor_outer_diameter/2;
motor_inner_radius = motor_inner_diameter/2;
terminal_center = term2term/2 - motor_terminal_width/2;


module motorTerminal() {
    translate([0,terminal_center,-motor_terminal_length/2])
    cube([motor_terminal_height, motor_terminal_width, motor_terminal_length], center=true);
}

module motorBody() {
    cylinder(h=motor_outer_length, r=motor_outer_radius);
    cylinder(h=motor_inner_length, r=motor_inner_radius);
    
    motorTerminal();
    
    mirror([0,1,0])
    motorTerminal();
    
    translate([0,0,-dimple_height])
    cylinder(h=dimple_height, r=motor_dimple_diameter/2);
}

module motorShaft() {

    // motor shaft
    
    cylinder(h=shaft_length, r=1);

    // motor gear
    translate([0,0,shaft_length-5])
    spur_gear (modul=0.5, tooth_number=10, width=5, bore=0, helix_angle=0, optimized=true);
}

module motor() {
    motorBody();
    motorShaft();
}

module motor_wire_jumper () {
    wire_width = 1;
    wire_length = 6;
    holder_width = 2.8;
    
    translate([0,0,wire_length/2])
    cube([wire_width, wire_width, wire_length], center=true);

    translate([0,0,wire_length+3-0.01])
    cube([holder_width, holder_width, 6], center=true);
}

//motor();