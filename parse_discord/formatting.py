"""Implementations of {meth}`Markup.normal_form` and {meth}`Markup.__str__`. Not exported."""

from typing import Callable, Literal

import regex

from .ast import *
from .ast import Mention
from . import limits


__all__ = ("normalize_markup", "format_markup")


def append_node(nodes: list[Node], node: Node) -> None:
    if not nodes:
        return nodes.append(node)
    match nodes[-1], node:
        case Text(x), Text(y):
            nodes[-1] = Text(x + y)
        case InlineCode(x), InlineCode(y):
            nodes[-1] = InlineCode(x + y)
        case Bold(m), Bold(n):
            nodes[-1] = Bold(Markup(cat_nodes(m.nodes, n.nodes)))
        case Underline(m), Underline(n):
            nodes[-1] = Underline(Markup(cat_nodes(m.nodes, n.nodes)))
        case List(), List():
            nodes.append(Text("\n"))
            nodes.append(node)
        case (Strikethrough(), Underline()) | (InlineCode(), Codeblock()):
            nodes.append(Text(" "))
            nodes.append(node)
        # only one case where a link doesn't need a forced space
        case (Link(), Text(t)) if regex.match(r"""[<.,:;"'\]\s)]""", t):
            nodes.append(node)
        # could suppress alternatively, which looks better, but the change in functionality sounds more annoying to me
        case (Link(), Text(t)):
            nodes.append(Text(" " + t))
        case (Link(), _):
            nodes.append(Text(" "))
            nodes.append(node)
        # pattern continues where it's easier to list ok cases than bad ones
        case (Text(t), List() | Quote()) if t.endswith(("\n", " ")):
            nodes.append(node)
        case (Text(t), Subtext() | Header()) if t.endswith("\n"):
            nodes.append(node)
        case (List() | Quote() | Subtext() | Header(), List() | Quote() | Subtext() | Header()) if not isinstance(node, Quote) or not isinstance(nodes[-1], Quote):
            nodes.append(node)
        case (b4, List() | Quote() | Subtext() | Header()):
            if isinstance(b4, Text):
                nodes[-1] = Text(b4.content + "\n")
            else:
                nodes.append(Text("\n"))
            nodes.append(node)
        case _:
            nodes.append(node)

def extend_nodes(xs: list[Node], ys: list[Node]) -> None:
    append_node(xs, ys[0])
    xs.extend(ys[1:])

def cat_nodes(xs: list[Node], ys: list[Node]) -> list[Node]:
    if not ys:
        return xs
    new = xs[:]
    extend_nodes(new, ys)
    return new

def one_line(codeblock: Codeblock) -> bool:
    return not codeblock.language and "\n" not in codeblock.content and not codeblock.content.endswith("`")

def lines(markup: Markup) -> list[Markup]:
    r = [Markup([])]

    for node in markup.nodes:
        match node:
            case Text(s):
                node_lines = [Markup([Text(x)]*bool(x)) for x in s.split("\n")]
            case InlineCode(c):
                node_lines = [Markup([InlineCode(x)]*bool(x)) for x in c.split("\n")]
            case Codeblock():
                if not r[-1]:
                    r[-1] = Markup([node])
                else:
                    r.append(Markup([node]))
                r.append(Markup([]))
                continue
            case Quote(inner) | Subtext(inner):
                node_lines = [Markup([type(node)(x)]) for x in lines(inner)]
                # implicit line after these "block elements"
                node_lines.append(Markup([]))
            case Header(inner, l):
                node_lines = [Markup([Header(x, l)]) for x in lines(inner)]
                node_lines.append(Markup([]))
            case Style(inner):
                node_lines = [Markup([type(node)(x)]) for x in lines(inner)]
            case Link(_url=u, inner=b, title=t, suppressed=s) if b is not None:
                node_lines = [Markup([Link._from_ada_url(u, x, t, s)]) for x in lines(b)]
            case List(xs, n):
                node_lines = [y for i, x in enumerate(xs) for l in [lines(x)] for y in [Markup([List([l[0]], None if n is None else n + i)]), *l[1:]]]
                node_lines.append(Markup([]))
            case _:
                node_lines = [Markup([node])]

        r[-1].nodes.extend(node_lines[0].nodes)
        r.extend(node_lines[1:])

    return r

