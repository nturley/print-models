// Pocket icons for the Root insert, debossed into pocket floors so an empty pocket shows what
// goes in it. Most are SVGs from game-icons.net (CC BY 3.0, credits in icons/CREDITS.md), stored
// in icons/ as plain 512 x 512 shapes.
// icon(name, size): the icon centred on the origin, scaled so its 512-unit box is `size` mm.
// "" draws nothing (for pockets whose shape already says what they hold).

function svg_icons() = ["log", "castle", "circular-saw", "anvil-impact", "shaking-hands",
                        "tree-branch", "camping-tent", "fist", "hearts", "swap-bag",
                        "ancient-columns", "round-star"];

function is_svg_icon(name) = len([for (s = svg_icons()) if (s == name) 1]) > 0;

module icon(name, size = 12) {
    if (name == "") { }
    else if (is_svg_icon(name))
        // offset() redraws the outline: some SVG paths overlap themselves, and without this
        // CGAL rejects the extruded icon ("mesh is not closed") and silently cuts nothing
        offset(delta = 0.001) scale(size / 512) import(str("icons/", name, ".svg"), dpi = 25.4, center = true);
    else assert(false, str("unknown icon: ", name));
}
