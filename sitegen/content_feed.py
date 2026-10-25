"""Build the versioned app content feed from pages already on the site.

Source of truth:
- gta-5-cheats.html: the verified GTA 5 cheat table (button combos, PC codes, phone numbers)
- index.html: GTA 6 launch date, platforms, and the pre-launch checklist
- sitegen/news.json: dated news items with source URLs

GTA 6 cheats are never invented. The feed lists a game entry and zero cheats
until a real code exists on the site.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHEATS_HTML = ROOT / "gta-5-cheats.html"
INDEX_HTML = ROOT / "index.html"
NEWS_JSON = Path(__file__).resolve().parent / "news.json"
FEED_PATH = ROOT / "feed" / "v1" / "content.json"

SCHEMA_VERSION = 1
GTA6_RELEASE_DATE = "2026-11-19"
GTA6_PLATFORMS = ["PS5", "Xbox Series X|S"]
CHEATS_PAGE_URL = "https://vicecodeshub.com/gta-5-cheats.html"
TAKE_TWO_PREORDER_URL = (
    "https://taketwointeractivesoftwareinc.gcs-web.com/news-releases/"
    "news-release-details/rockstar-games-announces-pre-orders-grand-theft-auto-vi"
)

BUTTON_TOKENS = {
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "X",
    "SQUARE",
    "TRIANGLE",
    "CIRCLE",
    "L1",
    "L2",
    "R1",
    "R2",
    "A",
    "B",
    "Y",
    "LB",
    "LT",
    "RB",
    "RT",
}

# PlayStation Cross is the X token. Xbox X is also X. They live on separate
# input lists, so the same token name is not ambiguous.
_TITLE_TO_TOKEN = {
    "Cross": "X",
    "Circle": "CIRCLE",
    "Square": "SQUARE",
    "Triangle": "TRIANGLE",
    "Up": "UP",
    "Down": "DOWN",
    "Left": "LEFT",
    "Right": "RIGHT",
}

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _slug(text: str) -> str:
    cleaned = text.lower().replace("&", " and ")
    cleaned = cleaned.replace("'", "").replace("’", "")
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    return cleaned


def _parse_iso_date(value: str) -> datetime:
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return datetime.strptime(value, "%Y-%m-%d")


def _is_iso(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if not (_ISO_DATE.match(value) or _ISO_DATETIME.match(value)):
        return False
    try:
        _parse_iso_date(value)
    except ValueError:
        return False
    return True


class _CheatTableParser(HTMLParser):
    """Pull one row per cheat from the GTA 5 cheat table."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_table = False
        self.table_depth = 0
        self.in_row = False
        self.row_class = ""
        self.cell_kind: str | None = None
        self.in_strong = False
        self.in_small = False
        self.in_code = False
        self.in_kbd = False
        self.skip_text = 0
        self.kbd_title: str | None = None
        self.kbd_parts: list[str] = []
        self.strong_parts: list[str] = []
        self.small_parts: list[str] = []
        self.code_parts: list[str] = []
        self.buttons: list[str] = []
        self.codes: list[str] = []
        self.plain_parts: list[str] = []
        self.category: str | None = None
        self.pending_category: str | None = None
        self.row: dict | None = None
        self.cheats: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        classes = attr.get("class", "").split()
        if tag == "table" and "cheat-table" in classes:
            self.in_table = True
            self.table_depth = 1
            return
        if not self.in_table:
            return
        if tag == "table":
            self.table_depth += 1
        if tag == "tr":
            self.in_row = True
            self.row_class = attr.get("class", "")
            self.row = {
                "name": "",
                "effect": "",
                "ps": [],
                "xbox": [],
                "pc": None,
                "phone": None,
                "plain": {},
            }
            return
        if tag in {"td", "th"} and self.in_row:
            classes = attr.get("class", "").split()
            if tag == "th" and ("cat-row" in self.row_class.split() or attr.get("colspan")):
                self.cell_kind = "cat"
            elif "c-name" in classes:
                self.cell_kind = "name"
            elif "col-ps" in classes:
                self.cell_kind = "ps"
            elif "col-xb" in classes:
                self.cell_kind = "xbox"
            elif "col-pc" in classes:
                self.cell_kind = "pc"
            elif "col-ph" in classes:
                self.cell_kind = "phone"
            else:
                self.cell_kind = None
            self.buttons = []
            self.codes = []
            self.plain_parts = []
            self.strong_parts = []
            self.small_parts = []
            return
        if tag == "strong" and self.cell_kind == "name":
            self.in_strong = True
        elif tag == "small" and self.cell_kind == "name":
            self.in_small = True
        elif tag == "code" and self.cell_kind in {"pc", "phone"}:
            self.in_code = True
            self.code_parts = []
        elif tag == "kbd" and self.cell_kind in {"ps", "xbox"}:
            self.in_kbd = True
            self.kbd_title = attr.get("title") or None
            self.kbd_parts = []
        elif tag == "span" and "sr" in classes:
            self.skip_text += 1

    def handle_endtag(self, tag: str) -> None:
        if not self.in_table:
            return
        if tag == "span" and self.skip_text:
            self.skip_text -= 1
            return
        if tag == "strong":
            self.in_strong = False
        elif tag == "small":
            self.in_small = False
        elif tag == "code" and self.in_code:
            self.in_code = False
            code = "".join(self.code_parts).strip()
            if code:
                self.codes.append(code)
        elif tag == "kbd" and self.in_kbd:
            self.in_kbd = False
            token = self._token()
            if token:
                self.buttons.append(token)
        elif tag in {"td", "th"} and self.cell_kind and self.row is not None:
            self._close_cell()
            self.cell_kind = None
        elif tag == "tr" and self.in_row:
            self._close_row()
        elif tag == "table":
            self.table_depth -= 1
            if self.table_depth <= 0:
                self.in_table = False

    def handle_data(self, data: str) -> None:
        if not self.in_table or self.skip_text or not self.cell_kind:
            return
        if self.in_kbd:
            self.kbd_parts.append(data)
        elif self.in_code:
            self.code_parts.append(data)
        elif self.in_strong:
            self.strong_parts.append(data)
        elif self.in_small:
            self.small_parts.append(data)
        elif self.cell_kind == "cat":
            self.plain_parts.append(data)
        elif self.cell_kind in {"ps", "xbox", "pc", "phone"}:
            self.plain_parts.append(data)

    def _token(self) -> str | None:
        if self.kbd_title:
            mapped = _TITLE_TO_TOKEN.get(self.kbd_title.strip())
            if mapped:
                return mapped
            raise ValueError(f"unknown button title: {self.kbd_title!r}")
        text = "".join(self.kbd_parts).strip().upper()
        if not text:
            return None
        if text not in BUTTON_TOKENS:
            raise ValueError(f"unknown button token: {text!r}")
        return text

    def _close_cell(self) -> None:
        assert self.row is not None
        kind = self.cell_kind
        if kind == "cat":
            label = " ".join("".join(self.plain_parts).split())
            if label:
                self.pending_category = label
            return
        if kind == "name":
            self.row["name"] = " ".join("".join(self.strong_parts).split())
            self.row["effect"] = " ".join("".join(self.small_parts).split())
            return
        if kind in {"ps", "xbox"}:
            self.row[kind] = list(self.buttons)
            self.row["plain"][kind] = " ".join("".join(self.plain_parts).split())
            return
        if kind in {"pc", "phone"}:
            self.row[kind] = self.codes[0] if self.codes else None
            self.row["plain"][kind] = " ".join("".join(self.plain_parts).split())

    def _close_row(self) -> None:
        self.in_row = False
        if self.pending_category:
            self.category = self.pending_category
            self.pending_category = None
            self.row = None
            return
        row = self.row
        self.row = None
        if not row or not row["name"]:
            return
        if not self.category:
            raise ValueError(f"cheat {row['name']!r} has no category")
        row["category"] = self.category
        self.cheats.append(row)


