"""Overall views of the whole model, phases 1 and 2 assembled: the pad at the window end,
the 6 m wire with the pods, the handover and the switch yard on the floor.

Run:  .venv/bin/python scale_down/make_overall.py
    -> scale_down/render_overall.png (perspective, print colours)
       scale_down/render_overall_dimensioned.png (elevation and plan with the main dimensions)
The wire is drawn 8 mm thick so it shows at this scale; the real one is 1.5 mm.
"""
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection
from matplotlib.patches import FancyArrowPatch

import make_pad_elevation as E
import make_pad_parts as M
import make_parts as P
import make_renders as R

HERE = Path(__file__).resolve().parent
INK, GRAPHITE = "#18283a", "#56636f"
COL = dict(R.COL)
COL.update({"white": (0.90, 0.91, 0.93), "lgrey": (0.70, 0.73, 0.76), "dgrey": (0.30, 0.33, 0.37), "orange": (0.89, 0.34, 0.06),
            "wire": (0.20, 0.25, 0.32), "blue": (0.17, 0.39, 0.56)})

SPAN = 6000.0                       # horizontal, wire saddle to handover nose
HANDOVER_X0 = -200.0                # handover nose block starts here (yard coordinates: turnout plate at x = 0)
Z_YARD_HEAD = 4.0 + P.HEAD_Z        # rail head above the floor at the yard (strip 4 mm + 47.75)
Z_RAMP_TOP = Z_YARD_HEAD + 14.0 + 1.0
Z_SADDLE = E.TILE_H + M.ACCESS_Z + 26.0   # wire groove in the saddle: tile + 840 + 26
SAG = 110.0


def wire_curve(n=60):
    x0, z0 = HANDOVER_X0 - SPAN, Z_SADDLE
    x1, z1 = HANDOVER_X0 + 10.0, Z_RAMP_TOP
    t = np.linspace(0, 1, n)
    x = x0 + (x1 - x0) * t
    z = z0 + (z1 - z0) * t - 4 * SAG * t * (1 - t)
    return x, z


def wire_mesh(radius=4.0):
    x, z = wire_curve()
    segs = []
    for i in range(len(x) - 1):
        a, b = np.array([x[i], 0, z[i]]), np.array([x[i + 1], 0, z[i + 1]])
        segs.append(trimesh.creation.cylinder(radius=radius, segment=[a, b], sections=8))
    return trimesh.util.concatenate(segs)


def pods_on_wire():
    """Three pods: one in the start gate, one a third of the way down, one entering bay 1."""
    x, z = wire_curve()
    out = []
    for t in (0.03, 0.35):
        i = int(t * (len(x) - 1))
        slope = math.degrees(math.atan2(z[i + 1] - z[i], x[i + 1] - x[i]))
        for m in R.pod(x[i], 0, z[i] - 4.0):
            # pitch the pod to the wire
            c = np.array([x[i], 0, z[i]])
            m.apply_translation(-c)
            m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-slope), [0, 1, 0]))
            m.apply_translation(c)
            out.append((m, "blue"))
    return out


def scene():
    pieces = []
    # yard (phase 1), floor-level strip top at z = 4 above the floor: shift by +4
    for m, c in R.yard():
        m = m.copy(); m.apply_translation([0, 0, 4.0])
        pieces.append((m, c if c != "pod" else "blue"))
    # pad (phase 2) at the window end: tower axis under the wire start, rocket 300 further out
    pad_dx = HANDOVER_X0 - SPAN - M.TOWER_W / 2 - 24 - M.OFFSET   # saddle on the tower's near face
    for m, c in E.assembled():
        m = m.copy(); m.apply_translation([pad_dx, 0, 0])
        pieces.append((m, c))
    pieces.append((wire_mesh(), "wire"))
    pieces += pods_on_wire()
    return pieces


def render_perspective(pieces):
    fig = plt.figure(figsize=(26, 6))
    ax = fig.add_subplot(111, projection="3d")
    light = np.array([0.3, -0.6, 0.75])
    allv = []
    for m, col in pieces:
        v = m.vertices
        allv.append(v)
        shade = np.clip(0.45 + 0.55 * np.abs(m.face_normals @ light), 0, 1)
        base = np.array(COL[col])
        ax.add_collection3d(__import__("mpl_toolkits.mplot3d.art3d", fromlist=["Poly3DCollection"]).Poly3DCollection(
            v[m.faces], facecolors=np.clip(base[None, :] * shade[:, None] + 0.06, 0, 1), edgecolor="none"))
    allv = np.vstack(allv)
    lo, hi = allv.min(axis=0), allv.max(axis=0)
    ext = np.maximum(hi - lo, 1.0)
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1] - 600, hi[1] + 600); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect((ext[0], ext[1] + 1200, ext[2]), zoom=1.0)
    ax.set_proj_type("ortho")
    ax.view_init(14, -72)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    out = HERE / "render_overall.png"
    fig.savefig(out, dpi=260, facecolor="white")
    plt.close(fig)
    from PIL import Image, ImageChops
    im = Image.open(out).convert("RGB")
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bbox:
        im.crop((max(bbox[0] - 30, 0), max(bbox[1] - 30, 0), min(bbox[2] + 30, im.width), min(bbox[3] + 30, im.height))).save(out)
    print("wrote", out.name)


