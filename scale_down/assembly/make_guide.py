"""Build the phase-1 assembly guide from the storyboard, the FreeCAD screenshots and the check reports.

Run after make_media.py:
  .venv/bin/python scale_down/assembly/make_guide.py
-> scale_down/assembly/README.md (GitHub: every step image with its caption)
   scale_down/assembly/build/guide/index.html + assets (the same guide as one web page)
"""
import csv
import html
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = HERE / "build"
GUIDE = BUILD / "guide"

SECTIONS = [
    ("wagon", "Wagon", "phase1_wagon.mp4",
     "Two identical plates, two wheels, two identical panniers and two printed axle pins. There are no screws: each pin goes through pannier, plate, wheel, plate and pannier, and its split end snaps out of the far side."),
    ("yard", "Yard", "phase1_yard.mp4",
     "Always lower the piece with the slot onto the piece with the tab. The tongue goes in before the rocker bridge, and slides under the end of the entry rail."),
    ("ends", "Wire ends and start gate", "phase1_ends.mp4",
     "The window hook holds the wire with three turns and a wedge. The start gate hangs on the wire, is locked by a tapered key, and holds the waiting wagon by its rear spacer peg."),
    ("run", "Three wagons", "phase1_run.mp4",
     "Each wagon rolls down the wire, lands on the rail head at the same height, crosses the tongue, lifts the flap, and stops in its own bay. The flap rocks the escapement and the spring steps the tongue to the next bay."),
    ("moving", "Moving parts", None, "The positions every moving part can take, each checked against everything around it."),
]


def stills():
    sb = json.load(open(BUILD / "storyboard.json"))
    out = {}
    for fr in sb["frames"]:
        if fr.get("still"):
            out[fr["still"]] = (fr["seq"], fr["caption"])
    return out


def report_lines(path):
    return Path(path).read_text().splitlines() if Path(path).exists() else []


def facts():
    path = report_lines(HERE / "path_check_report.md")
    run = [l for l in path if l.startswith("- no clashes") or "CLASH" in l]
    paths = [l for l in path if l.startswith("- ") and (": clear" in l or "CLASH" in l)]
    fc_static = report_lines(ROOT / "check" / "freecad_report.md")
    fc_motion = report_lines(HERE / "freecad_motion_report.md")
    fit = report_lines(ROOT / "check" / "assembly_report.md")
    n_static = next((re.search(r"(\d+) with overlapping", l).group(1) for l in fc_static if "with overlapping" in l), "?")
    bad_static = next((l.split(":")[-1].strip() for l in fc_static if l.startswith("Pairs expected clear")), "?")
    motion_bad = next((re.search(r"(\d+)", l.split(":")[-1]).group(1) for l in fc_motion if l.startswith("**Unexplained")), None)
    motion_frames = next((re.search(r"(\d+) frames replayed", l).group(1) for l in fc_motion if "frames replayed" in l), None)
    return dict(paths_total=len(paths), paths_clear=sum(": clear" in l for l in paths), run_clash=sum("CLASH" in l for l in run),
                static_pairs=n_static, static_bad=bad_static, motion_bad=motion_bad, motion_frames=motion_frames,
                fit_bad=sum(("CLASH" in l or "JAM" in l or "FAILED" in l) for l in fit))


def reprint_rows():
    md = (ROOT / "print_pack" / "phase1" / "reprint_v2" / "README.md").read_text().splitlines()
    rows, keep, mode = [], [], None
    for l in md:
        if l.startswith("## Print these"):
            mode = "print"
        elif l.startswith("## Keep"):
            mode = "keep"
        elif l.startswith("| ") and not l.startswith("| File") and not l.startswith("| Keep") and not l.startswith("|---"):
            cells = [c.strip() for c in l.strip("|").split("|")]
            (rows if mode == "print" else keep).append(cells)
    return rows, keep


def write_readme(st, f):
    lines = ["# Phase 1: step-by-step assembly, checked in FreeCAD", "",
             "Screenshots rendered by FreeCAD from the part files (`freecad_render.py`), placed by `make_storyboard.py`. "
             "Every move shown here was collision-checked: `path_check_report.md` (exact booleans) and `freecad_motion_report.md` (FreeCAD's own booleans).", "",
             "Full video of assembly, fitting and the three-wagon run: `video/phase1_full.mp4` (about four minutes).", "",
             f"- Insertion paths clear: {f['paths_clear']} of {f['paths_total']}",
             f"- Three-wagon run: {f['run_clash']} clashes",
             f"- FreeCAD motion check: {f['motion_bad'] if f['motion_bad'] is not None else 'running'} unexplained overlaps over {f['motion_frames'] or '?'} frames", "",
             "Animations: `video/phase1_wagon.mp4`, `video/phase1_yard.mp4`, `video/phase1_ends.mp4`, `video/phase1_run.mp4`.", ""]
    for key, title, video, intro in SECTIONS:
        lines += [f"## {title}", "", intro, ""]
        for name, (seq, cap) in st.items():
            if seq == key:
                lines += [f"![{cap}](steps/{name}.png)", ""]
    (HERE / "README.md").write_text("\n".join(lines))


