"""String parsing logic."""

from __future__ import annotations

import datetime
import functools
from enum import Enum
from typing import Generator, Any
from pathlib import Path

import regex

from .ast import *


__all__ = ("parse",)

with open(Path(__file__).parent / "emoji.txt") as f:
    emoji_source = f.read()

main_source = r"""
# utility definitions
(?(DEFINE)
    (?<some>(?:\\.|[^\\])+?)
)

# skip escapes
(?:\\.(*SKIP)(*F))?

# asterisks
  \*(?!\s)(?<i>(?:\\.|\*\*|[^*\\])+?)(?<!\s)\ {0,2}\*(?!\*)   # italics
| \*\*(?<b>(?&some))\*\*(?!\*)  # bold

# underscores, basically the same deal
| _(?<i>(?:\\.|__|[^_\\])+?)_(?![a-zA-Z0-9_])  # italics (doesn't have the same weird whitespace rules as asterisks)
| __(?<u>(?&some))__(?!_)  # underline

# strikethrough
| ~~(?<st>.+?)~~(?!_)

# spoilers
| \|\|(?<s>.+?)\|\|

# backticks
| (?<x>`{1,2})(?<c>.+?)(?<!`)\g<x>(?!`)  # inline code
| ```(?:(?<l>[a-zA-Z_\-+.0-9]*)\n)?(?<cb>.+?)```  # codeblock

# mentions
| <@!?(?<um>[0-9]+)>
| <\#(?<cm>[0-9]+)>
| <@&(?<rm>[0-9]+)>
| (?<ev>@everyone)
| (?<he>@here)

# emoji
| <(?<a>a?):(?<n>[a-zA-Z_0-9]+):(?<e>[0-9]+)>
| (?<ue>%s)

# time
| <t:(?<t>-?[0-9]+)(?::(?<f>[tTdDfFR]))?>

# optional rules. we use a custom {{??name ...}} fence for this, handled by the code below.

{{??headers
| ^(?<ty>\#{1,3})\s+(?!\#)(?<h>[^\n]*)\n?
}}

{{??quotes
| (?:(?<=^\ *)>\ (?<q>[^\n]*)\n?)+  # line
| (?<=^\ *)>>>\ (?<q>.*)  # block
}}

{{??lists
| (?<=^\ *)(?:(?<lb>(?:[*-]|\d+\.)\ +)(?<li>.[^\n]*(?:\n\ [^\n]*)*)\n?)+
}}
""" % emoji_source

@functools.cache
def compiled_regex(**kwargs: bool):
    s = main_source
    for name, value in kwargs.items():
        s = regex.sub(r"\{\{\?\?%s\b(.*?)}}" % name, r"\1" if value else "", s, flags=regex.S)
    return regex.compile(s, regex.X | regex.S | regex.M | regex.POSIX | regex.VERSION1)

class LineStart(Enum):
    NOTHING = 0
    SPACE = 1
    TEXT = 2

