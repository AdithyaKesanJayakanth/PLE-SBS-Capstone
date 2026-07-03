"""The print pack: for each phase, every STL, a dimensioned PNG per part, and a sliced
Bambu Lab P1S project (.gcode.3mf) per part with the right quantity on the plate, plus an
index with the exact filament grams and print time reported by the slicer.

Run:  .venv/bin/python scale_down/make_print_pack.py           (needs OrcaSlicer in /Applications)
      .venv/bin/python scale_down/make_print_pack.py --no-slice  (sheets and STLs only)

Output: scale_down/print_pack/phase1/{stl,sheets,sliced_p1s}/..., phase2/..., index.csv, README.md
"""
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection

HERE = Path(__file__).resolve().parent
PACK = HERE / "print_pack"
ORCA = Path("/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer")
PROFILES = Path("/Applications/OrcaSlicer.app/Contents/Resources/profiles/BBL")
INK, GRAPHITE, FILL = "#18283a", "#56636f", (0.55, 0.68, 0.80)
NO_SLICE = "--no-slice" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]   # part names: rebuild just these, keep the rest

# Per-part print settings. base: "std" (0.20 mm) or "fine" (0.12 mm). Keys are OrcaSlicer process keys.
MECH = dict(base="fine", wall_loops="4", sparse_infill_density="100%", elefant_foot_compensation="0.15", brim_type="outer_only", brim_width="3")
FLEX = dict(base="fine", wall_loops="4", sparse_infill_density="25%", elefant_foot_compensation="0.15", brim_type="outer_only", brim_width="3")
RAIL = dict(base="std", wall_loops="5", sparse_infill_density="25%", brim_type="no_brim")
BODY = dict(base="std", wall_loops="4", sparse_infill_density="25%", brim_type="outer_only", brim_width="3")
SUPPORTED = dict(BODY, enable_support="1", support_type="tree(auto)")
SHELL = dict(base="std", wall_loops="4", sparse_infill_density="0%", brim_type="outer_only", brim_width="5")
LATTICE = dict(base="std", wall_loops="3", sparse_infill_density="15%", brim_type="outer_only", brim_width="5")
TILE = dict(base="std", wall_loops="3", sparse_infill_density="15%", brim_type="no_brim")

SETTINGS = {
    # phase 1
    "wheel_x6": MECH, "axle_pin_x6": MECH, "gate_key_x1": MECH, "gate_pin_x1": MECH, "wedge_x1": MECH, "rocker_pin_x1": MECH, "gantry_axle_x1": MECH,
    "chain_11_links_x3": dict(FLEX, sparse_infill_density="100%", brim_type="no_brim"), "bias_spring_x1": dict(FLEX, sparse_infill_density="100%"),
    "trolley_plate_x6": BODY, "pannier_x6": BODY, "rocker_x1": dict(BODY, base="fine"), "flap_x1": BODY, "sled_x3": BODY,
    "rocker_bridge_x1": SUPPORTED,
    "turnout_base_x1": RAIL, "tongue_x1": RAIL, "handover_x1": RAIL,
    "lead_rail_230_x3": RAIL, "brake_comb_190_x3": RAIL, "chain_bed_190_x3": RAIL,
    "bumper_x3": FLEX, "window_hook_x1": BODY, "start_gate_x1": BODY, "gate_lever_x1": BODY,
    # phase 2
    "core_segment_x4": SHELL, "capsule_x1": SHELL, "booster_lower_x2": SHELL, "booster_upper_x2": SHELL, "booster_strut_x4": MECH,
    "tower_section_x4": LATTICE, "tower_crown_x1": LATTICE, "arm_bracket_x1": BODY, "access_arm_x1": BODY, "arm_pin_x1": MECH,
    "wire_saddle_x1": BODY, "launch_mount_x1": LATTICE, "platform_tile_x4": TILE,
    "fit_coupon_x1": MECH,
}
# parts whose modelled orientation is not the print orientation: rotation about x in degrees
FLIP = {"platform_tile_x4": 180}
FILAMENT = {"PLA": "Bambu PLA Basic @BBL X1C", "PETG": "Bambu PETG HF @BBL X1C"}
COLOUR1 = {"Cobalt Blue": ["trolley_plate_x6", "wheel_x6", "pannier_x6"],
           "Orange": ["tongue_x1", "rocker_x1", "rocker_pin_x1", "bias_spring_x1", "flap_x1", "gantry_axle_x1", "bumper_x3", "axle_pin_x6",
                      "wedge_x1", "window_hook_x1", "gate_key_x1", "gate_pin_x1", "fit_coupon_x1"]}
