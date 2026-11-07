"""Canonical YouTube link for generated pages.

Posts and shared chrome must use this channel. Do not embed retired videos.
"""

from __future__ import annotations

YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@yeaireallydidit"
YOUTUBE_CHANNEL_LABEL = "Yea I Really Did It"
YOUTUBE_WATCH_MORE_LABEL = "Watch more on Yea I Really Did It"
YOUTUBE_WATCH_MORE_LABEL_ES = "Mira más en Yea I Really Did It"


def channel_link(label: str | None = None) -> str:
    text = YOUTUBE_CHANNEL_LABEL if label is None else label
    return (
        f'<a href="{YOUTUBE_CHANNEL_URL}" target="_blank" rel="noopener">{text}</a>'
    )
