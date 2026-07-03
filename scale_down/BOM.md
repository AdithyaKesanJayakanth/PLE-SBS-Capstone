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
| Diameter | 1.5 mm nominal, 1.4 to 1.6 mm works | The start gate's slot and bore are 1.9 mm, the handover groove 1.9 mm, the wagon's lip slot 2.6 mm; the gate key and the hook's wedge grip anything from 1.4 to 1.6 mm. A 2 mm wire will not fit |
| Grade | AISI 316 (A4, marine) or AISI 304 (A2) | Either is fine indoors; 316 is the common stock item |
| Lay | Right-hand regular lay | Standard; no preference beyond what the shop has |
| Minimum breaking load | about 1.4 kN (140 kgf); check the seller's figure | The model runs at 50 to 80 N, a safety factor of about 20 |
| Weight | about 9 g/m | Self-weight sag over 6 m is under 2 mm at working tension; the pods set the sag |
| Length | 10 m on a reel or coil | 6 m span, 1 m round the window hook, 2 m on under the yard to the furniture leg, 1 m spare |
| Condition | No kinks, ends taped by the shop | A kink stops the trolley; never buy a bent offcut |

**Tension.** There is no turnbuckle; tension is set by hand at the floor tie-off and checked by sag. With one ballasted pod (about 0.4 kg) at mid-span, pull until the wire hangs 100 to 120 mm below the straight line between the two ends. That is about 50 to 80 N. Tighter gives a flatter, faster ride; slacker makes the last metre too flat and the pod stalls, which is the paper's Figure 4 in miniature.

**Cutting and ends.** Wrap tape round the cut point and cut through the tape with a cable cutter or a sharp side cutter at the very tip; wire snips crush the strands. Leave the tape on both ends so they cannot unlay. No ferrules or clips are needed: each end is held by three turns round a capstan post plus a wedge.

**Full-size, for comparison.** The paper's design uses 36 mm galvanised steel wire rope, 6×36 IWRC, extra improved plow steel (ASTM A1023), minimum breaking load 907 kN, at 150 kN tension. Scaled by 1:50 that would be 0.72 mm; the model's 1.5 mm is twice as thick because the trolleys need something to grip, and diameter does not affect the ride.

## 2. Already at home

| Item | Used for |
|---|---|
| PLA filament, about 885 g, and PETG, about 189 g (slicer figures, phase 1) | all parts; section 3 says which is which |
| Coins or steel washers | ballast: 0.1 to 0.5 kg per pod, the same in both panniers; about 15 g in the rocker's cup; a few in each sled |
| Sewing thread, about 30 cm | links the flap's crank to the rocker's outer arm (the trigger) |
| Books or a water bottle | weight on the turnout plate and the handover so the yard cannot creep |
| A heavy piece of furniture (bed or sofa leg) beyond the yard | the wire runs on under the yard and ties off here, so the handover carries almost none of the pull |
| Phone with slow-motion video, tape measure | timing runs (see docs/scale-model-protocol.md in the repository) |

## 3. Printed parts (phase 1, version 2)

Files are in `stl/`, each already in its print orientation, written by `make_parts.py`; `parts.csv` is the same list. Grams are OrcaSlicer's for the P1S profiles (`print_pack/README.md` has the times): **1,074 g in all, about 31.8 hours**. If you printed version 1, `print_pack/phase1/reprint_v2/README.md` lists the 19 files to print now (about 876 g) and the 7 you already have.

