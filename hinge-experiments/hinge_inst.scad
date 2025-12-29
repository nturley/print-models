use <hinge.scad>


module big_tray() {
    translate([10,-35,3])
    cube([30,70,10]);
}

difference() {
    translate([0,-20,5])
    hinge();
    
    big_tray();
    
    translate([-50,0,0])
    big_tray();
}

difference() {
    translate([0,20,5])
    hinge();
    
    big_tray();
    
    translate([-50,0,0])
    big_tray();
}
difference() {
    translate([5,-40,0])
    cube([40,80,10]);
    
    big_tray();

}

difference() {
    translate([-45.5,-40,0])
    cube([40,80,10]);
    
    translate([-50,0,0])
    big_tray();
}