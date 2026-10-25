"""Analytics consent: Consent Mode v2 defaults, cookie banner, no Google Fonts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]


class ConsentTest(unittest.TestCase):
    def test_consent_default_before_gtag(self) -> None:
        gtag_pages = [p for p in PAGES if "googletagmanager.com/gtag" in p.read_text(encoding="utf-8")]
        self.assertGreaterEqual(len(gtag_pages), 10)
        for path in gtag_pages:
            text = path.read_text(encoding="utf-8")
            default = text.find("gtag('consent', 'default'")
            self.assertNotEqual(default, -1, path)
            block = text[default:text.find("});", default)]
            for key in ("analytics_storage", "ad_storage", "ad_user_data", "ad_personalization"):
                self.assertRegex(block, rf"'{key}': 'denied'", path)
            config = text.find("gtag('config', 'G-RCMHE7MJPD'")
            self.assertGreater(config, default, path)
            self.assertGreater(text.find("googletagmanager.com/gtag/js"), default, path)
            self.assertGreater(text.find("adsbygoogle.js"), default, path)
            self.assertIn("'allow_google_signals': false", text, path)
            self.assertIn("'allow_ad_personalization_signals': false", text, path)

    def test_every_page_has_cookie_settings_and_banner(self) -> None:
        for path in PAGES:
            text = path.read_text(encoding="utf-8")
            footer = text[text.find("<footer"):text.find("</footer>")]
            self.assertIn("data-cookie-settings", footer, path)
            self.assertTrue("#do-not-sell" in footer or "#no-vender" in footer, path)
            self.assertRegex(text, r'<script src="(\.\./)*consent\.js" defer></script>', path)

    def test_banner_script(self) -> None:
        js = (ROOT / "consent.js").read_text(encoding="utf-8")
        self.assertIn("navigator.globalPrivacyControl === true", js)
        self.assertIn("localStorage", js)
        self.assertIn("analytics_storage: granted ? 'granted' : 'denied'", js)
        self.assertIn("ad_storage: 'denied'", js)

    def test_no_google_fonts(self) -> None:
        for path in list(PAGES) + [ROOT / "style.css"]:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("fonts.googleapis.com", text, path)
            self.assertNotIn("fonts.gstatic.com", text, path)

    def test_privacy_sections(self) -> None:
        en = (ROOT / "privacy.html").read_text(encoding="utf-8")
        es = (ROOT / "es" / "privacidad.html").read_text(encoding="utf-8")
        self.assertIn('id="cookies"', en)
        self.assertIn('id="do-not-sell"', en)
        self.assertIn('id="cookies"', es)
        self.assertIn('id="no-vender"', es)
        for text in (en, es):
            self.assertIn("Global Privacy Control", text)
            self.assertIn("12818 SW 8th St #1068, Miami, FL 33184", text)


if __name__ == "__main__":
    unittest.main()