CSS = """
:root {
  /* Layout: an assembly manual. One column of numbered steps per section, two images per row on wide screens; facts strip on top. */
  --bg: #f4f6f7; --panel: #ffffff; --fg: #172029; --muted: #56626e; --rule: #d6dde3;
  --accent: #c8541a; --wagon: #2b5d8c; --ok: #2c7548;
  --display: "IBM Plex Sans Condensed", "Arial Narrow", Arial, sans-serif;
  --body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #11161b; --panel: #182028; --fg: #e5eaee; --muted: #9aa6b1; --rule: #2a343d;
  --accent: #f08b4c; --wagon: #79a9da; --ok: #6cc28e; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #11161b; --panel: #182028; --fg: #e5eaee; --muted: #9aa6b1; --rule: #2a343d;
  --accent: #f08b4c; --wagon: #79a9da; --ok: #6cc28e; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font: 16px/1.55 var(--body); }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 32px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
header h1 { font: 600 clamp(30px, 5vw, 46px)/1.05 var(--display); margin: 0 0 8px; text-wrap: balance; letter-spacing: -0.01em; }
header p { margin: 0; color: var(--muted); max-width: 68ch; }
.eyebrow { font: 600 13px/1 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); margin-bottom: 12px; }
.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1px; background: var(--rule);
  border: 1px solid var(--rule); margin: 24px 0 8px; }
.fact { background: var(--panel); padding: 14px 16px; min-width: 0; }
.fact b { display: block; font: 600 26px/1.1 var(--display); color: var(--ok); font-variant-numeric: tabular-nums; }
.fact span { color: var(--muted); font-size: 14px; }
nav { display: flex; flex-wrap: wrap; gap: 8px 18px; margin: 18px 0 8px; font: 500 15px var(--display); }
nav a { color: var(--fg); text-decoration: none; border-bottom: 2px solid var(--rule); padding-bottom: 2px; }
nav a:hover, nav a:focus-visible { border-color: var(--accent); outline: none; }
.note { border-left: 3px solid var(--accent); background: var(--panel); padding: 12px 16px; margin: 20px 0; max-width: 80ch; }
section { padding-top: 36px; border-top: 1px solid var(--rule); margin-top: 36px; }
section h2 { font: 600 30px/1.1 var(--display); margin: 0 0 6px; }
section > p { margin: 0 0 18px; max-width: 72ch; color: var(--muted); }
video { width: 100%; max-width: 100%; display: block; background: #fff; border: 1px solid var(--rule); }
.steps { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 520px), 1fr)); gap: 22px; margin-top: 22px; }
figure { margin: 0; min-width: 0; }
figure img { width: 100%; display: block; background: #fff; border: 1px solid var(--rule); }
figcaption { font-size: 15px; margin-top: 8px; }
figcaption .n { font: 600 14px var(--mono); color: var(--accent); margin-right: 6px; }
.tablewrap { overflow-x: auto; margin-top: 16px; }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }
th { font: 600 13px var(--mono); letter-spacing: 0.04em; text-transform: uppercase; color: var(--muted); }
td.num { text-align: right; font-variant-numeric: tabular-nums; font-family: var(--mono); white-space: nowrap; }
code { font-family: var(--mono); font-size: 0.92em; }
ul.checks { padding-left: 20px; max-width: 80ch; }
ul.checks li { margin: 6px 0; }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
"""


