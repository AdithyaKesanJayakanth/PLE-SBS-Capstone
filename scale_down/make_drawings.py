"""Sketches for the print-only scale model, phase 1 version 2. Every outline is projected or
sectioned from the same solids as the STL files (make_parts.py), placed exactly as the fit check
(check/assembly_check.py) places them, so the drawings cannot drift from the parts.

Run:  .venv/bin/python scale_down/make_drawings.py   -> scale_down/sketch_1 ... sketch_7 *.png
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, PathPatch, Rectangle
from matplotlib.path import Path as MPath

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "check"))
import make_parts as P  # noqa: E402
import assembly_check as A  # noqa: E402

OUT = HERE
INK, GRAPHITE, STEEL, HAZARD, RULE = "#18283a", "#56636f", "#2c6390", "#e4570e", "#c8d0d8"
GREY, ORANGE, BLUE, WIRE = "#d5dade", "#f0a46c", "#7fa6c8", "#33404d"
plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "font.size": 8})


# ---------------------------------------------------------------------------- drawing helpers
def draw(ax, cs, fc, ec=GRAPHITE, lw=0.5, z=1, alpha=1.0):
    polys = cs.to_polygons()
    if not polys:
        return
    verts, codes = [], []
    for p in polys:
        p = np.asarray(p)
        verts += list(p) + [p[0]]
        codes += [MPath.MOVETO] + [MPath.LINETO] * (len(p) - 1) + [MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(verts, codes), fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha))


def top(m):
    return m.project()


def side(m):
    """Elevation looking along +y: (x, z)."""
    return m.rotate([-90, 0, 0]).project()


def end(m):
    """Elevation looking along +x: (-y, z)."""
    return m.rotate([0, 90, 0]).rotate([0, 0, 90]).project()


def cut_x(m, x):
    """Section at x, seen from the front: (y, z)."""
    return m.rotate([0, -90, 0]).slice(x).rotate(-90)


def cut_y(m, y):
    """Section at y, seen from the side: (x, z)."""
    return m.rotate([-90, 0, 0]).slice(-y)


def dim(ax, p0, p1, text, off=(0, 0), fs=7, color=GRAPHITE):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<->", mutation_scale=7, lw=0.6, color=color, zorder=5))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], text, color=INK, ha="center", va="center", fontsize=fs,
            bbox=dict(fc="white", ec="none", pad=0.4), zorder=6)


def label(ax, xy, text, xytext, fs=7, ha="left"):
    ax.annotate(text, xy, xytext, fontsize=fs, color=INK, ha=ha, va="center", zorder=7,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))


def finish(fig, ax_list, title, name):
    for ax in ax_list:
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle(title, fontsize=9.5, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=180, facecolor="white")
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------------------- 1. room
def room_layout():
    fig, ax = plt.subplots(figsize=(11, 3.8))
    L, H = 6.0, 0.9
    ax.plot([-0.8, 7.6], [0, 0], color=GRAPHITE, lw=1)
    ax.add_patch(Rectangle((-0.45, 0.3), 0.08, 1.5, fc="white", ec=GRAPHITE, lw=0.8))
    for z in np.arange(0.45, 1.8, 0.15):
        ax.plot([-0.45, -0.37], [z, z], color=GRAPHITE, lw=0.8)
    ax.text(-0.42, 1.92, "window grill or handle:\nprinted hook, 3 turns, wedge", ha="center", fontsize=7)
    x = np.linspace(0, L, 200)
    sag = 0.11
    y = (H + 0.05) - H * x / L - 4 * sag * (x / L) * (1 - x / L)
    ax.plot(x, y, color=STEEL, lw=1.6)
    ax.text(1.5, 0.95, "1.5 mm stainless wire rope, the only purchase", color=STEEL, fontsize=7.5)
    yi = (H + 0.05) - H * 0.2 / L - 4 * sag * (0.2 / L) * (1 - 0.2 / L)
    ax.add_patch(Rectangle((0.17, yi - 0.08), 0.06, 0.06, fc=STEEL, ec=STEEL))
    ax.text(0.2, 1.25, "start gate: one pod waits,\nthe next is hung on by hand", ha="center", fontsize=7)
    ax.add_patch(Rectangle((L - 0.21, 0), 0.21, 0.055, fc=RULE, ec=GRAPHITE, lw=0.8))
    ax.add_patch(Rectangle((L, 0), 0.25, 0.11, fc="#dde6ee", ec=GRAPHITE, lw=0.8))
    ax.add_patch(Rectangle((L + 0.25, 0), 0.69, 0.055, fc="#e8eef3", ec=GRAPHITE, lw=0.8))
    label(ax, (L - 0.1, 0.03), "handover 0.21 m", (L - 1.0, -0.22))
    label(ax, (L + 0.12, 0.06), "turnout 0.25 m, flap gantry 0.11 m high", (L - 0.5, -0.36))
    label(ax, (L + 0.6, 0.03), "three bays, 0.69 m:\nlead, brake comb, chain bed, bumper", (L + 0.75, -0.3))
    ax.add_patch(Rectangle((7.15, 0), 0.3, 0.45, fc=RULE, ec=GRAPHITE, lw=0.8))
    ax.text(7.3, 0.52, "heavy furniture leg:\nthe wire runs on under\nthe yard and ties here", ha="center", va="bottom", fontsize=7)
    ax.plot([L - 0.15, 7.15], [0.003, 0.003], color=STEEL, lw=1.0, ls="--")
    dim(ax, (0, 1.45), (L, 1.45), "span 6.0 m at 1:50 (4 to 6 m if the room is shorter)", off=(0, 0.06))
    dim(ax, (L - 0.55, 0.05), (L - 0.55, H + 0.05), "drop 0.9 m", off=(-0.32, 0))
    ax.set_xlim(-0.9, 7.7); ax.set_ylim(-0.5, 2.15)
    finish(fig, [ax], "Room layout, side view: the window end is tied with the printed hook; the yard sits on the floor and the wire runs on under it.", "sketch_1_room_layout.png")


# ---------------------------------------------------------------------------- 2. yard plan
def yard_plan():
    fig, ax = plt.subplots(figsize=(13, 5.2))
    draw(ax, top(P.handover_in_yard()), GREY)
    draw(ax, top(A.base_solid()), GREY)
    for k in P.LANES:
        for n, m, _ in A.bays(k):
            draw(ax, top(m), ORANGE if n.startswith("bumper") else GREY)
        s, c = A.sled_chain(k)
        draw(ax, top(c), "#b9c1c8", z=2)
        draw(ax, top(s), "#b9c1c8", z=2)
    draw(ax, top(A.tongue_at(P.THETA)), ORANGE, z=3)
    draw(ax, top(A.rocker_at(P.REST_TILT)), ORANGE, z=4)
    draw(ax, top(A.flap_at(0)), ORANGE, z=4)
    draw(ax, top(P.bias_spring(5.3)), ORANGE, z=4)
    for k, u in (("R", 700.0), ("C", 640.0)):
        x, y, yaw = A.pod_pose(k, u)
        for _, m in A.pod_at(x, y, yaw):
            draw(ax, top(m), BLUE, z=5)
    x0 = -P.HO_L
    xe = P.PLATE_L + 674
    dim(ax, (x0, -95), (0, -95), "handover 170 (+12 tab)")
    dim(ax, (0, -95), (P.PLATE_L, -95), f"turnout plate {P.PLATE_L:.0f} × {P.PLATE_Y1 - P.PLATE_Y0:.0f}")
    dim(ax, (P.PLATE_L, -150), (P.PLATE_L + 230, -150), "lead 230")
    dim(ax, (P.PLATE_L + 230, -150), (P.PLATE_L + 420, -150), "brake comb 190")
    dim(ax, (P.PLATE_L + 420, -150), (P.PLATE_L + 610, -150), "chain bed 190")
    dim(ax, (P.PLATE_L + 610, -150), (P.PLATE_L + 674, -150), "bumper 64")
    label(ax, (P.PIVOT[0], 0), "tongue pivot; the tongue is set to bay L\n(the third pod) after two pods have passed", (-60, 110))
    rx, ry = P.rk_plan(0, 0)
    label(ax, (rx, ry), "escapement rocker on two bridges", (60, 150))
    label(ax, (P.GANTRY_X, 40), "flap gantry: the passing pod lifts the flap,\nthe thread rocks the rocker", (250, 150))
    label(ax, (P.SPRING_ROOT[0] + 30, -10), "leaf spring: pushes the tongue toward the next bay", (-150, -55))
    for k in P.LANES:
        ang = math.radians(P.LANES[k])
        ex = P.PLATE_L + 674
        ey = P.lane_y(k, P.PLATE_L) + 674 * math.sin(ang)
        ax.text(ex + 12, ey, f"bay {k}", fontsize=8, color=INK, va="center")
    ax.text(P.PLATE_L + 120, 175, "Fill order: R, then C, then L. Lanes fan at ±9.65° from the pivot; the tongue tip moves 17 mm per step.",
            fontsize=7.5, color=INK)
    ax.set_xlim(x0 - 20, xe + 60); ax.set_ylim(-175, 200)
    finish(fig, [ax], "Yard plan from above, drawn from the part files: handover, turnout with the escapement, three bays; two wagons parked.", "sketch_2_yard_plan.png")


# ---------------------------------------------------------------------------- 3. wagon
def pod_assembly():
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"width_ratios": [1, 1.5]})
    parts = dict(P.pod_parts())
    rail = P.lead_rail().translate([-115, 0, 0])
    z0 = P.POD_Z
    # a: section through the front axle, on a rail
    for n, m in parts.items():
        draw(a, cut_x(m.translate([0, 0, z0]), P.AX_X), BLUE if not n.startswith("pin") else ORANGE, z=3)
    draw(a, cut_x(rail, P.AX_X), GREY, z=2)
    dim(a, (-24, 0), (-24, z0), f"axle {z0:.1f}\nabove the strip", off=(-9, 0))
    dim(a, (20, 0), (20, 12), "floor 12", off=(8, 0))
    dim(a, (-P.Y_OUT, 85), (P.Y_OUT, 85), f"{2 * P.Y_OUT:.0f} over the plates")
    dim(a, (-P.ARM_Y1 - 2, 95), (P.ARM_Y1 + 2, 95), f"{2 * P.ARM_Y1 + 4:.0f} over the pin heads")
    label(a, (0, P.HEAD_Z), "rail head Ø3.5 sits in the\nwheel's V; the wire Ø1.5 sits\n1.6 lower in the same V", (24, 66))
    label(a, (P.SLOT_W / 2 + 0.6, z0 + P.LIP_TOP - 1), "guide lips: 0.3 each side of\nthe web, 0.45 under the head", (24, 40))
    label(a, (P.ARM_Y1 + 1, z0), "axle pin: head, then pannier arm,\nplate, wheel, plate, arm, snap", (24, 54))
    label(a, (-9, 20), "pannier, same part both sides:\ncoins inside", (-60, 10), ha="left")
    a.set_xlim(-62, 62); a.set_ylim(-8, 100)
    a.set_title("Section through the front axle, on a rail (mm)", fontsize=8.5)
    # b: side view on a rail
    for n, m in parts.items():
        if n in ("plate R", "wheel rear", "wheel front", "pannier R", "pin rear", "pin front"):
            draw(b, side(m.translate([0, 0, z0])), ORANGE if n.startswith("pin") else BLUE, z=3 if not n.startswith("wheel") else 2)
    draw(b, side(rail.translate([0, 0, 0])), GREY, z=1)
    b.plot([-50, 50], [0, 0], color=GRAPHITE, lw=0.5)
    dim(b, (-P.PL_X, z0 + 26), (P.PL_X, z0 + 26), f"{2 * P.PL_X:.0f}")
    dim(b, (-P.AX_X, z0 - 4), (P.AX_X, z0 - 4), f"axles {2 * P.AX_X:.0f} apart")
    dim(b, (P.PL_X + 6, 0), (P.PL_X + 6, z0 + P.PL_ZT), f"{z0 + P.PL_ZT:.1f}", off=(7, 0))
    label(b, (-P.PEG_X, z0 + P.PEG_Z), "spacer peg Ø5: across the gap,\n3 mm into the other plate", (-75, 92))
    label(b, (P.AX_X, z0 + P.LIP_TOP - 3), "lips under each wheel", (40, 30))
    b.set_xlim(-80, 80); b.set_ylim(-8, 100)
    b.set_title("Side view on a rail; the far plate and pannier are the same parts turned round", fontsize=8.5)
    finish(fig, [a, b], "Wagon: two identical plates, two wheels, two identical panniers, two axle pins. Drawn from the part files.", "sketch_3_pod.png")


# ---------------------------------------------------------------------------- 4. mechanism
def mechanism():
    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1])
    a = fig.add_subplot(gs[0, 0]); b = fig.add_subplot(gs[0, 1]); c = fig.add_subplot(gs[1, 0]); d = fig.add_subplot(gs[1, 1])
    base = A.base_solid()
    window = P.box(170, 150, 30, (-10, -40, -1))
    # a: plan around the pivot at rest, tongue on R
    draw(a, top(base ^ window), GREY, z=1)
    draw(a, top(A.tongue_at(-P.THETA)), ORANGE, z=2)
    draw(a, top(P.bias_spring(15.9)), "#e0884a", z=3)
    draw(a, top(A.rocker_at(P.REST_TILT)), "#c9d6e2", z=4, alpha=0.85)
    for (fx, fy), nm in ((P.FA, "A"), (P.FB, "B")):
        px, py, _ = P.rk_point((fx, fy, -P.FING_H), P.REST_TILT)
        a.plot(px, py, "o", ms=4, color=HAZARD, zorder=6)
        a.text(px + 2, py + 3, f"finger {nm}", fontsize=7, color=HAZARD, zorder=7)
    label(a, P.polar(P.TOOTH_R1, P.tooth_alpha(1) - P.THETA, P.PIVOT), "four teeth on the tongue's ring", (120, 20))
    label(a, P.rk_plan(P.BEAM_X1, 0), "bridge over the ring,\nnotch for the 3 mm pin", (120, 70))
    label(a, P.rk_plan(0, P.CUP_Y), "coin cup: about 15 g\nholds finger A down", (110, 95))
    label(a, (P.PIVOT[0] + 30, -14), "spring tab", (60, -32))
    label(a, (P.PIVOT[0], 0), "pivot", (0, -30))
    a.set_xlim(-10, 175); a.set_ylim(-40, 110)
    a.set_title("Plan at rest: tongue set to bay R, finger A down, holding tooth 2", fontsize=8.5)
    # b: section across the rocker (perpendicular to its axis) at rest and triggered
    for k, (tilt, title) in enumerate(((P.REST_TILT, "rest: A in, B out"), (P.TRIG_TILT, "triggered: A out, B in"))):
        dx = k * 70
        rk = P.rocker().rotate([tilt, 0, 0])
        cs = rk.rotate([0, -90, 0]).slice(P.FA[0]).rotate(-90)
        draw(b, cs.translate([dx, P.ROCK_Z]), "#c9d6e2", z=3)
        cs = rk.rotate([0, -90, 0]).slice(P.FB[0]).rotate(-90)
        draw(b, cs.translate([dx, P.ROCK_Z]), "#c9d6e2", z=3, alpha=0.6)
        b.add_patch(Rectangle((dx - P.R_AX + P.TOOTH_R0, P.TOOTH_Z0), P.TOOTH_R1 - P.TOOTH_R0, P.TOOTH_Z1 - P.TOOTH_Z0, fc=ORANGE, ec=GRAPHITE, lw=0.4, alpha=0.5, zorder=1))
        b.add_patch(Rectangle((dx - P.R_AX + P.RING_R0, 0), P.RING_R1 - P.RING_R0, P.RING_T, fc=ORANGE, ec=GRAPHITE, lw=0.4, zorder=1))
        b.plot([dx - 30, dx + 30], [0, 0], color=GRAPHITE, lw=0.6)
        b.text(dx, -6, title, ha="center", fontsize=7.5)
        b.plot(dx, P.ROCK_Z, "+", color=INK)
    b.text(-25, 26, "teeth 2.5 to 8.5 high\nfinger tips 6.3 (in) or 10.0 (out)", fontsize=7)
    b.set_xlim(-40, 120); b.set_ylim(-10, 40)
    b.set_title("Across the rocker: the coin cup side is outward (right)", fontsize=8.5)
    # c: flap and thread
    pod = A.pod_at(P.GANTRY_X - 45, 0, 0)
    for _, m in pod:
        draw(c, side(m), BLUE, z=2, alpha=0.9)
    draw(c, side(base ^ P.box(80, 60, 120, (P.GANTRY_X - 40, 55, -1))), GREY, z=1)
    draw(c, side(A.flap_at(0)), ORANGE, z=3)
    draw(c, side(A.flap_at(40.3)), ORANGE, z=3, alpha=0.45)
    h0, h1 = P.crank_hole(0), P.rocker_hole(P.REST_TILT)
    c.plot([h0[0], h1[0]], [h0[2], h1[2]], color=WIRE, lw=0.8, ls="--")
    label(c, (P.GANTRY_X + 10, 74), "the wagon's top lifts the flap 40°;\nthe crank pulls the thread", (232, 30))
    label(c, ((h0[0] + h1[0]) / 2 + 40, (h0[2] + h1[2]) / 2 + 15), "thread to the rocker's outer arm\n(off to the left, 150 mm away)", (105, 108))
    c.set_xlim(100, 270); c.set_ylim(-5, 120)
    c.set_title("Flap gantry from the side (x along the yard)", fontsize=8.5)
    # d: sequence
    d.axis("off")
    rows = [["state", "rocker", "tongue", "next pod goes to"],
            ["reset by hand", "A in", "-9.6° (held by A on tooth 2)", "bay R"],
            ["pod 1 lifts the flap", "B in, A out", "springs to -4.9° (B holds)", ""],
            ["flap falls back", "A in, B out", "springs to +0.1° (A holds)", "bay C"],
            ["pod 2 lifts the flap", "B in, A out", "springs to +4.8°", ""],
            ["flap falls back", "A in, B out", "springs to +9.7°", "bay L"],
            ["pod 3", "", "stays on L (stop at +10.25°)", "bay L"]]
    t = d.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="left", colWidths=[0.25, 0.16, 0.36, 0.2])
    t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.5)
    d.set_title("One step per pod, simulated with the part geometry (check/assembly_report.md)", fontsize=8.5)
    d.text(0.0, 0.05, "Thread: tie it straight with the flap hanging and the rocker at rest; 0 to 1.5 mm of slack all work.\n"
           "Reset: lift the rocker out of its notches, swing the tongue to bay R, drop the rocker back.", fontsize=7.5, transform=d.transAxes)
    for ax in (a, b, c):
        ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("The self-indexing points: a two-finger escapement on the tongue, worked by a flap the pod lifts. Drawn from the part files.", fontsize=9.5, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "sketch_4_mechanism.png", dpi=180, facecolor="white")
    plt.close(fig)
    print("wrote sketch_4_mechanism.png")


# ---------------------------------------------------------------------------- 5. bays
def bay_sections():
    fig, (a, b) = plt.subplots(2, 1, figsize=(13, 6.2), gridspec_kw={"height_ratios": [1.3, 1]})
    s = 0.0
    for n, fn, L in A.BAY:
        draw(a, side(fn().translate([s, 0, 0])), ORANGE if n == "bumper" else GREY, z=1)
        s += L
    sl = P.sled().translate([420 + 16, -14, -2])
    ch = P.chain().translate([420 + P.CHAIN_X0, -14, -2])
    draw(a, side(ch), "#9aa4ad", z=2)
    draw(a, side(sl), "#9aa4ad", z=2)
    for x, alpha in ((300, 0.9), (420 - 16 - 32 + 2, 0.5)):
        for nm, m in P.pod_parts():
            if nm in ("plate R", "wheel rear", "wheel front", "pannier R"):
                draw(a, side(m.translate([x, 0, P.POD_Z])), BLUE, z=3, alpha=alpha)
    for x0, x1, t in ((0, 230, "lead 230"), (230, 420, "brake comb 190: 12 leaves, tips 13.8 high,\npressed 1.8 mm by the basket floor"),
                      (420, 610, "chain bed 190: the left basket meets\nthe sled and pushes it and the chain"), (610, 674, "bumper")):
        dim(a, (x0, -18), (x1, -18), t, off=(0, -10) if "\n" in t else (0, 0))
    a.set_xlim(-10, 690); a.set_ylim(-42, 90)
    a.set_title("One bay from the side", fontsize=8.5)
    # b: cross-sections of each segment with a wagon
    for i, (n, fn, L) in enumerate(A.BAY):
        dx = i * 95
        draw(b, cut_x(fn(), {"lead": 100, "brake": 40.5, "chainbed": 60, "bumper": 40}[n]).translate([dx, 0]), GREY, z=1)
        for nm, m in P.pod_parts():
            draw(b, cut_x(m.translate([0, 0, P.POD_Z]), 10).translate([dx, 0]), BLUE, z=3, alpha=0.8)
        if n == "chainbed":
            draw(b, cut_x(P.sled().translate([0, -14, -2]), 10).translate([dx, 0]), "#9aa4ad", z=2)
        b.text(dx, -12, {"lead": "lead", "brake": "brake comb", "chainbed": "chain bed + sled", "bumper": "bumper"}[n], ha="center", fontsize=7.5)
    b.set_xlim(-50, 340); b.set_ylim(-18, 90)
    b.set_title("Sections looking down the bay, wagon over each segment", fontsize=8.5)
    finish(fig, [a, b], "Bays: lead, passive brake comb, chain bed with sled, zig-zag bumper. Drawn from the part files.", "sketch_5_bays.png")


# ---------------------------------------------------------------------------- 6. terminations
def terminations():
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(14, 4.8), gridspec_kw={"width_ratios": [1, 1.6, 1]})
    hook = P.window_hook()
    draw(a, side(hook), ORANGE, z=1)
    draw(a, cut_y(hook, 14), "#e0884a", z=2)
    a.plot([P.POCKET_X0, 90], [P.POCKET_Z + 0.75] * 2, color=WIRE, lw=1.2, zorder=4)
    a.plot([-8, -8], [0, 12], color=WIRE, lw=1.2, zorder=4)
    label(a, (-8, 12), "capstan post: three turns", (-55, 40))
    label(a, (50, P.POCKET_Z + 1), "tail along the pocket floor;\nwedge pushed in from the end", (30, -18))
    label(a, (19, 60), "over a grill bar\nor handle ≤ 24", (-40, 70))
    a.set_xlim(-60, 100); a.set_ylim(-28, 80)
    a.set_title("Window hook, side view and section at the pocket", fontsize=8.5)
    ho = P.handover_in_yard()
    draw(b, side(ho), GREY, z=1)
    draw(b, side(A.base_solid() ^ P.box(80, 200, 120, (-1, -100, -10))), GREY, z=1, alpha=0.7)
    w = A.wire_solid() ^ P.box(400, 200, 100, (-300, -100, -10))
    draw(b, side(w), WIRE, ec=WIRE, z=3)
    for x in (-230, -150):
        for nm, m in P.pod_parts():
            if nm in ("plate R", "wheel rear", "wheel front", "pannier R"):
                draw(b, side(m.translate([x, 0, P.POD_Z])), BLUE, z=4, alpha=0.6)
    label(b, (-P.HO_L + 20, P.WIRE_C), "wire in a groove on the head for 45 mm:\nthe wheels are at the same height on both", (-260, 95))
    label(b, (-P.HO_L + P.GROOVE_END + 8, 30), "the wire dives through the blade at 51°", (-90, 85))
    label(b, (-40, -3), "and runs on under the yard to a furniture leg;\nthe handover carries almost none of its pull", (-110, -22))
    b.set_xlim(-275, 75); b.set_ylim(-30, 100)
    b.set_title("Handover, side view", fontsize=8.5)
    g, lv = P.gate_in_pod()
    for nm, m in P.pod_parts():
        if nm in ("plate L", "wheel rear", "pannier L"):
            draw(c, side(m), BLUE, z=1, alpha=0.7)
    draw(c, side(g), GREY, z=2)
    draw(c, side(lv), ORANGE, z=3)
    c.plot([-90, 40], [-P.R_WIRE, -P.R_WIRE], color=WIRE, lw=1.0, zorder=4)
    label(c, (P.GATE_CX, -P.R_WIRE), "clamp on the wire;\ntapered key locks it", (-95, -45))
    label(c, (-21, 13), "hook in front of the rear spacer peg;\nlift the lever 14° to release", (-60, 45))
    c.set_xlim(-100, 40); c.set_ylim(-55, 55)
    c.set_title("Start gate holding a wagon (pod frame)", fontsize=8.5)
    finish(fig, [a, b, c], "Wire ends and the start gate. Drawn from the part files.", "sketch_6_terminations.png")


# ---------------------------------------------------------------------------- 7. wheel
def wheel_section():
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    w = P.wheel().translate([0, 0, -P.WHEEL_W / 2])
    cs = w.rotate([-90, 0, 0]).slice(0.0)                  # section in the plane y = 0: (x, z)
    cs = cs.rotate(90)                                     # axis vertical on the page
    draw(ax, cs, BLUE, z=1)
    ax.add_patch(plt.Circle((0, -P.R_WIRE), P.WIRE_D / 2, color=WIRE, zorder=3))
    ax.add_patch(plt.Circle((0, P.R_HEAD), P.HEAD_D / 2, color="#8b98a5", zorder=3, alpha=0.9))
    ax.plot([-14, 14], [0, 0], color=GRAPHITE, lw=0.5, ls="-.")
    dim(ax, (7, 0), (7, -P.R_WIRE), f"{P.R_WIRE:.2f} to the wire's centre", off=(4.5, 0))
    dim(ax, (7, 0), (7, P.R_HEAD), f"{P.R_HEAD:.2f} to the head's centre", off=(4.5, 0))
    dim(ax, (-9, -P.WHEEL_OD / 2), (-9, P.WHEEL_OD / 2), "Ø24", off=(-1.8, 0))
    label(ax, (0.6, -P.R_WIRE), "wire Ø1.5 (on the wire)", (-13.5, -14.5))
    label(ax, (1.0, P.R_HEAD + 1), "rail head Ø3.5 (on a rail)", (-13.5, 14.5))
    ax.text(0, -17, "Section through the axle; the bore Ø4.4 runs left to right. V flanks at 1 : 0.8 with a 1.2 flat.", ha="center", fontsize=7)
    ax.set_xlim(-16, 22); ax.set_ylim(-18, 16)
    finish(fig, [ax], "Wheel section: the axle sits 9.45 above the wire's centre and 11.05 above the head's, so the handover sets\nthe head's centre 1.6 mm below the wire's and the wagon rolls from one to the other at the same height.", "sketch_7_wheel.png")


if __name__ == "__main__":
    room_layout()
    yard_plan()
    pod_assembly()
    mechanism()
    bay_sections()
    terminations()
    wheel_section()
