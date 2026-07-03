"""One video of the whole of phase 1: assembly step by step, fitting the moving parts, each
moving part through its positions, and the three-wagon run, with title cards and the check
results at the end. Built from the composed frames that make_media.py writes.

Run after make_media.py:  .venv/bin/python scale_down/assembly/make_full_video.py
-> scale_down/assembly/video/phase1_full.mp4
"""
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from make_media import BUILD, F_CAP, F_SMALL, F_TITLE, GREY, INK, ACCENT, VIDEO, font

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
W, H = 1920, 1240
CARDS = HERE / "build" / "cards"
F_BIG, F_H2, F_B = font(64, True), font(38, True), font(32)

SECTIONS = [
    ("wagon", "1. Wagon assembly", "Two identical plates, two wheels, two identical panniers, two printed axle pins. No screws: the pins snap through.",
     ["Lay the parts flat on the table in a stack: pannier, plate, wheels, plate, pannier.",
      "Push each axle pin down through all five until its split end clicks out.",
      "The peg shoulders set the plate gap; the wheels then have 0.2 mm of side play."]),
    ("yard", "2. Yard assembly", "Eighteen steps from the handover to the wire. Always lower the piece with the slot onto the piece with the tab.",
     ["The tongue slides under the end of the entry rail onto its post.",
      "The rocker bridge drops over the ring of teeth onto four pegs.",
      "Thread from the flap's crank to the rocker's outer arm: tight to 1.5 mm slack all work."]),
    ("ends", "3. Wire ends and start gate", "Three turns round the hook's post and a wedge at the window; a clamp, a key and a hook lever at the gate.",
     ["The gate hangs on the wire by itself; the key locks it.",
      "The lever's hook drops in front of the wagon's rear spacer peg.",
      "Lift the lever about 20 degrees to release."]),
    ("moving", "4. Moving parts, checked in every position", "Tongue at each bay, rocker tipped and at rest, flap through its swing.",
     ["Each position was measured against every neighbouring part.",
      "At the mid-tilt both fingers are inside the tooth band, so the tongue can never run free."]),
    ("run", "5. Three wagons", "Down the wire, onto the rail at the same height, across the points, into bays R, C and L.",
     ["The flap lifts, the thread tips the rocker, the spring steps the tongue one lane.",
      "The tongue only moves after the wagon's rear wheel has left it.",
      "Comb, sled and chain, then the bumper, stop each wagon."]),
]


def card(name, title, sub, bullets, big=False):
    CARDS.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill=ACCENT)
    d.text((110, 150), "PLE-SBS scale model 1:50 · phase 1", font=F_TITLE, fill=ACCENT)
    d.text((110, 215), title, font=F_BIG, fill=INK)
    y = 330
    for ln in wrap(d, sub, F_H2, W - 220):
        d.text((110, y), ln, font=F_H2, fill=GREY)
        y += 52
    y += 40
    for b in bullets:
        for i, ln in enumerate(wrap(d, b, F_B, W - 300)):
            d.text((150 if i == 0 else 190, y), ("•  " if i == 0 else "") + ln, font=F_B, fill=INK)
            y += 48
        y += 14
    p = CARDS / f"{name}.png"
    im.save(p)
    return p


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


def pad(p):
    """Composed frame onto the common canvas, cached."""
    out = CARDS / ("f_" + p.name)
    if not out.exists():
        im = Image.open(p).convert("RGB")
        if im.width > W or im.height > H:
            im.thumbnail((W, H))
        c = Image.new("RGB", (W, H), "white")
        c.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
        c.save(out)
    return out


def facts():
    def grab(path, pat, default="?"):
        t = Path(path).read_text() if Path(path).exists() else ""
        m = re.search(pat, t)
        return m.group(1) if m else default
    fit = Path(ROOT / "check" / "assembly_report.md").read_text()
    pc = Path(HERE / "path_check_report.md").read_text()
    paths = [l for l in pc.splitlines() if l.startswith("- ") and (": clear" in l or "CLASH" in l)]
    return [
        f"Fit check, every part in its working position: {len(re.findall('CLASH|JAM|FAILED', fit))} clashes, every running fit 0.2 mm per side",
        f"Assembly paths replayed step by step: {sum(': clear' in l for l in paths)} of {len(paths)} clear (snap fits excepted)",
        f"Three-wagon run: {sum('CLASH' in l for l in pc.splitlines() if l.startswith('- CLASH'))} clashes; the tongue steps R, C, L",
        f"FreeCAD, assembled yard: {grab(ROOT / 'check' / 'freecad_report.md', r'more than 0.05 mm³: (\d+)')} of {grab(ROOT / 'check' / 'freecad_report.md', r'(\d+) with overlapping')} pairs overlapping",
        f"FreeCAD, {grab(HERE / 'freecad_motion_report.md', r'(\d+) frames replayed')} moving frames: {grab(HERE / 'freecad_motion_report.md', r'Unexplained overlaps above 0.05 mm³: (\d+)')} unexplained overlaps",
        "Not checked by any of this: forces, friction, bounce. First runs: full drop, empty pods, then add ballast.",
    ]


def main():
    sb = json.load(open(BUILD / "storyboard.json"))
    frames = sb["frames"]
    fps = {"run": 18, "wagon": 15, "yard": 15, "ends": 15, "moving": 1}
    lst = BUILD / "full_list.txt"
    entries = []
    entries.append((card("title", "Phase 1: assembly, fitting and motion", "Every part placed and moved in FreeCAD before printing. Screenshots and animation are renders of the actual part files.",
                         ["1. Wagon assembly   2. Yard assembly   3. Wire ends and start gate", "4. Moving parts in every position   5. Three wagons down the wire"]), 6.0))
    for seq, title, sub, bullets in SECTIONS:
        entries.append((card(seq, title, sub, bullets), 7.0))
        for i, fr in enumerate(frames):
            if fr["seq"] != seq:
                continue
            p = BUILD / "composed" / f"{seq}_{i:05d}.png"
            if not p.exists():
                continue
            hold = fr.get("hold", 1) / fps[seq]
            if fr.get("still"):
                hold = max(hold, 3.5 if seq != "run" else 2.5)
            if seq == "moving":
                hold = 4.0
            entries.append((pad(p), hold))
    entries.append((card("end", "What was checked", "All five checks on the final part files (the reports are in scale_down/check and scale_down/assembly).", facts()), 12.0))
    with open(lst, "w") as f:
        for p, dur in entries:
            f.write(f"file '{p}'\nduration {dur:.4f}\n")
        f.write(f"file '{entries[-1][0]}'\n")
    out = VIDEO / "phase1_full.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", "format=yuv420p",
                    "-c:v", "libx264", "-crf", "23", "-preset", "slow", "-r", "30", "-movflags", "+faststart", str(out)], check=True)
    total = sum(d for _, d in entries)
    print(f"wrote {out.name}: {len(entries)} frames, {total / 60:.1f} min, {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
