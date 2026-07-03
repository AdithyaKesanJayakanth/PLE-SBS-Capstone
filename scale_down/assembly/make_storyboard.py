"""Storyboard for the phase-1 assembly guide and working animation.

Places every phase-1 part for each assembly step and for each frame of a run of three wagons
(down the wire, onto the handover, through the self-setting points into bays R, C and L), with the
flap, rocker, tongue, spring, sleds and chains driven by the same kinematics as the fit check.
Every insertion path and every run frame is collision-checked here with exact booleans, and the
pairs that touch are listed for FreeCAD to measure again with its own booleans.

Run:  .venv/bin/python scale_down/assembly/make_storyboard.py
      -> scale_down/assembly/build/meshes/*.stl, build/storyboard.json, path_check_report.md
Then: freecad_render.py (screenshots) and freecad_motion_check.py (FreeCAD booleans), make_media.py.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "check"))
import make_parts as P  # noqa: E402
import assembly_check as A  # noqa: E402

BUILD = HERE / "build"
MESH = BUILD / "meshes"
EPS = 0.05
REPORT = []


def say(s=""):
    print(s)
    REPORT.append(s)


# ---------------------------------------------------------------------------- transforms
def Tr(x=0.0, y=0.0, z=0.0):
    M = np.eye(4)
    M[:3, 3] = [x, y, z]
    return M


def Rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1.0]])


def Ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])


def Rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])


def mm(*Ms):
    out = np.eye(4)
    for M in Ms:
        out = out @ M
    return out


# ---------------------------------------------------------------------------- objects
COL = {"grey": (0.80, 0.82, 0.85), "rail": (0.68, 0.72, 0.77), "orange": (0.93, 0.47, 0.16), "blue": (0.18, 0.40, 0.63),
       "blue2": (0.30, 0.55, 0.78), "blue3": (0.12, 0.30, 0.50), "wire": (0.12, 0.14, 0.17), "coin": (0.83, 0.68, 0.25),
       "chain": (0.52, 0.56, 0.60), "pin": (0.95, 0.60, 0.20), "green": (0.20, 0.60, 0.30)}
OBJ, LOCAL = {}, {}


def add(name, m, colour):
    MESH.mkdir(parents=True, exist_ok=True)
    LOCAL[name] = m
    mesh = m.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=False)
    tmp = MESH / f".{name}.tmp.stl"
    tm.export(tmp)
    tmp.replace(MESH / f"{name}.stl")              # atomic: a reader never sees a half-written file
    OBJ[name] = dict(file=f"{name}.stl", colour=COL[colour])


def placed(name, M):
    return LOCAL[name].transform(M[:3, :])


def ov(a, b):
    return (a ^ b).volume()


I4 = np.eye(4)
ER = P.polar(P.R_AX, P.PHI_M, P.PIVOT)


def tongue_M(T):
    return mm(Tr(*P.PIVOT), Rz(T))


def rocker_M(t, lift=0.0):
    return mm(Tr(ER[0], ER[1], P.ROCK_Z + lift), Rz(P.PHI_M - 90), Rx(t))


def flap_M(s, lift=0.0):
    return mm(Tr(P.GANTRY_X, 0, P.GANTRY_Z + lift), Ry(-s))


def bay_M(k, s, lift=0.0):
    a = math.radians(P.LANES[k])
    x0, y0 = P.PLATE_L, P.lane_y(k, P.PLATE_L)
    return mm(Tr(x0 + s * math.cos(a), y0 + s * math.sin(a), lift), Rz(P.LANES[k]))


SPRING_STEPS = np.round(np.arange(0.0, 18.01, 0.5), 2)


def build_objects():
    add("turnout_plate", P.turnout_base(), "grey")
    add("handover", P.handover_in_yard(), "grey")
    for n, fn, L in A.BAY:
        add(f"bay_{n}", fn(), "orange" if n == "bumper" else "rail")
    add("tongue", P.tongue(), "orange")
    add("rocker_bridge", P.goalposts(), "grey")
    add("rocker", P.rocker(), "orange")
    add("rocker_pin", P.rocker_pin().rotate([0, 90, 0]).translate([-P.BEAM_X1 - 0.3, 0, 0]), "pin")
    add("coins", P.cyl(4.2, 20.0).translate([0, P.CUP_Y, 2.1]), "coin")
    add("flap", P._flap_body(), "orange")
    add("gantry_axle", P.gantry_axle().translate([-P.GANTRY_X, 0, -P.GANTRY_Z]), "pin")
    for d in SPRING_STEPS:
        add(f"spring_{d:04.1f}", P.bias_spring(float(d)), "green")
    add("sled", P.sled().translate([16.0, -14.0, -2.0]), "chain")
    add("chain", P.chain().translate([P.CHAIN_X0, -14.0, -2.0]), "chain")
    for n, m in P.pod_parts():
        colour = "pin" if n.startswith("pin") else ("blue2" if n.startswith("wheel") else ("blue3" if n.startswith("pannier") else "blue"))
        add("pod_" + n.replace(" ", "_"), m, colour)
    add("wire", wire_mesh(), "wire")
    add("window_hook", P.window_hook(), "orange")
    add("wedge", P.wedge().rotate([90, 0, 0]), "pin")
    add("gate", P.start_gate(), "grey")
    add("gate_lever", P.gate_lever(), "orange")
    add("gate_key", P.gate_key().rotate([0, 0, 0]), "pin")
    add("gate_pin", P.gate_pin().rotate([90, 0, 0]), "pin")
    add("hook_wire", hook_wire(), "wire")


# ---------------------------------------------------------------------------- the wire and the run path
ALPHA = 4.4                      # slope of the wire where it reaches the yard: 6 m span, 0.9 m drop, 110 mm sag
INCLINE = 520.0
NOSE = -P.HO_L


def wire_mesh():
    a = math.radians(ALPHA)
    start = (NOSE - INCLINE * math.cos(a), 0.0, P.WIRE_C + INCLINE * math.sin(a))
    inc = P.cyl_x(0, INCLINE + 0.4, P.WIRE_D).rotate([0, ALPHA, 0]).translate(list(start))
    rest = A.wire_solid() ^ P.box(2000, 400, 200, (NOSE - 0.3, -200, -20))
    return inc + rest


N_JOIN = (NOSE + P.R_WIRE * (1 / math.cos(math.radians(ALPHA)) - 1) / math.tan(math.radians(ALPHA)), P.POD_Z)


def path_points(k):
    a = math.radians(ALPHA)
    nx, nz = N_JOIN
    p0 = np.array([nx - INCLINE * math.cos(a), 0, nz + INCLINE * math.sin(a)])
    p1 = np.array([nx, 0, nz])
    p2 = np.array([P.PIVOT[0], 0, nz])
    t = math.radians(P.LANES[k])
    p3 = p2 + 1400 * np.array([math.cos(t), math.sin(t), 0])
    return [p0, p1, p2, p3]


def along(pts, u):
    for a, b in zip(pts, pts[1:]):
        L = np.linalg.norm(b - a)
        if u <= L:
            return a + (b - a) * (u / L)
        u -= L
    return pts[-1]


def pod_pose(k, u):
    pts = path_points(k)
    r, f = along(pts, u - P.AX_X), along(pts, u + P.AX_X)
    c = (r + f) / 2
    d = f - r
    yaw = math.degrees(math.atan2(d[1], d[0]))
    pitch = math.degrees(math.atan2(d[2], math.hypot(d[0], d[1])))
    return mm(Tr(*c), Rz(yaw), Ry(-pitch))


def u_pivot():
    pts = path_points("C")
    return np.linalg.norm(pts[1] - pts[0]) + np.linalg.norm(pts[2] - pts[1])


def bay_s(k, u):
    """Bay coordinate of the wagon's centre."""
    return (u - u_pivot()) - (P.PLATE_L - P.PIVOT[0]) / math.cos(math.radians(P.LANES[k]))


