"""Write print_pack/parts_table.md (one table per phase) from print_pack/index.csv.

Run:  .venv/bin/python scale_down/make_parts_table.py
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = {
    1: ["fit_coupon_x1", "wheel_x6", "axle_pin_x6", "trolley_plate_x6", "pannier_x6", "turnout_base_x1", "tongue_x1", "rocker_x1",
        "rocker_pin_x1", "bias_spring_x1", "flap_x1", "gantry_axle_x1", "handover_x1", "window_hook_x1", "wedge_x1", "lead_rail_230_x3",
        "brake_comb_190_x3", "chain_bed_190_x3", "chain_11_links_x3", "sled_x3", "bumper_x3", "start_gate_x1", "gate_lever_x1", "gate_key_x1", "gate_pin_x1"],
    2: ["core_segment_x4", "capsule_x1", "booster_lower_x2", "booster_upper_x2", "booster_strut_x4", "tower_section_x4", "tower_crown_x1",
        "arm_bracket_x1", "access_arm_x1", "arm_pin_x1", "wire_saddle_x1", "launch_mount_x1", "platform_tile_x4"],
}
TITLE = {1: "Phase 1: wire, pods and switch yard", 2: "Phase 2: launch pad and rocket"}
FIL = {"PLA": "PLA Basic", "PETG": "PETG HF"}


def secs(t):
    h, m = re.match(r"(\d+)h (\d+)m", t).groups()
    return int(h) * 3600 + int(m) * 60


def hm(s):
    return f"{s // 3600}h {s % 3600 // 60:02d}m"


def main():
    by = {r["file"].replace(".stl", ""): r for r in csv.DictReader(open(HERE / "print_pack" / "index.csv"))}
    out = ["# All printed parts, by phase", "",
           "Plate numbers are a suggested print order within each phase. A file sliced as one piece but needed four times takes four plates. Dimensions are the piece as it sits on the bed, in mm. Weights and times are the slicer's (OrcaSlicer, Bambu Lab P1S 0.4 mm profiles); the time is for all the pieces in that row.", ""]
    G, S, N, PL = 0.0, 0, 0, 0
    for ph in (1, 2):
        out += [f"## {TITLE[ph]}", "", "| Plate | Part | Qty | Dimensions (mm) | Filament | Colour | g each | g total | Time |", "|---|---|---:|---|---|---|---:|---:|---|"]
        plate, g, s, n, col = 0, 0.0, 0, 0, {}
        for name in ORDER[ph]:
            r = by[name]
            k = int(str(r["plates"]).split()[0]) if r["plates"] else 1
            nums = f"P{ph}-{plate + 1:02d}" if k == 1 else f"P{ph}-{plate + 1:02d} to P{ph}-{plate + k:02d}"
            plate += k
            gt = float(r["grams_total"]); g += gt; s += secs(r["time_total"]); n += int(r["qty"])
            key = (FIL[r["material"]], r["colour"]); col[key] = col.get(key, 0) + gt
            out.append(f"| {nums} | {name} | {r['qty']} | {r['x']} × {r['y']} × {r['z']} | {FIL[r['material']]} | {r['colour']} | {r['grams_each']} | {gt:.1f} | {r['time_total']} |")
        out += [f"| | **Phase {ph} total** | **{n}** | | | | | **{g:,.0f}** | **{hm(s)}** |", "",
                "| Filament | Colour | g |", "|---|---|---:|"] + [f"| {f} | {c} | {v:,.0f} |" for (f, c), v in sorted(col.items())] + ["",
                f"{len(ORDER[ph])} part files, {n} pieces, {plate} plates.", ""]
        G += g; S += s; N += n; PL += plate
    out += ["## Both phases", "", f"{N} pieces on {PL} plates, **{G:,.0f} g** of filament, about **{hm(S)}** of printing."]
    (HERE / "print_pack" / "parts_table.md").write_text("\n".join(out) + "\n")
    print(f"{N} pieces, {PL} plates, {G:.0f} g, {hm(S)}")


if __name__ == "__main__":
    main()
