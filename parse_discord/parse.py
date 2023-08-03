"""String parsing logic."""

from __future__ import annotations

import regex

from .ast import *


__all__ = ("parse",)

MAIN = regex.compile(r"""
# escape-aware definitions
(?(DEFINE)
    (?P<c>\\\p{Punct}|.)
    (?P<many>(?&c)*?)
    (?P<some>(?&c)+?)
)

# skip escapes
(?:\\.(*SKIP)(*F))?

# asterisks
  \*(?!\s)(?P<i>(?:\\\p{Punct}|\*\*|[^*\\])+?)(?<!\s{3}|\n\s*)\*(?!\*)   # italics
| \*\*(?P<b>(?&some))\*\*(?!\*)  # bold
""", regex.X | regex.S | regex.POSIX | regex.VERSION1)


def _append_text(l, t):
    if t:
        l.append(Text(regex.sub(r"\\(.)", r"\1", t)))

def _parse(s: str, /, *, at_line_start=True) -> Markup:
    i = 0
    l = []

    for m in MAIN.finditer(s):
        _append_text(l, s[i:m.start()])
        i = m.end()

        if r := m.group("i"):
            l.append(Italic(_parse(r)))
        if r := m.group("b"):
            l.append(Bold(_parse(r)))

    _append_text(l, s[i:])
    return Markup(l)

def parse(string: str, /) -> Markup:
    """Parse a string.

    Typical usage of this library will involve calling `parse` on message content returned by the API, then manipulating the resulting tree somehow.

    :param string: The string to parse.
    :returns: The resulting tree.
    """
    return _parse(string)