def _status_note(platform: str, plain: str) -> str | None:
    text = plain.lower()
    if "not confirmed" in text:
        label = {
            "ps": "PlayStation button combo",
            "xbox": "Xbox button combo",
            "pc": "PC code",
            "phone": "Phone number",
        }[platform]
        return f"{label} is not confirmed."
    if "phone / pc only" in text:
        return "no-console"
    if text == "phone":
        return "phone-only"
    return None


def _notes_for(row: dict, raw_name: str) -> str | None:
    notes: list[str] = []
    if raw_name.endswith("*") or "unlocked" in row["effect"].lower():
        notes.append("Must be unlocked in Story Mode before this cheat works.")
    flags = {key: _status_note(key, row["plain"].get(key, "")) for key in ("ps", "xbox", "pc", "phone")}
    if flags["ps"] == "no-console" and flags["xbox"] == "no-console":
        if flags["pc"] == "phone-only":
            notes.append("No PlayStation or Xbox button combo.")
        else:
            notes.append("No PlayStation or Xbox button combo; this one is phone and PC only.")
    else:
        for key in ("ps", "xbox"):
            if flags[key] and flags[key] not in {"no-console", "phone-only"}:
                notes.append(flags[key])
    if flags["pc"] == "phone-only":
        notes.append("No PC console code; this one is a phone cheat only.")
    elif flags["pc"] and flags["pc"] not in {"no-console", "phone-only"}:
        notes.append(flags["pc"])
    if flags["phone"] and flags["phone"] not in {"no-console", "phone-only"}:
        notes.append(flags["phone"])
    # Drop duplicate unlock notes when the effect already says it and the
    # asterisk path added the same sentence twice.
    deduped: list[str] = []
    for note in notes:
        if note not in deduped:
            deduped.append(note)
    return " ".join(deduped) if deduped else None


