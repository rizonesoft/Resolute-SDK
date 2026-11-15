"""The asset builder fits a tool's name: a long one never runs under the icon or off the edge."""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "brand"))
import brandkit

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


if __name__ == "__main__":
    unittest.main()
