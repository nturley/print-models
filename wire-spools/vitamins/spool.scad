// measurements

spool_inner_diameter = 25;
spool_outer_diameter = 54.5;
spool_height = 20;;
edge_thickness = 2;

epsilon = .001;

module spool_edge() {
        cylinder(h=edge_thickness, r=spool_outer_diameter/2);
}

module spool() {
    difference() {
        union() {
            spool_edge();

            translate([0,0,spool_height-edge_thickness])
            spool_edge();

            cylinder(h=spool_height, r=spool_inner_diameter/2+edge_thickness);
        }
        translate([0,0,-epsilon])
        cylinder(h=spool_height+2*epsilon, r=spool_inner_diameter/2);
    }
}
spool();