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

// Which part to render: "all" for the whole car, or one part name to render just
// that part in its assembled position (used by the tests:
// openscad -D 'part="gear1"' -o gear1.stl motorCar.scad).
// Vitamins render as real geometry when selected, as % background otherwise.
part = "all";

function show(name) = part == "all" || part == name;

module motorCar() {

    if (show("frame"))
    frame();

    if (part == "motor") placeMotor() motor();
    else if (part == "all") placeMotor() %motor();

    if (show("gear1"))
    translate([8.5,-shaft_length+4.3,enclosure_outer_radius])
    rotate([90,0,0])
    rotate([0,0,180]) // line the key up with gear2's slot
    gear1();

    if (show("gear2"))
    translate([8.5,-shaft_length+5-13,enclosure_outer_radius])
    rotate([270,0,0])
    gear2();

    if (show("driveShaft"))
    rotate([270,0,0])
    translate([9.4,-2.6,-50.6])
    driveShaft();

    if (show("driveWheel"))
    translate([9.4,14.2,2.4])
    rotate([90,180,0])
    driveWheel();

    if (show("freeWheel"))
    translate([-46,-15,1.5])
    rotate([90,0,0])
    freeWheel();

    //translate([-21,-42,10])
    //rotate([270,0,0])
    //%batteryAA();

    if (part == "batteryAAHolder") placeBatteryHolder() batteryAAHolder();
    else if (part == "all") placeBatteryHolder() %batteryAAHolder();
}

module placeMotor() {
    translate([0,-1,13.5])
    rotate([90,90,0])
    children();
}

module placeBatteryHolder() {
    translate([-12.5,-45.5,3])
    rotate([0,0,90])
    children();
}

motorCar();
