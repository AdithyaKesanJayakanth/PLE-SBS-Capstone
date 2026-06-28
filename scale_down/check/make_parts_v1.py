"""PLE-SBS print-only scale model: every part as a watertight STL for a Bambu Lab P1S.

The only thing bought is 1.5 mm stainless wire rope. No bearings, screws, magnets or
glue: wheels run on printed pins, the brake is a comb of printed springs, the chain bed
is a print-in-place chain, the self-indexing points are a printed cam driven by a
star that each passing pod pushes.

Run:  .venv/bin/python scale_down/make_parts.py     -> scale_down/stl/*.stl, parts_preview.png, parts.csv

All dimensions in mm. Coordinate conventions:
  yard parts:  x along the pod's direction of travel, y across, z up, z = 0 at the top
               of the rail base strip (the floor is at z = -4).
  pod parts:   x along the wire, y across, z up, z = 0 at the bottom of the trolley hooks.
"""
import csv
import math
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold

OUT = Path(__file__).resolve().parent / "stl"
OUT.mkdir(exist_ok=True)
SEG = 64

# ---- shared parameters -------------------------------------------------------------
WIRE_D = 1.5
BED = 250.0                 # usable bed (P1S is 256)
# rail (monorail blade with a round head)
WEB_T, WEB_H = 2.0, 46.0    # blade thickness and height above the strip
HEAD_D = 3.5                # round head
HEAD_Z = WEB_H + HEAD_D / 2 # head centre above the strip (= 47.75)
STRIP_T = 4.0
STRIP_W = 40.0
LEAD_W = 22.0               # narrow strip where the three lanes are still close together
DOVE = (12.0, 10.0, 14.0)   # dovetail: length, narrow width, wide width
CLR = 0.2                   # running clearance per side (print the fit test; 0.15 to 0.3 is the usual range)
# pod
WHEEL_OD, WHEEL_W, GROOVE_R = 24.0, 8.0, 9.0
AXLE_D = 4.0
AXLE_PITCH = 40.0
BODY_L, BODY_W = 64.0, 16.0  # trolley: two plates 3.5 mm thick, 9 mm wheel gap
PLATE_T = (BODY_W - 9.0) / 2
W_Z = 10.0                  # wire centre in pod coordinates
AXLE_Z = W_Z + WIRE_D / 2 + GROOVE_R  # 19.75
HOOK_TOP = 7.5              # hooks reach 1.75 mm under the wire; a 3.2 mm slot lets the rail web through
SLOT_W = 3.2
PAN = (60.0, 26.0, 30.0)    # pannier (basket half): x, y, z
PAN_BOT = -38.0             # pannier bottom, pod coordinates (= 12 mm above the strip)
# turnout
TONGUE_X0, TONGUE_L = 40.0, 130.0
TIP_OFF = 13.5              # tongue-tip offset for the outer lanes
LANE_ANG = math.degrees(math.atan2(TIP_OFF, TONGUE_L))   # 5.93 degrees
CAM_X, CAM_Y = 120.0, 52.0  # cam/star shaft: outside the sweep of the panniers (y <= 46)
STRIKE_X = 240.0            # the star's cross-bar waits here, across all three lanes
STAR_STEP = 90.0            # four arms, four cam dwells: bay 1, 2, 3, 2, 1 ...
PLATE = (236.0, -70.0, 110.0)   # length, y from, y to (+12 mm dovetail tabs = 248 mm)


def tongue_y(x):
    """Lateral position of the tongue centre-line at plate x, for the three tip settings."""
    f = (x - TONGUE_X0) / TONGUE_L
    return [TIP_OFF * f, 0.0, -TIP_OFF * f]


CAM_R = tuple(CAM_Y - 4.0 - yt for yt in tongue_y(CAM_X))   # follower boss (r 4) touches the rim: bay 1, 2, 3


# ---- helpers -------------------------------------------------------------------------
def cyl(h, d, center=False):
    return Manifold.cylinder(h, d / 2, d / 2, SEG, center)


def box(x, y, z, center=False):
    return Manifold.cube([x, y, z], center)


def poly(pts):
    """Counter-clockwise polygon as a CrossSection."""
    a = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        a += x0 * y1 - x1 * y0
    if a < 0:
        pts = pts[::-1]
    return CrossSection([pts])


