import unittest

from urlstd.parse import URL

from parse_discord import *


def u(url, inner=None, title=None, suppressed=False):
    return Link(URL(url), inner, title, suppressed)

class Links(unittest.TestCase):
    def test_bare(self):
        self.assertEqual(parse("https://example.com"), Markup([u("https://example.com")]))

    def test_not_single_char(self):
        self.assertEqual(parse("http://a"), Markup([Text("http://a")]))
        self.assertEqual(parse("http://a."), Markup([Text("http://a.")]))
        self.assertEqual(parse("http://a)"), Markup([u("http://a"), Text(")")]))

    def test_no_ending_special(self):
        self.assertEqual(parse("http://ab."), Markup([u("http://ab"), Text(".")]))

    def test_no_ending_unmatched_close_paren(self):
        self.assertEqual(parse("https://ab)"), Markup([u("https://ab"), Text(")")]))
        self.assertEqual(parse("https://a))"), Markup([u("https://a)"), Text(")")]))
        self.assertEqual(parse("https://(a)"), Markup([u("https://(a)")]))
        self.assertEqual(parse("https://(a))"), Markup([u("https://(a)"), Text(")")]))
        # yes, this is correct! close parens are only counted at the end
        self.assertEqual(parse("https://(a)b)"), Markup([u("https://(a)b)")]))
        self.assertEqual(parse("https://a)."), Markup([u("https://a"), Text(").")]))
        self.assertEqual(parse("https://a.)"), Markup([u("https://a."), Text(")")]))

    def test_steam(self):
        self.assertEqual(parse("steam://*a*"), Markup([Text("steam://*a*")]))

    def test_bogus(self):
        self.assertEqual(parse("blah://*a*"), Markup([Text("blah://"), Italic(Markup([Text("a")]))]))

    def test_suppressed(self):
        self.assertEqual(parse("<https://a>"), Markup([u("https://a", suppressed=True)]))

    def test_suppressed_bogus(self):
        self.assertEqual(parse("<blah:/*a*>"), Markup([Text("blah:/*a*")]))
        self.assertEqual(parse("<blah:*a*>"), Markup([Text("<blah:"), Italic(Markup([Text("a")])), Text(">")]))

    def test_qualified(self):
        self.assertEqual(parse("[a](https://example.com)"), Markup([u("https://example.com", inner=Markup([Text("a")]))]))

    def test_qualified_bogus(self):
        self.assertEqual(parse("[a](blah://b)"), Markup([Text("[a](blah://b)")]))

    def test_qualified_short(self):
        self.assertEqual(parse("[a](https://)"), Markup([Text("[a](https://)")]))
        self.assertEqual(parse("[a](discord://)"), Markup([u("discord://", inner=Markup([Text("a")]))]))

    def test_qualified_suppressed(self):
        self.assertEqual(parse("[a](<https://b>)"), Markup([u("https://b", inner=Markup([Text("a")]), suppressed=True)]))
        self.assertEqual(parse("[a](<https://b)"), Markup([u("https://b", inner=Markup([Text("a")]), suppressed=True)]))
        self.assertEqual(parse("[a](https://b>)"), Markup([u("https://b", inner=Markup([Text("a")]), suppressed=True)]))

    def test_title(self):
        self.assertEqual(parse("[a](http://b 'c')"), Markup([u("http://b", inner=Markup([Text("a")]), title="c")]))
        self.assertEqual(parse("[a](http://b ''')"), Markup([u("http://b", inner=Markup([Text("a")]), title="'")]))
        self.assertEqual(parse("[a](http://b> \"c')"), Markup([u("http://b", inner=Markup([Text("a")]), title="c", suppressed=True)]))

    def test_whitespace_allowance(self):
        self.assertEqual(parse("[ a ]( https://b  ' c ' )"), Markup([u("https://b", inner=Markup([Text(" a ")]), title=" c ")]))

    def test_bracket_parsing(self):
        self.assertEqual(parse("[[]](http://b)"), Markup([u("http://b", inner=Markup([Text("[]")]))]))
        self.assertEqual(parse("[[a](http://b)"), Markup([Text("["), u("http://b", inner=Markup([Text("a")]))]))
        self.assertEqual(parse("[[[]](http://b)"), Markup([u("http://b", inner=Markup([Text("[[]")]))]))
        self.assertEqual(parse("[[][]]](http://b)"), Markup([u("http://b", inner=Markup([Text("[][]]")]))]))
        self.assertEqual(parse("[[]][]](http://b)"), Markup([Text("[[]]"), u("http://b", inner=Markup([Text("]")]))]))

    def test_prevents_blocks(self):
        self.assertEqual(parse("[# a](http://b)"), Markup([u("http://b", inner=Markup([Text("# a")]))]))
        self.assertEqual(parse("[> a](http://b)"), Markup([u("http://b", inner=Markup([Text("> a")]))]))
        self.assertEqual(parse("[* a](http://b)"), Markup([u("http://b", inner=Markup([Text("* a")]))]))

    def test_with_newlines(self):
        self.assertEqual(parse("[a\n> b](http://c)"), Markup([u("http://c", inner=Markup([Text("a\n> b")]))]))

    def test_sanitization(self):
        self.assertEqual(parse("[a\N{IDEOGRAPHIC SPACE}b](http://c 'd\N{IDEOGRAPHIC SPACE}e')"), Markup([u("http://c", inner=Markup([Text("ab")]), title="de")]))

    def test_prevents_escapes(self):
        self.assertEqual(parse(r"[\*\**](http://a)"), Markup([u("http://a", inner=Markup([Text("\\"), Italic(Markup([Text(r"\*")]))]))]))

    def test_antiphish(self):
        # no links
        self.assertEqual(parse("[http://ab](http://c)"), Markup([Text("[http://ab](http://c)")]))
        self.assertEqual(parse("[ｈttp://ab](http://c)"), Markup([Text("[ｈttp://ab](http://c)")]))
        self.assertEqual(parse("[`http://ab`](http://c)"), Markup([Text("[`http://ab`](http://c)")]))
        # no blocks
        self.assertEqual(parse("[```a```](http://b)"), Markup([Text("[```a```](http://b)")]))
        # timestamps okay!
        self.assertEqual(parse("[<t:0>](http://a)"), Markup([u("http://a", inner=Markup([Timestamp(0, "f")]))]))
        # same rules in title
        self.assertEqual(parse("[a](http://b 'http://ab')"), Markup([Text("[a](http://b 'http://ab')")]))
        self.assertEqual(parse("[a](http://b 'ｈttp://ab')"), Markup([Text("[a](http://b 'ｈttp://ab')")]))
        self.assertEqual(parse("[a](http://b '`http://ab`')"), Markup([Text("[a](http://b '`http://ab`')")]))
        self.assertEqual(parse("[a](http://b '```a```')"), Markup([Text("[a](http://b '```a```')")]))
        self.assertEqual(parse("[a](http://b '<t:0>')"), Markup([u("http://b", inner=Markup([Text("a")]), title="<t:0>")]))

    def test_no_empty(self):
        self.assertEqual(parse("[|| ||_ _** **` `](http://a)"), Markup([Text("[|| ||_ _** **` `](http://a)")]))

    def test_emoji_ban(self):
        self.assertEqual(parse("[🥺](https://a)"), Markup([Text("[🥺](https://a)")]))
        # allowed in title
        self.assertEqual(parse("[a](https://b '🥺')"), Markup([u("https://b", inner=Markup([Text("a")]), title="🥺")]))
        # allowed in inline code
        self.assertEqual(parse("[`🥺`](https://a)"), Markup([u("https://a", inner=Markup([InlineCode("🥺")]))]))

    def test_wonderland(self):
        # a bug in the validation of the text part of these links allows you to place anything you want
        # inside them, as long as it's inside a list. because the parsing done by links has most
        # of the syntax rules disabled, this allows you to demonstrate a number of things about
        # the parser that would otherwise be unobservable. I dub this "wonderland".

        # inline code blocks with more than 2 backticks
        self.assertEqual(parse("[- ```a```](http://b)"), Markup([u("http://b", inner=Markup([Text("- "), InlineCode("a")]))]))
        self.assertEqual(parse("[- `````a`````](http://b)"), Markup([u("http://b", inner=Markup([Text("- "), InlineCode("a")]))]))

        # "links" with formatting in them!
        self.assertEqual(parse("[- https://**a**](http://a)"), Markup([u("http://a", inner=Markup([Text("- https://"), Bold(Markup([Text("a")]))]))]))

        # emoji!
        self.assertEqual(parse("[- 🥺](http://a)"), Markup([u("http://a", inner=Markup([Text("- "), UnicodeEmoji("🥺")]))]))

    def test_link_scourge(self):
        self.assertEqual(parse("[\\*[*a\n1. b](https://c)](https://d)"), Markup([u("https://d", inner=Markup([Text("\\"), Italic(Markup([Text("[")])), Text("a\n1. b](https://c)")]))]))