def cover(nodes: list[Node], markup: Markup, style: Callable[[Markup], Node]) -> None:
    ls = lines(markup)
    if not ls[-1].nodes:
        ls.pop()
    for line in ls:
        if not line:
            append_node(nodes, Text("\n"))
        elif any([isinstance(x, Codeblock) and not one_line(x) for x in line.walk()]):
            extend_nodes(nodes, line.nodes)
        else:
            ns = line.nodes
            if isinstance(ns[0], Text):
                ns[:1] = [Text(s := ns[0].content.lstrip())]*bool(s)
            if isinstance(ns[-1], Text):
                ns[-1:] = [Text(s := ns[-1].content.rstrip())]*bool(s)
            append_node(nodes, style(line))


def normalize_markup(markup: Markup, *, clean: set[type[Style]]) -> Markup:
    nodes = []

    for node in [y for x in markup.nodes for y in (x.inner.nodes if isinstance(x, tuple(clean)) else [x])]:
        match node.map(lambda n, clean=clean | {type(node)} if isinstance(node, Style) else clean: normalize_markup(n, clean=clean)):
            case Text("") | InlineCode("") | Style(Markup([])) | Link(inner=Markup([])) if not isinstance(node, Quote):
                continue
            case List(xs) if all(not x.nodes for x in xs):
                continue
            case Codeblock(c, l):
                if l is not None and not regex.fullmatch(r"[a-zA-Z_\-+.0-9]+", l):
                    l = None
                node = Codeblock(" "*c.startswith("\n") + (c or " ") + " "*c.endswith("\n"), l)
            case CustomEmoji(i, n, a):
                # name doesn't really matter so just mangle it, we can still display if the rest is ok
                node = CustomEmoji(i, regex.sub(r"[^a-zA-Z_0-9]+", "", n) or "blank", a)
            case Timestamp(t, f):
                node = Timestamp(min(max(t, limits.MIN_TIMESTAMP), limits.MAX_TIMESTAMP), f if f in ("t", "T", "d", "D", "f", "F", "R") else "f")
            case Link(_url=u, inner=b, title="", suppressed=s) | Link(_url=u, inner=None as b, suppressed=s):
                node = Link._from_ada_url(u, b, None, s)
            case List(xs, n) if n is not None:
                node = List(xs, min(max(n, 1), limits.MAX_LIST_INDEX))
            case Header(inner, level):
                level: Literal[1, 2, 3] = level  # ???
                cover(nodes, inner, lambda n: Header(n, level))
                continue
            case Subtext(inner):
                cover(nodes, inner, Subtext)
                continue
            case node:
                pass
        append_node(nodes, node)

    return Markup(nodes)


PERCENT_TRANSLATION = str.maketrans({"_": "%5F", "*": "%2A", "|": "%7C", "~": "%7E", "<": "%3C"})
END_PERCENT_TRANSLATION = {".": "%2E", ",": "%2C", ":": "%3A", ";": "%3B", '"': "%22", "'": "%27", "]": "%5D"}

def indent(m: str, w: str) -> str:
    return "".join(f"{w}{x}\n" for x in m.split("\n"))

