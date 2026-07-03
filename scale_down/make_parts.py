"""PLE-SBS print-only scale model, phase 1, version 2: every part as a watertight STL for a
Bambu Lab P1S, exported in its print orientation.

The only thing bought is 1.5 mm stainless wire rope. Everything else is printed.

Run:   .venv/bin/python scale_down/make_parts.py              -> stl/*.stl, parts.csv, parts_preview.png
Check: .venv/bin/python scale_down/check/assembly_check.py    (every part in its working position)

Frames (mm):
  yard frame: x along travel, y across, z up; z = 0 on top of the rail strips and the turnout plate.
  pod frame:  x along travel, y across, z up; z = 0 on the wheel axles.
Every working height comes from where the wheel's V-groove seats on the 1.5 mm wire and on the
3.5 mm rail head, so the wire, the wagon, the rails and the yard agree by construction.
Version 1 (printed 27 June 2026) is kept in check/make_parts_v1.py with its audit.
"""
import csv
import math
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, Mesh

HERE = Path(__file__).resolve().parent
OUT = HERE / "stl"
SEG = 64
BED = 250.0

# ======================================================================================
# shared dimensions
# ======================================================================================
CLR = 0.2                         # running clearance per side on every assembled fit
WIRE_D = 1.5
WEB_T, WEB_H = 2.0, 46.0
HEAD_D = 3.5
HEAD_Z = WEB_H + HEAD_D / 2       # 47.75
HEAD_TOP = HEAD_Z + HEAD_D / 2    # 49.5
STRIP_T, STRIP_W, LEAD_W = 4.0, 40.0, 22.0
DOVE = (12.0, 10.0, 14.0)

WHEEL_OD, WHEEL_W, GROOVE_R, FLAT = 24.0, 8.0, 9.0, 1.2
AXLE_D = 4.0


def seat(d):
    """Axle-to-centre distance of a round section of diameter d sitting in the wheel's V."""
    phi = math.atan(0.8)
    return GROOVE_R + (d / 2 / math.cos(phi) - FLAT / 2) / 0.8


R_WIRE = seat(WIRE_D)             # 9.45
R_HEAD = seat(HEAD_D)             # 11.05
POD_Z = HEAD_Z + R_HEAD           # 58.80: axle above the strip on a rail

# wagon (pod frame)
PL_T, GAP = 3.6, 9.2                               # plate thickness a multiple of the 0.2 mm layer; gap = wheel 8 + two 0.4 bosses + 0.2 play each side
Y_IN, Y_OUT = GAP / 2, GAP / 2 + PL_T              # 4.6, 8.2
PL_X, PL_ZB, PL_ZT = 32.0, -20.0, 20.0
AX_X = 20.0
LIP_TOP = -12.6                                    # 0.4 mm under the head, 2.4 mm under the wire
SLOT_W = 3.0                                      # lips: 0.5 mm each side of the 2 mm web (a printed blade is not straight to 0.3); they reach 0.25 under the head
BOSS_D, BOSS_H = 8.0, 0.4                          # two layers
PEG_D, PEG_X, PEG_Z = 5.0, 24.0, 16.0
ARM_Y0, ARM_Y1 = Y_OUT, Y_OUT + 6.0                # 8.1, 14.1
ARM_X, ARM_ZT = 30.0, 8.0
BX, BY0, BY1 = 32.0, 4.0, ARM_Y1
BZB = 12.0 - POD_Z                                 # basket floor 12 mm above the strip
BZT = BZB + 24.0
BWALL, BFLOOR = 1.6, 2.4
PIN_SPAN = 2 * ARM_Y1                              # 28.2
PEG_SHOULDER_D = 7.6                               # collar on each spacer peg that sets the plate gap; 0.7 clear of the wheel

# turnout
PIVOT = (40.0, 0.0)
TONGUE_LEN, TIP_OFF = 100.0, 17.0
THETA = math.degrees(math.atan2(TIP_OFF, TONGUE_LEN))   # 9.65: tongue angle between lanes
LANES = {"L": THETA, "C": 0.0, "R": -THETA}
FILL_ORDER = ["R", "C", "L"]
PLATE_L, PLATE_Y0, PLATE_Y1 = 236.0, -70.0, 85.0
ENTRY_END, ENTRY_HEAD_END = 33.5, 38.5
TONGUE_HEAD_START = -0.5
SHOE_T, SHOE_W = 2.0, 10.0
TBOSS_R, TBOSS_H = 6.0, 9.0
OVERTRAVEL = 0.6                   # tongue stops, degrees beyond the outer lanes
# escapement: teeth on a ring carried by the tongue, two fingers on a rocker above it.
# The rocker axis is a horizontal line tangent to the circle r = R_AX at angle PHI_M, so the
# fingers rise and fall without moving along the teeth.
PHI_M, R_AX = 65.0, 62.0
ROCK_Z = 15.3
REST_TILT, TRIG_TILT, LIMIT_TILT = -15.0, 15.0, 22.0    # outer side down at rest
FING_Y, FING_H, FING_TW, FING_RW = 7.0, 7.4, 2.0, 3.0  # radial offset, hang below the axis, widths
CONTACT_Z = 6.0                    # height of the finger-tooth contact
RING_R0, RING_R1, RING_T = 49.5, 75.0, 3.0
TOOTH_R0, TOOTH_R1, TOOTH_Z0, TOOTH_Z1, TOOTH_W = 51.5, 73.0, 2.5, 8.5, 2.0
TEETH_T = [-2 * THETA, -THETA, 0.0, THETA]             # tongue angle at which each tooth rests on finger A
STEP_B = 1.5 * THETA               # finger B sits one and a half steps ahead of finger A
BEAM_X0, BEAM_X1, BEAM_Z0, BEAM_Z1 = 15.7, 19.7, 11.0, 17.0   # 2.5 mm over the teeth: bridge sag
BEAM_Y0, BEAM_Y1 = -26.5, 20.0
ROCK_X = 15.3                      # rocker half-length along its axis
ARM_IN, ARM_OUT, CUP_Y, CUP_D = -24.0, 53.0, 36.0, 26.0       # cup takes a 1-rupee coin or M8 washers
THREAD_HOLE_Y = 50.0
REST_STOP_Y, LIMIT_STOP_Y = 24.0, -20.0
# tongue spring
TAB_X0, TAB_X1, TAB_Y0, TAB_Y1, TAB_H = 22.0, 38.0, -15.0, -4.0, 6.0
SPRING_ROOT = (7.0, -12.0)
SPRING_FREE_TIP = (70.0, -7.0)
SPRING_T, SPRING_H = 2.0, 5.0
# gantry
GANTRY_X, GANTRY_Z = 220.0, 100.0
FLAP_LEN, FLAP_Y, HUB_Y = 30.0, 50.0, 57.0
POST_Y = (60.0, 66.0)
CRANK_R, CRANK_Y = 16.0, (52.0, 57.0)                  # with the thread hole at 50: 11 deg of tilt at 1.5 mm slack
# the wire under the yard
HO_L, GROOVE_END, DIVE_ANG = 170.0, 45.0, 51.0
WIRE_C = HEAD_TOP - 0.15           # wire centre in the handover groove (wheel height is the same on wire and head)


