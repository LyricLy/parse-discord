"""Full AST definition of Discord markup."""

from __future__ import annotations

import datetime
import regex
from dataclasses import dataclass
from typing import Iterator


__all__ = (
    "Markup", "Node", "Style",
    "Text", "Bold", "Italic", "Underline", "Spoiler", "Strikethrough",
    "Quote", "Header", "InlineCode", "Codeblock", "List",
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

def indent(m, w):
    return "".join(f"{w}{x}\n" for x in str(m).split("\n"))

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

    def __str__(self):
        out = ""
        for idx, node in enumerate(self.nodes):
            is_middle = idx != len(self.nodes)-1
            def middled(s):
                return s if is_middle else s[:-1]
            match node:
                case Text(t):
                    # this could be less aggressive to save on character count
                    out += regex.sub(r"([^A-Za-z0-9\s])", r"\\\1", t)
                case Header(b, n):
                    out += middled(f"{'#'*n} {b} #\n")
                case Quote(b):
                    out += middled(indent(b, "> "))
                case Style(b):
                    match node:
                        case Bold():
                            outer = "**"
                        case Italic():
                            # in general, _ is much more sensible than * and works without issue in most contexts.
                            # however, it doesn't work if the closing _ is followed by an alphanumeric character,
                            # so we must use * in these cases instead.
                            if is_middle and isinstance(nxt := self.nodes[idx+1], Text) and regex.match("[a-zA-Z0-9_]", nxt.text):
                                outer = "*"
                            else:
                                outer = "_"
                        case Underline():
                            outer = "__"
                        case Strikethrough():
                            outer = "~~"
                        case Spoiler():
                            outer = "||"
                        case _:
                            assert False
                    out += f"{outer}{b}{outer}"
                case List(s, bs):
                    bullet = f"{s}. " if s else "- "
                    out += middled("".join(f"{bullet}{indent(x, ' '*len(bullet))[len(bullet):]}" for x in bs))
                case InlineCode(c):
                    outer = "``" if regex.search("(?<!`)`(?!`)", c) else "`"
                    start = " " * c.lstrip(" ").startswith("`")
                    end = " " * c.rstrip(" ").endswith("`")
                    out += f"{outer}{start}{c}{end}{outer}"
                case Codeblock(None, c):
                    out += f"```{c}```"
                case Codeblock(l, c):
                    out += f"```{l}\n{c}```"
                case Mention(i):
                    match node:
                        case UserMention():
                            symbol = "@"
                        case ChannelMention():
                            symbol = "#"
                        case RoleMention():
                            symbol = "@&"
                        case _:
                            assert False
                    out += f"<{symbol}{i}>"
                case Timestamp(t, f):
                    form = f":{f}" * (f != "f")
                    out += f"<t:{t.timestamp():.0f}{form}>"
                case UnicodeEmoji(t):
                    out += t
                case CustomEmoji(i, n, a):
                    out += f"<{'a'*a}:{n}:{i}>"
                case Everyone():
                    out += "@everyone"
                case Here():
                    out += "@here"
        return out

    def __repr__(self):
        return f"<{', '.join(map(repr, self.nodes))}>"
