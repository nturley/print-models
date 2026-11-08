// Print helpers shared by the board game inserts.

// Box with rounded vertical edges, from the origin like cube(). r <= 0 gives a plain cube.
module rbox(size, r, fn = 32) {
    if (r <= 0) cube(size);
    else hull() for (x = [r, size[0] - r], y = [r, size[1] - r])
        translate([x, y, 0]) cylinder(r = r, h = size[2], $fn = fn);
}

// Anti-warp texture for a large flat bottom: a grid of small V-grooves (square bars turned 45°
// about their length, so each cuts a diamond-shaped track) at z = 0. Subtract it from the part.
//   size: [w, d] area to cover; pitch: groove spacing; bar: bar side (groove depth = bar / sqrt(2)).
// CAUTION: not used any more. With bar = 0.4 the grooves (~0.28 deep) are deeper than a 0.2 mm
// first layer, so the slicer splits the first layer into separate islands that don't stick
// (the Root faction base failed this way on the K2's textured PEI). Keep grooves shallower than
// the first layer (bar < ~0.25) if you try it again.
module warp_relief(size, pitch = 10, bar = 0.4) {
    for (x = [pitch / 2 : pitch : size[0]])
        translate([x, size[1] / 2, 0]) rotate([0, 45, 0]) cube([bar, size[1] + 2, bar], center = true);
    for (y = [pitch / 2 : pitch : size[1]])
        translate([size[0] / 2, y, 0]) rotate([45, 0, 0]) cube([size[0] + 2, bar, bar], center = true);
}
