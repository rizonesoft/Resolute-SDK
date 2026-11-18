"""The asset builder fits a tool's name: a long one never runs under the icon or off the edge, and gives the icon the
suite's gradient finish."""
import io
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "brand"))
import brandkit
from PIL import Image

DRAWING = '<circle cx="48" cy="48" r="30" fill="#6366F1"/>'
NAME = re.compile(r'<text x="([\d.]+)" y="[\d.]+" font-family="Sora" font-weight="700" font-size="(\d+)"[^>]*>([^<]+)</text>')


def names(document: bytes) -> list[tuple[float, int, str]]:
    return [(float(x), int(size), text) for x, size, text in NAME.findall(document.decode("utf-8"))]


def assets(name: str) -> dict[str, bytes]:
    return brandkit.app_assets("tool", name, "What the tool is for", DRAWING, DRAWING, "#15163A", "#D5DAFB")


class NameFits(unittest.TestCase):
    def test_long_name_stays_left_of_the_icon_in_the_social_preview(self):
        lines = names(assets("Sleep and Wake Diagnostics")["social-preview.svg"])
        self.assertEqual(" ".join(text for _, _, text in lines), "Sleep and Wake Diagnostics")
        self.assertLessEqual(len(lines), 2)
        for x, size, text in lines:
            self.assertLessEqual(x + brandkit.text_width(text, "Sora-Bold.ttf", size, -0.03), 800, text)

    def test_long_name_stays_inside_the_readme_banner(self):
        (x, size, text), = names(assets("Sleep and Wake Diagnostics")["readme-banner.svg"])
        self.assertLessEqual(x + brandkit.text_width(text, "Sora-Bold.ttf", size, -0.03), 1280 - 40)

    def test_short_name_keeps_the_full_size_on_one_line(self):
        self.assertEqual([(size, text) for _, size, text in names(assets("Ownership")["social-preview.svg"])], [(104, "Ownership")])
        self.assertEqual([size for _, size, _ in names(assets("Ownership")["readme-banner.svg"])], [64])

class Credit(unittest.TestCase):
    def test_a_tool_is_credited_to_the_suite_and_the_launcher_passes_its_own_line(self):
        self.assertIn("A Resolute tool by Rizonesoft", assets("Ownership")["social-preview.svg"].decode("utf-8"))
        own = brandkit.app_assets("resolute", "Resolute", "One launcher", DRAWING, DRAWING, "#17191E", "#D9D5CC", credit="By Rizonesoft")
        text = own["social-preview.svg"].decode("utf-8")
        self.assertIn(">By Rizonesoft<", text)
        self.assertNotIn("A Resolute tool", text)

