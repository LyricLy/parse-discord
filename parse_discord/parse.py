"""String parsing logic."""

from __future__ import annotations

from typing import Generator

import regex

from .ast import *


__all__ = ("parse",)

MAIN = regex.compile(r"""
# utility definitions
(?(DEFINE)
    (?<some>(?:\\\p{Punct}|.)+?)
)

# skip escapes
(?:\\.(*SKIP)(*F))?

# asterisks
  \*(?!\s)(?<i>(?:\\\p{Punct}|\*\*|[^*\\])+?)(?<!\s{3}|\n\s*)\*(?!\*)   # italics
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
""", regex.X | regex.S | regex.POSIX | regex.VERSION1)


def append_text(l, t):
    if t:
        l.append(Text(regex.sub(r"\\(\p{Punct})", r"\1", t)))

def _parse(s: str, /, *, start="") -> Generator[tuple[str, str, regex.Match], Markup | None, Markup]:
    i = len(start)
    s = start + s
    l = []

    for m in MAIN.finditer(s, i):
        append_text(l, s[i:m.start()])
        i = m.end()

        for g, ty in [("i", Italic), ("b", Bold), ("u", Underline), ("s", Spoiler)]:
            if r := m.group(g):
                l.append(ty((yield r, s, m)))
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
                l.append(ty((yield title, s, m)))

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
            r, s, m = stack[-1].send(current_value)
        except StopIteration as e:
            stack.pop()
            current_value = e.value
            if not stack:
                return current_value
        else:
            # cut off the start of the line before the match
            # see tests/headers.py:test_even_through_asterisks for why we're doing this
            line_start = s[max(s.rfind("\n", 0, m.start()), 0):m.start()]
            stack.append(_parse(r, start=line_start))
            
