"""The committed feed parses, matches schema v1, and matches a fresh build."""

from __future__ import annotations

import json
import unittest

from sitegen.content_feed import (
    BUTTON_TOKENS,
    EXPECTED_GTA5_CHEATS,
    EXPECTED_GTA6_CHEATS,
    FEED_PATH,
    GTA6_CHEATS_PAGE_URL,
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

    def test_gta6_has_verified_launch_codes(self) -> None:
        feed = build_feed()
        gta6 = next(game for game in feed["games"] if game["id"] == "gta6")
        self.assertEqual(gta6["releaseDate"], GTA6_RELEASE_DATE)
        self.assertEqual(gta6["platforms"], GTA6_PLATFORMS)
        gta5 = [cheat for cheat in feed["cheats"] if cheat["gameId"] == "gta5"]
        gta6_cheats = [cheat for cheat in feed["cheats"] if cheat["gameId"] == "gta6"]
        self.assertEqual(len(gta5), EXPECTED_GTA5_CHEATS)
        self.assertEqual(len(gta6_cheats), EXPECTED_GTA6_CHEATS)
        self.assertTrue(all(cheat["verified"] for cheat in gta6_cheats))
        self.assertTrue(all(cheat["disablesAchievements"] for cheat in gta6_cheats))
        names = {cheat["name"] for cheat in gta6_cheats}
        self.assertIn("$250,000", names)
        self.assertIn("Raise Heat Level", names)
        self.assertNotIn("Raise Wanted Level", names)

        money = next(cheat for cheat in gta6_cheats if cheat["name"] == "$250,000")
        expected = ["UP", "RIGHT", "DOWN", "LEFT", "UP", "LEFT", "DOWN", "RIGHT"]
        self.assertEqual(money["inputs"]["ps"], expected)
        self.assertEqual(money["inputs"]["xbox"], expected)
        self.assertIsNone(money["inputs"]["pc"])
        self.assertIsNone(money["inputs"]["phone"])
        self.assertEqual(money["source"], GTA6_CHEATS_PAGE_URL)
        notes = money["notes"].lower()
        self.assertIn("91 story missions", notes)
        self.assertIn("press up", notes)
        self.assertIn("hold l1", notes)
        self.assertIn("disables saving", notes)
        self.assertIn("pc gamer", notes)
        # Unlock is only the story, so no extra "then unlock" line.
        self.assertNotIn("then unlock", notes)

        armor = next(cheat for cheat in gta6_cheats if cheat["name"] == "Body Armor")
        self.assertIn("complete 100 workouts", armor["notes"].lower())

        for cheat in gta6_cheats:
            for pad in ("ps", "xbox"):
                self.assertTrue(set(cheat["inputs"][pad]) <= {"UP", "DOWN", "LEFT", "RIGHT"})

        news_ids = [item["id"] for item in feed["news"]]
        self.assertIn("gta6-cheats-last-checked", news_ids)
        self.assertNotIn("gta5-cheats-last-checked", news_ids)

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
        self.assertTrue(any("november 10" in title for title in titles))
        self.assertTrue(any("clear space" in title for title in titles))
        self.assertTrue(any("edition" in title for title in titles))
        self.assertTrue(all(item["group"] == "launch-prep" for item in feed["checklist"]))
        preload = next(item for item in feed["checklist"] if "november 10" in item["title"].lower())
        self.assertIn("rockstargames.com/newswire", preload["detail"])
        # Install size is only stated alongside Rockstar's official source (Newswire, Nov 3, 2026).
        for item in feed["checklist"]:
            if "GB" in (item["detail"] or ""):
                self.assertIn("up to 212 GB", item["detail"])
                self.assertIn("rockstargames.com/newswire", item["detail"])

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
        self.assertTrue(any("CROSS" in error for error in errors))
        self.assertTrue(any("disable achievements" in error.lower() for error in errors))


if __name__ == "__main__":
    unittest.main()
