"""Full AST definition of Discord markup."""

from __future__ import annotations

import copy
import datetime
import regex
from dataclasses import dataclass
from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from urlstd.parse import URL

# defer import to prevent circular import between string and ast
def url_to_text(url: URL) -> str:
    from .string import url_to_text
    return url_to_text(url)


__all__ = (
    "Markup", "Node", "Style",
    "Text", "Bold", "Italic", "Underline", "Spoiler", "Strikethrough",
    "Quote", "Header", "InlineCode", "Codeblock", "List", "Link",
    "UserMention", "ChannelMention", "RoleMention", "Timestamp",
    "CustomEmoji", "UnicodeEmoji", "Everyone", "Here",
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
class List(Node):
    """A list, either ordered (`1. a`) or unordered (`- a`).

    :ivar Optional[int] start: The number at which an ordered list starts, or None for an unordered list.
        All the items after the first are numbered consecutively, independently of the numbers used in the original string.
    :ivar list[Markup] items: The items in the list.
    """

    start: int | None
    items: list[Markup]

    def __repr__(self):
        return f"List({self.start}, {self.items!r})"

@dataclass(frozen=True, slots=True)
class Link(Node):
    """Hyperlinks (all of `https://example.com`, `<https://example.com>`, `[example](https://example.com)`, and `[example](<https://example.com>)`).

    :ivar urlstd.parse.URL _url: The URL referenced by the link. See {attr}`target` and {attr}`display_target`.
    :ivar Optional[Markup] inner: For `[text](url)` form links, the markup used to display the link. `None` for bare links. See {meth}`appearance`.
    :ivar Optional[str] title: For `[text](url "title")` form links, the title (text shown when the link is hovered over). `None` for other links.
    :ivar bool suppressed: Whether angle brackets were used to stop the link from being embedded.
        Note that the library has no way of knowing if the link was actually embedded or not, as embedding is serverside and outside the scope of the library.
    """

    _url: URL
    inner: Markup | None
    title: str | None
    suppressed: bool

    def __repr__(self):
        return f"Link({self.target!r}, inner={self.inner!r}, title={self.title!r}, suppressed={self.suppressed})"

    @property
    def target(self) -> str:
        """The URL one is sent to after clicking the link. Equivalent (but not necessarily equal) to the source URL."""
        return url_to_text(self._url)

    @property
    def display_target(self) -> str:
        """The URL a user is told they are going to if they click the link.
        Equal to `target` with the username and password fields stripped, e.g. (`https://user:pass@example.com/` -> `https://example.com/`).
        """
        u = copy.deepcopy(self._url)
        u.username = ""
        u.password = ""
        return url_to_text(u)

    @property
    def appearance(self) -> Markup:
        """The appearance of the link before being clicked. Equal to `text or Markup([Text(display_target)])`."""
        return self.inner or Markup([Text(self.display_target)])

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

    :ivar int timestamp: The time being referenced in Unix time.
    :ivar str format: The formatting code, a single character. `f` by default.
    """

    timestamp: int
    format: str

    def as_datetime(self) -> datetime.datetime:
        """Convert the Timestamp to an aware UTC datetime object.

        This uses {meth}`datetime.datetime.fromtimestamp` internally, which is likely to raise if the timestamp is too large or too small.
        See that method's documentation for more information.
        """
        return datetime.datetime.fromtimestamp(self.timestamp, datetime.timezone.utc)

@dataclass(frozen=True, slots=True)
class Markup:
    """The main unit of rich text.

    A `Markup` is a list of one or more {class}`Node`s that make up its content. Nodes may be simple text nodes or they may be style nodes, like {class}`Bold`, that contain other `Markup`s recursively.

    The `__str__` method forms a round-trip: while `str(parse(s))` may not be the same string as `s`, it will display identically on Discord. `parse(str(m))` will always equal `m`.

    An additional property is that the string forms of separate `Markup`s can be concatenated safely: `str(m) + str(n)` will always have the same appearance as `str(Markup(m.nodes + n.nodes))`.
    This is not always true when simply concatenating markup strings. For example, `*a` displays an asterisk followed by an `a`, and `b*` displays a `b` followed by an asterisk, but if you
    add the strings `"*a"` and `"b*"` together, you get `"*ab*"`, which would display `ab` in italic. If you instead concatenate `parse("*a")` and `parse("b*")`,
    the asterisks will be escaped and this cannot occur.

    :ivar list[Node] nodes: The nodes contained.
    """

    nodes: list[Node]

    def walk(self) -> Iterator[Node]:
        """A simple way to visit all the nodes in the tree.

        :returns: A recursive iterator of all the {class}`Node` objects in the object, in rendering order. Parents come before children.
        """
        for node in self.nodes:
            yield node
            match node:
                case Style(b):
                    yield from b.walk()
                case List(_, bs):
                    for b in bs:
                        yield from b.walk()
                case Link(inner=b) if b is not None:
                    yield from b.walk()

    def __str__(self):
        from .formatting import format_markup
        return format_markup(self)

    def __repr__(self):
        return f"<{', '.join(map(repr, self.nodes))}>"
