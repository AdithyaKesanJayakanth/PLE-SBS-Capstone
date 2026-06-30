"""Rendered pictures of the print-only model, assembled from the STL files.

Run:  .venv/bin/python scale_down/make_renders.py
Writes scale_down/render_yard.png (the whole receiving end with three pods),
render_pod.png (one pod on the rail) and render_turnout.png (the points, cam and star).
These are renders of the design, not photographs; put photographs in scale_down/photos/.
"""
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "check"))
import make_parts as P
import assembly_check as A

HERE = Path(__file__).resolve().parent
STL = HERE / "stl"
COL = {"rail": (0.38, 0.52, 0.66), "plate": (0.80, 0.84, 0.88), "pod": (0.17, 0.39, 0.56), "mech": (0.89, 0.34, 0.06),
       "spring": (0.14, 0.48, 0.23), "chain": (0.54, 0.48, 0.35), "net": (0.89, 0.34, 0.06), "wire": (0.20, 0.25, 0.32)}


def load(name):
    return trimesh.load(STL / f"{name}.stl")


def place(m, x=0, y=0, z=0, yaw=0.0, mirror_y=False):
    m = m.copy()
    if mirror_y:
        m.apply_transform(np.diag([1, -1, 1, 1]))
        m.invert()
    T = trimesh.transformations.rotation_matrix(math.radians(yaw), [0, 0, 1])
    T[:3, 3] = [x, y, z]
    m.apply_transform(T)
    return m


def tm(m):
    """manifold3d solid to trimesh."""
    mm = m.to_mesh()
    v, f = trimesh.remesh.subdivide_to_size(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), max_edge=6.0)
    return trimesh.Trimesh(vertices=v, faces=f, process=False)       # small facets sort correctly in depth


def pod(x, y, z, yaw=0.0):
    """A wagon with the rail head (or the wire's equivalent) at height z: plates, wheels, panniers, pins."""
    return [tm(m) for _, m in A.pod_at(x, y, yaw, z=z - P.HEAD_Z + P.POD_Z)]


def yard():
    """The receiving end as assembled in check/assembly_check.py: tongue on L after two pods,
    pods 1 and 2 stopped in bays R and C, pod 3 coming down the handover."""
    pieces = [(tm(P.handover_in_yard()), "plate"), (tm(A.base_solid()), "plate"), (tm(A.tongue_at(P.THETA)), "mech"),
              (tm(A.rocker_at(P.REST_TILT)), "mech"), (tm(P.rocker_pin_in_yard()), "mech"), (tm(A.flap_at(0.0)), "mech"),
              (tm(P.gantry_axle()), "mech"), (tm(P.bias_spring(5.3)), "spring")]
    for k in P.LANES:
        for n, m, _ in A.bays(k):
            pieces.append((tm(m), "net" if n.startswith("bumper") else "rail"))
        sl, ch = A.sled_chain(k)
        pieces += [(tm(sl), "chain"), (tm(ch), "chain")]
    for k, u in (("R", 905.0), ("C", 900.0)):
        x, y, yaw = A.pod_pose(k, u)
        pieces += [(m, "pod") for m in pod(x, y, P.HEAD_Z, yaw)]
    pieces += [(m, "pod") for m in pod(-200, 0, P.HEAD_Z)]
    w = A.wire_solid() ^ P.box(700, 300, 120, (-500, -150, -10))
    pieces.append((tm(w), "wire"))
    return pieces


def render(pieces, out, elev, azim, figsize=(14, 7), title="", zoom=None):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    light = np.array([0.3, -0.6, 0.75])
    allv, tris, fcs = [], [], []
    for m, col in pieces:
        v = m.vertices
        t = v[m.faces]
        if zoom:                                   # keep only what is inside the view box
            c = t.mean(axis=1)
            keep = np.all((c >= np.array(zoom[0])) & (c <= np.array(zoom[1])), axis=1)
            t = t[keep]
            nrm = m.face_normals[keep]
        else:
            nrm = m.face_normals
        if not len(t):
            continue
        allv.append(t.reshape(-1, 3))
        shade = np.clip(0.45 + 0.55 * np.abs(nrm @ light), 0, 1)
        base = np.array(COL[col])
        tris.append(t)
        fcs.append(np.clip(base[None, :] * shade[:, None] + 0.08, 0, 1))
    # one collection, so every face is depth-sorted against every other
    ax.add_collection3d(Poly3DCollection(np.concatenate(tris), facecolors=np.concatenate(fcs), edgecolor="none"))
    allv = np.vstack(allv)
    if zoom:
        lo, hi = np.array(zoom[0]), np.array(zoom[1])
    else:
        lo, hi = allv.min(axis=0), allv.max(axis=0)
    ext = np.maximum(hi - lo, 1.0)
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(ext / ext.max()), zoom=0.98 if zoom is None else 1.15)   # true proportions, filling the frame
    ax.view_init(elev, azim)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    from PIL import Image, ImageChops
    im = Image.open(out).convert("RGB")
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bbox:
        pad = 24
        im.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0), min(bbox[2] + pad, im.width), min(bbox[3] + pad, im.height))).save(out)
    print("wrote", out.name)


if __name__ == "__main__":
    y = yard()
    render(y, HERE / "render_yard.png", 34, -58, title="")
    render(y, HERE / "render_turnout.png", 42, 128, figsize=(10, 7), zoom=((-5, -45, -5), (250, 105, 108)), title="")
    rail = tm(P.lead_rail().translate([-115, 0, 0]))
    render([(m, "pod") for m in pod(0, 0, P.HEAD_Z)] + [(rail, "rail")], HERE / "render_pod.png", 42, -132, figsize=(8, 6), title="")
