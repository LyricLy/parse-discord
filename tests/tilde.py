import unittest

from parse_discord import *


class Tilde(unittest.TestCase):
    def test_strikethrough(self):
        self.assertEqual(parse("~~foo~~"), Markup([Strikethrough(Markup([Text("foo")]))]))

    def test_stack(self):
        self.assertEqual(parse("~~~~~"), Markup([Strikethrough(Markup([Text("~")]))]))

    def test_no_escape(self):
        self.assertEqual(parse(r"~~\~~"), Markup([Strikethrough(Markup([Text("\\")]))]))