def prism(pts, h):
    return poly(pts).extrude(h)


def rot(m, ax, deg):
    return m.rotate([deg if ax == "x" else 0, deg if ax == "y" else 0, deg if ax == "z" else 0])


def save(part, name, qty, material, note):
    mesh = part.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=True)
    assert tm.is_watertight, name
    assert max(tm.extents) <= BED + 0.01, f"{name} is {tm.extents} mm, too big for the bed"
    tm.export(OUT / f"{name}.stl")
    cm3 = part.volume() / 1000
    grams = cm3 * 1.24 * 0.45   # PLA, about 45 % of solid volume once walls and infill are set
    PARTS.append(dict(name=name, qty=qty, material=material, grams=round(grams), mm=tuple(np.round(tm.extents, 1)), note=note, mesh=tm))
    print(f"{name:28s} x{qty:<2d} {material:5s} {grams:4.0f} g  {np.round(tm.extents, 1)}")
    return tm


PARTS = []


# ---- rail pieces ------------------------------------------------------------------
def rail(L):
    """Blade rail with a round head, L long along +x, standing on z = 0."""
    web = box(L, WEB_T, WEB_H + HEAD_D / 2).translate([0, -WEB_T / 2, 0])
    head = rot(cyl(L, HEAD_D), "y", 90).translate([0, 0, HEAD_Z])
    return web + head


def strip(L, w, male=True, female=True):
    """Base strip with a dovetail tab on the +x end and a matching slot on the -x end."""
    s = box(L, w, STRIP_T).translate([0, -w / 2, -STRIP_T])
    dl, n, wdt = DOVE
    tab = prism([(0, -n / 2), (dl, -wdt / 2), (dl, wdt / 2), (0, n / 2)], STRIP_T).translate([L, 0, -STRIP_T])
    slot = prism([(-1, -n / 2 - CLR), (dl + CLR, -wdt / 2 - CLR), (dl + CLR, wdt / 2 + CLR), (-1, n / 2 + CLR)], STRIP_T + 2).translate([0, 0, -STRIP_T - 1])
    if male:
        s += tab
    if female:
        s -= slot
    return s


def rail_segment(L, w=STRIP_W):
    return strip(L, w) + rail(L)


# ---- 1. wheel and axle pin ---------------------------------------------------------
def wheel():
    r_out, w, gr = WHEEL_OD / 2, WHEEL_W, GROOVE_R
    flat = 1.2                       # flat at the groove bottom (wire 1.5, rail head 3.5 sits higher in the V)
    bore = AXLE_D / 2 + CLR
    prof = [(bore, 0), (r_out, 0), (r_out, 1.0), (gr, w / 2 - flat / 2), (gr, w / 2 + flat / 2), (r_out, w - 1.0), (r_out, w), (bore, w)]
    return CrossSection([prof]).revolve(SEG)


def axle_pin():
    """4 mm pin with a head; the far end is split so it snaps through the second plate."""
    L = BODY_W + 2.0
    pin = cyl(L, AXLE_D) + cyl(2.0, 8.0).translate([0, 0, -2.0])
    pin += cyl(1.2, AXLE_D + 0.8).translate([0, 0, L - 0.4])          # retaining bump
    pin -= box(1.0, AXLE_D + 2, 7.0, center=True).translate([0, 0, L - 2.5])  # split
    return pin


