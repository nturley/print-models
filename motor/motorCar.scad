$fn=50;

include <vitamins/gear-motor.scad>
include <vitamins/batteryAA.scad>
use <vitamins/batteryAAHolder.scad>
use <parts/driveShaft.scad>
use <parts/driveWheel.scad>
use <parts/frame.scad>
use <parts/freeWheel.scad>
use <parts/gear1.scad>
use <parts/gear2.scad>

//parameters
enclosure_thickness = 1;

// derived constants
enclosure_outer_radius = motor_outer_radius + enclosure_thickness;
enclosure_inner_radius = motor_inner_radius + enclosure_thickness;
enclosure_outer_height = motor_outer_length + 2*enclosure_thickness;
enclosure_inner_height = motor_inner_length + 2*enclosure_thickness;

module motorCar() {

    frame();
    
    translate([0,-1,13.5])
    rotate([90,90,0])
    %motor();

    translate([8.5,-shaft_length+4.3,enclosure_outer_radius])
    rotate([90,0,0])
    gear1();

    translate([8.5,-shaft_length+5-13,enclosure_outer_radius])
    rotate([270,0,0])
    gear2();

    rotate([270,0,0])
    translate([9.4,-2.6,-50.6])
    driveShaft();
    
    translate([9.4,14.2,2.4])
    rotate([90,180,0])
    driveWheel();
    
    translate([-46,-15,1.5])
    rotate([90,0,0])
    freeWheel();
    
    //translate([-21,-42,10])
    //rotate([270,0,0])
    //%batteryAA();

    translate([-12.5,-45.5,3])
    rotate([0,0,90])
    %batteryAAHolder();
}

motorCar();
