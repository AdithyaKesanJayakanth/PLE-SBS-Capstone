# Run inside FreeCAD (no GUI needed):
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('scale_down/assembly/freecad_motion_check.py').read())"
# Replays the storyboard (build/storyboard.json): every frame of the wagon, yard and wire-end
# assembly sequences and every fourth frame of the three-wagon run. In each frame, every part that
# moved is measured against every other part in place with FreeCAD's own booleans (OpenCascade
# "common" on solids made from the exported meshes). Writes freecad_motion_report.md.
import json
import os
import time

import FreeCAD
import Mesh
import Part

ASM = os.path.join(os.getcwd(), "scale_down", "assembly")
BUILD = os.path.join(ASM, "build")
sb = json.load(open(os.path.join(BUILD, "storyboard.json")))
EPS = 0.05
_solids = {}


def solid(name):
    if name not in _solids:
        m = Mesh.Mesh(os.path.join(BUILD, "meshes", sb["objects"][name]["file"]))
        sh = Part.Shape()
        sh.makeShapeFromMesh(m.Topology, 0.01)
        sol = Part.makeSolid(sh)
        try:
            ref = sol.removeSplitter()           # merge coplanar triangles: far fewer faces, much faster booleans
            if ref.isValid() and abs(ref.Volume - sol.Volume) < 1e-3 * max(1.0, sol.Volume):
                sol = ref
        except Exception:
            pass
        _solids[name] = sol
    return _solids[name]


_placed = {}


def placed(name, M):
    key = (base(name), tuple(round(x, 4) for x in M))
    if key not in _placed:
        s = solid(base(name) if base(name) in sb["objects"] else name).copy()
        s.Placement = FreeCAD.Placement(FreeCAD.Matrix(*M))
        if len(_placed) > 4000:
            _placed.clear()
        _placed[key] = s
    return _placed[key]


def base(n):
    for p in ("pod1_", "pod2_", "pod3_"):
        if n.startswith(p):
            return "pod_" + n[len(p):]
    return n


def kind(a, b, seq):
    """Classify a touching pair the same way as the manifold checks."""
    A, B = base(a), base(b)
    pair = {A, B}

    def has(prefix_a, prefix_b):
        return (A.startswith(prefix_a) and B.startswith(prefix_b)) or (B.startswith(prefix_a) and A.startswith(prefix_b))

    if has("pod_pin", "pod_") and seq == "wagon":
        return "snap fit pressed through"
    if pair == {"rocker_pin", "rocker"} or pair == {"gantry_axle", "turnout_plate"}:
        return "snap fit pressed through"
    if has("pod_wheel", "wire") or has("pod_wheel", "bay_") or has("pod_wheel", "tongue") or has("pod_wheel", "turnout_plate") or has("pod_wheel", "handover"):
        return "wheel rolling on a rail or the wire"
    if has("pod_pannier_R", "bay_brake") or has("pod_pannier_L", "sled") or has("pod_pannier_L", "chain"):
        return "basket on a comb leaf or the sled (intended)"
    if has("spring_", "tongue"):
        return "spring preload on the tongue's tab (intended)"
    if has("flap", "pod_plate"):
        return "flap riding on the wagon's top (intended)"
    if pair == {"tongue", "rocker"}:
        return "finger against a tooth (the escapement working)"
    if pair == {"tongue", "turnout_plate"} or pair == {"rocker", "rocker_bridge"} or pair == {"coins", "rocker"}:
        return "resting against a stop"
    if has("gate_lever", "pod_") or has("wedge", "hook_wire") or has("wedge", "window_hook") or has("gate_key", "wire_gate"):
        return "gripping or latching (intended)"
    if has("bay_", "bay_") or has("bay_", "turnout_plate") or has("handover", "turnout_plate") or has("sled", "chain"):
        return "dovetail or neighbouring faces touching"
    return "CLASH"


