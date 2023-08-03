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

# asterisks
  \*(?!\s)(?P<i>(?:\\\p{Punct}|\*\*|[^*])+?)(?<!\s{3}|\n\s*)\*(?!\*)   # italics
| \*\*(?P<b>(?&some))\*\*(?!\*)  # bold
""", regex.X | regex.S | regex.VERSION1)


def _parse(s: str, /, *, at_line_start=True) -> Markup:
    i = 0
    l = []

    for m in MAIN.finditer(s):
        if sl := s[i:m.start()]:
            l.append(Text(sl))
        i = m.end()

        if r := m.group("i"):
            l.append(Italic(_parse(r)))
        if r := m.group("b"):
            l.append(Bold(_parse(r)))

    if sl := s[i:]:
        l.append(Text(sl))

    return Markup(l)

def parse(string: str, /) -> Markup:
    """Parse a string.

    Typical usage of this library will involve calling `parse` on message content returned by the API, then manipulating the resulting tree somehow.

    :param string: The string to parse.
    :returns: The resulting tree.
    """
    return _parse(string)
