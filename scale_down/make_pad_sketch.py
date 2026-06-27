"""Phase 2: the launch pad and rocket at 1:50, dimensioned, with the print-segment breakdown.

Run:  .venv/bin/python scale_down/make_pad_sketch.py   -> scale_down/sketch_8_pad_phase2.png
The pad is cosmetic: the wire's pull goes to the window hook, not to the printed tower.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parent
INK, GRAPHITE, STEEL, HAZARD, RULE, WHITE = "#18283a", "#56636f", "#2c6390", "#e4570e", "#c8d0d8", "#f7f8fa"
plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "font.size": 8})

S = 50.0
# full-size (m) -> model (mm): x 1000 / 50 = x 20
ROCKET_H, CORE_D, BOOSTER_D, BOOSTER_H, CAPSULE_H = 48.0, 4.0, 3.2, 26.0, 8.0
TOWER_H, TOWER_W, ACCESS_H, OFFSET = 50.0, 8.0, 42.0, 15.0
PAD_W, PAD_T = 24.0, 1.5


def mm(x):
    return x * 1000.0 / S


def dim(ax, p0, p1, text, off=(0, 0), color=GRAPHITE, fs=7.5):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<->", mutation_scale=8, lw=0.7, color=color))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], text, color=color, ha="center", va="center", fontsize=fs,
            bbox=dict(fc="white", ec="none", pad=0.5))


def main():
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 7.2), gridspec_kw={"width_ratios": [1.5, 1]})
    for ax in (a, b):
        ax.set_aspect("equal"); ax.axis("off")

    # ---- elevation (model mm) ----
    ax = a
    ax.add_patch(Rectangle((-mm(PAD_W) / 2, -mm(PAD_T)), mm(PAD_W), mm(PAD_T), fc=RULE, ec=GRAPHITE, lw=0.7))      # launch platform
    # boosters
    for sgn in (-1, 1):
        x = sgn * (mm(CORE_D) / 2 + mm(BOOSTER_D) / 2)
        ax.add_patch(Rectangle((x - mm(BOOSTER_D) / 2, 0), mm(BOOSTER_D), mm(BOOSTER_H), fc="#e3e8ed", ec=GRAPHITE, lw=0.6))
        ax.add_patch(Polygon([(x - mm(BOOSTER_D) / 2, mm(BOOSTER_H)), (x + mm(BOOSTER_D) / 2, mm(BOOSTER_H)), (x, mm(BOOSTER_H) + 40)], fc="#e3e8ed", ec=GRAPHITE, lw=0.6))
    # core and capsule
    core_h = mm(ROCKET_H - CAPSULE_H)
    ax.add_patch(Rectangle((-mm(CORE_D) / 2, 0), mm(CORE_D), core_h, fc=WHITE, ec=GRAPHITE, lw=0.7))
    ax.add_patch(Polygon([(-mm(CORE_D) / 2, core_h), (mm(CORE_D) / 2, core_h), (mm(CORE_D) / 4, core_h + mm(CAPSULE_H) * 0.6), (-mm(CORE_D) / 4, core_h + mm(CAPSULE_H) * 0.6)], fc=WHITE, ec=GRAPHITE, lw=0.7))
    ax.add_patch(Polygon([(-mm(CORE_D) / 4, core_h + mm(CAPSULE_H) * 0.6), (mm(CORE_D) / 4, core_h + mm(CAPSULE_H) * 0.6), (0, mm(ROCKET_H))], fc=WHITE, ec=GRAPHITE, lw=0.7))
    # segment lines on the core (200 mm prints)
    for k in range(1, 4):
        ax.plot([-mm(CORE_D) / 2, mm(CORE_D) / 2], [200 * k, 200 * k], color=GRAPHITE, lw=0.5, ls=":")
    # tower
    tx = mm(OFFSET)
    ax.add_patch(Rectangle((tx - mm(TOWER_W) / 2, 0), mm(TOWER_W), mm(TOWER_H), fc="#dde3e9", ec=INK, lw=0.8))
    for k in range(1, 4):
        ax.plot([tx - mm(TOWER_W) / 2, tx + mm(TOWER_W) / 2], [250 * k, 250 * k], color=INK, lw=0.5, ls=":")
    for y in range(0, int(mm(TOWER_H)), 50):
        ax.plot([tx - mm(TOWER_W) / 2, tx + mm(TOWER_W) / 2], [y, y + 50], color=GRAPHITE, lw=0.3)
    # access arm from the tower to the capsule at 42 m
    ax.add_patch(Rectangle((mm(CORE_D) / 2 + 4, mm(ACCESS_H) - 6), tx - mm(TOWER_W) / 2 - mm(CORE_D) / 2 - 4, 12, fc=HAZARD, ec=HAZARD))
    ax.plot(tx - mm(TOWER_W) / 2, mm(ACCESS_H), "o", color=INK, ms=4)
    # the wire: leaves the access level, runs over the tower side to the window hook (off to the right)
    ax.plot([tx + mm(TOWER_W) / 2, tx + 260], [mm(ACCESS_H) + 20, mm(ACCESS_H) + 32], color=STEEL, lw=1.6)
    ax.text(tx + 200, mm(ACCESS_H) + 70, "wire to the window hook\n(the hook carries the pull,\nnot the tower)", color=STEEL, fontsize=7, ha="center")
    # dimensions
    dim(ax, (-mm(PAD_W) / 2 - 70, 0), (-mm(PAD_W) / 2 - 70, mm(ROCKET_H)), f"rocket {mm(ROCKET_H):.0f} mm\n({ROCKET_H:.0f} m)", off=(-55, 0))
    dim(ax, (tx + mm(TOWER_W) / 2 + 40, 0), (tx + mm(TOWER_W) / 2 + 40, mm(TOWER_H)), f"tower {mm(TOWER_H):.0f} mm\n({TOWER_H:.0f} m)", off=(60, 0))
    dim(ax, (tx + mm(TOWER_W) / 2 + 110, 0), (tx + mm(TOWER_W) / 2 + 110, mm(ACCESS_H)), f"crew access\n{mm(ACCESS_H):.0f} mm ({ACCESS_H:.0f} m)", off=(70, 0))
    dim(ax, (0, -60), (tx, -60), f"offset {mm(OFFSET):.0f} mm (15 m)", off=(0, -16))
    dim(ax, (-mm(PAD_W) / 2, -110), (mm(PAD_W) / 2, -110), f"platform {mm(PAD_W):.0f} × {mm(PAD_W):.0f} mm (24 m), four 240 mm tiles", off=(0, -16))
    dim(ax, (-mm(CORE_D) / 2, mm(ROCKET_H) + 40), (mm(CORE_D) / 2, mm(ROCKET_H) + 40), f"core Ø{mm(CORE_D):.0f}", off=(0, 16))
    dim(ax, (mm(CORE_D) / 2, mm(BOOSTER_H) + 70), (mm(CORE_D) / 2 + mm(BOOSTER_D), mm(BOOSTER_H) + 70), f"booster Ø{mm(BOOSTER_D):.0f}, {mm(BOOSTER_H):.0f} tall", off=(0, 18))
    dim(ax, (tx - mm(TOWER_W) / 2, mm(TOWER_H) + 40), (tx + mm(TOWER_W) / 2, mm(TOWER_H) + 40), f"tower {mm(TOWER_W):.0f} × {mm(TOWER_W):.0f}", off=(0, 16))
    ax.text(0, -190, "Elevation, model millimetres. Dotted lines: joints between printed segments, 200 mm core, 240 mm tower (P1S bed 256 mm).", ha="center", fontsize=7.5, color=GRAPHITE)
    ax.set_xlim(-mm(PAD_W) / 2 - 160, tx + 320); ax.set_ylim(-220, mm(TOWER_H) + 90)
    ax.set_title("Phase 2: generic pad and reference launcher at 1:50", fontsize=9)

    # ---- plan ----
    ax = b
    ax.add_patch(Rectangle((-mm(PAD_W) / 2, -mm(PAD_W) / 2), mm(PAD_W), mm(PAD_W), fc=RULE, ec=GRAPHITE, lw=0.7))
    ax.plot([0, 0], [-mm(PAD_W) / 2, mm(PAD_W) / 2], color=GRAPHITE, lw=0.4, ls=":")
    ax.plot([-mm(PAD_W) / 2, mm(PAD_W) / 2], [0, 0], color=GRAPHITE, lw=0.4, ls=":")
    ax.add_patch(Circle((0, 0), mm(CORE_D) / 2, fc=WHITE, ec=GRAPHITE, lw=0.7))
    for sgn in (-1, 1):
        ax.add_patch(Circle((0, sgn * (mm(CORE_D) / 2 + mm(BOOSTER_D) / 2)), mm(BOOSTER_D) / 2, fc="#e3e8ed", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((tx - mm(TOWER_W) / 2, -mm(TOWER_W) / 2), mm(TOWER_W), mm(TOWER_W), fc="#dde3e9", ec=INK, lw=0.8))
    ax.add_patch(Rectangle((mm(CORE_D) / 2 + 4, -6), tx - mm(TOWER_W) / 2 - mm(CORE_D) / 2 - 4, 12, fc=HAZARD, ec=HAZARD))
    ax.annotate("", (tx + 150, 0), (tx + mm(TOWER_W) / 2, 0), arrowprops=dict(arrowstyle="->", color=STEEL, lw=1.4))
    ax.text(tx + 80, 14, "wire", color=STEEL, fontsize=7.5)
    ax.text(0, -mm(PAD_W) / 2 - 24, "Plan. Tiles 240 × 240 mm, joined with the same dovetails as the yard.", ha="center", fontsize=7.5, color=GRAPHITE)
    dim(ax, (tx - mm(TOWER_W) / 2, mm(TOWER_W) / 2 + 30), (tx + mm(TOWER_W) / 2, mm(TOWER_W) / 2 + 30), f"{mm(TOWER_W):.0f}", off=(0, 14))
    dim(ax, (-mm(PAD_W) / 2 - 30, -mm(PAD_W) / 2), (-mm(PAD_W) / 2 - 30, mm(PAD_W) / 2), f"{mm(PAD_W):.0f}", off=(-22, 0))
    ax.set_xlim(-mm(PAD_W) / 2 - 70, tx + 180); ax.set_ylim(-mm(PAD_W) / 2 - 50, mm(PAD_W) / 2 + 70)
    ax.set_title("Plan", fontsize=9)

    fig.suptitle("Launch pad and rocket, phase 2 (cosmetic; stands at the window end under the hook). Dimensions in mm at 1:50; full size in brackets.", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_8_pad_phase2.png", dpi=180)
    print("wrote scale_down/sketch_8_pad_phase2.png")


if __name__ == "__main__":
    main()