def format_markup(markup: Markup, *, escapes: bool = True) -> str:
    def recur(markup: Markup) -> str:
        return format_markup(markup, escapes=escapes)

    nodes = markup.nodes

    out = ""
    for idx, node in enumerate(nodes):
        is_middle = idx != len(nodes)-1
        nxt = nodes[idx+1] if is_middle else None
        def middled(s):
            return s if is_middle else s[:-1]

        match node:
            case Text(t):
                # when inside a [text](url) link (escapes = False), escapes don't work at all, so don't insert them
                out += regex.sub(r"([*\-_<:[`\\\p{Emoji_Presentation}]|@(?:here|everyone)|\|\||~~)", r"\\\1", t) if escapes else t
            case Header(b, n):
                out += middled(f"{'#'*n} {recur(b)} #\n")
            case Subtext(b):
                out += middled(f"-# {recur(b)}\n")
            case Quote(b):
                out += middled(indent(recur(b), "> "))
            case Style(b):
                match node:
                    case Bold():
                        outer = "**"
                    case Italic():
                        # in general, _ is much more sensible than * and works without issue in most contexts.
                        # however, it doesn't work if the closing _ is followed by an alphanumeric character,
                        # so we must use * in these cases instead. it's also necessary to use * to avoid conflict
                        # with surrounding italics, underlines, or strikethroughs.
                        prv = nodes[idx-1] if idx else None
                        match prv, nxt:
                            case _, Text(t) if regex.match("[a-zA-Z0-9_]", t):
                                outer = "*"
                            case (Bold() | Italic(), _) if out[-1] == "*":
                                outer = "_"
                            case (_, Underline()) | (Italic() | Strikethrough() | Underline(), _):
                                outer = "*"
                            case _:
                                outer = "_"
                    case Underline(Markup([Italic(b)])):
                        # silly special case
                        out += f"__*{recur(b)}*__"
                        continue
                    case Underline():
                        outer = "__"
                    case Strikethrough():
                        outer = "~~"
                    case Spoiler():
                        outer = "||"
                    case _:
                        assert False
                out += f"{outer}{recur(b)}{outer}"
            case List(bs, s):
                bullet = f"{s}. " if s else "- "
                out += middled("".join(f"{bullet}{indent(recur(b), ' '*len(bullet))[len(bullet):]}" for b in bs))
            case Link(target=l, inner=b, title=t, suppressed=s):
                l = l.translate(PERCENT_TRANSLATION)
                if l[-1] in END_PERCENT_TRANSLATION:
                    l = l[:-1] + END_PERCENT_TRANSLATION[l[-1]]
                url = f"<{l}>" if s else l
                if s:
                    url = f"<{l}>"
                # odd edge case
                # if the source string was "https://(a))", this is parsed as the url "https://(a)" followed by a literal ")"
                # but Link doesn't store the original text of the URL, and if we naively output it in normalized form,
                # a slash is put at the end of the URL and the result would be "https://(a)/)". since the first closing paren
                # is no longer at the end of the string, it isn't counted as nullifying the ( and this string is parsed as a
                # single url "https://(a)/)", breaking the round-trip property. so we check for this case and remove the
                # trailing slash if it occurs.
                elif isinstance(nxt, Text) and nxt.content.startswith(")"):
                    url = l.removesuffix("/")
                else:
                    url = l
                if t:
                    url += f' "{t}"'
                out += f"[{format_markup(b, escapes=False)}]({url})" if b else url
            case InlineCode(c):
                groups = regex.findall("`+", c)
                outer = "`"
                while outer in groups:
                    outer += "`"
                start = " " * c.lstrip(" ").startswith("`")
                end = " " * c.rstrip(" ").endswith("`")
                out += f"{outer}{start}{c}{end}{outer}"
            case Codeblock(c, l):
                l = l or ""
                if one_line(node):
                    out += f"```{c}```"
                else:
                    out += f"```{l}\n{c}\n```"
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
                out += f"<t:{t}{form}>"
            case UnicodeEmoji(t):
                out += t
            case CustomEmoji(i, n, a):
                out += f"<{'a'*a}:{n}:{i}>"
            case Everyone():
                out += "@everyone"
            case Here():
                out += "@here"
    return out