| File | Qty | Filament | Colour | g (slicer) | Size on the bed (mm) | What it is |
|---|---:|---|---|---:|---|---|
| fit_coupon_x1.stl | 1 | PETG | Orange | 21.5 | 118.0 × 36.0 × 15.0 | print first: posts and bored rings at 0.15 to 0.40 mm per side |
| wheel_x6.stl | 6 | PLA | Cobalt Blue | 20.9 | 24.0 × 24.0 × 8.0 | V-groove wheel; rides the wire and the rail head |
| axle_pin_x6.stl | 6 | PETG | Orange | 3.4 | 8.0 × 8.0 × 32.4 | 4 mm pin through pannier, plate, wheel, plate, pannier; snap bump |
| trolley_plate_x6.stl | 6 | PLA | Cobalt Blue | 49.1 | 64.0 × 40.0 × 15.8 | two identical plates per wagon; prints flat, peg up |
| pannier_x6.stl | 6 | PLA | Cobalt Blue | 105.2 | 64.0 × 10.2 × 54.8 | basket; two identical per wagon, clamped by the axle pins |
| turnout_base_x1.stl | 1 | PLA | Light Grey | 159.9 | 249.0 × 155.0 × 109.0 | plate, entry and exit rails, pivot, stops, rocker bridges, gantry posts |
| tongue_x1.stl | 1 | PLA | Orange | 22.2 | 106.0 × 88.7 × 49.5 | switch blade with the ring of four teeth |
| rocker_bridge_x1.stl | 1 | PLA | Light Grey | 6.6 | 39.4 × 53.0 × 17.0 | two beams over the tooth ring; carries the rocker pin and the tilt stops; sits on four pegs |
| rocker_x1.stl | 1 | PLA | Orange | 8.3 | 30.6 × 77.0 × 13.4 | escapement rocker; prints upside down |
| rocker_pin_x1.stl | 1 | PETG | Orange | 0.5 | 6.5 × 6.5 × 44.0 | 3 mm rocker axle with snap bump |
| bias_spring_x1.stl | 1 | PETG | Orange | 1.0 | 67.4 × 2.2 × 8.0 | leaf spring that pushes the tongue toward the next lane |
| flap_x1.stl | 1 | PLA | Orange | 14.8 | 34.5 × 114.0 × 9.0 | trigger flap with crank; prints on its downstream face |
| gantry_axle_x1.stl | 1 | PETG | Orange | 2.1 | 4.0 × 134.0 × 3.5 | 4 mm flap axle, prints on its flat |
| handover_x1.stl | 1 | PLA | Light Grey | 49.1 | 212.0 × 40.0 × 53.5 | wire-to-rail handover; the wire dives through it |
| window_hook_x1.stl | 1 | PETG | Orange | 49.6 | 84.0 × 74.0 × 46.0 | top anchor: capstan post and wedge pocket |
| wedge_x1.stl | 1 | PETG | Orange | 3.2 | 32.0 × 5.4 × 22.0 | pinches the wire in the window hook |
| lead_rail_230_x3.stl | 3 | PLA | Light Grey | 131.5 | 242.0 × 22.0 × 53.5 | first bay segment, narrow strip |
| brake_comb_190_x3.stl | 3 | PLA | Light Grey | 150.5 | 202.0 × 40.0 × 53.5 | rail with 12 leaves under the right basket and the chain trough under the left |
| chain_bed_190_x3.stl | 3 | PLA | Light Grey | 132.9 | 202.0 × 40.0 × 53.5 | rail with the chain trough, end to end; the sled starts here |
| chain_11_links_x3.stl | 3 | PLA | Light Grey | 17.1 | 156.0 × 10.0 × 10.0 | print-in-place drag chain |
| sled_x3.stl | 3 | PLA | Light Grey | 10.0 | 20.0 × 13.0 × 22.0 | pushed by the left basket; drags the chain tied to its back |
| bumper_x3.stl | 3 | PETG | Orange | 106.2 | 64.0 × 40.0 × 56.0 | zig-zag spring at the end of each bay |
| start_gate_x1.stl | 1 | PLA | Light Grey | 5.8 | 30.0 × 14.0 × 25.0 | clamps on the wire behind the waiting wagon |
| gate_lever_x1.stl | 1 | PLA | Light Grey | 1.4 | 28.9 × 28.5 × 4.6 | hook over the wagon's rear spacer peg |
| gate_key_x1.stl | 1 | PETG | Orange | 0.7 | 30.0 × 3.1 × 6.6 | tapered key that locks the gate on the wire |
| gate_pin_x1.stl | 1 | PETG | Orange | 0.4 | 6.0 × 6.0 × 26.0 | lever pivot pin |

Colours are a suggestion: blue for the wagons, orange for everything that moves or flexes, light grey for the yard.

## 4. Fits and tolerances

Every running fit is **0.2 mm per side** (`CLR = 0.2` at the top of `make_parts.py`). Dimensions along each part's print direction are multiples of the 0.2 mm layer where a fit depends on them (plate 3.6, thrust boss 0.4). Each one was measured on the assembled model by `check/assembly_check.py`, which moves one part against the other until they touch.

| Fit | Parts | Nominal | Hole or gap | Measured play |
|---|---|---|---|---:|
| Wheel on axle pin | wheel, axle_pin | Ø4.0 | Ø4.4 | 0.21 radial |
| Wheel between the thrust bosses | wheel, trolley_plate | 8.0 wide | 8.4 | 0.20 each side |
| Axle pin through plate and pannier arm | trolley_plate, pannier, axle_pin | Ø4.0 | Ø4.4 (teardrop in the arm) | 0.2 |
| Spacer peg in the other plate | trolley_plate | Ø5.0, 3 mm deep | Ø5.4 | 0.21 |
| Plate gap, set by the peg shoulders | trolley_plate | 9.2 | the shoulders meet the other plate's face | 0 (fixed) |
| Guide lips on the rail web | trolley_plate, any rail | 2.0 web | 3.0 slot | 0.50 each side (a printed blade is not straight to less) |
| Rail-strip dovetails | every rail segment, turnout, handover, bumper | dovetail | +0.2 all round | 0.19 / 0.20 |
| Tongue on its pivot post | tongue, turnout_base | Ø6.0 | Ø6.4 | 0.2 |
| Rocker pin in the rocker and the bridge notches | rocker_pin, rocker, rocker_bridge | Ø3.0 | Ø3.4, notch mouth 3.2 | 0.2 |
| Axle pin head to snap bump | axle_pin | 28.4 stack | 29.1 | 0.7 (the gap is set by the shoulders, not the pin) |
| Flap on its axle | flap, gantry_axle | Ø4.0 | Ø4.4 | 0.2 |
| Gate lever on its pin | gate_lever, start_gate, gate_pin | Ø3.0 | Ø3.4 | 0.2 |
| Spring foot in its socket | bias_spring, turnout_base | 4.0 × 2.2 | 4.4 × 2.6 | 0.2 |
| Rocker bridge on its pegs | rocker_bridge, turnout_base | Ø4.0 × 3 | Ø4.4 | 0.2 |