# ---- 2. trolley plate (two identical plates make one trolley) ----------------------
def trolley_plate():
    """Side plate with wheel-axle holes, the under-wire hook lips, a top bridge peg and
    hole, and a dovetail on the outer face for the pannier arm."""
    H = AXLE_Z + WHEEL_OD / 2 + 8   # 39.75
    p = box(BODY_L, PLATE_T, H).translate([-BODY_L / 2, 0, 0])
    # round the top corners
    p -= (box(10, PLATE_T + 2, 10).translate([-BODY_L / 2 - 1, -1, H - 9]) - rot(cyl(PLATE_T + 2, 18), "x", -90).translate([-BODY_L / 2 + 9, -1, H - 9]))
    p -= (box(10, PLATE_T + 2, 10).translate([BODY_L / 2 - 9, -1, H - 9]) - rot(cyl(PLATE_T + 2, 18), "x", -90).translate([BODY_L / 2 - 9, -1, H - 9]))
    # hook lips: from the plate's inner face (y = 0) inward to the slot edge, under each wheel
    lip = (9.0 - SLOT_W) / 2
    for x in (-AXLE_PITCH / 2, AXLE_PITCH / 2):
        p += box(7.0, lip, HOOK_TOP).translate([x - 3.5, -lip, 0])
    # axle holes
    for x in (-AXLE_PITCH / 2, AXLE_PITCH / 2):
        p -= rot(cyl(PLATE_T + 2, AXLE_D + 2 * CLR), "x", -90).translate([x, -1, AXLE_Z])
    # bridge: a peg on one end and a hole on the other, so two identical plates mate
    bridge_z = H - 4
    p += box(6, 4.5 - CLR, 6).translate([18, -4.5 + CLR, bridge_z - 3])            # peg reaches the mid-plane
    p += rot(cyl(4.5 + 3.5, 3.0), "x", 90).translate([18, 0, bridge_z])             # locating pin reaches into the other plate's hole
    p -= rot(cyl(PLATE_T + 2, 3.0 + 2 * CLR), "x", -90).translate([-18, -1, bridge_z])
    p += box(6, 4.5 - CLR, 6).translate([-21, -4.5 + CLR, bridge_z - 3])
    # dovetail on the outer face for the pannier arm (vertical, open at the bottom)
    p += prism([(-5, PLATE_T), (5, PLATE_T), (7, PLATE_T + 3), (-7, PLATE_T + 3)], 14).translate([0, 0, 0])
    # strike pad on top for the indexing star (nothing to add: the bridge is the strike face)
    return p


# ---- 3. pannier: basket half with its arm and dovetail socket ----------------------
def pannier(left=False):
    X, Y, Z = PAN
    y0 = BODY_W / 2 + 1.0           # inner face 1 mm off the plate
    b = box(X, Y, Z).translate([-X / 2, y0, PAN_BOT])
    b -= box(X - 3.2, Y - 3.2, Z).translate([-X / 2 + 1.6, y0 + 1.6, PAN_BOT + 2.4])
    # arm up to the plate and the dovetail socket
    sock = prism([(-5 - CLR, -1), (5 + CLR, -1), (7 + CLR, 3 + CLR), (-7 - CLR, 3 + CLR)], 15).translate([0, BODY_W / 2 + PLATE_T - 0.0, -14.5])
    arm = box(18, 7.0, 14).translate([-9, BODY_W / 2 + PLATE_T - 0.5, -14]) - sock
    # the arm hangs down to the pannier top
    neck = box(18, 4.0, -PAN_BOT - Z + 2).translate([-9, y0 - 2.0, PAN_BOT + Z - 2])
    b += arm + neck
    # chain hook under the front of the LEFT pannier; the RIGHT one rides the brake comb
    if left:
        b += box(3, 8, 9).translate([X / 2 - 3, y0 + 4, PAN_BOT - 7])
        b += box(6, 8, 3).translate([X / 2 - 6, y0 + 4, PAN_BOT - 7])
    if left:
        b = b.mirror([0, 1, 0])
    return b


