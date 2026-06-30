# Run inside FreeCAD:
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('scale_down/check/freecad_check.py').read())"
# Reads check/freecad_scene (written by freecad_export.py), turns every mesh into an OpenCascade
# solid, measures the common volume of each listed pair with FreeCAD's own booleans, and saves
# check/phase1_assembly.FCStd (meshes, coloured) to open in FreeCAD.
import json
import os

import FreeCAD
import Mesh
import Part

ROOT = os.path.join(os.getcwd(), "scale_down", "check")
SCENE = os.path.join(ROOT, "freecad_scene")
data = json.load(open(os.path.join(SCENE, "scene.json")))
COL = {"grey": (0.72, 0.74, 0.77), "orange": (0.89, 0.40, 0.10), "blue": (0.17, 0.39, 0.56)}

solids = {}


def solid(name):
    if name not in solids:
        m = Mesh.Mesh(os.path.join(SCENE, data["scene"][name]["file"] + ".stl"))
        sh = Part.Shape()
        sh.makeShapeFromMesh(m.Topology, 0.01)
        s = Part.makeSolid(sh)
        s = s.removeSplitter() if s.isValid() else s
        solids[name] = s
    return solids[name]


rows = []
bad = []
for a, b, expect in data["pairs"]:
    sa, sb = solid(a), solid(b)
    if not sa.BoundBox.intersect(sb.BoundBox):
        continue
    try:
        v = sa.common(sb).Volume
    except Exception as e:  # noqa: BLE001
        v = float("nan")
    rows.append((a, b, expect, v))
    if expect == "clear" and not v <= 0.05:
        bad.append((a, b, v))

lines = ["# FreeCAD cross-check (OpenCascade booleans on the exported meshes)", "",
         f"FreeCAD {'.'.join(FreeCAD.Version()[:3])}. {len(data['pairs'])} pairs listed, {len(rows)} with overlapping bounding boxes measured.", "",
         "| Part | Part | Expected | Common volume mm³ |", "|---|---|---|---:|"]
for a, b, e, v in rows:
    if v > 0.0005 or e != "clear":
        lines.append(f"| {a} | {b} | {e} | {v:.3f} |")
lines += ["", f"Pairs expected clear that overlap by more than 0.05 mm³: {len(bad)}"]
for a, b, v in bad:
    lines.append(f"- {a} / {b}: {v:.3f}")
open(os.path.join(ROOT, "freecad_report.md"), "w").write("\n".join(lines) + "\n")

# assembly file: meshes, coloured, grouped
doc = FreeCAD.newDocument("PLE_SBS_phase1")
groups = {}
for name, v in data["scene"].items():
    if v["group"] == "alt":
        continue
    g = groups.get(v["group"])
    if g is None:
        g = doc.addObject("App::DocumentObjectGroup", v["group"].replace(" ", "_"))
        groups[v["group"]] = g
    obj = doc.addObject("Mesh::Feature", name)
    obj.Mesh = Mesh.Mesh(os.path.join(SCENE, v["file"] + ".stl"))
    g.addObject(obj)
doc.recompute()
doc.saveAs(os.path.join(ROOT, "phase1_assembly.FCStd"))
print("\n".join(lines))
