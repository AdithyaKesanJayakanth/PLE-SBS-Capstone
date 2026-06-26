"""Phase 2 sketch: the launch pad and rocket at 1:50, dimensioned, as a side elevation and a plan.

Run:  .venv/bin/python scale_down/make_pad_drawing.py   -> scale_down/sketch_8_launchpad.png
The reference launcher and pad are the paper's (an LVM3-class crewed launcher on a generic 42 m crew-access pad,
tower 15 m from the rocket axis); the rocket's own dimensions are public LVM3 figures, rounded. Model mm = full-size
m x 20 (1:50). Segment lengths are kept under 240 mm for the P1S bed.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parent
INK, GRAPHITE, STEEL, HAZARD, RULE, SAND, WHITE = "#18283a", "#56636f", "#2c6390", "#e4570e", "#c8d0d8", "#8a7a5a", "#f4f4f2"
plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "font.size": 8})

# ── the model, in mm (full size in m x 20) ──
S = 20                      # mm per m
H_ROCKET = 43.5 * S         # 870
D_CORE = 4.0 * S            # 80
D_BOOST = 3.2 * S           # 64
L_BOOST = 25.0 * S          # 500
H_MOUNT = 4.0 * S           # 80, the launch pedestal
W_MOUNT = 12.0 * S          # 240
X_TOWER = 15.0 * S          # 300, rocket axis to tower axis
W_TOWER = 8.0 * S           # 160
H_TOWER = 48.0 * S          # 960
Z_ACCESS = 42.0 * S         # 840, the crew access level (the wire's anchor)
BASE_W, BASE_D = 560, 320   # the base plate (two tiles); the real deck is far larger
Z_CREW = H_MOUNT + 33.0 * S # 740, the crew module sits above the upper stage
H_CM = 4.0 * S              # 80, crew module cone
H_CES = 7.5 * S             # 150, the escape tower above it


def dim(ax, p0, p1, text, off=(0, 0), color=GRAPHITE, fs=7.5):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<->", mutation_scale=8, lw=0.7, color=color))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], text, color=color, ha="center", va="center", fontsize=fs,
            bbox=dict(fc="white", ec="none", pad=0.5))


def label(ax, xy, text, xytext, color=INK, fs=7.5):
    ax.annotate(text, xy, xytext, fontsize=fs, color=color, ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))


fig = plt.figure(figsize=(13, 9.2), dpi=160)
fig.patch.set_facecolor("white")
fig.text(0.02, 0.975, "PLE-SBS scale model, phase 2: the launch pad and rocket at 1:50 (model mm = full-size m × 20)", fontsize=11, color=INK, weight="bold", va="top")
fig.text(0.02, 0.948, "Reference launcher of the paper (LVM3-class, public figures rounded) on the generic 42 m crew-access pad, tower 15 m from the rocket. "
         "Every part prints on a Bambu Lab P1S in segments ≤ 240 mm.", fontsize=8, color=GRAPHITE, va="top")

# ═══ side elevation ═══
ax = fig.add_axes([0.04, 0.05, 0.56, 0.86])
ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-330, 560); ax.set_ylim(-60, 1080)
# base plate and the launch mount
ax.add_patch(Rectangle((-BASE_W / 2 + 60, -12), BASE_W, 12, fc=RULE, ec=GRAPHITE, lw=0.7))
ax.add_patch(Rectangle((-W_MOUNT / 2, 0), W_MOUNT, H_MOUNT, fc=SAND, ec=INK, lw=0.8))
ax.add_patch(Rectangle((-D_CORE / 2 - 14, 0), D_CORE + 28, H_MOUNT, fc="white", ec=INK, lw=0.6))   # the flame duct opening
# boosters
for sx in (-1, 1):
    x0 = sx * (D_CORE / 2 + D_BOOST / 2) - D_BOOST / 2
    ax.add_patch(Rectangle((x0, H_MOUNT), D_BOOST, L_BOOST, fc=WHITE, ec=INK, lw=0.8))
    ax.add_patch(Polygon([(x0, H_MOUNT + L_BOOST), (x0 + D_BOOST, H_MOUNT + L_BOOST), (x0 + D_BOOST / 2, H_MOUNT + L_BOOST + 2.4 * S)], fc=WHITE, ec=INK, lw=0.8))
# core and upper stage
ax.add_patch(Rectangle((-D_CORE / 2, H_MOUNT), D_CORE, Z_CREW - H_MOUNT, fc=WHITE, ec=INK, lw=0.9))
for k in range(1, 4):   # the four core segments stack on pins: joint lines
    ax.plot([-D_CORE / 2, D_CORE / 2], [H_MOUNT + k * 165] * 2, color=GRAPHITE, lw=0.6, ls=(0, (2, 2)))
for sx in (-1, 1):
    x0 = sx * (D_CORE / 2 + D_BOOST / 2) - D_BOOST / 2
    ax.plot([x0, x0 + D_BOOST], [H_MOUNT + 250] * 2, color=GRAPHITE, lw=0.6, ls=(0, (2, 2)))
ax.add_patch(Rectangle((-D_CORE / 2, H_MOUNT + 15 * S), D_CORE, 6 * S, fc="#f3d6c4", ec=INK, lw=0.6))   # the orange band, hypergolic core marking
# crew module and escape tower
ax.add_patch(Polygon([(-D_CORE / 2, Z_CREW), (D_CORE / 2, Z_CREW), (0.9 * S, Z_CREW + H_CM), (-0.9 * S, Z_CREW + H_CM)], fc=WHITE, ec=INK, lw=0.9))
ax.add_patch(Rectangle((-0.6 * S, Z_CREW + H_CM), 1.2 * S, H_CES - 1.2 * S, fc=WHITE, ec=INK, lw=0.8))
ax.add_patch(Polygon([(-0.6 * S, Z_CREW + H_CM + H_CES - 1.2 * S), (0.6 * S, Z_CREW + H_CM + H_CES - 1.2 * S), (0, Z_CREW + H_CM + H_CES)], fc=WHITE, ec=INK, lw=0.8))
# the umbilical tower: a lattice, four segments
tx0 = X_TOWER - W_TOWER / 2
ax.add_patch(Rectangle((tx0, 0), W_TOWER, H_TOWER, fc="none", ec=STEEL, lw=1.1))
for k in range(1, 4):
    ax.plot([tx0, tx0 + W_TOWER], [k * 240] * 2, color=STEEL, lw=1.1)     # segment joints
for z in range(0, int(H_TOWER), 80):
    ax.plot([tx0, tx0 + W_TOWER], [z, z + 80], color=STEEL, lw=0.4)
    ax.plot([tx0, tx0 + W_TOWER], [z + 80, z], color=STEEL, lw=0.4)
    ax.plot([tx0, tx0 + W_TOWER], [z, z], color=STEEL, lw=0.4)
# the crew access arm with its white room at the capsule, and the slidewire anchor
ax.add_patch(Rectangle((D_CORE / 2 + 1.2 * S, Z_ACCESS - 4), tx0 - D_CORE / 2 - 1.2 * S, 8, fc=STEEL, ec=STEEL))
ax.add_patch(Rectangle((D_CORE / 2, Z_ACCESS - 14), 1.2 * S + 6, 28, fc=WHITE, ec=INK, lw=0.7))
ax.add_patch(Circle((tx0 + W_TOWER + 4, Z_ACCESS + 10), 5, fc=HAZARD, ec=HAZARD))
ax.plot([tx0 + W_TOWER + 4, 545], [Z_ACCESS + 10, Z_ACCESS - 95], color=HAZARD, lw=1.2)
ax.text(548, Z_ACCESS - 120, "1.5 mm wire to the\nphase 1 yard (span\n5–6 m, 0.84 m drop)", fontsize=7, color=HAZARD, ha="right", va="top")
# the wire's old window hook is replaced by an anchor post on the tower
# dimensions
dim(ax, (-250, 0), (-250, H_ROCKET + H_MOUNT), "rocket 870\n(43.5 m)", off=(-38, 0))
dim(ax, (-170, 0), (-170, H_MOUNT), "80", off=(-18, 0))
dim(ax, (-D_CORE / 2, 1035), (D_CORE / 2, 1035), "core 80", off=(0, 18))
dim(ax, (-D_CORE / 2 - D_BOOST, 1005), (-D_CORE / 2, 1005), "booster 64", off=(-30, 14))
dim(ax, (-W_MOUNT / 2, -36), (W_MOUNT / 2, -36), "launch mount 240", off=(-60, 14))
dim(ax, (0, -36), (X_TOWER, -36), "300 (15 m)", off=(90, 16))
dim(ax, (tx0, 1000), (tx0 + W_TOWER, 1000), "tower 160", off=(0, 16))
dim(ax, (X_TOWER + 120, 0), (X_TOWER + 120, H_TOWER), "tower 960 (48 m)", off=(0, -60))
dim(ax, (X_TOWER + 200, 0), (X_TOWER + 200, Z_ACCESS), "crew access 840\n(42 m)", off=(0, -120))
dim(ax, (-D_CORE / 2 - D_BOOST - 40, H_MOUNT), (-D_CORE / 2 - D_BOOST - 40, H_MOUNT + L_BOOST), "500", off=(-14, 0))
dim(ax, (-BASE_W / 2 + 60, -52), (BASE_W / 2 + 60, -52), "base plate 560 × 320, two tiles (not to scale; the real deck is far larger)", off=(0, -16))
label(ax, (0, Z_CREW + H_CM + H_CES * .6), "escape tower, Ø12 × 150", (60, 1060))
label(ax, (0, Z_CREW + H_CM / 2), "crew module, cone 80 → 18", (-300, Z_CREW + 110))
label(ax, (D_CORE / 2 + 30, Z_ACCESS), "crew access arm 180 and white room", (-300, Z_ACCESS + 60))
label(ax, (0, H_MOUNT + 18 * S), "orange band: the hypergolic core", (-300, H_MOUNT + 18 * S + 120))
label(ax, (D_CORE / 2, H_MOUNT + 2 * 165), "dashed: segment joints, stacked by hand on printed pins", (-300, H_MOUNT + 2 * 165 - 160))
label(ax, (tx0 + W_TOWER / 2, 480), "lattice tower, 4 × 240 segments, PETG", (X_TOWER + 60, 600))
ax.text(-330, 1060, "SIDE ELEVATION", fontsize=8.5, color=INK, weight="bold", va="bottom")

# ═══ plan ═══
bx = fig.add_axes([0.63, 0.30, 0.35, 0.56])
bx.set_aspect("equal"); bx.axis("off")
bx.set_xlim(-250, 480); bx.set_ylim(-230, 230)
bx.add_patch(Rectangle((-BASE_W / 2 + 60, -BASE_D / 2), BASE_W, BASE_D, fc=RULE, ec=GRAPHITE, lw=0.7))
bx.plot([60, 60], [-BASE_D / 2, BASE_D / 2], color=GRAPHITE, lw=0.6, ls="--")   # the tile joint
bx.add_patch(Rectangle((-W_MOUNT / 2, -W_MOUNT / 2), W_MOUNT, W_MOUNT, fc=SAND, ec=INK, lw=0.8))
bx.add_patch(Rectangle((-D_CORE / 2 - 14, -D_CORE / 2 - 14), D_CORE + 28, D_CORE + 28, fc="white", ec=INK, lw=0.6))
for sx in (-1, 1):
    bx.add_patch(Circle((sx * (D_CORE / 2 + D_BOOST / 2), 0), D_BOOST / 2, fc=WHITE, ec=INK, lw=0.8))
bx.add_patch(Circle((0, 0), D_CORE / 2, fc=WHITE, ec=INK, lw=0.9))
bx.add_patch(Rectangle((tx0, -W_TOWER / 2), W_TOWER, W_TOWER, fc="none", ec=STEEL, lw=1.1))
bx.plot([tx0, tx0 + W_TOWER], [-W_TOWER / 2, W_TOWER / 2], color=STEEL, lw=0.4); bx.plot([tx0, tx0 + W_TOWER], [W_TOWER / 2, -W_TOWER / 2], color=STEEL, lw=0.4)
bx.add_patch(Rectangle((D_CORE / 2, -4), tx0 - D_CORE / 2, 8, fc=STEEL, ec=STEEL))
bx.add_patch(Circle((tx0 + W_TOWER + 4, 0), 5, fc=HAZARD, ec=HAZARD))
bx.plot([tx0 + W_TOWER + 4, 470], [0, -150], color=HAZARD, lw=1.2)
bx.text(400, -175, "wire to the yard", fontsize=7, color=HAZARD, ha="center")
dim(bx, (-W_MOUNT / 2, -W_MOUNT / 2 - 24), (W_MOUNT / 2, -W_MOUNT / 2 - 24), "240", off=(0, -14))
dim(bx, (-W_MOUNT / 2 - 24, -W_MOUNT / 2), (-W_MOUNT / 2 - 24, W_MOUNT / 2), "240", off=(-16, 0))
dim(bx, (0, 120), (X_TOWER, 120), "300", off=(0, 14))
dim(bx, (tx0, -W_TOWER / 2 - 24), (tx0 + W_TOWER, -W_TOWER / 2 - 24), "160", off=(0, -14))
dim(bx, (-BASE_W / 2 + 60, 190), (BASE_W / 2 + 60, 190), "560", off=(0, 14))
dim(bx, (-BASE_W / 2 + 40, -BASE_D / 2), (-BASE_W / 2 + 40, BASE_D / 2), "320", off=(-16, 0))
bx.text(-250, -230, "PLAN", fontsize=8.5, color=INK, weight="bold", va="bottom")

# ═══ the segment key ═══
cx = fig.add_axes([0.63, 0.04, 0.35, 0.23]); cx.axis("off")
rows = [("Rocket core + upper stage", "4 segments of 165, Ø80, PLA white, 2 walls"),
        ("Crew module + escape tower", "1 piece, 230 tall, PLA white"),
        ("Boosters", "2 × (2 segments of 250 + nose 48), Ø64, PLA white"),
        ("Umbilical tower", "4 lattice segments of 240, 160 × 160, PETG grey"),
        ("Launch mount", "240 × 240 × 80 with flame duct, PLA grey"),
        ("Base plate", "2 tiles 280 × 320 × 12, PLA grey, dovetailed"),
        ("Crew access arm + white room", "180 long at 840, PETG grey, swings"),
        ("Wire anchor post", "on the tower at 840, PETG; replaces the window hook")]
cx.text(0, 1.0, "Printed in segments (mm)", fontsize=8.5, color=INK, weight="bold", va="top")
for i, (a, b) in enumerate(rows):
    cx.text(0, 0.86 - i * 0.115, a, fontsize=7.5, color=INK, va="top")
    cx.text(0.5, 0.86 - i * 0.115, b, fontsize=7.5, color=GRAPHITE, va="top")
cx.set_xlim(0, 1); cx.set_ylim(0, 1)

fig.savefig(OUT / "sketch_8_launchpad.png", dpi=160, facecolor="white")
print("wrote", OUT / "sketch_8_launchpad.png")
