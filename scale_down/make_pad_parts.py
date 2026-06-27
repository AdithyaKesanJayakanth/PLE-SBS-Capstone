"""Phase 2: launch pad and rocket at 1:50 as printable STL segments for the P1S.

Run:  .venv/bin/python scale_down/make_pad_parts.py
    -> scale_down/stl_phase2/*.stl, pad_parts_preview.png, pad_parts.csv, render_pad.png

Everything is cosmetic and fits the 256 mm bed; segments join with spigots (tubes), pegs
(tower) and the yard's dovetails (platform tiles). The wire's pull goes to the window hook.
"""
import csv
import math
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold

import make_parts as P

OUT = Path(__file__).resolve().parent / "stl_phase2"
OUT.mkdir(exist_ok=True)
HERE = Path(__file__).resolve().parent

S = 50.0
def mm(x_m): return x_m * 1000.0 / S

CORE_D, BOOST_D = mm(4.0), mm(3.2)          # 80, 64
WALL = 1.6                                   # two perimeters
SEG_H = 240.0
SPIG_H, SPIG_CLR = 10.0, 0.25
TOWER_W, TOWER_SEC = mm(8.0), 240.0          # 160 x 160, four sections of 240 + 10 mm pegs = 250 on the bed
POST = 8.0
PAD_TILE, PAD_T = 236.0, 2.0                 # 236 + 12 mm dovetail tab = 248 on the bed
ACCESS_Z = mm(42.0)                          # 840
OFFSET = mm(15.0)                            # 300: rocket axis to tower axis

cyl, box, prism = P.cyl, P.box, P.prism
PARTS = []


def save(part, name, qty, material, colour, grams_each, note):
    mesh = part.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=True)
    assert tm.is_watertight, name
    assert max(tm.extents) <= 250.01, f"{name} {tm.extents}"
    tm.export(OUT / f"{name}.stl")
    PARTS.append(dict(name=name, qty=qty, material=material, colour=colour, grams=grams_each, mm=tuple(np.round(tm.extents, 1)), note=note, mesh=tm))
    print(f"{name:26s} x{qty:<2d} {material:8s} {colour:11s} {grams_each:4.0f} g  {np.round(tm.extents, 1)}")


def tube(d, h, wall=WALL):
    return cyl(h, d) - cyl(h + 2, d - 2 * wall).translate([0, 0, -1])


def spigot(d, wall=WALL):
    """Male spigot on top of a tube: fits inside the next segment's bore with clearance.
    A 2 mm ring joins it to the tube wall so the two are one solid."""
    di = d - 2 * wall - 2 * SPIG_CLR
    ring = (cyl(2.0, d) - cyl(4.0, di - 2 * wall).translate([0, 0, -1])).translate([0, 0, -2.0])
    return tube(di, SPIG_H, wall) + ring


# ---- rocket -----------------------------------------------------------------------
def core_segment():
    t = tube(CORE_D, SEG_H) + spigot(CORE_D).translate([0, 0, SEG_H])
    # strut peg holes at mid height, both sides (boosters sit at +-y)
    for sgn in (-1, 1):
        for z in (60.0, 180.0):
            t -= P.rot(cyl(12, 4.0), "x", 90).translate([0, sgn * (CORE_D / 2 + 1), z])
    return t


def capsule():
    """Frustum Ø80 -> Ø40 over 96 mm, then a nose to a 6 mm tip, with a socket for the core spigot."""
    skirt = cyl(13.0, CORE_D)
    frustum = Manifold.cylinder(84.0, CORE_D / 2, 20.0, P.SEG, False).translate([0, 0, 12.0])
    nose = Manifold.cylinder(65.0, 20.3, 3.0, P.SEG, False).translate([0, 0, 95.0])   # overlaps the frustum by 1 mm
    c = skirt + frustum + nose
    c -= cyl(SPIG_H + 1, CORE_D - 2 * WALL + 0.1).translate([0, 0, -1])      # socket for the spigot below, inside the skirt
    c -= Manifold.cylinder(82.0, CORE_D / 2 - 2.6, 14.0, P.SEG, False).translate([0, 0, 8.0])    # hollow, open into the socket below
    return c


def booster_lower():
    t = tube(BOOST_D, SEG_H) + spigot(BOOST_D).translate([0, 0, SEG_H])
    t -= P.rot(cyl(12, 4.0), "x", -90).translate([0, -(BOOST_D / 2 + 1), 60.0])
    t -= P.rot(cyl(12, 4.0), "x", -90).translate([0, -(BOOST_D / 2 + 1), 180.0])
    return t


