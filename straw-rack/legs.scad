$fn=40;

// Rack Legs
// leg cylinder: 4.2mm * 0.7 = 2.94mm radius, 114mm * 0.7 = 80mm tall
// rounded foot cylinder: ~10mm radius


for (i=[0:3]) {
    translate([40*i-60,0,0])

    // I made it too big so I just scaled it down 70%
    scale([0.7, 0.7, 0.7]){

        // rotate extrude a rounded rect for the foot
        translate([0,0,-2]) // align the bottom at z=0
        rotate_extrude()
        translate([8, 5, 0]) // rotate_extrude likes things only on one side of the axis
        offset(2) //turn into a rounded rect
        square([8.5, 2], center=true); // wider than tall
        
        // this is the leg, and covers up the donut hole.
        cylinder(114, r=4.2);
    }
}