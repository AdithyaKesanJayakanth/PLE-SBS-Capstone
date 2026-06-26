# Phase 2: launch pad and rocket at 1:50

A cosmetic model of the generic pad from the paper (reference medium-lift launcher, crew access level 42 m, tower 15 m from the rocket), printed in segments that fit the P1S bed and assembled by hand. It stands at the window end of the wire, under the hook. The wire's pull goes to the window hook; the printed tower carries nothing. Dimensions: [sketch_8_pad_phase2.png](sketch_8_pad_phase2.png).

![Pad and rocket](sketch_8_pad_phase2.png)

## Dimensions (model mm, full size in brackets)

| Item | Model | Full size |
|---|---|---|
| Rocket overall height | 960 | 48 m |
| Core diameter | 80 | 4.0 m |
| Boosters, two | Ø64 × 520 | 3.2 m × 26 m |
| Capsule and nose | 160 tall | 8 m |
| Tower | 160 × 160 × 1000 | 8 × 8 × 50 m |
| Crew access level | 840 above the platform | 42 m |
| Access arm | 300 long × 12 wide | 15 m |
| Tower offset from the rocket | 300 | 15 m |
| Launch platform | 480 × 480 × 30 | 24 × 24 m |

## Printed segments

| Part | Segments | Size each (mm) | Filament | g total | Colour |
|---|---:|---|---|---:|---|
| Core stage | 4 | Ø80 × 240, 2 walls, hollow, 8 mm spigot joints | PLA Basic | 240 | Jade White |
| Capsule and nose | 1 | Ø80 → point, 160 tall | PLA Basic | 50 | Jade White |
| Boosters | 4 | Ø64 × 260, 2 walls, 2 per booster, nose included on the top segment | PLA Basic | 210 | Light Grey |
| Booster struts | 4 | 20 × 10 × 12 clips to the core | PLA Basic | 8 | Light Grey |
| Tower | 4 | 160 × 160 × 250 lattice, 8 mm corner posts, dovetail stacking | PLA Basic | 440 | Dark Grey |
| Tower crown and crane | 1 | 160 × 160 × 40 | PLA Basic | 60 | Dark Grey |
| Access arm | 1 | 300 × 30 × 12, pivots on a pin at the tower | PLA Basic | 60 | Orange |
| Arm pivot pin and stop | 2 | Ø6 × 40; 20 × 10 × 10 | PETG HF | 5 | Orange |
| Launch mount ring | 1 | Ø120 × 40, holds the core base | PLA Basic | 80 | Light Grey |
| Platform tiles | 4 | 240 × 240 × 3 with ribs, dovetails | PLA Basic | 500 | Light Grey |
| Start-gate stand | 1 | clips to the tower at the access level, carries the three gates | PLA Basic | 30 | Dark Grey |

Total about 1.7 kg printed, 27 pieces. The platform is the heaviest item; print the tiles at 15 % infill with 3 walls, or drop them and stand the tower on the floor.

## Filament for phase 2

| Colour | Filament | Parts | Printed mass |
|---|---|---|---:|
| Jade White | PLA Basic | core, capsule | 290 g |
| Light Grey | PLA Basic | boosters, struts, launch mount, platform tiles | 798 g |
| Dark Grey | PLA Basic | tower, crown, gate stand | 530 g |
| Orange | PLA Basic | access arm | 60 g |
| Orange | PETG HF | arm pin and stop | 5 g |

## Phases 1 and 2 combined

| Colour | Filament | Phase 1 | Phase 2 | Used | Used + 40 % | Buy |
|---|---|---:|---:|---:|---:|---|
| Light Grey | PLA Basic | 427 | 798 | 1,225 | 1,715 | 2 spools (2 kg) |
| Dark Grey | PLA Basic | 0 | 530 | 530 | 740 | 1 spool |
| Jade White | PLA Basic | 0 | 290 | 290 | 405 | 1 spool |
| Cobalt Blue | PLA Basic | 84 | 0 | 84 | 120 | 1 spool |
| Orange | PLA Basic | 52 | 60 | 112 | 160 | 1 spool |
| Orange | PETG HF | 125 | 5 | 130 | 180 | 1 spool |
| **Total** | | 688 | 1,683 | **2,371** | **3,320** | **7 spools, 7 kg** |

About 2.4 kg is printed; 3.3 kg covers test prints, failures and purges; 7 kg is what seven 1 kg spools come to. To cut a spool, print the tower in Light Grey and skip Dark Grey: then Light Grey needs 3 spools and the total stays at 7. To cut two, drop the platform tiles and print the tower grey: 6 spools.

## Making the mechanisms work first time

The moving parts are all in phase 1: wheels on pins, the dovetails, the tongue on its post, the cam and star, the detent finger, the chain, the gates. Phase 2 adds only the arm pivot.

1. **Dry filament, one spool per mechanism.** Mechanism parts shrink with the filament and the temperature; print the indexer, tongue, star arms and pins from the same spool in one session.
2. **Print the fit test before anything else.** One wheel, one pin, one plate, one wedge and one gate key, in the final filaments. The pin must turn freely with slight side play; the dovetail must push on firmly by hand. If it binds, raise `CLR` in `make_parts.py` from 0.3 to 0.4; if it rattles, lower it to 0.2. Reprint the test, then the rest.
3. **Kill the elephant's foot.** The first layer spreads, and that is what makes pins stick and dovetails jam. In Bambu Studio set the first-layer flow to 0.95 and enable "elephant foot compensation" at 0.15 mm, or print mechanism parts on a brim and trim it.
4. **Layer height 0.12 mm for the cam, pins, wheels and chain;** 0.2 mm elsewhere. The cam's dwell steps and the pin's snap tip need the finer layers.
5. **Orientation as listed in BOM.md.** Pins standing on the head, wheels flat, indexer standing on the cam, star arms flat, chain flat. A pin printed lying down has layer lines across it and snaps.
6. **PETG HF for everything that flexes or snaps**, PLA for everything that must stay stiff and square. Do not swap them.
7. **Run in by hand.** Turn the star through twenty cycles, slide each pod the length of each bay, and flick each gate ten times before the first run. A trace of candle wax or PTFE spray on the cam rim, the pin shanks and the points is allowed; it is not a purchase if you have it.
8. **Set the tongue.** With the star at rest in each notch, the tongue tip must sit within 0.5 mm of its exit rail. Shave the follower boss or add tape to it; the sketch gives the three positions.