def ortho(ax, pieces, axes, depth_sign, light_axis):
    for m, col in pieces:
        v, n = m.vertices, m.face_normals
        depth = ({0, 1, 2} - set(axes)).pop()
        order = np.argsort(v[m.faces].mean(axis=1)[:, depth] * depth_sign)
        faces = m.faces[order]
        shade = np.clip(0.5 + 0.5 * np.abs(n[order] @ np.eye(3)[light_axis]), 0, 1)
        base = np.array(COL[col])
        ax.add_collection(PolyCollection(v[faces][:, :, axes], facecolors=np.clip(base[None, :] * shade[:, None] + 0.05, 0, 1), edgecolors="none"))


def dim_h(ax, x0, x1, y, text, above=False):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="<->", mutation_scale=9, lw=0.8, color=GRAPHITE))
    ax.text((x0 + x1) / 2, y + (12 if above else -12), text, color=INK, fontsize=8.5, ha="center", va="bottom" if above else "top", bbox=dict(fc="white", ec="none", pad=0.4))


def dim_v(ax, x, z0, z1, text, side=1):
    ax.add_patch(FancyArrowPatch((x, z0), (x, z1), arrowstyle="<->", mutation_scale=9, lw=0.8, color=GRAPHITE))
    ax.text(x + 12 * side, (z0 + z1) / 2, text, color=INK, fontsize=8.5, ha="left" if side > 0 else "right", va="center", bbox=dict(fc="white", ec="none", pad=0.4))


def render_dimensioned(pieces):
    fig, (a, b) = plt.subplots(2, 1, figsize=(22, 9), gridspec_kw={"height_ratios": [1.6, 1]})
    allv = np.vstack([m.vertices for m, _ in pieces])
    xmin, xmax = allv[:, 0].min(), allv[:, 0].max()
    ymin, ymax = allv[:, 1].min(), allv[:, 1].max()
    zmax = allv[:, 2].max()
    yard_end = max(m.vertices[:, 0].max() for m, c in pieces if c in ("rail", "net", "plate", "chain", "mech"))
    # ---- elevation
    ax = a
    ortho(ax, pieces, (0, 2), 1, 1)
    ax.plot([xmin - 150, xmax + 150], [0, 0], color=GRAPHITE, lw=1)
    x_sad = HANDOVER_X0 - SPAN
    dim_h(ax, x_sad, HANDOVER_X0, zmax + 120, f"wire span {SPAN:.0f} mm (300 m at 1:50)", above=True)
    dim_v(ax, x_sad + 420, 0, Z_SADDLE, f"wire leaves the tower at {Z_SADDLE:.0f} mm (42 m level);\nthe window hook, not the tower, takes the pull", side=1)
    dim_v(ax, HANDOVER_X0 - SPAN / 2, Z_YARD_HEAD, Z_SADDLE, f"drop {Z_SADDLE - Z_YARD_HEAD:.0f} mm (41 m)", side=1)
    dim_v(ax, yard_end + 60, 0, Z_YARD_HEAD, f"rail head {Z_YARD_HEAD:.0f} mm", side=1)
    dim_v(ax, xmin - 60, 0, zmax, f"pad {zmax:.0f} mm tall", side=-1)
    dim_h(ax, HANDOVER_X0, yard_end, -90, f"yard {yard_end - HANDOVER_X0:.0f} mm: handover 200 · turnout 236 · bays 674")
    dim_h(ax, xmin, xmax, -200, f"overall {xmax - xmin:.0f} mm ({(xmax - xmin) / 1000:.1f} m) from the far booster to the last bumper")
    ax.set_xlim(xmin - 400, xmax + 500); ax.set_ylim(-280, zmax + 260)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Elevation: phase 2 (pad) at the window end, phase 1 (wire, pods, yard) to the floor. True proportions, mm.", fontsize=10, color=INK)
    # ---- plan
    ax = b
    ortho(ax, pieces, (0, 1), -1, 2)
    dim_h(ax, x_sad - M.OFFSET - 24 - M.TOWER_W / 2, x_sad - 24 - M.TOWER_W / 2, ymax + 120, f"rocket axis to tower axis {M.OFFSET:.0f}", above=True)
    dim_v(ax, xmax + 60, -146, 146, "bays 146 apart at the bumpers", side=1)
    dim_v(ax, xmin - 60, -2 * M.PAD_TILE / 2 - 60, 2 * M.PAD_TILE / 2 - 60, f"platform {2 * M.PAD_TILE:.0f}", side=-1)
    dim_h(ax, 0, 236, ymin - 60, "turnout plate 236 × 155")
    ax.set_xlim(xmin - 400, xmax + 500); ax.set_ylim(ymin - 160, ymax + 220)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Plan: the three bays fan out at 9.65°; the wire runs straight from the tower saddle to the handover and on under the yard.", fontsize=10, color=INK)
    fig.tight_layout()
    out = HERE / "render_overall_dimensioned.png"
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    print("wrote", out.name, f"overall {xmax - xmin:.0f} x {ymax - ymin:.0f} x {zmax:.0f} mm")


if __name__ == "__main__":
    s = scene()
    render_perspective(s)
    render_dimensioned(s)
