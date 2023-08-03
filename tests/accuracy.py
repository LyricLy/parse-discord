import unittest

from parse_discord import *


def depth_of_insanity(m):
    if not isinstance(m, (Italic, Bold)):
        return 0
    return 1 + depth_of_insanity(m.inner.nodes[0])


class Asterisks(unittest.TestCase):
    def test_text(self):
        self.assertEqual(parse("foo"), Markup([Text("foo")]))

    def test_italics(self):
        self.assertEqual(parse("*foo*"), Markup([Italic(Markup([Text("foo")]))]))

    def test_bold(self):
        self.assertEqual(parse("**foo**"), Markup([Bold(Markup([Text("foo")]))]))

    def test_regular(self):
        self.assertEqual(parse("***foo* bar** baz"), Markup([Bold(Markup([Italic(Markup([Text("foo")])), Text(" bar")])), Text(" baz")]))

    def test_right_assoc(self):
        self.assertEqual(parse("**foo*"), Markup([Text("*"), Italic(Markup([Text("foo")]))]))

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
            
