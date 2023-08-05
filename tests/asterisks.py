import unittest

from parse_discord import *

from .utils import depth_of_insanity


class Asterisks(unittest.TestCase):
    def test_italics(self):
        self.assertEqual(parse("*foo*"), Markup([Italic(Markup([Text("foo")]))]))

    def test_bold(self):
        self.assertEqual(parse("**foo**"), Markup([Bold(Markup([Text("foo")]))]))

    def test_escape_start(self):
        self.assertEqual(parse(r"\*foo*"), Markup([Text("*foo*")]))

    def test_escape_middle(self):
        self.assertEqual(parse(r"*foo\*bar*"), Markup([Italic(Markup([Text("foo*bar")]))]))

    def test_escape_end(self):
        self.assertEqual(parse(r"*foo\*"), Markup([Text("*foo*")]))

    def test_italic_in_bold(self):
        self.assertEqual(parse("***foo* bar** baz"), Markup([Bold(Markup([Italic(Markup([Text("foo")])), Text(" bar")])), Text(" baz")]))

    def test_bold_in_italic(self):
        self.assertEqual(parse("***foo** bar* baz"), Markup([Italic(Markup([Bold(Markup([Text("foo")])), Text(" bar")])), Text(" baz")]))

    def test_cross_italic_first(self):
        self.assertEqual(parse("*foo **bar* baz**"), Markup([Italic(Markup([Text("foo **bar")])), Text(" baz**")]))

    def test_cross_bold_first(self):
        self.assertEqual(parse("**foo *bar** baz*"), Markup([Bold(Markup([Text("foo *bar")])), Text(" baz*")]))

    def test_right_assoc(self):
        self.assertEqual(parse("**foo*"), Markup([Text("*"), Italic(Markup([Text("foo")]))]))

    def test_newline_breaker(self):
        self.assertEqual(parse("*foo\n*"), Markup([Text("*foo\n*")]))

    def test_n_on_right(self):
        for i in range(20):
            p = parse(f"*foo****{'*'*i}")
            if i % 2:
                self.assertIsInstance(p.nodes[0], Italic)
                inner = p.nodes[0].inner.nodes  # type: ignore
                self.assertEqual(inner[0], Text("foo"))
                self.assertEqual(depth_of_insanity(inner[1]), i//2 + 1)
            else:
                self.assertEqual(p.nodes[0], Text("*foo"))
                self.assertEqual(depth_of_insanity(p.nodes[1]), i//2 + 1)
                
    def test_n(self):
        for i in range(20):
            p = parse("*"*(i+1))
            nth, part = divmod(i, 4)
            self.assertEqual(depth_of_insanity(p.nodes[0]), nth*2+(part//2%2) if part%2 else nth)
            self.assertIsInstance(p.nodes[0], (Text, Italic if part%2 else Bold))
            
    def test_ws(self):
        self.assertEqual(parse("a * *"), Markup([Text("a * *")]))
        self.assertEqual(parse("a * b*"), Markup([Text("a * b*")]))
        self.assertEqual(parse("a *b  *"), Markup([Text("a "), Italic(Markup([Text("b  ")]))]))
        # never change, discord
        self.assertEqual(parse("a *b   *"), Markup([Text("a *b   *")]))

        self.assertEqual(parse("** **"), Markup([Bold(Markup([Text(" ")]))]))
