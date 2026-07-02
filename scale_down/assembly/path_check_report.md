# Phase 1: assembly paths and the three-wagon run, checked

Every part is moved along the path you move it by hand, in small steps, and its overlap with the parts already in place is measured with exact booleans (manifold3d). A snap fit is expected to overlap while it is pressed through; everything else must stay clear. FreeCAD repeats the same measurements with its own booleans: `freecad_motion_report.md`.

## Wagon assembly: insertion paths
- two wheels laid on the thrust bosses over the axle holes: clear
- plate L laid on top, each spacer peg into the other plate's hole: clear
- both panniers held against the outer faces of the plates: clear
- axle pins pushed in from the right: arm, plate, wheel, plate, arm: clear; snap fits pressed through: pod_pin_front in pod_pannier_R (2.0 mm³ at the worst moment), pod_pin_rear in pod_pannier_R (2.0 mm³ at the worst moment), pod_pin_front in pod_plate_R (2.2 mm³ at the worst moment), pod_pin_rear in pod_plate_R (2.2 mm³ at the worst moment), pod_pin_front in pod_plate_L (2.2 mm³ at the worst moment), pod_pin_rear in pod_plate_L (2.2 mm³ at the worst moment), pod_pin_front in pod_wheel_front (2.2 mm³ at the worst moment), pod_pin_rear in pod_wheel_rear (2.2 mm³ at the worst moment), pod_pin_front in pod_pannier_L (2.0 mm³ at the worst moment), pod_pin_rear in pod_pannier_L (2.0 mm³ at the worst moment)
- axle pin shank alone at x = -20 (snap bump removed): clear
- axle pin shank alone at x = +20 (snap bump removed): clear
- wagon lowered onto the wire (the wire passes up between the baskets and through the 2.6 mm slot between the lips into the wheel grooves): plates, lips, panniers and pins clear all the way; the wheels touch the wire only as they sit down on it

## Yard assembly: insertion paths
- turnout plate lowered so its entry slot drops over the handover's dovetail tab: clear
- three lead segments lowered onto the previous dovetail tabs: clear
- three brake segments lowered onto the previous dovetail tabs: clear
- three chainbed segments lowered onto the previous dovetail tabs: clear
- three bumper segments lowered onto the previous dovetail tabs: clear
- tongue, held between lanes R and C, lowered to 10.5 mm, 6 mm forward of its post: clear
- tongue slid back 6 mm so its boss passes under the end of the entry rail: clear
- tongue lowered onto the pivot post: clear
- tongue swung on its post to the right-hand stop: clear (it touches the stop at the end)
- spring foot lowered into its socket with the leaf bent against the tab: clear
- rocker bridge lowered over the tooth ring onto its four pegs: clear
- rocker pin pushed through the rocker's bore (above the yard): clear; snap fits pressed through: rocker_pin in rocker (0.7 mm³ at the worst moment)
- rocker with pin lowered into the bridge notches, cup side down, tongue held at its right-hand stop: clear
- gantry axle slid through the flap's hub (above the yard): clear
- flap and axle pressed down into the gantry posts' snap notches: clear; snap fits pressed through: gantry_axle in turnout_plate (10.2 mm³ at the worst moment)
- sleds and chains laid in the chain-bed troughs: clear
- wire laid in the handover groove, down the dive slot and along the grooves underneath: clear

## Window hook and start gate
- wire wrapped on the hook's post and laid in its pocket: clear of the hook
- wedge pushed into the pocket over the wire until it grips: clear
- one millimetre further the wedge is already tight (overlap 61.88 mm³ with the wire and the pocket roof): it grips with about 8 mm showing
- gate clamp lowered onto the wire (the wire enters the slot in its underside): clear
- gate key slid in beside the wire: clear
- gate pin pushed through the lugs and the lever: clear
- wagon pushed back into the gate: the lever rides up over the peg and drops in front of it: clear
- latched wagon against the gate body, the key and the lever pin (the lever itself is meant to touch the peg): clear
- latched wagon's wheels against the gate body, the key and the lever pin: clear

## The run: three wagons down the wire, into bays R, C and L
- wagon 1 reached bay R; tongue now +0.09° (lanes: R -9.65, C 0.00, L +9.65)
- wagon 2 reached bay C; tongue now +9.73° (lanes: R -9.65, C 0.00, L +9.65)
- wagon 3 reached bay L; tongue now +9.73° (lanes: R -9.65, C 0.00, L +9.65)

### Tongue movements during the run
- pod1: tongue -9.56° → -9.46° while the rear wheel is 37 mm past the tongue's tip
- pod1: tongue -9.46° → -4.76° while the rear wheel is 50 mm past the tongue's tip
- pod1: tongue -4.76° → -4.85° while the rear wheel is 63 mm past the tongue's tip
- pod1: tongue -4.85° → +0.09° while the rear wheel is 102 mm past the tongue's tip
- pod2: tongue +0.09° → +0.22° while the rear wheel is 37 mm past the tongue's tip
- pod2: tongue +0.22° → +4.86° while the rear wheel is 50 mm past the tongue's tip
- pod2: tongue +4.86° → +4.79° while the rear wheel is 63 mm past the tongue's tip
- pod2: tongue +4.79° → +9.73° while the rear wheel is 102 mm past the tongue's tip
- pod3: tongue +9.73° → +9.84° while the rear wheel is 37 mm past the tongue's tip
- pod3: tongue +9.84° → +10.25° while the rear wheel is 50 mm past the tongue's tip
- pod3: tongue +10.25° → +9.73° while the rear wheel is 102 mm past the tongue's tip

- After the third wagon no tooth is left for finger B, so the tongue swings to its left-hand stop (+10.25°). When the flap falls, finger A comes down at the edge of the last tooth and, in this geometry, eases the tongue back to +9.73°, on lane L. If the coins are too light to do that, finger A simply rests on the tooth with the tongue at the stop, still on lane L. Either way nothing else runs until the reset (lift the rocker out, swing the tongue to the right-hand stop, drop the rocker back).

### Contacts seen in the run (worst overlap, mm³)
- intended: pod1 pannier_R / bay_brake_R: 172.06
- rolling: pod1 wheel_front / tongue: 0.23
- rolling: pod1 wheel_rear / tongue: 0.15
- rolling: pod1 wheel_rear / turnout_plate: 0.44
- intended: pod2 pannier_R / bay_brake_C: 173.54
- rolling: pod2 wheel_front / tongue: 0.15
- rolling: pod2 wheel_rear / tongue: 0.15
- intended: pod3 pannier_R / bay_brake_L: 172.06
- rolling: pod3 wheel_front / tongue: 0.27
- rolling: pod3 wheel_rear / tongue: 0.15
- rolling: pod3 wheel_rear / turnout_plate: 0.44
- no clashes: every contact is a wheel rolling over a rail joint, a basket on a comb leaf, or a basket on a sled

- landing at the handover nose with the wire arriving at 4.4°: plates, lips, panniers and pins against the handover and the wire, worst 0.00 mm³ (0 = clear; the wheels ride the wire into the groove and onto the head)