def parse_cheats(html: str) -> list[dict]:
    parser = _CheatTableParser()
    parser.feed(html)
    parser.close()
    if not parser.cheats:
        raise ValueError("no cheats parsed from gta-5-cheats.html")
    cheats = []
    seen: set[str] = set()
    for row in parser.cheats:
        raw_name = row["name"]
        name = raw_name.rstrip("*").strip()
        cheat_id = "gta5-" + _slug(name)
        if cheat_id in seen:
            raise ValueError(f"duplicate cheat id: {cheat_id}")
        seen.add(cheat_id)
        cheats.append(
            {
                "id": cheat_id,
                "gameId": "gta5",
                "name": name,
                "category": row["category"],
                "effect": row["effect"],
                "inputs": {
                    "ps": row["ps"],
                    "xbox": row["xbox"],
                    "pc": row["pc"],
                    "phone": row["phone"],
                },
                "notes": _notes_for(row, raw_name),
                "disablesAchievements": True,
                "verified": True,
                "source": CHEATS_PAGE_URL,
            }
        )
    return cheats


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _last_checked(html: str) -> str:
    match = re.search(r"Last checked:\s+([A-Z][a-z]+ \d{1,2}, \d{4})", html)
    _require(match is not None, "GTA 5 page is missing Last checked date")
    parsed = datetime.strptime(match.group(1), "%B %d, %Y")
    return parsed.date().isoformat()


def _checklist_detail(title: str, index_html: str) -> str | None:
    low = title.lower()
    if "pre-load" in low or "preload" in low:
        return (
            "Digital pre-orders can begin pre-loading on November 12, 2026, "
            "before the November 19, 2026 launch. "
            f"Source: {TAKE_TWO_PREORDER_URL}"
        )
    if "clear space" in low or "storage" in low:
        return "Update the console and free storage before the download. This site does not publish an install size."
    if "edition" in low:
        _require("~$79.99" in index_html and "~$99.99" in index_html, "homepage is missing edition prices")
        return (
            "The homepage lists Standard at about $79.99 and Ultimate at about $99.99. "
            "Take-Two's June 24, 2026 announcement lists Standard at $79.99 and Ultimate at $99.99. "
            f"Source: {TAKE_TWO_PREORDER_URL}"
        )
    if "download" in low:
        return (
            "Expect a large open-world download. Physical copies include a download code "
            "and are available starting November 12, 2026 to support pre-loading. "
            f"Source: {TAKE_TWO_PREORDER_URL}"
        )
    return None


