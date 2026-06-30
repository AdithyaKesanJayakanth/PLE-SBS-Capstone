"""Size the model to the room: given the highest point you can tie the wire to and the floor
length you have, print the span, drop, scale, pod speed and run time for each option.

Run:  .venv/bin/python scale_down/layout.py --tie 2.0 --floor 8.0
The physics is a pod on a straight wire with rolling resistance and air drag, integrated
at model scale; the full-size equivalent follows Froude scaling (time and speed by sqrt(s)).
"""
import argparse
import math

FULL_H, FULL_L = 45.0, 300.0      # worked example: 42 m access level into a 3 m pit, 300 m span
RAIL_HEAD = 0.06                   # rail head above the floor at the yard (m)
YARD = 1.15                        # handover + turnout + bays (m) at 1:50; scales with 50/s
MU, CDA, MASS, RHO = 0.03, 0.012, 0.30, 1.2   # model pod: printed wheels on printed pins, 0.3 kg with ballast


def run(span, drop):
    """Time to the end of the wire and arrival speed, straight wire, from rest."""
    L = math.hypot(span, drop)
    sin, cos = drop / L, span / L
    v, x, t, dt = 0.0, 0.0, 0.0, 0.002
    vmax = 0.0
    while x < L and t < 60:
        a = 9.81 * (sin - MU * cos) - 0.5 * RHO * CDA * v * v / MASS
        v = max(v + a * dt, 0.0)
        x += v * dt
        t += dt
        vmax = max(vmax, v)
        if v == 0.0 and t > 1.0:
            return math.inf, 0.0, 0.0
    return t, v, vmax


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tie", type=float, default=2.0, help="highest tie point above the floor, m")
    ap.add_argument("--floor", type=float, default=8.0, help="floor length available, m")
    a = ap.parse_args()
    drop_max = a.tie - RAIL_HEAD
    print(f"tie point {a.tie:.2f} m, floor {a.floor:.1f} m, rail head {RAIL_HEAD:.2f} m: usable drop {drop_max:.2f} m\n")
    print("scale   span    drop   wire   slope   yard   floor needed   ride   arrival   peak    full-size ride")
    print("        m       m      m             m      m              s      m/s       m/s     s (x sqrt s)")
    for s in (50, 40, 35, 30, 25, FULL_H / drop_max):
        span, drop = FULL_L / s, FULL_H / s
        yard = YARD * 50 / s
        need = span + yard + 0.5
        t, va, vp = run(span, drop)
        flag = "" if drop <= drop_max + 1e-9 and need <= a.floor else "   (does not fit)"
        print(f"1:{s:<5.1f} {span:5.2f}  {drop:5.2f}  {math.hypot(span, drop):5.2f}  1:{span / drop:4.1f}  {yard:5.2f}  {need:5.2f}          {t:5.2f}  {va:6.2f}    {vp:5.2f}    {t * math.sqrt(s):5.1f}{flag}")
    print("\nSame parts (1:50 yard and pods), using the height to sweep the slope at a fixed span:")
    span = min(6.0, a.floor - YARD - 0.5)
    print(f"  span {span:.1f} m (what the floor allows)")
    print("  drop   slope   full-size height   ride   arrival   peak")
    for drop in (0.5, 0.7, 0.9, 1.2, 1.5, drop_max):
        t, va, vp = run(span, drop)
        print(f"  {drop:4.2f}   1:{span / drop:4.1f}   {drop * 50:5.0f} m             {t:5.2f}  {va:6.2f}    {vp:5.2f}")
    print("\nStart gate about 0.3 m along the wire from the hook. Release the next pod when the one ahead has stopped in its bay.")


if __name__ == "__main__":
    main()
