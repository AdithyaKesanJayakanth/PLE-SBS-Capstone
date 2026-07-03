# Phase 1 version 2: what to print now

The version-1 parts printed on 27 June 2026 did not fit. Version 2 was checked part against part in its working position, along every assembly path and through a run of three wagons (`../../check/assembly_report.md`, `../../assembly/path_check_report.md`), and again in FreeCAD (`../../check/freecad_report.md`, `../../assembly/freecad_motion_report.md`). Step-by-step pictures and animations: `../../assembly/`.

## Print these (19 files)

| File | Qty | Filament | Colour | g | Time | Why it changed |
|---|---:|---|---|---:|---|---|
| trolley_plate_x6 | 6 | PLA | Cobalt Blue | 49.1 | 1h 27m | pegs reach the other plate and carry shoulders that set the 9.2 mm gap; axle holes print round (the plate lies flat); lips 0.5 mm clear of the web; 3.6 thick with 0.4 bosses to suit 0.2 mm layers |
| pannier_x6 | 6 | PLA | Cobalt Blue | 105.2 | 2h 25m | new: one part for both sides, clamped by the axle pins, floor 12 mm above the strip; arm spacing for the 9.2 mm plate gap |
| axle_pin_x6 | 6 | PETG | Orange | 3.4 | 0h 52m | longer (28.4 mm shank) to pass through pannier, plate, wheel, plate, pannier; snap bump 0.7 mm clear |
| turnout_base_x1 | 1 | PLA | Light Grey | 159.9 | 3h 38m | new layout: lane spacing, pegs for the rocker bridge, gantry posts with 3.6 mm snap mouths, wire groove underneath; the entry rail's end lets the tongue slide under |
| tongue_x1 | 1 | PLA | Orange | 22.5 | 0h 41m | new: ring of four teeth and the spring tab |
| rocker_bridge_x1 | 1 | PLA | Light Grey | 6.6 | 0h 25m | new: carries the rocker over the tooth ring; separate so the tongue can be fitted first; beams 2.5 mm over the teeth, sliced with supports |
| rocker_x1 | 1 | PLA | Orange | 8.3 | 0h 28m | new: escapement rocker with a 26 mm coin cup |
| rocker_pin_x1 | 1 | PETG | Orange | 0.5 | 0h 14m | new |
| bias_spring_x1 | 1 | PETG | Orange | 1.0 | 0h 14m | new leaf spring |
| flap_x1 | 1 | PLA | Orange | 14.8 | 0h 25m | new trigger flap with a 16 mm crank |
| gantry_axle_x1 | 1 | PETG | Orange | 2.1 | 0h 12m | new |
| handover_x1 | 1 | PLA | Light Grey | 49.1 | 1h 06m | the wire now dives through it and runs on under the yard; head height matches the wheel seat |
| window_hook_x1 | 1 | PETG | Orange | 49.6 | 1h 25m | pocket opens upward; rim prints without support |
| brake_comb_190_x3 | 3 | PLA | Light Grey | 150.5 | 3h 27m | v1 leaves stood 21.7 mm tall and would ram the baskets; v2 leaves reach 13.8 mm and end inside the segment |
| chain_bed_190_x3 | 3 | PLA | Light Grey | 132.9 | 2h 34m | trough runs to the end so the sled can reach the bumper; no stirrup ring |
| sled_x3 | 3 | PLA | Light Grey | 10.0 | 0h 23m | new: the left basket pushes it and the chain |
| bumper_x3 | 3 | PETG | Orange | 106.2 | 4h 45m | rail stub runs to the face plate; trough for the sled |
| start_gate_x1 | 1 | PLA | Light Grey | 5.8 | 0h 19m | v1 wire slot was 1 mm for a 1.5 mm wire and the key missed the wire; the slot now opens downward so the gate hangs on the wire |
| gate_lever_x1 | 1 | PLA | Light Grey | 1.4 | 0h 09m | new hook over the rear spacer peg |
| **Total** | **42** | | | **879** | **25h 09m** | |

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
