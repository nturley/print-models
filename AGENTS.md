# AGENTS.md

Personal collection of 3D-printable designs. Each design is a folder (usually top-level; nested designs like `board-game-inserts/root` work too, identified by their repo-relative path); there is no root build. The root `pyproject.toml` only holds the shared test tooling (see "Design tests and viewer"). Designs are OpenSCAD (`.scad`), Blender (`.blend`), or both. A few `hello-cq/` / `my-cq/` folders are Python CadQuery sandboxes and `solidpy/` is a SolidPython2 sandbox; each `.venv` self-ignores (that's why git status doesn't show them). `solidpy/example.py` generates `.scad` via `solid2`, renders STL through the OpenSCAD CLI, and ignores its `build/` output.

## Building STLs

- `ball-bearing/` and `motor/` have `Taskfile.yaml` (go-task, `task` CLI). `task` (default) renders every part into `build/`; `task build PART=frame` renders one part.
- OpenSCAD CLI does **not** create missing output directories, and `build/` is gitignored (missing on fresh clone), so `mkdir build` before running `task`. The `ball-bearing` Taskfile also runs with `dir: build` (uses `../parts/`), `motor` from the project root.
- Folders without a Taskfile: render manually, e.g. `openscad -o out.stl model.scad`.
- `openscad` (v2021.01) and `task` are installed and on PATH.

## Design tests and viewer

- Python tooling is managed with **uv** only (root `pyproject.toml` + `uv.lock`; never pip/venv directly).
- `scadcheck/` renders a design's parts to STL (cached by mtime in `<design>/build/`) and checks the meshes: `min_distance` (python-fcl, returns closest points), `intersection_volume` (manifold3d), `is_watertight`, `bounds`/`size`, `overhang_area`, plus `read_constants()` for `constants.scad`.
- Parts can be given as a plain path (the file renders the part in assembled position, like `ball-bearing/parts/*.scad`) or as `scad("assembly.scad", part="name", print="parts/name.scad")`: rendered in place through the assembly's `part` selector for fit checks, and from the part file for printing. `motor/motorCar.scad` has the selector: `openscad -D 'part="gear1"' motorCar.scad` renders one part in place (vitamins as real geometry when selected, `%` otherwise). Renders run in parallel and are cached by mtime.
- Blender designs: `blend("file.blend", ["Obj", ...])` (or `"collection:Print"`) exports those objects with modifiers applied, in place, via `scadcheck/blender_export.py` run headless (`blender -b --factory-startup --disable-autoexec`). Blender is found via `$BLENDER`, PATH, or `C:\Program Files\Blender Foundation\Blender *` (5.0 installed; CI downloads the official 5.0.1 build, cached). Exports get zero-thickness internal walls removed (Mirror-modifier seams) before fit checks; `is_watertight` still checks the raw export. `Design(print_in_place=True)` keeps parts as assembled on the bed (hinged prints like `paint-tray/`).
- Tests live in `<design>/tests/test_<design>.py`; run `uv run pytest <design>`. The `measure` fixture records values (and closest-point pairs) into `<design>/build/report.json`.
- Each test file builds its `Design` at module level (cheap; nothing renders until `design.ready()`) and adds the shared checks with `globals().update(standard_checks(DESIGN, ...))` from `scadcheck/checks.py`: watertight, print file matches assembly, fits printer, plate fits, rests flat on bed, no interference between any pair (`skip_pairs=` / `pair_tolerance=` for meshing gears or snug keys). The file itself only holds design-specific checks, using a module fixture that returns `DESIGN.ready()`. Give asserts a readable message: the viewer shows its first line.
- Results are mesh-based, so they're only as accurate as `$fn`: OpenSCAD puts vertices *on* the circle, so holes come out smaller and spheres have no vertex at the poles. Compare against nominal values from constants where that matters.
- Print bed: `scadcheck/printers.py` holds build volumes (default `creality-k2`, 260³ mm, the user's printer) and a hand-drawn plate outline. Set `part.print_rotation = (x, y, z)` (OpenSCAD `rotate()` degrees) for parts that print in a different orientation; `design.plate` shelf-packs the printed parts onto one bed and the report stores each part's bed transform.
- Downloads: each pytest run also writes print-ready files into `<design>/build/` (`scadcheck/exports.py`): `print/<part>.stl` (print orientation, centred, on z=0), `<design>-stl.zip` of those, and `<design>-plate.3mf` with the bed layout in slicer coordinates (hand-written 3MF, no extra deps). The report records the GitHub repo + commit (from `GITHUB_*` env in CI, else `git remote`/`HEAD`) so the viewer can link each part's `.scad` source.
- Viewer: `uv run python -m http.server` from the repo root, then open `http://localhost:8000/viewer/?design=<design>`. **Assembly** view (with vitamins, section plane, click-to-measure, test measurements) and **Print bed** view (`#bed`: parts in print orientation on the printer's plate inside its build volume).
- CI: `.github/workflows/pages.yml` installs OpenSCAD from apt, runs `uv run pytest`, builds the site with `uv run python -m scadcheck.site _site` (index page + viewer + each design's `build/report.json` and STLs), and deploys to GitHub Pages from `main`. It deploys even when tests fail, so the site shows the failures; the job is then marked failed. Pull requests run the tests without deploying. A design appears on the site once it has a `tests/` folder.

## OpenSCAD structure per design

- `parts/` – designed parts, one module per file (`use <parts/X.scad>` in the assembly). Each part file calls its own module at the bottom so it renders standalone.
- `vitamins/` – parametric models of off-the-shelf hardware (steel balls, gear motor, AA batteries) used only for fit/clearance checks. In assemblies these are shown transparent via the `%` prefix (e.g. `%motor();`).
- `vendor/` – third-party `.scad` libraries/models (e.g. `gear.scad`) or downloaded STLs.
- `lib/` – shared local modules.
- Tunable design parameters live in `constants.scad` (ball-bearing) or at the top of the file; `$fn` is set per primitive.

## Git conventions

- `*.stl` and `build/` are gitignored repo-wide: STLs and test reports are build artifacts, don't commit them. Exception: `wire-spools/vendor/.gitignore` contains `!*.stl` so a downloaded third-party STL is tracked. Use the same pattern if committing another vendor STL.
- `.blend` files are committed as-is; `.blend1` autosave backups are not.
- Commit style is short lowercase messages with no prefixes, e.g. `add ball bearing files`, `commit roller clutch attempt`.

Each design's `README.md` records practical print knowledge (supports, orientation, assembly, common issues) – read it before modifying a design.
