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
    "trolley_plate_x6": "pegs reach the other plate and carry shoulders that set the 9.2 mm gap; axle holes print round (the plate lies flat); lips 0.5 mm clear of the web; 3.6 thick with 0.4 bosses to suit 0.2 mm layers",
    "pannier_x6": "new: one part for both sides, clamped by the axle pins, floor 12 mm above the strip; arm spacing for the 9.2 mm plate gap",
    "axle_pin_x6": "longer (28.4 mm shank) to pass through pannier, plate, wheel, plate, pannier; snap bump 0.7 mm clear",
    "turnout_base_x1": "new layout: lane spacing, pegs for the rocker bridge, gantry posts with 3.6 mm snap mouths, wire groove underneath; the entry rail's end lets the tongue slide under",
    "tongue_x1": "new: ring of four teeth and the spring tab",
    "rocker_bridge_x1": "new: carries the rocker over the tooth ring; separate so the tongue can be fitted first; beams 2.5 mm over the teeth, sliced with supports",
    "rocker_x1": "new: escapement rocker with a 26 mm coin cup", "rocker_pin_x1": "new", "bias_spring_x1": "new leaf spring",
    "flap_x1": "new trigger flap with a 16 mm crank", "gantry_axle_x1": "new",
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


SETS = {
    1: ("Set 1: wagon, points and handover", ["trolley_plate_x6", "pannier_x6", "axle_pin_x6", "turnout_base_x1", "tongue_x1", "rocker_bridge_x1",
                                              "rocker_x1", "rocker_pin_x1", "bias_spring_x1", "flap_x1", "gantry_axle_x1", "handover_x1"]),
    2: ("Set 2: bays, window hook and start gate", ["window_hook_x1", "brake_comb_190_x3", "chain_bed_190_x3", "sled_x3", "bumper_x3", "start_gate_x1", "gate_lever_x1"]),
}


def table(rows, names, with_set=False):
    g = t = n = 0
    lines = ["| # | File | Qty | Filament | Colour | g | Time | Why it changed |", "|---:|---|---:|---|---|---:|---|---|"]
    for i, k in enumerate(names, 1):
        r = rows[k]
        g += float(r["grams_total"]); t += secs(r["time_total"]); n += int(r["qty"])
        lines.append(f"| {i} | {k} | {r['qty']} | {r['material']} | {r['colour']} | {float(r['grams_total']):.1f} | {r['time_total']} | {WHY[k]} |")
    lines.append(f"| | **Total** | **{n}** | | | **{g:.0f}** | **{t // 3600}h {t % 3600 // 60:02d}m** | |")
    return lines, n, g, t


def spools(rows, names):
    c = {}
    for k in names:
        key = (rows[k]["material"], rows[k]["colour"])
        c[key] = c.get(key, 0) + float(rows[k]["grams_total"])
    return ["| Filament | Colour | g |", "|---|---|---:|"] + [f"| {m} | {col} | {v:.0f} |" for (m, col), v in sorted(c.items(), key=lambda kv: -kv[1])]


KEEP_MD = ["## Keep these from the version-1 print (identical geometry, do not reprint)", "", "| Keep | Used as |", "|---|---|"] + \
          [f"| {v} | {k} |" for k, v in REUSE.items()] + ["",
          "Set aside, no longer used: indexer, star arms, the two v1 pannier types, v1 trolley plates, axle pins, start gates, gate levers, block marker flag, "
          "handover, turnout plate, tongue, combs, chain beds, bumpers and window hook."]


def main():
    rows = {r["file"][:-4]: r for r in csv.DictReader(open(PK / "index.csv")) if r["phase"] == "1"}
    assert set(WHY) | set(REUSE) == set(rows), set(rows) ^ (set(WHY) | set(REUSE))
    assert set(SETS[1][1]) | set(SETS[2][1]) == set(WHY)
    if R.exists():
        shutil.rmtree(R)
    R.mkdir(parents=True)
    for num, (title, names) in SETS.items():
        d = R / f"set{num}"
        (d / "stl").mkdir(parents=True)
        (d / "sliced_p1s").mkdir()
        for k in names:
            shutil.copy(P1 / "stl" / f"{k}.stl", d / "stl")
            shutil.copy(P1 / "sliced_p1s" / f"{k}.gcode.3mf", d / "sliced_p1s")
        lines, n, g, t = table(rows, names)
        md = [f"# Phase 1 version 2, {title}", "",
              f"{len(names)} files, {n} pieces, {g:.0f} g, {t // 3600}h {t % 3600 // 60:02d}m of printing. Every file is in `stl/` (print orientation) and "
              "`sliced_p1s/` (Bambu Lab P1S, 0.4 mm nozzle, quantity already on the plate). Pictures and details of every part: `phase1_reprint_v2_set{0}_parts.pdf`.".format(num), ""]
        if num == 1:
            md += ["Print this set first. Build one wagon with your existing wheels and roll it on an existing lead rail before printing the rest.", ""]
        else:
            md += ["Print this set once set 1 is assembled and the wagon rolls. These parts are the bays, the wire's top end and the start gate.", ""]
        md += ["## Print these", ""] + lines + ["", "## Filament", ""] + spools(rows, names) + [""] + KEEP_MD
        (d / "README.md").write_text("\n".join(md) + "\n")
        print(f"set {num}: {len(names)} files, {n} pieces, {g:.0f} g, {t // 3600}h {t % 3600 // 60:02d}m")
    # top-level summary, both sets
    all_names = SETS[1][1] + SETS[2][1]
    lines, n, g, t = table(rows, all_names)
    md = ["# Phase 1 version 2: what to print now", "",
          "The version-1 parts printed on 27 June 2026 did not fit. Version 2 was checked part against part in its working position, along every "
          "assembly path and through a run of three wagons (`../../check/assembly_report.md`, `../../assembly/path_check_report.md`), and again in "
          "FreeCAD (`../../check/freecad_report.md`, `../../assembly/freecad_motion_report.md`). Step-by-step pictures and animations: `../../assembly/`.", "",
          f"The reprint is split in two: **set 1** (`set1/`, parts 1 to {len(SETS[1][1])}: wagon, points, handover) and **set 2** (`set2/`, parts "
          f"{len(SETS[1][1]) + 1} to {len(all_names)}: bays, window hook, start gate). Each folder has its own STLs, sliced files, README and parts PDF; "
          "the zips are `../../phase1_reprint_v2_set1.zip` and `..._set2.zip`.", "",
          f"## Print these ({len(all_names)} files in two sets)", ""] + lines + ["", "## Filament, both sets", ""] + spools(rows, all_names) + [""] + KEEP_MD
    (R / "README.md").write_text("\n".join(md) + "\n")
    print("both:", n, "pieces", round(g), "g", f"{t // 3600}h {t % 3600 // 60:02d}m")


if __name__ == "__main__":
    main()
