# FreeCAD GUI macro: one shaded picture of every phase-1 part, in its filament colour.
#   PLESBS_ROOT=<scale_down> /Applications/FreeCAD.app/Contents/MacOS/FreeCAD scale_down/freecad_part_renders.py
# Reads stl/*.stl and parts.csv, writes print_pack/phase1/renders/<part>.png.
import csv
import os
import traceback

import FreeCAD
import FreeCADGui
import Mesh

ROOT = os.environ.get("PLESBS_ROOT", os.path.join(os.getcwd(), "scale_down"))
OUT = os.path.join(ROOT, "print_pack", "phase1", "renders")
RGB = {"Cobalt Blue": (0.00, 0.34, 0.72), "Light Grey": (0.80, 0.82, 0.84), "Orange": (0.98, 0.45, 0.10)}
LOG = open(os.path.join(ROOT, "print_pack", "phase1", "renders_log.txt"), "w")

try:
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(os.path.join(ROOT, "parts.csv"))))
    doc = FreeCAD.newDocument("parts")
    view = FreeCADGui.ActiveDocument.ActiveView
    for r in rows:
        name = r["file"][:-4]
        f = doc.addObject("Mesh::Feature", name)
        f.Mesh = Mesh.Mesh(os.path.join(ROOT, "stl", r["file"]))
        doc.recompute()
        f.ViewObject.ShapeColor = RGB.get(r["colour"], (0.6, 0.6, 0.6))
        try:
            f.ViewObject.CreaseAngle = 35.0
        except Exception:
            pass
        FreeCADGui.updateGui()
        view.viewIsometric()
        view.fitAll()
        view.saveImage(os.path.join(OUT, name + ".png"), 1200, 800, "White")
        f.ViewObject.Visibility = False
        LOG.write(name + "\n")
        LOG.flush()
    LOG.write("DONE\n")
except Exception:
    LOG.write(traceback.format_exc())
LOG.close()
os._exit(0)