def booster_upper():
    body = tube(BOOST_D, 200.0)
    cone = Manifold.cylinder(40.0, BOOST_D / 2, 4.0, P.SEG, False).translate([0, 0, 200.0])
    cone -= Manifold.cylinder(30.0, BOOST_D / 2 - WALL, 2.0, P.SEG, False).translate([0, 0, 200.0])
    b = body + cone
    b -= cyl(SPIG_H + 1, BOOST_D - 2 * WALL + 0.1).translate([0, 0, -1])
    return b


def booster_strut():
    """Two pegs back to back joined by a 6 mm collar: fills the 1 mm gap and locks the booster to the core."""
    s = cyl(6.5, 3.6).translate([0, 0, -0.5])         # into the core
    s += cyl(1.2, 10.0).translate([0, 0, -1.2])         # collar in the gap
    s += cyl(6.5, 3.6).translate([0, 0, -7.2])          # into the booster
    return s


# ---- tower --------------------------------------------------------------------------
def tower_section():
    w, h = TOWER_W, TOWER_SEC
    t = Manifold()
    half = w / 2 - POST / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            t += box(POST, POST, h, center=True).translate([sx * half, sy * half, h / 2])
    bay = h / 5.0
    # horizontal rings at every bay
    for z in np.arange(0, h + 1, bay):
        for sx in (-1, 1):
            t += box(w - 2 * POST + 8, 4, 4, center=True).translate([0, sx * half, min(z + 2, h - 2)])
            t += box(4, w - 2 * POST + 8, 4, center=True).translate([sx * half, 0, z + 2])
    # X bracing on all four faces
    L = math.hypot(w - POST - 6, bay - 6)
    ang = math.degrees(math.atan2(bay - 6, w - POST - 6))
    for k in range(5):
        z0 = k * bay
        for sgn in (-1, 1):
            brace = box(L, 3, 3, center=True)
            b1 = P.rot(brace, "y", -sgn * ang).translate([0, 0, z0 + bay / 2])
            t += b1.translate([0, half, 0]) + b1.translate([0, -half, 0])
            b2 = P.rot(P.rot(brace, "y", -sgn * ang), "z", 90).translate([0, 0, z0 + 25])
            t += b2.translate([half, 0, 0]) + b2.translate([-half, 0, 0])
    # stacking pegs on top, holes in the bottom
    for sx in (-1, 1):
        for sy in (-1, 1):
            t += cyl(10.0, 5.6).translate([sx * half, sy * half, h])
            t -= cyl(11.0, 6.1).translate([sx * half, sy * half, -1])
    return t


def crown():
    w = TOWER_W
    c = box(w, w, 8).translate([-w / 2, -w / 2, 0])
    half = w / 2 - POST / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            c -= cyl(9, 6.1).translate([sx * half, sy * half, -1])
    c += box(w, 10, 30).translate([-w / 2, -5, 8])                      # crane girder
    c += box(10, 10, 60).translate([w / 2 - 10, -5, 8]) + box(90, 8, 8).translate([w / 2 - 10, -4, 60])   # crane mast and jib
    return c


def arm_bracket():
    """Clips onto a corner post (8 x 8) and carries the arm pivot pin."""
    b = box(16, 20, 30).translate([-8, -10, 0]) - box(8.6, 8.6, 32).translate([-4.3, -4.3, -1])
    b -= box(2.0, 8.0, 32).translate([-1, 4.3, -1])                      # slit through one wall so the clip springs over the post
    b += box(12, 9, 30).translate([-6, -18, 0])                         # lug, overlapping the body by 1 mm
    b -= P.rot(cyl(40, 6.3), "x", 90).translate([0, -8, 15])            # pin hole through lug and body
    return b


def access_arm():
    L = OFFSET - TOWER_W / 2 - CORE_D / 2 - 2                           # 300 - 80 - 40 - 2 = 178
    a = box(L, 30, 12).translate([0, -15, 0])
    a += cyl(12, 20).translate([0, 0, 0]) - cyl(14, 6.3).translate([0, 0, -1])   # pivot boss
    a -= cyl(14, 6.3).translate([0, 0, -1])
    # curved yoke at the capsule end
    a -= cyl(14, CORE_D + 2).translate([L + CORE_D / 2 - 6, 0, -1])
    # handrails
    for sgn in (-1, 1):
        a += box(L - 30, 2, 14).translate([20, sgn * 13, 12])
    return a


