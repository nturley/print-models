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
finger_notch_w = 14;     // notch in the outer wall beside each token pocket (narrower than any token)
finger_notch_keep = 0;   // notches and scoops reach the pocket floor: a fingernail fits under the bottom token
notch_corner_r = 3;      // rounded bottom corners of the flat-bottomed finger notch
card_push_hole_d = 16;   // under the closed end of the card slot: push the cards out

// ---- Anti-warp ----
corner_r = 4;            // outer vertical corners of the base and top (inner corners: corner_r - wall)

// ---- Base-to-top joint: two pins on the base, two holes in the top (press fit, tune by test print) ----
pin_hole_d = 5.15;       // hole in the top piece (unchanged since the first prints)
pin_fit = 0.35;          // hole diameter minus pin diameter: tune the pin, not the hole
                         // (0.15: perfect in orange, too tight in green; 0.25: still tight in grey.
                         //  Err loose: a loose fit takes a drop of glue, a tight one can crack a piece)
pin_d = pin_hole_d - pin_fit;   // 4.8
pin_h = 4;
pin_chamfer = 0.6;       // lead-in on the pin tip
pin_hole_extra = 0.4;    // hole deeper than the pin, so the faces seat flush
pin_hole_chamfer = 0.4;  // at the hole mouth (bed side): room for elephant's foot
pin_inset = 6;           // four pins, one per corner, this far from the inside of both walls
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

// ---- Shared tray (one piece filling the right-hand column: deck at the back, tokens at the front) ----
shared_w = insert_w - 2 * faction_box_w;   // 94
shared_tray_d = insert_d;                  // 213, the whole tray
shared_d = insert_d / 2;                   // 106.5, each half (deck section, token section)
shared_x = 2 * faction_box_w;              // 182
deck_h = 19;             // 54-card shared deck (measured)
deck_scoop_d = 20;       // finger scoops halfway along the deck's long sides
suit_w = 14.7;           // winter suit markers (oblong), stored long side front to back
suit_l = 28.7;
die_flat = 21.7;         // custom d12: height lying on a face
die_corner = 25.5;       // widest point
shared_clr = 0.75;       // around each stack or die in the shared tray (each side)
bin_pocket_clr = 0.75;   // around the stack in the warrior-bin corner pocket (each side)
thumb_scoop_d = 10;      // on the front edge of each token pocket in the shared tray
die_scoop_d = 14;        // at each end of the dice slot
bay_max_w = 22;          // hollow bays under raised floors: widest one whose 45° roof fits

// Shared tray rows, back to front: [kind, stack count] per pocket
shared_rows = [
    [["suit", 4], ["suit", 4], ["suit", 4]],            // rabbit, fox, mouse
    [["dice", 2]],                                    // both dice in one long slot
    [["square", 12], ["square", 4], ["square", 9], ["square", 9]],   // supply items, ruins, 18 blank spare tiles
];

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
// Each faction keeps its own score marker. Items: the 12 supply items (placed every game, 5.1.5)
// are in the shared tray; the other 11 (4 ruin + 7 Vagabond starting items, 9.3.4-9.3.5) are only
// used with the Vagabond, so they live in its box.
function faction_tokens(f) =
    f == "marquise" ? [["round", 8], ["round", 1], ["square", 6], ["square", 6], ["square", 6]]   // wood, keep, sawmills, workshops, recruiters
    : f == "eyrie" ? [["square", 7], ["square", 1]]                                              // roosts, score marker
    : f == "alliance" ? [["round", 10], ["square", 3], ["square", 1]]                            // sympathy, bases, score marker
    : [["square", 3], ["square", 11], ["square", 1]];                                            // relationship markers, Vagabond items, score marker

// Extra pocket walled off in the warrior bin's back-right corner, next to the token column
// (the Marquise column is full).
function bin_corner_tokens(f) = f == "marquise" ? [["square", 1]] : [];                         // Marquise score marker

// Where each box sits in the insert (2 x 2 block on the left; the shared tray on the right)
function faction_pos(f) =
    f == "marquise" ? [0, insert_d - faction_box_d, 0]
    : f == "eyrie" ? [faction_box_w, insert_d - faction_box_d, 0]
    : f == "alliance" ? [0, 0, 0]
    : [faction_box_w, 0, 0];
