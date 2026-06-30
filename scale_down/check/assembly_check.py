"""Fit and motion check for phase 1: every part in its working position, exact overlaps by
manifold booleans, plus the escapement simulated through a full fill (R, C, L).

Run:  .venv/bin/python scale_down/check/assembly_check.py   -> prints the report and writes
      scale_down/check/assembly_report.md

Overlap volumes are in mm^3. "Contact" means the parts touch (zero or near-zero volume) where they
are meant to; anything else above 0.05 mm^3 is a clash.
"""
import functools
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import make_parts as P  # noqa: E402

EPS = 0.05
LINES = []


def say(s=""):
    print(s)
    LINES.append(s)


def ov(a, b):
    return (a ^ b).volume()


def clear_shift(a, b, d, hi=2.0, step=0.02):
    """Smallest move of a along d that clears b (hi if none)."""
    d = np.asarray(d, float)
    t = 0.0
    while t <= hi:
        if ov(a.translate(list(d * t)), b) <= EPS:
            return t
        t += step
    return hi


def gap(a, b, d, hi=6.0):
    """Distance a can move along unit vector d before it overlaps b (0 if it already does)."""
    d = np.asarray(d, float)
    if ov(a, b) > EPS:
        return 0.0
    if ov(a.translate(list(d * hi)), b) <= EPS:
        return hi
    lo, h = 0.0, hi
    for _ in range(22):
        m = (lo + h) / 2
        if ov(a.translate(list(d * m)), b) > EPS:
            h = m
        else:
            lo = m
    return lo


# ---------------------------------------------------------------------------- cached solids
tongue_solid = functools.lru_cache(None)(P.tongue)
rocker_solid = functools.lru_cache(None)(P.rocker)
base_solid = functools.lru_cache(None)(P.turnout_base)
flap_body = functools.lru_cache(None)(P._flap_body)


def tongue_at(T):
    return P.place(tongue_solid(), T, *P.PIVOT)


def rocker_at(t):
    return P.rk_place(rocker_solid(), t)


def flap_at(s):
    return flap_body().rotate([0, -s, 0]).translate([P.GANTRY_X, 0, P.GANTRY_Z])


POD = None


def pod_local():
    global POD
    if POD is None:
        POD = P.pod_parts()
    return POD


def pod_at(x, y, yaw, lift=0.0, z=None):
    z = P.POD_Z if z is None else z
    return [(n, m.rotate([0, 0, yaw]).translate([x, y, z + lift])) for n, m in pod_local()]


def union(ms):
    out = None
    for m in ms:
        out = m if out is None else out + m
    return out


# ============================================================================ 1. the wagon
def check_wagon():
    say("## 1. Wagon")
    parts = dict(pod_local())
    names = list(parts)
    bad = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = ov(parts[names[i]], parts[names[j]])
            if v > EPS:
                bad.append((names[i], names[j], v))
    say(f"- Clashes between wagon parts: {'none' if not bad else ''}")
    for a, b, v in bad:
        say(f"  - CLASH {a} / {b}: {v:.2f}")
    pr, pl = parts["plate R"], parts["plate L"]
    # spacer pegs: how far each peg reaches into the other plate
    for name, plate, x, sgn in (("front peg (plate R into L)", pr, P.PEG_X, -1), ("rear peg (plate L into R)", pl, -P.PEG_X, 1)):
        peg = plate ^ P.cyl_y(-20, 20, P.PEG_D - 0.2, x, P.PEG_Z)
        bb = peg.bounding_box()
        tip = bb[1] if sgn < 0 else bb[4]
        reach = abs(tip) - P.Y_IN
        hole = (pl if sgn < 0 else pr)
        say(f"- {name}: reaches {reach:.1f} mm into the {P.PL_T} mm plate; {gap(plate, hole, (0, 0, 1)):.2f} / {gap(plate, hole, (0, 0, -1)):.2f} mm play in the hole")
    for side in ("rear", "front"):
        w = parts[f"wheel {side}"]
        gy = min(gap(w, pr, (0, 1, 0)), gap(w, pl, (0, -1, 0)))
        say(f"- {side} wheel: side play {gap(w, pr, (0, 1, 0)):.2f} / {gap(w, pl, (0, -1, 0)):.2f} mm to the thrust bosses; "
            f"{gap(w, parts[f'pin {side}'], (0, 0, 1)):.2f} mm radial play on the pin")
    pin = parts["pin front"]
    say(f"- axle pin: head to right pannier {gap(pin, parts['pannier R'], (0, -1, 0)):.2f} mm; "
        f"snap bump to left pannier face {gap(pin, parts['pannier L'], (0, 1, 0)):.2f} mm (pin pushed home)")
    for side, pn, pl_ in (("right", "pannier R", pr), ("left", "pannier L", pl)):
        pa = parts[pn]
        say(f"- {side} pannier: {gap(pa, pl_, (0, -1 if side == 'right' else 1, 0)):.2f} mm to its plate (0 = clamped flat); "
            f"floor {pa.bounding_box()[2] + P.POD_Z:.1f} mm above the rail strip")
    say()


