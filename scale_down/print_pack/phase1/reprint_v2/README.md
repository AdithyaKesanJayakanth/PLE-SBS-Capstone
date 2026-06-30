# Phase 1 version 2: what to print now

The version-1 parts printed on 27 June 2026 did not fit: the wagon's spacer pegs and baskets missed their plates, the axle holes drooped because the plates printed standing, and the turnout's star arms swept the lanes. Version 2 was checked part against part in its working position (`../../check/assembly_report.md`, and independently in FreeCAD, `../../check/freecad_report.md`).

## Print these (18 files)

| File | Qty | Filament | Colour | g | Time | Why it changed |
|---|---:|---|---|---:|---|---|
| trolley_plate_x6 | 6 | PLA | Cobalt Blue | 47.9 | 1h 25m | pegs now reach the other plate; axle holes print round (plate lies flat); short guide lips |
| pannier_x6 | 6 | PLA | Cobalt Blue | 104.8 | 2h 24m | new: one part for both sides, clamped by the axle pins, floor 12 mm above the strip |
| axle_pin_x6 | 6 | PETG | Orange | 3.3 | 0h 52m | longer (28 mm shank) to pass through pannier, plate, wheel, plate, pannier |
| turnout_base_x1 | 1 | PLA | Light Grey | 164.4 | 3h 46m | new layout: escapement bridges, flap gantry posts, lane spacing, wire groove underneath |
| tongue_x1 | 1 | PLA | Orange | 22.2 | 0h 41m | new: ring of four teeth and the spring tab |
| rocker_x1 | 1 | PLA | Orange | 8.1 | 0h 28m | new: escapement rocker with coin cup |
| rocker_pin_x1 | 1 | PETG | Orange | 0.5 | 0h 14m | new |
| bias_spring_x1 | 1 | PETG | Orange | 1.0 | 0h 14m | new leaf spring |
| flap_x1 | 1 | PLA | Orange | 14.8 | 0h 25m | new trigger flap with crank |
| gantry_axle_x1 | 1 | PETG | Orange | 2.1 | 0h 12m | new |
| handover_x1 | 1 | PLA | Light Grey | 49.1 | 1h 06m | the wire now dives through it and runs on under the yard; head height matches the wheel seat |
| window_hook_x1 | 1 | PETG | Orange | 49.6 | 1h 25m | pocket turned to open upward; rim prints without support |
| brake_comb_190_x3 | 3 | PLA | Light Grey | 155.7 | 3h 31m | v1 leaves stood 21.7 mm tall and would ram the baskets; v2 leaves reach 13.8 mm |
| chain_bed_190_x3 | 3 | PLA | Light Grey | 133.6 | 2h 35m | trough now runs to the end so the sled can reach the bumper; no stirrup ring |
| sled_x3 | 3 | PLA | Light Grey | 10.0 | 0h 23m | new: the left basket pushes it and the chain |
| bumper_x3 | 3 | PETG | Orange | 106.2 | 4h 45m | rail stub runs to the face plate; trough for the sled |
| start_gate_x1 | 1 | PLA | Light Grey | 5.8 | 0h 19m | v1 wire slot was 1 mm (wire is 1.5) and the key missed the wire |
| gate_lever_x1 | 1 | PLA | Light Grey | 1.3 | 0h 09m | new hook over the rear spacer peg |
| **Total** | **41** | | | **880** | **24h 54m** | |

Every file is in `stl/` (print orientation) and `sliced_p1s/` (P1S, 0.4 mm nozzle, quantity already on the plate).

## Keep these from the version-1 print (identical geometry, do not reprint)

| Keep | Used as |
|---|---|
| fit_coupon_x1 | fit_coupon_x1 |
| wheel_x6 | wheel_x6 |
| wedge_x2 (you have 2, need 1) | wedge_x1 |
| lead_rail_230_x3 | lead_rail_230_x3 |
| chain_11_links_x3 | chain_11_links_x3 |
| gate_key_x4 (you have 4, need 1) | gate_key_x1 |
| gate_pin_x3 (you have 3, need 1) | gate_pin_x1 |

Set aside, no longer used: indexer, star arms, the two v1 pannier types, v1 trolley plates, axle pins, start gates, gate levers, block marker flag, handover, turnout plate, tongue, combs, chain beds, bumpers and window hook.
