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

import make_parts as P

HERE = Path(__file__).resolve().parent
STL = HERE / "stl"
COL = {"rail": (0.38, 0.52, 0.66), "plate": (0.80, 0.84, 0.88), "pod": (0.17, 0.39, 0.56), "mech": (0.89, 0.34, 0.06),
       "spring": (0.14, 0.48, 0.23), "chain": (0.54, 0.48, 0.35), "net": (0.89, 0.34, 0.06)}


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


def pod(x, y, z, yaw=0.0):
    """A pod with the rail head at (x, y, z): plates, wheels, panniers."""
    parts = []
    plate = load("trolley_plate_x6")
    pa = place(plate, 0, 4.5, 0)                       # inner face at y = +4.5 ... plate y 0..3.5 -> translate so inner face at 4.5
    pb = place(plate, 0, -4.5, 0, yaw=180)
    parts += [pa, pb]
    wheel = load("wheel_x6")
    for ax_ in (-P.AXLE_PITCH / 2, P.AXLE_PITCH / 2):
        w = wheel.copy()
        w.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90), [1, 0, 0]))
        w.apply_transform(trimesh.transformations.translation_matrix([ax_, P.WHEEL_W / 2, P.AXLE_Z]))
        parts.append(w)
    parts.append(load("pannier_right_x3"))
    parts.append(load("pannier_left_x3"))
    out = []
    for m in parts:
        m = place(m, 0, 0, -P.W_Z, yaw=0)             # pod coordinates: rail head at z = W_Z -> bring head to 0
        out.append(place(m, x, y, z, yaw=yaw))
    return out


def lane(yaw, y_tip):
    """One bay along its lane, starting at the turnout exit tab."""
    x_exit = P.TONGUE_X0 + P.TONGUE_L + 2.0
    L, y0, y1 = P.PLATE
    a = math.radians(yaw)
    start = np.array([x_exit + (L - x_exit) * math.cos(a) + 12 * math.cos(a), y_tip + (L - x_exit) * math.sin(a) + 12 * math.sin(a)])
    pieces = []
    s = start.copy()
    for name, length, col in [("lead_rail_230_x3", 230, "rail"), ("brake_comb_190_x3", 190, "rail"), ("chain_bed_190_x3", 190, "rail"), ("bumper_x3", 60, "net")]:
        pieces.append((place(load(name), s[0], s[1], 0, yaw=yaw), col))
        if name.startswith("chain_bed"):
            ch = place(load("chain_11_links_x3"), 14, -14, -2, 0)
            pieces.append((place(ch, s[0], s[1], 0, yaw=yaw), "chain"))
        s = s + (length + 12) * np.array([math.cos(a), math.sin(a)])
    return pieces


def yard():
    pieces = [(place(load("handover_x1"), -222 + 0, 0, 0), "plate"),
              (load("turnout_base_x1"), "plate"),
              (place(load("tongue_x1"), P.TONGUE_X0, 0, 0, yaw=P.LANE_ANG), "mech"),
              (place(load("indexer_x1"), P.CAM_X, P.CAM_Y, 0), "mech")]
    for k in range(4):
        pieces.append((place(load("star_arm_x4"), P.CAM_X, P.CAM_Y, 62.7, yaw=90 * k), "mech"))
    for k, yaw in ((1, P.LANE_ANG), (0, 0.0), (-1, -P.LANE_ANG)):
        pieces += lane(yaw, k * P.TIP_OFF)
    # pods: one stopped in bay 1, one braking in bay 2, one on the entry rail
    x_exit = P.TONGUE_X0 + P.TONGUE_L + 2.0
    a = math.radians(P.LANE_ANG)
    d1 = (236 - x_exit) + 12 + 230 + 12 + 120
    pieces += [(m, "pod") for m in pod(x_exit + d1 * math.cos(a), P.TIP_OFF + d1 * math.sin(a), P.HEAD_Z, yaw=P.LANE_ANG)]
    d2 = (236 - x_exit) + 12 + 230 + 12 + 40
    pieces += [(m, "pod") for m in pod(x_exit + d2, 0, P.HEAD_Z)]
    pieces += [(m, "pod") for m in pod(-120, 0, P.HEAD_Z + 14 * (1 - 102 / 110) + 0.6)]
    return pieces


def render(pieces, out, elev, azim, figsize=(14, 7), title="", zoom=None):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    light = np.array([0.3, -0.6, 0.75])
    allv = []
    for m, col in pieces:
        v = m.vertices
        allv.append(v)
        shade = np.clip(0.45 + 0.55 * np.abs(m.face_normals @ light), 0, 1)
        base = np.array(COL[col])
        fc = np.clip(base[None, :] * shade[:, None] + 0.08, 0, 1)
        ax.add_collection3d(Poly3DCollection(v[m.faces], facecolors=fc, edgecolor="none"))
    allv = np.vstack(allv)
    if zoom:
        lo, hi = np.array(zoom[0]), np.array(zoom[1])
    else:
        lo, hi = allv.min(axis=0), allv.max(axis=0)
    ext = np.maximum(hi - lo, 1.0)
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(ext / ext.max()), zoom=1.12 if zoom is None else 1.2)   # true proportions, filling the frame
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
    render(y, HERE / "render_yard.png", 30, -62, title="Rendered from the STL files: handover, turnout with the self-indexing points, three bays, three pods. Not a photograph.")
    render(y, HERE / "render_turnout.png", 38, -48, figsize=(10, 7), zoom=((-30, -90, -10), (340, 130, 90)),
           title="Rendered from the STL files: tongue, cam and four-arm star on the turnout plate.")
    rail = load("lead_rail_230_x3"); rail.apply_translation([-115, 0, 0])
    render([(m, "pod") for m in pod(0, 0, P.HEAD_Z)] + [(rail, "rail")],
           HERE / "render_pod.png", 42, -132, figsize=(8, 6), title="Rendered from the STL files: one pod on the rail.")
