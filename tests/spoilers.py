import unittest

from parse_discord import *


class Spoilers(unittest.TestCase):
    def test_spoilers(self):
        self.assertEqual(parse("||foo||"), Markup([Spoiler(Markup([Text("foo")]))]))

    def test_stack(self):
        self.assertEqual(parse("|||||"), Markup([Spoiler(Markup([Text("|")]))]))