def _dive_bottom_x():
    return GROOVE_END + (WIRE_C + STRIP_T - 1.1) / math.tan(math.radians(DIVE_ANG))


WIRE_EXIT = (_dive_bottom_x() - HO_L, 0.0)         # yard frame
WIRE_SLOPE = -0.0517


def wire_y(x):
    return WIRE_EXIT[1] + WIRE_SLOPE * (x - WIRE_EXIT[0])


# ======================================================================================
# geometry helpers
# ======================================================================================
def cyl(h, d, seg=SEG):
    return Manifold.cylinder(h, d / 2, d / 2, seg, False)


def box(x, y, z, at=(0, 0, 0)):
    return Manifold.cube([x, y, z], False).translate(list(at))


def poly(pts):
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return CrossSection([list(pts)[::-1] if a < 0 else list(pts)])


def _remap(m, f):
    mm = m.to_mesh()
    v = np.asarray(mm.vert_properties)[:, :3].astype(np.float64)
    return Manifold(Mesh(vert_properties=np.asarray(f(v), dtype=np.float32), tri_verts=np.asarray(mm.tri_verts, dtype=np.uint32)))


def section(pts, plane, a0, a1):
    """Prism from a 2-D section. plane 'xy': pts (x, y), along z; 'xz': pts (x, z), along y;
    'yz': pts (y, z), along x. Extruded from a0 to a1 along the third axis."""
    m = poly(pts).extrude(a1 - a0)
    if plane == "xy":
        return m.translate([0, 0, a0])
    if plane == "xz":      # (u, v, h) -> (u, a1 - h, v): rotation, keeps the solid outward
        return _remap(m, lambda v: np.column_stack([v[:, 0], a1 - v[:, 2], v[:, 1]]))
    if plane == "yz":      # (u, v, h) -> (a0 + h, u, v): cyclic, keeps orientation
        return _remap(m, lambda v: np.column_stack([a0 + v[:, 2], v[:, 0], v[:, 1]]))
    raise ValueError(plane)


def cyl_y(y0, y1, d, x=0.0, z=0.0, seg=SEG):
    return section([(x + d / 2 * math.cos(2 * math.pi * i / seg), z + d / 2 * math.sin(2 * math.pi * i / seg)) for i in range(seg)], "xz", y0, y1)


def cyl_x(x0, x1, d, y=0.0, z=0.0, seg=SEG):
    return section([(y + d / 2 * math.cos(2 * math.pi * i / seg), z + d / 2 * math.sin(2 * math.pi * i / seg)) for i in range(seg)], "yz", x0, x1)


def teardrop_pts(d, cu=0.0, cv=0.0, n=40):
    """Round section with a 45-degree peak toward +v: horizontal holes that print without drooping."""
    r = d / 2
    pts = [(cu + r * math.cos(math.radians(a)), cv + r * math.sin(math.radians(a))) for a in np.linspace(135, 405, n)]
    return pts + [(cu, cv + r * math.sqrt(2))]


def tear_y(y0, y1, d, x=0.0, z=0.0):
    return section(teardrop_pts(d, x, z), "xz", y0, y1)


def tear_x(x0, x1, d, y=0.0, z=0.0):
    return section(teardrop_pts(d, y, z), "yz", x0, x1)


def polar(r, deg, c=(0.0, 0.0)):
    return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


