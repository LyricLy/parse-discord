"""Full AST definition of Discord markup."""

from __future__ import annotations

from dataclasses import dataclass


__all__ = ("Node", "Text", "Bold", "Italic", "Underline", "Spoiler", "InlineCode", "Codeblock", "Header1", "Header2", "Header3", "Markup")


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
    """Bold text (`**foo**`)."""
    __slots__ = ()

class Italic(Style):
    """Italicized text (`*foo*` or `_foo_`)."""
    __slots__ = ()

class Underline(Style):
    """Underlined text (`__foo__`)."""
    __slots__ = ()

class Spoiler(Style):
    """A spoiler (`||foo||`)."""
    __slots__ = ()

class Header1(Style):
    """The largest header (`# foo`)."""
    __slots__ = ()

class Header2(Style):
    """The middle-sized header (`## foo`)."""
    __slots__ = ()

class Header3(Style):
    """The smallest header (`### foo`)."""
    __slots__ = ()

@dataclass(frozen=True, slots=True)
class InlineCode(Node):
    """Inline code (`` `foo` ``)."""

    content: str

    def __repr__(self):
        return f"InlineCode({self.content!r})"

@dataclass(frozen=True, slots=True)
class Codeblock(Node):
    """A codeblock (```` ```foo``` ````)."""

    language: str | None
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
