# FreeCAD motion check

FreeCAD 1.1.4, OpenCascade booleans on solids made from the exported meshes. 512 frames replayed: every frame of the wagon, yard and wire-end assembly and every fourth frame of the three-wagon run. In each frame every part that moved was measured against every part in place: 8980 booleans in 8 FreeCAD processes, 2 minutes.

Volumes in mm³. Listed are all pairs that touched at any moment, with the worst moment (frame numbers as in `build/storyboard.json` and the screenshots).

| Sequence | Part | Part | Worst common volume | Frame | What it is |
|---|---|---|---:|---:|---|
| ends | gate_key_placed | wire_gate | 0.044 | 346 | gripping or latching (intended) |
| ends | gate_lever | pod_plate_L | 3.983 | 404 | gripping or latching (intended) |
| ends | pod_wheel_front | wire_gate | 0.810 | 396 | wheel rolling on a rail or the wire |
| ends | pod_wheel_rear | wire_gate | 0.810 | 398 | wheel rolling on a rail or the wire |
| run | bay_brake_C | pod2_pannier_R | 173.537 | 648 | basket on a comb leaf or the sled (intended) |
| run | bay_brake_L | pod3_pannier_R | 164.595 | 771 | basket on a comb leaf or the sled (intended) |
| run | bay_brake_R | pod1_pannier_R | 164.595 | 509 | basket on a comb leaf or the sled (intended) |
| run | flap | pod1_plate_L | 0.024 | 481 | flap riding on the wagon's top (intended) |
| run | flap | pod1_plate_R | 0.024 | 481 | flap riding on the wagon's top (intended) |
| run | flap | pod2_plate_L | 0.025 | 612 | flap riding on the wagon's top (intended) |
| run | flap | pod2_plate_R | 0.025 | 612 | flap riding on the wagon's top (intended) |
| run | flap | pod3_plate_L | 0.024 | 743 | flap riding on the wagon's top (intended) |
| run | flap | pod3_plate_R | 0.024 | 743 | flap riding on the wagon's top (intended) |
| run | pod1_wheel_front | tongue | 0.068 | 473 | wheel rolling on a rail or the wire |
| run | pod1_wheel_front | wire | 0.653 | 413 | wheel rolling on a rail or the wire |
| run | pod1_wheel_rear | tongue | 0.070 | 473 | wheel rolling on a rail or the wire |
| run | pod1_wheel_rear | wire | 0.653 | 413 | wheel rolling on a rail or the wire |
| run | pod2_wheel_front | tongue | 0.068 | 604 | wheel rolling on a rail or the wire |
| run | pod2_wheel_front | wire | 0.653 | 544 | wheel rolling on a rail or the wire |
| run | pod2_wheel_rear | tongue | 0.070 | 604 | wheel rolling on a rail or the wire |
| run | pod2_wheel_rear | wire | 0.653 | 544 | wheel rolling on a rail or the wire |
| run | pod3_wheel_front | tongue | 0.068 | 735 | wheel rolling on a rail or the wire |
| run | pod3_wheel_front | wire | 0.653 | 675 | wheel rolling on a rail or the wire |
| run | pod3_wheel_rear | tongue | 0.070 | 735 | wheel rolling on a rail or the wire |
| run | pod3_wheel_rear | wire | 0.653 | 675 | wheel rolling on a rail or the wire |
| run | rocker | tongue | 0.050 | 481 | finger against a tooth (the escapement working) |
| wagon | pod_pannier_L | pod_pin_front | 1.951 | 59 | snap fit pressed through |
| wagon | pod_pannier_L | pod_pin_rear | 1.951 | 76 | snap fit pressed through |
| wagon | pod_pannier_R | pod_pin_front | 1.951 | 54 | snap fit pressed through |
| wagon | pod_pannier_R | pod_pin_rear | 1.951 | 71 | snap fit pressed through |
| wagon | pod_pin_front | pod_plate_L | 2.206 | 58 | snap fit pressed through |
| wagon | pod_pin_front | pod_plate_R | 2.206 | 55 | snap fit pressed through |
| wagon | pod_pin_front | pod_wheel_front | 2.206 | 56 | snap fit pressed through |
| wagon | pod_pin_rear | pod_plate_L | 2.206 | 75 | snap fit pressed through |
| wagon | pod_pin_rear | pod_plate_R | 2.206 | 72 | snap fit pressed through |
| wagon | pod_pin_rear | pod_wheel_rear | 2.206 | 74 | snap fit pressed through |
| wagon | pod_wheel_front | wire_short | 0.656 | 99 | wheel rolling on a rail or the wire |
| wagon | pod_wheel_rear | wire_short | 0.656 | 99 | wheel rolling on a rail or the wire |
| yard | gantry_axle | turnout_plate | 10.190 | 301 | snap fit pressed through |
| yard | rocker | rocker_pin | 0.744 | 236 | snap fit pressed through |
| yard | rocker | tongue | 0.050 | 277 | finger against a tooth (the escapement working) |
| yard | spring_16.0 | tongue | 0.049 | 274 | spring preload on the tongue's tab (intended) |

**Unexplained overlaps above 0.05 mm³: 0**
