"""String parsing logic."""

from __future__ import annotations

import copy
import datetime
import functools
from enum import Enum
from typing import Generator, Any
from pathlib import Path

import regex

from .ast import *
from .string import text_to_url, clean_whitespace, is_link_admissable


__all__ = ("parse",)

with open(Path(__file__).parent / "emoji.txt") as f:
    emoji_source = f.read()

bold_underline_source = r"""
 \*\*(?<b>(?:\\.|[^\\])+?)\*\*(?!\*)  # bold
| __(?<u>(?:\\.|[^\\])+?)__(?!_)  # underline
"""

allowed_in_links_source = r"""
# italics
  \*(?!\s)(?<i>(?:\\.|\*\*|[^*\\])+?)(?<!\s)\ {0,2}\*(?!\*)
| _(?<i>(?:\\.|__|[^_\\])+?)_(?![a-zA-Z0-9_])  # (doesn't have the same weird whitespace rules as asterisks)

# substituted with bold_underline_source below
| %s

# strikethrough
| ~~(?<s>.+?)~~(?!_)

# spoilers
| \|\|(?<S>.+?)\|\|

# backticks
| (?<x>`+)(?<c>.+?)(?<!`)\g<x>(?!`)  # inline code

# emoji
| <(?<cea>a?):(?<cen>[a-zA-Z_0-9]+):(?<ce>[0-9]+)>
| (?<ue>%s)  # substituted with emoji_source below

# time
| <t:(?<t>-?[0-9]+)(?::(?<tf>[tTdDfFR]))?>
""" % (bold_underline_source, emoji_source)

main_source = r"""
# skip escapes
{{??escapes(?:\\.(*SKIP)(*F))?}}

# codeblock
  ```(?:(?<Cl>[a-zA-Z_\-+.0-9]*)\n)?(?<C>.*?[^\n].*?)```

# substituted with allowed_in_links_source below
| %s

# mentions
| <@!?(?<um>[0-9]+)>
| <\#(?<cm>[0-9]+)>
| <@&(?<rm>[0-9]+)>
| (?<em>@everyone)
| (?<hm>@here)

# links
| (?<l>(?:https?|steam)://[^\s<]+[^<.,:;"'\]\s])
| (?<ls>)<(?<l>[^: >]+:/[^ >]+)>

# [text](url "title") links
| \[(?<Lb>(?:\[[^\]]*\]|[^\[\]])*[^\[]*)\]  # text part
  \(\s*
    (?<Ls><)?(?<L>(?:\([^)]*\)|[^\s\\]|\\[^\n])*?)(?<Ls>>)?  # url part
    (?:\s+['"](?<Lt>.*?)['"])?  # title part
  \s*\)

# subtext
| ^-\#\ +(?!-\#)(?<v>[^\n]*)\n?

# optional rules. we use a custom {{??name ...}} fence for this, handled by the code below.

{{??headers
| ^(?<hn>\#{1,3})\s+(?!\#)(?<h>[^\n]*)\n?
}}

{{??quotes
| (?:(?<=^\ *)>\ (?<q>[^\n]*)\n?)+  # line
| (?<=^\ *)>>>\ (?<q>.*)  # block
}}

{{??lists
| (?<=^\ *)(?:(?<lb>(?:[*-]|\d+\.)\ +)(?<li>.[^\n]*(?:\n\ [^\n]*)*)\n?)+
}}
""" % (allowed_in_links_source,)

FLAGS = regex.X | regex.S | regex.M | regex.VERSION1

@functools.cache
def compiled_regex(**kwargs: bool) -> regex.Pattern:
    s = main_source
    for name, value in kwargs.items():
        s = regex.sub(r"\{\{\?\?%s\b(.*?)}}" % name, r"\1" if value else "", s, flags=regex.S)
    return regex.compile(s, FLAGS)

