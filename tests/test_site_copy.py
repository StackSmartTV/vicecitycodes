"""App Review wording: the companion app is fan-made, and the footer says so."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISCLAIMER = (
    "Vice Codes Hub is an unofficial fan site and app. Not affiliated with, "
    "endorsed by, or sponsored by Rockstar Games or Take-Two Interactive. "
    "All trademarks belong to their owners."
)


class SiteCopyTest(unittest.TestCase):
    def test_companion_app_is_not_called_official(self) -> None:
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("unofficial fan-made companion app", index)
        self.assertIn("Vice Codes Hub", index)
        self.assertIn("coming to iPhone", index)
        self.assertNotIn("Our official", index)
        for path in ROOT.rglob("*.html"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("official companion", text, path)
            self.assertNotIn("our official", text, path)

    def test_footer_disclaimer_on_vice_city_pages(self) -> None:
        pages = [
            path
            for path in ROOT.rglob("*.html")
            if "super-squad-dash" not in path.parts and path.is_file()
        ]
        self.assertGreaterEqual(len(pages), 10)
        for path in pages:
            text = path.read_text(encoding="utf-8")
            self.assertIn(DISCLAIMER, text, path)
            self.assertIn('class="fan-disclaimer"', text, path)


if __name__ == "__main__":
    unittest.main()
