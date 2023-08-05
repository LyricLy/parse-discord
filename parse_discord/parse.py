"""String parsing logic."""

from __future__ import annotations

from enum import Enum
from typing import Generator, Any

import regex

from .ast import *


__all__ = ("parse",)

main_source = r"""
# utility definitions
(?(DEFINE)
    (?<some>(?:\\\p{Punct}|.)+?)
)

# skip escapes
(?:\\.(*SKIP)(*F))?

# asterisks
  \*(?!\s)(?<i>(?:\\\p{Punct}|\*\*|[^*\\])+?)(?<!\s)\ {0,2}\*(?!\*)   # italics
| \*\*(?<b>(?&some))\*\*(?!\*)  # bold

# underscores, basically the same deal
| _(?<i>(?:\\\p{Punct}|__|[^_\\])+?)_(?!_)  # italics (doesn't have the same weird whitespace rules as asterisks)
| __(?<u>(?&some))__(?!_)  # underline

# spoilers
| \|\|(?<s>(?&some))\|\|

# backticks
| (?<x>`{1,2})(?<c>.+?)(?<!`)\g<x>(?!`)  # inline code
| ```(?:(?<l>[a-zA-Z_\-+.0-9]*)\n)?(?<cb>.+?)```  # codeblock

# headers
| ^(?<ty>\#{1,3})\s+(?!\#)(?<h>[^\n]*)\n?

# quotes
%s
"""

quote_source = r"""
| (?:(?<=^ *)>\ (?<q>[^\n]*)\n?)+  # line
| (?<=^ *)>>>\ (?<q>.*)  # block
"""

flags = regex.X | regex.S | regex.M | regex.POSIX | regex.VERSION1
# we're using % for this because format uses braces and we need those for regex. doubling them up is too ugly
main_regex = regex.compile(main_source % quote_source, flags)
main_regex_wo_quotes = regex.compile(main_source % "", flags)


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
    """

    def __init__(self, line_start: LineStart = LineStart.NOTHING, is_quote: bool = False):
        self.line_start = line_start
        self.is_quote = is_quote

    def update(self, s: str, i: int, *, is_quote: bool = False) -> Context:
        # once in a quote, always in a quote
        is_quote = self.is_quote or is_quote
        line_start = LineStart.NOTHING
        while True:
            i -= 1
            if i < 0 or s[i] == "\n":
                break
            if s[i] != " ":
                line_start = LineStart.TEXT
                break
            line_start = LineStart.SPACE
        return Context(line_start, is_quote)

    def parse(self, s: str) -> tuple[Any, str, int]:
        if self.line_start == LineStart.NOTHING:
            start = ""
        elif self.line_start == LineStart.SPACE:
            start = " "
        else:
            start = "$"
        i = len(start)
        s = start + s
        r = main_regex if not self.is_quote else main_regex_wo_quotes
        return r.finditer(s, i), s, i


def append_text(l: list[Node], t: str):
    if t:
        l.append(Text(regex.sub(r"\\(\p{Punct})| +(?=\n)", r"\1", t)))

def _parse(s: str, context: Context = Context(), /) -> Generator[tuple[str, Context], Markup | None, Markup]:
    l = []

    it, s, i = context.parse(s)
    for m in it:
        append_text(l, s[i:m.start()])
        i = m.end()

        for g, ty in [("i", Italic), ("b", Bold), ("u", Underline), ("s", Spoiler)]:
            if r := m.group(g):
                l.append(ty((yield r, context.update(s, m.start()))))
                break
        else:
            if r := m.group("c"):
                s = r.strip(" ")
                if s[0] == "`":
                    r = r.removeprefix(" ")
                if s[-1] == "`":
                    r = r.removesuffix(" ")
                l.append(InlineCode(r))
            elif r := m.group("cb"):
                l.append(Codeblock(m.group("l") or None, r.strip()))
            elif r := m.group("h"):
                ty = [Header1, Header2, Header3][len(m.group("ty"))-1]
                title = r.rstrip().rstrip("#").rstrip()
                l.append(ty((yield title, context.update(s, m.start()))))
            elif r := m.captures("q"):
                l.append(Quote((yield "\n".join(r).rstrip(" "), context.update(s, m.start(), is_quote=True))))

    append_text(l, s[i:])
    return Markup(l)

def parse(string: str, /) -> Markup:
    """Parse a string.

    Typical usage of this library will involve calling `parse` on message content returned by the API, then manipulating the resulting tree somehow.

    :param string: The string to parse.
    :returns: The resulting tree.
    """
    # manually implement recursion on the heap to avoid stack overflow
    stack = [_parse(string)]
    current_value = None
    while True:
        try: 
            r, c = stack[-1].send(current_value)
        except StopIteration as e:
            stack.pop()
            current_value = e.value
            if not stack:
                return current_value
        else:
            stack.append(_parse(r, c))
            
