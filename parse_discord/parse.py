"""String parsing logic."""

from __future__ import annotations

import copy
import datetime
import functools
from enum import Enum
from typing import Generator, Any
from pathlib import Path

import regex
from urlstd.parse import URL

from .ast import *


__all__ = ("parse",)

with open(Path(__file__).parent / "emoji.txt") as f:
    emoji_source = f.read()

bold_underline_source = r"""
 \*\*(?<b>(?:\\.|[^\\])+?)\*\*(?!\*)  # bold
| __(?<u>(?:\\.|[^\\])+?)__(?!_)  # underline
"""

main_source = r"""
# skip escapes
(?:\\.(*SKIP)(*F))?

# italics
  \*(?!\s)(?<i>(?:\\.|\*\*|[^*\\])+?)(?<!\s)\ {0,2}\*(?!\*)
| _(?<i>(?:\\.|__|[^_\\])+?)_(?![a-zA-Z0-9_])  # (doesn't have the same weird whitespace rules as asterisks)

# substituted with bold_underline_source below
| %s

# strikethrough
| ~~(?<st>.+?)~~(?!_)

# spoilers
| \|\|(?<s>.+?)\|\|

# backticks
| ```(?:(?<l>[a-zA-Z_\-+.0-9]*)\n)?(?<cb>.+?)```  # codeblock
| (?<x>`{1,2})(?<c>.+?)(?<!`)\g<x>(?!`)  # inline code

# mentions
| <@!?(?<um>[0-9]+)>
| <\#(?<cm>[0-9]+)>
| <@&(?<rm>[0-9]+)>
| (?<ev>@everyone)
| (?<he>@here)

# emoji
| <(?<a>a?):(?<n>[a-zA-Z_0-9]+):(?<e>[0-9]+)>
| (?<ue>%s)  # substituted with emoji_source below

# time
| <t:(?<t>-?[0-9]+)(?::(?<f>[tTdDfFR]))?>

# links
| (?<hl>(?:https?|steam)://[^\s<]+[^<.,:;"'\]\s])
| (?<hls>)<(?<hl>[^: >]+:/[^ >]+)>

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
""" % (bold_underline_source, emoji_source)

FLAGS = regex.X | regex.S | regex.M | regex.VERSION1

@functools.cache
def compiled_regex(**kwargs: bool):
    s = main_source
    for name, value in kwargs.items():
        s = regex.sub(r"\{\{\?\?%s\b(.*?)}}" % name, r"\1" if value else "", s, flags=regex.S)
    return regex.compile(s, FLAGS)

bold_underline_compiled = regex.compile(bold_underline_source, FLAGS)

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

    def parse(self, s: str) -> Markup:
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
        return Parser(r, s, i, self).parse()

class Parser:
    def __init__(self, regex, s, i, ctx):
        self.regex = regex
        self.s = s
        self.i = i
        self.ctx = ctx
        self.nodes = []

    def advance(self, start, end):
        t = self.s[self.i:start]
        self.i = end
        if t:
            self.nodes.append(Text(regex.sub(r"(?|\\([^A-Za-z0-9\s])|(¯\\_\(ツ\)_/¯))| +(?=\n)", r"\1", t)))

    def parse(self) -> Markup:
        while n := self.get_match():
            self.nodes.append(n)
        self.advance(len(self.s), None)
        return Markup(self.nodes)

    def new_ctx(self, m: regex.Match, **kwargs) -> Context:
        return self.ctx.update(self.s, m, **kwargs)

    def get_match(self) -> Node:
        m = self.regex.search(self.s, self.i)

        if m is None:
            return m

        # bold and underline matches take precedence over shorter italic ones
        if m.group("i"):
            if nm := bold_underline_compiled.match(self.s, m.start()):
                if len(range(*nm.span())) > len(range(*m.span())):
                    m = nm

        self.advance(m.start(), m.end())

        for g, ty in [("b", Bold), ("u", Underline), ("i", Italic), ("s", Spoiler), ("st", Strikethrough)]:
            if r := m.group(g):
                return ty(self.new_ctx(m).parse(r))

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

        if r := m.group("hl"):
            if (len(r) - len(r.rstrip(")"))) > r.count("("):
                self.i -= 1
                r = r[:-1]

            if not URL.can_parse(r) or (u := URL(r)).protocol not in ("http:", "https:", "discord:"):
                x = Text(r)
            else:
                x = Link(u, None, None, m.group("hls") is not None)

            return x

        if r := m.captures("q"):
            return Quote(self.new_ctx(m, is_quote=True).parse("\n".join(r).rstrip(" ")))

        if r := m.captures("li"):
            items = []
            bullets = m.captures("lb")
            start = None if bullets[0].strip() in "*-" else min(max(int(bullets[0].split(".")[0]), 1), 1_000_000_000)
            for bullet, item in zip(bullets, r):
                t = regex.sub("^ {1,%d}" % len(bullet), "", item, flags=regex.M)
                items.append(self.new_ctx(m, is_list=True).parse(t))
            return List(start, items)

        if r := m.group("h"):
            title = r.rstrip().rstrip("#").rstrip()
            return Header(self.new_ctx(m).parse(title), len(m.group("ty")))

        assert False

def parse(string: str, /) -> Markup:
    """Parse a string.

    Typical usage of this library will involve calling `parse` on message content returned by the API,
    then manipulating the resulting tree somehow.

    :param string: The string to parse.
    :returns: The resulting tree.
    """
    return Context().parse(string)
