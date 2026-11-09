// Shared tray: one piece filling the right-hand column of the insert (94 x 213 x 40).
//   Back half:  the 54-card deck, centred, in a pocket whose floor is raised so the deck ends just
//               below the rim, with a big finger scoop on each long side (inside the outer walls) that
//               dips below the card floor (to get under the bottom card).
//   Front half: three rows:
//     back:   one pill-shaped bowl (curved both ways) for all 12 suit markers, loose (they're irregular)
//     middle: both dice in one long slot, with a scoop at each end
//     front:  4 square stacks (supply items, ruins, 2 x blank tiles) against the front wall, each
//             with a flat-bottomed finger notch through the wall down to its pocket floor
//   Pocket floors are raised so everything ends just below the rim. Hollow underneath in
//   peaked-roof bays (no bridging), one set per half. No lid: the board stack caps it.
//   Prints upright, no supports.
include <../constants.scad>
use <../lib/shared-layout.scad>
use <../../lib/print.scad>
use <../lib/icons.scad>

in_layout = true;   // place at its position in the insert (false: at the origin)

// flat-bottomed finger notch through the front wall (y = 0), from z = fz up, centred on x
module front_notch(x, fz) {
    translate([x, -1, 0]) hull() {
        for (s = [-1, 1]) translate([s * (finger_notch_w / 2 - notch_corner_r), 0, fz + notch_corner_r])
            rotate([-90, 0, 0]) cylinder(r = notch_corner_r, h = wall + 2, $fn = 24);
        translate([-finger_notch_w / 2, 0, faction_box_h]) cube([finger_notch_w, wall + 2, 1]);
    }
}

module shared_tray() {
    w = shared_w;
    d = shared_tray_d;
    h = faction_box_h;
    ri = corner_r - wall;
    pockets = shared_pockets();
    assert(shared_min_hgap() >= 2, "a shared tray row is too wide");
    dp = deck_pocket();
    dc = deck_centre();
    dfz = deck_floor_z();
    scoops = [for (s = [-1, 1]) [dc[0] + s * dp[0] / 2, dc[1]]];
    assert(dp[0] / 2 + deck_scoop_d / 2 + 1.2 <= w / 2, "deck scoops would break through the outer walls");
    arc = bowl_arc();

    difference() {
        union() {
            difference() {
                rbox([w, d, h], corner_r);
                // ---- hollows underneath, in peaked-roof bays: one set per half, at each half's height ----
                translate([wall, wall, floor_t])
                    tent_bays([w - 2 * wall, shared_d - wall - divider_t / 2],
                              lowest_floor(pockets) - pocket_floor_t - floor_t, bay_max_w, divider_t, ri);
                translate([wall, shared_d + divider_t / 2, floor_t])
                    tent_bays([w - 2 * wall, shared_d - wall - divider_t / 2],
                              dfz - pocket_floor_t - floor_t, bay_max_w, divider_t, ri);
            }
            // solid columns under the deck scoops, so dipping below the card floor doesn't open the hollow
            intersection() {
                rbox([w, d, h], corner_r);
                for (c = scoops) translate([c[0], c[1], floor_t - eps])
                    cylinder(d = deck_scoop_d + 2 * divider_t, h = dfz - floor_t + eps, $fn = 64);
            }
        }

        // ---- back half: deck ----
        translate([dc[0] - dp[0] / 2, dc[1] - dp[1] / 2, dfz]) rbox([dp[0], dp[1], h], ri);
        for (c = scoops) translate([c[0], c[1], dfz - deck_scoop_drop]) cylinder(d = deck_scoop_d, h = h, $fn = 64);

        // ---- front half: suit bowl, dice, square stacks ----
        for (p = pockets) {
            t = p[0];
            fz = stack_floor_z(t);
            if (t[0] == "bowl") {
                // pill-shaped bowl: a capsule (two spheres hulled) whose arc spans the bowl at the rim
                // and dips suit_bowl_depth, so it curves front to back and around both ends
                translate([p[1], p[2], arc[1]]) hull()
                    for (s = [-1, 1]) translate([s * (p[3] / 2 - p[4] / 2), 0, 0]) sphere(r = arc[0], $fn = 96);
            } else {
                translate([p[1], p[2], fz - icon_depth]) linear_extrude(icon_depth + 0.01)
                    icon(t[2], min(icon_max, min(p[3], p[4]) - 2 * icon_margin));
                translate([p[1], p[2], fz]) {
                    linear_extrude(h) {
                        if (t[0] == "dice") rotate(90) stadium(p[4], p[3]);   // long slot across x
                        else square([p[3], p[4]], center = true);
                    }
                    if (t[0] == "dice")
                        for (s = [-1, 1]) translate([s * p[3] / 2, 0, 0]) cylinder(d = die_scoop_d, h = h, $fn = 48);
                }
                if (front_row(p)) front_notch(p[1], fz + finger_notch_keep);
            }
        }
    }
}

translate(in_layout ? [shared_x, 0, 0] : [0, 0, 0])
    color("#b9955a") shared_tray();