Deliberate exceptions, which are not running fits:

| Feature | Gap | Why |
|---|---|---|
| Print-in-place chain links | 0.4 mm | parts printed already linked need a wider gap or they fuse |
| Gantry axle snap notches | 3.6 mouth on a 4 mm axle | the axle clicks in and stays |
| Wire in the handover groove | 1.9 mm for 1.5 | the wire lies in it |
| Gate key and window-hook wedge | tapered | they close onto the wire: about 10 mm of key (on the uphill side) and 8 mm of wedge stay showing |

Print `fit_coupon_x1` first. Its rings are bored at 0.15 to 0.40 mm per side; the first one that turns freely on the post without wobble is your printer's clearance. If it is not 0.20, change `CLR`, run `make_parts.py` and `check/assembly_check.py`, and re-slice.

## 5. Print settings (P1S, 0.4 mm nozzle)

The sliced files in `print_pack/phase1/sliced_p1s/` already carry these.

| Parts | Layer | Walls | Infill | Brim |
|---|---|---|---|---|
| wheels, pins, axles, wedge, key, coupon | 0.12 | 4 | 100 % | 3 mm |
| rocker | 0.12 | 4 | 25 % | 3 mm |
| rocker bridge | 0.20 | 4 | 25 % | 3 mm, tree supports under the two beams |
| bias spring, chain | 0.12 | 4 | 100 % | 3 mm / none |
| bumper | 0.12 | 4 | 25 % | 3 mm |
| plates, panniers, flap, sled, hook, gate, lever | 0.20 | 4 | 25 % | 3 mm |
| turnout, tongue, handover, rails, combs, chain beds | 0.20 | 5 | 25 % | none |

Only the rocker bridge is sliced with supports (tree supports under its two 46 mm beams, which otherwise sag toward the teeth). No other part needs them. Overhangs were measured on every STL (`check/assembly_report.md`, section 9): the only flat ceilings are bridges held at both ends (the rocker bridge's beams, 36 mm; the coin cup, 22 mm; trough and groove roofs), and the steep faces are the rail heads, the wheel's upper flank and the comb leaves, as in version 1.

## 6. Scale and what is and is not to scale

- Wire: 1:50 in length and drop. A 6 m span with a 0.9 m drop stands for 300 m from a 45 m crew access level.
- Pods: Froude scaling, as in the paper. A 3 s model run stands for about 21 s full size (√50).
- Switch yard: the logic is modelled exactly (one shared wire, points that index themselves, a bay per pod, passive brake, chain bed, backup stop). The bay lengths are compressed and the brake is friction, not eddy current, so the yard shows the logic, not the numbers.

## 7. Making the mechanism work first time

1. **Coupon first.** Settle `CLR` with `fit_coupon_x1` before printing anything else.
2. **One wagon on one rail.** Assemble a wagon (see the README) and push it along a lead rail: it should roll on the head with the lips clear of the web, and lift 0.4 mm before the lips touch the head.
3. **Tongue and spring.** Hold the tongue pointing between lanes R and C, a finger's width forward of the pivot post and just above it; slide it back so its round boss passes under the end of the entry rail, and lower it onto the post. Swing it to the right-hand stop, then drop the spring's foot into its socket with the leaf bent against the tongue's tab. The tongue should swing from stop to stop and the spring should carry it all the way to the left stop.
4. **Rocker bridge.** Lower it over the ring of teeth so its four holes drop onto the plate's pegs.
5. **Rocker.** Pin pushed through the rocker, then dropped into the bridge notches. With about 15 g in the cup the rocker rests outer side down. Swing the tongue right by hand and let go: finger A must stop it on the first tooth, at bay R.
6. **Flap and thread.** Click the axle into the gantry notches with the flap on it. Tie the thread from the crank's hole to the rocker's outer hole, straight but not lifting the rocker; anything from tight to 1.5 mm slack works. Lift the flap by hand: the rocker tips, the tongue moves half a step; lower it: the tongue lands on bay C. Again: bay L.
7. **Reset.** Lift the rocker out of its notches, swing the tongue to the right stop, drop the rocker back.
8. **Lubricate dry.** Pencil graphite or dry PTFE on the pivot post, the teeth and the fingers; never oil, which softens PLA.
9. **Springs tire.** The leaf spring, the comb leaves and the bumpers are PETG or PLA cantilevers. Store the model with the tongue at bay L (the spring least bent) and the pods out of the bays.