def arm_pin():
    return cyl(44, 6.0) + cyl(2, 10).translate([0, 0, -2])


def wire_saddle():
    """Clips onto a corner post at the access level and shows the wire leaving the tower."""
    s = box(16, 20, 30).translate([-8, -10, 0]) - box(8.6, 8.6, 32).translate([-4.3, -4.3, -1])
    s -= box(2.0, 8.0, 32).translate([-1, 4.3, -1])
    s += box(24, 9, 22).translate([-12, 9, 8])
    s -= P.rot(cyl(30, 3.0), "y", 90).translate([-15, 14, 26])         # groove the wire lies in
    return s


# ---- ground -----------------------------------------------------------------------
def launch_mount():
    """Holds the core and both boosters at the right spacing; boosters touch the core."""
    pitch = CORE_D / 2 + BOOST_D / 2 + 1.0                              # 73: 1 mm gap, filled by the strut collar
    m = box(100, 2 * pitch + BOOST_D + 20, 30).translate([-50, -(pitch + BOOST_D / 2 + 10), 0])
    m -= cyl(31, CORE_D + 0.6).translate([0, 0, 12])
    for sgn in (-1, 1):
        m -= cyl(31, BOOST_D + 0.6).translate([0, sgn * pitch, 12])
    m -= cyl(40, CORE_D - 12).translate([0, 0, -1])                     # through hole, saves filament
    return m


def platform_tile():
    t = box(PAD_TILE, PAD_TILE, PAD_T).translate([0, 0, 0])
    # rib grid underneath (print this face up, then turn the tile over)
    for i in range(0, 5):
        t += box(PAD_TILE, 3, 8).translate([0, i * (PAD_TILE - 3) / 4, -8])
        t += box(3, PAD_TILE, 8).translate([i * (PAD_TILE - 3) / 4, 0, -8])
    dl, n, wdt = P.DOVE
    tab = prism([(0, -n / 2), (dl, -wdt / 2), (dl, wdt / 2), (0, n / 2)], PAD_T)
    slot = prism([(-1, -n / 2 - P.CLR), (dl + P.CLR, -wdt / 2 - P.CLR), (dl + P.CLR, wdt / 2 + P.CLR), (-1, n / 2 + P.CLR)], PAD_T + 2).translate([0, 0, -1])
    for pos in (PAD_TILE * 0.25, PAD_TILE * 0.75):
        t += tab.translate([PAD_TILE, pos, 0])                                    # +x edge: tabs
        t += P.rot(tab, "z", 90).translate([pos, PAD_TILE, 0])                     # +y edge: tabs
        t -= slot.translate([0, pos, 0])                                           # -x edge: slots
        t -= P.rot(slot, "z", 90).translate([pos, 0, 0])                           # -y edge: slots
    return t