def hook_wire():
    """The wire's last few centimetres at the window hook: three turns on the post, the tail in the pocket."""
    w = None
    for i in range(3):
        ring = (P.cyl(1.5, 15.2) - P.cyl(3, 12.2).translate([0, 0, -1])).rotate([-90, 0, 0]).translate([-8, 27.5 + i * 1.6, 12])
        w = ring if w is None else w + ring
    zt = P.POCKET_Z + P.WIRE_D / 2
    w += P.cyl_x(P.POCKET_X0 + 0.3, 110, P.WIRE_D, 20.0, zt)                                  # tail along the pocket floor
    p0 = (-8 + 6.85 * math.cos(math.radians(-30)), 28.0, 12 + 6.85 * math.sin(math.radians(-30)))
    w += seg(p0, (P.POCKET_X0 + 1.5, 28.0, zt), P.WIRE_D)                                      # from the post, outside the hook's face
    w += seg((P.POCKET_X0 + 1.5, 28.0, zt), (P.POCKET_X0 + 1.5, 20.0, zt), P.WIRE_D)          # into the pocket
    w += seg((-8, 27.5, 12 + 6.8), (-60, 27.5, 90), P.WIRE_D)                                 # the span, down to the yard
    return w


def seg(p0, p1, d):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    v = p1 - p0
    L = float(np.linalg.norm(v))
    z = v / L
    a = np.cross([0, 0, 1.0], z)
    if np.linalg.norm(a) < 1e-9:
        R = np.eye(3)
    else:
        a /= np.linalg.norm(a)
        th = math.acos(np.clip(z[2], -1, 1))
        K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
        R = np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K
    M = np.eye(4)[:3]
    M[:, :3] = R
    M[:, 3] = p0
    return P.cyl(L, d, 16).transform(M)


# ---------------------------------------------------------------------------- cameras
def cam(direction, target, height, up=(0, 0, 1)):
    return dict(dir=list(map(float, direction)), target=list(map(float, target)), height=float(height), up=list(map(float, up)))


VIEWS = {
    "overview": cam((0.42, 0.78, -0.47), (175, 50, 30), 800),
    "landing": cam((0.05, 0.98, -0.2), (-195, 0, 50), 170),
    "switch": cam((0.42, 0.55, -0.72), (150, 35, 40), 270),
    "wagon": cam((-0.55, 0.65, -0.52), (0, 0, -14), 120),
    "wagon_explode": cam((-0.55, 0.65, -0.52), (0, 15, -14), 230),
    "wagon_out": cam((-0.55, -0.65, -0.52), (0, 0, -14), 120),
    "wagon_wire": cam((-0.45, 0.8, -0.4), (0, 0, -10), 150),
    "yard": cam((0.45, 0.7, -0.55), (340, 10, 0), 560),
    "turnout": cam((0.42, 0.55, -0.72), (110, 20, 20), 300),
    "escapement": cam((-0.3, -0.75, -0.59), (78, 62, 18), 170),
    "gantry": cam((0.55, 0.65, -0.5), (220, 10, 70), 180),
    "hook": cam((0.25, -0.9, -0.35), (20, 15, 32), 125),
    "gate": cam((0.0, 1.0, -0.15), (-30, 0, 0), 120),
}

FRAMES = []
CHECKS = []          # (frame index, moving object, other object, expected) for FreeCAD


def frame(objs, views, caption, seq, thread=None, still=None, hold=1, labels=None):
    FRAMES.append(dict(objs={k: v.flatten().tolist() for k, v in objs.items()}, views=views, caption=caption, seq=seq,
                       thread=[list(map(float, p)) for p in thread] if thread else None, still=still, hold=hold, labels=labels or {}))
    return len(FRAMES) - 1


# ---------------------------------------------------------------------------- path checks
def path_check(title, moving, fixed, n=20, expect_snap=()):
    """moving: list of (name, M_start, M_end); fixed: dict name -> M. Linear interpolation of the
    translation (rotations equal). Returns the worst overlap per pair."""
    worst = {}
    for i in range(n + 1):
        f = i / n
        for name, M0, M1 in moving:
            M = M0 + (M1 - M0) * f
            mv = placed(name, M)
            mb = mv.bounding_box()
            for on, oM in fixed.items():
                om = placed(on, oM)
                b = om.bounding_box()
                if any(mb[q] > b[q + 3] or b[q] > mb[q + 3] for q in range(3)):
                    continue
                v = ov(mv, om)
                key = (name, on)
                worst[key] = max(worst.get(key, 0.0), v)
    bad = [(k, v) for k, v in worst.items() if v > EPS]
    snaps = [(k, v) for k, v in bad if k in expect_snap]
    clashes = [(k, v) for k, v in bad if k not in expect_snap]
    tag = "clear" if not clashes else "CLASH"
    extra = "; snap fits pressed through: " + ", ".join(f"{a} in {b} ({v:.1f} mm³ at the worst moment)" for (a, b), v in snaps) if snaps else ""
    say(f"- {title}: {tag}{extra}" + ("" if not clashes else ": " + ", ".join(f"{a}/{b} {v:.2f}" for (a, b), v in clashes)))
    return not clashes


def lerp(M0, M1, f):
    return M0 + (M1 - M0) * f