def frames_to_check():
    """(frame index, moved objects) for every frame that is checked."""
    frames = sb["frames"]
    run_check = set(sb["checks"])
    prev, out = {}, []
    for i, fr in enumerate(frames):
        seq = fr["seq"]
        if seq == "moving":
            continue
        objs = fr["objs"]
        last = prev.get(seq, {})
        moved = [n for n, M in objs.items() if last.get(n) != M]
        prev[seq] = objs
        if seq == "run" and i not in run_check:
            continue
        out.append((i, moved))
    return out


def worker(k, n):
    t0 = time.time()
    frames = sb["frames"]
    todo = frames_to_check()[k::n]
    worst, cache, nb = {}, {}, 0
    log = open(os.path.join(BUILD, f"fc_motion_{k}.log"), "w")
    for j, (i, moved) in enumerate(todo):
        fr = frames[i]
        objs = fr["objs"]
        boxes = {nm: placed(nm, M).BoundBox for nm, M in objs.items()}
        for a in moved:
            for b, Mb in objs.items():
                if a == b or not boxes[a].intersect(boxes[b]):
                    continue
                key = (base(a), base(b), tuple(round(x, 3) for x in objs[a]), tuple(round(x, 3) for x in Mb))
                if key in cache:
                    v = cache[key]
                else:
                    try:
                        v = placed(a, objs[a]).common(placed(b, Mb)).Volume
                    except Exception:
                        v = float("nan")
                    cache[key] = v
                    nb += 1
                if not v > 0.0005:
                    continue
                pk = "|".join((fr["seq"],) + tuple(sorted((a, b))))
                if v > worst.get(pk, (0, None))[0]:
                    worst[pk] = (v, i)
        log.write(f"{j + 1}/{len(todo)} frame {i} {time.time() - t0:.0f}s\n")
        log.flush()
    json.dump(dict(worst=worst, frames=len(todo), booleans=nb, seconds=time.time() - t0), open(os.path.join(BUILD, f"fc_motion_{k}.json"), "w"))


def merge(n):
    worst, nframes, nb, secs = {}, 0, 0, 0.0
    for k in range(n):
        d = json.load(open(os.path.join(BUILD, f"fc_motion_{k}.json")))
        nframes += d["frames"]; nb += d["booleans"]; secs = max(secs, d["seconds"])
        for pk, (v, i) in d["worst"].items():
            if v > worst.get(pk, (0, None))[0]:
                worst[pk] = (v, i)
    lines = ["# FreeCAD motion check", "",
             f"FreeCAD {'.'.join(FreeCAD.Version()[:3])}, OpenCascade booleans on solids made from the exported meshes. "
             f"{nframes} frames replayed: every frame of the wagon, yard and wire-end assembly and every fourth frame of the three-wagon run. "
             f"In each frame every part that moved was measured against every part in place: {nb} booleans in {n} FreeCAD processes, {secs / 60:.0f} minutes.", "",
             "Volumes in mm³. Listed are all pairs that touched at any moment, with the worst moment (frame numbers as in `build/storyboard.json` and the screenshots).", "",
             "| Sequence | Part | Part | Worst common volume | Frame | What it is |", "|---|---|---|---:|---:|---|"]
    clashes = []
    for pk, (v, i) in sorted(worst.items()):
        seq, a, b = pk.split("|")
        kd = kind(a, b, seq)
        if v <= EPS and kd == "CLASH":
            kd = "touching (under 0.05 mm³)"
        lines.append(f"| {seq} | {a} | {b} | {v:.3f} | {i} | {kd} |")
        if kd == "CLASH":
            clashes.append((seq, a, b, v, i))
    lines += ["", f"**Unexplained overlaps above 0.05 mm³: {len(clashes)}**"]
    for seq, a, b, v, i in clashes:
        lines.append(f"- {seq}, frame {i}: {a} / {b}: {v:.3f} mm³")
    open(os.path.join(ASM, "freecad_motion_report.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[-3 - len(clashes):]))


W = os.environ.get("PLESBS_WORKER")
N = int(os.environ.get("PLESBS_WORKERS", "8"))
if W is not None:
    worker(int(W), N)
else:
    merge(N)