# ============================================================================ 2. wagon on rail and wire
def check_on_rail():
    say("## 2. Wagon on a rail and on the wire")
    rail = P.lead_rail().translate([-115, 0, 0])
    pod = dict(pod_at(0, 0, 0))
    wheels = union([pod["wheel rear"], pod["wheel front"]])
    say(f"- wheels seated on the head: drop before contact {gap(wheels, rail, (0, 0, -1)):.2f} mm (0 = seated)")
    lifted = dict(pod_at(0, 0, 0, lift=0.02))
    rest = union([m for n, m in lifted.items() if not n.startswith("wheel")])
    say(f"- lips under the head: the wagon lifts {gap(rest, rail, (0, 0, 1)):.2f} mm before a lip hooks the head")
    say(f"- side play on the rail web: {gap(rest, rail, (0, 1, 0)):.2f} / {gap(rest, rail, (0, -1, 0)):.2f} mm")
    clash = [(n, ov(m, rail)) for n, m in lifted.items() if ov(m, rail) > EPS]
    say(f"- clashes with the rail: {clash if clash else 'none'}")
    wire = P.cyl_x(-200, 200, P.WIRE_D, 0, P.POD_Z - P.R_WIRE)
    say(f"- on the wire: wheels drop {gap(wheels, wire, (0, 0, -1)):.2f} mm to seat; wire to lip slot sides "
        f"{gap(wire, rest, (0, 1, 0)):.2f} / {gap(wire, rest, (0, -1, 0)):.2f} mm; lips {gap(rest, wire, (0, 0, 1)):.2f} mm below the wire")
    say()


# ============================================================================ 3. the yard
BAY = [("lead", P.lead_rail, 230.0), ("brake", P.brake_segment, 190.0), ("chainbed", P.chain_bed, 190.0), ("bumper", P.bumper, 64.0)]


def bays(k):
    t = P.LANES[k]
    x0, y0 = P.PLATE_L, P.lane_y(k, P.PLATE_L)
    a = math.radians(t)
    out = []
    s = 0.0
    for name, fn, L in BAY:
        out.append((f"{name} {k}", P.place(fn(), t, x0 + s * math.cos(a), y0 + s * math.sin(a)), s))
        s += L
    return out


def sled_chain(k):
    t = P.LANES[k]
    a = math.radians(t)
    s0 = 230 + 190
    x0, y0 = P.PLATE_L + s0 * math.cos(a), P.lane_y(k, P.PLATE_L) + s0 * math.sin(a)
    sled = P.place(P.sled().translate([16.0, -14.0, -2.0]), t, x0, y0)
    ch = P.place(P.chain().translate([16.0 + 20.0 + 1.0 + P.LINK[0] / 2, -14.0, -2.0]), t, x0, y0)
    return sled, ch


def lane_path(k, u):
    """Point and heading at arc length u from x = -260 along lane k (straight to the pivot, then the lane)."""
    x0 = -260.0
    up = P.PIVOT[0] - x0
    t = math.radians(P.LANES[k])
    if u <= up:
        return np.array([x0 + u, 0.0])
    return np.array([P.PIVOT[0] + (u - up) * math.cos(t), (u - up) * math.sin(t)])


def pod_pose(k, u):
    r, f = lane_path(k, u - P.AX_X), lane_path(k, u + P.AX_X)
    c = (r + f) / 2
    return c[0], c[1], math.degrees(math.atan2(f[1] - r[1], f[0] - r[0]))