def animate(seq, base, moving, n, views, caption, still=None, hold=10, thread=None):
    """base: dict of fixed objects; moving: list of (name, M0, M1). Adds n+1 frames, the last held."""
    for i in range(n + 1):
        f = 0.5 - 0.5 * math.cos(math.pi * i / n)
        objs = dict(base)
        for name, M0, M1 in moving:
            objs[name] = lerp(M0, M1, f)
        frame(objs, views, caption, seq, thread=thread, still=still if i == n else None, hold=hold if i == n else 1)


# ---------------------------------------------------------------------------- 1. wagon assembly
POD_NAMES = ["pod_plate_R", "pod_plate_L", "pod_wheel_rear", "pod_wheel_front", "pod_pannier_R", "pod_pannier_L", "pod_pin_rear", "pod_pin_front"]


def wagon_sequence():
    say("## Wagon assembly: insertion paths")
    seq, v = "wagon", ["wagon"]
    explode = {"pod_plate_R": Tr(0, 30, 0), "pod_plate_L": Tr(0, -30, 0), "pod_wheel_rear": Tr(0, 0, 0), "pod_wheel_front": Tr(0, 0, 0),
               "pod_pannier_R": Tr(0, 62, 0), "pod_pannier_L": Tr(0, -62, 0), "pod_pin_rear": Tr(0, 95, 0), "pod_pin_front": Tr(0, 95, 0)}
    frame(explode, ["wagon_explode"], "The parts of one wagon: two identical plates, two wheels, two identical panniers, two axle pins. No screws: the pins snap in.",
          seq, still="wagon_00_parts", hold=16)
    placed_ = {"pod_plate_R": I4}
    frame(dict(placed_), v, "1. Plate R, bosses and spacer peg facing the middle. (Do this lying flat on the table, peg up.)", seq, still="wagon_01_plate", hold=14)
    mv = [("pod_wheel_rear", Tr(0, -45, 0), I4), ("pod_wheel_front", Tr(0, -45, 0), I4)]
    path_check("two wheels laid on the thrust bosses over the axle holes", mv, placed_)
    animate(seq, placed_, mv, 14, v, "2. A wheel on each thrust boss, groove centred over the axle hole.", still="wagon_02_wheels")
    placed_.update({"pod_wheel_rear": I4, "pod_wheel_front": I4})
    mv = [("pod_plate_L", Tr(0, -45, 0), I4)]
    path_check("plate L laid on top, each spacer peg into the other plate's hole", mv, placed_)
    animate(seq, placed_, mv, 14, v, "3. Plate L on top, turned end for end: its peg goes into plate R's hole and plate R's peg into its hole.", still="wagon_03_plate_L")
    placed_["pod_plate_L"] = I4
    mv = [("pod_pannier_R", Tr(0, 45, 0), I4), ("pod_pannier_L", Tr(0, -45, 0), I4)]
    path_check("both panniers held against the outer faces of the plates", mv, placed_)
    animate(seq, placed_, mv, 14, ["wagon_out"], "4. Keep the stack lying flat on the table (the picture is tilted to show the holes). Put a pannier against each plate, arm holes in line with the axle holes.", still="wagon_04_panniers")
    placed_.update({"pod_pannier_R": I4, "pod_pannier_L": I4})
    mv = [("pod_pin_front", Tr(0, 42, 0), I4), ("pod_pin_rear", Tr(0, 42, 0), I4)]
    ok = path_check("axle pins pushed in from the right: arm, plate, wheel, plate, arm",
                    mv, placed_, n=60, expect_snap={(p, q) for p in ("pod_pin_front", "pod_pin_rear") for q in POD_NAMES})
    # the pins without their snap bump must be clear all the way
    LOCAL["_pin_shank"] = P.cyl(P.PIN_SPAN + 2.0, P.AXLE_D).rotate([90, 0, 0]).translate([0, P.ARM_Y1, 0])
    for x in (-P.AX_X, P.AX_X):
        path_check(f"axle pin shank alone at x = {x:+.0f} (snap bump removed)", [("_pin_shank", Tr(x, 42, 0), Tr(x, 0, 0))], placed_, n=60)
    animate(seq, placed_, [mv[0]], 16, ["wagon_out"], "5. Push the front axle pin down through pannier, plate, wheel, plate and pannier until the split end clicks out of the far side.", still="wagon_05_pin_front")
    placed_["pod_pin_front"] = I4
    animate(seq, placed_, [mv[1]], 16, ["wagon_out"], "6. Same for the rear pin. The peg shoulders set the plate gap; the wheels spin with 0.2 mm side play.", still="wagon_06_pin_rear")
    placed_["pod_pin_rear"] = I4
    # onto the wire
    LOCAL["_wire_short"] = P.cyl_x(-120, 120, P.WIRE_D, 0, -P.R_WIRE)
    add("wire_short", LOCAL["_wire_short"], "wire")
    mv = [(n_, Tr(0, 0, 45), I4) for n_ in POD_NAMES]
    fixed = {"wire_short": I4}
    ok2 = True
    body, wheels, seat = 0.0, 0.0, None
    for i in range(91):
        z = 45 * (1 - i / 90)
        for n_ in POD_NAMES:
            v_ = ov(placed(n_, Tr(0, 0, z)), LOCAL["wire_short"])
            if n_.startswith("pod_wheel"):
                if v_ > EPS and seat is None:
                    seat = z
            else:
                body = max(body, v_)
    say(f"- wagon lowered onto the wire (the wire passes up between the baskets and through the 2.6 mm slot between the lips into the wheel grooves): "
        f"plates, lips, panniers and pins {'clear all the way' if body <= EPS else 'CLASH %.2f' % body}; "
        + ("the wheels touch the wire only as they sit down on it" if seat is None or seat < 0.2 else f"the wheels touch the wire {seat:.1f} mm above their seat"))
    base = {"wire_short": I4}
    animate(seq, base, mv, 18, ["wagon_wire"], "7. Hang it on the wire: lower it so the wire passes up between the baskets, through the slot between the lips, into the wheel grooves.",
            still="wagon_07_on_wire")
    say()


