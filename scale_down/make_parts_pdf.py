"""Phase-1 parts catalogue as a PDF: one picture of every part in its filament colour, with
quantity, filament type, colour, grams, print time, size on the bed, and whether it is in the
reprint set or kept from the first print.

Run after make_print_pack.py, make_reprint.py and freecad_part_renders.py:
  .venv/bin/python scale_down/make_parts_pdf.py             -> print_pack/phase1_parts.pdf (all 26 parts)
  .venv/bin/python scale_down/make_parts_pdf.py --set 1     -> print_pack/phase1_reprint_v2_set1_parts.pdf (wagon, points, handover)
  .venv/bin/python scale_down/make_parts_pdf.py --set 2     -> print_pack/phase1_reprint_v2_set2_parts.pdf (bays, hook, gate)
The set PDFs are also copied into print_pack/phase1/reprint_v2/setN/.
"""
import csv
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PK = HERE / "print_pack"
P1 = PK / "phase1"
REND = P1 / "renders"
W, H = 1754, 1240            # A4 landscape at 150 dpi
M = 70
INK, GREY, ACCENT, RULE = (24, 40, 58), (86, 99, 111), (200, 84, 26), (214, 221, 227)
SWATCH = {"Cobalt Blue": (0, 86, 184), "Light Grey": (205, 208, 212), "Orange": (250, 115, 25)}
ORDER = ["fit_coupon_x1", "wheel_x6", "axle_pin_x6", "trolley_plate_x6", "pannier_x6", "turnout_base_x1", "tongue_x1", "rocker_bridge_x1",
         "rocker_x1", "rocker_pin_x1", "bias_spring_x1", "flap_x1", "gantry_axle_x1", "handover_x1", "window_hook_x1", "wedge_x1",
         "lead_rail_230_x3", "brake_comb_190_x3", "chain_bed_190_x3", "chain_11_links_x3", "sled_x3", "bumper_x3", "start_gate_x1",
         "gate_lever_x1", "gate_key_x1", "gate_pin_x1"]
GROUP = {"fit_coupon_x1": "Test piece", "wheel_x6": "Wagon", "axle_pin_x6": "Wagon", "trolley_plate_x6": "Wagon", "pannier_x6": "Wagon",
         "turnout_base_x1": "Points", "tongue_x1": "Points", "rocker_bridge_x1": "Points", "rocker_x1": "Points", "rocker_pin_x1": "Points",
         "bias_spring_x1": "Points", "flap_x1": "Points", "gantry_axle_x1": "Points", "handover_x1": "Wire end", "window_hook_x1": "Wire end",
         "wedge_x1": "Wire end", "lead_rail_230_x3": "Bays", "brake_comb_190_x3": "Bays", "chain_bed_190_x3": "Bays", "chain_11_links_x3": "Bays",
         "sled_x3": "Bays", "bumper_x3": "Bays", "start_gate_x1": "Start gate", "gate_lever_x1": "Start gate", "gate_key_x1": "Start gate",
         "gate_pin_x1": "Start gate"}