PHASE1_COLOUR = {n: c for c, names in COLOUR1.items() for n in names}


# ---- OrcaSlicer profiles: resolve the "inherits" chain so density and temperatures come through
def find_profile(name):
    for sub in ("machine", "process", "filament"):
        p = PROFILES / sub / f"{name}.json"
        if p.exists():
            return p
    raise FileNotFoundError(name)


def resolve(name):
    d = json.loads(find_profile(name).read_text())
    parent = d.pop("inherits", None)
    if parent:
        base = resolve(parent)
        base.update(d)
        d = base
    return d


def write_profile(d, path, **overrides):
    d = dict(d)
    d.update(overrides)
    d.pop("inherits", None)
    path.write_text(json.dumps(d, indent=1))
    return path


# ---- part sheets ---------------------------------------------------------------------
def view(ax, tm, axes, light, title):
    v, n = tm.vertices, tm.face_normals
    depth = ({0, 1, 2} - set(axes)).pop()
    order = np.argsort(v[tm.faces].mean(axis=1)[:, depth] * light)
    faces = tm.faces[order]
    shade = np.clip(0.45 + 0.55 * np.abs(n[order] @ np.eye(3)[depth]), 0, 1)
    ax.add_collection(PolyCollection(v[faces][:, :, axes], facecolors=[(FILL[0] * s, FILL[1] * s, FILL[2] * s) for s in shade], edgecolors="none"))
    lo, hi = v[:, axes].min(axis=0), v[:, axes].max(axis=0)
    pad = 0.12 * max(hi - lo) + 4
    ax.set_xlim(lo[0] - pad, hi[0] + pad); ax.set_ylim(lo[1] - pad - 0.1 * max(hi - lo), hi[1] + pad)
    ax.set_aspect("equal"); ax.axis("off")
    names, (w, h) = "xyz", hi - lo
    ax.annotate("", (lo[0], lo[1] - pad * 0.55), (hi[0], lo[1] - pad * 0.55), arrowprops=dict(arrowstyle="<->", lw=0.7, color=GRAPHITE))
    ax.text((lo[0] + hi[0]) / 2, lo[1] - pad * 0.55 - 0.03 * max(w, h) - 2, f"{names[axes[0]]} {w:.1f}", ha="center", va="top", fontsize=8, color=GRAPHITE)
    ax.annotate("", (hi[0] + pad * 0.5, lo[1]), (hi[0] + pad * 0.5, hi[1]), arrowprops=dict(arrowstyle="<->", lw=0.7, color=GRAPHITE))
    ax.text(hi[0] + pad * 0.55, (lo[1] + hi[1]) / 2, f"{names[axes[1]]} {h:.1f}", ha="left", va="center", fontsize=8, color=GRAPHITE, rotation=90)
    ax.set_title(title, fontsize=9, color=INK)


