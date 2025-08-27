"""Full AST definition of Discord markup."""

from __future__ import annotations

import copy
import datetime
import regex
from dataclasses import dataclass
from typing import Iterator, Iterable, Callable, TYPE_CHECKING

from .emoji import names_from_emoji

if TYPE_CHECKING:
    from ada_url import URL

# defer import to prevent circular import between string and ast
def url_to_text(url: URL) -> str:
    from .string import url_to_text
    return url_to_text(url)


__all__ = (
    "Markup", "Node", "Style",
    "Text", "Bold", "Italic", "Underline", "Spoiler", "Strikethrough",
    "Quote", "Header", "Subtext", "InlineCode", "Codeblock", "List", "Link",
    "UserMention", "ChannelMention", "RoleMention", "Timestamp",
    "CustomEmoji", "UnicodeEmoji", "Everyone", "Here",
)


class Node:
    """A base class for all AST nodes."""
    __slots__ = ()

    @property
    def inners(self) -> list[Markup]:
        """A list of the node's immediate children as {class}`Markup` objects.

        This is a single-element list for {class}`Style`s, may be any length for {class}`List`s, has 0-1 elements for {class}`Link`s, and has no elements for all other `Node`s.
        """
        match self:
            case Style(b):
                return [b]
            case Link(inner=b) if b is not None:
                return [b]
            case List(_, bs):
                return bs
            case _:
                return []

    def map(self, f: Callable[[Markup], Markup]) -> Node:
        """Apply `f` to each immediate child of this `Node`, forming a new object from the results.

        `map` is equivalent to applying `f` to each element of {meth}`inners` and making a `Node` of the same type using the results. For example,
        if `n = Italic(m)`, then `n.map(f)` is `Italic(f(m))`.

        :param function: A callable to apply to each {class}`Markup`.
        :return: A new `Node` of the same type as this one, with `f(m)` in the place of each original subtree `m`.
        """
        match self:
            case Header(b, n):
                return Header(f(b), n)
            case Style(b):
                return type(self)(f(b))
            case Link(u, b, t, s) if b is not None:
                return Link(u, f(b), t, s)
            case List(s, bs):
                return List(s, [f(x) for x in bs])
            case _:
                return self

@dataclass(slots=True)
class Text(Node):
    """A leaf node representing plain text without any styling.

    :ivar str text: The text.
    """

    text: str

    def __repr__(self):
        return repr(self.text)

@dataclass(slots=True)
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

@dataclass(slots=True)
class Header(Style):
    """A header (`# foo`).

    :ivar int level: The level of the header (is it `#`, `##`, or `###`)?
    """

    level: int

    def __repr__(self):
        return f"Header({self.inner!r}, {self.level})"

class Subtext(Style):
    """Subtext (`-# foo`)."""
    __slots__ = ()

@dataclass(slots=True)
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

@dataclass(slots=True)
class Link(Node):
    """Hyperlinks (all of `https://example.com`, `<https://example.com>`, `[example](https://example.com)`, and `[example](<https://example.com>)`).

    :ivar Optional[Markup] inner: For `[text](url)` form links, the markup used to display the link. `None` for bare links. See {attr}`appearance`.
    :ivar Optional[str] title: For `[text](url "title")` form links, the title (text shown when the link is hovered over). `None` for other links.
    :ivar bool suppressed: Whether angle brackets were used to stop the link from being embedded.
        Note that the library has no way of knowing if the link was actually embedded or not, as embedding is serverside and outside the scope of the library.
    """

    _url: URL
    inner: Markup | None
    title: str | None
    suppressed: bool

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Link):
            return False
        return (str(self._url), self.inner, self.title, self.suppressed) == (str(other._url), other.inner, other.title, other.suppressed)

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

@dataclass(slots=True)
class InlineCode(Node):
    """Inline code (`` `foo` ``).

    :ivar str content: The content of the block.
    """

    content: str

    def __repr__(self):
        return f"InlineCode({self.content!r})"

@dataclass(slots=True)
class Codeblock(Node):
    """A codeblock (```` ```foo``` ````).

    :ivar Optional[str] language: The highlighting language specified.
    :ivar str content: The content of the block.
    """

    language: str | None
    content: str

@dataclass(slots=True)
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

@dataclass(slots=True)
class Everyone(Node):
    r"""@everyone.

    This represents the *rendering* of the text, not whether or not it actually pings. These are not the same in all cases: `\@everyone` will
    prevent the @everyone from being rendered, but the message will still ping people.
    """

@dataclass(slots=True)
class Here(Node):
    r"""@here.

    This represents the *rendering* of the text, not whether or not it actually pings. These are not the same in all cases: `\@here` will
    prevent the @here from being rendered, but the message will still ping people.
    """

@dataclass(slots=True)
class CustomEmoji(Node):
    """A custom emoji (`<:name:0>`).

    :ivar int id: The emoji ID.
    :ivar str name: The name of the emoji. This is trusted from the text and might not correspond with the actual emoji name according to the ID.
    :ivar bool animated: Whether or not the emoji is animated.
    """

    id: int
    name: str
    animated: bool

@dataclass(slots=True)
class UnicodeEmoji(Node):
    """A Unicode emoji (`🥺`).

    Will not be emitted for emoji that were escaped with backslashes.

    :ivar str char: The grapheme corresponding to the emoji. Might be multiple characters.
    """ 

    char: str

    @property
    def names(self):
        """The names used by Discord for this emoji."""
        return names_from_emoji(self.char)

    def __repr__(self):
        return f"UnicodeEmoji({self.char!r})"

@dataclass(slots=True)
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

@dataclass(slots=True)
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
            for inner in node.inners:
                yield from inner.walk()

    def map(self, f: Callable[[Node], Node]) -> Markup:
        """Apply `f` to each immediate child of this `Markup`, forming a new object from the results.

        In general, `m.map(f)` is equivalent to `Markup([f(n) for n in m.nodes])`.

        Note that this function only applies to the topmost level of the tree. To descend further, you must do the recursion yourself, probably in tandem with {meth}`Node.map`.

        :param function: A callable to apply to each {class}`Node`.
        :return: A new `Markup` object with `f(n)` in place of each original node `n`.
        """
        return Markup([f(n) for n in self.nodes])

    def flat_map(self, f: Callable[[Node], Iterable[Node]]) -> Markup:
        """Apply `f` to each immediate child of this `Markup`, concatenating the results into a new object.

        When the function always returns a single-element list, `flat_map` acts like `map`: `m.flat_map(lambda x: [...])` is the same as `m.map(lambda x: ...)`.
        However, the function is able to return lists of different lengths to remove elements or insert additional ones.

        In general, `m.flat_map(f)` is equivalent to `Markup([x for n in m.nodes for x in f(n)])`.

        Note that this function only applies to the topmost level of the tree. To descend further, you must do the recursion yourself, probably in tandem with {meth}`Node.map`.

        :param function: A callable to apply to each {class}`Node`. This function should return a list or other iterable.
        :return: A new `Markup` object with the sequence `f(n)` spliced in place of each original node `n`.
        """
        return Markup([x for n in self.nodes for x in f(n)])

    def __str__(self):
        from .formatting import format_markup
        return format_markup(self)

    def __repr__(self):
        return f"<{', '.join(map(repr, self.nodes))}>"