def wire_solid():
    """The wire: along y = 0 in the handover groove, down the dive, then under the yard."""
    zc = P.WIRE_C
    xs = P.GROOVE_END - P.HO_L
    w = P.cyl_x(-600, xs + 0.5, P.WIRE_D, 0, zc)
    a = math.radians(P.DIVE_ANG)
    zb = -P.STRIP_T + 1.1
    xb = P._dive_bottom_x() - P.HO_L
    L = math.hypot(xb - xs, zc - zb)
    seg = P.cyl_x(0, L, P.WIRE_D).rotate([0, P.DIVE_ANG, 0]).translate([xs, 0, zc])
    x_end = P.PLATE_L + 40
    run = P.cyl_x(0, math.hypot(x_end - xb, P.wire_y(x_end) - 0), P.WIRE_D).rotate([0, 0, math.degrees(math.atan(P.WIRE_SLOPE))]).translate([xb, 0, zb])
    return w + seg + run


def check_yard():
    say("## 3. Yard: static fit")
    base = base_solid()
    ho = P.handover_in_yard()
    statics = [("handover", ho), ("turnout plate", base)]
    for k in P.LANES:
        statics += [(n, m) for n, m, _ in bays(k)]
    bad = []
    for i in range(len(statics)):
        for j in range(i + 1, len(statics)):
            a, b = statics[i][1], statics[j][1]
            ba, bb = a.bounding_box(), b.bounding_box()
            if any(ba[q] > bb[q + 3] or bb[q] > ba[q + 3] for q in range(3)):
                continue
            v = ov(a, b)
            if v > EPS:
                bad.append((statics[i][0], statics[j][0], v))
    say(f"- modules joined by their dovetails, clashes: {'none' if not bad else ''}")
    for a, b, v in bad:
        say(f"  - CLASH {a} / {b}: {v:.2f}")
    tab = P.dove_tab()
    slot_part = P.strip(40, 40, male=False)
    say(f"- dovetail play: {gap(tab, slot_part, (0, 1, 0)):.2f} mm sideways, {gap(tab, slot_part, (1, 0, 0)):.2f} mm along")
    w = wire_solid()
    for n, m in statics[:2]:
        v = ov(w, m)
        say(f"- wire through the {n}: {'clear' if v <= EPS else f'CLASH {v:.2f}'}; "
            f"side play {min(gap(w, m, (0, 1, 0), 2), gap(w, m, (0, -1, 0), 2)):.2f} mm")
    say()
    return statics


def check_tongue_and_spring():
    say("## 4. Tongue, spring and stops")
    base = base_solid()
    lo, hi = -P.THETA - P.OVERTRAVEL, P.THETA + P.OVERTRAVEL
    clashes = []
    for T in np.arange(lo, hi + 0.01, 0.25):
        v = ov(tongue_at(T), base)
        if v > EPS:
            clashes.append((round(T, 2), round(v, 2)))
    say(f"- tongue swept {lo:.2f} to {hi:.2f} degrees against the plate: {'clear' if not clashes else clashes[:6]}")
    # the stops: tongue cannot go beyond
    for T, s in ((hi + 0.3, "left"), (lo - 0.3, "right")):
        say(f"- {s} overtravel stop: tongue {0.3:.1f} degrees past the outer lane overlaps the stop by {ov(tongue_at(T), base):.2f} (must be > 0)")
    # spring: deflection that just touches the tab
    rows = []
    for T in (lo, -P.THETA, 0.0, P.THETA, hi):
        tg = tongue_at(T)
        d0, d1 = 0.0, 25.0
        for _ in range(24):
            m = (d0 + d1) / 2
            if ov(P.bias_spring(m), tg) > EPS:
                d0 = m
            else:
                d1 = m
        leaf = P.bias_spring(d1 + 0.05)
        cl = ov(leaf, base)
        rows.append((T, d1, cl))
    E, I, L = 2000.0, P.SPRING_H * P.SPRING_T ** 3 / 12, P.spring_dir()[1] - 2.0
    k = 3 * E * I / L ** 3
    for T, d, cl in rows:
        say(f"- spring at tongue {T:+.2f} deg: leaf bent {d:.1f} mm, force {k * d:.2f} N, strain {3 * P.SPRING_T * d / (2 * L * L) * 100:.2f} %, "
            f"leaf vs plate {'clear' if cl <= EPS else f'CLASH {cl:.2f}'}")
    say()