def sheet(tm, png, title):
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.6))
    view(axs[0], tm, (0, 2), -1, "front (x–z)")
    view(axs[1], tm, (1, 2), 1, "side (y–z)")
    view(axs[2], tm, (0, 1), 1, "top (x–y), print orientation")
    fig.suptitle(title, fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    plt.close(fig)


# ---- slicing ---------------------------------------------------------------------------
def slice_part(stl, qty, material, settings, out_3mf, work):
    base = "0.12mm Fine @BBL X1C" if settings["base"] == "fine" else "0.20mm Standard @BBL X1C"
    over = {k: v for k, v in settings.items() if k != "base"}
    over["curr_bed_type"] = "Textured PEI Plate"
    machine = write_profile(resolve("Bambu Lab P1S 0.4 nozzle"), work / "machine.json")
    process = write_profile(resolve(base), work / "process.json", **over)
    fil = resolve(FILAMENT[material])
    filament = write_profile(fil, work / "filament.json")
    density = float(fil["filament_density"][0])
    outdir = work / "out"
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir()
    cmd = [str(ORCA), "--load-settings", f"{machine};{process}", "--load-filaments", str(filament),
           "--arrange", "1", "--orient", "0", "--slice", "0", "--export-3mf", "part.3mf", "--outputdir", str(outdir)] + [str(stl)] * qty
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    gcodes = sorted(outdir.glob("plate_*.gcode"))
    if not gcodes:
        return None, f"slicer gave no gcode (rc {r.returncode}): {r.stderr[-300:]}"
    cm3, secs = 0.0, 0
    for g in gcodes:
        txt = g.read_text(errors="ignore")
        m = re.search(r"; filament used \[cm3\] = ([\d.]+)", txt)
        cm3 += float(m.group(1)) if m else 0.0
        t = re.search(r"; model printing time: ([^;]+); total estimated time: ([^\n]+)", txt)
        if t:
            secs += parse_time(t.group(2))
        else:
            t2 = re.search(r"; estimated printing time \(normal mode\) = ([^\n]+)", txt)
            secs += parse_time(t2.group(1)) if t2 else 0
    if secs == 0:
        with zipfile.ZipFile(outdir / "part.3mf") as z:
            info = z.read("Metadata/slice_info.config").decode()
        secs = sum(int(x) for x in re.findall(r'key="prediction" value="(\d+)"', info))
    shutil.move(outdir / "part.3mf", out_3mf)
    return dict(plates=len(gcodes), cm3=cm3, grams=cm3 * density, seconds=secs, density=density), ""


def parse_time(s):
    secs = 0
    for val, unit in re.findall(r"(\d+)\s*([dhms])", s):
        secs += int(val) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[unit]
    return secs


def hms(secs):
    h, m = divmod(int(secs) // 60, 60)
    return f"{h}h {m:02d}m"


# ---- main --------------------------------------------------------------------------------
def main():
    old = {}
    if ONLY and (PACK / "index.csv").exists():
        old = {r["file"]: r for r in csv.DictReader(open(PACK / "index.csv"))}
        for r in old.values():
            r["phase"] = int(r["phase"]); r["seconds"] = parse_time(r["time_total"]) if r["time_total"] else 0
    elif PACK.exists():
        shutil.rmtree(PACK)
    rows = []
    work = Path(tempfile.mkdtemp(prefix="plesbs-slice-"))
    for phase, folder, csvname in [(1, HERE / "stl", HERE / "parts.csv"), (2, HERE / "stl_phase2", HERE / "pad_parts.csv")]:
        meta = {r["file"]: r for r in csv.DictReader(open(csvname))}
        pdir = PACK / f"phase{phase}"
        for sub in ("stl", "sheets", "sliced_p1s"):
            (pdir / sub).mkdir(parents=True, exist_ok=True)
        for stl in sorted(folder.glob("*.stl")):
            name = stl.stem
            if ONLY and name not in ONLY:
                if stl.name in old:
                    rows.append(old[stl.name])
                continue
            m = meta[stl.name]
            qty, material, colour = int(m["qty"]), m["material"], m.get("colour") or PHASE1_COLOUR.get(stl.stem, "Light Grey")
            tm = trimesh.load(stl)
            if name in FLIP:
                tm.apply_transform(trimesh.transformations.rotation_matrix(np.radians(FLIP[name]), [1, 0, 0]))
            tm.apply_translation(-tm.bounds[0])          # sit on z = 0 in print orientation
            dst = pdir / "stl" / stl.name
            tm.export(dst)
            ext = tm.extents
            sheet(tm, pdir / "sheets" / f"{name}.png", f"{name}   ·   {ext[0]:.1f} × {ext[1]:.1f} × {ext[2]:.1f} mm   ·   phase {phase}, qty {qty}, {material} {colour}")
            row = dict(phase=phase, file=stl.name, qty=qty, material=material, colour=colour, x=f"{ext[0]:.1f}", y=f"{ext[1]:.1f}", z=f"{ext[2]:.1f}",
                       layer="0.12" if SETTINGS.get(name, BODY)["base"] == "fine" else "0.20", plates="", grams_each="", grams_total="", time_total="", note=m.get("note", ""))
            if not NO_SLICE:
                res, err = slice_part(dst, qty, material, SETTINGS.get(name, BODY), pdir / "sliced_p1s" / f"{name}.gcode.3mf", work)
                copies = qty
                if not res and qty > 1:   # the quantity does not fit one plate: slice one, print it qty times
                    res, err = slice_part(dst, 1, material, SETTINGS.get(name, BODY), pdir / "sliced_p1s" / f"{name}.gcode.3mf", work)
                    copies = 1
                if res:
                    scale = qty / copies
                    row.update(plates=f"{res['plates']} x {qty}" if copies == 1 and qty > 1 else res["plates"], grams_each=f"{res['grams'] / copies:.1f}",
                               grams_total=f"{res['grams'] * scale:.1f}", time_total=hms(res["seconds"] * scale), seconds=res["seconds"] * scale,
                               note=(m.get("note", "") + (f" (sliced as one piece: print the file {qty} times)" if copies == 1 and qty > 1 else "")))
                    print(f"phase {phase} {name:26s} x{qty:<2d} {res['grams']:7.1f} g  {hms(res['seconds'])}  plates {res['plates']}")
                else:
                    row.update(note=f"NOT SLICED: {err}")
                    print(f"phase {phase} {name:26s} FAILED {err}")
            rows.append(row)
    with open(PACK / "index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["phase", "file", "qty", "material", "colour", "x", "y", "z", "layer", "plates", "grams_each", "grams_total", "time_total", "note"], extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    write_readme(rows)
    shutil.rmtree(work, ignore_errors=True)
    print("pack written to", PACK)


def write_readme(rows):
    md = ["# PLE-SBS print pack for the Bambu Lab P1S (0.4 mm nozzle)", "",
          "Each phase folder has `stl/` (every part, already in its print orientation), `sheets/` (one PNG per part with front, side and top views and the bounding dimensions in mm) and `sliced_p1s/` (one `.gcode.3mf` per part, sliced with OrcaSlicer using the Bambu Lab P1S 0.4 nozzle profile, Bambu PLA Basic or PETG HF, with the quantity already arranged on the plate; open in Bambu Studio or send to the printer).",
          "Grams and times are the slicer's own figures: filament volume times the filament's density, and the slicer's time estimate.", ""]
    for phase in (1, 2):
        sel = [r for r in rows if r["phase"] == phase]
        md += [f"## Phase {phase}", "", "| File | Qty | Material | Colour | Size (mm) | Layer | Plates | g each | g total | Time |", "|---|---:|---|---|---|---|---:|---:|---:|---|"]
        for r in sel:
            md.append(f"| {r['file']} | {r['qty']} | {r['material']} | {r['colour']} | {r['x']} × {r['y']} × {r['z']} | {r['layer']} | {r['plates']} | {r['grams_each']} | {r['grams_total']} | {r['time_total']} |")
        g = sum(float(r["grams_total"] or 0) for r in sel)
        s = sum(r.get("seconds", 0) for r in sel)
        md += ["", f"Phase {phase} total: **{g:.0f} g**, {hms(s)} of printing.", ""]
    md += ["## Filament totals", "", "| Material | Colour | Phase 1 g | Phase 2 g | Total g |", "|---|---|---:|---:|---:|"]
    combos = sorted({(r["material"], r["colour"]) for r in rows})
    tot = 0
    for mat, col in combos:
        g1 = sum(float(r["grams_total"] or 0) for r in rows if r["phase"] == 1 and (r["material"], r["colour"]) == (mat, col))
        g2 = sum(float(r["grams_total"] or 0) for r in rows if r["phase"] == 2 and (r["material"], r["colour"]) == (mat, col))
        tot += g1 + g2
        md.append(f"| {mat} | {col} | {g1:.0f} | {g2:.0f} | {g1 + g2:.0f} |")
    md += ["", f"Grand total **{tot:.0f} g** of filament through the nozzle, both phases, excluding purge, brims already included, failures not included.", ""]
    (PACK / "README.md").write_text("\n".join(md))


if __name__ == "__main__":
    main()
