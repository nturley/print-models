// Print helpers shared by the board game inserts.

// Box with rounded vertical edges, from the origin like cube(). r <= 0 gives a plain cube.
module rbox(size, r, fn = 32) {
    if (r <= 0) cube(size);
    else hull() for (x = [r, size[0] - r], y = [r, size[1] - r])
        translate([x, y, 0]) cylinder(r = r, h = size[2], $fn = fn);
}

// Closed hollow (to subtract) whose ceiling is a 45° peaked roof running along y, like a tent,
// so it prints without bridging: straight sides, then two slopes meeting in a ridge at height h.
// size: [w, l]; the roof needs w/2 of height. If h is less than that, the ridge is left flat
// (a short bridge, w - 2h wide).
module tent_hollow(size, h, r = 0) {
    w = size[0];
    l = size[1];
    eave = h - w / 2;   // height where the roof starts
    profile = eave >= 0
        ? [[0, 0], [w, 0], [w, eave], [w / 2, h], [0, eave]]   // house shape, sharp ridge
        : [[0, 0], [w, 0], [w - h, h], [h, h]];                // too low for a full roof: flat-topped
    intersection() {
        rbox([w, l, h], r);   // keeps the rounded corners
        translate([0, l, 0]) rotate([90, 0, 0]) linear_extrude(l) polygon(profile);
    }
}

// A row of tent_hollow() bays side by side across x, separated by ribs, filling [w, l] up to
// height h. Bays are at most max_w wide, and narrow enough that each full roof fits in the height
// (a roof needs bay width / 2), so there's never a flat ridge to bridge.
module tent_bays(size, h, max_w = 22, rib = 1.2, r = 0) {
    w = size[0];
    bay = min(max_w, 2 * h);
    n = max(1, ceil((w + rib) / (bay + rib)));
    bw = (w - (n - 1) * rib) / n;
    for (i = [0 : n - 1]) translate([i * (bw + rib), 0, 0]) tent_hollow([bw, size[1]], h, r);
}

// Rounded oblong (stadium), centred on the origin: w across x, l along y.
module stadium(w, l) {
    hull() for (s = [-1, 1]) translate([0, s * (l - w) / 2]) circle(d = w, $fn = 48);
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
