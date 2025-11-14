"""Handles the database of Discord emoji. Not exported."""

import json
import regex
from collections import defaultdict
from pathlib import Path


with open(Path(__file__).parent / "emoji.json") as f:
    _emoji = json.load(f)

_by_name = {name: emoji for emoji, names in _emoji.items() for name in names}

def _build_regex(lexicon: list[str]) -> str:
    if len(lexicon) == 1:
        return lexicon[0]
    starts = defaultdict(list)
    had_null = False
    for word in lexicon:
        if not word:
            had_null = True
            continue
        starts[word[0]].append(word[1:])

    starts = sorted(starts.items(), reverse=True)
    r = []
    while starts:
        start, words = starts.pop()
        end = start
        while starts and ord(starts[-1][0]) == ord(end)+1 and starts[-1][1] == words:
            end = starts.pop()[0]
        t = regex.escape(start) if start == end else f"[{regex.escape(start)}-{regex.escape(end)}]"
        r.append(t + _build_regex(words))

    return f'({"|".join(r)})' + "?"*had_null


emoji_source = _build_regex(_emoji)

def names_from_emoji(char: str) -> list[str]:
    """The names `char` has as an emoji on Discord."""
    return _emoji[char]

def emoji_from_name(name: str) -> str | None:
    """The emoji corresponding to `name` on Discord, or None if there is none."""
    return _by_name.get(name)
