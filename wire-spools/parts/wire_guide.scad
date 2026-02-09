
spool_height = 20;
spool_gap = 1;
spool_inner_diameter = 25;
dowel_radius = spool_inner_diameter/2 -1;
post_width = 16;

spool_span = spool_height+spool_gap;
num_spools = 6;

epsilon = .001;

total_spools_length = spool_span * num_spools;
left_edge = -total_spools_length / 2 - post_width;
dowel_length = total_spools_length + 2 * post_width;



module wire_guide() {
    difference() {
    translate([0,0,4])
    difference() {
        cube([dowel_length, 16, 8], center=true);

        translate([0,0, 1+epsilon])
        cube([total_spools_length, 16+epsilon*2, 6], center=true);

        for (i=[0:5]) {
            translate([spool_span*(i-3)+spool_span/2,0,-5])
            cylinder(h=10, r=2);
        }

        
        
    }

    for (i=[0:10]) {
            translate([i*20-100,0,0])
            rotate([0,45,0])
            cube([.4, 100, .4], center=true);
        }
    }
}

wire_guide();