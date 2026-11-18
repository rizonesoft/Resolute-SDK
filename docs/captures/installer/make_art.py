"""Render the installer art candidates (3 frames, 3 setup-icon badges) for two tools, from each tool's own brand spec.

    python make_art.py <out_dir>
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

sys.path.insert(0, r"D:\Resolute-SDK\brand")
import brandkit  # noqa: E402
from PIL import Image  # noqa: E402

TOOLS = {"MemBoost": r"D:\Resolute_Bin\MemBoost\brand\build.py", "Firemin": r"D:\Resolute_Bin\Firemin\brand\build.py"}
GRAPHITE, RAISED, PAPER, MUTED = brandkit.GRAPHITE, brandkit.GRAPHITE_RAISED, brandkit.PAPER, brandkit.MUTED_ON_DARK
INK = "#1F2329"
AMBER = "#FFB020"
LIGHT_PAGE, DARK_PAGE = "#FFFFFF", "#202020"

SIDE = [(202, 386), (269, 515), (336, 643), (403, 772), (430, 824), (498, 953), (534, 1022)]  # WizardImageFile 100% to 250% (Inno 7.1.1 help)
BACK = [(596, 432), (894, 648), (1192, 864)]         # WizardBackImageFile 100%, 150%, 200% (497:360)
SMALL = [58, 77, 97, 116, 124, 143, 159]              # WizardSmallImageFile 100% to 250%, square (Inno 7.1.1 help)


def load_spec(path: str) -> dict:
    captured = {}
    real = brandkit.app_assets

    def grab(**kw):
        captured.update(kw)
        return {}

    brandkit.app_assets, brandkit.main = grab, (lambda *a, **k: 0)
    try:
        src = Path(path).read_text(encoding="utf-8")
        exec(compile(src, path, "exec"), {"__name__": "__main__", "__file__": path})
    except SystemExit:
        pass
    finally:
        brandkit.app_assets = real
    captured["accent"] = re.findall(r'#[0-9A-Fa-f]{6}', captured["large"])[0]
    return captured


def png(markup: str, width: int) -> bytes:
    return brandkit.render(markup, width)


def name_block(name: str, cx: float, baseline: float, size: float, ink: str) -> str:
    w = brandkit.text_width(name, "Sora-Bold.ttf", size, -0.03)
    return brandkit.name_text(name, cx - w / 2, baseline, size, ink)[0]


def credit(cx: float, y: float, size: float, ink: str) -> str:
    return (f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="Inter" font-size="{size}" '
            f'fill="{ink}" letter-spacing="0.4">A Resolute tool by Rizonesoft</text>')


# Frame A: a graphite side panel, the same in light and dark.
def frame_a_side(s: dict) -> str:
    w, h = 164, 314
    body = (f'<defs><radialGradient id="g" cx="50%" cy="34%" r="60%"><stop offset="0" stop-color="{s["accent"]}" stop-opacity="0.38"/>'
            f'<stop offset="1" stop-color="{s["accent"]}" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="{GRAPHITE}"/><rect width="{w}" height="{h}" fill="url(#g)"/>'
            + brandkit.placed(s["large"], 30, 58, 104)
            + name_block(s["name"], w / 2, 196, 19 if len(s["name"]) < 10 else 15, PAPER)
            + f'<rect x="62" y="210" width="40" height="3" rx="1.5" fill="{s["accent"]}"/>'
            + credit(w / 2, 296, 7.6, MUTED))
    return brandkit.svg(w, h, body, "side")


# Frame B: a full-window wash with the icon as a large watermark, light and dark.
def frame_b_back(s: dict, dark: bool) -> str:
    w, h = 497, 360
    ground = DARK_PAGE if dark else LIGHT_PAGE
    op = 0.30 if dark else 0.16
    body = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0.35" stop-color="{s["accent"]}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{s["accent"]}" stop-opacity="{op}"/></linearGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="{ground}"/><rect width="{w}" height="{h}" fill="url(#g)"/>'
            f'<g opacity="{0.10 if dark else 0.08}">' + brandkit.placed(s["large"], 300, 150, 260) + '</g>')
    return brandkit.svg(w, h, body, "back")


# Frame C: no panel, the icon floats on the page with its name, light and dark.
def frame_c_side(s: dict, dark: bool) -> str:
    w, h = 164, 314
    ink = PAPER if dark else INK
    body = (f'<defs><radialGradient id="g" cx="50%" cy="40%" r="42%"><stop offset="0" stop-color="{s["accent"]}" stop-opacity="{0.22 if dark else 0.14}"/>'
            f'<stop offset="1" stop-color="{s["accent"]}" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#g)"/>'
            + brandkit.placed(s["large"], 26, 76, 112)
            + name_block(s["name"], w / 2, 226, 19 if len(s["name"]) < 10 else 15, ink))
    return brandkit.svg(w, h, body, "float")


def small_icon(s: dict) -> str:
    return brandkit.svg(96, 96, s["large"], "icon")


# Setup-icon badges: the tool icon with a knock-out ring and a badge bottom right.
ARROW = '<path d="M0 -9 V7 M-7 1 L0 8 L7 1" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
TRAY = ('<path d="M-9 2 V8 H9 V2" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M0 -10 V3 M-5 -2 L0 3 L5 -2" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
BADGES = {
    "1-graphite-arrow": dict(shape="circle", fill=GRAPHITE, ink=PAPER, glyph=ARROW),
    "2-amber-arrow": dict(shape="circle", fill=AMBER, ink=GRAPHITE, glyph=ARROW),
    "3-graphite-tray": dict(shape="square", fill=GRAPHITE, ink=PAPER, glyph=TRAY),
}


def badged(inner: str, badge: dict, small: bool) -> str:
    r = 22 if small else 19          # badge radius on the 96 grid; larger at small sizes so it survives 16 px
    cx = cy = 96 - r - 1
    gap = 5 if small else 4
    sw = 4.6 if small else 3.8
    scale = r / 13
    if badge["shape"] == "circle":
        hole = f'<circle cx="{cx}" cy="{cy}" r="{r + gap}" fill="black"/>'
        plate = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{badge["fill"]}"/>'
    else:
        hole = f'<rect x="{cx - r - gap}" y="{cy - r - gap}" width="{2 * (r + gap)}" height="{2 * (r + gap)}" rx="{r * 0.5 + gap}" fill="black"/>'
        plate = f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" rx="{r * 0.5}" fill="{badge["fill"]}"/>'
    glyph = badge["glyph"].format(ink=badge["ink"], sw=sw / scale)
    return (f'<defs><mask id="m"><rect width="96" height="96" fill="white"/>{hole}</mask></defs>'
            f'<g mask="url(#m)">{inner}</g>{plate}<g transform="translate({cx} {cy}) scale({scale})">{glyph}</g>')


def badged_ico(s: dict, badge: dict) -> bytes:
    frames = []
    for size in brandkit.ICO_SIZES:
        small = size < brandkit.SMALL_BELOW
        frames.append(Image.open(io.BytesIO(png(brandkit.svg(96, 96, badged(s["small"] if small else s["large"], badge, small), "setup"), size))).convert("RGBA"))
    out = io.BytesIO()
    frames[-1].save(out, format="ICO", sizes=[(z, z) for z in brandkit.ICO_SIZES], append_images=frames[:-1])
    return out.getvalue()


def main(out: Path) -> None:
    for tool, path in TOOLS.items():
        s = load_spec(path)
        d = out / s["slug"]
        d.mkdir(parents=True, exist_ok=True)
        for w, h in SIDE:
            (d / f"a-side-{w}.png").write_bytes(png(frame_a_side(s), w))
            (d / f"c-side-light-{w}.png").write_bytes(png(frame_c_side(s, False), w))
            (d / f"c-side-dark-{w}.png").write_bytes(png(frame_c_side(s, True), w))
        for w, h in BACK:
            (d / f"b-back-light-{w}.png").write_bytes(png(frame_b_back(s, False), w))
            (d / f"b-back-dark-{w}.png").write_bytes(png(frame_b_back(s, True), w))
        for z in SMALL:
            (d / f"small-{z}.png").write_bytes(png(small_icon(s), z))
        for key, badge in BADGES.items():
            (d / f"setup-{key}.ico").write_bytes(badged_ico(s, badge))
            for z in (256, 48, 32, 16):
                small = z < brandkit.SMALL_BELOW
                (d / f"setup-{key}-{z}.png").write_bytes(png(brandkit.svg(96, 96, badged(s["small"] if small else s["large"], badge, small), "setup"), z))
        for z in (256, 48, 32, 16):
            (d / f"app-{z}.png").write_bytes(png(brandkit.svg(96, 96, s["small"] if z < 40 else s["large"], "app"), z))
        (d / "spec.txt").write_text(f'{s["name"]}\n{s["accent"]}\n{s["tagline"]}\n', encoding="utf-8")
        print(tool, s["accent"], "->", d)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