def sector(r0, r1, a0, a1, z0, z1, n=48):
    pts = [polar(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [polar(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    return section(pts, "xy", z0, z1)


def bar(a, b, w, z0, z1):
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy * w / 2, ux * w / 2
    return section([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], "xy", z0, z1)


def place(m, deg, x, y, z=0.0):
    return m.rotate([0, 0, deg]).translate([x, y, z])


# ======================================================================================
# rails
# ======================================================================================
def rail(L, z0=0.0, pointed=False):
    """Blade rail along +x from 0 to L: 2 mm web from z0 up, 3.5 mm head at HEAD_Z."""
    r = box(L, WEB_T, HEAD_Z - z0, (0, -WEB_T / 2, z0)) + cyl_x(0, L, HEAD_D, 0, HEAD_Z)
    if pointed:          # pointed nose so a misaligned blade still finds the slot between the lips
        for s in (1, -1):
            r -= section([(-1, 0), (2.5, s * (HEAD_D / 2 + 0.01)), (2.5, s * 4), (-1, s * 4)], "xy", z0 - 1, HEAD_TOP + 1)
    return r


def dove_tab():
    dl, n, w = DOVE
    return section([(0, -n / 2), (dl, -w / 2), (dl, w / 2), (0, n / 2)], "xy", -STRIP_T, 0)


def dove_slot():
    dl, n, w = DOVE
    return section([(-1, -n / 2 - CLR), (dl + CLR, -w / 2 - CLR), (dl + CLR, w / 2 + CLR), (-1, n / 2 + CLR)], "xy", -STRIP_T - 1, 1)


def strip(L, w, male=True, female=True):
    s = box(L, w, STRIP_T, (0, -w / 2, -STRIP_T))
    if male:
        s += dove_tab().translate([L, 0, 0])
    if female:
        s -= dove_slot()
    return s


def rail_segment(L, w=STRIP_W):
    return strip(L, w) + rail(L)


def underside_groove(x0, x1, y_of_x, width=2.4, depth=2.2):
    """Channel in the bottom face (z = -STRIP_T) following the wire line from x0 to x1."""
    y0, y1 = y_of_x(x0), y_of_x(x1)
    return bar((x0, y0), (x1, y1), width, -STRIP_T - 1, -STRIP_T + depth)


# ======================================================================================
# 1. wheel and axle pin
# ======================================================================================
def wheel():
    """Axis along z, faces at z = 0 and 8 (unchanged from version 1)."""
    r_out, w, gr = WHEEL_OD / 2, WHEEL_W, GROOVE_R
    bore = AXLE_D / 2 + CLR
    prof = [(bore, 0), (r_out, 0), (r_out, 1.0), (gr, w / 2 - FLAT / 2), (gr, w / 2 + FLAT / 2), (r_out, w - 1.0), (r_out, w), (bore, w)]
    return CrossSection([prof]).revolve(SEG)


def axle_pin():
    """Along +z: head z -2..0 against the right pannier, shank 28 mm through arm, plate, boss,
    wheel, boss, plate and arm, then a split snap bump 0.7 mm clear of the far face. The plate
    gap is set by the peg shoulders, not by this pin, so the slack does not reach the lips."""
    L = PIN_SPAN
    p = cyl(L + 2.0, AXLE_D) + cyl(2.0, 8.0).translate([0, 0, -2.0])
    p += cyl(1.2, AXLE_D + 0.7).translate([0, 0, L + 0.7])                 # 0.7 clear of the far face: room for five parts' thickness
    p -= box(1.0, AXLE_D + 2, 8.5, (-0.5, -(AXLE_D + 2) / 2, L + 2.0 - 8.5))
    return p


def pin_in_pod(x):
    """Head outside the right (+y) pannier, shank along -y."""
    return axle_pin().rotate([90, 0, 0]).translate([x, ARM_Y1, 0])


# ======================================================================================
# 2. trolley plate
# ======================================================================================
def trolley_plate():
    """Right plate (pod frame): inner face y = 4.5, outer face y = 8. The left plate is the same
    part turned 180 degrees about z. Everything sticks out of the inner face, so it prints flat on
    the outer face and the axle holes come out round."""
    p = box(2 * PL_X, PL_T, PL_ZT - PL_ZB, (-PL_X, Y_IN, PL_ZB))
    for s in (1, -1):                                   # round top corners, r 9
        c = box(10, PL_T + 2, 10, (s * PL_X - (9 if s > 0 else 1), Y_IN - 1, PL_ZT - 9))
        c -= cyl_y(Y_IN - 2, Y_OUT + 2, 18, s * (PL_X - 9), PL_ZT - 9)
        p -= c
    lip_w = Y_IN - SLOT_W / 2
    for x in (-AX_X, AX_X):
        p += box(3.0, lip_w, LIP_TOP - PL_ZB, (x - 1.5, SLOT_W / 2, PL_ZB))    # guide lip under each wheel, short for the tongue kink
        p += cyl_y(Y_IN - BOSS_H, Y_IN + 0.5, BOSS_D, x, 0)                    # thrust boss
        p -= cyl_y(Y_IN - 2, Y_OUT + 2, AXLE_D + 2 * CLR, x, 0)
    p += cyl_y(Y_IN - GAP - 3.0, Y_IN + 0.5, PEG_D, PEG_X, PEG_Z)               # spacer peg: across the gap, 3 mm into the other plate
    p += cyl_y(Y_IN - GAP, Y_IN + 0.5, PEG_SHOULDER_D, PEG_X, PEG_Z)           # shoulder: the other plate's inner face lands on it
    p -= cyl_y(Y_IN - 1, Y_OUT + 1, PEG_D + 2 * CLR, -PEG_X, PEG_Z)             # hole for the other plate's peg
    return p


def plate_in_pod(side):
    return trolley_plate() if side > 0 else trolley_plate().rotate([0, 0, 180])


# ======================================================================================
# 3. pannier
# ======================================================================================
def pannier():
    """Right pannier (pod frame); the left one is the same part turned 180 degrees about z.
    The axle pins pass through the arm and clamp it to the plate. Prints standing on its floor."""
    b = box(2 * BX, BY1 - BY0, BZT - BZB, (-BX, BY0, BZB))
    b -= box(2 * BX - 2 * BWALL, BY1 - BY0 - 2 * BWALL, BZT - BZB, (-BX + BWALL, BY0 + BWALL, BZB + BFLOOR))
    for s in (1, -1):                                   # 3 mm lead-in under both ends of the floor
        b -= section([(s * BX, BZB - 1), (s * (BX - 4.0), BZB - 1), (s * BX, BZB + 3.0)], "xz", BY0 - 1, BY1 + 1)
    # arm, its 45-degree support and the wall that joins it to the basket, as one profile (no coplanar seams)
    arm = section([(ARM_Y0, PL_ZB), (ARM_Y0, ARM_ZT), (ARM_Y1, ARM_ZT), (ARM_Y1, BZT - 0.5), (ARM_Y1 - 3.0, BZT - 0.5), (ARM_Y1 - 3.0, PL_ZB - 3.0)],
                  "yz", -ARM_X, ARM_X)
    for x in (-AX_X, AX_X):
        arm -= tear_y(ARM_Y0 - 1, ARM_Y1 + 1, AXLE_D + 2 * CLR, x, 0)
    return b + arm


def pannier_in_pod(side):
    return pannier() if side > 0 else pannier().rotate([0, 0, 180])


def pod_parts():
    """The assembled wagon in the pod frame, as (name, solid) pairs."""
    w = wheel().rotate([90, 0, 0])                      # faces at y = 0 and -8
    return [("plate R", plate_in_pod(1)), ("plate L", plate_in_pod(-1)),
            ("wheel rear", w.translate([-AX_X, WHEEL_W / 2, 0])), ("wheel front", w.translate([AX_X, WHEEL_W / 2, 0])),
            ("pannier R", pannier_in_pod(1)), ("pannier L", pannier_in_pod(-1)),
            ("pin rear", pin_in_pod(-AX_X)), ("pin front", pin_in_pod(AX_X))]


# ======================================================================================
# 4. turnout plate
# ======================================================================================
def lane_start(k):
    return polar(TONGUE_LEN + 1.0, LANES[k], PIVOT)


def lane_y(k, x):
    sx, sy = lane_start(k)
    return sy + (x - sx) * math.tan(math.radians(LANES[k]))


# ---- rocker frame: x along the axis, y outward (away from the pivot), z up, origin on the axis.
def rk_place(m, tilt=0.0):
    """Rocker-frame solid into the yard, tilted about its axis (tilt > 0 lifts the outer side)."""
    er = polar(R_AX, PHI_M, PIVOT)
    return m.rotate([tilt, 0, 0]).rotate([0, 0, PHI_M - 90]).translate([er[0], er[1], ROCK_Z])


def rk_point(p, tilt=0.0):
    x, y, z = p
    t = math.radians(tilt)
    y, z = y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t)
    b = math.radians(PHI_M - 90)
    X, Y = x * math.cos(b) - y * math.sin(b), x * math.sin(b) + y * math.cos(b)
    er = polar(R_AX, PHI_M, PIVOT)
    return (er[0] + X, er[1] + Y, ROCK_Z + z)


def rk_plan(x, y):
    """Rocker-frame (x, y) on the floor plane, untilted: for things fixed to the plate."""
    X, Y, _ = rk_point((x, y, 0.0))
    return X, Y


def finger_x(phi, y, tilt):
    """Local x that puts a finger at radial offset y on the pivot ray at angle phi when tilted."""
    z = CONTACT_Z - ROCK_Z
    t = math.radians(tilt)
    yp = y * math.cos(t) - z * math.sin(t)
    return -(R_AX + yp) * math.tan(math.radians(phi - PHI_M))


PHI_A = PHI_M - STEP_B / 2         # finger A (outer), engaged at rest
PHI_B = PHI_M + STEP_B / 2         # finger B (inner), engaged when triggered
FA = (finger_x(PHI_A, FING_Y, REST_TILT), FING_Y)
FB = (finger_x(PHI_B, -FING_Y, TRIG_TILT), -FING_Y)


def finger_section(fx, fy, tilt):
    """Plan section of a finger in the rocker frame, with its side faces on pivot rays."""
    z = CONTACT_Z - ROCK_Z
    t = math.radians(tilt)
    pts = []
    for dy, dside in ((-FING_RW / 2, -1), (FING_RW / 2, -1), (FING_RW / 2, 1), (-FING_RW / 2, 1)):
        y = fy + dy
        yp = y * math.cos(t) - z * math.sin(t)
        r = R_AX + yp
        phi_c = PHI_M - math.degrees(math.atan2(fx, R_AX + (fy * math.cos(t) - z * math.sin(t))))
        phi = phi_c + dside * math.degrees(FING_TW / 2 / r)
        pts.append((-(r) * math.tan(math.radians(phi - PHI_M)), y))
    return pts


def a_low_face():
    """Pivot-ray angle of finger A's trailing face at rest: the angle a tooth stops at."""
    return PHI_A - math.degrees(FING_TW / 2 / (R_AX + FING_Y * math.cos(math.radians(REST_TILT)) - (CONTACT_Z - ROCK_Z) * math.sin(math.radians(REST_TILT))))


def tooth_alpha(i):
    """Tongue-frame angle of the leading face of tooth i."""
    return a_low_face() - TEETH_T[i]


def rocker():
    """Rocker frame. Prints upside down on its flat top (z = 6)."""
    b = box(2 * ROCK_X, 18.0, 9.0, (-ROCK_X, -9.0, -3.0))                    # core over the teeth
    b += box(16.0, -ARM_IN - 9.0 + 0.01, 6.0, (-8.0, ARM_IN, 0.0))           # inner arm (trigger-limit stop)
    b += box(16.0, ARM_OUT - 9.0, 6.0, (-8.0, 9.0 - 0.01, 0.0))               # outer arm: thread, rest stop, coin cup
    b += cyl(6.0, CUP_D + 3.2).translate([0, CUP_Y, 0])
    b -= cyl(5.0, CUP_D).translate([0, CUP_Y, 2.0])                            # cup for coins or washers, 15 g
    b -= cyl(10.0, 2.0).translate([0, THREAD_HOLE_Y, -1])
    b -= section(teardrop_pts(3.0 + 2 * CLR, 0.0, 0.0), "yz", -ROCK_X - 1, ROCK_X + 1).rotate([180, 0, 0])   # bore, peak down (up when printed)
    for (fx, fy), tilt in ((FA, REST_TILT), (FB, TRIG_TILT)):
        b += section(finger_section(fx, fy, tilt), "xy", -FING_H, -2.9)
    return b


def rocker_in_yard(tilt):
    return rk_place(rocker(), tilt)


def rocker_pin():
    """3 mm axle for the rocker: head, 40 mm shank, split snap bump. Prints standing on the head."""
    L = 2 * BEAM_X1 + 0.6
    p = cyl(L + 2.0, 3.0) + cyl(2.0, 6.5).translate([0, 0, -2.0])
    p += cyl(1.0, 3.6).translate([0, 0, L + 0.2])
    p -= box(0.8, 5, 6.0, (-0.4, -2.5, L + 2.0 - 6.0))
    return p


def rocker_pin_in_yard():
    return rk_place(rocker_pin().rotate([0, 90, 0]).translate([-BEAM_X1 - 0.3, 0, 0]))


BRIDGE_PEGS = [(sx * 10.0, y) for sx in (1, -1) for y in ((BEAM_Y0 + BEAM_Y0 + 5.0) / 2, BEAM_Y1 - 2.5)]
PEG_H = 3.0


def goalposts():
    """Rocker bridge, a separate part: two beams across the tooth ring carry the rocker pin in open
    notches; their posts stand outside the ring and are joined at floor level by an inner and an
    outer bar, which also carry the two tilt stops. It is lowered over the ring after the tongue is
    on its post and sits on four pegs of the turnout plate. Rocker frame, floor at z = -ROCK_Z."""
    g = None
    for sx in (1, -1):
        x0, x1 = sorted((sx * BEAM_X0, sx * BEAM_X1))
        beam = box(x1 - x0, BEAM_Y1 - BEAM_Y0, BEAM_Z1 - BEAM_Z0, (x0, BEAM_Y0, BEAM_Z0 - ROCK_Z))
        beam += box(x1 - x0, 5.0, BEAM_Z1, (x0, BEAM_Y0, -ROCK_Z))              # inner post
        beam += box(x1 - x0, 5.0, BEAM_Z1, (x0, BEAM_Y1 - 5.0, -ROCK_Z))        # outer post
        beam -= cyl_x(x0 - 1, x1 + 1, 3.0 + 2 * CLR)
        beam -= box(x1 - x0 + 2, 3.2, 5.0, (x0 - 1, -1.6, 0.0))                  # mouth narrower than the hole: no knife edge
        g = beam if g is None else g + beam
    t = math.radians(REST_TILT)
    h_rest = ROCK_Z + (REST_STOP_Y + 2.5) * math.tan(t)                       # arm bottom (z = 0) over the stop's outer edge
    t = math.radians(LIMIT_TILT)
    h_lim = ROCK_Z + max((LIMIT_STOP_Y - 2.5) * math.tan(t), ARM_IN * math.sin(t))   # or the arm's end
    g += box(6.0, REST_STOP_Y + 2.5 - (BEAM_Y1 - 5.0), h_rest, (-3.0, BEAM_Y1 - 5.0, -ROCK_Z))   # from the outer bar
    g += box(6.0, 5.0, h_lim, (-3.0, LIMIT_STOP_Y - 2.5, -ROCK_Z))
    for y0 in (BEAM_Y0, BEAM_Y1 - 5.0):                                       # floor bars, outside the ring
        g += box(2 * BEAM_X1, 5.0, 4.0, (-BEAM_X1, y0, -ROCK_Z))
    for x, y in BRIDGE_PEGS:
        g -= cyl(4.0 + 2, 4.0 + 2 * CLR).translate([x, y, -ROCK_Z - 1])
    return g


def rocker_bridge():
    """Print orientation: floor bars on the bed, beams bridging between the posts."""
    return goalposts().translate([0, 0, ROCK_Z])


def rocker_bridge_in_yard():
    return rk_place(goalposts())


def eyelet(x, y, along="x"):
    e = box(6, 6, 7, (x - 3, y - 3, 0))
    return e - (tear_x(x - 4, x + 4, 2.2, y, 3.5) if along == "x" else tear_y(y - 4, y + 4, 2.2, x, 3.5))


def spring_dir():
    (x0, y0), (x1, y1) = SPRING_ROOT, SPRING_FREE_TIP
    return math.degrees(math.atan2(y1 - y0, x1 - x0)), math.hypot(x1 - x0, y1 - y0)


def spring_socket():
    ang, _ = spring_dir()
    s = box(10, 8, 9, (-6, -4, 0)) - box(10.4, 2.6, 10, (-4.4, -1.3, 1))       # open to the front for the leaf
    return place(s, ang, *SPRING_ROOT)


def turnout_base():
    p = box(PLATE_L, PLATE_Y1 - PLATE_Y0, STRIP_T, (0, PLATE_Y0, -STRIP_T))
    p -= dove_slot()
    p += rail(ENTRY_END)                                                      # entry rail
    p += box(ENTRY_HEAD_END - ENTRY_END + 0.5, WEB_T, HEAD_Z - 21.0, (ENTRY_END - 0.5, -WEB_T / 2, 21.0))   # 12 mm over the tongue's boss: it slides under
    p += cyl_x(ENTRY_END - 0.5, ENTRY_HEAD_END, HEAD_D, 0, HEAD_Z)
    for k, t in LANES.items():                                                 # room for the angled lead strips
        if t:
            ex, ey = PLATE_L, lane_y(k, PLATE_L)
            p -= place(box(40, LEAD_W + 2 * CLR + 2, STRIP_T + 2, (0.0, -(LEAD_W / 2 + CLR + 1), -STRIP_T - 1)), t, ex, ey)
            p += place(box(1.0, DOVE[1], STRIP_T, (-0.5, -DOVE[1] / 2, -STRIP_T)), t, ex, ey)   # ties the tab to the plate
    for k, t in LANES.items():                                                 # exit rails + tabs
        sx, sy = lane_start(k)
        L = (PLATE_L - sx) / math.cos(math.radians(t))
        p += place(rail(L, pointed=True) + dove_tab().translate([L, 0, 0]), t, sx, sy)
    p += cyl(10.0, 6.0).translate([PIVOT[0], PIVOT[1], 0])                    # pivot post
    for s in (1, -1):                                                          # tongue overtravel stops
        a = math.radians(s * (THETA + OVERTRAVEL))
        xt, yt = 90.0, s * (SHOE_W / 2 + 1.5)
        p += cyl(5.0, 3.0).translate([PIVOT[0] + xt * math.cos(a) - yt * math.sin(a), PIVOT[1] + xt * math.sin(a) + yt * math.cos(a), 0])
    for x, y in BRIDGE_PEGS:                                                   # pegs for the separate rocker bridge
        px, py = rk_plan(x, y)
        p += cyl(PEG_H, 4.0).translate([px, py, 0])
    for s in (1, -1):                                                          # gantry posts, snap notches
        y0, y1 = sorted((s * POST_Y[0], s * POST_Y[1]))
        post = box(8, y1 - y0, GANTRY_Z + 5.0, (GANTRY_X - 4, y0, 0))
        post -= cyl_y(y0 - 1, y1 + 1, AXLE_D + 2 * CLR, GANTRY_X, GANTRY_Z)
        post -= box(AXLE_D - 0.4, y1 - y0 + 2, 10, (GANTRY_X - (AXLE_D - 0.4) / 2, y0 - 1, GANTRY_Z))   # 0.2 per side: PLA prongs across their layers
        p += post
    p += spring_socket()
    p -= underside_groove(-1, PLATE_L + 1, wire_y)                             # the wire runs on under the plate
    for x, y in [(12, PLATE_Y1 - 8), (12, PLATE_Y0 + 8), (PLATE_L - 40, PLATE_Y1 - 8), (PLATE_L - 40, PLATE_Y0 + 8)]:
        p -= box(14, 4, STRIP_T + 2, (x - 7, y - 2, -STRIP_T - 1))
    return p


# ======================================================================================
# 5. tongue
# ======================================================================================
def tongue():
    """Tongue frame: pivot at the origin, blade along +x. The ring of four teeth rides on the
    plate beside the blade; the tab on the other side takes the bias spring."""
    t = box(TONGUE_LEN + 5.0, SHOE_W, SHOE_T, (-5.0, -SHOE_W / 2, 0))
    t += rail(TONGUE_LEN - TONGUE_HEAD_START, z0=SHOE_T).translate([TONGUE_HEAD_START, 0, 0])
    t += cyl(TBOSS_H, 2 * TBOSS_R)
    t += box(TAB_X1 - TAB_X0, TAB_Y1 - TAB_Y0, TAB_H, (TAB_X0, TAB_Y0, 0))
    a_hi = max(tooth_alpha(i) for i in range(len(TEETH_T))) + 3.0
    t += sector(RING_R0, RING_R1, -3.0, a_hi, 0, RING_T)
    for i in range(len(TEETH_T)):
        a = tooth_alpha(i)
        t += sector(TOOTH_R0, TOOTH_R1, a - math.degrees(TOOTH_W / ((TOOTH_R0 + TOOTH_R1) / 2)), a, TOOTH_Z0, TOOTH_Z1, n=6)
    t -= cyl(TBOSS_H + 2, 6.0 + 2 * CLR).translate([0, 0, -1])
    return t


def tongue_in_yard(theta):
    return place(tongue(), theta, *PIVOT)


# ======================================================================================
# 6. bias spring (PETG)
# ======================================================================================
def bias_spring(defl_tip=0.0):
    """Leaf, yard frame, deflected toward -y by defl_tip at its tip (0 = as printed)."""
    ang, L = spring_dir()
    n = 24
    xs = np.linspace(0, L, n + 1)
    dy = -defl_tip * (xs / L) ** 2 * (3 - xs / L) / 2
    top = [(x, d + SPRING_T / 2) for x, d in zip(xs, dy)]
    bot = [(x, d - SPRING_T / 2) for x, d in zip(xs, dy)][::-1]
    leaf = section(top + bot, "xy", 1.0, 1.0 + SPRING_H)
    foot = box(4.4 - 2 * CLR, 2.6 - 2 * CLR, 8.0, (-4.4 + CLR, -1.3 + CLR, 1.0))
    return place(foot + leaf + box(2.0, SPRING_T, SPRING_H, (-0.5, -SPRING_T / 2, 1.0)), ang, *SPRING_ROOT)


# ======================================================================================
# 7. gantry axle and flap
# ======================================================================================
def gantry_axle():
    L = POST_Y[1] + 1.0
    a = cyl_y(-L, L, AXLE_D, GANTRY_X, GANTRY_Z)
    return a - box(6, 2 * L + 2, 2, (GANTRY_X - 3, -L - 1, GANTRY_Z - AXLE_D / 2 - 1.5))


def _flap_body():
    """Flap frame: axle along y at the origin. Plate and crank sit on the downstream side and every
    feature reaches x = +4.5, the face it prints on."""
    f = box(9.0, 2 * HUB_Y, 9.0, (-4.5, -HUB_Y, -4.5))
    f += box(2.0, 2 * FLAP_Y, FLAP_LEN, (2.5, -FLAP_Y, -FLAP_LEN))
    crank = box(5.0, CRANK_Y[1] - CRANK_Y[0], CRANK_R + 3.0, (-0.5, CRANK_Y[0], -CRANK_R - 3.0))
    crank -= tear_x(-2, 6, 2.2, (CRANK_Y[0] + CRANK_Y[1]) / 2, -CRANK_R)
    f += crank
    # axle bore along y; teardrop peak toward -x, which is up when printed on the x = +4.5 face
    f -= section([(-q[1], q[0]) for q in teardrop_pts(AXLE_D + 2 * CLR, 0, 0)], "xz", -HUB_Y - 1, HUB_Y + 1)
    return f


def flap(swing=0.0):
    """In the yard; swing in degrees, bottom moving forward (+x)."""
    return _flap_body().rotate([0, -swing, 0]).translate([GANTRY_X, 0, GANTRY_Z])


def crank_hole(swing=0.0):
    s = math.radians(swing)
    x, z = 2.0, -CRANK_R
    return (GANTRY_X + x * math.cos(s) - z * math.sin(s), (CRANK_Y[0] + CRANK_Y[1]) / 2, GANTRY_Z + x * math.sin(s) + z * math.cos(s))


def rocker_hole(tilt):
    return rk_point((0.0, THREAD_HOLE_Y, 6.0), tilt)


# ======================================================================================
# 9. handover
# ======================================================================================
def handover():
    """Handover frame: x = 0 at the nose. The wire lies in a groove on the head for 45 mm (wheel
    height is the same on wire and head), dives through the blade and the strip, and runs on under
    the turnout to the tie-off, so the handover carries almost none of the wire's tension."""
    L = HO_L
    s = box(L, STRIP_W, STRIP_T, (0, -STRIP_W / 2, -STRIP_T)) + dove_tab().translate([L, 0, 0])
    s += box(30, STRIP_W, 10, (-30, -STRIP_W / 2, -STRIP_T))
    r = rail(L, pointed=True) + Manifold.sphere(HEAD_D / 2, SEG).translate([0, 0, HEAD_Z])
    r -= cyl_x(-2, GROOVE_END + 1, WIRE_D + 0.4, 0, WIRE_C)
    a = math.radians(DIVE_ANG)
    Ld = (WIRE_C + STRIP_T + 2) / math.sin(a) + 3
    w = WIRE_D + 0.9
    slot = section([(0, -w / 2), (Ld, -w / 2), (Ld, w / 2), (0, w / 2)], "xz", -3.0, 3.0)
    slot = slot.rotate([0, DIVE_ANG, 0]).translate([GROOVE_END, 0, WIRE_C])
    out = s + r - slot
    xb = _dive_bottom_x()
    out -= underside_groove(xb - 3, L + 13, lambda x: wire_y(x - L))
    return out


def handover_in_yard():
    return handover().translate([-HO_L, 0, 0])


# ======================================================================================
# 10. bays
# ======================================================================================
def lead_rail():
    return rail_segment(230.0, LEAD_W)


def brake_segment():
    """Comb of flexible leaves under the right pannier: tip 13.8 mm above the strip, so each leaf
    is pressed down 1.8 mm by the basket floor (12 mm) as the wagon passes."""
    L = 190.0
    s = rail_segment(L) - box(L + 2, 16, 2.0, (-1, -22, -2.0))              # chain trough under the left basket
    leaf = section([(0, 0), (30, 0), (30, 1.2), (0, 1.2)], "xz", 0, 10.0).rotate([0, -25, 0])
    root = box(3, 10, 3, (-1, 0, 0))
    for i in range(12):                                                        # last tip ends 2 mm inside the segment
        s += (leaf + root).translate([14 + i * 13.3, 4.0, 0])
    return s


def chain_bed():
    """Rail with the chain trough, end to end. The sled stands at its start; the chain lies behind
    the sled in the comb segment's trough, tied to the sled, and is dragged when the basket pushes
    the sled. (Version 1 had a stirrup ring here, which stood in the basket's path.)"""
    L = 190.0
    return rail_segment(L) - box(L + 2, 16, 2.0, (-1, -22, -2.0))        # trough end to end: chain behind, sled and bumper ahead


def sled():
    """Stands in the chain trough; the left basket meets it 8 mm deep. Coins inside set its mass.
    The chain's first link is tied to the hole in its back wall."""
    s = box(20.0, 13.0, 22.0, (0, -6.5, 0)) - box(16.0, 9.0, 21.0, (2.0, -4.5, 2.0))
    return s - tear_x(-1, 3, 2.2, 0, 6.0)


CHAIN_X0 = 16.0 - 1.0 - 146.0      # chain-bed frame: the chain ends 1 mm behind the sled, in the comb's trough


LINK = (20.0, 10.0, 3.0)


def chain_link():
    L, Wd, d = LINK
    o = CrossSection.square([L, Wd], True).offset(Wd / 2 - 0.01, 0).offset(-(Wd / 2 - 0.01), 0)
    i = CrossSection.square([L - 2 * d, Wd - 2 * d], True).offset(1.5, 0).offset(-1.5, 0)
    return (o - i).extrude(d)


def chain(n=11):
    L, Wd, d = LINK
    pitch = L - 2 * d - 0.4
    c = None
    for k in range(n):
        lk = chain_link()
        lk = lk.rotate([90, 0, 0]).translate([0, d / 2, Wd / 2]) if k % 2 else lk.translate([0, 0, Wd / 2 - d / 2])
        lk = lk.translate([k * pitch, 0, 0])
        c = lk if c is None else c + lk
    return c


def bumper():
    """Zig-zag spring at the end of a bay; the rail runs right through to the face plate."""
    L, Wd, H = 64.0, 40.0, 52.0
    z = box(L, Wd, STRIP_T, (0, -Wd / 2, -STRIP_T)) - dove_slot()
    z -= box(24.0 + 1, 16, 2.0, (-1, -22, -2.0))                               # the chain trough continues to the springs
    t = 1.2
    for i in range(6):
        x = 24 + i * 6
        z += box(t, Wd - 6, H, (x, -Wd / 2 + 3, 0))
        if i < 5:
            z += box(6 + t, t, H, (x, (Wd / 2 - 3 - t) if i % 2 == 0 else (-Wd / 2 + 3), 0))
    z += box(4, Wd - 6, H, (60, -Wd / 2 + 3, 0))
    z -= box(L + 10, 5.2, HEAD_Z + 4, (-5, -2.6, 0.0))
    return z + rail(60.0)


# ======================================================================================
# 11. wire ends: window hook, start gate
# ======================================================================================
WEDGE = [(0, 0), (32, 0), (32, 5.4), (0, 1.8)]


def wedge():
    return section(WEDGE, "xy", 0, 22)


POCKET_Z, POCKET_X0, POCKET_L = 6.0, 28.0, 38.0


def window_hook():
    """Hooks over a grill bar or handle up to 24 mm. Three turns of wire round the capstan post,
    then the tail along the floor of the wedge pocket and the wedge pushed in from the open end
    (+x) until it grips, about 8 mm of it still showing. Prints lying on its y = 0 face: the post
    and the pocket both open upward."""
    prof = [(-20, 0), (64, 0), (64, 74), (14, 74), (14, 48), (24, 48), (24, 64), (54, 64), (54, 24), (-20, 24)]
    body = section(prof, "xz", 0, 26)
    body += cyl_y(26, 44, 12, -8, 12)                                     # capstan post on the side face
    rim = CrossSection([[(0, 0), (6.5, 0), (9, 2.5), (9, 4), (0, 4)]]).revolve(SEG)            # 45-degree underside, prints without support
    body += rim.rotate([-90, 0, 0]).translate([-8, 42, 12])                # rim that keeps the turns on
    x0, x1 = POCKET_X0, POCKET_X0 + POCKET_L
    t = 0.1125
    body -= section([(x0, POCKET_Z), (x1 + 2, POCKET_Z), (x1 + 2, POCKET_Z + 1.95 + t * (x1 + 2 - x0)), (x0, POCKET_Z + 1.95)], "xz", 2.0, 30.0)
    return body


GATE_PIN_D = 3.0
GATE_CX = -PL_X - 2.0 - 15.0                     # clamp centre, 2 mm behind the wagon's rear (pod frame x)
GPX, GPZ = 8.0, 12.0                             # lever pivot (gate frame)


KEY_TAPER = 1.5 / 30.0


def wire_clamp_body(L=30.0):
    """Wire along x at y = z = 0. The clamp is lowered onto the wire, which enters through the
    1.9 mm slot in the bottom, so the clamp hangs on the wire by the top of its bore even before
    the key is in. The tapered key slides in beside the wire from the uphill end (-x), so its tail
    points away from the waiting wagon, and presses the wire against the far wall. Fully home the key would leave 0.05 mm, so it grips a 1.4 to 1.6 mm wire with 6 to
    10 mm of key showing."""
    b = box(L, 14, 16, (-L / 2, -7, -8))
    b -= cyl_x(-L / 2 - 1, L / 2 + 1, WIRE_D + 0.4)
    b -= box(L + 2, WIRE_D + 0.4, 10, (-L / 2 - 1, -(WIRE_D + 0.4) / 2, -10))       # slot opens downward
    y0 = -(WIRE_D + 0.4) / 2
    wall = lambda x: y0 + 1.0 + 1.6 + KEY_TAPER * (L / 2 - x)               # wide at -x: the key goes in from uphill, its tail away from the wagon
    b -= section([(-L / 2 - 1, y0), (L / 2 + 1, y0), (L / 2 + 1, wall(L / 2 + 1)), (-L / 2 - 1, wall(-L / 2 - 1))], "xy", -3.3 - CLR, 3.3 + CLR)
    return b


def start_gate():
    """Gate frame: the wire along x at y = z = 0. Clamped on the wire uphill of the wagon; the hook
    lever pivots on two lugs on top."""
    b = wire_clamp_body(30.0)
    for s in (1, -1):
        b += box(8, 2.6, 9, (GPX - 4, (2.5 if s > 0 else -5.1), 8.0))
    return b - tear_y(-7, 7, GATE_PIN_D + 2 * CLR, GPX, GPZ)


def gate_lever():
    """Gate frame. Rises over the wagon's rear and drops between the plates in front of the rear
    spacer peg; a ramp on the hook lets the peg push it up when the wagon is pushed back to latch."""
    peg_x = -PEG_X - GATE_CX
    peg_z = PEG_Z + R_WIRE
    top = peg_z + PEG_D / 2 + 7.0
    wy = 4.6
    hub = cyl_y(-wy / 2, wy / 2, 7.0, GPX, GPZ)
    arm = section([(GPX - 2, GPZ), (GPX + 2, GPZ), (GPX + 8, top - 2), (GPX + 4, top + 2)], "xz", -wy / 2, wy / 2)
    arm += box(peg_x + PEG_SHOULDER_D / 2 + 4.6 - (GPX + 4), wy, 4.0, (GPX + 4, -wy / 2, top - 2))
    hx0 = peg_x + PEG_SHOULDER_D / 2 + 0.6
    hook = section([(hx0, peg_z - 2.0), (hx0 + 4.0 - 2.0, peg_z - 2.0), (hx0 + 4.0, peg_z), (hx0 + 4.0, top + 2), (hx0, top + 2)], "xz", -wy / 2, wy / 2)
    lv = hub + arm + hook
    lv -= tear_y(-wy, wy, GATE_PIN_D + 2 * CLR, GPX, GPZ)
    lv -= cyl(10, 2.0).translate([GPX + 14, 0, top - 5])
    return lv


def gate_in_pod():
    return start_gate().translate([GATE_CX, 0, -R_WIRE]), gate_lever().translate([GATE_CX, 0, -R_WIRE])


def gate_key():
    return section([(0, 0), (30, 0), (30, 3.1), (0, 1.6)], "xy", 0, 6.6)


def gate_pin():
    return cyl(24, 3.0) + cyl(2, 6).translate([0, 0, -2])


# ======================================================================================
# 12. fit coupon
# ======================================================================================
COUPON_CLR = (0.15, 0.20, 0.25, 0.30, 0.35, 0.40)


def fit_coupon():
    c = box(118, 36, 3, (0, 0, -3)) + cyl(12.0, 6.0).translate([12, 10, 0]) + cyl(12.0, 4.0).translate([12, 26, 0])
    for i, k in enumerate(COUPON_CLR):
        x = 34 + i * 15
        c += cyl(6.0, 12.0).translate([x, 10, 0]) - cyl(8, 6.0 + 2 * k).translate([x, 10, -1])
        c += cyl(6.0, 9.0).translate([x, 26, 0]) - cyl(8, 4.0 + 2 * k).translate([x, 26, -1])
        for n in range(i + 1):
            c -= box(1.0, 2.0, 2.0, (x - 0.5 + (n - i / 2) * 1.8, 15.0, 4.5))
    return c


# ======================================================================================
# build: every part in its print orientation
# ======================================================================================
def _lay(m):
    b = m.bounding_box()
    return m.translate([-b[0], -b[1], -b[2]])


def _spring_flat():
    ang, _ = spring_dir()
    return bias_spring().translate([-SPRING_ROOT[0], -SPRING_ROOT[1], 0]).rotate([0, 0, -ang])


# file, qty, material, colour, solid in print orientation, note
PARTS = [
    ("fit_coupon_x1", 1, "PETG", "Orange", lambda: fit_coupon(), "print first: posts and bored rings at 0.15 to 0.40 mm per side"),
    ("wheel_x6", 6, "PLA", "Cobalt Blue", lambda: wheel(), "V-groove wheel; rides the wire and the rail head"),
    ("axle_pin_x6", 6, "PETG", "Orange", lambda: axle_pin(), "4 mm pin through pannier, plate, wheel, plate, pannier; snap bump"),
    ("trolley_plate_x6", 6, "PLA", "Cobalt Blue", lambda: trolley_plate().rotate([-90, 0, 0]), "two identical plates per wagon; prints flat, peg up"),
    ("pannier_x6", 6, "PLA", "Cobalt Blue", lambda: pannier(), "basket; two identical per wagon, clamped by the axle pins"),
    ("turnout_base_x1", 1, "PLA", "Light Grey", lambda: turnout_base(), "plate, entry and exit rails, pivot, stops, rocker bridges, gantry posts"),
    ("tongue_x1", 1, "PLA", "Orange", lambda: tongue(), "switch blade with the ring of four teeth"),
    ("rocker_bridge_x1", 1, "PLA", "Light Grey", lambda: rocker_bridge(), "two beams over the tooth ring; carries the rocker pin and the tilt stops; sits on four pegs"),
    ("rocker_x1", 1, "PLA", "Orange", lambda: rocker().rotate([180, 0, 0]), "escapement rocker; prints upside down"),
    ("rocker_pin_x1", 1, "PETG", "Orange", lambda: rocker_pin(), "3 mm rocker axle with snap bump"),
    ("bias_spring_x1", 1, "PETG", "Orange", _spring_flat, "leaf spring that pushes the tongue toward the next lane"),
    ("flap_x1", 1, "PLA", "Orange", lambda: _flap_body().rotate([0, 90, 0]), "trigger flap with crank; prints on its downstream face"),
    ("gantry_axle_x1", 1, "PETG", "Orange", lambda: gantry_axle(), "4 mm flap axle, prints on its flat"),
    ("handover_x1", 1, "PLA", "Light Grey", lambda: handover(), "wire-to-rail handover; the wire dives through it"),
    ("window_hook_x1", 1, "PETG", "Orange", lambda: window_hook().rotate([90, 0, 0]), "top anchor: capstan post and wedge pocket"),
    ("wedge_x1", 1, "PETG", "Orange", lambda: wedge(), "pinches the wire in the window hook"),
    ("lead_rail_230_x3", 3, "PLA", "Light Grey", lambda: lead_rail(), "first bay segment, narrow strip"),
    ("brake_comb_190_x3", 3, "PLA", "Light Grey", lambda: brake_segment(), "rail with 12 leaves under the right basket and the chain trough under the left"),
    ("chain_bed_190_x3", 3, "PLA", "Light Grey", lambda: chain_bed(), "rail with the chain trough, end to end; the sled starts here"),
    ("chain_11_links_x3", 3, "PLA", "Light Grey", lambda: chain(), "print-in-place drag chain"),
    ("sled_x3", 3, "PLA", "Light Grey", lambda: sled(), "pushed by the left basket; drags the chain tied to its back"),
    ("bumper_x3", 3, "PETG", "Orange", lambda: bumper(), "zig-zag spring at the end of each bay"),
    ("start_gate_x1", 1, "PLA", "Light Grey", lambda: start_gate(), "clamps on the wire behind the waiting wagon"),
    ("gate_lever_x1", 1, "PLA", "Light Grey", lambda: gate_lever().rotate([90, 0, 0]), "hook over the wagon's rear spacer peg"),
    ("gate_key_x1", 1, "PETG", "Orange", lambda: gate_key(), "tapered key that locks the gate on the wire"),
    ("gate_pin_x1", 1, "PETG", "Orange", lambda: gate_pin(), "lever pivot pin"),
]


def build(only=None):
    import shutil
    OUT.mkdir(exist_ok=True)
    rows = []
    for name, qty, mat, col, fn, note in PARTS:
        if only and name not in only:
            continue
        m = _lay(fn())
        want = 11 if name.startswith("chain_11") else 1                      # the chain is 11 loose links, printed in place
        assert len(m.decompose()) == want, f"{name}: {len(m.decompose())} pieces, expected {want}"
        mm = m.to_mesh()
        tm = trimesh.Trimesh(vertices=np.asarray(mm.vert_properties)[:, :3], faces=np.asarray(mm.tri_verts), process=True)
        assert tm.is_watertight, name
        assert max(tm.extents[:2]) <= BED and tm.extents[2] <= BED, f"{name} {tm.extents} does not fit the bed"
        tm.export(OUT / f"{name}.stl")
        rows.append(dict(file=f"{name}.stl", qty=qty, material=mat, colour=col, grams_each=round(m.volume() / 1000 * (1.24 if mat == "PLA" else 1.27) * 0.5),
                         x_mm=round(tm.extents[0], 1), y_mm=round(tm.extents[1], 1), z_mm=round(tm.extents[2], 1), note=note))
        print(f"{name:22s} x{qty} {mat:4s} {col:11s} {np.round(tm.extents, 1)}")
    if not only:
        keep = {f"{n}.stl" for n, *_ in PARTS}
        for f in OUT.glob("*.stl"):
            if f.name not in keep:
                f.unlink()
                print("removed", f.name)
        with open(HERE / "parts.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        preview(rows)


def preview(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    cols = 6
    nrow = math.ceil(len(rows) / cols)
    fig = plt.figure(figsize=(16, 2.9 * nrow))
    for i, r in enumerate(rows):
        tm = trimesh.load(OUT / r["file"])
        ax = fig.add_subplot(nrow, cols, i + 1, projection="3d")
        v = tm.vertices - tm.bounds.mean(axis=0)
        shade = np.clip(0.35 + 0.65 * np.abs(tm.face_normals @ np.array([0.4, -0.5, 0.75])), 0, 1)
        ax.add_collection3d(Poly3DCollection(v[tm.faces], facecolors=[(0.17 * s + 0.1, 0.39 * s + 0.1, 0.56 * s + 0.1) for s in shade], edgecolor="none"))
        rr = np.abs(v).max()
        ax.set_xlim(-rr, rr); ax.set_ylim(-rr, rr); ax.set_zlim(-rr, rr)
        ax.set_box_aspect([1, 1, 1])
        ax.view_init(26, -58)
        ax.set_axis_off()
        ax.set_title(f"{r['file'][:-4]}\n{r['x_mm']:.0f}×{r['y_mm']:.0f}×{r['z_mm']:.0f} mm, {r['material']}", fontsize=8)
    fig.suptitle("PLE-SBS scale model, phase 1 version 2: parts as they sit on the P1S bed", fontsize=12)
    fig.tight_layout()
    fig.savefig(HERE / "parts_preview.png", dpi=120)
    plt.close(fig)
    print("wrote parts_preview.png")


if __name__ == "__main__":
    import sys
    build([a for a in sys.argv[1:]] or None)
