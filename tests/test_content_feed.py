"""The committed feed parses, matches schema v1, and matches a fresh build."""

from __future__ import annotations

import json
import unittest

from sitegen.content_feed import (
    BUTTON_TOKENS,
    FEED_PATH,
    GTA6_PLATFORMS,
    GTA6_RELEASE_DATE,
    build_feed,
    dump_feed,
    validate_feed,
)


class ContentFeedTest(unittest.TestCase):
    def test_committed_feed_parses_and_matches_schema(self) -> None:
        raw = FEED_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
        self.assertEqual(validate_feed(data), [])
        self.assertEqual(raw, dump_feed(data))

    def test_committed_feed_matches_rebuild(self) -> None:
        committed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
        rebuilt = build_feed()
        self.assertEqual(validate_feed(rebuilt), [])
        self.assertEqual(committed, rebuilt)

    def test_gta6_has_no_invented_cheats(self) -> None:
        feed = build_feed()
        gta6 = next(game for game in feed["games"] if game["id"] == "gta6")
        self.assertEqual(gta6["releaseDate"], GTA6_RELEASE_DATE)
        self.assertEqual(gta6["platforms"], GTA6_PLATFORMS)
        self.assertEqual([cheat for cheat in feed["cheats"] if cheat["gameId"] == "gta6"], [])
        self.assertEqual(len(feed["cheats"]), 35)
        self.assertTrue(all(cheat["gameId"] == "gta5" for cheat in feed["cheats"]))

    def test_known_gta5_codes_and_button_tokens(self) -> None:
        feed = build_feed()
        by_name = {cheat["name"]: cheat for cheat in feed["cheats"]}
        health = by_name["Max Health & Armor"]
        self.assertEqual(health["inputs"]["pc"], "TURTLE")
        self.assertEqual(health["inputs"]["phone"], "1-999-887-853")
        self.assertEqual(health["inputs"]["ps"][0], "CIRCLE")
        self.assertEqual(health["category"], "Player")
        self.assertTrue(health["verified"])
        self.assertTrue(health["disablesAchievements"])

        invincible = by_name["Invincibility"]
        self.assertEqual(invincible["inputs"]["pc"], "PAINKILLER")
        self.assertEqual(invincible["inputs"]["ps"][:4], ["RIGHT", "X", "RIGHT", "LEFT"])
        self.assertEqual(invincible["inputs"]["xbox"][1], "A")

        rapid = by_name["Spawn Rapid GT"]
        self.assertEqual(rapid["inputs"]["ps"], [])
        self.assertEqual(rapid["inputs"]["xbox"], [])
        self.assertEqual(rapid["inputs"]["pc"], "RAPIDGT")
        self.assertIn("not confirmed", rapid["notes"].lower())

        director = by_name["Director Mode"]
        self.assertIsNone(director["inputs"]["pc"])
        self.assertEqual(director["inputs"]["phone"], "1-999-5782-5368")
        self.assertNotIn("phone and PC only", director["notes"])
        self.assertIn("phone cheat only", director["notes"])

        fast_run = by_name["Fast Run"]
        self.assertIsNone(fast_run["inputs"]["phone"])

        for cheat in feed["cheats"]:
            for pad in ("ps", "xbox"):
                self.assertTrue(set(cheat["inputs"][pad]) <= BUTTON_TOKENS)

    def test_news_and_checklist_use_cited_launch_facts(self) -> None:
        feed = build_feed()
        self.assertGreaterEqual(len(feed["news"]), 3)
        for item in feed["news"]:
            self.assertTrue(item["url"].startswith("https://"))
        titles = [item["title"].lower() for item in feed["checklist"]]
        self.assertTrue(any("november 12" in title for title in titles))
        self.assertTrue(any("clear space" in title for title in titles))
        self.assertTrue(any("edition" in title for title in titles))
        self.assertTrue(all(item["group"] == "launch-prep" for item in feed["checklist"]))
        preload = next(item for item in feed["checklist"] if "november 12" in item["title"].lower())
        self.assertIn("taketwointeractivesoftwareinc.gcs-web.com", preload["detail"])
        self.assertNotIn("GB", " ".join(item["detail"] or "" for item in feed["checklist"]))

    def test_validator_rejects_invented_gta6_cheat_and_bad_token(self) -> None:
        feed = build_feed()
        invented = json.loads(json.dumps(feed))
        invented["cheats"].append(
            {
                "id": "gta6-fake",
                "gameId": "gta6",
                "name": "Invented",
                "category": "Player",
                "effect": "Should never ship.",
                "inputs": {"ps": ["CROSS"], "xbox": [], "pc": None, "phone": None},
                "notes": None,
                "disablesAchievements": False,
                "verified": False,
                "source": None,
            }
        )
        errors = validate_feed(invented)
        self.assertTrue(any("gta6" in error for error in errors))
        self.assertTrue(any("CROSS" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
