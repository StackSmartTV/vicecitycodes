"""Park Crown legal pages: required topics, contact details, no third-party names."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "parkcrown"


class ParkCrownPagesTest(unittest.TestCase):
    def test_pages_exist_and_cross_link(self) -> None:
        for name in ("privacy.html", "terms.html"):
            text = (DIR / name).read_text(encoding="utf-8")
            self.assertIn('href="privacy.html"', text, name)
            self.assertIn('href="terms.html"', text, name)
            self.assertIn("Dade-Made Studios", text, name)
            self.assertIn("mdecoded303@gmail.com", text, name)
            self.assertIn("12818 SW 8th St #1068, Miami, FL 33184", text, name)
            self.assertIn("November 11, 2026", text, name)
            self.assertNotIn("Alejandro", text, name)

    def test_no_forbidden_names(self) -> None:
        for path in DIR.glob("*.html"):
            low = path.read_text(encoding="utf-8").lower()
            for bad in (
                "gta",
                "rockstar",
                "grand theft",
                "bloons",
                "ninja kiwi",
                "official app",
                "nba",
            ):
                self.assertNotIn(bad, low, (path, bad))

    def test_privacy_covers_required_topics(self) -> None:
        text = (DIR / "privacy.html").read_text(encoding="utf-8")
        for needle in (
            "rated 13+",
            "COPPA",
            "not designed for or directed to children under 13",
            "no accounts",
            "analytics SDKs",
            "no ads",
            "on your device",
            "face recognition",
            "SwiftData",
            "King of the Court",
            "speech recognition",
            "Apple Privacy Policy",
            "CCPA",
        ):
            self.assertIn(needle, text, needle)

    def test_terms_cover_required_topics(self) -> None:
        text = (DIR / "terms.html").read_text(encoding="utf-8")
        for needle in (
            "stdeula",
            "Park Crown Pro",
            "$1.99",
            "$14.99",
            "7-day free trial",
            "automatically renews unless auto-renew is turned off at least 24 hours",
            "reportaproblem.apple.com",
            "never makes referee calls",
            "consent",
            "Assumption of Risk",
            "State of Florida",
            "Limitation of Liability",
            "rated 13+",
        ):
            self.assertIn(needle, text, needle)


if __name__ == "__main__":
    unittest.main()
