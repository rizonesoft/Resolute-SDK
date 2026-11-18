"""Render the installer reference set: frame A "Graphite panel" and setup badge 1 "Graphite arrow" (DESIGN.md section 17).

This is the reference implementation of the contract. D03 T01 sections 3 and 4 port it into brandkit.py, and their test
checks brandkit's output against the PNGs this script writes, pixel for pixel.

    python docs/captures/installer/reference/make_reference.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "brand"))
import brandkit  # noqa: E402  (the kit lives beside this repository's brand folder, as in every tool's build.py)
from PIL import Image  # noqa: E402

# Three tools cover the cases: a short name, a second accent, and the longest name in the suite (two lines).
TOOLS = {
    "memboost": r"D:\Resolute_Bin\MemBoost\brand\build.py",
    "firemin": r"D:\Resolute_Bin\Firemin\brand\build.py",
    "sleepwakediagnostics": r"D:\Resolute_Bin\SleepWakeDiagnostics\brand\build.py",
}

# Frame A on its 164 by 314 grid.
PANEL_W, PANEL_H = 164, 314
ICON_X, ICON_Y, ICON_SIZE = 30, 58, 104
TEXT_COLUMN = 136                      # the name and the credit stay inside x 14 to 150
NAME_SIZES = (19, 18, 17, 16, 15)      # the largest that fits on one line wins
NAME_LEADING = 1.2                     # line pitch for a two-line name, times the size
NAME_BASELINE = 196                    # the first line's baseline
RULE_W, RULE_H, RULE_GAP = 40, 3, 14   # the accent rule, its top RULE_GAP below the last baseline
CREDIT_BASELINE, CREDIT_SIZES, CREDIT_TRACKING = 296, (7.6, 7.2, 6.8, 6.4), 0.4
GLOW_CX, GLOW_CY, GLOW_R, GLOW_OPACITY = 0.5, 0.34, 0.6, 0.38

SIDE = [(202, 386), (269, 515), (336, 643), (403, 772), (430, 824), (498, 953), (534, 1022)]  # 100% to 250%
SMALL = [58, 77, 97, 116, 124, 143, 159]                                                      # 100% to 250%
REFERENCE_SIDE = (202, 430)    # the sizes kept as reference PNGs: 100% and 200%
REFERENCE_SMALL = (58, 116)
REFERENCE_SETUP = (256, 32, 16)

# Badge 1 on the 96 grid.
BADGE_R = {False: 19, True: 22}        # radius: detailed drawing, small drawing (below 40 px)
BADGE_GAP = {False: 4, True: 5}        # knock-out ring width
BADGE_STROKE = {False: 3.8, True: 4.6}
ARROW = "M0 -9 V7 M-7 1 L0 8 L7 1"     # on a 26-unit badge, scaled by radius / 13


def load_spec(path: str) -> dict:
    """The tool's app_assets arguments, read by running its build.py with app_assets and main stubbed out."""
    captured: dict = {}
    real = (brandkit.app_assets, brandkit.main)

    def grab(**kw):
        captured.update(kw)
        return {}

    brandkit.app_assets, brandkit.main = grab, (lambda *a, **k: 0)
    try:
        exec(compile(Path(path).read_text(encoding="utf-8"), path, "exec"), {"__name__": "__main__", "__file__": path})
    except SystemExit:
        pass  # build.py ends with sys.exit(brandkit.main(...)); the stub returned 0
    finally:
        brandkit.app_assets, brandkit.main = real
    # Until build.py declares `accent=` (D03 T01 section 3), the accent is the first colour of the detailed icon.
    captured.setdefault("accent", re.findall(r"#[0-9A-Fa-f]{6}", captured["large"])[0])
    return captured


def name_lines(name: str) -> tuple[float, list[str]]:
    for size in NAME_SIZES:
        if brandkit.text_width(name, "Sora-Bold.ttf", size, -0.03) <= TEXT_COLUMN:
            return size, [name]
    size = NAME_SIZES[-1]
    lines = brandkit.wrapped(name, "Sora-Bold.ttf", size, TEXT_COLUMN)
    if len(lines) > 2 or max(brandkit.text_width(line, "Sora-Bold.ttf", size, -0.03) for line in lines) > TEXT_COLUMN:
        raise SystemExit(f"installer: the name {name!r} does not fit the side panel in two lines at {size}")
    return size, lines


def credit_size(credit: str) -> float:
    for size in CREDIT_SIZES:
        if brandkit.text_width(credit, "Inter-Regular.ttf", size) + CREDIT_TRACKING * len(credit) <= TEXT_COLUMN:
            return size
    raise SystemExit(f"installer: the credit {credit!r} does not fit the side panel")


