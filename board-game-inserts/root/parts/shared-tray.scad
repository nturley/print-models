// Shared tray: one piece filling the right-hand column of the insert (94 x 213 x 46).
//   Back half:  the 54-card deck, centred, in a pocket whose floor is raised so the deck ends just
//               below the rim, with a finger scoop halfway along each long side.
//   Front half: three rows, each spread evenly:
//     back:   3 winter suit marker stacks (rounded oblong pockets, long side front to back)
//     middle: both dice in one long slot, with a scoop at each end
//     front:  4 square stacks: items x2, ruins, score markers
//   Pocket floors are raised so everything ends just below the rim; token pockets have a thumb
//   scoop on their front edge, down to the pocket floor. Hollow underneath in peaked-roof bays (no bridging), one set per
//   half. No lid: the board stack caps it. Prints upright, no supports.
include <../constants.scad>
use <../lib/shared-layout.scad>
use <../../lib/print.scad>

in_layout = true;   // place at its position in the insert (false: at the origin)

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

    difference() {
        rbox([w, d, h], corner_r);

        // ---- back half: deck ----
        translate([dc[0] - dp[0] / 2, dc[1] - dp[1] / 2, dfz]) rbox([dp[0], dp[1], h], ri);
        for (s = [-1, 1]) translate([dc[0] + s * dp[0] / 2, dc[1], dfz]) cylinder(d = deck_scoop_d, h = h, $fn = 48);

        // ---- front half: tokens and dice ----
        for (p = pockets) {
            t = p[0];
            fz = stack_floor_z(t);
            translate([p[1], p[2], fz]) {
                linear_extrude(h) {
                    if (t[0] == "dice") rotate(90) stadium(p[4], p[3]);   // long slot across x
                    else if (t[0] == "suit") stadium(p[3], p[4]);
                    else square([p[3], p[4]], center = true);
                }
                if (t[0] == "dice")
                    for (s = [-1, 1]) translate([s * p[3] / 2, 0, 0]) cylinder(d = die_scoop_d, h = h, $fn = 48);
                else
                    translate([0, -p[4] / 2, finger_notch_keep]) cylinder(d = thumb_scoop_d, h = h, $fn = 48);
            }
        }

        // ---- hollows underneath, in peaked-roof bays: one set per half, at each half's height ----
        translate([wall, wall, floor_t])
            tent_bays([w - 2 * wall, shared_d - wall - divider_t / 2],
                      lowest_floor(pockets) - pocket_floor_t - floor_t, bay_max_w, divider_t, ri);
        translate([wall, shared_d + divider_t / 2, floor_t])
            tent_bays([w - 2 * wall, shared_d - wall - divider_t / 2],
                      dfz - pocket_floor_t - floor_t, bay_max_w, divider_t, ri);
    }
}

translate(in_layout ? [shared_x, 0, 0] : [0, 0, 0])
    color("#b9955a") shared_tray();