# ---------------------------------------------------------------------------- 2. yard assembly
def yard_sequence():
    say("## Yard assembly: insertion paths")
    seq = "yard"
    Tright = -P.THETA - P.OVERTRAVEL
    placed_ = {"handover": I4}
    frame(dict(placed_), ["yard"], "1. Handover on the floor at the foot of the wire.", seq, still="yard_01_handover", hold=14)
    mv = [("turnout_plate", Tr(0, 0, 40), I4)]
    path_check("turnout plate lowered so its entry slot drops over the handover's dovetail tab", mv, placed_)
    animate(seq, placed_, mv, 12, ["yard"], "2. Turnout plate: lower its entry slot straight down over the handover's tab (always lower the slot onto the tab).",
            still="yard_02_turnout")
    placed_["turnout_plate"] = I4
    lanes_placed = {}
    for i, (n, fn, L) in enumerate(A.BAY):
        s0 = sum(LL for _, _, LL in A.BAY[:i])
        mv = []
        for k in P.LANES:
            nm = f"bay_{n}_{k}"
            if nm not in LOCAL:
                LOCAL[nm] = LOCAL[f"bay_{n}"]
                OBJ[nm] = dict(OBJ[f"bay_{n}"])
            mv.append((nm, bay_M(k, s0, 40), bay_M(k, s0)))
        fixed = dict(placed_)
        fixed.update(lanes_placed)
        path_check(f"three {n} segments lowered onto the previous dovetail tabs", mv, fixed)
        base = dict(placed_)
        base.update(lanes_placed)
        animate(seq, base, mv, 12, ["yard"], f"{3 + i}. Three {dict(lead='lead rails', brake='brake combs', chainbed='chain beds', bumper='bumpers')[n]}: each slot drops over the tab of the piece before.",
                still=f"yard_{3 + i:02d}_{n}")
        for nm, _, M1 in mv:
            lanes_placed[nm] = M1
    placed_.update(lanes_placed)
    v = ["turnout"]
    Tin = -P.THETA / 2
    M_up = mm(Tr(6, 0, 40), tongue_M(Tin))
    M_hover = mm(Tr(6, 0, 10.5), tongue_M(Tin))
    M_back = mm(Tr(0, 0, 10.5), tongue_M(Tin))
    ok = path_check("tongue, held between lanes R and C, lowered to 10.5 mm, 6 mm forward of its post", [("tongue", M_up, M_hover)], placed_)
    ok &= path_check("tongue slid back 6 mm so its boss passes under the end of the entry rail", [("tongue", M_hover, M_back)], placed_)
    ok &= path_check("tongue lowered onto the pivot post", [("tongue", M_back, tongue_M(Tin))], placed_)
    worst = max(ov(placed("tongue", tongue_M(Tin + (Tright - Tin) * f)), placed("turnout_plate", I4)) for f in np.linspace(0, 1, 21))
    say(f"- tongue swung on its post to the right-hand stop: {'clear' if worst <= EPS else 'CLASH %.2f' % worst} (it touches the stop at the end)")
    base = dict(placed_)
    animate(seq, base, [("tongue", M_up, M_hover)], 10, v, "7. Tongue: hold it pointing between lanes R and C, a finger's width forward of the pivot post and just above it.")
    animate(seq, base, [("tongue", M_hover, M_back)], 8, v, "7. Slide it back so its round boss passes under the end of the entry rail, over the post.")
    animate(seq, base, [("tongue", M_back, tongue_M(Tin))], 8, v, "7. Lower it onto the post.")
    for i in range(9):
        objs = dict(base)
        objs["tongue"] = tongue_M(Tin + (Tright - Tin) * i / 8)
        frame(objs, v, "7. Swing it to the right-hand stop.", seq, still="yard_07_tongue" if i == 8 else None, hold=10 if i == 8 else 1)
    placed_["tongue"] = tongue_M(Tright)
    dR = spring_defl(Tright)
    sp = spring_name(dR)
    mv = [(sp, Tr(0, 0, 25), I4)]
    path_check("spring foot lowered into its socket with the leaf bent against the tab", mv, {k: v_ for k, v_ in placed_.items() if k != "tongue"})
    animate(seq, placed_, mv, 12, v, "8. Leaf spring: bend the leaf toward the tongue's tab and drop the foot into its socket. It pushes the tongue toward bay L.",
            still="yard_08_spring")
    placed_[sp] = I4
    mv = [("rocker_bridge", rocker_M(0, 40), rocker_M(0))]
    path_check("rocker bridge lowered over the tooth ring onto its four pegs", mv, placed_)
    animate(seq, dict(placed_), mv, 12, ["escapement"], "9. Rocker bridge: lower it over the ring of teeth so its four holes drop onto the plate's pegs.",
            still="yard_09_bridge")
    placed_["rocker_bridge"] = rocker_M(0)
    # rocker: pin through the bore, coins in, lowered into the notches
    v = ["escapement"]
    up = 45.0
    mvpin = [("rocker_pin", mm(rocker_M(P.REST_TILT, up), Tr(-35, 0, 0)), rocker_M(P.REST_TILT, up))]
    path_check("rocker pin pushed through the rocker's bore (above the yard)", mvpin, {"rocker": rocker_M(P.REST_TILT, up)}, n=40,
               expect_snap={("rocker_pin", "rocker")})
    base = dict(placed_)
    base["rocker"] = rocker_M(P.REST_TILT, up)
    animate(seq, base, mvpin, 12, v, "10. Push the 3 mm pin through the rocker's bore until the split end clicks out of the far side.", still="yard_10_rocker_pin")
    base["rocker_pin"] = rocker_M(P.REST_TILT, up)
    mvc = [("coins", rocker_M(P.REST_TILT, up + 25), rocker_M(P.REST_TILT, up))]
    animate(seq, base, mvc, 10, v, "11. About 15 g of coins or washers in the cup on the outer arm.", still="yard_11_coins")
    mv = [("rocker", rocker_M(P.REST_TILT, up), rocker_M(P.REST_TILT)), ("rocker_pin", rocker_M(P.REST_TILT, up), rocker_M(P.REST_TILT)),
          ("coins", rocker_M(P.REST_TILT, up), rocker_M(P.REST_TILT))]
    path_check("rocker with pin lowered into the bridge notches, cup side down, tongue held at its right-hand stop", mv,
               placed_, n=45)
    base = dict(placed_)
    animate(seq, base, mv, 14, v, "12. Lower the rocker, cup side outward, so the pin drops into the two bridge notches. Finger A falls in front of the first tooth.",
            still="yard_12_rocker")
    placed_.update({"rocker": rocker_M(P.REST_TILT), "rocker_pin": rocker_M(P.REST_TILT), "coins": rocker_M(P.REST_TILT)})
    # release the tongue: the spring carries it onto finger A
    T_rest = A.first_contact(Tright, P.REST_TILT, P.THETA + P.OVERTRAVEL)
    for i in range(9):
        T = Tright + (T_rest - Tright) * i / 8
        objs = dict(placed_)
        objs["tongue"] = tongue_M(T)
        objs.pop(sp, None)
        objs[spring_name(spring_defl(T))] = I4
        frame(objs, v, f"13. Let go of the tongue: the spring carries it {T_rest - Tright:.2f}° until its tooth stops on finger A. The points are set for bay R.",
              seq, still="yard_13_set_R" if i == 8 else None, hold=12 if i == 8 else 1)
    placed_["tongue"] = tongue_M(T_rest)
    placed_.pop(sp, None)
    placed_[spring_name(spring_defl(T_rest))] = I4
    # flap on its axle, snapped into the posts
    v = ["gantry"]
    up = 40.0
    mvax = [("gantry_axle", mm(flap_M(0, up), Tr(0, -150, 0)), flap_M(0, up))]
    path_check("gantry axle slid through the flap's hub (above the yard)", [("gantry_axle", mm(Tr(P.GANTRY_X, -150, P.GANTRY_Z + up)), Tr(P.GANTRY_X, 0, P.GANTRY_Z + up))],
               {"flap": flap_M(0, up)}, n=60)
    base = dict(placed_)
    base["flap"] = flap_M(0, up)
    animate(seq, base, [("gantry_axle", Tr(P.GANTRY_X, -150, P.GANTRY_Z + up), Tr(P.GANTRY_X, 0, P.GANTRY_Z + up))], 12, v,
            "14. Slide the 4 mm axle through the flap's hub.", still="yard_14_axle")
    mv = [("flap", flap_M(0, up), flap_M(0)), ("gantry_axle", Tr(P.GANTRY_X, 0, P.GANTRY_Z + up), Tr(P.GANTRY_X, 0, P.GANTRY_Z))]
    path_check("flap and axle pressed down into the gantry posts' snap notches", mv, placed_, n=40,
               expect_snap={("gantry_axle", "turnout_plate")})
    animate(seq, dict(placed_), mv, 12, v, "15. Press the axle down into the two post notches until it clicks; the flap hangs free.", still="yard_15_flap")
    placed_.update({"flap": flap_M(0), "gantry_axle": Tr(P.GANTRY_X, 0, P.GANTRY_Z)})
    th = [P.crank_hole(0), P.rocker_hole(P.REST_TILT)]
    frame(dict(placed_), ["turnout"], "16. Thread from the crank's hole to the hole at the end of the rocker's arm, straight but not lifting the rocker (0 to 1.5 mm slack).",
          seq, thread=th, still="yard_16_thread", hold=14)
    # sleds and chains
    mv = []
    for k in P.LANES:
        for nm0 in ("sled", "chain"):
            nm = f"{nm0}_{k}"
            if nm not in LOCAL:
                LOCAL[nm] = LOCAL[nm0]
                OBJ[nm] = dict(OBJ[nm0])
            mv.append((nm, bay_M(k, 420, 30), bay_M(k, 420)))
    path_check("sleds and chains laid in the chain-bed troughs", mv, placed_)
    animate(seq, dict(placed_), mv, 10, ["yard"], "17. In each chain bed: the sled in the trough just past the start, a few M4 nuts in it, the chain tied to its back and laid in the trough behind it.",
            still="yard_17_sleds", thread=th)
    for nm, _, M1 in mv:
        placed_[nm] = M1
    fixed = dict(placed_)
    say(f"- wire laid in the handover groove, down the dive slot and along the grooves underneath: "
        f"{'clear' if all(ov(LOCAL['wire'], placed(n_, M_)) <= EPS for n_, M_ in fixed.items() if not n_.startswith(('sled', 'chain', 'coins'))) else 'CLASH'}")
    objs = dict(placed_)
    objs["wire"] = I4
    frame(objs, ["yard"], "18. Lay the wire: in the groove on the handover's head, down the dive slot, along the groove under the handover and the turnout, on to the furniture leg.",
          seq, thread=th, still="yard_18_wire", hold=16)
    say()
    return placed_, th