class Finish(unittest.TestCase):
    """The gradient finish, "Deep with gloss" (operator, 2026-11-18; DESIGN.md section 14)."""

    def test_a_solid_face_becomes_a_gradient_in_its_own_hue_with_its_flat_colour_as_fallback(self):
        icon = assets("Ownership")["tool-icon.svg"].decode("utf-8")
        self.assertIn('fill="url(#rfl0) #6366F1"', icon)
        stops = re.findall(r'<linearGradient id="rfl0"[^>]*>(.*?)</linearGradient>', icon)[0]
        self.assertEqual(re.findall(r'stop-color="(#[0-9A-F]{6})"', stops)[1], "#6366F1")

    def test_lit_from_the_upper_left_lighter_at_the_top_and_darker_at_the_bottom(self):
        light, _, dark = (brandkit._oklch(brandkit.tone("#6366F1", dl, cf))[0] for _, dl, cf in brandkit.FINISH_STOPS)
        self.assertGreater(light, brandkit._oklch("#6366F1")[0])
        self.assertLess(dark, brandkit._oklch("#6366F1")[0])

    def test_tones_stay_inside_the_section_14_limits_after_rounding(self):
        floor, ceiling = brandkit._oklch("#1F1F1F")[0], brandkit._oklch("#F0F0F0")[0]
        for colour in ("#202020", "#1F2A44", "#3B0A0A"):
            self.assertGreaterEqual(brandkit._oklch(brandkit.tone(colour, -0.13, 1.05))[0], floor, colour)
        for colour in ("#EFEFEF", "#FDE047", "#E0F2FE"):
            self.assertLessEqual(brandkit._oklch(brandkit.tone(colour, 0.15, 0.85))[0], ceiling, colour)

    @staticmethod
    def pixel(markup: str, x: int, y: int) -> tuple[int, ...]:
        image = Image.open(io.BytesIO(brandkit.render(brandkit.svg(96, 96, markup, "t"), 96))).convert("RGBA")
        value = image.getpixel((x, y))
        assert isinstance(value, tuple)   # an RGBA image's pixel is a 4-tuple
        return value

    def test_masks_and_clip_paths_are_left_as_drawn_so_a_cut_out_still_shows_the_ground(self):
        drawing = ('<defs><mask id="hole"><rect width="96" height="96" fill="#fff"/><circle cx="48" cy="48" r="8" fill="#000"/></mask>'
                   '<clipPath id="half"><rect width="48" height="96" fill="#123456"/></clipPath></defs>'
                   '<circle cx="48" cy="48" r="30" fill="#34D399" mask="url(#hole)"/>')
        out = brandkit.finished(drawing, "t")
        self.assertIn('<circle cx="48" cy="48" r="8" fill="#000" />', out)
        self.assertIn('fill="#123456"', out)
        self.assertIn('fill="url(#t0) #34D399"', out)
        self.assertEqual(self.pixel(out, 48, 48)[3], 0)

    def test_a_cut_out_after_a_nested_mask_still_shows_the_ground(self):
        drawing = ('<defs><mask id="outer"><rect width="96" height="96" fill="#fff"/>'
                   '<mask id="inner"><rect width="96" height="96" fill="#fff"/></mask>'
                   '<circle cx="48" cy="48" r="8" fill="#000"/></mask></defs>'
                   '<circle cx="48" cy="48" r="30" fill="#34D399" mask="url(#outer)"/>')
        self.assertEqual(self.pixel(brandkit.finished(drawing, "t"), 48, 48)[3], 0)

    def test_a_self_closing_gradient_does_not_hide_the_faces_after_it(self):
        drawing = '<defs><linearGradient id="empty"/></defs><rect width="40" height="40" fill="#34D399"/><linearGradient id="g"></linearGradient>'
        self.assertIn('fill="url(#t0) #34D399"', brandkit.finished(drawing, "t"))

    def test_only_real_paint_attributes_change(self):
        out = brandkit.finished('<rect width="40" height="40" fill="#34D399" data-fill="#123456"/>', "t")
        self.assertIn('data-fill="#123456"', out)

    def test_a_paint_the_finish_cannot_read_fails_by_name(self):
        for drawing in ('<rect width="9" height="9" style="fill:#34D399"/>', '<rect width="9" height="9" fill="currentColor"/>',
                        '<rect width="9" height="9" fill="red"/>', '<style>.f{fill:#663399}</style><rect class="f" width="9" height="9"/>'):
            with self.assertRaises(ValueError, msg=drawing):
                brandkit.finished(drawing, "t")

    def test_a_style_that_sets_no_paint_is_fine(self):
        self.assertIn("stroke-width:2", brandkit.finished('<path d="M10 10 L80 80" stroke="#34D399" style="stroke-width:2"/>', "t"))

    def test_a_namespaced_reference_keeps_the_drawing(self):
        drawing = ('<defs><rect id="r" x="16" y="16" width="64" height="64" fill="#6366F1"/></defs>'
                   '<use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#r"/>')
        self.assertEqual(self.pixel(brandkit.finished(drawing, "t"), 48, 70)[3], 255)

    def test_generated_ids_never_take_an_id_the_drawing_already_has(self):
        drawing = ('<defs><linearGradient id="t0"><stop offset="0" stop-color="#000000"/></linearGradient></defs>'
                   '<rect width="40" height="40" fill="url(#t0)"/><rect x="50" width="40" height="40" fill="#34D399"/>')
        out = brandkit.finished(drawing, "t")
        self.assertEqual(len(re.findall(r'id="t0"', out)), 1)
        self.assertIn('fill="url(#t0)"', out)

    def test_the_sheen_is_white_over_the_silhouette_at_the_stated_opacity_and_nothing_outside_it(self):
        out = brandkit.finished('<rect x="16" y="16" width="64" height="64" rx="4" fill="#6366F1"/>', "t")
        self.assertEqual(self.pixel(out, 4, 4)[3], 0)
        plain = self.pixel(out.replace(f'stop-opacity="{brandkit.FINISH_SHEEN[0]}"', 'stop-opacity="0"'), 48, 30)
        opacity, top, bottom = brandkit.FINISH_SHEEN
        sheen = opacity * (1 - (30.5 - top) / (bottom - top))
        expected = [round(c + (255 - c) * sheen) for c in plain[:3]]
        for got, want in zip(self.pixel(out, 48, 30)[:3], expected):
            self.assertLessEqual(abs(got - want), 3)

    def test_the_launcher_keeps_its_hand_drawn_gradients(self):
        own = brandkit.app_assets("resolute", "Resolute", "One launcher", DRAWING, DRAWING, "#17191E", "#D9D5CC", credit="By Rizonesoft", finish=False)
        self.assertIn(DRAWING, own["resolute-icon.svg"].decode("utf-8"))
        self.assertNotIn("linearGradient", own["resolute-icon.svg"].decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
