# Phase 2: the launch pad and rocket, 1:50

An addition to the print-only model in [BOM.md](BOM.md). The pad and rocket stand at the top of the wire at the same 1:50 scale, so the wire's upper end moves from the window hook to an anchor post on the tower at the crew access level. Dimensioned drawing: [sketch_8_launchpad.png](sketch_8_launchpad.png) (from `make_pad_drawing.py`).

The reference launcher is the paper's: an LVM3-class crewed launcher (two solid boosters, a hypergolic core, a cryogenic upper stage, a crew module with an escape tower on top) on the generic pad with its crew access level 42 m up and the tower 15 m from the rocket. The rocket's dimensions are public LVM3 figures, rounded; the pad's are the paper's estimates. At 1:50 the rocket stands 870 mm tall and the tower 960 mm, far taller than the printer, so every part is cut into pieces under 240 mm that print one at a time and are assembled by hand: the rocket tubes and the tower segments stack on printed pins, the boosters clip to the core, the tower pegs into its foot and the foot into the base tile. No glue is needed; a drop of PVA at each pin is optional once the fit is right.

## 1. To buy

| # | Item | Specification | Qty | Approx. ₹ |
|---:|---|---|---:|---:|
| 1 | PLA Basic, white | 1 kg spool, matte. The rocket. | 1 | 1,100 |
| 2 | PLA Basic, grey | 1 kg spool. The launch mount and base tiles. | 1 | 1,100 |
| 3 | PETG Basic, grey or black | 1 kg spool. The tower, arm and anchor. | 1 | 1,300 |
| 4 | PLA Basic, orange | small reel, 250 g. The core band and hazard marks. | 1 | 450 |
| 5 | TPU 95A (optional) | small reel. Hold-down clamps and umbilical hoses. | 1 | 700 |

Phase 1 left about 450 g of PLA and some PETG; the spools above cover phase 2 with a margin for failed prints. No glue, screws or magnets: the segments stack on printed pins and the tower bolts to the base with printed pegs, as in phase 1.

## 2. Already at home

| Item | Used for |
|---|---|
| The phase 1 wire, 1.5 mm stainless | now anchored on the tower post instead of the window hook |
| Sandpaper, 240 and 400 grit, and white spray primer (optional) | the rocket's segment joints, if you want them to vanish |
| A heavy book or a brick | on the base tiles, so the tower cannot tip when the wire is tensioned |

## 3. Printed parts

Files will be written by `make_pad_parts.py` (to be added, like `make_parts.py` for phase 1). Masses are estimates for the settings in section 4. Total about 1.35 kg plus failed prints.

| File | Qty | Material | Colour | g each | Size (mm) | What it is |
|---|---:|---|---|---:|---|---|
| base_tile_x2.stl | 2 | PLA | grey | 150 | 280 × 320 × 12 | the pad deck, dovetailed into one 560 × 320 plate; sockets for the mount and tower |
| launch_mount_x1.stl | 1 | PLA | grey | 95 | 240 × 240 × 80 | the pedestal with the flame-duct opening; four hold-down pads for the boosters |
| core_seg_x4.stl | 4 | PLA | white | 55 | Ø80 × 165 | the core and upper stage, four tubes on stacking pins; the lowest carries the engine section |
| core_band_x1.stl | 1 | PLA | orange | 12 | Ø80 × 120 (sleeve) | the hypergolic core marking, a thin sleeve over segment 2 |
| crew_module_x1.stl | 1 | PLA | white | 40 | Ø80 → Ø18, 230 tall | the crew module cone and the escape tower in one print, tower up |
| booster_seg_x4.stl | 4 | PLA | white | 48 | Ø64 × 250 | two per booster; the lower one carries the nozzle |
| booster_nose_x2.stl | 2 | PLA | white | 10 | Ø64 × 48 | booster nose cones |
| booster_strap_x4.stl | 4 | PETG | grey | 3 | 90 × 12 × 8 | clips each booster to the core at two heights |
| engine_set_x1.stl | 1 | PETG | black | 22 | 140 × 100 × 40 | the core's two nozzles and the booster nozzles, printed flat, bell up |
| tower_seg_x4.stl | 4 | PETG | grey | 62 | 160 × 160 × 240 | the lattice tower, four identical segments on corner pins; the top one carries the lightning mast |
| tower_foot_x1.stl | 1 | PETG | grey | 28 | 180 × 180 × 20 | pegs into the base tile; the tower's bottom segment sits in it |
| access_arm_x1.stl | 1 | PETG | grey | 25 | 180 × 20 × 24 | the crew access arm, hinged on the tower at 840 so it swings clear |
| white_room_x1.stl | 1 | PLA | white | 8 | 30 × 30 × 28 | the room at the capsule end of the arm |
| anchor_post_x1.stl | 1 | PETG | black | 14 | 40 × 24 × 60 | the slidewire anchor at the crew access level: capstan post and wedge pocket, as on the window hook |
| holddown_x4.stl | 4 | TPU | black | 2 | 20 × 14 × 10 | flexible hold-down clamps at the booster skirts |
| umbilical_x3.stl | 3 | TPU | black | 4 | 200 × 6 × 6 | hoses from the tower to the core, printed flat |

