import unittest

from parse_discord import *


class Subtext(unittest.TestCase):
    def test_subtext(self):
        self.assertEqual(parse("-# foo"), Markup([Subtext(Markup([Text("foo")]))]))

    def test_newline_ends(self):
        self.assertEqual(parse("-# foo\ning"), Markup([Subtext(Markup([Text("foo")])), Text("ing")]))

    def test_ender_trick(self):
        self.assertEqual(parse("*-# foo*ing"), Markup([Italic(Markup([Subtext(Markup([Text("foo")]))])), Text("ing")]))

    def test_only_at_start(self):
        self.assertEqual(parse("a -# foo"), Markup([Text("a -# foo")]))

    def test_indentation_breaks(self):
        self.assertEqual(parse(" -# foo"), Markup([Text(" -# foo")]))

    def test_even_through_asterisks(self):
        self.assertEqual(parse(" *-# foo*"), Markup([Text(" "), Italic(Markup([Text("-# foo")]))]))

    def test_leading_repeat(self):
        self.assertEqual(parse("-# -# a"), Markup([Text("-# -# a")]))

    def test_newline_start(self):
        self.assertEqual(parse("-#\na"), Markup([Text("-#\na")]))

    def test_codeblocks(self):
        self.assertEqual(parse("-# ```a```"), Markup([Subtext(Markup([Codeblock(None, "a")]))]))
        self.assertEqual(parse("-# ```\na\n```"), Markup([Subtext(Markup([Text("```")])), Text("a\n```")]))

    def test_strips(self):
        self.assertEqual(parse("-#    a   \N{IDEOGRAPHIC SPACE}"), Markup([Subtext(Markup([Text("a #")]))]))
