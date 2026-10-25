#!/usr/bin/env python3
"""Validate feed/v1/content.json against the version 1 schema.

    python3 -m sitegen.validate_feed
    python3 -m sitegen.validate_feed path/to/content.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sitegen.content_feed import FEED_PATH, validate_feed


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else FEED_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"missing {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"{path} is not JSON: {exc}", file=sys.stderr)
        return 1
    errors = validate_feed(data)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"ok {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