# ---- 4. turnout base plate with entry rail, three exit rails, posts ----------------
def turnout_base():
    L, y0, y1 = PLATE
    Wd = y1 - y0
    p = box(L, Wd, STRIP_T).translate([0, y0, -STRIP_T])
    dl, n, wdt = DOVE
    p -= prism([(-1, -n / 2 - CLR), (dl + CLR, -wdt / 2 - CLR), (dl + CLR, wdt / 2 + CLR), (-1, n / 2 + CLR)], STRIP_T + 2).translate([0, 0, -STRIP_T - 1])
    p += rail(TONGUE_X0 - 6.0)                                   # entry rail, 6 mm short of the pivot
    x_exit = TONGUE_X0 + TONGUE_L + 2.0
    for k in (-1, 0, 1):
        ex = rail(L - x_exit) + prism([(0, -n / 2), (dl, -wdt / 2), (dl, wdt / 2), (0, n / 2)], STRIP_T).translate([L - x_exit, 0, -STRIP_T])
        p += rot(ex, "z", k * LANE_ANG).translate([x_exit, k * TIP_OFF, 0])
    # tongue pivot post (the tongue's root boss drops over it)
    p += cyl(10.0, 6.0).translate([TONGUE_X0, 0, 0])
    # cam/star post: 4 mm boss, 6 mm pin
    p += cyl(4.0, 14.0).translate([CAM_X, CAM_Y, 0]) + cyl(18.0, 6.0).translate([CAM_X, CAM_Y, 0])
    # tongue leaf spring: cantilever along x at y = -20, pushes the tongue's pad toward the cam
    p += box(6, 12, 10).translate([48, -26, 0])
    p += box(70, 1.2, 10).translate([54, -20.6, 0])
    p += cyl(10, 3.0).translate([123, -20, 0])                  # rounded tip
    # detent: post and finger pressing on the notched ring under the star hub
    post = box(8, 8, 60).translate([-4, -4, 0])
    finger = box(21, 1.0, 6).translate([2, -0.5, 54]) + cyl(6, 2.4).translate([22, 0, 54])   # rooted 2 mm inside the post
    d = math.degrees(math.atan2(CAM_Y - 76, CAM_X - 140))
    p += rot(post + finger, "z", d).translate([140, 76, 0])
    # tie-down slots at the corners
    for x, y in [(12, y1 - 12), (12, y0 + 12), (L - 12, y1 - 12), (L - 12, y0 + 12)]:
        p -= box(16, 5, STRIP_T + 2, center=True).translate([x, y, -STRIP_T / 2])
    return p


# ---- 5. tongue (the switch blade) ---------------------------------------------------
def tongue():
    t = rail(TONGUE_L - 4.0).translate([4.0, 0, 0])
    t += cyl(10.0, 12.0) - cyl(12, 6.0 + 2 * CLR).translate([0, 0, -1])   # root boss on the pivot post
    t += box(6, 6, 10).translate([3, -3, 0])                                  # joins boss and blade
    xf = CAM_X - TONGUE_X0
    t += cyl(8.0, 8.0).translate([xf, 0, 2.0])                                # follower boss: rides the cam rim (+y side)
    t += box(10, 6, 10).translate([xf - 5, -6, 0])                            # pad the leaf spring pushes on (-y side)
    return t


