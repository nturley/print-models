// measurements
battery_case_height = 47.5;
battery_case_diameter = 14;
negative_terminal_height = 48.76 - 47.5;
negative_terminal_diameter = 8.5;
positive_terminal_height = 50 - 48.76;
positive_terminal_diameter = 5.35;

module batteryAA() {
    translate([0,0,negative_terminal_height])
    cylinder(h=battery_case_height, r=battery_case_diameter/2);
    
    cylinder(h=negative_terminal_height, r=negative_terminal_diameter/2);

    translate([0,0,battery_case_height+negative_terminal_height])
    cylinder(h=positive_terminal_height, r=positive_terminal_diameter/2);


}

//batteryAA();