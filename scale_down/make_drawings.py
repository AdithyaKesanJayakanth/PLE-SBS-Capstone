"""Sketches for the print-only scale model: room layout, yard plan, pod assembly,
the switch-yard mechanism, bay sections and the wire terminations.

Run:  .venv/bin/python scale_down/make_drawings.py   -> scale_down/sketch_*.png
Dimensions are read from make_parts.py so the sketches match the STL files.
"""
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

import make_parts as P

OUT = Path(__file__).resolve().parent
INK, GRAPHITE, STEEL, HAZARD, SAFE, RULE, SAND = "#18283a", "#56636f", "#2c6390", "#e4570e", "#237a3b", "#c8d0d8", "#8a7a5a"
plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "font.size": 8})


def dim(ax, p0, p1, text, off=(0, 0), color=GRAPHITE, fs=7.5):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<->", mutation_scale=8, lw=0.7, color=color))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], text, color=color, ha="center", va="center", fontsize=fs,
            bbox=dict(fc="white", ec="none", pad=0.5))


def label(ax, xy, text, xytext, color=INK, fs=7.5):
    ax.annotate(text, xy, xytext, fontsize=fs, color=color, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))


def rail_section(ax, x, z0=0.0, color=STEEL):
    """Rail cross-section at x (across the page): base strip, blade and round head."""
    ax.add_patch(Rectangle((x - P.STRIP_W / 2, z0 - P.STRIP_T), P.STRIP_W, P.STRIP_T, fc=RULE, ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((x - P.WEB_T / 2, z0), P.WEB_T, P.WEB_H, fc=color, ec=color, lw=0.6))
    ax.add_patch(Circle((x, z0 + P.HEAD_Z), P.HEAD_D / 2, fc=color, ec=color))


# ---- 1. room layout -----------------------------------------------------------------
def room_layout():
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.set_aspect("equal")
    ax.axis("off")
    L, H = 5.0, 1.0           # metres: horizontal span and drop (whatever the room allows)
    ax.plot([-0.8, 7.0], [0, 0], color=GRAPHITE, lw=1)
    # window with grill bars
    ax.add_patch(Rectangle((-0.45, 0.3), 0.08, 1.5, fc="white", ec=GRAPHITE, lw=0.8))
    for z in np.arange(0.45, 1.8, 0.15):
        ax.plot([-0.45, -0.37], [z, z], color=GRAPHITE, lw=0.8)
    ax.text(-0.5, 1.9, "window grill or handle\n(printed hook + 3 turns + wedge)", ha="center", fontsize=7)
    # wire with sag
    x = np.linspace(0, L, 200)
    sag = 0.12
    y = (H + 0.06) - H * x / L - 4 * sag * (x / L) * (1 - x / L)
    ax.plot(x, y, color=STEEL, lw=1.6)
    ax.text(1.6, 0.86, "1.5 mm stainless wire rope (the only purchase)", color=STEEL, fontsize=7.5)
    # pods
    for xi in (0.25, 0.55):
        yi = (H + 0.06) - H * xi / L - 4 * sag * (xi / L) * (1 - xi / L)
        ax.add_patch(Rectangle((xi - 0.03, yi - 0.07), 0.06, 0.05, fc=STEEL, ec=STEEL))
    ax.text(0.4, 1.22, "start gates\n(3 pods queued)", ha="center", fontsize=7)
    # yard on the floor
    ax.add_patch(Rectangle((L - 0.2, 0), 0.22, 0.06, fc=RULE, ec=GRAPHITE, lw=0.8))
    ax.add_patch(Rectangle((L + 0.02, 0), 0.25, 0.06, fc="#dde6ee", ec=GRAPHITE, lw=0.8))
    ax.add_patch(Rectangle((L + 0.27, 0), 0.69, 0.06, fc="#e8eef3", ec=GRAPHITE, lw=0.8))
    ax.annotate("handover 0.22 m", (L - 0.1, 0.0), (L - 0.9, -0.2), fontsize=7, ha="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))
    ax.annotate("turnout 0.25 m", (L + 0.14, 0.0), (L + 0.05, -0.32), fontsize=7, ha="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))
    ax.annotate("three bays, 0.69 m each\n(lead · brake comb · chain bed · bumper)", (L + 0.6, 0.0), (L + 1.1, -0.26), fontsize=7, ha="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))
    # anchor
    ax.add_patch(Rectangle((6.3, 0), 0.3, 0.5, fc=RULE, ec=GRAPHITE, lw=0.8))
    ax.text(6.45, 0.58, "heavy furniture leg:\nthe wire from the handover\ncleat ties off here", ha="center", va="bottom", fontsize=7)
    ax.plot([L - 0.1, 6.3], [0.06, 0.2], color=STEEL, lw=1.0, ls="--")
    dim(ax, (0, 1.3), (L, 1.3), "span 4 to 6 m (whatever the room allows)", off=(0, 0.05))
    dim(ax, (L - 0.6, 0.06), (L - 0.6, H + 0.06), "drop ≈ 1 m\n(1:50 of a 50 m tower)", off=(-0.55, 0))
    ax.set_xlim(-0.9, 7.1); ax.set_ylim(-0.5, 2.1)
    fig.suptitle("PLE-SBS print-only model: room layout (side view). Window end tied with the printed hook; the yard sits on the floor.", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_1_room_layout.png", dpi=180)


# ---- 2. yard plan -------------------------------------------------------------------
def yard_plan():
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.set_aspect("equal")
    ax.axis("off")
    # handover
    ax.add_patch(Rectangle((-222, -P.STRIP_W / 2), 222, P.STRIP_W, fc="#f1f4f7", ec=GRAPHITE, lw=0.7))
    ax.plot([-222, 0], [0, 0], color=STEEL, lw=2)
    ax.text(-111, -32, "handover module (wire-to-rail ramp, wedge cleat)", ha="center", fontsize=7)
    # turnout plate
    L, y0, y1 = P.PLATE
    ax.add_patch(Rectangle((0, y0), L, y1 - y0, fc="#f1f4f7", ec=GRAPHITE, lw=0.7))
    ax.plot([0, P.TONGUE_X0 - 6], [0, 0], color=STEEL, lw=2)
    xe = P.TONGUE_X0 + P.TONGUE_L + 2
    for k in (-1, 0, 1):
        a = math.radians(k * P.LANE_ANG)
        x1, yy1 = xe + (L - xe) * math.cos(a), k * P.TIP_OFF + (L - xe) * math.sin(a)
        ax.plot([xe, x1], [k * P.TIP_OFF, yy1], color=STEEL, lw=2)
        # bays: lead 230, brake 190, chain 190, bumper 60
        xs = x1 + 12
        ys = yy1 + 12 * math.sin(a)
        for seg, col, name in [(230, RULE, "lead 230"), (190, "#cfe0d6", "brake comb 190"), (190, "#efe6d6", "chain bed 190"), (60, "#fbe3d6", "bumper")]:
            dx, dy = seg * math.cos(a), seg * math.sin(a)
            w = P.LEAD_W if name.startswith("lead") else P.STRIP_W
            nx, ny = -math.sin(a) * w / 2, math.cos(a) * w / 2
            ax.add_patch(Polygon([(xs + nx, ys + ny), (xs + dx + nx, ys + dy + ny), (xs + dx - nx, ys + dy - ny), (xs - nx, ys - ny)], fc=col, ec=GRAPHITE, lw=0.5))
            ax.plot([xs, xs + dx], [ys, ys + dy], color=STEEL, lw=1.6)
            if k == 1:
                ax.text(xs + dx / 2, ys + dy / 2 + 30, name, ha="center", fontsize=7, rotation=P.LANE_ANG)
            xs, ys = xs + dx + 12, ys + dy + 12 * math.sin(a)
        ax.text(xs + 10, ys, f"bay {2 - k}", va="center", fontsize=8, fontweight="bold")
    # tongue in the bay-1 position
    ax.plot([P.TONGUE_X0, P.TONGUE_X0 + P.TONGUE_L], [0, P.TIP_OFF], color=HAZARD, lw=2)
    ax.plot(P.TONGUE_X0, 0, "o", color=INK, ms=4)
    ax.text(P.TONGUE_X0 + 30, -14, "tongue (pivots on the post)", color=HAZARD, fontsize=7)
    # cam and star
    cam = np.array(P.cam_profile())
    ax.add_patch(Polygon(cam + [P.CAM_X, P.CAM_Y], fc="#ffe9d6", ec=HAZARD, lw=0.8))
    ax.plot(P.CAM_X, P.CAM_Y, "o", color=INK, ms=3)
    ax.text(P.CAM_X, P.CAM_Y + 60, "4-dwell cam under the star\n(bay 1 · 2 · 3 · 2)", ha="center", fontsize=7)
    for k in range(4):
        a = math.radians(90 * k)
        R = P.STRIKE_X - P.CAM_X
        ex, ey = P.CAM_X + R * math.cos(a), P.CAM_Y + R * math.sin(a)
        ax.plot([P.CAM_X, ex], [P.CAM_Y, ey], color=INK, lw=1.5, alpha=0.9 if k == 0 else 0.3)
        bx0, bx1 = -21 - P.CAM_Y - 9, 4
        bx = np.array([[0, bx0], [0, bx1]])
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        pts = (rot @ (np.array([[R, bx0], [R, bx1]]).T)).T + [P.CAM_X, P.CAM_Y]
        ax.plot(pts[:, 0], pts[:, 1], color=INK, lw=3, alpha=0.9 if k == 0 else 0.3)
    ax.text(P.STRIKE_X + 6, -92, "cross-bar waits across all three lanes at x = 240;\nthe trolley's top pushes it and the star turns 90°", fontsize=7)
    # springs
    ax.plot([54, 124], [-20, -20], color=SAFE, lw=1.5)
    ax.text(30, -40, "leaf spring pushes the tongue onto the cam", color=SAFE, fontsize=7)
    ax.plot(140, 76, "s", color=GRAPHITE, ms=4)
    ax.text(146, 82, "detent post", fontsize=7)
    dim(ax, (0, -60), (L, -60), f"turnout plate {L:.0f} mm (+ dovetail tabs)", off=(0, -8))
    dim(ax, (P.TONGUE_X0, 22), (P.TONGUE_X0 + P.TONGUE_L, 22), f"tongue {P.TONGUE_L:.0f} mm, tip ±{P.TIP_OFF:.1f} mm, lanes ±{P.LANE_ANG:.1f}°", off=(0, 8))
    ax.set_xlim(-230, 980); ax.set_ylim(-130, 150)
    fig.suptitle("Yard plan (from above): handover, turnout with the self-indexing points, three fanned bays. Dovetails join every segment.", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_2_yard_plan.png", dpi=180)


# ---- 3. pod assembly ------------------------------------------------------------------
def pod_assembly():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax in (a, b):
        ax.set_aspect("equal"); ax.axis("off")
    # (a) end view across the wire / rail, pod coordinates (z up, wire centre at W_Z)
    ax = a
    rail_section(ax, 0, z0=P.W_Z - P.HEAD_Z)
    ax.add_patch(Circle((0, P.W_Z), P.WIRE_D / 2, fc=INK, ec=INK))
    # wheel (section) and plates
    ax.add_patch(Rectangle((-P.WHEEL_W / 2, P.AXLE_Z - P.WHEEL_OD / 2), P.WHEEL_W, P.WHEEL_OD, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Polygon([(-0.6, P.W_Z + 1), (0.6, P.W_Z + 1), (3, P.AXLE_Z - 9 + 3), (-3, P.AXLE_Z - 9 + 3)], fc="white", ec=GRAPHITE, lw=0.5))
    for sgn in (-1, 1):
        ax.add_patch(Rectangle((sgn * 4.5 if sgn > 0 else -8, 0), 3.5, 39.75, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))
        lip = (9 - P.SLOT_W) / 2
        ax.add_patch(Rectangle((sgn * 1.6 if sgn > 0 else -4.5, 0), lip, P.HOOK_TOP, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))
        # pannier
        y0 = 9.0
        ax.add_patch(Rectangle((sgn * y0 if sgn > 0 else -(y0 + P.PAN[1]), P.PAN_BOT), P.PAN[1], P.PAN[2], fc="#f1f4f7", ec=GRAPHITE, lw=0.6))
        ax.add_patch(Rectangle((sgn * 8 if sgn > 0 else -12, -14), 4, 14, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))   # arm over the dovetail
    ax.add_patch(Rectangle((-4.5, 35.75), 9, 4, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))  # bridge
    label(ax, (0, P.W_Z), "wire (1.5 mm) or rail head (3.5 mm)", (24, 12))
    label(ax, (2.5, 4), f"hook lips, {P.SLOT_W} mm slot: the rail blade passes, the wire cannot escape", (24, 2))
    label(ax, (0, 37.75), "bridge: the striker for the star", (24, 40))
    label(ax, (22, -20), "pannier: coins as ballast (0.1 to 0.5 kg per pod)", (40, -22))
    label(ax, (-26, -35), "chain hook (left pannier)", (-85, -45))
    dim(ax, (-8, 44), (8, 44), "16", off=(0, 3))
    dim(ax, (-35, -38), (35, -38), "70 across the panniers", off=(0, -5))
    dim(ax, (42, P.W_Z - P.HEAD_Z), (42, P.PAN_BOT), "12 above the strip", off=(18, 0))
    ax.set_xlim(-95, 95); ax.set_ylim(-55, 55)
    ax.set_title("(a) Pod, end view: trolley plates, wheel, hooks, panniers", fontsize=9)
    # (b) side view
    ax = b
    ax.plot([-60, 60], [P.W_Z, P.W_Z], color=INK, lw=1.5)
    ax.add_patch(Rectangle((-P.BODY_L / 2, 0), P.BODY_L, 39.75, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))
    for x in (-P.AXLE_PITCH / 2, P.AXLE_PITCH / 2):
        ax.add_patch(Circle((x, P.AXLE_Z), P.WHEEL_OD / 2, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
        ax.add_patch(Circle((x, P.AXLE_Z), 2, fc=INK, ec=INK))
        ax.add_patch(Rectangle((x - 3.5, 0), 7, P.HOOK_TOP, fc="#9fb3c8", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((-P.PAN[0] / 2, P.PAN_BOT), P.PAN[0], P.PAN[2], fc="#f1f4f7", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((-9, -14), 18, 14, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((P.PAN[0] / 2 - 3, P.PAN_BOT - 7), 3, 9, fc=INK, ec=INK))
    label(ax, (P.PAN[0] / 2 - 1.5, P.PAN_BOT - 6), "hook catches the chain's stirrup", (40, -48))
    label(ax, (-20, P.AXLE_Z), "wheel Ø24, V-groove, on a printed 4 mm pin", (-95, 50))
    label(ax, (0, -7), "dovetail arm: pannier slides up onto the plate", (10, -20))
    dim(ax, (-P.AXLE_PITCH / 2, 46), (P.AXLE_PITCH / 2, 46), "40 axle pitch", off=(0, 3))
    dim(ax, (-P.BODY_L / 2, -50), (P.BODY_L / 2, -50), "64", off=(0, -4))
    ax.set_xlim(-100, 100); ax.set_ylim(-58, 58)
    ax.set_title("(b) Pod, side view", fontsize=9)
    fig.suptitle("Pod: two identical plates + 2 wheels + 2 pins + 2 panniers. Thread the trolleys on from the free end of the wire before cleating it.", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_3_pod.png", dpi=180)


# ---- 4. mechanism side section ----------------------------------------------------
def mechanism():
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_aspect("equal"); ax.axis("off")
    # plate and rails (side view along the lanes), heights above the strip
    ax.add_patch(Rectangle((0, -4), 236, 4, fc=RULE, ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((0, 0), 34, P.WEB_H, fc=STEEL, ec=STEEL))
    ax.add_patch(Rectangle((P.TONGUE_X0 + 4, 0), P.TONGUE_L - 4, P.WEB_H, fc=HAZARD, ec=HAZARD, alpha=0.8))
    ax.add_patch(Rectangle((172, 0), 64, P.WEB_H, fc=STEEL, ec=STEEL))
    ax.plot([0, 236], [P.HEAD_Z, P.HEAD_Z], color=INK, lw=2)
    # pod on the exit, striking the bar
    px = 240 - P.BODY_L / 2 - 2
    ax.add_patch(Rectangle((px - P.BODY_L / 2, P.HEAD_Z - 10), P.BODY_L, 39.75, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((px - 30, 12), 60, 30, fc="#f1f4f7", ec=GRAPHITE, lw=0.6))
    # cam, shaft, ring, hub, arm with bar
    ax.add_patch(Rectangle((P.CAM_X - 14 / 2, 0), 14, 4, fc=GRAPHITE, ec=GRAPHITE))
    ax.add_patch(Rectangle((P.CAM_X - 28, 4), 56, 6, fc="#ffe9d6", ec=HAZARD, lw=0.8))
    ax.add_patch(Rectangle((P.CAM_X - 4, 10), 8, 50, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((P.CAM_X - 12, 54), 24, 6, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((P.CAM_X - 15, 60), 30, 14, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((P.CAM_X, 62.7), P.STRIKE_X - P.CAM_X + 4, 8, fc=INK, ec=INK))
    ax.add_patch(Rectangle((P.STRIKE_X - 4, 62.7), 8, 15, fc=INK, ec=INK))
    ax.add_patch(Rectangle((136, 0), 8, 60, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
    label(ax, (P.CAM_X, 7), "cam: z 4–10, panniers pass 2 mm above", (20, 20))
    label(ax, (P.CAM_X + 12, 57), "detent ring, 4 notches, printed finger on the post", (150, 100))
    label(ax, (180, 66), "arm (z 63–71) clears the pod's top (z 77) everywhere but the cross-bar", (100, 118))
    label(ax, (P.STRIKE_X, 70), "cross-bar z 63–78: struck by the trolley bridge", (250, 90))
    label(ax, (P.TONGUE_X0 + 60, 20), "tongue, pivot at x = 40", (60, -20))
    label(ax, (P.CAM_X - 20, 5), "follower boss on the tongue rides the cam rim (plan view in sketch 2)", (-10, -24))
    dim(ax, (P.STRIKE_X, -8), (P.STRIKE_X - P.BODY_L - 8, -8), "pod rear is 68 mm past the tongue tip when it strikes", off=(0, -8))
    ax.set_xlim(-30, 330); ax.set_ylim(-40, 130)
    ax.set_title("Self-indexing points, side view: the pod leaves the tongue, strikes the star, the cam sets the tongue for the next pod", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_4_mechanism.png", dpi=180)


# ---- 5. bay sections ----------------------------------------------------------------
def bay_sections():
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax in axs:
        ax.set_aspect("equal"); ax.axis("off")
    # (a) brake comb, side view
    ax = axs[0]
    ax.add_patch(Rectangle((0, -4), 80, 4, fc=RULE, ec=GRAPHITE, lw=0.6))
    ax.plot([0, 80], [P.HEAD_Z, P.HEAD_Z], color=INK, lw=2)
    for i in range(4):
        x0 = 10 + i * 15
        ax.add_patch(Polygon([(x0, 0), (x0 + 30 * math.cos(math.radians(25)), 30 * math.sin(math.radians(25))),
                              (x0 + 30 * math.cos(math.radians(25)) - 0.5, 30 * math.sin(math.radians(25)) + 1.2), (x0 - 0.5, 1.2)], fc=SAFE, ec=SAFE))
    ax.add_patch(Rectangle((30, 12), 60, 30, fc="#f1f4f7", ec=GRAPHITE, lw=0.6, alpha=0.9))
    ax.annotate("", (90, 27), (110, 27), arrowprops=dict(arrowstyle="<-", color=INK))
    label(ax, (24, 6), "12 teeth, 1.2 mm thick, 25°: the pannier floor presses them flat", (2, -14))
    ax.text(40, 48, "pannier floor at 12 mm; teeth reach 14 mm", fontsize=7)
    ax.set_xlim(-5, 125); ax.set_ylim(-20, 60)
    ax.set_title("(a) Brake comb (friction, no magnets)", fontsize=9)
    # (b) chain bed, end view
    ax = axs[1]
    rail_section(ax, 0)
    ax.add_patch(Rectangle((-22, -2), 16, 2, fc="white", ec=GRAPHITE, lw=0.6))
    for k in range(3):
        ax.add_patch(Rectangle((-20 + k * 0.1, -2), 10, 3, fc=SAND, ec=SAND))
    ax.add_patch(Rectangle((-21, -2), 14, 13, fc="none", ec=INK, lw=1.2))
    for sgn in (-1, 1):
        ax.add_patch(Rectangle((sgn * 9 if sgn > 0 else -35, 12), 26, 30, fc="#f1f4f7", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((-16, 5), 8, 7, fc=INK, ec=INK))
    label(ax, (-14, -1), "chain in a 2 mm trough (11 links, 20 × 10 mm)", (-120, -16))
    label(ax, (-14, 9), "stirrup ring; the pod's hook enters it and drags the chain", (-130, 54))
    ax.set_xlim(-135, 60); ax.set_ylim(-25, 60)
    ax.set_title("(b) Chain bed, end view", fontsize=9)
    # (c) bumper, plan
    ax = axs[2]
    ax.add_patch(Rectangle((0, -20), 60, 40, fc=RULE, ec=GRAPHITE, lw=0.6))
    for i in range(6):
        x = 20 + i * 6
        ax.add_patch(Rectangle((x, -17), 1.2, 34, fc=HAZARD, ec=HAZARD))
        yj = 15.8 if i % 2 == 0 else -17
        if i < 5:
            ax.add_patch(Rectangle((x, yj), 7.2, 1.2, fc=HAZARD, ec=HAZARD))
    ax.add_patch(Rectangle((56, -17), 4, 34, fc=INK, ec=INK))
    ax.plot([-10, 60], [0, 0], color=STEEL, lw=2)
    ax.annotate("", (56, 0), (80, 0), arrowprops=dict(arrowstyle="<-", color=INK))
    label(ax, (38, 17), "zig-zag PETG wall: 6 folds, 1.2 mm; 15 mm of stroke", (-5, 30))
    ax.set_xlim(-15, 95); ax.set_ylim(-28, 40)
    ax.set_title("(c) Bumper (the model's backup net), plan", fontsize=9)
    fig.suptitle("Bay pieces. The comb does the stopping; the chain bed shows the mechanism (its mass is small at this scale).", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_5_bays.png", dpi=180)


# ---- 6. wire terminations -----------------------------------------------------------
def terminations():
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax in (a, b):
        ax.set_aspect("equal"); ax.axis("off")
    # (a) window hook, side profile
    ax = a
    prof = [(0, 0), (56, 0), (56, 74), (6, 74), (6, 48), (16, 48), (16, 64), (46, 64), (46, 24), (0, 24)]
    ax.add_patch(Polygon(prof, fc="#dde6ee", ec=GRAPHITE, lw=0.8))
    ax.add_patch(Circle((31, 56), 10, fc="none", ec=GRAPHITE, lw=1, ls="--"))
    ax.text(31, 56, "grill bar\n≤ 24 mm", ha="center", va="center", fontsize=6.5)
    ax.add_patch(Rectangle((10, 24), 12, 20, fc="#c9d6e3", ec=GRAPHITE, lw=0.6))
    ax.text(16, 46, "capstan post Ø12:\n3 turns of wire", ha="center", fontsize=6.5)
    ax.add_patch(Polygon([(20, 2), (54, 2), (54, 8), (20, 4.2)], fc="white", ec=HAZARD, lw=0.8))
    ax.text(37, 13, "wedge pocket: tail of the wire pinched by the PETG wedge", ha="center", fontsize=6.5, color=HAZARD)
    ax.set_xlim(-10, 70); ax.set_ylim(-8, 82)
    ax.set_title("(a) Window hook (side)", fontsize=9)
    # (b) handover, side
    ax = b
    ax.add_patch(Rectangle((-40, -4), 40, 10, fc=RULE, ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((0, -4), 170, 4, fc=RULE, ec=GRAPHITE, lw=0.6))
    xs = np.linspace(0, 110, 20)
    ax.plot(xs, P.HEAD_Z + 14 * (1 - xs / 110), color=STEEL, lw=2.5)
    ax.plot([110, 170], [P.HEAD_Z, P.HEAD_Z], color=STEEL, lw=2.5)
    ax.plot([-60, 44], [P.HEAD_Z + 14 + 14, P.HEAD_Z + 14 * (1 - 44 / 110) + 1.6], color=INK, lw=1.2)
    ax.plot([44, 60], [P.HEAD_Z + 14 * (1 - 44 / 110) + 1.6, 6], color=INK, lw=1.2, ls="--")
    ax.add_patch(Rectangle((30, 0), 50, 22, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
    ax.add_patch(Rectangle((150, 0), 30, 10, fc="#dde6ee", ec=GRAPHITE, lw=0.6))
    label(ax, (20, P.HEAD_Z + 12), "wire lies in a groove on top of the head for 45 mm, then dives", (-50, 85))
    label(ax, (55, 11), "wedge cleat", (90, 30))
    label(ax, (165, 5), "tie-down loop: second wire or belt to a heavy furniture leg", (60, -18))
    label(ax, (-20, 2), "nose block", (-45, -14))
    dim(ax, (0, 70), (110, 70), "ramp 110 mm, 14 mm fall (≈ 7°)", off=(0, 5))
    ax.set_xlim(-70, 200); ax.set_ylim(-28, 100)
    ax.set_title("(b) Handover module (side)", fontsize=9)
    fig.suptitle("Wire terminations: no clips or thimbles. Wrap three turns round the post, pinch the tail with the wedge, tie the end off as well.", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_6_terminations.png", dpi=180)


# ---- 7. wheel section -----------------------------------------------------------------
def wheel_section():
    fig, ax = plt.subplots(figsize=(7, 5.2))
    ax.set_aspect("equal"); ax.axis("off")
    r_out, w, gr, flat, bore = P.WHEEL_OD / 2, P.WHEEL_W, P.GROOVE_R, 1.2, P.AXLE_D / 2 + 0.25
    half = [(bore, 0), (r_out, 0), (r_out, 1.0), (gr, w / 2 - flat / 2), (gr, w / 2 + flat / 2), (r_out, w - 1.0), (r_out, w), (bore, w)]
    pts = half + [(-x, y) for x, y in half[::-1]]
    ax.add_patch(Polygon(pts, fc="#dde6ee", ec=GRAPHITE, lw=0.8))
    ax.plot([0, 0], [-2, w + 2], color=GRAPHITE, lw=0.5, ls="-.")
    ax.add_patch(Circle((gr + P.WIRE_D / 2, w / 2), P.WIRE_D / 2, fc=INK, ec=INK))
    ax.add_patch(Circle((-(gr + 1.45), w / 2), P.HEAD_D / 2, fc=STEEL, ec=STEEL))
    label(ax, (gr + 0.75, w / 2), "1.5 mm wire sits on the 1.2 mm flat", (14, w / 2 + 6))
    label(ax, (-(gr + 1.45), w / 2), "3.5 mm rail head sits 1.45 mm higher in the V", (-24, w / 2 + 9), fs=7.5)
    dim(ax, (-r_out, -3), (r_out, -3), f"Ø{P.WHEEL_OD:.0f} outside", off=(0, -1.2))
    dim(ax, (-gr, -1.2), (gr, -1.2), f"Ø{2 * gr:.0f} at the groove floor", off=(0, 1.2))
    dim(ax, (-bore, w + 1.5), (bore, w + 1.5), f"Ø{2 * bore:.1f} bore (4 mm pin)", off=(0, 1.3))
    dim(ax, (r_out + 2, 0), (r_out + 2, w), f"{w:.0f} wide", off=(2.2, 0))
    dim(ax, (-r_out - 8, 1.0), (-r_out - 8, w - 1.0), f"V mouth {w - 2:.0f} wide", off=(-3.4, 0))
    ax.annotate(f"{flat} mm flat at the floor", (gr, w / 2 + flat / 2), (gr + 3, -1.5), fontsize=7.5, color=GRAPHITE, arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))
    ax.annotate(f"groove depth {r_out - gr:.0f} mm\nflanks {math.degrees(math.atan2((w - 2 - flat) / 2, r_out - gr)):.0f}° off radial\n(included angle {2 * math.degrees(math.atan2((w - 2 - flat) / 2, r_out - gr)):.0f}°)",
                (gr + 1.5, w - 1.0), (6, w + 4), fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))
    ax.set_xlim(-26, 26); ax.set_ylim(-7, w + 9)
    ax.set_title("Wheel (pulley) section: revolved profile from make_parts.py, file wheel_x6.stl", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_7_wheel.png", dpi=180)


if __name__ == "__main__":
    room_layout(); yard_plan(); pod_assembly(); mechanism(); bay_sections(); terminations(); wheel_section()
    print("wrote scale_down/sketch_1..7")
