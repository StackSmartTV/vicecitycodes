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
            if "super-squad-dash" not in path.parts and "gloopernova" not in path.parts and "parkcrown" not in path.parts and path.is_file()
        ]
        self.assertGreaterEqual(len(pages), 10)
        for path in pages:
            text = path.read_text(encoding="utf-8")
            self.assertIn(DISCLAIMER, text, path)
            self.assertIn('class="fan-disclaimer"', text, path)

    def test_youtube_links_use_the_current_channel(self) -> None:
        """Shared chrome links Yea I Really Did It, and retired videos stay out."""
        import re

        from sitegen.youtube import YOUTUBE_CHANNEL_LABEL, YOUTUBE_CHANNEL_URL

        retired_handle = "ViceCity" + "CentralHub"
        retired_phrase = "GTA 6" + " Hub"
        retired_ids = (
            "S15vn" + "MUktDA",
            "yjOgTY" + "b1tAU",
            "swMR3T" + "YJJ1o",
            "sK8GvR" + "qKZfg",
            "a9B1Od" + "RDT1Y",
            "l380Pj" + "TfGkI",
        )
        anchor = re.compile(
            r'<a\b[^>]*href="' + re.escape(YOUTUBE_CHANNEL_URL) + r'"[^>]*>.*?</a>',
            re.S,
        )
        pages = []
        scanned = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or "tests" in path.parts:
                continue
            if path.suffix.lower() not in {".html", ".js", ".css", ".py", ".json", ".xml"}:
                continue
            text = path.read_text(encoding="utf-8")
            scanned.append(path)
            self.assertNotIn(retired_handle, text, path)
            self.assertNotIn(retired_phrase, text, path)
            for video_id in retired_ids:
                self.assertNotIn(video_id, text, path)
            if path.suffix == ".html":
                self.assertNotIn("youtube.com/shorts/", text, path)
                self.assertNotIn("youtube-nocookie.com/embed/", text, path)
            if path.suffix != ".html" or "vh-yt" not in text:
                continue
            pages.append(path)
            anchors = anchor.findall(text)
            self.assertGreaterEqual(len(anchors), 3, path)
            for link in anchors:
                self.assertIn('target="_blank"', link, path)
                self.assertIn('rel="noopener"', link, path)
            footer = text[text.find("<footer"):text.find("</footer>")]
            header = text[text.find("vch-header:start"):text.find("vch-header:end")]
            self.assertIn(YOUTUBE_CHANNEL_URL, footer, path)
            self.assertIn(YOUTUBE_CHANNEL_LABEL, footer, path)
            self.assertIn(YOUTUBE_CHANNEL_URL, header, path)
            self.assertIn(YOUTUBE_CHANNEL_LABEL, header, path)
            self.assertIn("ca-pub-4487667124440052", text, path)
            self.assertIn("G-RCMHE7MJPD", text, path)
        self.assertGreaterEqual(len(pages), 19)
        self.assertGreaterEqual(len(scanned), 19)


if __name__ == "__main__":
    unittest.main()