def font(size, bold=False):
    for p in (["/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if bold else []) + ["/System/Library/Fonts/Supplemental/Arial.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_H1, F_H2, F_B, F_S, F_NUM = font(44, True), font(30, True), font(24), font(20), font(36, True)


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    return lines


def header(d, title, sub=None):
    d.rectangle([0, 0, W, 10], fill=ACCENT)
    d.text((M, 40), "PLE-SBS scale model 1:50 · phase 1 · version 2", font=F_S, fill=ACCENT)
    d.text((M, 70), title, font=F_H1, fill=INK)
    if sub:
        d.text((M, 128), sub, font=F_B, fill=GREY)
    d.line([(M, 170), (W - M, 170)], fill=RULE, width=2)


def footer(d, n):
    d.text((W - M - 60, H - 50), f"{n}", font=F_S, fill=GREY)
    d.text((M, H - 50), "reprint files, sliced for the P1S: print_pack/phase1/reprint_v2/", font=F_S, fill=GREY)


def load():
    rows = {r["file"][:-4]: r for r in csv.DictReader(open(PK / "index.csv")) if r["phase"] == "1"}
    notes = {r["file"][:-4]: r["note"] for r in csv.DictReader(open(HERE / "parts.csv"))}
    md = (P1 / "reprint_v2" / "README.md").read_text().splitlines()
    md = [l for l in md if not l.startswith("| # ")]
    status, keep_as = {}, {}
    mode = None
    for l in md:
        if l.startswith("## Print these"):
            mode = "print"
        elif l.startswith("## Keep"):
            mode = "keep"
        elif l.startswith("| ") and not l.startswith(("| File", "| Keep", "|---", "| **")):
            c = [x.strip() for x in l.strip("|").split("|")]
            if mode == "print":
                status[c[1]] = ("print", c[-1])
            elif mode == "keep":
                status[c[1]] = ("keep", c[0])
    return rows, notes, status


def part_block(page, d, y, name, r, note, st):
    """One part: picture left, facts right. Returns the height used."""
    hgt = 330
    img = Image.open(REND / f"{name}.png").convert("RGB")
    from PIL import ImageChops
    bb = ImageChops.difference(img, Image.new("RGB", img.size, "white")).getbbox()
    if bb:
        img = img.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), min(bb[2] + 20, img.width), min(bb[3] + 20, img.height)))
    img.thumbnail((440, hgt - 30))
    page.paste(img, (M + (460 - img.width) // 2, y + (hgt - 30 - img.height) // 2 + 10))
    x = M + 500
    kind, why = st
    tag = "PRINT" if kind == "print" else "KEEP from the first print"
    d.rectangle([x, y + 12, x + d.textlength(tag, font=F_S) + 24, y + 44], fill=ACCENT if kind == "print" else (44, 117, 72))
    d.text((x + 12, y + 16), tag, font=F_S, fill="white")
    d.text((x + d.textlength(tag, font=F_S) + 44, y + 12), GROUP[name], font=F_S, fill=GREY)
    d.text((x, y + 54), name, font=F_H2, fill=INK)
    sw = SWATCH.get(r["colour"], (150, 150, 150))
    d.rectangle([x, y + 108, x + 36, y + 144], fill=sw, outline=RULE)
    d.text((x + 50, y + 110), f"{r['material']} {r['colour']}", font=F_B, fill=INK)
    d.text((x + 50, y + 142), f"qty {r['qty']}   ·   {float(r['grams_total']):.1f} g   ·   {r['time_total']}   ·   {r['x']} × {r['y']} × {r['z']} mm on the bed   ·   {r['layer']} mm layers",
           font=F_S, fill=GREY)
    yy = y + 182
    for ln in wrap(d, note, F_S, W - x - M)[:2]:
        d.text((x, yy), ln, font=F_S, fill=INK)
        yy += 26
    if kind == "print":
        yy += 4
        for ln in wrap(d, "Why reprint: " + why, F_S, W - x - M)[:3]:
            d.text((x, yy), ln, font=F_S, fill=GREY)
            yy += 26
    else:
        d.text((x, yy + 4), f"Use your printed {why}.", font=F_S, fill=GREY)
    d.line([(M, y + hgt), (W - M, y + hgt)], fill=RULE, width=1)
    return hgt


def cover(rows, status, reprint_only=False, names=None, title=None, which=None):
    page = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(page)
    if reprint_only:
        header(d, title or "Phase 1 reprint set: the parts to print", "Version 2, checked in FreeCAD. Sliced files for the Bambu Lab P1S are in the same folder. The 7 parts from the first print that you keep are listed on the right.")
    else:
        header(d, "All phase-1 parts: what to print, what to keep", "26 part files, 57 pieces. The 19 marked PRINT make the reprint set; the 7 marked KEEP are unchanged from the first print.")
    pr = [n for n in (names or ORDER) if status[n][0] == "print"]
    kp = [n for n in ORDER if status[n][0] == "keep"]
    g = sum(float(rows[n]["grams_total"]) for n in pr)
    pcs = sum(int(rows[n]["qty"]) for n in pr)
    secs = 0
    for n in pr:
        h, m = re.match(r"(\d+)h (\d+)m", rows[n]["time_total"]).groups()
        secs += int(h) * 3600 + int(m) * 60
    y = 210
    for big, small in ((f"{len(pr)} files", "to print"), (f"{pcs} pieces", "on the bed"), (f"{g:.0f} g", "of filament"), (f"{secs // 3600}h {secs % 3600 // 60:02d}m", "of printing")):
        d.text((M + 60, y), big, font=F_NUM, fill=ACCENT)  # noqa
        d.text((M + 60, y + 44), small, font=F_S, fill=GREY)
        y += 100
    x0 = 560
    d.text((x0, 210), "Filament to have ready (reprint set)", font=F_H2, fill=INK)
    combos = {}
    for n in pr:
        k = (rows[n]["material"], rows[n]["colour"])
        combos[k] = combos.get(k, 0) + float(rows[n]["grams_total"])
    y = 260
    for (mat, col), gg in sorted(combos.items(), key=lambda kv: -kv[1]):
        d.rectangle([x0, y + 4, x0 + 28, y + 32], fill=SWATCH.get(col, (150, 150, 150)), outline=RULE)
        d.text((x0 + 44, y), f"{mat} {col}", font=F_B, fill=INK)
        d.text((x0 + 420, y), f"{gg:.0f} g  (buy with 20 % margin: {gg * 1.2:.0f} g)", font=F_B, fill=GREY)
        y += 42
    y += 20
    d.text((x0, y), "Keep from the first print", font=F_H2, fill=INK)
    y += 46
    for n in kp:
        d.text((x0, y), f"{n}:  use your printed {status[n][1]}", font=F_S, fill=INK)
        y += 30
    y += 20
    d.text((x0, y), "Print order", font=F_H2, fill=INK)
    y += 46
    order = {None: ["1. Set 1 first: wagon parts (plates, panniers, pins, about 4.7 h), then the points and the handover.",
                    "2. Build one wagon with your existing wheels and roll it on an existing lead rail; work the points by hand.",
                    "3. Set 2 when set 1 works: combs, chain beds, sleds, bumpers, window hook, start gate, lever."],
             1: ["1. Wagon parts first: plates, panniers, pins (about 4.7 h). Build one wagon with your existing wheels and roll it on a lead rail.",
                 "2. Then the points: turnout plate, tongue, rocker bridge (with supports), rocker, pins, spring, flap, axle; then the handover.",
                 "3. Work the points by hand before printing set 2."],
             2: ["1. Three each of comb, chain bed, sled and bumper; the sleds and bumpers can share plates with the small parts.",
                 "2. Window hook (PETG), start gate and lever.",
                 "3. Then rig the wire: hook at the window, handover on the floor, gate 0.3 m below the hook."]}
    for ln in order[which]:
        for l2 in wrap(d, ln, F_S, W - x0 - M):
            d.text((x0, y), l2, font=F_S, fill=INK)
            y += 28
    footer(d, 1)
    return page


def main():
    import sys
    from make_reprint import SETS
    which = int(sys.argv[sys.argv.index("--set") + 1]) if "--set" in sys.argv else None
    reprint_only = which is not None
    rows, notes, status = load()
    if which:
        title, names = SETS[which]
        title = f"Phase 1 reprint, {title[0].lower() + title[1:]}"
    else:
        title, names = None, list(ORDER)
    pages = [cover(rows, status, reprint_only, names, title, which)]
    per = 3
    for i in range(0, len(names), per):
        page = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(page)
        header(d, f"{'Reprint parts' if reprint_only else 'Parts'} {i + 1} to {min(i + per, len(names))} of {len(names)}")
        y = 190
        for name in names[i:i + per]:
            y += part_block(page, d, y, name, rows[name], notes[name], status[name])
        footer(d, len(pages) + 1)
        pages.append(page)
    out = PK / (f"phase1_reprint_v2_set{which}_parts.pdf" if which else "phase1_parts.pdf")
    pages[0].save(out, "PDF", resolution=150, save_all=True, append_images=pages[1:])
    shutil.copy(out, P1 / "reprint_v2" / (f"set{which}" if which else "") / out.name)
    print(f"wrote {out} ({len(pages)} pages, {out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
