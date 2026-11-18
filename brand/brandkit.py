#!/usr/bin/env python3
"""What every Resolute repository's brand/build.py shares: the fonts, the wordmark, the two banners, the renders and
the Windows icon. A repository describes its own icon and colours; this turns the description into the asset set.

An app's brand/build.py is a few lines:

    import sys
    from pathlib import Path
    BRAND = Path(__file__).resolve().parent
    sys.path.insert(0, str(BRAND.parent / "sdk" / "brand"))
    import brandkit

    LARGE = '<path d="..." fill="#34D399"/>'      # the icon on a 96-unit grid, for 40 pixels and up
    SMALL = '<path d="..." fill="#34D399"/>'      # the simplified drawing below 40 pixels
    sys.exit(brandkit.main(BRAND, brandkit.app_assets(
        slug="ownership", name="Ownership", tagline="...", large=LARGE, small=SMALL, social_ground="#10231C", social_muted="#BFE8D6")))

The fonts are beside this file under the SIL Open Font License, so a render never depends on what a machine has
installed. Needs resvg_py and Pillow (`pip install resvg_py pillow`).
"""
from __future__ import annotations

import io
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import resvg_py
from PIL import Image, ImageFont

FONTS = Path(__file__).resolve().parent / "fonts"
FONT_FILES = [str(p) for p in sorted(FONTS.glob("*.ttf"))]

# The suite's neutrals. DESIGN.md section 15 carries the same values.
GRAPHITE, GRAPHITE_RAISED = "#17191E", "#2A2E36"
PAPER, MUTED_ON_DARK = "#F6F5F2", "#C3C7CF"

ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
SMALL_BELOW = 40   # the size under which the simplified drawing is used
SOCIAL_COLUMN = 660  # the social preview's text column: from x 96 to just short of the icon at x 800

# The icon finish, "Deep with gloss" (operator, 2026-11-18; DESIGN.md section 14). Every solid colour becomes a gradient
# in its own hue across its face from the upper left: (offset, OKLab lightness shift, chroma factor) per stop. A white
# sheen then lies over the top half of the whole silhouette.
FINISH_STOPS = ((0.0, 0.15, 0.85), (0.45, 0.0, 1.0), (1.0, -0.13, 1.05))
FINISH_DIRECTION = (0.0, 0.0, 0.75, 1.0)           # x1 y1 x2 y2 in each face's bounding box
FINISH_SHEEN = (0.32, 8, 54)                       # opacity at the top, and the y range it fades over
TONE_FLOOR, TONE_CEILING = "#1F1F1F", "#F0F0F0"    # section 14: no face darker or lighter than these
SVG_NS = "http://www.w3.org/2000/svg"
_HEX = re.compile(r"#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})")
_LEFT_AS_DRAWN = {"mask", "clipPath", "linearGradient", "radialGradient", "pattern"}
ET.register_namespace("", SVG_NS)


