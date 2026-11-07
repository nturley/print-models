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





// Which part to render: "all" for the whole rack, or one part name to render just
// that part in its assembled position (used by the tests:
// openscad -D 'part="leg-left"' -o leg-left.stl spool-rack.scad).
// The spools render as real geometry when selected, as % background otherwise.
part = "all";

function show(name) = part == "all" || part == name;

module assembly() {
    if (show("leg-right"))
    translate([total_spools_length/2,0,0])
    holder_leg();

    if (show("leg-left"))
    translate([-post_width-total_spools_length/2,0,0])
    holder_leg();


    for (i = [0:num_spools-1]) {
        // + spool_gap/2 centres the row, leaving half a gap at each leg
        translate([i*spool_span-total_spools_length/2+spool_gap/2, 0, 0])
        rotate([0, 90, 0])
        if (part == "spools") spool();
        else if (part == "all") %spool();
    }

    // crossDowel() is lifted 1mm to sit on the print bed; translate([0,0,-1]) undoes
    // that so the two dowels interlock at their slots, corner to corner in the legs'
    // square holes.
    if (show("dowel-a"))
    rotate([135,0,0])
    rotate([0,180,0])
    translate([0,0,-1])
    crossDowel();

    if (show("dowel-b"))
    rotate([45,0,0])
    translate([0,0,-1])
    crossDowel();

    // centred in the legs' 8.4 x 16.4 slot (y 31.82..40.22, z -22.86..-6.46 in the
    // vendor STL), ~0.2mm clearance all round
    if (show("wire_guide"))
    translate([0,40,-14.66])
    rotate([90,0,0])
    wire_guide();
}




assembly();