# ============================================================================ 5. escapement
def first_contact(T0, t, T_max, step=0.1):
    """Tongue driven by the spring from T0 toward T_max; returns the angle it stops at."""
    rk = rocker_at(t)
    if ov(tongue_at(T0), rk) > EPS:
        return None
    T = T0
    while T < T_max:
        Tn = min(T + step, T_max)
        if ov(tongue_at(Tn), rk) > EPS:
            lo, hi = T, Tn
            for _ in range(12):
                m = (lo + hi) / 2
                if ov(tongue_at(m), rk) > EPS:
                    hi = m
                else:
                    lo = m
            return lo
        T = Tn
    return T_max


def move_rocker(T, t_from, t_to, T_max, steps=24):
    """Tilt the rocker step by step; after each step the spring advances the tongue. Returns the
    tongue angle, or raises if the rocker cannot reach the tilt (a finger lands on a tooth)."""
    log = []
    for t in np.linspace(t_from, t_to, steps + 1)[1:]:
        if ov(tongue_at(T), rocker_at(t)) > EPS:
            # the finger moving in touches a tooth: allow the tongue to be pushed back a little (recoil)
            back = T
            while back > T - 3.0 and ov(tongue_at(back), rocker_at(t)) > EPS:
                back -= 0.05
            if ov(tongue_at(back), rocker_at(t)) > EPS:
                raise RuntimeError(f"jam: rocker cannot reach {t:.1f} deg at tongue {T:.2f}")
            log.append(T - back)
            T = back
        T = first_contact(T, t, T_max)
    return T, log


def check_escapement():
    say("## 5. Escapement: three pods, three bays")
    T_max = P.THETA + P.OVERTRAVEL
    base = base_solid()
    rk_cl = []
    for t in np.arange(P.REST_TILT - 0.4, P.LIMIT_TILT + 0.41, 0.5):
        v = ov(rocker_at(t), base)
        rk_cl.append((round(t, 1), v))
    inside = [(t, v) for t, v in rk_cl if P.REST_TILT + 0.2 < t < P.LIMIT_TILT - 0.2 and v > EPS]
    say(f"- rocker tilted {P.REST_TILT:.0f} to {P.LIMIT_TILT:.0f} degrees against the goalposts and stops: {'clear' if not inside else inside}")
    say(f"- rest stop: 0.4 degrees beyond rest overlaps {ov(rocker_at(P.REST_TILT - 0.4), base):.2f}; limit stop 0.4 beyond overlaps "
        f"{ov(rocker_at(P.LIMIT_TILT + 0.4), base):.2f} (both must be > 0: they are the stops)")
    pin = P.rocker_pin_in_yard()
    say(f"- rocker pin in the notches: {'clear' if ov(pin, base) <= EPS else 'CLASH %.2f' % ov(pin, base)}; "
        f"pin in the rocker bore: {'clear' if ov(pin, rocker_at(0)) <= EPS else 'CLASH'}")
    # finger heights
    for t, nm in ((P.REST_TILT, "rest"), (P.TRIG_TILT, "triggered")):
        bb = rocker_at(t)
        ra = P.rk_point((P.FA[0], P.FA[1], -P.FING_H), t)[2]
        rb = P.rk_point((P.FB[0], P.FB[1], -P.FING_H), t)[2]
        say(f"- {nm}: finger A tip at z {ra:.2f}, finger B tip at z {rb:.2f} (teeth {P.TOOTH_Z0} to {P.TOOTH_Z1})")
    # full sequence
    ok = True
    T = -P.THETA - P.OVERTRAVEL
    T = first_contact(T, P.REST_TILT, T_max)
    say(f"- reset: tongue held by finger A at {T:+.2f} deg (lane R is {-P.THETA:+.2f})")
    expect = [0.0, P.THETA]
    for n, want in enumerate(expect):
        for trig in (P.TRIG_TILT, ):
            try:
                T1, log1 = move_rocker(T, P.REST_TILT, trig, T_max)
                T2, log2 = move_rocker(T1, trig, P.REST_TILT, T_max)
            except RuntimeError as e:
                say(f"  - JAM on trigger {n + 1}: {e}")
                ok = False
                break
            rc = max(log1 + log2) if log1 + log2 else 0.0
            say(f"- pod {n + 1} passes the flap: finger B catches the tongue at {T1:+.2f} deg; flap falls back, "
                f"finger A stops it at {T2:+.2f} deg (want {want:+.2f}); largest push-back by a finger {rc:.2f} deg")
            if abs(T2 - want) > 0.3:
                ok = False
            T = T2
    # minimum and maximum trigger tilts
    for trig in (P.TRIG_TILT - 6.0, P.LIMIT_TILT):
        try:
            Ts = first_contact(-P.THETA - P.OVERTRAVEL, P.REST_TILT, T_max)
            T1, _ = move_rocker(Ts, P.REST_TILT, trig, T_max)
            T2, _ = move_rocker(T1, trig, P.REST_TILT, T_max)
            say(f"- trigger to only {trig:.0f} deg: R to {T2:+.2f} deg")
        except RuntimeError as e:
            say(f"- trigger to only {trig:.0f} deg: JAM {e}")
    say(f"- escapement sequence: {'R, C, L as designed' if ok else 'FAILED'}")
    say()
    return ok


