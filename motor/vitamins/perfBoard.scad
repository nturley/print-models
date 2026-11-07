$fn = 50;

//measurements

perfBoardWidth = 44;
perfBoardLength = 39;
perfBoardHeight = 1.6;
holeEdgeToEdgeLengthY = 30;
holeEdgeToEdgeLengthX = 35;
holeDiameter = 3;
connectHoleDiameter = 1;

holeRadius = holeDiameter/2;
connectHoleRadius = connectHoleDiameter/2;

edgeToHoleCenter = (perfBoardWidth - holeEdgeToEdgeLengthX)/6 + holeRadius;
farHoleX = perfBoardWidth - edgeToHoleCenter;
farHoleY = perfBoardLength - edgeToHoleCenter;

epsilon = .01;

module perfBoard() {
    module mountingHole() {
        translate([0, 0, -epsilon])
        cylinder(h=perfBoardHeight + 2 * epsilon, r=holeRadius);
    }

    module connectHole() {
        translate([0, 0, -epsilon])
        cylinder(h=perfBoardHeight + 2 * epsilon, r=connectHoleRadius);
    }

    difference() {
        cube([perfBoardWidth, perfBoardLength, perfBoardHeight]);

        translate([edgeToHoleCenter, edgeToHoleCenter, 0])
        mountingHole();

        translate([farHoleX, edgeToHoleCenter, 0])
        mountingHole();

        translate([farHoleX, farHoleY, 0])
        mountingHole();

        translate([edgeToHoleCenter, farHoleY, 0])
        mountingHole();

        hole_spacing = 2.54;
cols = 15;
rows = 12;

margin_x = (perfBoardWidth - (cols - 1) * hole_spacing) / 2;
margin_y = (perfBoardLength - (rows - 1) * hole_spacing) / 2;

for (i=[0:cols-1]) {
    for (j=[0:rows-1]) {
        // Skip the four corners
        if (!((i==0 || i==cols-1) && (j==0 || j==rows-1))) {
            translate([margin_x + i*hole_spacing, margin_y + j*hole_spacing, 0])
            connectHole();
        }
    }
}
    }
}

perfBoard();