bold_underline_compiled = regex.compile(bold_underline_source, FLAGS)
allowed_in_links_compiled = regex.compile(allowed_in_links_source, FLAGS)

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
    :ivar bool testing_link: Whether the node is being tested by is_link_admissable.
    :ivar bool is_link: Whether the node is inside the text part of a [text](url) link.
    """

    def __init__(self,
        line_start: LineStart = LineStart.NOTHING,
        is_quote: bool = False,
        list_depth: int = 0,
        testing_link: bool = False,
        is_link: bool = False,
    ):
        self.line_start = line_start
        self.is_quote = is_quote
        self.list_depth = list_depth
        self.testing_link = testing_link
        self.is_link = is_link

    def update(self, s: str, m: regex.Match, *,
        is_quote: bool = False,
        is_list: bool = False,
        testing_link: bool = False,
    ) -> Context:
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
            self.is_quote or is_quote,
            self.list_depth + is_list,
            self.testing_link or testing_link,
            self.is_link,
        )

    def parse(self, s: str) -> Markup:
        if self.is_link:
            return Parser(allowed_in_links_compiled, s, 0, self).parse()

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
            escapes=not self.testing_link,
        )
        return Parser(r, s, i, self).parse()

class Parser:
    def __init__(self, regex: regex.Pattern, s: str, i: int, ctx: Context):
        self.regex = regex
        self.s = s
        self.i = i
        self.ctx = ctx
        self.nodes = []

    def advance(self, start: int, end: int):
        t = self.s[self.i:start]
        self.i = end
        if t:
            if not (self.ctx.testing_link or self.ctx.is_link):
                t = regex.sub(r"(?|\\([^A-Za-z0-9\s])|(¯\\_\(ツ\)_/¯))| +(?=\n)", r"\1", t)
            self.nodes.append(Text(t))

    def parse(self) -> Markup:
        while n := self.get_match():
            self.nodes.append(n)
        self.advance(len(self.s), 0)
        return Markup(self.nodes)

    def new_ctx(self, m: regex.Match, **kwargs) -> Context:
        return self.ctx.update(self.s, m, **kwargs)

    def get_match(self) -> Node | None:
        m = self.regex.search(self.s, self.i)

        if m is None:
            return m

        # bold and underline matches take precedence over shorter italic ones
        if m.group("i"):
            if nm := bold_underline_compiled.match(self.s, m.start()):
                if len(range(*nm.span())) > len(range(*m.span())):
                    m = nm

        self.advance(m.start(), m.end())

        for g, ty in [("b", Bold), ("u", Underline), ("i", Italic), ("s", Strikethrough), ("S", Spoiler)]:
            if r := m.group(g):
                return ty(self.new_ctx(m).parse(r))

        for g, ty in [("um", UserMention), ("cm", ChannelMention), ("rm", RoleMention)]:
            if r := m.groupdict().get(g):
                return ty(int(r))

        for g, ty in [("em", Everyone), ("hm", Here)]:
            if r := m.groupdict().get(g):
                return ty()

        if r := m.group("c"):
            s = r.strip(" ")
            if s.startswith("`"):
                r = r.removeprefix(" ")
            if s.endswith("`"):
                r = r.removesuffix(" ")
            return InlineCode(r) if not self.ctx.testing_link else Style(self.new_ctx(m).parse(r))

        if r := m.groupdict().get("C"):
            return Codeblock(m.group("Cl") or None, r.strip("\n"))

        if r := m.group("ce"):
            return CustomEmoji(int(r), m.group("cen"), bool(m.group("cea")))

        if r := m.group("ue"):
            return UnicodeEmoji(r)

        if r := m.group("t"):
            limit = 8_640_000_000_000
            timestamp = int(r)
            if not -limit <= timestamp <= limit:
                return Text(m[0])
            return Timestamp(timestamp, m.group("tf") or "f")

        if r := m.group("v"):
            return Subtext(self.new_ctx(m).parse(r))

        if r := m.groupdict().get("l"):
            if (len(r) - len(r.rstrip(")"))) > r.count("("):
                self.i -= 1
                r = r[:-1]
            if not (u := text_to_url(r)):
                return Text(r)
            return Link(u, None, None, m.group("ls") is not None)

        if r := m.groupdict().get("L"):
            url = text_to_url(regex.sub(r"\\([^a-zA-Z0-9\s])", r"\1", r))
            body = m.group("Lb")
            title = m.group("Lt")
            ctx = self.new_ctx(m, testing_link=True)
            if not url or not is_link_admissable(ctx, body, allow_emoji=False) or title and is_link_admissable(ctx, title, allow_emoji=True) is None:
                return Text(m[0])
            inner = Context(is_link=True).parse(clean_whitespace(body))
            return Link(url, inner, title and clean_whitespace(title), bool(m.captures("Ls")))

        if r := m.capturesdict().get("q"):
            return Quote(self.new_ctx(m, is_quote=True).parse("\n".join(r)))

        if r := m.capturesdict().get("li"):
            items = []
            bullets = m.captures("lb")
            start = None if bullets[0].strip() in "*-" else min(max(int(bullets[0].split(".")[0]), 1), 1_000_000_000)
            for bullet, item in zip(bullets, r):
                t = regex.sub("^ {1,%d}" % len(bullet), "", item, flags=regex.M)
                items.append(self.new_ctx(m, is_list=True).parse(t))
            return List(start, items)

        if r := m.groupdict().get("h"):
            title = r.rstrip().rstrip("#").rstrip()
            return Header(self.new_ctx(m).parse(title), len(m.group("hn")))

        assert False

def parse(string: str, /) -> Markup:
    """Parse a string.

    Typical usage of this library will involve calling `parse` on message content returned by the API,
    then manipulating the resulting tree somehow.

    :param string: The string to parse.
    :returns: The resulting tree.
    """
    return Context().parse(string)