# ============================================================================ 6. pods through the yard
def check_sweeps(statics):
    say("## 6. A wagon through each lane")
    base = base_solid()
    ho = P.handover_in_yard()
    T_of = {"R": -P.THETA, "C": 0.0, "L": P.THETA}
    results = {}
    for k in P.FILL_ORDER:
        bay = bays(k)
        sled, chain = sled_chain(k)
        obst = [("handover", ho), ("turnout plate", base), ("tongue", tongue_at(T_of[k])), ("rocker", rocker_at(P.REST_TILT)),
                ("rocker pin", P.rocker_pin_in_yard()), ("spring", P.bias_spring(0.0))]
        for kk in P.LANES:
            for n, m, _ in bays(kk):
                obst.append((n, m))
        # spring: deflect to touch the tongue
        tg = tongue_at(T_of[k])
        d0, d1 = 0.0, 25.0
        for _ in range(20):
            m_ = (d0 + d1) / 2
            if ov(P.bias_spring(m_), tg) > EPS:
                d0 = m_
            else:
                d1 = m_
        obst = [(n, P.bias_spring(d1 + 0.05)) if n == "spring" else (n, m) for n, m in obst]
        obst += [("sled", sled), ("chain", chain)]
        static_union = union([m for _, m in obst])
        bump_start = 230 + 190 + 190
        u_end = (P.PIVOT[0] + 260) + (P.PLATE_L - P.PIVOT[0]) / math.cos(math.radians(P.LANES[k])) + bump_start + 24 - P.PL_X - 1.0
        hits = {}
        swing_max = 0.0
        comb_ov = 0.0
        u = 40.0
        while u <= u_end:
            x, y, yaw = pod_pose(k, u)
            pod = pod_at(x, y, yaw, lift=0.03)
            pu = union([m for _, m in pod])
            if ov(pu, static_union) > EPS:
                for pn, pm in pod:
                    for on, om in obst:
                        v = ov(pm, om)
                        if v > EPS:
                            key = (pn, on)
                            hits.setdefault(key, [u, u, 0.0])
                            hits[key][1] = u
                            hits[key][2] = max(hits[key][2], v)
            if 150 < x < 300:
                s0, s1 = 0.0, 80.0
                if ov(pu, flap_at(0.0)) > EPS:
                    for _ in range(14):
                        m_ = (s0 + s1) / 2
                        if ov(pu, flap_at(m_)) > EPS:
                            s0 = m_
                        else:
                            s1 = m_
                    swing_max = max(swing_max, s1)
            u += 4.0
        results[k] = (hits, swing_max)
        say(f"- lane {k} (tongue {T_of[k]:+.2f} deg): wagon pushes the flap to {swing_max:.1f} deg")
        for (pn, on), (a, b, v) in sorted(hits.items(), key=lambda kv: kv[1][0]):
            intended = (on.startswith("brake") and pn == "pannier R") or (on == "sled" and pn == "pannier L")
            rolling = pn.startswith("wheel") and on in ("tongue", "turnout plate", "handover")
            tag = "intended" if intended else ("wheel steered by the head" if rolling else "CLASH")
            extra = ""
            if rolling:
                worst = 0.0
                for uu in np.arange(a, b + 0.1, 1.0):
                    x, y, yaw = pod_pose(k, uu)
                    wm = dict(pod_at(x, y, yaw, lift=0.03))[pn]
                    om = dict(obst)[on]
                    if ov(wm, om) > EPS:
                        worst = max(worst, clear_shift(wm, om, (0, 0, 1), 1.0, 0.01))
                extra = f"; the wheel rides up at most {worst:.2f} mm over the joint"
            say(f"  - {tag}: {pn} / {on} from {a:.0f} to {b:.0f} mm along the path, up to {v:.1f}{extra}")
    say()
    return results