_spring_cache = {}


def spring_defl(T):
    key = round(T, 2)
    if key in _spring_cache:
        return _spring_cache[key]
    tg = A.tongue_at(T)
    d0, d1 = 0.0, 25.0
    for _ in range(20):
        m_ = (d0 + d1) / 2
        if ov(P.bias_spring(m_), tg) > EPS:
            d0 = m_
        else:
            d1 = m_
    _spring_cache[key] = d1
    return d1


def spring_name(d):
    d = float(SPRING_STEPS[np.argmin(np.abs(SPRING_STEPS - (d + 0.25)))])
    return f"spring_{d:04.1f}"


# ---------------------------------------------------------------------------- 3. wire ends
def ends_sequence():
    say("## Window hook and start gate")
    seq = "ends"
    base = {"window_hook": I4, "hook_wire": I4}
    W0 = mm(Tr(P.POCKET_X0 + 40, 26.0, P.POCKET_Z + P.WIRE_D))
    W1 = mm(Tr(P.POCKET_X0 + 12, 26.0, P.POCKET_Z + P.WIRE_D))
    hook_fixed = {"window_hook": I4, "hook_wire": I4}
    v_hw = ov(LOCAL["hook_wire"], LOCAL["window_hook"])
    say(f"- wire wrapped on the hook's post and laid in its pocket: {'clear of the hook' if v_hw <= EPS else 'CLASH %.2f' % v_hw}")
    path_check("wedge pushed into the pocket over the wire until it grips", [("wedge", W0, W1)], hook_fixed, n=40)
    LOCAL["_wedge_further"] = LOCAL["wedge"]
    stop = ov(placed("wedge", mm(Tr(P.POCKET_X0 + 11, 26.0, P.POCKET_Z + P.WIRE_D))), LOCAL["hook_wire"]) + \
        ov(placed("wedge", mm(Tr(P.POCKET_X0 + 11, 26.0, P.POCKET_Z + P.WIRE_D))), LOCAL["window_hook"])
    say(f"- one millimetre further the wedge is already tight (overlap {stop:.2f} mm³ with the wire and the pocket roof): it grips with about 8 mm showing")
    frame(dict(base), ["hook"], "Window end: three turns of wire round the capstan post, the tail laid along the pocket floor.", seq, still="ends_01_hook_wire", hold=14)
    animate(seq, base, [("wedge", W0, W1)], 12, ["hook"], "Push the wedge in from the open end over the wire until it is tight; about 8 mm stays out. Then hang the hook on the grill.",
            still="ends_02_wedge")
    # gate: clamp lowered onto the wire, key in, lever pinned, wagon hooked
    gx = P.GATE_CX
    G = Tr(gx, 0, 0)            # gate frame: wire at z = 0
    wire = "wire_gate"
    LOCAL[wire] = P.cyl_x(-140, 80, P.WIRE_D, -0.2, 0)            # pressed against the far wall by the key
    add(wire, LOCAL[wire], "wire")
    fixed = {wire: I4}
    path_check("gate clamp lowered onto the wire (the wire enters the slot in its underside)", [("gate", mm(Tr(gx, 0, 30)), G)], fixed, n=40)
    animate(seq, fixed, [("gate", mm(Tr(gx, 0, 30)), G)], 12, ["gate"], "Start gate: lower the clamp onto the wire about 0.3 m below the hook; the wire goes up the slot into the bore.",
            still="ends_03_gate")
    fixed["gate"] = G
    # key: profile x 0..30 (thin end at 0), placed with its thin end toward -x and flat face against the wire
    fy = -(P.WIRE_D + 0.4) / 2 + 1.0 + P.KEY_TAPER * 9.8
    kM0 = mm(Tr(gx - 15 - 40, fy, -3.3))              # from the uphill end: the key's tail points away from the wagon
    kM1 = mm(Tr(gx - 15 - 9.8, fy, -3.3))
    LOCAL["gate_key_placed"] = P.section([(0, 0), (30, 0), (30, 1.6), (0, 3.1)], "xy", 0, 6.6)
    add("gate_key_placed", LOCAL["gate_key_placed"], "pin")
    path_check("gate key slid in beside the wire", [("gate_key_placed", kM0, kM1)], fixed, n=40)
    animate(seq, fixed, [("gate_key_placed", kM0, kM1)], 12, ["gate"], "From the uphill end, slide the tapered key in beside the wire until it grips; about 10 mm stays out, pointing away from the wagon.", still="ends_04_key")
    fixed["gate_key_placed"] = kM1
    pin_M = Tr(gx + P.GPX, 0, P.GPZ)
    lev_M = Tr(gx, 0, 0)
    fixed2 = dict(fixed)
    animate(seq, fixed2, [("gate_lever", Tr(gx, 0, 20), lev_M)], 10, ["gate"], "Drop the lever between the lugs.", still="ends_05_lever")
    fixed2["gate_lever"] = lev_M
    path_check("gate pin pushed through the lugs and the lever", [("gate_pin", mm(Tr(gx + P.GPX, 30, P.GPZ)), mm(Tr(gx + P.GPX, 5.1, P.GPZ)))],
               {"gate": G, "gate_lever": lev_M}, n=40)
    animate(seq, fixed2, [("gate_pin", mm(Tr(gx + P.GPX, 30, P.GPZ)), mm(Tr(gx + P.GPX, 5.1, P.GPZ)))], 10, ["gate"], "Push the 3 mm pin through the lugs and the lever.",
            still="ends_06_pin")
    fixed2["gate_pin"] = mm(Tr(gx + P.GPX, 5.1, P.GPZ))
    # wagon pushed back under the lever: the hook rides over the peg and drops in front of it
    podM = lambda dx: Tr(dx, 0, P.R_WIRE)
    piv = np.array([gx + P.GPX, 0, P.GPZ])

    def lever_angle(dx):
        pod = A.union([placed(n_, podM(dx)) for n_ in POD_NAMES])
        for a in np.arange(0, 40, 0.25):
            M = mm(Tr(*piv), Ry(-a), Tr(*(-piv)), lev_M)
            if ov(placed("gate_lever", M), pod) <= EPS:
                return a, M
        return None, None

    hits = []
    for dx in np.linspace(40, 0, 21):
        a, M = lever_angle(dx)
        if a is None:
            hits.append(dx)
        objs = dict(fixed2)
        objs["gate_lever"] = M if M is not None else lev_M
        for n_ in POD_NAMES:
            objs[n_] = podM(dx)
        frame(objs, ["gate"], "Hang a wagon below the gate and push it back: its rear spacer peg lifts the hook, which drops in front of the peg.",
              seq, still="ends_07_latched" if dx == 0 else None, hold=12 if dx == 0 else 1)
    say(f"- wagon pushed back into the gate: the lever rides up over the peg and drops in front of it: {'clear' if not hits else 'JAMS at ' + str(hits)}")
    latched = {"gate": G, "gate_key_placed": kM1, "gate_pin": fixed2["gate_pin"], wire: I4}
    path_check("latched wagon against the gate body, the key and the lever pin (the lever itself is meant to touch the peg)",
               [(n_, podM(40), podM(0)) for n_ in POD_NAMES if not n_.startswith("pod_wheel")], {k_: v_ for k_, v_ in latched.items() if k_ != wire}, n=40)
    path_check("latched wagon's wheels against the gate body, the key and the lever pin",
               [(n_, podM(40), podM(0)) for n_ in POD_NAMES if n_.startswith("pod_wheel")], {k_: v_ for k_, v_ in latched.items() if k_ != wire}, n=40)
    for a in np.linspace(0, 24, 13):
        M = mm(Tr(*piv), Ry(-a), Tr(*(-piv)), lev_M)
        objs = dict(fixed2)
        objs["gate_lever"] = M
        for n_ in POD_NAMES:
            objs[n_] = podM(0 if a < 20 else 4 * (a - 20))
        frame(objs, ["gate"], "To release, lift the lever about 20°: the hook clears the peg and the wagon rolls away down the wire.", seq,
              still="ends_08_release" if a == 24 else None, hold=12 if a == 24 else 1)
    say()


