"""Implementation of `Markup.__str__`. Not exported."""

import regex

from .ast import *
from .ast import Mention


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
                out += regex.sub(r"([*_<@:[`\\\p{Emoji_Presentation}]|\|\||~~)", r"\\\1", t) if escapes else t
            case Header(b, n):
                out += middled(f"{'#'*n} {recur(b)} #\n")
            case Quote(b):
                out += middled(indent(recur(b), "> "))
            case Style(b):
                match node:
                    case Bold():
                        outer = "**"
                    case Italic():
                        # in general, _ is much more sensible than * and works without issue in most contexts.
                        # however, it doesn't work if the closing _ is followed by an alphanumeric character,
                        # so we must use * in these cases instead.
                        match nxt:
                            case Text(t) if regex.match("[a-zA-Z0-9_]", t):
                                outer = "*"
                            case _:
                                outer = "_"
                    case Underline():
                        outer = "__"
                    case Strikethrough():
                        outer = "~~"
                    case Spoiler():
                        outer = "||"
                    case _:
                        assert False
                out += f"{outer}{recur(b)}{outer}"
            case List(s, bs):
                bullet = f"{s}. " if s else "- "
                out += middled("".join(f"{bullet}{indent(recur(b), ' '*len(bullet))[len(bullet):]}" for b in bs))
            case Link(target=l, inner=b, title=t, suppressed=s):
                url = f"<{l}>" if s else l
                # odd edge case
                # if the source string was "https://(a))", this is parsed as the url "https://(a)" followed by a literal ")"
                # but Link doesn't store the original text of the URL, and if we naively output it in normalized form,
                # a slash is put at the end of the URL and the result would be "https://(a)/)". since the first closing paren
                # is no longer at the end of the string, it isn't counted as nullifying the ( and this string is parsed as a
                # single url "https://(a)/)", breaking the round-trip property. so we check for this case and remove the
                # trailing slash if it occurs.
                match nxt:
                    case Text(x) if x.startswith(")"):
                        url = url.removesuffix("/")
                if t:
                    url += f' "{t}"'
                out += f"[{format_markup(b, escapes=False)}]({url})" if b else url
            case InlineCode(c):
                outer = "``" if regex.search("(?<!`)`(?!`)", c) else "`"
                start = " " * c.lstrip(" ").startswith("`")
                end = " " * c.rstrip(" ").endswith("`")
                out += f"{outer}{start}{c}{end}{outer}"
            case Codeblock(l, c):
                l = l or ""
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
