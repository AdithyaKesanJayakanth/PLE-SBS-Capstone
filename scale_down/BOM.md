# Print-only scale model: bill of materials

Everything except the wire is printed on a Bambu Lab P1S Combo (0.4 mm nozzle). No bearings, screws, magnets, clips or glue. Ballast and weights come from the house.

## 1. To buy

| # | Item | Specification | Qty | Approx. ₹ |
|---:|---|---|---:|---:|
| 1 | Stainless steel wire rope | 1.5 mm, 7×7, AISI 316, bare (uncoated); full specification below. Ask for "1.5 mm SS 316 wire rope 7×7, uncoated" | 10 m | 350 |

That is the whole shopping list.

### Wire specification

| Property | Specification | Why |
|---|---|---|
| Type | Stainless steel wire rope, bare (uncoated) | The printed parts are sized to the steel itself; PVC or nylon coating adds 0.3 to 0.5 mm and slips in the wedges |
| Construction | 7×7 (seven strands of seven wires) | Smooth enough for the printed wheels, flexible enough to wrap three turns round the Ø12 mm capstan post. 7×19 also works; 1×19 is too stiff for the post |
| Diameter | 1.5 mm nominal, 1.6 mm maximum | Gate and flag clamps have a 1.8 mm bore, the handover groove 1.9 mm, the wedge pockets taper from 2.2 mm. A 2 mm wire will not fit |
| Grade | AISI 316 (A4, marine) or AISI 304 (A2) | Either is fine indoors; 316 is the common stock item |
| Lay | Right-hand regular lay | Standard; no preference beyond what the shop has |
| Minimum breaking load | about 1.4 kN (140 kgf); check the seller's figure | The model runs at 50 to 80 N, a safety factor of about 20 |
| Weight | about 9 g/m | Self-weight sag over 6 m is under 2 mm at working tension; the pods set the sag |
| Length | 10 m on a reel or coil | 6 m span, 1 m round the window hook, 2 m to the floor tie-off, 1 m spare |
| Condition | No kinks, ends taped by the shop | A kink stops the trolley; never buy a bent offcut |

**Tension.** There is no turnbuckle; tension is set by hand at the floor tie-off and checked by sag. With one ballasted pod (about 0.4 kg) at mid-span, pull until the wire hangs 100 to 120 mm below the straight line between the two ends. That is about 50 to 80 N. Tighter gives a flatter, faster ride; slacker makes the last metre too flat and the pod stalls, which is the paper's Figure 4 in miniature.

**Cutting and ends.** Wrap tape round the cut point and cut through the tape with a cable cutter or a sharp side cutter at the very tip; wire snips crush the strands. Leave the tape on both ends so they cannot unlay. No ferrules or clips are needed: each end is held by three turns round a capstan post plus a wedge.

**Full-size, for comparison.** The paper's design uses 36 mm galvanised steel wire rope, 6×36 IWRC, extra improved plow steel (ASTM A1023), minimum breaking load 907 kN, at 150 kN tension. Scaled by 1:50 that would be 0.72 mm; the model's 1.5 mm is twice as thick because the trolleys need something to grip, and diameter does not affect the ride.

## 2. Already at home

| Item | Used for |
|---|---|
| PLA filament, about 550 g, and PETG, about 120 g | all parts (see section 3 for which is which). PLA only is acceptable; see the notes. |
| Coins or steel washers | ballast in the panniers: 0.1 to 0.5 kg per pod, same in both halves |
| Books or a water bottle | weight on the turnout plate and the handover module so the yard cannot creep |
| A heavy piece of furniture (bed or sofa leg) near the floor end | the far end of the wire ties off here, so the handover module carries no tension |
| Sewing thread (optional) | to pull the gate levers from a distance, and for the block-marker interlock |
| Phone with slow-motion video, tape measure | timing runs (see docs/scale-model-protocol.md in the repository) |

## 3. Printed parts

Files are in `stl/`, written by `make_parts.py`; `parts.csv` is the same table for a spreadsheet. Masses in this table are estimates. The slicer's exact figures for the P1S, per file, are in `print_pack/README.md`: phase 1 comes to 1,174 g and about 35 hours, more than estimated because the comb teeth, the rails and the mechanism parts print nearly solid.

