"""Full AST definition of Discord markup."""

from __future__ import annotations

from dataclasses import dataclass


__all__ = (
    "Node", "Markup",
    "Text", "Bold", "Italic", "Underline", "Spoiler",
    "Quote", "InlineCode", "Codeblock", 
    "Header1", "Header2", "Header3", 
    "RoleMention", "ChannelMention", "UserMention",
    "Everyone", "Here",
)


class Node:
    """A base class for all AST nodes."""
    __slots__ = ()

@dataclass(frozen=True, slots=True)
class Text(Node):
    """A leaf node representing plain text without any styling.

    :ivar str text: The text.
    """

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
    """Bold text (`**foo**`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

class Italic(Style):
    """Italicized text (`*foo*` or `_foo_`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

class Underline(Style):
    """Underlined text (`__foo__`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

class Spoiler(Style):
    """A spoiler (`||foo||`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

class Quote(Style):
    """A quote (`> foo`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

class Header1(Style):
    """The largest header (`# foo`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

class Header2(Style):
    """The middle-sized header (`## foo`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

class Header3(Style):
    """The smallest header (`### foo`).

    :ivar Markup inner: The inner markup.
    """
    __slots__ = ()

@dataclass(frozen=True, slots=True)
class InlineCode(Node):
    """Inline code (`` `foo` ``).

    :ivar str content: The content of the block.
    """

    content: str

    def __repr__(self):
        return f"InlineCode({self.content!r})"

@dataclass(frozen=True, slots=True)
class Codeblock(Node):
    """A codeblock (```` ```foo``` ````).

    :ivar Optional[str] language: The highlighting language specified.
    :ivar str content: The content of the block.
    """

    language: str | None
    content: str

    def __repr__(self):
        return f"Codeblock({self.language!r}, {self.content!r})"

@dataclass(frozen=True, slots=True)
class Mention(Node):
    """Base class for mentions."""

    id: int

    def __repr__(self):
        return f"{type(self)}({self.id!r})"

class UserMention(Mention):
    """A mention of a user (`<@319753218592866315>`).

    Note that only IDs are included in message content, not the name associated with the mention, so that is the only field this library can provide.

    This represents the *rendering* of the text, not whether or not it actually pings. These are not the same in all cases: `\<@319753218592866315>` will
    prevent the ping from being rendered, but the message will still ping.

    :ivar int id: The user ID.
    """
    __slots__ = ()

class ChannelMention(Mention):
    """A mention of a channel (`<#319753218592866315>`).

    Note that only IDs are included in message content, not the name associated with the mention, so that is the only field this library can provide.

    :ivar int id: The channel ID.
    """
    __slots__ = ()
    
class RoleMention(Mention):
    """A mention of a role (`<@&319753218592866315>`).

    Note that only IDs are included in message content, not the name associated with the mention, so that is the only field this library can provide.

    :ivar int id: The role ID.
    """
    __slots__ = ()

@dataclass(frozen=True, slots=True)
class Everyone(Node):
    """@everyone.

    This represents the *rendering* of the text, not whether or not it actually pings. These are not the same in all cases: `\@everyone` will
    prevent the @everyone from being rendered, but the message will still ping people.
    """

@dataclass(frozen=True, slots=True)
class Here(Node):
    """@here.

    This represents the *rendering* of the text, not whether or not it actually pings. These are not the same in all cases: `\@here` will
    prevent the @here from being rendered, but the message will still ping people.
    """

@dataclass(frozen=True, slots=True)
class Markup:
    """The main unit of rich text.

    A `Markup` is a list of one or more {class}`Node`s that make up its content. Nodes may be simple text nodes or they may be style nodes, like {class}`Bold`, that contain other `Markup`s recursively.

    :ivar list[Node] nodes: The nodes contained.
    """

    nodes: list[Node]

    def __repr__(self):
        return repr(self.nodes)