# ---- 6. indexer: 3-step cam + detent ring + shaft + star hub -----------------------
def cam_profile(n=240):
    """Four 90-degree sectors. The follower sits at 270 degrees (toward the tongue); the star
    turns counter-clockwise 90 degrees per pod, so the sectors read bay 1, 2, 3, 2 going
    clockwise from 270."""
    seq = [CAM_R[0], CAM_R[1], CAM_R[2], CAM_R[1]]     # at 270, 180, 90, 0 degrees
    pts = []
    for i in range(n):
        a = 360.0 * i / n
        u = (270.0 - a) % 360.0            # clockwise distance from the follower direction
        k = int(u // 90.0)
        s_ = u % 90.0
        r0, r1 = seq[k], seq[(k + 1) % 4]
        if s_ < 80:
            r = r0
        else:
            f = (s_ - 80) / 10.0
            r = r0 + (r1 - r0) * (0.5 - 0.5 * math.cos(math.pi * f))
        pts.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
    return pts


STRIKE_ANG = math.degrees(math.atan2(-21.0 - CAM_Y, STRIKE_X - CAM_X))   # arm angle when its bar waits across the lanes


def indexer():
    cam = prism(cam_profile(), 6.0).translate([0, 0, 4.0])      # z 4..10, sits on the boss; panniers pass 2 mm above
    shaft = cyl(50.0, 8.0).translate([0, 0, 10.0])
    ring = cyl(6.0, 24.0).translate([0, 0, 54.0])
    for k in range(4):
        a = math.radians(230 + 90 * k)   # the finger comes in at 230 degrees
        ring -= cyl(8, 3.2).translate([12.0 * math.cos(a), 12.0 * math.sin(a), 53.0])
    hub = cyl(14.0, 30.0).translate([0, 0, 60.0])
    for k in range(4):
        hub -= rot(box(20, 8.0 + 2 * CLR, 8.0 + 2 * CLR).translate([8, -4.0 - CLR, -4.0 - CLR]), "z", 90 * k).translate([0, 0, 67.0])   # 8 mm arm, CLR per side
    part = cam + shaft + ring + hub
    part -= cyl(30, 6.0 + 2 * CLR).translate([0, 0, -1])
    return part


def star_arm():
    """L-shaped arm: a leg from the hub socket to x = STRIKE_X, then a cross-bar hanging
    across the three lanes. The passing trolley's top strikes the bar and turns the star."""
    leg_len = STRIKE_X - CAM_X + 4.0 + 3.0          # from 3 mm inside the socket to 4 mm past the bar centre
    leg = box(leg_len, 8.0, 8.0).translate([-3.0 + 15.0 - 18.0, -4, 0])   # starts 18 mm inside the hub (socket depth)
    leg = box(leg_len + 15.0, 8.0, 8.0).translate([-15.0, -4, 0])
    bar_y0, bar_y1 = -21.0 - CAM_Y - 9.0, 4.0          # from 9 mm beyond lane 3 up to the leg
    bar = box(8.0, bar_y1 - bar_y0, 15.0).translate([STRIKE_X - CAM_X - 4.0, bar_y0, 0])
    return leg + bar


# ---- 7. handover module: wire-to-rail ramp with the wedge cleat ---------------------
def handover():
    L = 170.0
    rise = 14.0
    s = strip(L, STRIP_W, male=True, female=False)
    s += box(40, STRIP_W, 10).translate([-40, -STRIP_W / 2, -STRIP_T])        # nose block the wire comes over
    # ramp rail: head descends from HEAD_Z + rise at x = 0 to HEAD_Z at x = 110, then level
    pieces = []
    n = 11
    for i in range(n):
        x0 = 110.0 * i / n
        x1 = 110.0 * (i + 1) / n
        z0 = rise * (1 - i / n)
        z1 = rise * (1 - (i + 1) / n)
        seg = rail(math.hypot(x1 - x0, z1 - z0) + 1.0)
        ang = math.degrees(math.atan2(z1 - z0, x1 - x0))
        pieces.append(rot(seg, "y", -ang).translate([x0, 0, z0]))
    r = pieces[0]
    for pc in pieces[1:]:
        r += pc
    r += rail(L - 110).translate([110, 0, 0])
    # under-rail filler so the sloped blade is supported (printed solid)
    r += prism([(0, 0), (112, 0), (112, 0.1), (0, rise)], WEB_T).translate([0, -WEB_T / 2, 0])
    # the wire lies in a groove along the top of the head for the first 45 mm, then dives
    groove = rot(cyl(46, WIRE_D + 0.4), "y", 90).translate([0, 0, HEAD_Z + HEAD_D / 2 + rise - 0.4])
    groove = rot(groove, "y", -math.degrees(math.atan2(rise, 110)))
    r -= groove
    r -= rot(cyl(40, WIRE_D + 0.8), "y", 90 + 55).translate([44, 0, HEAD_Z + rise - 4])   # dive hole
    # wedge cleat block beside the rail at x = 30..80, y = 6..30
    cleat = box(50, 26, 22).translate([30, 5, 0])
    cleat -= prism([(0, 0), (34, 0), (34, 6), (0, 2.2)], 24).translate([38, 9, -1])      # tapered wedge pocket, wire runs along it
    cleat -= box(60, 2.0, 24).translate([25, 10.5, -1])                                    # wire channel into the pocket
    # tie-down loop at the rear
    loop = (box(30, 20, 10) - box(20, 8, 12).translate([5, 6, -1])).translate([L - 20, -10, 0])
    return s + r + cleat + loop


def wedge():
    return prism([(0, 0), (32, 0), (32, 5.4), (0, 1.8)], 22)


def window_hook():
    """Hooks over a grill bar or handle up to 24 mm: body with a capstan post (wrap the wire
    three turns) and a wedge pocket; an inverted U above."""
    prof = [(0, 0), (56, 0), (56, 74), (6, 74), (6, 48), (16, 48), (16, 64), (46, 64), (46, 24), (0, 24)]
    body = rot(prism(prof, 24), "x", 90).translate([0, 24, 0])      # profile in x-z, 24 thick in y
    body += cyl(20, 12).translate([16, 12, 24])                      # capstan post on the body top
    body -= prism([(0, 0), (34, 0), (34, 6), (0, 2.2)], 24).translate([20, 9, -1])   # wedge pocket along x
    body -= box(60, 2.0, 26).translate([-5, 10.5, -1])                               # wire channel into the pocket
    return body


# ---- 8. bay pieces ------------------------------------------------------------------
def lead_rail():
    return rail_segment(230.0, LEAD_W)


def brake_segment():
    L = 190.0
    s = rail_segment(L)
    # comb of flexible teeth under the right-hand pannier (y = 9..19 in pod terms)
    tooth = prism([(0, 0), (30, 0), (30, 1.2), (0, 1.2)], 10.0)    # 30 long, 1.2 thick, 10 wide
    tooth = rot(tooth, "y", -25).translate([0, 0, 0])              # tip rises 12.7 mm: above the pannier bottom (12)
    root = box(3, 10, 3).translate([-1, 0, 0])
    for i in range(12):
        s += (tooth + root).translate([10 + i * 15, 8.0, 0])
    return s


def chain_bed():
    L = 190.0
    s = rail_segment(L)
    s -= box(L - 20, 16, 2.0).translate([10, -22, -2.0])            # trough for the chain (links 10 wide)
    # stirrup: a standing ring the pod's hook passes through, at x = 12; the chain's first link ties to it
    ring = box(2.5, 14, 15).translate([12, -21, -2]) - box(4, 10, 8).translate([11, -19, 2])
    s += ring
    return s


LINK = (20.0, 10.0, 3.0)   # outside length, outside width, wire

def chain_link():
    L, Wd, d = LINK
    o = CrossSection.square([L, Wd], True).offset(Wd / 2 - 0.01, 0).offset(-(Wd / 2 - 0.01), 0)
    i = CrossSection.square([L - 2 * d, Wd - 2 * d], True).offset(1.5, 0).offset(-1.5, 0)
    return (o - i).extrude(d)


def chain(n=11):
    """Print-in-place chain: links alternate flat and upright, 0.45 mm apart."""
    L, Wd, d = LINK
    pitch = L - 2 * d - 0.4           # print-in-place links need 0.4 mm, more than the 0.2 running fits
    c = None
    for k in range(n):
        lk = chain_link()
        lk = rot(lk, "x", 90).translate([0, d / 2, Wd / 2]) if k % 2 else lk.translate([0, 0, Wd / 2 - d / 2])   # upright links stand on the bed; flat ones bridge
        lk = lk.translate([k * pitch, 0, 0])
        c = lk if c is None else c + lk
    return c


def bumper():
    """Zig-zag printed spring at the end of a bay, straddling the rail."""
    L, Wd, H = 60.0, 40.0, 52.0
    s = strip(16, STRIP_W, male=False, female=True)
    s = box(16, Wd, STRIP_T).translate([0, -Wd / 2, -STRIP_T]) - prism([(-1, -DOVE[1] / 2 - CLR), (DOVE[0] + CLR, -DOVE[2] / 2 - CLR), (DOVE[0] + CLR, DOVE[2] / 2 + CLR), (-1, DOVE[1] / 2 + CLR)], STRIP_T + 2).translate([0, 0, -STRIP_T - 1])
    z = s + box(L - 16, Wd, STRIP_T).translate([16, -Wd / 2, -STRIP_T])
    # serpentine wall: 6 folds, 1.2 mm thick, from z = 0 to H, between x = 20 and 56
    t = 1.2
    for i in range(6):
        x = 20 + i * 6
        z += box(t, Wd - 6, H).translate([x, -Wd / 2 + 3, 0])
        y_join = (Wd / 2 - 3 - t) if i % 2 == 0 else (-Wd / 2 + 3)
        if i < 5:
            z += box(6 + t, t, H).translate([x, y_join, 0])
    z += box(4, Wd - 6, H).translate([56, -Wd / 2 + 3, 0])         # face plate the trolley hits
    z -= box(70, SLOT_W + 2, HEAD_Z + 4).translate([-5, -(SLOT_W + 2) / 2, 0])   # slot for the rail blade
    z += rail(20)                                                   # rail stub into the slot region
    return z


# ---- 9. start gate and block-marker flag (clamp onto the wire) ----------------------
def wire_clamp_body(L=24.0):
    """Block with a wire slot and a tapered key pocket; pushing the key in pinches the wire."""
    b = box(L, 14, 16).translate([-L / 2, -7, -8])
    b -= rot(cyl(L + 2, WIRE_D + 0.3), "y", 90).translate([-L / 2 - 1, 0, 0])
    b -= box(L + 2, 1.0, 10).translate([-L / 2 - 1, -0.5, 0])          # slit from the wire slot upward
    b -= prism([(0, 0), (L + 2, 0), (L + 2, 3.5), (0, 2.0)], 7).translate([-L / 2 - 1, 0.5, 2])  # tapered key pocket
    return b


def start_gate():
    b = wire_clamp_body(30.0)
    # latch lever pivoting on a pin in two lugs below the wire; its tip holds the front axle head
    b += box(8, 20, 6).translate([-4, -10, -14]) - rot(cyl(22, 3.0 + 2 * CLR), "x", -90).translate([0, -11, -11])
    b -= rot(cyl(22, 3.0 + 2 * CLR), "x", -90).translate([0, -11, -11])   # 3 mm gate pin, CLR per side
    return b


def gate_key():
    return prism([(0, 0), (30, 0), (30, 3.1), (0, 1.6)], 6.6)


def gate_lever():
    lv = box(26, 6, 5).translate([-6, -3, -2.5])
    lv -= rot(cyl(8, 3.0 + 2 * CLR), "x", -90).translate([0, -4, 0])
    lv += box(5, 6, 14).translate([15, -3, -2.5])     # the finger that holds the trolley
    return lv


def gate_pin():
    return cyl(24, 3.0) + cyl(2, 6).translate([0, 0, -2])


def marker_flag():
    b = wire_clamp_body(20.0)
    b += box(6, 6, 4).translate([-3, 6, -8])
    flag = box(3, 30, 26).translate([-1.5, 9, -32])
    b += flag
    return b


# ---- 0. fit coupon: print this first and read the clearance off it -----------------
COUPON_CLR = (0.15, 0.20, 0.25, 0.30, 0.35, 0.40)


def fit_coupon():
    """One 6 mm post and one 4 mm pin (the cam post, the tongue pivot, the axle), beside a row
    of six rings bored at each clearance, numbered. Push the post through each ring: the first
    ring that turns freely with no wobble is your CLR; the first ring a 4 mm pin passes without
    force is your axle clearance. Set CLR at the top of this file (0.2 by default) and re-run."""
    base = box(118, 36, 3).translate([0, 0, -3])
    c = base + cyl(12.0, 6.0).translate([12, 10, 0]) + cyl(12.0, 4.0).translate([12, 26, 0])
    for i, k in enumerate(COUPON_CLR):
        x = 34 + i * 15
        c += cyl(6.0, 12.0).translate([x, 10, 0]) - cyl(8, 6.0 + 2 * k).translate([x, 10, -1])
        c += cyl(6.0, 9.0).translate([x, 26, 0]) - cyl(8, 4.0 + 2 * k).translate([x, 26, -1])
        for n in range(i + 1):   # i+1 notches on the rim: ring 1 = 0.15 ... ring 6 = 0.40
            c -= box(1.0, 2.0, 2.0).translate([x - 0.5 + (n - i / 2) * 1.8, 15.0, 4.5])
    return c


# ---- build everything ---------------------------------------------------------------
def main():
    print("part                          qty  mat    mass  bounding box (mm)")
    save(fit_coupon(), "fit_coupon_x1", 1, "PETG", "print first: post, pin and six bored rings at 0.15 to 0.40 mm; read your clearance off it")
    save(wheel(), "wheel_x6", 6, "PLA", "V-groove wheel; rides on the wire and on the rail head")
    save(axle_pin(), "axle_pin_x6", 6, "PETG", "4 mm pin, head one end, split snap the other")
    save(trolley_plate(), "trolley_plate_x6", 6, "PLA", "two identical plates per trolley; hooks under the wire")
    save(pannier(False), "pannier_right_x3", 3, "PLA", "basket half with brake-comb runner; slides onto the plate dovetail")
    save(pannier(True), "pannier_left_x3", 3, "PLA", "basket half with the chain hook")
    save(turnout_base(), "turnout_base_x1", 1, "PLA", "plate with entry rail, three exit rails, pivot post, cam post, both leaf springs")
    save(tongue(), "tongue_x1", 1, "PLA", "switch blade; pivots on the post, follower boss rides the cam")
    save(indexer(), "indexer_x1", 1, "PETG", "4-dwell cam (bays 1, 2, 3, 2), shaft, detent ring and star hub in one print")
    save(star_arm(), "star_arm_x4", 4, "PLA", "L-shaped; pushes into a hub socket; its cross-bar waits across the lanes")
    save(handover(), "handover_x1", 1, "PLA", "wire-to-rail ramp with wedge cleat and tie-down loop")
    save(wedge(), "wedge_x2", 2, "PETG", "pinches the wire in the cleat pockets (handover and window hook)")
    save(window_hook(), "window_hook_x1", 1, "PETG", "hooks a grill bar or handle; 3 turns round the post, then the wedge")
    save(lead_rail(), "lead_rail_230_x3", 3, "PLA", "first bay segment, narrow strip, straight")
    save(brake_segment(), "brake_comb_190_x3", 3, "PLA", "rail with 12 flexible teeth that rub the right pannier's floor")
    save(chain_bed(), "chain_bed_190_x3", 3, "PLA", "rail with a trough for the chain and the stirrup the hook catches")
    save(chain(), "chain_11_links_x3", 3, "PLA", "print-in-place drag chain, 11 links of 20 x 10 mm")
    save(bumper(), "bumper_x3", 3, "PETG", "zig-zag printed spring, the model's backup net")
    save(start_gate(), "start_gate_x3", 3, "PLA", "clamps on the wire; the lever holds a pod until flicked")
    save(gate_key(), "gate_key_x4", 4, "PETG", "tapered key that pinches the wire in a gate or flag")
    save(gate_lever(), "gate_lever_x3", 3, "PLA", "latch lever")
    save(gate_pin(), "gate_pin_x3", 3, "PETG", "lever pivot pin")
    save(marker_flag(), "block_marker_flag_x1", 1, "PLA", "optional: the block marker; the pod knocks the flag")
    with open(Path(__file__).resolve().parent / "parts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "qty", "material", "grams_each", "x_mm", "y_mm", "z_mm", "note"])
        for p in PARTS:
            w.writerow([p["name"] + ".stl", p["qty"], p["material"], p["grams"], *p["mm"], p["note"]])
    total = sum(p["grams"] * p["qty"] for p in PARTS)
    print(f"total filament about {total:.0f} g")
    preview()


def preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    n = len(PARTS)
    cols = 6
    rows = math.ceil(n / cols)
    fig = plt.figure(figsize=(16, 2.9 * rows))
    for i, p in enumerate(PARTS):
        tm = p["mesh"]
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        v = tm.vertices - tm.bounds.mean(axis=0)
        shade = np.clip(0.35 + 0.65 * np.abs(tm.face_normals @ np.array([0.4, -0.5, 0.75])), 0, 1)
        col = Poly3DCollection(v[tm.faces], facecolors=[(0.17 * s + 0.1, 0.39 * s + 0.1, 0.56 * s + 0.1) for s in shade], edgecolor="none")
        ax.add_collection3d(col)
        r = np.abs(v).max()
        ax.set_xlim(-r, r); ax.set_ylim(-r, r); ax.set_zlim(-r, r)
        ax.set_box_aspect([1, 1, 1])
        ax.view_init(26, -58)
        ax.set_axis_off()
        ax.set_title(f"{p['name']}\n{p['mm'][0]:.0f}×{p['mm'][1]:.0f}×{p['mm'][2]:.0f} mm, {p['material']}", fontsize=8)
    fig.suptitle("PLE-SBS print-only scale model: parts (Bambu Lab P1S, 0.4 mm nozzle)", fontsize=12)
    fig.tight_layout()
    fig.savefig(Path(__file__).resolve().parent / "parts_preview.png", dpi=120)
    print("wrote scale_down/parts_preview.png")


if __name__ == "__main__":
    main()