def _checklist(index_html: str) -> list[dict]:
    match = re.search(r"<h3>Pre-Launch Prep</h3>\s*<ul>(.*?)</ul>", index_html, re.S)
    _require(match is not None, "homepage is missing the Pre-Launch Prep list")
    items = re.findall(r"<li>(.*?)</li>", match.group(1), re.S)
    _require(bool(items), "Pre-Launch Prep list is empty")
    checklist = []
    for raw in items:
        title = " ".join(re.sub(r"<[^>]+>", "", raw).split())
        checklist.append(
            {
                "id": _slug(title),
                "title": title,
                "detail": _checklist_detail(title, index_html),
                "group": "launch-prep",
            }
        )
    return checklist


def _load_news() -> list[dict]:
    data = json.loads(NEWS_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("sitegen/news.json must be a non-empty list")
    return data


def _site_news(cheats_html: str, checked: str) -> dict:
    _require(
        "No official GTA 6 cheat codes have been confirmed" in cheats_html,
        "refusing to claim GTA 6 has no codes unless the cheats page says so",
    )
    parsed = datetime.strptime(checked, "%Y-%m-%d")
    pretty = f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"
    return {
        "id": "gta5-cheats-last-checked",
        "title": "GTA 5 cheat list checked; no GTA 6 codes yet",
        "date": checked,
        "summary": (
            f"Vice Codes Hub's GTA 5 cheats page was last checked on {pretty}. "
            "It says no official GTA 6 cheat codes have been confirmed. "
            "This feed includes the verified GTA 5 codes and no GTA 6 codes."
        ),
        "url": CHEATS_PAGE_URL,
    }


def build_feed(
    cheats_html: str | None = None,
    index_html: str | None = None,
    news: list[dict] | None = None,
) -> dict:
    cheats_html = CHEATS_HTML.read_text(encoding="utf-8") if cheats_html is None else cheats_html
    index_html = INDEX_HTML.read_text(encoding="utf-8") if index_html is None else index_html
    news = _load_news() if news is None else news

    _require("Grand Theft Auto V" in cheats_html, "cheats page is missing the Grand Theft Auto V title")
    _require(
        "Cheats disable trophies and achievements" in cheats_html,
        "cheats page no longer says cheats disable trophies and achievements",
    )
    for platform in ("PS3", "PS4", "PS5", "Xbox 360", "Xbox One", "Xbox Series X|S", "PC"):
        _require(platform in cheats_html, f"cheats page is missing platform {platform}")

    launch = re.search(r'data-launch="(\d{4}-\d{2}-\d{2})T', index_html)
    _require(launch is not None, "homepage is missing the GTA 6 data-launch date")
    release = launch.group(1)
    _require(release == GTA6_RELEASE_DATE, f"homepage launch date is {release}, expected {GTA6_RELEASE_DATE}")
    _require(
        "PS5 & Xbox Series X|S" in index_html or "PS5 and Xbox Series X|S" in index_html,
        "homepage is missing PS5 and Xbox Series X|S",
    )
    _require("Grand Theft Auto VI" in index_html, "homepage is missing the Grand Theft Auto VI title")

    cheats = parse_cheats(cheats_html)
    _require(len(cheats) == 35, f"expected 35 GTA 5 cheats, parsed {len(cheats)}")
    _require(all(cheat["gameId"] == "gta5" for cheat in cheats), "parsed a non-GTA 5 cheat")

    checked = _last_checked(cheats_html)
    feed_news = list(news) + [_site_news(cheats_html, checked)]
    feed_news.sort(key=lambda item: (item["date"], item["id"]), reverse=True)
    newest = max(item["date"] for item in feed_news)

    return {
        "schemaVersion": SCHEMA_VERSION,
        "updatedAt": f"{newest}T00:00:00Z",
        "games": [
            {
                "id": "gta5",
                "title": "Grand Theft Auto V",
                "releaseDate": None,
                "platforms": ["PS3", "PS4", "PS5", "Xbox 360", "Xbox One", "Xbox Series X|S", "PC"],
            },
            {
                "id": "gta6",
                "title": "Grand Theft Auto VI",
                "releaseDate": GTA6_RELEASE_DATE,
                "platforms": list(GTA6_PLATFORMS),
            },
        ],
        "cheats": cheats,
        "news": feed_news,
        "checklist": _checklist(index_html),
    }


def dump_feed(feed: dict) -> str:
    return json.dumps(feed, indent=2, ensure_ascii=False) + "\n"


def validate_feed(data: object) -> list[str]:
    """Return schema errors. An empty list means the feed matches schema v1."""
    errors: list[str] = []

    def err(message: str) -> None:
        errors.append(message)

    if not isinstance(data, dict):
        return ["feed must be a JSON object"]
    expected_keys = {"schemaVersion", "updatedAt", "games", "cheats", "news", "checklist"}
    if set(data) != expected_keys:
        err(f"top-level keys must be {sorted(expected_keys)}, got {sorted(data)}")
        return errors
    if data["schemaVersion"] != 1:
        err("schemaVersion must be 1")
    if not _is_iso(data["updatedAt"]) or not str(data["updatedAt"]).endswith("Z"):
        err("updatedAt must be an ISO8601 UTC datetime")

    games = data["games"]
    if not isinstance(games, list):
        err("games must be a list")
        games = []
    game_ids = []
    for index, game in enumerate(games):
        prefix = f"games[{index}]"
        if not isinstance(game, dict) or set(game) != {"id", "title", "releaseDate", "platforms"}:
            err(f"{prefix} must have id, title, releaseDate, platforms")
            continue
        if game["id"] not in {"gta5", "gta6"}:
            err(f"{prefix}.id must be gta5 or gta6")
        if not isinstance(game["title"], str) or not game["title"]:
            err(f"{prefix}.title must be a non-empty string")
        release = game["releaseDate"]
        if release is not None and not _is_iso(release):
            err(f"{prefix}.releaseDate must be ISO8601 or null")
        platforms = game["platforms"]
        if not isinstance(platforms, list) or not platforms or not all(isinstance(item, str) and item for item in platforms):
            err(f"{prefix}.platforms must be a non-empty list of strings")
        game_ids.append(game["id"])
    if game_ids != ["gta5", "gta6"]:
        err("games must be gta5 then gta6")
    gta6 = next((game for game in games if isinstance(game, dict) and game.get("id") == "gta6"), None)
    if isinstance(gta6, dict):
        if gta6.get("releaseDate") != GTA6_RELEASE_DATE:
            err(f"gta6.releaseDate must be {GTA6_RELEASE_DATE}")
        if gta6.get("platforms") != GTA6_PLATFORMS:
            err("gta6.platforms must be PS5 and Xbox Series X|S")

    cheats = data["cheats"]
    if not isinstance(cheats, list):
        err("cheats must be a list")
        cheats = []
    cheat_ids: set[str] = set()
    gta6_cheats = 0
    cheat_keys = {
        "id",
        "gameId",
        "name",
        "category",
        "effect",
        "inputs",
        "notes",
        "disablesAchievements",
        "verified",
        "source",
    }
    for index, cheat in enumerate(cheats):
        prefix = f"cheats[{index}]"
        if not isinstance(cheat, dict) or set(cheat) != cheat_keys:
            err(f"{prefix} is missing schema fields")
            continue
        if not isinstance(cheat["id"], str) or not cheat["id"]:
            err(f"{prefix}.id must be a non-empty string")
        elif cheat["id"] in cheat_ids:
            err(f"duplicate cheat id {cheat['id']}")
        else:
            cheat_ids.add(cheat["id"])
        if cheat["gameId"] not in game_ids:
            err(f"{prefix}.gameId is not a known game")
        if cheat["gameId"] == "gta6":
            gta6_cheats += 1
        for field in ("name", "category", "effect"):
            if not isinstance(cheat[field], str) or not cheat[field]:
                err(f"{prefix}.{field} must be a non-empty string")
        inputs = cheat["inputs"]
        if not isinstance(inputs, dict) or set(inputs) != {"ps", "xbox", "pc", "phone"}:
            err(f"{prefix}.inputs must have ps, xbox, pc, phone")
        else:
            for pad in ("ps", "xbox"):
                buttons = inputs[pad]
                if not isinstance(buttons, list) or not all(isinstance(token, str) for token in buttons):
                    err(f"{prefix}.inputs.{pad} must be a list of strings")
                else:
                    unknown = [token for token in buttons if token not in BUTTON_TOKENS]
                    if unknown:
                        err(f"{prefix}.inputs.{pad} has unknown tokens {unknown}")
            for field in ("pc", "phone"):
                value = inputs[field]
                if value is not None and (not isinstance(value, str) or not value):
                    err(f"{prefix}.inputs.{field} must be a string or null")
        if cheat["notes"] is not None and not isinstance(cheat["notes"], str):
            err(f"{prefix}.notes must be a string or null")
        if not isinstance(cheat["disablesAchievements"], bool):
            err(f"{prefix}.disablesAchievements must be a bool")
        if not isinstance(cheat["verified"], bool):
            err(f"{prefix}.verified must be a bool")
        if cheat["source"] is not None and not isinstance(cheat["source"], str):
            err(f"{prefix}.source must be a string or null")
    if gta6_cheats:
        err("gta6 must have zero cheats")
    if not any(isinstance(cheat, dict) and cheat.get("gameId") == "gta5" for cheat in cheats):
        err("expected verified GTA 5 cheats")

    news = data["news"]
    if not isinstance(news, list):
        err("news must be a list")
        news = []
    news_ids: set[str] = set()
    news_keys = {"id", "title", "date", "summary", "url"}
    for index, item in enumerate(news):
        prefix = f"news[{index}]"
        if not isinstance(item, dict) or set(item) != news_keys:
            err(f"{prefix} is missing schema fields")
            continue
        if not isinstance(item["id"], str) or not item["id"]:
            err(f"{prefix}.id must be a non-empty string")
        elif item["id"] in news_ids:
            err(f"duplicate news id {item['id']}")
        else:
            news_ids.add(item["id"])
        if not isinstance(item["title"], str) or not item["title"]:
            err(f"{prefix}.title must be a non-empty string")
        if not _is_iso(item["date"]):
            err(f"{prefix}.date must be ISO8601")
        if not isinstance(item["summary"], str) or not item["summary"]:
            err(f"{prefix}.summary must be a non-empty string")
        url = item["url"]
        if url is not None and (not isinstance(url, str) or not url.startswith(("https://", "http://"))):
            err(f"{prefix}.url must be an http(s) URL or null")

    checklist = data["checklist"]
    if not isinstance(checklist, list):
        err("checklist must be a list")
        checklist = []
    check_ids: set[str] = set()
    check_keys = {"id", "title", "detail", "group"}
    for index, item in enumerate(checklist):
        prefix = f"checklist[{index}]"
        if not isinstance(item, dict) or set(item) != check_keys:
            err(f"{prefix} is missing schema fields")
            continue
        if not isinstance(item["id"], str) or not item["id"]:
            err(f"{prefix}.id must be a non-empty string")
        elif item["id"] in check_ids:
            err(f"duplicate checklist id {item['id']}")
        else:
            check_ids.add(item["id"])
        if not isinstance(item["title"], str) or not item["title"]:
            err(f"{prefix}.title must be a non-empty string")
        if item["detail"] is not None and not isinstance(item["detail"], str):
            err(f"{prefix}.detail must be a string or null")
        if not isinstance(item["group"], str) or not item["group"]:
            err(f"{prefix}.group must be a non-empty string")
    return errors
