import unittest

from parse_discord import *

from .utils import depth_of_insanity


class Underscores(unittest.TestCase):
    def test_italics(self):
        self.assertEqual(parse("_foo_"), Markup([Italic(Markup([Text("foo")]))]))

    def test_underlined(self):
        self.assertEqual(parse("__foo__"), Markup([Underline(Markup([Text("foo")]))]))

    def test_escape_start(self):
        self.assertEqual(parse(r"\_foo_"), Markup([Text("_foo_")]))

    def test_escape_middle(self):
        self.assertEqual(parse(r"_a\_\\\_\\_"), Markup([Italic(Markup([Text("a_\\_\\")]))]))

    def test_invalid_escape_middle(self):
        self.assertEqual(parse(r"_\a_"), Markup([Italic(Markup([Text(r"\a")]))]))

    def test_escape_scourge(self):
        self.assertEqual(parse(r"__\__"), Markup([Text("_"), Italic(Markup([Text("_")]))]))

    def test_escape_end(self):
        self.assertEqual(parse(r"_foo\_"), Markup([Text("_foo_")]))

    def test_italic_in_underline(self):
        self.assertEqual(parse("___foo_ bar__ baz"), Markup([Underline(Markup([Italic(Markup([Text("foo")])), Text(" bar")])), Text(" baz")]))

    def test_underline_in_italic(self):
        self.assertEqual(parse("___foo__ bar_ baz"), Markup([Italic(Markup([Underline(Markup([Text("foo")])), Text(" bar")])), Text(" baz")]))

    def test_cross_italic_first(self):
        self.assertEqual(parse("_foo __bar_ baz__"), Markup([Italic(Markup([Text("foo __bar")])), Text(" baz__")]))

    def test_cross_underline_first(self):
        self.assertEqual(parse("__foo _bar__ baz_"), Markup([Underline(Markup([Text("foo _bar")])), Text(" baz_")]))

    def test_right_assoc(self):
        self.assertEqual(parse("__foo_"), Markup([Text("_"), Italic(Markup([Text("foo")]))]))

    def test_n_on_right(self):
        for i in range(20):
            p = parse(f"_foo____{'_'*i}")
            if i % 2:
                self.assertIsInstance(p.nodes[0], Italic)
                inner = p.nodes[0].inner.nodes  # type: ignore
                self.assertEqual(inner[0], Text("foo"))
                self.assertEqual(depth_of_insanity(inner[1]), i//2 + 1)
            else:
                self.assertEqual(p.nodes[0], Text("_foo"))
                self.assertEqual(depth_of_insanity(p.nodes[1]), i//2 + 1)
                
    def test_n(self):
        for i in range(20):
            p = parse("_"*(i+1))
            nth, part = divmod(i, 4)
            self.assertEqual(depth_of_insanity(p.nodes[0]), nth*2+(part//2%2) if part%2 else nth)
            self.assertIsInstance(p.nodes[0], (Text, Italic if part%2 else Underline))
            
    def test_ws(self):
        self.assertEqual(parse("_ _"), Markup([Italic(Markup([Text(" ")]))]))
        self.assertEqual(parse("__ __"), Markup([Underline(Markup([Text(" ")]))]))
        self.assertEqual(parse("a _b  _"), Markup([Text("a "), Italic(Markup([Text("b  ")]))]))