# ============================================================================ 7. flap and thread
def check_flap(swing_needed):
    say("## 7. Flap, thread and trigger")
    base = base_solid()
    ax = P.gantry_axle()
    cl = []
    for s in np.arange(0, 75.1, 2.5):
        f = flap_at(s)
        v1, v2 = ov(f, base), ov(f, ax)
        if v1 > EPS or v2 > EPS:
            cl.append((s, round(v1, 2), round(v2, 2)))
    say(f"- flap swung 0 to 75 deg: {'clear of the posts and the axle' if not cl else cl[:5]}")
    say(f"- axle in the snap notches: {'clear' if ov(ax, base) <= EPS else 'CLASH %.2f' % ov(ax, base)}")

    def taut_tilt(s, slack):
        L0 = np.linalg.norm(np.subtract(P.crank_hole(0), P.rocker_hole(P.REST_TILT))) + slack
        c = np.array(P.crank_hole(s))
        t = P.REST_TILT
        while t < 40 and np.linalg.norm(c - np.array(P.rocker_hole(t))) > L0:
            t += 0.05
        return t

    def stop_swing(slack):
        s = 0.0
        while s < 90 and taut_tilt(s, slack) < P.LIMIT_TILT:
            s += 0.25
        return s

    need = max(swing_needed.values())
    for slack in (0.0, 0.5, 1.0, 1.5):
        t_pass = taut_tilt(need, slack)
        say(f"- thread tied with {slack:.1f} mm slack: at {need:.1f} deg of flap the rocker tilts to {t_pass:+.1f} deg "
            f"(needs {P.TRIG_TILT - 6:+.0f} or more); the rocker reaches its stop, and holds the flap, at {stop_swing(slack):.1f} deg")
    say()


