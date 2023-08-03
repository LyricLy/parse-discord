"""String parsing logic."""

from __future__ import annotations

import regex

from .ast import *


__all__ = ("parse",)

MAIN = regex.compile(r"""
# escape-aware definitions
(?(DEFINE)
    (?<ch>\\\p{Punct}|.)
    (?<some>(?&ch)+?)
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
| (?<x>`{1,2})(?!`)(?<c>.+?)(?<!`)\g<x>(?!`)  # inline code
| ```(?:(?<l>[a-zA-Z_\-+.0-9]*)\n)?(?<cb>.+?)```  # codeblock
""", regex.X | regex.S | regex.POSIX | regex.VERSION1)


def _append_text(l, t):
    if t:
        l.append(Text(regex.sub(r"\\(\p{Punct})", r"\1", t)))

def _parse(s: str, /, *, at_line_start=True) -> Markup:
    i = 0
    l = []

    for m in MAIN.finditer(s):
        _append_text(l, s[i:m.start()])
        i = m.end()

        for (g, ty) in [("i", Italic), ("b", Bold), ("u", Underline), ("s", Spoiler)]:
            if r := m.group(g):
                l.append(ty(_parse(r)))
                break
        else:
            if r := m.group("c"):
                l.append(InlineCode(r))
            elif r := m.group("cb"):
                l.append(Codeblock(m.group("c") or None, r.strip()))

    _append_text(l, s[i:])
    return Markup(l)

def parse(string: str, /) -> Markup:
    """Parse a string.

    Typical usage of this library will involve calling `parse` on message content returned by the API, then manipulating the resulting tree somehow.

    :param string: The string to parse.
    :returns: The resulting tree.
    """
    return _parse(string)
