"""Full AST definition of Discord markup."""

from __future__ import annotations

import datetime
from dataclasses import dataclass


__all__ = (
    "Node", "Markup", "Style",
    "Text", "Bold", "Italic", "Underline", "Spoiler", "Strikethrough",
    "Quote", "Header", "InlineCode", "Codeblock",
    "RoleMention", "ChannelMention", "UserMention",
    "Timestamp", "CustomEmoji",
    "Everyone", "Here", "UnicodeEmoji",
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
    """Base class for elements that contain some other markup and add styling to it.

    :ivar Markup inner: The inner markup.
    """

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

class Strikethrough(Style):
    """Struck-through text (`~~foo~~`)."""
    __slots__ = ()

class Spoiler(Style):
    """A spoiler (`||foo||`)."""
    __slots__ = ()

class Quote(Style):
    """A quote (`> foo`)."""
    __slots__ = ()

@dataclass(frozen=True, slots=True)
class Header(Style):
    """A header (`# foo`).

    :ivar int level: The level of the header (is it `#`, `##`, or `###`)?
    """

    level: int

    def __repr__(self):
        return f"Header({self.inner!r}, {self.level})"

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

@dataclass(frozen=True, slots=True)
class Mention(Node):
    """Base class for mentions."""

    id: int

    def __repr__(self):
        return f"{type(self).__name__}({self.id!r})"

class UserMention(Mention):
    r"""A mention of a user (`<@319753218592866315>`).

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
    r"""@everyone.

    This represents the *rendering* of the text, not whether or not it actually pings. These are not the same in all cases: `\@everyone` will
    prevent the @everyone from being rendered, but the message will still ping people.
    """

@dataclass(frozen=True, slots=True)
class Here(Node):
    r"""@here.

    This represents the *rendering* of the text, not whether or not it actually pings. These are not the same in all cases: `\@here` will
    prevent the @here from being rendered, but the message will still ping people.
    """

@dataclass(frozen=True, slots=True)
class CustomEmoji(Node):
    """A custom emoji (`<:name:0>`).

    :ivar int id: The emoji ID.
    :ivar str name: The name of the emoji. This is trusted from the text and might not correspond with the actual emoji name according to the ID.
    :ivar bool animated: Whether or not the emoji is animated.
    """

    id: int
    name: str
    animated: bool

@dataclass(frozen=True, slots=True)
class UnicodeEmoji(Node):
    """A Unicode emoji (`🥺`).

    The library might not match the set of emoji supported by Discord, so it may emit `UnicodeEmoji` for emoji not supported
    by the platform. It also will not emit `UnicodeEmoji` for emoji that were escaped with backslashes.

    :ivar str char: The grapheme corresponding to the emoji. Might be multiple characters.
    """ 

    char: str

    def __repr__(self):
        return f"UnicodeEmoji({self.char!r})"

@dataclass(frozen=True, slots=True)
class Timestamp(Node):
    """A timestamp (`<t:1691280044:R>`).

    :ivar datetime.datetime time: The time being referenced as a timezone-aware UTC datetime.
    :ivar str format: The formatting code, a single character. `f` by default.
    """

    time: datetime.datetime
    format: str

@dataclass(frozen=True, slots=True)
class Markup:
    """The main unit of rich text.

    A `Markup` is a list of one or more {class}`Node`s that make up its content. Nodes may be simple text nodes or they may be style nodes, like {class}`Bold`, that contain other `Markup`s recursively.

    :ivar list[Node] nodes: The nodes contained.
    """

    nodes: list[Node]

    def __repr__(self):
        return f"<{', '.join(map(repr, self.nodes))}>"