# ============================================================================ 8. bumper, gate, wedges
def check_ends():
    say("## 8. Bumper, start gate, wire ends")
    # bumper: wagon pushed into the zig-zag until the face plate
    bump = P.bumper()
    seg = P.chain_bed().translate([-190.0, 0, 0])
    x_touch = None
    for x in np.arange(-40, 40, 0.25):
        pod = union([m for _, m in pod_at(x, 0, 0, lift=0.03)])
        if ov(pod, bump) > EPS:
            x_touch = x
            break
    pod = dict(pod_at(x_touch, 0, 0, lift=0.03))
    first = [n for n, m in pod.items() if ov(m, bump) > EPS]
    say(f"- bumper: first contact with the zig-zag by {', '.join(first)}; front axle then {x_touch + P.AX_X:.0f} mm along a 60 mm rail stub")
    # sled pushed down the trough: chain bed then bumper, until it meets the zig-zag
    bed = P.chain_bed()
    bmp = P.bumper().translate([190.0, 0, 0])
    sl = P.sled().translate([16.0, -14.0, -2.0])
    x_hit, what = None, None
    for dx in np.arange(0, 230, 1.0):
        s2 = sl.translate([dx, 0, 0])
        if ov(s2, bed) > EPS:
            x_hit, what = dx, "the chain bed"
            break
        if ov(s2, bmp) > EPS:
            x_hit, what = dx, "the bumper"
            break
    zz = (bmp ^ sl.translate([x_hit, 0, 0])).bounding_box() if x_hit is not None else None
    say(f"- sled pushed along the trough: runs {x_hit:.0f} mm, then meets {what} at z {zz[2]:.1f} to {zz[5]:.1f} (the zig-zag stands on z 0)")
    sl0, ch0 = sled_chain("C")
    say(f"- sled and chain at rest: {'clear' if ov(sl0, ch0) <= EPS else 'CLASH'}")
    # gate
    g, lv = P.gate_in_pod()
    pod = dict(pod_local())
    cl = [(n, round(ov(m, g), 2)) for n, m in pod.items() if ov(m, g) > EPS]
    say(f"- start gate clamp vs wagon: {'clear' if not cl else cl}; gap to the wagon {gap(g, union(list(pod.values())), (1, 0, 0)):.2f} mm")
    cl = [(n, round(ov(m, lv), 2)) for n, m in pod.items() if ov(m, lv) > EPS]
    say(f"- gate lever latched: {'clear' if not cl else cl}; the wagon moves {gap(union(list(pod.values())), lv, (1, 0, 0)):.2f} mm before the peg meets the hook")
    say(f"- gate lever vs clamp: {'clear' if ov(lv, g) <= EPS else 'CLASH %.2f' % ov(lv, g)}")
    piv = (P.GATE_CX + P.GPX, 0, P.GPZ - P.R_WIRE)
    sweep = union([pod["plate L"].translate([dx, 0, 0]) for dx in np.arange(0, 40, 1.0)])
    a_rel = None
    for a in np.arange(0, 60, 0.5):
        l2 = lv.translate([-piv[0], 0, -piv[2]]).rotate([0, -a, 0]).translate([piv[0], 0, piv[2]])
        if ov(l2, sweep) <= EPS:
            a_rel = a
            break
    say(f"- release: lifting the lever {a_rel} deg frees the wagon")
    wire = P.cyl_x(-200, 200, P.WIRE_D, 0, -P.R_WIRE)
    say(f"- wire in the gate clamp: {'clear' if ov(wire, g) <= EPS else 'CLASH'}")
    body = P.wire_clamp_body(30.0)
    y0 = -(P.WIRE_D + 0.4) / 2
    for d in (1.4, 1.5, 1.6):
        gw = P.cyl_x(-40, 40, d, y0 + d / 2, 0)
        shown = None
        for o in np.arange(0.0, 30.0, 0.05):
            f = y0 + 1.0 + P.KEY_TAPER * o
            key = P.section([(-15 + o, f), (15 + o, f), (15 + o, f + 3.1), (-15 + o, f + 1.6)], "xy", -3.3, 3.3)
            if ov(key, gw) <= EPS:
                shown = o
                break
        say(f"  - gate key on a {d} mm wire: grips with {shown:.1f} mm of key showing (clear of the body: {ov(key, body) <= EPS})")
    # wedge in the window hook pocket with a wire against the wall
    hook = P.window_hook()
    zw = P.POCKET_Z + P.WIRE_D / 2
    wire = P.cyl_x(P.POCKET_X0 + 0.2, 90, P.WIRE_D, 14.0, zw)
    wd = P.wedge().rotate([90, 0, 0]).translate([P.POCKET_X0, 26.0, P.POCKET_Z + P.WIRE_D])
    depth = None
    for dx in np.arange(40, -1, -0.1):
        if ov(wd.translate([dx, 0, 0]), hook) > EPS:
            depth = dx
            break
    say(f"- window hook: wire in the pocket {'clear' if ov(wire, hook) <= EPS else 'CLASH'}; the wedge grips a 1.5 mm wire with "
        f"{P.POCKET_X0 + depth + 32 - 64:.1f} mm of it showing past the hook's end")
    say()


# ============================================================================ 9. printability
def check_print():
    import trimesh
    say("## 9. Printability, each STL as it sits on the bed")
    say("Downward-facing area not on the bed: flat ceilings must be bridges (both ends supported); "
        "steep is steeper than 45 degrees from vertical.")
    say()
    say("| File | Flat ceilings mm² | Steeper than 45° mm² | Largest flat ceiling span mm |")
    say("|---|---:|---:|---:|")
    for f in sorted((HERE.parent / "stl").glob("*.stl")):
        tm = trimesh.load(f)
        n = tm.face_normals
        zc = tm.triangles_center[:, 2]
        off_bed = zc > 0.05
        flat = off_bed & (n[:, 2] < -0.985)
        steep = off_bed & (n[:, 2] < -0.7071) & ~flat
        span = 0.0
        if flat.any():
            sub = tm.submesh([np.where(flat)[0]], append=True)
            for comp in sub.split(only_watertight=False):
                e = comp.extents
                span = max(span, min(e[0], e[1]))
        say(f"| {f.name} | {tm.area_faces[flat].sum():.0f} | {tm.area_faces[steep].sum():.0f} | {span:.1f} |")
    say()


# ============================================================================ main
if __name__ == "__main__":
    say("# Phase 1 fit and motion check")
    say()
    check_wagon()
    check_on_rail()
    statics = check_yard()
    check_tongue_and_spring()
    check_escapement()
    res = check_sweeps(statics)
    check_flap({k: v[1] for k, v in res.items()})
    check_ends()
    check_print()
    (HERE / "assembly_report.md").write_text("\n".join(LINES) + "\n")
