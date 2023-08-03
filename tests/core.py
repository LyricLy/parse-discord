import unittest

from parse_discord import *


class Core(unittest.TestCase):
    def test_text(self):
        self.assertEqual(parse("foo"), Markup([Text("foo")]))

    def test_useless_escape(self):
        self.assertEqual(parse(r"\&"), Markup([Text("&")]))

    def test_invalid_escape(self):
        self.assertEqual(parse(r"\foo"), Markup([Text(r"\foo")]))