class Context:
    """Context about the contents of the source string surrounding a regex being matched.

    Ideally, markup parsing would be recursive, i.e. parsing `*foo*` should be the same
    as parsing `foo` on its own and substituting the result into a `Bold` node. However,
    this is not true in all contexts. For example, in `a *# foo*`, we must know that the
    `# foo` part is not at the start of a line, so that it doesn't turn into a header,
    while `*# foo*` *should* turn into a header. This class stores data related to these
    issues around context. Its `parse` method renders this information to "pass" it to
    the main regex using a variety of tricks.

    :ivar LineStart line_start: Info about the preceding text on the current line.
        One of:
        - `NOTHING`: This is the start of the line.
        - `SPACE`: There are only spaces preceding the node.
        - `TEXT`: The node is in the middle of a line.
    :ivar bool is_quote: Whether the node is inside a quote.
    :ivar int list_depth: The current level of list nesting, from 0 (not in a list) to 11.
    """

    def __init__(self, line_start: LineStart = LineStart.NOTHING, is_quote: bool = False, list_depth: int = 0):
        self.line_start = line_start
        self.is_quote = is_quote
        self.list_depth = list_depth

    def update(self, s: str, m: regex.Match, *, is_quote: bool = False, is_list: bool = False) -> Context:
        line_start = LineStart.NOTHING
        i = m.start()
        while True:
            i -= 1
            if i < 0 or s[i] == "\n":
                break
            if s[i] != " ":
                line_start = LineStart.TEXT
                break
            line_start = LineStart.SPACE

        return Context(
            line_start,
            # once in a quote, always in a quote
            self.is_quote or is_quote,
            self.list_depth + is_list,
        )

    def parse(self, s: str) -> tuple[Any, str, int]:
        if self.line_start == LineStart.NOTHING:
            start = ""
        elif self.line_start == LineStart.SPACE:
            start = " "
        else:
            start = "$"
        i = len(start)
        s = start + s
        r = compiled_regex(
            headers=not self.list_depth,
            quotes=not self.is_quote,
            lists=self.list_depth < 11,
        )
        return r.finditer(s, i), s, i


def append_text(l: list[Node], t: str):
    if t:
        l.append(Text(regex.sub(r"(?|\\([^A-Za-z0-9\s])|(¯\\_\(ツ\)_/¯))| +(?=\n)", r"\1", t)))

def resolve_match(m: regex.Match, ctx: Context, s: str) -> Node:
    for g, ty in [("i", Italic), ("b", Bold), ("u", Underline), ("s", Spoiler), ("st", Strikethrough)]:
        if r := m.group(g):
            return ty(_parse(r, ctx.update(s, m)))

    for g, ty in [("um", UserMention), ("cm", ChannelMention), ("rm", RoleMention)]:
        if r := m.group(g):
            return ty(int(r))

    for g, ty in [("ev", Everyone), ("he", Here)]:
        if r := m.group(g):
            return ty()

    if r := m.group("c"):
        s = r.strip(" ")
        if s[0] == "`":
            r = r.removeprefix(" ")
        if s[-1] == "`":
            r = r.removesuffix(" ")
        return InlineCode(r)

    if r := m.group("cb"):
        return Codeblock(m.group("l") or None, r.strip("\n"))

    if r := m.group("e"):
        return CustomEmoji(int(r), m.group("n"), bool(m.group("a")))

    if r := m.group("ue"):
        return UnicodeEmoji(r)

    if r := m.group("t"):
        dt = datetime.datetime.fromtimestamp(int(r), datetime.timezone.utc)
        return Timestamp(dt, m.group("f") or "f")

    if r := m.captures("q"):
        return Quote(_parse("\n".join(r).rstrip(" "), ctx.update(s, m, is_quote=True)))

    if r := m.captures("li"):
        items = []
        bullets = m.captures("lb")
        start = None if bullets[0].strip() in "*-" else min(max(int(bullets[0].split(".")[0]), 1), 1_000_000_000)
        for bullet, item in zip(bullets, r):
            t = regex.sub("^ {1,%d}" % len(bullet), "", item, flags=regex.M)
            items.append(_parse(t, ctx.update(s, m, is_list=True)))
        return List(start, items)

    if r := m.group("h"):
        title = r.rstrip().rstrip("#").rstrip()
        return Header(_parse(title, ctx.update(s, m)), len(m.group("ty")))

    assert False

def _parse(s: str, ctx: Context = Context(), /) -> Markup:
    l = []
    it, s, i = ctx.parse(s)
    for m in it:
        append_text(l, s[i:m.start()])
        i = m.end()
        l.append(resolve_match(m, ctx, s))
    append_text(l, s[i:])
    return Markup(l)

def parse(string: str, /) -> Markup:
    """Parse a string.

    Typical usage of this library will involve calling `parse` on message content returned by the API,
    then manipulating the resulting tree somehow.

    :param string: The string to parse.
    :returns: The resulting tree.
    """
    return _parse(string)
