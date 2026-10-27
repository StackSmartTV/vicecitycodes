"""app-ads.txt is published from the site root, and Super Squad Dash copy matches the 13+ rating."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RATED = (
    "Super Squad Dash is rated 13+ and is intended for users 13 and older. "
    "It is not designed for or directed to children."
)
DIRECT_LINES = (
    "google.com, pub-4487667124440052, DIRECT, f08c47fec0942fa0",
    "ironsrc.com, 694817, DIRECT, 79929e88b2ba73bc",
    "unity.com, 157504420, DIRECT, 96cabb5fbdde37a7",
)


class AppAdsTxtTest(unittest.TestCase):
    def test_root_file_keeps_direct_lines_and_jekyll_publishes_it(self) -> None:
        text = (ROOT / "app-ads.txt").read_text(encoding="utf-8")
        self.assertFalse(text.startswith("---"), "app-ads.txt must stay plain text")
        for line in DIRECT_LINES:
            self.assertIn(line, text.splitlines())
        lowered = text.lower()
        self.assertNotIn("placeholder", lowered)
        self.assertNotIn("todo", lowered)
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        self.assertIn("app-ads.txt", config)
        exclude = config.split("exclude:", 1)[1]
        self.assertNotIn("app-ads.txt", exclude)
        cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
        self.assertEqual(cname, "vicecodeshub.com")


class SuperSquadDashCopyTest(unittest.TestCase):
    def test_no_twelve_plus_or_coming_soon(self) -> None:
        for path in (ROOT / "super-squad-dash").glob("*.html"):
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            self.assertNotIn("12 and up", lowered, path)
            self.assertNotIn("ages 12", lowered, path)
            self.assertNotIn("coming soon", lowered, path)
            self.assertNotIn("gta", lowered, path)
            self.assertNotIn("rockstar", lowered, path)

    def test_marketing_page_has_no_store_link(self) -> None:
        index = (ROOT / "super-squad-dash" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Coming to the App Store", index)
        self.assertIn(RATED, index)
        self.assertNotIn("apps.apple.com", index)

    def test_privacy_matches_build_15_ads(self) -> None:
        privacy = (ROOT / "super-squad-dash" / "privacy.html").read_text(encoding="utf-8")
        self.assertIn(RATED, privacy)
        for phrase in (
            "Unity LevelPlay",
            "Google AdMob",
            "Unity Ads",
            "User Messaging Platform",
            "Privacy Choices",
            "App Tracking Transparency",
            "IDFA",
            "capped at Teen",
            "no first-party analytics server",
            "https://policies.google.com/privacy",
            "https://unity.com/legal/privacy-policy",
            "https://unity.com/legal/game-player-and-app-user-privacy-policy",
            "12818 SW 8th St #1068, Miami, FL 33184",
        ):
            self.assertIn(phrase, privacy)
        self.assertNotIn("after you finish your first level", privacy)
        self.assertNotIn("Unity Analytics", privacy)

    def test_terms_use_thirteen_plus(self) -> None:
        terms = (ROOT / "super-squad-dash" / "terms.html").read_text(encoding="utf-8")
        self.assertIn(RATED, terms)
        self.assertIn("capped at Teen", terms)
        self.assertIn("12818 SW 8th St #1068, Miami, FL 33184", terms)


if __name__ == "__main__":
    unittest.main()
