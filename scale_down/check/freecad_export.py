"""Write the assembled phase-1 scenes as STL files plus a list of part pairs, for an independent
check in FreeCAD (check/freecad_check.py) and an assembly file you can open.

Run:  .venv/bin/python scale_down/check/freecad_export.py
      /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('scale_down/check/freecad_check.py').read())"
"""
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import assembly_check as A  # noqa: E402
import make_parts as P  # noqa: E402

OUT = HERE / "freecad_scene"


def save(m, name):
    mm = m.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mm.vert_properties)[:, :3], faces=np.asarray(mm.tri_verts), process=False)
    tm.export(OUT / f"{name}.stl")
    return name


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    scene, pairs = {}, []

    def add(name, m, colour, group):
        scene[name] = dict(file=save(m, name), colour=colour, group=group)

    # the yard, filled: tongue on L after two pods, rocker at rest, one wagon in each bay
    add("handover", P.handover_in_yard(), "grey", "yard")
    add("turnout_plate", A.base_solid(), "grey", "yard")
    add("tongue_L", A.tongue_at(P.THETA), "orange", "yard")
    add("rocker_rest", A.rocker_at(P.REST_TILT), "orange", "yard")
    add("rocker_pin", P.rocker_pin_in_yard(), "orange", "yard")
    add("flap", A.flap_at(0.0), "orange", "yard")
    add("gantry_axle", P.gantry_axle(), "orange", "yard")
    add("spring", P.bias_spring(5.3), "orange", "yard")
    for k in P.LANES:
        for n, m, _ in A.bays(k):
            add(n.replace(" ", "_"), m, "orange" if n.startswith("bumper") else "grey", "yard")
        sled, ch = A.sled_chain(k)
        add(f"sled_{k}", sled, "grey", "yard")
        add(f"chain_{k}", ch, "grey", "yard")
    # a wagon on each lane, part way along its lead rail
    for k, u in (("R", 700.0), ("C", 640.0), ("L", 580.0)):
        x, y, yaw = A.pod_pose(k, u)
        for n, m in A.pod_at(x, y, yaw, lift=0.03):
            add(f"wagon_{k}_{n.replace(' ', '_')}", m, "blue", f"wagon {k}")
    # pairs to measure in FreeCAD: (a, b, expected): expected "clear" or "contact"
    yard = [n for n, v in scene.items() if v["group"] == "yard"]
    for i in range(len(yard)):
        for j in range(i + 1, len(yard)):
            touch = {yard[i], yard[j]} == {"tongue_L", "spring"}      # the spring's preload on the tab
            pairs.append((yard[i], yard[j], "contact" if touch else "clear"))
    for k in P.LANES:
        wag = [n for n, v in scene.items() if v["group"] == f"wagon {k}"]
        for i in range(len(wag)):
            for j in range(i + 1, len(wag)):
                pairs.append((wag[i], wag[j], "clear"))
        for w in wag:
            for y in yard:
                pairs.append((w, y, "clear"))

    # the wagon alone, centred, for the separate wagon file
    for n, m in P.pod_parts():
        scene[f"pod_{n.replace(' ', '_')}"] = dict(file=save(m, f"pod_{n.replace(' ', '_')}"), colour="blue", group="pod")
    pod = [n for n, v in scene.items() if v["group"] == "pod"]
    for i in range(len(pod)):
        for j in range(i + 1, len(pod)):
            pairs.append((pod[i], pod[j], "clear"))
    # tongue at each lane and the rocker at rest against the plate and the tongue
    for lab, T in (("R", -P.THETA), ("C", 0.0)):
        n = f"tongue_{lab}"
        scene[n] = dict(file=save(A.tongue_at(T), n), colour="orange", group="alt")
        pairs.append((n, "turnout_plate", "clear"))
        pairs.append((n, "rocker_rest", "contact"))
    pairs.append(("tongue_L", "rocker_rest", "contact"))
    json.dump(dict(scene=scene, pairs=pairs), open(OUT / "scene.json", "w"), indent=1)
    print(f"wrote {len(scene)} meshes and {len(pairs)} pairs to {OUT}")


if __name__ == "__main__":
    main()