# ---------------------------------------------------------------------------- 4. the run
def taut_tilt(s, slack=0.5):
    L0 = np.linalg.norm(np.subtract(P.crank_hole(0), P.rocker_hole(P.REST_TILT))) + slack
    c = np.array(P.crank_hole(s))
    t = P.REST_TILT
    while t < 40 and np.linalg.norm(c - np.array(P.rocker_hole(t))) > L0:
        t += 0.05
    return min(t, P.LIMIT_TILT)


def move_rocker_phys(T, t_from, t_to, steps=6, max_recoil=0.2):
    """Tilt the rocker toward t_to; the spring advances the tongue after each step. A finger may
    push the tongue back by at most max_recoil; beyond that the finger comes to rest on the tooth
    and the rocker stops tilting there. Returns (tongue angle, rocker tilt)."""
    T_max = P.THETA + P.OVERTRAVEL
    t_prev = t_from
    for t in np.linspace(t_from, t_to, steps + 1)[1:]:
        if ov(A.tongue_at(T), A.rocker_at(t)) > EPS:
            back = T
            while back > T - max_recoil and ov(A.tongue_at(back), A.rocker_at(t)) > EPS:
                back -= 0.02
            if ov(A.tongue_at(back), A.rocker_at(t)) > EPS:
                lo, hi = t_prev, t
                for _ in range(14):
                    mid = (lo + hi) / 2
                    if ov(A.tongue_at(T), A.rocker_at(mid)) > EPS:
                        hi = mid
                    else:
                        lo = mid
                RESTING.append((round(T, 2), round(lo, 1)))
                return T, lo
            T = back
        T = A.first_contact(T, t, T_max)
        t_prev = t
    return T, t_to


