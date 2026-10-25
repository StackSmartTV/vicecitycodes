"""Analytics consent: Consent Mode v2 defaults, cookie banner, no Google Fonts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]


class ConsentTest(unittest.TestCase):
    EEA = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE",
           "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
           "IS", "LI", "NO", "GB", "CH"]
    AD_KEYS = ("ad_storage", "ad_user_data", "ad_personalization")

    def _blocks(self, text: str) -> list[str]:
        out, i = [], 0
        while True:
            i = text.find("gtag('consent', 'default'", i)
            if i == -1:
                return out
            out.append(text[i:text.find("});", i)])
            i += 1

    def test_consent_default_before_gtag(self) -> None:
        gtag_pages = [p for p in PAGES if "googletagmanager.com/gtag" in p.read_text(encoding="utf-8")]
        self.assertGreaterEqual(len(gtag_pages), 10)
        for path in gtag_pages:
            text = path.read_text(encoding="utf-8")
            blocks = self._blocks(text)
            self.assertEqual(len(blocks), 2, path)
            regional, rest = blocks
            # EEA/UK/CH: everything denied until Google's CMP / our banner update it.
            for key in self.AD_KEYS + ("analytics_storage",):
                self.assertRegex(regional, rf"'{key}': 'denied'", path)
            region = re.search(r"'region': \[([^\]]*)\]", regional)
            self.assertIsNotNone(region, path)
            codes = re.findall(r"'([A-Z]{2})'", region.group(1))
            self.assertEqual(sorted(codes), sorted(self.EEA), path)
            self.assertIn("'wait_for_update'", regional, path)
            # Elsewhere: ads granted unless GPC / opt-out; analytics still denied until Accept.
            self.assertNotIn("'region'", rest, path)
            for key in self.AD_KEYS:
                self.assertIn(f"'{key}': vccAdsOptOut ? 'denied' : 'granted'", rest, path)
            self.assertIn("'analytics_storage': 'denied'", rest, path)
            self.assertIn("navigator.globalPrivacyControl===true", text[:text.find(regional)], path)
            self.assertIn("gtag('set', 'restricted_data_processing', true)", text, path)
            first = text.find("gtag('consent', 'default'")
            config = text.find("gtag('config', 'G-RCMHE7MJPD'")
            self.assertGreater(config, first, path)
            self.assertGreater(text.find("googletagmanager.com/gtag/js"), first, path)
            self.assertGreater(text.find("adsbygoogle.js"), first, path)
            self.assertIn("'allow_google_signals': false", text, path)
            self.assertIn("'allow_ad_personalization_signals': false", text, path)
            # Personalized ads allowed: no unconditional non-personalized request.
            self.assertNotIn("requestNonPersonalizedAds = 1;\n  (function", text, path)
            for line in text.splitlines():
                if "requestNonPersonalizedAds" in line:
                    self.assertTrue(line.startswith("    "), (path, line))  # only inside if (vccAdsOptOut)
            optout = text.find("if (vccAdsOptOut) {")
            self.assertTrue(-1 < optout < text.find("requestNonPersonalizedAds") < text.find("adsbygoogle.js"), path)

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
        self.assertIn("{ analytics_storage: granted ? 'granted' : 'denied' }", js)
        # The banner's Accept/Reject never touches ad_* (Google's messages own those).
        update = js[js.index("function update("):js.index("function analyticsGranted")]
        self.assertNotIn("ad_storage", update)
        self.assertNotIn("ad_personalization", update)
        # Auto-popup is suppressed only where Google's TCF message applies.
        self.assertIn("__tcfapi", js)
        self.assertIn("gdprApplies", js)
        self.assertNotIn("non-personalized ads only", js)
        self.assertNotIn("Personalized ads are always off", js)
        self.assertNotIn("anuncios personalizados siempre", js)
        # Own "Do Not Sell or Share" opt-out.
        self.assertIn("vcc-ads-optout", js)
        self.assertIn("restricted_data_processing", js)

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
            self.assertIn("https://adssettings.google.com", text)
            self.assertIn("https://policies.google.com/technologies/partner-sites", text)
            self.assertIn("data-ads-optout", text)
            self.assertNotIn("non-personalized ads only", text)
            self.assertNotIn("solo anuncios no personalizados", text)
        self.assertIn("may be personalized", en)
        self.assertIn("pueden ser personalizados", es)


if __name__ == "__main__":
    unittest.main()
