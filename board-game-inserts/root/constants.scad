// Root (base game) insert. All sizes in mm; see README.md for where the numbers come from.
// Coordinates: x along the box's long side (279), y toward the back of the box, z up.

eps = 0.01;

// ---- Box (measured) ----
box_inner_w = 279;      // cavity, long side
box_inner_d = 216;      // cavity, short side
box_inner_h = 71;       // lower box, floor to wall top
board_stack_h = 24;     // map + 4 faction boards + Law of Root + sheet + Learning to Play
lid_clearance = 1;      // so the box lid closes without pressing

// ---- Insert envelope ----
insert_w = 276;
insert_d = 213;
insert_h = box_inner_h - board_stack_h - lid_clearance;   // 46

// ---- Components (measured) ----
card_w = 63;
card_l = 88;
card_t = 0.35;          // per card (54-card deck = 19 mm)
square_tile = 17.6;     // buildings, roosts, bases, ruins, items, score, relationship
round_token_d = 19.2;   // wood, keep, sympathy
token_t = 2;
warrior_t = 8.9;        // all warriors and the pawn are ~8.9 thick

// Faction card stacks (walkthrough/reference/faction cards)
marquise_cards_h = 0.7;
eyrie_cards_h = 3.8;
alliance_cards_h = 0.7;
vagabond_cards_h = 8.2;

// ---- Tray construction ----
wall = 1.6;
floor_t = 1.2;
divider_t = 1.2;
card_clr = 1;            // around the cards, each side
slot_headroom = 1.5;     // above the card stack in the side-loading slot (0.8 was too tight to slide cards in)
token_pocket_clr_max = 3;   // pockets get the column's spare length, up to this much extra
token_headroom = 1;      // token stacks stop this far below the rim (the board stack caps the trays)
pocket_floor_t = 1.2;    // raised pocket floor; hollow underneath
finger_notch_w = 14;     // notch in the outer wall beside each token pocket
finger_notch_keep = 2;   // wall left above the pocket floor (holds the bottom token)
card_push_hole_d = 16;   // under the closed end of the card slot: push the cards out

// ---- Anti-warp ----
corner_r = 4;            // outer vertical corners of the base and top (inner corners: corner_r - wall)

// ---- Base-to-top joint: two pins on the base, two holes in the top (press fit, tune by test print) ----
pin_d = 5;
pin_h = 4;
pin_chamfer = 0.6;       // lead-in on the pin tip
pin_fit = 0.15;          // hole diameter over pin diameter (FDM holes print a little small)
pin_hole_extra = 0.4;    // hole deeper than the pin, so the faces seat flush
pin_hole_chamfer = 0.4;  // at the hole mouth (bed side): room for elephant's foot
pin_inset = 10;          // token-column pin centres from the inside of the front/back walls
corner_pin_inset = 6;    // third pin: front-left corner, this far from the inside of both walls
boss_wall = 1.6;         // around each hole, inside the top piece's token-column hollows
pinch_notch_w = 30;      // U-notch in the floor at the card slot opening
pinch_notch_l = 14;

// No lids: in the box, the board stack lies across every tray within ~1 mm of the tops,
// which is too small a gap for a 2 mm token or a warrior.

// ---- Faction box (all four share one size) ----
faction_box_w = 91;
faction_box_d = 106.5;
faction_box_h = insert_h;                    // 46
card_slot_w = card_w + 2 * card_clr;         // 65
card_slot_l = card_l + 2 * card_clr;         // 90
bin_w = card_slot_w;                         // warrior bin sits on the shelf, same width as the cards
column_x = wall + bin_w + divider_t;         // token column starts here
column_w = faction_box_w - column_x - wall;  // 21.6
column_l = faction_box_d - 2 * wall;         // 103.3

// ---- Per-faction data ----
factions = ["marquise", "eyrie", "alliance", "vagabond"];

function faction_name(f) =
    f == "marquise" ? "MARQUISE" : f == "eyrie" ? "EYRIE" : f == "alliance" ? "ALLIANCE" : "VAGABOND";

function faction_color(f) =
    f == "marquise" ? "#d9782d" : f == "eyrie" ? "#3d6fb4" : f == "alliance" ? "#4e9a48" : "#8b8f88";

function faction_cards_h(f) =
    f == "marquise" ? marquise_cards_h : f == "eyrie" ? eyrie_cards_h
    : f == "alliance" ? alliance_cards_h : vagabond_cards_h;

// Token stacks in the column, listed from the back of the box forward: [shape, count]
function faction_tokens(f) =
    f == "marquise" ? [["round", 8], ["round", 1], ["square", 6], ["square", 6], ["square", 6]]   // wood, keep, sawmills, workshops, recruiters
    : f == "eyrie" ? [["square", 7]]                                                              // roosts
    : f == "alliance" ? [["round", 10], ["square", 3]]                                           // sympathy, bases
    : [["square", 3]];                                                                           // relationship markers

// Where each box sits in the insert (2 x 2 block on the left; shared trays on the right)
function faction_pos(f) =
    f == "marquise" ? [0, insert_d - faction_box_d, 0]
    : f == "eyrie" ? [faction_box_w, insert_d - faction_box_d, 0]
    : f == "alliance" ? [0, 0, 0]
    : [faction_box_w, 0, 0];
