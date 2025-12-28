$fn=20;

// The top tray of the straw rack

// PARAMETERS

// rack thickness
depth = 6;

// holes for the legs to insert into the rack
feet_radius = 3;
// distance from edge
foot_inset = 1.7;

hole_rows = 4;
hole_cols = 6;
// min distance between holes
hole_gap = 1.5;
// distance from edge of outside holes to edge of rack
outer_gap = 6;
hole_radius = 8;

// DERIVED VALUES
// hole to hole gaps
num_gaps_x = hole_cols - 1;
num_gaps_y = hole_rows - 1;

hole_diameter = hole_radius * 2;
// rack dimensions
width = hole_cols * hole_diameter + outer_gap * 2 + num_gaps_x * hole_gap;
height = hole_rows * hole_diameter + outer_gap * 2 + num_gaps_y * hole_gap;

top_y = -height / 2;
left_x = -width / 2;
hole_span = hole_radius * 2 + hole_gap;

top_hole_center_y = top_y + outer_gap + hole_radius;
left_hole_center_x = left_x + outer_gap + hole_radius;

// COMPONENTS
difference() {
    cube([width, height, depth], center=true);
    
    for (hole_row=[0:hole_rows-1]) {
        hole_y = top_hole_center_y + hole_row * hole_span;
        for (hole_col=[0:hole_cols-1]) {
            hole_x = left_hole_center_x + hole_col * hole_span;
            translate([hole_x, hole_y, -depth]) {
                cylinder(depth*2, r=hole_radius);
            }
        }
    }
    
    for (foot_num=[0:3]) {
        row = foot_num % 2;
        col = floor(foot_num / 2);
        x = left_x + feet_radius + foot_inset + (width-feet_radius * 2-foot_inset*2) * row;
        y = top_y+feet_radius + foot_inset + (height-feet_radius*2-foot_inset*2) * col;
        translate([x, y, -depth / 2+1]) {
            cylinder(depth, r=feet_radius);
        }
    }
}