| File | Qty | Material | g each | Size (mm) | What it is |
|---|---:|---|---:|---|---|
| wheel_x6.stl | 6 | PLA | 2 | 24 × 24 × 8 | V-groove wheel; rides the wire and the rail head |
| axle_pin_x6.stl | 6 | PETG | 1 | 8 × 8 × 21 | 4 mm pin, head one end, split snap the other |
| trolley_plate_x6.stl | 6 | PLA | 5 | 64 × 15 × 40 | two identical plates make one trolley; hook lips under the wire; dovetail for the pannier |
| pannier_right_x3.stl | 3 | PLA | 7 | 60 × 28 × 38 | basket half that rides over the brake comb |
| pannier_left_x3.stl | 3 | PLA | 7 | 60 × 28 × 45 | basket half with the chain hook |
| turnout_base_x1.stl | 1 | PLA | 111 | 248 × 180 × 64 | plate with entry rail, three exit rails, pivot post, cam post, tongue spring, detent post |
| tongue_x1.stl | 1 | PLA | 8 | 136 × 12 × 50 | the switch blade |
| indexer_x1.stl | 1 | PETG | 31 | 103 × 104 × 70 | 4-dwell cam, shaft, detent ring and star hub, one print |
| star_arm_x4.stl | 4 | PLA | 11 | 142 × 86 × 15 | L-shaped arm; its cross-bar waits across the lanes |
| handover_x1.stl | 1 | PLA | 51 | 222 × 51 × 67 | wire-to-rail ramp with the wedge cleat and a tie-down loop |
| wedge_x2.stl | 2 | PETG | 1 | 32 × 5 × 22 | pinches the wire in the cleat pockets |
| window_hook_x1.stl | 1 | PETG | 31 | 56 × 24 × 74 | hooks a grill bar or handle up to 24 mm; capstan post and wedge pocket |
| lead_rail_230_x3.stl | 3 | PLA | 24 | 242 × 22 × 54 | first bay segment (narrow strip) |
| brake_comb_190_x3.stl | 3 | PLA | 30 | 202 × 40 × 54 | rail with 12 flexible teeth: the brake |
| chain_bed_190_x3.stl | 3 | PLA | 25 | 202 × 41 × 54 | rail with a chain trough and the stirrup |
| chain_11_links_x3.stl | 3 | PLA | 3 | 156 × 10 × 10 | print-in-place drag chain |
| bumper_x3.stl | 3 | PETG | 16 | 60 × 40 × 56 | zig-zag spring, the model's backup net |
| start_gate_x3.stl | 3 | PLA | 4 | 30 × 20 × 22 | clamps on the wire and holds a pod |
| gate_key_x4.stl | 4 | PETG | 1 | 30 × 3 × 7 | tapered key that pinches the wire in a gate or the flag |
| gate_lever_x3.stl | 3 | PLA | 1 | 26 × 6 × 14 | latch lever |
| gate_pin_x3.stl | 3 | PETG | 1 | 6 × 6 × 26 | lever pivot pin |
| block_marker_flag_x1.stl | 1 | PLA | 4 | 20 × 46 × 40 | optional block marker the pod knocks |

Print `fit_coupon_x1.stl` before anything else (section 6), then the six plate-level pieces (handover, turnout, three leads), and test-fit a trolley on the rail before printing the rest.

## 4. Fits and tolerances

Every running fit is **0.2 mm per side** (`CLR = 0.2` at the top of `make_parts.py`, `SPIG_CLR` and `P.CLR` in `make_pad_parts.py`): a 4 mm pin goes in a 4.4 mm hole, a 6 mm post in a 6.4 mm bore, an 8 mm arm in an 8.4 mm socket.

| Fit | Part | Nominal | Hole or gap | Per side |
|---|---|---|---|---:|
| Wheel on axle pin | wheel, axle_pin | Ø4.0 | Ø4.4 | 0.2 |
| Axle pin in trolley plate | trolley_plate | Ø4.0 | Ø4.4 | 0.2 |
| Plate bridge pin | trolley_plate | Ø3.0 | Ø3.4 | 0.2 |
| Pannier dovetail on plate | pannier, trolley_plate | dovetail | +0.2 all round | 0.2 |
| Rail-strip dovetails | all rail segments, turnout, bumper, platform tiles | dovetail | +0.2 all round | 0.2 |
| Tongue on pivot post | tongue, turnout_base | Ø6.0 | Ø6.4 | 0.2 |
| Indexer on cam post | indexer, turnout_base | Ø6.0 | Ø6.4 | 0.2 |
| Star arm in hub socket | star_arm, indexer | 8.0 × 8.0 | 8.4 × 8.4 | 0.2 |
| Gate lever pin | start_gate, gate_lever, gate_pin | Ø3.0 | Ø3.4 | 0.2 |
| Core and booster spigots | core_segment, booster_lower, capsule, booster_upper | tube bore | spigot 0.4 smaller | 0.2 |
| Tower stacking pegs | tower_section, tower_crown | Ø5.6 peg | Ø6.0 hole | 0.2 |
| Clip on tower post | arm_bracket, wire_saddle | 8.0 × 8.0 | 8.4 × 8.4, slit to spring | 0.2 |
| Access arm pivot | access_arm, arm_bracket, arm_pin | Ø6.0 | Ø6.4 | 0.2 |

Deliberate exceptions, which are not running fits:

| Feature | Gap | Why |
|---|---|---|
| Print-in-place chain links | 0.4 mm | Parts printed already linked need a wider gap than parts assembled after printing, or they fuse |
| Wire bore in the gate and flag clamps | 1.8 mm for a 1.5 mm wire (0.15 per side) | The key pinches the wire; a looser bore lets the gate slide |
| Wire groove in the handover ramp | 1.9 mm (0.2 per side) | The wire lies in it, it does not slide in it |
| Wedge pockets | tapered 2.2 to 6 mm | The wedge closes the gap onto the wire |