def write_html(st, f):
    if GUIDE.exists():
        shutil.rmtree(GUIDE)
    (GUIDE / "img").mkdir(parents=True)
    (GUIDE / "video").mkdir()
    for p in (BUILD / "plain").glob("*.jpg"):
        shutil.copy(p, GUIDE / "img" / p.name)
    for p in (HERE / "video").glob("*.mp4"):
        shutil.copy(p, GUIDE / "video" / p.name)
    e = html.escape
    out = ['<title>PLE-SBS Phase 1 Assembly</title>',
           '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500&display=swap">',
           f"<style>{CSS}</style>", '<div class="wrap">', "<header>", '<div class="eyebrow">Scale model 1:50 · phase 1 · version 2</div>',
           "<h1>PLE-SBS Phase 1 Assembly</h1>",
           "<p>Every phase-1 part, placed and moved in FreeCAD before printing: how the wagon and the yard go together, and how three wagons come down "
           "the wire, land on the rail and are sent one to each bay. The screenshots and animations are FreeCAD renders of the actual part files.</p>",
           "</header>", '<div class="facts">']
    mb = f["motion_bad"]
    for big, small in ((f"{f['paths_clear']} / {f['paths_total']}", "assembly moves clear (snap fits excepted)"),
                       (f"{f['run_clash']}", "clashes in the three-wagon run"),
                       (f"{f['static_bad']} / {f['static_pairs']}", "FreeCAD: assembled pairs overlapping"),
                       (("—" if mb is None else mb) + (f" in {f['motion_frames']} frames" if f["motion_frames"] else ""), "FreeCAD motion check: unexplained overlaps")):
        out.append(f'<div class="fact"><b>{e(big)}</b><span>{e(small)}</span></div>')
    out.append("</div>")
    out.append("<nav>" + '<a href="#full">Full video</a>' + "".join(f'<a href="#{k}">{e(t)}</a>' for k, t, *_ in SECTIONS) + '<a href="#print">What to print</a><a href="#checks">How it was checked</a></nav>')
    if (HERE / "video" / "phase1_full.mp4").exists():
        out.append('<section id="full"><h2>The whole of phase 1 in one video</h2><p>Assembly step by step, fitting the moving parts, each moving part through its positions, '
                   'and three wagons down the wire into their bays. About four minutes; the five sections below show the same steps as still images.</p>'
                   '<video controls muted playsinline preload="metadata" src="video/phase1_full.mp4" poster="img/run_1_R_stopped.jpg"></video></section>')
    out.append('<div class="note"><b>No screws.</b> Nothing in phase 1 is bought except the 1.5 mm wire. The wagon is held together by its two printed '
               '4 mm axle pins; the rocker, the flap and the gate lever turn on printed pins too. Each pin has a split end that squeezes through the holes and clicks out of the far side.</div>')
    for key, title, video, intro in SECTIONS:
        out.append(f'<section id="{key}"><h2>{e(title)}</h2><p>{e(intro)}</p>')
        if video:
            out.append(f'<video controls muted playsinline preload="metadata" src="video/{video}" poster="img/{next(n for n, (s, _) in st.items() if s == key)}.jpg"></video>')
        out.append('<div class="steps">')
        for name, (seq, cap) in st.items():
            if seq != key:
                continue
            m = re.match(r"^(\d+)\.\s*(.*)$", cap)
            num, text = (m.group(1), m.group(2)) if m else ("", cap)
            label = f'<span class="n">{e(num)}</span>' if num else ""
            out.append(f'<figure><img loading="lazy" src="img/{name}.jpg" alt="{e(cap)}"><figcaption>{label}{e(text)}</figcaption></figure>')
        out.append("</div></section>")
    rows, keep = reprint_rows()
    out.append('<section id="print"><h2>What to print</h2><p>If you printed version 1, print these files, sliced for the P1S. They come in two sets: '
               "<strong>set 1</strong> (parts 1 to 12: wagon, points, handover) in <code>print_pack/phase1_reprint_v2_set1.zip</code>, and "
               "<strong>set 2</strong> (parts 13 to 19: bays, window hook, start gate) in <code>..._set2.zip</code>. Print set 1 first and get a wagon "
               "rolling and the points stepping before set 2. Keep the parts in the second table.</p>")
    out.append('<div class="tablewrap"><table><thead><tr><th>#</th><th>Set</th><th>File</th><th>Qty</th><th>Filament</th><th>Colour</th><th>g</th><th>Time</th><th>Why it changed</th></tr></thead><tbody>')
    for r in rows:
        if not r[0].isdigit():
            continue
        setno = "1" if int(r[0]) <= 12 else "2"
        cls = ["num", "num", "", "num", "", "", "num", "num", ""]
        vals = [r[0], setno] + r[1:]
        out.append("<tr>" + "".join(f'<td class="{c}">{e(v.replace("**", ""))}</td>' for c, v in zip(cls, vals)) + "</tr>")
    out.append("</tbody></table></div>")
    out.append('<div class="tablewrap"><table><thead><tr><th>Keep from version 1</th><th>Used as</th></tr></thead><tbody>')
    for r in keep:
        out.append("<tr>" + "".join(f"<td>{e(v)}</td>" for v in r) + "</tr>")
    out.append("</tbody></table></div></section>")
    out.append('<section id="checks"><h2>How it was checked</h2><ul class="checks">'
               "<li>Every part was placed in its working position and every pair measured with exact booleans: no clashes, every running fit 0.2 mm per side.</li>"
               "<li>Every assembly move was replayed in small steps: each part travels the path your hand moves it along, against the parts already in place. Only the snap fits overlap while they are pressed through.</li>"
               "<li>Three wagons were driven down the wire with the wire arriving at 4.4°, over the handover, across the tongue and into bays R, C and L. The flap, rocker, tongue, spring, sleds and chains moved with them. "
               "The tongue only moves after the wagon's rear wheel has left it.</li>"
               "<li>FreeCAD repeated the clash checks with its own OpenCascade booleans, for the assembled yard and for every moving frame.</li>"
               "<li>Reports in the repository: <code>scale_down/check/assembly_report.md</code>, <code>scale_down/assembly/path_check_report.md</code>, "
               "<code>scale_down/check/freecad_report.md</code>, <code>scale_down/assembly/freecad_motion_report.md</code>.</li>"
               "<li>What the computer cannot prove: the forces. Whether the spring, the coins and the thread are strong enough is for the first runs to show; "
               "the BOM's section 7 says what to adjust.</li></ul></section>")
    out.append("</div>")
    (GUIDE / "index.html").write_text("\n".join(out))


def main():
    st = stills()
    f = facts()
    write_readme(st, f)
    write_html(st, f)
    print(f)


if __name__ == "__main__":
    main()
