
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



module crossDowel() {
    difference() {
        translate([0,0,1])
        rotate([45,0,0])
        difference() {
            intersection() {
                cube([dowel_length, 12, 12], center=true);
                rotate([45, 0, 0])
                cube([dowel_length+2*epsilon, 2, 20], center=true);
            }
            translate([dowel_length/2,0,0])
            rotate([-45, 0, 0])
            cube([dowel_length+2*epsilon, 2, 20], center=true);
        }

        for (i=[0:10]) {
            translate([i*20-100,0,0])
            rotate([0,45,0])
            cube([.4, 100, .4], center=true);
        }

        for (i=[0:10]) {
            translate([i*20-100,0,2])
            rotate([0,45,0])
            cube([.4, 100, .4], center=true);
        }
    }
}

crossDowel();