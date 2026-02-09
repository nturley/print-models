$fn=20;

use <parts/holder_leg.scad>
use <parts/crossDowel.scad>
use <parts/wire_guide.scad>
use <vitamins/spool.scad>

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





module assembly() {
    translate([total_spools_length/2,0,0])
    holder_leg();

    translate([-post_width-total_spools_length/2,0,0])
    holder_leg();


    for (i = [0:num_spools-1]) {
        translate([i*spool_span-total_spools_length/2, 0, 0])
        rotate([0, 90, 0])
        %spool();
    }

    rotate([45,180,0])
    crossDowel();

    rotate([45,0,0])
    crossDowel();

    translate([0,40,-15])
    rotate([90,0,0])
    wire_guide();
}




assembly();