def _linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _encoded(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _oklch(colour: str) -> tuple[float, float, float]:
    """A #RRGGBB colour as OKLCh (Björn Ottosson's OKLab), hue in radians."""
    r, g, b = (_linear(int(colour[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b2 = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_, math.hypot(a, b2), math.atan2(b2, a)


def _linear_rgb(lightness: float, chroma: float, hue: float) -> tuple[float, float, float]:
    a, b = chroma * math.cos(hue), chroma * math.sin(hue)
    l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_, -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)


def tone(colour: str, lightness_shift: float, chroma_factor: float) -> str:
    """`colour` made lighter or darker in its own hue, kept inside the tone limits and inside sRGB (by giving up chroma)."""
    floor, ceiling = _oklch(TONE_FLOOR)[0], _oklch(TONE_CEILING)[0]
    lightness, chroma, hue = _oklch(colour)
    lightness = min(ceiling, max(floor, lightness + lightness_shift))
    chroma *= chroma_factor
    while True:
        while chroma > 0 and not all(-1e-4 <= v <= 1 + 1e-4 for v in _linear_rgb(lightness, chroma, hue)):
            chroma = max(0.0, chroma - 0.002)
        out = "#" + "".join(f"{round(_encoded(min(1.0, max(0.0, v))) * 255):02X}" for v in _linear_rgb(lightness, chroma, hue))
        # Rounding to 8 bits can land a hair past a limit: step back inside it.
        if _oklch(out)[0] < floor:
            lightness += 0.001
        elif _oklch(out)[0] > ceiling:
            lightness -= 0.001
        else:
            return out


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def finished(inner: str, uid: str = "rf") -> str:
    """The drawing with the suite's finish. Masks, clip paths, patterns and existing gradients are left exactly as
    drawn (whole subtrees, nested ones included), so a cut-out still shows the ground. A face with no width or no height
    (a straight line) has no bounding box for its gradient, so each paint names its flat colour as the fallback after
    the url. A paint the finish cannot read (a named colour, currentColor, an inline style) fails the build by name
    rather than staying flat unseen."""
    root = ET.fromstring(f'<g xmlns="{SVG_NS}">{inner}</g>')
    taken = {element.get("id") for element in root.iter() if element.get("id")}
    while any(f"{uid}{suffix}" in taken for suffix in ("0", "s", "m", "b")):
        uid += "x"
    ids: dict[str, str] = {}
    gradients: list[str] = []

    def paint(colour: str) -> str:
        colour = colour.upper()
        if len(colour) == 4:
            colour = "#" + "".join(c * 2 for c in colour[1:])
        if colour not in ids:
            gid = f"{uid}{len(ids)}"
            while gid in taken:
                gid += "x"
            ids[colour] = gid
            x1, y1, x2, y2 = FINISH_DIRECTION
            stops = "".join(f'<stop offset="{o:g}" stop-color="{tone(colour, dl, cf)}"/>' for o, dl, cf in FINISH_STOPS)
            gradients.append(f'<linearGradient id="{gid}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}">{stops}</linearGradient>')
        return f"url(#{ids[colour]}) {colour}"

    def visit(element: ET.Element) -> None:
        if _local(element.tag) in _LEFT_AS_DRAWN:
            return
        if _local(element.tag) == "style":
            raise ValueError("brandkit: the finish cannot read a <style> sheet; give each face fill and stroke attributes")
        style = element.get("style", "")
        if any(part.split(":", 1)[0].strip() in ("fill", "stroke") for part in style.split(";")):
            raise ValueError(f"brandkit: the finish cannot read the inline style {style!r}; use fill and stroke attributes")
        for name in ("fill", "stroke"):
            value = element.get(name)
            if value is None or value == "none" or value.startswith("url("):
                continue
            if not _HEX.fullmatch(value):
                raise ValueError(f"brandkit: the finish cannot read {name}={value!r}; give the colour as #RRGGBB")
            element.set(name, paint(value))
        for child in element:
            visit(child)

    for child in root:
        visit(child)
    # Each child is written on its own, so it carries any namespace it needs (xlink:href), and nothing is cut by hand.
    body = (root.text or "") + "".join(ET.tostring(child, encoding="unicode") for child in root)
    opacity, top, bottom = FINISH_SHEEN
    return (f'<defs>{"".join(gradients)}'
            f'<linearGradient id="{uid}s" gradientUnits="userSpaceOnUse" x1="0" y1="{top}" x2="0" y2="{bottom}">'
            f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="{opacity}"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>'
            f'</linearGradient><mask id="{uid}m" mask-type="alpha" maskUnits="userSpaceOnUse" x="0" y="0" width="96" height="96">'
            f'<use href="#{uid}b"/></mask></defs>'
            f'<g id="{uid}b">{body}</g><rect width="96" height="96" fill="url(#{uid}s)" mask="url(#{uid}m)"/>')


def svg(width: int, height: int, body: str, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'role="img" aria-label="{label}">{body}</svg>\n')


def placed(inner: str, x: float, y: float, size: float) -> str:
    """A 96-unit drawing placed at x, y and scaled to `size`."""
    return f'<g transform="translate({x} {y}) scale({size / 96})">{inner}</g>'


def text_width(text: str, font: str, size: float, tracking_em: float = 0.0) -> float:
    face = ImageFont.truetype(str(FONTS / font), 1000)
    return (face.getlength(text) / 1000 + tracking_em * len(text)) * size


def wrapped(text: str, font: str, size: float, width: float) -> list[str]:
    """`text` broken at spaces into lines no wider than `width`."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and text_width(trial, font, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line] if line else lines

def name_text(name: str, x: float, baseline: float, size: float, ink: str) -> tuple[str, float]:
    """The name in Sora Bold. Returns the markup and its width."""
    markup = (f'<text x="{x:.1f}" y="{baseline:.1f}" font-family="Sora" font-weight="700" font-size="{size}" '
              f'letter-spacing="{-0.03 * size:.2f}" fill="{ink}">{name}</text>')
    return markup, text_width(name, "Sora-Bold.ttf", size, -0.03)


def render(markup: str, width: int | None = None, zoom: float | None = None) -> bytes:
    return bytes(resvg_py.svg_to_bytes(svg_string=markup, width=width, zoom=zoom, font_files=FONT_FILES, skip_system_fonts=True,
                                       text_rendering="geometric_precision", shape_rendering="geometric_precision"))


def ico(large: str, small: str) -> bytes:
    """Every size rendered from the vector, never scaled from a bitmap: the small drawing below 40 pixels."""
    frames = [Image.open(io.BytesIO(render(small if size < SMALL_BELOW else large, size))).convert("RGBA") for size in ICO_SIZES]
    out = io.BytesIO()
    frames[-1].save(out, format="ICO", sizes=[(s, s) for s in ICO_SIZES], append_images=frames[:-1])
    return out.getvalue()


def icon_files(slug: str, large: str, small: str) -> dict[str, bytes]:
    """The icon's two sources, its PNG renders and the .ico. `large` and `small` are whole SVG documents."""
    files = {f"{slug}-icon.svg": large.encode("utf-8"), f"{slug}-icon-small.svg": small.encode("utf-8")}
    for size in (512, 256, 192, 64, 48):
        files[f"{slug}-icon-{size}.png"] = render(large, size)
    for size in (32, 16):
        files[f"{slug}-icon-{size}.png"] = render(small, size)
    files[f"{slug}.ico"] = ico(large, small)
    return files


def app_assets(slug: str, name: str, tagline: str, large: str, small: str, social_ground: str, social_muted: str,
               credit: str = "A Resolute tool by Rizonesoft", finish: bool = True) -> dict[str, bytes]:
    """A tool's whole asset set. `large` and `small` are the icon's inner markup on a 96-unit grid, free-standing:
    no tile behind it, so it must read on a light and on a dark ground by itself (DESIGN.md section 14). `credit` is the
    small line under the tagline of the social preview: the launcher is not "a Resolute tool" and passes its own.
    `finish` gives the drawing the suite's gradient finish; the launcher, whose gradients are drawn by hand, passes False."""
    if finish:
        large, small = finished(large, "rfl"), finished(small, "rfs")
    big = svg(96, 96, large, f"{name} icon")
    little = svg(96, 96, small, f"{name} icon, small sizes")
    files = icon_files(slug, big, little)

    def wordmark(ink: str) -> str:
        text, width = name_text(name, 84, 58, 44, ink)
        return svg(int(84 + width + 10), 80, placed(large, 8, 8, 64) + text, name)

    # A long name is set smaller in the banner and on two lines in the social preview: "Sleep and Wake Diagnostics" ran under
    # the icon and off the edge at the one fixed size.
    banner_size = 64
    while banner_size > 40 and text_width(name, "Sora-Bold.ttf", banner_size, -0.03) > 940:
        banner_size -= 2
    text, _ = name_text(name, 280, 158, banner_size, PAPER)
    banner = svg(1280, 320, f'<rect width="1280" height="320" fill="{GRAPHITE}"/>' + placed(large, 72, 76, 168) + text
                 + f'<text x="282" y="214" font-family="Inter" font-size="22" fill="{MUTED_ON_DARK}">{tagline}</text>',
                 f"{name}. {tagline}")
    # The tagline wraps inside the column left of the icon: one long line ran under the icon on the first tool built.
    lines = wrapped(tagline, "Inter-Regular.ttf", 30, 640)
    name_size, name_lines = 104, [name]
    while name_size > 56 and max(text_width(line, "Sora-Bold.ttf", name_size, -0.03) for line in name_lines) > SOCIAL_COLUMN:
        name_size -= 4
        name_lines = wrapped(name, "Sora-Bold.ttf", name_size, SOCIAL_COLUMN)
        if len(name_lines) > 2:
            name_lines = [name]
    if len(name_lines) == 1 and name_size == 104:
        top = 280 if len(lines) == 1 else 258
    else:
        # The whole block (name, tagline, credit) is centred on the height; `top` is the last name line's baseline.
        leading = name_size * 1.08
        block = name_size * 0.72 + leading * (len(name_lines) - 1) + 70 + 42 * len(lines) + 28
        top = (640 - block) / 2 + name_size * 0.72 + leading * (len(name_lines) - 1)
    text = "".join(name_text(line, 96, top - name_size * 1.08 * (len(name_lines) - 1 - index), name_size, PAPER)[0]
                   for index, line in enumerate(name_lines))
    rows = "".join(f'<text x="98" y="{top + 70 + 42 * index}" font-family="Inter" font-size="30" fill="{social_muted}">{line}</text>'
                   for index, line in enumerate(lines))
    credit_y = top + 70 + 42 * len(lines) + 28
    social = svg(1280, 640, f'<rect width="1280" height="640" fill="{social_ground}"/>' + text + rows
                 + f'<text x="98" y="{credit_y}" font-family="Inter" font-size="20" fill="{social_muted}">{credit}</text>'
                 + placed(large, 800, 136, 368), f"{name}. {tagline}")
    sources = {f"{slug}-wordmark-light.svg": wordmark(GRAPHITE), f"{slug}-wordmark-dark.svg": wordmark(PAPER),
               "readme-banner.svg": banner, "social-preview.svg": social}
    files.update({key: value.encode("utf-8") for key, value in sources.items()})
    files[f"{slug}-wordmark-light.png"] = render(sources[f"{slug}-wordmark-light.svg"], zoom=3)
    files[f"{slug}-wordmark-dark.png"] = render(sources[f"{slug}-wordmark-dark.svg"], zoom=3)
    files["readme-banner.png"] = render(banner, 2560)
    files["social-preview.png"] = render(social, 1280)
    return files


def main(brand: Path, files: dict[str, bytes]) -> int:
    """Write the assets under `brand`, or with --check say which tracked asset differs from what is built."""
    if "--check" in sys.argv[1:]:
        stale = [name for name, data in files.items() if not (brand / name).is_file() or (brand / name).read_bytes() != data]
        for name in stale:
            print(f"brand: {name} is not what brand/build.py builds; run python brand/build.py")
        print(f"brand: {len(files) - len(stale)} of {len(files)} asset(s) current")
        return 1 if stale else 0
    for name, data in files.items():
        (brand / name).write_bytes(data)
        print(f"brand: wrote {name} ({len(data)} bytes)")
    return 0
