#!/usr/bin/env python3
"""Build the SDK's brand assets: the SVG sources, their PNG renders and the Windows icon.

    python brand/build.py            write every asset under brand/
    python brand/build.py --check    exit 1 when a tracked asset differs from what this script builds

One file states the identity (direction B, "Layers", chosen 2026-11-15) so the icon, the wordmark and both banners
cannot drift apart: the colours, the three plates and the type are named once here and DESIGN.md quotes them.
Needs resvg_py and Pillow (`pip install resvg_py pillow`). The fonts are in brand/fonts/ under the SIL Open Font
License, so a render never depends on what a machine has installed.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import resvg_py
from PIL import Image, ImageFont

BRAND = Path(__file__).resolve().parent
FONTS = BRAND / "fonts"
FONT_FILES = [str(p) for p in sorted(FONTS.glob("*.ttf"))]

# The palette. DESIGN.md section "Identity" carries the same values.
GRAPHITE, GRAPHITE_RAISED = "#17191E", "#2A2E36"
PLATE_LOW, PLATE_MID = "#3B414D", "#717B8C"
PLATE_LOW_ON_DARK, PLATE_MID_ON_DARK = "#4A515E", "#8A93A3"
AMBER, AMBER_INK = "#FFB020", "#7A4E00"
PAPER, MUTED_ON_DARK = "#F6F5F2", "#C3C7CF"

TAGLINE = "The shared foundation of the Resolute suite"


def plates(tile: str, low: str, mid: str) -> str:
    """The mark: three stacked plates, the top one amber. `tile` is the ground it sits on, which also cuts the gaps."""
    return (f'<g stroke="{tile}" stroke-width="3" stroke-linejoin="round">'
            f'<polygon points="48,44 78,58 48,72 18,58" fill="{low}"/>'
            f'<polygon points="48,33 78,47 48,61 18,47" fill="{mid}"/>'
            f'<polygon points="48,22 78,36 48,50 18,36" fill="{AMBER}"/></g>')


def icon(tile: str = GRAPHITE, low: str = PLATE_LOW, mid: str = PLATE_MID, x: float = 0, y: float = 0, size: float = 96) -> str:
    scale = size / 96
    return (f'<g transform="translate({x} {y}) scale({scale})"><rect width="96" height="96" rx="22" fill="{tile}"/>'
            f'{plates(tile, low, mid)}</g>')


def icon_small() -> str:
    """Below 40 pixels three plates blur into one: two plates and a wider gap keep the shape."""
    return (f'<rect width="96" height="96" rx="22" fill="{GRAPHITE}"/>'
            f'<g stroke="{GRAPHITE}" stroke-width="6" stroke-linejoin="round">'
            f'<polygon points="48,40 82,57 48,74 14,57" fill="{PLATE_MID}"/>'
            f'<polygon points="48,20 82,37 48,54 14,37" fill="{AMBER}"/></g>')


def svg(width: int, height: int, body: str, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'role="img" aria-label="{label}">{body}</svg>\n')


def text_width(text: str, font: str, size: float, tracking_em: float = 0.0) -> float:
    face = ImageFont.truetype(str(FONTS / font), 1000)
    return (face.getlength(text) / 1000 + tracking_em * len(text)) * size


def wordmark(x: float, baseline: float, size: float, ink: str, chip: str) -> tuple[str, float]:
    """`Resolute` in Sora Bold and the SDK chip beside it. Returns the markup and the x where it ends."""
    name_w = text_width("Resolute", "Sora-Bold.ttf", size, -0.03)
    chip_size = size * 0.5
    chip_text_w = text_width("SDK", "Sora-Bold.ttf", chip_size, 0.08)
    pad_x, border = chip_size * 0.5, max(2.0, size / 20)
    chip_w, chip_h = chip_text_w + 2 * pad_x, chip_size * 1.6
    chip_x = x + name_w + size * 0.42
    chip_y = baseline - size * 0.36 - chip_h / 2
    body = (f'<text x="{x:.1f}" y="{baseline:.1f}" font-family="Sora" font-weight="700" font-size="{size}" '
            f'letter-spacing="{-0.03 * size:.2f}" fill="{ink}">Resolute</text>'
            f'<rect x="{chip_x:.1f}" y="{chip_y:.1f}" width="{chip_w:.1f}" height="{chip_h:.1f}" rx="{chip_h * 0.25:.1f}" '
            f'fill="none" stroke="{chip}" stroke-width="{border:.1f}"/>'
            f'<text x="{chip_x + pad_x:.1f}" y="{chip_y + chip_h / 2 + chip_size * 0.36:.1f}" font-family="Sora" font-weight="700" '
            f'font-size="{chip_size}" letter-spacing="{0.08 * chip_size:.2f}" fill="{chip}">SDK</text>')
    return body, chip_x + chip_w


def wordmark_svg(dark: bool) -> str:
    ink, chip = (PAPER, AMBER) if dark else (GRAPHITE, AMBER_INK)
    tile = (GRAPHITE_RAISED, PLATE_LOW_ON_DARK, PLATE_MID_ON_DARK) if dark else (GRAPHITE, PLATE_LOW, PLATE_MID)
    body, end = wordmark(84, 58, 44, ink, chip)
    width = int(end + 8)
    return svg(width, 80, icon(*tile, x=8, y=8, size=64) + body, "Resolute SDK")


def readme_banner() -> str:
    body, _ = wordmark(280, 158, 64, PAPER, AMBER)
    return svg(1280, 320,
               f'<rect width="1280" height="320" fill="{GRAPHITE}"/>'
               + icon(GRAPHITE_RAISED, PLATE_LOW_ON_DARK, PLATE_MID_ON_DARK, x=72, y=76, size=168) + body
               + f'<text x="282" y="214" font-family="Inter" font-size="22" fill="{MUTED_ON_DARK}">{TAGLINE}</text>',
               "Resolute SDK. " + TAGLINE)


def social_preview() -> str:
    body, _ = wordmark(96, 250, 96, PAPER, AMBER)
    rows = ""
    for index, (colour, label) in enumerate(((AMBER, "UI library"), (PLATE_MID_ON_DARK, "Build rules"), (PLATE_LOW_ON_DARK, "Pinned toolchain"))):
        y = 392 + index * 40
        rows += (f'<rect x="96" y="{y - 12}" width="28" height="8" rx="4" fill="{colour}"/>'
                 f'<text x="140" y="{y}" font-family="Inter" font-weight="500" font-size="20" fill="{PAPER}">{label}</text>')
    return svg(1280, 640,
               f'<rect width="1280" height="640" fill="{GRAPHITE}"/>' + body
               + f'<text x="98" y="318" font-family="Inter" font-size="30" fill="{MUTED_ON_DARK}">{TAGLINE}</text>' + rows
               + f'<text x="96" y="548" font-family="Inter" font-size="18" fill="{MUTED_ON_DARK}">github.com/rizonesoft/Resolute-SDK</text>'
               + icon(GRAPHITE_RAISED, PLATE_LOW_ON_DARK, PLATE_MID_ON_DARK, x=784, y=120, size=400),
               "Resolute SDK. " + TAGLINE)


def render(markup: str, width: int | None = None, zoom: float | None = None) -> bytes:
    return bytes(resvg_py.svg_to_bytes(svg_string=markup, width=width, zoom=zoom, font_files=FONT_FILES, skip_system_fonts=True,
                                       text_rendering="geometric_precision", shape_rendering="geometric_precision"))


def ico(large: str, small: str) -> bytes:
    """Every size rendered from the vector, never scaled from a bitmap: the small drawing below 40 pixels."""
    sizes = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
    frames = [Image.open(io.BytesIO(render(small if size < 40 else large, size))).convert("RGBA") for size in sizes]
    out = io.BytesIO()
    frames[-1].save(out, format="ICO", sizes=[(s, s) for s in sizes], append_images=frames[:-1])
    return out.getvalue()


def build() -> dict[str, bytes]:
    large, small = svg(96, 96, icon(), "Resolute SDK icon"), svg(96, 96, icon_small(), "Resolute SDK icon, small sizes")
    sources = {
        "resolute-sdk-icon.svg": large,
        "resolute-sdk-icon-small.svg": small,
        "resolute-sdk-wordmark-light.svg": wordmark_svg(dark=False),
        "resolute-sdk-wordmark-dark.svg": wordmark_svg(dark=True),
        "readme-banner.svg": readme_banner(),
        "social-preview.svg": social_preview(),
    }
    files: dict[str, bytes] = {name: text.encode("utf-8") for name, text in sources.items()}
    for size in (512, 256, 192, 64, 48):
        files[f"resolute-sdk-icon-{size}.png"] = render(large, size)
    for size in (32, 16):
        files[f"resolute-sdk-icon-{size}.png"] = render(small, size)
    files["resolute-sdk-wordmark-light.png"] = render(sources["resolute-sdk-wordmark-light.svg"], zoom=3)
    files["resolute-sdk-wordmark-dark.png"] = render(sources["resolute-sdk-wordmark-dark.svg"], zoom=3)
    files["readme-banner.png"] = render(sources["readme-banner.svg"], 2560)
    files["social-preview.png"] = render(sources["social-preview.svg"], 1280)
    files["resolute-sdk.ico"] = ico(large, small)
    return files


def main() -> int:
    files = build()
    if "--check" in sys.argv[1:]:
        stale = [name for name, data in files.items() if not (BRAND / name).is_file() or (BRAND / name).read_bytes() != data]
        for name in stale:
            print(f"brand: {name} is not what brand/build.py builds; run python brand/build.py")
        print(f"brand: {len(files) - len(stale)} of {len(files)} asset(s) current")
        return 1 if stale else 0
    for name, data in files.items():
        (BRAND / name).write_bytes(data)
        print(f"brand: wrote {name} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
