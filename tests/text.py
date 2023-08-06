import unittest

from parse_discord import *


class Core(unittest.TestCase):
    def test_text(self):
        self.assertEqual(parse("foo"), Markup([Text("foo")]))

    def test_useless_escape(self):
        self.assertEqual(parse(r"\&"), Markup([Text("&")]))

    def test_invalid_escape(self):
        self.assertEqual(parse(r"\foo"), Markup([Text(r"\foo")]))

    def test_strip_trailing_ws(self):
        self.assertEqual(parse("foo   \nbar"), Markup([Text("foo\nbar")]))

    def test_self_escape(self):
        self.assertEqual(parse(r"\\\*"), Markup([Text(r"\*")]))

    def test_digit_not_escaped(self):
        self.assertEqual(parse(r"\0"), Markup([Text(r"\0")]))

    def test_preserve_shrug(self):
        self.assertEqual(parse(r"¯\_(ツ)_/¯"), Markup([Text(r"¯\_(ツ)_/¯")]))
