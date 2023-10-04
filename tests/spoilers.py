import unittest

from parse_discord import *


class Spoilers(unittest.TestCase):
    def test_spoilers(self):
        self.assertEqual(parse("||foo||"), Markup([Spoiler(Markup([Text("foo")]))]))

    def test_stack(self):
        self.assertEqual(parse("|||||"), Markup([Spoiler(Markup([Text("|")]))]))

    def test_no_escape(self):
        self.assertEqual(parse(r"||\||"), Markup([Spoiler(Markup([Text("\\")]))]))

    def test_two_together(self):
        self.assertEqual(parse("||a|| b ||c||"), Markup([Spoiler(Markup([Text("a")])), Text(" b "), Spoiler(Markup([Text("c")]))]))