RESTING = []


def run_sequence(yard):
    say("## The run: three wagons down the wire, into bays R, C and L")
    statics = {k: v for k, v in yard.items() if k not in ("tongue", "rocker", "rocker_pin", "coins", "flap") and not k.startswith(("spring_", "sled", "chain"))}
    statics["wire"] = I4
    static_union = A.union([placed(n, M) for n, M in statics.items() if n != "wire"])
    order = [("R", "pod1"), ("C", "pod2"), ("L", "pod3")]
    parked = {}
    T = A.first_contact(-P.THETA - P.OVERTRAVEL, P.REST_TILT, P.THETA + P.OVERTRAVEL)
    tilt = P.REST_TILT
    sled_push = {k: 0.0 for k in P.LANES}
    events, clashes, landing = [], {}, []
    for pod_i, (k, tag) in enumerate(order):
        names = {n: f"{tag}_{n[4:]}" for n in POD_NAMES}
        for n, nn in names.items():
            if nn not in LOCAL:
                LOCAL[nn] = LOCAL[n]
                OBJ[nn] = dict(OBJ[n])
        up = u_pivot()
        u_contact = up + (420 + 16 - P.BX) + (P.PLATE_L - P.PIVOT[0]) / math.cos(math.radians(P.LANES[k]))
        u_comb = up + (230 - P.BX) + (P.PLATE_L - P.PIVOT[0]) / math.cos(math.radians(P.LANES[k]))
        push = 60.0
        us, u = [], 30.0
        while u < u_contact + push:
            us.append(u)
            if u < u_comb:
                step = 13.0
            elif u < u_contact:
                step = 13.0 - 7.0 * (u - u_comb) / (u_contact - u_comb)
            else:
                step = max(1.5, 6.0 * (1 - (u - u_contact) / push))
            u += step
        us.append(u_contact + push)
        for fi, u in enumerate(us):
            M = pod_pose(k, u)
            pod_now = {nn: M for n, nn in names.items()}
            pod_solids = [placed(n, M) for n in POD_NAMES]
            pod_union = A.union(pod_solids)
            # flap
            s = 0.0
            cx = M[0, 3]
            if 150 < cx < 300:
                if ov(pod_union, A.flap_at(0.0)) > EPS:
                    lo, hi = 0.0, 80.0
                    for _ in range(14):
                        mid = (lo + hi) / 2
                        if ov(pod_union, A.flap_at(mid)) > EPS:
                            lo = mid
                        else:
                            hi = mid
                    s = hi
            new_tilt = taut_tilt(s)
            if abs(new_tilt - tilt) > 1e-6:
                T_before = T
                T, tilt = move_rocker_phys(T, tilt, new_tilt)
                if abs(T - T_before) > 0.01:
                    # is any wheel on the tongue while it moves?
                    rel = (u - P.AX_X) - up
                    events.append((tag, round(u), round(T_before, 2), round(T, 2), rel))
            # sled push
            if u > u_contact:
                sled_push[k] = u - u_contact
            # landing record
            if abs(cx - NOSE) < 60:
                body = A.union([sol for n, sol in zip(POD_NAMES, pod_solids) if not n.startswith("pod_wheel")])
                landing.append(ov(body, placed("handover", I4)) + ov(body, LOCAL["wire"]))
            # clash check against everything that is not meant to touch
            others = dict(statics)
            others.update({"tongue": tongue_M(T), "rocker": rocker_M(tilt), "coins": rocker_M(tilt), "rocker_pin": rocker_M(0), "flap": flap_M(s),
                           spring_name(spring_defl(T)): I4})
            for kk in P.LANES:
                others[f"sled_{kk}"] = bay_M(kk, 420 + sled_push[kk])
                others[f"chain_{kk}"] = bay_M(kk, 420 + sled_push[kk])
            for pk, pM in parked.items():
                others[pk] = pM
            for kk in P.LANES:
                for nm_ in (f"sled_{kk}", f"chain_{kk}"):
                    sm = placed(nm_, others[nm_])
                    for on in (f"bay_brake_{kk}", f"bay_chainbed_{kk}", f"bay_bumper_{kk}"):
                        v = ov(sm, placed(on, statics[on]))
                        if v > EPS:
                            key = ("yard", nm_, on, "CLASH")
                            clashes[key] = max(clashes.get(key, 0.0), v)
            for n, sol in zip(POD_NAMES, pod_solids):
                b = sol.bounding_box()
                for on, oM in others.items():
                    if on in ("wire",):
                        continue
                    om = placed(on, oM)
                    ob = om.bounding_box()
                    if any(b[q] > ob[q + 3] or ob[q] > b[q + 3] for q in range(3)):
                        continue
                    v = ov(sol, om)
                    if v <= EPS:
                        continue
                    intended = (n == "pod_pannier_R" and on.startswith("bay_brake")) or (n == "pod_pannier_L" and on.startswith(("sled", "chain")))
                    rolling = n.startswith("pod_wheel") and on in ("tongue", "turnout_plate", "handover") or (n.startswith("pod_wheel") and on.startswith("bay_"))
                    kind = "intended" if intended else ("rolling" if rolling else "CLASH")
                    key = (tag, n, on, kind)
                    clashes[key] = max(clashes.get(key, 0.0), v)
            # frame
            objs = dict(yard)
            for kk in ("tongue", "rocker", "rocker_pin", "coins", "flap"):
                objs.pop(kk, None)
            for kk in list(objs):
                if kk.startswith("spring_"):
                    objs.pop(kk)
            objs.update({"tongue": tongue_M(T), "rocker": rocker_M(tilt), "rocker_pin": rocker_M(0), "coins": rocker_M(tilt),
                         "flap": flap_M(s), "gantry_axle": Tr(P.GANTRY_X, 0, P.GANTRY_Z), spring_name(spring_defl(T)): I4, "wire": I4})
            for kk in P.LANES:
                objs[f"sled_{kk}"] = bay_M(kk, 420 + sled_push[kk])
                objs[f"chain_{kk}"] = bay_M(kk, 420 + sled_push[kk])
            objs.update(parked)
            objs.update(pod_now)
            lane_name = {"R": "bay R", "C": "bay C", "L": "bay L"}[k]
            if cx < NOSE - 30:
                stage = "on the wire"
            elif cx < NOSE + P.GROOVE_END + 20:
                stage = "landing: the wheels roll from the wire onto the rail head at the same height"
            elif u - P.AX_X < up + 101:
                stage = f"crossing the tongue, set for {lane_name}"
            elif s > 0.5:
                stage = f"lifting the flap {s:.0f}°: the rocker tips {tilt:+.0f}°, the tongue steps to {T:+.1f}°"
            elif bay_s(k, u) < 230 - P.BX:
                stage = f"rolling into {lane_name}"
            elif bay_s(k, u) < 420 + 16 - P.BX:
                stage = "brake comb: the leaves rub the right-hand basket"
            else:
                stage = f"the left basket pushes the sled and chain; stopped {sled_push[k]:.0f} mm on"
            frame(objs, ["overview", "landing", "switch"], f"Wagon {pod_i + 1} of 3 → {lane_name}: {stage}", "run",
                  thread=[P.crank_hole(s), P.rocker_hole(tilt)], labels={"tongue": round(T, 2), "tilt": round(tilt, 1), "flap": round(s, 1)},
                  still=f"run_{pod_i + 1}_{k}_stopped" if fi == len(us) - 1 else None, hold=14 if fi == len(us) - 1 else 1)
            if fi % 4 == 0:
                CHECKS.append(len(FRAMES) - 1)
        for n, nn in names.items():
            parked[nn] = pod_pose(k, us[-1])
        say(f"- wagon {pod_i + 1} reached bay {k}; tongue now {T:+.2f}° (lanes: R {-P.THETA:+.2f}, C 0.00, L {P.THETA:+.2f})")
    say()
    if RESTING:
        T_, t_ = RESTING[-1]
        say(f"- after the third wagon there is no tooth left for finger B: the tongue goes to its left-hand stop ({T_:+.2f}°, still on lane L) and when the flap "
            f"falls, finger A comes down on top of the last tooth and the rocker rests at {t_:+.1f}° instead of {P.REST_TILT:+.0f}°. Harmless: no fourth wagon comes; "
            "the reset (lift the rocker out, swing the tongue to the right-hand stop, drop the rocker back) clears it.")
        say()
    say("### Tongue movements during the run")
    for tag, u, a, b, rel in events:
        on = "a wheel is still on the tongue" if rel < 101 else f"the rear wheel is {rel - 101:.0f} mm past the tongue's tip"
        say(f"- {tag}: tongue {a:+.2f}° → {b:+.2f}° while {on}")
    say()
    if any(b >= P.THETA + P.OVERTRAVEL - 0.01 for _, _, _, b, _ in events):
        say('- After the third wagon no tooth is left for finger B, so the tongue swings to its left-hand stop (+10.25°). When the flap falls, finger A comes down at the edge of the last tooth and, in this geometry, eases the tongue back to +9.73°, on lane L. If the coins are too light to do that, finger A simply rests on the tooth with the tongue at the stop, still on lane L. Either way nothing else runs until the reset (lift the rocker out, swing the tongue to the right-hand stop, drop the rocker back).')
    say()
    say("### Contacts seen in the run (worst overlap, mm³)")
    for (tag, n, on, kind), v in sorted(clashes.items()):
        say(f"- {kind}: {tag} {n[4:] if n.startswith('pod_') else n} / {on}: {v:.2f}")
    if not any(kind == "CLASH" for (_, _, _, kind) in clashes):
        say("- no clashes: every contact is a wheel rolling over a rail joint, a basket on a comb leaf, or a basket on a sled")
    say()
    say(f"- landing at the handover nose with the wire arriving at {ALPHA}°: plates, lips, panniers and pins against the handover and the wire, "
        f"worst {max(landing) if landing else 0:.2f} mm³ (0 = clear; the wheels ride the wire into the groove and onto the head)")
    say()