# ---- build, preview, render ---------------------------------------------------------
def main():
    print("part                        qty  material colour       mass  bbox (mm)")
    save(core_segment(), "core_segment_x4", 4, "PLA", "Jade White", 60, "Ø80 x 240 tube, spigot on top, strut holes")
    save(capsule(), "capsule_x1", 1, "PLA", "Jade White", 50, "frustum and nose, socket for the core spigot")
    save(booster_lower(), "booster_lower_x2", 2, "PLA", "Light Grey", 50, "Ø64 x 240 tube, spigot on top")
    save(booster_upper(), "booster_upper_x2", 2, "PLA", "Light Grey", 55, "Ø64 x 200 tube with the nose")
    save(booster_strut(), "booster_strut_x4", 4, "PLA", "Light Grey", 1, "double peg: core hole to booster hole")
    save(tower_section(), "tower_section_x4", 4, "PLA", "Dark Grey", 110, "160 x 160 x 250 lattice, pegs up, holes down")
    save(crown(), "tower_crown_x1", 1, "PLA", "Dark Grey", 60, "cap with crane")
    save(arm_bracket(), "arm_bracket_x1", 1, "PLA", "Dark Grey", 8, "clips onto a corner post at the access level")
    save(access_arm(), "access_arm_x1", 1, "PLA", "Orange", 45, "swings on the bracket pin to the capsule")
    save(arm_pin(), "arm_pin_x1", 1, "PETG", "Orange", 2, "Ø6 pivot pin")
    save(wire_saddle(), "wire_saddle_x1", 1, "PLA", "Dark Grey", 10, "clips onto a post; the wire leaves the tower here")
    save(launch_mount(), "launch_mount_x1", 1, "PLA", "Light Grey", 80, "three pockets hold the core and boosters")
    save(platform_tile(), "platform_tile_x4", 4, "PLA", "Light Grey", 150, "240 x 240 tile, ribs below, dovetails")
    with open(HERE / "pad_parts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "qty", "material", "colour", "grams_each", "x_mm", "y_mm", "z_mm", "note"])
        for p in PARTS:
            w.writerow([p["name"] + ".stl", p["qty"], p["material"], p["colour"], p["grams"], *p["mm"], p["note"]])
    total = sum(p["grams"] * p["qty"] for p in PARTS)
    print(f"phase 2 filament about {total:.0f} g")
    preview()
    render_pad()


def preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    n, cols = len(PARTS), 5
    rows = math.ceil(n / cols)
    fig = plt.figure(figsize=(15, 3.2 * rows))
    for i, p in enumerate(PARTS):
        tm = p["mesh"]
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        v = tm.vertices - tm.bounds.mean(axis=0)
        shade = np.clip(0.35 + 0.65 * np.abs(tm.face_normals @ np.array([0.4, -0.5, 0.75])), 0, 1)
        ax.add_collection3d(Poly3DCollection(v[tm.faces], facecolors=[(0.17 * s + 0.1, 0.39 * s + 0.1, 0.56 * s + 0.1) for s in shade], edgecolor="none"))
        r = np.abs(v).max()
        ax.set_xlim(-r, r); ax.set_ylim(-r, r); ax.set_zlim(-r, r); ax.set_box_aspect([1, 1, 1]); ax.view_init(24, -58); ax.set_axis_off()
        ax.set_title(f"{p['name']}\n{p['mm'][0]:.0f}×{p['mm'][1]:.0f}×{p['mm'][2]:.0f} mm, {p['colour']}", fontsize=8)
    fig.suptitle("PLE-SBS phase 2: pad and rocket parts at 1:50 (Bambu Lab P1S)", fontsize=12)
    fig.tight_layout()
    fig.savefig(HERE / "pad_parts_preview.png", dpi=120)
    print("wrote scale_down/pad_parts_preview.png")


def render_pad():
    """Assembled pad in its print colours, two views."""
    import make_renders as R
    R.COL.update({"white": (0.93, 0.94, 0.95), "lgrey": (0.72, 0.75, 0.78), "dgrey": (0.30, 0.33, 0.37), "orange": (0.89, 0.34, 0.06)})
    def L(name): return trimesh.load(OUT / f"{name}.stl")
    pieces = []
    for i in range(2):
        for j in range(2):
            pieces.append((R.place(L("platform_tile_x4"), -PAD_TILE + i * PAD_TILE, -PAD_TILE + j * PAD_TILE - 60, 0), "lgrey"))
    pieces.append((R.place(L("launch_mount_x1"), 0, 0, PAD_T), "lgrey"))
    for k in range(4):
        pieces.append((R.place(L("core_segment_x4"), 0, 0, PAD_T + 12 + k * SEG_H), "white"))
    pieces.append((R.place(L("capsule_x1"), 0, 0, PAD_T + 12 + 4 * SEG_H), "white"))
    pitch = CORE_D / 2 + BOOST_D / 2 + 1.0
    for sgn in (-1, 1):
        pieces.append((R.place(L("booster_lower_x2"), 0, sgn * pitch, PAD_T + 12), "lgrey"))
        pieces.append((R.place(L("booster_upper_x2"), 0, sgn * pitch, PAD_T + 12 + SEG_H), "lgrey"))
    for k in range(4):
        pieces.append((R.place(L("tower_section_x4"), OFFSET, 0, PAD_T + k * TOWER_SEC), "dgrey"))
    pieces.append((R.place(L("tower_crown_x1"), OFFSET, 0, PAD_T + 4 * TOWER_SEC), "dgrey"))
    pieces.append((R.place(L("access_arm_x1"), OFFSET - TOWER_W / 2 + 4, 0, PAD_T + ACCESS_Z, yaw=180), "orange"))
    R.render(pieces, HERE / "render_pad.png", 18, -35, figsize=(9, 9))
    R.render(pieces, HERE / "render_pad_side.png", 6, -90, figsize=(9, 9))


if __name__ == "__main__":
    main()