Print the base tiles, the mount and one tower segment first, and test the tower on its foot before printing the rest.

## 4. Print settings (Bambu Studio, P1S, 0.4 mm nozzle)

| Setting | Value |
|---|---|
| Layer height | 0.2 mm (crew module and nozzles: 0.12 mm) |
| Walls | 2 for the rocket tubes (light, smooth), 4 for the mount, tiles and tower |
| Infill | 10 % gyroid for the tubes; 20 % for the mount and tiles; tower lattice is solid walls |
| Supports | none. Tubes stand on the bed; tower segments stand on their base; nozzles print bell up |
| Brim | 5 mm on the tower segments and the crew module |
| Speed | default; TPU at 40 % |

Orientation: every tube and segment stands upright, so the stacking pins print on top as short bosses and the sockets print as holes in the base. The crew module prints cone down, escape tower up, with a brim. Straps, arm, hoses and the engine set print flat.

## 5. Scale and what is and is not to scale

- Heights are 1:50, the same as the wire: the crew access level sits at 840 mm, so the wire drops 0.84 m to the yard over a 5 to 6 m span, close to phase 1's 0.9 m.
- The rocket, the launch mount and the tower are to scale in all three axes.
- The base plate is not: a real pad deck would be metres across at this scale. Two tiles of 280 × 320 mm carry the mount and the tower foot and nothing more.
- The umbilical tower is a plain lattice with the one arm that matters to the paper, the crew access arm; the real tower's other arms, lifts and platforms are left off.

## 6. Both phases together: spools and consumption

Phase 1's figures are from [BOM.md](BOM.md) (about 550 g PLA and 120 g PETG); phase 2's are the sums of section 3.

| Filament | Phase 1 | Phase 2 | Used, total | With ~15 % for brims, purge and failed prints |
|---|---:|---:|---:|---:|
| PLA, grey (yard, mount, base tiles) | 550 g | 395 g | 945 g | 1.09 kg |
| PLA, white (the rocket) | – | 480 g | 480 g | 0.55 kg |
| PLA, orange (core band, marks) | – | 12 g | 12 g | 15 g |
| PETG, grey or black (pins, springs, tower, arm, anchor, nozzles) | 120 g | 349 g | 469 g | 0.54 kg |
| TPU 95A, optional (clamps, hoses) | – | 20 g | 20 g | 25 g |
| **Total** | **670 g** | **1,256 g** | **1.93 kg** | **2.2 kg** |

| # | Spool | Size | Approx. ₹ | Left over after both phases |
|---:|---|---|---:|---|
| 1 | PLA Basic, grey | 2 × 1 kg | 2,200 | about 0.9 kg (one spool is enough if phase 1's 550 g of PLA is still at home) |
| 2 | PLA Basic, white, matte | 1 kg | 1,100 | about 0.45 kg |
| 3 | PETG Basic, grey or black | 1 kg | 1,300 | about 0.45 kg |
| 4 | PLA Basic, orange | 250 g | 450 | nearly all |
| 5 | TPU 95A, optional | 250 g | 700 | nearly all; or print the clamps in PETG and the hoses in PLA |
| | **Total** | **4.5 kg** | **5,750** | |