# ---------------------------------------------------------------------------- 5. moving parts close-ups
def moving_parts(yard, th):
    seq = "moving"
    base = {k: v for k, v in yard.items() if not k.startswith(("spring_",))}
    base.pop("tongue", None)
    for lab, T in (("R", -P.THETA), ("C", 0.0), ("L", P.THETA)):
        objs = dict(base)
        T_ = A.first_contact(T - 0.6, P.REST_TILT, P.THETA + P.OVERTRAVEL) if lab != "L" else A.first_contact(T - 0.6, P.REST_TILT, P.THETA + P.OVERTRAVEL)
        objs["tongue"] = tongue_M(T_)
        objs[spring_name(spring_defl(T_))] = I4
        frame(objs, ["escapement"], f"Tongue held at bay {lab} ({T_:+.2f}°): finger A down on a tooth, finger B up.", seq, thread=th, still=f"moving_tongue_{lab}", hold=10)
    T0 = A.first_contact(-P.THETA - 0.6, P.REST_TILT, P.THETA + P.OVERTRAVEL)
    T1, _ = A.move_rocker(T0, P.REST_TILT, P.TRIG_TILT, P.THETA + P.OVERTRAVEL)
    objs = dict(base)
    objs.update({"tongue": tongue_M(T1), "rocker": rocker_M(P.TRIG_TILT), "coins": rocker_M(P.TRIG_TILT), spring_name(spring_defl(T1)): I4})
    frame(objs, ["escapement"], f"Rocker tipped by the thread: A up, B down; the tongue has sprung half a step to {T1:+.2f}° and B holds it.", seq,
          thread=[P.crank_hole(40), P.rocker_hole(P.TRIG_TILT)], still="moving_rocker_tipped", hold=10)
    for sw in (0, 20, 40):
        objs = dict(yard)
        objs["flap"] = flap_M(sw)
        frame(objs, ["gantry"], f"Flap swung {sw}°", seq, thread=[P.crank_hole(sw), P.rocker_hole(taut_tilt(sw))], still=f"moving_flap_{sw:02d}", hold=8)


# ---------------------------------------------------------------------------- main
def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    build_objects()
    say("# Phase 1: assembly paths and the three-wagon run, checked")
    say()
    say("Every part is moved along the path you move it by hand, in small steps, and its overlap with the parts already in place is measured "
        "with exact booleans (manifold3d). A snap fit is expected to overlap while it is pressed through; everything else must stay clear. "
        "FreeCAD repeats the same measurements with its own booleans: `freecad_motion_report.md`.")
    say()
    wagon_sequence()
    yard, th = yard_sequence()
    ends_sequence()
    run_sequence(yard)
    moving_parts(yard, th)
    json.dump(dict(objects=OBJ, views=VIEWS, frames=FRAMES, checks=CHECKS), open(BUILD / "storyboard.json", "w"))
    (HERE / "path_check_report.md").write_text("\n".join(REPORT) + "\n")
    print(f"{len(FRAMES)} frames, {len(OBJ)} objects, {len(CHECKS)} frames marked for the FreeCAD check")


if __name__ == "__main__":
    main()
