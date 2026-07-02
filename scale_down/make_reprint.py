"""Write print_pack/phase1/reprint_v2/: the phase-1 files to print for anyone who printed
version 1 (27 June 2026), with a README listing what to keep from that print.

Run after make_print_pack.py:  .venv/bin/python scale_down/make_reprint.py
"""
import csv
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PK = HERE / "print_pack"
P1 = PK / "phase1"
R = P1 / "reprint_v2"

REUSE = {"fit_coupon_x1": "fit_coupon_x1", "wheel_x6": "wheel_x6", "wedge_x1": "wedge_x2 (you have 2, need 1)",
         "lead_rail_230_x3": "lead_rail_230_x3", "chain_11_links_x3": "chain_11_links_x3",
         "gate_key_x1": "gate_key_x4 (you have 4, need 1)", "gate_pin_x1": "gate_pin_x3 (you have 3, need 1)"}
WHY = {
    "trolley_plate_x6": "pegs now reach the other plate; axle holes print round (the plate lies flat); short guide lips",
    "pannier_x6": "new: one part for both sides, clamped by the axle pins, floor 12 mm above the strip",
    "axle_pin_x6": "longer (28 mm shank) to pass through pannier, plate, wheel, plate, pannier",
    "turnout_base_x1": "new layout: lane spacing, pegs for the rocker bridge, gantry posts, wire groove underneath; the entry rail's end lets the tongue slide under",
    "tongue_x1": "new: ring of four teeth and the spring tab",
    "rocker_bridge_x1": "new: carries the rocker over the tooth ring; separate so the tongue can be fitted first",
    "rocker_x1": "new: escapement rocker with coin cup", "rocker_pin_x1": "new", "bias_spring_x1": "new leaf spring",
    "flap_x1": "new trigger flap with crank", "gantry_axle_x1": "new",
    "handover_x1": "the wire now dives through it and runs on under the yard; head height matches the wheel seat",
    "window_hook_x1": "pocket opens upward; rim prints without support",
    "brake_comb_190_x3": "v1 leaves stood 21.7 mm tall and would ram the baskets; v2 leaves reach 13.8 mm and end inside the segment",
    "chain_bed_190_x3": "trough runs to the end so the sled can reach the bumper; no stirrup ring",
    "sled_x3": "new: the left basket pushes it and the chain", "bumper_x3": "rail stub runs to the face plate; trough for the sled",
    "start_gate_x1": "v1 wire slot was 1 mm for a 1.5 mm wire and the key missed the wire; the slot now opens downward so the gate hangs on the wire",
    "gate_lever_x1": "new hook over the rear spacer peg",
}


def secs(t):
    h, m = re.match(r"(\d+)h (\d+)m", t).groups()
    return int(h) * 3600 + int(m) * 60


def main():
    rows = {r["file"][:-4]: r for r in csv.DictReader(open(PK / "index.csv")) if r["phase"] == "1"}
    assert set(WHY) | set(REUSE) == set(rows), set(rows) ^ (set(WHY) | set(REUSE))
    if R.exists():
        shutil.rmtree(R)
    (R / "stl").mkdir(parents=True)
    (R / "sliced_p1s").mkdir()
    g = t = n = 0
    lines = []
    for k in WHY:
        r = rows[k]
        shutil.copy(P1 / "stl" / f"{k}.stl", R / "stl")
        shutil.copy(P1 / "sliced_p1s" / f"{k}.gcode.3mf", R / "sliced_p1s")
        g += float(r["grams_total"]); t += secs(r["time_total"]); n += int(r["qty"])
        lines.append(f"| {k} | {r['qty']} | {r['material']} | {r['colour']} | {float(r['grams_total']):.1f} | {r['time_total']} | {WHY[k]} |")
    md = ["# Phase 1 version 2: what to print now", "",
          "The version-1 parts printed on 27 June 2026 did not fit. Version 2 was checked part against part in its working position, along every "
          "assembly path and through a run of three wagons (`../../check/assembly_report.md`, `../../assembly/path_check_report.md`), and again in "
          "FreeCAD (`../../check/freecad_report.md`, `../../assembly/freecad_motion_report.md`). Step-by-step pictures and animations: `../../assembly/`.", "",
          f"## Print these ({len(WHY)} files)", "", "| File | Qty | Filament | Colour | g | Time | Why it changed |", "|---|---:|---|---|---:|---|---|"] + lines + [
          f"| **Total** | **{n}** | | | **{g:.0f}** | **{t // 3600}h {t % 3600 // 60:02d}m** | |", "",
          "Every file is in `stl/` (print orientation) and `sliced_p1s/` (P1S, 0.4 mm nozzle, quantity already on the plate).", "",
          "## Keep these from the version-1 print (identical geometry, do not reprint)", "", "| Keep | Used as |", "|---|---|"] + \
         [f"| {v} | {k} |" for k, v in REUSE.items()] + ["",
          "Set aside, no longer used: indexer, star arms, the two v1 pannier types, v1 trolley plates, axle pins, start gates, gate levers, block marker flag, "
          "handover, turnout plate, tongue, combs, chain beds, bumpers and window hook."]
    (R / "README.md").write_text("\n".join(md) + "\n")
    print(n, "pieces", round(g), "g", f"{t // 3600}h {t % 3600 // 60:02d}m")


if __name__ == "__main__":
    main()
