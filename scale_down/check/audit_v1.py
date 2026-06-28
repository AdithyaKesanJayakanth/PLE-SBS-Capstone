"""Audit of the phase-1 parts as printed (make_parts.py at commit 19d142d): assemble them in
their working positions and measure overlaps and gaps with exact solid booleans."""
import math, sys
sys.path.insert(0, "..")
sys.path.insert(0, "check")
sys.path.insert(0, ".")
import numpy as np
from manifold3d import Manifold
import make_parts_v1 as P

def vol(m): return m.volume()
def ov(a, b): return (a ^ b).volume()           # overlap volume, mm^3
def T(m, x=0, y=0, z=0): return m.translate([x, y, z])
def Rz(m, d): return m.rotate([0, 0, d])
def bbox(m):
    b = m.bounding_box(); return np.array(b[:3]), np.array(b[3:])

# ---- the trolley, pod coordinates (z = 0 at the bottom of the hook lips)
plate = P.trolley_plate()
plateA = T(plate, 0, 4.5, 0)                     # inner face at y = +4.5
plateB = T(Rz(plate, 180), 0, -4.5, 0)           # identical plate turned round, inner face at y = -4.5
wheel = P.wheel().rotate([-90, 0, 0])            # axis along y, from y = 0 to 8
wheels = [T(wheel, x, -4.0, P.AXLE_Z) for x in (-20, 20)]
pin = P.axle_pin().rotate([90, 0, 0])            # head outside plate A, shank along -y
pins = [T(pin, x, 8.0 + 0.0, P.AXLE_Z) for x in (-20, 20)]
panR, panL = P.pannier(False), P.pannier(True)
print("=== wagon (trolley) ===")
for i, w in enumerate(wheels):
    print(f"wheel {i} overlap plate A {ov(w, plateA):.2f}  plate B {ov(w, plateB):.2f}  pin {ov(w, pins[i]):.2f} mm3")
for i, p in enumerate(pins):
    print(f"pin {i} overlap plate A {ov(p, plateA):.2f}  plate B {ov(p, plateB):.2f} mm3")
lo, hi = bbox(pins[0]); print(f"pin spans y {hi[1]:.1f} .. {lo[1]:.1f}; plate B outer face at y -8.0 (bump must clear it)")
# do the bridge pegs/pins reach the other plate?
pegA = T(P.box(6, 4.5 - P.CLR, 6).translate([18, -4.5 + P.CLR, 35.75 - 3]), 0, 4.5, 0)
print(f"plate A spacer peg reaches y {bbox(pegA)[0][1]:.2f}; plate B inner face at y -4.5 -> gap {bbox(pegA)[0][1] + 4.5:.2f} mm (should be 0: plates are not spaced)")
locpin = T(P.rot(P.cyl(8.0, 3.0), 'x', 90).translate([18, 0, 35.75]), 0, 4.5, 0)
print(f"plate A locating pin tip at y {bbox(locpin)[0][1]:.2f}; plate B hole starts at y -4.5 -> engagement {max(0, -4.5 - bbox(locpin)[0][1]):.2f} mm")
lipA_top = P.HOOK_TOP; wheel_bottom = P.AXLE_Z - P.WHEEL_OD / 2
print(f"wheel bottom z {wheel_bottom:.2f} vs hook-lip top z {lipA_top:.2f}: gap {wheel_bottom - lipA_top:.2f} mm")
print("=== pannier on plate dovetail ===")
dove = T(P.prism([(-5, P.PLATE_T), (5, P.PLATE_T), (7, P.PLATE_T + 3), (-7, P.PLATE_T + 3)], 14), 0, 4.5, 0)
lo, hi = bbox(dove); print(f"dovetail tab on plate A: y {lo[1]:.1f}..{hi[1]:.1f}  z {lo[2]:.1f}..{hi[2]:.1f}")
lo, hi = bbox(panR); print(f"right pannier: y {lo[1]:.1f}..{hi[1]:.1f}  z {lo[2]:.1f}..{hi[2]:.1f}")
print(f"pannier overlap with plate A {ov(panR, plateA):.1f} mm3; dovetail tab inside the pannier socket? tab volume {vol(dove):.0f}, tab-pannier overlap {ov(dove, panR):.0f}")
arm = P.box(18, 7.0, 14).translate([-9, P.BODY_W / 2 + P.PLATE_T - 0.5, -14]); lo, hi = bbox(arm)
print(f"pannier arm with the socket: y {lo[1]:.1f}..{hi[1]:.1f}  z {lo[2]:.1f}..{hi[2]:.1f}  -> tab is at z 0..14, socket at z -14.5..0.5: they do not meet")