def side_panel(s: dict, width: int, height: int) -> str:
    """The panel for one image-area size. Inno's sizes are rounded, so 202 by 386 is not exactly 164:314: the viewBox
    keeps 164 units across and takes its height from the pixel size, so the drawing scales uniformly and the PNG comes
    out at exactly the listed size. Everything is laid out on the 164 by 314 grid; only the ground runs to the edge."""
    accent, credit = s["accent"], s.get("credit", "A Resolute tool by Rizonesoft")
    view_h = height * PANEL_W / width
    size, lines = name_lines(s["name"])
    text = ""
    for index, line in enumerate(lines):
        line_w = brandkit.text_width(line, "Sora-Bold.ttf", size, -0.03)
        text += brandkit.name_text(line, PANEL_W / 2 - line_w / 2, NAME_BASELINE + index * size * NAME_LEADING, size, brandkit.PAPER)[0]
    rule_y = NAME_BASELINE + (len(lines) - 1) * size * NAME_LEADING + RULE_GAP
    body = (f'<defs><radialGradient id="g" cx="{GLOW_CX}" cy="{GLOW_CY}" r="{GLOW_R}">'
            f'<stop offset="0" stop-color="{accent}" stop-opacity="{GLOW_OPACITY}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>'
            f'</radialGradient></defs>'
            f'<rect width="{PANEL_W}" height="{view_h:.4f}" fill="{brandkit.GRAPHITE}"/><rect width="{PANEL_W}" height="{PANEL_H}" fill="url(#g)"/>'
            + brandkit.placed(s["large"], ICON_X, ICON_Y, ICON_SIZE) + text
            + f'<rect x="{(PANEL_W - RULE_W) / 2:g}" y="{rule_y:.1f}" width="{RULE_W}" height="{RULE_H}" rx="{RULE_H / 2}" fill="{accent}"/>'
            + f'<text x="{PANEL_W / 2:g}" y="{CREDIT_BASELINE}" text-anchor="middle" font-family="Inter" font-size="{credit_size(credit)}" '
              f'fill="{brandkit.MUTED_ON_DARK}" letter-spacing="{CREDIT_TRACKING}">{credit}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PANEL_W} {view_h:.4f}" width="{width}" height="{height}" '
            f'role="img" aria-label="{s["name"]} setup">{body}</svg>\n')


def badged(inner: str, small: bool) -> str:
    r, gap, stroke = BADGE_R[small], BADGE_GAP[small], BADGE_STROKE[small]
    c = 96 - r - 1
    scale = r / 13
    return (f'<defs><mask id="m"><rect width="96" height="96" fill="white"/><circle cx="{c}" cy="{c}" r="{r + gap}" fill="black"/></mask></defs>'
            f'<g mask="url(#m)">{inner}</g><circle cx="{c}" cy="{c}" r="{r}" fill="{brandkit.GRAPHITE}"/>'
            f'<g transform="translate({c} {c}) scale({scale:g})"><path d="{ARROW}" fill="none" stroke="{brandkit.PAPER}" '
            f'stroke-width="{stroke / scale:.4f}" stroke-linecap="round" stroke-linejoin="round"/></g>')


def setup_svg(s: dict, size: int) -> str:
    small = size < brandkit.SMALL_BELOW
    return brandkit.svg(96, 96, badged(s["small"] if small else s["large"], small), f"{s['name']} setup")


def setup_ico(s: dict) -> bytes:
    frames = [Image.open(io.BytesIO(brandkit.render(setup_svg(s, z), z))).convert("RGBA") for z in brandkit.ICO_SIZES]
    out = io.BytesIO()
    frames[-1].save(out, format="ICO", sizes=[(z, z) for z in brandkit.ICO_SIZES], append_images=frames[:-1])
    return out.getvalue()


def main() -> int:
    for slug, path in TOOLS.items():
        s = load_spec(path)
        out = HERE / slug
        out.mkdir(exist_ok=True)
        for width, height in SIDE:
            panel = side_panel(s, width, height)
            data = brandkit.render(panel, width)
            if Image.open(io.BytesIO(data)).size != (width, height):
                raise SystemExit(f"installer: {slug} side panel rendered {Image.open(io.BytesIO(data)).size}, not {width} by {height}")
            if width in REFERENCE_SIDE:
                (out / f"side-{width}.svg").write_text(panel, encoding="utf-8")
                (out / f"side-{width}.png").write_bytes(data)
        for z in REFERENCE_SMALL:
            (out / f"small-{z}.png").write_bytes(brandkit.render(brandkit.svg(96, 96, s["large"], s["name"]), z))
        (out / "setup.svg").write_text(setup_svg(s, 256), encoding="utf-8")
        for z in REFERENCE_SETUP:
            (out / f"setup-{z}.png").write_bytes(brandkit.render(setup_svg(s, z), z))
        (out / "setup.ico").write_bytes(setup_ico(s))
        print(f"{slug}: accent {s['accent']}, name {name_lines(s['name'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
