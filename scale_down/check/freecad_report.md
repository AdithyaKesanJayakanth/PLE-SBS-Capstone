# FreeCAD cross-check (OpenCascade booleans on the exported meshes)

FreeCAD 1.1.4. 1066 pairs listed, 159 with overlapping bounding boxes measured.

| Part | Part | Expected | Common volume mm³ |
|---|---|---|---:|
| tongue_L | spring | contact | 0.106 |
| brake_L | chainbed_L | clear | 0.002 |
| chainbed_L | bumper_L | clear | 0.002 |
| brake_R | chainbed_R | clear | 0.002 |
| chainbed_R | bumper_R | clear | 0.001 |
| tongue_R | rocker_rest | contact | 0.000 |
| tongue_C | rocker_rest | contact | 0.000 |
| tongue_L | rocker_rest | contact | 0.000 |

Pairs expected clear that overlap by more than 0.05 mm³: 0
