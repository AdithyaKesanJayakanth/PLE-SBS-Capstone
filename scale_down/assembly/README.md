# Phase 1: step-by-step assembly, checked in FreeCAD

Screenshots rendered by FreeCAD from the part files (`freecad_render.py`), placed by `make_storyboard.py`. Every move shown here was collision-checked: `path_check_report.md` (exact booleans) and `freecad_motion_report.md` (FreeCAD's own booleans).

- Insertion paths clear: 31 of 31
- Three-wagon run: 0 clashes
- FreeCAD motion check: 0 unexplained overlaps over 512 frames

Animations: `video/phase1_wagon.mp4`, `video/phase1_yard.mp4`, `video/phase1_ends.mp4`, `video/phase1_run.mp4`.

## Wagon

Two identical plates, two wheels, two identical panniers and two printed axle pins. There are no screws: each pin goes through pannier, plate, wheel, plate and pannier, and its split end snaps out of the far side.

![The parts of one wagon: two identical plates, two wheels, two identical panniers, two axle pins. No screws: the pins snap in.](steps/wagon_00_parts.png)

![1. Plate R, bosses and spacer peg facing the middle. (Do this lying flat on the table, peg up.)](steps/wagon_01_plate.png)

![2. A wheel on each thrust boss, groove centred over the axle hole.](steps/wagon_02_wheels.png)

![3. Plate L on top, turned end for end: its peg goes into plate R's hole and plate R's peg into its hole.](steps/wagon_03_plate_L.png)

![4. Stand the sandwich up. Hold a pannier against each plate, arm holes in line with the axle holes.](steps/wagon_04_panniers.png)

![5. Push the front axle pin through from the right until the split end clicks out of the far pannier.](steps/wagon_05_pin_front.png)

![6. Same for the rear pin. The wheels now spin freely with 0.2 mm side play.](steps/wagon_06_pin_rear.png)

![7. Hang it on the wire: lower it so the wire passes up between the baskets, through the slot between the lips, into the wheel grooves.](steps/wagon_07_on_wire.png)

## Yard

Always lower the piece with the slot onto the piece with the tab. The tongue goes in before the rocker bridge, and slides under the end of the entry rail.

![1. Handover on the floor at the foot of the wire.](steps/yard_01_handover.png)

![2. Turnout plate: lower its entry slot straight down over the handover's tab (always lower the slot onto the tab).](steps/yard_02_turnout.png)

![3. Three lead rails: each slot drops over the tab of the piece before.](steps/yard_03_lead.png)

![4. Three brake combs: each slot drops over the tab of the piece before.](steps/yard_04_brake.png)

![5. Three chain beds: each slot drops over the tab of the piece before.](steps/yard_05_chainbed.png)

![6. Three bumpers: each slot drops over the tab of the piece before.](steps/yard_06_bumper.png)

![7. Swing it to the right-hand stop.](steps/yard_07_tongue.png)

![8. Leaf spring: bend the leaf toward the tongue's tab and drop the foot into its socket. It pushes the tongue toward bay L.](steps/yard_08_spring.png)

![9. Rocker bridge: lower it over the ring of teeth so its four holes drop onto the plate's pegs.](steps/yard_09_bridge.png)

![10. Push the 3 mm pin through the rocker's bore until the split end clicks out of the far side.](steps/yard_10_rocker_pin.png)

![11. About 15 g of coins or washers in the cup on the outer arm.](steps/yard_11_coins.png)

![12. Lower the rocker, cup side outward, so the pin drops into the two bridge notches. Finger A falls in front of the first tooth.](steps/yard_12_rocker.png)

![13. Let go of the tongue: the spring carries it 0.69° until its tooth stops on finger A. The points are set for bay R.](steps/yard_13_set_R.png)

![14. Slide the 4 mm axle through the flap's hub.](steps/yard_14_axle.png)

![15. Press the axle down into the two post notches until it clicks; the flap hangs free.](steps/yard_15_flap.png)

![16. Thread from the crank's hole to the hole at the end of the rocker's arm, straight but not lifting the rocker (0 to 1.5 mm slack).](steps/yard_16_thread.png)

![17. In each chain bed: the sled in the trough just past the start, coins in it, the chain in the trough ahead of it.](steps/yard_17_sleds.png)

![18. Lay the wire: in the groove on the handover's head, down the dive slot, along the groove under the handover and the turnout, on to the furniture leg.](steps/yard_18_wire.png)

## Wire ends and start gate

The window hook holds the wire with three turns and a wedge. The start gate hangs on the wire, is locked by a tapered key, and holds the waiting wagon by its rear spacer peg.

![Window end: three turns of wire round the capstan post, the tail laid along the pocket floor.](steps/ends_01_hook_wire.png)

![Push the wedge in from the open end over the wire until it is tight; about 8 mm stays out. Then hang the hook on the grill.](steps/ends_02_wedge.png)

![Start gate: lower the clamp onto the wire about 0.3 m below the hook; the wire goes up the slot into the bore.](steps/ends_03_gate.png)

![From the uphill end, slide the tapered key in beside the wire until it grips; about 10 mm stays out, pointing away from the wagon.](steps/ends_04_key.png)

![Drop the lever between the lugs.](steps/ends_05_lever.png)

![Push the 3 mm pin through the lugs and the lever.](steps/ends_06_pin.png)

![Hang a wagon below the gate and push it back: its rear spacer peg lifts the hook, which drops in front of the peg.](steps/ends_07_latched.png)

![To release, lift the lever about 20°: the hook clears the peg and the wagon rolls away down the wire.](steps/ends_08_release.png)

## Three wagons

Each wagon rolls down the wire, lands on the rail head at the same height, crosses the tongue, lifts the flap, and stops in its own bay. The flap rocks the escapement and the spring steps the tongue to the next bay.

![Wagon 1 of 3 → bay R: the left basket pushes the sled and chain; stopped 60 mm on](steps/run_1_R_stopped.png)

![Wagon 2 of 3 → bay C: the left basket pushes the sled and chain; stopped 60 mm on](steps/run_2_C_stopped.png)

![Wagon 3 of 3 → bay L: the left basket pushes the sled and chain; stopped 60 mm on](steps/run_3_L_stopped.png)

## Moving parts

The positions every moving part can take, each checked against everything around it.

![Tongue held at bay R (-9.56°): finger A down on a tooth, finger B up.](steps/moving_tongue_R.png)

![Tongue held at bay C (+0.09°): finger A down on a tooth, finger B up.](steps/moving_tongue_C.png)

![Tongue held at bay L (+9.73°): finger A down on a tooth, finger B up.](steps/moving_tongue_L.png)

![Rocker tipped by the thread: A up, B down; the tongue has sprung half a step to -4.87° and B holds it.](steps/moving_rocker_tipped.png)

![Flap swung 0°](steps/moving_flap_00.png)

![Flap swung 20°](steps/moving_flap_20.png)

![Flap swung 40°](steps/moving_flap_40.png)
