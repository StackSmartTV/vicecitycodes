"""Gloopernova store pages: 13+ wording, required policy links, no third-party game names, no personal details."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "gloopernova"


class GloopernovaPagesTest(unittest.TestCase):
    def test_pages_exist_and_cross_link(self) -> None:
        for name in ("index.html", "privacy.html", "terms.html", "support.html"):
            text = (DIR / name).read_text(encoding="utf-8")
            self.assertIn('href="privacy.html"', text, name)
            self.assertIn('href="terms.html"', text, name)
            self.assertIn("Dade-Made Studios", text, name)

    def test_no_third_party_game_names(self) -> None:
        for path in DIR.glob("*.html"):
            low = path.read_text(encoding="utf-8").lower()
            for bad in ("gta", "rockstar", "grand theft", "bloons", "ninja kiwi", "official app"):
                self.assertNotIn(bad, low, (path, bad))

    def test_privacy_covers_required_topics(self) -> None:
        text = (DIR / "privacy.html").read_text(encoding="utf-8")
        for needle in (
            "rated 13+", "COPPA", "Game Center", "Unity LevelPlay", "Google AdMob", "Unity Ads",
            "App Tracking Transparency", "User Messaging Platform", "Restore Purchases", "CCPA",
            "Data Retention", "https://policies.google.com/technologies/partner-sites",
            "https://unity.com/legal/privacy-policy", "12818 SW 8th St #1068, Miami, FL 33184",
        ):
            self.assertIn(needle, text, needle)

    def test_privacy_names_unity_iap_and_unity_ads(self) -> None:
        text = (DIR / "privacy.html").read_text(encoding="utf-8")
        sec4 = text[text.index("4. In-App Purchases"):text.index("5. Advertising")]
        for needle in ("Unity In-App Purchasing", "Unity Technologies", "installation ID", "IDFV",
                       "only if you allowed tracking", "not use this purchase data for tracking"):
            self.assertIn(needle, sec4, needle)
        self.assertIn("The Game uses Unity Ads through LevelPlay.", text)
        self.assertNotIn("may include <strong>Unity Ads", text)
        self.assertIn("Last updated: November 3, 2026", text)

    def test_terms_cover_required_topics(self) -> None:
        text = (DIR / "terms.html").read_text(encoding="utf-8")
        for needle in (
            "stdeula", "reportaproblem.apple.com", "State of Florida", "third-party beneficiar",
            "Limitation of Liability", "Acceptable Use", "rated 13+",
        ):
            self.assertIn(needle, text, needle)


if __name__ == "__main__":
    unittest.main()
