#!/usr/bin/env python3
"""Regenerate feed/v1/content.json from the site's cheat table and launch facts.

The published HTML is committed output (GitHub Pages serves the repo root).
Run this after gta-5-cheats.html, index.html, or sitegen/news.json changes,
then commit feed/v1/content.json:

    python3 -m sitegen.build
"""

from __future__ import annotations

import sys

from sitegen.content_feed import FEED_PATH, build_feed, dump_feed, validate_feed


def main() -> int:
    feed = build_feed()
    errors = validate_feed(feed)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEED_PATH.write_text(dump_feed(feed), encoding="utf-8")
    print(f"wrote {FEED_PATH.relative_to(FEED_PATH.parents[2])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
