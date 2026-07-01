# FreeCAD GUI macro: renders the phase-1 storyboard (build/storyboard.json) as screenshots.
#   PLESBS_ASM=<this folder> /Applications/FreeCAD.app/Contents/MacOS/FreeCAD scale_down/assembly/freecad_render.py
# Optional: PLESBS_SEQ=wagon,yard (only those sequences), PLESBS_RANGE=0:50 (frame range), PLESBS_SCALE=2 (supersampling).
# Writes build/frames/<sequence>/<frame>_<view>.png and exits.
import json
import math
import os
import traceback

import FreeCAD
import FreeCADGui
import Mesh
import Part

ASM = os.environ.get("PLESBS_ASM", os.path.join(os.getcwd(), "scale_down", "assembly"))
BUILD = os.path.join(ASM, "build")
LOG = open(os.path.join(BUILD, "render_log.txt"), "w")
SIZES = {"overview": (1920, 1080), "landing": (960, 540), "switch": (960, 540)}   # 16:9: very wide images come out off-centre
DEFAULT = (1600, 900)
SCALE = int(os.environ.get("PLESBS_SCALE", "1"))


def log(s):
    LOG.write(s + "\n")
    LOG.flush()


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def norm(a):
    n = math.sqrt(sum(x * x for x in a))
    return [x / n for x in a]


def camera_string(c):
    d = norm(c["dir"])
    up = c.get("up", [0, 0, 1])
    right = norm(cross(d, up))
    upo = cross(right, d)
    back = [-x for x in d]
    m = FreeCAD.Matrix(right[0], upo[0], back[0], 0, right[1], upo[1], back[1], 0, right[2], upo[2], back[2], 0, 0, 0, 0, 1)
    rot = FreeCAD.Placement(m).Rotation
    ax, ang = rot.Axis, rot.Angle
    t = c["target"]
    dist = 3000.0
    pos = [t[i] - d[i] * dist for i in range(3)]
    return ("#Inventor V2.1 ascii\nOrthographicCamera {\n viewportMapping ADJUST_CAMERA\n"
            f" position {pos[0]} {pos[1]} {pos[2]}\n orientation {ax.x} {ax.y} {ax.z} {ang}\n"
            f" nearDistance 10\n farDistance 6000\n aspectRatio 1\n focalDistance {dist}\n height {c['height']}\n}}\n")


def main():
    sb = json.load(open(os.path.join(BUILD, "storyboard.json")))
    seqs = os.environ.get("PLESBS_SEQ")
    seqs = set(seqs.split(",")) if seqs else None
    rng = os.environ.get("PLESBS_RANGE")
    lo, hi = (int(x) for x in rng.split(":")) if rng else (0, len(sb["frames"]))
    pick = os.environ.get("PLESBS_FRAMES")
    pick = {int(x) for x in pick.split(",")} if pick else None
    doc = FreeCAD.newDocument("PLE_SBS_phase1_assembly")
    objs = {}
    for name, o in sb["objects"].items():
        f = doc.addObject("Mesh::Feature", name)
        f.Mesh = Mesh.Mesh(os.path.join(BUILD, "meshes", o["file"]))
        objs[name] = f
    doc.recompute()
    for name, o in sb["objects"].items():
        vo = objs[name].ViewObject
        vo.ShapeColor = tuple(o["colour"])
        for prop, val in (("CreaseAngle", 35.0), ("Lighting", "Two side")):
            try:
                setattr(vo, prop, val)
            except Exception:
                pass
        vo.Visibility = False
    thread = doc.addObject("Part::Feature", "thread")
    thread.Shape = Part.makeCylinder(0.35, 10)
    thread.ViewObject.ShapeColor = (0.10, 0.10, 0.12)
    thread.ViewObject.Visibility = False
    view = FreeCADGui.ActiveDocument.ActiveView
    try:
        view.setAxisCross(False)
    except Exception:
        pass
    shown = set()
    for i, fr in enumerate(sb["frames"]):
        if i < lo or i >= hi or (seqs and fr["seq"] not in seqs) or (pick is not None and i not in pick):
            continue
        want = set(fr["objs"])
        for name in shown - want:
            objs[name].ViewObject.Visibility = False
        for name, M in fr["objs"].items():
            objs[name].Placement = FreeCAD.Placement(FreeCAD.Matrix(*M))
            if name not in shown:
                objs[name].ViewObject.Visibility = True
        shown = want
        if fr.get("thread"):
            p0, p1 = (FreeCAD.Vector(*p) for p in fr["thread"])
            v = p1 - p0
            thread.Shape = Part.makeCylinder(0.35, v.Length, p0, v)
            thread.ViewObject.Visibility = True
        else:
            thread.ViewObject.Visibility = False
        FreeCADGui.updateGui()
        out = os.path.join(BUILD, "frames", fr["seq"])
        os.makedirs(out, exist_ok=True)
        for vname in fr["views"]:
            view.setCamera(camera_string(sb["views"][vname]))
            w, h = SIZES.get(vname, DEFAULT)
            view.saveImage(os.path.join(out, f"{i:05d}_{vname}.png"), w * SCALE, h * SCALE, "White")
        log(f"frame {i} {fr['seq']} done")
    if os.environ.get("PLESBS_SAVE"):
        doc.saveAs(os.environ["PLESBS_SAVE"])


try:
    main()
    log("DONE")
except Exception:
    log(traceback.format_exc())
LOG.close()
os._exit(0)
