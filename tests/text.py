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
