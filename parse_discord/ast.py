"""Full AST definition of Discord markup."""

from __future__ import annotations

from dataclasses import dataclass


__all__ = ("Node", "Text", "Bold", "Italic", "Underline", "InlineCode", "Codeblock", "Markup")


class Node:
    """A base class for all AST nodes."""

@dataclass(frozen=True, slots=True)
class Text(Node):
    """A leaf node representing plain text without any styling."""

    text: str

    def __repr__(self):
        return repr(self.text)

@dataclass(frozen=True, slots=True)
class Style(Node):
    """Base class for elements that contain some other markup and add styling to it."""

    inner: Markup

    def __repr__(self):
        return f"{type(self).__name__}({self.inner!r})"

class Bold(Style):
    """Bold text."""
    __slots__ = ()

class Italic(Style):
    """Italicized text."""
    __slots__ = ()

class Underline(Style):
    """Underlined text."""
    __slots__ = ()

class InlineCode(Style):
    """Inline code."""
    __slots__ = ()

class Spoiler(Style):
    """A spoiler."""
    __slots__ = ()

@dataclass(frozen=True, slots=True)
class Codeblock:
    """A codeblock."""

    language: str
    content: str

    def __repr__(self):
        return f"Codeblock({self.language!r}, {self.content!r})"

@dataclass(frozen=True, slots=True)
class Markup:
    """The main unit of rich text.

    A `Markup` is a list of one or more {class}`Node`s that make up its content. Nodes may be simple text nodes or they may be style nodes, like {class}`Bold`, that contain other `Markup`s recursively.
    """

    nodes: list[Node]

    def __repr__(self):
        return repr(self.nodes)
