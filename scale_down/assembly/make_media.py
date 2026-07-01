"""Turn the FreeCAD screenshots into captioned step images and animations.

Run after freecad_render.py:
  .venv/bin/python scale_down/assembly/make_media.py
-> scale_down/assembly/steps/*.png (one captioned image per assembly step and per key moment of the run)
   scale_down/assembly/video/*.mp4 (wagon assembly, yard assembly, wire ends, the three-wagon run)
"""
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
FR = BUILD / "frames"
STEPS = HERE / "steps"
VIDEO = HERE / "video"
INK, GREY, ACCENT = (24, 40, 58), (86, 99, 111), (228, 87, 14)
TITLES = {"wagon": "Wagon assembly", "yard": "Yard assembly", "ends": "Wire ends and start gate", "run": "Three wagons: down the wire, landing, switching",
          "moving": "Moving parts"}
PANEL = {"overview": "Overview", "landing": "Landing: wire to rail at the handover", "switch": "Points: flap, rocker, tongue"}


def font(size, bold=False):
    for p in (["/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if bold else []) + ["/System/Library/Fonts/Supplemental/Arial.ttf",
                                                                                        "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


F_CAP, F_TITLE, F_SMALL = font(26), font(22, True), font(19)


def wrap(draw, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    return lines


def caption(img, seq, text, extra=None):
    W = img.width
    d0 = ImageDraw.Draw(img)
    lines = wrap(d0, text, F_CAP, W - 60)
    bar = 46 + 34 * len(lines)
    out = Image.new("RGB", (W, img.height + bar), "white")
    out.paste(img, (0, bar))
    d = ImageDraw.Draw(out)
    d.text((30, 12), f"PLE-SBS scale model, phase 1 · {TITLES[seq]}", font=F_TITLE, fill=ACCENT)
    for i, ln in enumerate(lines):
        d.text((30, 42 + 34 * i), ln, font=F_CAP, fill=INK)
    if extra:
        d.text((W - 30 - d.textlength(extra, font=F_SMALL), 14), extra, font=F_SMALL, fill=GREY)
    d.line([(0, bar - 1), (W, bar - 1)], fill=(210, 215, 220), width=2)
    return out


BAND = None


def overview_band():
    """Rows of the 16:9 overview that ever hold something: measured over the run's frames."""
    from PIL import ImageChops
    top, bot = 10 ** 6, 0
    files = sorted((FR / "run").glob("*_overview.png"))
    for f in files[:: max(1, len(files) // 40)]:
        im = Image.open(f).convert("RGB")
        bb = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        if bb:
            top, bot = min(top, bb[1]), max(bot, bb[3])
    return max(0, top - 20), bot + 20


def compose(i, fr):
    global BAND
    seq = fr["seq"]
    if seq == "run":
        if BAND is None:
            BAND = overview_band()
        ov = Image.open(FR / seq / f"{i:05d}_overview.png").convert("RGB")
        ov = ov.crop((0, BAND[0], ov.width, BAND[1]))
        la = Image.open(FR / seq / f"{i:05d}_landing.png").convert("RGB")
        sw = Image.open(FR / seq / f"{i:05d}_switch.png").convert("RGB")
        img = Image.new("RGB", (1920, ov.height + la.height + 4), "white")
        img.paste(ov, (0, 0))
        img.paste(la, (0, ov.height + 4))
        img.paste(sw, (960, ov.height + 4))
        d = ImageDraw.Draw(img)
        d.line([(0, ov.height + 2), (1920, ov.height + 2)], fill=(210, 215, 220), width=3)
        d.line([(960, ov.height + 4), (960, img.height)], fill=(210, 215, 220), width=3)
        for (x, y), name in (((16, 10), "overview"), ((16, ov.height + 14), "landing"), ((976, ov.height + 14), "switch")):
            d.text((x, y), PANEL[name], font=F_TITLE, fill=GREY)
        lab = fr.get("labels") or {}
        extra = f"tongue {lab.get('tongue', 0):+.2f}°   rocker {lab.get('tilt', 0):+.1f}°   flap {lab.get('flap', 0):.0f}°"
        return caption(img, seq, fr["caption"], extra)
    v = fr["views"][0]
    img = Image.open(FR / seq / f"{i:05d}_{v}.png").convert("RGB")
    return caption(img, seq, fr["caption"])


def compose_plain(i, fr):
    seq = fr["seq"]
    if seq == "run":
        full = compose(i, fr)
        bar = full.height - (BAND[1] - BAND[0]) - 540 - 4
        return full.crop((0, bar, full.width, full.height)).resize((1600, round((full.height - bar) * 1600 / full.width)))
    return Image.open(FR / seq / f"{i:05d}_{fr['views'][0]}.png").convert("RGB")


def main():
    sb = json.load(open(BUILD / "storyboard.json"))
    frames = sb["frames"]
    for d in (STEPS, VIDEO, BUILD / "composed"):
        if d.exists() and d != BUILD / "composed":
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    lists = {}
    for i, fr in enumerate(frames):
        seq = fr["seq"]
        try:
            img = compose(i, fr)
        except FileNotFoundError:
            continue
        p = BUILD / "composed" / f"{seq}_{i:05d}.png"
        if seq == "run":
            img = img.resize((1920, round(img.height * 1920 / img.width)))
        img.save(p)
        if fr.get("still"):
            img.save(STEPS / f"{fr['still']}.png")
            plain = compose_plain(i, fr)                    # without the caption bar, for the guide page
            (BUILD / "plain").mkdir(exist_ok=True)
            plain.save(BUILD / "plain" / f"{fr['still']}.jpg", quality=86)
        lists.setdefault(seq, []).append((p, fr.get("hold", 1), bool(fr.get("still"))))
    fps = {"run": 18, "wagon": 15, "yard": 15, "ends": 15, "moving": 2}
    for seq, items in lists.items():
        if seq == "moving":
            continue
        lst = BUILD / f"{seq}_list.txt"
        with open(lst, "w") as f:
            for p, hold, still in items:
                dur = hold / fps[seq]
                if still:
                    dur = max(dur, 3.0 if seq != "run" else 2.5)       # time to read each step
                f.write(f"file '{p}'\nduration {dur:.4f}\n")
            f.write(f"file '{items[-1][0]}'\n")
        out = VIDEO / f"phase1_{seq}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
                        "-c:v", "libx264", "-crf", "24", "-preset", "slow", "-r", "30", "-movflags", "+faststart", str(out)], check=True)
        print("wrote", out.name, f"{out.stat().st_size / 1e6:.1f} MB")
    print(len(list(STEPS.glob("*.png"))), "step images")


if __name__ == "__main__":
    main()
