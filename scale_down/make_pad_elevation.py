"""Dimensioned elevation of the assembled phase-2 model, drawn from the STL files.

Run:  .venv/bin/python scale_down/make_pad_elevation.py  -> scale_down/render_pad_dimensioned.png
Heights are above the floor with the platform tiles in place (ribs down, 10 mm thick).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection
from matplotlib.patches import FancyArrowPatch

import make_pad_parts as M
import make_renders as R

HERE = Path(__file__).resolve().parent
OUT = HERE / "stl_phase2"
INK, GRAPHITE, HAZARD = "#18283a", "#56636f", "#e4570e"
COL = {"white": (0.90, 0.91, 0.93), "lgrey": (0.70, 0.73, 0.76), "dgrey": (0.30, 0.33, 0.37), "orange": (0.89, 0.34, 0.06)}
TILE_H = 10.0     # tile with ribs down: 8 mm ribs + 2 mm plate


def L(name):
    return trimesh.load(OUT / f"{name}.stl")


def assembled():
    z0 = TILE_H
    pieces = []
    for i in range(2):
        for j in range(2):
            t = L("platform_tile_x4")
            t.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))   # ribs down
            t.apply_translation(-t.bounds[0])
            pieces.append((R.place(t, -M.PAD_TILE + i * M.PAD_TILE, -M.PAD_TILE + j * M.PAD_TILE - 60, 0), "lgrey"))
    pieces.append((R.place(L("launch_mount_x1"), 0, 0, z0), "lgrey"))
    core_base = z0 + 12
    for k in range(4):
        pieces.append((R.place(L("core_segment_x4"), 0, 0, core_base + k * M.SEG_H), "white"))
    pieces.append((R.place(L("capsule_x1"), 0, 0, core_base + 4 * M.SEG_H), "white"))
    pitch = M.CORE_D / 2 + M.BOOST_D / 2 + 1.0
    for sgn in (-1, 1):
        pieces.append((R.place(L("booster_lower_x2"), 0, sgn * pitch, core_base), "lgrey"))
        pieces.append((R.place(L("booster_upper_x2"), 0, sgn * pitch, core_base + 240), "lgrey"))
    for k in range(4):
        pieces.append((R.place(L("tower_section_x4"), M.OFFSET, 0, z0 + k * M.TOWER_SEC), "dgrey"))
    pieces.append((R.place(L("tower_crown_x1"), M.OFFSET, 0, z0 + 4 * M.TOWER_SEC), "dgrey"))
    pieces.append((R.place(L("access_arm_x1"), M.OFFSET - M.TOWER_W / 2 + 4, 0, z0 + M.ACCESS_Z, yaw=180), "orange"))
    return pieces


def dim_v(ax, x, z0, z1, text, side=1):
    ax.add_patch(FancyArrowPatch((x, z0), (x, z1), arrowstyle="<->", mutation_scale=9, lw=0.8, color=GRAPHITE))
    ax.plot([x - 8, x + 8], [z0, z0], color=GRAPHITE, lw=0.5); ax.plot([x - 8, x + 8], [z1, z1], color=GRAPHITE, lw=0.5)
    ax.text(x + 10 * side, (z0 + z1) / 2, text, color=INK, fontsize=8, ha="left" if side > 0 else "right", va="center", bbox=dict(fc="white", ec="none", pad=0.4))


def dim_h(ax, x0, x1, z, text):
    ax.add_patch(FancyArrowPatch((x0, z), (x1, z), arrowstyle="<->", mutation_scale=9, lw=0.8, color=GRAPHITE))
    ax.text((x0 + x1) / 2, z - 14, text, color=INK, fontsize=8, ha="center", va="top", bbox=dict(fc="white", ec="none", pad=0.4))


def main():
    pieces = assembled()
    fig, ax = plt.subplots(figsize=(9, 11))
    allv = []
    for m, col in pieces:
        v, n = m.vertices, m.face_normals
        order = np.argsort(v[m.faces].mean(axis=1)[:, 1])          # view along +y: far faces first
        faces = m.faces[order]
        shade = np.clip(0.5 + 0.5 * np.abs(n[order] @ np.array([0, 1, 0])), 0, 1)
        base = np.array(COL[col])
        ax.add_collection(PolyCollection(v[faces][:, :, [0, 2]], facecolors=np.clip(base[None, :] * shade[:, None] + 0.05, 0, 1), edgecolors="none"))
        allv.append(v)
    allv = np.vstack(allv)
    tops = {k: max(m.bounds[1][2] for m, c in pieces if c == k) for k in COL}
    rocket_top = max(m.bounds[1][2] for m, c in pieces if c == "white")
    tower_top = max(m.bounds[1][2] for m, c in pieces if c == "dgrey")
    plate_top = TILE_H
    access = TILE_H + M.ACCESS_Z
    # floor line
    xmin, xmax = allv[:, 0].min(), allv[:, 0].max()
    ax.plot([xmin - 60, xmax + 180], [0, 0], color=GRAPHITE, lw=1)
    # dimensions
    dim_v(ax, xmin - 40, 0, rocket_top, f"rocket tip {rocket_top:.0f} mm above the floor\n({rocket_top * 50 / 1000:.1f} m at 1:50)", side=-1)
    dim_v(ax, xmax + 40, 0, tower_top, f"tower with crane {tower_top:.0f} mm\n({tower_top * 50 / 1000:.1f} m)", side=1)
    dim_v(ax, xmax + 110, 0, access, f"crew access arm {access:.0f} mm\n(42 m level, 840 above the platform)", side=1)
    dim_v(ax, xmax + 180, 0, plate_top, f"platform {plate_top:.0f}", side=1)
    dim_h(ax, 0, M.OFFSET, -40, f"rocket axis to tower axis {M.OFFSET:.0f} mm (15 m)")
    dim_h(ax, -M.PAD_TILE, M.PAD_TILE, -80, f"platform {2 * M.PAD_TILE:.0f} mm (four tiles)")
    overall = max(rocket_top, tower_top)
    ax.set_title(f"Phase 2 assembled, elevation from the STL files. Overall height {overall:.0f} mm. Dimensions in mm; floor at 0.", fontsize=10, color=INK)
    ax.set_xlim(xmin - 140, xmax + 330); ax.set_ylim(-110, overall + 40)
    ax.set_aspect("equal"); ax.axis("off")
    fig.tight_layout()
    fig.savefig(HERE / "render_pad_dimensioned.png", dpi=160, facecolor="white")
    print(f"rocket tip {rocket_top:.0f}, tower {tower_top:.0f}, access {access:.0f}, overall {overall:.0f} mm")


if __name__ == "__main__":
    main()
