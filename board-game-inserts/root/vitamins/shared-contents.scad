// Shared deck, token stacks and dice at measured size, where they sit in the shared tray.
// Fit checks only.
include <../constants.scad>
use <../lib/shared-layout.scad>

show = "all";        // "deck", "tokens" or "all"
in_layout = true;

module die_shape() {
    // rounded d12 approximated as a sphere clipped top and bottom to the flat-to-flat height
    intersection() {
        translate([0, 0, die_flat / 2]) sphere(d = die_corner, $fn = 48);
        translate([-die_corner, -die_corner, 0]) cube([2 * die_corner, 2 * die_corner, die_flat]);
    }
}

module shared_deck_contents() {
    c = deck_centre();
    translate([c[0] - card_w / 2, c[1] - card_l / 2, deck_floor_z()]) cube([card_w, card_l, deck_h]);
}

module shared_token_contents() {
    for (p = shared_pockets()) {
        t = p[0];
        s = stack_size(t);
        translate([p[1], p[2], stack_floor_z(t)])
            if (t[0] == "dice")   // side by side, touching, centred in the slot
                for (k = [0 : t[1] - 1]) translate([(k - (t[1] - 1) / 2) * die_corner, 0, 0]) die_shape();
            else linear_extrude(stack_h(t)) {
                if (t[0] == "suit") hull() for (k = [-1, 1]) translate([0, k * (s[1] - s[0]) / 2]) circle(d = s[0], $fn = 48);
                else square(s, center = true);
            }
    }
}

translate(in_layout ? [shared_x, 0, 0] : [0, 0, 0]) {
    if (show != "tokens") shared_deck_contents();
    if (show != "deck") shared_token_contents();
}