# ---- pod on the rail: where does the 3.5 mm head sit in the wheel's V?
def seat(d):
    # V flank 39 deg off radial, 1.2 mm flat at r = 9: half-width at radius r = 0.6 + 0.8 (r - 9)
    phi = math.atan(0.8); r = 9 + (d / 2 / math.cos(phi) - 0.6) / 0.8
    return r                                      # distance from the axle to the circle's centre
r_wire, r_head = seat(1.5), seat(P.HEAD_D)
print("=== wagon on the yard rail ===")
print(f"wire centre {r_wire:.2f} below the axle, rail-head centre {r_head:.2f} below the axle")
pod_z0 = P.HEAD_Z - (P.AXLE_Z - r_head)           # strip-coordinate height of pod z = 0
pan_floor = pod_z0 + P.PAN_BOT
print(f"pannier floor {pan_floor:.2f} mm above the rail strip (code comment says 12)")
print(f"pannier spans y 9..35 each side; strip is 40 wide (+-20) -> floor skims the strip; comb teeth reach 12.7 -> interference {12.7 - pan_floor:.1f} mm")
pod = [plateA, plateB, *wheels, *pins, panR, panL]
pod = [T(m, 0, 0, pod_z0) for m in pod]
def pod_at(x, y, ang):
    return [T(Rz(m, ang), x, y, 0) for m in pod]
def hits(parts, other, name):
    o = sum(ov(m, other) for m in parts)
    return o
# ---- sweep through the turnout, each lane, tongue set to that lane
base = P.turnout_base()
idx = T(P.indexer(), P.CAM_X, P.CAM_Y, 0)
arms = [T(Rz(P.star_arm(), 90 * k), P.CAM_X, P.CAM_Y, 67.0 - 4.0) for k in range(4)]
print("=== wagon swept through the turnout (overlap volumes, mm3) ===")
for k, name in ((1, "bay 1"), (0, "bay 2"), (-1, "bay 3")):
    ang = k * P.LANE_ANG
    tong = T(Rz(P.tongue(), ang), P.TONGUE_X0, 0, 0)
    worst = {}
    for x in np.arange(0, 236, 8.0):
        if x < P.TONGUE_X0:
            px, py, pa = x, 0.0, 0.0
        else:
            s = x - P.TONGUE_X0
            px, py, pa = P.TONGUE_X0 + s * math.cos(math.radians(ang)), s * math.sin(math.radians(ang)), ang
        parts = pod_at(px, py, pa)
        for nm, other in (("turnout base + other lanes", base), ("tongue", tong), ("indexer", idx), *[(f"star arm {j}", a) for j, a in enumerate(arms)]):
            o = hits(parts, other, nm)
            if o > 0.5:
                worst[nm] = max(worst.get(nm, 0), o)
    print(f"{name}: " + ("; ".join(f"{n} {v:.0f}" for n, v in worst.items()) or "clear"))
# ---- tongue spring
print("=== tongue spring ===")
print("leaf spring face at y -19.4 (plate); tongue pad face at y -6 (tongue at bay 2); pad moves +-4.1 mm at the extremes -> gap 9.3..17.5 mm: the spring never touches the tongue")