Print `fit_coupon_x1` first. Its six rings are bored at 0.15, 0.20, 0.25, 0.30, 0.35 and 0.40 mm per side; the first one that turns freely on the post without wobble is your printer's clearance. If it is not 0.20, change `CLR`, regenerate and re-slice.

## 5. Print settings (Bambu Studio, P1S, 0.4 mm nozzle)

| Setting | Value |
|---|---|
| Layer height | 0.2 mm (wheels, pins, chain: 0.12 mm) |
| Walls | 4 (rails, tongue, star arms: 5, so the 2 mm blade is solid) |
| Infill | 25 % gyroid; wheels and pins 100 % |
| Supports | none. Every part is oriented to print without them (see below). |
| Brim | 5 mm on the turnout plate, handover, bumper and star arms |
| Speed | default profile; print the chain and the springs at 50 % speed |

Orientation: rails, plate, handover and bumper with the strip flat on the bed; wheels flat; axle pins standing on the head; trolley plates on their outer face (dovetail up, so the hook lips print as short bridges); panniers open side up; tongue on its foot; indexer standing on the cam; star arms flat; chain flat as exported (the upright links stand on the bed and the flat links bridge between them); window hook on its back (the hook opening faces up); gates, keys and wedges flat.

PETG where a part must flex many times or carry the wire's pull (pins, indexer, wedges, hook, bumper). If you only have PLA, print those in PLA and expect the bumper and the detent finger to tire after a few hundred cycles; the cleats will be fine.

## 6. Scale and what is and is not to scale

- Wire: 1:50 in length and drop. A 5 m span with a 1 m drop stands for a 250 m wire from a 50 m crew access level. Use whatever the room allows; the paper's rule (span ≈ 100 m + 4 × height) scales to span ≈ 2 m + 4 × drop.
- Pods: Froude scaling, as in the paper. A 3 s model run stands for about 21 s full size (√50).
- Switch yard: the mechanism is modelled (one shared wire, self-indexing points, a bay per pod, passive brake, chain bed, backup stop, block marker). The bay lengths are compressed and the brake is friction, not eddy current, so the yard shows the logic, not the numbers.

## 7. Making the mechanism work first time

Every moving fit in the model (the tongue on its pivot post, the indexer on the cam post, the axle pins, the dovetails) is cut with one clearance, `CLR = 0.3` in `make_parts.py`. Whether that is right depends on the printer, the filament and the nozzle, so measure it instead of guessing.

1. **Print the coupon.** `fit_coupon_x1.stl` (PETG, 10 g, 20 minutes) has a 6 mm post, a 4 mm pin and six rings bored at 0.15, 0.20, 0.25, 0.30, 0.35 and 0.40 mm, with one to six notches on the rim so they can be told apart. Push the post through each ring. The first ring that turns freely by finger with no wobble is your `CLR`. Do the same with the 4 mm pin for the axles.
2. **Set it and re-run** `make_parts.py`. Everything is regenerated with your number; the rest of the parts are printed only after this.
3. **Kill elephant's foot.** The pins, posts and ring bores all start on the bed, and a squashed first layer is what makes a 0.3 mm fit bind. In Bambu Studio set *Elephant foot compensation* to 0.15 mm and *First layer height* to 0.2 mm, and level the bed before the coupon.
4. **Calibrate the two filaments.** Run the P1S flow-rate and pressure-advance calibration for the PLA and the PETG you will use, once. Over-extrusion by 3 % closes a 0.3 mm gap.
5. **The cam, the tongue and the detent are the parts that must be right.** Print the indexer (PETG) and the tongue (PLA) at 0.12 mm layers with 5 walls; the cam rim and the follower boss are then smooth and the 2 mm blade is solid. Print the detent finger's plate (the turnout base) with the finger's thin wall parallel to the bed's X axis so it bends along the layers, not across them.
6. **Fit dry, then lubricate.** Before assembly, run a fingernail round the cam rim and the ring bores to knock off any seam bump, and chamfer the post tips with a blade so the tongue and indexer drop on square. Then a dry PTFE spray or a pencil's graphite on the cam rim, the pivot post and the detent ring. Never oil: it softens PLA and collects dust.
7. **Check in this order.** Spin the indexer on its post by hand: it should turn freely and click into four stops. Push the tongue through its throw with the indexer removed: it must swing past all three exit rails without catching, and the leaf spring must return it. Then with the indexer on, turn it by hand through a full revolution and watch the tongue step 1, 2, 3, 2. Only then run a pod. If the tongue hesitates at one position, the fault is in the cam profile's 10-degree ramps: sand the ramp, do not shim the follower.
8. **Springs tire.** The leaf spring, the detent finger, the brake teeth and the bumpers are PLA or PETG cantilevers. PETG lasts; PLA creeps if left bent. Store the model with the tongue centred and the pods out of the bays.
